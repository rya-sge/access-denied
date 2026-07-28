---
layout: post
title: "The GKR Protocol — Delegating Computation with Interactive Proofs"
date:   2026-06-19
lang: en
locale: en-GB
categories: cryptography ZKP
tags: zkp interactive-proof gkr sum-check multilinear-extension arithmetic-circuit
description: A technical introduction to the GKR protocol by Goldwasser, Kalai and Rothblum. Covers layered arithmetic circuits, the sum-check protocol, multilinear extensions, and the recursive reduction used to build efficient interactive proofs.
image: /assets/article/cryptographie/zero-knowledge-proof/gkr/2026-06-19-gkr-protocol.png
isMath: true
---

The GKR protocol is an interactive proof system that allows a computationally weak verifier to delegate the evaluation of an arithmetic circuit to an untrusted prover, receiving a convincing argument of correctness without re-executing the computation. Originally introduced by Goldwasser, Kalai, and Rothblum in 2008, the protocol now serves as a core ingredient in modern proof systems, including zkSNARKs and STARKs.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Background — Interactive Proofs and Delegating Computation

### Interactive Proofs

An **interactive proof system** for a language $$L$$ is a pair $$(P, V)$$ consisting of a prover and a verifier satisfying two properties:

- **Completeness**: If $$x \in L$$, the honest prover $$P$$ convinces $$V$$ with probability 1.
- **Soundness**: If $$x \notin L$$, no (possibly malicious) prover $$P^*$$ convinces $$V$$ with probability greater than a soundness error $$\varepsilon_s$$.

The verifier runs in polynomial time in $$\lvert x \rvert$$, while the prover may be computationally unbounded. The class **IP** captures all languages admissible by such systems. A celebrated result by Shamir (1992) establishes that $$\text{IP} = \text{PSPACE}$$, showing that interactive proofs are substantially more powerful than classical certificates.

### The Delegation Problem

Consider a verifier with limited computational resources (for example a mobile device, or a smart contract with strict gas limits) that wishes to evaluate a large arithmetic circuit $$C$$ on an input $$x$$. A naive approach requires the verifier to re-execute $$C$$, which is prohibitive when $$\lvert C \rvert$$ is large. The GKR protocol solves this: the verifier can delegate the computation to an untrusted prover and verify the claimed output in time sublinear in $$\lvert C \rvert$$.

## The Sum-Check Protocol

The sum-check protocol, introduced by Lund, Fortnow, Karloff, and Nisan (1992), is the core subroutine of GKR. It allows a verifier to check a claimed sum of a multivariate polynomial over the boolean hypercube.

### Setup

Let $$\mathbb{F}$$ be a finite field and $$g: \mathbb{F}^v \to \mathbb{F}$$ a $$v$$-variate polynomial. The prover claims:

$$
\begin{aligned}
H = \sum_{b_1 \in \{0,1\}} \sum_{b_2 \in \{0,1\}} \cdots \sum_{b_v \in \{0,1\}} g(b_1, \ldots, b_v)
\end{aligned}
$$

The verifier knows $$H$$ and has oracle access to $$g$$ (it can query the polynomial at a single point), but cannot afford to evaluate the entire sum over all $$2^v$$ inputs.

### Protocol

The protocol proceeds in $$v$$ rounds. In round $$j$$:

1. The prover sends a univariate polynomial $$g_j(X_j)$$, claiming:

$$
\begin{aligned}
g_j(X_j) = \sum_{(x_{j+1}, \ldots, x_v) \in \{0,1\}^{v-j}} g(r_1, \ldots, r_{j-1}, X_j, x_{j+1}, \ldots, x_v)
\end{aligned}
$$

where $$r_1, \ldots, r_{j-1}$$ are the challenges sent in prior rounds.

2. The verifier checks that $$\deg(g_j) \leq \deg_j(g)$$ and that the consistency condition $$g_{j-1}(r_{j-1}) = g_j(0) + g_j(1)$$ holds (with $$g_0(r_0) := H$$).

3. The verifier samples a fresh challenge $$r_j \xleftarrow{\$} \mathbb{F}$$ and sends it to the prover.

After round $$v$$, the verifier issues a single oracle query to check $$g_v(r_v) = g(r_1, \ldots, r_v)$$.

![Sum-check protocol round structure between prover and verifier]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/gkr/gkr-sumcheck-rounds-sequence.png)

The ordering of the two messages inside each round carries the whole security argument. The prover commits to $$g_j$$ before seeing $$r_j$$, so it cannot tailor a round polynomial to a challenge it has not yet observed.

### Complexity and Soundness Guarantees

| Property | Value |
|----------|-------|
| Number of rounds | $$v$$ |
| Total communication | $$O\!\left(\sum_{j=1}^{v} \deg_j(g)\right)$$ field elements |
| Verifier time | $$O(v \cdot d + \text{oracle query cost})$$ |
| Prover time | $$O(2^v)$$ field operations |
| Soundness error | $$\leq \frac{v \cdot d}{\lvert\mathbb{F}\rvert}$$ where $$d = \max_j \deg_j(g)$$ |

The soundness guarantee follows from the Schwartz-Zippel lemma: if the claimed sum $$H$$ is incorrect, then the polynomial $$g_1$$ sent by the prover must differ from the honest $$g_1$$ as a polynomial, and any two distinct polynomials of degree $$d$$ agree on at most $$d$$ points out of $$\lvert\mathbb{F}\rvert$$. This error propagates additively across $$v$$ rounds, yielding the bound $$v \cdot d / \lvert\mathbb{F}\rvert$$.

## Multilinear Extensions

### Definition

Given a function $$f: \{0,1\}^v \to \mathbb{F}$$, its **multilinear extension** (MLE) is the unique multilinear polynomial $$\tilde f: \mathbb{F}^v \to \mathbb{F}$$ satisfying $$\tilde f(x) = f(x)$$ for all $$x \in \{0,1\}^v$$. It is given by:

$$
\begin{aligned}
\tilde f(x_1, \ldots, x_v) = \sum_{(h_1, \ldots, h_v) \in \{0,1\}^v} f(h_1, \ldots, h_v) \cdot \prod_{i=1}^{v} \chi_{h_i}(x_i)
\end{aligned}
$$

where $$\chi_{h_i}(x_i) = h_i \cdot x_i + (1 - h_i)(1 - x_i)$$ is the Lagrange basis polynomial for the $$i$$-th variable (equal to 1 when $$x_i = h_i$$, and 0 when $$x_i = 1 - h_i$$).

### Why MLEs Enable Efficient Verification

The Schwartz-Zippel lemma implies that two distinct multilinear polynomials over $$\mathbb{F}^v$$ agree on at most a $$v / \lvert\mathbb{F}\rvert$$ fraction of inputs. Consequently, evaluating $$\tilde f$$ at a single random point $$r \in \mathbb{F}^v$$ identifies $$f$$ (as a function on the boolean hypercube) with high probability. This principle allows the verifier to check a claim about an entire table of $$2^v$$ values using a single field evaluation.

## The GKR Protocol

### Circuit Model

The GKR protocol operates on **layered arithmetic circuits** over a field $$\mathbb{F}$$. Such a circuit $$C$$ consists of $$D+1$$ layers (numbered 0 through $$D$$), where:

- **Layer 0** is the output layer (a single gate, or a small number of output gates).
- **Layer $$D$$** is the input layer, containing the circuit's inputs.
- Every gate in layer $$i$$ receives its inputs from gates in layer $$i+1$$ only.

![Layered arithmetic circuit with addition and multiplication gates]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/gkr/gkr-layered-circuit.png)

Computation flows from layer $$D$$ down to layer $$0$$. Verification in GKR runs in the **opposite direction**: the protocol starts with a claim about layer 0 and reduces it, layer by layer, toward the inputs.

Each gate in layer $$i$$ is labelled by a binary string $$p \in \{0,1\}^m$$, where $$2^m$$ bounds the number of gates per layer. The total circuit size is $$S = D \cdot 2^m$$.

### Gate Value Polynomials

For each layer $$i$$, define:

- $$V_i: \{0,1\}^m \to \mathbb{F}$$, where $$V_i(p)$$ is the value computed by gate $$p$$ in layer $$i$$.
- $$\tilde V_i: \mathbb{F}^m \to \mathbb{F}$$, the multilinear extension of $$V_i$$.

The wiring structure of the circuit is encoded by two boolean functions, written $$A_i$$ for addition and $$M_i$$ for multiplication:

- $$A_i: \{0,1\}^{3m} \to \{0,1\}$$, where $$A_i(z, w_1, w_2) = 1$$ if and only if gate $$z$$ in layer $$i$$ is an addition gate with inputs $$w_1, w_2$$ in layer $$i+1$$.
- $$M_i: \{0,1\}^{3m} \to \{0,1\}$$, where $$M_i(z, w_1, w_2) = 1$$ if and only if gate $$z$$ in layer $$i$$ is a multiplication gate with inputs $$w_1, w_2$$ in layer $$i+1$$.

Their multilinear extensions $$\tilde A_i$$ and $$\tilde M_i$$ are called **wiring predicates**. Most of the literature writes these with the words "add" and "mult" carrying a tilde and a layer subscript; the single-letter form is used here purely for readability.

### The Fundamental Recurrence

The key identity relating layer $$i$$ to layer $$i+1$$ is:

$$
\begin{aligned}
\tilde V_i(z) = \sum_{w_1, w_2 \in \{0,1\}^m} \Bigl[ \tilde A_i(z, w_1, w_2)\bigl(\tilde V_{i+1}(w_1) + \tilde V_{i+1}(w_2)\bigr) \\
+ \tilde M_i(z, w_1, w_2) \cdot \tilde V_{i+1}(w_1) \cdot \tilde V_{i+1}(w_2) \Bigr]
\end{aligned}
$$

This holds for all $$z \in \mathbb{F}^m$$, not just $$z \in \{0,1\}^m$$. The sum is a sum-check instance over $$2m$$ variables ($$w_1$$ and $$w_2$$, each of length $$m$$). The polynomial $$f_i$$ has degree at most 2 in each of its $$2m$$ variables: each wiring predicate is multilinear (degree 1 per variable), and the multiplication term contributes an additional degree-1 factor from $$\tilde V_{i+1}$$.

### Protocol Description

**Starting point**: The verifier holds the input $$x \in \mathbb{F}^n$$ and the claimed output $$C(x)$$. The prover claims $$\tilde V_0(z_0) = v_0$$ where $$z_0$$ is the label of the output gate and $$v_0 = C(x)$$.

![Layer-by-layer reduction from the circuit output down to the input layer]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/gkr/gkr-layer-reduction.png)

**Layer reduction** (repeated $$D$$ times, from $$i = 0$$ to $$i = D-1$$):

Given a claim that $$\tilde V_i(z_i) = v_i$$ for some $$z_i \in \mathbb{F}^m$$, the prover and verifier run the sum-check protocol on the polynomial:

$$
\begin{aligned}
f_i(w_1, w_2) = \tilde A_i(z_i, w_1, w_2)\bigl(\tilde V_{i+1}(w_1) + \tilde V_{i+1}(w_2)\bigr) + \tilde M_i(z_i, w_1, w_2) \cdot \tilde V_{i+1}(w_1) \cdot \tilde V_{i+1}(w_2)
\end{aligned}
$$

summed over $$(w_1, w_2) \in \{0,1\}^{2m}$$. After $$2m$$ rounds of sum-check, the verifier reduces to a claim about $$\tilde V_{i+1}$$ at two random points $$(u, u') \in \mathbb{F}^m \times \mathbb{F}^m$$.

**Reducing two claims to one** (the line-restriction trick): Two evaluation claims $$\tilde V_{i+1}(u) = a$$ and $$\tilde V_{i+1}(u') = a'$$ at distinct points can be reduced to a single claim. Define the line $$\ell: \mathbb{F} \to \mathbb{F}^m$$ with $$\ell(0) = u$$ and $$\ell(1) = u'$$. The restriction $$\tilde V_{i+1}(\ell(t))$$ is a univariate polynomial of degree at most $$m$$. The prover sends its coefficients, the verifier checks consistency with $$a$$ and $$a'$$, then sends a random $$t^* \in \mathbb{F}$$ and reduces to the single claim $$\tilde V_{i+1}(\ell(t^*))$$.

![Line-restriction trick collapsing two evaluation claims into one]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/gkr/gkr-line-restriction.png)

**Final layer**: At layer $$D$$, the verifier holds the inputs $$x$$ and can directly evaluate $$\tilde V_D(z_D) = \tilde x(z_D)$$ (the MLE of the input) in time $$O(n)$$. This check terminates the protocol.

### Complexity Analysis

| Property | Complexity |
|----------|-----------|
| Rounds per layer | $$O(m) = O(\log S)$$ |
| Total rounds | $$O(D \log S)$$ |
| Total communication | $$O(D \log S)$$ field elements |
| Verifier time | $$O(n + D \cdot m \cdot d)$$ where $$d$$ is the max degree per variable |
| Prover time | $$O(S \log S)$$ field operations |
| Soundness error | $$O(D \log S / \lvert\mathbb{F}\rvert)$$ |

For log-depth, log-space uniform circuits over inputs of size $$n$$ (a practically important class):

- **Verifier time**: $$n \cdot \text{polylog}(n)$$
- **Prover time**: $$\text{poly}(S)$$
- **Communication**: $$\text{polylog}(n)$$

The verifier therefore runs in nearly linear time in the input size, regardless of the circuit depth or size.

## A Concrete Example — Polynomial Evaluation Circuit

To illustrate the protocol, consider verifying that a polynomial $$p: \mathbb{F}^n \to \mathbb{F}$$ given by its evaluation table (of size $$2^n$$) evaluates to $$p(x) = v$$ for a specific input $$x$$. This is an instance of computing a multilinear extension at a point, representable as a layered circuit.

The circuit has $$n$$ layers, each halving the number of values via a linear combination controlled by the input coordinate $$x_i$$. At layer $$i$$, each gate computes:

$$
\begin{aligned}
V_i(z) = (1 - x_i) \cdot V_{i+1}(z, 0) + x_i \cdot V_{i+1}(z, 1)
\end{aligned}
$$

Each layer is a pure addition layer (no multiplication). The sum-check at each layer reduces to verifying two evaluations of the next-layer polynomial. After $$n$$ rounds, the verifier checks a single leaf of the evaluation table.

- **Total work for the prover**: $$O(2^n)$$ (linear in the table size).
- **Total work for the verifier**: $$O(n)$$ (logarithmic in the table size).

This is precisely the efficiency gain that GKR provides: the prover works proportionally to the computation, while the verifier's cost scales with the input size and circuit depth, not the circuit size.

## Zero-Knowledge Variants

The basic GKR protocol is not zero-knowledge: the messages exchanged by the prover (the univariate polynomials $$g_j$$) may reveal information about the witness (the gate values of the circuit). To obtain a zero-knowledge variant, one standard technique masks each univariate polynomial $$g_j$$ with a random polynomial of the same degree:

$$
\begin{aligned}
\hat g_j(X_j) = g_j(X_j) + r_j(X_j)
\end{aligned}
$$

where $$r_j$$ is chosen uniformly at random subject to $$r_j(0) + r_j(1) = 0$$, ensuring that the sum over the boolean hypercube is preserved. The verifier adjusts its consistency check accordingly. This technique achieves perfect zero knowledge for the sum-check sub-protocol; a detailed treatment appears in Thaler (2022), Chapter 6.

## Applications and Impact

### Connection to #P and PSPACE

The original motivation for the sum-check protocol was to show $$\#P \subseteq \text{IP}$$: counting problems (such as counting the number of satisfying assignments to a 3-SAT formula) can be verified interactively. The GKR protocol extends this to $$\text{NC}$$ circuits with efficient provers, providing the first practically-oriented interactive proof for general computation.

### zkSNARKs Based on GKR

Several modern zkSNARK constructions build on the GKR protocol or its techniques:

- **[Libra](https://eprint.iacr.org/2019/317)** (Xie et al., 2019): a zkSNARK based directly on GKR with a universal trusted setup, achieving prover time $$O(C)$$ linear in the circuit size.
- **[Spartan](https://eprint.iacr.org/2019/550)** (Setty, 2020): uses the sum-check protocol to reduce R1CS satisfiability to polynomial identity testing, without any trusted setup, yielding a transparent zkSNARK.
- **[Hyrax](https://eprint.iacr.org/2017/1132)** (Wahby et al., 2018): combines GKR with a discrete-log-based polynomial commitment to produce a full zkSNARK with no trusted setup and a sublinear verifier.

### Relation to STARKs

[ZK-STARKs](https://eprint.iacr.org/2018/046) (Ben-Sasson et al., 2018) use a different arithmetisation (AIR) and low-degree testing (FRI), but the sum-check protocol appears internally in their constraint composition step. The algebraic linking IOP (ALI) used in STARKs is conceptually related to the sum-check reduction: the verifier combines multiple polynomial constraints via random linear combination and tests the resulting polynomial for proximity to a low-degree code, echoing the sum-check reduction across layers.

## Protocol Steps at a Glance

The table below summarises the nine building blocks of the GKR protocol, the reason each one exists, and its dominant cost or trade-off.

| # | Step | Role in the protocol | Purpose | Dominant cost |
|---|------|----------------------|---------|---------------|
| 1 | **Sum-check protocol** | Reduces a claimed sum $$H = \sum_{b \in \{0,1\}^v} g(b)$$ to a single oracle query via $$v$$ interactive rounds | **Security.** Random challenges enforced after each prover message prevent the prover from back-fitting earlier answers. Soundness error $$\leq v \cdot d / \lvert\mathbb{F}\rvert$$ | Verifier: $$O(v \cdot d)$$ field checks. Prover: $$O(2^v)$$ field operations to build round polynomials |
| 2 | **Multilinear extension (MLE)** | Uniquely lifts $$f : \{0,1\}^v \to \mathbb{F}$$ to a polynomial $$\tilde f : \mathbb{F}^v \to \mathbb{F}$$ via the Lagrange basis | **Security and compression.** Uniqueness allows Schwartz-Zippel fingerprinting: a single random evaluation identifies the entire $$2^v$$-entry table. Without a unique extension the verifier could not compress a table check to one field element | Evaluation: $$O(2^v)$$ Lagrange terms for a general table; $$O(v)$$ for structured inputs |
| 3 | **Layered arithmetic circuit** | Organises computation into $$D$$ layers of fan-in-2 addition and multiplication gates | **Structural.** Layering gives the recurrence its recursive shape: the value at each gate in layer $$i$$ depends only on values in layer $$i+1$$. This locality is what makes the layer-by-layer reduction possible | No runtime cost; defines $$S = D \cdot 2^m$$ and the labelling scheme for gates |
| 4 | **Wiring predicates** | Encode the circuit topology (which gate feeds which) as multilinear polynomials | **Structural and efficiency.** Expressing wiring as polynomials lets the fundamental recurrence be written as a polynomial sum, turning each layer check into a sum-check instance the verifier can run cheaply. For structured circuits (data-parallel, FFT) these polynomials have closed-form expressions evaluable in $$O(m)$$ | Evaluation: $$O(S/D)$$ for general circuits; $$O(m)$$ for structured circuits |
| 5 | **Fundamental recurrence** | Expresses $$\tilde V_i(z)$$ as a sum over all gate pairs $$(w_1, w_2)$$ in layer $$i+1$$, combining wiring predicates and gate-value MLEs | **Correctness.** Translates the circuit's arithmetic semantics (a gate computes the sum or product of its two inputs) into a polynomial identity over $$\mathbb{F}$$. This identity is the claim that sum-check verifies at each layer | Produces a degree-2-per-variable polynomial over $$2m$$ variables, the input to each sum-check instance |
| 6 | **Layer-by-layer reduction** ($$\times D$$) | Applies sum-check to the recurrence at each layer, reducing the claim about layer $$i$$ to a claim about layer $$i+1$$ | **Efficiency.** Each reduction replaces one large computation (re-running a full layer) with $$2m$$ rounds of sum-check. The verifier's cost per layer is $$O(m \cdot d) = O(m)$$ instead of $$O(2^m)$$ | Verifier: $$O(Dm)$$ total. Communication: $$O(Dm)$$ field elements total |
| 7 | **Line-restriction trick** | After each sum-check, collapses two evaluation claims $$\tilde V_{i+1}(u) = a$$ and $$\tilde V_{i+1}(u') = a'$$ into one claim at a random point $$\ell(t^*)$$ | **Efficiency (critical).** Without this step, each layer doubles the number of open claims; after $$D$$ layers the verifier holds $$2^D$$ claims and must check $$O(S)$$ values, which is as expensive as re-running the circuit. The trick keeps the claim count at exactly 1 at all times | Prover sends $$m+1$$ coefficients. Verifier: 2 consistency checks plus 1 random evaluation |
| 8 | **Final input check** | At layer $$D$$ the verifier evaluates the MLE of the known inputs $$x$$ directly and compares it to the open claim | **Security (anchoring).** Provides an unconditional termination point: the verifier checks the remaining claim without relying on the prover. Any accumulated lie in the chain must surface here | Verifier: $$O(n)$$ field operations, the only computation the verifier does independently |
| 9 | **Zero-knowledge masking** (optional) | Adds a random polynomial $$r_j$$ satisfying $$r_j(0)+r_j(1)=0$$ to each sum-check message | **Privacy.** Hides intermediate gate values from the verifier while preserving all consistency checks (the constraint $$r_j(0)+r_j(1)=0$$ ensures the correct sum is unaffected). Soundness is unchanged because the masking is independent of the prover's cheating strategy | $$O(d)$$ extra field elements per round; negligible overhead relative to the base protocol |

## Conclusion

GKR converts the cost of verifying an arithmetic circuit from a function of the circuit size into a function of the input size and the circuit depth. Three ingredients carry that reduction: multilinear extensions, which let one field element stand in for a table of $$2^m$$ gate values; the sum-check protocol, which reduces a claimed sum to a single oracle query in $$v$$ rounds; and the line-restriction trick, which keeps the number of open claims at one as the reduction walks from the output layer to the inputs.

The protocol is an interactive proof rather than an argument of knowledge, and on its own it neither hides the witness nor commits the prover to one. Both properties are added by composition: masking polynomials for zero knowledge, and a polynomial commitment scheme for extractability. That is how the construction reaches modern proof systems. Spartan, Hyrax, and Libra each pair a sum-check-based reduction with a different commitment scheme, and the same reduction appears inside the constraint composition step of STARKs.

![GKR protocol summary mindmap]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/gkr/2026-06-19-gkr-protocol.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Interactive proof** | A protocol between a probabilistic polynomial-time verifier and an unbounded prover, satisfying completeness for true statements and soundness (bounded acceptance probability) for false ones. |
| **Soundness error** | The maximum probability that a cheating prover convinces the verifier of a false statement; in GKR it is $$O(D \log S / \lvert\mathbb{F}\rvert)$$. |
| **Sum-check protocol** | A $$v$$-round interactive reduction that turns a claimed sum of a $$v$$-variate polynomial over $$\{0,1\}^v$$ into a single evaluation of that polynomial at a random point. |
| **Multilinear extension (MLE)** | The unique polynomial of degree at most 1 in each variable that agrees with a given function on the boolean hypercube $$\{0,1\}^v$$. |
| **Schwartz-Zippel lemma** | The bound stating that a non-zero polynomial of total degree $$d$$ vanishes on at most a $$d / \lvert\mathbb{F}\rvert$$ fraction of points, which is what makes a single random evaluation a reliable fingerprint. |
| **Layered arithmetic circuit** | A circuit whose gates are partitioned into $$D+1$$ layers, where every gate in layer $$i$$ draws both inputs from layer $$i+1$$ only. |
| **Wiring predicate** | The multilinear extension of the boolean function describing which gate in layer $$i$$ is fed by which pair of gates in layer $$i+1$$, one predicate for addition gates and one for multiplication gates. |
| **Gate value polynomial** | The function $$V_i$$ mapping a gate label in layer $$i$$ to the value that gate computes, and its multilinear extension $$\tilde V_i$$. |
| **Line-restriction trick** | The step that replaces two evaluation claims about $$\tilde V_{i+1}$$ with a single claim, by restricting the polynomial to the line through the two points and evaluating at a random parameter. |
| **Delegation** | The setting in which a weak verifier outsources a computation to an untrusted prover and checks the result in time sublinear in the computation's size. |

## Annex — Security Implementation Checklist

The items below are the properties an implementation of GKR (or of a sum-check-based proof system built on it) has to satisfy for its soundness and zero-knowledge claims to hold. Each row states the requirement and what breaks when it is violated.

### Field and parameter selection

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The field $$\mathbb{F}$$ is large enough that $$D \cdot m \cdot d / \lvert\mathbb{F}\rvert$$ is negligible; at least a 128-bit field for a target of $$2^{-100}$$ soundness error. | A small field lets a cheating prover pass a round by guessing, and the error compounds over every layer. |
| ☐ | The round polynomial degree bound $$\deg_j(g)$$ is checked against the declared circuit, not taken from the prover's message. | A prover sending a higher-degree polynomial can satisfy the consistency checks while encoding a false sum. |
| ☐ | The number of variables and layers used by the verifier is fixed by the circuit description, not negotiated per proof. | A prover that shortens the reduction skips layers and never has its intermediate values anchored. |

### Challenge generation

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every challenge $$r_j$$ and $$t^*$$ is sampled uniformly from $$\mathbb{F}$$ by a CSPRNG, after the corresponding prover message has been received. | A predictable or early-released challenge lets the prover back-fit a polynomial that passes exactly at the checkpoint and lies elsewhere. |
| ☐ | Under Fiat-Shamir, the transcript hashed to derive each challenge includes the circuit description, the input, the claimed output, and every prior prover message. | An incomplete transcript permits grinding: the prover replays messages under a challenge it has chosen to its advantage. |
| ☐ | Challenge derivation uses a hash modelled as a random oracle with output at least twice the target security level in bits. | A short hash output makes challenge collisions findable, which reintroduces the adaptive-prover attack Fiat-Shamir is meant to prevent. |

### Verification logic

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The consistency check $$g_j(0) + g_j(1) = g_{j-1}(r_{j-1})$$ is enforced in every round, with $$g_0(r_0) := H$$ for the first. | Skipping any round breaks the chain that ties the final oracle query back to the claimed sum. |
| ☐ | The line-restriction step verifies $$q(0) = a$$ and $$q(1) = a'$$ before the random $$t^*$$ is drawn, and rejects if $$\deg q > m$$. | An unchecked line polynomial lets the prover substitute an unrelated claim and discard the two real ones. |
| ☐ | The final input check evaluates the MLE of $$x$$ independently, using the verifier's own copy of the input. | Accepting a prover-supplied input evaluation removes the only unconditional anchor in the protocol. |
| ☐ | The wiring predicates are evaluated from the public circuit description held by the verifier, never from prover-supplied values. | A prover that supplies its own wiring proves a different circuit than the one the verifier intended to delegate. |
| ☐ | Any failed check aborts the protocol; no partial acceptance path exists. | Continuing after a failed round lets an inconsistency be absorbed by later rounds. |

### Zero-knowledge variant

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Each masking polynomial $$r_j$$ is drawn uniformly from the set satisfying $$r_j(0) + r_j(1) = 0$$, using fresh randomness per proof. | Reused or biased masks leak the underlying round polynomial, and with it the intermediate gate values. |
| ☐ | The masked messages $$\hat g_j$$ replace $$g_j$$ everywhere in the transcript, including in the Fiat-Shamir hash. | A transcript mixing masked and unmasked values reveals the mask by subtraction. |
| ☐ | Zero knowledge is not assumed from GKR alone when the final oracle query touches a private input; a commitment scheme supplies the missing hiding property. | The last query can expose a witness value that every earlier round was careful to hide. |

## Frequently Asked Questions

**Q: Why must the verifier's challenges be random? Could not the verifier use a fixed, deterministic sequence?**

No. A deterministic challenge sequence can be predicted by the prover before sending any message. The prover could then craft a polynomial that passes every fixed checkpoint while lying elsewhere. The Schwartz-Zippel bound requires that each challenge be chosen after the prover commits, so the prover cannot adapt its responses retroactively. This is the commit-then-challenge structure that underlies all sum-check-based proofs.

**Q: What happens if the line-restriction trick is omitted?**

Without the trick, each sum-check at layer $$i$$ ends with two evaluation claims on $$\tilde V_{i+1}$$. Carrying both claims independently through $$D$$ layers doubles the number of open claims at each layer, ending with $$2^D$$ claims at the input layer. The verifier would then need $$O(S)$$ time to check all of them, eliminating the sub-linear complexity advantage. The line-restriction trick collapses two claims into one at the cost of one additional degree-$$m$$ polynomial, keeping the claim count at exactly 1 throughout.

**Q: Why must the MLE be multilinear (degree at most 1 in each variable) rather than a higher-degree extension?**

Uniqueness. A function $$f: \{0,1\}^v \to \mathbb{F}$$ has exactly $$2^v$$ free values, which is matched precisely by the $$2^v$$ monomials of a multilinear polynomial. Higher-degree extensions are not unique: infinitely many degree-2 polynomials can agree with $$f$$ on $$\{0,1\}^v$$. The Schwartz-Zippel argument requires a unique canonical representative of $$f$$, so that any two parties computing the MLE of the same table obtain the same polynomial and therefore agree at any random evaluation point.

**Q: Can GKR handle circuits with fan-in greater than 2 (gates with more than two inputs)?**

Yes, with mild modifications. A gate with $$k$$ inputs induces a sum-check instance over $$km$$ variables instead of $$2m$$. The communication and verifier work per layer scale as $$O(km)$$, which remains logarithmic in the circuit size. In practice most implementations fix fan-in to 2 for simplicity, but the protocol generalises cleanly.

**Q: Does the zero-knowledge masking affect soundness?**

No. Each masking polynomial $$r_j$$ satisfies $$r_j(0) + r_j(1) = 0$$ by construction, so the sum of the masked polynomial over $$\{0,1\}$$ equals the sum of the original. The verifier's consistency check $$\hat g_j(0) + \hat g_j(1) = \hat g_{j-1}(r_{j-1})$$ still enforces the correct relationship. Soundness is unchanged because a cheating prover would still need to find a masking polynomial that simultaneously makes a false sum pass every round, and Schwartz-Zippel rules this out.

**Q: What is the cost of evaluating the wiring predicate MLEs?**

For a general circuit, computing a single evaluation of $$\tilde A_i$$ or $$\tilde M_i$$ requires time proportional to the number of non-zero entries in the wiring table, which can be $$O(S/D)$$ per layer and $$O(S)$$ overall. For structured circuits (data-parallel computation, FFT, matrix multiplication), the wiring predicates factor into low-complexity closed-form expressions, reducing evaluation to $$O(m) = O(\log S)$$ per layer. This structural property is the reason GKR achieves a linear-time prover for specific computation families.

**Q: Is the basic GKR protocol a proof of knowledge?**

No. GKR is an interactive proof for the decision problem "does circuit $$C$$ evaluate to $$v$$ on input $$x$$?". It is sound (a false claim fails with high probability) but does not provide knowledge extraction: there is no efficient extractor that recovers the circuit's intermediate gate values from a successful prover. To obtain proof-of-knowledge guarantees, one must combine GKR with an extractable polynomial commitment scheme, as done in Libra.

**Q: What is a typical soundness error in a realistic deployment?**

Each sum-check over $$2m$$ rounds with degree-2 polynomials contributes error at most $$4m / \lvert\mathbb{F}\rvert$$. Over $$D$$ layers the total error is $$O(D \cdot m / \lvert\mathbb{F}\rvert)$$. For a circuit with $$n = 2^{20}$$ inputs, depth $$D = 40$$, and $$m = 20$$ (since $$2^m$$ bounds gates per layer), over a 128-bit prime field the total error is roughly $$40 \cdot 20 \cdot 2 / 2^{128} \approx 2^{-118}$$. This is negligible for all practical purposes.

**Q: How do the sum-check bound and the line-restriction step combine to give the protocol's overall soundness?**

They compose additively. Each of the $$D$$ layer reductions contributes two independent chances for a cheating prover to survive: the $$2m$$ sum-check rounds, bounded by $$2m \cdot d / \lvert\mathbb{F}\rvert$$ with $$d = 2$$, and the line-restriction step, where a dishonest degree-$$m$$ polynomial $$q$$ agreeing with the true restriction at the random $$t^*$$ costs a further $$m / \lvert\mathbb{F}\rvert$$. Summing over all layers gives $$O(D \cdot m / \lvert\mathbb{F}\rvert)$$. The point worth noting is that the line-restriction trick, introduced purely as an efficiency measure, adds a term of the same order as the sum-check itself and so does not change the security level.

## References

### Foundational papers

- Goldwasser, S., Kalai, Y. T., Rothblum, G. N.: [*Delegating Computation: Interactive Proofs for Muggles*](https://dl.acm.org/doi/10.1145/2699436). STOC 2008. Journal version in JACM 2015.
- Lund, C., Fortnow, L., Karloff, H., Nisan, N.: *Algebraic Methods for Interactive Proof Systems*. JACM 1992. (Introduces the sum-check protocol.)
- Shamir, A.: *IP = PSPACE*. JACM 1992.

### Proof systems building on GKR

- Xie, T., Zhang, J., Zhang, Y., Papamanthou, C., Song, D.: [*Libra: Succinct Zero-Knowledge Proofs with Optimal Prover Computation*](https://eprint.iacr.org/2019/317). CRYPTO 2019.
- Setty, S.: [*Spartan: Efficient and general-purpose zkSNARKs without trusted setup*](https://eprint.iacr.org/2019/550). CRYPTO 2020.
- Wahby, R. S., Tzialla, I., Shelat, A., Thaler, J., Walfish, M.: [*Doubly-efficient zkSNARKs without trusted setup*](https://eprint.iacr.org/2017/1132). IEEE S&P 2018. (The Hyrax system.)
- Ben-Sasson, E., Bentov, I., Horesh, Y., Riabzev, M.: [*Scalable, transparent, and post-quantum secure computational integrity*](https://eprint.iacr.org/2018/046). IACR ePrint 2018.

### Implementation and systems work

- Wahby, R. S., Ji, Y., Blumberg, A. J., Shelat, A., Thaler, J., Walfish, M., Wies, T.: *Full accounting for verifier complexity*. IEEE S&P 2016.
- Wahby, R. S., Setty, S., Ren, Z., Blumberg, A. J., Walfish, M.: *Efficient RAM and control flow in verifiable outsourced computation*. NDSS 2015.

### Lecture notes

- Thaler, J.: [*Proofs, Arguments, and Zero-Knowledge*](https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.html). Lecture notes, 2022. (Chapters 4 and 5 cover sum-check and GKR in depth.)
