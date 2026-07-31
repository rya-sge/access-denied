---
layout: post
title: "Cross-Chain Bridge Threat Model - Assets, Trust Boundaries, STRIDE and Threat Register"
date:   2026-07-31
lang: en
locale: en-GB
categories: blockchain security defi
tags: BA-bridge threat-model stride cross-chain bridge attack-tree security-architecture risk
description: A structured OWASP threat model for cross-chain bridges, built from the Ronin 2022, Poly Network 2023, Ronin 2024 and Kelp DAO 2026 incidents, covering assets, trust boundaries, STRIDE analysis, an attack tree and a prioritised threat register.
image: /assets/article/blockchain/defi/cross-chain-bridge/2026-07-31-cross-chain-bridge-threat-model-mindmap.png
isMath: false
---

A bridge that has already been drained tells you where its threat model was wrong. Four incidents provide that evidence directly: Ronin in March 2022, Poly Network in July 2023, Ronin again in August 2024, and Kelp DAO in April 2026. Between them they cover an attack on people, an attack on a build pipeline, an attack on a deployment procedure, and an attack on the data an attestation layer reads about the origin chain.

This article turns those incidents into a reusable threat model, following the OWASP structure of four questions: what are we working on, what can go wrong, what are we going to do about it, and did we do a good job. Every threat in the register below is either observed in one of the four incidents or is a near neighbour of one that was.

The incidents themselves are described in the companion article, [Cross-Chain Bridge Hacks](https://rya-sge.github.io/access-denied/2026/07/31/cross-chain-bridge-hacks/), which covers those four alongside six others, grouped by failure class. This one is the analytical counterpart and does not repeat the narratives.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Threat Model Header

| Field | Value |
|---|---|
| System | Generic cross-chain token bridge (lock/unlock and burn/mint) |
| Version | 1.0 |
| Description | Moves token value between two chains by escrowing on one and releasing on the other, authorised by an off-chain attestation layer |
| Date | 31 July 2026 |
| Evidence base | Ronin 2022, Poly Network 2023, Ronin 2024 and Kelp DAO 2026 post-mortems and forensic analyses |
| Refresh triggers | Contract upgrade, signer set or verifier configuration change, new chain onboarded, security incident in this bridge or a comparable one, new node software release, change of RPC or data provider |

### Scope

**In scope.** The escrow contract on the origin chain, the off-chain attestation layer (validators, keepers, bridge operators, verifier networks, and any relay chain), the data path through which that layer observes the origin chain, the gateway or verifier contract on the target chain, the build and release pipeline that produces the node software, the upgrade and governance path for both contracts and the signer or verifier set, and the monitoring and pause capability.

**Out of scope.** The consensus security of the origin and target chains themselves, the security of the tokens being bridged, and end-user wallet compromise. These are real risks, but a bridge team cannot remediate them and they did not feature in any of the four incidents.

### External dependencies

| ID | Dependency | Security relevance |
|---|---|---|
| D1 | Origin and target chain liveness and finality | An attestation to a reorganised block authorises a release that the origin chain no longer backs |
| D2 | RPC providers used by the attestation layer to observe chains | A malicious or compromised RPC feeds attestors a false view of the origin chain, which is what happened at Kelp DAO in 2026 |
| D3 | Node software toolchain and dependency graph | Compromise here reaches every signer at once, which is what happened at Poly Network |
| D4 | Corporate IT and identity infrastructure of each signer operator | The initial foothold in Ronin 2022 |
| D5 | Key custody hardware or software at each signer | Determines whether a host compromise becomes a key compromise |
| D6 | Public mempool of the target chain | Configuration mistakes are visible to anyone before they are fixed |
| D7 | Availability of each origin-chain data source | Removing the honest sources is enough to force failover onto compromised ones |

## System Overview and Trust Boundaries

A user locks assets in an escrow contract on the origin chain. The off-chain attestation layer observes the lock event and produces an authorisation, either as a set of threshold signatures or as a signed relay chain header plus a Merkle proof. A relayer, usually permissionless, submits that authorisation to the gateway contract on the target chain, which verifies it and releases the corresponding assets.

![Cross-chain bridge data flow and trust boundaries]({{site.url_complet}}/assets/article/blockchain/defi/cross-chain-bridge/2026-07-31-cross-chain-bridge-threat-model-dfd.png)

Five boundaries matter, and each one was crossed hostilely in at least one of the four incidents.

| ID | Trust boundary | What crosses it | Incident that crossed it |
|---|---|---|---|
| TB1 | Origin chain to attestation layer | Lock events and origin chain state | Kelp DAO 2026 |
| TB2 | Attestation layer to target chain | Signatures, headers, Merkle proofs, verifier attestations | Ronin 2022, Poly Network 2023, Ronin 2024, Kelp DAO 2026 |
| TB3 | Corporate IT to signer host | Administrative access, delegated signing rights | Ronin 2022 |
| TB4 | Build environment to running binary | Executable node software | Poly Network 2023 |
| TB5 | Upgrade admin to live implementation | Implementation address and initializer state | Ronin 2024 |

TB2 is where every attack has to arrive. The gateway counts valid attestations against a threshold and has no independent view of the origin chain, so any attack that produces enough valid attestations, or that lowers the threshold, is indistinguishable from legitimate use at the moment of execution.

TB1 was originally scored here as theoretical. Kelp DAO removed that comfort. An attestor that reads the origin chain over RPC depends on a data path sitting outside both chains and outside the contract repository. Corrupting it yields an attestation that TB2 accepts, with no signing key ever stolen.

### Trust levels

| ID | Principal | Privilege |
|---|---|---|
| L1 | Anonymous account | Can call the public lock function and submit proofs |
| L2 | Bridge user | Has assets in escrow awaiting release |
| L3 | Relayer | Submits attestations; usually permissionless, so equivalent to L1 in authority |
| L4 | Signer operator | Holds one key in the threshold set |
| L5 | Signer host administrator | Controls the machine on which a signer runs |
| L6 | Build and release engineer | Determines the binary every signer executes |
| L7 | Signer set governor | Can add, remove or reweight signers |
| L8 | Upgrade admin | Can replace the implementation behind the proxy |
| L9 | Guardian | Can pause the bridge |
| L10 | Application delegate | Chooses which verifiers are required for this application's messages, and how many |

L5 and L6 are the levels that bridge designs most often leave undocumented, and they are the ones that produced two of the four incidents. L10 is newer and easier still to overlook: on a configurable messaging protocol the application, not the protocol, decides how much verification its own messages receive. A threat model that stops at L4 misses all three.

### Assets

| ID | Asset | Why an attacker wants it | Trust levels with access |
|---|---|---|---|
| A1 | Escrow balance on the origin chain | The prize; total value of the bridge | L1 via a valid release, L8 via upgrade |
| A2 | Mint authority on the target chain | Inflates supply without touching escrow | L4 collectively, L8 |
| A3 | Signer private keys | Produces authorisations directly | L4, L5, and L6 transitively |
| A4 | Signer set membership and threshold | Changes how many keys are needed | L7, L8 |
| A5 | Node binary integrity | Grants A3 across every signer at once | L6 |
| A6 | Proxy implementation and initializer state | Controls all verification logic | L8 |
| A7 | Processed message set | Prevents replay | L8 |
| A8 | Bridge availability | Denial of service, or trapping user funds | L4, L9 |
| A9 | Pause capability | Removing it prevents containment | L8, L9 |
| A10 | The attestation layer's view of origin chain state | Corrupting it produces authentic attestations over events that never happened | L5, and anyone controlling a source in D2 |
| A11 | Required verifier count and identity | Reducing it to one removes every independent check | L7, L10 |

## STRIDE Analysis

Applied to each component, with the incident that demonstrates the threat noted where one exists.

### Origin escrow contract

- **Spoofing.** Low relevance; the lock function is intentionally permissionless.
- **Tampering.** Escrow accounting drift where the contract trusts a transfer amount rather than measuring the balance delta. Fee-on-transfer and rebasing tokens break the invariant that escrow covers circulating bridged supply.
- **Repudiation.** Lock events without a unique, chain-bound identifier cannot be matched one-to-one against releases, which is what a reconciliation monitor needs.
- **Information disclosure.** Not material; the escrow balance is public by design.
- **Denial of service.** A pause that traps deposits without a withdrawal path leaves user funds stranded.
- **Elevation of privilege.** An upgradeable escrow lets L8 drain it directly, bypassing the entire attestation layer.

### Off-chain signer set

- **Spoofing.** Key theft from a signer host. **Ronin 2022**, where a spear-phishing foothold led to four keys, and delegated signing authority that was never revoked supplied the fifth.
- **Tampering.** A backdoored binary that exfiltrates keys on startup. **Poly Network 2023**.
- **Repudiation.** Without per-signer attribution and logging, a compromised operator cannot be identified after the fact, and Dedaub could not distinguish key theft from a rug pull using on-chain data alone.
- **Information disclosure.** Keys readable from a wallet file on a general-purpose host, which is the precondition the Poly Network Trojan exploited.
- **Denial of service.** Enough signers offline to make the threshold unreachable freezes withdrawals.
- **Elevation of privilege.** Governance capture of the signer set, adding attacker keys or lowering the weight required. On a configurable protocol the application delegate can achieve the same effect by choosing a single required verifier, which is how the Kelp DAO pathway was set up.

### Relay chain, where present

- **Spoofing.** Signing a header for a chain state that never existed. **Poly Network 2023** cited relay block height 30150181, which does not exist on the real relay chain.
- **Tampering.** Altering the transaction parameters between origin chain and relay chain, so that the released amount differs from the locked amount. The legitimate lock was 0.000000000000001 ETH and the release was 1592.518 ETH.
- **Repudiation.** A relay chain that is not independently observable leaves no external record to reconcile against.

### Origin chain data feed

- **Spoofing.** An RPC endpoint that answers as though it were an honest full node. **Kelp DAO 2026**, where two internal op-geth nodes had their binaries swapped and their running memory patched.
- **Tampering.** Selective responses that differ by caller, so the attestor is lied to while monitoring and indexing services are told the truth. This is what defeated LayerZero's observability stack.
- **Repudiation.** A self-deleting implant removes the binary, local logs and configuration once the attack is complete, so the tampered responses leave no artefact.
- **Denial of service.** Taking the honest sources offline is an attack on integrity, not only on availability, whenever failover degrades onto a smaller set. **Kelp DAO 2026**, where a DDoS against the external RPC provider forced the verifier onto the two poisoned nodes.
- **Elevation of privilege.** Control of a quorum of data sources is equivalent to control of the attestation itself, without ever touching a key.

### Target gateway and verifier

- **Spoofing.** Replay of a valid proof, either a second time on the same chain or on a different chain, when messages are not bound to a chain identifier and a single-use nonce.
- **Tampering.** A Merkle verifier that accepts a zero-length witness places no structural constraint on what a signed root can authorise, since the leaf hash simply has to equal the root. **Identified by Dedaub** at Poly Network.
- **Repudiation.** Releases that do not record which signatures authorised them cannot be audited afterwards.
- **Denial of service.** Unbounded proof size or depth turns verification into a gas exhaustion vector.
- **Elevation of privilege.** A threshold that evaluates to zero authorises an unsigned withdrawal. **Ronin 2024**, where `_totalOperatorWeight` was left uninitialised and `0 >= 0` satisfied the check.

### Upgrade and governance path

- **Tampering.** An upgrade that changes verification logic or the threshold, whether malicious or mistaken. **Ronin 2024** was the mistaken case, and the mistaken case is more common than the malicious one.
- **Information disclosure.** The upgrade transaction is public in the mempool before it is mined, so a misconfiguration is observable by anyone watching. An MEV bot found the Ronin 2024 flaw this way, 48 minutes after the upgrade.
- **Elevation of privilege.** A single admin key controlling the proxy is a shorter path to the escrow than the entire signer set.

### Build and release pipeline

- **Tampering.** Implanting code in the compilation environment. **Poly Network 2023**, where the Trojan ran on startup and uploaded the local wallet keys.
- **Information disclosure.** Exfiltration channel from a signer host outbound to attacker infrastructure, in that case a TCP connection to a domain with a history as command-and-control.
- **Elevation of privilege.** One compromised build host yields every signer key, which collapses a multi-party threshold into a single failure domain.

### Monitoring and response

- **Repudiation.** Absence of large-outflow monitoring meant Ronin 2022 went unnoticed for six days and was found only because an unrelated user withdrawal failed.
- **Denial of service.** A guardian able to pause without accountability can censor or freeze the bridge.
- **Elevation of privilege.** An attacker who can disable monitoring or revoke the pause capability removes the only remaining containment.

## Attack Tree

The root goal is the release of escrowed assets to an attacker-controlled address. The branches are the distinct routes to it, with the incident that used each one marked.

![Cross-chain bridge attack tree]({{site.url_complet}}/assets/article/blockchain/defi/cross-chain-bridge/2026-07-31-cross-chain-bridge-attack-tree.png)

The tree makes the central point visible. Only two of the five branches, bypassing proof verification and attacking the escrow directly, need a defect in the contract code. One more turns on deployment and configuration. The remaining two end at the same gateway call, executed exactly as written, and no amount of Solidity review closes them.

### Abuse cases

| Use case | Abuse case | STRIDE |
|---|---|---|
| A user locks assets on the origin chain | An attacker locks a negligible amount to obtain a legitimate cross-chain identifier, then inflates the released amount in the attestation | S, T |
| A relayer submits a withdrawal proof | An attacker submits a proof with no valid signatures against a threshold of zero | E |
| A relayer submits a withdrawal proof | An attacker resubmits a previously executed proof, or submits it on a second chain | S |
| The team upgrades the gateway implementation | An observer detects an uninitialised parameter in the mempool and exploits it before the team notices | I, E |
| A signer operator runs the node software | The operator runs a binary whose build was compromised, leaking the key on first start | T, I |
| The team grants another party temporary signing rights | The grant is never revoked and becomes a permanent path to the threshold | E |
| A guardian pauses the bridge during an incident | An attacker with guardian access pauses it to trap user funds, or unpauses it during an attack | D |
| An attestor reads the origin chain to confirm a commitment | An attacker serves the attestor a fabricated view while answering honestly to everyone else | S, T |
| An attestor falls back to a secondary data source when the primary is unreachable | An attacker takes the honest sources offline so that failover lands on the ones they control | D, E |
| The application selects which verifiers must attest to its messages | The application selects one, or inherits a default it never reviewed, so no independent check exists | E |

## Threat Register

Risk is scored qualitatively. Likelihood reflects whether the attack is remotely reachable, automatable, and how much capability it needs. Impact reflects the fraction of escrow at risk and whether the loss is recoverable.

| ID | Threat | Boundary | STRIDE | Likelihood | Impact | Risk | Decision | Countermeasure |
|---|---|---|---|---|---|---|---|---|
| T-01 | Signer keys stolen after compromise of the operator's IT estate | TB3 | S, I | High | Critical | **Critical** | Mitigate | Hardware or HSM key custody; signer hosts isolated from corporate identity; independent operators |
| T-02 | Delegated signing authority granted temporarily and never revoked | TB3 | E | Medium | Critical | **Critical** | Mitigate | Every delegation carries an expiry; periodic entitlement review; alert on use of a dormant grant |
| T-03 | Backdoored node binary exfiltrates keys from every signer | TB4 | T, I | Medium | Critical | **Critical** | Mitigate | Independent per-party compilation with binary hash comparison; containerised reproducible builds; isolated audited build hosts |
| T-04 | Attestation to an origin chain state that never existed | TB2 | S, T | Medium | Critical | **Critical** | Mitigate | Independent reconciliation of every release against the origin chain lock; automatic halt on mismatch |
| T-05 | Threshold parameter uninitialised or set to zero | TB5 | E | Medium | Critical | **Critical** | Mitigate | Assert threshold greater than zero at the point of use; post-upgrade invariant checks before unpausing |
| T-06 | Upgrade replaces verification logic or drains escrow | TB5 | T, E | Low | Critical | **High** | Mitigate | Multi-signature plus timelock on `ProxyAdmin`; upgrade diff published before execution |
| T-07 | Merkle verifier accepts a zero-length or malformed witness | TB2 | T | Medium | High | **High** | Mitigate | Reject empty witnesses; enforce expected leaf structure and proof depth; domain-separate leaf and internal node hashing |
| T-08 | Valid proof replayed on a second chain or a second time | TB2 | S, T | Medium | High | **High** | Mitigate | Bind every message to a chain identifier and a single-use identifier; persist and check the processed set |
| T-09 | Signer set governance captured to add attacker keys | TB2 | E | Low | Critical | **High** | Mitigate | Signer set changes behind timelock and independent approval; alert on any membership change |
| T-10 | Loss undetected long enough to remove any chance of response | All | R, D | High | High | **Critical** | Mitigate | Large-outflow monitoring; withdrawal delay with challenge window; defined on-call owner and tested pause procedure |
| T-11 | Misconfiguration observable in the public mempool before it is fixed | TB5 | I | High | High | **Critical** | Mitigate | Pause the gateway for the duration of a multi-step upgrade; private submission of upgrade transactions |
| T-12 | Escrow accounting drift from fee-on-transfer, rebasing, or donation | TB1 | T | Medium | Medium | **Medium** | Mitigate | Measure balance deltas rather than trusting amounts; explicit allowlist of supported token behaviours |
| T-13 | Signers unavailable, threshold unreachable, withdrawals frozen | TB2 | D | Medium | Medium | **Medium** | Accept with control | Operator diversity and redundancy; documented recovery procedure for a stalled signer set |
| T-14 | Guardian pauses or unpauses without accountability | TB5 | D, E | Low | High | **Medium** | Mitigate | Guardian limited to pause only, never unpause; unpause requires the full governance path |
| T-15 | No attribution of which signer authorised a release | TB2 | R | Medium | Medium | **Medium** | Mitigate | Record the signer set and signatures per release; per-signer logging retained off-chain |
| T-16 | Compromised or poisoned data sources feed the attestation layer a false view of the origin chain | TB1 | S, T | Medium | Critical | **Critical** | Mitigate | Several independent origin-chain sources per attestor, with the attestor **failing closed** when agreement is unavailable rather than failing over to a reduced set; monitoring that reads through a separate path |
| T-17 | The application requires a single verifier, or inherits a platform default it never reviewed | TB2 | S, E | Medium | Critical | **Critical** | Mitigate | At least two independent required attestors; configuration pinned rather than inherited; the party bearing the loss owns and reviews the choice |
| T-18 | Honest data sources are taken offline so that failover degrades onto attacker-controlled ones | TB1 | D, E | Medium | Critical | **Critical** | Mitigate | Treat loss of a source as a reason to stop attesting, not to substitute; alert on any failover; capacity and provider diversity for the sources themselves |

### Prioritised mitigation list

The register above orders threats by risk. Grouped by what actually has to be built, the work falls into four tiers.

- **Tier 1, loss limitation.** Per-transaction value caps with manual approval above the limit, per-token daily volume limits, and a withdrawal delay with a challenge window. These address T-04, T-10 and T-11 and, unusually, they do not depend on knowing which attack is coming. All three teams converged on them independently.
- **Tier 2, attestation integrity.** At least two independent required verifiers, a pinned configuration, several independent origin-chain data sources per attestor, and a refusal to attest when those sources stop agreeing. These address T-16, T-17 and T-18. Nothing in the other tiers touches them, which is why a bridge with exemplary key custody and reproducible builds still lost $292M in 2026.
- **Tier 3, key and identity custody.** Hardware custody, isolation of signer hosts from corporate identity, expiring delegations, and entitlement review. These address T-01, T-02 and T-09.
- **Tier 4, supply chain.** Reproducible builds compiled independently by each party with hash comparison, on isolated and audited build hosts. This addresses T-03, and nothing else does.
- **Tier 5, contract and upgrade hygiene.** Post-upgrade invariant assertions, pausing during upgrades, timelocked admin, strict proof validation, and replay binding. These address T-05 through T-08 and T-11.

Tier 1 is listed first deliberately. It is the only tier that bounds the loss when the others fail, and in all four incidents the others had already failed.

## Assumptions and Open Questions

- **The signer count is assumed to overstate independence.** Counting keys is easy and counting failure domains is not. Any real application of this model should replace the assumption with an audit of where each signer actually runs and who administers it.
- **The relay chain is treated as part of the attestation layer**, not as an independent chain with its own security. Poly Network's incident supports that treatment, but a bridge whose relay chain has genuinely independent validators would need TB2 decomposed further.
- **Recovery is assumed to be out of band.** None of the four incidents was resolved by an on-chain mechanism; outcomes were determined by corporate balance sheets, the attacker's goodwill, or a coordinated industry effort. A model that assumes on-chain recoverability is assuming something no evidence here supports.
- **Fund destination after the fact is only partly documented.** The Ronin 2022 laundering path is well traced, Ronin 2024 was returned, and Poly Network 2023 has no published account of what was realised. Any threat model that reasons about attacker economics inherits that gap.
- **Value at risk should be measured against liquidity, not notional balances.** Poly Network's notional figure of around $34B never corresponded to realisable value because the affected tokens were illiquid.
- **Redundancy is assumed to fail closed, and usually does not.** Most deployed redundancy substitutes a healthy source for an unhealthy one, which is correct for availability and wrong for integrity. Any control in this model written as "use several independent sources" is incomplete until the behaviour on partial loss is specified.
- **The verifier configuration is assumed to be reviewed by whoever bears the loss.** On a protocol where the application picks its own verifier set, that assumption is frequently false, and neither the protocol operator nor the application treats the choice as theirs to defend.

## Validation

The OWASP fourth question asks whether the model is any good. Against its own checklist:

- Every trust boundary in the diagram has at least one threat in the register, and TB2 has seven.
- Every STRIDE category appears at least once per major component, with the exception of spoofing and information disclosure on the escrow contract, where they are not material and are documented as such.
- Every threat has a risk decision and a countermeasure. Owners are left unassigned here because this is a generic model; a real one must name them.
- Abuse cases cover the four main use cases plus the two administrative ones.
- Refresh triggers are documented in the header. Three of the four incidents happened at moments a refresh trigger would have caught, namely a change in delegated permissions, a contract upgrade, and a verifier configuration left at one.

The main known weakness is that the model is built from four incidents that share a trust structure. All four delegated verification to an external attestation layer, whether a validator set, a keeper set or a single configured verifier. A bridge that verifies origin chain state with a light client or a validity proof moves part of the threat surface into circuit and proof-system correctness, which this model does not cover.

A second weakness is arithmetic. The register grew from sixteen entries to eighteen because one incident, Kelp DAO, exposed a boundary previously scored as theoretical. That is the model working as intended, but it is also a reminder that the register describes the attacks that have happened, and the residual risk it leaves is the attack that has not.

## Conclusion

The register places ten threats at critical risk, and nine of the ten sit outside the smart contracts. Key custody, delegated permissions, the build pipeline, the upgrade procedure, the verifier configuration and the data feed underneath it account for far more critical risk than the verification logic does, which matches the incident record: in three of the four cases the contracts executed correctly and still released the escrow.

The practical consequence for anyone applying this model is that scope determines whether it is useful. A review bounded by the contract repository will find T-05, T-07, T-08 and T-12, and will miss T-01 through T-04 and T-16 through T-18, which between them caused every one of the four losses. The Tier 1 controls are worth building first, not because they are the most sophisticated, but because they are the only ones that bound the loss when a threat the model did not anticipate turns out to be real.

![Cross-chain bridge threat model mindmap]({{site.url_complet}}/assets/article/blockchain/defi/cross-chain-bridge/2026-07-31-cross-chain-bridge-threat-model-mindmap.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Trust boundary** | A point in a system where the privilege level changes; the place where a threat model expects to find its highest-value threats. |
| **Data flow diagram** | A decomposition of a system into external entities, processes, data stores and flows, annotated with trust boundaries. |
| **STRIDE** | A threat taxonomy covering spoofing, tampering, repudiation, information disclosure, denial of service and elevation of privilege. |
| **Attack tree** | A goal-oriented decomposition of the routes to a single attacker objective, with the root as the goal and branches as alternative paths. |
| **Abuse case** | The adversarial counterpart of a use case, describing how the same functionality is exercised by an attacker. |
| **Threat register** | The table of identified threats with likelihood, impact, risk rating, a decision to mitigate, accept, eliminate or transfer, and an owner. |
| **Failure domain** | A set of components that fail together; the unit that actually matters when counting the independence of a threshold signing set. |
| **Attestation layer** | The off-chain component that observes the origin chain and authorises releases on the target chain, whether by threshold signature or relay chain proof. |
| **Challenge window** | A delay between authorisation and release during which a monitor can veto a transaction, converting detection into prevention. |
| **Residual risk** | The risk that remains after countermeasures are applied, which must be explicitly accepted rather than assumed to be zero. |

## Annex — Security Implementation Checklist

Organised by trust boundary, so it can be run directly against the diagram. It complements the control checklist in the [companion article](https://rya-sge.github.io/access-denied/2026/07/31/cross-chain-bridge-hacks/), which is organised by control family rather than by boundary.

### TB1 — Origin chain to attestation layer

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Each attestor reads origin chain state from more than one independent source and requires agreement before signing. | A single compromised RPC convinces the whole set that a commitment occurred. |
| ☐ | Loss of a data source stops attestation rather than triggering failover onto a reduced set. | An attacker takes the honest sources offline and the system substitutes the ones they control, as at Kelp DAO. |
| ☐ | Any failover between data sources raises an alert, and the attestor records which sources it used. | The substitution is invisible, so the forged attestation looks routine afterwards. |
| ☐ | Monitoring reads chain state through a path that shares no dependency with the attestation layer. | A tampered node shows the monitor the same fiction it shows the verifier. |
| ☐ | Signers wait for finality appropriate to the origin chain before attesting. | A reorganisation removes the lock while the release stands. |
| ☐ | Escrow accounting uses measured balance deltas, not the requested amount. | Fee-on-transfer or rebasing tokens break the invariant that escrow covers bridged supply. |
| ☐ | Every lock emits a unique identifier bound to the origin chain. | Releases cannot be reconciled one-to-one against locks. |

### TB2 — Attestation layer to target chain

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The required threshold is validated as strictly positive at the point of use. | An uninitialised threshold makes `0 >= 0` a passing authorisation check. |
| ☐ | At least two independent attestors are required, and the configuration is pinned rather than inherited from a platform default. | One verifier's corrupted view authorises a release with nothing able to contradict it. |
| ☐ | The party that bears the loss owns and periodically reviews the verifier configuration. | Nobody defends the choice, and each side assumes the other reviewed it. |
| ☐ | Signatures are deduplicated by signer and checked against the current set. | Repeated signatures from one compromised key satisfy a naive count. |
| ☐ | Every message is bound to a chain identifier and a single-use identifier that is persisted on execution. | A valid proof is replayed on another chain or a second time. |
| ☐ | Merkle verification rejects zero-length witnesses and enforces expected leaf structure and depth. | A signed root authorises an arbitrary single-leaf payload with no structural constraint. |
| ☐ | Proof size and depth are bounded. | Verification becomes a gas exhaustion vector. |
| ☐ | Each release records the signer set and signatures that authorised it. | Post-incident attribution is impossible from on-chain data. |

### TB3 — Corporate IT to signer host

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Signing keys live in hardware or an HSM and are never readable from a file on the host. | A host compromise becomes an immediate key compromise. |
| ☐ | Signer hosts are isolated from corporate identity and general-purpose workstations. | A phishing foothold reaches the validator infrastructure by lateral movement. |
| ☐ | Every delegation of signing authority carries an expiry and is revoked when its purpose ends. | A dormant grant supplies the marginal signature that reaches the threshold. |
| ☐ | Use of a delegated or dormant signing path raises an alert. | The delegation is exercised by an attacker with no one watching. |
| ☐ | Signers in the threshold occupy distinct organisations, networks and administrative domains. | The nominal threshold collapses to one failure domain. |

### TB4 — Build environment to running binary

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Each party compiles the node software independently and compares binary hashes before execution. | One compromised build host backdoors every participant at once. |
| ☐ | Builds are reproducible, with a containerised or otherwise pinned toolchain. | Legitimate binaries differ, the comparison is abandoned, and the control lapses. |
| ☐ | Build hosts are isolated from other uses, with access logged and audited. | A build machine used for general work is reachable from an ordinary phishing foothold. |
| ☐ | Source repository access is under fine-grained control with an audit trail. | An implant is introduced without attribution. |
| ☐ | Signer hosts restrict outbound network egress to known destinations. | Keys are exfiltrated to attacker infrastructure on first start. |

### TB5 — Upgrade admin to live implementation

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every storage variable read by a new implementation is written by an initializer the upgrade actually executes. | An uninitialised threshold defaults to zero and all authorisation passes. |
| ☐ | Post-upgrade invariants are asserted before the contract is unpaused. | A misconfiguration goes live and is discoverable by anyone reading the mempool. |
| ☐ | The gateway is paused for the duration of a multi-step upgrade. | The window between two transactions is exploitable, 48 minutes in the Ronin 2024 case. |
| ☐ | `ProxyAdmin` is behind a multi-signature and a timelock, with the diff published before execution. | A single key is a shorter path to the escrow than the entire signer set. |
| ☐ | The guardian can pause but not unpause; unpausing requires full governance. | Pause authority becomes a censorship or trap mechanism. |

### Cross-boundary — detection and loss limitation

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | An independent monitor reconciles every target chain release against the corresponding origin chain lock and halts on mismatch. | A forged release is indistinguishable from a legitimate one until a user complains. |
| ☐ | Per-transaction value caps require human approval above a threshold. | The entire escrow leaves in two transactions with no human in the loop. |
| ☐ | Per-token daily volume limits suspend the route when exceeded. | An attacker drains across many transactions and many chains before anyone reacts. |
| ☐ | Large withdrawals are subject to a delay or challenge window before the user claims. | There is no interval in which detection can become prevention. |
| ☐ | A tested pause procedure exists with a named on-call owner and a target reaction time. | Hours elapse while an attacker works through multiple chains. |

## Frequently Asked Questions

**Q: Why is TB2 called the decisive boundary when four different boundaries were actually crossed in the four incidents?**

Because TB2 is where every attack has to end. The gateway contract is the only component that can move escrowed assets, and it authorises a release by counting valid signatures against a threshold. Crossing TB3 (stealing keys from a host) or TB4 (backdooring the binary) is a means of producing signatures that TB2 will accept; crossing TB5 is a means of lowering the threshold TB2 enforces.

The practical consequence is where you place detection. Controls at TB2 that do not trust the attestation, such as reconciliation against the origin chain and value caps, catch all four routes. Controls that verify the attestation more carefully catch none of them, because the attestations were valid.

Crossing TB1, as the Kelp DAO attackers did, is the same manoeuvre one step further out: rather than producing a signature TB2 will accept, they arranged for the honest signer to produce it voluntarily.

**Q: What is the difference between counting signers and counting failure domains, and why does it change the risk rating?**

Counting signers measures how many keys must sign. Counting failure domains measures how many independent events must occur for those keys to be produced by one attacker.

Ronin's 2022 set had nine validators and a threshold of five, which looks like five independent compromises. In practice, one phishing campaign against one company yielded four keys, and one un-revoked permission yielded the fifth, so the real count was closer to two. Poly Network had four keepers requiring three signatures, but a single build pipeline produced the software for all of them, giving a real count of one.

This is why T-01 and T-03 carry critical impact despite involving a threshold scheme. The threshold does not multiply attacker cost if the signers share an administrative domain, a network, or a toolchain.

Kelp DAO is the limiting case. Its pathway required one verifier, so the nominal count and the real count were both one, and the failure domain was whatever that verifier depended on.

**Q: T-16 was rated Medium in the first version of this register. What changed?**

Evidence. The threat was written as a plausible neighbour of the observed incidents, scored Low likelihood because no bridge had visibly lost money that way, and its countermeasure was the obvious one: read from several independent RPC sources and require agreement.

The Kelp DAO incident of 18 April 2026 executed that exact threat for 116,500 rsETH, roughly $292M. It also invalidated the countermeasure as written. LayerZero's DVN already read from internal and external RPC nodes for redundancy. The attackers poisoned two internal nodes and then ran a denial of service attack against the external provider, and the resulting failover put the verifier on the poisoned pair alone. Requiring agreement is worthless if the system responds to disagreement by shrinking the set until agreement is trivial.

So T-16 moves to Critical, its countermeasure now specifies failing closed, and T-18 splits out the availability attack that made the integrity attack possible.

**Q: An auditor reviews the bridge contracts thoroughly and finds nothing. Which threats in the register remain open?**

Most of the critical ones:

- **T-01 and T-02** are key custody and permission management, which live in the operator's IT estate and are invisible in the repository.
- **T-03** is the build pipeline, which produces the binary rather than the contracts.
- **T-04** is a valid attestation to a false origin state, which the contracts are supposed to accept.
- **T-10 and T-11** are detection and deployment procedure, not code.
- **T-16 and T-18** are the data path the attestation layer reads and how it behaves when that path degrades, neither of which appears in any repository.
- **T-17** is a configuration choice, and a reviewer will only catch it by reading the deployed verifier configuration rather than the contracts.

A contract review does cover T-05 (assuming the reviewer checks initializer coverage rather than only the withdrawal logic), T-07, T-08 and T-12. That is four of eighteen threats, and only one of the ten rated critical.

**Q: Why does the mitigation list put value caps and withdrawal delays in Tier 1, ahead of key custody and reproducible builds?**

Because they are the only controls that work against a threat the model failed to anticipate. Key custody stops key theft, reproducible builds stop supply chain implants, and invariant assertions stop uninitialised parameters. Each is specific to a route that is already known.

A per-transaction cap and a challenge window bound the loss regardless of how the authorisation was obtained. They would have limited all four incidents, and they would also limit a fifth using a route none of the four used. That is not hypothetical: this register was written with three incidents in it, and the fourth arrived through the boundary scored lowest.

**Q: The model documents "recovery is assumed to be out of band". Why is that an assumption worth writing down?**

Because it contradicts what a bridge design usually implies. A protocol that holds user assets in escrow reads as though the protocol itself is responsible for their safety, and a threat model that omitted the assumption would leave a reader thinking some on-chain mechanism handles the worst case.

None of the four incidents was resolved on-chain. Ronin 2022 users were made whole from a funding round and company balance sheet, Ronin 2024 was resolved because the exploiter chose to return the funds for a bounty, Kelp DAO's backing was restored by an industry recovery effort that raised around $300M and by liquidating the attacker's own leveraged positions, and Poly Network 2023 has no published recovery at all. Every one of those depended on someone outside the protocol choosing to act. Stating the assumption makes it visible that the residual risk after every countermeasure is a total, unrecoverable loss of escrow, which is what justifies putting loss limitation ahead of everything else.

**Q: How would this model change for a bridge that uses a light client or a validity proof instead of a signing set?**

TB2 changes character rather than disappearing. Instead of counting signatures, the gateway verifies a proof about origin chain state, so T-01 through T-04 (key theft, stale delegation, backdoored binaries, forged attestation) lose most of their force, since there is no threshold set whose compromise authorises a release.

What replaces them is a new threat class at the same boundary: soundness bugs in the circuit or proof system, trusted setup compromise, and mismatches between the verified statement and the intended one. TB4 and TB5 are unchanged, because the prover software still has to be built and the verifier contract still has to be upgraded, and Ronin 2024 would have happened in exactly the same way to a ZK bridge with a skipped initializer.

T-16 and T-18 also survive, in a weaker form. A prover still has to learn what the origin chain contains before it can prove anything about it, and it usually learns that over the same kind of data path. The proof constrains the statement, so a fabricated view produces a valid proof of a false statement rather than an unconstrained release, which is a real improvement. It is not an exemption.

**Q: The register rates T-13, signers unavailable and withdrawals frozen, as medium and marks it "accept with control" rather than "mitigate". Why treat availability differently?**

Because the countermeasures for availability and for integrity point in opposite directions. Lowering the threshold, adding signers, or building an emergency bypass all make it easier to keep the bridge running when signers are offline, and all of them enlarge the set of ways an attacker can reach a valid authorisation.

Given that the observed losses came from integrity failures and not from liveness failures, the model accepts a higher availability risk in exchange for a tighter integrity posture, and controls it through operator diversity and a documented recovery procedure rather than through a mechanism that weakens the threshold. That is a deliberate risk decision, and like every accepted risk it should be recorded with a named owner rather than left implicit.

## References

### Incident sources

- [Back to Building: Ronin Security Breach Postmortem](https://roninchain.com/blog/posts/back-to-building-ronin-security-breach-6513cc78a5edc1001b03c364) — Sky Mavis official post-mortem, 27 April 2022
- [North Korea's Lazarus Group identified as exploiters behind $540 million Ronin bridge heist](https://www.elliptic.co/blog/540-million-stolen-from-the-ronin-defi-bridge) — Elliptic, 14 April 2022
- [Poly Network Hack Postmortem](https://dedaub.com/blog/poly-network-hack/) — Dedaub, Neville Grech
- [The Poly Network Exploit Analysis](https://polynetwork.medium.com/the-poly-network-exploit-analysis-b0a77aff6078) — Poly Network, 20 November 2023
- [Poly Bridge Cross-Chain Security Reinforcement Solution](https://polynetwork.medium.com/poly-bridge-cross-chain-security-reinforcement-solution-86b8c9abecbc) — Poly Network, 22 December 2023
- [Ronin Bridge Attack: $12M Loss](https://threesigma.xyz/blog/exploit/ronin-network-12m-exploit-analysis) — Three Sigma, Simeon Cholakov, 7 August 2024
- [LayerZero Labs KelpDAO Incident Report](https://layerzero.network/blog/layerzero-labs-kelpdao-incident-report) — LayerZero, 20 May 2026
- [KelpDAO Incident Statement](https://layerzero.network/blog/kelpdao-incident-statement) — LayerZero, 19 April 2026
- [LayerZero Update](https://layerzero.network/blog/an-overdue-apology) — LayerZero, 8 May 2026
- [April 18, 2026 rsETH Incident Post Mortem](https://x.com/aave/status/2060901386611499378) — Aave

### Threat modelling methodology

- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [Threat Modeling Manifesto](https://www.threatmodelingmanifesto.org/)

### Related articles

- [Cross-Chain Bridge Hacks - Ten Incidents, Five Failure Classes](https://rya-sge.github.io/access-denied/2026/07/31/cross-chain-bridge-hacks/)
- [Zero-Knowledge Proof Failures in Cross-Chain Bridges](https://rya-sge.github.io/access-denied/2026/06/19/zkp-cross-chain-bridge-hacks/)

### Tooling

- [Claude Code](https://claude.com/product/claude-code)
