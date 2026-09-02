---
layout: post
title: "The Hyperliquid Protocol - HyperCore, HyperEVM and Onchain Perpetual Mechanics"
date:   2026-09-02
lang: en
locale: en-GB
categories: blockchain defi
tags: hyperliquid defi perpetual derivatives consensus staking oracle
description: How Hyperliquid runs a native order book and an EVM under one HyperBFT consensus, and how its margining, oracles, liquidations and HIP standards work.
image: /assets/article/blockchain/hyperliquid/hyperliquid-protocol.png
isMath: true
---

A decentralised derivatives venue normally keeps its order book off-chain and settles onchain, or replaces the book with an automated market maker. Hyperliquid does neither. The limit order book, the margin engine and the liquidation logic are the state machine that validators agree on, and a general-purpose EVM sits beside them inside the same consensus.

That choice propagates into every part of the design. Block production has to be aware of what an order is, because a naive transaction ordering would let a proposer front-run resting liquidity. Margin has to be re-checked at match time and not only at placement, because oracle prices move between the two. And a smart contract that wants to read the best bid does not call a bridge or an oracle adapter; it calls a precompile that sees HyperCore state as of the moment its own block was built.

This article walks through that architecture from consensus down to the fee schedule: how HyperCore orders actions inside a block, how oracle and mark prices are constructed, what the solvency ladder does between a missed margin call and auto-deleveraging, how the HyperEVM talks to HyperCore in both directions, and what the four HIP standards add on top. It reflects the documentation as of September 2026, which now covers portfolio margin, HIP-4 outcome markets and the migration of USDC away from the Arbitrum bridge.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## One consensus, two execution states

Hyperliquid is a proof-of-stake L1 secured by HyperBFT, a variant of [HotStuff](https://arxiv.org/abs/1803.05069). Validators produce blocks in proportion to the HYPE delegated to them, and consensus proceeds in *rounds*: a bundle of transactions plus signatures from a quorum, where a quorum is any validator set holding more than two thirds of the stake. A committed round is handed to execution. Rounds that carry at least one transaction increment a separate counter, the *height*, which indexes execution blocks.

Execution is split in two. HyperCore holds the margin and matching-engine state: perp and spot clearinghouses, one order book per asset, the oracle, staking, and the token state introduced by the HIP standards. The HyperEVM holds ordinary EVM accounts and contracts. Neither is a separate chain and there is no bridge between them; both are built as part of the same L1 execution, so a HyperEVM contract and a HyperCore order book share a single history.

![HyperBFT validators sign rounds feeding both the HyperCore clearinghouses, order books and oracle and the HyperEVM blocks, with precompiles reading Core state and CoreWriter writing back]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-execution-architecture-concept.png)

The performance target is end-to-end latency, measured from sending a request to receiving a committed response rather than from block to block. For a geographically co-located client that figure has a median of 0.2 seconds and a 99th percentile of 0.9 seconds. Mainnet handles roughly 200k orders per second, and the documentation is explicit that execution, not consensus or networking, is the current bottleneck.

Users do not talk to validators directly. API servers follow a node, keep a local copy of the state, serve it over REST and WebSocket, and forward signed actions to the node they are attached to. The API server holds the request open until the action lands in a committed block, then answers with the L1 execution response, which is why a client sees a fill confirmation rather than a transaction hash to poll.

## HyperCore: the order book as protocol state

### Clearinghouses

The perps clearinghouse owns the margin state of every address: balance and positions. Deposits land in the cross margin balance and positions open in cross mode by default. Isolated margin allocates collateral to one position, so the liquidation risk of that position is disconnected from everything else the account holds. The spot clearinghouse does the same job for token balances and holds.

### Matching and the intra-block ordering rule

Each asset has an order book that behaves like a centralised venue's: prices are integer multiples of a tick size, sizes are integer multiples of a lot size, and matching follows price-time priority. Operations on a perp book take a reference to the clearinghouse, and margin is checked twice: once when a new order is placed, and again for the resting side at every match. The second check exists because the oracle price can move between placement and fill, and without it the margin system would be consistent only at the instant an order arrives.

One rule has no equivalent on a general-purpose chain: the mempool and the consensus logic understand which actions touch a book. Within a block, actions are sorted into three classes before execution:

- **Actions that send no GTC or IOC order to any book.** Post-only (ALO) placements and everything unrelated to aggressive liquidity go first.
- **Cancels.** A market maker's cancel is processed before any aggressive order that could have hit the quote it is pulling.
- **Actions carrying at least one GTC or IOC order.** Aggressive flow executes last.

Inside each class, actions keep the order the proposer put them in. A *modify* is classified by the new order it places. The net effect is that a maker who cancels and an aggressor who takes in the same block resolve in the maker's favour, which removes a category of proposer-level extraction that ordinary first-come-first-served blocks leave open.

![A signed order travels from client to API server to a validator node, is ordered inside a HyperBFT round, then hits the book with margin checked at placement and again at each match]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-order-block-sequence.png)

### Nonces built for a market maker

Ethereum's strictly incrementing nonce is unusable for a strategy sending thousands of orders per second, because it forces a total order on inclusion. HyperCore instead keeps the 100 highest nonces per signer. A new action must carry a nonce larger than the smallest value in that set and must not have been used before, and the nonce has to fall inside the window $$(T - 2\ \text{days},\ T + 1\ \text{day})$$ where $$T$$ is the block's Unix millisecond timestamp. Nonces are tracked per signer, meaning per private key, so the master account and an API wallet (also called an agent wallet) each have their own set.

That last detail is a footgun: two sub-accounts signed by the same API wallet share one nonce tracker, and a deregistered API wallet may have its nonce state pruned, at which point previously signed actions become replayable. The documented advice is to use one API wallet per trading process and never to reuse an agent address.

### Native multi-sig

Multi-sig is a HyperCore primitive rather than a contract. A `ConvertToMultiSigUser` action names the authorised users, up to ten, and the signature threshold; afterwards every action from that account must arrive wrapped in a `MultiSig` action carrying the signatures. The account that submits the wrapper is the *leader*, must itself be an authorised user rather than the multi-sig account, and is the only party whose nonce is checked and updated.

Two consequences matter for anyone deploying this. Converting an account to multi-sig leaves the corresponding HyperEVM account controllable by the original key, and CoreWriter does not work for multi-sig users at all. A multi-sig account should therefore stay off the HyperEVM entirely.

## Prices: oracle, mark price and funding

Three distinct prices do three distinct jobs, and conflating them is the source of most confusion about why a position was liquidated.

**Oracle price** feeds funding. Every validator publishes a spot oracle price for each perp asset roughly every three seconds, computed as the weighted median of Binance, OKX, Bybit, Kraken, KuCoin, Gate.io, MEXC and Hyperliquid spot mid prices with weights 3, 2, 2, 1, 1, 1, 1 and 1. The clearinghouse then takes the stake-weighted median of the validators' submissions. Assets whose primary spot liquidity is on Hyperliquid, such as HYPE, exclude external sources until liquidity justifies them; assets whose liquidity is elsewhere, such as BTC, exclude Hyperliquid spot.

**Mark price** feeds margining, liquidations, TP/SL triggers and unrealised PnL. It is the median of three inputs: the oracle price plus a 150-second exponential moving average of the gap between Hyperliquid's mid and the oracle; the median of Hyperliquid's best bid, best ask and last trade; and the weighted median of Binance, OKX, Bybit, Gate.io and MEXC *perp* mids with weights 3, 2, 2, 1, 1. When only two of the three exist, a 30-second EMA of the second input is added as a fourth candidate. The EMA is maintained as a ratio updated with elapsed time $$t$$ and sample $$x$$:

$$
\begin{aligned}
n &\leftarrow n\,e^{-t/\tau} + x\,t, \qquad
d \leftarrow d\,e^{-t/\tau} + t, \qquad
\text{ema} = \frac{n}{d}
\end{aligned}
$$

with $$\tau = 2.5$$ minutes. Taking a median of three independently sourced indices is what makes a single manipulated venue insufficient to move a liquidation price.

**Funding** is peer-to-peer, paid hourly, and charged at one eighth of the computed eight-hour rate. Writing $$P$$ for the average premium index, $$I$$ for the fixed interest component of 0.01% per eight hours:

$$
\begin{aligned}
F = P + \operatorname{clamp}(I - P,\ -0.0005,\ 0.0005)
\end{aligned}
$$

The premium itself is sampled every five seconds and averaged over the hour. With $$b$$ and $$a$$ the average execution prices for the impact notional on the bid and ask sides and $$o$$ the oracle price:

$$
\begin{aligned}
P = \frac{\max(b - o,\ 0) - \max(o - a,\ 0)}{o}
\end{aligned}
$$

The impact notional is 20 000 USDC for BTC and ETH and 6 000 USDC elsewhere, so the premium reflects the price a real order of that size would pay rather than a top-of-book quote. HIP-3 perps use a more responsive variant, $$P = \tfrac{1}{2}(b + a)/o - 1$$, which gives deployers a wider range of funding behaviour. Funding is capped at 4% per hour, and the payment is computed as position size times *oracle* price times the rate, not mark price.

*Hyperps* are the edge case in this scheme: a Hyperliquid-only perp with no external underlying, where the oracle price is replaced by an eight-hour exponentially weighted moving average of the last day's minutely mark prices, capped at four times the initial mark price. Funding premium samples are taken at 1% of the usual formula. When the underlying eventually lists on Binance, OKX or Bybit spot, the contract converts to a vanilla perp.

## Margin, liquidation and the solvency ladder

### Initial margin, transfer margin, maintenance margin

Opening a position at user-selected integer leverage requires initial margin of position size times mark price divided by leverage. Leverage is validated only at open; afterwards the account holder is responsible for watching it. Unrealised profit on cross positions becomes initial margin for new positions automatically, while on isolated positions it acts as extra margin for that position alone.

Removing margin is stricter than opening. Any action that takes collateral out without trading, including withdrawals, transfers to the spot wallet and isolated margin removals, must leave the account meeting

$$
\begin{aligned}
m_t = \max(m_i,\ 0.1\,V)
\end{aligned}
$$

where $$m_i$$ is the initial margin requirement and $$V$$ the total notional of all open positions. The 10% floor is what stops an account from levering to the maximum and immediately withdrawing the profit.

Maintenance margin is half the initial margin at the asset's maximum leverage. With maximum leverage ranging from 3x to 40x, that puts the maintenance rate between 1.25% and 16.7%. For assets with margin tiers the rate is a function of position size, using the standard tiered formula with a deduction term that keeps total maintenance margin continuous across tier boundaries:

$$
\begin{aligned}
M_n &= V r_n - d_n, \qquad d_0 = 0, \qquad
d_n = d_{n-1} + L_n\,(r_n - r_{n-1})
\end{aligned}
$$

Here $$r_n$$ is the maintenance rate of tier $$n$$, equal to half the initial margin rate at that tier's maximum leverage, and $$L_n$$ is the tier's lower notional bound. On mainnet, BTC runs 40x up to 150M USDC of notional and 20x above; ETH 25x up to 100M then 15x; SOL 20x up to 70M then 10x.

The liquidation price of a position follows from the same quantities:

$$
\begin{aligned}
P_{\text{liq}} = p - s \cdot \frac{m}{q\,(1 - \ell s)}
\end{aligned}
$$

with $$p$$ the entry price, $$s = 1$$ for a long and $$-1$$ for a short, $$q$$ the position size, $$\ell$$ the reciprocal of the maintenance leverage, and $$m$$ the margin available: account value minus maintenance margin for cross, isolated margin minus maintenance margin for isolated. Note what is absent for cross positions: the leverage setting. A cross position at lower leverage simply locks more collateral and liquidates at the same price. For isolated positions leverage does matter, because it determines how much margin was allocated.

### The ladder

![The solvency ladder sends market orders to the book first, hands the position to the backstop liquidator below two thirds of maintenance margin, then auto-deleverages profitable counterparties]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-liquidation-workflow.png)

When account equity falls below the maintenance margin, HyperCore first sends market orders to the book for the full position. Anyone can take the other side, and if the fills restore the margin requirement the trader keeps whatever collateral is left. For positions above 100 000 USDC only 20% is sent, followed by a 30-second cooldown during which any further liquidation order for that user is for the entire position.

If equity keeps falling and reaches two thirds of the maintenance margin without a successful book liquidation, the position moves to a backstop liquidator. For validator-operated perps that is a component strategy of HLP; for a HIP-3 DEX it is a dedicated onchain strategy at `0x400..00 + dex_index`. A backstop-liquidated cross account has its cross positions and cross margin transferred wholesale, and does not get the maintenance margin back, because the vault needs that buffer for backstop liquidations to be profitable on average. Stop-loss orders exist precisely to avoid reaching this rung.

Auto-deleveraging is the last rung and the one that makes the solvency guarantee unconditional. If an account value or isolated position value goes negative anyway, traders on the opposite side are ranked by

$$
\begin{aligned}
\frac{p_m}{p_e} \cdot \frac{N}{A}
\end{aligned}
$$

the ratio of mark to entry price times notional over account value, so the most profitable and most levered counterparties are closed first, at the previous mark price, against the underwater account. Backstop-liquidated positions get no special treatment in that queue. The invariant this preserves is stated without qualification in the documentation: a user with no open positions never socialises platform losses.

## Account abstraction modes and portfolio margin

An account's *abstraction mode* decides how spot and perp balances interact and which assets collateralise perps. Three modes are live:

- **Standard (manual).** Perp and spot balances are separate, and each DEX has its own balance. Cross margin applies within one DEX only. Required for builder-code addresses to accrue builder fees, and recommended for market makers and deployers because it carries no action-rate cap.
- **Unified account.** One balance per asset, shared between spot and every cross margin position denominated in that asset. A USDC balance collateralises validator-operated perps, HIP-3 perps quoted in USDC, and spot trading against USDC at once.
- **Portfolio margin.** A single portfolio spanning all currently eligible assets, namely HYPE, BTC, USDC and USDT, with automatic borrowing and lending against the idle balance.

Unified account and portfolio margin are capped at 50 000 user actions per day. For API consumers, both report all balances and holds through the spot clearinghouse state, and the per-DEX perp user states stop being meaningful. A fourth mode, DEX abstraction, has been discontinued.

Portfolio margin is the most involved of the three. Eligible collateral carries a loan-to-value ratio: 0.65 for HYPE, 0.5 for BTC. Placing an order without sufficient balance borrows automatically, up to the token balance times its borrow oracle price times its LTV. Borrowed assets accrue interest continuously and are indexed hourly to match the funding interval, and the stablecoin borrow rate is a two-slope curve in utilisation $$u$$:

$$
\begin{aligned}
r = 0.05 + 4.75 \cdot \max(0,\ u - 0.8)
\end{aligned}
$$

Suppliers earn the same rate on idle balances, less the 10% the protocol retains as a liquidation buffer. Eligibility is bounded on both ends, with a master account needing either $5$M in weighted volume or $10$k of account value to opt in and an account value below $25$M to stay in, and each asset has global and per-user supply and borrow caps; when a cap binds, the account falls back to non-portfolio behaviour.

The motivating trade is the cash-and-carry. Holding 1 BTC spot and shorting 1 BTC-USDC perp at 10x, the trader pays interest only on the initial margin while earning funding on the full notional, and spot and perp PnL offset each other for margin purposes. If BTC rallies from 100k to 150k, portfolio margin borrows 50k USDC against the appreciated spot leg rather than liquidating the short. The hedged price range is considerably wider than for the same trade collateralised by USDC alone, which is what the mode is for.

Liquidation under portfolio margin generalises cross margin across the whole account, triggering when the portfolio margin ratio exceeds 0.95, with all notionals converted to USDC at the borrow oracle price. Positions are taken over by a backstop liquidator at system address `0xbbb...b`, in full below the full-liquidation threshold and in 20% increments between the partial and full thresholds, stopping as soon as the account is healthy. There is no market-liquidation phase as there is for perps, because spot books have less consistent depth; the liquidator instead unwinds collateral into the debt asset on a TWAP with a ten-minute half-life. Two behaviours should be understood before enabling it: sub-accounts are margined separately, and the order in which perp positions and spot borrows are liquidated depends on the order of oracle updates, so it is not deterministic.

## HyperEVM

The HyperEVM runs the Cancun hardfork without blobs, on chain ID 999 for mainnet and 998 for testnet, with HYPE as the native gas token at 18 decimals. [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) is enabled and base fees are burned in the usual way. Priority fees are burned too, sent to the zero address's EVM balance, because HyperBFT leaves nothing for a block builder to bid for.

### Dual blocks

Throughput is split between two interleaved block types drawing from two independent onchain mempools, sharing one increasing sequence of EVM block numbers. Small blocks are produced every second with a 3M gas limit; big blocks every minute with a 30M gas limit. A block duration of $$x$$ means the first L1 block for each value of `l1_block_time % x` produces an EVM block. The point is to stop block size and block latency from trading off against each other: a user wanting fast confirmation and a builder deploying a large contract are served by different lanes.

Targeting big blocks is a HyperCore user-level flag, set with `{"type": "evmUserModify", "usingBigBlocks": true}` and unset the same way. Because it is a HyperCore action, the deployer address must already exist as a Core user, which for a fresh EOA means receiving a Core asset first. The `bigBlockGasPrice` JSON-RPC method estimates the base fee of the next big block. The mempool accepts only the next eight nonces per address and prunes transactions older than a day.

### Reading HyperCore

Read precompiles start at `0x0000000000000000000000000000000000000800` and expose perp positions, spot balances, vault equity, staking delegations, oracle prices and the L1 block number. Their values are guaranteed to match HyperCore state at the time the EVM block was constructed. Gas is `2000 + 65 * (input_len + output_len)`, and an invalid input, such as an unknown asset or vault address, returns an error after consuming all gas passed into the precompile frame, so a contract that calls one speculatively has to bound the gas it forwards.

Returned prices are integers. Dividing by $$10^{6 - \text{szDecimals}}$$ gives a perp price and $$10^{8 - \text{szDecimals}}$$ a spot price, where `szDecimals` belongs to the base asset.

### Writing to HyperCore

The CoreWriter system contract at `0x3333333333333333333333333333333333333333` burns about 25 000 gas and emits a log that HyperCore processes as an action, for a realistic total near 47 000 gas. The payload is a byte string: byte 1 is the encoding version, currently 1; bytes 2 to 4 are a big-endian action ID; the remainder is the raw ABI encoding of the action's Solidity types.

The action set is broad enough to build a real application. Limit orders and both cancel variants cover trading; vault transfers, staking deposits and withdrawals, token delegation, spot sends, asset sends and USD class transfers cover treasury movement; `Add API wallet`, `Approve builder fee` and `Set abstraction` cover account configuration; `Finalize EVM Contract` completes a Core-to-EVM token link; and the newer `Borrow lend operation` and `Outcome operation` reach portfolio-margin supply/withdraw and HIP-4 split, merge and negate respectively.

One constraint shapes every design that uses it: order actions and vault transfers sent through CoreWriter are delayed onchain by a few seconds, so the HyperEVM cannot be used to bypass the L1 mempool for a latency advantage. Such actions appear twice in the L1 explorer, once when enqueued and once when executed. Since a user already waits for a small-block confirmation, the delay is invisible in practice but fatal to a strategy that assumed otherwise.

### Moving assets between the two states

Every HIP-1 token has a HyperCore *system address*: first byte `0x20`, remaining bytes zero except for the big-endian token index. Token index 200 gives `0x20000000000000000000000000000000000000c8`. HYPE is the exception, using `0x2222222222222222222222222222222222222222` and mapping to the native HyperEVM balance rather than an ERC-20.

Once a Core token and an EVM contract are linked, a Core-to-EVM transfer is a `sendAsset` action to the system address, credited by a system transaction that calls `transfer(recipient, amount)` on the linked contract; the reverse is an ordinary ERC-20 transfer to the system address, credited on HyperCore from the emitted `Transfer` event. Core to EVM costs 200 000 gas at the next block's base fee; EVM to Core costs about what any ERC-20 transfer to a funded address costs.

The linking flow is deliberately two-sided. The deployer sends a spot deploy action naming the EVM address, and the EVM side then proves intent either by sending an action with the nonce that deployed the contract, or, for contract-deployed contracts, by storing a finalizer address in the first storage slot or at `keccak256("HyperCore deployer")`.

The caveats section of that page is unusually blunt, and it lands on the integrator rather than the protocol. Nothing verifies that the system address holds sufficient supply, and nothing verifies that the linked contract is a valid ERC-20. The linked contract can carry arbitrary bytecode, and there is no guarantee about what its `transfer` does. If the EVM contract has extra wei decimals, any log value that is not a round multiple has the remainder burned, bounded by one wei. Fungibility between Core spot and EVM spot is a property of a specific deployment, not of the protocol.

Ordering inside a block that produces an EVM block is fixed: the L1 block is built, then the EVM block, then EVM-to-Core transfers, then CoreWriter actions. Core-to-EVM transfers wait for the next EVM block. The consequence that catches integrators is that an account performing a CoreWriter action must already exist on HyperCore before the EVM block is built; initialising it with an EVM-to-Core transfer in the same block still leaves the CoreWriter action rejected.

## The HIP standards

### HIP-1: native tokens and spot books

HIP-1 defines a capped-supply fungible token together with onchain spot order books between pairs of such tokens. A genesis transaction fixes a name of at most six characters with no uniqueness constraint, `weiDecimals` for the integer-to-float conversion, `szDecimals` for the tradable lot size subject to `szDecimals + 5 <= weiDecimals`, the maximum and initial supply, optional genesis balances, optional proportional genesis to holders of an existing anchor token, and HIP-2 initialisation parameters.

Deployment gas is set by a 31-hour Dutch auction, decreasing linearly from twice the previous clearing price down to a floor of 500 HYPE, with the floor also used as the starting price when the previous auction failed to clear. The documentation warns that the auction step is the only time-sensitive one and that a stuck multi-stage deployment cannot be refunded, so testnet rehearsal is not optional.

Trading fees collected in a non-USDC base token go to that token's deployer by default; the deployer can lower the share and, once lowered, can never raise it again, and the portion not redirected is burned. Legacy tokens deployed before the mechanism existed get one upward adjustment from zero. Spot dust below one lot size and one dollar of notional is swept daily at 00:00 UTC by aggregating all users' dust into a single market sell, with proceeds redistributed proportionally, skipped when the book is one-sided or the aggregate would move the market.

### HIP-2: Hyperliquidity

Hyperliquidity is an onchain market-making strategy executed by block transition logic, with no operator and no keeper transactions. It is parametrised by a spot asset, a starting price, an order count, a full order size, and a number of seeded bid levels. The price ladder is geometric:

$$
\begin{aligned}
p_0 = p_s, \qquad p_i = \operatorname{round}(1.003 \cdot p_{i-1})
\end{aligned}
$$

The strategy updates on any block at least three seconds after the previous update, targeting $$\lfloor \text{balance} / \text{orderSz} \rfloor$$ full ask orders plus one partial, and refilling each fully filled tranche on whichever side has balance. The result is a guaranteed 0.3% spread refreshed every three seconds, resting inside the same general-purpose book that human market makers quote into, so external liquidity can grow alongside it rather than in a separate pool.

### HIP-3: builder-deployed perpetuals

HIP-3 lets anyone deploy a perp DEX with its own margining, order books and settings, inheriting the HyperCore stack and API. The deployer defines the market, including its oracle and contract specifications, and operates it, including publishing oracle prices, setting leverage limits and settling via `haltTrading`, which cancels all orders and settles positions to the current mark price and can be reversed to recycle the asset for a new dated contract.

The economic bond is 500 000 staked HYPE, held for at least 183 days after deployment. The first three assets in a DEX skip the auction; further assets go through a Dutch auction shared across all perp DEXs, with each deployer also receiving $$7 + 0.2 n$$ reserve deployments usable at the current auction price without waiting for the timer. Deployers configure a fee share between 0% and 300%, where a share above 100% also raises the protocol fee to match.

Slashing is the enforcement mechanism, decided by stake-weighted validator vote, and the guidelines are explicit that it is technical rather than moral: it does not distinguish a deployer who deviated from a good spec, one who faithfully followed a bad spec, and one whose keys were stolen. The rough scale is up to 100% for irregular inputs causing invalid state transitions or prolonged downtime, up to 50% for brief downtime, and up to 20% for network degradation. Slashed stake is burned rather than distributed to affected users, on the reasoning that paying out victims would misalign incentives between users and deployers. Any team running an LST on top of a HIP-3 deployer inherits this risk and needs to say so to its depositors.

Cross margin on a HIP-3 asset is irreversible once enabled, and validators enforce eligibility standards on it: observable liquidity, a reliable external oracle, and resistance to manipulation. Each time an asset's `externalPerpPx` moves more than 50% from the start-of-day price, validators review whether the deployer should be slashed, and any asset where such moves are expected more than once a month is ineligible.

### HIP-4: outcome markets

HIP-4 adds fully collateralised contracts settling within a fixed range, which covers prediction markets and bounded option-like instruments without leverage or liquidations. Each market has two sides with a token each, typically Yes and No, and settlement converts Yes into `settleFraction` quote tokens and No into `1 - settleFraction`.

The two books are merged, since buying Yes at $$p$$ is selling No at $$1 - p$$, and price-time priority accordingly generalises to price-side-time priority: at the same merged price level, resting sells sort before resting dual buys. *Questions* group outcomes where exactly one settles to Yes, linked by `negate` and `merge` operations so a holder of No shares across every outcome of a question can redeem quote tokens before settlement. Advanced users can split and merge manually to move between primary and dual balances.

The first mainnet market is a recurring binary settling daily at 06:00 UTC against the BTC mark price on HyperCore, using linear interpolation between the mark price updates immediately before and after the settlement timestamp. Fees are currently zero while the primitive is being tested, though builder codes still earn on sell orders.

## Quote assets, fees and where value goes

### Becoming a quote asset

Any token can become a spot quote asset permissionlessly, subject to `weiDecimals = 8`, `szDecimals = 2`, a zero deployer fee share, and 200 000 staked HYPE committed for three years. The stake is slashable by validator vote against measurable book-quality conditions: QUOTE/USDC must show 100 000 USDC of size on both sides between 0.998 and 1.002 and 1M USDC between 0.99 and 1.01, and HYPE/QUOTE must show 50 000 QUOTE on both sides within a 0.5% spread. A condition failing for a majority of one-second samples over three days makes the asset slashable. USDC and USDT are exempt from the staking requirement.

### Aligned quote assets

Alignment is an opt-in revenue-share arrangement layered on quote-asset status. Under AQAv1, a deployer stakes 800 000 HYPE beyond the quote-asset requirement, for 1M total, and routes 50% of the AQA rate to the protocol, where the rate is a stake-weighted median of validator-reported values. In exchange the asset gets 20% lower taker fees, 50% larger maker rebates, and 20% more volume contribution toward fee tiers. Offchain conditions, enforced by validator quorum rather than by execution, require 1:1 backing by cash and short-term treasuries, par redemption, native minting on the HyperEVM as the source chain, and a deployer that takes no rate-linked compensation for conversions.

AQAv2 drops the exclusivity requirement and roughly doubles the share, with deployers passing about 90% of cost-adjusted reserve yield on their Hyperliquid supply. It splits the role into a *treasury deployer* and a *technical deployer*, each staking 500 000 HYPE, each requiring six months' notice before ceasing operation, and both slashable. Minted supply is held 9:1 between the treasury address and the technical deployer's linked EVM contract. Revenue accrues over 30-day intervals and is swept to the Assistance Fund eight days after each interval closes; an insufficient balance at the system interest address `0x50...00 + {token_index}` makes the treasury deployer's stake slashable at 2% per day. A future upgrade will make AQAv2 a requirement for quote assets listed against HIP-4 and validator-operated perp markets.

### Fees

Fee tiers use rolling 14-day volume assessed daily in UTC, with spot counted twice:

$$
\begin{aligned}
W = V_p + 2\,V_s
\end{aligned}
$$

One tier applies across perps, HIP-3 perps and spot. The base perp rate is 0.045% taker and 0.015% maker, falling to 0.024% taker at the top tier; spot starts at 0.070% and 0.040%. Staking HYPE layers a discount on top, from 5% above 10 HYPE to 40% above 500 000. Spot pairs between two quote assets pay 80% less. Growth mode for a HIP-3 perp cuts all-in fees, rebates and volume contribution by at least 90%, conditional on a deployer fee scale between 0 and 10 and on the market being disjoint from validator-operated perps, which rules out crypto perps, crypto indices, and duplicates of existing markets such as a gold perp competing with PAXG-USDC.

The destination of those fees is not an operator. There is no clearance fee on liquidations, and the profit stream from backstop liquidation accrues to HLP rather than to the operator or to privileged market makers. Protocol fees flow to HLP, to deployers, and to the Assistance Fund at `0xfefefefefefefefefefefefefefefefefefefefe`, which converts them to HYPE as part of L1 execution and burns the result, removing it from circulating and total supply.

Two operational details bite. Builder-code addresses must sit in standard abstraction mode to accrue builder fees. And staking-to-trading account linking, which attributes a staking account's HYPE to a trading account's fee tier, is permanent, unilateral in the staking account's favour, and lets that account irreversibly drain or lock the trading account; the two must be controlled by the same person.

### Vaults

The current vault model is a HyperEVM contract using CoreWriter and precompiles, with fully customisable accounting. A builder can follow [ERC-4626](https://eips.ethereum.org/EIPS/eip-4626), tokenise the share, trade on HyperCore through CoreWriter, delegate authorised agents, and read its own position back through precompiles for onchain accounting. This supersedes the legacy HyperCore vaults introduced in 2023, which support neither HIP-3 nor spot trading. HLP itself is a protocol vault: it market-makes, performs backstop liquidations, supplies USDC in Earn, accrues a share of trading fees, and imposes a four-day lock-up after each deposit.

## Staking, validators and slashing surfaces

HYPE staking happens inside HyperCore, with HYPE moving between spot and staking accounts the same way USDC moves between perp and spot. A validator needs 10 000 HYPE of self-delegation, locked for a year, to become active; dropping below that threshold puts it into undelegate-only mode, where its stake can only shrink. Commission can be raised only to a value at or below 1%, which forecloses the pattern of attracting stake cheaply and then repricing it.

Delegations lock for one day, after which undelegation is instant into the staking account. Moving from staking to spot goes through a seven-day queue with at most five pending withdrawals per address. Rewards accrue every minute and are distributed and compounded daily, based on the minimum balance held during each staking epoch of 100 000 rounds, roughly 90 minutes. The reward rate is inversely proportional to the square root of total stake, giving about 2.37% per year at 400M HYPE staked, funded from the future emissions reserve.

The validator set is static within an epoch. Validators can vote to *jail* a peer whose consensus responses are too slow or too infrequent; a jailed validator stops participating and stops producing rewards for its delegators until it unjails itself, subject to onchain rate limits. Jailing is not slashing. Slashing is reserved for provably malicious behaviour such as double-signing at the same round, and the documentation states plainly that no automatic slashing is currently implemented for ordinary validators.

That leaves three distinct slashing surfaces to keep separate when reasoning about risk, none of which is consensus slashing: HIP-3 deployers with 500 000 HYPE at stake for market operation, quote-asset deployers with 200 000 HYPE at stake for peg and book quality, and aligned-stablecoin deployers with 500 000 HYPE each for revenue delivery and infrastructure. A delegator choosing a validator that is also a HIP-3 deployer, or an LST accepting deposits from one, is exposed to a risk that ordinary delegation does not carry.

## USDC and the legacy bridge

USDC is now natively minted on the Hyperliquid L1 through Circle's CCTP, with Circle's contracts deployed on the HyperEVM and audited independently. The original Arbitrum bridge is deprecated and holds less than 10% of HyperCore's USDC supply.

The legacy bridge is still instructive, because its design states the protocol's trust model in the most explicit terms available. Deposits are credited once validators holding more than two thirds of stake have signed them. Withdrawals are deducted from the L1 balance immediately, then signed by validators as separate transactions; at a two-thirds quorum an Arbitrum transaction can request the withdrawal. A dispute period follows, during which cold-wallet signatures from two thirds of the stake-weighted validator set can lock the bridge against a withdrawal that does not match L1 state, and unlocking requires the same cold-wallet quorum. Finalisation then distributes USDC to destinations. The user pays no Arbitrum gas: a 1 USDC withdrawal fee on Hyperliquid covers the validators' costs, and funds arrive in three to four minutes. The minimum deposit is 5 USDC, and anything below it is lost. The bridge and its relationship to L1 staking were audited by Zellic in two reports.

## Trust assumptions and known risk surfaces

Reading the design as a whole, the assumptions a user or integrator takes on are these.

- **Consensus honesty.** More than two thirds of staked HYPE must be non-Byzantine. This is the base assumption of HyperBFT and it is inherited by everything else: the order book, the bridge quorum, and every validator vote.
- **Oracle honesty and liveness.** Mark and oracle prices come from validator submissions aggregated by stake-weighted median. Median-of-medians across eight spot venues and five perp venues makes single-venue manipulation expensive, but a colluding stake majority sets the price that liquidates positions.
- **Validator votes as a governance surface.** Quote-asset slashing, HIP-3 slashing, growth-mode eligibility, AQA activation and delistings are all validator votes on conditions that are partly offchain. This is a deliberate design choice, stated as such, rather than an oversight, but it is discretion nonetheless.
- **Deployer competence on HIP-1 and HIP-3.** A linked EVM contract can hold arbitrary bytecode; a HIP-3 oracle is whatever its deployer publishes. Slashing punishes the deployer after the fact and burns the stake rather than compensating users.
- **Application-layer risk on the HyperEVM.** Contracts calling CoreWriter inherit its delay semantics and its account-existence precondition, and contracts calling precompiles inherit the all-gas-consumed failure mode.

The bug bounty programme classifies findings by impact, with critical issues, meaning significant loss of user funds or a violation of L1 execution invariants, paying up to 1M USDC, network downtime without incorrect state up to 50 000 USDC, and API server performance issues up to 10 000 USDC. Reports go to the Hyper Foundation directly rather than through a platform, and testing against mainnet is prohibited.

## Conclusion

On Hyperliquid the exchange is the state machine rather than an application running on one. Putting the order book inside consensus is what allows the intra-block ordering rule that puts cancels ahead of aggressive orders, the second margin check on the resting side at match time, and a solvency ladder whose last rung is enforced by execution rather than by an insurance fund's balance. Putting a general-purpose EVM inside the same execution is what removes the bridge between contract logic and order book liquidity, at the cost of a delay on CoreWriter orders and a set of linking caveats that place real verification work on the integrator.

The recent additions extend the same pattern in both directions. Portfolio margin folds spot balances, borrowing and perp positions into one margin computation, which widens the range over which a carry trade stays hedged while introducing a non-deterministic liquidation ordering. HIP-4 adds a settled, fully collateralised primitive with no liquidation at all. And the trust surface has consolidated onto validator votes: quote-asset quality, HIP-3 market operation and aligned-stablecoin revenue are all enforced by stake-weighted vote against conditions that are partly observed off-chain, with slashed stake burned rather than paid to affected users.

![Mindmap of Hyperliquid covering HyperBFT consensus, HyperCore, the risk engine, account abstraction modes, the HyperEVM, the four HIP standards and the fee economics]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-protocol.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **HyperBFT** | Hyperliquid's HotStuff-derived proof-of-stake consensus, proceeding in rounds committed by a quorum holding more than two thirds of staked HYPE. |
| **HyperCore** | The native execution state holding the perp and spot clearinghouses, the order books, the oracle, staking and HIP token state. |
| **HyperEVM** | The general-purpose EVM execution state built inside the same L1 blocks as HyperCore, on chain ID 999, with HYPE as its gas token. |
| **Clearinghouse** | The HyperCore component that owns each address's margin state, positions and balances, and against which every order book operation checks margin. |
| **Mark price** | The median of three robust price inputs, used for margining, liquidation, TP/SL triggering and unrealised PnL, and distinct from the oracle price used for funding. |
| **Backstop liquidator** | The vault or system strategy that takes over a position once account equity falls below two thirds of the maintenance margin, keeping the maintenance margin as its buffer. |
| **Auto-deleveraging (ADL)** | The final solvency rule, closing the most profitable and most levered counterparties at the previous mark price against an account whose value has gone negative. |
| **CoreWriter** | The system contract at `0x3333...3333` through which a HyperEVM contract emits an encoded action for HyperCore to execute, with orders and vault transfers delayed a few seconds. |
| **System address** | The HyperCore address encoding a token index (`0x20` followed by the big-endian index, or `0x2222...` for HYPE) that acts as the transfer endpoint between Core and EVM spot. |
| **Aligned quote asset** | A stablecoin whose deployer stakes HYPE and shares reserve yield with the protocol in exchange for reduced fees, larger rebates and greater volume contribution. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A user with no open positions never socialises platform losses. | The ADL queue closes profitable counterparties before any shortfall can be mutualised. | ADL is disabled or an account's value can go negative without triggering it. |
| Margin remains consistent despite oracle movement between placement and fill. | A margin check on order placement plus a second check for the resting side at each match. | The resting-side check at match time is skipped as an optimisation. |
| A cancel submitted in the same block as an aggressive order is processed first. | The three-class intra-block action ordering in the mempool and consensus logic. | Actions are ordered purely by proposer sequence, as on a general-purpose chain. |
| A precompile read reflects HyperCore state as of the EVM block's construction. | HyperEVM blocks are built inside L1 execution, after which EVM-to-Core transfers and CoreWriter actions run. | The EVM is moved to a separate chain or reads become asynchronous. |
| The HyperEVM offers no latency advantage over the L1 mempool. | CoreWriter order actions and vault transfers are enqueued onchain and executed a few seconds later. | The delay is removed, at which point contract-routed orders could front-run direct ones. |
| Withdrawals through the legacy bridge match L1 state. | Two-thirds stake-weighted signatures, a dispute period, and a cold-wallet quorum able to lock the bridge. | The dispute window closes before a mismatched withdrawal is contested. |
| A quote asset holds its peg and book depth or its deployer is slashable. | Measurable depth conditions sampled once per second, with a three-day violation window and a validator vote. | The conditions are met at sample times but not between them, or the vote does not carry. |
| Assistance Fund revenue leaves circulation. | L1 execution converts collected fees to HYPE at `0xfefe...fe` and burns them. | The conversion or burn is changed to a distribution. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| A CoreWriter action from an account that does not yet exist on HyperCore is rejected, even if an EVM-to-Core transfer initialises it in the same block. | Initialise the account in an earlier block, and verify existence before emitting the action. |
| Precompiles consume all gas passed into their call frame on invalid input. | Validate asset indices and vault addresses before the call, and bound the gas forwarded to it. |
| A linked EVM contract may hold arbitrary bytecode, and nothing checks that the system address holds sufficient supply. | Read the linked contract's source and the system address balance before treating Core and EVM spot as fungible. |
| Extra wei decimals on a linked contract cause non-round transfer amounts to have the remainder burned. | Round transfer amounts to the token's `extraEvmWeiDecimals` before sending. |
| Nonces are per signer, and a deregistered API wallet may have its nonce state pruned, making old actions replayable. | Use one API wallet per trading process, never reuse an agent address, and generate a fresh one on rotation. |
| Under unified account and portfolio margin, per-DEX perp user states stop being meaningful and everything appears in the spot clearinghouse state. | Read balances from the spot clearinghouse state and compute the unified account ratio rather than reading per-DEX equity. |
| Builder-code addresses accrue no builder fees outside standard abstraction mode. | Keep builder addresses in standard mode and separate them from any account using portfolio margin. |
| Converting an account to multi-sig leaves its HyperEVM counterpart controllable by the original key, and CoreWriter does not work for multi-sig users. | Keep multi-sig accounts off the HyperEVM entirely, before and after conversion. |
| Portfolio margin liquidation order between perp positions and spot borrows depends on the order of oracle updates. | Do not build unwind logic that assumes a fixed sequence; monitor the portfolio margin ratio instead. |
| Funding is charged on the oracle price, while margining uses the mark price. | Use the oracle price when projecting funding cost and the mark price when projecting liquidation. |

## Frequently Asked Questions

**Q: Why does HyperCore check margin twice for a single fill, once at placement and once at match?**

Because the two checks answer different questions at different times. The placement check confirms the account can support the order when it is submitted. The match check confirms the *resting* side can still support the position at the moment the fill happens, which may be many seconds and several oracle updates later.

Without the second check, a resting order placed when the account was healthy could fill after the mark price had moved against it, opening a position the account could no longer margin. Checking only at placement would make the margin system consistent at submission time and inconsistent everywhere else.

**Q: What is the difference between the oracle price and the mark price, and which one liquidated my position?**

The oracle price is a weighted median of spot mid prices, published by each validator roughly every three seconds and aggregated by stake-weighted median. Its inputs are external spot venues, plus Hyperliquid spot for assets whose primary spot liquidity is on Hyperliquid; it never reads a perp book, which is what makes it a clean funding input.

The mark price is the median of three inputs: the oracle price adjusted by a 150-second EMA of Hyperliquid's basis, the median of Hyperliquid's best bid, best ask and last trade, and a weighted median of five external perp mids.

Margining, liquidation, TP/SL triggering and unrealised PnL all use the mark price, so that is what liquidated the position. Funding uses the oracle price, both for the premium and for converting position size to notional in the payment itself.

**Q: An account is below maintenance margin. What happens next, in order?**

Three rungs, in this sequence:

- **Market liquidation.** The full position is sent to the book as a market order, or 20% of it when the position exceeds 100 000 USDC, followed by a 30-second cooldown during which any further order is for the full size. If fills restore the requirement, the remaining collateral stays with the trader.
- **Backstop liquidation.** Once equity falls below two thirds of the maintenance margin without a successful book liquidation, the position and its margin transfer to the backstop liquidator, which is an HLP strategy for validator-operated perps or the `0x400..00 + dex_index` strategy for a HIP-3 DEX. The maintenance margin is not returned.
- **Auto-deleveraging.** If account value still goes negative, counterparties are ranked by mark-over-entry times notional-over-equity and closed at the previous mark price against the underwater account.

Only the first rung leaves residual collateral with the trader, which is the argument for stop-loss orders over relying on liquidation.

**Q: Why can a HyperEVM contract not use CoreWriter to get a latency advantage over a direct L1 order?**

Order actions and vault transfers emitted through CoreWriter are enqueued onchain and executed a few seconds later, deliberately. They appear twice in the L1 explorer, once as an enqueue and once as a HyperCore execution.

The reason is that without the delay, a contract could bypass the L1 mempool and its ordering rules, giving contract-routed flow a latency edge over ordinary orders. Since any user of the HyperEVM already waits at least one small-block confirmation, the delay costs nothing in practice, but it does invalidate any strategy that assumed CoreWriter was a fast path.

**Q: An account holds 1 BTC spot and a 1 BTC short perp. What changes when portfolio margin is enabled?**

Without portfolio margin, the perp leg is collateralised by USDC alone. A rally forces the account either to post more USDC or to unwind, even though the spot leg has appreciated by exactly the perp leg's loss.

With portfolio margin, spot and perp PnL offset each other in one margin computation, and a shortfall is met by borrowing automatically against the spot BTC up to its balance times its borrow oracle price times its 0.5 LTV. A rally from 100k to 150k borrows 50k USDC against the appreciated collateral instead of liquidating.

The trade-offs are real: borrowing accrues interest at $$0.05 + 4.75\max(0, u - 0.8)$$ APY on stablecoins, the account is capped at $25$M of value and by global and per-user borrow limits, and the position becomes liquidatable when the portfolio margin ratio passes 0.95 with no market-liquidation phase to soften it.

**Q: How does the intra-block ordering rule change what a market maker can be hit by?**

Actions are sorted into three classes before execution: everything that sends no GTC or IOC order, then cancels, then anything carrying at least one GTC or IOC order. Proposer order applies only within a class.

For a maker this means a cancel submitted in the same block as an aggressive order that would have hit the quote is processed first, regardless of which arrived at the proposer earlier. The stale-quote exposure that ordinary transaction ordering creates is therefore bounded by block time rather than by the proposer's discretion, which is why the documentation calls the mempool semantically aware of order book actions.

**Q: A HIP-3 deployer publishes an oracle price that liquidates users. What does the protocol do?**

Validators can slash the deployer's 500 000 staked HYPE by stake-weighted vote, and the stake stays slashable throughout the seven-day unstaking queue even after withdrawal is initiated. The guideline scale runs to 100% for irregular inputs causing invalid state transitions or prolonged downtime, 50% for brief downtime, and 20% for network degradation.

Two properties of that mechanism are easy to miss. Slashing does not distinguish malice from incompetence from a key compromise, since only the effect on the protocol is judged. And slashed stake is burned rather than distributed to affected users, on the stated reasoning that paying out victims would misalign incentives between users and deployers. A HIP-3 market's users are protected by the deployer's incentive not to be slashed, not by a compensation fund.

**Q: What makes the ADL invariant stronger than an insurance fund?**

An insurance fund is a balance, so its guarantee is conditional on that balance being large enough on the day it is needed. ADL is a state transition: when an account value goes negative, profitable counterparties are closed at the previous mark price until the shortfall is absorbed, which cannot fail for lack of funds.

The cost is borne by traders holding profitable, levered positions in the same asset rather than by the platform, which is why the ranking index weights both profit and leverage. The invariant it buys is that a user with no open positions never socialises a loss, and that holds under every operation rather than up to a fund's size.

## References

### Protocol documentation

- [Hyperliquid Docs](https://hyperliquid.gitbook.io/hyperliquid-docs) — the complete documentation set, read for this article on 2 September 2026
- [HyperCore overview](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/overview) — consensus, execution split, latency and throughput
- [Clearinghouse](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/clearinghouse) and [Order book](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/order-book) — margin state and the intra-block ordering rule
- [Oracle](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/oracle) and [Robust price indices](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/robust-price-indices) — oracle weights, mark price components, EMA definition
- [Staking](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/staking) — delegation, epochs, jailing and reward rate
- [Multi-sig](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/multi-sig) — native multi-signature accounts

### Trading and risk mechanics

- [Margining](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margining) and [Margin tiers](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margin-tiers) — margin modes, transfer requirement, tier formula
- [Liquidations](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations) and [Auto-deleveraging](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/auto-deleveraging) — the solvency ladder and the ADL ranking index
- [Funding](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding) — funding rate formula, premium sampling, impact notional
- [Account abstraction modes](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/account-abstraction-modes) and [Portfolio margin](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/portfolio-margin) — the three modes, LTVs, borrow curve and caps
- [Contract specifications](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications) and [Hyperps](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/hyperps) — quanto margining and the Hyperliquid-only perp design
- [Fees](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees) — tier tables, staking discounts, growth mode, Assistance Fund

### HyperEVM and developer interfaces

- [HyperEVM for developers](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm) — chain IDs, hardfork, fee burning
- [Dual-block architecture](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/dual-block-architecture) — small and big blocks, `evmUserModify`
- [Interacting with HyperCore](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/interacting-with-hypercore) — precompiles, CoreWriter encoding, action table
- [HyperCore and HyperEVM transfers](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/hypercore-less-than-greater-than-hyperevm-transfers) — system addresses, linking flow, caveats
- [Interaction timings](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/interaction-timings) — ordering inside a block that produces an EVM block
- [Nonces and API wallets](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/nonces-and-api-wallets) — the 100-nonce set and agent wallet pruning
- [Asset IDs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/asset-ids) — perp, spot, HIP-3 and outcome encodings

### Improvement proposals and asset standards

- [HIP-1: Native token standard](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-1-native-token-standard)
- [HIP-2: Hyperliquidity](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-2-hyperliquidity)
- [HIP-3: Builder-deployed perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals)
- [HIP-4: Outcome markets](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-4-outcome-markets)
- [Permissionless spot quote assets](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/permissionless-spot-quote-assets) and [Aligned quote assets](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/aligned-quote-assets)
- [Vaults](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults) and [Protocol vaults](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults/protocol-vaults) — the CoreWriter vault model and HLP

### Bridging, audits and security

- [USDC on HyperCore](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/usdc) and [USDC API reference](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/usdc) — CCTP minting and the deprecated Arbitrum bridge
- [Circle CCTP: transferring USDC from Arbitrum to HyperCore](https://developers.circle.com/cctp/howtos/transfer-usdc-from-arbitrum-to-hypercore)
- [circlefin/hyperevm-circle-contracts](https://github.com/circlefin/hyperevm-circle-contracts) — Circle's published contracts and flows
- [hyperliquid-dex/contracts — Bridge2.sol](https://github.com/hyperliquid-dex/contracts/blob/master/Bridge2.sol) — legacy bridge source, read on 2 September 2026 from the `master` branch
- [Audits](https://hyperliquid.gitbook.io/hyperliquid-docs/audits) — the two Zellic reports on the legacy bridge
- [Bug bounty program](https://hyperliquid.gitbook.io/hyperliquid-docs/bug-bounty-program) — scope and severity classification

### External standards and papers

- [EIP-1559: Fee market change for London](https://eips.ethereum.org/EIPS/eip-1559)
- [ERC-4626: Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-4626)
- [HotStuff: BFT Consensus in the Lens of Blockchain](https://arxiv.org/abs/1803.05069) — the consensus family HyperBFT derives from

### Related articles

- [Traditional Futures vs. Perpetual Futures: A Technical Comparison]({{site.url_complet}}/2025/12/29/traditional-vs-perpetual-futures/)
- [Automated Market Makers (AMMs) - Overview]({{site.url_complet}}/2025/07/29/automated-market-makers-amm/)
- [Cross-Chain Bridge Threat Model - Assets, Trust Boundaries, STRIDE and Threat Register]({{site.url_complet}}/2026/07/31/cross-chain-bridge-threat-model/)
