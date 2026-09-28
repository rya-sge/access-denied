---
layout: post
title: "Malachite Consensus on Arc — How Circle's L1 Finalises a Block, Compared with CometBFT, HotStuff and Gasper"
date:   2026-09-25
lang: en
locale: en-GB
categories: blockchain
tags: circle arc consensus malachite tendermint bft blockchain staking
description: "How Arc runs Malachite, a Tendermint-family BFT engine, over Reth, and how its rounds, proposers and validator sets compare with CometBFT, HotStuff and Gasper."
image: /assets/article/blockchain/circle/2026-09-25-malachite-consensus-arc-mindmap.png
isMath: false
---

[Arc](https://arc.network) is Circle's EVM-compatible Layer-1 blockchain, with USDC as the gas token and a permissioned set of institutional validators. A [previous article]({{site.url_complet}}/2026/09/25/arc-token-whitepaper-circle/) read the ARC token whitepaper against the node's code. This one looks at the part of that code that decides blocks.

Arc's consensus layer is [Malachite](https://github.com/circlefin/malachite), a Byzantine-fault-tolerant engine written in Rust. It was originally developed at Informal Systems and is now maintained by Circle. Malachite implements the Tendermint algorithm, so Arc has deterministic finality: a block is final the moment more than two thirds of the voting power has precommitted it, and there is no fork choice and no reorganisation.

What follows is taken from the source of `circlefin/arc-node` and from its design records (ADRs). It covers:

- how a height runs through the Engine API;
- where the timeouts come from;
- how proposers and validator sets are chosen;
- what the node does with misbehaviour evidence.

The last part compares the design with CometBFT, the HotStuff family, Ethereum's Gasper, Ouroboros and Solana's TowerBFT.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Malachite as Arc uses it

Arc splits the node in two, the way post-Merge Ethereum does:

- **Consensus layer (CL).** `arc-node-consensus` is a Malachite application.
- **Execution layer (EL).** `arc-node-execution` is a customised Reth node.

The two communicate through the standard Engine API (`forkchoiceUpdated`, `getPayload`, `newPayload`) over IPC or JWT-authenticated HTTP. Malachite knows nothing about the EVM: it orders opaque values, and the application turns those values into execution payloads.

![Arc consensus stack: the Malachite consensus binary drives Reth through the Engine API, persists certificates in redb with a WAL, signs through a Nitro Enclave remote signer, reads timeouts and validators from system contracts and gossips over libp2p]({{site.url_complet}}/assets/article/blockchain/circle/malachite-arc-stack-concept.png)

The dependency is Circle's fork of Malachite, pinned in `Cargo.toml` at tag `v0.8.0` (commit `72143f6c…` in `Cargo.lock`). Its crates are renamed with an `arc-` prefix (`arc-malachitebft-app-channel`, `arc-malachitebft-core-consensus`, and so on). Four integration choices define how Arc uses it:

- **Channel-based application API.** The node starts the engine with `start_engine(...)` and answers Malachite's messages in one loop (`crates/malachite-app/src/app.rs`). The messages are `ConsensusReady`, `StartedRound`, `GetValue`, `ReceivedProposalPart`, `Decided`, `Finalized`, `ProcessSyncedValue` and `RestreamProposal`. This fork splits the end of a height into two messages, `Decided` and `Finalized`.
- **`ValuePayload::ProposalAndParts`.** The proposer gossips a signed proposal message and also streams the block itself in parts. The comment in `hardcoded_config.rs` notes that Malachite's default is `PartsOnly`.
- **No vote extensions.** `ExtendVote` returns `None` and `VerifyVoteExtension` accepts everything, with the comment `// Currently not supported`.
- **Ed25519 signatures.** `type SigningScheme = Ed25519`. A validator can keep its key in `arc-remote-signer`, a gRPC service that holds the key inside an AWS Nitro Enclave.

## One round, three votes

Malachite runs the Tendermint round. Each round has one proposer and three phases:

1. **Propose.** The proposer broadcasts a block. The others wait up to `timeout_propose` for it.
2. **Prevote.** Each validator prevotes for the block if it received a valid one in time, and prevotes nil otherwise. Seeing more than two thirds of prevotes for the same block, called a *polka*, makes a validator lock on that block.
3. **Precommit.** A validator that saw a polka precommits the block, and otherwise precommits nil. More than two thirds of precommits for one block decides it.

If the round ends without a decision, the next round starts with the next proposer, and the timeouts grow.

![Tendermint round on Arc: propose with a linear timeout, prevote for the block or nil (nil on timeout, invalid block or timestamp skew), precommit after a polka, then decide on two-thirds precommits or move to the next round]({{site.url_complet}}/assets/article/blockchain/circle/malachite-round-state-machine.png)

Safety comes from the lock. A validator locked on a block precommits only that block unless it later sees a polka for something else in a higher round. So two conflicting blocks can never both collect two thirds of precommits while fewer than one third of the voting power is Byzantine. The Arc application configures nothing here: locking and proof-of-lock rules are Malachite's. The only trace in the app is the `valid_round` field in the proposal and the handler that re-streams a block that was already seen in an earlier round.

The result is a **commit certificate**: the list of more than two thirds of precommits for the block. On Arc it is a `repeated CommitSignature { validator_address, signature }` (`crates/types/proto/arc/sync/v1/sync.proto`), not an aggregated signature. After the decision, a `Finalized` step collects extra precommits that arrive late and stores them as an "extended" certificate. A scaffold for BLS aggregation exists only as commented-out code.

### Timeouts live onchain

The timeouts are not in a node configuration file. The node reads them from the **`ProtocolConfig`** system contract at `0x3600…0001` through `consensusParams()`. The contract returns a struct of `uint16` millisecond values:

| Parameter | Mainnet genesis | Client-side bounds (`consensus_params.rs`) |
|---|---|---|
| `timeoutProposeMs` | 3000 | 500 ms – 30 s |
| `timeoutPrevoteMs` | 1000 | 250 ms – 10 s |
| `timeoutPrecommitMs` | 1000 | 250 ms – 10 s |
| each `…DeltaMs` | 500 | 50 ms – 1 s |
| `timeoutRebroadcastMs` | 5000 | 1 s – 30 s |
| `targetBlockTimeMs` | 500 | 0 – 1 s |

The node maps these values to Malachite's `LinearTimeouts`. Each round, a timeout grows by its delta; `crates/eth-engine/src/deadline.rs` notes that Malachite grows the propose budget "by `propose_delta` every round". A value outside the client bounds is logged and replaced by the default. If the contract read fails, the node falls back to `ConsensusParams::default()`.

The contract's single `controller` can change all of these with `updateConsensusParams` or `updateTimeoutProposeMs`. Values are read at the decided height and apply from the next height on.

**Target block time.** `targetBlockTimeMs` does not bound a timeout. It makes the node pause briefly after finalising a block before starting the next height, and the pause is skipped while the node is catching up. This is why the testnet produces a block roughly every 0.48 s even though a round could finish faster. It also qualifies a sentence in the documentation, which says Malachite "delivers optimistic responsiveness … with no artificial delays or extra timeouts". On the happy path the network does run at its own speed, but the application then deliberately waits until the 500 ms target block time has elapsed.

## A height through the Engine API

The application maps each Malachite message to Engine API calls. The sequence below follows a height from start to finish.

![Sequence of one Arc height: the proposer builds a payload with forkchoiceUpdated and getPayload, streams it in signed 128 KiB chunks, validators check the timestamp and run newPayload, vote, store the certificate, set head, safe and finalized to the block, then read the next validator set]({{site.url_complet}}/assets/article/blockchain/circle/malachite-arc-height-lifecycle-sequence.png)

- **`StartedRound`.** The node records the round and its proposer, and validates proposal parts that arrived early for this round. After a restart it also re-sends to the EL, with `newPayload`, any blocks that were not yet decided. A metric (`consensus_round_missed`) counts rounds lost per proposer.
- **`GetValue`** runs on the proposer only:
  - If the proposer already built a block for this height and round, it proposes that same block again. The code comment gives the reason: "to adhere to the crash-recovery model, the same block must be re-proposed".
  - Otherwise it calls `forkchoiceUpdated(parent, attributes)` then `getPayload`, and checks its own block with `newPayload`. In the attributes, `prev_randao` is zero, the withdrawals list is empty, and `parent_beacon_block_root` is set to the parent hash.
  - The whole sequence must finish within the round's propose timeout. If it does not, the node logs "Proposer timed out", proposes nothing, and the round times out.
- **`ReceivedProposalPart`** runs on the other validators. Parts for a past height are dropped. Parts for a future round are stored as pending, up to a cap. Parts for the current round are checked for proposer and signature, then the block goes through `newPayload`. A block judged invalid is kept and marked invalid.
- **`Decided`.** The node looks up the block by hash and checks that the payload matches the decided value; a mismatch halts the node. It then stores the certificate and the block before it tells the EL anything, so that the decided height is never behind the finalised block. Finally it calls `forkchoiceUpdated` with no payload attributes. **Head, safe and finalized are set to the same hash** (`engine_ipc.rs`), which is the Engine API form of "no reorgs".
- **`Finalized`.** The node stores any misbehaviour evidence, extends the certificate, and starts the next height.

### Block dissemination (ADR-0002)

An `ExecutionPayloadV3` can exceed gossip message-size limits, so ADR-0002 defines a stream format:

- **`Init`** carries the height, the round and the proposer.
- **`Data`** messages each carry a chunk of the SSZ-encoded payload, 128 KiB at most.
- **`Fin`** carries an Ed25519 signature over `Keccak256(height ‖ round ‖ chunks)`.

The ADR rejected three alternatives: atomic messages, erasure coding and request/response. It admits two costs of the chosen design: there is no retransmission, and validation happens late, once the whole stream has arrived. The code matches the ADR on hashing and chunk size (`streaming.rs`, `CHUNK_SIZE = 128 * 1024`). It differs on limits: the ADR specifies 64 streams per peer and 100 in total, while the code sets `MAX_STREAMS_PER_PEER = 4` and has no global constant.

### Proposer timestamps (ADR-0006)

The proposer sets the block timestamp to `max(parent.timestamp, now())`. A validator **prevotes nil** when the timestamp is more than 30 seconds ahead of its own clock (`ARC_PROPOSER_CLOCK_SKEW_THRESHOLD_SECS = 30` in `skew_gate.rs`). There is no lower bound, and the ADR states that a validator without an NTP-synchronised clock "is considered byzantine".

Two design decisions stand out:

- **The check applies only when voting.** Its result is never stored as the block's validity, so a node that syncs a decided block later adopts it whatever its own clock says. The check used to live in `engine_newPayload`, and it was moved out because Reth's invalid-headers cache stalled nodes that had rejected a block for a transient reason.
- **Tendermint's BFT Time was rejected.** BFT Time derives the timestamp from the median of the voters' timestamps. The ADR rejects it as incompatible with a planned BLS aggregation of votes.

The ADR bounds the impact to liveness: "a malicious proposer can burn its own turn, and no more".

## Who proposes, and who votes

The validator set lives in a `ValidatorRegistry` contract at `0x3600…0002`, which only `PermissionedValidatorManager` can modify. An owner registers validators, and controllers set voting power up to a cap chosen by the owner. The mainnet genesis registers 11 validators with 2000 voting power each.

**When the set changes.** The CL reads the set with an `eth_call` to `getActiveValidatorSet()` **at block H-1**. The code comment explains why: "the set active at height H is the one committed after executing H-1". A registry change executed in block H therefore takes effect at height H+1. The decoder drops validators that are inactive or have zero voting power, and an empty set is a fatal error. The registry itself refuses to zero or remove the last validator with positive power.

**Proposer selection is plain rotation.** It is `(height - 1 + round) % n` (`crates/types/src/proposer.rs`), over a list sorted by voting power in descending order and then by address. Voting power weighs votes towards the two-thirds quorum; it has no effect on how often a validator proposes. As long as every validator has the same power, as at genesis, this makes no difference. If powers ever diverge, as the whitepaper's stake-weighted proof-of-stake would require, a validator holding 5% of the power would still propose one block in *n*.

**The one-third assumption is not enforced onchain.** The node's code contains no check that a single validator holds less than one third of the power. The only guard is in the operator script, `ValidatorManagement.s.sol`: `require(_highestVotingPower * 3 < _totalVotingPower, ...)`. Its `updateVotingPowerUnsafe` variant skips that check.

## Persistence, sync and restart

- **Store.** Certificates, decided and undecided blocks, pending proposal parts, misbehaviour evidence and invalid payloads live in `arc-consensus-db`, built on **redb**. Malachite's write-ahead log is at `<home>/wal/consensus.wal`, and it is replayed five seconds after start.
- **Restart.** On startup the CL compares its store with the EL. It replays into the EL any payload the EL is missing, and falls back to checkpoint sync if a payload is gone. An EL that is *ahead* of the CL is a fatal error.
- **Peer-to-peer sync.** Malachite's value sync serves decided blocks with their certificates, in batches of 10 with 5 parallel requests. An imported block is checked against the EL but not against the clock. A peer that serves a bad block is penalised.
- **RPC sync.** Follow nodes, which do not vote, fetch certificates and payloads over HTTP or WebSocket from trusted endpoints. They check the signatures against their own copy of the validator set.
- **Networking.** Gossipsub carries three topics: `/consensus`, `/proposal_parts` and `/liveness`. Since v0.7.0, mainnet uses Arc-branded protocol IDs (`/arc/consensus/v1`, `/arc/sync/v1`, …), so an older node can no longer peer with a newer one. Testnet keeps Malachite's default IDs.

### Misbehaviour is recorded, not punished

Malachite detects double votes and double proposals and passes them to the application in `Finalized`. Arc stores them in a `misbehavior_evidence` table and serves them at `GET /misbehavior-evidence`. Nothing else happens: the code, the contracts and the documentation contain no slashing and no jailing. The deterrent is the one the documentation names, "institutional accountability", meaning the owner can remove an identified operator. The node has no automatic penalty.

## Liveness and halting

Two figures bound the fault tolerance:

- **Safety** holds as long as less than one third of the voting power is Byzantine.
- **Liveness** holds as long as more than two thirds are online and honest.

If more than one third stops, the chain halts; nothing ever reverts. The code relies on this: a proposer whose block building times out simply produces nothing, and "the round times out and a later proposer's block gets decided". The node can also stop on purpose:

- **Chain anomaly.** A decided value that does not match the stored payload triggers `HaltAndWait`.
- **Coordinated upgrade.** An operator can set `ARC_HALT_AT_BLOCK_HEIGHT`: the node saves its store, waits ten seconds, then halts at that height.

The documentation claims under 350 ms finality and more than 3,000 TPS with 20 globally distributed validators, and more than 10,000 TPS with 4. These are benchmark figures, not measurements of mainnet. The roadmap lists multiple proposers, a reduction from "three rounds to two", and a "potential" move to permissioned proof-of-stake.

## Comparison with other consensus protocols

Malachite belongs to the family of classical BFT protocols descended from PBFT: a known validator set, votes in rounds, a quorum of more than two thirds, and immediate finality. The table places Arc next to a close relative (CometBFT), a protocol that differs in how leaders are replaced (HotStuff, as used by Hyperliquid), and protocols built on fork choice.

| | Arc (Malachite) | CometBFT (Cosmos) | HotStuff family (e.g. HyperBFT) | Ethereum (Gasper) | Cardano (Ouroboros Praos) | Solana (TowerBFT) |
|---|---|---|---|---|---|---|
| Family | Tendermint BFT | Tendermint BFT | Leader-based BFT, linear view change | Fork choice (LMD-GHOST) + finality gadget (Casper FFG) | Longest chain, PoS | PoS votes with lockouts on a PoH sequence |
| Finality | Deterministic, per block | Deterministic, per block | Deterministic, after a chain of certified rounds | Economic, after two epochs (about 13 minutes) | Probabilistic, bound k = 2160 blocks | Optimistic confirmation at ⅔ stake; "rooted" after 32 votes |
| Reorganisations | Never | Never | Never after commit | Possible before finality | Possible within k | Possible before confirmation |
| Leader selection | Round-robin, unweighted | Weighted round-robin by voting power | Rotating leader per view, stake-weighted on Hyperliquid | Random, stake-weighted per slot | Private VRF lottery per slot | Stake-weighted leader schedule per epoch |
| Validator set | Permissioned, owner-managed contract | Staked, top-N by bonded stake | Staked | Permissionless, 32 ETH deposit | Permissionless pools | Permissionless |
| Set change takes effect | H+1 | H+2 | Protocol-specific (epochs) | Activation queue, epochs | Snapshot two epochs ahead | Per epoch |
| > ⅓ offline | Halts | Halts | Halts | Keeps producing blocks; inactivity leak restores finality | Keeps producing blocks | Keeps producing blocks, without confirmation |
| Misbehaviour | Evidence stored, no penalty | Evidence goes to the application; Cosmos SDK slashes and jails | Protocol-specific (Hyperliquid jails unresponsive validators) | Protocol slashing | No slashing | No automatic slashing |
| Signatures in the certificate | List of Ed25519 signatures | List of Ed25519 signatures | Quorum certificate (threshold signature in the paper) | BLS aggregates | Single block-producer signature (KES) | Individual votes as transactions |

### Arc against CometBFT

CometBFT is the algorithm's reference production implementation, and most of the differences are choices the Arc team made. Five are worth noting:

- **Proposer weighting.** CometBFT gives each validator a proposer priority that grows with its voting power, so a validator with twice the power proposes twice as often. Arc rotates without weighting.
- **Validator updates.** In CometBFT a set change returned by the application at height H applies at H+2. Arc applies it at H+1, because the CL reads the registry from the state after H-1.
- **Block time.** In CometBFT the interval between blocks mostly comes from a commit timeout (historically `timeout_commit`). Arc uses a target block time from the system contract.
- **Block parts.** CometBFT splits blocks into 64 KiB parts authenticated by a Merkle proof. Arc streams 128 KiB chunks and signs the whole stream once in `Fin`.
- **Application interface.** CometBFT exposes ABCI++, with vote extensions, `PrepareProposal` and `ProcessProposal`. Arc's application is the Engine API, and vote extensions are disabled.

The last difference matters most. Arc is closer to an Ethereum consensus client than to a Cosmos chain: the EL is a standard Reth node, and the consensus layer could in principle be replaced without touching execution.

### Arc against HotStuff

HotStuff (Yin et al., 2019) changes how leaders are replaced. In Tendermint, a new proposer after a failed round must wait for the timeout to be sure it has seen the highest lock. HotStuff adds a phase so that a new leader can move at network speed as soon as it has collected a quorum of messages. This property is called *optimistic responsiveness*. HotStuff also keeps communication linear by relaying votes through the leader as a quorum certificate.

Hyperliquid's HyperBFT, [described in an earlier article]({{site.url_complet}}/2026/09/02/hyperliquid-protocol-architecture/), is a HotStuff variant with stake-weighted leaders. Arc's roadmap item "three rounds to two" goes the other way, towards fewer voting phases on the happy path.

### Arc against fork-choice protocols

Gasper, Ouroboros and TowerBFT favour availability: the chain keeps growing when a large part of the validators disappears, and finality comes later or only with a probability. Arc, like every Tendermint chain, makes the opposite trade: a block is final as soon as it is decided, and the chain stops rather than risk a fork. For a payments chain run by known institutions this is the expected choice. It also means that more than one third of the operators, or of their cloud providers, going offline stops USDC settlement on Arc entirely.

[Cardano's Ouroboros]({{site.url_complet}}/2026/07/16/ouroboros-proof-of-stake/) shows the other end of the range. Anyone can run a pool, leaders are elected privately by VRF, and settlement is only certain after k = 2160 blocks, about 12 hours.

## Conclusion

Arc's consensus is Tendermint implemented by Malachite, integrated with Reth through the Engine API. It is run by a small permissioned validator set that has no economic security yet.

- **The engine.** Circle's Malachite fork `v0.8.0` runs with the channel API and `ProposalAndParts`, with no vote extensions and with Ed25519 certificates made of individual signatures.
- **Rounds.** The three voting phases and their linear timeouts are read from `ProtocolConfig`, which one controller account can change. A 500 ms target block time paces the heights.
- **Integration with execution.** The proposer builds blocks with `forkchoiceUpdated` and `getPayload`, validators check them with `newPayload`, and after a decision head, safe and finalized are set to the same block. Blocks are streamed in 128 KiB chunks, and a 30-second clock-skew gate applies at vote time only.
- **Validators.** The set is read at H-1 and takes effect at H+1. Proposers rotate without weighting by voting power, and the one-third bound is guarded only by an operator script.
- **Accountability.** Double votes and double proposals are stored and served over HTTP. No slashing exists.
- **Against other protocols.** Arc keeps CometBFT's safety model but rotates proposers without weighting and changes validator sets one height sooner. It favours safety over the availability of Gasper, Ouroboros and TowerBFT. Stake-weighted proposers would require a new `ProposerSelector`.

![Mindmap of Malachite consensus on Arc covering the engine, the round and its timeouts, validator selection, the coupling with the execution layer, operations and the comparison with CometBFT, HotStuff, Gasper, Ouroboros and TowerBFT]({{site.url_complet}}/assets/article/blockchain/circle/2026-09-25-malachite-consensus-arc-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Malachite** | A Rust implementation of Tendermint BFT consensus, originally developed at Informal Systems and maintained by Circle for Arc. |
| **Height** | The position of a block in the chain. Each height is decided once, possibly after several rounds. |
| **Round** | One attempt to decide a height, with one proposer and propose, prevote and precommit phases. |
| **Polka** | More than two thirds of prevotes for the same value in one round, which makes validators lock on that value. |
| **Commit certificate** | The set of more than two thirds of precommits that proves a block was decided; on Arc, a list of Ed25519 signatures. |
| **Engine API** | The JSON-RPC interface through which a consensus client drives an Ethereum execution client (`forkchoiceUpdated`, `getPayload`, `newPayload`). |
| **ProtocolConfig** | Arc's system contract at `0x3600…0001` holding consensus timeouts, target block time and fee parameters. |
| **ValidatorRegistry** | Arc's system contract at `0x3600…0002` holding the active validators and their voting power. |
| **LinearTimeouts** | Malachite's timeout model, in which each phase's timeout grows by a fixed delta per round. |
| **Optimistic responsiveness** | The property that a new leader can make progress at network speed without waiting a worst-case timeout; HotStuff has it, classical Tendermint does not in the view-change case. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A decided block is never reverted. | Tendermint locking with fewer than ⅓ Byzantine voting power; `forkchoiceUpdated` sets head = safe = finalized. | One validator or a colluding group reaches ⅓ of the voting power (only an operator script checks this). |
| The CL is never behind the EL's finalised block. | `Decided` stores the certificate and block before calling `forkchoiceUpdated`; an EL ahead of the CL at startup is fatal. | The storage order in `decided.rs` changes. |
| A proposer re-proposes the same block after a crash in the same round. | `GetValue` reuses the stored block for (height, round). | The undecided-block store is lost or wiped between restart and proposal. |
| The validator set used at height H is the registry state after H-1. | `getActiveValidatorSet()` called with `consensus_height - 1`. | The query height changes, which would split nodes onto different sets. |
| Timeouts stay within sane ranges. | `enforce_bounds` in `consensus_params.rs` resets out-of-range values to defaults. | The bounds are removed; a bad `ProtocolConfig` value could stall rounds. |
| A proposer with a runaway clock cannot move time forward by more than 30 s. | Skew gate: prevote nil on `timestamp > local + 30 s`. | Validators run without NTP, or the threshold is raised. |

## Frequently Asked Questions

**Q: What is Malachite, and how does it relate to Tendermint?**

Malachite is a Rust library that implements the Tendermint consensus algorithm: rounds with propose, prevote and precommit, locking on a polka, and decision at more than two thirds of precommits. Informal Systems developed it and Circle now maintains it, and Arc uses Circle's fork at tag `v0.8.0` as its consensus layer.

**Q: How does Arc turn a Malachite decision into a finalised EVM block?**

The steps are:

- The proposer builds the block by calling `forkchoiceUpdated` with payload attributes and then `getPayload` on Reth.
- Other validators validate it with `newPayload` before voting.
- When Malachite reports `Decided`, the node stores the certificate and block, then calls `forkchoiceUpdated` with head, safe and finalized all set to the decided hash.

Because those three pointers are always equal, the EL never sees a reorg.

**Q: Why does a validator with more voting power not propose more often on Arc?**

Proposer selection is `(height - 1 + round) % n` over the sorted validator list. Voting power only counts towards the two-thirds quorum.

CometBFT, by contrast, uses weighted round-robin, in which proposer frequency is proportional to power. Supporting the stake-weighted selection described in the ARC whitepaper would require a new proposer-selection algorithm in the consensus application.

**Q: A controller sets `timeoutProposeMs` to 100 in `ProtocolConfig`. What happens?**

Nodes read the value at the decided height and pass it through `enforce_bounds`. 100 ms is below the 500 ms minimum for the propose timeout, so each node logs the violation and uses the 3 s default instead. The contract itself only requires the value to be positive, so the protection sits in the client, not onchain.

**Q: What happens to Arc if four of its eleven equally weighted validators go offline?**

Four of eleven is more than one third of the voting power, so the remaining seven cannot form a quorum of more than two thirds. Rounds time out one after another, with timeouts growing linearly, and no block is decided. No block is reverted either. Once enough validators return, consensus resumes at the same height.

Ethereum would behave differently: it would keep producing blocks and use the inactivity leak to regain finality.

**Q: Why did Arc choose a 30-second skew gate instead of Tendermint's BFT Time?**

BFT Time derives the block time from the median of voters' timestamps. ADR-0006 rejects it as incompatible with a planned BLS vote aggregation.

The gate instead makes a validator prevote nil on a block timestamped more than 30 s in its future. The check applies only at vote time, so a node that syncs the block later is not affected. The worst a malicious proposer can do is waste its own turn.

**Q: Is double signing on Arc punished?**

No. Malachite detects double votes and double proposals, and Arc stores them and serves them at `/misbehavior-evidence`. No slashing or jailing exists in the node or contracts. The only recourse is the registry owner removing the validator, which is the "institutional accountability" model described in the documentation.

## References

### Analyzed source

- [circlefin/arc-node](https://github.com/circlefin/arc-node) — analyzed at commit [`6e764023ee6515fe70573e123ed2db912a7207b4`](https://github.com/circlefin/arc-node/tree/6e764023ee6515fe70573e123ed2db912a7207b4) (10 commits after v0.8.0), 2026-09-25. Malachite dependency: [circlefin/malachite](https://github.com/circlefin/malachite) tag `v0.8.0`, commit `72143f6c99a98452b587e1c392bdb80944eb2232` (from `Cargo.lock`; the fork's source was not read)
- [circlefin/arc-remote-signer](https://github.com/circlefin/arc-remote-signer) — analyzed at commit [`a9e9fdb48c1e96a6c3fb875aba3d341e6a8af1a6`](https://github.com/circlefin/arc-remote-signer/tree/a9e9fdb48c1e96a6c3fb875aba3d341e6a8af1a6), 2026-09-25

### Arc documentation and design records

- [Arc documentation — Consensus layer](https://docs.arc.io/arc/concepts/consensus-layer)
- [Arc documentation — Deterministic finality](https://docs.arc.io/arc/concepts/deterministic-finality)
- [Arc documentation — System overview](https://docs.arc.io/arc/concepts/system-overview)
- `docs/adr/0002-block-dissemination-protocol.md` and `docs/adr/0006` (proposer timestamp validation) in circlefin/arc-node at the commit above

### Consensus protocols

- [The latest gossip on BFT consensus](https://arxiv.org/abs/1807.04938) (Buchman, Kwon, Milosevic, 2018), the Tendermint algorithm
- [HotStuff: BFT Consensus in the Lens of Blockchain](https://arxiv.org/abs/1803.05069) (Yin, Malkhi, Reiter, Gueta, Abraham, 2019)
- [Combining GHOST and Casper](https://arxiv.org/abs/2003.03052) (Buterin et al., 2020), Ethereum's Gasper
- [CometBFT documentation](https://docs.cometbft.com/)
- [Engine API specification](https://github.com/ethereum/execution-apis/tree/main/src/engine)

### Related articles

- [The ARC Token Whitepaper — Circle's Coordination Asset Read Against the Arc Node]({{site.url_complet}}/2026/09/25/arc-token-whitepaper-circle/)
- [The Hyperliquid Protocol - HyperCore, HyperEVM and Onchain Perpetual Mechanics]({{site.url_complet}}/2026/09/02/hyperliquid-protocol-architecture/)
- [Ouroboros: How Cardano Reaches Consensus with Proof of Stake]({{site.url_complet}}/2026/07/16/ouroboros-proof-of-stake/)
- [Canton Network — Architecture, Privacy Model, and Comparison with Ethereum, Railgun, Zcash, Zama fhEVM, and Besu]({{site.url_complet}}/2026/05/12/canton-network-architecture/)
- [Solana Staking - Overview]({{site.url_complet}}/2025/11/07/solana-staking-overview/)
