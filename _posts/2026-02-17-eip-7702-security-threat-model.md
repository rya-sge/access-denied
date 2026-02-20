---
layout: post
title: "EIP-7702 Smart Wallet Security: Threat Model and Attack Surface Analysis"
date: 2026-02-17
lang: en
locale: en-GB
categories: blockchain ethereum security solidity
tags: eip-7702 erc-4337 smart-wallet account-abstraction threat-model security audit
description: A practical security analysis of EIP-7702 smart wallets covering initialization front-running, access control, signature replay, dual nonce systems, and residual risks inherent to EOA code delegation.
image: /assets/article/blockchain/ethereum/eip-7702/EIP-7702-threat-model.png
isMath: false
---

EIP-7702 introduces a fundamentally new execution model for Ethereum: EOAs can delegate their code to smart contract implementations via type-4 transactions. This unlocks ERC-4337 Account Abstraction features — batching, gas sponsorship, programmable validation — without deploying a proxy. But this new paradigm introduces attack surfaces that did not exist in the traditional proxy-based smart wallet model. This article documents the threat model built from hands-on implementation of a minimal ERC-4337 smart account designed for EIP-7702 delegation, covering each attack vector, its mitigation, and the residual risks that cannot be solved at the smart contract level.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## How EIP-7702 Delegation Works

Before analyzing threats, it is necessary to understand the execution model. EIP-7702 adds a new transaction type (`0x04`) that carries an `authorization_list` — a set of tuples `[chain_id, address, nonce, y_parity, r, s]`. When processed, the protocol writes a delegation indicator (`0xef0100 || address`) to the signing EOA's code field. From that point on, any code-executing operation (CALL, STATICCALL, DELEGATECALL) targeting the EOA loads and executes the bytecode from the designated implementation contract.

The critical properties:

- **`address(this)` resolves to the EOA**, not the implementation. Storage reads and writes happen on the EOA's storage.
- **The EOA retains its private key**. It can sign transactions, re-delegate, or revoke delegation at any time.
- **No proxy is involved**. There is no `delegatecall` indirection, no ERC-1967 slot, no admin key.

A typical EIP-7702 smart account looks like this:

```solidity
contract SmartAccount7702 is ERC7739, SignerEIP7702, IAccount, Initializable {
    /// @custom:storage-location erc7201:smartaccount7702.entrypoint
    struct EntryPointStorage {
        address entryPoint;
    }

    // ERC-7201 namespaced slot — prevents collision under re-delegation
    bytes32 private constant ENTRY_POINT_STORAGE_LOCATION =
        0x38a124a88e3a590426742b6544792c2b2bc21792f86c1fa1375b57726d827a00;

    constructor() EIP712("TSmart Account 7702", "1") {
        _disableInitializers();
    }

    function initialize(address entryPoint_) external initializer {
        if (msg.sender != address(this)) revert Unauthorized();
        _getEntryPointStorage().entryPoint = entryPoint_;
    }

    function validateUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external onlyEntryPoint returns (uint256 validationData) {
        // Pay prefund when self-funding (no paymaster)
        if (missingAccountFunds > 0) {
            assembly ("memory-safe") {
                pop(call(gas(), caller(), missingAccountFunds, 0x00, 0x00, 0x00, 0x00))
            }
        }
        if (!_rawSignatureValidation(userOpHash, userOp.signature)) {
            return 1;
        }
        return 0;
    }

    function execute(address target, uint256 value, bytes calldata data)
        external payable onlyEntryPointOrSelf
    {
        _call(target, value, data);
    }
    // ...
}
```

The EOA delegates via a type-4 transaction, initializes the account with a trusted EntryPoint address, and then submits UserOperations through the ERC-4337 flow.

## Attack 1: Front-Running `initialize()` (Critical)

This is the most dangerous vulnerability specific to EIP-7702 wallets with configurable state.

### The Problem

When an EIP-7702 wallet stores mutable configuration — such as the trusted EntryPoint address — it needs an initialization step. If `initialize()` has no access control, any address can call it. There is a window between the moment the EOA delegates its code (the authorization tuple is processed) and the moment the owner calls `initialize()`. An attacker monitoring the mempool can front-run this call.

### Attack Flow

```
1. Alice delegates her EOA to SmartAccount7702 via EIP-7702
2. Attacker observes the delegation transaction in the mempool
3. Attacker calls alice.initialize(attackerContract) with higher gas price
4. attackerContract is now the trusted "EntryPoint" for Alice's account
5. attackerContract calls alice.execute(usdc, 0, transfer(attacker, balance))
6. onlyEntryPointOrSelf passes because msg.sender == entryPoint()
7. Alice's USDC balance is drained
```

The attacker does not need Alice's private key. They only need to call a public function faster than Alice does.

### The Fix

Require `msg.sender == address(this)` in `initialize()`:

```solidity
function initialize(address entryPoint_) external initializer {
    if (msg.sender != address(this)) revert Unauthorized();
    _getEntryPointStorage().entryPoint = entryPoint_;
}
```

The EntryPoint address is stored in [ERC-7201](https://eips.ethereum.org/EIPS/eip-7201) namespaced storage (a slot derived from `keccak256("smartaccount7702.entrypoint")`), which prevents collision if the EOA previously delegated to a different implementation that wrote to low storage slots.

Under EIP-7702, only the EOA can send a transaction where `msg.sender == address(this)`. The EOA bundles both the authorization tuple and the `initialize()` call in a single type-4 transaction:

```
Type-4 Transaction:
  authorization_list: [{chainId, implementationAddress, nonce, sig}]
  to: alice (self)
  data: abi.encodeCall(initialize, (entryPointAddress))
```

This makes delegation and initialization atomic. There is no window for front-running.

### Testing the Fix

```solidity
function test_attack_frontRunInitialize_reverts() public {
    _setupUninitialized();

    MaliciousEntryPoint malicious = new MaliciousEntryPoint();

    // Attacker tries to front-run initialize()
    vm.prank(attacker);
    vm.expectRevert(SmartAccount7702.Unauthorized.selector);
    smartAccount.initialize(address(malicious));

    // Alice's account is still uninitialized
    assertEq(smartAccount.entryPoint(), address(0));
}
```

A complementary test verifies that callback-based attacks also fail. If a malicious contract receives a callback from the wallet during execution and tries to call `initialize()`, it is rejected because `msg.sender` is the malicious contract's address, not `address(this)`.

### Design Consideration

An alternative approach is to make the EntryPoint address immutable (set in the constructor, shared by all delegating EOAs). This eliminates the initialization attack entirely but removes flexibility: all EOAs must use the same EntryPoint version. The initializable pattern is a trade-off between configurability and attack surface.

## Attack 2: Unauthorized Execution

Every execution function (`execute`, `executeBatch`, `deploy`, `deployDeterministic`) is gated by the `onlyEntryPointOrSelf` modifier:

```solidity
modifier onlyEntryPointOrSelf() {
    if (msg.sender != entryPoint() && msg.sender != address(this)) {
        revert Unauthorized();
    }
    _;
}
```

This permits exactly two callers:

1. **The trusted EntryPoint** — for ERC-4337 UserOperation execution
2. **The EOA itself** — for direct transactions where `msg.sender == address(this)` under EIP-7702

Any external address attempting to call `execute()`, `executeBatch()`, or the deployment functions receives an `Unauthorized` revert. This applies equally to ETH transfers (`execute(attacker, balance, "")`) and token transfers (`execute(token, 0, transferCalldata)`).

The `validateUserOp` function is further restricted to `onlyEntryPoint` — the EOA itself cannot call it directly, which prevents any confusion between direct execution and UserOp validation paths.

## Attack 3: Re-Initialization

Once `initialize()` has been called, OpenZeppelin's `Initializable` modifier prevents any subsequent call — even from the EOA itself:

```solidity
function test_attack_reinitialize_reverts() public {
    _setupInitialized();

    MaliciousEntryPoint malicious = new MaliciousEntryPoint();

    // Even the EOA itself cannot re-initialize
    vm.prank(alice);
    vm.expectRevert();
    smartAccount.initialize(address(malicious));

    // EntryPoint unchanged
    assertEq(smartAccount.entryPoint(), address(entryPoint));
}
```

The `Initializable` contract uses ERC-7201 namespaced storage to track initialization state. This storage lives on the EOA (not the implementation), so each EOA has independent initialization tracking.

An important nuance: if the EOA re-delegates to a different implementation that does not use `Initializable`, the guard is lost. The `_initialized` flag still exists in storage, but the new implementation does not check it. This is a residual risk discussed in the final section.

## Attack 4: Signature Security

Signature verification in an EIP-7702 wallet operates on three layers, each preventing a different class of attack.

### Layer 1: ECDSA Recovery

`SignerEIP7702` (from OpenZeppelin) provides `_rawSignatureValidation`:

```solidity
function _rawSignatureValidation(bytes32 hash, bytes calldata signature)
    internal view virtual override returns (bool)
{
    (address recovered, ECDSA.RecoverError err, ) = ECDSA.tryRecover(hash, signature);
    return address(this) == recovered && err == ECDSA.RecoverError.NoError;
}
```

The recovered address must match `address(this)` — which is the EOA under EIP-7702. Only the holder of the EOA's private key can produce a valid signature.

A UserOp signed by the wrong private key causes `validateUserOp` to return `1` (`SIG_VALIDATION_FAILED`). The EntryPoint rejects the operation.

### Layer 2: EntryPoint Nonce

Each UserOperation carries a nonce managed by the ERC-4337 EntryPoint. After a UserOp is processed, the nonce is incremented. Replaying the exact same UserOp with the same nonce causes the EntryPoint to revert.

```solidity
// First submission succeeds
entryPoint.handleOps(ops, payable(bundler));

// Replay with the exact same UserOp and nonce -- reverts
vm.expectRevert();
entryPoint.handleOps(ops, payable(bundler));
```

This is the standard ERC-4337 replay protection and requires no additional logic in the wallet.

### Layer 3: ERC-7739 Domain Binding

For ERC-1271 signature verification (`isValidSignature`), the wallet uses ERC-7739 anti-replay. The signed data includes an EIP-712 domain separator that encodes `address(this)`:

```
domainSeparator = keccak256(abi.encode(
    keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
    keccak256("TSmart Account 7702"),
    keccak256("1"),
    block.chainid,
    address(this)  // The EOA address
))
```

A signature valid on Alice's account (where `address(this) = alice`) is invalid on Bob's account (where `address(this) = bob`), because the domain separators differ. This prevents cross-account replay — a risk that matters especially when one private key controls multiple EIP-7702 delegated accounts.

ERC-7739 also preserves the original EIP-712 type structure in the nested hash, so wallet UIs display the actual message content rather than an opaque hash. This is a meaningful improvement over simpler wrapper schemes (like Coinbase's `CoinbaseSmartWalletMessage(bytes32 hash)`) in terms of phishing resistance.

## Attack 5: Uninitialized Account Exploitation

Before `initialize()` is called, `entryPoint()` returns `address(0)`. This creates a safe default:

- `onlyEntryPoint` blocks all calls because no real `msg.sender` can equal `address(0)`
- `onlyEntryPointOrSelf` only allows the EOA itself (`msg.sender == address(this)`)
- The account cannot process UserOperations (no EntryPoint to validate through)

The account is inert: non-functional but not exploitable. The EOA can still recover by calling `initialize()` on itself at any time.

```solidity
function test_attack_uninitializedAccount_isInert() public {
    _setupUninitialized();

    assertEq(smartAccount.entryPoint(), address(0));

    // Attacker cannot call execute
    vm.prank(attacker);
    vm.expectRevert(SmartAccount7702.Unauthorized.selector);
    smartAccount.execute(attacker, 1 ether, "");

    // Alice CAN call execute on herself (msg.sender == address(this))
    vm.prank(alice);
    smartAccount.execute(address(0x1234), 0, "");
}
```

## Paymaster Dependency Risk

A common ERC-4337 design is to rely entirely on a paymaster for gas sponsorship. The wallet never holds ETH and `missingAccountFunds` is always 0. This creates a single point of failure: if the paymaster goes offline, is discontinued, or censors the account, the wallet cannot submit any UserOperations.

A more resilient design supports both modes:

- **With paymaster**: `missingAccountFunds` is 0, the paymaster covers gas. No ETH needed.
- **Self-funded**: When no paymaster is attached, `validateUserOp` pays `missingAccountFunds` to the EntryPoint from the account's ETH balance.

```solidity
if (missingAccountFunds > 0) {
    assembly ("memory-safe") {
        pop(call(gas(), caller(), missingAccountFunds, 0x00, 0x00, 0x00, 0x00))
    }
}
```

The `pop` discards the return value — if the transfer fails (insufficient balance), the EntryPoint catches the shortfall in its own post-validation accounting and reverts the entire UserOp. This is the standard ERC-4337 prefund pattern.

Supporting self-funded UserOps ensures the wallet remains functional even if all paymaster services are unavailable. The EOA can always fall back to holding ETH.

## Token Receiver Callbacks Under EIP-7702

Under EIP-7702, the EOA has code (`address.code.length > 0`). This has a subtle but important consequence: ERC-721 `safeTransferFrom` and all ERC-1155 transfers check whether the recipient implements the receiver callback interface. If the recipient has code but does not implement the expected callback, the transfer reverts.

This is especially critical for **ERC-1155**, which has **no** non-safe transfer function — without `onERC1155Received`, the wallet cannot receive any ERC-1155 tokens at all.

A delegated EOA must implement:

| Callback | Returns | Standard |
|---|---|---|
| `onERC721Received` | `0x150b7a02` | ERC-721 |
| `onERC1155Received` | `0xf23a6e61` | ERC-1155 |
| `onERC1155BatchReceived` | `0xbc197c81` | ERC-1155 |

All three can be `pure` functions (no state reads or writes), which eliminates any reentrancy concern from the callback. `supportsInterface` should also advertise `IERC721Receiver` and `IERC1155Receiver`.

Without these callbacks, a delegated EOA that previously received ERC-721/ERC-1155 tokens as a plain EOA (before delegation) would still hold those tokens, but could no longer receive new ones via safe transfer methods.

## The Dual Nonce Problem: EVM Nonce vs EntryPoint Nonce

This is a subtle issue that surfaces when a smart wallet deploys contracts via CREATE.

### Two Independent Nonce Systems

An EIP-7702 smart wallet operates with two completely independent nonces:

1. **EntryPoint nonce**: managed by the ERC-4337 EntryPoint contract. Incremented for every validated UserOperation. Used for UserOp replay protection.
2. **EVM nonce**: the account's transaction nonce stored in the protocol state. Incremented only by `CREATE` opcodes, not by `CALL` or `DELEGATECALL`.

A wallet that has processed 100 UserOperations via `execute()` (which uses CALL internally) still has an EVM nonce of 0 if it has never deployed a contract.

### Why This Matters

The CREATE opcode derives the deployed contract address from `keccak256(rlp([deployer, evmNonce]))`. If you use the EntryPoint nonce instead of the EVM nonce to predict a CREATE address, the prediction is wrong.

For deterministic deployments, CREATE2 avoids this problem entirely: `keccak256(0xff ++ deployer ++ salt ++ keccak256(creationCode))` has no nonce dependency. CREATE2 is recommended when the deployed address must be known in advance.

### Testing Pitfall

In Foundry, `vm.etch` (used to simulate EIP-7702 delegation in tests) copies bytecode onto an address but does **not** modify the EVM nonce. For a fresh address in a test, the nonce starts at 0. However, real EIP-7702 delegation consumes an EOA nonce (the authorization tuple increments it), so production nonces may differ from test nonces. This can cause CREATE address prediction mismatches between tests and production.

The workaround is to query the actual nonce dynamically:

```solidity
uint256 currentNonce = vm.getNonce(alice);
address predicted = vm.computeCreateAddress(alice, currentNonce);
```

Rather than hardcoding an assumed nonce value.

## Residual Risks: What Cannot Be Fixed

These risks are inherent to the EIP-7702 model and have no smart-contract-level mitigation.

### Private Key Compromise

If the EOA's private key is stolen, the attacker has full control. They can:

- Sign valid UserOperations to drain all assets
- Re-delegate to a malicious implementation
- Send legacy transactions that bypass the smart account entirely

There is no multi-sig, guardian, or social recovery in a single-EOA EIP-7702 design. The EOA key is the sole authority by design.

### Re-Delegation to Malicious Implementation

The EOA can re-delegate to any contract at any time by signing a new type-4 transaction. If the owner is tricked into signing an authorization tuple pointing to a malicious implementation, the new code executes in the EOA's context with full access to its storage and assets.

There is no on-chain mechanism to restrict which implementations an EOA can delegate to. This is an inherent property of EIP-7702.

### Legacy Transaction Bypass

Even with delegation active, the EOA can send a regular type-0 or type-2 transaction. This transaction does not go through `validateUserOp` or any smart account logic. It executes directly as a plain EOA transaction.

This means all smart account access control — `onlyEntryPoint`, `onlyEntryPointOrSelf`, paymaster sponsorship — can be bypassed by the EOA sending a legacy transaction. This is by design (the EOA retains full sovereignty), but protocol integrators must be aware of it.

### Delegation Revocation During Pending UserOps

If the EOA revokes delegation (sends a new type-4 transaction with a different or null implementation) while UserOperations are in the mempool, those UserOps will fail at execution time since the bytecode is no longer available at the EOA's address.

### Storage Persistence Across Re-Delegation

Storage survives re-delegation because it lives on the EOA, not the implementation. If the EOA re-delegates to a new implementation with a different storage layout, old state can be misinterpreted. ERC-7201 namespaced storage mitigates but does not fully eliminate this risk.

More specifically, the `Initializable._initialized` flag persists. If the new implementation does not use `Initializable`, the flag exists in storage but is never checked — the initialization guard is effectively bypassed.

## Protocol Integration Warnings

For protocols that interact with EIP-7702 accounts:

- **Do not cache `EXTCODEHASH`**: the code can change or disappear if delegation is revoked.
- **Do not cache `isValidSignature` results**: delegation can change between calls, altering the signature validation logic.
- **Do not assume `code.length > 0` is permanent**: an EIP-7702 account can become a regular EOA mid-block if delegation is revoked.
- **Flash loan protocols**: be aware that an EIP-7702 account can transition from "has code" to "no code" within a single block.

## Summary

![EIP-7702-threat-model]({{site.url_complet}}/assets/article/blockchain/ethereum/eip-7702/EIP-7702-threat-model.png)

```
@startmindmap
* EIP-7702 Threat Model
** Initialization
*** Front-running initialize()
**** CRITICAL if no access control
**** Fix: require msg.sender == address(this)
**** Atomic delegation + init in type-4 tx
*** Re-initialization
**** Blocked by OpenZeppelin Initializable
**** Storage-based guard per EOA
*** Uninitialized state
**** Safe default: entryPoint() = address(0)
**** Account is inert, not exploitable
*** ERC-7201 namespaced storage
**** Prevents slot collision under re-delegation
**** Used for both EntryPoint and Initializable state
** Access Control
*** onlyEntryPoint
**** validateUserOp restricted to EntryPoint
*** onlyEntryPointOrSelf
**** execute/deploy restricted to EntryPoint or EOA
*** Unauthorized callers always revert
** Gas Model
*** Paymaster-sponsored (missingAccountFunds = 0)
*** Self-funded (account pays prefund to EntryPoint)
*** Dual mode prevents paymaster dependency
** Token Receivers
*** EIP-7702 EOA has code → callbacks required
*** onERC721Received, onERC1155Received, onERC1155BatchReceived
*** Without callbacks: ERC-1155 reception impossible
*** Pure functions → no reentrancy risk
** Signature Security
*** ECDSA recovery (ecrecover == address(this))
*** EntryPoint nonce (UserOp replay protection)
*** ERC-7739 domain binding (cross-account replay)
** Contract Deployment
*** Dual nonce system (EntryPoint vs EVM)
*** CREATE address depends on EVM nonce, not EntryPoint nonce
*** CREATE2 recommended for deterministic addresses
*** Foundry vm.etch increments EVM nonce (testing pitfall)
** Residual Risks (No Contract-Level Fix)
*** Private key compromise
*** Re-delegation to malicious implementation
*** Legacy transaction bypass
*** Delegation revocation during pending UserOps
*** Storage persistence across re-delegation
** Protocol Integration
*** Do not cache EXTCODEHASH
*** Do not cache isValidSignature results
*** code.length > 0 is not permanent
@endmindmap
```

## Reference

- [EIP-7702: Set Code for EOAs](https://eips.ethereum.org/EIPS/eip-7702)
- [ERC-4337: Account Abstraction Using Alt Mempool](https://eips.ethereum.org/EIPS/eip-4337)
- [ERC-7739: Readable Typed Signatures for Smart Accounts](https://eips.ethereum.org/EIPS/eip-7739)
- [OpenZeppelin Contracts — SignerEIP7702](https://docs.openzeppelin.com/contracts/5.x/)
- [OpenZeppelin Contracts — ERC7739 (draft)](https://docs.openzeppelin.com/contracts/5.x/)
- [OpenZeppelin Contracts — Initializable](https://docs.openzeppelin.com/contracts/5.x/api/proxy#Initializable)
- [Foundry Book — Cheatcodes](https://book.getfoundry.sh/cheatcodes/)
- [SmartAccount7702 — Source Repository](https://github.com/smart-wallet-7702)
