# 🌿 Smart Farm IoT System 🚜💧

![IoT](https://img.shields.io/badge/Platform-IoT-green)
![ESP32](https://img.shields.io/badge/Board-ESP32-blue)
![Language](https://img.shields.io/badge/Language-MicroPython-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-orange)

---

## 📖 Overview
A **comprehensive IoT solution** for smart agriculture management using ESP32.  
This project enables **automated environmental monitoring, remote device control, and OTA firmware updates**.

---

## 🚀 Key Features
- 🌡️ **Real-time Monitoring** → Temperature & humidity using DHT11  
- 🌐 **Web Dashboard** → Control pumps & devices via browser  
- 📡 **MQTT Protocol** → Fast and lightweight data communication  
- 🔄 **OTA Updates** → Update firmware remotely over WiFi  
- 📶 **Smart WiFi Manager** → Auto reconnect system  
- 🖥️ **OLED Display** → Live data on SSD1306 screen  

---

## 📂 Project Structure

.
├── 🟢 main.py # Main application logic
├── ⚙️ boot.py # System initialization
├── 🔐 config.py # WiFi & MQTT credentials
│
├── 📂 app/
│ ├── 🌡️ sensors.py # Sensor logic (DHT11, etc.)
│ ├── ⚙️ actuators.py # Relay & pump control
│ ├── 🌐 web_server.py # Web dashboard
│ ├── 📶 wifi_manager.py # WiFi handling
│ └── 🆙 ota.py # OTA update system
│
└── 📂 lib/ # External libraries
├── umqtt/
└── ssd1306/


---

## ⚙️ Setup & Installation Guide

### 1️⃣ Clone Repository 📥
```bash
git clone https://github.com/manhero4995-dotcom/smart_farm.git
cd smart_farm
2️⃣ Environment Setup 🛠️
🔹 Create Virtual Environment

Linux

python3 -m venv esptool-evn
source esptool-evn/bin/activate

Windows

python -m venv esptool-evn
.\esptool-evn\Scripts\activate
🔹 Install Dependencies
pip install esptool adafruit-ampy pyserial
🔹 Flash MicroPython (First Time Only)

Linux

esptool.py --port /dev/ttyUSB0 erase_flash

Windows

esptool --port COM3 erase_flash
3️⃣ Upload & Run 🚀
📤 Upload Files to ESP32
ampy --port <PORT> put app
ampy --port <PORT> put lib

ampy --port <PORT> put main.py
ampy --port <PORT> put boot.py
ampy --port <PORT> put config.py
🔄 System Workflow
⚡ boot.py → Initializes system & WiFi
📶 wifi_manager.py → Connects ESP32 to network
🌡️ sensors.py → Reads environmental data
🌐 web_server.py → Provides dashboard control
📡 MQTT → Sends data to broker
🔄 OTA → Enables remote updates
🌐 How to Use
Power ON ESP32
Connect to same WiFi network
Open browser and enter ESP32 IP
Control pump & monitor data in real-time
🧠 Future Improvements
📱 Mobile App integration
☁️ Cloud dashboard (ThingsBoard / Firebase)
🔋 Solar-powered system
🤖 AI-based irrigation decision system
👨‍💻 Author

Mohamed Ahmed

⭐ Support

If you like this project:

⭐ Star the repo
🍴 Fork it
🛠️ Contribute
📝 Git Commands
git add README.md
git commit -m "🚀 Professional README update"
git push origin main

