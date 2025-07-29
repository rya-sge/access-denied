---
layout: post
title: Automated Market Makers (AMMs) - Overview
date: 2025-07-29
lang: en
locale: en-GB
categories: defi blockchain ethereum
tags: automated-market-maker amm defi
description: Automated Market Makers (AMMs) are an essential piece of decentralized finance (DeFi). This article delves into the most commonly used formulas in AMM design, their benefits, and their limitations.
image: /assets/article/blockchain/defi/curve/curve-formula.png
isMath: true
---

Automated Market Makers (AMMs) are an essential piece of decentralized finance (DeFi), enabling to swap crypto assets without intermediaries. 

Unlike traditional order book-based exchanges, AMMs use mathematical formulas to determine the price of assets and facilitate liquidity. These formulas govern how users trade assets and earn rewards, making them the backbone of liquidity pools. 

This article delves into the most commonly used formulas in AMM design, their benefits, and their limitations.

## Brief history

The original AMMs based on `constant product market makers`were envisioned in 2017 by Ethereum founder Vitalik Buterin on a [reddit post](https://www.reddit.com/r/ethereum/comments/55m04x/lets_run_onchain_decentralized_exchanges_the_way/) to reduce the high spread (often 10% or even higher) during a trade on the plaform available at that moment (MKR market, etherdelta). 

The spreads were high because market making is very expensive, as creating an order and removing an order both take gas fees, even if the orders are never "finalized". 

State channel-based solutions could theoretically resolve this, but are far from being implemented in 2017. Vitalik proposed to use instead a style of "on-chain automated market maker" 

Its proposition was based  on concepts already used in prediction markets and also a first proposable by [Nick Johnson's proposal here](https://www.reddit.com/r/ethereum/comments/54l32y/euler_the_simplest_exchange_and_currency/)

After that, the first [**xy=k liquidity pool**](https://blog.bancor.network/gnosis-bancor-partner-on-the-first-ever-token-changer-gnobnt-63fb14b65653) was deployed by Bancor in 2017 with **BNT and GNO**. See also this [video](https://www.youtube.com/watch?v=ySeir-M2nj0) by Bancor dated from March 2017.

Reference: [Jennifer Albert - A historical account with Dr. Mark Richardson, Bancor Project Lead ](https://www.linkedin.com/pulse/how-bancor-revolutionized-defi-first-constant-product-jennifer-albert-p9d0c/)

------

### 1. **Constant Product Market Maker (CPMM)**

The **constant product formula** is the most popular AMM model, popularized by Uniswap and Bancor, the first AMM-based Dex. 

The equation implemented and used by Uniswap V2 is the following:
$$
\begin{aligned}
x⋅y=k
\end{aligned}
$$
Here:

- `x` represents the quantity of one token in the pool.
- `y` represents the quantity of another token in the pool.
- `k` is a constant.

### Price

With this formula, tokens (`x`, `y`) are priced in terms of each other. 

For example: in a ETH/USDC pool, ETH is priced in terms of USDC, and USDC is priced in terms of ETH. 

If 1 ETH costs 1000 USDC, then 1 USDC costs 0.001 ETH. 

The prices of tokens in a pool are determined by the supply of the tokens, that is by **the amounts of reserves of the tokens** that the pool is holding. Token prices are simply relations of reserves:
$$
\begin{aligned}
P_x = y/x
\end{aligned}
$$

$$
\begin{aligned}
P_y = x/y
\end{aligned}
$$

Where `Px` and  `Px`are prices of tokens in terms of the other token

#### Graph

The result is a **hyperbola** where liquidity is always available but at increasingly higher prices, which approach infinity at both ends.

![uniswap-amm]({{site.url_complet}}/assets/article/blockchain/defi/uniswap/uniswap-amm.png)

Reference image: [Dmitriy Berenzon - DeFi’s “Zero to One” Innovation](https://medium.com/bollinger-investment-group/constant-function-market-makers-defis-zero-to-one-innovation-968f77022159)

See also [Uniswap - How Uniswap works](https://docs.uniswap.org/contracts/v2/concepts/protocol-overview/how-uniswap-works)

#### How It Works:

- Traders interact with the pool by adding or removing liquidity, causing `x` or `y` to adjust.
- The product of the two reserves (`k`) remains constant during a trade.

#### Advantages:

- **Simplicity**: Easy to implement and understand.
- **Continuous Liquidity**: Always provides liquidity regardless of the pool size.
- **Price Discovery**: Adjusts prices based on supply and demand.

#### Limitations:

- **Price Impact**: Large trades result in significant slippage, making it unsuitable for high-volume trades.
- **Impermanent Loss**: Liquidity providers may suffer temporary losses compared to simply holding the assets.



## Implementation

Here the implementation from Uniswap V2, function [swap](https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Pair.sol#L182)

```solidity
 require(balance0Adjusted.mul(balance1Adjusted) >= uint(_reserve0).mul(_reserve1).mul(1000**2), 'UniswapV2: K');
```

There are four variables inside the `require` statement:

- `balance0Adjusted`: Reserves of **x** after the trader sends tokensX to the pool minus 0.3% of the amount sent.
- `balance1Adjusted`: Reserves of **y** after the tokensY are sent to the trader from the pool.
- `_reserve0`: Reserves of token `x` prior to the swap.
- `_reserve1`: Reserves of token `y `prior to the swap.



The simplify version gives the following formula:
$$
balance0Adjusted * balance1Adjusted >= \_reserve0 * \_reserve1
$$
In equation, it gives:


$$
\begin{aligned}
x * y = k
\end{aligned}
$$

$$
\begin{aligned}
x' * y' = k
\end{aligned}
$$

$$
\begin{aligned}
x * y = x' * y'
\end{aligned}
$$



Where

- `x` is `reserve0` and  `x'`  is  `balance0Adjusted`
- `y`is `reserve1`and `y'`is `balance1Adjusted`



The smart contract stores also the `k`value in the public variable [KLast](https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Pair.sol#L28)

See also [Uniswap V2 in Depth](https://medium.com/better-programming/uniswap-v2-in-depth-98075c826254)

#### Resources:

- [Constant Function Market Makers](https://uniswapv3book.com/milestone_0/constant-function-market-maker.html#constant-function-market-makers)
- [Uniswap Whitepaper](https://app.uniswap.org/whitepaper.pdf)
- [Uniswap V2 - How Uniswap works](https://docs.uniswap.org/contracts/v2/concepts/protocol-overview/how-uniswap-works)
- [Chaisomsri - [DeFi Math] About Uniswap V2 Lazy Liquidity](https://medium.com/@chaisomsri96/defi-math-about-uniswap-v2-lazy-liquidity-d73f9ef9d6e7)
- [Kirill Naumov - Back to the Basics: Uniswap, Balancer, Curve](https://medium.com/@kinaumov/back-to-the-basics-uniswap-balancer-curve-e930c3ad9046)

### Bancor - Smart token

Smart tokens are standard ERC20 tokens which implements the Bancor Protocol.

A smart token holds a balance of least one other reserve token, which can be a different smart token, any ERC20 standard token or Ether.

Smart tokens are issued when purchased and destroyed when liquidiation

Bancor uses the term of CRR to design K: `Constant Reserve Ratio`.

This constant was set by the smart token creator, for each reserve token and uses in price calcalation.
$$
Price = Balance / Supply * CRR
$$

- When smarts token are purchased, the payment is added to the reserve balance.

Based on the calculation price, new smart tokens are issued to the buyed.

- When smart token are liquidates, they are removed from the supply (destroed).

Based on the current price, reserve tokens are transfereed to the liquidator.

See [Bancor whitepaper](https://www.securities.io/bancor-whitepaper/)

------

### 2. **Constant Sum Market Maker** (CSMM)

The **constant sum formula** is expressed as:
$$
\begin{aligned}
x + y = k
\end{aligned}
$$
This model is less common but ensures no slippage for trades until the pool is depleted.

#### Graph

The result graph is a function affine, which means that this model does not provide infinite liquidity.

#### How It Works:

- Traders exchange assets without altering the reserves' proportions drastically.

#### Advantages:

- **No Slippage**: Ideal for stablecoins or assets with tightly correlated values.
- **Arbitrage-Friendly**: Maintains prices close to the market.

#### Limitations:

- **Vulnerability to Arbitrage**: Can be drained easily if asset prices deviate significantly.
- **Limited Use Cases**: Not suitable for volatile or uncorrelated assets.

See also:[Wikipedia - Constant function market maker](https://en.wikipedia.org/wiki/Constant_function_market_maker)

------

### 3. **Constant Mean Market Maker (CMMM / Balancer)**

Balancer pools generalize the constant product formula by allowing multiple assets with custom weightings. The formula is:
$$
\prod_{i=1}^{n} r_i^{w_i} = k
$$
Here:

- `ri`  is the reserve of the i-th asset.
- `wi` is the weight of the i-th asset.

Example:

For a liquidity pool with three assets, the equation would be the following
$$
\begin{aligned}
(x*y*z)^{⅓} = k
\end{aligned}
$$
. This allows for variable exposure to different assets in the pool and enables swaps between any of the pool’s assets.

See also [Chainlink - What Are Automated Market Makers (AMMs)?](https://chain.link/education-hub/what-is-an-automated-market-maker-amm)

#### How It Works:

- Balancer pools can hold more than two tokens and allocate custom weightings for each asset.
- Prices adjust based on the weighted reserves.

#### Advantages:

- **Diversified Liquidity**: Supports multiple assets in one pool.
- **Custom Weighting**: Liquidity providers can tailor pools to specific strategies.

#### Limitations:

- **Complexity**: Requires more sophisticated calculations.
- **Higher Gas Costs**: Computationally intensive, leading to increased transaction fees.



### 4. **StableSwap (Curve)**

[StableSwap whitepaper](https://docs.curve.fi/assets/pdf/stableswap-paper.pdf)

Curve Finance introduced the **StableSwap** formula, optimized for assets with similar prices, such as stablecoins or wrapped tokens. Its formula combines constant sum and constant product mechanisms, ensuring minimal slippage.

[Curve](http://curve.fi/) AMMs combine both a CPMM and CSMM to offers  offers low-price-impact swaps between tokens that have a relatively stable 1:1 exchange rate

#### How It Works

- At small price deviations, it behaves like a constant sum AMM, reducing slippage.
- For larger deviations, it transitions to a constant product AMM to maintain stability.

#### Pros/Cons

##### Advantages

- **Low Slippage**: Ideal for stablecoin trading.
- **Efficient Liquidity Use**: Concentrates liquidity near the equilibrium price.

##### Limitations

- **Specialized Use Case**: Not versatile for uncorrelated assets.
- **Complex Implementation**: Requires precise calibration.

#### Details

 The **constant D** represents the total amount of coins in the pool when their prices are equal. To minimize price slippage, an "amplified" invariant should have low curvature, leading to smaller price changes. A "zero slippage" invariant corresponds to infinite leverage, but it’s essentially a constant-price or constant-sum invariant. On the other hand, a constant-product invariant corresponds to zero leverage.

To find a balance between these two extremes, the proposed solution introduces a dimensionless **leverage parameter (χ)**. By adjusting χ, the invariant can smoothly transition between a constant-product invariant (when χ = 0) and a constant-sum invariant (when χ = ∞). To ensure consistency, the constant-sum invariant is multiplied by χDn−1, where D represents the total value of coins in the pool and n is the number of coins. This results in an invariant that incorporates both characteristics and allows for flexible adjustment of leverage.

![curve-formula]({{site.url_complet}}/assets/article/blockchain/defi/curve/curve-formula.png)

#### Graph

Graphs are from the StableSwap whitepaper

 Comparison of StableSwap invariant with Uniswap (constant-product) and constant price invariants. The portfolio consists of coins X and Y which have the “ideal” price of 1.0. There are x = 5 and y = 5 coins loaded up initially. As x decreases, y increases, and the price is the derivative dy/dx.

![curve-graph]({{site.url_complet}}/assets/article/blockchain/defi/curve/curve-graph.png)

The price slippage (Fig. 2) is much smaller, if compared to constant-product invariant. The StableSwap invariant has an “amplification coefficient” parameter: the lower it is, the closer the invariant is to the constant product. When calculating slippage, we use a practical value of A = 100. This is somewhat comparable to using Uniswap with 100x leverage.

Price slippage: Uniswap invariant (dashed line) vs Stableswap (solid line)

![curve-price-slippage]({{site.url_complet}}/assets/article/blockchain/defi/curve/curve-price-slippage.png)

------

### 5. **Hybrid Models**

Several AMMs, like **Bancor** and **Kyber Network**, use hybrid formulas that combine elements of the above models or introduce innovative mechanisms. These include:

- **Dynamic Fees**: Adjusting fees based on market conditions.
- **Concentrated Liquidity**: Allowing liquidity providers to specify price ranges for their funds (e.g., Uniswap v3).

#### Advantages:

- **Flexibility**: Adapts to various market conditions.
- **Efficiency**: Optimizes liquidity distribution.

#### Limitations:

- **High Complexity**: May be challenging to understand and implement.
- **Technical Risks**: Increased likelihood of bugs or vulnerabilities.



**Hybrid Constant Function Market Maker (HCFMM)** is mentioned in a [KPMG report](https://assets.kpmg.com/content/dam/kpmg/cn/pdf/en/2021/10/crypto-insights-part-2-decentralised-exchanges-and-automated-market-makers.pdf), but I haven't really found any further explanation



## Summary tab

Here is a summary of the different formula

| **Formula Type**            | Apps            | **Formula**                             | Graph           | **Best Use Case**                       | **Advantages**                                | **Limitations**                                         |
| --------------------------- | --------------- | --------------------------------------- | --------------- | --------------------------------------- | --------------------------------------------- | ------------------------------------------------------- |
| **Constant Product (CPMM)** | Uniswap, bancor | x⋅y=k                                   | Hyperbole       | General-purpose, token swaps            | Simple, continuous liquidity, price discovery | High slippage for large trades, impermanent loss        |
| **Constant Sum**            |                 | x+y=k                                   | Function affine | Stablecoin or tightly correlated assets | No slippage within the pool                   | Vulnerable to arbitrage, unsuitable for volatile assets |
| **Constant Mean **          | Balancer        | See article                             |                 | Multi-token pools                       | Diversified liquidity, custom weighting       | Complex, higher gas fees                                |
| **StableSwap**              |                 | Combination of constant sum and product | hyperbola       | Stablecoins, low-volatility pairs       | Low slippage, efficient liquidity             | Limited to specific asset types (e.g stablecoin)        |

------

### Conclusion

The choice of formula for an AMM depends on the specific use case and asset characteristics. While the constant product formula remains a foundational approach, innovations like StableSwap and custom weightings are paving the way for more specialized and efficient trading mechanisms. As DeFi evolves, we can expect further experimentation and hybridization of AMM models to cater to diverse needs.

By understanding the nuances of these formulas, developers and users alike can better navigate the dynamic world of decentralized trading.

## References

- [Dmitriy Berenzon - DeFi’s “Zero to One” Innovation](https://medium.com/bollinger-investment-group/constant-function-market-makers-defis-zero-to-one-innovation-968f77022159)
- [Chainlink - What Are Automated Market Makers (AMMs)?](https://chain.link/education-hub/what-is-an-automated-market-maker-amm)
- [BTX Capital - A Mathematical View of Automated Market Maker (AMM) Algorithms and Its Future](https://www.btx.capital/post/a-mathematical-view-of-automated-market-maker-amm-algorithms-and-its-future)