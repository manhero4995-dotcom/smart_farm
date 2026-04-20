

import json, time
from umqtt.simple import MQTTClient
import sys

sys.path.append('/app')
from config import *

_client   = None
_cmd_cb   = None


def connect():
    
    """
    Connect to MQTT broker.
    Sets a Last Will message so broker knows when ESP32 goes offline.
    Returns True on success.
    """
    
    global _client
    
    if not MQTT_ENABLED:
        
        print("[MQTT] disabled in  config")
        
        return False
    
    try:
        
        _client = MQTTClient(
            
            client_id   = MQTT_CLIENT,
            server      = MQTT_BROKER,
            port        = MQTT_PORT,
            user        = MQTT_USER,
            password    = MQTT_PASS,
            keepalive  = 60,
        )
        
        # ---- Last will: publisshed -----
        
        _client.set_last_will(MQTT_PUB_STATUS, b'offline', retain=True)
        _client.set_callback(_on_message)
        _client.connect()
        
        # ---- Subscribe to command topic -----
        
        _client.subscribe(MQTT_SUB_CMD)
        
        _client.publish(MQTT_PUB_STATUS, b'online', retain= True)
        
        print(f"[MQTT] Connected to {MQTT_BROKER} | listening on {MQTT_SUB_CMD}")
        
        return True
    
    except Exception as e:
        
        print("[MQTT] connect error:", e)
        
        _client = None
        
        return False
    
def disconnect():
    
    global _client
    
    if _client:
        
        try:
            
            _client.publish(MQTT_PUB_STATUS, b'offline', retain= True)
            _client.disconnect()
            
        except:
            
            pass
        
        _client = None
        
        
def publish_sensors(data: dict):
    
    """
    Publishes sensor dict as JSON to farm/sensors.
    Example payload:
      {"temperature":27,"humidity":55,"soil_pct":42,"tank_pct":80,
       "relay_1":false,"relay_2":false,"ts":1700000000}
    """
    
    if not _client:
        
        print("[MQTT] not connected, skip publish")
        
        return False
    
    try:
        
        data["ts"] = time.time()
        payload = json.dumps(data).encode()
        _client.publish(MQTT_PUB_SENSORS, payload)
        
        print(f"[MQTT] published {len(payload)} b  → {MQTT_PUB_SENSORS}")
        
        return True
    
    except Exception as e:
        
        print("[MQTT] publish error:", e)
        
        return False
    
def check_message():
    
    """
    Call this in your main loop to receive commands.
    Non-blocking — returns immediately if no message waiting.
    """
    
    if not _client:
        
        return
    
    try:
        
        _client.check_msg()
        
    except Exception as e:
        
        print("[MQTT] check_msg error:", e)
        
def _on_message(topic, msg):
    
    
     """
    Called automatically when a message arrives on farm/cmd.
    Passes the command string to the registered callback.
    """
    
     try:
        
        cmd = msg.decode().strip().lower()
        
        print(f"[MQTT] cmd received: '{cmd}'")
        
        if _cmd_cb:
            
            _cmd_cb(cmd)
        
     except Exception as e:
        
         print("[MQTT] message decode error", e)
        
        
def on_command(callback):
    
    """
    Register a function that will be called when a command arrives.
    Usage in main.py:
        import mqtt_client
        mqtt_client.on_command(handle_cmd)
    """
    
    global _cmd_cb
    
    _cmd_cb =callback
    
def reconnect(retries= 3):
    
    for i in range(retries):
        
        print(f"[MQTT] reconnect attempt {i+1} / {retries}")
        
        if connect():
            
            return True
        
        time.sleep(2)
        
    return False

def is_connected():
    
    return _client is not None
    
    
    
        
    
        
        
        
    