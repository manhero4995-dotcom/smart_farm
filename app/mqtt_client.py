# ============================================================
# mqtt_client.py — إرسال واستقبال عبر MQTT
#
# MQTT = Message Queuing Telemetry Transport
# بروتوكول خفيف جداً مصمم للـ IoT
#
# الفكرة:
#   Publisher  → بيبعت رسالة على topic معين
#   Subscriber → بيستنى رسايل على topic معين
#   Broker     → الوسيط (mosquitto على جهازك)
#
# مشروعنا:
#   ESP32 بيبعت  → farm/sensors (البيانات)
#   ESP32 بيسمع  → farm/cmd     (الأوامر)
# ============================================================

import json
import time
import sys
sys.path.append('/lib')
sys.path.append('/app')
from umqtt.simple import MQTTClient
from config import *

# متغيرات عامة
_client = None    # الـ connection object
_cmd_cb = None    # الـ function اللي بتتنفذ لما ييجي أمر


def connect():
    """
    اتصل بالـ MQTT broker
    بترجع True لو نجح
    """
    global _client

    if not MQTT_ENABLED:
        print("[MQTT] disabled in config")
        return False

    try:
        _client = MQTTClient(
            client_id = MQTT_CLIENT,   # اسم الجهاز على الـ broker
            server    = MQTT_BROKER,   # IP الـ broker
            port      = MQTT_PORT,     # 1883 الافتراضي
            user      = MQTT_USER,
            password  = MQTT_PASS,
            keepalive = 60             # ابعت ping كل 60 ثانية
        )

        # Last Will = رسالة تتبعت تلقائياً لو الـ ESP32 انقطع فجأة
        _client.set_last_will(MQTT_PUB_STATUS, b'offline', retain=True)

        # سجّل الـ callback اللي بيتنفذ لما تيجي رسالة
        _client.set_callback(_on_message)

        _client.connect()

        # اشترك في topic الأوامر
        _client.subscribe(MQTT_SUB_CMD)

        # أعلن إنك online
        _client.publish(MQTT_PUB_STATUS, b'online', retain=True)

        print(f"[MQTT] connected → {MQTT_BROKER}")
        print(f"[MQTT] listening on → {MQTT_SUB_CMD}")
        return True

    except Exception as e:
        print("[MQTT] connect error:", e)
        _client = None
        return False


def disconnect():
    global _client
    if _client:
        try:
            _client.publish(MQTT_PUB_STATUS, b'offline', retain=True)
            _client.disconnect()
        except:
            pass
        _client = None
        print("[MQTT] disconnected")


def publish_sensors(data):
    """
    ابعت بيانات السنسورات كـ JSON
    على topic: farm/sensors
    """
    if not _client:
        print("[MQTT] not connected")
        return False
    try:
        data["ts"] = time.time()              # أضف timestamp
        payload    = json.dumps(data).encode() # حوّل لـ bytes
        _client.publish(MQTT_PUB_SENSORS, payload)
        print(f"[MQTT] published {len(payload)}b → {MQTT_PUB_SENSORS}")
        return True
    except Exception as e:
        print("[MQTT] publish error:", e)
        return False


def check_messages():
    """
    اتحقق من الرسايل الجديدة — Non-blocking
    بتتنادى في الـ loop كل iteration
    """
    if not _client:
        return
    try:
        _client.check_msg()    # لو في رسالة → بتنادي _on_message
    except Exception as e:
        print("[MQTT] check_msg error:", e)


def _on_message(topic, msg):
    """
    بتتنادى تلقائياً لما تيجي رسالة على farm/cmd
    topic : اسم الـ topic
    msg   : محتوى الرسالة (bytes)
    """
    try:
        cmd = msg.decode().strip().lower()
        print(f"[MQTT] command received: '{cmd}'")
        if _cmd_cb:
            _cmd_cb(cmd)    # نادي الـ handle_command في main.py
    except Exception as e:
        print("[MQTT] message error:", e)


def on_command(callback):
    """
    سجّل الـ function اللي بتتنفذ لما ييجي أمر
    بتتنادى من main.py:
        mqtt_client.on_command(handle_command)
    """
    global _cmd_cb
    _cmd_cb = callback


def is_connected():
    return _client is not None

