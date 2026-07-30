---
layout: post
title: "How Alchemy Implements Smart Wallets and Account Abstraction"
date:   2026-07-30
lang: en
locale: en-GB
categories: blockchain ethereum solidity
tags: blockchain ethereum solidity erc-4337 erc-6900 account-abstraction smart-wallet modular-account session-keys eip-7702 bundler rundler
description: A walkthrough of Alchemy's ERC-4337 stack — Modular Account V2 and its semi-modular variants, validation selection through the UserOperation nonce, deferred actions, session-key permission modules, the Rundler bundler, and the hosted Wallet APIs.
image: /assets/article/blockchain/ethereum/erc-4337/2026-07-30-alchemy-smart-wallet-account-abstraction.png
isMath: false
---

Most write-ups of account abstraction stop at the standard: a `UserOperation`, a bundler, an `EntryPoint`. ERC-4337 deliberately says nothing about how an account decides *which* key signed, how permissions are scoped, or how a session key gets installed without an extra transaction. Those decisions belong to the account implementation, and they are where the engineering actually lives. Alchemy is one of the few teams that has published every layer of its answer — the account contracts, the bundler, and the API that hides both — so its stack can be read end to end. This article follows that path, from the Solidity that validates a signature to the handful of JSON-RPC methods an application actually calls.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What Alchemy ships

Four layers, each independently usable, each open source except the paymaster.

| Layer | Component | Language |
|-------|-----------|----------|
| Account | **Modular Account V2** (MAv2), **Light Account** | Solidity |
| Bundler | **Rundler** | Rust |
| Paymaster | **Gas Manager** — policy-driven sponsorship | hosted |
| API | **Wallet APIs** — a small `wallet_*` surface and a TypeScript SDK | hosted |

![The four layers of Alchemy's account abstraction stack and how a call travels through them]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/alchemy-aa-stack-concept.png)

The intended developer path runs top to bottom: call `wallet_prepareCalls`, sign the hash it returns, call `wallet_sendPreparedCalls`. Account deployment, nonce selection, gas estimation, paymaster data and bundling all happen below the API line. The contract detail that follows matters when you leave that path — when you write a module, integrate a different bundler, or audit the account.

## Modular Account V2

MAv2 is an ERC-4337 account that also implements [ERC-6900](https://eips.ethereum.org/EIPS/eip-6900), the modular-account standard, at version 0.8. Accounts are deployed as ERC-1967 proxies and use ERC-7201 namespaced storage, so the implementation behind a proxy can be replaced without storage collisions.

### The compromise the design makes

A fully modular account has an awkward first transaction. Before it can validate anything it must install a validation module, and that install costs gas on a path where gas is most visible — account creation. MAv2 avoids the cost by building a **fallback validation** into the account contract itself, reserved at validation entity ID `0`:

```solidity
// src/helpers/Constants.sol
// Magic value for the validation entity id of the fallback validation for SemiModularAccount.
uint32 constant FALLBACK_VALIDATION_ID = uint32(0);
```

The fallback supports exactly what `SingleSignerValidationModule` supports — secp256k1 ECDSA for an EOA owner, ERC-1271 for a contract owner — without a module install. Modules still work normally; the fallback is a fast path that can be re-pointed at a different signer (`updateFallbackSignerData`) or disabled entirely once other validations exist. Hence "semi-modular": modular by capability, monolithic by default.

The measurable result is that runtime gas for account creation drops below 100 000 — 97 764 by Alchemy's own benchmark, against 180 465 for ZeroDev Kernel v3 and 289 207 for Safe with its 4337 module.

### Four implementations, three of them position-dependent

![Where the owner is stored in each Modular Account V2 variant]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/alchemy-account-variants-concept.png)

| Contract | Owner stored in | Valid upgrade target | Use for |
|----------|-----------------|----------------------|---------|
| `SemiModularAccountBytecode` (SMA-B) | proxy bytecode, as a Solady `LibClone` immutable arg | **no** | the cheapest new deployment; the default |
| `SemiModularAccountStorageOnly` (SMA-S) | namespaced storage, set by `initialize()` | yes | upgrading an existing proxy into MAv2 |
| `SemiModularAccount7702` | defaults to `address(this)` | n/a | an EOA delegating under EIP-7702 |
| `ModularAccount` | nowhere — validation lives entirely in modules | yes | maximum modularity |

The distinctions are not stylistic. SMA-B reads its owner out of the proxy's own bytecode, so pointing an arbitrary ERC-1967 proxy at it produces an account with no owner; it is only deployable through `AccountFactory`. And the EIP-7702 variant carries a warning worth repeating in full, because getting it wrong is a total loss:

> When using EIP-7702, the delegate destination should only be the `SemiModularAccount7702` implementation, and not any of the other account variants. Otherwise, if the delegate destination is set to an account with an unprotected initializer function, an attacker will be able to take over the account.

Initializer functions on the other variants are not access-controlled — they rely on the proxy pattern's one-shot initialization for safety. An EOA that delegates to one of them exposes a live initializer at its own address, and anyone can call it to install their own validation. `upgradeToAndCall` is disabled on `SemiModularAccount7702` for the same class of reason.

### What the account can do before any module

`ModularAccountBase` exposes a working account out of the box:

- `execute(address target, uint256 value, bytes data)` and `executeBatch(Call[] calls)`
- `executeUserOp(PackedUserOperation, bytes32)`, the EntryPoint v0.7+ path needed when validation-attached execution hooks must see the user-operation fields
- `executeWithRuntimeValidation(bytes data, bytes authorization)` for callers that are not the EntryPoint
- `performCreate(uint256 value, bytes initCode, bool isCreate2, bytes32 salt)`
- `installValidation` / `uninstallValidation` / `installExecution` / `uninstallExecution`
- `isValidSignature(bytes32, bytes)` and `upgradeToAndCall`

Batching self-calls carries one rule that reads like a quirk and is in fact a security boundary: to call the account's own functions inside a batch, set `target` to the account address, and **flatten** — a self-call in the batch may not itself be `execute` or `executeBatch`. Nesting would let a caller reach an account function through a wrapper whose selector the validation *is* allowed to invoke, sidestepping the applicability check on the inner function. Flattening makes every self-call selector visible to the check.

### Validations, hooks, execution functions

Modules hold per-account state, so every installation is keyed by a `uint32` **entity ID**; the pair `(module address, entity ID)` is a module function. MAv2 adds a constraint ERC-6900 does not require: **validation entity IDs must be unique across the whole account**. The next section explains why.

A **validation function** authorizes actions, and is installed with flags:

| Flag | Grants |
|------|--------|
| `isGlobal` | may validate any account function in the global pool |
| `isSignatureValidation` | may validate ERC-1271 signatures |
| `isUserOpValidation` | may validate user-operation signatures |
| (runtime) | implicit; cannot be disabled |

`isSignatureValidation` deserves attention beyond its name. Because deferred actions are authorized through the ERC-1271 path (see below), a validation holding this flag can also approve an arbitrary self-call on the account — including `installValidation`. The repository's own security notes call it out: *"for Modular Account this is a very powerful capability to grant as it allows validation functions to approve deferred actions on the account."* A session key should not have it.

The alternative to `isGlobal` is scoping the validation to an explicit selector list. That is the primary blast-radius control, and it is the reason session keys are usable at all.

**Validation hooks** run before the validation function, in installation order, across user-op, runtime and signature validation alike. Each receives its own data segment. For user operations the time ranges returned by every hook and by the validation function are **intersected**, so the effective window is the most restrictive one. A hook that should block a particular validation type has to revert for it; one that should ignore a type has to pass.

Gas-related checks belong in validation hooks rather than execution hooks, and the reason is timing: a validation success is what lets the EntryPoint charge the account. By the time an execution hook runs, the account is already liable for the gas.

**Execution hooks** run in the execution phase, as pre-only, post-only, or a pair. They attach either to a validation function — running whenever that validation is used, which is how per-key permissions work — or to an execution selector, running whenever that function is called regardless of who authorized it. The second form expresses account-wide rules: block transfers of NFTs held in cold storage, apply a resource lock. A pre/post pair can measure state differences, which is what makes an oracle-bounded swap limit expressible.

**Execution functions** let the account expose arbitrary external selectors, forwarded to the installing module, and register the matching ERC-165 interface IDs. A `skipRuntimeValidation` flag exists for view and permissionless functions. The example the documentation gives is a flash-loan callback.

## The nonce as a routing field

ERC-4337 splits the 256-bit nonce into a 192-bit parallel key and a 64-bit sequence, and leaves the key's contents to the account. MAv2 spends most of it on validation selection.

Identifying a module function normally takes 24 bytes — 20 for the address, 4 for the entity ID — which is exactly 192 bits, leaving nothing for the user. The global-uniqueness rule on validation entity IDs collapses that to 4 bytes, because a unique entity ID implies its module. What is left looks like this:

```
// Regular validation function
0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA__________________________ // user parallel nonce key
0x______________________________________BBBBBBBB__________________ // validation entity ID (4 bytes)
0x______________________________________________CC________________ // options byte
0x________________________________________________DDDDDDDDDDDDDDDD // sequential nonce

// Direct-call validation used as a user-op validation
0xAAAAAA__________________________________________________________ // user parallel nonce key
0x______BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB__________________ // caller address (20 bytes)
0x______________________________________________CC________________ // options byte
0x________________________________________________DDDDDDDDDDDDDDDD // sequential nonce

// Options byte
0b00000___ // unused
0b_____A__ // is direct-call validation (union tag)
0b______B_ // has deferred action
0b_______C // is global validation
```

Direct-call validations are the exception that forces the union: they all share the magic entity ID `0xFFFFFFFF`, so uniqueness cannot identify them and they are keyed by the caller's 20-byte address instead. The options byte carries the tag that says which reading applies.

Three consequences follow:

- **The caller picks the validation on every operation.** There is no implicit default, which is a deliberate gas trade — the account never has to search.
- **Changing validation changes the nonce key.** Operations under different validations are independently sequenced and can be in flight simultaneously; the user still keeps 19 bytes of parallel key for their own concurrency.
- **Entity ID reuse is a correctness bug, not a style issue.** A recycled ID routes a signature to the wrong validation. The repository asks clients to check off-chain that an entity ID was never used on that account, because nothing on-chain enforces it.

Internally the account keys its storage by a `ValidationLookupKey`: the same tagged union with the `isGlobal` and `hasDeferredAction` bits masked out. Those two describe how a validation is being *used* in one call, not which validation it *is*, so masking them keeps a validation mapped to one slot regardless of context.

## Signatures: one format, three entry points

User operations, ERC-1271 signatures and runtime authorization all share the ERC-6900 **sparse calldata segment** encoding — per-hook data addressed by index, terminated by a reserved index carrying the validation function's own data:

```
concat([
  hookIndex,     // uint8, 0x00..0xFE — present only for hooks that need data
  hookDataLen,   // uint32
  hookData,      // bytes
  ...
  0xFF,          // reserved index
  signatureData  // bytes, no length prefix
])
```

"Sparse" is the point: all hooks run, but only the ones needing input pay for calldata. A hook verifying Merkle inclusion gets its proof; a time-range hook gets nothing.

The three paths differ only in how the validation is chosen:

| Path | Validation selected by | Prefix |
|------|------------------------|--------|
| User operation | the nonce | none |
| `isValidSignature` (ERC-1271) | the signature itself | `PackedValidationLocator`, 5 or 21 bytes |
| `executeWithRuntimeValidation` | the authorization blob | `PackedValidationLocator`, 5 or 21 bytes |

There are two encodings of the same union, and mixing them up silently selects the wrong validation. `ValidationLocator` is always 21 bytes and **right-aligned**, options byte last, because it is handled as a `uint168` and hashed in EIP-712. `PackedValidationLocator` is 5 or 21 bytes and **left-aligned**, options byte first, so calldata parsing can branch on the tag before reading the rest.

The final segment's contents depend on the module. The fallback validation and `SingleSignerValidationModule` prefix a type byte — `0x00` for an EOA signature, 65 bytes of `r‖s‖v` behind it, `0x01` for an ERC-1271 contract owner. The byte exists so gas estimation does not have to guess which of the two paths will execute; Light Account uses the same trick for the same reason. `WebAuthnValidationModule` instead ABI-encodes a `WebAuthnAuth` struct and verifies a secp256r1 signature over `sha256(authenticatorData ‖ sha256(clientDataJSON))`. It has no runtime path at all: `validateRuntime` reverts `NotAuthorized()`.

Runtime validation for the single-signer and fallback cases needs no signature — the module simply checks `msg.sender` against the configured signer.

### Replay-safe hashing

The hash an ERC-1271 signature actually covers is never the raw hash passed to `isValidSignature`. It is wrapped:

```
ReplaySafeHash(bytes32 hash)
```

with an EIP-712 domain. The domain differs by validator, and the difference matters:

- **SMA fallback validation** — `verifyingContract` is the **account**.
- **`SingleSignerValidationModule` and `WebAuthnValidationModule`** — `verifyingContract` is the **module**, with the account address carried in the EIP-712 `salt` as `0x000000000000 ‖ account`.

Either way the signature binds to one account on one chain. One signer commonly owns several accounts, on several chains, at addresses derived from the same key; without this wrapper a Permit2 approval signed for one would validate on all of them. During deferred-action validation the extra wrapping is skipped, because the payload is already an EIP-712 hash.

Putting the pieces together, this is the full resolution path from an incoming user operation to a verdict:

![How Modular Account V2 resolves a UserOperation to a validation function]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/alchemy-mav2-validation-workflow.png)

## Deferred actions

A deferred action is a self-call executed **during the validation phase, before the main validation runs**. It exists to solve two problems that otherwise cost either a transaction or an impossibility.

**Just-in-time session keys.** Installing a session key in a separate owner transaction at sign-in adds a confirmation and a wait to the moment users are least patient, and wastes the gas entirely if the key is never used.

**ERC-20 paymaster approval.** A paymaster that pulls tokens from the account during validation needs an approval; the transaction that grants the approval cannot itself be sponsored by that paymaster. The dependency is circular, and no ordering of separate transactions breaks it.

The signed structure is small:

```
DeferredAction(uint256 nonce, uint48 deadline, bytes call)
```

- `nonce` — the user-operation nonce this action is bound to, with the has-deferred-action bit set. The account keeps no separate nonce space; to invalidate an unused signature you call `incrementNonce` on the EntryPoint for that key.
- `deadline` — a `block.timestamp` expiry, `0` meaning none.
- `call` — an account self-call, in practice `installValidation`. External calls must be wrapped in `execute` or `executeBatch`, and the authorizing validation's scope rules still apply to it.

It rides inside the user-operation signature:

```
concat([
  uint32 encodedDataLength,
  encodedData,              // innerValidationLocator(21) ‖ uint48 deadline ‖ selfCall
  uint32 deferredActionSigLength,
  deferredActionSig,        // validated through the ERC-1271 path
  userOpSignature           // normal sparse-segment format
])
```

The validation authorizing the deferred action need not be the one validating the user operation. That is the whole trick behind deferred session keys: the owner's validation authorizes installing the key, and the freshly installed key validates the operation.

Four restrictions apply, plus one open weakness:

- Only a validation with `isSignatureValidation` may authorize a deferred action.
- A validation with **any** validation hooks installed may not — the authorization flow does not match the shape of a user-op, runtime or signature validation call, so hooks cannot be invoked correctly. Silently skipping them would be worse.
- Nesting is not supported; the inner locator's deferred-action bit must be zero.
- Time bounds from the deferred action and from user-op validation are intersected.
- **The action is malleable by anyone who relays it.** Because it lives entirely in the signature field, it does not affect `userOpHash` beyond one bit in the nonce. A bundler holding two valid signed deferred actions for the same nonce can substitute one for the other. The documented mitigations are behavioural: only issue deferred actions the user operation cannot validate without — which both motivating cases satisfy — and keep at most one unmined action broadcast per nonce.

## Direct-call validation and nested accounts

A validation installed at the reserved entity ID `0xFFFFFFFF` authorizes a specific **caller address** to call the account directly, without wrapping anything in `executeWithRuntimeValidation`. When a call arrives from an address that is neither the account nor the EntryPoint, the account looks for a direct-call validation matching `(msg.sender, selector)`. Hooks still run.

Two motivations. The first is compatibility: legacy contracts call accounts with a plain interface and know nothing about `executeWithRuntimeValidation`. The second is gas — when the only authorization needed is "who is calling", the runtime dispatcher is pure overhead.

A third consequence follows from the same property. `handleOps` and `handleAggregatedOps` are non-reentrant, so a smart account cannot process another account's user operation inside its own execution phase, even with a valid signature. Runtime validation bypasses the EntryPoint entirely, so a parent account can drive a child account directly. Nested account ownership works because of a path that exists for a different reason.

## Session keys

Session keys are where all the preceding machinery is spent. The API-level permission types map onto hook modules, and every one of them is checked on-chain — there is no off-chain policy engine that a compromised backend could bypass.

| API permission | Enforced by | Notes |
|----------------|-------------|-------|
| `native-token-transfer` | `NativeTokenLimitModule` | |
| `gas-limit` | `NativeTokenLimitModule` | the module is gas-aware and accounts for whether a paymaster is paying |
| `erc20-token-transfer` | `AllowlistModule` | allowance is **cumulative over transfers and approvals**, not per-operation |
| `contract-access` | `AllowlistModule` | every function on one contract |
| `functions-on-contract` | `AllowlistModule` | selected functions on one contract |
| `functions-on-all-contracts` | `AllowlistModule` | selected functions on any address |
| `account-functions` | `AllowlistModule` | selectors on the account itself — installs, upgrades |
| `root` | — | full access |
| `expirySec` | `TimeRangeModule` | |
| (paymaster pinning) | `PaymasterGuardModule` | requires a specific paymaster |

The ERC-20 row is the one that misleads. A key described as "may spend 100 USDC" can spend nothing and instead approve 100 USDC to an address it controls, if that address is reachable under its allowlist. Permissions compose, and combining the token limit with a `functions-on-contract` restriction is what closes the gap.

A key scoped to auto-stake once a day within a capped budget on one verified contract is a stack of hooks on a single validation: `TimeRangeModule` for the expiry, `AllowlistModule` for the target contract, the selector and the ERC-20 budget, and `NativeTokenLimitModule` for gas.

### The flow

What defines the session-key flow is that **two different keys sign two different things**.

![Session key creation and use — the owner signs the grant, the session key signs each operation]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/alchemy-session-key-sequence.png)

1. **Delegate**, for EIP-7702 accounts that have never sent calls: send an empty call as the owner to install the delegation.
2. **`wallet_createSession`** with `account`, `chainId`, `expirySec` (Unix seconds), `key: {publicKey, type: "secp256k1"}` — the session key's **address**, not its full public key — and a `permissions` array. It returns a `sessionId` and an EIP-712 `signatureRequest`.
3. **The owner signs** that request. The `rawPayload` is already an EIP-712 hash, so it must be signed without the `personal_sign` prefix; with Foundry that means `cast wallet sign --no-hash`. This is a common integration error, and it fails at signature verification rather than at request time.
4. **`wallet_prepareCalls`** with `capabilities.permissions = {sessionId, signature}` and optionally `capabilities.paymasterService.policyId`.
5. **The session key signs** the returned hash — not the owner.
6. **`wallet_sendPreparedCalls`** with the same permissions capability and `signature: {type: "secp256k1", data}`.

Through the SDK the same thing is `client.grantPermissions({expirySec, key, permissions})`. Alchemy's reference application splits the two signers into two hooks, `useSessionAuthorization` for the owner grant and `useSessionKeySigner` for the per-operation signature, which is a clean way to keep the distinction visible in application code.

## Light Account

Not every application needs modules. Light Account is `SimpleAccount` with the sharp edges filed off:

1. Namespaced storage, so switching implementations does not clash.
2. `transferOwnership` — single-step, so the target must be verified before calling.
3. ERC-1271 both ways: validating user-operation signatures and exposing `isValidSignature`.
4. A `SignatureType` prefix byte selecting `ecrecover` or ERC-1271, for accurate gas estimation.
5. A factory built on Solady's `LibClone.createDeterministicERC1967`.
6. Factory ownership and EntryPoint staking, addressing the ERC-7562 mempool limits on unstaked entities.
7. Custom errors, and `SimpleAccountInitialized` renamed `LightAccountInitialized`.

`MultiOwnerLightAccount` adds an owner set updated through `updateOwners`, and a `CONTRACT_WITH_ADDR` signature type where the contract owner's address is concatenated into the signature as `type ‖ ownerAddress ‖ signature`.

One constraint on contract owners comes from outside the contract entirely. ERC-7562 validation rules forbid the owner's `isValidSignature` from using `TIMESTAMP` or `NUMBER`, and forbid the owner from being an ERC-1967 proxy — reading a constant implementation slot not associated with the account violates the storage access rules. A `LightAccount` therefore cannot own another `LightAccount` if the operations must pass through a public bundler.

| Feature | LightAccount | MultiOwnerLightAccount | Modular Account V1 | Modular Account V2 |
|---------|:---:|:---:|:---:|:---:|
| Multiple owners | ✗ | ✓ | ✓ | ✓ |
| Session keys | ✗ | ✗ | ✓ | ✓ |
| Ecosystem modules | ✗ | ✗ | ✓ | ✓ |
| EIP-7702 | ✗ | ✗ | ✗ | ✓ |
| Gas optimized | ✓ | ✓ | ✗ | ✓ |

## Rundler

Rundler is the bundler behind Alchemy's Bundler API, written in Rust and split into three tasks that run in one binary or as separate gRPC services. It supports EntryPoint v0.6 through v0.9 at their canonical addresses, and is tested on Ethereum, OP Stack chains, Arbitrum Orbit chains and Polygon PoS.

**Pool** keeps one mempool per enabled entry point. Incoming operations go through prechecks and then ERC-7562 simulation via `debug_traceCall` with a JavaScript tracer. Operations are rejected if `validUntil` is under 60 seconds away or `validAfter` is in the future. Reputation and throttling follow the spec, with file-based allowlists and blocklists on top. A chain tracker handles reorgs up to a configurable cache depth — past that depth, un-mined operations cannot be returned to the pool and are simply lost.

**Builder** runs a pool of workers, each paired 1:1 with a signer but able to build for *any* configured entry point. An **Assigner** picks the entry point each cycle by eligible-operation count, with starvation prevention that force-selects any entry point idle for `num_signers × starvation_ratio` cycles, and guarantees that no two workers bundle operations from the same sender at once.

Each worker is a state machine: `Building → Pending → Cancelling → CancelPending`. The cancelling states exist for a specific deadlock. When operations are available that pay more than the estimated gas price, but submission returns "replacement underpriced", raising the fee prices the operations out — an underpriced meta-state with a stuck pending transaction blocking everything behind it. After `max_replacement_underpriced_blocks`, the builder cancels: a "hard" cancellation sends a deliberately empty transaction, a "soft" one is an RPC interaction with no transaction at all.

Signing supports a raw private key, a BIP-39 mnemonic, or AWS KMS. The KMS path requires Redis, for key leasing: without it, two signers could pick the same key and collide on nonces. Submission goes through `eth_sendRawTransaction`, its conditional variant, Flashbots Protect on mainnet, or Bloxroute on Polygon.

**RPC** serves one endpoint for all entry-point versions, routing by the entry-point address in the request, and exposes an Alchemy-specific namespace:

| `rundler_` method | Purpose |
|-------------------|---------|
| `rundler_maxPriorityFeePerGas` | suggested priority fee |
| `rundler_getUserOperationGasPrice` | gas price — what `@alchemy/aa-infra`'s `estimateFeesPerGas` wraps |
| `rundler_getUserOperationStatus` | status lookup |
| `rundler_getMinedUserOperation` | mined operation lookup |
| `rundler_getPendingUserOperationBySenderNonce` | pending operation by sender and nonce |
| `rundler_dropLocalUserOperation` | drop from the local pool |
| `rundler_sendSponsoredDelegation`, `rundler_delegationStatus` | EIP-7702 delegation |

### Per-operation permissions

Rundler accepts non-standard per-request permissions, as HTTP headers (preferred) or a third positional parameter on `eth_sendUserOperation` (deprecated; headers win when both appear). They are honoured only if `rpc.permissions_enabled` is set.

| Permission | Effect |
|------------|--------|
| `trusted` | skip ERC-7562 simulation entirely, avoiding the costly trace call |
| `maxAllowedInPoolForSender` | override the per-sender mempool cap |
| `underpricedAcceptPct` | accept an operation at X % of estimated fees into the pool |
| `underpricedBundlePct` | bundle at X % of bundle fees — **the bundler absorbs the difference** |
| `bundlerSponsorship {maxCost, validUntil}` | the bundler pays all gas; requires zeroed fee fields and no paymaster |
| `eip7702Disabled` | reject EIP-7702 senders |

Every one of these disables a protection. Rundler's documentation is direct about it: they are for trusted internal proxies, never a public endpoint. `trusted` removes the simulation that stops mempool DoS; `bundlerSponsorship` spends the bundler's own funds and needs an out-of-band refund mechanism.

### Signature aggregation

Rundler implements [ERC-7766](https://eips.ethereum.org/EIPS/eip-7766) but requires an **explicit registry** of supported aggregators rather than open participation. The reasoning is that the EntryPoint offers no on-chain gas metering for aggregators, so a bundler must know an aggregator's cost model in advance to charge for it, and an aggregator it does not understand can DoS it. Costs are hardcoded per implementation as `execution_fixed_gas`, `execution_variable_gas`, `sig_fixed_length` and `sig_variable_length`, and charged through `preVerificationGas`.

The aggregator address travels as an extra field on `eth_sendUserOperation` and `eth_estimateUserOperationGas` — a documented deviation from both ERC-4337 and ERC-7766, letting the bundler act on the aggregator without first running `validateUserOp`. It is not part of `PackedUserOperation` and never reaches the chain.

One limitation caps the feature's usefulness today: PVG estimation and fee checks assume a bundle size of 1, so every operation pays the aggregator's full fixed cost. Rundler's own documentation notes this "renders a large class of aggregators as not useful". The shipped implementations are BLS (explicitly a proof of concept) and World Chain's Priority Blockspace for Humans.

## The hosted layer

Five methods cover the application surface:

| Method | Purpose |
|--------|---------|
| `wallet_requestAccount` | get or create the smart account for a signer |
| `wallet_createSession` | create a session key with permissions |
| `wallet_prepareCalls` | build the user operation, or the 7702 authorization plus the operation |
| `wallet_sendPreparedCalls` | submit the signed payload |
| `wallet_getCallsStatus` | poll |

The standard bundler methods stay available underneath for direct ERC-4337 use.

**Gas sponsorship** is policy-driven: create a policy in the dashboard, pass its `policyId` as `capabilities.paymasterService.policyId` on `wallet_prepareCalls`, or as `policyId` in the SDK config. Conditional rules, bundler-sponsored operations and an ERC-20 "pay gas with any token" path build on the same policy object.

**EIP-7702 is the default mode.** Pass the owner EOA address directly as `from`; no separate account request is needed. The API detects whether delegation is required and returns an array containing both the authorization and the transaction, so the delegation and the first call land in a single on-chain submission. Afterwards one signature per operation suffices. The delegate is `SemiModularAccount7702` at `0x69007702764179f14F51cdce752f4f775d74E139`, whose fallback signer defaults to `address(this)` — the EOA keeps its address, its assets and its own key as owner.

One caveat is easy to trip over: if the EOA is already delegated to a different contract, `sendCalls` will request re-delegation to MAv2, overriding whatever was there.

The SDK layers accordingly, and most integrations should stay at the top:

| Package | Level |
|---------|-------|
| `@alchemy/wallet-apis` | `createSmartWalletClient` — MAv2, account creation, gas estimation and bundler in one call |
| `@account-kit/react`, `@account-kit/core` | React and state layer: `createConfig`, auth sections, `useSigner` |
| `@alchemy/smart-accounts` | viem-compatible account objects: `toModularAccountV2({client, owner, mode})` |
| `@alchemy/aa-infra` | `estimateFeesPerGas`, bundler RPC types |
| viem `account-abstraction` | `createBundlerClient`, `createPaymasterClient` |

## What it costs

From the open `aa-benchmarks` repository, in EVM gas units. For scale, a plain Uniswap swap without account abstraction runs around 150 000 gas.

| Operation | MAv2 | Coinbase SW | Biconomy Nexus | Kernel v3.1 | Safe v1.4.1 | SimpleAccount |
|-----------|-----:|------------:|---------------:|------------:|------------:|--------------:|
| Deployment | 233 004 | 317 904 | 342 381 | 338 419 | 435 486 | 297 367 |
| Native transfer | 158 725 | 156 812 | 164 351 | 190 912 | 176 479 | 151 045 |
| ERC-20 transfer | 182 665 | 181 014 | 188 136 | 214 817 | 200 732 | 175 283 |
| Uniswap V3 swap | 201 790 | 200 573 | 207 286 | 234 378 | 220 464 | 194 829 |

The deployment row is where the design shows. On the per-operation rows MAv2 sits within a few thousand gas of Coinbase Smart Wallet and SimpleAccount, neither of which offers modules — which is the more defensible claim: the modular machinery costs almost nothing when it is not used, because the fallback validation and the nonce-encoded selection avoid searching for it.

## Conclusion

Alchemy's stack is a set of consistent answers to the questions ERC-4337 declines to answer. Validation selection lives in the nonce, which buys a compact encoding at the cost of a global-uniqueness rule on entity IDs. The common single-owner case gets a fallback validation compiled into the account, which buys sub-100k deployment at the cost of four implementation variants that are not interchangeable. Session keys get their permissions enforced by hook modules on-chain, which buys real guarantees at the cost of a permission model the integrator has to read carefully — the ERC-20 allowance covering approvals as well as transfers being the clearest example. Deferred actions buy atomic session-key installation at the cost of a bundler-substitutable payload.

None of these are free, and the repository documentation is unusually direct about the prices — the EIP-7702 delegate warning, the deferred-action malleability note, the aggregator bundle-size limitation and the "use in production at your own risk" banner on Rundler are all upstream text, not external criticism. That candour is what makes the stack readable as a case study rather than a product page.

![Mindmap summary of Alchemy's smart wallet and account abstraction stack]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/2026-07-30-alchemy-smart-wallet-account-abstraction.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Modular Account V2 (MAv2)** | Alchemy's flagship smart account, implementing ERC-4337 and ERC-6900 v0.8, deployed as an ERC-1967 proxy with ERC-7201 namespaced storage. |
| **Semi-modular account** | An MAv2 variant carrying a fallback validation built into the contract at entity ID `0`, so a single-owner account works without installing a validation module. |
| **Entity ID** | A `uint32` identifying one installation of a module on one account; for validations it must be unique across the entire account, which lets 4 bytes identify the module too. |
| **Validation function** | A module function that authorizes an action — a user operation, an ERC-1271 signature, or a runtime call — installed with flags controlling which of the three it may authorize. |
| **Validation hook** | A module function running before a validation function, in installation order, whose returned time ranges are intersected with the validation's own. |
| **Execution hook** | A module function running in the execution phase, attached either to a validation function (per-key permissions) or to an execution selector (account-wide rules). |
| **Sparse calldata segment** | The ERC-6900 encoding used by all three authorization paths: per-hook data addressed by index `0x00`–`0xFE`, terminated by reserved index `0xFF` carrying the validation's own data. |
| **Deferred action** | An EIP-712-signed account self-call executed during the validation phase before the main validation, used for just-in-time session-key installation and ERC-20 paymaster approvals. |
| **Direct-call validation** | A validation installed at entity ID `0xFFFFFFFF` that authorizes a specific caller address to call the account directly, without wrapping the call in `executeWithRuntimeValidation`. |
| **Rundler** | Alchemy's Rust ERC-4337 bundler, split into Pool, Builder and RPC tasks, supporting EntryPoint v0.6 through v0.9. |

## Annex — Security Implementation Checklist

Derived from the design constraints described above. Each row is a property an implementation or integration either meets or fails.

### Account deployment and upgrade

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The EIP-7702 delegate destination is `SemiModularAccount7702` and no other variant. | Other variants expose an unguarded initializer at the EOA's address; anyone can call it and install their own validation. |
| ☐ | `SemiModularAccountBytecode` is used only for new deployments through `AccountFactory`, never as an upgrade target. | The owner is read from proxy bytecode an arbitrary proxy does not carry, producing an ownerless account. |
| ☐ | Accounts are deployed behind a proxy, not used directly. | OpenZeppelin's `Initializable` permits reentering the initializer during the constructor, allowing an attacker to install an extra validation. |
| ☐ | Before upgrading a proxy into MAv2, the `initialized` value at the MAv2 namespaced slot is read. | A proxy that was previously an MAv2 keeps its old ownership configuration, and `initializer` functions will not run. |
| ☐ | The upgrade target is confirmed to be an ERC-1967 proxy via the ERC-1822 `proxiableUUID` slot. | Upgrading a non-proxy leaves the account unreachable. |

### Validation and permissions

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Validation entity IDs are unique per account and never reused. | Nonce-encoded selection resolves a signature to the wrong validation. |
| ☐ | `isSignatureValidation` is granted only where deferred-action authority is intended. | The holder can approve arbitrary account self-calls, including `installValidation`. |
| ☐ | Session keys are scoped to an explicit selector list, not `isGlobal`. | The key reaches every function in the global pool, defeating the permission model. |
| ☐ | Installed execution selectors are checked against native account selectors. | A selector shadowing `execute` or `installValidation` is a takeover path. |
| ☐ | Gas-related limits are enforced in validation hooks, not execution hooks. | Validation success lets the EntryPoint charge the account before any execution hook runs. |
| ☐ | ERC-20 allowances are treated as cumulative over transfers **and** approvals. | A key limited to 100 USDC approves 100 USDC to an address it controls. |
| ☐ | Token limits are combined with target and selector allowlists. | A spend limit alone does not constrain where the value goes. |

### Signature handling

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | ERC-1271 hashes are wrapped in `ReplaySafeHash` before verification. | A signature replays across every account the same signer owns, on every chain. |
| ☐ | The EIP-712 domain matches the validator: account for SMA fallback, module with account-in-`salt` for modules. | Signatures validate under the wrong separator, or valid signatures are rejected. |
| ☐ | `ValidationLocator` (right-aligned, 21 bytes) and `PackedValidationLocator` (left-aligned, 5 or 21 bytes) are not interchanged. | The wrong validation is selected, silently. |
| ☐ | The `SignatureType` prefix byte matches the owner's actual type. | An EOA signature is routed to `isValidSignature`, or a contract signature to `ecrecover`. |
| ☐ | WebAuthn validations are never relied on for runtime calls. | `validateRuntime` always reverts `NotAuthorized()`. |
| ☐ | Contract owners of a Light Account avoid `TIMESTAMP`/`NUMBER` and are not ERC-1967 proxies. | ERC-7562 rules reject the operation at the bundler, so it never mines. |

### Deferred actions

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every deferred action issued is one the user operation cannot validate without. | A relayer substitutes a different signed action for the same nonce, with no effect on `userOpHash`. |
| ☐ | At most one unmined deferred action is broadcast per nonce. | Multiple valid alternatives give an attacker something to substitute. |
| ☐ | Deferred-action nonces are unique and free of dependencies. | A stale action replays under a reused nonce. |
| ☐ | The authorizing validation carries no validation hooks. | The flow cannot invoke them, so hook-based restrictions are skipped entirely. |
| ☐ | Unused actions are invalidated with EntryPoint `incrementNonce`. | The signature stays usable until its deadline. |

### Batching and direct calls

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Self-calls in `executeBatch` are flattened; no `execute`/`executeBatch` nested inside. | Nested self-calls reach account functions past the validation-applicability check. |
| ☐ | Direct-call validations are scoped to the intended selectors. | The authorized caller reaches more of the account than intended. |

### Bundler operation

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | `rpc.permissions_enabled` is off, or the endpoint is not publicly reachable. | `trusted` disables simulation and opens mempool DoS; `bundlerSponsorship` drains the bundler's funds. |
| ☐ | KMS signing uses Redis key leasing. | Two workers lease the same key and collide on transaction nonces. |
| ☐ | Reorgs deeper than the pool cache are handled out of band. | Un-mined operations cannot re-enter the pool and are lost. |
| ☐ | Custom aggregator cost values are measured by simulation before registration. | The bundler underprices `preVerificationGas` and loses funds, or the aggregator stalls bundling. |

## Frequently Asked Questions

**Q: Why must Modular Account V2 validation entity IDs be unique across the whole account, when ERC-6900 does not require it?**

Because validation selection is encoded in the ERC-4337 parallel nonce key, which is 192 bits — exactly 24 bytes. Identifying a module function the normal way takes 20 bytes for the module address plus 4 for the entity ID, consuming the entire key and leaving the user no room for their own parallel nonce.

Global uniqueness means a 4-byte entity ID implies its module address, cutting the identifier to 5 bytes including the options byte and leaving 18 bytes for user-defined parallelism. Nothing on-chain enforces the rule, so clients must check it before installing a validation; a reused ID routes a signature to the wrong validation function.

**Q: What is a deferred action, and which two problems does it exist to solve?**

A deferred action is an EIP-712-signed account self-call executed during the user-operation validation phase, before the main validation runs. It solves:

- **Just-in-time session keys.** Installing a session key in a separate owner transaction adds a confirmation and a wait at sign-in, and wastes the gas if the key is never used. A deferred action installs the key and lets it validate the same operation.
- **ERC-20 paymaster approval.** A paymaster that pulls tokens during validation needs an approval, but the transaction granting it cannot be sponsored by that same paymaster. The dependency is circular, and no ordering of separate transactions breaks it.

The validation authorizing the deferred action need not be the one validating the user operation, which is what makes the first case work.

**Q: Why can only `SemiModularAccount7702` be used as an EIP-7702 delegate?**

The other MAv2 variants have initializer functions with no access control. They are safe in a proxy because the proxy pattern makes initialization one-shot, and the deployment flow calls the initializer immediately. Under EIP-7702 there is no such flow: delegating an EOA to one of those implementations places a live, unguarded initializer at the EOA's own address, and anyone can call it to install a validation they control.

`SemiModularAccount7702` is written for this position — its fallback signer defaults to `address(this)`, so the EOA is its own owner from the first block, and `upgradeToAndCall` is disabled because a 7702-delegated account cannot upgrade that way.

**Q: A session key is granted `erc20-token-transfer` with a 100 USDC allowance and `contract-access` on a staking contract. What can it actually do with the USDC?**

More than the permission name suggests. The allowance is cumulative across transfers *and* approvals, not per-operation, so within that 100 USDC the key may issue `approve` calls rather than transfers. Whether it can approve an attacker-controlled spender depends on the second permission: `contract-access` scoped to the staking contract does not authorize calling the USDC contract at all, so in this configuration the allowance is only spendable through paths the staking contract itself opens.

The general lesson is that a spend limit constrains the amount, not the destination. Pairing it with a `functions-on-contract` or `contract-access` restriction is what constrains where value goes, and reading the two permissions in isolation gives the wrong answer.

**Q: Rundler exposes a `trusted` permission that skips ERC-7562 simulation. Why does that permission exist, and what does enabling it publicly cost?**

It exists for internal proxies with a trust relationship to the sender. ERC-7562 simulation runs a `debug_trace_call` over the operation's validation phase to check it does not use banned opcodes, touch other accounts' storage, or otherwise behave unpredictably. That trace is expensive, and for an operation the operator already vouches for, it is redundant latency.

Exposed publicly it removes the mechanism that stops an attacker submitting operations whose validation succeeds under simulation and fails on-chain — the mempool DoS that the simulation rules exist to prevent. Rundler gates it behind `rpc.permissions_enabled` and states the permissions are meant only for trusted connections. The same reasoning applies with money attached to `bundlerSponsorship`, which makes the bundler pay all gas and requires an out-of-band refund mechanism.

**Q: How do the ERC-1271 replay-safe hash domains differ between the SMA fallback and `SingleSignerValidationModule`, and why are they not the same?**

For the SMA fallback validation, `verifyingContract` in the EIP-712 domain is the **account**. For `SingleSignerValidationModule` and `WebAuthnValidationModule` it is the **module**, with the account address carried in the domain `salt` as `0x000000000000 ‖ account`.

They differ because of where the verifying code sits. The fallback is part of the account contract, so the account is the natural verifier. A validation module is one contract serving many accounts, so using the module as `verifyingContract` isolates it from other modules, and the account has to be reintroduced through the `salt` to keep a signature bound to one account. Both arrangements achieve the same property — a signature valid for one account on one chain — through different fields, and both are required because one signer commonly owns several accounts at addresses derived from the same key.

**Q: MAv2 deploys for roughly half the gas of Safe or Kernel, yet lands within a few thousand gas of SimpleAccount on a token transfer. Is the modularity therefore free?**

Close to free when unused, which is the design goal rather than an accident. Two mechanisms produce it. The fallback validation at entity ID `0` is compiled into the account, so the common single-owner case never installs a module and never pays for one. And validation selection is read out of the nonce rather than searched for, so dispatch costs a few bytes of decoding regardless of how many validations are installed.

What is not free is what you add: each validation hook is an external call with its own storage reads, so a session key carrying four permission modules costs meaningfully more per operation than the owner's fallback path. The benchmarks measure the unloaded account.

## References

- [Modular Account](https://github.com/alchemyplatform/modular-account) — Alchemy, including `doc/Architecture.md` and `doc/Data-Encoding.md`
- [Light Account](https://github.com/alchemyplatform/light-account) — Alchemy
- [Rundler](https://github.com/alchemyplatform/rundler) — Alchemy, including `docs/architecture/`
- [Wallet APIs documentation](https://alchemy.com/docs/wallets) — Alchemy
- [aa-benchmarks](https://github.com/alchemyplatform/aa-benchmarks) — open gas benchmarks across smart account implementations
- [ERC-4337: Account Abstraction Using Alt Mempool](https://eips.ethereum.org/EIPS/eip-4337)
- [ERC-6900: Modular Smart Contract Accounts and Plugins](https://eips.ethereum.org/EIPS/eip-6900)
- [ERC-7562: Account Abstraction Validation Scope Rules](https://eips.ethereum.org/EIPS/eip-7562)
- [ERC-7766: Signature Aggregation for ERC-4337](https://eips.ethereum.org/EIPS/eip-7766)
- [EIP-7702: Set EOA account code](https://eips.ethereum.org/EIPS/eip-7702)
- [ERC-1271: Standard Signature Validation Method for Contracts](https://eips.ethereum.org/EIPS/eip-1271)
- [Claude Code](https://claude.com/product/claude-code)
