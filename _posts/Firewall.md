# Firewall

https://tryhackme.com/room/firewallfundamentals

Firewall deployment became common in networks after organizations discovered their ability to filter harmful traffic from their systems and networks. Several different types of firewalls were introduced afterward, each serving a unique purpose. It's also important to note that different types of firewalls work on different OSI model layers. Firewalls are categorized into many types. 

Let’s examine a few of the most common types of firewalls and their roles in the OSI model.

![img](https://tryhackme-images.s3.amazonaws.com/user-uploads/6645aa8c024f7893371eb7ac/room-content/6645aa8c024f7893371eb7ac-1725967312491.png)

### Stateless Firewall

This type of firewall operates on layer 3 and layer 4 of the OSI model and works solely by filtering the data based on predetermined rules without taking note of the state of the previous connections. This means it will match every packet with the rules regardless of whether it is part of a legitimate connection. It maintains no information on the state of the previous connections to make decisions for future packets. Due to this, these firewalls can process the packets quickly. However, they cannot apply complex policies to the data based on its relationship with the previous connections. Suppose the firewall denies a few packets from a single source based on its rules. Ideally, it should drop all the future packets from this source because the previous packets could not comply with the firewall’s rules. However, the firewall keeps forgetting this, and future packets from this source will be treated as new and matched by its rules again.

### Stateful Firewall

Unlike stateless firewalls, this type of firewall goes beyond filtering packets by predetermined rules. It also keeps track of previous connections and stores them in a state table. This adds another layer of security by inspecting the packets based on their history with connections. Stateful firewalls operate at layer 3 and layer 4 of the OSI model. Suppose the firewall accepts a few packets from a source address based on its rules. In that case, it will take note of this connection in its stated table and allow all the future packets for this connection to automatically get allowed without inspecting each of them. Similarly, the stateful firewalls take note of the connections for which they deny a few packets, and based upon this information, they deny all the subsequent packets coming from the same source.

### Proxy Firewall

The problem with previous firewalls was their inability to inspect the contents of a packet. Proxy firewalls, or application-level gateways, act as intermediaries between the private network and the Internet and operate on the OSI model’s layer 7. They inspect the content of all packets as well. The requests made by users in a network are forwarded by this proxy after inspection and masking them with their own IP address to provide anonymity for the internal IP addresses. Content filtering policies can be applied to these firewalls to allow/deny incoming and outgoing traffic based on their content.

### Next-Generation Firewall (NGFW)

This is the most advanced type of firewall that operates from layer 3 to layer 7 of the OSI model, offering deep packet inspection and other functionalities that enhance the security of incoming and outgoing network traffic. It has an intrusion prevention system that blocks malicious activities in real time. It offers heuristic analysis by analyzing the patterns of attacks and blocking them instantly before reaching the network. NGFWs have SSL/TLS decryption capabilities, which inspect the packets after decrypting them and correlate the data with the threat intelligence feeds to make efficient decisions.

The table below lists each firewall’s characteristics, which will help you choose the most suitable firewall for different use cases.

| Firewalls                 | Characteristics                                              |
| ------------------------- | ------------------------------------------------------------ |
| Stateless firewalls       | - Basic filtering - No track of previous connections - Efficient for high-speed networks |
| Stateful firewalls        | - Recognize traffic by patterns - Complex rules can be applicable - Monitor the network connections |
| Proxy firewalls           | - Inspect the data inside the packets as well - Provides content filtering options - Provides application control - Decrypts and inspects SSL/TLS data packets |
| Next-generation firewalls | - Provides advanced threat protection - Comes with an intrusion prevention system - Identify anomalies based on heuristic analysis - Decrypts and inspects SSL/TLS data packets |



## **Known Vulnerabilities and Exploits**

Despite their critical role, firewalls are not immune to vulnerabilities:



| **Firewall Type**  | **Common Vulnerabilities**                                   |
| ------------------ | ------------------------------------------------------------ |
| Packet-Filtering   | IP spoofing, fragmented packet bypass                        |
| Stateful Firewalls | SYN flood attacks, evasion via protocol anomalies            |
| Proxy Firewalls    | Application misconfigurations, insufficient filtering        |
| NGFW               | Zero-day vulnerabilities in DPI engines, bypass via tunneling |
| WAF                | Bypass via encoding tricks, regex misconfiguration           |
| Cloud Firewalls    | API abuse, misconfigured access policies                     |

**Notable incidents:**

- *2019 Fortinet VPN flaw (CVE-2018-13379)*: Allowed unauthenticated access to system files.
- *SonicWall SMA 100 zero-day (2021)*: Allowed attackers to gain remote access.
- *Palo Alto Networks PAN-OS (CVE-2020-2021)*: Critical RCE vulnerability due to SAML implementation flaw.



## Ressources

Chatgpt with the input "Write me an article about the different type of firewall, what they are usefull, security incident possible, known vulnerabilites,..."