---
layout: post
title: "ISO 20022 for ATM Management — The caam Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation
tags: iso20022 cards caam atm management key-download
description: How ISO 20022 models the management of automated teller machines through the caam business area, covering device control, key download, diagnostics, configuration, reconciliation, and exception handling between an ATM and its manager.
image: /assets/article/finance/iso20022-atm-management-caam.png
isMath: false
---



An ATM does more than dispense cash. Behind each withdrawal sits a machine that must be configured, keyed, monitored, reconciled, and repaired, and that management is a job of its own. ISO 20022 gives it a dedicated business area, `caam`: **ATM management**. Where its sibling `catp` carries the transactions a customer performs, `caam` carries the operator's management of the machine itself. This article walks through the sixteen `caam` messages and the management functions they serve.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What caam is for

`caam` manages the ATM as a device, between the machine and its **ATM manager**, the back-office system that operates a fleet of machines. It is the counterpart to `catp`, the ATM transaction protocol: `catp` handles a customer's withdrawal or deposit, while `caam` handles everything the operator does to keep the machine working, downloading keys, pushing configuration, running diagnostics, collecting reconciliation, and handling faults.

![ATM management plane]({{site.url_complet}}/assets/article/finance/caam-management-concept.png)

Keeping management separate from transactions is the same design choice made across the card family: the operator's control plane and the customer's transaction plane are different concerns with different messages, even though they run to the same machine.

## The caam message catalogue

The sixteen messages group by management function, mostly as request-and-response or advice-and-acknowledgement pairs.

| Group | Messages | Purpose |
|-------|----------|---------|
| Device | `caam.001`, `caam.002` | Report and control the ATM's devices |
| Key download | `caam.003`, `caam.004` | Load cryptographic keys into the ATM |
| Diagnostic | `caam.005`, `caam.006` | Run diagnostics on the ATM |
| Host to ATM | `caam.007`, `caam.008` | Send a host request and acknowledge |
| Reconciliation | `caam.009`, `caam.010`, `caam.015`, `caam.016` | Reconcile the ATM's activity |
| Exception | `caam.011`, `caam.012` | Advise and acknowledge an exception |
| Configuration | `caam.013`, `caam.014` | Report and control the ATM's configuration |

The **device** pair reports the state of the ATM's hardware and lets the manager control it. The **key download** pair loads the cryptographic keys the machine needs to protect PIN and card data in its `catp` transactions. The **diagnostic** pair checks the machine's health. The **configuration** pair reports and updates how the ATM is set up. The **reconciliation** messages agree the machine's activity totals with the manager, and the **exception** pair reports faults and confirms them. The host-to-ATM pair lets the manager push a request to the machine and receive an acknowledgement.

## Managing a machine

The messages come together across the operation of an ATM.

![Managing an ATM: keys, configuration, reconciliation]({{site.url_complet}}/assets/article/finance/caam-lifecycle-workflow.png)

The machine reports its state to the manager with a `caam.001` **ATMDeviceReport**. The manager provisions it: a `caam.003` **ATMKeyDownloadRequest** and its `caam.004` response load the cryptographic keys, and a `caam.014` **ATMConfigurationControl** pushes the configuration, which the machine confirms with a `caam.013` report. If something goes wrong, the machine raises a `caam.011` **ATMExceptionAdvice**, acknowledged by a `caam.012`. At the end of the day the machine sends a `caam.009` **ATMReconciliationAdvice** to agree its activity, confirmed by a `caam.010`. None of this dispenses cash, but all of it keeps the machine fit to serve customers.

## Conclusion

The `caam` business area is the operator's control plane for automated teller machines. Its sixteen messages let an ATM manager download keys, push and report configuration, run diagnostics, reconcile activity, and handle exceptions on the machines it operates, keeping them provisioned and healthy so that the `catp` transaction traffic can run. It is deliberately separate from the transaction protocol, mirroring the split between control and transactions found throughout the card family. Read next to `catp`, which carries the withdrawals and deposits, `caam` is what keeps the machine behind them working.

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **caam** | The ISO 20022 ATM management business area, covering the operator's management of automated teller machines across sixteen messages. |
| **ATM manager** | The back-office system that operates a fleet of ATMs and manages each machine through `caam`. |
| **Device report / control** | The pair (`caam.001`, `caam.002`) that reports the state of an ATM's hardware and lets the manager control it. |
| **Key download** | The loading of cryptographic keys into an ATM (`caam.003`, `caam.004`), so it can protect its transaction data. |
| **Diagnostic** | The check of an ATM's health, carried by `caam.005` and `caam.006`. |
| **Configuration** | The setup of an ATM, reported and updated through `caam.013` and `caam.014`. |
| **Reconciliation** | The agreement of an ATM's activity totals with its manager, via `caam.009`, `caam.010`, `caam.015`, and `caam.016`. |
| **Exception advice** | The message (`caam.011`) by which an ATM reports a fault, acknowledged by `caam.012`. |
| **catp** | The sibling ISO 20022 area carrying ATM transactions, which `caam` complements by managing the machine. |
| **Control plane** | The management traffic that provisions and monitors a machine, as distinct from the transaction traffic that serves customers. |

## Frequently Asked Questions

**Q: What is the difference between caam and catp?**

They serve the same machine but different purposes. `catp` is the ATM transaction protocol: it carries the withdrawals, deposits, transfers, and PIN changes a customer performs. `caam` is the ATM management area: it carries what the operator does to the machine, downloading keys, pushing configuration, running diagnostics, reconciling activity, and handling faults. `catp` is the customer's transaction plane; `caam` is the operator's control plane. Both run to the same ATM, but they are kept as separate message sets because they are separate concerns.

**Q: Why does key download have its own pair of messages?**

Because loading cryptographic keys is a distinct, security-critical operation that the ATM depends on for its transactions. The `caam.003` ATMKeyDownloadRequest and `caam.004` ATMKeyDownloadResponse deliver and confirm the keys the machine uses to protect PIN and card data in its `catp` transactions. Giving key download its own pair keeps the operation explicit and auditable, separate from the routine device and configuration traffic, so an operator can see exactly when a machine's keys were provisioned or rotated.

**Q: What do the configuration messages do?**

They set up how an ATM behaves. A `caam.014` ATMConfigurationControl pushes configuration to the machine, telling it how to operate, and the machine reports its current configuration back with a `caam.013` ATMConfigurationReport. This lets an operator manage a fleet centrally, changing settings without visiting each machine physically. Configuration is one of the main day-to-day management tasks `caam` supports, alongside key download and diagnostics.

**Q: How does an ATM report a fault through caam?**

Through the exception pair. When something goes wrong, a jam, a hardware failure, or another abnormal condition, the machine sends a `caam.011` ATMExceptionAdvice to its manager describing the fault, and the manager confirms receipt with a `caam.012` ATMExceptionAcknowledgement. This lets the operator learn about problems promptly and dispatch a fix, which is essential for keeping a fleet of unattended machines running.

**Q: Does caam carry any transaction value?**

No. Like the card network-management area, `caam` carries no money. It manages the machine: keys, configuration, diagnostics, reconciliation, and exceptions. Its value is entirely in keeping the ATM provisioned and healthy so that the `catp` transaction traffic can run. An unkeyed or misconfigured machine cannot serve customers, so the management plane is a precondition for the transaction plane even though it moves no funds itself.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 card and payment messages](https://www.iso20022.org/payments)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [nexo standards — card payment message specifications](https://www.nexo-standards.org/)
- [Claude Code](https://claude.com/product/claude-code)
