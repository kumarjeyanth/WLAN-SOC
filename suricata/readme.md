wlan-soc

A network security monitoring and intrusion detection system designed to protect wireless local area networks (WLAN) using a Security Operations Center (SOC) framework powered by Suricata.
🚀 Rule Management & Configurations

Suricata relies on predefined rule signatures to detect threats, anomalies, and malicious behavior across the wireless network. You can manage rules using the options below:
1. Using Official Default Rules

To start with the highly stable, pre-packaged rule sets provided by the official Suricata community, you can use the default installation ruleset.
2. Fetching the Latest Updates

Threat signatures evolve constantly. To fetch and apply the latest emerging threat definitions, execute the built-in update utility in your terminal:

```
sudo suricata-update
```

3. Creating Custom Rules

If you need to deploy specific behavior tracking or tailor alerts for your unique network architecture, write your custom signatures inside the local rules file.

    File Location: 
    ```
       /etc/suricata/rules/local.rules
    ```
    
    Configuration: Ensure your suricata.yaml config file points to this path under the rule-files block.

Quick Example of a Custom Rule:

Add this line to your local.rules file to detect unauthorized or plain text HTTP traffic on your WLAN:
Plaintext

```
alert http $HOME_NET any -> $EXTERNAL_NET any (msg:"UNENCRYPTED HTTP TRAFFIC DETECTED"; sid:1000001; rev:1;)
```

🛠️ Deployment Checklist

    Install Suricata on your gateway or monitoring interface.

    Configure your wireless card to operate in monitor/promiscuous mode to capture raw traffic.

    Update standard signatures using suricata-update.

    Append custom project-specific threat vectors to local.rules.

    Restart the Suricata service to apply updates:

```
sudo systemctl restart suricata
```
