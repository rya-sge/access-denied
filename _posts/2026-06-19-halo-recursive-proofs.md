---
layout: post
title: "Halo — Recursive Proof Composition without a Trusted Setup"
date:   2026-06-19
last_modified_at: 2026-07-28
lang: en
locale: en-GB
categories: cryptography ZKP
tags: zkp recursive-proofs halo inner-product-argument polynomial-commitment elliptic-curves ivc
description: A technical introduction to Halo by Bowe, Grigg and Hopwood. Covers incrementally verifiable computation, amortized polynomial commitments, nested amortization, the Sonic-based main argument, and the Tweedledum/Tweedledee curve cycle.
image: /assets/article/cryptographie/zero-knowledge-proof/halo/2026-06-19-halo-recursive-proofs.png
isMath: true
---

Recursive proof composition (building proofs that attest to the correctness of earlier instances of themselves) is the mechanism behind incrementally verifiable computation (IVC): verifying an arbitrarily long computation with a single constant-size proof. All prior practical realisations required either a trusted setup or cycles of expensive pairing-friendly elliptic curves operating over 780-bit fields. Halo, introduced by Bowe, Grigg, and Hopwood in 2019, achieves recursive proof composition without a trusted setup and without pairing-friendly curves, relying solely on the discrete logarithm assumption over 255-bit prime-order curves. Fully recursive proofs are 3.5 KiB in size.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Background

### Incrementally Verifiable Computation

Incrementally verifiable computation (IVC) formalises the ability to verify a multi-step computation without re-executing it. If $$F$$ is a transition function and the computation applies $$F$$ for $$T$$ steps starting at $$x_0$$, then after step $$i$$ the prover holds a proof $$\pi_i$$ attesting that:

$$
\begin{aligned}
F^{(i)}(x_0) = x_i \quad \text{and} \quad \pi_{i-1} \text{ verified correctly}
\end{aligned}
$$

The size of $$\pi_i$$ is independent of $$i$$. This is realised via **recursive proof composition**: each step's proof statement includes verification of the previous proof. The motivating application is blockchain scalability, where a new participant can verify the current state of the network by checking only the latest proof, without downloading the full transaction history.

### Why Prior Art Required Pairing-Friendly Curves

A zkSNARK proof constructed with an elliptic curve $$E$$ over base field $$\mathbb F_p$$ encodes statements about arithmetic over the scalar field $$\mathbb F_q$$ (where $$q = \#E$$). The verification circuit for this proof must therefore perform arithmetic over $$\mathbb F_q$$. If the next recursive step's proof also uses $$E$$, the outer circuit must simulate $$\mathbb F_p$$ arithmetic inside an $$\mathbb F_q$$ circuit, which is prohibitively expensive.

The standard workaround is to find a 2-cycle $$(E_p, E_q)$$ such that $$\#E_p = q$$ and $$\#E_q = p$$, so that steps alternate between curves and keep all arithmetic native. Only one family of pairing-friendly curves (MNT curves) is known to support such cycles, but secure instantiations require 780-bit fields, yielding large proof sizes and slow operations. Additionally, all pairing-based SNARKs require a trusted setup ceremony.

Halo circumvents both constraints: it constructs a 2-cycle of ordinary 255-bit prime-order curves, and its polynomial commitment scheme needs no trapdoor.

## Polynomial Commitment Scheme

### Construction

The commitment scheme is a Pedersen vector commitment to a polynomial's coefficient vector. Given a degree bound $$d - 1$$, the public reference string $$\sigma = (\mathbb{G}, \mathbb F_p, \mathbf{G}, H)$$ contains $$d$$ random group generators $$\mathbf{G} \in \mathbb{G}^d$$ and a blinding generator $$H \in \mathbb{G}$$, produced by hashing public data (no trusted setup). For $$p(X) = \sum_{i=0}^{d-1} a_i X^i$$ with coefficient vector $$\mathbf{a}$$:

$$
\begin{aligned}
\text{Commit}(\sigma, p(X);\ r) = \langle \mathbf{a}, \mathbf{G} \rangle + [r]H
\end{aligned}
$$

The commitment is **perfectly hiding** (the blinding factor $$r$$ conceals $$\mathbf{a}$$ information-theoretically) and **additively homomorphic**, since $$[a]\text{Commit}(p) + [b]\text{Commit}(q) = \text{Commit}(ap + bq)$$.

### Modified Inner Product Argument

To prove that a committed polynomial $$p$$ evaluates to $$v$$ at a public point $$x$$, the prover and verifier run a modified inner product argument derived from Bulletproofs. The verifier first sends a random group element $$U \in \mathbb{G}$$ and both parties compute $$P' = P + [v]U$$. The argument then proves knowledge of $$\mathbf{a}$$ such that:

$$
\begin{aligned}
P' = \langle \mathbf{a}, \mathbf{G} \rangle + [r]H + [v']U, \quad v' = \langle \mathbf{a},\ (1, x, x^2, \ldots, x^{d-1}) \rangle
\end{aligned}
$$

For $$d = 2^k$$, the protocol proceeds in $$k$$ rounds. Write $$\mathbf a_{\text{lo}}$$ and $$\mathbf a_{\text{hi}}$$ for the lower and upper halves of the current coefficient vector, and likewise for the generator vector. In round $$j$$ (counting from $$k$$ down to 1), the prover sends two cross-terms:

$$
\begin{aligned}
L_j &= \langle \mathbf a_{\text{lo}}, \mathbf G_{\text{hi}} \rangle + [l_j]H + [\langle \mathbf a_{\text{lo}}, \mathbf b_{\text{hi}} \rangle]U \\
R_j &= \langle \mathbf a_{\text{hi}}, \mathbf G_{\text{lo}} \rangle + [r_j]H + [\langle \mathbf a_{\text{hi}}, \mathbf b_{\text{lo}} \rangle]U
\end{aligned}
$$

The verifier responds with a challenge $$u_j$$; both parties fold their vectors:

$$
\begin{aligned}
\mathbf a \leftarrow \mathbf a_{\text{hi}} \cdot u_j^{-1} + \mathbf a_{\text{lo}} \cdot u_j, \qquad
\mathbf G \leftarrow \mathbf G_{\text{lo}} \cdot u_j^{-1} + \mathbf G_{\text{hi}} \cdot u_j
\end{aligned}
$$

After $$k$$ rounds both vectors have collapsed to a single element each, and the prover sends the surviving scalar $$a$$ together with a blinding factor. Communication is $$2k$$ group elements and 2 scalars, for $$O(\log d)$$ total.

### The Linear-Time Bottleneck

At the end of the argument, the verifier must confirm that the folded generator $$G$$ was computed correctly from the original generators:

$$
\begin{aligned}
G = \langle \mathbf{s}, \mathbf{G} \rangle
\end{aligned}
$$

where $$\mathbf{s}$$ is a length-$$d$$ vector with a binary counting structure derived from the challenges $$(u_1, \ldots, u_k)$$:

$$
\begin{aligned}
\mathbf{s} = (u_1^{-1} u_2^{-1} \cdots u_k^{-1},\;
             u_1   u_2^{-1} \cdots u_k^{-1},\;
             \ldots,\;
             u_1 u_2 \cdots u_k)
\end{aligned}
$$

Computing $$G = \langle \mathbf{s}, \mathbf{G} \rangle$$ is a multi-scalar multiplication (MSM) requiring $$O(d)$$ group operations, linear in the degree bound. This single step dominates the cost of the entire argument and is the target of the amortisation strategy.

The related scalar value $$b = \langle \mathbf{s}, \mathbf{b} \rangle = g(x, u_1, \ldots, u_k)$$ costs only $$O(\log d)$$, because the vector's structure factors into a product:

$$
\begin{aligned}
g(X, u_1, \ldots, u_k) = \prod_{i=1}^k \left(u_i + u_i^{-1} X^{2^{i-1}}\right)
\end{aligned}
$$

The asymmetry between these two computations, one linear in the group and one logarithmic in the field, is what the rest of the construction exploits.

### Amortisation Strategy

The linear-time MSM cannot be eliminated for a single proof, but its cost can be spread across $$m$$ proofs via an untrusted **helper**. Given $$m$$ proofs with challenges $$(u_1^{(i)}, \ldots, u_k^{(i)})$$ for $$i = 1, \ldots, m$$, the helper computes $$G_1, \ldots, G_m$$ and provides a polynomial commitment opening argument showing that a random linear combination of the commitments opens at a value the verifier can compute in $$O(m \log d)$$ time. The verifier trades $$m$$ separate $$O(d)$$ checks for one combined check at $$O(m \log d)$$ marginal cost. As $$m$$ grows, the amortised cost per proof approaches $$O(\log d)$$.

![Helper amortisation batching m linear MSMs into a single opening argument]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/halo/halo-helper-amortization.png)

The helper needs no trust: if it supplies an incorrect $$G_i$$, the combined opening argument fails, because the value the verifier computes from the product formula would not match.

## Nested Amortisation

### The Core Innovation

Standard recursive proof composition requires the verification circuit to be fully succinct. With the inner product argument, full verification includes the $$O(d)$$ check $$G = \langle \mathbf{s}, \mathbf{G} \rangle$$. This check is too expensive to encode inside a verification circuit of sublinear size, blocking recursion below the threshold where the circuit can verify itself.

Halo introduces **nested amortisation**: split proof verification into two parts and embed only the cheap part in the circuit.

1. **Partial verification** ($$O(\log d)$$ time): all checks except $$G = \langle \mathbf{s}, \mathbf{G} \rangle$$.
2. **Final linear check** ($$O(d)$$ time): the MSM itself, performed once by the outermost verifier.

The verification circuit at step $$i$$ takes as **public inputs** the deferred state from the previous step:

$$
\begin{aligned}
\bigl(G_\text{old},\ S_\text{old},\ y_\text{old},\ u_1^{\text{old}}, \ldots, u_k^{\text{old}}\bigr)
\end{aligned}
$$

The circuit performs partial verification of the current proof $$\pi_i$$, uses the amortisation argument to update the deferred state, and outputs the new state as a public output for the next step.

![Nested amortisation across recursive steps with a single final linear check]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/halo/halo-recursive-step-activity.png)

### Why Arbitrary Recursion Depth is Achievable

Because the circuit performs only logarithmic-time operations, its size is sublinear in $$d$$. Provided $$d$$ is chosen so that the verification circuit fits within $$d$$ multiplication gates, the recursive step is self-referential and recursion can continue to any depth. Halo reaches this threshold at fewer than $$2^{17}$$ multiplication gates.

Applying the Fiat-Shamir heuristic transforms the interactive argument into a non-interactive proof. The deferred state then becomes part of the public input to each step, carried forward as explicit values through the recursive chain. The ultimate verifier, the only entity to perform the linear-time MSM, validates the entire accumulated chain at once.

## Main Argument

Halo's circuit satisfiability argument is a variant of Sonic, adapted to the polynomial commitment scheme described above. The prover demonstrates that a circuit $$\mathcal{C}$$ is satisfied for a private witness, consisting of:

- $$N$$ **multiplication constraints**: $$a_i \cdot b_i = c_i$$ for $$i = 1, \ldots, N$$, where $$a_i$$, $$b_i$$ and $$c_i$$ are the left input, right input and output of the $$i$$-th multiplication gate
- $$Q$$ **linear constraints** encoding the wiring: $$\sum_i a_i u_{q,i} + \sum_i b_i v_{q,i} + \sum_i c_i w_{q,i} = k_q$$ for $$q = 1, \ldots, Q$$, where the coefficients $$u_{q,i}$$, $$v_{q,i}$$, $$w_{q,i}$$ and the constant $$k_q$$ are fixed by the circuit

Following Sonic, all constraints are embedded into a single polynomial identity over a formal indeterminate $$Y$$ via polynomials $$r(X, Y)$$, $$s(X, Y)$$, and $$t(X, Y)$$:

$$
\begin{aligned}
r(X, Y) &= \sum_{i=1}^{N} a_i X^i Y^N u_i(Y) + \cdots \quad \text{(encodes the witness)} \\
t(X, Y) &= r(X, 1)(r(X, Y) + s'(X, Y)) - Y^N k(Y) \quad \text{(encodes the constraints)}
\end{aligned}
$$

The constraint system is satisfied if and only if the constant term of $$t(X, Y)$$ is zero. Soundness follows from the Schwartz-Zippel lemma: a non-zero polynomial has a zero constant term with probability at most $$\deg / \lvert\mathbb{F}\rvert$$ at a random evaluation point.

The protocol proceeds in several rounds in which the prover commits to $$r(X, 1)$$, to the low and high halves of $$t(X, y)$$, and to auxiliary polynomials, before opening all commitments at verifier-chosen points. Multiple polynomial openings are collapsed into a single invocation via the additive homomorphism of the commitment scheme.

**Theorem** (Bowe, Grigg, Hopwood 2019): the protocol has perfect completeness, perfect special honest-verifier zero knowledge, and computational witness-extended emulation under the discrete log relation assumption.

## Implementation — Tweedledum and Tweedledee

### Why a Curve Cycle is Necessary

The verification circuit for a Halo proof over $$E_p$$ (scalar field $$\mathbb F_q$$) must perform arithmetic in $$\mathbb F_q$$. The circuit is itself expressed over $$\mathbb F_q$$, which is the base field of a second curve $$E_q$$. Proofs at odd recursion steps use $$E_p$$; proofs at even steps use $$E_q$$. This alternation ensures that scalar arithmetic (polynomial evaluations, challenge derivation) is always native to the current curve's base field, avoiding costly cross-field simulation.

![Tweedledum and Tweedledee 2-cycle with alternating recursion steps]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/halo/halo-curve-cycle.png)

Unlike prior work, no pairing is needed: the 2-cycle need not involve pairing-friendly curves. Ordinary short Weierstrass curves are sufficient, and such cycles are easy to construct.

### Curve Definitions

$$
\begin{aligned}
E_p/\mathbb F_p &:\ y^2 = x^3 + 5 \quad \text{of order } q \qquad \text{[Tweedledum]} \\
E_q/\mathbb F_q &:\ y^2 = x^3 + 5 \quad \text{of order } p \qquad \text{[Tweedledee]}
\end{aligned}
$$

where $$p$$ and $$q$$ are 255-bit primes:

$$
\begin{aligned}
p &= 2^{254} + 4707489545178046908921067385359695873 \\
q &= 2^{254} + 4707489544292117082687961190295928833
\end{aligned}
$$

Both curves were chosen to satisfy:

| Property | Requirement | Purpose |
|----------|-------------|---------|
| Highly 2-adic fields | Large $$2^k$$ factor in $$p-1$$ and $$q-1$$ | Efficient radix-2 FFTs for polynomial multiplication |
| $$\gcd(p-1, 5) = \gcd(q-1, 5) = 1$$ | 5 is invertible mod $$p-1$$ and $$q-1$$ | Enables the Rescue algebraic hash (S-box $$x \mapsto x^5$$) |
| Order-3 endomorphism $$\phi$$ | $$\phi((x,y)) = (\zeta_p x, y)$$ | Reduces scalar multiplication circuit size |
| Prime order | $$q = \#E_p$$, $$p = \#E_q$$ | Avoids cofactor issues and simplifies the protocol |

Security stands at **126 bits** against Pollard rho, accounting for the factor-$$\sqrt{3}$$ speed-up available from the order-3 endomorphism.

### Endomorphism-Based Scalar Multiplication

The dominant cost inside the verification circuit is multiplying a group element by a verifier challenge. The paper's Algorithm 1 exploits the endomorphism $$\phi$$ of order 3 to process each challenge bit-pair with 3.5 multiplication constraints (versus the naive 4 or more), reducing the total circuit size.

### Verification and Proof Size

The verifier maintains a logarithmic-size state between proofs. Upon receiving each proof, it performs a logarithmic-time partial verification and updates that state. At the end of a sequence, it performs one linear-time check to accept or reject all proofs simultaneously.

| Metric | Halo | Fractal (concurrent work) |
|--------|------|---------------------------|
| Proof size | **3.5 KiB** | > 120 KiB |
| Recursion threshold | < $$2^{17}$$ mult. gates | $$\approx 2^{18}$$ mult. gates |
| Trusted setup | None | None |
| Curve type | Ordinary 255-bit ($$\times 2$$) | Ordinary |
| Security level | 126 bits | Post-quantum plausible |
| Field size | 255-bit | Not applicable |

## Protocol Steps at a Glance

| # | Step | Role | Purpose | Dominant cost |
|---|------|------|---------|---------------|
| 1 | **Pedersen commitment** | Commit to the witness polynomial $$p(X)$$ | No trusted setup; perfectly hiding; additive homomorphism used for batch opening | $$O(d)$$ group operations once; the commitment is one group element |
| 2 | **Inner product argument** ($$k$$ rounds) | Prove $$p(x) = v$$ without revealing $$p$$ | Reduces a degree-$$d$$ claim to a scalar check in $$k = \log_2 d$$ rounds, with $$O(\log d)$$ communication | $$2k$$ group elements sent; $$k$$ verifier challenges |
| 3 | **Linear-time MSM** | Verify $$G = \langle \mathbf{s}, \mathbf{G} \rangle$$ | Soundness anchor: confirms that the $$k$$-round folding was consistent with the public generators | $$O(d)$$ group operations, the bottleneck |
| 4 | **Helper amortisation** | Batch $$m$$ linear MSMs into one | Reduces amortised per-proof verifier cost from $$O(d)$$ to $$O(\log d)$$; the helper is untrusted | Helper: $$O(m \cdot d)$$; verifier: one opening argument |
| 5 | **Nested amortisation** | Defer the MSM through the recursive chain | Keeps the verification circuit sublinear, enabling arbitrary-depth recursion | Deferred state added as fixed-size public inputs |
| 6 | **Sonic-based circuit argument** | Prove $$N$$ multiplication and $$Q$$ linear constraints | Encodes the full arithmetic constraint system in polynomials; Schwartz-Zippel soundness | Prover: $$O(N \log N)$$; verifier: $$O(\log d)$$ marginal |
| 7 | **Batch polynomial opening** | Collapse multiple openings into one | Additive homomorphism reduces several opening arguments to one via random linear combination | Overhead proportional to the number of openings; one final IPA invocation |
| 8 | **Fiat-Shamir** | Replace interactive challenges with hash outputs | Makes the protocol non-interactive and threads the deferred state through public inputs | Rescue hash evaluation, $$O(1)$$ per challenge |
| 9 | **Curve alternation** | Alternate Tweedledum and Tweedledee per step | Keeps scalar field arithmetic native at each step, avoiding cross-field simulation | No runtime cost; a structural constraint on proof construction |
| 10 | **Final linear check** | Ultimate verifier computes the deferred MSM | Unconditional soundness anchor, paid exactly once regardless of recursion depth | $$O(d)$$ group operations, paid once for the entire chain |

## Conclusion

Halo removes two requirements that earlier recursive proof systems treated as unavoidable: a trusted setup, and a cycle of pairing-friendly curves. The trusted setup disappears because the Pedersen commitment's reference string is generated by hashing public data, so no trapdoor exists to be retained. The pairing requirement disappears because the verification algorithm uses only group operations, which any elliptic curve provides, leaving a 2-cycle of ordinary 255-bit curves sufficient.

Nested amortisation is what carries the construction. The linear-time multi-scalar multiplication at the end of the inner product argument is not made cheaper; it is deferred, carried forward as a fixed-size public input, and merged with the next step's deferred check. Only the ultimate verifier pays it, once, for a chain of any length. That change is what brings the verification circuit below $$2^{17}$$ multiplication gates and allows a step to verify its predecessor.

The trade-off is the security assumption. Halo rests on the discrete log relation assumption over elliptic curve groups, which a large quantum computer would break, whereas the concurrent Fractal construction is post-quantum plausible at the cost of proofs above 120 KiB. Later folding-based schemes, Nova in particular, keep the deferral idea and replace the polynomial commitment machinery with a cheaper per-step folding operation.

![Halo recursive proof composition summary mindmap]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/halo/2026-06-19-halo-recursive-proofs.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Incrementally verifiable computation (IVC)** | A setting in which a $$T$$-step computation carries a proof whose size and verification cost do not grow with $$T$$. |
| **Recursive proof composition** | The technique of making each step's proof statement include the verification of the previous step's proof. |
| **Polynomial commitment** | A short binding commitment to a polynomial that supports proving evaluations at chosen points without revealing the polynomial. |
| **Pedersen vector commitment** | A commitment of the form $$\langle \mathbf{a}, \mathbf{G} \rangle + [r]H$$, perfectly hiding and additively homomorphic, whose generators are derived by hashing public data. |
| **Inner product argument** | A logarithmic-round protocol, derived from Bulletproofs, that folds a length-$$d$$ vector claim down to a single scalar over $$k = \log_2 d$$ rounds. |
| **Multi-scalar multiplication (MSM)** | The computation $$\langle \mathbf{s}, \mathbf{G} \rangle$$ over a group, costing $$O(d)$$ group operations and forming the linear-time bottleneck of the argument. |
| **Amortisation** | Spreading the cost of $$m$$ separate linear-time checks over one combined check, so that the marginal per-proof cost falls to $$O(\log d)$$. |
| **Nested amortisation** | Halo's central technique: embedding only the logarithmic part of verification in the circuit and carrying the linear part forward as a fixed-size deferred state. |
| **Deferred state** | The constant-size tuple of group elements and scalars that records an outstanding linear check, passed between recursive steps as a public input. |
| **Curve cycle** | A pair of elliptic curves $$(E_p, E_q)$$ where each curve's group order equals the other's base field characteristic, so alternating between them keeps all arithmetic native. |

## Annex — Security Implementation Checklist

The properties below are what separate a secure Halo-style implementation from an insecure one. They apply to the commitment scheme, the recursion, and the Fiat-Shamir transform that makes the whole thing non-interactive.

### Reference string and generators

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The generators $$\mathbf{G}$$ and $$H$$ are derived by hash-to-curve from a public, auditable seed, with no party ever holding a discrete log relation among them. | Anyone knowing a relation among the generators can open a commitment to two different polynomials, breaking binding entirely. |
| ☐ | The hash-to-curve procedure maps to the prime-order subgroup and rejects the identity element. | A generator equal to the identity, or lying outside the prime-order subgroup, silently voids the binding argument for that position. |
| ☐ | The degree bound $$d$$ is fixed by the reference string, and openings for polynomials of degree $$\geq d$$ are rejected. | An over-degree polynomial escapes the folding structure, so the final scalar check no longer pins down the committed coefficients. |

### Commitment and opening

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every blinding factor ($$r$$, and the per-round $$l_j$$ and $$r_j$$) is drawn fresh from a CSPRNG for each proof. | Reused or predictable blinding removes the hiding property, exposing the witness coefficients from the commitments. |
| ☐ | All group elements received from the prover are validated: on-curve, in the prime-order subgroup, and not the identity where a non-identity value is required. | Invalid-curve and small-subgroup inputs let a malicious prover satisfy the folding equations with elements that carry no commitment. |
| ☐ | The final linear check $$G = \langle \mathbf{s}, \mathbf{G} \rangle$$ is performed by the ultimate verifier and never skipped, however deep the recursion. | Skipping it discards the only unconditional anchor: the entire chain of folded claims then rests on prover-supplied values. |
| ☐ | The scalar $$b$$ is recomputed by the verifier from the product formula, never accepted from the prover. | A prover-supplied $$b$$ decouples the evaluation claim from the challenges, allowing an arbitrary opening value. |

### Fiat-Shamir and challenge derivation

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every challenge ($$U$$, each $$u_j$$, and the evaluation points) is derived from a transcript hash covering all prior messages, the statement, and the public parameters. | An incomplete transcript permits grinding: the prover re-derives a challenge that makes a false claim pass. |
| ☐ | Each challenge $$u_j$$ is non-zero and invertible in the scalar field, with the derivation retried if it is not. | A zero challenge makes $$u_j^{-1}$$ undefined, and implementations that substitute a default value create a predictable folding step. |
| ☐ | The Rescue instance used inside the circuit matches the one used outside it, byte for byte, including padding and domain separation. | A mismatch between the in-circuit and out-of-circuit hash lets a proof verify in one context and not the other, or admits a second valid transcript. |
| ☐ | The condition $$\gcd(p-1, 5) = 1$$ is verified for the field in use before instantiating the Rescue S-box. | If 5 is not coprime to $$p-1$$, the map $$x \mapsto x^5$$ is not a bijection and the permutation loses the structure its security analysis assumes. |

### Recursion and deferred state

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The deferred state is bound into the circuit's public inputs at every step, and the outer verifier checks the state it receives against the one the final proof commits to. | An unbound deferred state can be swapped for one whose linear check trivially passes, invalidating the whole chain. |
| ☐ | The deferred state has a fixed size that is enforced structurally, not merely expected. | A variable-length state breaks the constant-size proof guarantee and can hide additional unchecked claims. |
| ☐ | Steps alternate strictly between the two curves of the cycle, and the circuit rejects a proof produced on the wrong curve. | Two consecutive steps on the same curve force cross-field simulation, which implementations typically approximate, opening a soundness gap. |
| ☐ | The base case of the recursion (step 0) is verified explicitly rather than assumed valid. | An unverified base case lets a chain start from an arbitrary claimed state, so every subsequent proof attests to a fiction. |

## Frequently Asked Questions

**Q: Why does deferred amortisation not accumulate an unbounded cost as recursion deepens?**

The deferred state has fixed size regardless of the recursion depth: it is a constant number of group elements and scalars. At each step, the amortisation argument merges the new proof's deferred check with the existing deferred state into a single new state of the same size. The cost of the final linear check is $$O(d)$$ once, not $$O(T \cdot d)$$ for $$T$$ recursive steps. This is the property that makes the chain constant-cost to verify at the end.

**Q: What is the discrete log relation assumption and how does it differ from standard DLOG?**

The discrete log relation assumption (DLRA) states that for $$n \geq 2$$ random group elements $$G_1, \ldots, G_n$$, no efficient adversary can find scalars $$a_1, \ldots, a_n$$ (not all zero) such that $$\sum_i a_i G_i = \mathcal{O}$$. For $$n = 2$$ this reduces to standard DLOG, since finding $$a_1$$ with $$a_1 G_1 = G_2$$ is equivalent to a non-trivial relation $$(a_1, -1)$$. No attack is known that breaks DLRA without also breaking DLOG, and it is conjectured to hold at the same security level.

**Q: Why are pairing-friendly curves not needed for the curve cycle in Halo?**

Pairing-friendly curves were required in prior work because those SNARKs use bilinear pairings in their verification algorithm. The verification circuit must therefore compute pairings, which requires the curve to support an efficient pairing map, a strong algebraic constraint. Halo's verification algorithm uses only group operations (scalar multiplication and point addition), which any elliptic curve supports. Any 2-cycle of ordinary prime-order curves suffices, and such cycles are easy to find among 255-bit curves.

**Q: How does the verification circuit avoid encoding the linear-time MSM?**

The circuit receives $$G_\text{old}$$ (the group element that would need the MSM to verify) as a public input, not as a value it recomputes. It treats this input as correct and propagates it forward as a new public input for the next step, applying the amortisation argument to merge it with the current proof's own $$G$$. The circuit never evaluates $$\langle \mathbf{s}, \mathbf{G} \rangle$$. The only entity that ever performs this computation is the final external verifier, who sits outside all circuits.

**Q: Is Halo zero-knowledge?**

Yes. The protocol achieves perfect special honest-verifier zero knowledge. The prover's blinding factors in the Pedersen commitments are chosen uniformly at random, ensuring that the committed polynomial cannot be recovered from the commitment alone. The opening argument also includes per-round blinding factors that mask the coefficient vectors. A perfect simulator can produce transcripts indistinguishable from honest proofs without knowing the witness.

**Q: How does the Rescue hash function fit into the protocol?**

The Fiat-Shamir transform derives verifier challenges by hashing the prover's messages. Inside the verification circuit, this hash must be expressed as arithmetic constraints. SHA-256 requires thousands of constraints per call because of its bitwise operations. Rescue is an algebraic hash function designed to be efficient over prime fields: its S-box is $$x \mapsto x^5$$ (or its inverse), which requires only a constant number of multiplication constraints. The condition $$\gcd(p-1, 5) = 1$$ ensures that $$x^5$$ is a bijection on $$\mathbb F_p$$, which the hash needs in order to be a permutation. This reduces the Fiat-Shamir overhead inside the circuit by orders of magnitude compared to SHA-256.

**Q: How does Halo compare to Nova, the subsequent folding-based IVC scheme?**

Nova (Kothapalli, Setty, Tzialla 2022) avoids the polynomial commitment scheme entirely by folding relaxed R1CS instances. Nova's prover requires only 2 MSMs per step, against Halo's $$O(N \log N)$$ work, and the recursion overhead per step is roughly 10,000 R1CS constraints. Nova does not achieve zero knowledge natively (the folded witness leaks information) and is not a SNARK by itself, so a final zkSNARK must be applied to produce a succinct proof. Halo produces a zero-knowledge proof at each step but with a higher per-step prover cost. The two sit at different points in the same trade-off.

**Q: Putting the amortisation and the curve cycle together, why does Halo need both to recurse?**

They remove two independent obstacles, and either one alone leaves the circuit too expensive. Nested amortisation addresses the cost in gate count: it keeps the $$O(d)$$ multi-scalar multiplication out of the circuit, so the circuit's size grows logarithmically rather than linearly in the degree bound. The curve cycle addresses the cost per gate: without it, every field operation the circuit performs would be simulated arithmetic in a non-native field, which inflates each operation by orders of magnitude. Halo needs the circuit to fit under $$2^{17}$$ multiplication gates, and only the two techniques together bring it there.

## References

### Primary source

- Bowe, S., Grigg, J., Hopwood, D.: [*Recursive Proof Composition without a Trusted Setup*](https://eprint.iacr.org/2019/1021). IACR ePrint 2019/1021.

### Components Halo builds on

- Maller, M., Bowe, S., Kohlweiss, M., Meiklejohn, S.: [*Sonic: Zero-Knowledge SNARKs from Linear-Size Universal and Updatable Structured Reference Strings*](https://eprint.iacr.org/2019/099). CCS 2019.
- Bünz, B., Bootle, J., Boneh, D., Poelstra, A., Wuille, P., Maxwell, G.: [*Bulletproofs: Short Proofs for Confidential Transactions and More*](https://eprint.iacr.org/2017/1066). IEEE S&P 2018. (Source of the inner product argument.)
- Albrecht, M., Grassi, L., Rechberger, C., Roy, A., Tiessen, T.: *MiMC: Efficient Encryption and Cryptographic Hashing with Minimal Multiplicative Complexity*. ASIACRYPT 2016. (Background for algebraic hash functions including Rescue.)

### Prior and concurrent recursive systems

- Ben-Sasson, E., Chiesa, A., Tromer, E., Virza, M.: *Succinct Non-Interactive Zero Knowledge for a von Neumann Architecture*. USENIX Security 2014. (First practical recursive composition, Pinocchio-based, trusted setup, pairing-friendly MNT curves.)
- Chiesa, A., Ojha, D., Spooner, N.: *Fractal: Post-Quantum and Transparent Recursive Proofs from Holography*. EUROCRYPT 2020. (The concurrent work compared in the table above.)
- Chiesa, A., Hu, Y., Maller, M., Mishra, P., Vesely, N., Ward, N.: [*Marlin: Preprocessing zkSNARKs with Universal and Updatable SRS*](https://eprint.iacr.org/2019/1047). EUROCRYPT 2020. (Fractal builds on Marlin.)
- Kothapalli, A., Setty, S., Tzialla, I.: [*Nova: Recursive Zero-Knowledge Arguments from Folding Schemes*](https://eprint.iacr.org/2021/370). CRYPTO 2022.
- Groth, J.: [*On the Size of Pairing-Based Non-interactive Arguments*](https://eprint.iacr.org/2016/260). EUROCRYPT 2016.

### Lecture notes

- Thaler, J.: [*Proofs, Arguments, and Zero-Knowledge*](https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.html). Lecture notes, 2022. (Chapters on IVC and recursive composition.)
