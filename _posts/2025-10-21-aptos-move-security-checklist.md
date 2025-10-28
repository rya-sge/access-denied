---
layout: post
title: Aptos Move Security Checklist
date:   2025-10-21
lang: en
locale: en-GB
categories: blockchain
tags: aptos move
description: Aptos Security Checklist
image:
isMath: 

---

This article is a summary of the Aptos Documentation [Move Security Guidelines](https://aptos.dev/build/smart-contracts/move-security-guidelines) made with ChatGPT

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
-  Assign `store` only to data meant to persist in global storage.
-  Assign `key` only to resources that need to be globally accessible.

**Reminder:**

| Ability | Description                                                  |
| ------- | ------------------------------------------------------------ |
| copy    | Permits the duplication of values, allowing them to be used multiple times within the contract. |
| drop    | Allows values to be discarded from memory, which is necessary for controlling resources and preventing leaks. |
| store   | Enables data to be saved in the global storage, critical to persist data across transactions. |
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


## Reference

- [Move Security Guidelines](https://aptos.dev/build/smart-contracts/move-security-guidelines)
- ChatGPT to summarize the documentation