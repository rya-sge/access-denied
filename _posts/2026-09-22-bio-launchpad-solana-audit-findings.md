---
layout: post
title: "Three Launchpad Bugs from the Bio Protocol Solana Audits - Stranded Supply, Refund Races and Dust Denial of Service"
date:   2026-09-22
lang: en
locale: en-GB
categories: blockchain solana security
tags: solana anchor rust security audit desci launchpad
series: bio-protocol
description: "Three Bio Solana launchpad audit bugs, with code: sale tokens stranded by pro-rata claims, a revenue sweep that starves refunds, a u16 table filled for cents."
image: /assets/article/blockchain/defi/bio-protocol/2026-09-22-bio-launchpad-solana-findings-mindmap.png
isMath: false
---

[Bio Protocol](https://www.bio.xyz/) is a decentralised-science launchpad, and in early 2025 it ran its token sales on Solana before the EVM V2 launchpad took over. Two Anchor programs from that period were audited and the reports published: the *DeSci Launchpad*, a fixed-price sale with a minimum revenue threshold, reviewed by Pashov Audit Group in February 2025 (12 findings, one Critical), and the *Bio Launchpad v0.1* curation program, reviewed by FYEO the same month (1 Low, 4 Informational). Neither program is open source; the reports are the public record.

This article explains three of those findings from the code up, chosen because each is a class of bug that any sale program can have regardless of chain, and because two of them show a specifically Solana flavour: **sale tokens stranded in a vault by pro-rata claim math**, **an admin revenue sweep and user refunds competing for the same vault**, and **a participant table sized as a `u16` that a few dollars of dust can fill**. A companion article, [Three Launchpad Bugs from the Bio Protocol EVM Audits - Units, Donations and Partial Claims]({{site.url_complet}}/2026/09/22/bio-launchpad-evm-audit-findings/), does the same for the EVM contracts.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The two reports

| Report | Date | Scope | Result |
|--------|------|-------|--------|
| Pashov Audit Group, *Desci Launchpad Security Review* | 7 to 10 February 2025 | `buy_token`, `claim_token`, `claim_revenue`, `create_token`, `deposit_token`, `init_stats`, `update_token`, `withdraw_token` and state (repository `merklelabshq/desci-launchpad`, commit `7167b47…`, fixes `e41b734…`) | 1 Critical, 2 High, 1 Medium, 8 Low; all resolved except two acknowledged Lows |
| FYEO, *Security Code Review of Bio Launchpad v0.1* | 11 to 21 February 2025 | `init_dao`, `init_curation`, `curation`, `close_curation`, `withdrawal_curation`, `start_bonding` and state (repository `ASCorreia/bio-launchpad`, commit `df25049…`) | 1 Low, 4 Informational; all open at report time |

The two programs do different jobs.

**The DeSci Launchpad** is a fixed-price sale. The project authority deposits `sale_supply` tokens into a vault owned by a `stats` PDA (`deposit_token`). Buyers pay with a payment token at `price_per_token` (`buy_token`), which records `tokens_purchased` per user and adds to a global `claimed_supply`; revenue accumulates in a `stats_pay_token` vault. After `end_time`, if `revenue >= min_threshold` buyers call `claim_token` and the admin calls `claim_revenue`; if not, buyers call `withdraw_tokens` to get their payment back.

**The Bio Launchpad v0.1** is a curation program: contributors deposit tokens toward a BioDAO's funding threshold during a curation window (`curation`), can withdraw (`withdrawal_curation`), and a bonding phase was planned but unfinished at review time. Contributors are counted in a `total_curators` field.

## Finding 1: sale tokens stranded in the vault (DeSci C-01 and H-01)

### What the code does

The claim instruction pays each buyer a share of the tokens in the vault, pro rata to their purchases:

```rust
let adjusted_tokens = (
  (user_stats.tokens_purchased as f64 / token_stats.claimed_supply as f64)
    * (token_stats.sale_supply.min(token_stats.claimed_supply) as f64))
    as u64;
transfer(
    CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        Transfer {
            from: ctx.accounts.stats_token.to_account_info(),
            to: ctx.accounts.user_token.to_account_info(),
            authority: ctx.accounts.stats.to_account_info(),
        },
        &[signer_seed],
    ),
    adjusted_tokens,
)?;
```

Read it for the case that matters, an undersubscribed sale where `claimed_supply < sale_supply`. The `min` picks `claimed_supply`, so the expression reduces to `tokens_purchased / claimed_supply * claimed_supply`, which is `tokens_purchased`. Every buyer receives exactly what they bought. That is correct for the buyers, and it is the problem.

### Where the tokens go

`deposit_token` moved the full `sale_supply` into the vault:

```rust
pub fn deposit_token_handler(ctx: Context<DepositToken>) -> Result<()> {
    let token_stats = &mut ctx.accounts.token_stats;
    transfer(
        CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            Transfer {
                from: ctx.accounts.authority_token.to_account_info(),
                to: ctx.accounts.stats_token.to_account_info(),
                authority: ctx.accounts.authority.to_account_info(),
            },
        ),
        token_stats.sale_supply,
    )?;
```

Claims pay out `claimed_supply` in total. The difference, `sale_supply - claimed_supply`, is still in the vault after every buyer has claimed, and no instruction can move it: `claim_token` only pays buyers, `claim_revenue` only touches the payment-token vault, and there is no "withdraw unsold" for the authority. Pashov rated this Critical: the unsold portion of every undersubscribed sale is permanently lost.

![Activity flow of the stranded-supply findings: the vault is funded with sale_supply, purchases add to claimed_supply, claims pay exactly tokens_purchased so the difference stays in the vault forever, and refunds below the threshold return the payment token without restoring claimed_supply or the purchased tokens]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-desci-launchpad-accounting-activity.png)

The sibling finding H-01 is the same leak from the refund side. When a sale misses its threshold, `withdraw_tokens` refunds the buyer's payment:

```rust
user_stats.is_claimed = true;
let signer_seed = &[STATS_SEED, &[ctx.accounts.stats.bump]];
let refund_amount = (((user_stats.tokens_purchased as f64)
    / (10u64.pow(token_stats.decimals as u32) as f64))
    * (token_stats.price_per_token as f64)) as u64;
transfer(/* stats_pay_token -> user_pay_token */, refund_amount)?;
```

It marks the user as claimed and refunds the payment token, but it neither subtracts `tokens_purchased` from `claimed_supply` nor returns those tokens to the authority. The tokens the refunded user had bought stay in the vault and are counted as claimed, so nobody can claim them and nobody can withdraw them. Pashov's example: a user with `tokens_purchased = 1000` out of `claimed_supply = 5000` withdraws; 4000 remain claimable by others and 1000 are locked forever.

### The fix and the lesson

Two fixes were recommended and adopted: an instruction that returns `sale_supply - claimed_supply` to the authority after the sale, and a `withdraw_tokens` that decrements `claimed_supply` and returns the tokens. The lesson is an accounting identity that every sale should be able to state and test: **tokens deposited for sale = tokens claimable by buyers + tokens refundable to the authority + tokens already paid out**. When one of those terms has no instruction that can move it, the identity is violated by construction, and the amount is lost regardless of how correct the per-user math is.

Note also the `as f64` casts on both paths; floating-point arithmetic on token amounts is a separate smell that Solana auditors flag on sight, because it rounds unpredictably and can overflow silently when cast back to `u64`.

## Finding 2: the admin's revenue sweep races user refunds (DeSci H-02 and M-01)

### What the code does

Below the threshold, buyers may reclaim their payment; above it, the admin claims the revenue. Both instructions draw from the same `stats_pay_token` vault. The refund path checks the threshold:

```rust
pub fn withdraw_token_handler(ctx: Context<WithdrawToken>) -> Result<()> {
    require!(token_stats.end_time < curr_time, RocketxLaunchpadError::InvalidWithdrawTime);
    require!(token_stats.is_launched, RocketxLaunchpadError::TokenNotLaunched);
    require!(!user_stats.is_claimed, RocketxLaunchpadError::TokenAlreadyClaimed);
    require!(
        token_stats.revenue < token_stats.min_threshold,
        RocketxLaunchpadError::InvalidThreshold
    );
    // ... refund from stats_pay_token
}
```

`claim_revenue` had no corresponding check: it could be called as soon as the sale ended, whether or not the threshold was met, and it transferred `token_stats.revenue`, the recorded total, out of the vault.

![Sequence of the refund race: when revenue is below the threshold, an admin claim_revenue first empties the vault so every buyer refund reverts for insufficient funds; a buyer refund first reduces the vault below the recorded revenue so the admin's claim_revenue reverts forever]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/bio-desci-launchpad-refund-race-sequence.png)

### The two orderings

Consider a sale that ended below `min_threshold`, so buyers are entitled to refunds.

- **Admin first.** `claim_revenue` moves the entire recorded revenue to the admin. Every subsequent `withdraw_tokens` passes its own checks, then fails at the SPL transfer because the vault is empty. Users who were promised a refund get nothing, and the admin holds payment for a sale that did not happen. This is the High finding: an admin action, malicious or merely hasty, voids every user's refund.
- **User first.** One buyer refunds. The vault now holds less than `token_stats.revenue`, so when the admin calls `claim_revenue` the transfer of the recorded amount fails. The admin can never sweep the remainder; it is stuck unless the program is upgraded.

Either side can starve the other because the two instructions share a resource and neither knows about the other's state. The Medium finding M-01 is the same conflict on the token side: below the threshold, `claim_token` was still callable, so some buyers could take tokens while others took refunds, leaving the sale's accounts inconsistent in both directions.

### The fix and the lesson

Pashov proposed either disabling `claim_revenue` when `revenue < min_threshold`, so that only refunds are possible, or a cooldown after the sale during which only users may act, after which `claim_revenue` transfers the *remaining balance* rather than the recorded figure. For M-01, `claim_token` gained the check `revenue >= min_threshold`.

The lesson is that **a sale's outcome must be a single branch**: once the threshold is evaluated, exactly one of {claim tokens, claim revenue} or {refund payment, return tokens} is open, and the two sets never overlap. Where two parties draw on one vault, the second mover must take "what is left", never a figure recorded before the first mover acted; that is the mirror image of the EVM article's one-wei donation, where a recorded figure was compared for equality against a live balance.

## Finding 3: a curator table filled for a few dollars (FYEO v0.1-01, Low)

### What the code does

The curation program counts contributors:

```rust
self.curation_account.total_curators =
    self.curation_account.total_curators.checked_add(1).ok_or(BioError::ContributionOverflow)?;
```

with `pub total_curators: u16` in the account state, so the count saturates at 65,535, at which point `checked_add` returns an error and the curation accepts no further contributors. The minimum contribution at review time was one base unit of the mint. For a 6-decimal token worth about one dollar, that is a millionth of a dollar; for a 9-decimal token, a billionth.

### The attack

FYEO's arithmetic: an attacker who submits the minimum contribution 65,535 times fills every slot. The tokens spent are worth "0.065 USD with a 6 decimal token or 0.000065 USD for a 9 decimal token"; the transaction fees are the only real cost. The curation is then closed to every legitimate contributor while having raised effectively nothing, and it cannot reach its funding threshold by construction, since `min_contribution × 65,535` is far below any realistic target. The checked add prevents an overflow, so this is not a memory-safety bug; it is a capacity bug with a mispriced entry ticket. FYEO rated it Low, and it was open at the time of the report.

The companion informational finding FYEO-02 completes the picture: `minimum_contribution` had no lower bound at all (it could be zero), and `timestamp_to_start` had no upper bound (a curation could be scheduled a hundred years out).

### The fix and the lesson

The recommendation is a single inequality that every crowdfund with a participant cap should satisfy: **the funding goal must be reachable when every participant contributes the minimum**, that is, `min_contribution × max_participants ≥ threshold`. Alternatively, drop the participant cap and store contributions in per-user PDAs rather than counting them in a bounded integer. More generally, any fixed-width counter in account state is a capacity limit, and the price of consuming one unit of that capacity has to be high enough that exhausting it costs more than the damage it does.

## Other findings worth knowing

- **`transfer` instead of `transfer_checked` (DeSci L-05).** The plain SPL `transfer` does not verify the mint or decimals of the accounts involved; `transfer_checked` requires both and fails on a mismatch. On a program that accepts arbitrary payment mints, this is the difference between a decimal mismatch moving a million tokens and a revert.
- **Three roles, one key (DeSci L-06).** `DEV_PUBKEY`, `ADMIN_PUBKEY` and `MINT_AUTHORITY_PUBKEY` were the same hard-coded public key. Acknowledged rather than fixed; a single compromise reaches every privileged instruction.
- **Rollback-safe configuration (DeSci L-07).** After a Solana cluster restart, state written shortly before the restart point may be gone. Pashov recommended recording `last_updated_slot` in the config and comparing it with the `LastRestartSlot` sysvar, pausing the program if the config predates the restart. Acknowledged.
- **Withdrawals only to an associated token account owned by the contributor (FYEO v0.1-03).** Correct for most users, but a contributor whose ATA authority was reassigned by a scam cannot receive their refund. A policy decision the report asked the team to make explicitly.
- **Unfinished code (FYEO v0.1-05).** `TODO` comments in `withdrawal_curation.rs` and `state/bonding.rs` marked the bonding phase as not implemented; a review of an incomplete state machine cannot vouch for the transitions that are missing.

## Conclusion

Three findings, none of them about Solana's account model as such, all about what a sale program promises and whether every promised amount has an instruction that can deliver it:

- **Stranded supply.** Pro-rata claim math paid buyers exactly, and left `sale_supply - claimed_supply` in a vault with no exit; refunds compounded it by leaving purchased tokens counted as claimed. The identity *deposited = claimable + returnable + paid* had a term nobody could move.
- **Refund race.** Admin revenue and user refunds drew from one vault with no ordering rule, so whichever moved first starved the other. A sale outcome must open exactly one set of instructions.
- **Dust denial of service.** A `u16` participant counter and a one-unit minimum contribution let anyone close a curation for cents. Capacity has to be priced.

The Solana-specific lessons sit alongside: no floating point in token math, `transfer_checked` over `transfer`, restart-aware configuration, and an explicit policy on ATA authority. All the Critical, High and Medium findings were resolved before the programs went live, and the EVM V2 launchpad that replaced them was reviewed in turn.

![Mindmap of the three Solana findings: stranded undersubscription supply, the revenue-sweep versus refund race, the u16 dust denial of service, the Solana-specific lessons, and the two reports they come from]({{site.url_complet}}/assets/article/blockchain/defi/bio-protocol/2026-09-22-bio-launchpad-solana-findings-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Anchor** | The Rust framework for Solana programs used by both audited launchpads; it generates account validation from `#[derive(Accounts)]` structs. |
| **PDA (program-derived address)** | An address derived from seeds and a program id, with no private key; the `stats` account owns the sale vaults and signs transfers with its seeds. |
| **Vault** | An SPL token account owned by a program PDA, here `stats_token` for the sale tokens and `stats_pay_token` for the payment token. |
| **`sale_supply`** | The number of tokens the authority deposits for a sale. |
| **`claimed_supply`** | The running total of tokens bought during the sale, used as the denominator of pro-rata claims. |
| **`min_threshold`** | The revenue level below which a sale is considered failed and buyers may reclaim their payment. |
| **Associated token account (ATA)** | The canonical token account for a wallet and mint; refunds in the curation program are sent only to the contributor's ATA. |
| **`transfer_checked`** | The SPL Token instruction that verifies mint and decimals, unlike plain `transfer`. |
| **`LastRestartSlot`** | A sysvar giving the slot of the last cluster restart, used to detect state written before a rollback. |
| **Dust denial of service** | Exhausting a bounded resource, such as a participant counter, with many minimum-size contributions. |

### Security Implementation Checklist

For any on-chain sale or crowdfund program with a threshold, a claim path and a refund path.

#### Supply accounting

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every token deposited for a sale is reachable by exactly one of: a buyer claim, a return to the authority, or a documented burn. | Undersubscription remainder stranded in the vault (DeSci C-01). |
| ☐ | A refund reverses every counter the purchase incremented (`claimed_supply`, per-user purchases) and releases the purchased tokens. | Refunded users' tokens locked and counted as claimed (DeSci H-01). |
| ☐ | Token amounts are computed in integer arithmetic with explicit rounding direction; no `f64` casts. | Unpredictable rounding, silent truncation on cast back to `u64`. |
| ☐ | An "unsold tokens" instruction exists and is callable only after the claim window. | Authority cannot recover what buyers did not take. |

#### Outcome exclusivity

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The threshold is evaluated once and gates both sides: `claim_token` and `claim_revenue` require `revenue >= min_threshold`; `withdraw_tokens` requires the negation. | Buyers and admin drain the same vault in conflicting directions (DeSci H-02, M-01). |
| ☐ | When two parties draw on one vault, the later mover transfers the remaining balance, not a figure recorded earlier. | Second transfer reverts forever once the first has moved funds (DeSci H-02). |
| ☐ | A refund window precedes any admin sweep, or the sweep is disabled below threshold. | Admin empties the vault before users can refund (DeSci H-02). |

#### Capacity and bounds

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | `min_contribution × max_participants ≥ funding_threshold`, or no bounded participant counter. | Curation filled with dust for cents (FYEO v0.1-01). |
| ☐ | Every user-supplied parameter has lower and upper bounds: minimum contribution > 0, start time within a horizon, cooldown ≤ a maximum. | Zero minimums, sales scheduled a century out, unbounded cooldowns (FYEO v0.1-02, DeSci L-02). |
| ☐ | Zero-amount purchases and withdrawals are rejected on the clamped amount, not the requested one. | Zero purchases pass the check (DeSci L-01, FYEO v0.1-04). |

#### Solana specifics

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Token movements use `transfer_checked` with the mint and decimals. | Wrong mint or decimal mismatch moves the wrong amount (DeSci L-05). |
| ☐ | Distinct keys for development, administration and mint authority. | One compromised key controls minting and configuration (DeSci L-06). |
| ☐ | Configuration records `last_updated_slot` and is compared with `LastRestartSlot`; the program pauses on stale config. | Program runs on pre-rollback parameters (DeSci L-07). |
| ☐ | `Anchor.toml` pins `anchor_version` and `solana_version`. | Builds differ across machines and CI (DeSci L-04). |
| ☐ | The refund destination policy (ATA only, or any token account with the right owner) is explicit and documented. | Scam-reassigned ATAs cannot receive refunds (FYEO v0.1-03). |

## Frequently Asked Questions

**Q: If every buyer received exactly what they bought, why is C-01 a Critical finding?**

Because the loss is on the protocol's side and is total for the unsold portion. The authority deposited `sale_supply`; buyers can only ever withdraw `claimed_supply`; no instruction moves the difference. For an undersubscribed sale the unsold tokens are gone as surely as if they had been burned, without anyone deciding to burn them. Pashov's matrix puts a certain, unrecoverable loss of protocol funds at Critical.

**Q: What is the difference between C-01 and H-01?**

They strand tokens by two routes. C-01 is the undersubscription case in a successful sale: tokens never bought stay in the vault. H-01 is the failed-sale case: a refunded buyer's tokens stay in the vault *and* remain counted in `claimed_supply`, so the other buyers' pro-rata shares are computed over a total that includes tokens nobody can take. Fixing C-01 alone (return the unsold remainder) would not fix H-01, because the refunded tokens are not part of `sale_supply - claimed_supply`.

**Q: Why does the order of `claim_revenue` and `withdraw_tokens` matter?**

Both instructions transfer out of `stats_pay_token`, and each computes its amount from stored state rather than from the vault's balance. If the admin moves first, the vault is empty and refunds fail at the token transfer. If a user moves first, the vault holds less than the recorded `revenue` and the admin's transfer fails. Neither instruction checks the other's precondition, so the first caller wins and the second is locked out permanently.

**Q: `checked_add` prevents the overflow in FYEO-01, so where is the bug?**

In the price of a slot. `checked_add` turns the 65,536th contribution into an error rather than a wrap-around, which is correct, but it means the curation stops accepting contributors after 65,535 of them. With a minimum contribution of one base unit, buying all 65,535 slots costs a fraction of a cent in tokens plus fees.

The width of the counter is a capacity, and a capacity that is nearly free to consume is a denial-of-service vector. The fix is not a wider integer but a minimum contribution large enough that filling the table would fund the curation.

**Q: Combining findings 1 and 2, what single test would have caught both?**

A property test over the accounting identity after every instruction sequence: for the token vault, `balance == sale_supply - Σ claimed_by_buyers - returned_to_authority`, and for the payment vault, `balance == Σ purchases - Σ refunds - revenue_swept`, with the additional invariant that once `end_time` has passed, either `Σ refunds == 0` or `revenue_swept == 0`. Sequences of `buy`, `end`, `claim_token`, `withdraw_tokens` and `claim_revenue` in random order violate the first identity in the undersubscribed case (C-01), the second on refund (H-01), and the exclusivity clause on the race (H-02).

**Q: How do these findings compare with the EVM launchpad audits?**

The EVM reports found the same two families, accounting drift and admin-versus-user conflicts on a shared balance, plus a unit mismatch at a contract boundary. The Solana reports add the chain-specific items: floating point in money paths, `transfer_checked`, bounded integer counters in account state, and rollback awareness. In both cases the Critical finding was an accounting error rather than an access-control or reentrancy bug.

## References

### Audit reports

- [Desci Launchpad Security Review, Pashov Audit Group, February 2025](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F3ba2jNU6BPQUl4RXgHor%2Fuploads%2Ff5zTFrmYvglsJ6WAXZxM%2FDesciLaunchpad-security-review_2025-02-07.pdf?alt=media&token=fb866405-1e2a-4035-b8f7-71aabae3841d) — review commit `7167b472dd4e1c1a45ed2d49f00cd1dfadad0fcd`, fixes `e41b734a8280fb7fe6440f9daf5f647b6ac5dec9` (private repository `merklelabshq/desci-launchpad`)
- [Security Code Review of Bio Launchpad v0.1, FYEO, February 2025](https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/o/spaces%2F3ba2jNU6BPQUl4RXgHor%2Fuploads%2FwUCj5OeWCmIpLizDug9d%2FBio%20-%20Security%20Code%20Review%20of%20Bio%20Launchpad%20v0.1.pdf?alt=media&token=388bf344-686f-47f6-8b56-996b19aacf23) — review commit `df250494e70fd3ab36ee4ee8729ff612c5a661ad` (private repository `ASCorreia/bio-launchpad`)
- [Audits index, Bio Protocol documentation](https://docs.bio.xyz/bio/developers/audits)

### Solana references

- [SPL Token `transfer_checked`](https://docs.rs/spl-token/latest/spl_token/instruction/fn.transfer_checked.html)
- [`LastRestartSlot` sysvar](https://docs.rs/solana-program/latest/solana_program/last_restart_slot/struct.LastRestartSlot.html)
- [Anchor framework](https://www.anchor-lang.com/)

### Related articles

- [Solana Programs - Basic Security with Anchor]({{site.url_complet}}/2024/08/20/solana-smart-contract-basic-security/)
- [Introduction to Solana Anchor — Core Concepts and Testing]({{site.url_complet}}/2026/03/13/solana-anchor-introduction/)
- [Fuzzing Solana Programs with Trident]({{site.url_complet}}/2026/03/13/fuzzing-solana-programs-with-trident/)
