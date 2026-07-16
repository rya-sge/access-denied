---
layout: post
title: "Money as a Jar of Coins — How Cardano Tracks Who Owns What, Explained for a 10-Year-Old"
date:   2026-07-16
lang: en
locale: en-GB
categories: blockchain
tags: cardano eutxo bitcoin blockchain analogy explainer
description: A simple guide to Cardano's eUTXO model, explained with a jar of real coins, sticky notes, and a referee. Shows how it works and how it is different from Bitcoin, for curious readers of all ages.
image: /assets/article/blockchain/cardano/eutxo-explained-eli10.png
isMath: false
---

Imagine you have some pocket money. There are two ways your family could keep track of it. One way is to write a number on the fridge, like "you have 50". The other way is to keep real coins in a jar that you can hold. Both tell you how much you have. But they work in very different ways once you start spending. Cardano, a kind of digital money, chose the jar of coins. Bitcoin did too, a long time before. This article explains how the coin jar works, and how Cardano made its coins a little bit smarter than Bitcoin's.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Two ways to keep your money

Think about a video game where you collect gold. In many games, your gold is just one number at the top of the screen. When you buy something, the number goes down. When you find treasure, the number goes up. There are no real coins anywhere. This is like a bank balance, which is one number on a list that says how much you own.

Now think about real life. You do not have one magic number. You have actual coins and bills in your pocket. Maybe a 30 coin, a 20 coin, and a 5 coin. To pay for something, you hand over some of those real coins. This is the way Cardano works. Each coin is real and separate, and you hold it until you spend it.

The fancy name for one of these coins is a UTXO (a coin you own that has not been spent yet). Cardano's whole system is called the eUTXO model, which just means "the coin way, with a few extra features." We will get to the extra features soon.

![Two ways to keep money: one number on a list, or a jar of real coins]({{site.url_complet}}/assets/article/blockchain/cardano/eutxo-eli10-coin-vs-balance-concept.png)

## How you spend a coin

Here is the important part. You cannot break a coin in half. If you have a 30 coin and you want to buy a 12 sticker, you cannot shave off exactly 12. You have to hand over the whole 30 coin. The shop then gives you change back.

So paying works just like using cash. You hand over one or more whole coins. The shop keeps what the toy costs. The shop gives you the leftover amount back as a brand-new coin. That new coin is your change.

Four simple rules come from this, and they are easy to remember:

1. You spend a coin whole. You cannot use just part of it.
2. What goes in must equal what comes out, plus a small fee for the helpers who run the system.
3. A coin never changes. It only gets created or used up. Nobody edits a coin.
4. A coin can be spent only once. Once you hand it over, it is gone from your pocket forever.

That last rule is a superpower for safety. Because a coin disappears the moment you use it, nobody can spend the same coin twice. It is like a movie ticket that the usher tears in half at the door. You cannot walk back in with the same torn ticket.

## What is inside Bitcoin's treasure chest

Let us look at Bitcoin first, because Cardano copied its good idea and then added more.

In Bitcoin, each coin sits inside a little treasure chest. The chest has two things: the coins inside, and a lock on the lid. To open the chest and spend the coins, you need the right key. The lock can be simple, like "only the person with this key may open it." It can also ask for a few keys at once, like a club treasure box that needs three friends to agree.

But there is a catch. The guard at a Bitcoin chest is not allowed to look at much. It checks the key you hand over, and that is almost all it sees. It cannot read any notes. It cannot look at the rest of your shopping list. It just checks the lock and says yes or no.

## What Cardano puts inside the chest

Cardano kept the treasure chest, then added three helpful things. Think of them as upgrades to the chest.

The first upgrade is a **sticky note** on the chest. Grown-ups call it a datum (a little note of extra facts that travels with the coins). The note can say something like "these coins belong to Alice" or "do not open until her birthday."

The second upgrade is a **note you write and hand over** when you want to open the chest. Grown-ups call it a redeemer (the message you give to say what you are trying to do). It is like handing the guard a slip that says "I would like to take my birthday money now."

The third upgrade is the biggest. The Cardano guard is allowed to read the **whole shopping receipt**. Grown-ups call it the script context (the full list of everything the payment does). The guard can see every chest being opened, every new coin being made, who signed the payment, and even what time window it is allowed in.

## The guard is a referee, not a player

Here is an idea that surprises grown-ups too. The guard on a Cardano chest never does anything on its own. It cannot grab coins. It cannot send money. It cannot start a payment. It is a referee, not a player.

All the guard does is look at the payment you propose and say one word: yes or no. You bring a full plan for the payment. The guard checks your plan against the rules on the sticky note. If everything follows the rules, the guard says yes and the payment happens. If anything breaks a rule, the guard says no and nothing happens at all.

This is why the guard reading the whole receipt matters so much. Because it can see the whole plan, it can enforce clever rules. For example: "you may take these coins only if you also send 100 to your sister," or "you may open this chest only after the school year ends."

![What the Bitcoin guard can see versus what the Cardano guard can see]({{site.url_complet}}/assets/article/blockchain/cardano/eutxo-eli10-guard-view-concept.png)

Bitcoin's guard checks a lock. Cardano's guard reads the whole receipt. That one difference is what lets Cardano build much smarter rules, while still keeping the simple, safe coin jar underneath.

## Why it is nice to know the answer early

Cardano's coins have one more happy result. Because your payment names the exact coins it will use, you can check if it will work before you even send it. You know the answer early.

Imagine a vending machine that could tell you "yes, this will work" before you put your money in. You would never waste a coin on a jammed machine. Cardano is like that. If the coins you picked are still in your jar, your payment goes through exactly as planned. If someone already used one of them, your payment simply does not happen, and you lose nothing.

There is a nice bonus too. A Cardano chest can hold more than plain money. It can carry other kinds of tokens in the same chest, like arcade tokens or collectible stickers, right next to your coins. You do not need a separate special box for them.

## Putting it all together

Let us follow one story from start to finish.

Grandma wants to give you birthday money, but not until your actual birthday. So she puts 1000 coins in a Cardano chest. On the sticky note she writes two facts: "this belongs to you," and "do not open until your birthday."

Your birthday comes. You build a payment. You pick the chest as the thing you want to open. You write a little note that says "I am taking my birthday money." You also make sure the payment says "today is on or after the birthday," and that the money goes to you.

Now the guard looks at your whole plan. It checks the sticky note. Is today on or after the birthday? Yes. Does the money go to the right person? Yes. Did you sign it? Yes. So the guard says yes. The old chest is used up, and a new coin worth 1000 lands in your jar. If you had tried this one day early, the guard would have said no, and nothing would have moved.

That is the whole idea. Real coins in a jar, a sticky note with rules, a slip you hand over, and a referee who reads the full plan and only says yes or no.

## Summary

Cardano keeps money as a jar of real, separate coins, not as one number on a list. You spend coins whole and get change back, just like cash, and each coin can be used only once, which stops cheating. Bitcoin uses the same coin jar, but its guard can only check a lock. Cardano gives each chest a sticky note of rules, lets you hand the guard a slip saying what you want, and lets the guard read the whole payment before saying yes or no. That extra sight is what makes Cardano's coins smart, while the simple coin jar keeps everything safe and easy to check.

![Mindmap of Cardano's coin model: two ways to keep money, how a coin is spent, Bitcoin's chest, what Cardano adds, the referee guard, and why it is nice]({{site.url_complet}}/assets/article/blockchain/cardano/eutxo-explained-eli10.png)

## Frequently Asked Questions

**Q: Why bother with real coins? Isn't one number on the fridge simpler?**

One number does feel simpler at first. But it has a hidden problem. When everyone shares one big list of numbers, two payments can bump into each other and change the same number at the same time, and it gets confusing about which one really happened. Real coins avoid this. Your coin is yours alone, sitting in your jar, and only you can hand it over. It is easier to be sure who owns what when you can point to a real coin instead of trusting a number that many people are editing at once.

**Q: What if two people try to spend the very same coin at the same time?**

Only one of them can win. A coin can be spent just once, like a movie ticket that gets torn at the door. If two payments both try to use the same coin, the first one to go through tears the ticket. The second payment then points at a coin that no longer exists, so it simply does not happen. Nobody loses money by accident. The loser just tries again with a different coin.

**Q: How does this help in real life?**

It makes digital money safe and predictable. Because each coin is used only once, nobody can copy money or spend it twice. Because your payment names the exact coins it uses, you can check that it will work before you send it, so you never waste a fee on a payment that was going to fail. And because a chest can hold other tokens too, the same safe system can carry game items or collectibles, not just money.

**Q: What goes wrong if the guard could not read the whole receipt?**

Then the rules would have to be very simple, like Bitcoin's lock. You could say "only the person with this key may open the chest." But you could not say "open this only after her birthday," or "open this only if the money also goes to her sister." Those clever rules need the guard to see the whole plan. Take away the guard's wide view, and you take away most of the smart things Cardano can do.

**Q: Can you give me another example of spending a coin and getting change?**

Sure. Imagine you have a 20 coin and you buy a book that costs 14. You cannot cut the coin, so you hand over the whole 20. The shop keeps 14 for the book and 1 for the helper fee, then hands you back a new 5 coin as change. Your old 20 coin is gone for good. In its place you now hold one fresh 5 coin. Count it up: 20 went in, and 19 plus a 1 fee came out. It always balances, exactly like paying with cash at a real shop.

## References

- [Cardano developer portal](https://developers.cardano.org/)
- [The Extended UTXO Model (Chakravarty and others, IOHK)](https://iohk.io/en/research/library/papers/the-extended-utxo-model/)
- [Bitcoin developer guide, transactions](https://developer.bitcoin.org/devguide/transactions.html)
- [Claude Code](https://claude.com/product/claude-code)
