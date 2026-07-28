---
layout: post
title: "Halo — How to Check an Endless Chain of Work with a Single Glance"
date:   2026-06-19
lang: en
locale: en-GB
categories: cryptography ZKP eli10
tags: zkp recursive-proofs halo analogy
description: An intuitive guide to Halo, the first system that lets you verify a million steps of computation by checking just one small proof, without trusting any secret setup ceremony.
image: /assets/article/cryptographie/zero-knowledge-proof/halo/2026-06-19-halo-recursive-proofs-eli10.png
isMath: true
---

Imagine a relay race with a million runners. Each runner takes a baton from the runner before and carries it one step further. At the end, a referee wants to confirm that every single handoff was done properly. Watching a million handoffs would take forever. Is there a smarter way?

Halo, created by Sean Bowe, Jack Grigg, and Daira Hopwood in 2019, answers this question for computers. It is the first system that lets you check an arbitrarily long chain of computations by looking at one small proof, without relying on any secret ceremony or any special mathematical structure that could be compromised.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why Is Checking Someone Else's Long Work So Hard?

Suppose you hire a company to process one million transactions for your bank. They come back and say: "all done, the final balance is $42$." Do you trust them?

You could check every transaction yourself. That takes as long as the original work, so you might as well have done it yourself. What you actually want is a short certificate you can check in seconds, one that proves every transaction was handled correctly.

This is the **verification problem**. A small, lazy checker (called a *verifier*) wants to confirm that a large, powerful worker (called a *prover*) did all their work correctly.

Zero-knowledge proofs already solve part of this. The prover produces a mathematical certificate, called a *proof*, that the verifier can check quickly. But what happens when the work never stops? What if new transactions keep arriving every day, and the chain grows forever?

That is the problem Halo solves.

## What Does a Chain of Stamps Have to Do with Proofs?

A regular proof says one thing: "I did this job and got this result."

A **recursive proof** says two things at once: "I did the next step correctly, AND the proof from the previous step was genuine."

Think of a chain of stamps on a parcel. Each stamp says "this parcel passed through my office, and the stamp before mine is authentic." When the parcel arrives, you inspect only the last stamp. If it is real, it vouches for the whole journey, all the way back to the first office.

![The chain of stamps, each one vouching for the one before it]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/halo/halo-eli10-stamp-chain.png)

Here is the property that makes this useful. Every stamp is the same small size, no matter how long the chain is. The stamp at step one million is no bigger than the stamp at step one.

## How Do You Lock a Value in a Box?

Before we can build a chain of stamps, we need a way for the prover to lock a value away and later prove things about it, without ever opening the box.

### The sealed envelope

Imagine you write a secret number on a slip of paper, seal it in an envelope, and hand the envelope to a friend. Later you want to prove your number is bigger than 10, without showing the slip. If your friend is confident the envelope cannot be swapped or forged, they can accept your proof.

In Halo, that envelope is called a **polynomial commitment**. The prover takes a whole formula (a long one, with thousands of terms) and locks it into one small value, a bit like a fingerprint of the formula. Afterwards they can prove facts about the formula without revealing it.

Here is the part that matters most. The lock needs no trusted third party to build it. The lock's settings come from public random numbers that anybody can regenerate by hashing a public string. Nothing secret was ever involved, so there is nothing for anyone to have kept.

### The library game

Once the formula is locked away, the prover has to prove statements like "when you plug in 7, the answer is 42." They do this with an **inner product argument**, which is a back-and-forth game played in rounds.

It works like finding a book in a library by halving the search over and over:

- **Round 1.** "Is the book in the left half or the right half?" Left half.
- **Round 2.** "Is it in the left-left quarter or the left-right quarter?" Left-right.
- **Round 3.** "Is it in the first or the second eighth?" Second eighth.

Each round cuts the problem in half. For a library of a million books, about twenty rounds is enough to point at a single book, and both sides then confirm it is the right one.

Twenty short messages instead of a million. There is only one catch, and it is a big one.

## Why Is the Last Step So Slow?

After all the halving rounds, the verifier has to do one final check. She must confirm that a particular value, built up during the folding, really was assembled from the public starting values in the correct way.

Picture it as weighing. After the library game, the verifier has to re-weigh every book on the path she took, to be sure the answer is consistent. For a library of a million books, that means putting a million books on the scale. It costs as much as reading the whole library.

This one slow check is the bottleneck. Everything else in the game is fast; this step alone is not.

Halo's central idea is to never do this slow check inside the chain.

## How Do You Avoid Paying the Bill Every Time?

Here is Halo's most important trick, told as a story about IOUs.

### The restaurant

A group of friends eats out together every day for a year. At each dinner, one of them says "I will pay for today and settle yesterday's debt too." If they really did pay every time, the total cost would be exactly the same as everyone paying separately every day. Nothing is saved.

Halo does something different. **Nobody pays until the very last dinner.** At each dinner the current friend writes a new note instead of paying. The note says "I owe for today, and I confirm yesterday's note was genuine." At the end of the year, the last friend reads the single accumulated note and pays the whole bill once.

The trick works because carrying a note costs nothing, and merging today's note into yesterday's note produces one note, not two.

In Halo, the "bill" is the slow weighing check. The note is a small piece of data called the **deferred state**: one locked value plus a few numbers that summarise everything still owed.

![Passing the IOU forward, and paying only once at the end]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/halo/halo-eli10-iou-passing.png)

The checking machinery at each step never touches the slow weighing. It handles only the fast part and updates the note. That is what keeps each step small enough to fit inside the next one, which is the whole point.

In real numbers, Halo's checking machinery needs fewer than $$2^{17}$$ multiplication steps, which is about 130,000. Small enough that each step can comfortably check the one before it, so the chain can keep growing.

## Why Do You Need Two Kinds of Money?

There is one more obstacle. Every step in the chain does arithmetic in a particular number system. The awkward part is that the arithmetic needed to *check* a proof uses a different number system from the arithmetic used *inside* that proof. Translating between the two is painfully slow.

### The currency analogy

Imagine two neighbouring countries, Tweedleland and Deedleland. Normally, crossing the border means changing money, which costs time and fees.

Halo finds a special pair of currencies where Tweedleland money is directly accepted in Deedleland, and Deedleland money is directly accepted in Tweedleland. No exchange booth needed. When you are in one country and need to think in the other country's numbers, you simply use them.

The two curves Halo uses are named **Tweedledum** and **Tweedledee**, and they work exactly like that pair of currencies. Each curve's number system is the other curve's working arithmetic. Steps take turns between the two:

- Step 1 uses Tweedledum, so its checking runs in Tweedledee's numbers.
- Step 2 uses Tweedledee, so its checking runs in Tweedledum's numbers.
- Step 3 goes back to Tweedledum, and so on.

At every step the arithmetic is native, and no translation is ever needed. The two curves were designed as a matching pair, like a lock and its key.

Older systems needed special "pairing-friendly" currencies, which only existed in very large and slow denominations. Tweedledum and Tweedledee are ordinary 255-bit curves, which are much faster to work with.

## Putting the Whole Relay Race Together

Here is the full race, with every piece in place.

1. **Lock the work away.** The prover seals their work in polynomial commitments (the sealed envelopes).
2. **Play the fast game.** The prover and verifier run the library game, halving the problem each round. About twenty messages, even for a million items.
3. **Write an IOU instead of paying.** Rather than weighing all the books now, the prover writes the note and passes it forward.
4. **Switch currency.** The next step moves to the partner curve, so all its arithmetic stays native.
5. **Settle up once.** After all the steps, the final verifier reads the accumulated note and pays the bill a single time. That cost does not grow with the length of the chain.

The final proof is about **3.5 kilobytes**, smaller than a typical email attachment. Checking it needs one slow computation that a single proof would have required anyway.

For comparison, Fractal, a competing system published around the same time, produced proofs of over 120 kilobytes. Halo's proofs are more than thirty times smaller.

## Conclusion

Halo takes the one expensive step in proof checking and refuses to pay for it more than once. The slow weighing check is not made faster. Instead it is written down as a small note, carried forward from step to step, merged with each new note along the way, and settled a single time by whoever looks at the end of the chain. Because the note never grows, the chain can be as long as you like.

Two other choices make that possible. The locks are built from public random numbers, so there is no secret ceremony anyone has to be trusted to have forgotten. And the two curves are picked as a matching pair, so no step ever has to translate between number systems.

One honest limitation is worth stating. Halo's security rests on a mathematical problem that ordinary computers cannot solve but a large quantum computer could. Systems built on hash functions instead do resist quantum computers, though their proofs are currently much larger. Which trade you prefer depends on what you are protecting and for how long.

![Halo explained in plain words, summary mindmap]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/halo/2026-06-19-halo-recursive-proofs-eli10.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Prover** | The powerful worker who does the big computation and then has to convince somebody it was done correctly. |
| **Verifier** | The small, lazy checker who wants certainty without redoing the work. The referee in the relay race. |
| **Proof** | A short certificate that convinces the verifier the work was done right, without showing all the work. |
| **Recursive proof** | A proof that says two things at once: "my own step is correct" and "the proof before mine was genuine." The stamp in the chain of stamps. |
| **Polynomial commitment** | The sealed envelope: a way to lock a whole formula into one small value and later prove facts about it without opening it. |
| **Inner product argument** | The library game: a back-and-forth that halves the problem each round, so a million items need only about twenty messages. |
| **The slow check** | The final weighing step, which costs as much as reading the whole library and is the one expensive part of the game. |
| **Deferred state** | The IOU: a small, fixed-size note recording the slow check that has not been paid yet, passed from one step to the next. |
| **Nested amortisation** | Halo's main idea: keep the slow check out of every step, merge the notes as you go, and settle the bill once at the end. |
| **Curve cycle** | The pair of matching currencies (Tweedledum and Tweedledee) that accept each other's money, so no step ever pays an exchange fee. |

## Frequently Asked Questions

**Q: But why does the proof stay the same size even when the chain grows to a million steps?**

Because each proof only ever describes two things: the new work done in this one step, and the small note carried forward from before. The note has a fixed number of values in it and never grows, however many times it gets merged. So the proof at step one million looks exactly like the proof at step one. The length of the chain lives in what the proof *claims*, not in how big the proof *is*.

**Q: What if someone slips a fake IOU into the middle of the chain?**

The library game at that step catches it. If a step tried to pass along a bad note, the checking for that step would fail, and it would fail with overwhelming probability: the chance of slipping one through is roughly 1 in $$10^{38}$$. That is about as likely as guessing which single grain of sand somebody picked from every beach on Earth, a hundred million times over. Once any step fails, the whole chain is rejected.

**Q: Why can you not simply make the slow check cheaper?**

Nobody knows how. That check is what ties the whole folding game back to the public starting values, and for a single proof there is no known way to do it faster than looking at every item once. Halo does not make it cheaper. It makes you do it only once, at the very end, no matter how many steps the chain has. The cost of checking a million steps ends up the same as the cost of checking one.

**Q: What does "no trusted setup" mean and why should anyone care?**

Many older proof systems begin with a setup ceremony. A group of people generate secret numbers, use them to build the public settings, and then destroy the secrets. If even one person quietly kept their secret number, they could later manufacture fake proofs that look perfectly valid, and nobody would be able to tell. Halo's public settings come from hashing public data, so anyone can regenerate them and confirm no secret was ever involved. There is no ceremony, nobody to trust, and nothing that needed destroying.

**Q: What goes wrong if the two curves are not a matching pair?**

Every step would have to translate between number systems. That translation is not impossible, but it turns each single arithmetic operation into hundreds or thousands of them. The checking machinery would blow far past the 130,000-step budget, and once it is bigger than a step can hold, a step can no longer check the one before it. The chain simply stops working. The matching pair is what keeps every operation native and the budget intact.

**Q: Is this used in real software today?**

Yes. Halo came out of the Electric Coin Company, the team behind the Zcash cryptocurrency, and its ideas fed directly into Zcash's later upgrades. The Tweedledum and Tweedledee curves, and the idea of deferring a check and merging the notes, now appear in several proof libraries. Newer systems such as Nova and ProtoStar refined the same idea and both cite Halo as their direct predecessor.

**Q: Could a powerful quantum computer break Halo?**

Yes, and this is worth being honest about. Halo's security rests on a problem called the discrete logarithm problem, which ordinary computers cannot solve for large numbers. A sufficiently large quantum computer running an algorithm published by Peter Shor in 1994 could solve it, which would let an attacker forge Halo proofs. This limitation is shared with most cryptography used in blockchains today. Alternatives that resist quantum computers do exist, built from hash functions or from lattices, but they currently produce larger proofs or take longer to generate.

## References

- Bowe, S., Grigg, J., Hopwood, D.: [*Recursive Proof Composition without a Trusted Setup*](https://eprint.iacr.org/2019/1021). IACR ePrint 2019/1021. (The Halo paper itself.)
- Bünz, B., Bootle, J., Boneh, D., Poelstra, A., Wuille, P., Maxwell, G.: [*Bulletproofs: Short Proofs for Confidential Transactions and More*](https://eprint.iacr.org/2017/1066). IEEE S&P 2018. (Where the library game comes from.)
- Kothapalli, A., Setty, S., Tzialla, I.: [*Nova: Recursive Zero-Knowledge Arguments from Folding Schemes*](https://eprint.iacr.org/2021/370). CRYPTO 2022. (A successor that keeps the same idea with a cheaper per-step trick.)
- Thaler, J.: [*Proofs, Arguments, and Zero-Knowledge*](https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.html). Lecture notes, 2022.
