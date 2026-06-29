# 📡 Wireless Traffic Analysis and Visualization (WLAN-SOC)

A dedicated security architecture lab establishing passive wireless network traffic inspection via custom Network Intrusion Detection Systems (NIDS) and visual data analysis tooling. 

This project orchestrates continuous packet processing, filters signatures for malicious activity via customized rule definitions, and streams logs seamlessly to an executive Web Dashboard and a Power BI analytics workflow.

---

## Technical Architecture Overview

| Layer | Component & Technology |
| :--- | :--- |
| **Ingestion Core** | Suricata IDS/IPS Engine *(Passive Monitoring Configuration)* |
| **Automation Backend** | Python 3 *(Flask, Subprocess Multi-threading Execution)* |
| **Exposition Layer** | Ngrok HTTP Secure Tunneling Protocols |
| **Analytics Engine** | Power BI Business Intelligence Desktop & Custom HTML5/JS Dashboard |

---

## Prerequisites & Dependencies

> ⚠️ **Important Requirement:** Ensure your Linux distribution has a wireless card capable of entering **monitor/promiscuous mode**.

```bash
# Update local packages
sudo apt update && sudo apt upgrade -y

# Install Suricata core engine
sudo apt install suricata -y

# Install backend python execution environments
pip install flask flask-cors
```

---
## Installation & Setup Instructions
1. Provision Custom Suricata Rules
Add your internal specific network threat parameters inside your local rules directory:
```bash
sudo nano /etc/suricata/rules/local.rules
```

Example Rule Sample:
```bash
alert tcp any any -> any any (msg:"POTENTIAL INSIDER RECONNAISSANCE ACTIVITY"; sid:1000001; rev:1;)
```

2. Deployment Execution
To guarantee that the monitoring script stays alive even if your terminal session disconnects, run the orchestrator tool as a background daemon process using nohup:
```bash
sudo nohup python3 soc_orchestrator.py wlan0 > soc_output.log 2>&1 &
```


## Quick-Copy Execution Guide
3. Initialize Web UI View
To view live alerts, open the custom index.html file locally or update the JavaScript connection string with your active Ngrok endpoint URL to share live telemetry streams with distributed web nodes.
```bash
# Step 1: Verify your active wireless interface label
ip link show

# Step 2: Execute the automated telemetry hub (Foreground Debug mode)
sudo python3 soc_orchestrator.py <your_interface_name>

# Step 3: View live system outputs
tail -f suricata_logs/eve.json
```
