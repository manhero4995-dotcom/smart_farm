# =====================
# 🌡️  app/sensors.py 
# =====================

from machine import Pin, ADC
import time
import dht
import sys

sys.path.append('/app')

from config import *

# ------------ DHT11 -------------

_dht = dht.DHT11(Pin(PIN_DHT11))

def read_dht():

    try:

        _dht.measure()
        return _dht.temperature(), _dht.humidity()

    except Exception as e:

        print(f"❌ [DHT11] error: {e}")
        return None, None


# ------------ Soil Moisture  -------------

_adc = ADC(Pin(PIN_SOIL_AO))
_adc.atten(ADC.ATTN_11DB)       # 0 → 3.3V
_adc.width(ADC.WIDTH_12BIT)     # 0 → 4095

def read_soil():

    DRY_VAL = 3300    
    WET_VAL  = 1000   

    samples  = [_adc.read() for _ in range(5)]
    raw      = sum(samples) // len(samples)
    pct      = (DRY_VAL - raw) / (DRY_VAL - WET_VAL) * 100
    pct      = max(0, min(100, round(pct, 1)))

    return pct, raw


# ------------ Ultrasonic HC-SR04  -------------

trig = Pin(PIN_ULTRASONIC_TR, Pin.OUT)
echo = Pin(PIN_ULTRASONIC_EC, Pin.IN)

def read_ultrasonic(timeout_us=30000):

    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    t0 = time.ticks_us()

    while echo.value() == 0:

        if time.ticks_diff(time.ticks_us(), t0) > timeout_us:

            return None

    start = time.ticks_us()

    while echo.value() == 1:

        if time.ticks_diff(time.ticks_us(), start) > timeout_us:
            return None

    duration    = time.ticks_diff(time.ticks_us(), start)
    distance_cm = (duration / 2) / 29.1

    return round(distance_cm, 1)

def water_level_pct():

    dist = read_ultrasonic()

    if dist is None:

        return None, None

    level = (TANK_EMPTY_CM - dist) / (TANK_EMPTY_CM - TANK_MAX_CM) * 100
    level = max(0, min(100, round(level, 1)))

    return dist, level

def read_all():

    temp, hum          = read_dht()
    soil_pct, soil_raw = read_soil()
    dist_cm, tank_pct  = water_level_pct()

    return {
        "temperature" : temp,
        "humidity"    : hum,
        "soil_pct"    : soil_pct,
        "soil_raw"    : soil_raw,
        "tank_dist"   : dist_cm,
        "tank_pct"    : tank_pct,

    }
