---
layout: post
title: "The Hyperliquid Oracle - How Validator Medians Become Mark Price, Funding and Liquidation"
date:   2026-09-02
lang: en
locale: en-GB
categories: blockchain defi oracle
tags: hyperliquid defi perpetual oracle derivatives trading
series: hyperliquid
description: Hyperliquid's oracle is a stake-weighted median of validator medians, published every three seconds. Which price drives funding, margin and liquidation.
image: /assets/article/blockchain/hyperliquid/hyperliquid-oracle.png
isMath: true
---

A liquidation on Hyperliquid is decided by a price that no trade on Hyperliquid has to print. The protocol maintains several prices, computed differently and updated on different schedules, and each drives a different part of the system. Funding settles on one; liquidation runs on another; the premium that feeds funding comes from a third.

Underneath all of them sits a single mechanism: every validator computes a weighted median of external spot venues roughly every three seconds and publishes it onchain, and the clearinghouse takes a stake-weighted median of those submissions. Two medians in series, one over venues and one over validators. Everything else in this article is either built on top of that number or is the special case where no external price exists to build it from.

This article takes that construction apart: how the oracle price is assembled and why the aggregation is built the way it is, how the mark price differs from it and why both are needed, what a single three-second tick sets in motion across margin and funding, what happens for assets with no external reference, and where the trust sits once the medians have done their work.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Four prices, four jobs

Before the mechanics, the map. Most surprises on the platform come from confusing two of these four.

| Price | Built from | Updated | Used for |
|---|---|---|---|
| **Oracle price** | Weighted median of external spot venues, then a stake-weighted median across validators | Roughly every 3 s | Funding: both the premium and the notional conversion in the payment |
| **Mark price** | Median of three indices, one of which is the oracle corrected for basis | Whenever validators publish, so roughly every 3 s | Margining, liquidation, TP/SL triggering, unrealised PnL |
| **Impact bid and ask** | The average execution price for a fixed notional on each side of Hyperliquid's own book | Sampled every 5 s | The funding premium |
| **Borrow oracle price** | The oracle price for the collateral asset | Roughly every 3 s | Portfolio margin: borrow capacity, the margin ratio, and borrow liquidation thresholds |

The division of labour is deliberate. Funding is supposed to pull the perpetual toward the underlying spot market, so it uses a price that ignores Hyperliquid's own book entirely. Margining is supposed to reflect a fair price for the contract itself, so it uses one that blends external spot, external perps and the local book. A single "the price" would have to be wrong for one of the two jobs.

## Building the oracle price

![Each validator takes a weighted median of eight spot venues every three seconds and publishes it, then the clearinghouse takes a stake-weighted median of those submissions]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-oracle-two-stage-median-concept.png)

### Stage one: inside each validator

Every validator is responsible for publishing a spot oracle price for each perp asset roughly every three seconds. It computes that number as the weighted median of spot mid prices from eight venues:

| Venue | Weight |
|---|:---:|
| Binance | 3 |
| OKX | 2 |
| Bybit | 2 |
| Kraken | 1 |
| KuCoin | 1 |
| Gate.io | 1 |
| MEXC | 1 |
| Hyperliquid spot | 1 |

The weights sum to twelve, so no single venue carries more than a quarter of the total. A **median** rather than a mean is what turns that bound into a guarantee: under a mean, one venue printing an absurd number drags the result in proportion to its weight, whereas a weighted median only moves if enough weight moves with it.

Membership is not fixed across assets, and it follows where an asset's liquidity sits:

- Perps on assets whose **primary spot liquidity is on Hyperliquid**, such as HYPE, exclude external sources until those venues have sufficient liquidity to be meaningful.
- Perps on assets whose **primary spot liquidity is elsewhere**, such as BTC, exclude Hyperliquid spot.

The reasoning is the same in both directions. Including a venue that barely trades the asset adds a manipulable input without adding information.

This is also where the quanto detail enters. Contracts are USDC-margined but the oracle price is usually denominated in **USDT**, with no conversion applied, which makes them technically quanto contracts whose USDT PnL is denominated in USDC. The exceptions are the assets whose most liquid spot source is Hyperliquid itself, currently PURR-USD and HYPE-USD, which are USDC-denominated throughout.

### Stage two: across the validator set

Each validator's number is its own opinion, published onchain. The price the clearinghouse uses is the **stake-weighted median** of all of them.

Stacking the two medians is what sets the cost of moving the price. To move stage one you need to move a weighted majority of eight venues. To move stage two you need to move a stake-weighted majority of validators. Neither a compromised exchange API nor a minority of dishonest validators changes the output, and the price becomes wrong only when a stake majority wants it wrong, which is the same assumption HyperBFT already makes for everything else.

That last point should be stated without softening. The oracle adds no trust assumption beyond the one the chain already has, and it also removes none. There is no fallback that survives a colluding stake majority, because a colluding stake majority is outside the security model by construction.

## Building the mark price

![Mark price is the median of three candidates: the oracle plus a 150 second basis EMA, the median of best bid, best ask and last trade, and five external perpetual mids]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-mark-price-concept.png)

The oracle price is a spot price. Perpetual contracts trade at a basis to spot, so margining a perp position against a spot price would systematically misprice it. The mark price is the fair-value estimate that solves this, and it is a median over three independently sourced candidates:

1. **The oracle price plus a 150-second exponential moving average** of the difference between Hyperliquid's mid price and the oracle. This is the external spot price corrected for the local basis.
2. **The median of Hyperliquid's best bid, best ask and last trade.** The local book, reduced to a single robust number rather than a single quote.
3. **The weighted median of Binance, OKX, Bybit, Gate.io and MEXC perpetual mid prices**, with weights 3, 2, 2, 1 and 1. External perp markets, which already contain the basis.

If exactly two of the three inputs exist, a 30-second EMA of the second candidate joins as a fourth, so the median is never computed over a single source.

The EMA itself is maintained as a ratio of two accumulators rather than a running average, which lets it handle irregular update intervals. For an update of value $$x$$ after elapsed time $$t$$:

$$
\begin{aligned}
n &\leftarrow n\,e^{-t/\tau} + x\,t, \qquad
d \leftarrow d\,e^{-t/\tau} + t, \qquad
\text{ema} = \frac{n}{d}
\end{aligned}
$$

with $$\tau = 2.5$$ minutes. Weighting each sample by its own $$t$$ is what keeps the estimate correct when samples arrive unevenly: a value that stood for thirty seconds counts thirty times as much as one that stood for one.

The median of three defends against something different from the median of eight venues. The venue median defends against one exchange printing a bad number. The candidate median defends against an entire **class** of price going wrong: a wick on Hyperliquid's own book moves candidate 2 and nothing else, an external spot dislocation moves candidate 1, and either way the median holds. Manipulating a liquidation price means moving two of three independently sourced indices at once.

Mark price is recomputed whenever validators publish new oracle prices, so both update on roughly the same three-second cadence.

## What one tick sets in motion

![One tick recomputes the oracle and mark price, then re-evaluates margin, trigger orders, unrealised PnL, the funding premium, collateral value and the order-entry bands]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-oracle-tick-workflow.png)

A three-second cadence sounds slow next to a matching engine that runs in microseconds, and for order matching it is irrelevant, because matching uses the book. What the tick drives is everything priced against the outside world:

- **Margin and liquidation.** Account equity is re-evaluated against the maintenance margin at the new mark price, and the solvency ladder starts where it fails.
- **Trigger orders.** Take-profit, stop-loss, stop-market and take-market orders all fire off the mark price, not the last trade.
- **Unrealised PnL**, on every open position.
- **The funding premium**, sampled from the impact bid and ask against the oracle price.
- **Portfolio-margin collateral**, revalued at the borrow oracle price, with borrow liquidations checked repeatedly on the same three-second interval.
- **Order-entry bands.** Orders priced too far from the oracle are rejected outright, and at an open-interest cap an order priced more aggressively than the oracle is rejected as well.

Those last two are easy to overlook and show up in the API as concrete error codes: `Oracle` ("order price too far from oracle"), `oracleRejected`, and `TooAggressiveAtOpenInterestCap`. The oracle is not only a valuation input; it also bounds what may be placed on the book.

## The oracle inside the funding rate

Funding is where the oracle price does its most visible work, and where the separation from the mark price matters most.

Writing $$P$$ for the average premium index and $$I$$ for the fixed interest component of 0.01% per eight hours:

$$
\begin{aligned}
F = P + \operatorname{clamp}(I - P,\ -0.0005,\ 0.0005)
\end{aligned}
$$

The premium is sampled every five seconds and averaged over the hour. It is built from the book, not from the mark price. With $$b$$ and $$a$$ the average execution prices for the impact notional on the bid and ask sides, and $$o$$ the oracle price:

$$
\begin{aligned}
P = \frac{\max(b - o,\ 0) - \max(o - a,\ 0)}{o}
\end{aligned}
$$

Two properties follow from that formula. The premium is **zero whenever the oracle sits between the impact bid and the impact ask**, so a perp trading inside its own spread relative to spot pays nothing. And the prices compared to the oracle are impact prices, meaning the average execution price for a fixed notional (20 000 USDC for BTC and ETH, 6 000 USDC elsewhere) rather than the top of book, so a single one-lot quote cannot manufacture a premium.

HIP-3 perps use a more responsive variant that gives deployers a wider range of behaviour through the funding multiplier and interest rate:

$$
\begin{aligned}
P = \frac{1}{2}\cdot\frac{b + a}{o} - 1
\end{aligned}
$$

Funding is paid hourly at one eighth of the computed eight-hour rate and capped at 4% per hour. The detail that most often surprises people is the conversion at settlement: the payment is `position_size × oracle_price × funding_rate`, using the **oracle** price, not the mark price the same position is margined against. A position can therefore be margined at one price and charged funding at another, and during a dislocation the gap is not small.

## When the standard construction is not enough

Two situations need a price the two-stage median cannot supply on its own: a contract whose underlying has not launched, and a contract being wound down. Each has its own mechanism.

### Hyperps

A *hyperp* is a Hyperliquid-only perpetual with no underlying spot or index price at all, typically for an asset that has not launched. The construction replaces the external oracle with the contract's own history: the oracle price becomes an eight-hour exponentially weighted moving average of the last day's minutely mark prices.

$$
\begin{aligned}
o(t) = \min\left(\ \frac{1 - e^{-1/480}}{1 - e^{-3}} \sum_{i=0}^{1439} m(t - i)\,e^{-i/480},\ \ 4\,m_0 \right)
\end{aligned}
$$

where $$m(t - i)$$ is the mark price $$i$$ minutes before $$t$$ and $$m_0$$ the initial mark price, which also pads the series when fewer than 480 samples exist. Samples are taken on the first block after each Unix minute, timestamped to the nearest exact minute.

Feeding a contract's own mark price back in as its oracle is obviously circular, so the design surrounds it with caps and dampening:

- The **mark price** is capped at three times the eight-hour mark EMA, and at 1.5 times the median external pre-launch perp price for hyperps that have one.
- The **oracle price** is capped, per the published formula, at four times the initial mark price, and the documentation additionally describes a restriction to at most four times the one-month average mark price.
- **Funding premium samples are taken at 1% of the usual clamped formula**, which is the line to internalise before trading one: the feedback loop is deliberately made slow.

Once the underlying lists for spot trading on Binance, OKX or Bybit, the contract converts to a vanilla perp and the ordinary oracle takes over. The mark price of hyperps also incorporates the weighted median of pre-launch perp prices from centralised venues, even when contract specifications differ, purely for stability during volatility.

### Delisting

When validators vote to delist a validator-operated perp, the contract does not simply stop. All positions settle to the **one-hour time-weighted spot oracle price** taken before the scheduled delisting vote time, open orders are cancelled, and no new orders are accepted afterwards. Using an hour-long TWAP rather than a spot reading is the standard defence against someone moving the settlement price in the final minutes, and it is the same mechanism many centralised venues use.

## HIP-3: the deployer becomes the oracle

Everything so far describes validator-operated perps. On a [HIP-3](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals) builder-deployed DEX, the oracle is whatever the deployer publishes, and this is the largest change in the trust model anywhere in the protocol.

The deployer owns the oracle definition and its operation through a set of dedicated actions: `setOracle` for the prices themselves, `setFundingMultipliers` and `setFundingInterestRates` for the funding behaviour built on top of them, and `setMarginTableIds` for the leverage the resulting prices margin against. A perp DEX may also nominate a separate `oracleUpdater` address distinct from the deployer, so price publication can be operationally separated from governance of the market.

What replaces the two-stage median is an economic bond and a review process:

- **500 000 staked HYPE**, held for at least 183 days after deployment and slashable by stake-weighted validator vote, including throughout the seven-day unstaking queue.
- **A standing review trigger.** Every time an asset's `externalPerpPx` moves more than 50% relative to the start-of-day price, validators conduct a review to determine whether the deployer should be slashed for manipulation.
- **An eligibility gate on cross margin.** Enabling cross margin on a HIP-3 asset is irreversible, and validators enforce that it is only enabled on assets with sufficient observable liquidity, a reliable external oracle source, and resilience to price manipulation. Assets where 50% daily moves are expected more than once a month are ineligible outright.

The documentation is candid that most price indices do not make sensible perp oracles, and that deployers should consider edge cases carefully because they are slashable for every market on their DEX. Two properties of that enforcement are easily missed: slashing does not distinguish a malicious deployer from an incompetent one or from one whose keys were stolen, since only the effect on the protocol is judged; and slashed stake is **burned rather than distributed to affected users**. A HIP-3 market's users are protected by the deployer's incentive not to be slashed, not by compensation after the fact.

## Reading the oracle from the HyperEVM

A contract on the HyperEVM has two ways to learn a price, and they are not interchangeable.

### The native path: read precompiles

HyperCore state is exposed to the EVM through read precompiles starting at `0x0000000000000000000000000000000000000800`. Oracle prices are among the values they serve, and the documented example queries a perp oracle price at `0x0000000000000000000000000000000000000807` with the asset index as the argument:

```bash
cast call 0x0000000000000000000000000000000000000807 \
  0x0000000000000000000000000000000000000000000000000000000000000003 \
  --rpc-url https://rpc.hyperliquid-testnet.xyz/evm
```

Three properties govern how a contract should use this:

- **The values match HyperCore state at the time the EVM block was constructed.** This is a guarantee, not a best effort, and it is the reason the precompile is not an ordinary oracle integration: there is no round trip, no staleness window to check, and no signature to verify.
- **Prices are integers.** Divide by $$10^{6 - \text{szDecimals}}$$ for a perp price and $$10^{8 - \text{szDecimals}}$$ for a spot price, using the base asset's `szDecimals`.
- **Invalid input consumes all the gas** passed into the precompile call frame and returns an error. Gas is otherwise `2000 + 65 * (input_len + output_len)`. A contract that calls one speculatively has to validate the asset index first and bound the gas it forwards.

Reading from the precompile is not the same as reading an external feed. It gives a contract the same number the clearinghouse is using to margin positions in the same block, which is exactly what a lending protocol pricing HyperCore collateral wants, and exactly the wrong thing if the contract needs a price for an asset HyperCore does not trade.

### The external path: third-party feeds

For everything else, the HyperEVM is an ordinary EVM chain and the usual oracle providers are deployed on it, including Chainlink, [Pyth]({{site.url_complet}}/2026/03/13/pyth-integration-security/), RedStone, Stork, DIA, Blocksense and Seda. Those carry the integration concerns any pull or push oracle carries, namely staleness checks, confidence intervals, sequencer or publisher liveness, and the update cadence the consuming protocol assumes.

The practical rule is straightforward. Price a HyperCore asset with the precompile, because nothing else can match the clearinghouse. Price anything else with a third-party feed, and treat it with the scepticism any external oracle deserves.

## Where the trust sits

Setting the failure modes against what bounds each of them shows where the guarantees end and the residual risk begins.

| Failure | What bounds it | Residual risk |
|---|---|---|
| One spot venue prints a manipulated price | Weighted median over eight venues, with a maximum single weight of 3 out of 12 | An attacker who moves several venues at once |
| Hyperliquid's own book is wicked | Mark price is a median over three indices, only one of which reads the book | A move large enough to drag two of the three |
| A minority of validators publish a false price | Stake-weighted median across the validator set | None below the stake majority threshold |
| A stake majority colludes | Nothing inside the oracle | This is the base HyperBFT assumption, not an oracle property |
| A HIP-3 deployer publishes a wrong price | 500 000 HYPE slashable by validator vote, plus a review on any 50% daily move | Slashed stake is burned, so users are not compensated |
| The asset has no external price | Hyperps: an EWMA of the contract's own marks, with caps and 1% premium sampling | Circularity remains, bounded rather than removed |
| The oracle stops updating | Mark and oracle both hold their last values until validators publish again | Liquidations and funding run on a stale price during the gap |

The pattern is that everything except the fourth row is bounded by construction, and the fourth row is not an oracle question at all. Median-of-medians buys defence in depth against venues and against individual validators; it buys nothing against the assumption the chain already rests on. That is not a criticism of the design so much as a statement of where a reader should direct their attention: for validator-operated perps, oracle risk reduces to stake distribution, and for HIP-3 perps it reduces to one deployer's competence and key hygiene.

## Conclusion

Hyperliquid's oracle is two medians in series. Each validator reduces eight external spot venues to one number by weighted median, and the clearinghouse reduces the validators' submissions to one number by stake-weighted median, roughly every three seconds. The mark price is then a third median, over the oracle corrected for basis, the local book, and external perp markets, so that margining reflects the contract rather than the spot asset.

Keeping the two separate lets each do its job: funding uses a price that ignores Hyperliquid entirely, so it pulls the contract toward spot, while margining uses one that includes the local book, so it prices the contract. The same tick that recomputes them also re-evaluates maintenance margin, fires trigger orders, restates unrealised PnL, samples the funding premium, revalues portfolio-margin collateral and re-applies the order-entry bands.

Where an external price does not exist, the construction degrades in a documented way rather than silently: hyperps feed the contract's own mark price back in with caps and a premium damped to 1%, delisting settles on a one-hour TWAP, and HIP-3 replaces the median entirely with a bonded deployer under standing validator review. Each of those is a different answer to the same question, and each moves the trust somewhere a reader can name.

![Mindmap of the Hyperliquid oracle covering the two-stage median, mark price, funding versus margin, hyperps, HIP-3 deployer oracles and reading prices from the HyperEVM]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-oracle.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Oracle price** | The stake-weighted median of validator submissions, each of which is a weighted median of external spot venue mid prices, published roughly every three seconds. |
| **Mark price** | The median of three candidate indices, used for margining, liquidation, TP/SL triggering and unrealised PnL, and never used for funding. |
| **Weighted median** | The aggregation used at both stages, chosen over a mean so that an extreme value moves the result only if enough weight moves with it. |
| **Impact price** | The average execution price for a fixed notional on one side of Hyperliquid's book, used in the funding premium instead of the top of book. |
| **Impact notional** | The size at which impact prices are measured: 20 000 USDC for BTC and ETH, 6 000 USDC for other assets. |
| **Premium index** | The book's deviation from the oracle, sampled every five seconds and averaged over the hour, and zero whenever the oracle lies between the impact bid and ask. |
| **Basis EMA** | The 150-second exponential moving average of the gap between Hyperliquid's mid price and the oracle, which converts the spot oracle into a perp fair value. |
| **Borrow oracle price** | The oracle price applied to portfolio-margin collateral, setting borrow capacity, the portfolio margin ratio and the borrow liquidation thresholds. |
| **Hyperp** | A Hyperliquid-only perpetual with no external underlying, whose oracle is an eight-hour EWMA of its own minutely mark prices under explicit caps. |
| **`externalPerpPx`** | The external perp reference on a HIP-3 asset whose 50% move from the start-of-day price triggers a validator review of the deployer. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| No single venue can set the oracle price. | A weighted median over eight venues, maximum single weight 3 of 12. | The aggregation becomes a mean, or one venue's weight exceeds half the total. |
| No minority of validators can set the oracle price. | The stake-weighted median taken across validator submissions. | The aggregation becomes a mean, or submissions are taken from a single source. |
| The mark price is never derived from one class of source. | A median over three independently sourced candidates, with a fourth added when only two exist. | Two of the three candidate sources become unavailable simultaneously. |
| Funding never reads Hyperliquid's mark price. | The premium is computed from impact prices against the oracle, and the payment converts on the oracle price. | The oracle is replaced by the mark price in either the premium or the settlement conversion. |
| A perp trading inside its own spread relative to spot pays no premium. | The `max(b - o, 0) - max(o - a, 0)` form, which is zero when the oracle lies between the impact prices. | The premium is computed from a mid price rather than from two clamped one-sided terms. |
| A one-lot quote cannot manufacture a funding premium. | The premium uses impact prices for a fixed notional, not the top of book. | The impact notional is reduced toward zero. |
| A hyperp's self-referential oracle cannot run away. | Mark capped at 3x the 8 h EMA, oracle capped at 4x the reference mark, premium samples at 1% of normal. | Any of the three caps is removed, at which point the feedback loop is unbounded. |
| A delisting cannot be settled at a manipulated instant. | Settlement on the one-hour time-weighted spot oracle price before the scheduled vote time. | Settlement uses a spot reading rather than a TWAP. |
| A precompile read matches the price the clearinghouse is using. | HyperEVM blocks are built inside L1 execution, and precompile values match Core state at construction. | The EVM is moved to a separate chain, or reads become asynchronous. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| Funding settles on the oracle price while margin runs on the mark price. | Project funding cost from the oracle and liquidation distance from the mark; never reuse one figure for both. |
| Trigger orders fire off the mark price, not the last trade. | Compute stop and take levels from the mark price feed, and expect them to fire without a trade printing at that level. |
| Oracle and mark update roughly every three seconds, not per block. | Do not treat a per-block price as available; sample on the publication cadence and handle unchanged values. |
| Orders are rejected for being too far from the oracle, and more aggressive than the oracle at an OI cap. | Handle `Oracle`, `oracleRejected` and `TooAggressiveAtOpenInterestCap` explicitly rather than as generic failures. |
| Precompile prices are integers with an asset-dependent scale. | Divide by `10^(6 - szDecimals)` for perps and `10^(8 - szDecimals)` for spot, reading `szDecimals` from `meta` rather than hard-coding it. |
| An invalid precompile input consumes all forwarded gas. | Validate the asset index before the call and cap the gas passed into the frame. |
| A precompile answers only for assets HyperCore trades. | Use a third-party HyperEVM feed for anything else, with the usual staleness and confidence checks. |
| HIP-3 oracle prices come from a deployer, optionally through a separate `oracleUpdater` address. | Read the `oracleUpdater` and deployer from the perp dex meta, and treat a HIP-3 price as a single-party feed rather than a network median. |
| Hyperps derive their oracle from their own mark prices under caps. | Do not model a hyperp's oracle as tracking any external asset, and account for funding premium samples at 1% of the normal formula. |
| Portfolio-margin borrow liquidations are checked repeatedly on the three-second interval. | Monitor the portfolio margin ratio continuously rather than assuming a single liquidation event per price update. |

## Frequently Asked Questions

**Q: Why does Hyperliquid maintain both an oracle price and a mark price instead of one price?**

Because the two are answering different questions.

The oracle price is meant to represent the **underlying spot market**, so it is computed entirely from external spot venues, and for assets whose liquidity is elsewhere it excludes Hyperliquid's own spot book. That independence is the property that makes it a valid funding input: funding exists to pull the perpetual toward spot, and an input that already contained the perpetual's price would be measuring itself.

The mark price is meant to represent the **fair value of the contract**, which trades at a basis to spot. It blends the oracle corrected for that basis, the local book, and external perp markets. That is the right input for margin and liquidation, and the wrong input for funding.

A single price would have to be either independent of Hyperliquid or representative of the contract, and it cannot be both.

**Q: Why a median at both stages rather than a weighted average?**

Because a mean is a linear function of its inputs and a median is not. Under a mean, a venue printing a price a thousand times too high moves the result in proportion to its weight, so a weight of 1 in 12 still shifts the output substantially. Under a weighted median, that venue simply sits at one end of the ordering and changes nothing until enough weight moves with it.

The same argument applies at stage two. A dishonest validator submitting an extreme number is at the tail of the stake-weighted ordering, and the output only moves when a stake-weighted majority moves.

Stacking the two means an attacker has to compromise a weighted majority of venues *and* be reflected across a stake-weighted majority of validators, rather than either one.

**Q: A position was liquidated but no trade printed near the liquidation price. How?**

Because liquidation runs on the mark price, and the mark price is a median over three candidates, only one of which reads Hyperliquid's book.

If external spot moved, candidate 1 moves. If external perp markets moved, candidate 3 moves. Two candidates moving is enough to carry the median, and neither of them requires a single trade on Hyperliquid at that level. Trigger orders behave the same way, which is why a stop can fire without a print at its price.

The corollary is that monitoring the local book alone is not sufficient to anticipate a liquidation. The documentation recommends computing the exact liquidation formula and tracking the mark price directly.

**Q: What does the premium formula do when the perp is trading close to spot?**

It returns exactly zero, by construction. The premium is

`max(impact_bid - oracle, 0) - max(oracle - impact_ask, 0)`

divided by the oracle price. When the oracle lies between the impact bid and the impact ask, both `max` terms are zero, so a contract trading inside its own spread relative to spot generates no premium at all.

This also explains why the premium uses impact prices rather than the best bid and ask. Impact prices are the average execution price for a fixed notional, 20 000 USDC for BTC and ETH and 6 000 USDC elsewhere, so a single small quote posted far from the oracle cannot manufacture a premium; moving the premium requires depth at the manipulated level.

**Q: Hyperps derive their oracle from their own mark prices. Why is that not circular in a dangerous way?**

It is circular, and the design does not pretend otherwise. What it does is bound the loop from three directions at once:

- **The oracle is a long average, not a reading.** It is an eight-hour EWMA over the last day's minutely mark prices, so a short manipulation contributes a small weight to a slow-moving number.
- **Hard caps on both prices.** The mark price is capped at three times the eight-hour mark EMA, and at 1.5 times the median external pre-launch perp price when one exists; the oracle is capped at four times the reference mark price.
- **Funding premium samples are taken at 1% of the usual formula**, so even a successfully moved premium translates into a hundredth of the normal funding response.

The result is a mechanism that is slow and bounded rather than non-circular, and it exists only until the underlying lists for spot trading on a major venue, at which point the contract converts to a vanilla perp with an ordinary oracle.

**Q: How does the oracle change when a market is deployed under HIP-3 rather than by validators?**

The two-stage median disappears. The deployer defines and operates the oracle through `setOracle`, optionally delegating publication to a separate `oracleUpdater` address, and also controls the funding multiplier and interest rate built on top of it. The price is a single party's output rather than a network aggregate.

What replaces the median is economic rather than statistical: 500 000 staked HYPE held for at least 183 days, slashable by stake-weighted validator vote, with a standing review triggered whenever the asset's `externalPerpPx` moves more than 50% from the start-of-day price, and an eligibility gate that only lets cross margin be enabled on assets with a reliable external oracle source.

The residual risk is that slashing is punitive rather than compensatory. It does not distinguish malice from incompetence from a key compromise, and slashed stake is burned rather than paid to affected users.

**Q: When should a HyperEVM contract read the precompile, and when should it use Chainlink or Pyth?**

Use the **precompile** when the contract needs the price HyperCore is using. Its values match Core state at the moment the EVM block was constructed, so a lending protocol liquidating against HyperCore collateral, or a vault marking a HyperCore position, gets the same number the clearinghouse used in the same block. There is no round trip, no staleness window and no signature to verify.

Use a **third-party feed** for anything HyperCore does not trade. Those are ordinary oracle integrations on an ordinary EVM chain and carry the usual concerns: staleness thresholds, confidence intervals, publisher liveness and update cadence.

Two constraints apply to the precompile path regardless: an invalid asset index consumes all the gas forwarded into the call frame, and prices come back as integers that must be scaled by `10^(6 - szDecimals)` for perps or `10^(8 - szDecimals)` for spot.

## References

### Hyperliquid documentation

- [Oracle](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/oracle) — the venue weights, the per-validator median and the stake-weighted aggregation
- [Robust price indices](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/robust-price-indices) — the three mark price candidates and the EMA update formula
- [Funding](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding) — the funding rate, the premium from impact prices, and the settlement conversion on the oracle price
- [Contract specifications](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications) — impact notional, quanto margining, and the USDC-denominated exceptions
- [Hyperps](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/hyperps) — the self-referential oracle, its caps and the 1% premium sampling
- [Delisting](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/delisting) — settlement on the one-hour time-weighted spot oracle price
- [Liquidations](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations) — why mark price rather than book price is used
- [Portfolio margin](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/portfolio-margin) — the borrow oracle price, borrow capacity and liquidation thresholds
- [Order book (HyperCore)](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/order-book) — the margin checks the oracle feeds

### Developer interfaces

- [Interacting with HyperCore](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/interacting-with-hypercore) — read precompiles, the oracle price example, price scaling and the gas semantics
- [Error responses](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/error-responses) — `Oracle` and `TooAggressiveAtOpenInterestCap`
- [Info endpoint: perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals) — asset contexts and the `oracleUpdater` field on a perp dex
- [HIP-3 deployer actions](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions) — `setOracle`, `setFundingMultipliers`, `setFundingInterestRates`
- [HIP-3: Builder-deployed perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals) — the staking requirement, the `externalPerpPx` review and the slashing guidelines
- [Tools for HyperEVM builders](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperevm/tools-for-hyperevm-builders) — the third-party oracle providers deployed on the HyperEVM

### Related articles

- [How to build a blockchain oracle]({{site.url_complet}}/2024/04/16/build-blockchain-oracle/)
- [Integrating Pyth Network Price Feeds — A Security-Focused Guide]({{site.url_complet}}/2026/03/13/pyth-integration-security/)
- [The Unified Risk Layer for DeFi - From Price Oracles to Protocol-Owned Risk Oracles]({{site.url_complet}}/2026/07/02/defi-unified-risk-layer-llama-guard/)
- [Traditional Futures vs. Perpetual Futures: A Technical Comparison]({{site.url_complet}}/2025/12/29/traditional-vs-perpetual-futures/)
