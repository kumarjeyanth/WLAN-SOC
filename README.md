# Wireless-Traffic-Analysis---Project
Developed Python-based (Scapy, Pandas, Matplotlib) traffic analysis tool with Suricata , Power BI visualization, and secure log deployment via Apache & Ngrok

#Requirements:
Python packages:
> OS
> subprocess
> threading
> time
> pyshark
Install those packages by using "pip install <package-name>"


service setup:
> sudo apt install apache2
  This above install the apache web service on your Linux system,

> curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \                  
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update \
  && sudo apt install ngrok
  This above install ngrok service and add your AuthToken for "ngrok config add-authtoken <token>"

> Setup Power BI graphic visualisation icons and import the downloaded log file into it, This is the dashboard for review logs...



#Installation on Linx:
> Using git clone to install the code
