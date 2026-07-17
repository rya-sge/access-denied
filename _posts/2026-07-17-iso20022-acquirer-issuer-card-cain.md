---
layout: post
title: "ISO 20022 for Acquirer-to-Issuer Card Transactions — The cain Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation
tags: iso20022 cards cain iso8583 authorisation chargeback
description: How ISO 20022 models the acquirer-to-issuer card rails through the cain business area, the modern successor to ISO 8583, covering authorisation, clearing, reversal, retrieval, and chargeback between an acquirer and an issuer.
image: /assets/article/finance/iso20022-acquirer-issuer-card-cain.png
isMath: false
---



Every time a card is tapped, the approval that comes back a second later has travelled from the merchant's acquirer to the cardholder's issuer and back. For decades that conversation has been carried by ISO 8583, the long-established card-message standard behind most of the world's payment terminals. ISO 20022 offers a modern replacement for the acquirer-to-issuer legs in its `cain` business area. This article walks through the nineteen `cain` messages, the request-and-response pairs they form, and the transaction and dispute lifecycle they express, from authorisation through clearing to chargeback.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Where cain sits

Card payments are usually drawn as four corners: the cardholder, the acceptor (a merchant terminal or an ATM), the acquirer, and the issuer. ISO 20022 splits the card rails by leg. The acceptor-to-acquirer leg (the terminal talking to its acquirer) is the `caaa` area; the ATM protocol is `catp`; and the **acquirer-to-issuer** leg, the interbank heart of a card transaction, is `cain`.

![Where cain sits in the four-corner card model]({{site.url_complet}}/assets/article/finance/cain-four-corner-concept.png)

That positioning is what makes `cain` the ISO 20022 counterpart to ISO 8583. ISO 8583 has long carried the acquirer-to-issuer messages, its familiar 0100 authorisation and 0200 financial message types routed across scheme networks. `cain` expresses the same interactions in ISO 20022's dictionary and XML syntax, with richer, explicitly typed data in place of ISO 8583's numbered bitmap fields. The traffic still usually flows across a card scheme network that connects the two institutions.

## The message shape

Every `cain` message shares the card family's structure. Taking the authorisation initiation (`cain.001`), the body opens with a header and then a set of typed blocks describing the transaction.

- **Header (`Hdr`, type `Header72`)** carries the message function (`MsgFctn`) and the routing and versioning data common to the card messages.
- **Transaction characteristics (`TxChrtcs`)** describe the kind of transaction being performed.
- **Acquirer data (`Acqrr`)**, a **transaction identification (`TxId`)**, and **transaction amounts (`TxAmts`)** identify who is asking, which transaction it is, and for how much.
- **Context (`Cntxt`)** carries the surrounding detail: the card, the environment, and the point of interaction.

As with the rest of the card family, the sensitive elements are protected. The primary account number, PIN data, and track or chip data are carried in encrypted form, and messages are authenticated, because this traffic crosses networks between institutions and must assume an untrusted path. The keys behind that protection are managed outside the transaction messages.

## The cain message catalogue

The nineteen messages are almost all **initiation-and-response** pairs, one message to ask and one to answer, with a single standalone amendment. They group by the stage of the card lifecycle they serve.

| Identifier | Message | Group |
|------------|---------|-------|
| `cain.001` | AuthorisationInitiation | Authorisation |
| `cain.002` | AuthorisationResponse | Authorisation |
| `cain.003` | FinancialInitiation | Clearing |
| `cain.004` | FinancialResponse | Clearing |
| `cain.005` | ReversalInitiation | Reversal |
| `cain.006` | ReversalResponse | Reversal |
| `cain.021` | RetrievalInitiation | Dispute |
| `cain.022` | RetrievalResponse | Dispute |
| `cain.014` | RetrievalFulfilmentInitiation | Dispute |
| `cain.015` | RetrievalFulfilmentResponse | Dispute |
| `cain.027` | ChargeBackInitiation | Dispute |
| `cain.028` | ChargeBackResponse | Dispute |
| `cain.016` | InquiryVerificationInitiation | Verification |
| `cain.017` | InquiryVerificationResponse | Verification |
| `cain.025` | AddendumInitiation | Supplementary |
| `cain.026` | AddendumResponse | Supplementary |
| `cain.023` | CardManagementInitiation | Card management |
| `cain.024` | CardManagementResponse | Card management |
| `cain.020` | Amendment | Correction |

## The transaction and dispute lifecycle

The messages make most sense read in the order a transaction moves through them.

![Card transaction and dispute lifecycle expressed with cain messages]({{site.url_complet}}/assets/article/finance/cain-transaction-lifecycle-workflow.png)

**Authorisation.** The acquirer asks the issuer to approve a transaction with a `cain.001` **AuthorisationInitiation**, and the issuer approves or declines in a `cain.002` **AuthorisationResponse**. This is the real-time step the cardholder waits for at the terminal, and it reserves funds without yet moving them.

**Clearing.** The money actually moves at clearing, carried by the `cain.003` **FinancialInitiation** and `cain.004` **FinancialResponse**. Depending on the flow, a financial message either completes a previously authorised transaction or, for some transaction types, both authorises and clears in one step.

**Reversal.** When an authorised or cleared transaction must be undone, for example because the terminal timed out or the amount was wrong, a `cain.005` **ReversalInitiation** and `cain.006` **ReversalResponse** reverse it.

**Disputes.** The distinctive part of the acquirer-to-issuer relationship is what happens when a cardholder disputes a charge, and `cain` gives it a full set of messages. The issuer can ask the acquirer for the record of a transaction with a `cain.021` **RetrievalInitiation**, answered by `cain.022`, and the acquirer supplies the supporting document, such as a copy of the receipt, through the `cain.014` **RetrievalFulfilmentInitiation** and `cain.015` response. If the dispute stands, the issuer pushes the transaction back to the acquirer with a `cain.027` **ChargeBackInitiation**, answered by `cain.028`. Together these express the retrieval-then-chargeback path that resolves cardholder disputes.

**Verification, addenda, and management.** Three smaller pairs round out the area. **Inquiry verification** (`cain.016` / `cain.017`) checks a card or account without moving money, the mechanism behind an account-status or address check. **Addendum** messages (`cain.025` / `cain.026`) attach supplementary data to a transaction, such as the itemised detail a hotel or car-rental transaction carries. **Card management** (`cain.023` / `cain.024`) exchanges card lifecycle actions between the acquirer and issuer domains. Finally, the standalone `cain.020` **Amendment** corrects data in a previously sent message.

## Conclusion

The `cain` business area brings the acquirer-to-issuer card conversation into ISO 20022. Its nineteen messages, almost all initiation-and-response pairs, trace the full arc of a card transaction: authorise it, clear it, reverse it if needed, and, when a cardholder disputes it, retrieve the record and charge it back. Alongside sit verification, addenda, card management, and a general amendment. Every message uses the card family's header and protects its sensitive data, because the traffic crosses networks between institutions. As the ISO 20022 successor to ISO 8583 for the interbank card legs, `cain` is where the card standard meets the payment rails that most of the world already runs on, and it completes the card picture next to the terminal area `caaa`, the ATM area `catp`, and the fraud area `cafr`.

![Mindmap summarising the ISO 20022 cain acquirer-to-issuer card transaction area]({{site.url_complet}}/assets/article/finance/iso20022-acquirer-issuer-card-cain.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **cain** | The ISO 20022 business area for acquirer-to-issuer card transactions, comprising the nineteen messages listed as `cain.001` to `cain.028`. |
| **ISO 8583** | The long-established card-message standard for the acquirer-to-issuer legs, which `cain` modernises in ISO 20022 syntax. |
| **Acquirer** | The institution that serves the merchant or acceptor and sends transactions toward the issuer. |
| **Issuer** | The institution that issued the card, holds the cardholder's account, and authorises or declines transactions. |
| **Authorisation** | The real-time approval step, carried by `cain.001` and `cain.002`, that reserves funds without moving them. |
| **Clearing (financial)** | The step that actually moves the money, carried by the `cain.003` and `cain.004` financial messages. |
| **Reversal** | The undoing of an authorised or cleared transaction, carried by `cain.005` and `cain.006`. |
| **Retrieval** | The request for the record of a transaction during a dispute (`cain.021`/`cain.022`), fulfilled by `cain.014`/`cain.015`. |
| **Chargeback** | The return of a disputed transaction from the issuer to the acquirer, carried by `cain.027` and `cain.028`. |
| **Message function (`MsgFctn`)** | A header field identifying what a message does, letting a receiver dispatch it without inspecting the whole body. |

## Frequently Asked Questions

**Q: How does cain relate to ISO 8583?**

`cain` is the ISO 20022 successor to ISO 8583 for the acquirer-to-issuer legs of a card transaction. ISO 8583 has carried authorisation and financial messages between acquirers and issuers for decades using numbered bitmap fields. `cain` expresses the same interactions, authorisation, clearing, reversal, and disputes, in ISO 20022's dictionary and XML syntax, with explicitly typed, structured data in place of the older positional fields. The traffic still typically crosses a card scheme network, but the message format is the modern standard.

**Q: What is the difference between an authorisation and a financial message?**

Authorisation reserves funds in real time; a financial (clearing) message moves them. When a card is presented, the `cain.001` AuthorisationInitiation asks the issuer to approve the amount, and the `cain.002` AuthorisationResponse approves or declines, all while the cardholder waits. No money has moved yet. The `cain.003` FinancialInitiation and `cain.004` FinancialResponse handle the actual transfer at clearing, either completing a previously authorised transaction or, for some transaction types, authorising and clearing in a single step.

**Q: How do the dispute messages work together?**

They form a retrieval-then-chargeback path. When a cardholder disputes a charge, the issuer first asks the acquirer for the transaction record with a `cain.021` RetrievalInitiation, answered by `cain.022`. The acquirer then supplies the supporting document, such as a receipt copy, through the `cain.014` RetrievalFulfilmentInitiation and its `cain.015` response. If the dispute is upheld, the issuer returns the transaction to the acquirer with a `cain.027` ChargeBackInitiation, answered by `cain.028`. The sequence lets the parties gather evidence before money is moved back, which is central to how card disputes are resolved.

**Q: Why are almost all cain messages initiation-and-response pairs?**

Because each step of the acquirer-to-issuer conversation is a request that needs an answer: authorise this, clear this, reverse this, retrieve this, charge this back. Pairing an initiation with a response gives every action a definite outcome the sender can act on, and it keeps the protocol symmetric and easy to reason about. The one exception is the `cain.020` Amendment, which corrects data in a previously sent message rather than requesting a new action, so it stands alone.

**Q: How does cain fit with the other ISO 20022 card areas?**

They divide the card rails by leg and purpose. `caaa` carries the acceptor-to-acquirer leg (the merchant terminal talking to its acquirer), `catp` is the ATM protocol, and `cain` carries the acquirer-to-issuer leg between the two institutions. The fraud area `cafr` then moves fraud information about those transactions between the parties. A single card payment can therefore start as a `caaa` exchange at the terminal, travel as a `cain` authorisation and clearing between acquirer and issuer, and, if it turns out to be fraudulent, be reported later through `cafr`.

**Q: What protects the sensitive data in a cain message?**

The card family's data-protection model. Because `cain` messages carry the primary account number, PIN data, and track or chip data across networks between institutions, those sensitive elements are carried in encrypted form rather than in the clear, and messages are authenticated so a receiver can trust their origin. The cryptographic keys that make this work are provisioned and rotated outside the transaction messages themselves. The protection matters precisely because this is interbank traffic on an untrusted path, exactly the threat model card networks are built to withstand.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 card and payment messages](https://www.iso20022.org/payments)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [nexo standards — card payment message specifications](https://www.nexo-standards.org/)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [Claude Code](https://claude.com/product/claude-code)
