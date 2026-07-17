---
layout: post
title: "ISO 20022 for Trade Services — The tsrv Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation
tags: iso20022 trade-finance guarantee standby tsrv undertaking
description: How ISO 20022 models bank guarantees and standby letters of credit through the tsrv business area, covering the issuance, amendment, demand, and termination of an undertaking between applicant, guarantor, advising party, and beneficiary.
image: /assets/article/finance/iso20022-trade-services-tsrv.png
isMath: false
---



A bank guarantee is a promise: if one party fails to perform, the bank will pay the other. That promise, and the standby letter of credit that works the same way, underpins a large share of international trade and construction contracts. ISO 20022 gives the lifecycle of such a promise a structured vocabulary in its `tsrv` business area, **trade services**. This article walks through the nineteen `tsrv` messages, the four parties they move between, and the life of an **undertaking** from issuance through amendment to a demand for payment.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What tsrv covers

The `tsrv` area is about **independent undertakings**: demand guarantees and standby letters of credit. Both are promises by a bank (the guarantor) to pay a beneficiary on presentation of a compliant demand, independent of the underlying commercial contract. That independence is the point: the beneficiary does not have to prove a breach in court, only present the documents the undertaking specifies. These instruments are governed by industry rules such as the ICC's Uniform Rules for Demand Guarantees (URDG 758) and the International Standby Practices (ISP98), and `tsrv` carries them in ISO 20022 form, modernising the older SWIFT MT760 family of guarantee messages.

![The parties to a demand guarantee and the tsrv messages between them]({{site.url_complet}}/assets/article/finance/tsrv-parties-concept.png)

Four parties recur. The **applicant** asks for the undertaking and carries the underlying obligation. The **guarantor** (an obligor bank) issues it. An **advising party** may pass it to the beneficiary and vouch for its authenticity. The **beneficiary** is the party protected, the one who can make a demand if the applicant fails to perform.

## The tsrv message catalogue

The nineteen messages follow the life of an undertaking through four stages: issuance, amendment, ending, and demand, with two status reports covering all of them.

| Identifier | Message | Stage |
|------------|---------|-------|
| `tsrv.001` | UndertakingIssuance | Issuance |
| `tsrv.002` | UndertakingIssuanceAdvice | Issuance |
| `tsrv.003` | UndertakingIssuanceNotification | Issuance |
| `tsrv.004` | UndertakingAmendmentRequest | Amendment |
| `tsrv.005` | UndertakingAmendment | Amendment |
| `tsrv.006` | UndertakingAmendmentAdvice | Amendment |
| `tsrv.007` | UndertakingAmendmentNotification | Amendment |
| `tsrv.008` | UndertakingAmendmentResponse | Amendment |
| `tsrv.009` | UndertakingAmendmentResponseNotification | Amendment |
| `tsrv.010` | UndertakingNonExtensionRequest | Ending |
| `tsrv.011` | UndertakingNonExtensionNotification | Ending |
| `tsrv.012` | UndertakingTerminationNotification | Ending |
| `tsrv.013` | UndertakingDemand | Demand |
| `tsrv.014` | ExtendOrPayRequest | Demand |
| `tsrv.015` | ExtendOrPayResponse | Demand |
| `tsrv.016` | DemandRefusalNotification | Demand |
| `tsrv.017` | DemandWithdrawalNotification | Demand |
| `tsrv.018` | TradeStatusReport | Status |
| `tsrv.019` | UndertakingStatusReport | Status |

The recurring trio of **issuance**, **advice**, and **notification** reflects the routing chain. The `tsrv.001` UndertakingIssuance is the undertaking itself, whose content is carried in an undertaking-issuance-details (`UdrtkgIssncDtls`) block. The advice (`tsrv.002`) informs the party being sent the undertaking, and the notification (`tsrv.003`) tells the beneficiary it exists. The amendment stage repeats the same pattern for changes, adding a response because an amendment to a guarantee usually needs the beneficiary's agreement to take effect.

## The life of an undertaking

The messages make most sense followed through a single undertaking's life.

![Life of an undertaking: issue, amend, and demand]({{site.url_complet}}/assets/article/finance/tsrv-undertaking-workflow.png)

**Issuance.** At the applicant's request, the guarantor issues the undertaking with a `tsrv.001` **UndertakingIssuance**, routed through any advising party with an advice (`tsrv.002`) and reaching the beneficiary as a notification (`tsrv.003`). The beneficiary now holds an enforceable promise.

**Amendment.** Terms change: an amount is reduced as a contract is fulfilled, or an expiry date is pushed out. The applicant asks with a `tsrv.004` **AmendmentRequest**, the guarantor issues the `tsrv.005` **Amendment** with its advice and notification, and the beneficiary accepts or rejects it in a `tsrv.008` **AmendmentResponse**, itself notified onward by `tsrv.009`. Because an amendment can only bind the beneficiary with consent, the response is an essential part of the flow rather than an afterthought.

**Ending.** Many undertakings are evergreen, renewing automatically unless stopped. A `tsrv.010` **NonExtensionRequest** and its `tsrv.011` notification signal that an undertaking will not be renewed at its next expiry, and a `tsrv.012` **TerminationNotification** records that it has ended.

**Demand.** The moment the instrument exists for is the demand. The beneficiary presents a `tsrv.013` **UndertakingDemand** claiming payment. A common answer is not a flat pay-or-refuse but the **extend-or-pay** exchange: the guarantor, prompted by the applicant, offers to extend the undertaking's validity instead of paying now, in a `tsrv.014` **ExtendOrPayRequest**, and the beneficiary responds with a `tsrv.015` **ExtendOrPayResponse** choosing extension or payment. If the demand does not comply with the undertaking's terms, the guarantor sends a `tsrv.016` **DemandRefusalNotification**; if the beneficiary drops the claim, a `tsrv.017` **DemandWithdrawalNotification** records it.

**Status.** Throughout, the `tsrv.018` **TradeStatusReport** and `tsrv.019` **UndertakingStatusReport** report where a trade or an undertaking stands, so parties can reconcile without inferring state from the flow of events.

## Conclusion

The `tsrv` business area brings bank guarantees and standby letters of credit into ISO 20022. Its nineteen messages follow an undertaking from issuance, through amendments that need the beneficiary's consent, to the demand the instrument exists to answer, with a distinctive extend-or-pay exchange and status reports throughout. The design mirrors the industry rules that govern these instruments and the routing chain of applicant, guarantor, advising party, and beneficiary. As the ISO 20022 successor to the MT760 guarantee family, `tsrv` is where trade finance's oldest promise meets the modern message standard.

![Mindmap summarising the ISO 20022 tsrv trade services area]({{site.url_complet}}/assets/article/finance/iso20022-trade-services-tsrv.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **tsrv** | The ISO 20022 trade services business area, covering demand guarantees and standby letters of credit across nineteen messages. |
| **Undertaking** | An independent promise by a bank to pay a beneficiary on a compliant demand, taking the form of a demand guarantee or standby letter of credit. |
| **Demand guarantee** | A guarantee payable on the beneficiary's demand, independent of proof of breach of the underlying contract. |
| **Standby letter of credit** | A letter of credit that functions as a guarantee, paying the beneficiary if the applicant fails to perform. |
| **Applicant** | The party that requests the undertaking and carries the underlying obligation. |
| **Guarantor** | The obligor bank that issues the undertaking and pays a compliant demand. |
| **Beneficiary** | The party protected by the undertaking, entitled to make a demand for payment. |
| **Amendment** | A change to an undertaking's terms, which binds the beneficiary only with its consent (`tsrv.008`). |
| **Demand** | The beneficiary's claim for payment under the undertaking, carried by `tsrv.013`. |
| **Extend or pay** | A response to a demand offering to extend the undertaking's validity instead of paying immediately, carried by `tsrv.014` and `tsrv.015`. |

## Frequently Asked Questions

**Q: What is an independent undertaking, and why does independence matter?**

An independent undertaking is a bank's promise to pay a beneficiary on presentation of a compliant demand, separate from the underlying commercial contract. Independence means the beneficiary does not have to prove that the applicant breached the contract; it only has to present the documents the undertaking specifies. This makes the instrument fast and reliable for the beneficiary, which is exactly why demand guarantees and standby letters of credit are used to secure trade and construction obligations. The `tsrv` messages carry these undertakings without needing to reference the merits of the underlying dispute.

**Q: Why do issuance and amendment each involve three messages (issuance, advice, notification)?**

Because an undertaking travels through a chain of parties, and each link needs the right message. The `tsrv.001` UndertakingIssuance is the undertaking itself, sent by the guarantor. The advice (`tsrv.002`) informs a party in the routing chain, such as an advising bank, that is being asked to pass the undertaking on. The notification (`tsrv.003`) tells the beneficiary the undertaking exists. The amendment stage repeats the pattern for changes. Splitting the roles lets each party in the chain receive a message suited to its position rather than a single message overloaded with every purpose.

**Q: What is the extend-or-pay mechanism?**

Extend-or-pay is a common response to a demand under a guarantee. Instead of paying immediately or refusing, the guarantor, usually prompted by the applicant, offers the beneficiary a choice: allow the undertaking's validity to be extended, or be paid now. It is carried by the `tsrv.014` ExtendOrPayRequest and the `tsrv.015` ExtendOrPayResponse. The mechanism gives the applicant time to resolve the underlying issue while leaving the beneficiary protected, because if it declines the extension it is paid. It is one of the distinctive features of demand-guarantee practice that `tsrv` models directly.

**Q: Why does an amendment need a response when an issuance does not?**

Because an amendment changes the terms of a promise the beneficiary already holds, and it cannot be forced on the beneficiary. Reducing an amount, changing an expiry, or altering a condition affects the beneficiary's protection, so the amendment takes effect only if the beneficiary consents. The `tsrv.008` AmendmentResponse carries that acceptance or rejection. An issuance, by contrast, creates a new undertaking in the beneficiary's favour, which it can simply hold; there is nothing for it to agree to for the undertaking to exist.

**Q: How does tsrv relate to the older SWIFT MT guarantee messages?**

`tsrv` is the ISO 20022 successor to the MT760 family that banks have long used to issue and amend guarantees and standby letters of credit over SWIFT. It expresses the same lifecycle, issuance, amendment, demand, and termination, in ISO 20022's structured XML, aligned with the ICC rules (URDG 758 and ISP98) that govern these instruments. As with other areas, the MX form carries richer, explicitly typed data than the older message, which helps automate the checking of demands and the tracking of an undertaking's state.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 trade services messages](https://www.iso20022.org/trade-services)
- [ICC — Uniform Rules for Demand Guarantees (URDG 758)](https://iccwbo.org/business-solutions/all-rules-guidelines/)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [Claude Code](https://claude.com/product/claude-code)
