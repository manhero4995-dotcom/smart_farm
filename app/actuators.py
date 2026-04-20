

from machine import Pin, I2C
import time, ssd1306
from config import *


relays = {
    
    1: Pin(PIN_RELAY_PUMP, Pin.OUT),
    2: Pin(PIN_RELAY_2,    Pin.OUT),
    3: Pin(PIN_RELAY_3,    Pin.OUT),
    4: Pin(PIN_RELAY_4,    Pin.OUT),
    
}

# -------- init all RElay OFF -------

for r in _relays.values():
    
    r.value(RELAY_OFF)
    
def relay_set(num, state):
    
    """state: True=ON, False=OFF"""
    
    pin_val = RELAY_ON if state else RELAY_OFF
    
    relays[num].value(pin_val)
    
    print(f"[RELAY] {num} → {'ON' if state else 'OFF'}")
    
    
def relay_get(num):
    
    return _relays[num].value() == RELAY_ON


def pump_on():
    
    relay_set(1, True)
    
def pump_off():
    
    relay_set(1, False)
    
    
    
def pump_timed(seconds):
    
    """Run pump for N seconds then stop."""
    
    print(f"[PUMP] Running for {seconds}s")
    
    pump_on()
    time.sleep(seconds)
    
    pump_off()
    print("[PUMP] Done")
    
    
def all_relays_off():
    
    for i in range(1, 5):
        
        relay_set(i, False)
        

# ----------- LED Status ------------------

_led = Pin(PIN_LED, Pin. OUT)

def led_on():
    
    _led.value(1)
    
def led_off():
    
    _led.value(0)
    
def led_blink(times= 3, delay= 0.2):
    
    for _ in range(times):
        
        _led.value(1)
        time.sleep(delay)
        
        _led.value(0)
        time.sleep(delay)
        
        
# ----------- OLED SSF1306 ------------------

try:
    
    _i2c  = I2C(0, scl= Pin(PIN_SCL),
    sda   = Pin(PIN_SDA),
    freq  = 400000)
    
    _oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, _i2c, addr=OLED_ADDR)
    
    OLED_OK = True
    
except Exception as e:
    
    print("[OLED] Not found:", e)
    
    OLED_OK =False
    
    
def oled_show(data):
    
    """Display sensor readings on OLED."""
    
    if not OLED_OK:
        
        return
    
    _oled.fill(0)
    _oled.text("= Smart Farm", 20, 0)
    
    t  = data.get("temperature", "--")
    h  = data.get("humidity", "--")
    s  = data.get("soil_pct", "--")
    tk  = data.get("tank_pct", "--")
    
    _oled.text(f"Temp: {t}c", 0, 14)
    _oled.text(f"Humi: {h}%", 0, 24)
    _oled.text(f"Soil: {s}%", 0, 34)
    _oled.text(f"Tank: {tk}%", 0, 44)
    
    pump_state = "ON" if relay_get(1) else "OFF"
    
    _oled.text(f"Pump: {pump_state}", 0, 54)
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
        
    
    


