---
layout: post
title: "Ephemeral Keys on Aztec — Encrypting to an Address, the Curve Behind It, and What a Quantum Computer Would Break"
date:   2026-09-17
lang: en
locale: en-GB
categories: blockchain ethereum ZKP cryptography
tags: aztec zkp privacy cryptography elliptic-curve post-quantum smart-contracts
description: "Every private note on Aztec is encrypted with a one-shot ECDH key on Grumpkin: how it is made, what the ciphertext holds, and why it is not post-quantum."
image: /assets/article/blockchain/aztec/2026-09-17-aztec-ephemeral-keys-mindmap.png
isMath: false
---

[Aztec](https://aztec.network/) is a privacy-focused Layer 2 on Ethereum. A contract there has a private side, executed on the user's device inside a zero-knowledge proof over encrypted *notes* that only their owner can read, and a public side executed by a sequencer; the chain stores the private side as commitments and as encrypted logs that carry each note to its recipient. [An earlier article]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/) covers that execution model. This one is about the encryption.

When a private function on Aztec creates a note for someone, the note's content has to travel to that someone, and the only channel the protocol offers is a public log. So the content is encrypted, and the question is: with what key? The sender may have never met the recipient, may hold nothing but its address, and must not leave in the ciphertext anything that ties two messages to the same recipient. The answer the framework uses is the one every "encrypt to a public key" system has used since ECIES: generate a fresh key pair for this one message, combine its secret half with the recipient's public key by Diffie-Hellman, derive a symmetric key from the result, and ship the public half alongside the ciphertext. That fresh pair is the **ephemeral key**.

This article follows an ephemeral key from the random field it starts as to the fifteen-field log it ends in, through the curve it lives on (Grumpkin, chosen so that the whole computation is cheap inside a proof), the recipient-side key that makes an Aztec *address* usable as an encryption key, the AES-128 construction on top, and the second place the same key pair appears, the handshake that lets a recipient find messages from a stranger. It ends with the question in the title: an ephemeral ECDH key is a discrete-logarithm object, a quantum computer solves discrete logarithms, and every ciphertext ever produced this way sits on a public ledger.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why a fresh key per message

Three requirements decide the design, and each rules out a simpler option.

- **The sender knows only an address.** A recipient may never have transacted with the sender, and the protocol's tagging system reaches recipients the sender has not registered. So the recipient's encryption key must be derivable from its address alone. Aztec arranges that by making the address itself the x-coordinate of an elliptic-curve point, as the next sections show.
- **Two messages to one recipient must not look related.** If the sender used a static key of its own, the ciphertexts would carry a fixed sender public key, and an observer could group every message from that sender. With a fresh ephemeral key the only public value in the ciphertext is a point nobody has seen before.
- **The sender's long-term keys must not protect the message.** A private function runs on the sender's device and is proved; the framework wants encryption that depends on nothing the sender holds durably, so that a later compromise of the sender's wallet reveals nothing about messages already sent. The ephemeral secret is used once and discarded.

The pattern is ephemeral-static Diffie-Hellman, and the shared secret is symmetric by construction: the sender computes `eph_sk × RecipientPoint`, the recipient computes `recipient_secret × eph_pk`, and both land on the same point because `eph_sk × recipient_secret × G` is the same whichever scalar is applied first.

## The curve: Grumpkin, embedded in BN254

Every key in this article is a point or a scalar on **Grumpkin**, the curve `y² = x³ − 17` defined over the field of the Noir `Field` type. Aztec did not pick it for its own sake; it picked it because of how it relates to BN254, the curve the proofs are built over.

A proof system fixes a field, the *scalar field* of its pairing curve, and every wire in a circuit is an element of that field. For BN254 that field is `Fr`, of prime order `r ≈ 2^254`. Doing elliptic-curve arithmetic on BN254 itself inside a BN254 circuit is expensive, because BN254's point coordinates live in a different field, `Fq`, and every operation has to emulate `Fq` arithmetic with `Fr` wires.

Grumpkin is the curve defined the other way round: its coordinates are in `Fr` and its group order is `q`, the order of `Fq`. The two curves form a cycle of fields, so adding two Grumpkin points or multiplying one by a scalar is native `Fr` arithmetic, with no emulation. That is why account keys, viewing keys, ephemeral keys and every Diffie-Hellman in the framework are on Grumpkin: they have to be computed *inside* the proof.

The price of the cycle is a type mismatch that shows up in the code. A Grumpkin **point** is two `Field`s; a Grumpkin **scalar** is an element of `Fq`, which is slightly larger than `Fr` (by about 2^127 values), so it does not fit in a `Field`. Noir's `EmbeddedCurveScalar` carries it as two 128-bit limbs, `lo` and `hi`; `EmbeddedCurveScalar::from_field(f)` converts a `Field` into one, which is how a random `Field` becomes a secret key. The public key is `fixed_base_scalar_mul(sk)`, the scalar times the generator `G`.

One more convention matters for everything below. A point is fully determined by its x-coordinate and the sign of its y-coordinate, and the framework defines "positive" as `y ≤ (r − 1) / 2`. When a point has to be transmitted in one field, only `x` is sent and the receiver reconstructs the point by taking the positive root; when a key is generated for that purpose, secrets are re-drawn until the public key's y is positive.

## The recipient side: an address is an encryption key

An Aztec account has several protocol key pairs, all on Grumpkin: a nullifier key pair (`Npk_m`, used to spend notes), an incoming viewing key pair (`Ivpk_m` / `ivsk`, used to receive them) and four reserved ones. Of these, only `Ivpk_m` is kept as a point; the others enter the account only as hashes. The reason is the address derivation:

```
pre_address   = H(public_keys_hash, partial_address)   // partial_address commits to the contract class and its initialisation
address_point = pre_address · G + Ivpk_m               // positive y chosen
address       = address_point.x
```

The address is the x-coordinate of a point whose discrete logarithm is `pre_address + ivsk`. Anyone holding the address can rebuild `address_point`: take `x`, solve `y² = x³ − 17`, keep the positive root. The framework calls that `to_address_point`, and an `x` with no root on the curve is an *invalid* address. Only the owner holds `ivsk`, so only the owner holds the scalar behind the point. The framework calls that scalar the **address secret**: `computeAddressSecret(pre_address, ivsk)` in the PXE, with the negation applied when the resulting point would have had a negative y, so that it always matches the point a sender reconstructs.

This is what lets a sender encrypt to an address it has never seen before. There is no key registry to look up and no first contact needed: the address is the public key. It also fixes what "the recipient's private key" means in every Diffie-Hellman below: not `ivsk` alone, but `pre_address + ivsk`, a scalar bound to the account's contract class and initialisation as well as to its viewing key.

![Concept: the two Grumpkin key pairs of a message, the sender's one-shot ephemeral pair drawn from the random oracle and the recipient's address point whose secret is pre_address plus ivsk, meeting in one shared secret and one AES-128 key]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-ephemeral-key-parties-concept.png)

## Encrypting one message, step by step

The framework's message encryption is the `AES128` implementation of the `MessageEncryption` trait (`aztec/src/messages/encryption/aes128.nr` in aztec-nr v5.2.0). Every private note, partial-note announcement and private event goes through it. The input is up to 12 `Field`s of plaintext, the recipient's address and the contract address; the output is always exactly 15 `Field`s.

![Sequence of encrypting one note: the sender draws an ephemeral Grumpkin key pair with positive y, computes the ECDH point against the recipient's address point, silos it to the contract with Poseidon2, derives two AES-128 key and IV pairs, encrypts body and header in CBC mode, packs the bytes into fields, masks them, prepends eph_pk.x and pads with random fields; the recipient reverses it from eph_pk.x and its address secret]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-ephemeral-key-encryption-sequence.png)

**1. Draw the ephemeral key pair.** `generate_positive_ephemeral_key_pair()` calls the randomness oracle (`random()`, the subject of [a companion article]({{site.url_complet}}/2026/09/17/aztec-randomness-notes-oracle-unconstrained/)), turns the field into a scalar with `from_field`, multiplies by `G`, and repeats until the public key's y-coordinate is positive; about half of the draws pass. Two checks follow: the point must not be the point at infinity, and its sign must be positive. The draw is unconstrained, and the framework's comment explains why that is acceptable: a sender who chooses a bad ephemeral key can only expose a plaintext it already knows.

**2. Diffie-Hellman against the address.** `S = eph_sk × address_point`, with the recipient's point reconstructed from its address. If the address is invalid (no curve point has that x), the code does *not* fail: it encrypts to a random valid point instead, so that a contract cannot be forced into an impossible transaction by feeding it a bad recipient. The message is then undecryptable by anyone, which is the intended outcome for a recipient that does not exist.

**3. Silo the secret to the contract.** `s_app = Poseidon2(S.x, S.y, contract_address)` under a domain separator. The same sender, recipient and ephemeral key would otherwise yield the same symmetric key in every contract; siloing makes a key derived in one application useless in another. The framework has a long comment on whether Poseidon2 may be used as the key-derivation hash here, citing a lemma from [Krawczyk's HKDF paper](https://eprint.iacr.org/2010/264) on extracting keys from a Diffie-Hellman value with a hash modelled as a random oracle, and concluding that it may, because neither scalar entering `S` was itself produced by Poseidon2.

**4. Derive two AES keys and IVs.** From `s_app`, four Poseidon2 subkeys are derived with distinct separators, and from each the framework takes the sixteen *low* bytes, because the high byte of a 254-bit field element carries under six bits of randomness. Two `(key, IV)` pairs of 128 bits each result: one for the body, one for a header.

**5. Encrypt body and header, AES-128-CBC.** The plaintext fields are serialised as 32 bytes each and encrypted with PKCS#7 padding, which always adds a full 16-byte block here since 32 is a multiple of 16. A 2-byte header holding the body's byte length is encrypted separately into one 16-byte block. There is no message authentication code; the next section returns to that.

**6. Pack, mask, frame.** Header and body ciphertexts are laid out in bytes, zero-padded to a multiple of 31, and packed 31 bytes per field (a field holds 254 bits, so 31 whole bytes). Each packed field is then *masked* by adding a Poseidon2-derived value, so that the fields look uniformly random rather than like 128-bit AES blocks. `eph_pk.x` is placed first; any remaining slots up to 15 are filled with random fields, indistinguishable from masked data, so that a two-field message and a twelve-field message have the same length. The protocol then prefixes the discovery tag, and the 16-field private log is emitted.

**Decryption** mirrors it from the recipient's PXE, in unconstrained code. It reads field 0, reconstructs `eph_pk` by taking the positive root, and asks its key store for the shared secret through an oracle: `address_secret × eph_pk`, then the same siloing. If the PXE does not hold the keys of the recipient in question (it can be syncing an address it only watches), the oracle returns nothing and the log is skipped. Otherwise it unmasks the fields, derives the two key pairs, decrypts the header to learn the body length, decrypts the body, and hands the plaintext to the message-type dispatcher. A log that was not meant for this recipient fails at the header or at the padding check and is discarded silently; that failure is how "not for me" is detected, since nothing in the log says who it is for.

## What the construction does and does not promise

Set against ECIES as usually specified, the differences are these.

- **Confidentiality** rests on the hardness of computing `S` from `eph_pk` and `address_point`, the computational Diffie-Hellman problem on Grumpkin, plus AES-128. Every message has its own `S`, so breaking one gives nothing on the others.
- **Recipient anonymity.** The ciphertext contains no recipient identifier; the tag prefixed by the protocol is the only routing information, and it is derived from a secret shared with the recipient, not from the address. An observer sees an ephemeral point and fourteen random-looking fields.
- **Sender anonymity.** No sender key appears anywhere in the ciphertext. The notion of "sender" in the tagging layer is a separate matter, chosen by the wallet and overridable by the contract.
- **Length hiding.** The fixed 15-field frame with random padding means content length is not visible.
- **No integrity tag.** There is no MAC over the ciphertext, and CBC on its own is malleable. The framework does not need one, because a note is not accepted for being decryptable: its hash must also be found in the note hash tree of the same transaction, and a note whose recomputed hash matches no leaf is dropped. Authenticity of *content* comes from the commitment on chain; the ciphertext only has to carry the preimage to whoever can use it. A tampered log yields a preimage whose hash is in no tree, and is discarded.
- **Constrained or not.** When a note is delivered with `MessageDelivery::onchain_constrained()`, the whole of steps 1 to 6 runs *inside the circuit* and the proof attests that the log contains a correct encryption of the note for the stated recipient. That is the reason the construction has to be circuit-friendly: Grumpkin for the curve, Poseidon2 for every hash, AES-128 as a black-box gate. Unconstrained delivery runs the same code without proving it, which is cheaper and trusts the sender to have delivered correctly.

## The second ephemeral key: handshakes and discovery tags

Encryption answers "can the recipient read it"; it does not answer "how does the recipient find it among every log on the chain". Aztec's answer is a *tag* prefixed to each log, `Poseidon2(secret, index)`, where `secret` is shared between sender and recipient and `index` counts the messages between them in this contract. The node indexes logs by tag, and a recipient asks for the tags it can compute. How the two parties come to share `secret` is the tagging-secret strategy, and two of the four strategies use an ephemeral key.

**Non-interactive handshake**, the default for a recipient the sender has not contacted before. The `HandshakeRegistry` contract, at a fixed protocol address, generates a *second* ephemeral pair `(eph_sk, eph_pk)`, computes `S = eph_sk × recipient_point`, and applies a **forgery protection**: `S' = k · S` with `k = Poseidon2(eph_pk, recipient_point)`. Without it a malicious recipient, who can compute the symmetric secret `S` itself, could register a second handshake landing on the same `S` and emit logs under the honest sender's constrained-delivery tag, blocking that sender's sequence; folding `eph_pk` into `k` forces a forger to announce a different point and land elsewhere. The registry stores `S'` in a note owned by the sender together with a random *sender-only* secret, then **announces** the handshake: it encrypts `[eph_pk.x]` to the recipient with the very `AES128::encrypt` of the previous section (a third ephemeral key, for the announcement itself) and emits it under a tag derived from the recipient's address alone. Anyone can see that *someone* handshook with that address; nobody learns who, or what follows. During sync the recipient finds the announcement, decrypts `eph_pk.x`, applies the same `k` to `eph_pk` (the protection commutes with the scalar multiplication) and derives `S'` with its address secret. From then on both sides compute the same tags.

**Interactive handshake** derives the same `S'` from an ephemeral key that is never published: the registry asks the recipient, through a wallet-side request oracle, to sign the handshake, verifies the signature in-circuit, and the recipient learns `eph_pk` in the act of signing. Nothing on chain announces the contact, at the price of the recipient being reachable at send time.

The other two strategies do without an ephemeral key. An **address-derived secret** is Diffie-Hellman between the two parties' *address* keys, `(pre_address_A + ivsk_A) × address_point_B`, computable by each side from its own secret and the other's address, so it leaves no trace on chain but requires the recipient to have registered the sender. An **arbitrary secret** is a point the parties agreed on out of band. Neither is backed by anything on chain, which is why only the two handshake strategies may support constrained delivery.

A first message to a new recipient therefore costs three ephemeral key pairs: one for the handshake secret, one to encrypt the handshake announcement, one to encrypt the note. Every later message to that recipient costs one.

## Is it post-quantum secure?

No, and the answer is worth giving layer by layer, because the layers fail differently and one of them does not fail at all.

| Layer | Primitive | Against a large quantum computer | What an attacker gains |
|---|---|---|---|
| Message key agreement | ECDH on Grumpkin | **Broken** by Shor's algorithm: `eph_sk` from `eph_pk`, or the address secret from `address_point` | Every ciphertext ever published, decrypted |
| Discovery tags | ECDH-derived handshake secrets | **Broken** the same way | Every log linked to its recipient |
| Symmetric layer | AES-128-CBC, keys from Poseidon2 | Weakened by Grover's algorithm to about 2^64 work | Nothing on its own; the key is reached through the layer above |
| Commitments | Poseidon2 note hashes, nullifiers, event commitments | **Holds**, up to Grover's square-root speed-up on preimage search (2^127 for a 254-bit output) | The blinding randomness stays hidden; balances in the tree remain private |
| Proofs | Honk-family SNARKs over BN254 (pairings, discrete logarithms) | **Soundness broken**: a quantum prover can forge proofs | Forged state transitions, not decryption |
| Account authorisation | Whatever the account contract chose; Schnorr on Grumpkin and ECDSA in the reference accounts | **Broken** for those signature schemes | Spending as the account |

The row that matters most for this article is the first, because of *where the ciphertexts live*. An Aztec private log is data-availability content of the rollup: it is published so that a recipient can sync from the chain alone, and it never leaves. Each log begins with `eph_pk.x`, and the recipient's `address_point` is public by construction. An adversary that records the chain today and obtains a cryptographically relevant quantum computer later has two routes:

- **per message**, one discrete logarithm on Grumpkin to recover `eph_sk`, one scalar multiplication to recover `S`, and the public Poseidon2 and AES steps to read the note: owner, amount, randomness;
- **per recipient**, one discrete logarithm on `address_point` to recover the address secret, then every message that address ever received.

This is the "harvest now, decrypt later" setting, and it applies to the confidentiality of every note delivered on chain, retroactively, from the first block.

Two things narrow the exposure without changing the cryptography. Offchain delivery (`MessageDelivery::offchain()`) uses the same encryption but does not publish the ciphertext, so what a harvester can collect is whatever it intercepted rather than the whole ledger. And the commitments themselves survive: a note hash `H(slot, H(owner, r), value)` with a 254-bit random `r` is not recoverable from the tree by a quantum computer within Grover's bound, so an adversary who decrypts no log learns no balance. Aztec's privacy against a quantum adversary is exactly as good as the secrecy of the logs, and no better.

What a post-quantum version would need is also clear from the construction, and the costs are the reason it does not exist yet:

- **A hybrid key agreement**, ECDH combined with a lattice KEM such as [ML-KEM](https://csrc.nist.gov/pubs/fips/203/final) (covered in [a previous article]({{site.url_complet}}/2026/06/29/ml-kem-fips-203-post-quantum-key-encapsulation/)), so that the symmetric key is safe if either survives. An ML-KEM-768 ciphertext is 1,088 bytes, which is 36 fields of 31 bytes; ML-KEM-512 is 768 bytes, 25 fields. The private log is 16 fields. The frame would have to grow several times, and DA cost with it.
- **A KEM public key per account**, published the way `Ivpk_m` is today, and folded into the address derivation so that "encrypt to an address" keeps working. That is a protocol-level change to what an address commits to.
- **The circuit cost.** For constrained delivery the encapsulation would run inside the proof. ML-KEM's arithmetic (polynomial multiplication mod 3329, SHAKE-based hashing) is far from the Poseidon2-and-Grumpkin toolkit the circuits are built around; it would be an expensive gadget, and it would be paid on every constrained note.
- **The proof system**, separately, would need a post-quantum-sound replacement (hash-based, STARK-style commitments) for integrity to survive, a much larger change than the encryption layer and outside the ephemeral key's story.

The framework's own documentation does not claim post-quantum security anywhere, and its choices of Grumpkin, Poseidon2, AES-128 and pairing-based proofs are those of a system optimised for proving cost today. A reader assessing Aztec for data with a long confidentiality horizon should take the first row of the table as the answer.

## Conclusion

An ephemeral key on Aztec is a one-shot Grumpkin key pair, drawn from the client's random oracle, that lets a sender encrypt to a recipient's address alone and leaves no reusable value in the ciphertext.

- **The curve is chosen for the proof.** Grumpkin's coordinates live in BN254's scalar field, so every Diffie-Hellman and every point operation is native inside a circuit; its scalars live in the slightly larger `Fq`, hence `EmbeddedCurveScalar { lo, hi }`.
- **An address is a public key.** `address = (pre_address · G + Ivpk_m).x`, so any address with a curve point behind it can be encrypted to; the matching secret is `pre_address + ivsk`, held only by the owner.
- **One message, one key.** Ephemeral pair with positive y → `S = eph_sk × address_point` → Poseidon2 siloing to the contract → two AES-128-CBC key/IV pairs → body and header → 31-byte packing, Poseidon2 masks, `eph_pk.x` first, random padding to 15 fields.
- **No MAC, by design.** Authenticity comes from the note hash in the tree, not from the ciphertext; a garbled log decrypts to nothing usable.
- **Handshakes use it too.** A non-interactive handshake spends a second ephemeral key for the tag secret, protected against recipient forgery by `k = H(eph_pk, recipient_point)`, and a third to announce it; an interactive handshake keeps the key off chain.
- **Not post-quantum.** ECDH on Grumpkin falls to Shor, and because every ciphertext is on the ledger with its `eph_pk.x`, all past onchain notes become readable the day such a machine exists; commitments and nullifiers hold, proof soundness does not. A hybrid KEM would need a larger log frame, a KEM key in the address and an in-circuit encapsulation.

![Mindmap of Aztec ephemeral keys covering why a fresh key per message, the Grumpkin curve embedded in BN254, the address as a public key, the AES-128 message construction, the handshake uses, and the post-quantum assessment layer by layer]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-17-aztec-ephemeral-keys-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Ephemeral key pair** | A Grumpkin key pair generated for one message or one handshake, `sk = from_field(random())`, `pk = sk · G`, used once and discarded. |
| **Grumpkin** | The curve `y² = x³ − 17` over BN254's scalar field `Fr`, with group order `q`; embedded in BN254 so that its arithmetic is native in a circuit. |
| **`EmbeddedCurveScalar`** | Noir's two-limb representation `{ lo, hi }` of a Grumpkin scalar, needed because `Fq` is larger than a `Field`. |
| **Address point** | The Grumpkin point `pre_address · G + Ivpk_m` with positive y, whose x-coordinate is the account's address; rebuilt from the address by anyone. |
| **Address secret** | `pre_address + ivsk` (negated when needed for a positive y), the discrete logarithm of the address point, held only by the account owner. |
| **Shared secret `S`** | `eph_sk × address_point = address_secret × eph_pk`, the ECDH point from which a message's symmetric keys are derived. |
| **App-siloed secret `s_app`** | `Poseidon2(S.x, S.y, contract_address)`, the per-contract scalar that feeds the AES key, IV and field-mask derivations. |
| **Positive y** | The convention `y ≤ (r − 1) / 2`; a point is sent as its x-coordinate alone and reconstructed with the positive root. |
| **Non-interactive handshake** | A registry entry whose secret `S' = k · (eph_sk × recipient_point)`, `k = H(eph_pk, recipient_point)`, is announced by encrypting `eph_pk.x` to the recipient under an address-derived tag. |
| **Harvest now, decrypt later** | Recording ciphertexts today to decrypt them once a quantum computer can solve the discrete logarithms that protect them; applies to every onchain private log. |

### Security Implementation Checklist

For a wallet or PXE holding the recipient side, and for anyone implementing the `MessageEncryption` trait or a custom note delivery.

#### Keys and curve

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The ephemeral secret comes from the CSPRNG-backed `random()` oracle, fresh per message, never derived from message content or reused across messages. | A reused or predictable `eph_sk` links messages and, if guessed, decrypts them. |
| ☐ | The ephemeral public key is rejected if it is the point at infinity, and re-drawn until its y-coordinate is positive when only `x` is transmitted. | An infinity key gives an undecryptable message; a negative-y key is reconstructed wrongly by the recipient and the message is lost. |
| ☐ | The recipient point is derived from the address with `to_address_point`, and an invalid address (no curve point) is handled without aborting the transaction. | Aborting lets an attacker force a contract into an unprovable transaction by supplying a bad recipient. |
| ☐ | The address secret is computed as `pre_address + ivsk` with the negation rule applied, never as `ivsk` alone. | The wrong scalar yields a different `S`; every message to the account fails to decrypt. |
| ☐ | `ivsk` and the address secret never leave the PXE key store; shared-secret derivation goes through the `get_shared_secret` oracle. | A leaked address secret decrypts every past and future message to the account. |

#### Symmetric layer and framing

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The raw ECDH point is siloed with the contract address before any key derivation. | One key across contracts lets a message encrypted in one application be read in another. |
| ☐ | AES keys and IVs are taken from the low 16 bytes of Poseidon2 subkeys with distinct separators, one pair per use; a key/IV pair is never reused. | High bytes have under six bits of entropy; a reused CBC IV leaks plaintext structure. |
| ☐ | Ciphertext fields are masked and the frame is padded with random fields to the fixed length. | Unmasked 128-bit blocks and variable length reveal message type and size. |
| ☐ | Decryption treats a failed header, length or padding check as "not for me" and discards the log without error. | Distinguishable failures leak which logs were addressed to a recipient. |
| ☐ | A decrypted note is accepted only if its recomputed hash matches a leaf of the transaction's note hash tree. | Without the tree check, a forged or tampered ciphertext (there is no MAC) could plant a fake note. |

#### Long-horizon data

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Data whose confidentiality must outlast the arrival of a quantum computer is not delivered on chain, or is accepted as exposed to harvest-now-decrypt-later. | Onchain logs carry `eph_pk.x` permanently; a future discrete-logarithm solver reads every one. |
| ☐ | Any post-quantum extension combines a KEM with the existing ECDH (hybrid) rather than replacing it, and the KEM key is bound into the address. | A KEM-only key that is not committed to by the address can be substituted by a sender. |

## Frequently Asked Questions

**Q: Why is the ephemeral public key sent as one field, and what if the x-coordinate has two possible points?**

Every x-coordinate on a curve has two points, `(x, y)` and `(x, −y)`. The framework fixes the convention that the transmitted point has a *positive* y, meaning `y ≤ (r − 1) / 2`, and generates ephemeral keys by re-drawing until the public key satisfies it. The recipient reconstructs the point by solving `y² = x³ − 17` and keeping the positive root.

That halves the size of the key in the log, one field instead of two, and is why `generate_positive_ephemeral_key_pair` exists alongside the plain generator. An x with no root on the curve is not a valid point; on decryption it is skipped.

**Q: How can a sender encrypt to someone it has never contacted, with nothing but an address?**

Because the address is the x-coordinate of a Grumpkin point, `pre_address · G + Ivpk_m`, and the discrete logarithm of that point, `pre_address + ivsk`, is held by the owner. The sender rebuilds the point from the address, draws an ephemeral key, and computes `eph_sk × address_point`; the owner computes `address_secret × eph_pk`; both are the same point. No registry, no prior exchange. The handshake mechanism is about *finding* the message afterwards, not about being able to encrypt it.

**Q: Why does the ciphertext have no MAC? Isn't unauthenticated CBC a known weakness?**

It would be, if decryptability were what made a message valid. On Aztec it is not. A note is accepted only when its recomputed hash matches a leaf in the note hash tree of the same transaction, and that tree is what the proof committed to. A tampered log decrypts to a preimage whose hash matches nothing and is discarded.

The ciphertext's job is to transport a preimage confidentially; integrity of the state is settled by the commitment, so a MAC would protect nothing the tree does not already protect. What is deliberately absent is any way for the recipient to learn *who* sent the note from the ciphertext.

**Q: How many ephemeral keys does one private transfer to a new recipient use?**

Three, on the first contact, and one afterwards:

- one inside the handshake registry, to derive the tag secret `S'` shared with the recipient;
- one to encrypt the handshake announcement, which carries the first key's `eph_pk.x` to the recipient;
- one to encrypt the note itself.

Later messages reuse the registered handshake for tags and spend only the third. A self-send, or a recipient reached through an address-derived secret, spends only the third from the start, since no handshake is made.

**Q: What does the forgery protection in the handshake defend against?**

The symmetric property of Diffie-Hellman. The recipient can compute the handshake's `S` itself, and the ephemeral key is unconstrained, so a malicious recipient could register a *second* handshake, crafted to land on the same `S` with a different sender-only secret, and emit logs under the honest sender's constrained-delivery tag; that collides with the sender's sequence and blocks it.

Multiplying `S` by `k = Poseidon2(eph_pk, recipient_point)` means a forgery has to announce a different `eph_pk` and therefore lands on a different protected secret. The recipient applies the same `k` to the announced `eph_pk` before its own ECDH, which works because a scalar multiplication commutes through the exchange.

**Q: Concretely, what would a quantum attacker do with the chain as it is today?**

Two routes, both from public data:

- **Per message.** Take `eph_pk.x` from a log, reconstruct the point, solve the discrete logarithm on Grumpkin for `eph_sk`, multiply by the recipient's address point, silo, derive the AES keys, decrypt. That yields the note's owner, value and randomness.
- **Per recipient.** Take an address, reconstruct its point, solve for the address secret, and decrypt every message that address has ever received, and every handshake announcement, which also reveals the tag secrets.

What the attacker still cannot do is read a balance from the note hash tree without a log, because the hash's blinding is a 254-bit random value and Grover's algorithm leaves a 2^127 search. Nor does the attack give the nullifier secret key, so it reads notes rather than spends them; spending would require breaking the account's signature scheme or the proof system, which for the reference accounts and the pairing-based proofs it also could.

**Q: Would switching to ML-KEM make the encryption post-quantum?**

For the message layer, in a hybrid with ECDH, yes, and three costs follow:

- **The frame.** An ML-KEM-768 ciphertext is 1,088 bytes, 36 fields against the current 15, so the private log would grow and DA fees with it.
- **The address.** The recipient's KEM public key has to be committed to by the address, or a sender could be given a substituted key; that changes what an Aztec address is.
- **The circuit.** Constrained delivery proves the encryption, so the encapsulation would run inside the proof, and ML-KEM's arithmetic is not the Poseidon2-and-Grumpkin toolkit the circuits are optimised for.

It would also leave discovery tags, proof soundness and account signatures where they are; the message layer is one of several rows in the table.

## References

### Aztec documentation

- [Keys](https://docs.aztec.network/developers/docs/foundational-topics/accounts/keys) — key types, app-siloing, address derivation, `Ivpk_m` kept as a point for encrypt-to-address
- [Note discovery](https://docs.aztec.network/developers/docs/foundational-topics/advanced/storage/note_discovery) — tags, the four tagging-secret strategies, handshakes, the sync process
- [Note delivery](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/note_delivery) — delivery modes, which strategies can back constrained delivery
- [Public execution and the AVM](https://docs.aztec.network/developers/docs/foundational-topics/advanced/circuits/public_execution) — Grumpkin operations and Poseidon2 supported in public; AES-128 not
- [Contract creation](https://docs.aztec.network/developers/docs/foundational-topics/contract_creation) — the partial address and salt behind `pre_address`

### Cryptography

- [FIPS 203, Module-Lattice-Based Key-Encapsulation Mechanism Standard](https://csrc.nist.gov/pubs/fips/203/final) — ML-KEM, with its 768-byte and 1,088-byte ciphertexts
- [H. Krawczyk, "Cryptographic Extraction and Key Derivation: The HKDF Scheme", IACR ePrint 2010/264](https://eprint.iacr.org/2010/264) — the key-extraction lemma the framework cites for deriving AES keys from `S` with Poseidon2
- [Elliptic-curve Diffie–Hellman](https://en.wikipedia.org/wiki/Elliptic-curve_Diffie%E2%80%93Hellman) — the exchange, as cited in the framework's own docstring

### Analyzed source

- [AztecProtocol/aztec-nr](https://github.com/AztecProtocol/aztec-nr) — analyzed at tag [v5.2.0](https://github.com/AztecProtocol/aztec-nr/tree/v5.2.0), commit [`22e152679f69a2307fdb1b17f60fd4f51a3fd4f5`](https://github.com/AztecProtocol/aztec-nr/tree/22e152679f69a2307fdb1b17f60fd4f51a3fd4f5), 2026-09-17: `aztec/src/keys/ephemeral.nr`, `aztec/src/keys/ecdh_shared_secret.nr`, `aztec/src/messages/encryption/aes128.nr`, `aztec/src/messages/encoding.nr`, `aztec/src/messages/delivery/handshake.nr`, `aztec/src/messages/delivery/tag_secret_source.nr`, `aztec/src/oracle/random.nr`
- [AztecProtocol/aztec-packages](https://github.com/AztecProtocol/aztec-packages) — analyzed at tag [v5.2.0](https://github.com/AztecProtocol/aztec-packages/tree/v5.2.0), commit [`49a592109ec4f18d79212b43d621891aaf36f7b6`](https://github.com/AztecProtocol/aztec-packages/tree/49a592109ec4f18d79212b43d621891aaf36f7b6), 2026-09-17: `noir-projects/noir-protocol-circuits/crates/types/src/address/aztec_address.nr` (`to_address_point`, address computation), `constants.nr` (`PRIVATE_LOG_SIZE_IN_FIELDS = 16`), `noir-projects/noir-contracts/contracts/standard/handshake_registry_contract/src/main.nr`; the `@aztec/stdlib` (`computeAddressSecret`) and `@aztec/pxe` (`getSharedSecrets`) packages at 5.2.0

### Related articles

- [Randomness on Aztec — One Oracle, Four Uses, and Why the Circuit Never Checks It]({{site.url_complet}}/2026/09/17/aztec-randomness-notes-oracle-unconstrained/)
- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
- [Native Account Abstraction on Aztec, Compared with ERC-4337]({{site.url_complet}}/2026/09/09/aztec-native-account-abstraction-vs-erc-4337/)
- [ML-KEM — The Module-Lattice Key-Encapsulation Standard (FIPS 203)]({{site.url_complet}}/2026/06/29/ml-kem-fips-203-post-quantum-key-encapsulation/)
- [ML-DSA — The Module-Lattice Digital Signature Standard (FIPS 204)]({{site.url_complet}}/2026/06/29/ml-dsa-fips-204-post-quantum-signatures/)
- [Chiffrement hybride sur les courbes elliptiques avec ECIES]({{site.url_complet}}/2022/04/22/elliptic-curve-integrated-encryption-scheme-ecies/)
