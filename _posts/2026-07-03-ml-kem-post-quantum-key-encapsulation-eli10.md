---
layout: post
title: "How Two Computers Agree on a Secret Code That a Quantum Computer Cannot Steal — Explained for a 10-Year-Old"
date:   2026-07-03
lang: en
locale: en-GB
categories: cryptography
tags: cryptography post-quantum lattice ml-kem key-encapsulation analogy explainer
description: A simple guide to ML-KEM, the new way two computers share a secret code that quantum computers cannot steal, explained with padlocks, locked boxes, and a clever double-check.
image: /assets/article/cryptographie/lattice/2026-07-03-ml-kem-post-quantum-key-encapsulation-eli10-mindmap.png
isMath: false
---

Imagine you and your best friend want to agree on a secret password. The trouble is, you have to shout across a crowded playground, and everyone can hear you. If you just yell the password, everyone learns it. So how can two people end up sharing a secret when every word they say is out in the open? Computers face this exact problem millions of times a second. They solved it with a clever trick, but a new kind of super-fast computer is about to break the old trick. This article explains the new solution, called ML-KEM.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and the custom skill `create-article-eli10`

[TOC]

## Why Is Today's Secret Handshake in Danger?

Think of a nosy neighbour with a tape recorder. Right now you and your friend use a secret handshake to agree on a password, and the neighbour cannot follow it. But the neighbour records every handshake on tape and keeps the tapes in a drawer. He is betting that one day he will own a machine that can figure out the handshake. When that day comes, he pulls out the old tapes and learns every password you ever used.

Computers have the same worry. Today, two computers agree on a secret using a math trick (its common names are Diffie-Hellman and RSA). The trick is safe because cracking it needs a giant number puzzle solved, and normal computers are far too slow. But scientists are building a new machine called a quantum computer, and it can solve that exact puzzle quickly. Worse, a spy can record scrambled messages today and simply wait. Once the spy has a quantum computer, he can unscramble all those saved messages. This waiting game even has a nickname: "harvest now, decrypt later" (grab the locked messages now, unlock them later).

That is why we cannot wait for quantum computers to actually arrive. Anything secret we send today needs a lock that the future machine still cannot pick. ML-KEM (its full name is the Module-Lattice-Based Key-Encapsulation Mechanism) is that new lock. A group of experts at a place called NIST tested many ideas for years and chose it as the standard in 2024.

## How Do You Share a Secret Using a Padlock?

Picture an open padlock, the kind that snaps shut with a click and needs a key to open again. Alice wants to receive a secret from Bob. So Alice makes lots of these padlocks, leaves them hanging open, and hands them out to anyone who asks. She keeps only one thing to herself: the little key that opens them. Bob takes one open padlock, writes a secret number on a card, drops the card in a box, and snaps Alice's padlock shut on it. He mails the locked box back to Alice. Only Alice has the key, so only Alice can open the box and read the number. Now both Bob and Alice know the number, and nobody in between could peek inside.

That padlock-and-box idea is exactly what ML-KEM does, and it comes in three simple steps.

1. **Make the padlocks.** Alice creates a public padlock (called the encapsulation key) that anyone can use, and a private key (called the decapsulation key) that only she keeps.
2. **Lock a secret inside.** Bob rolls a random secret number, uses Alice's padlock to seal it into a locked box (called the ciphertext), and keeps his own copy of the number.
3. **Unlock it.** Alice opens the box with her private key and reads the same number.

Both sides then run the number through the same recipe to turn it into the final shared key. In the real system, a clever extra step scrambles the number before it travels, but the effect is the same: a random secret ends up shared by both people, and only Alice could ever open the box.

![Two computers agreeing on a shared secret with a padlock and a locked box]({{site.url_complet}}/assets/article/cryptographie/lattice/ml-kem-eli10-locked-box-handoff.png)

## How Is the Padlock Built So a Robot Cannot Pick It?

Here is the puzzle that makes the padlock so hard to open. Imagine a huge multiplication done in front of everyone, but with a little dust sprinkled on the answer. You pick a small secret number, multiply it by a big number that everyone can see, and then sprinkle a bit of "fuzz" so the answer is slightly off. You show people the big number and the dusty answer, but never your secret. Because of the fuzz, nobody can simply divide to get your secret back.

The open padlock Alice hands out is really one of these dusty answers. Her private key is the small secret numbers hidden inside it. To build the lock (going forward) is easy. To pick the lock (working backward from the padlock to the secret) means cleaning off all the fuzz, and nobody knows how to do that quickly, not even a quantum computer.

Here is a tiny worked example with small numbers:

- Secret number: **5**
- Public multiplier everyone can see: **10**
- Tiny fuzz: **2**
- Public answer: 5 times 10, plus 2, equals **52**

If there were no fuzz, you could do 50 divided by 10 and instantly find the secret 5. The fuzz turns a clean 50 into a messy 52, so simple division stops working. The real ML-KEM does not use one number but hundreds of them, all multiplied by a giant grid and all fuzzed together at once. Untangling that many fuzzy sums at the same time is the puzzle that keeps every known computer stuck.

![How the padlock is built from a fuzzy multiplication that only goes one way]({{site.url_complet}}/assets/article/cryptographie/lattice/ml-kem-eli10-fuzzy-padlock-concept.png)

## Why Does Bob Lock a Dice Roll Instead of a Real Message?

Think about a spelling test where the teacher must pick words that nobody can plan for. If the teacher let students choose their own test words, a sneaky student could pick easy words on purpose and learn how the grading works. Picking the words at random takes that trick away.

ML-KEM does the same thing on purpose. Bob never locks a message he chose. He locks a fresh random number, like a dice roll. This might seem odd, because you would think the whole point is to send real information. But the job here is only to agree on a shared secret, and a random number does that perfectly. The reason for the dice roll is safety. If Bob could stuff a chosen message into the box, a clever attacker could craft trick messages, feed them to Alice's lock, and slowly learn how it works. By only ever locking a random number, there is nothing to craft and nothing to learn. The lock stays a mystery.

## What Is the Double-Check That Catches Cheaters?

Imagine Alice has a magic rule: any given secret number can only ever be packed into a box in one exact way. So when Alice opens a box and reads the number, she can re-pack a brand-new box herself, using that same number and the same steps, and the two boxes should look identical. If her fresh box matches the one Bob sent, she knows Bob packed it honestly. If they do not match, someone tampered with the box along the way.

ML-KEM does exactly this. After Alice unlocks the box and reads the number, she re-locks a fresh box the same way and compares it to the one she received. A match means the message is genuine. A mismatch means trouble. And here is the clever part: when there is a mismatch, Alice does not shout "this is fake!" Instead she quietly hands back a made-up key that looks completely normal. She builds this fake key from a secret ingredient only she knows, mixed with the box itself, so it always looks like a real shared key.

Why stay silent? Because a cheater's whole plan is to send box after box and watch how Alice reacts. If Alice ever shouted "fake", the cheater would learn something from each shout and slowly figure out her key. By never reacting differently, Alice gives the cheater nothing to go on. This silent trick is what makes ML-KEM safe even against an attacker who gets to send it thousands of tampered boxes.

![Alice's double-check: re-lock the box, compare, and hand back a fake key if it does not match]({{site.url_complet}}/assets/article/cryptographie/lattice/ml-kem-eli10-double-check.png)

## Why Are There Three Different Sizes?

Bike locks come in different strengths. A thin cable lock is light and easy to carry but easier to cut. A thick chain lock is heavy but very hard to break. You pick the one that matches how worried you are.

ML-KEM comes in three strengths too, with the names ML-KEM-512, ML-KEM-768, and ML-KEM-1024. The bigger the number, the more secret numbers packed inside, and the harder the puzzle is to crack. But bigger also means the padlocks and boxes take more room. Here is a rough idea:

| Strength | Padlock and box size | How safe |
|----------|----------------------|----------|
| ML-KEM-512 | about 800 bytes each | strong |
| ML-KEM-768 | about 1,100 bytes each | stronger (the recommended default) |
| ML-KEM-1024 | about 1,500 bytes each | strongest |

To picture how much bigger this is than the older method: an older key-sharing value called X25519 is only about 32 bytes, smaller than this sentence. ML-KEM padlocks and boxes are dozens of times larger. That extra bulk is the price we pay for a lock a quantum computer cannot pick. The shared secret both sides end up with is always the same small size, just enough to lock up the rest of the conversation.

## Does the Padlock Also Prove Who Sent It?

Here is one thing the padlock does not do. It keeps the secret safe, but it does not prove who left the open padlock hanging out. A trickster in the middle could take down Alice's padlock, hang up his own that looks just like it, and fool Bob into locking the secret with the wrong padlock. Now the trickster can open the box, not Alice. This sneaky move is called a man-in-the-middle.

To stop it, ML-KEM is used together with a signature, which is a separate tool that proves who someone really is (think of a wax seal that only Alice can stamp). ML-KEM keeps the secret hidden, and the signature proves who you are talking to. They are two different jobs. On top of that, people often use ML-KEM alongside an older lock at the same time, as a backup. If one lock ever turned out to be pickable, the other would still hold. Using two locks at once costs almost nothing and buys peace of mind.

## Putting It All Together

Let us follow one secret from start to finish, using all the ideas above.

1. **Making the padlocks.** Alice builds a padlock out of a fuzzy multiplication and hands out open copies. The little secret numbers that open it stay hidden with her.
2. **Locking a secret.** Bob rolls a random number, seals it into a box using Alice's padlock, and keeps his own copy of the number.
3. **Unlocking.** Alice opens the box with her private key and reads the same number.
4. **The double-check.** Alice re-locks a fresh box the same way. If it matches Bob's box, she trusts it and both sides turn the number into the same shared key. If it does not match, she quietly hands back a fake key so a cheater learns nothing.
5. **Adding a name and a backup.** A signature proves the padlock really came from Alice, and an older lock runs alongside as a safety net.

Every step keeps the secret hidden from anyone listening, and every step leans on the fuzzy puzzle that quantum computers cannot solve. That is how two computers agree on a secret code over a channel where everyone can listen.

## Summary

ML-KEM is a new way for two computers to agree on a shared secret over a public channel, even though a future quantum computer could break the old way. Alice hands out a padlock built from a fuzzy multiplication that only she can undo. Bob locks a random secret number in a box and sends it, and Alice opens it with her private key. To catch cheaters, Alice re-locks the box herself and compares, and if it does not match she quietly returns a harmless fake key instead of an error. The lock comes in three sizes, keeps secrets but does not prove who you are talking to, and so it teams up with a signature and often an older lock as backup. The price for this quantum-proof safety is that the padlocks and boxes are bigger than the ones we use today, but for keeping secrets safe for years to come, that is a fair trade.

![ML-KEM explained for a 10-year-old mindmap]({{site.url_complet}}/assets/article/cryptographie/lattice/2026-07-03-ml-kem-post-quantum-key-encapsulation-eli10-mindmap.png)

## Frequently Asked Questions

**Q: But why does Bob lock up a random number instead of just sending the secret he wants?**

Because the only job here is for both sides to end up holding the same secret, and a random number does that just as well as a chosen one. Choosing the contents would actually make things less safe. If Bob could pack a message he picked, a clever attacker could craft special trick messages, feed them to the lock, and learn how it works from the results. A random number gives an attacker nothing to craft. Once both sides share the number, they use it as the key to lock up the rest of their conversation.

**Q: What if someone changes the box while it is on its way to Alice?**

Alice catches it with her double-check. Because any given number can only be packed into a box one exact way, Alice re-packs a fresh box from the number she read and compares it to the one she got. A tampered box will not match. When that happens, Alice does not announce the problem. She quietly hands back a fake key that looks real but is useless, so the attacker cannot tell that anything went wrong and learns nothing.

**Q: How does this help in real life?**

Almost every time you visit a website that starts with a little padlock icon, your computer and the website first agree on a secret key, then use it to scramble everything you send. That secret-sharing step is exactly what ML-KEM protects. Without it, a spy who records your traffic today could unlock it years from now with a quantum computer, exposing your passwords, messages, and payments. Switching to ML-KEM now keeps those secrets safe even against a machine that does not exist yet.

**Q: What goes wrong if Alice skips the silent double-check?**

Then ML-KEM would only be safe against someone who just quietly listens, not against someone who actively sends fake boxes. An attacker could send box after box, each changed a little, and watch whether Alice's answer works or fails. Every success or failure would leak a tiny clue about her private key, and after enough tries the attacker could piece the key together. The double-check, plus the silent fake key on a mismatch, is what removes those clues and keeps the lock safe against an active cheater.

**Q: Can you give me another example of sharing a secret without saying it out loud?**

Think of a mailbox with a slot on top. Alice owns the mailbox and keeps the only key. Anyone can walk up and drop a letter through the slot, but only Alice can open the box and take letters out. If Bob drops a card with a random number through the slot, only Alice can read it, even though the mailbox stood in public the whole time. ML-KEM works like a mailbox that a quantum computer still cannot break into, so the number Bob drops in stays a secret between the two of them.

## References

- [FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard (NIST, 2024)](https://doi.org/10.6028/NIST.FIPS.203)
- [ML-KEM, the Module-Lattice Key-Encapsulation Standard (FIPS 203): the full technical version of this article]({{site.url_complet}}/cryptography/2026/06/29/ml-kem-fips-203-post-quantum-key-encapsulation.html)
- [CRYSTALS-Kyber, the design ML-KEM is based on](https://pq-crystals.org/kyber/)
- [NIST Post-Quantum Cryptography project](https://csrc.nist.gov/projects/post-quantum-cryptography)
