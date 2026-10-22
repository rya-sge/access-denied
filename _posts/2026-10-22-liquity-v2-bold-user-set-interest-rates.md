---
layout: post
title: "How Liquity V2 Works - BOLD, User-Set Interest Rates, Redemption Routing and Branch Shutdown"
date:   2026-10-22
lang: en
locale: en-GB
categories: blockchain defi ethereum
tags: liquity stablecoin defi ethereum lending liquidation oracle chainlink governance audit solidity
description: "Liquity V2 (BOLD) from its code, audits and whitepaper: user-set rates, redemptions by rate, batches, zombie troves, shutdown, and code-vs-paper gaps."
image: /assets/article/blockchain/defi/liquity/2026-10-22-liquity-v2-mindmap.png
isMath: true
isMermaid: true
---

[Liquity V2](https://www.liquity.org/) is the second version of the Liquity borrowing protocol on Ethereum. Users lock ETH, wstETH or rETH and mint BOLD, a dollar stablecoin, and each borrower chooses the annual interest rate they pay. Redemptions take collateral from the troves with the lowest rates first, so the rate a borrower picks is also how much redemption risk they accept.

V2 keeps the core of [Liquity V1]({{site.url_complet}}/2026/10/22/liquity-v1-lusd-troves-stability-pool/): immutable contracts, a Stability Pool that absorbs liquidations, redistribution as a backstop, and redemptions at face value. Around that core it adds interest, several collateral branches, NFT troves, delegation to rate managers, and a permanent shutdown for a branch whose collateral or oracle fails. This article describes the system from the `liquity/bold` and `liquity/V2-gov` repositories, the public audit reports, and the whitepaper rev. 0.3 of November 2024. It ends with the points where the deployed code differs from that whitepaper.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What you need to know first

The article assumes familiarity with DeFi and stablecoins, and with the V1 design described in the [Liquity V1 article]({{site.url_complet}}/2026/10/22/liquity-v1-lusd-troves-stability-pool/). It uses these more specific mechanisms without re-deriving them.

- **Stability Pool and redistribution.** A pool of stablecoin deposits cancels a liquidated position's debt in exchange for its collateral. What the pool cannot cover is shared among the remaining positions. V2 keeps both stages, per collateral branch.
- **Redemption.** Anyone can burn the stablecoin for 1 USD of collateral minus a fee, taken from specific positions. This sets a price floor near 1 USD.
- **Liquid staking token (LST).** A token such as Lido's wstETH or Rocket Pool's rETH represents staked ETH and accrues staking rewards. Its value is the ETH it redeems for at the issuer's exchange rate, the *canonical rate*, which can differ from its market price.
- **Push oracle with a deviation threshold.** A Chainlink feed updates on-chain only when the price moves by more than a threshold (for example 2% for RETH/ETH) or a heartbeat expires, so the on-chain price lags the market by up to that threshold.
- **Debt shares.** When several positions share one debt balance, each holds shares and its debt is `shares × total debt / total shares`. Rounding in this conversion is a classic source of exploits, and V2 uses it for batches.
- **Flash-loan callback.** A contract borrows tokens, receives them in a callback, and must repay in the same transaction. The callback must check who started the loan, not only who sent it.
- **Gauge voting.** Token holders vote each epoch on how a stream of rewards is split between recipients, a model popularised by Curve. V2 governance uses it for the share of interest that does not go to the Stability Pools.

## What changed from V1

| Feature | Liquity V1 | Liquity V2 |
|---|---|---|
| Stablecoin | LUSD | BOLD |
| Collateral | ETH only | WETH, wstETH, rETH, one branch each |
| Borrowing cost | One-off fee, no interest | Annual rate chosen by the borrower, plus a 7-day upfront fee |
| Redemption order | Lowest collateral ratio first | Lowest interest rate first, per branch |
| Minimum ratio | 110% | 110% (WETH), 120% (LSTs) |
| System stress | Recovery Mode below 150% TCR | Borrowing limits below CCR; permanent branch shutdown below SCR or on oracle failure |
| Position | One per address | ERC-721 trove NFT, many per address |
| Delegation | None | Add and remove managers, interest delegates, batch managers |
| Stability Pool yield | Liquidation gains and LQTY | Liquidation gains and 75% of interest |
| Governance | None | LQTY votes on where the remaining 25% of interest goes |

## Architecture: one registry, several branches

A single `CollateralRegistry` and a single `BoldToken` sit above one *branch* per collateral. Each branch is a full V1-like system with its own troves, Stability Pool and price feed, wired together by an `AddressesRegistry`. Collateral never mixes across branches: a liquidation on the rETH branch is paid in rETH to the rETH Stability Pool and redistributed only to rETH troves.

```mermaid
flowchart TD
    CR[CollateralRegistry<br/>redemption routing, baseRate]
    BT[BoldToken]
    subgraph WETH branch
      BO1[BorrowerOperations] --> TM1[TroveManager]
      TM1 --> SP1[StabilityPool]
      TM1 --> ST1[SortedTroves by rate]
      TM1 --> PF1[WETHPriceFeed]
    end
    subgraph wstETH branch
      TM2[TroveManager] --> SP2[StabilityPool]
      TM2 --> PF2[WSTETHPriceFeed]
    end
    subgraph rETH branch
      TM3[TroveManager] --> SP3[StabilityPool]
      TM3 --> PF3[RETHPriceFeed]
    end
    CR --> TM1
    CR --> TM2
    CR --> TM3
    TM1 -. interest .-> IR[InterestRouter = Governance]
```

Inside a branch, the contracts keep V1's names and roles, with three additions:

- **`TroveNFT`** makes each trove an ERC-721 token. The trove ID is the hash of the caller, the owner and an owner index.
- **`ActivePool`** tracks the branch's aggregate debt and mints the interest it accrues.
- **Periphery.** `HintHelpers`, `MultiTroveGetter`, `RedemptionHelper` and `DebtInFrontHelper` are read helpers. The zappers open and adjust troves from raw ETH and build leveraged positions with flash loans.

The branch parameters are constants in `Dependencies/Constants.sol`:

| Parameter | WETH branch | wstETH and rETH branches |
|---|---|---|
| MCR (liquidation threshold) | 110% | 120% |
| CCR (borrowing restrictions) | 150% | 160% |
| SCR (shutdown threshold) | 110% | 120% |
| BCR (extra ratio for troves in a batch) | 10% | 10% |
| Liquidation penalty, Stability Pool | 5% | 5% |
| Liquidation penalty, redistribution | 10% | 20% |

The other global constants are a minimum debt of 2,000 BOLD, rates between 0.5% and 250%, a liquidation reserve of 0.0375 WETH per trove, and a 75% share of interest for the Stability Pools (`SP_YIELD_SPLIT`).

## Interest rates and upfront fees

### Accrual and minting

Each trove records its debt, its annual rate $$r$$ and the time of its last update. Interest accrues as simple interest and is compounded each time the trove is touched:

$$
\begin{aligned}
\text{debt}(t) = \text{debt}(t_0) \cdot \left(1 + r \cdot \frac{t - t_0}{\text{1 year}}\right)
\end{aligned}
$$

Updating every trove at every operation would be too expensive, so `ActivePool` keeps the branch total as `aggRecordedDebt` and the weighted sum $$\sum_i d_i r_i$$ as `aggWeightedDebtSum`, where $$d_i$$ and $$r_i$$ are the debt and rate of trove $$i$$. Every operation that changes debt first mints the interest pending since the last mint as new BOLD. 75% of it goes to the branch's Stability Pool and 25% to the `InterestRouter`, which on mainnet is the governance contract.

The core invariant, corrected during the ChainSecurity audit, is that the individual debts add up to the aggregate plus pending interest plus the redistributed debt not yet applied:

$$
\begin{aligned}
\sum_i d_i = \text{aggRecordedDebt} + \text{pendingAggInterest} + \text{DefaultPool debt}
\end{aligned}
$$

### Fees that stop borrowers dodging redemptions

Since redemptions follow the rate order, a borrower could watch for an incoming redemption, raise their rate just before it, and lower it afterwards. They could also close and reopen their trove. Two fees make this costly. Both equal **7 days of the branch's average interest** on the trove's debt:

$$
\begin{aligned}
\bar r &= \frac{\sum_i d_i r_i}{\sum_i d_i} \\
\text{upfront fee} &= \text{debt} \cdot \bar r \cdot \frac{7 \text{ days}}{\text{1 year}}
\end{aligned}
$$

- **The upfront borrowing fee** is charged when a trove is opened or its debt increased, and added to its debt.
- **The premature adjustment fee** is charged when a trove changes its rate less than 7 days (`INTEREST_RATE_ADJ_COOLDOWN`) after its previous change. Joining a batch always pays it.

At an average rate of 5%, the fee is about 0.096% of the debt. The borrower passes a maximum fee, so a transaction does not execute at a fee the borrower did not expect.

## Redemptions

### Routing across branches

`CollateralRegistry.redeemCollateral` first splits the BOLD amount $$M$$ between branches, in proportion to each branch's *unbacked* debt, the part of its debt not covered by its Stability Pool:

$$
\begin{aligned}
U_b &= \max\left(0,\; D_b - SP_b\right) \\
M_b &= M \cdot \frac{U_b}{\sum_k U_k}
\end{aligned}
$$

A branch whose Stability Pool is small relative to its debt is treated as less trusted by the market, and is redeemed more. Branches that are shut down, or whose TCR is below the SCR, are excluded. If every eligible branch is fully backed, the split falls back to total debt.

### Order within a branch and "debt in front"

Within a branch, redemptions start with the trove that pays the lowest rate. The troves' collateral ratios play no part in the order. A borrower's risk is therefore measured by the *debt in front* of them: the total debt of troves with a lower rate, which a redemption must use up before reaching them. `DebtInFrontHelper` computes it, and the `bold-ir-management` rate manager targets a percentage of debt in front for the troves it manages.

The redeemer receives collateral worth the BOLD redeemed minus the fee, at the oracle price $$p_c$$:

$$
\begin{aligned}
c = m \cdot \frac{1 - f}{p_c}
\end{aligned}
$$

The fee portion stays in the redeemed trove as collateral, unlike in V1 where it went to LQTY stakers. A redeemed borrower therefore keeps a small premium.

### The redemption fee

The fee uses the V1 formula with different parameters, and is computed once in the registry for all branches:

$$
\begin{aligned}
b &\leftarrow b \cdot \delta^{m} + \alpha \cdot \frac{M}{N} \\
f &= \min\left(0.5\% + b,\; 100\%\right)
\end{aligned}
$$

where $$\delta$$ gives a half-life of 6 hours, $$m$$ is the minutes since the last fee event, $$\alpha = 1$$, and $$N$$ is the BOLD supply. At deployment, `baseRate` started at 100% (`INITIAL_BASE_RATE`), which blocked redemptions until BOLD fell below about 0.95 USD or the rate had decayed.

### Zombie troves

In V2, a redemption never closes a trove. A trove whose debt falls below 2,000 BOLD is flagged **zombie** and removed from the sorted list, so that many dust troves cannot clog redemptions. A zombie can only be adjusted back above the minimum debt or closed. Since a trove with little debt left has no reason to pay a high rate, the protocol keeps a pointer `lastZombieTroveId` to the last partially redeemed zombie, and the next redemption on the branch takes it first.

The zombie state has more transitions than any other part of the system: redemption, redistribution, `applyPendingDebt`, `adjustZombieTrove`, batch rate changes and liquidation all move a trove in or out of it. The audits found most of their redemption bugs there (see below).

## Liquidations and the Stability Pool

### Penalties and compensation

A trove is liquidated when its ICR falls below the branch's MCR. There is no Recovery Mode, so a trove above the MCR is never liquidated. The two V1 stages remain, with explicit penalties:

- **Stability Pool offset.** The pool burns BOLD equal to the debt and receives collateral worth the debt plus 5%. Any collateral above that goes to the `CollSurplusPool` for the borrower.
- **Redistribution.** The uncovered debt and collateral worth the debt plus 10% (WETH) or 20% (LSTs) are spread over the other active troves of the branch. The borrower can again claim any surplus.

The liquidator receives the 0.0375 WETH reserve plus 0.5% of the collateral offset by the Stability Pool, capped at 2 units of collateral. Since May 2025, a fully redistributed trove pays only the WETH reserve. A V1-style "just in time" liquidation is possible: deposit BOLD into the pool and liquidate in the same transaction.

### Restrictions below the CCR

When a branch's TCR falls below its CCR (150% or 160%), operations that would lower the TCR are refused. Debt increases and collateral withdrawals must leave the TCR higher than before, and a new trove can be opened only if the resulting TCR is at least the CCR. Liquidations still use the MCR. This replaces Recovery Mode without liquidating troves that are healthy on their own.

### The Stability Pool after the 2025 rework

The pool uses V1's product-sum accounting, extended with a third accumulator for BOLD yield. In March 2025, after a potential attack on the pool was found, the accounting was reworked:

- At least 1 BOLD (`MIN_BOLD_IN_SP`) always stays in the pool and cannot offset debt, so the pool can never be emptied.
- Since the pool cannot be emptied, epochs were removed. `P` now has 36 decimals (`P_PRECISION = 1e36`) and is rescaled by $$10^9$$ when it gets small.
- The error-correction terms of V1 were removed.

Depositors can claim their collateral and yield, or stash the collateral and compound the yield into their deposit. Unlike V1, withdrawals are not blocked while undercollateralized troves exist (see the whitepaper section).

## Delegation and batches

### Managers and delegates

A trove owner can grant three kinds of rights:

- **An add manager** may add collateral and repay debt. By default anyone can.
- **A remove manager** may withdraw collateral and borrow, with the funds sent to a chosen receiver. It also has add-manager rights.
- **An individual interest delegate** may change the rate within a range the owner sets, at most once per minimum period the owner chooses.

These rights stay attached to the NFT when it is transferred, so a buyer of a trove should check that no manager is set.

### Batch managers and debt shares

A batch manager registers a rate range, an annual management fee (up to 10%) and a minimum period between rate changes (at least 1 hour). Troves that join the batch share one debt balance: each holds shares, and a single rate change updates every member at once. Batch troves must keep an ICR of at least MCR + BCR (120% or 130%). The [`bold-ir-management`](https://github.com/liquity/bold-ir-management) canister on the Internet Computer is such a manager: it adjusts rates automatically to keep a target share of debt in front of its troves.

Share accounting is where the most serious bug of the audits was found. Converting debt to shares rounds down, so donating 1 wei of debt to a batch, combined with dust troves, raised the debt per share until a minimum-debt trove minted zero shares. The attacker could then push its debt onto the other members and mint unbacked BOLD (ChainSecurity CS-BOLD-001, Recon H-01). The fix caps the debt-to-shares ratio at $$10^9$$ (`MAX_BATCH_SHARES_RATIO`), burns all shares when a trove's debt is fully repaid, and lets anyone remove a trove from a batch above the cap with `kickFromBatch`. The kicked trove keeps the batch's rate and pays no fee.

## Price feeds and the redemption price

Each branch has a Chainlink-based feed, and the two LST feeds also read the issuer's canonical rate:

| Branch | Price for borrowing and liquidation | Price for redemptions |
|---|---|---|
| WETH | ETH/USD | ETH/USD |
| wstETH | STETH/USD × wstETH-stETH rate | max(STETH/USD, ETH/USD) × rate, if the two are within 1% |
| rETH | min(RETH/ETH market, canonical rate) × ETH/USD | max of the two, if within 2%, otherwise the min |

The redemption price gives the redeemer the *worse* of two prices whenever they are within the feed's deviation threshold. Without it, a redeemer could watch for a pending oracle update that raises the price, redeem at the stale lower price, and sell the extra collateral. The borrowing price takes the minimum of market and canonical prices, so a manipulated high price cannot mint excess BOLD.

If a Chainlink call reverts, returns 0 or is stale, or if the canonical-rate call fails, the feed falls back to `lastGoodPrice` (or a composite of the remaining sources) and **shuts the branch down**. Two audit findings shaped this path. A canonical-rate call without `try/catch` would have reverted every redemption, since redemptions loop over all branches (Coinspect BOLD-05). And a caller could give a `try` block just enough gas to fail while the remaining 1/64 still ran the shutdown (ChainSecurity CS-BOLD-030); the feed now compares `gasleft()` before and after the call.

## Branch shutdown and urgent redemptions

A branch shuts down when its TCR falls below its SCR (anyone can call `BorrowerOperations.shutdown`) or when its oracle fails. Shutdown is permanent:

- Pending interest and batch fees are minted, then interest stops accruing.
- Opening and adjusting troves, rate changes, batch operations and normal redemptions are disabled.
- Closing troves, liquidations, Stability Pool deposits and withdrawals remain possible, and the owner of the last trove can close it.
- `urgentRedemption` lets anyone redeem BOLD from that branch only, from any troves, with no fee and a 2% collateral bonus, so arbitrageurs clear its debt quickly.

If the branch's collateral is worth less than its debt, the shortfall is not socialized automatically. Part of the BOLD supply can end up unbacked, and the README suggests governance could redirect interest to burn BOLD until the hole is filled.

```mermaid
stateDiagram-v2
    [*] --> Normal
    Normal --> Restricted: TCR below CCR
    Restricted --> Normal: TCR back above CCR
    Normal --> Shutdown: TCR below SCR or oracle failure
    Restricted --> Shutdown: TCR below SCR or oracle failure
    Shutdown --> [*]: debt cleared by urgent redemptions and liquidations
```

## Governance and protocol-incentivized liquidity

The 25% of interest that does not go to the Stability Pools funds liquidity for BOLD. LQTY holders decide each week how it is split, through the `Governance` contract of `liquity/V2-gov`. Governance has no other power: the core contracts are immutable.

- **Deposits.** LQTY deposited in governance is staked in V1's `LQTYStaking` through a per-user `UserProxy`, so the voter keeps earning V1 fees.
- **Voting power** grows linearly with time: for a user with deposits $$m_i$$ made at times $$t_i$$, $$V(t) = \sum_i m_i (t - t_i) = t \cdot M - S$$. The contract stores each line as an amount and an offset $$S$$.
- **Epochs** last 7 days. During the first 6, users can vote for and veto *initiatives*. On the last day, they can only lower votes or add vetoes, so a bad initiative cannot be pushed through at the last minute.
- **Initiatives** are registered by anyone for a 100 BOLD fee: DEX gauges, Merkl campaigns, Curve gauges, bribe contracts. An initiative whose votes exceed 2% of all votes and its vetoes can claim a share of the epoch's BOLD proportional to its votes. The share of initiatives that do not qualify rolls over to the next epoch.
- **Bribes.** `BribeInitiative` lets third parties pay voters of an initiative in BOLD and one other token, by their share of the epoch's votes.

Governance received six audits, which found two Criticals and fifteen Highs between them. Most came from the first representation of voting power as an *average stake timestamp*, whose rounding made allocate-then-deallocate a non-zero operation and let a flash-loan stake shift what a deallocation subtracted. The current code stores each allocation's exact amount and offset and resets all allocations before each new one. One finding was accepted rather than fixed: vetoes can still be removed after the voting cutoff, which works like a late vote (ChainSecurity CS-V2Gov-012).

## Deployment history and audits

V2 has been deployed twice:

| Version | Commit | Date | Note |
|---|---|---|---|
| V4 | `ce0128a` | 13 Jan 2025 | First launch, after three audit rounds; osETH and ETHx branches had been dropped |
| V5 | `f87639d` | 3 Mar 2025 | Fix for a potential Stability Pool attack and pool rework; LST branches moved to 120% / 160%; maximum rate raised to 250%; BCR added |
| V6 | `2e901c7` | 6 May 2025 | Cantina competition fixes: `kickFromBatch`, closing the last trove after shutdown, liquidator compensation from the offset part only |
| V7 | `abe7cbf` | 14 May 2025 | Price feeds without owner; redeployment |

The public reports are listed in the documentation: two core audits and a review of the Cantina fixes by Dedaub, Recon, Chaos Labs (mechanism design), Certora (formal verification of batch equivalence), Coinspect (core, governance, redemption helper), ChainSecurity (core and governance), and a Cantina competition with 65 findings. Read together, they keep returning to the same few areas:

- **Batch accounting.** Share rounding, and the weighted debt and weighted fee accumulators that every batch path must update together (Dedaub found fourteen Mediums there in its first audit).
- **Zombie troves.** Lost pointers, zombies lifted above the minimum debt without becoming active again, and zombies whose batch could still change their rate.
- **Redemption inputs.** The redemption price leaking into other checks, and unbacked debt that includes debt redemptions cannot reach.
- **Shutdown as a terminal state.** The last trove could not be closed, a division by `totalStakes` could reach zero, and guards were missing on sibling entry points.
- **Zappers.** Flash-loan callbacks that checked only the lender (the class of bug behind the Prisma exploit on a V1 fork), and leftovers stuck when the core repaid less than requested.

## Whitepaper versus implementation

The whitepaper rev. 0.3 (November 2024) was written before the January 2025 launch. The redeployed code of May 2025 matches it on most parameters:

- the MCR, CCR and SCR of each branch;
- the 5% Stability Pool penalty and the 2% urgent-redemption bonus;
- the 0.5% to 250% rate range and the 7-day upfront and adjustment fees;
- the 75% yield split;
- the 0.5% redemption fee floor with a 6-hour half-life.

It differs on the points below.

### Behaviour that differs

| Topic | Whitepaper rev. 0.3 | Current code | Consequence |
|---|---|---|---|
| Stability Pool withdrawals | "Deposits can always be withdrawn unless there is undercollateralized debt in the respective borrow market" (as in V1) | `withdrawFromSP` has no such check | Depositors can exit ahead of a loss-making liquidation; the Cantina report lists this (3.2.3). |
| Borrowing below the critical threshold | "Creation of new debt in the affected market is prohibited" when TCR is below CT | A new trove may be opened if the resulting TCR is at least CCR | Borrowing with a high ratio helps the branch and is allowed; the Cantina report notes the README mismatch (3.2.6). |
| Redistribution penalty | The redistributed trove gives up its "remaining collateral" | Capped at 10% (WETH) or 20% (LSTs) above the debt; the rest is claimable by the borrower | Borrowers keep a surplus even when the pool is empty. |
| Liquidator compensation | "Effective gas costs plus a margin" | 0.0375 WETH reserve plus 0.5% of the collateral offset by the pool, capped at 2 units | A fixed formula; a fully redistributed trove pays only the reserve. |
| Voting power | "LQTY staked × (average) staking age" | Stored as an amount and an offset per allocation; a full reset before each allocation | Same quantity, but the representation changed after audits found rounding bugs in the average form. |

### Mechanisms the whitepaper does not mention

- **Zombie troves** and `lastZombieTroveId`. The whitepaper describes redemptions down the rate order, but not what happens to a trove left below the minimum debt.
- **The batch collateral buffer** (BCR, 10% above the MCR) and the 1-hour minimum period between batch rate changes. The whitepaper only says the delegate presets a waiting time.
- **The 10% cap on batch management fees.** The whitepaper gives "e.g. 0.05%" as an example.
- **`MAX_BATCH_SHARES_RATIO` and `kickFromBatch`**, both added to fix the share-inflation finding.
- **`INITIAL_BASE_RATE` of 100%**, which blocked redemptions at launch.
- **`MIN_BOLD_IN_SP`**, the 1 BOLD that always stays in each Stability Pool since the 2025 rework.
- **The separate redemption price** of the LST feeds, which takes the higher of the market and canonical prices when they are within the deviation threshold.

### Differences in wording only

- **Names.** The whitepaper calls the thresholds CT and ST; the code calls them CCR and SCR.
- **The symbol β.** In the whitepaper β is the decay factor and α = 1 is the spike parameter. In the code, `REDEMPTION_BETA` = 1 is described as 1/α, and the decay is `REDEMPTION_MINUTE_DECAY_FACTOR`, applied per minute.
- **ETH versus WETH.** The whitepaper speaks of ETH collateral and says it is wrapped "seamlessly" into WETH. The branch token is WETH, and the zappers wrap and unwrap at the edges.

The repository README itself is also behind the code in places. It gives a 72% yield split and a 1% urgent bonus, while `Constants.sol` has 75% and 2%. When the documents disagree, the constants file is the reference.

## Conclusion

Liquity V2 keeps V1's immutable, auction-free design and adds a market for interest rates. The way risk is shared follows from that addition.

- **Borrowers price their own redemption risk.** Redemptions follow the rate order, so a borrower chooses a rate relative to the debt in front of them, and the upfront and premature-adjustment fees (7 days of average interest) stop them from dodging a redemption at the last moment.
- **Interest funds the peg.** 75% goes to each branch's Stability Pool and 25% to liquidity incentives allocated by LQTY votes, so holding BOLD earns yield.
- **Branches isolate collateral.** Each collateral has its own troves, pool, feed and thresholds, and redemptions are routed toward branches whose debt is least covered by their pool.
- **Stress is handled per branch.** Below the CCR, borrowing that lowers the TCR is refused. Below the SCR or on oracle failure, the branch shuts down for good, and urgent redemptions with a 2% bonus clear its debt.
- **Most of the complexity is in batches and zombies.** The audits found their most serious bugs in debt-share rounding and in the below-minimum-debt state, and the fixes (the share-ratio cap, `kickFromBatch`, the zombie pointer) are not in the whitepaper.
- **The whitepaper is a design document, not a specification.** Stability Pool withdrawals, borrowing below the CCR, redistribution penalties and liquidator compensation all work differently in the deployed code.

![Mindmap of Liquity V2 covering branches and parameters, interest and upfront fees, redemption routing and zombie troves, liquidations and the Stability Pool, batches, price feeds and shutdown, governance, audits, and differences from the whitepaper]({{site.url_complet}}/assets/article/blockchain/defi/liquity/2026-10-22-liquity-v2-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **BOLD** | The dollar stablecoin of Liquity V2, minted by troves on every branch and redeemable for collateral. |
| **Branch** | The set of contracts for one collateral type, with its own troves, Stability Pool, price feed and thresholds. |
| **CollateralRegistry** | The contract that lists the branches, routes redemptions between them and holds the redemption `baseRate`. |
| **Trove NFT** | The ERC-721 token that represents ownership of a trove; one address can hold many. |
| **MCR / CCR / SCR** | The liquidation threshold of a trove, the system ratio below which borrowing is restricted, and the system ratio below which the branch shuts down. |
| **BCR** | The extra 10% collateral ratio, on top of the MCR, that troves in a batch must keep. |
| **User-set interest rate** | The annual rate between 0.5% and 250% that each borrower chooses and that orders redemptions. |
| **Debt in front** | The total debt of troves with a lower rate on the same branch, which a redemption reaches first. |
| **Upfront fee** | A fee of 7 days of the branch's average interest, charged on opening, on debt increases and on early rate changes. |
| **Unbacked debt** | A branch's debt minus the BOLD in its Stability Pool, used to split redemptions between branches. |
| **Zombie trove** | A trove whose debt fell below the 2,000 BOLD minimum after a redemption; it leaves the sorted list. |
| **Batch manager** | A delegate that sets one rate for every trove in its batch, within a registered range, for a management fee. |
| **Debt shares** | The units in which a batch's members hold its common debt. |
| **`MAX_BATCH_SHARES_RATIO`** | The cap of 1e9 on a batch's debt per share, introduced to prevent share-inflation attacks. |
| **Canonical rate** | The LST issuer's own exchange rate between the token and ETH, read alongside the market price. |
| **Redemption price** | The LST price used for redemptions, the worse of market and canonical prices for the redeemer. |
| **Shutdown** | The permanent state of a branch after TCR falls below the SCR or its oracle fails. |
| **Urgent redemption** | A fee-free redemption on a shut-down branch that pays a 2% collateral bonus. |
| **Initiative** | An address registered in governance that can receive a share of the 25% interest stream. |
| **Voting cutoff** | The last day of each 7-day epoch, when votes may only decrease and vetoes increase. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| The sum of trove debts equals aggregate recorded debt plus pending interest plus DefaultPool debt. | `ActivePool` aggregate updates on every operation | A batch path updates weighted debt and weighted fee differently, or omits redistribution gains. |
| A trove's share of batch debt is never minted at zero for non-zero debt. | `MAX_BATCH_SHARES_RATIO` check on share-increasing operations | The ratio cap is removed or skipped on a path other than redemption. |
| Every redemption fee and routing input counts only redeemable debt. | Exclusion of shut-down branches; `MIN_BOLD_IN_SP` | Zombie or sub-100% debt enters the unbacked portion. |
| A shut-down branch never resumes borrowing or interest accrual. | `shutdownTime` checks in BorrowerOperations and TroveManager | A sibling entry point lacks the shutdown guard. |
| Each Stability Pool keeps at least 1 BOLD. | `MIN_BOLD_IN_SP` in the offset and withdrawal paths | The pool is emptied and the product `P` collapses. |
| The rate changes that move a trove in the redemption order pay the premature-adjustment fee inside the cooldown. | Fee checks in rate change, batch join and batch rate change | A new path changes the rate without checking the trove's own timestamp. |

## Frequently Asked Questions

**Q: Why does V2 order redemptions by interest rate rather than by collateral ratio?**

In V1, borrowers could only protect themselves from redemptions by over-collateralizing, which wasted capital and made the 110% minimum mostly theoretical. Ordering by rate gives them a second dial: they pay more interest to have more debt in front of them, and that interest funds the Stability Pool yield that supports demand for BOLD. A trove's collateral ratio then only matters for liquidation.

**Q: A redeemer burns 1,000 BOLD while three branches have unbacked debt of 100, 50 and 100. What happens?**

The registry splits the amount in proportion to unbacked debt: 400 BOLD to the first branch, 200 to the second and 400 to the third. On each branch, the redemption starts with the zombie trove the pointer refers to, if any, then the trove with the lowest rate, and moves up. The redeemer receives collateral worth the BOLD minus the fee at each branch's redemption price, and the fee portion stays in the redeemed troves.

**Q: What do the upfront fee and the premature adjustment fee protect against?**

Two ways of dodging a redemption:

- Closing a trove before a redemption and reopening it afterwards. The upfront fee on opening makes this cost 7 days of average interest each time.
- Raising the rate just before a redemption and lowering it afterwards. A rate change within 7 days of the previous one pays the same fee, and joining a batch always pays it.

**Q: How could the batch share rounding bug mint unbacked BOLD, and how was it fixed?**

Shares are computed as `shares × debt increase / batch debt`, rounded down. By redeeming a trove down to one wei of debt and one share, then repeatedly donating one wei of debt and reopening troves, an attacker raised the debt per share until a 2,000 BOLD trove received zero shares. That trove's debt then belonged to the other members, and the attacker kept the BOLD.

The fix caps the debt-to-shares ratio at 1e9, burns all shares when a trove's debt is fully repaid, and lets anyone kick a trove out of a batch above the cap.

**Q: What happens to an rETH branch if the Rocket Pool exchange-rate call starts reverting?**

The price feed catches the failure, falls back to the last good price, and shuts the branch down permanently. Interest stops, normal redemptions and borrowing stop, and urgent redemptions open with a 2% bonus so the branch's debt is cleared. The other branches keep working, because the shutdown flag removes the branch from redemption routing. Before an audit fix, the canonical-rate call had no `try/catch`, and a revert would have blocked redemptions on every branch.

**Q: Name two places where the whitepaper and the deployed code differ in behaviour, and why it matters to a user.**

Two examples:

- **Stability Pool withdrawals.** The whitepaper says deposits cannot be withdrawn while undercollateralized debt exists, as in V1; the code has no such check. A depositor can therefore leave before a loss-making liquidation, and those who stay bear more of the loss.
- **Redistribution.** The whitepaper says a redistributed trove loses its remaining collateral; the code caps the penalty at 10% or 20% above the debt. The liquidated borrower keeps the surplus.

## Gaps

The following points are not settled by the sources used here.

| Gap | Why it matters | What to read or verify |
|-----|----------------|------------------------|
| The "potential attack to the protocol's Stability Pool" that led to the March 2025 rework is named but not described in the reports read. | It explains why epochs were removed and why the system was redeployed. | Liquity's announcement of the V2 relaunch and the PRs merged into V5 of `liquity/bold`. |
| The Cantina report gives no fix status for its 65 findings, and Dedaub's fix review does not map PRs to finding IDs. | The article states some issues as fixed from the code, not from the reports. | Compare each Cantina finding with commit `abe7cbf` of `liquity/bold`. |
| The analysed `bold` commit (September 2026) is later than the V7 redeployment commit. | Later commits may change frontend or periphery code compared with what is deployed. | `git diff abe7cbf d262669 -- contracts/src` and the verified source of the deployed contracts listed in `api.liquity.org/addresses/relaunch.json`. |
| The governance parameters come from the deploy script; ChainSecurity's notes mention a 1,000 BOLD registration fee where the script says 100. | Registration cost and thresholds decide how open initiative registration is. | `REGISTRATION_FEE()` and the other immutables on the mainnet `Governance` contract. |
| Market and on-chain figures (rate distribution, Stability Pool sizes, BOLD supply) are not covered. | Debt in front and the yield split only mean something against real numbers. | Liquity's dashboards and Dune queries referenced in `api.liquity.org`. |
| A third Dedaub governance audit report contains a fix-PR reference to an "H3" that does not exist in that report. | One governance fix may be mislabelled. | V2-gov PR #120 and the Dedaub report of 22 December 2024. |

## References

### Analyzed source

- [liquity/bold](https://github.com/liquity/bold) — analyzed at commit [`d262669ef3c4d37bf0544df3bb2624c07b8a5ee0`](https://github.com/liquity/bold/tree/d262669ef3c4d37bf0544df3bb2624c07b8a5ee0), 2026-10-22 (V7 redeployment commit: `abe7cbfbd465fba3812282c51773455766a70e96`)
- [liquity/V2-gov](https://github.com/liquity/V2-gov) — analyzed at commit [`8f4bff395ed4ef2023e98df12c078b65af94bb73`](https://github.com/liquity/V2-gov/tree/8f4bff395ed4ef2023e98df12c078b65af94bb73), 2026-10-22
- [liquity/bold-ir-management](https://github.com/liquity/bold-ir-management) — automated batch manager

### Liquity documentation

- [Liquity V2 whitepaper](https://liquity.gitbook.io/v2-whitepaper) (rev. 0.3, November 2024)
- [Liquity V2 documentation](https://docs.liquity.org/)
- *Technical Docs & Audits*, page of the Liquity V2 documentation that lists the reports below

### Audit reports

- [ChainSecurity, Liquity Bold smart contracts](https://www.chainsecurity.com/security-audit/liquity-bold-smart-contracts) (January and May 2025)
- [ChainSecurity, Liquity V2 Governance](https://www.chainsecurity.com/security-audit/liquity-v2-governance) (January 2025)
- [Dedaub, Liquity V2 first audit](https://dedaub.com/audits/liquity/liquity-v2-aug-28-2024/) (August 2024) and [second audit](https://dedaub.com/audits/liquity/liquity-v2-second-audit-nov-11-2024/) (November 2024)
- [Dedaub, Liquity V2 Cantina fixes review](https://dedaub.com/audits/liquity/liquity-v2-cantina-fixes-review-may-13-2025/) (May 2025)
- [Dedaub, Liquity V2 governance audits](https://dedaub.com/audits/liquity/liquity-v2-governance-1st-audit-aug-12-2024/) (August, November and December 2024)
- [Coinspect, Liquity Bold](https://www.coinspect.com/doc/Coinspect%20-%20Smart%20Contract%20Audit%20-%20Liquity%20-%20Bold%20-%20v241231.pdf) (December 2024) and [Bold Governance](https://www.coinspect.com/doc/Coinspect%20-%20Smart%20Contract%20Audit%20-%20Liquity%20-%20Bold%20Governance%20-%20v250120.pdf) (January 2025)
- [Certora, Liquity verification report](https://certora.cdn.prismic.io/certora/Z1tLJJbqstJ98b8J_LiquityVerificationReport.pdf) (December 2024)
- [Recon, Bold review](https://github.com/GalloDaSballo/bold-review) (2024)
- [Cantina, Liquity competition](https://cantina.xyz/portfolio/fca4f98a-7d24-49f1-9a3b-80e5e65b2b30) (March–April 2025)
- Chaos Labs, *Liquity V2 Mechanism Design Review*, September 2024 (linked from the Liquity technical docs)
- Coinspect, *Redemption Helper Smart Contract Audit*, October 2025

### Related articles

- [How Liquity V1 Works - LUSD, Troves, the Stability Pool, Redemptions and Recovery Mode]({{site.url_complet}}/2026/10/22/liquity-v1-lusd-troves-stability-pool/)
- [10 Key Differences Between MakerDAO and Liquity]({{site.url_complet}}/2024/12/16/10-Key-Differences-Between-MakerDAO-and-Liquity/)
- [How Polaris Works - pETH, the Power-Law Bonding Curve, Reserve Loans and pAsset Markets]({{site.url_complet}}/2026/10/21/polaris-peth-bonding-curve-passets/)
- [How Morpho Blue Works - Isolated Lending Markets, Shares, Liquidations and Bad Debt]({{site.url_complet}}/2026/10/10/morpho-blue-lending-markets/)
- [The Technical Concepts Behind the 2024 Crypto Hacks]({{site.url_complet}}/2026/10/07/crypto-hacks-2024-technical-concepts/)
- [Pricing a Lending Position During an Incident - What the Oracle Reads, When, and Who Bears the Gap]({{site.url_complet}}/2026/10/11/oracle-kinds-pricing-lending-position-incident/)
