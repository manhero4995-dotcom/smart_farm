# ====================
# ⚙️ config.py
# ====================

# =========================================
# 📶 WiFi
# =========================================
WIFI_SSID     = "WE_671AF0"
WIFI_PASSWORD = "M27037096d@"
HOSTNAME      = "smart_farm"


# =========================================
# 📡 Access Point
# =========================================
AP_SSID       = "SmartFarm"
AP_PASSWORD   = "farm1234"
AP_IP         = "192.168.4.1"


# =========================================
# 🔐 OTA
# =========================================
OTA_PASSWORD  = "admin123"


# =========================================
# 😴 Deep Sleep
# =========================================
SLEEP_SECONDS      = 300

SOIL_DRY_THRESHOLD = 30
SOIL_WET_THRESHOLD = 70


# =========================================
# 🌡️ Sensor Pins
# =========================================
PIN_DHT11          = 4

PIN_SOIL_AO        = 34

PIN_ULTRASONIC_TR  = 5
PIN_ULTRASONIC_EC  = 18


# =========================================
# ⚡ Output Pins
# =========================================
PIN_LED            = 2

PIN_RELAY_PUMP     = 26
PIN_RELAY_2        = 27
PIN_RELAY_3        = 25
PIN_RELAY_4        = 33


# =========================================
# 🪣 Tank LEDs
# =========================================
PIN_LED_TANK_1     = 13
PIN_LED_TANK_2     = 12
PIN_LED_TANK_3     = 14
PIN_LED_TANK_4     = 32


# =========================================
# 🖥️ OLED I2C
# =========================================
PIN_SDA            = 21
PIN_SCL            = 22

OLED_WIDTH         = 128
OLED_HEIGHT        = 64
OLED_ADDR          = 0x3C


# =========================================
# 🔌 Relay Logic
# =========================================
RELAY_ON           = 0
RELAY_OFF          = 1


# =========================================
# 🪣 Tank Calibration
# =========================================
# FULL  = sensor near water
# EMPTY = sensor far from water

TANK_FULL_CM       = 5
TANK_EMPTY_CM      = 30


# =========================================
# ☁️ MQTT HiveMQ
# =========================================
MQTT_ENABLED       = True

MQTT_BROKER        = "c90f783efca941e18bc649fcd3037ee7.s1.eu.hivemq.cloud"

MQTT_PORT          = 8883

MQTT_USER          = "M.M.K"
MQTT_PASS          = "M0102333d"

MQTT_CLIENT        = "esp32-farm"

MQTT_PUB_SENSORS   = "farm/sensors"
MQTT_PUB_STATUS    = "farm/status"
MQTT_SUB_CMD       = "farm/cmd"


# =========================================
# 🌐 Web Server
# =========================================
WEB_PORT           = 80