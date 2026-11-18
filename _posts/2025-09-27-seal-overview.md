---
layout: post
title: "Seal: Identity-Based Encryption for Onchain Access Control"
date:   2025-09-27
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: blockchain cryptography
tags: sui walrus move seal KEM DEK
description: Seal is a framework that allows developers to encrypt data using Identity-Based Encryption (IBE) while enforcing onchain access policies on Sui. 
image: /assets/article/cryptographie/2025-09-27-seal-overview-mindmap.png
isMath: true
---

Seal is a framework that allows developers to encrypt data using **Identity-Based Encryption (IBE)** while enforcing **onchain access policies** on Sui. The system abstracts away cryptographic details from users and developers, ensuring data confidentiality even from Seal itself.

In summary: 

- Application developers and users can use Seal to secure sensitive data at rest on decentralized storage like [Walrus](https://docs.wal.app/) or any other onchain / offchain storage. 
- Seal enables identity-based encryption and decryption of sensitive data, with access controlled by onchain policies on Sui. 
- Lightweight key servers enforce these policies and provide threshold-based decryption keys
- Developers can integrate easily using the [TypeScript SDK](https://www.npmjs.com/package/@mysten/seal).

## What you need to know first

Seal combines pairing-based cryptography with Sui's execution model, and the article uses the following concepts without explaining them.

- **Bilinear pairing and BLS12-381**: a pairing is a map $$e$$ from two elliptic-curve groups to a third one such that $$e(aP, bQ) = e(P, Q)^{ab}$$. Boneh-Franklin IBE is built on this property, and Seal instantiates it on the pairing-friendly curve BLS12-381; see [Understanding zk-SNARK: A Deep Dive into Zero-Knowledge Proofs]({{site.url_complet}}/2025/07/29/zk-snark-overview/) for another use of pairings.
- **Threshold (t-of-n) schemes**: a secret is split so that any $$t$$ of $$n$$ parties can recover it while fewer than $$t$$ learn nothing. Seal's threshold mode lets a user recover a key from any $$t$$ of the chosen key servers, so up to $$n - t$$ of them can be offline; [Introduction to Shamir's Secret Sharing - How to share a secret]({{site.url_complet}}/2024/10/29/shamir-secret-sharing-introduction/) shows the classic construction.
- **Multi-party computation (MPC)**: a set of parties jointly compute a function of their secret inputs without any of them seeing the others' inputs. An MPC committee can thus act as one key server whose master secret key never exists in a single place; see [Inside the Zama KMS — Threshold Key Management for FHE, From MPC Protocol to Enclave Deployment]({{site.url_complet}}/2026/09/18/zama-kms-threshold-key-management-architecture-and-operation/).
- **Authenticated encryption**: an encryption mode that provides both confidentiality and integrity, so a modified ciphertext is rejected at decryption. AES-256-GCM, one of Seal's DEM options, is such a mode.
- **Sui Move packages**: on Sui, smart contracts are Move modules published together as a package with its own on-chain ID. Seal uses that ID as a namespace, so only the package's own `seal_approve` function decides who may obtain keys for identities under it.
- **Programmable Transaction Block (PTB)**: a Sui transaction made of a sequence of commands, such as calls to Move functions. A key request carries a PTB that calls `seal_approve`, and the key server returns a key only if that call would succeed.
- **BCS**: Binary Canonical Serialization, the byte encoding used by Move and Sui. The time-lock example uses it to decode the timestamp stored in the identity bytes.

------

## Identity-Based Encryption (IBE)

An IBE scheme consists of four algorithms:

- **Setup() → (msk, mpk):** Generates a master secret and public key.
- **Derive(msk, id) → sk:** Produces a derived secret key for an identity.
- **Encrypt(mpk, id, m) → c:** Encrypts a message under an identity.
- **Decrypt(sk, c) → m:** Recovers the message.

**Correctness:**
$$
\begin{aligned}
Decrypt(Derive(msk, id), Encrypt(mpk, id, m)) = m
\end{aligned}
$$
The **identity domain is arbitrary**, allowing Seal to bind onchain strings to IBE identities.

------

## Seal Components

### Onchain Access Policies

- Each Move package (`PkgId`) controls a namespace `[PkgId]*`.
- Developers implement `seal_approve` to define authorization.
- Example: **Time-lock encryption**

```
entry fun seal_approve(id: vector<u8>, c: &clock::Clock) {
    let mut prepared: BCS = bcs::new(id);
    let t = prepared.peel_u64();
    assert!(prepared.into_remainder_bytes().length() == 0 && c.timestamp_ms() >= t, 1);
}
```

- Identity `[PkgId][bcs::to_bytes(T)]` is accessible only after timestamp `T`.

------

### Off-Chain Key Servers

- Hold the **IBE master secret key**.
- Only return derived keys if **onchain policies approve**.
- **APIs:**
  - `/v1/service` → Metadata
  - `/v1/fetch_key` → Derived keys (signed request, PTB, encrypted response)

**Advanced deployments:**

- Threshold encryption (`t-of-n`)
- MPC committees for decentralized key servers

------

### User Sessions

- Users approve key access per package via wallet.
- Session keys allow **temporary retrieval** of derived keys without repeated confirmations.

------

## Cryptographic Primitives

### KEM (Key Encapsulation Mechanism)

- **Boneh-Franklin IBE on BLS12-381**
- Encrypts a **symmetric key** (DEK) under an identity.
- Allows threshold/MPC setups and identity-based key management.

### DEM (Data Encapsulation Mechanism)

- Encrypts the **actual data** using the DEK.
- Current options:
  - **AES-256-GCM:** Authenticated encryption
  - **HMAC-CTR:** For onchain decryption scenarios

**Workflow:**

1. Generate a random DEK.
2. Encrypt data with DEK (DEM).
3. Encrypt DEK under identity using KEM.
4. Store/transmit `(encrypted DEK, encrypted data)`.

------

## Decentralization and Trust Model

- Users select one or more key servers based on trust assumptions.
- Threshold encryption ensures privacy and liveness.
- MPC committees allow dynamic membership of key server participants.
- Once data is encrypted, the key server set is fixed.

------

## Security Assumptions

1. **Key server integrity:** Fewer than the threshold of servers are compromised.
2. **Correct access policies:** Package code enforces rules accurately. Policy changes are onchain and transparent.

------

## Use Cases

- Time-lock encryption for MEV-resistant trading
- Secure voting
- Subscription-based or role-based encrypted data access

------

Seal provides a **flexible, generic, and decentralized** approach for encrypting data with identity-based keys, combining onchain access control with off-chain key management.

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Identity-Based Encryption (IBE)** | A public-key scheme in which a message is encrypted under an arbitrary identity string, and the matching secret key is derived from a master secret key. |
| **Identity** | The string under which data is encrypted; in Seal it is an on-chain value prefixed by the package ID, such as `[PkgId][bcs::to_bytes(T)]`. |
| **Master secret key (msk)** | The secret produced by `Setup`, held by a key server and used to derive the secret key of any identity. |
| **Master public key (mpk)** | The public key produced by `Setup`, with which anyone can encrypt under any identity. |
| **Derived key** | The secret key for one identity, returned by a key server through `/v1/fetch_key` only when the on-chain policy approves. |
| **Boneh-Franklin IBE** | The IBE scheme Seal uses as its KEM, instantiated on the BLS12-381 curve. |
| **Key server** | An off-chain service that holds an IBE master secret key and enforces on-chain policies before releasing derived keys. |
| **Access policy** | The rule, written in a Move package, that decides who may obtain the key for an identity in the package's namespace. |
| **`seal_approve`** | The Move function a developer implements to authorize key access; the key is released only if it does not abort. |
| **Namespace** | The set of identities `[PkgId]*` controlled by one Move package. |
| **Time-lock encryption** | A policy under which an identity becomes decryptable only after a given timestamp, checked against the Sui clock. |
| **Threshold encryption** | A `t-of-n` configuration in which a user needs keys from $$t$$ of the $$n$$ chosen key servers, so that fewer than $$t$$ compromised servers cannot decrypt. |
| **MPC committee** | A group of participants that jointly runs a key server, which allows dynamic membership. |
| **Session key** | A temporary key, approved once per package in the user's wallet, that retrieves derived keys without repeated confirmations. |
| **KEM** | Key Encapsulation Mechanism: the part that encrypts the symmetric data key under an identity, here with Boneh-Franklin IBE. |
| **DEM** | Data Encapsulation Mechanism: the part that encrypts the actual data with the data key. |
| **DEK** | Data Encryption Key: the random symmetric key generated for each encryption, used by the DEM and wrapped by the KEM. |
| **AES-256-GCM** | The authenticated-encryption DEM option of Seal. |
| **HMAC-CTR** | The DEM option of Seal meant for decryption on chain. |
| **Walrus** | A decentralized storage network on which Seal-encrypted data can be stored. |

## Reference

- [seal.mystenlabs.com](https://seal.mystenlabs.com)
- [Seal - Design](https://github.com/MystenLabs/seal/blob/main/docs/Design.md)
- [github.com/MystenLabs/seal](https://github.com/MystenLabs/seal)
- ChatGPT to summarize the documentation

## Mindmap

The mindmap below summarizes the article.

![Seal identity-based encryption mindmap]({{site.url_complet}}/assets/article/cryptographie/2025-09-27-seal-overview-mindmap.png)
