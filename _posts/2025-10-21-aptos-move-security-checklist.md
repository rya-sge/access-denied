---
layout: post
title: Aptos Move Security Checklist
date:   2025-10-21
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: blockchain
tags: aptos move
description: "Security checklist for Aptos Move modules, summarised from the Aptos Move Security Guidelines: access control, generics, abilities, arithmetic and more."
image: /assets/article/blockchain/aptos/2025-10-21-aptos-move-security-checklist-mindmap.png
isMath: 

---

This article is a summary of the Aptos Documentation [Move Security Guidelines](https://aptos.dev/build/smart-contracts/move-security-guidelines) made with ChatGPT

## What you need to know first

The checklist assumes the following Move and Aptos mechanisms, which it uses without developing them:

- **Modules and global storage.** Aptos code is published as Move modules, and persistent data lives in global storage as resources stored under an address. The operations `move_to`, `move_from` and `borrow_global` publish, remove and read a resource of a given type at an address.
- **`signer`.** A `&signer` argument represents the account that signed the transaction, and `signer::address_of` returns its address. Access control in Move compares addresses obtained this way with the owner of the data being accessed.
- **Aptos objects.** An object is a set of resources stored at its own address, with an owner that can be an account or another object. Creating one returns a `ConstructorRef`, from which capabilities such as transfer or extension rights are derived.
- **Generics and phantom type parameters.** A Move function or struct can take a type parameter, and a caller chooses it. A `phantom` parameter is not used in the struct's fields; it only distinguishes types, such as a coin type, so that values of different instantiations cannot be mixed.
- **Flash loan.** A loan that must be borrowed and repaid within a single transaction. The checklist uses it as the example where the returned asset must have the same type as the borrowed one.
- **Front-running and oracle manipulation.** Front-running is getting a transaction executed before a pending one to profit from it. Oracle manipulation means moving the price source a protocol reads, for example a single pool's spot price, to make the protocol act on a wrong price.

## Checklist

### Access Control

-  Verify signer ownership of all objects passed to functions.
-  Use `object::owner(&obj) == address_of(user)` before granting access to resources.
-  Restrict global storage access to the signer’s own address (`move_from` / `borrow_global` using `signer::address_of`).
-  Avoid exposing sensitive objects to any user or function.

### Function Visibility

-  Start all functions as `private` by default.
-  Use `entry` for functions callable via Aptos CLI/SDK.
  - Implement proper access control if required
-  Use `public(friend)` for functions accessible only by trusted modules.
-  Apply `#[view]` to read-only functions that should not modify state.
-  Confirm no sensitive logic is exposed through `public` functions unnecessarily.

**Reminder:**

|                | Module itself | Other Modules                              | Aptos CLI/SDK |
| -------------- | ------------- | ------------------------------------------ | ------------- |
| private        | &#x2611;      | &#x2612;                                   | &#x2612;      |
| public(friend) | &#x2611;      | &#x2611;if friend<br /> &#x2612; otherwise | &#x2612;      |
| public         | &#x2611;      | &#x2611;                                   | &#x2612;      |
| entry          | &#x2611;      | &#x2612;                                   | &#x2611;      |

### Type Safety and Generics

-  Validate generic types explicitly; do not trust unchecked generics.
-  Use phantom type parameters to enforce type constraints where necessary.
-  Ensure loaned or returned assets match the original type (e.g., flash loans).

### Resource Management & Unbounded Execution

-  Avoid loops over globally shared structures with unbounded entries.
-  Store user-specific assets in individual user accounts.
-  Separate module/package objects from user objects to prevent interference.
-  Use efficient data structures (e.g., `SmartTable`) for large collections.

### Move Abilities

-  Assign `copy` only where duplication of data is safe.
-  Assign `drop` only to resources that can be safely discarded.
-  Assign `store` only to data meant to be held inside other structs in global storage (a top-level resource needs `key`).
-  Assign `key` only to resources that need to be globally accessible.

**Reminder:**

| Ability | Description                                                  |
| ------- | ------------------------------------------------------------ |
| copy    | Permits the duplication of values, allowing them to be used multiple times within the contract. |
| drop    | Allows values to be dropped (discarded) when they go out of scope; a type without `drop` must be explicitly consumed, so an asset cannot be lost by accident. |
| store   | Allows values to exist inside a struct in global storage; storing a value at the top level of an account (`move_to`) requires `key`. |
| key     | Grants data the ability to serve as a key in global storage operations, important for data retrieval and manipulation. |

### Arithmetic Safety

-  Handle integer truncation for division; ensure fees or calculations cannot round down to zero.
-  Consider integer overflow/underflow; `+`, `-`, `*` abort on overflow, `/` aborts on divide-by-zero.
-  Avoid left-shift operations that exceed integer capacity.

### Aptos Objects

-  ConstructorRef leak
   -  When creating objects ensure to never expose publicly the object’s `ConstructorRef` as it allows adding resources to an object.

-  Keep objects in separate accounts when multiple objects are created together.
-  Prevent ownership leaks or unauthorized transfers of grouped objects.

### Business Logic Security

- **Front-running**
  -  Avoid multi-transaction sequences that can be manipulated.
  -  Combine state changes in a single transaction where possible.
- **Price Oracle Manipulation**
  -  Use multiple oracles to determine prices.
  -  Implement fallback mechanisms if primary oracle fails.
- **Token Identifier Collision**
  - When dealing with tokens, ensure that the method for comparing token structs to establish a deterministic ordering does not lead to collisions. 
  - Use unique `object::object_address` identifiers rather than concatenated strings.

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Move** | The smart contract language used on Aptos, whose type system and abilities control how values can be copied, discarded and stored. |
| **Module** | A unit of published Move code that defines structs and functions and controls who may call them through visibility. |
| **Global storage** | The on-chain storage where resources are kept under addresses and accessed with `move_from` or `borrow_global`. |
| **Resource** | A struct value held in global storage; access to it must be restricted to its owner. |
| **`signer`** | The value that represents the transaction's signing account; `signer::address_of` gives the address used in ownership checks. |
| **`entry` function** | A function that can be called from the Aptos CLI or SDK as a transaction, which needs its own access control. |
| **`public(friend)`** | A visibility that lets only the modules declared as friends call a function. |
| **`#[view]`** | An attribute for read-only functions that should not modify state. |
| **Abilities** | The `copy`, `drop`, `store` and `key` markers that decide whether a type can be duplicated, discarded, held inside a struct in global storage or used as a key in it. |
| **Phantom type parameter** | A type parameter that is not used in a struct's fields and only serves to enforce type constraints. |
| **`SmartTable`** | An Aptos data structure for large collections, recommended over loops on shared structures with unbounded entries. |
| **Aptos object** | A set of resources at its own address with an owner, whose ownership must be checked with `object::owner` before access is granted. |
| **`ConstructorRef`** | The reference returned when an object is created, which allows adding resources to it and must never be exposed publicly. |
| **Integer truncation** | The rounding down of integer division, which can make a fee or a calculation round to zero. |
| **Price oracle manipulation** | Making a protocol act on a wrong price by moving its price source, mitigated by using several oracles and a fallback. |
| **Token identifier collision** | Two different tokens producing the same identifier when it is built from concatenated strings, avoided by using `object::object_address`. |

## Reference

- [Move Security Guidelines](https://aptos.dev/build/smart-contracts/move-security-guidelines)
- [The Move on Aptos Book - Generics and Type Abilities](https://aptos-labs.github.io/move-book/generics-and-abilities.html)
- ChatGPT to summarize the documentation

## Mindmap

The mindmap below summarizes the article.

![Aptos Move security checklist mindmap]({{site.url_complet}}/assets/article/blockchain/aptos/2025-10-21-aptos-move-security-checklist-mindmap.png)
