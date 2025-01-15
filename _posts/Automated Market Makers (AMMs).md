### Exploring the Different Formulas Used to Build Automated Market Makers (AMMs)

Automated Market Makers (AMMs) are a cornerstone of decentralized finance (DeFi), enabling seamless peer-to-peer trading without intermediaries. Unlike traditional order book-based exchanges, AMMs use mathematical formulas to determine the price of assets and facilitate liquidity. These formulas govern how users trade assets and earn rewards, making them the backbone of liquidity pools. This article delves into the most commonly used formulas in AMM design, their benefits, and their limitations.

------

### 1. **Constant Product Market Maker (CPMM)**

The **constant product formula** is the most popular AMM model, popularized by Uniswap and Bancor, the first AMM-based Dex. It uses the equation:
$$
x⋅y=k
$$
Here:

- `x` represents the quantity of one token in the pool.
- `y` represents the quantity of another token in the pool.
- `k` is a constant.

#### Graph

The result is a **hyperbola** where liquidity is always available but at increasingly higher prices, which approach infinity at both ends.

![https://cdn.prod.website-files.com/5f75fe1dce99248be5a892db/63989f611320ebd8802b8422_63752abf0dbac21f659e13db_quantity%2520of%2520assets.png](https://cdn.prod.website-files.com/5f75fe1dce99248be5a892db/63989f611320ebd8802b8422_63752abf0dbac21f659e13db_quantity%2520of%2520assets.png)

#### How It Works:

- Traders interact with the pool by adding or removing liquidity, causing `x` or `y` to adjust.
- The product of the two reserves (`k`) remains constant during a trade.
- Graph:  

#### Advantages:

- **Simplicity**: Easy to implement and understand.
- **Continuous Liquidity**: Always provides liquidity regardless of the pool size.
- **Price Discovery**: Adjusts prices based on supply and demand.

#### Limitations:

- **Price Impact**: Large trades result in significant slippage, making it unsuitable for high-volume trades.
- **Impermanent Loss**: Liquidity providers may suffer temporary losses compared to simply holding the assets.

#### Example 

Uniswap V2: https://uniswapv3book.com/milestone_0/constant-function-market-maker.html

------

### 2. **Constant Sum Market Maker** (CSMM)

The **constant sum formula** is expressed as:
$$
x+y=k
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
(x*y*z)^{⅓}=k
$$
. This allows for variable exposure to different assets in the pool and enables swaps between any of the pool’s assets.

See also[Chainlink - What Are Automated Market Makers (AMMs)?](https://chain.link/education-hub/what-is-an-automated-market-maker-amm)

#### How It Works:

- Balancer pools can hold more than two tokens and allocate custom weightings for each asset.
- Prices adjust based on the weighted reserves.

#### Advantages:

- **Diversified Liquidity**: Supports multiple assets in one pool.
- **Custom Weighting**: Liquidity providers can tailor pools to specific strategies.

#### Limitations:

- **Complexity**: Requires more sophisticated calculations.
- **Higher Gas Costs**: Computationally intensive, leading to increased transaction fees.

------

### 4. **StableSwap (Curve)**

Curve Finance introduced the **StableSwap** formula, optimized for assets with similar prices, such as stablecoins or wrapped tokens. Its formula combines constant sum and constant product mechanisms, ensuring minimal slippage.

[Curve](http://curve.fi/) AMMs combine both a CPMM and CSMM to offers  offers low-price-impact swaps between tokens that have a relatively stable 1:1 exchange rate

#### How It Works:

- At small price deviations, it behaves like a constant sum AMM, reducing slippage.
- For larger deviations, it transitions to a constant product AMM to maintain stability.

#### Advantages:

- **Low Slippage**: Ideal for stablecoin trading.
- **Efficient Liquidity Use**: Concentrates liquidity near the equilibrium price.

#### Limitations:

- **Specialized Use Case**: Not versatile for uncorrelated assets.
- **Complex Implementation**: Requires precise calibration.

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



## Summary tab

| **Formula Type**             | **Formula**                             | Graph           | **Best Use Case**                       | **Advantages**                                | **Limitations**                                         |
| ---------------------------- | --------------------------------------- | --------------- | --------------------------------------- | --------------------------------------------- | ------------------------------------------------------- |
| **Constant Product (CPMM)**  | x⋅y=k                                   | Hyperbole       | General-purpose, token swaps            | Simple, continuous liquidity, price discovery | High slippage for large trades, impermanent loss        |
| **Constant Sum**             | x+y=k                                   | Function affine | Stablecoin or tightly correlated assets | No slippage within the pool                   | Vulnerable to arbitrage, unsuitable for volatile assets |
| **Constant Mean (Balancer)** | See article                             |                 | Multi-token pools                       | Diversified liquidity, custom weighting       | Complex, higher gas fees                                |
| **StableSwap**               | Combination of constant sum and product | hyperbola       | Stablecoins, low-volatility pairs       | Low slippage, efficient liquidity             | Limited to specific asset types (e.g stablecoin)        |

------

### Conclusion

The choice of formula for an AMM depends on the specific use case and asset characteristics. While the constant product formula remains a foundational approach, innovations like StableSwap and custom weightings are paving the way for more specialized and efficient trading mechanisms. As DeFi evolves, we can expect further experimentation and hybridization of AMM models to cater to diverse needs.

By understanding the nuances of these formulas, developers and users alike can better navigate the dynamic world of decentralized trading.

## References

- [Dmitriy Berenzon - DeFi’s “Zero to One” Innovation](https://medium.com/bollinger-investment-group/constant-function-market-makers-defis-zero-to-one-innovation-968f77022159)
- [Chainlink - What Are Automated Market Makers (AMMs)?](https://chain.link/education-hub/what-is-an-automated-market-maker-amm)
- [BTX Capital - A Mathematical View of Automated Market Maker (AMM) Algorithms and Its Future](https://www.btx.capital/post/a-mathematical-view-of-automated-market-maker-amm-algorithms-and-its-future)