---
layout: post
title: Nonce Management and CREATE2 in ERC-4337 Smart Wallets
date:   2026-02-17
lang: en
locale: en-GB
categories: blockchain ethereum solidity security
tags: blockchain ethereum solidity erc-4337 eip-7702 smart-wallet nonce create2 account-abstraction
description: Understanding the dual nonce system in ERC-4337 smart wallets, the differences between CREATE and CREATE2 for contract deployment, and the pitfalls encountered with EIP-7702 delegation.
image: /assets/article/blockchain/ethereum/erc-4337/smart-wallet-nonce-mindmap.png
isMath: false
---

When building a smart wallet that deploys contracts through ERC-4337 UserOperations, nonce management becomes a non-trivial problem. The EVM has one nonce, the EntryPoint has another, and EIP-7702 delegation adds a third layer of complexity. This article documents the lessons learned from implementing and testing contract deployment in an EIP-7702 smart account.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The Dual Nonce System

A fundamental aspect of ERC-4337 smart wallets is that they operate with two independent nonce systems. Confusing these two systems is a common source of bugs, particularly when predicting addresses for CREATE deployments.

### EntryPoint Nonce (ERC-4337 Protocol Level)

The EntryPoint contract maintains its own nonce mapping for each account. This nonce is included in the `PackedUserOperation` struct and is verified during `handleOps`. Its purpose is replay protection: each UserOperation must carry a fresh nonce, or the EntryPoint rejects it.

```solidity
// The EntryPoint tracks nonces per account, per key
// key = 0 is the default key; the sequence auto-increments
uint256 nonce = entryPoint.getNonce(account, 0);
```

The EntryPoint nonce is a 256-bit value split into two parts: a 192-bit key (allowing parallel nonce channels) and a 64-bit sequence number. The key is chosen by the caller, and the sequence auto-increments within each key.

This nonce has no effect on the EVM state. It exists entirely within the EntryPoint's storage and has no relation to the `CREATE` opcode.

### EVM Account Nonce (Protocol Level)

Every Ethereum account has an EVM-level nonce managed by the protocol itself. For EOAs, this nonce increments with each transaction sent. For contracts, it increments with each `CREATE` opcode execution.

```solidity
// The EVM nonce is what determines CREATE addresses
address deployed = computeCreateAddress(deployer, evmNonce);
```

This is the nonce that matters for `CREATE` address derivation. The formula is:

```
address = keccak256(rlp([deployer, nonce]))[12:]
```

### Where Confusion Arises

When a smart wallet deploys a contract via a UserOperation, both nonce systems are involved but at different layers:

1. The **EntryPoint nonce** is consumed when `handleOps` processes the UserOperation
2. The **EVM nonce** is consumed when the `CREATE` opcode executes inside the wallet's `deploy()` function

These two nonces are completely independent. After processing a UserOperation that deploys a contract, the EntryPoint nonce might be `1` while the EVM nonce might be `1` as well, but this is coincidental. They track different things.

## Contract Deployment from a Smart Wallet

A smart wallet built around `execute()` and `executeBatch()` uses the `CALL` opcode internally. 

The `CALL` opcode cannot deploy contracts. Deploying contracts requires the `CREATE` or `CREATE2` opcodes, which means dedicated deployment functions are needed in the wallet contract.

### The deploy() Function

The `deploy()` function wraps the `CREATE` opcode and is restricted to the EntryPoint or the account itself:

```solidity
function deploy(uint256 value, bytes calldata creationCode)
    external
    payable
    virtual
    onlyEntryPointOrSelf
    returns (address deployed)
{
    assembly ("memory-safe") {
        let m := mload(0x40)
        calldatacopy(m, creationCode.offset, creationCode.length)
        deployed := create(value, m, creationCode.length)
        if iszero(deployed) {
            returndatacopy(m, 0x00, returndatasize())
            revert(m, returndatasize())
        }
    }
}
```

The UserOperation encodes a call to this function:

```solidity
bytes memory creationCode = abi.encodePacked(
    type(MyContract).creationCode,
    abi.encode(constructorArg1, constructorArg2)
);

bytes memory callData = abi.encodeCall(
    SmartAccount7702.deploy,
    (0, creationCode)
);
```

### The deployDeterministic() Function

For deterministic addresses, `deployDeterministic()` wraps the `CREATE2` opcode:

```solidity
function deployDeterministic(
    uint256 value,
    bytes calldata creationCode,
    bytes32 salt
)
    external
    payable
    virtual
    onlyEntryPointOrSelf
    returns (address deployed)
{
    assembly ("memory-safe") {
        let m := mload(0x40)
        calldatacopy(m, creationCode.offset, creationCode.length)
        deployed := create2(value, m, creationCode.length, salt)
        if iszero(deployed) {
            returndatacopy(m, 0x00, returndatasize())
            revert(m, returndatasize())
        }
    }
}
```

## CREATE vs CREATE2: Address Derivation

The critical difference between `CREATE` and `CREATE2` lies in how the deployed address is computed.

### CREATE Address Formula

```
address = keccak256(rlp([deployer, nonce]))[12:]
```

The address depends on the deployer's EVM nonce. This makes the address **non-deterministic** from the perspective of the caller: you cannot predict the address without knowing the exact nonce at the time `CREATE` executes.

### CREATE2 Address Formula

```
address = keccak256(0xff ++ deployer ++ salt ++ keccak256(creationCode))[12:]
```

The address depends only on the deployer address, a chosen salt, and the creation bytecode. There is no nonce involved. This makes the address **fully deterministic**: you can compute it off-chain before the transaction is ever submitted.

### Why This Matters for Smart Wallets

Under EIP-7702, the deployer is `address(this)`, which resolves to the EOA's address. This means:

- For `CREATE`: the deployed address depends on the EOA's EVM nonce. Since the EVM nonce increments with each `CREATE`, the first deployment uses nonce 0, the second uses nonce 1, and so on. Predicting this nonce correctly is error-prone (see the next section).

- For `CREATE2`: the deployed address depends on the EOA's address, the salt, and the bytecode. All three are known before submission, so the address can be pre-computed reliably.

## The EVM Nonce Pitfall with vm.etch

When testing EIP-7702 smart wallets in Foundry, delegation is simulated using `vm.etch`:

```solidity
SmartAccount7702 impl = new SmartAccount7702();
vm.etch(alice, address(impl).code);
```

This copies the contract bytecode onto Alice's EOA address, but it does **not** modify Alice's EVM nonce. For a fresh address in a test, the nonce starts at 0.

This leads to a subtle bug when predicting CREATE addresses. A first attempt might assume the nonce is 1 (as is conventional for deployed contracts under EIP-161):

```solidity
// INCORRECT: assumes nonce starts at 1
address expected = computeCreateAddress(alice, 1);
```

But since `vm.etch` does not set the nonce to 1 (unlike a real contract deployment which initializes the nonce), the correct nonce for the first CREATE is 0.

The robust approach is to query the nonce at runtime, after the deployment has occurred:

```solidity
// CORRECT: query the actual nonce after CREATE
uint64 aliceNonce = vm.getNonce(alice);
address expected = computeCreateAddress(alice, aliceNonce - 1);
```

This pattern accounts for whatever nonce the account happens to have, regardless of how the test environment initialized it.

### On a Real Chain with EIP-7702

On a live network, the situation is different. When an EOA signs an EIP-7702 authorization tuple, its nonce is incremented (the auth tuple consumes a nonce). If Alice's EOA nonce was 5 before delegation, the first `CREATE` from her smart wallet code would use nonce 6 (or higher, depending on how many transactions were sent during initialization).

This makes CREATE address prediction fragile in production: the nonce depends on the EOA's entire transaction history. CREATE2 avoids this entirely.

## Practical Comparison

| Property | CREATE | CREATE2 |
|---|---|---|
| Address depends on | deployer + EVM nonce | deployer + salt + bytecode hash |
| Predictable before tx | Requires exact nonce knowledge | Always predictable |
| Cross-chain same address | Not guaranteed | Guaranteed (same deployer, salt, bytecode) |
| Re-deployable at same address | Not possible (nonce used) | Not possible (address occupied) |
| Smart wallet suitability | Fragile nonce tracking needed | Recommended for determinism |

## Recommendations

### Prefer CREATE2 for Deterministic Deployments

When the deployed address needs to be known ahead of time (e.g., for approvals, cross-chain coordination, or UI display), use `deployDeterministic()`. The address can be computed off-chain with:

```solidity
address predicted = computeCreate2Address(
    salt,
    keccak256(creationCode),
    walletAddress
);
```

### Use CREATE for Simple Deployments

When the address does not need to be known in advance (e.g., deploying a helper contract whose address will be stored on-chain), `deploy()` is simpler. Just do not attempt to predict the address from hardcoded nonce values.

### EntryPoint Nonce Channels for Parallel Operations

The EntryPoint's 192-bit key allows parallel nonce channels. Two UserOperations can be submitted concurrently if they use different keys:

```solidity
// These two UserOps can be submitted in parallel
uint256 nonce1 = entryPoint.getNonce(account, 0); // key 0
uint256 nonce2 = entryPoint.getNonce(account, 1); // key 1
```

This has no effect on CREATE address prediction (which depends on the EVM nonce), but it enables parallelism in the ERC-4337 flow.

## Summary

![smart-wallet-nonce-mindmap.png]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/smart-wallet-nonce-mindmap.png)



```
@startmindmap
* Nonce & CREATE2\nin Smart Wallets
** Dual Nonce System
*** EntryPoint Nonce
**** Replay protection
**** 192-bit key + 64-bit sequence
**** Parallel channels (key 0, 1, ...)
**** No effect on CREATE
*** EVM Account Nonce
**** Used by CREATE opcode
**** Incremented per CREATE
**** Determines deployed address
**** Independent from EntryPoint
** Contract Deployment
*** CREATE
**** address = keccak256(rlp([deployer, nonce]))
**** Non-deterministic
**** Nonce tracking required
**** Fragile with EIP-7702
*** CREATE2
**** address = keccak256(0xff ++ deployer ++ salt ++ bytecode_hash)
**** Fully deterministic
**** No nonce dependency
**** Cross-chain reproducible
** EIP-7702 Specifics
*** vm.etch does not set nonce
**** Fresh address = nonce 0
**** Use vm.getNonce at runtime
*** Real chain: EOA nonce history
**** Auth tuple increments nonce
**** Prior transactions count
*** address(this) = EOA
**** EOA is the deployer
**** EOA nonce is used
** Recommendations
*** Prefer CREATE2 for known addresses
*** Use CREATE for simple deployments
*** Query nonce at runtime, never hardcode
@endmindmap
```

## Reference

- [Claude Code](https://claude.com/product/claude-code)
- [EIP-7702: Set EOA account code](https://eips.ethereum.org/EIPS/eip-7702)
- [ERC-4337: Account Abstraction Using Alt Mempool](https://eips.ethereum.org/EIPS/eip-4337)
- [EIP-161: State trie clearing](https://eips.ethereum.org/EIPS/eip-161)
- [CREATE2 - EIP-1014](https://eips.ethereum.org/EIPS/eip-1014)
- [Foundry Book - vm.etch](https://book.getfoundry.sh/cheatcodes/etch)
- [Foundry Book - vm.getNonce](https://book.getfoundry.sh/cheatcodes/get-nonce)
