



import network, time
from   config import WIFI_SSID, WIFI_PASSWORD, HOSTNAME


def connect(timeout= 20):
    
    """
    Connect to WiFi. Returns IP string or None on failure.
    """
    
    sta = network.WLAN(network.STA_IF)
    sta .active(True)
    sta.config(dhcp_hostname=HOSTNAME)
    
    if sta.isconnected():
        
        print("[WIFI] Already connected:", sta.ifconfig()[0])
        
        return sta.ifconfig()[0]
    
    print(f"[WIFI] Conecting to '{WIFI_SSID}'", end="")
    
    for _ in range(timeout *2):
        
        if sta.isconnected():
            
            ip = sta.ifconfig()[0]
            
            print(f"\n[WIFI] connected! IP: {ip}")
            
            return ip
        
        print(".", end="")
        time.sleep(0.5)
    
    print("\n[WIFI] FAILED to conected")
    
    return  None

def disconnect():
    
    sta = network.WLAN(network.STA_IF)
    sta.disconnect()
    sta.active(False)
    

def ip():
    
    sta = network.WLAN(network.STA_IF)
    
    return sta.ifconfig()[0]  if sta.isconnected() else None

def is_connected():
    
    sta = network.WLAN(network.STA_IF)
    
    return sta.isconnected()
    
