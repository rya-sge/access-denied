---
layout: post
title: "The Zama FHEVM Whitepaper — What It Specifies, and What the Code Does Differently"
date:   2026-09-18
lang: en
locale: en-GB
categories: blockchain cryptography security
tags: zama fhe fhevm mpc zkpok privacy confidential-smart-contract
description: "A reading of the Zama fhevm whitepaper (v3.1, June 2025) against the zama-ai/fhevm repository, with the changes the implementation has made since the paper was written."
image: /assets/article/blockchain/zamafhe/2026-09-18-zama-fhevm-whitepaper-mindmap.png
isMath: true
---

[Zama](https://www.zama.ai/) publishes a whitepaper for fhevm, its protocol for confidential smart contracts on existing blockchains. The paper describes a system where contracts compute on encrypted values with Fully Homomorphic Encryption (FHE), a set of off-chain coprocessors does the actual arithmetic, and a threshold network holds the decryption key. Version 3.1 of the paper is dated 30 June 2025. The code it describes has kept moving: the repository it points to, `zama-ai/fhevm`, is more than a year further along at the revision read for this article.

That gap is the subject here. The first part restates what the whitepaper specifies, section by section, in enough detail that a reader can use it as the reference it is meant to be: the four design principles, the components and their trust assumptions, the Solidity library, the KMS, the Gateway contracts, the input, commitment and decryption procedures, and the numbers the paper reports. The second part compares each of those with the repository at commit `ac6ff45`, and lists what was removed, renamed, restricted or added, with the commit that made the change where it could be found.

[An earlier article]({{site.url_complet}}/2026/09/18/zama-fhevm-architecture-components-trust-model/) described the architecture as the current code implements it, and [another one]({{site.url_complet}}/2026/07/24/zero-knowledge-proofs-zama-protocol/) the zero-knowledge proof on encrypted inputs. This one is about the document, and about the distance between the document and the deployment.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Part 1 — What the whitepaper specifies

### Four principles and a positioning

The paper opens by naming the property it refuses to give up: a blockchain needs transparency for its validators to agree on state, and that transparency is what makes every balance and every amount public. The protocol's answer has to satisfy four principles at once:

- no negative impact on the security of the underlying blockchain;
- exact and correct results, with everything publicly verifiable;
- confidential contracts written in existing languages and tools, Solidity first;
- full composability between confidential contracts, and support for data from multiple users without loss of confidentiality.

The related-work section is a defence of FHE against the three other ways of computing on private data, summarised in a table the paper labels 1.1:

| | TEE | MPC | ZK | FHE |
|---|---|---|---|---|
| Security | limited | high | high | high |
| Composable | yes | yes | no | yes |
| Verifiable | yes | no | yes | yes |
| Performance (CPU) | high | medium | medium | medium |
| Performance (ASIC) | - | - | high | high |

The argument for each column is short:

- **Zero-knowledge proofs** need the prover to know the plaintext, so multi-user computation forces the data through some party in clear; the paper cites Zerocash, Zexe and Hawk as examples of that limit.
- **Trusted execution environments** depend on the enclave holding the decryption key and have a long side-channel record; the paper lists Spectre, Foreshadow, CacheOut and SGX.fail among others, and keeps enclaves as defence in depth rather than as the security base.
- **MPC** keeps the *state* secret-shared, which makes every change of the party set an expensive resharing of the whole state. fhevm keeps the state as FHE ciphertexts and shares only the key, so resharing touches one key; the paper still uses MPC for that one job.
- **Other FHE designs**, Zether, Zkay, smartFHE and PESCA, are named, and the difference claimed is that fhevm moves the computation off-chain and needs no change to the host chain.

### The components and what is trusted

The protocol is defined as a set of components around a *host chain*, any L1 or rollup where the confidential contracts are deployed:

- **Trusted host contracts** on the host chain, in particular an Access Control List (ACL) contract, used behind the scenes by the Solidity library.
- The **Gateway**, a set of contracts that validate encrypted inputs, bridge ciphertexts between host chains and process decryption requests. It keeps a copy of the ACLs of all connected host chains, enforces consensus among coprocessors and orchestrates the KMS. The paper makes no assumption about where the Gateway is deployed; a footnote says Zama's deployment is an Arbitrum Orbit rollup, locked to protocol contracts only, with operators each running a validator.
- The **coprocessors**, off-chain and run by different parties, which verify encrypted inputs, run the FHE computations and store the results, and replicate the ACL to the Gateway. Each commits its results to the Gateway, which enforces a consensus.
- The **KMS**, a key management service for FHE key generation, decryption and CRS generation, instantiated as MPC with, initially, 13 organisations.
- **Oracles**, one or more per host chain, which carry decryption requests from contracts to the Gateway and post the signed plaintext back.
- **Relayers**, which submit encrypted inputs and decryption requests on behalf of users.

The paper's Table 2.1 states the trust assumptions in four lines. Coprocessors: at least one half honest, but publicly verifiable and slashable. KMS: at least two thirds honest. Oracle and relayer: none, since all messages are signed.

### The Solidity library

Section 3 is the developer-facing specification. The encrypted types are listed as `ebool`, unsigned integers `euint8` to `euint256` in steps of 8, signed integers `eint8` to `eint256`, encrypted bytes `ebytes1` to `ebytes32` plus `ebytes64`, `ebytes128` and `ebytes256`, and `eaddress`. All are Solidity user-defined value types over `bytes32`, and the paper is explicit that a value is a *handle* pointing to a ciphertext held by the coprocessors, not the ciphertext itself.

The operators cover the usual families: logical, arithmetic (`add`, `sub`, `mul`, `div`, `rem`, `neg`, `abs`, `sign`), comparison, shifts and rotations, `min` and `max`. Branching is done with `select`, since an encrypted boolean cannot drive an `if` or a `require`; the paper's example zeroes a parameter when a condition is false, and a footnote notes that the output of `select` shares a plaintext with one input but is a fresh ciphertext, so an observer cannot tell which branch was taken.

Three mechanisms complete the library:

- **Encrypted inputs.** A user obtains *external values* and an *attestation* from the Gateway and passes them to the contract, which calls `fromExternal`. The attestation is a list of coprocessor signatures; `fromExternal` verifies them against the registered coprocessors, the user address and the contract address, and returns a handle the contract has transient access to.
- **Access control.** `allow(handle, address)` grants persistent access and emits an `Allowed` event; `allowTransient` grants access for the transaction; `allowForDecryption(handle)` marks a handle publicly decryptable and emits `AllowedForDecryption`; `isAllowed` and `isSenderAllowed` query the list. A contract that calls `allow` without itself having access reverts.
- **Random values.** `randEuint` and `randEuintBounded` produce uniform encrypted values, deterministic across coprocessors, with entropy derived from the secret FHE key.

Decryption is specified in two forms.

**Public decryption** goes through an on-chain oracle. The contract calls `FHE.setDecryptionOracle` once, then `FHE.requestDecryption(cts, callbackSelector)` with a list of handles; the oracle contract implements `IDecryptionOracle`, and the callback verifies the result with `FHE.checkSignatures(requestID, signatures)`.

**User decryption** returns the plaintext to one person. The user signs an [EIP-712](https://eips.ethereum.org/EIPS/eip-712) object that embeds the contract address and the user address, which the paper calls an *authentication token*, so that one signature can serve every handle the application and the user share. The KMS encrypts the result under a classical public key the user supplies; the paper specifies that each KMS party encrypts its *share* of the plaintext, so that no party learns the value. Listing 6 shows the client flow with `generateKeypair`, `createEIP712`, `eth_signTypedData_v4` and `userDecrypt`.

### Implementation details in the paper

**TFHE.** The scheme is TFHE, chosen over BGV, BFV and CKKS because those are used in levelled mode with bounded depth and, for CKKS, approximate results, neither of which suits a token that can be transferred any number of times and must never approve a transfer that should fail. TFHE's programmable bootstrapping evaluates a lookup table homomorphically while resetting noise, which gives exact, unbounded computation. The paper uses TFHE-rs as a black box and reports timings on one AMD EPYC 9R14 (192 cores) and two NVIDIA H100s: for `euint64`, an addition costs 109 ms on CPU and 20 ms on GPU, a multiplication 400 ms and 166 ms, a comparison 99 ms and 22 ms, a `select` 36 ms and 11 ms.

**KMS.** The KMS is $$n$$ MPC parties, $$n = 13$$ in Zama's deployment, each running a connector that listens to the Gateway and one or more cores that execute the MPC. The protocols are robust, maliciously secure with guaranteed output delivery, and tolerate a corruption threshold $$t \lt n/3$$, so $$t = 4$$ for $$n = 13$$. Three properties follow: no secret is stored centrally; the network stays live with a subset of nodes offline; and every operation is a Gateway transaction, so the audit log is the chain. The paper warns that each party must validate the Gateway contracts' execution independently, because a Gateway that emits faulty events could trigger decryptions that should not happen, or even extract the key through *selective failure attacks* on maliciously constructed ciphertexts. Enclaves (AWS Nitro in Zama's deployment) are added so that an operator cannot read, and so cannot sell, its own share.

Key lifecycles follow [NIST SP 800-57](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final): one *conceptual key* per Gateway, made of successive *concrete keys* that move through pre-activation, active, suspended, deactivated, compromised and destroyed. Rotation uses key-switching keys so that ciphertexts under a retired concrete key stay usable. A **custodial backup** covers the case where more than $$t$$ parties lose their shares at once: each party splits its share into $$m$$ pieces encrypted for $$m$$ custodians, who can restore it to the same or a different set of MPC parties on a quorum decision, without ever being able to reconstruct anything themselves.

**Gateway contracts.** Seven are named: `GatewayConfig` (operators, host chains, storage locations), `MultichainACL` (the copy of every host chain's ACL, updated by the coprocessors), `CiphertextCommits` (handle to ciphertext digest), `Bridging`, `KeyManagement`, `InputVerification` and `Decryption`.

**Coprocessor.** A full node per host chain feeds a listener; events become tasks in a database; workers pull tasks whose inputs are ready, compute with TFHE-rs and write results back; a sender posts commitments to the Gateway. Ciphertexts live in a public storage (an S3 bucket in Zama's deployment) registered with the Gateway.

**Handles and symbolic execution.** Listing 7 is the paper's definition of a handle: `keccak256(abi.encodePacked(fheAdd, x, y, ...))`, hashing the operation type, the input handles and the result type. The paper draws the consequence explicitly: handles are "unique, deterministic, and state independent". The host contract also enforces a maximum "FHE gas" per transaction, which bounds the latency between a value being used on-chain and its ciphertext existing.

The paper states the cost of this design plainly: the host chain reaches consensus on the symbolic computation, not on the ciphertexts, so a coprocessor could produce a wrong ciphertext by mistake or on purpose, to save compute, to substitute a decryptable result, or to attempt a selective-failure attack. The mitigation is the public commitment made when processing `Allowed` events: anyone can recompute and compare digests.

**Inputs.** The user encrypts, produces a ZKPoK with the intended user address $$u$$, contract address $$c$$ and host chain id as auxiliary information, and packs several values into one 16 to 20 kB ciphertext holding up to 2048 bits, with one proof for all of them. The Gateway emits a `VerifyProofRequest`; each coprocessor verifies the proof, unpacks the ciphertexts, derives handles by hashing, stores them, and signs the handle list with $$u$$ and $$c$$ embedded. When a majority return identical handles, the Gateway emits the list and the signatures to the user. The scheme is the one of [Libert 2024](https://eprint.iacr.org/2023/800); the benchmark for ten `euint64` values is 1.3 s of proving in a browser (WASM, MacBook Pro M2), 130 ms of verification on the EPYC server, and a 1.8 kB proof.

**Bridging.** A handle on one chain is not usable on another. The Gateway checks, against its ACL copy, that the user had access on the source chain, then coprocessors derive new handles for the destination chain and sign them; the rest is the input flow.

**Commitments and decryption.** On an `Allowed` event, each coprocessor prepares the ciphertext for decryption with a *switch-and-squash* operation that moves it to a larger plaintext domain, stores both forms, and sends the handle with two digests $$d_{req}$$ and $$d_{sns}$$ to the Gateway; on an ACL update it sends the grant. The Gateway waits for majority consensus on both. For **public decryption**, the Gateway validates the calling contract against the ACL and emits an event; each KMS connector downloads the prepared ciphertexts, checks their digests against the consensus, runs the MPC decryption, and posts a signed result; once $$t + 1$$ valid results agree, the oracle calls the contract, which can verify the KMS signatures. For **user decryption**, the request carries the user's classical public key, the user address, the handles, a list of contracts each handle must be allowed for, and the EIP-712 signature; each core returns its *share* encrypted under the user's key; the Gateway waits for $$2t + 1$$ shares and the user reconstructs locally.

### Future work as the paper lists it

Section 5 is a list of admitted gaps:

- **Verifiability of the KMS.** Full public verifiability is missing in one place, the KMS, where a threshold assumption still guarantees correctness of results; enclaves are the interim answer.
- **Verifiable FHE**, which would replace the coprocessors' consensus with proofs and remove substitution and selective-failure risks.
- **Decentralisation**, through proof-of-work-style competition among coprocessors once FHE is verifiable, and through larger or rotating KMS committees.
- **Post-quantum coverage**, complete for FHE and MPC but not for the ZKPoK, for which a post-quantum version is in progress.
- **Performance**: hardware acceleration, faster MPC, a bounded ACL instead of an append-only one, and a layered Gateway per host chain.
- **Features**: MPC threshold signatures in the KMS.

## Part 2 — What the implementation does differently

The repository was read at commit `ac6ff45`, 50 commits after the `v0.14.1` tag, with `FHEVMExecutor` reporting version 0.7.0. The whitepaper's own code listings and section numbers are the baseline. The table gives the summary; each row is discussed below.

![Component-level comparison of the whitepaper and the repository: the oracle and MultichainACL are removed, the KMS reads the host chain ACL directly, and ProtocolPayment, delegation and contexts are added]({{site.url_complet}}/assets/article/blockchain/zamafhe/zama-whitepaper-vs-code-concept.png)

| Area | Whitepaper (v3.1) | Repository (commit `ac6ff45`) | Kind of change |
|---|---|---|---|
| Public decryption | On-chain oracle: `setDecryptionOracle`, `requestDecryption(cts, selector)`, callback with `checkSignatures(requestID, signatures)` | Self-relaying: `makePubliclyDecryptable(handle)`, off-chain `publicDecrypt` through the relayer, any caller submits the cleartext with `checkSignatures(handles, abiEncodedCleartexts, decryptionProof)` | Removed and replaced (commit `a8b3e6ce1`, "good bye oracle", November 2025) |
| ACL replication | Coprocessors push `Allowed` events to a `MultichainACL` Gateway contract; the Gateway decides on decryption rights from its copy | No `MultichainACL`; coprocessors no longer propagate the ACL; the KMS worker queries each host chain's `ACL` contract over RPC before decrypting | Removed (commit `803f10487`, "simple acl", March 2026) |
| Gateway contract set | `GatewayConfig`, `MultichainACL`, `CiphertextCommits`, `Bridging`, `KeyManagement`, `InputVerification`, `Decryption` | `GatewayConfig`, `CiphertextCommits`, `Decryption`, `InputVerification`, `KMSGeneration`, `ProtocolPayment`, plus a `PauserSet` | Two removed, two added |
| Encrypted types | `ebool`, `euint8`–`euint256`, `eint8`–`eint256`, `ebytes1`–`ebytes32`, `ebytes64/128/256`, `eaddress` | `ebool`, `euint8`–`euint128` with the full operator set, `euint160` (alias `eaddress`) with `eq`, `ne`, `select` only, `euint256` without arithmetic; no signed integers, no `ebytes` | Restricted; signed integers are "coming soon" on the roadmap |
| Handle derivation | `keccak256(op, inputs, resultType)`, "unique, deterministic, and state independent" | `keccak256(domainSeparator, op, inputs, scalarFlag, ACL, chainid, blockhash(block.number - 1), block.timestamp)`, then bytes 21 to 31 overwritten with an index marker, the chain id, the type and a version | Changed; handles are block-dependent |
| Input attestation | "attestation": a list of coprocessor signatures over the handles with $$u$$ and $$c$$ embedded | `inputProof`: handle count, signer count, handles, signatures, extra data; the chain id is also signed and is checked against the chain id encoded in the handle; the proof is cached for the rest of the transaction | Same design, more fields |
| Public-decryption marking | `allowForDecryption(handle)` | Library: `FHE.makePubliclyDecryptable(value)` and `isPubliclyDecryptable`; ACL contract: `allowForDecryption(bytes32[])` | Renamed at the library level |
| FHE gas | A per-transaction maximum "FHE gas" | `HCULimit`: 20,000,000 HCU per transaction, 5,000,000 on the longest dependent chain, plus a governance-set per-block cap | Named and refined |
| User decryption | EIP-712 token over $$(u, c)$$; shares encrypted under the user's classical key; $$2t + 1$$ shares | Same, with a NaCl transport key pair generated by the SDK; shares recombined client-side; thresholds read per *context* from `GatewayConfig` | Unchanged in substance |
| Delegation | Not described | `ACL.delegateForUserDecryption(delegate, contract, expiry)` on the host chain and `delegatedUserDecryptionRequest` on the Gateway, for smart-contract accounts | Added |
| Operator contexts | Single operator set with fixed thresholds | A `contextId` selects the operator set and its thresholds; `getPublicDecryptionThresholdForContext`, `getUserDecryptionThresholdForContext` | Added (commit `19fc922e7`, March 2026) |
| Fees | Not described | `ProtocolPayment` on the Gateway prices input verification, public decryption and user decryption | Added |
| Configuration | Not described | `ZamaEthereumConfig` base contract wires a dApp to the host contracts; upgradeable UUPS contracts with version checks; pausing | Added |
| Coprocessor commitments | Two digests per handle, regular and switch-and-squash, majority consensus on the Gateway | `CiphertextCommits.addCiphertextMaterial` with both digests, consensus at `getCoprocessorMajorityThreshold`, and decryption refused until the material is added | Unchanged |
| KMS | 13 parties, $$t \lt n/3$$, robust MPC, Nitro Enclaves, NIST lifecycle, custodial backup | Same design; `KMSGeneration` contracts on both the Gateway and the host chain | Unchanged |

### The oracle is gone

The largest change is the one a developer notices first. In the paper, public decryption is an on-chain request: the contract names an oracle contract, calls `requestDecryption` with a list of handles and a callback selector, and later receives the plaintexts in that callback, where it checks the KMS signatures.

Since library version 0.9 there is no request on-chain; the change landed in the repository on 3 November 2025 under the title "good bye oracle". The contract marks a handle publicly decryptable with `FHE.makePubliclyDecryptable`, and that is the end of its involvement until someone brings the plaintext back. Any off-chain party, the user's own front-end in the documented flow, calls `publicDecrypt` on the relayer SDK and receives three things: the cleartext, its ABI encoding, and a *decryption proof* made of the KMS signatures and their metadata. It submits all three to a function of the contract, which calls `FHE.checkSignatures(handlesList, abiEncodedCleartexts, decryptionProof)`.

![Public decryption as the whitepaper specifies it, through an on-chain request and an oracle callback, next to the self-relaying flow the repository implements, where the contract marks the handle decryptable and any caller submits the KMS-signed plaintext]({{site.url_complet}}/assets/article/blockchain/zamafhe/zama-public-decryption-before-after-sequence.png)

Three things follow. The `IDecryptionOracle` interface, `setDecryptionOracle` and `requestDecryption` no longer exist in the library. The "oracle" line in the trust table becomes moot for public decryption: there is no relaying party to trust or distrust, because whoever submits the plaintext is verified by the same signature check. And the contract has to be written for a value that may never come back, since no protocol component is obliged to complete the round trip; the documentation's migration guide says so in as many words. The protocol documentation still carries a "Relayer & Oracle" page describing an oracle that listens for requests; it describes the pre-0.9 design.

### The Gateway no longer holds a copy of the ACL

The paper gives the Gateway a `MultichainACL` contract, fed by the coprocessors from every host chain's `Allowed` and `AllowedForDecryption` events, and has the Gateway decide from that copy whether a decryption may proceed. The repository removed that contract and the coprocessors' ACL-propagation jobs in March 2026 (commit `803f10487`, "simple acl"). A comment in the Gateway's `Decryption` contract now reads "ACL checks are performed by the KMS", and the KMS connector's worker holds one `ACL` contract binding per registered host chain and queries `isAllowed` (or the public-decryption flag, or the delegation) over RPC for every handle before running the MPC protocol.

The security consequence is a shift of where enforcement happens rather than a weakening. In the paper's design the Gateway could refuse a request; in the code, a decryption request the Gateway accepts is still refused by each KMS party that reads the host chain. The paper's own warning applied to the earlier design too: a KMS party must not trust the Gateway's view, and now it does not have one to trust. The cost is that every KMS node needs an RPC endpoint to every host chain, and the latency of a decryption includes those reads.

### Fewer types than announced

The paper lists signed integers and encrypted byte strings among the supported types. The library at this revision has neither. The `FheType` enumeration shared by the host contracts still reserves identifiers for `Int2` to `Int2048` and for an `AsciiString`, so the intent is kept, but the executor is narrower:

- arithmetic is accepted on `Uint8` to `Uint128` only;
- `Uint160` is the encrypted address, with equality and `select` only;
- `Uint256` has bitwise, shift, comparison and random operations, without addition or multiplication;
- division and remainder take a plaintext divisor only, which the paper also states.

The public roadmap lists signed integers as "coming soon", together with checked arithmetic (`safeAdd`, `safeSub`, `safeMul`). A contract written from the paper's type table for `eint64` or `ebytes256` does not compile against the current library.

### Handles depend on the block

This is the change least visible to a developer and the one with the most consequences. The paper's Listing 7 hashes the operation and its inputs and states that handles are state independent. The executor at this revision hashes, in addition, the ACL address, the chain id, the hash of the previous block and the block timestamp, and then overwrites the last eleven bytes with a fixed marker for computed handles, the chain id again, the type and a handle version.

The documentation's page on handles, added in May 2026, makes the new contract explicit: "the protocol mixes the previous block's hash into how each handle is built, so the same computation in two different blocks already gives you different handles". It asks developers to rely on one rule only, equal handles imply equal plaintexts, and on nothing else.

Two properties of the paper's design are lost, deliberately. A contract or an indexer can no longer predict a handle from its inputs, and identical computations in different blocks no longer collapse to one ciphertext. What is gained is that a handle now carries its chain of origin and its version in its own bytes, which is what lets `InputVerifier` reject a handle minted for another chain, and that re-execution of the same symbolic operation in a later block cannot be confused with the first.

### What was added around the protocol

The paper describes a protocol; the repository is a deployment, and several additions are the difference between the two:

- **Fees.** A `ProtocolPayment` contract on the Gateway prices input verification, public decryption and user decryption. The paper never mentions a fee or a token; the litepaper does.
- **Operator contexts.** Thresholds are read per `contextId` from `GatewayConfig`, so that a change of operator set can be introduced as a new context rather than a global reconfiguration. This is the machinery the paper's "committee-based MPC" future-work item would need.
- **Delegated user decryption.** A holder can delegate, per contract or with a wildcard and with an expiry, the right to request user decryption of its handles to another address. The stated use is account abstraction, where the decryption request is issued by a smart-contract account.
- **Operational controls.** Pausing on both the host and the Gateway contracts, UUPS upgradeability with an on-chain version check, `KMSGeneration` mirrored on the host chain, and a `ZamaEthereumConfig` base contract that wires a dApp to the right addresses.

### What did not change

The parts of the paper that carry the security argument are implemented as written:

- **Commitments.** Coprocessors still commit two digests per handle, the ciphertext and its switch-and-squash form, and the Gateway still refuses a decryption for a handle whose material has not reached the coprocessor majority; `CiphertextCommits.isCiphertextMaterialAdded` is the check.
- **Inputs.** They are still verified off-chain by the coprocessors and enter the chain as a list of signatures that `InputVerifier` checks against a threshold of registered signers, with the user and contract addresses bound in.
- **User decryption.** It still returns encrypted shares that the client recombines, with a threshold read from the Gateway.
- **KMS.** Thirteen parties with $$t = 4$$, robust MPC, Nitro Enclaves, the NIST lifecycle and the custodial backup, as the paper describes.

### Future work, one year on

Against the paper's own list: verifiable FHE has not replaced the coprocessor majority; the ZKPoK is still the non-post-quantum piece; the KMS still rests on a threshold assumption plus enclaves rather than on a proof; MPC threshold signatures have not appeared. Operator contexts are a concrete step toward rotating committees. The bounded-ACL and layered-Gateway items are not visible in this revision.

## Conclusion

The whitepaper is still the right document for the protocol's security argument, and the wrong one for its API.

- **Unchanged**: symbolic execution, coprocessor commitments with majority consensus, threshold decryption with $$t \lt n/3$$ over 13 parties, input attestation by coprocessor signatures, user decryption by encrypted shares, enclaves and the NIST key lifecycle.
- **Removed**: the on-chain decryption oracle (`requestDecryption`, `IDecryptionOracle`) and the Gateway's `MultichainACL`; public decryption is self-relayed and ACL enforcement at decryption time moved into the KMS nodes, which read each host chain directly.
- **Restricted**: no signed integers, no encrypted bytes; `eaddress` and `euint256` with a reduced operator set.
- **Changed**: handles are no longer state independent; they mix in the previous block hash, the timestamp, the chain id and a version.
- **Added**: fees, operator contexts, delegated user decryption, pausing and upgradeability.
- **Still future**: verifiable FHE, a post-quantum ZKPoK, a verifiable KMS.

![Mindmap of the whitepaper reading: the four principles, the components and trust table, the Solidity library, the implementation details, the future work, and the changes found in the repository]({{site.url_complet}}/assets/article/blockchain/zamafhe/2026-09-18-zama-fhevm-whitepaper-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Host chain** | The L1 or rollup where confidential contracts are deployed; the protocol asks nothing of it beyond hosting the trusted host contracts. |
| **Symbolic execution** | On-chain evaluation that produces handles and events instead of ciphertexts, leaving the FHE arithmetic to the coprocessors. |
| **Handle** | The `bytes32` identifier of a ciphertext; state independent in the paper, block-dependent in the code. |
| **Attestation / inputProof** | The list of coprocessor signatures over verified input handles, bound to a user, a contract and a chain, that the host chain checks instead of the zero-knowledge proof. |
| **Switch-and-squash** | The deterministic conversion of a ciphertext to a larger plaintext domain performed by the coprocessors so that the KMS can decrypt it safely. |
| **Ciphertext commitment** | The pair of digests, regular and switch-and-squash, a coprocessor posts to the Gateway for a handle; decryption waits for a majority to agree. |
| **Programmable bootstrapping** | The TFHE operation that evaluates a lookup table homomorphically while resetting noise, giving exact unbounded computation. |
| **Concrete key** | One instance of the FHE key in the NIST lifecycle; a conceptual key is the sequence of concrete keys linked by key-switching keys. |
| **Selective failure attack** | An attack in which a malicious ciphertext makes decryption succeed or fail depending on bits of the secret key; the paper's reason for validating Gateway events and ciphertext digests in the KMS. |
| **Self-relaying decryption** | The current public-decryption flow, where the contract marks a handle decryptable and any party submits the KMS-signed plaintext for on-chain verification. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| `FHE.requestDecryption` and `setDecryptionOracle` from the paper's Listing 5 do not exist. | Mark the handle with `makePubliclyDecryptable`, decrypt off-chain with the relayer SDK, and expose a function that takes the cleartext and proof and calls `checkSignatures(handles, abiEncodedCleartexts, proof)`. |
| Nobody is obliged to bring a public decryption back on-chain. | Design the contract for a reveal that may not happen; if the protocol must progress, have the interested party submit it. |
| `eint*` and `ebytes*` from the paper's type list do not compile. | Use unsigned types; encode signed values with an offset; keep byte strings off-chain and commit to them. |
| `eaddress` supports only `eq`, `ne` and `select`; `euint256` has no `add` or `mul`. | Use `euint128` or below for arithmetic; use `euint256` for bitwise work and comparisons only. |
| Two identical computations give different handles across blocks, and may or may not within one. | Never compare handles to compare values; use `FHE.eq` and decrypt the `ebool`. |
| The KMS checks the host chain's ACL at decryption time, not a Gateway copy. | Grant access with `FHE.allow` before the decryption request; a grant in the same block as the request may not be visible to every KMS node yet. |
| A transaction reverts above 20,000,000 HCU, or 5,000,000 on one dependency chain, or when the block cap is hit. | Prefer scalar operands, keep dependency chains short, and check `HCULimit` on the target network before assuming the devnet limits. |
| A smart-contract account cannot sign the EIP-712 user-decryption request itself. | Have the holder call `ACL.delegateForUserDecryption` and use the delegated request path on the Gateway. |

## Frequently Asked Questions

**Q: Which of the whitepaper's four trust assumptions are still exactly as stated?**

Coprocessors at more than one half honest and the KMS at two thirds honest are unchanged and are enforced by the same mechanisms: majority consensus on ciphertext digests in `CiphertextCommits`, and thresholds of $$t + 1$$ public-decryption results and $$2t + 1$$ user-decryption shares in `Decryption`. The relayer line is unchanged too. The oracle line has become moot for public decryption, because there is no oracle in the flow; whoever submits a plaintext is checked by `checkSignatures`.

**Q: Why did removing the oracle not weaken security?**

Because the oracle was never trusted. In the paper it could only delay a request, since the callback verified KMS signatures. The current design keeps the signature check and drops the intermediary; the plaintext is verified against the KMS signers' threshold whether a relayer, the user or a third party submits it. What changed is liveness: no component is responsible for completing the round trip, so the contract's author has to decide who is motivated to submit the result.

**Q: What does "handles are not state independent" break, concretely?**

Three assumptions a developer might have taken from Listing 7:

- that a handle can be predicted from its inputs, for instance by an indexer that wants to follow a computation;
- that two identical computations give the same handle, so that handle equality can stand in for value equality;
- that a handle is portable across chains.

None holds. The executor mixes the previous block hash, the timestamp and the chain id into the hash, and the documentation now states a single guarantee: equal handles mean equal plaintexts.

**Q: How does the KMS know that a user may decrypt a handle, now that the Gateway has no ACL copy?**

Each KMS worker is configured with the address of the `ACL` contract on every registered host chain. On a decryption request it reads, for each handle, whether the requesting user is allowed for the named contract; for a public decryption it reads the public flag instead, and for a delegated request it reads the delegation. It runs the MPC protocol only if every check passes.

The check moved from a replicated copy on the Gateway to a direct read of the source of truth.

**Q: Combine two changes: a smart-contract wallet wants to read a balance held in a confidential token. What is the path, and which whitepaper mechanisms does it rely on?**

The path has four steps:

- The holder's contract account calls `ACL.delegateForUserDecryption(delegate, tokenAddress, expiry)` on the host chain, naming an externally owned address as delegate.
- That address generates a transport key pair, signs the EIP-712 request the paper calls an authentication token, and submits a delegated user-decryption request to the Gateway.
- The Gateway checks that the ciphertext material has reached coprocessor consensus; the KMS workers read the host chain ACL and the delegation.
- Each party returns its share encrypted under the transport key, and the SDK recombines $$2t + 1$$ shares.

The threshold, the encrypted shares and the EIP-712 binding are the paper's mechanisms; the delegation and the direct ACL read are the repository's.

**Q: Which of the paper's numbers are still meaningful?**

The cryptographic ones: $$n = 13$$, $$t = 4$$, 128-bit security, the ZKPoK sizes and the packed-input format. The performance table is a June 2025 snapshot of TFHE-rs on one server and two GPUs and should be re-measured rather than quoted. The HCU limits, 20,000,000 per transaction and 5,000,000 of depth, are not in the paper and are stated for the devnet, with a per-block cap now set by governance on-chain.

## References

### Analyzed source

- [zama-ai/fhevm](https://github.com/zama-ai/fhevm) — analyzed at commit [`ac6ff45ebb27c1300cc44669235751c657b3ce14`](https://github.com/zama-ai/fhevm/tree/ac6ff45ebb27c1300cc44669235751c657b3ce14) (50 commits after tag [`v0.14.1`](https://github.com/zama-ai/fhevm/releases/tag/v0.14.1); host contract `FHEVMExecutor` at version 0.7.0), 2026-09-18
- Commits cited for individual changes: [`a8b3e6ce1`](https://github.com/zama-ai/fhevm/commit/a8b3e6ce1) "good bye oracle" (2025-11-03), [`803f10487`](https://github.com/zama-ai/fhevm/commit/803f10487) "simple acl" (2026-03-11), [`19fc922e7`](https://github.com/zama-ai/fhevm/commit/19fc922e7) "context-aware decryptions" (2026-03-23)

### The whitepaper and protocol documentation

- [Fhevm — A cross-chain protocol for confidential smart contracts, version 3.1, 30 June 2025](https://github.com/zama-ai/fhevm/blob/main/fhevm-whitepaper.pdf)
- [Zama Confidential Blockchain Protocol Litepaper](https://docs.zama.org/protocol/zama-protocol-litepaper)
- [FHE on Blockchain — architecture overview](https://docs.zama.org/protocol/protocol/overview)
- [Solidity guides](https://docs.zama.org/protocol/solidity-guides)
- [Relayer SDK guides](https://docs.zama.org/protocol/relayer-sdk-guides)
- [Access Control List](https://docs.zama.org/protocol/solidity-guides/smart-contract/acl)

### Papers cited by the whitepaper

- [Benoît Libert — Vector Commitments With Proofs of Smallness: Short Range Proofs and More](https://eprint.iacr.org/2023/800)
- [Dahl et al. — Noah's ark: Efficient threshold-FHE using noise flooding](https://doi.org/10.1145/3605759.3625259)
- [Bootland et al. — Threshold (fully) homomorphic encryption](https://eprint.iacr.org/2025/699)
- [Nigel P. Smart — Practical and efficient FHE-based MPC](https://doi.org/10.1007/978-3-031-47818-5_14)
- [Chillotti et al. — TFHE: Fast fully homomorphic encryption over the torus](https://doi.org/10.1007/s00145-019-09319-x)
- [NIST SP 800-57 Part 1 Rev. 5 — Recommendation for Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [TFHE-rs](https://github.com/zama-ai/tfhe-rs) and [threshold-fhe](https://github.com/zama-ai/threshold-fhe)

### Standards

- [EIP-712 — Typed structured data hashing and signing](https://eips.ethereum.org/EIPS/eip-712)

### Related articles

- [Running a Zama Coprocessor — Architecture, Services and Operator Setup]({{site.url_complet}}/2026/09/18/zama-coprocessor-architecture-and-operator-setup/)
- [Zama FHEVM Architecture — Components, Data Flow and What Has to Be Trusted]({{site.url_complet}}/2026/09/18/zama-fhevm-architecture-components-trust-model/)
- [Zero-Knowledge Proofs in the Zama Protocol — What They Prove and Where They Are Verified]({{site.url_complet}}/2026/07/24/zero-knowledge-proofs-zama-protocol/)
- [Technical Analysis of the OpenZeppelin ERC-7984 Implementation]({{site.url_complet}}/2026/02/24/erc7984-openzeppelin-analysis/)
- [Overview, security and applications of Multi-Party Computation (MPC)]({{site.url_complet}}/2024/10/21/mpc-protocol-overview/)

### Tooling

- [Claude Code](https://claude.com/product/claude-code)
