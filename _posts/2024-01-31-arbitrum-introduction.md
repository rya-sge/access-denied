---
layout: post
title:  "Introduction to Arbitrum"
date:   2024-01-31
lang: en
locale: en-GB
categories: blockchain ethereum
tags: ethereum arbitrum layer2 nitro nova orbit optimism
description: Introduction to Arbitrum, an optimistic layer2 designed to scale Ethereum, and its ecosystem Arbitrum Nova, Orbit and One.
image: /assets/article/blockchain/ethereum/arbitrum/1223_Arbitrum_Logos_Logomark_RGB.png
---

**Arbitrum** is a technology designed to scale Ethereum. The main product is **Arbitrum Rollup**, an Optimistic rollup protocol that uses Ethereum for its security.

## Arbitrum main points

### Concepts

- **Optimistic Rollup:** Arbitrum employs the optimistic rollup approach, where it assumes the validity of transactions by default and only challenges occur in case of disputes. This allows for faster transaction processing compared to on-chain validation.
- **Validation Game:** The validation game is a mechanism to challenge the validity of transactions during a specific period. If a challenge is successful, the disputed transaction is rolled back.
- **Ethereum Compatibility:** Arbitrum is fully compatible with the Ethereum Virtual Machine (EVM), enabling seamless migration for existing Ethereum projects. Developers can use the same tools and languages to build on Arbitrum.
- **Reduced Gas Fees and Faster Transactions:** By processing transactions off-chain and submitting a summary to the Ethereum mainnet, Arbitrum significantly reduces gas fees and improves transaction confirmation times.

### Main Components

- Arbitrum Rollup, an optimistic rollup in the Ethereum ecosystem for scaling Ethereum smart contracts.
- Arbitrum **Nitro** is a rollup network with a fraud proof system implemented with EVM compatibility.
- Arbitrum **Nova** is based on the Arbitrum AnyTrust protocol. Since it stores data through the Data Availability Committee (DAC) rather than the Ethereum network, it can provide higher scalability than Arbitrum One.
- Arbitrum **Orbit** is a framework that allows developers to easily develop L3 networks at the top of Arbitrum (own Rollup and AnyTrust chains).

Reference: [1. koreablockchainweek - Arbitrum 101](https://koreablockchainweek.com/blogs/kbw-blog/arbitrum-101), [docs.arbitrum - The Arbitrum Suite](https://docs.arbitrum.io/welcome/get-started#the-arbitrum-suite)

## Arbitrum Ecosystem Components

![orbit chain logo]({{site.url_complet}}/assets/article/blockchain/ethereum/arbitrum/orbit_chain.jpeg)

Reference: [forum.arbitrum.foundation - The Arbitrum Expansion Program and developer Guild](https://forum.arbitrum.foundation/t/the-arbitrum-expansion-program-and-developer-guild/20722?utm_source=substack&utm_medium=email)



### Arbitrum AnyTrust

The Arbitrum protocol requires that all Arbitrum nodes, including  validators, have access to the data of every L2  transaction in the Arbitrum chain's inbox. 

In the Rollup system, used by **Arbitrum One**, the rollup provides  data access by posting the data on L1  Ethereum as calldata, which is costly.

Arbitrum AnyTrust reduces the costs by accepting a mild trust assumption. Indeed, AnyTrust relies on an external Data Availability Committee (DAC) to store data and provide it on demand. 

Reference: [AnyTrust](https://docs.arbitrum.io/inside-anytrust)

### Arbitrum Nitro Stack

#### Components

The Arbitrum Nitro stack consists of core components like the

- Arbitrum Rollup contract; 
- [Arbitrum Bridge / Canonical token bridge](https://docs.arbitrum.io/for-devs/concepts/token-bridge/token-bridge-erc20#other-flavors-of-gateways)
  - Asset contracts (e.g ERC20)
  - Gateway: Pairs of contracts (one on L1, one on L2) that implement a particular type of cross-chain asset bridging.
  - Routers: Exactly two contracts (one on L1, one on L2) that route each asset to its designated gateway.
- [Arbitrum Sequencer](https://docs.arbitrum.io/sequencer)
  - Specially designated Arbitrum full node which, under normal conditions, is responsible for submitting users’ transactions onto L1.
  -  The Sequencer is currently a single and centralized entity. In the future, eventually, it could be replaced by a distributed committee of sequencers which come to consensus on ordering.
  - It can’t, in principle, derive security directly from layer 1

These components work together to form the foundation of the Arbitrum scaling solution.

#### Schema

Here a schema from the [Arbitrum documentation](https://docs.arbitrum.io/inside-arbitrum-nitro/)

![orbit chain logo]({{site.url_complet}}/assets/article/blockchain/ethereum/arbitrum/arbitrum-sequencer-schema.png)

#### Improvements

Nitro offers several improvements including 

- Advanced calldata compression; 
- Separate contexts for common execution and fault proving;
- Ethereum L1 gas compatibility.

Reference: [docs.arbitrum.io/for-devs/concepts/public-chains#nitro](https://docs.arbitrum.io/for-devs/concepts/public-chains#nitro), [docs.arbitrum.io/inside-arbitrum-nitro/](https://docs.arbitrum.io/inside-arbitrum-nitro/)

### Arbitrum One

**Arbitrum One** is a Layer 2 (L2) optimistic rollup chain that implements the Arbitrum Rollup protocol and settles to Ethereum's Layer 1 (L1) chain. 

- It is a live and production-ready instance of *Arbitrum* that developers and users can interact with. 
- It lets you build Ethereum dApps with low transaction costs.

Arbitrum One uses Ethereum to guarantee its security and contrary to Arbitrum Nova, there is no additional trust assumptions. 

Reference: [docs.arbitrum.io/for-devs/concepts/public-chains#arbitrum-one](https://docs.arbitrum.io/for-devs/concepts/public-chains#arbitrum-one)

### Arbitrum Nova 

- **Arbitrum Nova** is a high-performance alternative to Arbitrum One's chain. While Arbitrum One implements the purely trustless Rollup protocol, Arbitrum Nova implements the mostly trustless [AnyTrust](https://docs.arbitrum.io/inside-anytrust) protocol. 
- Like Arbitrum One, Arbitrum Nova uses Arbitrum's Nitro technology stack 
- They key difference between Rollup and AnyTrust is that the AnyTrust protocol introduces an additional trust assumption in the form of a data availability committee (DAC).
- This committee (detailed below) is responsible for expediting the process of storing, batching, and posting L2 transaction data to Ethereum's L1. 
- This lets you use Arbitrum in scenarios that demand performance and affordability, while Arbitrum One is optimal for scenarios that demand Ethereum's pure trustlessness. Arbitrum Nova is designed for applications that require a higher transaction throughput and don’t require the full decentralization that rollups provide.

Reference: [docs.arbitrum.io/for-devs/concepts/public-chains](https://docs.arbitrum.io/for-devs/concepts/public-chains)

### Arbitrum Orbit

Arbitrum Orbit allows the creation of blockchains / dapp on top of Arbitrum one or Nova. With it, you can create your own self-managed Arbitrum Rollup and AnyTrust chains.

Its main advantages are:

- Customization (privacy, permission access, gas token, governance, and more.)
- EVM compatibility Via Stylus 
- Low fee
- Account Abstraction
- "Ethereum security"
- Communication possible between different Orbit chains 

Reference: [A gentle introduction: Orbit chains](https://docs.arbitrum.io/launch-orbit-chain/orbit-gentle-introduction), [Arbitrum Launches Its Layer 3 Solution](https://cryptorank.io/insights/analytics/arbitrum-launches-its-layer-3-solution)



## Arbitrum classic (deprecated)

Classic is  the technology used by Arbitrum  before Nitro and is no deprecated since August 2022

The technology classic implements  the Arbitrum’s L2 state machine— known as [“ArbOS”](https://docs.arbitrum.io/arbos/) 

Arbitrum Classic used the Arbitrum Virtual Machine, a cumstom virtual machine, instead of the EVM

Nitro instead used a version of Geth to be EVM compatible. The code is generally directly compatibles in the native language and when a challenge comes in from the fraud proof system, it is compiled in Wasm bytecode during dispute periodes

Reference:

- [docs.arbitrum.io/why-nitro#nitro-vs-classic](https://docs.arbitrum.io/why-nitro#nitro-vs-classic)
- [github.com/OffchainLabs/arbitrum-classic](https://github.com/OffchainLabs/arbitrum-classic)
- [1. koreablockchainweek - Arbitrum 101](https://koreablockchainweek.com/blogs/kbw-blog/arbitrum-101)
- [medium.com/offchainlabs/how-arbitrum-rollup-works-39788e1ed73f](https://medium.com/offchainlabs/how-arbitrum-rollup-works-39788e1ed73f)

### Stylus

Stylus is a developer toolkit provided by Offchain Labs to simplify the process of building decentralized applications (DApps) on the Arbitrum chain. It includes tools and resources for developers. Stylus lets you write smart contracts in programming languages that compile down to WASM, such as Rust, C, C++, and many others.

Reference: [docs.arbitrum.io/stylus/stylus-gentle-introduction](https://docs.arbitrum.io/stylus/stylus-gentle-introduction)

## Examples of Projects Using Arbitrum

- Uniswap V3 is available on Arbitrum, swaps can be up to 22x [cheaper](https://l2fees.info/) on Arbitrum than mainnet,  see [blog.uniswap.org/scaling-summer-arbitrum](https://blog.uniswap.org/scaling-summer-arbitrum) & [blog.uniswap.org/uniswap-arbitrum-alpha](https://blog.uniswap.org/uniswap-arbitrum-alpha)

- Balancer is also available on Arbitrum, see [Balancer Protocol Live on Arbitrum to Scale DeFi Liquidity](https://medium.com/balancer-protocol/balancer-protocol-live-on-arbitrum-to-scale-defi-liquidity-c94c16ba9a43)

- SushiSwap is also available on Arbitrum Nova, see [coinlive.com](https://www.coinlive.com/news-flash/779)

## Lifecycle of an Arbitrum Transaction

1. Sequencer receives transaction (Directly / offchain or form L1) from a client
2. Sequencer orders transaction (off-chain)
3. Sequence posts transaction in a batch (on-chain)
4. Validator asserts Rollup Block (RB) that includes transaction
5. RB is confirmed on L1

Reference: [docs.arbitrum.io/tx-lifecycle](https://docs.arbitrum.io/tx-lifecycle)

## Security

### Detect Fraud

#### Optimism 

Ethereum adopts an [“innocent until proven guilty"](https://insights.deribit.com/market-research/making-sense-of-rollups-part-2-dispute-resolution-on-arbitrum-and-optimism/) attitude to Arbitrum. Layer 1 initially “optimistically assumes” activity on Arbitrum is following the proper rules. 

If a violation occurs (i.e., somebody claims “now I have all of your money”),

- This claim can be disputed back on L1; 
- Fraud will be proven, the invalid claim disregarded, and the malicious party will be financially penalized.

#### Assertion tree

- **Arbitrum state**: The state of an Arbitrum chain is confirmed back on Ethereum via "assertions," aka "disputable assertions" or "DAs." These are claims made by Arbitrum validators about the chain's state. To make an assertion, a validator must post a bond in Ether.
- **Happy / Common scenario**: all outstanding assertions will be valid; i.e., a valid assertion will build on another valid assertion, which builds on another valid assertion, and so on. 
- **Confirmation time**: After the dispute period (~ 1 week) passes and an assertion goes unchallenged, it can be confirmed back on L1.
- **Conflict / fraud**: If, however, two or more conflicting assertions exist, the Assertion Tree bifurcates into multiple branches:

Reference: [docs.arbitrum.io/assertion-tree](https://docs.arbitrum.io/assertion-tree)

#### Interactive proving

Arbitrum uses interactive proving. It refers to resolving disputes through interaction between the disputing parties. 

Arbitrum uses a method called dissection, in which the two parties interact to reduce N operations to → N/2 → N/4 → ... until one operation step remains, and the validity of this operation is judged.

For the moment, only [whitelisted validators](https://docs.arbitrum.foundation/state-of-progressive-decentralization) can participate in Arbitrum's fraud proof system.

References:

- [1. koreablockchainweek - Arbitrum 101](https://koreablockchainweek.com/blogs/kbw-blog/arbitrum-101)
- [Arbitrum - Challenge Protocol](https://www.youtube.com/watch?v=CbAEDS6RHJM)
- [2. docs.arbitrum.io/intro/](https://docs.arbitrum.io/intro/)
- [docs.arbitrum.io - Inside Arbitrum Nitro](https://docs.arbitrum.io/inside-arbitrum-nitro/)
- [docs.arbitrum.io - challenge-manager](https://docs.arbitrum.io/proving/challenge-manager)

### Accident

Since Arbitrum’s launch, its sequencer has halted **three times**. 

- 09.01.2022: [The first](https://x.com/arbitrum/status/1480165924355330051?s=20) was due to a bug in the sequencer’s batch submission mechanism, which lasted about 7 hours. 
- 07.06.2022: [The second](https://x.com/ArbitrumDevs/status/1666549893001887744?s=20) was due to the lack of the Ethereum gas fee of the sequencer and was resolved after an hour. 
- 15.12.2023: [The third](https://x.com/arbitrum/status/1735699786618020205?s=20) is due to the significant surge in network traffic provoked by Inscriptions, see a sustained surge of inscriptions triggered the sequencer to stop relaying transactions properly, see [status.arbitrum](https://status.arbitrum.io/clq6te1l142387b8n5bmllk9es)

Reference: [3. Patch Thursday — Risks on CEX’s Confirmation Number on Arbitrum and Optimism](https://medium.com/chainlight/patch-thursday-risks-on-cexs-confirmation-on-arbitrum-and-optimism-7ee25a1d58bf)

### Governance and Upgrade

The Arbitrum governance has two main bodies:

- **The DAO** - represented by holders of the $ARB token, and votes to pass proposals.
- **The Security Council** 
  -  is made up of a 9 of 12 multisig that can take quick action in case of an emergency 
  -  And a 7 of 12 multisig that can take slow action for routine upgrades that bypass the DAO vote.

According to a [L2Beat report](https://drive.google.com/file/d/182ycEW8C2wk5tGd3X1tG8oQfUy9WmSJk/view), the Security Council can perform emergency upgrades directly through the *UpgradeExecutor*, see also [github.com/ArbitrumFoundation/governance/#l1-upgrade-executor](https://github.com/ArbitrumFoundation/governance/blob/main/docs/overview.md#l1-upgrade-executor)

Such an upgrade can be executed instantly without any delay. 

Thus, the Security Council can instantly upgrade the chain. In case of emergency (security issue), it allows the Council to perform a patch "quickly" to save e.g. user founds.

But, it also means that If this Council acts maliciously, they can steal user funds. 

However, as indicated in the [L2Beat report](https://drive.google.com/file/d/182ycEW8C2wk5tGd3X1tG8oQfUy9WmSJk/view), the Security Council member list is publicly known, and the members are legally
bound (by a contract with Arbitrum Foundation) to act with integrity.

## Advantage and Disadvantage

### Advantages

The main advantages of Arbitrum is :

- low fees
- Scalability
- Inherits security from Ethereum  (can also be a disadvantage)
- Ethereum/EVM compatibility

See [Possibilities and Advantages of Using Arbitrum Compared to Ethereum](https://medium.com/@floating_monkey/possibilities-and-advantages-of-using-arbitrum-compared-to-ethereum-78a4cafc44d5)

### Disadvantages

Hallborn has made a good summary of the main disadvantages

- The long wait times for fraud proofs (7-day challenge periode)
- Vulnerability to attacks if the value in a roll-up exceeds the amount in an operator’s deposit
- Reliance on the L1 chain for security can be detrimental if the L1 chain gets compromised
- The long wait times before being able to withdraw funds back to Ethereum ([one week](https://docs.arbitrum.io/intro#q-this-dispute-game-obviously-takes-some-time-does-this-impose-any-sort-of-delay-on-arbitrum-users-transactions))
- In the absence of honest nodes, a malicious operator can exploit the system by posting invalid blocks and state commitments, allowing them to potentially steal funds
- The order of transactions can be tampered with by the centralized sequencers.

References. [A Comprehensive Guide to Arbitrum and its Security Features](https://www.halborn.com/blog/post/a-comprehensive-guide-to-arbitrum-and-its-security-features)

## [Milestones](https://l2beat.com/scaling/projects/arbitrum#milestones)

- 2023 Mar 23rd: ARB token airdrop

ARB token launched as a governance token for Arbitrum DAO. [Learn more](https://twitter.com/arbitrum/status/1638888588443111425)

- 2022 Aug 31st: Nitro Upgrade

Upgrade is live, introducing new architecture, increased throughput and lower fees.[Learn more](https://medium.com/offchainlabs/arbitrum-nitro-one-small-step-for-l2-one-giant-leap-for-ethereum-bc9108047450)

- 2021 Aug 31st: Mainnet for everyone

Whitelist got removed, there are no restrictions on who can transact with the network.



## FAQ

> How does Arbitrum Rollup compare to other Layer 2 scaling solutions, such as ZK-Rollups or Optimism? 

Contrary to Optimistic rollup, *ZK-Rollups* can provide immediate finality, since the fraud proof eliminates the need of the waiting period, which is one week for **Arbitrum**.

But *optimistic rollup* does not need to provide data since every transaction is assumed to be valid. Except if there is a challenge (fraud-proof claim), the costs are generally cheaper since you reduce the quantity of data to submit.

Reference:

- [Zero-Knowledge vs. Optimistic Rollups Explained: Which One is Better for Blockchain Games?](https://www.immutable.com/blog/zero-knowledge-vs-optimistic-rollups-explained-which-one-is-better-for-blockchain-games).

- [ZK-Rollups vs. Optimistic Rollups: What’s The Difference?](https://www.nervos.org/knowledge-base/zk_rollup_vs_optimistic_rollup)

- [Optimistic Rollups vs. Zero-Knowledge (ZK) Rollups: How Do They Work?](https://www.blockchain-council.org/ethereum/optimistic-rollups-vs-zero-knowledge-rollups/)



> What are the trade-offs and limitations of using Arbitrum Rollup for dApp development and deployment? 

- Centralized sequence and outage

At the moment, the sequencer is centralized. Since it is responsible for batching the transactions, the network may experience an outage if it stops working. It was the case [in December](https://status.arbitrum.io/clq6te1l142387b8n5bmllk9es) when there was an increase in traffic due to Inscriptions.

- Possible incompatibility with smart contract

You can have minor differences with Ethereum for some opcode. In the future, it is still possible that a new opcode will not be immediately available on Arbitrum, it was e.g. the case for `PUSH0`.

The complete list is available on [rollup.code](https://www.rollup.codes/arbitrum-one), see also my answers on an interview question about Layer2 [RareSkills Solidity Interview Answers - Hard](https://rya-sge.github.io/access-denied/2024/03/04/solidity-interview-question-rareskills-hard/#optimistic-rollup-and-a-zk-rollup)



> How can users and developers interact with Arbitrum Rollup chains, and what tools and services are available to support them?

Since Arbitrum is EVM compatible, you can use the same main developments tools as for Ethereum e.g [Foundry](https://book.getfoundry.sh) or [Hardhat](https://hardhat.org)

See also [docs.arbitrum.io/development-frameworks](https://docs.arbitrum.io/for-devs/dev-tools-and-resources/development-frameworks) and [Web3 libraries and tools](https://docs.arbitrum.io/for-devs/dev-tools-and-resources/web3-libraries-tools)

An explorer for Arbitrum is also available at the following address: [arbiscan.io](https://arbiscan.io)



## Main References

[1. koreablockchainweek - Arbitrum 101](https://koreablockchainweek.com/blogs/kbw-blog/arbitrum-101)

[2. docs.arbitrum.io/intro/](https://docs.arbitrum.io/intro/)

[3. Patch Thursday — Risks on CEX’s Confirmation Number on Arbitrum and Optimism](https://medium.com/chainlight/patch-thursday-risks-on-cexs-confirmation-on-arbitrum-and-optimism-7ee25a1d58bf)

[4.L2Beat report](https://drive.google.com/file/d/182ycEW8C2wk5tGd3X1tG8oQfUy9WmSJk/view)

5.ChatGPT with the input "Explains me Arbitrum, a blockchain rollup, the different concept associated and its ecosystem. Talk also about Arbitrum anyTrust, stylus, Arbitrum Nitro stack, Arbitrum One and Arbitrum Nova. Cite example which uses Arbitrum for their project".

6.The FAQ questions (not the answers) have been generated by Copilot.
