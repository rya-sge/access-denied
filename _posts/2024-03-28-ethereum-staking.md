---
layout: post
title:  Ethereum Staking - How It Works
date:   2024-03-28
lang: en
locale: en-GB
categories: blockchain ethereum cryptography
tags: ethereum staking merge
description: Staking in Ethereum is a key functionality. This article explains the main concepts behind it - BLS signature, slashing, Withdrawal address,...
image: /assets/article/blockchain/ethereum/ethereum-logo-portrait-purple-purple.png
isMath: false
---

## Introduction

When Ethereum is passed from Proof of Work (PoW) to Proof of Stake with the [Merge](https://ethereum.org/en/roadmap/merge/) in 2022, this operation has introduced several changes regarding the type of keys involved in securing the Ethereum chain.

With PoW, no identification system is required since you don't care who minted the blocked, only a correct hash was necessary.

But with staking, validators have now identities, and you need digital signatures to uniquely identify them.

For this purpose, Ethereum does not use the traditional Elliptic curve signature (secp256k1) as for legacy chain wallet (e.g. EOA) but uses another cryptography scheme called **BLS**, which stands for Boneh–Lynn–Shacham. 

- These signatures use a different Elliptic curve called BLS12-381.

- For staking, two keys pair are generated: the  **Signing (Validator) key pair**, to actively sign on-chain (ETH2) operations such as block proposals and attestations and optionally a **Withdrawal key pair** to set the withdrawal address.
- The **advantage** of BLS over the traditional Elliptice curve signature is the ability to aggregate signature. With BLS, you can combine multiple signatures and/or public keys from different users into a single representation. Therefore, it makes it possible to verify many signatures in a single operation, instead of verifying each signature individually.

Reference: [6. KEYS IN PROOF-OF-STAKE ETHEREUM](https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/keys/), [7. docs.prylabs - bls cryptography](https://docs.prylabs.network/docs/how-prysm-works/bls-cryptography), [8. kb.beaconcha.in - Ethereum 2.0 Keys](https://kb.beaconcha.in/ethereum-staking/ethereum-2-keys)

[TOC]

## Become a validator

To become a validator on the Beacon Chain, you need to deposit 32 ETH per validator that you wish to run. Like all Ethereum transactions, deposits are non-reversible, but the ability to withdrawal your funds via a separate process after depositing remains under your control.

**Summary**

- To become a validator, you need to deposit 32 ETH onto the Beacon Chain
- Withdrawing deposited ETH from the Beacon Chain is accomplished via a separate process.

## Responsibility

### Validator uptime

A validator will get full rewards only if it is online and up to date. This is the validator's responsibility. If the validator goes offline, it will be penalized.

More precisely, the validator will lose an amount of ETH roughly equivalent to the amount of ETH it will have gained in that period if it would have been active

References: [1.Launchpad - More on slashing risks](https://launchpad.ethereum.org/en/faq)

### Bad validator behavior

If the validator tries to cheat the system, or acts contrary to the specification, it will be liable to incur a penalty known as slashing*.*

- Running the validator keys simultaneously on two or more machines will result in slashing.
- Simply being offline with an otherwise healthy network does not result in slashing, but will result in small inactivity penalties.

References: [2. The Ethereum consensus layer specification](https://github.com/ethereum/consensus-specs), [1.Launchpad - More on slashing risks](https://launchpad.ethereum.org/en/faq), [3. consensys - Understanding Slashing in Ethereum Staking: Its Importance & Consequences](https://consensys.io/blog/understanding-slashing-in-ethereum-staking-its-importance-and-consequences)

## Key management

To become a validator, it is necessary to know about managing keys and protecting a mnemonic. 

### Setup

[Ethereum launchpad](https://launchpad.ethereum.org/) provides the different steps to create a signing key for every validator you want to run. 

- The operator may choose to provide a withdrawal address for his validator when generating the deposit data, which will permanently set the withdrawal address. This is recommended for most users.
- If the operator does not provide a withdrawal address with its initial deposit data, he will need to derive his withdrawal keys from his mnemonic later. In this case, it is very important to **store the mnemonic phrase safely**—it will be the ONLY way to withdraw the ETHs when the operator choses to activate withdrawals.

Summary:

- keys are the validator's responsibility and that my mnemonic (seed) will be the **ONLY WAY** to withdraw the funds if a withdrawal address is not provided with initial deposit data.

### Withdrawal address

As already indicated in the previous paragraph, the recommended way is to provide a withdrawal address with the initial deposit to automatically enable reward payments and also the ability to fully exit the funds at any time.

- The Withdrawal address should be to a regular Ethereum address and will be the only address funds can be sent to from the new validator accounts and cannot be changed once chosen.

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

To process incoming validator deposits from the execution layer (formerly 'Eth1' chain), the operator needs to run an execution client as well as a consensus client (formerly 'Eth2').

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

## Staking deposit contract

The Ethereum staking deposit contract is available at the following address:  [`0x00000000219ab540356cbb839cbe05303d7705fa`](https://etherscan.io/address/0x00000000219ab540356cbb839cbe05303d7705fa). 

This contract receives the staked funds.

- The deposit contract is the protocol's entry point for staking.
- Anybody may permissionlessly stake 32 ETH via the contract.
- On receiving a valid deposit the contract emits a receipt.
- An incremental Merkle tree maintains a Merkle root of all deposits.
- The deposit contract cannot verify a deposit's BLS signature.
- The balance of the deposit contract never decreases.
- Ether sent to the deposit contract should be considered burned.

Its address is published on the ethereum Foundation [website](https://ethereum.org/en/staking/deposit-contract/). As indicated on the website "Sending ETH to the address on this page will not make you a staker and will result in a failed transaction."

### Functions





Reference: [eth2book - The Deposit Contract](https://eth2book.info/capella/part2/deposits-withdrawals/contract/)

## Related EIP

See also [Ethereum - History](https://ethereum.org/en/history/)

### EIP-3675: Upgrade consensus to Proof-of-Stake (Paris/2022)

[EIP specification](https://eips.ethereum.org/EIPS/eip-3675), [Paris Upgrade specification](https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/paris.md)

This EIP deprecates Proof-of-Work (PoW) and supersedes it with the new Proof-of-Stake consensus mechanism (PoS) driven by the beacon chain. Information on the bootstrapping of the new consensus mechanism is documented in [EIP-2982](https://eips.ethereum.org/EIPS/eip-2982). Full specification of the beacon chain can be found in the `ethereum/consensus-specs` repository.

This document specifies the set of changes to the block structure, block processing, fork choice rule and network interface introduced by the consensus upgrade.

### EIP-4895: Beacon chain push withdrawals as operations (Shanghai/2023)

[EIP specification](https://eips.ethereum.org/EIPS/eip-4895), [Shanghai Network Upgrade Specification](https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/shanghai.md)

Introduce a system-level “operation” to support validator withdrawals that are “pushed” from the beacon chain to the EVM.

These operations create unconditional balance increases to the specified recipients.

This EIP provides a way for validator withdrawals made on the beacon chain to enter into the EVM. The architecture is “push”-based, rather than “pull”-based, where withdrawals are required to be processed in the execution layer as soon as they are dequeued from the consensus layer.

Withdrawals are represented as a new type of object,  called a `withdrawal` , in the execution payload – an “operation” – that separates the withdrawals feature from user-level transactions. 

`Withdrawal`s provide key information from the consensus layer:

1. a monotonically increasing `index`, starting from 0, as a `uint64` value that increments by 1 per withdrawal to uniquely identify each withdrawal
2. the `validator_index` of the validator, as a `uint64` value, on the consensus layer the withdrawal corresponds to
3. a recipient for the withdrawn ether `address` as a 20-byte value
4. a nonzero `amount` of ether given in Gwei (1e9 wei) as a `uint64` value.

*NOTE*: the `index` for each withdrawal is a global counter spanning the entire sequence of withdrawals.

### EIP-4788: Beacon block root in the EVM

Commit to the hash tree root of each beacon chain block in the corresponding execution payload header.

Store each of these roots in a smart contract.

See also [Consensys - Ethereum Evolved: Dencun Upgrade Part 3, EIP-4788](https://consensys.io/blog/ethereum-evolved-dencun-upgrade-part-3-eip-4788)

### EIP-6110: Supply validator deposits on chain (Last call)

[EIP reference](https://eips.ethereum.org/EIPS/eip-6110)

Appends validator deposits to the Execution Layer block structure. This shifts responsibility of deposit inclusion and validation to the Execution Layer and removes the need for deposit (or `eth1data`) voting from the Consensus Layer.

Validator deposits list supplied in a block is obtained by parsing deposit contract log events emitted by each deposit transaction included in a given block.

### EIP-7002: Execution layer triggerable withdrawals (Last call)

[EIP reference](https://eips.ethereum.org/EIPS/eip-7002)

Adds a new mechanism to allow validators to trigger withdrawals and exits from their execution layer (0x01) withdrawal credentials.

These new execution layer exit messages are appended to the execution layer block and then processed by the consensus layer.

Validators have two keys – an active key and a withdrawal credential. 

- The active key takes the form of a BLS key, whereas the withdrawal credential can either be a BLS key (0x00) or an execution layer address (0x01). 
- The active key is “hot”, actively signing and performing validator duties, whereas the withdrawal credential can remain “cold”, only performing limited operations in relation to withdrawing and ownership of the staked ETH. 
- Due to this security relationship, the withdrawal credential ultimately is the key that owns the staked ETH and any rewards.

As currently specified, only the active key can initiate a validator exit. This means that in any non-standard custody relationships (i.e. active key is separate entity from withdrawal credentials), that the ultimate owner of the funds – the possessor of the withdrawal credentials – cannot independently choose to exit and begin the withdrawal process. 

This leads to:

-  either trust issues (e.g. ETH can be “held hostage” by the active key owner) 
- insufficient work-arounds such as pre-signed exits. 
- Additionally, in the event that active keys are lost, a user should still be able to recover their funds by using their cold withdrawal credentials.

To ensure that the withdrawal credentials (owned by both EOAs and smart contracts) can trustlessly control the destiny of the staked ETH, this specification enables exits triggerable by 0x01 withdrawal credentials.

Note, 0x00 withdrawal credentials can be changed into 0x01 withdrawal credentials with a one-time signed message. Thus any functionality enabled for 0x01 credentials is defacto enabled for 0x00 credentials.

## 

### EIP-7251: Increase the MAX_EFFECTIVE_BALANCE (Last call)

[EIP reference](https://eips.ethereum.org/EIPS/eip-7251)

This EIP increases the constant `MAX_EFFECTIVE_BALANCE`, while keeping the minimum staking balance `32 ETH`. This permits large node operators to consolidate into fewer validators while also allowing solo-stakers to earn compounding rewards and stake in more flexible increments.

MAX_EFFECTIVE_BALANCE is changed from 32 ETH t0 2,048 ETH

This offers new opportunities for staking operations:

- More efficient validator management for large ETH holders
- Potential cost reduction in operational overhead
- Greater flexibility in stake deployment strategies
- Compounding for balances greater than 32 ETH

Reference: [Figment - What The Pectra And Fusaka Ethereum Upgrades Mean For Institutional Staking](https://figment.io/insights/what-the-pectra-and-fusaka-ethereum-upgrades-mean-for-institutional-staking/)

## 



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
