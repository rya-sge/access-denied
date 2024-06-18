---
layout: post
title: Main Concept Behind Zero-Knowledge Proof
date:   2024-06-17
lang: en
locale: en-GB
categories: cryptography blockchain
tags: zeroknowledge zkp
description: This article is a summary of the main concepts behind Zero-Knowledge Proof (ZKP).
image: /assets/article/cryptographie/zero-knowledge-proof/zero-knowledge-proof.drawio.png
isMath: true
---

This article is a summary of the main concepts behind Zero-Knowledge Proof (ZKP).

Zero knowledge proofs are increasingly present in the blockchain ecosystem. 

- They are used either to improve privacy, by the fact that they allow a statement to be proven without revealing any additional information about the data behind the statement
-  Or to improve scalability/performance, for example with Ethereum layer2 (StarkNet, ZKsync, Polygon zkEVM)

In a Zero knowledge system, there are three main "actors":

1. **Prover**: The entity in a ZKP protocol that generates the proof to convince the verifier of the statement's truth.
2. **Verifier**: The entity in a ZKP protocol that validates the proof provided by the prover.
3. **Statement**: The assertion or proposition that the prover aims to prove to the verifier.

The following properties represent the base of a zero-kwnoledge system:

1. **Completeness**: This property defines that if the statement is true, an honest prover can convince an honest verifier of this fact.

2. **Soundness**: This property defines that if the statement is false, no dishonest prover can convince the honest verifier that it is true with a sufficiently high probability.

3. **Zero-Knowledge**: This property defines that the verifier learns nothing other than the fact that the statement is true; no additional information is revealed.

[TOC]



## Basic concepts

### Zero-Knowledge Proof (ZKP)

A cryptographic method that allows a prover to demonstrate the truth of a statement to a verifier without revealing any additional information.

Example: 

- proving that a number `n` is of the form of the product of two prime number 
-  Proving that one knows p,q such that n=pq 
- Proving that one knows x such gx mod p = y 

Reference: [purdue.edu - Topic 23: Zero-Knowledge Proof and Cryptographic Commitment](https://www.cs.purdue.edu/homes/ninghui/courses/555_Spring12/handouts/555_Spring12_topic23.pdf)

###  Main components

There are the three main components:

1. **Prover**: The entity in a ZKP protocol that generates the proof to convince the verifier of the statement's truth.
2. **Verifier**: The entity in a ZKP protocol that validates the proof provided by the prover.
3. **Statement**: The assertion or proposition that the prover aims to prove to the verifier.

![zero-knowledge-proof.drawio]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/zero-knowledge-proof.drawio.png)



## Security Properties

### Main properties

For our example, we take L – some language (usually not in P)

These properties are the base of all zero-knowledge system

1.**Completeness**: This property defines that if the statement is true, an honest prover can convince an honest verifier of this fact.

> If x ∈ L, then the probability that (P, V) rejects x is negligible in the length of x.

2.**Soundness**: This property defines that if the statement is false, no dishonest prover can convince the honest verifier that it is true with a sufficiently high probability.

>  A cheating prover cannot convince the verifier that x ∈ L if it is not true, except with some probability

3.**Zero-Knowledge**: This property defines that the verifier learns nothing other than the fact that the statement is true; no additional information is revealed.

> The only thing that the verifier learns is that x ∈ L

Reference: [www.mimuw.edu.pl - Commitment Schemes and Zero‐Knowledge Protocols](https://www.mimuw.edu.pl/~std/Dydaktyka/BISS09/BISS10.pdf)

### Others propreties

1. **Extractor/Extractability**: This property defines that if a prover can convince a verifier of a statement, it is possible to extract the witness (the secret knowledge proving the statement). It concerns zero-knowledge *proofs of knowledge* which are zero-knowledge proofs which additionally guarantee that the prover indeed holds the witness.
2. **Simulator/Simulability**: To prove the zero-knowledge property, here the concept of simulator: A

A simulator gives the same probability distribution of the view of the interaction without invoking the prover. Contrary to the prover,  the simulator  has only access to public information and can not leak any information because it doesn't have the witness.

1. S is generally defined as follwing:

- S is a probabilistic (expected) polynomial time algorithm.
-  It can interact with the Verifier V , but does not have access to its private randomness.

Example:

Upon receiving an input string x, Prover (P) and Verifier (V) pass a series of message strings a1, . . . , am, through which P attempts to convince V whether x is in the language L.

> Given any verifier V , and an honest prover P, there is some simulator S 
> if x ∈ L, then the distribution of S(x) is indistinguishable from the interaction transcript a1, a2, . . . , am between P and V .

References:

- [On Interactive Proofs and Zero-Knowledge: A Primer](https://medium.com/magicofc/interactive-proofs-and-zero-knowledge-b32f6c8d66c3)
- [courses.cs.cornell.edu - Theory of Computing](https://courses.cs.cornell.edu/cs6810/2021fa/lec19.pdf)
- [crypto.stackexchange - What is purpose of a simulator and extractor in zero knowledge proof protocols?](https://crypto.stackexchange.com/questions/67610/what-is-purpose-of-a-simulator-and-extractor-in-zero-knowledge-proof-protocols)
- [ic-people.epfl.ch - Zero Knowledge Proofs](https://ic-people.epfl.ch/~achiesa/docs/CS276-F2015/lecture-19.pdf)
- [An Introduction to Zero-Knowledge Proofs in Blockchains
  and Economics](https://files.stlouisfed.org/files/htdocs/publications/review/2023/10/02/an-introduction-to-zero-knowledge-proofs-in-blockchains-and-economics.pdf)



## Efficiency

1. **Efficiency**: The measure of computational resources (time, space) required to generate and verify the proof, crucial for practical implementation.
1. **Succinctness**: A feature of some ZKPs where the size of the proof is very small compared to the size of the statement or the witness, i.e., the size of the computation itself.
3. Used in ZK-SNARKs and ZK-STARKs

## Types of Zero-Knowledge Proofs

### Interactive Zero-Knowledge Proofs

ZKP protocols that require back-and-forth communication between the prover and verifier. This generally involved three steps:

- The Prover sends a message (commitment) to the Verifier 
- The Verifier returns to the prover a challenge to resolve.
- The Prover then responds to the challenge with the proof of the challenge

Interactive ZKP is not  suitable for blockchains since you can not verify the proof independently. 

Reference: [hacken - Zero-Knowledge Proof – How It Works](https://hacken.io/discover/zero-knowledge-proof/)

### NIZK

Protocols that do not require back-and-forth interaction between the prover and verifier after an initial setup phase.

In this category, we have:

1. **zk-SNARKs (Zero-Knowledge Succinct Non-Interactive Arguments of Knowledge)**: A type of NIZK with very short proofs and quick verification times, widely used in blockchain technologies.
2. **zk-STARKs (Zero-Knowledge Scalable Transparent Arguments of Knowledge)**: A type of zero-knowledge proof that does not rely on trusted setup and offers scalability and transparency.

Here several concepts related to NIKZ:

- The algorithm **Fiat-Shamir** is used to turn an interactive protocol to its non-interactive version.
- **Public Parameters**: Values or settings known to both the prover and verifier, essential for running the ZKP protocol, used in NIZK. With [zk-snark](https://consensys.io/blog/introduction-to-zk-snarks), these paramters are typically the *proving key* `pk`, and athe *verification key*  vk.
- **A trusted setup ceremony** is a ceremony between multiple participants using multi-party computation between users who are believed not to collude. In principle, this kind of ceremony required only one honest participant to create valid parameters.
- **The Common reference string** (CSR) is a string shared between the verifier and prover, this string is generally generated during the trusted setup ceremony.

Reference: [Panther - Understanding Trusted Setups: A Guide](https://blog.pantherprotocol.io/a-guide-to-understanding-trusted-setups/), [zk-SNARKs: A Gentle Introduction](https://www.di.ens.fr/~nitulesc/files/Survey-SNARKs.pdf), [ZK FAQ: What's a trusted setup? What's a Structured Reference String? What's toxic waste?](https://www.cryptologie.net/article/560/zk-faq-whats-a-trusted-setup-whats-a-structured-reference-string-whats-toxic-waste/)



## References

- [On Interactive Proofs and Zero-Knowledge: A Primer](https://medium.com/magicofc/interactive-proofs-and-zero-knowledge-b32f6c8d66c3)
- [courses.cs.cornell.edu - Theory of Computing](https://courses.cs.cornell.edu/cs6810/2021fa/lec19.pdf)
- [crypto.stackexchange - What is purpose of a simulator and extractor in zero knowledge proof protocols?](https://crypto.stackexchange.com/questions/67610/what-is-purpose-of-a-simulator-and-extractor-in-zero-knowledge-proof-protocols)
- [ic-people.epfl.ch - Zero Knowledge Proofs](https://ic-people.epfl.ch/~achiesa/docs/CS276-F2015/lecture-19.pdf)
- [An Introduction to Zero-Knowledge Proofs in Blockchains
  and Economics](https://files.stlouisfed.org/files/htdocs/publications/review/2023/10/02/an-introduction-to-zero-knowledge-proofs-in-blockchains-and-economics.pdf)
- [hacken - Zero-Knowledge Proof – How It Works](https://hacken.io/discover/zero-knowledge-proof/)
- [Panther - Understanding Trusted Setups: A Guide](https://blog.pantherprotocol.io/a-guide-to-understanding-trusted-setups/), [zk-SNARKs: A Gentle Introduction](https://www.di.ens.fr/~nitulesc/files/Survey-SNARKs.pdf)
-  [ZK FAQ: What's a trusted setup? What's a Structured Reference String? What's toxic waste?](https://www.cryptologie.net/article/560/zk-faq-whats-a-trusted-setup-whats-a-structured-reference-string-whats-toxic-waste/)
-  [Chainlink - Commit-and-Prove ZKs](https://blog.chain.link/commit-and-prove-zks/)
- [cwi.nl - Commitment Schemes and Zero-Knowledge
  Protocols](https://homepages.cwi.nl/~schaffne/courses/crypto/2014/papers/ComZK08.pdf) 
- [mimuw - Commitment Schemes and Zero-Knowledge
  Protocols](https://www.mimuw.edu.pl/~std/Dydaktyka/BISS09/BISS10.pdf)
- [Zero-knowledge Proof: IZKs, NIZKs, SNARKS, STARKS Explained.](https://medium.com/coinmonks/zero-knowledge-proof-izks-nizks-snarks-starks-5bc06c96c7ee)
- [Zero-knowledge proofs explained in 3 examples](https://www.circularise.com/blogs/zero-knowledge-proofs-explained-in-3-examples)
- [zk-learning- Introduction to Modern SNARKs](https://zk-learning.org/assets/Lecture2-2023.pdf)
- [Zero-knowledge proofs explained in 3 examples](https://www.circularise.com/blogs/zero-knowledge-proofs-explained-in-3-examples)
- ChatGPT with the input "List a short explanation for the 15 most important terms to know about zero knowledge proof. Regroup them in difference topics"
- ChatGPT with the input "In zero knowledge system, what is the meaning of Language L"



