---
layout: post
title: "Three ATT&CK Techniques Behind the Ransomware Endgame - Service Stop, Disable or Modify Tools, and Indicator Blocking"
date:   2026-09-09
lang: en
locale: en-GB
categories: security
tags: security threat mitre ransomware edr incident-responder cybersecurity
description: How attackers disable security tools (T1562.001), cut telemetry (T1562.006) and stop services (T1489) before impact, and how defenders detect and stop it.
image: /assets/article/securite/mitre-attack/2026-09-09-mitre-attack-disruption-evasion-mindmap.png
isMath: false
---

Before a ransomware operator encrypts a file server or a wiper corrupts a database, the intrusion usually spends its final minutes doing something quieter: taking the defences apart. The endpoint agent is killed, the log pipeline is cut, and the services that hold the data open are stopped. Only then does the destructive payload run. Three MITRE ATT&CK techniques describe that teardown, and they are among the most commonly reported techniques in ransomware and destructive-attack post-mortems.

This article explains those three techniques with their definitions taken directly from the ATT&CK knowledge base: **Disable or Modify Tools** ([T1562.001](https://attack.mitre.org/techniques/T1562/001)), **Indicator Blocking** ([T1562.006](https://attack.mitre.org/techniques/T1562/006)), and **Service Stop** ([T1489](https://attack.mitre.org/techniques/T1489)). For each one it covers what the technique is, how adversaries carry it out, which groups and malware families use it, how a defender detects it, and which mitigations apply. It ends with how the three chain together and with a change in ATT&CK v19 that renumbered two of them.

> **Source and currency note.** Technique data is taken from the MITRE ATT&CK for Enterprise STIX dataset. `T1489` is current as of ATT&CK **v19.2**. `T1562.001` and `T1562.006` are described as they stood through **v18.0**, the last release in which they were live sub-techniques; ATT&CK v19 revoked the `T1562` "Impair Defenses" tree and folded it into a new top-level technique, [T1685](https://attack.mitre.org/techniques/T1685). The [What changed in ATT&CK v19](#what-changed-in-attck-v19-t1562--t1685) section covers that migration.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The three techniques at a glance

Two of these techniques sit under the **Defense Evasion** tactic and one under **Impact**, but they serve one operational goal: remove the defender's ability to see, respond to, or recover from what happens next. The split is between blinding the defender (evasion) and denying the asset (impact).

| Technique | ID | Tactic | What it targets |
|-----------|----|--------|-----------------|
| Disable or Modify Tools | [T1562.001](https://attack.mitre.org/techniques/T1562/001) | Defense Evasion | Security software (EDR, antivirus, IDS) |
| Indicator Blocking | [T1562.006](https://attack.mitre.org/techniques/T1562/006) | Defense Evasion | Telemetry and event collection (ETW, Sysmon, SIEM, syslog) |
| Service Stop | [T1489](https://attack.mitre.org/techniques/T1489) | Impact | Business and infrastructure services |

The mapping below shows each technique pointing at what it acts on, and why Service Stop is a precursor rather than an end in itself.

![Three techniques mapped to their tactics and targets: T1562.001 and T1562.006 under Defense Evasion act on security tools and telemetry, T1489 under Impact stops business services and clears the way for data destruction and encryption]({{site.url_complet}}/assets/article/securite/mitre-attack/mitre-technique-tactic-mapping-concept.png)

## Service Stop (T1489)

[Service Stop](https://attack.mitre.org/techniques/T1489) is an **Impact** technique. Adversaries stop or disable services on a system to make them unavailable to legitimate users. Stopping critical services can inhibit the response to an incident, or advance the adversary's own goal of damaging the environment. It applies across Windows, Linux, macOS, ESXi and IaaS platforms.

There are two motives, and they often occur together. The first is disruption for its own sake: an attacker disables a service of high importance, such as `MSExchangeIS`, which makes Exchange content inaccessible, or stops so many services that the system is left unusable. Olympic Destroyer, which ATT&CK cites as a reference case, disabled services wholesale to render systems inoperable.

The second motive is preparation for destruction. Many services keep their data stores locked while running, so an adversary stops the service to unlock the files underneath it. This is the standard move before [Data Destruction](https://attack.mitre.org/techniques/T1485) or [Data Encrypted for Impact](https://attack.mitre.org/techniques/T1486) against the data stores of Exchange, SQL Server, or virtual machines hosted on ESXi. Ransomware routinely stops database and backup services first so their files can be encrypted.

The technique reaches into the cloud as well. By calling the `DisableAWSServiceAccess` API in AWS, an actor can prevent a service from creating service-linked roles on new accounts across an AWS Organization, degrading a control-plane capability rather than a host process.

### Who uses it

Service Stop is dominated by ransomware and destructive operations. The groups and a sample of the software recorded against it:

| Type | Examples |
|------|----------|
| Groups | Sandworm Team (G0034), Lazarus Group (G0032), Wizard Spider (G0102), Indrik Spider (G0119), Kimsuky (G0094), LAPSUS$ (G1004), Medusa Group (G1051) |
| Software | Olympic Destroyer (S0365), WannaCry (S0366), Ryuk (S0446), Maze (S0449), Conti (S0575), REvil (S0496), Netwalker (S0457), Ragnar Locker (S0481), RobbinHood (S0400), EKANS (S0605), AvosLocker (S1053) |

### Mitigations

| Mitigation | ID | How it helps |
|------------|----|--------------|
| Restrict File and Directory Permissions | [M1022](https://attack.mitre.org/mitigations/M1022) | Prevents modification of service binaries and their startup files |
| Restrict Registry Permissions | [M1024](https://attack.mitre.org/mitigations/M1024) | Protects the registry keys that control Windows services |
| User Account Management | [M1018](https://attack.mitre.org/mitigations/M1018) | Limits which accounts can stop or disable services |
| Network Segmentation | [M1030](https://attack.mitre.org/mitigations/M1030) | Contains the blast radius when a host is taken down |
| Out-of-Band Communications Channel | [M1060](https://attack.mitre.org/mitigations/M1060) | Keeps incident response coordinated when primary services are down |

The most consequential control is not in this list, because ATT&CK treats it as recovery rather than mitigation: offline, immutable backups are what turn a successful Service Stop plus encryption from a disaster into an interruption.

## Disable or Modify Tools (T1562.001)

[Disable or Modify Tools](https://attack.mitre.org/techniques/T1562/001) is a sub-technique of Impair Defenses, under the **Defense Evasion** tactic. Adversaries modify or disable security tools to avoid detection of their malware and activity. It applies to Windows, macOS, Linux, Containers, IaaS and network devices.

The technique takes many forms, from crude to sophisticated:

- **Killing and stopping.** Terminate security software processes or stop their services outright. Adversaries have used rootkit-removal kits and tools such as GMER to find and shut down hidden processes and antivirus software.
- **Configuration tampering.** Delete or modify registry keys and configuration files so a tool no longer works, or disable updates so the latest signatures and patches never arrive. Modifying the `Start` and `Enable` values under the Sysmon `Autologger` registry key tampers with, and can disable, Sysmon logging.
- **Exclusions.** Add a directory to an EDR product's exclusion list, so malicious files placed there are ignored ([File/Path Exclusions](https://attack.mitre.org/techniques/T1564/012)).
- **Blocking the agent from loading.** Abuse the Windows process-mitigation policy to stop an EDR from loading its user-mode DLLs, by spawning a process with the `PROCESS_CREATION_MITIGATION_POLICY_BLOCK_NON_MICROSOFT_BINARIES_ALWAYS_ON` attribute so non-Microsoft-signed instrumentation cannot load.
- **Driver abuse.** Exploit a legitimate but vulnerable driver to reach kernel space and bypass anti-tampering features, the pattern known as Bring Your Own Vulnerable Driver (BYOVD). Attackers have also abused the Windows Time Travel Debugging monitor driver to suspend an EDR's child processes and crash the tool.
- **Firmware and network devices.** On network devices, alter startup configuration files to skip the digital-signature verification that normally runs at boot.

### Who uses it

This technique has very broad adoption, spanning state-linked espionage groups and commodity ransomware crews. A representative sample:

| Type | Examples |
|------|----------|
| Groups | Turla (G0010), APT29 (G0016), Lazarus Group (G0032), FIN6 (G0037), Gamaredon (G0047), Magic Hound (G0059), MuddyWater (G0069), TA505 (G0092), Kimsuky (G0094), Wizard Spider (G0102), Aquatic Panda (G0143), TeamTNT (G0139), INC Ransom (G1032), Play (G1040) |
| Software | Cobalt Strike (S0154), TrickBot (S0266), and dozens of ransomware and RAT families |

### Detection and mitigations

Detection focuses on the tool's own health as a signal. Monitor processes and command-line arguments for security tools or services being killed or stopped, and monitor registry edits that touch services and startup entries belonging to security products. A lack of expected log events is itself suspicious: when a sensor that normally chatters goes silent, that silence is the indicator.

| Mitigation | ID | How it helps |
|------------|----|--------------|
| Restrict Registry Permissions | [M1024](https://attack.mitre.org/mitigations/M1024) | Protects the keys that configure security tooling |
| Restrict File and Directory Permissions | [M1022](https://attack.mitre.org/mitigations/M1022) | Protects tool binaries and configuration files |
| User Account Management | [M1018](https://attack.mitre.org/mitigations/M1018) | Reduces the set of accounts that can tamper with tools |
| Execution Prevention | [M1038](https://attack.mitre.org/mitigations/M1038) | Blocks known-vulnerable drivers used for BYOVD |

## Indicator Blocking (T1562.006)

[Indicator Blocking](https://attack.mitre.org/techniques/T1562/006) is also a sub-technique of Impair Defenses under **Defense Evasion**, and it is the subtler sibling of Disable or Modify Tools. Rather than killing the tool, the adversary blocks the indicators or events that sensors would normally gather and forward for analysis. The tool may appear to run while reporting nothing useful.

The techniques operate at the point where telemetry is collected or transported:

- **Host sensor tampering.** Disable or reconfigure host-based sensors such as Event Tracing for Windows (ETW) by changing the settings that control the flow of event telemetry. This can be done through the PowerShell `Set-EtwTraceProvider` cmdlet or by editing the registry directly.
- **Redirecting the log.** Modify the `File` value under the `EventLog\Security` registry key so events are written to a different `.evtx` file, hiding activity from where analysts look. The change takes effect immediately and needs no reboot.
- **Cutting the network path.** Where indicators are shipped off-host, block the traffic that reports them: stop the local forwarding process, or add a host firewall rule that blocks traffic to the SIEM collectors that aggregate events.
- **Unix and hypervisor logging.** On Linux, disable or reconfigure log processing tools such as `syslog` or `nxlog`. ESXi also uses syslog, which can be reconfigured with commands such as `esxcli system syslog config set`.

### Who uses it

Compared with the previous two techniques, Indicator Blocking has a narrower, more deliberate set of reported users, weighted toward stealth-focused espionage:

| Type | Examples |
|------|----------|
| Groups | APT41 (G0096), APT5 (G1023) |
| Software | Ebury (S0377), Waterbear (S0579), HermeticWiper (S0697), Brute Ratel C4 (S1063), Woody RAT (S1065), HUI Loader (S1097) |

### Detection and mitigations

The primary detection is the absence of data: a host sensor that stops reporting, either entirely or only for certain event types, is a strong signal. Depending on what is collected, an analyst may still catch the triggering event; for example, Sysmon logs when its configuration state changes (Event ID 16). Correlating "last seen" times per host at the SIEM turns a silent agent into an alert.

| Mitigation | ID | How it helps |
|------------|----|--------------|
| Restrict File and Directory Permissions | [M1022](https://attack.mitre.org/mitigations/M1022) | Protects log files and sensor configuration |
| Software Configuration | [M1054](https://attack.mitre.org/mitigations/M1054) | Forwards logs to a remote collector so local blocking is detectable |
| User Account Management | [M1018](https://attack.mitre.org/mitigations/M1018) | Limits who can reconfigure telemetry |

Software Configuration is the load-bearing control here. Once logs are shipped to a remote collector in near real time, blocking them locally produces exactly the gap in the timeline that detection relies on.

## How the three chain together

These techniques are not independent choices from a menu; they are stages of one sequence. An intrusion that has reached administrative privilege runs them in a characteristic order: disable the tools that would raise an alert, block the telemetry that would preserve a record, then stop the services that hold the target data, and only then execute the destructive payload. The result is that the impact lands while the defender is both blind and slow to respond.

![Activity flow of the teardown: from an administrative foothold to disabling security tools (T1562.001), blocking telemetry (T1562.006), stopping critical services (T1489), and finally destroying or encrypting data (T1485/T1486), leaving incident response blinded]({{site.url_complet}}/assets/article/securite/mitre-attack/ransomware-defense-teardown-workflow.png)

The ordering is what makes the sequence dangerous, and it is also where a defender gets leverage. Each stage that survives, an EDR that cannot be killed, a log already shipped off-host, a backup service the attacker cannot stop, breaks the chain before impact. Defence in depth here means ensuring no single teardown step disables everything downstream of it.

## What changed in ATT&CK v19 (T1562 → T1685)

Anyone cross-referencing this article against the current ATT&CK website will find that two of the three IDs no longer resolve to a live page. In ATT&CK v19, MITRE revoked the entire `T1562` "Impair Defenses" technique and its sub-techniques, including `T1562.001` and `T1562.006`, and replaced them with a restructured top-level technique, [T1685 Disable or Modify Tools](https://attack.mitre.org/techniques/T1685), under a new **Defense Impairment** tactic.

A few points matter for anyone maintaining detections or mappings:

- **The IDs are revoked, not deleted.** `T1562.001` and `T1562.006` remain in the dataset with a `revoked-by` pointer to `T1685`, so historical reports and mappings can still be resolved. They were live through v18.0.
- **The concept is consolidated, not dropped.** The behaviours described above, killing tools, tampering with configuration, blocking telemetry, all fall under `T1685` now. Its own sub-techniques (`T1685.001` through `T1685.006`) reorganise the log-focused behaviours, covering Windows Event Log, cloud logs, the tool UI, the Linux audit system, and log clearing.
- **The tactic moved.** The old sub-techniques lived under Defense Evasion; `T1685` sits under the new Defense Impairment tactic, so a technique-to-tactic mapping needs updating, not just an ID swap.
- **Service Stop is unaffected.** `T1489` remains a live Impact technique in v19.2.

When writing new detection content, map to `T1685`; when reading older threat intelligence, expect `T1562.001` and `T1562.006` and treat them as equivalents of the new structure.

## Conclusion

Disable or Modify Tools, Indicator Blocking and Service Stop describe the three moves an attacker makes to clear the way before causing damage: blind the sensors, silence the record, and unlock the data. They are reported together in ransomware and destructive intrusions because they solve the same problem for the adversary, which is operating without being seen, stopped, or reversed. For a defender, the practical consequence is that endpoint tamper protection, off-host log forwarding, and offline backups are not three separate hygiene items but one connected line of defence, each covering the failure of the others. The ATT&CK v19 move of the Impair Defenses tree into `T1685` changes the identifiers and the tactic label, not the behaviour, so existing detections keep their value once their mappings are updated.

![Mindmap of the three ATT&CK techniques covering Service Stop (T1489), Disable or Modify Tools (T1562.001) and Indicator Blocking (T1562.006), their sub-behaviours, the defensive controls against them, and the ATT&CK v19 change to T1685]({{site.url_complet}}/assets/article/securite/mitre-attack/2026-09-09-mitre-attack-disruption-evasion-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Tactic** | The adversary's goal for an action in ATT&CK, such as Defense Evasion or Impact; the "why" behind a technique. |
| **Technique** | A specific way an adversary achieves a tactical goal, identified as `Txxxx`; a sub-technique is written `Txxxx.yyy`. |
| **Impair Defenses (T1562)** | The pre-v19 parent technique grouping ways to disable, block or degrade defensive capabilities; revoked in v19 in favour of T1685. |
| **EDR** | Endpoint Detection and Response, host security software that monitors process, file and network behaviour and reports it centrally. |
| **ETW** | Event Tracing for Windows, the kernel and user-mode telemetry framework many security tools consume; a frequent target of Indicator Blocking. |
| **Sysmon** | A Windows system-monitoring service that writes detailed event logs, configured through registry Autologger keys that adversaries tamper with. |
| **BYOVD** | Bring Your Own Vulnerable Driver, abusing a legitimate signed but flawed driver to gain kernel access and bypass tool anti-tampering. |
| **SIEM** | Security Information and Event Management, the central platform that aggregates and analyses forwarded logs and indicators. |
| **Data Encrypted for Impact (T1486)** | The Impact technique in which an adversary encrypts data to deny access, the ransomware payload that Service Stop enables. |
| **Revoked (ATT&CK)** | Status marking an object superseded by another; it stays in the dataset with a `revoked-by` link rather than being deleted. |

### Security Implementation Checklist

The rows below are defender-facing controls: each is a property a hardened environment should hold, paired with what the adversary achieves if it does not.

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | EDR and antivirus run with tamper protection enabled and cannot be stopped by a local administrator. | T1562.001 kills the agent and the intrusion proceeds unmonitored. |
| ☐ | The registry keys and configuration files of security tools are restricted and their changes audited. | Configuration tampering silently disables detection while the tool appears to run. |
| ☐ | Known-vulnerable drivers are blocked (for example via an execution-prevention or driver blocklist policy). | BYOVD grants kernel access that bypasses tool anti-tampering. |
| ☐ | Logs are forwarded to a remote collector in near real time, not only stored locally. | T1562.006 blocks or redirects local telemetry with no trace at the SIEM. |
| ☐ | The SIEM alerts on the absence of expected events (per-host "last seen" heartbeats). | A silenced or redirected sensor goes unnoticed because only present data is watched. |
| ☐ | Privileges to stop services and reconfigure logging are limited to dedicated accounts. | A single compromised admin account can perform the full teardown. |
| ☐ | Backups are kept offline or immutable and their service cannot be stopped from production hosts. | T1489 plus encryption becomes unrecoverable rather than an interruption. |
| ☐ | Networks are segmented so taking down one host does not cascade. | Service Stop and impact spread across the estate unimpeded. |

## Frequently Asked Questions

**Q: Why are two of these techniques classified as Defense Evasion and one as Impact?**

The tactic reflects the adversary's goal. Disable or Modify Tools (T1562.001) and Indicator Blocking (T1562.006) exist to avoid detection, which is the Defense Evasion goal: the attacker wants their other actions to go unseen. Service Stop (T1489) exists to make a service unavailable to legitimate users, which is the Impact goal of degrading or denying the target. The first two protect the operation; the third is part of the damage itself.

**Q: What is the practical difference between Disable or Modify Tools and Indicator Blocking?**

They attack different points in the detection chain:

- **Disable or Modify Tools** goes after the security software itself, by killing its process, corrupting its configuration, or preventing it from loading. The tool stops working.
- **Indicator Blocking** leaves the tool running but stops the events from being collected or delivered, by tampering with ETW or Sysmon, redirecting the event log, or blocking the network path to the SIEM. The tool works but reports nothing useful.

In practice adversaries combine them, but the distinction matters for detection: the first shows up as a tool going down, the second as data going quiet.

**Q: Why do ransomware operators stop services before encrypting files?**

Many services hold their data stores open and locked while running, so the files cannot be modified from outside the process. Databases such as SQL Server and Exchange, and virtual machines on ESXi, are the common cases. Stopping the service releases the lock, which lets the encryption or destruction payload operate on the underlying files. Attackers also stop backup and security services in the same step so recovery and detection are degraded at the same time.

**Q: If logs are being blocked, how can a defender detect the attack?**

By monitoring for absence rather than presence. A sensor that normally reports continuously and then goes silent is itself the indicator, so a SIEM that tracks a per-host heartbeat or "last seen" time can alert on the gap that Indicator Blocking creates. Some tampering also produces its own event before the silence, such as Sysmon's Event ID 16 when its configuration changes. The decisive control is forwarding logs off-host in near real time, so anything blocked locally has already left a record elsewhere.

**Q: These IDs are marked revoked on the ATT&CK website. Are they still worth learning?**

Yes. ATT&CK v19 revoked the `T1562` Impair Defenses tree and consolidated it into `T1685`, but the behaviours are unchanged and the revoked IDs remain in the dataset with a `revoked-by` pointer, so years of existing threat reports still reference `T1562.001` and `T1562.006`. Understanding them is necessary to read historical intelligence, and mapping them to `T1685` is a mechanical update once the concepts are clear. Service Stop (`T1489`) was not affected and remains current.

**Q: Which single control most reduces exposure to all three techniques?**

No single control covers all three, which is the point of treating them as a chain. That said, restricting privilege has the broadest effect: all three normally require administrative rights to kill a protected tool, reconfigure logging, or stop a service, so limiting which accounts hold those rights raises the cost of every stage. It must be paired with off-host log forwarding and offline backups, because privilege restriction slows the teardown but does not by itself preserve visibility or enable recovery.

## References

- [T1489 Service Stop](https://attack.mitre.org/techniques/T1489) — MITRE ATT&CK for Enterprise
- [T1562.001 Impair Defenses: Disable or Modify Tools](https://attack.mitre.org/techniques/T1562/001) — MITRE ATT&CK for Enterprise
- [T1562.006 Impair Defenses: Indicator Blocking](https://attack.mitre.org/techniques/T1562/006) — MITRE ATT&CK for Enterprise
- [T1562 Impair Defenses](https://attack.mitre.org/techniques/T1562) — parent technique (revoked in v19)
- [T1685 Disable or Modify Tools](https://attack.mitre.org/techniques/T1685) — the v19 replacement technique
- [T1486 Data Encrypted for Impact](https://attack.mitre.org/techniques/T1486) and [T1485 Data Destruction](https://attack.mitre.org/techniques/T1485) — the Impact techniques Service Stop enables
- [MITRE ATT&CK](https://attack.mitre.org) — the knowledge base, tactics and techniques

### Related articles

- [The Pyramid of Pain in Cybersecurity]({{site.url_complet}}/2024/11/28/pyramid-of-pain/)
- [Digital Forensics and Incident Response (DFIR) - Introduction]({{site.url_complet}}/2025/01/15/digital-forensics-incident-response-dfir/)
- [Windows Domain Persistence - Golden Tickets and the Skeleton Key]({{site.url_complet}}/2026/06/30/windows-persistence/)
- [Four ATT&CK Techniques for Getting Into Accounts - Valid Accounts, Brute Force, Password Guessing and Password Spraying]({{site.url_complet}}/2026/09/09/mitre-attack-valid-accounts-brute-force/)
