---
layout: post
title: "SHAKE128 — The Extendable-Output Function of the SHA-3 Standard (FIPS 202)"
date:   2026-08-24
lang: en
locale: en-GB
categories: cryptography
tags: cryptography sha-3 shake128 keccak sponge fips-202 xof hash
description: How SHAKE128 (FIPS 202) turns the Keccak sponge into an extendable-output function, with its rate, capacity, domain separation and related-output hazard.
image: /assets/article/cryptographie/sha3/2026-08-24-shake128-extendable-output-function-fips-202.png
isMath: true
---

[FIPS 202](https://doi.org/10.6028/NIST.FIPS.202), published in August 2015, is the SHA-3 standard. It specifies six functions built on a single permutation: four fixed-length hash functions (SHA3-224, SHA3-256, SHA3-384 and SHA3-512) and two extendable-output functions, SHAKE128 and SHAKE256. The two XOFs were the first functions of their kind that NIST standardized, and they differ from hash functions in one respect that the standard treats as significant enough to withhold approval of them as hash functions.

SHAKE128 takes a message and an output length, and returns exactly that many bits. The length is an argument of the call rather than a property of the function. That is what "extendable-output" means, and it is the source of both the flexibility that makes SHAKE128 useful and the single hazard that a caller has to design around.

This article works through the sponge construction that SHAKE128 is built on, the Keccak permutation underneath it, the specific parameters that distinguish SHAKE128 from the other five functions in the standard, its security strengths, the related-output property described in Annex A.2 of the specification, and the role it now plays inside the post-quantum standards. It is the second of a pair: [The SHA-3 Standard (FIPS 202)]({{site.url_complet}}/2026/08/24/sha3-standard-fips-202/) covers the standard as a whole, including the competition that produced it, the four SHA3 hash functions and the comparison with SHA-2, while this one stays with the extendable-output half.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The SHA-3 Standard and Where SHAKE128 Fits

SHA-3 came out of a public competition that NIST ran from 2007 to 2012, won by **Keccak**, designed by Guido Bertoni, Joan Daemen, Michaël Peeters and Gilles Van Assche. The motivation was not that SHA-2 was broken. It was that SHA-1 had fallen and SHA-2 shares its underlying design, so a successful attack on the Merkle-Damgård structure would have left no approved alternative standing. FIPS 202 therefore **supplements** [FIPS 180-4](https://doi.org/10.6028/NIST.FIPS.180-4) rather than replacing it: SHA-2 is a Merkle-Damgård construction over a block cipher, SHA-3 is a sponge over a permutation, and an advance against one is unlikely to transfer to the other.

All six functions are modes of operation of one permutation, `KECCAK-p[1600, 24]`. They differ only in three parameters: how many bits of internal state are withheld from the caller, what suffix is appended to the message, and whether the output length is fixed.

| Function | Type | Output | Capacity $$c$$ | Rate $$r$$ (bits) | Rate (bytes) | Suffix |
|----------|------|--------|------------|---------------|--------------|--------|
| SHA3-224 | hash | 224 | 448 | 1152 | 144 | `01` |
| SHA3-256 | hash | 256 | 512 | 1088 | 136 | `01` |
| SHA3-384 | hash | 384 | 768 | 832 | 104 | `01` |
| SHA3-512 | hash | 512 | 1024 | 576 | 72 | `01` |
| **SHAKE128** | **XOF** | **any $$d$$** | **256** | **1344** | **168** | `1111` |
| SHAKE256 | XOF | any $$d$$ | 512 | 1088 | 136 | `1111` |

Two conventions in this table are worth reading carefully. For the four hash functions the capacity is always twice the digest length, so the parameters follow from the name. For the two XOFs the suffix "128" and "256" denotes a **security strength, not an output length**, which is the opposite of what the hash function names mean. SHAKE128 does not produce 128 bits of output; it produces however many bits were requested, at up to 128 bits of security.

## The Sponge Construction

A sponge function is built from three components: a permutation $$f$$ on a fixed width $$b$$, a **rate** $$r$$, and a padding rule. The remaining state is the **capacity**:

$$
\begin{aligned}
r + c = b = 1600 \quad \text{for every function in FIPS 202.}
\end{aligned}
$$

The capacity is the part of the state that input never enters and output never leaves. Every security claim about a sponge function traces back to that separation, which is why $$c$$ rather than the digest length is the parameter that sets the security level.

Operation has two phases. During **absorbing**, the padded message is cut into $$r$$-bit blocks; each block is XORed into the first $$r$$ bits of the state and the permutation is applied. During **squeezing**, the first $$r$$ bits of the state are emitted, and if more output is needed the permutation is applied again and another $$r$$ bits are taken. The process stops once enough bits have been produced.

![Message blocks are XORed into the rate of a 1600-bit state and interleaved with the Keccak permutation while absorbing, then output is read from the rate while the capacity stays untouched]({{site.url_complet}}/assets/article/cryptographie/sha3/shake128-sponge-construction.png)

Written out, the sponge is short:

```text
SPONGE[f, pad, r](N, d):
  1. P = N || pad(r, len(N))          # pad to a multiple of the rate
  2. n = len(P)/r ;  c = b - r
  3. S = 0^b                          # 1600 zero bits
  4. for i = 0 .. n-1:                # ABSORB
        S = f(S XOR (P_i || 0^c))
  5. Z = ""                           # SQUEEZE
  6. repeat:
        Z = Z || first r bits of S
        if d <= len(Z): return first d bits of Z
        S = f(S)
```

The detail that matters most for an XOF is in step 6. The requested length $$d$$ decides **how many** bits are returned; it has no influence on **what** those bits are. Nothing in the absorbing phase or in the permutation depends on $$d$$. Conceptually the output is an infinite stream and the caller reads a prefix of it, which is precisely the behaviour discussed later under related outputs.

## The Keccak-p[1600, 24] Permutation

The permutation treats its 1600 bits as a three-dimensional array $$A$$ of shape 5 by 5 by 64, indexed by $$A[x, y, z]$$ and mapped from a bit string $$S$$ by $$A[x, y, z] = S[64(5y + x) + z]$$. The 64-bit runs at constant $$x$$ and $$y$$ are called **lanes**, and a 64-bit implementation holds the state as 25 lane words.

One round applies five step mappings in a fixed order, and the permutation is 24 such rounds:

```text
Rnd(A, ir) = iota( chi( pi( rho( theta(A) ) ) ), ir )
```

Each step has one job:

- **theta** XORs every bit with the parity of two columns, one at $$x-1$$ and one at $$x+1$$ shifted by one position in $$z$$. This is the diffusion step, and it is linear.
- **rho** rotates each lane by a fixed offset that depends on its coordinates. The offsets run from 0 for the lane at the origin up to 62 after reduction modulo 64, which spreads bits along the third dimension.
- **pi** permutes the positions of the 25 lanes without altering their contents.
- **chi** is the only non-linear step. Across each 5-bit row it computes `a ^= (~b) & c`, giving the round an algebraic degree of 2. All of SHA-3's non-linearity comes from this one operation.
- **iota** XORs a round constant into the lane at the origin. The constants come from a small LFSR and differ in every round, which is what stops the 24 rounds from being 24 copies of the same function and blocks the slide attacks that symmetry would allow.

![One Keccak-p round in order: theta diffuses column parities, rho rotates lanes, pi permutes lane positions, chi adds non-linearity, iota injects the round constant, over 24 rounds]({{site.url_complet}}/assets/article/cryptographie/sha3/keccak-p-round-concept.png)

The permutation uses only XOR, AND, NOT and rotation. There are no lookup tables and no data-dependent branches, so a straightforward implementation is constant-time by construction. That property is a consequence of the design rather than something an implementer has to add, and it is one reason SHAKE128 is a comfortable choice inside larger algorithms that handle secrets.

## Assembling SHAKE128

SHAKE128 is the sponge over `KECCAK-p[1600, 24]` with capacity 256, plus a four-bit suffix appended to the message before padding:

```text
SHAKE128(M, d) = KECCAK[256] (M || 1111, d)
               = SPONGE[KECCAK-p[1600, 24], pad10*1, 1344] (M || 1111, d)
```

The padding rule, `pad10*1`, appends a `1` bit, as many `0` bits as needed, and a final `1` bit, so that the total length is a multiple of the rate. It always adds **at least two bits**, which means a message whose length is already an exact multiple of the rate still receives a whole additional block. Skipping that case is one of the more common implementation errors.

For byte-aligned messages the suffix and the padding collapse into a small number of concrete bytes. With $$m$$ the message length in bytes and $$r$$ the rate in bits, the number of padding bytes is

$$
\begin{aligned}
q = (r/8) - (m \bmod (r/8)),
\end{aligned}
$$

and the bytes themselves are fixed by the suffix. FIPS 202 uses a least-significant-bit-first convention inside each byte, which is why the four suffix bits and the leading padding bit land in the low bits of the first appended byte:

| $$q$$ | Bytes appended to $$M$$ |
|---|---|
| 1 | `0x9F` |
| 2 | `0x1F 0x80` |
| > 2 | `0x1F`, then $$q-2$$ bytes of `0x00`, then `0x80` |

![Appending the 1111 suffix, padding to a multiple of 168 bytes, absorbing each block through the Keccak permutation, then squeezing 168-byte blocks until the requested length is reached]({{site.url_complet}}/assets/article/cryptographie/sha3/shake128-generation-workflow.png)

The canonical starting point for checking an implementation is the empty message:

```text
SHAKE128("", 256) = 7f9c2ba4e88f827d616045507605853ed73b8093f6efbc88eb1a6eacfa66ef26
```

## Why the Capacity Is 256 Bits

The choice of capacity is where SHAKE128 differs from every other function in the standard, and it explains the function's performance.

Generic attacks against a sponge cost roughly $$2^{c/2}$$ operations, so a capacity of 256 bits supports 128 bits of security. Fixing $$c = 256$$ leaves $$r = 1344$$ bits, or 168 bytes, absorbed per invocation of the permutation.

SHA3-256 is constrained differently, and the binding constraint is preimage resistance rather than collision resistance. It is specified to behave like a random 256-bit function, which means 256 bits of preimage resistance, and a sponge reaches that only when $$2^{c/2}$$ is at least $$2^{256}$$. That forces $$c = 2d = 512$$ and leaves 136 bytes per permutation call. SHAKE128 makes the weaker claim of 128 bits overall, so the smaller capacity is enough. Collision resistance is 128 bits either way, capped for SHA3-256 by its 256-bit output rather than by its capacity.

The consequence is that SHAKE128 processes about 23 percent more message per permutation than SHA3-256 at the same collision-resistance level, and can then emit output indefinitely at 168 bytes per additional call. Where an algorithm needs a long pseudorandom stream rather than a fixed digest, this is the reason SHAKE128 is chosen over repeated hashing.

## Security Strengths

Annex A of FIPS 202 gives the strengths of all six functions. The two XOF rows are parameterized by the requested output length $$d$$:

| Function | Output | Collision | Preimage | 2nd preimage |
|----------|--------|-----------|----------|--------------|
| SHA3-256 | 256 | 128 | 256 | 256 |
| SHAKE128 | $$d$$ | $$\min(d/2, 128)$$ | $$\ge \min(d, 128)$$ | $$\min(d, 128)$$ |
| SHAKE256 | $$d$$ | $$\min(d/2, 256)$$ | $$\ge \min(d, 256)$$ | $$\min(d, 256)$$ |

Two readings follow. A short output caps the strength: at $$d = 224$$, SHAKE128 and SHAKE256 both give 112 bits of collision resistance, because no function with a 224-bit output can do better. Their preimage resistance at that length differs, however, at 128 bits for SHAKE128 against 224 for SHAKE256, which is the point at which the "128" in the name becomes the binding constraint. A long output raises it: once $$d$$ exceeds $$r + c/2$$ the preimage resistance exceeds the nominal strength, and beyond 1600 bits a preimage probably does not exist at all.

The SHA-3 functions also gain a property that the SHA-2 family lacks. Because the capacity is never emitted, a SHA-3 or SHAKE output reveals nothing about the internal state, so **length extension does not apply**. Given `SHA-256(secret || msg)` an attacker can compute `SHA-256(secret || msg || padding || suffix)` without knowing the secret; the same manoeuvre against SHAKE128 has nothing to work with. A related benefit shows up in the second-preimage column: for SHA-2 that strength degrades with message length as $$n - \log_2(\text{len}(M)/B)$$, while the SHA-3 figures carry no such term.

## The Related-Output Hazard

This is the property that distinguishes an XOF from a hash function, and the reason FIPS 202 approves SHAKE128 as an XOF but not as a hash function.

Because the requested length selects bits from a stream that does not depend on it, outputs at different lengths are prefixes of one another:

$$
\begin{aligned}
\mathrm{Trunc}\big(\mathrm{SHAKE128}(M, d+e),\ d\big) = \mathrm{SHAKE128}(M, d).
\end{aligned}
$$

Two hash functions never behave this way. SHA3-256 of a message is not an extension of its SHA3-224, even though the two share almost all of their structure. But every construction that builds a variable-length output by concatenating or truncating a hash does behave this way, and an XOF makes the behaviour explicit rather than accidental.

The specification's own example is a key derivation. Two parties agree to derive a key as `SHAKE128(keymaterial, keylength)`. One believes `keylength` is 112 bits, the other is induced to use 168. The results are not two independent keys:

```text
SHAKE128(keymaterial, 112) = f g
SHAKE128(keymaterial, 168) = f g h        (each letter = 56 bits)
```

The two parties now hold keys sharing their first 112 bits, and against Triple DES, whose structure the example targets, that overlap is exploitable.

The fix is not to avoid XOFs. It is to make the output length part of the input, so that a disagreement about the length produces unrelated outputs rather than nested ones. A key derivation function that encodes the length and the key type into the message it hashes has no such failure mode, which is exactly what KMAC does with `right_encode(L)`. Domain separation through a customisation string achieves the same end by a different route.

## Domain Separation

Every mode in FIPS 202 appends a short suffix to the message before `pad10*1` runs. The suffix is what keeps the six functions from ever presenting the same input to the permutation, so an output of one can never be mistaken for an output of another.

| Domain | Suffix | Byte form (with padding) |
|--------|--------|--------------------------|
| SHA3-224/256/384/512 | `01` | `0x06` … `0x80` |
| SHAKE128 / SHAKE256 | `1111` | `0x1F` … `0x80` |
| RawSHAKE128 / RawSHAKE256 | `11` | `0x07` … `0x80` |
| cSHAKE (SP 800-185) | `00` | `0x04` … `0x80` |
| Original Keccak (pre-standard) | none | `0x01` … `0x80` |

SHAKE128 is defined a second time in the standard by way of an intermediate function, `RawSHAKE128(J, d) = KECCAK[256](J || 11, d)`, with `SHAKE128(M, d) = RawSHAKE128(M || 11, d)`. Expanding gives the same `M || 1111` as before. The split exists because the two bit pairs do different jobs: the pair RawSHAKE appends performs the domain separation, while the pair SHAKE appends provides compatibility with the Sakura coding scheme, which reserves the encoding space needed for the tree-hashing variants that parallelize long-message hashing.

The last row of the table is the one that causes trouble in practice. The Keccak submission to the competition appended no suffix at all, and Ethereum standardized on that pre-standard form. Solidity's `keccak256`, the EVM opcode at `0x20`, contract address derivation and event topics all use the original padding. Same permutation, same capacity, different digest:

```text
keccak256("")  = c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470
SHA3-256("")   = a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a
```

Libraries named `sha3` have shipped one under the other's name, so an implementation should be pinned against test vectors rather than trusted by name.

### The SP 800-185 Layer

FIPS 202 deliberately left the approved uses of XOFs to be specified separately, and [SP 800-185](https://doi.org/10.6028/NIST.SP.800-185) supplies them. **cSHAKE128** is SHAKE128 with a function name and a customisation string prepended, using the `00` suffix, and it falls back to plain SHAKE128 when both strings are empty so the two domains cannot collide. **KMAC128** is the approved keyed construction built on cSHAKE128, and it binds the output length into the input, which removes the related-output problem for its fixed-length form. The same document defines TupleHash, which hashes a sequence of strings unambiguously, and ParallelHash.

Because the sponge already resists length extension, `H(key || message)` is a sound MAC shape with SHAKE128, unlike with SHA-2. KMAC remains the approved construction, and it is preferable for the length binding rather than for any length-extension concern.

## SHAKE128 in Deployed Cryptography

SHAKE128's main role today is inside other standards, where it is used as a deterministic source of pseudorandom bytes rather than as a digest.

- **[ML-KEM](https://doi.org/10.6028/NIST.FIPS.203) (FIPS 203)** expands a 32-byte public seed into the matrix $$\mathbf A$$ with SHAKE128, so the matrix is regenerated on demand instead of transmitted. The number of bytes needed is not known in advance, because coefficients that fall outside the modulus are rejected and resampled, so the algorithm reads from the stream until enough have been accepted.
- **[ML-DSA](https://doi.org/10.6028/NIST.FIPS.204) (FIPS 204)** uses SHAKE128 and SHAKE256 for the equivalent expansion and sampling steps.
- **[SLH-DSA](https://doi.org/10.6028/NIST.FIPS.205) (FIPS 205)** offers a full family of parameter sets built on SHAKE256.

The pattern is the same in each: the algorithm needs an arbitrary quantity of reproducible pseudorandom bytes from a short seed, which is what an XOF provides directly and what a fixed-length hash provides only through a counter-based construction that the designer would then have to specify and defend.

## Conclusion

SHAKE128 is the sponge over `KECCAK-p[1600, 24]` with a 256-bit capacity and a `1111` domain suffix, absorbing and emitting 168 bytes per permutation call. The capacity, not the output length, sets its 128-bit security level, and holding the capacity at the minimum that supports that level is what makes it faster than SHA3-256 while producing output of any length. The same design decision that provides the flexibility also produces the related-output property: outputs at different lengths are prefixes of one another, so any caller deriving keys must bind the length into the input or use KMAC, which does so already. Within FIPS 202, SHAKE128 is approved as an XOF and deliberately not as a hash function, and its principal use is now as a seed-expansion primitive inside the post-quantum standards.

![Mindmap of SHAKE128 covering the sponge construction, the Keccak-p permutation, parameters and padding, security strengths, the related-output hazard, domain separation and deployment]({{site.url_complet}}/assets/article/cryptographie/sha3/2026-08-24-shake128-extendable-output-function-fips-202.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Sponge construction** | A framework that builds a variable-input, variable-output function from a fixed-width permutation, a rate, and a padding rule. |
| **Rate ($$r$$)** | The number of state bits that input is XORed into and that output is read from, 1344 bits for SHAKE128. |
| **Capacity ($$c$$)** | The state bits that input never enters and output never leaves; 256 bits for SHAKE128, and the parameter that sets the security level. |
| **KECCAK-p[1600, 24]** | The 1600-bit permutation of 24 rounds underlying all six FIPS 202 functions, identical to KECCAK-f[1600]. |
| **State array** | The 5 by 5 by 64 arrangement of the 1600 state bits on which the step mappings are defined. |
| **Extendable-output function (XOF)** | A function whose output can be extended to any requested length, the length being an argument rather than a fixed property. |
| **Domain separation** | Appending a distinct suffix per mode so that different functions never present the same input to the permutation. |
| **Multi-rate padding (pad10*1)** | The rule appending a `1` bit, zero or more `0` bits, and a final `1` bit to reach a multiple of the rate, always adding at least two bits. |
| **Absorbing and squeezing** | The two phases of a sponge: XORing message blocks into the rate and permuting, then reading output blocks from the rate and permuting. |
| **Related outputs** | The property that a shorter XOF output is a prefix of a longer one for the same message, which hash functions do not exhibit. |

### Security Implementation Checklist

#### Construction and encoding

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The `1111` suffix is appended before padding, giving `0x1F` as the first padding byte (`0x9F` when only one byte is added). | Omitting it computes original Keccak, not SHAKE128; using `01` computes a SHA-3 hash. Digests silently disagree with every other implementation. |
| ☐ | `pad10*1` always appends at least two bits, so a message that exactly fills the rate receives an additional whole block. | A missing final block makes a message and its truncation collide, destroying collision resistance at block boundaries. |
| ☐ | The capacity is 256 bits and the rate is 1344 bits (168 bytes). | A larger rate raises throughput while silently lowering the security level below 128 bits. |
| ☐ | Lane loading follows the FIPS 202 bit convention, with $$A[x,y,z] = S[64(5y+x)+z]$$ and least-significant-bit-first byte ordering. | A byte-order error produces a self-consistent but non-interoperable function that passes internal tests and fails against published vectors. |
| ☐ | The implementation is validated against published test vectors, including variable-output-length and long-message cases, not only the empty string. | Errors confined to multi-block absorbing or repeated squeezing survive a single-vector check. |

#### Output length and key derivation

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Any key derivation binds the output length, and the type or purpose of the key, into the input to SHAKE128. | Two parties disagreeing on the length derive prefix-related keys rather than independent ones, as in the Triple DES example of Annex A.2. |
| ☐ | Independent uses of one secret are domain-separated, by cSHAKE customisation string or an explicit unambiguous prefix. | One output stream reused for two purposes makes the second value derivable from the first. |
| ☐ | Requested output lengths are checked against Annex A: collision resistance is $$\min(d/2, 128)$$, not 128 for every $$d$$. | Truncating to 128 bits yields 64-bit collision resistance while the name suggests 128. |
| ☐ | Variable-length inputs are concatenated unambiguously, with explicit length prefixes or TupleHash. | Distinct input tuples map to the same byte string and therefore to the same output. |
| ☐ | KMAC is used for keyed operations in preference to an ad-hoc construction, and KMACXOF only where an unbound output length is intended. | KMACXOF does not bind the length, so the related-output property returns where the caller may not expect it. |

#### Implementation hygiene

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The permutation uses only XOR, AND, NOT and rotation, with no lookup tables and no secret-dependent branches. | Introducing a table or a branch on state creates a timing side channel in a primitive that had none. |
| ☐ | The full 1600-bit state is zeroised after any keyed or secret-bearing use. | The capacity retains key-derived material after the call returns, exposing it to a later memory disclosure. |
| ☐ | Absorbing does not resume after squeezing has begun. | Re-absorbing into a squeezed state implements a duplex construction whose security is outside the FIPS 202 analysis. |
| ☐ | Only `KECCAK-p[1600, 24]` is used, and only within an approved mode. | Reduced-round or other-width variants are non-conformant and carry no analysed security margin. |

## Frequently Asked Questions

**Q: What does the "128" in SHAKE128 refer to, given that the output can be any length?**

It is the security strength in bits, not the output size. This is the opposite of the convention used for the hash functions in the same standard, where the number after the dash is the digest length: SHA3-256 always produces 256 bits, while SHAKE128 produces whatever length was requested. The 128 is a ceiling set by the 256-bit capacity, and it is reached only when the requested output is long enough. At $$d = 128$$, for example, SHAKE128 gives 64 bits of collision resistance, not 128.

**Q: Why does SHAKE128 have a smaller capacity than SHA3-256, when both offer 128-bit collision resistance?**

Because they make different claims about preimage resistance, and the capacity has to be sized for the stronger claim:

- SHA3-256 is specified to behave like a random 256-bit function, so it claims 256 bits of preimage resistance. A sponge reaches that only when $$2^{c/2}$$ is at least $$2^{256}$$, which forces $$c = 512$$.
- SHAKE128 claims 128 bits of security overall, so $$c = 256$$ suffices.

Collision resistance is 128 bits in both cases, capped for SHA3-256 by the size of its own output rather than by its capacity. The practical effect is that SHAKE128 absorbs 168 bytes per permutation call against SHA3-256's 136, roughly 23 percent more message at the same collision-resistance level.

**Q: What is the related-output property, and why does it stop SHAKE128 from being an approved hash function?**

The requested length determines how many bits are returned but not what they are, so the output for a given message is a prefix of the output for the same message at any greater length: $$\mathrm{Trunc}(\mathrm{SHAKE128}(M, d+e), d) = \mathrm{SHAKE128}(M, d)$$. Two hash functions never relate this way, and a developer substituting an XOF for a hash function would not expect it.

FIPS 202 therefore approves SHAKE128 as an XOF and withholds approval of it as a hash function, leaving the approved uses of XOFs to be specified in NIST Special Publications. The concern is not that the function is weak, but that a caller may assume an independence between different-length outputs that it does not provide.

**Q: How does a caller safely derive keys of different lengths from one secret with SHAKE128?**

By making the length part of what is hashed, so that different lengths produce unrelated streams rather than nested ones. Encoding the length and the key's purpose into the input is enough; a customisation string with cSHAKE128 achieves the same separation. KMAC128 does this by construction, appending `right_encode(L)` to its input, which is why it is the approved keyed construction. The one case to watch is KMACXOF128, which deliberately encodes a length of zero so that its output stays extendable, restoring the prefix property for callers who want it.

**Q: What distinguishes SHAKE128 from Ethereum's `keccak256`, given that both use the same permutation?**

The message suffix appended before padding. SHAKE128 appends `1111`, producing `0x1F` as the first padding byte; the original Keccak submission that Ethereum adopted appends nothing, producing `0x01`. They also differ in capacity, since `keccak256` uses 512 bits to match its 256-bit output while SHAKE128 uses 256.

The consequence is that the two produce entirely different values for the same input, and neither is a truncation of the other. Because some libraries have shipped one under the name of the other, an implementation should be checked against published vectors instead of trusted on its name.

**Q: Why do the post-quantum standards use SHAKE128 for matrix expansion rather than a hash function?**

Because the amount of output required is not known in advance. ML-KEM regenerates its public matrix from a 32-byte seed by sampling coefficients and rejecting any that fall outside the modulus, so the number of bytes consumed depends on how many rejections occur. A fixed-length hash would force the designer to specify a counter-based expansion and argue for its soundness; an XOF supplies an indefinite stream from the seed directly, and the algorithm simply reads until it has enough. The same reasoning applies to noise sampling and to ML-DSA's mask expansion.

**Q: Does SHAKE128 need an HMAC wrapper to be used as a MAC?**

No. HMAC's nested structure exists to defeat length extension, which affects Merkle-Damgård functions such as SHA-2 but not sponge functions, because the capacity is never emitted and an attacker cannot reconstruct the internal state from the output. `SHAKE128(key || message, d)` is therefore not vulnerable in the way `SHA-256(key || message)` is, and the wrapper would add cost without adding security. The approved construction is nonetheless KMAC128, and the reason is the length binding described above rather than any length-extension concern.

## References

### Standards

- [FIPS 202 — SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions](https://doi.org/10.6028/NIST.FIPS.202)
- [FIPS 180-4 — Secure Hash Standard (SHS)](https://doi.org/10.6028/NIST.FIPS.180-4)
- [NIST SP 800-185 — SHA-3 Derived Functions: cSHAKE, KMAC, TupleHash and ParallelHash](https://doi.org/10.6028/NIST.SP.800-185)
- [NIST SP 800-107 Rev. 1 — Recommendation for Applications Using Approved Hash Algorithms](https://doi.org/10.6028/NIST.SP.800-107r1)

### Post-quantum standards using SHAKE

- [FIPS 203 — Module-Lattice-Based Key-Encapsulation Mechanism Standard](https://doi.org/10.6028/NIST.FIPS.203)
- [FIPS 204 — Module-Lattice-Based Digital Signature Standard](https://doi.org/10.6028/NIST.FIPS.204)
- [FIPS 205 — Stateless Hash-Based Digital Signature Standard](https://doi.org/10.6028/NIST.FIPS.205)

### Keccak design documents

- [The Keccak Reference, Version 3.0](https://keccak.team/files/Keccak-reference-3.0.pdf)
- [Cryptographic Sponge Functions](https://keccak.team/files/CSF-0.1.pdf)
- [Keccak Team](https://keccak.team/)
- [SHA-3 Cryptographic Hash Algorithm Competition](https://csrc.nist.gov/projects/hash-functions/sha-3-project)

### Tools

- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [The SHA-3 Standard (FIPS 202) — A Second Family of Hash Functions]({{site.url_complet}}/2026/08/24/sha3-standard-fips-202/)
- [ML-KEM — The Module-Lattice Key-Encapsulation Standard (FIPS 203)]({{site.url_complet}}/2026/06/29/ml-kem-fips-203-post-quantum-key-encapsulation/)
- [ML-DSA — The Module-Lattice Digital Signature Standard (FIPS 204)]({{site.url_complet}}/2026/06/29/ml-dsa-fips-204-post-quantum-signatures/)
