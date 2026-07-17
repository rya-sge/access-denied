---
layout: post
title: "ISO 20022 for Regulatory Reporting — The auth Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 regulatory mifir emir sftr auth reporting
description: A guided tour of ISO 20022's auth (authorities) business area, the regulatory-reporting messages that carry MiFIR, EMIR, SFTR, money-market, CCP, and settlement-fails data from firms and infrastructures to their competent authorities.
image: /assets/article/finance/iso20022-authorities-auth.png
isMath: false
---



Financial regulation runs on data. After the 2008 crisis, authorities demanded that firms report their transactions, positions, and exposures in detail, and those reports had to be structured, comparable, and machine-processable. ISO 20022 is where much of that reporting now lives, in the `auth` business area: **authorities**. It is one of the largest areas in the standard, ninety messages, because it serves many regimes at once, from MiFIR transaction reporting to EMIR derivatives, SFTR securities financing, money-market statistics, CCP supervision, and settlement-fails reporting. This article organises that breadth by regime and shows the reporting patterns they share.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What auth is for

Where most ISO 20022 areas carry business between commercial parties, `auth` carries data from those parties to their **regulators**. The reporting entities are investment firms, trading venues, trade repositories, central counterparties (CCPs), and central securities depositories (CSDs); the recipients are national competent authorities (NCAs), the European Securities and Markets Authority (ESMA), and central banks. The area exists because each major post-crisis regulation created a reporting obligation, and a common message standard lets those obligations be met, validated, and reconciled consistently.

![Who reports to whom under the auth area]({{site.url_complet}}/assets/article/finance/auth-reporting-topology-concept.png)

The clearest way to navigate ninety messages is by the regime each serves.

| Regime | Representative messages | What it reports |
|--------|------------------------|-----------------|
| Money market statistics (MMSR) | `auth.012` to `auth.015` | Daily money-market activity to the central bank |
| MiFIR / MiFID II | `auth.016`, `auth.017`, `auth.032`, `auth.040`, `auth.113` | Transactions, reference data, transparency, market data |
| EMIR (derivatives) | `auth.030`, `auth.090`, `auth.091`, `auth.108` | Derivatives trades, positions, reconciliation, margin |
| SFTR (securities financing) | `auth.052`, `auth.070`, `auth.071`, `auth.079` | Repo and lending transactions, collateral, reuse |
| CCP supervision | `auth.054` to `auth.069`, `auth.112` | CCP membership, stress tests, collateral, positions |
| CSDR settlement discipline | `auth.072`, `auth.100`, `auth.101` | Settlement internaliser and fails reporting |
| Currency control | `auth.018` to `auth.027` | Contract registration and currency-control filings |
| Cross-cutting | `auth.001` to `auth.003`, `auth.034`, `auth.077` | Information requests, tax, benchmark reporting |

## The major regimes

**MiFIR and MiFID II** account for the largest cluster. The `auth.016` **FinancialInstrumentReportingTransactionReport** is the RTS 22 transaction report, in which an investment firm reports each executed transaction to its NCA with the instrument, quantities, prices, parties, and decision-makers. Around it sit reference-data reports (`auth.017` and its delta and index variants), pre- and post-trade transparency reports for equity and non-equity instruments (`auth.032`, `auth.033`), trading-activity and volume-cap reports (`auth.040`, `auth.041`, `auth.035`), and the market-data and order-book reports (`auth.113`, `auth.122` to `auth.124`) that venues must keep and provide.

**EMIR** covers derivatives. Firms report their derivatives trades to a trade repository, and the repository and authorities exchange the `auth.030` **DerivativesTradeReport**, position-set reports (`auth.090`), reconciliation and rejection statistics (`auth.091`, `auth.092`), and margin and state reports (`auth.108`, `auth.107`). **SFTR** does the equivalent for securities financing: the `auth.052` **SecuritiesFinancingReportingTransactionReport** covers repo, buy-sell-backs, and securities lending, with companion messages for margin data (`auth.070`), reused collateral (`auth.071`), pairing and reconciliation (`auth.078`, `auth.080`), and transaction state (`auth.079`).

**CCP supervision** is a regime of its own: a run of reports (`auth.054` to `auth.069`) in which a central counterparty discloses its clearing members, their requirements and obligations, its stress-testing and back-testing definitions and results, its collateral, investments, cash flows, and available financial resources. These implement the supervisory and public-disclosure expectations placed on CCPs.

**Money-market statistics (MMSR)** feed the central bank: daily reports of secured (`auth.012`) and unsecured (`auth.013`) money-market borrowing and lending, foreign-exchange swaps (`auth.014`), and overnight index swaps (`auth.015`), from which reference rates are in part derived. **CSDR settlement discipline** adds the settlement-internaliser report (`auth.072`) and the monthly and annual settlement-fails reports (`auth.100`, `auth.101`).

## The reporting patterns

Across these regimes, `auth` messages share a few shapes.

![Regulatory reporting and an authority information request]({{site.url_complet}}/assets/article/finance/auth-report-status-workflow.png)

The common pattern is **report then status advice**. A reporting entity submits a report, such as an `auth.016` transaction report, an `auth.030` derivatives report, or an `auth.052` financing report, and the receiver answers with a status advice indicating acceptance or rejection, for example the `auth.031` reporting status advice. For the trade-repository regimes, a further **reconciliation** step compares the two sides of a reported trade, surfaced through messages such as the EMIR reconciliation statistics (`auth.091`) or the SFTR reconciliation status advice (`auth.080`).

A second, distinct pattern is the **information request**, where the authority is the initiator. In `auth.001` **InformationRequestOpening** an authority asks a party to provide information, the party answers with `auth.002` **InformationRequestResponse**, and the request's progress is tracked with `auth.003` **StatusChangeNotification**. This is the investigative counterpart to the routine, entity-initiated reports, letting an authority pull specific information rather than only receive scheduled filings.

## Conclusion

The `auth` business area is ISO 20022's home for regulatory reporting. Its ninety messages are best read not as one set but as many regimes sharing a standard: MiFIR transaction, reference, transparency, and market-data reporting; EMIR derivatives and SFTR securities-financing reporting to trade repositories; the daily money-market statistics that feed reference rates; the supervisory reports a CCP must publish; and the settlement-fails reporting of CSDR. Two patterns recur across them: a report answered by a status advice, sometimes followed by reconciliation, and an authority-initiated information request. As the regulatory-facing area of the standard, `auth` is where the post-crisis demand for data meets a common, validated format.

![Mindmap summarising the ISO 20022 auth authorities area]({{site.url_complet}}/assets/article/finance/iso20022-authorities-auth.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **auth** | The ISO 20022 authorities business area: regulatory-reporting messages from firms and infrastructures to their supervisors, across ninety messages. |
| **MiFIR / MiFID II** | The EU regime for markets in financial instruments, whose transaction, reference-data, transparency, and market-data reports are carried by `auth`. |
| **Transaction report (`auth.016`)** | The MiFIR report of each executed transaction, with instrument, quantities, prices, parties, and decision-makers. |
| **EMIR** | The EU regime for derivatives, under which trades are reported to a trade repository via `auth.030` and related messages. |
| **SFTR** | The EU securities-financing transactions regime, whose repo and lending reports are carried by `auth.052` and companions. |
| **MMSR** | Money-market statistical reporting to the central bank, covering secured, unsecured, FX-swap, and OIS activity (`auth.012` to `auth.015`). |
| **CCP supervisory reports** | The reports (`auth.054` to `auth.069`) through which a central counterparty discloses membership, stress tests, collateral, and resources. |
| **Settlement fails report** | The CSDR reports (`auth.100`, `auth.101`) of transactions that failed to settle, alongside the internaliser report (`auth.072`). |
| **Status advice** | The response confirming a report was accepted or rejected, such as the `auth.031` reporting status advice. |
| **Information request (`auth.001`)** | An authority-initiated request for information, answered by `auth.002` and tracked by `auth.003`. |

## Frequently Asked Questions

**Q: Why is the auth area so large compared with other business areas?**

Because it serves many separate regulatory regimes rather than one business process. Each major post-crisis regulation, MiFIR, EMIR, SFTR, the money-market statistics framework, CCP supervision, and CSDR settlement discipline, created its own detailed reporting obligation with its own data content. Rather than invent a new standard for each, ISO 20022 put them all in the `auth` area, so ninety messages cover what are really a dozen different reporting frameworks. The right way to read it is regime by regime, not as a single coherent set.

**Q: What does a MiFIR transaction report contain, and who sends it?**

The `auth.016` transaction report is sent by an investment firm to its national competent authority for each executed transaction covered by MiFIR. It carries the financial instrument, the quantities and prices, the buyer and seller, the decision-makers on each side, the venue, and various flags required by the regulation. Its purpose is to let the authority monitor for market abuse and reconstruct market activity. It is one of the highest-volume regulatory reports, which is why it anchors the MiFIR cluster of the `auth` area.

**Q: What is the difference between the report-and-status-advice pattern and the information-request pattern?**

They differ in who initiates. In the report-and-status-advice pattern, the reporting entity takes the initiative: it submits a report, such as an `auth.016`, `auth.030`, or `auth.052`, and the receiver answers with a status advice accepting or rejecting it, sometimes followed by reconciliation. In the information-request pattern, the authority takes the initiative: an `auth.001` InformationRequestOpening asks a party for specific information, answered by `auth.002` and tracked by `auth.003`. The first is routine, scheduled reporting; the second is an authority pulling information on demand, often for investigation.

**Q: How do EMIR and SFTR reporting differ within auth?**

They report different instruments to trade repositories but follow parallel shapes. EMIR covers derivatives: the `auth.030` DerivativesTradeReport and its position, reconciliation, and margin companions. SFTR covers securities financing transactions, repos, buy-sell-backs, and securities lending: the `auth.052` transaction report with margin (`auth.070`), reused-collateral (`auth.071`), pairing (`auth.078`), and state (`auth.079`) companions. Both regimes report trades to a repository, both include reconciliation between the two sides of a trade, and both use the report-then-status-advice pattern, but the instruments and the specific data content differ.

**Q: Which auth messages are aimed at central counterparties, and what do they cover?**

The block from `auth.054` to `auth.069`, plus the interoperability report (`auth.112`), is CCP-specific. Through them a central counterparty discloses its clearing members and their requirements and obligations, its portfolio and liquidity stress-testing definitions and results, its back-testing, its collateral and investments, its daily cash flows, its income and capital adequacy, and its available financial resources. These implement the supervisory and public quantitative disclosure expectations placed on CCPs, so that authorities and the market can judge a clearing house's resilience.

**Q: How does the auth area relate to the business areas that generate the reported activity?**

`auth` reports on activity that other areas create. A securities-financing transaction settled through `sese` and a derivatives trade cleared through a CCP become, respectively, an SFTR report (`auth.052`) and an EMIR report (`auth.030`). A settlement fail handled in `sese` and penalised in `semt` is aggregated into the CSDR fails reports (`auth.100`, `auth.101`). In other words, the other areas run the business, and `auth` is where a regulated view of that business is filed with the authorities.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ESMA — MiFIR, EMIR and SFTR reporting](https://www.esma.europa.eu/)
- [ECB — Money Market Statistical Reporting (MMSR)](https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/money_market/html/index.en.html)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [Claude Code](https://claude.com/product/claude-code)
