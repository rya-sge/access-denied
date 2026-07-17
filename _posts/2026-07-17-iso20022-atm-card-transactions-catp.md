---
layout: post
title: "ISO 20022 for ATM Card Transactions — The catp Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 atm cards catp payments security
description: How ISO 20022 models ATM card transactions through the catp business area, covering the withdrawal, deposit, transfer, inquiry and PIN management flows between an ATM and its host, and the message-level encryption and MAC that protect them.
image: /assets/article/finance/iso20022-atm-card-transactions-catp.png
isMath: false
---



Most ISO 20022 business areas describe messages between banks and market infrastructures. The `catp` area is different: it describes the conversation between a single **ATM** and the **host** that authorises what it does. Every cash withdrawal, balance inquiry, deposit, transfer, and PIN change is a short, protected exchange of `catp` messages. This article walks through the seventeen messages in the ATM card transactions package (`catp.001` to `catp.017`), the request-then-confirm pattern they follow, and the message-level security that card messaging carries and most other ISO 20022 areas do not.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What catp is for

The card world is usually drawn as four corners: the cardholder, the acceptor (here the ATM), the acquirer, and the issuer. The `catp` business area covers the first leg of that chain, between the ATM and the acquiring **ATM Manager** (the host that drives the terminal and authorises transactions, forwarding to the card scheme and issuer when needed). It is one of two ISO 20022 areas for automated teller machines. Its sibling `catm` handles **management** (terminal configuration, cryptographic key download, and reporting), while `catp` handles the **transactions** themselves.

![Where the catp protocol sits between the ATM, its host, and the card rails]({{site.url_complet}}/assets/article/finance/catp-atm-topology-concept.png)

This positioning explains why `catp` looks unlike, say, the collateral or clearing areas. It is a real-time device protocol. The messages are short, they are exchanged in tightly correlated pairs, and they carry data that must never travel in the clear, such as the customer's PIN. The design reflects decades of card-network practice carried into an ISO 20022 syntax.

## The anatomy of a catp message

Every `catp` message shares the same three-part shape, visible directly in the schemas. Taking the withdrawal request (`catp.001`), the top-level structure is a header, a body, and a security trailer.

![The three-part structure of a catp message]({{site.url_complet}}/assets/article/finance/catp-message-anatomy-concept.png)

- **Header (`Hdr`, type `Header31`)** carries the message function (`MsgFctn`), the protocol version (`PrtcolVrsn`), an exchange identifier (`XchgId`), a creation timestamp (`CreDtTm`), and the initiating party (`InitgPty`). The exchange identifier is what ties a response back to its request and a completion back to its authorisation.
- **Body**, which the schema models as a choice: the message carries *either* a clear body (`ATMWdrwlReq`) *or* a protected one (`PrtctdATMWdrwlReq`). The protected form wraps the same content in a `ContentInformationType10` structure, which is ISO 20022's envelope for enveloped and authenticated data (encryption plus integrity).
- **Security trailer (`SctyTrlr`, type `ContentInformationType15`)** carries a **MAC** computed over the message, so the receiver can detect any tampering in transit.

This built-in protection is the feature that distinguishes card messaging. Because a withdrawal request contains the encrypted PIN block and card data, the protocol assumes a hostile network: the sensitive body is encrypted, and the whole message is authenticated with a MAC. The keys that make this work are provisioned separately, through the `catm` management area, and are out of scope for the transaction messages themselves.

## The catp message catalogue

The ATM card transactions package defines seventeen messages. They fall into a handful of operations, and within each operation they follow one of two patterns: a two-message **request/response** for authorisation, and, for anything that physically dispenses or accepts value, an additional two-message **completion advice/acknowledgement** that reports what actually happened.

| Identifier | Message | Group |
|------------|---------|-------|
| `catp.001` | ATMWithdrawalRequest | Withdrawal |
| `catp.002` | ATMWithdrawalResponse | Withdrawal |
| `catp.003` | ATMWithdrawalCompletionAdvice | Withdrawal |
| `catp.004` | ATMWithdrawalCompletionAcknowledgement | Withdrawal |
| `catp.006` | ATMInquiryRequest | Inquiry |
| `catp.007` | ATMInquiryResponse | Inquiry |
| `catp.008` | ATMCompletionAdvice | Generic completion |
| `catp.009` | ATMCompletionAcknowledgement | Generic completion |
| `catp.010` | ATMPINManagementRequest | PIN management |
| `catp.011` | ATMPINManagementResponse | PIN management |
| `catp.012` | ATMDepositRequest | Deposit |
| `catp.013` | ATMDepositResponse | Deposit |
| `catp.014` | ATMDepositCompletionAdvice | Deposit |
| `catp.015` | ATMDepositCompletionAcknowledgement | Deposit |
| `catp.016` | ATMTransferRequest | Transfer |
| `catp.017` | ATMTransferResponse | Transfer |
| `catp.005` | ATMReject | Error handling |

The withdrawal and deposit groups have the full four-message lifecycle because value physically moves. The inquiry, PIN management, and transfer groups use only request and response, because the outcome is known the moment the host answers. The generic completion pair (`catp.008` / `catp.009`) provides a completion vehicle for operations that do not have their own dedicated completion message. And `catp.005`, the reject, sits outside every group: it is the protocol's answer to a message it cannot process at all.

## The two-phase pattern, message by message

The withdrawal flow is the clearest illustration of why card transactions need two phases rather than one.

![ATM cash withdrawal as a two-phase catp exchange]({{site.url_complet}}/assets/article/finance/catp-withdrawal-workflow.png)

**Phase one: authorisation.** The cardholder inserts a card, enters a PIN, and asks for cash. The ATM sends a `catp.001` **ATMWithdrawalRequest** to the host, with the PIN block and card data in the encrypted body. The host authorises the amount, routing to the issuer through the card scheme where required, and replies with a `catp.002` **ATMWithdrawalResponse** that approves or declines. At this point money has been reserved but no cash has moved.

**Phase two: completion.** Only now does the ATM try to dispense the notes, and this is where reality can diverge from the authorisation. The cash may dispense fully, dispense partially, or jam and fail entirely. The ATM reports the true outcome in a `catp.003` **ATMWithdrawalCompletionAdvice**, and the host confirms receipt with a `catp.004` **ATMWithdrawalCompletionAcknowledgement**. If the cash never came out, the completion advice is what tells the host to reverse the authorisation so the customer is not debited for money they never received.

Separating authorisation from completion is the whole point. A single request/response cannot express "you were approved but the machine failed to pay you", and for a device that hands over physical banknotes that gap is exactly where customer disputes and losses live. The deposit flow mirrors the same shape with `catp.012` to `catp.015`: authorise the deposit, physically accept the cash or cheques, then advise and acknowledge the counted result.

**The lighter flows.** An **inquiry** (`catp.006` / `catp.007`) retrieves information such as an available balance or the services the card is allowed to use, and needs no completion because nothing is dispensed. **PIN management** (`catp.010` / `catp.011`) covers changing or unblocking a PIN, again a request and a response, with the sensitive PIN data protected in the body. A **transfer** between accounts (`catp.016` / `catp.017`) is authorised and answered in a single exchange. Where any of these does need to record a definitive completion, the generic `catp.008` / `catp.009` pair is available.

**Rejection.** When a message arrives that the receiver cannot parse or process, for example because the protocol version is wrong or the security check fails, the answer is a `catp.005` **ATMReject** rather than a normal response. It keeps protocol errors distinct from business declines: a decline is a valid answer to a valid request, while a reject says the request itself could not be handled.

## Protection built into every message

It is worth returning to security, because it runs through every message rather than sitting in one of them. Three mechanisms combine.

First, **confidentiality**: the body of a message can be sent as protected content, encrypting the PIN block, track or chip data, and account identifiers so they are unreadable on the wire. Second, **integrity and authenticity**: the security trailer carries a MAC over the message, so a receiver detects any alteration and confirms the sender holds the shared key. Third, **correlation**: the header's exchange identifier binds a request, its response, and any completion into one traceable exchange, which frustrates replay and misattribution. The cryptographic keys behind the first two are loaded and rotated through the `catm` management area, keeping key administration separate from the transaction traffic that relies on it.

## Conclusion

The `catp` business area applies ISO 20022 to the point where a customer meets a machine. Seventeen messages cover the ATM's repertoire: withdrawals and deposits with a full authorise-then-complete lifecycle, inquiries, PIN management and transfers as simple request and response, a generic completion pair, and a reject for messages that cannot be processed. Two design choices define the area. The request/response then completion-advice/acknowledgement pattern separates authorisation from the physical outcome, which matters when a machine can approve a withdrawal yet fail to dispense it. And the three-part message shape, header plus clear-or-protected body plus MAC trailer, builds encryption and authentication into every exchange, because the traffic carries PINs and card data across an untrusted network. Read next to the `catm` management area that provisions its keys, `catp` completes the ISO 20022 picture of the ATM.

![Mindmap summarising ISO 20022 ATM card transactions with the catp message set]({{site.url_complet}}/assets/article/finance/iso20022-atm-card-transactions-catp.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **catp** | The ISO 20022 business area for ATM card transactions, comprising the seventeen messages `catp.001` to `catp.017`. |
| **catm** | The sibling ISO 20022 area for ATM management: terminal configuration, cryptographic key download, and reporting. |
| **ATM Manager** | The acquiring host that drives the ATM, authorises its transactions, and forwards to the card scheme and issuer as needed. |
| **Exchange identifier (`XchgId`)** | A header field that ties a response and any completion back to the original request, forming one traceable exchange. |
| **Message function (`MsgFctn`)** | A header code identifying what a message does, so a receiver can dispatch it without inspecting the whole body. |
| **Protected body** | The encrypted form of a message body (for example `PrtctdATMWdrwlReq`), carried as enveloped and authenticated content instead of clear data. |
| **Security trailer (`SctyTrlr`)** | The trailing element carrying a MAC computed over the message, used to detect tampering and authenticate the sender. |
| **MAC** | Message authentication code, a keyed checksum proving a message was not altered and came from a holder of the shared key. |
| **Completion advice** | The message an ATM sends after a physical action, reporting the true outcome (dispensed, partial, or failed) so the host can finalise or reverse. |
| **ATMReject (`catp.005`)** | The protocol-level negative response returned when a message cannot be parsed or processed, as distinct from a business decline. |

## Frequently Asked Questions

**Q: Why does an ATM withdrawal need four messages instead of one request and one response?**

Because authorising a withdrawal and physically dispensing the cash are two separate events, and either can succeed while the other fails. The request (`catp.001`) and response (`catp.002`) reserve the funds, but the cash has not moved yet. Only after the ATM tries to dispense does the real outcome become known, and it might be a full dispense, a partial one, or a jam. The completion advice (`catp.003`) reports that actual outcome and the acknowledgement (`catp.004`) confirms the host received it. Without the second phase there would be no reliable way to reverse an authorisation when the machine approved a withdrawal but failed to pay it out.

**Q: What are the three parts of a catp message, and what does each do?**

A header, a body, and a security trailer. The header (`Hdr`) carries routing and correlation data: the message function, protocol version, exchange identifier, timestamp, and initiating party. The body carries the operation's content and is sent either in the clear or, more usually for sensitive data, as an encrypted protected element. The security trailer (`SctyTrlr`) carries a MAC computed over the message so the receiver can verify it was not tampered with. Together they let a receiver route the message, read its content only if authorised, and trust that it is genuine.

**Q: Which catp flows use only a request and response, and why?**

Inquiries (`catp.006` / `catp.007`), PIN management (`catp.010` / `catp.011`), and transfers (`catp.016` / `catp.017`). These need only two messages because their result is fully determined the moment the host answers: an inquiry returns information, a PIN change either succeeds or not, and a transfer is booked or declined. Nothing is physically dispensed or accepted, so there is no later divergence between an authorisation and a physical outcome to report. Withdrawals and deposits, which do move cash, add the completion advice and acknowledgement for exactly that reason.

**Q: How does catp differ from catm, and why are they separate?**

`catp` carries the transactions an ATM performs: withdrawals, deposits, transfers, inquiries, and PIN changes. `catm` carries the management of the terminal itself: downloading configuration, provisioning and rotating cryptographic keys, and collecting operational reports. They are separate because they have different lifecycles and trust requirements. Transaction traffic is high-frequency and customer-driven; management traffic is periodic and administrative. Keeping key provisioning in `catm` also means the keys that protect `catp` messages are administered on their own channel rather than mixed into the transaction flow that depends on them.

**Q: What is the difference between an ATMReject and a declined transaction?**

A decline is a valid business answer to a valid request: the host understood a withdrawal request and answered that it will not authorise it, for example for insufficient funds. That answer travels in a normal response message such as `catp.002`. An `ATMReject` (`catp.005`) is a protocol-level failure: the message could not be processed at all, perhaps because the protocol version is unsupported, the structure is invalid, or the MAC did not verify. Keeping the two distinct lets the ATM tell the difference between "your request was refused" and "your message was never understood", which call for different handling.

**Q: How do the header's exchange identifier and the security mechanisms work together to prevent fraud?**

They address different attacks that combine into a defence. The encrypted body keeps the PIN and card data confidential, so an eavesdropper on the network cannot read them. The MAC in the security trailer proves the message was not altered and came from a party holding the shared key, so an attacker cannot forge or tamper with a message. The exchange identifier in the header binds a request, its response, and its completion into one correlated exchange, so a captured message cannot be replayed as if it belonged to a different transaction. Confidentiality, integrity, and correlation together mean an attacker can neither read, forge, nor replay the traffic, which is the threat model a device on an untrusted network must assume.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 card and payment messages](https://www.iso20022.org/payments)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [nexo standards — card payment message specifications](https://www.nexo-standards.org/)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [Claude Code](https://claude.com/product/claude-code)
