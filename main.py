# ================
# 🚀 main.py v3.3
# ================

import sys
sys.path.append('/app')
sys.path.append('/lib')

import gc
import machine
import time
import usocket as socket

from app import wifi_manager
import mqtt_client
import web_server

from sensors   import read_all
from actuators import *
from config    import *


_sta_ip = None
_ap_ip  = None


# ======================
# 📩 Command handler (MQTT)
# ======================
def handle_command(cmd):
    print(f"📩 [CMD] {cmd}")
    oled_msg("CMD", cmd[:14], "")

    if   cmd == "relay_1_on":  relay_set(1, True)
    elif cmd == "relay_1_off": relay_set(1, False)
    elif cmd == "relay_2_on":  relay_set(2, True)
    elif cmd == "relay_2_off": relay_set(2, False)
    elif cmd == "relay_3_on":  relay_set(3, True)
    elif cmd == "relay_3_off": relay_set(3, False)
    elif cmd == "relay_4_on":  relay_set(4, True)
    elif cmd == "relay_4_off": relay_set(4, False)

    elif cmd == "lamp_on":     relay_set(4, True)
    elif cmd == "lamp_off":    relay_set(4, False)

    elif cmd == "all_off":     all_relays_off()
    elif cmd == "reset":       machine.reset()

    elif cmd == "sleep_now":   go_sleep(SLEEP_SECONDS)

    elif cmd.startswith("sleep_"):
        try:
            go_sleep(max(10, min(int(cmd.split("_")[1]), 3600)))
        except:
            go_sleep(SLEEP_SECONDS)

    elif cmd.startswith("pump_"):
        try:
            pump_timed(int(cmd.split("_")[1]))
        except:
            pass


# ======================
# 🔍 Wake reason
# ======================
def wake_reason():
    cause = machine.wake_reason()
    return {
        machine.PIN_WAKE:   "PIN wake",
        machine.TIMER_WAKE: "Timer wake",
        machine.ULP_WAKE:   "ULP wake",
    }.get(cause, "Power-on / reset")


# ======================
# 💧 Auto irrigation logic
# ======================
def auto_irrigate(data):
    soil = data.get("soil_pct")
    tank = data.get("tank_pct")

    if soil is None:
        print("⚠️ [IRRIG] no soil data")
        return

    if tank is not None and tank < 10:
        oled_msg("WARNING!", "Tank low!", f"{tank}%")
        time.sleep(2)
        return

    if soil < SOIL_DRY_THRESHOLD:
        print(f"💧 [IRRIG] dry {soil}% → pump 10s")
        oled_msg("IRRIGATING", f"Soil:{soil}%", "10s")
        pump_timed(10)
    else:
        print(f"✅ [IRRIG] OK {soil}%")


# ======================
# 😴 Sleep mode
# ======================
def go_sleep(seconds=SLEEP_SECONDS):
    print(f"😴 [SLEEP] {seconds}s")
    oled_msg("Deep Sleep", f"{seconds}s", "zzz")

    try:
        mqtt_client.disconnect()
    except:
        pass

    all_relays_off()
    tank_leds_off()
    led_off()

    try:
        wifi_manager.stop_ap()
    except:
        pass

    time.sleep(1)
    oled_clear()
    machine.deepsleep(seconds * 1000)


# ======================
# 🔁 Main loop
# ======================
def run_loop():
    global _sta_ip, _ap_ip

    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", WEB_PORT))
    srv.listen(5)
    srv.settimeout(0.2)

    last_pub = time.time()
    last_reconnect = time.time()

    PUB_EVERY = 30
    RECONNECT_EVERY = 60

    print("🔄 [LOOP] running — STA + AP")

    while True:
        now = time.time()

        # MQTT processing
        try:
            mqtt_client.check_messages()
        except:
            pass

        # MQTT reconnect
        if now - last_reconnect >= RECONNECT_EVERY:
            try:
                if not mqtt_client.is_connected():
                    mqtt_client.reconnect_if_needed()
            except:
                pass
            last_reconnect = now

        # publish sensors
        if now - last_pub >= PUB_EVERY:
            data = read_all()

            data["relay_1"]  = relay_get(1)
            data["relay_2"]  = relay_get(2)
            data["relay_3"]  = relay_get(3)
            data["relay_4"]  = relay_get(4)
            data["free_ram"] = gc.mem_free()
            data["sta_ip"]   = _sta_ip
            data["ap_ip"]    = _ap_ip

            oled_show(data)
            tank_leds_update(data.get("tank_pct"))

            try:
                if mqtt_client.is_connected():
                    mqtt_client.publish_sensors(data)
            except:
                pass

            last_pub = time.time()
            gc.collect()

        # Web server
        try:
            conn, addr = srv.accept()
            web_server.handle(conn)
        except OSError:
            pass
        except Exception as e:
            print(f"❌ [WEB] {e}")


# ======================
# 🚀 Main entry
# ======================
def main():
    global _sta_ip, _ap_ip
    gc.collect()

    print("\n" + "="*40)
    print("  🌿 Smart Farm v3.3")
    print(f"  Wake: {wake_reason()}")
    print(f"  RAM : {gc.mem_free()}b")
    print("="*40 + "\n")

    led_blink(2)
    oled_msg("Smart Farm", "Booting", "v3.3")
    time.sleep(1)

    # ======================
    # 🌐 WiFi (STA + AP)
    # ======================
    oled_msg("WiFi", "STA + AP", "")

    try:
        result = wifi_manager.connect()

        if isinstance(result, tuple) and len(result) == 2:
            _sta_ip, _ap_ip = result
        else:
            _sta_ip = result
            _ap_ip  = None

    except Exception as e:
        print(f"❌ WiFi error: {e}")
        _sta_ip = None
        _ap_ip  = None

    web_server.set_ips(_sta_ip, _ap_ip)

    if _sta_ip:
        led_blink(3, 0.1)
        oled_msg("WiFi OK", str(_sta_ip), f"AP:{_ap_ip}")
        print(f"✅ STA:{_sta_ip}  AP:{_ap_ip}")
    else:
        oled_msg("AP only", str(_ap_ip or "none"), AP_SSID)
        print(f"📡 AP only: {_ap_ip}")

    time.sleep(2)

    # ======================
    # 🌡 Sensor warmup
    # ======================
    oled_msg("Warming", "Sensors", "3s")
    time.sleep(3)

    # ======================
    # 📊 First sensor read
    # ======================
    oled_msg("Reading", "Sensors", "")
    data = read_all()

    data["relay_1"]  = relay_get(1)
    data["relay_2"]  = relay_get(2)
    data["relay_3"]  = relay_get(3)
    data["relay_4"]  = relay_get(4)
    data["free_ram"] = gc.mem_free()
    data["sta_ip"]   = _sta_ip
    data["ap_ip"]    = _ap_ip

    oled_show(data)
    tank_leds_update(data.get("tank_pct"))

    auto_irrigate(data)

    # ======================
    # ☁️ MQTT connect
    # ======================
    if _sta_ip and MQTT_ENABLED:
        oled_msg("MQTT", "Connecting", "")

        mqtt_client.on_command(handle_command)
        ok = mqtt_client.connect()

        if ok:
            try:
                mqtt_client.publish_sensors(data)
            except:
                pass
            oled_msg("MQTT OK", "Cloud", "")
        else:
            oled_msg("MQTT FAIL", "local only", "")

        time.sleep(1)

    # ======================
    # 🌐 Dashboard start
    # ======================
    active = _sta_ip or _ap_ip or "no-ip"
    oled_msg("Dashboard", str(active), f"AP:{_ap_ip}")

    led_on()

    print(f"🌐 STA: http://{_sta_ip}  AP: http://{_ap_ip}")

    try:
        run_loop()
    except Exception as e:
        print(f"❌ loop error: {e}")
        sys.print_exception(e)

    led_off()
    go_sleep(SLEEP_SECONDS)


# ======================
# 🔥 Boot
# ======================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"💥 FATAL: {e}")
        sys.print_exception(e)
        led_blink(10, 0.1)
        time.sleep(3)
        machine.reset()