---
layout: post
title: "ISO 20022 for Terminal Management — The catm Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation
tags: iso20022 cards catm terminal-management tms certificate
description: How ISO 20022 models the management of payment terminals through the catm business area, covering status reporting, management plans, configuration updates, maintenance delegation, and certificate management between a terminal and its management system.
image: /assets/article/finance/iso20022-terminal-management-catm.png
isMath: false
---



A payment terminal in a shop is a managed device. Someone has to configure it, keep its software and parameters current, provision its certificates, and arrange its maintenance, all remotely, across a fleet that may number in the millions. ISO 20022 gives that job a business area, `catm`: **terminal management**. It is the point-of-sale counterpart to ATM management, and this article covers its eight messages and the terminal-management-system functions they serve.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What catm is for

`catm` is the language of the **terminal management system (TMS)**, the platform that manages a fleet of point-of-interaction (POI) terminals. Where `caaa` carries a terminal's transactions to the acquirer, `catm` carries the management of the terminal itself: telling it what configuration to run, what tasks to perform, how to renew its certificates, and how its maintenance is handled. It is the POS equivalent of the `caam` ATM-management area.

![Terminal management between a TMS and a POI]({{site.url_complet}}/assets/article/finance/catm-tms-concept.png)

Terminals are numerous, distributed, and long-lived, so managing them by hand is impossible. The TMS relationship lets an operator push updates and manage security remotely, and `catm` is the standard message set for it.

## The eight messages

The area is compact, built around a few management exchanges.

| Identifier | Message | Purpose |
|------------|---------|---------|
| `catm.001` | StatusReport | The terminal reports its state and contacts the TMS |
| `catm.002` | ManagementPlanReplacement | The TMS gives the terminal its plan of tasks |
| `catm.003` | AcceptorConfigurationUpdate | The TMS pushes new configuration |
| `catm.004` | TerminalManagementRejection | Reject an unprocessable management message |
| `catm.005` | MaintenanceDelegationRequest | Request delegation of a maintenance task |
| `catm.006` | MaintenanceDelegationResponse | Respond to the delegation request |
| `catm.007` | CertificateManagementRequest | Request certificate provisioning or renewal |
| `catm.008` | CertificateManagementResponse | Respond to the certificate request |

The **status report** is how a terminal makes contact with its TMS, reporting its current state. The **management plan** the TMS returns tells the terminal what to do next: which tasks to run and when. The **configuration update** delivers new parameters or software settings. The **maintenance delegation** pair lets maintenance tasks be delegated between parties, useful when a third party services the terminals. The **certificate management** pair provisions and renews the cryptographic certificates the terminal needs for secure communication, and the **rejection** message handles a management message the terminal cannot process.

## A terminal-management exchange

The messages come together when a terminal checks in with its management system.

![A terminal management exchange]({{site.url_complet}}/assets/article/finance/catm-management-workflow.png)

The terminal opens contact with a `catm.001` **StatusReport**, reporting where it stands. The TMS responds with a `catm.002` **ManagementPlanReplacement**, giving the terminal its updated plan of what to do. It then delivers any new settings with a `catm.003` **AcceptorConfigurationUpdate** and, where certificates are due for renewal, sends a `catm.007` **CertificateManagementRequest** that the terminal answers with a `catm.008` response. If the terminal cannot apply a management message, it returns a `catm.004` **TerminalManagementRejection**. Through this exchange the operator keeps a distant, unattended device current and secure.

## Conclusion

The `catm` business area is the terminal management system's message set. Its eight messages let a TMS manage a fleet of payment terminals remotely: the terminal reports its status, the TMS returns a management plan, pushes configuration, delegates maintenance, and provisions certificates, with a rejection for messages that cannot be applied. It is the point-of-sale counterpart to ATM management and, like it, is kept separate from the transaction traffic it supports. Read next to `caaa`, which carries the terminal's transactions to the acquirer, `catm` is what keeps the terminal itself configured, secured, and maintained.

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **catm** | The ISO 20022 terminal management business area, covering remote management of payment terminals across eight messages. |
| **Terminal management system (TMS)** | The platform that manages a fleet of POI terminals, using `catm` to configure, maintain, and secure them. |
| **POI** | The Point of Interaction, the payment terminal that is the managed device in a catm exchange. |
| **Status report (`catm.001`)** | The message by which a terminal reports its state and makes contact with its TMS. |
| **Management plan (`catm.002`)** | The set of tasks the TMS returns to a terminal, telling it what to do next. |
| **Configuration update (`catm.003`)** | The delivery of new parameters or settings to a terminal. |
| **Maintenance delegation** | The delegation of a maintenance task between parties, carried by `catm.005` and `catm.006`. |
| **Certificate management** | The provisioning and renewal of a terminal's cryptographic certificates, via `catm.007` and `catm.008`. |
| **Terminal management rejection (`catm.004`)** | The message returned when a terminal cannot apply a management message. |
| **caam** | The ISO 20022 ATM-management area, the automated-teller-machine counterpart to catm. |

## Frequently Asked Questions

**Q: What is a terminal management system, and how does catm serve it?**

A terminal management system (TMS) is the platform that operates a fleet of payment terminals remotely, keeping their configuration, software parameters, and security current. `catm` is the message set it uses. A terminal contacts the TMS with a status report, the TMS returns a management plan of tasks, and further messages push configuration, arrange maintenance, and provision certificates. Without such a system, managing thousands or millions of distributed terminals would be impossible; `catm` standardises the conversation that makes it feasible.

**Q: What is the role of the status report and management plan?**

Together they are how a terminal finds out what it should do. The `catm.001` StatusReport is the terminal's check-in: it contacts the TMS and reports its current state. The `catm.002` ManagementPlanReplacement is the TMS's answer: it gives the terminal an updated plan of the tasks it should perform and when. This pull-based model, terminal checks in, TMS returns a plan, lets the operator control a fleet centrally while each terminal initiates contact on its own schedule.

**Q: Why does certificate management need dedicated messages?**

Because a terminal relies on cryptographic certificates for secure communication, and those certificates must be provisioned and periodically renewed. The `catm.007` CertificateManagementRequest and `catm.008` CertificateManagementResponse handle that lifecycle over the air. Giving certificates their own pair keeps this security-critical operation explicit and separate from configuration and plan management, so an operator can renew a fleet's certificates in a controlled, auditable way rather than folding it into general updates.

**Q: What is maintenance delegation for?**

Maintenance delegation lets a maintenance task be handed to another party. In many deployments, a third-party servicer rather than the acquirer looks after the physical terminals, and the `catm.005` MaintenanceDelegationRequest and `catm.006` MaintenanceDelegationResponse let responsibility for a task be delegated accordingly. It reflects the reality that managing a terminal estate often involves several parties, and the standard provides messages to coordinate who does what.

**Q: How does catm relate to caam and caaa?**

`catm` is the point-of-sale terminal-management area; `caam` is its ATM-management counterpart; and `caaa` carries the POS terminal's transactions to the acquirer. So `catm` and `caam` are the two device-management areas, one for merchant terminals and one for ATMs, both kept separate from the transaction protocols. A merchant terminal is managed through `catm` and transacts through `caaa`, just as an ATM is managed through `caam` and transacts through `catp`.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 card and payment messages](https://www.iso20022.org/payments)
- [nexo standards — terminal management](https://www.nexo-standards.org/)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [Claude Code](https://claude.com/product/claude-code)
