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
# 🌱 Soil Moisture (FIXED + SMOOTH)
# =========================================
_adc = ADC(Pin(PIN_SOIL_AO))
_adc.atten(ADC.ATTN_11DB)
_adc.width(ADC.WIDTH_12BIT)


def read_soil():

    # 🔥 Calibration values (عدّلها حسب حساسك)
    DRY_VAL = 3800   # air / dry soil
    WET_VAL = 1200   # water / very wet soil

    samples = []

    # 📊 smoothing (تنعيم القراءة)
    for _ in range(10):
        samples.append(_adc.read())
        time.sleep_ms(10)

    raw = sum(samples) / len(samples)

    # 🚨 avoid division error
    if DRY_VAL == WET_VAL:
        return 0, int(raw)

    # 🌱 percentage conversion
    pct = (DRY_VAL - raw) * 100 / (DRY_VAL - WET_VAL)

    # 📌 clamp 0 → 100
    pct = max(0, min(100, pct))

    return round(pct, 1), int(raw)


# =========================================
# 🪣 Ultrasonic HC-SR04
# =========================================
trig = Pin(PIN_ULTRASONIC_TR, Pin.OUT)
echo = Pin(PIN_ULTRASONIC_EC, Pin.IN)

trig.value(0)


def read_ultrasonic(timeout_us=30000):

    trig.value(0)
    time.sleep_us(5)

    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    start_wait = time.ticks_us()

    while echo.value() == 0:
        if time.ticks_diff(time.ticks_us(), start_wait) > timeout_us:
            print("❌ [ULTRASONIC] timeout HIGH")
            return None

    pulse_start = time.ticks_us()

    while echo.value() == 1:
        if time.ticks_diff(time.ticks_us(), pulse_start) > timeout_us:
            print("❌ [ULTRASONIC] timeout LOW")
            return None

    pulse_end = time.ticks_us()

    duration = time.ticks_diff(pulse_end, pulse_start)

    distance_cm = duration / 58.0

    return round(distance_cm, 1)


# =========================================
# 🪣 Water Tank Percentage
# =========================================
def water_level_pct():

    dist = read_ultrasonic()

    if dist is None:
        return None, None

    print(f"📏 [ULTRASONIC] RAW = {dist} cm")

    dist = max(TANK_FULL_CM, min(dist, TANK_EMPTY_CM))

    pct = (
        1 - (dist - TANK_FULL_CM) / (TANK_EMPTY_CM - TANK_FULL_CM)
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