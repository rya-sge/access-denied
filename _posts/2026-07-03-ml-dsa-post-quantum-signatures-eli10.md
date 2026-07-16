---
layout: post
title: "How Computers Sign Messages That Even a Quantum Computer Cannot Fake — Explained for a 10-Year-Old"
date:   2026-07-03
lang: en
locale: en-GB
categories: cryptography
tags: cryptography post-quantum lattice ml-dsa digital-signature analogy explainer
description: A simple guide to ML-DSA, the new signature that quantum computers cannot fake, explained with everyday analogies about wax seals, secret paint, and drawings that must stay inside the lines.
image: /assets/article/cryptographie/lattice/2026-07-03-ml-dsa-post-quantum-signatures-eli10-mindmap.png
isMath: false
---

Imagine you get a letter that says "meet me at the treasure at noon" with your best friend's name signed at the bottom. How do you know your friend really wrote it, and not a sneaky rival who wants the treasure for himself? Long ago, people pressed a special wax stamp onto a letter to prove it was really from them. Computers do the same thing with something called a digital signature. But there is a new worry: a future kind of super-computer might learn to fake today's stamps. This article explains a brand-new stamp, called ML-DSA, that is built so even that super-computer cannot copy it.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and the custom skill `create-article-eli10`

[TOC]

## Why Are Today's Signatures Suddenly in Danger?

Think of a padlock. For years, one clever kind of padlock has kept everyone safe because picking it by hand would take longer than a lifetime. Now imagine someone is building a robot that can try millions of picks every second. A lock that was safe against human thieves is not safe against that robot.

A digital signature is a kind of lock. Today's most common signatures (with names like RSA and ECDSA) are safe because breaking them means solving a giant number puzzle, and normal computers are far too slow to solve it. But scientists are slowly building a new type of machine called a quantum computer. A quantum computer can solve that exact number puzzle very fast. So years later, once such a machine exists, an attacker could fake a message you sign today. That is a real problem for things that must stay trustworthy for a long time, like the software inside a car or a signed legal contract.

The fix is to build the lock out of a different puzzle. ML-DSA (its full name is the Module-Lattice-Based Digital Signature Algorithm) uses a puzzle about hidden numbers that even a quantum computer does not know how to solve quickly. A group of experts at a place called NIST tested many ideas for years and picked this one as the new standard in 2024.

## How Do You Hide a Secret in Plain Sight?

Picture a huge multiplication done in front of everyone, but with a tiny bit of dust sprinkled on the answer. You pick a small secret number. You multiply it by a big number that everyone can see. Then you sprinkle a little dust so the answer is slightly off. You show people the big number and the dusty answer, but never your secret. Because of the dust, nobody can just divide to get your secret back. The dust hides it.

This is the heart of ML-DSA. Your secret is a set of small numbers. The signer mixes them into a big public sum and adds a little "fuzz" on top. The result is the public key, which is the part everyone is allowed to see. Getting the secret back out of it is the hard puzzle that keeps quantum computers stuck.

Here is a tiny worked example with small numbers:

- Secret number: **4**
- Public multiplier everyone can see: **10**
- Tiny fuzz: **1**
- Public answer: 4 times 10, plus 1, equals **41**

If there were no fuzz, you could just do 40 divided by 10 and instantly find the secret 4. The fuzz turns a clean 40 into a messy 41, so simple division stops working. In the real ML-DSA there are not one but hundreds of secret numbers, all multiplied by a giant grid and all fuzzed together at once. Untangling that many fuzzy sums at the same time is what no computer, quantum or not, knows how to do in any reasonable amount of time.

```
   HIDING THE SECRET  (a one-way street)

   secret small numbers ──► [ multiply by big public grid ] ──► add fuzz ──► PUBLIC KEY
        (kept private)                                                      (safe to show)

   Going forward is easy.  Going backward (public key ──► secret) fails: the fuzz blocks it.
```

## How Does the Signer Prove the Secret Without Showing It?

Think about mixing paint. You have one drop of a secret colour. If you show the drop, everyone learns your colour. So instead you stir it into a big bucket of random white paint. The bucket now has a shade that depends on your secret drop, but nobody can look at the bucket and pull the single drop back out. And yet, with the right recipe, a judge can prove your special drop really is in there.

Signing a message works in three quick moves, like a little game between the signer and a checker.

1. **The random scribble.** The signer makes a big random scribble (the bucket of white paint) and shows a scrambled copy of it. This scrambled copy is called the commitment.
2. **The surprise question.** The signer drops the message and the scrambled scribble into a special machine called a hash. A hash is like a blender: you drop things in, you get a jumbled number out, and nobody can steer what comes out. That jumbled number is the surprise question, called the challenge.
3. **The answer.** The signer answers by stirring the secret into the scribble in an amount set by the challenge. Because the scribble is so big and random, it hides the secret, but the answer still only fits together correctly if the signer used the real secret and signed this exact message.

The checker then does a bit of arithmetic. If the numbers line up, the checker is sure the signer knew the secret, without ever seeing it. This clever three-move idea is very old (it is named after two people, Fiat and Shamir), and ML-DSA rebuilds it with the fuzzy-number puzzle so a quantum computer cannot break it.

## Why Does the Signer Keep Throwing Answers in the Bin?

Imagine you are drawing inside a colouring book and the rule is that your crayon must stay inside the printed lines. Sometimes your hand slips and the colour pokes out past a line. When that happens you tear out the page, throw it away, and start again on a fresh page. You only hand in a page where the colour stayed neatly inside.

ML-DSA does exactly this while signing. Remember, the answer is the secret stirred into the random scribble. If you were unlucky, the answer can lean a little too much toward the secret, and that lean would slowly give the secret away if you handed out many signatures. So the signer checks every answer. If any part of it poked "outside the lines" (grew too big), the signer throws the whole attempt in the bin and tries again with a brand-new scribble. Only an answer that lands safely in the middle gets sent out.

This throwing-away is called rejection sampling. On average the signer needs about four or five tries before an answer is good enough to keep. That is why signing takes a slightly different amount of time each go, a bit like re-rolling dice until you get a roll you like.

```
   THE SIGNING LOOP  (keep trying until it stays inside the lines)

        ┌───────────────────────────────────────────────┐
        │  make a fresh random scribble                  │
        │  mix the secret in, using the surprise question│
        ▼                                                │
   is the answer safely inside the lines?  ── NO ──►  toss it in the bin ─┘
        │
       YES
        ▼
   add a small sticky note, then send the signature
```

## What Is the Little Sticky Note on the Signature?

To save space, shops often round prices on a receipt. Instead of printing 4 dollars and 99 cents, a tiny receipt might just print "about 5 dollars". That saves ink, but now the total is a little off. To fix it, the shop could staple a small note that says "add one cent back here and here". With the note, you can rebuild the exact total from the rounded numbers.

ML-DSA does the same trick to keep its public key small. It chops off the last few digits of the big public number so the key takes less room. But that chopping makes the checker's math a tiny bit off. So the signature carries a small sticky note, called the hint, that tells the checker exactly where to nudge the numbers back into place. The hint is short, and with it the checker can rebuild the correct value even though part of the public key was thrown away. Without the hint, the space-saving and the checking could not both work.

## How Does the Checker Know a Signature Is Real?

Picture a teacher checking your homework against an answer sheet. The teacher does not trust the answer you wrote at the top of the page. Instead, the teacher redoes the problem from scratch and then compares. If the teacher's answer matches yours, the homework is correct. If it does not match, something is wrong.

Checking an ML-DSA signature works the same way, and this part never needs any re-tries. The checker takes the public key and the signature, redoes the arithmetic, applies the sticky-note hint, and then runs the very same blender (the hash) on the message. Out pops a jumbled number. The checker compares it to the number the signer wrote inside the signature. If the two numbers are identical, the signature is genuine. If someone changed the message by even one letter, or used the wrong secret, the blender spits out a different number and the check fails. So a faker cannot slip anything past it.

One important detail: the checker rebuilds everything from its own copy of the message and the public key. It never simply believes a value handed over by the signer. That is what ties a signature to one exact message from one exact person.

## Why Are There Three Different Sizes?

Bike locks come in different strengths. A thin cable lock is light and easy to carry but easier to cut. A thick chain lock is heavy but very hard to break. You pick the one that matches how worried you are.

ML-DSA comes in three strengths too, with the names ML-DSA-44, ML-DSA-65, and ML-DSA-87. The bigger the number, the bigger the secret grid inside, and the harder the puzzle is to crack. But bigger also means the keys and signatures take more room. Here is a rough idea of the sizes:

| Strength | Signature size | How safe |
|----------|----------------|----------|
| ML-DSA-44 | about 2,400 bytes | strong |
| ML-DSA-65 | about 3,300 bytes | stronger |
| ML-DSA-87 | about 4,600 bytes | strongest |

To picture how much bigger this is than older signatures: a popular older signature called Ed25519 is only about 64 bytes, which is smaller than this sentence. ML-DSA signatures are dozens of times larger. That extra bulk is the price we pay for a lock a quantum computer cannot pick. For most uses that trade is well worth it, because a slightly bigger file is a small cost compared to a signature that stays safe for decades.

## Putting It All Together

Let us follow one message from start to finish, using all the ideas above.

1. **Making the keys.** The signer picks small secret numbers, multiplies them by a big public grid, and adds fuzz. The fuzzy result becomes the public key that everyone can see. The small secrets stay hidden.
2. **Signing.** To sign "meet me at the treasure at noon", the signer makes a random scribble, blends the message and scribble to get a surprise question, and stirs the secret in by that amount to form an answer.
3. **Staying inside the lines.** If the answer pokes outside the safe range, the signer bins it and tries again with a new scribble, repeating until an answer lands safely. Then the signer adds the small sticky-note hint.
4. **Checking.** Anyone with the public key redoes the math, uses the hint to fix the rounding, and runs the same blender on the message. If the result matches the signer's number, the letter is proven real.

Every step avoids ever showing the secret, and every step relies on the fuzzy-number puzzle that quantum computers cannot solve. That is how ML-DSA proves who wrote a message while staying safe against machines that do not even exist yet.

## Summary

ML-DSA is a new way for computers to sign messages so that even a future quantum computer cannot forge them. The secret is hidden inside a big multiplication with a bit of fuzz added, and pulling it back out is a puzzle no known computer can solve quickly. To sign, the signer blends the secret into a random scribble tied to the message, throws away any answer that leans too far toward the secret, and keeps only a safe one. A checker can then redo the math and confirm the signature is real without ever learning the secret. The price for this quantum-proof safety is that the keys and signatures are bigger than the ones we use today, but for anything that must stay trustworthy for a long time, that is a fair trade.

![ML-DSA explained for a 10-year-old mindmap]({{site.url_complet}}/assets/article/cryptographie/lattice/2026-07-03-ml-dsa-post-quantum-signatures-eli10-mindmap.png)

## Frequently Asked Questions

**Q: But why can't a quantum computer just solve the fuzzy-number puzzle too?**

A quantum computer is very good at one special number trick, the trick that breaks today's signatures. It is not a magic machine that solves every puzzle. The fuzzy-number puzzle inside ML-DSA is a completely different shape, and nobody has found a way, even with a quantum computer, to untangle hundreds of fuzzy sums at once. So this puzzle stays hard. If someone ever did find a fast way, experts would need to build a new lock again, which is exactly why they keep studying these puzzles.

**Q: What if the signer's random scribble was the same twice by accident?**

That would be bad, and the designers were careful about it. If the same scribble were ever used to sign two different messages, a clever attacker could subtract the two answers and the scribble would cancel out, leaving the secret exposed. To stop this, ML-DSA builds each scribble from a mix of the secret key, the message, and a fresh dash of randomness, so two scribbles are never the same. It is the same reason you should never reuse the same secret code for two different locks.

**Q: How does this help in real life?**

Computers sign lots of important things: the updates your phone downloads, the certificate that proves a website is really your bank, and documents that must hold up in the future. If someone could forge those signatures, they could sneak bad software onto your phone or pretend to be your bank. Because a quantum computer might one day forge today's signatures, switching to ML-DSA now protects messages that need to stay trustworthy for many years.

**Q: What goes wrong if the signer skips the throwing-away step?**

The throwing-away step (keeping only answers that stay inside the safe lines) is what hides the secret. Each answer leans just a little toward the secret. One answer barely leaks anything, but if the signer kept every answer and handed out thousands of signatures, all those tiny leans would add up, and a patient attacker could slowly piece the secret together. By binning the risky answers and keeping only balanced ones, the signer makes sure the pile of signatures never points back to the secret.

**Q: Can you give me another example of hiding a secret this way?**

Think of a smoothie. You blend one secret fruit into a big cup with lots of other fruits. Anyone can taste the smoothie, but they cannot easily pick out and name your one secret fruit, because it is mixed with everything else. Yet if you know the recipe, you can prove the secret fruit is in there. ML-DSA hides its secret numbers in a similar way, by mixing them into a big pile of other numbers so nobody can pull a single one back out, while still letting a checker confirm you used the secret.

## References

- [FIPS 204: Module-Lattice-Based Digital Signature Standard (NIST, 2024)](https://doi.org/10.6028/NIST.FIPS.204)
- [ML-DSA, the Module-Lattice Digital Signature Standard (FIPS 204): the full technical version of this article]({{site.url_complet}}/cryptography/2026/06/29/ml-dsa-fips-204-post-quantum-signatures.html)
- [CRYSTALS-Dilithium, the design ML-DSA is based on](https://pq-crystals.org/dilithium/)
- [NIST Post-Quantum Cryptography project](https://csrc.nist.gov/projects/post-quantum-cryptography)
