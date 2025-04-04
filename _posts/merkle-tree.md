### Understanding Merkle Trees: Structure, Function, and Applications

In computer science and cryptography, Merkle trees are widely used for ensuring data integrity and efficient verification. However, in practice, various adaptations of this structure have been developed to address different computational and storage challenges. These variations, such as Merkle DAGs (Directed Acyclic Graphs) and Patricia Trees, enhance flexibility, scalability, and performance across a range of applications. This article explores the foundational concept of Merkle trees, examines their key variants, and highlights their real-world implementations.

### What is a Merkle Tree?

A **Merkle tree**, also called a **hash tree**, is a data structure that efficiently and securely verifies the integrity of large datasets. At its core, a Merkle tree organizes data into a hierarchical structure:

- **Leaf nodes** contain the hash of data blocks.
- **Non-leaf nodes** store the cryptographic hash of their child nodes.

The tree culminates in a **Merkle root**, representing the entire dataset's integrity. Any change in the underlying data causes a change in the Merkle root, enabling tamper detection.



In the world of computer science and cryptography, **Merkle trees** play a pivotal role in ensuring data integrity and enabling secure communication. 

Named after their inventor, Ralph Merkle, these trees are a type of binary tree where:

- each leaf node is a cryptographic hash of data
- each non-leaf node is a hash of its children nodes. 

They have become an essential component in blockchain technologies, distributed systems, and data verification processes. This article explores what Merkle trees are, how they work, and the various contexts in which they are used.

------

### What is a Merkle Tree?

A **Merkle tree**, also known as a **hash tree**, is a data structure used to efficiently and securely verify the integrity of large sets of data. The tree consists of nodes where:

- **Leaf nodes** contain the hash of a data block.
- **Non-leaf nodes** (internal nodes) contain the cryptographic hash of their respective child nodes.

This structure allows for the verification of the contents of a large set of data without the need to access every individual element. 

Instead, a **Merkle root** — the hash at the top of the tree — can be used to represent the entire dataset. By hashing the data in a way that each node depends on the integrity of its children, any change in the data results in a completely different Merkle root, allowing for easy detection of any tampering.

### How Do Merkle Trees Work?

The process of constructing a Merkle tree involves several steps:

1. **Data Hashing**: Start by hashing the individual data blocks (usually using cryptographic hash functions such as SHA-256).
2. **Pairing Hashes**: Pair the hashed data and compute the hash of the pair. This continues recursively up the tree until only one hash remains: the Merkle root.
3. **Merkle Root**: This root represents the entire dataset and can be used for validation purposes. If any data is altered, the Merkle root will change, signaling that the data has been tampered with.

For example, if we have four data blocks A, B, C, and D, the steps would look like this:

- Hash(A), Hash(B), Hash(C), Hash(D)
- Hash(Hash(A) + Hash(B)) and Hash(Hash(C) + Hash(D))
- Merkle Root = Hash(Hash(Hash(A) + Hash(B)) + Hash(Hash(C) + Hash(D)))

### Advantages of Merkle Trees

1. **Efficiency**: Merkle trees allow for efficient data verification. Instead of checking every data block, only the hashes along the path from a leaf to the Merkle root need to be verified.
2. **Security**: By utilizing cryptographic hash functions, Merkle trees ensure that any change in the data will lead to a completely different Merkle root, making it easy to detect tampering.
3. **Scalability**: Merkle trees are particularly useful for large datasets, as they provide a compact representation of data integrity without needing to store the entire dataset.





------

### Contexts Where Merkle Trees Are Used

#### 1. **Blockchain and Cryptocurrencies**

The most well-known use of Merkle trees is in **blockchain technology**. Blockchains, such as Bitcoin and Ethereum, rely on Merkle trees to organize transactions within blocks. Each block contains a list of transactions, and the Merkle tree structure ensures that the integrity of the entire block can be easily verified by just checking the Merkle root. This approach allows for:

- **Efficient Transaction Verification**: By using Merkle proofs, nodes can verify individual transactions without downloading the entire block.
- **Secure Blockchain**: Since each transaction is linked to the Merkle root, tampering with any transaction would alter the root and make it immediately obvious to the network.

#### 2. **Distributed Systems and File Sharing**

In distributed systems, Merkle trees are used to verify the consistency of data across multiple nodes. Systems like **Git** (for version control) and **IPFS** (InterPlanetary File System) leverage Merkle trees to ensure data integrity and synchronize content across distributed networks.

By using Merkle trees, these systems can detect discrepancies between nodes, ensure that files are not corrupted, and prevent unauthorized changes.

- **Git** uses Merkle trees to represent versions of files, allowing users to easily track changes over time and verify the integrity of their code.  Merkle DAGs are very widely used. Source control systems like git and others use them to efficiently store the repository history in a way that enables de-duplicating the objects and detecting conflicts between branches.

### IPFS

**IPFS** uses Merkle trees to organize and verify the blocks of data in its decentralized file storage system. 

In their case, they use a variant of Merkle Tree called Merkle DAG. Merkle DAGs are similar to Merkle trees, but there are no balance requirements, and every node can carry a payload. See [docs.ipfs.tech - merkle-dag/]( https://docs.ipfs.tech/concepts/merkle-dag/)

dentifying a data object (like a Merkle DAG node) by the value of its hash is referred to as *content addressing*. Thus, we name the node identifier as [*Content Identifier*](https://docs.ipfs.tech/concepts/content-addressing/), or CID.

### Details

A Merkle DAG is a DAG where each node has an identifier, and this is the result of hashing the node's contents — any opaque payload carried by the node and the list of identifiers of its children — using a cryptographic hash function like SHA256. This brings some important considerations:

- Merkle DAGs can only be constructed from the leaves, that is, from nodes without children. Parents are added after children because the children's identifiers must be computed in advance to be able to link them.
- Every node in a Merkle DAG is the root of a (sub)Merkle DAG itself, and this subgraph is *contained* in the parent DAG.
- Merkle DAG nodes are *immutable*. Any change in a node would alter its identifier and thus affect all the ascendants in the DAG, essentially creating a different DAG.

For example, the previous linked list, assuming that the payload of each node is just the CID of its descendant, would be: 

*A=Hash(B)→B=Hash(C)→C=Hash(∅)*. 

- **no cycles**: The properties of the hash function ensure that no cycles can exist when creating Merkle DAGs. (Note: Hash functions are one-way functions. Creating a cycle should then be impossibly difficult unless some weakness is discovered and exploited.)
- Merkle DAGs are *self-verified* structures. The CID of a node is univocally linked to the contents of its payload and those of all its descendants. Thus two nodes with the same CID univocally represent exactly the same DAG. This will be a key property to efficiently sync Merkle-CRDTs (Conflict-free Replicated Data Types) without having to copy the full DAG, as exploited by systems like IPFS.

From [IPFS Merke Directed Acyclic Graphs](https://docs.ipfs.tech/concepts/merkle-dag/)

See also [IPFS - Lesson: Turn a File into a Tree of Hashes](https://dweb-primer.ipfs.io/ipfs-dag/files-as-dags)

#### Data Integrity and Authentication

Merkle trees are also used in various data integrity and authentication mechanisms, especially in contexts where large datasets need to be verified for correctness.

- **Software Updates**: When software updates are delivered, a Merkle tree can be used to ensure the integrity of the update package. The update server provides a Merkle root, and the client can verify the integrity of the received data by comparing the hashes.
- **Secure Communication Protocols**: In secure messaging or communication protocols, Merkle trees are used to authenticate messages. By hashing messages and using Merkle roots, the recipient can verify that the message has not been altered in transit.

#### 4. **Cloud Storage and Backup Systems**

Cloud storage services that rely on data integrity checks can also benefit from Merkle trees. For example, if a cloud service wants to verify that a file has not been tampered with during storage or transmission, the Merkle root can serve as a fingerprint of the file’s integrity.

Merkle trees can also be used for:

- **Efficient Syncing**: To verify and synchronize files across different devices or cloud storage platforms.
- **Version Control**: Tracking changes in large datasets and enabling the ability to restore previous versions.

#### 5. **Cryptographic Protocols and Zero-Knowledge Proofs**

In cryptography, Merkle trees are utilized in **zero-knowledge proofs**, which allow one party to prove the validity of a statement to another party without revealing the statement itself. Merkle trees enable the creation of **Merkle proofs**, which allow verification of a specific piece of data in a dataset without needing to expose the entire dataset.

## Example

Merkle Proof Generator and Validator in Solidity

Murky contains contracts that can generate merkle roots and proofs. Murky also performs inclusion verification. A couple of default implementations are available out-of-the-box:

1. [`Merkle.sol`](https://github.com/dmfxyz/murky/blob/main/src/Merkle.sol) is the original Murky implementation. It implements the tree as a [Full Binary Tree](https://xlinux.nist.gov/dads/HTML/fullBinaryTree.html).
2. [`CompleteMerkle.sol`](https://github.com/dmfxyz/murky/blob/main/src/CompleteMerkle.sol) is a merkle tree implementation using [Complete Binary Trees](https://xlinux.nist.gov/dads/HTML/completeBinaryTree.html). Some external libraries, particulary front-end or off-chain ones, use this type of tree.



The function `checkInWhitelist`perform the following actions

- Compute the data leaf from the argument. The leaf is the hash of `msg.sender`and the maximum allowed to mint for this address

```solidity
bytes32 leaf = keccak256(abi.encodePacked(msg.sender, maxAllowanceToMint));  
```

- Verify that the leaf belongs to the merkle root by calling the function `verifyProof`from the library `Merke` If the leaf is in the merkle root and return the result in the variable `newVerified`

```solidity
bool newVerified= m.verifyProof(merkleRoot,proof,leaf );
```



- returns the result

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import {Merkle} from "murky/src/Merkle.sol";

contract Whitelist {

	Merkle m = new Merkle();   
    bytes32 public merkleRoot;
    
    constructor(bytes32 _merkleRoot) {
        merkleRoot = _merkleRoot;
    }

    function checkInWhitelist(bytes32[] calldata proof, uint64 maxAllowanceToMint) view public returns (bool) {
        
        bytes32 leaf = keccak256(abi.encodePacked(msg.sender, maxAllowanceToMint));     
		bool newVerified= m.verifyProof(merkleRoot,proof,leaf );
        return newVerified;
    }
```

## Edge case

As already briefly discussed above, Bitcoin and similar cryptocurrencies make use of Merkle trees to summarize and validate the transactions in a block, and embed the Merkle root into their block header as a summary of it all. The following figure illustrates this:

Each block has an ID value, which is the hash of its header fields. A part of this is the Merkle root. Another part is the previous block ID (*Parent* in above figure). By linking with the previous block ID, and including that as part of the next block ID, the blocks form a blockchain. By embedding the Merkle root in it, they make an immutable record of transactions in the block.

### Handling An Unbalanced Merkle Tree

https://medium.com/coinmonks/merkle-trees-concepts-and-use-cases-5da873702318

The above example illustrates the very basic case of a Merkle tree. It is a convenient example, as at every level there are just the right number of nodes to form exact pairs. What happens if you have an uneven (odd) number of leaf (data) nodes? For example, what happens to the above example if you have 5 Data nodes? You can hash Data1+Data2 together to form a Merkle branch, and same for Data3+Data4. But Data 5 is left without a pair to hash into a new branch.

Different approaches can be taken to address this. For example, in this situation Bitcoin simply copies the un-pairable (odd) hash, and uses the duplicate as a pair (the [odd hash is paired with itself](https://bitcoin.stackexchange.com/questions/37223/pairing-pattern-of-txids-in-merkle-tree)). The following figure illustrates this:

## Monero

From https://medium.com/coinmonks/merkle-trees-concepts-and-use-cases-5da873702318

The Monero approach could be described as converting the hash tree to a [perfect binary tree](https://cs.stackexchange.com/questions/32397/is-there-a-difference-between-perfect-full-and-complete-tree). It hashes enough leaf nodes in the first iteration, so that the following iterations will always have some variant of 2ˣ (a power of 2)

## FAQ

From [learnweb3dao - aidrop](https://learnweb3.io/lessons/how-to-create-merkle-trees-for-airdrops/)

>  What kind of data structure is a Merkle Tree?

A tree

> How is each leaf node labeled in Merkle Tree?

Cryptographic hash of the data block

>  How is each non-leaf node labeled in Merkle Tree?

Cryptographic hash of its child nodes' values

------

### Conclusion

Merkle trees are a foundational cryptographic structure that provides a highly efficient and secure method for verifying data integrity. By allowing large datasets to be represented in compact forms, Merkle trees are indispensable in areas like blockchain technology, distributed systems, secure communications, and cryptographic protocols. Whether for ensuring blockchain transactions' integrity or verifying the consistency of distributed files, Merkle trees continue to play a crucial role in modern digital security. As data grows more complex and decentralized, the importance of Merkle trees will likely continue to expand, shaping the future of secure data verification.



https://proto.school/merkle-dags/07

## Reference

- ChatGPT with the following input "Write an article about Merkle tree, and in what contexts they are used"



a node can have several parents.

### Further reading

https://medium.com/codex/power-of-merkle-trees-1e44819e9639

https://filebase.com/blog/ipfs-directed-acyclic-graphs-explained/

https://medium.com/@Spazzy757/merkle-dag-simplified-eaece84c4090

https://news.ycombinator.com/item?id=37783137

https://hector.link/presentations/merkle-crdts/merkle-crdts.pdf

https://proto.school/merkle-dags/05

https://ovanwijk.medium.com/proof-of-ipfs-content-e43d1698cba2

https://research.protocol.ai/publications/merkle-crdts-merkle-dags-meet-crdts/psaras2020.pdf
