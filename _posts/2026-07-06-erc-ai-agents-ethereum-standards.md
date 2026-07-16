---
layout: post
title: "ERC Standards for AI Agents - The On-Chain Agent Stack on Ethereum"
date:   2026-07-06
lang: en
locale: en-GB
categories: AI blockchain ethereum
tags: ethereum erc ai-agent erc-8004 identity zkml
description: A technical survey of the Ethereum ERC standards for AI agents, from ERC-8004 Trustless Agents to verification, coordination, commerce, and verifiable ML inference.
image: /assets/article/blockchain/ai/erc-agent-standards/2026-07-06-erc-ai-agents-ethereum-standards-mindmap.png
isMath: false
---

A wave of ERC drafts submitted since 2024 addresses a single question: how does one autonomous software agent transact with another when neither controls the other and no prior relationship exists? These proposals form a layered stack around identity, verification, execution, and settlement. This article surveys the standards, groups them by function, and shows how [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) sits at the centre of the design.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) / [Cursor](https://cursor.com/) and several custom skills

[TOC]

## Why Ethereum needs agent-specific standards

An AI agent that holds funds, calls contracts, and negotiates with other agents raises problems that existing token and account standards do not solve. Three gaps recur across the proposals.

The first is **discovery across trust boundaries**. Two agents built by different teams, running on different infrastructure, need a shared way to find each other and read each other's capabilities without a central directory. The second is **trust proportional to stake**. Ordering a pizza and authorising a medical diagnosis carry different risk, so a single binary "trusted / untrusted" flag is insufficient. The third is **bounded authority**. An owner who delegates a wallet to an agent wants the agent to act, but only within a policy, and wants a tamper-evident record of what the agent did.

The ERCs described here answer these gaps as composable modules rather than one monolith. The following sections walk through each functional group. The count and status figures reflect the local ERC repository snapshot used to compile this survey; most proposals remain in `Draft`, with a smaller set at `Final` or `Last Call`.

## Summary table

The nineteen standards covered in this article, grouped by function. Status values are taken from the ERC repository snapshot used for this survey and will change as the proposals progress.

| ERC | Title | Group | Status |
|-----|-------|-------|--------|
| [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) | Trustless Agents | Identity & registration | Draft |
| [ERC-8122](https://eips.ethereum.org/EIPS/eip-8122) | Minimal Agent Registry | Identity & registration | Draft |
| [ERC-8041](https://eips.ethereum.org/EIPS/eip-8041) | Fixed-Supply Agent NFT Collections | Identity & registration | Draft |
| [ERC-8217](https://eips.ethereum.org/EIPS/eip-8217) | Agent NFT Identity Bindings | Identity & registration | Draft |
| [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) | AI Agent Verification | Verification & trust | Final |
| [ERC-8107](https://eips.ethereum.org/EIPS/eip-8107) | ENS Trust Registry for Agent Coordination | Verification & trust | Draft |
| [ERC-8001](https://eips.ethereum.org/EIPS/eip-8001) | Agent Coordination Framework | Coordination | Final |
| [ERC-8196](https://eips.ethereum.org/EIPS/eip-8196) | AI Agent Authenticated Wallet | Execution & authorisation | Last Call |
| [ERC-8199](https://eips.ethereum.org/EIPS/eip-8199) | Sandboxed Smart Wallet | Execution & authorisation | Draft |
| [ERC-8273](https://eips.ethereum.org/EIPS/eip-8273) | Attestation-Gated Agentic Actions | Execution & authorisation | Draft |
| [ERC-8257](https://eips.ethereum.org/EIPS/eip-8257) | Agent Tool Registry | Execution & authorisation | Draft |
| [ERC-8183](https://eips.ethereum.org/EIPS/eip-8183) | Agentic Commerce | Commerce, compliance & oracles | Draft |
| [ERC-8226](https://eips.ethereum.org/EIPS/eip-8226) | Regulated Agent Mandate | Commerce, compliance & oracles | Draft |
| [ERC-8033](https://eips.ethereum.org/EIPS/eip-8033) | Agent Council Oracles | Commerce, compliance & oracles | Draft |
| [ERC-7662](https://eips.ethereum.org/EIPS/eip-7662) | AI Agent NFTs | Agents as tokenised assets | Draft |
| [ERC-7857](https://eips.ethereum.org/EIPS/eip-7857) | AI Agents NFT with Private Metadata | Agents as tokenised assets | Final |
| [ERC-7007](https://eips.ethereum.org/EIPS/eip-7007) | Verifiable AI-Generated Content Token | Verifiable AI compute | Final |
| [ERC-7992](https://eips.ethereum.org/EIPS/eip-7992) | Verifiable ML Model Inference (ZKML) | Verifiable AI compute | Draft |
| [ERC-7517](https://eips.ethereum.org/EIPS/eip-7517) | Content Consent for AI/ML Data Mining | Verifiable AI compute | Draft |

## The identity layer

### ERC-8004 — Trustless Agents

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8004-trustless-agents/25098)

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) is the anchor of the stack. It proposes using the blockchain to discover, choose, and interact with agents across organisational boundaries without pre-existing trust, so that open-ended agent economies can form. The standard is organised around three registries, described here following [Taiko's ERC-8004 guide](https://taiko.xyz/guides/erc-8004-trustless-agent-standard):

- **Identity Registry** is an [ERC-721](https://eips.ethereum.org/EIPS/eip-721) contract. Each agent is minted as an NFT with a unique `agentId` linked to an off-chain registration file, hosted on IPFS, over HTTPS, or as a base64 data URI, that lists the agent's capabilities, endpoints, and supported protocols.
- **Reputation Registry** records client feedback as scores from 0 to 100 with optional tags and evidence links. Each submission carries a cryptographic signature from the agent server, which keeps the feedback public while blocking forged or spammed scores, and different platforms build their own scoring models on the same raw data.
- **Validation Registry** provides hooks for requesting and recording independent verification of an agent's work, whether by stake-secured re-execution, a zkML verifier, a TEE oracle, or a trusted judge. It is the least mature of the three and was not yet deployed at the time of writing.

Registering an agent is a short sequence: publish a JSON metadata file describing the agent and its A2A or MCP endpoints, call `register()` to mint the [ERC-721](https://eips.ethereum.org/EIPS/eip-721) identity, call `setAgentURI(agentId, uri)` to bind that identity to the file, optionally call `setAgentWallet()` with an [EIP-712](https://eips.ethereum.org/EIPS/eip-712) or [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271) signature to attach a verified receiving wallet, then accumulate history through `giveFeedback()` on the Reputation Registry.

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) does not replace the agent-communication layer. Google's Agent-to-Agent (A2A) protocol and Anthropic's Model Context Protocol (MCP) still handle how agents talk and reach tools; ERC-8004 handles who an agent is and whether it can be trusted, and an agent advertises its A2A or MCP endpoints inside the registration file.

The defining idea is that **trust models are pluggable and tiered**, with security proportional to the value at risk. A developer integrating [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) can select among reputation systems built on client feedback, validation through stake-secured re-execution, zero-knowledge machine-learning (zkML) proofs, or trusted-execution-environment (TEE) oracles. Low-stake tasks lean on cheap reputation signals; high-stake tasks demand cryptographic or economic guarantees. Almost every other agent ERC references ERC-8004 as the identity substrate it builds on.

### The modular trust stack

[ERC-8196](https://eips.ethereum.org/EIPS/eip-8196) makes the layering explicit by naming a three-layer model, and several other standards slot into it:

- **Layer 1 (Register)**: [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) provides on-chain identity and registration.
- **Layer 2 (Verify)**: [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) provides verification and risk scoring.
- **Layer 3 (Execute)**: [ERC-8196](https://eips.ethereum.org/EIPS/eip-8196) provides policy-bound execution with an immutable audit trail.

![Modular trust stack for on-chain AI agents, mapping ERC-8004, ERC-8126, ERC-8196 and related standards across register, verify and execute layers]({{site.url_complet}}/assets/article/blockchain/ai/erc-agent-standards/modular-trust-stack-concept.png)

## Discovery and registration variants

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) provides an unlimited-mint identity registry, but not every deployment wants that shape. A cluster of standards adapts registration to specific needs.

### ERC-8122 — Minimal Agent Registry

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8122-minimal-agent-registry/27405)

[ERC-8122](https://eips.ethereum.org/EIPS/eip-8122) offers a lightweight on-chain registry for discovering agents. It reuses [ERC-6909](https://eips.ethereum.org/EIPS/eip-6909) as the underlying registry design, [ERC-7930](https://eips.ethereum.org/EIPS/eip-7930) for cross-chain agent identification, and [ERC-8048](https://eips.ethereum.org/EIPS/eip-8048) for on-chain metadata. Each agent is a token ID with a single owner and fully on-chain metadata, so discovery and ownership transfer do not depend on external storage.

### ERC-8041 — Fixed-Supply Agent NFT Collections

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8041-fixed-supply-agent-nft-collections/25656)

[ERC-8041](https://eips.ethereum.org/EIPS/eip-8041) addresses the case where an unlimited registry is the wrong tool. It lets a creator mint a fixed-supply collection of Agent NFTs, each registered in an [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) registry, keeping the association between agents and their collection through on-chain metadata and mint-number tracking.

### ERC-8217 — Agent NFT Identity Bindings

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/add-erc-8217-agent-nft-identity-bindings/28339)

[ERC-8217](https://eips.ethereum.org/EIPS/eip-8217) connects an [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) agent identity to an external NFT or tokenised-asset contract. The metadata record stores only the 20-byte binding contract address under a reserved key; the token standard, contract, and ID are read from that contract through `bindingOf(agentId)` rather than duplicated in metadata. The binding contract is expected to be a canonical per-chain singleton.

## Verification and trust

Registration says an agent exists. Verification says something about whether to believe it.

### ERC-8126 — AI Agent Verification

> **Status:** Final · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8126-ai-agent-verification/27445)

[ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) defines an interface for verifying agents registered through [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004). It supports several specialised processes: Ethereum Token Verification (ETV), Media Content Verification (MCV), Solidity Code Verification (SCV), Web Application Verification (WAV), and Wallet Verification (WV). Providers implement the standard using Private Data Verification (PDV) to generate zero-knowledge proofs, so detailed results stay accessible only to the agent's wallet holder while a unified **risk score from 0 to 100** summarises trustworthiness for others. Attestations can be posted back to ERC-8004's Validation Registry for ecosystem-wide discoverability. ERC-8126 is one of the few agent standards already at `Final`.

### ERC-8107 — ENS Trust Registry for Agent Coordination

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-ens-trust-registry-for-agent-coordination/27200)

[ERC-8107](https://eips.ethereum.org/EIPS/eip-8107) takes a different, graph-based approach. It lets agents establish and query transitive trust relationships using ENS names as identifiers. Trust is expressed at four levels (Unknown, None, Marginal, Full) and propagates through signature chains following the GnuPG web-of-trust model. The registry serves as the trust-and-delegation module anticipated by [ERC-8001](https://eips.ethereum.org/EIPS/eip-8001), so a coordinator can gate participation by trust-graph proximity: an agent is valid from a coordinator's perspective when sufficient trust paths connect them.

## Coordination

### ERC-8001 — Agent Coordination Framework

> **Status:** Final · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8001-secure-intents-a-cryptographic-framework-for-autonomous-agent-coordination-draft-erc-8001/24989)

[ERC-8001](https://eips.ethereum.org/EIPS/eip-8001) is a minimal single-chain primitive for multi-party agent coordination, and one of the earliest agent standards to reach `Final`. An initiator posts an intent; each participant provides a verifiable acceptance attestation. Once the required set of acceptances is present and fresh, the intent becomes executable. The standard specifies typed data, a lifecycle, mandatory events, and verification rules compatible with [EIP-712](https://eips.ethereum.org/EIPS/eip-712), [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271), [EIP-2098](https://eips.ethereum.org/EIPS/eip-2098), and [EIP-5267](https://eips.ethereum.org/EIPS/eip-5267). It deliberately omits privacy, reputation, threshold policies, bonding, and cross-chain semantics, expecting those as optional modules that reference it, which is exactly the role [ERC-8107](https://eips.ethereum.org/EIPS/eip-8107) fills for trust.

The diagram below traces how these pieces combine into a single agent lifecycle, from registration through verification, coordination, and settlement.

![End-to-end lifecycle of an on-chain AI agent across ERC-8004 registration, ERC-8126 verification, ERC-8107 trust, ERC-8001 coordination and ERC-8183 job settlement]({{site.url_complet}}/assets/article/blockchain/ai/erc-agent-standards/agent-lifecycle-workflow.png)

## Execution and authorisation

Once an agent is trusted, it must act, and the sharpest security questions live here: how does an owner grant an agent authority without handing over a private key, and how is that authority bounded?

### ERC-8196 — AI Agent Authenticated Wallet

> **Status:** Last Call · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8196-ai-agent-authenticated-wallet/27987)

[ERC-8196](https://eips.ethereum.org/EIPS/eip-8196) defines wallets that execute a transaction only when accompanied by verifiable cryptographic proof that the action complies with a policy set by the asset owner. It occupies Layer 3 of the trust stack and enables credential delegation without exposing private keys, prevents a host from manipulating agent behaviour, and provides tamper-evident logging of session activity. The design cites the Ethereum Foundation mandate that a user retains final say over their identities, assets, actions, and agents. It is currently at `Last Call`.

### ERC-8199 — Sandboxed Smart Wallet

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8199-sandboxed-smart-wallet/28029)

[ERC-8199](https://eips.ethereum.org/EIPS/eip-8199) targets high-frequency agent operators. It describes a smart wallet that runs in a fully detached, sandboxed environment: the agent smart wallet is completely separated from the owner wallet, and only the owner wallet retains persistent access to it. This isolates agent activity while leaving the owner in control.

### ERC-8273 — Attestation-Gated Agentic Actions

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8273-attestation-gated-agentic-actions/28617)

[ERC-8273](https://eips.ethereum.org/EIPS/eip-8273) specifies an on-chain Agent Attestation Registry with an atomic execution model. Issuance and action execution happen inside a single transaction. Active authorisation state is held in [EIP-1153](https://eips.ethereum.org/EIPS/eip-1153) transient storage (`TSTORE` / `TLOAD`) and is cleared automatically at the end of the transaction, so no long-lived or session-based authorisation persists. Each attestation carries a `capability` (a coarse authorisation class) and an `actionDigest` (a fine-grained action fingerprint that must include the target contract, selector, arguments, and a nonce for replay protection). A bundled `attestAndCall` entry point opens the authorisation window, executes the action through a chosen execution profile, and relies on the EVM to tear the window down. Execution profiles cover direct wallet execution for [ERC-7702](https://eips.ethereum.org/EIPS/eip-7702) EOAs and [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337) UserOperations, so the target DApp still sees the agent's own wallet as `msg.sender`.

### ERC-8257 — Agent Tool Registry

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8257-agent-tool-registry/28457)

[ERC-8257](https://eips.ethereum.org/EIPS/eip-8257) sits alongside execution as a permissionless registry for the tools an agent may invoke. Each registration commits a metadata URI and a content hash; invocation is gated by an optional external predicate contract. Registrations bind to an off-chain manifest through origin-binding (the manifest is served at a well-known path on the endpoint's origin) and creator self-attestation.

## Commerce, compliance, and oracles

Agents that transact need a settlement grammar and, where regulated assets are involved, a compliance boundary.

### ERC-8183 — Agentic Commerce

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8183-agentic-commerce/27902)

[ERC-8183](https://eips.ethereum.org/EIPS/eip-8183) defines the Agentic Commerce Protocol around a **job with an escrowed budget** and four states: Open, Funded, Submitted, and a Terminal state. The client funds the job, the provider submits work, and an **evaluator** is the only party who may mark the job completed. Rejections and refunds are possible along the way: the client may reject while Open, the evaluator may reject while Funded or Submitted, and an expired job refunds the client. An optional attestation reason (for example a hash) on completion or rejection enables audit and composition with reputation systems such as [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004).

![ERC-8183 agentic commerce job state machine showing transitions between Open, Funded, Submitted, Completed, Rejected and Refunded]({{site.url_complet}}/assets/article/blockchain/ai/erc-agent-standards/agentic-commerce-job-state.png)

### ERC-8226 — Regulated Agent Mandate

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8226-regulated-agent-mandate/28208)

[ERC-8226](https://eips.ethereum.org/EIPS/eip-8226), or RAMS, is a compliance-delegation layer for agents operating on tokenised regulated assets. A verified principal delegates scoped, time-bounded, and financially capped authority to an on-chain agent, and a regulated token verifies the mandate before an agent-initiated action. RAMS is agnostic to the identity system, the token standard, and the compliance framework, so it works with [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) identities, with [ERC-20](https://eips.ethereum.org/EIPS/eip-20) / [ERC-721](https://eips.ethereum.org/EIPS/eip-721) / [ERC-1155](https://eips.ethereum.org/EIPS/eip-1155) tokens, and with regulated standards such as [ERC-7943](https://eips.ethereum.org/EIPS/eip-7943) or [ERC-3643](https://eips.ethereum.org/EIPS/eip-3643).

### ERC-8033 — Agent Council Oracles

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8033-agent-council-oracles/25638)

[ERC-8033](https://eips.ethereum.org/EIPS/eip-8033) turns a set of agents into a trust-minimised oracle. A requester opens a query; `infoAgents` stake a bond and submit a commit-reveal answer; a selected `judgeAgent` reviews the revealed answers, rewards the agents that answered correctly, and slashes the bonds of those that did not. The commit-reveal-and-judge structure supports permissionless participation, bond-based incentives, and optional extensions for reputation and disputes, which suits semantic data oracles and prediction markets.

## Agents as tokenised assets

Two earlier standards treat the agent itself as a tradeable NFT, with special handling for the sensitive data an agent embodies.

### ERC-7662 — AI Agent NFTs

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-7662-ai-agent-nfts/19371)

[ERC-7662](https://eips.ethereum.org/EIPS/eip-7662) argues that when agents are minted and traded as NFTs, prompts should not sit in plain token metadata. It defines a custom struct and stores prompt data at decentralised-storage URLs rather than fully on-chain, since prompts can be large. Its favoured privacy option encrypts the data with contract parameters that decrypt only to the NFT's owner.

### ERC-7857 — AI Agents NFT with Private Metadata

> **Status:** Final · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-7857-an-nft-standard-for-ai-agents-with-private-metadata/22391)

[ERC-7857](https://eips.ethereum.org/EIPS/eip-7857) generalises that idea. Its metadata represents agent capabilities (models, memory, character definitions) and requires privacy protection, so the standard adds mechanisms for verifiable data ownership and secure transfer. A unified interface abstracts over verification methods such as TEE and zero-knowledge proofs, keeping valuable agent metadata confidential yet verifiable during transfer. ERC-7857 is `Final`.

## Verifiable AI computation

The stack's outer edge concerns proving what an AI model actually did, and controlling how content feeds AI systems in the first place.

### ERC-7007 — Verifiable AI-Generated Content Token

> **Status:** Final · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/eip-7007-zkml-aigc-nfts-an-erc-721-extension-interface-for-zkml-based-aigc-nfts/14216)

[ERC-7007](https://eips.ethereum.org/EIPS/eip-7007) extends [ERC-721](https://eips.ethereum.org/EIPS/eip-721) for AI-generated content. It adds `addAigcData` and `verify` interfaces, an `AigcData` event, optional enumerable and updatable extensions, and a metadata schema, with the `tokenId` indexed by the `prompt`. It incorporates zkML and optimistic-ML (opML) capabilities to verify that generated content matches its claimed provenance. ERC-7007 is `Final`.

### ERC-7992 — Verifiable ML Model Inference

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-7992-verifiable-ml-model-inference-zkml/24896)

[ERC-7992](https://eips.ethereum.org/EIPS/eip-7992) standardises how contracts reference ML models and accept zero-knowledge attestations of their inferences. A registry issues a `modelId` for a `ModelCommitment` (hashes of weights, architecture, proving circuit, and verifying key) plus a `proofSystemId`. A `verifyInference(modelId, inputCommitment, output, proof)` call dispatches to the declared proof system and reverts on any mismatch, emitting `InferenceVerified` on success. Inputs are bound by domain-separated, nonceable commitments for replay protection, and proof systems (Groth16, Plonk, STARK) are pluggable without ABI changes.

### ERC-7517 — Content Consent for AI/ML Data Mining

> **Status:** Draft · [Ethereum Magicians discussion](https://ethereum-magicians.org/t/eip-7517-content-consent-for-ai-ml-data-mining/15755)

[ERC-7517](https://eips.ethereum.org/EIPS/eip-7517) works upstream of inference. It standardises how a creator declares mining preferences for digital media, extending media-metadata standards such as [ERC-7053](https://eips.ethereum.org/EIPS/eip-7053) and NFT standards, so an asset can specify how it may be used in data mining, AI training, and machine-learning workflows.

## Patterns across the standards

Two patterns stand out. First, **[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) is the gravitational centre**: identity, verification, execution, commerce, and compliance standards all reference it, and the numbering shows a burst of activity through late 2025 and into 2026 as teams filled in the layers around it. Second, the design consistently favours **composable modules over a single specification**. [ERC-8001](https://eips.ethereum.org/EIPS/eip-8001) explicitly defers privacy, reputation, and bonding to other standards; RAMS is agnostic to identity and token frameworks; [ERC-8273](https://eips.ethereum.org/EIPS/eip-8273) leaves off-chain evaluation entirely to integrators. The trust decisions, which attestors to believe and how much stake to require, are pushed to the deploying application rather than fixed in the standard.

The maturity gradient is worth noting for anyone building today. [ERC-8001](https://eips.ethereum.org/EIPS/eip-8001), [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126), and the [ERC-7007](https://eips.ethereum.org/EIPS/eip-7007) family (7007, 7857) are `Final`; [ERC-8196](https://eips.ethereum.org/EIPS/eip-8196) is at `Last Call`; the majority, including [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) itself, remain `Draft` and subject to change.

## Adoption in practice

Draft status does not mean the standards are only paper. A short survey of real deployments shows adoption concentrated in three of them, with the rest still pre-adoption. The picture below reflects reporting from early to mid 2026 and will move quickly.

### ERC-8004 and the agentic-finance stack

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) is the only standard in the set with a live mainnet footprint. Its core registries were [deployed to Ethereum mainnet on 29 January 2026](https://www.forbes.com/sites/digital-assets/2026/02/05/ai-agents-gain-trust-via-ethereum-erc-8004-on-mainnet/), with reference contracts also on Base Sepolia, Linea Sepolia, and Hedera testnet. The standard is positioned as an on-chain extension of Google's Agent-to-Agent (A2A) protocol, and ecosystem participants including ENS, EigenLayer, The Graph, and Taiko, alongside the Ethereum Foundation's dAI team, have signalled integrations.

Layer-2 deployments followed. [Taiko brought the Identity and Reputation registries live in February 2026](https://taiko.xyz/guides/erc-8004-trustless-agent-standard) as a Type 1 ZK-EVM, where a registration costs around $0.01 against roughly $1 to $5 on Ethereum L1. That gap matters for agents expected to register and update frequently, and it illustrates why the standard is landing on L2s first. The Validation Registry, the part that would carry stake-secured or zkML verification, was still undeployed at the time of writing, so the live surface is identity plus reputation rather than the full trust model.

The DeFi-relevant traction comes from pairing [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) identity and reputation with [Coinbase's x402 payment protocol](https://thegraph.com/blog/understanding-x402-erc8004/), which lets agents settle USDC micropayments over HTTP. Together they form what the ecosystem calls the agentic-finance stack: an agent proves who it is through ERC-8004, then pays or gets paid through x402. A [Q1 2026 industry report](https://www.techflowpost.com/en-US/article/30438) put registrations in the tens of thousands and x402 payment volume above $50M, with early use cases skewed toward automated trading systems and DeFi assistant bots deployed on Base. Community trackers such as the [awesome-erc8004 list](https://github.com/sudeepb02/awesome-erc8004) and an [empirical study of the ecosystem](https://arxiv.org/pdf/2606.26028) have appeared alongside the deployments.

One qualification matters. This is a new agent-native ecosystem rather than established DeFi protocols retrofitting the standard. A DeFi product using [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) today means agent and payment infrastructure, not a lending market or an established DEX adopting agent identity.

### Agent execution infrastructure: MetaMask server wallets

Execution infrastructure is also being built against [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004). MetaMask's [server-wallet tutorial](https://docs.metamask.io/tutorials/design-server-wallets) describes a backend signer that holds private keys on behalf of an AI agent, where clients authenticate a request and receive a signature to submit on-chain. The design keeps signing away from the agent through a dual-key split: the agent holds only an authentication key, while control of the on-chain account derives from a separate signing key the agent never sees.

The signing path runs inside a trusted execution environment, such as an AWS Nitro enclave with no external networking or persistent storage, which handles key generation, decryption, policy application, and signature production. Before a signature is produced, the request passes a policy layer of spend limits, scope limits, chain limits, frequency limits, simulation checks, and optional human approval. MetaMask frames [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) as the piece that standardises how an agent expresses what it intends to do, so pairing a registered ERC-8004 identity with a policy-bounded server wallet is what makes an agent transaction attributable and verifiable end to end. While the production offering is being finalised, the tutorial points builders at the MetaMask Node.js Embedded Wallets SDK for the same pattern.

This is a useful reference point for the draft execution standards in the article. The server-wallet pattern implements in production what [ERC-8196](https://eips.ethereum.org/EIPS/eip-8196) specifies as policy-bound execution without key exposure, what [ERC-8199](https://eips.ethereum.org/EIPS/eip-8199) frames as a sandboxed agent wallet detached from the owner, and the TEE trust model already named in [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004), but it does so directly rather than through the draft interfaces. It shows the execution layer taking shape as concrete infrastructure ahead of the standards that describe it.

### Verifiable agents in a TEE: Oasis ROFL

Where MetaMask secures the signing side, [Oasis wires ERC-8004 to confidential compute](https://docs.oasis.io/build/use-cases/trustless-agent) on the validation side. Its guide deploys an Eliza AI agent inside ROFL, the Oasis confidential-compute framework, so the agent runs in a trusted execution environment whose code can be audited and proved to be the deployed instance, with no silent alteration. A `rofl-8004` service derives an Ethereum address for the agent, and once that address holds a little ether for fees the agent is registered and validated in the ERC-8004 registry automatically. ROFL performs the startup attestation of the container and injects secrets such as an `OPENAI_API_KEY` as end-to-end-encrypted environment variables stored on-chain, while registry interaction runs on Sapphire, the Oasis confidential EVM.

This is the TEE trust model from [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) made concrete. Rather than a reputation score or a zkML proof, the agent's trustworthiness rests on a hardware attestation that the registered code is what actually runs, which sits at the high-assurance end of the tiered trust spectrum the standard describes. Taken together, the three deployments cover the standard's surface from different angles: Taiko brings identity and reputation live cheaply on an L2, MetaMask secures policy-bound signing, and Oasis supplies the TEE-backed validation that ERC-8004's own registries have not yet shipped.

### Vendor-shipped token standards: ERC-7857 and ERC-7007

Two of the tokenisation standards are live because their authors ship products on them. [ERC-7857 was introduced by 0G Labs](https://0g.ai/blog/0g-introducing-erc-7857) as the basis for Intelligent NFTs (iNFTs): AI agents tokenised with encrypted metadata and oracle-based re-encryption on transfer, running on the 0G network. ERC-7007 is used by ORA Protocol for its Initial Model Offering and verifiable AI-generated-content NFTs, with zkML and opML backing a revenue-sharing model for tokenised inference. In both cases the standard's author is also its main user, so adoption is real but narrow.

> **Note:** ORA's protocol documentation at `docs.ora.io` no longer resolves (DNS failure as of July 2026), so the original ORA docs link has been removed. The [ERC-7007 specification](https://eips.ethereum.org/EIPS/eip-7007) remains the authoritative reference.

### The remaining standards

For the other standards covered here, including [ERC-8001](https://eips.ethereum.org/EIPS/eip-8001), [ERC-8033](https://eips.ethereum.org/EIPS/eip-8033), [ERC-8107](https://eips.ethereum.org/EIPS/eip-8107), [ERC-8122](https://eips.ethereum.org/EIPS/eip-8122), [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126), [ERC-8183](https://eips.ethereum.org/EIPS/eip-8183), [ERC-8196](https://eips.ethereum.org/EIPS/eip-8196), [ERC-8199](https://eips.ethereum.org/EIPS/eip-8199), [ERC-8217](https://eips.ethereum.org/EIPS/eip-8217), [ERC-8226](https://eips.ethereum.org/EIPS/eip-8226), [ERC-8257](https://eips.ethereum.org/EIPS/eip-8257), [ERC-8273](https://eips.ethereum.org/EIPS/eip-8273), [ERC-8041](https://eips.ethereum.org/EIPS/eip-8041), [ERC-7992](https://eips.ethereum.org/EIPS/eip-7992), and [ERC-7517](https://eips.ethereum.org/EIPS/eip-7517), no production DeFi product with meaningful usage surfaced during this survey. Several of them build directly on [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) and read as proposals waiting on the identity layer to mature rather than shipped systems. That gap is the honest state of the field: the identity and payment base is deploying, and the verification, execution, and compliance layers around it are still mostly specification.

## Proposals not yet merged

The standards above are all present in the [ethereum/ERCs](https://github.com/ethereum/ERCs) repository, which is how they received a merged number and a status. A second, larger wave of agent proposals is still being drafted on the [Fellowship of Ethereum Magicians forum](https://ethereum-magicians.org/c/ercs/57) and has not yet been merged into the repository. Their numbers are self-assigned by the authors and can still change or collide, and no `status` field applies to them yet. They are worth tracking because they extend the same themes seen above: assurance and threat registries, bounded execution, escrow payments, skill and memory registries, and regulated-asset handling.

The table lists the agent proposals under discussion at the time of writing, with the scope of each taken from its forum thread. These are draft posts rather than merged documents, so both the scope and the self-assigned number remain provisional.

| Proposal | Title | Scope |
|----------|-------|-------|
| [ERC-8028](https://ethereum-magicians.org/t/erc-8028-data-anchoring-token-dat/25512) | Data Anchoring Token (DAT) | Semi-fungible token binding ownership, usage rights, and revenue share for tokenised AI datasets, models, and agents, with on-chain usage metering |
| [ERC-8118](https://ethereum-magicians.org/t/erc-8118-agent-authorization/27402) | Agent Authorization | Authorises an agent to perform specific on-chain actions for a user, with time-bound, usage-limited, function-level delegation |
| [ERC-8203](https://ethereum-magicians.org/t/erc-8203-agent-off-chain-conditional-settlement-extension-interface/28041) | Agent Off-chain Conditional Settlement | State-channel settlement of conditional obligations between agents, keeping the happy path off-chain at zero gas |
| [ERC-8210](https://ethereum-magicians.org/t/erc-8210-agent-assurance/28097) | Agent Assurance | Agents lock collateral as a job fulfilment guarantee, with a claims process for non-delivery beyond a basic escrow refund |
| [ERC-8239](https://ethereum-magicians.org/t/erc-8239-agent-skill-registry/28335) | Agent Skill Registry | On-chain registry to publish, discover, and track agent skills, framed as a package manager for skills rather than a trust layer |
| [ERC-8240](https://ethereum-magicians.org/t/erc-8240-trust-infrastructure-for-agents-and-assets/28322) | Trust Infrastructure for Autonomous Agents and Tokenized Assets | Five composable interfaces (attestation, decision trail, accountability, risk signal, RWA passport) defining what trust data looks like, not how it is computed |
| [ERC-8259](https://ethereum-magicians.org/t/erc-8259-ai-agent-identity-reputation-threat-registry-draft-v2-request-for-feedback/28521) | AI Agent Identity, Reputation & Threat Registry | Identity binding, dynamic reputation scoring, and signed threat signals so contracts can make programmatic trust decisions |
| [ERC-8263](https://ethereum-magicians.org/t/erc-8263-onchain-proof-layer-for-ai-agents/28577) | Onchain Proof Layer for AI Agents | Registry and canonical payload to anchor inference attestations (agent, model, prompt, output) for third-party verification without storing full inference data |
| [ERC-8264](https://ethereum-magicians.org/t/erc-8264-ai-agent-memory-access-rights/28584) | AI Agent Memory Access Rights | Four-function interface (read, write, delete, export) giving an address GDPR-style control over an agent's memory records |
| [ERC-8275](https://ethereum-magicians.org/t/erc-8275-agent-service-discovery-and-escrow-payments/28622) | Agent Service Discovery and Escrow Payments | Registry, escrow with dispute resolution, and reputation interfaces so agents can be discovered, paid, and rated trustlessly |
| [ERC-8301](https://ethereum-magicians.org/t/erc-8301-ai-agent-execution/28785) | AI Agent Workflow Execution Interface | Shared task-dispatch interfaces (AgentTask, IAgentCaller, IAgentHandler) to remove N×M integration between dApps and agents |
| [ERC-8312](https://ethereum-magicians.org/t/erc-8312-bounded-agent-actions/28851) | Bounded Agent Actions | Metering interface tracking how much of a bounded mandate an agent has spent, so a contract can query the authority remaining |
| [ERC-8320](https://ethereum-magicians.org/t/erc-8320-regulated-asset-claim/28919) | Regulated Asset Claim | Registry of signed, machine-readable claims about an asset's identity, valuation, compliance, and backing, under role-based governance |

The overlap with the merged set is direct. ERC-8240 and ERC-8259 restate the identity, reputation, and trust-data role of [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) and [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126); ERC-8118 and ERC-8312 extend the bounded-authority idea behind [ERC-8226](https://eips.ethereum.org/EIPS/eip-8226) and [ERC-8273](https://eips.ethereum.org/EIPS/eip-8273); ERC-8275 and ERC-8210 rework the escrow and job settlement of [ERC-8183](https://eips.ethereum.org/EIPS/eip-8183); and ERC-8263 mirrors the verifiable-inference goal of [ERC-7992](https://eips.ethereum.org/EIPS/eip-7992). The duplication signals how contested this design space still is, with several teams proposing competing interfaces for the same gaps ERC-8004 deliberately left open.

## Conclusion

The AI-agent ERCs form a layered stack rather than a single interface. [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) supplies identity and pluggable, tiered trust; [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) and [ERC-8107](https://eips.ethereum.org/EIPS/eip-8107) add verification and trust-graph reasoning; [ERC-8196](https://eips.ethereum.org/EIPS/eip-8196), [ERC-8199](https://eips.ethereum.org/EIPS/eip-8199), and [ERC-8273](https://eips.ethereum.org/EIPS/eip-8273) bound execution; [ERC-8183](https://eips.ethereum.org/EIPS/eip-8183), [ERC-8226](https://eips.ethereum.org/EIPS/eip-8226), and [ERC-8033](https://eips.ethereum.org/EIPS/eip-8033) handle commerce, compliance, and oracle resolution; [ERC-7662](https://eips.ethereum.org/EIPS/eip-7662) and [ERC-7857](https://eips.ethereum.org/EIPS/eip-7857) tokenise agents themselves; and [ERC-7007](https://eips.ethereum.org/EIPS/eip-7007), [ERC-7992](https://eips.ethereum.org/EIPS/eip-7992), and [ERC-7517](https://eips.ethereum.org/EIPS/eip-7517) cover verifiable computation and data consent. The common thread is proportionality: trust and authority scale to the value at risk, and the standards leave the hard trust decisions to the integrating application. Most proposals are still in `Draft`, so the interfaces will move, but the shape of the stack is now visible.

The mindmap below summarises the standards by function.

![Mindmap of ERC standards for AI agents grouped into identity, verification, execution, commerce, tokenisation and verifiable compute]({{site.url_complet}}/assets/article/blockchain/ai/erc-agent-standards/2026-07-06-erc-ai-agents-ethereum-standards-mindmap.png)

## Frequently Asked Questions

**Q: What role does [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) play relative to the other agent standards?**

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) (Trustless Agents) is the identity substrate for the stack. It defines three registries, Identity, Reputation, and Validation, and a pluggable, tiered trust model where security scales with the value at risk. Most other agent ERCs reference it: [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) verifies identities registered through it, [ERC-8041](https://eips.ethereum.org/EIPS/eip-8041) mints fixed-supply collections registered in it, [ERC-8217](https://eips.ethereum.org/EIPS/eip-8217) binds its identities to external assets, and [ERC-8183](https://eips.ethereum.org/EIPS/eip-8183) composes job attestations with its reputation registry. It is the point the rest of the design hangs from.

**Q: What are the three layers of the modular trust stack, and which ERC fills each?**

The stack, named in [ERC-8196](https://eips.ethereum.org/EIPS/eip-8196), has Layer 1 Register ([ERC-8004](https://eips.ethereum.org/EIPS/eip-8004), on-chain identity and registration), Layer 2 Verify ([ERC-8126](https://eips.ethereum.org/EIPS/eip-8126), verification and a 0-to-100 risk score), and Layer 3 Execute (ERC-8196, policy-bound execution with an immutable audit trail). An agent flows through them in order: it registers, gets verified and scored, then acts through a wallet that checks each action against an owner-defined policy.

**Q: How does [ERC-8273](https://eips.ethereum.org/EIPS/eip-8273) prevent a granted authorisation from being reused for an unrelated action?**

[ERC-8273](https://eips.ethereum.org/EIPS/eip-8273) uses an atomic execution model with two defences. First, authorisation lives in [EIP-1153](https://eips.ethereum.org/EIPS/eip-1153) transient storage, which the EVM clears at the end of the transaction, so no session-based authorisation persists beyond the single call. Second, an attestation can carry a non-zero `actionDigest` that fingerprints the concrete action, and this digest must include the target contract, function selector, arguments, and a nonce or attestation ID. A DApp querying with that digest only accepts the authorisation for the exact action it computes, so it cannot be replayed against a different operation even under the same coarse `capability`.

**Q: Why does [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) use zero-knowledge proofs instead of publishing verification results directly?**

[ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) runs specialised verification processes (token, media, code, web-app, wallet) whose detailed outputs may be sensitive. Private Data Verification generates zero-knowledge proofs so that the full results stay accessible only to the agent's wallet holder, while a single unified risk score from 0 to 100 is exposed for others to judge trustworthiness. The score can be posted to [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004)'s Validation Registry for discoverability without leaking the underlying detail.

**Q: How do [ERC-8001](https://eips.ethereum.org/EIPS/eip-8001) and [ERC-8107](https://eips.ethereum.org/EIPS/eip-8107) combine to coordinate agents, and why are they two standards rather than one?**

[ERC-8001](https://eips.ethereum.org/EIPS/eip-8001) provides the coordination primitive: an initiator posts an intent, participants attach verifiable acceptance attestations, and once the required fresh set is present the intent is executable. It deliberately omits trust, reputation, and bonding. [ERC-8107](https://eips.ethereum.org/EIPS/eip-8107) supplies exactly that missing trust module as an ENS-based web of trust with four levels, propagating through signature chains. A coordinator uses ERC-8107 trust paths to decide who may participate in an ERC-8001 intent. Keeping them separate follows the stack's composability principle: the coordination mechanics stay minimal, and trust policy plugs in as an independent, swappable module.

**Q: A builder wants agents to trade tokenised real-world assets under regulatory constraints. Which standards combine, and how?**

This spans several layers. The agent gets an identity from [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) and a risk score from [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126). [ERC-8226](https://eips.ethereum.org/EIPS/eip-8226) (Regulated Agent Mandate) delegates scoped, time-bounded, financially capped authority from a verified principal to the agent, and the regulated token checks that mandate before any agent-initiated action; because RAMS is agnostic to the token framework, it works with [ERC-3643](https://eips.ethereum.org/EIPS/eip-3643) or [ERC-7943](https://eips.ethereum.org/EIPS/eip-7943) regulated tokens. Execution runs through an [ERC-8196](https://eips.ethereum.org/EIPS/eip-8196) authenticated wallet so each transaction carries proof of policy compliance and an audit trail, and [ERC-8273](https://eips.ethereum.org/EIPS/eip-8273) can gate individual actions atomically. Settlement of any resulting work can use [ERC-8183](https://eips.ethereum.org/EIPS/eip-8183) escrowed jobs, with completion attestations feeding back into ERC-8004 reputation.

## References

### ERC specifications (merged)

- [ERC-7007: Verifiable AI-Generated Content Token](https://eips.ethereum.org/EIPS/eip-7007)
- [ERC-7517: Content Consent for AI/ML Data Mining](https://eips.ethereum.org/EIPS/eip-7517)
- [ERC-7662: AI Agent NFTs](https://eips.ethereum.org/EIPS/eip-7662)
- [ERC-7857: AI Agents NFT with Private Metadata](https://eips.ethereum.org/EIPS/eip-7857)
- [ERC-7992: Verifiable ML Model Inference (ZKML)](https://eips.ethereum.org/EIPS/eip-7992)
- [ERC-8001: Agent Coordination Framework](https://eips.ethereum.org/EIPS/eip-8001)
- [ERC-8004: Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004)
- [ERC-8033: Agent Council Oracles](https://eips.ethereum.org/EIPS/eip-8033)
- [ERC-8041: Fixed-Supply Agent NFT Collections](https://eips.ethereum.org/EIPS/eip-8041)
- [ERC-8107: ENS Trust Registry for Agent Coordination](https://eips.ethereum.org/EIPS/eip-8107)
- [ERC-8122: Minimal Agent Registry](https://eips.ethereum.org/EIPS/eip-8122)
- [ERC-8126: AI Agent Verification](https://eips.ethereum.org/EIPS/eip-8126)
- [ERC-8183: Agentic Commerce](https://eips.ethereum.org/EIPS/eip-8183)
- [ERC-8196: AI Agent Authenticated Wallet](https://eips.ethereum.org/EIPS/eip-8196)
- [ERC-8199: Sandboxed Smart Wallet](https://eips.ethereum.org/EIPS/eip-8199)
- [ERC-8217: Agent NFT Identity Bindings](https://eips.ethereum.org/EIPS/eip-8217)
- [ERC-8226: Regulated Agent Mandate](https://eips.ethereum.org/EIPS/eip-8226)
- [ERC-8257: Agent Tool Registry](https://eips.ethereum.org/EIPS/eip-8257)
- [ERC-8273: Attestation-Gated Agentic Actions](https://eips.ethereum.org/EIPS/eip-8273)

### Deployments and integrations

- [ERC-8004 Trustless Agent Standard guide - Taiko](https://taiko.xyz/guides/erc-8004-trustless-agent-standard)
- [Design server wallets for AI agents - MetaMask docs](https://docs.metamask.io/tutorials/design-server-wallets)
- [Trustless Agent with ERC-8004 registration and validation - Oasis docs](https://docs.oasis.io/build/use-cases/trustless-agent)
- [Understanding Coinbase's x402 and Ethereum's ERC-8004 - The Graph](https://thegraph.com/blog/understanding-x402-erc8004/)
- [0G Introducing ERC-7857 - 0G Labs](https://0g.ai/blog/0g-introducing-erc-7857)
- ERC-7007 in the ORA Protocol (Initial Model Offering) — ORA's documentation at `docs.ora.io` is currently unreachable (DNS failure as of July 2026); see the [ERC-7007 specification](https://eips.ethereum.org/EIPS/eip-7007) instead

### Ecosystem analysis and reporting

- [AI Agents Gain Trust Via Ethereum: ERC-8004 On Mainnet - Forbes](https://www.forbes.com/sites/digital-assets/2026/02/05/ai-agents-gain-trust-via-ethereum-erc-8004-on-mainnet/)
- [Agentic Finance Comprehensive Report Q1 2026 - TechFlow](https://www.techflowpost.com/en-US/article/30438)
- [awesome-erc8004 ecosystem list - GitHub](https://github.com/sudeepb02/awesome-erc8004)
- [Can Trustless Agents Be Trusted? An Empirical Study of the ERC-8004 Ecosystem - arXiv](https://arxiv.org/pdf/2606.26028)

### Repositories and proposal tracking

- [ethereum/ERCs repository](https://github.com/ethereum/ERCs)
- [ERCs category - Fellowship of Ethereum Magicians](https://ethereum-magicians.org/c/ercs/57) (unmerged agent proposals are linked individually in the "Proposals not yet merged" table)

### Tools

- [Claude Code](https://claude.com/product/claude-code)
