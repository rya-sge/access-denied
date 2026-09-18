---
layout: post
title: "Bio Protocol Overview - DeSci Launchpad, BIO Token Economy and Open-Source DAO Contracts"
date:   2026-09-18
lang: en
locale: en-GB
categories: blockchain defi ethereum
tags: defi desci token staking airdrop merkle-tree governance ai-agent
series: bio-protocol
description: "How Bio Protocol funds biotech on-chain: USDC Ignition Sales, veBIO and BioXP allocation, a 1 % swap tax, and its audited token, vesting and airdrop contracts."
image: /assets/article/blockchain/defi/bio-protocol/2026-09-18-bio-protocol-overview-mindmap.png
isMath: false
---

[Bio Protocol](https://www.bio.xyz/) is a decentralised science (DeSci) platform that funds early-stage biotech research with tokens. Communities of patients, researchers and crypto users form *BioDAOs*, tokenise intellectual property as *IP-Tokens*, and, more recently, launch AI research agents (*BioAgents*) with their own tokens. The protocol was incubated by Molecule and is stewarded by the Bio.xyz Association; its native token is `BIO`, deployed on Ethereum, Base, BNB Chain and Solana.

This article gives an overview of the protocol as it stands in 2026: the assets it launches, the four-token economy (`BIO`, `vBIO`, `veBIO`, BioXP), the V2 launchpad with its Ignition Sales and Liquidity Engine, and the open-source repositories every BioDAO is built from: three Solidity projects for the token, vesting and Merkle airdrop, and one Solana governance program. It closes with the audit history, since the launchpad contracts themselves are not public and the six published reports are the only technical description of them.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What Bio Protocol funds

Bio describes itself as "a financial layer for funding and developing early-stage biotech". The protocol groups its activity into five verticals:

- **Explore**: scientific questions investigated with the BIOS assistant and OpenLabs.
- **Build**: projects prepared for funding in Buildspace.
- **Fund**: the Bio Launchpad.
- **Govern**: protocol and project decisions.
- **Monetize**: products commercialised through Biofy.

The launchpad is the part with on-chain mechanics, and the rest of this article concentrates on it.

Three kinds of asset are launched through it:

- **BioDAOs** are token-governed research communities focused on one therapeutic area. The documentation lists VitaDAO (longevity), HairDAO, CerebrumDAO, ValleyDAO (synthetic biology), AthenaDAO (women's health), CryoDAO, PsyDAO, Curetopia (rare diseases) and others. Each has a governance token (`VITA`, `HAIR`, `NEURON`, `GROW`, `ATH`, `CRYO`, `PSY`) listed in the [Bio token list](https://github.com/bio-xyz/tokenLists).
- **IP-Tokens (IPTs)**, a construction pioneered by Molecule, represent fractional governance rights over the intellectual property produced by a research project. The documentation is explicit that an IPT carries governance and information rights but no guaranteed financial return; whether IPT holders are paid on commercialisation is left to the IP owner.
- **BioAgents** are AI agents that perform research tasks (literature search, data analysis, hypothesis generation). They can be launched as independent projects with their own token and charge fees for their services. The reference implementation, [bio-xyz/BioAgents](https://github.com/bio-xyz/BioAgents), is an archived Bun/Elysia backend; the live product is BIOS at chat.bio.xyz.

![Bio Protocol layers: BIO locks into veBIO which accrues BioXP, BioXP weights Ignition Sale allocation, the sale seeds a Liquidity Engine pool and distributes BioDAO, IP and BioAgent tokens, while the open-source Token, TokenVesting and MerkleAirdrop contracts sit alongside]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-protocol-architecture-concept.png)

## The token economy

Four distinct units circulate in the protocol, and the documentation takes care to keep them apart.

### BIO

`BIO` is an ERC-20 on the EVM chains and an SPL token on Solana. The verified source of the Ethereum contract, `BioToken.sol`, is the same design as the open-source DAO token described later: a `MINTER_ROLE` with no cap, a `TRANSFER_ROLE`, and a one-way `enableTransfers()` switch. Its header records that it is a redeployment of an earlier contract at `0xd2cf1dC4Af7da92f849C2fF6A162b73cA3F4b331`, decided by a [Snapshot vote](https://snapshot.org/#/bioxyz.eth/proposal/0xdba4c882e33d8433b9238b9e3b6dc8d7be754c128aeeb511f27015b86bac0cbb). The initial supply was 3,320,000,000 tokens and the documentation describes it as uncapped, with the qualification that issuing more `BIO` would require deploying a new token contract to replace the current one.

The initial allocation, with six-year vesting schedules for team and investors, was:

- **Community, 56 %**: 20 % community auction, 6 % airdrop, 25 % ecosystem incentives and 5 % Molecule ecosystem fund.
- **Early backers, 13.6 %.**
- **Early contributors, 21.2 %.**
- **Advisors, 4.2 %.**
- **Molecule, 5 %.**

| Chain | Contract |
|-------|----------|
| Ethereum | `0xcb1592591996765Ec0eFc1f92599A19767ee5ffA` |
| Base | `0x226A2FA2556C48245E57cd1cbA4C6c9e67077DD2` |
| BNB Chain | `0x226a2fa2556c48245e57cd1cba4c6c9e67077dd2` |
| Solana | `bioJ9JTqW62MLz7UKHU69gtKhPpGi1BQhccj2kmSvUJ` |

The documented uses of `BIO` are staking (for governance and launch access), committing to launches, acting as the pair asset in project liquidity pools, paying for BioAgent services and obtaining ecosystem discounts.

### vBIO

`vBIO` is the vesting representation of `BIO`. It is not a wrapped token but the balance of a `TokenVesting` contract (described below), which exposes an ERC-20 interface whose `balanceOf` returns the holder's unreleased vested amount and whose `transfer` always reverts. On Ethereum it is split over two verified contracts: the **BIO Vesting Master** at `0x0d2ADB4Af57cdac02d553e7601456739857D2eF4`, which is the address the documentation lists as `vBIO`, and a subordinate **BIO Vesting Token** at `0x2141B47A1C7De6df073d23ff94F04d9fd2aaA9b3`. The master holds schedules of its own and adds the balances of an admin-managed list of external vesting contracts to its `balanceOf` and `totalSupply`, so a wallet's `vBIO` balance is the sum across both. `BIO` and `vBIO` together remain the governance tokens of the protocol until `veBIO` is adopted through a formal proposal. `vBIO` cannot be converted into `veBIO`.

### veBIO

`veBIO` is the vote-escrow token, following the model introduced by Curve's veCRV. Locking `BIO` for a duration between 1 week and 2 years mints a non-transferable balance:

```text
veBIO per BIO = weeks remaining in the lock / 104
```

The balance therefore decays linearly to zero as the lock approaches its end; an auto-renewal option resets the lock at regular intervals to keep it constant. Staking is initially available only on Base (`0xE1B48C0279Cd95D984f1290293116c45D049A3bD`; an Ethereum deployment also exists at `0xF91a12742Aa609d41513a137d3c36b749F56f40C`). Locked `BIO` cannot be withdrawn early. Besides future governance power, `veBIO` earns BioXP daily and entitles the holder to a pro-rata share of every new token launched through an Ignition Sale (see "Airdrops to veBIO stakers" below).

### BioXP

BioXP ("Bio Experiment Points") is a points system rather than a token. It is the priority layer of the launchpad: sales are open to anyone with USDC, but when a sale is oversubscribed the allocation is weighted by BioXP pledged. BioXP is earned three ways:

- **Staking `BIO`** (through `veBIO`), distributed automatically every day.
- **Staking ecosystem tokens** (IP-Tokens, BioAgent tokens, BioDAO tokens) with no lock but a two-week unstaking cooldown; these points must be claimed manually each day or they expire the next day. Seven multiplier levels tied to the staker's `veBIO` balance, plus a bonus during a token's first 60 days, scale the yield.
- **Instant mint**, spending `BIO` at a rate of 0.01 USD per point.

BioXP points expire 14 days after issuance, which the documentation presents as a deliberate anti-hoarding measure.

## Bio Protocol V2: the launchpad

V2 replaced the earlier curation and auction model with a fixed-price sale and a set of post-launch liquidity mechanisms. The V0 and V1 contracts it replaced are the ones audited in 2024 and early 2025, listed in the audit section. The stated philosophy is "launch and grow": low initial valuation, no large one-time raise, and funding that unlocks as the project gains market traction.

### The Ignition Sale

Every project, whether on the permissionless *Community Launch* track or the hand-picked *Curated Launch* track, is sold through an Ignition Sale with the same mechanics:

- **Denomination and price.** All sales are in USDC at a single fixed price; every participant pays the same.
- **Raise goal.** The sale succeeds only if committed USDC reaches the goal. Otherwise all USDC and pledged BioXP are returned, no tokens are issued and no pool is created.
- **Commitment.** USDC is locked until the sale closes. Pledging BioXP is optional; a participant who pledges none is treated as having pledged 1 BioXP, the lowest weight.
- **Oversubscription.** When commitments exceed the goal, each user's allocation is `min(user_points / total_points_pledged * tokens_for_sale, 0.005 * tokens_for_sale)`, and a single wallet may not buy more than 1 % of total supply. Excess USDC is refunded.
- **Vesting.** None for sale participants; tokens are liquid on claim.
- **Front-end requirement.** Commitments made directly against the contract from a wallet with no platform account are excluded at finalisation and refunded. The allocation logic depends on BioXP, which lives off-chain.

![Ignition Sale flow: commit USDC and optional BioXP, check the raise goal, compute pro-rata allocation capped at 0.5 % if oversubscribed, seed the AMM pool, apply the 1 % swap tax, airdrop to veBIO stakers and unlock team funding on FDV milestones]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-ignition-sale-workflow.png)

### The Liquidity Engine

After a successful sale, the Liquidity Engine creates a liquidity pool for the new token on a decentralised exchange. For a standard agent launch, the tokens sold to the public represent 37.5 % of supply and all the USDC raised is paired with the project token in the pool; a `BIO`/token pool is added later if the project meets its milestones. Two mechanisms then fund the project on an ongoing basis:

- **Limit-sell fundraising.** A reserved share of supply is deployed as concentrated liquidity at pre-set fully diluted valuation (FDV) thresholds, which acts as a ladder of limit sell orders. Proceeds unlock only when the price has held above a threshold for two weeks.
- **Secondary-market fee.** Every buy and sell on the project token carries a 1 % fee, split 70 % to the project treasury and 30 % to the Bio Protocol treasury. In the launchpad contracts audited by FYEO this is implemented in an `AgentToken` with `setProjectTaxRates` and `withdrawTax` functions.

### Airdrops to veBIO stakers

A percentage of every launched token's supply is airdropped to `veBIO` holders, pro rata to their balance with no cap: `allocation = veBIO_balance * airdrop_pool / total_veBIO`. The allocation follows an unlock schedule the documentation calls "rEUL-style", after Euler's reward token: 20 % is redeemable at the token generation event, the remaining 80 % unlocks linearly over six months, and redeeming before full vesting permanently forfeits the still-locked remainder of that allocation, which is burned.

## The open-source DAO contracts

The launchpad itself is closed source, but the three building blocks a BioDAO deploys on the EVM side are public Foundry projects under the [bio-xyz](https://github.com/bio-xyz) organisation. All three use Solidity 0.8.23, OpenZeppelin Contracts 4.x and share the same deployment pattern: an EOA deploys, grants operational roles to a multisig and calls `beginDefaultAdminTransfer(multisig)` from OpenZeppelin's `AccessControlDefaultAdminRules`, configured with a zero delay; the multisig then accepts. The revisions analysed here all date from 2025-01-31.

### Token.sol

The BioDAO governance token is a 40-line ERC-20 with `ERC20Burnable` and `AccessControlDefaultAdminRules`. Its distinguishing feature is a transfer gate that is closed at deployment and opened once, irreversibly:

```solidity
bool public transfersEnabled = false;

function enableTransfers() external onlyRole(DEFAULT_ADMIN_ROLE) {
    transfersEnabled = true;
}

function _beforeTokenTransfer(address from, address to, uint256 amount) internal virtual override {
    super._beforeTokenTransfer(from, to, amount);
    if (!transfersEnabled) {
        require(
            from == address(0) || from == owner() || hasRole(TRANSFER_ROLE, from),
            "ERC20: transfers not enabled"
        );
    }
}
```

While the gate is closed, only mints (`from == address(0)`), the default admin and holders of `TRANSFER_ROLE` can move tokens. Since the check is on `from` only, a burn by an ordinary holder is also blocked during that phase. `MINTER_ROLE` can mint without a cap: `ERC20Capped` is imported but never inherited. The deployment script grants `MINTER_ROLE` and `TRANSFER_ROLE` to the multisig, which is what lets the DAO distribute tokens to an auction or vesting contract before public trading opens.

The deployed `BIO` token differs from this template in its access-control stack only: it inherits `Ownable` and `AccessControlEnumerable` instead of `AccessControlDefaultAdminRules`, so `enableTransfers()` is `onlyOwner`, the `owner()` exempted by the transfer gate is the `Ownable` owner rather than the default admin, and ownership moves in one step with `transferOwnership` rather than through a two-step hand-over.

### TokenVesting and its Merkle variants

The vesting repository is a fork of Molecule's `token-vesting-contract` and is the code behind `vBIO`. Its central design decision is that the vesting contract *is* an ERC-20:

- `name`, `symbol`, `decimals` (fixed at 18), `totalSupply` and `balanceOf` are implemented; `totalSupply` is the sum of all unreleased schedule amounts and `balanceOf` is the holder's share of it.
- `transfer`, `transferFrom` and `approve` revert with `NotSupported()`; `allowance` returns 0.
- Creating a schedule emits `Transfer(address(0), beneficiary, amount)`; releasing or revoking emits `Transfer(beneficiary, address(0), amount)`, so wallets and governance tooling that index ERC-20 events see a virtual token being minted and burned.

Tokens are pushed to the contract rather than pulled; `getWithdrawableAmount()` is the balance not yet committed to a schedule, and `createVestingSchedule` reverts if it is insufficient. Only 18-decimal underlying tokens are accepted. A schedule has a start, a cliff, a duration, a slice period and an optional `revokable` flag, and the vested amount is computed in whole slices:

```solidity
uint256 timeFromStart = currentTime - vestingSchedule.start;
uint256 vestedSlicePeriods = timeFromStart / vestingSchedule.slicePeriodSeconds;
uint256 vestedSeconds = vestedSlicePeriods * vestingSchedule.slicePeriodSeconds;
uint256 vestedAmount = vestingSchedule.amountTotal * vestedSeconds / vestingSchedule.duration;
return vestedAmount - vestingSchedule.released;
```

Input bounds were added after the 2023 Pashov review:

- start no more than 30 weeks in the future;
- duration between 7 days and 50 years, and at least as long as the cliff;
- slice period between 1 and 60 seconds;
- amount at most `2**200`.

The two deployed `vBIO` contracts differ from the repository on the mitigation of the 2023 low finding on unbounded loops. Both cap a beneficiary at 100 schedules; the subordinate Vesting Token at `0x2141B47A…` also caps the contract at 500 schedules in total and keeps a `vestingSchedulesIds` array. The repository's current `main` has removed both caps, and the two error declarations remain unused.

The Vesting Master at `0x0d2ADB4A…` is the `MultiTokenVestingMerklePurchasable` variant that the repository keeps under `src/deprecated/`. It overrides `totalSupply()` and `balanceOf()` to add, for every address in `externalVestingContracts`, the corresponding value read from that contract. The list is edited by the admin with `addExternalVestingContract` and `removeExternalVestingContract`, and each balance query loops over it with an external call per entry.

Two roles exist. `DEFAULT_ADMIN_ROLE` can revoke, pause, withdraw the surplus and rotate the Merkle root; `VESTING_CREATOR_ROLE` can create schedules. Pausing stops the creation of schedules but not their release, a change made after the same review so that an admin cannot freeze beneficiaries' vested tokens. Release can be triggered by the beneficiary or by the owner on the beneficiary's behalf, and `releaseAvailableTokensForHolder` loops over every schedule of a holder.

`TokenVestingMerkle` adds `claimSchedule`: the beneficiary submits the full schedule parameters and a Merkle proof, the contract hashes them with the caller's address in the OpenZeppelin `StandardMerkleTree` double-hash format, verifies the proof with Solady's `MerkleProofLib`, marks the leaf as claimed and creates the schedule. `TokenVestingMerklePurchasable`, the variant the deployment script targets, additionally requires `msg.value == vTokenCost * amount / 1e18` and forwards the ETH to a configurable `paymentReceiver` with a low-level `call` before the schedule is written. The contract's own comments explain the purchase as a nominal payment made "for tax reasons". `setVTokenCost` is capped at 0.01 ETH per token.

![Merkle vesting sequence: the admin pushes tokens to the vesting contract, the beneficiary calls claimSchedule with a proof and ETH payment, the contract verifies the leaf, forwards the payment and mints a virtual balance, then releaseAvailableTokensForHolder transfers vested tokens and burns the virtual balance per schedule]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-vesting-merkle-claim-sequence.png)

### MerkleAirdrop.sol

The airdrop contract is a 99-line fork of a public minimal Merkle distributor, with `Ownable` and `ReentrancyGuard`. The leaf is `keccak256(bytes.concat(keccak256(abi.encode(who, amount))))`, verified again with Solady, and claim tracking is keyed on the root:

```solidity
mapping(bytes32 => mapping(address => bool)) private merkleToClaimed;

function claim(uint256 amount, bytes32[] calldata proof) external nonReentrant {
    if (!inMerkle(msg.sender, amount, proof)) revert NotInMerkleTree();
    if (hasClaimed(msg.sender)) revert AlreadyClaimed();
    if (merkleRoot == bytes32(0)) revert MerkleRootNotSet();
    merkleToClaimed[merkleRoot][msg.sender] = true;
    erc20.safeTransfer(msg.sender, amount);
    emit Claimed(msg.sender, amount);
}
```

Because the claimed flag lives under `merkleRoot`, calling `updateMerkleRoot` starts a fresh claim round in which every address in the new tree may claim once more, whether or not it claimed under the previous root. This differs from the vesting contract, where the flag is keyed on the leaf and survives a root rotation. The owner can also `withdraw` any amount of the token at any time.

The repository ships the off-chain side too: `creat_tree.js` builds the tree from a CSV of `Address,Amount in Wei` with OpenZeppelin's `StandardMerkleTree`, and `create_proof.js` emits the per-address proofs. The documentation describes the pipeline that produces the CSV for the `BIO` airdrop: auction contributor events, successful bids, `BIO` holder balances, then a distribution percentage.

## Security posture and audit history

Six reports are published, four by Krum Pashov or his audit group and two by FYEO, covering the vesting contract and every generation of the launchpad.

| Date | Auditor | Target | Findings |
|------|---------|--------|----------|
| 2023-04 | Pashov | `TokenVesting`, `TokenVestingMerkle` (Molecule fork) | 4 Medium, 2 Low |
| 2024-06 | Pashov Audit Group | `FairAuctionVesting` (Genesis swap of DAO tokens for `BIO` and `vBIO`) | 1 Medium, 6 Low |
| 2025-02 | Pashov Audit Group | DeSci Launchpad, Solana/Anchor program | 1 Critical, 2 High, 1 Medium, 8 Low |
| 2025-02 | FYEO | Bio Launchpad v0.1 curation program, Solana/Anchor | 1 Low, 4 Informational |
| 2025-03 | Pashov Audit Group | `Curation`, `LaunchFactory` in `launchpad-evm` | 1 Critical, 2 High, 2 Medium, 3 Low |
| 2025-07 | FYEO | `launchpad-agent-evm`: `Launch`, `LaunchFactory`, `AgentFactory`, `AgentToken`, `AgentVeToken`, `veBIO` | 1 Medium, 6 Low, 14 Informational |

The 2023 vesting review is the one that changed the code described above. Its four medium findings were:

- **M-01.** `revoke` forcibly pushes vested tokens and therefore fails for beneficiaries on the block list of tokens such as USDC. Acknowledged: the project documents that such tokens are not supported.
- **M-02.** Insufficient input validation in `createVestingSchedule`. Fixed with the bounds listed earlier.
- **M-03.** A payable `receive` and `fallback` with no way to withdraw ETH. Removed.
- **M-04.** A `whenNotPaused` modifier on release that let the owner freeze beneficiaries. Removed.

The two lows, an unbounded per-holder schedule loop and a modifier that accepted non-existent schedule IDs, were also fixed.

The two 2025 critical findings were both accounting errors in the launchpad rather than in the DAO contracts. On Solana, unclaimed tokens were locked permanently in a stats account. On the EVM `Curation` contract, an incorrect `vestingDuration` was passed to the vesting schedule, and a one-wei donation could permanently block `updateFundraiser()`.

The July 2025 FYEO review of the V2 agent launchpad is the most recent public description of the live system. Its single medium finding was a missing `_disableInitializers()` in a UUPS implementation, and its informational findings include a gas-exhaustion risk in `releaseAvailableTokensForHolder`, unbounded growth of a `locks[]` array in the vote-escrow contract, and unbounded `setProjectTaxRates`. The contract names in that scope, `AgentFactory`, `AgentToken` and `AgentVeToken`, match those of Virtuals Protocol's agent launch contracts, covered on this site in [Virtual Protocol, create co-ownership AI agents]({{site.url_complet}}/2024/12/05/virtual-protocol-architecture/).

Four themes recur across the six reports:

- unbounded loops over user-owned arrays;
- missing bounds on admin-set parameters;
- admin privileges that can strand user funds, such as withdraw-all, pause and root rotation;
- accounting drift between whitelist or Merkle totals and actual balances.

None of the DAO building blocks is upgradeable; the V2 launchpad is.

On Solana, one program is public: [bio-xyz/voter-stake-registry](https://github.com/bio-xyz/voter-stake-registry), a fork of the Mango DAO voter-weight add-in for spl-governance. It lets a realm accept deposits of several mints at configurable weights, with `None`, `Daily`, `Monthly`, `Cliff` and `Constant` lockup kinds and clawback-enabled grants. Bio's own change is an allowlist in `create_voter` that accepts a cross-program call from the Squads V4 multisig program and rejects every other CPI caller. The launchpad and auction programs audited in 2025 are not part of it.

## Conclusion

Bio Protocol applies a conventional DeFi toolkit, a vote-escrow token, a points system, fixed-price sales that seed AMM pools and a swap tax, to a narrow purpose: funding biotech research and its AI tooling. Its governance layer is still transitioning from `BIO`/`vBIO` voting to `veBIO`.

- **Assets.** BioDAOs, IP-Tokens and BioAgents are all launched through the same Ignition Sale and the same Liquidity Engine; what differs is who governs the resulting token and what it entitles the holder to.
- **Tokens.** `BIO` has a fixed deployed supply that only a replacement contract could extend; `vBIO` is a vesting balance exposed as a non-transferable ERC-20; `veBIO` decays linearly over a lock of at most two years; BioXP is off-chain, expires in 14 days and decides allocation only when a sale is oversubscribed.
- **Launchpad.** A sale either meets its USDC goal or refunds everything; participants get liquid tokens capped at 1 % of supply each; `veBIO` holders get a six-month-unlocking airdrop; the team's funding arrives through FDV-triggered limit orders and a 1 % swap fee split 70/30 with the protocol.
- **Contracts.** The public code is three small Foundry projects on OpenZeppelin 4.x with a shared multisig hand-over pattern. The vesting contract doubles as the `vBIO` governance token, and the airdrop contract resets its claim state on every root rotation.
- **Audits.** Six reports, two criticals, both in launchpad accounting; the DAO building blocks have had no high-severity finding. The launchpad code itself is not public, so the audit scopes are the only place its contract surface is documented.

![Mindmap of Bio Protocol covering launched assets, the BIO, vBIO, veBIO and BioXP tokens, the V2 launchpad mechanics, the open-source Token, Vesting and MerkleAirdrop contracts, and the audit history]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/2026-09-18-bio-protocol-overview-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **DeSci** | Decentralised science: funding, governing and commercialising research through token-holding communities rather than grants or venture capital. |
| **BioDAO** | A token-governed research community focused on one therapeutic area, such as VitaDAO or HairDAO, that sources, funds and governs projects. |
| **IP-Token (IPT)** | A token representing fractional governance and information rights over research intellectual property, with no guaranteed financial return. |
| **BioAgent** | An AI agent performing research tasks that can be launched as its own project with a token and charge fees for its services. |
| **veBIO** | Non-transferable vote-escrow balance minted by locking `BIO` for 1 week to 2 years; equals `BIO` locked times weeks remaining divided by 104. |
| **BioXP** | Off-chain points earned by staking, expiring after 14 days, that weight a participant's allocation when an Ignition Sale is oversubscribed. |
| **Ignition Sale** | Bio's fixed-price, USDC-denominated launch sale that refunds everything if the raise goal is not met. |
| **Liquidity Engine** | The post-sale mechanism that pairs raised USDC with the new token in an AMM pool and collects a 1 % fee on every swap. |
| **Limit-sell fundraising** | Concentrated liquidity placed at FDV milestones so that project funding unlocks only after the price holds above a threshold for two weeks. |
| **Virtual token** | An ERC-20 interface whose balance mirrors a vesting position and whose transfers always revert, used by `TokenVesting` to expose `vBIO`. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| `Token` transfers by ordinary holders are impossible until `enableTransfers()` is called, and possible forever after. | `_beforeTokenTransfer` check on `from`; `transfersEnabled` has no setter to `false`. | A future version adds a disable path or exempts additional senders. |
| `TokenVesting.totalSupply()` equals the sum of unreleased amounts of all non-revoked schedules, and `balanceOf(user)` its per-user share. | Every create, release and revoke updates `vestingSchedulesTotalAmount` and `holdersVestedAmount` in the same call. | A code path moves underlying tokens without touching both counters. |
| The vesting contract never commits more underlying tokens than it holds. | `_createVestingSchedule` reverts unless `getWithdrawableAmount() >= amount`; `withdraw` is limited to the same surplus. | The underlying token can be rebased, fee-on-transfer or otherwise change the contract's balance outside of `safeTransfer`. |
| A beneficiary can always release vested tokens, paused or not. | `release` and `releaseAvailableTokensForHolder` carry `nonReentrant` but not `whenNotPaused`. | `whenNotPaused` is reintroduced on release paths (the pre-2023 behaviour). |
| A Merkle vesting leaf is claimable at most once, across root rotations. | `claimed[leaf]` keyed on the leaf hash, not on the root. | The mapping is re-keyed on the root, as in `MerkleAirdrop`. |
| A `MerkleAirdrop` address claims at most once per root. | `merkleToClaimed[merkleRoot][who]`. | Nothing further: a root rotation deliberately resets the round. |
| Every vested amount is a whole number of slices of at most 60 seconds. | Bounds in `_createVestingSchedule` and the floor division in `_computeReleasableAmount`. | The slice bound is relaxed, reintroducing the rounding concern from Pashov M-02. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| `TokenVesting.transfer`, `transferFrom` and `approve` revert with `NotSupported()`; `allowance` returns 0. | Treat `vBIO` as a read-only balance for governance snapshots; do not route it through token routers, permit flows or ERC-20 allowance checks. |
| `TokenVesting` accepts only an 18-decimal underlying token and reverts in the constructor otherwise. | Do not reuse the contract for USDC-style 6-decimal tokens without modification. |
| Funding is push-based: the admin transfers tokens to the vesting or airdrop contract, and `createVestingSchedule` reverts if the surplus is insufficient. | Fund before creating schedules or opening claims, and monitor `getWithdrawableAmount()` when batching. |
| `Token` blocks burns by non-whitelisted holders while transfers are disabled. | Do not assume `burn()` works for all holders before `enableTransfers()`. |
| `releaseAvailableTokensForHolder` iterates over every schedule of the holder; the repository version has no cap, the deployed `vBIO` contracts cap at 100 per holder. | Cap the number of schedules per beneficiary off-chain when deploying from `main`; release schedules individually with `release(id, amount)` if a holder accumulates many. |
| The Vesting Master's `balanceOf` and `totalSupply` make one external call per registered external vesting contract. | Expect gas to grow with the list; a governance snapshot reading `vBIO` must query the master, not the subordinates, to avoid double counting or omissions. |
| `claimSchedule` on the purchasable variant requires `msg.value` to equal `vTokenCost * amount / 1e18` exactly and forwards it with a low-level `call`. | Compute the exact value client-side and ensure the `paymentReceiver` can receive ETH; a reverting receiver blocks all claims until it is changed. |
| `MerkleAirdrop.updateMerkleRoot` resets the per-address claim state. | Exclude already-paid addresses when building a replacement tree, or accept that they may claim again. |
| Ignition Sale commitments made outside the Bio front-end are refunded at finalisation. | Do not integrate the sale contract directly for end users; the BioXP weighting is applied off-chain. |
| `AccessControlDefaultAdminRules` is deployed with a zero delay and the admin transfer is only *begun* by the deploy script. | Verify on-chain that the multisig has called `acceptDefaultAdminTransfer()`; until then the deployer EOA is the admin. |

## Frequently Asked Questions

**Q: What is the difference between `vBIO` and `veBIO`?**

They share a prefix and nothing else. `vBIO` is the balance of a `TokenVesting` contract: it represents `BIO` that has been allocated to an address but not yet released, decreases as tokens vest and are claimed, and cannot be transferred or converted. `veBIO` is a vote-escrow position created by voluntarily locking already-liquid `BIO` for 1 week to 2 years; it decays with time remaining, earns BioXP and airdrop shares, and cannot be exited early. `vBIO` cannot be turned into `veBIO`.

**Q: How is a participant's allocation computed in an oversubscribed Ignition Sale?**

Each participant's share is `min(user_points / total_points_pledged * tokens_for_sale, 0.005 * tokens_for_sale)`, where `user_points` is the BioXP pledged (1 if none was pledged) and the second term caps any single allocation at 0.5 % of the tokens on sale; the documentation separately states that no wallet may buy more than 1 % of total supply. USDC committed beyond the resulting allocation is refunded. If the sale is not oversubscribed, allocation follows USDC committed and BioXP plays no role.

**Q: Why does the vesting contract implement the ERC-20 interface if transfers always revert?**

So that unvested allocations count for governance. Wallets, snapshot tools and governance frameworks read `balanceOf` and `Transfer` events; by emitting a mint on schedule creation and a burn on release, `TokenVesting` makes each beneficiary's unreleased amount visible as a token balance without letting it move. This is how `vBIO` served as a governance token alongside `BIO`.

**Q: A DAO rotates the Merkle root of its airdrop contract to add late recipients. What happens to addresses that already claimed?**

They can claim again. `MerkleAirdrop` records claims in `merkleToClaimed[merkleRoot][who]`, so a new root starts an empty claim map. An address present in both trees receives its amount twice unless the new tree omits it. The vesting contract behaves differently: `TokenVestingMerkle` records `claimed[leaf]` keyed on the leaf hash, so a leaf claimed under the old root stays claimed under the new one.

**Q: How does a launched project receive funding if sale participants' USDC goes into the liquidity pool?**

Through two post-launch channels rather than from the sale itself:

- A reserved share of supply is placed as concentrated liquidity at FDV milestones, so it is sold gradually as the price rises, and the proceeds unlock only once a milestone has held for two weeks.
- Every swap of the token pays a 1 % fee, 70 % of which goes to the project treasury and 30 % to Bio.

The design ties funding to sustained market traction instead of a one-time raise, which is the stated rationale of the "launch and grow" model.

**Q: Which parts of Bio Protocol can be audited from public code, and which cannot?**

The `Token`, `TokenVesting*` and `MerkleAirdrop` repositories are public, pinned in the references below, and the 2023 Pashov review of the vesting code is published as Markdown in the repository.

The launchpad repositories `launchpad-evm` and `launchpad-agent-evm`, the Solana programs, the `veBIO` staking contract and the `AgentToken` tax logic are private; their contract names, function names and known weaknesses are documented only in the FYEO and Pashov PDFs, and the documentation says the code "will be published and open-sourced in the near future".

**Q: Combining the token gate and the vesting design, how does a BioDAO distribute tokens before public trading opens?**

`Token` is deployed with transfers disabled, and the multisig holds `MINTER_ROLE` and `TRANSFER_ROLE`. It mints the supply and pushes tokens to the vesting and airdrop contracts; these transfers succeed because the sender is the multisig. Beneficiaries then claim schedules and accumulate `vBIO`-style balances.

They cannot yet receive released tokens in a transferable form, since a release is a `safeTransfer` *from the vesting contract*, which is blocked unless the multisig has granted that contract `TRANSFER_ROLE`. Once the DAO calls `enableTransfers()`, releases and airdrop claims go through, and the switch cannot be reversed.

## References

### Analyzed source

- [bio-xyz/token-contracts](https://github.com/bio-xyz/token-contracts) — analyzed at commit [`9031aa7de31d79fbd884404be3f463ff51cd8127`](https://github.com/bio-xyz/token-contracts/tree/9031aa7de31d79fbd884404be3f463ff51cd8127), 2026-09-18
- [bio-xyz/vesting-contracts](https://github.com/bio-xyz/vesting-contracts) — analyzed at commit [`b6bb5a8252259e6679a0e737c72d53d795530397`](https://github.com/bio-xyz/vesting-contracts/tree/b6bb5a8252259e6679a0e737c72d53d795530397), 2026-09-18
- [bio-xyz/airdrop-contracts](https://github.com/bio-xyz/airdrop-contracts) — analyzed at commit [`2b2f3fe8939f1209016df238eba9317b6a3c5fee`](https://github.com/bio-xyz/airdrop-contracts/tree/2b2f3fe8939f1209016df238eba9317b6a3c5fee), 2026-09-18
- [bio-xyz/voter-stake-registry](https://github.com/bio-xyz/voter-stake-registry) — analyzed at commit [`3dbc0ead93f64795f613d2cf8c50a839b50b1040`](https://github.com/bio-xyz/voter-stake-registry/tree/3dbc0ead93f64795f613d2cf8c50a839b50b1040), 2026-09-18

### Deployed verified sources

- [BIO token `0xcb1592591996765Ec0eFc1f92599A19767ee5ffA`](https://etherscan.io/address/0xcb1592591996765Ec0eFc1f92599A19767ee5ffA#code) — `BioToken.sol`, OpenZeppelin 4.9.0
- [vBIO, BIO Vesting Master `0x0d2ADB4Af57cdac02d553e7601456739857D2eF4`](https://etherscan.io/address/0x0d2ADB4Af57cdac02d553e7601456739857D2eF4#code) — `MultiTokenVestingMerklePurchasable`, OpenZeppelin 4.9.0, Solady
- [BIO Vesting Token `0x2141B47A1C7De6df073d23ff94F04d9fd2aaA9b3`](https://etherscan.io/address/0x2141B47A1C7De6df073d23ff94F04d9fd2aaA9b3#code) — `TokenVestingMerklePurchasable`, OpenZeppelin 4.9.0, Solady

### Documentation

- [Bio Protocol documentation](https://docs.bio.xyz/bio) — Introduction, Bio Protocol V2 (Launcher, Liquidity Engine, Staking and veBIO, BioXP), BIO Token, Developers
- [Basic Token Information](https://docs.bio.xyz/bio/introduction/bio-token/basic-token-information) — contract addresses and initial distribution
- [Launcher](https://docs.bio.xyz/bio/introduction/bio-protocol-v2/launcher) — Ignition Sale mechanics and allocation formula
- [Liquidity Engine](https://docs.bio.xyz/bio/introduction/bio-protocol-v2/liquidity-engine)
- [Staking BIO](https://docs.bio.xyz/bio/introduction/bio-protocol-v2/staking-and-vebio/staking-bio) and [veBIO Rewards](https://docs.bio.xyz/bio/introduction/bio-protocol-v2/staking-and-vebio/vebio-rewards)
- [Audits](https://docs.bio.xyz/bio/developers/audits) — index of the published reports
- [bio-xyz/tokenLists](https://github.com/bio-xyz/tokenLists) — BioDAO governance tokens and bidding tokens
- [bio-xyz/BioAgents](https://github.com/bio-xyz/BioAgents) — archived reference implementation of the BioAgents backend
- [Molecule token-vesting-contract](https://github.com/moleculeprotocol/token-vesting-contract) — upstream of `vesting-contracts`

### Audit reports

- [TokenVesting security review, Pashov, April 2023](https://github.com/bio-xyz/vesting-contracts/blob/main/audits/2023-04-pashov.md)
- [Bio Security Review (FairAuctionVesting), Pashov Audit Group, June 2024](https://499247139-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F3ba2jNU6BPQUl4RXgHor%2Fuploads%2FXm1EkQX20KCOrH0s1e3Y%2FBio-security-review.pdf?alt=media&token=5e15e865-c639-491a-95e8-9a46715e280e)
- [DeSci Launchpad Security Review (Solana), Pashov Audit Group, February 2025](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F3ba2jNU6BPQUl4RXgHor%2Fuploads%2Ff5zTFrmYvglsJ6WAXZxM%2FDesciLaunchpad-security-review_2025-02-07.pdf?alt=media&token=fb866405-1e2a-4035-b8f7-71aabae3841d)
- [Security Code Review of Bio Launchpad v0.1 (Solana), FYEO, February 2025](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F3ba2jNU6BPQUl4RXgHor%2Fuploads%2FwUCj5OeWCmIpLizDug9d%2FBio%20-%20Security%20Code%20Review%20of%20Bio%20Launchpad%20v0.1.pdf?alt=media&token=388bf344-686f-47f6-8b56-996b19aacf23)
- [Bio Security Review (Curation, LaunchFactory), Pashov Audit Group, March 2025](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F3ba2jNU6BPQUl4RXgHor%2Fuploads%2FW7mPQHDWHGApxw1jl6CO%2FBio-security-review_2025-03-12.pdf?alt=media&token=e715feb0-d7f7-4297-b0da-f68fc4686dc9)
- [Security Code Review of Launchpad Agent EVM (Launchpad v2), FYEO, July 2025](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F3ba2jNU6BPQUl4RXgHor%2Fuploads%2FuYIpl4lmoMs2hOgnrj18%2FLaunchpad%20v2%20Contracts%20(FYEO).pdf?alt=media&token=a30d98e2-2b1b-4b00-bca0-d29692d9bd9b)

### Libraries

- [OpenZeppelin Contracts 4.x — AccessControlDefaultAdminRules](https://docs.openzeppelin.com/contracts/4.x/api/access#AccessControlDefaultAdminRules)
- [OpenZeppelin merkle-tree (StandardMerkleTree)](https://github.com/OpenZeppelin/merkle-tree)
- [Solady MerkleProofLib](https://github.com/Vectorized/solady/blob/main/src/utils/MerkleProofLib.sol)

### Related articles

- [Virtual Protocol, create co-ownership AI agents]({{site.url_complet}}/2024/12/05/virtual-protocol-architecture/)
- [ERC Standards for AI Agents - The On-Chain Agent Stack on Ethereum]({{site.url_complet}}/2026/07/06/erc-ai-agents-ethereum-standards/)
- [Cyfrin First Fight 42 - Snowman Merkle Airdrop]({{site.url_complet}}/2025/07/11/cyfrin-first-fight-42-snowman-merkle-aidrop/)
- [OpenZeppelin v5 Data - Overview]({{site.url_complet}}/2025/07/29/openzeppelin-data-structure/)
