---
layout: post
title: "Bio's Voter Stake Registry - Vote-Escrow Governance on Solana with spl-governance"
date:   2026-09-18
lang: en
locale: en-GB
categories: blockchain solana defi
tags: solana anchor governance staking desci rust
series: bio-protocol
description: "How Bio's fork of the Mango Voter Stake Registry turns locked deposits into time-weighted spl-governance vote weight, and what its Squads V4 allowlist changes."
image: /assets/article/blockchain/defi/bio-protocol/2026-09-18-bio-voter-stake-registry-mindmap.png
isMath: true
---

[Bio Protocol](https://www.bio.xyz/) is a decentralised-science platform that funds biotech research through token-governed communities, with its `BIO` token deployed on Ethereum, Base, BNB Chain and Solana. The previous article in this series, [Bio Protocol Overview - DeSci Launchpad, BIO Token Economy and Open-Source DAO Contracts]({{site.url_complet}}/2026/09/18/bio-protocol-overview/), covered the launchpad and the EVM contracts. On Solana, Bio publishes a single program: a fork of the *Voter Stake Registry* (VSR) originally written by Blockworks for the Mango DAO.

The VSR is not a token or a staking pool. It is an *add-in* to [spl-governance](https://github.com/solana-labs/solana-program-library/tree/master/governance), the Realms DAO framework: a separate program that computes how much voting power a wallet has and writes the result into an account that spl-governance reads when a vote is cast. This article reads Bio's fork to explain how that number is computed, how deposits, lockups, grants and clawbacks are enforced, and what the one behavioural change Bio made, a CPI allowlist for the Squads V4 multisig program, does.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What a voter-weight add-in is

In a plain spl-governance realm, voting power is the number of governing tokens a member has deposited into the realm: one token, one vote, with no time dimension. The `VoterWeightRecord` mechanism, defined in the [spl-governance add-in API](https://github.com/solana-labs/solana-program-library/tree/master/governance/addin-api), lets a realm delegate that computation to another program. When a realm is configured with a voter-weight add-in, the default deposit and withdraw flow for the governing mint is disabled, and every `cast_vote` reads a `VoterWeightRecord` account instead of the member's token balance.

The contract between the two programs is small. The add-in owns a `VoterWeightRecord` account per member, holding `realm`, `governing_token_mint`, `governing_token_owner`, a `voter_weight` and a `voter_weight_expiry` slot. spl-governance requires the record's expiry to match the current slot, so the add-in has to refresh the record in the same transaction as the vote. The VSR never calls spl-governance itself; the doc comment in `lib.rs` states that it "simply writes a `VoterWeightRecord` account with a well defined format". The only direction of dependency is the other way: the VSR reads spl-governance's `TokenOwnerRecord` before a withdrawal to check that the member is not engaged in an active vote.

![Accounts around a realm: the realm authority creates the Registrar and grants or claws back; the voter authority owns a Voter PDA with a vault, refreshes a VoterWeightRecord that cast_vote reads, and withdraws only if the TokenOwnerRecord allows it]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-vsr-accounts-concept.png)

## Accounts and their invariants

The program keeps three account types of its own, all program-derived addresses, plus one SPL token vault per deposited mint.

### Registrar

One per realm and governing mint, at seeds `[realm, "registrar", realm_governing_token_mint]`. It stores the governance program id, the realm, the realm authority and an array of four `VotingMintConfig` entries. Only the realm authority can create it and configure its mints. A `time_offset` field exists for tests; the `set_time_offset` instruction that writes it refuses to run unless the registrar's governance program id is the test fixture `GovernanceProgramTest1111111111111111111111`, so it is inert on a production realm.

### VotingMintConfig

Each configured mint carries the parameters that turn a native token amount into vote weight:

| Field | Meaning |
|-------|---------|
| `mint` | The SPL mint that can be deposited under this entry. |
| `grant_authority` | An address allowed to push grants to voters for this mint, besides the realm authority. |
| `baseline_vote_weight_scaled_factor` | Weight per token for all deposited funds, locked or not, in units of $$10^{-9}$$. |
| `max_extra_lockup_vote_weight_scaled_factor` | Maximum extra weight per locked token, reached at full saturation, same units. |
| `lockup_saturation_secs` | Lockup duration at which the extra weight reaches its maximum. |
| `digit_shift` | Power of ten applied to native amounts before the factors, to align mints with different decimals. |

A mint whose two factors are both zero "grants no vote weight"; the code comments describe this as a way to use grants, vesting schedules and clawback for a non-voting token such as USDC. The `configure_voting_mint` instruction ends by computing the realm's maximum possible vote weight over the supplies of all configured mints, so a configuration that could overflow a `u64` is rejected at setup rather than at vote time.

### Voter and deposit entries

One `Voter` account per voter authority, at seeds `[registrar, "voter", voter_authority]`, holds 32 `DepositEntry` slots. Each entry records a `Lockup` with its start, end and kind, the mint config index, two amounts and two flags:

```rust
pub struct DepositEntry {
    pub lockup: Lockup,
    pub amount_deposited_native: u64,
    pub amount_initially_locked_native: u64,
    pub is_used: u8,
    pub allow_clawback: u8,
    pub voting_mint_config_idx: u8,
    pub reserved: [u8; 29],
}
```

`amount_deposited_native` is what the user can still withdraw in total and goes down with every withdrawal. `amount_initially_locked_native` is the amount the vesting schedule is computed from and is *not* reduced by withdrawals, which is why it can exceed the deposited amount after some tokens have vested and been taken out. Tokens themselves sit in an associated token account whose owner is the Voter PDA; every transfer out is signed with the voter seeds.

The `VoterWeightRecord` lives at `[registrar, "voter-weight-record", voter_authority]` and is created together with the Voter. It is the account spl-governance reads.

## From tokens to vote weight

The core of the program is a single function, `DepositEntry::voting_power`, whose result is summed over the used entries of a voter. For one entry with $$a_d$$ tokens deposited and $$a_l$$ tokens initially locked, after the mint's `digit_shift`:

$$
\begin{aligned}
w &= B \cdot a_d + \phi(t) \cdot M \cdot a_l \\
\phi(t) &= \min\left(\frac{t_{\mathrm{rem}}}{T_{\mathrm{sat}}},\ 1\right)
\end{aligned}
$$

where $$B$$ is the baseline factor, $$M$$ the maximum extra lockup factor, $$T_{\mathrm{sat}}$$ the saturation duration and $$t_{\mathrm{rem}}$$ the seconds left on the lockup. Both factors are integers divided by $$10^9$$, and all intermediate products are computed in `u128` with checked arithmetic. The baseline part applies to *everything* deposited; the bonus applies only to what was locked, and it decays as the lockup runs down.

How $$t_{\mathrm{rem}}$$ is defined depends on the lockup kind, and this is where the five kinds differ.

![Locked vote weight by lockup kind: None gives no bonus, Cliff decays linearly to zero at the end, Constant never decays until converted to Cliff, Daily and Monthly sum the decaying weights of one cliff per remaining period]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-vsr-lockup-kinds-activity.png)

### The five lockup kinds

- **`None`.** No lockup. The entry contributes baseline weight only and its tokens can be withdrawn at any time, subject to the active-vote check.
- **`Cliff`.** Tokens are locked until `end_ts` and unlock all at once. $$t_{\mathrm{rem}} = \mathrm{end} - \mathrm{now}$$, so the bonus falls linearly to zero at the cliff. The code comment gives the design rationale: at every instant the lockup should be worth the same as a fresh lockup of the remaining duration.
- **`Constant`.** A permanent lock. `seconds_left` substitutes `start_ts` for the current time, so $$t_{\mathrm{rem}}$$ never changes and the bonus does not decay. To exit, the holder converts the entry to `Cliff` with `reset_lockup`, at which point the configured number of days becomes the minimum unlock period.
- **`Daily` and `Monthly`.** Linear vesting in periods of one day, or of $$365/12$$ days. Each period, a fraction $$1/n$$ of the initially locked amount becomes withdrawable. For vote weight the schedule is treated as $$n$$ cliffs each holding $$M \cdot a_l / n$$, and their individually decaying bonuses are summed in closed form; the function `voting_power_linear_vesting` derives the sum in a long comment, splitting the periods into those below saturation and those at it.

Two limits bound every lockup: at most $$365 \times 200$$ periods, so 200 years for daily kinds, and a start at most 100 years in the future. A lockup whose start is in the future is still locked, and the weight computation ignores the start and counts the full interval to `end_ts`.

Lockups can only get stricter. `LockupKind::strictness` orders them `None` < `Daily` < `Monthly` < `Cliff` = `Constant`, and `reset_lockup` requires both that the new duration be at least the seconds left and that the new kind be at least as strict. Resetting also re-locks any vested tokens the holder has not yet withdrawn, since `amount_initially_locked_native` is set back to `amount_deposited_native`.

### Refreshing the record

`update_voter_weight_record` recomputes the sum over all entries and writes it into the record with `voter_weight_expiry = Some(current_slot)`. Because the expiry is a slot, the record is valid for exactly the transaction that refreshed it; a client votes by bundling this instruction with spl-governance's `cast_vote`. The same refresh is performed at the end of `withdraw`, so a withdrawal cannot leave a stale, higher weight behind.

![Deposit-to-vote sequence: create_voter checks the CPI caller against the Squads allowlist, deposit resolves past vesting and transfers to the vault, update_voter_weight_record and cast_vote run in one transaction, withdraw transfers then checks the TokenOwnerRecord and the unlocked amount]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-vsr-vote-sequence.png)

## Deposits, withdrawals, grants and clawbacks

### Deposit

`create_deposit_entry` reserves a slot with a kind, an optional future start, a number of periods and the clawback flag, holding zero tokens. `deposit` then moves tokens into the vault and adds them to both amounts. Adding to a vesting entry already in progress is supported: `resolve_vesting` first realises the periods that have passed by moving `start_ts` forward and reducing the locked amount, so the new tokens vest over the remaining periods only. The doc comment gives the example of 20 tokens added to a three-day schedule 36 hours in: 10 vest after 12 more hours and 10 after 36.

### Withdraw

`withdraw` is the only user path that moves tokens out, and it has three guards in sequence. First, if the mint grants vote weight, the caller's spl-governance `TokenOwnerRecord` is loaded and `assert_can_withdraw_governing_tokens()` is called, which fails while the member has outstanding votes on active proposals or unrelinquished vote records. Second, the amount must not exceed `amount_unlocked(now)`, the deposited amount minus what is still locked under the schedule. Third, the mint of the destination account must match the entry's mint config. The token transfer is issued before these checks in the instruction body; Solana transactions are atomic, so a failed check reverts it.

### Grant and clawback

`grant` creates a new, fully locked deposit entry for someone else, initialising their Voter and record if they do not exist yet. Because deposit slots are a finite resource (32 per voter) and could be exhausted by an attacker pushing tiny grants with long lockups, the signer must be the realm authority, the mint's `grant_authority` or the target voter itself.

A grant created with `allow_clawback = true` can later be reclaimed by the realm authority with `clawback`, which transfers the *still locked* portion back to a destination account and converts the entry to `None`. Vested tokens stay with the grantee. The code deliberately skips the active-vote check here, with the comment that otherwise "a grantee could block clawback" by keeping a vote open.

Clawback entries also cannot be re-locked with `reset_lockup`, nor used as the source of an `internal_transfer_locked`, since either would let a grantee move tokens out from under a clawback that targets a fixed entry index; the holder must withdraw and open a new entry. The intended use, per the README, is token grants to contributors, not ordinary member deposits.

`internal_transfer_locked` and `internal_transfer_unlocked` move tokens between two entries of the same voter without leaving the vault, with the same rule that locked tokens may only move to an entry at least as long and as strict. The documented use is consolidating small entries, or peeling a slice off a `Constant` entry into a `Cliff` entry to start unlocking part of it.

## What Bio changed

The fork's history has 50 commits. The first 34 are upstream Blockworks and Solana Labs commits up to December 2022 (Anchor 0.26); the 16 commits from August 2024 to May 2025 are Bio's, by a single contributor. Diffing the program source against the fork point shows one behavioural change and a set of toolchain changes.

### The Squads V4 allowlist

Upstream `create_voter` reads the instructions sysvar and refuses to run when invoked through a cross-program invocation, with the comment that the goal is "to make automation impossible that weakens some of the limitations intentionally imposed on locked tokens", for instance a program that wraps a locked position into a transferable token. Bio kept the check and added one exception:

```rust
pub const ALLOWED_CPI_PROGRAMS: &[Pubkey] = &[
    // Squads V4 Program
    pubkey!("SQDS4ep65T869zMMBKyuUq6aD6EgTu8psMjkvj52pCf"),
];

// Fast path: if the program_id matches this program, allow.
if current_ixn.program_id != *ctx.program_id {
    // Otherwise, only allow if in ALLOWED_CPI_PROGRAMS.
    require!(
        ALLOWED_CPI_PROGRAMS.contains(&current_ixn.program_id),
        VsrError::ForbiddenCpi
    );
}
```

A Squads V4 multisig executes its approved transactions through a vault PDA that signs by CPI, so under the upstream rule a multisig could never create a Voter and therefore could not hold locked governance deposits at all. With the allowlist, a Squads-controlled treasury or team wallet can create its Voter, deposit `BIO` under a lockup and vote, while any other program is still rejected. The check only guards `create_voter`; `deposit`, `withdraw` and the rest have no CPI restriction upstream either, which is consistent with the stated goal of preventing the *creation* of automated positions rather than their operation.

### Toolchain and layout changes

The remaining changes exist to build the 2022 code on a current stack, and two of them touch on-chain layout:

- **Anchor 0.26 to 0.31.1, Solana 1.x to 2.2.1.** Account bumps move from `ctx.bumps.get("voter")` to `ctx.bumps.voter`, `#[account(zero_copy)]` on `Voter` is combined with `#[repr(C)]`, and `DepositEntry` drops `zero_copy` for explicit `AnchorSerialize`/`AnchorDeserialize` plus `bytemuck::Pod`.
- **`bool` to `u8` flags.** `is_used` and `allow_clawback` become `u8` with accessor methods, because `bool` is not `Pod`. The size assertions (`80` bytes per entry, `32 × 80` in a Voter) are unchanged, so existing accounts keep their layout.
- **`VoterWeightRecord` wrapper.** The record is spl-governance's type, owned by this program. The fork wraps it in a newtype with hand-written borsh serialisation and, per the August 2024 commit message, forces the *old* account discriminator, so records created by the upstream binary remain readable.
- **Tests.** The `spl_governance.so` fixture is refreshed, and the test realm's `min_community_weight_to_create_proposal` is set to 1000.

The `CHANGELOG.md` labels this state v0.3.0 and "on mainnet". The `declare_id!` in the source is upstream's program id, `9SJqwCQ5AJkFtC7zxfFsF6Y5dm22XzN3JEhn3N14v23t`, the one the Mango DAO has used since 2022. Whether Bio's build runs at that address, which would require holding its upgrade authority, or whether Bio deployed under a different id and left the source unchanged, cannot be determined from the repository. The Bio documentation does not mention a Realms deployment; its Solana page says the vesting and token programs "will be added to the Docs in the future".

## veBIO on Base versus the VSR on Solana

Bio's EVM vote-escrow, documented as `veBIO`, and its Solana add-in solve the same problem with different parameters:

| | `veBIO` (Base, private code) | Voter Stake Registry (Solana, public) |
|---|---|---|
| Lock duration | 1 week to 2 years | Any of five kinds, up to 200 years |
| Weight formula | `BIO × weeks_remaining / 104` | `B × deposited + min(t / T_sat, 1) × M × locked` |
| Unlocked tokens | Contribute nothing | Contribute baseline weight `B` |
| Decay | Linear to zero, auto-renew option | Linear to zero for `Cliff`; none for `Constant` |
| Vesting inside the lock | No | `Daily` / `Monthly` release fractions while still locked |
| Multiple assets | `BIO` only | Up to 4 mints per registrar with per-mint factors |
| Grants and clawback | Not documented | Built in, realm-authority controlled |
| Governance consumer | Off-chain BioXP accrual; voting rights planned after a governance proposal | spl-governance `cast_vote`, on-chain |

The `Constant` kind is the closest analogue to `veBIO` with auto-renewal switched on: a position whose weight does not erode until the holder decides to start the clock. The VSR's `Daily` and `Monthly` kinds have no `veBIO` counterpart; they are the Solana equivalent of the EVM `TokenVesting` contract, where a vesting balance also counts for governance, but here the vesting and the voting live in one program.

## Conclusion

Bio's Solana governance program is a lightly modified Mango VSR, and reading it shows what "vote-escrow on spl-governance" consists of.

- **Add-in, not token.** The program never calls spl-governance. It writes a `VoterWeightRecord` that expires after one slot, and the client refreshes it in the same transaction as `cast_vote`.
- **Two-part weight.** Baseline factor times everything deposited, plus a lockup bonus on the locked part that scales with time remaining up to a saturation duration; both factors are per-mint, in $$10^{-9}$$ units, over up to four mints.
- **Five lockup kinds** with a strictness order that `reset_lockup` and internal transfers can never decrease; `Constant` does not decay, `Daily` and `Monthly` release tokens while still counting a decaying bonus.
- **Grants with clawback** let the realm authority lock tokens for contributors and reclaim the unvested part, and that path intentionally ignores active votes.
- **One Bio change** to behaviour: `create_voter` accepts a CPI from the Squads V4 program, so a multisig can hold a locked position. Everything else in the fork is the port to Anchor 0.31 and Solana 2.2, with account layouts and the record discriminator preserved.
- **Open question.** The source keeps upstream's program id, and the documentation does not name a realm, so the on-chain deployment is not verifiable from the repository alone.

![Mindmap of Bio's voter-stake-registry covering the spl-governance add-in model, its accounts, the vote weight formula, the five lockup kinds, grants and clawback, and Bio's changes]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/2026-09-18-bio-voter-stake-registry-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **spl-governance** | Solana's DAO framework, used by Realms, in which members deposit governing tokens into a realm and vote on proposals. |
| **Voter-weight add-in** | A separate program a realm delegates vote-weight computation to; it writes a `VoterWeightRecord` that `cast_vote` reads instead of the token balance. |
| **VoterWeightRecord** | Account owned by the add-in holding a member's `voter_weight` and an expiry slot; valid only in the slot it was refreshed in. |
| **Registrar** | The add-in's per-realm configuration account, holding up to four `VotingMintConfig` entries and the realm authority. |
| **Voter** | Per-member PDA with 32 deposit entries; its seeds sign every transfer out of the member's vaults. |
| **DepositEntry** | One lockup position: kind, start and end, mint index, amount deposited, amount initially locked, clawback flag. |
| **Lockup saturation** | The duration `lockup_saturation_secs` at which the extra lockup weight reaches its per-mint maximum. |
| **Constant lockup** | A lockup whose remaining time never decreases until it is converted to `Cliff`, so its bonus does not decay. |
| **Clawback** | Realm-authority instruction reclaiming the still-locked tokens of a grant created with `allow_clawback`. |
| **Squads V4** | A Solana multisig program whose vault PDA executes approved transactions by CPI; Bio allowlists it in `create_voter`. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A `VoterWeightRecord` used by `cast_vote` reflects the deposits at the vote's slot. | `voter_weight_expiry = Some(current_slot)` on every refresh; spl-governance rejects a stale expiry. | spl-governance's expiry check is relaxed, or a refresh path writes a non-current slot. |
| Tokens with vote weight cannot leave the vault while the member has active votes. | `withdraw` loads the `TokenOwnerRecord` and calls `assert_can_withdraw_governing_tokens()` when the mint grants weight. | The mint is configured with both factors zero, in which case the check is skipped by design. |
| A member can never withdraw more than the unlocked part of an entry. | `require_gte!(amount_unlocked(now), amount)` and `amount_deposited_native -= amount`. | `vested()` is wrong for a kind, or `amount_initially_locked_native` is reduced on withdrawal. |
| A lockup never becomes shorter or less strict. | `reset_lockup` and `internal_transfer_locked` compare seconds left and `strictness()`. | A new kind is added without a strictness rank, or the comparison is inverted. |
| The locked bonus never exceeds the configured maximum. | `require_gte!(max_locked_vote_weight, locked_vote_weight)` after every computation. | A linear-vesting sum overflows or `lockup_saturation_secs` is zero (rejected at configuration). |
| Total realm vote weight fits in a `u64`. | `configure_voting_mint` recomputes `max_vote_weight` over all mint supplies. | A mint's supply grows after configuration beyond what was checked. |
| Only the realm authority, the mint grant authority or the voter itself can consume a deposit slot for someone. | Authority check in `grant`; 32 slots per voter. | The check is widened, allowing slot-exhaustion denial of service. |
| A Voter is created only by a wallet, the program itself or Squads V4. | Instructions-sysvar check in `create_voter` against `ALLOWED_CPI_PROGRAMS`. | The allowlist grows to include a program that tokenises positions. |
| Clawback returns exactly the still-locked amount and never vested tokens. | `amount_locked(now)` computed before the entry is reset to `None`. | Clawback is made to honour the active-vote check, letting a grantee block it. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| The `VoterWeightRecord` expires after one slot. | Always prepend `update_voter_weight_record` to `cast_vote` in the same transaction; a standalone refresh is useless. |
| `create_voter` rejects CPI from any program except Squads V4. | Other multisigs or smart-wallet programs cannot open positions; the wallet must sign `create_voter` directly. `grant` can also initialise a Voter for a target that has none. |
| `withdraw` transfers first and validates second. | Do not read intermediate state within the transaction; rely on the atomic revert. |
| Adding to a vesting entry mid-schedule spreads the new tokens over the remaining periods only. | Expect a shorter effective vesting for top-ups; open a new entry for a fresh full schedule. |
| Withdrawal is blocked while the `TokenOwnerRecord` has outstanding votes. | Relinquish votes on finished proposals before withdrawing, or the instruction fails. |
| A `Constant` lockup cannot be withdrawn until converted to `Cliff`, which then runs for at least the configured days. | Treat `Constant` as an exit with notice period equal to the lockup's period count. |
| Clawback ignores active proposals. | Grantees should not assume an open vote protects an unvested grant. |
| `set_time_offset` is present in the deployed instruction set. | It is gated to the test governance program id; a production registrar cannot call it, but verify the registrar's `governance_program_id` on chain. |
| The source's `declare_id!` is the upstream Mango program id. | Confirm the actual program address and upgrade authority of Bio's deployment on chain before integrating; do not assume the id in the repository. |

## Frequently Asked Questions

**Q: Why does the VSR never call spl-governance, and how does spl-governance trust it?**

The add-in API is designed as a data contract, not a call contract. The realm stores which program is its voter-weight add-in, and `cast_vote` reads a `VoterWeightRecord` account that must be owned by that program and carry the current slot as expiry. The VSR therefore only needs to write that account correctly; spl-governance trusts the owner check and the freshness check rather than a return value.

The dependency runs the other way: the VSR reads spl-governance's `TokenOwnerRecord` to block withdrawals during active votes.

**Q: A member deposits 1,000 tokens with a 1-year `Cliff` on a mint configured with `B = 1e9`, `M = 1e9` and `T_sat` of 2 years. What is the weight at deposit, after six months, and after the cliff?**

With $$B = M = 1$$ after scaling, the baseline is $$1000$$ throughout. The bonus is $$1000 \times \min(t_{\mathrm{rem}} / 2\,\mathrm{y}, 1)$$:

- **At deposit**, $$t_{\mathrm{rem}} = 1$$ year, so the bonus is $$500$$ and the weight is $$1500$$.
- **After six months**, $$t_{\mathrm{rem}} = 0.5$$ year, bonus $$250$$, weight $$1250$$.
- **After the cliff**, the lockup is expired, bonus $$0$$, weight $$1000$$, and the tokens are withdrawable.

Locking for two years or more would have given the full $$1000$$ bonus at deposit.

**Q: What is the difference between `amount_deposited_native` and `amount_initially_locked_native`?**

`amount_deposited_native` is the withdrawable ceiling: it starts at the deposited amount and decreases with every `withdraw`. `amount_initially_locked_native` is the base of the vesting schedule and the bonus computation: it is set when tokens are deposited or the lockup is reset and is not reduced by withdrawals, so that the amount vesting per period stays constant. After some vesting and withdrawals the second can exceed the first; `amount_locked(now)` is derived from the second, and `amount_unlocked` is the first minus that.

**Q: Why does upstream forbid creating a Voter through CPI, and what does Bio's exception change?**

A program that could create Voters could wrap locked positions, for instance minting a transferable token against a `Constant` lockup, which would defeat the point of the lockup. The instructions-sysvar check makes the wallet itself sign `create_voter` at the top level of the transaction.

Bio's exception admits one program, Squads V4, whose vault PDA can only act on transactions its multisig members approved. The effect is that a multisig-controlled treasury or team allocation can hold and vote with locked `BIO`; no other program gains that ability, and the other instructions were never CPI-restricted.

**Q: How does a `Monthly` vesting entry count for voting while it is vesting?**

Each remaining period is treated as its own cliff holding $$1/n$$ of the initially locked amount, and the bonus of each cliff decays with its own remaining time, capped at saturation. `voting_power_linear_vesting` sums these in closed form: the periods still under saturation contribute a triangular sum of period lengths plus the fractional time to the next cliff, and the periods beyond saturation contribute the full saturated amount each.

Tokens from periods already passed are no longer locked and contribute baseline weight only, until withdrawn.

**Q: Combining `grant`, `clawback` and `reset_lockup`, what can and cannot a grantee do with a clawback-enabled grant?**

The grantee can vote with it and withdraw the vested part as periods pass. Three things are closed to them:

- **Re-locking.** `reset_lockup` rejects a clawback deposit.
- **Moving locked tokens.** `internal_transfer_locked` refuses clawback-enabled sources, so a clawback instruction cannot be pointed at an emptied slot.
- **Blocking the clawback.** `clawback` skips the active-vote check, so an open vote does not protect the grant.

The realm authority can at any time reclaim what is still locked, after which the entry becomes `None` and the vested remainder stays withdrawable.

**Q: How does this compare with the veBIO lock on Base?**

Both grant time-weighted governance power for locking `BIO`, but `veBIO` weights only the locked amount, over at most two years, with a single linear decay and an optional auto-renewal. The VSR gives unlocked deposits a baseline weight, lets the realm tune the ratio of baseline to lockup bonus per mint, supports vesting schedules and permanent locks, and feeds on-chain votes in spl-governance directly rather than an off-chain points system.

## References

### Analyzed source

- [bio-xyz/voter-stake-registry](https://github.com/bio-xyz/voter-stake-registry) — analyzed at commit [`3dbc0ead93f64795f613d2cf8c50a839b50b1040`](https://github.com/bio-xyz/voter-stake-registry/tree/3dbc0ead93f64795f613d2cf8c50a839b50b1040) (CHANGELOG v0.3.0), 2026-09-18; fork point [`3ef766d249ae95665a640356be37857f9e0185c7`](https://github.com/blockworks-foundation/voter-stake-registry/commit/3ef766d249ae95665a640356be37857f9e0185c7) of the upstream repository, 2022-12-22
- [blockworks-foundation/voter-stake-registry](https://github.com/blockworks-foundation/voter-stake-registry) — upstream, Mango DAO

### Specifications and programs

- [spl-governance](https://github.com/solana-labs/solana-program-library/tree/master/governance) — Solana Program Library governance program
- [spl-governance addin-api](https://github.com/solana-labs/solana-program-library/tree/master/governance/addin-api) — `VoterWeightRecord` and `MaxVoterWeightRecord` definitions
- [Squads Protocol V4](https://github.com/Squads-Protocol/v4) — multisig program `SQDS4ep65T869zMMBKyuUq6aD6EgTu8psMjkvj52pCf`
- [Anchor](https://www.anchor-lang.com/) — framework version 0.31.1 used by the fork

### Documentation

- [Bio Protocol documentation — Solana Programs](https://docs.bio.xyz/bio/developers/dao-setup/solana-programs)
- [Bio Protocol documentation — Staking BIO](https://docs.bio.xyz/bio/introduction/bio-protocol-v2/staking-and-vebio/staking-bio) — the `veBIO` formula used in the comparison

### Related articles

- [Introduction to Solana Anchor — Core Concepts and Testing]({{site.url_complet}}/2026/03/13/solana-anchor-introduction/)
- [Solana Core Concept]({{site.url_complet}}/2024/09/19/solana-core-concept/)
- [Solana Programs - Basic Security with Anchor]({{site.url_complet}}/2024/08/20/solana-smart-contract-basic-security/)
- [Solana Staking - Overview]({{site.url_complet}}/2025/11/07/solana-staking-overview/)
