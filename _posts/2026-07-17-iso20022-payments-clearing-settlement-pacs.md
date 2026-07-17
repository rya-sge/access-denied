---
layout: post
title: "ISO 20022 for Payments Clearing and Settlement — The pacs Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 payments pacs credit-transfer rtgs cbpr
description: How ISO 20022 models interbank payments through the pacs business area, the flagship of the MT-to-MX migration, covering the FIToFI credit transfer, direct debit, payment status, return, and reversal messages that move money between banks.
image: /assets/article/finance/iso20022-payments-clearing-settlement-pacs.png
isMath: false
---



Of all the areas in ISO 20022, this is the one the industry has spent the most effort migrating to. `pacs`, **payments clearing and settlement**, carries the interbank payments that move money between banks: the credit transfer behind a wire, the status report that confirms it, the return that sends it back. It is the heart of the global shift from the old SWIFT MT messages to ISO 20022 MX, and this article walks through its ten messages and the payment chain they sit in.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What pacs is for

`pacs` is the **financial-institution-to-financial-institution (FI to FI)** layer of payments: the messages banks exchange between themselves to clear and settle a payment. It sits between two neighbouring areas. Payment **initiation** by a customer lives in `pain` (a company instructs its bank to pay); payment **reporting** back to customers lives in `camt` (the statement and notification of what happened). In the middle, `pacs` is how the banks actually move the money.

![Where pacs sits in the payment chain]({{site.url_complet}}/assets/article/finance/pacs-payment-chain-concept.png)

This central position is why `pacs` is the flagship of the MT-to-MX migration. Cross-border correspondent banking, through the CBPR+ guidelines, and domestic real-time gross settlement systems such as the Eurosystem's T2, the UK's CHAPS, and the US Fedwire, have moved or are moving their interbank traffic from MT messages to `pacs`. When people say a bank is "migrating to ISO 20022", they usually mean its `pacs` traffic.

## The pacs message catalogue

The ten messages divide into credit transfers, direct debits, status and exception handling, and a settlement request.

| Identifier | Message | Replaces (MT) |
|------------|---------|---------------|
| `pacs.008` | FIToFICustomerCreditTransfer | MT103 |
| `pacs.009` | FinancialInstitutionCreditTransfer | MT202 / MT202COV |
| `pacs.003` | FIToFICustomerDirectDebit | MT104 |
| `pacs.010` | FinancialInstitutionDirectDebit | — |
| `pacs.002` | FIToFIPaymentStatusReport | MT199 / status |
| `pacs.028` | FIToFIPaymentStatusRequest | — |
| `pacs.004` | PaymentReturn | MTn03 return |
| `pacs.007` | FIToFIPaymentReversal | MTn92 reversal |
| `pacs.029` | MultilateralSettlementRequest | — |

The **credit transfers** are the core. The `pacs.008` **FIToFICustomerCreditTransfer** carries a payment on behalf of customers, the interbank leg of a wire and the ISO 20022 successor to the MT103. The `pacs.009` **FinancialInstitutionCreditTransfer** moves funds between the banks themselves, replacing the MT202, including the cover payment (MT202COV) that settles the interbank side of a customer transfer. The **direct debits** (`pacs.003`, `pacs.010`) pull funds rather than push them. The **status** messages (`pacs.002` report, `pacs.028` request) communicate whether a payment was accepted, rejected, or is pending. The **exception** messages return a payment that cannot be applied (`pacs.004`) or reverse one sent in error (`pacs.007`). The `pacs.029` **MultilateralSettlementRequest** supports settling a set of obligations together.

### Anatomy of a credit transfer

A `pacs.008` opens with a **group header** (`GrpHdr`) carrying the message identifier, creation timestamp, the number of transactions, and settlement information for the batch. Below it, each **credit transfer transaction** (`CdtTrfTxInf`) carries the payment: a payment identification with end-to-end and transaction references, the interbank settlement amount, the charge bearer, and the chain of parties, the debtor and its agent, the creditor and its agent, and any intermediary agents, along with structured remittance information that tells the creditor what the payment is for. That structured remittance data is one of the migration's main prizes: where an MT103 squeezed payment details into limited free-text lines, a `pacs.008` carries them in typed, machine-readable fields.

## The payment chain, message by message

The messages come together in a straightforward interbank credit transfer.

![An interbank credit transfer with status and return]({{site.url_complet}}/assets/article/finance/pacs-credit-transfer-workflow.png)

**The transfer.** The debtor's bank sends a `pacs.008` **FIToFICustomerCreditTransfer** toward the creditor's bank, routed through a clearing system or RTGS. The message names the parties, the amount, and the remittance detail, and the settlement moves the funds between the banks' accounts at the settlement agent.

**The status.** The creditor's bank (or an intermediary) reports the outcome with a `pacs.002` **FIToFIPaymentStatusReport**: accepted, rejected, or pending, with a reason if rejected. A bank that wants to know a payment's status can ask with a `pacs.028` **FIToFIPaymentStatusRequest**. Status reporting is how the sending bank learns whether its payment reached and was accepted by the beneficiary's bank.

**The exceptions.** Not every payment can be applied. If the creditor's bank cannot credit the beneficiary, for example because the account is closed, it sends the funds back with a `pacs.004` **PaymentReturn**, which moves the money in the reverse direction with a reason. If a bank realises it sent a payment in error, it can reverse it with a `pacs.007` **FIToFIPaymentReversal**. The two differ in who initiates and why: a return is the receiver declining, a reversal is the sender withdrawing.

## Conclusion

The `pacs` business area is the interbank engine of payments. Its ten messages move money between banks: the customer and institution credit transfers that replace the MT103 and MT202, the direct debits that pull funds, the status reports that confirm outcomes, and the return and reversal messages that handle payments that cannot stand. It sits between customer initiation in `pain` and customer reporting in `camt`, and because it carries the interbank traffic that market infrastructures and correspondent banking run on, it is the centre of gravity of the whole MT-to-MX migration. Read next to `pain`, `camt`, and the Business Application Header that routes it, `pacs` is where an ISO 20022 payment actually settles.

![Mindmap summarising the ISO 20022 pacs payments clearing and settlement area]({{site.url_complet}}/assets/article/finance/iso20022-payments-clearing-settlement-pacs.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **pacs** | The ISO 20022 payments clearing and settlement business area, carrying interbank (FI-to-FI) payments across ten messages. |
| **FIToFI credit transfer (`pacs.008`)** | The interbank credit transfer on behalf of customers, the ISO 20022 successor to the SWIFT MT103. |
| **FI credit transfer (`pacs.009`)** | The credit transfer between banks for their own account, replacing the MT202, including the cover payment. |
| **Cover payment** | The interbank settlement leg (MT202COV) that funds a customer credit transfer routed through correspondents. |
| **Payment status report (`pacs.002`)** | The message reporting whether a payment was accepted, rejected, or is pending. |
| **Payment return (`pacs.004`)** | The message sending funds back when the receiving bank cannot apply the payment. |
| **Payment reversal (`pacs.007`)** | The message by which the sending bank withdraws a payment it sent in error. |
| **Group header (`GrpHdr`)** | The header of a pacs message carrying the message identifier, timestamp, transaction count, and settlement information. |
| **CBPR+** | The cross-border payments and reporting market-practice guidelines governing correspondent-banking use of ISO 20022. |
| **RTGS** | A real-time gross settlement system, such as T2, CHAPS, or Fedwire, that settles interbank payments individually. |

## Frequently Asked Questions

**Q: What is the difference between pacs, pain, and camt?**

They are three stages of a payment. `pain` (payments initiation) is how a customer instructs its bank to make a payment. `pacs` (payments clearing and settlement) is how banks exchange and settle that payment between themselves. `camt` (cash management) is how the resulting balances and entries are reported back to customers. A single transfer is initiated with a `pain` message, carried between banks with a `pacs.008`, and reported to the payer and payee with `camt` statements and notifications. `pacs` is the interbank middle of the chain.

**Q: What is the difference between pacs.008 and pacs.009?**

Both are credit transfers, but they move different money. The `pacs.008` FIToFICustomerCreditTransfer carries a payment made on behalf of customers, the interbank leg of a customer wire, and replaces the MT103. The `pacs.009` FinancialInstitutionCreditTransfer moves funds between the banks for their own account, replacing the MT202, and includes the cover payment that settles the interbank side of a customer transfer routed through correspondents. In short, `pacs.008` is a customer payment between banks, and `pacs.009` is a bank-to-bank payment.

**Q: Why is pacs the centre of the MT-to-MX migration?**

Because it carries the interbank payment traffic that market infrastructures and correspondent banking depend on. The migration from SWIFT MT messages to ISO 20022 MX is driven by cross-border guidelines (CBPR+) and by domestic real-time gross settlement systems such as T2, CHAPS, and Fedwire, and the messages they are switching are the interbank credit transfers and status reports, which are `pacs`. When a bank is described as migrating to ISO 20022, it is chiefly migrating its `pacs` traffic, which is why this area receives the most attention.

**Q: What is the difference between a payment return and a payment reversal?**

They both undo a payment but from opposite ends. A `pacs.004` PaymentReturn is initiated by the receiving side: the creditor's bank cannot apply the funds, for example because the account is closed, so it sends the money back with a reason. A `pacs.007` FIToFIPaymentReversal is initiated by the sending side: the bank that sent the payment realises it did so in error and withdraws it. A return is the receiver declining the money; a reversal is the sender taking it back.

**Q: What does a bank gain from structured remittance information in a pacs.008?**

Automated reconciliation. An MT103 carried payment details in a few limited free-text lines, which a beneficiary often had to read and interpret by hand to match a payment to an invoice. A `pacs.008` carries the same details in typed, structured fields, including structured remittance information, so the beneficiary's system can match the payment to what it settles automatically. This richer data is one of the main practical benefits of the migration, alongside longer identifiers and clearer party information.

**Q: How does pacs relate to the Business Application Header?**

A `pacs` message travels wrapped in a Business Application Header (`head.001`), which carries the routing and control data: who is sending it, to whom, which message definition it is, and a signature. The header lets a clearing system or RTGS route and validate the payment without parsing its content, and it identifies the exact `pacs` version so the receiver can process it. In the market infrastructures that run `pacs` traffic, the header is a required envelope, which is why interbank ISO 20022 payments are always a header plus a `pacs` payload.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 payments messages](https://www.iso20022.org/payments)
- [SWIFT — ISO 20022 for financial institutions and CBPR+](https://www.swift.com/standards/iso-20022/iso-20022-programme)
- [ECB — TARGET Services (T2) and ISO 20022](https://www.ecb.europa.eu/paym/target/consolidation/html/index.en.html)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [Claude Code](https://claude.com/product/claude-code)
