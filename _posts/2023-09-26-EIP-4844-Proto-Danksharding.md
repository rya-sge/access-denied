---
layout: post
title:  "Summary of EIP-4844 Proto-Danksharding"
date:   2023-09-26
last-update: 
categories: blockchain
lang: en
locale: en-GB
tags: blockchain crypto ethereum EIP-4844
image: /assets/article/blockchain/ethereum/ethereum-logo-portrait-purple-purple.png
description: This article is a summary of the main concepts behind the EIP-4844:Proto-Danksharding where the main goal is to scale Ethereum using Blob.
---

This article is a summary of the main concepts behind the [5. EIP-4844:Proto-Danksharding,](https://eips.ethereum.org/EIPS/eip-4844)

The main reference of this article is a lesson from LearnWeb3: [1.Proto-Danksharding: Scaling Ethereum using Blobs](https://learnweb3.io/lessons/proto-danksharding-scaling-ethereum-using-blobs/)

## Common Concept

### Rollup

A rollup is a blockchain that runs on top of Ethereum, reason why they are called *Layer 2 Blockchains.* The goal is that users conduct the majority of their transactions on the rollup chains instead of the Layer 1 Mainnet. 

There are two main types of rullup: Optimistic Rollups & ZK Rollup

#### Limitation

Right now, rollups post their transactions in `CALLDATA`.

This is expensive because it is processed by all Ethereum nodes and lives on chain forever, even though rollups only need the data for a short time

Reference: [6. ethereum.org/en/roadmap/danksharding/](https://ethereum.org/en/roadmap/danksharding/).

#### Sequencers

A group of nodes called *sequencers* are in charge of batching (or *rolling up*) many Layer 2 transactions into a single Layer 1 transaction [https://domothy.com/blobspace/].

### Sharding

#### Sharding

The Ethereum blockchain is divided into mini shards - distinct pieces of the blockchain - which can all run in parallel.

#### Validator assignation

The Beacon Chain can then randomly assign validators on the network to different shards and periodically shuffle them up. 

#### Attack of 51%

An attacker wishes to perform an 51% attack on a specific shard would still have to  control 51% of the entire validator set, otherwise their chances of  having their validators randomly assigned to the same shard are near  zero. [[2. domothy.com/blobspace/](https://domothy.com/blobspace/)]

## Danksharding

###  Introduction

#### Goal

Focus on helping rollups scale

#### Principle

The concept of sharding is replaced by *blobs*. These blobs are constructed in a clever way so that although blocks are filled with big blobs, each individual node only needs to do a very small amount of work to check that all the data is  available (DA) [[2. domothy.com/blobspace/](https://domothy.com/blobspace/)].

##### Data Availability (DA)

 A way to ensure that all data needed for the network to continue in a valid manner is available without needing to download and verify all of it by hand

#### Trade-off

The construction of a block becomes a very heavy process in terms of bandwidth  and computation, which is a centralizing force on block builders.

This kind of tasks can be however done by centralized block builders using  high performance machine, already done due to MEV [[2. domothy.com/blobspace/](https://domothy.com/blobspace/)].

## Proto-Danksharding (EIP-4844)

This part is described in the EIP [4844](https://eips.ethereum.org/EIPS/eip-4844).

Proto-Danksharding introduces data blobs that can be sent and attached to blocks. The data in these blobs is not accessible to the EVM and is automatically deleted after a fixed time period (1-3 months), making the whole process cheaper for rollup 

Reference: [6. ethereum.org/en/roadmap/danksharding/](https://ethereum.org/en/roadmap/danksharding/).

### Blob-carrying transactions

In addition to the traditional parameter`sender`, `receiver`, `nonce`, `gas` , this new type of transaction contains two new things:

1. `max_fee_per_blob_gas`: a bid by the sequencer on how much they're willing to pay for the blob
2. `blob_version_hashes`: a list of hashes of blobs - since each transaction can actually include multiple blobs

The transaction doesn't actually contain the blob data itself. It only contains a list of hashes of the blobs. 

#### Blob construction

The actual blob data itself, under the hood, is constructed using some special mathematical schemes which allow for some fancy optimizations on the network allowing us to heavily speed up computations

#### Blob data max size

The blob can contain upto roughly ~125 KB (kilobytes) of data - which is roughly 128,000 bytes

### Blob pricing market

The blob transactions have their own gas pricing mechanic, named **blob gas**. It is similar to the pricing mechanic for [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) transactions that exist on Ethereum today. 

- Target of 3 blobs per block on the network, with a hard upper limit of 6 blobs per block. 
- Running alongside the existing gas mechanic (EIP-1559)

The separation of the pricing mechanics between EIP-1559 transactions and blob transactions (blob gas is priced independently) prevents one from affecting the other in case of peak.

## References

1. https://learnweb3.io/lessons/proto-danksharding-scaling-ethereum-using-blobs/
2. [https://domothy.com/blobspace/](https://domothy.com/blobspace/)
3. https://notes.ethereum.org/@dankrad/new_sharding
4. https://twitter.com/protolambda/status/1495538286332624898
5. https://eips.ethereum.org/EIPS/eip-4844
6. https://ethereum.org/en/roadmap/danksharding/