---
layout: post
title: "Four ATT&CK Techniques for Getting Into Accounts - Valid Accounts, Brute Force, Password Guessing and Password Spraying"
date:   2026-09-09
lang: en
locale: en-GB
categories: security
tags: security threat mitre authentication credentials active-directory cybersecurity
description: How adversaries acquire credentials with Brute Force (T1110), Password Guessing (T1110.001) and Spraying (T1110.003), then abuse them as Valid Accounts (T1078).
image: /assets/article/securite/mitre-attack/2026-09-09-mitre-valid-accounts-brute-force-mindmap.png
isMath: false
---

Most intrusions do not begin with an exploit. They begin with a login. An attacker who holds a working username and password walks through the front door as a legitimate user, and everything that follows looks, at first, like normal activity. Four MITRE ATT&CK techniques describe this identity-centred path: the ways credentials are acquired, and the way they are then used.

This article covers **Brute Force** ([T1110](https://attack.mitre.org/techniques/T1110)) and two of its sub-techniques, **Password Guessing** ([T1110.001](https://attack.mitre.org/techniques/T1110/001)) and **Password Spraying** ([T1110.003](https://attack.mitre.org/techniques/T1110/003)), which are three ways to obtain credentials, together with **Valid Accounts** ([T1078](https://attack.mitre.org/techniques/T1078)), which is what an adversary does once it holds them. For each one it gives the ATT&CK definition, how adversaries carry it out, which groups and malware use it, how a defender detects it, and which mitigations apply, before showing how the acquisition and the abuse connect into one sequence.

> **Source and currency note.** Technique data is taken from the MITRE ATT&CK for Enterprise STIX dataset and reflects release **v19.2**. All four techniques are current in that release; none is deprecated or revoked.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The four techniques at a glance

Three of these techniques sit under **Credential Access**, the tactic of stealing account names and passwords. The fourth, Valid Accounts, is different: it is the *use* of legitimate credentials, and ATT&CK maps it across four tactics at once because holding a valid account helps an adversary get in, stay in, gain privilege, and avoid detection.

| Technique | ID | Tactic | Role |
|-----------|----|--------|------|
| Brute Force | [T1110](https://attack.mitre.org/techniques/T1110) | Credential Access | Parent technique for guessing or cracking passwords |
| Password Guessing | [T1110.001](https://attack.mitre.org/techniques/T1110/001) | Credential Access | Many passwords against one account |
| Password Spraying | [T1110.003](https://attack.mitre.org/techniques/T1110/003) | Credential Access | One password against many accounts |
| Valid Accounts | [T1078](https://attack.mitre.org/techniques/T1078) | Initial Access, Persistence, Privilege Escalation, Defense Evasion | Abusing legitimate credentials once obtained |

The relationship is a supply chain: the Credential Access techniques produce credentials, and Valid Accounts consumes them.

![T1110.001 Password Guessing and T1110.003 Password Spraying feed the T1110 Brute Force technique under Credential Access, which produces valid credentials that are consumed by T1078 Valid Accounts across four tactics, also fed by credential dumping and phishing]({{site.url_complet}}/assets/article/securite/mitre-attack/credential-access-techniques-concept.png)

## Brute Force (T1110)

[Brute Force](https://attack.mitre.org/techniques/T1110) is the **Credential Access** parent technique for gaining access to accounts when passwords are unknown, or when password hashes have been obtained. Without knowing a password, an adversary systematically tries candidates through a repetitive mechanism. This can happen **online**, by interacting with a service that checks each credential, or **offline**, against previously acquired data such as password hashes. It applies across essentially every platform ATT&CK tracks, from Windows and Linux to SaaS, identity providers and network devices.

Brute forcing occurs at several points in an intrusion, not only at the start. Adversaries brute force [Valid Accounts](https://attack.mitre.org/techniques/T1078) using knowledge gathered post-compromise from [OS Credential Dumping](https://attack.mitre.org/techniques/T1003), [Account Discovery](https://attack.mitre.org/techniques/T1087), or [Password Policy Discovery](https://attack.mitre.org/techniques/T1201), and they combine it with [External Remote Services](https://attack.mitre.org/techniques/T1133) for initial access. ATT&CK also notes a modern wrinkle: even a correctly guessed password may fail against a location-based conditional-access policy, which becomes its own signal.

Brute Force has four sub-techniques, distinguished by what the adversary knows and how the attempts are distributed:

- **Password Guessing (T1110.001)** — no known passwords; try many candidates online.
- **Password Cracking (T1110.002)** — recover plaintext from stolen hashes offline.
- **Password Spraying (T1110.003)** — try a few common passwords across many accounts.
- **Credential Stuffing (T1110.004)** — replay username/password pairs leaked from other breaches.

This article details the two the request named, Password Guessing and Password Spraying, which are the mirror image of each other.

### Who uses it, and how to counter it

| Type | Examples |
|------|----------|
| Groups | APT28 (G0007), Turla (G0010), Dragonfly (G0035), OilRig (G0049), APT38 (G0082), APT39 (G0087), APT41 (G0096), Fox Kitten (G0117), HEXANE (G1001), Agrius (G1030) |
| Software | CrackMapExec (S0488), PoshC2 (S0378), QakBot (S0650), Chaos (S0220), Kinsing (S0599) |

| Mitigation | ID | How it helps |
|------------|----|--------------|
| Multi-factor Authentication | [M1032](https://attack.mitre.org/mitigations/M1032) | A guessed or cracked password alone is not enough to log in |
| Password Policies | [M1027](https://attack.mitre.org/mitigations/M1027) | Long, complex, non-reused passwords make guessing and cracking infeasible |
| Account Use Policies | [M1036](https://attack.mitre.org/mitigations/M1036) | Lockout thresholds and login-hour limits cut off repeated attempts |
| User Account Management | [M1018](https://attack.mitre.org/mitigations/M1018) | Removing unnecessary and stale accounts shrinks the target set |

## Password Guessing (T1110.001)

[Password Guessing](https://attack.mitre.org/techniques/T1110/001) is used by an adversary with **no prior knowledge** of legitimate credentials. It systematically tries candidates, typically from a list of common passwords, against an account. The technique may ignore the target's complexity and lockout policies, which is its defining risk: guessing generates many authentication failures and can trigger account lockouts, making it noisy and self-limiting.

Guessing is usually aimed at management services on well-known ports. ATT&CK lists SSH (22), Telnet (23), FTP (21), SMB (139/445), LDAP (389), Kerberos (88), RDP (3389), HTTP management interfaces (80/443), MSSQL (1433), Oracle (1521), MySQL (3306), VNC (5900) and SNMP (161/162). Beyond on-premises services, adversaries target single sign-on and cloud applications that use federated authentication.

| Type | Examples |
|------|----------|
| Groups | APT28 (G0007), APT29 (G0016), VOID MANTICORE (G1055) |
| Software | Emotet (S0367), CrackMapExec (S0488), Pony (S0453), Lucifer (S0532), Xbash (S0341), HermeticWizard (S0698) |

Its mitigations are Password Policies ([M1027](https://attack.mitre.org/mitigations/M1027)), Multi-factor Authentication ([M1032](https://attack.mitre.org/mitigations/M1032)), Account Use Policies ([M1036](https://attack.mitre.org/mitigations/M1036)), and Update Software ([M1051](https://attack.mitre.org/mitigations/M1051)) to close default and vulnerable authentication paths.

## Password Spraying (T1110.003)

[Password Spraying](https://attack.mitre.org/techniques/T1110/003) inverts the guessing loop. Instead of trying many passwords against one account, the adversary tries a **single common password**, such as `Password01`, or a small list of them, against **many different accounts**. Choosing a password that satisfies the domain complexity policy, and spreading the attempts across accounts, means no individual account accumulates enough failures to lock out. It trades depth for breadth precisely to defeat the lockout defence that makes guessing risky.

Spraying targets the same management services as guessing, and it is especially associated with externally facing identity surfaces: single sign-on, federated authentication protocols, and cloud email such as Office 365. Adversaries also deliberately **throttle** their attempts, spacing them out to stay under the rate and volume thresholds that trigger alerting.

| Type | Examples |
|------|----------|
| Groups | APT28 (G0007), APT29 (G0016), APT33 (G0064), Lazarus Group (G0032), Leafminer (G0077), Chimera (G0114), Silent Librarian (G0122), HAFNIUM (G0125), HEXANE (G1001), Agrius (G1030) |
| Software | MailSniper (S0413), CrackMapExec (S0488) |

Its mitigations are Password Policies ([M1027](https://attack.mitre.org/mitigations/M1027)), Multi-factor Authentication ([M1032](https://attack.mitre.org/mitigations/M1032)) and Account Use Policies ([M1036](https://attack.mitre.org/mitigations/M1036)).

### Guessing versus spraying

The two sub-techniques are defined by opposite distributions of the same attempts, and the difference is what a defender watches for:

- **Password Guessing** concentrates many passwords on one account, so it shows up as a **spike of failures on a single account** and often as a lockout.
- **Password Spraying** spreads one password across many accounts, so no single account looks abnormal; it shows up only as a **low rate of failures with the same password across the whole directory**, visible at the identity provider rather than on any one account.

Detecting spraying therefore requires correlation across accounts, which is exactly the view a per-account lockout policy does not provide.

## Valid Accounts (T1078)

[Valid Accounts](https://attack.mitre.org/techniques/T1078) is the abuse of legitimate credentials, and it is the reason the acquisition techniques matter. Adversaries obtain and abuse the credentials of existing accounts to gain **Initial Access, Persistence, Privilege Escalation, or Defense Evasion**, which is why ATT&CK lists it under all four tactics. Compromised credentials bypass access controls and grant persistent access to externally available services such as VPNs, Outlook Web Access, network devices and remote desktop.

Several properties make this technique dangerous and hard to detect:

- **No malware required.** An adversary can operate with nothing but legitimate access, so there is no tool or payload to catch. Activity blends into normal user behaviour.
- **Inactive accounts.** Abusing the account of someone who has left the organisation evades detection, because the real owner is not present to notice anomalous activity.
- **Permission overlap.** The overlap of local, domain and cloud account permissions across systems lets an adversary pivot from account to account and system to system, escalating toward domain or enterprise administrator.

Valid Accounts has four sub-techniques by account type: Default Accounts (T1078.001), Domain Accounts (T1078.002), Local Accounts (T1078.003) and Cloud Accounts (T1078.004).

### Who uses it, and how to counter it

Valid Accounts is one of the most widely reported techniques in ATT&CK, used by dozens of groups spanning espionage and financially motivated crews, including APT28 (G0007), APT29 (G0016), Lazarus Group (G0032), Sandworm Team (G0034), FIN6 (G0037), FIN7 (G0046), OilRig (G0049) and menuPass (G0045).

Detection depends on behavioural analytics rather than signatures: correlate account activity against a baseline and flag logins that are anomalous in time, source location, or the systems accessed. Because the credentials are legitimate, the anomaly is in *how* they are used, not in *what* is used.

| Mitigation | ID | How it helps |
|------------|----|--------------|
| Multi-factor Authentication | [M1032](https://attack.mitre.org/mitigations/M1032) | A stolen password alone cannot authenticate |
| Privileged Account Management | [M1026](https://attack.mitre.org/mitigations/M1026) | Limits the damage a single compromised account can do |
| Account Use Policies | [M1036](https://attack.mitre.org/mitigations/M1036) | Restricts where and when accounts can be used |
| User Account Management | [M1018](https://attack.mitre.org/mitigations/M1018) | Disables stale and inactive accounts before they are abused |
| Password Policies | [M1027](https://attack.mitre.org/mitigations/M1027) | Reduces the odds credentials are guessable in the first place |
| Active Directory Configuration | [M1015](https://attack.mitre.org/mitigations/M1015) | Hardens the directory against account pivoting |
| Privileged Account Management and User Training | M1026 / [M1017](https://attack.mitre.org/mitigations/M1017) | Reduce exposure and reuse of high-value accounts |

## How they chain together

The four techniques form a supply chain for access. An operator enumerates accounts and exposed services, then chooses an acquisition method based on the defences in place: where lockout policies are enforced, spraying avoids them; where they are not, or where password hashes are already in hand, guessing and cracking apply. A successful attempt yields valid credentials, which are then used under Valid Accounts to authenticate as a legitimate user, persist, escalate across the overlap of local, domain and cloud accounts, and blend into normal activity.

![Activity flow from enumerating accounts, choosing password spraying when lockout is enforced or guessing and cracking otherwise, to authenticating as a valid account, then persisting and escalating without malware]({{site.url_complet}}/assets/article/securite/mitre-attack/credential-attack-lifecycle-workflow.png)

The chain has one dominant choke point. Multi-factor authentication appears in the mitigation list of all four techniques, because it breaks the link between *holding a password* and *logging in*. An adversary can still guess, spray, or steal a password, but the credential no longer buys access on its own. Everything after that step in the diagram depends on the credential working, so the strongest single defence is placed exactly where acquisition would otherwise become abuse.

## Detection and mitigation summary

Because these techniques abuse authentication itself, most controls are shared, and they reinforce each other:

- **Multi-factor authentication (M1032)** is the through-line: it defends acquisition and abuse together.
- **Password policies (M1027)** raise the cost of guessing, cracking and spraying by removing weak and reused passwords.
- **Account use policies (M1036)** add lockout thresholds and login-hour and location limits, which blunt guessing directly and give spraying a rate ceiling to trip over.
- **Privileged and user account management (M1026, M1018)** shrink the target set and cap the value of any one compromised account, and disabling stale accounts removes the quiet targets Valid Accounts favours.

Detection differs by technique: guessing shows as failure spikes and lockouts on single accounts, spraying shows only in cross-account correlation at the identity provider, and Valid Accounts shows as behavioural anomalies in otherwise legitimate sessions.

## Conclusion

Valid Accounts, Brute Force, Password Guessing and Password Spraying describe one identity-centred path into an environment: acquire a working credential, then use it as a legitimate user. Guessing and spraying are opposite distributions of the same attempts, one deep on a single account and one wide across many, and each is tuned to the presence or absence of a lockout policy. Valid Accounts is what turns an acquired password into access, persistence and privilege, and it is hard to detect precisely because nothing about it is malware. The controls converge on a small set, with multi-factor authentication the one that appears against all four, because it separates knowing a password from being able to log in.

![Mindmap of the four ATT&CK techniques covering Brute Force and its sub-techniques, Password Guessing, Password Spraying, Valid Accounts and its account types, and the shared defensive controls]({{site.url_complet}}/assets/article/securite/mitre-attack/2026-09-09-mitre-valid-accounts-brute-force-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Credential Access** | The ATT&CK tactic covering techniques for stealing account names and passwords, such as Brute Force. |
| **Brute Force** | Systematically trying password candidates against a service or offline against hashes until one works. |
| **Password Guessing** | Brute forcing many candidate passwords against a single account, with no prior credential knowledge; risks lockout. |
| **Password Spraying** | Trying one common password across many accounts to acquire credentials while avoiding per-account lockout. |
| **Password Cracking** | Recovering a plaintext password offline from a stolen hash, the T1110.002 sub-technique. |
| **Credential Stuffing** | Replaying username/password pairs leaked from other breaches, the T1110.004 sub-technique. |
| **Valid Accounts** | Abusing legitimate credentials for initial access, persistence, privilege escalation or defence evasion. |
| **Account lockout** | A policy that disables an account after a set number of failed logins; the defence spraying is designed to evade. |
| **Federated authentication / SSO** | A single identity used across many applications; a high-value target for spraying because one credential unlocks many services. |
| **Multi-factor authentication (MFA)** | Requiring a second factor beyond the password, which breaks the link between a stolen password and a successful login. |

### Security Implementation Checklist

The rows below are defender-facing controls; each is a property a hardened environment should hold, paired with what an adversary gains if it does not.

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Multi-factor authentication is enforced on all externally reachable services (VPN, webmail, RDP, SSO). | A guessed, sprayed, or stolen password logs in directly (T1078). |
| ☐ | Password policy forbids common and breached passwords and requires sufficient length. | Common-password guessing and spraying succeed against weak accounts. |
| ☐ | Account lockout or throttling is enforced, with smart lockout that also detects distributed attempts. | Guessing runs unimpeded, and spraying stays under per-account thresholds. |
| ☐ | Authentication failures are correlated across accounts at the identity provider, not only per account. | Password spraying is invisible because no single account looks abnormal. |
| ☐ | Inactive and departed-user accounts are disabled and reviewed on a schedule. | Abandoned accounts give adversaries quiet, unmonitored access (T1078). |
| ☐ | Privileged accounts are separated from daily-use accounts and their sessions restricted. | One compromised credential pivots straight to domain or enterprise admin. |
| ☐ | Conditional access restricts logins by location, device, and risk. | A valid credential is usable from anywhere, with no second signal to flag. |
| ☐ | Sign-in logs feed behavioural analytics that baseline normal account use. | Legitimate-looking abuse of valid credentials goes undetected. |

## Frequently Asked Questions

**Q: What is the difference between Password Guessing and Password Spraying?**

They distribute the same attempts in opposite ways:

- **Password Guessing (T1110.001)** tries many candidate passwords against a single account. It risks triggering that account's lockout, so it is noisy and self-limiting.
- **Password Spraying (T1110.003)** tries one common password across many accounts. Because no single account sees more than one or two failures, it slips under lockout thresholds.

Guessing goes deep on one target; spraying goes wide across many. Spraying exists specifically to defeat the account-lockout defence that makes guessing risky.

**Q: Why is Valid Accounts listed under four different tactics?**

Because a legitimate credential is useful at every stage. It provides **Initial Access** through remote services, **Persistence** by giving a durable way back in, **Privilege Escalation** when the account has or can reach higher rights, and **Defense Evasion** because activity performed as a real user, with no malware, blends into normal behaviour. ATT&CK maps a technique to every tactic its use can satisfy, and Valid Accounts satisfies all four.

**Q: How does Brute Force relate to Valid Accounts?**

Brute Force is an acquisition method and Valid Accounts is the use of what it acquires. The Credential Access techniques (guessing, cracking, spraying, stuffing) produce a working username and password; Valid Accounts is then the technique of authenticating and operating with those credentials. The ATT&CK description of Brute Force explicitly points at Valid Accounts as its objective, and the same credentials can come instead from credential dumping or phishing.

**Q: Why is offline password cracking harder to detect than online guessing?**

Online guessing and spraying interact with a live service, so every attempt produces an authentication event that a defender can log, count and alert on. Offline cracking (T1110.002) runs against a stolen hash on the attacker's own hardware, producing no events in the victim environment at all. The defence therefore shifts: online attacks are countered with lockout, throttling and MFA, while offline cracking is countered upstream, by preventing hash theft and by using slow, salted hashing so recovery is infeasible.

**Q: Which single control most reduces exposure across all four techniques?**

Multi-factor authentication. It is the only mitigation ATT&CK lists against all four, because it breaks the assumption every one of them relies on: that a correct password equals access. An adversary can still guess, spray, crack or steal a password, but without the second factor the credential does not authenticate. It must be paired with password policies and cross-account monitoring, because MFA reduces the value of a stolen password without stopping the attempts that produce failure telemetry.

**Q: A burst of failed logins hits one account, then stops. Guessing or spraying?**

That pattern points to **guessing**, because the failures are concentrated on a single account, which is the guessing signature and the reason it often ends in a lockout. Spraying would instead show a low, steady rate of failures using the same password spread across many accounts, with no single account standing out. Confirming spraying requires correlating failures by password across the directory at the identity provider, a view that per-account monitoring alone does not provide.

## References

- [T1078 Valid Accounts](https://attack.mitre.org/techniques/T1078) — MITRE ATT&CK for Enterprise
- [T1110 Brute Force](https://attack.mitre.org/techniques/T1110) — MITRE ATT&CK for Enterprise
- [T1110.001 Brute Force: Password Guessing](https://attack.mitre.org/techniques/T1110/001) — MITRE ATT&CK for Enterprise
- [T1110.003 Brute Force: Password Spraying](https://attack.mitre.org/techniques/T1110/003) — MITRE ATT&CK for Enterprise
- [T1003 OS Credential Dumping](https://attack.mitre.org/techniques/T1003) and [T1133 External Remote Services](https://attack.mitre.org/techniques/T1133) — related credential and access techniques
- [MITRE ATT&CK](https://attack.mitre.org) — the knowledge base, tactics and techniques

### Related articles

- [Three ATT&CK Techniques Behind the Ransomware Endgame - Service Stop, Disable or Modify Tools, and Indicator Blocking]({{site.url_complet}}/2026/09/09/mitre-attack-service-stop-impair-defenses/)
- [Windows Advanced Authentication - Smartcards, Virtual Smartcards and Hello for Business]({{site.url_complet}}/2026/06/30/windows-advanced-authentication/)
- [Windows Credentials Protection - LAPS, WDigest, LSA Protection, Credential Guard and Protected Users]({{site.url_complet}}/2026/06/30/windows-credentials-protection/)
- [Recover your passwords with Hashcat]({{site.url_complet}}/2022/11/13/hashcat-summary/)
- [HOTP - An HMAC-Based One-Time Password Algorithm (RFC 4226)]({{site.url_complet}}/2026/07/20/hotp-hmac-one-time-password-rfc4226/)
