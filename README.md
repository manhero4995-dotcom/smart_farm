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

📂 Full Setup & Workflow Guide

1️⃣ First: Clone the Repository 📥Download the project files to your local machine.

   OS               Command
🐧 Linuxgit clone   git@github.com:manhero4995-dotcom/smart_farm.gitcd smart_farm
🪟 Windowsgit clone https://github.com/manhero4995-dotcom/smart_farm.gitcd smart_farm


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
ampy --port <PORT> put app
ampy --port <PORT> put lib

# Upload configuration and main scripts
ampy --port <PORT> put main.py
ampy --port <PORT> put boot.py
ampy --port <PORT> put config.py
⚙️ Step B: Project Operation Workflow
Network: boot.py initializes and triggers wifi_manager.py to get the ESP32 online.

Telemetry: main.py reads data from sensors.py (Temp/Humidity).

Dashboard: Access the local IP address in your browser to control pumps via web_server.py.

Remote: Data is published via umqtt for real-time tracking on your MQTT broker.

📝 Saving Changes to GitHub
To push this professional update to your repository, run:

Bash
git add README.md
git commit -m "🚀 Finalize Professional README with full setup guide"
git push origin main

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
