---
layout: post
title: "FRI in Twelve Cards — The Definitions to Memorise"
date:   2026-09-14
lang: en
locale: en-GB
categories: cryptography ZKP
tags: zkp snark stark fri reed-solomon iop folding flashcards glossary key-terms
description: "Twelve flashcards for the FRI protocol: low-degree polynomials, Reed-Solomon codes, proximity, Merkle commitments, folding, the commit and query phases."
image: /assets/article/cryptographie/zero-knowledge-proof/fri/2026-09-14-fri-flashcards-mindmap.png
isMath: true
---

FRI, the Fast Reed-Solomon Interactive Oracle Proof of Proximity, is the low-degree test underneath STARKs and most hash-based SNARKs. It was introduced by Ben-Sasson, Bentov, Horesh and Riabzev in [a 2017 paper](https://eccc.weizmann.ac.il/report/2017/134/), and it is the subject of a two-part [ZK Whiteboard Sessions lecture by Dan Boneh](https://www.youtube.com/watch?v=MBDBrEr2XQg). This deck is for someone who has met the protocol once and wants a mental map that survives a week.

Twelve cards, each with a plain-words definition, a precise one, and one thing to remember, plus a revision table at the end. The cards define the pieces and the two phases of the protocol; they do not derive its soundness. The lecture's first half, which builds the coding-theory and oracle-proof toolbox, has its own deck in [The FRI Toolbox in Twelve Cards]({{site.url_complet}}/2026/09/14/fri-toolbox-flashcards/), and the full thirty-term vocabulary is in [FRI and Proximity Proofs — The Vocabulary, From Beginner to Advanced]({{site.url_complet}}/2026/09/11/fri-proximity-proofs-glossary/).

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The twelve cards

### Low-degree polynomial

**In plain words:** a short formula whose list of answers is much longer than the formula itself.

**Precisely:** A polynomial whose degree bound $$d$$ is small compared with the size $$n$$ of the domain it is evaluated on, so that its evaluation table is much longer than its coefficient list. FRI is a test for this property.

**Remember:** few coefficients, many evaluations

### Reed-Solomon code

**In plain words:** write down a short formula's answers at many points; that long list is the codeword.

**Precisely:** The code whose codewords are the values of a [low-degree polynomial](#low-degree-polynomial) at every point of a fixed domain $$L$$. Two distinct codewords agree in fewer than $$d$$ positions, so different polynomials produce very different tables.

**Remember:** polynomial → evaluations; different polynomials rarely agree

### Rate

**In plain words:** how much shorter the formula is than its list; it sets how many errors the test can tolerate.

**Precisely:** The ratio $$\rho = d/n$$ of degree bound to domain size. The unique decoding distance is about $$(1-\rho)/2$$ and the Johnson bound is $$1 - \sqrt\rho$$; FRI's proximity parameter is chosen below the latter.

**Remember:** $$\rho = d/n$$; work below $$1 - \sqrt\rho$$

### Proximity

**In plain words:** being close means only a small share of the list is wrong.

**Precisely:** A word is $$\delta$$-close to the [Reed-Solomon code](#reed-solomon-code) if some codeword differs from it in at most a $$\delta$$ fraction of positions, and $$\delta$$-far otherwise. FRI tests closeness, not equality.

**Remember:** close to a polynomial, not necessarily equal to one

### Merkle commitment

**In plain words:** one fingerprint stands for the whole list, and a short receipt proves any single entry belongs to it.

**Precisely:** A hash tree over an evaluation table whose root commits the prover to every entry, and whose authentication path opens one entry without revealing the rest. It is how the verifier gets oracle access to a table it never receives.

**Remember:** root = the whole table; path = one entry

### IOP of proximity

**In plain words:** a game where the verifier reads a few sealed entries and rejects lists that have many errors.

**Precisely:** An interactive protocol in which the prover commits to words, the verifier sends random challenges and reads a few entries, and soundness is required only against words that are [$$\delta$$-far](#proximity): codewords always pass, far words almost never do.

**Remember:** accept codewords, reject the far, read few entries

### Random challenge

**In plain words:** a random number the verifier picks only after the prover has sealed the list.

**Precisely:** A field element $$r$$ the verifier sends after the prover has committed, used as the coefficient of the next fold. Chosen in advance, it would let the prover craft a far word that folds into a close one.

**Remember:** $$r$$ after the commitment, never before

### Folding

**In plain words:** blend each entry with its mirror entry to get a list half as long from a formula half as big.

**Precisely:** Combining the values of a word at $$x$$ and $$-x$$ into one value at $$x^2$$, weighted by the [random challenge](#random-challenge), so the degree bound and the domain both halve. A far word folds to a far word with high probability.

$$
\begin{aligned}
f_{i+1}(x^2) = \frac{f_i(x) + f_i(-x)}{2} + r_i\,\frac{f_i(x) - f_i(-x)}{2x}
\end{aligned}
$$

**Remember:** combine $$f(x)$$ and $$f(-x)$$; halve the degree

### Commit phase

**In plain words:** seal the list, get a random number, fold, seal again, until the list is tiny.

**Precisely:** The first half of FRI. The prover commits to $$f_0$$, receives $$r_0$$, computes and commits to the [fold](#folding) $$f_1$$, and repeats, each layer on a domain half the size, until the word is small enough to send in the clear.

**Remember:** commit → challenge → fold, repeat until tiny

### Final polynomial

**In plain words:** the last tiny formula is sent openly instead of sealed.

**Precisely:** The last layer of the [commit phase](#commit-phase), sent as explicit coefficients rather than as a commitment. Its degree bound is $$d / 2^k$$ after $$k$$ folds, often a constant, and the verifier checks it directly.

**Remember:** the last layer is sent in the clear

### Query phase

**In plain words:** pick a random spot and check it in every sealed layer, then repeat with new spots.

**Precisely:** The second half of FRI. The verifier picks a random position $$s$$ and, for every layer, opens $$f_i(s)$$ and $$f_i(-s)$$ to check that $$f_{i+1}(s^2)$$ is their fold, down to the [final polynomial](#final-polynomial); repeated for several positions.

**Remember:** one position, checked through every layer, repeated

### FRI

**In plain words:** shrink the sealed list by folding, then spot-check the shrinking steps at random spots.

**Precisely:** Fast Reed-Solomon Interactive Oracle Proof of Proximity: an [IOP of proximity](#iop-of-proximity) proving a committed word is close to a low-degree polynomial by folding it down in a commit phase, then checking random positions across all layers in a query phase.

**Remember:** fold it down, then spot-check every layer

## Flashcard table

| # | Term | In plain words | One thing to remember |
|:---:|------|----------------|------------------------|
| 1 | Low-degree polynomial | a short formula whose list of answers is much longer than the formula itself | few coefficients, many evaluations |
| 2 | Reed-Solomon code | write down a short formula's answers at many points; that long list is the codeword | polynomial → evaluations; different polynomials rarely agree |
| 3 | Rate | how much shorter the formula is than its list; it sets how many errors the test can tolerate | $$\rho = d/n$$; work below $$1 - \sqrt\rho$$ |
| 4 | Proximity | being close means only a small share of the list is wrong | close to a polynomial, not necessarily equal to one |
| 5 | Merkle commitment | one fingerprint stands for the whole list, and a short receipt proves any single entry belongs to it | root = the whole table; path = one entry |
| 6 | IOP of proximity | a game where the verifier reads a few sealed entries and rejects lists that have many errors | accept codewords, reject the far, read few entries |
| 7 | Random challenge | a random number the verifier picks only after the prover has sealed the list | $$r$$ after the commitment, never before |
| 8 | Folding | blend each entry with its mirror entry to get a list half as long from a formula half as big | combine $$f(x)$$ and $$f(-x)$$; halve the degree |
| 9 | Commit phase | seal the list, get a random number, fold, seal again, until the list is tiny | commit → challenge → fold, repeat until tiny |
| 10 | Final polynomial | the last tiny formula is sent openly instead of sealed | the last layer is sent in the clear |
| 11 | Query phase | pick a random spot and check it in every sealed layer, then repeat with new spots | one position, checked through every layer, repeated |
| 12 | FRI | shrink the sealed list by folding, then spot-check the shrinking steps at random spots | fold it down, then spot-check every layer |

## Conclusion

Three cards carry the deck. [Folding](#folding) is the operation; the [commit phase](#commit-phase) and the [query phase](#query-phase) are the two halves of the protocol that apply it and check it. The two phases are separate cards on purpose: queries are not made once per round but once per sampled position, across every layer, and the distinction is what makes the proof-size and soundness arguments in the papers readable.

The cards before folding are the vocabulary the protocol is stated in. A reader who wants the reasons behind them, in particular why the fold preserves distance and why the proximity parameter stops at the Johnson bound, should go to the Part 1 deck and then to the technical article.

![Mindmap of the FRI flashcards grouped into objects, the proximity property, commitments and challenges, and the protocol phases]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/fri/2026-09-14-fri-flashcards-mindmap.png)

## Frequently Asked Questions

**Q: What is the difference between the [commit phase](#commit-phase) and the [query phase](#query-phase)?**

The commit phase builds the layers: commit, receive a challenge, fold, commit again, until the [final polynomial](#final-polynomial) is small enough to send. The query phase checks them: the verifier picks a position and opens it in every layer at once, confirming each layer is the correct fold of the one before. Queries happen after all commitments exist, not inside each round.

**Q: Which card explains why a fixed fold coefficient would be unsafe?**

[Random challenge](#random-challenge). If the prover knew $$r$$ before committing, it could choose a word that is far from every low-degree polynomial but whose fold with that particular $$r$$ is close to one. Choosing $$r$$ after the commitment removes that freedom.

**Q: What does the Remember line of [FRI](#fri) leave out?**

The guarantee is probabilistic and conditional. A far word passes one query with probability roughly $$1 - \delta$$, so the query phase is repeated until the failure probability is negligible, and the whole analysis assumes $$\delta$$ is below the Johnson bound from the [rate](#rate) card and the field is large enough for the challenges.

**Q: Put [Merkle commitment](#merkle-commitment), [folding](#folding), [final polynomial](#final-polynomial) and [query phase](#query-phase) in protocol order.**

Merkle commitment to the first word; folding, then another Merkle commitment, repeated; the final polynomial sent in the clear; then the query phase opening positions through all committed layers down to that final polynomial.

**Q: Which card is wrong if the domain is not a set of roots of unity?**

[Folding](#folding). The fold needs every point $$x$$ to have its partner $$-x$$ in the domain and squaring to map the domain onto one of half the size. Both hold for a group of roots of unity of power-of-two order and fail for an arbitrary set of points, which is why FRI requires such a domain and, through it, a field whose size minus one is divisible by the domain size.

**Q: Why does the proof get shorter when the [query phase](#query-phase) uses fewer positions, and what does that cost?**

Each position opens two entries per layer, each with a Merkle authentication path, so positions multiply directly into proof size. Fewer positions mean a higher chance that a far word passes every check, since each position catches it only with probability about $$\delta$$. The number of positions is set by the security level wanted and the chosen $$\delta$$.

## References

- Eli Ben-Sasson, Iddo Bentov, Yinon Horesh, Michael Riabzev, [*Fast Reed-Solomon Interactive Oracle Proofs of Proximity*](https://eccc.weizmann.ac.il/report/2017/134/), 2017, the FRI paper
- [ZK Whiteboard Sessions — S2M7: FRI and Proximity Proofs (Part 1), with Dan Boneh](https://www.youtube.com/watch?v=MBDBrEr2XQg)
- Eli Ben-Sasson, Alessandro Chiesa, Nicholas Spooner, [*Interactive Oracle Proofs*](https://eprint.iacr.org/2016/116), 2016
- Eli Ben-Sasson, Dan Carmon, Yuval Ishai, Swastik Kopparty, Shubhangi Saraf, [*Proximity Gaps for Reed-Solomon Codes*](https://eprint.iacr.org/2020/654), 2020, why folding preserves distance up to the Johnson bound

### Related articles

- [The FRI Toolbox in Twelve Cards — The Definitions to Memorise]({{site.url_complet}}/2026/09/14/fri-toolbox-flashcards/)
- [FRI and Proximity Proofs — The Vocabulary, From Beginner to Advanced]({{site.url_complet}}/2026/09/11/fri-proximity-proofs-glossary/)
- [FRI and Proximity Proofs, Part 1 — Reed-Solomon Codes, IOPs of Proximity, Quotienting and Folding]({{site.url_complet}}/2026/09/11/fri-proximity-proofs-part-1-codes-iop-quotienting-folding/)
- [FRI Explained Like I'm Ten — How to Check a Million Numbers by Peeking at Twenty]({{site.url_complet}}/2026/09/14/fri-proximity-proofs-eli10/)
