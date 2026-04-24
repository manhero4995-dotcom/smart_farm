# 🌱 Smart Farm System using ESP32

![IoT](https://img.shields.io/badge/Project-IoT-green)
![ESP32](https://img.shields.io/badge/Board-ESP32-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Project Overview
This project is a **Smart Farming System** based on IoT using the ESP32.  
It monitors environmental conditions such as **soil moisture, temperature, humidity, and water level**, and automatically controls irrigation using a relay and water pump.

---

## 🚀 Features
- 🌡️ Measure temperature and humidity  
- 🌱 Monitor soil moisture level  
- 💧 Measure water tank level  
- ⚡ Automatic irrigation system  
- 📟 OLED display for real-time data  
- 💡 LED indicators for system status  
- 🌐 Remote monitoring (WiFi / MQTT optional)  

---

## 🧰 Components Used

### 🧠 Microcontroller
- 🔹 ESP32 Development Board  

### 🌱 Sensors
- 🌿 Soil Moisture Sensor (FC-28)  
- 🌡️ DHT11 Temperature & Humidity Sensor  
- 📏 HC-SR04 Ultrasonic Sensor  

### 📟 Display
- 🖥️ OLED Display (SSD1306)  

### ⚡ Actuators
- 🔌 4-Channel Relay Module  
- 🚰 DC Water Pump / Motor  

### 💡 Indicators
- 🔴🟡🟢 LEDs (Red, Yellow, Green)  
- ⚙️ 220Ω Resistors  

### 🔌 Other Components
- 🔲 Breadboard  
- 🔗 Jumper Wires  
- 🔋 Power Supply (5V / 9V)  

---

## 🔌 System Operation
1. ESP32 reads all sensor data 📡  
2. If soil is dry → Pump ON 🚰  
3. If soil is wet → Pump OFF ❌  
4. Water level monitored using ultrasonic sensor 💧  
5. Temperature & humidity displayed on OLED 📟  
6. LEDs show system status 💡  

---

## 🖼️ Circuit Diagram
> 📌 Add your image here

![Circuit Diagram](YOUR_IMAGE_LINK_HERE)

---

## 💻 Technologies Used
- 🐍 MicroPython / Arduino  
- 📡 ESP32 WiFi  
- ☁️ MQTT / Web Server  
- 🗂️ GitHub  

---

## 📂 Project Structure

smart-farm/
│── main.py
│── config.py
│── boot.py
│── app
│── lib
│── Digrame.circuit
│── README.md


---

## ⚙️ Future Improvements
- 📱 Mobile App Control  
- ☁️ Cloud Dashboard  
- 🔋 Solar Power Integration  
- 🤖 AI-based Irrigation  

---

## 👨‍💻 Author
**Mohamed Ahmed , Mohamed Asharf**

---

⭐ If you like this project, give it a star on GitHub!
