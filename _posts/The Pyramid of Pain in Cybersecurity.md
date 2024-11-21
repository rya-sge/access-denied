### The Pyramid of Pain in Cybersecurity

The Pyramid of Pain is a powerful concept in cybersecurity, designed to help threat intelligence analysts, incident responders, and cybersecurity teams understand the types of adversary indicators they might encounter and the relative difficulty (or "pain") an attacker faces if those indicators are disrupted. Created by David Bianco in 2013, the Pyramid of Pain visually organizes six types of indicators used to detect and mitigate cyber threats, illustrating how targeting each type of indicator affects the adversary’s ability to operate.

This article will cover each layer of the Pyramid of Pain, explain how it can help cybersecurity teams craft an effective threat detection strategy, and demonstrate why it’s a valuable tool for security operations.

This well-renowned concept is being applied to cybersecurity solutions like [Cisco Security](https://gblogs.cisco.com/ca/2020/08/26/the-canadian-bacon-cisco-security-and-the-pyramid-of-pain/), [SentinelOne](https://www.sentinelone.com/blog/revisiting-the-pyramid-of-pain-leveraging-edr-data-to-improve-cyber-threat-intelligence/), and [SOCRadar](https://socradar.io/re-examining-the-pyramid-of-pain-to-use-cyber-threat-intelligence-more-effectively/) to improve the effectiveness of CTI (Cyber Threat Intelligence), threat hunting, and incident response exercises.

Understanding the Pyramid of Pain concept as a Threat Hunter, Incident Responder, or SOC Analyst is important.

[TOC]



## What Is the Pyramid of Pain?

The Pyramid of Pain is a hierarchical model that categorizes indicators of compromise (IoCs) according to their effectiveness in hindering adversaries. The model’s premise is straightforward: as you move up the pyramid, the types of indicators become harder for the adversary to modify or replace. For defenders, this means that targeting indicators higher in the pyramid imposes more "pain" on the attacker.

The pyramid is divided into six levels, starting with basic technical indicators at the bottom and progressing to behavioral patterns at the top. Here’s a breakdown of each layer, from easiest to most challenging for the attacker to change.

### 1. Hash Values (Bottom of the Pyramid)

Hash values are cryptographic representations of data, typically file contents. Common hashing algorithms include MD5 (deprecated), SHA-1 (deprecated), and SHA-256..

- Utility: Hash values are easy to identify and can be quickly flagged by antivirus or intrusion detection systems.

- Pain for Adversary: Very low. Attackers can modify the file or change its contents to produce a new hash with little effort.

Hashes are the simplest form of detection, and though useful for identifying known malicious files, they are relatively easy for attackers to bypass by making minor modifications to their files.

You've probably read ransomware reports in the past, where security researchers would provide the hashes related to the malicious or suspicious files used at the end of the report. You can check out [The DFIR Report](https://thedfirreport.com/) and [FireEye Threat Research Blogs](https://www.fireeye.com/blog/threat-research.html) if you’re interested in seeing an example.

Various online tools can be used to do hash lookups like [VirusTotal](https://www.virustotal.com/gui/) and [Metadefender Cloud - OPSWAT](https://metadefender.opswat.com/?lang=en).

### 2. IP Addresses

IP addresses are numerical labels assigned to devices in a network.

- Utility: Analysts often use IP addresses to identify and block connections from known malicious sources.

- **Pain for Adversary**: Low. Attackers can change IP addresses easily by using different infrastructure, such as new cloud servers or compromised devices, to evade detection.

While IP addresses are common indicators used to block traffic, they aren’t highly effective in isolation because attackers frequently rotate IP addresses to avoid detection.

#### Fast flux

According to [Akamai](https://blogs.akamai.com/2017/10/digging-deeper-an-in-depth-analysis-of-a-fast-flux-network-part-one.html), Fast Flux is a DNS technique used by botnets to hide phishing, web proxying, malware delivery, and malware communication activities behind compromised hosts acting as proxies. 

The purpose of using the Fast Flux network is to make the communication between malware and its command and control server (C&C) challenging to be discovered by security professionals. 

So, the primary concept of a Fast Flux network is having multiple IP addresses associated with a domain name, which is constantly changing. Palo Alto created a great fictional scenario to explain Fast Flux: ["](https://unit42.paloaltonetworks.com/fast-flux-101/)[Fast Flux 101: How Cybercriminals Improve the Resilience of Their Infrastructure to Evade Detection and Law Enforcement Takedowns"](https://unit42.paloaltonetworks.com/fast-flux-101/)

### 3. Domain Names

- **Definition**: Domain names are the website addresses used by attackers to deliver malware, conduct phishing campaigns, or establish command-and-control (C2) connections.
- **Description**: Blocking a malicious domain can disrupt an adversary’s operations temporarily.
- **Pain for Adversary**: Moderate. Although changing domain names is relatively simple, it requires more time, resources, and sometimes additional cost for attackers.

Blocking malicious domains can disrupt an adversary’s infrastructure for longer than simply blocking an IP address, as attackers need to register new domains and reconfigure systems to resume operations.

Domain Names can be a little more of a pain for the attacker to change as they would most likely need to purchase the domain, register it and modify DNS records. 

Unfortunately for defenders, many DNS providers have loose standards and provide APIs to make it even easier for the attacker to change the domain.

### 4. Artefacts

#### Hosts Artifacts

#### Network Artifacts

- **Definition**: Network artifacts include details of network traffic, such as HTTP headers, URI patterns, and user-agent strings used in malicious activities.
- **Description**: These indicators are useful for identifying unusual traffic patterns and distinguishing normal traffic from malicious activity.
- **Pain for Adversary**: Moderate to high. Changing network artifacts requires attackers to alter their techniques, which can be resource-intensive and impact the efficiency of their operations.

Network artifacts are harder to alter than domain names because attackers must re-engineer some of their tools or adjust how their malware communicates. Detecting and blocking these indicators can frustrate attackers and hinder their communication capabilities.

In this level, the attacker will feel a little more annoyed and frustrated if you can detect the attack. The attacker would need to circle back at this detection level and change his attack tools and methodologies. This is very time-consuming for the attacker, and probably, he will need to spend more resources on his adversary tools.

Host artifacts are the traces or observables that attackers leave on the system, such as registry values, suspicious process execution, attack patterns or IOCs (Indicators of Compromise), files dropped by malicious applications, or anything exclusive to the current threat.

#### User-Agent

If you can detect the custom User-Agent strings that the attacker is using, you might be able to block them, creating more obstacles and making their attempt to compromise the network more annoying.

### 5. Tools

- **Definition**: Tools refer to the specific software, scripts, or frameworks attackers use to conduct their operations.
- **Description**: Common tools include custom malware, remote access trojans (RATs), and network scanners. Blocking or detecting these tools can prevent attackers from gaining a foothold in the environment.
- **Pain for Adversary**: High. If their tools are detected and blocked, attackers must find or develop alternative methods, which is time-consuming and costly.

Attackers would use the utilities to create malicious macro documents (maldocs) for spearphishing attempts, a backdoor that can be used to establish [C2 (Command and Control Infrastructure)](https://www.varonis.com/blog/what-is-c2/), any custom .EXE, and .DLL files, payloads, or password crackers.

Tools represent a higher level of pain for adversaries because finding or creating new tools is more challenging than modifying technical indicators. It also means the attacker’s usual techniques become less effective, potentially reducing their success rate.

Antivirus signatures, detection rules, and YARA rules can be great weapons for you to use against attackers at this stage.

[MalwareBazaar ](https://bazaar.abuse.ch/)and [Malshare ](https://malshare.com/)are good resources to provide you with access to the samples, malicious feeds, and YARA results - these all can be very helpful when it comes to threat hunting and incident response. 

For detection rules,[ SOC Prime Threat Detection Marketplace ](https://tdm.socprime.com/)is a great platform, where security professionals share their detection rules for different kinds of threats including the latest CVE's that are being exploited in the wild by adversaries. 

Fuzzy hashing is also a strong weapon against the attacker's tools. Fuzzy hashing helps you to perform similarity analysis - match two files with minor differences based on the fuzzy hash values. One of the examples of fuzzy hashing is the usage of [SSDeep](https://ssdeep-project.github.io/ssdeep/index.html); on the SSDeep official website, you can also find the complete explanation for fuzzy hashing. 

### 6. Tactics, Techniques, and Procedures (TTPs) (Top of the Pyramid)

- **Definition**: TTPs encompass the specific methods adversaries use to achieve their objectives, including strategies for phishing, lateral movement, and data exfiltration.
- **Description**: Detecting TTPs focuses on the behavioral patterns of attackers, such as repeated methods for network infiltration or privilege escalation.
- **Pain for Adversary**: Very high. Changing TTPs requires attackers to alter their entire methodology, which can compromise their effectiveness and even prevent them from carrying out attacks.

Targeting TTPs represents the most powerful and impactful level of the Pyramid of Pain. If defenders can detect and block TTPs, attackers are forced to devise new operational strategies, which is highly resource-intensive and may deter them from continuing the attack.

TTPs stands for Tactics, Techniques & Procedures. This includes the whole [MITRE ](https://attack.mitre.org/)[ATT&CK Matrix](https://attack.mitre.org/), which means all the steps taken by an adversary to achieve his goal, starting from phishing attempts to persistence and data exfiltration. 

If you can detect and respond to the TTPs quickly, you leave the adversaries almost no chance to fight back. For, example if you could detect a [Pass-the-Hash](https://www.beyondtrust.com/resources/glossary/pass-the-hash-pth-attack) attack using Windows Event Log Monitoring and remediate it, you would be able to find the compromised host very quickly and stop the lateral movement inside your network. At this point, the attacker would have two options:

1. Go back, do more research and training, reconfigure their custom tools
2. Give up and find another target

Option 2 definitely sounds less time and resource-consuming.

------

## How Security Teams Can Use the Pyramid of Pain

The Pyramid of Pain is a valuable framework for security teams to prioritize their detection and response efforts. By focusing on indicators higher up in the pyramid, teams can create more effective barriers for attackers, disrupting their operations at a strategic level. Here are some ways to leverage the Pyramid of Pain in a security strategy:

1. **Prioritize Indicators by Impact**: Teams can assess their resources and capabilities to focus on higher-impact indicators, such as TTPs and tools, rather than getting caught up in an endless cycle of updating hash or IP blocklists.
2. **Enhance Threat Hunting**: By understanding adversary TTPs, analysts can develop threat-hunting strategies aimed at identifying behaviors rather than specific technical indicators.
3. **Strengthen Incident Response**: Incident response plans can incorporate the pyramid to guide how indicators are prioritized in investigations and containment strategies.
4. **Build Resilience in Detection Systems**: Instead of solely relying on static indicators, detection systems can incorporate behavior-based monitoring to detect anomalous activities aligned with known TTPs.
5. **Improve Communication Across Teams**: The pyramid also serves as an educational tool, helping stakeholders understand the varying impact of different indicators and why detecting certain types can significantly alter the threat landscape.

------

## Conclusion

The Pyramid of Pain remains a foundational concept in modern cybersecurity, emphasizing the importance of strategic detection over simple blocking. By focusing on the top layers of the pyramid—especially TTPs—cybersecurity teams can inflict maximum disruption to adversaries and create stronger, more resilient defenses. In a field where attackers constantly adapt, the Pyramid of Pain offers a roadmap for defenders to stay one step ahead, focusing on the indicators that are hardest for attackers to change and forcing them into a position where they must reconsider or even abandon their attack strategies.

By aligning detection and response efforts with the Pyramid of Pain, security teams can make their adversaries' lives significantly harder, improving the organization’s overall resilience to cyber threats.