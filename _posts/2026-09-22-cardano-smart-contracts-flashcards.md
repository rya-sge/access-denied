---
layout: post
title: "Cardano Smart Contracts in Twelve Cards — The Definitions to Memorise"
date:   2026-09-22
lang: en
locale: en-GB
categories: blockchain
tags: cardano eutxo smart-contracts validator datum plutus flashcards glossary key-terms
description: "Twelve flashcards for Cardano smart contracts: UTXO, datum, redeemer, script context, validator, script address, minting policy, collateral and the eUTXO model."
image: /assets/article/blockchain/cardano/2026-09-22-cardano-smart-contracts-flashcards-mindmap.png
isMath: false
---

[Cardano](https://cardano.org/) is a proof-of-stake blockchain whose ledger follows the Extended UTXO (eUTXO) model: value sits in discrete outputs rather than in account balances, and a smart contract is not a program that acts but a validator that approves or rejects the transaction trying to spend those outputs. This deck compresses the smart-contract module of the [Cardano developer curriculum](https://developers.cardano.org/docs/developers/curriculum/smart-contracts/overview) and the site's own articles on the model, for a reader who has met the material once and wants the vocabulary to stay put.

Twelve cards, each with a plain-words definition, a precise one, one line to remember and a link to the page of the official documentation that defines the term, plus a revision table at the end. The cards cover the contract and the piece of ledger architecture it lives in (outputs, script addresses, the two validation phases); they define, they do not derive, and they leave consensus and governance to their own articles. The longer treatments are [The Extended UTXO Model, and How It Differs from Bitcoin]({{site.url_complet}}/2026/07/16/eutxo-vs-bitcoin-utxo/) for the model, [Writing Cardano Smart Contracts with Aiken]({{site.url_complet}}/2026/07/16/aiken-smart-contracts-cardano/) for the code, and [Smart Contract Security on Cardano: What the eUTXO Model Removes and What Remains]({{site.url_complet}}/2026/07/16/cardano-smart-contract-security/) for what goes wrong.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The twelve cards

### UTXO

**In plain words:** A UTXO is a coin the chain still holds unspent: a transaction created it, it carries a value and an address, and spending it consumes it whole.

**Precisely:** An unspent transaction output, identified by the creating transaction's id and an output index, holding a multi-asset value at an address. It is immutable and is consumed in full exactly once, by a later transaction's input.

**Remember:** created once, spent once, never edited

**Reference:** [Cardano developer portal — How does the UTXO model track ownership?](https://developers.cardano.org/docs/developers/curriculum/fundamentals/core-concepts/eutxo#how-does-the-utxo-model-track-ownership)

### Datum

**In plain words:** A datum is a piece of data attached to a UTXO when it is created, and it is where a Cardano contract keeps its state.

**Precisely:** Structured data attached to a [UTXO](#utxo) at creation, stored inline in the output or as a hash whose value is revealed at spend time. It is the state a contract keeps, at most one per UTXO it locks.

**Remember:** datum = state, at most one per UTXO

**Reference:** [Cardano developer portal — How does the datum represent state?](https://developers.cardano.org/docs/developers/curriculum/smart-contracts/datum-redeemer-context#how-does-the-datum-represent-state)

### Redeemer

**In plain words:** A redeemer is the argument a spender attaches to a transaction to say which action they want from the contract, such as claim or cancel.

**Precisely:** A typed argument supplied in the transaction, one per script execution, naming the requested action and any witness data. The [datum](#datum) is fixed at lock time by the UTXO's creator; the redeemer at spend time by its spender.

**Remember:** datum at lock time, redeemer at spend time

**Reference:** [Cardano developer portal — How does the redeemer represent actions?](https://developers.cardano.org/docs/developers/curriculum/smart-contracts/datum-redeemer-context#how-does-the-redeemer-represent-actions)

### Script context

**In plain words:** The script context is the full transaction handed to the contract to judge: every input and output, who signed, what is minted, and the time window.

**Precisely:** The structure the node passes to a script: a TxInfo with all inputs, reference inputs, outputs, mint, fee, signatories and validity interval, plus the script purpose stating why it runs: spend, mint, withdraw, publish, vote or propose.

**Remember:** the whole transaction, plus why the script runs

**Reference:** [Cardano developer portal — What does the ScriptContext provide?](https://developers.cardano.org/docs/developers/curriculum/smart-contracts/datum-redeemer-context#what-does-the-scriptcontext-provide)

### Validator

**In plain words:** A validator is a Cardano smart contract: a program that looks at a proposed transaction and only says yes or no, never acting on its own.

**Precisely:** A pure function of the [datum](#datum), [redeemer](#redeemer) and [script context](#script-context) returning success or failure, run by every node that validates the transaction. It cannot send funds, call another script, read outside the transaction or loop without bound; it only constrains.

**Remember:** f(datum, redeemer, context) → yes or no

**Reference:** [Cardano developer portal — Smart contracts are validators, not actors](https://developers.cardano.org/docs/developers/curriculum/smart-contracts/overview#smart-contracts-are-validators-not-actors)

### Script address

**In plain words:** A script address is an address whose rules are a validator: anyone can send coins to it, but only a transaction the validator approves can take them out.

**Precisely:** An address derived from the hash of a [validator](#validator)'s compiled code and a language tag, so the same code under the same Plutus version yields the same address. Sending a UTXO there locks it under that validator.

**Remember:** address = hash of the code; funds locked by rules

**Reference:** [Cardano developer portal — Script addresses and purposes](https://developers.cardano.org/docs/developers/curriculum/smart-contracts/overview#script-addresses-and-purposes)

### State transition

**In plain words:** A state transition is how a contract updates its state: the transaction spends the UTXO holding the old state and creates a new one holding the new state.

**Precisely:** A transaction that consumes the [UTXO](#utxo) at a [script address](#script-address) and produces a successor output at the same address with the next [datum](#datum); the validator must check that the old-to-new transition is legal. No UTXO is modified in place.

**Remember:** spend the old datum, create the new one, never edit

**Reference:** [Cardano developer portal — The continuing-output pattern](https://developers.cardano.org/docs/developers/curriculum/smart-contracts/datum-redeemer-context#the-continuing-output-pattern)

### Minting policy

**In plain words:** A minting policy is a validator that decides when tokens under its name may be created or destroyed; the tokens themselves then move around like ada, with no contract involved.

**Precisely:** A [validator](#validator) run with the mint purpose whenever a transaction mints or burns tokens; its script hash is the policy id. A native token is the pair (policy id, asset name), carried in [UTXO](#utxo) values by the ledger itself.

**Remember:** policy id = script hash; tokens live in UTXO values

**Reference:** [Cardano developer portal — Minting policies](https://developers.cardano.org/docs/developers/curriculum/native-tokens/minting-policies)

### Deterministic validation

**In plain words:** Deterministic validation means a transaction's result and its exact cost are known before it is sent, because the contract reads only the transaction itself, never the live chain.

**Precisely:** The property that a [validator](#validator)'s outcome depends only on the transaction and its [script context](#script-context), never on live chain state, so the builder can evaluate every script locally and know the result and the execution cost before submission.

**Remember:** same transaction, same result, cost known in advance

**Reference:** [Cardano developer portal — Why is deterministic validation such a big deal?](https://developers.cardano.org/docs/developers/curriculum/fundamentals/core-concepts/eutxo#why-is-deterministic-validation-such-a-big-deal)

### Two-phase validation

**In plain words:** Two-phase validation first checks that a transaction is well formed and signed, then runs its contracts; only a contract failing in the second phase costs the sender their collateral.

**Precisely:** Phase 1 checks structure: inputs exist, signatures verify, values balance; a failure costs nothing. Phase 2 runs the scripts within an execution-unit budget priced into the fee; if a script fails, the node consumes the ada-only collateral inputs instead.

**Remember:** phase 1 fails for free; phase 2 failure costs collateral

**Reference:** [Cardano developer portal — How scripts execute](https://developers.cardano.org/docs/developers/curriculum/smart-contracts/overview#how-scripts-execute)

### Off-chain code

**In plain words:** Off-chain code is the part of a Cardano application that finds the locked UTXOs and builds a transaction the validator will accept; it can be written in any language.

**Precisely:** The application half of a contract: it queries the chain, selects inputs, constructs datums and redeemers, evaluates the scripts locally and submits the transaction. The on-chain [validator](#validator) only judges what it built; the off-chain code does the creative work.

**Remember:** off-chain drafts, on-chain judges

**Reference:** [Cardano developer portal — On-chain and off-chain](https://developers.cardano.org/docs/developers/curriculum/smart-contracts/overview#on-chain-and-off-chain)

### eUTXO model

**In plain words:** The eUTXO model is Cardano's way of holding value and running contracts: coins carry data, and a contract is a rule that decides which transactions may spend them.

**Precisely:** The UTXO model extended so that an output carries a [datum](#datum), a spend carries a [redeemer](#redeemer), and a [validator](#validator) judges the whole transaction through the [script context](#script-context). Value moves by consuming and creating outputs, not by updating balances.

**Remember:** coins with data, guarded by predicates, not accounts

**Reference:** [Cardano developer portal — eUTXO](https://developers.cardano.org/docs/developers/curriculum/fundamentals/core-concepts/eutxo)

## Flashcard table

| # | Term | In plain words | One thing to remember |
|:---:|------|----------------|------------------------|
| 1 | UTXO | A UTXO is a coin the chain still holds unspent: a transaction created it, it carries a value and an address, and spending it consumes it whole. | created once, spent once, never edited |
| 2 | Datum | A datum is a piece of data attached to a UTXO when it is created, and it is where a Cardano contract keeps its state. | datum = state, at most one per UTXO |
| 3 | Redeemer | A redeemer is the argument a spender attaches to a transaction to say which action they want from the contract, such as claim or cancel. | datum at lock time, redeemer at spend time |
| 4 | Script context | The script context is the full transaction handed to the contract to judge: every input and output, who signed, what is minted, and the time window. | the whole transaction, plus why the script runs |
| 5 | Validator | A validator is a Cardano smart contract: a program that looks at a proposed transaction and only says yes or no, never acting on its own. | f(datum, redeemer, context) → yes or no |
| 6 | Script address | A script address is an address whose rules are a validator: anyone can send coins to it, but only a transaction the validator approves can take them out. | address = hash of the code; funds locked by rules |
| 7 | State transition | A state transition is how a contract updates its state: the transaction spends the UTXO holding the old state and creates a new one holding the new state. | spend the old datum, create the new one, never edit |
| 8 | Minting policy | A minting policy is a validator that decides when tokens under its name may be created or destroyed; the tokens themselves then move around like ada, with no contract involved. | policy id = script hash; tokens live in UTXO values |
| 9 | Deterministic validation | Deterministic validation means a transaction's result and its exact cost are known before it is sent, because the contract reads only the transaction itself, never the live chain. | same transaction, same result, cost known in advance |
| 10 | Two-phase validation | Two-phase validation first checks that a transaction is well formed and signed, then runs its contracts; only a contract failing in the second phase costs the sender their collateral. | phase 1 fails for free; phase 2 failure costs collateral |
| 11 | Off-chain code | Off-chain code is the part of a Cardano application that finds the locked UTXOs and builds a transaction the validator will accept; it can be written in any language. | off-chain drafts, on-chain judges |
| 12 | eUTXO model | The eUTXO model is Cardano's way of holding value and running contracts: coins carry data, and a contract is a rule that decides which transactions may spend them. | coins with data, guarded by predicates, not accounts |

## Conclusion

Three cards carry the deck. [Validator](#validator) is the contract itself, a predicate rather than an actor; [script context](#script-context) is what lets that predicate constrain every input and output of the transaction, not only the UTXO it guards; and [state transition](#state-transition) is the one operation a stateful contract ever performs, consuming the old datum and creating the new one. A reader who holds those three has the model; the other cards name the pieces they are stated in and the two ledger guarantees, determinism and two-phase validation, that follow from them.

The deck stops at the ledger. Consensus is covered in [Ouroboros: How Cardano Reaches Consensus with Proof of Stake]({{site.url_complet}}/2026/07/16/ouroboros-proof-of-stake/), the languages that compile to the validator in the Aiken article, and the ways a validator can be satisfied by a transaction its author did not intend in the security article.

![Mindmap of the Cardano smart-contract flashcards grouped into objects, the contract, operations and the ledger]({{site.url_complet}}/assets/article/blockchain/cardano/2026-09-22-cardano-smart-contracts-flashcards-mindmap.png)

## Frequently Asked Questions

**Q: What is the difference between the [datum](#datum) and the [redeemer](#redeemer)?**

Both are arguments to the validator, and the difference is who sets them and when. The datum is attached to the UTXO by whoever creates it, so it is the state that was locked. The redeemer is supplied by whoever spends the UTXO, so it is the action being requested against that state.

**Q: Which card explains why a Cardano contract cannot call another contract?**

[Validator](#validator): it is a pure function that only constrains a transaction and cannot send, call or initiate anything. Several validators still cooperate in one transaction, but not by calling each other: each independently checks its own rules against the same [script context](#script-context), and the transaction passes only if all of them approve.

**Q: If validation is deterministic, why does a transaction need collateral?**

[Deterministic validation](#deterministic-validation) says an honest builder can evaluate the scripts locally and learn the outcome before submitting, so a transaction that would fail in phase 2 need never be sent. [Two-phase validation](#two-phase-validation) says that if one is sent anyway, the node still has to run the script, and the collateral pays for that work. The two cards together explain why honest transactions never lose collateral and flooding the network with failing scripts is expensive.

**Q: Put [script address](#script-address), [datum](#datum), [redeemer](#redeemer), [validator](#validator) and [state transition](#state-transition) in the order a contract uses them.**

Script address first: sending a UTXO there, with an initial datum, creates the contract instance. Then a spender builds a transaction carrying a redeemer, the validator judges it against the datum, the redeemer and the script context, and if it approves, the state transition consumes the old UTXO and creates the successor with the next datum. Then the cycle repeats from the datum.

**Q: What does the Remember line of [validator](#validator) leave out?**

`f(datum, redeemer, context)` is the signature of a spend. A [minting policy](#minting-policy) guards no UTXO, so there is no datum for it to receive; it runs on the redeemer and the script context alone. The line also drops the qualifier that the function is run by every node and produces no side effects, which is what the deterministic-validation card depends on.

**Q: Which card is wrong if a validator could read the current balance of another contract?**

[Deterministic validation](#deterministic-validation), and with it the [script context](#script-context) card. The context is a snapshot of the transaction alone; if a validator could read live chain state, its outcome could change between local evaluation and inclusion in a block, the builder could no longer know the result in advance, and a failing script could no longer be blamed on the builder.

**Q: What does the plain-words line of [minting policy](#minting-policy) hide that the precise line states?**

Two identifiers. The policy id is the hash of the policy script, so a token's identity is bound to the code that governs its supply, and a native token is the pair of policy id and asset name, not a single name. It also states that tokens are carried in UTXO values by the ledger, which is why transferring one is an ordinary transaction with no script involved.

## References

- [Cardano developer curriculum — Smart Contracts](https://developers.cardano.org/docs/developers/curriculum/smart-contracts/overview), the module the deck compresses
- [Cardano developer curriculum — Datum, Redeemer, and ScriptContext](https://developers.cardano.org/docs/developers/curriculum/smart-contracts/datum-redeemer-context)
- Manuel Chakravarty, James Chapman, Kenneth MacKenzie, Orestis Melkonian, Michael Peyton Jones, Philip Wadler, [*The Extended UTXO Model*](https://iohk.io/en/research/library/papers/the-extended-utxo-model/), 2020
- [Cardano Academy glossary](https://github.com/cardano-foundation/cardano-academy/blob/main/glossary.md)

### Related articles

- [The Extended UTXO Model, and How It Differs from Bitcoin]({{site.url_complet}}/2026/07/16/eutxo-vs-bitcoin-utxo/)
- [Writing Cardano Smart Contracts with Aiken]({{site.url_complet}}/2026/07/16/aiken-smart-contracts-cardano/)
- [Smart Contract Security on Cardano: What the eUTXO Model Removes and What Remains]({{site.url_complet}}/2026/07/16/cardano-smart-contract-security/)
- [Money as a Jar of Coins — How Cardano Tracks Who Owns What, Explained for a 10-Year-Old]({{site.url_complet}}/2026/07/16/eutxo-explained-eli10/)
- [Ouroboros: How Cardano Reaches Consensus with Proof of Stake]({{site.url_complet}}/2026/07/16/ouroboros-proof-of-stake/)
