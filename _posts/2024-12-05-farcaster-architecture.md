---
layout: post
title:  Decentralizing Social Platform - Exploring Farcaster’s Architecture
date:   2024-12-05
lang: en
locale: en-GB
categories: blockchain ethereum
tags: social
description: Farcaster is a sufficiently decentralized social network built on Ethereum. It is a public social network similar to Twitter and Reddit. Users can create profiles, share posts known as "casts," and follow others. Users have full ownership of their accounts and connections, allowing them the freedom to transition between different apps.
image: 
isMath: false
---

Farcaster is a [sufficiently decentralized](https://www.varunsrinivasan.com/2022/01/11/sufficient-decentralization-for-social-networks) social network built on Ethereum.

It is a public social network similar to Twitter and Reddit. Users can create profiles, share posts known as "casts," and follow others. Users have full ownership of their accounts and connections, allowing them the freedom to transition between different apps.

> Warning: this article is still in draft state and its content is still mainly taken from the Farcaster documentation, part [architecture](https://docs.farcaster.xyz/learn/architecture/overview#architecture) . Its content should become more personal later.
>

[TOC]



## Overview

Farcaster has a hybrid architecture that stores identity onchain and data offchain.

![Architecture](https://docs.farcaster.xyz/assets/architecture.BPu0I8Sc.png)

### Onchain

Farcaster's onchain systems are implemented as [contracts on OP Mainnet](https://docs.farcaster.xyz/learn/architecture/contracts). Actions are performed onchain only when security and consistency are critical. Use of onchain actions is kept at a minimum to reduce costs and improve performance.

Only a handful of actions are performed onchain, including:

- Creating an [account](https://docs.farcaster.xyz/learn/what-is-farcaster/accounts).
- Paying rent to [store data](https://docs.farcaster.xyz/learn/what-is-farcaster/messages#storage).
- Adding account keys for [connected apps](https://docs.farcaster.xyz/learn/what-is-farcaster/apps#connected-apps).

See [docs.farcaster.xyz - overview#onchain](https://docs.farcaster.xyz/learn/architecture/overview#onchain)

### Offchain

Farcaster's offchain system is a peer-to-peer network of servers called [Hubs](https://docs.farcaster.xyz/learn/architecture/hubs) which store user data. The majority of user actions are performed offchain. These include:

- Posting a new public message.
- Following another user.
- Reacting to a post.
- Updating your profile picture.

Actions are performed offchain when performance and cost are critical. Use of offchain actions is typically preferred when consistency isn't a strict requirement. Offchain systems achieve security by relying on signatures from onchain systems.

See [docs.farcaster.xyz - overview#offchain](https://docs.farcaster.xyz/learn/architecture/overview#offchain)

## Contracts

A Farcaster account is managed and secured onchain using the Farcaster contracts. This section provides a high level overview and avoids some implementation details. 

For the full picture, see the [contracts repository](https://github.com/farcasterxyz/contracts/).

There are three main contracts deployed on OP Mainnet:

- **Id Registry** - creates new accounts
- **Storage Registry** - rents storage to accounts
- **Key Registry** - adds and removes app keys from accounts



![Registry Contracts](https://docs.farcaster.xyz/assets/registry-contracts.C93-05Rq.png)

The contracts are deployed at the following addresses:

| Contract        | Address                                                      |
| :-------------- | :----------------------------------------------------------- |
| IdRegistry      | [0x00000000fc6c5f01fc30151999387bb99a9f489b](https://optimistic.etherscan.io/address/0x00000000fc6c5f01fc30151999387bb99a9f489b) |
| StorageRegistry | [0x00000000fcce7f938e7ae6d3c335bd6a1a7c593d](https://optimistic.etherscan.io/address/0x00000000fcce7f938e7ae6d3c335bd6a1a7c593d) |
| KeyRegistry     | [0x00000000fc1237824fb747abde0ff18990e59b7e](https://optimistic.etherscan.io/address/0x00000000fc1237824fb747abde0ff18990e59b7e) |

See [docs.farcaster.xyz - contracts](https://docs.farcaster.xyz/learn/architecture/contracts#contracts)

### Id Registry

The IdRegistry lets users register, transfer and recover Farcaster accounts. 

- An account is identified by a unique number (the fid) which is assigned to an Ethereum address on registration.
-  An Ethereum address may only own one account at a time, though it may transfer it freely to other accounts. 
- It may also specify a recovery address which can transfer the account at any time.

See [docs.farcaster - id-registry](https://docs.farcaster.xyz/learn/architecture/contracts#id-registry) & [github.com/farcasterxyz - IdRegistry.sol](https://github.com/farcasterxyz/contracts/blob/0451f3f1c2219db467fa128a06d5938392d2974a/src/IdRegistry.sol)

![farcaster-id-registry]({{site.url_complet}}/assets/article/blockchain/social/farcaster/farcaster-id-registry.png)

### Storage Registry

The Storage Registry lets accounts rent [storage](https://docs.farcaster.xyz/learn/what-is-farcaster/messages#storage) by making a payment in ETH. 

- The storage prices are set by admins in USD and converted to ETH using a Chainlink oracle.
- The price increases or decreases based on supply and demand.

See [docs.farcaster - storage-registry](https://docs.farcaster.xyz/learn/architecture/contracts#storage-registry)  & [farcasterxyz/contracts - StorageRegistry.sol](https://github.com/farcasterxyz/contracts/blob/1aceebe916de446f69b98ba1745a42f071785730/src/StorageRegistry.sol)

![farcaster-storage-registry]({{site.url_complet}}/assets/article/blockchain/social/farcaster/farcaster-storage-registry.png)



### Key Registry

The Key Registry lets accounts issue keys to apps, so that they can publish messages on their behalf. Keys can be added or removed at any time. 

- To add a key, an account must submit the public key of an EdDSA key pair along with a requestor signature. 
- The requestor can be the account itself or an app that wants to operate on its behalf.

See [docs.farcaster - key-registry](https://docs.farcaster.xyz/learn/architecture/contracts#key-registry) & [github.com/farcasterxyz - KeyRegistry.sol](https://github.com/farcasterxyz/contracts/blob/0451f3f1c2219db467fa128a06d5938392d2974a/src/KeyRegistry.sol)

![farcaster-key-registry]({{site.url_complet}}/assets/article/blockchain/social/farcaster/farcaster-key-registry.png)



## Hubs

Hubs are a distributed network of servers that store and validate Farcaster data.

- A computer can run software to become a Farcaster Hub. It will download onchain Farcaster data from Ethereum and offchain Farcaster data from other Hubs. 

- Each Hub stores a copy of all Farcaster data, which can be accessed over an API.

- Hubs let you read and write data to Farcaster, and anyone building a Farcaster app will need to talk to one. 

- Anyone can run a Hub on their laptop or on a cloud server. A full guide to setting up and running a Hub is available [here](https://www.thehubble.xyz/).

See [docs.farcaster - hubs](https://docs.farcaster.xyz/learn/architecture/hubs#hubs)

### Design

A Hub starts by syncing data from Farcaster contracts on the Optimism blockchain. It becomes aware of every user's account and their account keys.

A message is a cryptographically signed binary data object that represents a delta-operation on the Farcaster network.

```protobuf
message Message {
  MessageData data = 1;                  // Contents of the message
  bytes hash = 2;                        // Hash digest of data
  HashScheme hash_scheme = 3;            // Hash scheme that produced the hash digest
  bytes signature = 4;                   // Signature of the hash digest
  SignatureScheme signature_scheme = 5;  // Signature scheme that produced the signature
  bytes signer = 6;                      // Public key or address of the key pair that produced the signature
  optional bytes data_bytes = 7;         // MessageData serialized to bytes if using protobuf serialization other than ts-proto
}
```

See [farcasterxyz - SPECIFICATION.md](https://github.com/farcasterxyz/protocol/blob/main/docs/SPECIFICATION.md)

The lifecycle of a Farcaster message looks like this:

1. Alice creates a new "Hello World!" message.
2. Alice (or her app) signs the message with an account key.
3. Alice (or her app) uploads the message to a Hub.
4. The Hub checks the message's validity.
5. The Hub sends the message to peer hubs over gossip.

![Hub](https://docs.farcaster.xyz/assets/hub.9TTY5EdM.png)

See [docs.farcaster - hubs#design](https://docs.farcaster.xyz/learn/architecture/hubs#design) & [hubs#faq](https://docs.farcaster.xyz/learn/architecture/hubs#faq)



### Validation

Alice's message is validated by checking that it has a valid signature from one of her account keys. The Hub also ensures that the message obeys the requirements of the message type. For example, a public message or "cast" must be less than 320 bytes. Message type requirements are specified in detail in the [protocol spec](https://github.com/farcasterxyz/protocol/blob/main/docs/SPECIFICATION.md).

[docs.farcaster - hubs#validation](https://docs.farcaster.xyz/learn/architecture/hubs#validation)

### Storage

Alice's message is then checked for conflicts before being stored in the Hub. Conflicts can occur for many reasons:

1. The Hub already has a copy of the message.
2. The Hub has a later message from Alice deleting this message.
3. Alice has only paid rent for 5000 casts, and this is her 5001st cast.

Conflicts are resolved deterministically and asynchronously using CRDTs (Conflict-free Replicated Data Types). For example, if Alice has no space to store messages, her oldest message will be removed.

See [docs.farcaster.xyz - hubs#storage](https://docs.farcaster.xyz/learn/architecture/hubs#storage)

### Replication

Hubs sync using a two-phase process: gossip and diff sync. When a Hub receives and stores a message, it immediately gossips it to its peers. Gossip is performed using libp2p's gossipsub protocol and is lossy. Hubs then periodically select a random peer and perform a diff sync to find dropped messages. The diff sync process compares merkle tries of message hashes to efficiently find dropped messages.

See [docs.farcaster.xyz - hubs#replication](https://docs.farcaster.xyz/learn/architecture/hubs#replication)

### Consistency

Hubs are said to have strong eventual consistency. If a Hub is disconnected, it can be written to it and will recover safely when it comes online. This is unlike blockchains where a node that is disconnected cannot confirm transactions. The downside is that messages may arrive out of order. For example, Bob's reply to Alice might appear before her "Hello World!" message.

See [docs.farcaster - hubs#consistency](https://docs.farcaster.xyz/learn/architecture/hubs#consistency)

### Peer Scoring

Hubs monitor peers and score their behavior. If a peer doesn't accept valid messages, falls behind, or gossips too much it may be ignored by its peers.

See [docs.farcaster - hubs#peer-scoring](https://docs.farcaster.xyz/learn/architecture/hubs#peer-scoring)

### Implementations

[/docs.farcaster.xyz - hubs#implementations](https://docs.farcaster.xyz/learn/architecture/hubs#implementations)

- [Hubble](https://www.thehubble.xyz/) - a Hub implementation in TypeScript and Rust

## ENS Names

Farcaster uses ENS names as human readable identifiers for accounts. Two kinds of ENS names are supported:

- **Offchain ENS names**: free and controlled by farcaster. (e.g. @alice)
- **Onchain ENS names**: costs money and is controlled by your wallet. (e.g. @alice.eth)

ENS names can only be used on Farcaster if they are <= 16 characters and contain only lowercase letters, numbers, and hyphens.

![Usernames](https://docs.farcaster.xyz/assets/usernames.D0JzJrCz.png)

See [docs.farcaster.xyz - ens-names#ens-names](https://docs.farcaster.xyz/learn/architecture/ens-names#ens-names)

### Onchain ENS Names

Users can use onchain ENS names like `@alice.eth` on Farcaster.

Onchain ENS names are issued by ENS, end in .eth and must be registered on the Ethereum L1 blockchain. Anyone can register an ENS name by using the [ENS app](https://app.ens.domains/).

Users must pay a fee to register an onchain ENS name, but once registered, it is controlled by the user and cannot be revoked.

See [docs.farcaster.xyz - ens-names#onchain-ens-names](https://docs.farcaster.xyz/learn/architecture/ens-names#onchain-ens-names)

### Offchain ENS Names (Fnames)

Users can use offchain ENS names like `@alice` on Farcaster.

Offchain ENS names, also called Farcaster Names or Fnames, are compliant with ENS but registered offchain. Fnames are free but are subject to a usage policy to prevent squatting and impersonation. They are also subject to the following requirements:

1. An account can only have one Fname at a time.
2. An account can change its Fname once every 28 days.

See [docs.farcaster.xyz - offchain-ens-names-fnames](https://docs.farcaster.xyz/learn/architecture/ens-names#offchain-ens-names-fnames)

#### Usage Policy

Registering an Fname is free but subject to the following policy:

1. Names connected to public figures or entities may be reclaimed (e.g. @google).
2. Names that haven't been used for 60+ days may be reclaimed.
3. Names that are registered for the sole purpose of resale may be reclaimed.

Decisions are made by the Farcaster team and often require human judgment. Users who want a name that is fully under their control should use an onchain ENS name.

See [docs.farcaster.xyz - usage-policy](https://docs.farcaster.xyz/learn/architecture/ens-names#usage-policy)

#### Registry

Fnames are issued as offchain names under the subdomain `fcast.id`.

Bob can register the offchain ENS name `bob.fcast.id` and use it on any Farcaster app with the shorthand `@bob`. The name can be registered by making a signed request to the Fname Registry server. See the [FName API reference](https://docs.farcaster.xyz/reference/fname/api) for more details on how to query and create Fnames.

To learn more about how Fnames work, see [ENSIP-16](https://docs.ens.domains/ens-improvement-proposals/ensip-16-offchain-metadata) and [ERC-3668](https://eips.ethereum.org/EIPS/eip-3668).

See [docs.farcaster.xyz - registry](https://docs.farcaster.xyz/learn/architecture/ens-names#registry)

## Reference

See [Farcaster doc](https://docs.farcaster.xyz/)