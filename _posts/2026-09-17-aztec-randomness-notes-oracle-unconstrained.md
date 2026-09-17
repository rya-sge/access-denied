---
layout: post
title: "Randomness on Aztec — One Oracle, Four Uses, and Why the Circuit Never Checks It"
date:   2026-09-17
lang: en
locale: en-GB
categories: blockchain ethereum ZKP
tags: aztec zkp noir privacy smart-contracts cryptography
description: "Every random value in an Aztec contract comes from one unconstrained oracle backed by the client's CSPRNG: what it blinds, its limits, and why that is safe."
image: /assets/article/blockchain/aztec/2026-09-17-aztec-randomness-mindmap.png
isMath: false
---

[Aztec](https://aztec.network/) is a privacy-focused Layer 2 on Ethereum. A contract there has a private side, executed on the user's device inside a zero-knowledge proof over encrypted *notes* that only their owner can read, and a public side executed by a sequencer; what the chain itself stores of the private side is commitments, hashes of data it never sees. [An earlier article]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/) covers that execution model; this one looks at one ingredient of those commitments.

An Aztec contract publishes hashes, not data. A private balance is a set of note hashes in a Merkle tree; a private event is a commitment in the nullifier tree; a message to a recipient is a ciphertext in a log. Each of those is public, and each is a function of values drawn from small sets: an address that appears in a known list, an amount below a few million units, a storage slot that the contract's layout fixes. A hash of small inputs is not hiding at all, because anyone can enumerate the inputs and compare. What makes the published commitments opaque is a blinding value mixed into every one of them, and that value has to come from somewhere.

On Aztec it comes from exactly one place: an oracle called `random()`, answered by the client software with a field element from the operating system's random number generator. The framework calls it when it creates a note, when it emits a private event, when it generates the ephemeral key that encrypts a message, and when it pads a ciphertext. The client libraries call the same generator for deployment salts, account salts, transaction nonces and bridge secrets. And in none of these places does the zero-knowledge proof check that the value was random. The `unsafe` block around every call is not an oversight; it follows from who knows what.

This article traces the value from the Noir call to the bytes it is made of, lists what it protects and what it does not, separates it from the two other values a note carries (the nonce and the nullifier) that are often confused with it, and explains why an unconstrained random value is acceptable in a system built on constraining everything. The [AIP-20](https://docs.aztec.network/developers/docs/aztec-nr/standards/aip-20) token is the worked example throughout. Two limits close it: public functions have no randomness at all, and a randomness reused across two partial notes links them.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why a private chain needs a blinding value

The randomness problem the EVM is known for is a different problem: a public contract that wants an unpredictable number (a lottery draw, a validator selection) has no source of one, because everything a public contract can read is also readable, and often influenceable, by whoever it is drawing against. Beacon-chain `prevrandao` and oracle networks such as Chainlink VRF exist to fill that gap.

Aztec has that gap too, and this article returns to it at the end. But the randomness that Aztec consumes in bulk is of the other kind: **client-side blinding**. The chain stores commitments, and a commitment `H(x)` hides `x` only if `x` cannot be guessed. Consider the inputs of an AIP-20 balance note without any blinding:

- the **owner** is an `AztecAddress`, and account deployments are public, so the candidates number in the thousands rather than 2^254;
- the **value** is a `u128`, but a real balance is a number of units that a search can cover in seconds;
- the **storage slot** is a constant of the contract's layout.

An observer with the token's source, the note hash tree and a list of deployed accounts could compute `H(slot, owner, value)` for every `(owner, value)` pair and learn every balance on the chain. The remedy is the standard one from commitment schemes: add a field `r` drawn uniformly from the whole scalar field, so that the preimage space has 2^254 members per guess and enumeration is hopeless. Every public artefact of a private operation on Aztec carries such an `r`. The rest of the article is about where it comes from and where it goes.

## One oracle, traced to the bytes

The framework has a single source. In aztec-nr v5.2.0 (`aztec/src/oracle/random.nr`):

```rust
/// Returns an unconstrained random value. Note that it is not possible to constrain this value to
/// prove that it is truly random: we assume that the oracle is cooperating and returning random
/// values. In some applications this behavior might not be acceptable and other techniques might
/// be more suitable, such as producing pseudo-random values by hashing values outside of user
/// control (like block hashes) or secrets.
pub unconstrained fn random() -> Field {
    rand_oracle()
}

#[oracle(aztec_misc_getRandomField)]
unconstrained fn rand_oracle() -> Field {}
```

An **oracle** in Noir is a call that leaves the program: the circuit records that a value was requested, the host process running the simulation supplies one, and execution continues with it as a witness. The function is `unconstrained` because nothing about the returned value is proven, and every call site wraps it in `unsafe { random() }` for the same reason. The Aztec docs state the general rule for oracles: any information injected through one "is later constrained for correctness", otherwise the circuit is under-constrained. Randomness is the deliberate exception, and the reason is the subject of a later section.

![Sequence of a random draw: the Noir contract calls the random oracle, the PXE answers with Fr.random from 64 CSPRNG bytes reduced modulo the field, and the value flows into the note hash and the message to the recipient]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-randomness-oracle-sequence.png)

On the host side the chain is short. The PXE's oracle handler (`@aztec/pxe`, `utility_execution_oracle.js`) and the TXE used by `aztec test` both implement `getRandomField()` as `Fr.random()`. In `@aztec/foundation` that is `fromBufferReduce(randomBytes(64), Fr)`: sixty-four bytes, 512 bits, interpreted as an integer and reduced modulo the BN254 scalar field order `r` (about 2^254). Because the input is roughly 258 bits wider than the modulus, the reduction bias is of the order of 2^-258 and irrelevant. `randomBytes` is `@aztec/bb.js`'s wrapper around Node's `crypto.randomBytes` on the server and the Web Crypto API in a browser, both operating-system CSPRNGs.

One switch sits in that path and matters for anyone running tests or a sandbox. If the environment variable `SEED` is set, `@aztec/foundation`'s `RandomnessSingleton` replaces the CSPRNG with a deterministic counter-based generator so that test runs are reproducible. The source carries a `TODO(#3949)` saying this "is not safe enough for production and should be made safer or removed before mainnet". A deployment that inherits a `SEED` from a CI configuration would generate every note blinding, every ephemeral encryption key and every deployment salt from a predictable sequence.

Three properties of the value follow from this construction, and every later section relies on one of them:

- **Uniform over the field.** Not a 128-bit value padded, not a hash of a counter. Guessing it is a 2^254 search.
- **Generated on the creator's device, invisible to the chain.** No sequencer, no other user and no contract sees it directly; it appears on the chain only inside hashes and ciphertexts.
- **Not reproducible by anyone else.** Unlike a key-derived value, nobody can recompute it later, which is why every use below is paired with a delivery of the value to whoever will need it.

## Where the framework spends it

Outside its own tests, aztec-nr calls the oracle of the previous section, and only it, from nine places in eight files; every one of them imports `crate::oracle::random::random`, and the framework has no second random function. Eight of the nine fall into four uses and one fallback, listed below; the ninth is an internal handle for an unconstrained scratch array and touches nothing on chain. The TypeScript client draws from the same generator, `Fr.random()`, but directly rather than through the oracle, and that family closes the section.

| Use | Call site (aztec-nr v5.2.0) | What the value does |
|---|---|---|
| **Note blinding** | `note/lifecycle.nr` `create_note`; `uint-note` `UintNote::partial` | Enters the note hash as `H(owner, r)`; hides owner and value from anyone reading the tree |
| **Private event blinding** | `event/event_emission.nr` `emit_event_in_private` | Enters the event commitment, which is pushed to the nullifier tree; prevents preimage attacks and, because two equal nullifiers are rejected, prevents two identical events from colliding |
| **Ephemeral encryption keys** | `keys/ephemeral.nr` `generate_ephemeral_key_pair` | Becomes the ephemeral secret scalar of the ECDH exchange that encrypts a note or event message to its recipient |
| **Ciphertext padding** | `messages/encryption/aes128.nr` | Fills the unused fields of a fixed-length ciphertext so that padding is indistinguishable from masked content |
| **Undiscoverable tag fallback** | `messages/delivery/tag_derivation.nr`, `oracle/resolve_tagging_strategy.nr` | When an unconstrained message is addressed to an invalid recipient, a random tagging secret produces a tag nobody can find, instead of aborting the send |

The first two are the ones this article is about; the others are worth a sentence each.

**Ephemeral keys.** Each message to a recipient is encrypted with a shared secret derived from a fresh ephemeral key pair and the recipient's public key. The key pair lives on **Grumpkin**, the elliptic curve Aztec uses for every account key: nullifier keys, viewing keys, tagging keys and the ephemeral keys of message encryption are all Grumpkin scalars, and the corresponding public keys are Grumpkin points. Grumpkin is the curve *embedded* in BN254, the curve the proofs are made over, and the two are defined so that their fields cross: Grumpkin's points have coordinates in `Fr`, the BN254 scalar field that every Noir `Field` belongs to, while Grumpkin's own scalars, the values a point is multiplied by, live in `Fq`, the BN254 base field. That crossing is what makes elliptic-curve arithmetic cheap inside a circuit: adding two Grumpkin points is native `Field` arithmetic, with no emulation of a foreign field. The price is that a Grumpkin scalar does not fit in a `Field`, since `Fq` is slightly larger than `Fr`; Noir's `EmbeddedCurveScalar` therefore carries it as two 128-bit limbs, `lo` and `hi`.

The ephemeral secret is `EmbeddedCurveScalar::from_field(random())`, and this is where the framework notes a `@todo`: `random()` returns a `Field`, an element of `Fr`, so the scalar it becomes is always below `r` and the values between `r` and `q` are never drawn. The excluded range is `q − r`, about 2^127 keys out of about 2^254, a fraction near 2^-127 of the key space. That is a uniformity remark, not a weakness an attacker can use. The library's tests mock the oracle to return `0` and check that the resulting key is rejected ("point at infinity"), which is the one degenerate value the code guards against.

**Padding.** A ciphertext has a fixed length, and the content fields are masked with Poseidon2-derived values so they look uniformly random. Padding the remainder with zeros would reveal the length of the content; padding it with `random()` makes a two-field message and a ten-field message indistinguishable.

**Client-side salts and nonces.** `aztec.js` and the wallet packages call `Fr.random()` for a contract deployment salt (`DeployMethod`), an account salt (`AccountManager`), the `txNonce` of a transaction and of a fee payment authwit, and the secret behind an L1-to-L2 claim (`generateClaimSecret`); that secret's hash goes to L1 and its preimage is consumed on L2. The transaction request itself carries a `salt` "to make the transaction request hash difficult to predict", because that hash is used as the transaction's first nullifier when the transaction emits none. These are unpredictability uses rather than hiding uses, but they draw from the same generator and are subject to the same `SEED` caveat.

## Three values in a note that are not the same thing

A completed note on Aztec involves three values that new readers tend to merge into one "random nonce". They come from three different parties and protect three different things.

![Concept: the client-drawn randomness blinds the note hash, the protocol-derived nonce makes the tree leaf unique, and the owner-key-derived nullifier marks the spend; three sources, three properties]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-note-randomness-nonce-nullifier-concept.png)

**Randomness `r`** is the client-side blinding value from the previous sections. For a `UintNote` it enters in two rounds:

```
partial_commitment = H(owner, r)                    // DOM_SEP__PARTIAL_NOTE_COMMITMENT
note_hash          = H(storage_slot, partial_commitment, value)   // DOM_SEP__NOTE_HASH
```

The two-round form is what lets a partial note fix `(owner, r)` first and `value` later; an ordinary note runs both rounds at once. `r` is chosen by whoever creates the note, which for a transfer is the **sender**, and is delivered to the owner inside the encrypted note message. The owner needs it to recompute the note hash, to prove membership when spending, and to compute the nullifier.

**The note nonce** is not random and is not chosen by anyone. The protocol derives it from the transaction:

```
note_nonce       = H(first_nullifier_in_tx, note_index_in_tx)   // DOM_SEP__NOTE_HASH_NONCE
siloed_note_hash = H(contract_address, note_hash)
unique_note_hash = H(note_nonce, siloed_note_hash)              // the leaf in the tree
```

Its job is uniqueness. Two notes with identical `(owner, r, slot, value)` would have identical note hashes, and a tree cannot hold two identical leaves with distinct nullifiers; the nonce, unique because the first nullifier of every transaction is unique, separates them. Since every input to the nonce is public, the nonce hides nothing, which is exactly why `r` is still needed: without `r`, the leaf `H(nonce, H(contract, H(slot, H(owner), value)))` has a fully enumerable preimage.

**The nullifier** is derived from the owner's nullifier secret key and the note's unique hash: `H(note_hash_for_nullification, nsk_app)`. It is what the owner publishes when spending. Its unlinkability to the note comes from the secret key, not from `r`; an observer who knew `r` and the whole note preimage still could not compute the nullifier without `nsk_app`. Conversely, the owner could spend a note whose `r` was badly chosen; a poor `r` weakens privacy, never ownership.

The AIP-20 `transfer_private_to_private(from, to, amount, nonce)` shows all three at once. The sender's `BalanceSet` spends some of the sender's notes, publishing one nullifier each (owner key). It creates two new notes, a change note for the sender and a payment note for the recipient, each with its own fresh `r` from the oracle (two `create_note` calls, two draws). The protocol assigns each a nonce from the transaction's first nullifier and its position. Neither recipient nor observer can relate the two new leaves to each other or to the spent ones.

## Why the proof does not check it

A system that constrains every state transition leaves one value unconstrained. The justification appears verbatim, four times, in the aztec-nr source, and the version in `create_note` reads:

> We use the randomness to preserve the privacy of the note recipient by preventing brute-forcing, so a malicious sender could use non-random values to make the note less private. But they already know the full note pre-image anyway, and so the recipient already trusts them to not disclose this information. We can therefore assume that the sender will cooperate in the random value generation.

The argument is about **who is harmed and who could harm**. The party that chooses `r` is the party that creates the note, and that party knows the entire preimage: it chose the owner, the value and the slot. A sender who wants the recipient's balance exposed does not need to pick `r = 0` and let an observer brute-force it; it can post the preimage. Constraining `r` to be "random" would protect the recipient against a sender who is already in a position to reveal everything by other means, so the constraint would buy nothing.

The same reasoning covers the other three uses. A sender who wants a message's plaintext public can publish it, so the ephemeral key and the padding need no constraint either; the emitter of a private event knows the event, so neither does the event commitment.

What *is* constrained is **consistency**. The circuit computes the note hash from whatever `r` the oracle returned and pushes that hash; the same `r` goes into the message the sender is obliged to deliver. If a sender delivers an `r` that does not match the hash in the tree, the recipient's PXE recomputes the hash from the received preimage, fails to find it, and discards the note. The sender has then paid without the recipient receiving; it has hurt itself. And the value is used exactly once per note, because it is drawn per `create_note` call.

Two situations sit outside the argument and are worth naming:

- **A contract as note creator.** When a contract computes a note for a user, the "sender" is the contract's code executing on the caller's device, and the caller controls the oracle. A DeFi protocol that returns a note to a counterparty is, in the framework's trust model, the counterparty's own execution choosing `r` for a note it will own; the party whose privacy `r` protects and the party who chose it are again the same, or in a relationship where the chooser already knows the preimage.
- **A recipient who did not choose.** For a partial note, the recipient chooses `r` (it calls `initialize_transfer_commitment` and its device draws the value) and the sender only learns `H(owner, r)`. The trust runs the other way, and the sender's privacy is not what `r` protects, so nothing changes.

The framework's own docstring on `random()` names the alternative for applications where an unconstrained draw is not acceptable: pseudo-random values derived by hashing values outside the user's control, such as block hashes, or secrets. That is a different tool for a different need, the one the next section is about.

## What a public function can and cannot do

Public functions run in the AVM on the sequencer, and the Aztec docs are direct about the consequence for oracles: "In public execution, oracles aren't available since the sequencer runs the code." There is no `random()` in a public function; the call does not exist in that context. The sequencer executes deterministically so that every node can re-execute and agree.

Nor does the protocol offer, at 5.2.0, a randomness beacon or a VRF a public function could read. A public function that needs an unpredictable value has the options the EVM has, minus `prevrandao`:

- **receive it from a private function**, which drew it from the caller's oracle and passes it as an argument of the enqueued public call; the value is then the caller's choice, which is acceptable when the caller is the party the unpredictability protects (a commitment the caller will later open) and not when it is the party being drawn against (a lottery entrant choosing its own draw);
- **commit-reveal across transactions**, where several parties commit to hidden values and the public function combines the reveals;
- **an external oracle contract**, none of which is part of the protocol.

The distinction to keep is that Aztec's `random()` is a *privacy* primitive for the party calling it, not a *fairness* primitive between parties. A contract that lets a user's private function draw the number that decides whether that user wins has let the user pick the outcome.

## Partial notes: the randomness the sender never sees

The [AIP-20](https://docs.aztec.network/developers/docs/aztec-nr/standards/aip-20) commitment flow is the one place in the standard where `r` is created by one party and completed by another, and it makes the properties of the previous sections visible.

The recipient calls `initialize_transfer_commitment(to, completer)`. Its device draws `r`, computes `C = H(to, r)`, sends itself the pair `(to, r, C)` as a private message so its PXE registers a *pending* partial note, and pushes a validity commitment `H(C, completer)` to the nullifier tree. The recipient then hands `C` to the payer. The payer's `transfer_private_to_commitment(from, C, amount, nonce)` completes the note: it checks that `H(C, msg_sender)` exists, emits a completion log tagged `H(C)` with `[slot, amount]` in clear, and pushes `H(slot, C, amount)` as a note hash. The payer never learns `r` and never learns `to`; `C` is all it holds.

Two consequences follow from `r` being a one-shot, undeliverable value:

- **The commitment is single-use.** The completion log's tag is `H(C)`; a second payment into the same `C` carries the same tag, which publicly links the two payments as going to one recipient, and the recipient's PXE, having matched the first completion and removed the pending entry, does not discover the second. The Aztec docs' *Single-use semantics* section states both effects, and the library's docstring on `UintNote::partial` gives the privacy half: "Each partial note should only be used once, since otherwise multiple notes would be linked together and known to belong to the same owner." A recipient who expects several payments creates several partial notes, each with its own draw.
- **Losing the pending message loses the note.** Because `r` is random rather than derived from the recipient's keys, a recipient whose PXE state is lost cannot reconstruct `(to, r)` from `C`, even though the note is provably its own. The value exists in exactly one place until completion.

A comparison with the ordinary transfer closes the loop: in `transfer_private_to_private` the *sender* draws `r` and delivers it; in the commitment flow the *recipient* draws it and keeps it. In both cases the party that draws is the party whose privacy the draw protects or a party that already knows the preimage, which is the condition under which leaving `r` unconstrained is safe.

## Testing with and without randomness

Two facilities exist for tests that need to control the value.

The TXE behind `aztec test` answers `getRandomField` with the same `Fr.random()` as the PXE, so tests see fresh values by default, and two runs never produce the same note hashes. Setting `SEED` makes the whole `@aztec/foundation` generator deterministic for a run, which is how reproducible test transcripts are obtained; it is the same switch that must never reach production.

Inside Noir, `std::test::OracleMock` intercepts a named oracle. The library's own test for ephemeral keys is the model:

```rust
#[test(should_fail_with = "point at infinity")]
unconstrained fn generate_positive_ephemeral_key_pair_rejects_zero_randomness() {
    // Making the randomness oracle return 0 emulates a malicious sender substituting eph_sk = 0.
    let _ = OracleMock::mock("aztec_misc_getRandomField").returns(0);
    let _ = generate_positive_ephemeral_key_pair();
}
```

The same mock lets a contract test pin the randomness of a note to a known value, so that a note hash or a partial commitment can be asserted against a constant rather than recomputed. It is also how a test can exercise the "malicious sender" branch of the trust argument and check that the worst a bad `r` does is what the framework claims.

## Conclusion

Randomness on Aztec is a client-side blinding value, drawn from one unconstrained oracle, and the system is designed so that its quality only ever matters to the party who drew it.

- **One source.** `aztec::oracle::random::random()` → `aztec_misc_getRandomField` → the PXE's `Fr.random()` → 64 CSPRNG bytes reduced modulo the field. Uniform, generated on the caller's device, invisible to the chain, not reproducible by anyone else.
- **Four uses in the framework**: note blinding (`H(owner, r)`), private event commitments, ephemeral encryption keys, ciphertext padding; plus a fallback tag for invalid recipients. The client libraries draw deployment and account salts, transaction nonces and bridge secrets from the same generator.
- **Three values per note, three sources.** `r` from the creator's oracle blinds the hash; the nonce `H(first_nullifier, index)` from the protocol makes the leaf unique and hides nothing; the nullifier from the owner's `nsk_app` marks the spend. A bad `r` weakens privacy, never ownership.
- **Unconstrained by design.** The party choosing `r` already knows the full preimage, so constraining `r` would protect against a party who can reveal everything anyway. Consistency, not randomness, is what the circuit enforces: the same `r` goes into the hash and into the message.
- **Two limits.** Public functions have no oracle and the protocol has no randomness beacon, so `random()` is a privacy primitive for the caller, not a fairness primitive between parties. A partial note's `r` is drawn once and kept in one place: reusing the commitment links payments and loses the second, and losing the pending message loses the note.
- **One operational trap.** The `SEED` environment variable turns the generator deterministic across the whole client stack.

![Mindmap of Aztec randomness covering the oracle and its host path, the four framework uses, the note's randomness-nonce-nullifier triad, the unconstrained-by-design argument, public-function limits and partial-note consequences]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-17-aztec-randomness-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Oracle** | A Noir call answered by the host process (PXE or TXE) during simulation; its result enters the circuit as an unconstrained witness. |
| **`random()`** | The aztec-nr oracle `aztec_misc_getRandomField`, the framework's single source of randomness, answered with `Fr.random()`. |
| **`Fr.random()`** | `@aztec/foundation`'s draw of 64 CSPRNG bytes reduced modulo the BN254 scalar field order, uniform up to a 2^-258 bias. |
| **Note randomness `r`** | The blinding field mixed into a note hash as `H(owner, r)`, chosen by the note's creator and delivered to the owner in the note message. |
| **Partial commitment** | `H(owner, r)`, the private half of a note hash; alone it is the commitment a partial-note recipient hands to a payer. |
| **Note nonce** | `H(first_nullifier_in_tx, note_index)`, a protocol-derived, public value that makes a tree leaf unique; it hides nothing. |
| **Nullifier** | `H(note_hash_for_nullification, nsk_app)`, published when a note is spent; its unlinkability comes from the owner's secret key, not from `r`. |
| **Grumpkin** | The elliptic curve embedded in BN254 on which Aztec's account and ephemeral keys live; its points have coordinates in `Fr`, its scalars (secret keys) in `Fq`. |
| **Ephemeral key pair** | A fresh Grumpkin key pair whose secret is `from_field(random())`, used once for the ECDH shared secret that encrypts a message. |
| **`SEED`** | The environment variable that switches `@aztec/foundation`'s generator to a deterministic sequence for reproducible tests; never set in production. |

### Security Implementation Checklist

For anyone writing a custom note, a custom message format, or a contract that hands a random value to a public function.

#### Sources

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every blinding value (note randomness, event randomness, ephemeral key, padding) comes from `random()`, not from a hash of public inputs, a counter or a timestamp. | A derived value has an enumerable preimage; note hashes and commitments become brute-forceable and balances are exposed. |
| ☐ | A hand-written `compute_note_hash` mixes the `randomness` parameter into the hash. | A note hash without `r` is a hash of small inputs; every note of that type is readable from the tree. |
| ☐ | The `SEED` environment variable is absent from every production and staging environment, and CI configurations that set it never produce deployable artefacts or run against a live network. | Every blinding, ephemeral key and salt in the run follows a predictable sequence; an observer replaying it reads all notes and messages. |
| ☐ | The client stack in use answers `aztec_misc_getRandomField` with a CSPRNG (`Fr.random()` on Node's `crypto.randomBytes` or Web Crypto), and a custom PXE does not substitute a weaker generator. | The circuit cannot detect a weak oracle; a low-entropy generator silently degrades every commitment the client produces. |

#### Uses

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Each note or event gets its own draw; `r` is never reused across notes, and a partial note is never completed twice. | Reused `r` or a reused commitment links notes or payments to one owner; the second completion of a partial note is not discovered and its funds are unreachable. |
| ☐ | The value delivered to the recipient is the same one hashed in the circuit (use the framework's `create_note` / `NoteMessage` path rather than a hand-rolled message). | A mismatched `r` gives the recipient an undiscoverable note; the sender has paid for nothing. |
| ☐ | A partial note's pending message is treated as the only copy of `r`; recipient tooling backs up PXE state before publishing commitments. | Loss of the pending entry makes a note the recipient owns unspendable, since `r` cannot be re-derived. |
| ☐ | `random()` is never used as a fairness primitive: no public outcome (draw, ordering, selection) depends on a value drawn by the party the outcome is drawn against. | The caller chooses its own draw; a lottery or auction built this way is decided by the entrant. |
| ☐ | Public functions do not expect an oracle; unpredictable values they need arrive as arguments from a private half or from a commit-reveal protocol, with the trust implication stated. | A public function has no `random()`; a design that assumes one either does not compile or is replaced by a caller-chosen value. |
| ☐ | Tests that pin randomness use `OracleMock::mock("aztec_misc_getRandomField")`, and at least one test exercises a degenerate value (`0`) to confirm it only affects privacy. | A degenerate value that also breaks correctness (such as an ephemeral key at infinity) would otherwise reach production unchecked. |

## Frequently Asked Questions

**Q: What exactly does `random()` return, and where is it computed?**

A single BN254 scalar-field element, uniformly distributed. The Noir side is an oracle declaration, `#[oracle(aztec_misc_getRandomField)]`; the host answers with `Fr.random()`, which draws 64 bytes from the operating system's CSPRNG (`crypto.randomBytes` under Node, Web Crypto in a browser) and reduces them modulo the field order. The reduction of a 512-bit input into a 254-bit modulus leaves a bias around 2^-258, which is irrelevant. It is computed on the device running the private simulation, never on the sequencer.

**Q: If the note nonce already makes every leaf unique, why does a note also need randomness?**

Because the nonce is public and hides nothing. It is `H(first_nullifier_in_tx, note_index)`, both inputs visible in the transaction, so anyone can recompute it. Its purpose is to let two otherwise identical notes coexist in the tree with distinct leaves.

The randomness `r` has the other job: without it the leaf's preimage is `(nonce, contract, slot, owner, value)`, every element of which is public or enumerable, and an observer could confirm any guessed `(owner, value)` against the tree. Uniqueness and hiding are separate properties, provided by separate values from separate parties.

**Q: The value is unconstrained. Could a malicious sender use that against me?**

Only in the one way the framework already concedes, and it gains nothing by it. The sender who creates a note for you chooses `r`; a sender who picks a weak `r` makes your note brute-forceable, but that sender already knows your address, the amount and the slot, so it could publish them directly.

Two things a bad `r` cannot do:

- **Take the note.** The nullifier depends on your secret key, so no choice of `r` lets anyone else spend it.
- **Trick your wallet.** If the delivered `r` does not match the hash in the tree, your PXE discards the note and the sender has paid without you receiving; the mismatch harms the sender.

The trust argument fails only where the chooser does not already know the preimage, and the framework's uses avoid that case.

**Q: Can a public function draw a random number?**

No. Public functions run in the AVM on the sequencer, which has no oracles, and the protocol provides no randomness beacon or VRF at 5.2.0. A public function that needs an unpredictable value has three routes:

- an argument passed from the private half of the same transaction, drawn by the caller's oracle, acceptable when the caller is the party the value protects;
- a commit-reveal protocol across transactions when several parties must not control the outcome;
- an external oracle contract, which is not part of the protocol.

Aztec's `random()` is a privacy tool for the party calling it, not a fairness tool between parties.

**Q: In the AIP-20 commitment flow, who chooses the randomness, and what does the payer see?**

The recipient. `initialize_transfer_commitment(to, completer)` runs on the recipient's device, draws `r`, and publishes only `C = H(to, r)` to the payer, plus a validity commitment `H(C, completer)` to the nullifier tree. The payer completes the note from `C` and an amount; it never learns `r` or `to`.

Two consequences follow. The commitment is single-use: a second completion carries the same log tag `H(C)`, linking the two payments publicly, and the recipient's PXE, having matched the first, does not discover the second. And the pending message on the recipient's side is the only copy of `r`, because a random value cannot be re-derived the way a key-derived one could.

**Q: How do I make a Noir test deterministic, or force a specific randomness?**

Two levels. Setting the `SEED` environment variable makes the whole `@aztec/foundation` generator deterministic for a run, which the TXE inherits, so every draw in every test follows the same sequence between runs. Inside a single test, `std::test::OracleMock::mock("aztec_misc_getRandomField").returns(v)` makes the next draw return `v`, which is how aztec-nr's own test checks that an ephemeral key of `0` is rejected and how a contract test can assert a note hash against a constant. Neither mechanism belongs anywhere near a production client.

**Q: What is a Grumpkin scalar, and is the `Fr` versus `Fq` remark on ephemeral keys a vulnerability?**

Grumpkin is the curve on which all Aztec account keys and ephemeral encryption keys live. It is embedded in BN254, the proving curve, with the fields crossed: Grumpkin points have coordinates in `Fr` (the Noir `Field`), and Grumpkin scalars, the multipliers in `secret × generator`, live in `Fq`, the BN254 base field. A Grumpkin scalar is thus a secret key, and because `Fq` is slightly larger than `Fr` it is stored as two limbs, `EmbeddedCurveScalar { lo, hi }`.

Not a vulnerability. The ephemeral secret is `EmbeddedCurveScalar::from_field(random())`, and `random()` returns an element of `Fr`, so the scalars between `r` and `q` are never drawn. That excluded range is `q − r`, about 2^127 out of about 2^254 keys, a fraction near 2^-127, and no structure in it helps an attacker.

The library marks it as a `@todo` for uniformity. The value the code does guard against is `0`, which yields the point at infinity and an undecryptable message.

## References

### Aztec documentation

- [Protocol oracles](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/advanced/protocol_oracles) — oracles introduce non-determinism and are unconstrained; injected data must otherwise be constrained
- [Custom notes](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/custom_notes) — how a note hash combines packed data, owner, storage slot and randomness
- [Partial notes](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/advanced/partial_notes) — the two-round hash and the *Single-use semantics* section
- [Partial notes as payment endpoints](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/advanced/partial_notes_as_payment_endpoints) — completer choice, commitment rotation, what leaks
- [Authentication witnesses](https://docs.aztec.network/developers/docs/foundational-topics/advanced/authwit) — "in public execution, oracles aren't available since the sequencer runs the code"
- [Transactions](https://docs.aztec.network/developers/docs/foundational-topics/transactions) — the transaction request `salt` and the first nullifier
- [Contract creation](https://docs.aztec.network/developers/docs/foundational-topics/contract_creation) — the deployment salt
- [Note discovery](https://docs.aztec.network/developers/docs/foundational-topics/advanced/storage/note_discovery) — ephemeral keys, tagging secrets and how a recipient finds its notes
- [Keys](https://docs.aztec.network/developers/docs/foundational-topics/accounts/keys) — all account keys are Grumpkin scalars, public keys Grumpkin points; app-siloed nullifier keys
- [AIP-20 Fungible Token](https://docs.aztec.network/developers/docs/aztec-nr/standards/aip-20)

### Analyzed source

- [AztecProtocol/aztec-nr](https://github.com/AztecProtocol/aztec-nr) — analyzed at tag [v5.2.0](https://github.com/AztecProtocol/aztec-nr/tree/v5.2.0), commit [`22e152679f69a2307fdb1b17f60fd4f51a3fd4f5`](https://github.com/AztecProtocol/aztec-nr/tree/22e152679f69a2307fdb1b17f60fd4f51a3fd4f5), 2026-09-17: `aztec/src/oracle/random.nr`, `aztec/src/note/lifecycle.nr`, `aztec/src/event/event_emission.nr`, `aztec/src/keys/ephemeral.nr`, `aztec/src/messages/encryption/aes128.nr`, `aztec/src/messages/delivery/tag_derivation.nr`, `aztec/src/oracle/resolve_tagging_strategy.nr`, `uint-note/src/uint_note.nr`
- [AztecProtocol/aztec-packages](https://github.com/AztecProtocol/aztec-packages) — analyzed at tag [v5.2.0](https://github.com/AztecProtocol/aztec-packages/tree/v5.2.0), commit [`49a592109ec4f18d79212b43d621891aaf36f7b6`](https://github.com/AztecProtocol/aztec-packages/tree/49a592109ec4f18d79212b43d621891aaf36f7b6), 2026-09-17: `noir-projects/noir-protocol-circuits/crates/types/src/hash.nr` (nonce, siloed and unique note hash) and `constants.nr` (domain separators); the `@aztec/foundation`, `@aztec/pxe`, `@aztec/aztec.js` and `@aztec/bb.js` packages at 5.2.0 (`Fr.random`, `RandomnessSingleton`, `getRandomField`, `randomBytes`)
- [CMTA/aztec-standards](https://github.com/CMTA/aztec-standards) — the AIP-20 `Token` used as the example, analyzed at commit [`5433e9c7dc34f1b426adfe0ce9e0ae3a688351d9`](https://github.com/CMTA/aztec-standards/tree/5433e9c7dc34f1b426adfe0ce9e0ae3a688351d9) (a fork of [defi-wonderland/aztec-standards](https://github.com/defi-wonderland/aztec-standards) on Aztec 5.2.0; the token source is unchanged), 2026-09-17

### Related articles

- [Partial Notes on Aztec — Deferred Completion and Private DeFi Composability]({{site.url_complet}}/2026/09/09/aztec-partial-notes-private-defi-composability/)
- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
- [AIP-20, the Aztec Token Standard, Compared with ERC-20 and ERC-7984]({{site.url_complet}}/2026/09/11/aip-20-aztec-token-standard-vs-erc-20-erc-7984/)
- [Packing Small Values into One Field on Aztec — The Packable Trait, Its Cost and Its Traps]({{site.url_complet}}/2026/09/16/aztec-packable-storage-packing/)
- [When the Hardware RNG Was Not Called - Anatomy of an Entropy Defect]({{site.url_complet}}/2026/07/31/coldcard-rng-entropy-incident/)
