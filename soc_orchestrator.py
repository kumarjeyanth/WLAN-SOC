#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import threading
import time
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

# Setup working base locations dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# FIXED: Changed from "Static" to lowercase "static" to match GitHub/Linux standards
STATIC_DIR = os.path.join(BASE_DIR, "static")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)

LOG_DIR = "/var/log/suricata"
EVE_JSON = os.path.join(LOG_DIR, "eve.json")
SURICATA_YAML = "/etc/suricata/suricata.yaml"

# Default fallbacks if config reading completely fails
CONFIG = {"interface": "wlan0", "port": 2000}

def load_config():
    global CONFIG
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                loaded_config = json.load(f)
                if "interface" in loaded_config and "port" in loaded_config:
                    CONFIG = loaded_config
                    print(f"[+] Configuration parsed -> Interface: {CONFIG['interface']}, Port: {CONFIG['port']}")
                else:
                    print("[-] config.json missing keys. Using defaults.")
        except Exception as e:
            print(f"[-] Config loading problem encountered: {e}")
    else:
        print(f"[-] Critical: {CONFIG_PATH} not found! Creating defaults.")
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(CONFIG, f, indent=4)

@app.route('/')
def serve_dashboard():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/api/logs', methods=['GET'])
def get_logs():
    if not os.path.exists(EVE_JSON):
        return jsonify({"error": f"Log target path missing at {EVE_JSON}"}), 404
    
    alerts = []
    try:
        with open(EVE_JSON, 'r') as f:
            for line in f:
                try:
                    log = json.loads(line)
                    if log.get("event_type") == "alert":
                        alerts.append({
                            "timestamp": log.get("timestamp"),
                            "signature": log.get("alert", {}).get("signature"),
                            "category": log.get("alert", {}).get("category"),
                            "severity": log.get("alert", {}).get("severity"),
                            "src_ip": log.get("src_ip", "N/A"),
                            "dest_ip": log.get("dest_ip", "N/A"),
                            "proto": log.get("proto", "N/A")
                        })
                except json.JSONDecodeError:
                    continue
        # Return last 100 alerts, newest first
        return jsonify(list(reversed(alerts[-100:])))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_suricata_live(interface):
    print(f"[*] Activating Suricata Engine on interface: {interface}")
    os.makedirs(LOG_DIR, exist_ok=True)
    
    cmd = ["suricata", "-c", SURICATA_YAML, "-i", interface, "-l", LOG_DIR, "-k", "none"]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(3)
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"[-] Suricata failed to stay alive. Code: {process.returncode}")
            print(f"[-] Suricata Error Log:\n{stderr}")
        else:
            print(f"[+] Suricata engine successfully spawned with PID {process.pid} on {interface}!")
    except Exception as e:
        print(f"[-] Failed to execute Suricata command: {e}")

def start_ngrok(port):
    """Starts ngrok in the background and prints the live public URL explicitly."""
    time.sleep(3) 
    print(f"[*] Initializing Ngrok tunnel exposing HTTP port {port}...")
    try:
        # Kill any lingering native instances first
        subprocess.run(["pkill", "-f", "ngrok"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Explicit configuration tracking to use system-wide configurations if available
        subprocess.Popen(["ngrok", "http", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Check for URL registration up to 10 times to provide more leeway
        for attempt in range(10):
            time.sleep(2)
            try:
                res = subprocess.run(["curl", "-s", "http://127.0.0.1:4040/api/tunnels"], capture_output=True, text=True)
                tunnel_data = json.loads(res.stdout)
                if 'tunnels' in tunnel_data and len(tunnel_data['tunnels']) > 0:
                    public_url = tunnel_data['tunnels'][0]['public_url']
                    print("\n====================================================")
                    print(f"[+] NGROK PUBLIC ACCESS URL: {public_url}")
                    print("====================================================\n")
                    return
            except Exception:
                continue
        print("[-] Ngrok API endpoints initialized but tunnel URL mapping is still pending. Verify your authtoken!")
    except Exception as e:
        print(f"[-] Failed to automatically establish ngrok tunnel: {e}")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] Privileged execution parameters missing. Please execute via sudo.")
        sys.exit(1)

    load_config()
    
    suricata_thread = threading.Thread(
        target=run_suricata_live, 
        args=(CONFIG.get("interface"),), 
        daemon=True
    )
    suricata_thread.start()
    
    target_port = CONFIG.get("port")
    
    ngrok_thread = threading.Thread(target=start_ngrok, args=(target_port,), daemon=True)
    ngrok_thread.start()

    print(f"[+] Dashboard UI and endpoints running on: http://0.0.0.0:{target_port}")
    app.run(host='0.0.0.0', port=target_port, debug=False, threaded=True)
