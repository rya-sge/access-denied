---
layout: post
title: "Ethereum Upgrade Pectra - Overview"
date:  2025-05-02
lang: en
locale: en-GB
categories: blockchain ethereum
tags: pectra EIP-2537 EIP-2935 EIP-6110 staking
description: This article presents the list of EIP included in Ethereum Pectra Upgrade (2025)
image: 
isMath: false
---



Here an overview of all EIP included in Ethereum Pectra upgrade with their description

- [EIP-2537](https://eips.ethereum.org/EIPS/eip-2537): Precompile for BLS12-381 curve operations
- [EIP-2935](https://eips.ethereum.org/EIPS/eip-2935): Serve historical block hashes in state
- [EIP-6110](https://eips.ethereum.org/EIPS/eip-6110): Supply validator deposits on chain
- [EIP-7002](https://eips.ethereum.org/EIPS/eip-7002): Execution layer triggerable withdrawals
- [EIP-7251](https://eips.ethereum.org/EIPS/eip-7251): Increase the MAX_EFFECTIVE_BALANCE
- [EIP-7549](https://eips.ethereum.org/EIPS/eip-7549): Move committee index outside Attestation
- [EIP-7623](https://eips.ethereum.org/EIPS/eip-7623): Increase calldata cost
- [EIP-7685](https://eips.ethereum.org/EIPS/eip-7685): General purpose execution layer requests
- [EIP-7691](https://eips.ethereum.org/EIPS/eip-7691): Blob throughput increase
- [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702): Set EOA account code
- [EIP-7840](https://eips.ethereum.org/EIPS/eip-7840): Add blob schedule to EL config files

Reference: [Coinbase - The Ultimate Guide to Ethereum's Pectra Upgrade](https://www.coinbase.com/blog/the-ultimate-guide-to-ethereums-pectra-upgrade)

[TOC]

## EIP-2537: Precompile for BLS12-381 curve operations

Add functionality to efficiently perform operations over the BLS12-381 curve, including those for BLS signature verification.

Along with the curve arithmetic, multi-scalar-multiplication operations are included to efficiently aggregate public keys or individual signer’s signatures during BLS signature verification.

## EIP-2935: Serve historical block hashes from state

Store last `HISTORY_SERVE_WINDOW` historical block hashes in the storage of a system contract as part of the block processing logic. Furthermore this EIP has no impact on `BLOCKHASH` resolution mechanism (and hence its range/costs etc).

## EIP-7549: Move committee index outside Attestation

Move the committee `index` field outside of the signed Attestation message to allow aggregation of equal consensus votes.

This proposal aims to make Casper FFG clients more efficient by reducing the average number of pairings needed to verify consensus rules. While all types of clients can benefit from this EIP, ZK circuits proving Casper FFG consensus are likely to have the most impact.

## EIP-7623: Increase calldata cost

The current calldata pricing permits EL payloads of up to 7.15 MB, while the average size is much smaller at around 100 KB. This EIP proposes adjusting the calldata cost to reduce the maximum possible block size and its variance without negatively impacting regular users. This is achieved by increasing calldata costs for transactions that predominantly post data.

## EIP-7685: General purpose execution layer requests

This proposal defines a general purpose framework for storing contract-triggered requests. It extends the execution header with a single field to store the request information. Requests are later on exposed to the consensus layer, which then processes each one.

## EIP-7691: Blob throughput increase

Increase the number of blobs to reach a new target and max of 6 and 9 blobs per block respectively

Increases the number of blobs in a block to provide more scale to Ethereum via L2 solution that rely on L1 data capacity.

## EIP-7702: Set Code for EOAs

Add a new tx type that permanently sets the code for an EOA

Add a new [EIP-2718](https://eips.ethereum.org/EIPS/eip-2718) transaction type that allows Externally Owned Accounts (EOAs) to set the code in their account. 

This is done by attaching a list of authorization tuples – individually formated as `[chain_id, address, nonce, y_parity, r, s]` – to the transaction. 

For each tuple, a delegation indicator `(0xef0100 || address)` is written to the authorizing account’s code. 

All code executing operations must load and execute the code pointed to by the delegation.

## EIP-7840: Add blob schedule to EL config files

Add a new object to client configuration files `blobSchedule` which lists the target blob count per block and max blob count per block for each fork.

## Staking

### EIP-6110: Supply validator deposits on chain

Appends validator deposits to the Execution Layer block structure. This shifts responsibility of deposit inclusion and validation to the Execution Layer and removes the need for deposit (or `eth1data`) voting from the Consensus Layer.

Validator deposits list supplied in a block is obtained by parsing deposit contract log events emitted by each deposit transaction included in a given block.

### EIP-7002: Execution layer triggerable withdrawals

Allow validators to trigger exits and partial withdrawals via their execution layer (0x01) withdrawal credentials

### EIP-7251: Increase the MAX_EFFECTIVE_BALANCE 

Allow validators to have larger effective balances, while maintaining the 32 ETH lower bound.

Increases the constant `MAX_EFFECTIVE_BALANCE`, while keeping the minimum staking balance `32 ETH`. This permits large node operators to consolidate into fewer validators while also allowing solo-stakers to earn compounding rewards and stake in more flexible increments.

## Reference

- [Coinbase - The Ultimate Guide to Ethereum's Pectra Upgrade](https://www.coinbase.com/blog/the-ultimate-guide-to-ethereums-pectra-upgrade)