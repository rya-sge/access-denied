---
layout: post
title: "Two Ways to Build a Permissioned Token — Centrifuge's Transfer Hook Against ERC-3643"
date:   2026-08-18
lang: en
locale: en-GB
categories: blockchain ethereum defi solidity security
tags: rwa erc-3643 t-rex cmtat erc-1404 centrifuge compliance permissioned-token security-token transfer-hook
series: centrifuge
description: A comparison of two enforcement architectures for regulated tokens - Centrifuge's single swappable hook with packed eligibility data, and ERC-3643's identity registry plus compliance modules.
image: /assets/article/blockchain/defi/centrifuge/2026-08-18-centrifuge-hook-vs-erc3643-mindmap.png
isMath: false
---

A regulated token has to answer one question on every balance change: may these two parties hold and move this amount right now. [ERC-3643](https://eips.ethereum.org/EIPS/eip-3643) answers it with two external contracts, an identity registry holding verified claims about each holder and a compliance contract holding the rules of the offering. Centrifuge answers it with a single swappable hook, eligibility data packed into the same storage slot as the balance, and a convention where the protocol operation is inferred from which addresses appear in the transfer. Both are in production, both hold real assets. This article compares the two chokepoint designs, the properties each one buys, and what a reviewer should check in either.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The requirement both models serve

Strip away the standards and a permissioned token owes four things.

- **Eligibility.** Only approved parties may receive or hold, and approval expires or is revoked.
- **Freezing.** An individual holder can be stopped without stopping the token.
- **A legal override.** Some authority can move or destroy tokens against the holder's wishes, because a court order does not care about private keys.
- **Complete coverage.** Issuance and redemption are screened as tightly as transfers, since a mint to a sanctioned address is exactly as much of a problem as a transfer to one.

That last item is the one that most often fails in practice. A compliance check wired into the transfer path only, leaving mint and burn unscreened, defeats the token's regulatory purpose while looking correct in a diff.

![Where the compliance decision is made]({{site.url_complet}}/assets/article/blockchain/defi/centrifuge/permissioned-token-enforcement-models-concept.png)

## Model A: ERC-3643

T-REX splits the decision in two, and the split is conceptual rather than merely structural.

`IdentityRegistry.isVerified(address)` answers who may hold. It resolves an address to an ONCHAINID identity contract, checks the claims on that identity against the topics the token requires, and checks those claims were signed by a trusted issuer. `Compliance.canTransfer(from, to, amount)` answers whether this particular movement is permitted under the rules of the offering: holder caps, per-country limits, maximum position sizes.

The standard's own example makes the pairing explicit:

```solidity
require( _tokenIdentityRegistry.isVerified(to), "ERC-3643: Invalid identity" );
require( _tokenCompliance.canTransfer(from, to, amount), "ERC-3643: Compliance failure" );
...
_tokenCompliance.transferred(msg.sender, _to, _amount);
```

The third call matters as much as the first two. `Compliance` is stateful, tracking holder counts and per-investor positions, so it exposes `transferred`, `created` and `destroyed` hooks that the token must invoke to keep those counters accurate. A missing notification does not block anything; it silently corrupts the module's view of the cap table.

Coverage across operations is deliberate and uneven, as the standard states directly: `mint` and `forcedTransfer` check only that the receiver is verified, bypassing the compliance rules, and `burn` bypasses all eligibility checks. Freezing exists at two granularities, whole-address through `setAddressFrozen` and partial through `freezePartialTokens`. Recovery is a first-class operation: `recoveryAddress` moves a balance from a lost wallet to a new one while binding both to the same ONCHAINID.

## Model B: the Centrifuge hook

Centrifuge puts everything behind one interface. `ShareToken` is an ERC-20 that also implements [ERC-1404](https://github.com/ethereum/EIPs/issues/1404), and every balance-changing entry point funnels into one internal call:

```solidity
function _onTransfer(address from, address to, uint256 value) internal {
    address hook_ = hook;
    require(
        hook_ == address(0)
            || ITransferHook(hook_).onERC20Transfer(from, to, value, HookData(hookDataOf(from), hookDataOf(to)))
                == ITransferHook.onERC20Transfer.selector,
        RestrictionsFailed()
    );
}
```

`transfer`, `transferFrom`, `mint` and `burn` all call it. Issuance appears to the hook as a transfer from the zero address, redemption as a transfer to it, and both are screened by the same code path as an ordinary transfer. On the coverage question above, this design passes by construction rather than by discipline.

### Eligibility lives in the balance slot

The detail with the largest downstream consequences is where holder state is kept:

```solidity
struct Balance {
    /// @dev The user balance is limited to uint128. ...
    uint128 amount;
    /// @dev There are 16 bytes that are used to store hook data (e.g. restrictions for users).
    bytes16 hookData;
}
```

One 32-byte slot holds both the balance and the compliance state. Within those 16 bytes, the first 8 are a `uint64` membership expiry and the least significant bit is the freeze flag:

```solidity
function isSourceMember(address from, HookData calldata hookData) public view returns (bool) {
    return uint128(hookData.from) >> 64 >= block.timestamp || isPoolEscrow(from);
}
```

Because the token already loads both parties' balance slots to perform the transfer, it obtains their eligibility for free and passes it to the hook as calldata. The hook needs no storage read to decide the common cases, and it holds no per-user state of its own. An ERC-3643 token, by contrast, makes external calls into a registry and a compliance contract on every transfer, each with its own cold reads.

The cost of that compactness is expressiveness. Membership is one expiry timestamp and freezing is one bit, so there is no partial freeze and no per-holder position limit. Rules of that shape have to live elsewhere.

### The operation is inferred, not declared

ERC-3643 knows it is minting because `mint` was called. The Centrifuge hook sees only `(from, to, value)` and has to work out what happened, which it does by recognising addresses:

```solidity
function isDepositRequestOrIssuance(address from, address to) public view returns (bool) {
    return from == address(0) && !isPoolEscrow(to) && to != crosschainSource;
}

function isRedeemRequest(address, address to) public pure returns (bool) {
    return to == ESCROW_HOOK_ID;
}

function isCrosschainTransferExecution(address from, address to) public view returns (bool) {
    return from == crosschainSource && to != address(0);
}
```

`ESCROW_HOOK_ID` is the constant `address(uint160(0x1CF60))`, and the comment on it states the constraint that makes the scheme safe: the value is chosen so it cannot collide with any `uint16` chain identifier, since an outbound cross-chain transfer is encoded as a transfer to `address(uint160(chainId))`.

![How the hook classifies a share movement]({{site.url_complet}}/assets/article/blockchain/defi/centrifuge/centrifuge-hook-sentinel-workflow.png)

A policy is then a single function over those predicates. `FullRestrictions` in its entirety:

```solidity
if (isSourceOrTargetFrozen(from, to, hookData)) return false;

if (isDepositRequestOrIssuance(from, to)) return isTargetMember(to, hookData);
if (isDepositFulfillment(from, to)) return true;
if (isDepositClaim(from, to)) return isTargetMember(to, hookData);
if (isRedeemRequest(from, to)) return isSourceMember(from, hookData);
if (isRedeemFulfillment(from, to)) return true;
if (isRedeemClaimOrRevocation(from, to)) return true;
if (isCrosschainTransfer(from, to)) return true;
if (isCrosschainTransferExecution(from, to)) return isTargetMember(to, hookData);

// Else, it's a transfer
return isTargetMember(to, hookData);
```

Four policies ship with the protocol, differing only in that function body:

| Policy | Membership to receive | Membership to redeem | Freezing |
|--------|----------------------|---------------------|----------|
| `FullRestrictions` | Required | Required | Yes |
| `RedemptionRestrictions` | Not required | Required | Yes |
| `FreelyTransferable` | Required to request or claim only | Required | Yes |
| `FreezeOnly` | Not required | Not required | Yes |

A pool installs one per share token and can replace it through a governance message, which is a lighter operation than rewiring a compliance module graph.

## Side by side

| Dimension | Centrifuge hook | ERC-3643 / T-REX |
|-----------|-----------------|------------------|
| Contracts in the decision | One hook | Identity registry, compliance, plus modules |
| Eligibility storage | 16 bytes packed in the holder's balance slot | External registry keyed to an ONCHAINID contract |
| Reads per transfer | None beyond the balances already loaded | External calls into registry and compliance |
| Identity model | An address with an expiry | An identity contract holding claims signed by trusted issuers |
| Operation detection | Inferred from sentinel addresses | Distinct functions |
| Mint screening | Same path as transfer | Receiver verified, compliance rules bypassed |
| Burn screening | Same path as transfer | All eligibility checks bypassed |
| Freeze granularity | Whole account, one bit | Whole account and partial amounts |
| Global rules such as holder caps | Not expressible in the shipped hooks | The compliance module's purpose |
| Recovery of a lost wallet | Protocol-level token recovery through governance | `recoveryAddress` rebinding to the same identity |
| Multi-chain | Built in, with chain identifiers as sentinel targets | Out of scope for the standard |

The rows are not a scorecard. They describe two answers to the question of how much the compliance layer should know.

The Centrifuge hook knows about one token's holders and the protocol's own operations. It cannot express "no more than 500 holders, at most 50 from any one country" because it has no aggregate state. The ERC-3643 compliance contract exists precisely to hold that aggregate state, and pays for it with external calls, notification hooks that must fire exactly once, and counters that can desynchronise.

## What each model gets tested on

The failure modes differ enough that the review checklist changes with the model.

### Chokepoint equivalence

The standard first question for any regulated token: enumerate every function that changes a balance or the supply, and confirm the compliance layer actually executes on each, rather than merely that a role guard is present. Access-gated is not policy-screened.

Centrifuge routes `transfer`, `transferFrom`, `mint` and `burn` through `_onTransfer`, so the answer is uniform. In ERC-3643 the answer is deliberately non-uniform, and the reviewer's job is to confirm the actual implementation matches the standard's stated asymmetry rather than accidentally extending it. A `mint` that also skips `isVerified` is a different contract from the one the standard describes.

### The privileged bypass, and what compensates for it

Both models have a path that moves tokens without asking the policy. In Centrifuge it is `authTransferFrom`:

```solidity
function authTransferFrom(address sender, address from, address to, uint256 value)
    public
    auth
    returns (bool success)
{
    success = _transferFrom(sender, from, to, value);
    address hook_ = hook;
    if (hook_ != address(0)) {
        ITransferHook(hook_)
            .onERC20AuthTransfer(sender, from, to, value, HookData(hookDataOf(from), hookDataOf(to)));
    }
}
```

The hook is notified but cannot object: the return value is discarded, and `BaseTransferHook` implements the callback as a `pure` no-op. The interface documents this as intentional, describing the callback as unblockable and kept for compatibility with V2 share tokens.

What makes that acceptable is that callers perform the check themselves, in advance, using the sentinel vocabulary. The cross-chain transfer path shows the pattern:

```solidity
require(
    share.checkTransferRestriction(msg.sender, address(uint160(centrifugeId)), amount),
    CrossChainTransferNotAllowed()
);

share.authTransferFrom(msg.sender, msg.sender, address(this), amount);
share.burn(address(this), amount);
```

The hook is consulted with the semantically meaningful pair, sender to chain sentinel, and only then does the mechanical move bypass it. The async request manager does the same before each request and claim.

This is a sound arrangement and also a fragile one, because the check and the move are now two separate statements that can drift apart. A new privileged code path that calls `authTransferFrom` without the preceding `checkTransferRestriction` compiles, passes ordinary tests, and silently bypasses the policy. In ERC-3643 the equivalent risk is narrower, since `forcedTransfer` still runs `isVerified` on the receiver and the bypass is confined to a named function rather than to a general-purpose primitive.

There is one guard on the primitive itself, in `BalanceSheet`:

```solidity
require(!endorsements.endorsed(from), CannotTransferFromEndorsedContract());
```

which prevents the protocol's own endorsed contracts from being drained through it.

### Sentinel integrity

Inferring the operation from addresses introduces a failure mode the function-per-operation model does not have: two different meanings colliding on one address.

The protocol addresses this in three ways. `ESCROW_HOOK_ID` is documented as chosen to avoid the chain-identifier range. Pool escrows are recognised by calling `poolId()` on the candidate and confirming the factory agrees, rather than by an address list. Endorsed protocol contracts are recognised through `root.endorsed`. A custom hook that reimplements `checkERC20Transfer` and treats every non-ordinary case as permitted, without reproducing these distinctions, opens a path from the escrow to any address the protocol pays out to.

The corresponding ERC-3643 question is whether the compliance module's counters can be desynchronised, since its `created`, `transferred` and `destroyed` notifications are separate calls that a partial implementation can omit.

### Freeze semantics

Centrifuge blocks a frozen party on both legs, with an exception:

```solidity
return (uint128(hookData.from).getBit(FREEZE_BIT) == true && !isPoolEscrow(from))
    || (uint128(hookData.to).getBit(FREEZE_BIT) == true && !isPoolEscrow(to));
```

The pool escrow is never treated as frozen, which is necessary because it is a counterparty to every request and claim. `freeze` refuses to act on endorsed addresses and on pool escrows at all, so the exception cannot be reached by freezing the escrow in the first place. Two guards for one property, which is the right number for a property whose failure would halt the pool.

Frameworks that support partial freezing, including ERC-3643, CMTAT and [ERC-7943](https://eips.ethereum.org/EIPS/eip-7943), carry a different and well-documented hazard: those specifications permit freezing more than the current balance, so every `balance - frozen` computation must clamp rather than underflow. Centrifuge's single bit sidesteps that class entirely by not offering the feature.

## Choosing between them

The models suit different products.

The hook model fits a token whose compliance rules are per holder and whose issuer wants the policy to be cheap, self-contained, and replaceable. It fits multi-chain deployment naturally, since the sentinel vocabulary already includes chain identifiers and the same hook code runs on every spoke. It does not fit a product that must enforce aggregate constraints, because there is nowhere to keep the aggregate.

The registry-and-compliance model fits a token whose rules are about the cap table as a whole, and whose holders carry portable identity that other issuers also recognise. An ONCHAINID verified for one offering can satisfy another, which is a network effect a per-token memberlist cannot reproduce. It costs more gas per transfer, more contracts to deploy and wire, and more surface where a notification can be missed.

A pool that needs both can put the aggregate rules in a custom hook, since the interface permits arbitrary logic. At that point the hook is a compliance module with a different signature, and the honest comparison is between one contract holding both concerns and two contracts separating them.

## Conclusion

Both designs place a mandatory check on the path that changes balances, and both provide a privileged path around it for legal enforcement. They differ in where the knowledge sits. ERC-3643 keeps identity in a registry that outlives any one token and keeps offering rules in a compliance contract that can hold aggregate state, at the cost of external calls and notification hooks that must be kept consistent. Centrifuge keeps a holder's expiry and freeze bit in the same storage slot as their balance and hands both to a single hook that infers the protocol operation from the addresses involved, which is compact and complete across mint and burn, but limited to per-holder rules.

For a reviewer the practical consequence is that the two models fail differently. The registry model fails at its seams, where a hook is not called or a counter drifts. The hook model fails at its conventions, where a sentinel is misread or a privileged move is made without the check that was supposed to precede it.

![Permissioned token design models mindmap]({{site.url_complet}}/assets/article/blockchain/defi/centrifuge/2026-08-18-centrifuge-hook-vs-erc3643-mindmap.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Enforcement chokepoint** | The single code path every balance change must traverse, where the compliance decision is made. |
| **Transfer hook** | In the Centrifuge model, one swappable contract that receives every share movement and returns a permit or block decision. |
| **hookData** | Sixteen bytes stored alongside a holder's balance, carrying a membership expiry in the first eight and a freeze flag in the least significant bit. |
| **Sentinel address** | A reserved address that encodes a protocol operation, such as the zero address for issuance or `ESCROW_HOOK_ID` for a redemption request. |
| **Identity registry** | In ERC-3643, the external contract mapping an address to an identity contract and answering whether that holder is verified. |
| **ONCHAINID** | The identity contract holding claims about a holder, signed by issuers the token's registry trusts. |
| **Compliance contract** | In ERC-3643, the contract holding the offering's global rules and the counters that enforce them, notified on every transfer, mint and burn. |
| **Forced transfer** | A privileged movement of tokens without the holder's consent, provided for legal enforcement and exempt from some or all policy checks. |
| **Partial freeze** | Freezing a specific amount of a holder's balance rather than the whole account, supported by ERC-3643 and CMTAT but not by the Centrifuge hooks. |
| **Endorsed contract** | A protocol contract the Centrifuge root has marked as trusted, which the hooks treat as always eligible and which cannot be frozen. |

## Annex — Security Implementation Checklist

The items below apply to a permissioned token of either design. Where a requirement is specific to one model, the row says so.

### Coverage of the chokepoint

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every balance- and supply-changing entry point reaches the compliance decision, mint and burn included, verified by enumeration rather than by inspection of the transfer path. | A mint to an ineligible or sanctioned address succeeds where a transfer to the same address would revert. |
| ☐ | Where a standard defines deliberate asymmetry between operations, the implementation matches it exactly and does not extend the exemption. | A privileged path quietly becomes broader than the specification the token claims to follow. |
| ☐ | The decision is enforced, not merely computed: a view returning a restriction code is wired into a reverting check. | An advisory-only screening layer reports violations that nothing prevents. |
| ☐ | Zero-address legs are handled explicitly, so issuance and redemption are neither exempted nor bricked by a naive both-parties-must-be-eligible rule. | Either the rule blocks all issuance, or it skips it entirely. |
| ☐ | The compliance call runs exactly once per operation across any override chain. | Stateful modules double-count, skewing holder caps and position limits. |

### The privileged path

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The bypass is confined to named enforcement functions and is not reachable from ordinary transfer, mint or burn. | The entire policy becomes optional for anyone who can reach the primitive. |
| ☐ | Model-specific, hook designs: every caller of an unblockable authorised-transfer primitive performs the policy check itself beforehand, with the correct sentinel pair. | A new privileged code path moves restricted shares with no check at all, and still compiles and tests clean. |
| ☐ | The authority that freezes and the authority that moves seized funds are separable. | One compromised key both immobilises a holder and drains them. |
| ☐ | Preconditions defined by the standard for the forced path are enforced, such as a verified recipient or a previously frozen source. | Seizure becomes an unconditional transfer primitive. |
| ☐ | Protocol-owned and endorsed addresses cannot be used as the source of a privileged transfer. | Escrowed pool assets are drained through the enforcement path. |

### Eligibility state

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Membership carries an expiry that is evaluated against the current block time on every check, not cached. | Lapsed investors keep transacting until someone notices. |
| ☐ | Setting membership preserves an existing freeze flag rather than overwriting it. | Re-approving a frozen holder silently unfreezes them. |
| ☐ | Addresses the protocol depends on, such as escrows and endorsed contracts, cannot be frozen or have their eligibility revoked. | Freezing one address halts every deposit and redemption in the pool. |
| ☐ | Where partial freezing exists, every active-balance computation clamps rather than underflowing when the frozen amount exceeds the balance. | Transfers revert with an arithmetic panic and the holder is locked out entirely. |
| ☐ | Model-specific, sentinel designs: reserved addresses are provably disjoint from every other address family the protocol encodes. | Two operations collide on one address and the policy applies the wrong rule. |
| ☐ | Model-specific, registry designs: identity claims are checked against the trusted issuer set at verification time, and revocation takes effect immediately. | A revoked or self-issued claim keeps an ineligible holder verified. |

## Frequently Asked Questions

**Q: Why does storing eligibility in the balance slot matter beyond gas?**

Because it removes a class of inconsistency. When the compliance state and the balance are in the same slot, they are read atomically and cannot disagree: there is no window in which a transfer sees a fresh balance and a stale membership, and no external contract that can be repointed independently of the token.

The gas saving is real as well, since the token already loads both parties' slots to move the balance and passes the compliance bytes to the hook as calldata rather than making it read them. The cost is that 16 bytes is all the state a holder gets, which is why membership is a single expiry and freezing is a single bit.

**Q: How does the Centrifuge hook know it is looking at an issuance rather than a transfer?**

It infers it from the addresses. Issuance arrives as a transfer whose source is the zero address, so `isDepositRequestOrIssuance` tests `from == address(0)` while excluding the two cases that share that source, a fulfilment paying into the pool escrow and a cross-chain execution. Similarly, a redemption request is any transfer whose target is `ESCROW_HOOK_ID`, and an outbound cross-chain transfer is one whose target is `address(uint160(chainId))`.

The scheme depends on those reserved values being disjoint, which is why the constant carries a comment explaining it was chosen to avoid colliding with any `uint16` chain identifier.

**Q: If ERC-3643 lets mint bypass the compliance rules, is that a weakness?**

It is a deliberate scoping decision rather than an oversight, and the standard states it plainly: `mint` and `forcedTransfer` check only that the receiver is verified, and `burn` skips eligibility altogether. The reasoning is that issuance and redemption are actions the issuer takes under its own legal process, and that the compliance rules describe secondary-market circulation.

For a reviewer the point is not whether the asymmetry is right but whether the implementation reproduces it faithfully. A `mint` that also skips `isVerified` has removed the one check the standard kept, which is a materially different contract.

**Q: Both models have a way to move tokens without asking the policy. What separates a well-designed override from a dangerous one?**

Three properties, and they are the same in either model:

- **Confinement.** The bypass is reachable only through named enforcement functions, never from ordinary transfer, mint or burn.
- **Residual checks.** Something is still verified even on the override path, such as ERC-3643 requiring the receiver to be verified, or Centrifuge's callers running `checkTransferRestriction` with the appropriate sentinel pair before invoking the unblockable primitive.
- **Role separation.** The authority that can freeze a holder is not automatically the authority that can move that holder's tokens, so a single compromised key cannot both immobilise and seize.

Centrifuge's arrangement is the weakest of the three on confinement, because `authTransferFrom` is a general primitive rather than a named seizure function, and the strongest on residual checks in the paths that currently exist. That combination is exactly why a new caller of the primitive is the thing to look for in a diff.

**Q: Which model handles a token deployed on several chains?**

Centrifuge, because it was designed for it. Share tokens exist on every spoke chain, the same hook code runs on each, and the sentinel vocabulary already encodes the cross-chain legs: an outbound transfer targets `address(uint160(chainId))` and an inbound execution originates from the spoke contract, both of which the policies classify explicitly. The documentation notes the operational consequence, that `address(uint160(centrifugeId))` has to be whitelisted as a member on the source chain for cross-chain transfers to be permitted under `FullRestrictions`.

ERC-3643 does not address multi-chain deployment. An issuer wanting it has to replicate the registry and compliance state across chains and keep them consistent, which is a distributed systems problem the standard leaves open.

**Q: A team asks whether to use a Centrifuge-style hook or an ERC-3643 stack for a new tokenized fund. What decides it?**

Whether the rules are about individual holders or about the holder set as a whole.

Per-holder rules, meaning eligibility with an expiry plus freezing, are exactly what the hook model expresses, and it will be cheaper per transfer, simpler to audit, and easier to replace when the rules change. Aggregate rules, meaning caps on the number of holders, per-country limits, or maximum position sizes, need state that spans holders, which the shipped hooks have nowhere to keep.

Two secondary factors usually settle borderline cases. If holders should carry identity that other issuers also recognise, the ONCHAINID model provides a network effect a per-token memberlist cannot. If the token must exist on several chains, the hook model already has the vocabulary for it. A team that needs aggregate rules and picks the hook model will end up writing a custom hook that keeps aggregate state, at which point they have rebuilt a compliance module with a different interface, and should compare the two honestly before committing.

## References

### Related articles on this site

- [How Centrifuge Vaults Work: Asynchronous ERC-7540 Investment on a Hub-and-Spoke Protocol](https://rya-sge.github.io/access-denied/2026/08/18/centrifuge-vaults/)
- [Centrifuge Cross-Chain Messaging: Per-Pool Adapter Quorums, Batching and Failure Recovery](https://rya-sge.github.io/access-denied/2026/08/18/centrifuge-cross-chain-messaging/)
- [Double-Entry Bookkeeping On-Chain: How the Centrifuge Hub Keeps a Multi-Chain Pool's Books](https://rya-sge.github.io/access-denied/2026/08/18/centrifuge-onchain-accounting/)

### Standards

- [ERC-3643: T-REX, Token for Regulated EXchanges](https://eips.ethereum.org/EIPS/eip-3643)
- [ERC-1404: Simple Restricted Token Standard](https://github.com/ethereum/EIPs/issues/1404)
- [ERC-7943: uRWA, Universal Real World Asset interface](https://eips.ethereum.org/EIPS/eip-7943)
- [ERC-20: Token Standard](https://eips.ethereum.org/EIPS/eip-20)

### Implementations and documentation

- [CMTAT, the CMTA Token framework](https://github.com/CMTA/CMTAT)
- [Tokeny T-REX implementation](https://github.com/TokenySolutions/T-REX)
- [Centrifuge token compliance documentation](https://docs.centrifuge.io/developer/protocol/features/token-compliance/)
- [Centrifuge pool access levels](https://docs.centrifuge.io/developer/security/pool-access-levels)

### Analyzed source

- [centrifuge/protocol](https://github.com/centrifuge/protocol) — analyzed at commit [`a1aeae93c94e8a3dbe078f0fefbe9a1a340ffde1`](https://github.com/centrifuge/protocol/tree/a1aeae93c94e8a3dbe078f0fefbe9a1a340ffde1) (no release tag on this commit; it follows the `deploy-testnet-v3.2` tag), 2026-08-18
