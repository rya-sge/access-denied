---
layout: post
title: "USD₮0 - Omnichain Fungible Token"
date:   2025-11-07
lang: en
locale: en-GB
categories: blockchain ethereum 
tags: defi stablecoin
description: USD₮0 is an Omnichain Fungible Token (OFT) built on LayerZero, enabling cross-chain transfers of USDT. Learn how USD₮0 works, its architecture, and the Legacy Mesh that connects existing USDT networks.
image: /assets/article/blockchain/defi/ustd0/usdt0-diagram.png
isMath: false
---

USD₮0 is an **Omnichain Fungible Token (OFT)** designed to operate seamlessly across multiple blockchains. 

Built on the OFT standard from LayerZero, USD₮0 enables cross-chain transfers while maintaining **full backing with USD₮**. 

Its architecture separates token functionality from messaging, allowing consistent behavior across all supported chains and enabling independent upgrades of its components.

------

## How USD₮0 Works

USD₮0 operates using a **lock-and-mint mechanism** supported by the OFT standard. This ensures transparency, full asset backing, and smooth cross-chain operations.

1. **Locking Assets:**
    USD₮ is locked in a smart contract on Ethereum Mainnet.
2. **Minting on Destination Chains:**
    Equivalent USD₮0 tokens are minted on the target chain. Each USD₮0 token is backed 1:1 by the locked USD₮, maintaining transparency and trust.
3. **Seamless Cross-Chain Transfers:**
    An advanced messaging layer enables efficient, cost-effective transfers between chains. Unlike bridges relying on fragmented liquidity, USD₮0 allows users to move tokens quickly and reliably.
4. **Redemption:**
    USD₮0 can be redeemed by unlocking the corresponding USD₮ on Ethereum, maintaining a consistent relationship between minted and locked assets.

From the [documentation](https://docs.usdt0.to/technical-documentation/developer): 

![usdt0-diagram]({{site.url_complet}}/assets/article/blockchain/defi/ustd0/usdt0-diagram.png)

------

## Role of the OFT Model

USD₮0 uses the **Omnichain Fungible Token (OFT) standard** to manage cross-chain operations. The OFT model provides a universal framework for messaging and token management, offering several advantages:

- **Unified Liquidity Management:** Reduces fragmentation by efficiently managing liquidity across chains.
- **Security:** Transactions are verified through decentralized oracles and relayers, ensuring integrity.
- **Scalability:** Supports expansion to new blockchains, enabling integration with emerging ecosystems.
- **Operational Efficiency:** Removes the need for intermediary bridges or wrapped tokens, reducing complexity and overhead.

By leveraging OFT, USD₮0 enables reliable cross-chain stablecoin functionality while maintaining asset backing and interoperability.

------

## Architecture Overview

USD₮0’s architecture separates **token logic** from **cross-chain messaging**, allowing each to be upgraded independently.

### Core Components

1. **OAdapterUpgradeable (Ethereum)**
   - Handles OFT functionality on Ethereum.
   - Locks and unlocks USD₮ for cross-chain transfers.
2. **OUpgradeable (Other Chains)**
   - Implements OFT for non-Ethereum chains.
   - Controls minting and burning of USD₮0.
3. **TetherTokenOFTExtension (Other Chains)**
   - Provides mint and burn interfaces for OFT transfers.

### Component Interaction

- **Ethereum → Chain B:** USD₮ locked on Ethereum triggers minting of USD₮0 on Chain B.
- **Chain B → Chain A:** USD₮0 burned on Chain B triggers minting on Chain A.
- **Chain A → Ethereum:** USD₮0 burned on Chain A allows USD₮ to be unlocked on Ethereum.

This flow ensures **consistent supply across all chains**.

------

## Cross-Chain Transfers: The Legacy Mesh

To support legacy USDT deployments, USD₮0 uses the **Legacy Mesh**, a cross-chain liquidity network that connects pre-existing USDT on multiple blockchains with the USD₮0 omnichain ecosystem.

### What is the Legacy Mesh?

The Legacy Mesh uses a **hub-and-spoke model** to move liquidity between networks that do not natively support USD₮0. Key chains include:

- **Ethereum:** native USD₮ via ERC-20
- **Tron:** native USD₮ via TRC-20
- **TON:** native USD₮ via TON token format
- **Arbitrum:** central USD₮0 hub
- **Solana:** native USD₮ via SPL-20
- **CELO:** native USD₮ via ERC-20

Liquidity pools facilitate **two-way conversions** between USD₮ and USD₮0, allowing users to move value across previously siloed networks without relying on wrapped or synthetic tokens. The network can expand over time to include additional chains, further unifying the stablecoin experience.

------

## Security

USD₮0 uses a **dual-DVN security configuration**:

1. **LayerZero DVN**
2. **USDT0 DVN**

Both networks must verify the payload hash before a cross-chain message is executed. This ensures **independent verification** and enhances security for cross-chain transfers.

More details: [LayerZero DVN Documentation](https://docs.layerzero.network/v2/home/modular-security/security-stack-dvns)

------

## Deployments

USD₮0 is deployed across multiple chains. Some key deployments include:

| Chain        | Component           | Address                                                      |
| ------------ | ------------------- | ------------------------------------------------------------ |
| Ethereum     | OAdapterUpgradeable | [`0x6C96dE32CEa08842dcc4058c14d3aaAD7Fa41dee`](https://etherscan.io/address/0x6C96dE32CEa08842dcc4058c14d3aaAD7Fa41dee) |
| Arbitrum One | OUpgradeable /      | [0x14E4A1B13bf7F943c8ff7C51fb60FA964A298D92](https://arbiscan.io/address/0x14E4A1B13bf7F943c8ff7C51fb60FA964A298D92) |
| Polygon PoS  | OUpgradeable        | [0x6BA10300f0DC58B7a1e4c0e41f5daBb7D7829e13](https://polygonscan.com/address/0x6BA10300f0DC58B7a1e4c0e41f5daBb7D7829e13) |
| Optimism     | OUpgradeable        | [`0xF03b4d9AC1D5d1E7c4cEf54C2A313b9fe051A0aD`](https://optimistic.etherscan.io/address/0xF03b4d9AC1D5d1E7c4cEf54C2A313b9fe051A0aD) |
| Berachain    | OUpgradeable        | OUpgradeable: [0x3Dc96399109df5ceb2C226664A086140bD0379cB](https://berascan.com/address/0x3Dc96399109df5ceb2C226664A086140bD0379cB) |

Full deployments also include Ink, Unichain, Corn, Sei, Flare, HyperEVM, Rootstock, XLayer, and Plasma.

See [docs.usdt0.to - usdt0-deployments](https://docs.usdt0.to/technical-documentation/developer/usdt0-deployments)

------

USD₮0 combines **cross-chain interoperability, consistent asset backing, and security** to provide a unified framework for moving USD₮ across multiple blockchains, while maintaining a connection to legacy USDT liquidity through the Legacy Mesh.