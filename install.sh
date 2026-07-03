#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]; then
  echo "[-] Script requires elevated access context. Please issue command with sudo."
  exit 1
fi

PROJECT_DIR=$(pwd)
CONFIG_FILE="$PROJECT_DIR/config/config.json"

clear
echo "========================================================================="
echo "  _      _ _       _   _       _  _____  ____   _____ "
echo " | |    | | |     | \ | |     | |/ ____|/ __ \ / ____|"
echo " | |    /\  | |     |  \| |____| | (___ | |  | | |     "
echo " | |   /  \ | |     | . \` |____| |\___ \| |  | | |     "
echo " | |__/ /\ \| |____ | |\  |    | |____) | |__| | |____ "
echo " |___/_/  \_\______|____\_|    |_|_____/ \____/ \_____|"
echo "                                                       "
echo "        WLAN-SOC Automated Managed Service Installer"
echo "========================================================================="

# Validate existing configuration parameters before system setup
if [ ! -f "$CONFIG_FILE" ]; then
    echo "[-] Configuration not found at $CONFIG_FILE. Creating default fallback layout."
    mkdir -p "$PROJECT_DIR/config"
    cat <<EOF > "$CONFIG_FILE"
{
    "interface": "wlan0",
    "port": 2000,
    "backup_port": 2001
}
EOF
fi

# Ensure jq dependency is locally present before config serialization parsing
if ! command -v jq &> /dev/null; then
    echo "[*] Bootstrapping jq engine tracking utilities..."
    apt-get update -y && apt-get install -y jq
fi

INTERFACE=$(jq -r '.interface' "$CONFIG_FILE")
PORT=$(jq -r '.port' "$CONFIG_FILE")

echo "[+] Target environment parsed: Interface [$INTERFACE] on HTTP Port [$PORT]"
echo "[*] Handling dependency requirements..."

apt-get update -y && apt-get install -y suricata python3 python3-pip python3-flask python3-flask-cors curl lsb-release

# Download and install ngrok handling dynamic platform names safely to prevent deb-conflicts
if ! command -v ngrok &> /dev/null; then
    echo "[*] Installing official ngrok binary..."
    rm -f /etc/apt/sources.list.d/ngrok.list
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
    
    # FIXED: Replaced hardcoded 'buster' with dynamically pulled OS_CODENAME variable
    OS_CODENAME=$(lsb_release -cs)
    echo "deb [signed-by=/etc/apt/trusted.gpg.d/ngrok.asc] https://ngrok-agent.s3.amazonaws.com ${OS_CODENAME} main" | tee /etc/apt/sources.list.d/ngrok.list
    
    apt-get update -y && apt-get install ngrok -y
fi

if systemctl is-active --quiet apache2; then
    echo "[*] Disabling conflicting Apache structural endpoints..."
    systemctl stop apache2
    systemctl disable apache2
fi

echo "[*] Generating local context workspace components..."
# FIXED: Changed from uppercase "Static" to lowercase "static"
mkdir -p "$PROJECT_DIR/static"
mkdir -p "/var/log/suricata"

chmod +x "$PROJECT_DIR/soc_orchestrator.py"

echo "[*] Building active daemon runtime environment configs..."
cat <<EOF > /etc/systemd/system/wlan-soc.service
[Unit]
Description=WLAN-SOC Sniffing & API Orchestrator Daemon
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/soc_orchestrator.py
ExecStop=/usr/bin/python3 -c "import subprocess; subprocess.run(['pkill', '-f', 'suricata']); subprocess.run(['pkill', '-f', 'ngrok'])"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable wlan-soc
systemctl restart wlan-soc

echo "===================================================="
echo "[+] Deployment finalized successfully."
echo "[+] Local Dashboard View: http://127.0.0.1:$PORT"
echo "[*] Check public URL via: sudo systemctl status wlan-soc"
echo "===================================================="
