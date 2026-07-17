---
layout: post
title: "ISO 20022 for Card Fraud Reporting — The cafr Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 cards fraud cafr payments security
description: How ISO 20022 models card fraud reporting through the cafr business area, a compact four-message set that lets card parties report fraudulent transactions and communicate their disposition in a structured, machine-readable form.
image: /assets/article/finance/iso20022-fraud-reporting-cafr.png
isMath: false
---



Card fraud is a shared problem. When an issuer confirms that a transaction was fraudulent, that fact is useful to the acquirer, to the card scheme, and to the fraud-scoring systems that will judge the next transaction. Getting the information to move cleanly between organisations needs a common format, and ISO 20022 provides one in its `cafr` business area: **fraud reporting and disposition**. It is one of the smallest areas in the standard, just four messages, but it sits on top of the same card-message machinery as authorisation and clearing. This article covers what the four `cafr` messages are, how the reporting and disposition flows fit together, and what each message carries.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What cafr is for

The `cafr` area belongs to the ISO 20022 card family, the same group of standards that carries authorisation and clearing between acquirers and issuers. Where those messages move money, `cafr` moves *information about fraud*. Its job is to let one card party tell another that a transaction was fraudulent, and to let the parties agree on the disposition of that report, meaning the classification and the action taken.

Two things motivate a standard here rather than ad hoc files. First, fraud data is only valuable if it is structured: a scoring model needs to know the fraud type, the channel, the dates, and the exact transaction, not a free-text note. Second, fraud reporting often carries regulatory and scheme obligations, with issuers and acquirers required to report confirmed fraud into scheme databases within set windows. A machine-readable message with a published schema makes both the structure and the timeliness enforceable.

![Where fraud reporting and disposition sit between card parties]({{site.url_complet}}/assets/article/finance/cafr-actors-concept.png)

The parties are the familiar ones from the four-corner card model: an **acquirer** on the merchant side, an **issuer** on the cardholder side, and often a **card scheme** or fraud system that collates reports and feeds shared databases. A report typically flows from the party that detected the fraud toward the scheme or the counterparty, and the disposition flows back.

## The four messages

The area is two request-and-response pairs. One pair reports the fraud; the other communicates its disposition.

| Identifier | Message | Role |
|------------|---------|------|
| `cafr.001` | FraudReportingInitiation | Report one or more fraudulent transactions |
| `cafr.002` | FraudReportingResponse | Acknowledge and respond to a fraud report |
| `cafr.003` | FraudDispositionInitiation | Communicate the disposition of reported fraud |
| `cafr.004` | FraudDispositionResponse | Acknowledge and respond to the disposition |

The split between *reporting* and *disposition* is the design decision worth understanding. Reporting is the act of flagging a transaction as fraudulent. Disposition is the subsequent agreement on what that report means and what happens because of it: whether the fraud is confirmed or dismissed, how it is classified, and what action follows. Keeping them in separate exchanges lets a report be filed immediately, while the disposition, which may depend on investigation, follows when it is known.

![Reporting a fraud, then communicating its disposition]({{site.url_complet}}/assets/article/finance/cafr-reporting-disposition-workflow.png)

## What the messages carry

Every `cafr` message opens with the same header as the rest of the card family. Taking the fraud reporting initiation (`cafr.001`), its top-level structure is a header followed by two content blocks.

- **Header (`Hdr`, type `Header72`)** carries the message function and the routing and versioning data shared across the card messages, so a receiver can identify and dispatch the message before reading its body.
- **Reported fraud (`RptdFrd`)** describes the fraud itself: the classification and the reporting context, the party reporting it, and the relevant dates.
- **Fraudulent transaction data (`FrdlntTxData`)** identifies the transaction or transactions being flagged, tying the report back to the specific authorisation or clearing records that were fraudulent.

The disposition messages follow the same header-plus-content shape, with content describing the outcome rather than the initial report. Because these messages carry account and cardholder identifiers, they inherit the card family's data protection: sensitive fields such as the primary account number are carried in protected form, and messages are authenticated so a receiver can trust their origin. The exact cryptographic material is provisioned outside these messages, in the same way it is for the authorisation and clearing traffic.

## How a report and its disposition connect

A typical exchange runs in two stages. The detecting party sends a `cafr.001` FraudReportingInitiation naming the fraud and the transactions, and the receiver acknowledges with a `cafr.002` FraudReportingResponse. That closes the reporting stage: the fraud is now on record with the counterparty or scheme.

The disposition stage may follow immediately or after investigation. A `cafr.003` FraudDispositionInitiation communicates the agreed classification and any action taken, and a `cafr.004` FraudDispositionResponse acknowledges it. Depending on scheme rules, the disposition may be initiated by the party that received the original report or by the scheme that collated it. The two pairs are deliberately independent so that filing a report never has to wait on a decision that is not yet available.

## Conclusion

The `cafr` business area is a small, focused part of ISO 20022, but it addresses a real need: moving fraud information between card parties in a structured form that scoring systems and scheme databases can consume, and that regulatory and scheme reporting obligations can rely on. Its four messages form two pairs, one to report a fraudulent transaction and one to communicate the disposition of that report, each built on the same header and data-protection model as the authorisation and clearing messages it accompanies. Read alongside the acquirer-to-issuer transaction area, `cafr` is the part of the card standard that turns a confirmed fraud into shared, actionable data.

![Mindmap summarising the ISO 20022 cafr fraud reporting and disposition area]({{site.url_complet}}/assets/article/finance/iso20022-fraud-reporting-cafr.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **cafr** | The ISO 20022 business area for card fraud reporting and disposition, comprising the four messages `cafr.001` to `cafr.004`. |
| **Fraud reporting** | The act of flagging one or more card transactions as fraudulent, carried by `cafr.001` and acknowledged by `cafr.002`. |
| **Disposition** | The agreed classification of a reported fraud and the action taken because of it, carried by `cafr.003` and acknowledged by `cafr.004`. |
| **Reported fraud (`RptdFrd`)** | The content block describing the fraud: its classification, the reporting party, and the relevant dates. |
| **Fraudulent transaction data (`FrdlntTxData`)** | The content block identifying the specific transactions being reported as fraudulent. |
| **Acquirer** | The card party on the merchant side of a transaction, one of the parties that reports or receives fraud information. |
| **Issuer** | The card party that issued the card and holds the cardholder's account, often the party that confirms a fraud. |
| **Card scheme** | The network that connects acquirers and issuers and that may collate fraud reports into shared databases. |
| **Header (`Hdr`)** | The `Header72` element opening every card-family message, carrying the message function and routing data. |
| **Protected data** | Sensitive fields such as the account number carried in encrypted form, so they are not exposed on the network. |

## Frequently Asked Questions

**Q: What is the difference between fraud reporting and fraud disposition?**

Reporting is flagging a transaction as fraudulent; disposition is the agreement on what that report means and what follows from it. A `cafr.001` FraudReportingInitiation says "this transaction was fraudulent" and records it with the counterparty or scheme. A `cafr.003` FraudDispositionInitiation communicates the resolution: how the fraud is classified and what action was taken. They are separate so a report can be filed at once while the disposition, which may need investigation, is sent when it is known.

**Q: Why are there only four messages in the cafr area?**

Because the area does one narrow job: exchanging fraud information, not preventing or authorising transactions. That job decomposes into exactly two request-and-response pairs, one for the report and one for the disposition. The heavier work of the card lifecycle, authorising and clearing transactions and handling disputes, lives in the acquirer-to-issuer area, so `cafr` does not need to duplicate it. A small, well-scoped area is a sign the standard has drawn its boundaries cleanly rather than a sign it is incomplete.

**Q: What does a cafr.001 message actually contain?**

Three parts. A header (`Hdr`, type `Header72`) carrying the message function and the routing and versioning data shared across the card messages. A reported-fraud block (`RptdFrd`) describing the fraud itself: its classification, the reporting party, and the relevant dates. And a fraudulent-transaction-data block (`FrdlntTxData`) identifying the specific transactions being flagged, which ties the report back to the authorisation or clearing records that were fraudulent. Together they let a receiver understand what kind of fraud occurred and exactly which transactions it applies to.

**Q: How does cafr protect the sensitive data it carries?**

It inherits the card family's protection model. Because a fraud report references account and cardholder identifiers, sensitive fields such as the primary account number are carried in protected, encrypted form rather than in the clear, and messages are authenticated so a receiver can trust their origin. The cryptographic keys that make this work are provisioned outside the `cafr` messages themselves, in the same way they are for the authorisation and clearing traffic that `cafr` accompanies.

**Q: Who initiates a fraud report, and who initiates the disposition?**

A report is initiated by the party that detected or confirmed the fraud, commonly the issuer, and sent toward the counterparty or the card scheme. The disposition can be initiated by the party that received the original report or by the scheme that collated it, depending on the scheme's rules. The `cafr` messages do not hard-code a single direction; they define the reporting and disposition exchanges and leave the routing to the operating rules of the network that uses them.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 card and payment messages](https://www.iso20022.org/payments)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [nexo standards — card payment message specifications](https://www.nexo-standards.org/)
- [Claude Code](https://claude.com/product/claude-code)
