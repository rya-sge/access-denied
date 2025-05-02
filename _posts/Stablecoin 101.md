# Stablecoin 101

**Second Lecture: Lending with Stablecoins**

In today's second lecture, we will touch on lending with stablecoins. Now, while we won't go too deep into the technicalities of stablecoins themselves—since, as Dan mentioned on Monday, we could easily spend an entire week on them—I will try to condense as much information as possible into this session.

[TOC]

## Why Take on Debt in the First Place?

Let’s begin with a simple question: why would anyone lend or borrow in the first place? At the core, lending and borrowing serve as mechanisms to access capital without necessarily exposing oneself to the fluctuations or the "price discovery" of the assets involved.

When you take out a loan, you might not want to speculate on the collateral's price. You may just want liquidity upfront to focus on your business or product without worrying about market movements. This is similar to the concept of taking on debt to enable growth, as is seen in traditional economics.

For example, imagine a young entrepreneur who wants to purchase a turntable but lacks the upfront capital. Instead of waiting, they could borrow money to make the purchase, allowing them to start producing music right away. This simple process of borrowing to produce something is a fundamental economic tool, and it works much the same way in the blockchain world.

There is a fascinating 30-minute YouTube video by Ray Dalio, which explains the concept of economic cycles in detail. Dalio, known for his work at Bridgewater Associates, breaks down the relationship between productivity growth, short-term debt cycles, and long-term debt cycles. It’s a great resource if you're interested in understanding how debt functions in broader economic systems.

## On-Chain Lending

In the world of decentralized finance (DeFi), lending is facilitated through smart contracts. These contracts often create "vaults"—essentially pools of assets—where users can deposit collateral like Ether (ETH) or DAI.

There are three key players in this system:

1. **The Lender:** Provides capital (collateral) to the system and receives interest on their deposit.
2. **The Borrower:** Collateralizes assets and takes out a loan.
3. **Liquidators:** Third-party entities that intervene if the value of collateral falls too low, to ensure the stability of the system.

To facilitate the process, the blockchain uses oracles—external services that feed price data into the smart contracts. These prices are crucial to understanding the value of collateral and ensuring that positions are healthy (i.e., not under-collateralized).

### Example Platforms and Terminology

Let’s take Aave as an example. Aave and similar platforms are examples of decentralized lending platforms, where users can deposit or borrow various assets. You'll often see metrics such as the **annual percentage yield (APY)**, which indicates the interest rate you either earn (as a lender) or pay (as a borrower).

In these platforms, you can also leverage your assets, but we won’t delve deeply into that today. One fascinating area that I suggest you explore is **AMMs (Automated Market Makers)** for stablecoins, such as Curve. These platforms allow for stable asset exchanges with a bond curve that looks quite different from the standard AMM curves you might be used to.

### Key Terminology

Let's go over some important terminology in lending and borrowing:

1. **Collateral:** The asset you pledge as security for a loan.
2. **Over-Collateralization:** This occurs when the value of the collateral exceeds the loan amount. In DeFi, this is common.
3. **Under-Collateralization:** When the value of the collateral is less than the loan value. This is riskier and typically not seen in decentralized lending without additional safeguards.
4. **Liquidation:** This happens if the value of your collateral falls below a certain threshold, and a third party steps in to purchase your collateral at a discount.
5. **Health Factor:** This represents the ratio between the value of your collateral and the debt. A healthy position has a health factor above 1. If it drops below 1, your position may be liquidated.

### Example of Health Factor and Liquidation

Let’s consider an example: Imagine you collateralize 1 ETH when ETH is valued at 2000 DAI. This gives you borrowing capacity, say, 1500 DAI. However, if the value of ETH decreases, your health factor declines. If it falls below 1, your position is up for liquidation.

To avoid liquidation, you might choose to borrow less than your full capacity (e.g., 1250 DAI instead of 1500 DAI), ensuring you have a buffer to absorb any market fluctuations. If ETH’s price falls from 2000 DAI to 1600 DAI, your borrowing capacity will also decrease, and you will be at risk of liquidation unless you take action.

### Liquidation Mechanism

The liquidation mechanism ensures that the protocol remains solvent. Liquidators—external entities—are incentivized to buy up collateral at a discount. This liquidation spread is typically between 5-15%, depending on the platform. These liquidations can happen quickly and automatically if a position falls below its liquidation threshold.

In traditional finance, liquidation can be a much more complicated process, but in DeFi, the blockchain facilitates a more seamless and instantaneous process. This helps prevent the kind of drawn-out proceedings that can occur in traditional finance, where liquidating an asset like a house (collateral for a mortgage) can take months.

### Traditional Finance vs. DeFi Liquidations

Liquidation, as a concept, is not new—it exists in traditional finance as well. In traditional finance, collateral for loans might be your house, while in DeFi, it could be an asset like Ether. The liquidation process in both domains serves to maintain financial stability by ensuring the borrower’s debt doesn’t surpass the value of their collateral.

In DeFi, however, the process is much faster. If an asset price drops, liquidators can purchase the collateral at a discount. This is where DeFi and traditional finance differ. While the process might be similar in concept, the speed and the mechanisms at play in DeFi make it an exciting (and volatile) environment for both borrowers and lenders.

### Price Manipulation and Liquidations

One interesting aspect of DeFi liquidation is the potential for **price manipulation**. Since the liquidation price is determined by oracles, there have been instances of manipulation, especially in AMMs. To combat this, decentralized platforms use **time-weighted average price (TWAP) oracles** that calculate price averages over several blocks to reduce the risk of manipulation. However, this is still an evolving area of research.

### Conclusion

Understanding lending and borrowing in DeFi is critical as these systems continue to evolve. The interplay between collateralization, liquidation, and health factors creates a dynamic environment where borrowers, lenders, and liquidators all have important roles to play. 

Whether you’re looking to speculate, hedge, or just gain access to liquidity, the concepts of debt and collateralization are foundational to the economic models that underpin DeFi platforms.