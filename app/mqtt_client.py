# ====================
# 📡 mqtt_client.py (FIXED + OTA SAFE)
# ====================

import json
import time
import sys
import ssl

sys.path.append('/lib')
sys.path.append('/app')

from umqtt.simple import MQTTClient

import config   # ✅ FIX: بدل from config import *


_client    = None
_cmd_cb    = None
_connected = False


# ======================
# 🆔 unique client id
# ======================
def _make_client_id():
    import machine
    uid = machine.unique_id()
    suffix = ''.join('{:02x}'.format(b) for b in uid[-3:])
    return "esp32-farm-" + suffix


# ======================
# 🧹 cleanup
# ======================
def _cleanup():
    global _client, _connected
    if _client is not None:
        try:
            _client.disconnect()
        except:
            pass
    _client = None
    _connected = False


# ======================
# 🔌 connect MQTT
# ======================
def connect(retries=3):
    global _client, _connected

    if not config.MQTT_ENABLED:
        print("📡 [MQTT] disabled")
        return False

    _cleanup()

    for attempt in range(1, retries + 1):
        try:
            print(f"📡 [MQTT] connecting ({attempt}/{retries})...")

            _client = MQTTClient(
                client_id=_make_client_id(),
                server=config.MQTT_BROKER,
                port=config.MQTT_PORT,
                user=config.MQTT_USER,
                password=config.MQTT_PASS,
                keepalive=60,
                ssl=True,
                ssl_params={"server_hostname": config.MQTT_BROKER}
            )

            _client.set_last_will(config.MQTT_PUB_STATUS, b'offline', retain=True)
            _client.set_callback(_on_message)

            _client.connect(clean_session=True)
            _client.subscribe(config.MQTT_SUB_CMD)

            _client.publish(config.MQTT_PUB_STATUS, b'online', retain=True)

            _connected = True
            print("✅ [MQTT] connected")
            return True

        except Exception as e:
            print(f"❌ [MQTT] attempt {attempt} failed: {e}")
            _cleanup()

            if attempt < retries:
                time.sleep(2 * attempt)

    print("❌ [MQTT] all failed")
    return False


# ======================
# 🔌 disconnect
# ======================
def disconnect():
    _cleanup()
    print("📴 [MQTT] disconnected")


# ======================
# 📤 publish sensors
# ======================
def publish_sensors(data):
    global _connected

    if not _client or not _connected:
        return False

    try:
        data["ts"] = time.time()
        payload = json.dumps(data).encode()

        _client.publish(config.MQTT_PUB_SENSORS, payload)

        print(f"📤 [MQTT] sent {len(payload)} bytes")
        return True

    except Exception as e:
        print(f"❌ [MQTT] publish error: {e}")
        _connected = False
        return False


# ======================
# 📩 check messages
# ======================
def check_messages():
    global _connected

    if not _client or not _connected:
        return

    try:
        _client.check_msg()

    except Exception as e:
        err = str(e)

        # normal no-message case
        if "-1" in err or "EAGAIN" in err:
            return

        print(f"⚠️ [MQTT] error: {e}")
        _connected = False


# ======================
# 🔄 reconnect helper
# ======================
def reconnect_if_needed():
    global _connected
    if not _connected:
        print("🔄 [MQTT] reconnecting...")
        connect()


# ======================
# 🎯 command callback
# ======================
def on_command(callback):
    global _cmd_cb
    _cmd_cb = callback


def is_connected():
    return _connected


# ======================
# 📩 message handler
# ======================
def _on_message(topic, msg):
    try:
        cmd = msg.decode().strip()

        print(f"📩 [MQTT] cmd: {cmd}")

        if _cmd_cb:
            _cmd_cb(cmd)

    except Exception as e:
        print(f"❌ [MQTT] msg error: {e}")