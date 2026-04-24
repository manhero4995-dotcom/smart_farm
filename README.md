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

```

## 📂 Full Setup & Workflow Guide

1️⃣ First: Clone the Repository 📥Download the project files to your local machine.

   OS               Command
   
   ```text
🐧  Linuxgit clone   git@github.com:manhero4995-dotcom/smart_farm.gitcd smart_farm
🪟  Windowsgit clone https://github.com/manhero4995-dotcom/smart_farm.gitcd smart_farm

  ```


2️⃣ Second: Environment & Tools 🛠️
Prepare the Python Virtual Environment and install the flashing tools.

🔹 Step A: Create Virtual Environment
Linux: python3 -m venv esptool-evn && source esptool-evn/bin/activate

Windows: python -m venv esptool-evn && .\esptool-evn\Scripts\activate

🔹 Step B: Install Dependencies
Bash
pip install esptool adafruit-ampy pyserial
🔹 Step C: Flash MicroPython Firmware (New Devices Only)
Linux: esptool.py --port /dev/ttyUSB0 erase_flash

Windows: esptool --port COM3 erase_flash

3️⃣ Third: Upload & Execution 🚀
Deploy the code to your ESP32 hardware.

📤 Step A: Upload Files to ESP32
Use ampy to push the project structure. (Replace <PORT> with your specific port).

Bash
# Upload application folders

```text

ampy --port <PORT> put app
ampy --port <PORT> put lib

# Upload configuration and main scripts
ampy --port <PORT> put main.py
ampy --port <PORT> put boot.py
ampy --port <PORT> put config.py

```

⚙️ Step B: Project Operation Workflow
Network: boot.py initializes and triggers wifi_manager.py to get the ESP32 online.

Telemetry: main.py reads data from sensors.py (Temp/Humidity).

Dashboard: Access the local IP address in your browser to control pumps via web_server.py.

Remote: Data is published via umqtt for real-time tracking on your MQTT broker.

📝 Saving Changes to GitHub
To push this professional update to your repository, run:

```text

Bash
git add README.md
git commit -m "🚀 Finalize Professional README with full setup guide"
git push origin main

```
