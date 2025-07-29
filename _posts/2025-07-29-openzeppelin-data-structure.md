---
layout: post
title: OpenZeppelin v5 Data - Overview
date: 2025-07-29
lang: en
locale: en-GB
categories: solidity blockchain ethereum
tags: solidity ethereum openzeppelin data
description: This article explores data structures in OpenZeppelin Contracts v5, including EnumerableSet, DoubleEndedQueue, CircularBuffer, Checkpoints, Heap, and MerkleTree.
image: 
isMath: 
---

OpenZeppelin Contracts v5 is a robust and widely used smart contract library for Solidity developers. Among its many features, it includes a suite of **custom data structures** that simplify common patterns in decentralized applications. This article explores the following data structures:

- `BitMaps`
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
- Map can be cleared (all entries removed) in O(n).

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

### Example:

```solidity
CircularBuffer.Uint32Buffer private buffer;

constructor() {
    buffer = CircularBuffer.newUint32Buffer(5); // buffer of size 5
}

function addNumber(uint32 n) external {
    buffer.push(n); // Overwrites oldest if full
}

function getLatest() external view returns (uint32) {
    return buffer.at(buffer.length() - 1);
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

- peek (get the highest priority value): O(1)
- insert (insert a value): O(log(n))
- pop (remove the highest priority value): O(log(n))
- replace (replace the highest priority value with a new value): O(log(n))
- length (get the number of elements): O(1)
- clear (remove all elements): O(1)

------

## MerkleTree

### Description:

`MerkleTree` helps you construct and verify **Merkle proofs** on-chain. It’s useful in **airdrop verification**, **allowlists**, or **zero-knowledge applications**.

Each tree is a complete binary tree with the ability to sequentially insert leaves, changing them from a zero to a non-zero value and updating its root. 

This structure allows inserting commitments (or other entries) that are not stored, but can be proven to be part of the tree at a later time if the root is kept. See [`MerkleProof`](https://docs.openzeppelin.com/contracts/5.x/api/utils/cryptography#MerkleProof).

A tree is defined by the following parameters:

- `Depth`: The number of levels in the tree, it also defines the maximum number of leaves as 2**depth.
- `Zero value`: The value that represents an empty leaf. Used to avoid regular zero values to be part of the tree.
- `Hashing function`: A cryptographic hash function used to produce internal nodes. Defaults to [`Hashes.commutativeKeccak256`](https://docs.openzeppelin.com/contracts/5.x/api/utils/cryptography#Hashes-commutativeKeccak256-bytes32-bytes32-).

------

## Conclusion

OpenZeppelin’s data structures offer powerful building blocks for secure, efficient, and readable smart contracts. Understanding when and how to use them can greatly improve your smart contract design and reliability.

Whether you're managing whitelists (`EnumerableSet`), tracking history (`Checkpoints`), handling events (`CircularBuffer`, `Deque`), or implementing airdrop (`MerkleTree`), OpenZeppelin Contracts v5 offers several data structures to help you.



## Reference

- ChatGPT with the input "Write me an article about these different data strucutre available with openzeppelin v5. EnumerableSet DoubleEndedQueue CircularBuffer Checkpoints Heap MerkleTree If possible provide small example"
- [OpenZeppelin V5 - data structure](https://docs.openzeppelin.com/contracts/5.x/api/utils#data_structures)