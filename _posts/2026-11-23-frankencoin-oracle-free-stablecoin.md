---
layout: post
title: "How Frankencoin Works - an Oracle-Free Swiss Franc Stablecoin with Veto Governance and Challenge Auctions"
date:   2026-11-23
last_modified_at: 2026-11-25
lang: en
locale: en-GB
categories: blockchain defi ethereum
tags: stablecoin defi liquidation governance audit oracle ccip erc-4626 lending
description: "Frankencoin (ZCHF) from its contracts: self-priced positions, challenge auctions instead of an oracle, veto governance, the FPS reserve, FCS and seven audits."
image: /assets/article/blockchain/defi/frankencoin/frankencoin-oracle-free-stablecoin-mindmap.png
isMath: true
isMermaid: true
---

[Frankencoin](https://frankencoin.com) (ZCHF) is an ERC-20 stablecoin on Ethereum, with bridged copies on seven other chains, that is designed to track the Swiss franc. It is minted against crypto collateral, like DAI or LUSD, but it reads no price feed: a borrower declares the liquidation price of their own position, and anyone who thinks that price is too high can start an auction to prove it. Governance works the same way. Nothing is voted in; proposals pass after a waiting period unless a holder with enough voting power vetoes them.

Those two ideas, challenges instead of an oracle and vetoes instead of votes, shape every contract of the system. This article follows them through the source code of the `Frankencoin-ZCHF/Frankencoin` repository at commit `8b4c4ab` (September 2026): the minter registry, the positions and their auctions, the reserve held by the pool-share token FPS and its newer wrapper FCS, the savings module, the bridges and the cross-chain deployment. It then groups what seven audits from 2023 to 2026 found by bug class, and closes with a risk assessment.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What you need to know first

The article assumes familiarity with stablecoins and lending protocols, and relies on the following mechanisms without deriving them.

- **Collateralised debt position (CDP) and liquidation.** A borrower locks collateral and mints a debt token against it; when the collateral is worth too little, a third party repays the debt and takes the collateral at a discount. [MakerDAO]({{site.url_complet}}/2023/11/21/makerdao/) vaults and [Liquity troves]({{site.url_complet}}/2026/10/22/liquity-v1-lusd-troves-stability-pool/) are CDPs. Frankencoin calls them *positions*.
- **Price oracle.** A contract that publishes an off-chain price on-chain, such as a Chainlink feed. Every CDP named above decides liquidations from such a price; Frankencoin decides them from auction results instead.
- **Dutch auction.** An auction whose price starts high and falls over time; the first bidder to accept the current price buys. Frankencoin's challenges end in one, with the price falling linearly to zero.
- **Bonding curve.** A formula that sets the price at which a contract mints or burns its own token as a function of supply or reserves. The pool-share token FPS is issued and redeemed on one.
- **Optimistic (veto-based) governance.** A proposal takes effect after a delay unless someone with enough voting power objects. Safety then depends on someone watching, not on turnout.
- **Time-weighted votes.** Voting power equal to the token balance multiplied by how long it was held, so that freshly bought tokens carry almost no weight. FPS and FCS count votes this way.
- **[ERC-4626](https://eips.ethereum.org/EIPS/eip-4626) vault.** A standard interface for a token that represents shares of an underlying asset, with `deposit`, `redeem` and preview functions. FCS presents FPS behind this interface, with ZCHF as the asset.
- **Cross-chain token pool.** With Chainlink CCIP, a token pool on each chain burns or locks tokens on the source chain and mints or releases them on the destination; a [previous article]({{site.url_complet}}/2026/11/16/chainlink-ccip-architecture/) covers the protocol.

## The system at a glance

The contracts are in `contracts/` of the repository. The main ones, with the name used in the rest of the article:

| Contract | Role |
|---|---|
| `stablecoin/Frankencoin.sol` | The ZCHF token, the minter registry, the reserve accounting (`mintWithReserve`, `burn*`, `coverLoss`) |
| `equity/Equity.sol` (FPS) | Frankencoin Pool Shares: holds the reserve, issues shares on a bonding curve, computes time-weighted votes |
| `equity/shares/FCS.sol` | Frankencoin Shares: wraps FPS one to one as an ERC-4626 vault, now the canonical governance token |
| `minting/MintingHub.sol`, `Position.sol` | Opening, cloning and challenging positions; the auctions |
| `minting/PositionRoller.sol` | Moves debt from one position to another with a flash mint |
| `rate/Leadrate.sol`, `savings/*.sol` | The governance-set base rate and the savings module that pays it |
| `swap/StablecoinBridge.sol` | One-to-one minting against another Swiss franc stablecoin |
| `swap/UniswapAmplifier.sol`, `CurveAmplifier.sol` | Minters that lend the ZCHF side of a liquidity pool position |
| `stablecoin/BridgedFrankencoin.sol`, `bridge/`, `equity/BridgeAccounting.sol` | ZCHF and governance on other chains over CCIP |

The figure shows how value and permissions flow between them. Its dotted arrows, numbered 1 to 4, show the order in which an auction shortfall is absorbed.

```mermaid
flowchart LR
    GOV["FPS / FCS holders<br/>veto power"] -->|"deny within<br/>application period"| ZCHF["Frankencoin (ZCHF)<br/>minter registry"]
    PROP["Anyone"] -->|"suggestMinter<br/>fee to reserve"| ZCHF
    ZCHF -->|"isMinter"| HUB["MintingHub"]
    ZCHF -->|"isMinter"| OTHER["Other minters<br/>bridges, amplifiers,<br/>savings, roller"]
    HUB -->|"registerPosition"| POS["Positions<br/>self-declared price"]
    POS -->|"mintWithReserve"| ZCHF
    ZCHF -->|"reserve + fees"| EQ["Equity (FPS)<br/>reserve contract"]
    FCS["FCS wrapper"] -->|"holds FPS 1:1"| EQ
    CH["Challengers and bidders"] -->|"challenge / bid"| HUB
    HUB -.->|"auction shortfall"| L1["1. Position's reserve<br/>contribution, released"]
    L1 -.->|"2. shortfall above it"| EQ
    EQ -.->|"3. equity at zero"| L3["Other minters' reserves<br/>refunds scaled down"]
    L3 -.->|"4. reserve balance empty"| L4["coverLoss mints<br/>new ZCHF"]
```

Two points of the design matter for everything that follows. First, ZCHF is not upgradable, but it accepts new minting modules at any time; the contract comment calls this "flexible but conservative governance". Second, loss absorption is layered: a position's own reserve contribution first, then the equity of the FPS holders, then the reserves of other minters, and finally newly minted ZCHF. In the code, a settlement takes the whole shortfall from the Equity contract's ZCHF balance with `coverLoss` and, in the same call, releases the position's reserve contribution to equity; equity therefore falls only by the part of the shortfall above that contribution.

*Implementation:* `Frankencoin.sol`, contract comment (lines 10-16) and `coverLoss()` (lines 321-330); `MintingHub.sol`, `_finishChallenge()` (lines 222-251). *Source:* `gitbook/reserve.md` and `gitbook/risks.md`.

## Minters and veto governance

### Proposing a minter

Any address can propose a new minter. The proposal names the minter contract, an application period, a fee and a message. It fails unless the period is at least 14 days, an immutable `MIN_APPLICATION_PERIOD` set to 1,209,600 seconds at deployment, and the fee at least `MIN_FEE` of 1,000 ZCHF. The fee is transferred to the reserve as profit. The minter becomes active once the application period has passed from the time of the proposal; `isMinter` only checks that this activation time is set and lies in the past.

During the application period, a qualified holder can veto the proposal with `denyMinter`, which deletes the entry and emits `MinterDenied`. There is no other way to remove a minter: once active, a minter cannot be paused or removed, a property the team accepted when Code4rena raised it in 2023 (finding M-13).

*Implementation:* `Frankencoin.sol`, `suggestMinter()`, `denyMinter()` and `isMinter()` (lines 100-112, 167-172 and 344-346).

The registry's event history shows the process in use. By 24 November 2026 at 15:06 UTC (Ethereum block [26,485,804](https://etherscan.io/block/26485804)), ZCHF had emitted 17 `MinterApplied` and 5 `MinterDenied` events: 12 proposals became minters, and the 5 vetoes each came on the day of the proposal. One vetoed proposal, on 29 May 2026, carried the name of the CHFAU bridge approved a month earlier followed by an asterisk, from an address with the same first four and last four hex digits (`0x3e44a184…f6c1` against the bridge's `0x3e445ff4…F6C1`).

The FCS governance layer added a second route. A proposal through the FCS minter governance module requires an application period of 60 days and a fee of 1,200 ZCHF, and records an announcement. Anyone may call `denyUnannouncedMinter` against a minter that was proposed directly on ZCHF without such an announcement. The call denies that minter with the FCS contract's own voting power and pays the caller 10% of a reward pool funded by the announcement fees. The direct ZCHF route still exists with its 14 days, but as long as the FCS contract is itself qualified in FPS1, a minter that skips the announcement can be vetoed by anyone.

*Implementation:* `MinterGovernance.sol`, `MIN_APPLICATION_FEE`, `MIN_APPLICATION_PERIOD` and `denyUnannouncedMinter()` (lines 16-19 and 93-99).

One exception remains: an address that was announced once keeps its announcement after a direct veto on ZCHF, so it can be re-proposed directly with 14 days and `denyUnannouncedMinter` then reverts (FPS2 #028, risk accepted); it is left to qualified holders.

### Vetoes, quorum and time-weighted votes

A veto needs a *qualified* caller. The check adds the caller's votes to those of the helpers who delegated to it, and reverts unless the sum exceeds the quorum:

```solidity
// equity/Governance.sol, checkQualified() (lines 78-82)
if (_votes * 10000 <= QUORUM * totalVotes()) revert NotQualified();
```

The quorum depends on which contract is asked:

- **FPS1, the deployed Equity contract** (`0x1bA2…41B2`), requires **at least 2%** of all votes. The source compiled for ZCHF and the Equity contract it creates, as embedded in the mainnet deployment artifact, sets `QUORUM = 200` and compares with a strict `<`, so exactly 2% qualifies. The [verified source of `0x1bA2…41B2` on Etherscan](https://etherscan.io/address/0x1bA26788dfDe592fec8bcB0Eaff472a42BE341B2#code) (Solidity 0.8.20), read on 24 November 2026, declares the same constant and the same comparison. The FCS source describes the change as "Reduce the veto power threshold from 2% in FPS1 to 1% in FCS", and ChainSecurity's FPS2 report states "a qualifying quorum of 1% of total FPS2 voting power, compared to the 2% threshold in FPS1" (p. 9).

  *Source:* `scripts/deployment/deployments/mainnet/Frankencoin.json`, with the check `if (_votes * 10000 < QUORUM * totalVotes()) revert NotQualified();`, and `FCS.sol` (line 16).
- **FCS and the current source** use `QUORUM = 100`, that is more than **1%**; the source comment says the value "used to be 200 in earlier versions, most notably in FPS1". Exactly 1% is not enough, because the comparison was switched to `<=` with FCS.

  *Implementation:* `Governance.sol`, `QUORUM` and `checkQualified()` (lines 12-17 and 80-81).

The project documentation gives the same 1% for direct FPS1 actions, which is true of the current Equity source but not of the immutable deployed FPS1; the annex table [Documentation, deployment and source](#documentation-deployment-and-source) lists this and the other differences found.

An FCS holder acts through the FCS contract, which must itself be qualified in FPS1. The audit notes the consequence: once FCS holds the FPS1 quorum, the effective minimum to act is "as low as 1% of 2%" of FPS1 votes, about 0.02% (pp. 6, 31).

Votes are not balances. FPS stores, for each holder, an anchor time; votes equal balance multiplied by the time since the anchor, with 20 extra bits of sub-second resolution, and receiving tokens moves the recipient's anchor forward in proportion. Buying a large block of FPS the day before a vote therefore gives almost no votes. Delegation is transitive and does not remove the delegator's own right to veto.

Two tools destroy votes. `kamikaze` lets a holder remove someone else's votes by giving up the same amount of its own. FCS's `shoot`, described below, builds on it.

*Implementation:* `Equity.sol`, vote anchors, `votes()` and `kamikaze()` (lines 101-151, 171-187 and 200-220).

### What an approved minter can do

The trust placed in a minter is total. When the spender is a minter, a position registered by a minter, or the reserve, and the holder has not set an explicit allowance, ZCHF reports an infinite allowance. A minter can also mint, burn from any holder, and call `coverLoss`. The contract comment is explicit: "We trust minters and the positions they have created to mint and burn as they please".

*Implementation:* `Frankencoin.sol`, `_allowance()` (lines 119-128).

A hostile minter that survives its application period can therefore drain every balance. The veto window, and people who read proposals during it, are the whole defence.

The main consequence of veto governance is that the safety of every balance depends on qualified holders reading each proposal in time; see [Centralisation and governance](#centralisation-and-governance).

## Positions

### Opening a position

Opening a position deploys a full `Position` contract through `PositionFactory`. The hub's `openPosition` takes the ten parameters listed below, registers the new position with ZCHF, charges an opening fee of 1,000 ZCHF and pulls the initial collateral.

*Implementation:* `minting/MintingHub.sol`, `openPosition()` (lines 100-147).

| Parameter | Meaning | Checked in code |
|---|---|---|
| `collateral` | ERC-20 token locked | `decimals() <= 24`; must revert on a transfer above balance |
| `minCollateral` | Smallest balance a position or challenge may hold | `minCollateral * liqPrice >= 5,000 ZCHF` |
| `initialCollateral` | First deposit | `>= minCollateral` |
| `mintingMaximum` | Limit shared by the original and its clones | sanity bound on the price |
| `initPeriodSeconds` | Veto window before minting starts | `>= 3 days` (`Position.sol:168`) |
| `expirationSeconds` | Duration after the start | none |
| `challengeSeconds` | Length of each auction phase | **no lower bound** |
| `riskPremiumPPM` | Added to the leadrate | `<= 100%` |
| `liqPrice` | Self-declared liquidation price | `price * minCollateral <= limit * 1e18` |
| `reservePPM` | Share of each mint kept in the reserve | between 2% and 100% |

The collateral check is a probe: the hub tries to transfer `totalSupply() + 1` tokens to a dummy address and expects the call to revert. A token that returns `false` instead is rejected as `IncompatibleCollateral`. The liquidation price is stored with `36 - decimals` decimals, so that multiplying it by a raw collateral amount always gives 36 decimals.

*Implementation:* `MintingHub.sol` (lines 95-96 and 116-122).

The init period is the veto window for this position. Until the start time, a qualified holder can deny the position, which closes it for good. Proposing a position is thus governed exactly like proposing a minter, with a shorter minimum delay.

*Implementation:* `Position.sol`, `deny()` (lines 246-251).

### Minting: reserve contribution and upfront interest

A position refuses to mint while a challenge is open, during a cooldown, after expiry, or when the amount exceeds the family limit. Otherwise it asks ZCHF to mint with a reserve, and ZCHF splits the gross amount three ways: the reserve contribution and the interest fee go to the Equity contract, the rest to the borrower. ZCHF also records in `minterReserveE6` the reserve owed back to the borrower on repayment.

*Implementation:* `Position.sol`, `mint()` (lines 381-387). `Frankencoin.sol`, `mintWithReserve()` (lines 178-189).

Interest is charged once, at mint time, for the whole remaining term. The annual rate is the global leadrate plus the position's risk premium, and the fee fraction is:

$$
\begin{aligned}
f &= \min\left(1,\ \frac{(T_{exp} - \max(t, T_{start})) \cdot (r_{lead} + r_{risk})}{365\ \text{days}}\right) \\
w &= m \cdot (1 - f - \rho)
\end{aligned}
$$

where $$m$$ is the gross amount minted, $$t$$ the current time, $$T_{start}$$ and $$T_{exp}$$ the position's start and expiration, $$r_{lead}$$ and $$r_{risk}$$ the two annual rates, $$\rho$$ the reserve contribution and $$w$$ what reaches the borrower's wallet. In the documentation's example, a leadrate of 2% and a risk premium of 1% over 365 days give $$f = 3\%$$; the FAQ works through that 10,000 ZCHF mint with $$\rho = 10\%$$, and [the worked example](#a-worked-example) a WETH position. The recorded debt is always the gross amount $$m$$, of which the reserve contribution comes back on repayment. Repaying early does not refund the interest.

*Implementation:* `Position.sol`, upfront fee calculation (lines 366-379). *Source:* `gitbook/positions/open.md` for the example.

The collateral condition checked after every adverse change is:

$$
\begin{aligned}
c \cdot P \geq m_{out} \cdot 10^{18}
\end{aligned}
$$

where $$c$$ is the collateral balance, counted as zero below `minimumCollateral`, $$P$$ the liquidation price and $$m_{out}$$ the debt outstanding. The liquidation price is thus the price at which the collateral exactly covers the gross debt, reserve included.

*Implementation:* `Position.sol`, `_checkCollateral()` (lines 513-516).

### Cloning and the family limit

A borrower can also copy an existing position instead of proposing a new one. The hub creates an [EIP-1167](https://eips.ethereum.org/EIPS/eip-1167) minimal proxy of the original position, and the clone's initialisation copies the parent's price and requires an expiration no later than the original's.

A clone skips the 1,000 ZCHF opening fee and the init period, because the parameters it inherits were already exposed to a veto. The parent must not be challenged, cooling down or expired. The original and all its clones share one `limit`, tracked on the original.

*Implementation:* `MintingHub.sol`, `clone()` (lines 157-169). `Position.sol`, `initialize()` and the shared limit (lines 189-195, 200 and 219-241).

### Adjusting the price and cooldowns

An owner can lower the liquidation price at once if the collateral still covers the debt. Raising it is restricted in the current source: at most three times the current price, and only outside a cooldown, after which minting and withdrawals are blocked for 3 days. Other events also set a cooldown: one day after an averted challenge and three days after a successful one. Price changes are impossible while a challenge is open or after expiry.

The 3-day delay after a price increase is the window for challengers. A borrower who raises the price to mint more must wait three days, during which anyone who disagrees can challenge.

*Implementation:* `Position.sol`, price adjustment and cooldowns (lines 321-333, 537-543 and 568).

The main consequence for minting is that every borrower's reserve contribution is both the first buffer of its own position and, once equity is gone, a buffer for everyone else's; see [Loss sharing](#loss-sharing).

## Challenges: replacing the oracle with an auction

### Starting a challenge

A challenger starts by transferring its **own** collateral, of the same token as the position, into the hub. It also passes a minimum price, which protects it against the owner: if the owner lowered the price in a front-running transaction, the call reverts with `UnexpectedPrice`. The challenge size must be at least `minimumCollateral`, unless it covers what is left of a partly challenged position.

A challenge then runs in two phases of `challengePeriod` seconds each. Bids in both phases go through the same `bid` function, which dispatches them by timestamp.

*Implementation:* `MintingHub.sol`, `challenge()` and `bid()` (lines 178-194 and 207-220). `Position.sol`, `notifyChallengeStarted()` (lines 527-532).

```mermaid
sequenceDiagram
    autonumber
    participant C as Challenger
    participant H as MintingHub
    participant P as Position
    participant B as Bidder
    C->>H: challenge(position, size, minimumPrice)
    H->>P: notifyChallengeStarted(size)
    Note over C,B: Avert phase, from start to start + period
    B->>H: bid(number, size)
    H->>C: size x liqPrice in ZCHF, paid by bidder
    H->>B: challenger's collateral
    H->>P: notifyChallengeAverted, 1-day cooldown
    Note over C,B: Auction phase, price falls from liqPrice to 0
    B->>H: bid(number, size)
    H->>C: own collateral back + 2% of bid
    H->>P: notifyChallengeSucceeded, 3-day cooldown
    P->>B: position's collateral
    H->>H: repay debt, split excess or coverLoss
```

### Avert phase

Until `start + challengePeriod`, a bid **averts** the challenge. The bidder pays the challenger `size * liqPrice` in ZCHF and receives the challenger's collateral; the position is untouched apart from a one-day cooldown. The challenger may cancel by bidding on its own challenge without paying. A bid in the same block as the challenge is rejected, a fix for ChainSecurity finding CS-ZCHF-037.

*Implementation:* `MintingHub.sol`, `_avertChallenge()` with the guard `require(block.timestamp != _challenge.start)` (lines 254-269).

An avert is a sale at the liquidation price. If someone buys the challenger's collateral at that price, the market has confirmed that the collateral is worth at least the declared price, and the position is considered sound. The challenger, who bet the opposite, has sold its collateral at the liquidation price, which it thought too high.

### Auction phase and settlement

If the challenge is still open after the first phase, the auction price falls linearly from the liquidation price $$P$$ at $$t_0 + \tau$$ to zero at $$t_0 + 2\tau$$, where $$t_0$$ is the challenge start and $$\tau$$ the challenge period:

$$
\begin{aligned}
p(t) = P \cdot \frac{t_0 + 2\tau - t}{\tau}, \qquad t_0 + \tau \lt t \lt t_0 + 2\tau
\end{aligned}
$$

*Implementation:* `MintingHub.sol`, `_calculatePrice()` (lines 295-305).

A bid in this phase buys the **position's** collateral at $$p(t)$$, and settlement proceeds as follows:

1. The challenger gets its own collateral back. The bidder may instead ask for the return to be postponed into `pendingReturns`, which the challenger claims later; the option exists for tokens whose transfer to the challenger would fail, such as a blacklisted address.
2. The bidder pays the offer $$p(t) \cdot \text{size}$$; 2% of the offer goes to the challenger as a reward (`CHALLENGER_REWARD = 20000` ppm).
3. The position repays $$m_{out} \cdot \text{size} / c$$, the share of the debt matching the collateral sold, and its minting is blocked for 3 days.
4. If the remaining proceeds exceed that repayment, the excess is split: the reserve contribution ratio of it goes to equity, the rest to the owner. If they are smaller, `coverLoss` takes the difference from the reserve.
5. `burnWithoutReserve` burns the repayment and releases the position's reserve contribution to equity.

*Implementation:* `MintingHub.sol`, `_finishChallenge()` (lines 222-251). `Position.sol`, repayment share (line 563).

The documentation gives a numeric case in `gitbook/reserve.md`. A debt of 5,000 ZCHF is fully liquidated; the position's reserve contribution was 20%, or 1,000 ZCHF; the winning bid is 4,500 ZCHF. The challenger receives 90 ZCHF, 4,410 ZCHF remain against the 5,000 ZCHF burnt, and the 590 ZCHF shortfall comes out of the reserve. The 1,000 ZCHF reserve liability is released at the same time, so equity ends 410 ZCHF higher. The borrower's reserve contribution has absorbed the loss and more.

### Why no oracle is needed, and what that assumes

The auction does two jobs, price discovery and liquidation. An owner who declares too high a price can be challenged by anyone holding the same collateral; defending the price in the avert phase means buying the challenger's tokens at that price, which costs real money if the price is wrong. Nothing in the protocol needs to know the market price; it learns, through bids, whether the market agrees with the declared one.

The argument has conditions, which the documentation states: challengers must be able to obtain the collateral, and "a collateral asset wholly controlled by the position owner cannot support that mechanism". Auctions also take time. When the challenge period is set to several days, the protocol reacts to a crash days later than an oracle-triggered liquidation would, and the reserve contribution has to cover the price move over that time. The collateral framework sizes it accordingly: retained reserve at least the 99% value-at-risk over twice the auction duration plus 2%, rounded up to 5 percentage points.

*Source:* `gitbook/positions/auctions.md` and `frankencoin-collateral-assessments/framework/collateral-risk-framework.md`.

The main consequence of replacing the oracle with auctions is that recovery depends on challengers and bidders being present within two challenge periods; see [Collateral and market risk](#collateral-and-market-risk).

### Expired positions and forced sale

A position that reaches its expiration with debt outstanding is not liquidated by challenge but sold. Anyone can buy the collateral through `buyExpiredCollateral`, which prices it at ten times the liquidation price at expiry, falling linearly to one times over one challenge period, then to zero over a second one:

$$
\begin{aligned}
p_{exp}(t) = \begin{cases} P + 9P \cdot \dfrac{\tau - \Delta}{\tau} & 0 \leq \Delta \leq \tau \\ P \cdot \dfrac{2\tau - \Delta}{\tau} & \tau \lt \Delta \lt 2\tau \\ 0 & \Delta \geq 2\tau \end{cases}
\end{aligned}
$$

with $$\Delta$$ the time since expiration. The sale repays the debt from the proceeds and the position's assigned reserve, sends any surplus to the owner, and books a loss through `coverLoss` when the collateral is exhausted and the debt is not covered. The sale is blocked while a challenge is open, so that an owner cannot pre-empt a challenge near expiry by forcing a sale on themselves. Both rules are fixes from ChainSecurity's v2024 audit (CS-ZCHF2-001 and -002). The first generation of contracts (`minting/v1/`) had no forced sale at all.

*Implementation:* `MintingHub.sol`, `buyExpiredCollateral()` (lines 348-383). `Position.sol`, `forceSale()` with the `noChallenge` modifier (lines 433-464).

The main consequence of the expiry rule is that an under-collateralised position nobody challenges is only sold at its expiration, which can be years away; see [Collateral and market risk](#collateral-and-market-risk).

### Position lifecycle

```mermaid
stateDiagram-v2
    [*] --> Proposed: openPosition, init period of at least 3 days
    Proposed --> Closed: deny by a qualified holder
    Proposed --> Active: start reached
    Active --> Cooldown: price raised 3 d, averted 1 d, succeeded 3 d
    Cooldown --> Active: cooldown over
    Active --> Challenged: challenge
    Cooldown --> Challenged: challenge
    Challenged --> Cooldown: averted or settled
    Active --> Expired: expiration reached
    Expired --> Closed: repaid or forced sale
    Active --> Closed: collateral below minimum
```

## A worked example

This section follows one borrower with WETH collateral from the opening of a position to its liquidation. The collateral parameters come from the published WETH assessment of 3 November 2026: a retained reserve of 20%, an auction duration of 24 hours, a maturity of up to three years, and no tail-risk compensation, hence no risk premium. In the pinned code the challenge period sets the length of each of the two auction phases, so each phase lasts 24 hours. The liquidation price of 2,500 ZCHF per WETH and the minimum collateral of 2 WETH are the documentation's illustration of the 5,000 ZCHF minimum, not a market quote.

*Source:* `frankencoin-collateral-assessments/assessments/published/WETH.md` and `frankencoin-collateral-assessments/framework/collateral-risk-framework.md` (section 4.1); `gitbook/positions/open.md` for the challenge period and the price illustration.

The following values are assumed:

- **Rate and term.** A leadrate of 3% and a one-year term, so that the upfront fee is the 3% of the FAQ example. The leadrate read on chain was 1% on 24 November 2026 at 15:06 UTC (Ethereum block [26,485,804](https://etherscan.io/block/26485804)); at that rate the fee would be 100 ZCHF instead of 300, and the wallet would receive 7,900 ZCHF instead of 7,700.
- **Market prices.** 3,000 ZCHF per WETH at opening; 2,300 ZCHF when the challenge starts; 2,600 ZCHF in the avert case.
- **Bid timing.** In the auction case, the bidder acts 2.4 hours into the falling-price phase.

### Opening the position and minting

The borrower proposes a new position, pays the 1,000 ZCHF opening fee to equity and deposits 4 WETH. The minimum collateral is worth 2 × 2,500 = 5,000 ZCHF at the liquidation price, exactly the hub's lower bound. After an init period of at least three days without a veto, the borrower mints 10,000 ZCHF gross. At 2,500 ZCHF per WETH, 4 WETH cover exactly 10,000 ZCHF, so this is the most the position can mint. At the assumed market price the collateral is worth 12,000 ZCHF, and the market can fall by about 16.7% before it reaches the liquidation price.

| Item | ZCHF | Computation |
|---|---:|---|
| Reserve contribution, added to the minter reserve | 2,000 | 10,000 × 20% |
| Upfront interest, added to equity | 300 | 10,000 × 3% |
| Borrower's wallet | 7,700 | 10,000 × (1 − 20% − 3%) |
| Debt recorded in the position | 10,000 | gross amount |
| Repayment that closes the position, unimpaired reserve | 8,000 | 10,000 × (1 − 20%) |

The gross amount and the rate are those of the FAQ example; the 20% reserve of WETH replaces its 10%, which is why the wallet receives 7,700 ZCHF instead of 8,700 ZCHF.

### The market falls and a challenge starts

WETH falls to 2,300 ZCHF, 8% below the liquidation price. A challenger who holds 4 WETH transfers them to the hub and starts a challenge on the whole position, with 2,500 ZCHF as its minimum price. While the challenge is open, the position cannot mint, withdraw collateral or change its price.

The challenge can then end in two ways.

### Case A: the challenge is averted

Suppose the market recovers to 2,600 ZCHF and a bidder acts within the first 24 hours. The bidder pays 4 × 2,500 = 10,000 ZCHF to the challenger and receives the challenger's 4 WETH, worth 10,400 ZCHF at the market.

- **Borrower:** unchanged, with 7,700 ZCHF in the wallet, 10,000 ZCHF of debt and 4 WETH in the position; minting and withdrawals are blocked for one day.
- **Challenger:** 10,000 ZCHF instead of 4 WETH worth 10,400 ZCHF, a loss of 400 ZCHF, about 3.8% of the collateral posted.
- **Bidder:** 4 WETH worth 10,400 ZCHF for 10,000 ZCHF.
- **Reserve and equity:** unchanged.

### Case B: the auction runs and settles

Suppose instead that WETH stays at 2,300 ZCHF and nobody averts. After 24 hours, the auction price starts at 2,500 ZCHF and falls to zero over the next 24 hours; it reaches the market price after 24 × (1 − 2,300 / 2,500) = 1.92 hours. A bidder buys the 4 WETH 2.4 hours into the phase, 26.4 hours after the challenge started, when the price is 2,500 × 21.6 / 24 = 2,250 ZCHF.

| Settlement step | ZCHF | Computation |
|---|---:|---|
| Bidder pays | 9,000 | 4 × 2,250 |
| Challenger reward | 180 | 2% × 9,000 |
| Available for repayment | 8,820 | 9,000 − 180 |
| Repayment, all collateral sold | 10,000 | 10,000 × 4 / 4 |
| Shortfall paid by `coverLoss` from the reserve balance | 1,180 | 10,000 − 8,820 |
| Position's reserve contribution released to equity | 2,000 | 20% × 10,000 |
| Net change in equity | +820 | 2,000 − 1,180 |

*Implementation:* `MintingHub.sol`, `bid()` and `_finishChallenge()` (lines 207-251); `Position.sol`, `notifyChallengeSucceeded()` (lines 554-575); `Frankencoin.sol`, `burnWithoutReserve()` and `coverLoss()` (lines 224-235 and 321-330).

Each party ends as follows:

- **Borrower:** 7,700 ZCHF, no debt and no WETH; there is no excess to share. Repaying 8,000 ZCHF before the challenge would have returned 4 WETH worth 9,200 ZCHF, so the liquidation costs the borrower 1,200 ZCHF more than a repayment (*derived*).
- **Challenger:** its 4 WETH back and 180 ZCHF, about 1.96% of the value of the collateral it kept locked for 26.4 hours.
- **Bidder:** 4 WETH worth 9,200 ZCHF for 9,000 ZCHF, a margin of 200 ZCHF before gas and the price risk of reselling.
- **Reserve and equity:** the reserve balance falls by 1,180 ZCHF and the minter reserve by 2,000 ZCHF, so equity rises by 820 ZCHF. With the opening fee and the interest, this position has added 2,120 ZCHF to equity.

The same arithmetic reproduces the documentation's example: a 5,000 ZCHF debt, a 20% reserve and a 4,500 ZCHF bid give a 90 ZCHF reward, a 590 ZCHF shortfall and a 410 ZCHF gain for equity.

### The stress case: how far the price can fall

The question is how low the winning bid can be before equity, and not only the borrower, pays for the liquidation. Equity breaks even when the bid net of the challenger's 2% equals the part of the debt that the released reserve contribution does not cover. For a position minted up to its liquidation price, that gives the lowest clearing price per collateral unit:

$$
\begin{aligned}
p_{min} = P \cdot \frac{1 - \rho}{0.98}
\end{aligned}
$$

where $$P$$ is the liquidation price and $$\rho$$ the reserve contribution. For WETH, $$p_{min}$$ is 2,500 × 0.8 / 0.98 ≈ 2,040.82 ZCHF: the auction can clear about 18.4% below the liquidation price, or about 32% below the assumed opening price, before equity loses anything (*derived*). This is the sense of the documentation's warning that a 20% reserve "does not imply exactly 20% price protection after all costs".

The time over which that fall has to stay is the challenge itself: one challenge period of avert phase, then up to one more of falling price. The assessment measured, for that 48-hour horizon, a 99% value-at-risk of 13.39% and a worst observed fall of 17.43%. The assessment justifies the 20% against the worst observed fall; the framework's value-at-risk route, 13.39% plus 2% for the reward, also rounds up to 20%. The worst observed 48-hour fall therefore stays within the 18.4% only if a challenge starts as soon as the market crosses the liquidation price and a bidder pays close to the market price (*derived*).

*Source:* `frankencoin-collateral-assessments/assessments/published/WETH.md` (section Market Risk) and `gitbook/risks.md` (section Fundamental Depeg).

Beyond that point, equity pays the difference. If the bid clears at 1,800 ZCHF, 28% below the liquidation price, the bidder pays 7,200 ZCHF, the challenger receives 144 ZCHF, 7,056 ZCHF are available, and the 2,944 ZCHF shortfall exceeds the released 2,000 ZCHF: equity falls by 944 ZCHF. Once equity is zero, the reserve balance falls below the minter reserve and every other borrower's refund is scaled down; once the balance is empty, `coverLoss` mints the rest as new ZCHF.

## Incentives: why each actor takes part

The challenge mechanism and the veto both work only if third parties act. For each actor, what pays, what it costs, and when a rational actor would stay out:

- **Challengers** earn 2% of the winning bid, 180 ZCHF in case B. They lock their own collateral until a bid arrives, which takes up to two challenge periods, 48 hours for WETH, and they pay gas. In the avert phase they sell their collateral at the liquidation price, which loses money when the declared price was fair: 400 ZCHF in case A. The reward shrinks with the bid, so a challenge on collateral nobody wants pays little. A challenger stays out when it cannot obtain the collateral or when the expected reward does not cover gas and the capital locked; on a challenge of the minimum collateral, worth 5,000 ZCHF at the opening liquidation price, the reward is about 100 ZCHF if the auction clears near that price, and less after a price cut or on the remainder of a partly challenged position (*derived*).
- **Bidders** in the auction phase buy at a discount: the price falls through the market price, and the first bidder below the market takes the difference, 200 ZCHF in case B. Competition between bidders pushes the bid towards the market price minus their costs (*derived*). In the avert phase, buying at the liquidation price pays only when the market is above it. A bidder stays out without ZCHF to pay, without a market to resell the collateral in, or when the collateral falls faster than the auction price.
- **Position owners** have reasons to declare a price below the market. A price above it invites a challenge, and a successful one takes the collateral and the reserve contribution, with only the excess above the debt shared with the owner; a price raise blocks minting for three days, and each averted challenge blocks it for one day, which leaves time for another challenge. The check fails for an owner who controls the supply of the collateral, because then nobody can challenge; that is why the collateral framework requires a sufficient free float.
- **Governance holders** veto at the cost of gas, only above the quorum, and the veto pays them nothing. The one rewarded veto, `denyUnannouncedMinter`, is open to anyone, not only to qualified holders, and pays the caller 10% of a reward pool. The proposer pays the fee, 1,000 ZCHF for a position and 1,000 or 1,200 ZCHF for a minter. A position's fee stays in equity after a veto; of a minter's 1,200 ZCHF, up to 200 ZCHF refill the reward pool when it holds less than 1,000 ZCHF. Holders' reason to veto is their exposure: a bad position's loss reaches equity once its reserve contribution is used up. A holder below the quorum cannot veto alone, and a qualified one may expect someone else to watch (*derived*).
- **FPS and FCS holders** receive the opening and minter fees, the upfront interest and liquidation gains (820 ZCHF in case B), and pay savings interest and losses. Their capital is held for at least 90 days before an FPS redemption, and FCS redemptions are discounted when large. A holder who expects losses above that income has a reason to sell, which lowers the share price on the bonding curve rather than stopping the system.

*Implementation:* `MintingHub.sol`, `CHALLENGER_REWARD` and `OPENING_FEE` at lines 22 and 28. `MinterGovernance.sol`, `suggestMinter()`, `denyUnannouncedMinter()` and `denyMinter()` (lines 52-62 and 93-112). *Source:* `gitbook/positions/open.md` for the fee kept after a veto, and `frankencoin-collateral-assessments/framework/collateral-risk-framework.md` (section 3) for free float.

When nobody acts, the protocol's defaults apply:

- **No veto:** the proposal becomes active at the end of its application or init period.
- **No challenge:** the position runs until expiration and is then sold by forced sale; the FAQ covers this case.
- **No bid:** the auction price reaches zero after the second challenge period, the next caller takes the collateral for nothing, and the whole repayment becomes a shortfall for `coverLoss`.

*Implementation:* `MintingHub.sol`, `_calculatePrice()` (lines 295-305).

The main consequence is that every line of defence assumes a third party with capital and attention at the right time; see [Centralisation and governance](#centralisation-and-governance) and [Collateral and market risk](#collateral-and-market-risk).

## Reserve and equity: FPS

### Minter reserve and equity

The Equity contract holds one ZCHF balance that serves two purposes. The minter reserve is the sum of the reserve contributions still owed back to borrowers; equity is the rest of the balance, the capital of the FPS holders. Opening fees, minter application fees, interest and liquidation surpluses add to equity; savings interest and liquidation shortfalls are paid from it by `coverLoss`.

*Implementation:* `Frankencoin.sol`, `minterReserve()` and `equity()` (lines 131-161).

On 24 November 2026 at 15:06 UTC (Ethereum block [26,485,804](https://etherscan.io/block/26485804)), the ZCHF supply was 27,897,210, the minter reserve 7,495,604 ZCHF and equity 3,675,652 ZCHF, about 13% of the supply. The FPS price was 1,279.71 ZCHF for 8,616.74 FPS, that is three times equity divided by the share supply, as the bonding curve below requires.

`coverLoss` transfers the amount from the reserve; if the reserve balance is too small, it transfers what there is and **mints** the rest. Losses never make it revert. Once equity is exhausted, the reserve balance falls below the minter reserve, and the reserve returned to each repaying borrower is scaled down in proportion. That is how the third layer of loss absorption, other minters' reserves, takes effect: each repaying borrower recovers less of their contribution.

*Implementation:* `Frankencoin.sol`, `calculateAssignedReserve()`, `calculateFreedAmount()` and `coverLoss()` (lines 284-310 and 321-330).

### The FPS bonding curve

FPS holders own that equity. The share price is set to three times equity per share:

$$
\begin{aligned}
\pi = \frac{3E}{S}
\end{aligned}
$$

where $$E$$ is equity in ZCHF and $$S$$ the FPS supply, so the market capitalisation is always three times the equity. Both directions use the same curve and charge a 0.3% fee. Investing $$a$$ ZCHF mints $$\Delta S$$ new shares, and redeeming $$q$$ shares pays out the proceeds:

$$
\begin{aligned}
\Delta S &= S \cdot \left( \sqrt[3]{\frac{E + 0.997\,a}{E}} - 1 \right) \\
\text{proceeds} &= E \cdot \left( 1 - \left( \frac{S - 0.997\,q}{S} \right)^3 \right)
\end{aligned}
$$

Supply grows with the cube root of equity; the contract's comment gives the table: 1,000 ZCHF of equity for 1,000 FPS at a price of 3, one million for 10,000 FPS at a price of 300. Profits and losses move the price with the supply unchanged.

*Implementation:* `Equity.sol`, share price and bonding curve (lines 36, 92-99, 257-265 and 316-323).

Three rules restrict the use of FPS:

- **Holding period.** Redemption requires an average holding duration of at least 90 days (`MIN_HOLDING_DURATION`), computed from the same anchor as the votes.
- **Minimum equity.** Investing requires at least 1,000 ZCHF of equity, and at least one share must remain after a redemption.
- **Recapitalisation.** When equity falls below 1,000 ZCHF, a qualified holder may call `restructureCapTable` and burn the FPS of any listed addresses without paying them, which is the path for recapitalising the system after its equity has been wiped out.

*Implementation:* `Equity.sol` (lines 51, 117-119, 232-235, 318 and 338-345).

### FCS: the share wrapper

FCS, for Frankencoin Shares, is defined in `equity/shares/FCS.sol`. The documentation now calls it the "canonical governance and share token". It was audited by ChainSecurity under the name FPS2 and renamed afterwards. FCS holds FPS one to one and exposes it as an ERC-4626 vault with ZCHF as the asset:

- **Entry.** `wrap` exchanges FPS for FCS and credits the votes the holder lost in FPS1; `deposit` and `mint` invest ZCHF into FPS1 through the vault interface.
- **Binding.** FCS is *binding* when it holds more than two thirds of all FPS1 votes. Only then are redemptions through FCS open, and only if FCS's own FPS1 holding satisfies the 90-day rule.
- **`shoot`.** While binding, anyone can call `shoot(target)`. The function does not check the caller: it only requires FCS to be binding and refuses FCS itself as a target. It destroys the target's FPS1 votes through `kamikaze`, paid for with an equal amount of the FCS contract's own FPS1 votes. Above two thirds, each shot raises FCS's share of the votes, which pushes FPS1 holders to migrate.
- **Exit.** `unwrap` is allowed only to holders whose holding duration is at or above the FCS average, which prevents gas-only wrap and unwrap loops that would drain FCS's votes.

*Implementation:* `FCS.sol`, `wrap()`, `redemptionsEnabled()`, `isBinding()`, `shoot()` and `unwrap()` (lines 52-61, 68-70, 77-79, 89-97 and 110-115). *Source:* `gitbook/README.md` for the "canonical" designation.

Redemptions through FCS pay the FPS1 proceeds multiplied by a discount factor:

$$
\begin{aligned}
d = \left( \frac{S - q/2}{S + R} \right)^4
\end{aligned}
$$

where $$S$$ is the FCS supply, $$q$$ the shares being redeemed and $$R$$ the recent redemptions, which decay linearly to zero over a 7-day `RECOVERY_PERIOD`. The withheld ZCHF stays in equity. With no recent redemptions, redeeming 10% of supply at once gives $$d = 0.95^4 \approx 0.81$$, so about a fifth of the proceeds stays behind; a small redemption gets close to the full price. `withdraw` is capped at 10% of supply per call, and the contract comments recommend spreading large exits over days or weeks.

*Implementation:* `FCSMintRedeem.sol`, withdrawal cap and discount factor (lines 201-262 and 343-348).

The main consequence of this reserve design is that, once equity is exhausted, losses pass to borrowers who were never liquidated and then to ZCHF holders through minting; see [Loss sharing](#loss-sharing).

## Leadrate and savings

The leadrate is the base interest rate. A qualified holder proposes a new rate, and anyone applies it after 7 days. Positions read it at every mint through the hub's `rate()`; it is the $$r_{lead}$$ of the fee formula above. Under FCS, `InterestGovernance` exposes separate proposals for the borrowing and the savings rate.

*Implementation:* `rate/Leadrate.sol`, `proposeChange()` and `applyChange()` (lines 40-55).

On 24 November 2026 at 15:06 UTC (Ethereum block [26,485,804](https://etherscan.io/block/26485804)), the V2 hub's `rate()` pointed to the `SavingsV2` contract `0x3BF3…B2aE`, whose `currentRatePPM()` returned 10,000 ppm, a leadrate of 1%. `nextRatePPM()` returned the same value, so no different rate was waiting to be applied.

The savings module pays the savings leadrate to deposited ZCHF as simple interest. Interest accrues in "ticks", a rate in ppm multiplied by seconds. A deposit starts earning after a 3-day delay, an optional referrer may take up to 25% of the interest, and interest is paid on refresh through `coverLoss`. Savings are thus a cost to equity, and, like any loss, they are minted once the reserve balance is empty. The legacy `SavingsV2` contract still deployed for the V2 hub differs: it locks withdrawals while interest ticks lie in the future and has no referral.

*Implementation:* `savings/AbstractSavings.sol` (lines 30, 82 and 218). `minting/v2/SavingsV2.sol` for the legacy module.

## Bridges, amplifiers and other minters

Positions are one kind of minter among several. Each of the following was or must be approved through the same veto process:

- **`StablecoinBridge`** mints ZCHF one to one against another Swiss franc stablecoin, up to an immutable limit, and stops minting 52 weeks after deployment. Mainnet bridges exist for XCHF, VCHF and CHFAU. The bridge has no loss write-off: if the other coin fails, the ZCHF minted against it stays in circulation. On 24 November 2026 at 15:06 UTC (Ethereum block [26,485,804](https://etherscan.io/block/26485804)), all three bridges were still minters, but only one could still mint:

  - XCHF closed on 26 October 2024; 0.017 ZCHF is still counted as minted against it.
  - VCHF closed on 15 April 2026, with nothing outstanding.
  - CHFAU stays open until 8 April 2027, with 550,290 ZCHF minted of its 10 million limit.

  *Implementation:* `swap/StablecoinBridge.sol` (lines 49-78).
- **`UniswapAmplifier`** lends the ZCHF side of a Uniswap V3 ZCHF/USD liquidity position, with the dollar side provided by the owner. The range is limited to about -14%/+10% around a price anchor fixed at deployment, and the owner must provide dollars worth at least four fifths of the borrowed ZCHF at the anchor. Its own comment warns that the amplifier "becomes exploitable as soon as the market price falls more than about 41% below the anchor price".

  *Implementation:* `swap/UniswapAmplifier.sol` (lines 16-29, 47-48 and 162).
- **`CurveAmplifier`** applies the same idea to a Curve pool, requiring the pool's oracle price to stay within 20% of the anchor recorded at deployment.

  *Implementation:* `swap/CurveAmplifier.sol` (lines 18 and 95).
- **`PositionRoller`** is a minter so that it can flash-mint. Its `roll` function mints the repayment amount to itself, repays the old position, withdraws the collateral, mints from or clones the target position, and burns the flash amount from the caller. Borrowers use it to extend a maturing loan.

  *Implementation:* `minting/PositionRoller.sol`, `roll()` (lines 112-132).
- **`TransferWithAuthorization`** is an [EIP-3009](https://eips.ethereum.org/EIPS/eip-3009) sidecar. Its deployment steps are to propose it as a minter, only to obtain the infinite allowance, which it then uses to execute signed transfers on behalf of holders. Whether it is an active minter today was not checked on chain.

  *Implementation:* `transfer/TransferWithAuthorization.sol` (lines 14-21).

The last item shows how the minter model can be used beyond minting: the infinite allowance makes any approved contract a fully trusted spender.

## Cross-chain deployment

ZCHF exists on Polygon, Arbitrum, Optimism, Base, Avalanche, Gnosis and Sonic as `BridgedFrankencoin`, at the same address on each, with the same minter and veto model; the addresses are listed in `exports/address.config.ts`. The CCIP token pool on each chain is a minter. Accounting flows back to mainnet:

- **Profits and losses.** On an L2, `coverLoss` mints any shortfall and books it as `accruedLoss`; later profits burn it down. A synchronisation call sends the net result to the accounting contract on mainnet, which collects profits into the reserve or covers the loss.

  *Implementation:* `stablecoin/BridgedFrankencoin.sol`, `coverLoss()` and `synchronizeAccounting()` (lines 206-257). `equity/BridgeAccounting.sol` (lines 27-69).
- **Votes.** Governance on an L2 needs mainnet voting power. Two sender contracts on mainnet push snapshots of selected holders' votes over CCIP to the bridged governance contracts of each chain. Snapshots cross, tokens do not, and a sync overwrites local delegations.

  *Implementation:* `GovernanceSender.pushVotes()` and `MainnetVotes.pushFCSVotes()`, received by `BridgedGovernance` and `BridgedVotes`. *Source:* `gitbook/governance.md`.
- **Bridge administration.** `CCIPAdmin` manages the token pool. Adding a remote pool or a chain is a proposal with a 7-day veto window, transferring the admin role takes 21 days, and setting rate limits is immediate for a qualified holder.

  *Implementation:* `bridge/CCIPAdmin.sol` (lines 103-212).

ChainSecurity's trust model for FCS states the dependency plainly: "If CCIP can relay incorrect values, Governance on that chain is fully compromised, which can lead to minting unlimited ZCHF on that chain" (FPS2 report, p. 9).

The main consequence of the cross-chain deployment is that supply and governance on every other chain inherit the trust placed in CCIP; see [External dependencies](#external-dependencies).

## What the audits found

### The reports

The repository and the auditors' sites hold seven stored reports, covering three generations of the code. A separate ChainSecurity CCIP Bridge assessment, cited by the FPS2 report, is not among them. The [timeline](#timeline) in the annex places the reports among the deployments.

| Report | Date | Scope | Findings as rated |
|---|---|---|---|
| Blockbite | 2023-02 | V1 core | 3 High, 3 Medium, 6 Low |
| [Code4rena contest](https://code4rena.com/reports/2023-04-frankencoin) | 2023-04, report 2023-06-09 | V1 core, 949 lines | 6 High, 15 Medium |
| ChainSecurity | 2023-10-30 | V1 core and bridge | 1 Critical, 3 High, 11 Medium, 16 Low |
| Decurity | 2024-09 | V2 minting and savings | 3 Critical, 3 High, 4 Medium, 5 Low |
| ChainSecurity *v2024* | 2024-11-28 | V2 | 2 High, 4 Medium, 4 Low |
| ChainSecurity *Uniswap Liquidity Amplifier* | 2026-07-30 | `UniswapAmplifier` | 1 Low, 6 Informational |
| [ChainSecurity *FPS2*](https://reports.chainsecurity.com/Frankencoin/ChainSecurity_Frankencoin_FPS2_Audit.pdf) | 2026-07-14 | FCS, governance modules, CCIP admin | 1 Critical, 3 High, 4 Medium, 9 Low, 11 Informational |

Across them: 5 Critical, 20 High and 41 Medium findings. The totals add ratings from auditors with different severity scales, and not every report uses a Critical level, so they describe volume rather than a common measure of risk. The five Critical ones are:

- **ChainSecurity V1, CS-ZCHF-034:** a dust position kept alive by a parallel self-challenge.
- **Decurity 5.1:** `buyExpiredCollateral` front-run by a price change.
- **Decurity 5.2:** a clone that could be re-initialised with a malicious parent.
- **Decurity 5.3:** a challenge period of a few seconds.
- **FPS2 #001:** `shoot` enabling a governance takeover.

### Bug classes

The findings cluster around the features that make Frankencoin unusual. The "today" column is checked against commit `8b4c4ab` and describes the source, not necessarily the deployed contracts.

| Class | Representative findings | Today |
|---|---|---|
| Competing liquidation paths | CS-ZCHF2-001: a forced sale of an expired position made challenging pointless; Decurity 5.1: the owner changed the price after expiry and front-ran the sale | `forceSale` is `noChallenge`, price changes require `alive` |
| Bad debt and reserve accounting | CS-ZCHF2-002: `forceSale` did not book bad debt; Code4rena H-06: the challenger reward, computed from the owner-set price, could drain the reserve | Reward is 2% of the bid; `forceSale` calls `coverLoss` |
| Owner-set values without bounds | Code4rena H-05: `adjustPrice(type(uint256).max)` made challenge arithmetic overflow; Decurity 5.3/5.6: a 30-second challenge period lets the owner win its own auction | Price raise capped at 3x; **no minimum challenge period**, left to the veto (acknowledged) |
| Dust and minimum collateral | CS-ZCHF-034; Code4rena H-03: a top-up just before settlement avoided the cooldown | Positions close below `minimumCollateral`; the 3-day cooldown is unconditional |
| Liquidation denial of service | Code4rena H-04: ownership moved to `address(0)` broke settlement; M-07: a blacklisted recipient stalls it | Zero owner rejected; challenger returns can be postponed, the position's own collateral transfer is still a push |
| Reentrancy and token behaviour | Code4rena H-02: double-entry-point collateral; CS-ZCHF-038: reentrant collateral minting during liquidation | In `bid`, the averting path transfers collateral before updating the challenge (`MintingHub.sol:263-268`); safe only for tokens without transfer hooks, which governance must keep out |
| Governance and votes | FPS2 #001: at a 50% binding threshold, shooting every other holder kept FCS binding and allowed unvetoable minting; #004: free wrap and unwrap loops drained FCS votes | Binding at 2/3, unwrap only above average holding, redemptions only while binding |
| Savings | Decurity 5.4 and 5.5: reward cursor advanced without payment, deposits on behalf of someone else blocked their withdrawal | 5.4 acknowledged, 5.5 fixed with the griefing risk accepted, both for `SavingsV2`; `AbstractSavings` has no withdrawal lock |
| Chain portability | Code4rena M-04: `block.number` used as a clock; FPS2 #006: old CCIP vote snapshots can be replayed | Timestamps now; stale snapshots accepted as a risk |

Code4rena's H-05 shows why an oracle-free design has its own attack surface. The owner sets the price that the liquidation arithmetic multiplies, so an extreme price is a denial of service on the one mechanism that replaces the oracle. The fix bounds the input in two ways: a raise is limited to 3x per step, and every price change checks that the price times the minimum collateral stays within the position's limit.

```solidity
// minting/Position.sol, _preparePriceIncrease() and _setPrice() (lines 330-338)
function _preparePriceIncrease(uint256 newPrice) internal noCooldown {
    if (newPrice > 3*price) revert PriceIncreaseTooHigh(3*price, newPrice);
    _restrictMinting(3 days);
}

function _setPrice(uint256 newPrice, uint256 bounds) internal {
    require(newPrice * minimumCollateral <= bounds * ONE_DEC18); // very important sanity check, see github.com/Frankencoin-ZCHF/FrankenCoin/issues/52
    price = newPrice;
}
```

### What is accepted rather than fixed

Several items stay in the code by design or by an accepted risk. They are part of the system's threat model rather than open bugs:

- No minimum challenge period; the veto and the front end are expected to reject short ones (Decurity 5.3).
- `coverLoss` mints when the reserve is empty, so losses dilute holders instead of reverting.
- A minter cannot be removed after its application period (Code4rena M-13).
- `restructureCapTable` burns FPS without payment once equity is below 1,000 ZCHF.
- An FPS redemption can front-run the booking of a loss (Code4rena M-15).
- Transfer-hook and double-entry collateral are kept out by governance, not by code.
- The stablecoin bridge has no write-off path (CS-ZCHF-002); its limit and expiry cap the exposure.
- FPS2 #006 and #025: stale cross-chain vote snapshots can be applied, and CCIP rate-limit changes take effect at once.

No audit among the stored sources covers `CurveAmplifier`, the bridged leadrate or the EIP-3009 sidecar. The team's own reviews of the Curve amplifier and the sidecar are design notes in `reports/`; nothing there covers the bridged leadrate. The FPS2 report had `AbstractLeadrate` and `BridgedFrankencoin` in scope, and it refers to a separate "CCIP Bridge code assessment" (p. 9) that is not among the stored sources.

## Conclusion

Frankencoin replaces the two external inputs most CDP stablecoins depend on, a price oracle and an active governance majority, with mechanisms that react to disagreement.

- **Prices come from auctions.** A borrower declares a liquidation price; a challenger who disagrees posts the same collateral; a bid at the declared price averts the challenge, otherwise a Dutch auction sells the position's collateral and pays the challenger 2% of the bid.
- **Governance is a veto.** Minters, positions, rate changes and bridge changes pass after a delay unless a qualified holder objects: at least 2% of FPS1 votes in the deployed contract, more than 1% in FCS and the current source.
- **Approved minters are fully trusted.** They mint, burn and spend any balance without allowance, so the application period is the only protection against a bad one.
- **Losses are layered.** The position's reserve contribution, then FPS equity, then other minters' reserves; `coverLoss` mints what the reserve cannot pay.
- **FPS and FCS hold that equity.** FPS is issued on a bonding curve at three times equity; FCS wraps it as an ERC-4626 vault, becomes binding above two thirds of the votes and discounts large redemptions.
- **The audit history** follows the design: competing liquidation paths, owner-set values without bounds, dust positions, transfer-hook collateral and vote mechanics account for most of the 5 Critical and 20 High findings.
- **The design relies on four conditions:** challengers who can obtain the collateral, bidders with ZCHF during the auction, a challenge period short enough that the collateral's price move over two periods stays within what the reserve contribution covers, and qualified holders who veto unsound minters and positions in time. For the WETH parameters of the worked example, the reserve and the 2% reward let an auction clear at most 18.4% below the liquidation price before equity loses.
- **The main risks** are a hostile minter or position that nobody vetoes, collateral that challengers cannot obtain or that falls faster than an auction runs, dependence on CCIP for the L2 deployments, and dilution through `coverLoss` once the reserve is empty.

![Mindmap of Frankencoin covering minters and veto governance, positions, challenges and auctions, a worked WETH example with the incentives of each actor, the FPS and FCS reserve, peripheral modules, and audits and risks]({{site.url_complet}}/assets/article/blockchain/defi/frankencoin/frankencoin-oracle-free-stablecoin-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **CDP** | Collateralised debt position: collateral locked in a contract against which a debt token is minted; Frankencoin calls it a position. |
| **Price oracle** | A contract that publishes an external price on-chain; Frankencoin's liquidation logic reads none. |
| **Dutch auction** | An auction whose price falls over time until a bidder accepts it; Frankencoin's auction phase falls linearly to zero. |
| **Bonding curve** | A formula that sets the issue and redemption price of a token from supply or reserves; FPS uses one with price equal to three times equity per share. |
| **Veto governance** | Proposals take effect after a delay unless a qualified holder objects; Frankencoin uses it for minters, positions, rates and bridge changes. |
| **Quorum** | The share of total votes a caller needs to be qualified: at least 2% in the deployed FPS1, more than 1% in FCS and the current source. |
| **Time-weighted votes** | Votes equal to balance multiplied by holding time, tracked with an anchor that moves forward when tokens are received. |
| **Minter** | A contract approved after its application period; it can mint, burn and spend any ZCHF balance without allowance. |
| **Application period** | The veto window before a minter becomes active, at least 14 days on the deployed ZCHF and 60 days through FCS `MinterGovernance`. |
| **Position** | A contract holding one borrower's collateral and debt, created by `MintingHub` with a self-declared liquidation price. |
| **Liquidation price** | The owner-set price per collateral unit at which the collateral exactly covers the gross debt; the reference for challenges. |
| **Reserve contribution** | The fraction of each mint kept in the Equity contract and returned on repayment; it absorbs the first loss of the position. |
| **Family limit** | The minting limit shared by an original position and all its clones, tracked on the original. |
| **Challenge** | A claim that a position's price is too high, backed by posting the same collateral; it starts the avert phase. |
| **Avert phase** | The first challenge phase, in which a bidder buys the challenger's collateral at the liquidation price and the position stays untouched. |
| **Forced sale** | The sale of an expired position's collateral, priced from ten times the liquidation price down to zero over two challenge periods. |
| **FPS** | Frankencoin Pool Shares, the Equity contract's token, whose holders own the equity and vote. |
| **FCS** | Frankencoin Shares, an ERC-4626 wrapper holding FPS one to one, binding above two thirds of FPS votes, now the canonical governance token. |
| **Leadrate** | The governance-set base rate, applied after a 7-day delay, added to the risk premium for borrowers and paid to savers. |
| **`coverLoss`** | The ZCHF function that pays a minter's loss from the reserve and mints the remainder when the reserve is empty. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A minter is active only after its application period passed without a veto. | `isMinter` checks `block.timestamp >= minters[m]`; `denyMinter` only before that time. | Nobody qualified watches the proposal, or the quorum can be reached cheaply. |
| A position holds collateral worth at least its debt at its own price: $$c \cdot P \geq m_{out} \cdot 10^{18}$$. | `_checkCollateral` after mint, withdraw and price changes (`Position.sol:513-516`). | A path changes collateral, debt or price without calling it. |
| A position with less than `minimumCollateral` is closed. | `_sendCollateral` closes on every outgoing transfer (`Position.sol:497-507`). | A new exit path sends collateral without `_sendCollateral`. |
| No position mints during a challenge, a cooldown, before start or after expiry. | `noChallenge noCooldown alive` on `_mint`. | A modifier is dropped on a new mint path, such as a roller. |
| A price increase is at most 3x and is followed by 3 days without minting. | `_preparePriceIncrease` (`Position.sol:330-333`), in the current source only; the deployed V2 hub has the cooldown but not the 3x cap. | A position is created by a hub without the cap, such as V2. |
| A forced sale cannot run while a challenge is open. | `forceSale` is `noChallenge`. | The modifier is removed (CS-ZCHF2-001). |
| Equity equals the reserve balance minus the minter reserve, floored at zero. | `Frankencoin.equity()`. | A minter burns with a reserve ratio different from the one it minted with. |
| FCS redemptions are possible only while FCS is binding. | `redemptionsEnabled` (`FCS.sol:68-70`). | Binding is redefined below 2/3 (FPS2 #001). |

### Documentation, deployment and source

The article compares three layers that do not always agree: the project documentation, the contracts deployed on mainnet, and the source at commit `8b4c4ab`. The table lists the items compared across the three layers, including three where they agree; each row names the files it rests on.

| Item | Documentation | Deployed | Current source | Source |
|---|---|---|---|---|
| Veto quorum for direct FPS1 actions | The same 1% as FCS | `QUORUM = 200`, at least 2% of FPS1 votes, in the deployment artifact and the Etherscan-verified source | `QUORUM = 100` in `Governance.sol`, inherited by `Equity` | `gitbook/governance.md` lines 17, 64 and 93; `gitbook/fps-reference.md` line 37; `scripts/deployment/deployments/mainnet/Frankencoin.json`; the verified source of `0x1bA2…41B2`; `Governance.sol` lines 12-17 |
| Comparison at the quorum | "Exactly 1% is not enough" | Strict `<`: exactly 2% qualifies | `<=`: exactly 1% does not qualify | `gitbook/governance.md` line 64; the deployment artifact above; `Governance.sol` lines 80-81 |
| Minter application | 60 days and 1,200 ZCHF through `MinterGovernance`; the direct route appears only as a bypass that `denyUnannouncedMinter` enforces against | ZCHF accepts direct proposals with 14 days (deployed with 1,209,600 seconds) and 1,000 ZCHF | Both routes | `gitbook/governance.md` lines 50-58; `Frankencoin.sol` lines 20-21 and 106-107; `MinterGovernance.sol` lines 16-19 |
| Liquidation price increase | A three-day minting cooldown; no cap mentioned | V2 hub positions: cooldown, no 3x cap | At most 3x per raise, then the cooldown | `gitbook/positions/adjust.md` line 49; `minting/v2/PositionV2.sol` (line 332); `Position.sol` lines 330-333 |
| Challenger reward | 2% of the accepted bid | 2% of the bid in the V1 and V2 hub sources; the V2 hub's `CHALLENGER_REWARD()` returned 20,000 ppm on 24 November 2026 | 2% of the bid in code; the constant's comment describes it as relative to the challenged collateral times the liquidation price | `gitbook/positions/auctions.md`; `MintingHubV1.sol` line 195; `MintingHubV2.sol` line 208; `MintingHub.sol` lines 25-28 and 230 |
| Savings withdrawals | Both modules listed; the `SavingsV2` lock documented | `SavingsV2` (lock, no referral) and a referral-enabled module | `AbstractSavings`: no withdrawal lock, referrer up to 25% of interest | `gitbook/savings.md` lines 15-16 and 34; `minting/v2/SavingsV2.sol` lines 145-148; `savings/AbstractSavings.sol` lines 30 and 218 |
| Minting hub version | The guide follows the pinned newer source; existing positions keep their version's terms | The V1 hub `0x7546…5219` and the V2 hub `0xDe12…3557` are the only hubs among the 12 active minters on 24 November 2026; no hub running the current `minting/` code had been proposed | `contracts/minting/` | `gitbook/positions/README.md`; `exports/address.config.ts`; the `MinterApplied` events of ZCHF |
| Stablecoin bridges | The XCHF and VCHF expiry of 15 April 2026 described as historical | XCHF closed on 26 October 2024, VCHF on 15 April 2026; CHFAU open until 8 April 2027 (`horizon()` on 24 November 2026) | Immutable `horizon` and `limit` per bridge | `swap/StablecoinBridge.sol` lines 20-31; the bridges' `horizon()`, `minted()` and `limit()` |

### Risks

The risks below combine the protocol's own disclosure page (`gitbook/risks.md`), the audit history and the code. Points that come from this article's reasoning rather than a source are marked (*derived*). Each bullet is also tagged *design* when it follows from the mechanism and would remain in a bug-free implementation, or *implementation* when it comes from this code or deployment. On-chain ownership and role getters were not queried for this article; see Gaps.

#### Smart contracts and transparency

- **Immutable core, many audits** (*design*). ZCHF and Equity have no owner, no pause and no upgrade path; the rules cannot change under a holder, and bugs cannot be patched in place. Fixes ship as new hubs, positions or modules proposed through the veto process, so several generations (V1, V2, current source) run side by side with different rules.
- **Source versus deployment** (*implementation*). This article describes the source at `8b4c4ab`. Which hub, if any, runs the current `minting/` code is not recorded in the repository's deployment exports; the deployed V2 hub lacks, for example, the 3x price-raise cap. The [table above](#documentation-deployment-and-source) lists the differences found.
- **Modules without a stored audit** (*implementation*). `CurveAmplifier`, the bridged leadrate and the EIP-3009 sidecar have no external audit among the stored reports; a ChainSecurity CCIP Bridge assessment cited by the FPS2 report was not read and may cover part of the bridged code.

#### External dependencies

- **No price oracle for liquidations** (*design*). The core does not depend on a feed, which removes oracle manipulation and staleness from the liquidation path. The `Arbitrage` helper and the amplifiers do read market prices, and the amplifiers depend on Uniswap or Curve pool state.
- **CCIP** (*design*). On every L2, governance and supply depend on CCIP delivering correct messages; the audit's trust model says a false relay compromises governance on that chain and can mint unlimited ZCHF there. Rate limits bound the flow, and qualified holders can change them immediately.
- **Other stablecoins** (*design*). Each `StablecoinBridge` imports the credit risk of the coin it accepts, up to its limit, with no write-off path.

#### Depeg

- **What holds the peg** (*design*). The documentation says ZCHF "has no fixed redemption promise for Swiss francs" and that collateral, reserves, borrowing costs and market activity support its exchange rate. In more detail (*derived*), the peg rests on borrowers needing ZCHF to repay, on positions being liquidated before their collateral falls below the debt, and on the bridges' one-to-one minting while they are open.

  *Source:* `gitbook/README.md`.
- **Downward** (*design*). A collateral fall faster than an auction can run, or collateral nobody can bid for, leaves bad debt. Once equity and the minter reserves are exhausted, `coverLoss` mints the shortfall, and ZCHF becomes partly unbacked; the documentation warns that aggregate collateral above supply does not rule out a shortfall, because one position's collateral does not cover another's debt.
- **Upward** (*design*). Repayment demand near maturities can push ZCHF above parity, the "short squeeze" in `gitbook/risks.md`.

#### Collateral and market risk

- **Reaction time** (*design*). When challenge periods last days, the reserve contribution must cover the price move over two auction phases; the collateral framework sizes it with a 99% value-at-risk over twice the auction duration plus 2%. In the worked example, a 20% reserve lets the auction clear about 18.4% below the liquidation price before equity loses (*derived*).
- **Challenger access** (*design*). Challenges need challengers who hold or can borrow the collateral. A thinly traded or owner-controlled token defeats the mechanism.

  *Source:* `gitbook/positions/auctions.md`.
- **Unchallenged positions** (*design*). Nothing but a challenge acts on an active position before expiration: no keeper, no oracle check, and a qualified holder can deny a position only before its start. An under-collateralised position nobody challenges stays open until its expiration, up to three years for the WETH parameters, and is then sold by forced sale. Its debt does not grow, because interest is paid upfront, but its shortfall follows the collateral price, and the owner can still mint up to the declared price if the family limit allows (*derived*).

  *Implementation:* `Position.sol`, `deny()`, `_mint()`, `_checkCollateral()` and `notifyChallengeStarted()` with the `alive` modifier (lines 246-251, 381-387, 513-516 and 527-532).
- **Token behaviour** (*design and implementation*). Pausable, blacklistable or hook-enabled tokens can block settlement or reopen the reentrancy ordering in `bid`; only the veto review keeps them out.

#### Liquidity

- **ZCHF holders** (*design*) exit through market liquidity, and selling into a thin pool costs a spread: in the documentation's example, 100,000 ZCHF sold at an average 0.98 lose 2,000 CHF.
- **FPS holders** (*design*) cannot redeem before a 90-day average holding period; **FCS holders** redeem only while FCS is binding, at a discount that grows with the size of recent redemptions, with `withdraw` capped at 10% of supply per call.
- **Savers** (*implementation*) using `SavingsV2` find withdrawals locked while their interest ticks lie in the future. This is the intended behaviour of that module: a withdrawal reverts with `FundsLocked` until the ticks are reached. A third party can extend the lock by depositing on someone's behalf, a griefing risk the team accepted (Decurity 5.5).

  *Implementation:* `minting/v2/SavingsV2.sol`, `withdraw()` (lines 145-148).

#### Centralisation and governance

- **No admin key in the core** (*design*). Power lies with holders above the quorum, each able to veto alone. A single wallet with at least 2% of FPS1 votes, or a group delegating to one, can block any proposal; through FCS, about 0.02% of FPS1 votes can act (FPS2 report, pp. 6 and 31).
- **Monitoring is the security model** (*design*). A hostile minter or a mispriced position passes if nobody qualified vetoes it in time. The design assumes holders with enough at stake watch every proposal; the audit adds the assumption that no malicious group holds more than half of FCS votes after binding.
- **`shoot` and `restructureCapTable`** (*design*) let one group of holders destroy another's votes or balances under specific conditions, by design.
- **Off-chain components** (*implementation*). The front end, the Ponder indexer, the API and the notification bot shape what users see; none controls funds.

#### Loss sharing

- **Order of loss** (*design*). **First loss:** the liquidated position's reserve contribution. **Second:** FPS/FCS equity, including through savings interest. **Third:** the reserve contributions of every other borrower, who recover less on repayment. **Last:** ZCHF holders, through minting of unbacked ZCHF by `coverLoss`.
- **Borrowers in sound positions** (*design*) can therefore lose part of their reserve without having been liquidated.

  *Source:* `gitbook/risks.md`, section "Third Line Bailout".

#### Regulatory

- **No issuer** (*design*). ZCHF has no issuer that promises redemption in francs at par, unlike the issuer-backed model of e-money tokens. How frameworks such as [MiCA]({{site.url_complet}}/2026/09/17/mica-stablecoins-asset-referenced-tokens-e-money-tokens/) treat such a token is not settled by the sources (*derived*). The project publishes a compliance page.

#### Summary

| Risk | Type | Where it comes from | What the design does about it | What remains |
|---|---|---|---|---|
| Hostile minter or position | Design | Infinite allowance of minters; owner-set prices | Application period and veto; 3-day init period for positions | Depends on qualified holders watching every proposal |
| Bad debt | Design | Collateral falls faster than a challenge runs | Reserve contribution sized for two auction phases; layered loss absorption | Minting through `coverLoss` once the reserve balance is exhausted |
| Unchallenged under-collateralised position | Design | Only a challenge acts before expiration | Forced sale at expiration, with the position's reserve used in settlement | Shortfall set by the price at expiration; owner can mint up to the declared price |
| Illiquid or hostile collateral | Design and implementation | Challengers cannot obtain the token; hooks, pauses, blacklists | Collateral assessments; transfer probe; postponed returns | Enforcement is governance, not code |
| Short challenge period | Implementation | No lower bound in `openPosition` | Veto and front end | A position that passes the veto with a tiny period |
| CCIP failure | Design and implementation | L2 supply and votes rely on CCIP messages | Rate limits; 7- and 21-day delays on pool changes | Instant rate-limit changes; stale snapshots accepted |
| Bridged stablecoin default | Design | `StablecoinBridge` mints 1:1 | Limit and 52-week horizon | No write-off path |
| FCS exit cost | Design | Discount on large redemptions | 7-day recovery, 10% withdraw cap | Holders who must exit fast take the discount |
| Version spread | Implementation | Old hubs and savings stay deployed | New modules through the veto | V1/V2 positions keep their own rules and known issues |

### Timeline

Events up to 25 November 2026.

| Date | Event | Why it matters here | Source |
|---|---|---|---|
| 12 April 2023 | Code4rena ran a public audit contest on the V1 core from 12 to 19 April 2023 and published its report on 9 June 2023. | It produced the H-05 price overflow and most of the V1 findings grouped in [Bug classes](#bug-classes). | [Code4rena, Frankencoin report](https://code4rena.com/reports/2023-04-frankencoin) |
| 28 October 2023 | ZCHF was deployed on Ethereum in block [18,451,518](https://etherscan.io/block/18451518), and the V1 Minting Hub was registered as a minter with no application period 19 blocks later, in block [18,451,537](https://etherscan.io/block/18451537). | Every later minter went through a veto window of at least 14 days; only the initial hub and the XCHF bridge were added at deployment. | [ZCHF creation transaction on Etherscan](https://etherscan.io/tx/0xdc09f425cfb64bbb93a07bf22ea7e7922e24874971b6d17ce1f91750ad92ef62) |
| 30 October 2023 | ChainSecurity issued its report on the V1 core and the stablecoin bridge. | It holds CS-ZCHF-034, the first of the five Critical findings, and the bridge's missing write-off path. | [ChainSecurity, Code Assessment of the Frankencoin Smart Contracts](https://github.com/Frankencoin-ZCHF/Frankencoin/blob/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/audits/V1/ChainSecurity-audit.pdf) |
| 27 November 2024 | Minting Hub V2 was proposed as a minter in block [21,281,110](https://etherscan.io/block/21281110), minutes after the `SavingsV2` module and the position roller. | V2 is one of the two hubs that run every live position today, with forced sale and the leadrate. | [`MinterApplied` transaction on Etherscan](https://etherscan.io/tx/0x1903230e1983883ea422619e929dbe51b42eb7db0ac56b508945bbce48251139) |
| 28 November 2024 | ChainSecurity issued its report on the V2 contracts. | Its CS-ZCHF2-001 and -002 findings led to the `noChallenge` guard and the bad-debt booking in `forceSale`. | [ChainSecurity, Code Assessment of the Frankencoin v2024 Smart Contracts](https://github.com/Frankencoin-ZCHF/Frankencoin/blob/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/audits/V2/ChainSecurity_Frankencoin_Frankencoin_v2024.pdf) |
| 24 June 2025 | The CCIP token pool was proposed as a minter in block [22,775,408](https://etherscan.io/block/22775408), with the bridge accounting contract in the next block. | These two minters carry ZCHF and its profits and losses to the other chains, which then depend on CCIP. | [`MinterApplied` transaction on Etherscan](https://etherscan.io/tx/0xcecb867417f3bc34ed8a2f2bfed8fcb876210d5722f92c1c7cb7900b5e98bdac) |
| 30 April 2026 | The AllUnity CHFAU stablecoin bridge was proposed as a minter in block [24,993,997](https://etherscan.io/block/24993997). | It is the only one of the three bridges still able to mint, until 8 April 2027. | [`MinterApplied` transaction on Etherscan](https://etherscan.io/tx/0xa1b5112f07a7f8b10fd183ad6819c486339874ddd6c5d7ceed92ecf04c64ed39) |
| 29 May 2026 | A minter named after the CHFAU bridge with an added asterisk, at a lookalike address, was proposed in block [25,199,256](https://etherscan.io/block/25199256) and denied 54 blocks later, in block [25,199,310](https://etherscan.io/block/25199310). | It is the clearest case of the veto stopping a proposal that imitated an approved minter. | [`MinterDenied` transaction on Etherscan](https://etherscan.io/tx/0xf64bc6b2c5032d3fff8caf8c57f1c5afdafd24cfdf6b79706be1ff03dee7f750) |
| 14 July 2026 | ChainSecurity issued its FPS2 report on the share wrapper, the governance modules and the CCIP admin. | Its Critical finding on `shoot` led to the two-thirds binding threshold of the current source. | [ChainSecurity, Code Assessment of the FPS2 Smart Contracts](https://reports.chainsecurity.com/Frankencoin/ChainSecurity_Frankencoin_FPS2_Audit.pdf) |
| 28 August 2026 | FCS and its minter, interest and CCIP governance modules were deployed on Ethereum in block [25,852,506](https://etherscan.io/block/25852506). | From this block, minters can be proposed with the 60-day announcement and vetoed through FCS at its 1% quorum. | [FCS creation transaction on Etherscan](https://etherscan.io/tx/0x5b7df19db201535b1a10f3e30a9d343cf2f78fcc645d059b6f5f3b84aeee70ec) |

## Frequently Asked Questions

**Q: How does Frankencoin decide that a position should be liquidated without a price oracle?**

It does not decide in advance. Anyone who thinks a position's declared liquidation price is above the market can challenge it by posting the same collateral. If someone buys that collateral at the liquidation price during the avert phase, the price is considered justified and the position is left alone. If nobody does, the auction phase sells the position's collateral at a falling price, which repays the debt and reveals what the collateral is worth.

**Q: What is the difference between the avert phase and the auction phase, and who loses in each?**

In the avert phase, a bidder buys the *challenger's* collateral at the liquidation price; the challenger has sold at a price it thought too high, and the position only gets a one-day cooldown.

In the auction phase, the bidder buys the *position's* collateral at a price falling linearly to zero. The challenger gets its collateral back plus 2% of the bid; the position repays the matching share of its debt, and any shortfall is taken from the reserve.

**Q: Why is the quorum given as 2% in some places and 1% in others?**

The deployed FPS1 Equity contract was compiled with `QUORUM = 200` (2%), as its mainnet deployment artifact shows, while the current governance source and the FCS wrapper use 1%; the comment at line 16 of `FCS.sol` and ChainSecurity's FPS2 report (p. 9) say the same. The documentation pages that give 1% for direct FPS1 actions describe the current source, not the deployed contract.

A direct veto on FPS1 needs at least 2% of FPS1 votes; because the comparison is strict, exactly 2% qualifies. A veto through FCS needs more than 1% of FCS votes, and the FCS contract itself must be above the FPS1 quorum, so the effective share of FPS1 votes can be as low as 1% of 2%, about 0.02%.

**Q: A borrower mints 10,000 ZCHF gross with a 10% reserve and a 3% annual rate over one year. What does the wallet receive, and what happens to the rest?**

The wallet receives 8,700 ZCHF:

- 1,000 ZCHF (10%) goes to the Equity contract as the reserve contribution and is returned when the debt is repaid, unless losses have impaired the reserve.
- 300 ZCHF (3% for one year) goes to equity as interest, paid upfront and not refunded on early repayment.

The debt recorded in the position is the full 10,000 ZCHF.

**Q: Which layers absorb a liquidation loss, and why can a borrower who was never liquidated lose money?**

The liquidated position's own reserve contribution comes first, then the equity owned by FPS and FCS holders. When equity is exhausted, the reserve balance drops below the sum of all reserve contributions, and `calculateAssignedReserve` scales every borrower's refund down in proportion. A borrower in a healthy position therefore recovers less of their contribution on repayment. If even that is not enough, `coverLoss` mints the remainder, which dilutes ZCHF holders.

**Q: Why did ChainSecurity rate the FCS `shoot` function Critical, and what changed?**

`shoot` is permissionless while FCS is binding: anyone can call it to destroy an outside FPS1 holder's votes, at the cost of the same amount of the FCS contract's own FPS1 votes. With binding defined at 50%, each shot kept FCS just above 50%.

An outside FPS1 holder could therefore shoot every other holder, then push FCS below binding and drain its votes with free wrap and unwrap loops, and finally submit a position with bad collateral that nobody was left to veto.

Binding now requires more than two thirds, a level at which each shot increases FCS's share; unwrapping requires an above-average holding duration, and redemptions are allowed only while binding.

**Q: Why does the short challenge period found by Decurity remain in the code?**

A challenge period of a few seconds lets an owner avert every challenge cheaply and later buy the collateral back for almost nothing. The team treats the challenge period as a parameter that governance reviews during the init period: a position with an unreasonable period should be denied, and the front end enforces a minimum. The code has no lower bound, so the protection depends on the veto.

**Q: What happens to an under-collateralised position that nobody challenges?**

Nothing acts on it before expiration. There is no keeper and no oracle check, and governance can deny a position only before its start. Until expiration:

- **The debt does not grow**, because interest is paid upfront; the shortfall moves only with the collateral price.
- **The owner can still mint** up to the collateral times the declared price, if the family limit and cooldowns allow, because the collateral check uses the declared price, not the market (*derived*).
- **The owner can repair it** by repaying, adding collateral, or lowering the price if the collateral still covers the debt at the new price.
- **Challenges remain possible** until expiration, and not after it.

At expiration, the forced sale starts at ten times the liquidation price and falls to it over one challenge period, then to zero over a second one. Two cases with the worked example's position, assuming the sale clears at the market price:

- **WETH at 2,300 ZCHF at expiration:** the sale raises 9,200 ZCHF, which with the 2,000 ZCHF reserve covers the 10,000 ZCHF debt; the owner receives 1,200 ZCHF and equity is unchanged.
- **WETH at 1,800 ZCHF**, with one buyer taking all 4 WETH in one call, since `forceSale` books the loss only once no collateral is left: the sale raises 7,200 ZCHF, `coverLoss` pays 2,800 ZCHF and the released reserve offsets 2,000 ZCHF of it, so equity falls by 800 ZCHF.

**Q: How sensitive is liquidation to market liquidity and bidder participation?**

Directly, because the winning bid is the only price the protocol learns:

- **Settlement follows the bid.** In the worked example, a bid at 2,250 ZCHF per WETH adds 820 ZCHF to equity, a bid at 1,800 ZCHF takes 944 ZCHF from it, and the challenger's 2% shrinks with the bid.
- **No bidder means no recovery.** The auction price reaches zero after the second challenge period, and the whole repayment becomes a loss for `coverLoss`.
- **Thin markets lower the bid.** Bidders bid below the market by what reselling costs them; the collateral framework asks for a higher reserve where market depth may not absorb the collateral and for longer auctions on less liquid assets.
- **Challengers need the same liquidity**, since they must obtain the collateral before they can challenge.

**Q: Which risks are inherent to the design and which are specific to the implementation?**

Design risks would remain in a bug-free implementation: the dependence on challengers who can obtain the collateral, on bidder liquidity, on a reaction time of two challenge periods, on qualified holders who read every proposal, the full trust given to approved minters, loss sharing ending in minting by `coverLoss`, and CCIP for the other chains.

Implementation risks come from this code or deployment: the missing lower bound on the challenge period, the deployed FPS1 quorum that differs from the documentation, old V1 and V2 positions with their own rules, the `bid` ordering that is safe only for tokens without transfer hooks, stale cross-chain snapshots, and modules without a stored audit. The Risks annex tags each entry with one of the two.

## Gaps

These points are not settled by the sources read for this article and should be checked before relying on it.

| Gap | Why it matters | What to read or verify |
|-----|----------------|------------------------|
| The worked example combines the published WETH assessment with assumed values: a 3% leadrate (the on-chain value was 1% on 24 November 2026), the market prices and the bid timing; the 2,500 ZCHF liquidation price is the documentation's illustration, and no deployed WETH position was read on chain. | The real fee and the buffer above the liquidation price depend on these values. | The WETH positions on the [monitoring page](https://app.frankencoin.com/monitoring), against the [WETH assessment](https://github.com/Frankencoin-ZCHF/frankencoin-collateral-assessments/blob/8db997f73e736fcd82f9ffba1be6f238a3cd14b2/assessments/published/WETH.md). |
| The 18.4% threshold is derived for a position minted up to its liquidation price and depends only on that price, the reserve contribution and the 2% reward. Whether a real market fall stays within it depends on when the challenge starts and how close the winning bid is to the market price, which were not measured. | A late challenge or a bid below the market lets a smaller market fall reach equity. | Recompute with `_finishChallenge()` in the pinned [`MintingHub.sol`](https://github.com/Frankencoin-ZCHF/Frankencoin/blob/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/contracts/minting/MintingHub.sol) for the parameters of a real position and observed challenge timings on the [auctions page](https://app.frankencoin.com/challenges). |
| The incentive statements on when a challenger, bidder or governance holder would not act are the article's reasoning, not measured behaviour; the minter registry shows five vetoes, each on the day of the proposal, but challenge delays were not measured. | Whether challenges and vetoes happen in time is the main assumption of the design. | Past challenges and their delays in the [Ponder indexer](https://github.com/Frankencoin-ZCHF/ponder) data, and the proposals in the [governance application](https://app.frankencoin.com/governance). |
| No hub running the current `contracts/minting/` code had been proposed by 24 November 2026, and when one will be is not known. | The 3x cap and the other newer behaviours described here apply to no live position yet. | New `MinterApplied` events of [ZCHF on Etherscan](https://etherscan.io/address/0xB58E61C3098d85632Df34EecfB899A1Ed80921cB#events). |
| The state of the bridged deployments on the other seven chains (CCIP pool rate limits, `isBinding`, the bridged leadrate) was not queried; only mainnet was read. | The cross-chain risks describe code, not the deployed state. | Read calls on the addresses of the other chains in `exports/address.config.ts` of the [pinned repository](https://github.com/Frankencoin-ZCHF/Frankencoin/blob/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/exports/address.config.ts). |
| The ERC-4626 classification of FCS is only partial: ChainSecurity found deviations, some acknowledged (#005, #021). | An integrator relying on strict ERC-4626 semantics may be surprised. | Findings #005 and #021 of the [FPS2 report](https://reports.chainsecurity.com/Frankencoin/ChainSecurity_Frankencoin_FPS2_Audit.pdf). |
| No external audit among the stored sources covers `CurveAmplifier`, the bridged leadrate or the EIP-3009 sidecar; the FPS2 report (p. 9) refers to a separate CCIP Bridge code assessment that was not read. | These modules have no review history in this article. | ChainSecurity's public report site (the [FPS2 report](https://reports.chainsecurity.com/Frankencoin/ChainSecurity_Frankencoin_FPS2_Audit.pdf) is hosted there) for the CCIP Bridge assessment and newer Frankencoin reports, and the team's design notes on `CurveAmplifier` and the sidecar in `reports/` of the [pinned repository](https://github.com/Frankencoin-ZCHF/Frankencoin/tree/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/reports). |
| Finding counts come from per-report digests; the Blockbite and Decurity PDFs were not re-read for this article. | Totals in the audit table could be off by a few. | `audits/V1/blockbite-audit.pdf` and `audits/V2/frankencoin-audit-report-2024-1.1.pdf` in the [pinned repository](https://github.com/Frankencoin-ZCHF/Frankencoin/tree/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/audits). |
| The regulatory remark (no issuer promising redemption at par, unlike e-money tokens) is the article's inference. | It is not a legal assessment. | The project's [compliance page](https://www.frankencoin.com/compliance#compliance-summary) and the MiCA texts. |
| The timeline has no leadrate, fee or quorum changes: the `RateProposed` and `RateChanged` events of the leadrate contracts were not read, and the minter events are the only governance history queried. | Rate changes alter every new position's upfront fee and the savings cost to equity. | The events of [`SavingsV2` on Etherscan](https://etherscan.io/address/0x3BF301B0e2003E75A3e86AB82bD1EFF6A9dFB2aE#events) and of the [`SavingsReferral` module](https://etherscan.io/address/0x27d9AD987BdE08a0d083ef7e0e4043C857A17B38#events). |
| The definitions of CDP, Dutch auction, bonding curve and optimistic governance in the prerequisites come from general knowledge. | They frame the reading but are not from the Frankencoin sources. | Compare with the site's [MakerDAO]({{site.url_complet}}/2023/11/21/makerdao/) and [Liquity V1]({{site.url_complet}}/2026/10/22/liquity-v1-lusd-troves-stability-pool/) articles, and with the [Frankencoin documentation](https://docs.frankencoin.com) for the protocol-specific use. |

## References

### Analyzed source

- [Frankencoin-ZCHF/Frankencoin](https://github.com/Frankencoin-ZCHF/Frankencoin) — analyzed at commit [`8b4c4ab67bb361b91d58c474b87f4608fc4c0566`](https://github.com/Frankencoin-ZCHF/Frankencoin/tree/8b4c4ab67bb361b91d58c474b87f4608fc4c0566), 2026-11-23 (contracts, `exports/`, `audits/`)
- [Frankencoin-ZCHF/gitbook](https://github.com/Frankencoin-ZCHF/gitbook) — analyzed at commit [`8512bc05f312fc6624b411577a3cbfea715a27cd`](https://github.com/Frankencoin-ZCHF/gitbook/tree/8512bc05f312fc6624b411577a3cbfea715a27cd), 2026-11-23 (published at [docs.frankencoin.com](https://docs.frankencoin.com))
- [Frankencoin-ZCHF/frankencoin-collateral-assessments](https://github.com/Frankencoin-ZCHF/frankencoin-collateral-assessments) — analyzed at commit [`8db997f73e736fcd82f9ffba1be6f238a3cd14b2`](https://github.com/Frankencoin-ZCHF/frankencoin-collateral-assessments/tree/8db997f73e736fcd82f9ffba1be6f238a3cd14b2), 2026-11-23 (`framework/collateral-risk-framework.md`, `assessments/published/WETH.md`)
- [code-423n4/2023-04-frankencoin-findings](https://github.com/code-423n4/2023-04-frankencoin-findings) — report read at commit [`df70ee616c774ecd7a381e1555df4dcf47589690`](https://github.com/code-423n4/2023-04-frankencoin-findings/tree/df70ee616c774ecd7a381e1555df4dcf47589690), 2026-11-23

### On-chain reads

- Ethereum mainnet, block [26,485,804](https://etherscan.io/block/26485804), 24 November 2026 at 15:06 UTC, through the PublicNode RPC endpoint with Foundry `cast`: [ZCHF](https://etherscan.io/address/0xB58E61C3098d85632Df34EecfB899A1Ed80921cB) `totalSupply()`, `minterReserve()`, `equity()`, `MIN_FEE()`, `MIN_APPLICATION_PERIOD()` and `isMinter()` for the addresses in `exports/address.config.ts`; [Equity](https://etherscan.io/address/0x1bA26788dfDe592fec8bcB0Eaff472a42BE341B2) `price()` and `totalSupply()`; [MintingHub V2](https://etherscan.io/address/0xDe12B620A8a714476A97EfD14E6F7180Ca653557) `rate()`, `CHALLENGER_REWARD()` and `OPENING_FEE()`; [SavingsV2](https://etherscan.io/address/0x3BF301B0e2003E75A3e86AB82bD1EFF6A9dFB2aE) `currentRatePPM()` and `nextRatePPM()`; the [XCHF](https://etherscan.io/address/0x7bbe8F18040aF0032f4C2435E7a76db6F1E346DF), [VCHF](https://etherscan.io/address/0x3b71ba73299f925a837836160c3e1fec74340403) and [CHFAU](https://etherscan.io/address/0x3e445ff4ddDf0ff8aE7458c9746eD80bD664F6C1) bridges `horizon()`, `minted()` and `limit()`
- Etherscan API V2, 24 November 2026, up to block 26,485,804: the [verified source of Equity](https://etherscan.io/address/0x1bA26788dfDe592fec8bcB0Eaff472a42BE341B2#code), and every `MinterApplied` and `MinterDenied` event of ZCHF since its deployment (17 and 5). Powered by [Etherscan.io](https://etherscan.io) APIs.

### Timeline sources

- ZCHF contract creation, Ethereum block [18,451,518](https://etherscan.io/block/18451518), 28 October 2023, and FCS contract creation, block [25,852,506](https://etherscan.io/block/25852506), 28 August 2026, read with Etherscan API V2 `contract getcontractcreation` on 25 November 2026
- `MinterApplied` and `MinterDenied` events of [ZCHF](https://etherscan.io/address/0xB58E61C3098d85632Df34EecfB899A1Ed80921cB#events), Etherscan API V2, read on 24 November 2026 (the batch listed under On-chain reads)
- Frankencoin-ZCHF, `exports/blocknumber.config.ts`, FCS start blocks, at commit [`8b4c4ab`](https://github.com/Frankencoin-ZCHF/Frankencoin/blob/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/exports/blocknumber.config.ts)

### Audit reports

- Blockbite, *Audit report Frankencoin*, February 2023: [`audits/V1/blockbite-audit.pdf`](https://github.com/Frankencoin-ZCHF/Frankencoin/blob/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/audits/V1/blockbite-audit.pdf)
- [Code4rena, *Frankencoin* contest report](https://code4rena.com/reports/2023-04-frankencoin), 2023-06-09
- ChainSecurity, *Code Assessment of the Frankencoin Smart Contracts*, 2023-10-30: [`audits/V1/ChainSecurity-audit.pdf`](https://github.com/Frankencoin-ZCHF/Frankencoin/blob/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/audits/V1/ChainSecurity-audit.pdf)
- Decurity, *FrankenCoin Security Audit Report* v1.1, September 2024: [`audits/V2/frankencoin-audit-report-2024-1.1.pdf`](https://github.com/Frankencoin-ZCHF/Frankencoin/blob/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/audits/V2/frankencoin-audit-report-2024-1.1.pdf)
- ChainSecurity, *Code Assessment of the Frankencoin v2024 Smart Contracts*, 2024-11-28: [`audits/V2/ChainSecurity_Frankencoin_Frankencoin_v2024.pdf`](https://github.com/Frankencoin-ZCHF/Frankencoin/blob/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/audits/V2/ChainSecurity_Frankencoin_Frankencoin_v2024.pdf)
- ChainSecurity, *Code Assessment of the Uniswap Liquidity Amplifier*, 2026-07-30: [`audits/amplifier/ChainSecurity_Frankencoin_UniswapLiquidityAmplifier_Audit.pdf`](https://github.com/Frankencoin-ZCHF/Frankencoin/blob/8b4c4ab67bb361b91d58c474b87f4608fc4c0566/audits/amplifier/ChainSecurity_Frankencoin_UniswapLiquidityAmplifier_Audit.pdf)
- [ChainSecurity, *Code Assessment of the FPS2 Smart Contracts*](https://reports.chainsecurity.com/Frankencoin/ChainSecurity_Frankencoin_FPS2_Audit.pdf), 2026-07-14

### Project documentation and standards

- [Frankencoin documentation](https://docs.frankencoin.com)
- [Frankencoin application](https://app.frankencoin.com)
- [EIP-1167: Minimal Proxy Contract](https://eips.ethereum.org/EIPS/eip-1167)
- [EIP-3009: Transfer With Authorization](https://eips.ethereum.org/EIPS/eip-3009)
- [ERC-4626: Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-4626)
- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [Introduction to MakerDAO]({{site.url_complet}}/2023/11/21/makerdao/)
- [How Liquity V1 Works - LUSD, Troves, the Stability Pool, Redemptions and Recovery Mode]({{site.url_complet}}/2026/10/22/liquity-v1-lusd-troves-stability-pool/)
- [How Liquity V2 Works - BOLD, User-Set Interest Rates, Redemption Routing and Branch Shutdown]({{site.url_complet}}/2026/10/22/liquity-v2-bold-user-set-interest-rates/)
- [Who Absorbs the Loss? Tranched Stablecoins Compared - infiniFi, f(x) Protocol and Liquity]({{site.url_complet}}/2026/11/16/tranched-stablecoins-loss-waterfall/)
- [Chainlink CCIP — from DONs to Cross-Chain Verifiers]({{site.url_complet}}/2026/11/16/chainlink-ccip-architecture/)
- [Stablecoins Under MiCA — Asset-Referenced Tokens and E-Money Tokens (Titles III and IV)]({{site.url_complet}}/2026/09/17/mica-stablecoins-asset-referenced-tokens-e-money-tokens/)
