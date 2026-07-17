---
layout: post
title: "ISO 20022 for Trade Services Management — The tsmt Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation
tags: iso20022 trade-finance bpo tsmt baseline matching
description: How ISO 20022 modelled the Bank Payment Obligation and the Trade Services Utility through the tsmt business area, covering the baseline, data set matching, status management, and reporting that drive a conditional interbank payment obligation.
image: /assets/article/finance/iso20022-trade-services-management-tsmt.png
isMath: false
---



Between the open-account trade where a buyer simply pays later and the letter of credit where a bank guarantees payment against documents sits a middle option: the **Bank Payment Obligation (BPO)**, an irrevocable promise by one bank to another to pay once trade data is matched by a machine rather than checked by hand. ISO 20022 modelled the BPO and its matching in the `tsmt` business area: **trade services management**. This article covers the fifty-two `tsmt` messages, the baseline-and-matching mechanism at their core, and the history that makes this area a cautionary tale as much as a technical one.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What tsmt was for

`tsmt` supported the **Trade Services Utility (TSU)** and the Bank Payment Obligation. The idea was to automate what a letter of credit does manually. In a letter of credit, a bank pays the seller once it checks paper documents against the credit's terms. The BPO replaces that manual document check with **electronic data matching**: the buyer's and seller's banks agree a **baseline** of expected trade data, then submit the actual data (from the purchase order, invoice, transport, and insurance) to a matching engine, and the payment obligation becomes due when the data matches.

![The BPO model: two banks and a matching engine]({{site.url_complet}}/assets/article/finance/tsmt-bpo-concept.png)

The participants are the buyer's bank (which takes on the obligation), the seller's bank (which receives it), and a **transaction matching application** that compares the submitted data against the baseline. The BPO itself is governed by the ICC's Uniform Rules for Bank Payment Obligations (URBPO 750).

## The tsmt message catalogue

The fifty-two messages support the phases of a BPO transaction: establishing the baseline, matching data sets against it, managing the transaction's status, and reporting throughout.

| Group | Representative messages | Purpose |
|-------|------------------------|---------|
| Baseline | `tsmt.019`, `tsmt.010`, `tsmt.011`, `tsmt.009` | Establish, match, report, and amend the baseline |
| Data set matching | `tsmt.014`, `tsmt.013`, `tsmt.020`, `tsmt.022` | Submit and match commercial data, accept or reject mismatches |
| Status management | `tsmt.025`, `tsmt.026`, `tsmt.031` to `tsmt.036`, `tsmt.040` | Change and extend the transaction's status |
| Reports | `tsmt.002`, `tsmt.041`, `tsmt.018`, `tsmt.015` | Activity, transaction, push-through, and delta reports |
| Amendment | `tsmt.005` to `tsmt.008` | Accept or reject amendments |
| Other | `tsmt.044`, `tsmt.049`, `tsmt.053` | Intent to pay, role acceptance, invoice reconciliation |

The **baseline** is the anchor. The `tsmt.019` **InitialBaselineSubmission** carries a submission identifier, a submitter reference, and the baseline itself, which frames the expected transaction. The matching engine compares the two banks' submissions and issues a `tsmt.010` **BaselineMatchReport**; once matched, the baseline is established and the BPO exists. The **data set matching** group then carries the actual commercial data: a `tsmt.014` **DataSetSubmission** presents invoice, transport, or insurance data, and a `tsmt.013` **DataSetMatchReport** states whether it matches the baseline, with mismatch-acceptance and rejection messages to resolve differences. The **status** and **report** groups track and communicate where a transaction stands.

## How a BPO transaction works

The core flow is baseline establishment followed by data matching.

![Baseline establishment and data set matching]({{site.url_complet}}/assets/article/finance/tsmt-baseline-matching-workflow.png)

**Establish the baseline.** The buyer's bank and the seller's bank each submit their view of the expected transaction with a `tsmt.019` **InitialBaselineSubmission**. The matching engine compares them and returns a `tsmt.010` **BaselineMatchReport** to both. When they match, the baseline is established and the Bank Payment Obligation comes into being: the buyer's bank is now conditionally obliged to pay.

**Match the data.** As the trade progresses, the seller ships the goods and its bank submits the commercial data, invoice, transport, insurance, with a `tsmt.014` **DataSetSubmission**. The engine checks it against the baseline and issues a `tsmt.013` **DataSetMatchReport**. If the data matches, the condition of the obligation is met and payment is due; the parties drive the transaction's status forward with `tsmt.025` **StatusChangeNotification** messages. If it does not, a `tsmt.022` **MisMatchRejection** or a `tsmt.020` acceptance resolves the difference. The whole exchange is data against data, with no human reading documents.

## Why this area is also a lesson

`tsmt` is technically complete and conceptually elegant, but its real-world history is instructive. The Bank Payment Obligation was launched with ICC backing and a SWIFT matching platform, yet it never achieved broad adoption: corporates and banks largely stayed with letters of credit and open-account trade, and SWIFT decommissioned the Trade Services Utility that hosted the matching in 2020. The messages remain a precise model of automated trade-data matching, but the instrument they served did not displace the practices it was designed to modernise.

That outcome echoes a theme seen elsewhere in ISO 20022: a clean, well-specified message set is necessary but not sufficient for adoption, which also needs the market to want the change. The BPO asked banks and corporates to trust data matching in place of document examination, and the incentive to switch proved too weak. `tsmt` is worth reading both as a model of how conditional, data-driven interbank obligations can be expressed, and as a reminder that standards succeed on economics as much as on design.

## Conclusion

The `tsmt` business area modelled the Bank Payment Obligation and the Trade Services Utility that supported it. Its fifty-two messages establish a baseline between the buyer's and seller's banks, match submitted commercial data against it, manage the transaction's status, and report throughout, replacing the manual document check of a letter of credit with electronic data matching. The mechanism is elegant, but the instrument saw limited uptake and SWIFT retired the matching platform in 2020, which makes the area both a technical reference and a case study in why adoption needs more than a good standard. Read next to the trade services and trade services initiation areas, `tsmt` is the automated-matching chapter of ISO 20022's trade-finance story.

![Mindmap summarising the ISO 20022 tsmt trade services management area]({{site.url_complet}}/assets/article/finance/iso20022-trade-services-management-tsmt.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **tsmt** | The ISO 20022 trade services management business area, which modelled the Bank Payment Obligation and the Trade Services Utility across fifty-two messages. |
| **Bank Payment Obligation (BPO)** | An irrevocable conditional promise by one bank to another to pay once submitted trade data matches an agreed baseline. |
| **Trade Services Utility (TSU)** | The SWIFT matching platform that hosted BPO data matching, decommissioned in 2020. |
| **Baseline** | The agreed record of a transaction's expected data, established by matching the two banks' `tsmt.019` submissions. |
| **Initial baseline submission (`tsmt.019`)** | The message by which a bank submits its view of the expected transaction to the matching engine. |
| **Baseline match report (`tsmt.010`)** | The engine's report on whether the two banks' baseline submissions match. |
| **Data set submission (`tsmt.014`)** | The message carrying actual commercial data (invoice, transport, insurance) for matching against the baseline. |
| **Data set match report (`tsmt.013`)** | The engine's report on whether submitted data matches the baseline. |
| **Matching engine** | The transaction matching application that compares baseline submissions and data sets. |
| **URBPO 750** | The ICC Uniform Rules for Bank Payment Obligations that govern the BPO instrument. |

## Frequently Asked Questions

**Q: What is a Bank Payment Obligation, and how does it differ from a letter of credit?**

A Bank Payment Obligation (BPO) is an irrevocable promise by one bank (the buyer's) to another (the seller's) to pay once agreed trade data matches. It differs from a letter of credit in how the condition is checked: a letter of credit is settled when a bank manually examines paper documents against the credit's terms, whereas a BPO is settled when a matching engine electronically compares submitted data against an agreed baseline. Both give the seller a bank's payment assurance; the BPO replaces document examination with automated data matching.

**Q: What is the baseline, and why does it matter?**

The baseline is the agreed record of what a transaction is expected to contain, established when the buyer's and seller's banks each submit their view with a `tsmt.019` message and the matching engine confirms they match. It matters because it is the reference against which all later data is checked: once the baseline is established, the Bank Payment Obligation exists, and the submitted invoice, transport, and insurance data are matched against the baseline to determine whether payment is due. Without a matched baseline there is no obligation and nothing to match data against.

**Q: How does data set matching drive the payment?**

After the baseline is established, the seller's bank submits the actual commercial data with a `tsmt.014` DataSetSubmission, and the matching engine compares it against the baseline, reporting the result in a `tsmt.013` DataSetMatchReport. If the data matches, the condition of the Bank Payment Obligation is satisfied and payment becomes due, with the parties advancing the transaction's status through `tsmt.025` notifications. If it does not match, mismatch acceptance or rejection messages resolve the difference. The payment is therefore driven by data agreement, not by a human checking documents.

**Q: Why did the BPO and the TSU not succeed?**

Because the market did not adopt them at scale. The Bank Payment Obligation asked banks and corporates to trust electronic data matching in place of the document examination they knew from letters of credit, and to change established processes, but the incentive to switch proved too weak: most trade stayed on letters of credit or open account. SWIFT decommissioned the Trade Services Utility that hosted the matching in 2020. The messages remain a complete model of the mechanism, but the instrument they served did not displace the practices it aimed to modernise.

**Q: Is tsmt still worth studying given its limited adoption?**

Yes, for two reasons. First, it is a precise, self-contained model of how a conditional, data-driven interbank obligation can be expressed: baseline agreement, data matching, status management, and reporting. Those ideas recur wherever automated matching replaces manual checking. Second, its history is a lesson that applies across standards: a clean, well-specified message set is necessary but not sufficient for adoption, which also depends on the market wanting the change. Reading `tsmt` teaches both the mechanism and the economics of why standards do or do not take hold.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 trade services messages](https://www.iso20022.org/trade-services)
- [ICC — Uniform Rules for Bank Payment Obligations (URBPO 750)](https://iccwbo.org/business-solutions/all-rules-guidelines/)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [Claude Code](https://claude.com/product/claude-code)
