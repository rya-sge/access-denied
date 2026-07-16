---
layout: post
title: "Smart Contract Security on Cardano: What the eUTXO Model Removes and What Remains"
date:   2026-07-16
lang: en
locale: en-GB
categories: blockchain
tags: cardano security eutxo smart-contracts plutus aiken validator audit
description: A technical guide to Cardano smart-contract security. Covers the attack classes the eUTXO model removes by design (reentrancy, double-spend, MEV) and the vulnerabilities that remain (double satisfaction, datum hijacking, token forgery, resource exhaustion) with defensive patterns.
image: /assets/article/blockchain/cardano/cardano-smart-contract-security.png
isMath: false
---

A deployed validator is immutable, or nearly so, and it usually guards value, which makes a single flaw a permanent, exploitable loss in an adversarial setting. Cardano's Extended UTXO (eUTXO) model helps by removing several of the worst attack classes structurally, but the remaining risks are the developer's responsibility and they are specific to the model. This article separates the two: what the platform protects against by design, the vulnerability classes that still require careful validator logic, the defensive patterns experienced teams rely on, and how to verify a contract before mainnet. It follows the Cardano [developer portal's security documentation](https://developers.cardano.org/) and its vulnerability catalog.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Two layers of security, and one that is not the contract's

Before the contract-level discussion, one boundary is worth drawing. Network-level threats such as 51%, long-range, and eclipse attacks target consensus, not a validator, and Cardano's Ouroboros protocol defends against those. Everything below is application-level: the security of the validator logic a developer writes.

Within that scope, the eUTXO model itself removes some attack classes, and the rest fall to the developer. The threat model splits cleanly along that line.

## What the eUTXO model removes by design

Four attack classes that dominate account-based smart-contract security do not exist on Cardano, and they are removed structurally rather than by careful coding.

- **Reentrancy is impossible.** The reentrancy attack, responsible for the 2016 DAO hack, relies on a contract calling another that calls back before the first finishes, exploiting state that has not yet been updated. In eUTXO a transaction is a complete, atomic unit; a validator runs once per input to decide whether that UTXO may be spent, and there is no notion of a contract calling another mid-execution. There is no intermediate state for a reentrant call to exploit.
- **Double-spending is prevented at the protocol level.** The ledger removes a UTXO the instant it is consumed, so any second attempt to spend the same output is structurally invalid. This is stronger than the account model's reliance on nonce tracking.
- **Determinism eliminates MEV.** A Cardano transaction names its exact inputs and outputs; if those inputs still exist when it reaches the chain, it executes exactly as built, otherwise it fails with no effect. This removes the reordering, insertion, and front-running that constitute Maximal Extractable Value on chains whose outcomes depend on global state at execution time.
- **Native assets share the ledger's security.** Tokens on Cardano are handled by the ledger, not by a per-token contract. The minting policy controls creation, but once tokens exist there is no token contract to exploit, unlike the ERC-20 surface where every token contract is its own target.

These are real guarantees, but they are not the whole story. The remaining classes are where audits find bugs.

## The vulnerabilities that remain

### Double satisfaction

Double satisfaction occurs when one output satisfies the conditions of several validators in the same transaction, so an attacker discharges two obligations by paying once.

```text
Script A (DEX pool):  valid if an output contains 100 USDx
Script B (lending):   valid if an output contains 100 USDx

Attacker's transaction:
  Inputs:  DEX pool UTXO (A), lending pool UTXO (B)
  Outputs: ONE output with 100 USDx
  Both A and B see that output and consider themselves satisfied.
```

![Component diagram of a double-satisfaction attack where one output satisfies two validators]({{site.url_complet}}/assets/article/blockchain/cardano/double-satisfaction-attack-concept.png)

The defense is to require *your specific* output rather than that *some* output meets the condition, typically by tagging the intended output with a unique state or beacon token and validating that the tagged output exists. It is the on-chain analogue of an insecure direct object reference: the fix is confirming the resource you validate is actually yours.

### Datum hijacking and arbitrary datum

A continuing script UTXO carries its state in a datum. If the validator does not check the datum of its continuing output, an attacker can substitute a malicious one that changes a critical field such as ownership.

```text
Normal:  output datum {owner: Alice, amount: 80}   (Alice withdrew 20)
Attack:  output datum {owner: Attacker, amount: 100}   (owner changed)
```

The defense is datum-continuity validation: check that immutable fields such as ownership are unchanged, that mutable fields such as balances changed only per the allowed rules, and that the datum matches the expected schema. The related **arbitrary datum** issue is the mirror image at lock time: failing to constrain the datum when value is locked can produce a UTXO that can never be spent.

![Activity diagram of datum-continuity validation checking address, immutable fields, mutable transition rules, and value preservation]({{site.url_complet}}/assets/article/blockchain/cardano/datum-continuity-check-activity.png)

### Token forgery

A careless minting policy can let an attacker mint unauthorized tokens, whether through a missing authorization check, a supposedly one-time NFT policy that can actually run twice, or an unvalidated policy parameter. The correct **one-shot** pattern ties minting to consuming a specific UTXO, which can never exist again:

```text
Policy: minting allowed only if this specific UTXO is consumed as input
  Tx 1 (mint):    Inputs: [UTXO_Unique_123]   Mints: 1 MyNFT   (UTXO consumed)
  Tx 2 (re-mint): Inputs: [???]               Mints: 1 MyNFT   (fails, UTXO gone)
```

A closely related class is **other token name**: a policy that checks the minted quantity but not the exact asset name can be satisfied by minting a different name under the same policy ID. A policy should pin both the name and the amount.

### Missing UTXO authentication

Anyone can create a UTXO at a script address with any datum. A validator that trusts a UTXO's presence or contents without an authenticating token cannot distinguish a legitimate state UTXO from a fake one an attacker planted. The defense is the same beacon-token discipline: require a uniquely minted token in the UTXOs the protocol treats as authoritative.

### Time handling

Validators do not see a wall-clock timestamp; they see the transaction's validity interval, a slot range. Reasoning about the wrong bound (for example enforcing a deadline against the lower bound when the upper is what matters, or leaving a bound open) enables time manipulation. The defense is to enforce deadlines through the validity range, which the ledger checks at the protocol level, and to normalize the interval so both bounds are reasoned about explicitly.

### Resource exhaustion

Validators run under execution-unit (ExUnits) budgets, and a transaction bounded by size and resource limits. An attacker can craft inputs that push a validator toward those limits, creating denial-of-service conditions or, worse, a UTXO that can no longer be spent. This family includes **unbounded value** (a UTXO carrying so many assets it cannot be spent), **unbounded datum** (state that grows past resource limits), and **unbounded inputs** (logic requiring too many UTXOs at once). The defense is to bound worst-case cost: parameterize scripts, cap iteration, and precompute expensive work off-chain.

### Others worth knowing

| Vulnerability | Identifier | Essence |
|---|---|---|
| Insufficient staking control | `insufficient-staking-control` | Ignoring the staking part of an address enables reward redirection and franken-addresses. |
| Other redeemer | `other-redeemer` | Logic expecting a specific redeemer is bypassed by using a different one on the same script. |
| Missed input | `missed-input` | A redeemer index not bound to the spent input lets an unvalidated input slip past a global validator. |
| Certificate deregistration | `certificate-deregistration` | An unguarded staking-script certificate path lets anyone deregister the credential and halt a withdraw-zero protocol. |
| Locked value | `locked-value` | A validator with no satisfiable spending path locks funds permanently. |
| Signature domain separation | `signature-domain-separation` | Off-chain signatures without a domain separator or nonce can be replayed across protocols. |

## Defensive patterns

Experienced Cardano developers reach for the same handful of patterns:

- **State / beacon token**: require a uniquely minted NFT in every UTXO the protocol treats as authoritative. This prevents rogue UTXOs at a script address and is the standard cure for double satisfaction and missing authentication.
- **Value-preservation check**: verify explicitly that the total value in script outputs equals inputs minus authorized withdrawals plus authorized deposits. Never rely on implicit preservation.
- **Datum-continuity validation**: when a script UTXO is consumed and recreated, validate every field of the output datum against the transition rules, rather than assuming a present datum is correct.
- **Deadline enforcement**: use the transaction validity range for time conditions, since it is checked at the protocol level.
- **Minimal on-chain logic**: every line of on-chain code is attack surface. Keep validators small and focused, and move complex work off-chain, checking only the critical invariants on-chain.

## Verifying a contract before mainnet

Security is layered, from cheapest to strongest, and each layer catches what the previous cannot.

- **Unit tests** find the bugs you already thought of.
- **Property-based testing** generates thousands of random inputs against invariants such as "no transaction can extract more value than was deposited" or "only the owner can withdraw", surfacing edge cases you would not enumerate by hand.
- **Audits** by specialized firms, with line-by-line review, attack-surface analysis, and testnet penetration testing, are standard practice before mainnet for any contract holding real value.
- **Formal verification** proves a property holds for all inputs; Cardano's ledger specification is itself formalized in Agda, and the Haskell and Aiken toolchains are well-suited to these techniques.

## Conclusion

Cardano's eUTXO model removes a set of attack classes that dominate account-based security: reentrancy cannot occur because transactions are atomic, double-spends are prevented by the ledger, determinism removes MEV, and native assets avoid a per-token contract surface. Those guarantees are structural, not the product of careful coding.

The vulnerabilities that remain are specific to the model and are the developer's responsibility. Double satisfaction, datum hijacking, token forgery, missing UTXO authentication, time-bound handling, and resource exhaustion all reduce to the same discipline: validate the whole transaction against explicit invariants, and never trust that a UTXO, datum, or output is well-formed or authorized because it is present. The established patterns (beacon tokens, value preservation, datum continuity, deadline enforcement, minimal logic) encode that discipline, and layered verification from unit tests through property-based testing and audit confirms it before deployment. The mindmap below collects the removed classes, the remaining ones, the patterns, and the verification layers.

![Mindmap summarizing Cardano contract security: attack classes removed by the eUTXO model, vulnerabilities that remain, defensive patterns, and verification layers]({{site.url_complet}}/assets/article/blockchain/cardano/cardano-smart-contract-security.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **eUTXO (Extended UTXO)** | Cardano's ledger model, in which a validator guards a UTXO and approves or rejects a whole transaction; its structure removes several attack classes by design. |
| **Validator** | the on-chain pure function that runs once per script input and returns approval or rejection for spending that UTXO. |
| **Reentrancy** | an attack where a contract calls back into another before the first call finishes, exploiting stale state; impossible on Cardano because transactions are atomic. |
| **MEV (Maximal Extractable Value)** | value extracted by reordering, inserting, or censoring transactions; eliminated by eUTXO's deterministic outcomes. |
| **Double satisfaction** | a flaw where one output satisfies several validators in one transaction, letting an attacker discharge multiple obligations with a single payment. |
| **Datum hijacking** | substituting a malicious datum on a continuing script output to change a critical field such as ownership, when the validator fails to check datum continuity. |
| **Beacon (state) token** | a uniquely minted NFT placed in the UTXOs a protocol treats as authoritative, used to prevent rogue UTXOs and to defeat double satisfaction and missing authentication. |
| **One-shot minting policy** | a policy that ties minting to consuming a specific UTXO, guaranteeing the mint can occur exactly once because that UTXO can never exist again. |
| **Validity interval** | the slot range during which a transaction is valid; validators reason about time through this interval rather than a wall-clock timestamp. |
| **ExUnits (execution units)** | the CPU and memory budget a validator may consume, bounded per transaction; exceeding it is the basis of resource-exhaustion attacks. |

## Frequently Asked Questions

**Q: Which attack classes does the eUTXO model remove, and why are they gone rather than merely mitigated?**

Four: reentrancy, double-spending, MEV, and the per-token-contract attack surface. They are gone structurally rather than mitigated because the model's design leaves no place for them to occur. A transaction is atomic and a validator runs once per input with no ability to call another contract mid-execution, so there is no intermediate state a reentrant call could exploit. The ledger deletes a spent UTXO immediately, so a second spend of it is invalid by construction. Outcomes are deterministic because a transaction names its exact inputs, so there is nothing for a block producer to reorder profitably. And native assets are ledger entries rather than contracts, so there is no token contract to attack. None of these depend on the developer writing careful code.

**Q: What is double satisfaction, and what is the standard defense?**

Double satisfaction is a flaw in which a single output in a transaction satisfies the spending conditions of two or more validators at once, letting an attacker fulfill several obligations while paying only once. It arises when each validator checks that *some* output meets its condition rather than that *its own* output does. The standard defense is the beacon-token pattern: tag the specific output your protocol expects with a uniquely minted token and validate that this tagged output is present, so another validator's requirement cannot be satisfied by the same output.

**Q: Why must a minting policy check the asset name and not only the minted quantity?**

Because a policy ID can cover many asset names. A policy that only verifies the quantity minted can be satisfied by an attacker minting a different name under the same policy ID, the "other token name" class. If downstream logic assumes only the intended name exists under that policy, the attacker's tokens can be passed off as legitimate. A correct policy pins both the exact name and the amount, so nothing else can be minted under it.

**Q: How does a developer defend against resource-exhaustion attacks specific to eUTXO?**

By bounding worst-case cost, since validators run under execution-unit budgets and transactions under size limits. The concrete measures are to parameterize scripts so their work does not scale with attacker-controlled data, to cap any iteration over inputs or list elements, and to precompute expensive work off-chain so the validator only checks a result. This defends against the unbounded-value, unbounded-datum, and unbounded-inputs classes, where an attacker inflates a UTXO's assets, a datum's size, or the number of required inputs until the transaction cannot be built or the UTXO can no longer be spent.

**Q: A team relies on the eUTXO model's guarantees and writes thorough unit tests. Why is that still not enough security assurance for a contract holding real value?**

Because the model's guarantees and unit tests cover different, incomplete parts of the risk. The eUTXO model removes reentrancy, double-spends, and MEV, but it does nothing about double satisfaction, datum hijacking, token forgery, or missing authentication, which are exactly the bugs the model leaves to the developer. Unit tests, in turn, only confirm the behaviors the author thought to test; most eUTXO vulnerabilities are omissions, a check that was never written. Closing that gap needs property-based testing to probe invariants against random inputs, and a professional audit to look for the constraints that should exist and do not. Formal verification adds proof over all inputs for the most critical properties. Assurance for real value comes from these layers together, not from the model plus unit tests alone.

## References

- [Cardano developer portal](https://developers.cardano.org/)
- [Common Plutus Security Vulnerabilities (MLabs)](https://www.mlabs.city/blog/common-plutus-security-vulnerabilities)
- [Invariant0 security analysis](https://medium.com/@invariant0)
- [Mesh (code examples)](https://github.com/MeshJS/mesh)
- [Claude Code](https://claude.com/product/claude-code)
