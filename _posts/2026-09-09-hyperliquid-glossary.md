---
layout: post
title: "Understanding Hyperliquid - The Vocabulary, from Beginner to Advanced"
date:   2026-09-09
lang: en
locale: en-GB
categories: blockchain defi
tags: hyperliquid defi perpetual derivatives trading glossary key-terms
series: hyperliquid
description: A layered glossary of Hyperliquid. Thirty terms across three levels, from HyperCore and mark price to auto-deleveraging, portfolio margin and the four HIPs.
image: /assets/article/blockchain/hyperliquid/hyperliquid-glossary-mindmap.png
isMath: false
---

Hyperliquid is a layer-1 blockchain whose state machine is a derivatives exchange. The order book, the margin engine and the liquidation logic are not a service running beside the chain, they are the thing validators agree on, and a general-purpose EVM runs next to them under the same consensus. A reader meets the protocol through its documentation, through its API, or through a contract that calls into the exchange, and in all three the vocabulary arrives before the explanation does.

That vocabulary is the obstacle. Hyperliquid borrows words from centralised derivatives trading (mark price, funding, maintenance margin), gives several of them a protocol-specific meaning, and adds a layer of names that exist nowhere else: HyperCore, CoreWriter, Hyperliquidity, HIP-3. This article is a term list rather than a walkthrough. It is split into three levels, beginner, intermediate and advanced, ordered so that no entry depends on a term defined after it, and each entry is written to stand on its own for a reader who arrives at it directly.

After reading it, the protocol documentation and the API reference should be legible without a second tab open, and a question about which price triggered a liquidation should have an unambiguous answer. The article defines the vocabulary and stops there. It does not walk through an integration, derive the margin formulas, or review any implementation; the narrative articles listed in the series box above do that work.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Beginner — the layers, the actors and the instrument

These terms name the pieces the protocol is built from and the roles that act on them. Nothing here assumes prior exposure to Hyperliquid, and everything in the next two levels is assembled out of this level.

### HyperBFT

The consensus algorithm Hyperliquid validators run to agree on the contents and order of blocks. It is a variant of HotStuff tuned for latency, and it commits a block in roughly 0.2 seconds at the median and 0.9 seconds at the 99th percentile.

One consensus covers the whole chain, so there is no settlement step between trading and smart contract execution and no bridge between the two. Safety and liveness hold as long as more than two thirds of the staked voting power behaves honestly.

### HyperCore

The exchange half of the chain's state. Order books, perpetual and spot balances, margin state, the oracle, staking records and vault positions all live here, and every order, cancel, fill and liquidation is a committed transaction rather than a message to an off-chain matching service.

HyperCore is not a smart contract and not an EVM component. It is execution logic built into the node itself, which is how it sustains around 200 000 orders per second while every validator holds an identical copy of the book.

### HyperEVM

The general-purpose execution environment that runs beside HyperCore under the same consensus, with Ethereum semantics and ordinary Solidity contracts. Mainnet is chain ID 999 and testnet 998, the hardfork level is Cancun without blobs, and gas is paid in HYPE.

Because both halves are committed by the same validators in the same block, a contract reaches exchange state without a bridge or a message-passing protocol. The two doors between them are [CoreWriter](#corewriter) for writes and the [L1Read precompiles](#l1read-precompiles) for reads.

### HYPE

The chain's native token. It pays gas on HyperEVM, is staked with validators to secure consensus, is the bond a market deployer must post, and is what trading fee revenue is eventually converted into and burned as.

Fees that are not paid out to a deployer reach the Assistance Fund at `0xfefe…fefe`, which buys HYPE with them and burns it. Staked HYPE also discounts trading fees, from 5% above 10 HYPE to 40% above 500 000.

### Validator

A node that participates in HyperBFT, produces blocks in proportion to the HYPE delegated to it, and publishes a price for every listed asset roughly every three seconds. Validators are also the electorate for the protocol's votes on deployers, quote assets and delistings.

Running one requires at least 10 000 HYPE of self-delegation, locked for a year. A validator that is slow or unavailable can be jailed by a quorum of its peers, which stops its rewards without touching its stake. Jailing is a separate mechanism from [slashing](#slashing-surface).

### Oracle price

The protocol's reference price for an asset, republished about every three seconds. Each validator computes a weighted median across major spot venues, with Binance counted three times, OKX and Bybit twice each, and Kraken, KuCoin, Gate.io, MEXC and Hyperliquid spot once each. The protocol then takes a stake-weighted median of every validator's submission.

Two medians in series is what makes the number expensive to move: one venue printing a bad price is outvoted inside a validator's own computation, and one validator lying is outvoted by stake. The oracle price drives funding, and it is not the price a liquidation is measured against.

### Central limit order book (CLOB)

The structure holding every resting buy and sell order for one market, sorted by price and, within a price level, by arrival time. An incoming order that crosses the best opposite price trades against it; one that does not rests in the book and waits.

On Hyperliquid the book is consensus state rather than a private process, so every validator holds the same book and the matching rules are part of the state machine instead of an operator's implementation. Prices must be integer multiples of a tick size and sizes integer multiples of a lot size.

### Maker and taker

The two roles in any trade. A maker posts an order that rests in the book and adds liquidity; a taker sends an order that crosses the spread and removes it. Fees follow the roles, so takers pay and makers are frequently paid.

Base perpetual fees run from 0.045% for a taker at the lowest volume tier down to 0.024% at the highest, with maker rebates reaching 0.015%. The distinction reaches further than cost, because Hyperliquid's block-ordering rule treats a maker's cancel and a taker's aggressive order differently (see [intra-block action ordering](#intra-block-action-ordering)).

### Perpetual future (perp)

A derivative tracking the price of an underlying asset with no expiry date and no delivery. A position is opened against collateral and stays open until it is closed or liquidated, and a recurring payment between the two sides keeps its price tethered to the underlying, doing the job that convergence to an expiry date does for a dated future.

Perps carry most of Hyperliquid's volume. The recurring payment is the [funding rate](#funding-rate), and the price it tethers to is the [oracle price](#oracle-price).

### Margin

The collateral backing an open position. Initial margin is what must be posted to open one, computed as position size times [mark price](#mark-price) divided by the chosen leverage. Maintenance margin is the smaller amount that must remain for the position to stay open.

Leverage on a perp is therefore a way of naming an initial margin requirement, not a loan of assets. Any transfer of margin out of an account without trading must also leave the larger of the initial margin requirement and 10% of total position value behind.

## Intermediate — how the pieces interact

These terms assume the objects above and name the mechanisms connecting them: how a position is priced and funded, when it is closed against its owner's wishes, and how a contract reaches the exchange.

### Clearinghouse

The component owning margin state: which addresses hold which positions, what collateral backs them, and what each account is worth. There is a perpetual clearinghouse and a spot clearinghouse, and one address can hold up to four kinds of sub-account across them, namely cross perp, spot, staking, and one per isolated position.

Transfers between sub-accounts are instant in every direction but one. Moving HYPE out of staking passes through a seven-day queue that admits at most five pending withdrawals.

### Mark price

The price the protocol values open positions at, and the one deciding margin, liquidation, stop-loss and take-profit triggers, and unrealized profit. It is the median of three independently sourced inputs: the [oracle price](#oracle-price) plus a 150-second EMA of the gap between Hyperliquid's mid and that oracle, the median of Hyperliquid's own best bid, best ask and last trade, and a weighted median of the perpetual mids on major external venues.

Mark price and oracle price are the pair most often collapsed into one. Funding is computed and paid on the oracle price; everything touching solvency runs on the mark price. A liquidation that looks unjustified against the oracle usually was not.

### Funding rate

The recurring payment between long and short holders of a perp that keeps its price near the underlying. It is a premium sampled from the book plus the gap between a fixed interest rate and that premium, clamped to 0.05% either way, capped at 4% per hour and settled every hour at one eighth of the quoted eight-hour rate.

The amount paid is position size times [oracle price](#oracle-price) times the rate, and it moves from one side of the market to the other. The protocol takes no share of it, which is what makes it a price anchor rather than a fee.

### Cross margin and isolated margin

Two ways of assigning collateral to positions. Under cross margin every cross position in an account draws on one shared collateral pool, which uses capital efficiently and means a loss on any one position can liquidate all of them. Under isolated margin a position carries its own collateral, and its liquidation cannot reach the rest of the account.

A third setting, strict isolated, behaves like isolated except that margin can never be withdrawn by hand; it is released only in proportion as the position closes. Cross positions may additionally count unrealized profit towards margin, so a winning position can support a new one before it is closed.

### Maintenance margin

The floor of collateral a position must keep to stay open, defined as half the initial margin required at the asset's maximum leverage. That places it between 1.25% and 16.7% of notional in practice, depending on the asset.

Falling below it produces no warning and no margin call. It makes the account liquidatable immediately. The requirement is not one number per asset either, but a function of position size, which is what a [margin tier](#margin-tier) describes.

### Liquidation

The forced closing of a position whose account equity has fallen below its maintenance margin. Hyperliquid runs it as a ladder rather than a single event. The first rung sends a market order to the book for the position; positions above 100 000 USDC go in 20% increments, followed by a 30-second cooldown during which any further liquidation order covers the whole position.

The second rung applies when equity falls below two thirds of the maintenance requirement: the position is transferred to the backstop liquidator inside [HLP](#hlp-hyperliquidity-provider) instead of being worked through the book. Hyperliquid charges no clearance fee, and profit from backstop liquidations accrues to HLP.

### HLP (Hyperliquidity Provider)

The protocol's community-owned vault. Anyone may deposit USDC into it and share in its profit and loss. It market-makes across several strategies, supplies USDC to Earn (the protocol's lending market), takes over backstop liquidations through its liquidator strategy, and receives a share of trading fees.

HLP is what stands between a badly underwater account and the rest of the platform, one rung before [auto-deleveraging](#auto-deleveraging-adl). Deposits are locked for four days from the most recent deposit, and that lock is the depositor's exposure to the backstop role.

### Intra-block action ordering

The rule deciding the sequence of actions inside a block. Instead of first-come-first-served, HyperCore sorts every action in a block into three classes and executes them in that order: actions sending no aggressive order at all (post-only placements, transfers), then cancels, then actions sending at least one order able to take liquidity. The proposer's chosen order applies only within a class.

The consequence is that a maker's cancel submitted in the same block as an order that would have hit that quote is processed first. Any model of Hyperliquid assuming FIFO ordering inside a block is wrong.

### L1Read precompiles

A set of precompiled contracts starting at address `0x…0800` through which a HyperEVM contract reads HyperCore state: perpetual positions, spot balances, oracle prices, vault equity, staking delegations, the L1 block number.

The values returned reflect HyperCore as of the moment the EVM block was constructed. Gas is `2000 + 65 × (input_len + output_len)`, and an invalid argument such as an unknown asset index consumes every unit of gas forwarded to the call rather than reverting cheaply, which makes an unvalidated index a griefing surface.

### CoreWriter

The system contract at `0x3333…3333` through which a HyperEVM contract writes to HyperCore. A call emits a log that HyperCore interprets as an action, encoded as a version byte, a three-byte action ID and ABI-encoded fields. The action table covers limit orders, cancels, vault transfers, staking, spot sends, borrow and lend, and account abstraction changes.

Two constraints catch integrators. The calling account must already exist on HyperCore before the EVM block is built, so funding it in the same block does not help. And order actions and vault transfers are held back a few seconds deliberately, so that routing through the EVM buys no latency advantage over the L1 mempool.

## Advanced — the edges, the failure modes and the deployable primitives

These terms assume the mechanisms above. They cover what happens at the boundaries: the formulas keeping requirements continuous, the last rung of the solvency ladder, and the primitives letting outsiders deploy markets of their own.

### Margin tier

The size bracket determining an asset's maintenance requirement. Requirements are not a flat percentage of notional; they follow `maintenance_margin = notional × rate(tier) − deduction(tier)`, where the deduction accumulates across brackets so that total maintenance margin stays continuous where a position crosses from one tier into the next.

Rates depend on the tier rather than on the asset, and each asset selects which table it uses. On mainnet, BTC allows 40x leverage up to 150M USDC of notional and 20x above it, ETH 25x up to 100M then 15x. Without the deduction term, a position crossing a boundary would jump discontinuously into liquidation.

### Auto-deleveraging (ADL)

The last rung of the solvency ladder, reached when an account's value has gone negative and neither book nor backstop liquidation recovered it. Profitable traders on the opposite side are ranked by `(mark price / entry price) × (notional / account value)` and closed against the underwater account at the previous mark price.

ADL is a state transition rather than a fund with a balance, which is what makes the protocol's core solvency invariant unconditional: a user holding no open positions never absorbs another account's losses. Venues that socialise losses across balances offer no equivalent guarantee.

### Portfolio margin

An account mode in which one portfolio of eligible collateral (HYPE, BTC, USDC, USDT) backs every position, with borrowing arranged automatically against it. Collateral counts at a loan-to-value ratio, 0.65 for HYPE and 0.5 for BTC, and any shortfall is borrowed at a utilisation-based rate indexed hourly to match the funding interval.

Liquidation triggers on a portfolio margin ratio above 0.95 and is taken over by a backstop liquidator that unwinds through a TWAP with a ten-minute half-life, with no market phase at all because spot books are thinner. Two behaviours surprise integrators: when a supply or borrow cap binds, the account silently falls back to non-portfolio behaviour, and whether perpetual positions or spot borrows unwind first depends on the order of oracle updates.

### Dual-block architecture

HyperEVM's two interleaved block types, each with its own mempool but sharing one sequence of EVM block numbers. Small blocks are produced every second with a 3M gas limit and carry ordinary traffic; big blocks are produced every 60 seconds with a 30M gas limit and exist for large deployments.

An address opts into big blocks with `evmUserModify {usingBigBlocks: true}`. The flag lives on the HyperCore user rather than the EVM account, so a deployer must already exist on HyperCore before it can set the flag, and must unset it to return to one-second blocks.

### API wallet and the nonce set

A delegated signing key registered to an account, so that a trading process never holds the master key. Strictly incrementing nonces do not suit an order book, so HyperCore instead keeps the 100 highest nonces seen for each signer. An action is valid when its nonce exceeds the smallest of those, has never been used, and falls inside a window running from two days before the block timestamp to one day after it.

Nonces are tracked per signer rather than per account, so two sub-accounts driven by one API wallet share a set. The hazard is pruning: when an API wallet is deregistered, expires, or its registering account is emptied, the set is discarded and previously signed actions become replayable.

### HIP-1 (native token standard)

Hyperliquid's native fungible token standard. A HIP-1 token has a capped supply and a spot order book on HyperCore from the moment it exists, with no contract deployed anywhere. The deployment gas is set by a 31-hour Dutch auction falling linearly to a floor of 500 HYPE, restarting at twice the previous clearing price.

Decimals obey `szDecimals + 5 ≤ weiDecimals`, which fixes the lot size at `10^(weiDecimals − szDecimals)`. The deployer initially receives all spot trading fees denominated in the base token and may lower that share but never raise it. Only the first of the five deployment steps is timed and charged, and a deployment stuck at a later step is not refunded.

### HIP-2 (Hyperliquidity)

A market-making ladder running inside block transition logic, with no operator, no keeper and no admin key. It maintains a geometric grid of price levels, `px_i = round(px_{i−1} × 1.003)`, refreshed on the first block at least three seconds after the previous update, and it posts post-only orders into the same book everyone else quotes in.

Hyperliquidity gives a newly deployed [HIP-1](#hip-1-native-token-standard) token a book with depth on its first day. It does not exclude other market makers, who are free to quote inside its 0.3% spread, and it currently runs only on spot pairs quoted in USDC.

### HIP-3 (builder-deployed perpetuals)

A permissionless path to deploying an entire perpetual DEX, with its own assets, oracle definitions, margin parameters and fee scale, running on the same HyperCore engine. The deployer stakes 500 000 HYPE and keeps it staked for at least 183 days after deployment, and the first three assets skip the Dutch auction that later ones go through.

What the deployer takes on is substantial: it publishes the oracle prices its own markets settle against, so users are protected mainly by its exposure to a validator vote that can burn the bond. One decision is permanent, since enabling cross margin on an asset can never be undone.

### HIP-4 (outcome market)

A fully collateralised contract settling within a fixed range, covering prediction markets and bounded option-like instruments. There is no leverage and no liquidation. Each outcome has two sides with their own tokens, and settlement pays a Yes token `settleFraction` quote tokens and a No token the remainder, so the pair always sums to one.

Because buying Yes at `p` is the same trade as selling No at `1 − p`, the two books are merged and share liquidity, and price-time priority generalises to price-side-time priority. Fees are charged only on closing or settling, never on opening, and outcome markets pay no maker rebates.

### Slashing surface

A role whose staked HYPE can be burned by a stake-weighted validator vote when that role's stated conditions fail. Hyperliquid has several, and none is consensus slashing: ordinary validators are jailed for unavailability rather than slashed, and no automatic slashing for double-signing is implemented today.

The surfaces are distinct, each with its own bond and its own condition:

- **[HIP-3](#hip-3-builder-deployed-perpetuals) deployer**, 500 000 HYPE, for irregular market operation, up to the full stake where it causes invalid state transitions or prolonged downtime.
- **Permissionless quote-asset deployer**, 200 000 HYPE committed for three years, for peg and book-depth conditions failing over a three-day window.
- **Aligned stablecoin deployer**, 500 000 HYPE for each of its treasury and technical roles, for failures of the mint, redemption and revenue infrastructure.

Slashed stake is burned rather than paid to affected users, so slashing deters rather than compensates.

## Conclusion

The vocabulary has an uneven shape. The beginner level is mostly ordinary derivatives language plus four proper nouns, so a reader who already knows perpetual futures holds most of it. The real threshold is the intermediate level, and inside it one distinction carries more weight than the others: funding is computed on the oracle price while margin and liquidation run on the mark price. Most confused readings of the protocol trace back to treating those as one number.

The advanced level splits into two halves worth learning separately. One is the solvency ladder with its formulas, which matters to anyone holding a position. The other is the deployable primitives, HIP-1 through HIP-4 and the bonds standing behind them, which matters to anyone building a market rather than trading in one. A reader who wants the mechanisms rather than the definitions should continue with the narrative articles in this series.

![Mindmap of Hyperliquid vocabulary, split into beginner, intermediate and advanced terms including HyperCore, oracle price, mark price, liquidation, auto-deleveraging and the four HIPs]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-glossary-mindmap.png)

The same thirty terms sort a second way, by subject rather than by reading order. That cut shows how much of the vocabulary is really one subject: six of the thirty terms describe margin and the account state it governs, and the four HIPs are one deployment idea applied to four instruments.

![Mindmap grouping Hyperliquid vocabulary by theme, with branches for chain and execution, actors and access, the instrument and the book, prices, margin and account state, when a position fails, and deployable primitives]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-glossary-themes.png)

## Frequently Asked Questions

**Q: What is the difference between the oracle price and the mark price?**

They are computed from different inputs and used for different things.

The [oracle price](#oracle-price) is a two-stage median: each validator takes a weighted median across major spot venues, and the protocol takes a stake-weighted median of what the validators publish, about every three seconds. It drives the [funding rate](#funding-rate), both the premium and the notional the payment is computed on.

The [mark price](#mark-price) is the median of three inputs, one derived from the oracle price and two coming from Hyperliquid's own book and from external perpetual mids. It drives everything touching solvency: initial and [maintenance margin](#maintenance-margin), unrealized profit, stop and take-profit triggers, and [liquidation](#liquidation).

If the question is why a position was liquidated, the mark price is the number to look at. If the question is why a payment appeared on the hour, it is the oracle price.

**Q: Why does a perpetual future need a funding rate?**

A [perpetual future](#perpetual-future-perp) has no expiry, so it lacks the mechanism that pulls a dated future onto its underlying as delivery approaches. With nothing in its place, the contract's price could drift away from spot and stay there.

The [funding rate](#funding-rate) supplies that correction as a recurring payment between the two sides of the market. When the perp trades above the [oracle price](#oracle-price), longs pay shorts, which makes a long more expensive to hold and a short more attractive to open until the gap narrows; below it, the flow reverses. The payment is peer-to-peer and the protocol keeps none of it, so it acts as an anchor rather than as a fee.

**Q: A cross-margin account falls below its maintenance margin. What happens next, and where does auto-deleveraging fit?**

Three stages, in order:

- **Book liquidation.** The protocol sends a market order to the [order book](#central-limit-order-book-clob) for the position. Above 100 000 USDC it goes in 20% increments with a 30-second cooldown, during which any further liquidation order covers the whole position.
- **Backstop liquidation.** If equity falls below two thirds of the [maintenance margin](#maintenance-margin) requirement, the position is transferred to the backstop liquidator inside [HLP](#hlp-hyperliquidity-provider) rather than worked through the book.
- **[Auto-deleveraging](#auto-deleveraging-adl).** If the account value has gone negative anyway, profitable counterparties are ranked and closed against it at the previous mark price.

The first two rungs exist so that the third is rare, but ADL is what makes the guarantee unconditional. It is a state transition rather than a fund that can be exhausted, so an account holding no positions never pays for someone else's loss.

**Q: When would a HyperEVM contract call CoreWriter rather than an L1Read precompile?**

They do opposite things. The [L1Read precompiles](#l1read-precompiles) read HyperCore state as of the moment the EVM block was constructed; [CoreWriter](#corewriter) emits an action that HyperCore executes afterwards. A contract needing to know its own position, an oracle price or a spot balance reads. A contract needing to place an order, cancel one, move funds between sub-accounts or delegate stake writes.

The ordering between the two is what catches integrators. A write issued through CoreWriter is not visible to a read in the same block, and order actions are additionally delayed a few seconds so that going through the EVM buys no latency advantage. A contract that writes and then immediately reads back to confirm will see the old state.

**Q: What breaks if an API wallet address is reused?**

Replay protection. Nonces are tracked per signer rather than per account, and HyperCore keeps only the 100 highest nonces it has seen for that signer. When an [API wallet](#api-wallet-and-the-nonce-set) is deregistered, expires, or its registering account is emptied, that set is pruned.

Register the same address again and the record of what it has already signed is gone. An action signed earlier and captured by anyone can then be submitted a second time and accepted, as long as its nonce still falls in the validity window, which reaches two days back from the current block. The defence is procedural rather than cryptographic: one API wallet per trading process, and never a second registration of an address that has already signed.

**Q: HIP-1 to HIP-4 are numbered like governance proposals. What do they name?**

Not proposals. Nothing about them is voted on and none carries a Draft or Final status; each number labels a primitive already compiled into L1 execution:

- **[HIP-1](#hip-1-native-token-standard)** is a token with a native spot book, its listing gas priced by Dutch auction.
- **[HIP-2](#hip-2-hyperliquidity)** is an operator-free market-making ladder running inside block transition logic.
- **[HIP-3](#hip-3-builder-deployed-perpetuals)** lets a bonded deployer stand up an entire perpetual DEX.
- **[HIP-4](#hip-4-outcome-market)** adds fully collateralised outcome contracts with no leverage.

What the four share is how permission is handled. Entry is open and priced, by auction or by a staked bond, and the deployer answers afterwards to a validator vote able to burn that bond (see [slashing surface](#slashing-surface)).

## References

### Architecture and execution

- [Hyperliquid documentation](https://hyperliquid.gitbook.io/hyperliquid-docs) — the protocol's own reference, and the source for every definition in this article
- [HyperCore overview](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/overview) — the exchange state machine and its components
- [Clearinghouse](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/clearinghouse) — perpetual and spot margin state, sub-accounts, transfer rules
- [Order book](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/order-book) — the intra-block action ordering rule and its three classes
- [Tick and lot size](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/tick-and-lot-size) — the price and size granularity constraints
- [Staking](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/staking) — delegation, self-delegation, jailing, rewards

### Pricing, margin and liquidation

- [Oracle](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/oracle) — the venue weights and the two-stage median
- [Robust price indices](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/robust-price-indices) — the three mark price inputs and the EMA
- [Funding](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding) — the premium, the clamp and the hourly settlement
- [Margining](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margining) — cross, isolated and strict isolated modes
- [Margin tiers](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margin-tiers) — the rate and deduction formula
- [Liquidations](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations) — the book, partial and backstop rungs
- [Auto-deleveraging](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/auto-deleveraging) — the ranking formula and the solvency invariant
- [Portfolio margin](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/portfolio-margin) — LTVs, borrow curve, caps and the liquidation path
- [Protocol vaults](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults/protocol-vaults) — HLP, its strategies and the deposit lock
- [Fees](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees) — the tier table, staking discounts and the Assistance Fund

### HyperEVM and the HIPs

- [Dual block architecture](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/dual-block-architecture) — small and big blocks, and the opt-in flag
- [Interacting with HyperCore](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/interacting-with-hypercore) — the CoreWriter action table and the read precompiles
- [Interaction timings](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/interaction-timings) — the ordering of reads, writes and transfers within a block
- [Nonces and API wallets](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/nonces-and-api-wallets) — the 100-nonce set, the validity window and the pruning hazard
- [HIP-1: Native token standard](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-1-native-token-standard) — the auction, the decimal constraint and the deployment steps
- [HIP-2: Hyperliquidity](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-2-hyperliquidity) — the geometric ladder and its refresh rule
- [HIP-3: Builder-deployed perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals) — the bond, the fee scale and the slashing guidelines
- [HIP-4: Outcome markets](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-4-outcome-markets) — merged books, questions and settlement
- [Permissionless spot quote assets](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/permissionless-spot-quote-assets) — the 200 000 HYPE bond and the depth conditions
- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [Traditional Futures vs. Perpetual Futures: A Technical Comparison]({{site.url_complet}}/2025/12/29/traditional-vs-perpetual-futures/)
- [Automated Market Makers (AMMs) - Overview]({{site.url_complet}}/2025/07/29/automated-market-makers-amm/)
- [Ethereum Staking - How It Works]({{site.url_complet}}/2024/03/28/ethereum-staking/)
