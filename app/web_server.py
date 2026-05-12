# ====================
# 🌐 Smart Farm Web Server — FINAL VERSION
# ====================

import json
import gc
import sys
import machine

sys.path.append('/app')
sys.path.append('/lib')

from sensors import read_all
from actuators import *
from ota import handle_ota_request, list_files
from config import *

# ─────────────────────────────
# 🌐 IP storage (set from main.py)
# ─────────────────────────────
_sta_ip = None
_ap_ip  = None

def set_ips(sta, ap):
    global _sta_ip, _ap_ip
    _sta_ip = sta
    _ap_ip = ap


# ─────────────────────────────
# 📡 HTTP Request Parser
# ─────────────────────────────
def _parse(conn):
    raw = b""
    try:
        conn.settimeout(5)

        while True:
            chunk = conn.recv(1024)
            if not chunk:
                break
            raw += chunk
            if len(chunk) < 1024:
                break

    except OSError:
        pass

    try:
        head, _, body = raw.partition(b"\r\n\r\n")
        lines = head.decode().split("\r\n")

        method, path, _ = lines[0].split(" ")[:3]
        path = path.split("?")[0]

        headers = {}
        for line in lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.lower()] = v.strip()

        clen = int(headers.get("content-length", 0))
        if clen > len(body):
            body += conn.recv(clen - len(body))

        return method, path, headers, body

    except:
        return "GET", "/", {}, b""


# ─────────────────────────────
# 📤 HTTP Response Sender
# ─────────────────────────────
def _send(conn, status, ctype, body):
    if isinstance(body, str):
        body = body.encode()

    header = (
        "HTTP/1.1 {}\r\n"
        "Content-Type: {}\r\n"
        "Content-Length: {}\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Connection: close\r\n\r\n"
    ).format(status, ctype, len(body))

    conn.send(header.encode() + body)


# ─────────────────────────────
# 🌐 Main Handler
# ─────────────────────────────
def handle(conn):
    try:
        method, path, headers, body = _parse(conn)
        print("🌐", method, path)

        # ───── CORS ─────
        if method == "OPTIONS":
            _send(conn, "200 OK", "text/plain", "")
            return

        # ─────────────────────────
        # 🏠 Dashboard
        # ─────────────────────────
        if path == "/" and method == "GET":
            conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            with open("/app/index.html", "r") as f:
                while True:
                    chunk = f.read(512)
                    if not chunk:
                        break
                    conn.send(chunk)

        # ─────────────────────────
        # 📊 Sensor Data API
        # ─────────────────────────
        elif path == "/api/data":
            data = read_all()

            data.update({
                "relay_1": relay_get(1),
                "relay_2": relay_get(2),
                "relay_3": relay_get(3),
                "relay_4": relay_get(4),
                "free_ram": gc.mem_free(),
                "sta_ip": _sta_ip,
                "ap_ip": _ap_ip
            })

            oled_show(data)
            tank_leds_update(data.get("tank_pct"))

            _send(conn, "200 OK", "application/json", json.dumps(data))

        # ─────────────────────────
        # 🔌 Relay Control
        # ─────────────────────────
        elif path == "/api/relay" and method == "POST":
            req = json.loads(body or b"{}")

            num = int(req.get("num", 0))
            state = bool(req.get("state", False))

            if num == 0:
                all_relays_off()
                result = {
                    "ok": True,
                    "all": "OFF"
                }
            else:
                relay_set(num, state)
                result = {
                    "ok": True,
                    "relay": num,
                    "state": relay_get(num)
                }

            _send(conn, "200 OK", "application/json", json.dumps(result))

        # ─────────────────────────
        # 💤 Deep Sleep
        # ─────────────────────────
        elif path == "/api/sleep" and method == "POST":
            req = json.loads(body or b"{}")
            secs = int(req.get("seconds", SLEEP_SECONDS))

            _send(conn, "200 OK", "application/json",
                  json.dumps({"ok": True, "sleep": secs}))

            conn.close()
            all_relays_off()
            machine.deepsleep(secs * 1000)

        # ─────────────────────────
        # 🔁 Reset
        # ─────────────────────────
        elif path == "/api/reset":
            _send(conn, "200 OK", "application/json", '{"ok":true}')
            conn.close()
            machine.reset()

        # ─────────────────────────
        # 📤 OTA Update
        # ─────────────────────────
        elif path == "/ota" and method == "POST":
            result = handle_ota_request(headers, body)

            if len(result) == 3:
                code, msg, do_reset = result
            else:
                code, msg = result
                do_reset = False

            _send(conn,
                  f"{code} OK" if code == 200 else f"{code} ERROR",
                  "text/plain",
                  msg)

            conn.close()
            gc.collect()

            if do_reset:
                import time
                time.sleep(1)
                machine.reset()

            return

        # ─────────────────────────
        # 📁 Files list
        # ─────────────────────────
        elif path == "/api/files":
            _send(conn, "200 OK", "application/json",
                  json.dumps(list_files()))

        # ─────────────────────────
        # ❌ Not Found
        # ─────────────────────────
        else:
            _send(conn, "404 Not Found", "text/plain", "Not Found")

    except Exception as e:
        print("❌ WEB ERROR:", e)

    finally:
        try:
            conn.close()
        except:
            pass
        gc.collect()