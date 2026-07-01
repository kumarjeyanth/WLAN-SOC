<div align="center">

# 📡 WLAN-SOC

### Wireless Traffic Analysis & Visualization Platform

*A lightweight, automated Security Operations Center (SOC) framework for passive wireless network traffic inspection.*

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white)
![Suricata](https://img.shields.io/badge/Suricata-IDS-D6002A?style=for-the-badge&logo=suricata&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-Dashboard-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Ngrok](https://img.shields.io/badge/Ngrok-Tunnel-1F1E37?style=for-the-badge&logo=ngrok&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-Only-FCC624?style=for-the-badge&logo=linux&logoColor=black)

</div>

---

## 📖 About The Project

WLAN-SOC pairs the **Suricata NIDS Engine** with a multi-threaded **Python Flask backend** to parse network telemetry and stream live security anomalies to a modern **Tailwind CSS** web dashboard — accessible locally or remotely via a secure Ngrok tunnel.

---

## 🛠️ System Architecture

```text
                                   [ Wireless Client ]
                                           │
                                      ▼ (Packets)
                    ┌──────────────── wlan0 / eth0 ────────────────┐
                    │       Suricata IDS Engine (Sniffing)         │
                    └─────────────────────┬────────────────────────┘
                                          │ Writes alerts to
                                          ▼
                    ┌─────────────── eve.json ─────────────────────┐
                    │       Flask API Orchestrator Backend         │
                    └─────────────────────┬────────────────────────┘
                                          ├─► Serves Web UI Dashboard (Port: 2000)
                                          └─► Spawns Ngrok Safe Tunnel
                                          │
                                          ▼
                                 [ Remote Public URL ]
```

### 🗺️ Operational Component Breakdown

| Layer | Component | Technology | Description |
| :---: | :--- | :--- | :--- |
| 📥 **Ingestion** | IDS Engine | `Suricata` | Sniffs raw packets on the configured interface and outputs JSON alert telemetry. |
| ⚙️ **Backend** | Orchestrator | `Python 3` + `Flask` | Parses engine logs, manages core processes, and exposes a REST API. |
| 🌐 **Exposition** | Secure Edge | `Ngrok Agent` | Automatically exposes the local dashboard port safely to the internet. |
| 📊 **Frontend** | Dashboard | `HTML5` / `JS` / `Tailwind` | Client-side engine that pulls real-time analytics using live API polling. |

---

## 📋 Pre-Requisites & Requirements

Before deploying, ensure your host platform meets the following foundational environment metrics.

### 🖥️ Base Environment

| Requirement | Details |
| :--- | :--- |
| **Operating System** | Linux (Kali Linux, Ubuntu, or Debian-based distributions) |
| **Privileges** | Full `sudo` root execution rights |
| **Hardware** | A network interface capable of promiscuous / monitor mode (`wlan0`, `eth0`) |

<br>

### 🐍 Python Dependencies

All required Python packages are listed in **[`requirements.txt`](./requirements.txt)**:

```text
Flask==3.0.3
Flask-Cors==4.0.1
```

> [!CAUTION]
> **Critical Service Requirement**
>
> Because the background system daemon (`systemd`) executes the orchestrator script under the **global root user space**, all dependencies must be installed **globally** (not inside a virtual environment).
>
> Run the command below before triggering the installer to prevent immediate `ModuleNotFoundError` crashes:

```bash
sudo pip3 install -r requirements.txt --break-system-packages
```

---

## 🚀 Step-by-Step Deployment Guide

Follow these configuration steps in **exact sequential order** to spin up the automated monitoring cluster.

### Step 1️⃣ — Add Your Ngrok Authentication Token

Install and retrieve your custom Auth Token from your personal Ngrok Dashboard.

Authenticate your local tracking agent:

```bash
sudo ngrok config add-authtoken <YOUR_NGROK_AUTH_TOKEN>
```

<br>

### Step 2️⃣ — Deploy Custom Suricata Configuration

This repository includes a customized `suricata.yaml` file, pre-optimized specifically for local wireless network log extraction and interface handling.

```bash
sudo cp suricata/suricata.yaml /etc/suricata/suricata.yaml
```

**Eve-Log JSON Stream Enabled** — Explicitly ensures `eve.json` output targets are toggled on with alert structures active, so the Flask parser can query events.

**Targeted Local Rule Paths** — Maps directly to your custom `/etc/suricata/rules/local.rules` asset as the absolute tracking priority, stripping away heavy public lists that slow down initial testing loops.

<br>

### Step 3️⃣ — Implement Testing Signatures (`local.rules`)

This repository provides a tailored `local.rules` file containing optimized detection rules to verify that the end-to-end telemetry pipeline is working smoothly.

Ensure the core rules storage directory tree exists on your host:

```bash
sudo mkdir -p /etc/suricata/rules
```

Move the rule configuration files from your repository workspace to Suricata's rule matrix:

```bash
sudo cp suricata/local.rules /etc/suricata/rules/local.rules
```

> [!TIP]
> The rules are custom-built using specialized `sid` values ranging from `1,000,001` to `1,000,004` to prevent logic or database collisions with default public signatures.
>
> They utilize the `classtype:not-suspicious;` classification tag to safely trigger frontend counters without generating false system security flags during initial setups.

If you wish to view or manually append custom operational rules to this engine layer later, edit the live path directly:

```bash
sudo nano /etc/suricata/rules/local.rules
```

<br>

### Step 4️⃣ — Fine-Tune Web Dashboard Ports

The ecosystem tracks configuration variables inside a centralized data file under the `config/` directory to manage system interface bindings.

Open `config/config.json` and adjust the variables to line up with your local hardware targets:

```json
{
    "interface": "wlan0",
    "port": 2000,
    "backup_port": 2001
}
```

> [!TIP]
> If running an Ethernet-based monitoring architecture instead of an over-the-air asset, update the `"interface"` entry string from `wlan0` to `eth0`.
>
> To bind your dashboard tracking console onto a separate network layer, adjust the target `"port"` integer to any preferred alternative (e.g., `1212`).

<br>

### Step 5️⃣ — Execute the Automated System Installer

The `install.sh` sequence installs missing software packages, automatically kills off conflicting web servers (such as native Apache2 instances) to keep port access clear, and safely mounts the background monitoring engine profile.

Grant the script executable permissions and kick off the automated deployment:

```bash
chmod +x install.sh

sudo ./install.sh
```

---

## 🚦 Managing the Framework Service

The cluster runs seamlessly inside a single background Systemd unit profile named **`wlan-soc.service`**.

<br>

### 🟢 Start the Service Core

```bash
sudo systemctl start wlan-soc
```

<br>

### 🔄 Enable Automatic Boot-Time Persistence

```bash
sudo systemctl enable wlan-soc
```

<br>

### 🌐 Retrieving Active Access Endpoints

> [!IMPORTANT]
> When evaluating system initialization metrics, pay close attention to the terminal console printouts.
>
> The orchestrator script dynamically pulls your local listener socket and your secure public Ngrok proxy tunnel URL directly into the status block:

```bash
sudo systemctl status wlan-soc
```

> [!TIP]
> **Active Network Gateways**
> - 🖥️ **Local Console:** `http://localhost:2000`
> - 🌍 **Public Ngrok Access:** `https://xxxx-xx-xx-xx.ngrok-free.app`

<br>

### 🪵 Tail the Live Output Telemetry Stream

Keep a live console session running to monitor telemetry traffic passing through the analytics engine processing loops:

```bash
sudo journalctl -u wlan-soc -f
```

<br>

### 🔒 Safe Service Termination

> [!WARNING]
> Stopping the service via Systemd triggers an automated teardown script sequence.
>
> This operation instantly drops the open Ngrok socket connection, stops background sniffing tasks, and frees system network ports to prevent interface locks.

To halt execution processing lines safely, run:

```bash
sudo systemctl stop wlan-soc
```

---

<div align="center">

## 🖤 Crafted By

```
   ██████╗  █████╗ ██████╗ ██╗  ██╗ ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗
   ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝
██║  ██║███████║██████╔╝█████╔╝ ██║  ███╗███████║██║   ██║███████╗   ██║
██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║   ██║██╔══██║██║   ██║╚════██║   ██║
██████╔╝██║  ██║██║  ██║██║  ██╗╚██████╔╝██║  ██║╚██████╔╝███████║   ██║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝
```

**⭐ If this project helped you, consider giving it a star! ⭐**

</div>
