---
layout: post
title: "ISO 20022 for Card Fee Collection — The cafc Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 cards cafc fees acquirer issuer
description: How ISO 20022 models card fee collection through the cafc business area, a two-message request-and-response pair that collects scheme and service fees between card parties on the same protected envelope as the transaction messages.
image: /assets/article/finance/iso20022-fee-collection-cafc.png
isMath: false
---



Card transactions do not just move a purchase amount. Around every payment sits a set of fees: scheme fees, processing fees, and service charges that flow between the acquirer, the issuer, and the network that connects them. Collecting those fees is its own small process, and ISO 20022 gives it a dedicated business area, `cafc`: **fee collection**. It is the smallest area covered in this series, just two messages, but it sits on the same card-message machinery as authorisation and clearing. This article covers what the two `cafc` messages are, how they exchange, and what they carry.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What cafc is for

The `cafc` area belongs to the ISO 20022 card family, alongside the acquirer-to-issuer transaction area and the fraud-reporting area. Where those carry purchases and fraud information, `cafc` carries the collection of **fees** between card parties: the amounts a scheme or processor charges an acquirer or issuer for its services, or that one party owes another under the card scheme's rules. Rather than bundle these charges into the transaction messages, the standard gives them their own exchange, so a fee can be collected, and accepted or rejected, on its own terms.

![Fee collection request and response between card parties]({{site.url_complet}}/assets/article/finance/cafc-fee-collection-workflow.png)

## The two messages

The area is a single request-and-response pair.

| Identifier | Message | Role |
|------------|---------|------|
| `cafc.001` | FeeCollectionInitiation | Initiate the collection of a fee |
| `cafc.002` | FeeCollectionResponse | Accept or reject the fee collection |

The **`cafc.001` FeeCollectionInitiation** starts the collection: the collecting party tells the charged party that a fee is due and for how much. The **`cafc.002` FeeCollectionResponse** answers, accepting or rejecting it. That is the whole area, a deliberately minimal design for a process that is itself simple: one party asks to collect, the other agrees or refuses.

## What the messages carry

Every `cafc` message uses the same envelope as the rest of the card family. The `cafc.001` initiation opens with a header and then the fee's details, drawn directly from the schema:

- **Header (`Hdr`, type `Header72`)** carries the message function and the routing and versioning data shared across the card messages.
- **Acquirer (`Acqrr`)** identifies the acquiring party involved.
- **Transaction identification (`TxId`)** names the fee-collection transaction.
- **Transaction amounts (`TxAmts`)** carry the amount to be collected.

Because it uses the card family's envelope, `cafc` inherits its protection model: sensitive fields are carried in protected form and messages are authenticated, so a fee collection crossing a network between institutions cannot be read or forged. Using the same header and structure as the transaction messages also means a system that already speaks the acquirer-to-issuer card protocol needs little extra to handle fee collection.

## Conclusion

The `cafc` business area is the smallest in this series, and deliberately so. Two messages, a fee-collection initiation and its response, let card parties collect the scheme and service fees that surround transactions, on the same protected, authenticated envelope as the payments themselves. It is a clean illustration of how ISO 20022 gives even a narrow process its own well-scoped area rather than overloading a neighbouring one. Read next to the acquirer-to-issuer transaction area whose fees it collects, `cafc` completes a small corner of the card standard.

![Mindmap summarising the ISO 20022 cafc fee collection area]({{site.url_complet}}/assets/article/finance/iso20022-fee-collection-cafc.png)

## Frequently Asked Questions

**Q: What does the cafc area do?**

It collects fees between card parties. The card ecosystem generates charges around transactions, scheme fees, processing fees, and service charges owed between acquirers, issuers, and the network. `cafc` provides a dedicated exchange to collect them: a `cafc.001` FeeCollectionInitiation states the fee due, and a `cafc.002` FeeCollectionResponse accepts or rejects it. It keeps fee collection separate from the transaction messages so that a charge can be handled on its own.

**Q: Why are there only two messages?**

Because the process is a single request and answer. One party asks to collect a fee; the other agrees or refuses. There is no multi-step negotiation, no physical delivery, and no lifecycle to track beyond the response, so two messages suffice. A small, well-scoped area is a sign the standard has drawn a clean boundary around a simple process rather than left it incomplete.

**Q: What does a cafc.001 message contain?**

Four parts, visible in the schema. A header (`Hdr`, type `Header72`) with the message function and the routing and versioning data shared across the card messages; an acquirer block (`Acqrr`) identifying the acquiring party; a transaction identification (`TxId`) naming the fee-collection transaction; and transaction amounts (`TxAmts`) giving the amount to be collected. Together they say who is involved, which collection this is, and how much is due.

**Q: How is a cafc message protected?**

Through the card family's data-protection model, the same one used by the transaction and fraud messages. Sensitive fields are carried in protected, encrypted form rather than in the clear, and messages are authenticated so a receiver can trust their origin. The cryptographic keys are provisioned outside the fee-collection messages themselves. The protection matters because a fee collection crosses networks between institutions, the same untrusted path the card transaction messages must assume.

**Q: How does cafc relate to the other card areas?**

It shares their envelope and complements their purpose. The acquirer-to-issuer area carries the transactions themselves, the fraud area carries fraud information about those transactions, and `cafc` carries the fees that surround them. All use the same `Header72` and the same protection model, so a party that implements the transaction protocol can add fee collection with little extra work. A card payment might be authorised and cleared through the transaction area, and the fees it generates then collected through `cafc`.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 card and payment messages](https://www.iso20022.org/payments)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [nexo standards — card payment message specifications](https://www.nexo-standards.org/)
- [Claude Code](https://claude.com/product/claude-code)
