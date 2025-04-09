---
layout: post
title: "An Overview of Merkle DAGs in Distributed Systems Like Git and IPFS"
date: 2025-04-09
lang: en
locale: en-GB
categories: blockchain programmation
tags: ipfs merkle-tree merkle-dag dag graph git
description: Learn what a Merkle DAG is and how it used in distributed systems like IPFS and Git. This overview explains the structure, key benefits, and use cases of Merkle DAGs in content-addressed storage and version control.
image: /assets/article/cryptographie/merkle-tree/merkle-dag-deduplication.png
isMath: false
---

A Merkle Directed Acyclic Graph (Merkle DAG) is a data structure that combines the principles of a **Merkle tree** and a **Directed Acyclic Graph (DAG)**. It is used in distributed systems, version control,  and content-addressable storage systems.

The two main examples are:

-  **Git** which use them to efficiently store the repository history in a way that enables de-duplicating the objects and detecting conflicts between branches.
- [IPFS](https://ipfs.tech)  which uses a Merkle DAG to implement a peer-to-peer content delivery network.
-  In distributed databases like [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), Merkle-Trees are used for efficient comparison and reconciliation of the state between replicas. 

This article delves into the mechanics, applications, and advantages of Merkle DAGs.

Reference: [Merkle-DAGs meet CRDTs](https://hector.link/presentations/merkle-crdts/merkle-crdts.pdf)

[TOC]



------

### Understanding Merkle DAGs

#### Merkle Trees

A Merkle tree is a cryptographic data structure in which every leaf node contains a hash of a data block, and every non-leaf node contains the hash of its child nodes. The root hash serves as a compact representation of the entire data structure, ensuring data integrity and enabling efficient verification.

Schema from [Wikipedia](https://en.wikipedia.org/wiki/Merkle_tree)

![wikipedia_hash_hree]({{site.url_complet}}/assets/article/cryptographie/merkle-tree/wikipedia_hash_hree.png)

#### Directed Acyclic Graph (DAG)

A DAG is a graph with directed edges and no cycles. This structure is ideal for representing systems where dependencies flow in a single direction, such as task scheduling, data pipelines, and blockchain.

In DAGs, several branches can re-converge or, in other words, a node can have several parents.

#### Merkle DAG

A Merkle DAG merges these concepts by organizing data into a graph where nodes represent data blocks, and edges represent hashes. Unlike a pure tree structure, a DAG allows nodes to have multiple parent nodes, making it more versatile and efficient for certain applications.

Merkle DAGs are similar to Merkle trees, but there are no balance requirements, and every node can carry a payload. 

Reference: [docs.ipfs.tech  - merkle-dag](https://docs.ipfs.tech/concepts/merkle-dag/)

------

### Key Properties of Merkle DAGs

1. **Content Addressability**
   Each node in a Merkle DAG is identified by its cryptographic hash, which uniquely represents its content. This ensures that nodes with identical content have the same identifier, reducing redundancy.
2. **Immutability**
   Once a node is added to the Merkle DAG, its hash—and by extension, its position in the graph—cannot change without altering its entire lineage. This property is crucial for ensuring data integrity.
3. **Efficient Verification**
   Like Merkle trees, Merkle DAGs allow for efficient proof and verification processes. Verifying the integrity of a single node or file requires only the hashes along its path to the root.
4. **Deduplication**
   Since nodes are content-addressable, identical data is represented by the same node, which eliminates unnecessary duplication and optimizes storage.

------

### Applications of Merkle DAGs

1. **Version Control Systems**
   Git, a popular version control system, uses a kind of Merkle DAG to manage and track file changes. Each commit in Git is a node, and the connections between nodes represent the history and relationships of changes.

   See [Understanding Merkle Trees](https://medium.com/geekculture/understanding-merkle-trees-f48732772199)

2. **Content-Addressable Storage**
   Systems like the InterPlanetary File System (IPFS) utilize Merkle DAGs to store and retrieve files. By breaking files into smaller chunks and linking them in a DAG, IPFS ensures deduplication and enables fast, decentralized access.

3. **Data Synchronization**
   Distributed databases and file-sharing protocols leverage Merkle DAGs for efficient synchronization. Changes can be detected and propagated by comparing hash paths.¨

----

## Examples

### Git

Git stores content in a manner similar to a UNIX filesystem, but a bit simplified. 

All the content is stored as tree and blob objects, with:

- `trees` corresponding to UNIX directory entries
- `blobs` corresponding more or less to inodes or file contents. 

A single tree object contains one or more entries, each of which is the SHA-1 hash of a blob or subtree with its associated mode, type, and filename.

 For example, a project where the most-recent tree looks something like:

```bash
git cat-file -p master^{tree}
```

```console
100644 blob a906cb2a4a904a152e80877d4088654daad0c859      README
100644 blob 8f94139338f9404f26296befa88755fc2598c289      Rakefile
040000 tree 99f1a6d12cb4b6f19c8655fca46c3ecf317074e0      lib
```

The `master^{tree}` syntax specifies the tree object that is pointed to by the last commit on your `master` branch. 

Notice that the `lib` subdirectory isn’t a blob but a pointer to another tree:

```bash
git cat-file -p 99f1a6d12cb4b6f19c8655fca46c3ecf317074e0
```

```console
100644 blob 47c6340d6459e05787f644c2447d2595f5d3a54b      simplegit.rb
```



The resulting tree will be the following:



![git-scm-data-model-1]({{site.url_complet}}/assets/article/cryptographie/merkle-tree/git-scm-data-model-1.png)

Another example:

Here, the hash is also present in the schema

![git-scm-data-model-2]({{site.url_complet}}/assets/article/cryptographie/merkle-tree/git-scm-data-model-2.png)

Reference:

- [blog.devgenius.io - GIT Internals](https://blog.devgenius.io/git-internals-347ec16ba507)
- [git-scm - Git Internals - Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [Understanding Merkle Trees](https://medium.com/geekculture/understanding-merkle-trees-f48732772199)

### IPFS

A Merkle DAG in IPFS is a DAG where each node has an identifier called a CID, and this is the result of hashing the node's contents — any opaque payload carried by the node and the list of identifiers of its children — using a cryptographic hash function like SHA-226. 

- Merkle DAGs can only be constructed from the leaves, that is, from nodes without children. 
- Parents are added after children because the children's identifiers must be computed in advance to be able to link them.
- Every node in a Merkle DAG is the root of a (sub)Merkle DAG itself, and this subgraph is *contained* in the parent DAG.

- Merkle DAGs are *self-verified* structures. The CID of a node is univocally linked to the contents of its payload and those of all its descendants. Thus two nodes with the same CID univocally represent exactly the same DAG. This will be a key property to efficiently sync Merkle-CRDTs (Conflict-free Replicated Data Types) without having to copy the full DAG, as exploited by systems like IPFS.

### Example

This example came from [proto.school/merkle-dags/07](https://proto.school/merkle-dags/07)

For an example of small-scale data duplication, consider the use case of tracking changes files in a directory over time (this is often called *versioning*).

We have this dag, constructed from a file directory `pics`which contain two folders inside: `fish`and `cats`.

One change we could make to this directory is to delete the "fish" directory, replacing it with a directory called "dogs". Since it is not possible to remove a directory, these change will create a new DAG, representing an updated state of the directory. 

However, all of the nodes representing the "cats" directory and its files are common to both DAGs. Therefore, we can reuse them, as depicted below, where:

- The orange nodes represent nodes that are only used in the original DAG,
- The green nodes represent those that are common to both, 
- and the blue nodes represent the extra nodes needed for the new state.

Schema from [proto.school/merkle-dags/07](https://proto.school/merkle-dags/07)

![merkle-dag-deduplication]({{site.url_complet}}/assets/article/cryptographie/merkle-tree/merkle-dag-deduplication.png)

Reference:  [IPFS Merke Directed Acyclic Graphs](https://docs.ipfs.tech/concepts/merkle-dag/), [proto.school - Anatomy of a CID](https://proto.school/anatomy-of-a-cid/01)

See also [IPFS - Lesson: Turn a File into a Tree of Hashes](https://dweb-primer.ipfs.io/ipfs-dag/files-as-dags)

------

### Advantages of Merkle DAGs

- **Scalability**: Merkle DAGs handle large datasets effectively, making them suitable for distributed and decentralized systems.
- **Data Integrity**: The hash function used ensures tamper-proof data since any modification of the data will result in a different hash.
- **Efficient Updates**: Partial updates to the structure require rehashing only affected nodes, reducing computational overhead.
- **Decentralization**: Content addressability and deduplication enable decentralized storage and retrieval.

------

### Challenges and Limitations

While Merkle DAGs are powerful, they are not without challenges:

1. **Complexity**: The implementation and management of Merkle DAGs can be more complex compared to simpler data structures or a traditional Merkle Tree.
2. **Storage Overhead**: Storing hash values alongside data adds overhead compared to a traditional Merkle Tree.

## Reference

### IPFS

- [Merkle-DAGs meet CRDTs](https://hector.link/presentations/merkle-crdts/merkle-crdts.pdf)
- [IPFS Merke Directed Acyclic Graphs](https://docs.ipfs.tech/concepts/merkle-dag/), [proto.school - Anatomy of a CID](https://proto.school/anatomy-of-a-cid/01)
- [IPFS - Lesson: Turn a File into a Tree of Hashes](https://dweb-primer.ipfs.io/ipfs-dag/files-as-dags)
- [proto.school/merkle-dags/07](https://proto.school/merkle-dags/07)
- [proto.school - Anatomy of a CID](https://proto.school/anatomy-of-a-cid/01)

### Git

- [blog.devgenius.io - GIT Internals](https://blog.devgenius.io/git-internals-347ec16ba507)
- [git-scm - Git Internals - Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [Understanding Merkle Trees](https://medium.com/geekculture/understanding-merkle-trees-f48732772199)