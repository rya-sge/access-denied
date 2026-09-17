---
layout: post
title: "Packing Small Values into One Field on Aztec — The Packable Trait, Its Cost and Its Traps"
date:   2026-09-16
last_modified_at: 2026-09-17
lang: en
locale: en-GB
categories: blockchain ethereum ZKP
tags: aztec zkp noir smart-contracts gas storage
description: "A derived Packable spends one Field per member. Packing two bools into one saves a slot or a note-hash input, can cost gates, and moves every slot after it."
image: /assets/article/blockchain/aztec/2026-09-16-aztec-packable-mindmap.png
isMath: false
---

[Aztec](https://aztec.network/) is a privacy-focused Layer 2 on Ethereum whose contracts are written in [Noir](https://noir-lang.org/) and compiled, for their private side, into zero-knowledge circuits proved on the user's device; the public side runs on a sequencer with storage slots much like the EVM's. A contract's state therefore has two cost models, one counted in constraints and one in slots, and a storage encoding is measured against both.

A Solidity developer who declares `struct CreditEvents { bool flagDefault; bool flagRedeemed; string rating; }` gets two storage slots without thinking about it: the compiler packs the two `bool`s into one 32-byte word and gives the string its own. The same struct in an Aztec contract written in Noir takes **three** slots, because the framework's default encoding spends one field element per struct member and nothing packs them for you. The tool to get the Solidity layout back is the `Packable` trait, written by hand.

This article explains what `Packable` is and what it is not (it is the storage encoding, distinct from the ABI encoding `Serialize`), where the packed width matters (public storage slots in one cost model, note-hash inputs in another), how to write an implementation and test it, and the two facts that make packing on Aztec different from packing on the EVM: bit arithmetic is not free inside a circuit, so a saving in storage can be a loss in proving; and a change to a struct's packed width moves every storage slot declared after it, which on a deployed contract is a redeployment. A pair of `bool`s next to a short string is the running example.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Two encodings, two purposes

Aztec.nr converts a struct to an array of `Field` elements in two unrelated situations, and gives each its own trait.

**`Serialize` / `Deserialize` is the ABI.** It is used wherever a value crosses the contract boundary: function arguments, return values, events. Its layout must match Noir's intrinsic serialisation — one or more `Field`s per member, in declaration order, nothing compressed — because the TypeScript side encodes arguments with that same intrinsic format. A hand-written `Serialize` on an argument type does not fail to compile; it fails at call time with an "arguments hash mismatch". So this pair is almost always derived, and the `#[event]` macro derives `Serialize` for events on its own.

**`Packable` is the storage encoding.** It is used wherever a value is written to state or hashed into a note: the data type of a `PublicMutable<T>`, `PublicImmutable<T>` or `DelayedPublicMutable<T>`, and the struct behind a `#[note]`. Nothing outside the contract ever sees this layout, so its only obligation is to round-trip: `unpack(pack(x)) == x`. That freedom is what makes packing possible.

The two can, and usually should, differ on the same struct. A struct that is both a function argument and a stored value derives `Serialize`/`Deserialize` (so the ABI stays intrinsic) and implements `Packable` by hand (so storage is compact). Confusing them in the other direction — hand-packing the ABI — is the defect the framework documentation warns about most loudly.

![A struct crosses the contract boundary through Serialize and Deserialize, which must match Noir's intrinsic layout, and reaches storage or a note hash through Packable, whose only requirement is a round trip]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-packable-two-encodings-concept.png)

## What `N` costs, and in which currency

`Packable` carries an associated constant `N`, the length of the `[Field; N]` the struct packs to. A derived implementation sets `N` to the number of members (each `Field`-sized member is one, each sub-`Field` member is also one). Everything a packing saves is expressed in `N`, and the currency depends on where the struct lives.

**Public storage is gas.** For a `PublicMutable<T>`, each element of the packed array is one storage slot: reading is `N` `SLOAD`s, writing is `N` `SSTORE`s, in the AVM's public execution, priced like an EVM L2. Halving `N` halves the storage operations of every read and write. `PublicImmutable<T>` and `DelayedPublicMutable<T>` keep more than the value — the delayed variable stores a scheduled change and a hash and occupies `2N + 2` slots — so a smaller `N` saves more there, and they also require `T: Eq` because they verify the stored value against that hash.

**Note hashes are gates.** A note's hash is Poseidon2 over its packed fields together with the storage slot, the owner and randomness. Fewer packed fields means fewer hash inputs, which is a direct reduction in the gate count of every private function that creates or spends the note — proving time on the user's own device, the scarcest resource on Aztec.

**Calldata is neither.** Function arguments go through `Serialize`, whose layout is fixed; the number of fields in calldata affects L2 gas for deserialisation, and the only lever is the function signature, not the encoding.

The framework's own examples set the scale: a `CardNote { strength: u32, points: u32 }` goes from `N = 2` to `N = 1`; a `GameState { started: bool, round: u32, score: u32 }` from `N = 3` to `N = 1`; a config struct with a `u128`, a `u64` and an address from `N = 3` to `N = 2`, because the address is a full `Field` and cannot share.

## Writing the implementation

The technique is arithmetic, not bit manipulation: multiply by a power of two to shift a value into position, add to concatenate, and reverse with a truncating cast, a subtraction and a division. The framework documents it in four steps.

**1. Determine bit widths.** A `bool` is 1 bit, `u8`/`u16`/`u32`/`u64`/`u128` are their names, a `Field` or an `AztecAddress` is up to 254 bits and cannot share with anything. A `Field` is an integer modulo the BN254 scalar-field prime, which is slightly under 2^254, so a packed group must stay at or below **253 bits** to avoid wrap-around: `u128 + u64 + u32` (224 bits) is safe, two `u128`s (256) are not.

**2. Pack by multiplying with powers of two.** `2.pow_32(k)` is 2^k; `(a as Field) * 2.pow_32(k) + (b as Field)` places `a` above `b`'s `k` bits. Putting the member whose width matches a native integer type in the lowest position lets `unpack` recover it with a plain cast.

**3. Unpack from the lowest bits upward.** Cast to extract the low member, subtract it, divide by the power of two, repeat. A `bool` comes back as a comparison of the remaining field to zero.

**4. Write the round-trip tests**, at ordinary and at boundary values. A hand-written pack is code the derive cannot get wrong; `unpack(pack(x)) == x` is the only check on it.

Applied to the running example, the two flags and the string:

```rust
// ABI: one Field per member (bool, bool, rating) - derived, must match the intrinsic layout.
#[derive(Deserialize, Eq, Serialize)]
pub struct CreditEvents {
    pub flag_default: bool,
    pub flag_redeemed: bool,
    pub rating: FieldCompressedString,   // a 31-byte string in exactly one Field
}

// Storage: the two flags share one Field as bits, the rating keeps the other. N = 2, was 3.
global FLAG_DEFAULT_BIT: u64 = 1;
global FLAG_REDEEMED_BIT: u64 = 2;

impl Packable for CreditEvents {
    let N: u32 = 2;

    fn pack(self) -> [Field; 2] {
        let mut flags: u64 = 0;
        if self.flag_default  { flags = flags | FLAG_DEFAULT_BIT; }
        if self.flag_redeemed { flags = flags | FLAG_REDEEMED_BIT; }
        [flags as Field, self.rating.serialize()[0]]
    }

    fn unpack(fields: [Field; 2]) -> Self {
        let flags = fields[0] as u64;
        Self {
            flag_default: (flags & FLAG_DEFAULT_BIT) == FLAG_DEFAULT_BIT,
            flag_redeemed: (flags & FLAG_REDEEMED_BIT) == FLAG_REDEEMED_BIT,
            rating: FieldCompressedString::deserialize([fields[1]]),
        }
    }
}

#[test]
fn credit_events_round_trip() {
    let rating = FieldCompressedString::from_string("AAA0000000000000000000000000000");
    for d in 0..2 {
        for r in 0..2 {
            let x = CreditEvents { flag_default: d == 1, flag_redeemed: r == 1, rating };
            assert_eq(CreditEvents::unpack(x.pack()), x);
        }
    }
}
```

Two details of the example are deliberate. The flags use bit masks on a `u64` rather than `2.pow_32(k)` arithmetic because there are only two of them and a reader sees the layout at a glance; both forms are valid, and both are cheap in the AVM. And the string is already one `Field` — `FieldCompressedString` packs up to 31 bytes into a single element, which is where Noir does *better* than Solidity, whose `string` is unbounded and spills into further slots once it passes 31 bytes. Noir is worse on the flags and better on the string.

![Packing two flags and a compressed string: the derived layout spends one Field per member for N of 3; the hand-written layout puts both flags as bits in Field 0 and the string in Field 1 for N of 2; the ABI keeps three fields either way]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-packable-layout-workflow.png)

## Where the packed value is used, and why nothing else changes

The packing is invisible at the call site. `PublicMutable::write(value)` calls `value.pack()` and stores `N` slots; `read()` loads `N` slots and calls `unpack`. The functions that set and get the struct look exactly as they did with the derived implementation:

```rust
#[external("public")]
fn set_credit_events(events: CreditEvents) {          // argument: Deserialize, 3 fields
    self.storage.credit_events.write(events);         // storage: Packable, 2 slots
}

#[external("public")]
#[view]
fn get_credit_events() -> pub [Field; 3] {
    self.storage.credit_events.read().serialize()     // return: Serialize, 3 fields
}
```

The ABI is untouched — the getter still returns three fields, the setter still takes the three-member struct, the TypeScript bindings do not change — and the storage footprint drops from three slots to two. That separation is the whole reason the two traits exist.

## The two facts that make this different from the EVM

Solidity packs storage automatically, and packing there is almost always a win. On Aztec neither holds, and both differences have caught reviewers who applied EVM intuition.

### Packing is not free inside a circuit

The same `pack` and `unpack` code is priced differently in the two execution contexts:

- **In public execution** the arithmetic is a few AVM opcodes, and the `SLOAD` it saves dominates. Packing pays.
- **In private execution** the same arithmetic is constraints in a circuit, paid in the user's proving time. And a read of a `DelayedPublicMutable` value already comes with a hash check over the whole packed value, so the extra field a packing would remove is nearly free to read.

A measured case makes the point:

- A two-`bool` flag struct held in a `DelayedPublicMutable` and read on a private transfer path was hand-packed from `N = 2` to `N = 1`, exactly as the sibling struct next to it already was.
- The private transfer became **7 gates more expensive**, not cheaper: unpacking two bits from one field cost marginally more than reading one additional field out of the already-hashed value.
- Seven gates against a 120,000-gate function is nothing either way, and the public-storage saving was real (and unmeasured).
- The sign of the prediction was still wrong, and the change was declined: it also moved storage slots (the second fact below) for no private benefit.

The rule that follows: **measure per context, and state which one a packing claim is about.** `aztec profile gates` gives the private cost per function; a packing that helps a `PublicMutable` read in a public setter says nothing about a `DelayedPublicMutable` read in a private transfer. A struct that is written rarely in public and never read in private, like the credit events above, is the clean case where packing is pure saving.

### Changing `N` moves every slot after it

The chain from a packing change to a broken deployment has four links:

- **Slots are allocated in declaration order.** The `#[storage]` macro walks the storage struct and gives each state variable as many consecutive slots as its packed length needs. Changing a struct's `Packable::N` therefore shifts every state variable declared after it.
- **Public state is orphaned.** The values written at the old slots are still there, but the contract now reads and writes different slots; from its point of view the state is gone.
- **Private state is worse: existing notes become unspendable.** The storage slot is an input to every note hash, and the note hash to every nullifier. A note created under the old slot no longer matches what the contract computes, so it can neither be found nor nullified.
- **There is no fix in place.** Aztec has no storage-layout compatibility tooling, and contract upgrades are a low-level protocol feature the `#[aztec]` macros are not built around. On a deployed contract a packing change is a redeployment and a holder migration, not a patch.

In the running example the credit-events struct sat *before* the private balance set in the storage struct, so the `N = 3 → 2` change moved the balance slot by one. The change was correct and the saving real, and it still waited a full release: it landed only in a version that was already breaking storage for other reasons and had no deployed instance to migrate. That is the right way to schedule a packing change on a live contract — fold it into a break that is happening anyway, never cause one for it.

Two smaller consequences of the slot rule: append new state variables at the **end** of the storage struct, so nothing existing moves; and treat a `#[storage_no_init]` struct, whose slots are hand-written to pin a layout, as a hard stop for any packing change.

## When to pack, and when not to

Worth it when a struct has several sub-`Field` members (`bool`s, small integers) and is stored or noted; when it is read or written often; when a public function is hitting gas limits; when it is a note, because every packed field is a hash input on the private path.

Not worth it when every member is already a `Field` or an address (nothing to pack); when the struct only ever crosses the ABI (that is `Serialize`, whose layout is fixed); when the struct is small and rarely touched and the contract is already deployed (the slot move costs more than the slot); and, the Aztec-specific case, when the struct is read on a private hot path and the measurement says the arithmetic costs more than the field it saves.

The framework adds a derive only where the struct's role strictly requires it, so what each macro does and does not derive is worth keeping at hand:

| Macro or type | Derives | Requires, without adding it |
|---|---|---|
| `#[event]` | `Serialize` | — |
| `#[note]` | nothing | `Packable` (the macro fails compilation without it) |
| `#[storage]` | nothing | `Packable` on every state variable's data type |
| `PublicImmutable<T>`, `DelayedPublicMutable<T>` | nothing | `Packable` and `Eq` (they verify the stored value against a hash) |
| `PublicMutable<T>` | nothing | `Packable` only |

A missing derive fails to compile with a clear message. An over-broad one (`Packable` on an event, `Deserialize` on a note that never crosses the boundary) is noise rather than a defect.

## Conclusion

`Packable` is the storage encoding of an Aztec contract, separate from the `Serialize` ABI encoding that must stay intrinsic. Its associated `N` is the number a packing changes: storage slots in public functions, note-hash inputs in private ones.

- A **derived** implementation spends one `Field` per member.
- A **hand-written** one concatenates sub-`Field` members with powers of two or bit masks, within 253 bits, and is checked by a round-trip test.

Two facts separate the technique from its Solidity counterpart, where the compiler packs for free and packing always wins:

- **Arithmetic inside a circuit has a cost**, and it can exceed the field it saves; every packing claim is measured in the context it applies to, public gas or private gates.
- **A change of `N` moves every slot declared after the struct.** On a deployed contract that invalidates notes and forces a migration, so the change is scheduled with a storage break, never as one.

![Mindmap of Packable on Aztec covering the two encodings, what N costs in public storage and in note hashes, the four steps of a hand-written implementation, the circuit-cost and slot-move traps, and when packing is worth it]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-16-aztec-packable-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **`Field`** | Noir's native element: an integer modulo the BN254 scalar-field prime, just under 2^254 bits. The unit of storage slots, note-hash inputs and ABI encoding. |
| **`Packable`** | The trait giving a type its storage encoding: `pack() -> [Field; N]` and `unpack`. Internal to the contract; must only round-trip. |
| **`Serialize` / `Deserialize`** | The ABI encoding for arguments, return values and events. Must match Noir's intrinsic layout; hand-rolling it on an argument fails at call time. |
| **`N`** | `Packable`'s associated constant, the packed length. Slots for public state, hash inputs for notes; the quantity a packing reduces. |
| **Derived implementation** | `#[derive(Packable)]`: one `Field` per member, sub-`Field` members included. Correct by construction, wasteful for small members. |
| **Bit packing** | Placing several sub-`Field` values in one `Field` by multiplying with powers of two (or masking bits) and adding; reversed by cast, subtract, divide. |
| **253-bit limit** | The safe total width of one packed `Field`, below the prime, so concatenation never wraps around. |
| **Round-trip test** | `assert_eq(T::unpack(x.pack()), x)` at ordinary and boundary values; the only check on a hand-written packing. |
| **Storage slot** | The position a state variable occupies, allocated sequentially by `#[storage]` in declaration order and by packed length; an input to every note hash under it. |
| **`DelayedPublicMutable`** | A public value readable from private functions after a delay; stores the value, a scheduled change and a hash in `2N + 2` slots, so `N` weighs more there. |

### Security Implementation Checklist

#### Encoding choice

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every struct used as a function argument, return value or event uses a **derived** `Serialize` / `Deserialize`. | A hand-rolled ABI layout produces an "arguments hash mismatch" at call time, after deployment, not at compile time. |
| ☐ | Storage and note types implement `Packable`; the derive is placed before `#[note]` or a manual impl is provided. | `#[note]` and `#[storage]` do not add it; the build fails, or a later "fix" hand-rolls the wrong trait. |
| ☐ | `PublicImmutable<T>` and `DelayedPublicMutable<T>` data types also implement `Eq`. | The hash verification these variables perform cannot compile. |

#### Packing correctness

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The total bit width of members sharing one `Field` is ≤ 253. | Values wrap around the field modulus; `unpack` returns wrong values silently. |
| ☐ | `unpack(pack(x)) == x` is tested for every flag combination and at each integer member's maximum. | A wrong shift or mask corrupts stored state or, in a note, produces a note whose hash no longer matches its content. |
| ☐ | Members that share a `Field` have disjoint bit ranges, asserted by a test that sets one at a time. | Two members overwrite each other; the round trip on a single value may still pass. |

#### Layout and deployment

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | A change to any stored struct's `N` is treated as a storage-layout change: shipped only with a redeployment, never as an upgrade of a live contract. | Every state variable after the struct moves; public state is orphaned and, for private state, every existing note becomes unspendable. |
| ☐ | New state variables are appended at the end of the storage struct. | Inserting one anywhere else re-slots what follows. |
| ☐ | `#[storage_no_init]` layouts are never changed by a packing edit. | Hand-pinned slots silently diverge from the code that reads them. |
| ☐ | A packing on a private read path is measured with `aztec profile gates` before and after, and the claim names the context (public gas or private gates). | The arithmetic can cost more gates than the field it saves; a "saving" becomes a regression on the user's proving time. |

## Frequently Asked Questions

**Q: If `Packable` is arbitrary, why not pack the ABI too and shrink calldata?**

Because the ABI layout is not the contract's to choose. Arguments are encoded by the caller — the TypeScript client, another contract's generated interface — in Noir's intrinsic format, and the callee's `Deserialize` must agree with it. A hand-rolled `Serialize` compiles and then fails every call with an "arguments hash mismatch". Calldata size is reduced by changing the function signature, not the encoding.

**Q: A `PublicMutable<bool>` and a `PublicMutable<u64>` sit next to each other in storage. Does the framework pack them like Solidity would?**

No. Each state variable is allocated its own slots from its own `Packable::N`; two neighbouring variables never share a slot. To pack them you put both members in one struct with a hand-written `Packable` and hold that struct in one state variable, which changes the type of the variable, and so the layout.

**Q: Why did hand-packing two `bool`s make a private function *more* expensive?**

Because the struct was read from a `DelayedPublicMutable` in a private function, and that read does not pay per field. The private read proves one storage slot — the hash of the whole value — and re-hashes the preimage in-circuit to check it; a second field is one more input to a hash the circuit computes anyway, a few gates. Recovering two `bool`s from one packed `Field` costs more than that: a cast to an integer (a range check), two bit masks (bit decomposition) and two comparisons. Net effect in the measured case: **+7 gates** on a 120,000-gate transfer, negligible but with the opposite sign to the prediction. The public write of the same struct did save storage operations. Measure per context and say which one the claim is about.

**Q: How can a `DelayedPublicMutable` read in private cost "almost nothing" per extra field, when a public storage read costs thousands of gates?**

A private function cannot read current public storage; it proves a *historical* read against the anchor block, with a Merkle inclusion path into the public data tree, at roughly 3,500–4,000 gates per slot proven. If a struct were stored as `N` plain slots, a private read would need `N` such proofs. `DelayedPublicMutable` avoids that with `WithHash`: the public write stores the `N` packed fields *plus* a Poseidon2 hash of all of them in one extra slot. The private read then proves the inclusion of **that one slot only**, fetches the `N`-field preimage from an oracle (unconstrained), and re-hashes it in the circuit to assert it matches the proven hash. The cost is therefore one inclusion proof, independent of `N`, plus one hash whose cost grows by a handful of gates per additional field. That is why packing two fields into one saves almost nothing on the private read, and why the unpacking arithmetic can outweigh it. On the public side the same variable is stored as `2N + 2` slots (current and scheduled value, the delay change and the hash), so `N` from 2 to 1 turns six `SSTORE`s into four on every scheduled write: a real saving, in gas, on the sequencer, which the private measurement says nothing about.

**Q: A struct's `N` goes from 3 to 2. What exactly breaks on a deployed contract?**

Every state variable declared after it in the storage struct is now one slot earlier. Public values at the old slots are no longer read; for private state the slot is an input to every note hash and every nullifier, so notes stored under the old slot can no longer be found or spent. There is no in-place fix: it is a redeployment and a migration of holders, which is why such a change is scheduled with a storage break that is happening anyway.

**Q: Two `u128`s in one struct: can they share a `Field`?**

No. 128 + 128 = 256 bits exceeds the 253-bit safe width of a `Field`, whose modulus is just under 2^254; the sum would wrap around (the next question explains why the limit is not 256). A `u128` and a `u64` (192 bits) can share; the second `u128` needs its own `Field`. `N` for the pair is 2 either way, so there is nothing to gain by trying.

**Q: Why is the safe width 253 bits and not 256? A Solidity word is 256 bits.**

Because a `Field` is not a 256-bit machine word. It is an element of the scalar field of the BN254 curve, the curve Aztec's proving system is built on, so a `Field` value is an integer **modulo a prime** `p ≈ 2^253.58`, and the representable range is `0 … p − 1`. Three things follow:

- **The modulus cannot be 2^256, or any power of two.** The field must be a prime field for the curve arithmetic and the pairings to work, and a prime is never a power of two; `p` is what the BN254 construction produced, not a chosen bit length.
- **`p` has 254 bits, but not every 254-bit value fits.** `p` lies between 2^253 and 2^254, so a value with 254 significant bits may be at or above `p` and is reduced modulo `p`. Every value below 2^253 is below `p`, which makes 253 bits the largest power-of-two range that is always representable.
- **Reduction is silent.** Two `u128`s concatenated into one `Field` (256 bits) would store `value − p` for any value at or above `p`, and `unpack` would return different members than were packed. Nothing fails at compile time or at call time; the stored state is quietly wrong.

A Solidity `uint256` really is 256 bits with wrap-around at 2^256, so two 128-bit values do fit in one EVM word. On Aztec the "word" is about 2.4 bits shorter, which is enough to make the same packing unsafe.

**Q: A struct has two `bool`s and one `AztecAddress`. What is the best `N`, and what does the round-trip test need?**

`N = 2`: the two flags in one `Field`, the address in the other, since an address is a full `Field` and cannot share. The test enumerates all four flag combinations with a fixed address and asserts `unpack(pack(x)) == x`, plus one case per flag alone to show the two bits are disjoint. With only `bool`s, there is no "maximum value" case to add.

## References

- [Aztec.nr — Data packing and serialization](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/data_packing)
- [Aztec.nr — State variables](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/state_variables)
- [Aztec.nr — Writing efficient contracts](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/advanced/writing_efficient_contracts)
- [Aztec.nr API — `Packable` trait](https://docs.aztec.network/aztec-nr-api/mainnet/noir_aztec/protocol/traits/trait.Packable)
- [Aztec packing example contract, v5.2.0](https://github.com/AztecProtocol/aztec-packages/blob/v5.2.0/docs/examples/contracts/packing_example/src/types.nr)
- [Noir — Data types](https://noir-lang.org/docs/noir/concepts/data_types)
- [Solidity — Layout of state variables in storage](https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html)
- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [Code Reuse in Aztec Contracts — Modules, Traits and Library Crates Instead of Inheritance]({{site.url_complet}}/2026/09/15/aztec-noir-contract-code-reuse-without-inheritance/)
- [Reading Public State from a Private Function on Aztec — Why a Pause Flag Comes with a Delay]({{site.url_complet}}/2026/09/14/aztec-delayed-public-mutable-pause-privacy-delay/)
- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
- [Solidity Gas Optimization Cheatsheet]({{site.url_complet}}/2023/09/27/gas-optimization/)
