
import os
import sys
sys.path.append('/app')

from config import OTA_PASSWORD


# --------- Handle OTA Upload ---------------

def handle_ota_request(headers, body):
    

    pwd = headers.get("x-ota-password", "")

    if pwd != OTA_PASSWORD:

        print("[OTA] wrong password")
        return 401, "Unauthorized: wrong password"


    filename = headers.get("x-ota-filename", "").strip()


    if not filename:
        return 400, "Missing X-OTA-Filename header"

    if not filename.endswith(".py"):
        return 400, "Only .py files accepted"


    try:
      
        if filename in ["sensors.py", "actuators.py", "wifi_manager.py",
                        "mqtt_client.py", "web_server.py", "ota.py"]:

            path = "/app/" + filename

        else:

            path = "/" + filename

        with open(path, "wb") as f:

            f.write(body)

        size = len(body)

        print(f"[OTA] saved {path} ({size} bytes)")
        return 200, f"OK: {filename} saved ({size} bytes) → {path}"

    except Exception as e:

        print("[OTA] write error:", e)
        return 500, f"Write error: {e}"

# --------- List Files ---------------

def list_files():
  
    files = []

    def scan(folder):

        try:

            for name in os.listdir(folder):

                full = folder + "/" + name if folder != "/" else "/" + name

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



# --------- Delete File ---------------

def delete_file(filename):

    try:

        os.remove(filename)

        print(f"[OTA] deleted {filename}")
        return True, f"Deleted {filename}"

    except Exception as e:

        return False, str(e)

# --------- Free Space ---------------

def free_space():

    try:

        s     = os.statvfs("/")
        block = s[0]
        total = s[2] * block
        free  = s[3] * block
        used  = total - free

        return used // 1024, total // 1024

    except:

        return 0, 0
