---
layout: post
title: "USD₮0 - Omnichain Fungible Token"
date:   2025-11-07
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: blockchain ethereum 
tags: defi stablecoin
description: "USD₮0, an Omnichain Fungible Token (OFT) built on LayerZero for cross-chain USDT transfers: its architecture and the Legacy Mesh linking USDT networks."
image: /assets/article/blockchain/defi/ustd0/usdt0-diagram.png
isMath: false
---

USD₮0 is an **Omnichain Fungible Token (OFT)** designed to operate seamlessly across multiple blockchains. 

Built on the OFT standard from LayerZero, USD₮0 enables cross-chain transfers while maintaining **full backing with USD₮**. 

Its architecture separates token functionality from messaging, allowing consistent behavior across all supported chains and enabling independent upgrades of its components.

## What you need to know first

USD₮0 is a LayerZero application, and the article relies on a few cross-chain and smart-contract mechanisms that it names without explaining.

- **Lock-and-mint and burn-and-mint bridging**: a lock-and-mint bridge locks the original token on the source chain and mints a representation on the destination chain; a burn-and-mint transfer destroys the token on the source chain and mints the same amount on the destination. USD₮0 combines both: USD₮ is locked on Ethereum, and USD₮0 is burned and minted between the other chains; see [Cross-Chain Bridge Threat Model - Assets, Trust Boundaries, STRIDE and Threat Register]({{site.url_complet}}/2026/07/31/cross-chain-bridge-threat-model/).
- **LayerZero messaging**: an application contract on one chain sends a message through the LayerZero endpoint, and the message is executed on the destination chain once the verifiers configured by the application, the DVNs, have attested to its payload hash. The OFT standard is a token built on this messaging; see [How LayerZero V2 Works - Endpoint, DVNs, Executors, OFT and the Kelp DAO Lesson]({{site.url_complet}}/2026/11/16/layerzero-v2-architecture/).
- **Upgradeable proxy contracts**: an upgradeable contract keeps its address and storage in a proxy and delegates execution to an implementation contract that its administrator can replace. The `Upgradeable` suffix of `OAdapterUpgradeable` and `OUpgradeable` refers to this pattern, which is what lets the token and messaging components be upgraded independently; see [Programming proxy contracts with OpenZeppelin | Summary]({{site.url_complet}}/2022/10/31/proxy-contract-summary/).
- **Liquidity-based bridging**: instead of minting, a bridge can hold pools of a token on each chain and pay the user out of the destination pool. The Legacy Mesh works this way for the chains where USD₮ already exists natively and cannot be minted by the OFT contracts.
- **Block confirmations and reorganisations**: a block that has just been produced can still be replaced if the chain reorganises, so a verifier waits for a number of later blocks before treating a source-chain event as final. The "reorg-safe confirmations" that LayerZero recommends are this waiting period.
- **RPC nodes**: off-chain services, a DVN among them, read the state of a chain through the RPC interface of a node. If that node returns false data, the service attests to events that never happened, which is how the Kelp DAO attack in the Security section worked.

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
- **Solana:** native USD₮ via the SPL Token program
- **CELO:** native USD₮ via ERC-20

Liquidity pools facilitate **two-way conversions** between USD₮ and USD₮0, allowing users to move value across previously siloed networks without relying on wrapped or synthetic tokens. The network can expand over time to include additional chains, further unifying the stablecoin experience.

------

## Security

USD₮0 uses a **dual-DVN security configuration**:

1. **LayerZero DVN**
2. **USDT0 DVN**

Both networks must verify the payload hash before a cross-chain message is executed. This ensures **independent verification** and enhances security for cross-chain transfers.

More details: [LayerZero DVN Documentation](https://docs.layerzero.network/v2/home/modular-security/security-stack-dvns)

### Why the DVN configuration matters

In LayerZero V2 the endpoint does not decide whether a message is genuine. Each application sets its own security stack per pathway: a receive library, a list of required DVNs, an optional set with a threshold, and a number of block confirmations. A packet verifies once every required DVN and the optional threshold have attested. [How LayerZero V2 Works]({{site.url_complet}}/2026/11/16/layerzero-v2-architecture/) covers this mechanism, the message lifecycle and the OFT adapter in detail.

Two properties of that configuration bear on a token like USD₮0:

- **Defaults belong to LayerZero Labs.** A configuration field left unset inherits the endpoint owner's default for that pathway, field by field. LayerZero's [May 2026 update](https://layerzero.network/blog/an-overdue-apology) states that an application on defaults is fully reliant on the LayerZero Labs multisig, and recommends pinning every configuration, setting reorg-safe confirmations and using at least two DVNs, three to five being better.
- **The adapter holds all the backing.** On Ethereum, USD₮0's `OAdapterUpgradeable` locks USD₮ for every other chain, so a single forged inbound message that passes verification can unlock from that one contract.

The Kelp DAO incident of 18 April 2026 shows what a single verifier allows. Kelp's rsETH pathway from Unichain to Ethereum used a 1-of-1 DVN configuration with the LayerZero Labs DVN as the only verifier. Attackers poisoned the RPC nodes that DVN read and forced a failover to them with a denial-of-service attack on its external provider; the DVN attested to a burn that never happened, and the Ethereum adapter released 116,500 rsETH, about $292M ([LayerZero Labs KelpDAO Incident Report](https://layerzero.network/blog/layerzero-labs-kelpdao-incident-report)). Since then the LayerZero Labs DVN no longer serves 1/1 configurations.

USD₮0's dual-DVN setup requires two parties to attest, the minimum LayerZero recommends. The configuration deployed on each pathway was not read on chain for this update.

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

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **USD₮** | Tether's stablecoin, issued natively on chains such as Ethereum, Tron, TON and Solana; it backs USD₮0 one to one. |
| **USD₮0** | An Omnichain Fungible Token backed 1:1 by USD₮ locked on Ethereum, minted and burned on the other supported chains. |
| **Omnichain Fungible Token (OFT)** | LayerZero's token standard for moving one fungible token across several chains through LayerZero messages while keeping a consistent total supply. |
| **Lock-and-mint** | The mechanism in which USD₮ is locked in a contract on Ethereum and the same amount of USD₮0 is minted on the destination chain. |
| **Redemption** | The reverse operation, in which USD₮0 is burned and the corresponding USD₮ is unlocked on Ethereum. |
| **`OAdapterUpgradeable`** | The USD₮0 contract on Ethereum that handles OFT functionality and locks and unlocks USD₮; it holds the backing for every other chain. |
| **`OUpgradeable`** | The USD₮0 OFT contract on non-Ethereum chains, which controls the minting and burning of USD₮0. |
| **`TetherTokenOFTExtension`** | The token contract on the other chains that exposes the mint and burn interfaces used by OFT transfers. |
| **Legacy Mesh** | A cross-chain liquidity network, built as a hub and spoke around Arbitrum, that connects pre-existing USD₮ deployments to USD₮0 through liquidity pools. |
| **Hub-and-spoke model** | A topology in which every chain connects to a central hub chain rather than to every other chain; Arbitrum is the hub of the Legacy Mesh. |
| **Decentralized Verifier Network (DVN)** | A verifier that attests to the payload hash of a LayerZero message before it can be executed on the destination chain. |
| **Dual-DVN configuration** | USD₮0's security setup, in which both the LayerZero DVN and the USDT0 DVN must verify each message. |
| **Security stack** | The per-pathway LayerZero configuration of an application: receive library, required DVNs, optional DVNs with a threshold, and block confirmations. |
| **Default configuration** | The values set by the endpoint owner, LayerZero Labs, that an application inherits for any field it leaves unset. |
| **1-of-1 DVN configuration** | A setup with a single verifier, as on the Kelp DAO rsETH pathway, where one compromised DVN is enough to forge a message. |

## Related articles

- [How LayerZero V2 Works - Endpoint, DVNs, Executors, OFT and the Kelp DAO Lesson]({{site.url_complet}}/2026/11/16/layerzero-v2-architecture/)
- [Cross-Chain Bridge Hacks - Ten Incidents, Five Failure Classes]({{site.url_complet}}/2026/07/31/cross-chain-bridge-hacks/)
- [Cross-chain tokens Standard (ERC-7281, xERC20) - Overview]({{site.url_complet}}/2025/05/07/cross-chain-token-overview/)
- [Cross-Chain Bridge Threat Model - Assets, Trust Boundaries, STRIDE and Threat Register]({{site.url_complet}}/2026/07/31/cross-chain-bridge-threat-model/)
- [Stablecoins Under MiCA — Asset-Referenced Tokens and E-Money Tokens (Titles III and IV)]({{site.url_complet}}/2026/09/17/mica-stablecoins-asset-referenced-tokens-e-money-tokens/)
