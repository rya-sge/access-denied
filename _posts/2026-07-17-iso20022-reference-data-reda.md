---
layout: post
title: "ISO 20022 for Reference Data — The reda Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 reference-data reda securities ssi calendar
description: A tour of ISO 20022's reda (reference data) business area, the messages that create, maintain, query, and report the static data behind transactions, from securities, parties, and accounts to standing settlement instructions, calendars, and prices.
image: /assets/article/finance/iso20022-reference-data-reda.png
isMath: false
---



Every transaction relies on data that does not change with the transaction: what a security is, who a party is, which account it settles to, where to send the cash. This is **reference data**, the static backdrop against which the moving parts operate, and ISO 20022 gives it a business area, `reda`. It is a large and varied area, sixty-three messages, because reference data covers many domains. This article organises them into families, describes the create-maintain-query-report pattern they share, and shows why getting reference data right underpins everything else.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What reda is for

`reda` carries the **static data** that transactions depend on. A settlement instruction names a security, an account, and a set of parties; a payment names a creditor and where to route it. None of that information is created by the transaction; it is looked up. Reference data is the authoritative record of those entities, and `reda` is how it is created, changed, queried, and distributed between the parties that maintain it and the parties that consume it.

![Reference data distribution and the CRUD pattern]({{site.url_complet}}/assets/article/finance/reda-golden-source-concept.png)

The value of a standard here is a single source of truth. When many participants must agree on what an instrument is or where a counterparty settles, a shared, structured record prevents the mismatches that cause failed transactions.

## The families of reda

The sixty-three messages group by the kind of reference data they manage.

| Family | Representative messages | What it covers |
|--------|------------------------|----------------|
| Prices | `reda.001`, `reda.004` | Security and fund prices |
| Securities | `reda.006`, `reda.007`, `reda.012` | Instrument reference data |
| Parties | `reda.014`, `reda.017`, `reda.022` | Party (entity) reference data |
| Securities accounts | `reda.018`, `reda.021`, `reda.023` | Account reference data |
| Collateral and eligibility | `reda.024`, `reda.025`, `reda.027` | Collateral values and eligibility |
| Links | `reda.045`, `reda.049` | CSD and account links |
| Standing settlement instructions | `reda.056` to `reda.059` | Where a party settles |
| Netting and calendars | `reda.060`, `reda.064` | Cut-offs and business calendars |
| Request to pay enrolment | `reda.066` to `reda.073` | Creditor enrolment and debtor activation |

The **securities**, **party**, and **securities account** families form the core, and are the static-data backbone of a settlement system such as a central securities depository. The **collateral and eligibility**, **links**, and **standing settlement instruction** families support settlement and collateral operations. The remaining families, prices, calendars, netting cut-offs, and request-to-pay enrolment, cover more specific reference needs.

## The create-maintain-query-report pattern

Most `reda` families follow the same lifecycle for a piece of reference data, built from a small set of verbs.

![Maintaining a security's reference data]({{site.url_complet}}/assets/article/finance/reda-security-lifecycle-workflow.png)

Taking securities as the example: a maintainer creates the instrument with a `reda.006` **SecurityCreationRequest** and receives a `reda.008` **SecurityCreationStatusAdvice**; consumers are told of the change through a `reda.009` **SecurityActivityAdvice**; a consumer that needs the current record sends a `reda.010` **SecurityQuery** and receives a `reda.012` **SecurityReport**; and later changes are made with a `reda.007` **SecurityMaintenanceRequest** and a `reda.029` status advice, or removed with a `reda.013` deletion request. The party and account families mirror this shape with their own create, modify, delete, query, report, and activity messages, and both add **audit-trail** queries and reports (`reda.033`, `reda.036`, `reda.042`) so a full history of changes can be retrieved. This uniform create-maintain-query-report pattern is what makes a large area navigable: learn it once and it applies across the domains.

## Two notable families

Two families are worth singling out because they reach beyond the securities world.

**Standing settlement instructions.** A standing settlement instruction (SSI) records, in advance, where a party wants a given kind of transaction settled: the accounts and agents for its cash and securities. The `reda.056` **StandingSettlementInstruction**, with its deletion, cancellation, and status-advice companions, is how SSIs are published and maintained, so that a counterparty always knows where to deliver without asking each time.

**Request to pay enrolment.** The `reda.066` to `reda.073` messages support request-to-pay schemes, in which a payee asks a payer to authorise a payment. They handle the reference-data setup of that service: enrolling a creditor (`reda.066`) and activating a debtor (`reda.070`), with amendment, cancellation, and status messages. It is an example of reference data underpinning a payment service rather than a securities one.

## Conclusion

The `reda` business area manages the static data that transactions rely on. Its sixty-three messages cover securities, parties, and accounts at the core, extended by collateral eligibility, CSD and account links, standing settlement instructions, prices, calendars, netting cut-offs, and request-to-pay enrolment. Most follow one create-maintain-query-report pattern, with activity advices and audit trails, so a single lifecycle applies across many domains. Because it is the source of truth the moving parts look up, `reda` is quietly foundational: a settlement instruction, a collateral movement, or a payment is only as correct as the reference data behind it. Read next to the settlement and collateral areas that consume it, `reda` is where the standard keeps its facts.

![Mindmap summarising the ISO 20022 reda reference data area]({{site.url_complet}}/assets/article/finance/iso20022-reference-data-reda.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **reda** | The ISO 20022 reference data business area, managing the static data behind transactions across sixty-three messages. |
| **Reference data** | The static, authoritative data that transactions look up rather than create, such as instruments, parties, and accounts. |
| **Security reference data** | The instrument data (identifiers, terms) created and maintained through `reda.006`, `reda.007`, and reported by `reda.012`. |
| **Party reference data** | The entity data for counterparties and institutions, managed through the `reda.014` family. |
| **Securities account reference data** | The account data managed through the `reda.018` family. |
| **Standing settlement instruction (SSI)** | A pre-recorded instruction (`reda.056`) stating where a party settles a given kind of transaction. |
| **Create-maintain-query-report** | The common lifecycle pattern: create a record, maintain it, query the current state, and report it, with activity advices and audit trails. |
| **Audit trail** | The retrievable history of changes to a reference-data record, via queries and reports such as `reda.033` and `reda.042`. |
| **Calendar** | The business-calendar reference data managed by `reda.064` and `reda.065`. |
| **Request to pay enrolment** | The reference-data setup of a request-to-pay service, enrolling creditors and activating debtors through `reda.066` to `reda.073`. |

## Frequently Asked Questions

**Q: What is reference data, and why does it need its own area?**

Reference data is the static, authoritative information that transactions rely on but do not create: what a security is, who a counterparty is, which account it uses, where its cash and securities settle. A transaction looks this up rather than carrying it fresh each time. It needs its own area because keeping that data correct and shared is a distinct job from processing transactions, and because many participants must agree on the same facts. `reda` provides the messages to create, maintain, query, and distribute reference data so that everyone works from the same record.

**Q: What is the create-maintain-query-report pattern?**

It is the common lifecycle most `reda` families follow for a piece of reference data. A maintainer creates the record (for a security, `reda.006`) and gets a status advice; consumers are notified through an activity advice; a consumer queries the current state (`reda.010`) and receives a report (`reda.012`); and later the record is maintained (`reda.007`) or deleted (`reda.013`). The party and account families repeat this shape with their own messages. Because the pattern is uniform, understanding it once lets you navigate the whole area rather than learning each family from scratch.

**Q: What is a standing settlement instruction, and why publish it as reference data?**

A standing settlement instruction (SSI) records in advance where a party wants a given kind of transaction settled: the cash and securities accounts and agents to use. Publishing it as reference data, through `reda.056` and its companions, means a counterparty can look up where to deliver without asking each time a trade is done. This avoids errors and delays: instead of exchanging settlement details per transaction, parties rely on a maintained, authoritative SSI record. It is a good example of reference data preventing the mismatches that cause settlement fails.

**Q: Why do the party and account families include audit-trail messages?**

Because changes to reference data have consequences, and who changed what, and when, must be reconstructable. The audit-trail queries and reports (such as `reda.033` for securities and `reda.042` for parties) let a participant retrieve the full history of changes to a record. This matters for control and for investigating problems: if a settlement failed because an account detail was wrong, the audit trail shows when and how that detail changed. Reference data is authoritative, so its history has to be auditable.

**Q: Why does a reference-data area include request-to-pay enrolment?**

Because a request-to-pay service, in which a payee asks a payer to approve a payment, needs its participants and their preferences set up in advance, and that setup is reference data. The `reda.066` to `reda.073` messages enrol a creditor and activate a debtor, with amendment, cancellation, and status messages. It sits in `reda` because it is about establishing the static enrolment behind the service rather than processing individual payment requests. It shows that reference data underpins payment services as much as securities ones.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 reference data messages](https://www.iso20022.org/securities)
- [ECB — TARGET2-Securities (T2S) reference data](https://www.ecb.europa.eu/paym/target/t2s/html/index.en.html)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [Claude Code](https://claude.com/product/claude-code)
