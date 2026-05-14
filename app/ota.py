# ==================
# 📦 ota.py (MULTI FILE SAFE VERSION)
# ==================

import os
import sys

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
# 🔐 OTA HANDLER
# ======================

def handle_ota_request(headers, body):

    # ─────────────────────────
    # 🔐 Password check
    # ─────────────────────────

    pwd = headers.get("x-ota-password", "")

    if pwd != OTA_PASSWORD:
        print("❌ [OTA] wrong password")
        return 401, "Unauthorized", False


    # ─────────────────────────
    # 📄 Filename
    # ─────────────────────────

    filename = headers.get("x-ota-filename", "").strip()

    if not filename:
        return 400, "Missing filename", False

    # clean filename
    filename = filename.split('/')[-1]
    filename = filename.split('\\')[-1]


    # ─────────────────────────
    # 📌 Validate file type
    # ─────────────────────────

    if not (filename.endswith(".py") or filename.endswith(".html")):
        return 400, "Only .py and .html allowed", False


    # ─────────────────────────
    # 📁 Select path
    # ─────────────────────────

    if filename in ROOT_FILES:
        path = "/" + filename
    else:
        path = "/app/" + filename


    try:

        print("================================")
        print(f"📦 OTA FILE: {filename}")
        print(f"📂 PATH: {path}")
        print(f"📏 SIZE: {len(body)} bytes")
        print("================================")

        # ─────────────────────────
        # 💾 WRITE FILE
        # ─────────────────────────

        with open(path, "wb") as f:
            f.write(body)

        print(f"✅ Saved: {path}")

        return 200, f"OK: {filename} updated", True


    except Exception as e:

        print(f"❌ [OTA ERROR]: {e}")

        return 500, str(e), False


# ==================
# 📂 LIST FILES
# ==================

def list_files():

    files = []

    def scan(folder):

        try:

            for name in os.listdir(folder):

                full = folder.rstrip('/') + '/' + name

                try:

                    stat = os.stat(full)

                    # directory
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
# 💾 FREE SPACE
# ==================

def free_space():

    try:

        s = os.statvfs("/")

        block = s[0]
        total = s[2] * block
        free  = s[3] * block

        used = total - free

        return used // 1024, total // 1024

    except:

        return 0, 0