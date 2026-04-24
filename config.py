# ====================
# ⚙️  config.py 
# ====================

# -------------- WiFi ---------------

WIFI_SSID          = "WE_671AF0"
WIFI_PASSWORD      = "M27037096d@"
HOSTNAME           = "smart_farm"


# -------------- OTA ---------------

OTA_PASSWORD       = "admin123"


# -------------- Deep Sleep ---------------

SLEEP_SECONDS      = 300
SOIL_DRY_THRESHOLD = 30
SOIL_WET_THRESHOLD = 70


# -------------- OTA ---------------
PIN_DHT11          = 4
PIN_SOIL_AO        = 34
PIN_ULTRASONIC_TR  = 5
PIN_ULTRASONIC_EC  = 18


# -------------- Output Pins ---------------

PIN_LED            = 2
PIN_RELAY_PUMP     = 26
PIN_RELAY_2        = 27
PIN_RELAY_3        = 25
PIN_RELAY_4        = 33


# -------------- Tank Level LEDs ---------------

PIN_LED_TANK_1     = 13    # 25%  أحمر
PIN_LED_TANK_2     = 12    # 50%  أصفر
PIN_LED_TANK_3     = 14    # 75%  أخضر
PIN_LED_TANK_4     = 32    # 100% أخضر


# -------------- I2C / OLED ---------------

PIN_SDA            = 21
PIN_SCL            = 22
OLED_WIDTH         = 128
OLED_HEIGHT        = 64
OLED_ADDR          = 0x3C


# -------------- Relay Logic ---------------

RELAY_ON           = 0     # Active LOW
RELAY_OFF          = 1


# -------------- Tank / Ultrasonic ---------------

TANK_MAX_CM        = 30.0
TANK_EMPTY_CM      = 5.0


# -------------- MQTT Cloud HiveMQ ---------------

MQTT_ENABLED       = True
MQTT_BROKER        = "339d2c94754c4104a5ed4a38c80553c6.s1.eu.hivemq.cloud"
MQTT_PORT          = 8883
MQTT_USER          = "M.K.M.M"
MQTT_PASS          = "Mohamed123"
MQTT_CLIENT        = "esp32-farm"
MQTT_PUB_SENSORS   = "farm/sensors"
MQTT_PUB_STATUS    = "farm/status"
MQTT_SUB_CMD       = "farm/cmd"


# -------------- Web ---------------

WEB_PORT           = 80
