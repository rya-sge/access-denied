---
layout: post
title: "CIP-113 Programmable Tokens on Cardano"
date:   2026-08-26
lang: en
locale: en-GB
categories: blockchain
tags: cardano cip aiken eutxo smart-contracts stablecoin securities
description: How CIP-113 puts issuer-enforced transfer rules on Cardano native assets with no hard fork. Shared custody address, sorted-list registry, seizure scope.
image: /assets/article/blockchain/cardano/cip-113-programmable-tokens-cardano.png
isMath: false
---

A Cardano native asset moves whenever its holder signs for it. That is the point of the design, and it is also the reason a regulated instrument cannot be issued as one. The issuer of a sanctioned-asset-screened stablecoin or a tokenized security stays legally accountable for the instrument after issuance: they have to be able to block a transfer to a sanctioned party, and to freeze or seize a holding when a court orders it. A plain native asset offers no mechanism for either.

[CIP-113](https://github.com/cardano-foundation/CIPs/pull/444) closes that gap without changing the ledger. Programmable tokens remain native assets, minted by an ordinary minting policy and tracked by the ledger like any other. What changes is where they live: every programmable token sits at a single shared script address, and the stake credential of the UTxO, rather than its payment credential, records who owns it. Because one payment credential covers every holder, one spending validator runs on every movement, and that validator can consult a registry, invoke the token's own rule set, and refuse.

This article works through the on-chain design as it stands in the Cardano Foundation's [Aiken]({{site.url_complet}}/2026/07/16/aiken-smart-contracts-cardano/) implementation: the custody model and what it costs integrators, the validator set and the withdraw-zero dispatch that keeps it affordable, the sorted-list registry and its two proof shapes, the boundaries of administrative authority, and the restructuring action that keeps a freeze from taking a holder's unrelated assets with it. Where the repository's own documentation has drifted from the code, the code is what is described here, and the drift is flagged.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The problem CIP-113 is answering

The gap is old enough to have its own Cardano Problem Statement. [CPS-0003 (Smart Tokens)](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0003/README.md) states it directly: Cardano native assets have no mechanism for issuer-defined conditions on transfer, and every workaround trades away something the ecosystem needs.

- **Centralised custody** reintroduces the intermediary and the counterparty risk that on-chain issuance was meant to remove.
- **Off-chain enforcement** watches transfers but cannot stop them, so it is a reporting tool rather than a control.
- **A smart-contract wrapper** does enforce rules, but the wrapped asset stops being a native asset and loses the wallet, explorer, and DEX support that comes with one.
- **A separate chain or sidechain** fragments liquidity and pushes the problem into a bridge.

Account-model chains solve this at the token contract. On Ethereum, [ERC-3643](https://eips.ethereum.org/EIPS/eip-3643) and comparable permissioned-token designs put a compliance hook inside `transfer`, because on an account ledger the token contract is the single chokepoint through which every movement passes. Cardano's extended UTXO model has no such chokepoint: a native asset has a minting policy, and the minting policy is consulted only when the supply changes. Once minted, the asset moves under the ordinary ledger rules for spending a UTxO, and no script of the issuer's is involved.

CIP-113 manufactures the missing chokepoint out of the address structure itself, which is why the design reads so differently from its account-model counterparts.

## The custody model

A Cardano address is a payment credential paired with an optional stake credential. Spending authority follows the payment credential; the stake credential normally decides where the delegation and rewards go. CIP-113 keeps the first half constant and repurposes the second.

Every programmable token is held at an address whose payment credential is the `programmable_logic_base` script hash. The stake credential slot carries the owner: a verification-key hash for a wallet holder, or a script hash when a dApp holds the tokens. A transfer rewrites the stake credential and leaves the payment credential untouched.

```
Before:  addr(programmable_logic_base, stake_alice) -> 100 USDX
After:   addr(programmable_logic_base, stake_bob)   -> 100 USDX
```

![Three programmable-token UTxOs sharing one payment credential, the programmable_logic_base script hash, while each carries a different stake credential that identifies its owner]({{site.url_complet}}/assets/article/blockchain/cardano/cip113-shared-custody-address-concept.png)

Phil DiSarro, who wrote the reference implementation this codebase descends from, described the result in a [CIP-113 review comment](https://github.com/cardano-foundation/CIPs/pull/444#issuecomment-4084863264) as "a mini ledger within Cardano". The metaphor earns its keep, because most of the architecture follows from it. A ledger needs a record of what it tracks, which becomes the on-chain registry. It needs rules for what makes a movement valid, which become the substandard validators. And it needs a boundary nothing crosses unchecked, which becomes the invariant that no registered policy's tokens ever leave the shared address.

### The credential slot is polymorphic, and that matters downstream

The on-chain validators never ask what kind of key produced a credential hash. They branch on the `Credential` constructor only:

```aiken
when stake_cred is {
  VerificationKey(pkh) -> is_signed_by(tx, pkh)
  Script(_hash) -> is_script_invoked(tx, stake_cred)
}
```

Three things can therefore sit in the slot, and all three are valid on-chain:

- **A stake key hash.** The default convention, because it aligns with Cardano's existing address model.
- **A payment key hash.** Necessary for enterprise wallets, such as an exchange, that operate addresses with no stake part.
- **A script hash.** Necessary whenever a DEX, lending market, escrow, or treasury holds the tokens.

Which one a given deployment uses is an off-chain convention, not an on-chain rule. A wallet that builds the query address with the wrong one sees a zero balance and cannot explain why, and an indexer cannot tell a payment key hash from a stake key hash by inspecting the address, since both are 28-byte blake2b-224 digests under the same constructor.

### What the model costs

Nothing here requires a hard fork, and the tokens are native assets at the ledger level throughout. The cost lands entirely on tooling. A wallet that queries by payment credential gets every holder's tokens at once rather than the user's; an explorer that does the same attributes the entire supply to one script address; a DEX contract has to become invokable as a stake validator before it can hold anything. The design trades ledger changes for integration work, and it is worth being explicit that the trade is real rather than free.

## The validator set

Twelve validators make up the deployed protocol. What organises them is the split between scripts the ledger runs once per spent input and scripts it runs once per transaction.

![The CIP-113 validator set: programmable_logic_base dispatching to the transfer, third_party and unfracking delegates, alongside the registry, issuance and protocol-coordination validators, with the pluggable substandard scripts below]({{site.url_complet}}/assets/article/blockchain/cardano/cip113-validator-architecture-concept.png)

`programmable_logic_base` is the spending validator on every programmable-token UTxO, so the ledger runs it once for each such input in a transaction. Everything expensive has been moved out of it. What remains is a dispatcher:

```aiken
validator programmable_logic_base(params_policy: PolicyId) {
  spend(
    _datum: Option<Data>,
    redeemer: BaseSpendRedeemer,
    _own_ref: Data,
    self: Transaction,
  ) {
    let check = fn(params_idx: Int, wdrl_idx: Int, cred_of) {
      let fields <- params.with_protocol_params_fields(
        self.reference_inputs,
        params_policy,
        params_idx,
      )
      let Pair(witnessed, _) = list.expect_at(self.withdrawals, wdrl_idx)
      (witnessed == cred_of(fields))?
    }

    when redeemer is {
      SpendViaTransfer { params_idx, wdrl_idx } ->
        check(params_idx, wdrl_idx, params.transfer_cred_field)
      SpendViaThirdParty { params_idx, wdrl_idx } ->
        check(params_idx, wdrl_idx, params.third_party_cred_field)
      SpendViaUnfracking { params_idx, wdrl_idx } ->
        check(params_idx, wdrl_idx, params.unfracking_cred_field)
    }
  }

  else(_) {
    fail
  }
}
```

The redeemer names one of three delegates and says where that delegate's credential sits in the transaction's withdrawal map. The base validator reads the delegate's current credential out of the protocol-parameters datum, jumps straight to the witnessed withdrawal entry, and checks one equality. That is the whole of it.

The three arms differ only in *which* datum field they read, and that field accessor is passed to `check` as a function argument. The shaping is deliberate rather than stylistic: this validator runs once per programmable input, so anything left inside an arm is paid per input, and anything duplicated across arms is paid in reference-script bytes on every transaction that loads the script. Hoisting the shared work into one closure pays for itself on both axes.

### Why the work lives in a withdraw-zero validator

The Cardano ledger executes a stake validator when a transaction withdraws from its reward address, and the withdrawal may be zero. The zero-lovelace withdrawal has no economic effect; it exists purely to force the script to run with the full transaction in scope. Because the ledger runs a stake validator once per transaction regardless of how many inputs the transaction spends, the pattern converts per-input work into per-transaction work.

That is the entire reason the registry lookups and the value-containment check live in the `transfer` validator rather than in `programmable_logic_base`. A transfer consolidating eight UTxOs runs the dispatcher eight times and the expensive validation once.

The three delegates are separate scripts rather than three arms of one script, and the motive is reference-script fees. Every transfer references the `transfer` script, so every byte of it is paid for on every transfer, permanently. Splitting the seizure logic and the restructuring logic into their own validators dropped the measured reference-script footprint of a transfer transaction from 3659 to 3045 bytes, of a seizure from 3659 to 2674, and of a restructuring transaction from 5491 to 2700. Exactly one delegate is loaded per transaction; a transfer never carries the seizure script's bytes.

### The indexed lookup, and the assumption underneath it

Resolving the delegate by a redeemer-supplied index instead of scanning the withdrawal map drops one credential comparison per entry walked, on every input. The repository's own benchmark puts the indexed path at roughly 1.1M CPU per position against 2.7M for the scan, breaking even around position three and saving about 19M CPU at width 16, position 15. A wrong index resolves to some other credential and fails the equality, so a dishonest witness can only invalidate its own transaction.

One caveat is worth stating because the code does not enforce it. "A wrong arm fails" holds only while the protocol-parameters datum carries three pairwise-distinct delegate credentials. Neither the genesis mint nor the upgrade path checks distinctness, so it is a deployment and upgrade-authority responsibility. If two of the three were ever set equal, both arms would resolve to the same script and that script would have to dispatch internally. The repository pins the behaviour with a test named `plb_equal_delegate_creds_collapse_the_arms` rather than pretending the property is guaranteed.

## The on-chain registry

The registry answers one question: given a policy ID, is it a programmable token, and if so, which scripts govern it? It is a sorted linked list of UTxOs, each marked with an NFT from a one-shot minting policy and carrying a `RegistryNode` inline datum.

![The registry linked list from origin node through two policy nodes to the 30-byte sentinel, with a TokenExists proof pointing at a matching node and a TokenDoesNotExist proof pointing at a covering node]({{site.url_complet}}/assets/article/blockchain/cardano/cip113-registry-linked-list-concept.png)

At the analyzed revision the node carries seven fields:

```aiken
pub type RegistryNode {
  key: ByteArray,                                 // the registered policy id
  next: ByteArray,                                // next key in sorted order
  minting_logic_script: Credential,               // issuance and lifecycle authority
  transfer_logic_script: Credential,              // transfer rules
  third_party_transfer_logic_script: Credential,  // seizure and freeze enforcement
  unfracking_logic_script: Credential,            // restructuring hook, unset means forbidden
  global_state_cs: ByteArray,                     // optional global state NFT, e.g. a denylist
}
```

### Two proof shapes, one reference input each

Sorting is what makes the structure cheap to query. A transaction proves membership by pointing at a node whose `key` equals the policy in question; it proves non-membership by pointing at the *covering* node, the one where `node.key < policy < node.next`. Because the list is sorted and complete, a covering node is a proof that no node with the target key exists.

Non-membership is not an edge case here, it is the common path. A programmable-token UTxO also holds ADA and may hold ordinary native assets, and the `transfer` validator demands one proof per distinct policy in the inputs. A covering-node proof is how the validator learns that a given policy is not its business and skips it, rather than rejecting the transaction for carrying an unregistered asset.

The list terminates in a 30-byte sentinel of `0xff` bytes rather than a 28-byte one. Plutus compares bytestrings byte by byte and treats the longer string as greater when the shared prefix matches, so a 30-byte value sorts above every possible 28-byte policy ID. Normalising it to 28 bytes would collide with a hypothetical real policy ID of all `0xff`, and the code says so in a comment.

### Registration binds the policy ID to a credential

A registry entry is only trustworthy if a policy cannot register itself under someone else's rules. The binding is cryptographic. The issuance minting policy is a parameterized script, and the `IssuanceCborHex` reference NFT holds the compiled template as a prefix and a postfix. To register a policy under a given credential, `registry_mint` reconstructs the script bytes from that credential's hash and hashes the result:

```aiken
pub fn apply_hashed_parameter(
  prefix: ByteArray,
  postfix: ByteArray,
  hashed_param: ByteArray,
) -> ByteArray {
  let version_header = #"03"
  let script_bytes = builtin.append_bytearray(
    version_header,
    builtin.append_bytearray(
      prefix,
      builtin.append_bytearray(hashed_param, postfix),
    ),
  )
  builtin.blake2b_224(script_bytes)
}
```

If the result does not equal the policy ID being registered, the insertion fails. Collision resistance of blake2b-224 therefore forces `minting_logic_script` to be the credential the policy was actually parameterized with, so that field cannot lie. The constructor tag distinguishing a script credential from a verification-key credential is baked into the prefix by the off-chain bootstrap, so variant agreement is enforced by the same derivation.

### The cost of a linked list: registration contention

Inserting a node spends the covering node and re-creates it, and an in-place node update does the same. This is intrinsic to a linked list, and it has a concurrency consequence that transaction builders have to handle.

Registry proofs cite a node as a *reference input*, and a reference input has to be a live UTxO at validation time. So a transfer whose proof points at node `N` is invalidated the moment another transaction spends `N`, whether to insert after it or to update it. The transfer has to be rebuilt against `N`'s new output reference.

The practical consequences are a retry requirement in every builder, and a mild griefing surface: an actor who repeatedly registers around a particular node can transiently block transactions that depend on it. The project classifies this as an informational limitation and declines the heavier remedies, such as a Merkle-tree registry that proves membership without consuming a node, on the grounds that the added complexity is disproportionate to an impact that is neither a custody nor an escape risk. The mitigation is off-chain: resolve the covering node at build time, and on failure re-resolve against the current registry rather than retrying the same reference.

### There is no de-registration

The lifecycle path supports update only. A node cannot be removed, and it cannot be flagged as retired. The reason is the custody invariant: deleting a node would make its policy unregistered, at which point covering-node proofs would let its tokens leave the shared address freely and the guarantee would be void retroactively. Registration is a one-way door by construction.

## How a transfer validates

With the pieces in place, an ordinary transfer is legible end to end.

![Sequence of a programmable-token transfer: the base validator checking the witnessed withdrawal index, the transfer validator authenticating parameters, walking registry proofs and checking value containment, then the substandard transfer logic approving]({{site.url_complet}}/assets/article/blockchain/cardano/cip113-transfer-flow-sequence.png)

The transaction carries two zero-lovelace withdrawals, one for the `transfer` validator and one for the token's own `transfer_logic_script`, plus two reference inputs, the protocol-parameters UTxO and the registry node. The base validator runs per input and checks its one equality. The `transfer` validator then runs once and enforces three things over the whole transaction.

- **Ownership.** Every input at the shared payment credential has to be authorised by its own stake credential, by signature for a verification key or by a withdraw-zero invocation for a script. One unauthorised input fails the transaction, which is what stops a transfer from sweeping up a stranger's UTxO.
- **Registry resolution.** One proof per distinct policy in the inputs, in ascending policy order. A `TokenExists` proof additionally requires that node's `transfer_logic_script` to appear in the withdrawals, which is the step that actually invokes the token's rules.
- **Value containment.** The programmable-token value across outputs at the shared payment credential has to be at least the value drawn from authorised inputs. Tokens can move between owners but not out of the address space.

Only then does the substandard's own logic run, and it can refuse for any reason it likes, a denylist hit being the canonical one.

### Indices in redeemers are a build-time obligation

Three separate index hints appear across the redeemers: `params_idx` for the protocol-parameters UTxO, `registry_node_idx` (or a `node_idx` inside each proof) for registry nodes, and `wdrl_idx` for the delegate credential. All three are positions into the *ledger's canonical ordering*, not the order the builder added things.

Reference inputs are sorted by output reference, meaning transaction ID then output index. Withdrawals are ordered with every script credential before every verification-key credential, and bytewise by hash within each group. Neither matches insertion order, and the withdrawal ordering does not match bech32 string order either. A builder that computes these positions from its own list gets them wrong, and the failure surfaces as a validator rejection rather than anything more descriptive.

The design is deliberately self-validating rather than trusting: a wrong `params_idx` fails the NFT authentication, a wrong `wdrl_idx` fails the credential equality, and a wrong node index fails the proof. A dishonest hint costs its author a transaction and gains nothing.

## Administrative authority and its limits

The third-party path is the one on which someone other than the holder moves the holder's tokens, so its boundaries deserve more attention than the rest of the design. Three questions set them: what the base layer guarantees unconditionally, what it hands to the token's own rules, and what it declines to decide at all.

![Activity flow of a third-party action, from the SpendViaThirdParty dispatch through the per-pair identity, anti-injection and lovelace-ratchet checks to the aggregate conservation test that keeps seized tokens inside the shared address]({{site.url_complet}}/assets/article/blockchain/cardano/cip113-third-party-action-activity.png)

### What holds unconditionally

A third-party action is a forced *transfer*, not only a removal. Each spent programmable-token input is paired positionally with a continuing output, and on the subject policy the amount may be decreased, removed entirely, increased, or left unchanged. What the framework pins is everything else:

- **The subject policy's own third-party script is invoked.** The framework never authorises a seizure by itself; it requires the credential the issuer declared at registration.
- **Address, datum, and reference script are byte-identical across each pair.** A seizure cannot move a UTxO to a different owner, rewrite its state, or attach and strip reference scripts.
- **Every non-subject policy is conserved byte for byte.** No other token can be injected, redirected, split, or destroyed by an action aimed at the subject policy.
- **The paired input must already hold the subject policy.** An administrator can neither conjure the policy onto a UTxO that never held it nor drag an unrelated UTxO into the action.
- **Output lovelace has to be at least input lovelace.** ADA is not a programmable asset, so the ratchet is one-way: an administrator may top a UTxO up but never drain it.
- **The aggregate reconciles against mint and burn.** The subject total across all outputs at the shared address accounts for every seized input plus any minting or burning, so amounts are redistributed rather than created or made to escape.

The lovelace ratchet arrived by audit rather than by design. The original code required exact value equality across the pair, which pinned the lovelace along with everything else. A rise in the protocol's minimum-UTxO calculation above an existing UTxO's balance would then have made every third-party action on that UTxO permanently unsatisfiable, since equality forbade the top-up that would have fixed it. The fix peels the ADA entry off both sides and requires only that the output be greater than or equal. Accepting less is what would let an administrator drain a non-programmable asset, which is why the ratchet runs one way and not the other.

### One policy per transaction

The third-party redeemer resolves exactly one registry node, so a single action can touch many UTxOs of one policy but cannot atomically seize across two policies. A multi-policy variant was prototyped and rejected: making the path multi-policy taxed the execution cost and script size of the common single-policy case more than the capability was judged to be worth. A compliance operation spanning several policies needs sequential transactions, with the exposure window that implies. The limitation is accepted and permanent.

### Fragmentation is not prevented either

An action operates only on the inputs the transaction actually spends. A holder's balance may be spread across many UTxOs, and nothing forces consolidation, so a holder can fragment a balance to push a full seizure past the transaction-size or execution-budget limit. This is inherent to the eUTXO model rather than a defect of the framework: there is no account-style "seize the whole balance in one call" to reach for. An administrator has to plan for multiple transactions.

### Freeze and extraction are not symmetric

Two administrative powers exist, and only one of them is gated:

- **Freeze**, meaning a refusal to authorise a spend, is unconditional. A substandard's transfer logic can always decline.
- **Extraction**, meaning removal of tokens through the third-party path, is the conditional power.

The asymmetry is safe because hiding assets behind a non-cooperating script is self-freezing rather than evasion. Tokens parked under a script that refuses to authorise spends become unspendable by the holder too. There is no construction that both evades seizure and keeps the tokens usable, so gating extraction while leaving freeze unconditional does not open a hole.

### Who is seizable is not a framework decision

The only on-chain signal of who holds a token is the UTxO's stake credential, and it does not carry enough information. A verification-key credential is a directly held wallet, and extraction is straightforward. A script credential is ambiguous: it might be a smart-contract wallet, or it might be a lending pool holding the tokens as collateral against a borrower's debt with other lenders' claims behind it. The two are indistinguishable as credentials, and any hard-coded framework rule is wrong for someone.

So the framework ships primitives and leaves the policy to the substandard, with a stated guiding principle: the third-party path may freeze anywhere, but should not unilaterally extract from a UTxO whose validator has not opted in. Two patterns implement that at the substandard level. An **allowlist** makes a script-staked input seizable only if its stake script is on an issuer-maintained list of known protocols. **Consent** makes it seizable only if that script's own withdraw-zero appears in the same transaction, so the protocol agrees to the seizure. Both gate extraction only, and freeze stays unconditional under either.

### A note on the documentation drift

The repository's architecture and control-scope documents describe a `protected_prefixes` field on the registry node: an append-only list of [CIP-67](https://cips.cardano.org/cip/CIP-0067) label prefixes that a third-party action may never seize or burn, intended to shield [CIP-68](https://cips.cardano.org/cip/CIP-0068) reference NFTs and [CIP-102](https://cips.cardano.org/cip/CIP-0102) royalty tokens from an administrator sweeping up the metadata infrastructure alongside the user token.

That field is not in the code at the analyzed revision. It was added and then removed, with the reasoning recorded in the removal commit: prefix protection is substandard responsibility rather than framework policy, because the framework already guarantees that the subject policy's third-party logic script runs on every action, so a substandard can protect its own reference tokens without a framework field. The removal took out the datum field, its accessor, the registry well-formedness and append-only checks, the per-pair protected-subset equality, and thirteen dedicated tests. Anyone reading the published documents alongside the code should treat the prefix machinery as historical. The scope boundary it enforced is still real; it now lives one layer up.

## Unfracking, and the freeze-for-ransom problem

A single UTxO can hold several policies at once, and a freeze applies to the UTxO rather than to one asset in it. If a UTxO holds a legitimate token and a frozen one, the legitimate token and the UTxO's ADA are locked with it until the frozen policy permits a spend. Nothing is stolen; everything sharing the UTxO is held hostage.

That is the mechanism behind a freeze-for-ransom scam. An attacker gets a freezable token co-located in a UTxO with a victim's real assets, then declines transfers until paid. The attacker cannot place a victim's asset into a UTxO directly, since they do not hold it. The co-location happens on the victim's own side, when a wallet merges an unsolicited token into a UTxO with real assets during coin selection or change construction.

Wallet hygiene is the first defence, and three rules carry most of it: keep programmable tokens in single-policy UTxOs, keep the ADA in such a UTxO at or near the minimum so a freeze holds as little hostage as possible, and never auto-consolidate unsolicited or unknown programmable-token UTxOs. Detection helps too, and the registry supplies signals an ordinary spam filter does not have. A *registered* co-located token with unknown transfer logic is the loud signal, because only a registered token can lock the shared UTxO. An unregistered one moves under a covering-node proof and cannot freeze anything, though it may still be spam.

Prevention is not a cure, though, so the protocol provides one.

![Activity flow of an unfracking action, from the registry hook check and the empty-mint and single-owner requirements through the per-pair byte identity and full strip to the owner-side conservation equality]({{site.url_complet}}/assets/article/blockchain/cardano/cip113-unfracking-workflow.png)

The `unfracking` validator lets a holder restructure the UTxOs they already own for **one** registered policy, moving that policy's tokens into their own UTxO while everything else stays put. The frozen policy's transfer logic is never consulted, which is the whole point: the separation cannot be blocked by the party doing the freezing. Six invariants keep it from becoming a bypass of the transfer path.

- **Registry-gated, default deny.** The acted policy's `unfracking_logic_script` withdraw-zero must be invoked. An unset hook is the empty verification key, and no ledger transaction can carry a withdrawal keyed by an empty hash, so an issuer who declares nothing forbids unfracking for their policy outright. Issuers opt in explicitly, and a token carrying stateful datums gets its restructuring constraints enforced by its own hook.
- **No minting.** `tx.mint` has to be empty. Unfracking is strictly value-preserving; changing supply is the issuance policy's job.
- **Single owner.** Every input at the shared address carries the same full address, pinned by the first one. The owner authorises once, by signature or by their script's withdraw-zero. Restructuring across owners would be a transfer in disguise, bypassing the transfer logic.
- **Per-pair identity.** Address, datum, and reference script are byte-identical across each pair, as are all non-acted policies. A co-resident policy's stateful datum survives another policy's unfracking untouched.
- **Full strip.** The acted policy is present on the input and absent from the continuing output. A partial strip is rejected, because an output still carrying the policy would still need that policy's transfer proof on every future spend, which in the freeze case means still stuck.
- **Conservation by strict equality.** The acted policy's total across the owner's non-paired outputs equals its total across the inputs. Counting only owner-address outputs is what forces the tokens to land back with the owner, since routing any to another stake credential leaves the owner-side total short.

ADA is deliberately unconstrained here, for the same reason the third-party path uses a ratchet rather than equality: the owner authorised the action, ADA is not a programmable asset, and an equality would recreate the minimum-UTxO hazard.

The upshot for users is simple: the scam only works if the tokens cannot be separated. A wallet that avoids co-location and supports this separation defeats it, and there is no reason to pay.

## Upgradability: what can change, and who changes it

Two independent mutation surfaces exist, with different authorities and different blast radii.

**Protocol-level.** The coordination UTxO holds a one-shot protocol-parameters NFT and a datum that, at the analyzed revision, carries seven fields:

```aiken
pub type ProgrammableLogicGlobalParams {
  registry_node_cs: PolicyId,     // 0 - registry NFT policy
  prog_logic_cred: Credential,    // 1 - the shared payment credential
  transfer_cred: Credential,      // 2 - live transfer validator
  third_party_cred: Credential,   // 3 - live third-party validator
  unfracking_cred: Credential,    // 4 - live unfracking validator
  upgrade_cred: Credential,       // 5 - upgrade authority
  max_inline_datum_bytes: Int,    // 6 - datum-size bound on PLB outputs
}
```

Fields two through four are what makes the delegates swappable in place. The base validator's hash anchors every programmable-token address, so redeploying it would move everyone's tokens; rewriting a credential in this datum replaces a delegate without touching a single holder. Field five names the authority permitted to rewrite the datum, and making it a datum field rather than a script parameter is what lets the authority itself be replaced later, a federated multisig now and a governance validator afterwards, without moving the coordination UTxO. The field ordering is not cosmetic either: the fields are sorted by read frequency, and `max_inline_datum_bytes` was appended last precisely so that adding it left every existing accessor at its original traversal depth.

That last field exists for a reason worth following. A seizure has to reproduce the paired input's datum byte for byte on the continuing output, so an unbounded datum lets a holder inflate the seizure transaction past the maximum transaction size, or short of that, collapse how many UTxOs an issuer can process at once. The holder pays nothing for the tactic, because the transfer path never pairs inputs to outputs and so never reads the datum. Bounding the datum at creation is what keeps every UTxO seizable later.

**Token-level.** A registry node's `transfer_logic_script`, `third_party_transfer_logic_script`, `unfracking_logic_script`, and `global_state_cs` are mutable through the lifecycle path, authorised by the node's `minting_logic_script`. Its `key`, `next`, and `minting_logic_script` are frozen.

Two consequences follow, and integrators need both. The change is **retroactive**, governing every existing holder's tokens on their next spend, and it can **flip credential type** between script and verification key, moving a token between script-enforced and signature-gated logic. The registry node is therefore the live source of truth. Caching a token's logic credentials as facts established at registration is a correctness bug, not an optimisation.

One separation is enforced structurally. `registry_spend` is the sole spender of every registry node, and it forbids minting or burning that node's own token in the same transaction. A registry lifecycle operation can therefore never double as an issuance of the same policy; the two are always separate, independently authorised transactions. The authorising credential is nonetheless *shared* between issuance and lifecycle, so by default whoever can mint can also update the node. A substandard that needs those to be distinct powers has to separate them inside its own issuance logic.

## The integration surface

The framework's cost lands on integrators, so it is worth collecting what each audience actually has to change.

**Wallets** query by the full address rather than by payment credential, since the payment credential alone returns every holder's tokens. They sign with whichever key matches the credential in the stake slot, which is not necessarily the payment key. They add the two withdraw-zero invocations and the two reference inputs, compute three ledger-ordered indices, and resolve the registry node fresh at build time.

**Indexers and explorers** decompose holdings by stake credential, or the entire supply appears to belong to one script address. They treat script credentials as a distinct owner type, since a DEX or treasury holding tokens is invisible to an indexer that only tracks verification keys. And they distinguish the three transaction kinds by the delegate invoked, because a third-party action is a compliance event rather than a voluntary transfer and should not be displayed as one.

**dApps** face the largest change. Holding programmable tokens means the dApp's script hash occupies the stake credential slot, so the script has to implement the `withdraw` purpose and its stake address has to be registered on-chain before any zero-lovelace withdrawal can occur. That registration is a ledger requirement rather than a validator one, which means the failure arrives as a bare ledger rejection with no validator trace, and it is a reliable source of confusion. A dApp's withdraw handler also gets invoked both for programmable-token authorisation and for any real reward withdrawal, so it has to tell the two apart by checking the amount.

## Status

The implementation is at version `0.5.0-alpha.2`, built with Aiken `v1.1.23` against Plutus V3, and declares more than 480 tests and benchmarks across 28 modules. A professional security audit has been performed and the fixes from both the initial round and the follow-up re-audit are merged, but the final report has not been published, and testnet exercise has been limited in scope. The project's own guidance is that this is not production-ready until the report lands, and nothing here should be read as contradicting that.

The specification itself is likewise unfinished. [CIP-113](https://github.com/cardano-foundation/CIPs/pull/444) is at the CIP editors' Last Check stage, the final review window before merge, so late changes remain possible. The architecture descends from [CIP-143](https://cips.cardano.org/cip/CIP-0143) and its Plutarch reference implementation by Phil DiSarro and the IOG team, which CIP-113 supersedes.

## Conclusion

CIP-113 gets issuer-enforced transfer rules onto Cardano without a ledger change, and the mechanism is a single reinterpretation of the address: hold every programmable token under one payment credential, and use the stake credential to record ownership. One spending validator then sees every movement, and a registry tells it which rules to invoke. The rest of the design is the consequences of that choice being worked through, including several that are not free.

The parts worth reading closely are the ones where a boundary had to be chosen rather than derived from the model. Extraction is gated and freeze is not, because hiding behind an uncooperative script is self-freezing rather than evasion. Who is seizable is left to substandards, because a script credential does not say whether it is a wallet or a lending pool. A holder can always separate a frozen policy out of a co-mingled UTxO without the freezer's consent, but only if the issuer declared a hook, since the default is deny. And registration is one-way, because de-registration would void the custody guarantee for tokens already issued.

Two caveats bound all of it. The specification is still in its final review window, and the implementation is waiting on its audit report. The design reads clearly and the reasoning behind each choice is documented in the repository, which is not the same thing as the work being finished.

![Mindmap of CIP-113 programmable tokens covering the shared custody model, the validator set and withdraw-zero dispatch, the sorted-list registry, pluggable substandards, the limits of administrative authority, and the integration surface]({{site.url_complet}}/assets/article/blockchain/cardano/cip-113-programmable-tokens-cardano.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Programmable token** | A Cardano native asset held at the shared custody address, whose every movement is gated by validation logic registered on-chain for its policy. |
| **Programmable logic base (PLB)** | The spending validator whose script hash is the payment credential of every programmable-token UTxO. It runs once per spent input and only dispatches. |
| **Withdraw-zero pattern** | Including a zero-lovelace withdrawal from a script's reward address to force the ledger to execute that stake validator once for the whole transaction. |
| **Delegate validator** | One of `transfer`, `third_party`, or `unfracking`: the stake validators the base validator dispatches to. Exactly one is loaded per transaction. |
| **Registry node** | A UTxO marked with a one-shot NFT whose datum records a registered policy ID, its position in the sorted list, and the credentials that govern it. |
| **Covering node** | The registry node satisfying `key < target < next`, which in a sorted complete list proves the target policy is not registered. |
| **Substandard** | A pluggable set of stake validators defining a specific token's rules (transfer, third-party, unfracking) and any supporting on-chain state such as a denylist. |
| **Third-party action** | An administrative forced transfer, seizure, or burn, authorised by the policy's third-party script rather than by the holder's stake credential. |
| **Unfracking** | A holder-authorised, value-preserving restructuring that strips one policy out of the holder's own UTxOs without invoking that policy's transfer logic. |
| **Coordination UTxO** | The UTxO carrying the one-shot protocol-parameters NFT, whose datum holds the live delegate credentials and is the target of an in-place protocol upgrade. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A registered policy's tokens never leave the shared payment credential. | Value containment in `transfer`, aggregate conservation in `third_party`, owner-side equality in `unfracking`, `no_escape` in `issuance_mint`. | A registry node could be deleted, making the policy unregistered and its tokens movable under a covering-node proof. |
| Every spent programmable-token input is authorised by its own stake credential. | The ownership walk in the `transfer` validator, by signature or withdraw-zero. | The walk stopped short of covering all inputs at the shared credential. |
| A registered policy ID is the hash of the issuance template applied to the registered credential. | `is_programmable_token_id_valid` in `registry_mint`, via blake2b-224 reconstruction. | The template reference NFT could be forged, or a second `IssuanceCborHex` could exist. |
| Exactly one delegate validator runs per transaction, and its arm is unambiguous. | The base validator's equality against the credential named by the redeemer arm. | Two of the three delegate credentials in the parameters datum were set equal, which no validator checks. |
| A third-party action changes only the subject policy on each pair. | Per-pair byte identity of address, datum, reference script, and all non-subject policies. | The pairing were positional-optional rather than mandatory, letting an unpaired output escape the check. |
| A third-party action cannot reduce a holder's ADA. | The lovelace ratchet requiring output lovelace to be at least input lovelace. | The check reverted to value equality, which also reintroduces the minimum-UTxO deadlock it replaced. |
| A policy cannot be unfracked unless its issuer declared a hook. | The registry `unfracking_logic_script` withdraw-zero requirement; an unset field is an empty hash no withdrawal can key on. | The empty credential were ever treated as a wildcard rather than as a denial. |
| A registry lifecycle transaction never mints or burns the node's own token. | `registry_spend`, the sole spender of every registry node. | Another validator gained the ability to spend a registry node. |
| Every programmable-token output carries a bounded inline datum. | The `max_inline_datum_bytes` check on the seizure and unfracking output walks. | The bound were removed, letting a holder inflate a datum until seizure exceeds the transaction size limit. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| Querying by payment credential returns every holder's tokens, not the user's. | Build the full address from the base script hash plus the owner credential, and query that. |
| The credential in the stake slot may be a payment key hash, a stake key hash, or a script hash, and on-chain data cannot distinguish the first two. | Learn the deployment's convention off-chain; where a user may hold under both, query both addresses and sum. |
| Spending authority follows the stake slot, so the payment key may not be the signer. | Sign with the key matching the credential in the stake slot. |
| `params_idx`, `wdrl_idx`, and node indices are positions in the ledger's canonical ordering, not insertion order. | Sort reference inputs by output reference, and withdrawals with script credentials before key credentials and bytewise within each, before computing any index. |
| A registry node UTxO is consumed and re-created by any registration or update touching it, invalidating transactions that reference it. | Resolve the node at build time and, on failure, re-resolve against the current registry and rebuild rather than retrying the same reference. |
| A node's logic credentials are live mutable configuration, and a change is retroactive for all existing holders. | Never cache them as facts from registration; read the current node at build time and monitor node updates for supported policies. |
| A script holding programmable tokens is authorised by withdraw-zero, and its stake address must be registered on-chain first. | Implement the `withdraw` purpose, register the stake address, and expect a bare ledger rejection with no validator trace if you skip it. |
| A dApp's withdraw handler is invoked both for token authorisation and for any real reward withdrawal. | Distinguish the two by checking the withdrawal amount. |
| A third-party action is a compliance event, not a voluntary transfer, and is identified by the delegate invoked. | Display and record the three transaction kinds separately rather than folding seizures into transfer history. |
| Merging distinct programmable policies into one output exposes the user to a freeze that locks everything in it. | Keep programmable tokens in single-policy UTxOs, hold near the minimum ADA, and exclude unsolicited programmable-token UTxOs from automatic coin selection. |

## Frequently Asked Questions

**Q: Why does CIP-113 need a shared custody address at all, rather than putting the rules in the minting policy?**

Because a Cardano minting policy is consulted only when supply changes. It runs on a mint and on a burn, and it has no involvement in an ordinary transfer, which is just the spending of a UTxO under the ledger's normal rules. There is no per-transfer hook to attach anything to.

Putting every programmable token behind one payment credential manufactures the hook. Spending a UTxO requires satisfying its payment credential, so if that credential is a script shared by all holders, then that script necessarily runs on every movement and can consult the registry and invoke the token's rules.

**Q: What is the withdraw-zero pattern, and why is the expensive logic behind it?**

The Cardano ledger executes a stake validator whenever a transaction withdraws from its reward address, and the withdrawal amount may be zero. A zero withdrawal has no economic effect; it exists purely to force the script to run with the whole transaction in scope.

The reason it matters here is arithmetic. A spending validator runs once for every input it guards, so a transaction consolidating eight programmable-token UTxOs would run the registry lookups and the value-containment check eight times. A stake validator runs once per transaction regardless. Moving the expensive work behind a withdraw-zero invocation converts per-input cost into per-transaction cost, and leaves the base validator with one credential comparison.

**Q: What does a covering-node proof prove, and why is it needed on ordinary transfers?**

It proves that a policy is *not* registered. The registry is a sorted, complete linked list, so if a node exists with `node.key < target < node.next`, no node with `target` as its key can exist anywhere in the list.

It is needed constantly because the `transfer` validator demands one proof per distinct policy in the transaction's inputs, and a programmable-token UTxO always holds ADA and may hold ordinary native assets alongside. The covering-node proof is how the validator learns that a policy is not its business and skips it, rather than rejecting a transaction for carrying an unregistered asset.

**Q: Can an issuer seize a holder's ADA along with the tokens?**

No. The paired output's lovelace has to be at least the paired input's, so an administrator may top a UTxO up but never reduce it. ADA is not a programmable asset, and the framework treats it accordingly.

The check is worth knowing about because it used to be an equality, which pinned the lovelace exactly. That created a deadlock: a rise in the protocol's minimum-UTxO calculation above an existing UTxO's balance made every third-party action on it permanently unsatisfiable, because equality forbade the top-up that would have fixed it. Replacing equality with a one-way ratchet removed the deadlock without granting any new power.

**Q: A frozen token is sitting in a UTxO with my real assets. How do I get them out?**

Through an unfracking action, if the issuer of the token you want to separate has declared a hook for it. Unfracking lets you restructure the UTxOs you already own for one policy, moving that policy's tokens into their own UTxO while everything else in the pair stays byte-identical. The frozen policy's transfer logic is never invoked, so the party doing the freezing cannot block the separation.

Three conditions apply. The acted policy's `unfracking_logic_script` has to be set, since an unset hook is a denial rather than a permission. Every input has to belong to the same owner, or the action would be a transfer in disguise. And the strip has to be complete, because an output still holding some of the acted policy would still require that policy's transfer proof on every future spend, which in the freeze case means still stuck.

**Q: The architecture document describes a `protected_prefixes` field. Where is it in the code?**

It was removed. The field was an append-only list of CIP-67 label prefixes that a third-party action could not seize or burn, added to keep an administrator from sweeping up CIP-68 reference NFTs and CIP-102 royalty tokens alongside the user token.

The removal commit gives the reasoning: the framework already guarantees that the subject policy's third-party script is invoked on every action, so a substandard can protect its own companion assets without a framework field, and prefix protection is substandard responsibility rather than framework policy. The scope boundary the field enforced still exists; it moved one layer up. The published documents predate the change.

**Q: A wallet has cached a token's transfer logic credential from when the token was registered. What can go wrong?**

The transaction it builds can be rejected, and worse, the wallet can misinform the user about what rules apply. Four registry-node fields are mutable through the lifecycle path: the transfer, third-party, and unfracking credentials, and the global state pointer. Only `key`, `next`, and `minting_logic_script` are frozen.

Two properties make the caching actively wrong rather than merely stale. A change is retroactive, governing every existing holder's tokens on their next spend rather than only newly minted ones. And a change can flip the credential's *type*, moving a token between script-enforced logic and signature-gated logic. The registry node is the live source of truth, and it has to be read at transaction-build time.

**Q: What would an integrator have to combine from this article to explain a transfer that reverts with no obvious cause?**

The likely candidates cluster around three mechanisms that have nothing to do with the token's own rules.

- **A stale registry reference.** A registration or node update touching the referenced node consumed it, so the reference input is no longer live. The fix is to re-resolve the node and rebuild, not to retry the same transaction.
- **A wrong index.** `params_idx`, `wdrl_idx`, and node indices are positions in the ledger's canonical ordering, which matches neither insertion order nor, for withdrawals, bech32 string order. A wrong index fails an NFT authentication or a credential equality rather than producing a descriptive error.
- **An unregistered stake address.** If a script holds the tokens and its stake address was never registered, the zero-lovelace withdrawal is rejected by the ledger rather than by a validator, so there is no validator trace at all.

Only after ruling those out is the substandard's transfer logic, a denylist hit for instance, the probable cause.

## References

### Specifications and proposals

- [CIP-113 — Programmable token-like assets (PR #444)](https://github.com/cardano-foundation/CIPs/pull/444), Cardano Foundation CIP repository, at Last Check as of 2026-08-18
- [CIP-143 — Interoperable Programmable Tokens](https://cips.cardano.org/cip/CIP-0143), the predecessor architecture CIP-113 supersedes
- [CPS-0003 — Smart Tokens](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0003/README.md), the problem statement CIP-113 addresses
- [CIP-67 — Asset Name Label Registry](https://cips.cardano.org/cip/CIP-0067)
- [CIP-68 — Datum Metadata Standard](https://cips.cardano.org/cip/CIP-0068)
- [CIP-102 — Royalties Standard](https://cips.cardano.org/cip/CIP-0102)
- [ERC-3643 — T-REX Permissioned Tokens](https://eips.ethereum.org/EIPS/eip-3643), the account-model counterpart referenced for contrast

### Implementations

- [cardano-foundation/cip113-programmable-tokens-platform](https://github.com/cardano-foundation/cip113-programmable-tokens-platform), the off-chain reference frontend, Java backend, and substandard implementations
- [input-output-hk/wsc-poc](https://github.com/input-output-hk/wsc-poc), the original Plutarch reference implementation by Phil DiSarro and the IOG team

### Related articles

- [Writing Cardano Smart Contracts with Aiken]({{site.url_complet}}/2026/07/16/aiken-smart-contracts-cardano/)
- [A Categorized Guide to Cardano Improvement Proposals]({{site.url_complet}}/2026/07/16/cardano-cip-categories/)
- [The Extended UTXO Model, and How It Differs from Bitcoin]({{site.url_complet}}/2026/07/16/eutxo-vs-bitcoin-utxo/)
- [Two Ways to Build a Permissioned Token — Centrifuge's Transfer Hook Against ERC-3643]({{site.url_complet}}/2026/08/18/centrifuge-hook-vs-erc3643/)
- [Flexible Access Control in smart contracts (CMTAT)]({{site.url_complet}}/2026/01/27/cmtat-access-control/)

### Tooling and background

- [Aiken language documentation](https://aiken-lang.org/), the smart-contract language and toolchain used by the implementation
- [Cardano Developer Portal](https://developers.cardano.org/)
- ["Think of programmable tokens as a mini ledger within Cardano"](https://github.com/cardano-foundation/CIPs/pull/444#issuecomment-4084863264), review comment by Phil DiSarro on the CIP-113 pull request

### Analyzed source

- [cardano-foundation/cip113-programmable-tokens](https://github.com/cardano-foundation/cip113-programmable-tokens) — analyzed at commit [`9db7e0629a1509cc9d41d069f0ef0ed251601173`](https://github.com/cardano-foundation/cip113-programmable-tokens/tree/9db7e0629a1509cc9d41d069f0ef0ed251601173), version `0.5.0-alpha.2`, Aiken `v1.1.23`, 2026-08-26. No release tag points at this commit. All code excerpts, field lists, and measured figures in this article come from that revision.
