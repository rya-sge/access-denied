---
layout: post
title: "ISO 20022 for Collateral Management — The colr Message Set"
date:   2026-07-17
lang: en
locale: en-GB
categories: network programmation ISO20022
tags: iso20022 swift collateral margin csa triparty
description: How ISO 20022 models collateral management through the colr business area, from margin call and collateral proposal to substitution, interest, disputes, and triparty processing between two counterparties and their custodian.
image: /assets/article/finance/iso20022-collateral-management-colr.png
isMath: true
---



Collateral is what makes modern derivatives trading safe to do at scale. When two firms hold a portfolio of uncleared swaps against each other, the one that is out of the money owes the other its mark-to-market value, and collateral is the buffer posted against that exposure so a default does not become a loss. ISO 20022 gives this daily exchange a structured vocabulary in its `colr` business area. This article walks through the `colr` message set (`colr.001` to `colr.024`, plus one `reda` message) using the schemas shipped in the collateral management package, covering the margin call cycle, collateral delivery, substitution, interest, disputes, and the triparty variant.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why collateral management needs a message standard

Two firms trading over-the-counter derivatives sign a legal agreement, typically a **Credit Support Annex (CSA)** to an ISDA Master Agreement, that sets out how they will collateralise their exposure to each other. Every business day each side revalues the shared portfolio, compares the resulting exposure to the collateral already held, and one side calls the other for more (or returns a surplus). The assets that move are cash or high-quality securities.

Done manually this is slow and error-prone, and it involves several distinct steps: valuing the exposure, issuing the call, agreeing the amount, choosing which specific assets to deliver, settling them, and later swapping or returning them. Since the 2008 crisis, regulation has pushed almost all of it onto a mandatory, timetabled footing. The **[BCBS-IOSCO margin requirements for non-centrally cleared derivatives](https://www.bis.org/bcbs/publ/d499.htm)**, implemented in the EU through EMIR and in the US under Dodd-Frank, phased in obligatory exchange of variation and initial margin between 2016 and 2022. A mandatory, high-volume, time-critical process is exactly the kind of thing that needs a machine-readable standard, and `colr` is ISO 20022's answer.

### Two kinds of margin

Two distinct exposures are collateralised, and the distinction runs through the whole message set.

- **Variation margin (VM)** covers the *current* mark-to-market exposure. As the portfolio's value moves each day, VM flows back and forth to keep the net exposure close to zero.
- **Initial margin (IM)** covers *potential future* exposure, the extra loss that could accrue between a counterparty's default and the close-out of the positions. IM is posted up front, held gross, and under the uncleared margin rules it must be **segregated** so it cannot be reused. In the `colr` schemas this appears as the `SgrtdIndpdntAmt` (segregated independent amount) element.

### The arithmetic of a margin call

The amount called is not simply the raw exposure. A CSA defines a **threshold** (an amount of exposure a party is willing to leave unsecured) and a **minimum transfer amount (MTA)** (a floor below which no call is made, to avoid moving trivial sums). Posted securities are valued after a **haircut**, a percentage discount that protects the taker against a fall in the collateral's own price. The delivery amount is therefore

$$
\begin{aligned}
\text{Call} = \max\!\big(0,\; (E - T) - C_{\text{adj}}\big), \qquad C_{\text{adj}} = \sum_k V_k \,(1 - h_k)
\end{aligned}
$$

where $$E$$ is the exposure, $$T$$ the threshold, $$V_k$$ the market value of each posted asset $$k$$, and $$h_k$$ its haircut. The call is only issued when the result is at least the MTA. These are the quantities the `colr` messages carry and that the two sides must agree on.

## The colr message catalogue

The collateral management package defines twenty-two `colr` messages and one `reda` message. They split cleanly into a **bilateral** group, where the two counterparties talk to each other directly, and a **triparty** group, where a custodian sits in the middle. The bilateral group follows the lifecycle of a margin call:

| Identifier | Message | Role |
|------------|---------|------|
| `colr.001` | CollateralValueQuery | Ask for the value of collateral held |
| `colr.002` | CollateralValueReport | Report that value |
| `colr.003` | MarginCallRequest | Issue a margin call for VM and/or IM |
| `colr.004` | MarginCallResponse | Agree, partially agree, or reject the call |
| `colr.009` | MarginCallDisputeNotification | Notify that the called amount is disputed |
| `colr.007` | CollateralProposal | Propose the specific assets to be delivered |
| `colr.008` | CollateralProposalResponse | Accept or reject the proposed assets |
| `colr.010` | CollateralSubstitutionRequest | Ask to swap posted collateral for other assets |
| `colr.011` | CollateralSubstitutionResponse | Answer the substitution request |
| `colr.012` | CollateralSubstitutionConfirmation | Confirm the completed substitution |
| `colr.013` | InterestPaymentRequest | Request interest owed on cash collateral |
| `colr.014` | InterestPaymentResponse | Respond to the interest request |
| `colr.015` | InterestPaymentStatement | Statement of interest amounts |
| `colr.016` | CollateralAndExposureReport | Full statement of exposure and collateral held |
| `colr.005` | CollateralManagementCancellationRequest | Cancel a previously sent instruction |
| `colr.006` | CollateralManagementCancellationStatus | Report the status of a cancellation |

The triparty group supports the model where a triparty agent holds and administers the collateral for both sides:

| Identifier | Message | Role |
|------------|---------|------|
| `colr.019` | TripartyCollateralTransactionInstruction | Instruct the agent to set up or adjust a triparty collateral transaction |
| `colr.020` | TripartyCollateralTransactionInstructionProcessingStatusAdvice | Report processing status of that instruction |
| `colr.021` | TripartyCollateralAllegementNotification | Allege a transaction against the counterparty |
| `colr.022` | TripartyCollateralAndExposureReport | Agent's report of collateral and exposure |
| `colr.023` | TripartyCollateralStatusAdvice | Advise the status of a triparty transaction |
| `colr.024` | TripartyCollateralAllegementNotificationCancellationAdvice | Cancel a previously sent allegement |
| `reda.074` | TripartyCollateralUnilateralRemovalRequest | Request unilateral removal of collateral |

### The shared anchor: the obligation

Almost every bilateral `colr` message opens with the same two elements: a transaction identifier (`TxId`) and an **obligation** block (`Oblgtn`). The obligation identifies the two parties, the exposure type being collateralised, and the collateral account, so a receiver can tie the message to the right agreement before reading its specifics. Because this block is shared, the messages of the cycle chain together naturally: a `MarginCallResponse` (`colr.004`) references the same obligation as the `MarginCallRequest` (`colr.003`) it answers, and so does the `CollateralProposal` (`colr.007`) that follows.

The `MarginCallRequest` illustrates the pattern. Below the transaction id and obligation it carries the margin call result (`MrgnCallRslt`), broken into the variation margin result (`VartnMrgnRslt`), the overall margin call amount (`MrgnCallAmt`), and the segregated independent amount (`SgrtdIndpdntAmt`) for initial margin. Rendered as illustrative XML, and omitting the `Document` wrapper and Business Application Header, a call for variation margin looks like this:

```xml
<MrgnCallReq>
  <TxId>MC-20260717-778</TxId>
  <Oblgtn>
    <PtyA><Id><AnyBIC>PARTAGB2LXXX</AnyBIC></Id></PtyA>
    <PtyB><Id><AnyBIC>PARTBFRPPXXX</AnyBIC></Id></PtyB>
    <CollAcctId><Id>CSA-A-B-001</Id></CollAcctId>
  </Oblgtn>
  <MrgnCallRslt>
    <MrgnCallAmt>
      <DlvrMrgnAmt Ccy="EUR">3400000.00</DlvrMrgnAmt>
    </MrgnCallAmt>
  </MrgnCallRslt>
</MrgnCallReq>
```

The receiving party validates this against `colr.003.001.05.xsd`, reads a request to deliver €3.4M of variation margin under CSA `CSA-A-B-001`, and replies with a `MarginCallResponse` that either agrees or opens a dispute.

## The margin call cycle, message by message

The diagram below sequences the bilateral messages across the life of a call.

![Sequence of colr messages across the daily margin call cycle]({{site.url_complet}}/assets/article/finance/colr-margin-call-workflow.png)

**Valuation.** Each morning a party marks the portfolio to market and compares its exposure with the collateral it already holds. Where it needs to check the other side's figure, `CollateralValueQuery` (`colr.001`) and `CollateralValueReport` (`colr.002`) let it ask for and receive a valuation. The standing picture of what is owed and held is carried in the `CollateralAndExposureReport` (`colr.016`), the collateral equivalent of an account statement.

**The call.** Having computed a shortfall above the MTA, the exposed party issues a `MarginCallRequest` (`colr.003`), stating the variation margin, the initial margin as a segregated independent amount, or both. The counterparty answers with a `MarginCallResponse` (`colr.004`), which can fully agree, agree in part, or reject. If the two sides disagree on the exposure or the valuation, the counterparty raises a `MarginCallDisputeNotification` (`colr.009`), which begins a reconciliation rather than a delivery. Disputes are a routine part of collateral operations, which is why the standard gives them a dedicated message rather than treating a rejection as the end of the conversation.

**Choosing and delivering assets.** Agreeing the amount is not the same as agreeing what to post. The delivering party sends a `CollateralProposal` (`colr.007`) naming the specific assets, cash in a currency or particular securities by ISIN, and the other side accepts or rejects them with a `CollateralProposalResponse` (`colr.008`). Once accepted, the assets themselves move through the settlement layer using `sese` messages; `colr` agrees the what and how much, `sese` performs the delivery.

**Substitution.** Collateral is not posted and forgotten. A party may need a specific security back, perhaps to deliver it elsewhere, and wants to swap it for other eligible assets. That is a three-step exchange: `CollateralSubstitutionRequest` (`colr.010`), `CollateralSubstitutionResponse` (`colr.011`), and once settled a `CollateralSubstitutionConfirmation` (`colr.012`).

**Interest.** Cash collateral earns interest for the party that posted it, since the taker is holding someone else's money. The `InterestPaymentRequest` (`colr.013`), `InterestPaymentResponse` (`colr.014`), and `InterestPaymentStatement` (`colr.015`) handle the calculation, agreement, and reporting of those amounts.

**Cancellation.** When an instruction was sent in error, `CollateralManagementCancellationRequest` (`colr.005`) withdraws it and `CollateralManagementCancellationStatus` (`colr.006`) reports whether the cancellation succeeded.

## Bilateral versus triparty

Everything above assumes the two counterparties administer collateral between themselves. In the **triparty** model a third party, a triparty agent that is usually a large custodian or a central securities depository, holds the collateral and runs the mechanics: selecting eligible assets from the giver's account, applying haircuts, valuing daily, and substituting automatically as needed. Both counterparties instruct the agent rather than each other, which removes a great deal of bilateral operational work.

![Component view of bilateral and triparty collateral flows]({{site.url_complet}}/assets/article/finance/colr-collateral-architecture-concept.png)

The `colr.019` to `colr.024` messages plus `reda.074` serve this model, each covering one part of the exchange with the agent:

- **Instruct.** A party sends a `TripartyCollateralTransactionInstruction` (`colr.019`) to open or adjust a collateral transaction, and the agent replies with a `TripartyCollateralTransactionInstructionProcessingStatusAdvice` (`colr.020`).
- **Allege.** Where one side has instructed and the agent needs the other to match it, a `TripartyCollateralAllegementNotification` (`colr.021`) alleges the transaction against that counterparty, and a `TripartyCollateralAllegementNotificationCancellationAdvice` (`colr.024`) withdraws the allegement if needed.
- **Report.** The agent reports holdings and exposure through the `TripartyCollateralAndExposureReport` (`colr.022`) and the state of individual transactions through the `TripartyCollateralStatusAdvice` (`colr.023`).
- **Remove.** Finally, `reda.074`, a `TripartyCollateralUnilateralRemovalRequest`, lets a party request removal of collateral on its own initiative.

The triparty set carries pagination (`Pgntn`) and general parameters (`GnlParams`) because an agent's reports can span many positions across many clients.

## Conclusion

The `colr` business area models the full lifecycle of collateral against derivatives and financing exposures. A bilateral core runs the daily margin cycle: value the exposure, call the margin, agree the amount or dispute it, propose and accept specific assets, then substitute and pay interest over the life of the trade. A triparty extension delegates the mechanics to a custodian through instruction, allegement, status, and reporting messages. Every message is an XML document validated against a schema and anchored by a shared obligation block, so the parties act on the same identified agreement and the same agreed figures. Read alongside the settlement (`sese`) and clearing (`secl`) areas that it hands off to, `colr` completes the ISO 20022 picture of what happens to a trade after it is struck.

![Mindmap summarising ISO 20022 collateral management with the colr message set]({{site.url_complet}}/assets/article/finance/iso20022-collateral-management-colr.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **colr** | The ISO 20022 business area for collateral management, comprising the bilateral messages `colr.001` to `colr.016` and the triparty messages `colr.019` to `colr.024`. |
| **CSA** | Credit Support Annex, the legal document to an ISDA Master Agreement that sets the terms under which two counterparties collateralise their mutual exposure. |
| **Variation margin (VM)** | Collateral covering the current mark-to-market exposure of a portfolio, exchanged as the portfolio's value moves each day. |
| **Initial margin (IM)** | Collateral covering potential future exposure between default and close-out, posted up front and, under the uncleared margin rules, held segregated. |
| **Segregated independent amount** | The `SgrtdIndpdntAmt` element carrying initial margin that must be held separately and cannot be reused by the taker. |
| **Threshold** | An amount of exposure a party agrees to leave unsecured; only exposure above it is collateralised. |
| **Minimum transfer amount (MTA)** | The floor below which no margin call is made, so that trivial amounts are not moved. |
| **Haircut** | A percentage discount applied to a posted security's market value, protecting the taker against a fall in the collateral's own price. |
| **Obligation (`Oblgtn`)** | The block opening most bilateral `colr` messages that identifies the two parties, the exposure type, and the collateral account. |
| **Triparty agent** | A custodian or CSD that holds collateral for both counterparties and runs selection, valuation, haircutting, and substitution on their behalf. |

## Frequently Asked Questions

**Q: What is the difference between variation margin and initial margin?**

Variation margin covers the current exposure: the mark-to-market value one party owes the other right now, exchanged daily so the net stays near zero as prices move. Initial margin covers potential future exposure, the additional loss that could build up in the gap between a counterparty defaulting and its positions being closed out. Initial margin is posted up front rather than in response to daily moves, and under the uncleared margin rules it must be segregated so the taker cannot reuse it. In the `colr` schemas initial margin surfaces as the segregated independent amount (`SgrtdIndpdntAmt`).

**Q: Why does agreeing a margin call take more than one message?**

Because a margin call involves several separable agreements. First the two sides must agree that a call is due and for how much, which is the `MarginCallRequest` (`colr.003`) and `MarginCallResponse` (`colr.004`). Then they must agree which specific assets will satisfy it, since a party has discretion over what eligible collateral to deliver, which is the `CollateralProposal` (`colr.007`) and `CollateralProposalResponse` (`colr.008`). And if either side disagrees on the exposure or valuation, that is a dispute (`colr.009`) rather than a delivery. Splitting the amount from the asset selection from the dispute lets each be handled and, if necessary, re-tried independently.

**Q: How is the amount of a margin call actually calculated?**

The call is the exposure minus the threshold minus the haircut-adjusted value of collateral already held, floored at zero, and only issued if the result reaches the minimum transfer amount. Formally, $$\text{Call} = \max(0, (E - T) - C_{\text{adj}})$$ with $$C_{\text{adj}} = \sum_k V_k (1 - h_k)$$. The threshold is unsecured exposure the parties tolerate, the MTA avoids moving trivial sums, and the haircut discounts each posted security against a fall in its own value. These parameters come from the CSA, and the `colr` messages carry the resulting figures for both sides to agree.

**Q: What does the obligation (`Oblgtn`) block do, and why is it in nearly every message?**

The obligation block identifies the two counterparties, the exposure being collateralised, and the collateral account. It is the shared key that ties every message in a cycle to the same underlying agreement. Because the `MarginCallRequest`, its response, the collateral proposal, and any substitution all carry the same obligation, a receiver can associate them without reconstructing the context each time. It is the same design idea as the shared building blocks in other ISO 20022 areas: put the common identifying data in one reusable component so the messages compose cleanly.

**Q: When would parties use the triparty messages instead of the bilateral ones?**

They use triparty when they want a custodian to run the collateral mechanics for them. In the bilateral model the two firms value exposure, select assets, apply haircuts, and arrange substitutions between themselves. In the triparty model a custodian or CSD holds the collateral and does that work automatically, so both firms instruct the agent (`colr.019`), receive processing status (`colr.020`), are alleged into transactions (`colr.021`), and get holdings and status reports (`colr.022`, `colr.023`). This scales far better when a firm faces many counterparties, which is why large dealers and their clients often prefer it.

**Q: How do the colr messages relate to secl and sese?**

They cover adjacent stages of the post-trade lifecycle. The clearing area (`secl`) is where a CCP tells a member what it owes and what margin it must post; `colr` is the general collateral language used to actually value exposure, call margin, and agree which assets move, whether against cleared or uncleared trades; and the settlement area (`sese`) performs the physical delivery of those assets. A margin call handled in `colr` therefore ends with a `sese` settlement instruction, and a CCP margin requirement reported in `secl` is covered by collateral whose movement `colr` and `sese` describe.

## References

- [ISO 20022 message definitions catalogue and downloads](https://www.iso20022.org/iso-20022-message-definitions?business-domain=1)
- [ISO 20022 securities and collateral messages](https://www.iso20022.org/securities)
- [SWIFT — ISO 20022 for financial institutions](https://www.swift.com/standards/iso-20022)
- [BCBS-IOSCO margin requirements for non-centrally cleared derivatives](https://www.bis.org/bcbs/publ/d499.htm)
- [ISDA — collateral and margin documentation](https://www.isda.org/category/collateral/)
- [Business Application Header (head.001) specification](https://www.iso20022.org/catalogue-messages/additional-content-messages/business-application-header)
- [Claude Code](https://claude.com/product/claude-code)
