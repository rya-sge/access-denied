---
layout: post
title: "ISO 20022 for Foreign Exchange Trade — The fxtr Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 foreign-exchange fx fxtr confirmation settlement
description: How ISO 20022 models the foreign exchange post-trade process through the fxtr business area, covering trade capture, confirmation and matching, status notification, and net settlement reporting between counterparties and their matching and settlement services.
image: /assets/article/finance/iso20022-fx-trade-fxtr.png
isMath: false
---



A foreign exchange trade is agreed in seconds, but the work of confirming it, matching both sides, and settling two currencies safely takes the rest of the day. That post-trade work needs a common language, and ISO 20022 supplies one in its `fxtr` business area: **foreign exchange trade**. This article walks through the fifteen `fxtr` messages, plus the `camt.088` net report that ships with them, and shows how they carry an FX trade from capture through confirmation and status to net settlement.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What fxtr covers

The `fxtr` area is about the FX trade *after* it is executed. It does not match orders or make prices; it takes a done deal (a spot, a forward, a swap, or a non-deliverable forward) and carries it through the confirmation and settlement chain. The parties are the two counterparties to the trade, the matching and confirmation services that sit between them, and the settlement systems, most importantly CLS, that settle the two currency legs.

![FX post-trade flow and where the fxtr messages fit]({{site.url_complet}}/assets/article/finance/fxtr-posttrade-concept.png)

The reason this needs a standard is settlement risk. In FX, each side must pay the currency it sold and receive the currency it bought, and a party that pays out before it receives is exposed to its counterparty failing in between. Confirmation (agreeing the trade's terms precisely) and matching (checking that both sides recorded the same deal) are the controls that make settlement safe, and `fxtr` is the message vocabulary for both.

## The fxtr message catalogue

The fifteen messages fall into three groups, plus a net settlement report. The groups are trade instruction and status, trade capture, and confirmation.

| Identifier | Message | Group |
|------------|---------|-------|
| `fxtr.014` | ForeignExchangeTradeInstruction | Instruction and status |
| `fxtr.015` | ForeignExchangeTradeInstructionAmendment | Instruction and status |
| `fxtr.016` | ForeignExchangeTradeInstructionCancellation | Instruction and status |
| `fxtr.013` | ForeignExchangeTradeWithdrawalNotification | Instruction and status |
| `fxtr.008` | ForeignExchangeTradeStatusNotification | Instruction and status |
| `fxtr.017` | ForeignExchangeTradeStatusAndDetailsNotification | Instruction and status |
| `fxtr.030` | ForeignExchangeTradeBulkStatusNotification | Instruction and status |
| `fxtr.031` | ForeignExchangeTradeCaptureReport | Capture |
| `fxtr.032` | ForeignExchangeTradeCaptureReportRequest | Capture |
| `fxtr.033` | ForeignExchangeTradeCaptureReportAcknowledgement | Capture |
| `fxtr.034` | ForeignExchangeTradeConfirmationRequest | Confirmation |
| `fxtr.035` | ForeignExchangeTradeConfirmationRequestAmendmentRequest | Confirmation |
| `fxtr.036` | ForeignExchangeTradeConfirmationRequestCancellationRequest | Confirmation |
| `fxtr.037` | ForeignExchangeTradeConfirmationStatusAdvice | Confirmation |
| `fxtr.038` | ForeignExchangeTradeConfirmationStatusAdviceAcknowledgement | Confirmation |
| `camt.088` | NetReport | Net settlement |

### What a trade instruction carries

The `fxtr.014` ForeignExchangeTradeInstruction is the central message of the area, the one that submits a trade for matching and settlement. Its structure names the economic terms of the deal directly:

- **Trade information (`TradInf`)** identifies the trade and its status.
- **Trading-side and counterparty-side identification (`TradgSdId`, `CtrPtySdId`)** name the two parties to the deal.
- **Traded amounts (`TradAmts`)** carry the two currency amounts being exchanged.
- **Agreed rate (`AgrdRate`)** carries the exchange rate the parties struck.

Those four blocks are the heart of any FX confirmation: who traded with whom, which two amounts, and at what rate. The amendment (`fxtr.015`) and cancellation (`fxtr.016`) act on a previously sent instruction, and the withdrawal notification (`fxtr.013`) tells the service a trade has been pulled.

## The post-trade flow, message by message

The three groups map onto three stages a trade passes through.

![FX trade capture, confirmation, and status]({{site.url_complet}}/assets/article/finance/fxtr-capture-confirm-workflow.png)

**Capture.** Before or alongside confirmation, a party may want the service's record of a trade. The `fxtr.032` **TradeCaptureReportRequest** asks for it, the `fxtr.031` **TradeCaptureReport** returns the captured trade detail, and the `fxtr.033` **TradeCaptureReportAcknowledgement** confirms receipt. This is the reporting view of what the service holds, used by middle-office and reconciliation systems.

**Instruction and status.** The party submits the trade with an `fxtr.014` **TradeInstruction**, amends or cancels it if needed with `fxtr.015` and `fxtr.016`, and receives progress back through the status messages. A single trade's status comes in an `fxtr.008` **StatusNotification** or the fuller `fxtr.017` **StatusAndDetailsNotification**, which returns the status together with the trade's details, while many trades at once are reported in an `fxtr.030` **BulkStatusNotification**. Status is where a party learns whether its trade matched the other side.

**Confirmation.** The confirmation exchange establishes that both sides agree the terms. A party raises a `fxtr.034` **ConfirmationRequest**, adjusts it with the `fxtr.035` amendment request or withdraws it with the `fxtr.036` cancellation request, and the service reports the confirmation outcome in a `fxtr.037` **ConfirmationStatusAdvice**, which the party acknowledges with `fxtr.038`. A matched, confirmed trade is one both counterparties have agreed identically and is safe to settle.

**Net settlement.** Where trades are settled on a net basis, the `camt.088` **NetReport** reports the netted amounts per currency that will actually move, the figures a party funds into a settlement system such as CLS. Netting many trades down to one payment per currency is what keeps FX settlement volumes manageable, and the net report is how those final positions are communicated.

## Conclusion

The `fxtr` business area applies ISO 20022 to the foreign exchange post-trade process. Its fifteen messages carry a trade through capture, confirmation, and status, with amendment and cancellation at each step, and the accompanying `camt.088` reports the net amounts for settlement. The design centres on the two controls that make FX settlement safe: confirmation, so both parties agree the exact terms, and matching, so both recorded the same deal. Read next to the settlement systems it feeds, `fxtr` is the standard vocabulary for turning an executed FX trade into a matched, confirmed, and settleable one.

![Mindmap summarising the ISO 20022 fxtr foreign exchange trade area]({{site.url_complet}}/assets/article/finance/iso20022-fx-trade-fxtr.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **fxtr** | The ISO 20022 foreign exchange trade business area, covering FX post-trade capture, confirmation, status, and net reporting across fifteen messages. |
| **Confirmation** | The process of agreeing the precise terms of an FX trade between the two counterparties, carried by the `fxtr.034` to `fxtr.038` messages. |
| **Matching** | Checking that both counterparties recorded the same trade, reported through the status notifications. |
| **Trade instruction (`fxtr.014`)** | The message submitting an FX trade for matching and settlement, carrying the parties, amounts, and agreed rate. |
| **Agreed rate (`AgrdRate`)** | The exchange rate the two parties struck, one of the core economic terms of an FX trade. |
| **Traded amounts (`TradAmts`)** | The two currency amounts exchanged in the trade. |
| **Trade capture report** | The service's record of a captured trade, requested and returned by `fxtr.032`, `fxtr.031`, and `fxtr.033`. |
| **Net report (`camt.088`)** | The report of netted per-currency amounts to be settled, the figures a party funds into a settlement system. |
| **CLS** | The settlement system that settles the two currency legs of an FX trade to remove settlement risk. |
| **Settlement risk** | The risk that a party pays the currency it sold but does not receive the currency it bought because its counterparty fails. |

## Frequently Asked Questions

**Q: What is the difference between confirmation and matching in fxtr?**

Confirmation is agreeing the precise terms of a trade with the counterparty; matching is checking that both sides recorded the same deal. Confirmation is handled by the dedicated `fxtr.034` to `fxtr.038` messages, which raise, adjust, and report the status of a confirmation. Matching is reflected in the status notifications (`fxtr.008`, `fxtr.017`, `fxtr.030`), where a party learns whether its submitted trade lined up with the other side's. Both must succeed before a trade is safe to settle: the terms have to be agreed and both records have to align.

**Q: What are the core economic terms carried by a trade instruction?**

Four blocks in the `fxtr.014` instruction carry them: trade information identifying the deal, the trading-side and counterparty-side identifications naming the two parties, the traded amounts giving the two currency amounts, and the agreed rate giving the exchange rate. Together they answer who traded with whom, which two amounts, and at what rate, which is exactly what an FX confirmation must pin down.

**Q: Why does FX settlement need this much process around a simple trade?**

Because of settlement risk. Each side of an FX trade must deliver the currency it sold and receive the currency it bought, and if one party pays out before it receives, it is exposed to the other failing in the gap. Confirmation and matching are the controls that reduce this risk by ensuring both sides agree the same terms before any money moves, and settling on a net basis through a system like CLS reduces the number and size of payments at risk. The `fxtr` messages exist to carry those controls in a standard, machine-readable form.

**Q: What does the camt.088 net report do, and why is it here rather than in cash management?**

The `camt.088` NetReport reports the netted amounts per currency that will actually settle after many trades are combined. It ships alongside `fxtr` because FX settlement is where net positions matter most: rather than settling every trade gross, parties net them down to one payable or receivable per currency and fund that figure into a settlement system. The message carries a `camt` identifier because it is a cash-management report by nature, but it is packaged with the FX trade messages because that is the flow it serves.

**Q: How does a trade move through the three fxtr groups in order?**

A party can pull the service's record of the trade through the capture group (`fxtr.032` request, `fxtr.031` report, `fxtr.033` acknowledgement). It submits the trade for processing with an instruction (`fxtr.014`), amending or cancelling as needed, and receives matching progress through the status notifications (`fxtr.008`, `fxtr.017`, `fxtr.030`). It agrees the exact terms through the confirmation group (`fxtr.034` to `fxtr.038`). Once the trade is matched and confirmed, its net settlement amounts are reported in `camt.088`. The groups are not strictly sequential in every implementation, but capture, instruction and status, and confirmation together take a trade from executed to settleable.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 foreign exchange messages](https://www.iso20022.org/foreign-exchange)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [CLS — settlement of foreign exchange](https://www.cls-group.com/)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [Claude Code](https://claude.com/product/claude-code)
