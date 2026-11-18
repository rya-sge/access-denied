---
layout: post
title: Chainlink DECO, zkTLS oracle 
date:   2025-01-13
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: cryptography blockchain ZKP
tags: chainlink oracle
description: "DECO, the zkTLS oracle from Chainlink: how a prover shows that data came from a TLS server, using commitments, key binding proofs and zero-knowledge proofs."
image: /assets/article/cryptographie/zero-knowledge-proof/deco/deco-tls-k.drawio.png
isMath: false
---

DECO is a zkTLS-oracle made by Chainlink for authenticating and verifying web data in a privacy-preserving manner.

> Warning: this article is still in draft state and its content is still mainly taken from several articles by Chainlink. See:
>
> - [DECO Research Series #1: An Introduction](https://blog.chain.link/deco-introduction/)
> - [DECO Research Series #2: Provenance and Authenticity](https://blog.chain.link/deco-provenance-and-authenticity/)
> - [DECO Research Series #3: Parsing the Response](https://blog.chain.link/deco-parsing-the-response/)
> - [DECO Research Series #4: Hiding Secret Lengths](https://blog.chain.link/hiding-secret-lengths/)

[TOC]

## What you need to know first

DECO combines an unmodified TLS session with a zero-knowledge proof, and the sections below rely on the following concepts without explaining them.

- **Blockchain oracles**: a smart contract cannot fetch web data itself, so an [oracle]({{site.url_complet}}/2024/04/16/build-blockchain-oracle/) brings off-chain data on-chain. DECO is presented as a zkTLS oracle: instead of relaying the data, it lets a user prove a claim about data obtained from a web server.
- **The TLS handshake and session keys**: at the start of a [TLS]({{site.url_complet}}/2024/11/04/TLS1.3-overview/) connection, the client and the server run a key exchange and authenticate the server, then derive symmetric session keys that encrypt every record. Anyone relaying the bytes sees only ciphertext, which is why the verifier can sit as a proxy without learning the data.
- **Diffie-Hellman key exchange**: in [Diffie-Hellman]({{site.url_complet}}/2021/10/28/diffie-hellman-python/), each party combines its own private value with the other's public value and both obtain the same shared secret. An observer of the public values cannot compute that secret, so the verifier in DECO does not learn the session key `K`.
- **Authenticated encryption and key commitment**: TLS 1.3 protects records with an AEAD cipher such as [AES-GCM]({{site.url_complet}}/2022/04/24/galois-counter-mode-gcm/) or ChaCha20-Poly1305. These ciphers are not key-committing: a ciphertext can be built that decrypts and authenticates correctly under two different keys, which is the opening the key binding proof closes.
- **Zero-knowledge proofs and soundness**: a [zero-knowledge proof]({{site.url_complet}}/2024/06/17/zero-knowledge-proof-main-concepts/) convinces a verifier that a statement is true without revealing anything beyond that fact. Soundness is the property that a cheating prover cannot convince the verifier of a false statement; decrypting with a wrong key `K′` would break it.
- **Interactive and non-interactive proofs**: an interactive proof is a back-and-forth exchange with a verifier who takes part live, while a non-interactive proof is a single message that anyone can check later. DECO's verifier already takes part in the TLS session, so DECO can use an interactive proof and its speed and memory advantages.
- **Boolean circuits**: a computation such as decrypting a record or checking a field can be written as a circuit of AND and XOR gates over bits. XOR is addition modulo 2 and AND is multiplication modulo 2, which is why an additively homomorphic commitment makes XOR gates free and leaves AND gates as the cost.
- **VOLE-based commitments**: vector oblivious linear evaluation (VOLE) is a two-party primitive that leaves the prover with a value `x` and a tag `M`, and the verifier with a key `K` and a global secret `Δ`, such that `M = K + x·Δ`. That relation acts as a commitment to `x`, and adding two of them gives a commitment to the sum, which is the additive homomorphism the article uses.



## Introduction

DECO enables a user to prove the authenticity of data and claims about it without revealing the data itself. 

Authenticity, in this context, means that the data is obtained from a specific web server through the [TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security) protocol. 

- Example

For example, a user can prove that she obtained her financial report from her bank’s website and that, according to this report, her account balance is above a particular amount. 

However, she does not reveal any other information present in the report, such as her account number or exact balance. 

![DECO overview: a user proves a claim about data fetched from a web server over TLS without revealing the rest of the data](https://blog.chain.link/wp-content/uploads/2024/10/DECO-Diagrams-V3_Generic-2.png)

- Integration

DECO requires no server side cooperation. 

The TLS server does not have to be modified or even be aware that it is participating in the DECO protocol, greatly simplifying DECO’s path to adoption. 

![https://blog.chain.link/wp-content/uploads/2023/03/deco-in-action-2048x1152.png](https://blog.chain.link/wp-content/uploads/2023/03/deco-in-action-2048x1152.png)



## A (Very) Brief Overview of Interactive Zero-Knowledge Proofs (ZKPs)

DECO adds a ZKP layer to the TLS protocol to ensure privacy. 

If you want an introduction to ZKP, you can read my article [Main Concept Behind Zero-Knowledge Proof](https://rya-sge.github.io/access-denied/2024/06/17/zero-knowledge-proof-main-concepts/)

In TLS, the identity of the server is verified using fresh challenges generated by the client for every session. This makes TLS, and in turn DECO, **interactive protocols**. 

Therefore, DECO uses an interactive “commit-and-prove” form of ZKP called VOLE-based ZKP in order to benefit from its higher speed, lower memory footprint, and scalability compared to non-interactive ZKP. 

### Commitments

#### Reminder

- Commitments are a cryptographic concept that can be viewed as a locked box. The prover *committing* to a variable x is analogous to putting x in a locked box and sending it to the verifier. 

- The verifier cannot view the committed value but has the guarantee that the prover cannot change it once sent. 
- Later, the prover can send the key to the verifier to *open* the commitment. We denote the commitment to x with `[x]`. 

![zero-knowledge-proof-Commitment.drawio]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/deco/zero-knowledge-proof-Commitment.drawio.png)

#### Commit-and-prove ZKP protocol 

Given commitments to the inputs of a logic gate (AND/XOR), a commit-and-prove ZKP protocol enables the prover and verifier to compute the commitment to the output. 

This in turn enables the prover to prove the correct computation of a circuit consisting of these gates through the following steps: 

(i) The prover commits to the inputs of the circuit.

(ii) Together the prover and the verifier compute the commitments to the outputs of the gates going through them in topological order.

(iii) The prover opens the commitments to the outputs of the circuit. 

#### Additively homomorphic

The commitment scheme used in the DECO ZKP core is `additively homomorphic`. 

This means that the commitment to the output of an XOR gate (addition modulo 2) can be computed locally without incurring any communication or computation cost. The cost of evaluating a circuit through the ZKP protocol is thus linear in the number of AND gates. 

As a reminder, here the table for the XOR operation

| Input 1 | Input 2 | Addition view | Result X |
| ------- | ------- | ------------- | -------- |
| 0       | 0       | (0 + 0) % 2   | 0        |
| 1       | 0       | (1 + 0) % 2   | 1        |
| 0       | 1       | (0 + 1) % 2   | 1        |
| 1       | 1       | (1 + 1) % 2   | 0        |

## Provenance and Authenticity

### Context

DECO involves three parties: 

1. The prover (Alice, “she”), 
2. the verifier (Bob, “he”), 
3. and the TLS server (Charlie, “it”). 

In TLS, authentication of the server relies on secret challenges generated by the client (prover in DECO) for every new session. 

This makes TLS an interactive protocol. Therefore, the verifier needs to be a part of the protocol execution to be able to verify the authenticity of data. 

#### Solution

The solution is to put the verifier as a proxy between the prover and the server and recording the bytes communicated as part of the TLS protocol. 

These bytes are later used as the “truth” known by both prover and verifier in the proofs of authenticity. Note that TLS ensures the privacy of data from any eavesdropper, in this case the verifier.

The server is oblivious ("not aware") to its participation in the DECO protocol. 

This requires the TLS protocol to be executed without any modification, and DECO thus follows steps in the TLS protocol precisely. 

1. First, the TLS session keys are generated by the prover together with the server; the verifier, acting as a proxy, does not take part in the key exchange. 
2. Then the keys are used to decrypt the TLS ciphertext.

![DECO provenance: the verifier sits as a proxy between the prover and the TLS server and records the encrypted bytes exchanged, which later serve as the truth shared by both parties in the proof](https://blog.chain.link/wp-content/uploads/2023/04/deco-diagram-provenance-2048x1153.png)

### TLS Key Agreement and Key Binding Proofs

At the beginning of the TLS protocol, the prover and server generate a TLS session key `K` using a key exchange protocol, e.g., [Diffie–Hellman](https://en.wikipedia.org/wiki/Diffie–Hellman_key_exchange). 

![deco-tls-k.drawio]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/deco/deco-tls-k.drawio.png)

The verifier does not learn K (otherwise TLS wouldn’t be secure). 

This is the proxy mode described in the Chainlink series. The default protocol of the original DECO paper uses instead a *three-party handshake*: the prover and the verifier jointly act as the TLS client, and the session keys are secret-shared between them, so that neither of them holds K alone. 

#### Use of invalid key K′

However, this creates a security problem 

> what if the prover later uses an invalid key K′ in the subsequent [ZKP](https://chain.link/education/zero-knowledge-proof-zkp) proofs? 

This is possible because encryption algorithms in modern TLS are not committing, which means that a ciphertext can be decrypted in multiple ways. This may allow the prover to decrypt the ciphertext to something the server has never sent, causing a soundness violation. 

The solution in DECO is to ask the prover to show a `key binding proof` to prove that the commitment `K` to the session key is generated correctly.

The goal of a key binding proof is for the prover to convince the verifier that a session key K is uniquely bound to the session recorded by the verifier. 

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Oracle** | A system that brings off-chain data, such as web data, to a blockchain application. |
| **zkTLS** | The family of protocols that let a user prove, with zero-knowledge proofs, facts about data received over a TLS connection. |
| **DECO** | Chainlink's zkTLS oracle, which lets a user prove the authenticity of web data and claims about it without revealing the data and without any change on the server side. |
| **TLS** | The protocol that secures a connection between a client and a web server; in DECO, it is what makes data "authentic", meaning obtained from a specific server. |
| **Session key (`K`)** | The symmetric key generated at the start of a TLS session by the prover and the server, which the verifier does not learn. |
| **Diffie-Hellman key exchange** | A key exchange protocol through which the prover and the server agree on the TLS session key. |
| **Prover, verifier and TLS server** | DECO's three parties: the prover (Alice) proves a claim, the verifier (Bob) checks it, and the TLS server (Charlie) provides the data without knowing it takes part. |
| **Interactive protocol** | A protocol in which the parties exchange messages during the run; TLS is one because the client issues fresh challenges each session, and DECO inherits this. |
| **Zero-knowledge proof (ZKP)** | A proof that convinces a verifier of a statement without revealing anything else, used by DECO to keep the data private. |
| **Soundness** | The guarantee that a prover cannot convince the verifier of something false, such as a plaintext the server never sent. |
| **Commitment** | A cryptographic "locked box": the prover commits to a value `x`, which the verifier cannot see but the prover can no longer change, written `[x]`. |
| **Opening** | The step where the prover reveals a committed value to the verifier, like handing over the key to the locked box. |
| **Commit-and-prove ZKP** | A ZKP in which the prover commits to a circuit's inputs, both parties compute commitments to every gate's output in topological order, and the prover opens the outputs. |
| **VOLE-based ZKP** | The interactive commit-and-prove ZKP that DECO uses, chosen for its speed, low memory footprint and scalability compared with non-interactive ZKPs. |
| **Additively homomorphic commitment** | A commitment where the commitment to a sum can be computed from the commitments to its terms, which lets XOR gates be evaluated locally at no cost. |
| **XOR and AND gates** | The two gate types of the circuits DECO proves; XOR (addition modulo 2) is free, so the proof cost grows linearly with the number of AND gates. |
| **Provenance and authenticity** | The property that the data comes from a given server over TLS, which DECO obtains by having the verifier record the TLS bytes as a proxy. |
| **Committing encryption** | An encryption scheme where a ciphertext can only be decrypted under one key; the ciphers of modern TLS are not committing, so a ciphertext can decrypt in several ways. |
| **Key binding proof** | The proof by which the prover shows that the committed session key `K` was generated correctly and is uniquely bound to the session the verifier recorded. |

## References

- [Chainlink DECO Sandbox](https://blog.chain.link/deco-sandbox/)
- [Zhang et al. - DECO: Liberating Web Data Using Decentralized Oracles for TLS (CCS 2020, extended version)](https://arxiv.org/abs/1909.00938)
- [DECO Research Series #1: Introduction](https://blog.chain.link/deco-introduction/)
- [DECO Research Series #2: Provenance and Authenticity](https://blog.chain.link/deco-provenance-and-authenticity/)
- [DECO Research Series #3: Parsing the Response](https://blog.chain.link/deco-parsing-the-response/)
- [DECO Research Series #4: Hiding Secret Lengths](https://blog.chain.link/hiding-secret-lengths/)