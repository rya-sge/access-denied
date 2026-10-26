---
layout: post
title: "Hyperliquid HIPs in Practice - Risks, Failure Scenarios and Market Quality"
date:   2026-10-26
lang: en
locale: en-GB
categories: blockchain defi
tags: hyperliquid defi perpetual derivatives oracle trading risk liquidation prediction-market
series: hyperliquid
description: "What users lose when a HIP-1 to HIP-4 market fails on Hyperliquid, how to judge a market before trading it, and worked examples for each proposal."
image: /assets/article/blockchain/hyperliquid/hyperliquid-hip-risks-market-quality.png
isMath: false
---

Hyperliquid lets anyone list a spot token (HIP-1), seed it with automatic liquidity (HIP-2), run a perpetual exchange under a bond (HIP-3) or deploy outcome markets from validator-approved templates (HIP-4). How each mechanism works is covered in [The Hyperliquid Improvement Proposals - HIP-1 to HIP-4]({{site.url_complet}}/2026/09/02/hyperliquid-improvement-proposals-hip-1-to-hip-4/). This article covers what that article leaves to the reader: who loses money when a market built on a HIP goes wrong, how much of that loss any protection covers, and what to check before trading a market or depending on one.

It opens with a risk matrix, then works through one example per HIP with numbers: a token deployment, a liquidity ladder being bought and sold, an oracle failure on a builder-deployed perp, and an outcome settlement. It then gives a checklist for judging market quality, examines how much discretion validators exercise and what a deployer can do about it, and ends with the practical risks specific to each proposal. Request payloads and deployment checklists are in the companion [Building on Hyperliquid HIPs - A Developer Reference for Deployment and Integration]({{site.url_complet}}/2026/10/26/hyperliquid-hip-developer-reference/).

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What you need to know first

The examples assume the mechanics of the four HIPs and a few Hyperliquid terms:

- **Mark price and oracle price.** The oracle price drives funding; the mark price drives margining and liquidation. On validator-operated perps both come from validator medians, as described in [The Hyperliquid Oracle - How Validator Medians Become Mark Price, Funding and Liquidation]({{site.url_complet}}/2026/09/02/hyperliquid-oracle-mark-price/). On a HIP-3 DEX the deployer supplies them.
- **Maintenance margin.** A position is liquidated when its equity falls below the maintenance margin, which on Hyperliquid is half of the initial margin at the asset's maximum leverage. The ladder that follows (liquidation, backstop, auto-deleveraging) is covered in [The Hyperliquid Protocol - HyperCore, HyperEVM and Onchain Perpetual Mechanics]({{site.url_complet}}/2026/09/02/hyperliquid-protocol-architecture/).
- **Auto-deleveraging (ADL).** The last rung of the liquidation ladder: when a position cannot be closed without bad debt, profitable positions on the other side are closed against it. It protects solvency by moving the loss onto other traders.
- **ALO orders.** Add Liquidity Only orders rest as maker orders and are rejected if they would trade immediately. HIP-2 uses them exclusively.
- **Slashing.** A stake-weighted validator vote that cuts a deployer's stake. Slashed stake is burned, not paid to the users who lost money.
- **Implied probability.** In a binary market paying one unit if an event happens, a price of 0.62 means the market prices the event at about 62%.

## The risk matrix

Each row names a way a HIP market can fail, who is in a position to cause or prevent it, who absorbs the loss, and what the protocol does about it. The last column is the point of the table: what is left after every protection has done its work.

| HIP | Failure mode | Who controls it | Who bears the loss | Protection that exists | What remains |
|-----|--------------|-----------------|--------------------|------------------------|--------------|
| HIP-1 | Look-alike ticker | Any deployer (names are not unique) | Buyers and integrators keyed on the name | Token index and token ID are unique | Wrong token bought; no recovery |
| HIP-1 | Concentrated or misleading genesis | Deployer at genesis | Later buyers | Genesis balances are public (`tokenDetails`) | Large holders can sell into the book at any time |
| HIP-1 | Deployer freezes holders | Deployer, if it enabled the freeze privilege | Frozen holders (cannot trade, send or receive the token) | Privilege must be enabled per token and can be revoked; visible through the deployer's actions | Balances locked at the deployer's discretion |
| HIP-1 | Bridged asset loses its backing | Bridge operator, EVM contract owner | Holders of the HyperCore token | None at the HyperCore level | Token trades on, unbacked |
| HIP-1 | Stuck deployment | Deployer | Deployer (gas is not refunded) | Testnet rehearsal | Auction gas lost |
| HIP-2 | Ladder sold through or bought out | Nobody (fixed parameters) | Traders who rely on the ladder's depth | Other makers may quote | One-sided book beyond the range |
| HIP-2 | Informed flow picks off stale levels | Nobody | The Hyperliquidity inventory, so the deployer's seeded capital and the token's float | None; the ladder has no price feed | Losses to better-informed traders |
| HIP-3 | Wrong or manipulated oracle | Deployer or its `oracleUpdater` key | Liquidated traders, and the other side through ADL | 1% mark clamp per update, 10x daily clamp, 50% move review, slashing | Liquidations at a wrong price are not reversed; slashed stake is burned |
| HIP-3 | Oracle goes stale | Deployer | Traders on a thin book | Mark falls back to the local book after 10 s | Mark set by a manipulable book |
| HIP-3 | Bad parameters (leverage, OI caps, `szDecimals`) | Deployer | Traders, then ADL counterparties | Validator review, OI caps | Losses up to the size of the positions |
| HIP-3 | Halt or settlement at an unfavourable mark | Deployer (`haltTrading`) | Open positions | Slashing if the input is irregular | Positions closed at the mark of the moment |
| HIP-3\* | Account-level intervention (testnet only) | Deployer and sub-deployers | Approved users | None documented beyond the allow-list rules | Deployer can force reduce-only, cancel and move collateral within the venue |
| HIP-4 | Wrong settlement | Deployer (`settleOutcome`) | Holders of the losing side | Template `semanticRestriction`, slashing | No dispute window, no documented refund |
| HIP-4 | Ambiguous event wording | Template author, then validators who approved it | Both sides | Typed keywords, validator-voted templates | Settlement depends on the deployer's reading |
| HIP-4 | Settlement-time sensitivity | Mark price around the settlement timestamp | Holders near the target | Linear interpolation between mark updates | A few seconds of price movement can decide the outcome |
| All | Validator intervention outside the written rules | Validator supermajority | Whoever the vote disadvantages | None (it is the last resort) | Outcomes decided case by case |

Two patterns run through the table. First, every loss that reaches a user stays with that user: neither slashing nor any HIP has a compensation path. Second, the protections are rate limits and reviews, not reversals. They slow a bad price down or punish the deployer afterwards; they do not undo a liquidation.

## What a user loses when a market fails

The HIP-3 bond is large, and that makes it easy to read as insurance. It is not. When validators slash a deployer, the stake is burned "instead of being distributed to affected users", in the words of the HIP-3 specification. A trader liquidated by a bad oracle price loses the margin on that position, and the deployer losing 500 000 HYPE does not change the trader's balance.

Four situations account for most of the realistic losses:

- **Manipulated or wrong oracle prices.** On a HIP-3 DEX the deployer publishes the prices that decide liquidation. A wrong feed, a compromised updater key or a deliberate push can move the mark price far enough to liquidate leveraged positions, within the clamps described in the HIP-3 example below.
- **Thin liquidity.** A small book cannot absorb a large liquidation or a large exit. The liquidation then reaches the backstop and possibly ADL, and a trader closing voluntarily pays the slippage. The March 2025 JELLY episode on a validator-operated perp shows how a thin market and a large position combine; it is described under validator discretion below.
- **Bad market parameters.** Leverage too high for the asset's volatility, OI caps that do not bind because `szDecimals` was badly chosen, or margin tables copied from a liquid asset onto an illiquid one. None of these needs bad intent, and slashing does not distinguish incompetence from malice.
- **Losses beyond every protection.** ADL closes profitable positions on the other side when the backstop cannot absorb a loss. Those traders did nothing wrong and their gains are cut. This is how the DEX stays solvent without an insurance fund, and it means solvency is protected at the expense of some of its users.

For HIP-1 and HIP-2 the losses are those of any spot market: a token can go to zero, a holder with a large genesis allocation can sell, and a bridged token is only as good as its bridge. For HIP-4 the collateralisation guarantee holds exactly: a share never pays more than one quote token or less than zero, and nobody is liquidated. The risk moves to settlement, which is decided by the deployer.

## Worked examples

The four examples use made-up names and round numbers. Parameters such as the auction floor and the ladder step are those of the documentation on 2026-10-26.

### HIP-1: one token deployment, from auction to first trade

A deployer wants to launch a token called LUME with a supply of one billion.

**Decimals.** They choose `weiDecimals = 8` and `szDecimals = 2`. The rule `szDecimals + 5 <= weiDecimals` holds (7 is at most 8), both values are inside the frontend ranges, and the lot size is ten to the power of 6 wei, so the smallest tradable amount is 0.01 LUME.

**Auction.** The previous token deployment cleared at 1 000 HYPE, so this auction starts at 2 000 HYPE and falls linearly to the 500 HYPE floor over 31 hours. The deployer waits about half the auction, until the price is near 1 250 HYPE, and sends `registerToken2` with `maxGas` set to 1 300 HYPE so that the transaction fails rather than overpays if the price is not where they expect. From this point the name and decimals are fixed and the gas is spent.

**Genesis.** Two `userGenesis` calls credit 200 million LUME to a team address and 300 million to a treasury multisig. The remaining 500 million go to Hyperliquidity: 1 000 levels of 500 000 LUME each. The ladder's 500 million are credited in `userGenesis` too, to the Hyperliquidity address. The `genesis` call passes `maxSupply` in wei, 10^17 for one billion LUME with 8 wei decimals, which works as a checksum. If the genesis balances and the Hyperliquidity allocation do not add up to it, the call fails and the deployer has to correct the earlier steps before continuing.

**Pair and ladder.** `registerSpot` creates LUME/USDC with `tokens = [lumeIndex, 0]`, USDC being token 0. `registerHyperliquidity` then needs the **spot** index of that pair, which is not the token index, plus `startPx = 0.01`, `orderSz = 500000` and `nOrders = 1000`.

**What a buyer should check afterwards.** The `tokenDetails` info request returns the genesis balances, the deployer, the gas paid and the circulating supply. In this example a buyer would see that half the supply sits at two addresses that can sell at any time, and that the other half is in the ladder. Nothing in HIP-1 locks or vests the team allocation; that would have to be enforced elsewhere, if at all.

### HIP-2: one ladder, bought up and sold back down

Continue with the LUME ladder: `startPx = 0.01` USDC, `nOrders = 1000`, `orderSz = 500 000`, no seeded levels.

**The shape of the ladder.** Each level is 0.3% above the previous one, so the price doubles every 231 levels. Level 100 is at about 0.01349 USDC, level 231 at about 0.01998, and the top level, number 999, at about 0.1994, almost twenty times the start. Selling the entire 500 million tokens up the ladder would raise about 31.7 million USDC.

**The launch book is one-sided.** With `nSeededLevels = 0`, every level begins as an ask. At launch the strategy has no USDC and therefore posts no bids. The first person who wants to sell LUME finds no Hyperliquidity bid at all, only whatever other traders post. Seeding bids costs USDC: twenty seeded levels at 500 000 LUME each, at the lowest prices of the range, cost about 102 900 USDC and reduce the tokens allocated to the strategy by 10 million.

**A buyer lifts the first 100 levels.** They receive 50 million LUME for about 582 100 USDC, an average price of 0.01164, and leave the best ask at about 0.01349, 35% above the start. On the next update at least three seconds later, every completely filled tranche is re-placed as an order of 500 000 on the side that now has a balance, which is the USDC side. The strategy now holds about 582 100 USDC as bids across the levels just consumed, and 450 million LUME as asks above.

**The price falls back.** Anyone selling LUME hits those bids level by level, and the strategy converts USDC back into LUME on the way down. If 50 million LUME are sold back, the inventory returns to roughly its starting state.

What this example shows about the strategy's risks:

- **Inventory imbalance.** At every moment the strategy is all tokens above the current price and all USDC below. A large one-directional move empties one side. Above level 999 there are no Hyperliquidity asks left, and below the start price there are no bids unless levels were seeded.
- **No price feed, so adverse selection.** The ladder does not know the external price. If LUME becomes worth 0.02 elsewhere, an arbitrageur buys every level up to 0.02 at stale prices, and the strategy has sold those tokens below their market value. A conventional market maker would move its quotes; Hyperliquidity cannot.
- **Capital efficiency.** Most of the inventory sits far from the current price. In the example, tokens at levels 500 to 999 are only reached after the price has risen more than fourfold.
- **Quotes that cannot be placed.** Orders are ALO, so a level that would cross a resting order is rejected rather than executed. The documentation's guarantee is qualified accordingly: the quotes are ensured "to the extent that ALO orders are not rejected". When another trader's order sits across a level, the ladder has a gap there until the next update.
- **Price gaps between levels.** Between two levels the strategy offers nothing, so a trade that consumes one level moves the best price by a full 0.3% step unless other makers quote inside the ladder.

### HIP-3: one oracle failure

A deployer runs a DEX called `idx` with one perp, `idx:IDX`, tracking an equity index at 5 000 USDC. The asset's maximum leverage is 20x, so maintenance margin is half the 5% initial margin at that leverage: 2.5% of notional.

A trader opens a long of 10 contracts at 5 000 with 10x isolated margin: 50 000 USDC of notional and 5 000 USDC of margin. Equity is 5 000 plus 10 times the price change, and liquidation happens when equity falls to 2.5% of notional. Solving gives a liquidation price of about **4 615**, a fall of 7.7%.

**The failure.** The deployer's price pipeline starts publishing a wrong value, for example after a vendor feed returns a stale or mis-scaled index. If the deployer sends two mark inputs, the mark price is the median of those two and the local book mark, so two wrong inputs set the mark.

**What the protocol limits.** The HIP-3 action reference constrains `setOracle` in three ways. Calls must be at least 2.5 seconds apart. Each update can move the mark by at most 1%. All prices are clamped to ten times the start-of-day value. The 1% clamp is the important one here: the mark cannot jump from 5 000 to 4 500 in one step. It can, however, step down by 1% per update, and 0.99 to the power of 8 is about 0.923. Eight updates take the mark to about 4 613, below the liquidation price. At the minimum spacing that is about 20 seconds.

**What happens next.** The position is liquidated. Its remaining margin is lost to the trader, and if the book cannot absorb the liquidation the position passes to the DEX's backstop liquidator, then to ADL against profitable shorts. The 50% daily-move review does not trigger, because the move is under 10%. Validators may still vote to slash the deployer if the input was irregular. Even a full 100% slash leaves the trader's balance unchanged.

**The stale-feed variant.** If the deployer simply stops calling `setOracle`, the mark falls back to the local mark, the median of best bid, best ask and last trade, after 10 seconds. The documentation says this fallback "should not be relied upon". On a thin book, the local mark is exactly what a manipulator can move with a few orders, which turns an operational failure into a manipulation opportunity.

### HIP-4: one settlement, and trading before it

The first mainnet outcome market is a recurring binary on BTC that settles daily at 06:00 UTC against HyperCore's mark price. Suppose the day's market asks whether BTC is at or above 100 050 USDC.

**Buying a view.** At 04:00 the Yes side trades at 0.62, an implied probability of about 62%. A trader buys 1 000 Yes for 620 USDC. If Yes settles, they receive 1 000 USDC; if No settles, nothing. They can never lose more than the 620 paid, and nobody can liquidate them.

**Trading before settlement.** At 05:30 BTC is at 100 300 and Yes bids 0.85. The trader sells and realises 850 USDC without waiting. Outcome fees are charged only when closing or settling, and are currently zero during testing. The merged book means this sale is also a purchase of No by whoever takes the other side at 0.15.

**The settlement rule.** The target price is not the mark at 06:00 exactly. It is a linear interpolation between the mark updates immediately before and after the settlement time. Suppose the mark was 100 000 at 05:59:58 and 100 060 at 06:00:01. Two of the three seconds have elapsed at 06:00:00, so the interpolated price is 100 000 plus two thirds of 60, which is **100 040**. That is below 100 050, so the market settles **No**, even though BTC was above the target one second later. A holder close to the target is effectively holding a bet on a few seconds of price movement.

**Arbitrage across a question.** For a question with three outcomes (A, B and the automatic fallback), exactly one settles Yes. If the best Yes asks are 0.30, 0.35 and 0.30, buying one Yes of each costs 0.95, and `mergeQuestion` redeems the set for one quote token immediately: 0.05 of risk-free profit per set before fees. That arbitrage is what keeps the sum of Yes prices near one. `negateOutcome` ties the No price of each outcome to the Yes prices of the others in the same way. At the time of writing, multi-outcome questions are not part of the mainnet release.

## Judging a market before trading it

A HIP-3 or HIP-4 market carries the quality of whoever deployed it, so the questions worth asking before trading are about that market, not about Hyperliquid in general. Every item below can be read from the public info endpoint.

| What to check | What it tells you | Where to read it | Warning sign |
|---------------|-------------------|------------------|--------------|
| Order-book depth | How much size the market absorbs before the price moves | `l2Book` | Most depth from one ladder or one maker |
| Bid-ask spread | The round-trip cost of a small trade | `l2Book` | Spread wider than the expected move you are trading |
| Impact prices | Slippage for a standard notional | `impactPxs` in `metaAndAssetCtxs` (with `dex`) | Impact prices far from the mid |
| Open interest against its cap | Whether you can add to a position, and whether one trader dominates | `openInterest` in `metaAndAssetCtxs`; caps in `perpDexs` and `perpDexLimits` | OI close to the cap, so orders fail with `PositionIncreaseAtOpenInterestCap` |
| Funding rate | The carry cost of holding the position | `funding` in `metaAndAssetCtxs`; deployer multipliers in `perpDexs` | Funding multiplier far from 1, or persistent extreme funding |
| Oracle against mark against external price | Whether the deployer's price agrees with the market | `oraclePx`, `markPx` in `metaAndAssetCtxs`; an independent source for the underlying | Persistent gaps, or prices that move in steps of exactly 1% |
| Margin mode and leverage | How the market behaves under stress | `perpDexs`, margin tables | High leverage on an illiquid underlying; cross margin absent where the backstop needs it |
| Market status | Whether trading is live | `perpDexStatus` | Recent halts or settlements |
| Token supply and holders (spot) | Who can sell and how much | `tokenDetails` | Large genesis balances at a few addresses |
| Outcome specification (HIP-4) | What exactly settles the market, and when | `outcomeMeta`, `outcomeTemplates` | Free-text keywords that admit two readings |

### Exit risk

Being unable to close a position costs as much as being wrong about it. On a HIP-3 market the exits can close in four ways: the book is too thin for the size; the deployer halts trading, which settles every position at the current mark; an open-interest cap blocks orders that would flip a position; or the market is delisted. On a HIP-4 market the only certain exit is settlement, and before that the book may be empty. On a HIP-1 market with a Hyperliquidity ladder, the strategy only bids where it has previously sold tokens, so the bid side can be empty for a newly launched token.

### Evaluating a deployer

The deployer is the counterparty to every trust assumption in a HIP-3 or HIP-4 market. A few signals can be read onchain:

- **Whose stake backs the bond.** A self-bonded deployer bears its own slashing; a deployer backed by a liquid staking token passes the risk to the LST's depositors, which the HIP-3 specification flags explicitly.
- **Who updates the oracle.** `perpDexs` returns the deployer and the `oracleUpdater`. A separate updater key reduces the damage of one compromise but adds a key to protect.
- **Who else can act.** Sub-deployers can be granted individual actions, including `setOracle` and `haltTrading`. Each grant is another key with the same power over the market.
- **What the deployer earns.** A fee scale up to 3 under normal mode, with the protocol fee raised to match above 1, gives the deployer revenue proportional to volume. Nothing in the documentation prevents a deployer from also trading on its own DEX, and the deployer controls the oracle there.
- **What the deployer has done before.** Every deployer action is an onchain transaction. Halts, oracle gaps, parameter changes and fee changes (at most one per 30 days on mainnet) are all part of a public history.

## Validator discretion and its limits

Validators decide slashing by stake-weighted vote, and the amount applied is the stake-weighted median of their votes. The documentation sets out principles for those votes rather than an exhaustive rulebook, and it separates four cases that are easy to blur:

| Case | Example | Slashable? | Basis in the documentation |
|------|---------|------------|----------------------------|
| Irregular input that harms the protocol | A deployer input causing an invalid state transition or downtime | Yes: up to 100%, 50% or 20% depending on impact | HIP-3 slashing guidelines |
| Irregular input that causes no harm | An attempted malicious input the protocol absorbs | Yes | "Even attempted malicious deployer inputs that do not cause protocol issues are slashable" |
| Regular input that triggers a bug | A normal action exposing an implementation flaw | No; covered by the bug bounty if responsibly disclosed | "Inputs that do cause protocol issues but that are not irregular are not slashable" |
| Valid but objectionable behaviour | A deployer acting within its spec in a way users consider unfair | No; left to the application and social layers | "The protocol should not intervene in subjective matters" |

Three further triggers involve a validator judgment rather than a rule. Every time an asset's `externalPerpPx` moves more than 50% from its start-of-day value, validators review whether the deployer manipulated it. Assets with cross margin enabled must meet eligibility standards that validators enforce. And a HIP-4 market that contradicts its template's `semanticRestriction` is malformed and slashable. In each case the evidence is onchain, but the reading of "irregular" or "contradicts" is a vote.

**What recourse a deployer has.** The documentation describes no appeal procedure, no notice period and no published record of past votes. A deployer's recourse is the evidence (every deployer transaction is public and can be analysed by anyone) and the social layer. The specification itself says that the deployer's reputation is always at stake. A deployer who wants predictability has only the stated guideline levels and the principle that slashable behaviour should normally be matched by a protocol bug fix.

**When validators act outside slashing.** On 26 March 2025, a JELLY perp position of about 4.5 million USD was deliberately pushed into liquidation on a validator-operated market. The book was too thin to close it, so it passed to the liquidator vault, while the JELLY spot price was driven up about 250%. The vault's unrealised loss reached roughly 12 million USD, and ADL did not trigger. Validators voted to delist the asset and close the position at a price that removed the loss, and the Hyperliquid Foundation reimbursed affected long holders apart from addresses it flagged as involved ([OAK Research analysis](https://oakresearch.io/en/analyses/investigations/hyperliquid-jelly-attack-context-vulnerability-team-solution)). This was not a HIP-3 market and not a slashing vote. It shows that a validator supermajority can override prices when it judges the protocol threatened, and that reimbursement, when it happened, came from a foundation decision rather than from any mechanism a user could rely on in advance.

## Risks by proposal

The matrix gives the outline. The points below go into the risks that matter most in practice for each HIP.

### HIP-1

- **Token distribution and holder concentration.** Genesis balances are set entirely by the deployer and are visible in `tokenDetails`. HIP-1 has no vesting or lock-up, so a large genesis holder can sell from the first block.
- **Supply verification.** `maxSupply` is a ceiling that can only fall. For a bridged asset the deployer often puts the maximum value, up to `2^64-1`, in the token's system address, so the real circulating supply is whatever has crossed the bridge. Checking it means reading the system address balance and the HyperEVM contract, not the HyperCore `maxSupply`.
- **Bridge security.** A bridged HIP-1 token inherits every risk of the bridge that minted the ERC-20 (LayerZero, Axelar, Chainlink CCIP, deBridge and Wormhole are the ones the documentation names) and of whoever controls the ERC-20 contract. An unbacked mint on the HyperEVM can be moved to HyperCore through the system address like any other balance.
- **Freeze privilege.** The [Hyperliquid Python SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk) exposes `enableFreezePrivilege`, `freezeUser` and `revokeFreezePrivilege` for spot deployers. A frozen address cannot trade, send or receive the token. The deployment documentation does not list these actions, so before holding a token, check whether its deployer enabled the privilege and whether it was revoked.
- **Duplicate tickers.** A phishing token can carry the same six-character name as a popular one. Frontends may show a different display name again, since the annotation is set by the deployer. Only the token index and token ID are reliable identifiers.

### HIP-2

The worked example covers the main points: the ladder is one-sided at launch unless bids are seeded, it holds all its inventory on one side of the current price, it cannot react to external prices, and it disappears from the book once the price leaves its range. The deployer's choice of `startPx` and `nOrders` fixes the range for good, so a token that succeeds beyond the top level, or fails below the start, trades only on whatever other makers provide.

### HIP-3

- **Oracle failures.** A wrong feed, a stale feed and a compromised updater key are the three cases, and the 1% clamp slows the first and the last without preventing them. The stale case hands the mark to the local book.
- **Deployer incentives.** Fee revenue rewards volume, and growth mode rewards new markets with lower fees. Neither rewards prudent leverage limits. The deployer's stake is the only economic counterweight, and it is not paid to users.
- **Market manipulation.** Thin books are easier to push, and the backstop liquidator only accepts assets with cross margin enabled. An isolated-only asset on a thin book goes from liquidation to ADL with fewer intermediate steps.
- **Liquidation and ADL.** The HIP-3 example shows a liquidation caused by the oracle. If the liquidated position is large relative to the book, ADL closes profitable positions on the other side at the bankruptcy price, and those traders lose unrealised gains without having done anything.
- **HIP-3\* venues.** On testnet, a HIP-3\* deployer approves who may trade and can cancel an approved user's orders, force reduce-only, place reduce-only orders for them and move their collateral within the venue. That is a trust level close to a custodial venue, and a user should treat it as one.

### HIP-4

- **Resolution-source reliability.** Protocol-run recurring markets settle on HyperCore's own mark price, so their resolution source is the validator oracle. Deployer-created markets settle when the deployer sends `settleOutcome`; the template fixes what the market means, but no oracle reads the result. The source is the deployer.
- **Ambiguous outcomes.** Templates use typed keywords to limit ambiguity, but free-text `string` keywords still allow wording that admits two readings. Standalone outcomes can settle to a fraction (for example 0.66), which a deployer could use for a partial result; question outcomes must settle to exactly 0 or 1.
- **Settlement timing.** For recurring markets the interpolation rule decides close calls within seconds. For deployer markets the documentation does not state a deadline by which the deployer must settle after the event, and capital stays locked until it does.
- **Disputes.** There is no challenge window of the kind an optimistic oracle provides. A holder who thinks a market settled wrongly has one route: validators finding that the settlement contradicted the template's `semanticRestriction`, which can slash the deployer but is not documented as reversing the settlement.
- **Pre-settlement economics.** A Yes share is worth its probability-weighted payoff, which is why the price moves with the underlying and can be sold before settlement. The merged book and the split and merge operations keep Yes and No prices summing to one, and `mergeQuestion` keeps the Yes prices of a question near one in total, as the arbitrage example shows.

## Conclusion

The HIP design puts permission behind a price and conduct behind a vote. In practice, a user's position in any HIP market depends on four things:

- **Losses are not compensated by the protocol.** Slashed stake is burned. The only reimbursement on record, after JELLY, was a discretionary foundation decision on a validator-operated market.
- **Clamps slow failures without stopping them.** A 1% clamp per oracle update still lets a wrong feed liquidate a 10x position in about 20 seconds.
- **Market quality is the deployer's quality.** Depth, oracle behaviour, leverage and settlement all come from one party, and every signal needed to judge that party is onchain.
- **HIP-4 swaps liquidation risk for settlement risk.** A share cannot be liquidated, but its value is decided by whoever settles it, at a timestamp that can turn on seconds.

The [developer reference]({{site.url_complet}}/2026/10/26/hyperliquid-hip-developer-reference/) turns these points into deployment and integration checklists.

![Mindmap of Hyperliquid HIP risks covering the risk matrix, worked examples for each HIP, market-quality checks, validator discretion and per-proposal risks]({{site.url_complet}}/assets/article/blockchain/hyperliquid/hyperliquid-hip-risks-market-quality.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Impact price** | The average execution price for a standard notional on each side of the book; the gap from the mid measures slippage. |
| **Local mark price** | The median of best bid, best ask and last trade on a market's own book; the fallback mark when a HIP-3 deployer stops updating. |
| **`oracleUpdater`** | The address allowed to call `setOracle` for a HIP-3 DEX, the deployer by default. |
| **Backstop liquidator** | The onchain strategy at `0x400..00 + dex_index` that takes over liquidations a HIP-3 DEX's book cannot absorb, for assets with cross margin enabled. |
| **Seeded level** | A Hyperliquidity level that starts as a bid funded with USDC instead of an ask. |
| **Interpolated settlement price** | The price a recurring HIP-4 binary settles on: a linear interpolation between the mark updates just before and after the settlement time. |
| **HIP-3\*** | A testnet-only HIP-3 variant with an allow-list and deployer-proxied user actions. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| Slashed stake is burned, never paid to users. | Do not present a deployer's bond as user protection in an interface. |
| A HIP-3 mark price can move 1% per update, at most every 2.5 seconds. | Model liquidation distance in updates, not only in percent. |
| A stale HIP-3 oracle falls back to the local mark after 10 seconds. | Alert on oracle staleness and treat the market as book-priced while it lasts. |
| A Hyperliquidity ladder posts no bids at launch unless levels were seeded. | Do not assume two-sided liquidity on a new HIP-1 token. |
| A recurring HIP-4 binary settles on an interpolated mark, not the mark at the timestamp. | Reproduce the interpolation when displaying the likely outcome near settlement. |
| HIP-4 deployer markets have no dispute window. | Show who settles a market and from which template before a user buys. |

## Frequently Asked Questions

**Q: A HIP-3 deployer is slashed 100% after a bad oracle price liquidates a trader. What does the trader get back?**

Nothing from the protocol. The specification states that slashed stake is burned rather than distributed to affected users, to avoid misaligned incentives between users and deployers. The trader's liquidation stands, and the bond's role was to make the deployer's error expensive beforehand.

**Q: Why does the 1% mark-price clamp not prevent the liquidation in the HIP-3 example?**

The clamp limits each update, not the total. Updates can arrive every 2.5 seconds, so eight consecutive 1% steps move the mark about 7.7% in roughly 20 seconds, enough to reach a 10x long's liquidation price at 2.5% maintenance margin. The 50% daily-move review does not trigger for a move that small.

**Q: Why does a new HIP-1 token with a Hyperliquidity ladder often have no bids?**

Hyperliquidity posts bids only where it holds USDC. With `nSeededLevels = 0`, every level starts as an ask funded with tokens, so the strategy has no USDC until someone buys. Bids appear only at levels that have been bought through, or at levels the deployer seeded with USDC at genesis.

**Q: In the HIP-4 example, BTC is above the target one second after 06:00 but the market settles No. Why?**

Recurring binaries settle on a linear interpolation between the mark updates immediately before and after the settlement time. With updates at 100 000 (two seconds before) and 100 060 (one second after), the interpolated price at 06:00 is 100 040, below the 100 050 target. The later price only counts through its weight in the interpolation.

**Q: What can a deployer do if validators slash it unfairly?**

The documentation describes no appeal process. The amount is the stake-weighted median of validator votes, and the evidence is the deployer's own onchain transactions. A deployer can only argue its case publicly and rely on the stated guidelines: irregular inputs are slashable, regular inputs that trigger bugs are not, and subjective disputes are out of scope.

**Q: Combine the HIP-3 and HIP-1 sections: why are thin books dangerous in both, but in different ways?**

In HIP-1 a thin book means slippage and possibly no exit, a loss limited to the trader's own trade. In HIP-3 a thin book also feeds the mark price when the oracle is stale, and decides whether a liquidation can be absorbed or reaches ADL. A thin perp book can therefore cost traders who were not trading at all.

## Gaps

The documentation leaves several points open that this article depends on:

| Gap | Why it matters | What to read or verify |
|-----|----------------|------------------------|
| Exact placement of re-placed Hyperliquidity tranches (same level or adjacent) | Determines the strategy's realised spread and the depth after a fill | HIP-2 specification; observe a testnet ladder |
| Whether the HIP-3 release rule can shorten the 183-day minimum | Decides when a deployer's stake stops being at risk | HIP-3 specification, Spec and Settlement sections |
| A deadline for deployer settlement of HIP-4 markets | Decides how long capital can be locked after an event | HIP-4 deployer actions |
| Whether slashed HIP-4 stake is burned like HIP-3 stake | The general principle suggests so, but HIP-4 does not say it | HIP-4 deployer actions |
| Maintenance margin rule on HIP-3 margin tables | The worked example assumes half the initial margin at maximum leverage, as on validator-operated perps | Margining and margin tiers documentation |
| JELLY figures | Taken from a third-party analysis, not from an official post-mortem | OAK Research analysis; Hyperliquid announcements of 26 to 27 March 2025 |

## References

### Hyperliquid documentation

- [HIP-1: Native token standard](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-1-native-token-standard) — genesis, auction, bridged assets
- [HIP-2: Hyperliquidity](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-2-hyperliquidity) — ladder parameters and update rule
- [HIP-3: Builder-deployed perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals) — staking, settlement, oracle, slashing, cross margin, backstop liquidator
- [HIP-3 deployer actions](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions) — `setOracle` clamps and timing, fee changes, HIP-3\*
- [HIP-4: Outcome markets](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-4-outcome-markets) — mechanics, merged books, questions
- [HIP-4 deployer actions](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions) — templates, `semanticRestriction`, settlement
- [Contract specifications, Recurring outcomes](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications#recurring-outcomes) — the interpolation rule
- [Info endpoint, Perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals) — `perpDexs`, `metaAndAssetCtxs`, `perpDexLimits`, `perpDexStatus`
- [Info endpoint, Spot](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot) — `tokenDetails`, `spotDeployState`, `outcomeMeta`

### SDK

- [hyperliquid-python-sdk](https://github.com/hyperliquid-dex/hyperliquid-python-sdk) — official Python SDK (commit `2fdb18f`, 2026-06-04); `examples/spot_deploy.py` shows the Hyperliquidity genesis address, `maxSupply` in wei and the freeze privilege

### Incident analysis

- [Hyperliquid and the JELLY attack: Context, vulnerability and team solution](https://oakresearch.io/en/analyses/investigations/hyperliquid-jelly-attack-context-vulnerability-team-solution) — OAK Research, 28 March 2025

### Related articles

- [Pricing a Lending Position During an Incident - What the Oracle Reads, When, and Who Bears the Gap]({{site.url_complet}}/2026/10/11/oracle-kinds-pricing-lending-position-incident/)
- [Traditional Futures vs. Perpetual Futures: A Technical Comparison]({{site.url_complet}}/2025/12/29/traditional-vs-perpetual-futures/)
- [Gnosis Conditional Tokens — Combinatorial Prediction Markets on ERC-1155]({{site.url_complet}}/2026/07/28/gnosis-conditional-tokens-framework/)
- [Hyperliquid HIP-1 to HIP-4 in Twelve Cards — The Definitions to Memorise]({{site.url_complet}}/2026/10/26/hyperliquid-hip-flashcards/)
