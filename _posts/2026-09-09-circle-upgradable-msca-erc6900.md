---
layout: post
title: "Inside Circle's UpgradableMSCA — A Modular Smart Contract Account Under ERC-6900"
date:   2026-09-09
lang: en
locale: en-GB
categories: blockchain ethereum solidity wallet
tags: blockchain ethereum solidity erc-4337 erc-6900 account-abstraction smart-wallet modular-account circle entrypoint
description: "How Circle's UpgradableMSCA implements an ERC-6900 modular account: validation entities, hook ordering, ERC-7201 storage, and the factory that deploys it."
image: /assets/article/blockchain/ethereum/erc-4337/2026-09-09-circle-upgradable-msca-mindmap.png
isMath: false
---

`UpgradableMSCA` is the smart-contract wallet in Circle's `buidl-wallet-contracts` repository, and the contract file itself is exactly a hundred lines, licence header included. Almost everything it does comes from `BaseMSCA`, a 1,086-line base class that implements [ERC-6900](https://eips.ethereum.org/EIPS/eip-6900): the standard that splits a smart account into a validation layer, an execution layer, and a hook layer, each populated by separate module contracts the owner installs and removes.

The point of that split is to make one account address outlive its own authentication logic. A user starts with a single ECDSA signer, later moves to a weighted multisig with a passkey as one of the participants, later still adds a spending-limit hook, and the address that holds their USDC never changes. Circle's implementation adds a second axis of longevity on top: the account sits behind an ERC-1967 proxy, so the implementation can be replaced as well.

This article reads the contracts at commit `3c47aa94`. It covers what `UpgradableMSCA` adds over its base, the storage layout that makes an upgradeable modular account possible, how a validation function is selected and how hooks are ordered around it, the guard rails on self-calls and installable selectors, the factory that computes account addresses, and the modules Circle ships alongside.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Two generations live in the repository

Before reading any code, one fact settles which version matters. The repository holds two independent implementations under `src/msca/6900/`:

- **`v0.7`** targets the earlier ERC-6900 draft, where extensions are called **plugins**, installation is delegated to a separate `PluginManager` contract, and a plugin declares a manifest hash plus dependencies on other plugins. This is the generation deployed on chain: every script under `script/` imports from `v0.7`, and `script/000_ContractAddress.sol` carries a live `PLUGIN_MANAGER_ADDRESS`.
- **`v0.8`** targets ERC-6900 v0.8, where extensions are **modules**, installation logic moved inside the account, dependencies are gone, and validation gained a global mode. Its own README states plainly that the contracts "are not deployed on any mainnets yet".

The rest of this article reads `v0.8`, because it is the design Circle is moving to and the cleaner expression of the standard, with a section at the end on what changed from `v0.7`.

## What `UpgradableMSCA` adds over `BaseMSCA`

The concrete contract is deliberately thin. It contributes five things.

- **An account identifier.** `ACCOUNT_ID = "circle.msca.2.0.0"`, returned by `accountId()`, following the ERC-6900 `vendor.account.semver` convention.
- **One-shot initialisation.** `initializeWithValidation` installs the first validation function and is guarded by `walletStorageInitializer`, a fork of OpenZeppelin's `Initializable` that keeps its flags in the account's namespaced storage rather than at slot 0.
- **Token callbacks.** It inherits `DefaultCallbackHandler`, so the account answers `onERC721Received`, `onERC1155Received`, `onERC1155BatchReceived` and `tokensReceived` without any module installed, and folds those interface ids into `supportsInterface`.
- **UUPS upgradeability.** It overrides `upgradeToAndCall` to run it through the account's own permission machinery.
- **An empty upgrade authorisation.**

That last one deserves its own line, because it looks alarming and is not:

```solidity
function upgradeToAndCall(address newImplementation, bytes memory data)
    public payable override onlyProxy wrapNativeExecutionFunction
{
    super.upgradeToAndCall(newImplementation, data);
}

// solhint-disable-next-line no-empty-blocks
function _authorizeUpgrade(address newImplementation) internal override {}
```

`_authorizeUpgrade` is empty on purpose. The gate is the `wrapNativeExecutionFunction` modifier, which routes the call through `_checkCallPermission` exactly like `execute` or `installValidation`. An upgrade arriving from the EntryPoint has already passed the account's user-operation validation; an upgrade arriving from any other address must satisfy a direct-call validation installed for that caller. Which key or module may upgrade the account is therefore a per-account configuration rather than a constant in the implementation, which is what the contract's comment means by "more granular ACLs to the upgrade mechanism should be enforced by modules".

![Proxy, implementation and module surface: the factory deploys one shared UpgradableMSCA implementation and one ERC1967Proxy per user, the proxy delegatecalls into BaseMSCA which reads an ERC-7201 namespaced storage region, and validation and hook logic lives in separate module contracts]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/upgradable-msca-architecture-concept.png)

## Storage: a namespace, not a slot

An upgradeable account that also hosts third-party modules has two ways to corrupt itself. A new implementation can shift the layout under the old data, and a module can write where the account expected something else. `WalletStorageV2Lib` answers the first:

```solidity
// 1. id = "circle.msca.v2.storage"
// 2. keccak256(abi.encode(uint256(keccak256(id)) - 1)) & ~bytes32(uint256(0xff))
bytes32 internal constant WALLET_STORAGE_SLOT =
    0x1ffef775e8122370efaac4f28eeec94f03b0484eca026ee3ab713094c73f5d00;
```

This is [ERC-7201](https://eips.ethereum.org/EIPS/eip-7201) namespaced storage. The whole account state hangs off one derived slot instead of starting at slot 0, so a different implementation placed behind the same proxy finds its data exactly where it left it, provided it uses the same namespace id. The trailing mask clears the low byte, aligning the region to a 256-slot boundary; the library's own comment ties that choice to anticipated gas-schedule changes after a Verkle migration, where a group of 256 slots may warm together.

The layout itself is three mappings and two initialisation flags:

```solidity
struct Layout {
    mapping(bytes4 => uint256) supportedInterfaces;
    mapping(bytes4 => ExecutionStorage) executionStorage;
    mapping(ModuleEntity validationFunction => ValidationStorage) validationStorage;
    uint8 initialized;
    bool initializing;
}
```

`supportedInterfaces` is a **counter**, not a boolean, so two modules declaring the same interface id both increment it and an uninstall of one does not silently strip ERC-165 support that the other still provides.

The second corruption path, a module writing into account storage, is handled by not letting modules write there at all. Module state lives in the module's own contract, keyed by the account address, which is why `SingleSignerValidationModule` holds `mapping(uint32 entityId => mapping(address account => address)) signers` rather than reaching into the account.

## Validation: entities, flags, and two ways to be allowed

A validation function is identified by a **`ModuleEntity`**: 24 bytes packing a module address and a `uint32` entity id. The entity id is what lets one module contract serve several distinct roles for the same account, and the multisig module uses it for exactly that, keeping one signer group under entity 0 for cheap single-signature spending and a stricter group under another id for larger amounts.

Every user operation names its validation function in the first bytes of the signature field:

```text
 0                       24    25
 +-----------------------+-----+---------------------------------------+
 | ModuleEntity          | flag| sparse-segmented hook data + signature |
 |  20-byte module addr  | 0/1 |                                       |
 |  + uint32 entityId    |     |                                       |
 +-----------------------+-----+---------------------------------------+
```

Byte 24 is the global-validation flag, and it selects between the two ways a validation function can be permitted for a given selector:

- **Global validation** (`flag == 1`) applies to every native execution function and to any module execution function whose manifest set `allowGlobalValidation`. It is the "this key can drive the whole account" mode, and it requires the `isGlobal` flag on the installed validation.
- **Per-selector validation** (`flag == 0`) applies only to the selectors explicitly listed for that `ModuleEntity` at install time. It is the session-key mode: a validation that may call `transfer` and nothing else.

`_checkValidationForSelector` resolves the two, and a third mode, `EITHER`, is used internally for direct calls. The `ValidationFlags` byte carries three independent bits, `isGlobal`, `isSignatureValidation` and `isUserOpValidation`, so a validation authorised to sign ERC-1271 messages is not automatically authorised to drive user operations.

Everything after byte 25 is consumed by `SparseCalldataSegmentLib`: each pre-validation hook takes one segment, and whatever remains is the final segment handed to the validation module. A hook that needs no data of its own simply has no segment at its index.

### Intersecting the answers

Hooks and the validation function each return a packed `validationData`, and `ValidationDataLib._intersectValidationData` folds them together. The time range narrows, taking the later `validAfter` and the earlier `validUntil`. The authorizer field follows a priority: an unexpected value wins over failure, failure wins over success. And an empty resulting window is converted into an outright failure, so a set of hooks whose windows do not overlap cannot accidentally produce a passing result:

```solidity
if (validationData.validAfter >= validationData.validUntil && validationData.authorizer == address(0)) {
    validationData.authorizer = address(1);
}
```

`BaseMSCA` then rejects any authorizer that is neither `address(0)` nor `address(1)` with `InvalidAuthorizer`, which rules out a module trying to route the account through a signature aggregator.

![A UserOperation through UpgradableMSCA: the EntryPoint calls validateUserOp, the account reads the ModuleEntity and global flag from the signature, runs the pre-validation hooks and the validation module and intersects their answers, then executeUserOp self-calls the trimmed calldata between validation-associated and selector-associated execution hooks]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/upgradable-msca-userop-sequence.png)

## Hooks, and the order they run in

There are three kinds of hook, and they attach to different things:

- **Validation hooks** attach to a `ModuleEntity` and run before it, as `preUserOpValidationHook`, `preRuntimeValidationHook`, or `preSignatureValidationHook` depending on the entry path.
- **Validation-associated execution hooks** also attach to a `ModuleEntity`, and run around the execution that the validation authorised. A spending-limit hook belongs here, because the limit is a property of the key being used, not of the function being called.
- **Selector-associated execution hooks** attach to a `bytes4` selector through a module's `ExecutionManifest`, and run whenever that function is called, whichever validation approved it.

`MSCACallFlow.t.sol` pins the resulting order as an explicit array of 21 recorded calls. Reading it back: validation hooks in install order, then the validation function, then validation-associated pre-execution hooks, then selector-associated pre-execution hooks, then the execution itself, then the post hooks unwinding in reverse, selector-associated first and validation-associated last.

Two details in `HookLib` make that unwinding safe. The post-hook list is **copied before any pre-hook runs**, so a pre-hook that installs or removes hooks cannot change which post-hooks fire. And a hook declared pre-only contributes nothing on the way out, while a post-only hook contributes nothing on the way in, which is why the recorded order skips indices rather than running every hook twice.

![Call order for one execution: pre-validation hooks in install order, the validation function unless the caller is the module providing it, validation-associated then selector-associated pre-execution hooks, the execution function, then both hook groups unwinding in reverse order]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/upgradable-msca-call-flow-workflow.png)

### Why validation-associated hooks force `executeUserOp`

Validation-associated execution hooks are stored against the validation function, and only `executeUserOp` receives the full user operation, so only `executeUserOp` can look up which hooks the signature selected. `BaseMSCA` refuses the combination that cannot work:

```solidity
if (
    bytes4(userOp.callData[:4]) != this.executeUserOp.selector
        && WalletStorageV2Lib.getLayout().validationStorage[validationFunction].executionHooks.size() > 0
) {
    revert RequireUserOperationContext();
}
```

An integrator who installs a spending-limit hook and keeps building calldata that starts with `execute` rather than `executeUserOp` will see every operation fail at validation. The selector prefix is not cosmetic; it is what tells the EntryPoint to hand the account the operation itself.

## Guard rails

Three checks in `BaseMSCA` exist to stop a permitted call from becoming an unpermitted one.

**Self-calls through `execute` are banned outright.** If the target of `execute` is the account itself, the call reverts with `SelfCallRecursionDepthExceeded`. Otherwise a session key permitted to call `execute` could aim it at the account's own `installValidation` and grant itself anything.

**Self-calls through `executeBatch` are allowed, but flattened.** An inner call whose target is the account may not itself be `execute` or `executeBatch`, so nesting cannot be used to hide a selector from inspection, and every inner selector is checked against the same validation function as the outer one. The comment in the source calls this "all self-calls must occur at the top level of the batch".

**Module execution functions cannot shadow the account.** `_installExecution` rejects any selector that `SelectorRegistryLib` classifies as native, ERC-4337, or part of `IModule`. Without it, a module could register `validateUserOp` or `onInstall` as its own execution function and intercept the account's dispatch.

There is also a subtler rule in `_checkCallPermission`. Calls from the EntryPoint, from the account itself, or to a function whose manifest set `skipRuntimeValidation` are already trusted at that layer. Everything else, which in practice means a module calling back into the account, must satisfy a **direct-call validation**: a `ModuleEntity` packing the caller's address with `DIRECT_CALL_VALIDATION_ENTITY_ID`. Its validation function is skipped, since the caller is the module that would provide it, but its validation hooks and execution hooks still run.

## The factory

`UpgradableMSCAFactory` is an `Ownable2Step` contract that deploys the shared implementation once, in its own constructor, and then one `ERC1967Proxy` per account.

```solidity
mixedSalt = keccak256(abi.encodePacked(_sender, _salt));
bytes32 code = keccak256(
    abi.encodePacked(
        type(ERC1967Proxy).creationCode,
        abi.encode(
            address(ACCOUNT_IMPLEMENTATION),
            abi.encodeCall(
                UpgradableMSCA.initializeWithValidation, (_validationConfig, _selectors, _installData, _hooks)
            )
        )
    )
);
addr = Create2.computeAddress(mixedSalt, code, address(this));
```

Four properties follow from that expression.

- **The address commits to the initial configuration.** The init calldata is part of the CREATE2 creation code hash, so a different first validation function, a different selector list, or a different hook set yields a different address. An account cannot be deployed at a known address with a signer the user did not agree to.
- **The salt is namespaced.** `mixedSalt` mixes a caller-supplied `_sender` identifier with a salt, so Circle's backend can partition the address space per user without collisions.
- **Deployment is idempotent.** `createAccountWithValidation` returns the existing account if code is already present at the computed address, which is what makes it safe to call from an ERC-4337 `initCode` that may be replayed.
- **A new factory means new addresses.** `ACCOUNT_IMPLEMENTATION` is deployed inside the factory's constructor and read into the creation-code hash, so redeploying the factory moves every counterfactual address.

The factory also keeps an owner-controlled `isModuleAllowed` allowlist, checked against the validation module and against the first 20 bytes of every hook blob, with the contract's comment stating the reason: "We only support fully audited modules during account creation for security reasons." Modules outside the allowlist can still be installed later through `installValidation`, once the account exists and its own validation governs the change.

Two operational details round it out. The factory carries `addStake`, `unlockStake` and `withdrawStake`, and it needs them: deployment happens inside the validation phase, `_getAddressWithValidation` reads the factory's own `isModuleAllowed` mapping there, and [ERC-7562](https://eips.ethereum.org/EIPS/eip-7562) only lets an entity touch its own storage during validation if it is staked. The contract's NatSpec states the requirement directly. And `renounceOwnership` is overridden to revert with `Unsupported`, so the allowlist cannot be frozen by an accidental renounce.

## The modules Circle ships

Three modules accompany the v0.8 account, and between them they cover the module roles the standard defines.

**`SingleSignerValidationModule`** is the baseline: one signer per `(entityId, account)` pair, verified with `SignatureChecker`, so the signer may itself be a contract implementing ERC-1271. `validateUserOp` checks the signature over `userOpHash.toEthSignedMessageHash()`, while `validateSignature` wraps the hash in an EIP-712 struct first, through `BaseERC712CompliantModule`, to keep an ERC-1271 signature from being replayed against another account.

**`WeightedMultisigValidationModule`** implements a weighted threshold scheme supporting EOA signers, ERC-1271 contract signers, and raw secp256r1 public keys for passkeys, with weights from 1 to 1,000,000 and up to 1,000 signers. Its most interesting design decision concerns gas fields: when several people sign one operation over an extended period, network fees move between signatures. The module lets the first *k−1* signers sign a **minimal** user operation, with only `sender`, `nonce`, `initCode` and `callData` populated, and lets the final signer fill in the gas fields and sign the complete object, marking that difference by adding 32 to the signature's `v` byte. The encoding is documented in the repository's `Smart_Contract_Signatures_Encoding.md`, which extends the [Safe signature encoding](https://docs.safe.global/advanced/smart-account-signatures#encoding) with secp256r1 support.

**`ColdStorageAddressBookModule`** is both a validation hook and an execution module. As a hook it decodes the calldata of `execute` or `executeBatch`, works out the recipient of each call, and reverts with `UnauthorizedRecipient` when that address is not in the account's address book; as an execution module it exposes `addAllowedRecipients` and `removeAllowedRecipients`, which are themselves subject to the account's validation. Its recipient list is stored in the module under an associated linked list keyed by the account, which the interface comment ties directly to the bundler rules: "bundler validation rules only allow the entity to access the sender associated storage".

The v0.8 version is unfinished, and says so: `preUserOpValidationHook` carries a `TODO: add tests when we revamp this WIP module soon`, `preSignatureValidationHook` reverts unconditionally, and the hook is wired to exactly two entity ids covering `execute` and `executeBatch`, reverting `Unsupported` for anything else. The deployed cold-storage restriction is the v0.7 `ColdStorageAddressBookPlugin`, not this one.

## What changed from v0.7

The deployed generation differs in four ways that matter to anyone reading both.

- **Installation moved into the account.** In v0.7, `installPlugin` builds calldata for a separate `PluginManager` contract and runs it with `delegatecall`, so the manager's code executes against the account's storage. In v0.8 the equivalent logic is `_installExecution` and `_installValidation` inside `BaseMSCA`, and the `PluginManager` immutable is gone.
- **Validation identifiers grew.** v0.7's `FunctionReference` packs an address with a `uint8` function id into 21 bytes; v0.8's `ModuleEntity` packs an address with a `uint32` entity id into 24 bytes.
- **Global validation arrived.** v0.7 stores one `userOpValidationFunction` and one `runtimeValidationFunction` per selector, so every selector must be wired individually. v0.8 adds the global mode described above.
- **Storage was realigned.** `WalletStorageV1Lib` uses `circle.msca.v1.storage` and, as its comment admits, predates the finalisation of ERC-7201, so it is not 256-aligned. v0.8 moved to `circle.msca.v2.storage` with the alignment mask, and the comment explains the decision not to migrate v1 accounts: doing so would be a breaking change for accounts already deployed.

Manifest hashes and plugin dependencies also disappeared. In v0.7 a plugin declares the hash of its own manifest and may depend on validation functions provided by other plugins, which the account must resolve at install time; v0.8 drops both, and `UpgradableMSCA.initializeUpgradableMSCA` in v0.7 passes an empty dependency array precisely because the initial install cannot resolve them.

![Circle MSCA v0.7 and v0.8 side by side: v0.7 delegatecalls a separate PluginManager and uses 21-byte FunctionReferences with per-selector validation, while v0.8 installs modules inside BaseMSCA using 24-byte ModuleEntities, global or per-selector validation, and ERC-7201 aligned storage]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/msca-v07-vs-v08-concept.png)

## Conclusion

`UpgradableMSCA` is short because the interesting decisions are made one level down and one level out. `BaseMSCA` decides how a validation function is named, how it is matched to a selector, and how hooks wrap the call. The modules decide what a signature means. The account contract itself contributes an identifier, a one-shot initialiser, token callbacks, and an upgrade path whose authorisation it deliberately declines to hard-code.

The parts worth studying are the ones the standard leaves room to get wrong. Copying the post-hook list before running any pre-hook closes the window in which a pre-hook could change which post-hooks fire. Banning `execute` self-calls and flattening `executeBatch` self-calls closes the route from a narrow session key to full account control. Intersecting hook time ranges, and converting an empty window into a failure, keeps a set of independently-written hooks from combining into a permission none of them granted. And putting the account's whole state behind an ERC-7201 namespace is what makes replacing the implementation a routine operation rather than a migration.

Two things are worth keeping in view when reading this code as a user rather than an author. The v0.8 tree is not deployed; the accounts holding funds today run the v0.7 plugin design. And the flexibility that makes the account durable is also its risk surface, since a module installed with global validation can drive every native function, including the upgrade.

![Mindmap of Circle's UpgradableMSCA covering the two ERC-6900 generations in the repository, what the account contract adds over BaseMSCA, the ERC-7201 storage layout, the validation model and hook ordering, the self-call guard rails, the factory, and the shipped modules]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/2026-09-09-circle-upgradable-msca-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **MSCA** | Modular Smart Contract Account. An ERC-4337 account whose validation, execution and hook logic comes from installable module contracts rather than from fixed code. |
| **Module** | A separate contract providing validation, execution functions, or hooks to an account. Called a *plugin* in the v0.7 generation. |
| **`ModuleEntity`** | 24 bytes packing a module address with a `uint32` entity id, naming one specific validation function or hook inside a module. |
| **`HookConfig`** | 25 bytes packing a module address, an entity id, and flags saying whether the hook is a validation hook and whether it has pre and post halves. |
| **Global validation** | A validation function permitted for every native execution function and for any module function whose manifest allows it. Selected by byte 24 of the signature. |
| **Per-selector validation** | A validation function permitted only for the selectors registered against it at install time. The session-key mode. |
| **Validation-associated hook** | An execution hook attached to a validation function rather than a selector, so it runs around whatever that validation authorised. |
| **Direct-call validation** | The `ModuleEntity` packing a caller's address with `DIRECT_CALL_VALIDATION_ENTITY_ID`, used to permit a module to call back into the account. |
| **ERC-7201 namespace** | A storage region rooted at a hash-derived slot instead of slot 0, so a replacement implementation finds the same layout. |
| **`ExecutionManifest`** | A module's declaration of the execution functions it adds, the hooks it attaches to selectors, and the ERC-165 interface ids it brings. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| Only the EntryPoint may call `validateUserOp` and `executeUserOp`. | An explicit `msg.sender != address(ENTRY_POINT)` check reverting with `UnauthorizedCaller` in both. | The check is removed, allowing anyone to drive execution without validation. |
| `execute` can never target the account itself. | `_checkValidationForCalldata` reverts with `SelfCallRecursionDepthExceeded` when the decoded target is `address(this)`. | The check is dropped, letting a narrow validation reach `installValidation` through `execute`. |
| Self-calls inside `executeBatch` are one level deep and individually authorised. | Inner selectors may not be `execute` or `executeBatch`, and each is re-checked against the same validation function. | Nested batches become permitted, hiding a selector from the validation check. |
| A module cannot register a selector the account already owns. | `_installExecution` rejects native, ERC-4337 and `IModule` selectors via `SelectorRegistryLib`. | The rejection list falls out of sync with the account's own function set. |
| The post-hook set is fixed before any hook runs. | `HookLib._copyPostExecHooks` snapshots the list at the start of `_processPreExecHooks`. | Post-hooks are read from storage after the pre-hooks, letting a pre-hook remove its own post-half. |
| Hook time ranges narrow, never widen. | `ValidationDataLib._intersectValidationData` takes the later `validAfter` and earlier `validUntil`, and fails an empty window. | The intersection is replaced by a union, or the empty-window case stops mapping to `address(1)`. |
| A validation may only do what its flags allow. | `isUserOpValidation` is checked in `_processUserOpHooksAndValidation` and `isSignatureValidation` in `isValidSignature`. | The flag checks are removed, so a signing-only validation can drive user operations. |
| The account's state survives an implementation change. | All state hangs off the ERC-7201 slot derived from `circle.msca.v2.storage`. | A replacement implementation uses a different namespace id or adds plain state variables. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| `userOp.signature` must begin with a 24-byte `ModuleEntity` and a 1-byte global flag; anything shorter than 25 bytes reverts. | Build the signature as entity, flag, hook segments, then the module's own signature. Do not pass a bare 65-byte ECDSA signature. |
| `isValidSignature` reads the first 24 bytes of the signature as the validation entity, not as signature data. | Prepend the `ModuleEntity` to every ERC-1271 signature. A verifier that forwards a raw signature will always fail. |
| Installing a validation-associated execution hook makes any calldata not starting with `executeUserOp` revert with `RequireUserOperationContext`. | Once such a hook is installed, wrap all user-operation calldata with the `executeUserOp` selector. |
| `uninstallValidation` only removes hooks when `hookUninstallData` is supplied, and requires its length to match the hook count exactly. | Pass one entry per validation hook plus one per execution hook, or expect the hooks to remain in storage and reappear if the same `ModuleEntity` is reinstalled. |
| `installValidation` can be called again on an existing entity to add hooks and selectors, which are never removed by that path. | Treat repeated installs as additive updates, and use `uninstallValidation` when the intent is to reduce a validation's reach. |
| The counterfactual address commits to the implementation and to the full initial configuration. | Recompute the address whenever the factory, the first validation function, the selector list, or the hooks change. Do not cache it across factory redeployments. |
| `onUninstall` failures are swallowed and reported as a `false` flag in the event rather than reverting. | Read the `onUninstallSuccess` field of `ExecutionUninstalled` and `ValidationUninstalled` instead of assuming a successful transaction means clean module state. |
| The factory allowlist applies at creation only. | Do not treat an account's installed module set as allowlisted; audit modules added after deployment separately. |
| The v0.8 tree is not deployed to any mainnet. | Read `src/msca/6900/v0.7` when investigating an account that exists on chain today. |

## Frequently Asked Questions

**Q: Why is `_authorizeUpgrade` empty, and what stops an arbitrary address from upgrading the account?**

The `wrapNativeExecutionFunction` modifier on `upgradeToAndCall` does. It calls `_checkCallPermission`, which lets through the EntryPoint and the account itself, and requires everyone else to satisfy a direct-call validation registered for their address. A call from the EntryPoint has already been through `validateUserOp`, where the signature named a validation function that had to be permitted for the `upgradeToAndCall` selector, either globally or per-selector. Leaving `_authorizeUpgrade` empty avoids a second, redundant, hard-coded check and puts the policy where the rest of the account's policy lives.

**Q: What is the difference between a validation hook and a validation-associated execution hook?**

A validation hook runs during the validation phase, before the validation function, and returns a packed `validationData` that is intersected with everything else. It can narrow a time window or reject an operation outright, and it sees the user operation but not the result of anything.

A validation-associated execution hook runs during the execution phase, wrapped around the call the validation authorised, and its pre-half can return data that its post-half receives. It can observe state before and after, which is what a spending limit needs.

Both attach to a `ModuleEntity` rather than to a selector, so both follow the key being used rather than the function being called.

**Q: An account is configured with a session key permitted only to call `transfer`. Why can it not escalate through `executeBatch`?**

Three checks compose. First, `_checkValidationForCalldata` verifies the outer selector, `executeBatch`, is permitted for that validation. Second, for each inner call whose target is the account itself, the inner selector is re-checked against the *same* validation function, so an inner `installValidation` fails unless the session key was explicitly granted it. Third, an inner `execute` or `executeBatch` is rejected outright, so the key cannot add a level of nesting to hide the selector from the second check. A key that may only call `transfer` therefore ends up with `transfer` as the only self-call selector it can reach.

**Q: Why does the multisig module let the last signer set the gas fields, and how does the account know which digest was signed?**

Collecting several signatures takes time, and the gas fields of a user operation are part of what a signature covers, so fees moving between the first and last signature would invalidate the earlier ones. The module resolves it by having the first *k−1* signers sign a minimal operation with only `sender`, `nonce`, `initCode` and `callData` populated, leaving the rest at default values, and having the final signer sign the complete object. The two digests are distinguished by the signature type byte: a signature over the actual, fully-populated operation has 32 added to its `v` value, and the module subtracts 32 back before recovering.

**Q: What stops a module from corrupting the account's storage?**

Modules are separate contracts called with `CALL`, not `DELEGATECALL`, so they execute in their own storage context and physically cannot write to the account. That is why module state is keyed by account address inside the module, as in `signers[entityId][account]`. The one place this does not hold is v0.7, where `installPlugin` delegatecalls into `PluginManager` — but `PluginManager` is a fixed contract deployed by Circle, not a user-supplied module, and its address is an immutable in the account implementation.

**Q: Combining the storage design and the factory, why does upgrading an account's implementation not change its address, while redeploying the factory changes every address?**

The two are computed from different things. An account's address is a CREATE2 address derived from the factory address, the mixed salt, and the hash of the `ERC1967Proxy` creation code with its constructor arguments, which include the implementation address the factory held *at deployment time*. Once deployed, the proxy's address is fixed and an upgrade only rewrites the implementation pointer in the ERC-1967 slot, leaving the ERC-7201 namespace and therefore the account's whole state untouched.

Redeploying the factory creates a *new* `ACCOUNT_IMPLEMENTATION` in its constructor, which changes the constructor arguments hashed into the creation code, and the factory address itself is the CREATE2 deployer. Both inputs move, so every counterfactual address moves with them.

**Q: If an account's validation is uninstalled but the transaction succeeds, can its hooks still be active?**

Yes, and this is the case worth checking. `_uninstallValidation` zeroes the validation flags and removes the registered selectors unconditionally, but it only touches the hooks when `hookUninstallData` is non-empty, and then it requires exactly one entry per validation hook plus one per execution hook. Calling it with an empty array leaves both hook lists in `validationStorage` for that `ModuleEntity`. The validation itself is unusable, since its flags are cleared, but reinstalling the same module and entity id later would find the old hooks still attached.

## References

### Analyzed source

- [circlefin/buidl-wallet-contracts](https://github.com/circlefin/buidl-wallet-contracts) — analyzed at commit [`3c47aa94a8422bbd69a5e71ef21dbaa5ff6e1939`](https://github.com/circlefin/buidl-wallet-contracts/tree/3c47aa94a8422bbd69a5e71ef21dbaa5ff6e1939), 2026-09-09. Files read: `src/msca/6900/v0.8/account/UpgradableMSCA.sol`, `src/msca/6900/v0.8/account/BaseMSCA.sol`, `src/msca/6900/v0.8/account/WalletStorageInitializable.sol`, `src/msca/6900/v0.8/libs/WalletStorageV2Lib.sol`, `src/msca/6900/v0.8/libs/HookLib.sol`, `src/msca/6900/v0.8/libs/SelectorRegistryLib.sol`, `src/msca/6900/v0.8/factories/UpgradableMSCAFactory.sol`, `src/msca/6900/v0.8/modules/`, `src/msca/6900/shared/libs/ValidationDataLib.sol`, `src/msca/6900/v0.7/account/`, `test/msca/6900/v0.8/MSCACallFlow.t.sol`.

### Specifications

- [ERC-6900: Modular Smart Contract Accounts and Plugins](https://eips.ethereum.org/EIPS/eip-6900)
- [ERC-4337: Account Abstraction Using Alt Mempool](https://eips.ethereum.org/EIPS/eip-4337)
- [ERC-7201: Namespaced Storage Layout](https://eips.ethereum.org/EIPS/eip-7201)
- [ERC-7562: Account Abstraction Validation Scope Rules](https://eips.ethereum.org/EIPS/eip-7562)
- [ERC-1967: Proxy Storage Slots](https://eips.ethereum.org/EIPS/eip-1967)
- [ERC-1822: Universal Upgradeable Proxy Standard (UUPS)](https://eips.ethereum.org/EIPS/eip-1822)
- [ERC-1271: Standard Signature Validation Method for Contracts](https://eips.ethereum.org/EIPS/eip-1271)
- [ERC-165: Standard Interface Detection](https://eips.ethereum.org/EIPS/eip-165)

### Implementations and documentation

- [erc6900/reference-implementation](https://github.com/erc6900/reference-implementation) — the source of `ModuleEntity`, `HookConfig`, `ValidationConfig` and `SparseCalldataSegmentLib`
- [eth-infinitism/account-abstraction](https://github.com/eth-infinitism/account-abstraction) — the EntryPoint and `PackedUserOperation`
- [Safe smart account signatures](https://docs.safe.global/advanced/smart-account-signatures#encoding) — the encoding Circle's multisig signature scheme extends
- [OpenZeppelin Contracts 5.x — Upgradeable proxies](https://docs.openzeppelin.com/contracts/5.x/upgradeable)
- [Circle Programmable Wallets documentation](https://developers.circle.com/w3s/programmable-wallets)

### Related articles

- [Inside Circle's SponsorPaymaster — How a Verifying Paymaster Is Built]({{site.url_complet}}/2026/09/09/circle-sponsor-paymaster-erc4337/)
- [ERC-4337: Account Abstraction Using Alt Mempool]({{site.url_complet}}/2025/05/02/erc-4337-overview/)
- [How Alchemy Implements Smart Wallets and Account Abstraction]({{site.url_complet}}/2026/07/30/alchemy-smart-wallet-account-abstraction/)
- [SenderCreator in ERC-4337 — Deploying Accounts and Reading Counterfactual Addresses]({{site.url_complet}}/2026/07/23/sendercreator-entrypoint-erc4337-counterfactual-address/)
- [Nonce Management and CREATE2 in ERC-4337 Smart Wallets]({{site.url_complet}}/2026/02/17/nonce-management-create2-smart-wallets-erc4337/)
- [ERC-1271 and ERC-7913 Signature Verification — OpenZeppelin, Solady, Coinbase Smart Wallet, and Solarity Solidity Library]({{site.url_complet}}/2026/02/13/erc1271-erc7913-signature-verification-comparison/)
