---
layout: post
title: "ISO 20022 — A Map of the Financial Messaging Standard"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 messaging payments securities cards standards
description: An overview of ISO 20022 as a whole, tying together its methodology, message identifier, and Business Application Header with a map of its business areas across payments, securities, cards, trade finance, FX, regulatory, and reference data.
image: /assets/article/finance/iso20022-standard-overview.png
isMath: false
---



ISO 20022 is the common language of modern financial messaging. It reaches from the payment that settles a wire to the vote cast at a shareholder meeting, from the card tapped at a shop to the report a bank files with its regulator. This article is the map that ties the pieces together. It explains what the standard is, how a message is identified and wrapped, and how its business areas divide the financial world, linking to a companion article on each area covered in this series.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What ISO 20022 is

ISO 20022 is often called a message format, but it is more than that. It is three things at once.

![The structure of ISO 20022]({{site.url_complet}}/assets/article/finance/iso20022-three-pillars-concept.png)

- A **methodology**: a defined way of modelling a financial business process and deriving messages from that model.
- A **central dictionary**: a repository of reusable business concepts, so that "clearing member", "settlement amount", or "creditor agent" mean the same thing and share the same structure wherever they appear.
- A set of **physical syntaxes**: the serialisations a message can take, chiefly XML, with JSON and ASN.1 also defined.

The payoff of this design is consistency. Because every message is assembled from the same dictionary and validated against a published XSD schema, a concept carries one meaning across areas, and a receiver can reject a malformed document before any business logic runs. The older SWIFT MT messages, by contrast, were defined format by format; ISO 20022 messages (called **MX**) share a common model.

## The message identifier

Every message type has a four-part identifier. Taking `pacs.008.001.10`:

```
pacs . 008 . 001 . 10
 |      |     |     |
 |      |     |     +--- version
 |      |     +--------- variant
 |      +--------------- message number within the area
 +---------------------- business area
```

The business-area prefix is the key to navigation: `pacs` for interbank payments, `sese` for securities settlement, `camt` for cash management, and so on. Learn the prefixes and the catalogue organises itself.

## The Business Application Header

A business message rarely travels alone. It is wrapped in a **Business Application Header** (`head.001`), a separate document that carries the routing and control information: who is sending it, to whom, which message definition it is, when it was created, and a signature proving it is authentic. Keeping routing out of the payload lets an intermediary route or log a message without parsing its content, and gives every message a uniform, signable envelope. The header is described in its own companion article, [the Business Application Header]({{site.url_complet}}/2026/07/17/iso20022-business-application-header-head/).

## The map of business areas

The standard divides the financial world into business areas. The ones covered in this series group into six domains.

### Payments

| Area | Prefix | Companion article |
|------|--------|-------------------|
| Payments clearing and settlement | `pacs` | [The pacs message set]({{site.url_complet}}/2026/07/17/iso20022-payments-clearing-settlement-pacs/) |
| Cash management | `camt` | [The camt message set]({{site.url_complet}}/2026/07/17/iso20022-cash-management-camt/) |

`pacs` is the interbank engine that moves money between banks and the centre of the MT-to-MX migration; `camt` is the reporting, exception, and account-administration layer around it.

### Securities

| Area | Prefix | Companion article |
|------|--------|-------------------|
| Securities clearing | `secl` | [The secl message set]({{site.url_complet}}/2026/07/17/iso20022-securities-clearing-secl/) |
| Securities settlement | `sese` | [The sese message set]({{site.url_complet}}/2026/07/17/iso20022-securities-settlement-sese/) |
| Securities management | `semt` | [The semt message set]({{site.url_complet}}/2026/07/17/iso20022-securities-management-semt/) |
| Securities events | `seev` | [The seev message set]({{site.url_complet}}/2026/07/17/iso20022-securities-events-seev/) |
| Collateral management | `colr` | [The colr message set]({{site.url_complet}}/2026/07/17/iso20022-collateral-management-colr/) |

These trace a security through its post-trade life: cleared by a CCP (`secl`), covered by collateral (`colr`), settled at a depository (`sese`), reported to the owner (`semt`), and subject to corporate actions and votes (`seev`).

### Trade finance and foreign exchange

| Area | Prefix | Companion article |
|------|--------|-------------------|
| Foreign exchange trade | `fxtr` | [The fxtr message set]({{site.url_complet}}/2026/07/17/iso20022-fx-trade-fxtr/) |
| Trade services | `tsrv` | [The tsrv message set]({{site.url_complet}}/2026/07/17/iso20022-trade-services-tsrv/) |
| Trade services initiation | `tsin` | [The tsin message set]({{site.url_complet}}/2026/07/17/iso20022-trade-services-initiation-tsin/) |
| Trade services management | `tsmt` | [The tsmt message set]({{site.url_complet}}/2026/07/17/iso20022-trade-services-management-tsmt/) |

`fxtr` confirms and matches FX trades; `tsrv` carries bank guarantees; `tsin` is the corporate-to-bank front end of supply chain finance; and `tsmt` modelled the Bank Payment Obligation.

### Cards

| Area | Prefix | Companion article |
|------|--------|-------------------|
| ATM card transactions | `catp` | [The catp message set]({{site.url_complet}}/2026/07/17/iso20022-atm-card-transactions-catp/) |
| Acceptor to acquirer | `caaa` | [The caaa message set]({{site.url_complet}}/2026/07/17/iso20022-acceptor-to-acquirer-caaa/) |
| Acquirer to issuer | `cain` | [The cain message set]({{site.url_complet}}/2026/07/17/iso20022-acquirer-issuer-card-cain/) |
| Sale to POI | `casp` | [The casp message set]({{site.url_complet}}/2026/07/17/iso20022-sale-to-poi-casp/) |
| Network management | `canm` | [The canm message set]({{site.url_complet}}/2026/07/17/iso20022-network-management-canm/) |
| ATM management | `caam` | [The caam message set]({{site.url_complet}}/2026/07/17/iso20022-atm-management-caam/) |
| Terminal management | `catm` | [The catm message set]({{site.url_complet}}/2026/07/17/iso20022-terminal-management-catm/) |
| Fraud reporting | `cafr` | [The cafr message set]({{site.url_complet}}/2026/07/17/iso20022-fraud-reporting-cafr/) |
| Fee collection | `cafc` | [The cafc message set]({{site.url_complet}}/2026/07/17/iso20022-fee-collection-cafc/) |
| Settlement reporting | `casr` | [The casr message set]({{site.url_complet}}/2026/07/17/iso20022-settlement-reporting-casr/) |

The card family is the largest group. The transaction areas (`catp`, `caaa`, `cain`) carry payments at ATMs, merchant terminals, and between acquirer and issuer; `casp` drives the terminal from the till; the management areas (`canm`, `caam`, `catm`) keep the devices signed on, keyed, and configured; and `cafr`, `cafc`, and `casr` handle fraud, fees, and settlement reporting. All share a protected, authenticated message envelope, because card traffic carries PINs and card data across untrusted networks.

### Regulatory and reference data

| Area | Prefix | Companion article |
|------|--------|-------------------|
| Authorities | `auth` | [The auth message set]({{site.url_complet}}/2026/07/17/iso20022-authorities-auth/) |
| Reference data | `reda` | [The reda message set]({{site.url_complet}}/2026/07/17/iso20022-reference-data-reda/) |

`auth` carries regulatory reporting to authorities across many regimes (MiFIR, EMIR, SFTR, and more); `reda` manages the static data (securities, parties, accounts, standing settlement instructions) that all the other areas look up.

## Patterns that recur across the standard

Reading the areas together, a handful of design patterns appear again and again. Recognising them makes any new area faster to learn.

- **Request and response.** The simplest and most common shape: one message asks, one answers. It runs through card transactions, queries, and confirmations everywhere.
- **Initiation, advice, and notification.** When a message travels a chain of parties, each link gets a message suited to its role, as in the trade-services and corporate-action flows.
- **Get and return.** The query convention for market-infrastructure objects, where a Get is answered by a matching Return, seen across `camt` and `reda`.
- **Create, maintain, query, report.** The reference-data lifecycle for a record, uniform across the `reda` securities, party, and account families.
- **Authorise then confirm.** The two-phase pattern separating an authorisation from the physical outcome, essential where value moves, as in card withdrawals and settlement.
- **The protected card envelope.** Across the card areas, a shared header with encrypted sensitive data and a message authentication code, because the traffic assumes a hostile network.

## The migration from MT to MX

The reason ISO 20022 matters now, and not just as a design, is the industry-wide move to it. Correspondent banking, through the CBPR+ guidelines, and domestic real-time gross settlement systems such as the Eurosystem's T2, the UK's CHAPS, and the US Fedwire, are replacing their SWIFT MT traffic with ISO 20022 MX. The flagship of that migration is `pacs`, and the reporting messages of `camt` are the modern successors to the MT statements banks have long sent. Beyond payments, the securities and cards worlds have their own long-running adoption stories. The common thread is richer, structured, validated data in place of terse, fixed-format legacy messages.

## Conclusion

ISO 20022 is a single standard with many faces. A shared methodology, dictionary, and syntax produce messages that are consistent across a financial world divided into business areas: payments in `pacs` and `camt`; the securities post-trade chain in `secl`, `colr`, `sese`, `semt`, and `seev`; trade finance and FX in `fxtr`, `tsrv`, `tsin`, and `tsmt`; the broad card family from ATMs to terminals to fraud reporting; and the regulatory and reference-data areas that report on and underpin the rest. A four-part identifier names each message and a Business Application Header routes it. The companion articles linked above go into each area in depth; this map is where they connect.

![Mindmap of the ISO 20022 standard and its business areas]({{site.url_complet}}/assets/article/finance/iso20022-standard-overview.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **ISO 20022** | The international standard for financial messaging, comprising a methodology, a central dictionary, and physical syntaxes. |
| **MX / MT** | MX is an ISO 20022 message; MT is a legacy SWIFT FIN message. The industry is migrating from MT to MX. |
| **Business area** | The four-letter prefix grouping related messages, such as `pacs` for payments or `sese` for securities settlement. |
| **Message identifier** | The four-part name of a message type (area.number.variant.version), such as `pacs.008.001.10`. |
| **Central dictionary** | The repository of reusable business concepts from which every message is assembled. |
| **Business Application Header** | The `head.001` envelope carrying a message's routing, control, and signature data, separate from the payload. |
| **Request and response** | The most common message pattern, one message asking and one answering. |
| **Authorise then confirm** | The two-phase pattern separating an authorisation from the physical outcome, used where value moves. |
| **CBPR+** | The cross-border payments and reporting market-practice guidelines for correspondent-banking use of ISO 20022. |
| **Protected card envelope** | The shared card-family message structure with encrypted sensitive data and a message authentication code. |

## Frequently Asked Questions

**Q: Is ISO 20022 just a new message format?**

No. It is a methodology for modelling financial processes, a central dictionary of reusable business concepts, and a set of physical syntaxes (chiefly XML) into which messages are serialised. The format you see, an XML document, is only the last of the three. The deeper value is that every message is built from the same dictionary and validated against a published schema, so concepts mean the same thing across areas and messages can be checked automatically. Calling it a format captures the surface but misses the model underneath.

**Q: How do I find the right message for a task?**

Start from the business-area prefix. The four-letter prefix of a message identifier tells you the domain: `pacs` for interbank payments, `camt` for cash reporting, `sese` for securities settlement, `seev` for corporate actions, `colr` for collateral, `auth` for regulatory reporting, and so on. Once you know the area, the message number identifies the specific function within it. Learning the prefixes is the fastest way to navigate a catalogue of thousands of messages, because they partition the whole standard by purpose.

**Q: What does the Business Application Header add to a message?**

Routing, control, and integrity, kept separate from the business content. The header names the sender and receiver, identifies exactly which message definition the payload is, timestamps and can prioritise the message, links it to related exchanges, and carries a signature that proves it is authentic. Because this sits outside the payload, an intermediary can route or log a message without parsing its content, and the same envelope works for every message type. In most market infrastructures the header is a required part of every exchange.

**Q: Why does the card family look so different from the payments and securities areas?**

Because it is a real-time device protocol carrying sensitive data across untrusted networks. Card messages run between terminals, acquirers, and issuers, and they carry PINs and card numbers, so the card family wraps its content in a shared header with encrypted sensitive fields and a message authentication code. The payments and securities areas, exchanged between institutions over trusted infrastructures, do not need that per-message envelope in the same way and instead rely on the Business Application Header. The difference reflects the different threat models the two kinds of traffic face.

**Q: How do the business areas connect into end-to-end processes?**

They hand off to one another. A payment is initiated in `pain`, cleared and settled between banks in `pacs`, and reported to customers in `camt`. A securities trade is cleared by a CCP in `secl`, covered by collateral in `colr`, settled at a depository in `sese`, reported to the owner in `semt`, and reported to regulators in `auth`, while corporate actions on the holding flow through `seev`. No single area does everything; each owns one stage, and the standard's shared dictionary is what lets them pass a consistent picture of the same transaction between them.

**Q: Why is the migration from MT to MX significant?**

Because it changes the data that the world's payments run on. The SWIFT MT messages that have carried interbank payments for decades use terse, fixed-format fields; ISO 20022 MX messages carry richer, structured, validated data. Correspondent banking (through CBPR+) and major real-time gross settlement systems are replacing MT with MX, chiefly in the `pacs` and `camt` areas. The gain is automation and clarity: structured remittance information, longer identifiers, and clearer party data that let systems reconcile and process payments without human interpretation. The migration is the reason ISO 20022 is a present concern and not just a design.

## References

- [ISO 20022 official site](https://www.iso20022.org/)
- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [SWIFT — ISO 20022 programme and MT to MX migration](https://www.swift.com/standards/iso-20022/iso-20022-programme)
- [ECB — TARGET Services (T2) and ISO 20022](https://www.ecb.europa.eu/paym/target/consolidation/html/index.en.html)
- [Claude Code](https://claude.com/product/claude-code)
