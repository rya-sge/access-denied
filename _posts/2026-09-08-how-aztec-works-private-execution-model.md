---
layout: post
title: "How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun"
date:   2026-09-08
lang: en
locale: en-GB
categories: blockchain ethereum ZKP
tags: aztec zkp privacy zcash railgun canton fhe rollup
description: Aztec runs private functions on the user's device and public ones on the sequencer. Notes, nullifiers, what a transaction still leaks, and four rival designs.
image: /assets/article/blockchain/aztec/2026-09-08-aztec-privacy-protocol-mindmap.png
isMath: false
---

Most confidential-ledger designs answer one question: where does the plaintext live? Zcash keeps it in notes only the owner can decrypt. Zama's protocol keeps it encrypted under a key nobody holds in full. Canton keeps it on the machines of the parties entitled to see it, and nowhere else. Each answer determines what the system can compute, who has to be online, and what leaks anyway.

Aztec answers it the same way Zcash does, then tries to do something Zcash does not: run arbitrary smart contracts over that state, including contracts that touch public state in the same transaction. That combination is the whole design, and it is why Aztec has two execution environments rather than one. Private functions run on the user's own device, in a zero-knowledge circuit, over notes only that user can decrypt. Public functions run on the sequencer, in a virtual machine that looks much like the EVM. A single transaction crosses from one to the other, in that order, and never back.

This article works through that machinery: the state model, the keys, how a note reaches its recipient, what the kernel circuits do, how fees are priced, and how L1 and L2 exchange messages. It ends with what a transaction still reveals even when everything is used correctly, and a comparison with four other systems that solve the same problem differently. It is a companion to the earlier [Aztec: A Privacy-First Layer 2 for Ethereum]({{site.url_complet}}/2025/10/29/aztec-architecture-overview/), which covers the same ground in a shorter form.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why two execution environments

A private function has to be executed by someone who can see the private inputs. On Aztec that is the user, on their own machine, and the output is a zero-knowledge proof that the execution was correct. Nobody else runs the function, so nobody else learns the arguments, the notes consumed, or which function was called.

A public function has the opposite requirement. Updating public state means writing at the current head of the chain, and only the sequencer knows what that head is. A user cannot prove a public state transition in advance, because the state may change before their transaction lands.

The two requirements cannot be satisfied by one environment, so Aztec ships both:

- **The PXE** (Private eXecution Environment, pronounced "pixie") is a TypeScript library that runs in the wallet, a browser, or Node.js. It stores the user's notes, viewing keys and tagging secrets, executes private functions, and generates the proofs. Private inputs never leave it.
- **The AVM** (Aztec Virtual Machine) runs on the sequencer and executes public functions against the public data tree. Its state model is close to Ethereum's.
- **Utility functions** are a third category and are not part of a transaction at all. They are unconstrained queries that run offchain in the PXE, can read both private and public state, and are the rough equivalent of a Solidity `view` reachable only through `eth_call`. Because they are unconstrained, nothing guarantees their results.

The ordering is fixed and follows from the above: all private execution happens first, on the client; public calls are *enqueued* during private execution and run afterwards on the sequencer. A private function cannot read the result of a public call it enqueues, because that call has not happened yet. This is the single most consequential fact about writing Aztec contracts, and the reason so much of the framework is about deferred, unilateral messages rather than ordinary calls.

## The state model

Private and public state live in separate trees, and they behave differently enough that the choice between them is the first design decision in any contract.

![The client-side PXE writes note hashes and nullifiers, the sequencer-side AVM reads and writes the public data tree, and all three feed the archive tree of block headers]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-trees-and-state-concept.png)

### Private state is a UTXO set

Private state cannot be stored as "account X has value Y", because updating a record in place would leak the transaction graph: an observer watching a slot change learns that its owner just transacted, even without learning the value. Aztec therefore uses an append-only structure.

A unit of private state is a **note**. The protocol does not store the note; it stores a **note commitment**, a hash, as a leaf in the note hash tree. The note contents reach the owner separately, encrypted. To use a note, the owner proves in a circuit that they know a preimage of some leaf in that tree, without revealing which leaf.

Notes are never edited or deleted. "Deleting" a note means emitting a **nullifier** into a separate nullifier tree. The nullifier is derived from the note and from the owner's nullifier key, so:

- Only the owner can compute it, which is what prevents anyone else from spending the note.
- Nobody can link a nullifier back to the note it destroys without that key, which is what preserves privacy.
- The nullifier tree is an indexed Merkle tree, a structure that supports efficient **non-membership** proofs — the operation double-spend prevention needs, since the check is "this nullifier has never appeared before".

Modifying private state is therefore always nullify-then-create. The mental model in the documentation is cash: spending a 5 unit note on a 3.50 purchase nullifies the 5 note and creates two new ones, 1.50 back to you and 3.50 to the recipient. It also explains why a private balance is a *set* of notes rather than a number, and why the number of notes a user holds affects their proving time.

### Public state is close to the EVM

Public state lives in a sparse public data tree, written by the sequencer during AVM execution, and behaves as a developer coming from Ethereum would expect: a slot holds a value, reads and writes are ordinary, everything is visible.

Both kinds of storage are **siloed by contract address** so that contracts cannot collide or reach into each other's state. The kernel circuit performs the siloing: a public slot becomes `H(contract_address, storage_slot)`, and a note hash becomes `H(contract_address, note_hash)` before insertion. For notes there is a further step, mixing in a nonce derived from the transaction, so that two identical notes produce distinct leaves.

One consequence is worth stating plainly, because it constrains contract design more than anything else: **a private function cannot read current public state.** Private execution happens before the sequencer touches the block, so the current value is not knowable. Aztec offers three ways around this, and the choice is a real trade-off rather than a formality.

| State variable | Mutable | Readable in private | Typical use |
|---|---|---|---|
| `PublicMutable` | yes | no | Total supply, vote counts, admin configuration |
| `PublicImmutable` | no (write once) | yes | Token name, symbol, decimals, fixed configuration |
| `DelayedPublicMutable` | yes, after a delay | yes | Configuration that is not time-sensitive, such as a swap fee |

`PublicImmutable` is readable in private because once a circuit has proved the value was set in the past, it knows the value cannot have changed. `DelayedPublicMutable` generalises that: writes take effect only after a configured delay, typically hours or days, which gives private execution a window in which the value is guaranteed stable. The cost is that it is unusable for anything needing immediate effect, an emergency pause being the obvious example.

On the private side, the equivalent choices are `PrivateMutable`, `PrivateImmutable` and `PrivateSet`, each wrapped in an `Owned<>` type that binds the collection to an owner address. One property of `PrivateMutable` surprises people: **reading it is a write.** `get_note()` nullifies the note it reads and recreates it, so that reads are indistinguishable from writes and the sequencer cannot infer the value from the access pattern. The consequences are that a read costs a note creation and a delivery, and that two transactions reading the same note contend, so only one of them lands.

## Keys: one account, several key pairs

An Ethereum account is one key pair doing every job. An Aztec account is several, because the jobs have different requirements — you may want to give someone the ability to *see* your notes without the ability to *spend* them.

| Key | Purpose | Protocol-managed | Rotatable |
|---|---|---|---|
| Nullifier keys (`Npk_m`) | Spending notes | Yes | No |
| Incoming viewing keys (`Ivpk_m`) | Decrypting received notes | Yes | No |
| Outgoing viewing, tagging, message-signing, fallback | Reserved slots, not currently used | Yes | No |
| Signing key | Authorising transactions | No, defined by the account contract | Yes |

Two details matter more than the table suggests.

**Nullifier keys are app-siloed.** The key used to nullify is not the master key but `nhk_app = hash(nhk_m, app_contract_address)`. A contract therefore only ever works with a key scoped to itself, which bounds what a flaw in one application can do to a user's state in another. The protocol verifies that the siloed key derives from the master key without learning either: the user proves that derivation in the circuit, and the protocol checks the proof.

**The signing key is not a protocol key at all.** Aztec has native account abstraction in a strong sense: there is no protocol-level signature scheme. An account contract is an ordinary contract with an entrypoint that validates the request however it likes — ECDSA over secp256k1, Schnorr, a passkey, a multisig, or a rule with no signature in it. The protocol keys above are fixed at account creation and cannot be rotated; the signing key can be, because it is application state.

## Getting a note to its recipient

A note commitment onchain is useless to a recipient who does not know the note's contents. Delivery is therefore a separate step from creation, and in current Aztec.nr it is explicit: a creation method returns a message object, and failing to call `deliver` on it loses the information permanently. The compiler warns about the unused value, which is the main thing standing between a developer and silent data loss.

There are three delivery modes, and choosing between them is a cost-versus-trust decision:

- **`offchain()`** — the message is encrypted and emitted as an offchain effect, never posted to Ethereum blobs. Zero data-availability cost, zero proving overhead, and no guarantee at all: the sender can simply not deliver, or deliver wrong content. The recipient hands the message to their wallet through an auto-generated `offchain_receive` function. Correct whenever the sender is motivated to deliver — a change note going back to yourself, or a payment where the recipient withholds the goods until the note arrives.
- **`onchain_unconstrained()`** — encrypted without constraints but posted onchain. Pays for blob space, no proving overhead, and the sender can still deliver incorrect content. The documentation is blunt that this is strictly worse than offchain delivery if you are willing to build the offchain channel: you pay for data availability and buy no guarantee. It exists so that you do not have to build that channel.
- **`onchain_constrained()`** — the encryption *and* the discovery tag are constrained in the circuit and posted onchain. Costs blob space and proving time, and guarantees the recipient will be able to find and decrypt the content. Required whenever the sender cannot be trusted: minting to a third party, fee payment, an escrow release, a multisig configuration change.

### Note discovery by tagging

Even with the content onchain, a recipient has to find it. Downloading every encrypted log and trial-decrypting it works, and is what Zcash does, but the cost grows with the network rather than with the user's own activity.

Aztec's default is **note tagging**. Every emitted log is an array of fields whose first element is a tag, the node indexes logs by tag, and both parties can compute the tags independently. The derivation is always `poseidon2(secret, index)`, where `index` counts the logs the sender has emitted to this recipient in this contract; what varies between strategies is only how the two parties come to share `secret`:

- **Non-interactive handshake.** The sender publishes an ephemeral public key onchain, encrypted to the recipient. The recipient finds it during sync and derives the shared secret by Diffie-Hellman against their incoming viewing key. This reaches a recipient who has never registered the sender, at the cost of publishing that a handshake with them occurred. It is the default for a new external recipient.
- **Interactive handshake.** The same derivation, but the ephemeral key is never published: the recipient signs it at send time through an oracle request that is verified in-circuit. Nothing appears onchain, but the send fails if the recipient is unreachable, so it is never the default.
- **Address-derived secret.** The PXE computes the shared point by Diffie-Hellman from the two addresses. No onchain trace, no coordination, but the recipient only finds the message if they registered the sender in advance.
- **Arbitrary secret.** A point the two parties already agreed out of band.

The last two cannot back constrained delivery, because nothing onchain vouches for the secret. The tag is finally siloed with the contract address by the kernel before it appears onchain.

## The transaction lifecycle

![A transfer is simulated in the PXE, proved through the kernel circuits, sent to the sequencer which runs the enqueued public calls, then settled by an epoch proof verified on L1]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-transaction-lifecycle-sequence.png)

The wallet first asks the PXE to **simulate** the entrypoint. By default this runs in a kernel-less mode: the private bytecode executes and the values the kernel circuits *would* have produced are computed in TypeScript instead of proving them. That is much faster, and it lets the wallet collect authentication-witness requests without prompting the user to sign during a simulation.

Only then does the wallet call `proveTx`, and the **private kernel circuits** run. The kernel is recursive, processing one private call per iteration and accumulating side effects — note hashes, nullifiers, logs, messages — while validating the call context and the scoping of those side effects to the contract that produced them. It has five phases:

- **Init** processes the first call and checks it matches the transaction request. The first call has no `msg_sender`.
- **Inner** processes each subsequent call: it verifies the previous kernel proof, pops the next call from the private call stack, and appends the new side effects. It chains as many times as there are calls.
- **Reset** can run at any point before the tail. It squashes transient note/nullifier pairs, where a note is created and destroyed within the same transaction, and validates read requests against the state. This is what keeps the accumulated data small.
- **Tail** finalises a transaction with no public calls, sorting the side effects into rollup format.
- **Tail to public** is the bridge for a transaction that has both, splitting side effects into revertible and non-revertible sets before handing over.

![Init validates the first call, inner iterates once per additional private call at about 101,000 gates each, reset squashes transient pairs, and tail finalises the transaction]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-kernel-recursion-workflow.png)

That recursion is where most of a transaction's proving cost comes from. The fixed overhead for init, reset and tail is roughly **290,000 gates**, and every private call beyond the account entrypoint adds an inner iteration of roughly **101,000 gates**. Splitting a private function into two smaller, tidier private functions therefore makes the transaction more expensive, not less, however much smaller each half becomes. This is the reverse of the intuition an EVM developer brings, and it is the reason Aztec.nr offers `#[internal]` functions that are inlined at compile time and add no kernel iteration.

The sequencer then verifies the private proof, executes the enqueued public calls in the AVM, updates public state and publishes the block to L1 with the data going into blobs. Settlement is separate and later: the **rollup circuits** aggregate proofs in a binary tree — transaction, block, checkpoint, epoch — and provers submit an epoch proof to the verifier contract on Ethereum. Once that proof is verified, the state transition is final. The binary-tree topology exists so that proving can be parallelised across many prover instances.

## Fees

Aztec renames Ethereum's fee vocabulary but keeps the mechanism. **Mana** is the unit of computational effort, the equivalent of gas. **Fee Juice** is the fee token, bridged from Ethereum and deliberately **non-transferable** on Aztec: it can pay fees and nothing else.

Mana has two dimensions, priced separately, because the underlying costs are unrelated:

```
fee = (daMana × feePerDaMana) + (l2Mana × feePerL2Mana)
```

Data-availability mana covers publishing transaction data to blobs on Ethereum; L2 mana covers execution on Aztec. Pricing borrows from [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559), including a congestion multiplier and separate base and priority components. One naming trap: the SDK and the protocol code call these `daGas`, `l2Gas` and `feePerDaGas` rather than mana, so when reading code, gas and mana are the same thing.

Proving cost is not in this formula at all. It is paid by the user in time and memory on their own device, which is why gate counts matter to a user's experience in a way gas never does on Ethereum.

## L1 and L2 messaging

Aztec cannot do synchronous cross-chain calls. A private function is proved against historical state before the sequencer sees it, so it cannot learn the result of an L1 call within the same transaction. Communication is therefore asynchronous message passing through **portals**: a portal is the L1 half of an application, associated with an L2 address, and it may be a contract or even an externally owned account.

Messages travel through message boxes with one end on each side, an inbox for L1 to L2 and an outbox for the reverse. A sender inserts into a pending set; the rollup moves the message to a ready set on the other side; the recipient consumes it, which nullifies it. Because a message can legitimately be sent many times, the boxes are multi-sets.

The design decision worth noticing is that Aztec **pulls** messages rather than pushing them. On most rollups, execution originates from the message bridge, which calls the target contract — and that requires full calldata, which for L1 to L2 messages is committed on L1 and therefore public. Pushing would expose the inputs of the private function that consumes the message. By pulling, the message can be a value *derived* from the arguments instead: a deposit still leaks the value and the depositor on L1, where it happened publicly, but the new owner on L2 stays hidden.

The corollary is that every cross-domain call is unilateral, and applications have to handle failure explicitly. A token bridge that assumes the far side succeeded is a bridge that eventually locks funds on one side without minting on the other.

## What a transaction still leaks

Aztec's own documentation is direct about this, and it is the part most worth reading twice, because a contract can be entirely correct — no value stolen, no assertion bypassed — and still defeat the purpose it was written for.

**Every argument passed to a public function is public.** A private transfer that enqueues `mint_to_public(recipient, amount)` has published exactly the two facts it was hiding. The leak is in the arguments, not in the call.

**`enqueue` reveals `msg_sender`.** A private function that enqueues a public call publishes the caller's address by default. `enqueue_incognito` sets it to a null address instead, and the callee then has to use `maybe_msg_sender()` to cope with its absence. Tracing every `enqueue` in a contract that advertises privacy is the highest-yield review a developer can perform on their own code.

**Calling an internal public function from private identifies the contract.** The fact that the call came from a private function of that same contract is trivially known, which reveals which application the user was interacting with even when every value is hidden.

**Some counts are visible.** Note hashes, nullifiers and private logs are padded so their true counts are hidden. The **number of public function calls** and the **number of L2 to L1 messages** are not. Two private entrypoints of the same contract that produce different counts are therefore distinguishable from outside — a "transaction fingerprint" that anyone watching the pool can read. Reducing this is the motivation behind proposals to standardise fingerprints so that transactions fall into indistinguishable privacy sets, and it is not solved today.

**Querying a node reveals what you are interested in.** Reading a note means proving its existence against a tree root, and getting the current sibling path from a third-party node means telling that node which leaf you care about. Using an older root avoids the query but shrinks your anonymity set to transactions before that snapshot. The clean answer is to run your own node; the honest answer is that most users will not.

**L2 to L1 messages are entirely public**, message and resulting L1 execution both.

Two further limitations belong in the same list. The stack is unaudited and under active development, and the documentation says explicitly that real secrets should not be entrusted to it yet. And the PXE's `scopes` mechanism, which restricts whose notes a call may access, is caller-specified: the application chooses its own scopes, and there is no mandatory protocol-enforced layer denying an application access to another application's private data.

## Comparison with four other confidential systems

These five systems are usually grouped together as "privacy" projects, though they answer different questions. The axis that separates them is not the strength of the cryptography but **where the plaintext lives and who has to act to read it**.

![Aztec, Railgun and Zcash keep per-owner notes read locally, Zama encrypts state under a threshold key computed on in place, and Canton sends plaintext only to entitled parties]({{site.url_complet}}/assets/article/blockchain/aztec/confidential-systems-secret-location.png)

Three groupings fall out of that question:

- **Per-owner notes, read locally** — Zcash, Railgun and Aztec. Each note is sealed to one key tree. The owner decrypts locally and proves a valid transition. No third party is consulted and no permission is requested; the cost moves to scanning or tagging.
- **Ciphertext computed on in place** — Zama's protocol. State is encrypted under one network key that nobody holds in full. Computation happens on ciphertext, and reading your own value requires a live, authorised round trip to a threshold committee.
- **Plaintext held only by entitled parties** — Canton. There is no global replicated state to hide. Confidentiality comes from not sending the data at all.

### The table

| Dimension | **Aztec** | **Zama Protocol** | **Zcash** | **Canton** | **Railgun** |
|---|---|---|---|---|---|
| Architecture | Privacy-first L2 rollup on Ethereum | Confidential compute layer for EVM chains | Standalone L1 | Standalone permissioned L1 | Contract-based privacy layer on EVM chains |
| Confidentiality primitive | ZK proofs over per-owner notes | Fully homomorphic encryption (TFHE) | ZK proofs over per-owner notes | Selective data distribution, no global state | ZK proofs over per-owner notes |
| Where the plaintext lives | Owner's device | Nowhere in full; key split across a KMS committee | Owner's device | Machines of the entitled parties | Owner's device |
| Reading your own balance | Local trial decryption or tag lookup | Authorised round trip to the threshold committee | Local trial decryption | Read your own local ledger view | Local decryption with the viewing key |
| Programmability | Arbitrary contracts in Noir, private and public | Solidity with encrypted types | Payments only | Arbitrary multi-party logic in Daml | Token transfers and DeFi integrations |
| Private and public state in one transaction | Yes, private then public | Yes, all state is encrypted in place | No | Not applicable; no public state | Limited to the shielded pool boundary |
| Composability with existing EVM contracts | No; a distinct VM and language | Yes, on the host chain | None | None | Partial, through the shield and unshield boundary |
| Proof or crypto system | Client-side proving, kernel and rollup circuits | TFHE plus a ZK proof of knowledge on inputs | Groth16 (Sapling), Halo 2 (Orchard) | No ZK proving; encrypted view distribution | Groth16 with a trusted setup |
| Trusted setup | No | Not for FHE; a CRS for the input proofs | Sapling yes, Orchard no | Not applicable | Yes, Perpetual Powers of Tau |
| Selective disclosure | Viewing keys, plus contract-level design | ACL grants per ciphertext handle | Viewing keys per address | Observer parties, per contract | Viewing keys, scopable by block range |
| Who can censor a read | Nobody | The KMS committee, by refusing to decrypt | Nobody | The counterparty who holds the data | Nobody |
| Liveness needed to read | None | The committee must be live | None | None | None |
| Fee and relay privacy | Native account abstraction, fee abstraction | Host chain's model | Transparent fee | Not applicable | Broadcaster network over Waku, fees in any token |
| Main cost | Client-side proving time and gate counts | FHE evaluation, capped by an HCU budget | Proving and chain scanning | Validation scales with stakeholder count | Proving and gas on the host chain |
| Quantum posture | Elliptic-curve commitments and proofs | TFHE is lattice-based | Elliptic-curve based | Depends on the underlying scheme | Elliptic-curve based |

### Zama Protocol

Zama takes the opposite side of the central trade-off. Because the state is encrypted under a single network key and computed on homomorphically, **a contract can operate on two users' values at once without either user participating**: a sealed auction can compare bids, a confidential token can move a balance between two accounts, and neither party needs to produce a proof about their own state. That is beyond what a note model does.

The price is who holds the key. Nobody does, in full: it is split across a threshold KMS committee, and reading a value means an authorised request that the committee answers, sealed to a transport key. So reading your own balance requires a live third party and permission, decryption is a protocol event rather than a local computation, and a threshold breach is global and retroactive rather than confined to one account. Zero-knowledge appears in the design too, but in a narrow role: a proof of knowledge attached to encrypted inputs, showing the submitter knows the plaintext. The article [Zero-Knowledge Proofs in the Zama Protocol — What They Prove and Where They Are Verified]({{site.url_complet}}/2026/07/24/zero-knowledge-proofs-zama-protocol/) covers exactly where that proof sits and what it does not assert.

The two designs also fail differently. Aztec's confidentiality rests on encryption to per-user keys and the soundness of its proofs; Zama's rests on the FHE scheme and on the committee's threshold assumption holding.

### Zcash

Zcash is the closest relative and the origin of most of the vocabulary: note commitments in an append-only tree, nullifiers for spend prevention, viewing keys for selective disclosure. Aztec's key hierarchy, with separate nullifier and incoming-viewing keys, mirrors the structure of Orchard's key tree closely.

The differences are scope and discovery. Zcash shields payments in its own asset; it has no general smart contracts and no notion of public state to compose with. Aztec is trying to run arbitrary contracts over the same substrate, which is where all its additional machinery comes from: the public/private split, the kernel circuits, delayed public state, portals. On discovery, Zcash's shielded wallets trial-decrypt candidate outputs, whose cost grows with total network activity; Aztec's tagging lets a recipient query for logs addressed to them, at the cost of a handshake that reveals contact occurred. On proving, Sapling used Groth16 with a trusted setup, and Orchard moved to Halo 2 without one.

### Canton

Canton is the outlier here, because it achieves confidentiality without cryptographically hiding state at all. There is no globally replicated ledger: a transaction is decomposed into sub-transaction views, and each validator receives only the views for the parties it hosts. What a party is not entitled to see is never sent to it.

That buys things a note model cannot easily offer. Disclosure is structural rather than opt-in, so an auditor is modelled as an observer party on a contract and receives the relevant views by construction, instead of being handed a viewing key after the fact. Multi-party workflows with different visibility per participant are the native case rather than something built on top. And there is no proving cost anywhere, because nothing is being proved in zero knowledge.

The corresponding losses are real. There is no public state and no permissionless composability; participation is permissioned and identities are named parties rather than pseudonymous addresses. Confidentiality depends on counterparties not redistributing what they legitimately received, which is a legal and operational control rather than a cryptographic one. [Canton Network — Architecture, Privacy Model, and Comparison with Ethereum, Railgun, Zcash, Zama fhEVM, and Besu]({{site.url_complet}}/2026/05/12/canton-network-architecture/) develops this model in full, including the two-layer consensus that makes it work.

### Railgun

Railgun is the nearest neighbour in deployment terms: it puts a Zcash-style shielded pool inside contracts on chains that already exist, rather than asking anyone to move to a new one. Balances live as encrypted UTXOs in a Merkle tree, spending emits nullifiers, and zk-SNARKs (Groth16, over a Perpetual Powers of Tau setup) prove valid spends. Users hold a spending key on Baby Jubjub and a viewing key on Ed25519, and the viewing key can be scoped by block range for reporting.

Its distinctive piece is the Broadcaster network: relayers that submit transactions on a user's behalf over Waku and pay the gas, so the transaction does not originate from the user's own address and fees can be paid in any token. Aztec addresses the same metadata problem differently, with native account abstraction and fee abstraction built into the protocol rather than an external relay layer.

Railgun's privacy holds inside the pool; every shield and unshield is a visible event on a public chain, and interaction with an ordinary DeFi contract means crossing that boundary. Aztec has no equivalent boundary internally, because private and public execution are both native. It pays for that by being a separate chain with a separate language, unable to call an existing Solidity contract at all. The earlier [RAILGUN: Privacy Infrastructure for DeFi]({{site.url_complet}}/2025/10/28/railgun-overview/) covers its circuits and key model in detail.

### Reading the table

No system here dominates. The choice follows from three questions:

- **Does a contract need to compute over values whose owners are not present?** If yes, only the FHE model does it directly. A note model requires each owner to prove something about their own state.
- **Is public state part of the application?** If yes, Aztec is the only one of the five with both in one transaction. Zcash and Railgun have a shielded pool and a boundary around it; Canton has no public state at all.
- **Who must be trusted or online for a read to succeed?** Note models answer "nobody"; the FHE model answers "a threshold committee"; Canton answers "nobody, but the data was distributed by policy rather than hidden by mathematics".

## Conclusion

Aztec's design follows from a single constraint: private execution must happen where the private data is, which is the user's device, and public execution must happen where the chain head is, which is the sequencer. Everything else — the ordering of private before public, the deferred and unilateral call model, delayed public state, portals that pull rather than push, kernel circuits that recurse once per call — is a consequence of that split.

The state model is Zcash's, extended to arbitrary contracts and paired with an EVM-like public tree. The costs are correspondingly different from an EVM chain's: proving time is paid by the user in gate counts on their own hardware, and the design pressures that produces run opposite to EVM instincts, since an extra private call costs more than a larger single one.

The leakage surface deserves the same attention as the cryptography. Public call arguments, a revealed `msg_sender`, and the visible count of public calls and L2 to L1 messages are all places where a correct contract can still fail at the thing it was built to do. The protocol supplies the tools to close them; it does not close them by default. Aztec is also explicitly unaudited and under development, and its own documentation advises against entrusting real secrets to it at this stage.

![Mindmap of Aztec covering its two execution environments, note and nullifier state model, account keys, note delivery, the transaction lifecycle, fees, L1 portals and what still leaks]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-08-aztec-privacy-protocol-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Note** | A unit of private state, held as an encrypted record by its owner; only a commitment to it is stored onchain. |
| **Nullifier** | A value derived from a note and its owner's nullifier key, emitted to mark the note spent without revealing which note it was. |
| **PXE** | The Private eXecution Environment: a client-side library that stores notes and keys, executes private functions and generates their proofs. |
| **AVM** | The Aztec Virtual Machine, executed by the sequencer for public functions against the public data tree. |
| **Kernel circuit** | The recursive circuit that processes one private call per iteration, accumulating and validating side effects across a transaction. |
| **Utility function** | An unconstrained offchain query that can read private and public state, is never part of a transaction, and carries no correctness guarantee. |
| **Note tagging** | The default discovery mechanism, deriving a per-message tag as `poseidon2(secret, index)` so a recipient can query for their own logs. |
| **Mana** | Aztec's unit of computational effort, split into data-availability and L2 dimensions, and paid in Fee Juice. |
| **Portal** | The L1 half of an application, paired with an L2 address, through which asynchronous messages cross between the chains. |
| **Transaction fingerprint** | The publicly observable shape of a transaction, notably the number of public calls and L2 to L1 messages, which padding does not currently hide. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A note can be spent only once. | Non-membership proof against the indexed nullifier tree before insertion. | The same nullifier could be inserted twice, permitting a double spend. |
| Only a note's owner can spend it. | The nullifier is derived from the owner's app-siloed nullifier key, proved in-circuit. | The nullifier derivation stops binding the owner's key to the note. |
| One contract cannot touch another's state. | The kernel siloes every storage slot and note hash with the contract address. | Siloing is bypassed, or two contracts derive a colliding siloed slot. |
| Private execution cannot observe current public state. | Private functions are proved against historical state before the sequencer runs. | A private function reads a `PublicMutable`, which the framework rejects at compile time. |
| A private function's arguments are never sent to the network. | Execution and proving happen entirely in the PXE; only proofs and side effects are sent. | The value is passed to an enqueued public call, where arguments are public. |
| Public state is written only by the sequencer. | Public writes are available only in the AVM; private code can enqueue but not write. | An enqueued public function lacks `#[only_self]` and becomes a public entrypoint. |
| A contract's own notes stay findable by their recipient. | An explicit delivery call with a mode the recipient can act on. | The returned message object is never delivered, and the note content is lost permanently. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| A private function cannot read the return value of a public call it enqueues. | Design for unilateral messages: split the flow across transactions, or move the decision into the public phase. |
| Creating a note returns a message that must be delivered explicitly. | Always call the delivery method, and treat the compiler's unused-value warning as an error in CI. |
| `enqueue` publishes the calling account's address. | Use `enqueue_incognito` where the sender must stay hidden, and have the callee read `maybe_msg_sender()`. |
| Reading a `PrivateMutable` nullifies and recreates the note. | Expect a read to cost a write and to contend between concurrent transactions; pick another state variable if that is wrong for the use case. |
| An extra private call adds roughly 101,000 gates of kernel overhead. | Prefer compile-time inlined `#[internal]` helpers over splitting logic into separate private calls; measure with `aztec profile gates`. |
| ECDSA, AES-128, Blake2s and Blake3 are unavailable in public functions. | Keep those operations in private functions; the transpiler fails at compile time rather than at runtime. |
| Fee Juice is non-transferable. | Do not model it as a token balance an application can move; use fee abstraction for sponsored transactions. |
| A cross-chain message is consumed by pulling, and the far side may never act. | Handle the failure path explicitly so users can recover funds locked on one side. |

## Frequently Asked Questions

**Q: Why can a private function read a `PublicImmutable` but not a `PublicMutable`?**

Private functions execute on the user's device before the sequencer processes the block, so the current value of mutable public state is not knowable at proving time — any value the circuit assumed could have changed by the time the transaction lands.

A `PublicImmutable` escapes this because it can be written only once. Once a circuit has proved the value was set at some point in the past, it knows the value cannot have changed since, so the historical reading is still correct. `DelayedPublicMutable` generalises the same trick to mutable values by making every write take effect only after a delay, which gives private execution a window in which the value is guaranteed stable.

**Q: What is the difference between a note commitment and a nullifier, and why are two structures needed?**

A note commitment is a hash of a note, inserted as a leaf in an append-only tree when the note is created. It proves the note exists without revealing its contents.

A nullifier is a separate value derived from the note *and* the owner's nullifier key, emitted when the note is spent. It goes into a different tree, which supports non-membership proofs.

Two structures are needed because the trees answer different questions and neither can answer both. The note hash tree answers "does this note exist?" and must be append-only, since editing a leaf in place would reveal that its owner transacted. The nullifier tree answers "has this note already been spent?", which is a non-membership query. Keeping them apart is also what decouples creating, updating and deleting private state, and what makes a nullifier unlinkable to its note without the owner's key.

**Q: A contract's private transfer function compiles, tests pass, and no assertion can be bypassed. What can still make it fail at its purpose?**

Leakage through the boundary with public execution. Three things to check:

- Every argument passed to an enqueued public function is published in clear, so a transfer that enqueues a public call with the recipient and the amount has revealed exactly what it was hiding.
- `enqueue` publishes the calling account's address unless `enqueue_incognito` is used and the callee reads `maybe_msg_sender()`.
- The number of public calls and of L2 to L1 messages is not padded, so two private entrypoints producing different counts are distinguishable to anyone watching the transaction pool.

None of these is a vulnerability in the usual sense, which is precisely why they survive a security review that is looking for stolen value or bypassed checks.

**Q: Why would splitting a large private function into two smaller ones make a transaction more expensive?**

Because the cost that dominates is not the function body but the kernel iteration around it. Every private call beyond the account entrypoint adds a `private_kernel_inner` iteration of roughly 101,000 gates, on top of about 290,000 gates of fixed overhead for init, reset and tail. Two smaller functions are two calls, so they pay that iteration twice.

This inverts the EVM intuition, where a `CALL` is cheap and factoring code out is close to free. The Aztec answer for readability without the cost is `#[internal]`, which is inlined at compile time and adds no kernel iteration at all.

**Q: Aztec, Zcash and Railgun all use per-owner notes with nullifiers. What actually distinguishes them?**

Scope and boundary, not the cryptographic core. Zcash shields payments in its own asset and has no general smart contracts. Railgun puts the same note model inside contracts on chains that already exist, so it inherits their composability but has a visible shield and unshield boundary that every interaction with an ordinary DeFi contract must cross.

Aztec extends the model to arbitrary contracts and pairs it with an EVM-like public state tree, so private and public execution happen in one transaction with no pool boundary between them. What it gives up is exactly what Railgun keeps: it is a separate chain with a separate language and cannot call an existing Solidity contract.

**Q: When would Zama's FHE model be the right choice over Aztec's note model, and why?**

When a contract must compute over values belonging to users who are not participating in the transaction. Because Zama's state is encrypted under one network key and evaluated homomorphically, a sealed auction can compare two bids, or a confidential token can move a balance, without either owner producing a proof about their own state. In a note model, each owner must be present to prove a transition over the notes they hold.

The cost is the read path and the failure mode. No party holds the key in full, so reading your own value requires an authorised round trip to a threshold committee that must be live and must agree; decryption becomes a protocol event rather than a local computation. A breach of that threshold is global and retroactive, whereas losing a key in a note model exposes one account.

## References

### Aztec protocol documentation

- [Aztec Developer Documentation](https://docs.aztec.network/)
- [State Management — notes, nullifiers and the hybrid model](https://docs.aztec.network/developers/docs/foundational-topics/state_management)
- [Private Execution Environment (PXE)](https://docs.aztec.network/developers/docs/foundational-topics/pxe)
- [Private Kernel Circuit](https://docs.aztec.network/developers/docs/foundational-topics/advanced/circuits/private_kernel)
- [Rollup Circuits](https://docs.aztec.network/developers/docs/foundational-topics/advanced/circuits/rollup_circuits)
- [Transactions and the transaction lifecycle](https://docs.aztec.network/developers/docs/foundational-topics/transactions)
- [Keys](https://docs.aztec.network/developers/docs/foundational-topics/accounts/keys)
- [Note Discovery](https://docs.aztec.network/developers/docs/foundational-topics/advanced/storage/note_discovery)
- [Note Delivery and delivery modes](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/note_delivery)
- [State Variables](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/state_variables)
- [Storage Slots](https://docs.aztec.network/developers/docs/foundational-topics/advanced/storage/storage_slots)
- [Fees](https://docs.aztec.network/developers/docs/foundational-topics/fees)
- [L1-L2 Communication (Portals)](https://docs.aztec.network/developers/docs/foundational-topics/ethereum-aztec-messaging)
- [Writing Efficient Contracts — gate counts and kernel overhead](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/advanced/writing_efficient_contracts)
- [AVM Cryptographic Compatibility](https://docs.aztec.network/developers/docs/foundational-topics/advanced/circuits/avm_compatibility)
- [Privacy Considerations](https://docs.aztec.network/developers/docs/resources/considerations/privacy_considerations)
- [Limitations](https://docs.aztec.network/developers/docs/resources/considerations/limitations)
- [Noir Language Documentation](https://noir-lang.org/docs/)
- [AztecProtocol/aztec-packages](https://github.com/AztecProtocol/aztec-packages) — the protocol, framework and tooling monorepo

### Comparison systems

- [Zama Protocol documentation](https://docs.zama.ai/protocol) — FHE coprocessor, gateway, threshold KMS and the ACL model
- [TFHE-rs](https://github.com/zama-ai/tfhe-rs) — the FHE library underlying the Zama protocol
- [Zcash Protocol Specification](https://zips.z.cash/protocol/protocol.pdf) — Sapling and Orchard note commitments, nullifiers and key derivation
- [Halo 2](https://zcash.github.io/halo2/) — the proof system used by Orchard, without a trusted setup
- [Canton Network documentation](https://docs.digitalasset.com/) — sub-transaction privacy, parties and synchronizers
- [Daml documentation](https://docs.daml.com/) — the contract language behind Canton's authorization model
- [RAILGUN documentation](https://docs.railgun.org/) — shielded balances, Broadcasters and viewing keys
- [Waku](https://waku.org/) — the messaging layer Railgun Broadcasters use

### Standards

- [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) — the fee-market design Aztec's mana pricing borrows from

### Related articles

- [Aztec Contract Standards — AIP-20, AIP-721, ARC-1155, ARC-403, AIP-4626 and the Escrow Standard]({{site.url_complet}}/2026/09/11/aztec-contract-standards-overview/)
- [AIP-20, the Aztec Token Standard, Compared with ERC-20 and ERC-7984]({{site.url_complet}}/2026/09/11/aip-20-aztec-token-standard-vs-erc-20-erc-7984/)
- [Partial Notes on Aztec — Deferred Completion and Private DeFi Composability]({{site.url_complet}}/2026/09/09/aztec-partial-notes-private-defi-composability/)
- [Aztec: A Privacy-First Layer 2 for Ethereum]({{site.url_complet}}/2025/10/29/aztec-architecture-overview/)
- [Native Account Abstraction on Aztec, Compared with ERC-4337]({{site.url_complet}}/2026/09/09/aztec-native-account-abstraction-vs-erc-4337/)
- [Zero-Knowledge Proofs in the Zama Protocol — What They Prove and Where They Are Verified]({{site.url_complet}}/2026/07/24/zero-knowledge-proofs-zama-protocol/)
- [Canton Network — Architecture, Privacy Model, and Comparison with Ethereum, Railgun, Zcash, Zama fhEVM, and Besu]({{site.url_complet}}/2026/05/12/canton-network-architecture/)
- [RAILGUN: Privacy Infrastructure for DeFi]({{site.url_complet}}/2025/10/28/railgun-overview/)
- [Understanding zk-SNARK: A Deep Dive into Zero-Knowledge Proofs]({{site.url_complet}}/2025/07/29/zk-snark-overview/)
- [Tornado Cash Circuits - Overview]({{site.url_complet}}/2025/11/19/tornado-cash-overview/)
