---
layout: post
title: "Betting Stickers at the School Fair — How Prediction Market Tokens Work, Explained for a 10-Year-Old"
date:   2026-07-28
lang: en
locale: en-GB
categories: blockchain defi eli10
tags: blockchain prediction-market conditional-tokens gnosis analogy explainer eli10
description: A simple guide to conditional tokens, the stickers that turn into money once a question is answered. Explained with a school fair prize shop, a locked money box, and a clever way of naming things.
image: /assets/article/blockchain/defi/conditional-tokens/2026-07-28-conditional-tokens-eli10.png
isMath: false
---

There is a running race at the school fair tomorrow. Alice, Bob and Carol are competing. You are sure Alice will win, and your friend is sure Bob will win. You would both like to put a coin on it. But who holds the money until the race is over, and how do you make sure the loser actually pays up? This article is about a machine that solves that problem, and about one very sneaky trick someone found to break it.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What is the Prize Shop?

Picture a small stall at the fair called the Prize Shop. It has a locked money box and a sticker printer. It does not care who wins. It only follows rules.

Before anything else, somebody sets up a question. A question needs two things. First, a list of every possible answer. For our race that list is Alice, Bob, Carol. Second, a **judge**: one particular person who promises to announce the answer afterwards. Everybody agrees on the judge in advance, and the shop writes their name down. Nobody else is allowed to announce the answer later.

That is the whole setup. A list of answers, and one judge.

> **The grown-up name.** The Prize Shop is a **smart contract**, a program living on a blockchain that anybody can use and nobody can quietly change. The question is a **condition**, each possible answer is an **outcome slot**, and the judge is an **oracle** (the one account allowed to report what happened in the real world). Setting the question up is a function call named `prepareCondition`.

## How does the shop swap your coin for stickers?

Here is the strange part. If you walk up and hand over one coin, the shop does not give you a sticker that says "Alice wins". It gives you **three** stickers: one saying "Alice wins", one saying "Bob wins", one saying "Carol wins". You get the whole set.

![One coin goes in, and one sticker comes out for every possible answer]({{site.url_complet}}/assets/article/blockchain/defi/conditional-tokens/conditional-tokens-eli10-split-stickers-concept.png)

Why the whole set? Because of a neat piece of arithmetic. Exactly one of those three stickers is going to be the winner. So the three of them together are always worth exactly one coin, no matter what happens in the race. The shop locks your coin in the money box, and it now holds exactly enough money to pay out whichever sticker wins.

This is the rule that keeps the shop honest. It can never owe more money than it is holding.

> **The grown-up name.** The stickers are **conditional tokens**, and the shop keeps track of them using a standard called **ERC-1155**, which lets one contract look after many different kinds of token at once. Each sticker design is a **position**, and its serial number is literally the token's identity number. Swapping a coin for a full set is called **splitting a position** (`splitPosition`), and handing a full set back for a coin is **merging** (`mergePositions`).

Of course, you did not want all three stickers. You wanted the Alice one. So you find your friend, who thinks Bob will win, and you sell them the "Bob wins" sticker. Somebody else buys the Carol one. Now you are holding only the sticker you believe in, and you have some of your coin back. The price your friend pays you is really their guess about Bob's chances. That is where the betting actually happens: not at the shop, but between people trading stickers.

## Can you change your mind before the race?

Yes, and this is important. Suppose you get nervous and want your coin back.

You collect all three stickers again (buy back the ones you sold) and hand the complete set to the shop. The shop unlocks the box and gives you your coin. Then it tears up the three stickers.

The shop is happy to do this at any time, even before the race, because a complete set is worth exactly one coin. Handing over a full set and taking a coin out is the exact opposite of handing in a coin and taking a full set. The money box balances either way.

## What happens when the judge speaks?

After the race, the judge announces the result. Let us say Bob won.

The judge tells the shop: Alice gets nothing, Bob gets everything, Carol gets nothing. The shop writes this down once and never lets it be changed. Not by the judge, not by anybody. One announcement, and it is locked in for good.

Now the stickers stop being guesses and become facts:

- A "Bob wins" sticker can be handed in for one coin from the box.
- An "Alice wins" sticker is now worth nothing. So is a "Carol wins" sticker.

> **The grown-up name.** The judge's announcement is a call to `reportPayouts`, and what they submit is a **payout vector**, one number per answer. Handing a sticker in for money is **redeeming a position** (`redeemPositions`). "Written down once and never changed" is enforced by a single check in the code, which refuses a second announcement for the same question.

There is a slightly cleverer version of this for questions that are not simple win-or-lose. Imagine the question was "how many goals will be scored, somewhere between 0 and 10?" The shop sets up two answers, "low" and "high". If the real result is 9 goals, the judge does not pick just one. The judge says the high sticker is worth nine tenths of a coin and the low sticker is worth one tenth. The two amounts still add up to exactly one coin, so the money box still balances. The idea is the same, only the split is fractional.

## What if you care about two things at once?

Now it gets interesting. Suppose there is a second question at the fair: will it rain during the race, yes or no?

You do not just think Alice will win. You think Alice will win **and** it will rain, because Alice is brilliant in the mud. You want one sticker that pays out only if both of those things happen.

You can build it. Start with your "Alice wins" sticker and take it back to the shop. The shop swaps it for two new stickers: "Alice wins AND it rains", and "Alice wins AND it stays dry". Notice you did not pay another coin. You handed in one sticker and got two more detailed ones back. Together the two new ones are worth exactly what the old one was worth, so the money box does not change at all.

But there is a second way to build the same thing. You could have started from the weather question instead. Swap your coin for a "rain" sticker and a "dry" sticker. Keep the rain one. Then take the rain sticker back and swap it for "Alice AND rain", "Bob AND rain", "Carol AND rain". Keep the first.

![Two different routes that end on the very same sticker]({{site.url_complet}}/assets/article/blockchain/defi/conditional-tokens/conditional-tokens-eli10-two-routes-workflow.png)

Both routes end with a sticker meaning exactly the same thing. So they had better be the same sticker. If the shop treated them as two different kinds of sticker, that would be a real problem. You could not sell yours to somebody who built theirs the other way round, even though you both want exactly the same deal. Half the people at the fair would end up holding one version and half the other, and nobody could trade with anybody.

Making sure both routes land on the same sticker turns out to be the hardest part of the whole design.

## Why does every sticker need a serial number?

The shop is not really a person with a printer. It is a computer program, and a computer cannot read the words "Alice wins AND it rains" off a sticker. It needs a number.

So every sticker gets a **serial number**, worked out from what the sticker means. The program only ever looks at serial numbers. Two stickers with the same serial number are the same sticker, full stop.

That gives us two rules the numbering scheme must obey, and they pull against each other:

- **Rule one.** Combining "Alice wins" with "it rains" must give the same serial number as combining "it rains" with "Alice wins". Order must not matter, or the two routes from the last section produce two different stickers.
- **Rule two.** Nobody must be able to invent a fake sticker that happens to land on a serial number that already belongs to a real, valuable sticker. If they could, they would be printing money.

Rule one wants the combining step to be simple and predictable. Rule two wants it to be impossible to work backwards. Finding something that does both is the tricky bit.

## Why did the first idea fail?

The first version of the shop used the obvious answer: **addition**.

Give each simple label its own huge scrambled number. "Alice wins" gets one. "It rains" gets another. To combine two labels, add their numbers together.

This passes rule one straight away. Adding two numbers gives the same result whichever one you write first. Five plus three and three plus five are both eight. So both routes really do land on the same total.

It fails rule two, though, and the way it fails is worth understanding. A cheater does not have to guess a fake sticker and hope. They can go hunting. They pick the serial number they want to land on, then search through enormous piles of possible labels looking for a handful whose numbers happen to add up to exactly that target. Mathematicians worked out how to do this search efficiently a long time ago, and it is far, far faster than trying every combination one at a time.

Once a cheater finds such a set, they can walk into the shop holding a sticker the shop has never issued, and the shop's own arithmetic will agree that it is real.

> **The grown-up name.** Naming things by adding up scrambled numbers is called **AdHash**. The clever search that breaks it is **Wagner's generalized birthday attack**, and the kind of puzzle it solves is a **subset-sum** problem (find a few numbers from a big pile that add up to a target). In the real system the numbers are not simply added, they are added and then wrapped around to a fixed size, the way a clock wraps from 12 back to 1. That wrapping is part of what makes the search work.

## How do spots on a curved line fix it?

Here is the clever bit. Instead of giving each label a plain number, the shop gives each label a **spot on a special curved line**.

Draw a curve on a very large sheet of graph paper. Only certain points sit exactly on the curve; the rest of the paper is empty. Each label gets one of the points that does.

There is a rule for adding two spots. You take spot A and spot B, follow the rule, and you land on a third spot, which is also on the curve. It is not ordinary addition, but it behaves like it in the way that counts: **A plus B always lands in the same place as B plus A**. Rule one is satisfied.

And rule two? Working the sum forwards is easy. Working it backwards is not. If somebody hands you a spot and asks "which labels add up to this one?", nobody knows a good way to answer. People have been trying to crack that puzzle for decades, and it is one of the puzzles that a lot of internet security already relies on. It is not proven to be unbreakable, but nobody has broken it.

> **The grown-up name.** That backwards puzzle is called the **discrete logarithm problem**. On a curved line like this one it is the **elliptic curve discrete logarithm problem**, or **ECDLP**. It is the same hard problem behind the padlock icon in your browser and behind the signatures on most cryptocurrency payments. The naming scheme built on top of it has a name too: an **Elliptic Curve Multiset Hash**, which means "turn every item in a set into a curve point, then add the points up". The researchers who published it proved something reassuring. Anyone who could find two different piles of labels landing on the same total could also solve the discrete logarithm problem. So you cannot break the naming scheme without first breaking a puzzle the whole internet is already betting on. The curve the shop actually uses is called **alt_bn128**, and Ethereum has a built-in shortcut for adding spots on it, which is why the adding step is cheap.

That is the swap. The shop gave up plain addition, which was easy to run backwards, for curve addition, which is not.

### How does a label become a spot?

You might wonder how the shop turns the words "Alice wins" into a spot in the first place. It uses a little bit of trial and error.

![Turning a label into a spot on the curve]({{site.url_complet}}/assets/article/blockchain/defi/conditional-tokens/conditional-tokens-eli10-name-from-label-workflow.png)

First it runs the label through a **scrambler** (a machine that turns any text into one huge, messy-looking number). The scrambler is reliable: the same words always give the same number. But you cannot look at the number and work out what words went in.

Then it checks whether there is a spot on the curve at that number. Often there is not, because plenty of positions on the graph paper are empty. So it adds one and checks again. And again. About half of all positions have a spot, so it usually finds one after a try or two.

The shop also checks any serial number a customer hands over. It tests whether that number really is a spot on the curve, and refuses it if not.

That check on its own is not what keeps cheaters out, and it is worth being clear about why. A number picked at random lands on the curve about half the time, so passing the test proves very little. The check is there to make sure the shop only ever adds real spots together, because the adding rule only behaves properly on real spots.

What actually keeps cheaters out is simpler. You cannot ask the shop for a sticker out of nowhere. You can only get one by handing in a sticker you already own, and that chain runs all the way back to somebody putting a real coin in the box. So every serial number the shop will ever pay out on was built up from real spots, one honest step at a time. To cheat, you would have to find some completely different pile of labels whose spots add up to one of those numbers. That is the backwards puzzle nobody knows how to solve.

## What went wrong at the swap counter?

There is a second mistake in the story, and it has nothing to do with numbers. It is about the order in which the clerk does things.

In the old version of the shop, when you asked to swap a sticker for two more detailed ones, the clerk handed you the two new stickers **first**, and asked for your old one afterwards. For a brief moment, you were holding all three.

![The gap where the customer holds the old sticker and the new ones at the same time]({{site.url_complet}}/assets/article/blockchain/defi/conditional-tokens/conditional-tokens-eli10-swap-counter-workflow.png)

A normal customer would never notice. A sneaky one did.

During that gap they ran over to the cash-in counter. They spent the new stickers there. One of the payouts handed them a replacement for the old sticker the clerk was about to ask for. The other payout was real money out of the box. Then they strolled back, gave the clerk the replacement, and the clerk saw nothing unusual.

Notice that this trick only pays off if the cheater can also fake a serial number, which is the earlier weakness. The two problems worked as a team. Fixing either one would have blocked this particular trick, and the shop fixed both, because the fake serial number problem is dangerous by itself as well.

The fix is boring and completely effective. **Take the old sticker first. Print the new ones afterwards.** Now there is no moment where a customer holds both, so there is nothing to exploit during the gap. Real shops of this kind put the same rule everywhere: always collect before you hand out.

> **The grown-up name.** Sneaking back into a program before it has finished its previous job is called **reentrancy**, and it is one of the most famous bug families in blockchain programming. The moment the clerk hands over new stickers is a **callback** (the ERC-1155 standard makes the shop notify the receiver, which is what gives the customer a chance to act). The rule that fixes it is **checks-effects-interactions**: check everything first, update your own books second, and only talk to the outside world last. A real security review found this exact bug in these contracts and rated it critical.

## Putting it all together

Let us follow one coin from start to finish.

1. Somebody sets up the question "who wins the race?" with three answers, and names a judge. The shop writes the judge's name down and will never accept an answer from anyone else.
2. You hand the shop one coin. It locks the coin in the money box and prints you three stickers, one per runner.
3. You sell the Bob and Carol stickers to friends who believe in them. You keep the Alice one.
4. You decide you also want to bet on rain. You hand your Alice sticker back. The shop takes it (first!) and then prints "Alice AND rain" and "Alice AND dry". No coin changes hands.
5. The shop works out the serial number for each new sticker by turning each label into a spot on the curve and adding the spots together. Because adding spots does not care about order, your sticker gets exactly the same serial number as one built by starting from the weather question.
6. You sell the "Alice AND dry" sticker to somebody who thinks it will stay dry.
7. Race day comes. Alice wins, and it rains. The judge announces both results, once each, and they are locked in forever.
8. You hand in your "Alice AND rain" sticker. Both of its conditions came true, so the shop opens the box and pays you a full coin.

At no point did the shop hold less money than it owed. Every coin in the box got there because somebody paid it in, and every coin that left did so against a sticker the judge had confirmed.

## Summary

Conditional tokens are stickers that turn into money once a question is answered. You buy a full set with one coin, sell off the answers you do not believe in, and keep the one you do. Because a full set is always worth exactly one coin, the shop can always pay out. The hard part is not the betting; it is giving every sticker a serial number in a way that ignores the order you built it in, while still stopping anyone from inventing a fake number. Plain addition handles the first job and fails the second, so the real system adds up spots on a curved line instead. Add in one rule about doing things in the right order at the counter, and the whole machine holds together.

![Mindmap of the Prize Shop and how betting stickers work]({{site.url_complet}}/assets/article/blockchain/defi/conditional-tokens/2026-07-28-conditional-tokens-eli10.png)

## Frequently Asked Questions

**Q: But why does the shop give me all three stickers? I only wanted the Alice one.**

Because that is the only way the shop can be certain it will not run out of money. If it sold you a lone "Alice wins" sticker for one coin, it would have one coin in the box, and it would owe you one coin if Alice wins and nothing otherwise. That sounds fine until you notice it also sold Alice stickers to twenty other people. Now it owes twenty-one coins and only holds twenty-one coins if every single one of those bets loses.

By always printing the complete set at once, the shop turns the problem into simple arithmetic. One coin in, one full set out. One full set in, one coin out. The winning sticker is paid for by the losing ones, and the shop never has to guess anybody's chances. Working out what an individual sticker is worth is left to the people trading them, which is exactly where that job belongs.

**Q: What if the judge lies about who won?**

Then everybody who backed the real winner loses their money, and the shop cannot help them. This is a genuine weakness, and it is worth being honest about it.

The shop only checks one thing: that the announcement came from the exact person named when the question was set up. It has no way of knowing who actually crossed the line first. If you name your dishonest cousin as the judge, the shop will faithfully do whatever your cousin says.

Real systems handle this by being fussy about who gets to judge. Some use a large group instead of one person, so several would have to lie together. Some let anybody challenge a result and force a second look, with the challenger losing a deposit if they were wrong. None of that lives inside the shop itself. The shop is deliberately dumb, and choosing a trustworthy judge is your problem.

**Q: What goes wrong if the clerk hands over the new stickers before taking the old one?**

You create a moment when the same value exists twice: once in the old sticker still in the customer's pocket, and once in the brand new stickers. For an honest customer that moment is harmless, because they just hand the old one over.

A dishonest customer treats it as an opportunity. They dash off and spend the new stickers somewhere else in the shop before the clerk has finished the swap. When they come back, the paperwork looks fine, but they have taken money out of the box that they never put in.

This is not a made-up worry. It is the mistake that a real security review found in the real version of these contracts, and it was serious enough to be marked as critical. The fix was one line of reordering. That is often how it goes: the bug is subtle, and the fix is embarrassingly small.

**Q: How does any of this help in real life? Is it just for betting on races?**

Betting is the easy example, but the useful part is the price. When lots of people trade "Alice wins" stickers, the price settles at roughly what the crowd collectively thinks Alice's chances are. If the sticker trades for 30 pence, the crowd is saying "about a 30 percent chance". Unlike a poll, everybody stating an opinion has money on the line, so guessing carelessly costs them.

That makes it a way of collecting a crowd's honest opinion about something that has not happened yet. People have used it for election results, for whether a project will ship on time, and for whether a disease outbreak will spread. The two-questions-at-once feature is the really interesting one, because it lets you ask things like "if this policy passes, will unemployment fall?" You compare the price of the combined sticker with the price of the plain one, and the difference tells you what the crowd thinks the policy actually does.

**Q: Can you give me another example of an order that does not matter, and one that does?**

Mixing paint is a good one where order does not matter. Blue then yellow, or yellow then blue, both give you green. Adding numbers is the same, and so is adding spots on the curve. Anything like this is a good fit for naming stickers, because you cannot tell afterwards which order somebody used, and that is exactly what you want.

Getting dressed is a good one where order does matter. Socks then shoes works. Shoes then socks does not. Baking is another: mixing the batter and then heating it gives you a cake, and heating the ingredients before mixing gives you a mess.

The old nested style of prediction market was accidentally like getting dressed. A sticker built race-first and a sticker built weather-first were two different objects even though they meant the same thing. The whole point of the new design is to make the ordering vanish, so the machine behaves like paint rather than like shoes.

**Q: What if two different stickers accidentally get the same serial number?**

That would be a disaster, because the shop would treat two unrelated bets as the same bet. Somebody could hand in a worthless sticker and the shop would pay them for a valuable one.

Two things prevent it. First, the serial numbers are astronomically large. There are so many possible numbers that two honest stickers colliding by chance is not something you would expect to see in the lifetime of the universe. Second, and more importantly, the shop worries about deliberate collisions rather than accidental ones. A cheater is not waiting for luck; they are actively searching for a clash. That is exactly the search that plain addition made easy and that adding spots on a curve makes hard.

So the protection is not really "the numbers are big". It is "the numbers are big **and** there is no shortcut for hunting through them".

## References

- [Gnosis Conditional Tokens documentation](https://docs.gnosis.io/conditionaltokens/)
- [gnosis/conditional-tokens-contracts on GitHub](https://github.com/gnosis/conditional-tokens-contracts)
- [Audit Report for the Gnosis Conditional Tokens](https://github.com/gnosis/conditional-tokens-contracts/blob/master/docs/audit/AuditReport-ConditionalTokens.md)
- [Elliptic Curve Multiset Hash, the paper behind the spots-on-a-curve idea](https://arxiv.org/abs/1601.06502)
- [A Generalized Birthday Problem, the paper describing the search that broke plain addition](https://link.springer.com/chapter/10.1007/3-540-45708-9_19)
- [The technical version of this article]({{site.url_complet}}/2026/07/28/gnosis-conditional-tokens-framework/)
- [Claude Code](https://claude.com/product/claude-code)
