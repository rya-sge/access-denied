---
layout: post
title: Digital Forensics and Incident Response (DFIR) - Introduction
date:   2025-01-15
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

NIST has defined a process in their [SP-800-61 Incident Handling guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf), which has the following steps:

1. Preparation
2. Detection and Analysis
3. Containment, Eradication, and Recovery
4. Post-incident Activity

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

You can learn more about Redline in the [Velociraptor room](https://tryhackme.com/room/velociraptorhp).

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