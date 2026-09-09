---
layout: post
title: "Native Account Abstraction on Aztec, Compared with ERC-4337"
date:   2026-09-09
lang: en
locale: en-GB
categories: blockchain ethereum ZKP
tags: aztec account-abstraction erc-4337 smart-wallet zkp privacy paymaster
description: Aztec has no EOAs and no protocol signature scheme, so account validation is proved on the user's device. What that changes against ERC-4337, and what it costs.
image: /assets/article/blockchain/aztec/2026-09-09-aztec-vs-erc4337-account-abstraction-mindmap.png
isMath: false
---

[ERC-4337](https://eips.ethereum.org/EIPS/eip-4337) abstracts accounts on a chain that still has externally owned accounts underneath. Everything it adds — the alt mempool, the bundler, the singleton EntryPoint, the paymaster — exists to route around a protocol that was not built for programmable accounts, and at the bottom of every bundle there is still an EOA paying for a normal Ethereum transaction in ETH.

Aztec has no EOAs. Every account is a contract, there is no protocol-level signature scheme at all, and an account's entrypoint decides for itself what counts as authorisation: a Schnorr signature, an ECDSA signature, a passkey, a multisig, a password, or a rule with no signature in it. None of ERC-4337's supporting machinery exists, because none of it is needed.

The comparison is worth making carefully, because the interesting parts are not the obvious ones. Aztec's headline advantage is not that accounts are contracts, which ERC-4337 achieves too. It is that validation is proved on the user's device, so the network never runs it and therefore never has to be defended against it. The headline cost is not proving time either. It is that Aztec accounts have protocol keys baked into the address, and unlike an ERC-4337 account, they cannot be rotated.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Where the abstraction sits

ERC-4337 is deliberately an application-layer standard: it required no consensus change, which is why it shipped. A user signs a `UserOperation` rather than a transaction, sends it to a mempool that Ethereum nodes do not know about, and a bundler collects several of them and calls `handleOps` on the EntryPoint singleton. The EntryPoint calls each account's `validateUserOp`, then its execution function. The bundler is an ordinary EOA and pays real gas, so it must be reimbursed, which is what the account's deposit or a paymaster is for.

Aztec inverts this. The account contract's entrypoint is where a transaction starts, full stop. There is no separate mempool, no bundler role, no singleton mediating between accounts, and no fallback path for a "plain" transaction because there is no plain transaction to fall back to.

That difference propagates further than it first appears. Every piece of ERC-4337 machinery is a consequence of the abstraction sitting *above* a protocol that does not know about it, and each piece brings its own security surface: the site's articles on [ERC-4337: Account Abstraction Using Alt Mempool]({{site.url_complet}}/2025/05/02/erc-4337-overview/) and [SenderCreator in ERC-4337 — Deploying Accounts and Reading Counterfactual Addresses]({{site.url_complet}}/2026/07/23/sendercreator-entrypoint-erc4337-counterfactual-address/) cover the factory, paymaster and aggregator staking rules that exist to keep those pieces honest. On Aztec that surface is absent, and a different one takes its place.

## Validation, and the denial-of-service problem

If accounts may run arbitrary validation logic, someone can flood the network with operations that are expensive to validate and then turn out to be invalid. The validator has done the work and cannot charge for it. Every account-abstraction design has to answer this, and the two answers here are opposites.

![ERC-4337 has the bundler simulate validateUserOp under ERC-7562 restrictions and run it onchain; Aztec proves the entrypoint on the device and the sequencer verifies a constant-size proof]({{site.url_complet}}/assets/article/blockchain/aztec/aa-validation-paths-comparison.png)

**ERC-4337 restricts what validation is allowed to do.** The bundler has to simulate `validateUserOp` before it will include an operation, and it must be able to trust that simulation result when the bundle actually executes. So the validation rules — now codified as [ERC-7562](https://eips.ethereum.org/EIPS/eip-7562) — forbid opcodes whose result can change between simulation and inclusion, restrict which storage slots an account may touch during validation, and cap validation gas. Entities that step outside the account's own storage, such as factories and paymasters, must be staked. It works, and the cost is that an account's authentication logic is confined to a sandbox designed to protect a third party from it.

**Aztec removes the third party instead.** Validation runs in the PXE on the user's own device and is proved there, along with the rest of private execution. The sequencer receives a proof and verifies it, and verification is constant-time regardless of what the account's entrypoint did. There is nothing to sandbox, because the sequencer never executes the account's code.

The practical consequences are larger than they sound:

- **Validation complexity is free to the network.** An account that verifies a hundred signatures, walks a Merkle proof of a guardian set, or evaluates a spending policy costs the network exactly what a single-signature account costs. On ERC-4337 all of that is gas the user pays and gas the bundler must bound.
- **Validation logic is not visible onchain.** The circuit hides which function ran and what it checked, so an account's authentication rules are private. A 3-of-5 multisig does not announce itself as one.
- **The cost moves to the user.** Complex validation is paid in local proving time and memory. It is free to everyone except the person doing it, which is the correct place for it, but it is not free.

Aztec's own documentation makes the DoS argument explicitly, and it is the cleanest statement of why native abstraction is not merely a tidier ERC-4337.

## Keys, and what cannot be rotated

Here the trade-off runs the other way, and it is the point most easily missed.

An ERC-4337 account has whatever keys its code says it has. Rotating a signer is a state change in the account contract; the address is unaffected, because the address came from CREATE2 over the factory, implementation and salt. Social recovery, guardian rotation and key replacement are all ordinary contract logic.

An Aztec account has two categories of key, and only one of them behaves that way.

| Key | Purpose | Protocol-managed | Rotatable |
|---|---|---|---|
| Nullifier keys (`Npk_m`) | Spending notes | Yes | No |
| Incoming viewing keys (`Ivpk_m`) | Decrypting received notes | Yes | No |
| Outgoing viewing, tagging, message-signing, fallback | Reserved slots, not currently used | Yes | No |
| Signing key | Authorising transactions | No, defined by the account contract | Yes |

The signing key is the ERC-4337-like one: the account contract owns it, and swapping it is application logic. The protocol keys are different. They are hashed into the address itself — `address = hash(public_keys_hash, partial_address)` — so changing them would change the address, and the nullifier key is what makes a user's notes spendable.

Two things follow, and both deserve to be said plainly:

- **Key rotation is only half available.** You can replace the key that authorises transactions. You cannot replace the key that decrypts your notes or the key that spends them.
- **Recovery has a hard limit.** A social-recovery scheme on Aztec can restore the ability to *send transactions* from the account. It cannot restore the ability to *read or spend the private notes* the account already holds, because that requires the nullifier and viewing keys, which no amount of contract logic can reissue. On an ERC-4337 account holding ERC-20s, recovering the signer recovers the funds. On Aztec the two are separable, and losing the account secret is not the same failure as losing the signing key.

There is a partial mitigation in the design: nullifier keys are **app-siloed**, derived per contract as `nhk_app = hash(nhk_m, app_contract_address)`, so a contract only ever handles a key scoped to itself. That bounds what a flaw in one application can do to state held in another. It does not make the master keys rotatable.

## Addresses and counterfactual deployment

Both designs let an address exist before its code does, and both use it for the same onboarding trick (fund the address first, deploy on first use), but they derive it differently and get different properties.

ERC-4337 derives the address with CREATE2 from the factory, the implementation and a salt. The first `UserOperation` carries `initCode`, and the EntryPoint's `SenderCreator` deploys the account before validation runs. The factory has to be staked, or bundlers will not accept the operation.

Aztec folds the account's public keys into the address. That is what makes an undeployed Aztec address useful in a way an undeployed Ethereum address is not: a sender can encrypt a note *to the address*, because the viewing key needed to do so is inside it. An account can therefore receive private notes before it exists onchain, with no factory and no registry involved.

Spending is where the extra step appears. An address alone is enough to receive; spending requires the **complete address** — the address, all the public keys, and the partial address — which is what proves the nullifier key inside the address is the right one. A wallet that has only the bare address of its own account can be paid but cannot spend.

Deployment itself is also more granular than on Ethereum. An account used only for private functions needs initialisation but not public deployment; an account that will touch public state needs both. And because the address derivation does not depend on deployment, notes sent to an account that is never deployed are not lost: they are simply unspendable until it is.

## Nonces

ERC-4337 calls its nonce handling *semi-abstracted*, and the word is accurate. The `UserOperation` carries a single `uint256` that the EntryPoint reads as two fields: a 192-bit key and a 64-bit sequence. Within a key the sequence must increment monotonically; a new key can start at zero at any time. That buys parallel operation streams from one account while keeping operation-hash uniqueness enforced at the protocol level, though the EntryPoint still enforces it, so the account chooses lanes rather than rules.

Aztec has no protocol nonce at all. Replay protection is entirely the account contract's problem, and the documentation sets out the strategies that become available:

| Strategy | How it works | What it buys |
|---|---|---|
| Sequential | Nonces must be used in order | Predictable ordering, as on Ethereum |
| Unordered | Any unused nonce is valid | Parallel transactions, no head-of-line blocking |
| Time-windowed | Nonces valid only in a period | Automatic expiry, natural batching |
| Merkle-tree based | Nonces drawn from a pre-committed set | Batch pre-authorisation, and privacy |

The last one has no ERC-4337 equivalent worth the name: an account can commit to a set of future authorisations and later prove membership without revealing the set. That is a direct consequence of validation being a circuit rather than an onchain call.

The flip side is that nothing supplies replay protection by default. An Aztec account contract that neglects it has no protocol backstop, whereas an ERC-4337 account gets uniqueness from the EntryPoint whatever its own logic does. When a transaction emits no nullifier of its own, Aztec uses the hash of the transaction request — which includes a random salt — as the first nullifier, so a transaction cannot be replayed verbatim; that is a uniqueness property, not a substitute for an account's own scheme. The site's article on [Nonce Management and CREATE2 in ERC-4337 Smart Wallets]({{site.url_complet}}/2026/02/17/nonce-management-create2-smart-wallets-erc4337/) covers the failure modes on the Ethereum side, and most of them transfer.

## Fees

ERC-4337 pays for sponsorship with a paymaster that holds a deposit at the EntryPoint and is staked against abuse. The account or the paymaster reimburses the bundler, which fronted real ETH.

Aztec uses a **fee-paying contract** (FPC) and a dedicated **teardown phase** at the end of the transaction, in which the fee is settled after execution has determined what it actually costs. The available methods are:

- **Fee Juice**, the default, paid from the account's own balance.
- **Sponsored FPC**, where a contract pays on the user's behalf. This is what makes deploying a brand-new account possible when it holds nothing at all — the deployment transaction is itself sponsored.
- **Private FPC**, where the fee payment is private rather than public.
- **Third-party FPC**, paying in another token through a provider.
- **Bridge and claim**, bootstrapping from L1 in a single step.

Two details have no Ethereum analogue. Fee Juice is **non-transferable**: it is bridged in, it can pay fees, and it cannot be sent between accounts. Aztec's stated reason is credible neutrality between third-party asset portals and room for local compliance rules — the fee asset deliberately is not a tradeable token. And a fee payment can be *private*, which no ERC-4337 paymaster arrangement offers, since on Ethereum the paymaster's involvement is on the public record.

## Delegated authorisation: approve, permit, authwit

Every account system needs a way to let a contract act on a user's behalf. Ethereum's answer is `approve` and `permit`, and both are well understood to be uncomfortable: infinite approvals are a standing risk, and revocation costs a transaction.

Aztec's answer is the **authentication witness**, and the design difference is that it authorises one exact action rather than a standing allowance.

![In the private flow the token static-calls Alice's account, which fetches the witness from a PXE oracle; in the public flow the approval is stored in the auth registry and consumed there]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-authwit-flow-sequence.png)

The authorisation is a two-level hash:

```
inner_hash   = H(caller, selector, args_hash)
message_hash = H(consumer, chain_id, version, inner_hash)
```

The inner hash pins the caller, the function and the exact arguments; the outer hash pins the contract that will verify it, plus the chain id and version, which is what stops a witness being replayed on another chain. Read aloud, a witness says "this specific contract may call this specific function with these specific arguments, on this chain, once".

The two execution contexts need different plumbing:

- **In private**, the consuming contract makes a *static* call to the account contract asking whether the action is authorised. The account fetches the witness through a PXE oracle and answers. The call is static so that the account cannot re-enter and mutate state mid-verification — which also means the account cannot emit the nullifier, so the consuming contract does it instead.
- **In public**, oracles do not exist, because the sequencer is running the code. Authorisations are written to a shared **auth registry** first and consumed from it. There is a neat efficiency here: if an authorisation is set and consumed in the same transaction, the two state changes squash.

There is a further reason the public flow looks the way it does, and it is a good illustration of how Aztec's constraints interlock: **ECDSA verification is not available in the AVM at all**. Signature verification in a public function does not compile. The recommended pattern is therefore to verify the signature in private, record the approval in the registry, and consume it in public.

Replay protection comes from a nullifier: each witness is single-use. Authorising the same action repeatedly means including a nonce in the arguments. Revocation is the sharpest contrast with `approve` — a user cancels a witness by emitting its nullifier directly, invalidating it without performing the action.

| Aspect | ERC-20 approve | Authwit |
|---|---|---|
| Scope | Blanket allowance | One specific action, with its arguments |
| What the user sees | Often an unbounded amount | The exact call being authorised |
| Revocation | A transaction that overwrites the allowance | Emit the nullifier; the witness is dead |
| Reuse | Until the allowance is spent or changed | Single-use unless a nonce is included |
| Private state | Cannot work; the spender needs note secrets | Works, via the account contract |

**One caveat matters more than the rest, and it is easy to misread the mechanism without it.** An authwit does not confer the ability to spend someone's private notes. Spending a note requires the note secrets and the owner's nullifier key, so the owner still has to participate in the transaction. A witness authorises a contract to *perform an action within a transaction the owner is part of*; it does not let a third party go and move private funds on their own later. That is a stronger guarantee than `approve` gives, and it is also a real functional limitation: the "grant now, spend whenever" pattern that ERC-20 allowances enable does not exist for private balances.

## Comparison

| Dimension | **ERC-4337** | **Aztec** |
|---|---|---|
| Where abstraction lives | Application layer, above the protocol | The protocol; there is no alternative |
| EOAs | Still exist, and the bundler is one | None |
| Supporting infrastructure | Alt mempool, bundlers, EntryPoint singleton | None of it |
| Who runs account validation | The bundler, then the EntryPoint, onchain | The user's own device, proved |
| DoS defence | Restrict validation: ERC-7562 opcode and storage rules, gas caps, staking | No restriction needed; the network verifies a proof |
| Cost of complex validation | Gas, paid onchain, bounded by the bundler | Local proving time; free to the network |
| Is validation logic public | Yes, it is onchain code | No, the circuit hides it |
| Signature scheme | Account's choice, within the sandbox | Account's choice, unrestricted |
| Nonce | Semi-abstracted: 192-bit key, 64-bit sequence, EntryPoint-enforced | Fully abstracted; the account owns replay protection |
| Address derivation | CREATE2 over factory, implementation, salt | `hash(public_keys_hash, partial_address)` |
| Counterfactual funding | Yes, plain value transfers | Yes, including encrypted notes, because keys are in the address |
| Key rotation | Everything the account defines | Signing key only; nullifier and viewing keys are fixed |
| Recovery ceiling | Recovering the signer recovers the funds | Recovers transaction sending, not note access |
| Sponsorship | Paymaster with an EntryPoint deposit and stake | Fee-paying contract settling in the teardown phase |
| Private fee payment | No; the paymaster is on the public record | Yes, via a private FPC |
| Fee asset | ETH under the hood, any token at the surface | Fee Juice, non-transferable by design |
| Delegated authorisation | `approve` / `permit` allowances | Authwit: one action, single-use, nullifier-revocable |
| Batching | Multiple calls in one `UserOperation` | Multiple calls in one entrypoint payload |
| Maturity | Deployed on Ethereum mainnet and L2s since 2023 | Unaudited and under active development |

## What each design cannot do

Being fair about this matters, because the two are not competing for the same deployment.

**ERC-4337 cannot make validation cheap or private.** Every rule an account enforces is code that runs onchain, is paid for in gas, and is visible to anyone. It also cannot remove the entities its own architecture introduced: bundler censorship, paymaster griefing and factory staking are live concerns precisely because the design needs those roles. [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) narrows the gap by letting an EOA delegate to contract code, but it does not close it: the account is still an EOA whose ECDSA key can act directly, which is a different security model from one where no such key exists.

**Aztec cannot be adopted incrementally.** It is a separate chain with a separate language, and an existing Solidity account cannot be ported. It cannot rotate the keys that matter most for asset recovery. It cannot verify an ECDSA signature in a public function. And it is explicitly unaudited and under development, with its own documentation advising against entrusting real secrets to it — which rules it out of exactly the custody scenarios where sophisticated account logic is most wanted today.

The honest summary is that ERC-4337 is a retrofit that works and is in production, and Aztec is what the same idea looks like when the protocol is designed around it from the start, at the cost of being a different protocol.

## Conclusion

The distinguishing feature of Aztec's account model is not that accounts are programmable — ERC-4337 achieved that without a consensus change, which is why it is deployed and Aztec's model is not. It is that moving validation into a client-side proof dissolves the problem that shaped ERC-4337's design. There is no need to constrain what an account may do during validation when no one but the account's owner ever runs it, and the sequencer's cost is the same whether the account checks one signature or a hundred.

The costs are visible in the same places. Proving is paid by the user rather than the network. Protocol keys are hashed into the address and cannot be rotated, so recovery can restore the ability to transact but not the ability to read or spend existing notes. And an authwit's tight scoping is also a restriction: it authorises an action inside a transaction the owner joins, not an allowance a contract can draw on later.

![Mindmap of account abstraction on Aztec and ERC-4337 covering where the abstraction sits, validation and DoS, keys, addresses, nonces, fees and delegated authorisation]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-09-aztec-vs-erc4337-account-abstraction-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Entrypoint (Aztec)** | The function on an account contract where a transaction begins; it authenticates, sets the fee payer and executes the requested calls. |
| **EntryPoint (ERC-4337)** | The singleton Ethereum contract that validates and executes bundled `UserOperation`s and enforces the nonce. |
| **Authwit** | An authentication witness authorising one exact call with its arguments, verified by the account contract and consumed once. |
| **Auth registry** | The shared contract holding authorisations for public execution, where oracles are unavailable. |
| **Complete address** | An Aztec address together with its public keys and partial address; required to spend notes, whereas the bare address suffices to receive them. |
| **App-siloed key** | A nullifier key derived per contract as `hash(nhk_m, app_contract_address)`, so one application never handles another's spending key. |
| **Fee-paying contract (FPC)** | The Aztec contract that settles a transaction fee, optionally on someone else's behalf and optionally in private. |
| **Fee Juice** | Aztec's fee asset, bridged from Ethereum and non-transferable between accounts by design. |
| **Teardown phase** | The final phase of an Aztec transaction, in which the fee is settled once the actual cost is known. |
| **ERC-7562** | The validation rules an ERC-4337 account, factory and paymaster must obey so a bundler can trust its own simulation. |

### Security Implementation Checklist

Properties an account contract should satisfy on either platform. Each is checkable against an implementation.

#### Replay protection and nonces

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | An Aztec account contract implements its own replay protection; nothing in the protocol supplies one. | The same authorised payload can be submitted repeatedly, replaying the user's intent. |
| ☐ | The authorised payload the account validates covers every field that determines the effect, including the calls and their arguments. | A signature over a partial payload lets a relayer alter the unsigned part. |
| ☐ | An authwit's arguments include a nonce when the same action must be authorised more than once. | Either the action can only ever run once, or a single witness is reused across intended-distinct calls. |
| ☐ | Chain id and version are bound into the authorisation hash. | A witness or signature is replayed on another chain or another protocol version. |

#### Keys and recovery

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The signing key is stored and rotated as contract state, separate from the account secret that derives the protocol keys. | Rotating the signer is impossible, or the encryption secret is exposed by the signing path. |
| ☐ | Recovery documentation states that recovering an Aztec account restores transacting, not access to existing notes. | Users believe a guardian set can recover funds that are in fact permanently unreadable. |
| ☐ | The account secret, salt and signing key are all backed up; all three are needed. | Losing any one of them permanently loses the account. |
| ☐ | Nullifier keys are obtained through the framework's getters rather than derived by hand. | A hand-derived key breaks siloing or produces nullifiers that do not match the protocol's. |

#### Validation logic

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | An ERC-4337 account's `validateUserOp` stays inside the ERC-7562 opcode and storage rules. | Bundlers reject the operation, or the account is griefable through simulation divergence. |
| ☐ | An Aztec entrypoint treats every unconstrained oracle result as untrusted until constrained. | An unproven value reaching an assertion lets a malicious client forge authorisation. |
| ☐ | Authwit verification is reached through a static call, so the account cannot mutate state during it. | The account re-enters the flow and changes the state the decision depended on. |
| ☐ | Signature verification is placed in a private function, never a public one. | The AVM has no ECDSA, so the transpiler fails at compile time. |

#### Authorisation scope

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The consuming contract emits the authwit nullifier before acting on the authorisation. | The witness stays valid and the authorised action can be repeated. |
| ☐ | A cancellation path exists and its race with a pending use is documented. | A user believes a witness is revoked while the sequencer is including the transaction that uses it. |
| ☐ | Public functions that exist to service an enqueued private call are marked `#[only_self]`. | The function is a public entrypoint that anyone can call directly. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| An Aztec address can receive notes before the account is deployed. | Do not treat "not deployed" as "cannot be paid"; check deployment separately from payability. |
| Spending requires the complete address, not just the address. | Store the public keys and partial address alongside the address wherever an account is persisted. |
| A private-only account needs initialisation but not public deployment. | Do not force public deployment on accounts that will never touch public state. |
| A new account holds no Fee Juice and cannot pay for its own deployment. | Deploy through a sponsored fee-paying contract. |
| Fee Juice cannot be transferred between accounts. | Fund accounts by bridging or sponsorship, never by sending the fee asset from another account. |
| An authwit does not let a contract spend a user's private notes independently. | Design flows where the note owner is present in the transaction. |
| A cancelled authwit and a pending use may race. | Treat cancellation as best-effort until it is mined; the sequencer decides the order. |

## Frequently Asked Questions

**Q: ERC-4337 also makes accounts programmable. What does native abstraction actually add?**

It removes the reason ERC-4337 has to constrain accounts. Because a bundler simulates an account's validation and then relies on that result at inclusion time, ERC-7562 forbids opcodes whose value can change in between, restricts which storage an account may read during validation, and caps validation gas. Those rules exist to protect a third party from the account's code.

On Aztec no third party runs the code. Validation executes and is proved on the user's device, and the sequencer verifies a constant-size proof. Nothing needs sandboxing, so the account's authentication logic is unrestricted, private, and costs the network the same whatever it does.

**Q: Why can an Aztec account rotate its signing key but not its nullifier key?**

Because they live in different places. The signing key is ordinary state inside the account contract, and the protocol has no opinion about it: Aztec has no protocol-level signature scheme at all.

The nullifier and viewing keys are protocol keys, and they are hashed into the address itself through `public_keys_hash`. Changing them would produce a different address, and the nullifier key is what makes existing notes spendable. So they are fixed at account creation, and no contract logic can reissue them.

**Q: What does "semi-abstracted nonce" mean in ERC-4337, and how is Aztec different?**

ERC-4337 packs a single `uint256` into a 192-bit key and a 64-bit sequence. Within one key the sequence must increase monotonically, and a new key may start at zero at any time. That gives an account parallel operation lanes, but the EntryPoint still enforces the scheme, so the account picks lanes rather than rules.

Aztec has no protocol nonce. The account contract implements replay protection itself, which makes strategies such as unordered nonces, time-windowed validity or a Merkle-committed set of future authorisations possible. The cost is that an account which omits replay protection has no protocol backstop.

**Q: If a user loses their signing key, can a social-recovery Aztec account restore their funds?**

Only partly, and this is the sharpest limitation in the design. Recovery logic can restore the ability to authorise transactions from the account, because the signing key is contract state.

It cannot restore access to the account's private notes. Reading them needs the incoming viewing key and spending them needs the nullifier key, both derived from the account secret and both baked into the address. If that secret is gone, the notes are unreadable and unspendable regardless of what the account contract permits. An ERC-4337 account holding ERC-20 tokens has no equivalent split: recovering the signer recovers the assets.

**Q: An authwit authorises a contract to move a user's tokens. Why can that contract not simply drain the private balance later?**

Because the authwit and the ability to spend are separate things. A witness authorises a specific call with specific arguments, and it is consumed once, enforced by a nullifier the consuming contract emits.

Spending a private note additionally requires the note secrets and the owner's app-siloed nullifier key, which the witness does not convey. The owner therefore has to be a participant in the transaction where the authorised action happens. A contract cannot take a witness away and act on it independently later, which is precisely the ERC-20 allowance failure mode the design avoids, and it is also why the "approve once, spend over time" pattern has no private equivalent.

**Q: Why does the public authwit flow use a registry when the private flow uses an oracle, and what does that have to do with signatures?**

Oracles work in private execution because the code runs on the user's device, where the wallet can answer a mid-execution request for a witness. In public execution the sequencer runs the code and there is no user to ask, so the authorisation has to exist beforehand — hence the shared auth registry.

The signature connection is a second constraint pointing the same way: the AVM has no ECDSA, so a public function cannot verify a signature at all. The recommended pattern therefore verifies the signature in private, writes the approval to the registry, and consumes it in public. When the set and the consume land in the same transaction, the two state changes squash.

## References

### Aztec documentation

- [Understanding Accounts in Aztec](https://docs.aztec.network/developers/docs/foundational-topics/accounts) — native account abstraction, the entrypoint pattern, nonce and fee abstraction
- [Keys](https://docs.aztec.network/developers/docs/foundational-topics/accounts/keys) — the key hierarchy, app-siloing, and what is rotatable
- [Authentication Witness](https://docs.aztec.network/developers/docs/foundational-topics/advanced/authwit) — hash structure, private and public flows, replay prevention
- [Authentication Witnesses (implementation)](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/authentication_witnesses) — the `#[authorize_once]` macro and the auth registry
- [Creating Accounts](https://docs.aztec.network/developers/docs/aztec-js/how_to_create_account) — secret, salt and signing key; deployment paths
- [Paying Fees](https://docs.aztec.network/developers/docs/aztec-js/how_to_pay_fees) — Fee Juice, sponsored, private and third-party fee-paying contracts
- [Fees](https://docs.aztec.network/developers/docs/foundational-topics/fees) — mana, Fee Juice and the teardown phase
- [Contract Deployment Reference](https://docs.aztec.network/developers/docs/aztec-nr/contract_readiness_states) — which deployment states a contract needs
- [AVM Cryptographic Compatibility](https://docs.aztec.network/developers/docs/foundational-topics/advanced/circuits/avm_compatibility) — why ECDSA is unavailable in public functions
- [Limitations](https://docs.aztec.network/developers/docs/resources/considerations/limitations) — the unaudited, in-development status

### Ethereum standards

- [ERC-4337: Account Abstraction Using alt mempool](https://eips.ethereum.org/EIPS/eip-4337)
- [ERC-7562: Account Abstraction Validation Scope Rules](https://eips.ethereum.org/EIPS/eip-7562)
- [EIP-7702: Set EOA account code](https://eips.ethereum.org/EIPS/eip-7702)
- [eth-infinitism/account-abstraction](https://github.com/eth-infinitism/account-abstraction) — the reference EntryPoint and account implementations

### Related articles

- [Partial Notes on Aztec — Deferred Completion and Private DeFi Composability]({{site.url_complet}}/2026/09/09/aztec-partial-notes-private-defi-composability/)
- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
- [ERC-4337: Account Abstraction Using Alt Mempool]({{site.url_complet}}/2025/05/02/erc-4337-overview/)
- [SenderCreator in ERC-4337 — Deploying Accounts and Reading Counterfactual Addresses]({{site.url_complet}}/2026/07/23/sendercreator-entrypoint-erc4337-counterfactual-address/)
- [Nonce Management and CREATE2 in ERC-4337 Smart Wallets]({{site.url_complet}}/2026/02/17/nonce-management-create2-smart-wallets-erc4337/)
- [OpenZeppelin ERC-4337 Account contract Overview]({{site.url_complet}}/2025/12/13/erc4337-oz-account/)
- [EIP-7702 Smart Wallet Security: Threat Model and Attack Surface Analysis]({{site.url_complet}}/2026/02/17/eip-7702-security-threat-model/)
- [Inside Circle's SponsorPaymaster — How a Verifying Paymaster Is Built]({{site.url_complet}}/2026/09/09/circle-sponsor-paymaster-erc4337/)
