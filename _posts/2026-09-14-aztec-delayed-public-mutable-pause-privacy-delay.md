---
layout: post
title: "Reading Public State from a Private Function on Aztec — Why a Pause Flag Comes with a Delay"
date:   2026-09-14
last_modified_at: 2026-09-17
lang: en
locale: en-GB
categories: blockchain ethereum ZKP
tags: aztec zkp privacy smart-contracts token
description: A private Aztec function cannot read a public flag. DelayedPublicMutable allows it, at the price of a delay that also caps how long the transaction stays valid.
image: /assets/article/blockchain/aztec/2026-09-14-aztec-delayed-public-mutable-mindmap.png
isMath: false
---

[Aztec](https://aztec.network/) is a privacy-focused Layer 2 on Ethereum. A contract there has private functions, proved on the user's device over encrypted notes, and public functions, executed afterwards by a sequencer over ordinary readable state; the private half of a transaction runs first, without access to the current public state. That ordering is the reason the problem in this article exists.

A token contract usually carries a small piece of public configuration that every transfer has to consult: a pause flag, a fee rate, an allowlist entry. 

On Ethereum this is a single storage read. 

On [Aztec](https://aztec.network/), the private half of a transfer is proved on the user's device against a block that has already been mined, so the function never sees the chain's present state and cannot know whether the flag flipped since. 

Aztec.nr offers two ways around this, and neither is free: 

- Enqueue a public call that performs the check, which publishes the fact that the token was touched;
- Store the flag in a `DelayedPublicMutable`, which lets the private function read it but only because every write is postponed by a fixed delay.

This article works through the second option with a generic private token and a pause flag as the running example. It explains why the delay is what makes the private read sound, what the delay costs the sender (a shorter window in which the transaction can be included, and a public expiration timestamp that shrinks the privacy set) and why the same delay that protects the read makes the mechanism a poor fit for an emergency pause. The reasoning is not specific to any one token design; it applies to any public value a private function needs to read.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The problem: a private function cannot see the present

Aztec splits a contract into private functions, executed and proved on the sender's device, and public functions, executed by the sequencer when the block is built. A previous article, [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/), covers the model in detail; two properties matter here.

- **Private execution is anchored to a past block.** The proof is built against the state root of an *anchor block* the wallet picked when it started simulating. The transaction is then broadcast, sits in the mempool and is included some blocks later. Between the anchor block and the inclusion block, public state can change.
- **The proof cannot be re-run by the sequencer.** Public functions are re-executed by whoever builds the block, so they always see the current state. Private functions are verified, not executed, so their inputs are frozen at proving time.

A private function can therefore prove what a public storage slot *contained at the anchor block*. Aztec.nr exposes this as a historical read. What it cannot do is prove that the slot still holds that value at inclusion time, because between the two blocks an admin may have written to it. The `PublicMutable` documentation states the consequence plainly: private functions "can perform historical reads of `PublicMutable` values at past times, but they have no way to guarantee that the value has not changed since then". So `PublicMutable` has no private read at all.

Take the running example. A token keeps balances as private notes, and a `PAUSE_ROLE` holder can stop transfers:

```rust
#[storage]
struct Storage<Context> {
    balances: Map<AztecAddress, BalanceSet<Context>, Context>,
    paused: PublicMutable<bool, Context>,
}

#[external("public")]
fn pause() {
    // role check omitted
    self.storage.paused.write(true);
}

#[external("private")]
fn transfer(to: AztecAddress, amount: u128) {
    // There is no `self.storage.paused.read()` available here.
    self.storage.balances.at(self.msg_sender()).sub(amount);
    self.storage.balances.at(to).add(amount);
}
```

The `transfer` body compiles without any pause check, and no method exists that would let it read `paused`. If the flag matters, the contract has to pick one of the two designs below.

![A private transfer either enqueues a public call that reads PublicMutable and publishes the contract interaction, or reads a DelayedPublicMutable in private and accepts a bounded expiration timestamp]({{site.url_complet}}/assets/article/blockchain/aztec/delayed-public-mutable-two-paths-concept.png)

## Option one: enqueue a public check

The pattern the `PublicMutable` documentation recommends is to let the private function enqueue a public call on the same contract, marked `#[only_self]` so nobody else can invoke it:

```rust
#[external("private")]
fn transfer(to: AztecAddress, amount: u128) {
    self.storage.balances.at(self.msg_sender()).sub(amount);
    self.storage.balances.at(to).add(amount);
    self.enqueue_self._assert_not_paused();
}

#[external("public")]
#[only_self]
fn _assert_not_paused() {
    assert(!self.storage.paused.read(), "paused");
}
```

The public phase runs after the private phase, inside the block, against current state. If the flag is set, the assertion fails and the whole transaction reverts, private effects included. The check is exact and immediate: a pause written in block *N* stops every transfer included from block *N* on.

The price is visibility. Everything the public phase does is public: the address of the contract, the selector of the function called, the arguments it receives, its gas usage. Because the call comes from the contract itself, `msg_sender` is the token rather than the user, so the sender's account is not published. But an observer reading the block still learns that this transaction called `_assert_not_paused` on this token, which is the same as learning that a transfer of this token happened. Every transfer becomes a countable, timestamped public event even though its amount and parties stay hidden.

Whether that matters depends on the token. A design that already enqueues a public call for another reason, say to update a public `total_supply` on mint and burn, has paid this cost already on those paths, and adding the pause assertion there is free. A design whose transfers are otherwise fully private loses the property that nothing in the block ties a transaction to the token.

## Option two: DelayedPublicMutable

`DelayedPublicMutable<T, DELAY>` is a public value that behaves like `PublicMutable` with one change: a write does not take effect when it is executed. Instead the public function *schedules* it, and the new value becomes current only once `DELAY` seconds have elapsed. The example becomes:

```rust
// The initial delay is a type parameter, in seconds.
global PAUSE_DELAY_SECONDS: u64 = 6 * 60 * 60; // 6 hours

#[storage]
struct Storage<Context> {
    balances: Map<AztecAddress, BalanceSet<Context>, Context>,
    paused: DelayedPublicMutable<bool, PAUSE_DELAY_SECONDS, Context>,
}

#[external("public")]
fn pause() {
    // role check omitted
    self.storage.paused.schedule_value_change(true);
}

#[external("private")]
fn transfer(to: AztecAddress, amount: u128) {
    assert(!self.storage.paused.get_current_value(), "paused");
    self.storage.balances.at(self.msg_sender()).sub(amount);
    self.storage.balances.at(to).add(amount);
}
```

The private `get_current_value` is now legal, and no public call is enqueued. The transfer stays entirely private: no contract address, no selector, no evidence in the public part of the block that this token was involved.

### How the private read is made sound

The delay is what turns a historical read into a safe one. In public, `schedule_value_change` stores three things: the value before the change, the value after, and the timestamp at which the switch happens, computed as the current block timestamp plus the current delay. Nothing can make the value change earlier than that timestamp, and a second schedule replaces the first rather than shortening it.

In private, `get_current_value` reads that packed structure from the anchor block through a historical storage proof and derives a *time horizon*: the last timestamp at which the value it just read is guaranteed to still be current. Two cases:

- **No change is pending at the anchor block.** The earliest a change could land is a schedule made right after the anchor block, effective one delay later, so the horizon is `anchor_timestamp + delay`.
- **A change is already scheduled.** The horizon is the scheduled timestamp of change, which is public information.

The function then calls `set_expiration_timestamp(horizon)`. The kernel circuits carry the smallest expiration requested by any function in the transaction, and the rollup circuits refuse to include a transaction in a block whose timestamp exceeds it. The private function has, in effect, proved "this was the value, and the protocol will not let this transaction land after the value may have changed".

![The wallet reads the paused flag at the anchor block through a historical proof, computes the time horizon, sets the transaction expiration timestamp, and the sequencer rejects inclusion past that horizon]({{site.url_complet}}/assets/article/blockchain/aztec/delayed-public-mutable-private-read-sequence.png)

The delay itself is also protected. A public function can lower or raise it with `schedule_delay_change`, but a decrease only takes effect after a wait equal to the difference between the old and new delay, so a value change scheduled the moment the shorter delay becomes active lands no earlier than it would have under the old one. An increase applies immediately, because it can only push changes further out. Without this rule an admin could shorten the delay to zero and flip the flag under a transaction that had already been proved.

### What the read costs in the circuit

The private read is a historical public storage read plus a hash check: the library stores the whole scheduled-change structure behind one hash, so the proof needs a single inclusion path whatever the size of `T`. 

The Aztec.nr source puts this at roughly 4,000 constraints per variable read. Two flags read in the same function cost two reads, which is why the library recommends packing values that are read together into one `Packable` struct held in a single `DelayedPublicMutable`. The consequence is that they then share one delay, a point that comes back below.

## What the delay costs

The read is private, but it is not free of side effects. Two of them fall on the sender of every transaction that performs it.

### The transaction expiration window

A transaction that reads no `DelayedPublicMutable` carries the protocol default: its expiration is the anchor block timestamp plus `MAX_TX_LIFETIME`, which is 86,400 seconds, one day. A transaction that reads the pause flag carries `anchor_timestamp + PAUSE_DELAY_SECONDS` instead, or less if a change is pending. The delay is therefore the window in which the sender must prove the transaction, broadcast it and see it included.

That window has to absorb three things in sequence:

- **Client-side proving.** On a laptop this takes tens of seconds to minutes, depending on the number of private calls.
- **Mempool time.** The interval between submission and a sequencer picking the transaction up.
- **The sequencer's own scheduling.** The transaction has to land in a block before the expiration timestamp.

The library's list of what a short delay breaks is concrete: "large transactions that take long to prove be unfeasible, restrict users with slow proving devices, and force large transaction fees to guarantee fast inclusion".

Two values show the range. With a 360-second delay, the value used in the Aztec.nr documentation example (five slots of 72 seconds), a transaction that took four minutes to prove on a phone has two minutes left to be picked up. With a six-hour delay the constraint disappears for any realistic device.

The kernel keeps the minimum across every function in the transaction. A transaction that touches two contracts, one with a 1,000-second delay and one with 10,000, expires after 1,000 seconds. The same mechanism is used by contract upgrades: an upgradeable contract class carries an update delay, and a pending upgrade lowers the expiration of every transaction that calls it to the moment of the upgrade.

### The privacy-set fingerprint

The expiration timestamp is part of the transaction's public data. Observers cannot see what a private transaction did, but they can see when it expires, and they can subtract the anchor timestamp. Every transaction that read a delayed value with the same delay produces the same difference. That turns the delay into a label:

| Delay of the contract | What an observer learns from `expiration - anchor` |
|---|---|
| Equal to `MAX_TX_LIFETIME` (24 h) | Nothing. The transaction is indistinguishable from one that read no delayed value at all. |
| Shared with many other contracts (a few hours) | The transaction read *some* delayed value with that delay. The privacy set is every user of every such contract. |
| Unique to one contract | Every transaction with that difference interacts with that contract. The private transfer is now as identifiable as the enqueued public check would have made it. |
| Any value while a change is pending | The expiration equals the scheduled change timestamp, which is public. Transactions that read the variable during the pending window stand out until the change lands. |

The library's own summary is that a delay smaller than every other contract's "might be large enough to uniquely identify those transactions that interact with the contract - fully defeating the purpose of `DelayedPublicMutable`". The recommendation that follows is a delay of at least a couple of hours, with `MAX_TX_LIFETIME` as the optimum from a privacy standpoint.

There is a second-order effect worth noting. Nothing stops a wallet from setting an even lower expiration on purpose, so that a transaction reading a soon-to-change variable does not carry that variable's exact change timestamp. The `PrivateContext` source describes this as something a "sophisticated wallet" should do and observes that wallets deviating from a common convention would in turn reveal which wallet produced each transaction. Expiration timestamps are a fingerprinting surface in their own right, and the delay is only the largest contributor.

## Why it is unsuitable for an emergency pause

Put the two costs together with the pause use case and the two requirements pull in opposite directions. The point of a pause is to stop transfers now; the point of the delay is to guarantee that nothing changes for a while.

Consider the timeline. At `t0` the pause role schedules `paused = true`, effective at `t0 + D`. Every transfer proved against an anchor block before `t0` already carries an expiration no later than `anchor + D`, so those transactions remain includable until their own horizon. Every transfer proved after `t0` reads the pending change, sets its expiration to exactly `t0 + D`, and is includable until then. The flag stops nothing before `t0 + D`. The pause window is the delay, whatever the delay is.

![Pause scheduled at t0 with delay D. Transfers proved before and after t0 stay includable until t0 plus D, the first block where the flag is true and transfers fail]({{site.url_complet}}/assets/article/blockchain/aztec/delayed-pause-timeline-workflow.png)

Shortening the delay does not resolve the conflict; it moves it. A ten-minute delay gives a ten-minute pause window, and in exchange every transfer gets a ten-minute inclusion window and a fingerprint that no other contract is likely to share. Lengthening it to the recommended few hours gives good privacy and comfortable proving time, and a pause that lands hours after the incident. The Aztec.nr documentation draws the conclusion itself: delays "typically on the order of a couple hours, if not days" make the variable "unsuitable for actions that must be executed immediately - such as an emergency shutdown".

Two details make the emergency case worse than the timeline suggests:

- **The delay cannot be shortened in a hurry.** Decreasing it takes as long as the difference, so an operator who set six hours and wants one hour waits five hours before the shorter delay applies, and then a further hour for the pause. Increasing it is immediate, but that is the wrong direction.
- **A pending change is public and self-announcing.** From the moment the pause is scheduled, every transaction reading the flag expires at the same public timestamp. Anyone watching the mempool sees the deadline approaching and can front-load transfers before it.

The alternatives are the ones the first option already gave. If the contract needs a pause that bites within a block, the pause has to be checked in public, and the transaction has to accept that its interaction with the contract is visible.

A hybrid is common in practice, splitting state by how fast it has to change:

- **Routine configuration** that changes rarely and can tolerate a delay lives in `DelayedPublicMutable` and is read privately. Roles, allowlist entries, the issuer of a regulated token and a fee all fit here.
- **A single kill switch** stays in `PublicMutable` and is asserted in an enqueued `#[only_self]` public call.

If that public call already exists because the design updates a public counter, the kill switch costs nothing extra in privacy terms.

## Choosing the delay

Once a contract does use `DelayedPublicMutable`, the delay is a design parameter with consequences in three directions at once, and the three do not agree:

| Direction | Short delay | Long delay |
|---|---|---|
| Reaction time of the flag | Fast | Slow |
| Inclusion window for the sender | Tight; slow provers and congested blocks fail | Comfortable |
| Privacy set of the transaction | Small; likely unique to this contract | Large; at `MAX_TX_LIFETIME`, identical to non-readers |

A few rules follow from the mechanics rather than from taste:

- **Keep one delay per contract.** Every `DelayedPublicMutable` a private function reads sets its own horizon, and the kernel keeps the minimum, so the shortest one governs the whole transaction. Different delays on different flags buy nothing and add fingerprint values. Grouping the flags into one struct, as the library suggests for gate cost, enforces this by construction.
- **Pick a value other contracts use.** The privacy set is shared across contracts with the same delay. A round number of hours that matches the ecosystem's convention is worth more than a value tuned to one contract's operational preference.
- **Treat the delay as a duration, not a block count.** It is in seconds, compared against block timestamps. On a chain with 72-second slots, 360 seconds is five slots, but a period of empty slots or a timestamp jump changes how many blocks that is.
- **Budget the delay against proving time, not just against the flag's reaction time.** The users with the slowest devices are the ones who lose transactions when the window is tight, and they will not know why.
- **Plan the sandbox and test flow around it.** A scheduled change is not readable until the delay has elapsed, and a sandbox clock does not advance on demand, so a six-hour delay in a contract under test needs either a shorter test-only delay or explicit timestamp control in the test harness.

## Conclusion

The rule behind every design here is one sentence: a private function may act on public state only for as long as the protocol can guarantee that state has not changed. The two state variables answer it differently:

- **`PublicMutable`** offers no such guarantee, so private functions cannot read it and must enqueue a public call whose existence is visible.
- **`DelayedPublicMutable`** manufactures the guarantee by postponing every write, and the private read pays for it with an expiration timestamp equal to the postponement.

That timestamp is two things at once: a bound on how long the sender has to get the transaction included, and a public value that clusters transactions by delay. A delay short enough to be useful for a pause is therefore also short enough to strand slow provers and to single out the contract's users.

Configuration that changes rarely belongs in a delayed variable read privately; a switch that must act at once belongs in a public check, with the visibility that entails.

![Mindmap of DelayedPublicMutable on Aztec covering the private read problem, the enqueued public check, the delayed variable mechanics, the expiration and privacy-set costs, and delay selection]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-14-aztec-delayed-public-mutable-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Anchor block** | The already-mined block against whose state root a private function is simulated and proved. Everything the function knows about public state is as of this block. |
| **Historical read** | A proof that a public storage slot held a given value at the anchor block. Available to private functions for any public variable; it says nothing about the current value. |
| **`PublicMutable`** | A public value readable and writable in public functions only. Private functions must enqueue a public call to check it. |
| **`DelayedPublicMutable`** | A public value whose writes are scheduled and take effect only after a delay, which is what allows private functions to read its current value. |
| **Scheduled value change** | The packed record kept by a `DelayedPublicMutable`: the value before, the value after and the timestamp at which the switch occurs. A new schedule replaces a pending one. |
| **Time horizon** | The last timestamp at which a value read at the anchor block is guaranteed to still be current: `anchor + delay` with no pending change, or the scheduled change timestamp otherwise. |
| **`expiration_timestamp`** | A public transaction property; the rollup refuses to include the transaction in a block with a later timestamp. The kernel keeps the minimum requested by any function. |
| **`MAX_TX_LIFETIME`** | The protocol's default expiration, 86,400 seconds after the anchor block. A transaction that reads no delayed value carries exactly this. |
| **Privacy set** | The set of transactions an observer cannot tell apart from a given one. Shared expiration offsets enlarge it; a unique offset shrinks it to the users of one contract. |
| **`#[only_self]`** | Attribute on a public function restricting its caller to the contract itself, used for the public half enqueued by a private function so `msg_sender` is the contract, not the user. |

### Security Implementation Checklist

The properties below hold for any contract that lets a private function read a delayed public value, whatever the value means. Rows are grouped by the decision they constrain.

#### Delay selection

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The delay is at least a couple of hours, or equal to `MAX_TX_LIFETIME` when the flag can tolerate it. | A short delay gives every transaction a tight inclusion window and an expiration offset likely unique to the contract, identifying its users. |
| ☐ | Every `DelayedPublicMutable` read in the same private path shares one delay, preferably by packing the values into one struct. | The shortest delay governs the whole transaction; extra distinct delays add fingerprint values without shortening anything useful. |
| ☐ | The delay matches a value in common use across the ecosystem rather than a contract-specific number. | The privacy set collapses to this contract's users even if the delay is long. |
| ☐ | The delay is budgeted against worst-case client proving time plus expected inclusion latency. | Users on slow devices produce transactions that expire before inclusion and fail with no clear cause. |

#### Flag semantics

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Any switch that must take effect within a block is checked in an enqueued `#[only_self]` public call, not read from a `DelayedPublicMutable`. | An emergency pause takes effect only after the delay; transfers proved before and during the pending window remain includable until then. |
| ☐ | Operators know that a pending change is public and that its timestamp becomes the expiration of every transaction reading the flag. | Users assume a scheduled pause is silent; observers see the deadline and can front-run it. |
| ☐ | Delay decreases are planned with the extra wait equal to the difference between the old and new delay. | A "shorten the delay then pause" plan takes far longer than expected during an incident. |
| ☐ | The uninitialised zero value of the variable is the safe state, or the variable holds an `Option<T>`. | A never-written `DelayedPublicMutable<bool>` reads as `false`; if `false` means "allowed", the check passes before the flag is ever set. |

#### Testing and operations

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Tests advance the chain timestamp past the delay before asserting on a scheduled change, or use a test-only delay. | Tests pass against the pre-change value and never exercise the post-change path. |
| ☐ | The wallet or SDK surfaces the effective expiration to the user before broadcasting. | A transaction expires in the mempool and the user retries with a fresh proof, paying twice. |

## Frequently Asked Questions

**Q: Why can a private function read `PublicImmutable` but not `PublicMutable`?**

Both reads are historical proofs against the anchor block. For `PublicImmutable` the value is written once at initialisation and never again, so the historical value is the current value by construction. For `PublicMutable` the value may have been overwritten between the anchor block and the inclusion block, and the proof cannot rule that out, so the library does not offer the read.

**Q: What exactly does a private read of a `DelayedPublicMutable` add to the transaction?**

Two things: a historical public storage read of roughly 4,000 constraints in the private circuit, and a call to `set_expiration_timestamp` with the time horizon. The expiration is the only externally observable effect; the read itself, like the rest of the private execution, leaves no trace in the public part of the block.

**Q: A pause is scheduled with a six-hour delay. When does the first transfer fail?**

In the first block whose timestamp is at or past `t0 + 6 h`, where `t0` is the timestamp of the block that executed `schedule_value_change`. Until then every transfer, whether proved before or after `t0`, reads `paused = false` and carries an expiration no later than `t0 + 6 h`, so the sequencer can still include it. After that point transfers proved against an anchor block at or past `t0 + 6 h` read `true` and fail in simulation; older ones have expired.

**Q: If the enqueued public check hides `msg_sender` behind `#[only_self]`, what does it leak?**

That this transaction called this contract, plus the function selector and arguments of the public call. The sender's account, the recipient and the amount stay private, but each transfer becomes a countable public event with a block timestamp, which a fully private transfer would not be.

**Q: Why does lowering the delay require a wait, while raising it is immediate?**

Because the guarantee behind every private read is that a value cannot change earlier than one current delay after the anchor block. If the delay could drop from six hours to one hour instantly, a change scheduled right after would land after one hour, inside the six-hour horizon of transactions already proved. Waiting the five-hour difference first means the earliest possible change under the new delay is no earlier than under the old one. Raising the delay only pushes changes later, which cannot invalidate any existing horizon.

**Q: Two contracts in one transaction use delays of 1,000 and 10,000 seconds. What is the expiration, and what does an observer learn?**

The kernel keeps the minimum, so the transaction expires 1,000 seconds after its anchor block. An observer computing `expiration - anchor` sees 1,000 and places the transaction in the privacy set of every contract using that delay. If the 1,000-second contract is the only one with that value, the observer learns that the transaction interacted with it, and learns nothing about the 10,000-second contract.

## References

- [Aztec.nr state variables documentation, DelayedPublicMutable section](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/state_variables#delayedpublicmutable)
- [Aztec.nr contract upgrades documentation, transaction expiration](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/contract_upgrades#transaction-expiration)
- [Aztec.nr API reference, DelayedPublicMutable](https://docs.aztec.network/aztec-nr-api/mainnet/noir_aztec/state_vars/struct.DelayedPublicMutable)
- [AztecProtocol/aztec-nr, `delayed_public_mutable.nr` at v5.2.0](https://github.com/AztecProtocol/aztec-nr/blob/v5.2.0/aztec/src/state_vars/delayed_public_mutable.nr)
- [AztecProtocol/aztec-nr, `public_mutable.nr` at v5.2.0](https://github.com/AztecProtocol/aztec-nr/blob/v5.2.0/aztec/src/state_vars/public_mutable.nr)
- [AztecProtocol/aztec-packages, protocol constants (`MAX_TX_LIFETIME`) at v5.2.0](https://github.com/AztecProtocol/aztec-packages/blob/v5.2.0/noir-projects/noir-protocol-circuits/crates/types/src/constants.nr)
- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [Gates on Aztec — What a Private Function Costs, Where the Cost Hides, and Seven Measured Ways to Lower It]({{site.url_complet}}/2026/09/18/aztec-gate-count-optimization-private-functions/)
- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
- [Partial Notes on Aztec — Deferred Completion and Private DeFi Composability]({{site.url_complet}}/2026/09/09/aztec-partial-notes-private-defi-composability/)
- [AIP-20, the Aztec Token Standard, Compared with ERC-20 and ERC-7984]({{site.url_complet}}/2026/09/11/aip-20-aztec-token-standard-vs-erc-20-erc-7984/)
- [Aztec Contract Standards — AIP-20, AIP-721, ARC-1155, ARC-403, AIP-4626 and the Escrow Standard]({{site.url_complet}}/2026/09/11/aztec-contract-standards-overview/)
- [Aztec: A Privacy-First Layer 2 for Ethereum]({{site.url_complet}}/2025/10/29/aztec-architecture-overview/)
- [Code Reuse in Aztec Contracts — Modules, Traits and Library Crates Instead of Inheritance]({{site.url_complet}}/2026/09/15/aztec-noir-contract-code-reuse-without-inheritance/)
- [Packing Small Values into One Field on Aztec — The Packable Trait, Its Cost and Its Traps]({{site.url_complet}}/2026/09/16/aztec-packable-storage-packing/)
