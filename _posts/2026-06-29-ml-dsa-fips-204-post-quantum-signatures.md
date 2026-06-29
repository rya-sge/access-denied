---
layout: post
title: "ML-DSA — The Module-Lattice Digital Signature Standard (FIPS 204)"
date:   2026-06-29
lang: en
locale: en-GB
categories: cryptography
tags: cryptography post-quantum lattice ml-dsa dilithium fips-204 digital-signature
description: How ML-DSA (FIPS 204) builds a post-quantum digital signature from module lattices, the Fiat-Shamir with Aborts construction, rejection sampling, and the three NIST parameter sets.
image: /assets/article/cryptographie/lattice/2026-06-29-ml-dsa-fips-204-post-quantum-signatures.png
isMath: true
---

ML-DSA is the digital signature scheme standardized by NIST in [FIPS 204](https://doi.org/10.6028/NIST.FIPS.204), published on 13 August 2024. It is derived from [CRYSTALS-Dilithium](https://pq-crystals.org/dilithium/) and is designed to remain secure against an adversary equipped with a large-scale quantum computer. Unlike RSA and ECDSA, whose hardness rests on integer factorization and discrete logarithms (both broken by Shor's algorithm), ML-DSA reduces to the difficulty of lattice problems over module structures. This article works through the construction: the hard problems it relies on, the Fiat-Shamir with Aborts paradigm that shapes the signing loop, the rejection sampling that removes the secret-dependent bias, and the three parameter sets that target NIST security categories 2, 3, and 5.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## From the Quantum Threat to a Standard

Public-key cryptography deployed today rests on two number-theoretic assumptions: that factoring a large integer is hard, and that computing discrete logarithms in a finite group is hard. Both assumptions fail against a cryptographically relevant quantum computer running Shor's algorithm. A signature produced by RSA or ECDSA today can be forged by an adversary who later obtains such a machine, which threatens any signature that must remain valid for a long time (firmware roots of trust, certificate authorities, long-lived legal documents).

In 2016 NIST opened a public Post-Quantum Cryptography (PQC) standardization process. A total of 82 candidate algorithms were submitted, and after three rounds of analysis NIST selected the first set for standardization. ML-DSA is the lattice-based signature from that selection, derived from CRYSTALS-Dilithium and published as FIPS 204. Two companion standards were published the same day: [FIPS 203](https://doi.org/10.6028/NIST.FIPS.203) (ML-KEM, a key-encapsulation mechanism derived from Kyber) and [FIPS 205](https://doi.org/10.6028/NIST.FIPS.205) (SLH-DSA, a stateless hash-based signature derived from SPHINCS+).

ML-DSA is the recommended general-purpose post-quantum signature because it offers a balanced profile: signatures of a few kilobytes and signing and verification that are dominated by fast polynomial arithmetic. The hash-based SLH-DSA makes more conservative assumptions but produces much larger signatures, so ML-DSA is the default for most applications.

## The Hard Problems: MLWE and SelfTargetMSIS

The security of lattice signatures is usually phrased in terms of two problems. The **Learning With Errors (LWE)** problem asks an adversary to recover a secret vector $$\mathbf{s}$$ from a system of noisy linear equations $$\mathbf{A}\mathbf{s} + \mathbf{e} = \mathbf{b}$$, where $$\mathbf{A}$$ and $$\mathbf{b}$$ are given and the error $$\mathbf{e}$$ is small but unknown. The **Short Integer Solution (SIS)** problem asks for a non-zero short vector $$\mathbf{t}$$ satisfying $$\mathbf{A}\mathbf{t} = \mathbf{0}$$ over $$\mathbb{Z}_q$$. For appropriate parameters, both are intractable for the best known techniques, including lattice reduction and Gaussian elimination.

ML-DSA does not work over plain integer vectors. It replaces the module $$\mathbb{Z}_q^n$$ with a module over a polynomial ring $$R_q$$, which yields the **Module-LWE (MLWE)** and **Module-SIS (MSIS)** variants. Working over a ring lets the scheme use structured matrices and the Number Theoretic Transform for fast multiplication, which shrinks key sizes and accelerates arithmetic relative to an unstructured LWE scheme.

The unforgeability of ML-DSA rests on two assumptions. Key recovery (finding the secret from the public key) is an MLWE problem. Forging a signature without the secret is a non-standard variant of MSIS that NIST calls **SelfTargetMSIS**, which captures the way the challenge is bound to the message through a hash. ML-DSA is designed to be **strongly existentially unforgeable under chosen-message attack (SUF-CMA)**: even an adversary that can request signatures on messages of its choice cannot produce any new valid message-signature pair, including a second signature on a message that was already signed.

## The Algebraic Setting: Rings, Modules, and the NTT

All arithmetic happens in the ring

$$
\begin{aligned}
R_q = \mathbb{Z}_q[X] / (X^{256} + 1), \qquad q = 8380417 = 2^{23} - 2^{13} + 1.
\end{aligned}
$$

An element of $$R_q$$ is a polynomial of degree less than 256 with coefficients reduced modulo the prime $$q$$. The public matrix $$\mathbf{A}$$ is a $$k \times \ell$$ matrix over $$R_q$$, the secret vectors $$\mathbf{s}_1, \mathbf{s}_2$$ are vectors of polynomials with small coefficients, and the dimensions $$(k, \ell)$$ are what vary between parameter sets. The numerical suffix in the names ML-DSA-44, ML-DSA-65, and ML-DSA-87 records these dimensions: in ML-DSA-65 the matrix $$\mathbf{A}$$ is $$6 \times 5$$.

The prime $$q$$ was chosen so that $$X^{256} + 1$$ splits completely into linear factors modulo $$q$$. This is what makes the **Number Theoretic Transform (NTT)** available. The NTT is a ring isomorphism

$$
\begin{aligned}
\mathsf{NTT} : R_q \;\xrightarrow{\;\cong\;}\; T_q,
\end{aligned}
$$

where $$T_q$$ is the ring of length-256 coefficient arrays with entry-wise multiplication. Because the map is an isomorphism, $$\mathsf{NTT}(ab) = \mathsf{NTT}(a) \circ \mathsf{NTT}(b)$$, so a polynomial product (normally a convolution) becomes 256 independent coordinate-wise products. The value $$\zeta = 1753$$ is a 512th root of unity modulo $$q$$ and serves as the transform's twiddle factor. Matrix-vector products such as $$\mathbf{A}\mathbf{y}$$ are therefore computed by transforming both operands once, multiplying coordinate-wise, and transforming the result back. The standard mandates that no floating-point arithmetic be used anywhere, since rounding errors would produce incorrect results.

## The Fiat-Shamir with Aborts Construction

ML-DSA is a Schnorr-like signature. To see where it comes from, recall the Schnorr identification protocol, in which a prover demonstrates knowledge of a discrete log $$x$$ behind $$y = g^x$$ in three moves:

1. **Commitment.** The prover picks a random $$r$$ and sends $$g^r$$.
2. **Challenge.** The verifier replies with a random $$c$$.
3. **Response.** The prover returns $$s = r - cx$$, and the verifier checks $$g^s \cdot y^c = g^r$$.

The Fiat-Shamir heuristic turns this interactive protocol into a signature by replacing the verifier's random challenge with a hash of the commitment concatenated with the message. The lattice analogue keeps the same skeleton but works with matrices and short vectors. A prover who knows short secrets $$\mathbf{s}_1, \mathbf{s}_2$$ behind the public relation $$\mathbf{t} = \mathbf{A}\mathbf{s}_1 + \mathbf{s}_2$$ would proceed as follows:

1. **Commitment.** Sample a masking vector $$\mathbf{y}$$ with small coefficients and send $$\mathbf{w} = \mathbf{A}\mathbf{y}$$.
2. **Challenge.** Receive a small polynomial $$c$$.
3. **Response.** Return $$\mathbf{z} = \mathbf{y} + c\mathbf{s}_1$$, and the verifier checks that $$\mathbf{z}$$ is short and that $$\mathbf{A}\mathbf{z} - c\mathbf{t} \approx \mathbf{w}$$.

There is a problem the discrete-log version does not have. The response $$\mathbf{z} = \mathbf{y} + c\mathbf{s}_1$$ is biased in a direction that depends on the secret $$\mathbf{s}_1$$. Releasing many such responses would leak the secret. The fix is **rejection sampling**: the signer only releases $$\mathbf{z}$$ when every coefficient falls inside a fixed safe range $$(-(\gamma_1 - \beta), \gamma_1 - \beta)$$, and otherwise discards the attempt and restarts with a fresh mask $$\mathbf{y}$$. Conditioned on passing the test, the distribution of $$\mathbf{z}$$ is independent of the secret. This is the **Fiat-Shamir with Aborts** paradigm: the signer may abort and retry an attempt many times before it produces a publishable signature. The expected number of iterations is small (between roughly 4 and 5 for the standardized parameters), but it is not fixed.

![ML-DSA Fiat-Shamir with Aborts identification protocol]({{site.url_complet}}/assets/article/cryptographie/lattice/fiat-shamir-aborts-protocol.png)

ML-DSA layers several engineering refinements on top of this core idea:

- **Module structure** replaces unstructured matrices with polynomial matrices over $$R_q$$, enabling the NTT and shrinking sizes.
- The matrix $$\mathbf{A}$$ is **not stored**; it is regenerated on demand from a 32-byte seed $$\rho$$, so the public key carries the seed rather than the full matrix.
- The public vector $$\mathbf{t}$$ is **compressed**: its $$d = 13$$ low-order bits per coefficient are dropped, leaving $$\mathbf{t}_1$$ in the public key. The dropped part $$\mathbf{t}_0$$ is kept in the private key.
- A **hint** $$\mathbf{h}$$ is added to the signature so the verifier can reconstruct the high bits of $$\mathbf{w}$$ despite the compression of $$\mathbf{t}$$.
- The message is not signed directly; the signer signs a **message representative** $$\mu$$ derived by hashing the public-key hash together with the message, which provides additional binding properties.

## Key Generation

Key generation starts from a single 32-byte seed $$\xi$$ drawn from an approved random bit generator. Everything else is derived deterministically, which means the entire private key can later be regenerated from the seed alone.

The seed is expanded with SHAKE256 (the function $$\mathsf{H}$$) into three values: a 32-byte public seed $$\rho$$, a 64-byte private seed $$\rho'$$, and a 32-byte signing seed $$K$$. From these:

$$
\begin{aligned}
\mathbf{A} &\leftarrow \mathsf{ExpandA}(\rho) && \text{(public matrix, in NTT form)} \\
(\mathbf{s}_1, \mathbf{s}_2) &\leftarrow \mathsf{ExpandS}(\rho') && \text{(short secret vectors, coefficients in } [-\eta, \eta]) \\
\mathbf{t} &= \mathbf{A}\mathbf{s}_1 + \mathbf{s}_2 && \text{(the public value)} \\
(\mathbf{t}_1, \mathbf{t}_0) &\leftarrow \mathsf{Power2Round}(\mathbf{t}, d) && \text{(split into high and low bits).}
\end{aligned}
$$

The public key is $$pk = (\rho, \mathbf{t}_1)$$, and the private key is $$sk = (\rho, K, tr, \mathbf{s}_1, \mathbf{s}_2, \mathbf{t}_0)$$, where $$tr = \mathsf{H}(pk, 64)$$ is a 64-byte hash of the public key kept for fast use during signing. The compression of $$\mathbf{t}$$ into $$\mathbf{t}_1$$ is an efficiency optimization, not a security measure: the low-order bits of $$\mathbf{t}$$ can be recovered from a handful of signatures, so they are not treated as secret, but they are kept in the private key because the signer needs them to compute the hint.

## Signing: The Rejection Sampling Loop

Signing begins by binding the message to the key. The signer computes the message representative

$$
\begin{aligned}
\mu = \mathsf{H}\big(\mathsf{BytesToBits}(tr) \,\|\, M', \; 64\big),
\end{aligned}
$$

where $$M'$$ is the formatted message (the message wrapped with a domain separator and context string, described later). A per-signature private seed $$\rho'' = \mathsf{H}(K \,\|\, rnd \,\|\, \mu, 64)$$ drives the mask generation, where $$rnd$$ is a 32-byte random value in the default hedged variant.

The body of the algorithm is a loop that retries until an attempt passes every validity check. Each iteration, indexed by a counter $$\kappa$$, performs the following steps:

$$
\begin{aligned}
\mathbf{y} &\leftarrow \mathsf{ExpandMask}(\rho'', \kappa) && \text{(mask, coefficients in } [-\gamma_1 + 1, \gamma_1]) \\
\mathbf{w} &= \mathbf{A}\mathbf{y}, \qquad \mathbf{w}_1 = \mathsf{HighBits}(\mathbf{w}) && \text{(commitment)} \\
\tilde{c} &\leftarrow \mathsf{H}\big(\mu \,\|\, \mathsf{w1Encode}(\mathbf{w}_1), \; \lambda/4\big) && \text{(commitment hash)} \\
c &\leftarrow \mathsf{SampleInBall}(\tilde{c}) && \text{(challenge: } \tau \text{ non-zero } \pm 1 \text{ coefficients)} \\
\mathbf{z} &= \mathbf{y} + c\mathbf{s}_1 && \text{(response)} \\
\mathbf{r}_0 &= \mathsf{LowBits}(\mathbf{w} - c\mathbf{s}_2).
\end{aligned}
$$

Two validity checks then decide whether the attempt is acceptable. If $$\|\mathbf{z}\|_\infty \geq \gamma_1 - \beta$$, the response is too large and would leak information about $$\mathbf{s}_1$$, so the attempt is rejected. If $$\|\mathbf{r}_0\|_\infty \geq \gamma_2 - \beta$$, the low part of the commitment is too large for the verifier to reconstruct the high bits reliably, so the attempt is also rejected. Here $$\beta = \tau \cdot \eta$$ bounds the size of $$c\mathbf{s}_i$$.

If both checks pass, the signer computes the hint $$\mathbf{h} = \mathsf{MakeHint}(-c\mathbf{t}_0, \; \mathbf{w} - c\mathbf{s}_2 + c\mathbf{t}_0)$$, which records where the carry caused by dropping $$\mathbf{t}_0$$ changes the high bits. A final check rejects the attempt if $$\|c\mathbf{t}_0\|_\infty \geq \gamma_2$$ or if the hint has more than $$\omega$$ non-zero coefficients. When everything passes, the signature is

$$
\begin{aligned}
\sigma = \mathsf{sigEncode}(\tilde{c}, \; \mathbf{z} \bmod^{\pm} q, \; \mathbf{h}).
\end{aligned}
$$

The activity diagram below traces one pass through the loop, including the three points at which the attempt can be discarded.

![ML-DSA signing rejection sampling loop]({{site.url_complet}}/assets/article/cryptographie/lattice/ml-dsa-signing-loop.png)

## Verification

Verification is deterministic and does not retry. The verifier decodes $$pk = (\rho, \mathbf{t}_1)$$ and the signature $$\sigma = (\tilde{c}, \mathbf{z}, \mathbf{h})$$. If the hint was not properly byte-encoded, verification returns false immediately. The verifier then regenerates $$\mathbf{A}$$ from $$\rho$$, recomputes the message representative $$\mu$$ in exactly the same way the signer did, and recovers the challenge $$c = \mathsf{SampleInBall}(\tilde{c})$$.

The central step reconstructs the signer's commitment. The verifier computes

$$
\begin{aligned}
\mathbf{w}'_{\mathsf{Approx}} = \mathbf{A}\mathbf{z} - c\,\mathbf{t}_1 \cdot 2^d,
\end{aligned}
$$

then applies the hint to obtain the high bits $$\mathbf{w}'_1 = \mathsf{UseHint}(\mathbf{h}, \mathbf{w}'_{\mathsf{Approx}})$$. The algebra explains why this matches: because $$\mathbf{z} = \mathbf{y} + c\mathbf{s}_1$$ and $$\mathbf{t} = \mathbf{A}\mathbf{s}_1 + \mathbf{s}_2$$,

$$
\begin{aligned}
\mathbf{A}\mathbf{z} - c\mathbf{t} = \mathbf{A}\mathbf{y} - c\mathbf{s}_2 = \mathbf{w} - c\mathbf{s}_2 \approx \mathbf{w},
\end{aligned}
$$

and since $$c$$ and $$\mathbf{s}_2$$ are both small, $$\mathbf{w} - c\mathbf{s}_2$$ has the same high bits as $$\mathbf{w}$$. The compression $$\mathbf{t}_1 \cdot 2^d \approx \mathbf{t}$$ introduces a small discrepancy, and the hint corrects exactly that. The verifier then recomputes the commitment hash and accepts only if both conditions hold:

$$
\begin{aligned}
\|\mathbf{z}\|_\infty < \gamma_1 - \beta \quad \text{and} \quad \tilde{c} = \mathsf{H}\big(\mu \,\|\, \mathsf{w1Encode}(\mathbf{w}'_1), \; \lambda/4\big).
\end{aligned}
$$

The norm check confirms the response is short, and the hash equality confirms that the reconstructed commitment is consistent with the challenge that the signer hashed. The sequence diagram summarizes the exchange of derived values.

![ML-DSA verification flow]({{site.url_complet}}/assets/article/cryptographie/lattice/ml-dsa-verification.png)

## Parameter Sets and Sizes

FIPS 204 specifies three parameter sets, each targeting a different NIST security category. The table below collects the parameters that govern the constructions above.

| Parameter | ML-DSA-44 | ML-DSA-65 | ML-DSA-87 |
|-----------|-----------|-----------|-----------|
| $$q$$ (modulus) | 8380417 | 8380417 | 8380417 |
| $$d$$ (dropped bits) | 13 | 13 | 13 |
| $$\tau$$ (non-zero $$\pm 1$$ in $$c$$) | 39 | 49 | 60 |
| $$\lambda$$ (collision strength of $$\tilde{c}$$) | 128 | 192 | 256 |
| $$\gamma_1$$ (mask range) | $$2^{17}$$ | $$2^{19}$$ | $$2^{19}$$ |
| $$\gamma_2$$ (low-order rounding) | $$(q-1)/88$$ | $$(q-1)/32$$ | $$(q-1)/32$$ |
| $$(k, \ell)$$ (dimensions of $$\mathbf{A}$$) | (4, 4) | (6, 5) | (8, 7) |
| $$\eta$$ (secret range) | 2 | 4 | 2 |
| $$\beta = \tau \cdot \eta$$ | 78 | 196 | 120 |
| $$\omega$$ (max hint weight) | 80 | 55 | 75 |
| Expected repetitions | 4.25 | 5.1 | 3.85 |
| Claimed security category | 2 | 3 | 5 |

NIST does not quote a single "bits of security" number. Instead each parameter set is claimed to be at least as hard to break as a generic block cipher or hash function of a given size: category 2 is comparable to finding a SHA-256 collision, category 3 to recovering an AES-192 key, and category 5 to recovering an AES-256 key. The encoded key and signature sizes follow from the dimensions.

| Size (bytes) | ML-DSA-44 | ML-DSA-65 | ML-DSA-87 |
|--------------|-----------|-----------|-----------|
| Private key | 2560 | 4032 | 4896 |
| Public key | 1312 | 1952 | 2592 |
| Signature | 2420 | 3309 | 4627 |

These are considerably larger than the 32-to-64-byte keys and 64-byte signatures of Ed25519, which is the central practical cost of post-quantum migration. The private key can optionally be stored as just the 32-byte seed $$\xi$$ and regenerated on demand, trading computation for storage. The verification length checks are part of the security argument: an implementation must reject any $$pk$$ or $$\sigma$$ whose length differs from the value mandated for the parameter set, because skipping that check can interfere with strong unforgeability.

## Hedged and Deterministic Signing

The mask $$\mathbf{y}$$ must never repeat across two signatures and must not be guessable. Reusing $$\mathbf{y}$$ for two different challenges allows recovery of $$\mathbf{s}_1$$ by subtracting the two responses, the same structural failure that nonce reuse causes in ECDSA. ML-DSA derives the randomness for $$\mathbf{y}$$ from the per-signature seed $$\rho''$$, which mixes the signing key $$K$$, the message representative $$\mu$$, and a value $$rnd$$.

Two variants differ only in how $$rnd$$ is chosen. In the default **hedged** variant, $$rnd$$ is 32 fresh random bytes from a random bit generator. In the optional **deterministic** variant, $$rnd$$ is the all-zero string, so signing becomes a pure function of the key and message. The hedged variant is preferred: the fresh randomness helps mitigate side-channel and fault attacks, while the dependence on $$\mu$$ and $$K$$ means that even a weak or failing random source does not immediately break security. The deterministic variant makes fault attacks easier to mount and should not be used where side channels are a concern. Both variants are verified by the same algorithm, so interoperability does not require implementing the deterministic path.

## Pre-Hash ML-DSA and Domain Separation

The message that actually enters the internal signing routine is not the raw message $$M$$ but a formatted message $$M'$$ that begins with a domain separator. In "pure" ML-DSA,

$$
\begin{aligned}
M' = \mathsf{IntegerToBytes}(0, 1) \,\|\, \mathsf{IntegerToBytes}(|ctx|, 1) \,\|\, ctx \,\|\, M,
\end{aligned}
$$

where the leading byte $$0$$ marks a pure signature and $$ctx$$ is an optional context string of at most 255 bytes. The context string lets an application separate signatures generated for different purposes under the same key.

**HashML-DSA** is a pre-hash variant for settings where the message is too large to stream through SHAKE256 efficiently, or where the platform can hash the message with a different approved function. Here the message is replaced by its digest, and the formatted message uses a leading byte $$1$$:

$$
\begin{aligned}
M' = \mathsf{IntegerToBytes}(1, 1) \,\|\, \mathsf{IntegerToBytes}(|ctx|, 1) \,\|\, ctx \,\|\, \mathsf{OID} \,\|\, \mathsf{PH}_M,
\end{aligned}
$$

where $$\mathsf{OID}$$ is the object identifier of the pre-hash function (for example SHA-256, SHA-512, or SHAKE128) and $$\mathsf{PH}_M$$ is the digest of $$M$$. The leading domain-separator byte guarantees that a pure ML-DSA signature can never be reinterpreted as a HashML-DSA signature or vice versa. To preserve the claimed security level, the pre-hash digest must be drawn from a function offering at least $$\lambda$$ bits of collision resistance, which means a digest of at least $$2\lambda$$ bits. FIPS 204 states that the pure version is generally preferred, with HashML-DSA reserved for the cases that need it.

## Frequently Asked Questions

**Q: What lattice problems underpin ML-DSA, and what does each one protect against?**

ML-DSA relies on two assumptions over the module ring $$R_q$$. Module-LWE (MLWE) protects the secret key: recovering $$\mathbf{s}_1, \mathbf{s}_2$$ from the public relation $$\mathbf{t} = \mathbf{A}\mathbf{s}_1 + \mathbf{s}_2$$ is an MLWE instance. A non-standard variant of Module-SIS that NIST calls SelfTargetMSIS protects against forgery: producing a valid signature without the secret would solve it. The "self-target" qualifier reflects that the challenge is bound to the message through a hash, so a forger cannot choose the target freely.

**Q: Why does the signing algorithm need a rejection sampling loop instead of producing a signature in one pass?**

The response $$\mathbf{z} = \mathbf{y} + c\mathbf{s}_1$$ is statistically biased toward the secret $$\mathbf{s}_1$$, because $$c\mathbf{s}_1$$ shifts the distribution of the mask $$\mathbf{y}$$. If the signer published every $$\mathbf{z}$$, the accumulated bias across many signatures would leak the secret. Rejection sampling discards any $$\mathbf{z}$$ whose coefficients leave the safe range $$(-(\gamma_1 - \beta), \gamma_1 - \beta)$$. Conditioned on acceptance, the published $$\mathbf{z}$$ follows a distribution independent of the secret, which is what makes the leakage vanish. The price is that signing takes a variable number of iterations (on the order of four or five on average) rather than exactly one.

**Q: What is the hint $$\mathbf{h}$$ in the signature, and why is it necessary?**

The public key stores only the high bits $$\mathbf{t}_1$$ of $$\mathbf{t}$$; the low bits $$\mathbf{t}_0$$ are dropped to shrink the key. During verification the term $$c\mathbf{t}_1 \cdot 2^d$$ is therefore only an approximation of $$c\mathbf{t}$$, and that small error can flip the high bits of the reconstructed commitment at a few coefficients. The hint $$\mathbf{h}$$ is a compact record (at most $$\omega$$ non-zero positions) of exactly where those carries occur, so the verifier can correct them with $$\mathsf{UseHint}$$ and recover the same $$\mathbf{w}_1$$ the signer hashed. Without the hint, key compression and correct verification could not coexist.

**Q: How do the three parameter sets relate to security categories, and what is the cost of choosing a higher one?**

ML-DSA-44, ML-DSA-65, and ML-DSA-87 target NIST categories 2, 3, and 5 respectively. The numerical suffix gives the dimensions of $$\mathbf{A}$$: $$(k, \ell)$$ equal to $$(4,4)$$, $$(6,5)$$, and $$(8,7)$$. Raising the category enlarges the matrix and several norms, which increases the lattice problem's hardness but also enlarges every artifact. Signatures grow from 2420 bytes at category 2 to 4627 bytes at category 5, and public keys from 1312 to 2592 bytes, with proportionally more arithmetic per operation.

**Q: Combining the construction details, why must verification recompute the message representative $$\mu$$ rather than trusting a value from the signer?**

The signature contains the commitment hash $$\tilde{c}$$ but not $$\mu$$ itself. Verification recomputes $$\mu = \mathsf{H}(\mathsf{BytesToBits}(tr) \,\|\, M', 64)$$ from the public-key hash $$tr$$ and the formatted message, then derives the challenge $$c = \mathsf{SampleInBall}(\tilde{c})$$ and reconstructs $$\mathbf{w}'_1$$ from $$\mathbf{z}$$, $$\mathbf{t}_1$$, and the hint. The acceptance test $$\tilde{c} = \mathsf{H}(\mu \,\|\, \mathsf{w1Encode}(\mathbf{w}'_1), \lambda/4)$$ only succeeds if the same message, the same key, and a consistent commitment all feed the hash. If $$\mu$$ came from the signer, an adversary could decouple the challenge from the actual message and forge. Recomputing $$\mu$$ from the verifier's own inputs is what binds the signature to that exact message under that exact key.

**Q: Why does the deterministic signing variant carry more risk than the hedged variant if both verify identically?**

Both variants derive the mask from $$\rho'' = \mathsf{H}(K \,\|\, rnd \,\|\, \mu, 64)$$ and produce signatures the same verifier accepts, so interoperability is unaffected. The difference is $$rnd$$: hedged signing uses fresh random bytes, deterministic signing uses zeros. With deterministic signing, every internal value is a fixed function of the key and message, so an attacker who can induce a hardware fault and observe the corrupted output can compare it against the known correct computation, which makes fault attacks and certain side-channel attacks easier. The fresh randomness in the hedged variant breaks that repeatability without weakening the mathematics, which is why FIPS 204 makes it the default and warns against deterministic signing on platforms exposed to physical attacks.

## Conclusion

ML-DSA recasts the Schnorr signature over module lattices. Its security reduces to MLWE for key recovery and to SelfTargetMSIS for forgery, and it achieves SUF-CMA security against quantum adversaries. The signing algorithm follows the Fiat-Shamir with Aborts pattern: it samples a mask, forms a commitment, derives a challenge by hashing, computes a response, and uses rejection sampling to strip the secret-dependent bias before release, retrying until an attempt passes. Key compression and the verifier's hint keep the public key small while preserving exact verification. The three parameter sets trade size for security category, and the choice between hedged and deterministic signing, together with the pure and pre-hash message formats, lets implementers match the scheme to their platform and threat model. The main practical cost relative to elliptic-curve signatures is size: kilobyte-scale keys and signatures in place of the tens of bytes used today.

![ML-DSA FIPS 204 mindmap]({{site.url_complet}}/assets/article/cryptographie/lattice/2026-06-29-ml-dsa-fips-204-post-quantum-signatures.png)

## References

- [FIPS 204 — Module-Lattice-Based Digital Signature Standard](https://doi.org/10.6028/NIST.FIPS.204)
- [FIPS 203 — Module-Lattice-Based Key-Encapsulation Mechanism Standard](https://doi.org/10.6028/NIST.FIPS.203)
- [FIPS 205 — Stateless Hash-Based Digital Signature Standard](https://doi.org/10.6028/NIST.FIPS.205)
- [FIPS 202 — SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions](https://doi.org/10.6028/NIST.FIPS.202)
- [CRYSTALS-Dilithium — Algorithm Specifications and Supporting Documentation](https://pq-crystals.org/dilithium/)
- [NIST Post-Quantum Cryptography Standardization](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Claude Code](https://claude.com/product/claude-code)
</content>
</invoke>
