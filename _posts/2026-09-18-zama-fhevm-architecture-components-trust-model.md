---
layout: post
title: "Zama FHEVM Architecture — Components, Data Flow and What Has to Be Trusted"
date:   2026-09-18
lang: en
locale: en-GB
categories: blockchain cryptography security
tags: zama fhe fhevm mpc privacy security confidential-smart-contract
description: "How the Zama Confidential Blockchain Protocol splits work between host contracts, coprocessors, a Gateway rollup and a threshold KMS, and which of them you trust."
image: /assets/article/blockchain/zamafhe/2026-09-18-zama-fhevm-architecture-mindmap.png
isMath: false
---

[Zama](https://www.zama.ai/) builds the Confidential Blockchain Protocol, a way to run smart contracts on encrypted data on an ordinary EVM chain. Its core technology, FHEVM, lets a Solidity contract add, compare and select over ciphertexts with Fully Homomorphic Encryption (FHE), while the chain itself never learns the plaintext. The property this article depends on is that the chain does not run the FHE either: the expensive work is done off-chain by a set of operators, and the chain only records what should be computed and who may read the result.

That split raises the questions a security-minded reader asks first. Which component holds which key? When a contract calls `FHE.add`, what exactly happens on-chain, and what happens elsewhere? If the computation runs off-chain, how does anyone know it was performed, and performed correctly? And when a value is finally decrypted, who had to be honest for the plaintext to be right and for nobody else to have seen it?

This article answers those questions from the protocol documentation and the `zama-ai/fhevm` repository. It walks through the six components, follows one encrypted value from a user's browser to a decrypted result, and ends with a trust table: for each component, what it can do if it misbehaves, and what stops it. [An earlier article]({{site.url_complet}}/2026/07/24/zero-knowledge-proofs-zama-protocol/) covered the zero-knowledge proof attached to encrypted inputs; this one takes the rest of the system.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Two ideas that make FHE fit on a blockchain

FHE operations cost milliseconds to seconds each and need dedicated hardware to run at any scale. No L1 or L2 can execute them inside its state transition function without slowing every other transaction down. The protocol avoids the problem with two design decisions stated in the [litepaper](https://docs.zama.org/protocol/zama-protocol-litepaper).

**Symbolic execution.** When a contract calls the FHEVM library, the host chain does not compute anything. It derives a 32-byte pointer to the future result, called a *handle*, checks that the caller was allowed to use the inputs, and emits an event describing the operation. A network of *coprocessors* reads those events and performs the real FHE computation off-chain. Because handles are just pointers, operations chain without waiting for the previous one to finish, and independent operations run in parallel. The only time the protocol has to wait for a ciphertext to exist is when someone asks to decrypt it.

**Threshold decryption.** For contracts to compose, every ciphertext in the system is encrypted under one global public key. The matching private key is therefore the single most sensitive object in the protocol, and it is never held by one party: it is secret-shared across a set of MPC nodes, the *Key Management Service*, which decrypts only on request and only when the on-chain access list allows it.

Everything else in the architecture exists to connect those two ideas: to get a user's encrypted input into the system safely, to make the coprocessors' work checkable, and to move a decryption request from a contract to the KMS and the plaintext back.

## The six components

![The six components of the Zama protocol: host contracts and the FHEVM library on the host chain, coprocessors and KMS off-chain, the Gateway rollup between them, and the relayer and oracle at the edge]({{site.url_complet}}/assets/article/blockchain/zamafhe/zama-fhevm-components-concept.png)

### FHEVM Solidity library

The library is what a developer sees. It defines four groups of things:

- **Encrypted types**: `ebool`, `euint8` to `euint256`, `eaddress`, and their `external*` input variants.
- **Operations**: `add`, `sub`, `mul`, comparisons, bitwise operators, `select` for branching without revealing the branch, and `rand*` for encrypted randomness.
- **Input handling**: `FHE.fromExternal`, which turns an attested external input into a usable handle.
- **Access control**: `allow`, `allowTransient`, `allowThis`, `makePubliclyDecryptable` and `isSenderAllowed`.

Every encrypted type is a `bytes32` handle underneath; the library forwards each call to the host contracts.

### Host contracts

The host contracts are deployed once per supported chain and are the only trusted on-chain component. In the repository they are `FHEVMExecutor`, `ACL`, `InputVerifier`, `KMSVerifier`, `HCULimit`, `KMSGeneration` and `ProtocolConfig`. Three of them carry the security logic:

- **`FHEVMExecutor`** implements symbolic execution. For a binary operation it checks that `msg.sender` is allowed on both input handles, checks the types match, derives the result handle, grants the caller transient access to it, and emits the operation event. It also enforces a per-transaction budget of *Homomorphic Complexity Units* through `HCULimit`, so that a transaction cannot queue unbounded off-chain work.
- **`ACL`** is the authority on who may use or decrypt a handle. It stores persistent grants, transient grants (in transient storage, per [EIP-1153](https://eips.ethereum.org/EIPS/eip-1153)), and the list of handles marked publicly decryptable. Every grant emits an event, which the coprocessors relay to the Gateway.
- **`InputVerifier`** and **`KMSVerifier`** are the two doors through which off-chain attestations enter the chain. The first accepts a user's encrypted input only with a threshold of coprocessor signatures over it; the second accepts a public decryption result only with a threshold of KMS signatures. Both are [EIP-712](https://eips.ethereum.org/EIPS/eip-712) verifications against a signer set the protocol configures.

### Coprocessors

A coprocessor is an off-chain service written in Rust on top of TFHE-rs. Each one runs its own host-chain node and has five jobs:

- **Compute.** Listen to the executor's events, fetch the input ciphertexts, evaluate the operation with the *evaluation key*, which computes on ciphertexts but cannot decrypt them, and store the result under the handle the chain already derived.
- **Verify inputs.** Check the zero-knowledge proof on user inputs and sign the resulting handles.
- **Replicate the ACL.** Forward the host chain's `Allowed` events to the Gateway.
- **Commit.** Publish a digest of every ciphertext they produce, so that results can be compared.
- **Prepare decryptions.** Normalise a ciphertext with a "switch-and-squash" step before handing it to the KMS.

Several coprocessors run the same work independently. At genesis the operators are Artifact, Blockscape, Luganodes, P2P and Zama.

### Gateway

The Gateway is a dedicated [Arbitrum](https://arbitrum.io/) rollup that runs only the protocol's own contracts; third parties cannot deploy on it. Its contracts are the meeting point of the off-chain operators:

- **`InputVerification`** collects coprocessor signatures on new inputs.
- **`CiphertextCommits`** collects their commitments to computed ciphertexts and records when a majority agree.
- **`Decryption`** receives decryption requests and collects KMS responses.
- **`KMSGeneration`** orchestrates key generation and rotation.
- **`GatewayConfig`** and **`ProtocolPayment`** hold the operator registry, the thresholds and the fee logic.

The Gateway also bridges handles between host chains. It performs no cryptography of its own.

### Key Management Service

The KMS is a network of thirteen MPC nodes run by independent organisations. At genesis they are Conduit, DFNS, Etherscan, Figment, Fireblocks, InfStones, LayerZero, Ledger, Omakase, OpenZeppelin, Stake Capital, Unit 410 and Zama. Together they generate the global FHE key pair so that no node ever holds the private key, they decrypt on request with a threshold protocol, and they generate the common reference string used by the input proofs.

Each node runs inside an AWS Nitro Enclave, and the key lifecycle follows [NIST SP 800-57](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final), with rotation done by FHE key switching so that existing ciphertexts stay usable. The KMS is orchestrated by the Gateway and signs every result it returns.

### Relayer and oracle

Two lightweight services sit at the edge. The *relayer* is an HTTP endpoint that lets a browser or a mobile app register an encrypted input and request a user decryption without sending transactions to the Gateway itself. The *oracle* watches for on-chain public decryption requests, waits for the signed KMS result, and calls the requesting contract back with it. Neither is trusted: a user can run their own relayer or talk to the Gateway directly, and a contract verifies the oracle's callback against the KMS signatures.

## Three keys, three locations

The protocol's security rests on keeping three keys apart.

| Key | Where it lives | What it can do |
|---|---|---|
| **Public key** | Published; loaded by the relayer SDK in the user's client | Encrypt a plaintext into a ciphertext usable by any contract on any supported chain |
| **Evaluation key** | On every coprocessor | Compute on ciphertexts (add, compare, select) without decrypting them |
| **Private key** | Nowhere in full; secret-shared across the 13 KMS nodes | Decrypt, but only when a threshold of nodes runs the protocol together |

A coprocessor therefore sees every ciphertext in the system and can compute on all of them, but cannot read any. A KMS node can take part in a decryption but cannot decrypt alone, and never sees a ciphertext it was not asked to decrypt. The user's device is the only place where a plaintext and its ciphertext coexist, at encryption time and, for user decryption, at the end.

## The life of an encrypted value

![Sequence of one encrypted value through the protocol: client-side encryption and proof, coprocessor attestation, on-chain input verification, symbolic execution, off-chain computation and commitment, ACL grant, and public or user decryption through the Gateway and KMS]({{site.url_complet}}/assets/article/blockchain/zamafhe/zama-fhevm-encrypt-compute-decrypt-sequence.png)

### Step 1: encryption and proof on the user's device

The client library encrypts the plaintext under the public key and produces a zero-knowledge proof of knowledge (ZKPoK) that the ciphertext is well-formed and that the user knows what is inside. Several values for one transaction are packed into a single ciphertext list with one proof. The proof is bound to the target contract address and to the user's address, which is why it cannot be replayed by someone else or against another contract.

### Step 2: attestation by the coprocessors

The ciphertext and proof go to the Gateway (usually through the relayer). Each coprocessor verifies the proof, unpacks the ciphertexts, stores them, derives their handles, and signs the list of handles together with the user address, the contract address and the chain identifier. `InputVerification` on the Gateway collects the signatures. What comes back to the client as the `inputProof` is not the zero-knowledge proof: it is the list of handles plus the coprocessor signatures, a compact attestation that the chain can check with `ecrecover`.

### Step 3: input verification on the host chain

The contract calls `FHE.fromExternal(handle, inputProof)`, which reaches `InputVerifier.verifyInput`. The contract checks that the chain identifier encoded in the handle matches `block.chainid`, that the handle version is current, that the handle passed is one of the handles listed in the proof, and that at least `threshold` distinct registered coprocessors signed the EIP-712 structure `(handles, userAddress, contractAddress, chainId)`. On success the proof is cached for the rest of the transaction and the contract receives a usable `euint64`.

### Step 4: symbolic execution

Now the contract computes. Each `FHE.add(a, b)` becomes a call to `FHEVMExecutor.fheAdd`. The executor checks that the calling contract is allowed on `a` and `b`, then derives the result handle as

```text
prehandle = keccak256(DOMAIN_SEPARATOR, op, lhs, rhs, scalarFlag, ACL, chainid,
                      blockhash(block.number - 1), block.timestamp)
handle    = prehandle[0:21] || 0xff || chainid (8 bytes) || type (1 byte) || version (1 byte)
```

The inclusion of the previous block hash and the timestamp makes the handle unique per block, so the same operation on the same inputs in two blocks produces two handles. The executor grants the caller transient access to the new handle, charges HCU, and emits the event. The contract then typically stores the handle and calls `FHE.allow` to give the holder persistent access, which the ACL records and announces.

### Step 5: computation and commitment off-chain

Every coprocessor sees the event, evaluates the operation, and stores the resulting ciphertext under the handle. Because TFHE operations are deterministic on given input ciphertexts, honest coprocessors produce bit-identical results. When the ACL emits an `Allowed` event for a handle, each coprocessor submits a digest of the corresponding ciphertext to `CiphertextCommits` on the Gateway; the contract counts confirmations per digest and marks the material as *added* once the count reaches the coprocessor majority threshold set in `GatewayConfig`. A coprocessor that computed something different is simply outvoted, and its divergent digest is on the record.

### Step 6: decryption

Two paths exist. Both start with the Gateway refusing any request for a handle whose ciphertext material has not reached consensus, and both end with a result signed by the KMS.

- **Public decryption** is used when a contract needs the plaintext. The contract marks the handle publicly decryptable, a request goes to `Decryption` on the Gateway, the KMS nodes fetch the ciphertext, run the threshold protocol, and each signs the plaintext. Once the public decryption threshold of responses is reached, the oracle posts the plaintext to the contract, which verifies the signatures through `KMSVerifier`.
- **User decryption** is used when only one person should see the value. The user generates an ephemeral key pair, signs its public key with their wallet (EIP-712), and submits the handle, the contract address and the signature. The KMS checks the ACL entry for that user and that contract, decrypts, and re-encrypts the plaintext under the user's ephemeral key. The user decrypts locally; the plaintext never touches a chain, a relayer or the Gateway.

## Access control is the hinge

The ACL is what turns "anyone can compute on any ciphertext" into a usable confidentiality model. Three kinds of entry exist.

| Grant | Function | Lifetime | Typical use |
|---|---|---|---|
| Persistent | `FHE.allow(handle, account)`, `FHE.allowThis(handle)` | Forever | A token gives a holder the right to read their new balance |
| Transient | `FHE.allowTransient(handle, account)` | Current transaction | The executor grants the caller its own result; a contract passes a handle to another contract in the same call |
| Public decryption | `FHE.makePubliclyDecryptable(handle)` | Forever | A sealed-bid auction reveals the winning bid |

Three properties follow from the implementation:

- **Checked at use as well as at read.** A contract cannot run `FHE.add` on a handle it was not allowed on, so it cannot compute on another contract's private state by guessing the handle.
- **Never revoked.** A party that once had access to a handle keeps it. Since every operation produces a new handle, confidentiality after a revocation is achieved by not granting the next handle.
- **Replicated.** Coprocessors relay every `Allowed` event to the Gateway, and the KMS consults that replica before decrypting.

The host chain's ACL is authoritative, but the enforcement at decryption time happens off-chain, in the KMS, against the copy.

## What has to be trusted

![Trust boundaries of the Zama protocol: on-chain host contracts as the authoritative but upgradeable base, coprocessors under an honest-majority and staking assumption, the Gateway trusted only for liveness, the KMS under a two-thirds threshold inside Nitro Enclaves, and untrusted relayer and oracle]({{site.url_complet}}/assets/article/blockchain/zamafhe/zama-fhevm-trust-model-concept.png)

The protocol is not trustless; it is trust-distributed, with a different assumption for each component. The table states, for each one, what a misbehaving instance could achieve and what the protocol does about it.

| Component | Assumption | If it misbehaves | What limits the damage |
|---|---|---|---|
| **Host contracts** | Correct code; the owner's upgrade and configuration keys are honest | A malicious upgrade could change the ACL, the signer sets or the thresholds | On-chain, auditable, upgrades are visible; the audits by Trail of Bits and Zenith cover them |
| **Coprocessors** | More than half of them are honest | A minority can only produce a divergent digest that loses the vote; a colluding majority could attest a wrong ciphertext and nobody would detect it from the chain | Redundant execution with commitment consensus on the Gateway; anyone can recompute an operation and compare; operators stake ZAMA and can be slashed through governance; operators are public, named organisations |
| **Gateway** | None for confidentiality or correctness; availability only | Can delay or drop input attestations and decryption requests | Cannot read, forge or alter a value: every input is signed by coprocessors and every plaintext by the KMS; the rollup is replaceable |
| **KMS** | At most one third of the 13 nodes are malicious | Below the threshold, nothing; above it, the private key could be reconstructed and every ciphertext in the system read | Threshold MPC with a 2/3 rule and robust output delivery; each node's share lives inside a Nitro Enclave the operator cannot open; enclave attestation of the software version; custodial backup shares held by separate parties |
| **Relayer and oracle** | None | Can delay a request or refuse to serve it | Results are signed by the KMS and verified by the recipient; anyone can run a replacement |
| **User's device** | The client library and the environment are honest | A compromised client sees the user's own plaintexts | Nothing in the protocol protects against it; it is outside the trust boundary |
| **The FHE scheme** | TFHE with 128-bit security and a failure probability of 2^-128 per operation | A cryptanalytic break would read every ciphertext | The scheme is lattice-based and considered post-quantum; the proof system on inputs is not, which is the one non-post-quantum piece |

Two consequences follow from this table.

**Correctness of a computation is attested, not proven.** There is no cryptographic proof that a coprocessor evaluated `FHE.add` correctly. What exists instead is three weaker mechanisms:

- **Redundancy**: several operators compute the same thing.
- **Agreement**: the Gateway accepts a ciphertext only once a majority commit to the same digest.
- **Accountability**: a divergent commitment is a public, signed record that can be slashed.

The litepaper compares this to optimistic-rollup security: anyone can recompute and challenge. The chain, for its part, fixes exactly *what* must be computed, since the handle derivation binds the operation, the inputs and the block, so the argument is only about the ciphertext content, never about which operation was requested. The stated long-term direction is ZK-FHE, where a proof of correct evaluation would replace the majority assumption.

**Confidentiality rests on the KMS, and the KMS rests on two things.** The threshold protocol guarantees that fewer than one third of nodes learn nothing, by mathematics. Above that, the second line of defence is hardware: each share sits in a Nitro Enclave, so extracting it requires the operator and the cloud provider to cooperate. The litepaper states that this makes verifiability of the MPC depend on hardware assumptions, and names ZK-MPC as the planned replacement. Until then, the confidentiality claim is "a colluding two-thirds of thirteen named organisations, or a break of the enclave model".

## How a user can tell the computation happened

The question comes up as soon as one understands symbolic execution: the transaction succeeded, the handle is stored, but did anyone compute the ciphertext? The protocol offers no on-chain flag for it, and the host chain never waits. Three observations answer it in practice.

- **The on-chain state is final regardless.** The handle, the events and the ACL are written when the transaction is mined. A contract's logic does not depend on the coprocessors' progress; only the readability of the result does.
- **Decryption is the observable.** The Gateway will not process a decryption request for a handle whose ciphertext material has not reached commitment consensus, and the KMS only signs a plaintext it has decrypted. A signed decryption result is therefore evidence that a majority of coprocessors computed and agreed on the ciphertext. If they have not, the request stays pending; it never returns an invented value.
- **Anyone can recompute.** Ciphertexts are stored in public storage and the evaluation key is public. A third party can fetch the inputs, evaluate the operation and compare the digest with the one the coprocessors committed. This is the mechanism a slashing proposal would rely on.

So the answer for an application is: treat an undecryptable handle as "not yet computed", and treat a KMS-signed plaintext as "computed and majority-attested". Nothing stronger is available today.

## Conclusion

The Zama protocol keeps FHE off the host chain and replaces it with two on-chain primitives, a handle and an access list, plus a set of off-chain operators whose outputs are signed and checked at the chain boundary.

- **Symbolic execution** puts the description of the computation on-chain, bound to the operation, the inputs and the block, and leaves the evaluation to coprocessors.
- **Three keys in three places** separate encryption (public, client-side), computation (evaluation key, coprocessors) and decryption (private key, secret-shared in the KMS).
- **Two verifiers guard the chain boundary**: `InputVerifier` admits an input only with a threshold of coprocessor signatures, `KMSVerifier` admits a plaintext only with a threshold of KMS signatures.
- **The ACL is checked at use and at read**, is never revoked, and is replicated to the Gateway for the KMS to enforce.
- **Correctness is attested by majority**, not proven: redundant execution, commitment consensus and slashing, with ZK-FHE as the announced replacement.
- **Confidentiality is a 2/3-of-13 threshold plus enclaves**, with ZK-MPC as the announced replacement for the hardware assumption.
- **The Gateway, relayer and oracle are trusted for liveness only.**

![Mindmap of the Zama FHEVM architecture covering the two design ideas, the six components, the three keys, the life of a value, access control and the trust model]({{site.url_complet}}/assets/article/blockchain/zamafhe/2026-09-18-zama-fhevm-architecture-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Handle** | A 32-byte on-chain pointer to a ciphertext stored off-chain, derived deterministically by the executor from the operation, its inputs and the block, with the chain id, type and version encoded in its last bytes. |
| **Symbolic execution** | The execution model in which the host chain derives handles and emits operation events instead of computing on ciphertexts. |
| **Coprocessor** | An off-chain operator that verifies input proofs, evaluates FHE operations with the evaluation key, stores ciphertexts and commits to their digests. |
| **Gateway** | A dedicated Arbitrum rollup holding the protocol's coordination contracts for input attestation, ciphertext commitments, decryption requests and operator configuration. |
| **KMS** | The Key Management Service, thirteen MPC nodes that hold shares of the global FHE private key and decrypt only under a threshold protocol. |
| **ACL** | The on-chain Access Control List recording which addresses may use or decrypt a handle, replicated to the Gateway and consulted by the KMS. |
| **ZKPoK** | The zero-knowledge proof of knowledge attached to an encrypted input, proving it is well-formed and bound to a user and a contract. |
| **inputProof** | The calldata attestation produced after the coprocessors verified an input: the list of handles plus their EIP-712 signatures, verified on-chain by `InputVerifier`. |
| **Ciphertext commitment** | A digest of a computed ciphertext submitted by each coprocessor to the Gateway; a handle becomes decryptable once a majority commit to the same digest. |
| **HCU** | Homomorphic Complexity Unit, the per-transaction budget the executor charges for symbolic operations to bound the off-chain work a transaction can queue. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A contract can only compute on handles it has been allowed on. | `FHEVMExecutor` checks `ACL.isAllowed(handle, msg.sender)` on every input before deriving a result. | The ACL contract is upgraded to a permissive version, or its owner grants access out of band. |
| An encrypted input is accepted only if a threshold of registered coprocessors signed it for this user, this contract and this chain. | `InputVerifier.verifyInput` recovers EIP-712 signatures and counts distinct registered signers against the threshold. | The signer set or the threshold is reconfigured by the contract owner, or the coprocessors' signing keys are compromised. |
| A plaintext reaches a contract only with a threshold of KMS signatures over it. | `KMSVerifier.verifyDecryptionEIP712KMSSignatures`, called by the contract's callback. | The KMS signer set is reconfigured, or more than the threshold of KMS nodes collude. |
| A handle is decryptable only after a majority of coprocessors committed to the same ciphertext digest. | `Decryption` on the Gateway checks `CiphertextCommits.isCiphertextMaterialAdded` before accepting a request. | The coprocessor majority threshold is lowered, or a majority of coprocessors collude on a wrong digest. |
| The private key is never reconstructed in one place. | Threshold key generation and threshold decryption in the KMS; shares confined to Nitro Enclaves. | More than one third of the nodes collude, or the enclave isolation fails. |
| A handle from one chain is not usable on another. | The chain id is encoded in the handle and checked by `InputVerifier`; bridging goes through the Gateway with new handles. | The chain id check is removed or a bridged handle is attested without the ACL check on the source chain. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| A successful transaction does not mean the ciphertext exists yet; the coprocessors compute asynchronously. | Never assume a fresh handle is decryptable in the same block; poll the decryption readiness or design for asynchronous reveals. |
| Every FHE operation returns a new handle, and access granted on the old one does not carry over. | Re-grant access after each state update, as OpenZeppelin's ERC-7984 does in `_update`; observers must be re-allowed on every new balance handle. |
| ACL grants cannot be revoked, and public decryption is irreversible for that handle. | Treat `FHE.allow` and `makePubliclyDecryptable` as permanent disclosures; revoke by not granting the next handle. |
| A comparison result is itself encrypted, so a contract cannot `require` on it. | Use `FHE.select` to branch without revealing the condition; accept that an "insufficient balance" becomes a transfer of zero rather than a revert. |
| The `inputProof` is bound to `(user, contract, chain)` and cached per transaction. | Generate the input with the exact contract address and sender that will submit it; one proof cannot serve two contracts. |
| Symbolic operations consume HCU, with a global and a sequential-depth limit per transaction. | Keep dependency chains short and prefer scalar operands where possible; a transaction over the limit reverts on-chain before any off-chain work. |
| The KMS checks the ACL replica, not the host chain, at decryption time. | Expect a short delay between an `allow` on the host chain and the ability to decrypt, while the coprocessors relay the event to the Gateway. |

## Frequently Asked Questions

**Q: What does the host chain execute when a contract calls `FHE.add`?**

Nothing homomorphic. `FHEVMExecutor.fheAdd` checks that the caller is allowed on both input handles, checks their types agree, derives the result handle by hashing the operation, the inputs, the ACL address, the chain id, the previous block hash and the timestamp, grants the caller transient access to that handle, charges HCU, and emits an event. The addition itself is performed later by every coprocessor that reads the event.

**Q: Why does the `inputProof` in calldata contain signatures rather than the zero-knowledge proof?**

Because verifying the proof on-chain would be far too expensive. The proof is verified off-chain by each coprocessor; what the chain receives is their EIP-712 signatures over the resulting handles, the user address, the contract address and the chain id. `InputVerifier` recovers the signers and requires a threshold of distinct registered coprocessors. The zero-knowledge proof protects the coprocessors from malformed ciphertexts; the signatures protect the chain from unverified ones.

**Q: Which component would have to be compromised to read every balance in a confidential token?**

The KMS, and specifically more than one third of its thirteen nodes, since the threshold protocol reconstructs nothing below that. The other components do not hold what is needed:

- A compromised **coprocessor** holds every ciphertext but only the evaluation key, so it can compute but not read.
- A compromised **Gateway** can delay requests but sees no plaintext.
- A compromised **relayer or oracle** handles only signed or re-encrypted data.

The other way in is the FHE scheme itself, which is a cryptanalytic question rather than an operational one.

**Q: If the coprocessors never computed a value, what does the user observe?**

The transaction that produced the handle succeeds normally, because the chain never waits. When the user asks to decrypt the handle, the Gateway checks whether a majority of coprocessors committed to the ciphertext material; if not, the request is not processed and stays pending. The user therefore sees a handle they cannot decrypt, never a wrong plaintext. A signed decryption result is the evidence that the computation was performed and agreed on.

**Q: How do the three grant types differ, and why can none of them be revoked?**

A persistent grant lasts forever, a transient grant lasts for the current transaction and lives in transient storage, and a public-decryption grant makes the handle readable by anyone through the KMS.

None is revocable because the grant is an event that has already been replicated to the Gateway and acted on. The protocol's answer to revocation is that every operation creates a new handle, and a party that should no longer read is simply not granted the next one. A confidential token therefore re-grants the holder and its observers on every `_update`.

**Q: Combine the trust table with the decryption flow: which parties must be honest for a user decryption to be both correct and private?**

Two sets of parties, one per property:

- **Correctness**: a majority of coprocessors, so that the ciphertext being decrypted is the right one, and a threshold of KMS nodes, so that the signed plaintext is the true decryption.
- **Privacy**: at most one third of KMS nodes malicious, so that no one reconstructs the key, plus the user's own device, which decrypts the re-encrypted result.

The Gateway and the relayer can be entirely malicious and only delay the request. The host contracts must be the audited code, since a malicious ACL could have granted the handle to someone else.

**Q: What does "publicly verifiable" mean for a coprocessor, given that there is no proof of correct FHE evaluation?**

It means that the inputs, the operation and the outputs are all available: ciphertexts sit in public storage, the operation is described in an on-chain event, the evaluation key is public, and each coprocessor's commitment to its result is recorded on the Gateway. Anyone can re-run the operation and compare digests.

Verifiability here is the ability to detect and prove misbehaviour after the fact, which is what slashing needs, not a proof that accompanies each result. The protocol names ZK-FHE as the way to turn the former into the latter.

## References

### Analyzed source

- [zama-ai/fhevm](https://github.com/zama-ai/fhevm) — analyzed at commit [`c2d1a202aa5fea04c34ba62780b1a1e33a307f00`](https://github.com/zama-ai/fhevm/tree/c2d1a202aa5fea04c34ba62780b1a1e33a307f00) (12 commits after tag `v0.13.0-0`; host contracts `FHEVMExecutor` at version 0.4.0), 2026-09-18

### Protocol documentation

- [Zama Confidential Blockchain Protocol Litepaper](https://docs.zama.org/protocol/zama-protocol-litepaper)
- [FHE on Blockchain — architecture overview](https://docs.zama.org/protocol/protocol/overview)
- [Host contracts](https://docs.zama.org/protocol/protocol/overview/hostchain)
- [Coprocessor](https://docs.zama.org/protocol/protocol/overview/coprocessor)
- [Gateway](https://docs.zama.org/protocol/protocol/overview/gateway)
- [Key Management Service](https://docs.zama.org/protocol/protocol/overview/kms)
- [Relayer and Oracle](https://docs.zama.org/protocol/protocol/overview/relayer_oracle)
- [Access Control List](https://docs.zama.org/protocol/solidity-guides/smart-contract/acl)
- [Solidity guides (types, operations, inputs, decryption, HCU)](https://docs.zama.org/protocol/solidity-guides)
- [Relayer SDK guides](https://docs.zama.org/protocol/relayer-sdk-guides)

### Standards and libraries

- [EIP-712 — Typed structured data hashing and signing](https://eips.ethereum.org/EIPS/eip-712)
- [EIP-1153 — Transient storage opcodes](https://eips.ethereum.org/EIPS/eip-1153)
- [NIST SP 800-57 Part 1 Rev. 5 — Recommendation for Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [TFHE-rs](https://docs.zama.ai/tfhe-rs)
- [OpenZeppelin Confidential Contracts (ERC-7984)](https://docs.openzeppelin.com/confidential-contracts/erc7984)
- [AWS Nitro Enclaves](https://aws.amazon.com/ec2/nitro/nitro-enclaves/)

### Related articles

- [The Zama FHEVM Whitepaper — What It Specifies, and What the Code Does Differently]({{site.url_complet}}/2026/09/18/zama-fhevm-whitepaper-vs-implementation/)
- [Zero-Knowledge Proofs in the Zama Protocol — What They Prove and Where They Are Verified]({{site.url_complet}}/2026/07/24/zero-knowledge-proofs-zama-protocol/)
- [Technical Analysis of the OpenZeppelin ERC-7984 Implementation]({{site.url_complet}}/2026/02/24/erc7984-openzeppelin-analysis/)
- [Overview, security and applications of Multi-Party Computation (MPC)]({{site.url_complet}}/2024/10/21/mpc-protocol-overview/)
- [AWS Nitro Enclaves: Secure and Isolated Compute for Sensitive Data]({{site.url_complet}}/2025/07/17/aws-nitro-enclaves-overview/)
- [Introduction to Arbitrum, an Optimistic rollup protocol]({{site.url_complet}}/2024/01/31/arbitrum-introduction/)

### Tooling

- [Claude Code](https://claude.com/product/claude-code)
