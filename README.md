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


📂 Full Setup & Workflow Guide1️⃣ First: Install the Repo on your Device 📥To get the project files from GitHub to your laptop:

   OS               Command
🐧 Linuxgit clone   git@github.com:manhero4995-dotcom/smart_farm.gitcd smart_farm
🪟 Windowsgit clone https://github.com/manhero4995-dotcom/smart_farm.gitcd smart_farm


2️⃣ Second: Install Tools & Environment 🛠️
Setup the Python Virtual Environment and install the necessary drivers to talk to the ESP32.

Step A: Create Environment

🐧 Linux: python3 -m venv esptool-evn && source esptool-evn/bin/activate

🪟 Windows: python -m venv esptool-evn && .\esptool-evn\Scripts\activate

Step B: Install Dependencies

Bash
pip install esptool adafruit-ampy pyserial
Step C: Flash Firmware (Optional/First Time Only)

🐧 Linux: esptool.py --port /dev/ttyUSB0 erase_flash

🪟 Windows: esptool --port COM3 erase_flash

3️⃣ Third: Upload to ESP32 & Run Project 🚀
How to move your code from the laptop to the hardware and start the "Smart Farm".

Step A: Upload Files
We use ampy to send the folders and files. Replace <PORT> with your port (e.g., /dev/ttyUSB0 or COM3).

Bash
# Uploading the core folders
ampy --port <PORT> put app
ampy --port <PORT> put lib

# Uploading the main files
ampy --port <PORT> put main.py
ampy --port <PORT> put boot.py
Step B: How the Project Works

Boot Up: When the ESP32 starts, it runs boot.py to connect to WiFi (via wifi_manager.py).

Sensors: The main.py calls sensors.py to read temperature and moisture.

Control: You can open your browser and enter the ESP32's IP address to see the Web Server and control the pumps.

MQTT: The device will start publishing data to the MQTT broker for remote monitoring.

📝 To Save these changes to your GitHub:
Copy the code above, paste it at the end of your README.md, then run:

Bash
git add README.md
git commit -m "Add 1st, 2nd, and 3rd steps for Linux and Windows"
git push origin main
