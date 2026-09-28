---
layout: post
title: "The ARC Token Whitepaper — Circle's Coordination Asset Read Against the Arc Node"
date:   2026-09-25
lang: en
locale: en-GB
categories: blockchain defi
tags: circle arc stablecoin usdc tokenomics staking governance consensus fees
description: "Circle's ARC whitepaper proposes staking, fee-to-ARC conversion and burn for Arc. The live chain credits USDC fees to the proposer and burns nothing."
image: /assets/article/blockchain/circle/2026-09-25-arc-token-whitepaper-mindmap.png
isMath: false
---

[Arc](https://arc.network) is a Layer-1 blockchain built by Circle, the issuer of USDC. It is EVM-compatible and pays gas in USDC rather than in a volatile token. Its blocks are final as soon as a permissioned validator set commits them, with a target block time of half a second.

In May 2026 Circle published *ARC: The Native Asset of the Economic OS*, a twelve-page whitepaper that adds a second asset to this design. ARC is described as a "native coordination asset". It is staked to secure the network, collects the protocol's fees and gives its holders a vote on the chain's economic parameters.

This article covers what the whitepaper proposes, then compares each proposal with two other sources. The first is the official documentation at docs.arc.io, scraped on 16 September 2026. The second is the source code of [`circlefin/arc-node`](https://github.com/circlefin/arc-node). Most of the token economy is presented as a future phase, so the absence of code is expected. A few points go further than that: the documentation and the whitepaper disagree on terminology or on design rationale, and one mechanism would need a change to the consensus engine itself.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Arc as it runs today

A description of the running system comes first, because every comparison below depends on it. `arc-node` has two processes that talk through the Engine API:

- **Execution layer.** A customised Reth node (Reth v2.2.0, revm 38).
- **Consensus layer.** A Malachite application. Malachite is a Tendermint-style BFT engine that Circle now maintains in its own fork.

![Sequence of an Arc transaction today: the user submits a USDC-paid transaction, the txpool applies the denylist, a round-robin proposer builds the block, validators commit it at a two-thirds quorum and the EVM handler credits the whole fee to the proposer's recipient]({{site.url_complet}}/assets/article/blockchain/circle/arc-transaction-lifecycle-workflow.png)

The properties that matter for the token discussion:

- **USDC is the native coin.** Native balances use 18 decimals. The same balance is exposed as an ERC-20 at `0x3600…0000` with 6 decimals, and native transfers emit [EIP-7708](https://eips.ethereum.org/EIPS/eip-7708) `Transfer` logs. Minting and burning go only through the Native Coin Authority precompile, and only the USDC token contract may call it.
- **The validator set is permissioned Proof-of-Authority.** It lives in a `ValidatorRegistry` contract that only `PermissionedValidatorManager` can modify. That contract has an owner, plus controllers who can set a validator's voting power up to an owner-defined cap. Mainnet genesis (chain ID `5042`, 12 May 2026) registers 11 validators with 2000 voting power each.
- **The proposer is chosen by rotation.** The proposer for height *h* and round *r* is validator `(h - 1 + r) mod n` in `crates/types/src/proposer.rs`. Voting power weighs votes towards the two-thirds quorum; it does not affect who proposes.
- **The fee market is [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) with smoothing.** The base fee is computed from an exponential moving average of gas used. It is bounded between 20 and 20,000 gwei on mainnet, and its parameters sit in a `ProtocolConfig` contract. The documented target is about $0.001 for an ERC-20 transfer.
- **The base fee is not burned.** The EVM handler overrides the usual EIP-1559 behaviour:

```rust
// crates/evm/src/handler.rs, ArcEvmHandler::reward_beneficiary
// Redirect both base fee and priority fee to the specified beneficiary
// This overrides the default EIP-1559 behavior which burns the base fee
let total_fee_amount = U256::from(effective_gas_price) * U256::from(gas_used);
...
evm.ctx_mut().journal_mut().balance_incr(beneficiary, total_fee_amount)
```

The beneficiary is the address each validator passes as `--suggested-fee-recipient`. The v0.7.0 release notes call it the address "where block rewards (tx fees, in USDC) collect". The node contains no block reward, no issuance and no staking code.

## The thesis: an "Economic OS" needs a coordination asset

The whitepaper opens with an analogy. Mobile phones had calling and texting before iOS and Android, and companies ran servers before AWS. In both cases a shared platform is what let activity grow past a certain scale. Circle argues that finance is now at the same point: payments, lending, FX and settlement still run on separate closed systems, which settle hours or days apart. Blockchains, stablecoins and emerging regulation together would now make a shared "Economic OS" feasible.

Arc is presented as that OS, and the paper describes the system in three layers:

- **Arc network:** the execution environment, which provides deterministic settlement, stablecoin gas, configurable privacy and institutional validators.
- **Stablecoins:** the medium of exchange.
- **ARC:** the coordination layer, "the mechanism through which participants secure the network, govern its economics, and share in the value that network activity creates."

The paper's closing sentence sums up the rationale: "ARC exists because a global economic operating system cannot be coordinated by a single entity."

![Layers of the Economic OS as the whitepaper draws them, from Arc core through assets, protocol services and developer kits to applications, with ARC as a coordination layer spanning them and token holders, validators and Circle as actors]({{site.url_complet}}/assets/article/blockchain/circle/arc-token-layers-concept.png)

## The five functions of ARC

The paper assigns ARC five functions that are meant to reinforce each other. Network activity feeds all five, and each one is expected to generate more activity.

| Function | What it coordinates (whitepaper, Table 1) |
|---|---|
| Economic alignment | Holders stake ARC and earn rewards from fees and inflation. |
| Platform utility | Reduced fees and preferential access across the network, services, kits and applications. |
| Fee capture and distribution | Fees are converted to ARC at protocol level, then split between validators and stakers and a permanent burn. |
| Governance | Holders vote on economic parameters, and validators enforce the decisions. |
| Expanding utility surface | Possible future designs: multichain coordination, multi-asset gas, specialised transaction lanes. |

### Staking and the two-layer security model

The whitepaper says the network "will transition from a Proof-of-Authority (PoA) consensus model to a Proof-of-Stake (PoS) consensus model". The validator set remains permissioned after the transition. Holders stake ARC while keeping custody of it, and stake allocates economic weight among the permissioned operators. Rewards come from inflation and from fees converted into ARC. Validators keep a commission, and the rest goes to stakers pro rata.

Security is described as two layers:

- **Identity layer.** Permissioning ensures each operator is "known, committed to minimum standards, and legally accountable."
- **Economic layer.** Staking "determines each validator's weight in proposer selection, reward flow, and what they stand to lose from underperformance and misbehavior."

In the early phase permissioning is handled offchain and published as validators join. Performance scoring, qualification thresholds and access controls may later move onchain.

### Platform utility

At the core layer, stakers may pay reduced gas and receive "partial or full gas subsidies". Above it, holders and stakers may get reduced fees on Circle services: cross-chain transfers (CCTP), mint and redemption, payments infrastructure and developer tooling. The paper labels these "illustrative utility possibilities" (Table 2), not commitments.

## Fee capture, conversion and burn

This is the core of the proposed token economy, and the part furthest from the current code. According to the whitepaper, fees stay priced in stablecoins for predictability. Whatever asset a user pays with, "protocol fees are programmatically converted into ARC at the protocol level prior to the reward cadence." Figure 4 of the paper places the conversion "at block settlement" and lists the possible payment assets as USDC, other stablecoins, ARC and future assets. The resulting ARC is then split two ways:

- **Distribution** to validators and stakers.
- **Permanent burn**, which offsets issuance.

The ratio between them is set by governance. The illustrative Figure 3 of the paper uses a 50% burn.

The revenue sources are listed in order. Base fees and priority fees come at launch, and revenue from MEV auctions follows later. Possible future fee categories include privacy-preserving transactions and dedicated transaction lanes. Each would feed "the existing conversion infrastructure without requiring changes to the protocol's core economic logic."

![Fee routing compared: today the base fee and tip are credited in USDC to the proposer's fee recipient with no burn, while the whitepaper converts fees to ARC at settlement and splits them between staker rewards and a governance-set burn]({{site.url_complet}}/assets/article/blockchain/circle/arc-fee-routing-today-vs-whitepaper.png)

Set against the implementation, three points stand out:

- **Today the base fee is paid out, not burned.** The documentation agrees with the code: "Unlike standard EIP-1559, Arc doesn't burn the base fee. Both the base fee and the priority fee are credited to the block's beneficiary." Nothing goes to a treasury or to stakers, and nothing is burned. The burn therefore cannot be added as a small change to an existing EIP-1559 burn, because the implementation removed that burn on purpose. It would be a new routing rule in the EVM handler.
- **The conversion needs a price, and the whitepaper does not say where it comes from.** Converting USDC fees into ARC at block settlement requires an exchange rate, whether from an oracle, an onchain market or an auction. The documentation lists avoiding that kind of dependency as a reason for the current design: a single gas denomination "avoids oracle dependencies for gas price conversion" (`stablecoin-native-model.md`). A protocol-level conversion brings back the dependency the documentation says was removed.
- **Priority fees are small by design.** The whitepaper names priority fees as a launch revenue source. The documentation advises wallets to set `maxPriorityFeePerGas` to 0 for most transactions and states that "validators don't require tips". Early on, fee revenue is therefore almost entirely the base fee, which the smoothed curve keeps near its 20 gwei floor.

## Supply, inflation and allocation

ARC starts with 10 billion tokens. To pay validators before fee revenue exists, new ARC is issued "at a modest annual rate, expected to begin at approximately 2–3%". The rate declines on a predefined schedule that governance can change. The long-term goal is *inflation neutrality*, where the burn offsets issuance. The paper gives no date for it and says it depends on real network activity.

The initial allocation is:

- **60% Ecosystem:** token sales, developer grants, growth programmes and participation mechanisms.
- **25% Circle:** protocol development, staking, governance and running ecosystem programmes.
- **15% Long-Term Reserve:** resilience, strategic flexibility and stabilisation in periods of stress.

Unlock schedules are "to be announced in the coming months". The disclaimer states that ARC gives no equity, debt, dividend, revenue-share or liquidation claim on Circle. It also presents the benefits of holding ARC as coming "solely from the participant's interaction with the Arc network" and "not dependent upon efforts of Circle", wording that addresses the "efforts of others" criterion of the Howey test used in US securities law. An offer to EU users would in addition need a crypto-asset white paper under [Regulation (EU) 2023/1114 (MiCA)](https://eur-lex.europa.eu/eli/reg/2023/1114/oj), which this document does not claim to be.

None of this appears in the node. `executor.rs` credits no block reward, and the only operations that change native supply are USDC mint and burn by the token contract.

## MEV, mempool and privacy

The whitepaper says private and encrypted mempools will remove the information asymmetry that frontrunning and sandwich attacks rely on. It says "TEE-based block building ensures verifiable, non-malicious transaction ordering." It also says block builders will compete in sealed-bid auctions for the right to build blocks, with the proceeds going through the ARC reward and burn path.

The current node has none of these components:

- **Mempool.** It is the standard Reth pool, unencrypted and ordered by coinbase tip, with an added denylist validator.
- **RPC-level MEV mitigation.** Pending-transaction RPCs are hidden by default. `eth_sendBundle` and `eth_sendPrivateTransaction` are removed from public transports. Transactions still gossip between nodes in plaintext.
- **Trusted execution.** The only TEE in the stack is the [arc-remote-signer](https://github.com/circlefin/arc-remote-signer), which keeps each validator's ed25519 consensus key inside an AWS Nitro Enclave. It signs consensus messages and does not build blocks.

The larger point is that the whitepaper assumes a separation between proposer and builder that does not exist on Arc. Today the round-robin proposer builds its own block from its own pool, so no builder role exists to put up for auction. Adding one is a change to how blocks are produced, not a fee category that plugs into existing code.

The same gap applies to privacy. The whitepaper lists "configurable privacy" among the properties of the execution environment in the present tense. The documentation says: "Privacy features are on the roadmap and not yet available on Arc." The planned feature is the *Arc Privacy Sector* (APS), in which confidential Solidity runs inside hardware enclaves and is called through a precompile. The documentation calls it "opt-in" privacy, not "configurable" privacy.

## Governance

The governance chapter is the most carefully hedged part of the paper. After the move to PoS, some powers "will shift from Circle towards the participants who depend on the network". Three principles guide the split:

1. Participants govern what directly affects them.
2. Some decisions require concentrated accountability.
3. Authority expands with readiness.

The initial allocation of decisions is:

| Decision domain | Initial model |
|---|---|
| Economic parameters (fees, inflation, burn) | Token holders decide, validators enforce |
| Protocol rules, features, upgrades | Circle decides with broad input, validators adopt |
| Network stewardship and incidents | Circle decides, validators enforce |
| Validator membership | Circle decides |
| Treasury and budgets | Circle, with transparency obligations |

The code matches the present-day column:

- **Economic parameters.** Every parameter the whitepaper would hand to token holders is set by a single `controller` of `ProtocolConfig` (`updateFeeParams`, `updateConsensusParams`, `updateBlockGasLimit`). The mainnet genesis fixes that controller as one externally owned account. ADR-0003 describes `ProtocolConfig` as a "governance smart contract", but the contract contains no voting logic.
- **Validator membership.** Membership and voting power belong to the `PermissionedValidatorManager` owner and its controllers.
- **Upgrades.** Protocol changes ship as named hardforks (`Zero3` to `Zero8`) in node releases.
- **Stewardship.** A mandatory denylist in the txpool and a native-USDC blocklist in the EVM handler fit the "Circle decides" row.

The whitepaper does not list blocklist control as a governance domain.

## Where the whitepaper, the docs and the code diverge

Most gaps fall into the category the whitepaper itself signals: features of a future PoS phase. The table groups all of them, and the paragraphs after it single out the ones that are more than a timing question.

| Topic | Whitepaper | Documentation | `arc-node` | Nature of the gap |
|---|---|---|---|---|
| Native asset | "ARC is the native coordination asset" | "There is no volatile native token."; USDC is "the native token of Arc" | Native coin is USDC; no ARC token | Terminology conflict |
| Consensus | "will transition" from PoA to PoS | "a potential transition from Proof-of-Authority to permissioned Proof-of-Stake" | Owner-managed registry; no staking or slashing | Roadmap, hedged differently |
| Proposer selection | Weighted by stake | "Rotating proposer" | `(h-1+r) mod n`, ignores voting power | Needs a consensus-layer change |
| Fee destination | Converted to ARC, split, part burned | Base fee "credited to the block's beneficiary" | Full fee in USDC to the proposer's recipient | Opposite of the target design |
| Fee conversion | Protocol-level, at settlement | Single denomination "avoids oracle dependencies" | No conversion code | Design tension, price source unspecified |
| Issuance | ~2–3%, decaying | Not mentioned | No block reward | Not implemented |
| Staker gas discounts | Discounts and subsidies | Uniform fee; sponsorship only through paymasters and EIP-3009 relayers | Uniform base fee | Not implemented |
| MEV | Encrypted mempool, TEE builder, sealed-bid auction | Not mentioned | Plain pool; RPC-level hiding only | Requires a builder role |
| Privacy | "configurable privacy" as a current property | "on the roadmap and not yet available" | README: "(Coming soon)" | Presented as current |
| Governance | Holders vote on economic parameters | Not described | One controller EOA | Not implemented (post-PoS) |
| Mainnet | "Expected in the summer of 2026"; "public, open" | Mainnet `5042` in a "private mainnet phase", permissioned RPC | Genesis 12 May 2026 | Live but not yet public |
| Service discounts | Reduced CCTP, mint/redeem and payments fees for holders | Flat App Kit fees; "10% to Arc" of custom bridge fees | n/a | Not implemented; recipient of "Arc" share undefined |

Four divergences are worth reading beyond "not built yet".

**"Native" means two different assets.** The documentation repeats that Arc has "no volatile native token" and presents it as a benefit to users and institutions, who then need no second asset to transact. The whitepaper calls ARC "native to the network". Both statements can hold if ARC is never required as gas. Figure 4, however, lists "ARC fees" as a payment input, and Table 1 lists multi-asset gas among future designs. If ARC becomes an accepted gas asset, the documentation's main selling point no longer applies as written.

**Stake-weighted proposer selection is a consensus change.** A staking contract that writes voting power into the existing registry would change quorum weights, since those are already read through `getActiveValidatorSet()`. Proposer selection would stay a plain rotation. The whitepaper's statement that staking determines "each validator's weight in proposer selection" therefore needs a new `ProposerSelector` in the Malachite application, not only a new module.

**Burn and conversion reverse a deliberate design choice.** The documentation presents the non-burned base fee as a feature, and names avoiding oracles as a reason for USDC-only gas. The whitepaper's fee path brings back a conversion price and removes part of the fee from circulation. The paper gives no mechanism for the price, whether an oracle, an AMM or a batch auction, and no treatment of the fee's exposure to ARC's price between collection and conversion.

**The privacy and MEV claims assume components the architecture does not yet have.** Encrypted mempools and TEE builders require a separate builder, a sealed transaction format and an enclave-attested build pipeline. Arc's only enclave today protects a signing key.

Some minor inconsistencies inside the documentation turned up during the comparison:

- The fee pages refer to a "sequencer", although Arc has rotating proposers.
- The wallet fee-display guide works through an example with a 500,000 gwei base fee, above the documented 20,000 gwei maximum.
- The same guide converts 840,000,000,000,000 wei to "0.00000084 USDC", where the correct figure is 0.00084 USDC.
- The post-quantum page calls SLH-DSA verification "live on Arc mainnet" but marks the milestone "In progress" in its roadmap table.

The documentation also covers features the whitepaper does not mention:

- post-quantum signature verification with [SLH-DSA]({{site.url_complet}}/2026/06/29/slh-dsa-fips-205-hash-based-signatures/) through a precompile at `0x1800…0004`;
- transaction memos and sender-preserving batch calls (`Memo`, `Multicall3From`);
- the native USDC blocklist.

## Conclusion

The ARC whitepaper describes a token economy for a chain that currently has none. What runs on Arc today is a USDC-native, permissioned PoA network with Circle-held admin keys. The whitepaper is open about most of this: it places staking, token-holder governance and the burn after a future PoS upgrade, and it labels its numbers as illustrative.

- **What the whitepaper proposes:** ARC as a stakeable coordination asset with five functions, a 10 billion initial supply, issuance decaying from about 2–3%, fees converted to ARC and partly burned, and a 60/25/15 allocation.
- **What the code does:** USDC is the gas coin, fees go in full to the proposer's recipient, the proposer is chosen by rotation, fee parameters are set by one controller, and the mempool is plaintext with RPC-level MEV hiding.
- **Gaps that are only timing:** issuance, staking rewards, staker discounts, token-holder voting and service-fee discounts.
- **Gaps that need design work:**
  - a price source for fee conversion;
  - a stake-aware proposer selector;
  - a proposer-builder separation for TEE building and sealed-bid auctions;
  - reconciling "native coordination asset" with the documentation's "no volatile native token".
- **Timeline:** mainnet exists as a private, permissioned phase (chain ID 5042), which is consistent with the whitepaper's "summer 2026" date but not yet with its description of a public, open network.

![Mindmap of the ARC token whitepaper covering Arc today, the five functions of ARC, supply and allocation, governance roles and the gaps with the documentation and the node code]({{site.url_complet}}/assets/article/blockchain/circle/2026-09-25-arc-token-whitepaper-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Arc** | Circle's EVM-compatible Layer-1 blockchain, with USDC as native gas and deterministic BFT finality. |
| **ARC** | The token proposed by the May 2026 whitepaper as Arc's coordination asset for staking, fee capture, governance and platform discounts. |
| **Economic OS** | Circle's framing of Arc as shared infrastructure on which payments, lending, FX and settlement are composed. |
| **Malachite** | The Tendermint-style BFT consensus engine used by Arc's consensus layer, maintained by Circle in its own fork. |
| **Native USDC** | USDC held as the chain's native coin with 18 decimals, mirrored by an ERC-20 interface with 6 decimals at `0x3600…0000`. |
| **ProtocolConfig** | The system contract holding fee-curve, gas-limit and consensus parameters, updated today by a single controller account. |
| **PermissionedValidatorManager** | The system contract through which an owner and its controllers register validators and set their voting power. |
| **Fee recipient** | The address a validator configures with `--suggested-fee-recipient`, which currently receives the base fee and the priority fee in USDC. |
| **Fee conversion** | The whitepaper's proposed protocol-level exchange of all collected fees into ARC at block settlement, before distribution and burn. |
| **Inflation neutrality** | The long-term state in which ARC burned from fees equals ARC issued to validators and stakers. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| Native USDC has 18 decimals, while the ERC-20 view at `0x3600…0000` has 6. | Scale by 10^12 when moving between `msg.value` or balances and ERC-20 amounts. Index EIP-7708 native `Transfer` logs separately from ERC-20 events. |
| The base fee is not burned; it goes to the proposer's fee recipient. | Do not model Arc supply or fee economics on Ethereum's EIP-1559 burn. Total USDC supply changes only through mint and redeem. |
| Proposers rotate and tips are not required. | Set `maxPriorityFeePerGas` to 0 by default. A tip does not buy inclusion priority the way it does on a builder market. |
| No ARC token, staking or governance contract exists on mainnet or testnet. | Treat any "ARC" contract address or staking interface as unverified until it appears in docs.arc.io's contract-address reference. |
| Transactions from or to blocklisted addresses are rejected in the txpool and at execution. | Surface a clear error for blocklisted counterparties rather than retrying. Monitor the blocklist events documented for indexers. |
| Mainnet RPC is permissioned during the private mainnet phase. | Develop against testnet `5042002` and request mainnet credentials and gas USDC through Circle. |

## Frequently Asked Questions

**Q: What is ARC, and how does it differ from the gas token on Arc?**

ARC is the token proposed in Circle's May 2026 whitepaper as Arc's "native coordination asset". Holders would stake it, receive converted fees and vote on economic parameters. The gas token is USDC, both today and in the documentation's description of the network. ARC is not needed to send a transaction, and the documentation states that Arc has "no volatile native token".

**Q: Where does a transaction fee go on Arc today, and where would it go under the whitepaper?**

Today the handler credits the whole fee, base fee plus priority fee, in USDC to the proposing validator's configured fee recipient. Nothing is burned and nothing is shared with stakers.

Under the whitepaper, the fee would be converted into ARC at block settlement, then split between validator and staker rewards and a permanent burn, with the ratio set by governance.

**Q: Why is stake-weighted proposer selection more than an added staking contract?**

On Arc, voting power already flows from the validator registry into Malachite's quorum computation. A staking contract that writes voting power there would therefore change how votes are weighted. Proposer selection, however, is a round-robin formula, `(h - 1 + r) mod n`, that ignores voting power. For stake to determine "weight in proposer selection", the consensus application needs a new proposer-selection algorithm.

**Q: What would protocol-level fee conversion to ARC require that the current design avoids?**

It requires a USDC/ARC exchange rate at settlement time, from an oracle, an onchain market or an auction. The documentation lists avoiding oracle dependencies for gas-price conversion as a reason Arc launched with USDC as its only gas token. The whitepaper does not name a price source, and it does not say who carries ARC price risk between fee collection and conversion.

**Q: How are ARC's supply and allocation designed?**

The design has three parts:

- **Supply.** 10 billion tokens at launch, with issuance starting at roughly 2–3% a year and decaying on a schedule that governance can adjust.
- **Target.** Inflation neutrality, where the burn from fees offsets issuance, with no fixed date.
- **Allocation.** 60% ecosystem, 25% Circle and 15% long-term reserve, with unlock schedules still to be announced.

**Q: Which governance decisions stay with Circle after the PoS transition, and what enforces parameters today?**

The whitepaper keeps three things with Circle:

- protocol rules and upgrades, where validators adopt Circle's decisions;
- stewardship and incident response;
- validator membership and the treasury.

Token holders would decide fees, inflation and burn parameters. Today those economic parameters sit in `ProtocolConfig` and are changed by a single controller account, and validator membership is managed by the `PermissionedValidatorManager` owner.

**Q: Does Arc have MEV protection today?**

Only at the RPC level. Nodes hide pending-transaction RPCs by default and remove the bundle and private-transaction methods from public endpoints. The mempool is not encrypted, blocks are built by the rotating proposer, and no builder auction exists. The whitepaper's encrypted mempools, TEE block building and sealed-bid auctions are future components.

## References

### Analyzed source

- [circlefin/arc-node](https://github.com/circlefin/arc-node) — analyzed at commit [`6e764023ee6515fe70573e123ed2db912a7207b4`](https://github.com/circlefin/arc-node/tree/6e764023ee6515fe70573e123ed2db912a7207b4) (10 commits after v0.8.0), 2026-09-25
- [circlefin/arc-remote-signer](https://github.com/circlefin/arc-remote-signer) — analyzed at commit [`a9e9fdb48c1e96a6c3fb875aba3d341e6a8af1a6`](https://github.com/circlefin/arc-remote-signer/tree/a9e9fdb48c1e96a6c3fb875aba3d341e6a8af1a6), 2026-09-25

### Whitepaper and documentation

- *ARC: The Native Asset of the Economic OS*, Circle, May 2026 (whitepaper, published through [arc.network](https://arc.network))
- [Arc documentation — Consensus layer](https://docs.arc.io/arc/concepts/consensus-layer)
- [Arc documentation — Stable fee design](https://docs.arc.io/arc/concepts/stable-fee-design)
- [Arc documentation — Stablecoin-native model](https://docs.arc.io/arc/concepts/stablecoin-native-model)
- [Arc documentation — Opt-in privacy](https://docs.arc.io/arc/concepts/opt-in-privacy)
- [Arc documentation — Deterministic finality](https://docs.arc.io/arc/concepts/deterministic-finality)
- [Arc documentation — RPC endpoints](https://docs.arc.io/arc/references/rpc-endpoints)

### Standards

- [EIP-1559: Fee market change for ETH 1.0 chain](https://eips.ethereum.org/EIPS/eip-1559)
- [EIP-7708: ETH transfers emit a log](https://eips.ethereum.org/EIPS/eip-7708)
- [Regulation (EU) 2023/1114 on markets in crypto-assets (MiCA)](https://eur-lex.europa.eu/eli/reg/2023/1114/oj)

### Related articles

- [Issuing a Token Under MiCA — The Crypto-Asset White Paper and Its Exemptions (Title II)]({{site.url_complet}}/2026/09/17/mica-crypto-asset-white-paper-token-issuers/)
- [Stablecoins Under MiCA — Asset-Referenced Tokens and E-Money Tokens (Titles III and IV)]({{site.url_complet}}/2026/09/17/mica-stablecoins-asset-referenced-tokens-e-money-tokens/)
- [BIO Tokenomics - Supply, Unlocks, Demand and Value Capture of Bio Protocol's Token]({{site.url_complet}}/2026/09/18/bio-protocol-tokenomics-analysis/)
- [Inside Circle's SponsorPaymaster — How a Verifying Paymaster Is Built]({{site.url_complet}}/2026/09/09/circle-sponsor-paymaster-erc4337/)
- [SLH-DSA — The Stateless Hash-Based Signature Standard (FIPS 205)]({{site.url_complet}}/2026/06/29/slh-dsa-fips-205-hash-based-signatures/)
- [Blockchain gas price]({{site.url_complet}}/2025/11/10/blockchain-gas-price/)
- [Malachite Consensus on Arc — How Circle's L1 Finalises a Block, Compared with CometBFT, HotStuff and Gasper]({{site.url_complet}}/2026/09/25/malachite-consensus-arc/)
