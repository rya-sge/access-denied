---
layout: post
title: "A Categorized Guide to Cardano Improvement Proposals"
date:   2026-07-16
lang: en
locale: en-GB
categories: blockchain
tags: cardano cip governance standards ledger plutus wallets metadata
description: A categorized tour of the Cardano Improvement Proposals. Explains the CIP and CPS processes, the status lifecycle, and walks through all nine official categories (Meta, Ledger, Consensus, Network, Wallets, Tokens, Metadata, Plutus, Tools) with their notable proposals.
image: /assets/article/blockchain/cardano/cardano-cip-categories.png
isMath: false
---

The Cardano Improvement Proposal repository is the written record of how Cardano changes. It holds roughly 140 CIPs and 21 Cardano Problem Statements, spanning wallet interfaces, token standards, ledger rules, the Plutus virtual machine, consensus upgrades, and the governance system. Read as one flat list it is hard to navigate, but the proposals carry an official `Category` field, and using it turns the repository into something a reader can actually orient inside. This article explains what a CIP is, how its status evolves, and then walks through each of the nine categories with its most important proposals. Figures were taken from the [cardano-foundation/CIPs](https://github.com/cardano-foundation/CIPs) repository at commit `23b89bd`; counts and statuses will drift as new proposals are merged.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What a CIP is, and what a CPS is

A **Cardano Improvement Proposal (CIP)** is a formalized design document describing a change to the Cardano ecosystem, its processes, or its environment. The format and the process that governs it are themselves defined by a CIP, [CIP-0001](https://cips.cardano.org/cip/CIP-1). Because the proposals are text files in a version-controlled repository, their history is also the historical record of significant decisions about the platform.

A **Cardano Problem Statement (CPS)** is the companion document type, defined by [CIP-9999](https://cips.cardano.org/cip/CIP-9999). A CPS states a problem, its context, and its constraints without prescribing a solution. It exists so that discussion can start from an agreed problem rather than a single proposed answer, and several CIPs can then be offered as competing or complementary solutions to the same CPS. The two link to each other: a CPS lists its `Proposed Solutions`, and a CIP names the CPS it is a `Solution To`. At the reference commit there are 21 CPSs, on subjects such as smart tokens, wallet connectors, post-quantum signatures, and transaction throughput.

The repository has a simple shape. A master `README.md` indexes every proposal by number, title, and status. Each proposal lives in its own directory (`CIP-XXXX/` or `CPS-XXXX/`) containing a `README.md` with the proposal text and any supporting assets. Two directories are worth bookmarking: `CIP-0001/` defines the CIP process, and `CIP-9999/` defines the CPS process.

![Component diagram of the CIP repository structure showing the index, per-proposal directories, process documents, and templates]({{site.url_complet}}/assets/article/blockchain/cardano/cip-repository-structure-concept.png)

## The status lifecycle

Every CIP header carries a `Status`, and there are only three values: `Proposed`, `Active`, and `Inactive`. At the reference commit the split across the 140 CIPs is 75 `Proposed`, 62 `Active`, and 3 `Inactive`.

There is deliberately **no "Draft" status**. A proposal that has not been merged is a draft by virtue of still being an open pull request, and it should already declare the status it targets on acceptance. Once merged, its status moves through the following states:

- **Proposed**: the proposal meets the essential criteria (complete required sections, editor-satisfactory quality, established technical soundness, and a valid Path to Active) but has not yet taken effect. It describes an accepted design, not a realized one.
- **Active**: the proposal has taken effect according to its own `Path to Active` section. What that requires depends on the proposal: released software for a tool, a live mainnet implementation for a protocol change, or visible community adoption for an ecosystem standard. An Active CIP is treated as complete and production-ready and is not substantially revised afterward, though a later CIP can supersede it.
- **Inactive**: the proposal was abandoned, lost interest, or was superseded by another. Two of the three Inactive CIPs at the reference commit are superseded rather than abandoned, for example CIP-0058 (Plutus Bitwise Primitives), replaced by CIP-0121 and CIP-0122.

![State diagram of the CIP status lifecycle from an unmerged draft pull request through Proposed, Active, and Inactive]({{site.url_complet}}/assets/article/blockchain/cardano/cip-lifecycle-states.png)

Reading the status is essential before citing a CIP. A number being present in the repository says only that a design was written down. Whether it is a ratified standard, a live protocol feature, or a proposal still under discussion is exactly the distinction the status encodes.

## The category system

Each CIP header also carries a `Category`, and [CIP-0001](https://cips.cardano.org/cip/CIP-1) fixes the set. The nine categories and their counts at the reference commit:

| Category | Count | What it covers (per CIP-0001) |
|----------|------:|-------------------------------|
| **Meta** | 6 | Meta-CIPs that serve another category or the process itself. |
| **Ledger** | 25 | The Cardano ledger; follows the process in CIP-0084. |
| **Consensus** | 4 | The consensus layer and its algorithms. |
| **Network** | 3 | Cardano's network protocols and applications. |
| **Wallets** | 26 | Standardization across wallets (hardware, full-node, or light). |
| **Tokens** | 9 | Fungible and non-fungible tokens and minting policies. |
| **Metadata** | 21 | On-chain and off-chain metadata proposals. |
| **Plutus** | 25 | Changes or additions to Plutus; follows the process in CIP-0035. |
| **Tools** | 21 | A broad category for ecosystem features that fit nowhere else. |

The categories fall into three loose bands. Four of them (Ledger, Consensus, Network, Plutus) touch the protocol internals and change how nodes agree and how scripts execute. Four more (Wallets, Tokens, Metadata, Tools) are application and ecosystem standards that let independently built software interoperate. The last, Meta, governs the process itself. Note that two categories run their own sub-process: Plutus changes follow CIP-0035 and ledger changes follow CIP-0084, reflecting that those areas need review by the teams who maintain the respective implementations.

The rest of the article takes the categories one at a time. Each table lists a curated selection rather than every member, chosen for adoption and illustrative value, with the status shown so the mature standards are distinguishable from open proposals.

## Meta

Meta-CIPs describe the process rather than the technology. They are the documents to read first if you intend to contribute.

| CIP | Title | Status |
|-----|-------|--------|
| 0001 | CIP Process | Active |
| 9999 | Cardano Problem Statements | Active |
| 0035 | Plutus Core Evolution | Active |
| 0084 | Cardano Ledger Evolution | Active |
| 0059 | Terminology Surrounding Core Features | Active |
| 0052 | Cardano audit best practice guidelines | Proposed |

CIP-0035 and CIP-0084 are the notable pair here: they carve out sub-processes for the two areas (Plutus and the ledger) where a change needs sign-off from the implementation teams, which is why proposals in those categories are reviewed differently from, say, a wallet standard.

## Ledger

The Ledger category is where accounting rules, addresses, protocol parameters, staking rewards, and governance live. It is the largest protocol-internal category.

| CIP | Title | Status |
|-----|-------|--------|
| 1694 | A First Step Towards On-Chain Decentralized Governance | Active |
| 0019 | Cardano Addresses | Active |
| 0009 / 0028 / 0055 | Protocol Parameters (Shelley / Alonzo / Babbage eras) | Active |
| 0040 | Collateral Output | Active |
| 0080 | Transaction Serialization Deprecation Cycle | Active |
| 0118 | Nested Transactions | Proposed |
| 0181 | Remove DRep Requirement for Reward Withdrawals | Proposed |

[CIP-1694](https://cips.cardano.org/cip/CIP-1694) is the headline document: it defines the Conway-era governance model, including delegated representatives (DReps), the constitutional committee, stake pool operators as a voting body, and the treasury. CIP-0019 is the reference for how addresses are structured. The protocol-parameter CIPs (one per ledger era) record the tunable values that shape fees, block sizes, and staking, and are useful whenever a value needs to be traced to its origin.

## Consensus

The Consensus category is small but among the most forward-looking, since it holds the proposed evolutions of the Ouroboros protocol family. Every entry is currently `Proposed`.

| CIP | Title | Status |
|-----|-------|--------|
| 0140 | Ouroboros Peras - Faster Settlement | Proposed |
| 0164 | Ouroboros Linear Leios - Greater transaction throughput | Proposed |
| 0161 | Ouroboros Phalanx - Breaking Grinding Incentives | Proposed |
| 0177 | Ouroboros Tachys - Faster Cardano partner chains | Proposed |

These map onto the named research lines: Peras targets faster settlement, Leios targets throughput, Phalanx addresses randomness-grinding incentives, and Tachys targets partner chains. Their `Proposed` status is the important caveat: they are designs under active research, not shipped features.

## Network

The Network category covers the peer-to-peer and data-distribution layers. It is the smallest category, with three proposals.

| CIP | Title | Status |
|-----|-------|--------|
| 0137 | Decentralized Message Queue | Proposed |
| 0150 | Block Data Compression | Proposed |
| 0155 | SRV registry | Proposed |

These concern how nodes exchange and encode data rather than what the data means. Like Consensus, the category is entirely `Proposed` at the reference commit.

## Wallets

Wallets is the largest category overall, which reflects how much of Cardano's usability depends on wallets agreeing on shared conventions. It spans key derivation, hardware-wallet interoperability, URI schemes, and the browser bridge that dApps use to talk to wallets.

| CIP | Title | Status |
|-----|-------|--------|
| 0030 | Cardano dApp-Wallet Web Bridge | Active |
| 0095 | Web-Wallet Bridge - Conway ledger era | Active |
| 1852 | HD Wallets for Cardano | Active |
| 1854 | Multi-signature HD Wallets | Active |
| 0105 | Conway era Key Chains for HD Wallets | Active |
| 0003 / 0011 | Wallet key generation / Staking key chain for HD wallets | Active |
| 0013 | Cardano URI Scheme | Proposed |

[CIP-0030](https://cips.cardano.org/cip/CIP-30) is the one most developers meet first: it is the connector API every browser wallet implements, and it is what a dApp calls to request addresses, build, and sign transactions. The CIP-0095, CIP-0103, and CIP-0106 series extend that same bridge for the Conway era, bulk signing, and multisig. The CIP-1852/1854/1855 set (in the 1852 number block reserved for BIP-style derivation) defines hierarchical-deterministic key derivation.

## Tokens

The Tokens category covers Cardano's native assets: fungible tokens, NFTs, minting policies, and the metadata standards that describe them.

| CIP | Title | Status |
|-----|-------|--------|
| 0025 | Media Token Metadata Standard | Active |
| 0068 | Datum Metadata Standard | Active |
| 0027 | CNFT Community Royalties Standard | Active |
| 0014 | User-Facing Asset Fingerprint | Active |
| 0088 | Token Policy Registration | Active |
| 0067 | Asset Name Label Registry | Proposed |
| 0143 | Interoperable Programmable Tokens | Inactive |

[CIP-0025](https://cips.cardano.org/cip/CIP-25) and [CIP-0068](https://cips.cardano.org/cip/CIP-68) are the two metadata standards to know. CIP-0025 attaches metadata through the minting transaction; CIP-0068 stores it in a datum using a reference-token pattern, which lets the metadata be read on-chain by scripts and updated over time. CIP-0014 defines the human-facing asset fingerprint (the `asset1...` string), and CIP-0027 standardizes royalty information.

## Metadata

The Metadata category is about attaching structured information to transactions and to the chain, both on-chain and off-chain. In recent proposals it has become the home of governance metadata.

| CIP | Title | Status |
|-----|-------|--------|
| 0010 | Transaction Metadata Label Registry | Active |
| 0020 | Transaction message/comment metadata | Active |
| 0100 | Governance Metadata | Active |
| 0083 | Encrypted Transaction message/comment metadata | Active |
| 0151 | On-Chain Registration - Stake Pools | Active |
| 0108 / 0119 / 0136 | Governance metadata (actions / DReps / committee votes) | Proposed |
| 0015 / 0036 | Catalyst Registration metadata | Active / Proposed |

CIP-0010 is foundational: it is the registry of metadata label numbers, which prevents different applications from colliding on the same transaction-metadata keys. CIP-0020 standardizes attaching a plain message to a transaction, and the CIP-0100 family standardizes the off-chain documents referenced by on-chain governance actions and votes.

## Plutus

The Plutus category collects changes to the smart-contract platform: new builtins, cryptographic primitives, and the reference-input machinery that made lightweight dApps practical.

| CIP | Title | Status |
|-----|-------|--------|
| 0031 | Reference inputs | Active |
| 0032 | Inline datums | Active |
| 0033 | Reference scripts | Active |
| 0049 | ECDSA and Schnorr signatures in Plutus Core | Active |
| 0381 | Plutus support for Pairings over BLS12-381 | Active |
| 0069 | Plutus Script Type Uniformization | Active |
| 0121 / 0122 / 0123 | Integer-ByteString and bitwise / logical operations | Active |
| 0101 / 0127 | keccak256 / ripemd_160 builtins | Proposed / Active |

The CIP-0031/0032/0033 trio is the one to understand for contract development. Reference inputs let a transaction read a UTXO's datum without spending it, inline datums put the datum directly in the output rather than only its hash, and reference scripts let a script be supplied from an existing UTXO instead of being included in every transaction that uses it. Together they cut transaction sizes and enabled shared on-chain state. The cryptographic builtins (CIP-0049, CIP-0381, CIP-0133) extend what validators can verify natively, which is what makes on-chain signature checks and zero-knowledge verification feasible within the execution budget.

## Tools

Tools is the deliberate catch-all: ecosystem features and formats that do not belong to any single other category. Despite the loose definition it holds several widely used standards.

| CIP | Title | Status |
|-----|-------|--------|
| 0057 | Plutus Contract Blueprint | Active |
| 0008 | Message Signing | Active |
| 0005 | Common Bech32 Prefixes | Active |
| 0016 | Cryptographic Key Serialisation Formats | Active |
| 0089 | Distributed DApps & Beacon Tokens | Active |
| 0129 | Governance Identifiers | Proposed |
| 0139 | Universal Query Layer | Proposed |

[CIP-0057](https://cips.cardano.org/cip/CIP-57) is the most consequential entry for contract developers: it defines the Plutus blueprint, a machine-readable JSON description of a compiled contract (its validators, datum and redeemer schemas, and compiled code) that off-chain tooling consumes in place of the source. CIP-0005 defines the Bech32 prefixes (`addr`, `stake`, `pool`, and so on) that make Cardano identifiers recognizable, and CIP-0008 defines how to sign an arbitrary message with a wallet key.

## Using the categories in practice

The category field is most useful as a filter matched to what you are building. A dApp front-end developer lives mostly in Wallets (CIP-0030 and its extensions) and Tools (CIP-0057). A validator author works from Plutus (the reference-input trio, the crypto builtins) and, for token work, Tokens (CIP-0025, CIP-0068). Anyone integrating governance reads Ledger (CIP-1694) alongside the governance-metadata proposals in Metadata. A stake pool operator looks at Ledger (protocol parameters, rewards) and the pool-facing entries in Wallets, Metadata, and Tools. Protocol researchers track Consensus and Network, where most proposals are still open.

The workflow for contributing follows the same structure in reverse: a change is scoped, optionally preceded by a CPS if the problem is broad, assigned a category, written against the template, and taken through review toward a Path to Active.

## Conclusion

The CIP repository organizes Cardano's design record through two fields, `Status` and `Category`, and reading them makes a large flat list navigable. The status separates ratified standards and live features from designs still under discussion, and it has only three values, with no separate draft state. The category places each proposal into one of nine buckets that group into protocol internals (Ledger, Consensus, Network, Plutus), ecosystem standards (Wallets, Tokens, Metadata, Tools), and the process itself (Meta).

For a working developer, the practical takeaway is to treat the category as a filter: identify which one or two categories match the task, read the Active proposals there first, and check the status of anything before depending on it. The counts and statuses in this article reflect one commit and will change, but the taxonomy is stable, and it is the fastest way into the repository. The mindmap below collects the categories and their anchor proposals.

![Mindmap summarizing the Cardano CIP categories and their notable proposals]({{site.url_complet}}/assets/article/blockchain/cardano/cardano-cip-categories.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Cardano Improvement Proposal (CIP)** | a formalized design document describing a change to the Cardano ecosystem, its processes, or its environment; the format and process are themselves defined by CIP-0001. |
| **Cardano Problem Statement (CPS)** | a problem-first companion document that states a problem and its constraints without prescribing a solution, so several CIPs can be offered as answers to it. |
| **Category** | the header field placing a CIP in one of nine buckets (Meta, Ledger, Consensus, Network, Wallets, Tokens, Metadata, Plutus, Tools). |
| **Status** | the header field recording a CIP's maturity; it takes one of three values, `Proposed`, `Active`, or `Inactive`. |
| **Proposed** | a merged CIP that meets the essential criteria (structure, quality, technical soundness, a valid Path to Active) but has not yet taken effect. |
| **Active** | a CIP that has taken effect per its own Path to Active (released software, a live mainnet feature, or adopted standard); treated as complete and not substantially revised. |
| **Inactive** | a CIP that was abandoned, lost interest, or was superseded by a later proposal. |
| **Path to Active** | the section of a CIP defining the acceptance criteria and implementation plan by which it can become Active. |
| **CIP editors** | the reviewers who facilitate discussion and progress submissions, reviewing proposals in bi-weekly public meetings. |
| **Superseded** | the relationship in which a newer CIP replaces an older one, moving the older proposal to Inactive (for example CIP-0058, replaced by CIP-0121 and CIP-0122). |

## Frequently Asked Questions

**Q: What is the difference between a CIP and a CPS?**

A CIP (Cardano Improvement Proposal) is a design document that proposes a specific change or standard. A CPS (Cardano Problem Statement) is a problem-first document: it describes a problem, its context, and its constraints without prescribing a solution. The two are complementary. A CPS lets the community agree on what needs solving before committing to how, and multiple CIPs can then be proposed as solutions to the same CPS. They cross-reference each other through the `Proposed Solutions` field on a CPS and the `Solution To` field on a CIP. At the reference commit there were 21 CPSs alongside roughly 140 CIPs.

**Q: What are the possible statuses of a CIP, and why is there no "Draft" status?**

A CIP has one of three statuses: `Proposed`, `Active`, or `Inactive`. There is no `Draft` status because a proposal that has not yet been merged already exists as an open pull request, which is what "draft" means in practice; such a PR simply declares the status it aims for on acceptance. Once merged, a CIP is `Proposed` (an accepted design that has not yet taken effect), becomes `Active` when it meets its own Path to Active (released, live on mainnet, or adopted, depending on its nature), and is marked `Inactive` if it is abandoned or superseded.

**Q: How many categories exist, and how do they group together?**

There are nine categories: Meta, Ledger, Consensus, Network, Wallets, Tokens, Metadata, Plutus, and Tools. They group into three bands. Ledger, Consensus, Network, and Plutus concern protocol internals, meaning how nodes reach agreement and how scripts execute. Wallets, Tokens, Metadata, and Tools are application and ecosystem standards that let independently built software interoperate. Meta governs the CIP process itself. The grouping is informal but useful for deciding which categories are relevant to a given role.

**Q: Why do Plutus and Ledger proposals follow a different sub-process from other categories?**

Changes in those two areas alter the behavior of the node implementations that every participant runs, so they require review and sign-off from the teams that maintain those implementations. CIP-0001 delegates this by pointing Plutus proposals to the process in CIP-0035 and ledger proposals to the process in CIP-0084. A wallet or metadata standard, by contrast, can be adopted by any subset of applications without changing the core protocol, so it does not need the same gate.

**Q: A developer wants to build a dApp that mints an NFT and connects to a browser wallet. Which categories and CIPs are most relevant, and why?**

This task spans three categories. From Wallets, CIP-0030 (and its Conway-era extension CIP-0095) is the connector API the dApp uses to request addresses and have transactions signed by the browser wallet. From Tokens, the NFT's metadata follows either CIP-0025 (metadata attached through the minting transaction) or CIP-0068 (metadata stored in a datum, readable on-chain and updatable). From Plutus and Tools, if the mint is guarded by a validator, CIP-0057 describes the blueprint that the off-chain code consumes to interact with that validator, and the CIP-0031/0032/0033 trio governs the reference-input machinery the contract may rely on. Combining them shows how a single feature draws on standards from several categories at once, which is why the category field is a filter rather than a strict partition of concerns.

## References

### CIP process and index

- [cardano-foundation/CIPs repository](https://github.com/cardano-foundation/CIPs)
- [CIP-0001 — CIP Process](https://cips.cardano.org/cip/CIP-1)
- [CIP-9999 — Cardano Problem Statements](https://cips.cardano.org/cip/CIP-9999)
- [cips.cardano.org — rendered index](https://cips.cardano.org/)

### Notable proposals cited

- [CIP-1694 — On-Chain Decentralized Governance](https://cips.cardano.org/cip/CIP-1694)
- [CIP-0030 — Cardano dApp-Wallet Web Bridge](https://cips.cardano.org/cip/CIP-30)
- [CIP-0025 — Media Token Metadata Standard](https://cips.cardano.org/cip/CIP-25)
- [CIP-0068 — Datum Metadata Standard](https://cips.cardano.org/cip/CIP-68)
- [CIP-0057 — Plutus Contract Blueprint](https://cips.cardano.org/cip/CIP-57)

### Tooling used

- [Claude Code](https://claude.com/product/claude-code)
