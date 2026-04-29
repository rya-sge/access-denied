---
layout: post
title:  Crypto wallet - What could go wrong ?
date:   2024-09-19
lang: en
locale: en-GB
categories: blockchain cryptography
tags: blockchain wallet
description: This article is an introduction to Multi-Party Computation (MPC)
image:  /assets/article/blockchain/solana/solanaLogoMark.png
isMath: false
---

Crypto wallets are a key piece of blockchain and crypto infrastructures. These software are generally responsible to:

- Generate seed phrase and associated private keys
- Store the private keys securely
- Provide a way to sign transactions, interact with applications (dApps), move the funds, ...

Several hacks and vulnerabilities are related to crypto wallets. This paper provides an eye about the main hacks and vulnerabilities, having affected known crypto wallets.

This paper does not consider vulnerabilities which target the user, e.g. to sign a malicious transaction. 

[TOC]

## Physical Supply Chain Attack

This type of attack targets physical crypto wallet such as Hardware wallet

### Fake device sold on marketplace

#### Fake Trezor Wallet (2022)

##### Trezor security

Trezor implements several protection to protect against fake device:

- Seal on the device or the package.
- A legitimate device will always arrive without firmware installed
- The bootloader verifies that the firmware you install has been signed by SatoshiLabs (= secure boot).
- “New”: individual chips are now glued onto the board

##### Attack details

Fake Trezor sold on the Russia Market through a popular website.

Modification performed by the attackers:

1. They install a malicious firmware in the device
2. They removed the bootloader-checks to avoid detection at startup.
3. They replace the randomly generated seed phrase with a pre-generated seed phrases saved in the malicious firmware. 

Reference: [Kaspersky.com - Case study: fake hardware cryptowallet](https://www.kaspersky.com/blog/fake-trezor-hardware-crypto-wallet/48155/)

## Online Supply Chain Attack

### Ledger Connect kit (2023)

[Ledger](https://www.ledger.com) is a family of hardware wallet

To connect the wallet to Dapps front-end, the company provides a software called Connect kit

On December 14th, 2023, an attacker managed to compromise the NPMJS accounts of a former Ledger employee through phishing and use this access to deploy a malicious package instead of the official one. 

As a result, when a user signs a transaction on an affected dapp, the funds were rerouted to the attacker's wallet.

When this attack doesn't not affect directly the security of the hardware wallet, it demonstrates the importance to keep external library safe.

### Detection and accident response

Quickly detected by different tools and users.Ledger quickly replaced the malicious version on NPM (40 minutes).With the caching mechanism in CDNs, the malicious package remained active longer.

Reference: [ledger.com - A letter from Ledger Chairman & CEO Pascal Gauthier Regarding Ledger Connect Kit Exploit](https://www.ledger.com/blog/a-letter-from-ledger-chairman-ceo-pascal-gauthier-regarding-ledger-connect-kit-exploit), https://hacken.io/insights/ledger-hack-explained/ https://www.ledger.com/blog/security-incident-report

![img](https://cdn.prod.website-files.com/64ef149a1d50ae58a7c04212/657dfed1d65f297b75f26cb7_Screenshot%202023-12-16%20at%2021.47.19.png)

### IOTA Trinity wallet Hack (2020)

**Date:** 2020

**Impact:** Theft of 8.55 Ti in IOTA tokens.

- Trinity was a software wallet (Desktop and mobile phone) managed by the IOTA foundation

- Moonpay is a third-party service that allows users to purchase IOTA tokens from within the Trinity wallet.
- On 2020 the Trinity Wallet was attacked via a third-party dependency from Moonpay

An attacker compromised with one of several illicit versions of Moonpay’s software development kit (SDK), which was being loaded automatically from Moonpay’s servers (their content delivery network) when a user opened Trinity. 

a. The code was loaded into the local Trinity instance

b. After the user’s wallet was unlocked, decrypted the user’s seed

c.  Sent the seed and passphrase to a server controlled by the attacker. 

Before transferring tokens out, the attacker awaited the release of a new Trinity version, which would overwrite Trinity’s cache files and thus remove the remaining traces of the hacker

Reference:

- IOTA blog
  - [blog.iota - Trinity Attack Incident Part 1: Summary and next steps](https://blog.iota.org/trinity-attack-incident-part-1-summary-and-next-steps-8c7ccc4d81e8/)

  - [Medium - ](https://medium.com/@iotafoundation/trinity-attack-incident-part-3-key-learnings-takeaways-c933de22fd0a)

- [fullycrypto.com - IOTA Releases Comprehensive Trinity Wallet Hack Reports](https://fullycrypto.com/iota-releases-comprehensive-trinity-wallet-hack-reports)

- 

