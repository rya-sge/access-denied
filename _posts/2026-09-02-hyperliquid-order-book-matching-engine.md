---
layout: post
title: "Hyperliquid's Onchain Order Book - Matching, Ordering, and How It Differs from a CEX and from GMX"
date:   2026-09-02
lang: en
locale: en-GB
categories: blockchain defi
tags: hyperliquid defi perpetual derivatives trading amm
series: hyperliquid
description: How HyperCore matches orders inside consensus state, why cancels beat aggressive orders in a block, and how that compares with a CEX engine, dYdX v4 and GMX.
image: /assets/article/blockchain/hyperliquid/hyperliquid-order-book.png
isMath: true
---

Almost every venue that calls itself a decentralised exchange has moved the order book somewhere the chain cannot see. dYdX v4 keeps short-term orders in validator memory and commits only the fills. GMX has no book at all and prices trades from an oracle. A centralised exchange runs a single matching engine in a private process nobody outside the company can inspect.

Hyperliquid takes the other option: the book is consensus state. Every validator holds it, every order and cancel is a committed transaction, and the matching rules are part of the state machine rather than part of an operator's implementation. That is a small sentence with large consequences, because once the ordering of transactions is a protocol rule rather than an operational detail, the protocol has to decide what fairness means and write it down.

This article looks at how HyperCore matches, what its transaction-ordering rule buys a market maker, how latency is priced when there is no colocation to sell, and then places that design next to a CEX engine, dYdX v4 and GMX to see which trade-offs each one is making.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Where the book lives

The phrase "onchain order book" covers four designs that share almost nothing, so they are best separated before anything else.

![A CEX engine in operator memory, Hyperliquid's book as replicated consensus state, dYdX v4's short-term orders in validator memory, and GMX with a pool instead of a book]({{site.url_complet}}/assets/article/blockchain/hyperliquid/order-book-venue-models-concept.png)

On Hyperliquid, HyperCore state includes one order book per asset. Placing, modifying and cancelling are all L1 actions, committed by HyperBFT like any other transaction, and the resting book at block height *h* is a deterministic function of the chain's history. Anyone running a node reconstructs the same book, including the queue position of every order.

On [dYdX v4](https://docs.dydx.xyz/), short-term orders live in validator memory for up to twenty blocks, and only the fill amount and expiry block height are committed to state. Long-term and conditional orders are stateful and do reach the chain. Matching happens off-chain, and the proposer includes the resulting matches in its block. The design achieves lower latency and free order placement, at the cost that the resting book itself is not something you can derive from chain state.

On [GMX](https://docs.gmx.io/docs/trading/v2/) there is no book to place anywhere. A trader creates an order request onchain, a keeper executes it against a signed oracle price, and the counterparty is a GM pool rather than another trader.

The rest of this article treats Hyperliquid's design as the subject and the others as points of comparison.

## The matching engine

### Price-time priority, ticks and lots

The order book behaves the way a centralised venue's does. Prices are integer multiples of a tick size, sizes are integer multiples of a lot size, and matching follows price-time priority.

The tick rule is expressed through decimals rather than an absolute increment. A price carries at most five significant figures and at most `MAX_DECIMALS - szDecimals` decimal places, where `MAX_DECIMALS` is 6 for perps and 8 for spot. Integer prices are always valid regardless of significant figures, which is why `123456` is accepted while `12345.6` is not. Sizes are rounded to the asset's `szDecimals`, so with `szDecimals = 3` a size of `1.001` is valid and `1.0001` is not.

### Margin is checked twice

Operations on a perp book take a reference to the clearinghouse, and margin is verified at two distinct moments: when an order is placed, and again **for the resting side at every match**.

The second check is the one without an obvious CEX analogue, and it exists because the oracle price moves between the two moments. A resting order placed when the account was healthy can fill several seconds and several oracle updates later, by which point the account may no longer be able to margin the position it is about to open. Checking only at placement would leave the margin system consistent at submission time and inconsistent everywhere else.

### Self-trade prevention is "expire maker"

When two orders from the same address would cross, HyperCore cancels the resting order instead of producing a fill. No fees are deducted and the cancel does not appear in the trade feed.

This is the behaviour a CEX would label *expire maker*, and it is the variant market makers generally want: the aggressing order keeps taking liquidity resting behind its own quote, up to its limit price, instead of being stopped by its own order.

## Transaction ordering: the rule with no CEX equivalent

![Cancels and ALO orders are prioritised in the mempool while IOC and GTC orders are delayed by their priority fee, then execution sorts the block into three classes before matching]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-order-priority-workflow.png)

A general-purpose chain orders transactions inside a block however the proposer arranged them. That is fine when transactions are independent and catastrophic for a limit order book, because it lets whoever controls block construction place an aggressive order ahead of a cancel that was submitted earlier.

Hyperliquid's mempool and consensus logic are **semantically aware** of which actions touch a book. Within a block, actions are sorted into three classes before execution:

1. Actions that send no GTC or IOC order to any book, which covers post-only (ALO) placements, transfers and everything unrelated to aggressive liquidity.
2. Cancels.
3. Actions carrying at least one GTC or IOC order.

Proposer order applies only *within* a class, and a `modify` is classified by the new order it places. Each L1 block also contains only a few consensus bundles, and within each bundle ALO orders and cancels execute before other transactions.

The documentation is explicit about both the purpose and the scope of the rule. It exists to protect makers against toxic flow, so that end users see tight spreads and deep liquidity during volatility, and the prioritisation of cancels and ALO orders over IOC and GTC orders sent at the same time **spans several blocks** rather than applying only inside one.

For a market maker this changes the shape of the risk. On a venue with plain first-come-first-served ordering, the exposure of a stale quote is bounded by how quickly your cancel reaches the sequencer relative to a taker's order, which is a race you win by spending money on infrastructure. Here the exposure is bounded by the protocol's own ordering rule, and no amount of priority fee buys the taker a place ahead of the cancel.

## Latency when there is no colocation to sell

A centralised venue sells proximity. Rack space next to the matching engine, cross-connects, and a tiered market-maker programme are all products, and the fairness of the queue is whatever the operator has decided to implement and is under no obligation to publish.

Hyperliquid has no designated market maker programme, no special fee schedule, and no latency advantage on offer. It replaces the colocation market with two explicit, onchain auctions, and the proceeds of both are burned rather than paid to anyone.

### The measurement problem

End-to-end latency on Hyperliquid is not comparable with a centralised matching engine's, because the book is onchain: the measurement includes the trip to an API server, mempool inclusion, and the time to commit, which is usually two blocks under pipelined HyperBFT.

The number that matters for a strategy is not that figure but its variance. A cancel or an ALO order can show roughly 380 ms end-to-end, while a user sending orders less than 10 ms apart can expect to see them sequenced predictably on the L1. Ordering is far less noisy than the round-trip time suggests, and ordering is what a queue position is made of.

### Gossip priority: paying to read sooner

Reading market data quickly is auctioned separately from sending orders. Two independent Dutch auctions run on a shared three-minute schedule, and nodes may interpret the resulting indices as an ordering for their peers when sending data, covering both split client blocks and normal client blocks. The Hyper Foundation non-validator opts into respecting that ordering.

Three properties of the auction are easy to get wrong:

- **Slots are not additive.** An IP bidding on multiple slots is prioritised according to its *lowest* slot, so buying both does not compound.
- **The onchain IP must match exactly** the IP the sending peer sees, and every network hop between a node and the validating set may or may not respect the ordering depending on how the parent is configured.
- **Pricing resets upward.** Each auction resets to ten times the previous winning price for that slot, with a minimum of 0.1 HYPE, and results only affect the following auction's duration.

The empirical effect on mainnet is around 25 ms of latency reduction per slot. Current winners are queryable through the `gossipPriorityAuctionStatus` info request, which is itself the difference from a colocation contract: the advantage is priced in public and its holder is a matter of record.

### Order priority: paying to be sequenced sooner

Sending is priced through a fee attached to the order action itself, expressed as a grouping `{"p": 12345}` interpreted as the fraction `p / 100000000`. It is charged from undelegated staking balance, converted to HYPE at the spot mark price, and burned. Priority grouping is only accepted when every order in the action is on a non-outcome asset and the action is homogeneous: all IOC, or all non-reduce-only ALO.

The mempool is then sorted by an effective time rather than an arrival time:

$$
\begin{aligned}
t_{\text{eff}} = t_{\text{arrival}} + f(\text{action},\ \text{priority})
\end{aligned}
$$

where $$f$$ is strictly decreasing in the priority rate and **zero for prioritised actions such as cancels**. Because the sort is on $$t_{\text{eff}}$$ and not on block membership, boundaries between blocks are irrelevant to relative ordering within an action type: the prioritisation is continuous even though blocks are discrete.

**IOC priority** has a linear effect on end-to-end latency between 0 and 8 basis points, worth roughly 45 ms per basis point on mainnet. Two constraints bound what it can buy:

- **Cancels are never overtaken.** All cancels are prioritised before all immediately executable orders, at any priority rate. A taker cannot pay to get ahead of a maker's cancel.
- **Above 8 bps, money stops buying time.** Everything from 8 bps to 100% has identical time preference in the mempool. Within a 70 ms bucket, IOC orders at or above 8 bps that the proposer would execute are sorted in decreasing order of fee, so the upper range breaks ties among near-simultaneous orders rather than moving an order forward in time.

**ALO priority** does something different, and confusing the two is easy. It has no effect on mempool ordering at all: ALO orders are processed FIFO as transactions, with end-to-end latency similar to cancels. What the fee buys is **queue position at a price level**, on a 400 ms timescale. The tail of the queue at each level, consisting of orders placed within the past 400 ms, is sorted in decreasing order of priority rate, so any slot is open to bidding for a window of that duration. The fee is deducted when the order is placed, whether or not it ever fills.

The window is continuous rather than bucketed, which produces an ordering that looks wrong until the rule is applied carefully. Take a level that opens empty. Order `A` lands with no priority fee at time `t'`. Order `B` lands at `t' + 399 ms` with priority `p`, so `B` sorts ahead of `A`. Order `C` lands at `t' + 401 ms` with a higher priority `p' > p`, but `A` has now been resting for the full window and its position is locked, so the queue reads `B > A > C` despite `C` paying the most.

## Rate limits are part of the book's design

On a centralised venue, rate limits are an operational protection for the exchange's own infrastructure. On Hyperliquid they are also a resource-allocation rule for shared block space, and they are indexed to how much you actually trade rather than to how much you are willing to send.

Alongside the per-IP REST and WebSocket limits, the address-based rule allows **one request per 1 USDC of cumulative volume since the address was created**, with an initial buffer of 10 000 requests. An order value of 100 USDC therefore requires a 1% fill rate to be sustainable. A rate-limited address is allowed one request every ten seconds, and cancels get a separate, larger allowance of `min(limit + 100000, limit * 2)` precisely so that hitting the limit never traps open orders on the book.

Two further limits shape quoting behaviour. The default open-order allowance is 1 000, plus one order per 5M USDC of volume, capped at 5 000; once an address holds 1 000 open orders, a new reduce-only or trigger order is rejected. And during high congestion, an address is limited to twice its previous day's maker share of block space, computed once per UTC date, with the maker share scaled the same way volume counts toward fee tiers.

Read together, these say something the fee schedule alone does not: block space is allocated in proportion to liquidity provided, and the venue would rather throttle a spammy quoter than widen everyone's spread.

## How a centralised order book differs

| | Centralised exchange | Hyperliquid |
|---|---|---|
| **Where the book lives** | Operator memory, in a private process | Consensus state, replicated by every validator |
| **Who matches** | One engine the operator runs | Every validator, deterministically |
| **Ordering inside the queue** | Arrival at the gateway, subject to whatever the engine implements | Three action classes, then proposer order within a class |
| **Cancel versus aggressive order** | A race decided by network latency | Cancels are a prioritised class and are never overtaken |
| **Buying an advantage** | Colocation, cross-connects, DMM programmes, negotiated privately | Two public Dutch auctions, proceeds burned, winners queryable |
| **Verifiability** | The operator's word plus a trade feed | Reconstructable from node output, including queue position |
| **Rate limits** | Weighted requests, tiered by account | Weighted requests plus one action per 1 USDC of lifetime volume |
| **Custody** | The operator holds the funds | The clearinghouse is protocol state |
| **Failure you cannot observe** | Reordering, a favoured counterparty, a paused withdrawal | A colluding stake majority setting the oracle |

The last row is where the two designs really part. A CEX asks a trader to trust an operator whose queue, whose reordering and whose favours are all invisible from outside. Hyperliquid asks the trader to trust that more than two thirds of staked HYPE is honest, and hands over the transaction log for everything downstream of that one assumption.

## How other DeFi designs differ

### dYdX v4: the book off-chain, the fills onchain

dYdX v4 keeps a real limit order book with real makers, but deliberately keeps most of it out of consensus. Short-term orders sit in validator memory for up to twenty blocks; only the fill amount and the expiry block height are written to state. Long-term and conditional orders are stateful and are committed. Validators gossip orders to each other, the proposer matches, and the matches go into the next block.

The gain is real: placing and cancelling short-term orders costs no gas and takes no block space, and latency is closer to a centralised venue's. What is given up is the property Hyperliquid keeps, namely that the resting book is derivable from chain state. Two nodes can hold different views of the book without either being provably wrong, and a fill can be verified after the fact while the queue it came from cannot be replayed.

Hyperliquid pays for that property with block space and with an end-to-end latency it openly describes as not comparable with a centralised engine's.

### GMX: no book at all

![The same long twice: on Hyperliquid it is committed and matched against a resting maker; on GMX a keeper executes the request against a signed oracle price with the pool as counterparty]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-vs-gmx-execution-sequence.png)

GMX V2 is not a slower order book but a different instrument. There is no matching between users: every position is opened against a GM pool, whose liquidity providers take the other side, and the price comes from an oracle rather than from a queue.

Several of the mechanics that follow from that choice invert what an order-book trader expects:

- **Execution is a two-step, asynchronous flow.** The trader creates an order request onchain; a keeper then fetches a signed Chainlink Data Streams price and executes the order in a separate transaction. Nothing has traded when the request lands.
- **The entry price is the oracle price.** A long opens at `maxPrice` and closes at `minPrice`; a short opens at `minPrice` and closes at `maxPrice`.
- **There is no price impact at entry.** Impact applies when a position is closed or decreased, computed from the change in pool imbalance, and it adjusts the exit price rather than deducting collateral so that leverage is preserved.
- **Fees are steered by imbalance, not by aggression.** The position fee is 0.04% when a trade reduces the gap between long and short open interest and 0.06% when it widens it, which is the pool's substitute for a maker-taker schedule.
- **Two separate carrying costs exist.** Funding flows continuously between longs and shorts according to open-interest imbalance, while the borrowing fee is paid only by the side with the larger open interest and accrues to liquidity providers and the protocol.
- **Execution is not guaranteed.** An order can fail to execute because of an oracle price gap, insufficient liquidity, or a max-leverage constraint.

Writing the price impact as a function of imbalance $$I$$ with factor $$k$$ and exponent $$e$$:

$$
\begin{aligned}
\text{impact} = k\,I_{0}^{\,e} - k\,I_{1}^{\,e}
\end{aligned}
$$

where $$I_0$$ and $$I_1$$ are the imbalance before and after the trade. A trade that reduces imbalance receives a better price; one that increases it receives a worse one.

Four consequences distinguish this from a book:

- **Depth is a pool parameter, not a queue.** On Hyperliquid, a large IOC order walks the book and fills at progressively worse prices set by makers who chose those prices. On GMX, size is bounded by open-interest caps and priced by a formula, so slippage is predictable in advance but nobody chose it.
- **There is no queue to be ahead of.** Priority fees, cancel prioritisation, ALO queue position and price-time priority have no meaning where there is no queue. The equivalent competitive surface is keeper behaviour and oracle timing.
- **The counterparty is passive.** GM liquidity providers hold the other side of every position whether they want the exposure or not. A Hyperliquid maker chooses each quote and can pull it.
- **The oracle is the whole attack surface for pricing.** A book can be manipulated by trading against it, which costs money and leaves a trail. An oracle-priced venue lives or dies on the freshness and integrity of the signed price the keeper submits.

### Constant-function AMMs

A [constant-function market maker]({{site.url_complet}}/2025/07/29/automated-market-makers-amm/) sits further from an order book still. Price is a function of reserves, liquidity is passive, and there is neither a queue nor a resting quote to cancel. The closest thing Hyperliquid has to it is HIP-2 Hyperliquidity, and the difference is instructive: Hyperliquidity is an onchain strategy that posts discrete post-only orders **into the shared book**, so an active market maker can quote inside its ladder and improve the market without liquidity having to migrate anywhere.

## What each design costs

| | CEX | Hyperliquid | dYdX v4 | GMX V2 |
|---|---|---|---|---|
| **Counterparty** | Another trader | Another trader | Another trader | The pool's LPs |
| **Price comes from** | The book | The book | The book | An oracle, plus imbalance on close |
| **Book is verifiable** | No | Yes, from chain state | Fills only | No book exists |
| **Cancel guarantee** | Best-effort race | Prioritised class, spans blocks | Off-chain, proposer-dependent | Nothing to cancel |
| **Latency advantage** | Sold as colocation | Auctioned publicly, proceeds burned | Validator proximity | Keeper and oracle timing |
| **Cost of an order** | Free, subject to limits | Block space, plus volume-indexed limits | Free for short-term orders | Gas for the request, plus keeper execution |
| **Main failure mode** | Operator misbehaviour | Stake-majority collusion on the oracle | Book state not reconstructable | Stale or gapped oracle, keeper inaction |

## Conclusion

Hyperliquid's matching engine is conventional in its core: price-time priority, ticks and lots, post-only and IOC semantics that a CEX market maker would recognise. What changes is that the engine runs inside consensus, which forces the protocol to answer questions a centralised venue answers privately. It answers them by writing an ordering rule into execution that places cancels ahead of aggressive orders, by checking margin again on the resting side at every match, and by replacing the colocation market with two Dutch auctions whose proceeds are burned and whose winners are queryable.

The comparison sharpens what that costs. dYdX v4 buys latency and free order placement by keeping the resting book out of consensus, which means a fill can be verified but the queue it came from cannot. GMX removes the book entirely: there is no queue, no cancel and no maker, the pool takes the other side of every position, and the entire pricing surface reduces to an oracle price a keeper delivers. Each design relocates trust rather than removing it, and the question that separates them is not which is most decentralised but which failure a user can still observe after it happens.

![Mindmap of Hyperliquid's order book covering consensus state, the two margin checks, intra-block ordering, priority auctions, rate limits and the CEX, dYdX v4 and GMX comparisons]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-order-book.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Price-time priority** | The matching rule where the best price fills first and, within a price level, the earliest resting order fills first. |
| **ALO (post-only)** | An order that may only rest on the book; if it would cross on arrival it is rejected rather than taking liquidity. |
| **IOC** | An order that fills whatever it can immediately and cancels the remainder, and which HyperCore places in the last of the three intra-block ordering classes. |
| **Intra-block ordering classes** | The three groups (no GTC/IOC order, cancels, GTC/IOC orders) into which HyperCore sorts a block's actions before execution, with proposer order applying only inside a group. |
| **Effective time** | The mempool sort key `arrival_time + f(action, priority)`, where `f` is strictly decreasing in the priority rate and zero for prioritised actions such as cancels. |
| **Gossip priority** | A three-minute Dutch auction over two independent slots that buys earlier delivery of market data from peers respecting the ordering, worth roughly 25 ms per slot. |
| **Order priority** | A fee attached to an order action, charged from undelegated staking balance and burned, that moves an IOC order forward in the mempool or an ALO order forward in the queue at its level. |
| **Expire maker** | The self-trade prevention behaviour where two orders from one address cause the resting order to be cancelled rather than filled, with no fee and no trade-feed entry. |
| **GM pool** | The GMX V2 per-market liquidity pool that acts as the counterparty to every position in that market, in place of a matching engine. |
| **Price impact (GMX)** | The adjustment to a closing or decreasing position's exit price derived from the change in pool imbalance, absent at entry and applied to the price rather than to collateral. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| The resting book at any height is derivable from chain state. | Every order, modify and cancel is a committed L1 action executed deterministically. | Orders are moved to validator memory, as in the dYdX v4 short-term design. |
| A cancel submitted at time `t` is processed before an aggressive order submitted at `t`. | The three-class intra-block ordering, plus `f = 0` for cancels in the mempool sort. | Actions are ordered purely by proposer sequence. |
| No priority fee lets a taker overtake a cancel. | All cancels are prioritised before all immediately executable orders, at any rate. | The prioritised-action carve-out is removed from the mempool sort. |
| Margin holds for the resting side at the moment of the fill, not only at placement. | A second margin check for the resting side at every match. | The match-time check is dropped as an optimisation. |
| A latency advantage is public, priced and burned. | The gossip and order priority auctions, with results in `gossipPriorityAuctionStatus` and fees burned. | Advantages are negotiated off-chain, as with colocation or a DMM programme. |
| An address cannot consume block space out of proportion to its trading. | The one-request-per-1-USDC-of-volume rule and the congestion cap at twice the previous day's maker share. | Rate limits become purely per-IP, letting a spammy address crowd the book. |
| Hitting the rate limit never traps open orders. | Cancels carry a separate allowance of `min(limit + 100000, limit * 2)`. | Cancels are metered on the same budget as placements. |
| Two orders from one address never trade with each other. | Self-trade prevention cancels the resting order, with no fill and no fee. | The expire-maker behaviour is replaced by a fill. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| ALO priority fees are deducted at placement whether or not the order ever fills. | Budget them as a cost of quoting, not a cost of trading, and size them against expected queue value. |
| ALO priority has no effect on mempool ordering; it only reorders the queue tail over a 400 ms window. | Do not use it to try to reach the book sooner; use it only where queue position at a level is what you need. |
| An IOC priority above 8 bps buys no additional time, only tie-breaking inside a 70 ms bucket. | Cap the bid at 8 bps unless you specifically need to win ties against near-simultaneous orders. |
| The address rate limit is indexed to lifetime volume, and a new address starts with only 10 000 requests. | Model the sustainable quote-and-cancel rate from expected fill rate before deploying a strategy on a fresh address. |
| Prices are limited to five significant figures and `MAX_DECIMALS - szDecimals` decimals, but integer prices are always valid. | Round prices with both rules, not just the decimal one, and read `szDecimals` from the `meta` response rather than hard-coding it. |
| Self-trade prevention cancels the resting order silently: no fee, and nothing in the trade feed. | Reconcile open orders from the book feed rather than inferring cancellation from trade events. |
| End-to-end latency is dominated by commit time and is not comparable with a CEX round trip. | Measure the variance of L1 sequencing rather than the round-trip figure when tuning a strategy. |
| Reconstructing the book locally from node output is faster and more granular than the API. | Follow the `order_book_server` reference, and use the `insertBefore` field on `RawBookDiff::New` to keep level ordering correct under ALO priority. |
| Gossip priority only applies if the onchain IP matches exactly what the sending peer sees, and each hop may ignore it. | Verify the IP registered in the bid against the peer's view, and check how every intermediate node is configured. |

## Frequently Asked Questions

**Q: What does it change that the order book is consensus state rather than validator memory?**

Two things, one gained and one paid for.

The gain is that the resting book at any height is a deterministic function of the chain's history, so any node reconstructs the same book including every order's queue position. A fill can be checked against the book that produced it, and no two honest nodes can hold different views.

The cost is block space and latency. Every placement, modification and cancellation is a committed transaction, which is why Hyperliquid meters actions against trading volume and describes its end-to-end latency as not comparable with a centralised engine's. dYdX v4 makes the opposite trade: short-term orders stay in validator memory for up to twenty blocks and only the fill amount and expiry height reach state, which makes placement free and fast and the queue unverifiable.

**Q: Why are cancels a separate class in the block, and what does that protect against?**

Under plain first-come-first-served ordering, a maker's cancel and a taker's aggressive order race each other, and the race is decided by network latency. A maker holding a stale quote during a fast move loses that race to whoever has better infrastructure.

HyperCore sorts a block's actions into three classes before execution: actions sending no GTC or IOC order, then cancels, then actions carrying at least one GTC or IOC order. Proposer order only applies inside a class, and the prioritisation spans several blocks rather than a single one.

The effect is that stale-quote exposure is bounded by a protocol rule instead of by a spending contest, which is the stated reason it exists: protecting makers against toxic flow so that users see tighter spreads during volatility.

**Q: Order priority fees look like paying for queue jumping. Why is that not the same as selling colocation?**

Because of what the fee cannot buy and where the money goes.

A taker can never overtake a cancel, at any priority rate, since cancels are a prioritised class with a zero delay term in the mempool sort. Beyond 8 basis points, additional payment buys no additional time and only breaks ties among orders arriving inside the same 70 ms bucket.

The auctions are also public: current gossip priority winners are queryable through `gossipPriorityAuctionStatus`, and both gossip and order priority fees are burned rather than paid to the venue. A colocation contract is negotiated privately, benefits the operator's revenue, and is not visible to the counterparties trading against its holder.

**Q: An ALO order pays a high priority fee and still ends up behind an older order with none. Why?**

Because ALO priority reorders only the *tail* of the queue at a level, defined as orders placed within the past 400 ms, and an order older than that window has locked in its position.

Take an empty level. Order `A` lands with no fee at `t'`. Order `B` lands at `t' + 399 ms` with priority `p`, so it sorts ahead of `A`, both still being inside the window. Order `C` lands at `t' + 401 ms` with `p' > p`, but `A` is now outside the window and immovable, and `B` already sits in front of `A`. The queue reads `B > A > C`.

The window is continuous rather than bucketed: each new order compares against the tail of orders less than 400 ms old at the moment it is placed.

**Q: Where does the difference between Hyperliquid and GMX show up for a trader?**

In four places:

- **Who takes the other side.** On Hyperliquid it is another trader who chose to quote there. On GMX it is a GM pool, whose liquidity providers hold the exposure whether they want it or not.
- **What sets the price.** A queue of resting orders versus an oracle price, `maxPrice` for a long open and `minPrice` for a short open, with no price impact applied at entry.
- **When execution happens.** A committed match inside the block that carried the order, versus a two-step flow where the request lands first and a keeper later executes it against a signed price, with no guarantee it executes at all.
- **What can go wrong with pricing.** Manipulating a book requires trading against it, which costs money and leaves a record. An oracle-priced venue depends entirely on the freshness and integrity of the price the keeper submits.

The corollary is that the whole vocabulary of queue competition, meaning priority fees, cancel ordering, post-only placement and price-time priority, has no counterpart on GMX, because there is no queue.

**Q: GMX charges 0.04% or 0.06% depending on the trade. Is that a maker-taker schedule?**

No, and the distinction matters. A maker-taker schedule prices *aggression*: whether you removed liquidity from a book or added it.

GMX has no book to add to, so it prices *balance* instead. A position fee of 0.04% applies when the trade reduces the absolute gap between long and short open interest, and 0.06% when it widens that gap. The same principle drives the rest of the pool's economics: funding flows between longs and shorts according to open-interest imbalance, the borrowing fee is paid only by the larger side, and price impact on closing is computed from the change in imbalance.

Where an order book pays you for supplying a quote someone else needed, a pool pays you for taking the side it is short of.

**Q: Combining the ordering rule and the double margin check, why can a resting order be safe when placed and unsafe when filled?**

Because the two events are separated in time by the oracle. The mark price is recomputed whenever validators publish new oracle prices, roughly every three seconds, and a resting order can sit through many such updates before an aggressor reaches it.

The placement check confirms the account can support the order at submission. The match check confirms the resting side can still support the position at the instant of the fill, and it runs for every match rather than once per order. Without it, an order placed by a healthy account could open a position that account can no longer margin, and the clearinghouse would be consistent only at submission time.

This is also why the intra-block ordering rule matters beyond fairness: putting cancels ahead of aggressive orders gives a maker a usable way to withdraw a quote before the oracle moves it into a position they no longer want.

## References

### Hyperliquid documentation

- [Order book (HyperCore)](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/order-book) — the matching engine, the two margin checks and the intra-block action ordering
- [Order book (trading)](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/order-book) — tick and lot semantics, price-time priority
- [Tick and lot size](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/tick-and-lot-size) — the five-significant-figure and `MAX_DECIMALS - szDecimals` rules
- [Order types](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/order-types) — market, limit, chase, scale, TWAP, and the GTC/ALO/IOC options
- [Self-trade prevention](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/self-trade-prevention) — the expire-maker behaviour
- [Optimizing latency](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/optimizing-latency) — end-to-end latency, sequencing variance, node-side book reconstruction
- [Priority fees](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/priority-fees) — the gossip and order priority auctions, `effective_time`, the 400 ms ALO window
- [Rate limits and user limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) — address-based limits, open-order caps, congestion maker share
- [Market making](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/market-making) — no DMM programme, no special rebates, no latency advantages
- [Robust price indices](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/robust-price-indices) — the oracle and mark price the margin checks use
- [HIP-2: Hyperliquidity](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-2-hyperliquidity) — the onchain strategy that quotes into the shared book

### Other venue designs

- [GMX documentation — Trading on V2](https://docs.gmx.io/docs/trading/v2/) — the pool model and keeper execution
- [GMX documentation — Positions and order types](https://docs.gmx.io/docs/trading/order-types/) — the two-step request and execution flow, and the oracle price used per side
- [GMX documentation — Fees](https://docs.gmx.io/docs/trading/fees/) — position fees by imbalance, price impact on close, funding and borrowing fees
- [dYdX documentation](https://docs.dydx.xyz/) — short-term orders in validator memory, stateful orders, and proposer matching

### Tooling

- [hyperliquid-dex/order_book_server](https://github.com/hyperliquid-dex/order_book_server) — reference implementation for reconstructing the book from node output, read on 2 September 2026 from the default branch

### Related articles

- [Automated Market Makers (AMMs) - Overview]({{site.url_complet}}/2025/07/29/automated-market-makers-amm/)
- [Traditional Futures vs. Perpetual Futures: A Technical Comparison]({{site.url_complet}}/2025/12/29/traditional-vs-perpetual-futures/)
