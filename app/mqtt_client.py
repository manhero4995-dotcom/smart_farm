

# ============================
# 📡 app/mqtt_client.py — MQTT with TLS , HiveMQ Cloud
# ============================

import json
import time
import sys
import ssl

sys.path.append('/lib')
sys.path.append('/app')

from umqtt.simple import MQTTClient
from config import *

_client = None
_cmd_cb = None

def connect():

    global _client

    if not MQTT_ENABLED:

        print("📡 [MQTT] disabled")
        return False

    try:

        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.verify_mode = ssl.CERT_NONE
        _client = MQTTClient(
            client_id = MQTT_CLIENT,
            server    = MQTT_BROKER,
            port      = MQTT_PORT,
            user      = MQTT_USER,
            password  = MQTT_PASS,
            keepalive = 30,
            ssl       = ssl_ctx,
        )

        _client.set_last_will(
            MQTT_PUB_STATUS, b'offline', retain=True

        )

        _client.set_callback(_on_message)
        _client.connect()
        _client.subscribe(MQTT_SUB_CMD)
        _client.publish(MQTT_PUB_STATUS, b'online', retain=True)

        print(f"✅ [MQTT] connected → {MQTT_BROKER}")
        return True

    except Exception as e:

        print(f"❌ [MQTT] error: {e}")

        _client = None

        return False

def disconnect():

    global _client

    if _client:

        try:

            _client.publish(
                MQTT_PUB_STATUS, b'offline', retain=True
            )
            _client.disconnect()

        except:
            pass

        _client = None
        print("📴 [MQTT] disconnected")

def publish_sensors(data):

    if not _client:
        return False

    try:

        data["ts"] = time.time()
        payload    = json.dumps(data).encode()
        _client.publish(MQTT_PUB_SENSORS, payload)
        print(f"📤 [MQTT] sent {len(payload)}b")

        return True

    except Exception as e:

        print(f"❌ [MQTT] publish error: {e}")
        return False

def check_messages():

    if not _client:
        return

    try:
        _client.check_msg()

    except Exception as e:
        print(f"⚠️  [MQTT] check error: {e}")

def _on_message(topic, msg):

    try:

        cmd = msg.decode().strip().lower()

        print(f"📩 [MQTT] cmd: '{cmd}'")

        if _cmd_cb:
            _cmd_cb(cmd)

    except Exception as e:

        print(f"❌ [MQTT] msg error: {e}")

def on_command(callback):

    global _cmd_cb

    _cmd_cb = callback

def is_connected():

    return _client is not None
