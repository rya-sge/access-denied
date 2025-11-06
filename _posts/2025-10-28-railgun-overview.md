---
layout: post
title: "RAILGUN: Privacy Infrastructure for DeFi"
date:   2025-10-28
lang: en
locale: en-GB
categories: blockchain ethereum zkp
tags: railgun zk-snark zeroknwoledgeproof
description: RAILGUN brings full privacy to DeFi using zk-SNARK cryptography, shielding senders, recipients, and tokens for untraceable blockchain transactions.
image: /assets/article/blockchain/defi/railgun/railgun-mindmap.png
isMath: false
---

RAILGUN is a privacy system built on Ethereum and other EVM-compatible blockchains. It introduces a suite of smart contracts that shield user activity — making **sender**, **recipient**, **token type**, and **amount** completely private — without sacrificing composability or smart contract functionality.

RAILGUN is a privacy system built on Ethereum and other EVM-compatible blockchains. It introduces a suite of smart contracts that shield user activity — making sender, recipient, token type, and amount completely private — without sacrificing composability or smart contract functionality.

Unlike mixers or simple transaction obfuscation tools, RAILGUN enables users to interact privately with decentralized finance (DeFi) protocols while maintaining compatibility with existing ERC-20, ERC-721, and ERC-1155 tokens.
 This is achieved through a combination of **zk-SNARK cryptography**, **Merkle Tree–based state management**, and **community broadcasters** that mask on-chain identities.

> Warning: this article is still in draft state and its content is still mainly taken from the [documentation](https://docs.railgun.org/wiki) summarized with the help of ChatGPT. Its content should become more personal later.

[TOC]



------

## Core Architecture

### Private Balances and Privacy Set

The foundation of RAILGUN is its **Private Balance system**, which holds user assets within encrypted smart contract states.
 These balances are referred to as a **privacy set** — a pool of shielded assets where any transaction could have originated from any participant in that pool.

#### Privacy Factors

The strength of privacy depends on factors such as:

- The total number of unique users and shielded transactions
- Total Value Locked (TVL) in the smart contracts
- The transaction and trading volume within RAILGUN

A larger and more active privacy set creates greater obfuscation, as interactions are statistically less likely to be traced back to a specific user or token.

Common tokens like **USDC** or **DAI** provide greater anonymity due to higher transaction density compared to niche assets.

------

## Zero-Knowledge Cryptography in RAILGUN

RAILGUN’s privacy guarantees are anchored by **zk-SNARKs (Zero-Knowledge Succinct Non-Interactive Arguments of Knowledge)**.

You can find more details about zk-SNARK in my article [Understanding zk-SNARK: A Deep Dive into Zero-Knowledge Proofs](https://rya-sge.github.io/access-denied/2025/07/29/zk-snark-overview/)

These allow a prover (user) to demonstrate ownership of tokens and permission to spend them without revealing any identifying details. The proof’s compactness and efficiency make it suitable for on-chain verification, enabling private yet fully verifiable state changes.

### Elliptic Curve Cryptography

RAILGUN employs elliptic curve cryptography (ECC) to reduce key size and improve proof efficiency.
 It uses the **Groth16** zk-SNARK protocol — the same proving system that powered Zcash’s early shielded transactions.

The circuits operate on elliptic curve pairings (EIP-197 and EIP-198) allowing proofs to be verified by Ethereum smart contracts directly.

------

### Circuit Design

The RAILGUN system is built on **54 zk-SNARK circuits**, each supporting different transaction types and input/output combinations.
 Each circuit is parameterized by the number of UTXO inputs and outputs.

Examples:

- **1 → 2**: Splitting one note into two recipients.
- **7 → 2**: Merging seven inputs and sending to two destinations.
- **5 → 1**: Multi-token send or swap operations.

This modular design allows RAILGUN to efficiently handle:

- Private swaps with variable liquidity.
- Multi-token sends.
- NFT shielding and DeFi composability (e.g., Uniswap v3 LP NFTs).

The circuit framework provides composability across protocols — enabling, for instance, a private Uniswap v3 liquidity position represented by a shielded LP NFT.



![railgun-circuit]({{site.url_complet}}/assets/article/blockchain/defi/railgun/railgun-circuit.png)

------

### Trusted Setup Ceremony (Groth16)

RAILGUN’s zk-SNARK proofs use the **Groth16** proving system, known for compact proofs and efficient on-chain verification.
Each circuit requires a **trusted setup ceremony** to generate a *Common Reference String (CRS)* )**, generated via the **Perpetual Powers of Tau ceremony, used for both proof generation and verification.

#### The Perpetual Powers of Tau

RAILGUN participated in the **Perpetual Powers of Tau** ceremony — an open, multi-party computation where anyone can contribute entropy.

- Security is ensured as long as one participant destroys their private randomness (“toxic waste”).
- New ceremonies are conducted whenever RAILGUN upgrades or introduces new circuits

## Architecture

### Merkle Trees, UTXOs, and Nullifiers

RAILGUN tracks private token ownership through an internal **Merkle Tree** of **encrypted UTXOs (Unspent Transaction Outputs)**.

When a user spends tokens:

- The protocol validates that each UTXO is unspent using **Nullifiers** (hashes derived from the Spending Key).
- Each transaction updates the Merkle Tree Root, ensuring global consistency.
- Nullifiers prevent double-spends without linking back to specific users or transactions.
- Ownership proofs are provided through zk-SNARKs, ensuring the system can verify valid spends without revealing identities or values.

This model mirrors Bitcoin’s UTXO structure — but with full zero-knowledge encryption.

![railgun-merkle-tree]({{site.url_complet}}/assets/article/blockchain/defi/railgun/railgun-merkle-tree.png)

------

### Shielding and Unshielding

- **Shielding** transfers tokens from the public blockchain (0x address) into the private pool (0zk).
- **Unshielding** reverses the process, sending tokens back to a public address.

Both rely on RAILGUN’s `shield()` and `transact()` smart contract functions, which leverage Poseidon hashing and zk-SNARK validation.
 While shielding and unshielding are visible on-chain, the internal transfers remain fully confidential.

You can find more information about the Poseidon hash function in my article: [Poseidon Hash Function - Overview](https://rya-sge.github.io/access-denied/2025/05/27/poseidon-hash-function-overview/)

------

### Privacy in Action

Within RAILGUN, users can:

- Swap tokens privately (via Railway DEX or other integrations)
- Provide liquidity to DeFi protocols
- Send or receive funds without exposing wallet links
- Privately trade or auction NFTs

Each transaction increases the **“noise”** of the privacy set, benefiting all participants — a concept known as **privacy amplification**.



![railgun-flow]({{site.url_complet}}/assets/article/blockchain/defi/railgun/railgun-flow.png)

------

## Broadcasters and Gas Abstraction

To further obfuscate user identities, RAILGUN introduces **Broadcasters** — independent nodes that submit transactions on behalf of users.

When a private transaction occurs:

- The sender encrypts it and routes it through a Broadcaster.
- The Broadcaster pays the network gas fee and relays the transaction on-chain.
- To external observers, the transaction appears to originate from the Broadcaster, not the actual user.

Broadcasters communicate with clients via the **Waku** decentralized messaging protocol, ensuring metadata privacy and censorship resistance.

Notably, users can pay gas in **any token**, thanks to RAILGUN’s **meta-transaction system** — enabling “gasless” DeFi interactions.

Broadcasters never see transaction contents — they only cover gas costs and forward encrypted data for confirmation on-chain.

------

## Wallets, Keys, and Security

Each RAILGUN wallet consists of:

- A **public 0x address** for standard blockchain operations
- A **private 0zk address** for shielded transactions

### Key Types

1. **Spending Key** – Used to generate zk proofs and authorize private transactions (built on the Baby Jubjub curve).
2. **Viewing Key** – Enables selective read-only access for auditing or compliance purposes (Ed25519 curve).

Viewing keys can be scoped by block range, allowing for transparent yet privacy-preserving reporting (e.g., for taxation).

## Summary

------

### Summary Table: RAILGUN vs Other Confidential Systems

| **Feature**                             | **RAILGUN**                                 | **Zcash**                   | **Monero**                     | **Tornado Cash**                                             |
| --------------------------------------- | ------------------------------------------- | --------------------------- | ------------------------------ | ------------------------------------------------------------ |
| **Base Layer**                          | Ethereum (and other EVM chains)             | Zcash blockchain            | Monero blockchain              | Ethereum                                                     |
| **Privacy Method**                      | zk-SNARKs (Groth16)                         | zk-SNARKs (Sapling)         | RingCT + stealth addresses     | zk-SNARKs (Mixer Model)                                      |
| **Architecture**                        | Smart contract-based DeFi layer             | L1 protocol                 | L1 protocol                    | Smart contract mixer                                         |
| **UTXO Model**                          | Private Merkle Tree UTXOs                   | Native UTXO model           | Native UTXO model              | N/A (pool-based deposits)                                    |
| **Private Smart Contract Interactions** | &#x2611; (DeFi composability)               | &#x2612;                    | &#x2612;                       | &#x2612;                                                     |
| **Supported Assets**                    | Any ERC-20, ERC-721, ERC-1155               | Native ZEC only             | Native XMR only                | Supported ERC-20 only                                        |
| **Broadcasters (Relayers)**             | &#x2611;decentralized Broadcaster network   | &#x2612;                    | &#x2612;                       | Interaction directly on the smart contracts or through Centralized front-end/relayers (in some cases) |
| **Gas Payment Options**                 | Any token (meta-transactions)               | N/A                         | N/A                            | ETH only                                                     |
| **Viewing Key System**                  | &#x2611;<br />Scoped and selective          | &#x2611;<br />Viewing keys  | &#x2612;                       | &#x2612;                                                     |
| **NFT Privacy Support**                 | &#x2611;                                    | &#x2612;                    | &#x2612;                       | &#x2612;                                                     |
| **Trusted Setup**                       | &#x2611;<br />Perpetual Powers of Tau       | &#x2611;<br />Powers of Tau | &#x2612;<br />No trusted setup | &#x2611; <br /> Tornado setup                                |
| **Main Use Case**                       | Private DeFi, swaps, LP, transfers          | Private payments            | Private payments               | Simple anonymization of transfers                            |
| **Decentralization Level**              | High – Smart contract & broadcaster network | Protocol-level              | Protocol-level                 | Contract-based (limited governance)                          |

------

### Mindmap



![railgun-mindmap.png]({{site.url_complet}}/assets/article/blockchain/defi/railgun/railgun-mindmap.png)

## Conclusion

RAILGUN is a privacy protocol that applies zero-knowledge cryptography to decentralized finance (DeFi) workflows. By combining **zk-SNARK** circuits, meta-transaction gas abstraction, and private smart contract composability, it offers a framework for conducting transactions and interactions on-chain with enhanced confidentiality.

While earlier privacy systems such as Zcash and Monero focus primarily on shielding payment data, RAILGUN extends similar principles to a broader range of **DeFi** activities — including token swaps, lending, liquidity provision, and NFT management — while operating directly on Layer 1 networks.

## Reference

- [Railgun - Wiki](https://docs.railgun.org/wiki)
- ChatGPT with the following input: "Here is the documentation of Railgun. Write me a technical article about it. At the end I want a summary tab. provide me also a summary tab with other confidential system such as Zcash, monero or Tornado cash"