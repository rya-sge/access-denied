---
layout: post
title: "A Test That Could Never Pass — An Aztec End-to-End Failure Three Layers from Its Cause"
date:   2026-09-23
lang: en
locale: en-GB
categories: blockchain ethereum ZKP
tags: aztec testing debugging noir privacy smart-contracts
description: "An Aztec test failed on a tagging-secret assertion. The cause was a Jest timeout smaller than the sleep it guarded, and two unrelated changes that made it fatal."
image: /assets/article/blockchain/aztec/2026-09-23-aztec-e2e-three-layers-mindmap.png
isMath: false
---

[Aztec](https://aztec.network/) is a privacy-focused Layer 2 on Ethereum. A contract there has a private half, proved on the user's own device over encrypted *notes*, and a public half executed by a sequencer; because the private half runs against a historical snapshot, public state it needs to read has to be published in a form whose value cannot change for a known window. [An earlier article]({{site.url_complet}}/2026/09/14/aztec-delayed-public-mutable-pause-privacy-delay/) covers that mechanism and the delay it costs.

This one is a debugging narrative. An end-to-end suite that had been green for weeks started failing with an assertion that named none of the things that were wrong:

```
Simulation error: Assertion failed: Cannot resolve a constrained tagging secret for an invalid recipient
  at resolve_tagging_strategy.nr:23:9
  at messages/delivery/tag.nr:52:37
```

Nothing in that message mentions a timeout, a dependency version, or a configuration constant, and all three were involved. The interesting part is not the fix, which is four lines, but the distance between the symptom and the cause, and the fact that two of the three contributing changes were individually correct.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The setting

The system under test is a privacy-preserving security token: balances are private notes, while supply, roles, the pause flag and the compliance flags are public. An issuer receives a copy of every movement so it can audit activity without asking any holder.

Three facts about it matter here, and each arrived as a separate, deliberate change:

- **The issuer's address is a `DelayedPublicMutable`.** Every mint, transfer and burn reads it in private, and a value written to such a variable becomes current only after a configured delay. The constructor *schedules* it rather than writing it.
- **The delay was raised from 360 seconds to one hour.** The old value was an order of magnitude below the framework's own recommendation, and it left a six-minute window in which a transaction had to be proved and included.
- **The issuer's record of a mint became a constrained delivery.** Previously the issuer received only an offchain copy of each note, which a standard client cannot process at all; the fix was to also emit a `Transfer` event delivered with cryptographic guarantees.

Each change was reviewed on its own terms. None of them was reviewed against the test suite's constants.

## The symptom, and what the assertion means

The failing assertion lives in the framework, not in the contract. Its source is short enough to quote in full:

```rust
pub(crate) unconstrained fn resolve_tagging_strategy(
    sender: AztecAddress,
    recipient: AztecAddress,
    mode: OnchainDeliveryMode,
) -> ResolvedTaggingStrategy {
    if recipient.is_valid() {
        resolve_tagging_strategy_oracle(sender, recipient, mode)
    } else if mode == OnchainDeliveryMode::onchain_constrained() {
        panic("Cannot resolve a constrained tagging secret for an invalid recipient")
    } else {
        ResolvedTaggingStrategy::unconstrained_secret(random())
    }
}
```

Two things follow from those nine lines.

**"Invalid" is a statement about geometry, not about registration.** An Aztec address is the x-coordinate of a point on the Grumpkin curve, and `is_valid()` is `self.get_y().is_some()`: does `y² = x³ − 17` have a solution at this x? Roughly half of all field elements do not sit on the curve, so an arbitrary 254-bit number is invalid about half the time. A real account address is always valid, because it is derived as the x-coordinate of an actual point.

**The delivery mode decides whether an invalid recipient is fatal.** Unconstrained delivery is best-effort: it returns a random secret, producing a tag nobody can find, rather than aborting the sender's transaction. Constrained delivery has no such option, because it must not silently emit an undiscoverable tag while claiming a guarantee. So it fails.

The question therefore became: which recipient in a mint is not on the curve? The mint delivers three messages, and only one of them is both constrained and addressed to something other than the recipient of the tokens: the issuer's `Transfer` event.

## Layer one: the run never started

Before any of that could be established, the suite had to run at all, and it did not. Every test failed at contract deployment:

```
RangeError: Maximum call stack size exceeded
  at NestedProcessReturnValues.get schema (@aztec/stdlib/.../public_simulation_output.js)
  at isRecursive (zod/v4/core/memoizer.js:84:29)
  at check      (zod/v4/core/memoizer.js:26:39)   ← repeating to the stack limit
```

[zod](https://zod.dev/) is a schema-validation library. Nothing in the project imports it; it arrives transitively, because five framework packages depend on it and each declares the range `^4`. It validates everything crossing the JSON-RPC boundary between a client and a node.

The schema at the top of that stack is self-referential, and legitimately so:

```js
static get schema() {
    return z.object({
        values: NullishToUndefined(z.array(schemas.Fr)),
        nested: z.array(z.lazy(() => NestedProcessReturnValues.schema)),
    })...
}
```

A public simulation result contains nested results of its own type, because a public call can enqueue further public calls. The library's recursion check walked that cycle instead of detecting it.

The dates settle who broke what:

| | |
|---|---|
| The framework version in use was published | 2026-08-17 |
| Newest zod in existence at that moment | 4.4.3, released 2026-05-04 |
| zod 4.5.0 released | 2026-08-28, eleven days later |
| What the package manager had installed | 4.5.4 |

The framework was never built against the code that breaks. A caret range on a transitive dependency is a dependency the project never chose, and pinning it to 4.4.3 restored the run:

```json
"resolutions": {
  "zod": "4.4.3"
}
```

`resolutions` rather than a dependency entry, because the copy that needs pinning is the one the framework packages resolve, not one the project imports.

## Layer two: a timeout smaller than the sleep it guards

With the run unblocked, a different failure appeared. The deployment test timed out, and every later test failed on the tagging-secret assertion.

Two constants, forty lines apart in the same file:

```ts
const CHANGE_ROLES_DELAY_SECONDS = 3600;
const DELAY_MS = (CHANGE_ROLES_DELAY_SECONDS + 12) * 1000;   // 3,612,000 ms

const LONG_TEST_TIMEOUT = 900_000;                            //   900,000 ms
```

The deployment test performs `await sleep(DELAY_MS)` and runs under `LONG_TEST_TIMEOUT`. A test that sleeps for 3,612 seconds under a 900-second timeout cannot pass, in any circumstances, on any machine.

It was not always wrong. When the delay was 360 seconds, `DELAY_MS` was 372,000 and the 900,000 timeout had more than double the margin it needed. Raising the delay to one hour multiplied one constant by ten and left the other alone. The two had been consistent by coincidence rather than by construction, and nothing connected them.

The fix is to derive one from the other, so the relationship is stated rather than maintained:

```ts
const LONG_TEST_TIMEOUT = DELAY_MS + 600_000;
```

## Layer three: why the failure was loud

Here the three changes meet. The deployment test was killed at 900 seconds, in the middle of a sleep that existed precisely so that the scheduled issuer address would become current. It never did. Every subsequent mint read `issuer_address` and got the type's default: the zero address.

Is zero a valid Aztec address? It is the x-coordinate 0, and `y² = −17` has no solution in this field, so no. It is exactly the kind of value the framework's `is_valid()` rejects.

So the chain is:

1. the deployment test dies before the delay elapses;
2. `issuer_address` is still the default zero;
3. a mint emits a `Transfer` event to the issuer with `onchain_constrained` delivery;
4. constrained delivery resolves a tagging secret for the recipient;
5. the recipient is not a curve point, and constrained mode has no fallback, so it panics.

What makes this worth writing down is step 3. Before the auditability change, the issuer received only an *offchain* copy of each note. Offchain delivery is unconstrained, so the same zero address took the `else` branch: a random secret, an undiscoverable tag, and a mint that succeeded while delivering the issuer's copy to nobody.

The change that introduced constrained delivery did not create the bug. It converted a silent, wrong success into a loud, correct failure, and it did so in a code path nobody expected to be exercised, because nobody expected a mint during the first hour after deployment.

## What generalises

Four points survive the specifics.

- **A delayed value has a dead window after deployment, and the contract is partly unusable inside it.** If a constructor schedules rather than writes, everything reading that value sees the default until the delay elapses. That is a documented property of the mechanism; what is easy to miss is that it makes some entry points fail outright rather than merely read a stale value.
- **Two constants in a fixed relationship should be written as that relationship.** `LONG_TEST_TIMEOUT = 900_000` was correct for one value of a delay it did not mention. Deriving it costs nothing and removes an invariant from the list of things a human has to remember.
- **A best-effort path hides the bug that a guaranteed path reports.** Unconstrained delivery's fallback is a reasonable design: a malformed recipient should not abort an otherwise valid transaction. The cost is that a wrong address produces no error until something upgrades that delivery to a guaranteed one.
- **An unpinned transitive dependency is an unowned decision.** Nothing in the project changed between the run that worked and the run that did not; a library eleven days younger than the framework did.

The last one also explains why the failure surfaced now rather than in the change that caused it. The suite had not been run since the delay was raised, because it takes over an hour of wall-clock time, most of it a single `sleep`. A test that is expensive enough to skip is a test that stops reporting.

## Conclusion

The visible error named a cryptographic mechanism: a tagging secret that could not be resolved for a recipient the framework refused to encrypt to. That mechanism worked exactly as designed at every step. The defect was a test-harness constant that had been correct under a previous configuration, exposed by a delay change, and made fatal by an unrelated auditability change that removed a silent fallback.

- **The dependency failure was independent** and merely first: an unpinned transitive library, eleven days newer than the framework it serves, broke deployment before any contract logic ran.
- **The timeout was the defect**, and the only one of the three that was ever wrong.
- **The delay change and the auditability change were both correct**, and both are what turned a latent inconsistency into a hard failure.

![Mindmap of an Aztec end-to-end debugging case, covering the tagging-secret symptom, the zod dependency pin, the timeout smaller than its sleep, the delayed issuer address, and the four lessons that generalise]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-23-aztec-e2e-three-layers-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Note** | An encrypted record holding private state, readable only by its owner, which a contract creates and later nullifies rather than updating. |
| **Tagging secret** | A value shared between sender and recipient from which the tag indexing an encrypted log is derived, so the recipient can find messages meant for it. |
| **Constrained delivery** | A delivery mode whose encryption is proved, guaranteeing the recipient can decrypt the message; the most expensive mode and the only one that cannot silently fail. |
| **Unconstrained delivery** | A delivery mode that trusts the sender to encrypt correctly and falls back to an undiscoverable tag rather than aborting when the recipient is unusable. |
| **`DelayedPublicMutable`** | A public state variable whose writes take effect only after a configured delay, which is what makes it readable from a private function. |
| **Grumpkin** | The elliptic curve Aztec addresses and keys live on, chosen because its arithmetic is native inside the proof system's field. |
| **Valid address** | An address whose value is the x-coordinate of a real point on Grumpkin; roughly half of all field elements are not, and no shared secret can be derived for those. |
| **Anchor block** | The historical block a private execution is proved against, and the point from which a transaction's expiry is measured. |
| **Transitive dependency** | A library a project does not import but receives through one of its dependencies, and whose version the project therefore does not choose unless it pins it. |
| **`resolutions`** | A package-manager field that forces a version of a package anywhere in the dependency tree, including copies the project never imports directly. |

### Integration Notes

| Behaviour | What an integrator should do |
|---|---|
| A constructor that *schedules* a delayed value leaves it at the type default until the delay elapses. | Treat the first delay after deployment as a window in which value-moving entry points are unavailable, and sequence deployment scripts accordingly. |
| Constrained delivery to an address that is not a curve point aborts the transaction. | Validate any configurable recipient address before it can reach a constrained delivery, rather than relying on the send to succeed. |
| Unconstrained and offchain delivery to the same invalid address succeed silently. | Do not infer from a successful send that a recipient received anything; a delivery guarantee exists only in constrained mode. |
| A test that waits out a real delay cannot be given a fixed timeout. | Derive the timeout from the delay constant, and re-check it whenever the protocol-level delay changes. |
| Framework packages declare caret ranges on their own dependencies. | Pin the transitive versions that the framework release was built against, and re-check the pins when upgrading the framework. |

## Frequently Asked Questions

**Q: Why does an invalid recipient abort a constrained delivery but not an unconstrained one?**

Because the two modes promise different things. Constrained delivery proves the encryption, so the recipient is guaranteed to be able to decrypt the message. That guarantee cannot be met for an address with no curve point behind it, and emitting a tag nobody can compute while claiming the guarantee would be worse than failing.

Unconstrained delivery promises nothing about the recipient's ability to read the message. Falling back to a random secret costs the sender nothing and avoids letting a malformed recipient abort an otherwise valid transaction.

**Q: What makes an Aztec address "invalid" if it is just a number?**

An address is the x-coordinate of a point on the Grumpkin curve. Recovering the point means solving `y² = x³ − 17` for that x, which has a solution for roughly half of all field elements. An address derived from real account keys is always valid, because it was computed as the x-coordinate of a point that exists. An arbitrary number, including zero, usually is not.

**Q: Was the change that introduced constrained delivery to the issuer a mistake?**

No, and it is the reason the problem was found. Before it, the issuer's copy of a mint went out unconstrained to the same zero address and hit the best-effort fallback, so the mint succeeded while the issuer received nothing it could process. The change replaced a silent wrong result with a visible error.

**Q: Why did raising a delay from 360 seconds to one hour break a test that does not mention either number?**

The test slept for the delay plus a small margin, under a hard-coded timeout of 900 seconds. At 360 seconds the sleep was 372 seconds and fitted comfortably. At 3,600 seconds it did not, and no machine or configuration could make it fit. The two constants had a required relationship that was never written down, so changing one of them silently invalidated the other.

**Q: How could an unpinned dependency break a project whose own code did not change?**

Five framework packages declare their dependency on the validation library as `^4`, which permits any 4.x release. A resolution taken after a newer 4.x appeared installed a version published eleven days after the framework, containing a recursion check that overflows on a self-referential schema the framework uses. Nothing in the project changed; what changed was what `^4` meant on the day the dependencies were resolved.

**Q: Would running the test suite more often have caught this earlier?**

Yes, and that is the practical lesson. The suite waits out a real delay, so a full run takes over an hour, most of it a single sleep. It was therefore skipped after the delay change, and a test that is expensive enough to skip stops reporting. The structural answer is to keep the fast suite in continuous integration and to run the slow one on a schedule rather than on demand.

## References

### Analyzed source

- [AztecProtocol/aztec-nr](https://github.com/AztecProtocol/aztec-nr) — framework sources read at tag [`v5.2.0`](https://github.com/AztecProtocol/aztec-nr/tree/v5.2.0), 2026-09-23. The assertion is in `aztec/src/oracle/resolve_tagging_strategy.nr`; the address validity check is in the protocol-circuit types, `address/aztec_address.nr`.

### Documentation and libraries

- [Aztec developer documentation](https://docs.aztec.network/) — note delivery, delayed public mutable state and the tagging-based discovery scheme.
- [zod](https://zod.dev/) — the schema-validation library, and its version history on [npm](https://www.npmjs.com/package/zod?activeTab=versions).

### Related articles

- [Reading Public State from a Private Function on Aztec — Why a Pause Flag Comes with a Delay]({{site.url_complet}}/2026/09/14/aztec-delayed-public-mutable-pause-privacy-delay/)
- [Ephemeral Keys on Aztec — Encrypting to an Address, the Curve Behind It, and What a Quantum Computer Would Break]({{site.url_complet}}/2026/09/17/aztec-ephemeral-keys-ecdh-encryption-post-quantum/)
- [Randomness on Aztec — One Oracle, Four Uses, and Why the Circuit Never Checks It]({{site.url_complet}}/2026/09/17/aztec-randomness-notes-oracle-unconstrained/)
- [Building a Wallet for Aztec — What a MetaMask for a Private Chain Has to Contain]({{site.url_complet}}/2026/09/17/building-an-aztec-wallet-pxe-proving-accounts/)
- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
