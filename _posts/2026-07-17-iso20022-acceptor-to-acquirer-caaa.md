---
layout: post
title: "ISO 20022 for Acceptor-to-Acquirer Card Transactions — The caaa Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation
tags: iso20022 cards caaa pos acquirer acceptance
description: How ISO 20022 models the merchant-terminal-to-acquirer leg of a card payment through the caaa business area, covering authorisation, completion, cancellation, reconciliation, currency conversion, and batch transfer.
image: /assets/article/finance/iso20022-acceptor-to-acquirer-caaa.png
isMath: false
---



When you pay by card in a shop, the terminal has to ask someone whether the payment is good. That someone is the **acquirer**, the merchant's bank or processor, and the conversation between the terminal and the acquirer is what ISO 20022 standardises in its `caaa` business area: **acceptor to acquirer card transactions**. It is the point-of-sale counterpart to the ATM protocol, and this article walks through its twenty-seven messages, the transaction lifecycle they express, and how they relate to the other card areas.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What caaa covers

`caaa` carries the leg between the **acceptor**, the merchant's point of interaction (POI) or terminal, and the **acquirer** that authorises and settles the merchant's card transactions. In the four-corner card model, this is the merchant-side link: the acceptor asks the acquirer to approve a payment, and the acquirer forwards to the issuer over its own rails.

![Where caaa sits: acceptor to acquirer]({{site.url_complet}}/assets/article/finance/caaa-poi-acquirer-concept.png)

It is the ISO 20022 successor, on the acquiring side, to the ISO 8583 messages that terminals have long used, and it grew out of the nexo acquirer protocol. It sits between two other card areas: the sale system drives the POI through `casp`, and the acquirer reaches the issuer through `cain`. `caaa` is the middle leg, from terminal to acquirer.

## The caaa message catalogue

The twenty-seven messages are organised into functional groups, almost all request-and-response or advice-and-response pairs. Each message opens with the card family's header; the authorisation request (`caaa.001`), for example, carries a header and an authorisation-request block.

| Group | Messages | Purpose |
|-------|----------|---------|
| Authorisation | `caaa.001`, `caaa.002` | Approve a transaction in real time |
| Completion | `caaa.003`, `caaa.004` | Advise the final outcome and confirm |
| Cancellation | `caaa.005` to `caaa.008` | Cancel a transaction, by request or advice |
| Reconciliation | `caaa.009`, `caaa.010` | Agree totals with the acquirer |
| Batch transfer | `caaa.011`, `caaa.012`, `caaa.026`, `caaa.027` | Send captured transactions in a batch or file |
| Diagnostic | `caaa.013`, `caaa.014` | Check the link to the acquirer |
| Currency conversion | `caaa.016` to `caaa.019` | Dynamic currency conversion at the point of sale |
| Transaction advice | `caaa.020`, `caaa.021` | Advise a transaction and confirm |
| Non-financial | `caaa.022`, `caaa.023` | Non-financial operations |
| Transaction log | `caaa.024`, `caaa.025` | Request and return the transaction log |
| Rejection | `caaa.015` | Reject an unprocessable message |

The **authorisation** pair is the real-time approval a cardholder waits for. The **completion** pair reports the transaction's final outcome, since the authorised amount and the captured amount can differ. The **cancellation** group handles voiding a transaction, either by a request that asks or an advice that informs. **Reconciliation** and the **batch** messages handle end-of-period settlement of captured transactions. The **currency conversion** group supports dynamic currency conversion, offering a cardholder payment in their home currency. The remaining pairs cover diagnostics, transaction advices, non-financial operations, and log retrieval.

## The transaction lifecycle

The core messages trace an ordinary card payment at a merchant.

![A card acceptance transaction]({{site.url_complet}}/assets/article/finance/caaa-transaction-workflow.png)

**Authorisation.** The acceptor asks the acquirer to approve the payment with a `caaa.001` **AcceptorAuthorisationRequest**, and the acquirer approves or declines in a `caaa.002` **AcceptorAuthorisationResponse**. This reserves the funds; the cardholder sees "approved".

**Completion.** Once the sale is finalised, the acceptor reports the transaction's final outcome, including the captured amount if it differs from the authorised one, in a `caaa.003` **AcceptorCompletionAdvice**, confirmed by a `caaa.004` response. Separating authorisation from completion matters because the final amount, after tips or partial fulfilment, is not always the amount authorised.

**Cancellation and reconciliation.** If a transaction must be voided, the cancellation group (`caaa.005` to `caaa.008`) handles it. At the end of the day the acceptor reconciles totals with the acquirer using a `caaa.009` **AcceptorReconciliationRequest** and its `caaa.010` response, and captured transactions are transferred in batch through `caaa.011` and `caaa.012` or as a file through `caaa.026` and `caaa.027`. Diagnostics (`caaa.013`, `caaa.014`) confirm the link is healthy, and any message that cannot be processed is answered with a `caaa.015` rejection.

## Conclusion

The `caaa` business area standardises the merchant-terminal-to-acquirer conversation of a card payment. Its twenty-seven messages, almost all request-and-response pairs, authorise a transaction, report its completion, cancel it if needed, reconcile and batch the day's captures, offer currency conversion, and run diagnostics, all on the card family's protected envelope. It is the acquiring-side successor to ISO 8583 and the middle leg of the card acceptance chain, between the `casp` sale-to-POI interface at the till and the `cain` acquirer-to-issuer link beyond. Read alongside the ATM protocol `catp` that mirrors it for cash machines, `caaa` is where a card payment at a shop actually gets approved.

![Mindmap summarising the ISO 20022 caaa acceptor-to-acquirer area]({{site.url_complet}}/assets/article/finance/iso20022-acceptor-to-acquirer-caaa.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **caaa** | The ISO 20022 acceptor-to-acquirer card transactions business area, covering the merchant-terminal-to-acquirer leg across twenty-seven messages. |
| **Acceptor** | The merchant's point of interaction, the terminal or device that accepts the card and asks the acquirer to approve. |
| **Acquirer** | The merchant's bank or processor that authorises and settles the merchant's card transactions. |
| **Authorisation (`caaa.001`)** | The real-time request to approve a transaction and reserve funds, answered by `caaa.002`. |
| **Completion advice (`caaa.003`)** | The message reporting a transaction's final outcome, including the captured amount if it differs from the authorised one. |
| **Reconciliation (`caaa.009`)** | The exchange that agrees the totals of captured transactions with the acquirer, typically at end of day. |
| **Batch transfer** | The delivery of captured transactions to the acquirer in a batch (`caaa.011`) or file (`caaa.026`). |
| **Dynamic currency conversion** | Offering a cardholder payment in their home currency at the point of sale, supported by `caaa.016` to `caaa.019`. |
| **POI** | The Point of Interaction, the terminal that acts as the acceptor in a caaa exchange. |
| **nexo acquirer protocol** | The industry protocol from which the acceptor-to-acquirer messages derive. |

## Frequently Asked Questions

**Q: What leg of a card payment does caaa cover?**

`caaa` covers the leg between the acceptor (the merchant's terminal) and the acquirer (the merchant's bank or processor). When a card is presented, the terminal uses `caaa` to ask the acquirer to authorise the payment and later to report its completion, reconcile totals, and transfer captured transactions. It does not reach the issuer directly; the acquirer forwards to the issuer over the acquirer-to-issuer rails. `caaa` is specifically the merchant-side, acquiring link of the transaction.

**Q: Why are authorisation and completion separate messages?**

Because the amount authorised and the amount finally captured can differ, and both events need recording. The `caaa.001` authorisation request reserves funds in real time while the cardholder waits, but the final amount may change afterwards, for example when a tip is added or an order is only partly fulfilled. The `caaa.003` completion advice reports that final outcome. Separating the two lets the terminal get a fast approval and then settle the true amount, which a single message could not express.

**Q: How does caaa relate to casp and cain?**

They are three legs of the card acceptance chain. `casp` is the sale-to-POI interface, where the cash register drives the payment terminal. `caaa` is the acceptor-to-acquirer leg, where that terminal talks to the acquirer. `cain` is the acquirer-to-issuer leg, where the acquirer reaches the card issuer. A single shop payment flows through all three: the till instructs the terminal (`casp`), the terminal authorises with the acquirer (`caaa`), and the acquirer authorises with the issuer (`cain`).

**Q: What is dynamic currency conversion in caaa?**

Dynamic currency conversion is the option, offered at the point of sale, to let a cardholder pay in their own home currency rather than the merchant's local currency. The `caaa.016` to `caaa.019` messages support it: a currency conversion request and response establish the rate to offer, and an advice and response record the choice. It is a distinct sub-process because it involves quoting a rate and capturing the cardholder's acceptance of it before the transaction proceeds.

**Q: How does caaa compare with the ATM protocol catp?**

They are counterparts for different acceptance devices. `catp` is the ATM protocol, carrying withdrawals, deposits, and related operations between a cash machine and its host. `caaa` is the point-of-sale protocol, carrying purchases, completions, and reconciliations between a merchant terminal and its acquirer. Both are card-acceptance transaction areas on the same protected envelope, but one serves ATMs and the other serves merchant terminals, reflecting the different operations each device performs.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 card and payment messages](https://www.iso20022.org/payments)
- [nexo standards — acquirer protocol](https://www.nexo-standards.org/)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [Claude Code](https://claude.com/product/claude-code)
