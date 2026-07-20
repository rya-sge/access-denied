---
layout: post
title: "PCI PTS POI v7.0 — Securing the Payment Terminal at the Point of Interaction"
date:   2026-07-20
lang: en
locale: en-GB
categories: security
tags: pci poi pin-pad payment terminal sred tamper-resistance cryptography
description: A technical walkthrough of the PCI PTS POI Modular Security Requirements v7.0, the standard that governs payment terminals, from tamper resistance and PIN protection to account-data encryption, wireless security, and third-party applications.
image: /assets/article/securite/pci-poi/pci-pts-poi-security-requirements.png
isMath: false
---

The device a cardholder touches at a checkout counter, an unattended fuel pump, or a transit gate is the Point of Interaction (POI): the PIN pad, the card reader, and the secure processor that first handle a PIN and account data. If that terminal can be opened, overlaid, or coaxed into revealing a PIN, every downstream control is moot. The [PCI PTS POI Modular Security Requirements v7.0](https://www.pcisecuritystandards.org/document_library/), published by the PCI Security Standards Council in May 2025, is the standard that defines what such a terminal must do to be approved for the payments industry.

This article walks through that standard: the device classes it covers, the four evaluation modules, the physical and logical controls that protect PINs and account data, the attack-potential methodology behind its tamper thresholds, and the features new to v7.0 such as third-party application isolation and a TLS 1.3 requirement. It is a companion to the backend side of the same PCI PTS family, the PCI PTS HSM standard that governs the Hardware Security Modules which verify these transactions.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What a POI Device Is and What Gets Evaluated

A POI device is the merchant-facing endpoint of a payment. Where an HSM sits in a data centre and verifies PINs, the POI is the terminal in the field that captures them. The standard evaluates several product categories:

- **PED or UPT POI devices.** Complete terminals a merchant can use as-is for PIN transactions, both attended point-of-sale devices and unattended payment terminals (UPTs) such as vending machines, automated fuel dispensers, and kiosks.
- **Non-PIN acceptance POI devices**, evaluated only for account-data protection rather than PIN entry.
- **Encrypting PIN pads (EPPs)** that are integrated into POS terminals or ATMs.
- **Secure components for POS terminals**, which are integrated into a final solution: OEM PIN-entry devices, secure (encrypting) card readers (SCRs), and secure card readers with PIN (SCRPs).

Like its HSM sibling, the standard is deliberately modest about its own reach. It is a risk-reduction instrument, defined so the cost of an attack exceeds its benefit, and its controls are drawn from existing ISO, ANSI, NIST, FIPS, and EMV standards. Its life-cycle concern also has a hard boundary: it covers the device only up to the point of initial key loading of payment transaction keys, or up to the facility of initial deployment. After that, responsibility passes to the acquiring institution under the PCI PIN Security Requirements.

## The Four Evaluation Modules

Version 7.0 groups its requirements into four evaluation modules, and a device is assessed against the subset that matches its architecture:

- **Module 1 — Physical and Logical Requirements.** Section A (physical) and Section B (logical). The core of the standard.
- **Module 2 — POS Terminal Integration.** Section C, which governs how previously approved components are combined into an integrated terminal without weakening it.
- **Module 3 — Communications and Interfaces.** Section D, covering protocols, wireless links, and open-protocol exposure to public networks.
- **Module 4 — Life Cycle Security.** Section E (manufacturing) and Section F (between manufacturer and initial deployment). Always applicable.

Each requirement is answered Yes, No, or N/A by a test laboratory, and an N/A is acceptable only when another requirement option provides equivalent coverage or the governed characteristic is genuinely absent from the device. The modular structure exists so that a vendor can reuse the approval of an already-certified card reader or secure processor inside a new terminal, rather than re-evaluating every component from scratch.

## Module 1, Section A — Physical Security

The physical requirements defend a terminal that an attacker can touch, overlay, or open. As in the HSM standard, the foundation is tamper detection and response: requirement A1 mandates mechanisms that make the device immediately inoperable and erase sensitive data on physical penetration, explicitly protecting against drills, lasers, chemical solvents, prying covers, splitting the casing at its seams, and exploiting ventilation openings.

The difficulty of an attack is graded with an **attack-potential** score inherited from the Common Criteria, which aggregates the time, expertise, target knowledge, opportunity, and equipment an attack requires. Two numbers appear on most requirements: a combined value for *identification and initial exploitation*, and a smaller floor for the *initial exploitation* phase alone. The split matters because discovering an attack is usually far harder than repeating it, and a control is only sound if repetition is also expensive. The thresholds vary by the sensitivity of what is being protected, which is where this standard is richer than the HSM one:

- **A2 — keypad bugging.** A keypad used for PIN entry must resist a key-press-disclosing bug to an attack potential of at least **26**, floor **13**, excluding the IC card reader. A keypad used for manual PAN entry but not PIN entry (a non-PED) needs only **16**, floor **8**.
- **A4 — sensitive functions.** Unauthorized modification of sensitive functions or data requires at least **26**, floor **13**.
- **A6 and A7 — key extraction by penetration and by emanation.** Determining a PIN-security-related secret or private key requires at least **35**, floor **15**. For an SRED-enabled device, determining an account-data key requires at least **26**, floor **13**.
- **A13 — card reader.** Penetrating the ICC reader to alter it requires at least **20**, floor **10**; an SCRP requires **26**, floor **13**.
- **A15 — biometric reader.** New in v7.0, tampering with a biometric reader's hardware or software requires at least **20**, floor **10**.

The remaining Section A requirements close specific attack channels. A3 requires resistance to environmental and operational manipulation such as out-of-range temperature or voltage. A5 and A7 address side channels, requiring that a PIN digit cannot be recovered by monitoring sound, electromagnetic emissions, power consumption, or timing, even with the cooperation of a sales clerk. A9 requires a means to deter visual observation ("shoulder surfing") of PIN entry. Account data gets its own chain: A10 protects magnetic-stripe and contactless data on entry to an attack potential of 16 (floor 8), A11 requires account data to be encrypted immediately on entry or entered in cleartext only into the secure controller, and A12 through A14 ensure that integrating a card reader creates no new path to the account data and that the card slot is in the cardholder's view to expose skimming bugs.

## Module 1, Section B — Logical Security

Section B constrains the terminal's behaviour even for a legitimate interface. Its twenty-six requirements protect two assets: the PIN, and (for SRED devices) the account data.

The diagram below shows how these controls surround the sensitive material inside the terminal's secure perimeter.

![PCI POI terminal components and trust boundary]({{site.url_complet}}/assets/article/securite/pci-poi/pci-poi-terminal-anatomy-concept.png)

**PIN confidentiality.** B3 requires that the device never displays or otherwise indicates the value of an entered PIN digit: any on-screen array shows only non-significant symbols such as asterisks, and if key presses are accompanied by audible tones, the tone for every digit is indistinguishable. B4 requires that sensitive data is retained no longer than strictly necessary, with the online PIN encrypted immediately after the cardholder signals completion, and internal buffers of full track data cleared on completion or timeout. B8 requires characteristics that deter exhaustive PIN determination, and B14 keeps other transaction data entry a clearly separate operation from PIN entry so a cardholder is never tricked into typing a PIN into a non-PIN field.

**Key handling.** This is the same discipline the HSM standard imposes, expressed for a terminal:

- **B9 — key management.** Conforms to ISO 11568 and/or ANSI X9.24, and must support key blocks as defined in DTR 77, the interoperable key-wrapping format (ANSI X9.143, formerly TR-31) that binds a key to its usage attributes.
- **B11 — PIN encryption.** Uses a PIN-encryption technique included in ISO 9564.
- **B12 — key separation.** It is not possible to encrypt or decrypt arbitrary data with any PIN-encryption, account-data, data-encrypting, or key-encrypting key, and these four key types must hold different values.
- **B13 — no cleartext leakage.** No mechanism outputs a cleartext secret or private key, encrypts a key under a disclosable key, or moves a cleartext key from a higher-security component to a lower-security one.
- **B18 — no key misuse.** When multiple PIN-encryption keys exist and the key can be selected externally, the device prevents unauthorized key replacement and key misuse.

**Integrity and least privilege.** B1 requires self-tests on start-up and at least daily, with memory reinitialised at least every 24 hours and fail-secure behaviour on failure. B2 requires cryptographically authenticated firmware updates, with any update failing the check rejected and deleted. B5 and B6 require authentication for sensitive services and limits on the number of actions and a time bound before the device returns to normal mode. B7 requires an assessed random number generator. B17 requires that the operating system contains only necessary components, runs with least privilege, and (new in v7.0) enforces mandatory access controls in an enforcing mode. B20 requires a published security policy that lists the roles and the services available to each role in a deterministic tabular format, confirming the device has no hidden functionality.

**Third-party applications.** A theme new to v7.0 is running untrusted code safely. B2.1 and B2.2 require that the firmware authenticates payment applications loaded onto the security processor, with the signing process performed under dual control using a secure cryptographic device. B2.3 requires that third-party applications must be signed and must not run in execution environments that can access cleartext account data. B16.1 requires segregation between software security domains, and B16.2 obliges the vendor to give application developers clear guidance so their code cannot leak cleartext data or over-retain account data.

**Secure Reading and Exchange of Data (SRED).** Requirements B23 through B26 govern account-data protection. B23 forbids any mechanism to output cleartext account data in encrypting mode and bars cleartext account data from environments that run third-party applications, even via whitelists; B23.1 restricts release of cleartext account data to applications authenticated under B2.1. B24 requires that surrogate PAN values (tokens) cannot be reversed to the original PAN, using a keyed-hash function where hashing is used, and B25 deters exhaustive PAN determination. B21 handles the subtle case of PIN protection in transit between the PIN-encrypting device and the ICC reader, requiring ISO 9564 enciphering whenever the PIN block crosses an unprotected boundary, and B22 requires that any remote administration access is cryptographically authenticated.

## Module 2 — POS Terminal Integration

Module 2 (Section C) exists because a modern terminal is assembled from separately approved parts. Its purpose is to ensure that combining previously approved components, such as a card reader, display, keypad, or secure processor, does not create a device weaker than its pieces.

C1.1 requires that integrating an approved secure component does not impair the overall PIN-protection level, and C1.2 targets a physical attack specific to terminals: fitting a fraudulent overlay over the PIN pad to capture key presses. Resisting an overlay must require an attack potential of at least 18, floor 9. On the POS-terminal side, C2.1 requires that integration creates no new attack path to the PIN, C2.2 requires mechanisms against card-capture attacks such as the Lebanese Loop (a sleeve that traps the inserted card for later retrieval), and C2.3 requires clear segregation between secure and non-secure components. C2.4 requires that the terminal enforces, cryptographically, the correspondence between what the display shows the cardholder and the actual operating state of the PIN-entry device, so a compromised store controller cannot silently switch the device into PIN-harvesting mode behind a benign prompt. C2.5 requires that a PIN-accepting terminal has only one payment-card PIN-acceptance interface, with any secondary keyboard prevented from being used for PIN entry.

The physical and logical attacks these controls address, and the requirements that counter them, are summarised below.

![PCI POI attack surface and countering requirements]({{site.url_complet}}/assets/article/securite/pci-poi/pci-poi-attack-surface-concept.png)

## Module 3 — Communications and Interfaces

Module 3 (Section D) governs how a terminal talks to the outside world, an attack surface that has grown as terminals moved onto IP networks and wireless links. The **Open Protocols** approach requires the vendor to declare, on a Protocol Declaration Form, every public-domain protocol and interface the device exposes, so the laboratory can assess each for known vulnerabilities.

D1 through D6 require that all protocols and interfaces are accurately identified, documented, and shipped with secure default configurations and key-management guidance. The asset-flow requirements then impose the cryptographic properties of a network channel:

- **D7 — confidentiality** of data over a network, using appropriate key sizes and keys established by sound key management (NIST SP 800-21, ISO 11568).
- **D8 — integrity**, provided by a MAC as defined in ISO 16609 or by a digital signature, with hashing from the SHA-2 family (SHA-224 through SHA-512).
- **D9 — authenticated, mutually authenticated sessions** using a declared security protocol, with the device verifying the validity and authenticity of the public keys it receives and holding only trusted-CA or acquirer-verified certificates in its trust store. New in v7.0, a device that implements an IP stack must support TLS 1.3 or higher.
- **D10 and D11 — replay detection and session management**, keeping the number of open sessions to the minimum and closing them promptly.

Wireless links get dedicated treatment: D12 requires Bluetooth to be secured against eavesdropping and man-in-the-middle attacks, D13 requires Wi-Fi to be securely configured with vulnerable protocols disabled, and D14 requires that any wireless interface which does not meet those specific requirements is physically and cryptographically isolated.

## Module 4 — Life Cycle Security

The final module protects the terminal before it reaches a merchant, on the principle that a device compromised in the factory or in transit defeats every runtime control. It establishes a chain of custody from design to initial key loading, illustrated below in the sequence a PIN follows once the device is in service.

![PIN transaction flow inside a PCI POI terminal]({{site.url_complet}}/assets/article/securite/pci-poi/pci-poi-pin-transaction-workflow.png)

Section E covers **manufacturing**. Change control triggers re-certification when security characteristics change (E1); firmware is inspected through an auditable process and verified free of hidden functions (E2), then protected against modification throughout manufacturing under dual control (E3). Assembly uses only certified components (E4), production software moves under dual control (E5), and a unique device secret is installed during manufacturing so the key-loading facility can authenticate the device (E7). Version 7.0 strengthens the vulnerability lifecycle: E10 requires the vendor to run an effective internal process for detecting vulnerabilities across all declared interfaces, E11 requires an actual vulnerability assessment supported by analysis, a public-domain survey, and testing, and E12 requires documented vulnerability-disclosure measures that distribute information and mitigations in a timely fashion.

Section F covers the interval **between the manufacturer and initial deployment**. The device is protected by tamper-detection features with authenticity-validation instructions provided to customers, or shipped under auditable controls that account for every device at every point in time, for example serialised tamper-evident packaging with physical inspection on receipt (F1). Accountability transfers formally from party to party along the shipping chain, and absent an agreement the vendor remains responsible (F2). In transit the device carries a secret that self-erases on any physical or functional alteration and can be verified by the key-loading facility but not by unauthorized personnel (F3). Each device carries a unique visible identifier, its model name and hardware version, also retrievable by query (F7), and the vendor maintains a manual recording the full life cycle of the device's security-related components, including production, whereabouts, repair, removal from operation, and loss or theft (F8).

## What Changed in v7.0

Version 7.0 (May 2025) evolves the standard along the lines that matter as terminals become general-purpose networked computers running third-party code:

- **Stronger cryptography.** Cryptography used for device-security purposes must implement an effective key strength of 128 bits or stronger.
- **Refined key-extraction thresholds.** Non-invasive attacks are modelled with distinct attack potentials for PIN keys and account-data keys.
- **Biometric readers.** A new requirement (A15) sets a tamper threshold for biometric reader hardware and software.
- **Third-party applications.** New requirements govern how untrusted applications are signed, isolated, and kept away from cleartext account data.
- **Mandatory access controls.** The operating system must enforce MAC in an enforcing mode.
- **TLS 1.3.** A device that implements an IP stack must support TLS 1.3 or higher.

## Requirements Checklist

The standard is written as a form: a laboratory marks each requirement Yes, No, or N/A. The tables below condense every requirement into a one-line checklist, grouped by section, so the catalogue can be used directly as an evaluation or procurement aid. A device is assessed only against the sections that match its architecture, and an N/A is acceptable when a requirement's characteristic is genuinely absent or another option provides equivalent coverage. Attack-potential thresholds are shown as ≥ combined (≥ exploitation floor).

### Module 1, Section A — Physical Security

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | A1 | Tamper detection and response erase sensitive data on penetration (drills, lasers, solvents, seams, vents). |
| ☐ | A2 | No way to defeat the tamper mechanism and insert a key-press bug; PIN keypad ≥ 26 (≥ 13), non-PED PAN keypad ≥ 16 (≥ 8). |
| ☐ | A3 | Security is not compromised by altering environmental or operational conditions (temperature, voltage). |
| ☐ | A4 | Sensitive functions used only in protected areas; modification requires ≥ 26 (≥ 13), excluding IC/biometric reader. |
| ☐ | A5 | No practical way to determine a PIN digit by monitoring sound, EM, power, or timing; ≥ 26 (≥ 13). |
| ☐ | A6 | PIN keys by penetration require ≥ 35 (≥ 15); SRED account-data keys ≥ 26 (≥ 13). |
| ☐ | A7 | PIN keys by emanations require ≥ 35 (≥ 15); SRED account-data keys ≥ 26 (≥ 13). |
| ☐ | A8 | Altering prompts to harvest a PIN via non-PIN entry requires ≥ 18 (≥ 9). |
| ☐ | A9 | The device provides a means to deter visual observation of PIN entry. |
| ☐ | A10 | Account data is protected on entry (magnetic-stripe, contactless); accessing cleartext requires ≥ 16 (≥ 8). |
| ☐ | A11 | All account data is encrypted immediately on entry or entered in cleartext only into the secure controller. |
| ☐ | A12 | Integrating an approved card reader creates no new attack path to the account data. |
| ☐ | A13 | Penetrating the ICC reader requires ≥ 20 (≥ 10); no card plus foreign object share the slot; SCRP ≥ 26 (≥ 13). |
| ☐ | A14 | The card-insertion opening is in full view of the cardholder; skimming wires are observable. |
| ☐ | A15 | Modifying the biometric reader's hardware or software requires ≥ 20 (≥ 10). |

### Module 1, Section B — Logical Security

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | B1 | Self-test of integrity and authenticity on start-up and at least daily; fail secure; memory reinitialised ≥ every 24 h. |
| ☐ | B2 | Firmware updates are cryptographically authenticated; failed updates are rejected and deleted. |
| ☐ | B2.1 | The firmware authenticates payment applications loaded onto the security and application processors. |
| ☐ | B2.2 | A documented signing process runs under dual control, signing only via a secure cryptographic device. |
| ☐ | B2.3 | Third-party applications must be signed and cannot run where cleartext account data is accessible. |
| ☐ | B3 | The device never displays or indicates an entered PIN digit; feedback uses only non-significant symbols and uniform tones. |
| ☐ | B4 | Sensitive data is not over-retained; the online PIN is encrypted immediately; track buffers clear on completion/timeout. |
| ☐ | B5 | Access to sensitive services requires authentication; entering or exiting them does not reveal sensitive data. |
| ☐ | B6 | The number of sensitive-service actions is limited and time-bounded before a forced return to normal mode. |
| ☐ | B7 | Any random number generator is assessed to produce sufficiently unpredictable output. |
| ☐ | B8 | The device deters exhaustive PIN determination. |
| ☐ | B9 | Key management conforms to ISO 11568 / ANSI X9.24 and supports key blocks (DTR B9). |
| ☐ | B10 | Account data is encrypted using ANSI X9 / ISO-approved algorithms (AES, TDES) and modes. |
| ☐ | B11 | The PIN-encryption technique is one included in ISO 9564. |
| ☐ | B12 | Keys cannot encrypt/decrypt arbitrary data; PIN, account, data, and key-encipherment keys hold different values. |
| ☐ | B13 | No mechanism outputs a cleartext key or PIN, or transfers a cleartext key to a lower-security component. |
| ☐ | B14 | Non-PIN transaction data entry is a clearly separate operation from PIN entry. |
| ☐ | B15 | Cryptographic mechanisms ensure display authenticity and prevent prompt modification. |
| ☐ | B16 | Multiple applications enforce separation; none can tamper with another or the OS. |
| ☐ | B16.1 | Lesser-security or non-vendor software is segregated between software security domains. |
| ☐ | B16.2 | The vendor gives developers guidance so applications cannot leak cleartext data or over-retain account data. |
| ☐ | B17 | The OS holds only necessary software, runs least-privileged, and enforces mandatory access controls (enforcing mode). |
| ☐ | B18 | With externally selectable PIN-encryption keys, the device prevents unauthorized key replacement and misuse. |
| ☐ | B19 | The vendor provides documented guidance for integrating any secure component into a POI terminal. |
| ☐ | B20 | A published security policy defines roles and per-role services in a deterministic table; no hidden functionality. |
| ☐ | B21 | The PIN block is enciphered per ISO 9564 whenever it crosses an unprotected boundary to the ICC reader. |
| ☐ | B22 | Remote administration access is cryptographically authenticated and denied if authenticity is unconfirmed. |
| ☐ | B23 | In encrypting mode, no mechanism outputs cleartext account data, including to third-party environments or whitelists. |
| ☐ | B23.1 | Cleartext account data is released only to applications authenticated under B2.1, never to third-party apps. |
| ☐ | B24 | Surrogate PAN values cannot be reversed to the original PAN; a keyed-hash function is used where hashing applies. |
| ☐ | B25 | The device deters exhaustive PAN determination. |
| ☐ | B26 | Secure enablement tokens from the attestation and monitoring system are required for an SCRP to process payments. |

### Module 2, Section C — POS Terminal Integration

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | C1.1 | Integrating an approved secure component does not reduce the overall PIN-protection level. |
| ☐ | C1.2 | The PIN pad and its surround resist a fraudulent overlay; an overlay attack requires ≥ 18 (≥ 9). |
| ☐ | C2.1 | Integrating an approved secure component into the terminal creates no new attack path to the PIN. |
| ☐ | C2.2 | Mechanisms prevent card-capture attacks such as the Lebanese Loop. |
| ☐ | C2.3 | Secure and non-secure components in the same device are clearly segregated. |
| ☐ | C2.4 | The terminal cryptographically enforces correspondence between the display and the PIN-entry operating state (≥ 18, ≥ 9). |
| ☐ | C2.5 | The terminal has one PIN-acceptance interface; any secondary keyboard is barred from PIN entry. |

### Module 3, Section D — Communications and Interfaces

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | D1 | All protocols and interfaces are accurately identified; public-domain ones appear on the Protocol Declaration Form. |
| ☐ | D2 | Functionality is not influenced by logical anomalies that could output a cleartext PIN or sensitive data. |
| ☐ | D3 | Security guidance describes how each accessible interface's protocols and interfaces must be used. |
| ☐ | D4 | Guidance defines a secure default configuration for each protocol and interface. |
| ☐ | D5 | Key-management guidance covers key properties, responsibilities, and secure use including certificate status. |
| ☐ | D6 | All security protocols are declared, with implementation and use documentation provided. |
| ☐ | D7 | Network data confidentiality uses appropriate key sizes and soundly established keys (NIST SP 800-21, ISO 11568). |
| ☐ | D8 | Network data integrity is provided by a MAC (ISO 16609) or a signature, hashing with SHA-224 to SHA-512. |
| ☐ | D9 | Sessions are mutually authenticated over a declared protocol with verified public keys; IP stacks support TLS 1.3+. |
| ☐ | D10 | The device detects message replay and handles the exceptions securely. |
| ☐ | D11 | Session management tracks connections, minimises active sessions, and closes them promptly. |
| ☐ | D12 | Bluetooth is secured against eavesdropping and man-in-the-middle attacks (or D14 applies). |
| ☐ | D13 | Wi-Fi is securely configured with vulnerable protocols disabled (or D14 applies). |
| ☐ | D14 | Wireless interfaces not meeting D12/D13 are physically and cryptographically isolated. |

### Module 4, Section E — Life Cycle During Manufacturing

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | E1 | Change control triggers re-certification when physical or functional security characteristics change. |
| ☐ | E2 | Firmware is inspected through an auditable process and verified free of hidden or undocumented functions. |
| ☐ | E3 | Certified firmware is protected against modification throughout manufacturing (dual control or crypto auth). |
| ☐ | E4 | Assembly uses only certified hardware components, with no unauthorized substitutions. |
| ☐ | E5 | Production software is transported, stored, and loaded under dual control. |
| ☐ | E6 | Between production and shipment, devices are stored in a protected area or sealed tamper-evident packaging. |
| ☐ | E7 | The device is authenticated at key loading or deployment via a unique manufacturing secret or public-key method. |
| ☐ | E8 | Development-security measures and documentation protect the integrity of security-related components. |
| ☐ | E9 | Controls govern repair at authorized facilities, including tamper-mechanism reset and subsequent inspection. |
| ☐ | E10 | Internal processes effectively detect vulnerabilities across all declared interfaces. |
| ☐ | E11 | A vulnerability assessment (analysis, public-domain survey, testing) confirms no exploitable protocol/interface flaws. |
| ☐ | E12 | Documented vulnerability-disclosure measures distribute vulnerability information and mitigations in a timely way. |

### Module 4, Section F — Between Manufacturer and Deployment

| Check | # | Requirement |
|:---:|:---:|------------|
| ☐ | F1 | The device has tamper detection with authenticity-validation docs, or ships under fully accountable controls. |
| ☐ | F2 | Accountability is transferred formally along the shipping chain; absent an agreement, the vendor remains responsible. |
| ☐ | F3 | In transit the device carries a secret that self-erases on alteration, verifiable only by the key-loading facility. |
| ☐ | F4 | Development-security documentation lets the key-loading facility assure component authenticity. |
| ☐ | F5 | If the manufacturer loads initial keys, it verifies the authenticity of security-related components. |
| ☐ | F6 | If it does not, the manufacturer provides the key-loading facility the means to verify authenticity. |
| ☐ | F7 | Each device has a unique visible identifier (model and hardware version), also retrievable by query. |
| ☐ | F8 | The vendor maintains a manual recording the full life cycle (production, whereabouts, repair, removal, loss/theft). |

## Conclusion

The PCI PTS POI v7.0 requirements describe a terminal defined by what it withholds. It withholds the value of a PIN from its own display, withholds cleartext keys and account data from anything outside its secure perimeter, withholds trust from unsigned firmware and unauthenticated third-party code, and withholds its secrets from an attacker who drills, overlays, or eavesdrops on it. The four modules apply this posture from the silicon of the PIN pad out to the IP stack and back to the factory floor.

Read alongside the PCI PTS HSM standard, the POI requirements complete the picture of a payment transaction's cryptographic path: the POI captures and encrypts the PIN at the edge, and the HSM verifies it at the centre, each governed by the same principles of tamper response, key separation, and life-cycle custody applied to a different point in the chain. For anyone building, procuring, or auditing payment acceptance, the standard is a concrete catalogue of the properties a terminal must hold before a cardholder should be asked to type a PIN into it.

![PCI PTS POI v7.0 requirements mindmap]({{site.url_complet}}/assets/article/securite/pci-poi/pci-pts-poi-security-requirements.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **POI** | Point of Interaction, the merchant-facing payment terminal (PIN pad, card reader, secure processor) that first handles a PIN and account data. |
| **PED / EPP** | PIN Entry Device and Encrypting PIN Pad, terminal types that accept and encrypt a cardholder PIN. |
| **SCR / SCRP** | Secure (encrypting) Card Reader, and Secure Card Reader with PIN, secure components integrated into a larger terminal solution. |
| **SRED** | Secure Reading and Exchange of Data, the account-data protection function that encrypts card data on entry and never exposes it in cleartext. |
| **Attack potential** | A Common Criteria score grading attack difficulty by combining time, expertise, target knowledge, opportunity, and equipment. |
| **Tamper response / zeroization** | Automatic erasure of sensitive data when a device detects physical intrusion, making the data infeasible to recover. |
| **Key separation** | The rule that each key is usable for one function only, so a PIN key cannot decrypt arbitrary data or act as another key type. |
| **Open Protocols** | The requirement to declare every public-domain protocol and interface a device exposes so each can be assessed for known vulnerabilities. |
| **Overlay attack** | Fitting a fraudulent layer over a PIN pad to capture key presses, countered by the integration requirement C1.2. |
| **Lebanese Loop** | A card-capture attack using a sleeve that traps an inserted card for later retrieval, countered by requirement C2.2. |

## Frequently Asked Questions

**Q: What is the difference between a POI device and an HSM in the payments chain?**

They sit at opposite ends of the same transaction. The POI is the merchant-facing terminal, the PIN pad and card reader a cardholder physically touches, where a PIN and account data are first captured and encrypted. The HSM is a backend appliance in a data centre that receives the encrypted PIN block and verifies it, and that generates and manages keys. Both are tamper-resistant and both are governed by the PCI PTS family of standards, but the POI faces field attacks such as overlays, card-capture sleeves, and shoulder surfing, while the HSM faces a data-centre threat model. This article's companion on the PCI PTS HSM standard covers the backend side.

**Q: Why does the standard forbid the terminal from ever displaying the PIN it just received?**

Requirement B3 requires that the device neither displays nor otherwise indicates the value of an entered PIN digit. Any visible feedback is limited to non-significant symbols such as asterisks, and if audible tones accompany key presses, every digit must sound identical so the PIN cannot be reconstructed by ear. The reasoning is that the PIN's secrecy is the entire point of PIN verification: a terminal that echoed digits, or emitted a distinct tone per key, would leak the secret through the very interface meant to protect it, whether to a shoulder-surfer, a hidden camera, or a microphone.

**Q: What are the two numbers in a requirement like "attack potential of at least 35 with a minimum of 15 for initial exploitation"?**

Attack potential is a score for how hard an attack is, combining time, expertise, knowledge of the device, opportunity, and equipment. The larger number is the bar for *identification plus initial exploitation*, discovering a working attack and performing it the first time. The smaller number is the floor for *initial exploitation* alone, how hard it is to repeat the attack once it is known. Requiring both prevents a device from passing on the strength of an attack that is hard to invent but trivial to replicate. In this standard the thresholds are tiered by sensitivity: 35 for extracting a PIN key (A6/A7), 26 for account-data keys or for penetrating sensitive functions, 20 for a card or biometric reader, and as low as 16 for a non-PIN PAN keypad.

**Q: What is SRED, and how does it interact with third-party applications on a modern terminal?**

SRED, Secure Reading and Exchange of Data, is the account-data protection function: the terminal encrypts card data on entry and, in encrypting mode, provides no mechanism to output it in cleartext (B23). The interaction with third-party code is the sharp edge introduced in v7.0. Because a modern terminal may run untrusted applications, the standard requires that cleartext account data is never made available to any execution environment that can run third-party applications, even through a whitelist (B23), and that cleartext account data is released only to applications authenticated under the firmware's signing requirements (B23.1). Third-party applications themselves must be signed and kept out of environments with cleartext access (B2.3). SRED and application isolation together ensure that adding programmability to the terminal does not open a path to the card data it protects.

**Q: Combining the integration and communications modules, how does the standard stop an attacker who controls the store controller or network from harvesting PINs?**

Several requirements interlock. On the integration side, C2.4 requires the terminal to enforce cryptographically the correspondence between the prompt shown to the cardholder and the actual operating state of the PIN-entry device, and to authenticate any command from an external device such as a store controller that would enable data entry. So a compromised controller cannot display a benign "enter PIN" prompt while silently routing the digits to itself, because switching the device into a PIN-capturing state requires an authenticated command and an honest display. On the communications side, D9 requires mutually authenticated sessions over a declared protocol with verified public keys, D8 requires message integrity by MAC or signature, and D10 requires replay detection, so an attacker on the network cannot inject, replay, or forge the messages that drive the terminal. The physical requirements (A5, A7) close the side-channel path, and B13 ensures that even if prompts are manipulated, no cleartext key or PIN can be output. The attacker is denied every individual step: honest display, authenticated commands, authenticated network peers, and a boundary that never emits the secret.

**Q: What are the most significant changes introduced in v7.0?**

The headline additions reflect terminals becoming networked, programmable computers. Cryptography for device security must now provide at least 128-bit effective key strength; a new requirement (A15) covers biometric readers; a set of requirements governs third-party applications, requiring them to be signed and isolated from cleartext account data; the operating system must enforce mandatory access controls in an enforcing mode; and any device with an IP stack must support TLS 1.3 or higher. Non-invasive attack modelling was also refined to set distinct attack potentials for PIN keys and account-data keys.

## References

- [PCI Security Standards Council — Document Library](https://www.pcisecuritystandards.org/document_library/) — source of the PCI PTS POI Modular Security Requirements v7.0 (May 2025) and related PCI standards.
- [PCI PIN Transaction Security (PTS) programme](https://www.pcisecuritystandards.org/assessors_and_solutions/pin_transaction_devices) — approved-device listings and the PTS evaluation framework.
- [ANSI X9.24 — Retail Financial Services Symmetric Key Management](https://x9.org/) — key-management techniques referenced by requirement B9.
- [ANSI X9.143 — Interoperable Secure Key Block Specification](https://x9.org/) — the key-block format (formerly TR-31) mandated via DTR B9.
- [ISO 9564 — PIN Management and Security](https://www.iso.org/standard/68669.html) — PIN-encryption and PIN-block techniques required by B11 and B21.
- [ISO 11568 — Financial Services Key Management (Retail)](https://www.iso.org/standard/73412.html) — key-management framework referenced by B9 and D7.
- [ISO 16609 — Requirements for message authentication using symmetric techniques](https://www.iso.org/standard/64068.html) — MAC integrity referenced by requirement D8.
- [NIST SP 800-90A Rev. 1 — Random Number Generation Using Deterministic Random Bit Generators](https://csrc.nist.gov/pubs/sp/800/90/a/r1/final) — DRBG guidance behind requirement B7.
- [RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3](https://www.rfc-editor.org/rfc/rfc8446) — the TLS 1.3 requirement for IP-enabled devices in D9.
