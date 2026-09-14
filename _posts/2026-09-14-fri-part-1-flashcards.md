---
layout: post
title: "FRI Part 1 in Twelve Cards — The Definitions to Memorise From the Lecture"
date:   2026-09-14
lang: en
locale: en-GB
categories: cryptography ZKP
tags: zkp snark stark fri reed-solomon iop flashcards glossary key-terms
description: "Twelve flashcards for the FRI toolbox: Reed-Solomon codes, rate, the Johnson bound, IOPs of proximity, quotienting, DEEP, proximity gaps and folding."
image: /assets/article/cryptographie/zero-knowledge-proof/fri/2026-09-14-fri-part-1-flashcards-mindmap.png
isMath: true
---

The first half of the [ZK Whiteboard Sessions lecture on FRI by Dan Boneh](https://www.youtube.com/watch?v=MBDBrEr2XQg) builds a toolbox before it builds the protocol: coding theory, interactive oracle proofs, a trick for turning evaluation claims into proximity claims, and two lemmas about random linear combinations. This deck is for someone who has watched that half, or read its [companion article]({{site.url_complet}}/2026/09/11/fri-proximity-proofs-part-1-codes-iop-quotienting-folding/), and wants to fix it in memory.

Twelve cards, one thing to remember each, and a table at the end to revise from. The cards define; they do not derive. The full vocabulary, thirty terms in three levels, is in [FRI and Proximity Proofs — The Vocabulary, From Beginner to Advanced]({{site.url_complet}}/2026/09/11/fri-proximity-proofs-glossary/); the protocol itself, which the lecture builds in its second half, has its own deck in [FRI in Twelve Cards — The Definitions to Memorise]({{site.url_complet}}/2026/09/14/fri-flashcards/).

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The twelve cards

### Reed-Solomon code

The code whose codewords are the values of a polynomial of degree less than $$d$$ at every point of a fixed domain $$L$$ of size $$n$$. Two distinct codewords agree in fewer than $$d$$ positions.

**Remember:** polynomial → evaluations; different polynomials rarely agree

### Rate

The ratio $$\rho = d/n$$ of message length to codeword length for a [Reed-Solomon code](#reed-solomon-code). Every decoding radius that follows is a function of $$\rho$$ alone.

**Remember:** $$\rho = d/n$$; every bound is a function of it

### Delta-far

A word is $$\delta$$-far from a code if every codeword differs from it in more than a $$\delta$$ fraction of positions, and $$\delta$$-close if some codeword is within that fraction.

**Remember:** far = wrong in more than a $$\delta$$ fraction

### Unique decoding distance

The radius $$\mu/2$$, about $$(1-\rho)/2$$ for Reed-Solomon, within which a word has at most one codeword; two would contradict the minimum distance by the triangle inequality.

**Remember:** below $$(1-\rho)/2$$, exactly one candidate

### Johnson bound

The radius $$1 - \sqrt\rho$$ below which the number of Reed-Solomon codewords within $$\delta$$ of any word is provably bounded. Between it and $$1 - \rho$$ the list size for structured domains is unknown.

**Remember:** $$1 - \sqrt\rho$$; few candidates; the proofs stop here

### Interactive oracle proof (IOP)

A proof system in which the prover sends strings, the verifier answers with random challenges, and the verifier's decision algorithm reads only a few cells of the strings (oracle access) rather than the strings themselves.

**Remember:** strings sent, dice rolled, a few cells read

### IOP of proximity (IOPP)

An [IOP](#interactive-oracle-proof-iop) whose instance includes a committed word and whose soundness is required only against words $$\delta$$-far from the relation: codewords are always accepted, [$$\delta$$-far](#delta-far) words rejected with overwhelming probability, and nothing is promised in between.

**Remember:** accept codewords, reject the far, promise nothing between

### BCS compiler

The transformation of an IOP into a hash-based SNARK: strings become Merkle roots, cell reads become Merkle authentication paths, and challenges become hashes of the transcript (Fiat-Shamir). Proof size is driven by the number of cell reads.

**Remember:** Merkle roots + Fiat-Shamir turn an IOP into a SNARK

### Quotienting

Turning the claim "$$f(a) = b$$" about a committed word $$u$$ into a proximity claim about a derived word. If the claim is true the quotient is a codeword of degree one less; if it is false for every polynomial near $$u$$, the quotient is $$\delta$$-far.

$$
\begin{aligned}
q(x) = \frac{u(x) - b}{x - a}
\end{aligned}
$$

**Remember:** $$(u - b)/(x - a)$$: evaluation claim → proximity claim

### DEEP

An out-of-domain sample: before any evaluation query the verifier picks a random $$r$$ outside $$L$$, the prover answers $$s = f(r)$$, and every later quotient includes $$(r, s)$$. Below the Johnson bound this binds the prover to one polynomial in the list.

**Remember:** one random $$(r, s)$$ outside the domain pins one polynomial

### Proximity gap theorem

For $$\delta$$ below the [Johnson bound](#johnson-bound), a random linear combination $$\sum_j r^j u_j$$ is $$\delta$$-close to the code either for a negligible fraction of $$r$$ or for all of them, and in the second case every $$u_j$$ agrees with a codeword on one common set of positions.

**Remember:** a far word cannot hide in a random blend

### Folding

Splitting a word on $$L$$ into even and odd parts and recombining them with a random $$r$$ on the halved domain $$L^2$$, so the degree bound and the domain both halve while the rate and, below the Johnson bound, the distance to the code are preserved.

$$
\begin{aligned}
u_{\mathrm{fold}}(x^2) = \frac{u(x) + u(-x)}{2} + r\,\frac{u(x) - u(-x)}{2x}
\end{aligned}
$$

**Remember:** even + $$r$$ · odd; half the degree, distance kept

## Flashcard table

| # | Term | One thing to remember |
|:---:|------|------------------------|
| 1 | Reed-Solomon code | polynomial → evaluations; different polynomials rarely agree |
| 2 | Rate | $$\rho = d/n$$; every bound is a function of it |
| 3 | Delta-far | far = wrong in more than a $$\delta$$ fraction |
| 4 | Unique decoding distance | below $$(1-\rho)/2$$, exactly one candidate |
| 5 | Johnson bound | $$1 - \sqrt\rho$$; few candidates; the proofs stop here |
| 6 | Interactive oracle proof (IOP) | strings sent, dice rolled, a few cells read |
| 7 | IOP of proximity (IOPP) | accept codewords, reject the far, promise nothing between |
| 8 | BCS compiler | Merkle roots + Fiat-Shamir turn an IOP into a SNARK |
| 9 | Quotienting | $$(u - b)/(x - a)$$: evaluation claim → proximity claim |
| 10 | DEEP | one random $$(r, s)$$ outside the domain pins one polynomial |
| 11 | Proximity gap theorem | a far word cannot hide in a random blend |
| 12 | Folding | even + $$r$$ · odd; half the degree, distance kept |

## Conclusion

Three cards carry the deck. The [Johnson bound](#johnson-bound) is the line every other guarantee is stated below; [quotienting](#quotienting) is how a proximity test becomes an evaluation proof; and [folding](#folding) is the operation FRI repeats. The rest of the cards are what those three need in order to be stated: a code, a rate, a notion of far, an oracle model, and the theorem that says random blends preserve distance.

The next step is the second half of the lecture, where the folding card becomes a protocol. Its deck, [FRI in Twelve Cards]({{site.url_complet}}/2026/09/14/fri-flashcards/), picks up where this one ends.

![Mindmap of the FRI Part 1 flashcards grouped into codes and radii, oracle proofs, evaluation proofs and distance-preserving maps]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/fri/2026-09-14-fri-part-1-flashcards-mindmap.png)

## Frequently Asked Questions

**Q: Which card explains why the verifier only checks "close" and not "equal"?**

[IOP of proximity](#iop-of-proximity-iopp), together with [Delta-far](#delta-far). A verifier reading a few cells cannot see a single wrong position, so the only promise it can keep is to reject words that are wrong in more than a $$\delta$$ fraction of positions. Everything closer than that is left unpromised.

**Q: What is the difference between the [unique decoding distance](#unique-decoding-distance) and the [Johnson bound](#johnson-bound)?**

Below the unique decoding distance a word has at most one nearby codeword. Below the Johnson bound it may have several, but provably few. The second radius is larger, about $$1/2$$ against $$3/8$$ at rate $$1/4$$, and a bounded list is enough for every argument in the deck, so the Johnson bound is the working limit.

**Q: What does the Remember line of [quotienting](#quotienting) leave out?**

Two things. The evaluation point $$a$$ must lie outside the domain, or the division is by zero and the quotient has to be defined through exact polynomial division instead. And the "false" direction is conditional: the quotient is far only when the claim is wrong for *every* polynomial near $$u$$, which is exactly why [DEEP](#deep) is needed when the list has more than one member.

**Q: Put [Reed-Solomon code](#reed-solomon-code), [DEEP](#deep), [BCS compiler](#bcs-compiler) and [quotienting](#quotienting) in the order the compiled protocol uses them.**

Reed-Solomon code first: the prover encodes its polynomial as a codeword. DEEP second: the out-of-domain sample is taken before any evaluation query. Quotienting third: each evaluation query becomes a proximity test on a quotient that includes the DEEP point. BCS compiler last: the whole interactive oracle proof is turned into a hash-based proof.

**Q: Which card is wrong if the field is small?**

None becomes false, but two need their fallback. [DEEP](#deep) bounds the bad event by $$|\mathrm{List}|^2 \cdot d / (|\mathbb F| - |L|)$$, and the [proximity gap theorem](#proximity-gap-theorem) has an error term with the field size in the denominator. In a small field both are handled by sampling several values of $$r$$ instead of one.

**Q: Why does [folding](#folding) not change the [rate](#rate)?**

The degree bound halves because the even and odd parts each hold half the coefficients, and the domain halves because squaring on a set of roots of unity is two-to-one. Both terms of $$\rho = d/n$$ halve, so the ratio is unchanged, and a $$\delta$$ chosen below the Johnson bound stays below it after every fold.

## References

- [ZK Whiteboard Sessions — S2M7: FRI and Proximity Proofs (Part 1), with Dan Boneh](https://www.youtube.com/watch?v=MBDBrEr2XQg), the lecture this deck compresses
- Eli Ben-Sasson, Iddo Bentov, Yinon Horesh, Michael Riabzev, [*Fast Reed-Solomon Interactive Oracle Proofs of Proximity*](https://eccc.weizmann.ac.il/report/2017/134/), 2017
- Eli Ben-Sasson, Alessandro Chiesa, Nicholas Spooner, [*Interactive Oracle Proofs*](https://eprint.iacr.org/2016/116), 2016
- Eli Ben-Sasson, Lior Goldberg, Swastik Kopparty, Shubhangi Saraf, [*DEEP-FRI: Sampling Outside the Box Improves Soundness*](https://eprint.iacr.org/2019/336), 2019
- Eli Ben-Sasson, Dan Carmon, Yuval Ishai, Swastik Kopparty, Shubhangi Saraf, [*Proximity Gaps for Reed-Solomon Codes*](https://eprint.iacr.org/2020/654), 2020

### Related articles

- [FRI and Proximity Proofs, Part 1 — Reed-Solomon Codes, IOPs of Proximity, Quotienting and Folding]({{site.url_complet}}/2026/09/11/fri-proximity-proofs-part-1-codes-iop-quotienting-folding/)
- [FRI and Proximity Proofs — The Vocabulary, From Beginner to Advanced]({{site.url_complet}}/2026/09/11/fri-proximity-proofs-glossary/)
- [FRI in Twelve Cards — The Definitions to Memorise]({{site.url_complet}}/2026/09/14/fri-flashcards/)
- [FRI Explained Like I'm Ten — How to Check a Million Numbers by Peeking at Twenty]({{site.url_complet}}/2026/09/14/fri-proximity-proofs-eli10/)
