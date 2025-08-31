# WMATA-PIDS
Brian Leschke 2025

## **Overview**

An enhanced and unofficial version of the New and Improved WMATA Station PIDS screens. Created with ChatGPT :)

This display has the ability to do the following:
* Metro Train arrival times for either:
    * Single (1) Platform
    * Both (2) Platforms
* Line Circle will pulse when train is Boarding (BRD) or Arriving (ARR)
* Display Metro Rail Alerts
* Display line analytics (optional)
* Update API Key from developer.wmata.com
* Display in Full Screen (optional)
* Display in Kiosk/TV Mode (optional) - Toggle with "T" key

### **Prerequisities**

You will need:

1. Python 3.x
2. Linux
3. downloaded git file 

### **Installation**

```
sudo apt update && sudo apt install -y python3-venv python3-pip nginx
cd /opt/wmata-pids && python3 -m venv .venv
source .venv/bin/activate
pip install flask requests gunicorn
printf 'WMATA_API_KEY="%s"\n' "YOUR_KEY" | sudo tee /opt/wmata-pids/.env (optional - key can be set in webui)
```

Service - systemd:

```
sudo tee /etc/systemd/system/wmata-pids.service >/dev/null <<'EOF'
[Unit]
Description=WMATA PIDS (Gunicorn)
After=network-online.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/wmata-pids
Environment="PYTHONUNBUFFERED=1"
ExecStart=/opt/wmata-pids/.venv/bin/gunicorn -w 3 -b 127.0.0.1:5001 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

Enable and Start:

```
sudo systemctl daemon-reload
sudo systemctl enable wmata-pids
sudo systemctl start wmata-pids
sudo systemctl status wmata-pids
```      

### **Recognition and Credit**
I would like to recognize ChatGPT and OpenAI for generating the code. 
