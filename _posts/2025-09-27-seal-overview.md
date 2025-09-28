---
layout: post
title: Seal: Identity-Based Encryption for Onchain Access Control
date:   2025-09-27
lang: en
locale: en-GB
categories: blockchain cryptography
tags: sui walrus move seal KEM DEK
description: Seal is a framework that allows developers to encrypt data using Identity-Based Encryption (IBE) while enforcing onchain access policies on Sui. 
image:
isMath: 
---

Seal is a framework that allows developers to encrypt data using **Identity-Based Encryption (IBE)** while enforcing **onchain access policies** on Sui. The system abstracts away cryptographic details from users and developers, ensuring data confidentiality even from Seal itself.

In summary: 

- Application developers and users can use Seal to secure sensitive data at rest on decentralized storage like [Walrus](https://docs.wal.app/) or any other onchain / offchain storage. 
- Seal enables identity-based encryption and decryption of sensitive data, with access controlled by onchain policies on Sui. 
- Lightweight key servers enforce these policies and provide threshold-based decryption keys
- Developers can integrate easily using the [TypeScript SDK](https://www.npmjs.com/package/@mysten/seal).

------

## **Identity-Based Encryption (IBE)**

An IBE scheme consists of four algorithms:

- **Setup() → (msk, mpk):** Generates a master secret and public key.
- **Derive(msk, id) → sk:** Produces a derived secret key for an identity.
- **Encrypt(mpk, id, m) → c:** Encrypts a message under an identity.
- **Decrypt(sk, c) → m:** Recovers the message.

**Correctness:**
$$
Decrypt(Derive(msk, id), Encrypt(mpk, id, m)) = m
$$
The **identity domain is arbitrary**, allowing Seal to bind onchain strings to IBE identities.

------

## **Seal Components**

### 1. **Onchain Access Policies**

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

### 2. **Off-Chain Key Servers**

- Hold the **IBE master secret key**.
- Only return derived keys if **onchain policies approve**.
- **APIs:**
  - `/v1/service` → Metadata
  - `/v1/fetch_key` → Derived keys (signed request, PTB, encrypted response)

**Advanced deployments:**

- Threshold encryption (`t-of-n`)
- MPC committees for decentralized key servers

------

### 3. **User Sessions**

- Users approve key access per package via wallet.
- Session keys allow **temporary retrieval** of derived keys without repeated confirmations.

------

## **Cryptographic Primitives**

### **KEM (Key Encapsulation Mechanism)**

- **Boneh-Franklin IBE on BLS12-381**
- Encrypts a **symmetric key** (DEK) under an identity.
- Allows threshold/MPC setups and identity-based key management.

### **DEM (Data Encapsulation Mechanism)**

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

## **Decentralization and Trust Model**

- Users select one or more key servers based on trust assumptions.
- Threshold encryption ensures privacy and liveness.
- MPC committees allow dynamic membership of key server participants.
- Once data is encrypted, the key server set is fixed.

------

## **Security Assumptions**

1. **Key server integrity:** Fewer than the threshold of servers are compromised.
2. **Correct access policies:** Package code enforces rules accurately. Policy changes are onchain and transparent.

------

## **Use Cases**

- Time-lock encryption for MEV-resistant trading
- Secure voting
- Subscription-based or role-based encrypted data access

------

Seal provides a **flexible, generic, and decentralized** approach for encrypting data with identity-based keys, combining onchain access control with off-chain key management.

# Reference

- [seal.mystenlabs.com](https://seal.mystenlabs.com)
- [Seal - Design](https://github.com/MystenLabs/seal/blob/main/docs/Design.md)
- [github.com/MystenLabs/seal](https://github.com/MystenLabs/seal)
- ChatGPT to summarize the documentation

