---
layout: post
title: "Cardano On-Chain Governance: The Voltaire Era and CIP-1694"
date:   2026-07-16
lang: en
locale: en-GB
categories: blockchain
tags: cardano governance cip-1694 voltaire drep treasury conway
description: A technical overview of Cardano's on-chain governance under CIP-1694 (the Voltaire era). Covers the three governance bodies, the seven action types, ratification thresholds and lifecycle, vote delegation, and what it means for developers.
image: /assets/article/blockchain/cardano/cardano-voltaire-governance-cip-1694.png
isMath: false
---

Cardano's Voltaire era, defined by [CIP-1694](https://cips.cardano.org/cip/CIP-1694) and activated with the Conway ledger era, moved decisions about the protocol on-chain: ADA holders can now propose, vote on, and enact changes to parameters, the treasury, and the protocol itself. For a developer the central fact is that governance actions are ordinary transactions, built with the same wallets and transaction builders as any transfer, plus a few new certificate and procedure types. This article explains the governance system: the three bodies that hold power, the seven action types, how an action is ratified and enacted, how vote delegation works, and why it matters to anyone building on Cardano. It follows the Cardano [developer portal's governance documentation](https://developers.cardano.org/).

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why governance reaches into developer code

Governance is not only an end-user feature; it shapes the platform a developer builds on.

- **Protocol parameters affect your code.** Transaction size limits, execution-unit budgets, min-UTXO values, and fees are all governance-controlled, and a change can affect deployed contracts. Design with margin and watch proposals that touch technical parameters.
- **Hard forks can change Plutus.** Upgrades may add Plutus versions with new capabilities; the Chang hard fork introduced Plutus V3 with built-ins for governance. Older scripts keep working, but new features require the newer version.
- **The treasury funds development.** The on-chain treasury, over a billion ADA, is allocated by governance vote, an on-chain alternative to traditional grants that a team can propose into.
- **Your users participate.** If you build a wallet or dApp, your users are governance participants who may expect to register a DRep, delegate a vote, or vote through your interface.

## The three governance bodies

CIP-1694 distributes power across three bodies that act as checks and balances.

- **Constitutional Committee (CC)**: verifies that actions comply with the Cardano Constitution. It functions as a constitutional court, ruling on constitutionality rather than on the merit of a proposal.
- **Delegated Representatives (DReps)**: the primary voice of ADA holders. Anyone can register as a DRep, and any holder can delegate their vote to one.
- **Stake Pool Operators (SPOs)**: vote on specific action types, notably hard forks and certain security-relevant parameters.

Each action type requires a different combination of these bodies, which is what produces the checks and balances.

![Component diagram of the three governance bodies (Constitutional Committee, DReps, SPOs) voting on a governance action]({{site.url_complet}}/assets/article/blockchain/cardano/governance-bodies-concept.png)

## The seven action types

There are seven kinds of governance action, and each engages a different mix of the three bodies.

| Action | CC | DReps | SPOs |
|---|---|---|---|
| Motion of no-confidence | - | Yes | Yes |
| Update committee / threshold | - | Yes | Yes |
| New constitution or guardrails script | Yes | Yes | - |
| Hard-fork initiation | Yes | Yes | Yes |
| Protocol parameter change | Yes | Yes | * |
| Treasury withdrawal | Yes | Yes | - |
| Info action (non-binding) | - | Yes | Yes |

The asterisk on protocol parameter changes marks that SPOs vote only on specific parameter groups. An info action records a signal on-chain but has no protocol effect. A hard-fork initiation is the only type that engages all three bodies at once.

## Ratification and the action lifecycle

Each action type is ratified by meeting a different mix of voting thresholds across the three bodies. The fractions below are the Conway defaults, and they are themselves governance-controlled.

| Governance action | CC | DReps | SPOs |
|---|---|---|---|
| Motion of no-confidence | - | 0.67 | 0.51 |
| Update committee / threshold (normal) | - | 0.67 | 0.51 |
| Update committee / threshold (no-confidence) | - | 0.60 | 0.51 |
| New constitution or guardrails script | 2/3 | 0.75 | - |
| Hard-fork initiation | 2/3 | 0.60 | 0.51 |
| Protocol parameters (network / economic / technical) | 2/3 | 0.67 | - |
| Protocol parameters (governance group) | 2/3 | 0.75 | - |
| Treasury withdrawal | 2/3 | 0.67 | - |
| Info action (non-binding) | 2/3 | 1 | 1 |

Changing a **security-relevant** parameter (block and transaction sizes, fees, `utxoCostPerByte`, `govActionDeposit`, and similar) requires an extra SPO vote at 0.51, even for parameter groups SPOs do not normally vote on.

A proposed action then runs a fixed lifecycle, which is what governance tooling reads when it displays an action's status:

1. **Live** for `govActionLifetime` epochs (6 on mainnet), during which the bodies vote.
2. **Ratified** once it meets the thresholds for its type, and added to the enactment set at the epoch boundary.
3. **Enacted** at the next epoch boundary, when the change takes effect.
4. **Expired** if it never reaches its thresholds within its lifetime.

![State diagram of the governance action lifecycle from Live through Ratified and Enacted, or to Expired]({{site.url_complet}}/assets/article/blockchain/cardano/governance-action-lifecycle-states.png)

Most action types carry a pointer to the last enacted action of the same kind, so an action ratifies against the state it was proposed against; treasury withdrawals and info actions are exempt. The deposit is returned to the proposer's reward account once the action leaves the Live state, whether it was enacted or expired.

## Vote delegation is separate from stake delegation

Voting power delegation is independent of stake delegation. A holder can delegate stake to one pool for rewards and delegate their vote to a different DRep, and change either without affecting the other. Both delegations attach to the **stake credential**, the part of an address distinct from the payment credential.

For holders who do not want to pick a DRep, two built-in options exist: **Abstain**, whose voting power is not counted, and **No Confidence**, which counts against the committee. In the Conway era there is a concrete incentive to make a choice: staking rewards keep accruing, but they cannot be withdrawn until the stake credential has delegated its vote, whether to a DRep or to one of the built-in options.

## Participating: from proposal to enactment

Because governance actions are ordinary transactions, the operations map onto certificates and procedures a wallet or backend can build:

- **Register as a DRep**: a registration certificate with a refundable deposit (`drepDeposit`, currently 500 ADA) and an optional metadata anchor describing the DRep. Registration can also be controlled by a native (multisig) or Plutus script rather than a key.
- **Delegate a vote**: a vote-delegation certificate on the stake credential targeting a registered DRep or one of the built-in options.
- **Vote**: a registered DRep, a CC member, or an SPO casts a Yes / No / Abstain vote against a specific action, identified by the transaction that created it and its index.
- **Propose**: anyone can submit any of the seven action types with a deposit (`govActionDeposit`), refunded after the vote.

Governance state is queryable, so a UI can show proposals, DRep registration and voting power, and committee state; API providers expose the same data over HTTP. For browser dApps, [CIP-95](https://cips.cardano.org/cip/CIP-0095) extends the wallet connector with governance methods so a dApp can read the user's DRep key and registered stake keys to build these transactions.

## Governance inside validators

Plutus V3 added governance **script purposes**: a validator can run as a `Voting` or `Proposing` script, letting a contract participate in governance under script control. The same script-controlled model applies to DRep and committee credentials, so a DRep can be a multisig or a Plutus script rather than a single key, with authorization coming from a redeemer instead of a signature.

## Conclusion

Cardano's Voltaire governance, defined by CIP-1694 and running on the Conway ledger era, places protocol decisions on-chain and distributes them across three bodies: the Constitutional Committee rules on constitutionality, DReps represent ADA holders, and SPOs vote on hard forks and security-relevant parameters. Seven action types each require a different mix of these bodies to meet their ratification thresholds, and every action runs a fixed Live, Ratified, Enacted, or Expired lifecycle with a refundable deposit.

For developers the model has two practical consequences. Governance-controlled parameters, hard forks, and the treasury all touch what you build, so proposals are worth watching and, when useful, proposing into. And because governance actions are ordinary transactions, integrating DRep registration, vote delegation, voting, and proposals into a wallet or dApp uses the same tooling as any other transaction, extended by a set of certificates and, through CIP-95, by wallet-connector methods. The mindmap below collects the bodies, action types, lifecycle, and participation paths.

![Mindmap summarizing Cardano Voltaire governance: the three bodies, seven action types, ratification, lifecycle, participation, and developer relevance]({{site.url_complet}}/assets/article/blockchain/cardano/cardano-voltaire-governance-cip-1694.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **CIP-1694** | the proposal defining Cardano's on-chain governance, activated with the Conway ledger era and giving the Voltaire era its rules. |
| **Voltaire** | the Cardano development era focused on governance, in which protocol decisions move on-chain. |
| **Constitutional Committee (CC)** | the body that verifies whether a governance action complies with the Cardano Constitution, ruling on constitutionality rather than merit. |
| **DRep (Delegated Representative)** | an entity, registered on-chain, that votes on behalf of the ADA holders who delegate their voting power to it. |
| **Stake Pool Operator (SPO)** | a pool operator who, in governance, votes on specific action types such as hard forks and security-relevant parameters. |
| **Governance action** | an on-chain proposal of one of seven types, submitted with a refundable deposit and voted on by the relevant bodies. |
| **Ratification threshold** | the fraction of a body's voting power required to approve a given action type; the Conway defaults are themselves governance-controlled. |
| **govActionLifetime** | the number of epochs (6 on mainnet) during which an action stays Live and open to votes before it is ratified or expires. |
| **Vote delegation** | assigning voting power to a DRep or a built-in option; it attaches to the stake credential and is independent of stake delegation to a pool. |
| **Treasury** | the on-chain pool of ADA, over a billion, that governance allocates by vote, including funding for ecosystem development. |

## Frequently Asked Questions

**Q: What are the three governance bodies, and what is each responsible for?**

The Constitutional Committee, the Delegated Representatives (DReps), and the Stake Pool Operators (SPOs). The Constitutional Committee checks that an action complies with the Cardano Constitution, acting like a constitutional court on constitutionality rather than judging whether a proposal is a good idea. DReps are the primary voice of ADA holders; anyone can register as one, and any holder can delegate their vote to one. SPOs vote on specific action types, principally hard-fork initiations and security-relevant parameters. Different action types require different combinations of the three, which is what creates the checks and balances.

**Q: Why can a holder delegate stake to one pool but their vote to a different DRep?**

Because the two delegations are independent and both attach to the stake credential, the part of an address separate from the payment credential. Stake delegation directs block-production participation and rewards to a pool; vote delegation directs governance voting power to a DRep. They are recorded by separate certificates and can be changed independently. A holder who does not want to name a DRep can instead delegate to a built-in Abstain or No Confidence option. In the Conway era this choice is effectively required to access rewards: staking rewards accrue but cannot be withdrawn until the stake credential has delegated its vote to something.

**Q: What is the lifecycle of a governance action from proposal to effect?**

A submitted action becomes Live for `govActionLifetime` epochs (6 on mainnet), during which the bodies cast votes. If it meets the ratification thresholds for its type, it becomes Ratified and is added to the enactment set at the epoch boundary, then Enacted at the following epoch boundary, when the change takes effect. If it never reaches its thresholds within its lifetime, it Expires. In either terminal case the proposer's deposit is returned to their reward account once the action leaves the Live state.

**Q: Why does changing a security-relevant parameter require an SPO vote even when SPOs do not normally vote on that parameter group?**

Security-relevant parameters (such as block and transaction sizes, fees, `utxoCostPerByte`, and `govActionDeposit`) directly affect the operation and safety of the network that stake pool operators run. To prevent such changes from being made without the operators who bear their consequences, CIP-1694 requires an additional SPO vote at a 0.51 threshold for these parameters, even for groups that SPOs would otherwise not vote on. It is an extra check placed specifically on the changes most able to disrupt the network.

**Q: A team wants to add a "vote through our wallet" feature and later apply for treasury funding. Which parts of the governance system does that touch, and how do they connect?**

Both draw on the same machinery from different angles. The wallet feature uses the participation path: vote delegation and voting are ordinary transactions built from certificates and voting procedures, and for a browser dApp, CIP-95 extends the wallet connector so the app can read the user's DRep key and registered stake keys to construct them. Applying for treasury funding uses the proposal path: a treasury-withdrawal action is one of the seven action types, submitted with a refundable `govActionDeposit` and an anchor describing the request, then voted on by the Constitutional Committee (constitutionality) and DReps to their thresholds before it can be ratified and enacted. The connection is that the team's own users, voting through the wallet feature, are part of the DRep-delegated electorate whose votes decide whether proposals like the team's funding request pass.

## References

- [CIP-1694 — On-Chain Decentralized Governance](https://cips.cardano.org/cip/CIP-1694)
- [Cardano developer portal](https://developers.cardano.org/)
- [cardano.org/governance — participant hub](https://cardano.org/governance)
- [CIP-95 — Web-Wallet Bridge, Conway era](https://cips.cardano.org/cip/CIP-0095)
- [CIP-119 — DRep metadata](https://cips.cardano.org/cip/CIP-0119)
- [Claude Code](https://claude.com/product/claude-code)
