---
layout: post
title: "Three Launchpad Bugs from the Bio Protocol EVM Audits - Units, Donations and Partial Claims"
date:   2026-09-22
lang: en
locale: en-GB
categories: blockchain ethereum security
tags: solidity security audit desci token vesting launchpad
series: bio-protocol
description: "Three Bio EVM launchpad audit bugs, with code: a vesting duration passed as a timestamp, a one-wei donation that bricks a launch, a transfer that burns claims."
image: /assets/article/blockchain/defi/bio-protocol/2026-09-22-bio-launchpad-evm-findings-mindmap.png
isMath: false
---

[Bio Protocol](https://www.bio.xyz/) is a decentralised-science launchpad: contributors commit a token, the protocol decides who receives how much of a new project token, and the result is handed to a vesting contract. Its EVM launchpad went through three generations between 2024 and 2025, and each was reviewed before deployment: the `FairAuctionVesting` Genesis swap by Pashov Audit Group in June 2024, the `Curation` and `LaunchFactory` pledging contracts by Pashov Audit Group in March 2025, and the V2 Launchpad Agent contracts by FYEO in July 2025. The launchpad source itself is private, so these reports are the only public description of how the code works and where it went wrong.

This article takes three findings from those reports and explains each one from the code up: what the contract was trying to do, the exact line that broke it, how the failure plays out for a user or an attacker, and the fix. The three were chosen because they belong to three different classes of launchpad bug, each of which recurs in other protocols: a **unit mismatch at the seam between two contracts**, a **balance equality check that a one-wei donation defeats**, and a **"safe" partial transfer that quietly destroys a user's claim**. A companion article covers the Solana programs.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The three reports

| Report | Date | Scope | Result | Status of the three findings |
|--------|------|-------|--------|------------------------------|
| Pashov Audit Group, *Bio Security Review* | 13 to 15 June 2024 | `FairAuctionVesting` (repository `MTXstudio/bio-contracts`, commit `c28a415…`, fixes `70e2f84…`) | 1 Medium, 6 Low | M-01 resolved |
| Pashov Audit Group, *Bio Security Review* | 12 to 14 March 2025 | `Curation`, `LaunchFactory` (repository `bio-xyz/launchpad-evm`, commit `e232dca…`, fixes `f5c92a5…`) | 1 Critical, 2 High, 2 Medium, 3 Low | C-01 and H-02 resolved |
| FYEO, *Security Code Review of Launchpad Agent EVM* | 14 to 18 July 2025 | `Launch`, `LaunchFactory`, `AgentFactory`, `AgentToken`, `AgentVeToken`, `veBIO` (repository `bio-xyz/launchpad-agent-evm`, commit `1368872…`) | 1 Medium, 6 Low, 14 Informational | Used for context |

The two contracts the findings live in work as follows.

**`FairAuctionVesting`** (2024) is a swap sale: holders of BioDAO tokens contribute them during a window, and at the end each contributor's share of the raise is paid partly in liquid `BIO` and partly in `vBIO`, the vesting balance of a `TokenVesting` contract. The sale contract holds the `BIO` to distribute, computes each user's `(bioAmount, vbioAmount)` from their contribution, transfers the liquid part to the user and the vested part to the vesting contract, and then asks the vesting contract to create a schedule.

**`Curation`** (2025) is a pledge crowdfund: `BIO` holders pledge to a project during a whitelist phase and then a public phase, can unpledge, and once `totalPledged` reaches `bioTarget` a fundraiser contract deploys the project. The fundraiser transfers the project's `bioDaoToken` into the `Curation` contract and calls `updateFundraiser()` to mark success; pledgers then call `claim()`, which computes their share of the project token and creates a vesting schedule for it.

Both therefore end at the same place, `TokenVesting.createVestingSchedule(beneficiary, start, cliff, duration, slicePeriodSeconds, revokable, amount)`, the function of Bio's open-source vesting contract described in the [protocol overview]({{site.url_complet}}/2026/09/18/bio-protocol-overview/). Two of the three findings are about that hand-off.

## Finding 1: a vesting duration passed as a timestamp (Curation C-01, Critical)

### What the code does

`Curation.claim()` pays each pledger their share of the project token. If the vesting period is already over it transfers directly; otherwise it moves the tokens into the vesting contract and creates a schedule:

```solidity
function claim() external {
    // ...
    // If the vesting period has ended, transfer tokens directly to the user
    if (vestingDuration < block.timestamp) {
        // ...
    } else {
        bioDaoToken.safeTransfer(address(vesting), bioDaoTokenToAmount);
        // Create a vesting schedule for the sender
        vesting.createVestingSchedule(
            msg.sender, vestingStart, vestingCliff, vestingDuration, ...
        );
    }
    // ...
}
```

The comparison on the first line settles the unit: `vestingDuration < block.timestamp` only makes sense if `vestingDuration` is a Unix timestamp, the moment the vesting ends. The same variable is then passed as the fourth argument of `createVestingSchedule`, whose signature reads:

```solidity
function createVestingSchedule(
    address _beneficiary,
    uint256 _start,
    uint256 _cliff,
    uint256 _duration,          // duration in seconds
    uint256 _slicePeriodSeconds,
    bool _revokable,
    uint256 _amount
) external whenNotPaused onlyRole(VESTING_CREATOR_ROLE)
```

`_duration` is a length in seconds, added to `_start` to obtain the end of the schedule. A timestamp in 2025 is about 1.74 billion seconds, so a schedule created with it would run for roughly 55 years from its start. Pashov's report calls the result "catastrophic for vesting schedule creation, as the duration would be an extremely large number", and rated it Critical: every pledger of every curation would have their project tokens locked for decades.

### Why the vesting contract did not catch it

Bio's `TokenVesting` has input bounds that were added after Pashov's own 2023 review of that contract: a duration must be between 7 days and 50 years. A 2025 timestamp is about 55 years, so in principle the call reverts with `InvalidDuration` rather than creating the bad schedule.

That does not make the bug harmless. A reverting `claim()` means **nobody can claim**, the project tokens sit in `Curation` with no other exit, and the failure only appears after the fundraise has succeeded and the tokens are committed. Had the timestamp been a few years earlier, or the bound absent, as it is in many vesting contracts, the schedule would have been created silently.

### The fix and the lesson

The fix is to compute a duration: `vestingDuration - vestingStart`, or to store a duration and derive the end timestamp for the comparison. The general lesson is that **every parameter crossing a contract boundary needs its unit checked at the call site**, not only its type. `uint256` carries no unit, and a value that is a timestamp in one contract and a duration in another compiles without a warning.

The same seam produced FYEO's V2 informational finding a few months later: the `VestingSchedule` struct field named `cliff` is documented as a duration but stored as `start + cliff`, a timestamp. Tests would have caught C-01 in a minute, which suggests the claim path had no test that asserted the schedule's end date.

## Finding 2: a one-wei donation bricks finalisation (Curation H-02, High)

### What the code does

Once a curation reaches its target, the fundraiser contract is expected to send the project tokens and then call `updateFundraiser()` to flip the curation into its successful state. The function checks that the tokens arrived:

```solidity
function updateFundraiser() external onlyFundraiserContract {
    if (isFundraiseSuccessful) revert Curation__FundraiserAlreadyUpdated();
    if (bioDaoTokenToDistribute != bioDaoToken.balanceOf(address(this))) {
        revert Curation__BioDAOTokenForVestingNotSent();
    }
    // ...
}
```

The check is an **equality** between an expected amount and the contract's live ERC-20 balance.

![Sequence of the one-wei donation: the fundraiser transfers the project tokens and calls updateFundraiser, which reads balanceOf and requires equality; an attacker who sent one wei beforehand makes the balance exceed the expected amount, so every call reverts and nothing can remove the extra wei]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-curation-donation-dos-sequence.png)

### The attack

Anyone can transfer ERC-20 tokens to any address. An attacker who holds one wei of `bioDaoToken` sends it to the `Curation` contract before `updateFundraiser()` runs, either by front-running the call in the mempool or simply at any earlier moment. The balance is now `bioDaoTokenToDistribute + 1`, the equality fails, and the function reverts. Nothing in the contract can remove the extra wei, so **every future call reverts too**: the curation is permanently stuck between "target reached" and "successful".

Pledgers cannot claim their project tokens, the fundraiser cannot finalise, and the only recourse is a redeployment. Pashov rated the impact High and the likelihood Medium, giving a High overall; the cost of the attack is one wei plus gas.

### The fix and the lesson

The fix is one character:

```solidity
-        if (bioDaoTokenToDistribute != bioDaoToken.balanceOf(address(this))) {
+        if (bioDaoTokenToDistribute > bioDaoToken.balanceOf(address(this))) {
```

With `>`, a surplus is harmless; the contract only insists that at least the required amount is present. The broader rule is that **`balanceOf` is never equal to anything you control**. It is a global, externally writable quantity, and any check of the form `balanceOf(this) == x` is an invitation to a griefing attack at the cost of dust. Contracts should either compare with `>=` or, better, keep internal accounting of what they received through their own functions and ignore the raw balance. The same class of bug appears in the Solana companion article in the opposite direction, where a vault balance *lower* than a recorded figure blocks a withdrawal.

## Finding 3: a "safe" partial transfer burns the claim (FairAuction M-01, Medium)

### What the code does

`FairAuctionVesting.claim()` marks the caller as claimed, computes what they are owed, and transfers the liquid `BIO` to them and the vested `BIO` to the vesting contract before creating the schedule:

```solidity
function claim() external nonReentrant isClaimable {
    UserInfo storage user = userInfo[msg.sender];
    if (totalRaised == 0 || user.contribution == 0) revert ZeroContribution();
    if (user.hasClaimed) revert AlreadyClaimed();
    user.hasClaimed = true;
    (uint256 bioAmount, uint256 vbioAmount) = getExpectedClaimAmount(msg.sender);
    emit Claim(msg.sender, bioAmount, vbioAmount);
    if (bioAmount > 0) {
        _safeClaimTransfer(BIO_TOKEN, msg.sender, bioAmount);
    }
    if (vbioAmount > 0) {
        _safeClaimTransfer(BIO_TOKEN, address(VBIO_TOKEN), vbioAmount);
        VBIO_TOKEN.createVestingSchedule(
            msg.sender, vestingStart, vestingCliff, vestingDuration, vestingSlicePerSecond, false, vbioAmount
        );
    }
}
```

The helper is what the name suggests: a transfer that never reverts for lack of balance.

```solidity
function _safeClaimTransfer(IERC20 token, address to, uint256 amount) internal {
    uint256 balance = token.balanceOf(address(this));
    bool transferSuccess = false;
    if (amount > balance) {
        transferSuccess = token.transfer(to, balance);
    } else {
        transferSuccess = token.transfer(to, amount);
    }
    if (!transferSuccess) revert TransferFailed();
}
```

If the contract holds less than `amount`, it sends whatever it holds, possibly zero, and reports success. Helpers like this are usually copied from farming contracts, where they exist to absorb a rounding error of a few wei on the last withdrawal.

### How it fails

The sale contract also has `emergencyWithdrawBIO()`, which lets the admin move the entire `BIO` balance to the treasury at any time, and nothing stops users from calling `claim()` afterwards.

![Activity flow of the partial-claim bug: after an emergency withdrawal the balance is zero, claim sets hasClaimed before transferring, the helper clamps the transfer to zero for both the user and the vesting contract, a vesting schedule is still created for the full amount, and the user ends with nothing and no right to claim again]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-fairauction-partial-claim-activity.png)

Walk through a claim after the balance has been drained:

- `hasClaimed` is set to `true` before any transfer.
- `_safeClaimTransfer(BIO, user, bioAmount)` finds `balance == 0`, transfers zero and returns.
- `_safeClaimTransfer(BIO, vBIO, vbioAmount)` does the same: the vesting contract receives nothing.
- `createVestingSchedule(user, ..., vbioAmount)` is still called for the full amount. `TokenVesting` checks that its *pool* has enough uncommitted balance, not that this particular transfer arrived, so as long as earlier claims' tokens are sitting in the pool the schedule is accepted.
- `claim()` succeeds and emits `Claim(user, bioAmount, vbioAmount)` for amounts that were never paid.

The user has received zero `BIO`, holds a `vBIO` schedule that the pool cannot honour for everyone, and can never call `claim()` again. Pashov rated the impact High (loss of the claim) and the likelihood Low (it requires the admin's emergency withdrawal first), giving a Medium.

### The fix and the lesson

The recommendation was to delete `_safeClaimTransfer` and use a plain `safeTransfer`, so that a claim either pays in full or reverts and leaves `hasClaimed` untouched. Two rules follow. **A claim must be all-or-nothing**: state that records "this user has been paid" may only be written when the full amount has moved, and a transfer helper that silently clamps the amount violates that by construction. And **a transfer into a vesting contract must be reconciled with the schedule it funds**: `TokenVesting`'s pool-level check is a reasonable design for a contract funded in bulk, but it means the caller is responsible for delivering exactly the scheduled amount in the same transaction.

## Other findings worth knowing

The three findings above are not the only ones of interest in the reports. Four others are short enough to summarise:

- **Cap bypass through a counter that never decrements (Curation H-01, High).** `_whitelistPledge` increased `whitelistPledges[user]` but `_unpledge` never decreased it. A whitelisted user who pledged and unpledged 10 tokens twice had `whitelistPledges == 20` with nothing pledged, and the public phase then allowed them `maxTotalPledgePerAddress + 20`. The sibling M-02 is the same drift on the global `totalPledgedForWhitelist`. Every counter used in a cap check needs a reverse path.
- **Wrong denominator after unpledging (Curation M-01, Medium).** `claim()` computed `amount * bioDaoTokenToDistribute / bioTarget`, but users could still unpledge after success, so `totalPledged` fell below `bioTarget`, each claimer received less than their share and the remainder was stranded. The fix divides by the final `totalPledged`.
- **An admin sweep with no scope (FYEO V2-15, Informational).** `withdrawLeftAssetsAfterFinalized(to, token, amount)` lets an admin withdraw any ERC-20 up to the full balance as soon as a launch ends, including participants' deposits and unclaimed launch tokens. FYEO left it as an open recommendation to "make sure this can not be abused by a malicious admin".
- **Upgradeable hygiene (FYEO V2-01, 03, 06, 11).** Missing `_disableInitializers()` in the `VeBIO` and `Launch` implementations, an `initialize` that called only `__Pausable_init()` while inheriting non-upgradeable `AccessControl`, and a `ReentrancyGuard` never initialised under a proxy. These are the standard UUPS mistakes and were remediated.

## Conclusion

Three findings, three classes of launchpad failure, all at points where one contract hands value or state to another:

- **Units at the seam.** `Curation.claim()` passed a timestamp where `TokenVesting` expected seconds. Solidity's `uint256` does not carry a unit; the call site has to.
- **Equality on `balanceOf`.** `updateFundraiser()` required the live balance to equal an expected amount, and one donated wei made the launch unfinalisable forever. Compare with `>=`, or account internally.
- **Clamped transfers.** `_safeClaimTransfer` turned an underfunded sale into a silent loss: `hasClaimed` set, zero paid, a vesting schedule recorded for tokens that never arrived. Claims must pay in full or revert.

All three were resolved before deployment, which is the point of a pre-launch review. The launchpad code is not public, so the reports remain the reference for anyone integrating with or reasoning about these contracts.

![Mindmap of the three EVM findings: the timestamp-as-duration critical, the one-wei donation denial of service, the partial-claim medium, other findings from the same reports, and the three audits they come from]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/2026-09-22-bio-launchpad-evm-findings-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Curation** | Bio's 2025 pledge crowdfund contract: `BIO` holders pledge toward a target, can unpledge, and claim project tokens once a fundraiser marks the curation successful. |
| **FairAuctionVesting** | Bio's 2024 Genesis swap contract: BioDAO tokens contributed during a window are paid out as liquid `BIO` plus vested `vBIO`. |
| **TokenVesting** | Bio's open-source vesting contract; a sale funds it by transfer and calls `createVestingSchedule` with a start, cliff, duration in seconds, slice, revocability and amount. |
| **vBIO** | The non-transferable ERC-20 balance a `TokenVesting` contract exposes, equal to a holder's unreleased vested amount. |
| **Unit mismatch** | Passing a value with one meaning (a timestamp) to a parameter with another (a duration) of the same Solidity type. |
| **Donation attack** | Sending tokens directly to a contract to change its `balanceOf` and break a check that compares it with an expected value. |
| **Front-running** | Submitting a transaction so that it is mined before a pending one, here to place the donation before finalisation. |
| **Clamped transfer** | A helper that transfers `min(amount, balance)` instead of reverting when the balance is short. |
| **All-or-nothing claim** | A claim that either pays the full amount and records it, or reverts and leaves the claim available. |
| **Push-funded vesting** | A vesting contract that expects tokens to be transferred to it before a schedule is created, checked at the pool level rather than per schedule. |

### Security Implementation Checklist

Derived from the three findings and their siblings, for any contract that sells or distributes a token and hands the result to a vesting contract.

#### Cross-contract hand-off

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every argument passed to another contract is checked for unit as well as type: seconds vs timestamp, absolute vs relative, basis points vs percent. | A timestamp used as a duration locks tokens for decades, or reverts every claim (Curation C-01). |
| ☐ | The amount transferred to a vesting or escrow contract in a call equals the amount scheduled in the same call, and the schedule is created only if the transfer moved the full amount. | Schedules recorded for tokens that never arrived; last claimants cannot be paid (FairAuction M-01). |
| ☐ | The calling contract holds the role the callee requires (`VESTING_CREATOR_ROLE`) and deployment scripts grant it before the sale opens. | Every swap or claim reverts once the sale is live (FairAuction L-05). |
| ☐ | Vesting parameters used by a sale are frozen once contributions begin. | Users contribute on one schedule and receive another (FairAuction L-06). |

#### Balance and accounting

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | No check compares `balanceOf(address(this))` for equality with an expected amount; use `>=` or internal accounting. | One wei of donation makes finalisation revert forever (Curation H-02). |
| ☐ | Every counter used in a cap check is decremented on the reverse operation (unpledge, refund, cancel). | Repeated pledge/unpledge inflates the counter and bypasses the cap (Curation H-01, M-02). |
| ☐ | Pro-rata allocations divide by the final total of the population being paid, not by a target that the total may no longer equal. | Claimers are underpaid and the remainder is stranded (Curation M-01). |
| ☐ | Unsold or residual tokens have a defined recipient and a computed amount, not "whatever is left". | Admin sweeps participants' funds or unclaimed tokens (FYEO V2-15, FairAuction L-01). |

#### Claims and admin actions

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | `hasClaimed` (or equivalent) is written only after the full amount has been transferred, and transfers revert rather than clamp. | Users lose the right to claim while receiving nothing (FairAuction M-01). |
| ☐ | An emergency withdrawal either disables claims or withdraws only the surplus above what is owed. | Claims after the withdrawal succeed with zero payout (FairAuction M-01, L-04). |
| ☐ | Finalisation can always be reached from a filled sale, and a failed sale always allows full refunds regardless of admin actions. | A sale is stuck between "filled" and "successful" (Curation L-01, H-02). |
| ☐ | Upgradeable implementations call `_disableInitializers()` in the constructor and chain every parent initializer. | Implementation can be initialised by an attacker; guards and roles unset under the proxy (FYEO V2-01, 03, 06, 11). |

## Frequently Asked Questions

**Q: Why was a bug that most likely causes a revert rated Critical rather than a denial of service?**

Because the impact in either branch is total. If the timestamp had passed `TokenVesting`'s 50-year bound, every pledger's project tokens would have been locked for about 55 years; since it does not, every `claim()` reverts and the tokens sit in `Curation` with no other exit. Both outcomes lose the entire distribution for every participant of every curation, with a likelihood of one, which is the top of Pashov's matrix. The report rated it High impact and High likelihood.

**Q: How can one wei permanently disable a contract, and why is `>=` enough to fix it?**

Because `balanceOf` is written by anyone who transfers tokens to the address, while `bioDaoTokenToDistribute` is a fixed expectation. An equality between them holds only if nobody ever sends a single extra unit, and the contract has no function to remove one. 
Changing the check to `bioDaoTokenToDistribute > balance`, reverting only when short, makes surplus irrelevant: the fundraiser's transfer still has to arrive, and extra tokens simply sit there. The stronger pattern is to not read `balanceOf` at all and to record receipts inside the function that receives them.

**Q: What is wrong with a transfer helper that sends whatever balance is available?**

It converts an underfunded contract from a loud failure into a quiet one. A plain `safeTransfer` reverts when the balance is short, the transaction is rolled back, `hasClaimed` stays false, and the user can retry once the contract is funded. The clamped helper succeeds, writes `hasClaimed = true`, emits an event for the full amount and pays zero.

The user's claim is consumed with nothing in return, and in this contract a vesting schedule is also created for tokens the vesting contract never received.

**Q: Why did `TokenVesting.createVestingSchedule` accept a schedule when no tokens had just been transferred to it?**

Its precondition is `getWithdrawableAmount() >= amount`, where the withdrawable amount is the contract's whole balance minus everything already committed to schedules. That is a pool-level check: if earlier claims had deposited tokens that were still unreleased, the pool had headroom, so a new schedule was accepted even though this particular claim contributed nothing. The pool is then over-committed and the last beneficiaries to release will find it empty. The caller, not the vesting contract, has to ensure each schedule is funded.

**Q: Combining findings 2 and 3, what single design rule would have prevented both?**

Keep internal accounting of what the contract has received and what it owes, and never let a raw ERC-20 balance decide either a state transition or a payout amount. Finding 2 used the balance as the condition to finalise; finding 3 used it as the amount to pay. With `received` and `owed` tracked in storage, finalisation checks `received >= required`, claims transfer exactly `owed[user]` or revert, and neither a donation nor an emergency withdrawal can silently change the outcome.

**Q: Were these bugs in the open-source contracts?**

No. `TokenVesting`, `Token` and `MerkleAirdrop` are public; the sale contracts that call them, `FairAuctionVesting`, `Curation`, `LaunchFactory` and the V2 `Launch` and `AgentFactory` family, are private, and the audit reports are the only public source for their code. The one contract the findings touch that is public, `TokenVesting`, behaved as designed; the bugs were in how the callers used it.

## References

### Audit reports

- [Bio Security Review (FairAuctionVesting), Pashov Audit Group, June 2024](https://499247139-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F3ba2jNU6BPQUl4RXgHor%2Fuploads%2FXm1EkQX20KCOrH0s1e3Y%2FBio-security-review.pdf?alt=media&token=5e15e865-c639-491a-95e8-9a46715e280e) — review commit `c28a41517d1f426d49e9b477e565432f1307ba58`, fixes `70e2f84927752fd43446dee282df189993f55548` (private repository `MTXstudio/bio-contracts`)
- [Bio Security Review (Curation, LaunchFactory), Pashov Audit Group, March 2025](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F3ba2jNU6BPQUl4RXgHor%2Fuploads%2FW7mPQHDWHGApxw1jl6CO%2FBio-security-review_2025-03-12.pdf?alt=media&token=e715feb0-d7f7-4297-b0da-f68fc4686dc9) — review commit `e232dca8a7899324be31ac35090e7b88221b13a6`, fixes `f5c92a54ec87310d59b8e4e6af7cbec914d2c435` (private repository `bio-xyz/launchpad-evm`)
- [Security Code Review of Launchpad Agent EVM, FYEO, July 2025](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F3ba2jNU6BPQUl4RXgHor%2Fuploads%2FuYIpl4lmoMs2hOgnrj18%2FLaunchpad%20v2%20Contracts%20(FYEO).pdf?alt=media&token=a30d98e2-2b1b-4b00-bca0-d29692d9bd9b) — review commit `136887267584adbd77509cf0062abf9bcd8e7c85`, remediations `b24d9d4133d58538ea6cf812f6b49f2352ff684f` (private repository `bio-xyz/launchpad-agent-evm`)
- [TokenVesting security review, Pashov, April 2023](https://github.com/bio-xyz/vesting-contracts/blob/main/audits/2023-04-pashov.md) — origin of the vesting input bounds
- [Audits index, Bio Protocol documentation](https://docs.bio.xyz/bio/developers/audits)

### Analyzed source

- [bio-xyz/vesting-contracts](https://github.com/bio-xyz/vesting-contracts) — analyzed at commit [`b6bb5a8252259e6679a0e737c72d53d795530397`](https://github.com/bio-xyz/vesting-contracts/tree/b6bb5a8252259e6679a0e737c72d53d795530397), 2026-09-22, for the `createVestingSchedule` signature and bounds quoted above

### Related articles

- [Cyfrin First Fight 42 - Snowman Merkle Airdrop]({{site.url_complet}}/2025/07/11/cyfrin-first-fight-42-snowman-merkle-aidrop/)
- [Cross-Chain Bridge Hacks - What Went Wrong and What Was Learned]({{site.url_complet}}/2026/07/31/cross-chain-bridge-hacks/)
