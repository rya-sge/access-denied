---
layout: post
title:  Introduction to Shamir’s Secret Sharing - How to share a secret
date:   2024-10-29
lang: en
locale: en-GB
categories: blockchain cryptography
tags: blockchain wallet
description: Shamir's Secret Sharing (SSS) is a cryptographic technique that allows to split a secret, such as a private key, into multiple shares distributed among trusted parties. Only a specified threshold of shares is required to reconstruct the secret, ensuring security against unauthorized access.
image: /assets/article/blockchain/wallet/ledger/Ledger-recover.drawio.png
isMath: true
---

**Shamir's Secret Sharing** (SSS) is a cryptographic method developed by Israeli cryptographer Adi Shamir in 1979 in the paper *How to share a secret*. I

t enables a secret to be divided into multiple parts, known as "shares," which can be distributed among participants. Only a subset of these shares, a threshold number, is required to reconstruct the original secret. 

This technique provides a secure way to protect sensitive information by splitting it, ensuring that no single person can access the information alone unless they gather a specific number of shares.

For example, if a business wants to protect its most critical secret, it can split it into multiple parts and set a rule where only a certain number of executives together can reconstruct it. 

This principle is highly relevant in protecting sensitive data, like cryptographic keys in digital wallets.

### Use case

The three main use cases are:

- Multi-party computation
- Protection against side-channel attack (masking)
- Share a secret between different locations/people: unlock the secret requires to have enough shares

### The Mechanics of Shamir’s Secret Sharing

Shamir’s Secret Sharing is based on polynomial interpolation. A secret S is encoded as the constant term in a polynomial equation of degree `t−1`, where `t` is the **threshold** number of shares required to reconstruct the secret. Here’s a simplified breakdown of the process:

1. **Define a polynomial**: For a given secret S, create a random polynomial 

$$
f(x) = a_0 + a_1x + a_2x² + a_3x³ + ... + a_{(t-1)}x^{(t-1)}
$$



1. **Generate shares**: Assign each share a unique x value, and compute f(x) to generate each share as a point (x,f(x))
2. **Reconstruction**: To reconstruct the secret, a subset of `t` or more shares is required. By using Lagrange interpolation, the participants can reconstruct the polynomial and, thus, the constant term a0=S which is the original secret.

$$
S = f(0) = a_0 
$$

If fewer than t shares are available, there is not enough information to reconstruct the polynomial, and the secret remains safe.

### Share generation in Practice

- It is important that the shares are different evaluation of the polynomial
- It is important that we do not give the evaluation at 0
- In practice, increment a counter `i` starting at 1 and let (i, p(i)) be the share
- The secret is often a chain of n bits. Then

$$
K ∈ GF(2^n)
$$

This is also the case for the coefficients of the polynomial.

The share is then an element of 
$$
(GF(2^n))²
$$

## Secret Recovery

- To recover the secret, apply **Lagrande interoplation** on `t` shares (no need for more)
- We don't need the polynomial, but only `f(0)`
- This simplify the computation since we only need to compute `f(0)`

### Properties

- Information-theorice security
- Extensibility: for fixed `t`, shares can be added without changing the original ones
- Flexibility: in hierarchical organizations, it is possible to give peaople a different number of shares depending on their importance inside the organizatin

### Security of Shamir’s Secret Sharing: A Threat Model

Shamir’s Secret Sharing offers a high level of security and resilience against specific threats:

1. **Confidentiality**: Since each share does not reveal any information about the secret by itself, unauthorized access to any subset with fewer than `t` shares provides no advantage in recovering the secret.
2. **Integrity**: Shares can be validated during the reconstruction process, reducing the risk of tampering.
3. **Redundancy**: By distributing shares among a group, Shamir’s Secret Sharing offers protection against loss of data. As long as the threshold `t` shares are available, the secret can be reconstructed even if other shares are lost or destroyed.

#### Threat Model Analysis

When considering Shamir's Secret Sharing as a security measure, we can outline the following threat scenarios:

- **Insider Threats**: If a trusted party tries to act maliciously, they would need the cooperation of other trusted parties to meet the threshold number of shares. This division of trust prevents single points of failure and minimizes the risk of insiders accessing the secret independently.
- **External Adversaries**: An external attacker attempting to reconstruct the secret would need to gather the threshold number of shares, which might be stored in separate, secure locations. The distribution reduces the risk of a single breach compromising the entire system.
- **Data Loss or Corruption**: If shares are lost, such as through hardware failure or accidental deletion, as long as enough shares are intact to meet the threshold, the secret can be recovered. This characteristic provides protection against data loss compared to single-point storage solutions.

### Shamir’s Secret Sharing in Cryptocurrency Wallets

Cryptocurrency wallets, especially those managing large amounts of assets, face unique security challenges. Cryptocurrency wallets generally store private keys, which are the only means of accessing and transferring digital assets. If a private key is lost or stolen, the associated funds can be permanently lost. This risk has led to the adoption of Shamir’s Secret Sharing for wallet security.

#### Use Cases in Crypto Wallet Security

1. **Seed Phrase Protection**: Wallets often use a seed phrase, which is a series of words that generates the private key. Protecting this phrase is critical because anyone with access to it can control the wallet. Shamir’s Secret Sharing can be used to split the seed phrase into multiple shares, distributed to various secure locations or people.
2. **Multi-Party Wallets**: In corporate or institutional settings, Shamir's Secret Sharing enables a multi-signature-like setup, where multiple authorized parties must collaborate to reconstruct the private key. This setup aligns well with governance policies, such as requiring approvals from multiple executives to initiate a transaction.
3. **Backup and Recovery**: For individuals concerned about the loss of access to their wallet, Shamir’s Secret Sharing provides a recovery mechanism. By distributing shares across different storage solutions—such as a safe deposit box, a trusted family member, or a secure digital vault—the individual can regain access to their wallet even if one or more shares are lost or inaccessible.

### Practical Implementation and Challenges

While Shamir’s Secret Sharing offers substantial security benefits, practical implementation in crypto wallets involves challenges:

- **Storage and Security of Shares**: Each share needs to be stored securely to prevent unauthorized access. A poorly stored share could become a vulnerability.
- **Threshold Management**: Setting an appropriate threshold is crucial. If the threshold is too high, it may be difficult to gather enough shares if some are lost; if too low, security could be compromised.
- **Handling Corruption or Loss**: While Shamir’s Secret Sharing is resilient, share corruption (e.g., through bit rot in digital storage) can compromise reconstruction. Solutions like error-checking mechanisms and regular integrity checks are recommended.

### Comparing Shamir’s Secret Sharing with Alternative Security Solutions

Other techniques, such as multi-signature wallets, offer similar security benefits. Multi-signature (multisig) wallets require multiple private keys for transaction approval, and each participant has a private key rather than a share of a single key. The main advantages of Shamir's Secret Sharing over multisig include:

- **Enhanced Flexibility in Share Distribution**: Shamir's Secret Sharing allows for more dynamic distribution of shares, including options for hierarchical access structures.
- **Lower On-Chain Complexity**: Shamir's Secret Sharing operates off-chain, avoiding the added transaction fees and complexities that multisig can entail.

However, multisig offers the advantage of native blockchain support for some cryptocurrencies, which can make it easier to implement on a technical level.

## Example

### Ledger Recover

Ledger Recover is an optional paid subscription service from Ledger which allows you to back up your wallet’s SRP using a specific variant of Shamir’s Secret Sharing, called Pedersen’s Verifiable Secret Sharing (PVSS).

![Ledger-recover.drawio]({{site.url_complet}}/assets/article/blockchain/wallet/ledger/Ledger-recover.drawio.png)

#### Consent

Firstly, to initiate the process, the user need to physically consent to it using its device. 

#### Creation

After that, the secure element:

- duplicates;
- encrypts;
- and splits an encrypted version of the seed phrase (called the entropy) into three fragments. 

### Transmission

From there, these encrypted fragments will be sent through three independent secure channels to these fragments’ backup providers. The secure channel allows mutual authentication and avoids man-in-the-middle attacks.

During the process, the secure channel uses an ephemeral symmetric key to securely transport the fragments. 

#### Security

- Company

To ensure your backup’s security, a separate and independent company in different countries secures each fragment. The three companies include Coincover, Ledger, and Escrowtech, and it’s important to note that no single company has access to the entire backup: each fragment is completely useless by itself. This removes a single point of failure.

- Colde storage (HSM)

 Additionally, each fragment backup provider uses a hardened, tamper-resistant server called a Hardware Security Module (HSM) to securely store these encrypted fragments.

- Fragment validity with PVSS

Ass a supplementary protection, contrary to SSS, PVSS also verifies the validity of the fragments received during reconstruction of the secret . Essentially, PVSS introduces additional variables alongside the creation of the secret which allows it to verify the fragments are consistent with the original secret. And it does so without revealing any intelligible information about the original secret. 

In short, this guarantees that custodians are sending the correct shares back during the secret’s reconstitution.

This is much more secure and verifiable than SSS, hence why Ledger chose this specific method for its secret recovery phrase backup service.

Reference: [Ledger - What is Shamir’s Secret Sharing?](https://www.ledger.com/academy/topics/security/shamirs-secret-sharing), [Ledger Recover](https://www.ledger.com/academy/what-is-ledger-recover)

### Conclusion

Shamir’s Secret Sharing provides a robust, theoretically sound method for protecting sensitive information by dividing it among multiple trusted participants. Its application in cryptocurrency wallets offers a valuable layer of security for both individual and institutional users, helping to secure private keys and seed phrases in a way that minimizes risks associated with insider threats, data loss, and external attacks. Although practical challenges exist, careful implementation and management can make Shamir’s Secret Sharing a powerful tool in safeguarding digital assets in the ever-evolving landscape of cryptocurrency security.