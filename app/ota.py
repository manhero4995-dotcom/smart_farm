

# ==================
# 📦 app/ota.py — Over The Air file upload
# ==================

import os
import sys

sys.path.append('/app')

from config import OTA_PASSWORD

def handle_ota_request(headers, body):

    pwd = headers.get("x-ota-password", "")

    if pwd != OTA_PASSWORD:

        print("❌ [OTA] wrong password")
        return 401, "Unauthorized"

    filename = headers.get("x-ota-filename", "").strip()

    if not filename:
        return 400, "Missing filename header"

    if not filename.endswith(".py") and \
       not filename.endswith(".html"):

        return 400, "Only .py and .html accepted"

    try:

        app_files = [
            "sensors.py", "actuators.py",
            "wifi_manager.py", "mqtt_client.py",
            "web_server.py", "ota.py", "index.html"
        ]
        path = "/app/" + filename \
               if filename in app_files else "/" + filename

        with open(path, "wb") as f:

            f.write(body)
        size = len(body)

        print(f"✅ [OTA] saved {path} ({size}b)")
        return 200, f"OK: {filename} saved ({size} bytes)"

    except Exception as e:

        print(f"❌ [OTA] error: {e}")
        return 500, f"Error: {e}"

def list_files():

    files = []

    def scan(folder):

        try:

            for name in os.listdir(folder):
                full = folder.rstrip('/') + '/' + name

                try:

                    stat = os.stat(full)

                    if stat[0] & 0x4000:
                        scan(full)

                    else:
                        files.append({
                            "name": full,
                            "size": stat[6]
                        })

                except:
                    pass

        except:
            pass

    scan("/")

    return files

def free_space():

    try:

        s     = os.statvfs("/")
        block = s[0]
        total = s[2] * block
        free  = s[3] * block

        return (total - free) // 1024, total // 1024

    except:

        return 0, 0
