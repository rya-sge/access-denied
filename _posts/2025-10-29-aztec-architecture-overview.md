---
layout: post
title: "Aztec: A Privacy-First Layer 2 for Ethereum"
date:   2025-10-29
lang: en
locale: en-GB
categories: blockchain ethereum zkp
tags: zk aztec circuit
description: Aztec L2 enables private, composable smart contracts on Ethereum using zero-knowledge proofs and hybrid public/private state.
image: /assets/article/blockchain/aztec/aztec-mindmap.png
isMath: false
---

Ethereum’s transparency provides security and auditability but also makes all transactions, balances, and smart contract state publicly visible.

**[Aztec](https://aztec.network/)** offers a **privacy-focused Layer 2 (L2)** solution on Ethereum, supporting hybrid private and public state and execution. Developers can create smart contracts whose operations are verified using **zero-knowledge proofs (ZKPs)**.

In addition to scalability features found in other zk-rollups, Aztec introduces a **dedicated virtual machine (the AVM)** designed to handle privacy-preserving computations natively.

> Warning: this article is still in draft state and its content is still mainly taken from the [documentation](https://docs.aztec.network) summarized with the help of ChatGPT. Its content should become more personal later.

[TOC]

## Aztec Architecture Overview

At a high level, Aztec’s architecture comprises several key layers:

- **[Aztec.js](https://docs.aztec.network/dev_docs/aztecjs/)** – SDK for interacting with the network.
- **PXE (Private Execution Environment)** – Executes private functions client-side.
- **AVM (Aztec Virtual Machine)** – Executes public functions network-side.
- **Rollup Sequencer & Prover Network** – Aggregates transactions and produces ZK proofs.
- **Ethereum Bridge Contract** – Verifies rollup proofs on L1 and updates final state commitments.

**Transaction flow:**

1. A user constructs a transaction via `aztec.js`.
2. **Private functions** execute locally in the PXE.
3. PXE generates a **ZK proof** of correctness.
4. **Public functions** execute in the AVM.
5. The rollup sequencer batches transactions.
6. A rollup proof is verified on Ethereum.

This dual-environment model enables **composable transactions**—private and public logic can interact in a single pipeline without breaking confidentiality.

---

## Execution Model: Private and Public

Aztec defines two distinct execution domains:

| Type                  | Environment        | Privacy     | Description                                            |
| --------------------- | ------------------ | ----------- | ------------------------------------------------------ |
| **Private Execution** | Client-side (PXE)  | Encrypted   | Runs user-specific logic privately and outputs a proof |
| **Public Execution**  | Network-side (AVM) | Transparent | Runs verifiable state updates visible to all           |

Private execution **always precedes** public execution. This directional constraint ensures determinism and prevents privacy leaks—private functions can enqueue public calls, but not vice versa.

---

## State Model: Private and Public

Aztec maintains **two complementary state spaces**: Private and Public states

![aztec-private-public-state]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-private-public-state.png)

### Private State
- Represented by **UTXOs** called _notes_.
- Stored in an **append-only note hash tree**.
- **Nullifiers** mark notes as spent.
- Encrypted to ensure only recipients can view them.
- Provides unlinkable transactions and selective disclosure.

### Public State
- Stored in a **public Merkle tree**.
- Directly updated by the AVM.
- Visible to all participants.
- Ideal for transparent global data (e.g., token supply, governance).

This **hybrid state model** allows developers to combine private and public logic—for instance, a private lending protocol interacting with a public liquidity pool.

---

## Core Components

### Private Execution Environment (PXE)

The **PXE** is the user’s local runtime that:

- Executes private contract functions.
- Generates ZK proofs for correctness.
- Manages encryption keys and notes.
- Provides scoped APIs for dapps and wallets.
- Synchronizes with the network for note discovery.

It acts as a **confidential sandbox**. Dapps can only access PXE data they’re authorized for, ensuring strong privacy boundaries between contracts and accounts.

### Aztec Virtual Machine (AVM)

The **AVM** executes **public contract functions**.  
It mirrors the EVM in design but extends it for Aztec’s privacy architecture:

- Custom instruction sets for hybrid execution.
- Deterministic call graph resolution.
- Proof-friendly opcode semantics.

PXE and AVM are **logically disconnected**; data passes only via proofs, preserving end-to-end privacy.

### Noir

**[Noir](https://noir-lang.org/)** is Aztec’s domain-specific language for writing zero-knowledge circuits.  
It allows developers to express private logic succinctly and compile it into constraint systems compatible with Aztec’s proving stack.

Noir is **universal**—circuits written in Noir can be verified on Aztec, other zk-rollups, or standalone applications.

### Circuits

Aztec’s privacy guarantees are enforced cryptographically through circuit constraints:

- **Hidden function calls:** Execution logic is never revealed.
- **Encrypted state updates:** Commitments replace cleartext writes.
- **Nullifier checks:** Prevent double-spending without revealing linkage.
- **UTXO anonymity:** Inputs and outputs are unlinkable.

Unlike Ethereum, where validators replay transactions, Aztec validators only verify **succinct proofs**, ensuring confidentiality and scalability simultaneously.

Aztec’s protocol-level security is enforced by a set of circuits:

| Circuit              | Function                                           |
| -------------------- | -------------------------------------------------- |
| **Kernel Circuit**   | Validates individual transactions                  |
| **Rollup Circuit**   | Batches multiple kernel proofs                     |
| **Squisher Circuit** | Compresses rollup proofs for Ethereum verification |

These circuits ensure:

- Hidden execution of private functions.
- Valid note creation and nullification.
- Correct rollup aggregation.
- Efficient L1 verification using Fflonk proofs.

---

## Accounts and Keys

Every Aztec account is a **smart contract**.  
This enforces **account abstraction (AA)** natively—authentication logic, fee models, and nonce schemes are all programmable.

Each account has **three key pairs**:

| Key Type                 | Purpose                              |
| ------------------------ | ------------------------------------ |
| **Nullifier Key**        | Generates nullifiers for spent notes |
| **Incoming Viewing Key** | Decrypts notes received              |
| **Outgoing Viewing Key** | Decrypts notes sent                  |

Developers can implement arbitrary signature verification schemes (e.g., Schnorr, BLS, multisig) directly in account contracts, allowing wallets to define unique security and UX models.

---

## Wallet Architecture & Transaction Lifecycle

Aztec wallets extend beyond simple key managers—they function as **proof generators** and **private state managers**.

### Transaction Lifecycle

![aztec-transaction-lifecycle]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-transaction-lifecycle.png)

1. The dapp calls a contract function via the wallet.
2. The wallet executes private logic in PXE.
3. ZK proofs are generated locally.
4. The transaction (proof + calldata) is submitted to the network.
5. Sequencer includes it in a rollup.
6. Ethereum verifies the rollup proof.

Wallets also manage:

- **Authwits (Authorization Witnesses):** For delegating permissions to other contracts.
- **Note tracking:** Syncing with on-chain commitments.
- **Fee management:** Private or paymaster-sponsored gas models.

---

## Developer Considerations

- **Composability:** Private ↔ Public contract calls are supported.
- **Data design:** Differentiate between private commitments and public variables.
- **Fee models:** Paymasters can sponsor or abstract fees.
- **Nonces:** Fully programmable at the contract level.
- **Optimization:** Proof generation is compute-heavy—efficient Noir coding is key.

---

## Summary

### Comparison with Other Privacy Systems

| Feature                  | **Aztec**                             | **Monero**         | **Zcash**           | **Tornado Cash**               | **Railgun**                 |
| ------------------------ | ------------------------------------- | ------------------ | ------------------- | ------------------------------ | --------------------------- |
| **Architecture**         | zk-Rollup (L2)                        | L1 blockchain      | L1 blockchain       | Smart contract mixer           | Smart contract + zk circuit |
| **Privacy Scope**        | Private + public smart contracts      | Full-chain privacy | Transaction privacy | Deposit/withdraw unlinkability | Transaction privacy         |
| **Composability**        | Full (private ↔ public)               | None               | Limited             | None                           | Limited                     |
| **Execution Model**      | PXE (private) + AVM (public)          | Native chain       | Native chain        | EVM-only                       | EVM-based                   |
| **Account Abstraction**  | Native                                | None               | None                | None                           | Partial                     |
| **Proving System**       | Custom circuits (Honk/Fflonk)         | Bulletproofs       | zk-SNARKs           | zk-SNARKs                      | zk-SNARKs                   |
| **Ethereum Integration** | Direct (L2 verified on L1)            | None               | None                | Native                         | Native                      |
| **Programmability**      | Noir smart contracts                  | Minimal            | Limited             | None                           | Moderate                    |
| **Privacy Guarantees**   | ZK composability of state + execution | Strong TX privacy  | TX privacy          | Mixer unlinkability            | TX privacy in EVM           |



---

### Summary Table

| Category                   | Description                                           |
| -------------------------- | ----------------------------------------------------- |
| **Objective**              | Programmable privacy on Ethereum                      |
| **Execution Environments** | PXE (private) + AVM (public)                          |
| **State Model**            | Hybrid (private UTXOs + public state)                 |
| **Core Circuits**          | Kernel, Rollup, Squisher                              |
| **Language**               | Noir                                                  |
| **Account Model**          | Full account abstraction                              |
| **Wallet Role**            | Proof generation, note management, authwit delegation |
| **Privacy Enforcement**    | ZK circuits for hidden state + execution              |
| **Ethereum Integration**   | Rollup proofs verified on L1                          |
| **Differentiator**         | Composable, programmable privacy for developers       |

---

### Mindmap

![]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-mindmap.png)

## References

- [Aztec Developer Docs](https://docs.aztec.network/)
- [Noir Language Docs](https://noir-lang.org/)
- [Aztec Protocol GitHub](https://github.com/AztecProtocol)
- [Aztec.js SDK Reference](https://docs.aztec.network/dev_docs/aztecjs/)
- ChatGPT with the input "Write me a technical article on Aztec by using the documentation I provide here. At the end, provide me a summary tab and also a comparison with other privacy system such as moneor, zcash, tornado cash, railgun"