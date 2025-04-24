---
layout: post
title: Overview of ECDSA - Elliptic Curve Digital Signature Algorithm
date:   2024-10-23
lang: en
locale: en-GB
categories: blockchain cryptography
tags: blockchain wallet ecdsa elliptic-curve
description: Learn how ECDSA (Elliptic Curve Digital Signature Algorithm) works, its role in digital signatures, and its different use cases, notably in Blockchain.
image: 
isMath: true
---

The **Elliptic Curve Digital Signature Algorithm (ECDSA)** is a widely used cryptographic algorithm for creating digital signatures. Based on **elliptic curve cryptography (ECC)**, ECDSA provides a high level of security with smaller key sizes compared to older algorithms like RSA, making it more efficient. 

This efficiency is a key reason why ECDSA is employed in secure communications, identity verification, and especially **blockchain** technologies.

[TOC]

## How ECDSA Works

ECDSA operates over the algebraic structure of elliptic curves, which are defined by equations of the form:
$$
\begin{aligned}
y^2 = x^3 + ax + b \mod p
\end{aligned}
$$
Where `a`, `b`, and `p` are constants that define the specific elliptic curve. The points on the curve, along with a special point at infinity, form a group under an operation called **point addition**.

### Summary

1. Choose an elliptic curve, cryptographically secure
2. Private key

$$
\begin{aligned}
a ∈ \{1,...., n -1\}
\end{aligned}
$$

2. public key

$$
\begin{aligned}
A = aG
\end{aligned}
$$

### Key Generation

To generate a key pair in ECDSA, the process follows these steps:

1. **Private Key**: Randomly select a private key `a`, which is a number in the range `1 ≤ a ≤ n-1`, where `n` is the order of the base point `G` on the curve.

$$
\begin{aligned}
a ∈ \{1,...., n -1\}
\end{aligned}
$$



2. **Public Key**: The corresponding public key is calculated as:

$$
\begin{aligned}
A = aG
\end{aligned}
$$

where `G` is the generator point of the elliptic curve, and the result`A` is a point on the curve.

### Signing

To sign a message `m`, the signer performs the following steps:

1.**Hash the message**: Let `h` be the hash of the message `m`.

2. Select a random integer `k` from `[1, n-1]`.

$$
\begin{aligned}
k ∈ \{1, . . . , n − 1\}
\end{aligned}
$$



3.Calculate the point 
$$
\begin{aligned}
(x_1, y_1) = kG
\end{aligned}
$$



4. The signature `r` is defined as:

$$
\begin{aligned}
r = x_1 \mod n
\end{aligned}
$$



If `r = 0`, select a new `k` and repeat the process.

5. The signature `s` is computed as:

$$
\begin{aligned}
s = \frac{h + ar}{k} mod~ n = k^{-1}(h + ar)~mod ~n
\end{aligned}
$$

If `s = 0`, select a new `k` and repeat the process.

The signature is the pair `(r, s)`.

### Verification

To verify a signature `(r, s)` on a message `m`, the verifier must perform the following:

1. Ensure that `r` and `s` are within the valid range `[1, n-1]`.
2. Calculate `h`, the hash of the message.

3. Calculate 

$$
\begin{aligned}
u_1 = \frac{h}{s} mod ~ n = h * s^{-1} \mod n
\end{aligned}
$$

$$
\begin{aligned}
u_2 = \frac{r}{s} mod ~ n
\end{aligned}
$$

4.Calculate the point:
$$
\begin{aligned}
(x_2, y_2) = u_1G + u_2A
\end{aligned}
$$



5.The signature is valid if:
$$
\begin{aligned}
r \equiv x_1 \mod n
\end{aligned}
$$

If this condition holds, the signature is valid; otherwise, it is invalid.

## Use case

### ECDSA in Blockchain

ECDSA plays a critical role in **blockchain** technologies, particularly in **Bitcoin** and other cryptocurrencies. In blockchain systems, digital signatures are used to authorize transactions. When a user wants to transfer cryptocurrency, they sign the transaction using their private key, and others on the network can verify the signature using the corresponding public key.

In **Bitcoin**, for example:

- **Private Key**: Used by the user to sign a transaction, proving ownership of the cryptocurrency.
- **Public Key**: Used by the network participants to verify the validity of the transaction.

This ensures the integrity of the blockchain by making it computationally infeasible for anyone to forge signatures or tamper with transactions.

#### ECDSA in a Bitcoin Transaction

1. **Creating the transaction**: The owner uses their private key to sign the transaction, which includes details like the amount and the recipient's address.
2. **Broadcasting the transaction**: The transaction is broadcast to the network.
3. **Verification**: Miners and nodes verify the signature using the sender's public key before accepting the transaction as valid.

By relying on ECDSA, blockchain systems can maintain decentralized trust and security.

## Security of ECDSA

The security of ECDSA relies on the hardness of two mathematical problems:

1. **Elliptic Curve Discrete Logarithm Problem (ECDLP)**: Given points `P` and `Q = dP`, it is computationally infeasible to determine the scalar `d`.
2. **Hash Function Resistance**: The algorithm depends on a secure cryptographic hash function (e.g., SHA-256) to ensure that message hashes cannot be reversed or manipulated.

#### Poor Random Number Generation

While ECDSA is secure when implemented correctly, it can be compromised by poor implementation practices. 

### Nonce (k) generation

#### Same nonce (k) for several signatures

##### Introduction

If the same `k` is reused for multiple signatures, an attacker can extract the private key `a`. This is because the equations for different signatures would lead to a system of equations that can be solved to reveal `a`.

##### Examples

An infamous example of this vulnerability occurred in 2010 when a programming flaw in the PlayStation 3's ECDSA implementation allowed hackers to break the system and extract Sony's private key. The issue arose because the same value of `k` was reused across signatures.

##### Details

For each signature, the value of `k` must be chosen randomly and uniquely. Otherwise, if two signatures share the same `k`, an attacker can easily compute the private key.

Given two signatures:
$$
\begin{aligned}
(r, s_1)
\end{aligned}
$$

$$
\begin{aligned}
s1 = \frac{h1 + ar}{k} mod~ n = k^{-1}(h1 + ar)~mod ~n
\end{aligned}
$$


And
$$
\begin{aligned}
(r, s_2)
\end{aligned}
$$

$$
\begin{aligned}
s2 = \frac{h2 + ar}{k} mod~ n = k^{-1}(h2 + ar)~mod ~n
\end{aligned}
$$

for messages `m_1` and `m_2` where the same `k` was used:
$$
\begin{aligned}
s_1 - s_2 = k^{-1}(h_1 + ar) - k^{-1}(h_2 + ar)
\end{aligned}
$$


This simplifies to:
$$
\begin{aligned}
s_1 - s_2 = k^{-1}(h_1 - h_2) ~mod ~ n
\end{aligned}
$$
Since `k` has the same value for the two signatures.

Thus, `k` can be recovered as:
$$
\begin{aligned}
k = \frac{h_1 - h_2}{s_1 - s_2} \mod n
\end{aligned}
$$
Once `k` is known, the private key `a` can be computed as:
$$
\begin{aligned}
a = \frac{s_1k - h_1}{r} \mod n
\end{aligned}
$$
This highlights the critical importance of using a secure random number generator for `k`.

You can find a script python for Ethereum (EC secp256k1) here: [github.com - pcaversaccio - ecdsa-nonce-reuse-attack](https://github.com/pcaversaccio/ecdsa-nonce-reuse-attack)

#### Nonce generation - Bad Randomness

A major issue is the use of weak or predictable random numbers for `k`, the ephemeral key in the signature generation process.

The following paragraphs is mainly taken from this great article from Kudelski: [POLYNONCE: A TALE OF A NOVEL ECDSA ATTACK AND BITCOIN TEARS](https://research.kudelskisecurity.com/2023/03/06/polynonce-a-tale-of-a-novel-ecdsa-attack-and-bitcoin-tears/)

Nonces are generally generated by using a pseudorandom number generator (PRNG) rather than being really random.

If the PRNG does not create nonce with enough entropy, it is possible to have a polynomial correlation between the different output of the PRNG, which in some specific cases, can be used to compute the private key used.

The two main conditions are the following:

- Batch of ECDSA signatures that are **consecutive** (meaning that the nonces are consecutive outputs from the same PRNG) 
- The signatures are ordered, meaning that you know the order in which these signatures have been generated.

These two conditions are filled by Bitcoin (and other blockchain). The research by Kudelski shows that several (old) bitcoin wallets have been drained due to this vulnerability.

## ECDSA Security Against Quantum Computers

ECDSA's security is currently based on the difficulty of solving the **Elliptic Curve Discrete Logarithm Problem (ECDLP)** using classical computers. However, the advent of **quantum computers** poses a significant threat to cryptographic algorithms, including ECDSA.

Quantum algorithms like **Shor's Algorithm** could potentially solve the ECDLP in **polynomial time**, drastically reducing the computational difficulty. 

In theory, this would allow quantum computers to break ECDSA by recovering private keys from public keys within feasible timeframes. This makes ECDSA vulnerable to future quantum attacks.

To mitigate this risk, cryptographic research is moving towards **post-quantum cryptography**, which aims to develop algorithms that are secure against both classical and quantum computers.

For now, while quantum computers capable of breaking ECDSA are not yet realized, the potential threat requires ongoing preparation and adaptation in cryptographic protocols.

### Resistance compared to RSA

According to this [article](https://research.kudelskisecurity.com/2021/08/24/quantum-attack-resource-estimate-using-shors-algorithm-to-break-rsa-vs-dh-dsa-vs-ecc/) from Kudelski Security, dated from 2021, Elliptic curve looks more vulnerable than RSA against quantum attack because elliptic curve keys are smaller than RSA key. This is because the best classical attack are more inefficient against EC than RSA. 

But the quantum attacks have similar time complexity between RSA and EC. Since the key is smaller for EC, the required qubit count is actually smaller to break ECDSA.

From the article:

| quivalent (classical) bit-security | Minimum qubits needed to attack RSA, DSA etc | Minimum qubits needed to attack ECDSA and similar EC schemes |
| ---------------------------------- | -------------------------------------------- | ------------------------------------------------------------ |
| 112                                | 4098                                         | 2042                                                         |
| 128                                | 6146                                         | 2330                                                         |
| 192                                | 15362                                        | 3484                                                         |

## Mindmap

Made with the help of ChatGPT

![ecdsa-mindmap-schema]({{site.url_complet}}/assets/article/cryptographie/ecdsa/ecdsa-mindmap-schema.png)

## FAQ

Quiz on ECC (Elliptic Curve Cryptography) from [Bill Buchanan - ECC questions](https://billatnapier.medium.com/elliptic-curve-cryptography-ecc-questions-9aa67c147c9b)

> Who was a co-inventor of ECC:
> A. Neal Koblitz
> B. Ron Rivest
> C. Adi Shamir
> D. Shafi Goldwasser
> E. Tahir ElGamal

Answer: A - Neal Koblitz

See

> Which curve did Satoshi Nakamoto select for Bitcoin:
> A. secp128r1
> B. secp160r1
> C. secp256k1
> D. secp256r1
> E. secp521r1

Answer: C - secp256k1

> Which curve is used for P256 - as used in TLS:
> A. secp128r1
> B. secp160r1
> C. secp256k1
> D. secp256r1
> E. secp521r1

Answer: D-secp256r1

> Which curve gives has 256-bit equivalent security:
> A. secp128r1
> B. secp160r1
> C. secp256k1
> D. secp256r1
> E. secp521r1

Answer: E-secp521r1

> Which is true about a private key in ECC:
> A. It is a random scalar value
> B. It is a non-changing scalar value
> C. It is a point on the curve

Answer: A-it is a random scalar value

> Which is true about a public key in ECC:
> A. It is a random scalar value
> B. It is a non-changing scalar value
> C. It is a point on the curve

Answer: C - It is a point on the curve

> Which signing method is used in Bitcoin and Ethereum:
> A. ECDSA
> B. EdDSA
> C. RSA
> D. ElGamal

A. ECDSA

More details is available in this article ECC: [bill's security - ECC](https://asecuritysite.com/cryptojs/crytojs_ecc)

## Reference

- Cryptography course (CRY) taught at HEIG-VD in 2020
- Cryptography course (CRY) taught at HEIG-VD in 2023
- [research.kudelskisecurity - QUANTUM ATTACK RESOURCE ESTIMATE: USING SHOR’S ALGORITHM TO BREAK RSA VS DH/DSA VS ECC](https://research.kudelskisecurity.com/2021/08/24/quantum-attack-resource-estimate-using-shors-algorithm-to-break-rsa-vs-dh-dsa-vs-ecc/)
- [Bill Buchanan - ECC questions](https://billatnapier.medium.com/elliptic-curve-cryptography-ecc-questions-9aa67c147c9b)
- ChatGPT with the input "Write an article explaining ecdsa, Details some use case, notably in blockchain and a topic on its security and known bad implementation (e.g. in the random generation)"