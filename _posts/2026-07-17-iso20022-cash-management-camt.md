---
layout: post
title: "ISO 20022 for Cash Management — The camt Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation
tags: iso20022 swift camt cash-management statement payments
description: A guided tour of ISO 20022's camt (cash management) business area, from the camt.052/053/054 reporting trio that replaces SWIFT MT940/942/900/910 to payment cancellation, investigations, liquidity, and market-infrastructure query messages.
image: /assets/article/finance/iso20022-cash-management-camt.png
isMath: false
---



If you have ever downloaded a machine-readable bank statement, requested that a wrong payment be recalled, or watched a treasury system pull an intraday balance, you have touched the `camt` business area of ISO 20022. Cash management is the broadest and among the most widely deployed corners of the standard: ninety-nine message definitions covering account reporting, payment cancellation and investigation, liquidity, and the operation of the market infrastructures that settle central-bank money. This article organises that sprawl into families, goes deep on the three or four that matter most in practice, and shows how the flagship reporting messages replace the SWIFT MT statements banks have sent for decades.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What camt covers, and why it is so large

`camt` is the ISO 20022 business area for **cash management**: everything a party needs to know and do about balances and movements on a cash account, short of instructing the payment itself. Payment initiation lives in `pain`, interbank payment clearing in `pacs`; `camt` is the reporting, exception handling, and account administration that surrounds them.

Its size comes from serving several very different audiences with one dictionary. A corporate treasurer consuming an end-of-day statement, two banks negotiating the recall of a mistaken transfer, and a central bank operating a real-time gross settlement system all use `camt` messages, and each community needs its own vocabulary. The result is one business area with a dozen functional families. As with every ISO 20022 message, each has a four-part identifier, for example `camt.053.001.14`: business area `camt`, message number `053`, variant `001`, version `14`.

The families break down as follows.

| Family | Representative messages | Purpose |
|--------|------------------------|---------|
| Account reporting | `camt.052`, `camt.053`, `camt.054`, `camt.060` | Report balances and transactions on an account |
| Exceptions and investigations | `camt.055`, `camt.056`, `camt.029`, `camt.110`, `camt.111` | Cancel, modify, and investigate payments |
| Case management | `camt.026` to `camt.039` | Administer an investigation case |
| Liquidity | `camt.050`, `camt.051` | Move liquidity between accounts |
| Notification to receive | `camt.057`, `camt.058`, `camt.059` | Announce expected incoming funds |
| Market-infrastructure management | `camt.003` to `camt.021`, `camt.046` to `camt.049`, `camt.069` to `camt.071`, `camt.101` to `camt.104` | Query and administer an RTGS or CSD system |
| Intra-balance movement | `camt.066` to `camt.085` | Move cash between sub-balances (T2S) |
| Fund cash forecast | `camt.040` to `camt.045` | Report investment-fund cash flows |
| Pay-in | `camt.061`, `camt.062`, `camt.063` | Schedule pay-ins to a settlement system |
| Billing and charges | `camt.076`, `camt.077`, `camt.086`, `camt.105`, `camt.106` | Report bank service charges |
| Cheques | `camt.107`, `camt.108`, `camt.109` | Present and stop cheques |
| Cash deposit and withdrawal | `camt.113` to `camt.116` | Instruct branch or agent cash operations |

The three sections that follow take the families that dominate real traffic: account reporting, exceptions and investigations, and the management and liquidity messages used by market infrastructures.

## Account reporting: the camt.05x trio

The most deployed `camt` messages are the reporting trio and the request that pulls them.

- **`camt.052` BankToCustomerAccountReport** is an intraday or interim report, sent one or many times during the day.
- **`camt.053` BankToCustomerStatement** is the definitive end-of-day statement.
- **`camt.054` BankToCustomerDebitCreditNotification** notifies individual debits and credits as they post.
- **`camt.060` AccountReportingRequest** is how a customer asks the bank to send one of the above.

These are the ISO 20022 successors to the SWIFT MT statements that treasuries have consumed for decades: `camt.053` replaces the MT940 customer statement (and MT950 statement message), `camt.052` replaces the MT941/MT942 interim reports, and `camt.054` replaces the MT900 and MT910 debit and credit confirmations. The migration from MT to MX across cross-border payments and domestic market infrastructures has made the `camt.05x` set the modern default for account information.

### Anatomy of a statement

A `camt.053` is a structured document, not a flat list of lines. Its shape is worth knowing because `camt.052` and `camt.054` share it.

![The nested structure of a camt.053 bank-to-customer statement]({{site.url_complet}}/assets/article/finance/camt-statement-anatomy-concept.png)

At the top sits a **group header** (`GrpHdr`) with the message identifier and creation timestamp. Below it comes one or more **statements** (`Stmt`), each tied to an **account** (`Acct`) and its servicer. Each statement carries **balances** (`Bal`), typed by code, so an opening booked balance (`OPBD`) and a closing booked balance (`CLBD`) frame the day, with intermediate and available balances as needed. It then carries a series of **entries** (`Ntry`), and each entry has an amount, a credit-or-debit indicator (`CdtDbtInd`), a status (booked or pending), a **booking date** and a **value date**. An entry can be broken down further into **entry details** and **transaction details** (`NtryDtls`, `TxDtls`) that carry references, the parties involved, and structured remittance information. That nesting is what lets a single statement line carry enough machine-readable detail for a treasury system to reconcile it automatically, which the old fixed-format MT statement struggled to do.

![How a customer requests and receives account information]({{site.url_complet}}/assets/article/finance/camt-account-reporting-workflow.png)

In practice a customer registers for reporting or sends a `camt.060` to request it, receives `camt.052` reports through the day and `camt.054` notifications as entries post, and receives the authoritative `camt.053` after the books close.

## Exceptions and investigations

Payments go wrong: they are sent twice, sent for the wrong amount, or sent to the wrong beneficiary. The exceptions and investigations family is how banks and their customers try to fix them after the fact. It is a genuinely two-sided, negotiated process, which is why it has more message types than any other `camt` family.

![Cancelling a payment and escalating to an investigation]({{site.url_complet}}/assets/article/finance/camt-cancellation-investigation-workflow.png)

The entry points are the cancellation requests. A customer who wants to recall a payment it initiated sends its bank a **`camt.055` CustomerPaymentCancellationRequest**. A bank that needs another bank to return funds sends a **`camt.056` FIToFIPaymentCancellationRequest**, the interbank recall that replaces the legacy MT n92 request for cancellation. Where the payment should be changed rather than cancelled, **`camt.087` RequestToModifyPayment** applies. The outcome of any of these, whether the funds were returned or the request refused, comes back in a **`camt.029` ResolutionOfInvestigation**.

Around these sit the older exception messages: **`camt.026` UnableToApply** when a bank cannot process a payment because information is missing, **`camt.027` ClaimNonReceipt** when a beneficiary says money never arrived, and **`camt.028` AdditionalPaymentInformation** to supply missing detail. The classic model wrapped all of this in a *case*, administered by a run of case-management messages (`camt.030` NotificationOfCaseAssignment, `camt.031` RejectInvestigation, `camt.032` CancelCaseAssignment, `camt.033`/`camt.034` request and supply a duplicate, `camt.038`/`camt.039` case status).

More recently the standard introduced a streamlined pair, **`camt.110` InvestigationRequest** and **`camt.111` InvestigationResponse**, that generalise the request-and-answer of an enquiry without the heavier case scaffolding. In a modern flow a `camt.056` recall may resolve directly with a `camt.029`, or escalate into a `camt.110`/`camt.111` exchange when the receiving bank needs to enquire before it can resolve.

## Managing a market infrastructure

A large slice of `camt` exists to operate real-time gross settlement systems and central securities depositories, where participants hold accounts of central-bank money and the operator must expose those accounts for query and control. These messages follow a consistent verb pattern built from a small set of actions applied to a small set of objects.

The verbs are **Get**, **Return**, **Modify**, **Delete**, and **Create**; the objects are accounts, transactions, limits, members, reservations, and standing orders. So a participant sends a `camt.003` **GetAccount** and receives a `camt.004` **ReturnAccount**; queries a payment with `camt.005` **GetTransaction** and receives `camt.006` **ReturnTransaction**, or acts on it with `camt.007` **ModifyTransaction** or `camt.008` **CancelTransaction**. Bilateral and multilateral **limits** are administered with `camt.009` to `camt.012` and `camt.101`; **members** with `camt.013` to `camt.015` and `camt.104`; **reservations** of liquidity with `camt.046` to `camt.049` and `camt.103`; and **standing orders** with `camt.024`, `camt.069` to `camt.071`, and `camt.102`. Supporting queries return reference data the operator publishes: `camt.016`/`camt.017` for currency exchange rates, `camt.018`/`camt.019` for business-day information, and `camt.020`/`camt.021` for general business information such as broadcasts.

Two further messages actually move money between accounts inside such a system: **`camt.050` LiquidityCreditTransfer** and **`camt.051` LiquidityDebitTransfer**, used to fund and defund settlement accounts and to sweep liquidity between them. Alongside them, the **notification to receive** trio (`camt.057` NotificationToReceive, `camt.058` its cancellation advice, and `camt.059` its status report) lets a party warn an account servicer that incoming funds are expected, so the servicer can anticipate them.

## The rest of the area, in brief

The remaining families are narrower but fill out the picture of what "cash management" spans.

- **Intra-balance movement** (`camt.066` to `camt.085`) moves cash between sub-positions of a securities account, the machinery behind collateral and settlement cash in TARGET2-Securities. It has its own instruction, status, confirmation, modification, cancellation, and query messages.
- **Fund cash forecast** (`camt.040` to `camt.045`) reports estimated and confirmed cash flows in and out of an investment fund, so a transfer agent can manage subscriptions and redemptions.
- **Pay-in** (`camt.061` PayInCall, `camt.062` PayInSchedule, `camt.063` PayInEventAcknowledgement) schedules and calls funding into a settlement system of the kind used for currency settlement.
- **Billing and charges** (`camt.076`, `camt.077`, `camt.086` bank services billing, plus `camt.105`/`camt.106` for charges) report what a bank charges for its services.
- **Cheques** (`camt.107` presentment notification, `camt.108` cancellation or stop request, `camt.109` its report) cover the cheque instrument.
- **Cash deposit and withdrawal** (`camt.113` to `camt.116`) instruct and track physical cash operations at a branch or agent.

## Conclusion

The `camt` business area is cash management in the full sense: not only the statement a customer reads each morning, but the recall of a mistaken payment, the query a bank runs against a settlement system, the liquidity it sweeps between accounts, and the charges it bills. Ninety-nine messages is a lot, but they organise into families around a few shared ideas: a nested, machine-readable account statement in the `camt.05x` trio; a negotiated request-and-resolution pattern for exceptions; and a Get/Return/Modify/Delete/Create verb set for administering an infrastructure. Its flagship reporting messages are the ISO 20022 replacements for the MT940, MT942, and MT900/MT910 statements, which is why, of all the areas in this series, `camt` is the one a working treasury or operations team is most likely to meet first.

![Mindmap summarising the ISO 20022 cash management area and its camt families]({{site.url_complet}}/assets/article/finance/iso20022-cash-management-camt.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **camt** | The ISO 20022 cash management business area, covering account reporting, exceptions, liquidity, and infrastructure administration across ninety-nine message definitions. |
| **camt.053** | The Bank-to-Customer Statement, the definitive end-of-day account statement and the ISO 20022 successor to the SWIFT MT940. |
| **camt.052** | The Bank-to-Customer Account Report, an intraday or interim report, successor to the MT941/MT942. |
| **camt.054** | The Bank-to-Customer Debit/Credit Notification, advising individual postings, successor to the MT900/MT910. |
| **Entry (`Ntry`)** | A single movement on a statement, carrying amount, credit-or-debit indicator, status, booking date, and value date. |
| **Balance (`Bal`)** | A typed balance on a statement, such as an opening booked (`OPBD`) or closing booked (`CLBD`) balance. |
| **camt.056** | The FI-to-FI Payment Cancellation Request, the interbank recall of a payment, successor to the MT n92 request for cancellation. |
| **camt.029** | The Resolution of Investigation, reporting the outcome of a cancellation, claim, or investigation. |
| **Get/Return pattern** | The query convention for market-infrastructure objects, where a Get message (e.g. `camt.003`) is answered by a matching Return (`camt.004`). |
| **Liquidity transfer** | A movement of funds between accounts inside a settlement system, instructed with `camt.050` (credit) or `camt.051` (debit). |

## Frequently Asked Questions

**Q: What is the difference between camt.052, camt.053, and camt.054?**

They report account activity at different moments and granularities. `camt.053` is the Bank-to-Customer Statement, the authoritative end-of-day record of a period's balances and entries. `camt.052` is the Bank-to-Customer Account Report, an intraday or interim view sent one or more times before the books close, used for real-time cash positioning. `camt.054` is the Bank-to-Customer Debit/Credit Notification, which advises individual postings as they happen rather than summarising a period. A treasury typically uses `camt.052` through the day for positioning, `camt.054` to be alerted to specific movements, and `camt.053` as the definitive statement to reconcile against.

**Q: How do the camt reporting messages relate to the old SWIFT MT statements?**

They are the ISO 20022 replacements. `camt.053` replaces the MT940 customer statement and the MT950 statement message; `camt.052` replaces the MT941 and MT942 interim reports; and `camt.054` replaces the MT900 and MT910 debit and credit confirmations. The MX messages carry the same information as the MT ones but in a nested, richly typed XML structure, which lets a statement line carry structured references, party details, and remittance information that a fixed-format MT line could not hold. The industry-wide migration from MT to MX is why these `camt` messages are now the default for account information.

**Q: Why does the exceptions and investigations family have so many message types?**

Because resolving a problem payment is a negotiation, not a single instruction, and several distinct situations can arise. A customer may want to recall its own payment (`camt.055`) or a bank may recall from another bank (`camt.056`); a payment might need modifying rather than cancelling (`camt.087`); a beneficiary might claim non-receipt (`camt.027`); a bank might be unable to apply a payment for missing information (`camt.026`). Each of these needs its own request, an outcome has to be reported back (`camt.029`), and the classic model wrapped the whole exchange in a case with its own administrative messages. The newer `camt.110`/`camt.111` investigation pair streamlines the request-and-answer without the full case scaffolding. The variety reflects the many ways a payment can go wrong and the back-and-forth needed to put each right.

**Q: What is the Get/Return/Modify/Delete/Create pattern, and where is it used?**

It is the query and administration convention for the messages that operate a market infrastructure such as a real-time gross settlement system. A small set of verbs (Get, Return, Modify, Delete, Create) is applied to a small set of objects (accounts, transactions, limits, members, reservations, standing orders). A participant reads an object with a Get message and receives the answer in the matching Return, and changes it with Modify, Delete, or Create. For example `camt.003` GetAccount is answered by `camt.004` ReturnAccount, and `camt.009` to `camt.012` get, return, modify, and delete a limit. The pattern gives the operator and its participants a uniform, predictable interface to the state of the system.

**Q: Where does camt sit relative to pain and pacs?**

They divide the payment lifecycle. `pain` (payments initiation) is how a customer instructs its bank to make a payment. `pacs` (payments clearing and settlement) is how banks exchange that payment between themselves. `camt` (cash management) is everything about the account and the exceptions around those payments: reporting the resulting balances and entries, cancelling or investigating a payment that went wrong, and administering the accounts and liquidity in a settlement system. A single cross-border transfer might be initiated with a `pain` message, carried between banks with a `pacs` message, reported to the payer and payee with `camt.054` and `camt.053`, and, if it was a mistake, recalled with a `camt.056`.

**Q: Why is a camt.053 statement nested rather than a flat list of lines?**

Because a flat line cannot carry enough structured detail to reconcile automatically. A `camt.053` groups its content: a group header identifies the message, each statement is tied to an account and carries typed balances, and each entry carries an amount, a credit-or-debit indicator, a status, and booking and value dates. An entry can then expand into entry and transaction details holding references, the parties to the underlying payment, and structured remittance information. That hierarchy lets a treasury system match an entry to the invoice or instruction it settles without a human reading a free-text narrative, which is the main practical gain of the ISO 20022 statement over the older fixed-format MT one.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 payments messages](https://www.iso20022.org/payments)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [SWIFT — ISO 20022 programme and MT to MX migration](https://www.swift.com/standards/iso-20022/iso-20022-programme)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [Claude Code](https://claude.com/product/claude-code)
