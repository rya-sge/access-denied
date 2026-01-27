---
layout: post
title: "Blockchain e"
date:   2025-11-10
lang: en
locale: en-GB
categories: blockchain ethereum 
tags: gas
description: Blockchain downtime overview
image: 
isMath: false
---

Blockchain network availability is a big important topic, particularlly if we move financial instruments on-chain.For defi application, this is already a big topic for  all protocols using a collateral design such as Lending protocol or derivative products. When the price of a collaterteral fails during a certain threshold, the collateral must be liquidied to avoid that the procool acumulate bad debts. This is not possible when the blockchain network is not available, in the sense that new transactions can not be added to the protocol or are delayed.

This article summarizes the main  blockchain outage. Blockchain outages can have serveral different cause, notably:

- Vulnerability discovered in the software node or consensus requiring to halt the blockchain,
- A bug which halt the prochain during an upgrade(e.g. Cosmos)
- A pic of transaction which halt the blockchain or some key components (e.g centralized sequencer for Layer 2)

Example: Bitcoin,

### Summary tab

| Blockchain                        | Check<br />Current status                                    | Date of downtime / major halt                                | Notes                                                        |
| --------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Aptos**                         | [Aptos explorer](https://explorer.aptoslabs.com/?network=mainnet) | **October 19, 2023** — outage for over 5 hours ([10/18/23 Aptos Mainnet Incident Report](https://aptosnetwork.com/currents/10-18-23-aptos-mainnet-incident-report)) | Block production stopped at block height 104,621,314, due to a bug in the Aptos-core code base (charge / refund for a transaction) |
| **Arbitrum**                      | [Arbitrum status](https://status.arbitrum.io) & [Arbiscan](https://arbiscan.freshstatus.io) |                                                              |                                                              |
| **Avalanche (C-Chain / Mainnet)** | [Avalanche status](https://status.avax.network)              | **~February 23, 2024** — ~5 h outage due to consensus stall. [Blockworks](https://blockworks.co/news/avalanche-blockchain-downtime), [Official source](https://status.avax.network/incidents/qmx0s7zk6gkm) / [Official source 2](https://status.avax.network/incidents/4vq54hv6b9t4) | Validator networking bug halted finalization until fix.      |
| **Berachain (L1)**                | [Berachain status](https://status.berachain.com)             | **Nov 2025** — coordinated halt for emergency hard fork related to Balancer V2 exploit | Validators paused consensus to mitigate exploit fallout.     |
| **Bitcoin (mainnet)**             | [bitcoin.org](https://bitcoin.org/en/alerts)<br />[Bitcoin uptime tracker](https://bitbo.io/uptime/) | **2010**: Value Overflow Incident;<br />**2013**: Client fork divergence | Extremely rare halts; formal downtime events are historical. |
| **Cardano**                       | [Cardano status (general)](https://cardanoscan.io)           | **January 22–23, 2023** — Brief node disruption/automatic restarts. [updates.cardano.intersectmbo.org+1](https://updates.cardano.intersectmbo.org/2023-04-17-ledger/?utm_source=chatgpt.com) | No confirmed full network downtime; block production continued with automatic recovery. [KuCoin](https://www.kucoin.com/news/flash/cardano-clarifies-no-network-downtime-mainnet-continues-stable-block-production?utm_source=chatgpt.com) |
| **Cosmos Hub**                    | [Atom scan](https://atomscan.com)                            | **June 5, 2024** — ~4 h 40 min outage during v17 upgrade made to patch a vulnerability in the Liquid Staking Module. [ForkLog](https://forklog.com/en/cosmos-hub-resumes-operations-after-four-hour-outage/) | Block production halted while validators applied a fix.      |
| **Ethereum (mainnet)**            | [Ethereum status](https://ethstats.dev)                      | –                                                            | No prolonged network halt documented; occasional client issues historically. |
| **Hedera**                        | [Hedera status](https://status.hedera.com)                   | **September 3–5, 2023** — ~2 day proxy disablement post-exploit. [status.hedera.com](https://status.hedera.com/incidents/j27rmgv4plcl) | Mainnet proxies were turned off to stop exploit; resumed after patch. |
| **ICP**                           | [ICP Analytics](https://icpanalytics.statuspage.io)          | –                                                            | No significant public chain halt reported.                   |
| **Linea (L2)**                    | [linea.statuspage.io](https://linea.statuspage.io)           | –                                                            | Sequencer/prover outages have occurred but no extended halt documented. |
| **Polkadot**                      | [Polkadot status](https://polkadot.subscan.io)               | –                                                            | No confirmed relay chain halt to date; isolated parachain issues possible. |
| **Polygon PoS**                   | [Polygon Status](https://status.polygon.technology)          | **July 30, 2025** — Heimdall unresponsive ([Mainnet heimdall halted](https://status.polygon.technology/incidents/ll8nkw7q8x5k));<br />**Sep 10, 2025** — delayed finality ([Official source – Polygon to Ethereum Asset Withdrawals Impacted](https://status.polygon.technology/incidents/cflvgc1zkbk9) & [Consensus Finalization Delay – Temporary Issue](https://status.polygon.technology/incidents/c8nc05x3qvmg)) | Consensus and finality service degradation issues noted.     |
| **Solana**                        | [Solana status](https://status.solana.com)                   | **Feb 6, 2024** — ~4 h 46 min outage; multiple past outages. | Consensus stalls requiring cluster restarts.                 |
| **Starknet**                      |                                                              |                                                              |                                                              |
| **Sui**                           | [Sui status](https://status.sui.io)                          | **Nov 21, 2024** — ~2.5 h outage. [status.sui.io](https://status.sui.io/incidents/f2yz7qzwcc94) | Validator crash loop; congestion control code bug.           |
| **XRP Ledger**                    | [livenet.xrpl.org](https://livenet.xrpl.org)                 | –                                                            | Historically brief consensus stalls but no major downtime.   |

### 





https://dune.com/vcryptojack/blockchain-downtime

## Aptos

### 10/18/2023 - Delayed transactions

> Start: 4:15 pm PDT
> End: 9:18 PM PDT
> Duration: 4 hours

On October 18, 2023 the Aptos network delayed transactions at approximately 4:15 PM PDT. Transaction load was not an issue for this incident – no committed transactions were lost and no fork occurred. Non-deterministic code led to the issue and a fix was deployed. The issue was resolved at approximately 9:30 PM PDT.

Reference: [Aptos Network - 10/18/23 Aptos Mainnet Incident Report](https://aptosnetwork.com/currents/10-18-23-aptos-mainnet-incident-report), [Forklog - Aptos network resumes operation after five-hour outage](https://forklog.com/en/aptos-network-resumes-operation-after-five-hour-outage/), [Aptos Hit With 5-Hour Outage on Blockchain's First Birthday](https://decrypt.co/202340/aptos-hit-5-hour-outage-blockchains-first-birthday)

### Arbitrum

Arbitrum is an Ethereum Layer-2 optimistic rollup designed to improve scalability and throughput while retaining security anchored on Ethereum. It relies on a *sequencer* to order transactions and produce blocks before submitting batched data to L1.

### 2023/12/15 - Sequencer & Feed Issues (Arbitrum One)

> Start: 10:29 am EST (2023/12/15)
>
> End: 1:57 AM EST.

The Arbitrum One Sequencer and Feed stalled at 10:29 AM ET during a significant surge in network traffic. 

Status: [Sequencer & Feed Issues (Arbitrum One)](https://status.arbitrum.io/clq6te1l142387b8n5bmllk9es)

### 2022/09/01 - Hardware failure in the main Sequencer node

Arbitrum experienced a period during which its sequencer stopped processing transactions following a hardware failure on the primary sequencer node. Failover redundancies failed due to an ongoing software upgrade, temporarily preventing new transaction acceptance. Restoration required careful replay and posting of pending transactions.

Reference: [Offchain labs - Today’s Arbitrum Sequencer Downtime: What Happened?](https://offchain.medium.com/todays-arbitrum-sequencer-downtime-what-happened-6382a3066fbc)

### Notes

- As an optimistic rollup, Arbitrum’s design *does not require sequencer liveness* for eventual transaction inclusion; users can fall back to submitting transactions via Ethereum L1 contracts if sequencers fail.  
- Historical issues largely relate to sequencer availability rather than fundamental consensus faults, and there are *no recent officially acknowledged full chain halts*.

## Avalanche

### 2024/02/23 - Block Finalization Stall

*Avalanche Validators provision a stake-weighted bandwidth allocation for each peer and this buggy logic led to each node saturating their allocation with useless transaction gossip. This dynamic prevented pull queries issued by the validator from being processed in a timely manner and led to consensus stalling (as no polls were being handled).*

Reference: [Incident Report - Block Finalization Stall](https://status.avax.network/incidents/qmx0s7zk6gkm)

See also [The Blocks - Avalanche confirms block finalization stall](https://www.theblock.co/post/278816/avalanche-block-finalization-stall), [decrypt - AVAX Dips as Avalanche Network Faces Block Production Halt](https://decrypt.co/218758/avalanche-network-block-production-halt-avax-dips)

### 2024/02/01 - Block Ingestion delayed

Due to an issue with an infrastructure provider, block ingestion across the Primary Network and Subnets is delayed. This means that subnets.avax.network, Core, and stats.avax.network will not show the latest activity. Public APIs hosted by Ava Labs are still accessible.

Reference: [Block Ingestion Delayed](https://status.avax.network/incidents/4vq54hv6b9t4)



### 2023/03/23 - Avalanche Network unstable

Avalanche C-Chain and X-Chain have been been unstable for a bit over an hour. It was a bug with v1.9.12

[Coindesk - Avalanche Blockchain's X and C Networks See Brief Outage](https://www.coindesk.com/markets/2023/03/23/avalanche-blockchains-x-and-c-networks-see-brief-outage),[Kevin Sekniqi  -tweet](x.com/i/status/1638712640242319364)



**February 13, 2021**

[X - Avalanche announcement](https://x.com/avax/status/1360667899497693184)

[forklog - Developers fix bug that halted transactions on the Avalanche blockchain](https://forklog.com/en/developers-fix-bug-that-halted-transactions-on-the-avalanche-blockchain/)



## Berachain (cosmos-based)

**Overview:** Berachain is a relatively new Cosmos-based smart contract platform that augments liquidity-oriented consensus and DeFi integration. It is distinct from Ethereum L2 rollups and is a *standalone Layer-1 chain*.  

### 2025/11/03 - Emergency hard fork

Validators *purposefully halted network operations* and initiated an **emergency hard fork** to respond to a large exploit impacting Balancer V2 liquidity pools  and related fork across multiple blockchains.  On berachain, the attack primarily hit the Ethena/Honey tripool.

Validators agreed to pause consensus to mitigate further loss and prepare protective rollbacks/hard fork binary distribution.

**Technical Notes:**  

- The pause was coordinated rather than accidental, representing a governance-level response to a *smart contract systemic exploit* with cross-chain effects.  
- Recovery efforts included distributing the emergency hard fork binary to validators and updating infrastructure before resuming block production.

**Implications:**  

- This event highlights the tension between *decentralization and pragmatic emergency response*; halting an L1 highlights risks when large protocol vulnerabilities are exploited.  
- Networking governance and validator coordination are central to resuming operations post-incident.

Reference: [X announcement](https://x.com/berachain/status/1985288599152042101), [Berachain halts network to conduct emergency hard fork amid $128 million Balancer exploit](https://www.theblock.co/post/377257/berachain-emergency-hardfork)



---

## Bitcoin

Reference: [bitbo - downtime](https://bitbo.io/calendar/downtime/)

### 2010/08/15 - Value Overflow

> Duration: 8 hours and 27 minutes.

Bitcoin went down in 2010 due to something [called](https://en.bitcoin.it/wiki/Value_overflow_incident) *The Value Overflow Incident* (also known as [CVE-2010-5139](https://www.cve.org/CVERecord?id=CVE-2010-5139)).

On August 15, 2010 block 74638 was created and it contained a transaction that created 184,467,440,737.09551616 bitcoins for three different addresses. Since one of Bitcoin’s main features is its 21 million limit, this was an obvious bug.

The reason the bug was able to happen was because there was, at the time, no check to make sure that values so large could not be sent.

Bitcoin’s founder, Satoshi Nakamoto, posted a code update for this bug around 5 hours after the bug was discovered.

The extra bitcoins sent in that transaction no longer exist.

Reference: https://en.bitcoin.it/wiki/Value_overflow_incident

### 2013 - chain fork

> Duration: 6 hours and 20 minutes.

The 2013 Bitcoin downtime (also called [CVE-2013-3220](https://www.cve.org/CVERecord?id=CVE-2013-3220)) event was very different than 2010’s bug.

In 2010, someone temporarily “created” new bitcoins. In 2013, there was a network split where Bitcoin’s network temporarily split into two separate networks.

Versions 0.7 and 0.8 of the Bitcoin software diverged from each other, causing the block chain to “fork” into two.

Unlike 2010, by 2013 there were already a good number of people using Bitcoin. The 2013 bug being discovered caused the Bitcoin price to [fall](https://arstechnica.com/information-technology/2013/03/major-glitch-in-bitcoin-network-sparks-sell-off-price-temporarily-falls-23/) by 23%.

https://en.bitcoin.it/wiki/BIP_0050

### Cosmos Hub

#### 2024/06/05 - Upgrade bug

> Start: On June 5th, 2024, at 19:21 (UTC), the *Cosmos Hub* chain halted,
> End: The chain resumed on June 6th, 2024, at 0:02 (UTC).
>
> Total: the total time the chain was halted was around 4 hours and 40 minutes.

Cosmos Hub saw a temporary halt to block production as validators patched a security vulnerability with the Liquid Staking Module (LSM) during the v17 upgrade.

Cosmos developers identified and deployed a fix for the bug within the next two hours, but the chain did not resume producing blocks until the majority of validators had implemented the patch.

[Cosmos Hub Resumes Block Production After 4-Hour Outage](https://unchainedcrypto.com/cosmos-hub-resumes-block-production-after-4-hour-outage/), [Cosmos - X annoucement](https://x.com/cosmoshub/status/1798459903289553148), [Cosmos Hub v17.1 Chain Halt - Post-mortem](https://forum.cosmos.network/t/cosmos-hub-v17-1-chain-halt-post-mortem/13899)

#### 2020/02/27

https://iqlusion.blog/postmortem-2020-02-27-cosmos-hub-validator-outage

## Hedera

### 2023/09/03 - Exploit

> Start: 03/09/2023 - 20:14 UTC
>
> End: 03/11/2023 - 02:08 UTC
>
> Duration: 2 days

Attackers exploited the Smart Contract Service code of the Hedera mainnet to transfer Hedera Token Service tokens held by victims’ accounts to their own account. 

The attacker targeted accounts used as liquidity pools at multiple DEXes that use Uniswap v2-derived contract code ported over to use the Hedera Token Service, including Pangolin, SaucerSwap, and HeliSwap. When the attackers moved tokens obtained through these attacks over the Hashport bridge, the bridge operators detected the activity and took swift action to disable it.

To prevent the attacker from being able to steal more tokens, Hedera turned off mainnet proxies, which removed user access to the mainnet. 

After that the root cause has been identified, Hedera Council members have signed transactions to approve the deployment of the code on mainnet to patch the vulnerabilities and mainnet proxies have been turned back on, allowing normal activity to resume.

Reference: [status.hedera.com - Mainnet network proxies disabled](https://status.hedera.com/incidents/j27rmgv4plcl)

### 2020/03/08 (Mainet Upgrade)

> Start: 03/09/2023 - 20:14 UTC
>
> End: 03/11/2023 - 02:08 UTC
>
> Duration: 2 days

Mainet upgrade to v0.6.0 which has taken approx. 150 minutes to complete, during which time all network services have been offline.

[status.hedera.com - Mainnet Upgrade to v0.6.0](https://status.hedera.com/incidents/dvng86d1tgn3)

### 2020/06/18 (mainet upgrade)

Mainnet upgrade to 0.5.8 (150 minutes)

[Status - Mainnet upgrade to 0.5.8](https://status.hedera.com/incidents/20n97k7j2ls9)

### 2010/06/18 (mainet upgrade)

## Linea

Linea is an Ethereum zk-rollup with a centralized sequencer and prover.

- Multiple outages between 2023–2024
- Primarily caused by prover failures and sequencer downtime

These incidents exposed **operational centralization risks** in early zk-rollup deployments.



## Optimism

**Overview:** Optimism is another modular Ethereum L2 built on the OP Stack with a centralized sequencer managed by OP Labs (transitioning over time towards decentralization). Sequencer function is critical to fast block production and transaction ordering. :contentReference[oaicite:7]{index=7}

### 2024/02/15 - Sequencer outage

Optimism Mainnet experienced *sequencer outage and instabilities* starting ~06:00 ET. The sequencer stopped producing blocks (“unsafe head stall”), and subsequent patches were applied to restore operations. Community reports indicate additional node restarts were required by operators, suggesting deeper issues beyond initial fixes.

**Mechanics of Outages:**  

- Sequencer downtime occurs when the machine responsible for batching and posting transactions to Ethereum cannot process L2 submissions; this appears to users as the network “stuck” at a particular block height.  
- Optimism’s documentation distinguishes between *sequencer downtime outages* and *transaction submission outages*, both of which have different implications for L2 liveness and user options. 

**Mitigation:**  

- Users can bypass sequencer outages by submitting transactions directly to the *OptimismPortal* contract on Ethereum L1, ensuring transaction inclusion even if the sequencer is offline.

## Polygon PoS

> [Polygon Status](https://status.polygon.technology)
> See all [accidents](https://status.polygon.technology/history)

Polygon PoS network which uses Ethereum for settlement is composed of the following two layers:

- `Heimdall layer`, a consensus layer consisting of a set of proof-of-stake Heimdall nodes for monitoring staking contracts deployed on the Ethereum mainnet, bridging events, and committing the Polygon PoS network checkpoints to the Ethereum mainnet. The new version of Heimdall is based on [CometBFT](https://docs.cometbft.com/).
- `Bor layer`, an execution layer which is made up of a set of block-producing Bor nodes shuffled by Heimdall nodes. The primary Bor client is based on Go Ethereum (Geth) and Erigon is also supported.

Reference: [Polygon PoS]( https://docs.polygon.technology/pos/overview/)

### 2025/12/18 - Incident Report for Polygon

Partial Bor Halt

https://status.polygon.technology/incidents/9ysh9zczb8ml

### 2025/09/10 - Delayed finality (race condition)

Delayed finality (10-15 minutes) rather than full halt. 

*On September 10, 2025, at 04:30 UTC, the Polygon network experienced a degradation in its milestone finalization mechanism.*

*A rare race condition between milestone processing and block importing caused an incompatible milestone to be recorded in some validator nodes, leading to extended delays in milestone based finality.*

*While blocks continued to be finalised via checkpoints, providing finality in around 20 minutes, a hard fork based fix was required to remediate the incorrect milestone, and restore usual milestone based finality (4 - 5 seconds). The network resumed normal operation following this emergency hard fork at 15:00.*

*Following a detailed post-mortem, the development team have released a new version of bor as an additional safety guards to prevent any reoccurrence. We advise upgrading t*o v2.2.11 to ensure continued compatibility and performance, detailed here: https://github.com/0xPolygon/bor/releases/tag/v2.2.11

[Official source - Polygon to Ethereum Asset Withdrawals Impacted](https://status.polygon.technology/incidents/cflvgc1zkbk9) & [Consensus Finalization Delay – Temporary Issue](https://status.polygon.technology/incidents/c8nc05x3qvmg), [Bor v2.2.11-beta2 and Heimdall v0.3.1 hot fix release for Polygon Mainnet](https://forum.polygon.technology/t/bor-v2-2-11-beta2-and-heimdall-v0-3-1-hot-fix-release-for-polygon-mainnet/21284), [X annoucement](https://x.com/sandeepnailwal/status/1965821862358683955), [X - Polygon Foundation ](https://x.com/0xPolygonFdn/status/1965776869917151626)

Other reference: [CryptoRank](https://cryptorank.io/news/feed/02add-polygon-pos-network-faces-10-15-minute-transaction-delays-due-to-node-bug)

### 2025/07/30 - Bug in consensus

> Cause: Bug in consensus

*As of 09:30 AM UTC on July 30, 2025, the mainnet Heimdall service became unresponsive. The Polygon protocol team is currently investigating the issue. This affects the ability to view validator and checkpoint data via the mainnet Heimdall APIs.
Component: Mainnet Heimdall-V2 network*

~ July 30, 2025 — the mainnet Heimdall service became unresponsive.

Reference:  

- [Official source - Mainnet heimdall halted](https://status.polygon.technology/incidents/ll8nkw7q8x5k)
- Other ressources: [The block.com - Polygon suffers hour-long outage weeks after complex hard fork](https://www.theblock.co/post/364913/polygon-suffers-hour-long-outage-weeks-after-complex-hard-fork), [finway.com.ua](https://finway.com.ua/en/polygon-pos-network-experiences-outage/),

## Solana

### 2024/02/06 - outage

The outage began at approximately 09:53 UTC, lasting 5 hours. 

Block production on Solana mainnet beta resumed at 14:57 UTC, following a successful upgrade to v1.17.20 and a restart of the cluster by validator operators. Engineers will continue to monitor performance as network operations are restored. The outage began at approximately 09:53 UTC, lasting 5 hours. Core contributors are working on a root cause report, which will be made available once complete.

Reference: [Solana - Status](https://status.solana.com/incidents/n5kcgs8dl9pj)

### 2023/02/26 - degraded performance

 Slow root production on mainnet beta.

Reference: [Solana - Status](https://status.solana.com/incidents/ymr0gyj9xqyz)



### 2023/02/06 - outage

The outage began at approximately 09:53 UTC, lasting 5 hours. Core contributors are working on a root cause report, which will be made available once complete.

Reference: [Solana - Status](https://status.solana.com/incidents/n5kcgs8dl9pj)



### 06/2022 - outage

Validator operators successfully completed a cluster restart of Mainnet Beta at 9:00 PM UTC, following a roughly 4 and a half hour outage after the network failed to reach consensus. Network operators and dapps will continue to restore client services over the next several hours.

Reference: [Solana - Status](https://status.solana.com/incidents/ymr0gyj9xqyz)



### 01/06/2022 - degraded perform

The Solana Network is currently experiencing degraded performance due to an increase in high compute transactions, which is reducing network capacity to several thousand transactions per second

Reference: [Solana - Status](https://status.solana.com/incidents/3cvfj59zzrgs)

## Sui

### 11/21/2024 - outage

On the morning of November 21, 2024, between approximately 1:15 and 3:45 am PT, Sui Mainnet suffered a complete network halt. All validators were stuck in a crash loop, preventing all transaction processing.

An `assert!` in congestion control code (described below) erroneously caused validators to crash if the estimated execution cost was zero.

**Congestion control**, the system that limits the rate of transactions writing to a single shared object, prevents the network from becoming overloaded with checkpoints that take too long to execute.

We recently upgraded our congestion control system to improve shared object utilization by more accurately estimating the complexity of a transaction. The code for the new mode, `TotalGasBudgetWithCap`, had a bug that caused this issue.

Reference: [Sui Mainnet Outage Resolution - Sui Mainnet Outage Resolution](https://blog.sui.io/sui-mainnet-outage-resolution/), [https://status.sui.io/incidents/f2yz7qzwcc94](https://status.sui.io/incidents/f2yz7qzwcc94)





