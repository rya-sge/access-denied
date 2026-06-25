---
layout: post
title: "Traditional Futures vs. Perpetual Futures: A Technical Comparison"
date:   2025-12-29
locale: en-GB
lang: en
last-update: 
categories: defi blockchain
tags: defi futures perpetual derivatives funding-rate trading
description: A technical comparison of traditional futures and crypto perpetual futures, covering no-arbitrage pricing, mark-to-market settlement, the funding rate mechanism, and liquidation.
isMath: true
image: /assets/article/blockchain/defi/perpetual-futures/2025-12-29-traditional-vs-perpetual-futures-mindmap.png
---

Futures contracts let traders speculate on, or hedge against, the future price of an underlying asset. **Traditional futures** have a long history in commodities, equities, and foreign-exchange markets. The growth of cryptocurrency derivatives popularised a newer instrument: the **perpetual future** (also called a **perpetual swap**). The two share a similar payoff profile, but they differ in settlement, price anchoring, and funding dynamics.

This article compares the two instruments. The pricing theory for the traditional side follows the no-arbitrage treatment in the [University of Oslo STK-MAT3700 lecture notes on forward and future contracts](https://www.uio.no/studier/emner/matnat/math/STK-MAT3700/h22/lecture-notes/lecture6__7_forvard_future_contract_option.pdf); the perpetual side draws on the mechanics introduced by crypto derivatives venues.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Foundations: No-Arbitrage and Positions

All pricing results below rest on a single assumption, the **principle of no arbitrage**. An **arbitrage** is a guaranteed risk-free profit obtained from a trade or a series of trades. A market is **arbitrage-free** when no such opportunity exists, and an **arbitrage-free price** for a security is one that admits no arbitrage. The forward price derived later is exactly the price that keeps the market arbitrage-free.

Two pieces of terminology recur throughout:

- A **long position** holds (or will hold) a positive amount of an asset and gains when its price rises.
- A **short position** holds (or will hold) a negative amount and gains when the price falls. Taking a short position on an asset you do not own is done through **short selling**: borrowing the asset, selling it, and returning it later.

Let $$S(t)$$ denote the **spot price** of the underlying at time $$t$$, and let $$r$$ be the constant risk-free interest rate under continuous compounding.

## Contract Structure

### Forward contract

A **forward contract** is a private, over-the-counter agreement between two parties to buy or sell an asset on a fixed future date, the **delivery time** $$T$$, at a price agreed in advance, the **forward price** $$F(t,T)$$. The buyer takes the long position, the seller the short position, and both are obliged to settle.

No money changes hands at inception. If the contract is entered at time $$t$$, the payoffs at delivery are:

$$
\begin{aligned}
\text{long:}\quad & S(T) - F(t,T) \\
\text{short:}\quad & F(t,T) - S(T)
\end{aligned}
$$

Forwards are customisable and are not settled until maturity. Because settlement happens only once, at $$T$$, each party carries **counterparty risk**: the party that ends up losing money may default before delivery.

The payoff at delivery is linear in the terminal spot price:

```
 payoff
   ^                       long: S(T) - F
   |                    /
   |                  /
 0 +----------------*----------------> S(T)
   |              / F(t,T)
   |            /          short: F - S(T)
   |          /  (mirror image, negated)
```

### Traditional futures contract

A **futures contract** is a standardised, exchange-traded agreement to buy or sell an underlying asset at an agreed price for delivery at a specified future date. Futures are designed to remove the default risk inherent in forwards. Three properties distinguish them:

- They are **standardised** and traded on an exchange (CME, ICE, and similar venues), which makes them liquid.
- They are guaranteed by a central **clearing house**, so neither party is exposed to the other's default.
- They are **marked to market daily**, meaning gains and losses are settled every day through a margin account rather than accumulated until maturity.

Each contract has a **defined expiration date** (monthly or quarterly, for instance) and a **settlement method**, either *physical delivery* of the underlying or *cash settlement* against the price difference.

### Perpetual futures contract

A **perpetual futures contract** has **no expiration date**. A position can be held indefinitely as long as margin requirements are met. There is no terminal delivery date at which the contract price converges to spot, so a different anchoring mechanism is required: a **funding rate** that periodically transfers payments between longs and shorts to keep the contract price close to the spot price.

This structure originated in cryptocurrency markets, notably with the [BitMEX XBTUSD perpetual swap](https://www.bitmex.com/blog/announcing-the-launch-of-the-perpetual-xbtusd-leveraged-swap) launched in 2016, to provide continuous leveraged exposure without periodic contract rollovers. Writing $$P_t$$ for the perpetual price and $$S_t$$ for the spot price, alignment between the two is maintained through funding payments rather than through convergence at maturity.

## Pricing and Price Anchoring

### Traditional futures: the no-arbitrage forward price

The natural first guess for a forward price is to discount the expected payoff. Setting the present value of a long forward to zero gives

$$
\begin{aligned}
0 = V(0) = e^{-rT}\,\mathbb{E}\!\left[\,S(T) - F(0,T)\,\right],
\end{aligned}
$$

which yields $$F(0,T) = \mathbb{E}[S(T)]$$. This is unsatisfactory, because it depends on the assumed distribution of $$S(T)$$ and merely shifts the problem to agreeing on that distribution.

The no-arbitrage argument removes the dependence on any distribution. Consider a **buy-and-hold strategy**: borrow $$S(0)$$ at time zero, buy the asset, and hold it until $$T$$. At delivery the loan has grown to $$S(0)e^{rT}$$, which is the only amount that can be charged for the asset at $$T$$ without creating an arbitrage. This gives the forward price (Theorem 6.1 of the lecture notes):

$$
\begin{aligned}
F(0,T) = S(0)\,e^{rT}, \qquad F(t,T) = S(t)\,e^{r(T-t)}.
\end{aligned}
$$

The price obtained this way does not depend on the distribution of $$S(T)$$. The formula holds as long as the underlying generates no income (such as dividends) and incurs no holding cost (such as storage or insurance). Once those are present, the relation generalises to the **cost-of-carry model**:

$$
\begin{aligned}
F_t = S_t \cdot e^{(r + c - y)(T - t)},
\end{aligned}
$$

where $$c$$ is the storage or carrying cost and $$y$$ is the convenience yield. The forward and futures price sits above spot whenever $$r + c - y > 0$$.

The difference $$F(t,T) - S(t)$$ is called the **basis**. As $$t \to T$$, the exponent $$r(T-t) \to 0$$, so $$F(t,T) \to S(t)$$ and the basis converges to zero. This **time-based convergence** is what ties a traditional futures price to spot:

```
Traditional futures                       Perpetual futures
 price                                      price
  |   F_t                                    |  P_t ~~~~~~~~~~~~~  (funding-tethered)
  |     \  basis = F_t - S_t                 | ~~~~~ S_t (spot)
  |      \__                                 |
  |   S_t   \___                             |  no expiry; funding keeps
  |              \  (basis -> 0)             |  P_t close to S_t over time
  +---------------*------> t                 +-----------------------> t
                  T (expiry)                  (held indefinitely)
```

A subtle point distinguishes a forward from a future even on the pricing side. Because a future is marked to market daily, its intermediate cash flows are random. When the interest rate $$r$$ is constant, however, this randomness does not affect the initial price, and the futures price equals the forward price (Theorem 6.3):

$$
\begin{aligned}
f(0,T) = F(0,T), \qquad f(t,T) = S(t)\,e^{r(T-t)}.
\end{aligned}
$$

Under a constant rate the futures price is random only through its dependence on $$S(t)$$.

### Perpetual futures: the funding rate mechanism

A perpetual contract has no maturity, so there is no $$T$$ at which the basis is forced to zero. Exchanges replace time-based convergence with a recurring payment between longs and shorts, the **funding rate** $$f$$, designed to keep $$P_t$$ near $$S_t$$.

The direction of the payment depends on the sign of the gap between the perpetual price and the spot (index) price:

- If the perpetual trades above spot ($$P_t > S_t$$), the funding rate is **positive** and longs pay shorts. Holding a long position becomes costly, which discourages buying and pushes $$P_t$$ down toward $$S_t$$.
- If the perpetual trades below spot ($$P_t < S_t$$), the funding rate is **negative** and shorts pay longs, pushing $$P_t$$ back up.

The payment exchanged each interval is proportional to position size:

$$
\begin{aligned}
\text{Funding payment} = \text{Position notional} \times f.
\end{aligned}
$$

```
                P_t  (perpetual price)         S_t (spot/index)
                 |                               |
   P_t > S_t :   | ====  funding f > 0  ====>    | longs PAY shorts
                 |                               |
   P_t < S_t :   | <====  funding f < 0  ====    | shorts PAY longs
                 |                               |
   funding settled every interval (commonly 8h);  payment = notional x f
   net effect: arbitrageurs are paid to close the (P_t - S_t) gap
```

The mechanism makes the basis expensive to hold rather than impossible to sustain. It tethers the perpetual to spot continuously instead of at a single terminal date.

## Settlement and Mark-to-Market

The settlement model is where the two instruments diverge most clearly in day-to-day mechanics.

For a **traditional future**, time is effectively discrete with steps of length $$\tau$$ (typically one day). At each step the holder of a long position receives the change in the futures price, $$f(n\tau, T) - f((n-1)\tau, T)$$, if it is positive, and pays it if it is negative. After each settlement the value of the position is reset to zero. At delivery the futures price equals spot, $$f(T,T) = S(T)$$.

```
 Day 0        Day 1            Day 2          ...        Day N = T
   |            |                |                          |
 entry      f(1,T)            f(2,T)                   f(T,T) = S(T)
   |            |                |                          |
   +-- settle f(n,T) - f(n-1,T) to margin each day ---------+
        long receives the daily gain (pays the daily loss);
        position value reset to 0 after every settlement
```

For a **perpetual future**, margining is continuous rather than daily. Unrealised profit and loss are updated on a near-real-time basis, often every few seconds, and the funding payment is exchanged at each funding interval. There is no terminal settlement against a delivery price; a position is closed only when the trader exits voluntarily or is liquidated.

### Closing a perpetual position

A position can be closed in three ways:

- **Voluntary closure.** The trader closes at any time, realising the accumulated profit or loss. Losses are deducted directly from the deposited collateral.
- **Forced closure (liquidation).** A position stays open only while the collateral covers the unrealised loss. If the price moves far enough against the trader that the loss approaches the value of the collateral, the platform forcibly closes the position. The collateral securing that position is consumed by the loss.
- **Auto-deleveraging (ADL).** In extreme conditions, when the insurance fund cannot absorb liquidation losses, the platform deleverages profitable or highly leveraged positions on the opposite side of the liquidated one, selected by an ADL ranking.

## Margining and Liquidation

Both instruments are margin-traded, but their risk processes differ in tempo.

- **Traditional futures.** Margins are settled daily through mark-to-market. Profits and losses are realised each day, and a margin call is issued if account equity falls below the maintenance requirement.
- **Perpetual futures.** Margining is continuous and coupled to funding payments. Liquidation is automated and immediate once the trader's equity falls below the liquidation threshold.

Combined with the high leverage that perpetual venues offer (often up to 100×), continuous margining makes perpetuals more sensitive to short-term volatility than daily-settled traditional futures.

### Auto-deleveraging in practice

[Bybit's Auto-Deleveraging system](https://www.bybit.com/en/help-center/article/Auto-Deleveraging-ADL) controls overall platform risk during liquidation events in extreme conditions where the insurance fund cannot cover the losses. It deleverages profitable or highly leveraged positions on the side opposite the liquidated position, ordered by an ADL ranking.

[Binance computes a similar liquidation priority ranking](https://www.binance.com/en/support/faq/detail/360033525471) from a position's profitability and effective leverage:

$$
\begin{aligned}
\text{PNL\%} &= \frac{\text{Unrealised Profit}}{\lvert \text{Position Notional} \rvert} \\[4pt]
\text{Effective Leverage} &= \frac{\lvert \text{Position Notional} \rvert}{\text{Wallet Balance} + \text{Unrealised Profit}}
\end{aligned}
$$

A position with positive PNL is ranked by $$\text{PNL\%} \times \text{Effective Leverage}$$, and one with negative PNL by $$\text{PNL\%} / \text{Effective Leverage}$$. The leverage-PNL quantile is the position's rank divided by the total user count, so the most profitable and most leveraged positions are deleveraged first.

## Market Behaviour and Use Cases

| Feature | **Traditional Futures** | **Perpetual Futures** |
| --- | --- | --- |
| **Participants** | Institutional traders, hedgers | Retail and professional crypto traders |
| **Trading horizon** | Defined, periodic | Continuous |
| **Primary function** | Hedging, portfolio diversification | Speculation, liquidity provision |
| **Rollover requirement** | Yes | No |
| **Price anchoring** | Time-based convergence (basis → 0) | Funding rate |
| **Settlement** | Daily mark-to-market, expiry at $$T$$ | Continuous, no expiry |
| **Funding cost** | None | Dynamic funding rate |

Traditional futures are favoured in regulated venues such as CME and ICE for risk management and hedging. Perpetuals, being non-expiring, offer continuous liquidity and convenience for speculative trading, but they introduce funding-cost volatility as an additional dimension of risk.

## Practical Example

Suppose Bitcoin trades at $60,000$ on the spot market.

- A **quarterly traditional future** might trade at $61,200$, a premium of roughly 2% (annualised) that reflects the cost of carry. As the quarterly expiry approaches, this premium decays and the futures price converges to spot.
- A **perpetual future** might oscillate between $59,950$ and $60,050$, staying close to spot because funding-rate arbitrage continuously corrects deviations.

If the perpetual premium persists above spot, the funding rate turns positive, say $$f = 0.01\%$$ every 8 hours, and longs pay shorts to restore balance. The longer the gap persists, the more it costs to hold the rich side.

## Historical Note: BitMEX XBTUSD (2016)

The perpetual swap was introduced commercially by [BitMEX with its XBTUSD product](https://www.bitmex.com/blog/announcing-the-launch-of-the-perpetual-xbtusd-leveraged-swap) in 2016. Its design set the template still used today:

1. XBTUSD is perpetual and never expires, so a position can be held for as long as the trader wants.
2. Longs and shorts exchanged a periodic funding payment derived from lending-market rates, in the manner of margin trading but with higher available leverage than competing venues at the time.
3. Longs profit when the price rises and shorts profit when it falls.

## Conclusion

Traditional futures and perpetual futures share the core properties of a derivative, namely leverage, margining, and directional exposure, but they differ in structural design and settlement.

- Traditional futures rely on time-based convergence: the basis decays to zero as the contract approaches its delivery date, and the no-arbitrage price $$F(0,T) = S(0)e^{rT}$$ ties the contract to spot.
- Perpetual futures rely on funding-based anchoring: a recurring payment between longs and shorts keeps the contract price near spot in the absence of any expiry.

The perpetual model provides continuous liquidity and avoids contract rollovers, which suits crypto markets, at the cost of funding-rate volatility and continuous liquidation risk. As perpetual contracts extend beyond digital assets, the distinction between time-based convergence and funding-based anchoring is the structural detail that traders and risk managers need to track.

![Traditional vs perpetual futures mindmap]({{site.url_complet}}/assets/article/blockchain/defi/perpetual-futures/2025-12-29-traditional-vs-perpetual-futures-mindmap.png)

```
@startmindmap
* Futures: Traditional vs Perpetual
** Foundations
*** No-arbitrage principle
*** Long / short positions
*** Spot price S(t)
** Forward contract
*** OTC, private agreement
*** Counterparty risk
*** Settled once at delivery T
*** F(0,T) = S(0)e^rT
** Traditional futures
*** Exchange-traded, standardized
*** Clearing house (no default risk)
*** Marked to market daily
*** Fixed expiry T
*** f(0,T) = F(0,T) if r constant
*** Basis -> 0 as t -> T
** Perpetual futures
*** No expiration date
*** Funding rate anchors P to S
**** P > S: longs pay shorts (f > 0)
**** P < S: shorts pay longs (f < 0)
*** Continuous margining
*** Origin: BitMEX XBTUSD (2016)
** Pricing
*** Cost of carry: F = S e^(r+c-y)(T-t)
*** Convergence vs funding tether
** Risk and liquidation
*** Daily mark-to-market (traditional)
*** Liquidation when equity < maintenance
*** Auto-deleveraging (ADL)
**** Bybit / Binance ranking
*** High leverage (up to 100x)
@endmindmap
```

## Frequently Asked Questions

**Q: What is the defining structural difference between a traditional future and a perpetual future?**

A traditional future has a fixed expiration date at which it is settled, by physical delivery or in cash, and its price converges to spot as that date approaches. A perpetual future has no expiration date; a position can be held indefinitely, and price alignment with spot is maintained by a recurring funding payment rather than by terminal convergence.

**Q: Why is the no-arbitrage forward price $$F(0,T) = S(0)e^{rT}$$ preferred over the expected-value price $$\mathbb{E}[S(T)]$$?**

The expected-value price depends on the assumed probability distribution of the terminal spot price, so two parties would first have to agree on that distribution. The no-arbitrage price is derived from a buy-and-hold strategy (borrow $$S(0)$$, buy the asset, repay $$S(0)e^{rT}$$ at $$T$$) and is the unique price that admits no risk-free profit. It does not depend on any distributional assumption, which makes it the price both parties can accept.

**Q: How does the funding rate keep a perpetual contract close to the spot price?**

When the perpetual trades above spot, the funding rate is positive and longs pay shorts, which makes holding a long position costly and discourages further buying, pushing the price down. When the perpetual trades below spot, the rate is negative and shorts pay longs, pushing the price up. The payment equals the position notional times the funding rate and is exchanged each interval (commonly every 8 hours), so persistent deviations become progressively expensive to hold and arbitrageurs are paid to close the gap.

**Q: What is "marking to market", and how does its tempo differ between the two instruments?**

Marking to market means settling the change in a position's value as a cash flow rather than letting it accumulate to maturity. A traditional future is marked to market daily: the holder of a long position receives the day's price increase or pays the day's decrease, and the position value is reset to zero after each settlement. A perpetual future is margined continuously, with unrealised profit and loss updated in near-real time and funding exchanged at each interval, so there is no single daily settlement point.

**Q: Why are perpetual futures considered more sensitive to short-term volatility than traditional futures?**

Two factors compound. First, margining is continuous and liquidation is automated and immediate once equity falls below the threshold, rather than waiting for a daily margin call. Second, perpetual venues commonly offer leverage up to 100×, so a small adverse price move can wipe out the collateral backing a position. Together these mean a brief volatility spike can trigger liquidations on a perpetual that a daily-settled traditional future would absorb.

**Q: Under what condition does the futures price equal the forward price, and why does the distinction matter otherwise?**

When the risk-free interest rate is constant (more generally, deterministic), the futures price equals the forward price, $$f(0,T) = F(0,T)$$. The two can differ when interest rates are stochastic, because a future's daily mark-to-market cash flows are reinvested or financed at the prevailing rate, so the correlation between the rate and the underlying price affects the value of those intermediate flows. A forward, settled only once at maturity, has no such intermediate cash flows.

## References

- [University of Oslo STK-MAT3700 — Forward and Future Contract. Option. (Lecture 6/7)](https://www.uio.no/studier/emner/matnat/math/STK-MAT3700/h22/lecture-notes/lecture6__7_forvard_future_contract_option.pdf)
- [BitMEX — Announcing the Launch of the Perpetual XBTUSD Leveraged Swap](https://www.bitmex.com/blog/announcing-the-launch-of-the-perpetual-xbtusd-leveraged-swap)
- [BitMEX — Perpetual Contracts Guide](https://www.bitmex.com/app/perpetualContractsGuide)
- [Bybit — Auto-Deleveraging (ADL) Mechanism](https://www.bybit.com/en/help-center/article/Auto-Deleveraging-ADL)
- [Binance — What Is Auto-Deleveraging (ADL) and How Does It Work?](https://www.binance.com/en/support/faq/detail/360033525471)
- [NC State Financial Mathematics — Futures Contract glossary](https://financial.math.ncsu.edu/glossary-f/futures-contract/)
