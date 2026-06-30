#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import time
from flask import Flask, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allows your HTML frontend to fetch logs seamlessly

LOG_DIR = "./suricata_logs"
EVE_JSON = os.path.join(LOG_DIR, "eve.json")

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Serves the last 100 security alerts in JSON format."""
    if not os.path.exists(EVE_JSON):
        return jsonify({"error": "No logs generated yet"}), 404
    
    alerts = []
    try:
        with open(EVE_JSON, 'r') as f:
            for line in f:
                import json
                try:
                    log = json.loads(line)
                    if log.get("event_type") == "alert":
                        alerts.append({
                            "timestamp": log.get("timestamp"),
                            "signature": log.get("alert", {}).get("signature"),
                            "category": log.get("alert", {}).get("category"),
                            "severity": log.get("alert", {}).get("severity"),
                            "src_ip": log.get("src_ip"),
                            "dest_ip": log.get("dest_ip"),
                            "proto": log.get("proto")
                        })
                except json.JSONDecodeError:
                    continue
        return jsonify(alerts[-100:]) # Return latest 100 alerts
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_suricata_live(interface):
    """Launches Suricata in continuous live sniffing mode."""
    print(f"[*] Starting Suricata live engine on interface: {interface}")
    os.makedirs(LOG_DIR, exist_ok=True)
    
    cmd = [
        "sudo", "suricata",
        "-i", interface,
        "-l", LOG_DIR,
        "-k", "none" # Disable checksum verification for home labs
    ]
    subprocess.run(cmd)

def start_ngrok():
    """Starts Ngrok tunnel over port 5000 (Flask API)."""
    print("[*] Launching Ngrok tunnel over port 5000...")
    try:
        # Tunneling Flask API instead of static apache for true dynamic interaction
        subprocess.Popen(["ngrok", "http", "5000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("[-] Warning: Ngrok binary not found in PATH.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] Critical Error: This script must be run with 'sudo' privileges.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("[-] Usage: sudo python3 soc_orchestrator.py <interface>")
        sys.exit(1)
        
    interface_name = sys.argv[1]
    
    # 1. Start Suricata engine in a background thread
    suricata_thread = threading.Thread(target=run_suricata_live, args=(interface_name,), daemon=True)
    suricata_thread.start()
    
    # 2. Wait briefly for logs initialization
    time.sleep(2)
    
    # 3. Expose the environment globally via Ngrok
    start_ngrok()
    
    # 4. Spin up the Flask API Server natively (Blocks main thread natively, keeps app alive)
    print("[*] Starting Web View API on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
