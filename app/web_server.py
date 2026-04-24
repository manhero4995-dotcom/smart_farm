
# ====================
# 🌐 app/web_server.py — HTTP Server
# Work html and API
# ====================

import json
import gc
import gc as _gc
import sys
import machine

sys.path.append('/app')
sys.path.append('/lib')

from sensors   import read_all
from actuators import *
from ota       import handle_ota_request, list_files
from config    import *

def _load_html():

    try:

        with open("/app/index.html", "r") as f:
            return f.read()

    except Exception as e:

        print(f"❌ [WEB] index.html not found: {e}")
        return "<h2>Upload index.html via OTA</h2>"

def _parse(conn):

    raw = b""

    while True:

        chunk = conn.recv(1024)

        if not chunk:
            break

        raw += chunk

        if len(chunk) < 1024:
            break

    try:

        head, _, body = raw.partition(b"\r\n\r\n")
        lines  = head.decode("utf-8", "ignore").split("\r\n")
        parts  = lines[0].split(" ")

        if len(parts) < 2:
            return "GET", "/", {}, b""

        method = parts[0]
        path   = parts[1]
        headers = {}

        for line in lines[1:]:

            if ":" in line:

                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()

        return method, path, headers, body

    except Exception as e:

        print(f"⚠️  [WEB] parse error: {e}")
        return "GET", "/", {}, b""

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

    conn.sendall(header.encode() + body)

def handle(conn):

    try:

        method, path, headers, body = _parse(conn)

        print(f"🌐 [WEB] {method} {path}")

        # GET / → Dashboard
        if path == "/" and method == "GET":
            
            conn.send("HTTP/1.1 200 OK\r\n")
            conn.send("Content-Type: text/html\r\n")
            conn.send("Connection: close\r\n\r\n")

            try:

                with open("/app/index.html", "r") as f:  
                
                    while True:

                        chunk = f.read(512)

                        if not chunk:
                            break

                        conn.send(chunk)

            except Exception as e:

                print(f"❌ [WEB] index.html error: {e}")
                conn.send("<h2>Error loading page</h2>")


        # GET /api/data → JSON
        elif path == "/api/data" and method == "GET":

            data = read_all()

            data["relay_1"]  = relay_get(1)
            data["relay_2"]  = relay_get(2)
            data["relay_3"]  = relay_get(3)
            data["relay_4"]  = relay_get(4)
            data["free_ram"] = _gc.mem_free()

            oled_show(data)

            tank_leds_update(data.get("tank_pct"))

            _send(conn, "200 OK", "application/json",
                  json.dumps(data))

        # POST /api/relay → control relay
        elif path == "/api/relay" and method == "POST":

            req   = json.loads(body.decode())
            num   = req.get("num",   0)
            state = req.get("state", False)

            if num == 0:

                all_relays_off()

            else:

                relay_set(num, state)
            _send(conn, "200 OK", "application/json",
                  '{"ok":true}')

        # POST /api/sleep → deep sleep

        elif path == "/api/sleep" and method == "POST":

            req  = json.loads(body.decode())
            secs = int(req.get("seconds", SLEEP_SECONDS))
            _send(conn, "200 OK", "application/json",
                  json.dumps({"ok": True, "seconds": secs}))
            conn.close()

            all_relays_off()
            machine.deepsleep(secs * 1000)

        # POST /api/reset → restart
        elif path == "/api/reset" and method == "POST":

            _send(conn, "200 OK", "application/json",
                  '{"ok":true}')

            conn.close()
            machine.reset()

        # POST /ota → upload file

        elif path == "/ota" and method == "POST":

            code, msg = handle_ota_request(headers, body)
            _send(conn,
                  f"{code} {'OK' if code==200 else 'Error'}",
                  "text/plain", msg)

        # GET /api/files → list files

        elif path == "/api/files" and method == "GET":
            _send(conn, "200 OK", "application/json",
                  json.dumps(list_files()))

        # 404
        else:

            _send(conn, "404 Not Found",
                  "text/plain", "not found")

    except Exception as e:

        print(f"❌ [WEB] error: {e}")

    finally:

        conn.close()
        gc.collect()
