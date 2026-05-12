# =========================
# ⚡ Smart Farm — ACTUATORS FINAL CLEAN
# =========================

from machine import Pin, I2C
import time
import sys

sys.path.append('/app')
sys.path.append('/lib')

import ssd1306
from config import *

# =========================================================
# 🔌 RELAYS
# =========================================================

_relays = {
    1: Pin(PIN_RELAY_PUMP, Pin.OUT),
    2: Pin(PIN_RELAY_2, Pin.OUT),
    3: Pin(PIN_RELAY_3, Pin.OUT),
    4: Pin(PIN_RELAY_4, Pin.OUT),
}

for r in _relays.values():
    r.value(RELAY_OFF)


def relay_set(num, state):
    if num in _relays:
        _relays[num].value(RELAY_ON if state else RELAY_OFF)

        oled_relay_animation(num, state)

        print(f"⚡ RELAY {num} → {'ON' if state else 'OFF'}")


def relay_get(num):
    return _relays[num].value() == RELAY_ON


def pump_on(): relay_set(1, True)
def pump_off(): relay_set(1, False)


# =========================================================
# 💡 LED SYSTEM
# =========================================================

_led = Pin(PIN_LED, Pin.OUT)


def led_on():
    _led.value(1)


def led_off():
    _led.value(0)


def led_blink(times=3, delay=0.2):
    for _ in range(times):
        _led.value(1)
        time.sleep(delay)
        _led.value(0)
        time.sleep(delay)


# =========================================================
# 🪣 TANK LEDs
# =========================================================

_tank_leds = [
    Pin(PIN_LED_TANK_1, Pin.OUT),
    Pin(PIN_LED_TANK_2, Pin.OUT),
    Pin(PIN_LED_TANK_3, Pin.OUT),
    Pin(PIN_LED_TANK_4, Pin.OUT),
]

for l in _tank_leds:
    l.value(0)


def tank_leds_update(pct):

    if pct is None:
        for l in _tank_leds:
            l.value(1)
        time.sleep(0.1)
        for l in _tank_leds:
            l.value(0)
        return

    levels = [25, 50, 75, 100]

    for i, t in enumerate(levels):
        _tank_leds[i].value(1 if pct >= t else 0)


def tank_leds_off():
    for l in _tank_leds:
        l.value(0)


# =========================================================
# 📺 OLED INIT
# =========================================================

try:
    _i2c = I2C(0, scl=Pin(PIN_SCL), sda=Pin(PIN_SDA), freq=400000)

    _oled = ssd1306.SSD1306_I2C(
        OLED_WIDTH,
        OLED_HEIGHT,
        _i2c,
        addr=OLED_ADDR
    )

    OLED_OK = True
    print("✅ OLED READY")

except Exception as e:
    OLED_OK = False
    print("❌ OLED FAIL:", e)


# =========================================================
# ⚡ SIMPLE ANIMATION (FAST FLASH)
# =========================================================

def oled_simple_anim():
    if not OLED_OK:
        return

    _oled.invert(1)
    _oled.show()
    time.sleep(0.03)
    _oled.invert(0)
    _oled.show()


# =========================================================
# ⚡ RELAY ANIMATION (LIGHT)
# =========================================================

def oled_relay_animation(num, state):

    if not OLED_OK:
        return

    _oled.fill(0)
    _oled.text("SMART FARM", 20, 0)
    _oled.hline(0, 10, 128, 1)

    _oled.text("RELAY", 45, 25)

    if state:
        _oled.text(f"R{num} ON", 40, 40)
    else:
        _oled.text(f"R{num} OFF", 40, 40)

    _oled.show()
    time.sleep(0.2)


# =========================================================
# 📊 OLED DASHBOARD (WITH UNITS + SIMPLE ANIM)
# =========================================================

def oled_show(data):

    if not OLED_OK:
        return

    # simple animation عند التحديث
    oled_simple_anim()

    _oled.fill(0)

    _oled.text("SMART FARM", 20, 0)
    _oled.hline(0, 10, 128, 1)

    # ======================
    # 📊 DATA
    # ======================

    t = data.get("temperature", "--")
    h = data.get("humidity", "--")
    s = data.get("soil_pct", "--")
    tk = data.get("tank_pct", "--")

    pump = "ON" if relay_get(1) else "OFF"

    # 🌡 TEMP
    _oled.text("TEMP:", 0, 14)
    _oled.text(str(t) + "C", 60, 14)

    # 💧 HUMIDITY
    _oled.text("HUMI:", 0, 24)
    _oled.text(str(h) + "%", 60, 24)

    # 🌱 SOIL
    _oled.text("SOIL:", 0, 34)
    _oled.text(str(s) + "%", 60, 34)

    # 🪣 TANK
    _oled.text("TANK:", 0, 44)
    _oled.text(str(tk) + "%", 60, 44)

    # ⚡ PUMP STATUS
    _oled.hline(0, 54, 128, 1)
    _oled.text("PUMP:" + pump, 0, 56)

    _oled.show()


# =========================================================
# 🧾 MESSAGE SCREEN
# =========================================================

def oled_msg(l1, l2="", l3=""):

    if not OLED_OK:
        return

    _oled.fill(0)
    _oled.text(str(l1), 0, 10)
    _oled.text(str(l2), 0, 28)
    _oled.text(str(l3), 0, 46)
    _oled.show()


# =========================================================
# 🚀 BOOT SCREEN
# =========================================================

def oled_boot():

    if not OLED_OK:
        return

    _oled.fill(0)
    _oled.text("SMART FARM", 20, 10)
    _oled.text("STARTING...", 25, 30)

    _oled.rect(10, 50, 108, 8, 1)

    for i in range(0, 100, 5):
        _oled.fill_rect(12, 52, i, 4, 1)
        _oled.show()
        time.sleep_ms(40)


# =========================================================
# 🧹 CLEAR
# =========================================================

def oled_clear():

    if OLED_OK:
        _oled.fill(0)
        _oled.show()