




# ---------- WIFI -------------

WIFI_SSID     = "WE_671AF0"
WIFI_PASSWORD = "M27037096d@"
HOSTNAME      = "smart_farm"     

# ---------- OTA -------------

OTA_PASSWORD  = "admin123"

# ---------- Deep Sleep -------------

SLEEP_SECONDS      = 300    
SOIL_DRY_THRESHOLD = 30    
SOIL_WET_THRESHOLD = 70    

# ---------- Sensors Pins -------------

PIN_DHT11         = 4       
PIN_SOIL_AO       = 34      
PIN_ULTRASONIC_TR = 5       
PIN_ULTRASONIC_EC = 18      

# ---------- Output Pins -------------

PIN_LED        = 2          
PIN_RELAY_PUMP = 26         
PIN_RELAY_2    = 27         
PIN_RELAY_3    = 25        
PIN_RELAY_4    = 33         


# ---------- I2C / OLED -------------

PIN_SDA     = 21
PIN_SCL     = 22
OLED_WIDTH  = 128
OLED_HEIGHT = 64
OLED_ADDR   = 0x3C   


# ---------- Relay Logic -------------

RELAY_ON  = 0
RELAY_OFF = 1


# ---------- Tank / Ultrasonic -------------

TANK_MAX_CM   = 30.0   
TANK_EMPTY_CM = 5.0    


# ---------- MQTT -------------


MQTT_ENABLED     = True
MQTT_BROKER      = "192.168.1.157"   
MQTT_PORT        = 1883
MQTT_USER        = "MOHA"
MQTT_PASS        = "moha"
MQTT_CLIENT      = "esp32-farm"      
MQTT_PUB_SENSORS = "farm/sensors"   
MQTT_PUB_STATUS  = "farm/status"    
MQTT_SUB_CMD     = "farm/cmd"       


# ---------- Web Dashboard -------------

WEB_PORT = 80    
