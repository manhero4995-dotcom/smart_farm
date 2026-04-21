# ============================================================
# sensors.py — قراءة كل السنسورات
#
# السنسورات:
#   DHT11      → حرارة + رطوبة الهواء
#   Soil       → رطوبة التربة (analog)
#   Ultrasonic → مستوى المياه في الخزان
# ============================================================

from machine import Pin, ADC
import time
import dht
import sys
sys.path.append('/app')
from config import *


# ══════════════════════════════════════════════════════════════
# DHT11 — سنسور الحرارة والرطوبة
# بيتكلم مع الـ ESP32 عبر سلك واحد (One Wire)
# ══════════════════════════════════════════════════════════════
_dht = dht.DHT11(Pin(PIN_DHT11))

def read_dht():
    """
    بترجع (temperature, humidity)
    لو في مشكلة بترجع (None, None)
    """
    try:
        _dht.measure()              # اطلب قراءة جديدة
        return _dht.temperature(),  _dht.humidity()
    except Exception as e:
        print("[DHT11] error:", e)
        return None, None


# ══════════════════════════════════════════════════════════════
# Soil Moisture — رطوبة التربة
# بيدي جهد بين 0 و 3.3V
# الـ ADC بيحوّله لرقم بين 0 و 4095
# تربة جافة  → رقم عالي (~3300)
# تربة رطبة  → رقم واطي (~1000)
# ══════════════════════════════════════════════════════════════
_adc = ADC(Pin(PIN_SOIL_AO))
_adc.atten(ADC.ATTN_11DB)       # اقبل جهد لحد 3.3V
_adc.width(ADC.WIDTH_12BIT)     # دقة 12bit = 0 لـ 4095

def read_soil():
    """
    بترجع (soil_pct, raw_value)
    soil_pct: نسبة مئوية 0-100%
    raw_value: القيمة الخام من الـ ADC
    """
    DRY_VAL = 3300    # قيمة الـ ADC لما التربة جافة تماماً
    WET_VAL  = 1000   # قيمة الـ ADC لما التربة مبلولة تماماً

    # بناخد 5 قراءات ونحسب المتوسط عشان نقلل الضوضاء
    samples = [_adc.read() for _ in range(5)]
    raw     = sum(samples) // len(samples)

    # نحوّل الرقم الخام لنسبة مئوية
    pct = (DRY_VAL - raw) / (DRY_VAL - WET_VAL) * 100
    pct = max(0, min(100, round(pct, 1)))   # نضمن إنها بين 0 و 100

    return pct, raw


# ══════════════════════════════════════════════════════════════
# Ultrasonic HC-SR04 — مستوى المياه
# بيبعت موجة صوت وبيقيس وقت رجوعها
# المسافة = (الوقت / 2) / 29.1  (بالسم)
# ══════════════════════════════════════════════════════════════
trig = Pin(PIN_ULTRASONIC_TR, Pin.OUT)
echo = Pin(PIN_ULTRASONIC_EC, Pin.IN)

def read_ultrasonic(timeout_us=30000):
    """
    بترجع المسافة بالسم
    لو في timeout بترجع None
    """
    # بعت pulse قصيرة على Trig
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    # استنى الـ Echo يبقى HIGH (الموجة اتبعتت)
    t0 = time.ticks_us()
    while echo.value() == 0:
        if time.ticks_diff(time.ticks_us(), t0) > timeout_us:
            return None   # timeout — مفيش استجابة

    # قيس وقت الـ Echo وهو HIGH (الموجة في الهواء)
    start = time.ticks_us()
    while echo.value() == 1:
        if time.ticks_diff(time.ticks_us(), start) > timeout_us:
            return None   # timeout — مشكلة في السنسور

    # احسب المسافة
    duration    = time.ticks_diff(time.ticks_us(), start)
    distance_cm = (duration / 2) / 29.1
    return round(distance_cm, 1)


def water_level_pct():
    """
    بتحوّل المسافة لنسبة مئوية لمستوى المياه
    بترجع (distance_cm, level_pct)
    """
    dist = read_ultrasonic()
    if dist is None:
        return None, None

    # مسافة صغيرة = مياه كتير = نسبة عالية
    level = (TANK_EMPTY_CM - dist) / (TANK_EMPTY_CM - TANK_MAX_CM) * 100
    level = max(0, min(100, round(level, 1)))
    return dist, level


def read_all():
    """
    بتقرأ كل السنسورات وبترجع dict واحد بكل البيانات
    """
    temp, hum          = read_dht()
    soil_pct, soil_raw = read_soil()
    dist_cm, tank_pct  = water_level_pct()

    return {
        "temperature": temp,
        "humidity":    hum,
        "soil_pct":    soil_pct,
        "soil_raw":    soil_raw,
        "tank_dist":   dist_cm,
        "tank_pct":    tank_pct,
    }
