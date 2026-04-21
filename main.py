# ============================================================
# main.py — نقطة البداية الرئيسية
#
# ترتيب التشغيل:
#   1. boot.py  → يضبط الـ paths
#   2. main.py  → ده الملف ده
#
# خطوات main:
#   1. WiFi connect
#   2. قراءة السنسورات
#   3. ري تلقائي لو التربة جافة
#   4. MQTT connect + نشر البيانات
#   5. Web Dashboard + MQTT loop (بيفضل شغال)
#   6. Deep Sleep
# ============================================================

import sys
sys.path.append('/app')
sys.path.append('/lib')

import gc
import machine
import time
import json
import usocket as socket

import wifi_manager
import mqtt_client, web_server
from  web_server import *

from sensors   import *
from actuators import (pump_timed, relay_set, relay_get,
                       oled_show, oled_msg, oled_clear,
                       led_blink, led_on, led_off,
                       all_relays_off)
from config    import *


# ══════════════════════════════════════════════════════════════
# Command Handler — معالج الأوامر
# بيتنادى لما تييجي رسالة على farm/cmd
# ══════════════════════════════════════════════════════════════
def _mqtt_callback(topic, msg):
    """
    الـ MQTT بيبعت (topic, msg) — wrapper بيحوّلها لـ string
    """
    cmd = msg.decode().strip().lower()
    handle_command(cmd)

def handle_command(cmd):
    """
    تنفيذ الأمر اللي جه عبر MQTT أو Web

    أمثلة:
        relay_1_on   → شغّل المضخة
        relay_1_off  → وقّف المضخة
        pump_10      → شغّل المضخة 10 ثواني
        all_off      → وقّف كل حاجة
        sleep_now    → روح نام
    """
    print(f"[CMD] {cmd}")
    oled_msg("CMD", cmd[:16], "")

    if   cmd == "relay_1_on":   relay_set(1, True)
    elif cmd == "relay_1_off":  relay_set(1, False)
    elif cmd == "relay_2_on":   relay_set(2, True)
    elif cmd == "relay_2_off":  relay_set(2, False)
    elif cmd == "relay_3_on":   relay_set(3, True)
    elif cmd == "relay_3_off":  relay_set(3, False)
    elif cmd == "relay_4_on":   relay_set(4, True)
    elif cmd == "relay_4_off":  relay_set(4, False)
    elif cmd == "all_off":      all_relays_off()
    elif cmd == "sleep_now":    go_sleep(SLEEP_SECONDS)
    elif cmd.startswith("pump_"):
        try:
            # pump_10 → شغّل 10 ثواني
            pump_timed(int(cmd.split("_")[1]))
        except:
            pass


# ══════════════════════════════════════════════════════════════
# Wake Reason — سبب الاستيقاظ
# الـ ESP32 ممكن يصحى من النوم لأسباب مختلفة
# ══════════════════════════════════════════════════════════════
def wake_reason():
    cause = machine.wake_reason()
    reasons = {
        machine.PIN_WAKE:   "PIN wake",     # ضغطة زرار
        machine.TIMER_WAKE: "Timer wake",   # Timer انتهى
        machine.ULP_WAKE:   "ULP wake",     # ULP processor
    }
    return reasons.get(cause, "Power-on / reset")


# ══════════════════════════════════════════════════════════════
# Auto Irrigation — الري التلقائي
# ══════════════════════════════════════════════════════════════
def auto_irrigate(data):
    """
    لو رطوبة التربة أقل من SOIL_DRY_THRESHOLD → شغّل المضخة
    لو مستوى المياه أقل من 10% → لا تسقي (الخزان فاضي)
    """
    soil = data.get("soil_pct")
    tank = data.get("tank_pct")

    if soil is None:
        print("[IRRIG] soil sensor error, skip")
        return

    # تحقق من مستوى المياه أول
    if tank is not None and tank < 10:
        print(f"[IRRIG] tank low ({tank}%), skip")
        oled_msg("WARNING", "Tank low!", f"{tank}%")
        time.sleep(2)
        return

    if soil < SOIL_DRY_THRESHOLD:
        duration = 10
        print(f"[IRRIG] dry ({soil}%) → pump {duration}s")
        oled_msg("IRRIGATING", f"Soil:{soil}%", f"Pump {duration}s")
        pump_timed(duration)
    elif soil > SOIL_WET_THRESHOLD:
        print(f"[IRRIG] wet ({soil}%) → no action")
    else:
        print(f"[IRRIG] OK ({soil}%) → no action")


# ══════════════════════════════════════════════════════════════
# MQTT Connect
# ══════════════════════════════════════════════════════════════
def mqtt_connect_and_subscribe():
    if not MQTT_ENABLED:
        return None
    try:
        # سجّل الـ command handler قبل الاتصال
        mqtt_client.on_command(handle_command)
        if mqtt_client.connect():
            return True
        return None
    except Exception as e:
        print("[MQTT] failed:", e)
        return None


# ══════════════════════════════════════════════════════════════
# Deep Sleep — النوم العميق
# أثناء النوم: استهلاك ~10µA بس
# الـ RAM بتتمسح — بيبدأ من الأول لما يصحى
# ══════════════════════════════════════════════════════════════
def go_sleep(seconds=SLEEP_SECONDS):
    print(f"[SLEEP] going to sleep {seconds}s")
    oled_msg("Deep Sleep", f"{seconds}s", "zzzzz")
    mqtt_client.disconnect()   # قطع MQTT قبل النوم
    all_relays_off()           # وقّف كل الريلايات
    led_off()
    time.sleep(1)
    oled_clear()               # امسح الشاشة
    machine.deepsleep(seconds * 1000)   # النوم (ms)


# ══════════════════════════════════════════════════════════════
# run_loop — الحلقة الرئيسية
# Web + MQTT بيشتغلوا مع بعض هنا
# ══════════════════════════════════════════════════════════════
def run_loop():
    """
    كل iteration بتعمل:
      1. check_messages → في أوامر MQTT جديدة؟
      2. كل 30 ثانية → اقرأ السنسورات وابعتهم
      3. srv.accept → في HTTP request جديد؟
    """
    # افتح TCP socket على البورت 80
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", WEB_PORT))
    srv.listen(3)
    srv.settimeout(0.5)   # انتظر نص ثانية بس لكل request

    last_pub  = time.time()
    PUB_EVERY = 30        # ابعت للـ MQTT كل 30 ثانية

    print("[LOOP] started — web + MQTT")

    while True:

        # ── MQTT: check for commands ──────────────────────────
        try:
            mqtt_client.check_messages()
        except Exception as e:
            print("[MQTT ERROR]", e)

        # ── MQTT: publish every 30s ───────────────────────────
        if time.time() - last_pub >= PUB_EVERY:
            data = read_all()
            data["relay_1"] = relay_get(1)
            data["relay_2"] = relay_get(2)
            data["relay_3"] = relay_get(3)
            data["relay_4"] = relay_get(4)
            oled_show(data)
            mqtt_client.publish_sensors(data)
            last_pub = time.time()
            gc.collect()   # امسح الـ RAM الزيادة

        # ── Web: handle one HTTP request ──────────────────────
        try:
            conn, _ = srv.accept()
            web_server.handle(conn)
        except OSError:
            pass   # timeout عادي — مفيش request


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════
def main():
    gc.collect()
    print("\n" + "=" * 40)
    print("  Smart Farm IoT — MicroPython")
    print("=" * 40)
    print(f"  Wake reason : {wake_reason()}")
    print(f"  Free RAM    : {gc.mem_free()} bytes")
    print("=" * 40 + "\n")

    led_blink(2)
    oled_msg("Smart Farm", "Booting...", "v1.0")
    time.sleep(1)

    # ── Step 1: WiFi ──────────────────────────────────────────
    oled_msg("WiFi", "Connecting...", "")
    ip = wifi_manager.connect()
    if ip:
        led_blink(3, 0.1)
        print(f"[MAIN] IP: {ip}")
        oled_msg("WiFi OK", ip, "")
        time.sleep(1)
    else:
        oled_msg("WiFi FAIL", "no network", "local only")
        time.sleep(2)

    # ── Step 2: Read Sensors ──────────────────────────────────
    oled_msg("Reading", "Sensors...", "")
    data = read_all()
    data["relay_1"] = relay_get(1)
    data["relay_2"] = relay_get(2)
    data["relay_3"] = relay_get(3)
    data["relay_4"] = relay_get(4)
    print("[MAIN] sensor data:", data)
    oled_show(data)

    # ── Step 3: Auto Irrigation ───────────────────────────────
    auto_irrigate(data)

    # ── Step 4: MQTT ──────────────────────────────────────────
    if ip and MQTT_ENABLED:
        oled_msg("MQTT", "Connecting...", "")
        ok = mqtt_connect_and_subscribe()
        if ok:
            mqtt_client.publish_sensors(data)
            oled_msg("MQTT OK", "", "")
            print("[MQTT] data published")
        else:
            oled_msg("MQTT FAIL", "", "")
        time.sleep(1)

    # ── Step 5: Web Dashboard + MQTT loop ─────────────────────
    if ip:
        oled_msg("Dashboard", ip, ":80")
        led_on()
        print("[MAIN] starting dashboard...")
        try:
            run_loop()        # بيفضل هنا لحد ما تبعت sleep
        except Exception as e:
            print("[MAIN] loop error:", e)
            sys.print_exception(e)
        led_off()

    # ── Step 6: Deep Sleep ────────────────────────────────────
    go_sleep(SLEEP_SECONDS)


# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("[MAIN] FATAL:", e)
        sys.print_exception(e)
        led_blink(10, 0.1)
        time.sleep(3)
        machine.reset()
