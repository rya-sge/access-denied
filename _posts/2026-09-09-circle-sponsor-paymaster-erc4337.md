---
layout: post
title: "Inside Circle's SponsorPaymaster — How a Verifying Paymaster Is Built"
date:   2026-09-09
lang: en
locale: en-GB
categories: blockchain ethereum solidity wallet
tags: blockchain ethereum solidity erc-4337 account-abstraction paymaster smart-wallet gasless entrypoint circle
description: A line-by-line reading of Circle's SponsorPaymaster, the ERC-4337 v0.7 verifying paymaster behind gasless Circle wallets, and the design choices behind it.
image: /assets/article/blockchain/ethereum/erc-4337/2026-09-09-circle-sponsor-paymaster-mindmap.png
isMath: false
---

A paymaster is the part of ERC-4337 that decides someone else pays. `SponsorPaymaster`, in Circle's `buidl-wallet-contracts` repository, is the contract behind the gasless experience of Circle's programmable wallets: the end user signs an operation, Circle's backend agrees to fund it, and the on-chain contract does nothing more than check that the agreement is genuine.

That split is the whole design. The policy question, whether this particular user deserves free gas, is answered off-chain by a service that can look at subscriptions, quotas, credit-card charges, or a free tier. The on-chain contract answers a much narrower question: did one of my trusted keys sign exactly this operation, and is the signature still inside its validity window? Everything in the 200 lines of `SponsorPaymaster.sol` below its licence header exists to make that second question cheap, unambiguous, and impossible to answer "yes" twice for the same operation.

This article reads the contract as it stands at commit `3c47aa94`, walks through the byte layout it parses, the payload it signs, and the failure modes it deliberately does not revert on, then looks at the plumbing it inherits from `BasePaymaster` and at the operational surface an owner is left holding.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Where a paymaster sits in ERC-4337

Under [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337), a user does not send a transaction. They sign a `UserOperation`, hand it to a bundler, and the bundler packs it into a call to the singleton `EntryPoint`. The EntryPoint runs every operation in two phases. The **validation phase** asks each account "is this authorised?" and each paymaster "will you pay?", under storage and opcode restrictions tight enough that a bundler can simulate the answer off-chain. The **execution phase** then runs the account's call data and settles the gas.

Settlement is the reason paymasters exist at all. If no paymaster is named, the account itself must have ETH deposited in the EntryPoint. If a paymaster is named and its validation succeeds, the EntryPoint debits the **paymaster's** deposit instead, and the account pays nothing. The user needs no ETH, which is exactly the experience Circle sells.

The contract analysed here targets **EntryPoint v0.7**, deployed at `0x0000000071727De22E5E9d8BAf0edAc6f37da032`. That version replaced v0.6's loose `UserOperation` struct with `PackedUserOperation`, packing gas fields into `bytes32` pairs and folding the paymaster's own gas limits into the `paymasterAndData` field. Both changes show up directly in the contract's parsing code.

![Inheritance and responsibility split: SponsorPaymaster extends BasePaymaster, which itself implements IPaymaster and the OpenZeppelin upgradeable Initializable, UUPS, Ownable and Pausable modules, and talks to the EntryPoint singleton for deposits and stake]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/sponsor-paymaster-contract-layers-concept.png)

## Two contracts, two concerns

The repository splits the paymaster in half, and the split is worth naming because it is the reason the policy contract is short enough to read in one sitting.

`BasePaymaster` is an abstract contract holding everything that is true of any paymaster:

- **The EntryPoint binding.** `IEntryPoint public immutable ENTRY_POINT`, set in the constructor, plus `_requireFromEntryPoint()` which reverts with `UnauthorizedCaller` on any other caller. This guard is the single most important access control in an ERC-4337 component, since `validatePaymasterUserOp` is otherwise an open door to a free signature oracle.
- **The money.** `deposit()`, `getDeposit()`, `getDepositInfo()`, `withdrawTo()` for the gas balance, and `addStake()`, `unlockStake()`, `withdrawStake()` for the separate locked stake.
- **The lifecycle.** UUPS upgradeability with `_authorizeUpgrade` gated on `onlyOwner`, `OwnableUpgradeable` for that owner, and `PausableUpgradeable` for a kill switch.
- **A storage gap.** `uint256[50] private __gap`, so a future version of the base contract can add state without shifting whatever the child declared.

`SponsorPaymaster` adds only the policy: a set of trusted signers, the code that parses the paymaster's slice of the operation, the code that reconstructs the signed hash, and the verification itself. The single overridden hook is `_validatePaymasterUserOp`, and it is declared `view`, which is a small but real signal: sponsorship decisions in this design write nothing to storage.

## The `paymasterAndData` envelope

`paymasterAndData` is a single `bytes` field in the operation, and v0.7 gives its first 52 bytes a meaning the EntryPoint itself reads. The contract documents its own reading of the layout in a comment above `parsePaymasterAndData`:

```solidity
uint256 private constant PAYMASTER_VALIDATION_GAS_OFFSET = 20;
uint256 private constant PAYMASTER_POSTOP_GAS_OFFSET = 36;
uint256 private constant TIMESTAMP_START = 52;
uint256 private constant SIGNATURE_START = 116;
```

Laid out, the field is:

```text
 0                20                36                52                              116
 +----------------+-----------------+-----------------+-------------------------------+---------+
 | paymaster addr | verificationGas | postOpGasLimit  | abi.encode(validUntil,         | ECDSA   |
 |    20 bytes    |    16 bytes     |    16 bytes     |            validAfter)         |   sig   |
 +----------------+-----------------+-----------------+-------------------------------+---------+
        EntryPoint parses these 52 bytes         |          paymaster-specific data
```

The first three fields belong to the EntryPoint: it slices the address to route the call, and the two `uint128` gas limits to bound `validatePaymasterUserOp` and `postOp` respectively. `parsePaymasterAndData` re-reads those same bytes, and that redundancy is deliberate, because those two values then go into the signed hash.

The time window is `abi.encode`d rather than packed, so two `uint48` values occupy 64 bytes rather than 12. It costs 52 bytes of calldata per operation, and it makes the offsets trivially readable, which is the trade the contract accepts.

One consequence of using calldata slices: a `paymasterAndData` shorter than 116 bytes makes the slice expression revert. The EntryPoint wraps that as `FailedOpWithRevert` with reason `"AA33 reverted"`, and the bundler drops the operation. Malformed input fails loudly rather than silently recovering a garbage signer.

## What the signature commits to

`getHash` is the heart of the contract, and the interesting part is the list of things it covers:

```solidity
return keccak256(
    abi.encode(
        userOp.packUpToPaymasterAndData(),
        paymasterVerificationGasLimit,
        paymasterPostOpGasLimit,
        block.chainid,
        address(this),
        validUntil,
        validAfter
    )
);
```

`packUpToPaymasterAndData` is a small library function in `PaymasterUtils` that mirrors the EntryPoint's own operation hashing, minus the two trailing fields:

```solidity
return abi.encode(
    sender, nonce, hashInitCode, hashCallData,
    accountGasLimits, preVerificationGas, gasFees
);
```

The obvious omission is `paymasterAndData` itself, which cannot be included because it is where the signature lives. The less obvious omission is `userOp.signature`: the account's own authorisation is not covered. That is intentional, and it matches the reference `VerifyingPaymaster` in the account-abstraction repository: the paymaster agrees to fund a specific action by a specific account, and does not endorse one particular way of authorising it.

Everything a bundler could profitably tamper with **is** covered. `gasFees` and `accountGasLimits` are in the hash, so a bundler cannot inflate the price and bill the sponsor for the difference. `preVerificationGas` is in the hash. The paymaster's own two gas limits are in the hash, so a bundler cannot hand the paymaster a larger validation budget than the service agreed to fund.

### The replay surface

Four values in the hash define exactly how far a sponsorship signature travels.

| Value | What it prevents |
|-------|------------------|
| `block.chainid` | Replaying a Polygon sponsorship on Arbitrum. The contract is deployed at the same address on every chain, so without this the same signature would verify everywhere. |
| `address(this)` | Replaying against a second paymaster that shares a verifying signer. |
| `userOp.sender` | Redirecting the sponsorship to a different account. |
| `userOp.nonce` | Reusing it for a second operation from the same account. The EntryPoint's `NonceManager` guarantees a nonce is consumed once, so a signature bound to one is single-use. |

The test suite checks the last of these directly: after a successful validation it bumps `userOp.nonce` from 28 to 29 and re-submits, and the same signature now recovers a different address and fails.

What is **not** in the hash is the EntryPoint address. It does not need to be under normal operation, because `ENTRY_POINT` is immutable in the implementation and `address(this)` pins the proxy. It becomes relevant only in one scenario, discussed under upgradeability below.

### The prefix

The digest is wrapped with `MessageHashUtils.toEthSignedMessageHash`, giving the classic `\x19Ethereum Signed Message:\n32` prefix rather than an EIP-712 typed-data domain. The prefix keeps a sponsorship signature from ever being mistaken for a transaction, and the chain id and contract address that EIP-712 would put in a domain separator are already in the payload. The cost is legibility: a signer using this scheme sees an opaque 32-byte blob rather than a structured message, which matters little for a backend HSM and would matter a lot for a human wallet prompt.

## Validation returns, it does not revert

```solidity
(address recovered, ECDSA.RecoverError error,) = ECDSA.tryRecover(hash, signature);
if (error != ECDSA.RecoverError.NoError || !verifyingSigners.contains(recovered)) {
    return ("", _packValidationData(true, validUntil, validAfter));
}
return ("", _packValidationData(false, validUntil, validAfter));
```

Two choices are packed into those five lines.

**`tryRecover` rather than `recover`.** The `try` variant returns an error enum instead of reverting, so a signature of the wrong length, a malleable `s` value, or a zero recovery all produce the same outcome as a signature by the wrong key.

**The failure is reported, not thrown.** `_packValidationData(true, ...)` sets the low bit of the returned `validationData`, which the EntryPoint reads as `SIG_VALIDATION_FAILED` and converts into `FailedOp(opIndex, "AA34 signature error")`. ERC-4337 requires this distinction, because a revert inside validation is an unexpected condition that damages the paymaster's bundler reputation, while a returned signature failure is the normal way to say no. The contract's own comment says as much: *don't revert on signature failure: return SIG_VALIDATION_FAILED*.

The time window rides along in both branches. `_packValidationData` places `validUntil` at bit 160 and `validAfter` at bit 208, and the EntryPoint compares them against `block.timestamp`, rejecting with `"AA32 paymaster expired or not due"` when the operation is outside the window. Note that the window is taken from the calldata blob in both branches, including the failure branch, which is harmless because the failure bit already decides the outcome.

![Decision path through _validatePaymasterUserOp: the paused check and the EntryPoint caller check revert, a short calldata blob reverts in the slice, a bad signature returns a packed sigFailed flag that the EntryPoint reports as AA34, and a valid signature still has to pass the AA32 time-window check]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/sponsor-paymaster-validation-workflow.png)

## The signer set, and why the paymaster must be staked

Trusted signers live in an `EnumerableSet.AddressSet`, which the deployed bytecode places at storage slot 50, immediately after the base contract's 50-slot gap. `addVerifyingSigners` and `removeVerifyingSigners` are `onlyOwner whenNotPaused` and revert on a duplicate or a missing entry, so a batch is all-or-nothing rather than partially applied.

A set rather than a single address is what makes key rotation possible without downtime: add the new signer, wait for signatures from the old one to fall outside their validity windows, remove the old signer. The legacy version of this contract, still visible in the ABI of the Hardhat deployments under `deployments/`, had a single `verifyingSigner` address and a `setVerifyingSigner` setter, where rotation meant a window in which one of the two keys was not accepted.

The set lookup has a consequence that is easy to miss. `verifyingSigners.contains(recovered)` reads the paymaster's **own** storage during the validation phase, and [ERC-7562](https://eips.ethereum.org/EIPS/eip-7562), the validation-rules companion to ERC-4337, only permits an entity to touch its own storage slots during validation if that entity is **staked** with the EntryPoint. An unstaked deployment would have its operations rejected by conforming bundlers before they ever reached the chain. `BasePaymaster.addStake` exists for precisely this reason, and the repository's README makes calling it a mandatory post-deployment step.

## `postOp` is never called

Both validation branches return an empty `context`. In EntryPoint v0.7, the post-execution path only calls `postOp` when the context returned by validation is non-empty, so this paymaster's `postOp` hook is dead code on the happy path, and `BasePaymaster._postOp` is an empty body accordingly.

Nothing is lost by it. A paymaster only needs `postOp` when it has to settle something after the fact, which is what an ERC-20 paymaster does when it pulls tokens at the measured gas cost. The repository clearly anticipated that: `PaymasterUtils` declares a `ChargeMode` enum with `GAS_ONLY`, `FREE`, `FEE_ONLY` and `FEE_AND_GAS`, and carries a long comment working through a Chainlink `ETH/USDC` conversion down to token subunits. None of it is referenced by `SponsorPaymaster`, which implements the `FREE` path alone. The scaffolding for the charging modes is present; the contract that would use it is not in this repository.

Skipping `postOp` also removes a class of failure. A reverting `postOp` forces the EntryPoint to undo the execution and call the hook a second time in `postOpReverted` mode, and a paymaster that never returns a context never enters that path.

![Sponsored UserOperation from off-chain signing to on-chain verification: the wallet sends an unsigned operation to Circle's service, which applies policy, signs getHash with a verifying key, and returns paymasterAndData; the bundler simulates and calls handleOps, and the EntryPoint runs paymaster validation before execution]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/sponsor-paymaster-sponsorship-sequence.png)

## Upgradeability and the immutable EntryPoint

The contract is deployed behind an `ERC1967Proxy` with UUPS upgrade logic in the implementation. Three details follow from that.

**The constructor is not the initialiser.** `ENTRY_POINT` is `immutable`, so it is baked into the implementation's bytecode rather than stored in the proxy. The constructor carries the OpenZeppelin `@custom:oz-upgrades-unsafe-allow constructor` annotation to permit it, and calls `_disableInitializers()` so the implementation cannot be initialised directly. Owner and signers arrive later through `initialize`, invoked in the proxy's constructor.

**Changing the EntryPoint means a new implementation.** Because the address is immutable, there is no setter. Migrating to EntryPoint v0.8 would mean deploying a fresh `SponsorPaymaster` implementation against the new address and calling `upgradeToAndCall` on the proxy, which is exactly what `testUpgradeToNewEntryPoint` exercises.

**And that is where the omission of the EntryPoint address from `getHash` becomes visible.** Nonce uniqueness is enforced per EntryPoint, by each EntryPoint's own `NonceManager`. A signature issued while the proxy pointed at v0.7 binds a `(sender, nonce)` pair that a different EntryPoint would consider unused, and the signed payload contains nothing that distinguishes the two. The operational answer is the same one that covers a suspected signer compromise: rotate the signer set, or let outstanding validity windows expire, before repointing the proxy. Short windows make this a non-issue in practice, which is presumably why the field was left out.

## Operating the contract

The owner holds a wide set of powers, and the pause modifier covers more functions than a reader might expect. `pause()` sets a flag that `whenNotPaused` checks on `validatePaymasterUserOp`, `postOp`, `deposit`, `receive`, `withdrawTo`, `addStake`, `unlockStake`, `withdrawStake`, `addVerifyingSigners` and `removeVerifyingSigners`. Three consequences follow:

- **Sponsorship stops by reverting, not by declining.** Validation reverts with `EnforcedPause` rather than returning a signature failure, so operations already in the alt-mempool fail as `"AA33 reverted"` and count against the paymaster's reputation with bundlers.
- **A paused paymaster cannot be topped up.** Both `deposit()` and the `receive()` fallback are gated, and the test suite asserts that a plain ETH transfer to a paused contract fails.
- **It cannot be drained either.** `withdrawTo` is gated too, so a pause freezes the deposit in both directions until the owner unpauses.

The one function that stays open is the upgrade path: `_authorizeUpgrade` carries `onlyOwner` and no pause check.

The contract emits no events of its own. Adding or removing a verifying signer, the single most security-relevant state change available, produces no log. Monitoring signer rotation means reading `getAllSigners()` on a schedule or decoding calldata, and the same applies to reconstructing the history of the set after the fact.

Ownership is a single address, and it can upgrade the implementation, replace the signer set, pause the contract, and withdraw the entire deposit. A multisig or a timelock in that role is doing most of the security work.

## Deployment

`script/012_DeploySponsorPaymaster.s.sol` deploys both the implementation and the proxy with `salt: 0` through Foundry's CREATE2 path, guarded by an `EXPECTED_*_ADDRESS.code.length == 0` check so a re-run on an already-deployed chain is a no-op. The expected addresses are constants in `script/000_ContractAddress.sol`:

```solidity
address constant ENTRY_POINT = 0x0000000071727De22E5E9d8BAf0edAc6f37da032;
address constant PAYMASTER_ADDRESS = 0x36058Cc257967db1912FC276F9CBEC072CD572cb;
address constant PAYMASTER_PROXY_ADDRESS = 0x03dF76C8c30A88f424CF3CBBC36A1Ca02763103b;
```

The mainnet and Polygon deployments recorded under `broadcast/` were instead issued as raw `cast send` calls to the canonical deterministic deployer at `0x4e59b44847b379578588920cA78FbF26c0B4956C`, with the ready-made calldata in `script/cmd/`. Either route yields the same address on every chain, which is what lets a wallet SDK hard-code one paymaster address across the eight chain ids recorded under `broadcast/`: mainnet, Sepolia, Polygon, Amoy, Arbitrum, Arbitrum Sepolia, Avalanche and Fuji.

Deployment leaves the contract non-functional on purpose. The proxy is initialised with an **empty** signer array, as the constructor calldata in `script/cmd/DeploySponsorPaymasterProxy` shows, so every signature fails until the owner calls `addVerifyingSigners` and `addStake` from the block explorer. The README still names the legacy `setVerifyingSigner` at that step, which no longer exists in the contract.

## Conclusion

`SponsorPaymaster` is a small contract because it delegates the hard part. The question of who deserves free gas is a business question with no on-chain answer, so the design pushes it entirely to an off-chain service and keeps only the cryptographic residue: an ECDSA check against a rotatable signer set, a validity window, and a hash whose contents fix the operation, the chain, the paymaster and the account nonce.

The parts that repay attention are the ones that are easy to get wrong elsewhere. Returning `SIG_VALIDATION_FAILED` instead of reverting keeps the paymaster in good standing with bundlers. Covering both paymaster gas limits in the signed payload closes the gap a bundler could otherwise use to bill a larger validation budget than the service agreed to. Returning an empty context removes the `postOp` path and its `postOpReverted` re-entry entirely. And reading the signer set during validation is what makes staking a hard requirement rather than an optional reputation boost.

The residual risk sits off-chain and in the owner key. A compromised verifying signer drains the deposit up to whatever the validity windows allow, and a compromised owner key does so directly, or replaces the implementation. Neither is a flaw in the contract. Both are the trust this design deliberately places off-chain, in a service and a key rather than in code, and the contract at least makes it obvious where that trust sits.

![Mindmap of Circle's SponsorPaymaster covering its role in ERC-4337, the BasePaymaster plumbing and SponsorPaymaster policy split, the paymasterAndData byte layout, what the signed payload commits to, the validation outcome encoding, and the operational surface]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/2026-09-09-circle-sponsor-paymaster-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Paymaster** | An ERC-4337 contract that agrees to pay an operation's gas from its own EntryPoint deposit, so the account needs no ETH. |
| **Verifying paymaster** | A paymaster whose sponsorship decision is made off-chain and conveyed on-chain as a signature by a trusted key, which is the pattern `SponsorPaymaster` implements. |
| **`PackedUserOperation`** | The EntryPoint v0.7 operation struct, with gas limits and fees packed into `bytes32` pairs and the paymaster's gas limits folded into `paymasterAndData`. |
| **`paymasterAndData`** | The operation field carrying the paymaster address, its two gas limits, and any paymaster-specific data. Here that data is a validity window plus an ECDSA signature. |
| **`validationData`** | The packed `uint256` a paymaster returns: a signature-failure bit, `validUntil` at bit 160, and `validAfter` at bit 208. |
| **Deposit** | ETH the paymaster holds inside the EntryPoint, debited for actual gas cost. Freely withdrawable, and distinct from the stake. |
| **Stake** | Separately locked ETH subject to an unstake delay. ERC-7562 requires it before an entity may read its own storage during validation. |
| **`context`** | The blob validation passes to `postOp`. An empty context means the EntryPoint skips `postOp` altogether. |
| **Verifying signer** | An address in the contract's `EnumerableSet` whose ECDSA signature over `getHash` authorises sponsorship. Managed by the owner. |
| **UUPS** | An upgrade pattern where the upgrade logic lives in the implementation, gated here by `_authorizeUpgrade` under `onlyOwner`. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| Only the EntryPoint can trigger paymaster validation or `postOp`. | `_requireFromEntryPoint()` on both external entry points, comparing against the immutable `ENTRY_POINT`. | The guard is removed, turning the contract into a free signature oracle. |
| A sponsorship signature is valid for exactly one operation. | `userOp.nonce` and `userOp.sender` are inside `getHash`, and the EntryPoint's `NonceManager` consumes each nonce once. | The nonce leaves the signed payload, or the operation is submitted through a different EntryPoint with its own nonce space. |
| A sponsorship signature is valid on one chain and one paymaster only. | `block.chainid` and `address(this)` are inside `getHash`. | Either value leaves the payload, which matters because the contract is deployed at the same address on every chain. |
| A bundler cannot enlarge the gas budget the sponsor agreed to fund. | `accountGasLimits`, `preVerificationGas`, `gasFees` and both paymaster gas limits are inside `getHash`. | Any of those fields is dropped from the signed payload. |
| A bad signature costs the paymaster no reputation. | `ECDSA.tryRecover` plus `_packValidationData(true, ...)`, returning rather than reverting. | `recover` replaces `tryRecover`, or the failure branch reverts. |
| `postOp` is never called. | Both validation branches return an empty `context`, which EntryPoint v0.7 treats as "no post-op". | A future version returns a non-empty context without implementing `_postOp`. |
| Only the owner changes signers, upgrades, pauses, or moves funds. | `onlyOwner` on every mutating function, and `_authorizeUpgrade` gated the same way. | The owner key is compromised, which is equivalent to compromising the deposit and the implementation. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| A `paymasterAndData` shorter than 116 bytes reverts inside a calldata slice rather than failing validation cleanly. | Build the field from the four fixed-width parts plus the signature, and validate its length before submitting. |
| Pausing reverts inside validation rather than returning a signature failure, producing `"AA33 reverted"` for operations already in the mempool. | Treat a pause as a mempool-invalidating event: stop issuing signatures first, and expect bundler-side reputation effects on in-flight operations. |
| `deposit()` and `receive()` are both `whenNotPaused`, so a paused paymaster cannot be topped up. | Unpause before funding. Do not rely on being able to refill a paused contract during an incident. |
| `withdrawTo` is also `whenNotPaused`, so pausing freezes the deposit in both directions. | Plan incident response around unpausing to withdraw, and hold the owner key somewhere that permits that under pressure. |
| No event is emitted when a verifying signer is added or removed. | Monitor `getAllSigners()` on a schedule, or decode owner calldata, rather than subscribing to logs. |
| The contract must be staked with the EntryPoint, not merely funded, because validation reads its own storage. | Verify `getDepositInfo()` reports both a deposit and a stake with a sane unstake delay before routing traffic to it. |
| `ENTRY_POINT` is immutable, so an EntryPoint migration is an implementation upgrade. | Rotate the signer set or drain outstanding validity windows around the upgrade, since the signed payload does not name the EntryPoint. |
| The README's post-deployment step names `setVerifyingSigner`, which the current contract does not have. | Call `addVerifyingSigners(address[])` instead. |
| Deployment initialises the signer set to an empty array. | Expect every operation to fail with `AA34` until the owner adds at least one signer. |

## Frequently Asked Questions

**Q: Why does the paymaster return a packed failure value on a bad signature instead of reverting?**

ERC-4337 draws a sharp line between a validation that says "no" and a validation that malfunctions. A returned `validationData` with the signature-failure bit set is the protocol's normal way to decline, and the EntryPoint converts it into `FailedOp(opIndex, "AA34 signature error")`. A revert is treated as an unexpected condition and counts against the paymaster's reputation with bundlers, which can lead to throttling or a ban from the alt-mempool. Since a verifying paymaster will legitimately see stale, expired and forged signatures as part of normal operation, reverting on each one would be self-harming.

**Q: What does `getHash` deliberately leave out, and why is each omission safe?**

Three things:

- **`paymasterAndData` itself**, because that is where the signature is written. `packUpToPaymasterAndData` stops one field short of it, and the paymaster gas limits it would have covered are passed in as separate arguments instead.
- **`userOp.signature`**, the account's own authorisation. The paymaster is funding an action by a named account at a named nonce, not endorsing one particular way of authorising it, and the sender and nonce are both covered.
- **The EntryPoint address.** Under normal operation `address(this)` and the implementation's immutable `ENTRY_POINT` pin it indirectly. It matters only if the proxy is later upgraded to point at a different EntryPoint, since nonce uniqueness is per-EntryPoint.

**Q: Why does this contract need to be staked, when its deposit is what pays for gas?**

Deposit and stake answer different questions. The deposit is the money the EntryPoint debits for gas. The stake is collateral that ERC-7562 requires before an entity may read its **own** storage during the validation phase, because such an entity can invalidate many pending operations at once with a single state change and a bundler needs something to slash against. `_validatePaymasterUserOp` calls `verifyingSigners.contains(recovered)`, a read of the paymaster's own storage, so a conforming bundler will reject its operations if it is unstaked. Funding without staking produces a paymaster that looks solvent and is never used.

**Q: What can an attacker do with a stolen sponsorship signature?**

Almost nothing. The signature binds the sender, the nonce, the call data hash, the gas fields, the chain id and the paymaster address. Submitting it from another account fails; submitting it on another chain fails; submitting it a second time fails once the nonce is consumed. The realistic use is front-running the legitimate submission with the identical operation, which executes exactly what the sponsor already agreed to pay for. This is why the contract can afford to put the signature in public calldata.

**Q: Why is `postOp` never called, and what would have to change for it to be?**

Both validation branches return an empty `context`, and EntryPoint v0.7 only invokes `postOp` when the context is non-empty. For pure sponsorship there is nothing to settle afterwards, so returning empty is both correct and cheaper. It would change for a charging paymaster: an ERC-20 variant has to measure the actual gas cost and pull the equivalent in tokens, which can only happen after execution. The repository already carries the scaffolding for that in `PaymasterUtils`, whose `ChargeMode` enum and Chainlink price-feed comment describe a token-charging design that `SponsorPaymaster` does not implement.

**Q: Combining two parts of the design, why is the choice of an `EnumerableSet` over a single signer address both an availability improvement and an extra staking obligation?**

The set makes key rotation continuous. With a single `verifyingSigner`, replacing the key invalidates every signature already issued under the old one, so there is a gap in which sponsorship is broken; the legacy version of this contract worked that way. A set lets the owner add the new key, keep signing with the old one until outstanding windows expire, then remove it, with no interruption. The cost is that the lookup is a read of the paymaster's own storage during validation, which is exactly the access ERC-7562 gates behind a stake. A design that carried the authorised signer in the implementation as an immutable would avoid the storage read, and would give up rotation entirely.

**Q: If the paymaster is paused during an incident, what can and cannot the owner still do?**

The owner can unpause, transfer ownership, and upgrade the implementation, since `_authorizeUpgrade` carries no pause check. Everything touching money or policy is gated: `deposit`, `receive`, `withdrawTo`, `addStake`, `unlockStake`, `withdrawStake`, and both signer-management functions all carry `whenNotPaused`. So a paused paymaster can be neither refilled nor emptied, and its signer set cannot be corrected while paused. Any response that involves moving funds or rotating a compromised signer must go through an unpause first.

## References

### Analyzed source

- [circlefin/buidl-wallet-contracts](https://github.com/circlefin/buidl-wallet-contracts) — analyzed at commit [`3c47aa94a8422bbd69a5e71ef21dbaa5ff6e1939`](https://github.com/circlefin/buidl-wallet-contracts/tree/3c47aa94a8422bbd69a5e71ef21dbaa5ff6e1939), 2026-09-09. Files read: `src/paymaster/v1/permissioned/SponsorPaymaster.sol`, `src/paymaster/BasePaymaster.sol`, `src/utils/PaymasterUtils.sol`, `src/utils/CalldataUtils.sol`, `test/SponsorPaymaster.t.sol`, `script/012_DeploySponsorPaymaster.s.sol`, `script/000_ContractAddress.sol`.

### Specifications

- [ERC-4337: Account Abstraction Using Alt Mempool](https://eips.ethereum.org/EIPS/eip-4337)
- [ERC-7562: Account Abstraction Validation Scope Rules](https://eips.ethereum.org/EIPS/eip-7562)
- [ERC-1967: Proxy Storage Slots](https://eips.ethereum.org/EIPS/eip-1967)
- [ERC-1822: Universal Upgradeable Proxy Standard (UUPS)](https://eips.ethereum.org/EIPS/eip-1822)
- [eth-infinitism/account-abstraction](https://github.com/eth-infinitism/account-abstraction) — the reference EntryPoint, `PackedUserOperation`, `UserOperationLib` and `Helpers.sol`

### Libraries and documentation

- [OpenZeppelin Contracts 5.x — Upgradeable proxies and storage gaps](https://docs.openzeppelin.com/contracts/5.x/upgradeable)
- [OpenZeppelin Contracts 5.x — `ECDSA` and `MessageHashUtils`](https://docs.openzeppelin.com/contracts/5.x/api/utils#cryptography)
- [OpenZeppelin Contracts 5.x — `EnumerableSet`](https://docs.openzeppelin.com/contracts/5.x/api/utils#EnumerableSet)
- [Circle Programmable Wallets documentation](https://developers.circle.com/w3s/programmable-wallets)

### Related articles

- [ERC-4337: Account Abstraction Using Alt Mempool]({{site.url_complet}}/2025/05/02/erc-4337-overview/)
- [SenderCreator in ERC-4337 — Deploying Accounts and Reading Counterfactual Addresses]({{site.url_complet}}/2026/07/23/sendercreator-entrypoint-erc4337-counterfactual-address/)
- [How Alchemy Implements Smart Wallets and Account Abstraction]({{site.url_complet}}/2026/07/30/alchemy-smart-wallet-account-abstraction/)
- [Rundler — Inside Alchemy's ERC-4337 Bundler]({{site.url_complet}}/2026/07/30/rundler-alchemy-erc4337-bundler/)
- [Nonce Management and CREATE2 in ERC-4337 Smart Wallets]({{site.url_complet}}/2026/02/17/nonce-management-create2-smart-wallets-erc4337/)
- [Native Account Abstraction on Aztec, Compared with ERC-4337]({{site.url_complet}}/2026/09/09/aztec-native-account-abstraction-vs-erc-4337/)
- [Inside Circle's UpgradableMSCA — A Modular Smart Contract Account Under ERC-6900]({{site.url_complet}}/2026/09/09/circle-upgradable-msca-erc6900/)
