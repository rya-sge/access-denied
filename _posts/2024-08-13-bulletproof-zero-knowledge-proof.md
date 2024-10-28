---
layout: post
title:  Zero Knowledge Proofs with Bulletproof 
date:   2024-08-13
lang: en
locale: en-GB
categories: cryptography blockchain ZKP
tags: ethereum solidity security code4Arena
description: Bulletproofs are efficient and compact zero-knowledge proofs. They're enhancing privacy and scalability in blockchain systems by reducing data size and verification time.
image: /assets/article/blockchain/monero-symbol-on-white-480.png
isMath: false
---

[TOC]

Bulletproofs have been developed in 2017 by a Stanford Applied Cryptography Group composed of **Jonathan Bootle** (University College London), Benedict Bunz (Stanford University), Dan Boneh, Andrew Poelstra, Pieter Wuille and Greg Maxwell. 

This protocol is defined in this specification paper: [Bulletproofs: Short Proofs for Confidential Transactions and More](https://eprint.iacr.org/2017/1066.pdf)

Bulletproofs are short non-interactive zero-knowledge proofs (NIZK) that:

- require no trusted setup.
- Work with any Elliptic Curve such as Ristretto 
- The verifier cost scales linearly with the computation size.

A bulletproof can be used to convince a verifier that:

-  an encrypted plaintext is well formed. 
-  an encrypted number is in a given range, without revealing anything else about the number. 

Reference: [Bulletproofs - Dimitry Khovratovich](https://sikoba.com/docs/SKOR_DK_Bulletproofs_201905.pdf)

## General presentation

According to the Stanford presentation, Bulletproofs

- Shrink the size of the cryptographic proof from over 10kB to less than 1kB. 
- Support proof aggregation, so that proving that *m* transaction values are valid adds only *O*(log(*m*)) additional elements to the size of a single proof.

### Overview

#### Pros

+: Compared to [SNARKs](https://medium.com/@VitalikButerin/zk-snarks-under-the-hood-b33151a013f6), Bulletproofs require no trusted setup, like zkSTARKs.

+: they are smaller than zkSTARKs

+: batch verification available

+: They require no interaction between prover and verifier since they are non-interactive zero-knowledge proofs

#### Cons

-: verifying a bulletproof is more time consuming than verifying a SNARK proof.

-: linear verification time (O(N))

-: No post-quantum secure (based on discrete log)

Reference: [crypto.stanford.edu - bulletproofs/](https://crypto.stanford.edu/bulletproofs/), [academy.bit2me - What are Bulletproofs?](https://academy.bit2me.com/en/que-son-las-bulletproofs/)

### Applications and use-case

Bulletproofs have many other applications in cryptographic protocols: 

- Shortening proofs of solvency
- Short verifiable shuffles, 
- Confidential smart contracts / transactions,
- Created range proof on committed values ([p.1](https://eprint.iacr.org/2017/1066.pdf))
  - they enable proving that a committed value is in a range using only *2log2(n)+9* group and field elements, where n is the bit length of the range. Proof generation and verification times are linear in n.
- A general replacement for [Sigma-protocols](https://medium.com/@loveshharchandani/zero-knowledge-proofs-with-sigma-protocols-91e94858a1fb),  which are 3 phase protocols for proving knowledge of values without disclosing the values themselves.

#### Bitcoin

If all Bitcoin transactions were confidential and used Bulletproofs, then the total size of the UTXO set would be only 17 GB, compared to 160 GB with the currently used proofs according to the group behind Bulletproof, see [crypto.stanford.edu - bulletproofs/](https://crypto.stanford.edu/bulletproofs/)

#### MPC protocol

Bulletproofs can be combined with a MPC protocol to aggregate proofs from multiple parties. Through a simple MPC protocol, the different parties can generate a single proof without revealing their inputs for constructing Bulletproofs. 

In this [video](https://youtu.be/Adrh6BCc_Ao?si=sBlZDDaSsTvhBJ-T&t=616) from Stanford University, Benedikt Bünz has presented an overview of such architecture: 

- Custom MPC to generate proofs
- Works if circuits are disjoint, e.g n range proofs for n provers
- Simply aggregate proofs in each round and compute Fiat-Shamir challenge
- Either log(n) rounds and log(n) communication

------

## Implementation details

- They rely on the *Discrete Logarithm* assumption. This means that given an output, it is not possible to compute the input used (one-way computation). This also means that these proofs are probably not post quantum resistant since problems relying on the discrete logarithm are not

- They are made non-interactive using the *Fiat-Shamir Heuristic*. This algorithm creates a digital signature based on an interactive zero-knowledge proof, converting thus this proof to a non-interactive one.

- They use an efficient algorithm to calculate an inner-product argument for two independent (not related) binding vector Pedersen Commitment. 

  What is the *inner product* ? It is the component by component  product of two vector.  it is a generalization of the dot product in a [vector space](https://mathworld.wolfram.com/VectorSpace.html): a way to multiply [vectors](https://mathworld.wolfram.com/Vector.html) together, with the result of this multiplication being a [scalar](https://mathworld.wolfram.com/Scalar.html). References: [tlu.tarilabs.com - the bulletproof protocols](https://tlu.tarilabs.com/cryptography/the-bulletproof-protocols), [dankradfeist.de - Inner Product Arguments](https://dankradfeist.de/ethereum/2021/07/27/inner-product-arguments.html), [mathworld.wolfram.com - InnerProduct](https://mathworld.wolfram.com/InnerProduct.html)

Reference:

- [tlu.tarilabs.com - learning-paths/bulletproofs](https://tlu.tarilabs.com/learning-paths/bulletproofs)
- [tlu.tarilabs.com - bulletproofs-and-mimblewimble](https://tlu.tarilabs.com/cryptography/bulletproofs-and-mimblewimble)
- [https://blog.pantherprotocol.io/bulletproofs-in-crypto-an-introduction-to-a-non-interactive-zk-proof/](https://blog.pantherprotocol.io/bulletproofs-in-crypto-an-introduction-to-a-non-interactive-zk-proof/)

------

## Use

### Monero

A use-case of bulletproofs is in confidential transactions. Notably, Monero, a privacy focus chain, uses them to power its [RingCT](https://blog.pantherprotocol.io/ring-signatures-vs-zksnarks-comparing-privacy-technologies/) technology. They switched from using Schnorr signatures and Borromean ring signatures to lightweight bulletproofs. The initial ring signatures were effective, but they increased the size of an average RingCT exponentially.

Monero has made some improvement to Bulletproof with a new range-proving system called [Bulletproofs+](https://www.getmonero.org/2020/12/24/Bulletproofs+-in-Monero.html?ref=blog.pantherprotocol.io). When you transfer coins on the Monero blockchain, for instance, Bulletproofs+ proves that your payment is a positive number without revealing how much you paid.

References:[getmonero.org - Bulletproofs+ in Monero](https://www.getmonero.org/2020/12/24/Bulletproofs+-in-Monero.html), [panther - Bulletproofs In Crypto – An introduction to a Non-Interactive ZKP](https://blog.pantherprotocol.io/bulletproofs-in-crypto-an-introduction-to-a-non-interactive-zk-proof/)

### Mimblewimble

MimbleWimble is a blockchain solution designed for Confidential Transactions, where the transaction addresses and amounts are hidden, providing a high level of privacy for blockchain users. 

- Validators in MimbleWimble only store Unspent Transaction Outputs (UTXOs) instead of the entire transaction history for the blockchain, enabling space savings and faster sync. 
- The design of MimbleWimble relies on Elliptic Curve Cryptography, which is easy to understand
  and audit.

A [Mimblewimble](https://tlu.tarilabs.com/protocols/mimblewimble) blockchain relies on two complementary aspects to provide security:

- [Pedersen Commitments](https://tlu.tarilabs.com/cryptography/the-bulletproof-protocols#pedersen-commitments-and-elliptic-curve-pedersen-commitments) to provide perfectly hiding and computationally binding commitments.
- Range proofs (in the form of [Bulletproof range proofs](https://tlu.tarilabs.com/cryptography/bulletproofs-and-mimblewimble)) : it would only grow with the number of transactions that have unspent outputs, which is much smaller than the size of the UTXO set. Range proofs assures that all values are positive and not too large

Reference: [Confidential Assets on MimbleWimble](https://eprint.iacr.org/2019/1435.pdf) [tarilabs -Mimblewimble](https://tlu.tarilabs.com/protocols/mimblewimble), [What consensus algorithm is MimbleWimble/Grin using? Does it use Zero Knowledge Proofs as well?](https://bitcoin.stackexchange.com/questions/71870/what-consensus-algorithm-is-mimblewimble-grin-using-does-it-use-zero-knowledge)

#### Implementation

- [MimbleWimble Extension Blocks](https://wenmweb.com/) (MWEB) is the MimbleWimble implementation on Litecoin.
- [Grin](https://github.com/mimblewimble/grin) is an in-progress implementation of the Mimblewimble protocol. 
- [beam](https://beam.mw) is a mimblewimble L1 privacy blockchain, completely concealing transactions
- [Epic Cash](https://epiccash.com) is a MimbleWimble blockchain implementation that yields advances in scalability as a result of space efficient design that sheds redundant transaction data. 

------

## Bulletproof Commitment Scheme

Not sure this term ("Bulletproof Commitment Scheme) is very common but the goal is to refer to the way Bulletproofs can be used with commitments. A commitment scheme allows one to commit to a value while keeping it hidden, with the ability to reveal it later.

In this case, the scheme relies on [Pedersen commitments](https://www.getmonero.org/resources/moneropedia/pedersen-commitment.html?ref=blog.pantherprotocol.io), which allow zero-knowledge verification of values using a mathematical trick. This can be used in a utxo blockchain like Monero to reveal that the sum of the inputs is of a greater value than the sum of the outputs without disclosing any of the values. 

A Pedersen commitment (C) uses a point on an elliptic curve to create a one-way function. A Pedersen commitment to a value `v` is of the form `C = vG + sQ`, where `G` and `Q` are known generator points on an elliptic curve, and `s` is a secret blinding factor.

**Key Characteristics**:

- **Binding**: Once a value is committed, the committer cannot change it.
- **Hiding**: The committed value remains hidden from others until it is revealed.
- **Use with Bulletproofs**: When combined with Bulletproofs, the commitment scheme allows proving properties about the committed values (e.g., range proofs) efficiently and privately.

**Applications**: Used in confidential transactions to commit to transaction amounts and then use Bulletproofs to prove that these amounts are within a certain range without revealing the amounts themselves.

Reference: [zk-learnin.org - Polynomial Commitments based on Pairing and Discrete Logarithm](https://zk-learning.org/assets/lecture6.pdf), p.40, [blog.rachitasrivastava - Bulletproof Commitment Schemes: Integrating Cryptography and Mathematics](https://blog.rachitasrivastava.com/bulletproof-commitment-schemes-integrating-cryptography-and-mathematics), [RareSkills - What are Pedersen Commitments and How They Work](https://www.rareskills.io/post/pedersen-commitment)

------

## Comparison of the most popular zkp systems

This summary is taken from the project [Awesome zero knowledge proofs (zkp)](https://github.com/matter-labs/awesome-zero-knowledge-proofs?tab=readme-ov-file#comparison-of-the-most-popular-zkp-systems) by Matter labs: 

|                                       | SNARKs                                                       | STARKs                              | Bulletproofs                                                 |
| ------------------------------------- | ------------------------------------------------------------ | ----------------------------------- | ------------------------------------------------------------ |
| Used by                               | [Zcash](https://z.cash/learn/what-are-zk-snarks/), [ZkSync](https://tokeninsight.medium.com/zksync-vs-starkware-whats-the-difference-between-the-top-two-zk-rollups-66d1a7d08ef3) | [StarkWare ](https://starkware.co/) | [Monero](https://www.getmonero.org/2020/12/24/Bulletproofs+-in-Monero.html) |
| CRS Size*                             | n                                                            | 0                                   | n                                                            |
| Algorithmic complexity: prover        | O(N * log(N))                                                | O(N * poly-log(N))                  | O(N * log(N))                                                |
| Algorithmic complexity: verifier      | ~O(1)                                                        | O(poly-log(N))                      | O(N)                                                         |
| Communication complexity (proof size) | ~O(1)                                                        | O(poly-log(N))                      | O(log(N))                                                    |
| - size estimate for 1 TX              | Tx: 200 bytes, Key: 50 MB                                    | 45 kB                               | 1.5 kb                                                       |
| - size estimate for 10.000 TX         | Tx: 200 bytes, Key: 500 GB                                   | 135 kb                              | 2.5 kb                                                       |
| Ethereum/EVM verification gas cost    | ~600k (Groth16)                                              | ~2.5M (estimate, no impl.)          | N/A                                                          |
| Trusted setup required?               | &#x2611;                                                     | &#x2612;                            | &#x2612;                                                     |
| Post-quantum secure                   | &#x2612;                                                     | &#x2611;                            | &#x2612;                                                     |
| Crypto assumptions                    | DLP + secure bilinear pairing                                | Collision resistant hashes          | Discrete log                                                 |

*Reference: [eprint.iacr.org/2019/099.pdf](https://eprint.iacr.org/2019/099.pdf), page 3

Other reference used: [ethereum.stackexchange - zk-SNARKs vs. Zk-STARKs vs. BulletProofs? (Updated)](https://ethereum.stackexchange.com/questions/59145/zk-snarks-vs-zk-starks-vs-bulletproofs-updated)

------

## Known implementation

From [Matter labs - awesome-zero-knowledge-proofs ](https://github.com/matter-labs/awesome-zero-knowledge-proofs?tab=readme-ov-file#try) and [crypto.stanford.edu/bulletproofs/](https://crypto.stanford.edu/bulletproofs/)

- [Implementation in Haskell](https://github.com/adjoint-io/bulletproofs)
- [Implementation in Rust](https://github.com/dalek-cryptography/bulletproofs)
- [Implementation in C](https://github.com/Tongsuo-Project/Tongsuo)
- [Prototype in Java](https://github.com/bbuenz/BulletProofLib)
- [Prototype in Rust](https://github.com/chain/ristretto-bulletproofs)

------

## References

- Specification: [crypto.stanford.edu/bulletproofs - Short Proofs for Confidential Transactions and More ](https://crypto.stanford.edu/bulletproofs/)
- [crypto.stanford - Introduction and collection of resources](https://crypto.stanford.edu/bulletproofs/)
- [tlu.tarilabs.com - The Bulletproof Protocols](https://tlu.tarilabs.com/cryptography/the-bulletproof-protocols)
- [From Zero (Knowledge) to Bulletproofs](https://github.com/AdamISZ/from0k2bp) - a long and very nice gradual explanation
- [Dmitry Khovratovich - Bulletproofs](http://sikoba.com/docs/SKOR_DK_Bulletproofs_201905.pdf) - succinct and complete description of the protocol
- ChatGpt with the input "What is the difference and link between Bulletproof, Bulletproof Commitment Scheme and pedersen commitment ?"