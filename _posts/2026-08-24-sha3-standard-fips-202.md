---
layout: post
title: "The SHA-3 Standard (FIPS 202) — A Second Family of Hash Functions"
date:   2026-08-24
lang: en
locale: en-GB
categories: cryptography
tags: cryptography sha-3 keccak sponge fips-202 hash sha-2 hash-competition
description: Why NIST ran a hash competition, what FIPS 202 standardized, how the four SHA3 hash functions differ from SHA-2, and the rules governing their approved use.
image: /assets/article/cryptographie/sha3/2026-08-24-sha3-standard-fips-202.png
isMath: true
---

[FIPS 202](https://doi.org/10.6028/NIST.FIPS.202) is the SHA-3 standard, published in August 2015 at the end of an eight-year public competition. It specifies six functions: the hash functions SHA3-224, SHA3-256, SHA3-384 and SHA3-512, and the extendable-output functions SHAKE128 and SHAKE256.

SHA-3 is not a replacement for SHA-2, and it was not standardized because SHA-2 was failing. Both families remain approved, both are recommended, and [FIPS 180-4](https://doi.org/10.6028/NIST.FIPS.180-4) was never withdrawn. What SHA-3 provides is a second family built on different principles, so that a break in one leaves the other standing.

This article covers why NIST ran the competition, what the standard actually specifies, how the four SHA3 hash functions compare with their SHA-2 counterparts, and the conformance rules governing what an implementation may and may not claim. The extendable-output half of the standard is treated separately in [SHAKE128 — The Extendable-Output Function of the SHA-3 Standard]({{site.url_complet}}/2026/08/24/shake128-extendable-output-function-fips-202/), which goes into the sponge construction and the XOF-specific hazards in more depth.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why NIST Ran a Hash Competition

Between 2004 and 2005 the cryptanalytic ground under the deployed hash functions shifted. Xiaoyun Wang and co-authors published practical collisions for MD5, collisions for SHA-0, and a collision attack on SHA-1 requiring roughly $$2^{69}$$ operations rather than the $$2^{80}$$ a 160-bit output should demand. MD5 and SHA-1 were the two hash functions the internet actually ran on.

The immediate concern was not SHA-2, which resisted those techniques and still does. The concern was structural. MD5, SHA-1 and SHA-2 are all **Merkle-Damgård** constructions, iterating a compression function over message blocks, and SHA-2 inherits a good deal of design DNA from SHA-1. An advance that generalized from SHA-1 to SHA-2 was not obviously impossible, and had it arrived, every approved hash function would have fallen at once. There was no second option to migrate to.

NIST announced the SHA-3 competition in November 2007 on that reasoning. It received 64 submissions, of which 51 met the requirements for the first round; 14 advanced to the second; five became finalists, namely BLAKE, Grøstl, JH, Keccak and Skein. On 2 October 2012 NIST selected **Keccak**, designed by Guido Bertoni, Joan Daemen, Michaël Peeters and Gilles Van Assche. Daemen was already a co-designer of Rijndael, which had become AES through the same kind of open process.

Keccak won on a combination of a large security margin, a design unlike anything in the SHA-2 lineage, and hardware performance well ahead of the other finalists. That second property was the point of the exercise. A finalist that resembled SHA-2 would have provided a faster hash function but not an insurance policy.

Two things followed that the competition had not planned for. Draft FIPS 202 appeared in 2014 and the final standard in August 2015, by which point SHA-2 was more entrenched than ever and no attack had materialised. And in February 2017, well after publication, the SHAttered result produced the first practical SHA-1 collision, confirming the direction of the 2005 work without touching SHA-2. SHA-3 therefore arrived as a hedge rather than a rescue, which is precisely how the standard is written.

## What FIPS 202 Specifies

The standard defines three layers, and it is worth separating them because they carry different approval status.

- **The `KECCAK-p[b, nr]` permutations.** A family parameterized by width $$b$$ and round count $$nr$$. The standard generalizes the original Keccak-f permutations by making the round count an input, which lets future documents specify reduced-round or narrower variants.
- **`KECCAK[c]`**, the sponge over `KECCAK-p[1600, 24]` with multi-rate padding, parameterized only by capacity.
- **The six SHA-3 functions**, each a mode of `KECCAK[c]` with a fixed capacity, a domain-separation suffix, and either a fixed or a caller-chosen output length.

![The KECCAK-p permutation family at the base, the KECCAK sponge with multi-rate padding above it, and the six approved SHA-3 modes on top, each with its own capacity and suffix]({{site.url_complet}}/assets/article/cryptographie/sha3/fips202-layers-concept.png)

Only the last layer is generally approved. `KECCAK-p[1600, 24]` is approved **only within an approved mode**, and the intermediate functions (`KECCAK[c]`, RawSHAKE128, RawSHAKE256) likewise. An implementation that exposes the raw permutation as a primitive and builds its own construction on top is outside the standard, whatever its merits.

All six functions share one permutation:

| Function | Type | Output | Capacity $$c$$ | Rate $$r$$ (bytes) | Suffix |
|----------|------|--------|------------|----------------|--------|
| SHA3-224 | hash | 224 | 448 | 144 | `01` |
| SHA3-256 | hash | 256 | 512 | 136 | `01` |
| SHA3-384 | hash | 384 | 768 | 104 | `01` |
| SHA3-512 | hash | 512 | 1024 | 72 | `01` |
| SHAKE128 | XOF | any $$d$$ | 256 | 168 | `1111` |
| SHAKE256 | XOF | any $$d$$ | 512 | 136 | `1111` |

For the four hash functions the capacity is twice the digest length. That rule is set by **preimage** resistance rather than by collisions: a hash function is specified to behave like a random $$d$$-bit function, so it must offer $$2^{d}$$ preimage resistance, and a sponge delivers that only when $$2^{c/2}$$ reaches $$2^{d}$$. Collision resistance is $$2^{d/2}$$ in every case, capped by the output size rather than by the capacity.

## SHA-3 and SHA-2 Are Different Constructions

The design divergence that justified the competition is visible in one comparison.

| | SHA-2 | SHA-3 |
|---|---|---|
| Construction | Merkle-Damgård | Sponge |
| Core primitive | Compression function (block cipher in Davies-Meyer) | Permutation `KECCAK-p[1600, 24]` |
| Internal state | 256 or 512 bits | 1600 bits, of which only the rate is exposed |
| Message schedule | Yes, per block | None; blocks are XORed into the state |
| Length extension | Applies | Does not apply |
| 2nd preimage vs long messages | Degrades with message length | No degradation |
| Constants | Fractional parts of roots of small primes | LFSR-generated round constants |
| Typical software speed | Faster on general-purpose CPUs | Slower without hardware support |
| Hardware cost | Higher | Lower, and highly parallel |

Two rows carry most of the practical weight.

**Length extension.** A Merkle-Damgård hash outputs its entire final state, so an attacker who knows `SHA-256(secret || msg)` and the length of the secret can resume the computation and produce `SHA-256(secret || msg || padding || anything)` without knowing the secret. This is why the naive MAC `H(key || message)` is unsafe with SHA-2 and why HMAC's nested structure exists. A sponge never emits its capacity, so the output does not reveal the state, and the attack has no foothold. With SHA-3, `H(key || message)` is a sound MAC shape.

**Second preimage resistance against long messages.** For SHA-2 the strength against second preimages degrades as $$n - \log_2(\text{len}(M)/B)$$, where $$B$$ is the block length: hashing a very long message measurably weakens the guarantee. The SHA-3 column in the standard's own table carries no such term. SHA3-256 offers 256 bits regardless of message length, while SHA-256 offers $$256 - \log_2(\text{len}(M)/512)$$.

The one row that favours SHA-2 is software speed. On a general-purpose CPU without hardware acceleration, SHA-256 is typically faster than SHA3-256, and modern x86 and ARM parts carry SHA-256 instructions that widen the gap considerably. SHA-3 was optimised for hardware, where its permutation is compact and parallel. This is a large part of why adoption has been slow: for most deployments SHA-2 is not broken, is faster, and is already there.

## The Four Hash Functions

The four hash functions are defined from `KECCAK[c]` by appending a two-bit suffix and fixing the output length:

```text
SHA3-224(M) = KECCAK[448] (M || 01, 224)
SHA3-256(M) = KECCAK[512] (M || 01, 256)
SHA3-384(M) = KECCAK[768] (M || 01, 384)
SHA3-512(M) = KECCAK[1024](M || 01, 512)
```

They offer the same digest lengths as SHA-224, SHA-256, SHA-384 and SHA-512, deliberately, so that either family can be substituted for the other in a protocol that names a digest size.

The security strengths follow from those lengths:

| Function | Collision | Preimage | 2nd preimage |
|----------|-----------|----------|--------------|
| SHA3-224 | 112 | 224 | 224 |
| SHA3-256 | 128 | 256 | 256 |
| SHA3-384 | 192 | 384 | 384 |
| SHA3-512 | 256 | 512 | 512 |

Canonical digests of the empty string, useful as the first check on any implementation:

```text
SHA3-224("") = 6b4e03423667dbb73b6e15454f0eb1abd4597f9a1b078e3f5b5a6bc7
SHA3-256("") = a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a
SHA3-384("") = 0c63a75b845e4f7d01107d852e4c2485c51a50aaaa94fc61995e71bbee983a2a
               c3713831264adb47fb6bd1e058d5f004
SHA3-512("") = a69f73cca23a9ac5c8b567dc185a756e97c982164fe25859e0d1dcc1475c80a6
               15b2123af1f5f94c11e3e9402c3ac558f500199d95b6d3e301758586281dcd26

SHA3-256("abc") = 3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532
```

Note the direction of the capacity trade. SHA3-512 withholds 1024 of the 1600 state bits, so only 72 bytes of message are absorbed per invocation of the permutation, against 136 for SHA3-256. **SHA3-512 is therefore close to twice as slow as SHA3-256**, which inverts the intuition carried over from SHA-2, where SHA-512 is often the faster of the two on 64-bit hardware because it processes larger blocks with the same number of rounds.

## The Sponge and the Permutation, Briefly

The mechanism underneath all six functions is covered in depth in the [companion article on SHAKE128]({{site.url_complet}}/2026/08/24/shake128-extendable-output-function-fips-202/); this is the short version.

The state is 1600 bits, split into a **rate** $$r$$ that input and output touch and a **capacity** $$c$$ that neither touches, with $$r + c = 1600$$. Absorbing XORs each message block into the rate and applies the permutation; squeezing reads the rate and applies the permutation again if more output is needed. All security follows from the capacity, which is why $$c$$ and not the digest length is the parameter that distinguishes the six functions.

Before absorbing begins, the message receives its domain suffix and then `pad10*1`, which appends a `1` bit, enough `0` bits, and a final `1` bit to reach a multiple of the rate. It always adds at least two bits, so a message that exactly fills the rate still gets an extra block.

![Appending the 01 suffix, padding to a multiple of 136 bytes, absorbing each block into the 1600-bit state through 24 Keccak rounds, then reading 256 bits of the rate as the digest]({{site.url_complet}}/assets/article/cryptographie/sha3/sha3-hash-workflow.png)

`KECCAK-p[1600, 24]` treats the state as a 5 by 5 by 64 array and applies 24 rounds of five step mappings: **theta** diffuses column parities, **rho** rotates each lane, **pi** permutes lane positions, **chi** supplies the only non-linearity through `a ^= (~b) & c` on each 5-bit row, and **iota** XORs a round constant into one lane to break the symmetry between rounds. The whole permutation is XOR, AND, NOT and rotation, with no lookup tables and no data-dependent branches, so it is constant-time by construction.

## Domain Separation

Each mode appends a distinct suffix to the message before padding, so two different functions can never present the same input to the permutation. This is what makes it safe for six functions to share one permutation.

| Domain | Suffix | First padding byte |
|--------|--------|--------------------|
| SHA3-224/256/384/512 | `01` | `0x06` |
| SHAKE128 / SHAKE256 | `1111` | `0x1F` |
| RawSHAKE128 / RawSHAKE256 | `11` | `0x07` |
| cSHAKE (SP 800-185) | `00` | `0x04` |
| Original Keccak (pre-standard) | none | `0x01` |

The suffix also reserves room for future work. FIPS 202 states outright that additional modes of `KECCAK-p[1600, 24]`, and modes of other `KECCAK-p` permutations, may be approved later, and the encoding space is laid out so they can be added without colliding with the six functions already defined. [SP 800-185](https://doi.org/10.6028/NIST.SP.800-185) took up that room in 2016 with cSHAKE, KMAC, TupleHash and ParallelHash.

## Conformance and Approved Use

FIPS 202 draws several lines that matter to anyone claiming compliance.

- **The four SHA3 functions are approved cryptographic hash functions**, usable anywhere an approved hash is required, including inside HMAC.
- **SHAKE128 and SHAKE256 are approved XOFs but are not approved as hash functions.** Their approved uses are left to NIST Special Publications, and the reason for the distinction is the related-output property described in Annex A.2 of the standard.
- **`KECCAK-p[1600, 24]` is approved only inside an approved mode**, as are `KECCAK[c]` and the RawSHAKE functions.
- **Conformance is tested through the Cryptographic Algorithm Validation Program.** Only validated implementations comply.
- **An implementation may restrict** the message bit lengths and XOF output lengths it supports, at the cost of interoperability. It may also replace any procedure in the standard with a mathematically equivalent one, which is what permits the lane-oriented implementations everyone actually writes.

For HMAC, the input block size $$B$$ is the rate in bytes, which is not the value a developer carrying habits over from SHA-2 would guess:

| Function | SHA3-224 | SHA3-256 | SHA3-384 | SHA3-512 |
|----------|----------|----------|----------|----------|
| HMAC block size $$B$$ (bytes) | 144 | 136 | 104 | 72 |

Getting $$B$$ wrong produces a function that is self-consistent and interoperates with nothing. Note also that because SHA-3 resists length extension, HMAC is available but not necessary; KMAC from SP 800-185 is the construction NIST recommends for keyed use of these primitives.

## The Ethereum keccak256 Confusion

A recurring practical error involving FIPS 202 has nothing to do with the standard's contents: the assumption that Ethereum's `keccak256` computes SHA3-256.

It does not. The Keccak team's competition submission appended no domain suffix, and Ethereum standardized on that pre-standard construction before FIPS 202 was published. Solidity's `keccak256`, the EVM opcode at `0x20`, contract address derivation, `CREATE2`, event topics and Merkle-Patricia trie hashing all use the original padding of `0x01 … 0x80`. FIPS 202 appends `01` first, giving `0x06 … 0x80`. Same permutation, same capacity, one byte of difference, entirely different digests:

```text
keccak256("")  = c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470
SHA3-256("")   = a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a
```

Ethereum's opcode was in fact named `SHA3` for years before being renamed `KECCAK256` to end the confusion. Libraries published under the name `sha3` have shipped one algorithm under the other's name, so an implementation should be pinned against published test vectors rather than trusted by its name. The two are not interchangeable and neither is a truncation of the other.

## Conclusion

FIPS 202 standardizes a hash family built on a sponge over the `KECCAK-p[1600, 24]` permutation, alongside rather than in place of SHA-2. The four SHA3 hash functions match SHA-2's digest lengths, set their capacity at twice the digest length to reach the preimage resistance a random function of that size would offer, and gain two properties SHA-2 lacks: immunity to length extension, and second preimage resistance that does not decay with message length. The cost is software speed on CPUs that accelerate SHA-256 and not Keccak, which is the main reason SHA-2 remains the default a decade after publication. The standard also draws its approval boundaries narrowly: the permutation is approved only inside an approved mode, and the two SHAKE functions are approved as XOFs and deliberately not as hash functions.

![Mindmap of FIPS 202 covering the competition, the three specification layers, the four hash functions, the SHA-2 contrast, conformance rules and the keccak256 confusion]({{site.url_complet}}/assets/article/cryptographie/sha3/2026-08-24-sha3-standard-fips-202.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **FIPS 202** | The SHA-3 standard, published August 2015, specifying the KECCAK-p permutations, the KECCAK sponge, and six approved functions. |
| **Keccak** | The sponge-based algorithm by Bertoni, Daemen, Peeters and Van Assche that won the SHA-3 competition in October 2012. |
| **Merkle-Damgård** | The iterated compression-function construction behind MD5, SHA-1 and SHA-2, from which SHA-3 deliberately departs. |
| **Sponge construction** | The framework behind SHA-3: absorb input into part of a fixed state, permute, then squeeze output from that same part. |
| **Rate ($$r$$)** | The portion of the 1600-bit state that input enters and output leaves; equal to the HMAC input block size $$B$$. |
| **Capacity ($$c$$)** | The portion of the state untouched by input and output, equal to twice the digest length for the SHA3 hash functions. |
| **KECCAK-p[1600, 24]** | The 1600-bit, 24-round permutation shared by all six functions, approved only within an approved mode. |
| **Domain separation** | Appending a mode-specific suffix before padding so that distinct functions never present the same input to the permutation. |
| **Length extension** | The Merkle-Damgård attack that computes a hash of an extended message from the hash of the original; it does not apply to sponges. |
| **CAVP** | The Cryptographic Algorithm Validation Program, through which an implementation is tested for conformance to the standard. |

### Security Implementation Checklist

#### Selection and approved use

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | A SHA3 function is chosen where a fixed-length digest is required, not a truncated SHAKE output. | SHAKE is not approved as a hash function, and its outputs at different lengths are prefixes of one another. |
| ☐ | The digest length is chosen for the collision resistance actually needed, at $$d/2$$ bits. | SHA3-224 provides 112-bit collision resistance, below the 128-bit floor most current policy requires. |
| ☐ | `KECCAK-p[1600, 24]` is used only inside an approved mode, never as a bare primitive under a custom construction. | The result falls outside FIPS 202 and carries none of the standard's analysis or validation. |
| ☐ | Claims of conformance rest on CAVP validation, not on passing a handful of self-selected vectors. | An implementation correct on short inputs can still fail on multi-block or boundary-length messages. |

#### Construction and encoding

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The `01` suffix is appended before padding, giving `0x06` as the first padding byte. | Omitting it computes original Keccak rather than SHA-3; the two disagree on every input. |
| ☐ | The capacity matches the digest length as $$c = 2d$$, and the rate follows as $$1600 - c$$. | A larger rate raises throughput while silently lowering preimage resistance below the claimed level. |
| ☐ | `pad10*1` always appends at least two bits, so a message that exactly fills the rate gets an additional block. | A message and a shorter one collide at block boundaries, breaking collision resistance. |
| ☐ | HMAC uses the rate as the block size $$B$$: 144, 136, 104 or 72 bytes. | Using 64 or 128 bytes produces a MAC that interoperates with no other implementation. |
| ☐ | Implementations are checked against vectors for multi-block, boundary-length and long messages, not only the empty string. | Errors confined to the absorbing loop survive a single-vector check. |

#### Implementation hygiene

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The permutation uses only XOR, AND, NOT and rotation, with no lookup tables and no secret-dependent branches. | Adding a table or a branch on state introduces a timing side channel into a primitive that had none. |
| ☐ | The full 1600-bit state is zeroised after any keyed or secret-bearing use. | The capacity retains key-derived material after the call returns. |
| ☐ | A codebase using both `keccak256` and SHA-3 names them distinctly and pins each against its own test vectors. | The two are silently interchanged, producing digests that no counterparty reproduces. |
| ☐ | Only the round count and width specified by the standard are used. | Reduced-round variants carry no analysed security margin and are non-conformant. |

## Frequently Asked Questions

**Q: If SHA-2 is not broken, why does SHA-3 exist?**

For structural diversity rather than to fix a failure. MD5, SHA-1 and SHA-2 are all Merkle-Damgård constructions, and SHA-2 shares design lineage with SHA-1, which fell to the 2004 to 2005 cryptanalysis and then to a practical collision in 2017. Had that line of attack generalised to SHA-2, every approved hash function would have been affected simultaneously and there would have been nowhere to migrate.

SHA-3 is built on a sponge over a permutation, so an advance against the Merkle-Damgård structure does not carry over. Both families remain approved and FIPS 180-4 was never withdrawn.

**Q: Why is SHA3-512 slower than SHA3-256, when SHA-512 is often faster than SHA-256?**

Because the two families scale in opposite directions. In SHA-2, SHA-512 works on 1024-bit blocks with 64-bit words and roughly the same round count as SHA-256, so on 64-bit hardware it can process more message per unit of work.

In SHA-3 the permutation is the same 1600-bit, 24-round function regardless of digest length, and a longer digest is bought entirely with capacity. SHA3-512 sets $$c = 1024$$, leaving only 72 bytes of rate per permutation call against SHA3-256's 136. Roughly half the message is absorbed per unit of work, so it runs close to half the speed.

**Q: Does SHA-3 need HMAC?**

Not for the reason SHA-2 does. HMAC's nested structure exists to defeat length extension, which is a property of the Merkle-Damgård construction. A sponge never outputs its capacity, so the digest does not reveal the internal state and `SHA3-256(key || message)` cannot be extended the way `SHA-256(key || message)` can.

HMAC-SHA3 is nonetheless defined and approved, and the standard supplies the block sizes for it. For new designs NIST recommends KMAC from SP 800-185, which is built directly on cSHAKE and binds the output length into the input.

**Q: What is the difference between KECCAK-p, KECCAK[c], and SHA3-256?**

They are three layers of the same specification, with different approval status:

- **`KECCAK-p[b, nr]`** is the permutation family, parameterized by width and round count. It is approved only inside an approved mode.
- **`KECCAK[c]`** is the sponge over `KECCAK-p[1600, 24]` with multi-rate padding, parameterized only by capacity. Also an intermediate function, approved only within a mode.
- **SHA3-256** is a fully specified mode: `KECCAK[512](M || 01, 256)`, with the capacity, the domain suffix and the output length all fixed.

Only the third layer is a function an implementation may expose and claim conformance for.

**Q: Why does the capacity equal twice the digest length for the SHA3 hash functions?**

Because preimage resistance is the binding constraint. A hash function is specified to behave like a random $$d$$-bit function, which means $$2^{d}$$ preimage resistance, and generic attacks against a sponge cost about $$2^{c/2}$$, so $$c$$ must reach $$2d$$ for the sponge to deliver it.

Collision resistance does not drive the choice: it is $$2^{d/2}$$ regardless, capped by the size of the output rather than by the capacity. This is also why SHAKE128, which claims 128 bits of security overall rather than matching a $$d$$-bit random function, can run at $$c = 256$$ and absorb more message per permutation call.

**Q: Ethereum uses Keccak. Does that mean Solidity's `keccak256` is SHA3-256?**

No. Ethereum adopted the competition submission before FIPS 202 was finalised, and the standard later added a two-bit `01` suffix to every hash input for domain separation. Ethereum's construction appends nothing, so its first padding byte is `0x01` where SHA-3's is `0x06`.

The two therefore produce completely different digests for the same input, and neither is a truncation of the other, despite sharing the permutation and the 512-bit capacity. The EVM opcode was renamed from `SHA3` to `KECCAK256` to reduce exactly this confusion.

**Q: Why has SHA-3 adoption been slow?**

Three reasons compound. SHA-2 is not broken, so there is no forcing event of the kind that moved deployments off MD5 and SHA-1. SHA-3 is generally slower in software on general-purpose CPUs, and the SHA-256 instructions now present on mainstream x86 and ARM parts widen that gap, since no equivalent acceleration for Keccak is as widely available. And migrating a hash function means touching protocols, certificates and stored digests across a whole system for a benefit that is contingent on a future attack.

Where SHA-3 has become established is in new designs with no legacy: the post-quantum standards ML-KEM, ML-DSA and SLH-DSA all build on SHAKE, and hardware implementations benefit from Keccak's compact, parallel structure.

## References

### Standards

- [FIPS 202 — SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions](https://doi.org/10.6028/NIST.FIPS.202)
- [FIPS 180-4 — Secure Hash Standard (SHS)](https://doi.org/10.6028/NIST.FIPS.180-4)
- [NIST SP 800-185 — SHA-3 Derived Functions: cSHAKE, KMAC, TupleHash and ParallelHash](https://doi.org/10.6028/NIST.SP.800-185)
- [NIST SP 800-107 Rev. 1 — Recommendation for Applications Using Approved Hash Algorithms](https://doi.org/10.6028/NIST.SP.800-107r1)
- [FIPS 198-1 — The Keyed-Hash Message Authentication Code (HMAC)](https://doi.org/10.6028/NIST.FIPS.198-1)

### The competition

- [SHA-3 Cryptographic Hash Algorithm Competition](https://csrc.nist.gov/projects/hash-functions/sha-3-project)
- [NIST IR 7896 — Third-Round Report of the SHA-3 Cryptographic Hash Algorithm Competition](https://doi.org/10.6028/NIST.IR.7896)
- [The Keccak Reference, Version 3.0](https://keccak.team/files/Keccak-reference-3.0.pdf)
- [Cryptographic Sponge Functions](https://keccak.team/files/CSF-0.1.pdf)
- [Keccak Team](https://keccak.team/)
- [SHAttered — The first collision for full SHA-1](https://shattered.io/)
- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [SHAKE128 — The Extendable-Output Function of the SHA-3 Standard (FIPS 202)]({{site.url_complet}}/2026/08/24/shake128-extendable-output-function-fips-202/)
- [HMAC - Hash-Based Message Authentication Code]({{site.url_complet}}/2024/11/27/hmac/)
- [SLH-DSA — The Stateless Hash-Based Signature Standard (FIPS 205)]({{site.url_complet}}/2026/06/29/slh-dsa-fips-205-hash-based-signatures/)
