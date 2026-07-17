---
layout: post
title: "ISO 20022 for Securities Clearing — The secl Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 swift securities clearing ccp post-trade
description: How ISO 20022 models securities clearing through the secl business area, from trade leg notification and netting to margin, default fund, and buy-in messaging exchanged between a CCP and its clearing members.
image: /assets/article/finance/iso20022-securities-clearing-secl.png
isMath: true
---



ISO 20022 is the financial industry's common language for structured messaging. In the post-trade world it replaces terse, position-based SWIFT MT telexes with rich XML documents that a machine can validate against a published schema. This article looks at one narrow but instructive corner of that standard: the `secl` business area, which models **securities clearing** between a central counterparty (CCP) and its clearing members. The message definitions used throughout are taken directly from the published `secl.*.xsd` schemas (`secl.001` through `secl.010`).

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What ISO 20022 actually is

ISO 20022 is often called "the new SWIFT format", which is a useful shorthand but not quite accurate. The standard is not a single message format. It is a **methodology** for describing financial business processes, a **central repository** of reusable business concepts (the data dictionary), and a set of **physical syntaxes** into which those concepts are serialised. XML is the dominant syntax; ASN.1 and JSON are also defined.

Two properties matter for the rest of this article. First, every message derives from a shared dictionary, so a concept such as "clearing member" or "net position" carries the same meaning and the same structure wherever it appears. Second, every message is backed by an XSD schema, so a receiver can reject a malformed document before any business logic runs.

The legacy SWIFT world uses **MT** (Message Type) messages carried over the FIN network, for example an MT541 to instruct a receive-against-payment settlement or an MT548 to report its status. ISO 20022 messages are called **MX**. They are not a cosmetic re-encoding of MT: they carry more structure, permit longer and more granular identifiers, and separate the business payload from routing metadata.

### The message identifier

Every ISO 20022 message type has an identifier with four dot-separated parts. Taking one of these schemas, `secl.004.001.04`:

```
secl . 004 . 001 . 04
 |      |     |     |
 |      |     |     +--- version           (04 = 4th version)
 |      |     +--------- variant           (001 = base variant)
 |      +--------------- message number     (004 within the business area)
 +---------------------- business area     (secl = securities clearing)
```

The business area prefix is the useful anchor. Securities post-trade processing is split across several areas that hand off to one another:

| Area | Scope |
|------|-------|
| `setr` | Securities trade (order to trade confirmation) |
| `secl` | Securities clearing (CCP to clearing member) |
| `sese` | Securities settlement and reconciliation |
| `semt` | Securities management, statements and reporting |
| `colr` | Collateral management |
| `seev` | Securities events (corporate actions) |
| `reda` | Reference data |

`secl` sits between trading and settlement. It is the vocabulary a CCP uses to tell its members what has been cleared, what they now owe on a net basis, and what they must post to cover risk.

### The Business Application Header

An ISO 20022 message does not travel alone. It is paired with a **Business Application Header** (`head.001.001.xx`) that carries the sender, the receiver, a business message identifier, the message definition identifier, and a creation timestamp. The header is the routing envelope; the `secl` document is the letter inside it. Separating the two means an intermediary can route or archive a message without parsing its business content.

## Where clearing sits in the trade lifecycle

A securities transaction passes through three broad stages:

- **execution**: the trade is agreed on a venue or over the counter;
- **clearing**: obligations are established, novated and netted, and risk is collateralised;
- **settlement**: securities and cash actually change hands at a central securities depository.

Clearing is the risk-management stage in the middle, and it is where a CCP earns its place.

When a CCP clears a trade it performs **novation**: the original bilateral contract between buyer and seller is torn up and replaced by two new contracts, one between the buyer and the CCP and one between the CCP and the seller. From that moment the CCP is the buyer to every seller and the seller to every buyer. Each member faces only the CCP, not a shifting set of anonymous counterparties, so a single default is absorbed by the CCP's risk waterfall rather than propagating across the market.

Novation enables the second core function, **multilateral netting**. Because the CCP is the common counterparty, a member's many trades in the same security across the day collapse into a single net obligation. If a member bought 10,000 and sold 7,000 units of an ISIN, it settles one delivery of 3,000, not seventeen separate legs. Formally, the net quantity for a member $$m$$ in security $$s$$ is

$$
\begin{aligned}
Q_{m,s} = \sum_{i \in \text{buys}} q_i - \sum_{j \in \text{sells}} q_j
\end{aligned}
$$

with an analogous sum producing the net cash amount. Netting is what makes central clearing operationally cheap: it collapses gross settlement traffic, and the `secl` messages are how the CCP communicates the inputs and the results of that calculation.

The diagram below places the `secl` traffic around the CCP, between trade capture upstream and settlement downstream.

![Component view of secl message flows around a central counterparty]({{site.url_complet}}/assets/article/finance/secl-clearing-architecture-concept.png)

## The secl message catalogue

The securities clearing business area defines ten messages. Each root element in the schema resolves to a versioned message type, listed here with the schema file it comes from:

| Identifier | Message | Direction | Purpose |
|------------|---------|-----------|---------|
| `secl.001` | TradeLegNotification | CCP → member | Notify a member of a single cleared and novated trade leg |
| `secl.002` | TradeLegNotificationCancellation | CCP → member | Cancel a previously sent trade leg notification |
| `secl.003` | TradeLegStatement | CCP → member | Periodic statement listing all trade legs |
| `secl.004` | NetPosition | CCP → member | Report net positions per security after netting |
| `secl.005` | MarginReport | CCP → member | Report the margin requirement, as excess or deficit |
| `secl.006` | DefaultFundContributionReport | CCP → member | Report the member's contribution to the default fund |
| `secl.007` | BuyInNotification | CCP → member | Notify that a buy-in has been initiated after a fail |
| `secl.008` | BuyInResponse | member → CCP | Respond to a buy-in notification |
| `secl.009` | BuyInConfirmation | CCP → member | Confirm the outcome of the buy-in |
| `secl.010` | SettlementObligationReport | CCP → member | Report the net obligations to be settled |

Most traffic flows from the CCP to its members: the CCP is the calculating party and the member is informed. Only the buy-in exchange (`secl.007` / `secl.008` / `secl.009`) is a genuine round trip.

### Shared building blocks

The messages reuse the same dictionary components, which is why they feel consistent once you have read one. Inspecting the schemas, the recurring elements include:

- `ClrMmb`: the clearing member, identified by a BIC (`AnyBIC`), a proprietary identifier, or a name and address block.
- `ClrAcct`: the clearing account under which positions are held.
- `RptParams`: report parameters (report identifier, creation date, reporting period, frequency).
- `Pgntn`: pagination, so a long report can be split into numbered pages with a last-page indicator.
- Financial instrument identification, typically an **ISIN**, together with quantities and settlement amounts.

Because these blocks are shared, a system that can parse a `NetPosition` already understands most of a `MarginReport`. This reuse is the practical payoff of the ISO 20022 dictionary approach.

### A concrete shape

The `MarginReport` (`secl.005`) illustrates the style. Below its report parameters and pagination, it carries the clearing member and a margin figure expressed as either an excess amount (`XcssAmt`) or a deficit amount (`DfcitAmt`), qualified by a code or proprietary type. Rendered as illustrative XML, and omitting the outer `Document` and Business Application Header for brevity, a margin call for a shortfall looks like this:

```xml
<MrgnRpt>
  <RptParams>
    <RptId>MGN-20260717-000042</RptId>
    <RptDtAndTm><Dt>2026-07-17</Dt></RptDtAndTm>
  </RptParams>
  <ClrMmb>
    <Id><AnyBIC>ABCDGB2LXXX</AnyBIC></Id>
  </ClrMmb>
  <DfcitAmt Ccy="EUR">1250000.00</DfcitAmt>
</MrgnRpt>
```

The receiving member's system validates this against `secl.005.001.02.xsd`, reads a deficit of €1.25M, and either posts additional collateral or triggers an internal alert. The point is that the meaning is unambiguous and machine-checkable: there is no free-text field to interpret.

## The clearing workflow, message by message

The lifecycle below strings the `secl` messages together in the order a member typically sees them across a clearing day.

![Sequence of secl messages across the clearing lifecycle]({{site.url_complet}}/assets/article/finance/secl-clearing-workflow.png)

**Trade capture and novation.** Matched trades arrive at the CCP from trading venues. The CCP novates each one and issues a **TradeLegNotification** (`secl.001`) per leg, telling the member the trade has been accepted for clearing. If a leg is later withdrawn, a **TradeLegNotificationCancellation** (`secl.002`) reverses the specific notification. Periodically the CCP sends a **TradeLegStatement** (`secl.003`) so the member can reconcile the full set of legs it has been notified of.

**Netting.** At defined cut-offs the CCP nets each member's legs down to one position per security and reports them in a **NetPosition** message (`secl.004`). This is the document that turns a day of gross activity into a short list of net deliverables.

**Risk cover.** Against those positions the CCP calculates initial and variation margin and sends a **MarginReport** (`secl.005`) stating whether the member is in excess or deficit. The member covers any deficit by delivering collateral, a flow that belongs to the `colr` collateral business area rather than `secl`. Separately, the CCP reports the member's mutualised default-fund obligation in a **DefaultFundContributionReport** (`secl.006`). Margin covers a member's own risk; the default fund is the shared, pre-funded layer that absorbs a defaulter's losses once its own margin is exhausted.

**Settlement handover.** Once positions and cover are settled, the CCP issues a **SettlementObligationReport** (`secl.010`) listing the net deliver and receive obligations. These feed the settlement stage, where the member instructs its custodian or the CSD using `sese` messages, and the securities and cash finally move.

**Buy-in.** If a member fails to deliver securities by the settlement date, the CCP can initiate a buy-in: it goes to the market, sources the securities, delivers them to the buyer it had guaranteed through novation, and charges the failing member the cost. This is the one genuinely conversational exchange in `secl`, because it is a process with a decision point and an uncertain outcome rather than a one-way report. It runs across the three buy-in messages:

- **BuyInNotification** (`secl.007`, CCP → member) announces the buy-in against a specific failed delivery. Its schema carries the failing `ClrMmb`, an `OrgnlSttlmOblgtn` reference that pins down exactly which settlement obligation failed, and a buy-in date. In many markets this is sent after a grace period, giving the member a final chance to deliver.
- **BuyInResponse** (`secl.008`, member → CCP) is the member's reply and the only member-to-CCP message in the set. It can quantify the position with `Unit`, `FaceAmt` or `AmtsdVal`, together with `UnitCcy`, `QtdCcy`, `XchgRate` and a `RsltgAmt`, typically to signal a late delivery that cures the fail or to acknowledge the buy-in.
- **BuyInConfirmation** (`secl.009`, CCP → member) reports the outcome once the CCP has executed in the market, carrying the `BuyInDtls` and the `SttlmAmt` the member now owes.

The amount charged back, the buy-in cost $$C_{\text{buyin}}$$, is in essence the market cost of sourcing the securities plus the price difference against the original trade:

$$
\begin{aligned}
C_{\text{buyin}} = Q \cdot (P_{\text{market}} - P_{\text{trade}}) + \text{fees and penalties}
\end{aligned}
$$

where $$Q$$ is the failed quantity, $$P_{\text{market}}$$ the price the CCP paid, and $$P_{\text{trade}}$$ the original agreed price. If the market rose after the trade, the failing seller absorbs the difference, which is precisely the loss the buyer would otherwise have taken. In the EU the [CSDR settlement-discipline regime](https://www.esma.europa.eu/policy-activities/post-trading/settlement) formalised cash penalties for fails and defined a mandatory buy-in framework, whose mandatory application was later suspended in favour of a discretionary one.

## Where the secl schemas come from

The schemas used here were downloaded from the ISO 20022 message definitions catalogue, which offers one ZIP package per business area. Those download files all share the same `archive_business_area_<name>` naming, for example `archive_business_area_securities_clearing`, where "archive" refers to the ZIP package itself and not to the lifecycle status of the messages inside it. The `secl` set is a registered ISO 20022 business area with published Message Definition Reports, not something that was removed from the standard.

It does, however, occupy a narrow slice of the securities post-trade stack, and it overlaps with neighbouring areas in practice. Collateral movement is modelled in `colr`, the actual delivery of securities and cash in `sese`, and position and transaction reporting in `semt`. A given CCP may also expose a proprietary interface alongside, or instead of, the standard `secl` messages. The value of reading `secl` is therefore less about counting production deployments and more about seeing a complete, dictionary-backed model of central clearing expressed in the standard, built from the same components as the areas around it.

## Conclusion

The `secl` business area is a compact, self-contained illustration of how ISO 20022 turns a financial process into structured messages. Ten message types trace the arc of central clearing: novation and trade leg notification, netting into net positions, margin and default-fund cover, the handover to settlement, and the buy-in remedy for a fail. Each is an XML document backed by a schema and assembled from shared dictionary components, so the meaning is explicit and a receiver can validate it mechanically. It is a registered business area of the standard, packaged like every other in a downloadable `archive_business_area_` ZIP, and it remains an accurate map of the vocabulary of securities clearing.

![Mindmap summarising ISO 20022 securities clearing with the secl message set]({{site.url_complet}}/assets/article/finance/iso20022-securities-clearing-secl.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **ISO 20022** | An international standard defining a methodology, a central data dictionary, and physical syntaxes (chiefly XML) for financial messaging. |
| **MX / MT** | MX is an ISO 20022 XML message; MT is a legacy SWIFT FIN message. The post-trade world is migrating from MT to MX. |
| **Business area** | The four-letter prefix of a message identifier grouping related messages, such as `secl` for securities clearing or `sese` for settlement. |
| **secl** | The ISO 20022 business area covering securities clearing between a CCP and its clearing members, comprising messages `secl.001` to `secl.010`. |
| **CCP** | Central counterparty, an entity that interposes itself between buyer and seller through novation, becoming counterparty to both. |
| **Novation** | The replacement of an original bilateral contract with two new contracts facing the CCP, making the CCP counterparty to each side. |
| **Multilateral netting** | Collapsing a member's many trades in one security into a single net obligation, made possible because the CCP is the common counterparty. |
| **Margin** | Collateral a member posts to cover its own potential future exposure, reported by the CCP through the `secl.005` MarginReport. |
| **Default fund** | A mutualised, pre-funded pool that absorbs a defaulting member's losses once its own margin is exhausted, reported through `secl.006`. |
| **Buy-in** | A remedy in which the CCP sources undelivered securities in the market at the failing member's cost, driven by messages `secl.007` to `secl.009`. |

## Frequently Asked Questions

**Q: What does the identifier `secl.004.001.04` mean?**

It is a four-part ISO 20022 message identifier. `secl` is the business area (securities clearing), `004` is the message number within that area (NetPosition), `001` is the variant, and `04` is the version. Reading the identifier alone tells you which family a message belongs to and how mature the definition is, before you open the schema.

**Q: How do MX messages differ from the older SWIFT MT messages?**

MT messages are the legacy FIN-network format: compact, positional, and limited in the length and granularity of their fields. MX messages are ISO 20022 XML documents built from a shared data dictionary and backed by an XSD schema. They carry more structure, allow richer identifiers, separate the business payload from the routing header, and can be validated automatically by a receiver. MX is not merely MT re-encoded in XML; it is a more expressive model.

**Q: Why does novation have to happen before multilateral netting is possible?**

Netting requires a single common counterparty. Novation is precisely what creates that common counterparty: it replaces each bilateral contract with two contracts facing the CCP, so the CCP becomes buyer to every seller and seller to every buyer. Only once every one of a member's trades faces the same entity can they be summed into one net position per security. Without novation, a member's obligations would still point at many different counterparties and could not be collapsed.

**Q: Which functions of clearing are handled outside the secl area, and why?**

Two important flows sit outside `secl`. Posting collateral to cover a margin deficit belongs to the collateral management area (`colr`), and the actual movement of securities and cash belongs to the settlement area (`sese`). This is deliberate: ISO 20022 assigns each business process to the area that owns it, so `secl` reports what is owed and required (net positions, margin, default fund, settlement obligations) while the delivery of collateral and the final settlement are modelled where those processes properly live. The `secl.010` SettlementObligationReport is the explicit handover point between clearing and settlement.

**Q: The buy-in exchange uses three messages while most secl flows use one. Why?**

Most `secl` messages are one-way reports: the CCP calculates something (a net position, a margin figure, a default-fund contribution) and informs the member, so a single message suffices. A buy-in is a negotiation triggered by a settlement failure. The CCP must announce it (`secl.007`), the member must be able to respond, for example by supplying late-delivery information or accepting the action (`secl.008`), and the CCP must report the actual outcome once it has sourced the securities in the market (`secl.009`). Because the process has genuine back-and-forth with an uncertain result, it needs a request, a response, and a confirmation rather than a single notification.

**Q: The download folder is called `archive_business_area_securities_clearing`. Does that mean the secl messages are retired?**

No. Every business area on the ISO 20022 message definitions catalogue is offered as a ZIP whose name begins with `archive_business_area_`, so the word describes the download package, not the status of the messages. The `secl` set is a registered business area with published Message Definition Reports. It does sit in a narrow part of the securities post-trade stack and overlaps with `colr`, `sese` and `semt`, and CCPs sometimes use proprietary interfaces as well, but that is a matter of scope and adoption, not of the messages being withdrawn from the standard.

## References

- [ISO 20022 official site and message catalogue](https://www.iso20022.org/)
- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 securities messages overview](https://www.iso20022.org/securities)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [ESMA — CSDR settlement discipline and buy-in regime](https://www.esma.europa.eu/policy-activities/post-trading/settlement)
- [Claude Code](https://claude.com/product/claude-code)
