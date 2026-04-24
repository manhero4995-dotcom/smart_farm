
# ================
# 🚀 main.py 
# ================

import sys

sys.path.append('/app')
sys.path.append('/lib')

import gc
import machine
import time
import json
import usocket as socket

import wifi_manager
import mqtt_client
import web_server 


from sensors   import read_all
from actuators import *
from config    import *



# --------------- Command Handler ------------------

def handle_command(cmd):
    
    print(f"📩 [CMD] {cmd}")
    oled_msg("CMD", cmd[:14], "")

    if   cmd == "relay_1_on":    relay_set(1, True)
    elif cmd == "relay_1_off":   relay_set(1, False)
    elif cmd == "relay_2_on":    relay_set(2, True)
    elif cmd == "relay_2_off":   relay_set(2, False)
    elif cmd == "relay_3_on":    relay_set(3, True)
    elif cmd == "relay_3_off":   relay_set(3, False)
    elif cmd == "relay_4_on":    relay_set(4, True)
    elif cmd == "relay_4_off":   relay_set(4, False)
    elif cmd == "lamp_on":       relay_set(4, True)
    elif cmd == "lamp_off":      relay_set(4, False)
    elif cmd == "all_off":       all_relays_off()
    elif cmd == "sleep_now":     go_sleep(SLEEP_SECONDS)
    elif cmd == "reset":         machine.reset()
    elif cmd.startswith("pump_"):

        try:
            pump_timed(int(cmd.split("_")[1]))

        except:
            pass



# --------------- Wake Reason ------------------

def wake_reason():

    cause = machine.wake_reason()

    return {

        machine.PIN_WAKE:   "PIN wake",
        machine.TIMER_WAKE: "Timer wake",
        machine.ULP_WAKE:   "ULP wake",
    }.get(cause, "Power-on / reset")



# --------------- Auto Irrigation ------------------

def auto_irrigate(data):

    soil = data.get("soil_pct")
    tank = data.get("tank_pct")

    if soil is None:

        print("⚠️  [IRRIG] soil sensor error")
        return

    if tank is not None and tank < 10:

        print(f"🚨 [IRRIG] tank low ({tank}%), skip")
        oled_msg("WARNING!", "Tank low!", f"{tank}%")
        time.sleep(2)

        return

    if soil < SOIL_DRY_THRESHOLD:

        print(f"💧 [IRRIG] dry ({soil}%) → pump 10s")
        oled_msg("IRRIGATING", f"Soil:{soil}%", "Pump 10s")
        pump_timed(10)

    elif soil > SOIL_WET_THRESHOLD:

        print(f"✅ [IRRIG] wet ({soil}%) → OK")

    else:

        print(f"✅ [IRRIG] soil OK ({soil}%)")



# --------------- MQTT Connect ------------------

def mqtt_connect_and_subscribe():

    if not MQTT_ENABLED:

        return None

    try:

        mqtt_client.on_command(handle_command)

        if mqtt_client.connect():
            return True

        return None

    except Exception as e:

        print(f"❌ [MQTT] failed: {e}")

        return None



# --------------- Deep Sleep ------------------

def go_sleep(seconds=SLEEP_SECONDS):

    print(f"😴 [SLEEP] {seconds}s")
    oled_msg("Deep Sleep", f"{seconds}s", "zzzzz")

    mqtt_client.disconnect()
    all_relays_off()
    tank_leds_off()
    led_off()
    time.sleep(1)

    oled_clear()
    machine.deepsleep(seconds * 1000)


# --------------- Web + MQTT Loop ------------------

def run_loop():
   
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", WEB_PORT))
    srv.listen(3)
    srv.settimeout(0.5)

    last_pub  = time.time()
    PUB_EVERY = 30

    print("🔄 [LOOP] started — web + MQTT")

    while True:

        # MQTT commands

        try:
            mqtt_client.check_messages()

        except Exception as e:
            print(f"⚠️  [MQTT] {e}")

        # Periodic publish
        if time.time() - last_pub >= PUB_EVERY:
            data = read_all()
            data["relay_1"]  = relay_get(1)
            data["relay_2"]  = relay_get(2)
            data["relay_3"]  = relay_get(3)
            data["relay_4"]  = relay_get(4)
            data["free_ram"] = gc.mem_free()
            oled_show(data)
            tank_leds_update(data.get("tank_pct"))
            mqtt_client.publish_sensors(data)
            last_pub = time.time()
            gc.collect()

        # Web request
        try:

            conn, _ = srv.accept()
            web_server.handle(conn)

        except OSError:
            pass


# --------------- Main ------------------

def main():

    gc.collect()

    print("\n" + "=" * 40)
    print("  🌿 Smart Farm IoT — MicroPython")
    print("=" * 40)
    print(f"  Wake  : {wake_reason()}")
    print(f"  RAM   : {gc.mem_free()} bytes")
    print("=" * 40 + "\n")

    led_blink(2)
    oled_msg("Smart Farm", "Booting...", "v2.0")
    time.sleep(1)

    # ------------- Step 1: WiFi ----------------

    oled_msg("WiFi", "Connecting...", "")
    ip = wifi_manager.connect()
    if ip:
        led_blink(3, 0.1)
        oled_msg("WiFi OK", ip, "")
    else:
        oled_msg("WiFi FAIL", "local only", "")
    time.sleep(1)


    # ------------- Step 2: Sensors ----------------

    oled_msg("Reading", "Sensors...", "")

    data = read_all()

    data["relay_1"]  = relay_get(1)
    data["relay_2"]  = relay_get(2)
    data["relay_3"]  = relay_get(3)
    data["relay_4"]  = relay_get(4)
    data["free_ram"] = gc.mem_free()

    print(f"📊 [MAIN] sensors: {data}")

    oled_show(data)
    tank_leds_update(data.get("tank_pct"))


    # -------------Step 3: Auto Irrigation ----------------

    auto_irrigate(data)


    # ------------- Step 4: MQTT ----------------

    if ip and MQTT_ENABLED:

        oled_msg("MQTT", "Connecting...", "")
        ok = mqtt_connect_and_subscribe()

        if ok:

            mqtt_client.publish_sensors(data)
            oled_msg("MQTT OK", "HiveMQ", "Cloud")

        else:

            oled_msg("MQTT FAIL", "", "")
        time.sleep(1)


    # ------------- Step 5: Web Dashboard + Loop ----------------

    if ip:

        oled_msg("Dashboard", ip, ":80")
        led_on()

        print(f"🌐 [MAIN] dashboard at http://{ip}")

        try:

            run_loop()

        except Exception as e:

            print(f"❌ [MAIN] loop error: {e}")

            sys.print_exception(e)
        led_off()


    # ------------- Step 6: Sleep ----------------

    go_sleep(SLEEP_SECONDS)


if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print(f"💥 [MAIN] FATAL: {e}")

        sys.print_exception(e)
        led_blink(10, 0.1)
        time.sleep(3)
        machine.reset()
