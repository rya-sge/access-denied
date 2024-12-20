---
layout: post
title: 10 Key Differences Between MakerDAO and Liquity
date:   2024-12-16
lang: en
locale: en-GB
categories: security cryptography
tags: tls mtls cloud
description: Mutual TLS (mTLS) is an extension of the standard TLS protocol which requires both the client and server to present and validate certificates, enabling mutual authentication.  
image: 
isMath: false
---



This article comes from a [presnetation video](https://www.youtube.com/watch?v=bXLTE-5BkhA) made by  Robert Lauko in 2021 to explain how Liquity differs from Maker DAO.

Since the video is rather old, it is possible that some information is no longer completely up to date. However, I found it very interesting to understand Liquity and the first version of MakerDAO (now [Sky](https://sky.money))

- A transcript has been generated with [NoteGPT](https://notegpt.io)
- A more formal article has been made with ChatGPT from this transcript
- Finally, I have perform a few addition and personal notes.

Here’s an exploration of the 10 key differences between MakerDAO and Liquity.

------

### **1. Governance**

MakerDAO operates on a human governance model, where key parameters like `interest rates` and `collateralization ratios` are adjusted through community votes. These votes require holding the Maker (MKR) token, which grants voting rights. However, challenges such as low voter turnout and the potential for manipulation, such as through flash loans, can affect the system's efficiency.

>  Personal note:

- In 2020, a protocol team uses a flashloan to pass one of their proposal, see [MakerDAO issues warning after a flash loan is used to pass a governance vote](https://www.theblock.co/post/82721/makerdao-issues-warning-after-a-flash-loan-is-used-to-pass-a-governance-vote).
- Sky Money, the new version of MakerDao uses a specific smart contract `ds-chief`to prevent MKR locked for voting from being used in the same block as the deposit.  See [developers.sky.money - governance-flash-loan-attacks](https://developers.sky.money/security/security-measures/security-mechanisms#governance-flash-loan-attacks)

In contrast, Liquity employs a fully algorithmic governance system. Parameters like `fees` adjust automatically based on external inputs without human intervention. This ensures a more efficient and tamper-resistant governance structure, reducing risks associated with manual adjustments.

------

### **2. Collateral Approach**

MakerDAO supports a multi-collateral system, allowing various ERC-20 tokens as collateral. While this provides flexibility, it introduces risks, as many tokens depend on issuers or are vulnerable to security exploits.

Liquity adopts a single-collateral approach, accepting only Ether (ETH) as collateral. This choice aligns with its belief in Ether as the most trustless, risk-free asset on the Ethereum network. By focusing on Ether, Liquity minimizes complexity and potential vulnerabilities.

------

### **3. Decentralized Frontends**

MakerDAO relies on centralized frontends, often hosted on specific servers, which could pose censorship risks. 

Liquity, on the other hand, supports a decentralized network of frontends. Anyone can run a frontend that interacts with the protocol, enhancing censorship resistance and decentralization. Additionally, Liquity incentivizes frontend operators with rewards, encouraging broader adoption and usage.

------

### **4. Stablecoin Redemption**

Liquity’s stablecoin, LUSD, is fully redeemable against Ether at face value, ensuring a direct and transparent peg to the US dollar. This mechanism creates a hard price floor, as holders can arbitrage any deviation below $1 by redeeming LUSD for Ether.

In contrast, MakerDAO’s DAI lacks direct redeemability for collateral. Instead, it employs indirect stability mechanisms, resulting in a soft peg that may be less resilient under extreme market conditions.

------

### **5. Interest-Free Loans**

Liquity offers loans without recurring interest. Borrowers only pay a `one-time` issuance fee when opening a loan, and there are no ongoing costs. This allows users to keep their debt positions open indefinitely without accumulating additional charges.

MakerDAO applies a `stability fee`, which functions as an interest rate, accruing over time. This recurring cost can be a significant consideration for long-term borrowers.

------

### **6. Collateralization Ratios**

MakerDAO’s minimum collateralization ratio for Ether is either 130% or 150%, depending on the specific parameters. Higher ratios provide a buffer but limit capital efficiency.

Liquity’s system requires only a 110% minimum collateralization ratio, enabled by its innovative liquidation mechanism. This lower requirement increases capital efficiency while maintaining system stability.

------

### **7. Liquidation Mechanisms**

MakerDAO utilizes an auction-based liquidation process, which can take up to six hours. This delay requires higher collateral buffers to account for potential price fluctuations during the auction.

Liquity employs instantaneous liquidations. A stability pool pre-funds the repayment of under-collateralized debt, ensuring immediate resolution. This approach eliminates the need for auctions, reduces risks from price volatility, and enhances capital efficiency.

------

### **8. Savings and Incentives**

MakerDAO offers the `DAI Savings Rate (DSR)`, allowing users to earn interest on their DAI holdings. However, the rate is determined by human governance and is currently set at 0%.

Liquity does not have a direct savings feature but offers two alternative mechanisms: the Stability Pool and LQTY staking. The Stability Pool allows users to deposit LUSD and earn liquidation gains in Ether. Additionally, LQTY token holders can stake their tokens to earn a share of system fees, providing multiple avenues for rewards.

------

### **9. Secondary Token Role**

MakerDAO relies on the MKR token as a lender of last resort. In extreme scenarios, MKR tokens can be minted and sold to recapitalize the system, potentially diluting existing holders.

> Personal note

This was indeed the case in 2020: a rapid price declines has provoked a $4 million shortfall on MakerDAO. In order to bring the system back to a healthy state, MKRhas been created and auctioned off to make up for the lost collateral value.

See [Messari - MakerDAO releases plans to recapitalize the protocol through MKR auction](https://messari.io/report/makerdao-releases-plans-to-recapitalize-the-protocol-through-mkr-auction)

Liquity avoids this approach by employing a redistribution mechanism. If the Stability Pool is insufficient to cover liquidations, debt is redistributed among remaining borrowers. This decentralized co-guarantor model eliminates the need for token dilution while maintaining system stability.

------

### **10. Emergency Shutdown vs. Recovery Mode**

MakerDAO employs an emergency shutdown mechanism to wind down the system in case of extreme under-collateralization. While effective, it results in the complete cessation of the protocol.

Liquity uses a recovery mode that temporarily relaxes liquidation conditions when the total collateralization ratio drops below 150%. This mode allows the system to stabilize and return to normal operation without shutting down, ensuring continuous functionality.

------

### **Conclusion**

While both MakerDAO and Liquity aim to provide stablecoin solutions and DeFi lending, their approaches differ significantly in governance, collateral management, liquidation mechanisms, and system design. Liquity’s emphasis on algorithmic governance, single collateralization, and instantaneous liquidations offers a fresh perspective, appealing to users seeking a more efficient and decentralized protocol.