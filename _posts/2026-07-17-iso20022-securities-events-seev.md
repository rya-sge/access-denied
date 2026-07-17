---
layout: post
title: "ISO 20022 for Securities Events — The seev Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 securities seev corporate-actions proxy-voting
description: A tour of ISO 20022's seev (securities events) business area, covering corporate actions, general meetings and proxy voting, shareholder identification, market claims, and buyer protection across the custody chain.
image: /assets/article/finance/iso20022-securities-events-seev.png
isMath: false
---



Owning a share is not a static thing. The company pays dividends, offers rights, splits its stock, and calls its holders to vote at meetings. Each of these is a **securities event**, and communicating them down the chain from issuer to investor, then collecting the investors' choices back up, is what ISO 20022's `seev` business area is for. It is a large area, seventy-three messages, because it spans several distinct processes: corporate actions, general meetings and proxy voting, shareholder identification, market claims, and buyer protection. This article maps those sub-domains and follows the corporate-action lifecycle that anchors the area.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What seev covers

A securities event is anything that happens to an issued security during its life and affects its holders. `seev` carries these events across the **custody chain**: from the issuer and its agent, through the central securities depository (CSD), to custodians, and finally to the investors who hold the securities in their accounts. Because the investor is often several intermediaries away from the issuer, the event has to be announced downward and the investor's response gathered upward, at each link.

![The seev sub-domains and the custody chain]({{site.url_complet}}/assets/article/finance/seev-domains-concept.png)

The area splits into several processes that share this chain.

| Sub-domain | Messages | Purpose |
|-----------|----------|---------|
| General meetings and proxy voting | `seev.001` to `seev.008` | Notify meetings, gather votes, disseminate results |
| Agent corporate actions | `seev.009` to `seev.030` | Set up and run a corporate action between issuer agent and CSD |
| Corporate action distribution | `seev.031` to `seev.044` | Announce and process corporate actions to account holders |
| Shareholder identification | `seev.045` to `seev.049` | Disclose shareholder identity up the chain (SRD II) |
| Market claims | `seev.050` to `seev.053` | Compensate entitlements on in-flight trades |
| Buyer protection | `seev.060` to `seev.067` | Let a buyer instruct elections before settlement |

## Corporate actions

Corporate actions are the largest and most-used part of `seev`, the messages between an account servicer (a CSD or custodian) and the account holders it serves. Events come in three kinds, and the distinction drives the flow.

- **Mandatory** events happen automatically, such as a cash dividend or a stock split; the holder receives the outcome without doing anything.
- **Mandatory with choice** events require the holder to pick from options, with a default if it does not.
- **Voluntary** events, such as a tender offer or exercising rights, happen only if the holder elects to take part.

The flagship announcement is the **`seev.031` CorporateActionNotification**, which carries the event: a notification-general-information block, a corporate-action-general-information block giving the event type and its key dates, and the account details of the holder it concerns. Everything else in the corporate-action flow follows from that announcement.

![Corporate action lifecycle expressed with seev messages]({{site.url_complet}}/assets/article/finance/seev-corporate-action-workflow.png)

The lifecycle runs as follows. The servicer announces the event with a `seev.031` **Notification** and reports its processing state with a `seev.032` **EventProcessingStatusAdvice**. For an elective event, the holder responds with a `seev.033` **CorporateActionInstruction** carrying its election, and the servicer confirms receipt with a `seev.034` **InstructionStatusAdvice**. As payment approaches, a `seev.035` **MovementPreliminaryAdvice** tells the holder what it is due to receive, and on the payment date a `seev.036` **MovementConfirmation** confirms the securities or cash actually credited. If a booked movement must be undone, a `seev.037` **MovementReversalAdvice** reverses it, and free-text detail that does not fit the structured fields travels in a `seev.038` **CorporateActionNarrative**. Cancellations of an event or of an instruction are handled by `seev.039` and `seev.040`.

## General meetings and proxy voting

The first eight messages handle the shareholder's other main right: voting. A `seev.001` **MeetingNotification** announces a general meeting and its agenda, a `seev.003` **MeetingEntitlementNotification** tells a holder how many votes it may cast, and the holder instructs its votes with a `seev.004` **MeetingInstruction**. The servicer reports progress with a `seev.006` **MeetingInstructionStatus**, confirms the votes were lodged with a `seev.007` **MeetingVoteExecutionConfirmation**, and, after the meeting, circulates the outcome with a `seev.008` **MeetingResultDissemination**. This is the proxy-voting chain that lets an investor several custodians removed from the issuer still vote its shares.

## The other sub-domains

Three further processes round out the area.

- **Shareholder identification disclosure** (`seev.045` to `seev.049`) implements the transparency an issuer is entitled to under rules such as the EU Shareholder Rights Directive II: a `seev.045` disclosure request travels down the chain and `seev.047` responses return the identities of the underlying holders.
- **Market claims** (`seev.050` to `seev.053`) handle entitlements on trades that were in flight over a corporate action's record date. A `seev.050` **MarketClaimCreation** raises a claim so the party that should have received a dividend or other benefit is compensated, even though the trade had not yet settled.
- **Buyer protection** (`seev.060` to `seev.067`) lets the buyer of a security involved in an elective event give its election before the trade settles, through a `seev.060` **BuyerProtectionInstruction**, so it does not lose the right to choose because settlement is late.

## Conclusion

The `seev` business area carries the events in the life of a security across the custody chain. Its seventy-three messages cover corporate actions, from the `seev.031` notification through elections to the movement confirmation that pays them, general meetings and the proxy-voting chain that lets distant investors vote, shareholder identification for issuer transparency, market claims that compensate entitlements on unsettled trades, and buyer protection for elective events in flight. What ties them together is direction: an event is announced downward from issuer to investor, and the investor's choice, an election or a vote, is gathered back upward. Read next to the settlement area `sese` that moves the resulting securities and cash, `seev` is how a security's corporate life reaches the people who own it.

![Mindmap summarising the ISO 20022 seev securities events area]({{site.url_complet}}/assets/article/finance/iso20022-securities-events-seev.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **seev** | The ISO 20022 securities events business area, covering corporate actions, meetings, shareholder identification, market claims, and buyer protection across seventy-three messages. |
| **Corporate action** | An event affecting a security's holders, such as a dividend, split, rights issue, or tender offer. |
| **Mandatory event** | A corporate action that happens automatically, with no choice required from the holder. |
| **Voluntary event** | A corporate action that occurs only if the holder elects to take part. |
| **Corporate action notification (`seev.031`)** | The announcement of a corporate action, carrying the event type, key dates, and affected account. |
| **Corporate action instruction (`seev.033`)** | The holder's election in response to an elective event. |
| **Movement confirmation (`seev.036`)** | The message confirming the securities or cash actually credited on the payment date. |
| **Proxy voting** | The process by which an investor casts votes at a general meeting through the custody chain, using the `seev.001` to `seev.008` messages. |
| **Market claim** | A compensation for an entitlement on a trade that was unsettled over a corporate action's record date, raised by `seev.050`. |
| **Buyer protection** | The mechanism (`seev.060`) letting a buyer instruct its election on an elective event before the trade settles. |

## Frequently Asked Questions

**Q: What are the three kinds of corporate action, and how do they differ?**

Mandatory, mandatory with choice, and voluntary. A mandatory event, such as a cash dividend or a stock split, happens automatically and the holder simply receives the outcome. A mandatory-with-choice event requires the holder to pick from options but applies a default if it does not respond. A voluntary event, such as a tender offer or the exercise of rights, happens only if the holder actively elects to take part. The distinction matters because elective events need the holder to send a `seev.033` instruction, while a purely mandatory event needs no response.

**Q: Why does a securities event have to travel through a chain of intermediaries?**

Because the investor usually does not hold its securities directly with the issuer. Its holding sits with a custodian, which holds with another custodian or a CSD, which connects to the issuer's agent. When an event occurs, the announcement has to pass down this chain from the issuer to the investor, and the investor's response (an election or a vote) has to pass back up. `seev` provides messages for each link, which is why the corporate-action distribution and agent-corporate-action sub-domains both exist: they carry the same event at different points in the chain.

**Q: What is the corporate-action lifecycle in seev messages?**

It begins with a `seev.031` CorporateActionNotification announcing the event and a `seev.032` status advice on its processing. For an elective event, the holder sends a `seev.033` instruction with its election and receives a `seev.034` status advice. Before payment, a `seev.035` movement preliminary advice states what the holder is due, and on the payment date a `seev.036` movement confirmation records what was actually credited. A `seev.037` reversal advice can undo a booked movement, and cancellations are handled by `seev.039` and `seev.040`. The arc runs from announcement, through election where needed, to the confirmed payment.

**Q: What problem do market claims solve?**

They solve who gets an entitlement when a trade is unsettled over a corporate action's record date. If you buy shares just before a dividend record date but the trade has not settled by then, the dividend is paid to the seller who is still the holder of record, even though you are economically entitled to it. A market claim corrects this: a `seev.050` MarketClaimCreation raises a claim so the benefit is passed to the party that should have received it. Buyer protection (`seev.060`) addresses a related timing problem for elective events, letting a buyer instruct its election before its trade settles.

**Q: How does shareholder identification in seev relate to regulation?**

The shareholder-identification messages (`seev.045` to `seev.049`) implement an issuer's right to know who its shareholders are, a right strengthened in the EU by the Shareholder Rights Directive II. Because holdings are layered through intermediaries, an issuer cannot see the underlying investors directly. A `seev.045` disclosure request travels down the custody chain and `seev.047` responses return the identities back up, so the issuer can assemble a picture of its beneficial owners. It is an example of regulation driving a dedicated sub-domain into an ISO 20022 business area.

**Q: How does seev connect to sese?**

They handle different halves of a corporate action's effect. `seev` announces the event and gathers the holder's choice; `sese` moves the securities and cash that result. When a `seev.036` movement confirmation reports that a holder has been credited with new shares or cash, the underlying movement is a settlement handled in the `sese` area. In short, `seev` decides what should happen to a holding because of an event, and `sese` performs the resulting transfer.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 securities messages](https://www.iso20022.org/securities)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [ESMA — Shareholder Rights Directive II](https://www.esma.europa.eu/)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [Claude Code](https://claude.com/product/claude-code)
