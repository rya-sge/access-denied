---
layout: post
title: "SenderCreator in ERC-4337 — Deploying Accounts and Reading Counterfactual Addresses"
date:   2026-07-23
last_modified_at: 2026-07-28
lang: en
locale: en-GB
categories: blockchain ethereum solidity security
tags: blockchain ethereum solidity erc-4337 account-abstraction entrypoint sender-creator eip-7702 create2
description: How the ERC-4337 SenderCreator contract deploys smart accounts on behalf of the EntryPoint, how third parties read counterfactual addresses through getSenderAddress, and what changed across EntryPoint v0.6 to v0.9.
image: /assets/article/blockchain/ethereum/erc-4337/sendercreator-mindmap.png
isMath: false
---

In ERC-4337, a smart account is usually deployed the first time it sends a `UserOperation`. The contract that performs that deployment is not the `EntryPoint` itself but a small, deliberately powerless helper: `SenderCreator`. This article explains what `SenderCreator` does, why the account-abstraction design routes deployment through a separate "neutral" address, how external tooling uses it indirectly through `getSenderAddress` to compute a counterfactual account address, and how the contract evolved between EntryPoint v0.6 and v0.9.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What SenderCreator is

`SenderCreator` is a helper contract deployed by the `EntryPoint` in its constructor. Its job description sits in a single sentence in the source header:

```solidity
/**
 * Helper contract for EntryPoint, to call userOp.initCode from a "neutral" address,
 * which is explicitly not the entryPoint itself.
 */
contract SenderCreator is ISenderCreator {
```

An ERC-4337 `UserOperation` carries an `initCode` field. When the account does not yet exist on-chain, `initCode` tells the EntryPoint how to create it. The layout is fixed:

- **First 20 bytes**: the address of an account factory contract.
- **Remaining bytes**: the calldata to send to that factory, which typically encodes a `createAccount(owner, salt)` call.

The EntryPoint never calls the factory directly. It hands the `initCode` to `SenderCreator`, which splits off the factory address, calls the factory with the remaining calldata, and returns whatever address the factory reports. The factory is expected to deploy the account with `CREATE2` so the resulting address is deterministic.

The EntryPoint holds one immutable reference to its helper, created at construction time:

```solidity
SenderCreator private immutable _senderCreator = new SenderCreator();
```

Because the EntryPoint is the deployer, the `SenderCreator` records the EntryPoint address in its own constructor and later uses it for access control (from v0.8 onward, discussed below):

```solidity
address public immutable entryPoint;

constructor(){
    entryPoint = msg.sender;
}
```

## Anatomy of the contract

The contract exposes two functions, both declared in `ISenderCreator`.

### createSender

`createSender` is the classic deployment path. It validates the caller, extracts the factory address, and performs a low-level `call` to the factory, copying back exactly 32 bytes as the returned sender address:

```solidity
function createSender(
    bytes calldata initCode
) external returns (address sender) {
    require(msg.sender == entryPoint, NotFromEntryPoint(msg.sender, address(this), entryPoint));
    address factory = address(bytes20(initCode[0 : 20]));

    bytes memory initCallData = initCode[20 :];
    bool success;
    assembly ("memory-safe") {
        success := call(
            gas(),
            factory,
            0,
            add(initCallData, 0x20),
            mload(initCallData),
            0,
            32
        )
        if success {
            sender := mload(0)
        }
    }
}
```

Two properties matter for callers. First, on a failed factory call the function does not revert; it simply leaves `sender` as the zero address, and the EntryPoint interprets that zero as a deployment failure. Second, the factory is called with `value = 0`, so a factory that needs funding must obtain it elsewhere (for example from the account's own prefund logic).

### initEip7702Sender

The second function, added in v0.8, supports EIP-7702 accounts. Under EIP-7702 the account already has code, because the EOA delegated to an implementation through an authorization tuple, so there is nothing to deploy. What may still be needed is a one-time initialization call into that account. `initEip7702Sender` performs exactly that call and, unlike `createSender`, bubbles up a descriptive revert on failure:

```solidity
function initEip7702Sender(
    address sender,
    bytes memory initCallData
) external {
    require(msg.sender == entryPoint, NotFromEntryPoint(msg.sender, address(this), entryPoint));
    bool success;
    assembly ("memory-safe") {
        success := call(gas(), sender, 0, add(initCallData, 0x20), mload(initCallData), 0, 0);
    }
    if (!success) {
        bytes memory result = Exec.getReturnData(REVERT_REASON_MAX_LEN);
        revert IEntryPoint.FailedOpWithRevert(0, "AA13 EIP7702 sender init failed", result);
    }
}
```

The interface documents that this call is idempotent by design: it "can be called multiple times as long as an appropriate initCode is supplied," and the EntryPoint has already verified that `sender` is a genuine EIP-7702 delegate before invoking it.

## The neutral-address rationale

`SenderCreator` is a separate contract rather than a function on the EntryPoint, and the reason is trust isolation. A factory is arbitrary, user-supplied code, and whatever contract calls it becomes its `msg.sender`. If the EntryPoint called the factory directly, a malicious or buggy factory would run with the EntryPoint as its caller and could try to re-enter privileged EntryPoint functions (deposit accounting, withdrawals, staking) that trust `msg.sender`.

Routing the call through `SenderCreator` closes that door. The factory sees `SenderCreator` as its caller, and `SenderCreator` holds no deposits, no stake, and no authority anywhere in the system. A factory that turns hostile can, at worst, abuse a powerless relay. The following diagram shows where the boundary sits.

![SenderCreator as an isolation boundary between the EntryPoint and untrusted factories]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/sendercreator-architecture-concept.png)

## How the EntryPoint uses it

During `handleOps`, the EntryPoint calls the internal `_createSenderIfNeeded` for every operation that carries a non-empty `initCode`. That function decides between three outcomes: skip an already-deployed account, initialize an EIP-7702 account, or deploy a fresh account through the factory.

The deployment branch calls `createSender` with an explicit gas ceiling taken from the operation's `verificationGasLimit`, then applies three post-conditions:

- **AA13** — the returned address must be non-zero, otherwise the factory call failed or ran out of gas.
- **AA14** — the returned address must equal the `sender` declared in the `UserOperation`, so the account cannot be deployed to an unexpected address.
- **AA15** — the returned address must now contain code, proving the factory actually created the account.

```solidity
address sender1 = senderCreator().createSender{
        gas: opInfo.mUserOp.verificationGasLimit
    }(initCode);
if (sender1 == address(0))
    revert FailedOp(opIndex, "AA13 initCode failed or OOG");
if (sender1 != sender)
    revert FailedOp(opIndex, "AA14 initCode must return sender");
if (sender1.code.length == 0)
    revert FailedOp(opIndex, "AA15 initCode must create sender");
```

If the account already has code, the EntryPoint ignores the supplied `initCode` and emits `IgnoredInitCode` instead of reverting, which keeps a bundle from failing just because two operations both include the same deployment. The full path is shown below.

![Sequence of handleOps deploying a sender account through SenderCreator]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/sendercreator-deploy-workflow.png)

## Reading an address without deploying

Bundlers, SDKs, and dApps frequently need the account address *before* it exists: to display it to a user, to receive funds at it, or to set it as the `sender` of the very operation that will deploy it. That address is called the counterfactual address, and the canonical on-chain way to obtain it is `EntryPoint.getSenderAddress`:

```solidity
function getSenderAddress(bytes calldata initCode) external virtual {
    address sender = senderCreator().createSender(initCode);
    revert SenderAddressResult(sender);
}
```

The mechanism is a controlled dry run. `getSenderAddress` actually runs the factory through `createSender`, captures the address the deployment would produce, and then reverts with `SenderAddressResult(sender)`. The revert serves two purposes at once: it rolls back the deployment that just happened inside the call frame, and it carries the address back to the caller inside the error payload. A caller invokes the function with `eth_call`, so no transaction is mined and no state is committed, then decodes the address from the revert data:

```solidity
try entryPoint.getSenderAddress(initCode) {
    // unreachable: the function always reverts
} catch (bytes memory reason) {
    // strip the SenderAddressResult selector, decode the address
}
```

Using a distinct error type lets the caller separate the success case from a genuine factory failure. If the factory reverts for a real reason, that error surfaces instead of `SenderAddressResult`, signalling a broken `initCode`.

![getSenderAddress dry-run sequence: run the factory, capture the address, revert]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/sendercreator-getsenderaddress-workflow.png)

There is an access-control subtlety here that is easy to miss. From v0.8 onward, `createSender` reverts unless the caller is the EntryPoint. A third party therefore cannot call `SenderCreator.createSender` directly to probe an address; the only sanctioned route is `EntryPoint.getSenderAddress`, which reaches `createSender` from the EntryPoint context so the check passes. In v0.6 and v0.7, by contrast, `SenderCreator` had no such guard, and anyone could call `createSender` directly. Off-chain SDKs may also skip the contract entirely and compute the CREATE2 address locally, but `getSenderAddress` remains the authoritative answer because it runs the real factory.

## What changed across EntryPoint versions

`SenderCreator` has existed as a distinct helper since the early EntryPoint releases, but its responsibilities and its access control grew over time. The table summarizes the trajectory; the v0.8 and v0.9 rows are verified against the sources bundled in this repository, and the v0.6 and v0.7 rows against the tagged releases of the reference implementation.

| Version | Access control on `createSender` | EIP-7702 support | Notable |
|---|---|---|---|
| v0.6 | None — any caller | No | Minimal relay; `createSender` only; failure returns `address(0)`. |
| v0.7 | None — any caller | No | Same shape as v0.6; no `entryPoint` immutable, no constructor. |
| v0.8 | `require(msg.sender == entryPoint, "AA97 should call from EntryPoint")` | Yes | Adds `entryPoint` immutable set in constructor, `initEip7702Sender`, and the `ISenderCreator` interface. |
| v0.9 | `require(msg.sender == entryPoint, NotFromEntryPoint(...))` | Yes | Replaces the `AA97` string revert with the typed error `NotFromEntryPoint(msgSender, entity, entryPoint)`. |

Three transitions are worth calling out.

- **v0.7 to v0.8, access control appears.** Earlier versions left `createSender` open because a permissionless relay with no privileges is harmless to call. Version 0.8 introduced `initEip7702Sender`, which calls straight into a user account, so restricting the helper to the EntryPoint became necessary. The team recorded the deploying EntryPoint as an immutable and gated both functions with `require(msg.sender == entryPoint, "AA97 should call from EntryPoint")`.
- **v0.7 to v0.8, EIP-7702 enters the picture.** Alongside the new function, `ISenderCreator` gained `initEip7702Sender`, and the EntryPoint's `_createSenderIfNeeded` learned to branch on `_isEip7702InitCode` and dispatch to it. This is also when `getSenderAddress` picked up the notice that it "cannot be used for EIP-7702 derived contracts," since those accounts have no factory to run.
- **v0.8 to v0.9, string reverts become typed errors.** The behaviour is identical, but the guard moved from the string `"AA97 should call from EntryPoint"` to a custom error, `NotFromEntryPoint(address msgSender, address entity, address entryPoint)`, declared on the contract. The typed error carries the offending caller, the helper's own address, and the expected EntryPoint, which makes off-chain debugging and revert decoding cleaner. Aside from that substitution, the v0.8 and v0.9 `SenderCreator` files are the same.

## SenderCreator and EIP-7702

EIP-7702 changes the account lifecycle enough that half of `SenderCreator` no longer applies. An EIP-7702 account is an EOA whose code points at an implementation through a signed authorization tuple. There is no factory and no `CREATE2`, and the account address is simply the EOA address, fixed by its key.

Two consequences follow. First, deployment is replaced by initialization: the EntryPoint routes EIP-7702 `initCode` to `initEip7702Sender`, which calls into the already-code-bearing EOA rather than creating anything. Second, `getSenderAddress` is meaningless for these accounts, which is exactly what its `@notice` warns, because there is no counterfactual address to compute when the sender is the EOA itself. For an EIP-7702 smart wallet, where the EOA delegates directly to the account implementation and then initializes itself, `SenderCreator` is only relevant through the EIP-7702 initialization branch, never through the factory deployment branch.

## Conclusion

`SenderCreator` is a small contract that carries a specific security responsibility: it is the neutral hand that touches untrusted factory code so the EntryPoint never has to. Its `createSender` function deploys accounts during `handleOps` and, through `getSenderAddress`, lets external tooling read a counterfactual address by running the factory and reverting. Across versions the contract gained an access-control guard and an EIP-7702 initialization path in v0.8, and a typed `NotFromEntryPoint` error in v0.9, while its core role stayed constant. The mindmap below summarizes the pieces.

![Mindmap summary of the SenderCreator contract, its functions, callers, version history, and EIP-7702 caveat]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/sendercreator-mindmap.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **SenderCreator** | Helper contract deployed by the EntryPoint that calls a UserOperation's `initCode` from a neutral, privilege-free address to create or initialize the sender account. |
| **EntryPoint** | The central ERC-4337 singleton that validates and executes UserOperations and holds account and paymaster deposits. |
| **initCode** | A UserOperation field of 20 bytes of factory address followed by factory calldata, used to deploy the account when it does not yet exist. |
| **Account factory** | User-supplied contract that deploys a smart account, typically with `CREATE2`, when called by `SenderCreator`. |
| **Counterfactual address** | The deterministic address a smart account will have once deployed, known in advance and usable before any code exists there. |
| **getSenderAddress** | EntryPoint function that computes the counterfactual address by running the factory and reverting with `SenderAddressResult`. |
| **SenderAddressResult** | The custom error `getSenderAddress` reverts with to carry the computed sender address back to an off-chain caller. |
| **createSender** | `SenderCreator` function that splits `initCode`, calls the factory, and returns the created account address or the zero address on failure. |
| **initEip7702Sender** | `SenderCreator` function, added in v0.8, that calls initialization data into an already-delegated EIP-7702 account instead of deploying one. |
| **NotFromEntryPoint** | The typed error introduced in v0.9 that replaces the v0.8 `AA97` string revert when a caller other than the EntryPoint invokes `SenderCreator`. |

## Annex — Security Implementation Checklist

The properties below are the ones that make a `SenderCreator`-style deployment relay safe rather than merely functional. They are useful when reviewing the EntryPoint or any contract that deploys untrusted factory code on another contract's behalf.

### Isolation and access control

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Factory `initCode` is called from a dedicated helper, not from the privileged coordinator (EntryPoint), so the factory's `msg.sender` carries no authority. | A malicious factory re-enters privileged functions that trust `msg.sender` and drains deposits or corrupts accounting. |
| ☐ | The helper records the deploying coordinator as an immutable and rejects any other caller (`msg.sender == entryPoint`). | An arbitrary caller drives `initEip7702Sender` into user accounts, or probes deployments outside the sanctioned path. |
| ☐ | The helper holds no deposits, stake, or privileges anywhere in the protocol. | A compromised helper becomes a lever for stealing funds or forging authorization. |

### Deployment correctness

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The returned sender is checked non-zero (AA13) before it is trusted. | A silently failed factory call is treated as a successful deployment. |
| ☐ | The returned sender must equal the `UserOperation.sender` (AA14). | The account is deployed to an attacker-chosen address that differs from the one validated and funded. |
| ☐ | The deployed sender must actually contain code afterward (AA15). | An empty or self-destructing factory passes validation without creating a usable account. |
| ☐ | Deployment runs under an explicit gas ceiling derived from `verificationGasLimit`. | An unbounded factory call enables griefing or gas exhaustion of the bundle. |

### EIP-7702 handling

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | EIP-7702 accounts are initialized, not deployed; the sender is confirmed to be a genuine delegate before `initEip7702Sender` runs. | A non-delegated address is called with attacker calldata, or a factory deployment is attempted on code that already exists. |
| ☐ | `getSenderAddress` is documented and treated as inapplicable to EIP-7702 senders. | Tooling derives a bogus counterfactual address for an account whose address is just the EOA. |

## Frequently Asked Questions

**Q: Why does the EntryPoint delegate account creation to a separate contract instead of calling the factory itself?**

For trust isolation. The factory is arbitrary user code, and it runs with its caller as `msg.sender`. If the EntryPoint were the caller, a hostile factory could try to re-enter privileged EntryPoint functions that trust `msg.sender`, such as deposit or withdrawal accounting. `SenderCreator` is a neutral relay with no funds and no privileges, so a hostile factory can only abuse something powerless.

**Q: What exactly does `createSender` return when the factory call fails?**

The zero address. `createSender` does not revert on a failed factory call; the inline assembly only writes `sender` when the call succeeds, leaving it as `address(0)` otherwise. The EntryPoint then converts that zero into an `AA13 initCode failed or OOG` failure. This is different from `initEip7702Sender`, which does revert with a descriptive `FailedOpWithRevert` on failure.

**Q: How does `getSenderAddress` return a value if it always reverts?**

It uses the revert as a data channel. The function runs the factory through `createSender`, obtains the address the deployment would produce, then reverts with `SenderAddressResult(sender)`. The revert rolls back the deployment so nothing persists, and the address travels back inside the error payload. A caller invokes it with `eth_call` and decodes the address from the revert reason. It cannot be a `view` function because it actually performs a state-changing factory call.

**Q: Can a third party call `SenderCreator.createSender` directly to learn an address?**

Not from v0.8 onward. Since v0.8, `createSender` reverts unless `msg.sender` is the EntryPoint, so a direct call from an external account fails. The supported route is `EntryPoint.getSenderAddress`, which calls `createSender` from the EntryPoint context so the guard passes. In v0.6 and v0.7 the guard did not exist, and direct calls were possible.

**Q: Combining the version history with the EIP-7702 behaviour, why did access control become necessary precisely in v0.8?**

Because v0.8 introduced `initEip7702Sender`, which calls directly into a user's account with supplied calldata. A permissionless relay is harmless when it only forwards to a factory that deploys a fresh contract, but a function that can call into an existing account must not be open to arbitrary callers. Adding the `entryPoint` immutable and the `msg.sender == entryPoint` guard in v0.8 restricted both functions to the EntryPoint at the same time the EIP-7702 path was added. Version 0.9 kept the same guard and only upgraded its string revert to the typed `NotFromEntryPoint` error.

**Q: Why does the notice say `getSenderAddress` cannot be used for EIP-7702 accounts?**

Because those accounts have no factory and no `CREATE2` deployment to simulate. An EIP-7702 account is an EOA that delegated to an implementation, and its address is simply the EOA address, already fixed by the key. There is no counterfactual address to compute, so the function's dry-run-a-factory mechanism has nothing to run.

## References

- [ERC-4337: Account Abstraction Using Alt Mempool](https://eips.ethereum.org/EIPS/eip-4337)
- [EIP-7702: Set EOA account code](https://eips.ethereum.org/EIPS/eip-7702)
- [eth-infinitism/account-abstraction — SenderCreator.sol](https://github.com/eth-infinitism/account-abstraction/blob/develop/contracts/core/SenderCreator.sol)
- [eth-infinitism/account-abstraction — EntryPoint.sol](https://github.com/eth-infinitism/account-abstraction/blob/develop/contracts/core/EntryPoint.sol)
- [account-abstraction v0.7.0 SenderCreator.sol](https://github.com/eth-infinitism/account-abstraction/blob/v0.7.0/contracts/core/SenderCreator.sol)
- [account-abstraction v0.6.0 SenderCreator.sol](https://github.com/eth-infinitism/account-abstraction/blob/v0.6.0/contracts/core/SenderCreator.sol)
- [Claude Code](https://claude.com/product/claude-code)
