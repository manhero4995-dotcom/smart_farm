# =========================
# 📶 wifi_manager.py — STA + AP
# =========================

import network
import time
import sys

sys.path.append('/app')

from config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    HOSTNAME,
    AP_SSID,
    AP_PASSWORD,
    AP_IP
)

print("✅ NEW WIFI_MANAGER LOADED")


# =========================
# 📡 Start Access Point
# =========================
def start_ap():

    ap = network.WLAN(network.AP_IF)
    ap.active(True)

    try:
        ap.config(
            essid=AP_SSID,
            password=AP_PASSWORD,
            authmode=network.AUTH_WPA_WPA2_PSK
        )

    except Exception as e:
        print("⚠️ AP config fallback:", e)

        try:
            ap.config(
                essid=AP_SSID,
                password=AP_PASSWORD
            )
        except Exception as e2:
            print("❌ AP config error:", e2)

    # AP IP
    try:
        ap.ifconfig((
            AP_IP,
            "255.255.255.0",
            AP_IP,
            "8.8.8.8"
        ))
    except Exception as e:
        print("❌ AP ifconfig error:", e)

    print(f"📡 [AP] SSID:{AP_SSID}  IP:{AP_IP}")

    return AP_IP


# =========================
# 📶 Connect STA + AP
# =========================
def connect(timeout=20):

    # Start AP first
    ap_ip = start_ap()

    sta = network.WLAN(network.STA_IF)
    sta.active(True)

    try:
        sta.config(dhcp_hostname=HOSTNAME)
    except:
        pass

    # Already connected
    if sta.isconnected():

        sta_ip = sta.ifconfig()[0]

        print(f"📶 [STA] already connected: {sta_ip}")

        return (sta_ip, ap_ip)

    print(f"📶 [WiFi] connecting to '{WIFI_SSID}'", end="")

    sta.connect(WIFI_SSID, WIFI_PASSWORD)

    for _ in range(timeout * 2):

        if sta.isconnected():

            sta_ip = sta.ifconfig()[0]

            print(f"\n✅ [WiFi] connected! IP: {sta_ip}")

            return (sta_ip, ap_ip)

        print(".", end="")

        time.sleep(0.5)

    print(f"\n⚠️ [STA] failed — AP only: {ap_ip}")

    return (None, ap_ip)


# =========================
# 🔌 Disconnect STA
# =========================
def disconnect():

    sta = network.WLAN(network.STA_IF)

    try:
        sta.disconnect()
    except:
        pass

    sta.active(False)


# =========================
# 📴 Stop AP
# =========================
def stop_ap():

    try:
        network.WLAN(network.AP_IF).active(False)

    except Exception as e:
        print("❌ stop_ap:", e)


# =========================
# 📶 STA Status
# =========================
def is_sta_connected():

    return network.WLAN(network.STA_IF).isconnected()


# =========================
# 📡 AP Status
# =========================
def is_ap_active():

    return network.WLAN(network.AP_IF).active()