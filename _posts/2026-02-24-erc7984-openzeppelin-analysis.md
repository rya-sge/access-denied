---
layout: post
title: Technical Analysis of the OpenZeppelin ERC-7984 Implementation
date: 2026-02-24
lang: en
locale: en-GB
categories: blockchain solidity cryptography
tags: blockchain fhe erc7984 openzeppelin confidential-token zama
description: A deep technical analysis of the OpenZeppelin ERC-7984 Confidential Fungible Token implementation, covering the core accounting model, FHE-safe arithmetic, ACL access patterns, operator system, and the extension ecosystem.
image: /assets/article/blockchain/zamafhe/openzeppelin_confidential_token_mindmap.png
isMath: false
---

ERC-7984 is OpenZeppelin's draft standard for a Confidential Fungible Token built on the Zama FHEVM. 

Unlike ERC-20, where all balances and transfer amounts are public state, ERC-7984 stores every balance and amount as a `euint64` — an encrypted 64-bit integer managed by a coprocessor network. 

This article provides a detailed analysis of the reference implementation found in the `openzeppelin-confidential-contracts` library (v0.3.0), covering the core accounting logic, the safety arithmetic library, the ACL access pattern, the operator system, the disclosure mechanism, and the available extensions.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Background and Scope

The implementation resides under `contracts/token/ERC7984/` and comprises:

| File | Role |
|------|------|
| `ERC7984.sol` | Core contract |
| `utils/ERC7984Utils.sol` | Transfer-and-call callback utility |
| `utils/FHESafeMath.sol` | Overflow-safe FHE arithmetic |
| `extensions/ERC7984ObserverAccess.sol` | Per-account observer slot |
| `extensions/ERC7984Freezable.sol` | Confidential partial freeze |
| `extensions/ERC7984Restricted.sol` | Cleartext transfer restrictions |
| `extensions/ERC7984Rwa.sol` | Pre-assembled RWA token with compliance features |
| `extensions/ERC7984Omnibus.sol` | Omnibus settlement with encrypted sub-accounts |
| `extensions/ERC7984Votes.sol` | Governance voting extension |

The analysis focuses on the first six files and the RWA bundle. All FHE types (`euint64`, `ebool`, `externalEuint64`) are provided by the `@fhevm/solidity` library.

---

## Storage Model

The core state of `ERC7984` is deliberately minimal:

```solidity
mapping(address holder => euint64) private _balances;
mapping(address holder => mapping(address spender => uint48)) private _operators;
euint64 private _totalSupply;
```

Three design decisions are worth noting immediately.

**Encrypted balances, cleartext operators.** Balances are encrypted (`euint64`) but operator expiration timestamps are stored as plain `uint48`. The delegation relationship itself — who may spend on whose behalf, until when — is fully visible on-chain. Only the transferred amount is hidden.

**uint64 cap.** `euint64` has a maximum representable value of approximately 18.4 × 10¹⁸. With the recommended 6 decimals (rather than 18), the maximum realistic total supply is approximately 18.4 trillion tokens. The standard mandates 6 decimals by default:

```solidity
function decimals() public view virtual returns (uint8) {
    return 6;
}
```

This is a deliberate trade-off between supply range and FHE circuit complexity. Using 18 decimals would limit a token to roughly 18 units at full precision.

**Handle semantics.** A `euint64` value is not the ciphertext itself — it is a 32-byte pointer (a *ciphertext handle*) referencing an encrypted value managed off-chain by the coprocessor network. Every arithmetic operation produces a new handle; the old handle is not automatically invalidated. This staleness property has important implications for ACL management, discussed below.

---

## The `_update` Function

All state-changing operations — mint, burn, and transfer — converge into a single internal function:

```solidity
function _update(address from, address to, euint64 amount) internal virtual returns (euint64 transferred)
```

The `from == address(0)` and `to == address(0)` conventions mirror the ERC-20 pattern: minting routes through `address(0)` as source, burning routes through `address(0)` as destination.

### Phase 1 — Debit

```solidity
if (from == address(0)) {
    (success, ptr) = FHESafeMath.tryIncrease(_totalSupply, amount);
    FHE.allowThis(ptr);
    _totalSupply = ptr;
} else {
    euint64 fromBalance = _balances[from];
    require(FHE.isInitialized(fromBalance), ERC7984ZeroBalance(from));
    (success, ptr) = FHESafeMath.tryDecrease(fromBalance, amount);
    FHE.allowThis(ptr);
    FHE.allow(ptr, from);
    _balances[from] = ptr;
}
```

For a transfer or burn, `FHESafeMath.tryDecrease` attempts to subtract `amount` from `fromBalance` and returns an encrypted boolean `success`. Crucially, the new balance handle `ptr` is immediately stored and ACL-granted to the contract and to `from`. The decrement happens unconditionally at the FHE level — the success flag is only used in the next phase to determine the actual transferred amount.

Note the cleartext guard: `require(FHE.isInitialized(fromBalance))`. This is the only plaintext check in the function. It verifies that the sender has ever received tokens; it does not reveal whether the balance is sufficient. An account that has received and then spent all its tokens still has an initialized handle, and `tryDecrease` will correctly compute `success = false` in the FHE domain.

### Phase 2 — Compute Actual Transfer Amount

```solidity
transferred = FHE.select(success, amount, FHE.asEuint64(0));
```

`FHE.select` is an encrypted conditional (a multiplexer). Since `success` is an `ebool`, this operation is performed homomorphically: the result is a new ciphertext whose plaintext is either `amount` or `0`, but no observer — including the chain itself — can tell which case was taken. This is the mechanism by which insufficient-balance transfers silently transfer zero without revealing the balance state.

### Phase 3 — Credit

```solidity
if (to == address(0)) {
    ptr = FHE.sub(_totalSupply, transferred);
    FHE.allowThis(ptr);
    _totalSupply = ptr;
} else {
    ptr = FHE.add(_balances[to], transferred);
    FHE.allowThis(ptr);
    FHE.allow(ptr, to);
    _balances[to] = ptr;
}
```

For a burn (`to == address(0)`), the total supply is decremented by `transferred` — not by `amount`. This preserves the supply invariant: if the debit failed (insufficient balance), `transferred` is `0`, and the supply is unchanged. For a transfer or mint, the recipient's balance is incremented by `transferred`.

Note that for burns, `FHE.sub` is used rather than `FHESafeMath.tryDecrease`. This is safe because `transferred <= fromBalance` is guaranteed by construction: the debit phase already ensured the sender's balance was decremented by at most `amount`, and `transferred <= amount`.

### Phase 4 — ACL Grants

```solidity
if (from != address(0)) FHE.allow(transferred, from);
if (to != address(0)) FHE.allow(transferred, to);
FHE.allowThis(transferred);
emit ConfidentialTransfer(from, to, transferred);
```

Both participants are granted permanent ACL access to the `transferred` ciphertext. This allows them to later request decryption of the actual transferred amount — useful for the sender to confirm that the transfer was effective and for the recipient to verify receipt.

`FHE.allow()` is permanent and irrevocable. Once a handle has been allowed to an address, that permission cannot be withdrawn. This is a protocol-level constraint of the Zama ACL system, not a choice of the implementation.

---

## FHESafeMath

The `FHESafeMath` library provides four operations — `tryIncrease`, `tryDecrease`, `tryAdd`, `trySub` — each returning `(ebool success, euint64 result)`.

### Overflow Detection via Wrapping Arithmetic

Standard FHE arithmetic wraps on overflow (modular `uint64`). FHESafeMath detects overflow by exploiting this property:

```solidity
function tryIncrease(euint64 oldValue, euint64 delta) internal returns (ebool success, euint64 updated) {
    if (!FHE.isInitialized(oldValue)) {
        return (FHE.asEbool(true), delta);
    }
    euint64 newValue = FHE.add(oldValue, delta);
    success = FHE.ge(newValue, oldValue);
    updated = FHE.select(success, newValue, oldValue);
}
```

After addition, if `newValue >= oldValue`, no overflow occurred. If `newValue < oldValue`, the addition wrapped around and the result is discarded in favor of the original `oldValue`. All comparisons are encrypted and do not reveal the magnitude of any value.

### Underflow Detection

```solidity
function tryDecrease(euint64 oldValue, euint64 delta) internal returns (ebool success, euint64 updated) {
    if (!FHE.isInitialized(oldValue)) {
        if (!FHE.isInitialized(delta)) {
            return (FHE.asEbool(true), oldValue);
        }
        return (FHE.eq(delta, 0), FHE.asEuint64(0));
    }
    success = FHE.ge(oldValue, delta);
    updated = FHE.select(success, FHE.sub(oldValue, delta), oldValue);
}
```

`FHE.ge(oldValue, delta)` computes `success` as an encrypted boolean indicating whether subtraction is safe. The result is selected homomorphically. One edge case is notable: if `oldValue` is uninitialized but `delta` is initialized, the function returns `success = (delta == 0)`. This means attempting to transfer a non-zero amount from an uninitialized balance is treated as a failure, consistent with the zero-balance guard in `_update`.

---

## Dual-Overload Transfer Pattern

Every public transfer function exists in two variants: one accepting `externalEuint64` with an accompanying ZKPoK, and one accepting a pre-existing `euint64` handle.

```solidity
// Variant 1: Encrypted input with proof
function confidentialTransfer(address to, externalEuint64 encryptedAmount, bytes calldata inputProof)
    public virtual returns (euint64) {
    return _transfer(msg.sender, to, FHE.fromExternal(encryptedAmount, inputProof));
}

// Variant 2: Existing handle (caller must have ACL access)
function confidentialTransfer(address to, euint64 amount) public virtual returns (euint64) {
    require(FHE.isAllowed(amount, msg.sender), ERC7984UnauthorizedUseOfEncryptedAmount(amount, msg.sender));
    return _transfer(msg.sender, to, amount);
}
```

`FHE.fromExternal` validates the ZKPoK and converts the external ciphertext into an internal `euint64` handle, granting transient ACL access to `msg.sender` and the contract. The second variant requires the caller to already hold ACL access — enforced via the cleartext `FHE.isAllowed()` check. The handle itself is not decrypted during this check.

This dual-overload pattern appears across all eight transfer functions and the mint/burn functions in derived contracts, creating a consistent API surface.

---

## Operator System

Unlike ERC-20 allowances (amount-bounded, infinite time), the ERC-7984 operator system is time-bounded and amount-unlimited:

```solidity
mapping(address holder => mapping(address spender => uint48)) private _operators;

function isOperator(address holder, address spender) public view virtual returns (bool) {
    return holder == spender || block.timestamp <= _operators[holder][spender];
}
```

An operator is either the account itself or an address whose expiration timestamp has not passed. There is no per-amount limit: an approved operator may transfer any amount during the approval window. This is a deliberate design decision that simplifies the FHE accounting — FHE comparison against an allowance would require additional encrypted operations.

The trade-off is significant for users: granting operator access grants full control over the holder's balance for the duration of the approval. Contracts integrating ERC-7984 should communicate this clearly to users.

---

## Disclosure Mechanism

Two functions support voluntary disclosure of encrypted amounts:

```solidity
function requestDiscloseEncryptedAmount(euint64 encryptedAmount) public virtual {
    require(FHE.isAllowed(encryptedAmount, msg.sender), ...);
    FHE.makePubliclyDecryptable(encryptedAmount);
    emit AmountDiscloseRequested(encryptedAmount, msg.sender);
}

function discloseEncryptedAmount(euint64 encryptedAmount, uint64 cleartextAmount, bytes calldata decryptionProof) public virtual {
    bytes32[] memory handles = new bytes32[](1);
    handles[0] = euint64.unwrap(encryptedAmount);
    bytes memory cleartextMemory = abi.encode(cleartextAmount);
    FHE.checkSignatures(handles, cleartextMemory, decryptionProof);
    emit AmountDisclosed(encryptedAmount, cleartextAmount);
}
```

`requestDiscloseEncryptedAmount` marks a handle as publicly decryptable — any off-chain party can then request its plaintext from the KMS without holding ACL access. `discloseEncryptedAmount` finalizes the process by verifying the decryption proof on-chain and emitting the cleartext value.

These functions implement the complete two-phase public decryption flow (request → KMS → verify) within the token contract itself, without requiring any external callback infrastructure.

---

## Transfer-and-Call

The `_transferAndCall` pattern extends the ERC-1363 receiver interface to the FHE domain:

```solidity
function _transferAndCall(address from, address to, euint64 amount, bytes calldata data)
    internal returns (euint64 transferred) {
    euint64 sent = _transfer(from, to, amount);
    ebool success = ERC7984Utils.checkOnTransferReceived(msg.sender, from, to, sent, data);
    euint64 refund = _update(to, from, FHE.select(success, FHE.asEuint64(0), sent));
    transferred = FHE.sub(sent, refund);
}
```

The receiver contract's `onConfidentialTransferReceived` function returns an `ebool`. If it returns false, a refund is issued via a second `_update` call. The refund amount is `FHE.select(success, 0, sent)` — the entire transferred amount is refunded on failure. `transferred` is the net amount: `sent - refund`, which is either `sent` (accepted) or `0` (rejected). Both outcomes are private; the on-chain observer sees two `_update` calls but cannot determine whether the callback was accepted.

`ERC7984Utils.checkOnTransferReceived` skips the callback for EOAs, returning an encrypted `true`, consistent with the ERC-1363 approach.

---

## Extension Ecosystem

### `ERC7984ObserverAccess` — Per-Account Observer

```solidity
mapping(address account => address) private _observers;
```

Each account can designate a single observer address. On every `_update`, the observer receives `FHE.allow()` on both the updated balance handle and the transferred amount handle. This provides continuously current read access without any on-chain interaction from the observer after the initial setup.

The observer can set itself to `address(0)` to abdicate (the only self-service removal path). The account can replace the observer at any time, but ACL grants already issued to the previous observer remain valid.

### `ERC7984Freezable` — Confidential Partial Freeze

Unlike the cleartext freeze in CMTAT (which blocks the account entirely), `ERC7984Freezable` stores a confidential frozen amount per account:

```solidity
mapping(address account => euint64 encryptedAmount) private _frozenBalances;
```

Transfers are gated on the available (unfrozen) balance:

```solidity
function _update(address from, address to, euint64 encryptedAmount) internal virtual override returns (euint64) {
    if (from != address(0)) {
        euint64 unfrozen = _confidentialAvailable(from);
        encryptedAmount = FHE.select(FHE.le(encryptedAmount, unfrozen), encryptedAmount, FHE.asEuint64(0));
    }
    return super._update(from, to, encryptedAmount);
}
```

`FHE.select(FHE.le(amount, unfrozen), amount, 0)` either passes the requested amount through or substitutes zero — all homomorphically. From an observer's perspective, the transfer either proceeds or silently transfers nothing; the frozen amount is never revealed.

### `ERC7984Restricted` — Cleartext Transfer Restrictions

In contrast to `ERC7984Freezable`, the restriction state is stored in cleartext:

```solidity
mapping(address account => Restriction) private _restrictions;

enum Restriction { DEFAULT, BLOCKED, ALLOWED }
```

Whether an account is `BLOCKED` or `ALLOWED` is fully visible on-chain. The `_update` override calls `_checkSenderRestriction` and `_checkRecipientRestriction` before invoking the parent, reverting in cleartext if either party is blocked. This is an intentional trade-off: compliance operators need to verify restriction status without decryption overhead, and the restriction itself carries no financial information.

### `ERC7984Rwa` — Pre-Assembled RWA Bundle

`ERC7984Rwa` combines `ERC7984Freezable`, `ERC7984Restricted`, `Pausable`, `AccessControl`, and `Multicall` into a single abstract contract with a single `AGENT_ROLE`. The `_update` override chains all compliance checks:

```solidity
function _update(address from, address to, euint64 encryptedAmount)
    internal virtual override(ERC7984Freezable, ERC7984Restricted) whenNotPaused returns (euint64) {
    return super._update(from, to, encryptedAmount);
}
```

`forceConfidentialTransferFrom` bypasses the `from` restriction check and the pause state by calling `super._update` directly, skipping the overridden chain. The bypass detection relies on a function selector comparison:

```solidity
function _isForceTransfer() private pure returns (bool) {
    return
        msg.sig == 0x6c9c3c85 ||
        msg.sig == 0x44fd6e40;
}
```

This approach is functional but fragile: if a function selector changes (due to a parameter type change, for example), the bypass silently stops working. Hardcoded selectors require explicit maintenance.

### `ERC7984Omnibus` — Encrypted Sub-Account Settlement

The omnibus extension enables institutional custody patterns where multiple beneficial owners share a single on-chain address. Sub-account identities are provided as `externalEaddress` (encrypted Ethereum addresses) and are recorded in the `OmnibusConfidentialTransfer` event:

```solidity
event OmnibusConfidentialTransfer(
    address indexed omnibusFrom,
    address indexed omnibusTo,
    eaddress sender,
    eaddress indexed recipient,
    euint64 amount
);
```

No on-chain sub-account balance accounting is performed. The implementation states explicitly: *"There is no onchain accounting for sub-accounts — integrators must track sub-account balances externally."* The contract provides only settlement finality between custodian addresses; the attribution of that settlement to specific beneficial owners is an off-chain responsibility.

---

## Summary of Design Invariants

The following invariants are maintained by the core implementation:

| Invariant | Mechanism |
|-----------|-----------|
| `sum(_balances) == _totalSupply` | `transferred` (not `amount`) is used for both debit and credit |
| Insufficient-balance transfers succeed silently | `FHE.select(success, amount, 0)` |
| No balance is ever decremented below zero | `FHESafeMath.tryDecrease` returns original value on underflow |
| Total supply never overflows | `FHESafeMath.tryIncrease` returns original value on overflow |
| ACL access is always current after an update | Every new handle is immediately granted to the contract and the affected addresses |

---

## Notable Limitations

**ACL permanence.** `FHE.allow()` grants are irrevocable. Revoking an observer, removing an operator, or otherwise changing authorization does not affect previously issued grants. The only mitigation is handle rotation: once a balance is updated by any transfer, the old handle becomes stale and the observer no longer has access to the current balance.

**`uint64` arithmetic range.** The 64-bit ceiling imposes constraints on decimal precision and total supply. Contracts with high-precision tokens or very large total supplies must account for this limit explicitly. There is no built-in warning or revert if the supply approaches the maximum.

**Cleartext restriction visibility (`ERC7984Restricted`).** The `BLOCKED`/`ALLOWED` state of any account is visible to anyone reading storage. For use cases where the restriction list itself is sensitive, an FHE-based restriction mechanism would be necessary, at significant additional gas cost.

**Operator unlimited amount.** Granting an operator provides unrestricted access to the holder's entire balance until expiration. There is no partial-allowance mechanism analogous to ERC-20's `approve`. This simplifies the FHE accounting but changes the trust model for users.

**Hardcoded selectors in `ERC7984Rwa`** The `_isForceTransfer()` function uses hardcoded function selectors. Any refactoring of those function signatures would silently break the bypass logic without a compile-time error.

---

## Conclusion

The OpenZeppelin ERC-7984 implementation translates the well-known ERC-20 accounting model into the FHE domain with minimal structural changes. 

- The `_update` / `_mint` / `_burn` / `_transfer` pattern is preserved. 
- Overflow and underflow safety is moved from the Solidity type system (which does not apply to ciphertexts) into the `FHESafeMath` library, which produces encrypted success flags and uses `FHE.select` for conditional result selection. 
- The dual-overload transfer API cleanly separates the case where the caller submits a fresh encrypted input (with a ZKPoK) from the case where the caller already holds a ciphertext handle with ACL access.

The extension system is well-layered: 

- each extension overrides only `_update`, allowing multiple extensions to be composed through linear inheritance without ambiguity. 
- The `ERC7984Rwa` bundle demonstrates a complete compliance stack built from these extensions. 
- The omnibus extension is architecturally notable for its explicit decision to push sub-account accounting entirely off-chain.

![openzeppelin_confidential_token_mindmap]({{site.url_complet}}/assets/article/blockchain/zamafhe/openzeppelin_confidential_token_mindmap.png)

```
@startmindmap
* ERC-7984 Core
** Storage
*** euint64 _balances (encrypted)
*** euint64 _totalSupply (encrypted)
*** uint48 _operators (plaintext, timestamp)
** _update
*** Mint (from = address(0))
*** Burn (to = address(0))
*** Transfer (both non-zero)
*** FHE.select → silent zero on failure
** FHESafeMath
*** tryIncrease (overflow via wrapping)
*** tryDecrease (underflow via ge check)
** ACL Management
*** FHE.allow (permanent)
*** FHE.allowTransient (tx-scoped)
*** FHE.makePubliclyDecryptable
** Dual Overloads
*** externalEuint64 + ZKPoK
*** euint64 + isAllowed check
** Operators
*** Time-bounded (uint48)
*** Amount-unlimited
** Extensions
*** ObserverAccess (1 observer slot/account)
*** Freezable (encrypted partial freeze)
*** Restricted (cleartext blocklist/allowlist)
*** Rwa (Freezable + Restricted + Pausable)
*** Omnibus (off-chain sub-account settlement)
@endmindmap
```

---

## References

- [Claude Code](https://claude.com/product/claude-code)
- [OpenZeppelin Confidential Contracts](https://docs.openzeppelin.com/confidential-contracts)
- [ERC-7984 Draft Interface](https://docs.openzeppelin.com/confidential-contracts/erc7984)
- [Zama FHEVM Documentation](https://docs.zama.org/protocol/solidity-guides/getting-started/overview)
- [Zama ACL — Access Control List](https://docs.zama.org/protocol/solidity-guides/smart-contract/acl)
- [Zama FHE Types](https://docs.zama.org/protocol/solidity-guides/smart-contract/types)
- [ERC-1363 Token and Token Sender](https://eips.ethereum.org/EIPS/eip-1363)

