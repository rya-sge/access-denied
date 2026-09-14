---
layout: post
title: "FRI Explained Like I'm Ten — How to Check a Million Numbers by Peeking at Twenty"
date:   2026-09-14
lang: en
locale: en-GB
categories: cryptography ZKP eli10
tags: zkp snark stark fri reed-solomon iop folding analogy
description: A plain-language guide to FRI and proximity proofs. Secret rules, smudged lists, sealed notebooks, a division trick and paper folding, with worked examples.
image: /assets/article/cryptographie/zero-knowledge-proof/fri/2026-09-14-fri-proximity-proofs-eli10-mindmap.png
isMath: true
---

Imagine your friend hands you a notebook with one million numbers in it. She says every single number comes from one short secret rule, the kind of rule you could write on a sticky note. You do not have time to check a million numbers. You barely have time to check twenty. Can twenty peeks ever be enough to trust the whole notebook?

Surprisingly, yes, if the game is set up carefully. The trick is called FRI, and it sits underneath a whole family of computer proofs that let a phone check, in a blink, work that took a data centre hours. This article explains the ideas behind it with notebooks, smudges, sealed envelopes and folded paper.

This article is based on a [video lecture on FRI by Dan Boneh](https://www.youtube.com/watch?v=MBDBrEr2XQg) and on its more technical companion piece on this site, [FRI and Proximity Proofs, Part 1 — Reed-Solomon Codes, IOPs of Proximity, Quotienting and Folding]({{site.url_complet}}/2026/09/11/fri-proximity-proofs-part-1-codes-iop-quotienting-folding/). If a word here makes you curious, that article has the grown-up version.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What is a "short rule" and why do we care?

Think of a rule like "take the spot number, multiply it by itself, then add one." At spot 1 the rule gives 2. At spot 2 it gives 5. At spot 3 it gives 10. You can keep going forever, and the rule never gets longer. A short rule can produce an enormous list.

Rules like this have a special property. Two *different* short rules almost never agree. If two rules each use at most three numbers on their sticky note, their lists can agree in at most two spots and then they must go their separate ways. So a rule with a few numbers on its note cannot "pretend" to be another rule for very long. This one fact is the engine behind everything that follows.

Why does anyone care? Because computers can turn almost any calculation into "here is a list that should follow a short rule." If you can check that cheaply, you can check the calculation cheaply. The Storyteller (the friend with the notebook) does all the hard work. The Inspector (you) just wants to be sure she did it right, without redoing it.

> **The grown-up name.** A "short rule" is a **polynomial of low degree** (a formula built from adding and multiplying the spot number, with only a few numbers on the sticky note). The Storyteller is the **prover** and the Inspector is the **verifier**. The fact that two different low-degree polynomials agree in only a few spots comes from a rule you may meet later: a polynomial with $$d$$ numbers on its note has fewer than $$d$$ spots where it equals zero.

## Why does writing things twice help?

Suppose you want to send your friend the word CAT, but the letter might get rained on. If you write CAT once and the C smudges, she reads "?AT" and cannot tell CAT from BAT or HAT. If you write it three times, CATCATCAT, one smudge is no problem. She can still see what you meant.

Writing something longer than it needs to be, on purpose, so that smudges can be spotted and fixed, is a very old idea. The long version is called a codeword. The rule that stretches short things into long things is called a code. How much longer? If a three-letter word becomes nine letters, we say the rate is one third. A smaller rate means more stretching, which means more protection but more paper.

Our secret rules do the same thing. The sticky note is the short message. The giant list of numbers, computed at thousands of spots, is the long version. And because two different rules almost never agree, two different lists produced this way disagree in nearly every spot. That is what makes smudges easy to notice: a valid list is very far from every other valid list.

```
Short message (sticky note):   [ 1 , 0 , 1 ]           3 numbers
                                    |
                                    |  apply the rule at spots 1, 2, 3, ... 12
                                    v
Long list (codeword):     [ 2, 5, 10, 17, 26, 37, 50, 65, 82, 101, 122, 145 ]   12 numbers

Rate = 3 / 12 = one quarter
```

> **The grown-up name.** Stretching a message so that errors can be caught is an **error-correcting code**. When the stretching is "evaluate a polynomial at many spots", the code is called a **Reed-Solomon code**, and it is the same code that protects the data on a CD or a QR code from scratches. The number of spots where two lists disagree, divided by the list length, is the **relative Hamming distance**. The short-over-long ratio is the **rate**, written $$\rho$$.

## Why can we only check "close enough"?

Here is the bad news. Suppose the Storyteller's notebook follows the rule perfectly in 999,999 spots and is wrong in exactly one. If you peek at twenty random spots, what is the chance you land on the one bad spot? About twenty in a million. You will almost certainly miss it.

So the Inspector cannot promise to catch *every* mistake. What she can promise is this: if the notebook is wrong in *lots* of spots, say more than a quarter of them, then twenty random peeks will almost certainly hit at least one wrong spot. A notebook that is wrong in a quarter of its spots is called "far" from the rule. One that is wrong in very few spots is "close."

That sounds like a weaker promise, and it is. But it turns out to be exactly enough. A notebook that is close to a valid one still pins down a single short rule, just like CATCATCAT with one smudge still spells CAT. The Inspector does not need the notebook to be perfect. She needs it to be close enough that only one rule could have produced it.

> **The grown-up name.** A test that only promises to reject lists that are far from every valid one is a **proximity test** (proximity means closeness). The fraction of allowed smudges is written $$\delta$$ (the Greek letter delta), and a list is called **delta-far** or **delta-close** depending on which side of that line it sits.

## How many smudges are too many?

Think of the smudge budget as a ruler. On the left, no smudges. On the right, every spot is wrong.

```
 no smudges                                                         all wrong
 |---------------|----------------|-----------------------------------|
 0            "one rule"      "a few rules"          "no idea"        1
              zone ends       zone ends
```

In the first zone, a smudged list still points to exactly one rule. It is like CATCATCAT with one letter gone: there is only one word it could be.

In the second zone, more smudges are allowed, and now a smudged list might be close to two or three different rules at once. Like "?A?" which could be CAT, BAT, CAR or CAB. But the number of candidates stays small, and small is good enough for what comes next.

In the third zone, nobody knows how many candidate rules there could be. Mathematicians have proved things about the first two zones. About the third, for the kinds of lists FRI uses, the answer is still an open puzzle. So FRI stays inside the second zone, where the proofs are known.

Why not just stay in the first zone, where life is simplest? Because the further right you go, the fewer peeks the Inspector needs, and fewer peeks means a smaller proof. The second zone is the best trade that has been proven safe.

> **The grown-up name.** The end of the first zone is the **unique decoding distance**. The end of the second zone is the **Johnson bound**. Finding all the candidate rules near a smudged list is called **list decoding**. For a Reed-Solomon code with rate $$\rho$$, the two lines sit at about $$(1 - \rho)/2$$ and $$1 - \sqrt{\rho}$$. With rate one quarter, that is three eighths and one half.

## How do you ask questions about a notebook you cannot see?

Now for the game itself. The Storyteller does not hand over the whole notebook. That would defeat the point. Instead, she seals it.

Here is how sealing works. She takes every page, and from all the pages she makes one short fingerprint, a bit like a wax seal that depends on every letter inside. She gives the Inspector only the seal. Later, when the Inspector asks "what is on line 4,217?", the Storyteller shows that one line together with a small receipt proving the line belongs to the sealed notebook. Changing even one digit after sealing would break the receipt.

The game then goes back and forth. The Storyteller seals a notebook. The Inspector rolls dice and sends the result. The Storyteller seals another notebook based on the dice. This repeats a few times. At the end, the Inspector asks to open a handful of lines from each sealed notebook, checks that they fit together, and says yes or no.

![The sealed notebook game as a back-and-forth: the Storyteller sends a seal, the Inspector sends a dice roll, and at the end the Inspector opens a few lines and receives receipts]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/fri/fri-eli10-sealed-notebook-sequence.png)

Two details make this practical. First, the dice rolls can be replaced by a trick. Instead of the Inspector rolling, the Storyteller computes the "roll" from the seals she has already sent, using a scrambling recipe that nobody can steer. That way she can play the whole game alone, write down everything, and mail the result as a single letter. Second, the cost of the letter is mostly the receipts. Every line the Inspector opens needs one receipt. So the whole design pushes towards opening as few lines as possible.

> **The grown-up name.** The back-and-forth with sealed notebooks and line-by-line peeks is an **interactive oracle proof**, or **IOP**. The seal is a **Merkle root** and the receipt is a **Merkle proof** (both built from a hash function, a scrambler that turns any input into a short fingerprint). Replacing the dice with a hash of the seals is the **Fiat-Shamir transformation**. Doing both at once is called the **BCS compiler**, and the single letter that comes out is a **SNARK**.

## How do you check one value with a division trick?

The Inspector often needs more than "the notebook follows some rule." She needs to know what the rule says at a particular spot, one that is not even in the notebook. For example: "your rule, at spot 3, gives 10. True?"

Here is a clever trick. Take every number in the notebook, subtract 10, and divide by (that spot minus 3). If the claim was true, this new list follows a rule that is *one step shorter* than the old one. If the claim was false, the new list is a mess that follows no short rule at all. So the Inspector just runs the same closeness check on the new list.

Let us try it with the rule "spot times itself, plus one." Its values at spots 1, 2, 4 and 5 are 2, 5, 17 and 26. The Storyteller claims the rule gives 10 at spot 3, which is correct.

```
spot 1:  (2  - 10) / (1 - 3) = (-8) / (-2) = 4
spot 2:  (5  - 10) / (2 - 3) = (-5) / (-1) = 5
spot 4:  (17 - 10) / (4 - 3) =   7  /   1  = 7
spot 5:  (26 - 10) / (5 - 3) =  16  /   2  = 8
```

The new list is 4, 5, 7, 8. That is just "spot plus three." A one-step-shorter rule, exactly as promised.

Now suppose she had lied and claimed 11 instead:

```
spot 1:  (2  - 11) / (1 - 3) = 4.5
spot 2:  (5  - 11) / (2 - 3) = 6
spot 4:  (17 - 11) / (4 - 3) = 6
spot 5:  (26 - 11) / (5 - 3) = 7.5
```

The new list is 4.5, 6, 6, 7.5. No "spot plus something" rule fits those. The lie turned a tidy list into a messy one, and mess is exactly what the closeness check catches.

![Activity diagram of the division trick: subtract the claimed value, divide by spot minus the query spot, then run the closeness check on the result]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/fri/fri-eli10-division-trick-workflow.png)

One more nice thing: the Inspector never needs the new list written down. Whenever she wants to peek at line 4,217 of the new list, she peeks at line 4,217 of the sealed notebook and does the subtraction and division herself.

> **The grown-up name.** This is **quotienting**: the new list is $$(u(x) - b) / (x - a)$$ where $$a$$ is the spot asked about and $$b$$ is the claimed value. Checking several spots at once uses a **vanishing polynomial** (zero at all the asked spots) and an **interpolation polynomial** (hitting all the claimed values). A list that is computed on the fly from a sealed one, rather than sealed itself, is a **virtual oracle**.

## Why ask a surprise question first?

Remember the second zone of the smudge ruler, where a smudged notebook can be close to two or three rules at once? That opens a loophole. A sneaky Storyteller could answer the first question using rule A, and the second question using rule B. Each answer passes the division trick on its own. But she never committed to one rule, which is cheating.

The fix is simple. Before asking any real questions, the Inspector picks a random spot from far outside the notebook and says: "What does your rule give here?" The Storyteller must answer with a number. From then on, every division trick includes this surprise question along with the real one.

Why does that close the loophole? Because two different short rules almost never agree at a random spot. If the Storyteller answered the surprise with rule A's value, she cannot later switch to rule B, because rule B gives a different value at the surprise spot, and the division trick would turn that into mess. One surprise question welds her to a single rule.

> **The grown-up name.** The surprise question is an **out-of-domain sample**, and the technique is called **DEEP**, short for Domain Extension for Eliminating Pretenders. It works because the number of candidate rules is small (that is the Johnson bound again) and the field of possible spots is huge, so the chance two candidates collide at a random spot is tiny, about the odds of guessing which grain of sand on a beach someone is thinking of.

## Can you check many notebooks with one dice roll?

Sometimes the Storyteller has ten notebooks, and the Inspector wants to know that all ten follow short rules. Running the whole game ten times would be slow.

Instead, the Inspector rolls a number, say 7. The Storyteller builds one blended notebook: line 1 of the blend is line 1 of notebook one, plus 7 times line 1 of notebook two, plus 49 times line 1 of notebook three, and so on. Then they play the game once, on the blend.

If all ten notebooks follow short rules, the blend follows a short rule too, whatever number was rolled. That part is easy. The surprising part is the other direction. If even one of the ten notebooks is a mess, the blend is a mess for almost every roll. A mess cannot hide inside a blend. Proving that took mathematicians until 2020, and it holds as long as we stay in the second zone of the smudge ruler.

> **The grown-up name.** The blend is a **random linear combination**, and this is **batching**. The theorem that says a mess cannot hide is the **proximity gap theorem**. It also says something extra: all ten notebooks are clean on the *same* set of lines, which is called **correlated agreement**.

## How do you fold a notebook in half?

This is the step that gives FRI its name and its speed. The idea is to turn a long notebook that follows a rule with, say, eight numbers on its note into a notebook *half as long* that follows a rule with *four* numbers on its note. Then do it again. And again. After a few folds the notebook is so short the Inspector can just read the whole thing.

Here is how one fold works. Take a rule like "2 + 3x + 5x² + 4x³". Split it into two halves: the pieces where x is raised to an even power, and the pieces where it is raised to an odd power.

```
even half:  2 + 5x²    ->  think of it as  2 + 5y     (with y = x²)
odd half:   3x + 4x³   ->  x times (3 + 4x²)  ->  3 + 4y
```

Each half has only two numbers on its note instead of four. Now the Inspector rolls a number, say 10, and the Storyteller blends the halves: even half plus 10 times odd half.

```
(2 + 5y) + 10 × (3 + 4y) = 32 + 45y
```

The folded rule is "32 + 45y". Two numbers on the note, down from four. And the folded notebook only needs entries at the squares of the old spots, which is half as many spots, because a spot and its negative twin both square to the same thing.

The important question is whether folding could accidentally turn a messy notebook into a clean one, letting a cheat slip through. The answer, proven using the same 2020 theorem as before, is no: for almost every roll, a notebook that was far from every rule folds into a notebook that is still far from every rule. Smudges do not disappear when you fold.

![Activity diagram of one fold: split the rule into even and odd halves, blend them with a rolled number, and get a notebook half as long that follows a rule half as complex]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/fri/fri-eli10-folding-workflow.png)

> **The grown-up name.** This is **folding**. The spots are chosen as **roots of unity** (a set where every spot $$x$$ has a partner $$-x$$, and squaring maps both to the same new spot). The even and odd halves are written $$f_e$$ and $$f_o$$, and the fold is $$f_e + r \cdot f_o$$ for the rolled number $$r$$. The guarantee that smudges survive folding is the **distance-preservation lemma**, and it is what FRI repeats round after round.

## Putting it all together

Here is the whole story, start to finish.

1. The Storyteller has done a big calculation and turned the result into a giant notebook that should follow a short rule. She seals it and sends the seal.
2. The Inspector asks a surprise question about a spot far outside the notebook. The Storyteller answers. She is now welded to one rule.
3. The Inspector asks the questions she came for: "what does your rule give at this spot?" The division trick checks each answer, turning "is this value right?" into "is this new list close to a short rule?"
4. The Inspector rolls a number and the Storyteller blends all of those new lists into one, so there is only one closeness check to run.
5. That one check is done by folding: halve the notebook, roll, halve again, until what is left is short enough to read in full. At each fold the Inspector opens a few lines of the old notebook and the new one and checks that the fold was done honestly.
6. Every line opened comes with a receipt against its seal. The Storyteller computes the dice rolls from the seals, so she can do all of this alone and mail one letter.

The Inspector reads the letter, checks the receipts, redoes a few subtractions and divisions, and is done. She has peeked at a few dozen lines out of a million, and if the Storyteller cheated anywhere, the odds of getting away with it are smaller than one in a billion billion billion.

This article covers steps 1 to 4 and the idea behind step 5. The exact rules of the folding game in step 5, and how many lines to open at each fold, are the subject of the second half of the lecture.

## Summary

FRI is a way to check that a huge list of numbers follows one short rule by peeking at only a few entries. It works because two different short rules almost never agree, so a list that is even slightly wrong stands out once you look at enough of it. The Inspector cannot catch a single smudge, so she settles for catching lists that are far from every rule, and that turns out to be enough. Sealed notebooks make the peeks trustworthy. A division trick turns "is this value right?" into "is this list clean?" A surprise question stops the Storyteller from switching rules. Blending checks many lists at once. And folding shrinks the list by half each round until it is small enough to read.

![Mindmap of FRI explained simply, covering short rules, codes and smudges, the smudge budget, the sealed notebook game, the division trick, the surprise question, blending and folding]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/fri/2026-09-14-fri-proximity-proofs-eli10-mindmap.png)

## Frequently Asked Questions

**Q: But why not just send the sticky note with the rule on it? Then the Inspector could check everything herself.**

Sometimes she could, and then no game is needed. But in the real use of FRI, the "rule" is the whole record of a big calculation, and the notebook is a stretched-out version of that record. The sticky note itself can be as big as the calculation. The point is that the Inspector wants to spend far less effort than the Storyteller did. Peeking at a few lines of a sealed notebook costs her almost nothing. Reading the whole rule would cost as much as redoing the work.

**Q: What if the Storyteller is wrong in exactly one spot? Does she get away with it?**

Yes, probably. Twenty random peeks will almost never land on one bad line out of a million. That is why the Inspector only promises to catch notebooks that are far from every rule. In real systems this is fine, because a notebook that is close to a valid one still pins down the same single rule, and it is the rule that matters, not the individual lines. In real systems this is more complex, but the core idea is the same.

**Q: How does this help in real life?**

Think of a small phone that wants to be sure a giant computer did a calculation correctly, without redoing it. Or a blockchain (a shared ledger that thousands of computers keep in sync) that wants to accept thousands of transactions at once but only has room to check a tiny proof. FRI-based proofs are used for exactly that. The big computer plays the Storyteller, does the work, and mails a short letter. Everyone else plays the Inspector and checks the letter in a blink.

**Q: What goes wrong if you skip the surprise question?**

Then a sneaky Storyteller with a smudged notebook can answer different questions using different candidate rules, and every single answer passes the division trick on its own. The Inspector would think she checked one rule when she had checked pieces of two or three. The surprise question welds the Storyteller to one rule before any real question is asked, so switching later gets caught.

**Q: Can you give me another example of "two short rules almost never agree"?**

Think of straight lines drawn on graph paper. Two different straight lines can cross at most once. Two different curves that bend once (like a smile) can cross at most twice. In general, two different rules with a few numbers on their notes can meet only a few times, and then they part forever. So if you check a random spot and both rules give the same answer, you were incredibly unlucky, or they are secretly the same rule.

**Q: Why does folding not lose information?**

The two halves together are the whole rule, so nothing is thrown away when you split. Blending them with a random number does mix them, but because the Inspector chose the number after the Storyteller sealed the notebook, the Storyteller could not arrange for a mess to cancel out. That is why the folded notebook is still a mess if the original was. And each fold is checked: the Inspector opens a few pairs of twin lines in the old notebook and confirms the blend was done honestly.

## References

- [ZK Whiteboard Sessions — S2M7: FRI and Proximity Proofs (Part 1), with Dan Boneh](https://www.youtube.com/watch?v=MBDBrEr2XQg), the lecture this article is based on
- [ZK Whiteboard Sessions](https://zkhack.dev/whiteboard/), the series page
- Eli Ben-Sasson, Iddo Bentov, Yinon Horesh, Michael Riabzev, [*Fast Reed-Solomon Interactive Oracle Proofs of Proximity*](https://eccc.weizmann.ac.il/report/2017/134/), 2017, the original FRI paper
- Eli Ben-Sasson, Lior Goldberg, Swastik Kopparty, Shubhangi Saraf, [*DEEP-FRI: Sampling Outside the Box Improves Soundness*](https://eprint.iacr.org/2019/336), 2019, the surprise question
- Eli Ben-Sasson, Dan Carmon, Yuval Ishai, Swastik Kopparty, Shubhangi Saraf, [*Proximity Gaps for Reed-Solomon Codes*](https://eprint.iacr.org/2020/654), 2020, the theorem that a mess cannot hide in a blend
- Alessandro Chiesa, Eylon Yogev, [*Building Cryptographic Proofs from Hash Functions*](https://snargsbook.org/), 2024, the sealed notebook game in full detail

### Related articles

- [FRI Part 1 in Twelve Cards — The Definitions to Memorise From the Lecture]({{site.url_complet}}/2026/09/14/fri-part-1-flashcards/)
- [FRI in Twelve Cards — The Definitions to Memorise]({{site.url_complet}}/2026/09/14/fri-flashcards/)
- [FRI and Proximity Proofs, Part 1 — Reed-Solomon Codes, IOPs of Proximity, Quotienting and Folding]({{site.url_complet}}/2026/09/11/fri-proximity-proofs-part-1-codes-iop-quotienting-folding/)
- [FRI and Proximity Proofs — The Vocabulary, From Beginner to Advanced]({{site.url_complet}}/2026/09/11/fri-proximity-proofs-glossary/)
- [The GKR Protocol — How to Check a Million Calculations Without Doing Them]({{site.url_complet}}/2026/06/19/gkr-protocol-explained/)
- [Zero-Knowledge Proofs Explained Like You're Ten — Why Proofs Break and How to Spot It]({{site.url_complet}}/2026/06/19/zkp-vulnerabilities-eli10/)
