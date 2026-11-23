---
layout: post
title: "Vault Curator - Steak House Finance"
date:   2025-11-06
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: blockchain ethereum defi
tags: steakhouse-finance defi blockchain
description: Initially established as core contributors to the Sky (f.k.a. MakerDAO) ecosystem, Steakhouse has gone on to become a curator and DeFi advisory firm working with some of the largest protocols, including Lido, Morpho, Ethena, ENS, Arbitrum, and more.
image: /assets/article/blockchain/defi/2025-11-06-steakhouse-finance-overview-mindmap.png
isMath: false
---

Initially established as core contributors to the Sky (f.k.a. MakerDAO) ecosystem, Steakhouse has gone on to become a curator and DeFi advisory firm working with some of the largest protocols, including Lido, Morpho, Ethena, ENS, Arbitrum, and more.

Reference used: [steakhouse.financial](https://www.steakhouse.financial) / [hackmd.io/@SteakhouseFi](https://hackmd.io/@SteakhouseFi) / [Aribtrum forum](https://forum.arbitrum.foundation/t/steakhouse-financial-step-program-manager/23829) / [ENS discussion](https://discuss.ens.domains/t/ens-financial-reporting-by-steakhouse/16601/21).

[TOC]

## What you need to know first

The vault descriptions below use a few DeFi lending notions without explaining them.

- **Over-collateralized lending**: a borrower deposits collateral worth more than the loan, and the position is liquidated if the collateral value falls too far. Every vault in this article earns its yield by lending a stablecoin or ETH to such borrowers; see [How Morpho Blue Works]({{site.url_complet}}/2026/10/10/morpho-blue-lending-markets/).
- **Curated lending vaults**: depositors put one asset into a vault, and a curator chooses which lending markets receive it and up to which cap. Steakhouse plays this role on Morpho and Kamino; see [How Morpho Vault V1 (MetaMorpho) Works, and What Vault V2 Changes]({{site.url_complet}}/2026/10/10/morpho-vault-v1-metamorpho/).
- **Timelock and guardian**: on a MetaMorpho vault, sensitive changes such as raising a market cap wait for a delay before taking effect, and a guardian can cancel them in the meantime. The Smokehouse vaults rely on a 3-day timelock and an Aragon DAO acting as guardian.
- **Real-world assets (RWA)**: tokens that represent off-chain assets such as Treasury bills or loan portfolios, issued by a regulated entity that holds the underlying. Several vaults accept them as collateral, and Grove allocates Sky's reserves into them.
- **Price oracles**: contracts that publish an asset's market price on-chain, which a lending market reads to decide when a position can be liquidated; see [How to build a blockchain oracle]({{site.url_complet}}/2024/04/16/build-blockchain-oracle/). Steakhouse runs a validator for the Chronicle oracle network.
- **Sky (formerly MakerDAO)**: the protocol that issues the DAI and USDS stablecoins against collateral and invests part of its reserves; see [Introduction to MakerDAO]({{site.url_complet}}/2023/11/21/makerdao/). Steakhouse started as a contributor to it.

## Kamino Finance

Steakhouse is an official risk contributor to [Kamino Finance](https://kamino.com)

Here a  list of some of their vaults.

[USDC prime](https://app.kamino.finance/earn/HDsayqAsDWy3QvANGqh2yNraqcD8Fnjgh73Mhb3WRS5E)

- Risk: conservative
- USDC Prime is a conservative lending strategy designed to deliver consistent, risk-adjusted yields by allocating funds across highly liquid markets and premium collateral. Managed by Steakhouse Financial, this vault lends USDC against both core collateral markets, such as ain/JLP, and selected real-world asset (RWA) pools. It adapts its allocation to market conditions, with yield and capital preservation as its stated aims.

[Steakhouse USDC High Yield](https://app.kamino.finance/earn/BEEfo7xwgK2ZP13Pxo7qqTPzAteKJmXjVWtMWcXSvbn2)

- Risk: Balanced
- The Steakhouse High Yield USDC vault aims to optimize yields by lending USDC against a wide range of collaterals.

[Steakhouse USDG](https://app.kamino.finance/earn/BqBsS4myH82S4yfqeKjXSF7yErWwSi5WTshSzKmHQgzw)

- Risk: Balanced
- Steakhouse USDG vault aims to optimize yields by lending USDG against blue chip crypto and real world asset (RWA) collateral markets, depending on market conditions. We call this the “dual engine".

Reference: [gov.kamino.finance -  Introducing Steakhouse Financial as Official Risk Contributors](https://gov.kamino.finance/t/introducing-steakhouse-financial-as-official-risk-contributors/653)



## Morpho

[Steakhouse financial](https://app.morpho.org/arbitrum/curator/steakhouse-financial) is a vault manager for [Morpho](https://morpho.org)

Here a non-exhaustive list of some of their vaults.

See also [steakhouse.financial - morpho-vaults](https://www.steakhouse.financial/docs/products/steakhouse-financial-products/morpho-vaults)

### Ethereum

- [SteakhouseUSDC](https://app.morpho.org/ethereum/vault/0xBEEF01735c132Ada46AA9aA4c54623cAA92A64CB/steakhouse-usdc)

The Steakhouse USDC vault aims to optimize yields by lending USDC against blue chip crypto and real world asset (RWA) collateral markets, depending on market conditions. We call this the “dual engine.”

- [Steakhouse USDT](https://app.morpho.org/ethereum/vault/0xbEef047a543E45807105E51A8BBEFCc5950fcfBa/steakhouse-usdt)

The Steakhouse USDT vault aims to optimize yields by lending USDT against blue chip crypto and real world asset (RWA) collateral markets, depending on market conditions. We call this the “dual engine.”

- SteakhouseRUSD

The Steakhouse rUSD vault allows Reservoir Protocol to deploy rUSD against bluechip crypto and RWA collaterals.

- [SteakhouseUSDC RWA](https://app.morpho.org/base/vault/0xbEefc4aDBE58173FCa2C042097Fe33095E68C3D6/steakhouse-usdc-rwa)

### Katana

- [Steakhouse Prime USDC](https://app.morpho.org/katana/vault/0x61D4F9D3797BA4dA152238c53a6f93Fb665C3c1d/steakhouse-prime-usdc)
- [Steakhouse Prime AUSD](https://app.morpho.org/katana/vault/0x82c4C641CCc38719ae1f0FBd16A64808d838fDfD/steakhouse-prime-ausd)

The Steakhouse Prime AUSD vault aims to optimize yields by lending AUSD against blue chip crypto assets.

- [Steakhouse High Yield AUSD](https://app.morpho.org/katana/vault/0xdE6a4F28Acfe431DD1CfA2D9c7A3d8301624a841/steakhouse-high-yield-ausd)
- [Steakhouse High Yield USDC](https://app.morpho.org/katana/vault/0x1445A01a57D7B7663CfD7B4EE0a8Ec03B379aabD/steakhouse-high-yield-usdc)

### Arbitrum

- [Steakhouse Prime USDC](https://app.morpho.org/arbitrum/vault/0x250CF7c82bAc7cB6cf899b6052979d4B5BA1f9ca/steakhouse-prime-usdc)
- [Steakhouse High Yield USDC](https://app.morpho.org/arbitrum/vault/0x5c0C306Aaa9F877de636f4d5822cA9F2E81563BA/steakhouse-high-yield-usdc)
- [Steakhouse Prime ETH](https://app.morpho.org/arbitrum/vault/0x0623a67D69bB2F59D266897A15dC1509d291D631/steakhouse-prime-eth)

The Steakhouse Prime ETH vault aims to optimize yields by lending ETH against blue chip crypto assets.

- [Steakhouse High Yield USDT0](https://app.morpho.org/arbitrum/vault/0x4739E2c293bDCD835829aA7c5d7fBdee93565D1a/steakhouse-high-yield-usdt0)

The Steakhouse High Yield USDT0 vault aims to optimize yields by lending USDT0 against a wide range of collaterals.

- [Steakhouse Prime USDT0](https://app.morpho.org/arbitrum/vault/0x2281961480216653529A03D6CE03Ee6B8cdF564E/steakhouse-prime-usdt0)

### Proposal

#### RWA-backed Steakhouse USDC MetaMorpho Vault

Proposal date: November 9, 2023

The inaugural USDC vault curated by Steakhouse Financial will initially lend against tokenized T-bills, namely Backed Finance’s bIB01. bIB01 is an ERC-20 token backed by IB01 ([Blackrock’s iShares 0-1 yr US Treasury ETF](https://www.ishares.com/uk/individual/en/products/307243/ishares-treasury-bond-0-1yr-ucits-etf)). Suppliers to the vault can earn a passive yield by lending their USDC to over-collateralized borrowers, who in turn provide bIB01 as collateral for their loans.

Reference:  [Steakhouse Financial: RWA-backed Flagship USDC MetaMorpho Vault Whitlisting](https://forum.morpho.org/t/steakhouse-financial-rwa-backed-flagship-usdc-metamorpho-vault-whitlisting/375)



#### Introducing the Smokehouse product line: bbqUSDC and bbqDAI

Smokehouse vaults are for frontiersmen and women who are not afraid of exotic collateral types. It will use a wide range of collateral to allow vaults to be exposed to the most diverse possible types of borrowing activity. Like all our vaults, it is non-custodial and users should perform their risk analysis by themselves before depositing.

The Smokehouse vault keeps all the great features of other Steakhouse vaults:

- 3-day timelock allowing people to exit if a new collateral is not fitting their risk tolerance
- On-chain Aragon DAO Guardians to allow all depositors to veto any significant action made by the curator:
  - [bbqUSDC guardian](https://app.aragon.org/#/daos/ethereum/bbqusdc-guardian.dao.eth/dashboard)
  - [bbqDAI guardian](https://app.aragon.org/#/daos/ethereum/bbqdai-guardian.dao.eth/dashboard)
- State of the art programmatic reallocation system

Reference: [Introducing the Smokehouse product line: bbqUSDC and bbqDAI](https://forum.morpho.org/t/introducing-the-smokehouse-product-line-bbqusdc-and-bbqdai/1182)



## MakerDAO / SKY

Reference

- [steakhouse.financial - MakerDAO Financial Report 2023](https://kitchen.steakhouse.financial/p/makerdao-financial-report-2023)
- [MIPS - Rewards Plan budget for the Strategic Finance Core Unit (SF-001) / Steakhouse Financial.](https://mips.makerdao.com/mips/details/MIP40c3SP94)



### Grove (Sky)

Steakhouse Financial is building `Grove`, an institutional-grade credit protocol to unlock USDS's full potential by bridging DeFi and traditional finance.

It will enable Sky to scale offchain credit, create new farming opportunities, and offer USDS holders better savings rates with diversified real-world assets. 

Its main product is `Grove Allocator`: 

- Grove allocator integrated directly with a wide range of tokenized assets extending the reach of DeFi to major institutions, scalable RWAs, and frontier DeFi protocols.
- Optimized yield: The Grove Allocation layer aggregates yields across a growing list of on-chain and off-chain tokenized assets.

Reference: 

- [grove.finance](https://www.grove.finance)
- [kitchen.steakhouse.financial/p/introducing-grove](https://kitchen.steakhouse.financial/p/introducing-grove)

#### Example

According to an [announcement](https://www.businesswire.com/news/home/20250624393365/en/Grove-Announces-Launch-of-Institutional-Grade-Credit-Infrastructure-DeFi-Protocol-with-%241-Billion-Allocation-to-Tokenized-Janus-Henderson-Anemoy-AAA-CLO-Strategy), Sky, formerly MakerDAO, approved a $1 billion allocation into the Janus Henderson Anemoy AAA CLO Strategy, using Grove's decentralized infrastructure. The strategy is an onchain collateralized loan obligation (CLO) launched in collaboration with the tokenized real-world asset lending protocol [Centrifuge](https://www.theblock.co/post/288846/centrifuge-raises-15-million-in-series-a-funding-for-institutional-defi-adoption).

Reference: [theblock.co - Sky approves $1 billion allocation for Janus Henderson's onchain fund using fresh-out-of-stealth Grove infrastructure](https://www.theblock.co/post/359687/sky-approves-1-billion-allocation-for-janus-hendersons-onchain-fund-using-fresh-out-of-stealth-grove-infrastructure)

## Chronicle Oracle

Steakhouse is an oracle provider to Chronicle Protocol's decentralized validator network

Reference: [The Block - Bitcoin Suisse, Steakhouse Financial and Block Analitica join as validators for oracle provider Chronicle Protocol - The Block](https://www.theblock.co/post/338141/bitcoin-suisse-steakhouse-financial-block-analitica-validators-oracle-chronicle-protocol), [Chronicle Labs - The Security of DeFi Grows Stronger: Steakhouse Financial, Block Analitica, and Bitcoin Suisse Join Chronicle](https://chroniclelabs.org/blog/the-security-of-defi-grows-stronger-steakhouse-financial-block-analitica-and-bitcoin-suisse-join)

## Other

### Arbitrum

See [Aribtrum forum](https://forum.arbitrum.foundation/t/steakhouse-financial-step-program-manager/23829)

### Lido

[2022]

Lido DAO onboards Steakhouse Financial as the Finance unit, partnering with Lido DAO contributors to build out full financial statements; develop, manage, and execute payroll processes end-to-end in concert with operations and legal workstreams; create standardized financial reports for the entire DAO including cash flow, grants, operating expenses; and develop financing and operating plans to support long-term growth of Lido DAO.

Status: [passed](https://snapshot.org/#/s:lido-snapshot.eth/proposal/0xa7a8d9f42f72405a72f91d8124f970815028526197b9cc186a1882fae2d17e05)

See [Lido - research](https://research.lido.fi/t/lido-dao-finance-workstream-proposal-steakhouse-financial/2823)

### Blog

- [Steakhouse Financial - The Curious Case of On-Chain Private Credit Repo](https://kitchen.steakhouse.financial/p/the-curious-case-of-on-chain-private)

## Mindmap

The mindmap below summarizes the article.

![Steakhouse Financial overview mindmap]({{site.url_complet}}/assets/article/blockchain/defi/2025-11-06-steakhouse-finance-overview-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Vault curator** | The entity that selects the markets and collateral a lending vault may use and sets its caps; Steakhouse acts as one on Morpho and as a risk contributor on Kamino. |
| **Lending vault** | A contract that pools deposits of one asset and lends them across several lending markets to earn yield for its depositors. |
| **MetaMorpho vault** | Morpho's vault design, through which Steakhouse launched its first RWA-backed USDC vault in 2023. |
| **Over-collateralized loan** | A loan backed by collateral worth more than the borrowed amount, as with the bIB01-backed USDC loans of the first Steakhouse vault. |
| **Blue-chip collateral** | Large, liquid crypto assets accepted as collateral in the Prime vaults, as opposed to the wider range of the High Yield vaults. |
| **Real-world asset (RWA)** | A token representing an off-chain asset, such as a tokenized Treasury bill or a loan portfolio, used as collateral or as an investment. |
| **Tokenized T-bill** | A token backed by short-term US government debt, such as Backed Finance's bIB01, backed by the iShares 0-1 year US Treasury ETF. |
| **Dual engine** | Steakhouse's name for a vault that lends against both blue-chip crypto and RWA collateral, shifting between them with market conditions. |
| **Timelock** | A delay imposed before a significant curator action takes effect, so depositors can exit if they disagree with it. |
| **Guardian** | An on-chain role, held by an Aragon DAO for the Smokehouse vaults, that can veto significant curator actions during the timelock. |
| **Reallocation** | Moving a vault's funds between its lending markets, which Steakhouse performs through a programmatic system. |
| **Grove** | The credit protocol built by Steakhouse for Sky, whose Grove Allocator deploys USDS into tokenized on-chain and off-chain assets. |
| **Collateralized loan obligation (CLO)** | A pooled portfolio of loans split into tranches; the Janus Henderson Anemoy AAA CLO Strategy is an on-chain version that received a $1 billion Sky allocation through Grove. |
| **Oracle validator** | A participant that signs price data for an oracle network; Steakhouse holds this role for Chronicle Protocol. |

## Related articles

- [How Morpho Blue Works - Isolated Lending Markets, Shares, Liquidations and Bad Debt]({{site.url_complet}}/2026/10/10/morpho-blue-lending-markets/)
- [Monitoring a Morpho Vault V2 - What a Depositor Needs to Watch]({{site.url_complet}}/2026/10/10/morpho-vault-v2-risk-monitoring/)
- [How Morpho Vault V2 Works - Adapters, Caps, Timelocks and In-Kind Redemption]({{site.url_complet}}/2026/10/10/morpho-vault-v2-architecture/)
- [How Morpho Vault V1 (MetaMorpho) Works, and What Vault V2 Changes]({{site.url_complet}}/2026/10/10/morpho-vault-v1-metamorpho/)
- [Morpho Vault V2 Adapters - How a Vault Allocates, and Why It Wraps a Vault V1]({{site.url_complet}}/2026/10/10/morpho-vault-v2-adapters/)
