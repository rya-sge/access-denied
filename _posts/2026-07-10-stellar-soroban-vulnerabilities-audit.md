---
layout: post
title: "Three Vulnerabilities from the OpenZeppelin Stellar Contracts Audits"
date:   2026-07-10
lang: en
locale: en-GB
categories: blockchain security
tags: stellar soroban smart-contracts audit rust security vulnerability
description: A technical walkthrough of three real, resolved findings from the OpenZeppelin Stellar Contracts audits — silent supply inflation via self-recovery, signer aliasing through non-canonical keys, and a ledger-arithmetic TTL underflow — each with the vulnerable code, a flow diagram, and the fix.
image: /assets/article/blockchain/stellar/stellar-soroban-vulnerabilities-audit.png
isMath: false
---

The OpenZeppelin Stellar Contracts library ships its [audit reports](https://github.com/OpenZeppelin/stellar-contracts/tree/main/audits) in the repository. Seven differential audits between February 2025 and April 2026 recorded 143 findings: 4 Critical, 12 High, 35 Medium, 55 Low, and 37 notes. Reading them is one of the better ways to learn how Soroban contracts actually break, because each finding names a broken invariant and the reviewers proposed a concrete fix that later landed in the code.

This article works through three of them. They were chosen for diversity rather than severity alone: one breaks a supply invariant, one breaks a cryptographic identity assumption, and one is pure ledger arithmetic. They live in three different packages (real-world-asset tokens, smart accounts, and non-fungible tokens), and each has a fix that is instructive in its own right. Every code path below was checked against the library at commit `1e51389`.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Reading a Soroban audit

Three properties of the Soroban execution model recur across all three findings, so they are worth stating up front.

**Token amounts are `i128`; ledger sequences are `u32`.** Balances, allowances and supply use a signed 128-bit integer. The ledger sequence number, and any TTL derived from it, are unsigned 32-bit. Mixing the two, or subtracting on the `u32` side without a guard, is a recurring source of bugs.

**Storage has three tiers, each with a Time-To-Live.** `instance` holds contract-wide singletons, `persistent` holds long-lived per-key data such as balances, and `temporary` holds time-bounded data such as allowances and pending transfers. Every entry carries a TTL and is archived (persistent) or deleted (temporary) when it expires. `extend_ttl` can only ever *raise* a TTL, never lower it.

**Smart accounts delegate signature checking to verifier contracts.** A Soroban smart account composes signers, context rules, and pluggable policies. A signer is modelled as a `(verifier_contract, key_bytes)` pair, and cryptographic verification is offloaded to the verifier. The framework's security therefore depends on those verifiers being strict about what they accept.

The audits are **differential**: reviewers diff a new HEAD commit against a previously-audited base and focus on what changed. That is why the same class of bug can reappear across versions, and why a fix that changes a data model warrants its own re-review.

## Vulnerability 1 — Silent supply inflation through self-recovery

**Finding: v0.5.0 C-01 (Critical), `packages/tokens/src/rwa`.**

Real-world-asset tokens support account recovery. If an investor loses control of a wallet, an operator can force-transfer that wallet's balance to a replacement wallet after identity checks. The function was `recovery_address(lost_wallet, new_wallet)`.

### The bug

The vulnerable implementation read the source balance, computed the destination balance as source-plus-lost, and then wrote both balances directly to storage rather than routing through the canonical `Base::update` path. That is safe when the two wallets differ. It is not safe when they are the same address.

With `lost_wallet == new_wallet == A` and `b = Base::balance(A)`:

1. Read `lost_balance = b`.
2. Compute `new_balance = Base::balance(A) + lost_balance = b + b = 2b`.
3. Write `Balance(A) = 0`, then write `Balance(A) = 2b` (the **same key**), so the final value is `2b`.

No supply variable is touched, because the function never calls `Base::update`, where total-supply accounting lives. The sum of balances grows by `b` while `total_supply` stays constant, so the fundamental invariant "sum of balances equals total supply" is broken silently.

The function had no `require_auth()` and checked only `verify_identity(new_wallet)`, which `A` already satisfies. So any caller controlling an eligible address with a non-zero balance could call `(A, A)` repeatedly and double the balance each time: `b → 2b → 4b → 8b`, up to the `i128` limit. It also emitted `transfer(A, A, b)`, which confuses indexers while the real problem, silent inflation, goes unlogged.

![Flow of the self-recovery inflation bug, showing the read-read-write on one key doubling the balance while total_supply is untouched]({{site.url_complet}}/assets/article/blockchain/stellar/recovery-inflation-flow.png)

### Why the canonical path matters

The root cause is not the missing `from == to` guard by itself; it is that the function reimplemented balance movement instead of delegating to `Base::update`. Look at what `update` does for a self-transfer:

```rust
pub fn update(e: &Env, from: Option<&Address>, to: Option<&Address>, amount: i128) {
    // ...
    if let Some(account) = from {
        let mut from_balance = Base::balance(e, account);      // reads b
        // ...
        from_balance -= amount;                                // b - amount
        e.storage().persistent()
            .set(&FungibleStorageKey::Balance(account.clone()), &from_balance);  // writes b - amount
    }
    if let Some(account) = to {
        let to_balance = Base::balance(e, account) + amount;   // reads b - amount, adds amount
        e.storage().persistent()
            .set(&FungibleStorageKey::Balance(account.clone()), &to_balance);    // writes b
    }
}
```

When `from == to`, the destination read happens **after** the source write, so it reads `b - amount` and adds `amount` back, netting to `b`. Routing through `update` makes a self-transfer a no-op automatically, and it keeps `total_supply` correct because minting and burning are the only branches that touch it. The vulnerable code lost both properties by doing its own read-read-write.

### The fix

The remediation (PR #432) rewrote recovery to route through `forced_transfer`, which calls `Base::update`, and added the identity-continuity check that a sibling finding (C-02) required. The current `recover_balance` fetches the recovery target from the identity verifier, refuses to proceed unless it matches, and only then moves funds through the canonical path:

```rust
pub fn recover_balance(e: &Env, old_account: &Address, new_account: &Address) -> bool {
    let identity_verifier_client = IdentityVerifierClient::new(e, &Self::identity_verifier(e));
    identity_verifier_client.verify_identity(new_account);

    // C-02 fix: source and destination must resolve to the same identity
    let recovery_target = identity_verifier_client
        .recovery_target(old_account)
        .unwrap_or_else(|| panic_with_error!(e, RWAError::IdentityMismatch));
    if recovery_target != *new_account {
        panic_with_error!(e, RWAError::IdentityMismatch);
    }

    let lost_balance = Base::balance(e, old_account);
    if lost_balance == 0 {
        return false;
    }
    // ... snapshot frozen state ...
    Self::forced_transfer(e, old_account, new_account, lost_balance); // -> Base::update
    // ... reapply frozen state on the destination ...
    true
}
```

The general rule: route every balance change through the canonical `update` function so that supply accounting, hooks, and self-transfer semantics come for free. A privileged move that reimplements storage writes is exactly where invariants get lost.

## Vulnerability 2 — Signer aliasing through non-canonical key bytes

**Finding: v0.5.0 C-03 (Critical), `packages/accounts/src/verifiers`.**

Recall the smart-account model: a signer is a `(verifier_contract, key_bytes)` pair, and the framework treats that whole pair as the signer's identity. A rule can require *M of N* distinct signers, or assign weights to signers and require a total weight. The security of both mechanisms rests on distinct pairs being distinct keys.

### The bug

The Ed25519 and WebAuthn verifiers accepted `key_data` that was **at least** the required length and then silently truncated it to the first 32 bytes (Ed25519) or 65 bytes (uncompressed P-256 / WebAuthn). The verifier only used the truncated prefix, but the smart-account layer keyed the signer's identity on the full, untruncated byte string.

That gap is the whole bug. A malicious user registers several "different" signers that share one real public key `K` and differ only in trailing junk:

- `(ed25519_verifier, K)`
- `(ed25519_verifier, K || 0x00)`
- `(ed25519_verifier, K || 0xDEAD)`

To the account these are three distinct signers. To the verifier they are all `K`, because it truncates the junk away before checking. So a single signature produced by `K` authenticates as all three at once.

![One real key expanded into three distinct signer identities that all truncate back to the same key at verification time]({{site.url_complet}}/assets/article/blockchain/stellar/signer-aliasing-concept.png)

### The impact

A multisig is only as strong as the number of *independent* keys behind it. Aliasing collapses that number. An attacker holding one key can appear to satisfy a 3-of-5 threshold, or accumulate weight in a weighted policy, with no additional keys. The audit rated the practical impact as severe: fake signers that look like authorization diversity while there is really only one key behind them, undermining exactly the guarantee a smart account exists to provide.

### The fix

The remediation (PR #384) enforces canonical key material by construction. The verifier no longer accepts a variable-length `Bytes`; it takes a fixed-size type, so a non-canonical length cannot be represented at all:

```rust
pub fn verify(
    e: &Env,
    signature_payload: &Bytes,
    public_key: &BytesN<32>,   // fixed 32-byte type, not variable-length Bytes
    signature: &BytesN<64>,
) -> bool {
    e.crypto().ed25519_verify(public_key, signature_payload, signature);
    true
}
```

The library documents the reasoning directly: "The `BytesN<32>` type constraint already enforces the correct length at deserialization." Trailing junk is no longer a value the function can be handed. This is the strongest form of the fix, moving the check from a runtime comparison the reviewers had to remember into the type system, where the compiler and deserializer enforce it. When a value must be exactly *N* bytes, prefer `BytesN<N>` over a length check on `Bytes`.

## Vulnerability 3 — Ledger-arithmetic underflow on approval revocation

**Finding: v0.2.0 H-01 (High), `packages/tokens/src/non_fungible`.**

Non-fungible tokens let an owner approve an operator to manage all of their tokens, through `approve_for_all`. The approval carries a `live_until_ledger`: the ledger sequence at which it expires. By convention, passing `live_until_ledger = 0` means "revoke now."

### The bug

To revoke, the vulnerable code removed the operator from the approved set and then extended the TTL of the storage entry. The extension amount was computed as:

```rust
let live_for = live_until_ledger - e.ledger().sequence();
```

Both operands are `u32`. On the revoke path `live_until_ledger` is `0`, so the subtraction is `0 - sequence`, which **underflows** to a value near `u32::MAX` (roughly `4.29 × 10⁹`). The code then asks the host to extend the entry's TTL by that enormous amount. The host rejects any extension beyond its maximum and panics, so the whole transaction reverts. Revocation is impossible: the one operation an owner most needs to succeed, removing a compromised operator, is the one that always fails.

![Sequence of the approve_for_all revoke path, where a u32 underflow feeds a near-maximal TTL into the host and triggers a panic]({{site.url_complet}}/assets/article/blockchain/stellar/approve-underflow-sequence.png)

### The test that hid it

The audit flagged something subtle alongside the bug. A test named `revoke_approve_for_all_works` existed and **passed**. It passed because Soroban's test environment initializes the ledger sequence to `0` by default. With `sequence = 0`, the subtraction is `0 - 0 = 0`, no underflow occurs, and the revoke path looks healthy. The bug only manifests once `sequence > live_until_ledger`, which is every real ledger.

This is a general hazard for any code doing ledger arithmetic. `Env::default()` starts at sequence 0, so TTL and expiry logic must be tested at a realistic non-zero sequence or the tests are theatre:

```rust
let e = Env::default();
e.ledger().set_sequence_number(100_000); // before any TTL assertion
```

### The fix

The remediation (PR #170) special-cases the revoke path so the subtraction never runs when there is nothing to extend. The current code removes the entry and returns early:

```rust
// If revoking approval (live_until_ledger == 0)
if live_until_ledger == 0 {
    e.storage().temporary().remove(&key);
    emit_approve_for_all(e, owner, operator, live_until_ledger);
    return;
}

let current_ledger = e.ledger().sequence();

if live_until_ledger > e.ledger().max_live_until_ledger()
    || live_until_ledger < current_ledger
{
    panic_with_error!(e, NonFungibleTokenError::InvalidLiveUntilLedger);
}

// NOTE: cannot underflow because of the checks above
let live_for = live_until_ledger - current_ledger;
e.storage().temporary().extend_ttl(&key, live_for, live_for);
```

Two guards now stand in front of every subtraction: the early return for the `== 0` revoke case, and the `live_until_ledger < current_ledger` check for a stale expiry. The `max_live_until_ledger()` bound also rejects an over-large value before it can panic the host. The rule generalizes to any `ledger_target - ledger_now` expression: guard the `== 0` and `target < now` cases before subtracting on the `u32` side.

## Cross-cutting lessons

The three findings sit in different packages and different vulnerability classes, but the remediations rhyme.

- **Route state changes through the canonical path.** Vulnerability 1 existed because recovery reimplemented balance movement instead of calling `Base::update`. A single well-tested mutation function that owns the invariants is safer than several call sites that each re-derive them.
- **Make invalid states unrepresentable.** Vulnerability 2's fix replaced a length check that reviewers had to remember with a `BytesN<32>` type the deserializer enforces. When the type system can carry an invariant, it should.
- **Guard arithmetic at the boundary.** Vulnerability 3 was a `u32` subtraction with no guard on its zero and underflow cases. Ledger arithmetic is unsigned and unforgiving; the guard belongs immediately before the operation.
- **Test at realistic values.** The default test ledger sequence of `0` masked a High-severity underflow behind a passing test. Boundary-value coverage is not optional for TTL and ledger logic.

A closing observation from the corpus as a whole: the v0.5.0 re-audit found that the fixes for two mapping and counter bugs introduced *new* invariant violations of their own. A fix that changes a data model, replacing a flag with a list, or a monotonic counter with a live count, deserves the same scrutiny as new code, because it can introduce fresh invariants that the original review never considered.

## Conclusion

The three findings are a supply-invariant break, a cryptographic-identity break, and a ledger-arithmetic break. Each was Critical or High, each was resolved, and each fix illustrates a distinct discipline: delegate to a canonical mutation path, encode invariants in types, and guard unsigned arithmetic. None of the three depended on exotic conditions. The self-recovery inflation needed only a caller passing the same address twice; the signer aliasing needed only trailing bytes on a key; the TTL underflow fired on every real ledger and was hidden only by a test running at sequence zero.

Reading these reports against the fixed source is a practical way to build a mental model of how Soroban contracts fail. The full set of findings, indexed by class, is available in the repository's `audits/` directory.

![Mindmap summarising the three Soroban vulnerabilities, their mechanics, and the cross-cutting lessons]({{site.url_complet}}/assets/article/blockchain/stellar/stellar-soroban-vulnerabilities-audit.png)

## Frequently Asked Questions

**Q: Why did the self-recovery bug inflate the balance instead of leaving it unchanged?**

Because the function performed a read-read-write on a single storage key. It read the balance `b`, computed the new destination balance as `b + b = 2b`, then wrote `0` and then `2b` to the same `Balance(A)` key, so the last write won and the account ended with `2b`. The extra `b` was created out of nothing, and because the function never called `Base::update`, the `total_supply` counter was never adjusted to match. Routing the same operation through `Base::update` would have made it a no-op, because `update` reads the destination balance *after* writing the source, so a self-transfer nets to the original value.

**Q: What makes `BytesN<32>` a stronger fix than checking the length of a `Bytes` value?**

A length check is a runtime guard that a reviewer must remember to write and keep in place on every path that accepts a key. `BytesN<32>` is a fixed-size type: a value of the wrong length cannot be constructed or deserialized into it at all, so the invariant is enforced by the deserializer and the compiler rather than by hand-written validation. The bug in the original verifiers was precisely that they accepted a longer `Bytes` and truncated it; once the parameter type is `BytesN<32>`, the trailing junk that produced the aliases is not a representable input.

**Q: Why did the `approve_for_all` underflow escape the test suite?**

The test `revoke_approve_for_all_works` ran in `Env::default()`, whose ledger sequence starts at `0`. The buggy expression was `live_until_ledger - e.ledger().sequence()`, and on the revoke path `live_until_ledger` is also `0`, so the subtraction evaluated to `0 - 0 = 0` with no underflow. The bug only appears when the sequence exceeds `live_until_ledger`, which is true on every real ledger but not in a test left at sequence zero. Setting a realistic sequence with `e.ledger().set_sequence_number(...)` before the assertion would have exposed it.

**Q: All three bugs were fixed. Why is reading the reports still useful?**

The value is in the *class* of bug, not the individual instance. The library will keep adding features, and the same patterns recur: a new privileged function that reimplements a mutation instead of delegating, a new input treated as an identity without canonicalization, a new TTL computation on unsigned ledger values. A reviewer who has internalized these three will look for the canonical-path bypass, the non-canonical-identity gap, and the unguarded subtraction in code that has not been audited yet. The reports are a training set for that pattern recognition.

**Q: Combine two of the findings. How do the self-recovery inflation and the TTL underflow each illustrate the same underlying reviewing failure, despite being different bug classes?**

Both slipped through because a critical case was never exercised with the values that trigger it. The self-recovery inflation required `lost_wallet == new_wallet`, an input the original tests presumably never passed because it looks nonsensical, yet it is trivially reachable by an attacker. The TTL underflow required a non-zero ledger sequence, which the tests never set. In both cases the code path "worked" under the conditions it was tested against and failed under the conditions it would actually meet. The shared lesson is adversarial boundary testing: self-referential inputs (`from == to`), zero and maximal values, and realistic environment state are exactly where invariants tend to break, so they are exactly what the tests must cover.

**Q: What is a differential audit, and why does it matter that these were differential?**

A differential audit reviews the changes between a new commit and a previously-audited baseline, rather than re-reviewing the whole codebase from scratch. It concentrates effort on what is new or modified, which is efficient, but it also means a bug can be reintroduced or a fix can create a fresh problem in a later diff. The OpenZeppelin Stellar audits are differential, and the v0.5.0 re-audit demonstrated the risk directly: the fixes for two earlier findings introduced new invariant bugs of their own. It is why a remediation that changes a data structure should be treated as new code needing its own review, not as a settled matter.

## References

### Audit reports and repository

- [OpenZeppelin Stellar Contracts (repository)](https://github.com/OpenZeppelin/stellar-contracts)
- [Audit reports (`audits/` directory)](https://github.com/OpenZeppelin/stellar-contracts/tree/main/audits)
- [`packages/tokens/src/rwa`](https://github.com/OpenZeppelin/stellar-contracts/tree/main/packages/tokens/src/rwa) — recovery (Vulnerability 1)
- [`packages/accounts/src/verifiers`](https://github.com/OpenZeppelin/stellar-contracts/tree/main/packages/accounts/src/verifiers) — signer verifiers (Vulnerability 2)
- [`packages/tokens/src/non_fungible`](https://github.com/OpenZeppelin/stellar-contracts/tree/main/packages/tokens/src/non_fungible) — `approve_for_all` (Vulnerability 3)

### Soroban and Stellar references

- [Soroban storage and state archival](https://developers.stellar.org/docs/learn/fundamentals/contract-development/storage/state-archival)
- [SEP-41 Token Interface](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0041.md)
- [Soroban authorization model](https://developers.stellar.org/docs/learn/fundamentals/contract-development/authorization)

### Related reading

- [Soroban State Archival — Storage Semantics and Security Implications]({{site.url_complet}}/2026/04/15/soroban-state-archival/)
- [Deploying a SEP-41 Fungible Token on Stellar with OpenZeppelin]({{site.url_complet}}/2026/07/09/stellar-fungible-token-openzeppelin-sep41/)
- [Claude Code](https://claude.com/product/claude-code)
