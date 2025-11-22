---
layout: post
title: The Pedersen Commitment - Overview
date: 2025-11-22
lang: en
locale: en-GB
categories: cryptography
tags: pedersen commitment secret sharing
description: 
image: 
isMath: true
---

The **Pedersen commitment** is a cryptographic primitive introduced by **Torben Pryds Pedersen** in 1991 in his paper *“[Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing.](https://eprint.iacr.org/2004/201.pdf)”*
 It provides a way to *commit* to a secret value while keeping it hidden, and ensures the value cannot be changed later.

------

## Core Idea

We work in a finite cyclic group **G** of prime order **q**, where the **discrete logarithm problem** is hard.

We select two generators **g** and **h** in **G**, such that no one knows a value **a** where 
$$
h = g^a
$$


To commit to a secret value **s**, with **0 ≤ s < q**, we:

1. Pick a random blinding factor **t** from **Z_q**.

2. Compute the commitment:

   
   $$
   c = g^s * h^t
   $$
   

The value **c** is the commitment to **s**.
 To open the commitment, you reveal **(s, t)**, and anyone can verify:
$$
c = g^s * h^t
$$


------

## Properties

### Hiding

Because **t** is random, the commitment **c** hides **s**.
Even if someone sees **c**, they cannot determine **s** because there are many possible pairs **(s, t)** that yield the same **c**.

### Binding

Under the discrete logarithm assumption, it is infeasible to find another pair **(s', t')** such that:

**(s' ≠ s)** and **(c = g^{s'} \* h^{t'})**

If you could do that, you would effectively solve the discrete logarithm problem — which is assumed to be hard.

------

## Homomorphic Property

Pedersen commitments are **additively homomorphic**.
 If you have two commitments:
$$
c1 = g^{s1} * h^{t1}
$$

$$
c2 = g^{s2} * h^{t2}
$$

Then their product is:
$$
c1 * c2 = g^{s1 + s2} * h^{t1 + t2}
$$

This means **(c1 \* c2)** is a commitment to **(s1 + s2)**, using blinding factor **(t1 + t2)**.

This property is extremely useful in privacy-preserving systems, because you can prove relations among committed values without revealing them.

------

## Why It Matters

A commitment scheme like Pedersen’s allows you to:

- **Lock in** a value without revealing it immediately.
- **Prove** something about it later (like its range or sum).
- **Ensure** you cannot change it after committing.

Such schemes are critical in applications like:

- Auctions (commit bids first, reveal later)
- Secret sharing
- Zero-knowledge proofs
- Blockchain confidentiality

------

## Use in Blockchain and Privacy Systems

Because Pedersen commitments are both *hiding* and *homomorphic*, they are used in many privacy-preserving blockchain systems.

### Monero

Monero uses Pedersen commitments in its **Ring Confidential Transactions (RingCT)** protocol.
 Transaction amounts are hidden with commitments **(c = g^s \* h^t)**, but validators can still verify that:

**(Σ inputs = Σ outputs + fees)**

— all without revealing the actual amounts.
 Range proofs (like Bulletproofs) ensure that each committed amount is non-negative and within valid limits.

As the the result:

When you spend Monero, the value of the inputs that you are spending and the value of the outputs you are sending are encrypted and opaque to everyone except the recipient of each of those outputs. 

- Pedersen commitments allow you to send Monero without revealing the value of the transactions. 
- Pedersen commitments also make it possible for people to verify that transactions on the blockchain are valid and not creating Monero out of thin air.

Reference: [Monero - Pedersen Commitment](https://www.getmonero.org/resources/moneropedia/pedersen-commitment.html) / [Ring - Confidential Transactions](https://eprint.iacr.org/2015/1098.pdf)

#### Other

##### Project Khokha

2018 / PoC: The South African Reserve Bank’s **Project Khokha**, built on ConsenSys’ Quorum blockchain, used Pedersen commitments and range proofs for **confidential interbank settlements** — allowing banks to transact privately but still maintain regulatory assurance.

[https://consensys.io/blockchain-use-cases/finance/project-khokha](https://consensys.io/blockchain-use-cases/finance/project-khokha)

### Other Uses

Pedersen commitments are also standard building blocks in:

- **Zero-knowledge proofs** (e.g., zk-SNARKs, Bulletproofs)
- **Range proofs**
- **Confidential assets** in enterprise blockchains
- **Voting systems** where ballots must remain private but verifiable

------

## Limitations and Considerations

- The generators **g** and **h** must be chosen so that no one knows the relation between them (i.e., no **a** where **h = g^a**).
   If this relation is known, the commitment loses its hiding property.
- **Hiding** is information-theoretic (depends on random **t**).
   **Binding** is computational — it relies on the discrete log problem being hard.
- If discrete logs become easy (e.g., via quantum computing), the scheme’s binding property breaks.
- Commitments alone don’t prevent negative or invalid values — you need range proofs or other zero-knowledge checks for that.

------

## Summary

The **Pedersen commitment** is a powerful and elegant cryptographic primitive that provides both privacy and verifiability.
 It allows users to commit to values securely while keeping them hidden, and its additive homomorphism makes it ideal for complex privacy systems.

**Projects that use Pedersen commitments include:**

- Monero (for confidential transactions)
- MobileCoin (for private payments)
- Project Khokha (for interbank settlement privacy)
- Various zero-knowledge proof frameworks (like Bulletproofs)

## Reference

- [eprint - Non-Interactive and Information-Theoretic Secure Publicly Verifiable Secret Sharing](https://eprint.iacr.org/2004/201.pdf)

- [RareSkills - What are Pedersen Commitments and How They Work](https://rareskills.io/post/pedersen-commitment)

- https://crypto.stackexchange.com/questions/64437/what-is-a-pedersen-commitment
- https://dl.acm.org/doi/10.5555/646756.705507