

# ==================
# 📦 ota.py (MICROPYTHON SAFE VERSION)
# ==================

import os
import sys
import machine

sys.path.append('/app')

from config import OTA_PASSWORD


# ======================
# 📂 File routing
# ======================

ROOT_FILES = (
    "config.py",
    "main.py",
    "boot.py",
)

APP_FILES = (
    "sensors.py",
    "actuators.py",
    "wifi_manager.py",
    "mqtt_client.py",
    "web_server.py",
    "ota.py",
    "index.html",
)


# ======================
# 🔐 OTA Handler
# ======================
def handle_ota_request(headers, body):

    # ─── password check ───
    pwd = headers.get("x-ota-password", "")
    if pwd != OTA_PASSWORD:
        print("❌ [OTA] wrong password")
        return 401, "Unauthorized", False

    # ─── filename ───
    filename = headers.get("x-ota-filename", "").strip()
    if not filename:
        return 400, "Missing filename", False

    # ─── SAFE filename (NO os.path in MicroPython) ───
    filename = filename.split('/')[-1]
    filename = filename.split('\\')[-1]

    # ─── validate extension ───
    if not (filename.endswith(".py") or filename.endswith(".html")):
        return 400, "Only .py and .html allowed", False

    # ─── choose storage location ───
    if filename in ROOT_FILES:
        path = "/" + filename
    else:
        path = "/app/" + filename

    try:
        print(f"📦 [OTA] writing -> {path}")
        print(f"📦 [OTA] size -> {len(body)} bytes")

        # write file
        with open(path, "wb") as f:
            f.write(body)

        print(f"✅ [OTA] saved: {path}")

        needs_reset = True
        msg = f"OK: {filename} updated -> {path}"

        return 200, msg, needs_reset

    except Exception as e:
        print(f"❌ [OTA] error: {e}")
        return 500, str(e), False


# ==================
# 📂 list files (debug)
# ==================
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


# ==================
# 💾 free space
# ==================
def free_space():
    try:
        s = os.statvfs("/")
        block = s[0]
        total = s[2] * block
        free = s[3] * block
        return (total - free) // 1024, total // 1024
    except:
        return 0, 0