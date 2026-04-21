# ============================================================
# web_server.py — HTTP Server + Web Dashboard
#
# الـ ESP32 بيشتغل كـ Web Server صغير
# بيستقبل requests من المتصفح ويرد عليها
#
# Routes:
#   GET  /           → الـ Dashboard HTML
#   GET  /api/data   → بيانات السنسورات JSON
#   POST /api/relay  → تحكم في الريلاي
#   POST /api/sleep  → Deep Sleep
#   POST /ota        → رفع ملف جديد
#   GET  /api/files  → قائمة الملفات
# ============================================================

import json
import gc
import sys
sys.path.append('/app')
sys.path.append('/lib')

from sensors   import *
from actuators import relay_set, relay_get, all_relays_off, oled_show
from ota       import handle_ota_request, list_files
from config    import SLEEP_SECONDS


# ══════════════════════════════════════════════════════════════
# Dashboard HTML
# الصفحة دي بتتبعت للمتصفح لما حد يفتح IP الـ ESP32
# فيها:
#   - كروت السنسورات (حرارة، رطوبة، تربة، خزان)
#   - أزرار الريلاي
#   - زرار Deep Sleep
#   - رفع ملفات OTA
#   - Log للأحداث
# ══════════════════════════════════════════════════════════════
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Smart Farm</title>
<style>
  /* ── Reset ── */
  *{box-sizing:border-box;margin:0;padding:0}
  body{
    font-family:system-ui,sans-serif;
    background:#0f172a;
    color:#e2e8f0;
    min-height:100vh;
  }

  /* ── Header ── */
  header{
    background:#1e293b;
    padding:14px 22px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    border-bottom:1px solid #334155;
  }
  header h1{
    font-size:1.1rem;
    color:#38bdf8;
    font-weight:600;
  }
  /* النقطة الخضرا اللي بتومض = الجهاز online */
  .dot{
    width:8px;height:8px;
    border-radius:50%;
    background:#22c55e;
    animation:pulse 2s infinite;
    display:inline-block;
    margin-right:5px;
  }
  @keyframes pulse{
    0%,100%{opacity:1}
    50%{opacity:.2}
  }

  /* ── Main container ── */
  main{
    padding:16px;
    max-width:820px;
    margin:0 auto;
  }

  /* ── Status bar ── */
  #stat{
    font-size:.72rem;
    color:#475569;
    margin-bottom:14px;
    display:flex;
    gap:14px;
    flex-wrap:wrap;
  }
  #stat b{color:#94a3b8}

  /* ── Sensor cards ── */
  .cards{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(155px,1fr));
    gap:11px;
    margin-bottom:14px;
  }
  .card{
    background:#1e293b;
    border-radius:12px;
    padding:14px 15px;
    border:1px solid #334155;
  }
  .card-lbl{
    font-size:.67rem;
    color:#64748b;
    text-transform:uppercase;
    letter-spacing:.07em;
    margin-bottom:4px;
  }
  .card-val{
    font-size:1.8rem;
    font-weight:700;
    color:#f1f5f9;
    line-height:1.1;
  }
  .card-unit{
    font-size:.78rem;
    color:#475569;
    margin-left:2px;
  }
  /* شريط التقدم تحت كل كارت */
  .bar{
    height:4px;
    background:#0f172a;
    border-radius:2px;
    margin-top:9px;
    overflow:hidden;
  }
  .bar-fill{
    height:100%;
    border-radius:2px;
    transition:width .7s ease;
  }
  .c-amber{background:#f59e0b}  /* حرارة */
  .c-blue {background:#38bdf8}  /* رطوبة / خزان */
  .c-green{background:#22c55e}  /* تربة كويسة */
  .c-red  {background:#ef4444}  /* تربة جافة */

  /* ── Sections ── */
  .sec{
    background:#1e293b;
    border-radius:12px;
    padding:15px 17px;
    border:1px solid #334155;
    margin-bottom:13px;
  }
  .sec-title{
    font-size:.7rem;
    color:#64748b;
    text-transform:uppercase;
    letter-spacing:.07em;
    margin-bottom:12px;
    font-weight:500;
  }

  /* ── Relay buttons ── */
  .relay-grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(118px,1fr));
    gap:7px;
    margin-bottom:11px;
  }
  .rbtn{
    padding:9px 4px;
    border:none;
    border-radius:8px;
    cursor:pointer;
    font-size:.8rem;
    font-weight:600;
    transition:all .18s;
    width:100%;
  }
  /* الريلاي شغّال = أخضر */
  .ron {background:#22c55e;color:#052e16}
  .ron:hover{background:#16a34a}
  /* الريلاي واقف = رمادي غامق */
  .roff{background:#1e3a4a;color:#64748b;border:1px solid #334155}
  .roff:hover{background:#334155}

  /* ── Generic buttons ── */
  .btn{
    padding:8px 15px;
    border:none;
    border-radius:8px;
    cursor:pointer;
    font-weight:600;
    font-size:.8rem;
    transition:background .15s;
  }
  .btn-blue {background:#0ea5e9;color:#fff}
  .btn-blue:hover{background:#0284c7}
  .btn-red  {background:#ef4444;color:#fff}
  .btn-red:hover{background:#dc2626}
  .btn-amber{background:#f59e0b;color:#111}
  .btn-amber:hover{background:#d97706}

  /* ── Row layout ── */
  .row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  .spacer{flex:1}

  /* ── Inputs ── */
  input[type=number],
  input[type=password]{
    background:#0f172a;
    border:1px solid #334155;
    color:#e2e8f0;
    padding:7px 10px;
    border-radius:8px;
    font-size:.8rem;
    outline:none;
  }
  input:focus{border-color:#38bdf8}

  /* ── Event log ── */
  .log{
    background:#0f172a;
    border-radius:8px;
    padding:9px 11px;
    font-family:monospace;
    font-size:.71rem;
    color:#475569;
    height:86px;
    overflow-y:auto;
    border:1px solid #1e293b;
  }
</style>
</head>
<body>

<!-- ══ Header ══════════════════════════════════════════════ -->
<header>
  <h1>Smart Farm IoT</h1>
  <span>
    <span class="dot" id="dot"></span>
    <span id="stxt" style="font-size:.78rem;color:#64748b">connecting...</span>
  </span>
</header>

<main>

  <!-- Status bar: IP / uptime / last update -->
  <div id="stat">
    <span>IP: <b id="s-ip">--</b></span>
    <span>Uptime: <b id="s-up">--</b></span>
    <span>Updated: <b id="s-time">--</b></span>
  </div>

  <!-- ══ Sensor cards ══════════════════════════════════════ -->
  <div class="cards">

    <!-- Temperature -->
    <div class="card">
      <div class="card-lbl">Temperature</div>
      <div class="card-val" id="vt">
        --<span class="card-unit">C</span>
      </div>
      <div class="bar">
        <div class="bar-fill c-amber" id="bt" style="width:0%"></div>
      </div>
    </div>

    <!-- Air Humidity -->
    <div class="card">
      <div class="card-lbl">Air Humidity</div>
      <div class="card-val" id="vh">
        --<span class="card-unit">%</span>
      </div>
      <div class="bar">
        <div class="bar-fill c-blue" id="bh" style="width:0%"></div>
      </div>
    </div>

    <!-- Soil Moisture -->
    <div class="card">
      <div class="card-lbl">Soil Moisture</div>
      <div class="card-val" id="vs">
        --<span class="card-unit">%</span>
      </div>
      <div class="bar">
        <!-- اللون بيتغير: أحمر = جافة ، أخضر = كويسة ، أزرق = رطبة -->
        <div class="bar-fill c-green" id="bs" style="width:0%"></div>
      </div>
    </div>

    <!-- Tank Level -->
    <div class="card">
      <div class="card-lbl">Tank Level</div>
      <div class="card-val" id="vk">
        --<span class="card-unit">%</span>
      </div>
      <div class="bar">
        <div class="bar-fill c-blue" id="bk" style="width:0%"></div>
      </div>
    </div>

  </div>

  <!-- ══ Relay Control ═════════════════════════════════════ -->
  <div class="sec">
    <div class="sec-title">Relay Control</div>
    <div class="relay-grid">
      <button class="rbtn roff" id="r1" onclick="tog(1)">Pump — OFF</button>
      <button class="rbtn roff" id="r2" onclick="tog(2)">Relay 2 — OFF</button>
      <button class="rbtn roff" id="r3" onclick="tog(3)">Relay 3 — OFF</button>
      <button class="rbtn roff" id="r4" onclick="tog(4)">Relay 4 — OFF</button>
    </div>
    <div class="row">
      <button class="btn btn-red"  onclick="allOff()">All OFF</button>
      <div class="spacer"></div>
      <button class="btn btn-blue" onclick="load()">Refresh</button>
    </div>
  </div>

  <!-- ══ Deep Sleep ════════════════════════════════════════ -->
  <div class="sec">
    <div class="sec-title">Deep Sleep</div>
    <div class="row">
      <input type="number" id="ssec"
             value="300" min="10" max="3600"
             style="width:78px">
      <span style="font-size:.8rem;color:#64748b">seconds</span>
      <button class="btn btn-amber" onclick="goSleep()">
        Sleep Now
      </button>
    </div>
  </div>

  <!-- ══ OTA Upload ════════════════════════════════════════ -->
  <div class="sec">
    <div class="sec-title">OTA File Upload</div>
    <div class="row">
      <input type="password" id="opwd"
             placeholder="OTA password"
             style="width:130px">
      <input type="file" id="ofile" accept=".py">
      <button class="btn btn-blue" onclick="doOTA()">Upload</button>
    </div>
    <div id="ota-msg"
         style="margin-top:7px;font-size:.75rem;color:#64748b">
    </div>
  </div>

  <!-- ══ Event Log ═════════════════════════════════════════ -->
  <div class="sec">
    <div class="sec-title">Event Log</div>
    <div class="log" id="log"></div>
  </div>

</main>

<script>
  // ── state ────────────────────────────────────────────────
  // حالة كل ريلاي: false = OFF
  const rs = {1:false, 2:false, 3:false, 4:false};
  // اسم كل ريلاي
  const rn = {1:'Pump', 2:'Relay 2', 3:'Relay 3', 4:'Relay 4'};
  // وقت بدء التشغيل (للـ uptime)
  const boot = Date.now();

  // ── log ─────────────────────────────────────────────────
  // بيضيف سطر جديد في الـ event log
  function lg(msg, ok=true){
    const d = document.getElementById('log');
    const t = new Date().toLocaleTimeString();
    const c = ok ? '#22c55e' : '#ef4444';
    d.innerHTML =
      `<span style="color:#334155">[${t}]</span> ` +
      `<span style="color:${c}">${msg}</span><br>` +
      d.innerHTML;
  }

  // ── load sensor data ─────────────────────────────────────
  // بيطلب بيانات السنسورات من الـ ESP32 كل 10 ثواني
  async function load(){
    try{
      // اطلب البيانات من /api/data
      const res = await fetch('/api/data');
      const d   = await res.json();

      // الجهاز online → النقطة خضرا
      document.getElementById('dot').style.background  = '#22c55e';
      document.getElementById('stxt').textContent       = 'live';
      document.getElementById('s-ip').textContent       = location.hostname;
      document.getElementById('s-time').textContent     = new Date().toLocaleTimeString();

      // Uptime
      const up = Math.floor((Date.now()-boot)/1000);
      document.getElementById('s-up').textContent =
        up < 60 ? up+'s' : Math.floor(up/60)+'m '+(up%60)+'s';

      // ── تحديث قيم الكروت ──
      function sv(id, val, unit){
        document.getElementById(id).innerHTML =
          val !== null && val !== undefined
            ? val + '<span class="card-unit">'+unit+'</span>'
            : '--';
      }
      sv('vt', d.temperature, 'C');
      sv('vh', d.humidity,    '%');
      sv('vs', d.soil_pct,    '%');
      sv('vk', d.tank_pct,    '%');

      // ── تحديث البارات ──
      function sb(id, val, max){
        const el = document.getElementById(id);
        if(el && val !== null) el.style.width = (val/max*100)+'%';
      }
      sb('bt', d.temperature, 50);
      sb('bh', d.humidity,   100);
      sb('bs', d.soil_pct,   100);
      sb('bk', d.tank_pct,   100);

      // لون بار التربة بيتغير حسب الرطوبة
      const bs = document.getElementById('bs');
      if(bs && d.soil_pct !== null){
        bs.className = 'bar-fill ' +
          (d.soil_pct < 30 ? 'c-red'    :   // جافة = أحمر
           d.soil_pct > 70 ? 'c-blue'   :   // رطبة = أزرق
                             'c-green');     // كويسة = أخضر
      }

      // ── تحديث أزرار الريلاي ──
      [1,2,3,4].forEach(n => {
        rs[n] = d['relay_'+n] || false;
        updBtn(n);
      });

      lg(`T:${d.temperature}C  H:${d.humidity}%  Soil:${d.soil_pct}%  Tank:${d.tank_pct}%`);

    } catch(e) {
      // الجهاز offline → النقطة حمرا
      document.getElementById('dot').style.background = '#ef4444';
      document.getElementById('stxt').textContent     = 'offline';
      lg('connection error: '+e, false);
    }
  }

  // ── update relay button ──────────────────────────────────
  // بيغير شكل الزرار حسب حالة الريلاي
  function updBtn(n){
    const b = document.getElementById('r'+n);
    if(!b) return;
    const on = rs[n];
    b.className   = 'rbtn ' + (on ? 'ron' : 'roff');
    b.textContent = rn[n] + ' — ' + (on ? 'ON' : 'OFF');
  }

  // ── toggle relay ─────────────────────────────────────────
  // لما تضغط على زرار الريلاي
  async function tog(n){
    const newState = !rs[n];   // اعكس الحالة
    try{
      await fetch('/api/relay', {
        method : 'POST',
        headers: {'Content-Type':'application/json'},
        body   : JSON.stringify({num:n, state:newState})
      });
      rs[n] = newState;
      updBtn(n);
      lg('Relay '+n+' → '+(newState?'ON':'OFF'));
    } catch(e){ lg('relay error: '+e, false); }
  }

  // ── all off ──────────────────────────────────────────────
  async function allOff(){
    try{
      await fetch('/api/relay', {
        method : 'POST',
        headers: {'Content-Type':'application/json'},
        body   : JSON.stringify({num:0, state:false})
      });
      [1,2,3,4].forEach(n => { rs[n]=false; updBtn(n); });
      lg('All relays OFF');
    } catch(e){ lg('error: '+e, false); }
  }

  // ── deep sleep ───────────────────────────────────────────
  async function goSleep(){
    const s = parseInt(document.getElementById('ssec').value)||300;
    if(!confirm('Sleep for '+s+' seconds?')) return;
    try{
      await fetch('/api/sleep', {
        method : 'POST',
        headers: {'Content-Type':'application/json'},
        body   : JSON.stringify({seconds:s})
      });
      document.getElementById('dot').style.background  = '#f59e0b';
      document.getElementById('stxt').textContent       = 'sleeping...';
      lg('Sleeping '+s+'s — will wake automatically', false);
    } catch(e){}
  }

  // ── OTA upload ───────────────────────────────────────────
  // بيرفع ملف .py للـ ESP32 بدون سلك
  async function doOTA(){
    const pwd  = document.getElementById('opwd').value;
    const file = document.getElementById('ofile').files[0];
    const msg  = document.getElementById('ota-msg');

    if(!file){ alert('Select a .py file first'); return; }

    msg.textContent = 'Uploading '+file.name+'...';
    msg.style.color = '#64748b';

    try{
      const buf = await file.arrayBuffer();   // اقرأ الملف كـ bytes
      const r   = await fetch('/ota', {
        method : 'POST',
        headers: {
          'X-OTA-Password' : pwd,
          'X-OTA-Filename' : file.name,
          'Content-Type'   : 'application/octet-stream'
        },
        body: buf
      });
      const txt = await r.text();
      msg.textContent = (r.ok ? 'OK: ' : 'FAIL: ') + txt;
      msg.style.color = r.ok ? '#22c55e' : '#ef4444';
      lg('OTA '+(r.ok?'ok':'fail')+': '+file.name, r.ok);
    } catch(e){
      msg.textContent = 'Error: '+e;
      msg.style.color = '#ef4444';
    }
  }

  // ── auto refresh ─────────────────────────────────────────
  // اقرأ البيانات فوراً
  load();
  // وكرر كل 10 ثواني
  setInterval(load, 10000);

</script>
</body>
</html>"""


# ══════════════════════════════════════════════════════════════
# Parse HTTP Request
# بتحلل الـ raw bytes اللي جت من المتصفح
# وبتطلع منها: method + path + headers + body
# ══════════════════════════════════════════════════════════════
def _parse(conn):
    raw = b""
    while True:
        chunk = conn.recv(1024)
        if not chunk:
            break
        raw += chunk
        # لو الـ chunk أصغر من buffer = خلص الاستقبال
        if len(chunk) < 1024:
            break
    try:
        # افصل الـ headers عن الـ body
        head, _, body = raw.partition(b"\r\n\r\n")
        lines  = head.decode("utf-8", "ignore").split("\r\n")

        # السطر الأول: "GET / HTTP/1.1"
        parts = lines[0].split(" ")
        if len(parts) < 2:
            return "GET", "/", {}, b""

        method = parts[0]    # GET أو POST
        path   = parts[1]    # / أو /api/data إلخ

        # باقي السطور = headers
        headers = {}
        for line in lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()

        return method, path, headers, body

    except Exception as e:
        print("[WEB] parse error:", e)
        return "GET", "/", {}, b""


# ══════════════════════════════════════════════════════════════
# Send HTTP Response
# بتبني الـ response وتبعتها للمتصفح
# ══════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════
# Handle — معالجة Request واحدة
# بتنادى من run_loop في main.py لكل request
# ══════════════════════════════════════════════════════════════
def handle(conn):
    try:
        method, path, headers, body = _parse(conn)
        print(f"[WEB] {method} {path}")

        # ── GET / → ابعت الـ Dashboard ───────────────────────
        if path == "/" and method == "GET":
            _send(conn, "200 OK", "text/html", HTML)

        # ── GET /api/data → ابعت بيانات السنسورات ─────────────
        elif path == "/api/data" and method == "GET":
            data = read_all()
            data["relay_1"] = relay_get(1)
            data["relay_2"] = relay_get(2)
            data["relay_3"] = relay_get(3)
            data["relay_4"] = relay_get(4)
            oled_show(data)    # حدّث الشاشة كمان
            _send(conn, "200 OK", "application/json", json.dumps(data))

        # ── POST /api/relay → تحكم في الريلاي ─────────────────
        elif path == "/api/relay" and method == "POST":
            req   = json.loads(body.decode())
            num   = req.get("num",   0)
            state = req.get("state", False)
            if num == 0:
                all_relays_off()      # 0 = وقّف الكل
            else:
                relay_set(num, state)
            _send(conn, "200 OK", "application/json", '{"ok":true}')

        # ── POST /api/sleep → Deep Sleep ───────────────────────
        elif path == "/api/sleep" and method == "POST":
            req  = json.loads(body.decode())
            secs = int(req.get("seconds", SLEEP_SECONDS))
            # ابعت الـ response الأول
            _send(conn, "200 OK", "application/json",
                  json.dumps({"ok": True, "seconds": secs}))
            conn.close()
            # ثم نام
            import machine
            all_relays_off()
            machine.deepsleep(secs * 1000)

        # ── POST /ota → رفع ملف ────────────────────────────────
        elif path == "/ota" and method == "POST":
            code, msg = handle_ota_request(headers, body)
            _send(conn,
                  f"{code} {'OK' if code==200 else 'Error'}",
                  "text/plain", msg)

        # ── GET /api/files → قائمة الملفات ─────────────────────
        elif path == "/api/files" and method == "GET":
            _send(conn, "200 OK", "application/json",
                  json.dumps(list_files()))

        # ── 404 ────────────────────────────────────────────────
        else:
            _send(conn, "404 Not Found", "text/plain", "not found")

    except Exception as e:
        print("[WEB] handler error:", e)

    finally:
        conn.close()      # دايماً اقفل الـ connection
        gc.collect()      # امسح الـ RAM
