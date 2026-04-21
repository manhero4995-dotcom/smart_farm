# ============================================================
# wifi_manager.py — إدارة اتصال الـ WiFi
#
# الـ ESP32 عنده WiFi مدمج
# بيشتغل كـ Station (STA) = عميل يتصل بالـ router
# ============================================================

import network
import time
import sys
sys.path.append('/app')
from config import WIFI_SSID, WIFI_PASSWORD, HOSTNAME

def connect(timeout=20):
    """
    اتصل بالـ WiFi
    بترجع الـ IP لو نجح
    بترجع None لو فشل
    """
    # STA_IF = Station mode = اتصل بـ router
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.config(dhcp_hostname=HOSTNAME)   # اسم الجهاز على الشبكة

    # لو متصل أصلاً ارجع الـ IP بدون إعادة اتصال
    if sta.isconnected():
        print("[WiFi] already connected:", sta.ifconfig()[0])
        return sta.ifconfig()[0]

    print(f"[WiFi] connecting to '{WIFI_SSID}'", end="")
    sta.connect(WIFI_SSID, WIFI_PASSWORD)

    # استنى لحد ما يتصل أو يعدّي الـ timeout
    for _ in range(timeout * 2):
        if sta.isconnected():
            ip = sta.ifconfig()[0]
            print(f"\n[WiFi] connected! IP: {ip}")
            return ip
        print(".", end="")
        time.sleep(0.5)

    print("\n[WiFi] FAILED")
    return None

def disconnect():
    sta = network.WLAN(network.STA_IF)
    sta.disconnect()
    sta.active(False)

def ip():
    sta = network.WLAN(network.STA_IF)
    return sta.ifconfig()[0] if sta.isconnected() else None

def is_connected():
    return network.WLAN(network.STA_IF).isconnected()

