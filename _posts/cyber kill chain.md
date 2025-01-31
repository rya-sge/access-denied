- Many regulation and standardization bodies have released their cyber kill chain. Each kill chain follows roughly the same structure, with some going more in-depth or defining objectives differently. Below is a small list of standard cyber kill chains.
  - [Lockheed Martin Cyber Kill Chain](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html)
  - [Unified Kill Chain](https://unifiedkillchain.com/)
  - [Varonis Cyber Kill Chain](https://www.varonis.com/blog/cyber-kill-chain/)
  - [Active Directory Attack Cycle](https://github.com/infosecn1nja/AD-Attack-Defense)
  - [MITRE ATT&CK Framework](https://attack.mitre.org/)

In this room, we will commonly reference the "Lockheed Martin Cyber Kill Chain." It is a more standardized kill chain than others and is very commonly used among red and blue teams.

The Lockheed Martin kill chain focuses on a perimeter or external breach. Unlike other kill chains, it does not provide an in-depth breakdown of internal movement. You can think of this kill chain as a summary of all behaviors and operations present.

https://tryhackme.com/r/room/redteamfundamentals

In this room, we will commonly reference the "Lockheed Martin Cyber Kill Chain." It is a more standardized kill chain than others and is very commonly used among red and blue teams.

The Lockheed Martin kill chain focuses on a perimeter or external breach. Unlike other kill chains, it does not provide an in-depth breakdown of internal movement. You can think of this kill chain as a summary of all behaviors and operations present.

![img](https://tryhackme-images.s3.amazonaws.com/user-uploads/5ed5961c6276df568891c3ea/room-content/33e4c2dc2ab851b11654ae61953a7df1.png)

Components of the kill chain are broken down in the table below.

| Technique             | Purpose                                                      | Examples                                         |
| --------------------- | ------------------------------------------------------------ | ------------------------------------------------ |
| Reconnaissance        | Obtain information on the target                             | Harvesting emails, OSINT                         |
| Weaponization         | Combine the objective with an exploit. Commonly results in a deliverable payload. | Exploit with backdoor, malicious office document |
| Delivery              | How will the weaponized function be delivered to the target  | Email, web, USB                                  |
| Exploitation          | Exploit the target's system to execute code                  | MS17-010, Zero-Logon, etc.                       |
| Installation          | Install malware or other tooling                             | Mimikatz, Rubeus, etc.                           |
| Command & Control     | Control the compromised asset from a remote central controller | Empire, Cobalt Strike, etc.                      |
| Actions on Objectives | Any end objectives: ransomware, data exfiltration, etc.      | Conti, LockBit2.0, etc.                          |



e. As an example, you can check [Carbanak's information](https://attack.mitre.org/groups/G0008/).