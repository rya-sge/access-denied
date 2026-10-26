---
layout: post
title: "Hyperliquid HIP-1 to HIP-4 in Twelve Cards — The Definitions to Memorise"
date:   2026-10-26
lang: en
locale: en-GB
categories: blockchain defi
tags: hyperliquid defi perpetual trading flashcards glossary key-terms
series: hyperliquid
description: "Twelve flashcards for Hyperliquid HIP-1 to HIP-4: native tokens, Hyperliquidity, builder-deployed perp DEXs, slashing and outcome markets, with a revision table."
image: /assets/article/blockchain/hyperliquid/hyperliquid-hip-flashcards-mindmap.png
isMath: false
---

The four Hyperliquid Improvement Proposals add native spot tokens, automatic order-book liquidity, builder-deployed perpetual exchanges and fully collateralised outcome contracts to HyperCore. This deck compresses the site's article [The Hyperliquid Improvement Proposals - HIP-1 to HIP-4]({{site.url_complet}}/2026/09/02/hyperliquid-improvement-proposals-hip-1-to-hip-4/) for a reader who has gone through it once and wants the vocabulary to stay put.

Twelve cards, each with a plain-words definition, a precise one, one line to remember and a link to the page of the official Hyperliquid documentation that defines the term, plus a revision table at the end. The cards define; they do not derive the fee formulas or walk through the deployment flows, which the technical article covers. The wider protocol vocabulary is in [Understanding Hyperliquid - The Vocabulary, from Beginner to Advanced]({{site.url_complet}}/2026/09/09/hyperliquid-glossary/). Parameters such as stakes, auction floors and fee rules are those of the documentation in October 2026 and can change.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The twelve cards

### HyperCore

**In plain words:** HyperCore is the part of the Hyperliquid chain that runs the exchange itself, keeping the order books, the margin accounts and the balances inside the chain's own rules.

**Precisely:** Hyperliquid's native execution layer, secured by HyperBFT consensus, whose block-transition logic holds spot and perpetual order books, margining and balances; each HIP extends its state and actions rather than deploying smart contracts.

**Remember:** the exchange is the state machine

**Reference:** [Hyperliquid Docs — HyperCore overview, Execution](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/overview#execution)

### Add Liquidity Only (ALO)

**In plain words:** An add-liquidity-only order is an order that may only wait on the book for someone else to fill it; if it would trade at once, it is refused instead.

**Precisely:** The post-only option of [HyperCore](#hypercore) order books: the order rests as a maker order, and is rejected rather than executed if it would cross the book on arrival.

**Remember:** rest as maker or be rejected

**Reference:** [Hyperliquid Docs — Order types, Order options](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/order-types#order-options)

### HIP-1 token

**In plain words:** A HIP-1 token is a token created directly on Hyperliquid, with a fixed maximum supply, that trades against USDC on its own order book from launch.

**Precisely:** A capped-supply fungible token native to HyperCore, defined by `weiDecimals`, `szDecimals` and `maxSupply`, indexed by its token index because its name (at most six characters) carries no uniqueness constraint; it launches with a USDC spot book.

**Remember:** capped supply, native book, identify by index not ticker

**Reference:** [Hyperliquid Docs — HIP-1: Native token standard](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-1-native-token-standard)

### Deployment Dutch auction

**In plain words:** The deployment auction sets the price of launching a new token: the price starts high and falls steadily for 31 hours until someone pays it, never going below 500 HYPE.

**Precisely:** The gas for the first HIP-1 deployment step, `registerToken2`, set by a 31-hour Dutch auction in HYPE falling linearly from twice the last price (500 HYPE after a failed auction) to 500 HYPE; HIP-3 asset auctions reuse these parameters.

**Remember:** 31 hours, falling price, 500 HYPE floor, paid once

**Reference:** [Hyperliquid Docs — HIP-1, Gas cost for deployment](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-1-native-token-standard#gas-cost-for-deployment)

### Hyperliquidity (HIP-2)

**In plain words:** Hyperliquidity is a market maker run by the chain itself, which keeps a ladder of buy and sell orders on a new token's book and refreshes it with no operator.

**Precisely:** A HIP-2 strategy in [HyperCore](#hypercore) block-transition logic quoting a [HIP-1 token](#hip-1-token)'s USDC pair on price levels 0.3% apart with [ALO](#add-liquidity-only-alo) orders, refreshed at least three seconds apart; other makers can quote inside its spread.

**Remember:** 0.3% ladder, every 3 seconds, no operator, shared book

**Reference:** [Hyperliquid Docs — HIP-2: Hyperliquidity](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-2-hyperliquidity)

### Builder-deployed perp DEX (HIP-3)

**In plain words:** A builder-deployed perp DEX is a perpetual futures exchange that anyone with enough staked HYPE can launch on Hyperliquid, choosing its markets, its price sources and its risk limits.

**Precisely:** A HIP-3 perpetual DEX with its own margining, books and settings on [HyperCore](#hypercore), deployed under a 500k HYPE stake kept at least 183 days; the deployer defines markets and oracles, sets oracle prices and leverage limits, and may settle markets.

**Remember:** 500k HYPE stake, deployer runs oracle and risk

**Reference:** [Hyperliquid Docs — HIP-3: Builder-deployed perpetuals, Spec](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals#spec)

### Deployer slashing

**In plain words:** Slashing is the penalty validators can vote to take from a perp DEX deployer's stake when its inputs break or threaten the exchange, even by mistake; the stake taken is destroyed.

**Precisely:** A stake-weighted validator vote cutting a [HIP-3 deployer](#builder-deployed-perp-dex-hip-3)'s stake, even during the 7-day unstaking queue, for irregular inputs that jeopardise correctness, uptime or performance, attempted or not, malicious or careless; slashed HYPE is burned.

**Remember:** irregular input → validator vote → stake burned, not refunded

**Reference:** [Hyperliquid Docs — HIP-3, Slashing](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals#slashing)

### Outcome (HIP-4)

**In plain words:** An outcome is a fully paid-up contract with a Yes side and a No side whose payouts always add up to one unit of the quote token, so nobody can be liquidated.

**Precisely:** A HIP-4 contract whose Yes token settles to `settleFraction` quote tokens and No token to `1 - settleFraction`, with `settleFraction` in [0, 1]; the two books are merged, so buying Yes at p equals selling No at 1 − p.

**Remember:** Yes + No = 1 quote token, no leverage

**Reference:** [Hyperliquid Docs — HIP-4: Outcome markets, Mechanics](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-4-outcome-markets#mechanics)

### Split and merge

**In plain words:** Splitting turns quote tokens into equal numbers of Yes and No shares, and merging turns a matched pair back into quote tokens, so the backing never changes.

**Precisely:** `splitOutcome` converts X quote tokens into X Yes and X No shares of one [outcome](#outcome-hip-4); `mergeOutcome` converts X Yes plus X No shares back into X quote tokens, so every share pair stays backed by one quote token.

**Remember:** 1 quote token ⇄ 1 Yes + 1 No

**Reference:** [Hyperliquid Docs — Exchange endpoint, Split outcome](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#split-outcome)

### Question

**In plain words:** A question groups several outcomes of which exactly one will turn out Yes, so holding No on one outcome can be swapped for Yes on all the others.

**Precisely:** A collection of [outcomes](#outcome-hip-4) of which exactly one settles to Yes; `negateOutcome` converts X No shares of one outcome into X Yes shares of every other, and `mergeQuestion` redeems X Yes of every outcome for X quote tokens.

**Remember:** No on one = Yes on all the others

**Reference:** [Hyperliquid Docs — Exchange endpoint, Negate outcome](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#negate-outcome)

### Outcome template

**In plain words:** An outcome template is a market blueprint that validators approve in advance; a HIP-4 deployer creates markets only by filling in its blanks, such as a date or a target price.

**Precisely:** A validator-voted pattern fixing an [outcome](#outcome-hip-4)'s display text with `{keyword}` placeholders, side names, typed keyword hints and a `semanticRestriction`; staked deployers instantiate it without gas, on testnet only so far, and contradicting the restriction is slashable.

**Remember:** validators approve the pattern, deployers fill the blanks

**Reference:** [Hyperliquid Docs — HIP-4 deployer actions, Templates](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions#templates)

### Hyperliquid Improvement Proposal (HIP)

**In plain words:** A Hyperliquid Improvement Proposal is a feature built into the chain's exchange under a number; the first four add tokens, automatic liquidity, builder perp exchanges and outcome contracts.

**Precisely:** A primitive compiled into [HyperCore](#hypercore) execution and labelled by number, not a governance document: HIP-1 [tokens](#hip-1-token), HIP-2 [Hyperliquidity](#hyperliquidity-hip-2), HIP-3 [perp DEXs](#builder-deployed-perp-dex-hip-3) and HIP-4 [outcomes](#outcome-hip-4).

**Remember:** 1 token, 2 liquidity, 3 perps, 4 outcomes

**Reference:** [Hyperliquid Docs — Hyperliquid Improvement Proposals (HIPs)](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips)

## Flashcard table

| # | Term | In plain words | One thing to remember |
|:---:|------|----------------|------------------------|
| 1 | HyperCore | HyperCore is the part of the Hyperliquid chain that runs the exchange itself, keeping the order books, the margin accounts and the balances inside the chain's own rules. | the exchange is the state machine |
| 2 | Add Liquidity Only (ALO) | An add-liquidity-only order is an order that may only wait on the book for someone else to fill it; if it would trade at once, it is refused instead. | rest as maker or be rejected |
| 3 | HIP-1 token | A HIP-1 token is a token created directly on Hyperliquid, with a fixed maximum supply, that trades against USDC on its own order book from launch. | capped supply, native book, identify by index not ticker |
| 4 | Deployment Dutch auction | The deployment auction sets the price of launching a new token: the price starts high and falls steadily for 31 hours until someone pays it, never going below 500 HYPE. | 31 hours, falling price, 500 HYPE floor, paid once |
| 5 | Hyperliquidity (HIP-2) | Hyperliquidity is a market maker run by the chain itself, which keeps a ladder of buy and sell orders on a new token's book and refreshes it with no operator. | 0.3% ladder, every 3 seconds, no operator, shared book |
| 6 | Builder-deployed perp DEX (HIP-3) | A builder-deployed perp DEX is a perpetual futures exchange that anyone with enough staked HYPE can launch on Hyperliquid, choosing its markets, its price sources and its risk limits. | 500k HYPE stake, deployer runs oracle and risk |
| 7 | Deployer slashing | Slashing is the penalty validators can vote to take from a perp DEX deployer's stake when its inputs break or threaten the exchange, even by mistake; the stake taken is destroyed. | irregular input → validator vote → stake burned, not refunded |
| 8 | Outcome (HIP-4) | An outcome is a fully paid-up contract with a Yes side and a No side whose payouts always add up to one unit of the quote token, so nobody can be liquidated. | Yes + No = 1 quote token, no leverage |
| 9 | Split and merge | Splitting turns quote tokens into equal numbers of Yes and No shares, and merging turns a matched pair back into quote tokens, so the backing never changes. | 1 quote token ⇄ 1 Yes + 1 No |
| 10 | Question | A question groups several outcomes of which exactly one will turn out Yes, so holding No on one outcome can be swapped for Yes on all the others. | No on one = Yes on all the others |
| 11 | Outcome template | An outcome template is a market blueprint that validators approve in advance; a HIP-4 deployer creates markets only by filling in its blanks, such as a date or a target price. | validators approve the pattern, deployers fill the blanks |
| 12 | Hyperliquid Improvement Proposal (HIP) | A Hyperliquid Improvement Proposal is a feature built into the chain's exchange under a number; the first four add tokens, automatic liquidity, builder perp exchanges and outcome contracts. | 1 token, 2 liquidity, 3 perps, 4 outcomes |

## Conclusion

Three cards carry most of the deck. The [HyperCore](#hypercore) card explains why none of the four proposals needs a smart contract, the [builder-deployed perp DEX](#builder-deployed-perp-dex-hip-3) card and its [slashing](#deployer-slashing) companion explain how a permissionless venue is kept accountable, and the [outcome](#outcome-hip-4) card explains why HIP-4 needs no liquidation engine at all. The remaining cards are the operations and safeguards attached to each proposal.

The next step is the technical article, which covers the deployment sequences, the fee scales and the HIP-3 cross-margin and backstop rules that the cards leave out.

![Mindmap of the Hyperliquid HIP flashcards grouped into the execution layer, spot tokens and liquidity, builder perpetuals, outcome markets and the proposals themselves]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-hip-flashcards-mindmap.png)

## Frequently Asked Questions

**Q: Why should an integrator identify a HIP-1 token by its index rather than its ticker?**

The [HIP-1 token](#hip-1-token) card says the name carries no uniqueness constraint, so two tokens can display the same ticker. The token index assigned at deployment is unambiguous, and keying balances or prices on the ticker alone lets a look-alike token be mistaken for the real one.

**Q: What are the five deployment actions of a HIP-1 token, and which one is the auction attached to?**

`registerToken2`, `userGenesis`, `genesis`, `registerSpot` and `registerHyperliquidity`, sent in that order. The [deployment Dutch auction](#deployment-dutch-auction) prices only the first; once it is paid, the token is locked in and the remaining steps have no time limit.

**Q: Which card explains why Hyperliquidity needs no keeper, and how does it differ from a constant-product AMM?**

The [Hyperliquidity](#hyperliquidity-hip-2) card: its logic runs inside [HyperCore](#hypercore) block transitions under consensus, so no admin key or keeper transaction refreshes it. Unlike a constant-product pool, it posts a discrete ladder on a shared order book, and other makers can quote inside its 0.3% spread.

**Q: Why does Hyperliquidity use ALO orders?**

An [ALO](#add-liquidity-only-alo) order either rests as a maker order or is rejected; it never takes liquidity. The strategy is meant to supply liquidity, so an order that would cross the book is dropped rather than executed against another trader.

**Q: How are assets listed on a HIP-3 DEX?**

The first three assets of each [perp DEX](#builder-deployed-perp-dex-hip-3) need no auction. Additional assets go through a Dutch auction shared across all perp DEXs, with the same parameters as the [HIP-1 auction](#deployment-dutch-auction), or use one of the deployer's `7 + 0.2 × n` reserve deployments at the current auction price.

**Q: What does the Remember line of the deployer slashing card leave out?**

Three clauses. Slashing is technical: it does not distinguish malice from incompetence or a compromised key. An attempted irregular input is slashable even if it causes no harm, while a regular input that happens to trigger a bug is not. And the stake stays slashable during the 7-day unstaking queue.

**Q: What is HIP-3 growth mode, and which card does it attach to?**

A mode a [perp DEX](#builder-deployed-perp-dex-hip-3) deployer can switch on per asset to cut all-in fees, rebates and volume contributions by at least 90%. It is open only to markets entirely disjoint from validator-operated perps, caps the deployer fee share at 100%, and has a 30-day cooldown per asset.

**Q: Why can an outcome never become undercollateralised?**

The [outcome](#outcome-hip-4) card fixes the Yes and No payouts to sum to one quote token, and [split and merge](#split-and-merge) only ever create or destroy shares in matched pairs against exactly that amount. There is no borrowed exposure, so there is nothing to liquidate.

**Q: Which card is wrong if a question had two outcomes settle to Yes?**

The [question](#question) card, which requires exactly one outcome to settle Yes. `negateOutcome` relies on that rule: No on one outcome is worth Yes on all the others only because exactly one of them wins.

**Q: What is the difference between deploying under HIP-3 and under HIP-4?**

A [HIP-3](#builder-deployed-perp-dex-hip-3) deployer defines its own markets, oracles and risk settings and runs them under a bonded stake. A HIP-4 deployer, also staked, can only instantiate a validator-approved [outcome template](#outcome-template) by filling in its keywords, pays no gas, and for now can do so only on testnet.

## References

- [Hyperliquid Docs — Hyperliquid Improvement Proposals (HIPs)](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips)
- [Hyperliquid Docs — HIP-1: Native token standard](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-1-native-token-standard)
- [Hyperliquid Docs — HIP-2: Hyperliquidity](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-2-hyperliquidity)
- [Hyperliquid Docs — HIP-3: Builder-deployed perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals)
- [Hyperliquid Docs — HIP-4: Outcome markets](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-4-outcome-markets)
- [Hyperliquid Docs — Deploying HIP-1 and HIP-2 assets](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets)
- [Hyperliquid Docs — HIP-4 deployer actions](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions)
- [Hyperliquid Docs — Fees, Growth mode for HIP-3 perps](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees#growth-mode-for-hip-3-perps)

### Related articles

- [The Hyperliquid Improvement Proposals - HIP-1 to HIP-4]({{site.url_complet}}/2026/09/02/hyperliquid-improvement-proposals-hip-1-to-hip-4/)
- [Understanding Hyperliquid - The Vocabulary, from Beginner to Advanced]({{site.url_complet}}/2026/09/09/hyperliquid-glossary/)
- [The Hyperliquid Protocol - HyperCore, HyperEVM and Onchain Perpetual Mechanics]({{site.url_complet}}/2026/09/02/hyperliquid-protocol-architecture/)
