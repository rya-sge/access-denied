---
layout: post
title: 10 Key Differences Between MakerDAO and Liquity
date:   2024-12-16
last_modified_at: 2026-10-22
lang: en
locale: en-GB
categories: blockchain defi
tags: makerDAO liquity stablecoin
description: How Liquity V1 differs from MakerDAO on governance, collateral, redemptions, interest, liquidations and shutdown, with notes on what Liquity V2 changed.
image: /assets/article/blockchain/defi/2024-12-16-10-Key-Differences-Between-MakerDAO-and-Liquity-mindmap.png
isMath: false
---

This article comes from a [presentation video](https://www.youtube.com/watch?v=bXLTE-5BkhA) made by  Robert Lauko in 2021 to explain how Liquity differs from Maker DAO.

Since the video is rather old, it is possible that some information is no longer completely up to date. However, I found it very interesting to understand Liquity and the first version of MakerDAO (now [Sky](https://sky.money))

- A transcript has been generated with [NoteGPT](https://notegpt.io)
- A more formal article has been made with ChatGPT from this transcript
- Finally, I have perform a few addition and personal notes.

> **Update (October 2026).** The comparison below describes Liquity V1. Liquity V2, launched in 2025 with the BOLD stablecoin, changes several of these points (interest, collateral, governance, Recovery Mode). Each section now ends with a short *Liquity V2* note where it differs. The two versions are described in detail in [How Liquity V1 Works]({{site.url_complet}}/2026/10/22/liquity-v1-lusd-troves-stability-pool/) and [How Liquity V2 Works]({{site.url_complet}}/2026/10/22/liquity-v2-bold-user-set-interest-rates/).

Here’s an exploration of the 10 key differences between MakerDAO and Liquity.

## Introduction

### MakerDAO (DAI)

[MakerDAO](https://makerdao.com/en/) is a decentralized autonomous organization managing and issuing the **stablecoin** DAI, which is designed to maintain a 1:1 peg with the US Dollar.

Unlike traditional fiat-backed stablecoins that rely on a centralized entity to hold reserves, Dai is generated through a process called **collateralized debt positions (CDPs)**. 

Users lock up collateral, in the form of Ethereum (ETH), in a smart contract, and in return, they receive Dai. 

This process ensures that Dai is always backed by collateral, maintaining its stability.

You can find more information in my article: [Introduction to MakerDAO](https://rya-sge.github.io/access-denied/2023/11/21/makerdao/)

### Liquity V1

Liquity is a decentralized borrowing protocol that allows you to draw [interest-free](https://app.gitbook.com/@liquity/s/liquity-docs/faq/borrowing#how-can-you-offer-borrowing-at-a-0-interest-rate) loans against Ether used as [collateral](https://docs.liquity.org/liquity-v1/faq/borrowing#what-do-you-mean-by-collateral). 

Loans are paid out in LUSD (a USD pegged stablecoin) and need to maintain a [minimum collateral ratio](https://docs.liquity.org/liquity-v1/faq/borrowing#what-is-the-minimum-collateral-ratio-mcr-and-the-recommended-collateral-ratio) of 110%.

In addition to the collateral, the loans are secured by a Stability Pool containing LUSD and by borrowers collectively acting as guarantors of last resort. 

Liquity as a protocol is non-custodial, immutable, and governance-free.

Reference: Liquity is a decentralized borrowing protocol that allows you to draw [interest-free](https://app.gitbook.com/@liquity/s/liquity-docs/faq/borrowing#how-can-you-offer-borrowing-at-a-0-interest-rate) loans against Ether used as [collateral](https://docs.liquity.org/liquity-v1/faq/borrowing#what-do-you-mean-by-collateral). Loans are paid out in LUSD (a USD pegged stablecoin) and need to maintain a [minimum collateral ratio](https://docs.liquity.org/liquity-v1/faq/borrowing#what-is-the-minimum-collateral-ratio-mcr-and-the-recommended-collateral-ratio) of 110%.

In addition to the collateral, the loans are secured by a Stability Pool containing LUSD and by fellow borrowers collectively acting as guarantors of last resort. Learn more about these mechanisms in our documentation.

Liquity as a protocol is non-custodial, immutable, and governance-free.

Reference: [Liquity V1](https://docs.liquity.org/liquity-v1)

------

### 1. Governance

MakerDAO operates on a human governance model, where key parameters like `interest rates` and `collateralization ratios` are adjusted through community votes. These votes require holding the Maker (MKR) token, which grants voting rights. However, challenges such as low voter turnout and the potential for manipulation, such as through flash loans, can affect the system's efficiency.

>  Personal note:

- In 2020, a protocol team uses a flashloan to pass one of their proposal, see [MakerDAO issues warning after a flash loan is used to pass a governance vote](https://www.theblock.co/post/82721/makerdao-issues-warning-after-a-flash-loan-is-used-to-pass-a-governance-vote).
- Sky Money, the new version of MakerDao uses a specific smart contract `ds-chief`to prevent MKR locked for voting from being used in the same block as the deposit.  See [developers.sky.money - governance-flash-loan-attacks](https://developers.sky.money/security/security-measures/security-mechanisms#governance-flash-loan-attacks)

In contrast, Liquity V1 has no governance at all. Its parameters (minimum collateral ratio, fee floors, liquidation reserve) are constants in immutable contracts with no admin key. The only values that move are the borrowing and redemption fees, which follow a formula driven by redemption volume and time, without any vote.

*Liquity V2:* a limited governance exists. LQTY stakers vote each week on how 25% of the interest paid by borrowers is distributed to liquidity initiatives. They cannot change any protocol parameter, since the core contracts remain immutable.

------

### 2. Collateral Approach

MakerDAO supports a multi-collateral system, allowing various ERC-20 tokens as collateral. While this provides flexibility, it introduces risks, as many tokens depend on issuers or are vulnerable to security exploits.

Liquity V1 adopts a single-collateral approach, accepting only Ether (ETH) as collateral. This choice aligns with its belief in Ether as the most trustless, risk-free asset on the Ethereum network. By focusing on Ether, Liquity minimizes complexity and potential vulnerabilities.

*Liquity V2:* the BOLD stablecoin also accepts two liquid staking tokens (LSTs), Lido's wstETH and Rocket Pool's rETH, in addition to Ether. Each collateral has its own branch of contracts, Stability Pool and parameters, so a problem with one LST does not mix collateral across branches. See the [Liquity V2 Whitepaper](https://liquity.gitbook.io/v2-whitepaper) and [How Liquity V2 Works]({{site.url_complet}}/2026/10/22/liquity-v2-bold-user-set-interest-rates/).

### 3. Decentralized Frontends

MakerDAO relies on centralized frontends, often hosted on specific servers, which could pose censorship risks. 

Liquity, on the other hand, supports a decentralized network of frontends. Anyone can run a frontend that interacts with the protocol, enhancing censorship resistance and decentralization. Additionally, Liquity incentivizes frontend operators with rewards, encouraging broader adoption and usage.

------

### 4. Stablecoin Redemption

Liquity’s stablecoin, LUSD, is fully redeemable against Ether at face value, ensuring a direct and transparent peg to the US dollar. This mechanism creates a hard price floor, as holders can arbitrage any deviation below $1 by redeeming LUSD for Ether.

See [docs.liquity.org - lusd-redemptions](https://docs.liquity.org/liquity-v1/faq/lusd-redemptions)

In contrast, MakerDAO’s DAI lacks direct redeemability for collateral. Instead, it employs indirect stability mechanisms, resulting in a soft peg that may be less resilient under extreme market conditions.

------

### 5. Interest-Free Loans

Liquity offers loans without recurring interest. Borrowers only pay a `one-time` issuance fee when opening a loan, and there are no ongoing costs. This allows users to keep their debt positions open indefinitely without accumulating additional charges.

MakerDAO applies a `stability fee`, which functions as an interest rate, accruing over time. This recurring cost can be a significant consideration for long-term borrowers.

*Liquity V2:* loans are no longer interest-free. Each borrower chooses their own annual rate, between 0.5% and 250%, and can change it. Redemptions take collateral from the troves with the lowest rates first, so the rate also sets how exposed a borrower is to redemptions. The rate is set by the market of borrowers, not by governance as with Maker's stability fee.

See [Maker DAO archive - stability-fee](https://rya-sge.github.io/maker-dao-community-archive/faqs/stability-fee/)

------

### 6. Collateralization Ratios

MakerDAO’s minimum collateralization ratio for Ether is either 130% or 150%, depending on the specific parameters. Higher ratios provide a buffer but limit capital efficiency.

Liquity’s system (V1) requires only a 110% minimum collateralization ratio, enabled by its innovative liquidation mechanism. This lower requirement increases capital efficiency while maintaining system stability. See [Liquity CR](https://www.liquity.org/features/collaterization-ratio)

*Liquity V2:* the minimum is 110% for ETH and 120% for wstETH and rETH.

------

### 7. Liquidation Mechanisms

MakerDAO utilizes an auction-based liquidation process, which can take up to six hours. This delay requires higher collateral buffers to account for potential price fluctuations during the auction.

Liquity employs instantaneous liquidations. A stability pool pre-funds the repayment of under-collateralized debt, ensuring immediate resolution. This approach eliminates the need for auctions, reduces risks from price volatility, and enhances capital efficiency.

------

### 8. Savings and Incentives

MakerDAO offers the `DAI Savings Rate (DSR)`, allowing users to earn interest on their DAI holdings. However, the rate is determined by human governance and is currently set at 0%.

Liquity does not have a direct savings feature but offers two alternative mechanisms: the Stability Pool and LQTY staking. The Stability Pool allows users to deposit LUSD and earn liquidation gains in Ether. Additionally, LQTY token holders can stake their tokens to earn a share of system fees, providing multiple avenues for rewards.

*Liquity V2:* the Stability Pool of each collateral branch receives 75% of the interest paid by that branch's borrowers, in addition to liquidation gains. It works as a savings product whose yield comes from borrowers rather than from a governance-set rate such as the DSR.

------

### 9. Secondary Token Role

MakerDAO relies on the MKR token as a lender of last resort. In extreme scenarios, MKR tokens can be minted and sold to recapitalize the system, potentially diluting existing holders.

> Personal note

This was indeed the case in 2020: a rapid price declines has provoked a $4 million shortfall on MakerDAO. In order to bring the system back to a healthy state, MKR tokens has been created and auctioned off to make up for the lost collateral value.

See [Messari - MakerDAO releases plans to recapitalize the protocol through MKR auction](https://messari.io/report/makerdao-releases-plans-to-recapitalize-the-protocol-through-mkr-auction)

Liquity avoids this approach by employing a redistribution mechanism. If the Stability Pool is insufficient to cover liquidations, debt is redistributed among remaining borrowers. This decentralized co-guarantor model eliminates the need for token dilution while maintaining system stability.

------

### 10. Emergency Shutdown vs. Recovery Mode

MakerDAO employs an emergency shutdown mechanism to wind down the system in case of extreme under-collateralization. While effective, it results in the complete cessation of the protocol.

What happens during an Emergency Shutdown?

1. An emergency Shutdown stops CDP creation and freezes the Price Feed.
2. Collateral Claims are processed: After Emergency Shutdown is activated, a time period is needed to allow the processing of the proportional collateral claims of all CDP owners. After this processing is done, all CDP owners will be able to claim a fixed amount of ETH with their CDPs. Dai holders can access their collateral claims immediately.
3. Dai and CDP owners claim collateral: Each Dai holder and CDP owner can exchange their Dai and CDPs directly for a fixed amount of ETH that corresponds to the calculated value of their assets.

See [Maker DAO archive - Emergency Shutdown](https://rya-sge.github.io/maker-dao-community-archive/scd-faqs/emergency-shutdown/#what-is-an-emergency-shutdown)

Liquity V1 uses a Recovery Mode when the total collateralization ratio drops below 150%. In that mode, a trove whose ratio is below the system's total ratio can be liquidated if the Stability Pool covers its whole debt (the borrower keeps collateral above 110% of the debt), and new borrowing must keep the system ratio from falling. The system returns to normal operation when the ratio recovers, without shutting down.

*Liquity V2:* Recovery Mode is removed, so a trove above the minimum ratio is never liquidated. Each collateral branch has a critical ratio (150% or 160%) below which borrowing that lowers the system ratio is refused, and a shutdown ratio (110% or 120%). Below the shutdown ratio, or if the branch's oracle fails, the branch shuts down permanently and fee-free "urgent" redemptions with a 2% bonus clear its debt. This is closer to Maker's emergency shutdown, but it applies to one collateral at a time rather than to the whole system.

------

### Conclusion

While both MakerDAO and Liquity aim to provide stablecoin solutions and DeFi lending, their approaches differ significantly in governance, collateral management, liquidation mechanisms, and system design. Liquity’s emphasis on algorithmic governance, single collateralization, and instantaneous liquidations.

## Mindmap

The mindmap below summarizes the article.

![MakerDAO vs Liquity mindmap]({{site.url_complet}}/assets/article/blockchain/defi/2024-12-16-10-Key-Differences-Between-MakerDAO-and-Liquity-mindmap.png)

## Related articles

- [How Liquity V1 Works - LUSD, Troves, the Stability Pool, Redemptions and Recovery Mode]({{site.url_complet}}/2026/10/22/liquity-v1-lusd-troves-stability-pool/)
- [How Liquity V2 Works - BOLD, User-Set Interest Rates, Redemption Routing and Branch Shutdown]({{site.url_complet}}/2026/10/22/liquity-v2-bold-user-set-interest-rates/)
- [Stablecoins Under MiCA — Asset-Referenced Tokens and E-Money Tokens (Titles III and IV)]({{site.url_complet}}/2026/09/17/mica-stablecoins-asset-referenced-tokens-e-money-tokens/)
- [How Polaris Works - pETH, the Power-Law Bonding Curve, Reserve Loans and pAsset Markets]({{site.url_complet}}/2026/10/21/polaris-peth-bonding-curve-passets/)
