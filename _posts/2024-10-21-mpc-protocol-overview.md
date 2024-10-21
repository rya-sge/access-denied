```
layout: post
title:  Overview, security and applications of Multi-Party Computation (MPC)
date:   2024-09-19
lang: en
locale: en-GB
categories: blockchain cryptography
tags: blockchain wallet
description: This article is an introduction to Multi-Party Computation (MPC)Mathematical Foundation of MPC
image: 
isMath: true
```

**Multi-Party Computation (MPC)** is a cryptographic technique that enables multiple parties to jointly compute a function over their private inputs without revealing those inputs to one another. 

It ensures that while the participants collaborate to produce a common output, none of them has access to the others’ private data. 

MPC is a fundamental building block for privacy-preserving computations and is widely used in cryptography, financial technology, and decentralized systems.

The two main properties of MPC are correctness and privacy:

- **Correctness**: the output produced by an algorithm is correct (as expected).
- **Privacy**: the secret input data that a party holds would not leak to the other parties

This article explores the pros and cons of MPC, provides a deeper dive into its security guarantees, presents a threat model, and showcases real-world use cases, enriched with technical and mathematical details.

Here a schema for a basic MPC Protocol performing an addition.

![MPC]({{site.url_complet}}/assets/article/cryptographie/mpc/MPC.png)

Note: with only two participants, it clears that A and B can learns the other input by performing a subtraction, but it is for the example.

Reference: [wiki.mpcalliance.org](https://wiki.mpcalliance.org)

[TOC]



## Mathematical Foundation of MPC

At the core of MPC protocols are **cryptographic primitives** like **secret sharing**, **oblivious transfer**, and **homomorphic encryption**. The security and privacy of MPC rely on these concepts to ensure that data is hidden throughout the computation.

### Secret sharing

- One of the most common building blocks for MPC is **secret sharing**, such as **Shamir’s Secret Sharing**. In this scheme, a secret value x is divided into multiple parts (shares) such that only a certain threshold number of shares can reconstruct the secret, but fewer than the threshold reveals no information about x.

- Mathematical Definition:

  - To share a secret `s`, the dealer selects a random polynomial `f(x)` of degree <= `t−1` where `f(0)=s` . The dealer then distributes evaluations of the polynomial `f(i)` to participant `i`.

  $$
  f(x) = a_0 + a_1x + a_2x² + a_3x³ + ... + a_(t-1)x⁽t-1)
  $$

  

  - The secret can be reconstructed using Lagrange interpolation if at least `t` participants collaborate:

  $$
  s = f(0) = \sum_{i=1}^{t} s_i \cdot \lambda_i(0)
  $$

  where `λi(0)` are Lagrange basis polynomials.

- Shamir’s Secret Sharing is widely used in **threshold MPC** schemes, where any t-out-of-n parties can reconstruct the final result.

Reference: [purdue - Lecture 07: Shamir Secret Sharing (Lagrange Interpolation)](https://www.cs.purdue.edu/homes/hmaji/teaching/Fall%202018/lectures/07.pdf), [Wikipedia - Shamir's secret sharing](https://en.wikipedia.org/wiki/Shamir%27s_secret_sharing), [NPTEL - Lec 07 Secret sharing](https://youtu.be/-86lvXoe7Qw?si=uLrsdBoVBhd41rQk)

### Oblivious Transfer (OT)

- OT initially proposed by Rabin in 1981

- In **Oblivious Transfer (OT)**, a sender holds two pieces of information, and the receiver chooses one without revealing their choice. The sender remains oblivious to which piece was selected.
- The protocol can be implemented by using several different algorithm, notably RSA or ECDSA
- One of the knwon implementation is the **1-out-of-2 OT** 
  - It is used as a fundamental tool in MPC protocols such as Yao's Garbled Circuits for securely transferring input data without revealing it (not sure).

Reference: [MPC - Oblivious Transfer](https://wiki.mpcalliance.org/Oblivious%20Transfer.html), [MPC Techniques Series, Part 5: What is Oblivious Transfer, and why should you care?](https://medium.com/partisia-blockchain/what-is-oblivious-transfer-and-why-should-you-care-db40d246ac0), [Devious Transfer: Breaking Oblivious Transfer-based Threshold ECDSA](https://blog.fordefi.com/devious-transfer-breaking-oblivious-transfer-based-threshold-ecdsa), [Wikipedia - Oblivious transfer ](https://en.wikipedia.org/wiki/Oblivious_transfer), [NPTEL - Lec 37 Oblivious Transfer (OT)](https://www.youtube.com/watch?v=1s-bKKdElAU&list=PLgMDNELGJ1Ca3l-xioOzN86BIZ2a0N8Ds&index=38)

### Homomorphic Encryption

- In **Homomorphic Encryption (HE)**, operations can be performed on encrypted data without decrypting it. This enables MPC participants to operate on encrypted inputs without revealing their actual data.
- For example, a partially homomorphic encryption scheme like **Paillier** supports additive operations: 

$$
Enc(m_1) \cdot Enc(m_2) = Enc(m_1 + m_2)
$$



- Fully Homomorphic Encryption (FHE), though computationally expensive, allows arbitrary operations on encrypted data.

Reference: [Partisia - MPC Techniques Series, Part 7: Homomorphic Encryption](https://medium.com/partisia-blockchain/mpc-techniques-series-part-7-homomorphic-encryption-7ece9e24ff5f)

## Pros & Cons of MPC

| Pros                                                         | Cons                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| - Privacy Preservation<br />- Decentralized Trust<br />- Fault Tolerence | - High Computational Overhead<br />- Communication Complexity<br />- Implementation Complexity<br />- Dependency on Network Availability<br /> (depends of the threshold) |



### Pros

**1. Privacy Preservation:**

- MPC ensures that participants’ inputs remain private throughout the computation. Using techniques like secret sharing or garbled circuits, no individual party learns anything beyond the final result.
- Example: In an MPC-based voting system, voters’ choices remain secret, but the total count can still be computed.

**2. Decentralized Trust:**

- MPC eliminates the need for a trusted third party. Parties can collaborate without trusting each other, as the security of the protocol ensures that no party can gain access to others' inputs.

**3. Fault Tolerance:**

- Many MPC protocols are threshold-based, meaning computations can proceed even if some parties are unavailable or corrupted, as long as the number of honest participants exceeds the threshold ttt.
- Example: In an MPC-based crypto wallet, even if one party's share of the private key is lost or compromised, the system can still function if the required threshold number of parties is available.

------

### Cons of MPC

**1. High Computational Overhead:**

- MPC protocols often involve multiple rounds of communication and cryptographic operations (e.g., secret sharing, homomorphic encryption), which can lead to significant computational overhead.
- For instance, **Fully Homomorphic Encryption (FHE)**, while powerful, remains too slow for many practical applications, requiring large amounts of computation to perform even basic arithmetic operations.

**2. Communication Complexity:**

Many MPC protocols require parties to exchange a large number of messages. For example, in the **GMW protocol** (Goldreich, Micali, Wigderson), every gate in a Boolean circuit requires a round of communication (an interactive *OT*) for AND gates, which can be inefficient in complex circuits.

See also [NPTEL - Lec 36 GMW MPC protocol](https://www.youtube.com/watch?v=YiwTVQFkAQQ&list=PLgMDNELGJ1Ca3l-xioOzN86BIZ2a0N8Ds&index=37), [GMW vs. Yao? Efficient Secure Two-Party Computation with Low Depth Circuits](https://fc13.ifca.ai/proc/8-3.pdf)

**3. Implementation Complexity:**

Designing and implementing MPC systems is non-trivial. Developers must carefully consider the cryptographic assumptions, adversarial models, and network communication to avoid security pitfalls.

**4. Dependency on Network Availability:**

Since MPC requires real-time communication between participants, network availability and reliability are critical. In decentralized systems, unreliable network conditions can cause delays or failure in completing computations.

------

## Security & Threat Model of MPC

The **security** of an MPC protocol ensures that no party can learn anything beyond what can be inferred from the result of the computation. This is formalized under different security models:

### 1. Semi-Honest

**Semi-Honest (passive) Attackers (Honest-but-Curious):**

External attackers might attempt to intercept communication between parties. 

- In this model, the attacker follows the protocol correctly but may try to infer information from the messages they receive. MPC protocols secure against semi-honest adversaries ensure that the protocol does not leak information and no party learns any private input beyond the final output.
- **Example**: In Yao's Garbled Circuits, each party receives garbled values but cannot infer the actual inputs.

Secure MPC protocols rely on encryption to protect against such eavesdropping attacks.

### 2. Malicious (active) Attackers

Malicious attackers may deviate from the protocol in an attempt to corrupt the computation or learn private data. To be secure against malicious adversaries, MPC protocols must incorporate additional mechanisms to detect and prevent cheating, such as **zero-knowledge proofs** to ensure correct behavior.

- **Example**: Protocols like SPDZ (pronounced "SPeeDz") offer malicious security by using **MACs (Message Authentication Codes)** and public-key encryption to ensure integrity and correctness, even when some parties behave maliciously.

See [Partisia - MPC Techniques Series, Part 9: SPDZ](https://medium.com/partisia-blockchain/mpc-techniques-series-part-9-spdz-dbe1b7381e3b)

### 3. Internal Malicious Parties

#### Individual

A participant may attempt to deviate from the protocol to gain additional information or tamper with the result. 

Protocols resistant to **malicious adversaries** include additional checks to detect incorrect behavior, such as verifying commitments or using zero-knowledge proofs.

#### Collusion Resistance

MPC protocols typically provide security against collusion, meaning that a subset of participants cannot combine their information to learn the inputs of non-colluding participants, as long as their size is smaller than the predefined threshold.

##### Threshold MPC protocol (specific case)

For threshold MPC protocol, we can also add a last security model where we have at most `t`corrupted parties (semi-honest or malicious) among `n`participants.

The protool must be secure against  `t < n/2`, so before the threshold limit.

The set of corrupted parties can be static or dynamic, across protocol runs.

**Threshold cryptography** in MPC ensures that even if `t−1` parties collude, they cannot reconstruct the secret or tamper with the result. 

### 4. Denial-of-Service (DoS) Attacks

Malicious parties could attempt to disrupt the computation by refusing to participate or sending invalid data. Some MPC protocols are designed to be **Byzantine-fault-tolerant**, allowing the system to proceed even if a subset of parties is unresponsive or actively trying to sabotage the computation.

### Use Cases of MPC

![MPC-useCase.drawio]({{site.url_complet}}/assets/article/cryptographie/mpc/MPC-useCase.drawio.png)

**1. MPC for Crypto Wallets:**

- MPC, with a Threshold Signature Scheme (TSS), is widely used in **cryptocurrency wallets** to split private keys among multiple parties, preventing any single party from having complete control over the private key. 
- **Example**: In a threshold cryptographic wallet, the private key is shared among multiple devices or service providers. When a transaction is signed, these parties jointly compute the signature without any one of them reconstructing the private key. This ensures higher security against key theft and misuse.
- Company: [Fireblocks](https://www.fireblocks.com/secure-multi-party-computation-framework/), [Zengo](https://zengo.com/mpc-wallet/)

**2. Privacy-Preserving Data Analytics:**

- MPC enables organizations to compute joint analytics on sensitive data without sharing it.
- **Example**: In healthcare, hospitals could use MPC to jointly analyze patient data across institutions to identify trends in disease outbreaks while keeping individual records private.

**3. Secure Auctions:**

- MPC could be used to implement **sealed-bid auctions**, where participants submit bids privately, and the auction is computed without revealing the actual bids.
- **Example**: A secure auction system might use MPC to determine the highest bidder without revealing the bids of other participants.

Reference: [Harvard - A Practical Implementation of Secure Auctions Based on Multiparty Integer Computation](http://www.eecs.harvard.edu/~cat/cs/diss/paperlinks/bogetoft06practical.pdf)

**4. Private Set Intersection (PSI):**

- MPC enables two or more parties to compute the intersection of their datasets without revealing the non-overlapping elements.
- **Example**: 
  - Companies can use MPC to compare customer lists to identify shared clients without disclosing the entire list of customers. 
  - A concrete use is by Apple for its CSAM - Child Sexual Abuse Material. Apple uses a PSI to flag accounts exceeding a threshold number of images that match a known database of CSAM image hashes. As the result, Apple does not learn anything about images that do not match the known CSAM database and until a threshold of matches. 
  - Reference: [Apple - CSAM detection](https://www.apple.com/child-safety/pdf/CSAM_Detection_Technical_Summary.pdf), [The Private Set Intersection (PSI) Protocol of the Apple CSAM Detection System](https://decentralizedthoughts.github.io/2021-08-29-the-private-set-intersection-psi-protocol-of-the-apple-csam-detection-system/)


Reference: [Taurus  MPC and smart contracts: same but different ](https://www.taurushq.com/blog/mpc-smartcontract/)

**5. Electronic Voting:**

- MPC can be used in **secure electronic voting systems**, where voters’ ballots remain private, and the final tally is computed without revealing individual votes. This ensures both privacy and integrity of the election process.

------

### Conclusion

**Multi-Party Computation (MPC)** provides a privacy-preserving method of collaborative computation, ensuring that data remains private while allowing useful joint computations. 

TThe technology is powerful and applicable to numerous domains like:

- cryptocurrency
- secure voting, 
- and privacy-preserving data analytics,

Nevertheless, it comes with challenges such as computational overhead and communication complexity. 

The threat models considered in MPC protect against malicious adversaries, collusion, and availability attacks, making it robust for decentralized, trustless environments.

## Reference

- [wiki.mpcalliance.org](https://wiki.mpcalliance.org)
- MPC Partisia article:
  - [MPC Techniques Series, Part 1: Secret Sharing](https://medium.com/partisia-blockchain/mpc-techniques-series-part-1-secret-sharing-d8f98324674a)
  - [MPC Techniques Series, Part 2: Security Taxonomy and Active Security](https://medium.com/partisia-blockchain/mpc-techniques-series-part-2-security-taxonomy-and-active-security-6b5f14a15217)
  - [MPC Techniques Series, Part 5: What is Oblivious Transfer, and why should you care?](https://medium.com/partisia-blockchain/what-is-oblivious-transfer-and-why-should-you-care-db40d246ac0)
  - [MPC Techniques Series, Part 7: Homomorphic Encryption](https://medium.com/partisia-blockchain/mpc-techniques-series-part-7-homomorphic-encryption-7ece9e24ff5f)
  - [MPC Techniques Series, Part 9: SPDZ](https://medium.com/partisia-blockchain/mpc-techniques-series-part-9-spdz-dbe1b7381e3b)
- Shamir Secret Sharing
  - [MPC - Oblivious Transfer](https://wiki.mpcalliance.org/Oblivious%20Transfer.html), [MPC Techniques Series, Part 5: What is Oblivious Transfer, and why should you care?](https://medium.com/partisia-blockchain/what-is-oblivious-transfer-and-why-should-you-care-db40d246ac0)
  - [Devious Transfer: Breaking Oblivious Transfer-based Threshold ECDSA](https://blog.fordefi.com/devious-transfer-breaking-oblivious-transfer-based-threshold-ecdsa)
  - [Wikipedia - Oblivious transfer ](https://en.wikipedia.org/wiki/Oblivious_transfer), [NPTEL - Lec 37 Oblivious Transfer (OT)](https://www.youtube.com/watch?v=1s-bKKdElAU&list=PLgMDNELGJ1Ca3l-xioOzN86BIZ2a0N8Ds&index=38)
- ChatGPT with the inputs "Write me an article about MPC, the pros and cons, with also a paragraph to discuss its security, a threat model and its use case", "Complete with some mathematical and technical details"
