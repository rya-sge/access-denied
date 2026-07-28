---
layout: post
title: "Gnosis Conditional Tokens — Combinatorial Prediction Markets on ERC-1155"
date:   2026-07-28
lang: en
locale: en-GB
categories: blockchain ethereum defi solidity
tags: blockchain ethereum solidity conditional-tokens prediction-market erc-1155 gnosis alt-bn128 elliptic-curve
description: How the Gnosis Conditional Tokens contracts model prediction markets, why collection identifiers are elliptic curve points on alt_bn128, and what the 2019 audit found.
image: /assets/article/blockchain/defi/conditional-tokens/2026-07-28-gnosis-conditional-tokens-framework.png
isMath: true
---

The Gnosis Conditional Tokens contracts are a small pair of Solidity files that underpin a large part of on-chain prediction market infrastructure. In roughly 290 lines of contract code plus a helper library, they define how a question becomes a *condition*, how a subset of that condition's answers becomes a tradable ERC-1155 token, and how those tokens compose across several independent questions without the ordering of the questions mattering. This article walks through the data model, the elliptic curve construction used to derive identifiers, the split/merge/redeem operations that enforce collateral backing, and the two critical findings that shaped the final design.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The problem the framework solves

A conventional prediction market contract creates one outcome token per possible answer to one question. Backing a claim that depends on two questions means nesting: the outcome tokens of the first market are used as collateral for a second market. That construction works, but it produces an asymmetry that the framework was written to remove.

Consider two oracles reporting on two independent questions:

1. Which **choice** out of Alice, Bob, and Carol will be made?
2. Will the **score** be high or low?

There are two ways to nest them. Either the *choice* market is created first and its outcome tokens collateralise a *score* market, or the reverse. Both routes produce a token that pays out when Alice is chosen and the score is high, and economically those two tokens are identical. On-chain they are not. They live in different contracts, hold different balances, and cannot be traded against each other. Liquidity fragments across every ordering of the same set of conditions, and the fragmentation grows factorially with depth.

Partial redemption inherits the same problem. In the nested design, unwinding a second-layer token back to a first-layer token requires the second layer's condition to have resolved, because the second-layer contract is the only place that knows how to convert. The dependency runs in one direction only, fixed at market creation time.

The Conditional Tokens Framework removes both limitations by keeping every condition in a single contract and by deriving token identifiers from a construction where combination is commutative. A position contingent on *(Alice or Bob)* and *(low score)* has exactly one identifier, whichever order it was built in, and stake in it can be redeemed against whichever of the two conditions resolves first.

## Conditions and the payout vector

A **condition** is a question assigned to a specific oracle with a fixed number of outcome slots. It is created by anyone through `prepareCondition`:

```solidity
function prepareCondition(address oracle, bytes32 questionId, uint outcomeSlotCount) external {
    // Limit of 256 because we use a partition array that is a number of 256 bits.
    require(outcomeSlotCount <= 256, "too many outcome slots");
    require(outcomeSlotCount > 1, "there should be more than one outcome slot");
    bytes32 conditionId = CTHelpers.getConditionId(oracle, questionId, outcomeSlotCount);
    require(payoutNumerators[conditionId].length == 0, "condition already prepared");
    payoutNumerators[conditionId] = new uint[](outcomeSlotCount);
    emit ConditionPreparation(conditionId, oracle, questionId, outcomeSlotCount);
}
```

Three points are worth isolating. First, the condition identifier is `keccak256(abi.encodePacked(oracle, questionId, outcomeSlotCount))`, so the oracle address and the slot count are baked into the identity of the condition rather than stored as mutable fields. Second, `questionId` is opaque to the contract: a client is free to interpret it as an IPFS hash pointing at a full question specification, and the contract never inspects it. Third, the length of `payoutNumerators[conditionId]` doubles as the initialisation flag, which is why `getOutcomeSlotCount` returning zero means "not prepared".

The upper bound of 256 slots comes directly from the representation chosen for subsets of slots, discussed in the next section. The lower bound of 2 rules out a degenerate condition whose single slot would always absorb the whole payout.

Resolution is performed by the oracle through `reportPayouts`:

```solidity
function reportPayouts(bytes32 questionId, uint[] calldata payouts) external {
    uint outcomeSlotCount = payouts.length;
    require(outcomeSlotCount > 1, "there should be more than one outcome slot");
    // IMPORTANT, the oracle is enforced to be the sender because it's part of the hash.
    bytes32 conditionId = CTHelpers.getConditionId(msg.sender, questionId, outcomeSlotCount);
    require(payoutNumerators[conditionId].length == outcomeSlotCount, "condition not prepared or found");
    require(payoutDenominator[conditionId] == 0, "payout denominator already set");
    ...
}
```

There is no access control modifier here, and none is needed. The condition identifier is recomputed from `msg.sender`, so a caller who is not the designated oracle simply addresses a different condition identifier, which will almost certainly be unprepared and cause the length check to fail. Authorisation is a consequence of the identifier derivation rather than a separate check.

The oracle submits a vector of numerators $(n_0, \dots, n_{k-1})$ over the $k$ slots. The contract sums them into a denominator $d$ and stores both:

$$
\begin{aligned}
d = \sum_{j=0}^{k-1} n_j, \qquad d > 0
\end{aligned}
$$

The normalised payout of slot $j$ is $n_j / d$. A categorical question with three candidates resolves to something like $(0, 1, 0)$, meaning the second candidate was chosen. A scalar question bracketing a range $[0, 1000]$ with two slots resolves to $(9, 1)$ to indicate a value of 100, since the reported score sits nine times closer to the low endpoint than to the high one. Because `payoutDenominator` is non-zero only after resolution, it is also the flag that gates redemption, and the `require` on it makes resolution single-shot.

## Outcome collections and index sets

An **outcome collection** is a nonempty proper subset of one condition's outcome slots. Writing the three candidate slots as `A`, `B` and `C`:

- `(A|B)` is valid, and represents the event "Alice or Bob was chosen".
- `(C)` is valid.
- `()` is rejected, because an empty subset represents no eventuality at all and would be permanently worthless.
- `(A|B|C)` is rejected, because a subset containing every slot always pays out in full and is therefore economically identical to whatever collateralised it.

Slots from different conditions cannot be mixed inside a single outcome collection. Cross-condition composition happens one level up, at the collection identifier.

A collection is encoded as an **index set**, a 256-bit mask over the slots of its condition, with slot $j$ at bit $j$. So `(A|B)` is `0b011 == 3` and `(C)` is `0b100 == 4`. This is the reason a condition may not exceed 256 slots: the mask must fit in one EVM word.

A **partition** is a list of index sets that are pairwise disjoint. The contract validates disjointness with a running complement rather than a nested loop, which keeps the check linear:

```solidity
uint fullIndexSet = (1 << outcomeSlotCount) - 1;
uint freeIndexSet = fullIndexSet;
for (uint i = 0; i < partition.length; i++) {
    uint indexSet = partition[i];
    require(indexSet > 0 && indexSet < fullIndexSet, "got invalid index set");
    require((indexSet & freeIndexSet) == indexSet, "partition not disjoint");
    freeIndexSet ^= indexSet;
    ...
}
```

`freeIndexSet` starts as every slot and has each consumed index set XORed out of it. Requiring `indexSet & freeIndexSet == indexSet` asserts that every bit of the incoming set is still unclaimed. The strict inequality `indexSet < fullIndexSet` enforces the proper-subset rule, and `indexSet > 0` the nonemptiness rule.

The edge case of exactly 256 slots is handled by arithmetic that looks like an overflow but is not. Under Solidity 0.5 semantics, `1 << 256` evaluates to zero, and the unchecked subtraction `0 - 1` wraps to the word with all 256 bits set, which is precisely the mask required. The expression yields the correct value for every slot count in range.

Whatever remains in `freeIndexSet` after the loop is meaningful in itself. If it is zero, the partition covers the condition entirely. If it is non-zero, the partition covers only a sub-collection, and `fullIndexSet ^ freeIndexSet` is the index set of that sub-collection. The split and merge functions branch on exactly this distinction.

## Deriving collection identifiers on alt_bn128

A collection identifier cannot be a plain hash of the collection's data, because it must satisfy two requirements that pull in opposite directions:

- Identifiers for two collections belonging to different conditions must be **combinable** into a single identifier, and the combination must be commutative and associative so that ordering is irrelevant.
- The combination must be **collision resistant**, so that no attacker can construct a set of collections whose combined identifier equals that of a different set.

The first version of the contracts combined identifiers by summing hashes modulo $2^{256}$, an incremental hashing scheme known as AdHash. Summation is commutative and associative, so requirement one held. Requirement two did not: [Wagner's generalized birthday problem](https://link.springer.com/chapter/10.1007/3-540-45708-9_19) gives practical algorithms for finding sets of hash values that sum to a chosen target, and the same weakness applies to bitwise XOR. The audit flagged this as critical.

The replacement is an [Elliptic Curve Multiset Hash](https://arxiv.org/abs/1601.06502). Each collection is mapped to a point on the alt_bn128 curve, and collections are combined by elliptic curve point addition. The group law is commutative and associative, and finding a set of points summing to a target point requires solving a discrete logarithm relation rather than a subset-sum, which is not tractable on this curve.

The curve is the one exposed by the EVM precompiles of [EIP-196](https://eips.ethereum.org/EIPS/eip-196):

$$
\begin{aligned}
y^2 = x^3 + 3 \pmod P, \qquad P = 21888242871839275222246405745257275088696311157297823662689037894645226208583
\end{aligned}
$$

![Identifier derivation across conditions, collections and positions]({{site.url_complet}}/assets/article/blockchain/defi/conditional-tokens/conditional-tokens-id-derivation-concept.png)

### Hashing to a curve point

`CTHelpers.getCollectionId` maps a `(conditionId, indexSet)` pair to a point using try-and-increment:

```solidity
uint x1 = uint(keccak256(abi.encodePacked(conditionId, indexSet)));
bool odd = x1 >> 255 != 0;
uint y1;
uint yy;
do {
    x1 = addmod(x1, 1, P);
    yy = addmod(mulmod(x1, mulmod(x1, x1, P), P), B, P);
    y1 = sqrt(yy);
} while(mulmod(y1, y1, P) != yy);
if(odd && y1 % 2 == 0 || !odd && y1 % 2 == 1)
    y1 = P - y1;
```

The keccak digest seeds a candidate x-coordinate, and its top bit is peeled off first as an `odd` flag that will select which of the two possible y-coordinates is canonical. Note that the increment happens before the first residuosity test, so the raw digest is never used as an x-coordinate directly; the `addmod` also reduces a digest that exceeds $P$ into the field.

Each iteration computes $x^3 + 3$ and attempts a square root. Because $P \equiv 3 \pmod 4$, the square root of a quadratic residue $a$ is $a^{(P+1)/4}$, and the `sqrt` helper is an addition chain for that exponent, unrolled into more than 300 `mulmod` operations in inline assembly. The helper is unconditional: it returns $a^{(P+1)/4}$ whether or not $a$ is a residue, and the caller distinguishes the two cases by squaring the result and comparing. Roughly half of all field elements are residues, so the loop terminates after two iterations on average. The worked example in the project documentation needs four.

The final parity adjustment replaces $y$ with $P - y$ when its parity disagrees with the flag, which pins down a single point out of the pair $(x, \pm y)$.

### Compression and combination

Because $P < 2^{254}$, an x-coordinate leaves two spare bits in an EVM word. The framework uses bit 254 to record the parity of $y$ and leaves bit 255 clear, giving a 32-byte compressed point that fits a `bytes32`:

```solidity
if(y1 % 2 == 1)
    x1 ^= 1 << 254;
return bytes32(x1);
```

Decompression is the inverse, and it revalidates rather than trusting the input:

```solidity
uint x2 = uint(parentCollectionId);
if(x2 != 0) {
    odd = x2 >> 254 != 0;
    x2 = (x2 << 2) >> 2;
    yy = addmod(mulmod(x2, mulmod(x2, x2, P), P), B, P);
    uint y2 = sqrt(yy);
    if(odd && y2 % 2 == 0 || !odd && y2 % 2 == 1)
        y2 = P - y2;
    require(mulmod(y2, y2, P) == yy, "invalid parent collection ID");

    (bool success, bytes memory ret) = address(6).staticcall(abi.encode(x1, y1, x2, y2));
    require(success, "ecadd failed");
    (x1, y1) = abi.decode(ret, (uint, uint));
}
```

The `require` on `mulmod(y2, y2, P) == yy` is the load-bearing check. A caller supplies `parentCollectionId` as an arbitrary 32-byte value, and without that check any word could be interpreted as a parent collection. Rejecting x-coordinates that are not on the curve means a valid parent identifier can only be produced by actually running the derivation, which is what makes forging a parent collection infeasible.

Point addition is delegated to the precompile at address `0x06`. A parent identifier of `bytes32(0)` is treated as the group identity, which is why splitting from raw collateral passes zeros: adding the identity leaves the child collection identifier unchanged.

Two consequences follow from the group structure. Combination is commutative, so `(A|B)&(LO)` and `(LO)&(A|B)` produce the same identifier, which is the fungibility property the whole design exists to provide. And because `getCollectionId` performs a `staticcall`, it cannot be marked `pure`; the public wrapper on `ConditionalTokens` is declared `view`, unlike the `pure` wrappers for condition and position identifiers.

![Collection identifier derivation workflow]({{site.url_complet}}/assets/article/blockchain/defi/conditional-tokens/conditional-tokens-collection-id-workflow.png)

## Positions and the ERC-1155 token ID

A **position** pairs a collateral token with a combined collection identifier:

```solidity
function getPositionId(IERC20 collateralToken, bytes32 collectionId) internal pure returns (uint) {
    return uint(keccak256(abi.encodePacked(collateralToken, collectionId)));
}
```

The resulting `uint256` is used directly as the ERC-1155 token identifier, so `balanceOf(holder, positionId)` returns a holder's stake in that position and the standard transfer and approval functions work without modification.

The value of a position is the product of the values of its constituent collections. If a position bundles collections $C_1, \dots, C_m$ from distinct conditions and each $C_i$ carries a normalised payout $q_i \in [0,1]$, then one unit of the position is worth

$$
\begin{aligned}
\prod_{i=1}^{m} q_i
\end{aligned}
$$

units of collateral once every relevant condition has resolved. The **depth** of a position is $m$, the number of conditions it depends on. Depth-1 positions redeem directly to collateral; deeper positions redeem to a shallower position.

Using the project's worked example, with a collateral token `DollaCoin` at `0xD011ad011ad011AD011ad011Ad011Ad011Ad011A` denoted `$`, the categorical condition identifier is `0x67eb23e8932765c1d7a094838c928476df8c50d1d3898f278ef1fb2a62afab63` and the collection `(A|B)` has identifier `0x229b067e142fce0aea84afb935095c6ecbea8647b8a013e795cc0ced3210a3d5`. Hashing the two together gives the position `$:(A|B)` an ERC-1155 identifier of `0x5355fd8106a08b14aedf99935210b2c22a7f92abaf8bb00b60fcece1032436b7`.

Note that the collection identifier and the position identifier are distinct values with distinct roles, and confusing them is an easy integration mistake. `splitPosition` takes a *collection* identifier as its `parentCollectionId` argument, not the position identifier of the parent.

## Splitting, merging and redeeming

Stake in a position can only come into existence by consuming an equivalent amount of backing, either collateral pulled into the contract or stake in a shallower position that is burnt. This is what `splitPosition` enforces.

![splitPosition control flow]({{site.url_complet}}/assets/article/blockchain/defi/conditional-tokens/conditional-tokens-split-position-workflow.png)

After the partition loop described earlier, the function branches on `freeIndexSet`:

```solidity
if (freeIndexSet == 0) {
    // Partitioning the full set of outcomes for the condition in this branch
    if (parentCollectionId == bytes32(0)) {
        require(collateralToken.transferFrom(msg.sender, address(this), amount), "could not receive collateral tokens");
    } else {
        _burn(msg.sender, CTHelpers.getPositionId(collateralToken, parentCollectionId), amount);
    }
} else {
    // Partitioning a subset of outcomes for the condition in this branch.
    _burn(
        msg.sender,
        CTHelpers.getPositionId(collateralToken,
            CTHelpers.getCollectionId(parentCollectionId, conditionId, fullIndexSet ^ freeIndexSet)),
        amount
    );
}

_batchMint(msg.sender, positionIds, amounts, "");
```

Three source cases are covered. A full partition with no parent pulls ERC-20 collateral in. A full partition with a parent burns stake in the parent position one level up. A partial partition burns stake in the union of the covered slots, which is how `$:(B|C)` splits into `$:(B)` and `$:(C)` without touching slot `A`.

The ordering matters more than it appears. The source stake is consumed *before* `_batchMint` runs, and `_batchMint` is the call that invokes `onERC1155BatchReceived` on the recipient. A recipient contract therefore regains control only after the accounting is already balanced.

`mergePositions` is the exact inverse and burns first as well, calling `_batchBurn` on the partition before minting the parent position or transferring collateral out.

`redeemPositions` converts resolved stake back into backing:

```solidity
uint payoutNumerator = 0;
for (uint j = 0; j < outcomeSlotCount; j++) {
    if (indexSet & (1 << j) != 0) {
        payoutNumerator = payoutNumerator.add(payoutNumerators[conditionId][j]);
    }
}

uint payoutStake = balanceOf(msg.sender, positionId);
if (payoutStake > 0) {
    totalPayout = totalPayout.add(payoutStake.mul(payoutNumerator).div(den));
    _burn(msg.sender, positionId, payoutStake);
}
```

For an index set $S$ the numerator is $N_S = \sum_{j \in S} n_j$, and a stake $s$ redeems for $\lfloor s \cdot N_S / d \rfloor$ units of backing. Redemption always consumes the caller's entire balance in each listed position rather than a caller-specified amount, which is why the function takes index sets rather than amounts.

The function does not require the supplied index sets to be disjoint, and it does not need to. A repeated index set resolves to the same position identifier, whose balance is read fresh on each iteration and is already zero after the first burn, so the second pass contributes nothing.

The floor division is worth noting for integrators. A stake that is not an exact multiple of the denominator leaves a remainder of at most $d - 1$ base units stranded in the contract per redeemed position. The effect is negligible for the 18-decimal collateral typical of these markets and unbounded only in the sense that it accumulates across many redemptions, but a market maker settling small positions against a large denominator should be aware of it.

## The collateral conservation invariant

The three operations above are the only ways stake is created or destroyed, and each of them preserves a single invariant: the contract's balance of a collateral token is at least the total redeemable value of every outstanding position backed by that token. Splitting from collateral increases both sides by `amount`. Splitting deeper, merging, and redeeming to a parent position move value between positions without touching the collateral balance. Redeeming to collateral decreases both sides by the payout, rounded down in the contract's favour.

Nothing in the contract lets an account mint stake without consuming backing, and nothing lets it withdraw collateral except through a resolved condition. That is the whole of the contract's security argument, and both critical audit findings were attacks on it.

## What the 2019 audit found

The [audit report](https://github.com/gnosis/conditional-tokens-contracts/blob/master/docs/audit/AuditReport-ConditionalTokens.md) shipped in the repository lists three issues against commit `a050b6c`, two of them critical. The two criticals are connected: the exploit path described in the first depends on the identifier weakness described in the second.

### Forging a collection through the minting hook

The first finding chains three properties of the earlier revision:

1. In `splitPosition`, the target tokens were minted *before* the source tokens were burnt.
2. Minting calls `onERC1155Received` on the recipient, handing control to a contract recipient mid-operation.
3. Under AdHash, a combined collection identifier was a plain sum of member hashes, so an attacker could solve for a parent identifier whose split lands on a chosen target.

Property 3 lets an attacker pick a parent collection identifier $P$ constructed so that splitting it produces, among its outputs, an already-redeemable position. Property 1 and 2 let the attacker cover the resulting shortfall: during the minting hook, before the burn of $P$ has run, the attacker re-enters `redeemPositions` twice, once to conjure the stake in $P$ that the pending burn will consume, and once to drain real collateral from the forged winning position. The split then completes cleanly and the accounting looks consistent.

![Reentrancy attack path against the pre-fix revision]({{site.url_complet}}/assets/article/blockchain/defi/conditional-tokens/conditional-tokens-reentrancy-attack-workflow.png)

The fix was to reorder the operation so the source stake is consumed first, which is the ordering visible in the shipped code. Re-entering the contract from the mint hook is still possible, but there is no longer a window in which minted stake exists while its backing has not yet been taken.

### The AdHash collision

The second finding targets property 3 on its own. Even with the reordering, an identifier scheme where combination is truncated addition of hashes is vulnerable to a generalized birthday attack, which finds sets of values summing to a target far faster than brute force. Any such collision lets an attacker reach a position whose backing was never posted.

Replacing AdHash with the elliptic curve multiset hash removes the algebraic structure the attack relied on. The audit noted the replacement as promising but pending evaluation, and a follow-up review of the multiset hashing proposal plus a January 2020 accumulator audit are both archived in the repository's `docs/audit` directory.

### Batch minting

The third and minor finding was about gas. Minting each target position individually triggered one `onERC1155Received` external call per position, and the auditors suggested a batch mint using `_doSafeBatchTransferAcceptanceCheck` instead. The shipped `_batchMint` does exactly that, collapsing $n$ acceptance callbacks into one and emitting a single `TransferBatch` event.

## Implementation notes for integrators

A handful of behaviours are easy to trip over when building on top of the framework.

- **The oracle is fully trusted.** `reportPayouts` accepts any vector with a positive sum, and there is no dispute period, no challenge window, and no way to correct a report. Every economic guarantee downstream of resolution rests on the oracle address chosen at `prepareCondition` time. Real deployments layer an escalation mechanism such as a dispute-resolution oracle on top; the contracts themselves take no position on this.
- **Conditions resolve once.** `payoutDenominator` is checked to be zero and then set, so a second `reportPayouts` for the same condition reverts. Combined with the fact that the oracle address is part of the condition identifier, a condition's outcome is immutable once written.
- **Anyone can prepare a condition.** `prepareCondition` has no caller restriction. It is the `oracle` argument, not `msg.sender`, that gains reporting rights, so preparation is a permissionless bookkeeping step and clients must verify that the oracle in a condition identifier is the one they expect.
- **The collateral token is not validated.** Any address is accepted as `collateralToken`, and the return value of `transfer` and `transferFrom` is checked with a `require` rather than a safe-transfer wrapper. Tokens that do not return a boolean, and tokens with transfer fees or rebasing balances, will either revert or silently break the conservation invariant.
- **Approval must be granted first.** Splitting from collateral calls `transferFrom`, so the caller must have approved the `ConditionalTokens` contract for at least `amount` beforehand.
- **Transfers ignore the `data` parameter.** The ERC-1155 implementation forwards `data` to the receiver hook but attaches no meaning to it, and contract recipients must implement `ERC1155TokenReceiver` and return the correct magic value or the transfer reverts.

## Deployment and downstream use

The contracts target Solidity `^0.5.1` with a Truffle build, depend on `openzeppelin-solidity` pinned at `2.3.0`, and are released under LGPL-3.0. Version 1.0.3 is the last tagged release, and the canonical deployments recorded in the repository are:

| Network | Address |
|---------|---------|
| Mainnet | `0xC59b0e4De5F1248C1140964E0fF287B192407E0C` |
| xDai | `0xCeAfDD6bc0bEF976fdCd1112955828E00543c0Ce` |
| Rinkeby | `0x36bede640D19981A82090519bC1626249984c908` |

The repository deliberately contains no market maker. Pricing and liquidity live in the separate `conditional-tokens-market-makers` project, which supplies an LMSR market maker and a fixed-product market maker operating on positions from this contract. Gnosis's own Omen interface was built on that pair, and Polymarket adopted the same framework for its markets on Polygon, where the ERC-1155 positions are traded through an external order book rather than an automated market maker. Keeping pricing logic out of the accounting layer is what lets one set of contracts back both designs.

## Conclusion

The Conditional Tokens Framework rests on one property: positions contingent on several independent questions should have a single identity regardless of the order in which they were assembled. Holding that property on-chain required moving identifier derivation from hashing into an elliptic curve group, since commutative combination and collision resistance coexist only where the combining operation is hard to invert. The audit found two critical issues, each of which broke the collateral conservation invariant from a different direction, and the shipped code carries both fixes.

The remaining design surface is deliberately left open. Oracle trust, dispute resolution, pricing, and liquidity are all outside the contract, which restricts itself to bookkeeping that is verifiable from the code alone.

![Mindmap summarising the Gnosis Conditional Tokens Framework]({{site.url_complet}}/assets/article/blockchain/defi/conditional-tokens/2026-07-28-gnosis-conditional-tokens-framework.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Condition** | A question assigned to a specific oracle with a fixed number of outcome slots, identified by `keccak256(oracle, questionId, outcomeSlotCount)`. |
| **Outcome slot** | One of a condition's possible answers; the oracle assigns each slot a share of the payout at resolution. |
| **Payout vector** | The numerators reported by the oracle, one per outcome slot, normalised by their sum which is stored as the payout denominator. |
| **Outcome collection** | A nonempty proper subset of one condition's outcome slots, worth the sum of the payouts of the slots it contains. |
| **Index set** | A 256-bit mask encoding an outcome collection, with outcome slot $j$ represented by bit $j$. |
| **Partition** | A list of pairwise disjoint index sets over the same condition, validated by the contract with a running complement. |
| **Collection identifier** | A compressed alt_bn128 curve point identifying one or more outcome collections, combinable across conditions by point addition. |
| **Position** | The pairing of a collateral token with a combined collection identifier, whose hash serves as the ERC-1155 token identifier. |
| **Position depth** | The number of conditions a position depends on; depth-1 positions redeem to collateral, deeper positions redeem to shallower positions. |
| **Elliptic curve multiset hash** | An incremental hash that maps each element to a curve point and combines them by point addition, replacing the collision-prone AdHash sum. |

## Annex — Security Implementation Checklist

The items below are the properties a deployment or a fork of this framework must satisfy for the collateral conservation invariant to hold. They are derived from the contract's security surface rather than transcribed from a standard.

### Identifier derivation

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Collection identifiers are combined by an operation with no exploitable algebraic structure, such as elliptic curve point addition, never by modular addition or XOR of hashes. | A generalized birthday attack forges a collection identifier that redeems against collateral it never posted. |
| ☐ | A supplied `parentCollectionId` is decompressed and its x-coordinate is verified to satisfy the curve equation before use. | Arbitrary 32-byte words are accepted as parent collections, letting an attacker address positions outside the legitimate derivation. |
| ☐ | The hash-to-curve loop rejects non-residues by squaring the candidate root and comparing, rather than trusting the exponentiation result. | Points that are not on the curve enter the identifier space and break the collision-resistance argument. |
| ☐ | The parity bit is fixed at a defined position outside the 254-bit x-coordinate and applied consistently in compression and decompression. | Two encodings map to the same point or one point yields two identifiers, splitting balances that should be fungible. |
| ☐ | The condition identifier binds the oracle address, the question identifier and the outcome slot count together. | Reporting rights or slot counts can be reassigned after preparation, invalidating already-minted positions. |

### Accounting order and reentrancy

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | In `splitPosition`, collateral is pulled in or the source stake is burnt before any target position is minted. | A recipient hook re-enters while unbacked stake exists and drains collateral, which is audit finding 1. |
| ☐ | In `mergePositions`, the partition is burnt before the parent position is minted or collateral is sent out. | The same reentrancy window reopens in the inverse direction. |
| ☐ | In `redeemPositions`, each position is burnt inside the loop before any payout is minted or transferred. | A hook re-enters and redeems the same stake twice against one balance. |
| ☐ | Every ERC-1155 receiver hook is reached only after all balance and collateral state has been written. | Any hook observes an inconsistent intermediate state and acts on it. |

### Partition and index set validation

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Each index set satisfies `0 < indexSet < fullIndexSet`, rejecting both the empty set and the full set. | A full-set collection is minted that is economically identical to its own collateral, creating a free unwind path. |
| ☐ | Disjointness is enforced across the whole partition, for example with `indexSet & freeIndexSet == indexSet`. | Overlapping sets mint more redeemable value than the backing consumed. |
| ☐ | Outcome slot count is bounded at 256 so the index set fits one EVM word, and is at least 2. | Bits are silently truncated, or a single-slot condition always pays in full without risk. |
| ☐ | The condition is confirmed prepared, by a non-zero `payoutNumerators` length, before any split or merge. | Positions are created against a condition that no oracle can ever resolve, permanently locking collateral. |

### Resolution and redemption

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The reporting condition identifier is recomputed from `msg.sender` so only the designated oracle can resolve. | Any account resolves any condition and redeems the entire collateral pool. |
| ☐ | Resolution is single-shot, gated on `payoutDenominator` being zero before it is written. | An oracle rewrites an outcome after redemptions have started, leaving later redeemers unbacked. |
| ☐ | The payout denominator is required to be strictly positive. | An all-zero report causes a division by zero, or freezes every position on the condition. |
| ☐ | Redemption is refused until the condition's denominator is non-zero. | Positions redeem against an unreported payout vector of zeros and stake is destroyed for nothing. |
| ☐ | Payout arithmetic rounds down and any remainder stays in the contract. | Rounding in the redeemer's favour lets repeated small redemptions withdraw more than the position is worth. |

### Collateral handling

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The return value of every ERC-20 `transfer` and `transferFrom` is checked, or a safe-transfer wrapper is used. | A token that returns false on failure is treated as having paid, minting stake with no backing. |
| ☐ | Collateral tokens with transfer fees, rebasing balances or callback hooks are excluded at the integration layer. | The amount received differs from the amount credited and the conservation invariant no longer holds. |
| ☐ | Balance arithmetic uses checked addition and subtraction throughout the ERC-1155 layer. | An underflow mints an enormous balance out of a burn of stake the holder does not have. |

## Frequently Asked Questions

**Q: What is the difference between a condition identifier, a collection identifier and a position identifier?**

They are the three layers of the data model. A condition identifier is `keccak256(oracle, questionId, outcomeSlotCount)` and names a question. A collection identifier is a compressed alt_bn128 point derived from a condition identifier and an index set, and it names a subset of that condition's answers, possibly combined with subsets from other conditions by point addition. A position identifier is `keccak256(collateralToken, collectionId)` and names the tradable ERC-1155 token that pairs a collection with the ERC-20 that backs it. Only the position identifier appears in balances; only the condition identifier appears in the payout mappings.

**Q: Why can a condition have at most 256 outcome slots?**

Because a subset of slots is represented as an index set, a bitmask stored in a single `uint256`. Bit $j$ of the mask indicates whether slot $j$ belongs to the collection, so 256 bits accommodate exactly 256 slots. The bound is a consequence of the representation rather than an economic choice. The full mask for a 256-slot condition is computed as `(1 << 256) - 1`, where the shift evaluates to zero under Solidity 0.5 semantics and the unchecked subtraction wraps to the correct all-ones word.

**Q: Why does the framework hash to an elliptic curve point instead of simply hashing the concatenated collection data?**

Because the identifiers must be combinable after the fact. A position spanning two conditions has to have the same identifier whichever condition it was split on first, so the combining operation must be commutative and associative. Plain concatenation and hashing is neither. The earlier design achieved commutativity by summing hashes, but modular sums are vulnerable to a generalized birthday attack that finds colliding sets. Elliptic curve point addition keeps commutativity and associativity while making the collision search equivalent to a discrete logarithm problem on alt_bn128.

**Q: How does `reportPayouts` restrict who may resolve a condition, given that it has no access control modifier?**

It recomputes the condition identifier from `msg.sender` together with the supplied question identifier and the length of the payout array. An account that is not the condition's designated oracle therefore addresses a completely different identifier, one that will not have been prepared, and the check `payoutNumerators[conditionId].length == outcomeSlotCount` fails. Authorisation falls out of the identifier derivation, which also means an attacker cannot resolve a condition by preparing a lookalike, since the oracle address is bound into the identifier.

**Q: What does a non-zero `freeIndexSet` at the end of the partition loop mean, and how does the contract use it?**

It means the supplied partition does not cover every outcome slot of the condition, so the operation is a split of a sub-collection rather than a split of the whole condition. The contract uses `fullIndexSet ^ freeIndexSet` as the index set of the covered union and burns stake in that position instead of pulling collateral or burning the parent. This is what allows `$:(B|C)` to split into `$:(B)` and `$:(C)` while leaving slot `A` untouched.

**Q: Combining the audit findings, why did the mint-before-burn ordering only become exploitable in the presence of the AdHash collision weakness?**

The reentrancy window alone gives an attacker control during an operation, but not a target worth reaching. To profit, the attacker needs a parent collection whose split produces a position that is already redeemable for collateral the attacker never backed, and constructing such a parent is exactly the collision problem. AdHash made it solvable, because the combined identifier was a modular sum the attacker could work backwards from. With the elliptic curve multiset hash, no such parent can be constructed, so the reentrancy window would have had nothing to exploit. The fixes are independent because either one alone closes the attack, and both were applied.

**Q: Why is `getCollectionId` declared `view` on the contract while `getConditionId` and `getPositionId` are `pure`?**

Because combining a child collection with a parent requires elliptic curve point addition, and that is performed by a `staticcall` to the precompile at address `0x06`. Any external call, even a static one to a precompile, disqualifies a function from being `pure` under the Solidity mutability rules. The other two helpers are plain `keccak256` computations over their arguments and require no state or external access.

## References

### Repository and documentation

- [gnosis/conditional-tokens-contracts](https://github.com/gnosis/conditional-tokens-contracts)
- [Conditional Tokens documentation](https://docs.gnosis.io/conditionaltokens/)
- [Audit Report — Gnosis Conditional Tokens](https://github.com/gnosis/conditional-tokens-contracts/blob/master/docs/audit/AuditReport-ConditionalTokens.md)
- [gnosis/conditional-tokens-market-makers](https://github.com/gnosis/conditional-tokens-market-makers)

### Standards

- [EIP-1155: Multi Token Standard](https://eips.ethereum.org/EIPS/eip-1155)
- [EIP-196: Precompiled contracts for addition and scalar multiplication on the elliptic curve alt_bn128](https://eips.ethereum.org/EIPS/eip-196)
- [EIP-20: Token Standard](https://eips.ethereum.org/EIPS/eip-20)

### Cryptography

- [Elliptic Curve Multiset Hash](https://arxiv.org/abs/1601.06502)
- [A Generalized Birthday Problem](https://link.springer.com/chapter/10.1007/3-540-45708-9_19)
- [Incremental Cryptography and Application to Virus Protection](http://cseweb.ucsd.edu/~mihir/papers/inchash.pdf)

### Tooling

- [OpenZeppelin Contracts (Solidity) 2.3.0](https://github.com/OpenZeppelin/openzeppelin-contracts/tree/v2.3.0)
- [Claude Code](https://claude.com/product/claude-code)
