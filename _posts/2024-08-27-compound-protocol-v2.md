---
layout: post
title:  Compound V2 Overview
date:   2024-08-27
lang: en
locale: en-GB
categories: blockchain
tags: blockchain
description: This article presents the architecture and the behavior of Compound V2, a DeFi protocol on Ethereum for supplying or borrowing assets
image:  /assets/article/blockchain/defi/compound/compound-comp-logo.png
isMath: true
---

This article presents the architecture and the behavior of Compound V2, a DeFi protocol on Ethereum for supplying or borrowing assets. The content of this article is mainly taken up and annotated from the following resources:

- A  free [online course](https://www.youtube.com/playlist?list=PLE1Vu6ctbqa7Df5YJgMtH1xCcy0yX_dri) made by Cambell Harvey.
- Compound V2 Documentation: [docs.compound.finance/v2/](https://docs.compound.finance/v2/)
- [Compound whitepaper](https://compound.finance/documents/Compound.Whitepaper.pdf)
- [Compound GitHub](https://github.com/compound-finance/compound-protocol)
- [Understanding Compound protocol's interest rates](https://ianm.com/posts/2020-12-20-understanding-compound-protocols-interest-rates)
- [RareSkills - DeFi Lending: Liquidations and Collateral](https://www.rareskills.io/post/defi-liquidations-collateral)

[TOC]

## Introduction

This article present one of the first version of Compound: Compound V2.

This version has been replaced by Compound V3 (Comet) on [August 2022](https://thedefiant.io/news/defi/compound-v3-released).

Here the main points come from the [whitepaper](https://compound.finance/documents/Compound.Whitepaper.pdf)

Compound is a protocol initially based on the Ethereum blockchain that establishes **money markets**:

- Money markets  are pools of assets with algorithmically derived interest rates, based on the supply and demand for the asset. 

- Suppliers (and borrowers) of an asset interact directly with the protocol earning (and paying) a floating interest rate, without having to negotiate terms such as maturity, interest rate, or collateral with a peer or counterparty.
- Each money market is unique to an Ethereum asset such as Ether or an ERC-20 such as Dai.
- Unlike an exchange or peer-to-peer platform, where a user’s assets are matched and lent to another user, the Compound protocol aggregates the supply of each user; when a user supplies an asset, it becomes a [fungible resource](https://rya-sge.github.io/access-denied/2024/07/12/fungible-tokens-blockchains/). 
  - This approach offers significantly more liquidity than direct lending; 
  - unless every asset in a market is borrowed, users can withdraw their assets at any time, without waiting for a specific loan to mature.

- Assets supplied to a market are represented by an ERC-20 token balance (**cToken**), which entitles the owner to an increasing quantity of the underlying asset. As the money market accrues interest, which is a function of borrowing demand, cTokens become convertible into an increasing amount of the underlying asset. In this way, earning interest is as simple as holding a ERC-20 cToken.

- Market View for Tether

![alt text]({{site.url_complet}}/assets/article/blockchain/defi/compound/compound-tether.png)

### Difference between V2 and V3

Compound V3 has been deployed on [August 2022](https://thedefiant.io/news/defi/compound-v3-released)

Here the main resource is the [Compound Academy](https://compound.education/guides/view/compound-v2-vs-v3-compound/1).

- The most significant improvement was moving away from the **pooled-risk** model, which allowed users to borrow any asset but constantly rehypothecated collateral. This model was vulnerable to a single bad asset or oracle update draining all assets from the protocol.
- In Compound III, each market deployment offers a **single borrowable asset**, and the supplied collateral remains the property of the borrower, except during liquidation. This new approach increases capital efficiency and reduces risk since the collateral is more "useful" when the borrower knows the specific asset being borrowed in advance. 
- The first release of Compound III allows borrowing of USDC using ETH, WBTC, LINK, UNI, and COMP as collateral. Although borrowers will not earn interest on their collateral, they will be able to borrow more with lower risks of liquidation and penalties while spending less on gas fees.
- wETH market is also live now, with `Coinbase Wrapped Staked ETH(cbETH)` and `Lido Staked ETH(stETH)` as collateral.

| Compound II                                                  | Compound III                                                 |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Uses pools for assets with no separation                     | Each market has a base asset  and no assets are shared between the markets |
| There is a single deployment of the protocol contracts on a blockchain | Each market is a separate instance of new Comet contracts    |
| Risk Level of some hack draining all the funds is relatively high | Risk Level of some hack draining all the funds is relatively low as the markets are completely isolated |
| Lender earns interest on all the assets that lent to the protocol | Only the base asset earns interest, while all other assets in the market act as collateral |

Reference: [compound.education/guides - compound-v2-vs-v3-compound/4](https://compound.education/guides/view/compound-v2-vs-v3-compound/4)

------

## Overcollateralization

- Concept of credit rating can not be apply because Ethereum account are pseudonymous. It is impossible to enforce repayment in the event of a loan default
- As the result, all loans are overcollateralized in a collateral asset different from the one being borrowed.
- If a borrower falls belows their collateralization ratio (CR), their position is liquidated to pay back their debt.
- The debt can be liquidated by a **keeper**. The keeper received in return a bonus.



### Collateralization ratios and factors

- The CR is calculated via a collateral factor (CF)

- The collateral factor is the percentage of the collateral value that can be borrowed

- This CF is decided through a [gouvernance proposal](https://www.comp.xyz/t/historical-record-of-collateral-factors/1982)
- Each ERC-20 asset on the platform has its own collateral factor ranging from zero to 90
- A CR of zero means an asset cannot be used as collateral but it can still be borrowed
- The required CR for a single collateral type is calculated as 100 divided by the CR
- Volatile assets generally have lower collateral factors, which mandate higher CR due to increased risk of a price movement that could lead to undercollateralization
- An account can use multiple collateral types at once, in which case the CR is calculated as 100 divided by the weighted average of the collateral types by their relative sizes(denominated in a common currency) in the portfolio

See also [docs.compound.finance - collateral-factor](https://docs.compound.finance/v2/comptroller/#collateral-factor)

### CR as a reserve multiplier

- The CR is similar to a reserve multiplier in traditional banking, constraining the amount of "borrow" dollars that can be in the system relative to the "real" supply.
- For instance,there is occasionally more DAI in Compound than is actually supplied by MakerDAO, because users are borrowing and resupplying or selling to others who resupply.
- Importantly, all MakerDAO supply is ultimately backed by real collateral and there is no way to borrow more collateral value than has been supplied

Example 1:

- An investor deposits 100 DAI with a CR of 90
- This transaction alone correspond to a required CR of 111%.
- Assuming 1 DAI = $1, the investor can borrow up top $90 worth of any other asset in Compound

Example 2:

- If the user borrows the maximum, and the price of the borrowed asset increases at all, the position is subject to liquidation.

- Suppose the user also deposits two ETH with a CR of 60 and a price of $200/ETH.

- The total supply balance is now $500, with 80% being ETH and 20% being DAI. The required CR is

  
  $$
  \begin{aligned}[b]
  100/(0.8*60 + 0.2 * 90) = 151\%
  \end{aligned}
  $$
  

------

## Supply and borrow rates

- The supply and borrow interest rates are compounded every block (~12 seconds)
- There are determined by the utiliation percentage in the market
- Utilization rare is used as an input parameter to a formula that determines the interest rates
- The remaining parameters are set by Compound Governance

### Utilization rate

All interest rates in Compound are determined as a function of a metric known as the **utilization rate**. The utilization rate U_a for a money market a is defined as:
$$
\begin{aligned}[b]
U_a = Borrows_a / (Cash_a + Borrows_a - Reserves_a)
\end{aligned}
$$

- Borrows_a refers to the amount of a borrowed.
- Cash_a refers to the amount of *a* left in the system, available to be borrowed
- Reserves_a refers to the amount of *a* that Compound keeps as profit.

#### Code

See [compound-finance/compound-protocol - JumpRateModel.sol#L56C3-L62C8](https://github.com/compound-finance/compound-protocol/blob/a3214f67b73310d547e00fc578e8355911c9d376/contracts/JumpRateModel.sol#L56C3-L62C8)

```solidity
uint256 private constant BASE = 1e18; 
  /**
     * @notice Calculates the utilization rate of the market: `borrows / (cash + borrows - reserves)`
     * @param cash The amount of cash in the market
     * @param borrows The amount of borrows in the market
     * @param reserves The amount of reserves in the market (currently unused)
     * @return The utilization rate as a mantissa between [0, BASE]
     */
function utilizationRate(uint cash, uint borrows, uint reserves) public pure returns (uint) {
        // Utilization rate is 0 when there are no borrows
        if (borrows == 0) {
            return 0;
        }

        return borrows * BASE / (cash + borrows - reserves);
    }
```



#### Example

For example: given that reserves are 0,

- Alice supplies $500 [USDC](https://www.coingecko.com/en/coins/usd-coin)
- Bob supplies $500 USDC
- Charles borrows $100 USDC

Cash_a = 1000

Borrow = 100

We have cash_a = 900 and borrows_a = 100
$$
\begin{aligned}[b]
Ua = 100 / ( 900 + 100 - 0) = 100 / 1000 = 10%
\end{aligned}
$$


### Borrow rate formula

- It is an increasing linear function with a y-intercept known as the *base rate* that represents the borrow rate at 0% borrow demand and a *slope* representing the rate of change of the rates
- These parameters are different for each ERC-20 asset supported by the platforms
- Some market includes also a *kink*: 
  - a kink is a utilization ratio beyond which the [slope](https://ftp.worldpossible.org/endless/eos-rachel/RACHEL/RACHEL/modules/en-boundless-static/www.boundless.com/finance/definition/slope/index.html) steepens.
  - kink is The utilization point at which the jump multiplier is applied

- These formula can be used to reduce the cost of borrowing up to the *kink* and then increase the cost of borrowing after the *kink* to incentivize a minimum level of liquidity.



- Formula

$$
\begin{aligned}[b]
Borrow~interest~rate = utilization ~ratio * multiplierPerBlock + baseRatePerBlock
\end{aligned}
$$



#### Code

See [compound-finance - JumpRateModel.sol#L79](https://github.com/compound-finance/compound-protocol/blob/a3214f67b73310d547e00fc578e8355911c9d376/contracts/JumpRateModel.sol#L79)

```solidity
    /**
     * @notice Calculates the current borrow rate per block, with the error code expected by the market
     * @param cash The amount of cash in the market
     * @param borrows The amount of borrows in the market
     * @param reserves The amount of reserves in the market
     * @return The borrow rate percentage per block as a mantissa (scaled by BASE)
     */
    function getBorrowRate(uint cash, uint borrows, uint reserves) override public view returns (uint) {
        uint util = utilizationRate(cash, borrows, reserves);

        if (util <= kink) {
            return (util * multiplierPerBlock / BASE) + baseRatePerBlock;
        } else {
            uint normalRate = (kink * multiplierPerBlock / BASE) + baseRatePerBlock;
            uint excessUtil = util - kink;
            return (excessUtil * jumpMultiplierPerBlock/ BASE) + normalRate;
        }
    }
```



### Supply interest formula

$$
\begin{aligned}[b]
Supply ~ interest ~ rate = ( ~utilisation \ ~ratio~x~borrow ~ interest ~rate)
\end{aligned}
$$

- Reserve factor

  - The reserve factor defines the portion of borrower interest that is converted into [reserves](https://docs.compound.finance/v2/ctokens/#total-reserves).
  - this is % of the borrow payments not given to the suppliers and instead set aside in a reserve pool that acts as insurance in that case of a borrower defaults.
  - This reserve can be withdrawn or transferred through the protocol’s governance.

  - See https://docs.compound.finance/v2/ctokens/#total-reserves

- In an extreme price movement, many positions may become undercollateralized in that they have insufficient funds to repay the suppliers. In the event of such a scenario, the suppliers would be repaid using the assets in the reserve pool

#### Code

```solidity
    /**
     * @notice Calculates the current supply rate per block
     * @param cash The amount of cash in the market
     * @param borrows The amount of borrows in the market
     * @param reserves The amount of reserves in the market
     * @param reserveFactorMantissa The current reserve factor for the market
     * @return The supply rate percentage per block as a mantissa (scaled by BASE)
     */
    function getSupplyRate(uint cash, uint borrows, uint reserves, uint reserveFactorMantissa) override public view returns (uint) {
        uint oneMinusReserveFactor = BASE - reserveFactorMantissa;
        uint borrowRate = getBorrowRate(cash, borrows, reserves);
        uint rateToPool = borrowRate * oneMinusReserveFactor / BASE;
        return utilizationRate(cash, borrows, reserves) * rateToPool / BASE;
    }
```



#### Example 1

In the DAI market, 100 million is supplied and 50 millions is borrowed.

- Base rate = 1%

- Slope = 10%

At 50 million borrowed, utilization is 50%

$$
\begin{aligned}[b]
borrow~ interest~ rate =  utilization * Slope + base ~rate ???
.\end{aligned}
$$

$$
\begin{aligned}[b]
borrow~ interest~ rate =  0.5 * 0.1 + 0.01 = 0.06 = 6\%
.\end{aligned}
$$

maximum supply rate wtih a reserve factor of zero:

$$
\begin{aligned}[b]
maximum~supply ~rate = utilization~ ratio * borrow~ interest ~rate
.\end{aligned}
$$

$$
0.5 * 0.06 = 0.03 ~or~ 3\%
$$



#### Example 2

- The borrow rate is not a marginal rate, it is a rate for all borrowers
- If an initial borrower does $25 millions. The rate would be .25*0.1 + 0.01 = 3.5%.
- Then suppose another borrower enters the market with another $25 million loan
- The rate increases to 6% for all borrowers

#### Example 3 - Reserve Factor

- If the reserve factor is set to 10, then 10% of the borrow interest is diverted to a DAI reserve pool, lowering the supply interest rate to 2.7%

$$
\begin{aligned}[b]
0.5 * 0.06 * (1-0.10) = 0.027
.\end{aligned}
$$

| Label                      | Value            |
| -------------------------- | ---------------- |
| Borrow  rate               | = 6%             |
| Total interest             | = .06 * 50m = 3m |
| Reserve .1 x 3m            | = .3m            |
| Distributions to suppliers | = 2.7 m          |



- 6% of borrow interest of 50 million is equal to 3 million of borrow payment
- Distributing 3 millions of payments to 100 millions of suppliers implies a 3% interest rate to all suppliers. 
- Withh 10% diverted to the reserve (300,000), then there is only 2.7 millions of payments to the suppliers

#### Example 4 -  Kink

- The base rate remains at 1%
- The borrow interest rate

$$
\begin{aligned}[b]
0.01 (base) + 0.8 * 0.1 (pre-kink) + 0.1 * 0.4 (post-kink) = 13\%
\end{aligned}
$$

- The supplay rate (assuming a reserve factor of zero) is

$$
\begin{aligned}[b]
0.9 * 0.13 = 11.7\%
\end{aligned}
$$



### Advantage of Compound

- Unlock value of asset without selling it, like a *home equity line of credit *(HELOC)
- Easily engineer levered long or short positions
- Suppose you are bearing on price of ETH
  - Deposit stablecoin like USDC or DAI
  - Borrow ETH
  - Sell ETH for stablecoin
  - If price of ETH falls, you can use your stablecoin to buy (cheap) ETH to pay of debt

------

## cTokens

- The compound protocol must escrow tokens as a depositor in order to mainthan that liquidity for the platform itself and to keep track of each person's ownership stake in each market
- A naive approach woul be to keep track of the number inside a contract
- A better approach would be to tokenize the user's share
- Compound does this using a **cToken**, and this one of the platform's important innovations

### Burn and mint

cTokens are minted and burned

- Compound's cToken is an ERC-20 in its own right that represents an ownership stake in the underlying Compound market

- For example, 
  - `cDAI` corresponds to the Compound DAI market 
  - `cETH` corresponds to the Compound ETH market
- Both tokens are minted and burned in proportion to the funds added and removed from the underlying market as a means to track the amount belonging to a specific investor

### cTokens can be traded

- Given interest payments continually accrue to suppliers, these toeksn are always worth more than the underlying asset
- cTokens can be traded on their own like a normal ERC-20 assets
- Other protocols can seamlessly integrate with Compound simply by holding cTokens and allows users to deploy their cTokens directly into other opportunities, such as using a cToken as collateral for MakerDAO vault
- Instead of using ETH only as collateral, an investor can use cETH and lending interest on the ETH collateral

#### Example 1

There are 2,000 DAI in the Compound DAI market a total 500 cDAI respresents the ownership in the market; this ratio of cDAI is not determinative *and could just as easily be 500,000 cDAI*

1 cDAI = 2,000 / 500 = 4 DAI

If a trader comes in and deposits 1,000 DAI to a supply of 3'000, the supply increasey by 50% and Compound mints 50% in more which correspond to 250 cDAI (1000 / 4 = 250 cDAI)

#### Example 2

Currently, 1 cDAI = 4 DAI, but after interest accrues the ratio will change. 

Let interest = 10%, at year end, 3_300 DAI because 3_000 * 10% = 300

Trader redeems then 250 cDAI for 1_100 DAI.

Trader redeems 250 cDAI for 1,100 DAI

#### Remark

- The trader can also deploy cDAI in the play of DAI so the DAI is not sitting idle but earning interest via the COmpound pool.
- For example, the trader could deploy cDAI as the necessary collateral to open a perpetual futures position on DYdX or she could market male on Uniswap using a cDAI trading pair

------

## Governance parameters

- The many differents parameters of Compound's functioanality, such as the collateral factor, reseve factor, base rate, slope and kink, can all be tuned
- The entity capable of tuning these paramters is Compound governance
- Compound governance has the power to change parameters, add new markets, freeze the ability to initiate new deposits or borrow in a market, and event upgrade some of the contract code itself

### Governance

- Importantly, Compound governance cannot steal funds or prevent users from withdrawing. However, they can manage funds inside the reserve according to the documentation
- In the early stages of Compound's growth, governance was controlled by developer admins, similar to any tech startup
- Technically, this meant that the first version of Compound was not fully decentralized

### Governance parameter

- A strong development goal of Compound, as with most DeFi protocols, was to remove developer admin access and release the protocol to the leadership of a DAO via a governance token
- The token allowed shareholdrs and community members to collectively become Compound Governance and propose upgrade or parameter tuning
- A quorum agreement is required for any change to be implemented
- The quorum rule is a majority of users each of whom holds with a minimum of 400_000 COMP(4% of total eventual supply)

#### Code

See [github.com/compound-finance - contracts/Governance/GovernorAlpha.sol#L8](https://github.com/compound-finance/compound-protocol/blob/a3214f67b73310d547e00fc578e8355911c9d376/contracts/Governance/GovernorAlpha.sol#L8)

```solidity
 /// @notice The number of votes in support of a proposal required in order for a quorum to be reached and for a vote to succeed
    function quorumVotes() public pure returns (uint) { return 400000e18; } // 400,000 = 4% of Comp
```



### COMP token

- Compound implemented this new governance system in MAY 2020 via the COMP token
- COMP is used to vote on protocol updates, such a parameter tuning, adding new asset support, and functionality upgrade (similar to MKR for MakerDAO)
- On June 15, 2020, the 7th governance proposal passed which provider for distribution COMP tokens to users of the plateform based on the borrow volume per market.
  - The COMP token is distributed to both suppliers and borrowers, and acts as a subsidization of rates.

------

## Liquidation

If the value of an account’s borrowing outstanding exceeds their borrowing capacity, a portion of the outstanding borrowing may be repaid in exchange for the user’s cToken collateral, at the current market price minus a liquidation discount ;

-  this incentives an ecosystem of arbitrageurs to quickly step in to reduce the borrower’s exposure, and eliminate the protocol’s risk. 
- The proportion eligible to be closed, a close factor , is the portion of the borrowed asset that can be repaid, and ranges from 0 to 1, such as 25%. 
- The liquidation process may continue to be called until the user’s borrowing is less than their borrowing capacity. 
- Any Ethereum address that possesses the borrowed asset may invoke the liquidation function, exchanging their asset for the borrower’s cToken collateral. 
- As both users, both assets, and prices are all contained within the Compound protocol, liquidation is frictionless and does not rely on any outside systems or order-books.

#### Code

From [github.com/compound-finance - CToken.sol#L721](https://github.com/compound-finance/compound-protocol/blob/a3214f67b73310d547e00fc578e8355911c9d376/contracts/CToken.sol#L721)

```solidity
/**
     * @notice The liquidator liquidates the borrowers collateral.
     *  The collateral seized is transferred to the liquidator.
     * @param borrower The borrower of this cToken to be liquidated
     * @param liquidator The address repaying the borrow and seizing collateral
     * @param cTokenCollateral The market in which to seize collateral from the borrower
     * @param repayAmount The amount of the underlying borrowed asset to repay
     */
    function liquidateBorrowFresh(address liquidator, address borrower, uint repayAmount, CTokenInterface cTokenCollateral) internal {
        //Fail if liquidate not allowed
        uint allowed = comptroller.liquidateBorrowAllowed(address(this), address(cTokenCollateral), liquidator, borrower, repayAmount);
        if (allowed != 0) {
            revert LiquidateComptrollerRejection(allowed);
        }

        // Verify market's block number equals current block number **/
        if (accrualBlockNumber != getBlockNumber()) {
            revert LiquidateFreshnessCheck();
        }

        //Verify cTokenCollateral market's block number equals current block number
        if (cTokenCollateral.accrualBlockNumber() != getBlockNumber()) {
            revert LiquidateCollateralFreshnessCheck();
        }

        // Fail if borrower = liquidator 
        if (borrower == liquidator) {
            revert LiquidateLiquidatorIsBorrower();
        }

        // Fail if repayAmount = 0 
        if (repayAmount == 0) {
            revert LiquidateCloseAmountIsZero();
        }

        // Fail if repayAmount = -1 
        if (repayAmount == type(uint).max) {
            revert LiquidateCloseAmountIsUintMax();
        }

        // Fail if repayBorrow fails ^
        uint actualRepayAmount = repayBorrowFresh(liquidator, borrower, repayAmount);

        /////////////////////////
        // EFFECTS & INTERACTIONS
        // (No safe failures beyond this point)

....
(rest of the functions available on Compound GitHub)
```



------

## Overview

### Other platform use Compound

- The Compound protocol can no longer be truned off and will exist on Ethereum as long as Ethereum exists
- Other platforms can easily escrow funds in Compound to provide additional value to their users or enable novel business models
- Easy, instant access to yield or borrow liquidity on different Ethereum tokens makes Compound an import platform in DeFi.

### Compound VS traditional finance

**Centralized control**

- Traditional finance problem: Borrowing and lending  are are controlled by institutions

- Compound solution: Compound rates are determined algorithmically and gives control of market paramters to COMP stakeholders incentivized to provide value to users

**Limited access**

- Traditional finance problem: Difficulty in accessing high-yield USD investment opportunities or competitive borrowing
- Compound solution: Open ability to borrow or lend any supported assets at competitive algorithmically determined rate (temporally subsidized by COMP distribution)

**Inefficiency**

- Traditional finance problem: Suboptimal rates for borrowing and lending due to inflated costs
- Compound solution: Algorithmically pooled and optimized interest rates

**Lack of Interoperability**

- Cannot repurpose supplied positions for other investment opportunities
- Compound solution: tokenized positions via cTokens can be used to turn static assets into yield-generating assets

**Opacity**

Traditional finance problem: under collateralization of lending institutions

Compound solution: Transparent collateralization ratios of borrowers visible to entire ecosystem

------

## Screenshot

From August 26, 2024

- Dashboard view

![alt text]({{site.url_complet}}/assets/article/blockchain/defi/compound/compound-dashboard-view.png)



![alt text]({{site.url_complet}}/assets/article/blockchain/defi/compound/compound-tether.png)

- Collateral factor is 0% meaning this is not possible to use tether as a collateral
- There are $2.26 Millions set in the reserved!!!!

![alt text]({{site.url_complet}}/assets/article/blockchain/defi/compound/compound-ether.png)

- The CR is high (82.5%) indicated that Ether is considered as a safe asset



![alt text]({{site.url_complet}}/assets/article/blockchain/defi/compound/compound-yearn.png)



- The CR is pretty low, only 20% meaning that this asset is considered as more volatile
