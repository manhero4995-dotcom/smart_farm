


# ============================================================
#  web_server.py  —  Async HTTP server + Web Dashboard
#  Routes:
#    GET  /           → Dashboard HTML
#    GET  /api/data   → JSON sensor data
#    POST /api/relay  → Control relay {num, state}
#    POST /api/sleep  → Enter deep sleep now
#    GET  /ota        → OTA upload page
#    POST /ota        → Upload file (OTA)
#    GET  /api/files  → List filesystem
#    POST /api/delete → Delete file
# ============================================================
import json, gc
import usocket as socket
from sensors   import read_all
from actuators import relay_set, relay_get, all_relays_off, oled_show
from ota       import handle_ota_request, list_files, delete_file, free_space
from config    import WEB_PORT, SLEEP_SECONDS
 
# ── Shared state ─────────────────────────────────────────────
_last_data   = {}
_auto_mode   = True     # True = automatic irrigation logic
_sleep_flag  = False    # Set True to trigger sleep after response
 
# ── HTML Dashboard ────────────────────────────────────────────
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Smart Farm IoT</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
  header{background:#1e293b;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #334155}
  header h1{font-size:1.3rem;color:#38bdf8;display:flex;align-items:center;gap:8px}
  .dot{width:10px;height:10px;border-radius:50%;background:#22c55e;animation:pulse 2s infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
  main{padding:20px;max-width:900px;margin:0 auto}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:24px}
  .card{background:#1e293b;border-radius:12px;padding:18px;border:1px solid #334155}
  .card-label{font-size:.72rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}
  .card-value{font-size:2rem;font-weight:700;color:#f1f5f9}
  .card-unit{font-size:.9rem;color:#64748b;margin-left:4px}
  .card-bar{height:6px;background:#0f172a;border-radius:3px;margin-top:10px;overflow:hidden}
  .card-bar-fill{height:100%;border-radius:3px;transition:width .6s}
  .bar-blue{background:#38bdf8}
  .bar-green{background:#22c55e}
  .bar-amber{background:#f59e0b}
  .bar-red{background:#ef4444}
  section{background:#1e293b;border-radius:12px;padding:20px;border:1px solid #334155;margin-bottom:18px}
  section h2{font-size:.9rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.06em;margin-bottom:16px}
  .relay-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}
  .relay-btn{padding:10px 0;border:none;border-radius:8px;cursor:pointer;font-size:.88rem;font-weight:600;transition:all .2s}
  .relay-on{background:#22c55e;color:#052e16}
  .relay-off{background:#334155;color:#94a3b8}
  .relay-on:hover{background:#16a34a}
  .relay-off:hover{background:#475569}
  .btn{padding:10px 20px;border:none;border-radius:8px;cursor:pointer;font-weight:600;font-size:.88rem;transition:all .15s}
  .btn-blue{background:#0ea5e9;color:#fff}
  .btn-blue:hover{background:#0284c7}
  .btn-red{background:#ef4444;color:#fff}
  .btn-red:hover{background:#dc2626}
  .btn-amber{background:#f59e0b;color:#1c1000}
  .btn-amber:hover{background:#d97706}
  .toggle{display:flex;align-items:center;gap:10px;margin-bottom:12px}
  .toggle input[type=checkbox]{width:36px;height:20px;accent-color:#38bdf8;cursor:pointer}
  .log{background:#0f172a;border-radius:8px;padding:12px;font-family:monospace;font-size:.78rem;color:#94a3b8;height:100px;overflow-y:auto;border:1px solid #334155}
  .tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.72rem;font-weight:600;margin-left:6px}
  .tag-ok{background:#052e16;color:#22c55e}
  .tag-warn{background:#431407;color:#f97316}
  .tag-err{background:#450a0a;color:#ef4444}
  .row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
  .spacer{flex:1}
  input[type=number],input[type=password]{background:#0f172a;border:1px solid #334155;color:#e2e8f0;padding:8px 12px;border-radius:8px;width:80px;font-size:.88rem}
  a{color:#38bdf8;text-decoration:none}
</style>
</head>
<body>
<header>
  <h1><span>🌿</span> Smart Farm IoT</h1>
  <div style="display:flex;align-items:center;gap:10px">
    <div class="dot" id="status-dot"></div>
    <span id="status-txt" style="font-size:.8rem;color:#94a3b8">Connecting…</span>
  </div>
</header>
<main>
 
<!-- Sensor Cards -->
<div class="grid" id="cards">
  <div class="card">
    <div class="card-label">Temperature</div>
    <div class="card-value" id="val-temp">--<span class="card-unit">°C</span></div>
    <div class="card-bar"><div class="card-bar-fill bar-amber" id="bar-temp" style="width:0%"></div></div>
  </div>
  <div class="card">
    <div class="card-label">Air Humidity</div>
    <div class="card-value" id="val-hum">--<span class="card-unit">%</span></div>
    <div class="card-bar"><div class="card-bar-fill bar-blue" id="bar-hum" style="width:0%"></div></div>
  </div>
  <div class="card">
    <div class="card-label">Soil Moisture</div>
    <div class="card-value" id="val-soil">--<span class="card-unit">%</span></div>
    <div class="card-bar"><div class="card-bar-fill bar-green" id="bar-soil" style="width:0%"></div></div>
  </div>
  <div class="card">
    <div class="card-label">Tank Level</div>
    <div class="card-value" id="val-tank">--<span class="card-unit">%</span></div>
    <div class="card-bar"><div class="card-bar-fill bar-blue" id="bar-tank" style="width:0%"></div></div>
  </div>
</div>
 
<!-- Relay Control -->
<section>
  <h2>Relay Control</h2>
  <div class="relay-grid" id="relay-grid">
    <button class="relay-btn relay-off" onclick="toggleRelay(1)" id="relay-1">Relay 1 — Pump ⬤ OFF</button>
    <button class="relay-btn relay-off" onclick="toggleRelay(2)" id="relay-2">Relay 2 ⬤ OFF</button>
    <button class="relay-btn relay-off" onclick="toggleRelay(3)" id="relay-3">Relay 3 ⬤ OFF</button>
    <button class="relay-btn relay-off" onclick="toggleRelay(4)" id="relay-4">Relay 4 ⬤ OFF</button>
  </div>
  <div style="margin-top:12px" class="row">
    <label class="toggle">
      <input type="checkbox" id="auto-mode" checked onchange="setAuto(this.checked)">
      <span style="font-size:.85rem">Auto irrigation mode</span>
    </label>
    <span class="spacer"></span>
    <button class="btn btn-red" onclick="allOff()">All Relays OFF</button>
  </div>
</section>
 
<!-- Sleep & System -->
<section>
  <h2>Power & Sleep</h2>
  <div class="row">
    <span style="font-size:.85rem">Sleep duration:</span>
    <input type="number" id="sleep-sec" value="300" min="10" max="3600">
    <span style="font-size:.85rem">seconds</span>
    <button class="btn btn-amber" onclick="goSleep()">💤 Deep Sleep Now</button>
    <span class="spacer"></span>
    <button class="btn btn-blue" onclick="fetchData()">↻ Refresh</button>
  </div>
</section>
 
<!-- OTA Update -->
<section>
  <h2>OTA File Upload</h2>
  <div class="row">
    <input type="password" id="ota-pwd" placeholder="OTA password" style="width:140px">
    <input type="file" id="ota-file" accept=".py">
    <button class="btn btn-blue" onclick="uploadOTA()">⬆ Upload</button>
  </div>
  <div id="ota-status" style="margin-top:8px;font-size:.8rem;color:#94a3b8"></div>
  <div id="fs-list" style="margin-top:12px;font-size:.78rem;color:#64748b"></div>
</section>
 
<!-- Log -->
<section>
  <h2>Event Log</h2>
  <div class="log" id="log"></div>
</section>
 
</main>
<script>
const relayStates = {1:false,2:false,3:false,4:false};
const relayNames  = {1:"Pump",2:"Relay 2",3:"Relay 3",4:"Relay 4"};
 
function log(msg, type="info"){
  const d=document.getElementById("log");
  const t=new Date().toLocaleTimeString();
  const cls=type==="ok"?"tag-ok":type==="warn"?"tag-warn":"tag-err";
  d.innerHTML=`<span style="color:#475569">[${t}]</span> ${msg}<br>`+d.innerHTML;
}
 
async function fetchData(){
  try{
    const r=await fetch("/api/data");
    const d=await r.json();
    document.getElementById("status-dot").style.background="#22c55e";
    document.getElementById("status-txt").textContent="Live";
 
    const set=(id,val,unit="")=>{
      const el=document.getElementById(id);
      if(el) el.innerHTML=val!==null?`${val}<span class="card-unit">${unit}</span>`:`--`;
    };
    set("val-temp",d.temperature,"°C");
    set("val-hum",d.humidity,"%");
    set("val-soil",d.soil_pct,"%");
    set("val-tank",d.tank_pct,"%");
    const bar=(id,v,max=100)=>{const el=document.getElementById(id);if(el)el.style.width=(v/max*100)+"%";};
    bar("bar-temp",d.temperature,50);
    bar("bar-hum",d.humidity);
    bar("bar-soil",d.soil_pct);
    bar("bar-tank",d.tank_pct);
 
    [1,2,3,4].forEach(n=>{
      relayStates[n]=d["relay_"+n]||false;
      updateRelayBtn(n);
    });
 
    if(d.auto_mode!==undefined)
      document.getElementById("auto-mode").checked=d.auto_mode;
 
    log(`Temp:${d.temperature}°C Hum:${d.humidity}% Soil:${d.soil_pct}% Tank:${d.tank_pct}%`,"ok");
  } catch(e){
    document.getElementById("status-dot").style.background="#ef4444";
    document.getElementById("status-txt").textContent="Offline";
    log("Fetch failed: "+e,"err");
  }
}
 
function updateRelayBtn(n){
  const btn=document.getElementById("relay-"+n);
  if(!btn) return;
  const on=relayStates[n];
  btn.className="relay-btn "+(on?"relay-on":"relay-off");
  btn.textContent=`${relayNames[n]} ⬤ ${on?"ON":"OFF"}`;
}
 
async function toggleRelay(n){
  const newState=!relayStates[n];
  try{
    await fetch("/api/relay",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({num:n,state:newState})});
    relayStates[n]=newState;
    updateRelayBtn(n);
    log(`Relay ${n} → ${newState?"ON":"OFF"}`,"ok");
  } catch(e){ log("Relay error: "+e,"err"); }
}
 
async function allOff(){
  try{
    await fetch("/api/relay",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({num:0,state:false})});
    [1,2,3,4].forEach(n=>{relayStates[n]=false;updateRelayBtn(n);});
    log("All relays OFF","ok");
  } catch(e){ log("Error: "+e,"err"); }
}
 
async function setAuto(val){
  try{
    await fetch("/api/auto",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({auto:val})});
    log("Auto mode: "+val,"ok");
  } catch(e){}
}
 
async function goSleep(){
  const sec=document.getElementById("sleep-sec").value||300;
  if(!confirm(`Enter deep sleep for ${sec} seconds?`)) return;
  try{
    await fetch("/api/sleep",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({seconds:parseInt(sec)})});
    log(`Entering deep sleep for ${sec}s…`,"warn");
    document.getElementById("status-dot").style.background="#f59e0b";
    document.getElementById("status-txt").textContent="Sleeping…";
  } catch(e){}
}
 
async function uploadOTA(){
  const pwd=document.getElementById("ota-pwd").value;
  const file=document.getElementById("ota-file").files[0];
  if(!file){ alert("Select a file first"); return; }
  const status=document.getElementById("ota-status");
  status.textContent="Uploading "+file.name+"…";
  try{
    const buf=await file.arrayBuffer();
    const r=await fetch("/ota",{method:"POST",
      headers:{"X-OTA-Password":pwd,"X-OTA-Filename":file.name,"Content-Type":"application/octet-stream"},
      body:buf});
    const txt=await r.text();
    status.textContent=r.ok?"✓ "+txt:"✗ "+txt;
    status.style.color=r.ok?"#22c55e":"#ef4444";
    log((r.ok?"OTA OK: ":"OTA FAIL: ")+file.name, r.ok?"ok":"err");
    loadFileList();
  } catch(e){ status.textContent="Error: "+e; }
}
 
async function loadFileList(){
  try{
    const r=await fetch("/api/files");
    const files=await r.json();
    const el=document.getElementById("fs-list");
    el.innerHTML="<b>Filesystem:</b> "+files.map(f=>
      `<span style="margin:0 8px">${f.name} <span style="color:#475569">(${f.size}b)</span></span>`
    ).join("");
  } catch(e){}
}
 
// Auto-refresh every 10 seconds
fetchData();
loadFileList();
setInterval(fetchData, 10000);
</script>
</body>
</html>"""
 
# ── HTTP Server ───────────────────────────────────────────────
def _parse_request(conn):
    """Parse raw HTTP request → (method, path, headers, body)"""
    raw = b""
    while True:
        chunk = conn.recv(1024)
        raw += chunk
        if len(chunk) < 1024:
            break
 
    try:
        header_part, _, body = raw.partition(b"\r\n\r\n")
        lines = header_part.decode("utf-8", "ignore").split("\r\n")
        method, path, _ = lines[0].split(" ", 2)
        headers = {}
        for line in lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()
        return method, path, headers, body
    except:
        return "GET", "/", {}, b""
 
def _send(conn, status, ctype, body):
    if isinstance(body, str):
        body = body.encode()
    conn.sendall(
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {ctype}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Access-Control-Allow-Origin: *\r\n"
        f"Connection: close\r\n\r\n".encode() + body
    )
 
def run():
    global _last_data, _auto_mode, _sleep_flag
 
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", WEB_PORT))
    s.listen(3)
    s.settimeout(1.0)
    print(f"[WEB] Listening on :{WEB_PORT}")
 
    while not _sleep_flag:
        try:
            conn, addr = s.accept()
        except OSError:
            continue
 
        try:
            method, path, headers, body = _parse_request(conn)
            print(f"[WEB] {method} {path}")
 
            # ── GET / ────────────────────────────────────────
            if path == "/" and method == "GET":
                _send(conn, "200 OK", "text/html", DASHBOARD_HTML)
 
            # ── GET /api/data ─────────────────────────────────
            elif path == "/api/data" and method == "GET":
                data = read_all()
                _last_data = data
                data["relay_1"]   = relay_get(1)
                data["relay_2"]   = relay_get(2)
                data["relay_3"]   = relay_get(3)
                data["relay_4"]   = relay_get(4)
                data["auto_mode"] = _auto_mode
                oled_show(data)
                _send(conn, "200 OK", "application/json", json.dumps(data))
 
            # ── POST /api/relay ───────────────────────────────
            elif path == "/api/relay" and method == "POST":
                try:
                    req = json.loads(body)
                    num   = req.get("num", 0)
                    state = req.get("state", False)
                    if num == 0:
                        all_relays_off()
                    else:
                        relay_set(num, state)
                    _send(conn, "200 OK", "application/json", '{"ok":true}')
                except Exception as e:
                    _send(conn, "400 Bad Request", "text/plain", str(e))
 
            # ── POST /api/auto ────────────────────────────────
            elif path == "/api/auto" and method == "POST":
                try:
                    req = json.loads(body)
                    _auto_mode = bool(req.get("auto", True))
                    _send(conn, "200 OK", "application/json", '{"ok":true}')
                except:
                    _send(conn, "400 Bad Request", "text/plain", "bad json")
 
            # ── POST /api/sleep ───────────────────────────────
            elif path == "/api/sleep" and method == "POST":
                try:
                    req = json.loads(body)
                    secs = int(req.get("seconds", SLEEP_SECONDS))
                    _send(conn, "200 OK", "application/json",
                          json.dumps({"ok": True, "sleep_seconds": secs}))
                    conn.close()
                    import machine
                    all_relays_off()
                    machine.deepsleep(secs * 1000)
                except Exception as e:
                    _send(conn, "500 Error", "text/plain", str(e))
 
            # ── POST /ota ─────────────────────────────────────
            elif path == "/ota" and method == "POST":
                code, msg = handle_ota_request(headers, body)
                _send(conn, f"{code} {'OK' if code==200 else 'Error'}",
                      "text/plain", msg)
 
            # ── GET /api/files ────────────────────────────────
            elif path == "/api/files" and method == "GET":
                files = list_files()
                _send(conn, "200 OK", "application/json", json.dumps(files))
 
            # ── POST /api/delete ──────────────────────────────
            elif path == "/api/delete" and method == "POST":
                try:
                    req = json.loads(body)
                    ok, msg = delete_file(req.get("filename", ""))
                    _send(conn, "200 OK", "application/json",
                          json.dumps({"ok": ok, "msg": msg}))
                except Exception as e:
                    _send(conn, "400 Bad Request", "text/plain", str(e))
 
            # ── 404 ───────────────────────────────────────────
            else:
                _send(conn, "404 Not Found", "text/plain", "Not found")
 
        except Exception as e:
            print("[WEB] Handler error:", e)
        finally:
            conn.close()
            gc.collect()
 
    s.close()
    print("[WEB] Server stopped (sleep flag set)")