---
layout: post
title: "The Black-Scholes Model for Curious Kids — Pricing a Ticket to Buy Later"
date: 2026-07-18
lang: en
locale: en-GB
categories: finance
tags: options black-scholes analogy eli10 finance
description: A simple guide to the Black-Scholes model - what an option is, why pricing it was a hard puzzle, and how two clever people solved it, explained with everyday analogies for curious readers.
image: /assets/article/finance/black-scholes-eli10.png
isMath: false
---

Imagine your favourite bike costs 100 coins today. You think it might get more expensive next month, but you are not sure. So you go to the shop and buy a special paper ticket. The ticket says: "You may buy this exact bike for 100 coins any time in the next month, if you want to." How much should that ticket cost? Not the bike. Just the ticket. That question puzzled clever people for a very long time, and this is the story of how two of them finally answered it.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What is this magic ticket?

Think about a coupon at a toy shop. A coupon does not force you to buy anything. It just gives you the *choice* to buy at a set price. If the toy gets cheaper, you throw the coupon away and buy the toy normally. If the toy gets much more expensive, your coupon is like treasure, because you still pay the old low price.

Grown-ups call this kind of ticket an **option** (a piece of paper that gives you the choice, but not the duty, to buy something later at a price fixed today). The fixed price written on the ticket has a name too. It is called the **strike price** (the price you are allowed to pay if you use the ticket). In our story the strike price is 100 coins.

Here is the nice part about a ticket like this. It can never hurt you. The worst that happens is the bike gets cheaper, you skip the ticket, and you only lose what you paid for the ticket. But if the bike shoots up to 200 coins, your ticket lets you pay 100 and instantly own something worth 200. Heads you win a lot, tails you lose only a little.

## Why was the price such a hard puzzle?

Suppose you and a friend both try to guess a fair price for the ticket. You are cheerful and think the bike price will probably jump up. Your friend is gloomy and thinks it will drop. You will guess a high ticket price. Your friend will guess a low one. Who is right?

For many years, every attempt to price the ticket had this exact problem. Each formula needed you to first guess how fast the bike price would climb. Different guesses gave different answers, and nobody could prove whose guess was correct. The puzzle was stuck. Smart people wrote down formulas that were *almost* right, but each one hid a secret number that no one knew how to fill in.

The breakthrough was to find a price that does not depend on anyone's guess about the future. That sounds impossible. How can you price a ticket about the future without guessing the future? The trick is beautiful, and it comes next.

## The balancing-backpack trick

Picture a see-saw in a playground. On one side you put a heavy rock. If that were all, the see-saw would crash down and you could get hurt. So on the other side you carefully add just enough weight to keep it level. Now, no matter how someone bounces it, it barely tips. You have made it safe by balancing one thing against another.

Two clever people, Fischer Black and Myron Scholes, did exactly this with money. On one side, they *owned* a bike. On the other side, they *sold* some tickets to other people. When the bike price wiggles up, owning the bike is good news, but the tickets you sold become more valuable and you owe more, which is bad news. The good news and the bad news are set up to almost perfectly cancel. When the price wiggles down, the same thing happens in reverse. Either way, your total barely changes.

Here is a small example with easy numbers. For every one bike you own, you sell two tickets.

- The bike price ticks up a little. Your bike is worth a bit more (you gain). The two tickets you sold are worth a bit more, so you owe a bit more (you lose). The gain and the loss are about the same size, so they wipe each other out.
- The bike price ticks down a little. Your bike is worth a bit less (you lose). The two tickets are worth a bit less, so you owe less (you gain). Again they cancel.

![The balancing trick, owning a bike against selling tickets]({{site.url_complet}}/assets/article/finance/black-scholes-balancing-concept.png)

This balanced mix has a wonderful property. Whichever way the price moves, you end up in almost the same place. You built something that is safe, like the level see-saw. In real markets it is not perfectly safe, because prices can jump suddenly, but if you keep the balance carefully the idea holds.

## Why a safe recipe must earn bank interest

Imagine you have a magic piggy bank that is completely safe. Money in it can never shrink. Now imagine a shop offered you a *different* completely safe way to grow money that paid more than the piggy bank. What would everyone do? Everyone would rush to the better one and pour money in until it was no longer such a bargain. Two things that are both perfectly safe cannot pay different amounts for long. People racing after the better deal always pull them back together.

The balanced bike-and-tickets mix from the last section is safe, like the piggy bank. So it must grow at exactly the same boring, steady rate as safe money in a bank. That single sentence is the key that unlocks everything. Once you say "this safe mix must grow at the bank rate," you can work backwards and figure out the only ticket price that makes the sentence true. If the ticket had any other price, the safe mix would grow faster or slower than the bank, and that is not allowed.

So the fair price of the ticket is not about guessing the future at all. It is the price that keeps the balanced mix growing at the plain old bank rate. The cheerful kid and the gloomy kid now agree, because neither one's guess matters any more.

## The one thing you still need to know

You do need one fact about the bike, but it is not where the price is heading. It is how *jumpy* the price is. Think of two bikes. One bike has a price that barely moves, like a calm pond. The other has a price that leaps around wildly, like popcorn in a hot pan.

Which ticket is worth more? The ticket on the wild, jumpy bike. Remember, a ticket is heads-you-win, tails-you-lose-only-a-little. A jumpy price has bigger heads. It might rocket up and hand you a big prize, and if it crashes you still just skip the ticket. More wildness means more chances for a big win, with the downside still capped. So a jumpy price makes the ticket more valuable.

Grown-ups call this jumpiness **volatility** (how much a price bounces around over time). It is the one ingredient in the recipe that you cannot simply read off a price tag. You have to measure how bouncy the price has been. Everything else, like today's bike price and how long the ticket lasts, you already know.

## You have to keep steering

There is a catch to the balancing trick, and it is worth stopping on because it is easy to miss. Remember how you owned one bike but sold two tickets? Here is a fair worry. If both ticket-holders come back and use their tickets, you must hand over two bikes, but you only own one. You would have to rush out and buy a second bike just to give it away. So how can one bike ever balance two tickets?

The answer is that "one bike for two tickets" is only the right mix for *right now*, while the bike sits near 100 coins and nobody yet knows whether the tickets will be used. At that moment each ticket is a coin-flip, so a single ticket only behaves like *half* a bike. Two half-bikes make one whole bike, and that is why one bike cancels two tickets today. Grown-ups even have a name for "how much of a real bike one ticket behaves like." They call it **delta** (a number saying how many bikes a single ticket currently acts like).

As the price moves, that number changes, and you change how many bikes you own to match it. The table shows the idea.

| What is happening | Each ticket behaves like | Bikes you should own (for two tickets) |
|-------------------|--------------------------|----------------------------------------|
| Bike near 100, very unsure | about half a bike | 1 bike |
| Bike climbing, tickets likely to be used | about three-quarters of a bike | about one and a half bikes |
| Bike high, tickets almost certainly used | almost a whole bike | 2 bikes |
| Bike low, tickets almost certainly skipped | almost nothing | 0 bikes |

So your worry actually points straight at the answer. If the price climbs and it starts to look like both tickets will be used, you slowly buy that second bike along the way, while it is still cheaper than it will be at the end. By the time the tickets are used you already own the two bikes you need, so you are never caught buying one at the last second. And if the price sinks so the tickets look worthless, you do the opposite and sell your bike back down, because you will not have to hand anything over.

It is like riding a bike in a straight line. You do not set the handlebars once and freeze. You make tiny steering corrections all the time to stay on course. Black and Scholes imagined doing the same with the money mix, nudging it constantly so it always stays balanced. In their imaginary perfect world, you correct the balance every single instant, and then the mix is perfectly safe. Real people cannot steer *that* often, so real life is a little messier, but the closer you steer, the safer it gets. The coins you collected for selling the tickets are what pay for buying those bikes along the way, and if you steer well they turn out to be just enough.

## A surprise, a company is a kind of ticket too

Here is the part that made the idea famous far beyond bike tickets. A whole company can be seen as a ticket.

Imagine a lemonade company. It borrowed some coins and promised to pay them back next year. Whatever the company is worth next year, it must first pay back what it owes. If the company is worth more than the debt, the owners keep the leftover. If it is worth less than the debt, the owners walk away with nothing and the lenders take what is left.

Look closely and that is exactly our ticket. The company's owners hold a ticket to "buy the whole company back" by paying off the debt. If the company grew and is worth a lot, they happily pay the debt and keep the rest, just like using a coupon on a valuable toy. If the company shrank, they skip it and lose only their share, just like throwing away a coupon. So the same recipe that prices a bike ticket can also price who really owns a company and how risky its loans are. One idea, many uses.

## Putting it all together

Let us walk through the whole story in order, using our playground words.

1. **The ticket.** Someone wants to buy a ticket that lets them purchase a bike later at today's price. You need to charge a fair amount for it.
2. **The old problem.** Old methods asked you to guess where the price was heading, and everybody guessed differently, so nobody trusted the answer.
3. **The balance.** You own a bike and sell tickets in a careful mix, like weights on a see-saw, so gains and losses cancel and the mix is safe.
4. **The bank rule.** A safe mix cannot beat a safe piggy bank, so it must grow at the plain bank rate. That fact pins down the only fair ticket price.
5. **The jumpiness.** The one thing you still measure is how bouncy the bike price is. Bouncier means a pricier ticket.
6. **The steering.** You keep nudging the balance as the price moves, like steering a bike to stay straight.
7. **The bonus.** The very same recipe also explains who owns a company and how safe its debts are.

![How the fair ticket price is found, step by step]({{site.url_complet}}/assets/article/finance/black-scholes-eli10-workflow.png)

## Summary

The Black-Scholes model answers one question: what is the fair price of a ticket that lets you buy something later at a price fixed today? The clever move is to stop guessing the future. Instead you build a balanced mix of owning the thing and selling tickets, so the mix is safe no matter which way the price moves. A safe mix must grow at the same slow rate as money in a bank, and that rule leaves exactly one fair price for the ticket. The only fact you still need is how jumpy the price is, because a jumpier price makes the ticket worth more. The same idea even explains who really owns a company that has borrowed money. The picture below sums it up.

![Black-Scholes for kids mindmap]({{site.url_complet}}/assets/article/finance/black-scholes-eli10.png)

## Frequently Asked Questions

**Q: But why is a ticket to buy later worth anything at all? Why not just buy the bike when you want it?**

Because the ticket protects you from a price jump while asking almost nothing of you in return. If the bike suddenly costs a lot more, the ticket still lets you pay the old low price, so you save a pile of coins. If the bike gets cheaper instead, you simply ignore the ticket and buy normally. You get the good surprises and dodge the bad ones. Something that gives you only the nice outcomes and shields you from the nasty ones is worth paying a little for.

**Q: What if the bike price goes down instead of up? Do I lose a lot?**

No, and that is the whole point of a ticket. If the price drops, you just do not use the ticket. You throw it away like an expired coupon. The only thing you lose is the small amount you paid for the ticket in the first place. That little cost is the most you can lose, while your possible win has no such limit. That lopsided deal, small possible loss and big possible win, is why the ticket has value.

**Q: How does any of this help in real life?**

Grown-ups all over the world buy and sell these tickets, on things like company shares, oil, gold, and foreign money. Before Black and Scholes, people argued endlessly about fair prices and often got them badly wrong. Their recipe gave everyone a shared, sensible way to price these tickets, which made buying and selling them much safer and fairer. Airlines use tickets like this to protect against fuel price jumps, and farmers use them to protect against crop price drops.

**Q: What goes wrong if you skip the constant steering?**

If you set the balance once and then stop paying attention, the balance slowly slips out of place as the price moves. Then your mix is no longer safe, and a big price swing can leave you with a real loss or a surprise gain. It is like letting go of your handlebars. For a second you roll straight, but soon you drift off the path. The safety of the trick depends on making lots of small corrections, so skipping them breaks the promise that the mix cannot lose.

**Q: You sold two tickets but own only one bike. If both tickets get used, don't you come up short?**

Good catch, and this is the whole reason the balance is never a set-it-once thing. "One bike for two tickets" is only right at the start, while the bike is near 100 coins and each ticket is still a coin-flip, so each ticket behaves like only half a bike. If the price climbs and it starts to look like both tickets really will be used, you gradually buy that second bike on the way up, while it is still cheaper than the final price. By the time both tickets are used you already own two bikes, one for each, so you never have to scramble at the last moment. If the price falls and the tickets look worthless, you sell your bike back down instead. The coins you were paid for the tickets are what cover the cost of buying bikes as you go.

**Q: Can you give me another example of a "company is a ticket" situation?**

Think about renting a house with an option to buy it. You pay to live there, and the deal says you may purchase the house later for a price agreed now. If the neighbourhood becomes fancy and house prices soar, you happily buy at the old cheaper price and pocket the difference. If prices fall, you walk away and just lose your rent. You were holding a ticket the whole time. Lots of everyday deals, from renting with an option to buy, to a business owing money to a bank, hide this same ticket shape inside them.

## References

- [Black, Fischer, and Myron Scholes. "The Pricing of Options and Corporate Liabilities." Journal of Political Economy 81, no. 3 (1973): 637-654.](https://www.jstor.org/stable/1831029)
- [The Black-Scholes Model - Pricing Options and Corporate Liabilities (the technical companion to this article)]({{site.url_complet}}/2026/07/18/black-scholes-option-pricing-model/)
- [Claude Code](https://claude.com/product/claude-code)
