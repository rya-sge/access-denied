---
layout: post
title: "Double-Entry Bookkeeping On-Chain — How the Centrifuge Hub Keeps a Multi-Chain Pool's Books"
date:   2026-08-18
last_modified_at: 2026-08-19
lang: en
locale: en-GB
categories: blockchain ethereum defi solidity finance
tags: centrifuge accounting double-entry nav rwa tokenization hub-spoke bookkeeping valuation
series: centrifuge
description: How Centrifuge implements real double-entry accounting in Solidity - debit-normal accounts, balanced journals, cross-chain snapshots, and the NAV and share price derived from them.
image: /assets/article/blockchain/defi/centrifuge/2026-08-18-centrifuge-onchain-accounting-mindmap.png
isMath: true
---

`Accounting.sol` in the Centrifuge protocol is 157 lines of Solidity that implement a general ledger: accounts with a debit and a credit total, a declared normal balance, journal entries grouped by identifier, and a transaction scope that reverts unless debits equal credits. Sitting above it, `Holdings` records what a pool owns and what those holdings are worth, and a manager contract derives net asset value and a price per share from account balances rather than from a stored figure. The interesting problem is not the bookkeeping itself, which is old, but that the pool's assets sit on several chains at once while the books live on one. This article walks through the ledger, the posting rules, and the synchronisation mechanism that decides when the books are consistent enough to price a share.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The ledger

An account is four numbers and a flag:

```solidity
struct Account {
    uint128 totalDebit;
    uint128 totalCredit;
    bool isDebitNormal;
    uint64 lastUpdated;
    bytes metadata;
}
```

Running totals are kept rather than a net balance, which is how paper ledgers work and which keeps `addDebit` and `addCredit` monotonic. The balance is derived, and the derivation depends on the account's declared nature:

$$
\begin{aligned}
V = \begin{cases}
D - C & \text{if the account is debit-normal} \\
C - D & \text{otherwise}
\end{cases}
\end{aligned}
$$

where $$D$$ and $$C$$ are the running debit and credit totals. Because both are unsigned, `accountValue` returns a sign flag alongside the magnitude rather than a signed integer, and callers have to handle a negative asset account explicitly. `NAVManager` does exactly that, and the code comments on which accounts are expected to be negative.

`lastUpdated` doubles as an existence marker: a zero value means the account was never created, which is what `AccountDoesNotExist` checks. It costs nothing extra, since a created account always has a non-zero timestamp.

Account identifiers are derived, not assigned. `AccountId` is a `uint256` composed from either an asset identifier or a chain identifier, plus a 16-bit index:

```solidity
function withCentrifugeId(uint16 centrifugeId, uint16 index) pure returns (AccountId) {
    return AccountId.wrap((uint256(centrifugeId) << 16) | uint256(index));
}

function withAssetId(AssetId assetId, uint16 index) pure returns (AccountId) {
    return AccountId.wrap((uint256(assetId.raw()) << 16) | uint256(index));
}
```

`NAVManager` uses the account type as the index, so the asset account for a given asset, or the equity account for a given chain, can be computed by any caller without a lookup table. Asset and expense accounts are per asset; equity, liability, gain and loss accounts are per chain.

## Transaction scoping

Entries can only be added while a pool is unlocked, and the unlock is scoped to a single pool:

```solidity
function unlock(PoolId poolId) external auth {
    require(PoolId.unwrap(_currentPoolId) == 0, AccountingAlreadyUnlocked());
    debited = 0;
    credited = 0;
    _currentPoolId = poolId;
    ...
}

function lock() external auth {
    require(debited == credited, Unbalanced());
    ...
}
```

`debited`, `credited` and `_currentPoolId` are all transient storage. The fundamental invariant of double-entry bookkeeping is enforced at `lock`: a sequence that debits without a matching credit reverts, taking the whole transaction with it. Since `addDebit` and `addCredit` read the pool from transient state rather than from an argument, no caller can post an entry to the wrong pool while another pool's journal is open.

Journal identifiers get their own treatment, explained in a comment on the helper library:

> In a transaction there can be multiple journal entries for different pools, which can be interleaved. We want entries for the same pool to share the same journal ID. So we're keeping a journal ID per pool in transient storage.

```solidity
function _generateJournalId(PoolId poolId) internal returns (uint256) {
    return uint256((uint256(poolId.raw()) << 128) | ++_poolJournalIdCounter[poolId]);
}
```

A multicall that touches three pools produces three journal identifiers, each stable across every unlock and lock pair for that pool within the transaction. An off-chain indexer reconstructing the ledger from `Debit` and `Credit` events can therefore group entries into journals correctly even when the on-chain calls were interleaved, and the identifier itself carries the pool in its high bits.

## The chart of accounts

Six account types exist, and a holding is wired to either four of them or two:

```solidity
enum AccountType {
    Asset, Equity, Loss, Gain, Expense, Liability
}
```

![Holding to account wiring]({{site.url_complet}}/assets/article/blockchain/defi/centrifuge/centrifuge-chart-of-accounts-concept.png)

An ordinary holding gets an asset, equity, gain and loss account. A holding flagged as a liability gets an expense and a liability account instead, and the two sets are created through different entry points, `initializeHolding` and `initializeLiability`. `NAVManager.initializeNetwork` creates the per-chain accounts once with the right normal balances:

```solidity
hub.createAccount(poolId, equityAccount(centrifugeId), false);
hub.createAccount(poolId, liabilityAccount(centrifugeId), false);
hub.createAccount(poolId, gainAccount(centrifugeId), false);
hub.createAccount(poolId, lossAccount(centrifugeId), true);
```

Equity, liability and gain are credit-normal; loss is debit-normal, as is the asset account created later per asset. That matches standard practice, and it is the reason `accountValue` can return a plain magnitude for each of them and still be combined correctly.

Initialisation is not required before value arrives. Both `initializeHolding` and `initializeLiability` end with a catch-up posting:

```solidity
// If increase/decrease was called before initialize, we add journal entries for this
_updateAccountingAmount(poolId, scId, assetId, true, holdings.value(poolId, scId, assetId));
```

so a pool that received deposits before its chart of accounts existed does not end up with holdings the ledger never saw.

## The two posting rules

Every entry the protocol makes automatically comes from one of two functions, and the distinction between them is the classic one between a change in quantity and a change in price.

**`updateAccountingAmount`** handles assets entering or leaving. The account pair depends on whether the holding is a liability, and the direction flips on a decrease:

```solidity
bool isLiability = holdings.isLiability(poolId, scId, assetId);
AccountType debitAccountType = isLiability ? AccountType.Expense : AccountType.Asset;
AccountType creditAccountType = isLiability ? AccountType.Liability : AccountType.Equity;

if (isPositive) {
    accounting.addDebit(holdings.accountId(poolId, scId, assetId, uint8(debitAccountType)), diff);
    accounting.addCredit(holdings.accountId(poolId, scId, assetId, uint8(creditAccountType)), diff);
} else {
    accounting.addDebit(holdings.accountId(poolId, scId, assetId, uint8(creditAccountType)), diff);
    accounting.addCredit(holdings.accountId(poolId, scId, assetId, uint8(debitAccountType)), diff);
}
```

**`updateAccountingValue`** handles revaluation, where the quantity is unchanged but the valuation moved. Here gains and losses get their own accounts rather than being netted into equity immediately.

The full posting map:

| Event | Holding kind | Debit | Credit |
|-------|--------------|-------|--------|
| Assets received | Asset | Asset | Equity |
| Assets withdrawn | Asset | Equity | Asset |
| Liability incurred | Liability | Expense | Liability |
| Liability settled | Liability | Liability | Expense |
| Revaluation up | Asset | Asset | Gain |
| Revaluation down | Asset | Loss | Asset |
| Revaluation up | Liability | Expense | Liability |
| Revaluation down | Liability | Liability | Expense |

Both functions return early when the difference is zero, so a revaluation that moves nothing costs no gas beyond the read.

Keeping gain and loss separate from equity is a deliberate reporting choice: it preserves the period's performance as its own figure. `NAVManager.closeGainLoss` folds them back when a manager decides the period is over, in one balanced journal:

```solidity
if (gainValue > 0) {
    debits[index] = JournalEntry({value: gainValue, accountId: gainAccount_});
    credits[index] = JournalEntry({value: gainValue, accountId: equityAccount_});
    index++;
}

if (lossValue > 0) {
    debits[index] = JournalEntry({value: lossValue, accountId: equityAccount_});
    credits[index] = JournalEntry({value: lossValue, accountId: lossAccount_});
}
```

Debiting the gain account and crediting equity zeroes the first and raises the second, since gain is credit-normal and equity is too. The loss leg mirrors it.

## Where the numbers come from

`Holdings` stores, per pool, share class and asset, both a quantity and its value in pool units:

```solidity
struct Holding {
    uint128 assetAmount;
    uint128 assetAmountValue;
    IValuation valuation; // Used for existence
    bool isLiability;
}
```

`increase` and `decrease` convert an asset amount into pool units at a supplied price and adjust both fields. `update` is the revaluation path: it asks the holding's valuation contract to quote the current amount, and returns the signed difference against the stored value, which the Hub then posts.

Two details are worth pausing on.

The first is that `decrease` clamps rather than reverting:

```solidity
// Clamp amount and value to 0 to prevent underflow
// The unclamped amount and value are emitted in the event, as well as returned to the caller
holding_.assetAmount = amount_ > holding_.assetAmount ? 0 : holding_.assetAmount - amount_;
```

The unclamped figure is what gets returned and posted to the ledger, while the stored holding floors at zero. That combination keeps a withdrawal from bricking on an arithmetic underflow when prices moved between the increase and the decrease, at the cost of allowing the ledger and the holding record to disagree in exactly that edge case. The event carries the unclamped number so the discrepancy is observable off-chain.

The second is the constraint on reclassification:

```solidity
require(holding_.assetAmount == 0 && holding_.assetAmountValue == 0, HoldingNotZero());
```

A holding cannot be switched between asset and liability while it still carries value, because its postings would then move between two account pairs and the ledger would carry a permanent imbalance. The NatSpec spells out the operational consequence: a manager has to call `update` first to bring the value to zero.

Valuation is pluggable per holding. `IdentityValuation` quotes one-to-one for stablecoin-style assets, `OracleValuation` reads a fed price, and a pool can install its own contract. The ledger does not care which, since it only ever sees the difference the valuation reports.

## The multi-chain problem

An asset deposit happens on a spoke chain. The ledger lives on the hub. Between the two sits a queue, and the queue is what makes the accounting tractable.

`BalanceSheet` on each spoke accumulates deltas rather than sending a message per operation:

```solidity
struct ShareQueueAmount {
    uint128 delta;
    bool isPositive;
    uint32 queuedAssetCounter;
    uint64 nonce;
}

struct AssetQueueAmount {
    uint128 deposits;
    uint128 withdrawals;
}
```

When a manager submits a queue, the message carries a net amount, a direction, a nonce, and a flag that is the heart of the design:

```solidity
ISpokeMessageSender.UpdateData memory data = ISpokeMessageSender.UpdateData({
    netAmount: (assetQueue.deposits >= assetQueue.withdrawals)
        ? assetQueue.deposits - assetQueue.withdrawals
        : assetQueue.withdrawals - assetQueue.deposits,
    isIncrease: assetQueue.deposits > assetQueue.withdrawals,
    isSnapshot: shareQueue.delta == 0 && shareQueue.queuedAssetCounter == assetCounter,
    nonce: shareQueue.nonce
});
```

`isSnapshot` is true only when submitting this queue leaves nothing else outstanding for that share class on that chain: no pending share delta, and no other asset queue waiting. It is the spoke telling the hub that its assets and its share issuance are now consistent with each other.

On the hub, `Holdings.setSnapshot` enforces ordering and fires the hook:

```solidity
Snapshot storage snapshot_ = snapshot[poolId][scId][centrifugeId];
require(snapshot_.nonce == nonce, InvalidNonce(snapshot_.nonce, nonce));

snapshot_.isSnapshot = isSnapshot;
snapshot_.nonce++;
...
_callOnSync(poolId, scId, centrifugeId, snapshot_);
```

with the hook call gated:

```solidity
function _callOnSync(PoolId poolId, ShareClassId scId, uint16 centrifugeId, Snapshot memory snapshot_) internal {
    if (!snapshot_.isSnapshot) return;
    ...
}
```

The nonce is per pool, share class and chain, and messages that arrive out of order revert rather than being applied. Combined with the retry mechanism in the messaging layer, that turns an unordered transport into an ordered stream per share class and chain.

![From a spoke balance change to a new share price]({{site.url_complet}}/assets/article/blockchain/defi/centrifuge/centrifuge-snapshot-nav-workflow.png)

The reason the flag matters is that a share price is a ratio of two quantities that live in different places. Assets are reported by the spoke's balance sheet; issuance is tracked by the hub's `ShareClassManager`. If the hub priced a share the moment an asset message arrived, it would divide new assets by an issuance figure that had not yet caught up, and the price would spike or collapse for as long as the mismatch lasted. The snapshot flag delays the calculation until both halves describe the same moment.

## Net asset value

`NAVManager` computes NAV per chain from four account balances:

$$
\begin{aligned}
\text{NAV} = V_{\text{equity}} + V_{\text{gain}} - V_{\text{loss}} - V_{\text{liability}}
\end{aligned}
$$

The implementation is more careful than the formula, because each term arrives as a magnitude plus a sign, and any of them can be negative:

```solidity
// Equity: normally positive, if negative flip to negative side
if (equityIsPositive) totalPositive += equity;
else totalNegative += equity;
...
if (totalNegative >= totalPositive) return 0;

return totalPositive - totalNegative;
```

Each account is sorted into a positive or negative bucket according to its actual sign rather than its expected one, the buckets are summed, and the result floors at zero. A pool whose liabilities exceed its assets reports a NAV of zero rather than reverting or underflowing, which keeps the share price defined at the point where it stops being meaningful.

Note that this is per chain. The figure passed to the NAV hook describes one chain's balance sheet, and it is the hook's job to aggregate.

## From NAV to a share price

`SimplePriceManager` is the reference hook for single-share-class pools. It keeps a global figure and a per-chain figure, and updates the global one by difference:

```solidity
metrics_.netAssetValue = metrics_.netAssetValue + netAssetValue - networkMetrics_.netAssetValue;
```

Issuance needs more care, because shares can move between chains without being created or destroyed. A cross-chain transfer burns on one spoke and mints on another, and `ShareClassManager` records both legs immediately, while `SimplePriceManager` learns about them through a separate `onTransfer` callback. Counting the difference naively would double count. The correction is explicit:

```solidity
// transferredIn was already added to SCM, so needs to be subtracted
// transferredOut was already removed from SCM, so needs to be added back
uint128 adjustedNew = newIssuance + transferredOut;
uint128 adjustedOld = oldIssuance + transferredIn;
```

Reordering the arithmetic into two sums that are then compared, rather than adding and subtracting in place, also avoids an intermediate underflow on `uint128`.

The price itself is then the obvious ratio, with a defined value for an empty pool:

$$
\begin{aligned}
P = \begin{cases}
1 & \text{if issuance is } 0 \\
\dfrac{\text{NAV}}{\text{issuance}} & \text{otherwise}
\end{cases}
\end{aligned}
$$

```solidity
return metrics_.issuance == 0 ? d18(1, 1) : d18(metrics_.netAssetValue) / d18(metrics_.issuance);
```

The result goes to `hub.updateSharePrice`, which stores it and, if a fee hook is installed, accrues fees at the same time. From there it is pushed to spokes through `notifySharePrice`, and it becomes the number the vaults use.

## What a reviewer should look at

The ledger enforces its own core invariant, so the interesting questions are at the edges where it meets the rest of the protocol.

- **Whether every mutation of a holding has a corresponding posting.** `HubHandler.updateHoldingAmount` calls `hub.updateAccountingAmount` only when the holding is initialised, so holdings that receive value before their accounts exist rely on the catch-up posting in `initializeHolding` firing exactly once.
- **The clamping in `decrease`.** The posted value is unclamped while the stored value floors at zero, which is the one place the two records can legitimately diverge.
- **Who can supply a valuation.** `updateHoldingValuation` is manager-gated, and a valuation contract that returns an inflated quote moves NAV and therefore the share price directly, with no bound in the accounting layer.
- **Snapshot liveness rather than safety.** The nonce check makes out-of-order application impossible, but a share class whose queue never reaches a quiet moment never sets `isSnapshot`, and the price simply stops updating. That is the safe failure direction, and it is also a silent one.
- **The per-chain nature of NAV.** `NAVManager` documents that it assumes all assets in a pool are shared across share classes rather than segregated. A pool that needs segregation needs a different hook.

## Conclusion

The Centrifuge hub keeps a general ledger rather than a set of balances. Accounts declare a normal balance and carry running debit and credit totals, entries are made inside a pool-scoped transaction that reverts unless it balances, and journal identifiers are held in transient storage so interleaved calls across pools still group correctly for anyone reading the events. Net asset value and price per share are computed from account balances at the point they are needed, not stored and updated in place.

The part that is specific to a multi-chain protocol is the snapshot flag. A spoke reports not only its net asset movement but whether that movement leaves its assets and its share issuance mutually consistent, and the hub recalculates the price only on the reports where it does. The nonce alongside it makes the stream ordered per share class and chain. Together they reduce a distributed accounting problem to one the ledger can treat as a sequence of balanced journals.

![Centrifuge onchain accounting mindmap]({{site.url_complet}}/assets/article/blockchain/defi/centrifuge/2026-08-18-centrifuge-onchain-accounting-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Debit-normal account** | An account whose value is its debit total minus its credit total, used for assets, losses and expenses. |
| **Credit-normal account** | An account whose value is its credit total minus its debit total, used for equity, gains and liabilities. |
| **Journal** | A group of debit and credit entries sharing one identifier, generated per pool and held in transient storage for the duration of a transaction. |
| **Unlock and lock** | The scope within which entries may be posted to one pool; locking reverts unless the debited and credited totals are equal. |
| **Holding** | A per pool, share class and asset record of a quantity, its value in pool units, its valuation contract, and whether it is a liability. |
| **Valuation** | A pluggable contract that quotes the current pool-unit value of a holding's quantity, used to compute revaluation differences. |
| **Liability holding** | A holding whose postings use the expense and liability accounts instead of asset and equity, and which cannot be reclassified while it carries value. |
| **Snapshot** | A spoke's assertion that its asset movements and share issuance for a share class are mutually consistent at that moment, carried as a flag on the queue submission. |
| **Snapshot nonce** | A per pool, share class and chain counter that must match on arrival, making the stream of balance-sheet updates ordered. |
| **Net asset value** | Equity plus gains minus losses and liabilities, computed per chain from account balances and floored at zero. |

## Frequently Asked Questions

**Q: Why store both a debit total and a credit total instead of one net balance?**

Because a net balance loses information that both the audit trail and the sign convention need. Running totals make each posting an increment that never has to consider the account's current side, they let `accountValue` derive a balance according to the account's declared nature at read time, and they preserve gross activity, so an account that saw a million in and a million out is distinguishable from one that saw nothing. It also matches how the paper practice works, which matters when the on-chain books are meant to be reconcilable with off-chain ones.

**Q: What exactly does the `isSnapshot` flag assert, and what happens when it is false?**

It asserts that after this queue submission, nothing else is outstanding for that share class on that chain: the queued share delta is zero and no other asset queue is pending. In other words, the assets the spoke has reported and the share issuance the hub has recorded now describe the same moment.

When it is false, the update is still applied in full. Holdings move, the journal is posted, the nonce advances. Only the hook call is skipped, so net asset value is not recomputed and the share price is not updated. The books stay correct; the derived figures simply wait.

**Q: A pool's liabilities exceed its assets. What does the protocol report?**

Zero. `netAssetValue` sorts each of the four account balances into a positive or negative bucket by its actual sign, sums both, and returns zero when the negative bucket is the larger:

```solidity
if (totalNegative >= totalPositive) return 0;
return totalPositive - totalNegative;
```

The price manager then divides zero by the issuance, producing a share price of zero rather than a wrapped or reverting value. The ledger itself still holds the real figures, so the shortfall remains readable from the individual accounts.

**Q: Why do gains and losses get their own accounts instead of adjusting equity directly?**

To preserve performance as a separate, readable figure. Posting a revaluation straight to equity would make the balance correct but would erase the distinction between capital contributed and value earned, which is the distinction a report is usually about.

`closeGainLoss` folds them into equity when a manager decides a period has ended, in a single balanced journal that debits the gain account against equity and credits the loss account from equity. It is an explicit manager action rather than something the protocol does on a schedule.

**Q: Shares move from one chain to another. Why does that need special handling in the price manager?**

Because two contracts learn about the transfer through different paths and would otherwise both count it. `ShareClassManager` updates the per-chain issuance for both legs as soon as the transfer is processed, while `SimplePriceManager` tracks it separately as `transferredIn` and `transferredOut` through an `onTransfer` callback.

When the next snapshot arrives, the manager compares its own stale issuance against the fresh figure. Without adjustment, the transfer would appear as an issuance on the receiving chain and a revocation on the sending one, changing global issuance even though no share was created or destroyed. The correction adds `transferredOut` to the new figure and `transferredIn` to the old, which nets the transfer out and, by summing before subtracting, avoids an underflow.

**Q: If the accounting is enforced to balance, where can value still be lost, and what would you inspect first?**

The balance check guarantees internal consistency, not correspondence with reality. Every figure entering the ledger comes from somewhere the ledger does not verify, so the exposure sits at those boundaries.

- **Valuation contracts.** A quote is taken at face value, and revaluation posts the difference directly to gains or losses. A manager who can install a valuation can move net asset value at will, so the first thing to inspect is who holds that permission and whether the valuation has its own bounds.
- **Prices supplied with amount updates.** `increase` and `decrease` convert quantities using a price passed in the message rather than one the hub derives.
- **The initialisation gap.** Value can arrive before a holding's accounts exist, and correctness then depends on the catch-up posting in `initializeHolding` running exactly once.
- **Snapshot liveness.** Nothing forces a share class to reach a quiet state, and a price that stops updating fails silently rather than loudly.

## References

### Related articles on this site

- [How Centrifuge Vaults Work: Asynchronous ERC-7540 Investment on a Hub-and-Spoke Protocol](https://rya-sge.github.io/access-denied/2026/08/18/centrifuge-vaults/)
- [Centrifuge Cross-Chain Messaging: Per-Pool Adapter Quorums, Batching and Failure Recovery](https://rya-sge.github.io/access-denied/2026/08/18/centrifuge-cross-chain-messaging/)

### Protocol documentation

- [Centrifuge developer documentation](https://docs.centrifuge.io/)
- [Onchain accounting](https://docs.centrifuge.io/developer/protocol/features/onchain-accounting/)
- [Hub architecture](https://docs.centrifuge.io/developer/protocol/architecture/hub/)
- [Security reviews and audit reports](https://docs.centrifuge.io/developer/security/audits)

### Standards and background

- [EIP-1153: Transient storage opcodes](https://eips.ethereum.org/EIPS/eip-1153)
- [ERC-7540: Asynchronous ERC-4626 Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-7540)

### Analyzed source

- [centrifuge/protocol](https://github.com/centrifuge/protocol) — analyzed at commit [`a1aeae93c94e8a3dbe078f0fefbe9a1a340ffde1`](https://github.com/centrifuge/protocol/tree/a1aeae93c94e8a3dbe078f0fefbe9a1a340ffde1) (no release tag on this commit; it follows the `deploy-testnet-v3.2` tag), 2026-08-18
