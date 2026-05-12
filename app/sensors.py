# =====================
# 🌡️ sensors.py
# =====================

from machine import Pin, ADC
import time
import dht
import sys

sys.path.append('/app')

from config import *

# =========================================
# 🌡️ DHT11
# =========================================
_dht = dht.DHT11(Pin(PIN_DHT11))


def read_dht():
    try:
        _dht.measure()
        return _dht.temperature(), _dht.humidity()

    except Exception as e:
        print(f"❌ [DHT11] error: {e}")
        return None, None


# =========================================
# 🌱 Soil Moisture
# =========================================
_adc = ADC(Pin(PIN_SOIL_AO))
_adc.atten(ADC.ATTN_11DB)
_adc.width(ADC.WIDTH_12BIT)


def read_soil():

    # dry soil value
    DRY_VAL = 3300

    # wet soil value
    WET_VAL = 1000

    samples = []

    for _ in range(5):
        samples.append(_adc.read())
        time.sleep_ms(10)

    raw = sum(samples) // len(samples)

    pct = (DRY_VAL - raw) / (DRY_VAL - WET_VAL) * 100

    pct = max(0, min(100, pct))

    return round(pct, 1), raw


# =========================================
# 🪣 Ultrasonic HC-SR04
# =========================================
trig = Pin(PIN_ULTRASONIC_TR, Pin.OUT)
echo = Pin(PIN_ULTRASONIC_EC, Pin.IN)

trig.value(0)


def read_ultrasonic(timeout_us=30000):

    # clean trigger
    trig.value(0)
    time.sleep_us(5)

    # send pulse
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    # wait echo HIGH
    start_wait = time.ticks_us()

    while echo.value() == 0:

        if time.ticks_diff(time.ticks_us(), start_wait) > timeout_us:
            print("❌ [ULTRASONIC] timeout waiting HIGH")
            return None

    pulse_start = time.ticks_us()

    # wait echo LOW
    while echo.value() == 1:

        if time.ticks_diff(time.ticks_us(), pulse_start) > timeout_us:
            print("❌ [ULTRASONIC] timeout waiting LOW")
            return None

    pulse_end = time.ticks_us()

    duration = time.ticks_diff(pulse_end, pulse_start)

    # convert to cm
    distance_cm = duration / 58.0

    return round(distance_cm, 1)


# =========================================
# 🪣 Water Tank Percentage
# =========================================
def water_level_pct():

    dist = read_ultrasonic()

    if dist is None:
        return None, None

    # show raw value
    print(f"📏 [ULTRASONIC] RAW = {dist} cm")

    # limits
    dist = max(TANK_FULL_CM, min(dist, TANK_EMPTY_CM))

    # percentage calculation
    pct = (
        1 -
        (dist - TANK_FULL_CM) /
        (TANK_EMPTY_CM - TANK_FULL_CM)
    ) * 100

    pct = round(max(0, min(100, pct)), 1)

    print(f"🪣 [TANK] dist={dist}cm → {pct}%")

    return dist, pct


# =========================================
# 📦 Read All Sensors
# =========================================
def read_all():

    temp, hum = read_dht()

    soil_pct, soil_raw = read_soil()

    dist_cm, tank_pct = water_level_pct()

    return {

        "temperature": temp,

        "humidity": hum,

        "soil_pct": soil_pct,

        "soil_raw": soil_raw,

        "tank_dist": dist_cm,

        "tank_pct": tank_pct,
    }