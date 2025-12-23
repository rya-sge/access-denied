---
layout: post
title: "Blockchain downtime"
date:   2025-11-10
lang: en
locale: en-GB
categories: blockchain ethereum 
tags: gas uptime resilience
description: Overview and analysis of major blockchain downtime and network halts
image: 
isMath: false
---

This article provides a technical overview of **major blockchain downtime events**, including full chain halts, partial outages, delayed finality, and sequencer failures. While blockchains are often described as *highly available* or *fault tolerant*, real-world incidents demonstrate that both Layer-1 and Layer-2 systems remain subject to software bugs, consensus failures, validator coordination issues, and infrastructure faults.

The scope of this article focuses on **mainnet-impacting incidents** that materially affected block production, transaction finality, or user access.

---

## Summary table

| Blockchain          | Check current status       | Date of downtime / major halt  | Notes                                                        |
| ------------------- | -------------------------- | ------------------------------ | ------------------------------------------------------------ |
| Bitcoin (mainnet)   | bitcoin.org / bitbo.io     | 2010, 2013                     | Extremely rare halts; incidents were caused by protocol-level bugs and client divergence. |
| Ethereum (mainnet)  | ethstats.dev               | —                              | No full chain halt; resilience through client diversity and social coordination. |
| Avalanche (C-Chain) | status.avax.network        | Feb 2024                       | Consensus stalled due to validator gossip bandwidth bug.     |
| Arbitrum (L2)       | arbitrum.statuspage.io     | Jan 2022 (historical)          | Sequencer outage; fallback to L1 remained possible.          |
| Optimism (L2)       | —                          | Feb 2024                       | Sequencer stalled due to unsafe head handling bug.           |
| Berachain (L1)      | —                          | Nov 2025                       | Coordinated halt for emergency hard fork following exploit.  |
| Cardano             | cardanostatus.com          | —                              | No full mainnet halt reported; occasional degraded performance during upgrades. |
| Linea (L2)          | —                          | 2023–2024 (multiple incidents) | Outages related to centralized sequencer and prover components. |
| Polygon PoS         | status.polygon.technology  | Jul 2025, Sep 2025             | Heimdall consensus and milestone finality issues.            |
| Solana              | status.solana.com          | Multiple (2021–2024)           | Repeated consensus stalls and required coordinated restarts. |
| Polkadot            | polkadot.subscan.io        | —                              | No confirmed full chain halt to date.                        |
| Cosmos Hub          | atomscan.com               | Jun 2024                       | Chain halted during security patch deployment.               |
| Sui                 | status.sui.io              | Nov 2024                       | Validator crash loop caused full halt.                       |
| Aptos               | explorer.aptoslabs.com     | Oct 2023                       | Non-deterministic execution bug.                             |
| ICP                 | icpanalytics.statuspage.io | —                              | No major public chain halt reported.                         |
| XRP Ledger          | livenet.xrpl.org           | —                              | Historically brief consensus stalls but no prolonged halt.   |
| Hedera              | status.hedera.com          | Sep 2023                       | Proxies disabled following smart contract exploit.           |

---

## Bitcoin

Bitcoin has experienced **two historically significant downtime-related events**, both early in its lifecycle.

### August 15, 2010 — Value Overflow Incident

- **Duration:** ~8 hours
- **Cause:** Integer overflow bug allowed creation of ~184 billion BTC
- **Impact:** Consensus rollback and emergency patch
- **Outcome:** Invalid transaction removed; supply restored

This incident demonstrated the importance of explicit invariant checks in monetary systems.

### March 2013 — Chain split (CVE-2013-3220)

- **Duration:** ~6 hours
- **Cause:** Incompatible behaviour between Bitcoin Core 0.7 and 0.8
- **Impact:** Temporary fork into two valid chains
- **Outcome:** Manual coordination reverted the chain

Despite price volatility, Bitcoin recovered without permanent damage.

---

## Ethereum (Mainnet)

Ethereum has **never experienced a full, prolonged mainnet halt**. However, it has faced:

- Client-specific bugs (e.g. Geth, Prysm)
- Temporary finality delays
- Upgrade-related coordination risks (e.g. The Merge)

Ethereum’s **client diversity and social consensus mechanisms** have been key to maintaining uptime.

---

## Avalanche

### February 23, 2024 — Block finalisation stall

- **Duration:** ~5 hours
- **Cause:** Bug in stake-weighted peer bandwidth allocation
- **Impact:** Validators failed to process consensus polls
- **Outcome:** Patch released; network resumed

The issue highlighted how **validator networking assumptions** can affect liveness.

---

## Arbitrum

Arbitrum is an **Ethereum optimistic rollup** relying on a centralized sequencer for transaction ordering.

### January 2022 — Sequencer outage

- **Cause:** Hardware failure combined with incomplete failover configuration
- **Impact:** Transactions could not be sequenced temporarily
- **Mitigation:** Users could submit transactions directly via Ethereum L1

No full chain halt occurred, but user experience degraded significantly.

---

## Optimism

Optimism is an Ethereum Layer-2 built on the OP Stack.

### February 15, 2024 — Sequencer stall

- **Cause:** Unsafe head tracking bug
- **Impact:** Block production stopped
- **Resolution:** Emergency patches and sequencer restart

This incident reinforced that **sequencer availability remains a central risk** for optimistic rollups.

---

## Berachain

Berachain is a **Cosmos-based Layer-1 blockchain**.

### November 3, 2025 — Emergency network halt

- **Cause:** Large-scale exploit affecting Balancer-derived liquidity pools
- **Action:** Coordinated validator halt and emergency hard fork
- **Outcome:** Network resumed after binary upgrade

This event illustrates governance-level intervention in L1 emergencies.

---

## Cardano

Cardano has not experienced a confirmed full mainnet halt. Historical issues include:

- Temporary block propagation delays
- Upgrade-related performance degradation

Its Ouroboros consensus has remained live during upgrades.

---

## Linea

Linea is an Ethereum zk-rollup with a centralized sequencer and prover.

- Multiple outages between 2023–2024
- Primarily caused by prover failures and sequencer downtime

These incidents exposed **operational centralization risks** in early zk-rollup deployments.

---

## Polygon PoS

Polygon PoS consists of **Heimdall (consensus)** and **Bor (execution)** layers.

### July 30, 2025 — Heimdall halt

- **Cause:** Consensus bug
- **Impact:** Validator APIs unavailable; checkpoints stalled

### September 10, 2025 — Delayed finality

- **Cause:** Race condition in milestone finalization
- **Impact:** Finality delayed to ~20 minutes
- **Resolution:** Emergency hard fork and client upgrade

---

## Solana

Solana has experienced **multiple high-profile outages**.

### February 6, 2024

- **Duration:** ~5 hours
- **Cause:** Consensus failure
- **Resolution:** Cluster restart after client upgrade

Earlier incidents (2021–2023) followed similar patterns, often requiring coordinated restarts.

---

## Polkadot

As of the latest reports:

- No full relay chain halt has occurred
- Parachains may experience isolated outages
- Shared security model has preserved relay chain liveness

---

## Cosmos Hub

### June 5–6, 2024

- **Duration:** ~4 hours 40 minutes
- **Cause:** Vulnerability in Liquid Staking Module (LSM)
- **Resolution:** Validator patching and restart

This was a **planned security halt**, not an accidental failure.

---

## Sui

### November 21, 2024 — Full network halt

- **Cause:** Assertion failure in congestion control logic
- **Impact:** Validators entered crash loop
- **Resolution:** Code fix and coordinated restart

---

## Aptos

### October 18–19, 2023

- **Duration:** ~5 hours
- **Cause:** Non-deterministic execution bug
- **Outcome:** No data loss; patch deployed

---

## Hedera

### September 3–5, 2023

- **Duration:** ~2 days
- **Cause:** Smart contract exploit affecting DEX liquidity pools
- **Action:** Mainnet proxies disabled
- **Outcome:** Vulnerability patched and services restored

---

## Conclusion

Blockchain downtime remains a **practical engineering reality**, even in mature networks. Key lessons include:

- Client diversity improves resilience
- Centralized sequencers are a liveness risk
- Validator coordination is critical during emergencies
- Governance processes directly affect uptime

As blockchain adoption grows, **operational transparency and post-mortem discipline** will be as important as decentralization itself.

---