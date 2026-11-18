---
layout: post
title: Digital Forensics and Incident Response (DFIR) - Introduction
date:   2025-01-15
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: security tryhackme
tags: security threat incident-responder cybersecurity pyramid
description: DFIR stands for **Digital Forensics and Incident Response**. This field covers the collection of forensic artifacts from digital devices such as computers, media devices, and smartphones to investigate an incident. 
image: /assets/article/securite/dfir-sans-picerl.png
isMath: false
---

## Introduction

DFIR stands for **Digital Forensics and Incident Response**. This field covers the collection of forensic artifacts from digital devices such as computers, media devices, and smartphones to investigate an incident. 

This field helps Security Professionals identify:

- footprints left by an attacker when a security incident occurs
-  use them to determine the extent of compromise in an environment, 
- and restore the environment to the state it was before the incident occurred. 

> Warning: this article is still in draft state and its content is still mainly taken from the documentation. Its content should become more personal later.
>
> This article is based on the room [DFIR: An Introduction](https://tryhackme.com/r/room/introductoryroomdfirmodule) by TryHackMe

[TOC]

## What you need to know first

This introduction names several notions of security operations and forensics in passing, without defining them.

- **Forensic artifact**: a trace of activity left on a system, such as a log entry, a registry key, a file timestamp or a process in memory. DFIR collects and interprets these artifacts to reconstruct what an attacker did, and the tools listed below each extract a family of them.
- **Indicators of compromise (IoCs)**: observable signs that a system has been attacked, such as a malicious file hash, an IP address or a domain. The Identification step starts from such indicators; the site's [Pyramid of Pain]({{site.url_complet}}/2024/11/28/pyramid-of-pain/) article classifies them by how hard they are for an attacker to change.
- **False positive**: an alert raised for activity that turns out to be benign. Sifting false alarms from real incidents is one of the reasons for DFIR given below, and it happens during Identification.
- **Disk image and memory capture**: investigators work on copies of the evidence, a bit-for-bit image of a disk or a dump of a machine's RAM, rather than on the live system. Autopsy analyses the first and Volatility the second; the [disk image (dd) article]({{site.url_complet}}/2022/09/16/forensic-image-disk-dd/) shows how such an image is analysed.
- **Windows registry**: the hierarchical database in which Windows stores system and user configuration, and which also records traces of user and program activity. Eric Zimmerman's tools parse it alongside the file system.
- **Timeline analysis**: ordering the timestamps found in many artifacts into one chronology of events. KAPE and Zimmerman's tools help build such a timeline to establish the extent and timeframe of a breach.



## The need for DFIR

DFIR helps security professionals in various ways, some of which are summarized below:

- Finding evidence of attacker activity in the network and sifting false alarms from actual incidents.
- Robustly removing the attacker, so their foothold from the network no longer remains.
- Identifying the extent and timeframe of a breach. This helps in communicating with relevant stakeholders.
- Finding the loopholes that led to the breach. What needs to be changed to avoid the breach in the future?
- Understanding attacker behavior to pre-emptively block further intrusion attempts by the attacker.
- Sharing information about the attacker with the community.

-----

## Who performs DFIR?

As the name suggests, DFIR requires expertise in both Digital Forensics and Incident Response. Dividing these two fields this way, the following skillset is needed to become a DFIR professional:

- **Digital Forensics:** These professionals are experts in identifying forensic artifacts or evidence of human activity in digital devices. 
- **Incident Response:** Incident responders are experts in cybersecurity and leverage forensic information to identify the activity of interest from a security perspective. 

DFIR professionals know about Digital Forensics and cybersecurity and combine these domains to achieve their goals. Digital Forensics and Incident Response domains are often combined because they are highly interdependent. Incident Response leverages knowledge gained from Digital Forensics. Similarly, Digital Forensics takes its goals and scope from the Incident Response process, and the IR process defines the extent of forensic investigation.



------

## The Incident Response Process

In Security Operations, the prominent use of Digital Forensics is to perform Incident Response. We will learn the Incident Response process and observe how Digital Forensics helps in the IR process in this task.

Different organizations have published standardized methods to perform Incident Response. 

### NIST SP-800-61

NIST has defined a process in their [SP-800-61 Rev. 2 Incident Handling guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf), which has the following steps:

1. Preparation
2. Detection and Analysis
3. Containment, Eradication, and Recovery
4. Post-incident Activity

This four-step lifecycle comes from Revision 2 (2012). [SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final), published in April 2025, supersedes it and places incident response within the NIST Cybersecurity Framework (CSF) 2.0. The SANS comparison below uses the Rev. 2 steps.

### SANS - Incident Handler's handbook (PICERL)

Similarly, SANS has published an [Incident Handler's handbook](https://www.sans.org/white-papers/33901/). The handbook defines the steps as follows:

1. Preparation
2. Identification
3. Containment
4. Eradication
5. Recovery
6. Lessons Learned

The steps defined by SANS are often summarized as the acronym PICERL, making them easy to remember. We can see that the steps specified by SANS and NIST are identical. 

While NIST combines Containment, Eradication, and Recovery, SANS separates them into different steps. **Post-incident activity** and **Lessons learned** can be comparable, while **Identification** and **Detection and Analysis** have the same implications.

Now that we understand that the two processes are similar let's learn briefly what the different steps mean. We explain the PICERL steps as they are easier to remember by the acronym, but as described above, they are identical to the steps defined by NIST.

![dfir-sans-picerl]({{site.url_complet}}/assets/article/securite/dfir-sans-picerl.png)

1. **Preparation**: Before an incident happens, preparation needs to be done so that everyone is ready in case of an incident. Preparation includes having the required people, processes, and technology to prevent and respond to incidents.
2. **Identification**: An incident is identified through some indicators in the identification phase. These indicators are then analyzed for False Positives, documented, and communicated to the relevant stakeholders.
3. **Containment**: In this phase, the incident is contained, and efforts are made to limit its effects. There can be short-term and long-term fixes for containing the threat based on forensic analysis of the incident that will be a part of this phase.
4. **Eradication**: Next, the threat is eradicated from the network. It has to be ensured that a proper forensic analysis is performed and the threat is effectively contained before eradication. For example, if the entry point of the threat actor into the network is not plugged, the threat will not be effectively eradicated, and the actor can gain a foothold again.
5. **Recovery**: Once the threat is removed from the network, the services that had been disrupted are brought back as they were before the incident happened.
6. **Lessons Learned**: Finally, a review of the incident is performed, the incident is documented, and steps are taken based on the findings from the incident to make sure that the team is better prepared for the next time an incident occurs.



------

## DFIR Tools

The security industry has built various exciting tools to help with the DFIR process. 

These tools help save valuable time and enhance the capabilities of security professionals.

### Eric Zimmerman's tools

Eric Zimmerman is a security researcher who has written a few tools to help perform forensic analysis on the Windows platform. These tools help the registry, file system, timeline, and many other analyses. 

To learn more about these tools, you can check out the [Windows Forensics 1](https://tryhackme.com/room/windowsforensics1) and [Windows Forensics 2](https://tryhackme.com/room/windowsforensics2) rooms, where these tools are discussed concerning the different artifacts found in the Windows Operating System.

#### KAPE

[Website](https://www.kroll.com/en/services/cyber-risk/incident-response-litigation-support/kroll-artifact-parser-extractor-kape)

Kroll Artifact Parser and Extractor (KAPE) is another beneficial tool by Eric Zimmerman. This tool automates the collection and parsing of forensic artifacts and can help create a timeline of events. 

You can learn more about Kape in the TryHackMe's [KAPE room](https://tryhackme.com/room/kape).

### Autopsy

[Website](https://www.autopsy.com)

Autopsy is an open-source forensics platform that helps analyze data from digital media like mobile devices, hard drives, and removable drives. Various plugins for autopsy speed up the forensic process and extract and present valuable information from the raw data sources. 

You can learn more about Autopsy in the TryHackMe's [Autopsy room](https://tryhackme.com/room/btautopsye0).

### Volatility

[Volatility](https://volatilityfoundation.org)

Volatility is a tool that helps perform memory analysis for memory captures from both Windows and Linux Operating Systems. It is a powerful tool that can help extract valuable information from the memory of a machine under investigation. 

You can learn more about Volatility in the [Volatility room](https://tryhackme.com/room/volatility).

### Redline

[Website](https://fireeye.market/apps/211364)

Redline is an incident response tool developed and freely distributed by FireEye. This tool can gather forensic data from a system and help with collected forensic information. 

You can learn more about Redline in the [Redline room](https://tryhackme.com/room/btredlinejoxr3d).

### Velociraptor

Velociraptor is an advanced endpoint-monitoring, forensics, and response platform. It is open-source but very powerful.

You can learn more about Velociraptor in the [Velociraptor room](https://tryhackme.com/room/velociraptorhp).

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **DFIR** | Digital Forensics and Incident Response, the field that collects forensic artifacts from digital devices to investigate a security incident. |
| **Digital forensics** | The discipline of identifying forensic artifacts or evidence of human activity on digital devices. |
| **Incident response (IR)** | The process of handling a security incident, which uses forensic information to identify the activity of interest and remove the attacker. |
| **Forensic artifact** | A trace of activity on a computer, media device or smartphone that an investigator collects as evidence. |
| **NIST SP 800-61** | The NIST incident handling guide; Rev. 2 (2012), superseded by Rev. 3 in April 2025, defines four steps: Preparation, Detection and Analysis, Containment, Eradication and Recovery, and Post-incident Activity. |
| **PICERL** | The acronym of the six steps of the SANS Incident Handler's handbook: Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned. |
| **Containment** | The step that limits the effects of an incident with short-term and long-term fixes based on forensic analysis. |
| **Eradication** | The step that removes the threat from the network, after making sure its entry point is closed so the attacker cannot regain a foothold. |
| **Lessons Learned** | The final step, a review and documentation of the incident so the team is better prepared for the next one; NIST calls it Post-incident Activity. |
| **KAPE** | Kroll Artifact Parser and Extractor, a tool by Eric Zimmerman that automates the collection and parsing of forensic artifacts and helps build a timeline. |
| **Autopsy** | An open-source forensics platform that analyses data from media such as hard drives, mobile devices and removable drives, extended by plugins. |
| **Volatility** | A memory analysis tool for memory captures of Windows and Linux systems. |
| **Velociraptor** | An open-source endpoint-monitoring, forensics and response platform. |

## FAQ

> What does DFIR stand for?

Digital Forensics and Incident Response

> DFIR requires expertise in two fields. One of the fields is Digital Forensics. What is the other field?

Incident Response

> At what stage of the IR process are disrupted services brought back online as they were before the incident?

Recovery

> At what stage of the IR process is the threat evicted from the network after performing the forensic analysis?

Eradication

> What is the NIST-equivalent of the step called "Lessons learned" in the SANS process?

Post-incident Activity