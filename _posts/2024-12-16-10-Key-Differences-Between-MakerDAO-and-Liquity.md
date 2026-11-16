---
layout: post
title: 10 Key Differences Between MakerDAO and Liquity
date:   2024-12-16
last_modified_at: 2026-11-16
lang: en
locale: en-GB
categories: blockchain defi
tags: makerDAO sky liquity stablecoin
description: How Liquity V1 and V2 differ from MakerDAO and Sky on governance, collateral, redemptions, interest, liquidations and shutdown, version by version.
image: /assets/article/blockchain/defi/2024-12-16-10-Key-Differences-Between-MakerDAO-and-Liquity-mindmap.png
isMath: false
---

This article comes from a [presentation video](https://www.youtube.com/watch?v=bXLTE-5BkhA) made by  Robert Lauko in 2021 to explain how Liquity differs from Maker DAO.

Since the video is rather old, it is possible that some information is no longer completely up to date. However, I found it very interesting to understand Liquity and MakerDAO as it stood in 2021 (now [Sky](https://sky.money)).

- A transcript has been generated with [NoteGPT](https://notegpt.io)
- A more formal article has been made with ChatGPT from this transcript
- Finally, I have perform a few addition and personal notes.

> **Update (October 2026).** The comparison below describes Liquity V1. Liquity V2, launched in 2025 with the BOLD stablecoin, changes several of these points (interest, collateral, governance, Recovery Mode). Each section now ends with a short *Liquity V2* note where it differs. The two versions are described in detail in [How Liquity V1 Works]({{site.url_complet}}/2026/10/22/liquity-v1-lusd-troves-stability-pool/) and [How Liquity V2 Works]({{site.url_complet}}/2026/10/22/liquity-v2-bold-user-set-interest-rates/).

> **Update (November 2026).** MakerDAO has also changed several times since the talk, so each section now says which Maker version implements what, and corrects what the current mainnet configuration has made outdated: debt auctions are switched off, the Emergency Shutdown Module can no longer be triggered by token holders, and the savings rates are no longer at 0%. The Maker side is taken from the `dss` core contracts, the LitePSM, the USDS repository and the archived executive spells of [Sky](https://github.com/sky-ecosystem); the Single-Collateral DAI code is not part of these sources, so statements about it are marked as general knowledge.

### Versions referred to

| Name | Protocol | Date (source) | Main features used below |
| ---- | -------- | ------------- | ------------------------ |
| SCD (Sai) | Maker | 2017 (general knowledge) | ETH only, global settlement |
| MCD (`dss` 1.0) | Maker | launch spell 2019-11-18 | several collateral types, stability fee per type (`Jug`), DSR (`Pot`), `Cat` + `Flip` English auctions, `Flap`/`Flop` auctions, `End` + ESM |
| PSM | Maker | spell 2020-12-20 | USDC ⇄ DAI at 1:1 |
| Liquidations 2.0 | Maker | `dss` tag `1.3.0` and first spell, 2021-04-19 | `Dog` + `Clipper` Dutch auctions, flash liquidation |
| LitePSM | Maker | spell 2024-07-25 | USDC ⇄ DAI from a pool of pre-minted DAI |
| Sky (USDS) | Maker | spell 2024-09-13 | USDS, sUSDS, DAI ⇄ USDS converter, SKY token |
| Current Sky configuration | Maker | `spells-mainnet` test config, 2026-11-09 | debt and Vow surplus auctions off, ESM threshold at its maximum, rates moved by SP-BEAM |
| Liquity V1 (LUSD) | Liquity | April 2021 | ETH only, no interest, Stability Pool, redemptions, Recovery Mode |
| Liquity V2 (BOLD) | Liquity | first launch 13 Jan 2025, redeployed May 2025 | WETH, wstETH, rETH branches, user-set rates, branch shutdown |

The Maker dates are explained in [Introduction to MakerDAO]({{site.url_complet}}/2023/11/21/makerdao/), which now has a section on each version.

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

Governance exists in every Maker version. Since the Sky upgrade (2024-09-13 spell) the voting token is SKY, and MKR can be converted into it. A voted spell waits behind a pause delay, 48 hours in the current configuration, before it runs; the "Mom" contracts let governance halt an oracle, a Clipper, a debt ceiling or the PSM without that delay.

In contrast, Liquity V1 has no governance at all. Its parameters (minimum collateral ratio, fee floors, liquidation reserve) are constants in immutable contracts with no admin key. The only values that move are the borrowing and redemption fees, which follow a formula driven by redemption volume and time, without any vote.

*Liquity V2:* a limited governance exists. LQTY stakers vote each week on how 25% of the interest paid by borrowers is distributed to liquidity initiatives. They cannot change any protocol parameter, since the core contracts remain immutable.

------

### 2. Collateral Approach

MakerDAO supports a multi-collateral system, allowing various ERC-20 tokens as collateral. While this provides flexibility, it introduces risks, as many tokens depend on issuers or are vulnerable to security exploits.

*Maker versions:* this is true since Multi-Collateral DAI (2019). Single-Collateral DAI accepted only ETH, like Liquity V1 (general knowledge). Since the PSM (2020, then the LitePSM in 2024), a large part of DAI and USDS is minted against USDC at 1:1, which adds a dependency on a centralised issuer.

Liquity V1 adopts a single-collateral approach, accepting only Ether (ETH) as collateral. This choice aligns with its belief in Ether as the most trustless, risk-free asset on the Ethereum network. By focusing on Ether, Liquity minimizes complexity and potential vulnerabilities.

*Liquity V2:* the BOLD stablecoin also accepts two liquid staking tokens (LSTs), Lido's wstETH and Rocket Pool's rETH, in addition to Ether. Each collateral has its own branch of contracts, Stability Pool and parameters, so a problem with one LST does not mix collateral across branches. See the [Liquity V2 Whitepaper](https://liquity.gitbook.io/v2-whitepaper) and [How Liquity V2 Works]({{site.url_complet}}/2026/10/22/liquity-v2-bold-user-set-interest-rates/).

### 3. Decentralized Frontends

MakerDAO relies on centralized frontends, often hosted on specific servers, which could pose censorship risks. 

*Maker versions:* the Maker contracts themselves are permissionless in every version, so anyone can build an interface; the difference is that Maker has no on-chain mechanism that registers or rewards third-party frontends.

Liquity, on the other hand, supports a decentralized network of frontends. Anyone can run a frontend that interacts with the protocol, enhancing censorship resistance and decentralization. Additionally, Liquity V1 incentivizes frontend operators with rewards: the LQTY rewards of a Stability Pool deposit are split between the depositor and the frontend it was made through, at a rate the frontend chooses.

------

### 4. Stablecoin Redemption

Liquity’s stablecoin, LUSD, is fully redeemable against Ether at face value, ensuring a direct and transparent peg to the US dollar. This mechanism creates a hard price floor, as holders can arbitrage any deviation below $1 by redeeming LUSD for Ether.

See [docs.liquity.org - lusd-redemptions](https://docs.liquity.org/liquity-v1/faq/lusd-redemptions)

In contrast, MakerDAO’s DAI lacks direct redeemability for collateral. Instead, it employs indirect stability mechanisms, resulting in a soft peg that may be less resilient under extreme market conditions.

*Maker versions:* no Maker version lets a DAI holder redeem against vault collateral during normal operation; only an Emergency Shutdown pays DAI holders in collateral. Since the PSM (2020), however, DAI can be swapped for USDC at 1:1 plus the fee `tout`, and since the LitePSM (2024) this swap comes out of a pocket of USDC. This is a hard exit while the pocket holds USDC, but it is an exit into USDC, not into the vaults' collateral. USDS converts 1:1 to DAI, so it has the same exit.

*Liquity V2:* BOLD keeps a hard floor through redemptions, routed across branches and taken from the troves with the lowest interest rate first.

------

### 5. Interest-Free Loans

Liquity offers loans without recurring interest. Borrowers only pay a `one-time` issuance fee when opening a loan, and there are no ongoing costs. This allows users to keep their debt positions open indefinitely without accumulating additional charges.

MakerDAO applies a `stability fee`, which functions as an interest rate, accruing over time. This recurring cost can be a significant consideration for long-term borrowers.

*Maker versions:* Single-Collateral DAI already charged a stability fee. Since Multi-Collateral DAI it is set per collateral type in the `Jug` and accrues to every vault of the type at once. In the current configuration, the rates of many collateral types are moved by a rate-setter module (SP-BEAM) within bounds set by governance.

*Liquity V2:* loans are no longer interest-free. Each borrower chooses their own annual rate, between 0.5% and 250%, and can change it. Redemptions take collateral from the troves with the lowest rates first, so the rate also sets how exposed a borrower is to redemptions. The rate is set by the market of borrowers, not by governance as with Maker's stability fee.

See [Maker DAO archive - stability-fee](https://rya-sge.github.io/maker-dao-community-archive/faqs/stability-fee/)

------

### 6. Collateralization Ratios

MakerDAO’s minimum collateralization ratio for Ether is either 130% or 150%, depending on the specific parameters. Higher ratios provide a buffer but limit capital efficiency.

*Maker versions:* since Multi-Collateral DAI the ratio (`mat`) is set per collateral type, and ETH has several types. In the current configuration ETH-A is at 145%, ETH-B at 130%, ETH-C at 170% and WSTETH-A at 150%. The PSM collateral type uses 100%, because USDC is assumed to be worth one DAI.

Liquity’s system (V1) requires only a 110% minimum collateralization ratio, enabled by its innovative liquidation mechanism. This lower requirement increases capital efficiency while maintaining system stability. See [Liquity CR](https://www.liquity.org/features/collaterization-ratio)

*Liquity V2:* the minimum is 110% for ETH and 120% for wstETH and rETH.

------

### 7. Liquidation Mechanisms

MakerDAO utilizes an auction-based liquidation process, which can take up to six hours. This delay requires higher collateral buffers to account for potential price fluctuations during the auction.

*Maker versions:* this describes the `Cat` + `Flipper` English auctions of Multi-Collateral DAI from 2019 to 2021, in which bidders raise the DAI bid, then lower the collateral they accept; the code defaults are 3 hours per bid and 2 days at most. Liquidations 2.0 (2021) replaced them with `Dog` + `Clipper` **Dutch auctions**. The price starts above market and falls step by step, and the first buyer at an acceptable price takes the lot in one transaction. The buyer can sell the collateral within the same transaction through `clipperCall`, so a liquidation no longer requires capital or bidding rounds. For ETH-A the price falls by 1% every 90 seconds, and the auction is reset after 2 hours or after a 55% drop. Two delays remain: the oracle security module publishes prices one period late, and the `hole`/`Hole` limits can make liquidations wait in a crash.

Liquity employs instantaneous liquidations. A stability pool pre-funds the repayment of under-collateralized debt, ensuring immediate resolution. This approach eliminates the need for auctions, reduces risks from price volatility, and enhances capital efficiency.

*Liquity V2:* the same model, with one Stability Pool per collateral branch.

------

### 8. Savings and Incentives

MakerDAO offers the `DAI Savings Rate (DSR)`, allowing users to earn interest on their DAI holdings. However, the rate is determined by human governance and is currently set at 0%.

*Maker versions:* the DSR exists since Multi-Collateral DAI (`Pot`); Single-Collateral DAI had none. The 0% figure dates from the talk and is no longer current. Since the Sky upgrade, USDS holders also have sUSDS, an ERC-4626 token paid the Sky Savings Rate (6.25% at launch). In the current configuration both rates are moved by SP-BEAM within governance bounds of 0 to 30% for the DSR and 2 to 30% for the SSR. In every version, the savings rate is paid by minting DAI against the system's surplus.

Liquity does not have a direct savings feature but offers two alternative mechanisms: the Stability Pool and LQTY staking. The Stability Pool allows users to deposit LUSD and earn liquidation gains in Ether. Additionally, LQTY token holders can stake their tokens to earn a share of system fees, providing multiple avenues for rewards.

*Liquity V2:* the Stability Pool of each collateral branch receives 75% of the interest paid by that branch's borrowers, in addition to liquidation gains. It works as a savings product whose yield comes from borrowers rather than from a governance-set rate such as the DSR.

------

### 9. Secondary Token Role

MakerDAO relies on the MKR token as a lender of last resort. In extreme scenarios, MKR tokens can be minted and sold to recapitalize the system, potentially diluting existing holders.

> Personal note

This was indeed the case in 2020: a rapid price declines has provoked a $4 million shortfall on MakerDAO. In order to bring the system back to a healthy state, MKR tokens has been created and auctioned off to make up for the lost collateral value.

See [Messari - MakerDAO releases plans to recapitalize the protocol through MKR auction](https://messari.io/report/makerdao-releases-plans-to-recapitalize-the-protocol-through-mkr-auction)

*Maker versions:* the debt auctions (`Flop`) that mint MKR exist since Multi-Collateral DAI (2019). In the current configuration they are switched off (`vow_sump` at its maximum), as is the Vow's own surplus auction. Bad debt left by a liquidation now stays in the Vow and is absorbed only by the surplus buffer or by a governance decision, with no automatic dilution of SKY holders. Surplus leaves through the Kicker, which buys SKY on Uniswap V2.

Liquity avoids this approach by employing a redistribution mechanism. If the Stability Pool is insufficient to cover liquidations, debt is redistributed among remaining borrowers. This decentralized co-guarantor model eliminates the need for token dilution while maintaining system stability.

*Liquity V2:* redistribution remains, per branch, and no token is minted to cover losses.

------

### 10. Emergency Shutdown vs. Recovery Mode

MakerDAO employs an emergency shutdown mechanism to wind down the system in case of extreme under-collateralization. While effective, it results in the complete cessation of the protocol.

What happens during an Emergency Shutdown in Single-Collateral DAI (from the SCD FAQ)?

1. An emergency Shutdown stops CDP creation and freezes the Price Feed.
2. Collateral Claims are processed: After Emergency Shutdown is activated, a time period is needed to allow the processing of the proportional collateral claims of all CDP owners. After this processing is done, all CDP owners will be able to claim a fixed amount of ETH with their CDPs. Dai holders can access their collateral claims immediately.
3. Dai and CDP owners claim collateral: Each Dai holder and CDP owner can exchange their Dai and CDPs directly for a fixed amount of ETH that corresponds to the calculated value of their assets.

See [Maker DAO archive - Emergency Shutdown](https://rya-sge.github.io/maker-dao-community-archive/scd-faqs/emergency-shutdown/#what-is-an-emergency-shutdown)

*Maker versions:* in Multi-Collateral DAI the `End` contract runs the shutdown in nine steps. It freezes the system, fixes a price for each collateral type, cancels each vault's debt against its collateral, and lets DAI holders lock their DAI and redeem a share of every collateral type, net of the shortfall of under-collateralised vaults. The trigger has changed:

- From 2019, the Emergency Shutdown Module (ESM) let MKR holders trigger it by depositing a threshold of MKR, without a vote. The launch setup comes from general knowledge; the spells show a threshold of 300,000 MKR after 2024-07-25 and of 500,000 MKR after 2024-11-28.
- In the current configuration the ESM threshold is set to the maximum, so token holders can no longer trigger it. Shutdown is reachable only by a governance spell through `End.cage`.
- The LitePSM README states that it assumes shutdown is never called, so the USDC peg module is not designed for that path.

Liquity V1 uses a Recovery Mode when the total collateralization ratio drops below 150%. In that mode, a trove whose ratio is below the system's total ratio can be liquidated if the Stability Pool covers its whole debt (the borrower keeps collateral above 110% of the debt), and new borrowing must keep the system ratio from falling. The system returns to normal operation when the ratio recovers, without shutting down.

*Liquity V2:* Recovery Mode is removed, so a trove above the minimum ratio is never liquidated. Each collateral branch has a critical ratio (150% or 160%) below which borrowing that lowers the system ratio is refused, and a shutdown ratio (110% or 120%). Below the shutdown ratio, or if the branch's oracle fails, the branch shuts down permanently and fee-free "urgent" redemptions with a 2% bonus clear its debt. This is closer to Maker's emergency shutdown, but it applies to one collateral at a time rather than to the whole system.

------

### Conclusion

While both MakerDAO and Liquity aim to provide stablecoin solutions and DeFi lending, their approaches differ significantly in governance, collateral management, liquidation mechanisms, and system design. Liquity V1 replaces governance with fixed parameters and fee formulas, accepts only ETH and liquidates through the Stability Pool. Maker has moved in the other direction since the talk: Dutch auctions since 2021, a USDC exit through the PSM, USDS and sUSDS since 2024, and a configuration in which debt auctions are off and only governance can shut the system down. Liquity V2 has in turn borrowed from Maker, with interest rates and a per-branch shutdown, but keeps immutable contracts and redemptions.

## Mindmap

The mindmap below summarizes the article.

![Mindmap of the MakerDAO and Liquity versions and of the ten differences, grouped into governance, collateral, access, economics and risk management]({{site.url_complet}}/assets/article/blockchain/defi/2024-12-16-10-Key-Differences-Between-MakerDAO-and-Liquity-mindmap.png)

## Related articles

- [How Liquity V1 Works - LUSD, Troves, the Stability Pool, Redemptions and Recovery Mode]({{site.url_complet}}/2026/10/22/liquity-v1-lusd-troves-stability-pool/)
- [How Liquity V2 Works - BOLD, User-Set Interest Rates, Redemption Routing and Branch Shutdown]({{site.url_complet}}/2026/10/22/liquity-v2-bold-user-set-interest-rates/)
- [Stablecoins Under MiCA — Asset-Referenced Tokens and E-Money Tokens (Titles III and IV)]({{site.url_complet}}/2026/09/17/mica-stablecoins-asset-referenced-tokens-e-money-tokens/)
- [How Polaris Works - pETH, the Power-Law Bonding Curve, Reserve Loans and pAsset Markets]({{site.url_complet}}/2026/10/21/polaris-peth-bonding-curve-passets/)
