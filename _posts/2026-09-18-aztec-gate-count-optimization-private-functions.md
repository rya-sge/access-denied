---
layout: post
title: "Gates on Aztec — What a Private Function Costs, Where the Cost Hides, and Seven Measured Ways to Lower It"
date:   2026-09-18
lang: en
locale: en-GB
categories: blockchain ethereum ZKP
tags: aztec zkp noir smart-contracts gas privacy
description: "On Aztec a private function's gate count is proving time on the user's device: kernel overhead, budgets, deliveries, reads, and seven measured optimisations."
image: /assets/article/blockchain/aztec/2026-09-18-aztec-gates-mindmap.png
isMath: false
---

[Aztec](https://aztec.network/) is a privacy-focused Layer 2 on Ethereum whose contracts are written in [Noir](https://noir-lang.org/). A contract's private functions are compiled to zero-knowledge circuits and proved on the user's own device before the transaction is sent; its public functions run later on a sequencer, in a virtual machine close to the EVM. [An earlier article]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/) covers that split. This one is about what the private half costs.

On Ethereum the unit of cost is gas, it is paid to the network, and the compiler's job is to spend less of it. On Aztec's private side the unit is the **gate**, the number of constraints in the circuit a function compiles to, and nobody is paid for it: it is the size of the proof the user's laptop or phone has to produce, so it is time, memory and battery, in roughly linear proportion. A 160,000-gate transfer proves in tens of seconds on a laptop; the same transfer at 120,000 gates proves a quarter faster, and the network does not know the difference. The Aztec documentation is direct about the consequence: "you can do as much computation as you want in private functions", the network cost being the same regardless, and "the only effect of a large circuit is that it takes longer to prove on the client."

Gate optimisation therefore follows different rules from gas optimisation. The big costs are not where an EVM developer expects them: a nested function call is worth a hundred thousand gates, a `>=` comparison costs more than a multiplication, and a loop is paid for its maximum iteration count whether or not it runs that far. This article sets out the cost model as the documentation and the tooling give it, then works through seven optimisations measured on a security-token contract during two code reviews, with the gate counts before and after, and the cases where the measurement said not to bother.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The cost model

### A circuit is sized for its worst case

A private function does not execute; it is *proved*. The compiler turns it into a fixed arithmetic circuit, and the proof shows that some assignment of wires satisfies every constraint. Two properties follow that have no EVM counterpart:

- **No variable-length loops.** The number of iterations, the size of every array, the number of notes a function may read are fixed when the contract is compiled. A loop `for i in 0..16` costs sixteen iterations of gates even if the data fills two of them; the other fourteen are proved on zeros.
- **Every branch is paid.** An `if` does not skip its body; both arms are in the circuit and a selector picks the result. Code that is "rarely executed" costs the same as code that always is.

The Noir documentation's phrase for this is *thinking in circuits*: the size of the circuit equals the size of the longest execution trace it can represent.

### The kernel overhead nobody's code shows

`aztec profile gates ./target` prints the gate count of each contract function on its own. That number is what the developer controls, and it is not what the user proves. Every private transaction also proves the protocol's **kernel circuits**, which check each function call's outputs against its inputs and fold them into one proof. The documentation's figures for a transaction that calls one contract function:

| Circuit | Gates |
|---|---:|
| Account entrypoint (the account contract's function) | ~22,000 |
| Your function | 14,000 (in the example) |
| `private_kernel_init` (first call) | ~46,000 |
| `private_kernel_inner` (every further call) | ~101,000 |
| `private_kernel_reset` | ~200,000 |
| `private_kernel_tail` | ~44,000 |
| **Total** | **~427,000** |

![One private call as the user proves it: the account entrypoint and the contract function feed the kernel init and inner circuits, then reset and tail, about 427,000 gates in total for 14,000 of contract code]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-gates-transaction-cost-concept.png)

Two lessons are in that table. The fixed kernel overhead is around 290,000 gates before any contract code runs, so a 40,000-gate saving in a function is a 10% saving on the transaction, not a 30% one. And **each additional private function call costs a `private_kernel_inner` iteration of about 101,000 gates**, more than most functions cost themselves. The documentation draws the design conclusion: "inlining a verification step into the calling function saves an entire kernel fold (~101k gates), even if it slightly increases the calling function's own gate count."

### What the common operations cost

The documentation's reference table, with two rows added from the measurements below:

| Gates | Operation |
|---:|---|
| ~75 | Hashing three fields with Poseidon2 |
| ~3,050 | One note slot in a note read budget (measured, next section) |
| 3,500 | Reading a value from a tree (public data, note hash, nullifier) |
| 4,000 | Reading a `DelayedPublicMutable` from a private function (a second read of the same slot: ~1,920, measured) |
| ~5,000 | SHA-256, varying with input size |
| ~20,200 | One constrained encrypted delivery of a private log (measured, on a `Transfer` event) |
| ~101,000 | One nested private call, through the kernel |

Note what is *not* in the table: arithmetic. Additions and multiplications of field elements are the native operation of the proving system and cost single gates. The expensive things are bit operations, comparisons, hashes, tree reads and, above all, anything that produces a side effect the kernel has to process.

### Two tools, two questions

`aztec profile gates ./target` answers "how big is this function"; it needs only a compiled artifact and runs in seconds, which makes it the tool for before/after measurement in a review. `aztec profile flamegraph <artifact> <function>` shows where inside a function the gates are, with width proportional to gate count, and is the tool for finding what to cut. `aztec-wallet profile` and `.profile()` in aztec.js run a full transaction against a network and add the kernel circuits, which is the tool for the number the user experiences. Every figure in this article comes from the first, unless stated.

## Seven optimisations, measured

The subject is a CMTAT-style security token on Aztec at framework version 5.2.0: private balances as notes, an issuer that receives an encrypted copy of every note for audit, freeze and blacklist screening on every party, and the AIP-20 private/public bridges. Two code reviews measured every change with `aztec profile gates` before and after, and reverted every probe. The cases are ordered by what they teach, not by size.

### 1. A duplicated read is cheaper than a read, but it is not free

`burn` checked the account's freeze flag, then called an inlined helper that checked it again. Both are `DelayedPublicMutable` reads, quoted at ~4,000 gates each.

| | gates |
|---|---:|
| `burn` with both reads | 83,656 |
| `burn` with one | **81,736** |
| saving | 1,920 |

The saving is under half the quoted cost of a read, and that is the lesson: a second read of the *same* slot shares most of its constraints with the first (the membership proof, the delay logic), so "one read equals 4,000 gates" overstates a duplicate by more than two times. The naive arithmetic would have predicted a saving twice as large. The removal was still made, because it was free and also fixed a wrong error message; the point is that the estimate had to be checked.

### 2. Hoist what does not vary out of a loop

Batch functions call a helper once per array entry. In a circuit the helper is inlined, so every read inside it is repeated per entry, including reads that cannot change within the call: the issuer's address, the sender's own flags. Moving the issuer read above the loop and passing it as a parameter:

| Function (cap 4) | unhoisted | hoisted | saved |
|---|---:|---:|---:|
| `mint_batch` | 113,619 | **107,871** | 5,748 |
| `burn_batch` | 312,568 | **306,820** | 5,748 |
| `transfer_batch` | 453,051 | **447,303** | 5,748 |

Three identical savings, because the hoisted read is the same one in all three. The technique is ordinary loop-invariant code motion; what differs from the EVM is that the compiler does not do it for you, since it cannot know that a state read is invariant, and that the cost multiplies by the loop bound even when the array is mostly empty.

### 3. Size a loop for the common case and grow on demand

The largest saving. Spending a private balance means picking notes until their sum covers the amount. The library function every transfer, bridge and burn used sized that search for the protocol maximum of **sixteen** notes, at about 3,050 gates per slot, whatever the holder actually owned:

| Note budget | `transfer_private_to_private` | `transfer_private_to_public` | `burn` |
|---:|---:|---:|---:|
| 16 | 161,493 | 95,941 | 111,638 |
| 8 | 136,709 | 71,157 | 86,854 |
| 4 | 124,500 | 58,948 | 74,645 |
| 2 | **119,290** | **53,737** | **69,434** |

Linear, as the library's own comment on `try_sub` says ("the gate count scales relatively linearly with `max_notes`"), and 42,000 gates between the two ends. The catch is that a budget of two fails for a holder whose balance is spread over three notes. The AIP-20 token's answer, adopted here, is to try two and, if they do not cover the amount, have the contract call **itself** through an `#[only_self]` function with a budget of eight, as many times as needed:

```noir
pub fn try_debit(balances, from, amount, max_notes) -> (bool, u128) {
    let subtracted = balances.at(from).try_sub(amount, max_notes);
    if subtracted >= amount { (true, subtracted - amount) }        // covered: the change
    else { assert(subtracted > 0, "Balance too low"); (false, amount - subtracted) }
}
```

![Debit workflow: try two notes; if they cover the amount create the change note, if nothing was found fail with Balance too low, otherwise the contract calls itself with a budget of eight and repeats until covered]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-gates-note-budget-workflow.png)

That recursion is a nested private call, so it costs a `private_kernel_inner` iteration, about 101,000 gates, plus the recursive function's own 30,138. The trade-off is explicit and it is the one every "size for the common case" decision makes:

| Notes to spend | Fixed budget of 16 | Budget 2 + recursion of 8 |
|---|---:|---|
| 1 or 2 | 161,493 | **119,290** |
| 3 to 10 | 161,493 | 119,290 + one recursive call, **worse** |
| 13 to 16 | fails (side-effect budget) | works |
| more than 16 | fails | works |

The scheme wins if most holders spend one or two notes per transfer, which for a security token with large, infrequent transfers is plausible but which nobody has measured; the decision was taken on the standard's reasoning, and a side benefit decided it: the old fixed budget also *failed* on fragmented balances, because a call's side-effect budget ran out at twelve notes, and each recursive call has its own.

### 4. Every constrained delivery is a circuit of its own

Sending a private note or event to a recipient means encrypting it and tagging it so the recipient's wallet can find it. Done *constrained*, inside the proof, so the recipient is guaranteed a correct ciphertext, it is the single most expensive line a token writes:

| Change | Function | before | after |
|---|---|---:|---:|
| `Transfer` event delivered constrained to the recipient **and** the issuer | `transfer_private_to_private` | 120,824 | 161,493 (+40,669) |
| Constrained mint event to the issuer | `mint_to_private` | 36,976 | 61,062 (+24,086) |
| Constrained burn event to the issuer | `burn` | 87,935 | 111,638 (+23,703) |

About **20,000 to 24,000 gates per delivery**, and each note created has at least one. Two consequences shaped the token's design:

- **Delivery count, not note count, set the batch cap.** With the `Transfer` event constrained to two parties, a transfer recipient costs four constrained deliveries where a mint recipient costs one; `transfer_batch` at three recipients aborted with `push out of bounds`, and the cap is two while `mint_batch`'s is four. The caps were found by trying values against the test suite, not derived.
- **Unconstrained delivery is the cheap option and often the wrong one.** `MessageDelivery::onchain_unconstrained()` skips the in-circuit encryption. It is the right mode when the sender is the party who wants the note to arrive, and the wrong mode for anything a recipient relies on, because the sender's software could then post a ciphertext that says something else: a `Transfer` receipt delivered unconstrained is forgeable by the sender. The token paid the 40,669 for that reason.

### 5. Read only what varies, once

The screening of a transfer reads five `DelayedPublicMutable` values in private: two freeze flags, two list flags and the list mode. A variant of the token without lists reads two. The difference in the whole `transfer_private_to_public` circuit is 10,407 gates, which is what the two list reads and the mode flag cost together; against AIP-20's 38,277 for the same operation, the token's 53,737 after optimisation 3 is almost entirely these compliance reads.

The lesson is not to drop them. Reads are the cost of a *feature*, and a design that reads the same slot in two places (case 1) or reads per iteration what is constant per call (case 2) pays for the feature twice.

### 6. Packing is a storage saving, not always a gate saving

Storage on Aztec is field elements, and a struct's default encoding spends one field per member. A `CreditEventsStruct { bool, bool, string }` took three slots; a hand-written `Packable` put the two flags into one field as bits and brought it to two. Fewer slots means fewer public storage operations and, for notes, fewer inputs to the note hash. But packing and unpacking is bit arithmetic inside a circuit, and bit arithmetic is the expensive kind:

- The documentation's own example: `number << 16` costs 60 gates more than `number * 2^16`, for the same result. Its advice is to prefer multiplications and additions to shifts and masks, and boolean equality to `>=`: a thousand-iteration loop saved 751 gates by replacing one relational comparison with an equality latch.
- On the token, the packing was measured to leave the gate profile of the variant unchanged, because the struct is read in *public*, where the cost is gas and the saving is a slot. The same packing on a struct read in a private function would have to be measured, and could lose.

The technique is covered on its own in [an earlier article]({{site.url_complet}}/2026/09/16/aztec-packable-storage-packing/); the point here is that "smaller in storage" and "fewer gates" are two different measurements, and only one of them is guaranteed.

### 7. Moving code does not move gates, and asserts on constants cost nothing

Two refactors were checked for cost and found to have none, which is as useful to know as a saving:

- **Library functions and inlined helpers compile identically.** Moving the mint, transfer and burn chains out of three contracts into one library module produced 48 private circuits **byte-identical** to the originals. A `#[internal("private")]` helper and a plain library function are both inlined into the caller; neither is a nested call. The corollary matters for design: the 101,000-gate nested-call cost applies to `#[external]` functions the contract calls through `call_self` or on another contract, not to how the source is organised.
- **An assertion the compiler can decide is free.** Two `assert`s checked array lengths that were compile-time constants; removing them left every gate count unchanged, because a constraint on a constant folds away. The reverse is the trap: an assertion on a *witness* value is a real constraint, and a check that is repeated (case 1) is paid each time.

## What the measurements say in general

Reading the seven cases together:

- **Measure; the estimates are wrong in both directions.** A duplicate read cost half the quoted figure (case 1); packing cost nothing where it was expected to cost gates (case 6); a refactor everyone worried about cost nothing (case 7). `aztec profile gates` runs in seconds on an artifact, so the price of knowing is small.
- **The budget you did not use is the budget you paid.** Notes (case 3), loop iterations (case 2), array sizes: a circuit is its maximum trace. The optimisations that mattered most were about sizing for what usually happens and handling the rest another way.
- **Side effects cost more than computation.** Deliveries at 20,000 gates each and nested calls at 101,000 dwarf any arithmetic a token does. A design review should count deliveries and calls before it counts operations.
- **The user pays, so the trade-offs are the user's.** A cheaper common case with a dearer rare case (case 3), a forgeable receipt against a provable one (case 4): these are choices about whose device does the work and what a recipient can trust, and they belong in the design document, not in a micro-optimisation pass.
- **Correctness first, then the profile.** Every change here was measured together with the test suite, and two of the largest changes moved limits the tests had pinned; the gate count is one acceptance criterion, the tests are the other.

## Conclusion

A private function's gate count is the proving work the user's device does, and the network does not see it; optimising it is a matter of the user's time, not of fees.

- **The kernel dominates.** About 290,000 gates of fixed overhead per transaction, and about 101,000 for every additional private call; inlining a helper saves more than any micro-optimisation inside it.
- **A circuit is its worst case.** Loops, arrays and note budgets are paid at their bound. Sizing for the common case and recursing for the rest saved 42,000 gates on a transfer, at the price of a nested call for fragmented balances.
- **Side effects are the expensive lines.** A constrained delivery costs 20,000 to 24,000 gates; a tree read about 3,500; a delayed public read about 4,000, half that for a repeat of the same slot; arithmetic on fields is nearly free, bit operations and comparisons are not.
- **Some refactors are free and some optimisations are not.** Library functions inline exactly like internal helpers; asserts on constants vanish; storage packing saves slots and only sometimes gates.
- **Measure with `aztec profile gates`**, before and after, with the tests green on both sides.

![Mindmap of gate optimisation on Aztec covering the cost model (worst-case circuits, kernel overhead, operation costs, tools), the seven measured cases and the general lessons]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-18-aztec-gates-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Gate** | One constraint of the arithmetic circuit a private function compiles to; the gate count is proportional to the time and memory the user's device spends proving. |
| **Kernel circuit** | A protocol circuit proved with every private transaction that validates each function call and folds it into one proof: `init`, `inner` (per further call), `reset`, `tail`. |
| **Nested private call** | A call from one private function to another `#[external]` function, on the same or another contract; each costs a `private_kernel_inner` iteration of about 101,000 gates. |
| **Inlining** | What the compiler does with library functions and `#[internal]` helpers: their gates join the caller's circuit, and no kernel iteration is added. |
| **Note budget** | The fixed number of notes a debit is compiled to read; every slot costs about 3,050 gates whether or not a note fills it. |
| **`#[only_self]` recursion** | A private function the contract calls on itself to extend a bounded operation (here, spending more notes) at the cost of a nested call. |
| **Constrained delivery** | Encrypting and tagging a private note or event inside the proof, so the recipient is guaranteed a correct message; about 20,000 gates per delivery. |
| **`DelayedPublicMutable` read** | Reading a public value from a private function through a delay that lets the read be proved against a past block; about 4,000 gates, less for a repeated read of one slot. |
| **Side-effect budget** | The per-call maximum of note hashes, nullifiers and logs a private function may emit; exceeding it aborts with `push out of bounds`. |
| **`aztec profile gates`** | The CLI command that prints per-function gate counts from a compiled artifact, without kernel overhead; the measurement tool for before/after comparison. |

### Integration Notes

For a team measuring or lowering the cost of its own Aztec contract.

| Behaviour | What to do about it |
|---|---|
| `aztec profile gates` excludes the kernel; a user's transaction is that number plus roughly 290,000 fixed and 101,000 per extra private call. | Quote function gates for comparing versions and `aztec-wallet profile` for what the user experiences; never present the former as the latter. |
| A nested private call costs more than most functions. | Inline helpers (library functions and `#[internal]` are free); reserve `call_self` and cross-contract calls for what needs a separate circuit, such as recursion past a budget. |
| Loops, arrays and note reads are paid at their compile-time bound. | Set bounds for the common case; measure the linear cost per slot; provide a recursion or a batching path for the tail. |
| A constrained delivery is ~20,000 gates and the side-effect budget caps how many fit in a call. | Count deliveries per recipient before choosing a batch cap; find caps by running the suite at candidate values, not by reading protocol constants. |
| `onchain_unconstrained` delivery is cheaper and forgeable by the sender. | Use it only where the sender is the party who wants the message received; constrain receipts, audit copies and anything a third party relies on. |
| Repeated reads of one slot cost less than the first, but not nothing. | Read each slot once per call and pass the value; hoist reads out of loops. |
| Bit shifts, masks and `<`/`>=` are dearer than field arithmetic and equality. | Prefer multiplication by a power of two, boolean latches on equality, and `array.sort()` from the standard library over hand-written loops. |
| Packing a struct saves storage slots; its gate effect depends on where the struct is read. | Measure private-side packing separately from public-side; a public read pays gas, not gates. |
| A change that is meant to be gate-neutral can be checked exactly. | Diff `aztec profile gates` output before and after; a byte-identical artifact is the strongest form of the check. |

## Frequently Asked Questions

**Q: If the network does not charge for gates, why optimise them at all?**

Because the user pays them in time. The proof of a private function is produced on the user's device, and its cost is roughly proportional to the gate count: memory, seconds, battery. A transaction that proves in a minute on a phone against twenty seconds is a product difference.

The two edge cases the documentation names, transaction expiry during a long proof and fee movement while proving, are both functions of proving time. The network cost is unchanged; the user's is not.

**Q: A function shows 14,000 gates in `aztec profile gates`. What does the user prove in total?**

Around 427,000, in the documentation's worked example. The transaction also proves the account contract's entrypoint (~22,000), `private_kernel_init` (~46,000), one `private_kernel_inner` per further call (~101,000), `private_kernel_reset` (~200,000) and `private_kernel_tail` (~44,000). The function's own gates are a small share; the way to move the total by a large amount is to change the number of private calls, not to shave the function.

**Q: What is the difference, in gates, between a library function, an `#[internal]` helper and a `call_self`?**

The first two cost nothing extra: both are inlined into the caller, and moving code between them was measured to leave 48 circuits byte-identical. `call_self`, and any call to an `#[external]` function, is a nested private call and adds a kernel iteration of about 101,000 gates. That is why the recursion in case 3 is worth avoiding for the common case and worth paying for the rare one.

**Q: Why does a duplicate read cost less than the quoted price of a read?**

The quoted ~4,000 gates for a `DelayedPublicMutable` read include the parts every read shares when it targets the same slot in the same call: the tree membership proof and the delay logic. A second read reuses them and adds only its own comparison and wiring, measured at 1,920.

The general point is that per-operation prices do not add linearly when operations share inputs; only a measurement of the pair gives the cost of the pair.

**Q: How was the batch cap of two recipients for `transfer_batch` found, and why is it lower than the mint cap of four?**

By trying values against the test suite: three recipients aborted with `push out of bounds`, the per-call side-effect budget. A transfer recipient costs four constrained deliveries, namely the recipient's note, the change note and the `Transfer` event to each of the recipient and the issuer, where a mint recipient costs one or two, so the transfer batch reaches the budget with half the entries. Protocol constants such as the nested-call limit are irrelevant, since a batch makes no nested calls; the binding constraint had to be measured.

**Q: In case 3, why not just use a budget of four without recursion?**

It would save 37,000 gates on a transfer and still fail for a balance spread over five notes, which is more often than the sixteen-note version failed. The recursion is what turns "cheaper and fails more" into "cheaper and never fails": each recursive call has its own side-effect budget, so the note count is no longer bounded at all.

Whether the cheaper common case is worth the dearer fragmented one depends on how fragmented real balances are, which is usage data the reviews did not have.

**Q: When should a private log be delivered unconstrained?**

When the sender is the party who wants the message received and nobody else relies on its content: a note a user creates for itself, a self-send, a message whose only reader is the sender's own future wallet state.

Unconstrained delivery skips the in-circuit encryption and saves about 20,000 gates, but the circuit then proves nothing about the ciphertext, so the sender's software could post one that decrypts to something else. A receipt, an audit copy, a payment to a third party: anything a recipient acts on must be constrained.

## References

### Aztec documentation

- [Writing Efficient Contracts](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/advanced/writing_efficient_contracts) — the cost model, the operation-cost table, the arithmetic, loop and unconstrained-function examples
- [Profiling Transactions](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/advanced/how_to_profile_transactions) — `aztec profile gates`, flamegraphs, `aztec-wallet profile`
- [Private Kernel Circuit — Performance Impact](https://docs.aztec.network/developers/docs/foundational-topics/advanced/circuits/private_kernel#performance-impact) — the per-circuit gate figures and the ~427,000 worked example
- [Data Packing and Serialization](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/data_packing)
- [Note Delivery](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/note_delivery) — constrained and unconstrained delivery modes

### Noir documentation

- [Thinking in Circuits — Writing efficient Noir](https://noir-lang.org/docs/explainers/explainer-writing-noir) — the language-level guidance the Aztec page builds on

### Analyzed source

- [AztecProtocol/aztec-nr](https://github.com/AztecProtocol/aztec-nr) — analyzed at tag [v5.2.0](https://github.com/AztecProtocol/aztec-nr/tree/v5.2.0), commit [`22e152679f69a2307fdb1b17f60fd4f51a3fd4f5`](https://github.com/AztecProtocol/aztec-nr/tree/22e152679f69a2307fdb1b17f60fd4f51a3fd4f5), 2026-09-18: `balance-set/src/balance_set.nr` (`sub`, `try_sub` and its comment on `max_notes`)
- [CMTA/aztec-standards](https://github.com/CMTA/aztec-standards) — the AIP-20 `Token` whose note-budget scheme case 3 adopts (`INITIAL_TRANSFER_CALL_MAX_NOTES = 2`, `RECURSIVE_TRANSFER_CALL_MAX_NOTES = 8`), analyzed at commit [`5433e9c7dc34f1b426adfe0ce9e0ae3a688351d9`](https://github.com/CMTA/aztec-standards/tree/5433e9c7dc34f1b426adfe0ce9e0ae3a688351d9), 2026-09-18
- [CMTA/private-CMTAT-aztec](https://github.com/CMTA/private-CMTAT-aztec) — the token whose 0.3.0 and 0.4.0 code-quality reviews produced every measurement in this article; the figures are quoted from `doc/audits/tools/v0.3.0/` and `v0.4.0/` at the 0.4.0 development head, 2026-09-18

### Related articles

- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
- [Packing Small Values into One Field on Aztec — The Packable Trait, Its Cost and Its Traps]({{site.url_complet}}/2026/09/16/aztec-packable-storage-packing/)
- [Code Reuse in Aztec Contracts — Modules, Traits and Library Crates Instead of Inheritance]({{site.url_complet}}/2026/09/15/aztec-noir-contract-code-reuse-without-inheritance/)
- [Reading Public State from a Private Function on Aztec — Why a Pause Flag Comes with a Delay]({{site.url_complet}}/2026/09/14/aztec-delayed-public-mutable-pause-privacy-delay/)
- [AIP-20, the Aztec Token Standard, Compared with ERC-20 and ERC-7984]({{site.url_complet}}/2026/09/11/aip-20-aztec-token-standard-vs-erc-20-erc-7984/)
- [Understanding zk-SNARK: A Deep Dive into Zero-Knowledge Proofs]({{site.url_complet}}/2025/07/29/zk-snark-overview/)
