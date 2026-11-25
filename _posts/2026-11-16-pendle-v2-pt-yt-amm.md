---
layout: post
title: "How Pendle V2 Works - SY, PT and YT, the Rate AMM, Oracles and PT as Collateral"
date:   2026-11-16
last_modified_at: 2026-11-25
lang: en
locale: en-GB
categories: blockchain defi ethereum
tags: pendle defi amm oracle lending morpho liquidation risk-management
description: "Pendle V2 from its code: SY wrappers, the PT/YT split, the logit rate AMM with a worked trade, PT prices to expiry, TWAP and linear oracles, PT as collateral."
image: /assets/article/blockchain/defi/pendle/2026-11-16-pendle-v2-pt-yt-amm-mindmap.png
isMath: true
isMermaid: true
---

[Pendle](https://docs.pendle.finance/) is a yield-trading protocol on Ethereum and other EVM chains. It takes a yield-bearing token, such as Ethena's sUSDe or Lido's wstETH, and splits it into two tokens with a fixed maturity: a principal token (PT) that redeems for one unit of the underlying asset at expiry, and a yield token (YT) that collects all the yield until then. A PT bought below 1 is therefore a fixed-rate position, close to a zero-coupon bond, and that property is what made PTs common collateral on lending markets such as Morpho and Aave.

This article follows Pendle V2 through its contracts: the SY wrapper, the PT and YT split and its index, the PT/SY market and its logit curve with a worked numeric trade, the PT price before and after expiry, the two oracle designs, the router, and what a lender takes on when it accepts PT as collateral. The code is `pendle-core-v2-public` at v6.11.0, pinned under References. The dated events behind it, from the SY standard to the 2026 timelock, are in the timeline in the annex.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What you need to know first

The article assumes the reader knows tokens, DEXes and lending in general. A few mechanisms one level below are used without being derived:

- **Exchange-rate tokens.** A yield-bearing token such as an [ERC-4626](https://eips.ethereum.org/EIPS/eip-4626) vault share does not rebase; its value grows through an exchange rate, assets per share. Pendle's whole accounting is built on that rate.
- **Zero-coupon pricing and continuous compounding.** A claim to 1 unit at time $$\tau$$ years from now, discounted at a continuously compounded rate $$r$$, is worth $$e^{-r\tau}$$ today. Pendle stores rates as $$r = \ln(1 + \text{APY})$$, the "ln implied rate".
- **Automated market makers.** A pool prices a trade from its reserves through a curve; [Automated Market Makers (AMMs) - Overview]({{site.url_complet}}/2025/07/29/automated-market-makers-amm/) covers constant-product and StableSwap designs. Pendle's curve is a different one, built for a token whose fair price drifts toward 1.
- **TWAP oracles.** A pool can keep a running sum of a quantity over time, so that the average over any window is a difference of two sums divided by the window. Pendle adapts the [Uniswap V3 oracle](https://docs.uniswap.org/concepts/protocol/oracle) design to the log of the implied rate.
- **Flash swaps.** A pool that sends the output first, calls back the caller, and only then checks that the input arrived. Pendle uses this for every swap, and to trade YT without a YT pool.
- **Liquidation in an isolated lending market.** A borrower is liquidated when the oracle value of the collateral times the liquidation threshold falls below the debt; the liquidator repays debt and takes collateral with a bonus, which it then has to sell. [How Morpho Blue Works - Isolated Lending Markets, Shares, Liquidations and Bad Debt]({{site.url_complet}}/2026/10/10/morpho-blue-lending-markets/) describes this for Morpho Blue.

## Architecture: three layers behind interfaces

Pendle V2 has three layers of contracts that only talk through interfaces, plus a router on top:

- **SY (Standardized Yield)** wraps a yield-bearing token into one interface. For most SYs, 1 SY is 1 yield token, and `exchangeRate()` returns the amount of *asset* one SY is worth.
- **The YT contract** (`PendleYieldToken`) is the YT token itself: it holds the SY and mints both PT and YT against it. PT and YT of one SY and one expiry form a pair, written PY in the code.
- **The market** (`PendleMarketV7`) is an AMM between PT and SY with an LP token and a built-in oracle. There is no YT pool: YT is traded through flash swaps on the PT/SY market.
- **The router** (`PendleRouterV4`, an EIP-2535 diamond proxy) bundles these steps into one call from any token.

```mermaid
flowchart TD
    YTK["Yield token<br/>(sUSDe, wstETH, ERC-4626 share)"] -->|"deposit"| SY["SY<br/>exchangeRate = asset per SY"]
    SY -->|"mintPY"| YC["YT contract<br/>holds SY, pyIndex"]
    YC --> PT["PT<br/>1 asset at expiry"]
    YC --> YT["YT<br/>yield until expiry"]
    PT <-->|"swap"| MK["PendleMarket<br/>PT / SY AMM + TWAP"]
    SY <-->|"swap"| MK
    RT["PendleRouterV4"] --> MK
    RT --> SY
    MK -->|"ln implied rate"| OR["PT oracles"]
    OR --> MM["Lending market<br/>(Morpho Blue, Aave)"]
    PT -->|"collateral"| MM
```

### Units: asset, SY and the index

The word *asset* has a precise meaning here: it is what the yield token appreciates against, given by `SY.assetInfo()`. For SY-wstETH the asset is stETH; for SY-sUSDe it is USDe. The documentation notes that the asset address is a best estimate and may not exist on the chain. The token decimals and the scaling of rates are left to the Integration Notes, where an oracle integration needs them.

A PT is worth 1 asset at expiry, not 1 SY: at maturity it redeems for the amount of SY that is worth 1 asset. With wstETH worth 1.2 stETH at expiry, 1 PT-wstETH redeems for $$1/1.2 = 0.8333$$ wstETH.

## SY: the wrapper everything else uses

`IStandardizedYield` is a small interface: `deposit(receiver, tokenIn, amount, minSharesOut)` and `redeem(receiver, shares, tokenOut, minOut, burnFromInternalBalance)` wrap and unwrap, `exchangeRate()` gives the asset value of one SY, and `claimRewards` pays out non-compounding rewards, such as AURA or BAL for a Balancer LP. For an ERC-4626 vault the rate is the vault's `totalAssets / totalSupply` (`PendleERC4626SY.sol`).

Three properties of SY matter later, when PT is used as collateral:

- **The output token set is narrow.** `getTokensOut()` lists what SY can redeem into. `PendleSUSDESY` redeems to sUSDe only, so whoever unwinds PT-sUSDe ends with sUSDe and still has to exit Ethena's cooldown or sell on a DEX. SY-wstETH accepts ETH in but never pays ETH out.
- **SY is pausable.** `SYBaseUpgV2.pause()`, callable by the owner, makes every SY transfer revert, which freezes swaps on the market, `redeemPY` and SY redemptions for every PT built on it. Pendle's troubleshooting page says it pauses contracts when an integrated protocol is compromised.
- **Newer SYs are upgradeable proxies** behind Pendle's proxy admin, while markets are immutable.

`previewDeposit` and `previewRedeem` exist but are documented as best-effort and not audited for on-chain use.

## PT and YT: split, accrual and redemption

### The PY index

The YT contract keeps one number, the PY index:

$$
\begin{aligned}
\text{pyIndex} = \max\left(\text{SY.exchangeRate()},\ \text{pyIndexStored}\right)
\end{aligned}
$$

It never decreases. Minting sends SY in and returns $$\text{SY} \times \text{pyIndex}$$ PT **and** the same amount of YT, so one unit of PT and one unit of YT together are always backed by one unit of asset at the current index. Before expiry, `redeemPY` needs equal amounts of PT and YT and returns $$\text{PY} / \text{pyIndex}$$ SY.

### YT accrual

Backing $$B$$ asset takes $$B/I_0$$ SY at index $$I_0$$ and only $$B/I_1$$ SY at a higher index $$I_1$$. A balance $$B$$ of YT accrues the difference:

$$
\begin{aligned}
\Delta\text{SY} = \frac{B}{I_0} - \frac{B}{I_1} = B \cdot \frac{I_1 - I_0}{I_0 \, I_1}
\end{aligned}
$$

*Implementation:* `InterestManagerYT._distributeInterestPrivate`.

With 1,000 YT and an index going from 1.200 to 1.212 (a 1 % rise), the holder accrues 8.2508 SY, which is worth exactly $$8.2508 \times 1.212 = 10.000$$ asset: 1 % of 1,000 asset of principal. The accrual is settled on every YT transfer, paid in SY by `redeemDueInterestAndRewards`, and the factory's `interestFeeRate` and `rewardFeeRate` are taken for the treasury on payout.

### Expiry and the treasury's share

At expiry, YT stops accruing new yield and is worth zero, but the cut-off is the first interaction after expiry, which freezes the index as `firstPYIndex`: index growth between the expiry timestamp and that call still accrues to YT.

From then on, PT redeems alone, without YT, at the current index: $$\text{PT} / \text{pyIndexCurrent}$$ SY. The index keeps rising after expiry, so this pays fewer SY than redeeming at the frozen index would, and the difference goes to the treasury.

For example, with the index frozen at 1.25 and at 1.30 when the holder redeems, 100 PT would be worth $$100/1.25 = 80$$ SY at the frozen index; the holder receives $$100/1.30 = 76.92$$ SY, and the remaining 3.08 SY go to the treasury.

*Implementation:* `PendleYieldToken._calcSyRedeemableFromPY`, credited to `totalSyInterestForTreasury`.

In other words, **a PT held after expiry does not earn yield**: it is a fixed amount of asset, and the yield on the SY behind it belongs to Pendle's treasury until the holder redeems.

### Negative yield

If the SY's exchange rate falls below the stored index, the index stays where it was. Redemptions then return fewer SY per PY than the asset value implies, and YT stops accruing until the rate recovers. The documentation's example: a PT minted at index 1.20 that redeems when 1 SY is worth 1.15 asset returns 115 asset per 120 PT (120 PT redeem for $$120/1.20 = 100$$ SY, worth 115 asset). The promise "1 PT = 1 asset" holds only while the SY stays solvent.

## The PT/SY market

The market is an AMM between PT and SY whose curve is defined on the *proportion of PT* in the pool rather than on the product of reserves. The model comes from Notional Finance's AMM, and the formulas below are read from `MarketMathCore.sol`.

### State and parameters

`MarketState` holds `totalPt`, `totalSy`, `totalLp`, the immutable `scalarRoot`, `expiry` and `lnFeeRateRoot`, a `reserveFeePercent` from the factory, and `lastLnImpliedRate`. The SY side is converted to asset with the index: $$A = \text{totalSy} \times \text{pyIndex}$$. Time to expiry $$\tau$$ is counted in years of 365 days. Market creation is permissionless (`createNewMarket(PT, scalarRoot, initialAnchor, lnFeeRateRoot)`), and the documentation caps `lnFeeRateRoot` at $$\ln 1.05 \approx 0.0488$$.

### The curve

For a trade that takes $$\Delta$$ PT out of the pool, a negative $$\Delta$$ when PT is sold in, the code computes:

$$
\begin{aligned}
s &= \frac{\text{scalarRoot}}{\tau} \\
p &= \frac{N - \Delta}{N + A} \\
E &= \frac{1}{s}\,\ln\frac{p}{1 - p} + a \\
\text{PT price in asset} &= \frac{1}{E}
\end{aligned}
$$

where $$N$$ is `totalPt`, $$s$$ is the rate scalar, $$a$$ the rate anchor and $$E$$ the exchange rate in PT per asset. The pool's implied rate is read from the same curve with $$\Delta = 0$$:

$$
\begin{aligned}
r &= \frac{\ln E}{\tau} \\
\text{implied APY} &= e^{r} - 1
\end{aligned}
$$

Three things in these formulas carry the design:

- **The logit term $$\ln\frac{p}{1-p}$$.** It is zero at an even pool and grows without bound as PT fills the pool. More PT in the pool means a larger $$p$$, a larger $$E$$, a cheaper PT and a higher implied rate: selling PT into the pool pushes the rate up, and buying PT pulls it down. Liquidity is concentrated around the anchor; `scalarRoot` sets how concentrated. The docs describe a large `scalarRoot` as a tighter, more capital-efficient market with a narrower range of tradeable rates. Pendle's [AMM whitepaper](https://github.com/pendle-finance/pendle-core-v2-public/blob/87685c89d05087535e9b9647eeda0e3d297d1f06/whitepapers/AMM.pdf) treats $$p$$ between 0.1 and 0.9 as the reasonable trading range and derives the rate scalar at the pool's start from an expected and a maximum rate, so that this range covers implied rates from 0 % up to the maximum.
- **The rate scalar grows as expiry nears.** $$s$$ is `scalarRoot × 365 days / timeToExpiry`, so near expiry the same trade moves $$E$$, and with it the rate and the price, less and less. The scalar does not pull the price to 1; the next point does.
- **The anchor is re-solved before every trade.** `_getRateAnchor` picks $$a$$ so that the pool's current proportion $$p_0$$ reproduces the last implied rate at today's $$\tau$$:

$$
\begin{aligned}
a = e^{r_{last}\,\tau} - \frac{1}{s}\,\ln\frac{p_0}{1 - p_0}
\end{aligned}
$$

So without any trade the implied rate stays constant, and the PT price drifts up deterministically as $$e^{-r\tau}$$, reaching 1 at expiry.

The curve has two hard bounds, one at each end of the rate range:

| Bound | Reached by | What reverts |
|---|---|---|
| High rate: more than 96 % PT in the pool after the trade | selling PT, buying YT | market-order PT sales, YT buys and zaps out; limit orders still fill |
| Zero rate: an exchange rate below 1 | buying PT | PT buys, so PT can never be bought above 1 asset and the implied rate cannot go negative |

A zap is a router call that converts to or from another token in one transaction, and limit orders are fills from Pendle's off-chain order book; both are described under [The router](#the-router). Only the high-rate bound is what Pendle's troubleshooting page calls a market going **out of range**: the implied APY has passed the upper end of the yield range that `scalarRoot` and the initial anchor set. Since markets are immutable, Pendle then redeploys a wider pool.

*Implementation:* `MarketProportionTooHigh` (`MAX_MARKET_PROPORTION`) and `MarketExchangeRateBelowOne` in `MarketMathCore.sol`.

### Fees on the rate

The fee is applied to the exchange rate rather than to the amount. With $$\phi$$ = `lnFeeRateRoot`, the fee factor is $$f = e^{\phi\tau}$$, so it shrinks toward 1 as expiry approaches. In `calcTrade`:

- **Buying PT** divides the exchange rate by $$f$$ (fewer PT per asset); the code checks that the post-fee rate is still at least 1. The buyer pays the pre-fee asset amount times $$f$$.
- **Selling PT** returns the pre-fee asset amount divided by $$f$$.

`reserveFeePercent` of the fee goes to the treasury in SY; the rest stays in the pool for LPs. A swap whose LP fee rounds to zero reverts with `MarketZeroNetLPFee`. The factory can set a lower fee for a given router on a given market (`setOverriddenFee`), which is how trades through the Pendle router pay less than direct pool calls.

### Swaps and liquidity

The market exposes only two primitive swaps, `swapExactPtForSy` and `swapSyForExactPt`, and both are flash swaps: the output is sent, `swapCallback` runs if data was passed, and the balance check comes last. The curve gives the cost of a trade from its PT amount, and that relation cannot be inverted in closed form for a given input, so the router solves every other exact-input trade by binary search over the PT amount, bounded by `ApproxParams`.

LP `mint` is proportional to reserves, with 1,000 units locked on the first mint; `burn` is pro-rata and still works after expiry, while swaps and mints revert with `MarketExpired`.

YT is traded on the same pool:

```mermaid
sequenceDiagram
    autonumber
    participant U as "User"
    participant R as "Router"
    participant M as "PT/SY market"
    participant Y as "YT contract"
    U->>R: "SY in, wants YT"
    R->>M: "flash swap: take extra SY, owe PT"
    R->>Y: "user SY + borrowed SY"
    Y-->>R: "PT and YT minted"
    R->>M: "repay the PT"
    R-->>U: "YT"
```

Buying YT therefore sells PT into the pool, and selling YT buys PT from it. A large YT purchase moves the PT price down exactly like a large PT sale, which matters for any oracle that reads this pool.

### A worked trade

The parameters below are illustrative, chosen to make the steps visible; they are not read from a deployed market. Every figure was computed at full precision and is rounded only in the table.

| Input | Value |
|---|---|
| Time to expiry $$\tau$$ | 0.5 year (182.5 days) |
| `scalarRoot`, so $$s = 10 / 0.5$$ | 10, rate scalar 20 |
| `totalPt` $$N$$ | 1,500,000 PT |
| `totalSy`, `pyIndex` | 800,000 SY at 1.25 asset per SY, so $$A$$ = 1,000,000 asset |
| `lastLnImpliedRate` | $$\ln 1.10$$ (10 % implied APY) |
| `lnFeeRateRoot`, `reserveFeePercent` | 0.003, 80 |
| Trade | buy $$\Delta$$ = 10,000 PT |

The steps, in the order `executeTradeCore` takes them:

1. **Spot before the trade.** $$E_0 = e^{0.5 \ln 1.1} = \sqrt{1.1} = 1.048809$$, so PT trades at $$1/E_0 = 0.953463$$ asset.
2. **Anchor.** $$p_0 = 1{,}500{,}000 / 2{,}500{,}000 = 0.6$$, and $$a = 1.048809 - \ln(1.5)/20 = 1.028536$$.
3. **Trade rate.** The code evaluates the curve at the post-trade PT count over the *pre-trade* total: $$p = 1{,}490{,}000 / 2{,}500{,}000 = 0.596$$, so $$E = \ln(1{,}490{,}000/1{,}010{,}000)/20 + a = 1.047977$$, where $$1{,}010{,}000 = 2{,}500{,}000 - 1{,}490{,}000$$ is the $$1 - p$$ side. Before fees, 10,000 PT cost $$10{,}000 / 1.047977 = 9{,}542.20$$ asset, against $$10{,}000 / 1.048809 = 9{,}534.63$$ at the pre-trade spot.
4. **Fee.** $$f = e^{0.003 \times 0.5} = 1.001501$$. The buyer pays $$9{,}542.20 \times f = 9{,}556.52$$ asset, so the fee is 14.32 asset. The post-fee rate $$E/f = 1.046406$$ is above 1, so the trade is allowed.
5. **Settlement in SY.** 9,556.52 asset is 7,645.22 SY at 1.25 (rounded up in the code, `assetToSyUp`). Of the 14.32 asset fee, 80 % (11.46 asset, 9.17 SY) leaves the pool for the treasury, and 2.86 asset stays with the LPs.
6. **New state.** `totalPt` = 1,490,000 and `totalSy` = 807,636.05 (800,000 + 7,645.22 paid in − 9.17 to the treasury). With the same anchor, the new spot rate is $$E_1 = 1.047999$$: the PT spot price rises to 0.954199 and the stored implied APY falls from 10.00 % to 9.83 %.

The buyer paid 0.955652 asset per PT on average, 0.23 % above the pre-trade spot of 0.953463; the fee accounts for about 0.15 points of that.

Buying PT lowers the implied rate. The [PT-reUSD liquidations on Morpho]({{site.url_complet}}/2026/10/11/pt-reusd-morpho-liquidations-pendle-twap-replay/) were the mirror image: a large YT purchase sold PT into the pool and pushed the rate up.

## The PT price to expiry and after

If nobody trades, the anchor keeps the implied rate fixed and the PT price follows $$e^{-r\tau}$$. At a 10 % implied APY this gives 0.909091 one year out, 0.953463 at six months, 0.976454 at three months and 0.992089 at one month. Rate risk shrinks with $$\tau$$: a jump of the implied rate from 10 % to 20 % six months before expiry moves the price from 0.953463 to 0.912871, a 4.26 % fall. The same jump with one month left moves it from 0.992089 to 0.984921, a 0.72 % fall.

![Left, the PT price over the last 365 days before expiry at a constant 10 % implied APY, two linear-discount oracle lines at 10 % and 18 %, and the market price after a jump to 20 % at 182.5 days; right, after expiry an unredeemed PT stays at 1 asset while PT redeemed into SY keeps earning]({{site.url_complet}}/assets/article/blockchain/defi/pendle/pendle-pt-price-expiry.svg)

The left panel shows the three prices at the 182.5-day mark: 0.9535 for the market at 10 %, 0.9500 for a linear oracle at 10 %, and 0.9129 for the market after the rate jump, which a 10 % linear oracle would not see. The right panel shows the cost of not redeeming: at 8 % a year of SY yield, continuously compounded (illustrative), 180 days after expiry the redeemed position is worth about 1.040 asset while the unredeemed PT is still worth 1.

The phases, with what each one does to a PT holder:

| Phase | Market | PT value |
|---|---|---|
| Long before expiry | swaps live; $$\tau$$ is large, so a given rate move costs more price, and the small rate scalar lets a trade move the rate more | $$e^{-r\tau}$$ asset |
| Approaching expiry | the rate scalar grows, price impact per unit traded falls; liquidity and incentives often leave | converges to 1 asset if the SY is solvent |
| At expiry | swaps and mints revert; LP `burn` still works | `redeemPY` returns $$1/\text{pyIndex}$$ SY per PT |
| After expiry | no AMM exit; the exit is `redeemPY` then `SY.redeem` into `getTokensOut()` (router `exitPostExpToToken`) | a fixed amount of asset, no further yield |

## Oracles: TWAP of the rate, or a linear discount

Pendle documents two ways to price a PT. Its oracle overview recommends the **linear-discount** oracle for money markets and keeps the **TWAP** oracle for integrations that need a market-derived price.

### The TWAP oracle

Each market stores observations in a ring buffer (`OracleLib.sol`, adapted from Uniswap V3): a timestamp and a cumulative sum of the ln implied rate over time. At most one observation is written per timestamp, accumulating the *previous* `lastLnImpliedRate` over the elapsed time, so a rate set in a block enters the sum only from the next block. Over a window of $$D$$ seconds:

$$
\begin{aligned}
\bar r &= \frac{C(t) - C(t - D)}{D} \\
\text{PT price in asset} &= e^{-\bar r\,\tau}
\end{aligned}
$$

where $$C(t)$$ is the cumulative ln implied rate recorded at time $$t$$.

`getPtToAssetRateRaw` returns exactly 1 after expiry. The average is taken over the **rate**, and converted to a price at today's $$\tau$$, so the TWAP price still converges to 1 at expiry whatever the rate did. `PendlePYOracleLib` (or the deployed `PendlePYLpOracle` at `0x5542be50420E88dd7D5B4a3D488FA6ED82F6DAc2`) adds the SY solvency check. With $$P$$ the raw PT price in asset above:

$$
\begin{aligned}
\text{PtToAsset} &= P \cdot \min\left(1,\ \frac{\text{SY rate}}{\text{pyIndex}}\right) \\
\text{PtToSy} &= \frac{P}{\max(\text{SY rate},\ \text{pyIndex})}
\end{aligned}
$$

When the SY rate has fallen below the stored index, a PT redeems at the index, so dividing by the larger of the two gives the SY a PT redeems for, not the larger amount the falling rate would suggest.

*Implementation:* `PendlePYOracleLib.getPtToAssetRate` and `getPtToSyRate`.

Practical points from the integration guide and the code:

- **Cardinality starts at 1.** A window older than the oldest observation reverts with `OracleTargetTooOld`. Anyone can call `increaseObservationsCardinalityNext(n)`, and the integrator then waits `D` seconds. `getOracleState(market, duration)` reports readiness and the number of slots needed, about one per block over the window: the integration guide's table gives 85 slots for 900 s on Ethereum. The formula behind that count is in the Integration Notes.
- **Recommended windows** are 900 s or 1800 s. A window of 0 returns the spot `lastLnImpliedRate`, which is manipulable within a block and should not price collateral.
- **Price to SY, not to asset.** Pendle guarantees PT to SY; SY to asset (sUSDe to USDe, ezETH to ETH) happens outside Pendle and may trade at a discount. The docs advise `getPtToSyRate` times the yield token's price over `getPtToAssetRate` times the asset's price.
- **`PendleChainlinkOracle`**, the wrapper with Chainlink's interface, reports `updatedAt = block.timestamp` and `roundId = 0`, so a staleness check on it tests nothing. Its answer reads as whole tokens with 18 decimals: answer / 1e18 is the number of output tokens one input token is worth. For an 18-decimal PT worth 0.95 of a 6-decimal output token, the raw rate per raw unit, scaled by 1e18, is 950,000; the wrapper multiplies it by $$10^{18}/10^{6}$$ and reports $$0.95 \times 10^{18}$$. Pendle's FAQ gives a different reading of the decimals, noted in the Integration Notes.

*Implementation:* `PendleChainlinkOracle._descalePrice`.

### The linear-discount oracle

`PendleSparkLinearDiscountOracle`, deployed through a factory at `0x34C91651A070664279866E5f3d6B4d5F65cbbFFb`, ignores the market entirely:

$$
\begin{aligned}
\text{answer} = 1 - d \cdot \max(\text{maturity} - \text{now},\ 0) / 365\ \text{days}
\end{aligned}
$$

It reads only `block.timestamp`, so it has no liveness or manipulation surface, and it reaches 1 at maturity. It is a discount factor in the PT's asset, not a USD price, and it sees neither a market move nor an SY depeg. Here $$d$$ is a simple annual discount, while the market quotes an APY and prices PT at $$(1 + \text{APY})^{-\tau} = e^{-\ln(1+\text{APY})\,\tau}$$. Setting $$d$$ equal to the market's APY therefore already prices slightly below the market, for two reasons that add up:

- **Linear against exponential.** At the same rate, $$1 - d\tau \le e^{-d\tau}$$: 0.9500 against 0.9512 at 10 % and six months.
- **APY against ln rate.** The market discounts at $$\ln(1.1) = 0.0953$$, less than 0.10, so its price is higher again: 0.9535.

Pendle's parameter guide advises keeping the oracle below the market price until maturity; setting $$d$$ so that the oracle stays under the price at the highest rate the market can trade, the top of its rate range, guarantees this. Its example for PT-USDe-25SEP2025 is 18 %.

If instead $$d$$ is set at the current market rate, and the market rate then rises far enough above $$d$$, through a stress, a depeg or LPs leaving, the oracle **overprices** the PT. For $$d$$ = 10 % six months out, the break-even is an implied APY of 10.80 %, since $$0.95^{-2} - 1 = 0.1080$$. In the jump to 20 % above, a 10 % oracle reads 0.9500 while the market pays 0.9129, 3.91 % less. Positions are then not liquidated while the collateral's sale value falls, and the liquidation bonus is spent on the gap. That is the cost of the liveness the design buys.

[Pricing Yield Collateral on Morpho - Huma's PST Exchange Rate and Ojo's Pendle PT Feed]({{site.url_complet}}/2026/10/11/huma-pst-ojo-pt-oracle-morpho-collateral-pricing/) looks at a third design, Ojo's feed, which takes the minimum of the TWAP and a linear discount.

## The router

`PendleRouterV4` lives at `0x888888888889758F76e7103c6CbF23ABbF58F946` on Ethereum. It is an upgradeable diamond whose full ABI is in `IPAllActionV3.sol` (explorers show only the proxy), and it holds no special permission on markets. Its functions fall into a few groups:

| Need | Functions |
|---|---|
| Buy or sell PT | `swapExactTokenForPt`, `swapExactSyForPt`, `swapExactPtForToken`, `swapExactPtForSy` |
| YT | `swapExactTokenForYt`, `swapExactYtForToken` |
| Liquidity | `addLiquiditySingleToken`, `removeLiquiditySingleToken` and dual variants |
| Mint and redeem | `mintPyFromToken`, `redeemPyToToken`, `exitPreExpToToken`, `exitPostExpToToken`, `exitPostExpToSy` |

`TokenInput` and `TokenOutput` carry a `SwapData` route through an external aggregator, one of those in the `SwapType` enum such as KyberSwap, ODOS or 1inch, for tokens the SY does not take directly, and `LimitOrderData` for fills from Pendle's off-chain limit-order book. Pendle recommends generating calldata with its hosted SDK (`POST /v3/sdk/{chainId}/convert`), and its [API overview](https://docs.pendle.finance/pendle-v2-dev/Backend/ApiOverview) warns that the transaction data is tied to current market conditions and must be generated again right before sending.

## PT as lending collateral

Pendle's own collateral guide lists three uses: leveraging the spread between the PT's fixed rate and the borrow rate, leveraging a short-yield view, and a leveraged long on the asset with fixed carry on top.

Its example of the first: PT-stETH yields 5 %, ETH borrows at 3 %, and a collateral factor of 0.80 allows up to 5x, for at most $$5 \times (5 - 3) = 10$$ %.

That figure is the guide's, and counts the spread on five times the capital. With 1 of equity, 5 of PT and 4 of debt, the return on equity is $$5 \times 5 - 4 \times 3 = 13$$ %, of which 5 points is the unlevered PT yield.

On Morpho Blue, a PT market's oracle can be a `MorphoChainlinkOracleV2` whose base feed is the linear-discount oracle or the TWAP behind a Chainlink-shaped adapter, for which Morpho's documentation lists a community adapter and factory; third-party feeds such as Ojo's min(TWAP, linear) feed are also used. How that price enters a Morpho market's health check is covered in [Morpho Blue and Vault V2]({{site.url_complet}}/2026/11/16/morpho-blue-vault-v2/). Aave's PT price adapter is not in the sources read for this article.

The liquidator's side is short in code and long in consequences. `BoringPtSeller` branches on expiry:

```mermaid
flowchart TD
    S["Liquidator holds seized PT"] --> Q{"PT expired?"}
    Q -->|"no"| A["market.swapExactPtForSy<br/>(reverts past 96 % PT)"]
    Q -->|"yes"| B["YT.redeemPY: PT alone<br/>SY = PT / pyIndex"]
    A --> C["SY.redeem into getTokensOut()"]
    B --> C
    C --> D["sell the yield token<br/>for the loan token"]
```

Every arrow in that path is a dependency: the PT/SY pool's depth before expiry, the SY's output set, and the yield token's own exit through a cooldown or a DEX.

Pendle's sizing rule makes the first one checkable. The letters below differ from the guide's so that they do not clash with the fee factor $$f$$ and the PT proportion $$p$$ used above.

With a deposit cap $$dCap$$, collateral factor $$c$$, share $$k$$ of loans liquidatable at once, close factor $$q$$ and liquidation bonus $$b$$, selling $$dCap \cdot c \cdot k \cdot q \cdot (1 + b)$$ worth of PT must cost less than $$b$$ in price impact. In the guide's Compound V2 example, with $$c = 0.70$$, $$k = 0.30$$, $$q = 0.5$$ and $$b = 0.08$$, that is $$0.1134 \cdot dCap$$.

The guide also warns that sales lower the price and liquidate more loans, so a strict analysis takes $$k = 1$$.

The risks of PT collateral are collected in the Risks annex below.

## Conclusion

Pendle V2 turns a yield-bearing token into a fixed-maturity bond and a yield strip, and prices the bond with a curve built on the implied rate rather than on reserves.

- **SY** standardises the yield token behind `exchangeRate()`, with a narrow redemption set, an owner pause and, for newer SYs, an upgradeable proxy.
- **PT and YT** are minted against SY at a PY index that never decreases. YT accrues $$B(I_1 - I_0)/(I_0 I_1)$$ SY; after expiry the yield on unredeemed PT goes to the treasury.
- **The market** prices PT on the logit of the PT proportion, with a rate scalar that grows toward expiry and an anchor re-solved before each trade so that the implied rate persists. Fees are on the rate, and the pool refuses trades past 96 % PT or below a zero rate.
- **The worked trade** of 10,000 PT moved the implied APY from 10.00 % to 9.83 % and cost 0.23 % above spot, of which about 0.15 points was fee.
- **The two oracles** trade accuracy for liveness: the TWAP follows the market and can be moved by it, while the linear discount ignores the market and overprices PT when rates rise far enough above its discount.
- **As collateral**, a PT depends on the pool's depth before expiry, the SY's exit after it, the solvency of the yield token, and Pendle's and the SY's admin keys.

![Mindmap of Pendle V2 covering the SY wrapper, the PT and YT split, the market AMM, the PT price, the oracles, the router and PT as collateral]({{site.url_complet}}/assets/article/blockchain/defi/pendle/2026-11-16-pendle-v2-pt-yt-amm-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Yield-bearing token** | A token whose value grows against an underlying asset through an exchange rate, such as wstETH against stETH or an ERC-4626 share. |
| **Asset** | What the SY's yield token appreciates against, given by `assetInfo()`; PT redeems for 1 asset at expiry. |
| **SY (Standardized Yield)** | Pendle's wrapper around a yield-bearing token, with `deposit`, `redeem` and `exchangeRate()` in asset per SY. |
| **PT (principal token)** | A claim to 1 asset at expiry, minted together with YT; before expiry it trades at a discount on the market. |
| **YT (yield token)** | A claim to the interest and rewards of 1 asset of principal until expiry; worth zero after. |
| **PY index** | `max(SY.exchangeRate(), pyIndexStored)`, the never-decreasing index at which PT and YT are minted and redeemed. |
| **Expiry (maturity)** | The timestamp after which swaps and mints revert and PT redeems alone; YT stops earning at the first interaction after it. |
| **Implied rate** | The fixed rate at which the market prices PT; stored as `lnImpliedRate` = ln(1 + APY). |
| **Exchange rate (market)** | $$E$$, the number of PT per asset on the curve; its inverse is the PT price. |
| **Rate scalar** | `scalarRoot × 365 days / timeToExpiry`, the factor that flattens the logit curve and grows toward expiry. |
| **scalarRoot** | An immutable market parameter that sets how concentrated liquidity is around the anchor. |
| **Rate anchor** | The curve's offset, re-solved before each trade so that the current pool reproduces the last implied rate. |
| **lnFeeRateRoot** | The market's fee parameter in log form; the fee factor is $$e^{\phi\tau}$$ and applies to the exchange rate. |
| **Out of range** | A market whose rate has left what its curve can trade: selling PT and buying YT revert, limit orders still work. |
| **Flash swap** | A swap that sends the output first and checks the input after a callback; Pendle uses it for every swap and for YT trades. |
| **TWAP oracle** | The market's ring buffer of cumulative ln implied rates, averaged over a window and converted to a PT price at today's time to expiry. |
| **Cardinality** | The number of observation slots a market keeps; it starts at 1 and must be raised before a TWAP window can be read. |
| **Linear-discount oracle** | A feed returning $$1 - d\tau$$ from the timestamp alone, without reading the market. |
| **Liquidation threshold (LLTV)** | The ratio of debt to oracle-valued collateral at which a lending position becomes liquidatable. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| The PY index never decreases. | `_pyIndexCurrent` takes the max of the SY rate and the stored index. | Never by design; a falling SY rate is absorbed by redeeming fewer SY, not by lowering the index. |
| One PT plus one YT are backed by one asset at the current index before expiry. | `mintPY` mints SY × pyIndex of each; `redeemPY` needs equal amounts. | The SY's exchange rate falls below the index: the backing in asset shrinks. |
| PT can never be bought above 1 asset in the pool. | `MarketExchangeRateBelowOne` on the pre- and post-fee rate. | Never by design; the market reverts instead. |
| The pool never holds more than 96 % PT after a trade. | `MAX_MARKET_PROPORTION` in `_getExchangeRate`. | Never by design; sales of PT revert past it. |
| No swap or mint happens after expiry. | `MarketExpired` in `executeTradeCore` and `mint`. | Never by design; only `burn` and redemptions work. |
| Without trades, the implied rate stays constant over time. | The anchor is re-solved from `lastLnImpliedRate` before each trade. | A trade, which moves `lastLnImpliedRate`. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| PT and YT carry the asset's decimals, SY the yield token's, and LP tokens 18; assets with fewer than 18 decimals get a `scaled18` wrapper. Every rate in the contracts is 1e18-scaled on raw units. | Read each token's `decimals()` before converting a rate into a price. |
| `PendlePYLpOracle` sizes the cardinality as $$\lceil D \times 1000 / \text{blockCycleNumerator} \rceil + 1$$, where `blockCycleNumerator` / 1000 is a block time in seconds set below the real one; the code comments give 11000 on Ethereum, which yields 83 slots for 900 s against 85 in the integration guide. | Use the guide's figure or read `blockCycleNumerator()` on-chain rather than assuming either. |
| `PendleChainlinkOracle.updatedAt` is always `block.timestamp`. | Do not treat it as freshness; check readiness with `getOracleState`. |
| The answer of `PendleChainlinkOracle` is in 18-decimal natural units after rescaling by the token decimals; Pendle's FAQ states $$18 + \text{out}$$ decimals, which contradicts the formula the FAQ itself gives. | Test the scaling against a known rate on a pair with different decimals before relying on either reading. |
| `PendleSparkLinearDiscountOracle.latestRoundData` returns `updatedAt = 0`. | A Chainlink-style staleness check rejects it; the answer depends only on `block.timestamp`, so exempt this feed from that check rather than disabling it for the whole oracle. |
| A TWAP window older than the oldest observation reverts. | Raise cardinality first and wait the window length before reading. |
| `getPtToAssetRate` assumes the yield token redeems at its exchange rate. | Price to SY and multiply by the yield token's own price where possible. |
| Market swaps revert after expiry; `redeemPY` does not need YT then. | Branch the liquidation path on `PT.isExpired()`, as `BoringPtSeller` does. |
| `pyIndexCurrent()` is state-changing. | Use `pyIndexStored()` and `max(syIndex, stored)` in views. |
| `previewDeposit` and `previewRedeem` are not audited for on-chain use. | Call them with `eth_call` only. |

### Risks

The risks below are those a PT holder or a lender against PT carries. They start from Pendle's own collateral risk analysis (`Oracles/PTAsCollateral.md`) and add what the code shows. Points from this article's own reasoning are marked *(derived)*.

#### Smart contracts and transparency

- **Pendle core.** The core repository lists audits by Ackee, CMichel, Dedaub, Dingbats, 0xleastwood, WatchPug, ChainSecurity and Spearbit, and separate reviews of markets V6 and V7 and of the oracles. Pendle's collateral guide states that there have been no incidents in Pendle contracts since June 2021; the page is undated, and only its sizing example carries a date, June 2023. The audit PDFs were not read for this article.
- **Each SY separately.** Every PT sits on its own SY implementation, audited separately in `Pendle-SY-Public`. The SY is the part that is upgradeable and pausable, so its code and its admin matter as much as the core's.
- **Upgradeability, both sides.** Markets are immutable, so a market's maths cannot change under an LP or a lender, and a bug in it cannot be patched either. Newer SYs and the router are upgradeable: they can be fixed, and the proxy admin can replace their logic.

#### External dependencies

- **The yield token's issuer.** A PT is as good as the protocol behind its SY: Ethena for sUSDe, Lido for wstETH. A loss there reaches the PT through the SY rate.
- **The oracle composition.** A money market prices PT through Pendle's TWAP or a linear discount, and usually multiplies it by an external price for the asset or yield token, which brings that feed's own risks.
- **Aggregators.** Router routes through external aggregators such as KyberSwap and the limit-order book are off-chain components; they affect execution, not the market's maths.

#### Depeg

- **PT = 1 asset only if the SY is solvent.** The PY index does not fall, so a drop in the SY rate passes to PT holders in full. The documentation's example returns 115 asset for 120 PT.
- **Asset versus yield token.** PT's asset, such as USDe or stETH, can itself trade away from its target, and the yield token can trade below its exchange rate (an exit queue, a cooldown). A feed priced in asset hides both.

#### Collateral and market risk

- **Rate risk scales with time to expiry.** A rate jump from 10 % to 20 % six months out moves the price 4.26 % (*derived*, from the worked figures). A lender's margin must cover the rate range, not only the asset's volatility.
- **Pool-driven moves.** Buying YT sells PT into the pool. A TWAP lags such a move and then follows it, which is what liquidated PT-reUSD loans on Morpho in August 2026.
- **Linear oracle gap.** With the rate far enough above $$d$$, past 10.80 % implied APY for $$d$$ = 10 % six months out, the oracle overprices the PT, and liquidations come late or not at all while the sale value falls.

#### Liquidity

- **One pool, thinning toward expiry.** Liquidators sell PT on one PT/SY market; LPs and incentives often leave as maturity nears. Pendle's sizing rule ($$0.1134 \cdot dCap$$ in its Compound example) is the test to run at the current depth.
- **Out of range.** Past 96 % PT, sells revert and only limit orders fill.
- **After expiry.** No AMM exit; the exit is `redeemPY` then `SY.redeem` into a narrow output set, then the yield token's own exit.

#### Centralisation and governance

- **Admin keys.** On Ethereum, `deployments/1-core.json` names a `proxyAdmin` (`0xA28c08f165116587D4F3E708743B4dEe155c5E64`), a `timelockController` (`0x68d8D192dF476bC01895E16b0ED3945673d777AC`) and a `timelockedProxyAdmin`. Their owners, thresholds and delays were not read on-chain for this article.
- **SY owner.** The SY owner can pause all transfers of an SY, freezing the market, redemptions and any liquidation path through it.
- **Fees.** The factory owner sets `reserveFeePercent`, the treasury and per-router fee overrides.

#### Loss sharing

- **No insurance layer in Pendle.** A loss in the SY passes pro rata to PT and YT holders through the index; there is no Pendle-level buffer described in the sources (*derived*).
- **Lenders.** A lender against PT takes the loss when liquidations fail to cover the debt, through the money market's own bad-debt rule.

#### Regulatory

- None found in the sources specific to Pendle's design; the regulatory profile follows the underlying yield token.

#### Summary

| Risk | Where it comes from | What the design does about it | What remains |
|------|---------------------|-------------------------------|--------------|
| SY insolvency | The yield token's issuer | The oracle library scales the price down when the SY rate is below the index | PT holders take the full loss |
| Rate jump | Market trading, YT buying | TWAP smooths over its window | The price still falls; a long window delays liquidations |
| Linear oracle gap | Rate far enough above the discount $$d$$ | None, by design | Late liquidations, bonus eaten by the gap |
| Pool depth | One PT/SY pool, LPs leaving near expiry | Concentrated liquidity curve | Cascades, out-of-range sells revert |
| Post-expiry exit | No AMM after expiry | `redeemPY` without YT | Narrow SY output set, yield token exit |
| Pause and upgrade | SY owner, proxy admin | Timelocked proxy admin listed in deployments | Owner thresholds not verified here |
| Contract bugs | Core and SY code | Multiple audits, immutable markets | Each SY needs its own review |

### Timeline

Events up to 25 November 2026.

| Date | Event | Why it matters here | Source |
|------|-------|---------------------|--------|
| 30 May 2022 | Vu Nguyen, Long Vuong and Anton Buenavista created EIP-5115, the SY Token interface for wrapped yield-bearing tokens, which is still a Draft. | The SY wrapper that every PT and YT sits on follows this interface. | [ERC-5115: SY Token](https://eips.ethereum.org/EIPS/eip-5115) |
| 23 November 2022 | The first Pendle V2 market factory was deployed on Ethereum in block [16032059](https://etherscan.io/block/16032059). | It marks the start of the PT/SY markets and logit curve described in the article. | [Market factory creation transaction](https://etherscan.io/tx/0xf281802ac6e2b68c38cf170c2a47433d1a0e1d26ebad023fd0c60f3b4752d1ff) |
| 26 May 2023 | WatchPug's PT oracle audit reported a high-severity issue for the case where `SY.exchangeRate()` falls below `YT.pyIndexCurrent()`. | This is the negative-yield case that the oracle library now handles by scaling the PT price down. | [WatchPug, Pendle PT Oracle Audit Report](https://github.com/pendle-finance/pendle-core-v2-public/blob/87685c89d05087535e9b9647eeda0e3d297d1f06/audits/LpPtoracle/WatchPug-PtOracle.pdf) |
| 3 September 2024 | An attacker exploited Penpie, a yield protocol built on Pendle, through a market it had created on Pendle, in block [20671878](https://etherscan.io/block/20671878), and Pendle paused its contracts in response. | Market creation is permissionless, so a market is only as safe as its SY, and the pause shows who can stop the core contracts. | [Pendle, Post Mortem (on X)](https://x.com/pendle_fi/status/1831168623634993402) |
| 11 April 2025 | Aave's ARFC to onboard PT-sUSDE-31JUL2025 to the Aave V3 Core instance passed its Snapshot vote, with PTs to be priced by a dynamic linear discount mechanism. | It brings PT collateral to Aave, whose price adapter this article does not cover. | [Aave governance, ARFC Onboard Pendle PT tokens to Aave V3 Core Instance](https://governance.aave.com/t/arfc-onboard-pendle-pt-tokens-to-aave-v3-core-instance/20541) |
| 16 April 2025 | The `sparkLinearDiscountOracleFactory` listed in Pendle's Ethereum deployments was created in block [22280882](https://etherscan.io/block/22280882). | It deploys the linear-discount oracle that the article compares with the TWAP oracle. | [Factory creation transaction](https://etherscan.io/tx/0x2f15874562f57d4e8fa3321baa692dd742bc6d9eb3dc8344c880f2e217ab4869) |
| 13 June 2025 | Phoenix Labs proposed PT-syrupUSDC and PT-USDe collateral for the Spark DAI Morpho Vault at a 91.5 % LLTV, priced by the Pendle linear discount oracle at a 15 % discount rate. | It is a live example of the linear-discount oracle on Morpho and of the discount rate a lender chooses. | [Sky forum, June 26 2025 proposed changes to Spark](https://forum.skyeco.com/t/june-26-2025-proposed-changes-to-spark-for-upcoming-spell/26663) |
| 23 October 2025 | The `marketFactoryV6` of the Ethereum deployments was created in block [23638439](https://etherscan.io/block/23638439), on the date of WatchPug's MarketV6 audit report. | Markets created by this factory carry the market code that preceded `PendleMarketV7`. | [WatchPug, Pendle MarketV6 Audit Report](https://github.com/pendle-finance/pendle-core-v2-public/blob/87685c89d05087535e9b9647eeda0e3d297d1f06/audits/marketV6/WatchPug.pdf) |
| 20 January 2026 | Commit "Deprecate voting escrow" renamed `PendleMarketV6` to `PendleMarketV7`, removed the vePENDLE voting contracts and added `StakedPendle` (sPENDLE). | `PendleMarketV7` is the market contract the article analyses. | [pendle-core-v2-public commit 7bde3ec](https://github.com/pendle-finance/pendle-core-v2-public/commit/7bde3ecbec38082b5c00f73a4ef142ed0f71cdb8) |
| 7 July 2026 | Pendle deployed a `timelockController` and a `timelockedProxyAdmin` on Ethereum in blocks [25481956](https://etherscan.io/block/25481956) and [25481966](https://etherscan.io/block/25481966). | A timelocked admin puts a delay on upgrades, which changes the pause and upgrade risk discussed above; the delay itself was not read on-chain. | [Timelock creation transaction](https://etherscan.io/tx/0x23567ad03ed62f53656c9241f88cd0c59d05ef5cc12a99731a970f73d79f4427) |

## Frequently Asked Questions

**Q: Why is a PT worth 1 asset at expiry and not 1 SY?**

Because PT and YT are minted at the PY index: one SY at an index of 1.25 mints 1.25 PT and 1.25 YT. The PT side is a claim to the asset principal, the YT side to everything the SY earns on top. At expiry one PT redeems for $$1/\text{pyIndex}$$ SY, which is 1 asset at that index.

**Q: What does the rate anchor do, and why is it recomputed before each trade?**

The anchor is the offset of the curve. Before each trade, `_getRateAnchor` chooses it so that the pool's current PT proportion gives back the last stored implied rate at the current time to expiry.

As a result, the passage of time alone does not move the implied rate; only trades do, and the PT price drifts up as $$e^{-r\tau}$$ to 1 when nobody trades. The rate scalar, growing as $$1/\tau$$, only makes each trade move the rate less as expiry nears.

**Q: How does buying YT affect the PT price, given that there is no YT pool?**

The router flash-swaps SY out of the PT/SY market, mints PT and YT from the user's SY plus the borrowed SY, repays the market in PT and hands the YT to the user. The market receives PT and gives SY, which is a PT sale. A large YT purchase therefore pushes the PT price down and the implied rate up, and a TWAP oracle on that market follows after its window.

**Q: In the worked trade, why did the buyer pay 0.23 % above spot, and how much of it was the fee?**

Two parts add up:

- **Price impact.** Before fees the trade rate was 1.047977 PT per asset against a spot of 1.048809, so 10,000 PT cost 9,542.20 asset instead of 9,534.63 at spot.
- **Fee.** The fee factor $$e^{0.003 \times 0.5}$$ multiplies the cost by 1.001501, adding 14.32 asset, about 0.15 % of the trade.

The total is 9,556.52 asset, 0.955652 per PT against a spot price of 0.953463.

**Q: A lending market prices PT-sUSDe with a linear-discount oracle at 10 % six months before expiry. The implied rate jumps to 20 %. What happens to the market's borrowers and lenders?**

The oracle still reads 0.9500 asset, while the PT now sells for 0.9129, 3.91 % less.

Borrowers near their threshold are not liquidated, because the oracle does not see the fall. If one is liquidated, the liquidator receives PT valued at 0.95 but sells it for 0.913, so the bonus must cover the gap before the liquidation is profitable. If it does not, liquidations stop and the lenders carry the difference as possible bad debt. A TWAP oracle would have moved toward 0.9129 within its window.

**Q: Why should an integrator price PT to SY rather than to asset?**

Pendle guarantees the conversion from PT to SY, but SY to asset happens outside Pendle: sUSDe to USDe goes through Ethena's cooldown or a DEX. `getPtToAssetRate` times the asset price assumes that conversion happens at the exchange rate. `getPtToSyRate` times the price of the yield token itself does not, so a discount on the yield token shows up in the collateral value.

## Gaps

The points below were not settled by the sources read for this article.

| Gap | Why it matters | What to read or verify |
|-----|----------------|------------------------|
| The worked trade uses illustrative `scalarRoot`, fee and reserve values, not a deployed market's. | Real markets may have very different price impact for the same size. | `readState(router)` on a live market, or the API's market data. |
| The Ethereum `blockCycleNumerator` of `PendlePYLpOracle` was not read on-chain; 11000 comes from a code comment, and gives 83 slots for 900 s where the integration guide's table gives 85. | A different value changes the cardinality a TWAP window needs. | `blockCycleNumerator()` at `0x5542be50420E88dd7D5B4a3D488FA6ED82F6DAc2`. |
| Owners, thresholds and delays of the proxy admin, timelock and SY owners were not read on-chain. | They decide who can pause or upgrade what a PT depends on. | `owner()` and `getMinDelay()` on the addresses in `deployments/1-core.json`. |
| Aave's PT price adapter is not covered by the sources. | An Aave PT listing may price differently from both oracles described here. | Aave governance proposals for PT listings. |
| Only the sUSDe, wstETH and ERC-4626 SY implementations were read. | Output sets, caps and pause hooks differ per SY. | The specific SY under `Pendle-SY-Public/.../implementations/`. |
| The audit reports were listed, not read. | Known findings on markets V6/V7 and the oracles are not summarised. | `pendle-core-v2-public/audits/`. |
| The documentation's wstETH example gives 0.8928 wstETH per PT at a rate of 1.2, which would give 0.8333. | One of the two figures in the doc is wrong; the article uses the computed 0.8333. | `HighLevelArchitecture.md`, PT section. |
| No Ethereum deployment of `PendleMarketFactoryV7Upg` was found in `deployments/1-core.json`, so the timeline dates `PendleMarketV7` by its commit, not by a deployment. | Markets created before the V7 code still run older market contracts. | The factory addresses in [`deployments/1-core.json`](https://github.com/pendle-finance/pendle-core-v2-public/blob/87685c89d05087535e9b9647eeda0e3d297d1f06/deployments/1-core.json) and their implementation slots. |

## References

### Analyzed source

- [pendle-finance/pendle-core-v2-public](https://github.com/pendle-finance/pendle-core-v2-public) — analyzed at commit [`87685c89d05087535e9b9647eeda0e3d297d1f06`](https://github.com/pendle-finance/pendle-core-v2-public/tree/87685c89d05087535e9b9647eeda0e3d297d1f06) (v6.11.0 in its changelog), 2026-11-16
- [pendle-finance/Pendle-SY-Public](https://github.com/pendle-finance/Pendle-SY-Public) — analyzed at commit [`73676d931102a369a978a713abfd0b48e3e34361`](https://github.com/pendle-finance/Pendle-SY-Public/tree/73676d931102a369a978a713abfd0b48e3e34361), 2026-11-16

### Documentation

- [Pendle V2 developer documentation](https://docs.pendle.finance/pendle-v2-dev/), read 2026-11-16
- [Pendle Oracle Overview](https://docs.pendle.finance/pendle-v2-dev/Oracles/OracleOverview)
- [PT as Collateral in a Money Market](https://docs.pendle.finance/pendle-v2-dev/Oracles/PTAsCollateral)
- [Linear Discount Oracle](https://docs.pendle.finance/pendle-v2-dev/Oracles/DeterministicOracles/LinearDiscountOracle) and [Choosing Linear Discount Parameters](https://docs.pendle.finance/pendle-v2-dev/Oracles/DeterministicOracles/ChoosingLinearDiscountParams)
- [How to Integrate PT and LP Oracle](https://docs.pendle.finance/pendle-v2-dev/Oracles/HowToIntegratePtAndLpOracle)
- [Vu Nguyen, A study on AMMs for trading fixed yield and Pendle V2's Principal Token AMM](https://github.com/pendle-finance/pendle-core-v2-public/blob/87685c89d05087535e9b9647eeda0e3d297d1f06/whitepapers/AMM.pdf), 14 October 2022 (`whitepapers/AMM.pdf` in the analyzed repository), read 2026-11-18
- [Pendle API Overview](https://docs.pendle.finance/pendle-v2-dev/Backend/ApiOverview) and [Router Types and Utility Functions](https://docs.pendle.finance/pendle-v2-dev/Contracts/PendleRouter/ApiReference/Types)
- [Spark forum, June 26 2025 proposed changes to Spark](https://forum.sky.money/t/june-26-2025-proposed-changes-to-spark-for-upcoming-spell/26663) (linear discount rates for PT listings), cited by Pendle and read 2026-11-25 for the timeline
- [Uniswap V3 oracle concepts](https://docs.uniswap.org/concepts/protocol/oracle)
- [ERC-4626: Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-4626)
- [Claude Code](https://claude.com/product/claude-code)

### Timeline sources

- [ERC-5115: SY Token](https://eips.ethereum.org/EIPS/eip-5115), Vu Nguyen, Long Vuong and Anton Buenavista, created 30 May 2022, read 2026-11-25
- [WatchPug, Pendle PT Oracle Audit Report](https://github.com/pendle-finance/pendle-core-v2-public/blob/87685c89d05087535e9b9647eeda0e3d297d1f06/audits/LpPtoracle/WatchPug-PtOracle.pdf), 26 May 2023, read 2026-11-25
- [WatchPug, Pendle MarketV6 Audit Report](https://github.com/pendle-finance/pendle-core-v2-public/blob/87685c89d05087535e9b9647eeda0e3d297d1f06/audits/marketV6/WatchPug.pdf), 23 October 2025, read 2026-11-25
- [Pendle, Post Mortem](https://x.com/pendle_fi/status/1831168623634993402) (on X), Penpie incident, 4 September 2024, read 2026-11-25
- [Aave governance, ARFC Onboard Pendle PT tokens to Aave V3 Core Instance](https://governance.aave.com/t/arfc-onboard-pendle-pt-tokens-to-aave-v3-core-instance/20541), ACI, 7 January 2025 (Snapshot result 11 April 2025), read 2026-11-25
- [Sky forum, June 26 2025 proposed changes to Spark](https://forum.skyeco.com/t/june-26-2025-proposed-changes-to-spark-for-upcoming-spell/26663), Phoenix Labs, 13 June 2025, read 2026-11-25
- [pendle-core-v2-public commit 7bde3ec, Deprecate voting escrow](https://github.com/pendle-finance/pendle-core-v2-public/commit/7bde3ecbec38082b5c00f73a4ef142ed0f71cdb8), Pendle, 20 January 2026, read 2026-11-25
- Contract creation blocks and transactions for the market factories, the linear-discount oracle factory and the timelock, read from Ethereum on 2026-11-25. Powered by [Etherscan.io APIs](https://etherscan.io)

### Related articles

- [Automated Market Makers (AMMs) - Overview]({{site.url_complet}}/2025/07/29/automated-market-makers-amm/)
- [How Morpho Works - Blue Markets, Liquidations, Oracles and Vault V2]({{site.url_complet}}/2026/11/16/morpho-blue-vault-v2/)
- [How Morpho Blue Works - Isolated Lending Markets, Shares, Liquidations and Bad Debt]({{site.url_complet}}/2026/10/10/morpho-blue-lending-markets/)
- [The PT-reUSD Liquidations on Morpho - How a 320,000 SY Trade Liquidated 36M, Replayed from On-Chain State]({{site.url_complet}}/2026/10/11/pt-reusd-morpho-liquidations-pendle-twap-replay/)
- [Pricing Yield Collateral on Morpho - Huma's PST Exchange Rate and Ojo's Pendle PT Feed]({{site.url_complet}}/2026/10/11/huma-pst-ojo-pt-oracle-morpho-collateral-pricing/)
- [Risk of Ethena's USDe and sUSDe - Backing Venues, Depeg Priors and a Leveraged PT Position]({{site.url_complet}}/2026/10/11/ethena-usde-risk-backing-venues-leveraged-positions/)
