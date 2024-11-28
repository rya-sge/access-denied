### Cyber Kill Chain

From https://tryhackme.com/r/room/cyberthreatintel

Developed by Lockheed Martin, the Cyber Kill Chain breaks down adversary actions into steps. This breakdown helps analysts and defenders identify which stage-specific activities occurred when investigating an attack. The phases defined are shown in the image below.

![Image of the seven steps of the Cyber Kill Chain.](https://tryhackme-images.s3.amazonaws.com/user-uploads/5fc2847e1bbebc03aa89fbf2/room-content/ef67be43aaf8073a8309df3e160c7e36.png)

| Technique             | Purpose                                                      | Examples                                                  |
| --------------------- | ------------------------------------------------------------ | --------------------------------------------------------- |
| Reconnaissance        | Obtain information about the victim and the tactics used for the attack. | Harvesting emails, OSINT, and social media, network scans |
| Weaponisation         | Malware is engineered based on the needs and intentions of the attack. | Exploit with a backdoor, malicious office document        |
| Delivery              | Covers how the malware would be delivered to the victim's system. | Email, weblinks, USB                                      |
| Exploitation          | Breach the victim's system vulnerabilities to execute code and create scheduled jobs to establish persistence. | EternalBlue, Zero-Logon, etc.                             |
| Installation          | Install malware and other tools to gain access to the victim's system. | Password dumping, backdoors, remote access trojans        |
| Command & Control     | Remotely control the compromised system, deliver additional malware, move across valuable assets and elevate privileges. | Empire, Cobalt Strike, etc.                               |
| Actions on Objectives | Fulfil the intended goals for the attack: financial gain, corporate espionage, and data exfiltration. | Data encryption, ransomware, public defacement            |



## FAQ

> When an adversary has obtained access to a network and is extracting data, what phase of the kill chain are they on?

Actions on Objectives