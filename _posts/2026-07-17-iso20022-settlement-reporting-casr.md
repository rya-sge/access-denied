---
layout: post
title: "ISO 20022 for Card Settlement Reporting — The casr Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 cards casr settlement reporting
description: How ISO 20022 models card settlement reporting through the casr business area, a two-message request-and-response pair that reports settlement positions and totals between card parties on the same protected envelope as the transaction messages.
image: /assets/article/finance/iso20022-settlement-reporting-casr.png
isMath: false
---



Once card transactions have been authorised and cleared, the money owed between the parties has to be tallied and reported: how much an acquirer is due, how much an issuer owes, what the net position is. That tallying is settlement reporting, and ISO 20022 gives it a compact business area, `casr`: **settlement reporting**. It is one of the smallest areas in the card family, two messages, but it closes the loop on the transaction traffic. This article covers what the two `casr` messages are and how they exchange.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What casr is for

`casr` belongs to the ISO 20022 card family, alongside the acquirer-to-issuer transaction area, fee collection, and network management. Its job is to report **settlement**: the positions and totals that result once a period of card transactions is aggregated for money to move between the parties. Rather than derive settlement from the raw transaction messages, the parties exchange a dedicated report so the figures are stated explicitly and can be accepted or disputed on their own.

![Settlement reporting request and response between card parties]({{site.url_complet}}/assets/article/finance/casr-settlement-reporting-workflow.png)

The parties are the familiar card actors: an acquirer, an issuer, and often a scheme or processor that collates the positions.

## The two messages

The area is a single request-and-response pair.

| Identifier | Message | Role |
|------------|---------|------|
| `casr.001` | SettlementReportingInitiation | Report settlement positions and totals |
| `casr.002` | SettlementReportingResponse | Accept or reject the settlement report |

The **`casr.001` SettlementReportingInitiation** carries the settlement data: the positions, totals, and amounts due for the period being reported. The **`casr.002` SettlementReportingResponse** answers, accepting or rejecting the report. As with the rest of the card family, both messages open with the shared header carrying the message function, and sensitive data is protected and messages are authenticated, because settlement reports cross networks between institutions.

## Conclusion

The `casr` business area is a small, focused part of the ISO 20022 card family. Two messages, a settlement reporting initiation and its response, let card parties state and confirm the settlement positions and totals that arise from a period of transactions, on the same protected, authenticated envelope as the transactions themselves. It gives settlement figures their own explicit exchange rather than leaving them to be inferred from transaction traffic. Read next to the acquirer-to-issuer transaction area whose activity it settles and the fee-collection area it sits beside, `casr` is the reporting step that closes the card money cycle.

![Mindmap summarising the ISO 20022 casr settlement reporting area]({{site.url_complet}}/assets/article/finance/iso20022-settlement-reporting-casr.png)

## Frequently Asked Questions

**Q: What does the casr area do?**

It reports card settlement. Once a period of card transactions has been authorised and cleared, the amounts owed between the parties have to be tallied into settlement positions and totals, and `casr` provides a dedicated exchange for that. A `casr.001` SettlementReportingInitiation states the positions and amounts, and a `casr.002` SettlementReportingResponse accepts or rejects them. It gives the settlement figures an explicit, confirmable message rather than leaving them implicit in the transaction data.

**Q: Why are there only two messages?**

Because the process is a single report and its answer. One party states the settlement position; the other accepts or disputes it. There is no multi-step lifecycle beyond that response, so two messages are enough. As with other small card areas, a two-message design reflects a cleanly bounded process rather than an incomplete one.

**Q: How is a casr message protected?**

Through the card family's data-protection model, shared with the transaction, fee-collection, and network-management areas. Sensitive fields are carried in protected, encrypted form rather than in the clear, and messages are authenticated so a receiver can trust their origin. The keys are provisioned outside the settlement-reporting messages themselves. Because a settlement report crosses networks between institutions, it assumes the same untrusted path the transaction messages do.

**Q: How does casr differ from cafc?**

They report different things in the same family. `cafc` (fee collection) collects the fees that surround transactions, the scheme and service charges owed between parties. `casr` (settlement reporting) reports the settlement positions and totals that result from the transactions themselves. Both are two-message request-and-response pairs on the shared card envelope, but one concerns fees and the other concerns the settlement of the underlying card activity.

**Q: Where does casr sit in the card money cycle?**

At the end. A card payment is driven at the till (sale-to-POI), authorised and cleared between acquirer and issuer, has its fees collected through fee collection, and its resulting settlement positions reported and confirmed through `casr`. Network management keeps the links alive underneath, and fraud reporting handles any fraudulent transactions. `casr` is the step that states what is owed once all the transactions of a period are aggregated, closing the loop that the transaction messages open.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 card and payment messages](https://www.iso20022.org/payments)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [nexo standards — card payment message specifications](https://www.nexo-standards.org/)
- [Claude Code](https://claude.com/product/claude-code)
