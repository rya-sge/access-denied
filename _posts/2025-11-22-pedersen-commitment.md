---
layout: post
title: The Pedersen Commitment - Overview
date: 2025-11-22
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: cryptography
tags: pedersen commitment secret sharing
description: Pedersen commitment provides a way to commit to a secret value while keeping it hidden, and ensures the value cannot be changed later.
image: /assets/article/cryptographie/pedersen/2025-11-22-pedersen-commitment-mindmap.png
isMath: true
---

The **Pedersen commitment** is a cryptographic primitive introduced by **Torben Pryds Pedersen** in 1991 in his paper *“[Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing.](https://link.springer.com/chapter/10.1007/3-540-46766-1_9)”* (CRYPTO '91)
 It provides a way to *commit* to a secret value while keeping it hidden, and ensures the value cannot be changed later.

> This article has been written with the help of ChatGPT

[TOC]

## What you need to know first

The construction relies on a few notions from group-based cryptography that the article uses without defining them.

- **Cyclic group of prime order**: a group $$G$$ of prime order $$q$$ in which every element other than the identity is a generator, meaning its successive powers produce the whole group. The commitment $$c = g^s \cdot h^t$$ is computed in such a group, from two generators $$g$$ and $$h$$.
- **Integers modulo $$q$$**: $$\mathbb{Z}_q$$ is the set $$\{0, \dots, q-1\}$$ with addition and multiplication taken modulo $$q$$. Exponents in $$G$$ behave as elements of $$\mathbb{Z}_q$$, which is why the secret $$s$$ and the blinding factor $$t$$ are taken from it.
- **Discrete logarithm problem**: given $$g$$ and $$h = g^a$$, finding $$a$$ is assumed to be computationally infeasible in a well-chosen group. The binding property rests on this assumption; see [Le Logarithme Discret sur courbe elliptique avec SageMath]({{site.url_complet}}/2021/07/30/logarithme-discret-courbe-elliptique/) for the elliptic-curve version.
- **Information-theoretic versus computational security**: a property is information-theoretic when it holds even against an attacker with unlimited computing power, and computational when it only holds as long as some problem stays hard to solve. The article uses this distinction to compare hiding and binding.
- **Range proofs**: a zero-knowledge proof that a committed value lies in a given interval, for example that an amount is non-negative, without revealing it. Monero pairs its commitments with range proofs such as Bulletproofs; see [Zero Knowledge Proofs with Bulletproof]({{site.url_complet}}/2024/08/13/bulletproof-zero-knowledge-proof/).

## Core Idea

We work in a finite cyclic group **G** of prime order **q**, where the **discrete logarithm problem** is hard.

We select two generators **g** and **h** in **G**, such that no one knows a value **a** where 
$$
\begin{aligned}
h = g^a
\end{aligned}
$$

To commit to a secret value **s**, with **0 ≤ s < q**, we:

1. Pick a random blinding factor **t** from **Z_q**.

2. Compute the commitment:

   
   $$
   \begin{aligned}
   c = g^s * h^t
   \end{aligned}
   $$
   

The value **c** is the commitment to **s**.
 To open the commitment, you reveal **(s, t)**, and anyone can verify:
$$
\begin{aligned}
c = g^s * h^t
\end{aligned}
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
\begin{aligned}
c1 = g^{s1} * h^{t1}
\end{aligned}
$$

$$
\begin{aligned}
c2 = g^{s2} * h^{t2}
\end{aligned}
$$

Then their product is:
$$
\begin{aligned}
c1 * c2 = g^{s1 + s2} * h^{t1 + t2}
\end{aligned}
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

2018 / PoC: The South African Reserve Bank’s **Project Khokha**, built on ConsenSys’ Quorum blockchain, used Pedersen commitments and range proofs for a Proof Of Concept of**confidential interbank settlements**. This could allow banks to transact privately but still maintain regulatory assurance.

Reference: [consensys.io - Project Khokha: Blockchain Case Study for Central Banking in South Africa](https://consensys.io/blockchain-use-cases/finance/project-khokha)

### Other Uses

Pedersen commitments are also standard building blocks in:

- **Zero-knowledge proofs** (e.g., zk-SNARKs, Bulletproofs)
- **Range proofs**
- **Confidential assets** in enterprise blockchains
- **Voting systems** where ballots must remain private but verifiable

------

## Limitations and Considerations

- The generators **g** and **h** must be chosen so that no one knows the relation between them (i.e., no **a** where **h = g^a**).
   If this relation is known, the commitment loses its binding property: the committer can open the same commitment to another value. Hiding is not affected, since $$h^t$$ still masks the value perfectly.
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

![Pedersen commitment mindmap]({{site.url_complet}}/assets/article/cryptographie/pedersen/2025-11-22-pedersen-commitment-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Commitment scheme** | A primitive that lets a party lock in a value without revealing it, then open it later in a way that cannot be changed. |
| **Generator** | An element of the group whose powers produce the whole group; the scheme uses two generators $$g$$ and $$h$$. |
| **Discrete logarithm assumption** | The assumption that, given $$g$$ and $$h = g^a$$, no efficient algorithm can find $$a$$. |
| **Blinding factor** | The random value $$t$$ from $$\mathbb{Z}_q$$ that makes the commitment hide the secret $$s$$. |
| **Commitment** | The group element $$c = g^s \cdot h^t$$ that represents the secret $$s$$. |
| **Opening** | Revealing $$(s, t)$$ so that anyone can recompute $$g^s \cdot h^t$$ and compare it with $$c$$. |
| **Hiding** | The property that $$c$$ reveals nothing about $$s$$; for Pedersen commitments it is information-theoretic. |
| **Binding** | The property that the committer cannot open $$c$$ to a different value; for Pedersen commitments it is computational and relies on the discrete logarithm problem. |
| **Additive homomorphism** | The property that the product of two commitments is a commitment to the sum of their values, with the sum of their blinding factors. |
| **Range proof** | A zero-knowledge proof that a committed value lies in a valid range, such as a non-negative amount. |
| **RingCT** | Monero's Ring Confidential Transactions protocol, which hides amounts with Pedersen commitments while letting validators check that inputs equal outputs plus fees. |
| **Bulletproofs** | A range-proof system used with Pedersen commitments, for example in Monero. |

## Reference

- [Springer - Pedersen, Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing (CRYPTO '91)](https://link.springer.com/chapter/10.1007/3-540-46766-1_9)
- [RareSkills - What are Pedersen Commitments and How They Work](https://rareskills.io/post/pedersen-commitment)
- [crypto.stackexchange.com - What is a Pedersen commitment?](https://crypto.stackexchange.com/questions/64437/what-is-a-pedersen-commitment)
- [https://dl.acm.org/doi/10.5555/646756.705507](https://dl.acm.org/doi/10.5555/646756.705507)

### Related articles

- [Pedersen Hash Function Overview]({{site.url_complet}}/2024/05/07/pedersen-hash-function/)
- [Zero Knowledge Proofs with Bulletproof]({{site.url_complet}}/2024/08/13/bulletproof-zero-knowledge-proof/)
