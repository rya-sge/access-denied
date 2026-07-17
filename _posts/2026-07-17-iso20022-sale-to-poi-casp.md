---
layout: post
title: "ISO 20022 for Sale to POI — The casp Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 cards casp point-of-interaction retail pos
description: How ISO 20022 models the interface between a retailer's sale system and its payment terminal through the casp business area, covering the service, session, device, reconciliation, and reporting messages of the sale-to-POI protocol.
image: /assets/article/finance/iso20022-sale-to-poi-casp.png
isMath: false
---



At a shop checkout, two devices talk to each other before your card is ever charged: the **sale system**, the cash register or point-of-sale application ringing up the goods, and the **POI**, the payment terminal that reads the card. ISO 20022 standardises the conversation between them in its `casp` business area: **sale to POI**. This article covers the seventeen `casp` messages, the request-and-response pattern they share, and how a cash register drives a payment terminal through a card sale.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What casp covers

`casp` sits at a very specific interface: between the **sale system** (the retailer's till or point-of-sale application) and the **POI**, the Point of Interaction, which is the payment terminal or acceptance device. It does not reach the acquirer. When the cashier presses "pay", the sale system tells the POI to take a payment; the POI runs the card transaction with the acquirer over its own rails and reports the result back to the sale system. `casp` is only the sale-to-POI leg, standardising what has historically been a mess of proprietary, terminal-specific integrations.

![Where casp sits: sale system, POI, and acquirer]({{site.url_complet}}/assets/article/finance/casp-sale-poi-concept.png)

This standard grew out of the nexo retailer protocol, and its value is portability: a retailer whose till speaks `casp` can work with any conformant terminal, rather than writing bespoke code for each device.

## The casp message catalogue

The seventeen messages are organised as request-and-response pairs by function, with a few standalone control messages. Each message shares a header carrying its function and a body specific to the operation, for example the `casp.001` service request opens with a header and a service-request block.

| Identifier | Message | Function |
|------------|---------|----------|
| `casp.001` / `casp.002` | SaleToPOIServiceRequest / Response | Payment, refund, and other services |
| `casp.003` / `casp.004` | SaleToPOIReconciliationRequest / Response | Reconcile totals |
| `casp.005` / `casp.006` | SaleToPOISessionManagementRequest / Response | Open and close a session |
| `casp.007` / `casp.008` | SaleToPOIAdministrativeRequest / Response | Administrative operations |
| `casp.009` / `casp.010` | SaleToPOIReportRequest / Response | Retrieve reports |
| `casp.016` / `casp.017` | SaleToPOIDeviceRequest / Response | Drive the terminal's devices |
| `casp.014` / `casp.015` | SaleToPOIMessageStatusRequest / Response | Query the status of a message |
| `casp.011` | SaleToPOIAbort | Abort an operation |
| `casp.012` | SaleToPOIEventNotification | Notify an event |
| `casp.013` | SaleToPOIMessageRejection | Reject a message |

The **service** pair is the heart of the area: it carries the actual payment, refund, reversal, and related card services the sale system asks the POI to perform. The **device** pair is distinctive: it lets the sale system drive the terminal's peripherals directly, printing a receipt, showing a message on the display, or capturing input from the cardholder, so the two devices act as one system. The remaining pairs handle sessions, administration, reporting, and reconciliation, while the standalone messages abort operations, notify events, reject malformed messages, and query message status.

## A card payment at the till

The messages come together in an ordinary purchase.

![A card payment driven from the sale system]({{site.url_complet}}/assets/article/finance/casp-payment-service-workflow.png)

**Open a session.** The sale system opens a working session with the POI using a `casp.005` SessionManagementRequest, acknowledged by a `casp.006` response. This establishes the context the subsequent operations run in.

**Request the payment.** The cashier totals the basket and the sale system sends a `casp.001` ServiceRequest asking the POI to take a payment for the amount. The POI does its job, prompting the cardholder, reading the card, and authorising with the acquirer over its own connection, and returns the outcome in a `casp.002` ServiceResponse: approved or declined.

**Drive the devices.** To finish the sale, the sale system asks the POI to print the receipt with a `casp.016` DeviceRequest, answered by a `casp.017` response. The same pair can display prompts or capture cardholder input during the flow.

**Reconcile.** At the end of the day the sale system reconciles with the POI using a `casp.003` ReconciliationRequest and its `casp.004` response, agreeing the totals of what was taken. Throughout, an operation can be cancelled with a `casp.011` Abort, unexpected occurrences are announced with a `casp.012` EventNotification, and a message that cannot be processed is answered with a `casp.013` MessageRejection.

## Conclusion

The `casp` business area standardises the conversation between a retailer's sale system and its payment terminal. Its seventeen messages, mostly request-and-response pairs, let a cash register drive a POI through a card sale: open a session, request a payment or refund, drive the terminal's printer and display, retrieve reports, and reconcile totals, with control messages to abort, notify, and reject. It covers only the sale-to-POI leg, leaving the POI to reach the acquirer over its own rails, and its payoff is portability: a till that speaks `casp` works with any conformant terminal. It is the ISO 20022 answer to the tangle of proprietary terminal integrations that retail once required.

![Mindmap summarising the ISO 20022 casp sale-to-POI area]({{site.url_complet}}/assets/article/finance/iso20022-sale-to-poi-casp.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **casp** | The ISO 20022 sale-to-POI business area, standardising the interface between a sale system and a payment terminal across seventeen messages. |
| **Sale system** | The retailer's cash register or point-of-sale application that rings up goods and requests payment. |
| **POI** | The Point of Interaction, the payment terminal or acceptance device that reads the card and runs the transaction. |
| **Service request (`casp.001`)** | The message by which the sale system asks the POI to perform a payment, refund, or related service. |
| **Device request (`casp.016`)** | The message by which the sale system drives the POI's peripherals, such as the printer, display, or input. |
| **Session management (`casp.005`)** | The pair that opens and closes a working session between the sale system and the POI. |
| **Reconciliation (`casp.003`)** | The pair that agrees the totals of what the POI has processed, typically at end of day. |
| **Abort (`casp.011`)** | The control message that cancels an in-progress operation. |
| **Event notification (`casp.012`)** | The message announcing an unexpected event to the counterpart. |
| **nexo retailer protocol** | The industry protocol from which the sale-to-POI messages derive. |

## Frequently Asked Questions

**Q: What interface does casp standardise, and what does it deliberately leave out?**

`casp` standardises the interface between the sale system (the cash register or point-of-sale application) and the POI (the payment terminal). It lets the till tell the terminal to take a payment, drive its printer and display, manage sessions, and reconcile totals. It deliberately leaves out the leg from the POI to the acquirer: the terminal runs the actual card authorisation over its own rails. `casp` is only the sale-to-POI conversation, which is exactly the part that used to require bespoke, terminal-specific integration.

**Q: Why is the device pair (casp.016 / casp.017) important?**

Because it lets the sale system drive the terminal's peripherals directly, so the two devices behave as one integrated system. Through a `casp.016` DeviceRequest and its `casp.017` response, the sale system can make the POI print a receipt, show a message or prompt on its display, or capture input from the cardholder. Without this, the till and terminal would be two disconnected devices; with it, the cashier's application controls the whole customer-facing flow, which is a large part of what a modern point-of-sale integration needs.

**Q: How does a typical payment flow through the casp messages?**

The sale system opens a session with a `casp.005` request and `casp.006` response, then asks for the payment with a `casp.001` ServiceRequest carrying the amount. The POI prompts the cardholder, reads the card, authorises with the acquirer over its own connection, and returns the result in a `casp.002` ServiceResponse. The sale system then prints the receipt with a `casp.016` DeviceRequest. At end of day it reconciles totals with a `casp.003` reconciliation request. Control messages such as abort (`casp.011`) and rejection (`casp.013`) handle the exceptions.

**Q: Why does standardising the sale-to-POI interface matter for retailers?**

Because it delivers portability. Historically, integrating a till with a payment terminal meant writing code specific to each terminal model and vendor, an expensive and brittle arrangement. When both the sale system and the terminal speak `casp`, the till can work with any conformant POI, and a retailer can change terminals or add vendors without re-integrating. Standardising this one interface removes a long-standing source of cost and lock-in in retail payment acceptance.

**Q: How does casp relate to the other card areas?**

`casp` is the front of the chain, at the point of sale. The POI it drives then talks to the acquirer using the acquirer-to-issuer transaction messages, maintains that link with the network-management messages, and the whole chain shares the card family's protection model. So a purchase begins as a `casp` exchange between till and terminal, becomes an acquirer-to-issuer authorisation once the POI reaches the acquirer, and settles through the card clearing and settlement traffic. `casp` covers only the first leg, but it is the one the customer and cashier actually see.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 card and payment messages](https://www.iso20022.org/payments)
- [nexo standards — retailer protocol and sale-to-POI](https://www.nexo-standards.org/)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [Claude Code](https://claude.com/product/claude-code)
