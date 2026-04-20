

from machine import Pin, ADC
import time, dht 
import sys
from config import *


# ------ DHT11 --------


_dht = dht.DHT11(Pin(PIN_DHT11))

def read_dht():
    
    """ Returns (temperature_c, humidity_pct) or
    (None, None) on error."""
    
    try:
        
        _dht.measure()
        
        return _dht.temperature(), _dht.humidity()
    
    except Exception as e:
        
        print("[DHT11] Error:", e)
        
        return None, None
    
    
# ------ Soil Moisture --------
# see datasheet sensor

_adc = ADC(Pin(PIN_SOIL_AO))
_adc.atten(ADC.ATTN_11DB)
_adc.width(ADC.WIDTH_12BIT)

def read_soil():
    
    """
    Returns soil moisture as percentage 0–100%.
    Dry soil  → ADC high (~3300+) → 0%
    Wet soil  → ADC low  (~1000)  → 100%
    Calibrate DRY_VAL / WET_VAL for your specific sensor.
    """
    
    DRY_VAL = 3300
    WET_VAL = 1000
    
    samples = [_adc.read()  for _ in range(5)]
    raw     = sum(samples) / len(samples)
    
    pct = (DRY_VAL - raw) / (DRY_VAL - WET_VAL) * 100
    pct = max(0, min(100, round(pct,1)))
    
    return pct , raw



# ------ Ultrasonic HC-SR04 --------


trig = Pin(PIN_ULTRASONIC_TR, Pin.OUT)
echo = Pin(PIN_ULTRASONIC_EC, Pin.IN )
     
def read_ultrasonic(timeout_us=30000):
    
    
     """
     Returns distance in cm, or None on timeout.
     """
     trig.value(0)
     
     time.sleep_us(2)
     trig.value(1)
     
     time.sleep_us(10)
     trig.value(0)
     
     
    # ---- Wait for echo HIGH -----
    
     t0 = time.ticks_us()   
     
     while echo.value() == 0:
        
         if time.ticks_diff(time.ticks_us(), t0) > timeout_us:
            
             return None
    
     start = time.ticks_us()
    
    # ---- wait for echo LOW --------
    
     while echo.value() == 1:
        
         if time.ticks_diff(time.ticks_us(), start) > timeout_us:
            
             return None
        
     duration = time.ticks_diff(time.ticks_us(), start)
     distance_cm = (duration / 2) / 29.1
    
     return round(distance_cm, 1)


def water_level_pct():
    
    
     """
     Converts ultrasonic distance to water level percentage.
     Returns (distance_cm, level_pct)
     """
    
     dist = read_ultrasonic()
    
     if dist is None:
         
         return None, None
     
     
     level = (TANK_EMPTY_CM - dist) / (TANK_EMPTY_CM - TANK_MAX_CM) * 100
     level = max(0, min(100, round(level, 1)))
     
     return dist, level
    

# ------ Read All --------

def read_all():
    
     """Returns a dict with all sensor readings."""
     
     temp, hum            = read_dht()
     soil_pct, soil_raw   = read_soil()
     dist_cm, tank_pct    = water_level_pct()

     
     return {
         
         "temperature" : temp,
         "humidity"    : hum,
         "soil_pct"    : soil_pct,
         "soil_raw"    : soil_raw,
         "tank_dist"   : dist_cm,
         "tank_pct"    : tank_pct,
      }


    
