---
layout: post
title: "The GKR Protocol — How to Check a Million Calculations Without Doing Them"
date:   2026-06-19
lang: en
locale: en-GB
categories: cryptography ZKP eli10
tags: zkp interactive-proof gkr sum-check multilinear-extension analogy
description: An intuitive guide to the GKR protocol through everyday analogies. Learn how a verifier can check a massive computation by asking a few clever questions, without re-running a single step.
image: /assets/article/cryptographie/zero-knowledge-proof/gkr/2026-06-19-gkr-protocol-explained.png
isMath: true
---

Imagine a classmate claims to have added up one million numbers and got the answer 42. You could grab a pencil and check all one million additions yourself, but that takes as long as it took them. Is there a smarter way?

The GKR protocol says yes. Named after its creators Goldwasser, Kalai, and Rothblum, it is an interactive proof system that lets a slow, lazy checker confirm the result of a large computation by playing a short question-and-answer game with the person (or computer) who did the work. At the end of the game, the checker is convinced the answer is correct, yet has done only a tiny fraction of the total work.

This article walks through the core ideas using everyday analogies, building toward the full protocol one piece at a time.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why Would You Trust Someone Else's Homework?

Suppose your teacher needs to know whether the entire school cafeteria (say, 512 students) all received the correct change at lunch. Checking each receipt one by one takes all day. What if there were a way to ask a few smart questions and be almost certain the accounts are correct?

Computer scientists call this the **delegation problem**. A *verifier* (the person checking, who has very little time) wants to check the output of a large computation. Somebody else did that computation. That somebody is called the *prover*, and nobody has any reason to trust them.

The obvious approach is to redo the work. That costs exactly as much as doing it yourself in the first place, so it helps nobody.

GKR takes a different route. It turns the checking into a sequence of small challenges. At every step the prover has to commit to an answer before hearing the next question. One single inconsistency anywhere in the chain gets caught, with very high probability.

## How Does the Cookie Game Work?

Before explaining GKR itself, we need one key ingredient. It is called the **sum-check protocol**, and it is easiest to meet it as a game.

### The setup

A baker claims to have baked exactly 1,024 cookies. Each cookie has a quality score between 1 and 10. The baker says the total score of all the cookies is 6,144. You want to check this without tasting 1,024 cookies.

### The game

You and the baker play a game with several rounds. The cookies sit on a grid, so every cookie has a position, and every position has several coordinates (like a seat number that says "row 3, column 7, shelf 2").

**Round 1.** You ask the baker a question about the *first* coordinate only: "add up the scores of every cookie whose first coordinate is 0, then do the same for the ones where it is 1." The baker sends back two numbers. Every cookie belongs to exactly one of those two groups, so the two numbers have to add up to the grand total. You check that: 2,500 plus 3,644 does indeed make 6,144.

Then you pick a random number and hand it to the baker. Notice the order. The baker answered first, and only then did you choose.

**Round 2.** The baker's job is now narrower. They must report the total when the first coordinate is pinned to your random number. You check the new answer against the previous one, pick another random number, and pass it on.

**The last round.** After one round per coordinate, the baker has nothing general left to report. They must name the score of one single specific cookie. You walk over and taste that one cookie yourself.

![The cookie game between the baker and you, one round at a time]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/gkr/gkr-eli10-cookie-game-sequence.png)

### Why the baker cannot cheat

If the baker lied about the total, they must keep lying consistently in every single round. But you choose your random number *after* they answer, so they cannot tune an earlier answer to fit a challenge they have not seen.

The chance that a lying baker survives the whole game is tiny, though it is not exactly zero. Mathematicians write the bound like this:

$$
\begin{aligned}
\text{chance of cheating} \leq \frac{v \cdot d}{\lvert\mathbb{F}\rvert}
\end{aligned}
$$

Here $$v$$ is the number of coordinates, $$d$$ is a small number describing how curvy the maths is, and $$\lvert\mathbb{F}\rvert$$ is how many different random numbers you could have picked. Put in real numbers: with 10 coordinates, $$d = 2$$, and roughly $$3 \times 10^{38}$$ possible random numbers, the chance comes out around 1 in $$10^{37}$$. That is about as likely as picking one particular grain of sand out of ten thousand planets' worth of beaches.

### What just happened

You did one cheap check per round, plus one taste at the end. The baker did all the heavy adding. That is the sum-check protocol: checking a huge total over a big grid by narrowing down one coordinate at a time.

## What Is a Smooth Surface Through a Table of Numbers?

The cookie game works on *formulas*, not just tables of numbers. Here is why that matters.

### From a table to a formula

Imagine a small table:

| $$x_1$$ | $$x_2$$ | $$f(x_1, x_2)$$ |
|--------|--------|------------|
| 0 | 0 | 3 |
| 0 | 1 | 7 |
| 1 | 0 | 5 |
| 1 | 1 | 2 |

This table has four entries. It only says anything at the four corners. A **multilinear extension** is the one smooth formula that passes through all four corners and is as gentle as possible in between. Think of stretching a rubber sheet so it touches all four corner posts. There is exactly one way to do it, and once it is stretched you can measure the height anywhere, not just at the posts.

The formula looks like this:

$$
\begin{aligned}
\tilde f(x_1, x_2) = f(0,0)(1-x_1)(1-x_2) + f(0,1)(1-x_1)x_2 + f(1,0)x_1(1-x_2) + f(1,1)x_1 x_2
\end{aligned}
$$

Each of the four pieces switches on at exactly one corner and switches off at the other three. Try the middle of the table, where both coordinates are $$0.5$$. Every one of the four pieces contributes a quarter, so the answer is $$3 \times 0.25 + 7 \times 0.25 + 5 \times 0.25 + 2 \times 0.25 = 4.25$$.

### Why this trick is worth so much

Here is the useful fact. Two different tables always give two different rubber sheets, and two different rubber sheets almost never have the same height at a randomly chosen spot. Change one single entry in the table and the whole sheet shifts nearly everywhere.

So if you want to know whether two enormous tables are identical, you do not compare them entry by entry. You measure the height of both sheets at one random spot. A table of a million values gets checked with a single number.

## What Does a Chocolate Factory Have to Do with Computing?

The computations GKR handles are shaped like **layered arithmetic circuits**. A chocolate factory is a fair picture of one.

- The **ingredients** (sugar, cocoa, milk, butter) go in at the top.
- At each **stage**, machines process whatever the stage above produced.
- The **finished bar** comes out at the bottom.

Every machine takes two things from the stage above and does one of two jobs:

- an **adding machine** puts its two inputs together;
- a **multiplying machine** multiplies them.

```
  [sugar] [cocoa] [milk] [butter]   <- INGREDIENTS (top stage)
      \     /         \    /
       \   /           \  /
        [+]             [*]          <- mix the ingredients
          \             /
           \           /
            [*]     [+]              <- cook and blend
               \   /
                \ /
                [+]                  <- final mix
                 |
                [*]                  <- packaging
                 |
           CHOCOLATE BAR             <- the claimed answer
```

The **wiring plan** says which machine feeds which. That plan is public: anybody can look it up. What is expensive is the pile of intermediate values flowing through the pipes, because working those out means running the whole factory.

One detail matters for later. Chocolate flows downward, from ingredients to bar. The inspection runs the other way, from the bar back up toward the ingredients.

## How Does the Inspector Play the Game?

Now every piece is on the table. GKR is a factory inspection. The checker is the inspector, and the prover is the factory manager.

### Where the inspection starts

The inspector shows up and sees the output: one chocolate bar. She asks the obvious question.

> "Is this the right bar?"

The manager says yes and points at the stage that produced it. Now he has to back that up.

### Working upward, one stage at a time

![The factory inspection, stage by stage]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/gkr/gkr-eli10-factory-inspection-sequence.png)

At every stage the inspector is holding exactly one claim, of the form "the machine at position $$z$$ in this stage produced the value $$v$$". The manager has to show that this fits what the stage above produced.

The value at a machine is fixed by the wiring plan and the two values feeding into it. Written out over the whole stage, that becomes:

$$
\begin{aligned}
\tilde V_i(z) = \sum_{w_1, w_2} \Bigl[ \tilde A_i(z, w_1, w_2)\bigl(\tilde V_{i+1}(w_1) + \tilde V_{i+1}(w_2)\bigr) \\
+ \tilde M_i(z, w_1, w_2) \cdot \tilde V_{i+1}(w_1) \cdot \tilde V_{i+1}(w_2) \Bigr]
\end{aligned}
$$

That is a wall of symbols, so here is what it says in words. Go through every possible pair of machines in the stage above, written $$w_1$$ and $$w_2$$. The two pieces $$\tilde A_i$$ and $$\tilde M_i$$ are the rubber sheets of the wiring plan, one for adding machines and one for multiplying machines. Each of them equals 1 when the wiring really does connect that pair to machine $$z$$ through that kind of machine, and 0 otherwise. So every pair that is not actually wired up contributes nothing, and the pair that *is* wired up contributes either the sum or the product of its two values.

The important thing is the shape. It is a giant total over every pair. And checking a giant total is exactly what the cookie game does.

### One stage in five steps

1. The inspector says: "convince me that this machine really produced that value."
2. They play the cookie game over the stage above.
3. The game ends with the inspector holding *two* questions instead of one, about two randomly chosen machines in that stage.
4. A short extra step, the **line trick**, turns those two questions back into one.
5. The inspector now has a single fresh question about the stage above, and the whole thing repeats.

### The line trick

Why does the inspector end up with two questions? Because each machine has two inputs, so the game naturally lands on a pair.

Two questions per stage would be a disaster. Two becomes four at the next stage, four becomes eight, and after twenty stages the inspector is holding over a million questions. She might as well have run the factory herself.

The line trick fixes this. Picture the two machines the inspector is asking about as two points. Draw the straight line through them. The manager describes what the rubber sheet looks like along that line, which takes only a handful of numbers. The inspector checks that the description matches her two questions at the two ends. Then she picks a random spot somewhere along the line and keeps only the question at that spot.

Two questions in, one question out, every time. The inspector never carries more than one.

### How the inspection ends

At the very top stage sit the raw ingredients, and the inspector brought those herself. She can check the last remaining question on her own, without asking the manager anything. If it matches, the whole factory ran honestly.

## Why Is This Actually Faster?

Let us count who does what.

| Who | What they do | Cost |
|-----|-------------|------|
| Manager (prover) | Runs the full factory and works out the game answers for every stage | $$O(S \log S)$$ |
| Inspector (verifier) | Plays the cookie game once per stage | $$O(D \log S)$$ |
| Messages | A short list of numbers per stage | $$O(D \log S)$$ |
| Final check | Measures the ingredient sheet herself | $$O(n)$$ |

Here $$S$$ is the number of machines in the whole factory, $$D$$ is the number of stages, and $$n$$ is the number of ingredients.

The naive approach costs the inspector $$O(S)$$, because she runs everything. GKR costs her $$O(n + D \log S)$$. For a factory with a million machines, twenty stages and a thousand ingredients, that is the difference between a million steps and roughly a couple of thousand.

The manager pays a small price for this. He does a bit more work than simply running the factory, because he also has to produce the game answers. That is the trade: the person with the computing power does slightly more, and the person without it does dramatically less.

## The Whole Thing as One Short Story

> **The Magic Audit**
>
> A factory produces 1,000,000 widgets through 20 assembly stages. An auditor arrives to check whether the final output is correct. She does not have time to watch all 20 stages run.
>
> Instead, she plays a game with the factory manager.
>
> 1. The auditor says: "prove to me that the output is correct."
> 2. The manager says: "it is correct, because stage 19 produced exactly these values."
> 3. The auditor does not check all of stage 19. She plays the cookie game about stage 19 until the question shrinks down to one specific widget.
> 4. The auditor then says: "prove to me that *that* widget's value is correct."
> 5. The manager appeals to stage 18, and the game runs again.
> 6. This repeats for all 20 stages.
> 7. At the raw materials, the auditor checks the value directly, because she brought the raw materials herself.
>
> At no point did the auditor re-run a full stage. She only asked targeted questions. Yet if the manager had cheated anywhere, she would have caught it with overwhelming probability.

## How Do You Keep the Values Secret?

A plain GKR game leaks something. The messages the manager sends carry hints about the values inside the factory, and sometimes those values are private.

The fix is to add noise that cancels out. Each message gets a random number bundled into it, chosen so that the *total* is unaffected:

$$
\begin{aligned}
\hat g_j(X_j) = g_j(X_j) + r_j(X_j), \quad r_j(0) + r_j(1) = 0
\end{aligned}
$$

The second condition is doing all the work. It says the random piece adds up to zero across the two halves, so every total the inspector checks stays exactly the same. The individual numbers, however, are now buried under randomness the inspector cannot strip away.

With that addition, the inspector still ends up certain the answer is right, and still learns nothing about what happened inside the factory. That property is called **zero-knowledge**.

## Conclusion

The GKR protocol replaces "redo the work" with "play a short game". Three ideas make it work. A table of values turns into a smooth rubber sheet, so one measurement at a random spot stands in for the whole table. The cookie game shrinks a huge total down to one single lookup, one coordinate per round, with the checker always choosing her random number after the other side has answered. And the line trick keeps the checker carrying exactly one open question as the inspection climbs from the finished product back to the raw ingredients, which is what stops the questions from doubling at every stage.

None of this makes cheating impossible, and it is worth being precise about that. It makes cheating so unlikely that you would expect to wait longer than the age of the universe to see it happen once. In exchange, a checker with a phone can verify work that took a data centre to produce. That is why the same machinery now sits inside blockchain proof systems and inside tools for checking computations run on somebody else's computer.

![GKR protocol explained in plain words, summary mindmap]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/gkr/2026-06-19-gkr-protocol-explained.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Prover** | The one who did the big computation and now has to convince somebody it was done right. The factory manager in the story. |
| **Verifier** | The one checking the work, who has very little time. The inspector in the story. |
| **Delegation** | Handing a big computation to somebody else and then checking their answer far more cheaply than redoing it. |
| **Sum-check protocol** | The cookie game: a way to check a huge total by narrowing it down one coordinate per round, ending in a single lookup. |
| **Multilinear extension** | The single smooth rubber sheet stretched through all the corner values of a table, letting you measure the table anywhere, not just at the corners. |
| **Arithmetic circuit** | The chocolate factory: a network of machines that only add or multiply, arranged so values flow from the ingredients to the finished product. |
| **Layer** | One stage of the factory. Every machine in a stage takes its two inputs from the stage directly above it. |
| **Wiring plan** | The public map saying which machines feed which. Everybody can read it, so nobody has to be told what it is. |
| **Line trick** | The short step that turns the two questions left over at the end of each round back into a single question. |
| **Zero-knowledge** | The property that the checker ends up certain the answer is right while learning nothing about the values inside the computation. |

## Frequently Asked Questions

**Q: Do the baker and the checker have to be in the same room?**

Not at all. In real systems both sides are programs on different computers, sending messages over a network. Every round of the game is just one message each way, like a slow text conversation. The one thing that matters is the order: each side's message has to go out before the other side's reply comes back, so nobody can peek at a challenge before answering.

**Q: But why bother with rubber sheets? Would checking a few random cookies not be enough?**

Random tasting catches sloppy cheating, like half the cookies being wrong. It does not catch careful cheating. A clever baker could get one single cookie wrong and you would almost certainly never pick that one. The rubber sheet closes the loophole, because changing even one entry in the table shifts the sheet nearly everywhere. So one measurement at a random spot notices a single wrong cookie just as reliably as a thousand wrong ones.

**Q: What if the baker guesses your random numbers before you pick them?**

That is exactly the attack the game is built to stop, and the defence is the order of play. You pick your random number only after the baker has already sent their answer for that round. They cannot see the future, so they are locked in. If they lied, they cannot go back and adjust a message you have already received. The chance of them simply getting lucky is roughly 1 in $$10^{37}$$ per round.

**Q: What goes wrong if you skip the line trick?**

The inspector's workload explodes. After each stage she is holding two questions instead of one. Skip the trick and those two become four at the next stage, then eight, then sixteen. After twenty stages she is juggling more than a million questions, roughly one per machine in the factory, so she is back to checking everything by hand. The line trick squashes two questions into one after every stage, so she always carries exactly one, no matter how many stages there are.

**Q: Could the manager just send all the intermediate values to the inspector?**

He could, and it would prove nothing useful. That list is as long as the whole computation, so receiving it and checking it takes about as long as running the factory. The point of GKR is that only a short list of numbers travels per stage. The inspector gets certainty about a huge computation while receiving a tiny amount of information.

**Q: Can you give me another example of what zero-knowledge means here?**

Picture the cookie version. You finish the game completely convinced that the total score is 6,144, and yet you were never told what any individual cookie scored. You know the sum is honest, and you know nothing else. In GKR, the same effect comes from mixing random noise into every message, chosen so the noise cancels out of the totals the inspector checks but hides the values underneath.

**Q: How does this help in real life?**

It lets small devices trust big ones. A phone, or a blockchain smart contract with a tight budget, can accept the result of a computation that a large server carried out, without repeating it. Blockchain rollups use exactly this to prove that thousands of off-chain transactions were processed correctly. The proof libraries built on GKR's ideas, such as Spartan and Libra, produce these proofs in milliseconds on ordinary hardware for practical problem sizes.

## References

- Goldwasser, S., Kalai, Y. T., Rothblum, G. N.: [*Delegating Computation: Interactive Proofs for Muggles*](https://dl.acm.org/doi/10.1145/2699436). STOC 2008 / JACM 2015. (The original GKR paper.)
- Lund, C., Fortnow, L., Karloff, H., Nisan, N.: *Algebraic Methods for Interactive Proof Systems*. JACM 1992. (Where the cookie game comes from.)
- Thaler, J.: [*Proofs, Arguments, and Zero-Knowledge*](https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.html). Lecture notes, 2022. (Chapters 4 and 5 are a self-contained treatment.)
- Xie, T., Zhang, J., Zhang, Y., Papamanthou, C., Song, D.: [*Libra: Succinct Zero-Knowledge Proofs with Optimal Prover Computation*](https://eprint.iacr.org/2019/317). CRYPTO 2019.
- Setty, S.: [*Spartan: Efficient and general-purpose zkSNARKs without trusted setup*](https://eprint.iacr.org/2019/550). CRYPTO 2020.
