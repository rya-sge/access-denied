---
layout: post
title: Overview of Zero-Knowledge development framework
date:   2024-06-10
lang: en
locale: en-GB
categories: cryptography blockchain ZKP
tags: zeroknowledge zkp
description: Overview of the main development frameworks to build zero-knowledge system which Plonky2(Polygon), Halo2(Zcash), Boojum (Matter Labs),...
image: /assets/article/cryptographie/zero-knowledge-proof/zcash-zec-logo.png
isMath: true
---

This article is a summary of the main zero-knowledge development framework. 

This article is mainly based on the following great article by Celo: [The Pantheon of Zero Knowledge Proof Development Frameworks (Updated!)](https://blog.celer.network/2023/08/04/the-pantheon-of-zero-knowledge-proof-development-frameworks/)

[TOC]

## Boojum (Matter labs)

[GitHub](https://github.com/matter-labs/era-boojum)

Boojum is a Rust-based arithmetization & constraint library, based on the implementation developed for Plonky2 (recursive SNARK).

- According to ZkSync, Boojum provers only require 16 GB of RAM.
- Use the FRI commitment scheme
- The purpose of this library is to work with a very specific arithmetization with additional assumptions about the field size.
- Boojum by default operates over the following prime field 

$$
\begin{aligned}
2^{64} - 2^{32} + 1
\end{aligned}
$$

- Boojum provides also implementations of the corresponding field-bound  primitives like the Poseidon2 hash function, as well as SHA256, Keccak256 and Blake2s.

Reference: [ZkSync - Boojum Upgrade: zkSync Era’s New High-performance Proof System for Radical Decentralization](https://zksync.mirror.xyz/HJ2Pj45EJkRdt5Pau-ZXwkV2ctPx8qFL19STM5jdYhc)

## gnark (Consensys)

[Github](https://github.com/ConsenSys/gnark)

Build by Consensys and written in Go, `gnark` is a fast zk-SNARK library that offers a high-level API to design circuits. 

`gnark` supports two proving schemes [Groth16](https://eprint.iacr.org/2016/260.pdf) and [PlonK](https://eprint.iacr.org/2019/953.pdf). These schemes can be instantiated with any of the following elliptic curves: *BN254*, *BLS12-381*, *BLS12-377*, *BLS24-315*, *BW6-633* or *BW6-761*.

All these curves are defined over a finite field Fp and have an equation of the form 
$$
\begin{aligned}
y² = x^3+b (b∈Fp).
\end{aligned}
$$
Reference: [Consensys - Prove schemes and curves](https://docs.gnark.consensys.io/Concepts/schemes_curves)

## Halo2 (ZCash)

[GitHub](https://github.com/zcash/halo2)

Halo2 is Zcash’s zk-SNARK implementation with Plonk. It is equipped with the Plonkish arithmetization that supports many useful primitives, such as custom gates and lookup tables.

The arithmetization used by Halo 2 comes from [PLONK](https://eprint.iacr.org/2019/953), or more precisely its extension UltraPLONK that supports custom gates and lookup arguments. They call it [***PLONKish***](https://twitter.com/feministPLT/status/1413815927704014850).

Reference:

- [zcash - arithmetization](https://zcash.github.io/halo2/concepts/arithmetization.html)
- [privacy-scaling-explorations/halo2](https://github.com/privacy-scaling-explorations/halo2)
- [halo2 - PLONKish Arithmetization](https://zcash.github.io/halo2/concepts/arithmetization.html#plonkish-arithmetization)
- [zcash - halo2](https://zcash.github.io/halo2/)

## Nova (Microsoft)

[GitHub](https://github.com/microsoft/Nova)

Nova is a recursive SNARK. A recursive  SNARK enables producing proofs that prove statements about prior  proofs).

`nova-snark,` is the rust library implementation of Nova over a cycle of elliptic curves

There are three supported curve cycles: Pallas/Vesta, BN254/Grumpkin, and secp/secq.

The library implements also two commitment schemes and evaluation arguments:

1. Pedersen commitments with IPA-based evaluation argument (supported on all three curve cycles), and
2. HyperKZG commitments and evaluation argument (supported on curves with pairings e.g., BN254).

## ZoKrates

[zokrates.github.io/](https://zokrates.github.io/)

ZoKrates is a toolbox for zkSNARKs on Ethereum. It helps you use verifiable computation in your DApp, from the specification of your program in a high level language to generating proofs of computation to verifying those proofs in Solidity.



## Iden3

### snarkjs

[GitHub](https://github.com/iden3/snarkjs)

snarkjs is an implementation in JavaScript and WASM of zkSNARK and PLONK schemes.

It uses the Groth16 Protocol (3 point only and 3 pairings), PLONK and FFLONK.

### rapidsnark

[GitHub](https://github.com/iden3/rapidsnark)

Rapidsnark is a zkSnark proof generation written in C++ and intel/arm assembly. That generates proofs created in [circom](https://github.com/iden3/snarkjs) and [snarkjs](https://github.com/iden3/circom) very fast.

Old version: [https://github.com/iden3/rapidsnark-old](https://github.com/iden3/rapidsnark-old)

## Polygon

### Plonky2

[Github](https://github.com/0xPolygonZero/plonky2)

Plonky2 is a recursive SNARK natively compatible with Ethereum. It combines PLONK and [FRI](https://aszepieniec.github.io/stark-anatomy/fri.html)(*Fast Reed-Solomon IOP of Proximity*,):

- for the best of STARKs, with fast proofs and no trusted setup,  
- and the best of SNARKs, with support for recursion and low verification  cost on Ethereum.

 Plonky2 uses a small Goldilocks field and supports efficient recursion. 

Reference: [Polygon Introducing Plonky2](https://polygon.technology/blog/introducing-plonky2)

### Plonky3

[github.com/Plonky3/Plonky3](https://github.com/Plonky3/Plonky3)

Plonky3 is a toolkit which provides a set of primitives, such as polynomial commitment schemes, for implementing polynomial IOPs (PIOPs). It is mainly used to power STARK-based zkVMs, though in principle it may be used for PLONK-based circuits or other PIOPs.

See also [polygon.technology - plonky3](https://polygon.technology/plonky3)

### Starky

[GitHub](https://github.com/0xPolygonZero/plonky2/tree/main/starky)

Starky is a highly performant STARK framework from Polygon Zero. 

Unfortunately, I didn't find more information on that.