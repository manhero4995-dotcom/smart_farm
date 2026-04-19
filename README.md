# 🌿 Smart Farm IoT System 🚜💧

![IoT](https://img.shields.io/badge/Focus-Internet_of_Things-blue)
![Platform](https://img.shields.io/badge/Hardware-ESP32%20%7C%20ESP8266-orange)
![Language](https://img.shields.io/badge/Language-MicroPython-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

A comprehensive **IoT solution** for smart agriculture management. This project enables automated environmental monitoring, remote actuation, and seamless firmware management.

---

## 🚀 Key Features
* 🌡️ **Real-time Monitoring:** Accurate tracking of temperature and humidity (DHT11).
* 🌐 **Web Dashboard:** Interactive local web server to toggle pumps and fans.
* 📡 **MQTT Protocol:** Lightweight messaging for high-speed data telemetry.
* 🔄 **OTA Updates:** Remote firmware flashing over WiFi (no USB needed).
* 📶 **Smart Connectivity:** Auto-reconnecting WiFi manager.
* 🖥️ **OLED Display:** Real-time status updates on a local SSD1306 screen.

## 📂 Project Structure
```text
.
├── 🟢 main.py            # Main application logic
├── ⚙️ boot.py            # Startup & system initialization
├── 🔐 config.py          # Private credentials (WiFi/MQTT)
├── 📂 app/
│   ├── 🌡️ sensors.py     # Sensor drivers and logic
│   ├── ⚙️ actuators.py   # Relay and motor controls
│   ├── 🌐 web_server.py  # Dashboard & API routes
│   ├── 📶 wifi_manager.py # Network management
│   └── 🆙 ota.py          # Over-The-Air update engine
└── 📂 lib/               # External libraries (umqtt, ssd1306)
