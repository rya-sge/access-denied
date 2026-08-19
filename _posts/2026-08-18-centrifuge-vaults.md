---
layout: post
title: "How Centrifuge Vaults Work — Asynchronous ERC-7540 Investment on a Hub-and-Spoke Protocol"
date:   2026-08-18
last_modified_at: 2026-08-19
lang: en
locale: en-GB
categories: blockchain ethereum defi solidity
tags: blockchain ethereum solidity centrifuge erc-7540 erc-4626 erc-7575 rwa tokenized-vault
description: A technical walkthrough of Centrifuge V3 vaults - the ERC-7540 request lifecycle, the pool escrow reservation model, the pricing and rounding rules, and the transfer hook.
image: /assets/article/blockchain/defi/centrifuge/2026-08-18-centrifuge-vaults-mindmap.png
isMath: true
---

A Centrifuge vault looks like an [ERC-4626](https://eips.ethereum.org/EIPS/eip-4626) vault from the outside and behaves nothing like one on the inside. Calling `deposit()` on a Centrifuge async vault does not mint shares, and `previewDeposit()` reverts by design. The vault is a thin, standards-compliant facade over a request pipeline that spans two blockchains: the investor's assets sit in an escrow on the chain where the vault lives, while the decision to accept those assets, the price at which they are accepted, and the share issuance itself are all made on a different chain. This article follows the money through that pipeline, from `requestDeposit` to the moment shares land in an investor's wallet, and examines the accounting, pricing, and permissioning rules that hold the design together.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Where a vault sits in the protocol

Centrifuge V3 runs a hub-and-spoke topology. Each pool nominates exactly one **hub** chain, which owns the pool registry, the double-entry accounting ledger, the share prices, and the request approval logic. The pool then deploys onto any number of **spoke** chains, each of which acts as a separate balance sheet where share tokens are minted, held, and transferred, and where vaults accept deposits.

Vaults live on the spoke side. They never decide anything. A vault validates the caller, records that a request exists, moves tokens into the pool escrow, and emits an event. The actual investment decision travels to the hub as a cross-chain message, gets batched into an epoch alongside every other investor's request for the same asset, is approved by the pool manager at a price the manager supplies, and comes back as a callback that unlocks the investor's claim.

![Centrifuge V3 vault architecture]({{site.url_complet}}/assets/article/blockchain/defi/centrifuge/centrifuge-vault-architecture-concept.png)

In practice, **the vault contract holds no assets and computes no authoritative price**. Assets live in a per-pool escrow, and the price an investor actually receives is set on the hub after the request was made, not when it was made.

## The standards a Centrifuge vault implements

The vault surface is assembled from five interfaces, each contributing one capability.

- **[ERC-4626](https://eips.ethereum.org/EIPS/eip-4626)** supplies the vocabulary: `asset`, `share`, `totalAssets`, `convertToShares`, `convertToAssets`, `maxDeposit`, `maxMint`, `maxWithdraw`, `maxRedeem`. Centrifuge implements the read side faithfully and reimplements the write side.
- **[ERC-7540](https://eips.ethereum.org/EIPS/eip-7540)** adds the request phase: `requestDeposit`, `requestRedeem`, `pendingDepositRequest`, `claimableDepositRequest`, and the three-argument `deposit(assets, receiver, controller)` claim form. It also mandates that `previewDeposit`, `previewMint`, `previewWithdraw` and `previewRedeem` revert, because no honest preview is possible when the price is decided later.
- **[ERC-7575](https://eips.ethereum.org/EIPS/eip-7575)** separates the share token from the vault, which is what lets several vaults on the same share class each accept a different asset while all minting the same ERC-20 share.
- **[ERC-7887](https://eips.ethereum.org/EIPS/eip-7887)** adds cancellation, itself asynchronous: `cancelDepositRequest`, `pendingCancelDepositRequest`, `claimableCancelDepositRequest`, `claimCancelDepositRequest`, and the redeem-side equivalents.
- **[ERC-7741](https://eips.ethereum.org/EIPS/eip-7741)** adds EIP-712 signed operator authorisation, so a third party can be granted the right to act for a controller without that controller sending a transaction.

A sixth interface, ERC-7714 (`isPermissioned(address)`), is implemented but is still a draft that has not been merged into the ERCs repository, so it has no published page to link. Centrifuge answers it by forwarding to the share token's transfer restriction check.

All requests carry `REQUEST_ID = 0`. The code comments this as requests being non-fungible, and the practical effect is that a controller has at most one aggregate pending deposit and one aggregate pending redeem per vault. Successive `requestDeposit` calls accumulate into a single pending amount rather than creating distinguishable request objects.

## Contract structure

Three abstract contracts compose into two concrete vaults.

`BaseVault` carries everything common: the immutable `poolId`, `scId`, `asset` and `share` addresses, the operator mapping, the ERC-7741 domain separator and nonce tracking, `convertToShares` / `convertToAssets` delegation, and `_validateController`. It also exposes `setEndorsedOperator`, which lets an endorsed core contract (the router) register itself as operator for a user in a single call.

`BaseAsyncRedeemVault` extends it with the ERC-7540 redemption path and ERC-7887 redeem cancellation. `BaseSyncDepositVault` extends it instead with ERC-4626 synchronous deposit and mint.

From those:

- **`AsyncVault`** inherits `BaseAsyncRedeemVault` and adds asynchronous deposits. Both directions are request-based.
- **`SyncDepositVault`** inherits both `BaseSyncDepositVault` and `BaseAsyncRedeemVault`. Deposits settle in one transaction, redemptions go through the request pipeline.

Behind the vaults sit the managers, which hold all the state:

| Contract | Chain | Responsibility |
|----------|-------|----------------|
| `AsyncRequestManager` | spoke | Per-investor request state, escrow reservations, claim accounting |
| `SyncManager` | spoke | Synchronous issuance, per-asset deposit caps, optional valuation override |
| `BatchRequestManager` | hub | Epochs, approvals, issuance and revocation, per-investor claim splitting |
| `BalanceSheet` | spoke | The only contract allowed to mint, burn, and move escrow balances |
| `PoolEscrow` | spoke | Custody of assets and of not-yet-claimed shares, per pool |

## Asynchronous deposits: request, process, claim

The deposit path has three phases, separated by two cross-chain round trips.

![Asynchronous deposit lifecycle]({{site.url_complet}}/assets/article/blockchain/defi/centrifuge/centrifuge-async-deposit-workflow.png)

### Phase 1, the request

```solidity
function requestDeposit(uint256 assets, address controller, address owner) public returns (uint256) {
    require(owner == msg.sender || isOperator[owner][msg.sender], InvalidOwner());
    require(IERC20(asset).balanceOf(owner) >= assets, InsufficientBalance());

    require(asyncManager().requestDeposit(this, assets, controller, owner, msg.sender), RequestDepositFailed());
    SafeTransferLib.safeTransferFrom(asset, owner, address(baseManager.globalEscrow()), assets);

    emit DepositRequest(controller, owner, REQUEST_ID, msg.sender, assets);
    return REQUEST_ID;
}
```

Note the ordering: the manager is called first, the token transfer happens last. `globalEscrow()` is a legacy name kept for ABI compatibility with vaults deployed before v3.1.0; it resolves to the pool-specific `PoolEscrow` and reverts unless the caller is a linked vault.

Inside the manager, four things happen. The vault is checked to be linked to the registry. The investor is checked against the share token's transfer restriction, using `address(0)` as source, which is the sentinel for issuance. The pending amount is incremented, but only if no cancellation is already in flight. Finally a `DepositRequest` message is serialised and dispatched to the hub, and the assets are reserved in the escrow under the reason code `REASON_DEPOSIT`.

That last step matters. The reservation is recorded before the assets are noted as a holding, so a pool manager cannot treat freshly requested capital as available liquidity, and a cancellation can return it untouched.

### Phase 2, approval, issuance, notification

Everything in this phase is driven by the pool manager on the hub, and it is deliberately split into three separate calls so that price discovery and issuance need not happen in the same transaction.

**`approveDeposits`** takes an epoch number, an approved asset amount, and a `pricePoolPerAsset`. It enforces that the epoch is exactly the current one, that the approval does not exceed the pending total, and that it is non-zero. Approving less than the pending total is normal, and the leftover stays pending for a later epoch. The callback tells the spoke to unreserve the approved assets and note them as a deposit, which moves them from "sitting in the escrow contract" to "counted in the pool's holdings".

**`issueShares`** supplies `pricePoolPerShare` and computes how many shares the whole approved batch earns:

$$
\begin{aligned}
\text{shares} = \left\lfloor \frac{P_a \cdot 10^{d_s} \cdot A}{10^{d_a} \cdot P_s} \right\rfloor
\end{aligned}
$$

where $$A$$ is the approved asset amount, $$P_a$$ the pool price per asset unit, $$P_s$$ the pool price per share unit, and $$d_a$$, $$d_s$$ the asset and share decimals. Pool and share denomination are equal by design, which is why a single ratio of two pool-denominated prices converts between the two. On the spoke, the callback mints those shares to the pool escrow and immediately reserves them, so they are held on behalf of claimants rather than being available to the pool.

**`notifyDeposit`** walks an investor's unclaimed epochs, up to a caller-supplied `maxClaims`, and computes that investor's proportional slice of each approved batch. It returns a `FulfilledDepositRequest` callback that raises the investor's `maxMint` and updates a running weighted-average `depositPrice`.

The proportional split is where the rounding policy becomes visible:

$$
\begin{aligned}
\text{payment} = \left\lceil \frac{u \cdot A_{\text{approved}}}{A_{\text{pending}}} \right\rceil,
\qquad
\text{basis} = \left\lfloor \frac{u \cdot A_{\text{approved}}}{A_{\text{pending}}} \right\rfloor
\end{aligned}
$$

with $$u$$ the investor's pending amount. The investor's pending balance is reduced by the ceiling, while the share payout is computed from the floor. The asymmetry is intentional and documented in the source: it guarantees that the sum of individual pending amounts never exceeds the recorded total and that the sum of claimed shares never exceeds the shares issued. The cost is up to one wei of drift per claim, borne by the investor, in exchange for a bounded accounting invariant.

### Phase 3, the claim

Only now can the investor take possession. Both ERC-4626 entry points work, and they are not equivalent:

```solidity
// claim by asset amount: user receives floor(shares), maxMint is debited ceil(shares)
uint128 sharesUp   = _assetToShareAmount(vault_, assets_, state.depositPrice, MathLib.Rounding.Up);
uint128 sharesDown = _assetToShareAmount(vault_, assets_, state.depositPrice, MathLib.Rounding.Down);
shares = uint256(sharesDown);
_processDeposit(state, sharesUp, sharesDown, vault_, receiver);
```

`deposit(assets)` debits `maxMint` by the ceiling and pays out the floor, so repeated partial claims leak dust. `mint(shares)` passes the same share amount for both, so it does not. The NatSpec says so explicitly, and any integration that claims in a loop should use `mint`.

The claim itself unreserves the shares in the escrow and calls `balanceSheet.withdraw` in `TransferOnly` mode, which moves the shares without touching the escrow's holding accounting or queueing a message to the hub, because the hub already learned about the issuance in phase 2.

## Asynchronous redemptions

Redemption mirrors the deposit path with the roles of the two token types swapped.

![Asynchronous redemption lifecycle]({{site.url_complet}}/assets/article/blockchain/defi/centrifuge/centrifuge-async-redeem-workflow.png)

`requestRedeem` transfers the investor's shares into the pool escrow immediately and reserves them under `REASON_REDEEM`. The shares are gone from the investor's balance from that moment, which is why the vault documents that `withdraw` and `redeem` do not support a `controller` other than `msg.sender` in the usual delegated sense: the economic transfer already happened at request time.

On the hub, `approveRedeems` locks in an approved share amount and `revokeShares` supplies the share price. The `RevokedShares` callback does four things in one transaction: reserves the payout assets, unreserves the shares, calls `noteWithdraw` to queue the asset decrease, and burns the shares. The source comments the ordering explicitly, since queueing the asset decrease atomically with the burn is what prevents a window in which the hub's view of net asset value disagrees with the share supply.

`notifyRedeem` then raises the investor's `maxWithdraw` and records a weighted-average `redeemPrice`. The final claim, `withdraw` or `redeem`, unreserves the assets and transfers them out in `EscrowAndTransfer` mode, which updates escrow accounting but skips the hub queue because `noteWithdraw` already handled that.

## Cancellation is a request too

An investor cannot simply withdraw a pending request. `cancelDepositRequest` sets a `pendingCancelDepositRequest` flag and sends a message to the hub; the flag blocks any further request on that vault until it clears. The hub may not act on the cancellation immediately: if the investor's order is mid-epoch, the cancellation is queued rather than applied, and it takes effect when the investor next claims up to the latest epoch.

The hub tracks this with a `QueuedOrder` per investor holding an `amount` and an `isCancelling` flag. `_canMutatePending` decides which of the two paths a new request takes:

```solidity
function _canMutatePending(UserOrder memory userOrder, uint32 currentEpoch) internal pure returns (bool) {
    return currentEpoch <= 1 || userOrder.pending == 0 || userOrder.lastUpdate >= currentEpoch;
}
```

An investor with nothing pending, or whose last update is already at the current epoch, mutates the pending amount directly. Anyone else is queued, because their pending amount is entangled with an approval they have not yet claimed and cannot be edited without breaking the proportional split.

Once fulfilled, the cancelled amount becomes claimable through `claimCancelDepositRequest`, which returns the original assets rather than shares. The pool manager also has `forceCancelDepositRequest` and `forceCancelRedeemRequest`, gated by per-investor `allowForceDepositCancel` flags that must be set beforehand, for cases where an investor must be removed from a pool.

## Synchronous deposit vaults

`SyncDepositVault` collapses the deposit path into a single transaction. There is no request, no epoch, and no hub round trip for deposits; redemptions still go the asynchronous route.

```solidity
function deposit(uint256 assets, address receiver) external returns (uint256 shares) {
    shares = syncDepositManager.deposit(this, assets, receiver, msg.sender);
    // NOTE: For security reasons, transfer must stay at end of call despite the fact that it logically should
    // happen before depositing in the manager
    SafeTransferLib.safeTransferFrom(asset, msg.sender, address(baseManager.poolEscrow(poolId)), assets);
    emit Deposit(receiver, msg.sender, assets, shares);
}
```

The comment is worth reading twice. Accounting is updated before the token moves, so that a token with a transfer callback cannot re-enter the manager and observe a half-updated state.

Two mechanisms bound what synchronous deposits can do.

- **A per-asset reserve cap.** `maxDeposit` returns `maxReserve - availableBalance`, clamped at zero. Once the escrow's available balance for that asset reaches the configured ceiling, synchronous deposits stop until the pool manager deploys the capital. This is the pool's protection against being handed more instant liquidity than its strategy can absorb.
- **Price validity.** `SyncManager` reads prices with the validity check enabled, so a stale price beyond `maxSharePriceAge` or `maxAssetPriceAge` makes the call revert. The asynchronous manager reads with the check disabled, which is correct there because the price used for settlement is the one the hub supplies at fulfilment, not the one on the spoke at request time.

A pool may also install a custom `ISyncDepositValuation` per share class, in which case the synchronous price comes from that contract instead of the spoke's stored price.

## Custody: the pool escrow and its reserved balance

Every pool has one `PoolEscrow` on each spoke, and it tracks each holding as a pair:

```solidity
struct Holding {
    uint128 total;
    uint128 reserved;
}
```

`availableBalanceOf` returns `total - reserved`, and returns zero rather than reverting if the subtraction would underflow. Reservations are also attributed:

```solidity
mapping(ShareClassId => mapping(address reserver =>
    mapping(uint32 reason => mapping(address asset => mapping(uint256 tokenId => uint128))))) public reservedBy;
```

so a reservation can only be released by the same reserver under the same reason code. `REASON_DEPOSIT` and `REASON_REDEEM` keep the two flows from unwinding each other's earmarks.

The escrow holds both sides of the trade. Assets sit there from the moment a deposit is requested until they are either claimed back after cancellation or deployed by the pool manager. Newly issued shares sit there between issuance and claim. That single fact explains most of the reserve and unreserve pairs scattered through the request manager.

`BalanceSheet` is the only contract permitted to move any of it, and its `withdraw` has three modes that determine how much bookkeeping travels with the transfer:

| Mode | Escrow accounting | Hub queue | Used by |
|------|-------------------|-----------|---------|
| `TransferOnly` | no | no | Claiming shares, claiming a cancellation |
| `EscrowAndTransfer` | yes | no | Claiming redeemed assets after `noteWithdraw` |
| `Full` | yes | yes | Pool manager withdrawals, on/off-ramps |

## Pricing and rounding

Prices are `D18` values, 18-decimal fixed point, and there are two of them per share class and asset pair: `pricePoolPerAsset` and `pricePoolPerShare`. Every conversion in `PricingLib` funnels into one helper:

```solidity
function convertWithPrices(
    uint256 baseAmount, uint8 baseDecimals, uint8 quoteDecimals,
    D18 priceNumerator, D18 priceDenominator, MathLib.Rounding rounding
) internal pure returns (uint128 quoteAmount) {
    require(priceDenominator.isNotZero(), DivisionByZero());
    return MathLib.mulDiv(
        priceNumerator.raw(),
        10 ** quoteDecimals * baseAmount,
        10 ** baseDecimals * priceDenominator.raw(),
        rounding
    ).toUint128();
}
```

Multiplying before dividing, with the decimal scaling folded into the same `mulDiv`, keeps a single rounding step for the whole conversion. The library also offers `convertWithReciprocalPrice`, documented as more precise than multiplying by a pre-computed reciprocal, for the cases where only one price is available.

Amounts are `uint128` throughout the protocol, and the synchronous path guards the boundary explicitly: `_maxConvertibleAssets` computes the largest asset amount that still converts to a `uint128` share amount, and clamps `maxDeposit` to it rather than reverting on overflow deep inside a conversion.

The per-investor prices, `depositPrice` and `redeemPrice`, are running weighted averages recomputed on every fulfilment from cumulative amounts, not stored per epoch. An investor who is fulfilled across three epochs at three different prices ends up with a single blended rate, which is what makes the claim arithmetic tractable.

## Transfer restrictions and the hook sentinels

Share tokens are ERC-20 plus [ERC-1404](https://github.com/ethereum/EIPs/issues/1404), with an optional hook contract:

```solidity
function detectTransferRestriction(address from, address to, uint256 value) public view returns (uint8) {
    address hook_ = hook;
    if (hook_ == address(0)) return SUCCESS_CODE_ID;
    return ITransferHook(hook_).checkERC20Transfer(from, to, value, HookData(hookDataOf(from), hookDataOf(to)))
        ? SUCCESS_CODE_ID
        : ERROR_CODE_ID;
}
```

The protocol ships four hooks: `FullRestrictions` (memberlist plus freezing on both sides), `RedemptionRestrictions` (membership required only to redeem), `FreelyTransferable`, and `FreezeOnly`. A pool can install its own.

The hook has no separate callback per protocol operation. Each operation is instead encoded as a transfer between recognisable addresses, which the hook reads off the `from` and `to` arguments:

| Operation | `from` | `to` |
|-----------|--------|------|
| Deposit request / issuance | `address(0)` | investor |
| Deposit fulfilment | `address(0)` | pool escrow |
| Deposit claim | pool escrow | investor |
| Redeem request | investor | `ESCROW_HOOK_ID` |
| Redeem fulfilment | balance sheet | `address(0)` |
| Redeem claim | investor | `address(0)` |
| Cross-chain transfer out | investor | `address(uint160(chainId))` |

`ESCROW_HOOK_ID` is the constant `address(uint160(0x1CF60))`, chosen so it cannot collide with any `uint16` Centrifuge chain identifier. Using a fixed sentinel instead of the real escrow address saves the hook a lookup, since the escrow is per pool.

This is also why `maxDeposit` and `maxMint` return zero rather than reverting when the restriction check fails. A frozen investor sees an empty vault through the ERC-4626 view functions, which is the behaviour aggregators and front ends expect.

## Vault deployment and linking

Vaults are created by the hub, not by anyone on the spoke. A `updateVault` message carries a `VaultUpdateKind` of `DeployAndLink`, `Link`, or `Unlink`, and `VaultRegistry` executes it.

Deployment and linking are distinct steps. `deployVault` calls a factory, checks that an async vault has a request manager configured for its pool, and records `VaultDetails` with `isLinked = false`. `linkVault` then registers the vault in the `(poolId, scId, assetId, requestManager)` lookup, sets `isLinked = true`, and points the share token's per-asset vault pointer at it, which is the ERC-7575 `vault(asset)` accessor.

Unlinking reverses all of that. Since every state-changing entry point in `AsyncRequestManager` begins with `_checkIsLinked`, unlinking a vault is the protocol's kill switch for a single asset on a single share class: existing requests freeze, new ones revert, and the rest of the pool is unaffected.

## Access control

Two mechanisms guard the vault stack.

The **ward pattern** is the primary boundary. `Auth` exposes `wards[address] => uint256` and a modifier that reverts unless the caller's entry is `1`. All vault-to-manager and manager-to-balance-sheet calls are `auth`-gated, so a vault can only reach the manager it was wired to, and only `BalanceSheet` can mint or move escrow balances. Root holds the top of the hierarchy and, on live networks, is reachable only through a timelocked spell.

The **pool manager role** is separate. `BalanceSheet` and `BatchRequestManager` use an `isManager(poolId)` modifier resolved against the hub registry, so the entity that approves deposits for one pool has no authority over another.

Investor-facing functions are deliberately outside both. `requestDeposit`, `deposit`, `mint`, `requestRedeem`, `withdraw` and `redeem` carry no `auth` modifier; they are gated by `_validateController`, by the operator mapping, and by the transfer hook. Three delegation routes exist: direct `setOperator`, signature-based `authorizeOperator` under ERC-7741 with a `bytes32` nonce that can be pre-invalidated, and `setEndorsedOperator`, restricted to contracts that `Root` has endorsed. `VaultRouter` uses the third to enable itself for a user, and wraps its own entry points in a reentrancy lock that also survives multicall by pinning the initiator address.

## Conclusion

The Centrifuge vault is an adapter. It presents the ERC-4626 and ERC-7540 surface that DeFi integrations expect, and forwards every decision to a request pipeline whose authority lives on another chain. The design constraints follow from that split: prices arrive with the fulfilment rather than being read at request time, requests are aggregated into epochs so a manager approves a batch instead of individual orders, and the pool escrow tracks a reserved amount alongside a total so that capital which is pending, issued, or being redeemed cannot be spent as though it were free.

The parts most worth attention when integrating or reviewing are the rounding policy in the claim path, where the ceiling and floor asymmetry protects a protocol invariant at the investor's expense, and the reservation reason codes, which are the mechanism keeping the deposit and redemption flows from unwinding each other's earmarks.

![Centrifuge V3 vaults mindmap]({{site.url_complet}}/assets/article/blockchain/defi/centrifuge/2026-08-18-centrifuge-vaults-mindmap.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Hub** | The single chain a pool nominates to hold its registry, accounting ledger, prices, and request approval logic. |
| **Spoke** | A chain where a pool issues share tokens and deploys vaults; a pool may have many, each acting as a separate balance sheet. |
| **Share class** | A subdivision of a pool with its own share token, price, and restriction hook, identified by a `ShareClassId`. |
| **Pool escrow** | The per-pool contract on a spoke that custodies both deposited assets and issued-but-unclaimed shares, tracking `total` and `reserved` per holding. |
| **Reservation** | An earmark on an escrow holding, attributed to a reserver and a reason code, that removes the amount from the pool's available balance without moving it. |
| **Epoch** | The unit of batching on the hub; an approval, an issuance, and the resulting claims all reference one epoch number for a given share class and asset. |
| **Controller** | The address that owns a pending request and is entitled to claim it, which may differ from the address that funded it or the one that receives the output. |
| **Operator** | An address authorised to act on a controller's behalf, set directly, by EIP-712 signature under ERC-7741, or by endorsement of a core protocol contract. |
| **D18** | The protocol's 18-decimal fixed-point price type; prices are expressed as pool units per asset unit or pool units per share unit. |
| **Transfer hook** | The contract a share token consults on every transfer, which infers the protocol operation from the sentinel addresses involved and permits or blocks accordingly. |

## Annex — Invariants

The properties below are what the deposit and redemption machinery is built to preserve. They are stated as
invariants rather than as advice, since each one is enforced by a specific mechanism in the code and each is a
candidate property for an invariant-testing campaign.

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| The sum of investors' pending amounts never exceeds the pool-level pending total. | Ceiling rounding when reducing `userOrder.pending` in `_claimDeposit`. | The reduction is switched to floor, letting rounding dust accumulate into an over-claim. |
| The sum of shares claimed for an epoch never exceeds the shares issued for it. | Floor rounding on the payment basis used to compute the share payout. | The payout basis is rounded up, so the last claimant of an epoch finds the escrow short. |
| An escrow's available balance equals `total - reserved` and is never negative. | `availableBalanceOf` returns zero when reserved exceeds total, and `withdraw` requires `total >= reserved`. | An unguarded subtraction underflows and reports a large available balance to pool managers. |
| A reservation is released only by the reserver that created it, under the same reason code. | The `reservedBy[scId][caller][reason][asset][tokenId]` mapping and the `InsufficientReserve` check. | The deposit flow can release the redemption flow's earmark, freeing assets owed to redeemers. |
| Shares issued against a fulfilled deposit remain in the pool escrow, reserved, until claimed. | `issue()` mints to `balanceSheet.escrow(poolId)` and is immediately followed by a `reserve` of the same amount. | Issued shares count as pool liquidity and can be deployed before their owners claim them. |
| A controller has at most one pending deposit and one pending redeem per vault. | `REQUEST_ID` fixed at 0 and single `uint128` pending fields per `(vault, controller)`. | Requests become individually addressable and the aggregate accounting no longer describes them. |
| No new request is accepted while a cancellation for the same controller is in flight. | The `pendingCancelDepositRequest` and `pendingCancelRedeemRequest` flags and the `CancellationIsPending` check. | Hub and spoke disagree about the pending amount, and the proportional split is computed against the wrong total. |
| A claim never delivers more shares than it debits from `maxMint`. | `sharesUp` is rounded up and debited while `sharesDown` is rounded down and paid out. | Repeated partial claims extract more than the allocation, at the expense of other claimants in the same escrow. |
| Only a vault currently linked in the registry can move pool capital. | `_checkIsLinked` at the head of every state-changing entry point in `AsyncRequestManager`. | An unlinked or superseded vault keeps operating after its kill switch was pulled. |

## Annex — Integration Notes

The behaviours below follow from the asynchronous design and differ from what an ERC-4626 integration usually
assumes. Each is intentional and documented in the contracts.

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| `previewDeposit`, `previewMint`, `previewWithdraw` and `previewRedeem` revert. | Treat them as unavailable on async vaults, as ERC-7540 requires. Quote with `convertToShares` and `convertToAssets` instead, and label the result as indicative. |
| `convertToShares` and `convertToAssets` use the spoke's most recent price, which the contracts note may change between submission and execution. | Never present the result as the price the user will receive. The settlement price is the one the hub supplies at fulfilment. |
| Claiming by asset amount loses up to one wei of allocation per call. | Claim with `mint(shares, ...)` and `withdraw(assets, ...)` rather than `deposit` and `redeem`, especially in loops. The NatSpec recommends this explicitly. |
| `maxDeposit`, `maxMint`, `maxWithdraw` and `maxRedeem` return zero when the transfer restriction blocks the user. | Do not read zero as "vault is empty" or as an error. A restricted or frozen investor sees an empty vault through the standard views. |
| Every request carries `REQUEST_ID = 0`, and repeat requests accumulate into one pending amount. | Do not build a per-request identifier model. Track one aggregate pending deposit and one aggregate pending redeem per controller and vault. |
| A pending cancellation blocks further requests on that vault until it clears. | Surface cancellation state in the interface, and expect `CancellationIsPending` rather than treating a failed request as a transient error. |
| On `requestRedeem` the shares leave the holder's balance immediately. | Reflect the reduced balance right away. Note that `withdraw` and `redeem` do not support the usual controller-different-from-caller delegation, because there is no remaining share balance to authorise against. |
| Delegation has three routes: `setOperator`, an ERC-7741 signature through `authorizeOperator`, and `setEndorsedOperator` for endorsed protocol contracts. | Use `VaultRouter.enable()` for the common case; it registers the router as an endorsed operator in one call. |
| `totalAssets()` is `convertToAssets(totalSupply)` of the share class, not a balance held by the vault. | Do not expect the vault address to hold assets. Custody is the pool escrow. |
| `pricePerShare()` and `priceLastUpdated()` exist outside the standards. | Use them for display, and check `priceLastUpdated` before showing a price as current. |


## Frequently Asked Questions

**Q: Why does `previewDeposit` revert on a Centrifuge async vault?**

Because there is no answer it could return that would be true. The number of shares a deposit earns depends on `pricePoolPerShare`, which the pool manager supplies on the hub when the epoch containing that request is issued, potentially days after the request was made. ERC-7540 makes this explicit and requires the four preview functions to revert on asynchronous flows rather than return a figure that integrations would treat as a quote.

**Q: What is actually stored on a per-investor basis, and where?**

Two contracts hold complementary halves of the state:

- On the spoke, `AsyncRequestManager` keeps an `AsyncInvestmentState` per `(vault, investor)`: `pendingDepositRequest`, `pendingRedeemRequest`, the two cancellation flags, the two claimable-cancellation amounts, `maxMint`, `maxWithdraw`, and the weighted-average `depositPrice` and `redeemPrice`.
- On the hub, `BatchRequestManager` keeps a `UserOrder` per `(pool, share class, asset, investor)` holding a pending amount and the epoch of its last update, plus a `QueuedOrder` for requests that arrived mid-epoch.

The spoke half is what the ERC-7540 view functions read. The hub half is what the approval and claim-splitting arithmetic operates on.

**Q: An investor requests a deposit and the pool manager approves only part of it. What happens to the rest?**

It stays pending. `approveDeposits` requires the approved amount to be at most the pending total and subtracts it, leaving the remainder in `pendingDeposit` for a later epoch. The investor's own `UserOrder.pending` is reduced only when they claim, by their proportional share of what was approved, so their view of the remainder stays consistent with the pool-level figure.

**Q: Why is `requestRedeem` allowed to move shares immediately, while `requestDeposit` also moves assets immediately, yet only the deposit can be fully returned by cancelling?**

Both move tokens into the pool escrow at request time, and both can be cancelled with the original tokens returned: `claimCancelDepositRequest` returns assets and `claimCancelRedeemRequest` returns shares. The asymmetry is in what the vault can promise about delegation afterwards. Because the shares have already left the investor's balance on `requestRedeem`, the vault documents that its `withdraw` and `redeem` do not support the usual controller-different-from-caller pattern, since there is no remaining share balance to authorise against.

**Q: A synchronous deposit vault stops accepting deposits although the pool is healthy. What are the two things to check?**

First, the per-asset reserve cap. `maxDeposit` returns `maxReserve - availableBalance` clamped at zero, so once the escrow's available balance for that asset reaches the configured ceiling, deposits return zero until the pool manager deploys the capital or raises the cap.

Second, price staleness. `SyncManager` reads both `pricePoolPerShare` and `pricePoolPerAsset` with the validity check enabled, so a price older than `maxSharePriceAge` or `maxAssetPriceAge` makes the call revert. The asynchronous vault on the same share class would keep working, because it reads with the check disabled and settles at the price the hub supplies at fulfilment.

**Q: How would a reviewer confirm that a custom transfer hook cannot be bypassed by the protocol's own operations?**

Enumerate the sentinel pairs and check each one. The hook infers the operation from the `from` and `to` addresses: issuance is `address(0)` to the investor, deposit fulfilment is `address(0)` to the pool escrow, the deposit claim is escrow to investor, a redeem request is investor to `ESCROW_HOOK_ID`, redemption fulfilment is the balance sheet to `address(0)`, and a cross-chain transfer targets `address(uint160(chainId))`. A hook that only implements a memberlist check on ordinary transfers and treats every sentinel case as automatically permitted has effectively opened a path from the escrow to any address the protocol will pay out to. The corresponding positive check is that `checkTransferRestriction` is consulted on both legs of every movement, including the internal ones, which is what `AsyncRequestManager._canTransfer` is doing at each request and claim boundary.

## References

### Standards

- [ERC-4626: Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-4626)
- [ERC-7540: Asynchronous ERC-4626 Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-7540)
- [ERC-7575: Multi-Asset ERC-4626 Vaults](https://eips.ethereum.org/EIPS/eip-7575)
- [ERC-7741: Authorize Operator](https://eips.ethereum.org/EIPS/eip-7741)
- [ERC-7887: Cancelation for ERC-7540 Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-7887)
- [ERC-1404: Simple Restricted Token Standard](https://github.com/ethereum/EIPs/issues/1404)

### Protocol documentation

- [Centrifuge developer documentation](https://docs.centrifuge.io/)
- [Vaults architecture](https://docs.centrifuge.io/developer/protocol/architecture/vaults/)
- [Standards-based composability](https://docs.centrifuge.io/developer/protocol/features/vaults/)
- [Security reviews and audit reports](https://docs.centrifuge.io/developer/security/audits)

### Analyzed source

- [centrifuge/protocol](https://github.com/centrifuge/protocol) — analyzed at commit [`a1aeae93c94e8a3dbe078f0fefbe9a1a340ffde1`](https://github.com/centrifuge/protocol/tree/a1aeae93c94e8a3dbe078f0fefbe9a1a340ffde1) (no release tag on this commit; it follows the `deploy-testnet-v3.2` tag), 2026-08-18
- [centrifuge/documentation](https://github.com/centrifuge/documentation) — analyzed at commit [`8cf0194170e0cfdadd88f82cd9f2946a7cccdb4d`](https://github.com/centrifuge/documentation/tree/8cf0194170e0cfdadd88f82cd9f2946a7cccdb4d), 2026-08-18
