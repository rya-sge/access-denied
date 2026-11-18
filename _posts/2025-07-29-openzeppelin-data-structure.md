---
layout: post
title: OpenZeppelin v5 Data - Overview
date: 2025-07-29
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: solidity blockchain ethereum
tags: solidity ethereum openzeppelin data
description: "Data structures in OpenZeppelin Contracts v5: BitMaps, EnumerableMap, EnumerableSet, DoubleEndedQueue, CircularBuffer, Checkpoints, Heap and MerkleTree."
image: /assets/article/blockchain/solidity/2025-07-29-openzeppelin-data-structure-mindmap.png
isMath: 
---

OpenZeppelin Contracts v5 is a robust and widely used smart contract library for Solidity developers. Among its many features, it includes a suite of **custom data structures** that simplify common patterns in decentralized applications. This article explores the following data structures:

- `BitMaps`
- `EnumerableMap`
- `EnumerableSet`
- `DoubleEndedQueue`
- `CircularBuffer`
- `Checkpoints`
- `Heap`
- `MerkleTree`

Each data structure is tailored to specific use cases in blockchain applications, balancing efficiency, gas cost, and usability.

See [OpenZeppelin V5 - data structure](https://docs.openzeppelin.com/contracts/5.x/api/utils#data_structures)

> This article comes primarily from OpenZeppelin and ChatGPT. I hope to make it more personal in the future.

[TOC]

## What you need to know first

The data structures below are built on a few Solidity and EVM mechanisms that the article uses without developing them:

- **Storage slots.** A contract's persistent state is stored in 32-byte slots. Writing a slot from zero to a non-zero value is the most expensive storage write, which is why `BitMaps` packs 256 booleans into one slot.
- **Warm and cold access.** Since [EIP-2929](https://eips.ethereum.org/EIPS/eip-2929), the first access to a storage slot in a transaction is "cold" and costs more gas than later "warm" accesses to the same slot. `BitMaps` benefits from it when sequential indices share a slot.
- **Solidity mappings are not enumerable.** A `mapping` has no length and no list of its keys, so a contract cannot iterate over it. `EnumerableSet` and `EnumerableMap` add that ability on top of a mapping.
- **Libraries and `using for`.** A Solidity library is reusable code attached to a type with `using Library for Type;`, so that `whitelist.add(user)` calls the library function with `whitelist` as its first argument. Every structure in this article is used this way.
- **Merkle trees and proofs.** A Merkle tree hashes leaves pairwise up to a single root, and a Merkle proof is the list of sibling hashes that shows a leaf belongs to the tree. See [Cyfrin First Fight 42 - Snowman Merkle Airdrop]({{site.url_complet}}/2025/07/11/cyfrin-first-fight-42-snowman-merkle-aidrop/) for an airdrop that relies on them.
- **Vote snapshots in governance.** Token governance reads each voter's balance at a past point in time rather than the current one, so tokens moved after a proposal starts cannot be counted twice. `Checkpoints` stores the history that makes such lookups possible.

## BitMaps

```solidity
import "@openzeppelin/contracts/utils/structs/BitMaps.sol";
```

Library for managing uint256 to bool mapping in a compact and efficient way, provided the keys are sequential. Largely inspired by Uniswap’s [merkle-distributor](https://github.com/Uniswap/merkle-distributor/blob/master/contracts/MerkleDistributor.sol).

BitMaps pack 256 booleans across each bit of a single 256-bit slot of `uint256` type. Hence booleans corresponding to 256 *sequential* indices would only consume a single slot, unlike the regular `bool` which would consume an entire slot for a single value.

This results in gas savings in two ways:

- Setting a zero value to non-zero only once every 256 times
- Accessing the same warm slot for every 256 *sequential* indices

## EnumerableMap

```solidity
import "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
```

Library for managing an enumerable variant of Solidity’s [`mapping`](https://solidity.readthedocs.io/en/latest/types.html#mapping-types) type.

Maps have the following properties:

- Entries are added, removed, and checked for existence in constant time (O(1)).
- Entries are enumerated in O(n). No guarantees are made on the ordering.
- Map can be cleared in O(n), which removes all entries.

```solidity
contract Example {
    // Add the library methods
    using EnumerableMap for EnumerableMap.UintToAddressMap;

    // Declare a set state variable
    EnumerableMap.UintToAddressMap private myMap;
}
```

------

## EnumerableSet

### Description:

`EnumerableSet` is a set data structure for primitive types like `address`, `uint256`, and `bytes32`. It offers **constant-time (O(1)) operations** for adding, removing, and checking existence, and allows enumeration.

### Example:

```solidity
using EnumerableSet for EnumerableSet.AddressSet;

EnumerableSet.AddressSet private whitelist;

function addToWhitelist(address user) external {
    whitelist.add(user);
}

function isWhitelisted(address user) external view returns (bool) {
    return whitelist.contains(user);
}

function getWhitelisted(uint256 index) external view returns (address) {
    return whitelist.at(index);
}
```

------

## DoubleEndedQueue

### Description:

A **double-ended queue (deque)** allows inserting and removing elements from both ends. It's ideal for implementing **task queues, buffers**, or **event logs**.

### Example:

```solidity
using DoubleEndedQueue for DoubleEndedQueue.AddressDeque;

DoubleEndedQueue.AddressDeque private queue;

function enqueue(address user) external {
    queue.pushBack(user);
}

function dequeue() external returns (address) {
    return queue.popFront();
}
```

------

## CircularBuffer

### Description:

`CircularBuffer` is a **fixed-size buffer** that overwrites older elements when full, ideal for **bounded history** or **limited event storage** scenarios.

It is available since v5.1 with a single `Bytes32CircularBuffer` type, so other types are cast to and from `bytes32`.

### Example:

```solidity
using CircularBuffer for CircularBuffer.Bytes32CircularBuffer;

CircularBuffer.Bytes32CircularBuffer private buffer;

constructor() {
    buffer.setup(5); // buffer of size 5
}

function addNumber(uint32 n) external {
    buffer.push(bytes32(uint256(n))); // Overwrites oldest if full
}

function getLatest() external view returns (uint32) {
    return uint32(uint256(buffer.last(0))); // last(0) is the most recent value
}
```

------

## Checkpoints

### Description:

```solidity
import "@openzeppelin/contracts/utils/structs/Checkpoints.sol";
```

`Checkpoints` is used to **track values over time**, such as token balances at specific block numbers. It’s useful for **governance voting** or **historical queries**.

This library defines the `Trace*` struct, for checkpointing values as they change at different points in time, and later looking up past values by block number. See [`Votes`](https://docs.openzeppelin.com/contracts/5.x/api/governance#Votes) as an example.

To create a history of checkpoints define a variable type `Checkpoints.Trace*` in your contract, and store a new checkpoint for the current transaction block using the [`push`](https://docs.openzeppelin.com/contracts/5.x/api/utils#Checkpoints-push-struct-Checkpoints-Trace160-uint96-uint160-) function.

------

## Heap

### Description:

`Heap` is a **priority queue** that always gives access to the highest (or lowest) value. It can be configured as a **min-heap** or **max-heap**, and is useful in **auctions, job queues, or game leaderboards**.

Heaps are represented as a tree of values where the first element (index 0) is the root, and where the node at index i is the child of the node at index (i-1)/2 and the parent of nodes at index 2*i+1 and 2*i+2. Each node stores an element of the heap.

The structure is ordered so that each node is bigger than its parent. An immediate consequence is that the highest priority value is the one at the root. This value can be looked up in constant time (O(1)) at `heap.tree[0]`

The structure is designed to perform the following operations with the corresponding complexities:

- peek, which gets the highest priority value: O(1)
- insert, which inserts a value: O(log(n))
- pop, which removes the highest priority value: O(log(n))
- replace, which replaces the highest priority value with a new value: O(log(n))
- length, which gets the number of elements: O(1)
- clear, which removes all elements: O(1)

------

## MerkleTree

### Description:

`MerkleTree` helps you build a Merkle tree on-chain by inserting leaves and updating its root; the proofs against that root are verified with the separate `MerkleProof` library. It’s useful in **airdrop verification**, **allowlists**, or **zero-knowledge applications**.

Each tree is a complete binary tree with the ability to sequentially insert leaves, changing them from a zero to a non-zero value and updating its root. 

This structure allows inserting commitments (or other entries) that are not stored, but can be proven to be part of the tree at a later time if the root is kept. See [`MerkleProof`](https://docs.openzeppelin.com/contracts/5.x/api/utils/cryptography#MerkleProof).

A tree is defined by the following parameters:

- `Depth`: The number of levels in the tree, it also defines the maximum number of leaves as 2**depth.
- `Zero value`: The value that represents an empty leaf. Used to avoid regular zero values to be part of the tree.
- `Hashing function`: A cryptographic hash function used to produce internal nodes. Defaults to [`Hashes.commutativeKeccak256`](https://docs.openzeppelin.com/contracts/5.x/api/utils/cryptography#Hashes-commutativeKeccak256-bytes32-bytes32-).

------

## Conclusion

OpenZeppelin’s data structures offer powerful building blocks for secure, efficient, and readable smart contracts. Understanding when and how to use them can greatly improve your smart contract design and reliability.

OpenZeppelin Contracts v5 provides a data structure for each of these uses: `EnumerableSet` for whitelists, `Checkpoints` for tracking history, `CircularBuffer` and `Deque` for handling events, and `MerkleTree` for airdrops.

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **OpenZeppelin Contracts v5** | A widely used Solidity smart contract library whose `utils/structs` folder provides the data structures covered here. |
| **Library (`using for`)** | Solidity code attached to a type, so that a structure's functions are called as methods, as in `whitelist.add(user)`. |
| **Storage slot** | A 32-byte unit of a contract's persistent storage; a regular `bool` occupies a whole slot for one value. |
| **Warm slot** | A storage slot already accessed in the current transaction, which is cheaper to access again. |
| **BitMaps** | A library that maps `uint256` keys to booleans by packing 256 sequential values into the bits of a single slot. |
| **EnumerableMap** | An enumerable variant of Solidity's `mapping`, with O(1) add, remove and lookup, and O(n) enumeration in no guaranteed order. |
| **EnumerableSet** | A set of `address`, `uint256` or `bytes32` values with O(1) add, remove and membership checks, which can also be enumerated. |
| **DoubleEndedQueue (deque)** | A queue that allows inserting and removing elements at both ends, for task queues, buffers or event logs. |
| **CircularBuffer** | A fixed-size buffer that overwrites its oldest element when full, suited to bounded history. |
| **Checkpoints** | A library that records how a value changes over time and looks up past values, used by governance `Votes`. |
| **Trace** | The `Checkpoints.Trace*` struct that stores the history of checkpoints for one value. |
| **Heap** | A priority queue stored as a tree in an array, where the root at index 0 holds the highest-priority value, with O(1) peek and O(log n) insert and pop. |
| **Merkle tree** | A complete binary tree of hashes whose root commits to all its leaves; OpenZeppelin's `MerkleTree` inserts leaves sequentially and updates the root. |
| **Merkle proof** | The data that shows a leaf belongs to a tree whose root is known, verified with OpenZeppelin's `MerkleProof`. |
| **Zero value** | The value that represents an empty leaf in a `MerkleTree`, so that regular zero values are kept out of the tree. |

## Reference

- ChatGPT with the input "Write me an article about these different data strucutre available with openzeppelin v5. EnumerableSet DoubleEndedQueue CircularBuffer Checkpoints Heap MerkleTree If possible provide small example"
- [OpenZeppelin V5 - data structure](https://docs.openzeppelin.com/contracts/5.x/api/utils#data_structures)

## Mindmap

The mindmap below summarizes the article.

![OpenZeppelin v5 data structures mindmap]({{site.url_complet}}/assets/article/blockchain/solidity/2025-07-29-openzeppelin-data-structure-mindmap.png)
