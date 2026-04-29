# Pendle Overview

[TOC]

[Pendle](https://pendle.finance/) is a permissionless yield-trading protocol where users can execute various yield-management strategies.

## What does Pendle do?

We give users the reins to their yield.

[Pendle](https://pendle.finance/) is a permissionless yield-trading protocol where users can execute various yield-management strategies.

There are 3 main parts to fully understand Pendle:

1. Yield Tokenization

   First, Pendle wrap **yield-bearing tokens** into **SY**(standardized yield tokens), which is a wrapped version of the underlying yield-bearing token that is compatible with the Pendle AMM (e.g. stETH → SY-stETH). SY is then split into its principal and yield components, **PT** (principal token) and **YT** (yield token) respectively, this process is termed as yield-tokenization, where the yield is tokenized into a separate token.

2. Pendle AMM

   Both **PT** and **YT** can be traded via Pendle’s **AMM**. Even though this is the core engine of Pendle, understanding of the AMM is not required to trade PT and YT.

3. vePENDLE

As a yield derivative protocol, we are bringing the TradFi interest derivative market ([worth over $400T in notional value](https://www.bis.org/publ/otc_hy2111/intgraphs/graphA3.htm)) into DeFi, making it accessible to all.

By creating a yield market in DeFi, Pendle unlocks the full potential of yield, enabling users to execute advanced yield strategies, such as:

- Fixed yield (e.g. earn fixed yield on stETH)
- Long yield (e.g. bet on stETH yield going up by purchasing more yield)
- Earn more yield without additional risks (e.g. provide liquidity with your stETH)

https://docs.pendle.finance/Introduction#what-does-pendle-do

There are 3 main parts to fully understand Pendle:

### Yield Tokenization

First, Pendle wrap **yield-bearing tokens** into **SY**(standardized yield tokens), which is a wrapped version of the underlying yield-bearing token that is compatible with the Pendle AMM (e.g. stETH → SY-stETH). 

SY is then split into its principal and yield components:

-  **PT** (principal token) 
-  **YT** (yield token) respectively, this process is termed as yield-tokenization, where the yield is tokenized into a separate token.

Pendle AMM

Both **PT** and **YT** can be traded via Pendle’s **AMM**. Even though this is the core engine of Pendle, understanding of the AMM is not required to trade PT and YT.

vePENDLE

As a yield derivative protocol, we are bringing the TradFi interest derivative market ([worth over $400T in notional value](https://www.bis.org/publ/otc_hy2111/intgraphs/graphA3.htm)) into DeFi, making it accessible to all.

By creating a yield market in DeFi, Pendle unlocks the full potential of yield, enabling users to execute advanced yield strategies, such as:

- Fixed yield (e.g. earn fixed yield on stETH)
- Long yield (e.g. bet on stETH yield going up by purchasing more yield)
- Earn more yield without additional risks (e.g. provide liquidity with your stETH)
- A mix of any of the above strategies, learn more on how to execute these strategies at our [Pendle Academy](https://pendle.gitbook.io/pendle-academy)

https://docs.pendle.finance/Introduction

## Yield tokenization

###  Wrapped yield-bearing tokens (SY)

SY is a token standard that implements a standardized API for wrapped yield-bearing tokens within smart contracts. All yield-bearing tokens can be wrapped into SY, giving them a common interface that can be built upon. SY opens up Pendle’s yield-tokenization mechanism to all yield-bearing tokens in DeFi, creating a permissionless ecosystem.

> For example, stETH, cDAI and yvUSDC can be wrapped into SY-stETH, SY-cDAI and SY-yvUSDC, standardizing their yield-generating mechanics to be supported on Pendle.

As all SYs have the same mechanism, Pendle interacts with SY as the main interface to all yield-bearing tokens. PT and YT are minted from SY and Pendle AMM pools trade PT against SY.

While this might seem daunting, Pendle automatically converts yield-bearing tokens into SY and vice versa. This process happens automatically behind the scenes, making users feel as if they’re interacting directly with their yield-bearing tokens instead of having to manually deal with SY <> yield-bearing token conversion.

While this standard benefits Pendle, our vision for SY extends beyond just our own protocol. SY aims to create unprecedented composability across all of DeFi, enabling developers to seamlessly build on top of existing contracts without the need for manual integration.

Read more about SY and EIP-5115 [here](https://eips.ethereum.org/EIPS/eip-5115).

### Principal Token (PT)

Principal Token (PT) represents the principal portion of an underlying yield-bearing asset. Upon maturity, PT can be redeemed at 1:1 for the accounting asset. This is the base, principal asset deployed in the underlying protocol such as Lido, Renzo, and Aave (e.g. ETH in stETH, ETH in ezETH, USDC in aUSDC).

Since the collective value of its yield component has been separated, PT can be acquired at a discount relative to its accounting asset. Assuming no swaps, the value of PT will approach and ultimately match the value of accounting asset on maturity when redemption is enabled.

This appreciation in value is what establishes its Fixed Yield APY.

### Redemption Value

In general, yield bearing assets can be broadly categorized as:

1. Rebasing assets - tokens that increase in count/number overtime as yield is accrued

   *Examples: stETH, aUSDC*

2. Interest-bearing assets - tokens that increase in value overtime as yield is accrued

   *Examples: ezETH, wstETH*



### Yield token (YT)

Yield Token (YT) represents the yield component of an underlying yield-bearing asset.

By holding YT, yield from the underlying asset will be streamed to the users, up until maturity. This rate of yield production is represented as “[Underlying APY](https://docs.pendle.finance/ProtocolMechanics/Glossary)” in the Pendle app.

For example, buying 10 YT-stETH and holding them for 5 days lets you receive all of the yield equivalent to a 10 ETH deposit on Lido within the same period of time.

The value of YT trends towards $0 as it approaches maturity (*ceteris paribus*), becoming $0 upon maturity. Users profit when the total yield collected up to that point ends up being higher than the cost of YT acquisition.

You can think of [Implied APY](https://docs.pendle.finance/ProtocolMechanics/Glossary) as the “rate” at which YT is priced by the market. If the average Underlying APY ends up being higher than the “rate” or Implied APY that you paid for, you will profit.

As such, buying YT can be treated as “longing the yield” of an asset.

You can learn more about yield trading on Pendle [here](https://app.pendle.finance/trade/education/learn).

Note: YT yields are distributed as SY, which can be unwrapped back into the underlying asset using [SY Unwrapper](https://docs.pendle.finance/ProtocolMechanics/YieldTokenization/SY).

## Liquidity engines

### Pendle’s V2 AMM

Pendle’s V2 AMM is designed specifically for trading yield, and takes advantage of the behaviors of PT and YT.

The AMM model was adapted from Notional Finance's AMM. The AMM curve changes to account for yield accrued over time and narrows PT’s price range as it approaches maturity. By concentrating liquidity into a narrow, meaningful range, the capital efficiency to trade yield is increased as PT approaches maturity

Furthermore, we managed to create a pseudo-AMM that allows us to both facilitate PT and YT swaps using just a single pool of liquidity. With a PT/SY pool, PT can be directly traded with SY, while YT trades are also possible via flash swaps.

Liquidity on Pendle V2 comprises of PT/SY (where SY is simply a wrapped version of the underlying yield bearing asset). This means that LPs earn yields from:

1. PT fixed yield
2. Underlying yield (SY yield)
3. Swap fees (from PT and YT swaps)
4. $PENDLE incentives

## Swaps

[docs.pendle.finance/ProtocolMechanics/LiquidityEngines/AMM#swaps](https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/AMM#swaps)

Both PT and YT are tradeable anytime on Pendle through a single pool of liquidity. This is made possible by implementing a pseudo-AMM with flash swaps.

Liquidity pools in Pendle V2 are set up as PT/SY, e.g. PT-aUSDC / SY-aUSDC. Swapping PT is a straightforward process of swapping between the 2 assets in the pool, while swapping YT is enabled via flash swaps in the same pool.

> Auto-routing is built in, allowing anyone to trade PTs and YTs with any major asset.

### Flash Swaps

[docs.pendle.finance/ProtocolMechanics/LiquidityEngines/AMM#flash-swaps](https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/AMM#flash-swaps)

Flash swaps are possible due to the relationship between PT and YT. As PT and YT can be minted from and redeemed to its underlying SY, we can express the price relationship:
$$
P(T) + P(Y) = P(Underlying)
$$
Knowing that YT price has an inverted correlation against PT price, we use this price relationship to utilise the PT/SY pool for YT swaps.

Buying YT:

1. Buyer sends SY into the swap contract (auto-routed from any major token)
2. Contract withdraws more SY from the pool
3. Mint PTs and YTs from all of the SY
4. Send the YTs to the buyer
5. The PTs are sold for SY to return the amount from step 2

## Matured LP

https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/AMM#matured-lp

Upon maturity, LPs are able to Zap Out + Redeem PT for Underlying + Claim Rewards in a single transaction:

1. Visit [Pendle Trade](https://app.pendle.finance/trade/pools) and toggle to the “Inactive” pool list
2. Select a pool
3. Toggle “Claim All Pool Rewards”
4. Select an output asset. Pendle will automatically Redeem PT for Underlying > Unwrap SY > Perform Swaps (if needed) here

## Key Features

https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/AMM#key-features

### Minimal Impermanent Loss (IL)

https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/AMM#minimal-impermanent-loss-il

Pendle V2 design ensures that IL is a negligible concern. Pendle’s AMM accounts for PT’s natural price appreciation by shifting the AMM curve to push PT price towards its underlying value as time passes, mitigating time-dependent IL (No IL at maturity).

On top of that, IL from swaps is also mitigated as both assets LP’ed are very highly correlated against one another (e.g. PT-stETH / SY-stETH). If liquidity is provided until maturity, an LP’s position will be equivalent to fully holding the underlying asset since PT essentially appreciates towards the underlying asset.

In most cases prior to maturity, PT trades within a yield range and does not fluctuate as much as an asset’s spot price. For example, it’s rational to assume that Aave’s USDC lending rate fluctuates between 0%-15% for a reasonable timeframe (and PT accordingly trades within that yield range). This premise ensures a low IL at any given time as PT price will not deviate too far from the time of liquidity provision.

### Customizable AMM

https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/AMM#customizable-amm

![Customizable AMM](https://docs.pendle.finance/assets/images/customizable_amm-b4da107e9ed6c28f3c125a8a40c4ecc3.png)

Pendle’s AMM curve can be customised to cater to tokens with varying yield volatilities. Yields are often cyclical in nature and typically swing between highs and lows. Typically, the floor and ceiling for the yield of a liquid asset are much easier to predict than its price.

For example, the annual yield of staked ETH is likely to fluctuate in a band of 0.5-7%. Knowing the rough yield range of an asset enables us to concentrate liquidity within that range, enabling much larger trade sizes at a lower slippage.

However, if the implied yield of the pool trades out of its set range, liquidity will be too thin to further push it in said direction. Using the above example, if the implied yield of the stETH pool goes beyond 7%, buying YT (or selling PT) might no longer be possible.

To check the set yield range of the pool, click on the sign as shown in the screenshot below.



## Order book

Pendle features an Order Book system alongside its AMM to enable peer-to-peer trading of PT and YT. Users can place limit orders to buy or sell at a specified implied APY.

Together, the Order Book and AMM enhance market liquidity, facilitating smoother trading on Pendle.

![Order Book](https://docs.pendle.finance/assets/images/order_book-abec17db6b23dd6552d333c1e00a5fe3.png)

## What is Limit Order

https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/OrderBook#what-is-limit-order

Limit order on Pendle is a purchase / sell order at a specified implied APY. You can set limit orders on PT and YT of supported assets on any chain.

Most popular market on Pendle has limit order support.

## Order Execution

https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/OrderBook#order-execution

A limit order will be executed if the implied APY of the AMM moves towards the order APY. At that moment, any further swaps (taker order) in said implied APY direction will fill the order book first, before proceeding to the AMM. In other words, a limit order deepens liquidity of the AMM at that specific implied APY as swaps will fill the order first before pushing the AMM’s implied APY again.

Swaps can be partially allocated to the AMM and limit orders (if any) to optimize for price-impact. That amount is determined at the most optimal amount, taking the AMM price impact and gas fees into account. Consequently, smaller orders face a lower likelihood of being filled due to the increased number of transactions required, leading to higher gas fees, particularly on chains with costly gas fees.

Orders can be:

- Active (Partially or fully fillable)
- Executed (Order is fully filled)
- Expired (Order is not fully filled by its expiry date)
- Cancelled
- Invalid

[Flash swap](https://docs.pendle.finance/ProtocolMechanics/AMM#flash-swaps) capability between PT and YT enhances the Order Book's flexibility by allowing a buy YT taker order to be matched with a buy PT limit order, and vice versa—a sell YT taker order can be matched with a sell PT limit order. This capability significantly broadens potential trading matches, streamlining transactions between PT and YT.

## Order Validity

https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/OrderBook#order-validity

Only the underlying yield-bearing asset can be used to place a limit order.

Partially Fillable order will be highlighted in a yellow warning. Orders will only be partially fillable when:

1. The balance of asset in your wallet falls below the order amount but not 0
2. The allowance set from your address is less than the order amount but not 0

Invalid orders will be highlighted in a red warning. Limit orders will be invalid when:

1. The balance of asset in your wallet falls to 0
2. The allowance set from your address is 0

Setting a limit order requires signature from your address while revoking the order involves a transaction to revoke the signature.

## Fees

[docs.pendle.finance/ProtocolMechanics/LiquidityEngines/OrderBook#fees](https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/OrderBook#fees)

Fees for swaps on limit order will be the same as if they were done on the AMM. Currently, maker order fee is set to be 0 (taker order fees remain the same). The team has full discretion on when to scale-up fees for maker order.

Fees collected will be distributed in $ETH to vePENDLE voters of its respective pools.

## Arbitrage

[https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/OrderBook#arbitrage](https://docs.pendle.finance/ProtocolMechanics/LiquidityEngines/OrderBook#arbitrage)

Pendle operates an arbitrage bot that continuously aligns prices between the AMM and the Order Book. This ensures any price discrepancies due to liquidity differences are quickly corrected, maintaining consistent pricing across the two system.

## Math

### PT <-> any token[](https://docs.pendle.finance/ProtocolMechanics/PendleMarketAPYCalculation#pt---any-token)

- underlyingunderlying: input/output token amount in terms of the underlying token
- ptAmountptAmount: PT input/output amount

$$
ptExchangeRate=ptAmount / underlying
$$



### YT <-> any token

https://docs.pendle.finance/ProtocolMechanics/PendleMarketAPYCalculation#yt---any-token

- ytAmountytAmount: YT input/output amount

ptExchangeRate=1 −underlyingytAmountptExchangeRate=1−ytAmountunderlying1

### PT <-> YT[]()

$$
ptExchangeRate=1+ptAmount / ytAmount
$$

https://docs.pendle.finance/ProtocolMechanics/PendleMarketAPYCalculation#pt---yt

From ptExchangeRateptExchangeRate you can calculate the effectiveImpliedApy as follow:

effectiveImpliedApy=ptExchangeRate365daysToExpiry−1effectiveImpliedApy=ptExchangeRatedaysToExpiry365−1