---
layout: post
title: Insuring Composable DeFi - First-Loss Capital Along the Attack Graph
date:   2026-07-02
lang: en
locale: en-GB
categories: blockchain defi security
tags: defi insurance first-loss-capital composability bridge oracle risk-management bad-debt
description: How to insure composable DeFi more efficiently by placing first-loss capital along the attack graph (bridges, oracles, signers) instead of only at protocol endpoints.
image: /assets/article/blockchain/defi/composable-insurance/2026-07-02-defi-composable-first-loss-capital-mindmap.png
isMath: true
---

Several of the largest DeFi incidents of the last few months share a pattern: the attack did not exploit a single protocol in isolation, it chained several protocols together and turned composability against them. The reflexive response has been to add more insurance at the protocol or asset level. This article is based on a [conference talk on the subject](https://www.youtube.com/watch?v=BgNGjJgTw2E) and follows its argument that the more useful question is *where* in a composable system the insurance should sit. Placing first-loss capital along the path an attacker actually travels, rather than only at the endpoint where the loss lands, turns out to be far more capital efficient.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Composability and Its Weaponization

Composability is one of the defining properties of DeFi. Positions that would require expensive legal contracts and bilateral agreements in traditional finance can be assembled permissionlessly on-chain: a token minted on one venue can be bridged to another, posted as collateral in a lending market, and borrowed against, all in a single transaction. This is where DeFi gets its capital efficiency.

The same property is also an attack surface. Many of the incidents of the last six months did not break a single contract; they strung several honest-looking components together so that a fault in one propagated, unchecked, into another. Because each hop looks locally valid, the composite failure is invisible to any one protocol's risk model. The result is bad debt that no single team believes is theirs to underwrite.

## Anatomy of a Composable Attack

The largest incident of the period serves as a worked example. The asset involved was a staking token (rETH) that had been moved across a bridge from another chain. The mechanics matter, so it is worth walking through them step by step.

When a token crosses a bridge, the bridge effectively *vouches* for the collateral on the origin chain: its message asserts that the backing exists and is real. An attacker found a way to forge the messages the bridge relied on, causing the bridge to sign an attestation it should never have signed. From that forged attestation, the attacker minted an amount of unbacked asset, a fake supply with no real collateral behind it.

The composability then did the rest. Lending vaults had already whitelisted this asset as acceptable collateral. So the attacker deposited the unbacked token and immediately borrowed real assets against it. The lending protocol handed out genuine value in exchange for collateral that did not exist, and that gap is exactly where the bad debt came from.

![Composable attack workflow from bridge forgery to bad debt]({{site.url_complet}}/assets/article/blockchain/defi/composable-insurance/composable-attack-workflow.png)

The important observation is that the loss materialised at the lending protocol, but the *cause* was upstream, at the bridge and the minting signer. The endpoint is where the money left; it is not where the fault was introduced.

## The Limits of Endpoint Insurance

The first instinct after such an incident is to add coverage at the protocol or asset level: asset issuers should provide insurance, or protocols should provide insurance. Over the last few months the prevailing sentiment has been pessimistic, that arranging this is very hard. Part of the reason is that endpoint insurance ignores the cause of the attack and ends up covering too many things at once.

Concretely, the industry response has been to add junior pools and first-loss capital: mechanisms such as Aave Umbrella and similar staking-backed backstops, mostly funded from protocol revenue or from users who stake capital into the first-loss tranche. A first-loss pool absorbs the initial losses before senior depositors are touched, which is a sound idea in isolation.

The problem is *placement*. These pools sit at the destination, the final state in the graph where coverage is actually paid out. But an attack traverses many components before it gets there: it goes through a bridge, the bridge attests to backing, new collateral is created, and only then does the loss land at the endpoint. Insuring only the endpoint means every asset is effectively backstopped by a single pool against every possible cyber incident, which is both expensive and badly targeted.

This placement problem produces a tragedy of the commons. A bridge or an oracle is a shared dependency of many protocols, yet no individual protocol wants to fund coverage for a component it does not own. Everyone protects their own endpoint of the graph, and the shared factors, the parts that actually caused the incident, go uninsured.

## Reframing First-Loss Capital as a Flow Problem

The proposed reframing is to stop thinking of first-loss capital as a static buffer at each endpoint and start thinking of it as coverage placed along the *attack graph*. In this graph, the nodes are not only protocols and assets but also the shared *factors* they depend on: bridges, oracles, minting signers, LP vaults, meta-vaults, and so on. An attack is a path through this graph.

![Attack graph with shared factors feeding composable protocols]({{site.url_complet}}/assets/article/blockchain/defi/composable-insurance/attack-graph-coverage-concept.png)

Viewed this way, exposure has two different decompositions. One is by asset and protocol: which endpoint holds the position. The other is by factor: which particular signer, bridge, or oracle caused a given issue. If you insure by the first decomposition, you appear to need coverage for every asset against every possible attack at the same time, which is why endpoint insurance looks so expensive. If you insure by the second, you notice that only certain paths through the graph correspond to incidents that were ever actually reported.

In an ideal arrangement, a shared factor such as a bridge would be insured by each protocol that uses it, in proportion to that usage. If roughly 40% of a bridge's volume flows to Aave, 30% to Morpho, and the remainder to Spark, each would contribute to the bridge's coverage in that proportion. That is the opposite of the current state, where the shared dependency is nobody's responsibility.

## Loss Attribution and Capital Efficiency

To make this concrete, consider why one smaller, well-placed pool can provide the same protection as several larger ones. Suppose four protocols each post $50M$ of their own revenue or users' capital as first-loss capital, for $200M$ in total. Now suppose a particular factor failure, say a faulty oracle, can only ever affect two of those four protocols, because the other two have larger buffers and larger supply caps and are essentially never touched by that specific route. If the maximum loss along that route is $100M$, the four-endpoint arrangement is holding $200M$ of capital against a $100M$ exposure. On that route it is over-collateralised by a factor of two, which is capital that could have been doing something else.

Placing the capital by route instead of by endpoint recovers that inefficiency. If the worst-case insured loss is $200M$, spreading the same first-loss budget across the right vaults might cover most of it with $120M$; targeting the responsible factors directly can lower the requirement further; and a mix of some protocol-level and some factor-level coverage can be lower still. The point is not the exact figures but the direction: matching coverage to where risk actually flows removes the systematic over-provisioning that endpoint-only insurance forces.

The mechanism for choosing *which* parts of the graph should carry coverage is a loss-attribution rule. Think of an attack as a flow of value through the graph, and attribute the resulting loss to each factor according to how much of that flow passed through it and how much of the damage it caused. Writing $L$ for the total loss of an incident and $f_i$ for the fraction of the attack flow that traversed factor $i$, a first-order attribution assigns

$$
\begin{aligned}
L_i = f_i \cdot L, \qquad \sum_i f_i = 1
\end{aligned}
$$

so that each factor's share of the loss reflects its share of the malicious flow. These attributed losses become the scores that say how much insurable coverage each factor needs. Coverage is then concentrated on the most likely failure paths first, rather than smeared across every path equally.

This turns provisioning into an optimisation problem. Let $B$ be the total insurance budget to allocate and $b_i \ge 0$ the amount placed on factor or protocol $i$. The goal is to choose the $b_i$ that maximise the coverage of realistic loss paths subject to the budget:

$$
\begin{aligned}
\max_{\,b \,\ge\, 0}\ \ \text{covered loss}(b) \quad \text{subject to} \quad \sum_i b_i \le B
\end{aligned}
$$

In the worked example this pushes more of the budget onto the bridge, a little onto the oracle, and a defined amount onto the minting signer, because that is where the attributed losses concentrate. The current tragedy-of-the-commons equilibrium, where each protocol funds only its own endpoint, is precisely the arrangement this optimisation improves on.

## Shared Coverage and Custom Credit Default Swaps

There is a useful financial reading of each attack path. A path through the graph, together with the coverage attached to it, behaves like a bespoke credit-default-swap-style instrument: it pays out when a specific composite failure occurs along that specific route. Because the route and its trigger are explicit, such an object is easier to price than a blanket policy that must stand behind every asset against every incident.

This also changes the incentives. Under the current model each protocol keeps its own pool and shares nothing, which is individually rational and collectively wasteful. Under a shared-coverage model, protocols that depend on the same bridge or oracle co-fund its coverage in proportion to their usage, and the aggregate outcome is better for all of them because the shared factor is no longer an uninsured single point of failure.

## Formal Coverage Guarantees

The final consequence is the most forward-looking. Once coverage is defined over paths in the graph, it becomes possible to ask which set of protocols is the safest to compose. By reasoning about how coverage moves across the graph, one can state a guarantee of the form: as long as a position stays within a given set of protocols and uses less than a certain amount of borrowed asset, it is always fully covered. Because the guarantee is a statement about the graph and its coverage, it can in principle be verified formally and checked live, rather than asserted after the fact.

The takeaway is deliberately narrow. The recommendation is to insure where risk moves through these systems, following it along bridges, oracles, and signers, rather than keeping static capital waiting at every endpoint for every conceivable attack.

## Conclusion

The composable incidents of 2026 exposed a mismatch between where losses land and where they are caused. Endpoint insurance, junior pools and first-loss tranches sitting at each protocol, backstops the destination while leaving the shared factors that actually failed uninsured, which is both costly and poorly targeted. Reframing first-loss capital as coverage placed along the attack graph, attributing losses to factors in proportion to the malicious flow through them and allocating a fixed budget by optimisation, matches capital to risk and removes the over-provisioning that endpoint-only coverage forces. The same framing yields per-path instruments that are easier to price and, ultimately, formal guarantees about which compositions are safe. The mindmap below summarises the argument.

![Mindmap summarising first-loss capital along the DeFi attack graph]({{site.url_complet}}/assets/article/blockchain/defi/composable-insurance/2026-07-02-defi-composable-first-loss-capital-mindmap.png)

## Frequently Asked Questions

**Q: What does "composability" mean in DeFi, and why is it described as an attack surface?**

Composability is the ability to assemble on-chain positions permissionlessly by plugging protocols into one another: a bridged token can be posted as collateral in a lending market and borrowed against in one transaction. It gives DeFi its capital efficiency because arrangements that would need legal contracts off-chain can be built directly on-chain. It is an attack surface because each hop looks locally valid while a fault in one component can propagate unchecked into the next, producing a composite failure that no single protocol's risk model sees.

**Q: In the rETH bridge example, where did the bad debt actually come from?**

The attacker forged the cross-chain message that the bridge relied on, so the bridge attested that collateral existed on the origin chain when it did not. From that forged attestation the attacker minted an unbacked amount of the asset, deposited it as collateral in lending vaults that had already whitelisted it, and borrowed real assets against it. The bad debt is the gap between the real value the lending protocol paid out and the unbacked collateral it received in return.

**Q: What is "endpoint insurance" and what is its main weakness?**

Endpoint insurance places first-loss capital at the destination, junior pools and staking-backed backstops such as Aave Umbrella sitting at each protocol, so that these tranches absorb losses before senior depositors are affected. Its weakness is placement, not concept. An attack traverses a bridge, an attestation, and newly created collateral before the loss ever lands, so insuring only the endpoint covers every asset against every incident with a single pool, which is expensive and badly targeted, and it leaves shared factors uninsured.

**Q: Why does insuring shared factors lead to a "tragedy of the commons" when it is not addressed?**

A bridge or oracle is a shared dependency of many protocols, but no individual protocol owns it, so none wants to fund coverage for it. Each team rationally protects only its own endpoint of the graph, and the shared factor, the component most likely to cause a cross-protocol incident, ends up with no coverage at all. The proposed fix is to have each protocol co-fund a shared factor's coverage in proportion to its usage of that factor.

**Q: How does loss attribution by flow make insurance more capital efficient, and how is it computed?**

Instead of buffering every endpoint against every attack, the model attributes each incident's loss to the factors along the path the attack took. Writing $L$ for the total loss and $f_i$ for the fraction of the attack flow through factor $i$, the attributed loss is $L_i = f_i \cdot L$ with $\sum_i f_i = 1$. These attributed losses score how much coverage each factor needs, so a fixed budget can be concentrated on the most likely failure paths first. The efficiency gain is concrete: four endpoints holding $200M$ against a route whose maximum loss is $100M$ are over-collateralised twofold, whereas allocating the same budget by route can cover the same worst case with materially less capital.

**Q: What is meant by "formal coverage guarantees," and how does the credit-default-swap analogy relate to them?**

Each path through the graph, together with its attached coverage, behaves like a bespoke credit-default-swap-style instrument: it pays out on a specific composite failure along a specific route, which makes it easier to price than a blanket policy standing behind everything. Once coverage is defined over paths this way, one can reason about how it moves across the graph and state a guarantee such as "any position that stays within this set of protocols and borrows less than a given amount is always fully covered." Because that guarantee is a property of the graph and its coverage, it can in principle be verified formally and checked live rather than asserted after an incident.

## References

- [Original talk (YouTube)](https://www.youtube.com/watch?v=BgNGjJgTw2E)
- [Aave protocol](https://aave.com)
- [Claude Code](https://claude.com/product/claude-code)
