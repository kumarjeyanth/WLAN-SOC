# 📡 Wireless Traffic Analysis and Visualization (WLAN-SOC)

A security architecture lab for passive wireless network traffic inspection using a custom Network Intrusion Detection System (NIDS) and a visual data web dashboard.

This framework processes live network packets, filters signatures for malicious activity via custom rules, and streams alert logs to a web dashboard or Power BI analytics workflow.

---

## 🛠️ Technical Architecture

| Layer | Component & Technology | Description |
| :--- | :--- | :--- |
| **Ingestion** | Suricata IDS/IPS Engine | Sniffs raw packets passively and dumps alert telemetry to `eve.json`. |
| **Backend** | Python 3 (Flask + Systemd) | Multi-threaded engine that serves the log data via a local REST API. |
| **Exposition** | Ngrok Secure Tunneling | Securely exposes the local API (`5000`) or Web Console (`80`) to the internet. |
| **Frontend** | Apache2 + HTML5/JS | Apache serves static dashboard assets; JS pulls logs via live API polling. |

---

## 📋 Step-by-Step Deployment Guide

### Step 1: Install & Authenticate Ngrok
1. Download and install the Ngrok agent:
   ```bash
   curl -s [https://ngrok-agent.s3.amazonaws.com/ngrok.asc](https://ngrok-agent.s3.amazonaws.com/ngrok.asc)
   | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
   echo "deb [https://ngrok-agent.s3.amazonaws.com](https://ngrok-agent.s3.amazonaws.com) buster main" \
   | sudo tee /etc/apt/sources.list.d/ngrok.list
   sudo apt update && sudo apt install ngrok -y
   
1. Link your Ngrok account token (Retrieve this from your [Ngrok Dashboard](https://dashboard.ngrok.com)):

```bash
ngrok config add-authtoken <YOUR_AUTHTOKEN>
```

---
---

## Step 2: Configure Suricata Parameters
1. Find your target network interface name (e.g., wlan0, mon0, eth0):

```bash
ip link show
```
⚠️ Note: Ensure your network card is switched to monitor/promiscuous mode if analyzing raw wireless traffic.

2. Open your local rules file:
```bash
sudo nano /etc/suricata/rules/local.rules
```
3. Add your custom threat signatures. Example:
```bash
alert tcp any any -> any any (msg:"POTENTIAL INSIDER RECONNAISSANCE ACTIVITY"; sid:1000001; rev:1;)
```
4. Confirm that /etc/suricata/suricata.yaml includes a pointer to your local.rules file.

Step 3: Run the Automated Installer

The install.sh script installs system dependencies, configures directory pathways, links Apache components, and registers the background systemd service without auto-starting it.
```bash
chmod +x install.sh
sudo ./install.sh
```
Installer Prompts: Provide your target interface (or press Enter for default) and your primary binding API port (default: 5000).

Step 4: Deploy Frontend Web Assets

1. Copy your visual dashboard frontend files from your project's static/ folder into Apache's server directory:
```bash
sudo cp -r static/* /var/www/html/wlan-soc/
sudo chown -R www-data:www-data /var/www/html/wlan-soc/
```

2. Verify your frontend JavaScript file (app.js or script tags) accurately points to your local/public backend API route:
JavaScript
```bash 
fetch('http://localhost:5000/api/logs')
  .then(response => response.json())
  .then(data => renderLogsToDashboard(data));
```


Step 5: Start & Manage the Service (Systemd)

1. The installer registers the framework but leaves it stopped. Use the following standard commands to manage it:

Start the Monitoring Framework Daemon:
```bash
sudo systemctl start wlan-soc
```
2. Enable Boot-time persistence execution:
```bash
sudo systemctl enable wlan-soc
```

3. Verify active status metrics:
```bash
sudo systemctl status wlan-soc
```

4. Tail stream system telemetry & execution output:
```bash
    sudo journalctl -u wlan-soc -f
```

🔒 Security Lockdown & Service Termination

When you stop the service via Systemd, an integrated ExecStop routine automatically executes a structural cleanup. It shuts down background processes, terminates open Ngrok connections, and clears active socket ports instantly.

To cleanly kill all associated sniffing engines and free up ports, run:
```bash
sudo systemctl stop wlan-soc
```
