---
layout: post
title: "ERC-8004 Trustless Agents - Identity, Reputation and Validation for On-Chain AI Agents"
date:   2026-07-06
lang: en
locale: en-GB
categories: ai blockchain ethereum
tags: ethereum erc-8004 ai-agent identity reputation validation
description: A technical deep dive into ERC-8004 Trustless Agents - its three registries for agent identity, reputation and validation, the pluggable trust models, and how the standard is being deployed.
image: /assets/article/blockchain/ai/erc-8004/2026-07-06-erc-8004-trustless-agents-mindmap.png
isMath: false
---

ERC-8004 gives an autonomous agent something it could not have before: a portable on-chain identity, a public feedback history, and a way to record independent checks of its work. 

This article looks at the standard in detail, registry by registry, and at how it is being deployed. 

It is a companion to an earlier [survey of the AI-agent ERC standards](https://rya-sge.github.io/access-denied/2026/07/06/erc-ai-agents-ethereum-standards/), narrowed to the one standard the rest of that stack builds on.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) / [Cursor](https://cursor.com/) and several custom skills

[TOC]

## The gap ERC-8004 fills

Two agent-communication protocols already exist. Anthropic's Model Context Protocol (MCP) lets a server list its prompts, resources, and tools. Google's Agent-to-Agent (A2A) protocol handles authentication, skill advertisement through AgentCards, direct messaging, and task orchestration. Neither answers the two questions that matter when agents from different organisations meet: how do I find an agent, and why should I trust it?

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) addresses discovery and trust with three lightweight registries. Its abstract frames the goal as using the blockchain to discover, choose, and interact with agents across organisational boundaries without a pre-existing relationship. The authorship is made of several different authors: Marco De Rossi (MetaMask), Davide Crapis (Ethereum Foundation), Jordan Ellis (Google), and Erik Reppel (Coinbase). 

The standard is `Draft`, created in August 2025, and it requires [EIP-155](https://eips.ethereum.org/EIPS/eip-155), [EIP-712](https://eips.ethereum.org/EIPS/eip-712), [ERC-721](https://eips.ethereum.org/EIPS/eip-721), and [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271).

The design keeps a strict separation:

- Communication stays with MCP and A2A. 
- Payments are handled elsewhere, with Coinbase's x402 given only as an example. 
- ERC-8004 covers identity, reputation, and validation, and nothing else.

## Architecture: three per-chain singletons

The three registries are meant to be deployed as one canonical contract per chain, on any L2 or on Mainnet. An agent registered on chain A can still operate and transact on other chains, and an owner may register the same agent on several chains if they wish.

![ERC-8004 three per-chain singleton registries, showing identity, reputation and validation and how the agent owner, client and validator interact with each]({{site.url_complet}}/assets/article/blockchain/ai/erc-8004/three-registry-architecture-concept.png)

The three registries divide the work cleanly:

- The **Identity Registry** is the anchor. It is an ERC-721 contract that resolves an agent to its registration file.
- The **Reputation Registry** stores feedback signals that clients post about an agent.
- The **Validation Registry** records requests for independent verification and the responses that validators return.

The Reputation and Validation registries both hold a reference back to the Identity Registry, set once through `initialize(address identityRegistry_)` and readable through `getIdentityRegistry()`. The following sections take each registry in turn.

## Identity Registry

The Identity Registry uses ERC-721 with the URIStorage extension, so every agent is immediately browsable and transferable in any NFT-compatible application. 

The standard renames two ERC-721 concepts for clarity: the `tokenId` is the `agentId`, and the `tokenURI` is the `agentURI`. 

The owner of the token is the owner of the agent and can transfer it or delegate management to operators.

An agent is globally identified by two things:

1) The `agentId` is the ERC-721 token id, assigned incrementally by the registry. 
2) The `agentRegistry` is a [CAIP](https://chainagnostic.org/)-style colon-separated string `{namespace}:{chainId}:{identityRegistry}`, for example `eip155:1:0x742...`, where `namespace` is the chain family, `chainId` is the network, and `identityRegistry` is the deployed contract address. Together they pin down one agent on one chain.

### The registration file

The `agentURI` MUST resolve to a registration file, and it MAY use any URI scheme: `ipfs://`, `https://`, or a base64-encoded `data:` URI for fully on-chain metadata. 

The file is a JSON document whose shape the standard fixes:

```json
{
  "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
  "name": "myAgentName",
  "description": "What the agent does, how it works, pricing, interaction methods",
  "image": "https://example.com/agentimage.png",
  "services": [
    { "name": "A2A", "endpoint": "https://agent.example/.well-known/agent-card.json", "version": "0.3.0" },
    { "name": "MCP", "endpoint": "https://mcp.agent.eth/", "version": "2025-06-18" },
    { "name": "ENS", "endpoint": "vitalik.eth", "version": "v1" }
  ],
  "x402Support": false,
  "active": true,
  "registrations": [
    { "agentId": 22, "agentRegistry": "eip155:1:0x742..." }
  ],
  "supportedTrust": [ "reputation", "crypto-economic", "tee-attestation" ]
}
```

- The `type`, `name`, `description`, and `image` fields keep the file compatible with ERC-721 applications. 
- The `services` list is open-ended: an agent advertises A2A cards, MCP endpoints, ENS names, DIDs, email, or wallet addresses on any chain, even chains where it is not registered. 
- The `supportedTrust` field is optional, and when it is absent the agent is discoverable but makes no trust claim.
- Because a service endpoint can point at a domain the owner does not control, the standard adds an optional check. An agent proves control of an HTTPS endpoint-domain by publishing `https://{endpoint-domain}/.well-known/agent-registration.json` with a `registrations` entry matching the on-chain agent. 

A consumer that fetches this file over HTTPS can treat the domain as verified.

### Registration and updates

Minting an agent is a single call, in one of three overloads:

```solidity
struct MetadataEntry { string metadataKey; bytes metadataValue; }

function register(string agentURI, MetadataEntry[] calldata metadata) external returns (uint256 agentId);
function register(string agentURI) external returns (uint256 agentId);
function register() external returns (uint256 agentId); // agentURI added later
```

- Registration emits a `Transfer` event, a `MetadataSet` event for the reserved `agentWallet` key, a `MetadataSet` for each extra metadata entry, and a `Registered(agentId, agentURI, owner)` event. 

- The `agentURI` is changed later with `setAgentURI()`, which emits `URIUpdated`. To store the whole file on-chain, the owner sets the `agentURI` to a base64 `data:` URI rather than a raw JSON string.

### On-chain metadata and the agent wallet

Beyond the registration file, the registry carries optional key-value metadata through `getMetadata(agentId, key)` and `setMetadata(agentId, key, value)`, with a `MetadataSet` event on write. One key is special. The `agentWallet` key is reserved: it holds the address where the agent receives payments, it starts as the owner's address, and it cannot be written through `setMetadata()` or `register()`.

Changing it requires proof of control of the new wallet. The owner calls `setAgentWallet(agentId, newWallet, deadline, signature)`, where the signature is an [EIP-712](https://eips.ethereum.org/EIPS/eip-712) signature for an EOA or an [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271) signature for a smart-contract wallet. The wallet is read with `getAgentWallet()` and cleared with `unsetAgentWallet()`. When the agent token is transferred, `agentWallet` is reset to the zero address automatically, so a new owner cannot inherit a payment address they have not re-proved.

## Reputation Registry

The Reputation Registry turns client experience into on-chain signals. Any address can post feedback about a registered agent, subject to one rule: the submitter MUST NOT be the agent's owner or an approved operator, which stops an agent from rating itself.

### Giving feedback

Feedback is a signed fixed-point number plus optional context:

```solidity
function giveFeedback(
  uint256 agentId, int128 value, uint8 valueDecimals,
  string calldata tag1, string calldata tag2,
  string calldata endpoint, string calldata feedbackURI, bytes32 feedbackHash
) external;
```

Only `value` and `valueDecimals` are mandatory, and `valueDecimals` is bounded to 0 through 18. The pair encodes a fixed-point number: a quality score of 87 out of 100 is `value = 87, valueDecimals = 0`, while an uptime of 99.77 percent is `value = 9977, valueDecimals = 2`. The two free-form tags let developers slice feedback on-chain, for example `starred`, `uptime`, `successRate`, or `responseTime`.

Storage is deliberately split. The registry stores `value`, `valueDecimals`, `tag1`, `tag2`, `isRevoked`, and a 1-indexed `feedbackIndex` counting how many times that client has rated that agent. The `endpoint`, `feedbackURI`, and `feedbackHash` are emitted in the `NewFeedback` event but not stored, which keeps rich detail in an off-chain file, typically on IPFS, while leaving the numeric signal on-chain for smart-contract composability. 

Where the URI is not content-addressed, `feedbackHash` is the KECCAK-256 hash of the referenced file, so integrity is verifiable.

Two follow-up actions round out the flow. A client revokes its own feedback with `revokeFeedback(agentId, feedbackIndex)`. Anyone, including the agent showing a refund or an aggregator flagging spam, appends context with `appendResponse(...)`, which emits `ResponseAppended`.

### Reading reputation, and the Sybil problem

The read functions expose the signals for aggregation. `readFeedback` and `readAllFeedback` return raw entries, `getClients` lists who has rated an agent, and `getSummary(agentId, clientAddresses, tag1, tag2)` returns a count and an aggregated value. 

One detail in `getSummary` is a design decision rather than an accident: the `clientAddresses` filter MUST be non-empty. The standard is explicit that an unfiltered summary is open to Sybil and spam attacks, so aggregation always runs against a caller-chosen set of reviewers. 

Simple filtering by reviewer and tag happens on-chain; sophisticated scoring, auditor networks, and insurance pools are expected to build off-chain on the same public data.

Because clients no longer need to be registered, any application can offer frictionless feedback and sponsor the gas with [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702). Feedback given by one agent about another should use that agent's `agentWallet` address as the client, so reputation aggregates cleanly.

## Validation Registry

Reputation is subjective. The Validation Registry adds an objective channel: an agent asks for its work to be checked, and a validator contract records a verdict on-chain.

![ERC-8004 validation request and response sequence between the agent owner, the validation registry, a validator contract and a consumer]({{site.url_complet}}/assets/article/blockchain/ai/erc-8004/validation-request-response-sequence.png)

The owner or operator of an agent opens a request:

```solidity
function validationRequest(address validatorAddress, uint256 agentId, string requestURI, bytes32 requestHash) external;
```

The `requestURI` points to the off-chain data a validator needs, including the inputs and outputs to check, and `requestHash` is the KECCAK-256 commitment to that payload and the request's identifier. The named validator then answers:

```solidity
function validationResponse(bytes32 requestHash, uint8 response, string responseURI, bytes32 responseHash, string tag) external;
```

Only `requestHash` and `response` are mandatory, and the call MUST come from the `validatorAddress` in the original request. The `response` is a value from 0 to 100, usable as a binary pass or fail (0 or 100) or as a graded score. A validator can respond more than once for the same request, which supports progressive states such as a soft finality followed by a hard finality, distinguished through the `tag`. The registry stores `requestHash`, `validatorAddress`, `agentId`, `response`, `responseHash`, `lastUpdate`, and `tag`, and exposes them through `getValidationStatus`, `getSummary`, `getAgentValidations`, and `getValidatorRequests`.

What a validator actually does is left open. The standard names stake-secured re-execution, zkML verifiers, and TEE oracles as examples, and it puts incentives and slashing outside its own scope, in the validation protocol itself.

This is the least settled of the three registries. The [official contracts repository](https://github.com/erc-8004/erc-8004-contracts) publishes no Validation Registry address on any chain, and the specification notes that this section is still under active update and discussion with the TEE community, to be expanded in a follow-up revision later in 2026. The interface above should therefore be read as a design in progress rather than a deployed contract.

## The tiered trust model

The single idea that ties the three registries together is that trust should scale with what is at risk. Ordering a pizza and authorising a medical diagnosis are not the same, so the standard offers a spectrum rather than one mechanism. A developer picks from four trust models:

- **Reputation**: client feedback, cheap and immediate, suited to low-stake tasks.
- **Crypto-economic**: stake-secured re-execution, where a validator re-runs the job and risks a bond.
- **zkML**: a zero-knowledge proof that a specific model produced a specific output.
- **TEE attestation**: a hardware enclave attesting that the registered code is what actually ran.

The `supportedTrust` field in the registration file advertises which of these an agent stands behind. The design does not force a choice; it standardises how the choice is expressed and read.

The whole lifecycle, from minting an identity through collecting feedback and validation, is shown below.

![ERC-8004 agent lifecycle across the registries, from registration and wallet verification to feedback and validation]({{site.url_complet}}/assets/article/blockchain/ai/erc-8004/agent-registration-lifecycle-workflow.png)

## Security considerations

- Sybil attacks remain possible, since anyone can inflate a fake agent's reputation, and the protocol's answer is not to prevent them outright but to make every signal public under a shared schema, so that reputation systems can filter by reviewer, which the read functions already support. 
  - On-chain pointers and hashes cannot be deleted, which preserves the audit trail. 
  - Validator incentives and slashing live in the validation protocols, not here.

- ERC-8004 cryptographically ties the registration file to the on-chain agent, but it cannot guarantee that an agent's advertised capabilities are functional or non-malicious. That gap is exactly what the three trust models exist to close, each at a different cost and assurance level.

## Adoption in practice

ERC-8004 occupies a specific slot in what its researchers call the agentic-internet stack. 

- Communication protocols (A2A and MCP) make an agent legible;

- ERC-8004 makes it accountable, and a payment rail makes it payable. 

Coinbase's x402 fills that last slot by reviving the HTTP 402 status code: 

- an agent settles stablecoins inside the HTTP request and response cycle, and rather than touching the chain on every call it issues cryptographically signed vouchers that batch and settle later, which is what lets an agent field thousands of paid queries per minute. 
- [The Graph connects discovery to this flow](https://thegraph.com/blog/understanding-x402-erc8004/) by indexing the ERC-8004 registries across eight chains into a cross-chain directory, so one agent can check another's identity, reputation, and validation status before it engages, pay for the work through x402, and resell the result to a third agent.

The subsections below map the ecosystem forming around the standard: the chains that carry the registries and their cost, what the on-chain data shows, an explorer that makes it browsable (AltLayer's 8004scan), and the products wiring ERC-8004 into execution (MetaMask), validation (Oasis and ZyFai), payments (Brickken), and live agents (Toppa and Agentic Eye).

### Blockchain support

The Identity and Reputation registries went live on Ethereum mainnet on [29 January 2026](https://www.forbes.com/sites/digital-assets/2026/02/05/ai-agents-gain-trust-via-ethereum-erc-8004-on-mainnet/), and deployment has since spread widely. The [official contracts repository](https://github.com/erc-8004/erc-8004-contracts) lists the two registries on more than thirty mainnet chains, among them Base, Arbitrum, Optimism, Polygon, BSC, Celo, Linea, Scroll, Taiko, Monad, and 0G, along with a matching set of testnets. The Validation Registry is the exception. It is not deployed on any chain: that part of the spec is still under active revision and discussion with the TEE community, with a follow-up update expected later in 2026. Its absence shapes the whole adoption picture below.

Several EVM chains have published dedicated ERC-8004 deployment guides: [Taiko](https://taiko.xyz/guides/erc-8004-trustless-agent-standard) on its Type 1 ZK-EVM, [Monad](https://docs.monad.xyz/guides/erc-8004) on its high-throughput L1, and [Celo](https://docs.celo.org/build-on-celo/build-with-ai/8004), where an agent can register and give feedback while paying gas in stablecoins through Celo's fee abstraction, which is why the live agents later in this section settle in cUSD. On mainnet all of them expose the Identity Registry at `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` and the Reputation Registry at `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63`, with the Validation Registry still absent.

The shared address across unrelated chains is by design. The reference registries are deployed deterministically, so the canonical instance lands at the same address on every chain in a given environment, with the leading `0x8004` a vanity prefix echoing the ERC number. Every mainnet lands on the pair above; the Sepolia testnets share a different canonical pair, `0x8004A818...` for Identity and `0x8004B663...` for Reputation, which is the pair ZyFai and Brickken use on Base Sepolia below.

The registration flow is identical wherever the registries run: prepare the JSON file, `register()` to mint the ERC-721, `setAgentURI()` to point at the file, an optional `setAgentWallet()`, then `giveFeedback()` over time. Because ERC-8004 uses one shared registry per chain, an identity minted on an L2 can still transact elsewhere, and on a settlement rollup like Taiko it inherits Ethereum L1 finality.

### Cost

Gas is the reason activity gravitates to L2s and high-throughput L1s. Taiko's guide gives the clearest figures, comparing its Type 1 ZK-EVM against Ethereum L1:

| Operation | Ethereum L1 | Taiko |
| --- | --- | --- |
| Agent registration | $1 to $5 | around $0.01 |
| Identity update | $0.50 to $3 | under $0.01 |
| Reputation feedback | $0.50 to $3 | under $0.01 |

For agents expected to register once and then post feedback continuously, that ratio decides where they live. The cross-organisational authorship, spanning MetaMask, the Ethereum Foundation, Google, and Coinbase, gave the standard unusual reach for a `Draft`, and ENS, EigenLayer, and The Graph have signalled integrations.

### What the on-chain data shows

Raw adoption looks large and is partly hollow. The [first empirical study of ERC-8004](https://arxiv.org/abs/2606.26028), from a group at Imperial College London, Ohio State, Bristol, CSIRO, and Manchester, crawled Ethereum, BSC, and Base through 13 May 2026 and counted more than 170,000 registered agents and over 150,000 feedback records. Most of that is noise. Registration is dominated by batch-minted placeholders and templated deployments, ownership is concentrated (a Gini coefficient of 0.733 on Ethereum and 0.708 on Base), and many identities never resolve to anything: 53% of Ethereum registrations carry no URI at all, and only 3% to 15% across the three chains expose a valid registration file with at least one live service endpoint. Raw registration volume, in other words, is a poor proxy for how many agents actually exist.

The reputation picture is worse, and it turns the standard's own Sybil caveat into measured fact. The study finds that the Reputation Registry, as deployed, meets none of the four conditions for a trustworthy score: the values are not commensurable, the feedback is rarely tied to a verifiable interaction, a single input can move the aggregate, and a reputation can be fabricated or destroyed for cents (a median of $0.055 on Ethereum, and fractions of a cent on BSC and Base). Coordinated reviewers account for 73.6%, 59.2%, and 90.6% of all reviewers on Ethereum, BSC, and Base. Strip their feedback out and 15.5%, 72.3%, and 89.4% of rated agents are left with no valid feedback at all. This is the concrete reason the `getSummary` read function forces a caller-chosen reviewer set: an unfiltered score reflects mostly Sybils.

### Discovery and explorers: AltLayer's 8004scan

Raw registry events are hard to read directly, the same problem block explorers solved for tokens. [AltLayer's 8004scan](https://docs.altlayer.io/altlayer-documentation/8004-scan/overview) is an explorer for the agent economy, a web application for browsing agents registered under ERC-8004. It lists featured and live agents, lets a user filter by domain such as data access, workflow, or orchestration, and shows activity feeds of agent interactions alongside network stats meant to signal growth and ecosystem health. It adds reputation and behaviour tracking so a prospective client can weigh an agent before engaging, and a builder section for launching a new ERC-8004 agent. Under the surface it indexes the on-chain registration metadata, the same events the empirical study crawled, and renders them for people rather than for a subgraph query.

AltLayer positions this inside a wider protocol for rollups and agents: its Restaked Rollups framework secures rollups through EigenLayer restaking, while a suite of x402 and ERC-8004 products, of which 8004scan is the explorer, targets agent discovery, reputation, and payment. The explorer is a sign that the tooling layer, not just the registries, is filling in.

### Execution: MetaMask server wallets

The registries say who an agent is and how it is rated, but not how it signs a transaction safely. [MetaMask's server-wallet design](https://docs.metamask.io/tutorials/design-server-wallets) covers that side and treats an ERC-8004 identity as the thing that expresses what an agent intends to do. 

A server wallet is a backend signer that holds keys on behalf of the agent: the agent authenticates a request, and the wallet returns a signature to submit on-chain.

The design keeps the signing key away from the agent through a dual-key split. 

- The agent holds only an authentication key, while control of the on-chain account comes from a separate signing key it never sees. 
- That signing key lives inside a trusted execution environment, an AWS Nitro-style enclave with no external networking and no persistent storage, which performs key generation, decryption, policy evaluation, and signature production in one place. 
- Before any signature is produced, the request passes a policy layer: spend limits, scope limits, chain limits, frequency limits, simulation checks, and optional human approval. 
- Pairing a registered ERC-8004 identity with a policy-bounded server wallet is what makes an agent transaction attributable and verifiable from end to end, with a tamper-evident record of the session. 
- While the production offering is being finalised, the tutorial points builders at the MetaMask Node.js Embedded Wallets SDK for the same pattern.

### Validation: Oasis ROFL and confidential compute

The Validation Registry is not deployed on any chain, so on-chain objective verification does not yet exist through the standard itself. [Oasis fills the gap off the registry](https://docs.oasis.io/build/use-cases/trustless-agent) by attaching the TEE trust model directly to registration. Its guide runs an Eliza agent inside ROFL, the Oasis confidential-compute framework, so the agent executes in a hardware enclave whose code can be audited and proved to be the deployed instance, with no silent alteration.

How it works:

- A `rofl-8004` service derives an Ethereum address for the agent, and once that address holds a little ether for fees, the agent is registered and validated in the ERC-8004 registry automatically. 
- ROFL performs the startup attestation of the container and injects secrets, such as an `OPENAI_API_KEY`, as end-to-end-encrypted environment variables stored on-chain, while registry interaction runs on Sapphire, the Oasis confidential EVM. 
- The result is the high-assurance end of the tiered trust model realised in production: an agent's trustworthiness rests not on a reputation score but on a hardware attestation that the registered code is what actually runs.

### zkML validation and DeFi: ZyFai

Oasis attests that the right code ran; [ZyFai](https://docs.zyf.ai/docs/product/execution/8004) proves that it ran correctly. ZyFai is a DeFi execution platform whose agents rebalance yield positions across pools. Its logic is a deterministic rule set, so the same input always produces the same verifiable output, which is what makes the result provable in the first place.

Each rebalance is checked by a zero-knowledge circuit. ZyFai uses a Circom 2.0 circuit with fifteen public signals enforcing five constraints on the move, among them a minimum APY improvement of 0.1% and stability bounds on APY and TVL. ZyFai deploys its own `RebalancerVerifier` for this and links each proof to the agent's ERC-8004 identity, so the agent builds a tamper-proof history of verified actions rather than self-reported scores. Its docs describe this as populating the Validation Registry, but since that registry is not deployed anywhere yet, ZyFai is best read as a preview of the standard's zkML trust model built on a custom verifier rather than the registry itself. It is also the closest thing in this section to a DeFi use case, though ZyFai is an agent-native product rather than an established protocol.

It runs on testnets so far, Base Sepolia (chain 84532) and Ethereum Sepolia (chain 11155111), using the canonical Sepolia Identity and Reputation registries (`0x8004A818...` and `0x8004B663...`) alongside its own `RebalancerVerifier` contract on each.

### Payments and identity: Brickken's x402 API

The payments side has a concrete implementation as well. [Brickken exposes an x402-paid API](https://docs.brickken.com/api-reference/endpoint/agentic-methods-x402) that wires ERC-8004 identity and reputation directly into agent operations on Base. Its `/x402/agent/register` endpoint takes an agent's `name`, `description`, `image`, `aiModelName`, and `services`, then writes them to the ERC-8004 registries on Base Sepolia, at the canonical Sepolia addresses `0x8004A818...` for identity and `0x8004B663...` for reputation (the same testnet pair Celo Sepolia uses).

What makes it a useful reference is how it joins identity to payment. Every agentic operation runs as a two-phase flow:

- The agent first prepares an unsigned transaction, which is free.
- The agent then sends the operation, at which point an x402 USDC payment is charged using [EIP-3009](https://eips.ethereum.org/EIPS/eip-3009) transfer authorization.

The caller picks between a Brickken-relayed mode, where the API signs and pays gas while the user only authorises the x402 payment, and a client-signed mode, where the user keeps key custody but still settles the fee through x402. The same surface manages agent-owned ERC-20 tokens, so one registered agent can hold an identity, accrue reputation, and move value under a single API. Brickken, a real-world-asset tokenisation platform also behind [ERC-7943 (uRWA)](https://eips.ethereum.org/EIPS/eip-7943), shows the identity-plus-payment pattern reaching application platforms rather than only wallets and base infrastructure.

### Live agents on Celo: Toppa and Agentic Eye

Most of this section is infrastructure. [Toppa](https://toppa.cc/docs/) is a concrete agent that puts the whole stack together. It is a consumer assistant on Telegram and WhatsApp that buys airtime and mobile data, pays utility bills, and buys gift cards, settling in cUSD on Celo, and it accepts natural-language requests and voice notes. Its ERC-8004 registration lives on Celo mainnet as agent ID 1870, and its agent card at the conventional `https://api.toppa.cc/.well-known/agent-card.json` path declares MCP, A2A, and x402 support, exactly the `services` list the registration file is built to carry.

The three protocols map onto the roles the standard keeps separate. A2A, at `https://api.toppa.cc/a2a` over JSON-RPC, handles machine-to-machine delegation. MCP, at `https://api.toppa.cc/mcp` with thirteen tools over streamable HTTP, exposes Toppa to clients such as Claude Desktop. x402 handles payment: a caller requests pricing, receives an HTTP 402 with a recipient address, transfers cUSD on-chain, and resubmits with the transaction proof, against a flat 1.5% fee. Discovery endpoints for operators, billers, and gift cards are free, while fulfilment endpoints such as `/send-airtime` and `/pay-bill` are paid. Its computed reputation is visible on ERC-8004 explorers, including its [8004scan profile](https://8004scan.io/users/0x558e7bfaf2cf1a494f44e50d92431afc060c9d12). Toppa is a useful reference because it uses the standard as intended: one on-chain identity, communication over A2A and MCP, payment over x402, and a reputation any explorer can read.

[Agentic Eye](https://agenticeye.co/for-agents) is a second Celo agent, registered as [agent ID 1865](https://8004scan.io/agents/celo/1865) under the on-chain name `agenticeye.x`. It is a content-intelligence service: on each call it pulls live data from fourteen sources across YouTube, TikTok, Reddit, and Google Trends and scores the opportunity, data a general model cannot reach from its training set. Other agents discover it through the ERC-8004 registry and card, then pay per call over x402, which it accepts in several tokens, cUSD, USDC, and USDT on Celo and USDC on Base, against tiered pricing from $0.10 to $8.00 per call. Two production agents sharing one chain, one identity standard, and one payment rail is a small but real sign of an agent-native cluster forming on Celo rather than a single isolated deployment.

## Conclusion

ERC-8004 is a discovery and trust layer, not a communication or payment protocol. Its Identity Registry gives an agent a transferable ERC-721 handle that resolves to a structured registration file. Its Reputation Registry records signed, filterable feedback on-chain while keeping detail off-chain. Its Validation Registry lets validators post verdicts that other contracts can read. Around these sits a tiered trust model that ranges from cheap reputation to hardware attestation, expressed through a single `supportedTrust` field. The standard is still `Draft` and its interfaces can change, but the registries are already deployed and the surrounding infrastructure is taking shape.

The mindmap below summarises the standard.

![Mindmap of ERC-8004 covering its purpose, the identity, reputation and validation registries, the trust models, and adoption]({{site.url_complet}}/assets/article/blockchain/ai/erc-8004/2026-07-06-erc-8004-trustless-agents-mindmap.png)

## Frequently Asked Questions

**Q: Why does ERC-8004 build the Identity Registry on ERC-721 instead of a bespoke registry?**

Reusing ERC-721 with the URIStorage extension makes every agent immediately browsable, transferable, and manageable in existing NFT tooling, with no new interface for wallets and marketplaces to learn. The `agentId` is just the ERC-721 `tokenId`, and the `agentURI` is the `tokenURI` pointing at the registration file. Ownership transfer and operator delegation come for free from ERC-721, which is why transferring the token transfers the agent.

**Q: What is the `agentWallet` key, and why is it reset when the agent is transferred?**

The `agentWallet` is a reserved metadata key holding the address where the agent receives payments. It cannot be set through the generic `setMetadata()` or during `register()`; it can only be changed through `setAgentWallet()`, which requires an EIP-712 signature (for an EOA) or an ERC-1271 signature (for a smart-contract wallet) proving control of the new address. On transfer it is cleared to the zero address, so a buyer or recipient of the agent token cannot silently inherit a payment address they have not re-proved. This blocks an attack where a payment address rides along with a transferred agent.

**Q: How does the Reputation Registry decide what is stored on-chain versus off-chain?**

The numeric signal is stored on-chain: `value`, `valueDecimals`, the two tags, `isRevoked`, and the per-client `feedbackIndex`. The richer context, meaning the `endpoint`, `feedbackURI`, and `feedbackHash`, is emitted in the `NewFeedback` event but not written to storage. This keeps small, composable numbers cheap to read from other contracts while pushing verbose detail into an off-chain file, usually on IPFS. When the file is not content-addressed, `feedbackHash` is its KECCAK-256 hash so integrity can still be checked.

**Q: Why must the `clientAddresses` filter in `getSummary` be non-empty?**

Because anyone can post feedback, an unfiltered aggregate is trivially manipulable through Sybil accounts inflating an agent's score. Requiring the caller to pass a specific set of reviewer addresses forces aggregation to run against a chosen, trusted subset rather than the whole open population. The standard treats this as the on-chain half of spam mitigation, with more sophisticated reviewer-trust systems expected to emerge off-chain on the same public data.

**Q: How do the Reputation and Validation registries differ, and when would you use each?**

The Reputation Registry captures subjective client experience: scores, uptime, success rate, and similar signals that accumulate over time. The Validation Registry captures objective verification of a specific piece of work: an owner opens a `validationRequest` referencing the inputs and outputs, and a named validator returns a `response` from 0 to 100. Reputation suits low-stake, cumulative judgement; validation suits a high-stake task where you want a stake-secured re-execution, a zkML proof, or a TEE attestation of one result. In the tiered trust model they sit at different points on the cost and assurance curve.

**Q: If an agent is registered on one chain, can it work on another?**

Yes. The registries are per-chain singletons, but the standard states that an agent registered and receiving feedback on chain A can still operate and transact on other chains, and an owner may register the same agent on several chains. The registration file's `services` list can advertise wallet addresses and endpoints on chains where the agent is not registered at all, so identity on one chain does not confine operation to it.

## References

### Specifications

- [ERC-8004: Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004)
- [EIP-155: Simple replay attack protection](https://eips.ethereum.org/EIPS/eip-155)
- [EIP-712: Typed structured data hashing and signing](https://eips.ethereum.org/EIPS/eip-712)
- [EIP-3009: Transfer With Authorization](https://eips.ethereum.org/EIPS/eip-3009)
- [EIP-7702: Set EOA account code](https://eips.ethereum.org/EIPS/eip-7702)
- [ERC-721: Non-Fungible Token Standard](https://eips.ethereum.org/EIPS/eip-721)
- [ERC-1271: Standard Signature Validation Method for Contracts](https://eips.ethereum.org/EIPS/eip-1271)
- [ERC-7943: uRWA - Universal Real World Asset Interface](https://eips.ethereum.org/EIPS/eip-7943)
- [CAIP chain-agnostic identifiers](https://chainagnostic.org/)

### Deployments and integrations

- [ERC-8004 reference contracts and deployment addresses - GitHub](https://github.com/erc-8004/erc-8004-contracts)
- [ERC-8004 Trustless Agent Standard guide - Taiko](https://taiko.xyz/guides/erc-8004-trustless-agent-standard)
- [ERC-8004 guide - Monad docs](https://docs.monad.xyz/guides/erc-8004)
- [Build with AI: ERC-8004 - Celo docs](https://docs.celo.org/build-on-celo/build-with-ai/8004)
- [Design server wallets for AI agents - MetaMask docs](https://docs.metamask.io/tutorials/design-server-wallets)
- [Trustless Agent with ERC-8004 registration and validation - Oasis docs](https://docs.oasis.io/build/use-cases/trustless-agent)
- [ERC-8004 execution and zkML validation - ZyFai docs](https://docs.zyf.ai/docs/product/execution/8004)
- [Understanding Coinbase's x402 and Ethereum's ERC-8004 - The Graph](https://thegraph.com/blog/understanding-x402-erc8004/)
- [Agentic methods and x402 - Brickken API reference](https://docs.brickken.com/api-reference/endpoint/agentic-methods-x402)
- [8004scan agent explorer - AltLayer docs](https://docs.altlayer.io/altlayer-documentation/8004-scan/overview)
- [Toppa - an ERC-8004 agent on Celo](https://toppa.cc/docs/)
- [Agentic Eye - an ERC-8004 agent on Celo](https://agenticeye.co/for-agents)

### Ecosystem analysis and reporting

- [Can Trustless Agents Be Trusted? An Empirical Study of the ERC-8004 Ecosystem - arXiv](https://arxiv.org/abs/2606.26028)
- [AI Agents Gain Trust Via Ethereum: ERC-8004 On Mainnet - Forbes](https://www.forbes.com/sites/digital-assets/2026/02/05/ai-agents-gain-trust-via-ethereum-erc-8004-on-mainnet/)
- [ERC standards for AI agents - survey article](https://rya-sge.github.io/access-denied/2026/07/06/erc-ai-agents-ethereum-standards/)

### Discussion

- [ERC-8004: Trustless Agents - Fellowship of Ethereum Magicians](https://ethereum-magicians.org/t/erc-8004-trustless-agents/25098)

### Tools

- [Claude Code](https://claude.com/product/claude-code)
