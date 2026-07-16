---
layout: post
title: "Windows Domain Persistence - Golden Tickets and the Skeleton Key"
date:   2026-06-30
lang: en
locale: en-GB
categories: security network
tags: windows active-directory persistence golden-ticket skeleton-key kerberos krbtgt lsass mimikatz
description: How an attacker who already controls a Domain Controller keeps coming back - the Golden Ticket forged from the krbtgt key and the Skeleton Key LSASS backdoor, with detection and mitigation.
image: /assets/article/securite/windows-persistence/2026-06-30-windows-persistence.png
isMath: false
---

The two previous articles in this series looked at hardening authentication ([smartcards, Hello, FIDO2]({{site.url_complet}}/windows-advanced-authentication)) and protecting credentials ([LAPS, Credential Guard, Protected Users]({{site.url_complet}}/windows-credentials-protection)). This one assumes the defender has already lost: the attacker holds a Domain Controller. The question becomes *persistence*, the techniques an intruder uses to guarantee a way back even after the initial hole is closed. Two are specific to Active Directory and rest entirely on how Kerberos and LSASS work: the **Golden Ticket** and the **Skeleton Key**. Both are documented here for defensive and authorized-testing purposes, with detection and mitigation as the goal.

> **Source and currency note.** This article is based on the lecture *SOS 2021 - 05 Windows persistence* (Jean-Marc Bost, HEIG-VD, April 2021), targeting Windows Server 2016-era domains. The underlying mechanics (a stateless KDC trusting any TGT signed with the krbtgt key, an in-memory LSASS patch) are unchanged, but tradecraft and defenses have evolved: modern forged tickets favour **AES** over **RC4** and have variants designed to evade detection (**Diamond** and **Sapphire** tickets), and **Credential Guard** plus **LSA Protection** raise the bar for the LSASS access both techniques need. Treat exact Mimikatz syntax and version specifics as a 2021 snapshot.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What persistence means on a Domain Controller

An attacker who has reached the Domain Controller (DC) with high privilege wants to ensure continued access even after the original entry point is patched, the malware removed, or passwords reset. That is *persistence*.

Classical techniques apply here as on any host: install a backdoor, weaken the local configuration, create a rogue account. But a Domain Controller is the root of trust for an entire domain, and that role exposes techniques that are specific to it. The two below do not drop a file on disk that an antivirus might catch; they abuse the legitimate trust relationships of Kerberos and the LSASS authentication process. That is what makes them both powerful and instructive.

A precondition worth stating clearly: both techniques *assume the attacker has already fully compromised the DC* (SYSTEM, and the ability to read secrets or patch LSASS). They are not entry vectors. They are what an intruder does *after* winning, to keep winning.

## Golden Ticket

### Why it works

Kerberos issues a Ticket Granting Ticket (TGT) at logon; the client later presents that TGT to obtain service tickets. Two design facts combine into the vulnerability:

- **The KDC is stateless.** Domain Controllers keep no record of the TGTs they have issued. When a TGT comes back, the DC does not check a list; it simply verifies the ticket is encrypted with the right key and trusts its contents.
- **That key is the krbtgt account's password hash.** Every TGT is encrypted and signed with a key shared only among the DCs, and that key is derived from the password hash of a single special account: **krbtgt**.

The consequence is severe. Anyone who steals the krbtgt hash can **forge a TGT for any identity**, including users who do not exist, with any group memberships they choose (for example, Domain Admins). Because the DC validates only the krbtgt encryption and never consults a database of issued tickets or even checks that the user account exists, the forged ticket is accepted as genuine. This forged TGT is the **Golden Ticket**.

![Why a Golden Ticket works - the krbtgt key as root of trust]({{site.url_complet}}/assets/article/securite/windows-persistence/golden-ticket-trust-concept.png)

### How it is done

The lecture demonstrates the technique with Mimikatz. The krbtgt hash is dumped once on the DC:

```text
mimikatz# privilege::debug
mimikatz# lsadump::lsa /inject /name:krbtgt
```

Then, from any machine, a ticket is forged and injected into the current session (`/ptt` = pass-the-ticket):

```text
mimikatz# kerberos::golden /domain:[domain] /sid:[domain_sid] /rc4:[krbtgt_ntlm_hash] /user:[username] /id:[user_id] /ptt
mimikatz# misc::cmd
```

Other tooling does the same. With Metasploit:

```text
golden_ticket_create -d wad.local -u timmy -s [domain_sid] -k [krbtgt_hash] -t golden.tck
kerberos_ticket_use golden.tck
```

The critical property for persistence is in the timing: the krbtgt hash is stolen *once* on the DC, but tickets are forged *offline, later, from anywhere*, with no further contact needed to mint them. The sequence below makes that split explicit.

![Golden Ticket - from DC compromise to persistent access]({{site.url_complet}}/assets/article/securite/windows-persistence/golden-ticket-workflow.png)

### Modern note

The 2021 example uses an RC4 (`/rc4`) krbtgt hash. Current tradecraft prefers **AES** keys, both because RC4 usage is increasingly anomalous (and therefore detectable) and because AES-only domains reject RC4. Detection-aware variants have also appeared: a **Diamond Ticket** modifies a *real* TGT obtained from the DC rather than fabricating one from scratch, and a **Sapphire Ticket** borrows a real high-privilege user's PAC, both to blend in with legitimate traffic. The defensive point is unchanged: the krbtgt key is the root of trust, and its theft is catastrophic.

## Skeleton Key

All authentication in a Windows domain is performed by the **LSASS** process on the Domain Controller. If an attacker has SYSTEM on the DC, that process can be altered in memory.

The **Skeleton Key** is a backdoor that patches LSASS so it accepts a single hidden *master password* for **any** domain account, in addition to each account's legitimate password. A normal user still logs in with their real password and notices nothing; the attacker logs in as that same user (or any user) using the master password.

With Mimikatz the patch is a single command run on the DC:

```text
mimikatz# privilege::debug
mimikatz# misc::skeleton
```

Two properties define its character. First, it is **transparent**: legitimate authentication continues to work, so the backdoor is invisible to users. Second, it is **volatile**: the patch lives only in the running LSASS process and **does not survive a reboot** of the Domain Controller. That makes it a convenient short-term backdoor rather than durable persistence, though an attacker with DC access can simply re-apply it.

![Skeleton Key - patching LSASS to accept a master password]({{site.url_complet}}/assets/article/securite/windows-persistence/skeleton-key-workflow.png)

## Detection and mitigation

Both techniques converge on two defensive levers, which is why the lecture ends on them.

**Monitor LSASS debug access.** Skeleton Key requires patching LSASS, and dumping the krbtgt hash typically requires reading LSASS or replicating secrets. Debug access to the LSASS process on a Domain Controller is not a normal event; it should be logged and alerted on. The credential-protection controls from the [companion article]({{site.url_complet}}/windows-credentials-protection) raise the cost of this access directly: **LSA Protection (RunAsPPL)** blocks user-mode tampering with LSASS, and **Credential Guard** isolates the secrets so a memory read finds nothing reusable. Neither is a perfect wall (a signed kernel driver can still reach LSASS), but both turn a quiet operation into a noisy, detectable one.

**Rotate the krbtgt password.** Because the Golden Ticket is forged from the krbtgt hash, changing that password invalidates every forged (and legitimate) TGT signed with the old key. The lecture's guidance: reset krbtgt **every year and whenever a domain administrator leaves**. One subtlety matters: the reset must be performed **twice**, because the krbtgt account keeps a password history of two keys and TGTs signed with the immediately previous key remain valid until the second rotation flushes it. A single reset does not fully evict an attacker.

Beyond the lecture, modern detection also watches for Kerberos anomalies: tickets with implausible lifetimes, TGS requests (Event ID 4769) for a user with no preceding TGT request, RC4 usage in an AES domain, and authentications for accounts that do not exist in the directory.

## Conclusion

Golden Tickets and the Skeleton Key are post-compromise persistence techniques that weaponise the design of Active Directory itself rather than any software bug. The Golden Ticket exploits a stateless KDC that trusts any TGT encrypted with the krbtgt key, so stealing that one hash lets an attacker mint tickets for any identity, offline and indefinitely. The Skeleton Key patches the LSASS authentication routine on a Domain Controller to accept a universal master password while leaving legitimate logins untouched, at the cost of being volatile across reboots.

The defenses follow directly from the mechanisms. Both require privileged access to LSASS on a DC, so monitoring debug access to that process and deploying LSA Protection and Credential Guard attack the shared precondition. The Golden Ticket specifically is undone by rotating the krbtgt password, performed twice to clear the two-entry key history, on a schedule and whenever a privileged administrator departs. These techniques also sit at the end of the attack chain that the earlier articles try to prevent: strong authentication and credential protection exist precisely so that an attacker never reaches the Domain Controller from which this persistence becomes possible.

![Windows Domain Persistence mindmap]({{site.url_complet}}/assets/article/securite/windows-persistence/2026-06-30-windows-persistence.png)

## Frequently Asked Questions

**Q: What exactly is forged in a Golden Ticket, and what key makes it possible?**

A Golden Ticket is a forged Ticket Granting Ticket (TGT). It is possible because every TGT is encrypted and signed with a key derived from the password hash of the **krbtgt** account, a key shared only among the Domain Controllers. An attacker who steals the krbtgt hash can construct a TGT for any user with any group memberships and encrypt it with that key. Since the DC validates a returning TGT only by checking the krbtgt encryption, the forgery is accepted.

**Q: Why does a stateless KDC make the Golden Ticket so powerful?**

Because the Domain Controller keeps no record of the TGTs it has issued. It does not consult a list of valid tickets, and it does not re-check that the named user still exists or that the ticket was ever legitimately granted. It trusts the contents of any TGT that decrypts correctly under the krbtgt key. Statelessness means the only thing standing between an attacker and a valid-looking ticket is possession of that key, so once the key is stolen, fabricated tickets (even for non-existent users) are indistinguishable from real ones.

**Q: How does the Skeleton Key differ from the Golden Ticket in what it modifies and how durable it is?**

The Golden Ticket modifies nothing on the DC at attack time; it forges tickets offline using a previously stolen krbtgt hash, and those tickets stay valid until the krbtgt key is rotated. The Skeleton Key instead patches the running LSASS process on the DC so it accepts a hidden master password for any account. The Golden Ticket is durable (forge anytime, from anywhere, until krbtgt rotation), whereas the Skeleton Key is volatile: it lives only in memory and is lost when the DC reboots, although an attacker with DC access can re-apply it.

**Q: Why must the krbtgt password be reset twice rather than once?**

The krbtgt account retains a password history of two keys, and TGTs signed with the immediately previous key remain valid for compatibility. A single reset replaces the current key but leaves the previous one (the one the attacker may hold) still trusted. Performing the reset a second time pushes the attacker's key out of the two-entry history, invalidating tickets forged with it. Resetting only once therefore leaves a window in which a Golden Ticket still works.

**Q: Combining this article with the credential-protection one, why do LSA Protection and Credential Guard help against both persistence techniques, and where do they fall short?**

Both techniques depend on privileged access to LSASS on the Domain Controller: the Skeleton Key patches LSASS directly, and obtaining the krbtgt hash typically means reading LSASS or abusing replication from a position of LSASS-level control. LSA Protection (RunAsPPL) marks LSASS a Protected Process and blocks user-mode debugging and memory access, and Credential Guard moves the usable secrets into a VBS-isolated world so a memory dump yields nothing reusable. They therefore attack the shared precondition rather than each technique individually. They fall short because they are not absolute: a signed kernel driver can bypass RunAsPPL, Credential Guard has hardware requirements and does not cover every secret or a keylogger, and neither helps once the krbtgt hash has already been exfiltrated, at which point only rotating the key (twice) closes the Golden Ticket.

**Q: Are these techniques an initial attack vector?**

No. Both assume the attacker has already fully compromised a Domain Controller with SYSTEM-level privilege and the ability to read secrets or patch LSASS. They are persistence mechanisms used after a successful intrusion to keep access, not ways to break in. This is why prevention focuses earlier in the chain (strong authentication, credential protection, limiting privileged-account exposure): the goal is to ensure an attacker never reaches the Domain Controller where these techniques become available.

## References

- [Microsoft - krbtgt account maintenance and reset](https://learn.microsoft.com/en-us/microsoft-identity-manager/pam/how-to-reset-the-krbtgt-account-password)
- [MITRE ATT&CK T1558.001 - Golden Ticket](https://attack.mitre.org/techniques/T1558/001/)
- [MITRE ATT&CK T1556.001 - Skeleton Key (Modify Authentication Process)](https://attack.mitre.org/techniques/T1556/001/)
- [Microsoft Learn - How Credential Guard works](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/how-it-works)
- [Microsoft Learn - Configure added LSA protection (RunAsPPL)](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection)
- *SOS 2021 - 05 Windows persistence*, Jean-Marc Bost, HEIG-VD, April 2021 (source lecture)
- [Claude Code](https://claude.com/product/claude-code)
