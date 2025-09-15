import os
import subprocess
import threading
import time
import pyshark 

def capture_wireless_packets(interface, duration, output_pcap):
    print(f"Starting wireless capture on {interface} for {duration} seconds...")
    capture = pyshark.LiveCapture(interface=interface, output_file=output_pcap)

    def stop_capture_after_delay():
        time.sleep(duration)
        capture.close()  # Stops the capture

    stopper = threading.Thread(target=stop_capture_after_delay)
    stopper.start()

    capture.sniff_continuously()
    print("Packet capture finished.")

def generate_malicious_traffic(test_url):
    print(f"Generating malicious traffic by visiting {test_url} ...")
    subprocess.run(["curl", "-s", test_url])
    print("Malicious traffic generated.")

def run_suricata_on_pcap(pcap_file, suricata_output_dir):
    print(f"Running Suricata on {pcap_file} ...")

    # Check if Suricata is installed
    suricata_path = subprocess.run(["which", "suricata"], capture_output=True, text=True).stdout.strip()
    if not suricata_path:
        print("Error: Suricata is not installed or not in PATH.")
        print("Install it with: sudo apt install suricata")
        return

    # Make sure output directory exists
    os.makedirs(suricata_output_dir, exist_ok=True)

    suricata_command = [
        suricata_path,
        "-r", pcap_file,
        "-l", suricata_output_dir
    ]
    subprocess.run(suricata_command)
    print("Suricata analysis complete.")

def move_log_to_web_root(suricata_output_dir, web_root):
    eve_json = os.path.join(suricata_output_dir, "eve.json")
    web_log = os.path.join(web_root, "eve.json")

    if not os.path.exists(web_root):
        try:
            os.makedirs(web_root)
        except PermissionError:
            print(f"Permission denied: Cannot create {web_root}. Try running with sudo.")
            return

    if os.path.exists(eve_json):
        subprocess.run(["cp", eve_json, web_log])
        print(f"eve.json moved to {web_log}")
    else:
        print("eve.json not found!")

def start_apache_ngrok():
    print("Starting Apache2 ...")
    subprocess.run(["sudo", "systemctl", "restart", "apache2"])
    print("Starting ngrok on port 80 ...")
    try:
        subprocess.Popen(["ngrok", "http", "80"])
    except FileNotFoundError:
        print("Error: ngrok not found. Please install ngrok and add to PATH.")
    print("Apache2 and ngrok started.")

if __name__ == "__main__":
    interface = input("Enter wireless interface name: ")
    duration = int(input("Enter capture duration (seconds): "))
    output_pcap = "captured_traffic.pcap"
    suricata_output_dir = "./suricata_logs"
    test_url = "https://testmynids.org/uid/index.html"  # Test site for IDS
    web_root = "/var/www/html/"

    # Step 1: Capture wireless traffic
    capture_wireless_packets(interface, duration, output_pcap)

    # Step 2: Generate malicious traffic
    generate_malicious_traffic(test_url)

    # Step 3: Use Suricata to analyze packets
    run_suricata_on_pcap(output_pcap, suricata_output_dir)

    # Step 4: Move eve.json to web root
    move_log_to_web_root(suricata_output_dir, web_root)

    # Step 5: Start Apache and ngrok
    start_apache_ngrok()

    print("Workflow complete. Access eve.json via Apache/ngrok.")
