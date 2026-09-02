---
layout: post
title: "The Hyperliquid Improvement Proposals - HIP-1 to HIP-4"
date:   2026-09-02
lang: en
locale: en-GB
categories: blockchain defi
tags: hyperliquid defi perpetual derivatives oracle trading
series: hyperliquid
description: HIP-1 tokens, HIP-2 Hyperliquidity, HIP-3 builder-deployed perps and HIP-4 outcome markets, with the stakes, auctions and slashing rules that gate each one.
image: /assets/article/blockchain/hyperliquid/hyperliquid-hips.png
isMath: true
---

A Hyperliquid Improvement Proposal is not a governance document. Nothing is voted on, nothing sits in a Draft or Final status, and there is no editor. Each HIP is a primitive already compiled into L1 execution, and the proposal number is simply the label it shipped under.

What the four HIPs share is a way of handling permission. On a centralised venue, listing an asset or opening a market is a decision someone makes about you. On Hyperliquid the decision is priced instead: a Dutch auction for a token ticker, a staked bond for a perp DEX, a per-deployer capacity limit for an outcome venue. Nobody approves the listing, and a deployer who operates a market badly is answerable afterwards to a stake-weighted validator vote that can burn the bond. HIP-2 is the one case with no deployer role to price, because it has no deployer at all.

This article works through the four in order: the token standard and its five-step deployment, the operator-free market-making ladder, the builder-deployed perp DEX with its 500 000 HYPE bond, and the fully collateralised outcome markets that arrived most recently. It closes on what the four have in common, which is where the design shows most clearly.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The shape of the four proposals

The four HIPs sit on the same HyperCore primitives: the order book engine, the clearinghouse, and staking. None of them is a smart contract, and none is upgradeable by its deployer. HIP-1 defines a token and the spot book it trades on. HIP-2 defines a market-making strategy that runs inside block transition logic on a HIP-1 book. HIP-3 lets a bonded deployer stand up an entire perp DEX with its own margining. HIP-4 adds a settled, fully collateralised instrument with no leverage.

Two of them create a deployer role that carries an ongoing obligation, one creates a deployer role that ends at genesis, and one creates no role at all. That distinction is what the permissioning table at the end of this article turns on.

## HIP-1: the native token standard

HIP-1 is a capped-supply fungible token standard with onchain spot order books between pairs of HIP-1 tokens. Read that as two things bundled together: an asset, and a venue for it. The two arrive in the same deployment because HyperCore has no separate listing step.

### Genesis parameters

The genesis transaction fixes the token permanently:

- **`name`** — at most six characters, with **no uniqueness constraint**. The ticker is a display string, not an identifier; the deployment transaction generates a globally unique hash that execution indexes the token by. Two tokens can legitimately be called the same thing, which is a fact any frontend or integrator has to handle.
- **`weiDecimals`** — the conversion from the token's minimal integer unit to a human-readable float, the same role as 18 for ETH or 8 for BTC.
- **`szDecimals`** — the minimum tradable decimal count on spot books, subject to `szDecimals + 5 <= weiDecimals`. The lot size follows:

$$
\begin{aligned}
\text{lot} = 10^{\,\text{weiDecimals} - \text{szDecimals}}
\end{aligned}
$$

- **`maxSupply`** — the maximum and initial supply. It can only decrease afterwards, through spot book fees or future burn mechanisms.
- **`initialWei`** — optional genesis balances the deployer specifies directly, for a multisig treasury or an initial bridge mint.
- **`anchorTokenWei`** — optional proportional genesis to holders of an existing HIP-1 token. The allocation is computed on `balance - 1e-6 * anchorTokenMaxSupply`, so a holder needs at least 0.0001% of the anchor's max supply to receive anything at all.
- **`hyperliquidityInit`** — the HIP-2 parameters, covered in the next section.

The frontend checks published alongside the standard narrow the ranges further for the ordinary deployment path: `szDecimals` in [0, 2] and `weiDecimals` in [0, 8], on top of the `szDecimals + 5 <= weiDecimals` rule.

### The auction, and the one step that cannot be undone

![The five-step HIP-1 spot deployment, from the Dutch auction and registerToken2 through userGenesis, genesis, registerSpot and registerHyperliquidity]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hip-1-deployment-workflow.png)

Deployment gas is priced by a Dutch auction lasting 31 hours, in which the price decreases **linearly** from an initial value down to a floor of 500 HYPE. The initial value is twice the previous clearing price, or the 500 HYPE floor itself if the last auction failed to complete. Gas is paid in HYPE.

Deployment is a five-action sequence: `registerToken2`, then `userGenesis` (repeatable, and able to blacklist addresses), then `genesis` with a `maxSupply` checksum that verifies every `userGenesis` call landed, then `registerSpot` naming the base and quote indices, then `registerHyperliquidity`.

The property that catches deployers is that only the **first** step is time-sensitive and gas-charged. Once `registerToken2` lands, the ticker and the decimals are locked in and the HYPE is spent, with no time limit on the remaining four. The documentation's own warning is unusually direct: a deployment can end up stuck, for instance with incompatible Hyperliquidity and supply values, and **gas is not refunded** for a stuck deployment. Rehearsing the exact deployment on testnet is the documented mitigation, not a suggestion.

Deploying a pair between two assets that both already exist runs through an independent Dutch auction of its own, queried through `spotPairDeployAuctionStatus`.

### Spot books and fees

A HIP-1 book is parametrised by a base and a quote token. A limit order commits to exchanging `sz * 10^(weiDecimalsBase - szDecimalsBase)` units of base for `px * sz * 10^(weiDecimalsQuote - szDecimalsQuote)` units of quote. Every HIP-1 token is initialised with a book quoted in spot USDC, which carries `szDecimals = weiDecimals = 8` specifically so that a wide range of token prices remains expressible.

Fees collected in a non-USDC base token go to the base token's deployer, defaulting to 100%. `setDeployerTradingFeeShare` can change it, but only downward: the value may never increase, so the ratchet only turns one way. Whatever is not redirected to the deployer is burned. Legacy tokens deployed before the mechanism existed get exactly one upward move away from zero, after which the same ratchet applies and the share can never return to exactly zero. Fees in a non-USDC **quote** token go to the Assistance Fund, and quote token deployers cannot configure a share at all.

### Dust conversion

Spot balances below one lot size and worth at most one dollar are swept daily at 00:00 UTC. All users' dust in a given token is aggregated into a single market sell, and the USDC proceeds are redistributed proportionally to each dusted user's share of the aggregate. If the aggregate is itself below one lot size it is burned instead.

The sweep is skipped when the book is one-sided, or when the aggregate notional is large enough to move the market: 10 000 USDC for PURR and 3 000 USDC for every other token. Users receive whatever the market sell actually realised, which slippage can put below the mid-price valuation.

### Deploying an asset that already exists elsewhere

A common pattern is to use HyperCore's spot books to trade an asset minted somewhere else, such as a bridged token or a tokenised RWA. The recommended shape is to mint the ERC-20 on the HyperEVM using an established bridge (LayerZero, Axelar, Chainlink CCIP, deBridge or Wormhole are the ones the documentation names), then pay the HIP-1 auction to buy the HyperCore token and order book state.

For that pattern, the deployer puts the max supply, or `2^64-1` for maximum flexibility, at the token's **system address** during genesis, and normally sets `noHyperliquidity` since a bridged asset already has a price. The auction fee is explicitly framed as charging the deployer for state that would otherwise be charged to future users.

## HIP-2: Hyperliquidity

Bootstrapping liquidity for a token in early price discovery is a different problem from quoting BTC. HLP can quote deep and tight on assets with a CEX reference price; a token that listed an hour ago has none. HIP-2 addresses that without introducing an operator.

### An order book strategy with no operator

Hyperliquidity is a fully onchain strategy that is part of Hyperliquid's **block transition logic**. There are no keeper transactions, no admin key, and no vault contract. The strategy is secured by exactly the same consensus that operates the book it quotes into, which is a stronger statement than "the code is onchain": there is no transaction anyone could fail to send.

It is parametrised at deployment by five values: the spot asset, `startPx`, `nOrders`, `orderSz`, and `nSeededLevels`. The price ladder is geometric:

$$
\begin{aligned}
p_0 = \text{startPx}, \qquad p_i = \operatorname{round}(1.003 \cdot p_{i-1})
\end{aligned}
$$

`nSeededLevels` is the number of levels that begin as bids rather than asks. Each additional seeded level costs the deployer `px * sz` worth of USDC to fund and correspondingly **reduces** the genesis token supply allocated to Hyperliquidity, so seeding the bid side and total supply trade off against each other at fixed `nOrders`.

### The update rule

![On any block three seconds after the last update, Hyperliquidity targets floor(balance / orderSz) full ALO asks plus one partial, then refills each filled tranche]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hip-2-hyperliquidity-update-workflow.png)

The strategy updates on every block whose timestamp is at least three seconds after the previous update. Each update targets $$\lfloor \text{balance} / \text{orderSz} \rfloor$$ full ask orders plus one partial order of the remainder, and those orders are placed to the extent that ALO orders are not rejected. Every tranche that filled completely since the last update is re-placed at `orderSz` on whichever side has balance, excluding the single partial order.

Two details follow from the ALO choice. Hyperliquidity never takes, so it never pays a taker fee and never crosses a resting order; and an ALO order that would cross is simply rejected, which is the reason the documentation qualifies the guarantee with "to the extent that ALO orders are not rejected".

The result is a 0.3% spread refreshed every three seconds without a single user transaction. The improvement over a constant-product pool is not the curve, which is coarser, but the venue: Hyperliquidity rests in a general-purpose order book, so an active market maker can quote inside the ladder at any time and the market can adapt as demand for liquidity grows. Liquidity does not have to migrate off the AMM to improve; it accumulates in the same book.

Hyperliquidity is currently available only on spot pairs quoted in USDC.

## HIP-3: builder-deployed perpetuals

HIP-3 is the largest of the four by surface area. It lets anyone who posts the bond deploy a perp DEX with **independent margining, order books and deployer settings**, while inheriting the HyperCore matching engine, risk engine and API. Trading a HIP-3 asset uses the same actions as any other perp; only the asset ID differs.

### What the deployer owns

The deployer is responsible for market definition, which means the oracle definition and the contract specifications, and for market operation, which means publishing oracle prices, setting leverage limits, and settling the market when needed. The action set reflects that: `registerAsset2`, `setOracle`, `setFundingMultipliers`, `setFundingInterestRates`, `setMarginTableIds`, `setOpenInterestCaps`, `setMarginModes`, `setDeployerFees`, `setFeeRecipient`, `setSubDeployers`, `setPerpAnnotation`, `haltTrading` and `disableDex`.

`haltTrading` does more than its name suggests. It cancels every order and settles all positions to the current mark price, and the same action reverses to resume trading. That makes it a general recycling mechanism: a deployer can list a dated contract, settle it at expiry, and relist the next one on the same asset slot without returning to the deployment auction.

### The bond and the listing cost

![The life of a HIP-3 DEX: stake 500k HYPE, list three assets without an auction, configure and optionally enable cross margin irreversibly, then operate under validator review]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hip-3-dex-lifecycle-workflow.png)

Mainnet requires **500 000 staked HYPE**, maintained for a minimum of 183 days after the DEX is deployed, with anything above the current requirement free to unstake. The requirement is expected to fall as the infrastructure matures. One qualifying deployer gets one perp DEX for now, with shared-stake multi-DEX deployment named as a future upgrade.

Listing follows a two-tier rule. The **first three assets** in any DEX skip the auction entirely. Additional assets go through a Dutch auction with the same hyperparameters as the HIP-1 auction, shared across every perp DEX rather than per-DEX. Deployers also accumulate $$7 + 0.2 n$$ reserve deployments, where $$n$$ is their number of auction deployments, usable at the current auction price but bypassing the auction timer — the mechanism for listing something time-sensitive without waiting.

Any quote asset can serve as the DEX's collateral. If a quote asset loses its status by validator vote, perp DEXs collateralised by it are disabled; a deployer-initiated disabling is not contagious in the same way. HIP-3 deployers are not themselves slashed over quote-asset failures, since quote token deployers post their own separate stake.

### Fees

The deployer sets a fee `scale` between 0% and 300%, or 0% to 100% under growth mode. Taking a base user fee of one unit and non-aligned collateral, the split behaves as follows:

| `growthMode` | `feeScale` | To protocol | To deployer |
|:---:|:---:|:---:|:---:|
| false | 0 | 1 | 0 |
| false | 0.5 | 1 | 0.5 |
| false | 1 | 1 | 1 |
| false | 3 | 3 | 3 |
| true | 0 | 0.1 | 0 |
| true | 0.5 | 0.1 | 0.05 |
| true | 1 | 0.1 | 0.1 |
| true | 9.99 | 0.999 | 0.999 |

The rule visible in the table is that above a scale of 1, the protocol fee is raised to **equal** the deployer fee rather than staying fixed. A deployer choosing a 300% share is therefore tripling what the protocol takes as well as what they take.

**Growth mode** cuts all-in fees, rebates, volume contribution and L1 user rate-limit contribution by at least 90%, taking the baseline all-in taker rate to between 0.0045% and 0.009%. It carries two conditions. The fee scale must sit between 0 and 10, and setting growth mode has a 30-day cooldown per asset. More consequentially, the markets must be **entirely disjoint** from validator-operated perps, to prevent parasitic volume: crypto perps against any collateral, perps on crypto indices or baskets, perps on mathematical combinations involving crypto prices, perps on wrappers holding mostly crypto, and duplicates of existing markets such as a gold perp when PAXG-USDC already tracks gold. As with delistings, the arbiter is an onchain validator vote.

### Margin modes and the irreversible switch

A user's account abstraction mode decides how cross margin behaves across DEXs. Under unified account or portfolio margin, cross margin positions in DEXs sharing a collateral asset are margined together; under standard mode, cross margin applies within a single DEX. HIP-3 DEXs additionally support a **no-cross** mode, which allows isolated margin with removal enabled but forbids cross margin entirely.

Enabling cross margin on a HIP-3 asset is **irreversible**. Because a user in cross margin across DEXs run by different deployers is taking on more than the system-level protections cover, validators enforce eligibility standards before it is enabled: sufficient observable liquidity, a reliable external oracle source, and resilience to price manipulation. Every time an asset's `externalPerpPx` moves more than 50% relative to the start-of-day price, validators review whether the deployer should be slashed for manipulation, and an asset where 50% daily moves are expected more than once a month is ineligible for cross margin outright.

### The backstop liquidator

Each HIP-3 DEX has a fully onchain strategy at `0x400..00 + {dex_index}` that takes over backstop-liquidatable positions from that DEX. It accepts only assets where cross margin is enabled, which makes those assets materially less likely to reach auto-deleveraging during a volatility event. The strategy is an independent user and itself falls back to ADL, so the DEX's solvency guarantee holds mathematically rather than depending on the strategy's balance.

### Open interest caps

HIP-3 markets carry two kinds of cap. **Notional** caps apply both per-asset and to the total across the DEX, and the deployer can set a custom per-asset value. **Size-denominated** caps are per-asset only and are currently a constant 1 billion units. The documentation therefore advises choosing `szDecimals` so that the minimum size increment is worth roughly one to ten dollars at the initial mark price. Getting that wrong caps the market far below its notional limit.

### Slashing

Slashing decided by stake-weighted validator vote is what makes the bond meaningful, and its stated principle is narrow: prevent behaviour that jeopardises protocol correctness, uptime or performance. The rule of thumb given is that any slashable behaviour should also be accompanied by a bug fix in the protocol implementation, so that HIP-3 in its final state should not need slashing at all.

The guideline scale runs to 100% for irregular inputs causing invalid state transitions or prolonged downtime, up to 50% for brief downtime, and up to 20% for network degradation. The amount actually applied is a stake-weighted median of validator votes, and the stake stays slashable throughout the seven-day unstaking queue even after withdrawal is initiated.

Three properties of the mechanism deserve to be stated rather than inferred:

- **It is technical, not moral.** It does not distinguish a deployer who deviated from a well-designed spec, one who faithfully followed a badly designed spec, and one whose private keys were compromised. Only the effect on the protocol is judged. Symmetrically, inputs that cause protocol issues but are not *irregular* are not slashable, and bugs unrelated to deployer inputs fall outside its scope entirely.
- **Subjective harm is out of scope.** Behaviour that is valid by protocol definition but objectionable by some interpretation is left to the application and social layers, on the reasoning that a proof-of-stake chain preserving neutrality should not intervene in subjective matters any more than it should hard-fork over an unpopular state transition.
- **Slashed stake is burned.** It is not distributed to affected users, explicitly to avoid misaligned incentives between users and deployers. A HIP-3 market's users are protected by the deployer's incentive not to be slashed, not by a compensation fund.

The last of these has a direct consequence for anything built on top: an LST accepting deposits that back a HIP-3 deployer inherits the slashing risk, and the documentation says plainly that LST operators should diligence deployers carefully, communicate the risk to their users, and that a self-bonding requirement for deployers could make sense.

## HIP-4: outcome markets

HIP-4 is the newest of the four and the only one that adds an instrument rather than a venue or an asset. Outcomes are fully collateralised contracts that settle within a fixed range, which covers prediction markets and bounded option-like instruments. They bring non-linearity and dated contracts to HyperCore without leverage and without liquidations.

### Two sides that always sum to one

![splitOutcome and mergeOutcome exchange quote tokens for a matched Yes and No pair, mergeQuestion redeems one Yes of every outcome, and negateOutcome inverts a No]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hip-4-outcome-algebra-concept.png)

Each outcome market has two sides, each with its own token, labelled by `sideSpecs` in the `outcomeMeta` info response and usually named Yes and No. Settlement converts a Yes share into `settleFraction` quote tokens and a No share into `1 - settleFraction`, so `settleFraction = 1` is a binary yes and `0` a binary no. A standalone outcome may settle to any fraction in [0, 1], which is what allows scalar payouts.

Because the two sides always sum to exactly one quote token, the position can never become undercollateralised. That is the whole reason there is no leverage and nothing to liquidate, and it separates outcome markets from every other HyperCore instrument, all of which can go underwater.

Four conversions move between the representations, and their semantics are exact:

| Action | Effect |
|--------|--------|
| `splitOutcome` | Split `X` quote tokens into `X` Yes shares and `X` No shares. |
| `mergeOutcome` | Merge `X` Yes and `X` No shares back into `X` quote tokens. |
| `mergeQuestion` | Merge `X` Yes shares from **every** outcome of one question into `X` quote tokens. |
| `negateOutcome` | Convert `X` No shares of one outcome into `X` Yes shares of **every other** outcome of the question. |

`negateOutcome` is the least obvious of the four. A question is a collection of outcomes where exactly one settles Yes, so holding No on outcome A is the same claim as holding Yes on the union of everything else. The action makes that identity mechanical, which lets a holder who is short one outcome redeem quote tokens before the underlying outcomes settle rather than waiting.

### The merged book

The Yes and No books of the same outcome are **merged** so they share liquidity, on the identity that an order to buy Yes at price $$p$$ is an order to sell No at $$1 - p$$. Price-time priority accordingly generalises to **price-side-time priority**: for orders at the same merged price level, resting sell orders sort before all resting buy dual orders.

Most operations abstract the dual book away from the user, but not all of them yet. Historical orders can return the primary and dual orders separately when a single order both matches and rests, which is documented as an ergonomic issue to be improved on a future upgrade rather than as intended behaviour.

### Fees

Outcome trading charges fees only when **closing or settling**, never when opening, and only fee-paying volume is counted. The six cases the documentation enumerates fall out of that rule: minting charges nothing and counts no volume; a normal trade credits both users `fee_paying_px * sz` when one side pays and nothing when neither does; burning credits `(maker_px + taker_px) * sz = 1 * sz` when both pay and `taker_px * sz` when only the taker does; and settlement credits `settle_fraction * sz`.

There are no rebates on outcome markets. Users who would earn a rebate on spot or perp trading instead pay zero on maker orders. Builder codes work as in spot for sell orders, and additionally apply to **buy** orders on outcomes, charged in the quote token on a best-effort basis.

Fees are currently zero across outcome markets while the primitive is being tested.

### Deployment, and how it differs from HIP-3

HIP-4 deployment is the most tightly constrained of the four, and at the time of writing the deployer flow is **testnet-only**. Rather than letting a deployer define a market freely, validators vote on **templates**, and deployers instantiate them.

A template fixes the display name and description text as strings containing `{keyword}` placeholders, the side names, and a typed hint per keyword. The hint types are `dateTime`, `date`, `string`, `shortString`, `hlPerp`, `uInt` and `uDecimal`, each with its own value format, and dates must fall within the next year. An instantiation supplies exactly one value per keyword; the onchain name becomes `template:<template_id>` and the description is the sorted keyword-value pairs joined as `keyword:value|keyword:value`.

Template metadata carries a `semanticRestriction` field defining the intended semantics of markets built from it. A market contradicting its template's restriction is malformed and **slashable by validators**, which is the HIP-4 analogue of HIP-3's irregular-input standard.

Other structural differences from HIP-3:

- **A venue, not a DEX.** Each deployer registers a venue name of 2 to 4 lowercase ASCII letters, unique across all venue names including deactivated ones and across perp DEX names. A venue name is reserved permanently.
- **Deployment costs no gas.** Capacity is bounded by per-deployer limits instead: on testnet, at most 10 active outcomes and 50 deployments per day. Settling an outcome frees capacity.
- **Staking requirements stack.** Stake counting toward HIP-3 deployment does not double-count toward outcome deployment. Deactivation requires the 183-day minimum to have elapsed with no active outcomes, and is permanent: the account can never activate again.
- **Deployers must use Standard account abstraction**, the same requirement builder-code addresses carry.

The deployer fee scale is a decimal in [0, 10] with a different formula from HIP-3. Users pay the base outcome rate times `scale + max(scale, 1)`, and the deployer receives the `scale` component:

| `deployerFeeScale` | Total user fee | Deployer | Protocol |
|:---:|:---:|:---:|:---:|
| 0 | 1x | 0x | 1x |
| 0.25 | 1.25x | 0.25x | 1x |
| 0.5 | 1.5x | 0.5x | 1x |
| 1 | 2x | 1x | 1x |
| 3 | 6x | 3x | 3x |
| 10 | 20x | 10x | 10x |

Settlement is sequential for a question: outcomes may settle to 0 in any order, and the outcome settling to 1 does so once it is the last active one, which automatically settles the fallback to 0 and closes the question. `settleQuestion2` settles every remaining outcome in a single action, requiring exactly one to settle to 1. Adding an outcome to a live question is possible up to 100 outcomes, and holders of the question's fallback Yes token receive an equal balance of the new outcome's Yes token so that existing "other" positions keep their meaning.

The first mainnet market is a recurring binary settling daily at 06:00 UTC against the BTC mark price on HyperCore, with the target computed by linear interpolation between the mark price updates immediately before and after the settlement timestamp.

## Asset IDs: how the four appear in the API

The four HIPs share one exchange endpoint and are distinguished by the integer asset ID:

```
Validator perps    asset = index in the `meta` response          (BTC = 0 on mainnet)
HIP-3 perps        asset = 100000 + perp_dex_index * 10000 + index_in_meta
                   name is always {dex}:{coin}, e.g. test:ABC -> 110000
Spot (HIP-1)       asset = 10000 + spotInfo["index"]             (PURR/USDC -> 10000)
Outcomes (HIP-4)   encoding = outcome_id * 10 + side             (side in {0, 1})
                   spot coin  #<encoding>     e.g. #10
                   token name +<encoding>     e.g. +10
                   asset ID   100000000 + encoding   e.g. 100000010
```

Two traps live here. The spot ID is not the token ID: HYPE on mainnet has token ID 150 and spot ID 107, and both differ again on testnet. And outcome markets, despite sharing most of their implementation with spot, use a third encoding that is neither the spot nor the perp scheme.

## The common pattern

Setting the four side by side, the design that repeats is clearer than any individual proposal.

| | Entry is gated by | Ongoing obligation | Slashable for | Deployer role after launch |
|---|---|---|---|---|
| **HIP-1** | Dutch auction, 31 h, floor 500 HYPE | None | Nothing | Fee share only, and it can only decrease |
| **HIP-2** | Nothing; it is a HIP-1 genesis field | None | Nothing | **None at all** |
| **HIP-3** | 500 000 HYPE for ≥183 days, plus a shared auction after the first three assets | Publish oracle prices, operate the market | Irregular inputs: up to 100% / 50% / 20% by impact | Continuous |
| **HIP-4** | Staking requirement that stacks; free deployment with per-deployer capacity caps | Settle outcomes correctly | Markets contradicting their template's `semanticRestriction` | Continuous |
| **Quote asset** | 200 000 HYPE committed for 3 years | Maintain peg and book depth | Depth conditions failing across a 3-day sample window | Continuous |
| **Aligned quote asset** | 1M HYPE (v1), or 500 000 each for the treasury and technical deployers (v2) | Deliver reserve-yield revenue and mint/redeem infrastructure | Unpaid revenue at the system interest address, at 2% per day | Continuous |

Three observations follow.

**Permission is priced, not granted.** Every entry gate is either an auction, a bond, or a capacity limit, and none of them is a decision about the applicant. A deployer who can pay can list, which is the property the documentation contrasts with CEX listings involving "behind-the-scenes negotiations for preferential treatment".

**Conduct is policed after the fact, by stake-weighted vote, against partly offchain conditions.** Quote-asset depth is measured onchain, but AQA compliance, HIP-4 semantic restrictions and HIP-3 "irregular input" all involve validator judgment on evidence that execution cannot evaluate. This is stated as a deliberate choice rather than a gap: validators achieve consensus on a self-contained state machine, and any condition outside it has to be driven by vote.

**Slashed stake is burned in every case.** No HIP compensates users from a slashed bond. The stake exists to make bad operation expensive for the operator, and the protection it offers users is entirely ex ante.

The one proposal that escapes the pattern is HIP-2, and it escapes by having no operator to bond or slash. That is the design in its simplest form, and it is available only because the strategy is simple enough to express as block transition logic. Everything a deployer might get wrong in HIP-1, HIP-3 or HIP-4 is something HIP-2 has no room to get wrong.

## Conclusion

The four HIPs are not versions of one another. HIP-1 is an asset plus a venue, priced by auction and finished at genesis. HIP-2 is a market-making strategy with no operator, no keeper and no admin key, which is why it is the only one with nothing to slash. HIP-3 hands a bonded deployer the whole HyperCore risk engine and polices what they do with it afterwards. HIP-4 adds an instrument whose collateralisation is exact by construction, which is what lets it dispense with leverage and liquidation entirely.

What connects them is the substitution of a price for an approval, and of a burned bond for a compensation fund. A deployer buys entry at auction or posts stake, operates without asking anyone, and answers to a stake-weighted vote if the operation damages the protocol. For a user or an integrator, the practical reading is that the protections are ex ante: the deployer's incentive not to be slashed, the eligibility standards validators enforce before cross margin is enabled, and the collateralisation arithmetic in HIP-4. There is no rung below those where losses are made whole.

![Mindmap of the four Hyperliquid Improvement Proposals covering HIP-1 native tokens, HIP-2 Hyperliquidity, HIP-3 builder-deployed perps, HIP-4 outcome markets and the permissioning pattern they share]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-hips.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **HIP** | A Hyperliquid Improvement Proposal: a primitive compiled into L1 execution, not a governance document awaiting approval. |
| **`szDecimals` / `weiDecimals`** | The tradable decimal count and the integer-to-float conversion of a HIP-1 token; the lot size is `10^(weiDecimals - szDecimals)` and `szDecimals + 5 <= weiDecimals` must hold. |
| **Anchor token** | An existing HIP-1 token whose holders receive a proportional genesis allocation in a new deployment, subject to holding at least 0.0001% of its max supply. |
| **Hyperliquidity** | The HIP-2 strategy: a geometric price ladder of ALO orders refreshed every three seconds by block transition logic, with no operator. |
| **`nSeededLevels`** | The number of Hyperliquidity levels beginning as bids; each one costs the deployer `px * sz` in USDC and reduces the strategy's genesis token supply. |
| **Perp DEX** | A HIP-3 deployment with its own margining, order books and settings, sharing the HyperCore engine and API but not its collateral pool under standard abstraction. |
| **Growth mode** | A HIP-3 setting cutting all-in fees, rebates and volume contribution by at least 90%, restricted to markets disjoint from validator-operated perps. |
| **Outcome** | A HIP-4 market of two tokens whose settlement values sum to exactly one quote token, making it fully collateralised and free of liquidation. |
| **Question** | A collection of HIP-4 outcomes of which exactly one settles Yes, linked by `mergeQuestion` and `negateOutcome` and carrying an automatic fallback outcome. |
| **`semanticRestriction`** | The field on a HIP-4 template defining the intended meaning of markets built from it; a market contradicting it is malformed and slashable. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A HIP-1 deployer's fee share can never increase. | `setDeployerTradingFeeShare` rejects any value above the current one. | The ratchet is removed, at which case a deployer could attract volume cheaply and reprice it. |
| A HIP-1 token's supply never exceeds `maxSupply`. | Supply is fixed at genesis and can only fall through fees or burns. | A mint path is added after genesis. |
| Hyperliquidity requires no user transaction to stay quoting. | The strategy runs in block transition logic, not as a contract call. | It is reimplemented as a keeper-driven contract. |
| Hyperliquidity never takes liquidity. | It places ALO (post-only) orders, which are rejected rather than crossing. | The order type is changed to GTC. |
| A HIP-3 DEX stays solvent without an insurance balance. | The `0x400..00 + dex_index` backstop liquidator, falling back to ADL. | Cross margin is enabled on an asset the backstop does not accept. |
| A HIP-3 deployer's stake is answerable for at least 183 days. | The minimum staking duration, plus slashability throughout the 7-day unstaking queue. | The duration is shortened below the window in which damage becomes visible. |
| A HIP-4 outcome's two sides always redeem for exactly one quote token. | `settleFraction` and `1 - settleFraction` by construction, with split and merge as the only issuance paths. | An issuance path is added that does not mint both sides together. |
| A HIP-4 question always has an exhaustive outcome set. | The fallback outcome is created automatically and receives matching balances when a new outcome is added. | The fallback is removed or new outcomes skip the balance credit. |
| Merged Yes and No books never quote a crossed dual price. | Price-side-time priority sorts resting sells before resting dual buys at the same merged level. | The two books are separated and quoted independently. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| HIP-1 tickers carry **no uniqueness constraint**; the token is indexed by a hash from its deployment transaction. | Key on the token index, never on the displayed name, and expect duplicate tickers in any listing UI. |
| Only `registerToken2` is time-sensitive and gas-charged; a stuck later step is not refundable. | Rehearse the exact deployment on testnet, and treat the auction win as a commitment rather than a first draft. |
| Spot ID, token ID and outcome asset ID are three different numbering schemes, and they differ between mainnet and testnet. | Resolve IDs from `spotMeta` / `outcomeMeta` at runtime; never hard-code them or carry them across networks. |
| Enabling cross margin on a HIP-3 asset can never be undone. | Treat it as a one-way door in any deployment runbook, and confirm the asset meets the liquidity and oracle standards first. |
| HIP-3 size-denominated OI caps are a constant 1B units per asset. | Choose `szDecimals` so the minimum size increment is worth roughly one to ten dollars at the initial mark price, or the notional cap will never bind. |
| A HIP-3 fee scale above 100% raises the protocol fee to match the deployer fee. | Model the total user cost, not the deployer share, when choosing a scale. |
| HIP-4 historical orders can return the primary and dual orders separately when one order both matches and rests. | Reconcile fills against the merged book rather than assuming one order produces one record. |
| HIP-4 `Outcome operation` payloads through CoreWriter are **dropped** if unused fields are non-zero. | Zero every field the operation does not use: `SplitOutcome` and `MergeOutcome` ignore `question`, `MergeQuestion` ignores `outcome`. |
| HIP-4 deployers and builder-code addresses must use Standard account abstraction. | Keep those addresses out of unified account and portfolio margin, and separate them from trading accounts. |
| A HIP-4 venue name is reserved permanently, including after deactivation, and cannot collide with a perp DEX name. | Register the name you intend to keep; deactivation is not a way to release it. |

## Frequently Asked Questions

**Q: HIP-2 is described as inspired by Uniswap. Where does it diverge?**

Three things:

- **It quotes into a general-purpose order book** rather than into a separate pool. An active market maker can place orders inside Hyperliquidity's ladder at any time, so the market improves without liquidity having to migrate off the AMM.
- **It has no operator and no keeper transactions.** The strategy is part of block transition logic, secured by the same consensus that runs the book, so there is no transaction anyone could fail to send and no admin key.
- **It posts discrete ALO orders**, not a continuous curve. The ladder is `p_i = round(1.003 · p_{i-1})`, refreshed on any block at least three seconds after the last update, which gives a guaranteed 0.3% spread rather than a curve-derived price.

The similarity to Uniswap is the requirement that liquidity provision needs no maintenance; almost everything else differs.

**Q: A deployer wins the HIP-1 auction and then discovers their Hyperliquidity parameters are incompatible with their supply. What are the options?**

Practically, none that recover the gas. The auction is settled at `registerToken2`, which is the only gas-charged and time-sensitive step, and the documentation states directly that gas cannot be refunded if a deployment gets stuck.

The remaining four steps have no time limit, so there is room to work out a valid combination if one exists; but the ticker and both decimal values are locked from step one, and `genesis` carries a `maxSupply` checksum that will not accept a set of `userGenesis` calls that do not add up. This is why testnet rehearsal of the exact deployment, not an approximation of it, is the documented process.

**Q: Why does a HIP-3 fee scale of 3 cost the user six times the base fee rather than four?**

Because above a scale of 1, the protocol fee is raised to equal the deployer fee rather than staying at its base value. At `scale = 3` the deployer takes 3 units and the protocol also takes 3, for 6 in total; at `scale = 0.5` the deployer takes 0.5 and the protocol still takes its base 1, for 1.5.

The practical implication is that the deployer's share and the user's total cost are not proportional. A deployer optimising their own revenue past 100% is raising the total user fee twice as fast as their own take.

**Q: What is `negateOutcome` for, and why can it not exist in a two-sided market?**

`negateOutcome` converts `X` No shares of one outcome into `X` Yes shares of every *other* outcome of the same question. It exists because a question's outcomes are exhaustive and mutually exclusive, so "not A" is exactly the same claim as "B or C or the fallback".

It cannot exist for a standalone outcome, because there is no set of other outcomes to convert into; there, No is already the dual of Yes and `mergeOutcome` is the only conversion available. Its purpose is redemption timing: a holder short one outcome can combine `negateOutcome` with `mergeQuestion` to get quote tokens back before the underlying outcomes settle, rather than waiting for settlement.

**Q: HIP-3 slashing does not distinguish a malicious deployer from a compromised one. Why is that deliberate rather than an oversight?**

Because the mechanism judges effect on the protocol, not intent, and intent is not something execution or a validator vote can establish. A deployer whose keys were stolen and a deployer acting in bad faith produce identical onchain evidence, and treating them differently would require a subjective finding the protocol explicitly declines to make.

The same principle runs in the other direction and is easier to overlook: inputs that cause protocol issues but are *not* irregular are not slashable, and bugs under normal operation unrelated to deployer inputs fall outside its scope entirely. The bond prices the deployer's operational security along with their competence, which is why the documentation suggests LST operators diligence deployers and consider requiring self-bonding.

**Q: Which HIPs create an ongoing obligation, and what does a user actually get from the ones that do?**

HIP-3 and HIP-4 create continuous deployer obligations, as do quote-asset and aligned-quote-asset status. HIP-1's deployer role effectively ends at genesis, apart from a fee share that can only decrease. HIP-2 creates no role at all.

What a user gets is narrower than it first appears. The bond is slashable by stake-weighted validator vote, and the slashed stake is **burned**, not distributed to affected users. So the protection is entirely ex ante: it is the deployer's incentive to avoid slashing, plus the eligibility standards validators enforce before an irreversible step such as enabling cross margin. There is no rung below that where losses are made whole.

**Q: Comparing HIP-2 and HIP-3, why does one need no bond at all while the other needs 500 000 HYPE?**

The difference is whether there is anything for a human to get wrong at run time. Hyperliquidity's entire behaviour is fixed by five parameters at deployment and executed thereafter by block transition logic: no one publishes a price, no one adjusts a leverage limit, no one settles anything. There is no operator, so there is nothing to bond.

A HIP-3 deployer, by contrast, publishes the oracle prices that drive margining and liquidation on their DEX, sets margin tables and OI caps, and settles markets. Every one of those is a continuous opportunity to damage users or the protocol, and the bond is what makes that opportunity expensive. The general rule the pair illustrates is that Hyperliquid bonds discretion, not deployment: where a primitive can be expressed as execution logic it is, and where it needs a human in the loop, that human posts stake.

## References

### Improvement proposals

- [Hyperliquid Improvement Proposals (HIPs)](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips) — the index page for the four proposals
- [HIP-1: Native token standard](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-1-native-token-standard) — genesis parameters, the Dutch auction, fee share, dust conversion, deploying existing assets
- [HIP-2: Hyperliquidity](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-2-hyperliquidity) — parameters, the geometric ladder, the update rule
- [HIP-3: Builder-deployed perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals) — the spec, settlement, oracle, slashing, cross margin, backstop liquidator
- [HIP-4: Outcome markets](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-4-outcome-markets) — mechanics, merged books, questions, fees
- [Frontend checks](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/frontend-checks) — the client-side validation for spot deployment

### Deployer and trading APIs

- [Deploying HIP-1 and HIP-2 assets](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets) — the five-step `spotDeploy` sequence and its optional actions
- [HIP-3 deployer actions](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions) — the `perpDeploy` action set, the fee scale table, open interest caps
- [HIP-4 deployer actions](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions) — templates, venues, the deployer fee scale, settlement and limits
- [Exchange endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint) — `splitOutcome`, `mergeOutcome`, `mergeQuestion` and `negateOutcome` semantics
- [Asset IDs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/asset-ids) — the perp, HIP-3, spot and outcome encodings
- [Interacting with HyperCore](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/interacting-with-hypercore) — the CoreWriter action table, including `Outcome operation`

### Supporting mechanics

- [Fees](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees) — fee tiers, growth mode, outcome token fee cases, the Assistance Fund
- [Contract specifications](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications) — recurring outcome settlement and the interpolation rule
- [Margining](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margining) — HIP-3 margin modes and the no-cross mode
- [Permissionless spot quote assets](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/permissionless-spot-quote-assets) — the 200k HYPE bond and the depth conditions
- [Aligned quote assets](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/aligned-quote-assets) — AQAv1 and AQAv2 stakes, revenue share and slashing
- [HyperCore and HyperEVM transfers](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/hyperevm/hypercore-less-than-greater-than-hyperevm-transfers) — system addresses and the Core-to-EVM linking flow

### External standards

- [ERC-20: Token Standard](https://eips.ethereum.org/EIPS/eip-20) — the HyperEVM side of a linked HIP-1 token
