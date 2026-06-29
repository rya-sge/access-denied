---
layout: post
title: "SLH-DSA — The Stateless Hash-Based Signature Standard (FIPS 205)"
date:   2026-06-29
lang: en
locale: en-GB
categories: cryptography
tags: cryptography post-quantum hash-based slh-dsa sphincs fips-205 digital-signature
description: How SLH-DSA (FIPS 205) builds a stateless post-quantum signature from hash functions alone, layering WOTS+, XMSS, a hypertree, and FORS, with the twelve parameter sets and the small/fast trade-off.
image: /assets/article/cryptographie/hash-based/2026-06-29-slh-dsa-fips-205-hash-based-signatures.png
isMath: true
---

SLH-DSA is the stateless hash-based digital signature scheme standardized by NIST in [FIPS 205](https://doi.org/10.6028/NIST.FIPS.205), published on 13 August 2024. It is the standardized form of [SPHINCS+](https://sphincs.org/). Where ML-DSA (FIPS 204) rests on the hardness of module lattice problems, SLH-DSA rests on essentially nothing beyond the security of its hash function: preimage and collision resistance. That makes it the most conservative post-quantum signature NIST standardized, at the cost of signatures measured in tens of kilobytes. This article builds the scheme from the bottom up (WOTS+ one-time signatures, XMSS Merkle trees, the hypertree, and FORS), then assembles key generation, signing, and verification, and closes with the twelve parameter sets and the small/fast trade-off.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## From SPHINCS+ to a Stateless Standard

The 2016 NIST Post-Quantum Cryptography process (82 submissions) selected a small first set of algorithms. Two of the signatures are lattice-based (ML-DSA and the draft Falcon). The third, SLH-DSA, is hash-based. NIST standardized it precisely because its security argument does not depend on lattice assumptions: if module lattices were one day found weaker than believed, a hash-based signature would still stand.

"Hash-based signature" is an old idea (Lamport, 1979; Merkle, 1979). The obstacle to deploying it has always been **state**. Classical Merkle-tree signatures consume a one-time key per signature and must record which keys have already been used; reusing a one-time key is catastrophic. The stateful hash-based schemes LMS and XMSS (standardized in [NIST SP 800-208](https://doi.org/10.6028/NIST.SP.800-208)) require the signer to persist and correctly update a counter, which is fragile in practice (a restored VM snapshot or a cloned device can silently reuse keys).

SLH-DSA removes the state. Instead of a counter, the signer pseudorandomly selects which one-time/few-time key to use, drawing from a key space so astronomically large that an accidental harmful collision is negligible across the $2^{64}$ signatures a key pair is allowed to produce. The "SLH" in the name is exactly this: **S**tate**L**ess **H**ash-based.

## Security From Hashing Alone

SLH-DSA is designed to be **existentially unforgeable under chosen-message attack (EUF-CMA)** when a key pair signs at most $2^{64}$ messages. Its security reduces to standard properties of the underlying hash function (one-wayness, collision resistance, and related notions), with no number-theoretic or lattice assumption. A large quantum computer running Grover's algorithm only halves the effective preimage security, which the parameter sets account for by sizing the output.

The three security parameters $n = 16, 24, 32$ bytes map directly to NIST categories 1, 3, and 5 (comparable to the key-search hardness of AES-128, AES-192, and AES-256). The trade-off for this conservative footing is size: SLH-DSA signatures range from roughly 8 KB to 50 KB, one to two orders of magnitude larger than ML-DSA.

## The Building Blocks

SLH-DSA is a tower of four constructions. From the bottom up: WOTS+ signs one hash value once; XMSS turns many WOTS+ keys into one reusable key via a Merkle tree; the hypertree chains XMSS trees so one short root can certify an enormous number of lower keys; FORS is a few-time signature that actually signs the message digest.

![SLH-DSA hypertree and FORS structure]({{site.url_complet}}/assets/article/cryptographie/hash-based/slh-dsa-hypertree-structure.png)

### WOTS+ — A One-Time Signature

WOTS+ (Winternitz One-Time Signature Plus) signs a single message by walking hash chains. Fix a Winternitz parameter $w = 2^{lg_w}$ (all FIPS 205 sets use $lg_w = 4$, so $w = 16$). The message digest is split into base-$w$ digits. For each digit, the signer starts from a secret chain value and applies the hash function $F$ a number of times equal to the digit, revealing the intermediate chain element as that digit's signature.

A checksum prevents forgery by incrementing digits. Without it, an attacker who saw a signature could advance any chain (hash forward) to forge a larger digit. The checksum is constructed so that increasing any message digit necessarily decreases the checksum, which an attacker cannot produce because advancing a checksum chain would itself require inverting $F$. The number of chains is $len = len_1 + len_2$, with $len_2 = 3$ for every standardized set.

![WOTS+ hash chain concept]({{site.url_complet}}/assets/article/cryptographie/hash-based/wots-plus-hash-chain-concept.png)

The public key compresses all chain endpoints with the function $T_\ell$. WOTS+ is strictly one-time: signing two different messages under the same key leaks enough chain elements to forge.

### XMSS — Many Uses From a Merkle Tree

A single WOTS+ key signs once. XMSS (eXtended Merkle Signature Scheme) bundles $2^{h'}$ WOTS+ public keys as the leaves of a binary Merkle hash tree of height $h'$. The root of that tree is the XMSS public key, a single $n$-byte value that stands in for all $2^{h'}$ one-time keys.

An XMSS signature is a WOTS+ signature plus the **authentication path**: the $h'$ sibling nodes along the route from the used leaf to the root. A verifier recomputes the WOTS+ public key from the signature, hashes it up the tree using the authentication path, and checks the result against the known root. XMSS is therefore a $2^{h'}$-time signature, but it is still stateful on its own (the leaves must not be reused).

### The Hypertree — Certifying Trees With Trees

A single XMSS tree of usable height cannot hold enough leaves for $2^{64}$ stateless signatures. The **hypertree (HT)** stacks XMSS trees in $d$ layers (FIPS 205 uses $d \in \{7, 8, 17, 22\}$). The top layer is one XMSS tree whose root is the public value $\mathbf{PK.root}$. Each XMSS tree at layers $0$ to $d-2$ has its root signed by a WOTS+ key in the tree one layer above. The total height is $h = d \cdot h'$, giving $2^{h}$ leaves at the bottom layer.

A hypertree signature is a chain of $d$ XMSS signatures: the bottom XMSS tree signs the payload, its root is certified by the next layer up, and so on to $\mathbf{PK.root}$. Only $\mathbf{PK.root}$ needs to be published; the rest of the enormous tree is generated on demand from seeds.

### FORS — A Few-Time Signature for the Message

What the hypertree ultimately certifies is not the message directly but a **FORS (Forest Of Random Subsets)** public key. FORS is a *few-time* signature, tolerant of a bounded number of reuses, which is what makes the stateless construction safe.

FORS uses $k$ independent Merkle trees, each with $2^a$ leaves built over secret values. The message digest is interpreted as $k$ indices, one per tree. The signature reveals, for each tree, the secret leaf at its index plus the authentication path to that tree's root. The $k$ roots are compressed into the FORS public key. Because each tree contributes one revealed secret per signature, a small number of signatures under the same FORS key leaks only a few secrets per tree, and the parameters are sized so that forging from this partial leakage stays infeasible across $2^{64}$ signatures.

## Key Generation

Key generation is short. The private key holds two secret $n$-byte seeds and a copy of the public key:

$$
\begin{aligned}
SK &= (\mathbf{SK.seed},\ \mathbf{SK.prf},\ \mathbf{PK.seed},\ \mathbf{PK.root}) && (4n \text{ bytes}) \\
PK &= (\mathbf{PK.seed},\ \mathbf{PK.root}) && (2n \text{ bytes}).
\end{aligned}
$$

$\mathbf{SK.seed}$ pseudorandomly generates every WOTS+ and FORS secret in the whole structure. $\mathbf{SK.prf}$ generates the per-signature randomizer. $\mathbf{PK.seed}$ provides domain separation across hash calls. The one computed value is the top-layer root:

$$
\begin{aligned}
\mathbf{PK.root} \leftarrow \mathsf{xmss\_node}(\mathbf{SK.seed},\ 0,\ h',\ \mathbf{PK.seed},\ \mathbf{ADRS}),
\end{aligned}
$$

with the address set to the top layer $d-1$. The public key is just $2n$ bytes: 32, 48, or 64 depending on the parameter set. Computing $\mathbf{PK.root}$ requires building the top-layer tree, which is why key generation is more expensive than for a number-theoretic scheme even though the key is tiny.

## Signing

An SLH-DSA signature has three parts (sizes in $n$-byte units):

```
Randomness  R           : n bytes
FORS sig    SIG_FORS     : k·(1 + a)·n bytes
Hypertree   SIG_HT       : (h + d·len)·n bytes
```

Signing (`slh_sign_internal`) proceeds as follows:

$$
\begin{aligned}
R &\leftarrow \mathsf{PRF_{msg}}(\mathbf{SK.prf},\ opt\_rand,\ M) && \text{(randomizer)} \\
digest &\leftarrow \mathsf{H_{msg}}(R,\ \mathbf{PK.seed},\ \mathbf{PK.root},\ M) && (m \text{ bytes}) \\
md &\leftarrow \text{first } \lceil k a / 8 \rceil \text{ bytes of } digest && \text{(FORS message)} \\
idx_{tree},\ idx_{leaf} &\leftarrow \text{remaining digest bits} && \text{(which key to use).}
\end{aligned}
$$

The digest is split into three pieces. The first selects which FORS leaves to open; the rest pseudorandomly select the bottom-layer XMSS tree ($idx_{tree}$) and the leaf within it ($idx_{leaf}$). The signer then signs the message digest with that FORS key, derives the FORS public key, and certifies it up the hypertree:

$$
\begin{aligned}
\mathsf{SIG_{FORS}} &\leftarrow \mathsf{fors\_sign}(md,\ \mathbf{SK.seed},\ \mathbf{PK.seed},\ \mathbf{ADRS}) \\
\mathsf{PK_{FORS}} &\leftarrow \mathsf{fors\_pkFromSig}(\mathsf{SIG_{FORS}},\ md,\ \mathbf{PK.seed},\ \mathbf{ADRS}) \\
\mathsf{SIG_{HT}} &\leftarrow \mathsf{ht\_sign}(\mathsf{PK_{FORS}},\ \mathbf{SK.seed},\ \mathbf{PK.seed},\ idx_{tree},\ idx_{leaf}).
\end{aligned}
$$

The output is $\mathsf{SIG} = (R \,\|\, \mathsf{SIG_{FORS}} \,\|\, \mathsf{SIG_{HT}})$. There is no rejection loop and no retry: signing is a single deterministic pass over a very large pseudorandom structure, which is what makes it slow rather than variable-time.

![SLH-DSA signing flow]({{site.url_complet}}/assets/article/cryptographie/hash-based/slh-dsa-signing-flow.png)

## Verification

Verification (`slh_verify_internal`) mirrors signing without any secret. It first rejects any signature whose length is not exactly $(1 + k(1+a) + h + d\cdot len)\cdot n$ bytes, then recomputes the same digest, $md$, and indices, and reconstructs the certification chain:

$$
\begin{aligned}
digest &\leftarrow \mathsf{H_{msg}}(R,\ \mathbf{PK.seed},\ \mathbf{PK.root},\ M) \\
\mathsf{PK_{FORS}} &\leftarrow \mathsf{fors\_pkFromSig}(\mathsf{SIG_{FORS}},\ md,\ \mathbf{PK.seed},\ \mathbf{ADRS}) \\
\text{return } &\mathsf{ht\_verify}(\mathsf{PK_{FORS}},\ \mathsf{SIG_{HT}},\ \mathbf{PK.seed},\ idx_{tree},\ idx_{leaf},\ \mathbf{PK.root}).
\end{aligned}
$$

The hypertree verification walks up all $d$ layers: it reconstructs each candidate WOTS+ public key from its signature, hashes it up its XMSS tree with the authentication path to obtain a candidate root, and uses that root as the message for the next layer up. The signature is valid if and only if the final candidate root at layer $d-1$ equals the published $\mathbf{PK.root}$. Every step is a forward hash computation, so verification is much faster than signing.

## Why Stateless Works

The danger in any hash-based scheme is reusing a one-time key. SLH-DSA never tracks state, so how does it avoid reuse? Two mechanisms combine:

1. **FORS is few-time, not one-time.** A handful of signatures under the same FORS key does not break it, because each reveals only one secret per tree. The parameters bound the forgery advantage even after the worst-case number of collisions across $2^{64}$ signatures.
2. **The index is pseudorandom over a vast space.** $idx_{tree}$ and $idx_{leaf}$ come from hashing the message with a fresh randomizer $R$. With a hypertree of height $h$ up to 68, the chance that two of the $2^{64}$ signatures land on the same FORS key often enough to matter is negligible.

The $2^{64}$ ceiling is generous: at ten billion signatures per second it would take over 58 years to reach it.

## Parameter Sets and the Small/Fast Trade-off

FIPS 205 approves **twelve** parameter sets: six value-sets, each instantiable with either SHA2 or SHAKE. The name encodes the hash family, the security strength, and whether the set is tuned for small signatures (`s`) or fast signing (`f`).

| Parameter set | $n$ | $h$ | $d$ | $h'$ | $a$ | $k$ | $m$ | Category | pk (B) | sig (B) |
|---------------|-----|-----|-----|------|-----|-----|-----|----------|--------|---------|
| SLH-DSA-(SHA2/SHAKE)-128s | 16 | 63 | 7 | 9 | 12 | 14 | 30 | 1 | 32 | 7 856 |
| SLH-DSA-(SHA2/SHAKE)-128f | 16 | 66 | 22 | 3 | 6 | 33 | 34 | 1 | 32 | 17 088 |
| SLH-DSA-(SHA2/SHAKE)-192s | 24 | 63 | 7 | 9 | 14 | 17 | 39 | 3 | 48 | 16 224 |
| SLH-DSA-(SHA2/SHAKE)-192f | 24 | 66 | 22 | 3 | 8 | 33 | 42 | 3 | 48 | 35 664 |
| SLH-DSA-(SHA2/SHAKE)-256s | 32 | 64 | 8 | 8 | 14 | 22 | 47 | 5 | 64 | 29 792 |
| SLH-DSA-(SHA2/SHAKE)-256f | 32 | 68 | 17 | 4 | 9 | 35 | 49 | 5 | 64 | 49 856 |

The `s` and `f` variants invert the same balance. A `small` set uses few hypertree layers ($d=7$ or $8$) with tall subtrees, which keeps signatures shorter but forces signing to build large Merkle trees (slow). A `fast` set uses many shallow layers ($d=22$) with a wider FORS, which speeds signing but roughly doubles the signature. The public key is always just $2n$ bytes, and the private key $4n$ bytes, regardless of variant.

The message digest length is fixed by the geometry:

$$
\begin{aligned}
m = \left\lceil \frac{h - h'}{8} \right\rceil + \left\lceil \frac{h'}{8} \right\rceil + \left\lceil \frac{k \cdot a}{8} \right\rceil.
\end{aligned}
$$

## Hedged vs Deterministic, Pure vs Pre-Hash

Two orthogonal choices mirror those in ML-DSA.

**Randomizer.** The value $opt\_rand$ feeding $\mathsf{PRF_{msg}}$ is either a fresh $n$-byte random value (the default **hedged** variant) or set to $\mathbf{PK.seed}$ (the **deterministic** variant). Hedged is recommended where side-channel or fault attacks matter; deterministic is available when no random source is present and makes signing reproducible.

**Message format.** The internal routine never sees the raw message; it sees $M'$ carrying a one-byte domain separator and a context string ($ctx$, at most 255 bytes):

- **Pure SLH-DSA:** $M' = \mathsf{toByte}(0,1) \,\|\, \mathsf{toByte}(|ctx|,1) \,\|\, ctx \,\|\, M$.
- **HashSLH-DSA (pre-hash):** $M' = \mathsf{toByte}(1,1) \,\|\, \mathsf{toByte}(|ctx|,1) \,\|\, ctx \,\|\, \mathsf{OID} \,\|\, \mathsf{PH}_M$, where $\mathsf{PH}_M$ is the message digest under an approved function (SHA-256, SHA-512, SHAKE128, SHAKE256) and $\mathsf{OID}$ identifies it.

The leading byte (0 vs 1) keeps pure and pre-hash signatures from being reinterpreted as one another. FIPS 205 prefers the pure version; the pre-hash version exists for modules that cannot stream a large message through $\mathsf{H_{msg}}$. Note that with HashSLH-DSA, a collision on the external pre-hash function would yield a forged message, so the digest must offer at least $8n$ bits of classical collision resistance.

## SLH-DSA vs ML-DSA: When to Use Which

| | ML-DSA (FIPS 204) | SLH-DSA (FIPS 205) |
|--|-------------------|--------------------|
| Family | Lattice (Fiat-Shamir with Aborts) | Hash-based (stateless) |
| Security basis | MLWE + SelfTargetMSIS | Hash preimage/collision only |
| Security goal | SUF-CMA | EUF-CMA (≤ $2^{64}$ signatures) |
| Public key | 1312–2592 B | 32–64 B |
| Signature | 2420–4627 B | 7 856–49 856 B |
| Signing speed | Fast | Slow (s) to moderate (f) |
| Main appeal | Balanced size and speed | Most conservative assumption |

The practical reading: ML-DSA is the default general-purpose post-quantum signature; SLH-DSA is the choice when the threat model demands the weakest possible cryptographic assumption and large signatures are acceptable, for example long-lived roots of trust or firmware signing where verification dominates and signatures are rare.

## Frequently Asked Questions

**Q: What assumption does SLH-DSA rely on, and why is that attractive?**

It relies only on standard security properties of its hash function: one-wayness (preimage resistance) and collision resistance. There is no integer-factorization, discrete-log, or lattice assumption. This is attractive because hash functions are old, heavily studied, and not threatened by Shor's algorithm; the only quantum speedup, Grover's, merely halves preimage security and is compensated by the output length. If a future cryptanalytic result weakened lattices, SLH-DSA would be unaffected.

**Q: What does "stateless" mean here, and why was it the hard problem to solve?**

Stateless means the signer keeps no mutable counter between signatures. Classical hash-based schemes use a one-time key per signature and must record which keys are spent; reusing one is catastrophic. Persisting that state correctly across crashes, VM snapshots, or device clones is error-prone. SLH-DSA replaces the counter with a pseudorandom index over an enormous key space and uses FORS, a few-time signature, so the rare index collisions that do occur are tolerated rather than fatal.

**Q: How do WOTS+, XMSS, the hypertree, and FORS fit together?**

Bottom-up: WOTS+ signs one hash value once by revealing positions along hash chains. XMSS collects $2^{h'}$ WOTS+ public keys as leaves of a Merkle tree and publishes only the root, turning many one-time keys into one reusable root plus authentication paths. The hypertree stacks $d$ XMSS trees so each tree's root is signed by the layer above, reducing the whole structure to a single public root $\mathbf{PK.root}$. FORS is a separate few-time signature that actually signs the message digest; the hypertree's job is to certify the FORS public key.

**Q: Concretely, what is the difference between the `s` and `f` parameter variants?**

They tune the hypertree and FORS geometry in opposite directions. The `small` variants use few layers (e.g. $d=7$) with tall subtrees: shorter signatures but slow signing, because building tall Merkle trees is expensive. The `fast` variants use many shallow layers (e.g. $d=22$) and a wider FORS: faster signing but signatures roughly twice as large. For example, SLH-DSA-128s produces 7 856-byte signatures while SLH-DSA-128f produces 17 088-byte signatures at the same category 1 security. Keys are the same size in both.

**Q: Combining the building blocks, trace what a verifier does to accept a signature.**

The verifier first checks the signature length matches the parameter set, then recomputes the message digest $\mathsf{H_{msg}}(R, \mathbf{PK.seed}, \mathbf{PK.root}, M)$ and splits it into the FORS message $md$ and the indices $idx_{tree}, idx_{leaf}$. From $\mathsf{SIG_{FORS}}$ and $md$ it reconstructs a candidate FORS public key. That candidate becomes the payload certified up the hypertree: for each of the $d$ layers it rebuilds the WOTS+ public key from the layer's signature, hashes it up the XMSS tree with the supplied authentication path, and feeds the resulting root to the next layer. Acceptance is exactly the condition that the final layer-$(d-1)$ root equals the published $\mathbf{PK.root}$. Every operation is a forward hash, so no secret and no inversion is involved.

**Q: Why is SLH-DSA signing slow and its signatures large compared with ML-DSA, and when does that trade-off pay off?**

Both costs come from the tower of hash trees. A signature must carry a FORS signature plus $d$ XMSS signatures (each a WOTS+ signature and an authentication path), which is thousands of $n$-byte hashes, hence 8–50 KB. Signing must build large Merkle trees from seeds, which is many thousands of hash calls. ML-DSA, by contrast, does a few NTT-based polynomial operations. The trade-off pays off when the application values the minimal-assumption security and the tiny public key over signature size and signing speed, and where signatures are produced rarely but must remain trustworthy for decades, such as firmware or root-certificate signing.

## Conclusion

SLH-DSA turns a hash function into a stateless signature by layering four constructions: WOTS+ one-time signatures, XMSS Merkle trees, a $d$-layer hypertree reducing everything to one public root, and FORS few-time signatures that sign the message digest. Statelessness comes from pseudorandomly selecting a FORS key over a space large enough that the few collisions occurring within $2^{64}$ signatures are absorbed by FORS's few-time tolerance. The security argument depends only on the hash function, which is its defining advantage and the reason NIST standardized it alongside the lattice-based ML-DSA. The cost is size and signing time: signatures of 8 to 50 KB and slow signing, against a public key of only 32 to 64 bytes. The twelve parameter sets let an implementer pick a hash family, a security category, and a point on the small/fast curve.

![SLH-DSA FIPS 205 mindmap]({{site.url_complet}}/assets/article/cryptographie/hash-based/2026-06-29-slh-dsa-fips-205-hash-based-signatures.png)

## References

- [FIPS 205 — Stateless Hash-Based Digital Signature Standard](https://doi.org/10.6028/NIST.FIPS.205)
- [FIPS 204 — Module-Lattice-Based Digital Signature Standard](https://doi.org/10.6028/NIST.FIPS.204)
- [SPHINCS+ — submission and specification](https://sphincs.org/)
- [NIST SP 800-208 — Recommendation for Stateful Hash-Based Signature Schemes](https://doi.org/10.6028/NIST.SP.800-208)
- [FIPS 202 — SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions](https://doi.org/10.6028/NIST.FIPS.202)
- [NIST Post-Quantum Cryptography Standardization](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Claude Code](https://claude.com/product/claude-code)
</content>
