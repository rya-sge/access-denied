---
layout: post
title: "The Extended UTXO Model, and How It Differs from Bitcoin"
date:   2026-07-16
lang: en
locale: en-GB
categories: blockchain
tags: cardano bitcoin eutxo utxo smart-contracts datum validator
description: A technical comparison of Cardano's Extended UTXO (eUTXO) model with Bitcoin's original UTXO model. Covers the shared coin-based foundation and the three extensions (datum, redeemer, script context) that enable expressive validators and stateful contracts.
image: /assets/article/blockchain/cardano/eutxo-vs-bitcoin-utxo.png
isMath: false
---

Cardano's ledger is built on the same idea as Bitcoin's: value is held in discrete, immutable coins rather than in mutable account balances. Cardano then extends that idea so that scripts can express far more than Bitcoin's allow, without giving up the properties that make the coin model predictable. The result is the Extended UTXO (eUTXO) model. This article works through what Cardano keeps from Bitcoin, what the word "Extended" actually adds, and where the two models diverge for anyone writing or reasoning about on-chain logic. The model description follows the Cardano [developer portal](https://developers.cardano.org/).

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The shared foundation: tracking value as coins

Every blockchain needs a way to record who owns what. Two designs dominate. The **account model**, used by Ethereum, keeps a mutable balance per address and updates it in place, debiting the sender and crediting the receiver like rows in a database. The **UTXO model**, introduced by Bitcoin and adopted in extended form by Cardano, does something different: it tracks ownership through discrete unspent transaction outputs, and value moves by consuming whole outputs and creating new ones.

The physical-cash analogy is exact. You do not hold an abstract balance of 50; you hold specific bills. To pay 25 you hand over a 30 and receive 5 in change. A UTXO transaction works the same way: it consumes one or more existing UTXOs in full and produces new UTXOs, one of which is usually change back to the sender.

```text
Alice's UTXOs:
  UTXO_1: 3,000   (from tx_abc, output #0)
  UTXO_2: 2,000   (from tx_def, output #1)

Alice sends 4,500 to Bob:
  INPUTS:                 OUTPUTS:
  UTXO_1  3,000           To Bob    4,500   (new UTXO)
  UTXO_2  2,000           Change      300   (new UTXO)
  Total: 5,000            Fee         200
                          Total:    5,000
```

Four properties follow from this design, and they hold identically in Bitcoin and Cardano:

1. **A UTXO is consumed entirely.** You cannot partially spend one; spending part of a UTXO means consuming all of it and creating change.
2. **Inputs equal outputs plus fees, exactly.** The protocol enforces the balance; value is not created or destroyed in an ordinary transaction.
3. **A UTXO is immutable.** Once created it never changes. There is no update, only create (as an output) and consume (as an input).
4. **A UTXO is spent once.** Consuming it in a confirmed transaction removes it from circulation forever, which is how double-spending is prevented.

The **UTXO set** is the collection of all unspent outputs at a given moment, and it is the current state of the chain. Each entry is identified by the transaction that created it plus an output index, the `(TxId, index)` pair known as a transaction output reference. On both networks every node keeps this set for validation.

Everything in this section is common ground. The differences begin at what a single output can carry and what a script may inspect when it is spent.

## Bitcoin's output and its script model

In Bitcoin, an output is a pair: an amount in satoshis and a **locking script** (the `scriptPubKey`), a predicate that says what it takes to spend the coin. To spend it, a later transaction supplies an **unlocking script** (the `scriptSig`, or witness data in SegWit), and the network runs the unlocking data against the locking script. If the combined program succeeds, the spend is authorized.

Bitcoin Script is a stack-based language, and it is deliberately restricted. It has no loops and is not Turing-complete, which keeps validation bounded and predictable. The common templates are familiar: pay-to-public-key-hash requires a signature matching a public key, pay-to-script-hash commits to a redeem script revealed at spend time, and multisig requires several signatures.

The point that matters for the comparison is what a Bitcoin script can actually observe. It sees the unlocking data provided to it. Signature-checking opcodes such as `OP_CHECKSIG` verify a signature over a serialization of the spending transaction, and the `SIGHASH` flags choose which parts of that transaction the signature commits to, so a spend can be bound to particular outputs to a limited degree. Time is available through `nLockTime` together with `OP_CHECKLOCKTIMEVERIFY` (absolute) and `OP_CHECKSEQUENCEVERIFY` (relative). What Bitcoin does not provide is any persistent state attached to a coin, or a general ability for a script to read the other inputs and outputs of its transaction. There is also no notion of assets other than bitcoin at the base layer.

These limits are a design choice, not an oversight. They keep the surface small and validation simple. They also mean that expressing a rule like "this coin may only be spent into an output that preserves some updated state" (a covenant) is not generally possible in deployed Bitcoin Script; such capabilities are the subject of ongoing proposals rather than shipped features.

## What "Extended" adds

Cardano keeps the coin model in full and extends the output with three elements. Two of them live on the output or are supplied at spend time; the third is a view the ledger hands to the script.

- **Datum**: data attached to a UTXO. This is state that lives inside a specific output. Where an account-based contract keeps state in mutable storage, an eUTXO contract keeps it in a datum, and it advances that state by consuming the UTXO and creating a new one carrying new data. Cardano supports a datum hash (only the hash is stored on-chain, the full value supplied when spending) and an inline datum (the full value stored in the output so anyone can read it without off-chain coordination).
- **Redeemer**: the argument the spender supplies when unlocking a script-controlled UTXO. The validator uses it to decide whether the spend is allowed, and it is roughly the analogue of Bitcoin's unlocking data, but typed and structured.
- **Script context**: the view the validator receives of the entire transaction, including all inputs, all outputs, the fee, the validity interval, and the signatories.

![Component diagram comparing the fields of a Bitcoin UTXO with a Cardano eUTXO]({{site.url_complet}}/assets/article/blockchain/cardano/utxo-vs-eutxo-structure-concept.png)

A Cardano validator is a pure function of the datum, the redeemer, and the context, returning approval or rejection. Like Bitcoin Script it cannot loop forever (execution budgets enforce termination) and it produces no side effects, so it remains a predicate rather than an actor. What changes is how much it can see and therefore how much it can enforce.

## The decisive difference: what a script can see

The two models diverge most in what a script is allowed to inspect when a UTXO is spent.

A Bitcoin script sees, in practice, the unlocking data and the signature commitments allowed by `SIGHASH`, plus the time-lock checks. It cannot attach state to a coin, and it cannot in general inspect the sibling inputs and outputs of its own transaction.

A Cardano validator sees the whole transaction through the script context: every input and output, the amounts and datums involved, the fee, the validity interval, and who signed. It does not see arbitrary global chain state, which is exactly the property that preserves determinism. This middle ground was the subject of formal research, and it was designed to give expressive power comparable to the account model while keeping the stronger guarantees of the coin model.

![Component diagram contrasting the narrow visibility of a Bitcoin script with the whole-transaction context a Cardano validator receives]({{site.url_complet}}/assets/article/blockchain/cardano/script-visibility-scope-concept.png)

That visibility is what makes conditions like the following expressible in a single validator:

- This UTXO may be spent only if the transaction also pays a specified amount to a specified address.
- This UTXO may be spent only after a given slot (enforced through the validity interval).
- This UTXO may be spent only if the transaction recreates this same script address with an updated datum.

The last condition is the foundation of stateful contracts, and it is the capability Bitcoin Script does not generally have.

## Stateful contracts without mutable state

Because a validator can read the transaction's outputs, it can require that spending its UTXO also produces a successor output at the same script address carrying the next valid state. State therefore advances by a destroy-and-create cycle rather than an in-place update: the old UTXO is consumed, a new one is created with the new datum, and the validator enforces that the transition is legal.

![Sequence diagram of a stateful contract advancing its state by consuming a script UTXO and recreating it with an updated datum]({{site.url_complet}}/assets/article/blockchain/cardano/eutxo-stateful-spend-sequence.png)

This is how a vesting contract, an auction, or a decentralized-exchange pool holds and updates state on Cardano. A concrete vesting example: a UTXO is locked at a script with a datum recording the beneficiary and a release slot; the validator approves a withdrawal only when the transaction's validity interval starts after the release slot, the funds go to the beneficiary, and the beneficiary has signed. Every one of those checks reads the script context. In Bitcoin the closest constructions rely on pre-signed transactions and time locks rather than a script reading and enforcing arbitrary conditions on its transaction's outputs.

## Native assets in the output

Cardano's outputs are multi-asset. A single UTXO carries ADA alongside any number of native tokens, tracked by the ledger at the protocol level rather than by a smart contract.

```text
A single UTXO:
  Address: addr_alice
  Value:
    5 ADA (5,000,000 lovelace)
    PolicyID_abc.TokenA: 1,000
    PolicyID_def.MyNFT:  1
```

Because tokens live in the value of a UTXO the way ADA does, transferring them is an ordinary UTXO operation and needs no contract execution, and they inherit the ledger's security. Bitcoin has no equivalent at the base layer; representing other assets there requires overlay protocols built on top of the chain rather than a native ledger feature.

## What Cardano keeps: determinism and its consequences

The extensions do not cost the model its predictability, because a validator reads only its transaction, never mutable global state. A Cardano transaction names its exact inputs by reference and fixes all script arguments in advance, so its outcome is knowable before submission.

Several practical properties follow, and they are stronger than in the account model:

- **Fail-fast, off-chain checkable.** The builder can evaluate the scripts locally before submitting. If a chosen input has already been spent, validation fails without the transaction ever landing on-chain. Structural (phase-1) failures cost nothing; only script (phase-2) failures consume collateral.
- **Atomic, no partial state.** Either every condition holds and the transaction applies in full, or it fails and nothing changes. There is no equivalent of running out of gas halfway through a state change.
- **Exact fees.** Because the computation is fixed at build time, the fee is computed precisely rather than estimated.

Concurrency is inherited from the UTXO model and is explicit in both Bitcoin and Cardano: two transactions cannot consume the same UTXO, so if both try, only one succeeds and the other fails because it references a spent output. On Cardano, protocols manage this contention with UTXO fan-out (spreading state across many outputs), batching (a single transaction consuming many user orders plus a shared state UTXO), and reference inputs (reading a UTXO, such as an oracle, without consuming it). These are design patterns rather than protocol changes, and they exist precisely because the eUTXO model makes contention visible instead of hiding it behind a mutable balance.

## Side-by-side comparison

| Aspect | Bitcoin UTXO | Cardano eUTXO |
|---|---|---|
| Value representation | Discrete immutable coins | Discrete immutable coins |
| Output payload | Amount + locking script | Amount (multi-asset) + address + optional datum |
| Attached state | None | Datum (hash or inline) |
| Unlocking input | scriptSig / witness | Redeemer (typed) |
| Script visibility | Unlocking data, signature commitments, time locks | Whole transaction via script context |
| Reads other inputs/outputs | Not in general | Yes |
| Script language | Bitcoin Script, stack-based, no loops | Plutus Core / Aiken, bounded, no loops |
| Stateful contracts | Limited (pre-signed tx, time locks) | Native (consume and recreate) |
| Assets besides the coin | None at base layer | Native multi-asset |
| Determinism | Yes | Yes |
| Concurrency | Explicit (one spend per UTXO) | Explicit, with fan-out and batching patterns |

Neither model is strictly better than the other. Bitcoin's narrower script keeps its attack surface small and its purpose focused. Cardano's extensions buy programmability while retaining the coin model's determinism, at the cost of a richer and more complex development model than Bitcoin's.

## Conclusion

Cardano's eUTXO model and Bitcoin's UTXO model share a foundation: value as discrete, immutable, single-spend coins, transactions that consume whole inputs and create outputs, and an exact input-equals-output-plus-fee balance. On that base, Bitcoin runs a small, stateless, stack-based script that sees little beyond its unlocking data. Cardano adds three elements to each output and its spend, a datum, a redeemer, and the script context, and hands the validator a view of the entire transaction. That visibility is what turns a spending predicate into a mechanism for stateful contracts, covenants, and native multi-asset transfers.

The trade-off is deliberate. Cardano gains expressiveness without reading mutable global state, so it keeps the determinism, fail-fast validation, atomicity, and exact fees that the coin model provides and the account model does not. A developer moving from Bitcoin will find the coin mechanics familiar and the extensions new; a developer moving from an account chain will find the programmability familiar and the consume-and-recreate discipline new. The mindmap below collects the shared foundation, the Bitcoin baseline, and the extensions.

![Mindmap summarizing the eUTXO model against Bitcoin's UTXO model: shared foundation, Bitcoin output, the datum/redeemer/context extensions, and preserved properties]({{site.url_complet}}/assets/article/blockchain/cardano/eutxo-vs-bitcoin-utxo.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **UTXO (Unspent Transaction Output)** | a discrete, immutable coin produced by a transaction and spendable exactly once; value is held in UTXOs rather than in account balances. |
| **eUTXO (Extended UTXO)** | Cardano's model, which keeps the UTXO foundation and extends each output and its spend with a datum, a redeemer, and a script context. |
| **Account model** | the alternative design (used by Ethereum) that keeps a mutable balance per address and updates it in place; contrasted with the coin model throughout. |
| **UTXO set** | the collection of all unspent outputs at a moment in time, which constitutes the current state of the chain. |
| **Locking script (`scriptPubKey`)** | the predicate on a Bitcoin output that specifies the conditions required to spend the coin. |
| **Datum** | data attached to a Cardano UTXO, giving it persistent state; supported as a datum hash or an inline datum. |
| **Redeemer** | the typed argument a spender supplies when unlocking a script-controlled UTXO, roughly the analogue of Bitcoin's unlocking data. |
| **Script context** | the whole-transaction view (all inputs and outputs, fee, validity interval, signatories) that a Cardano validator receives, and the source of its expressive power. |
| **Covenant** | a rule constraining how a coin may be spent onward, for example requiring a specific output; natural in eUTXO via the script context, but not a deployed feature of Bitcoin Script. |
| **Deterministic validation** | the property that a transaction's outcome is knowable before submission, because a validator reads only its own transaction and never mutable global state. |

## Frequently Asked Questions

**Q: What does Bitcoin's UTXO model and Cardano's eUTXO model have in common?**

They share the entire coin-based foundation. Both track value as discrete unspent transaction outputs rather than mutable balances, both consume whole UTXOs as inputs and create new UTXOs as outputs (with change handled like physical cash), both enforce that the sum of inputs equals the sum of outputs plus fees exactly, and both treat every UTXO as immutable and spendable exactly once. The current state of each chain is its UTXO set, and each output is identified by a `(TxId, index)` reference. The differences are not in this foundation but in what an output can carry and what a script may inspect.

**Q: What are the three things the "Extended" in eUTXO refers to?**

Datum, redeemer, and script context. The datum is data attached to a UTXO, giving it persistent state. The redeemer is the typed argument a spender supplies when unlocking a script-controlled UTXO. The script context is the view of the whole transaction (all inputs, all outputs, fee, validity interval, signatories) that the ledger passes to the validator. Bitcoin has an analogue of the redeemer in its unlocking script, but nothing equivalent to a datum or a general script context.

**Q: Why can a Cardano validator enforce conditions on a transaction's outputs when a Bitcoin script generally cannot?**

Because of the script context. A Cardano validator receives the entire transaction as input, so it can read the other outputs and require, for example, that spending its UTXO also produces a specific output or recreates its own script address with an updated datum. A Bitcoin script primarily sees the unlocking data supplied to it and the signature commitments selected by SIGHASH flags; it has no general facility to read the sibling inputs and outputs of its transaction, which is why output-constraining covenants are not a deployed feature of Bitcoin Script.

**Q: How does a contract keep and update state if UTXOs are immutable?**

It never mutates a UTXO. Instead, state advances by a destroy-and-create cycle: the transaction consumes the UTXO holding the current state (with its datum) and creates a new UTXO at the same script address carrying the updated datum. The validator, reading the script context, enforces that this successor output exists and that the transition from old state to new state is legal. This is how vesting contracts, auctions, and exchange pools hold evolving state on Cardano despite every individual UTXO being immutable.

**Q: The eUTXO model adds programmability. Why does that not cost it the determinism that Bitcoin's model has?**

Because the added visibility stops at the transaction boundary. A Cardano validator can read everything in its own transaction, but it cannot read arbitrary mutable global chain state, which is the source of unpredictability in account-based systems. Since a transaction names its exact inputs by reference and fixes all script arguments at build time, its outcome is fully determined before submission: it either produces exactly the result the builder saw or fails with no effect. This is why fees can be computed exactly, scripts can be evaluated off-chain before submitting, and a transaction that references an already-spent input simply fails rather than executing against changed state. Cardano keeps the coin model's determinism while extending its expressiveness precisely because it declined to give scripts access to global state.

## References

- [Cardano developer portal](https://developers.cardano.org/)
- [The Extended UTXO Model (Chakravarty et al., IOHK)](https://iohk.io/en/research/library/papers/the-extended-utxo-model/)
- [eUTXO handbook (PDF)](https://ucarecdn.com/3da33f2f-73ac-4c9b-844b-f215dcce0628/EUTXOhandbook_for_EC.pdf)
- [Bitcoin developer guide — transactions](https://developer.bitcoin.org/devguide/transactions.html)
- [Claude Code](https://claude.com/product/claude-code)
