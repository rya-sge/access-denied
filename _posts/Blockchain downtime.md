---
layout: post
title: "Blockchain downtime"
date:   2025-11-10
lang: en
locale: en-GB
categories: blockchain ethereum 
tags: gas
description: Blockchain downtime overview
image: 
isMath: false
---



| Blockchain                    | Check<br />Current status                            | Date of downtime / major halt                                | Notes                                                        |
| ----------------------------- | ---------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Bitcoin (mainnet)             | [bitcoin.org](https://bitcoin.org/en/alerts)         | Various historical incidents: e.g., a network split bug in 2013 that lasted ~6 hours. [Reddit - Has the Bitcoin Blockchain been functional 100% of the time? If not, when?](https://www.reddit.com/r/BitcoinBeginners/comments/o7gog6?) | Broadly the Bitcoin network is considered to have extremely high uptime; exact formal “downtime” events are rare and often partial rather than full halts. |
| Ethereum (mainnet)            |                                                      | -                                                            |                                                              |
| Avalanche (C-Chain / Mainnet) | [Avalanche status](https://status.avax.network)      | ~ February 23, 2024 — ~5 hour outage due to a client‐code bug. [Blockworks](https://blockworks.co/news/avalanche-blockchain-downtime)<br />[Official source](https://status.avax.network/incidents/qmx0s7zk6gkm) / [Official source 2](https://status.avax.network/incidents/4vq54hv6b9t4) | The C-Chain stopped producing blocks around 6:30 am ET and resumed about 5 hours later. [Blockworks](https://blockworks.co/news/avalanche-blockchain-downtime) |
| Polygon PoS                   | [Polygon Stautus](https://status.polygon.technology) | **July 2025**<br />~ July 30, 2025 — no blocks produced for ~2 hours. [finway.com.ua](https://finway.com.ua/en/polygon-pos-network-experiences-outage/)<br /><br />[Mainnet heimdall halted](https://status.polygon.technology/incidents/ll8nkw7q8x5k)<br />**September 10, 2025** — delayed finality (10-15 minutes) rather than full halt. [CryptoRank](https://cryptorank.io/news/feed/02add-polygon-pos-network-faces-10-15-minute-transaction-delays-due-to-node-bug)<br />[Official source - Polygon to Ethereum Asset Withdrawals Impacted](https://status.polygon.technology/incidents/cflvgc1zkbk9) & [Consensus Finalization Delay – Temporary Issue](https://status.polygon.technology/incidents/c8nc05x3qvmg) |                                                              |
| Solana                        | [Solana status](https://status.solana.com)           | February 6, 2024 — ~4 h 46 m outage. [Solana](https://solana.com/en/news/network-performance-report-march-2024) | Earlier outages also in Solana’s history (e.g., Sept 14, 2021 for ~17 hours) [OKX](https://www.okx.com/learn/solana-outage-guide) |
| Polkadot                      |                                                      | -                                                            | A reddit comment states “Polkadot has consistently produced blocks … there has never been a chain halt” as of 2023. [Reddit](https://www.reddit.com/r/Polkadot/comments/10z061g) |
| Cosmos Hub                    | [Atom scan](https://atomscan.com)                    | June 5, 2024 — ~4 hour outage due to vulnerability in the Liquid Staking Module during v17 upgrade. [ForkLog+1](https://forklog.com/en/cosmos-hub-resumes-operations-after-four-hour-outage/) | Block production halted until validators applied patch.      |
| Sui                           | [Sui status](https://status.sui.io)                  | November 21, 2024 — >1 hour outage (block production halted after ~9:15 am UTC). [Cointelegraph](https://cointelegraph.com/news/sui-down-no-blocks-produced-1-hour) | The network was restored after approximately 2 hours.        |
| Aptos                         |                                                      | October 19, 2023 — outage for over 5 hours. [The Crypto Times](https://www.cryptotimes.io/2023/10/19/aptos-suffers-major-outage-for-over-5-hours-on-its-birthday/) | Block production stopped at block height 104,621,314.        |
| ICP                           |                                                      |                                                              |                                                              |





## Avalanche

**February 23, 2024**

*Avalanche Validators provision a stake-weighted bandwidth allocation for each peer and this buggy logic led to each node saturating their allocation with useless transaction gossip. This dynamic prevented pull queries issued by the validator from being processed in a timely manner and led to consensus stalling (as no polls were being handled).*

Reference: [Incident Report - Block Finalization Stall](https://status.avax.network/incidents/qmx0s7zk6gkm)

See aslo [The Blocks - Avalanche confirms block finalization stall](https://www.theblock.co/post/278816/avalanche-block-finalization-stall), [decrypt - AVAX Dips as Avalanche Network Faces Block Production Halt](https://decrypt.co/218758/avalanche-network-block-production-halt-avax-dips)



**Feburary 01, 2024**

Due to an issue with an infrastructure provider, block ingestion across the Primary Network and Subnets is delayed. This means that subnets.avax.network, Core, and stats.avax.network will not show the latest activity. Public APIs hosted by Ava Labs are still accessible.

[Block Ingestion Delayed](https://status.avax.network/incidents/4vq54hv6b9t4)



**March 2023, **

[Coindesk - Avalanche Blockchain's X and C Networks See Brief Outage](https://www.coindesk.com/markets/2023/03/23/avalanche-blockchains-x-and-c-networks-see-brief-outage)



**February 13, 2021**

[X - Avalanche annoucement](https://x.com/avax/status/1360667899497693184)

[forklog - Developers fix bug that halted transactions on the Avalanche blockchain](https://forklog.com/en/developers-fix-bug-that-halted-transactions-on-the-avalanche-blockchain/)









## Bitcoin

:) 

### Cosmos hub

Cosmos Hub saw a temporary halt to block production as validators patched a security vulnerability with the Liquid Staking Module (LSM) during the v17 upgrade.

Cosmos developers identified and deployed a fix for the bug within the next two hours, but the chain did not resume producing blocks until the majority of validators had implemented the patch.

[Cosmos Hub Resumes Block Production After 4-Hour Outage](https://unchainedcrypto.com/cosmos-hub-resumes-block-production-after-4-hour-outage/), [Cosmos - X annoucement](https://x.com/cosmoshub/status/1798459903289553148)

## Polygon

> [Polygon Status](https://status.polygon.technology)
> See all [accidents](https://status.polygon.technology/history)

Polygon PoS network which uses Ethereum for settlement is composed of the following two layers:

- `Heimdall layer`, a consensus layer consisting of a set of proof-of-stake Heimdall nodes for monitoring staking contracts deployed on the Ethereum mainnet, bridging events, and committing the Polygon PoS network checkpoints to the Ethereum mainnet. The new version of Heimdall is based on [CometBFT](https://docs.cometbft.com/).
- `Bor layer`, an execution layer which is made up of a set of block-producing Bor nodes shuffled by Heimdall nodes. The primary Bor client is based on Go Ethereum (Geth) and Erigon is also supported.

Reference: [Polygon PoS]( https://docs.polygon.technology/pos/overview/)

**July  30, 2025**

> Cause: Bug in consensus

*As of 09:30 AM UTC on July 30, 2025, the mainnet Heimdall service became unresponsive. The Polygon protocol team is currently investigating the issue. This affects the ability to view validator and checkpoint data via the mainnet Heimdall APIs.
Component: Mainnet Heimdall-V2 network*

~ July 30, 2025 — the mainnet Heimdall service became unresponsive.

Reference:  

- [Official source - Mainnet heimdall halted](https://status.polygon.technology/incidents/ll8nkw7q8x5k)
- Other ressources: [The block.com - Polygon suffers hour-long outage weeks after complex hard fork](https://www.theblock.co/post/364913/polygon-suffers-hour-long-outage-weeks-after-complex-hard-fork), [finway.com.ua](https://finway.com.ua/en/polygon-pos-network-experiences-outage/),

**September 10, 2025** — delayed finality (10-15 minutes) rather than full halt. 

*On September 10, 2025, at 04:30 UTC, the Polygon network experienced a degradation in its milestone finalization mechanism.*

*A rare race condition between milestone processing and block importing caused an incompatible milestone to be recorded in some validator nodes, leading to extended delays in milestone based finality.*

*While blocks continued to be finalised via checkpoints, providing finality in around 20 minutes, a hard fork based fix was required to remediate the incorrect milestone, and restore usual milestone based finality (4 - 5 seconds). The network resumed normal operation following this emergency hard fork at 15:00.*

*Following a detailed post-mortem, the development team have released a new version of bor as an additional safety guards to prevent any reoccurrence. We advise upgrading t*o v2.2.11 to ensure continued compatibility and performance, detailed here: https://github.com/0xPolygon/bor/releases/tag/v2.2.11



[Official source - Polygon to Ethereum Asset Withdrawals Impacted](https://status.polygon.technology/incidents/cflvgc1zkbk9) & [Consensus Finalization Delay – Temporary Issue](https://status.polygon.technology/incidents/c8nc05x3qvmg), [Bor v2.2.11-beta2 and Heimdall v0.3.1 hot fix release for Polygon Mainnet](https://forum.polygon.technology/t/bor-v2-2-11-beta2-and-heimdall-v0-3-1-hot-fix-release-for-polygon-mainnet/21284), [X annoucement](https://x.com/sandeepnailwal/status/1965821862358683955), [X - Polygon Foundation ](https://x.com/0xPolygonFdn/status/1965776869917151626)

Other reference: [CryptoRank](https://cryptorank.io/news/feed/02add-polygon-pos-network-faces-10-15-minute-transaction-delays-due-to-node-bug)

## Solana

### 02/06/2024 - outage

The outage began at approximately 09:53 UTC, lasting 5 hours. 

Block production on Solana mainnet beta resumed at 14:57 UTC, following a successful upgrade to v1.17.20 and a restart of the cluster by validator operators. Engineers will continue to monitor performance as network operations are restored. The outage began at approximately 09:53 UTC, lasting 5 hours. Core contributors are working on a root cause report, which will be made available once complete.

https://status.solana.com/incidents/n5kcgs8dl9pj

### 02/26/2023 - degraded performance

 Slow root production on mainnet beta.

https://status.solana.com/incidents/ymr0gyj9xqyz



### 02/07/2023 - outage

The outage began at approximately 09:53 UTC, lasting 5 hours. Core contributors are working on a root cause report, which will be made available once complete.

https://status.solana.com/incidents/n5kcgs8dl9pj



**06/2022 - outage**

Validator operators successfully completed a cluster restart of Mainnet Beta at 9:00 PM UTC, following a roughly 4 and a half hour outage after the network failed to reach consensus. Network operators and dapps will continue to restore client services over the next several hours.

https://status.solana.com/incidents/ymr0gyj9xqyz



**01/06/2022 - degraded perform**

The Solana Network is currently experiencing degraded performance due to an increase in high compute transactions, which is reducing network capacity to several thousand transactions per second

https://status.solana.com/incidents/3cvfj59zzrgs

## Sui

### 11/21/2024 - outage

On the morning of November 21, 2024, between approximately 1:15 and 3:45 am PT, Sui Mainnet suffered a complete network halt. All validators were stuck in a crash loop, preventing all transaction processing.

An `assert!` in congestion control code (described below) erroneously caused validators to crash if the estimated execution cost was zero.

**Congestion control**, the system that limits the rate of transactions writing to a single shared object, prevents the network from becoming overloaded with checkpoints that take too long to execute.

We recently upgraded our congestion control system to improve shared object utilization by more accurately estimating the complexity of a transaction. The code for the new mode, `TotalGasBudgetWithCap`, had a bug that caused this issue.

https://blog.sui.io/sui-mainnet-outage-resolution/

https://status.sui.io/incidents/f2yz7qzwcc94