# USDe Overview

Ethena enables the creation and redemption of a delta-neutral synthetic dollar, *USDe*, crypto's first fully-backed, onchain, scalable, and censorship-resistant form of money. 

The mechanism backing *USDe* enables sUSDe, the first "Internet Bond" offering a crypto-native, reward-accruing asset, derived from staked asset returns (to the extent utilized in backing) and the funding and basis spread available in perpetual and futures markets.

## Peg Stability Mechanism



*USDe* derives its relative peg stability from executing automated and programmatic delta-neutral hedges with respect to the underlying backing assets. 

Hedging the price change risk of the backing asset in the same size minimizes fluctuations in the backing asset price as the change in value of the collateral asset is generally offset by the change in value of the hedge. 

This enables the synthetic USD value of the backing to remain relatively stable in most market conditions.

Ethena does not use any material leverage to margin the delta hedging derivatives positions beyond the natural state as a result of exchanges applying slight discounts to the value of backing assets to the extent used as backing and margin collateral on the initial hedge and issuance of *USDe*. 

#### Key Information

1. Users are able to acquire USDe in permissionless external liquidity pools.
2. Approved parties from permitted jurisdictions who pass KYC/KYB screening are able to **mint** & **redeem** *USDe* on-demand with Ethena contracts directly following whitelisting. See Supplemental USDe Terms and Conditions.
3. There is minimal reliance upon traditional banking infrastructure as trustless backing assets are held and stored within the crypto ecosystem. 

#### **Mechanic Example**

1. A whitelisted user provides ~$100 of *stETH* and receives ~100 newly-minted *USDe* atomically in return less the gas & execution costs to execute the hedge.
2. Slippage & execution fees are included in the price when **minting** & **redeeming**. Ethena earns no profit from the **minting** or **redeeming of** *USDe*.
3. The protocol opens a corresponding short perpetual position for the approximate same notional dollar value on a derivatives exchange.
4. The backing assets are transferred directly to an "Off Exchange Settlement" solution. Backing assets remain onchain and custodied by off exchange service providers to minimize counterparty risk. 
5. Ethena delegates, but never transfers custody of, backing assets to derivatives exchanges to margin the short perpetual hedging positions.

## Generated Revenue

The Ethena protocol generates two sustainable sources of revenue from the backing assets. 

The protocol revenue is derived from:

1. Staked ETH assets receiving consensus and execution layer rewards.
2. The funding and basis spread from the delta hedging derivatives positions.

Revenue from staked assets is floating by nature and denominated in the native asset - for example, liquid staked ETH tokens are typically denominated in *ETH*. 

The funding and basis spread can be floating or fixed depending upon if the protocol uses non-deliverable or deliverable derivatives positions to hedge the backing asset delta.

The funding and basis spread has historically generated a positive return given the mismatch in demand and supply for leverage in crypto as well as the existence of positive baseline funding.  If funding rates are deeply negative for a sustained period of time, such that the staked asset revenue cannot cover the funding and basis spread cost, the Ethena "reserve fund" is designed to bear the cost.

[Learn more about the protocol revenue.](https://docs.ethena.fi/solution-overview/protocol-revenue-explanation)

## Risks

The protocol is exposed to [various risks](https://docs.ethena.fi/solution-overview/risks) including but not limited to:

1. Smart Contract Risk
2. External Platform Risk
3. Liquidity Risk
4. Custodial Operational Risk
5. Exchange Counterparty Risk
6. Market Risk

Ethena recognizes these risks and actively attempts to ameliorate & diversify these risks as much as possible. In practice, this means the system uses multiple providers for each step of the workflow and actively monitors all partners and market conditions. 



Every element of the Ethena design has been formulated with risk mitigation in mind including the use of custodians, absence of material leverage, and diversification constraints on the hedging positions

Please refer to the [*USDe* Risk](https://docs.ethena.fi/solution-overview/risks) section for more information.

# Delta-Neutral Stability

### What is "delta"?

"Delta" refers to the sensitivity of the derivatives contract to a change in the price of the underlying asset. 

By way of example, if Ethena did not execute a hedge with respect to 1 ETH transferred by a minter upon mint of USDe, the backing of *USDe* would have a positive delta of 1 ETH. As a result, the USD value (and, by extension, *USDe* backing value) of the 1 ETH would change equally with the change in the spot market price of ETH.

Read more: [Introduction to Option Greeks](https://insights.deribit.com/education/introduction-to-option-greeks/)

### What is delta-neutral stability?

A portfolio can be considered to be "delta-neutral" if it has a delta of 0. This means the portfolio is NOT exposed to the price change in the underlying value of the asset.

Following on from the example above, where Ethena naturally has a positive delta of 1 *ETH* from a user providing 1 *ETH* of backing, if Ethena hedges 1 *ETH* worth of delta by going short a perpetual contract with a nominal position size equal to that 1 *ETH*, the delta of Ethena's portfolio is 0.

Said differently. when a portfolio is delta-neutral, the value in USD terms remains constant regardless of market conditions (ie regardless of any change in the spot price of *ETH*). The price of *ETH* could triple and then fall by 90% one second after another & the USD value of the portfolio would remain unaffected (outside of momentary dislocations between spot and derivatives markets). This is because the profits from the 1 *ETH* tripling in price are perfectly offset by losses from the equal-in-size short perpetual position.  [Here is a worked example of a portfolio being delta-neutral.](https://docs.ethena.fi/solution-overview/usde-overview/delta-neutral-examples)

Ethena trades with no effective leverage across exchanges as the delta offsetting short perpetual positions are equal in size to the backing assets.

To note, many institutional market makers remain delta-neutral to avoid profits/losses from price volatility and this is a very familiar concept across both traditional finance & digital assets.

# Delta-Neutral Examples

## Context

*Based on Arthur Hayes' example in his article:* [*Dust on Crust*](https://blog.bitmex.com/dust-on-crust/)

*Here, we have used an inverse perpetual to explain the different payoff scenarios of a delta-neutral strategy. Ethena will utilize both inverse and linear perpetuals. The payoff outcomes on an inverse perpetual are more intricate and as a result, we focus on explaining those scenarios below.*

An Ethereum inverse perpetual which is worth $1 of Ethereum paid out in Ethereum has the following payoff function:

*$1 / Ethereum Price in USD*

If Ethereum is worth $1, then the Ethereum value of the perpetual is 1 *ETH*, $1 / $1.

If Ethereum is worth $0.5, then the Ethereum value of the perpetual is 2 *ETH*, $1 / $0.5.

If Ethereum is worth $2, then the Ethereum value of the perpetual is 0.5 *ETH*, $1 / $2.

------

## Worked Examples



1 *USDe* = $1 of *ETH* + Short 1 Ethereum / USD Inverse Perpetual

To create 1 *USDe*, Ethena needs to delegate 1 *ETH* as margin with a derivatives exchange (via "Off-Exchange Settlement" solution) and short 1 ETHUSD perpetual.

#### Rapid ETH Price Decrease

- Now the Ethereum price falls from $1 to $0.1.
- The value of ETHUSD in ETH = $1 / $0.1 = 10 *ETH*
- The PNL of ETHUSD Position = 10 *ETH* (current value) – 1 *ETH* (initial value) = +9 *ETH* 
- We have 1 *ETH* delegated as margin with the exchange.
- Ethena's total equity balance with the exchange is 1 *ETH* (our initial margin) + 9 *ETH (*profit from the ETHUSD position), and the total balance is now 10 ETH. 
- The Ethereum price is now $0.1, but the system has 10 *ETH*, and therefore the USD value of the total portfolio is **unchanged** at $1, $0.1 * 10 *ETH*.

#### Rapid ETH Price Increase

- Now the Ethereum price rises from $1 to $100.
- The value of ETHUSD in *ETH* = $1 / $100 = 0.01 *ETH*
- The PNL of ETHUSD Position = 0.01 *ETH* (current value) – 1 *ETH* (initial value) = -0.99 *ETH*
- Ethena's total equity balance with the exchange is 1 *ETH* (initial margin) – 0.99 *ETH* (loss from ETHUSD position), and total balance is now 0.01 *ETH*. 
- The Ethereum price is now $100, but Ethena has 0.01 *ETH*, and therefore the USD value of the total portfolio is **unchanged** at $1, $100 * 0.01 *ETH*.

Delta-neutral strategies aim to ensure the portfolio value in synthetic USD terms is **unchanged** despite changes in value of the underlying collateral. In certain conditions and market environments this may not hold, as is described in more detail in the Risks section.

------

## Further Worked Examples

![img](https://docs.ethena.fi/~gitbook/image?url=https%3A%2F%2F596495599-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FsBsPyff5ft3inFy9jyjt%252Fuploads%252FonzheZxSlAzV6UlTTnUW%252Fimage.png%3Falt%3Dmedia%26token%3D548d4876-12b0-4cc9-9532-6763cb4b1659&width=768&dpr=4&quality=100&sign=9c58767f&sv=2)

![img](https://docs.ethena.fi/~gitbook/image?url=https%3A%2F%2F596495599-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FsBsPyff5ft3inFy9jyjt%252Fuploads%252F69OAKyvAo4QgWVz8gQ1B%252Fimage.png%3Falt%3Dmedia%26token%3D4c1aeaba-c9ca-4f30-9d42-7c953901d8fe&width=768&dpr=4&quality=100&sign=92a2dda2&sv=2)

# Scalability

### How *USDe* enables scalability

1. **Backing Ratio**

*USDe* is backed at a 1:1 ratio thanks to a delta-neutral strategy, where short BTC & *ETH* futures positions offset any changes in value to the underlying collateral. 

The result is the most capital-efficient synthetic dollar in the industry. 

Other onchain overcollateralized "stablecoins" tend to run minimum collateral ratios of ~150%, with some even higher, requiring more capital to be locked up than the stablecoin it mints. Effective overcollateralization is often over 200%.

While this approach is a good way to ensure stability when using decentralized collateral, the capital inefficiency of doing so means that the stablecoin cannot scale into the billions without taking on more centralized collateral, as we have seen with the proliferation of onchain RWAs. This opens up censorship risk and essentially makes the stablecoin a wrapper for U.S Treasuries. The only way to ensure capital efficiency and relative stability using decentralized collateral is to delta hedge any price exposure on trustless crypto collateral.

1. **CeFi Liquidity**

Unfortunately, decentralized perpetual liquidity isn’t sufficient to allow Ethena to achieve its goal of scaling *USDe* into the billions. Projects like UXD have tried to solely use decentralized exchanges, but the lack of liquidity severely limited their ability to scale, while others have fallen victim to hacks and exploits of the decentralized exchanges. 

With >25x the open interest on perpetual futures on centralized exchanges, a synthetic USD asset that leverages that liquidity has the ability to scale exponentially larger than would be possible on just decentralized exchanges living purely onchain. 

![img](https://docs.ethena.fi/~gitbook/image?url=https%3A%2F%2F596495599-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FsBsPyff5ft3inFy9jyjt%252Fuploads%252FI8V1dwHrOzTSCXeiWhBg%252Fimage_2024-04-15_15-15-16.png%3Falt%3Dmedia%26token%3Da2afd410-e2c4-48c2-b3f6-5bc3f7f0b2ed&width=768&dpr=4&quality=100&sign=ddb7bd8e&sv=2)

1. **Scalable Collateral Base**

The consensus view among Ethereum researchers and the ecosystem is that 40% of *ETH* supply staked is a very realistic near-term goal, with 27% of *ETH* supply staked currently (as of April 2024). 

At current prices that’s an extra ~$50bn of staked ETH growth, on top of an already impressive total of ~$110bn today. There is more than sufficient liquid staking token ("LST") collateral available to be used to mint *USDe* & for *USDe* to scale into the tens of billions using ETH alone.

In order to scale the product even further, Ethena uses *BTC* and will use other non-*ETH* assets as collateral in the future. Our product design is extendable in such a way that we are able to support any crypto asset with a sufficiently liquid derivatives market.

Currently, *BTC* funding rates closely mirror *ETH’s*, with funding being paid to the short side in the range of 7-9% annually on average.

# Censorship Resistance

### How *USDe furthers* censorship resistance



Assets backing USDe remain in "Off-Exchange Settlement" institutional grade solutions at all times. The only time collateral flows between custody and exchange is to settle funding or realized P&L.

Ethena utilizes "Off-Exchange Settlement" (OES) providers to hold backing assets. This enables Ethena to delegate/undelegate collateral to centralized exchanges without being exposed to exchange-specific idiosyncratic risk.

While using an OES provider requires a technological dependence upon the OES provider, it does NOT mean counterparty risk has simply been transferred from the exchange to the OES provider. OES providers typically, where not using an MPC solution, employ a bankruptcy-remote trust framework to ensure the OES provider's creditors have no claim to the assets. In the case of an OES provider failing, these assets are expected to be outside the provider's estate and not exposed to the credit risk of the custodian.

All supported OES providers are non-US-based. This offers a unique risk profile versus custodying funds with an exchange or holding fiat or treasury bonds in a US bank account or with a US based custodian. Treasury bonds and even stablecoins holding said treasuries present significant censorship risk.  Note: Due to the current regulatory environment in the US, and with a strong focus on global regulatory compliance, we have chosen not to work with US-based service providers at this time.  

In summary, while the use of OES providers may be viewed as more centralized vs fully onchain solutions, they represent very different censorship risk profiles than onchain stablecoins holding U.S Treasuries in a US bank account, or the opaque risk of holding assets on a centralized exchange.  Empirically, Ethena's integrated providers for custody services have never lost a dollar of users funds compared to the $7bn lost in DeFi hacks, and >$15bn in CeFi insitutions last cycle.

# Regulatory Compliance

As of 29 July 2024 Ethena GmbH, a wholly-owned subsidiary of Ethena Labs, submitted an application for authorization to make an offer to the public of an asset-referenced token pursuant to Art. 16 et seq. of Regulation (EU) 2023/1114 ("MiCAR") with Bundesanstalt für Finanzdienstleistungsaufsicht (“BaFin”) with respect to USDe. BaFin has significant experience and expertise with respect to crypto assets and we look forward to a collaborative process. As the application was submitted prior to the 30 July 2024 deadline, it is expected that the MiCAR grandfathering provisions with respect to the ongoing issuance of USDe apply (see Art. 143 para. 4 MiCAR). Updates will be provided publicly as appropriate as the authorization process proceeds according to the provisions of MiCAR. Please refer to the Supplemental USDe Terms and Conditions located at https://ethena-labs.gitbook.io/ethena-labs/resources/supplemental-usde-terms-and-conditions.

# Peg Arbitrage Mechanism

There is one presently available trade strategy available to users to profit from a price dislocation of *USDe* in external markets from what it is actually worth:

**Cross Market Arbitrage:** purchasing or selling USDe into the protocol mint & redeem contract when USDe price has diverged from $1.

## Trade Strategies

It's important to keep in mind:

- *USDe* is backed strictly by the protocol backing assets. 
- *USDe* is able to be **minted** & **redeemed** on demand by authorized, whitelisted users. This means that at any time, approved users are able to ramp in & out.
  - about 0.50% of backing assets are typically held in stablecoin form and available in the Minting Smart Contract to enable on-demand redemptions. This balance is systematically replenished from the 4% of the backing assets of *USDe* held in stablecoins that are readily available from multiple custodians.
- The value & amount of *USDe's* underlying backing is generally unaffected by any dislocations or rapid movements of price across any Centralized/Decentralized Spot Market, AMM Protocols, etc., though fluctuations in those markets may cause temporary dislocations in the secondary market price of *USDe* as the market's "reference assets" for the target peg.
- The value of the reserve underpinning *USDe* is generally unaffected by the removal of liquidity in volatile markets.

### 1. Cross Market Arbitrage

This strategy enables any user approved to mint/redeem to profit from the difference between the price/amount users' are able to **mint**/**redeem** *USDe* with Ethena & the value of *USDe* in an external market. An external market includes all centralized & decentralized spot markets such as "USDe/USDC" and AMM Protocols such as Uniswap or Curve. ![img](https://docs.ethena.fi/~gitbook/image?url=https%3A%2F%2Flh7-us.googleusercontent.com%2Fdocsz%2FAD_4nXe3W4OFZkxbBozA5Xid5BKDx_eBTrSwGn57b4eH1-tjHkZG784up8qbzDg-LDF57l1g5SAy3tFgnJFe7V9vfjhpKgB-Tv-hUBtwf_VEbkIr7xueN1AS1cjxoxVmei4DTaYjHCqOm6ynUCNOMI1WT8Xct2cE%3Fkey%3DLQPGPTylFgZCiOSN3cvgEA&width=300&dpr=4&quality=100&sign=b18925e2&sv=2)

If *USDe* is worth **LESS** in an external market than from Ethena directly, a user could:

1. Buy 1x *USDe* at 0.95 from Curve using *USDT*.
2. Redeem 1x *USDe* at 1.00 from Ethena receiving *USDT*.
3. Profit.

![img](https://docs.ethena.fi/~gitbook/image?url=https%3A%2F%2Flh7-us.googleusercontent.com%2Fdocsz%2FAD_4nXfl7pvmWxGSYQbfq7OkGYBrAbd-IuQ29HUesLZZ2kwsd6nVjuXrk4f2Sr9mFuJpRCELN5vIM7zweqE1g510kaMCb0W1swWiw38vPp7tyu5_IOGQoMxrrpoosndZeAu1oKJKPNJ6e-R5vEjbCd7EuSImStOv%3Fkey%3DLQPGPTylFgZCiOSN3cvgEA&width=300&dpr=4&quality=100&sign=3a5bfcf1&sv=2)

If *USDe* is worth **MORE** in an external market than from Ethena Labs, a user could:

1. Mint *USDe* using *USDT* from Ethena.
2. Sell the *USDe* in the Curve pool for > 1.00 for *USDT*.
3. Profit.