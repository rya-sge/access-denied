---
layout: post
title:  Ethereum Staking - How It Works
date:   2024-03-28
lang: en
locale: en-GB
categories: blockchain ethereum
tags: ethereum staking merge
description: Staking in Ethereum is a key functionality. This article explains the main concepts behind it - BLS signature, slashing, Withdrawal address,...
image: /assets/article/blockchain/ethereum/ethereum-logo-portrait-purple-purple.png
isMath: false
---

## Introduction

When Ethereum is passed from Proof of Work (PoW) to Proof of Stake with the [Merge](https://ethereum.org/en/roadmap/merge/) in 2022, this operation has introduced several changes regarding the type of keys involved in securing the Ethereum chain.

With PoW, no identification system is required since you don't care who minted the blocked, only a correct hash was necessary.

But with staking, validators have now identities and you need digital signatures to uniquely identify them.

For this purpose, Ethereum does not use the traditional Elliptic curve signature (secp256k1) as for legacy chain wallet (e.g EOA) but uses another cryptography scheme called **BLS**, which stands for Boneh–Lynn–Shacham. 

- These signatures use a different Elliptic curve called BLS12-381.

- For staking, two keys pair are generated: the  **Signing (Validator) key pair**, to actively sign on-chain (ETH2) operations such as block proposals and attestations and optionally a **Withdrawal key pair** to set the withdrawal address.
- The **advantage** of BLS over the traditional Elliptice curve signature is the ability to aggregate signature. With BLS, you can combine multiple signatures and/or public keys from different users into a single representation. Therefore, it makes possible to verify many signatures in a single operation, instead of verify each signature individually.

Reference: [6. KEYS IN PROOF-OF-STAKE ETHEREUM](https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/keys/), [7. docs.prylabs - bls cryptography](https://docs.prylabs.network/docs/how-prysm-works/bls-cryptography), [8. kb.beaconcha.in - Ethereum 2.0 Keys](https://kb.beaconcha.in/ethereum-staking/ethereum-2-keys)

## Become a validator

To become a validator on the Beacon Chain, you need to deposit 32 ETH per validator that you wish to run. Like all Ethereum transactions, deposits are non-reversible, but the ability to withdrawal your funds via a separate process after depositing remains under your control.

**Summary**

- To become a validator, you need to deposit 32 ETH onto the Beacon Chain
- Withdrawing deposited ETH from the Beacon Chain is accomplished via a separate process.

## Responsibility

### Validator uptime

A validator will get full rewards only if it is online and up to date. This is the validator's responsibility. If the validator goes offline, it will be penalized.

More precisly, the validator will lose an amount of ETH roughly equivalent to the amount of ETH it will have gained in that period if it would have been active

References: [1.Launchpad - More on slashing risks](https://launchpad.ethereum.org/en/faq)

### Bad validator behavior

If the validator try to cheat the system, or act contrary to the specification, it will be liable to incur a penalty known as slashing*.*

- Running the validator keys simultaneously on two or more machines will result in slashing.
- Simply being offline with an otherwise healthy network does not result in slashing, but will result in small inactivity penalties.

References: [2. The Ethereum consensus layer specification](https://github.com/ethereum/consensus-specs), [1.Launchpad - More on slashing risks](https://launchpad.ethereum.org/en/faq), [3. consensys - Understanding Slashing in Ethereum Staking: Its Importance & Consequences](https://consensys.io/blog/understanding-slashing-in-ethereum-staking-its-importance-and-consequences)

## Key management

To become a validator, it is necessary to know about managing keys and protecting a mnemonic. 

### Setup

[Ethereum launchpad](https://launchpad.ethereum.org/) provides the different steps to create a signing key for every validator you want to run. 

- The operator may choose to provide a withdrawal address for his validator when generating the deposit data, which will permanently set the withdrawal address. This is recommended for most users.
- If the operator does not provide a withdrawal address with its initial deposit data, he will need to derive his withdrawal keys from his mnemonic at a later time. In this case, it is very important to **store the mnemonic phrase safely**—it will be the ONLY way to withdraw the ETHs when the operator choses to activate withdrawals.

Summary:

- keys are the validator's responsibility and that my mnemonic (seed) will be the **ONLY WAY** to withdraw the funds if a withdrawal address is not provided with initial deposit data.

### Withdrawal address

As already indicated in the previous paragraph, the recommended way is to provide a withdrawal address with the initial deposit to automatically enable reward payments and also the ability to fully exit the funds at anytime.

- The Withdrawal address should be to a regular Ethereum address and will be the only address funds can be sent to from the new validator accounts, and cannot be changed once chosen.

- If this is not provided now, the deposited funds will remain locked on the Beacon Chain until an address is provided. Unlocking will require signing a message with the BLS withdrawal keys, generated from the mnemonic seed phrase (so keep it safe).

Before the Merge, it was not possible to set a withdrawal address. It is the reason why BLS withdrawal keys were used to allow the validators to set later the withdrawal address. 

Reference: [4. eth2book.info/capella#bls-withdrawal-credentials](https://eth2book.info/capella/part2/deposits-withdrawals/withdrawal-processing/#bls-withdrawal-credentials), [6. ethereum.org#withdrawal-key](https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/keys/#withdrawal-key)

### Signing keys

#### Generate private key

Digital signatures in the blockchain world are usually based on elliptic curve groups. 

- For signing users' transactions, Ethereum uses [ECDSA](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm) signatures with the [secp256k1](https://en.bitcoin.it/wiki/Secp256k1) elliptic curve. 
- However, the beacon chain protocol uses [BLS](https://en.wikipedia.org/wiki/BLS_digital_signature) signatures with the [BLS12-381](https://hackmd.io/@benjaminion/bls12-381) elliptic curve

- Proof of stake protocols use digital signatures to identify their participants and hold them accountable.
- BLS signatures can be aggregated together, making them efficient to verify at large scale.
- Signature aggregation allows the beacon chain to scale to hundreds of thousands of validators.
- Ethereum transaction signatures on the execution (Eth1) layer remain as-is.

A CLI tool is available on the [Ethereum github](https://github.com/ethereum/staking-deposit-cli).

BLS signatures, specifically those over the  BLS12–381 curve are used in Beacon chain block signatures and  attestations. This makes it possible to aggregate multiple signatures  and verify them in a single operation, which is an outstanding  improvement in scalability.

Reference: [4. eth2book.info - signatures](https://eth2book.info/capella/part2/building_blocks/signatures/), [5. A deep-dive into Eth-staking-smith](https://chorus.one/articles/a-deep-dive-into-eth-staking-smith)

#### Verification

The verification mechanism works because every public part of a Signing  key (Public Signing Key) is published on-chain, so every signature done with the private part of the Signing key (Private Signing Key) can be  verified by every other validator.

#### Move funds with Signing keys

Despite having the power for creating blockchain content, the Signing keys can not be used to move any funds  including staking funds, and they only listen for and sign the  transaction content provided by the peering network of Ethereum nodes.

## Client

To process incoming validator deposits from the execution layer (formerly 'Eth1' chain), the operator need to run an execution client as well as a consensus client (formerly 'Eth2').

#### Execution client

- [Nethermind](https://www.nethermind.io)
- [Geth](https://geth.ethereum.org)
- [Besu](https://besu.hyperledger.org) (Hyperledger)
- [Erigon](https://github.com/ledgerwatch/erigon)

#### Consensus client

- [Prsysm](https://docs.prylabs.network/docs/getting-started)
- [Nimbus](https://nimbus.team/index.html)
- [Lighthouse](https://lighthouse-book.sigmaprime.io)
- [Teku](https://github.com/Consensys/teku) (Consensys)
- [Lodestar](https://lodestar.chainsafe.io) (ChainSafe)

## staking deposit contract

The Ethereum staking deposit contract is available at the following [address](https://etherscan.io/address/0x00000000219ab540356cBB839Cbe05303d7705Fa). This contract receives the stacked funds.

Its address is published on the ethereum Foundation [website](https://ethereum.org/en/staking/deposit-contract/). As indicated in the website "Sending ETH to the address on this page will not make you a staker and will result in a failed transaction."

## References

- [1. launchpad.ethereum.org](https://launchpad.ethereum.org)
  - [launchpad.ethereum.org - FAQ](https://launchpad.ethereum.org/en/faq)
  - [launchpad.ethereum.org - Validator checklist](https://launchpad.ethereum.org/en/checklist)
- [2. The Ethereum consensus layer specification](https://github.com/ethereum/consensus-specs)
- [3. Consensys.io - Understanding Slashing in Ethereum Staking: Its Importance & Consequences](https://consensys.io/blog/understanding-slashing-in-ethereum-staking-its-importance-and-consequences)
- [4. eth2book.info/capella/](https://eth2book.info/capella/part2/)
  - [eth2book.info - bls-withdrawal-credentials](https://eth2book.info/capella/part2/deposits-withdrawals/withdrawal-processing/#bls-withdrawal-credentials)
  - [eth2book.info - signatures](https://eth2book.info/capella/part2/building_blocks/signatures/)
- [5. A deep-dive into Eth-staking-smith](https://chorus.one/articles/a-deep-dive-into-eth-staking-smith)
- [6. KEYS IN PROOF-OF-STAKE ETHEREUM](https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/keys/)
  - [ethereum.org - withdrawal-key](https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/keys/#withdrawal-key)
- [7. docs.prylabs - bls cryptography](https://docs.prylabs.network/docs/how-prysm-works/bls-cryptography)
- [8. kb.beaconcha.in - Ethereum 2.0 Keys](https://kb.beaconcha.in/ethereum-staking/ethereum-2-keys)
