

# =========================
# ⚡ app/actuators.py — Relay + LED + OLED + Tank LEDs
# =========================

from machine import Pin, I2C
import time
import sys

sys.path.append('/app')
sys.path.append('/lib')

import ssd1306
from config import *

# ── Relays ────────────────────────────────────────────────────
# K1 → Water Pump (12V DC)
# K2 → Spare
# K3 → Spare
# K4 → 220V Lamp / Device ⚠️

_relays = {

    1: Pin(PIN_RELAY_PUMP, Pin.OUT),
    2: Pin(PIN_RELAY_2,    Pin.OUT),
    3: Pin(PIN_RELAY_3,    Pin.OUT),
    4: Pin(PIN_RELAY_4,    Pin.OUT),
}

for r in _relays.values():

    r.value(RELAY_OFF)

def relay_set(num, state):

    _relays[num].value(RELAY_ON if state else RELAY_OFF)
    print(f"⚡ [RELAY] {num} → {'ON' if state else 'OFF'}")

def relay_get(num):
    return _relays[num].value() == RELAY_ON

def pump_on():          relay_set(1, True)
def pump_off():         relay_set(1, False)
def lamp_on():          relay_set(4, True)
def lamp_off():         relay_set(4, False)

def pump_timed(seconds):
    print(f"💧 [PUMP] running {seconds}s")
    pump_on()
    time.sleep(seconds)
    pump_off()
    print("💧 [PUMP] done")

def all_relays_off():
    for i in range(1, 5):
        relay_set(i, False)

# ── Status LED ────────────────────────────────────────────────
_led = Pin(PIN_LED, Pin.OUT)

def led_on():    _led.value(1)
def led_off():   _led.value(0)

def led_blink(times=3, delay=0.2):
    for _ in range(times):
        _led.value(1); time.sleep(delay)
        _led.value(0); time.sleep(delay)

# ── Tank Level LEDs ───────────────────────────────────────────
# 4 LEDs 
# LED1 أحمر  GPIO13 = 25%
# LED2 أصفر  GPIO12 = 50%
# LED3 أخضر  GPIO14 = 75%
# LED4 أخضر  GPIO32 = 100%

_tank_leds = [
    Pin(PIN_LED_TANK_1, Pin.OUT),
    Pin(PIN_LED_TANK_2, Pin.OUT),
    Pin(PIN_LED_TANK_3, Pin.OUT),
    Pin(PIN_LED_TANK_4, Pin.OUT),
]
for l in _tank_leds:
    l.value(0)

def tank_leds_update(tank_pct):
    
    if tank_pct is None:
        for l in _tank_leds:
            l.value(1)
        time.sleep(0.1)
        for l in _tank_leds:
            l.value(0)
        return

    thresholds = [25, 50, 75, 100]
    for i, t in enumerate(thresholds):
        _tank_leds[i].value(1 if tank_pct >= t else 0)
    if tank_pct < 15:
        print("🚨 [TANK] Level critical!")

def tank_leds_off():

    for l in _tank_leds:
        l.value(0)

# ── OLED SSD1306 ──────────────────────────────────────────────

try:
    _i2c = I2C(0,
               scl=Pin(PIN_SCL),
               sda=Pin(PIN_SDA),
               freq=400000)
    _oled  = ssd1306.SSD1306_I2C(
        OLED_WIDTH, OLED_HEIGHT, _i2c, addr=OLED_ADDR
    )
    OLED_OK = True
    print("✅ [OLED] found at", hex(OLED_ADDR))
except Exception as e:
    print(f"❌ [OLED] not found: {e}")
    OLED_OK = False

def oled_show(data):

    if not OLED_OK:
        return
    _oled.fill(0)
    _oled.text("= Smart Farm =", 8, 0)
    t  = data.get("temperature", "--")
    h  = data.get("humidity",    "--")
    s  = data.get("soil_pct",    "--")
    tk = data.get("tank_pct",    "--")
    _oled.text(f"Temp: {t}C",  0, 14)
    _oled.text(f"Humi: {h}%",  0, 24)
    _oled.text(f"Soil: {s}%",  0, 34)
    _oled.text(f"Tank: {tk}%", 0, 44)
    pump = "ON" if relay_get(1) else "OFF"
    _oled.text(f"Pump: {pump}", 0, 54)
    _oled.show()

def oled_msg(line1, line2="", line3=""):

    if not OLED_OK:
        return
    _oled.fill(0)
    _oled.text(line1, 0, 10)
    _oled.text(line2, 0, 28)
    _oled.text(line3, 0, 46)
    _oled.show()

def oled_clear():

    if OLED_OK:
        _oled.fill(0)
        _oled.show()
