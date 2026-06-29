#!/usr/bin/env bash

# Ensure running as root
if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run this script using sudo."
  exit 1
fi

echo "===================================================="
echo "       WLAN-SOC Managed Service Installer"
echo "===================================================="

# 1. Detect and Ask for Interface
DEFAULT_IFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
if [ -z "$DEFAULT_IFACE" ]; then
    DEFAULT_IFACE="eth0"
fi

read -p "[?] Enter network interface to sniff [$DEFAULT_IFACE]: " USER_IFACE
INTERFACE=${USER_IFACE:-$DEFAULT_IFACE}

read -p "[?] Enter Primary API Port [5000]: " USER_PORT
PORT=${USER_PORT:-5000}
BACKUP_PORT=$((PORT + 1))

# 2. Install System Dependencies
echo "[*] Synchronizing environment mirrors & installing binaries..."
apt-get update -y && apt-get install -y apache2 suricata python3 python3-pip python3-flask python3-flask-cors curl jq

# 3. Create Configuration Ecosystem
echo "[*] Writing static asset directory paths..."
mkdir -p /etc/wlan-soc
mkdir -p /var/log/suricata

cat <<EOF > /etc/wlan-soc/config.json
{
  "interface": "$INTERFACE",
  "port": $PORT,
  "backup_port": $BACKUP_PORT
}
EOF

# 4. Stage Orchestrator Files
echo "[*] Packaging core application engines..."
cp soc_orchestrator.py /etc/wlan-soc/soc_orchestrator.py
chmod +x /etc/wlan-soc/soc_orchestrator.py

# 5. Build Apache Deployment Structure
echo "[*] Setting web root environments..."
mkdir -p /var/www/html/wlan-soc

# Production-ready index page that connects to your endpoints
cat <<EOF > /var/www/html/wlan-soc/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WLAN-SOC Dashboard</title>
    <style>body { font-family: monospace; background: #111; color: #0f0; padding: 20px; }</style>
</head>
<body>
  <h2>[ WLAN-SOC REAL-TIME ALERTS BOARD ]</h2>
  <hr style="border-color: #0f0;">
  <pre id="logs">Waiting for background service startup authorization pipeline...</pre>
  
  <script>
    function fetchTelemetry() {
        fetch('/api/logs')
          .then(res => res.json())
          .then(data => {
              document.getElementById('logs').innerText = JSON.stringify(data, null, 2);
          })
          .catch(err => {
              document.getElementById('logs').innerText = "System Idle or API Service is Stopped.";
          });
    }
    setInterval(fetchTelemetry, 3000);
    fetchTelemetry();
  </script>
</body>
</html>
EOF

chown -R www-data:www-data /var/www/html/wlan-soc
systemctl restart apache2

# 6. Generate Unit Service Definitions
echo "[*] Registering systemd execution models..."
cat <<EOF > /etc/systemd/system/wlan-soc.service
[Unit]
Description=WLAN-SOC Sniffing & API Orchestrator Daemon
After=network.target apache2.service

[Service]
Type=simple
User=root
WorkingDirectory=/etc/wlan-soc
ExecStart=/usr/bin/python3 /etc/wlan-soc/soc_orchestrator.py
ExecStop=/usr/bin/python3 -c "import subprocess; subprocess.run(['pkill', '-f', 'ngrok']); subprocess.run(['pkill', '-f', 'suricata'])"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 7. Complete Reload Without Active Run Commands
systemctl daemon-reload

echo "===================================================="
echo "[+] Target installation processes completed successfully."
echo "[-] STATUS: Service is registered but remains DISABLED/STOPPED."
echo "===================================================="
echo ""
echo "To interact with your newly structured service, execute:"
echo "  -> Start Service:    sudo systemctl start wlan-soc"
echo "  -> Enable Boot Start: sudo systemctl enable wlan-soc"
echo "  -> Check Status:      sudo systemctl status wlan-soc"
echo ""
echo "===================================================="
