

#  ------ WIFI ------

WIFI_SSID          = "WE_671AF0"
WIFI_PASSWORD      = "M27037096d@"
HOSTNAME           = "smart_farm"


#  ------ OTA ------

OTA_PASSWORD       = "admin123"


#  ------ Deep Sleep ------

SLEEP_SECONDS      = 300

SOIL_DRY_THRESHOLD = 30
SOIL_DRY_THRESHOLD = 70


#  ------ Sensor Pins ------

PIN_DHT11          = 4
PIN_SOIL_AO        = 34

PIN_ULTRASONIC_TR  = 5
PIN_ULTRASONIC_EC  = 14


#  ------ Output Pins ------

PIN_LED            = 2
PIN_RELAY_PUMP     = 26
PIN_RELAY_2        = 27
PIN_RELAY_3        = 25
PIN_RELAY_4        = 33


#  ------ I2C / OLED ------

PIN_SDA            = 21
PIN_SCL            = 22

#  Note when use another module big i use small dont work this pin  
# ...revision the code of olde

OLED_WIDTH         = 128
OLED_HEIGHT        = 64
OLED_ADDR          = 0x3C


#  ------ Tank / Ultrasonic ------

TANK_MAX_CM        = 30
TANK_EMPTY_CM      = 5.0


#  ------ MQTT ------

#  Revision the ip and another

MQTT_ENABLED      = False
MQTT_BROKER       = "192.168.1.100"
MQTT_PORT         = 1883
MQTT_USER         = "MOHA"
MQTT_PASS         = "moha"
MQTT_TOPIC        = "farm/sensors"


#  ------ Web Dashboard ------

WEB_PORT          = 80



