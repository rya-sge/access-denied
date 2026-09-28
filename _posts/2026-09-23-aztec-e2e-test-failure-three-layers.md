---
layout: post
title: "A Test That Could Never Pass — An Aztec Failure, the Explanation That Fitted, and the One That Was True"
date:   2026-09-23
lang: en
locale: en-GB
categories: blockchain ethereum ZKP aztec
tags: aztec testing debugging noir privacy smart-contracts
description: "An Aztec test failed on a tagging-secret assertion. The obvious explanation fitted every symptom and was wrong: the chain had never advanced at all."
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

Nothing in that message mentions a timeout, a dependency version, or a chain that stopped producing blocks, and all three were involved. The interesting part is not the fix, which is a few lines, but that the first explanation fitted every symptom, made a failing test pass when it was applied, and was still not the cause.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The setting

The system under test is a privacy-preserving security token: balances are private notes, while supply, roles, the pause flag and the compliance flags are public. An issuer receives a copy of every movement so it can audit activity without asking any holder.

Three facts about it matter here, and each arrived as a separate, deliberate change:

- **The issuer's address is a `DelayedPublicMutable`.** Every mint, transfer and burn reads it in private, and a value written to such a variable becomes current only after a configured delay. The constructor *schedules* it rather than writing it:

  ```rust
  // storage
  issuer_address: DelayedPublicMutable<AztecAddress, CHANGE_ROLES_DELAY_SECONDS, Context>,

  // constructor
  self.storage.issuer_address.schedule_value_change(admin);
  ```

  Until the delay elapses, a read returns the type's default. For an `AztecAddress` that default is zero, which matters later.

- **The delay was raised from 360 seconds to one hour.** The old value was an order of magnitude below the framework's own recommendation, and it left a six-minute window in which a transaction had to be proved and included.

- **The issuer's record of a mint became a constrained delivery.** Previously the issuer received only an offchain copy of each note, which a standard client cannot process at all, so the mint also emits an event:

  ```rust
  self.emit(Transfer { from: AztecAddress::zero(), to, amount }).deliver_to(
      issuer,           // read from issuer_address a few lines earlier
      MessageDelivery::onchain_constrained(),
  );
  ```

  An event has no owner and no nullifier, so any recipient's client can process it. `onchain_constrained` is what makes it an unforgeable receipt rather than a claim, and it is the line that turns a zero `issuer` from harmless into fatal.

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

Deriving one from the other states the relationship instead of leaving it to be remembered:

```ts
const LONG_TEST_TIMEOUT = DELAY_MS + 600_000;
```

The deployment test passed after that. The mints still failed, with the same assertion, which is where the interesting part begins: the obvious explanation was available, it fitted every symptom, and it was wrong.

## The explanation that fitted and was wrong

It reads plausibly. The deployment test is killed at 900 seconds, in the middle of a sleep that exists precisely so the scheduled issuer address becomes current. It never does. Every later mint reads `issuer_address`, gets the type's default, and the default is the zero address.

The rest follows mechanically, and this part is correct:

1. `issuer_address` reads as zero;
2. a mint emits a `Transfer` event to the issuer with `onchain_constrained` delivery;
3. constrained delivery resolves a tagging secret for the recipient;
4. the recipient is not a curve point, constrained mode has no fallback, so it panics.

Zero is an invalid address. `is_valid()` asks whether `y² = x³ − 17` has a solution at that x, and at zero it does not; about half of all field elements fail the same test.

But the story has a hole, and the hole is visible in the run that followed the timeout fix. With a timeout large enough to survive the sleep, **the deployment test passed** and the mints failed anyway. It also asserted, on the way through, that the issuer address was set:

```ts
const { result: onChainIssuer } = await token.methods.public_get_issuer().simulate({ from: issuer });
expect(onChainIssuer.toString()).toEqual(issuer.toString());
```

That assertion passed. The issuer address was current. And the next transaction to read it in private still saw zero.

## The actual cause: the chain never moved

Two measurements settled it. First, the chain tip against the wall clock:

```
wall clock            : 1790172319
block  42 timestamp   : 1790154805   (now - ts = 17514s)
block  41 timestamp   : 1790154733
block  40 timestamp   : 1790154661
```

The tip was **4.9 hours behind real time**, and the three most recent blocks were 72 seconds apart — one slot — and then nothing. A local network's L1 is an anvil instance whose clock does not track wall time while idle, and no transactions meant no blocks. Sleeping for an hour moved nothing a contract could observe.

Second, what warping does and does not do. Warping L1 through the rollup's cheat codes, then re-reading the tip:

```
BEFORE: tip=42 ts=1790154805
AFTER : tip=42 ts=1790154805      chain advanced by 0s
```

L1 moved; L2 did not. The sequencer builds a block when there is a transaction to put in it, not because time passed. Submitting any transaction after the warp produced one:

```
before: tip=42 ts=1790154805
after : tip=43 ts=1790158477       (+3,672s, exactly the 51 slots warped)
```

That is the whole mechanism, and it explains the contradiction:

- **A public simulation is evaluated at the current time.** `public_get_issuer()` therefore returned the right answer.
- **A private function is proved against the chain tip.** With no block past `effective_at`, `get_current_value()` still returned the pre-delay default.

The two views of the same variable disagreed, and the test asserted the one that could not fail.

What makes the auditability change part of the story is step 2 above. Before it, the issuer received only an *offchain* copy of each note, and offchain delivery is unconstrained: the same zero address took the `else` branch, got a random secret and an undiscoverable tag, and the mint completed while delivering the issuer's copy to nobody. The change did not create the bug. It replaced a wrong result with an error, in a code path nobody expected to be exercised.

## What generalises

Five points survive the specifics.

- **Waiting is not the same as time passing.** A development chain's clock is not the wall clock. Anvil does not advance while idle, and an L2 block exists only when a transaction is included, so a `sleep` in a test moves nothing a contract can observe. Any test that waits for an on-chain deadline has to move the chain and then check that it moved.
- **A public view and a private read are two different questions.** A public simulation is evaluated at the current time; a private function is proved against the chain tip. They can disagree about the same variable, and a test that asserts the public one has asserted the easier question.
- **A delayed value has a dead window after deployment.** If a constructor schedules rather than writes, everything reading that value sees the default until the delay elapses *and* a block exists past that point. What is easy to miss is that some entry points then fail outright rather than read a stale value.
- **Two constants in a fixed relationship should be written as that relationship.** `LONG_TEST_TIMEOUT = 900_000` was correct for one value of a delay it did not mention. Deriving it costs nothing and removes an invariant from the list of things a human has to remember.
- **An unpinned transitive dependency is an unowned decision.** Nothing in the project changed between the run that worked and the run that did not; a library eleven days younger than the framework did.

Two of these only became visible because the first explanation was tested rather than believed. The timeout was a real defect, it fitted every symptom, and fixing it changed the outcome — the deployment test started passing. It was still not the cause of the failure being investigated, and the evidence that said so was one assertion passing in a test whose later steps failed. A fix that improves the symptoms is the easiest kind of wrong answer to keep.

The sleep is gone as well. `RollupCheatCodes.advanceToSlot` warps L1, one transaction produces the L2 block that carries the new timestamp, and a one-hour delay clears in seconds. The suite waited an hour not because the clock could not be moved, but because nobody had looked for the method that moves it, and a comment asserting the opposite was copied forward until it read as established fact.

## Conclusion

The visible error named a cryptographic mechanism: a tagging secret that could not be resolved for a recipient the framework refused to encrypt to. That mechanism worked exactly as designed at every step, and so did the contract. What failed was the test's model of time.

- **The dependency failure was independent** and merely first: an unpinned transitive library, eleven days newer than the framework it serves, broke deployment before any contract logic ran.
- **The timeout was a genuine defect** — a test that slept longer than the timeout guarding it could never pass — but fixing it did not fix the mints, and the difference between those two facts is the point of the article.
- **The cause was that the chain never advanced.** Anvil's clock does not follow wall time, an L2 block needs a transaction, and a private read is anchored to the tip. The issuer address was set in public and unset in private at the same moment.
- **The auditability change made it visible.** A constrained delivery to the zero address cannot be served, where the earlier unconstrained one silently delivered to nobody.

![Mindmap of an Aztec end-to-end debugging case, covering the tagging-secret symptom, the zod dependency pin, the timeout smaller than its sleep, the explanation that fitted but was wrong, the chain that never advanced, and the lessons that generalise]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-23-aztec-e2e-three-layers-mindmap.png)

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
| **Transitive dependency** | A library a project does not import but receives through one of its dependencies, and whose version the project therefore does not choose unless it pins it. |
| **`resolutions`** | A package-manager field that forces a version of a package anywhere in the dependency tree, including copies the project never imports directly. |
| **Cheat codes** | Test-only methods a local network exposes for manipulating chain state, including warping L1 time so that a delay elapses without waiting. |

### Integration Notes

| Behaviour | What an integrator should do |
|---|---|
| A constructor that *schedules* a delayed value leaves it at the type default until the delay elapses. | Treat the first delay after deployment as a window in which value-moving entry points are unavailable, and sequence deployment scripts accordingly. |
| Constrained delivery to an address that is not a curve point aborts the transaction. | Validate any configurable recipient address before it can reach a constrained delivery, rather than relying on the send to succeed. |
| Unconstrained and offchain delivery to the same invalid address succeed silently. | Do not infer from a successful send that a recipient received anything; a delivery guarantee exists only in constrained mode. |
| Waiting in wall-clock time does not advance a development chain. | Warp L1 with the rollup's cheat codes, submit one transaction so an L2 block carries the new timestamp, and assert the tip moved before depending on it. |
| A public view and a private read of the same delayed variable can disagree. | Assert the private path, or the block timestamp, rather than the public getter; the getter is evaluated at the current time and will pass first. |
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

Note what this did and did not explain. Fixing it made the deployment test pass, which looked like progress, but the mints kept failing: the sleep had never been advancing the chain in the first place. A change that improves the symptoms is not evidence that it addressed the cause.

**Q: How can a public getter and a private function disagree about the same storage variable?**

They are answering at different times. A public view is a simulation the node evaluates against the current timestamp, so it sees a scheduled value that has become current. A private function is proved against the chain tip, and its reads are evaluated at that block's timestamp.

When no block has been produced since the value became effective, the two diverge: the getter returns the new value and the private read returns the old one. A test that asserts only the public view has asserted the question that cannot fail.

The fix is not to assert harder but to advance the chain: warp the clock, submit one transaction so a block carries the new timestamp, and verify the tip moved before relying on it.

**Q: How could an unpinned dependency break a project whose own code did not change?**

Five framework packages declare their dependency on the validation library as `^4`, which permits any 4.x release. A resolution taken after a newer 4.x appeared installed a version published eleven days after the framework, containing a recursion check that overflows on a self-referential schema the framework uses. Nothing in the project changed; what changed was what `^4` meant on the day the dependencies were resolved.

**Q: Would running the test suite more often have caught this earlier?**

Yes, and that is the practical lesson. The suite waited out a real delay, so a full run took over an hour, most of it a single sleep. It was therefore skipped after the delay change, and a test that is expensive enough to skip stops reporting.

The better answer, though, is to remove the reason it was slow, and in this case the wait was not merely expensive but ineffective. Warping the chain and forcing one block took the suite from 3,698 seconds to 142 seconds, and from eight failures to none in the token suite. Keeping the fast suite in continuous integration remains worthwhile, but a slow test is worth interrogating before it is scheduled around.

## References

### Analyzed source

- [CMTA/private-CMTAT-aztec](https://github.com/CMTA/private-CMTAT-aztec/) — the token and the test suite described here, analyzed at commit [`cb6111a87f21317c6d3ab226edb80d8b297e4923`](https://github.com/CMTA/private-CMTAT-aztec/tree/cb6111a87f21317c6d3ab226edb80d8b297e4923), 2026-09-23. The quoted storage declaration and constructor are in `contracts/cmtat-aztec/src/main.nr`; the test constants are in `src/test/e2e/index.test.ts`.
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
