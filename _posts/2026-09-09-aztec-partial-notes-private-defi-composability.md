---
layout: post
title: "Partial Notes on Aztec — Deferred Completion and Private DeFi Composability"
date:   2026-09-09
lang: en
locale: en-GB
categories: blockchain defi ZKP
tags: aztec zkp privacy defi smart-contracts
description: A private function cannot read the price it needs. Partial notes split a note into a private half that fixes the payee and a public half that fixes the amount.
image: /assets/article/blockchain/aztec/2026-09-09-aztec-partial-notes-mindmap.png
isMath: false
---

A private swap on Aztec looks impossible on paper. Creating a note requires knowing its value. The value of a swap output is the exchange rate times the input, and the exchange rate is public state that a private function cannot read: private execution happens on the user's device, before the sequencer touches the block, so the current reserves are not knowable at proving time. Public execution can read them, but by then the private half of the transaction is finished and cannot create anything private.

Partial notes resolve this by splitting a note in two along the same seam. A private function commits to *who gets paid*, without saying how much. A later public function supplies *how much*, without learning who. Neither half alone is a note; together they hash to exactly the note a one-step creation would have produced.

The primitive turns out to be more general than the swap that motivated it. The same two-phase commitment backs interest accrual, vault share issuance, and a payment-endpoint pattern in which a name resolves to a list of commitments rather than to an address, so a sender can pay a recipient without learning who they are and without the recipient doing anything at payment time. It also has one sharp edge: the protocol does not enforce that a partial note is completed only once, and completing one twice usually destroys the second payment.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The constraint this exists to work around

Aztec runs private functions first, on the client, and public functions afterwards, on the sequencer. The ordering is fixed and one-directional: a private function can *enqueue* a public call, but it cannot read that call's result, because the call has not happened yet. The [protocol article]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/) covers why the split is forced rather than chosen.

For most contract logic this is merely awkward. For DeFi it is fatal in a specific way, because the same pattern recurs: the *recipient* of a value is private and known early, while the *value itself* is public and known late. A swap knows Alice should receive token2 but not how much until the reserves are read. A lending position knows whose balance accrues but not by how much until the rate is applied. A vault knows who gets shares but not how many until the total supply and assets are read.

Without a way to bridge that gap, the only options are both bad: settle publicly, which loses the privacy the chain exists for, or split the operation across two transactions, which requires the user to come back and destroys atomicity.

## Splitting a note in two

A note hash on Aztec is not a hash of a flat struct. It is built in two rounds, and partial notes exploit the boundary between them.

![The private phase commits owner and randomness and binds a completer; the public phase supplies storage slot and value to produce the final note hash]({{site.url_complet}}/assets/article/blockchain/aztec/partial-note-two-phase-concept.png)

The private phase commits to the fields only the creator knows:

```
partial_commitment = H(owner, randomness)
```

The completion phase folds in the fields that were unavailable earlier:

```
note_hash = H(storage_slot, partial_commitment, value)
```

`randomness` is fresh per note and blinds the owner, so the partial commitment is an opaque `Field` that reveals nothing about who it pays. For a `UintNote` — whose struct holds only a `value`, with `owner`, `randomness` and `storage_slot` supplied to the hash as parameters — the fields divide cleanly:

| Field | Fixed at | Bound how |
|---|---|---|
| `owner` | Creation, in private | Inside `partial_commitment = H(owner, randomness)` |
| `randomness` | Creation, in private | Same commitment; fresh per note |
| `completer` | Creation, in private | In the validity commitment `H(partial_commitment, completer)`, not in the note hash |
| `storage_slot` | Completion | Hashed into the final note hash |
| `value` | Completion | Same hash; supplied by the completer's call |

The creator fixes who gets paid and who may finalise; the completer fixes how much. Funds flow from the completing side to the owner the creator chose.

**A detail that is easy to miss and worth stating: every Aztec note is hashed this way, even when nothing is deferred.** A note created in one step with all fields known still computes a partial commitment first and then completes it immediately. That is what makes the two paths indistinguishable — a note assembled in two phases and a note assembled in one produce the same hash and behave identically thereafter. Partial notes are not a special case bolted onto the note format; the note format was designed around them.

## The completer, and why a commitment is not a capability

Once created, a partial commitment is just a field element. It can be copied, published, and handed to strangers. Completion does not re-derive or re-check its private preimage — it only supplies the public fields.

That makes the obvious design unsafe. If holding the commitment were enough to complete it, anyone could insert a note with an arbitrary `value` into the note hash tree, unbacked by any transfer, or complete it at a moment of their choosing.

The fix is to name a **completer** at creation time. The constrained private execution that creates the partial note writes a *validity commitment* to the nullifier tree:

```
validity_commitment = H(partial_commitment, completer)
```

Completion recomputes that hash with `completer` set to the caller's `msg_sender` and asserts it exists. Its presence proves two things at once: that a legitimate constrained execution created this partial note, and that this particular caller was authorised to finalise it.

Two aspects of this deserve care, because the naming misleads.

**It is not a nullifier.** The validity commitment uses its own domain separator, so it is not a note nullifier and consumes nothing. The nullifier tree is being used here purely as an append-only set whose entries support existence proofs — the same structural property that makes it useful for double-spend prevention, applied to a different question.

**Completer and payer are separate roles.** In [AIP-20](https://docs.aztec.network/developers/docs/aztec-nr/standards/aip-20), completion binds the completer to `msg_sender` but debits a separately authorised `from` account. So a contract can be the completer while a user's balance is the source of funds, which is what makes the relayer pattern below work at all.

![The token sets the completer to msg_sender and reverts unless the validity commitment exists; that is the only authorisation check, and the validity commitment is not consumed]({{site.url_complet}}/assets/article/blockchain/aztec/partial-note-completion-validation-workflow.png)

## Single use, and the sharp edge

**The protocol does not enforce single completion.** The check is existence, not consumption: the validity commitment stays in the tree after use, so a second completion of the same commitment passes every check the contract makes.

It is nonetheless unsafe, for two independent reasons, and neither produces an error:

- **Privacy.** The completion log is tagged by `H(partial_commitment)`. Two completions of the same partial note emit logs carrying the same tag, publicly linking them as payments to one recipient — which defeats the property most partial-note patterns are built to obtain.
- **Discovery, and this one costs money.** The recipient's PXE holds the partial note as a pending entry and scans for a matching completion log. On the first match it removes the pending entry. A second completion against the same commitment therefore has nothing to match against, is not found by the recipient's log processing, and the amount is most likely lost.

Treat a partial note as a one-shot object. An endpoint that accepts many payments needs many partial notes, and a commitment must be pruned from wherever it was published once it has been used. This is the failure mode most worth designing against, because the contract will not revert and the sender will see a successful transaction.

## Completing in public or in private

`PartialUintNote` can be completed in either context, and the choice determines who learns the amount.

- **`complete`**, in a public function — AIP-20's `transfer_public_to_commitment`. The storage slot and value go into a public log tagged by the commitment. Anyone watching the chain learns the amount.
- **`complete_from_private`**, in a private function — AIP-20's `transfer_private_to_commitment`. The same data goes into a private log with the same tag. The payload is plaintext, but only a party who can derive the tag can find it, and the tag derives from the commitment.

The second point has a consequence worth being explicit about, because it is a privacy property that depends on operational discipline rather than on cryptography: **in private completion the amount is hidden only for as long as the commitment is.** If the commitment is published in an onchain registry, anyone can derive the tag and read the amount out of the private log. If it is handed only to prospective senders, the amount stays hidden from everyone else.

One protocol constraint bounds what is buildable: `complete_from_private` requires the validity commitment to have settled in a *prior* transaction. A partial note cannot be created and completed in the same private transaction. Public completion has no such restriction, which is why the swap flow below creates in private and completes in public within one transaction.

## The DeFi case: a swap

The AMM contract shipped with aztec-packages is the reference use. The exchange rate lives in public state, so the output amount cannot exist during private execution.

![Alice's private call debits her balance and creates a commitment naming the AMM as completer; the enqueued public call reads the reserves, computes the output and completes the note at that value]({{site.url_complet}}/assets/article/blockchain/aztec/partial-note-amm-swap-sequence.png)

The private half debits Alice's input balance and creates a partial note that names Alice as owner and the AMM as completer. The public half — enqueued by the private half, executed by the sequencer — reads the reserves, computes the output amount, and completes the note at that value. One transaction, atomic, with the recipient hidden inside the commitment throughout.

What an observer sees is the amount, since public completion emits it in a public log. What they do not see is who it went to. For a swap that is usually the right trade: the pool's reserves move by an amount that is public anyway, so hiding the counterparty is the part that matters.

The same structure appears wherever the value arrives late. [AIP-4626](https://docs.aztec.network/developers/docs/aztec-nr/standards/aip-4626) vaults compute share counts from the total supply and total assets, both public, then mint into a private or public output context. Interest accrual and any gas-price-dependent value work identically.

## The payment-endpoint case

The second family of uses is unrelated to deferred pricing, and it is the more interesting one. Here the partial note is not waiting for a value: it is an **offer to be paid**, published in advance.

The problem it solves is that a stable address is a correlation handle. If `alice.aztec` resolves to an Aztec address, every sender and every observer of the registry can link payments to the same identifier even when the notes themselves are private, and two senders can collude to confirm they paid the same person.

The pattern removes the address from the lookup entirely. The name maps to a list of partial-note commitments.

![Alice pre-creates commitments naming a relayer as completer and publishes them under her name; Bob resolves it, signs an authwit and calls the relayer, which completes the note while Bob is debited]({{site.url_complet}}/assets/article/blockchain/aztec/partial-note-payment-endpoint-sequence.png)

Four pieces make it work:

- **The recipient pre-creates partial notes**, each `H(alice_address, randomness_i)` with fresh randomness. Her address is inside every hash, blinded, so the list reveals nothing about her.
- **The chain records who may complete each one**, as the validity commitment. Also just a hash, so no address is visible there either.
- **The lookup channel stores `alice.aztec → [c1, c2, c3, ...]`.** The commitments are opaque field elements, so this can be a hosted JSON file, an ENS text record, or an onchain registry.
- **The recipient's PXE holds the preimages** and watches for completion logs, so payments land with no action from her.

### Choosing the completer

The completer choice decides who can pay. Two options matter, and only one scales:

- **Completer set to a specific sender.** The recipient creates one note per known sender, and that sender completes it with their own funds, acting as both `from` and `msg_sender`. This needs no new contracts but requires knowing every sender's address in advance, which suits subscriptions and recurring invoices and nothing else.
- **Completer set to a relayer contract.** The recipient names a known relayer whose only job is to forward a payment into the token's completion function. Any sender can invoke it, the token sees the relayer as `msg_sender` so the validity check passes, and the sender is debited as the authorised `from`. Because the relayer needs no per-name logic, one global relayer contract could serve every endpoint on the network.

The relayer path depends on the authwit mechanism: since the token sees the relayer rather than the sender as its immediate caller, the sender signs an authentication witness authorising the relayer to call `transfer_private_to_commitment` with those exact arguments. The [account abstraction article]({{site.url_complet}}/2026/09/09/aztec-native-account-abstraction-vs-erc-4337/) covers how authwits are scoped and consumed. The relayer never holds or is pre-funded with the sender's tokens, because completion debits `from` directly.

### Where the list lives

Distribution is independent of who completes. Offchain — a hosted file, an ENS record, IPFS — keeps the name and the list size off the chain entirely, at the cost of trusting the hosting and needing a way to authenticate the result. Onchain, in a registry contract, is censorship-resistant and permits atomic lookup-and-pay in one transaction, but exposes the plaintext name, the list size and the refill cadence.

The documented recommendation for "name resolves to an unlinkable endpoint, recipient stays passive" is offchain distribution, a relayer as completer, and private completion.

### What it hides and what it leaks

The pattern hides the recipient's address from senders, the link between any two payments to the same name provided each consumes a different commitment, and, under private completion where the commitment is not public, the amount.

It leaks that the relayer contract was invoked, one completion tag per payment (which confirms a completion happened without revealing the recipient), whatever the lookup channel itself exposes, and the refill cadence if the transactions creating fresh notes are visible.

**It is also not a stealth-address scheme, and the distinction is worth keeping straight.** A stealth-address scheme lets a recipient publish one meta-address and stay passive forever, with each sender deriving a fresh one-time address non-interactively. Partial-note endpoints require the recipient to create, publish and keep refilling a finite supply of slots. If senders drain the list faster than it is refilled, the lookup returns nothing and payments fail. What is bought in exchange is an explicit, recipient-controlled supply of payment slots with a cryptographically enforced completer.

## Limitations and current status

- **Reuse is a silent failure**, not a revert. Nothing in the protocol stops a second completion, and the loss surfaces as a payment the recipient's wallet never finds.
- **Refill cadence is an operational burden** on any endpoint with unpredictable traffic. Batching many creations into one transaction reduces the per-payment cost but does not remove the need to keep the supply stocked.
- **Public completion reveals the amount.** Where that matters, private completion is required, and it in turn requires the commitment to have settled in a prior transaction and to have been kept out of public view.
- **Partial-note creation currently uses unconstrained onchain delivery.** A constrained delivery mode exists, but its log tag is not yet fully constrained and partial notes do not use it. The concepts here are stable across that change; the recipient's discovery-side code may not be.
- Aztec as a whole remains unaudited and under active development.

## Conclusion

Partial notes exist because Aztec's execution order is one-directional, and the pattern DeFi keeps hitting is one where the payee is private and known early while the amount is public and known late. Splitting the note hash at the boundary between its two commitment rounds lets each half be produced in the context that has the information for it.

The security of the arrangement rests on one check: a validity commitment binding the partial note to a named completer, written during constrained private execution and asserted to exist at completion. That check is what stops a copied commitment from becoming a licence to mint an unbacked note, and it is the only authorisation the completion path performs.

The property it does not provide is single use. Completion checks existence rather than consuming anything, so the guarantee that a commitment is used once lives in application discipline and in the recipient's pruning, not in the protocol. Given that a second completion is accepted onchain and lost offchain, that is the part of the design most in need of care from anyone building on it.

![Mindmap of Aztec partial notes covering the execution-order constraint, the two-phase commitment, the completer, single-use semantics, completion contexts, DeFi uses, payment endpoints and what leaks]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-09-aztec-partial-notes-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Partial note** | A note created with its private fields committed but its value left unset, to be supplied later by a designated completer. |
| **Partial commitment** | `H(owner, randomness)`, the private half of a note hash; an opaque field element that can be shared freely. |
| **Completion** | The step that supplies `storage_slot` and `value` and inserts the finished note hash into the note hash tree. |
| **Completer** | The address named at creation as the only party permitted to complete a given partial note. |
| **Validity commitment** | `H(partial_commitment, completer)`, written to the nullifier tree at creation and asserted to exist at completion. |
| **Completion log** | The log carrying the completed slot and value, tagged by the commitment so the recipient's wallet can find it. |
| **Payment endpoint** | An application-level use of a partial note as a pre-published, one-shot offer to be paid. |
| **Relayer contract** | A contract named as universal completer so that any sender can pay into an endpoint without being known in advance. |
| **Lookup channel** | Wherever a name resolves to its list of commitments: a hosted file, an ENS record, or an onchain registry. |
| **Pending entry** | The recipient's local record of an uncompleted partial note, removed by their PXE once a matching completion log is found. |

### Security Implementation Checklist

#### Completion authorisation

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every partial note names a completer at creation, inside a constrained private execution. | A holder of the commitment completes it with an arbitrary value, minting an unbacked note. |
| ☐ | Completion asserts the validity commitment exists, with the completer taken from `msg_sender`. | Any caller finalises the note, at a time and value of their choosing. |
| ☐ | The completer and the debited `from` account are authorised separately. | Either the relayer pattern is impossible, or the completer can spend an account that did not approve it. |
| ☐ | A relayer's authwit binds the token, commitment and amount, not merely the function. | The relayer completes a different commitment or a larger amount than the sender agreed to. |

#### Single-use discipline

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Each partial note is completed at most once; the application enforces this, since the protocol does not. | The second completion is accepted onchain and lost offchain: the recipient's PXE never matches it. |
| ☐ | A commitment is removed from its lookup channel as soon as it is consumed. | A later sender pays into a spent commitment and the funds are unrecoverable. |
| ☐ | An endpoint holds enough unconsumed commitments for expected traffic, and is refilled. | The lookup returns nothing and payments fail, or senders reuse a consumed commitment. |
| ☐ | Distinct payments consume distinct partial notes. | Completions share a log tag, publicly linking them as payments to one recipient. |

#### Amount and recipient privacy

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Where the amount must stay private, completion runs in a private function. | Public completion emits the value in a public log, visible to everyone. |
| ☐ | Where private completion is used, the commitment is not published where observers can read it. | Any holder of the commitment derives the log tag and reads the amount. |
| ☐ | Randomness is fresh for every partial note. | Two commitments become linkable, or the owner is recoverable from the hash. |
| ☐ | The flow does not require the recipient to act at payment time. | Recipient interaction reintroduces the correlation the pattern removed. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| A partial note cannot be created and completed in the same private transaction. | Use public completion for single-transaction flows; split across transactions when private completion is required. |
| Completion does not consume the validity commitment. | Do not rely on a revert to prevent double completion; track consumption in the application. |
| The completion log tag derives from the commitment, not from the recipient. | Treat publication of a commitment as publication of the right to read that payment's amount. |
| A commitment is an opaque `Field` and can be stored anywhere. | Store lists as plain arrays; no special encoding or onchain structure is required. |
| Completion debits an authorised `from`, which need not be the completer. | A relayer needs no float and should never be pre-funded with sender tokens. |
| The recipient must prune consumed commitments themselves. | Build pruning into the wallet flow; the PXE knows when each note was completed. |
| Partial-note creation currently uses unconstrained onchain delivery. | Expect the recipient-side discovery code to change when constrained tagging lands. |

## Frequently Asked Questions

**Q: Why can a private function not simply read the exchange rate and create a complete note?**

Because private execution runs on the user's device before the sequencer processes the block, so there is no current public state to read. Any rate the circuit assumed could have changed by the time the transaction lands.

The ordering is also one-directional: a private function can enqueue a public call but cannot see its result, since that call runs afterwards. So the amount is unavailable in the only context that can create private state, and the context that knows the amount runs after private execution has finished.

**Q: What stops someone who obtains a commitment from completing it themselves?**

The validity commitment. When the partial note is created, a constrained private execution writes `H(partial_commitment, completer)` to the nullifier tree. At completion the token recomputes that hash using the caller's `msg_sender` as the completer and asserts the result exists in the tree.

A stranger holding the commitment computes a different hash, which is not in the tree, so their completion reverts. The commitment alone is therefore not a capability — it identifies a note, but the right to finalise it was fixed by whoever created it.

**Q: If the validity commitment lives in the nullifier tree, does completing a partial note nullify something?**

No. The validity commitment uses its own domain separator, so it is not a note nullifier, and completion checks that it exists rather than consuming it. Nothing is spent by the check.

The nullifier tree is simply the structure Aztec has for an append-only set supporting efficient existence and non-membership proofs. Double-spend prevention is its usual application; this is a second, unrelated use of the same property.

**Q: A recipient publishes one commitment and two senders each pay into it. What happens?**

Both transactions succeed onchain, because completion only checks that the validity commitment exists and does not consume it. Neither sender sees an error.

The recipient receives one payment. Their PXE held the partial note as a pending entry, matched the first completion log and removed the entry; the second completion has nothing left to match against, so the wallet never finds it and the amount is most likely lost. The two completions also carry the same log tag, which publicly links them as payments to the same recipient. This is the reason each commitment must be treated as one-shot and pruned once used.

**Q: How does a payment endpoint let a stranger pay without the recipient knowing them in advance?**

By naming a relayer contract as the completer instead of a specific sender. The recipient creates commitments with `completer = relayer` and publishes them; any sender calls the relayer, which forwards into the token's completion function.

The token sees the relayer as `msg_sender`, so the validity check passes, while the sender is debited as the separately authorised `from` — which they authorise with an authwit, since the token does not see them as the immediate caller. The relayer needs no per-recipient logic and never holds the sender's funds, so one deployment can serve every endpoint on the network.

**Q: Private completion is described as hiding the amount, yet the log payload is plaintext. How is it private?**

The payload is not encrypted; it is hidden by being hard to locate. The log is tagged with a value derived from the partial note's commitment, and finding it means deriving that tag, which means holding the commitment.

So the amount's privacy is exactly as strong as the commitment's secrecy. Handed only to prospective senders, the amount is hidden from everyone else. Published in an onchain registry, anyone who reads the registry can derive the tag and read the amount. This is an operational property rather than a cryptographic guarantee, and it is the main reason the recommended endpoint pattern distributes commitments offchain.

## References

### Aztec documentation

- [Partial notes](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/advanced/partial_notes) — the two-phase commitment, the completer, and single-use semantics
- [Partial notes as payment endpoints](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/advanced/partial_notes_as_payment_endpoints) — the naming-service pattern, completer choice and distribution
- [AIP-20: Fungible Token](https://docs.aztec.network/developers/docs/aztec-nr/standards/aip-20) — commitment-based transfers and recursive note consumption
- [AIP-4626: Tokenized Vault](https://docs.aztec.network/developers/docs/aztec-nr/standards/aip-4626) — share conversion across private and public contexts
- [Escrow](https://docs.aztec.network/developers/docs/aztec-nr/standards/escrow) — salt-based authorisation and deterministic per-user escrows
- [Authentication Witnesses](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/authentication_witnesses) — how a relayer is authorised to debit a sender
- [State Management](https://docs.aztec.network/developers/docs/foundational-topics/state_management) — notes, nullifiers and the hybrid state model
- [Call Types](https://docs.aztec.network/developers/docs/foundational-topics/call_types) — the private-then-public ordering the pattern works around
- [Note Discovery](https://docs.aztec.network/developers/docs/foundational-topics/advanced/storage/note_discovery) — tagging, and how a recipient finds a completion log
- [Storage Slots](https://docs.aztec.network/developers/docs/foundational-topics/advanced/storage/storage_slots) — how slots enter the note hash
- [Limitations](https://docs.aztec.network/developers/docs/resources/considerations/limitations) — current development status

### Source

- [AztecProtocol/aztec-packages](https://github.com/AztecProtocol/aztec-packages/tree/v5.2.0/noir-projects/noir-contracts/contracts/app/amm_contract) — the AMM contract using partial notes for swap settlement, at tag v5.2.0
- [noir-projects/aztec-nr/uint-note](https://github.com/AztecProtocol/aztec-packages/blob/v5.2.0/noir-projects/aztec-nr/uint-note/src/uint_note.nr) — `UintNote` and `PartialUintNote`, at tag v5.2.0
- [defi-wonderland/aztec-standards](https://github.com/defi-wonderland/aztec-standards) — the canonical AIP-20, AIP-721 and AIP-4626 implementations
- [aztec-packages issue #14565](https://github.com/AztecProtocol/aztec-packages/issues/14565) — constrained tagging and handshaking, which will affect partial-note discovery

### Related articles

- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
- [Native Account Abstraction on Aztec, Compared with ERC-4337]({{site.url_complet}}/2026/09/09/aztec-native-account-abstraction-vs-erc-4337/)
- [Aztec: A Privacy-First Layer 2 for Ethereum]({{site.url_complet}}/2025/10/29/aztec-architecture-overview/)
- [RAILGUN: Privacy Infrastructure for DeFi]({{site.url_complet}}/2025/10/28/railgun-overview/)
- [Understanding zk-SNARK: A Deep Dive into Zero-Knowledge Proofs]({{site.url_complet}}/2025/07/29/zk-snark-overview/)
