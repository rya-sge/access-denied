# Sky protocol - RWA Vault

In 2024, MakerDAO rebranded to Sky Ecosystem and launched a range of new products including a new stablecoin called USDS. 

- USDS is similar to the pre-existing Dai stablecoin, in the sense that it's a decentralized, unbiased, collateral-backed cryptocurrency soft-pegged to the US Dollar.
-  Technically, USDS is an IOU token on the Ethereum blockchain representing a collateralized balance in the MCD protocol's ‘vat’ smart contract—just like the Dai stablecoin.

This article focuses on the RWA part of the Sky ecosystem.

[TOC]



## RWA Vaults

### Introduction

Sky was one of the first projects in Decentralized Finance (DeFi) to introduce Real World Assets (RWA) as collateral to a stablecoin protocol.

https://makerdao.com/en/whitepaper/#sky-protocol-auctions

### About Real World Assets

Real World Assets (RWAs) are off-chain assets, such as real estate, loans, bonds, or commodities, that are tokenized for use in blockchain systems. They bridge the gap between traditional finance and decentralized finance (DeFi) by enabling these assets to be traded, used as collateral, or accessed more easily through digital means. 

RWAs bring stability, diversification, and liquidity to blockchain ecosystems but also require robust legal frameworks and mechanisms for accurate valuation and risk management.

### How the vaults work

A **vault** in the Sky Protocol (specifically within its Multi-Collateral Dai system, or MCD) is a feature of the MCD system that allows users to lock up collateral assets and generate DAI. It is a core component of how the Sky Protocol functions, enabling users to leverage their assets while maintaining a decentralized and over-collateralized system for creating stablecoins. Traditional vaults exclusively deal with on-chain cryptocurrencies like ETH or WBTC, which are native to the blockchain, easily verifiable, and highly liquid. These assets enable the protocol to operate entirely on-chain, using automated smart contracts to manage collateralization, valuation, and liquidation processes with minimal external dependencies.

**RWA vaults** differ from traditional vaults primarily in the type of collateral they support and the mechanisms required to manage them. They are implemented as a set of predefined rules on how the vault is managed within the MCD system—this implementation is described in MIP21 as part of Sky's former MIP (Maker Improvement Proposal) framework. 

- RWA vaults represent a protocol mechanism for interfacing with traditional financial instruments (ie. financial assets not natively issued on a blockchain and governed by off-chain legal agreements) and gaining exposure to them. 
- The protocol's technical architecture enables governance-approved strategies for capital deployment into sovereign debt instruments and similar highly-rated securities, with returns accruing to the protocol's surplus buffer. These assets exist outside the blockchain and require tokenization to represent their value digitally. 
- Managing RWA vaults involves more complex processes, which might include legal agreements to ensure enforceable claims on the underlying assets, reliance on third-party custodians and trustees to secure and manage these assets, and mechanisms to handle off-chain valuation and compliance. 
- Unlike traditional vaults, which rely on decentralized oracles for near-instant price feeds for managing risk, RWA vaults incorporate complementary off-chain methods and settlement processes that bridge traditional and decentralized finance systems for valuing and liquidating the collateral to manage the risk.

## High-Level Technical Overview

On a more technical level, each RWA vault is tailored for the specific requirements of the off-chain deal that drives it. However, there are some common components/patterns. Each RWA deal is composed of at least 3 smart-contract components:

### smart-contract components

#### RWA Urn

RWA Urn is the actual RWA Vault, with the rules that define the operation of the lower-level vault. Unlike regular crypto vaults that can be created by anyone, only Sky Governance is able to create them. The operation of such vaults is delegated to Sky Governance-approved counterparties. For instance, they can draw or repay Dai back and forth while the vault is active. Borrower capital use is dictated by an off-chain legal agreement with the DAO.

#### RWA token

RWA Token is the tokenized representation of the off-chain asset, to ensure consistent accounting of the transaction. The token is locked into the vault as collateral, for which the price is determined by the RWA Oracle. RWA Tokens are not freely transferable, as they have no intrinsic value, since it is not possible to redeem them anywhere. It should be either in control of the vault operator, or ideally be locked into the vault when the RWA deal is set up.

#### RWA Liquidation Oracle

Unlike regular crypto oracles, with live price feeds, the RWA Oracle is controlled by Sky Governance and only updated when required. Besides the RWA Token prices, the RWA Oracle also stores the link to the legal documents that govern the deal – usually in the form of an IPFS hash – and the "liquidation" status for the vault (see more on RWA Liquidation Process below).

### Helper components

Additionally, some helper components might be required:

#### RWA Output Conduit[1](https://makerdao.com/en/whitepaper/#fn-1):

After the operator draws Dai, an intermediate step might be required before it reaches its final destination. For instance, a specified third party might be required to authorize the transfer, or Dai should be converted into another stablecoin (i.e.: USDC) and then transferred. In those cases, a specialized variation of RWA Output Conduit is added to the setup as the destination for the Dai drawn from the RWA Urn.

#### RWA Input Conduit

Similar to output conduits, but used when the operator wants to repay Dai into the vault. Be it third party authorization, stablecoin swapping (i.e.: repayment is made in USDC instead of Dai), or something else, there might be a specialized variation of RWA Input Conduit added to the mix.

#### RWA jar

Stability fees in the Sky Protocol are inherently fixed—while they can be updated, they remain constant between updates—and accrue by the second.

- Some RWA deals don’t align with this model because they invest in assets with variable interest rates. 
- Rather than relying on approximate estimates and making frequent on-chain adjustments—which would be operationally expensive—certain RWA Vaults set their on-chain stability fee to zero, with the actual fee defined off-chain and enforced through binding legal documents. 
- In these cases, for accounting consistency, the fees generated by the Dai drawn from the vault must be transferred into an RWA Jar. From there, the fees can be permissionlessly moved to the Sky Protocol’s Surplus Buffer.

## RWA Liquidation Process

Unlike crypto collateral, which can be sold on-chain immediately as soon as the liquidation conditions are met, RWA liquidations might take months or even years to complete. Liquidations for RWA vaults occur entirely off-chain, through manual processes requiring Sky Governance and Ecosystem Actor coordination.

The RWA Liquidation has 2 steps:

1. **Soft Liquidation**: some conditions of the deal terms (i.e. covenants) are currently not being met. Some deals have an on-chain enforced grace period through which stakeholders can fix such issues before hard liquidation kicks in. If the relevant counterparty can meet the terms defined in the legal agreement, the RWA vault can be moved out of the soft liquidation state.
2. **Hard Liquidation**: if the stakeholders and Sky Governance agree that the Dai drawn from a specific RWA Vault is unrecoverable after the soft liquidation and the grace period has expired, then the Sky protocol needs to write off the existing debt, so the accounting reflects the reality. 
   - That means that the total outstanding debt for that vault needs to be deducted from the protocol's Surplus Buffer. 
   - If there is not enough surplus to cover the losses, the protocol will perform Flop auctions (mint governance tokens and purchase Dai from the market) until the surplus buffer returns to zero.

## The future of RWA Vaults

The inclusion of RWA vaults allowed Sky to diversify its collateral base and reduce dependence on volatile cryptocurrencies. However, this came with increased operational complexity, slower liquidation times, and legal complexity. Despite these factors, RWAs continue to be a key collateral type for the Sky Protocol. Since the rebranding from MakerDAO to Sky, the creation and management of RWAs will be spearheaded by Stars, which are independent projects within the Sky Ecosystem. Stars will be operating a new framework called the Allocation System to autonomously manage allocations into tokenized RWAs, which will be implemented with new and improved techniques from the historical RWA vaults described above. While the Stars will have some level of autonomy, their actions will still being subject to Sky's risk management systems. The allocation system is a framework designed to manage and deploy capital across the Sky ecosystem efficiently. It allows Stars to borrow funds from the Sky Protocol at favorable rates, enabling targeted liquidity injections into DeFi protocols and tokenized real-world assets. This system enhances the ecosystem's financial stability through significant allocations into liquid asset types, with an emphasis on risk management to ensure that capital allocations are optimized for risk-adjusted returns while fostering growth and diversification within the Sky ecosystem.