# ============================================================
# actuators.py — التحكم في كل المخرجات
#
# المخرجات:
#   Relay x4   → تشغيل/إيقاف المضخة والأجهزة
#   LED        → مؤشر حالة
#   OLED       → شاشة العرض
# ============================================================

from machine import Pin, I2C
import time
import sys
sys.path.append('/app')
sys.path.append('/lib')
import ssd1306
from config import *


# ══════════════════════════════════════════════════════════════
# Relay — التحكم في المضخة والأجهزة
# الريلاي زي مفتاح كهربي
# الـ ESP32 بيبعت إشارة صغيرة (3.3V)
# الريلاي بيفتح/يقفل دائرة كبيرة (12V للمضخة)
# Active LOW: يعني 0 = تشغيل ، 1 = إيقاف
# ══════════════════════════════════════════════════════════════
_relays = {
    1: Pin(PIN_RELAY_PUMP, Pin.OUT),
    2: Pin(PIN_RELAY_2,    Pin.OUT),
    3: Pin(PIN_RELAY_3,    Pin.OUT),
    4: Pin(PIN_RELAY_4,    Pin.OUT),
}

# عند بدء التشغيل — وقّف كل الريلايات عشان الأمان
for r in _relays.values():
    r.value(RELAY_OFF)

def relay_set(num, state):
    """
    num   : رقم الريلاي (1-4)
    state : True = تشغيل ، False = إيقاف
    """
    pin_val = RELAY_ON if state else RELAY_OFF
    _relays[num].value(pin_val)    # ✅ _relays مش relays
    print(f"[RELAY] {num} → {'ON' if state else 'OFF'}")

def relay_get(num):
    """ بترجع True لو الريلاي شغّال """
    return _relays[num].value() == RELAY_ON

def pump_on():
    relay_set(1, True)

def pump_off():
    relay_set(1, False)

def pump_timed(seconds):
    """ شغّل المضخة لمدة معينة ثم وقّفها """
    print(f"[PUMP] running {seconds}s")
    pump_on()
    time.sleep(seconds)
    pump_off()
    print("[PUMP] done")

def all_relays_off():
    """ وقّف كل الريلايات دفعة واحدة """
    for i in range(1, 5):
        relay_set(i, False)


# ══════════════════════════════════════════════════════════════
# LED — مؤشر الحالة
# ══════════════════════════════════════════════════════════════
_led = Pin(PIN_LED, Pin.OUT)

def led_on():
    _led.value(1)

def led_off():
    _led.value(0)

def led_blink(times=3, delay=0.2):
    """ وميض متكرر — بيستخدم للإشارة """
    for _ in range(times):
        _led.value(1)
        time.sleep(delay)
        _led.value(0)
        time.sleep(delay)


# ══════════════════════════════════════════════════════════════
# OLED SSD1306 — شاشة العرض
# بتتكلم مع الـ ESP32 عبر I2C
# I2C = بروتوكول اتصال بسلكين: SDA و SCL
# ══════════════════════════════════════════════════════════════
try:
    _i2c = I2C(0,
               scl=Pin(PIN_SCL),
               sda=Pin(PIN_SDA),
               freq=400000)        # سرعة الاتصال 400kHz
    _oled  = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT,
                                  _i2c, addr=OLED_ADDR)
    OLED_OK = True
    print("[OLED] found at", hex(OLED_ADDR))
except Exception as e:
    print("[OLED] not found:", e)
    OLED_OK = False

def oled_show(data):
    """ عرض قراءات السنسورات على الشاشة """
    if not OLED_OK:
        return
    _oled.fill(0)                           # امسح الشاشة
    _oled.text("= Smart Farm =", 8, 0)      # عنوان
    t  = data.get("temperature", "--")
    h  = data.get("humidity",    "--")
    s  = data.get("soil_pct",    "--")
    tk = data.get("tank_pct",    "--")
    _oled.text(f"Temp: {t}c",  0, 14)
    _oled.text(f"Humi: {h}%",  0, 24)
    _oled.text(f"Soil: {s}%",  0, 34)
    _oled.text(f"Tank: {tk}%", 0, 44)
    pump_state = "ON" if relay_get(1) else "OFF"
    _oled.text(f"Pump: {pump_state}", 0, 54)
    _oled.show()                            # ابعت للشاشة

def oled_msg(line1, line2="", line3=""):
    """ عرض رسالة على 3 أسطر """
    if not OLED_OK:
        return
    _oled.fill(0)
    _oled.text(line1, 0, 10)
    _oled.text(line2, 0, 28)
    _oled.text(line3, 0, 46)
    _oled.show()

def oled_clear():
    """ امسح الشاشة """
    if OLED_OK:
        _oled.fill(0)
        _oled.show()
