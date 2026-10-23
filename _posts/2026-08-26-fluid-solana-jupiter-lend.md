---
layout: post
title: "Fluid on Solana — Porting a Liquidity Layer from the EVM to the SVM"
date:   2026-08-26
last_modified_at: 2026-10-22
lang: en
locale: en-GB
categories: blockchain defi solana
tags: blockchain solana defi rust anchor oracle fluid
description: Fluid's liquidity layer runs on Solana as Jupiter Lend. A read of its Anchor programs, from balance-delta deposits and tick PDAs to introspected flash loans.
image: /assets/article/blockchain/defi/fluid/2026-08-26-fluid-solana-jupiter-lend-mindmap.png
isMath: true
---

Fluid, the DeFi protocol formerly known as Instadapp, is built around a single idea: one contract holds every token the protocol has, and the lending market, the collateralised debt positions and the DEX are thin protocols that borrow accounting space from it rather than custody of their own. On Ethereum that contract is the Liquidity Layer, and everything above it reaches it through one function, `operate()`.

In 2025 that design was deployed on Solana under the name Jupiter Lend, a partnership between Fluid and Jupiter announced in May and launched in August. It is Fluid's first non-EVM deployment. The economics carried over intact: one shared reserve per token, tick-based liquidation, dynamic borrow and withdrawal ceilings. The mechanics did not, because most of the plumbing Fluid relies on has no equivalent on Solana. There is no `msg.sender` reaching a callee, no [ERC-20](https://eips.ethereum.org/EIPS/eip-20) allowance the pool can draw on, no reentrant callback, no `mapping` that materialises storage on first write, and no way to touch an account a transaction did not name in advance.

This article reads the six [Anchor]({{site.url_complet}}/2026/03/13/solana-anchor-introduction/) programs that make up the Solana deployment and looks specifically at the seams: which parts of the EVM design survived the port unchanged, which had to be rebuilt around Solana's account model, and what an integrator or a reviewer should know about the mechanisms that only exist on this side.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The program topology

Six programs are deployed on mainnet, and the split matches the EVM contract layout closely.

| Program | Program ID | Role |
|---------|-----------|------|
| Liquidity | `jupeiUmn818Jg1ekPURTpr4mFo29p46vygyykFJ3wZC` | Holds all funds, one reserve per mint |
| Lending | `jup3YeL8QhtSx1e253b2FDvsMNC87fDrgQZivbrndc9` | Yield-bearing shares over the liquidity layer |
| Lending reward rate model | `jup7TthsMgcR9Y3L277b8Eo9uboVSmu1utkuXHNUKar` | Reward schedule for the lending program |
| Vaults | `jupr81YtYssSyPt8jbnGuiWon5f6x9TcDEFxYe3Bdzi` | Collateralised debt positions |
| Oracle | `jupnw4B6Eqs7ft6rxpzYLJZYSnrpRgPcr589n5Kv4oc` | Price feeds, up to four chained sources |
| Flashloan | `jupgfSgfuAXv4B6R2Uxu85Z1qdzgju79s6MfZekN6XS` | Atomic loans repaid in the same transaction |

![Wallets and liquidators call Lending, Vaults and Flashloan, which reach the permissioned Liquidity program by cross-program invocation; Vaults also calls the Oracle]({{site.url_complet}}/assets/article/blockchain/defi/fluid/fluid-solana-two-layer-concept.png)

The liquidity program is permissioned in the same sense as its Solidity counterpart. End users never invoke it. A protocol becomes able to touch it only when governance runs `init_new_protocol`, which creates the `UserSupplyPosition` and `UserBorrowPosition` accounts that carry that protocol's own limits, and then `update_user_supply_config` and `update_user_borrow_config`, which set them. Until those configs are written the position sits at status `NotSet` and every operation on it fails.

## Reworking operate for a chain without allowances

On Ethereum, `IFluidLiquidityLogic.operate()` takes a `callbackData_` argument and calls back into the calling protocol's `liquidityCallback` to pull the deposit. The pool decides how much it wants, then reaches into the protocol and takes it. Two chain features make that work: an ERC-20 allowance the pool can spend, and reentrancy into the caller mid-execution.

Solana has neither. A cross-program invocation cannot re-enter the program that issued it, and SPL token transfers are pushed by whoever signs, never pulled by a third party. The Solana implementation inverts the flow.

### The pre_operate handshake

Deposits and paybacks run as three separate instructions or CPIs.

- **`pre_operate(mint)`.** The liquidity program records three fields on the `TokenReserve` account: `interacting_protocol` (the caller), `interacting_timestamp` (the current Unix second), and `interacting_balance` (the token vault's balance right now).
- **The transfer.** The calling protocol pushes tokens into the liquidity program's token vault with an ordinary SPL transfer. Nothing in the liquidity program participates.
- **`operate(supply_amount, borrow_amount, ...)`.** The program re-reads the vault balance, subtracts the snapshot, and checks that the difference matches what the signed amounts imply.

![A deposit in three steps: pre_operate snapshots the vault balance, the protocol pushes an SPL transfer, and operate rejects the call unless the balance delta lands in the expected band]({{site.url_complet}}/assets/article/blockchain/defi/fluid/fluid-solana-operate-balance-delta-workflow.png)

Two guards make the handshake safe against a caller trying to reuse someone else's deposit. The `interacting_protocol` must equal the current caller, and the `interacting_timestamp` must equal the current second, so a snapshot cannot be carried across into a later transaction. `operate` clears both fields with `reset_interacting_state()` before it returns, so a single `pre_operate` authorises exactly one `operate`.

```rust
if token_reserve.interacting_protocol != ctx.accounts.protocol.key()
    || token_reserve.interacting_timestamp != Clock::get()?.unix_timestamp.cast::<u64>()?
{
    return Err(ErrorCodes::DepositExpected.into());
}
```

### Why the tolerance is one percent

The balance check is a band, not an equality:

```rust
if net_amount_in < operate_amount_in
    || net_amount_in
        > operate_amount_in
            .safe_mul(FOUR_DECIMALS.safe_add(MAX_INPUT_AMOUNT_EXCESS)?)?
            .safe_div(FOUR_DECIMALS)?
{
    return Err(ErrorCodes::TransferAmountOutOfBounds.into());
}
```

With `FOUR_DECIMALS` at `1e4` and `MAX_INPUT_AMOUNT_EXCESS` at `100`, the accepted range is `[operate_amount_in, operate_amount_in × 1.01]`. The lower bound is strict, so a protocol can never credit itself more than it actually sent. The upper bound absorbs a rounding difference or a small transfer-hook surcharge without failing the transaction, and the excess simply stays in the vault as revenue. A protocol that sends more than one percent above the amount it declares gets an error rather than a silent donation.

Note what the check does *not* do: it never reads the transfer instruction. It only compares two balances. Any token program behaviour that changes the vault balance between the snapshot and the check is absorbed by the same arithmetic, which is why a fee-on-transfer or Token-2022 hook token can be listed without a special case, so long as its overhead stays inside the band.

## When a transfer cannot land

An EVM contract that owes a user tokens can always send them. On Solana it cannot, because the destination associated token account may not exist, may be frozen by the mint's freeze authority, or may belong to a Token-2022 mint whose transfer hook rejects the transfer. If a withdrawal reverts because of that, the position becomes unwithdrawable.

The liquidity program answers with a `TransferType` on every operation:

```rust
pub enum TransferType {
    SKIP,   // skip transfer
    DIRECT, // transfer directly to the user (no claim)
    CLAIM,  // transfer to claim account and then can be claimed by user later
}
```

Under `CLAIM`, `handle_transfer_or_claim` moves no tokens. It credits a `UserClaim` PDA and adds the amount to the reserve's `total_claim_amount`. The tokens stay in the vault but are earmarked, and every later transfer is checked against the earmark:

```rust
if balance - last_stored_claim_amount < transfer_params.amount {
    return Err(ErrorCodes::InsufficientBalance.into());
}
```

This makes claimed balances senior to the free vault balance. A user calls `claim` later, from a transaction they control, and can pick a fresh recipient token account at that point.

`SKIP` covers the case the EVM version handles implicitly: a smart-collateral or smart-debt operation where a supply and a borrow of equal size cancel out, and no transfer should happen at all.

## Storage: mappings become accounts

An EVM `mapping` needs no allocation. Writing to a new key costs gas and nothing else. Solana has no such thing: every piece of state lives in an account that must be created, rent-funded, and named by the transaction before the program runs. Fluid's vault protocol is unusually mapping-heavy, so this is where the port diverges most.

![A position PDA and its SPL NFT mint link to the vault config and state, to the per-tick and per-branch accounts, and to the sixteen tick-has-debt bitmap shards]({{site.url_complet}}/assets/article/blockchain/defi/fluid/fluid-solana-tick-branch-concept.png)

### One account per tick, one per branch

Every tick that has ever held debt is its own PDA under the seed `tick`, and every liquidation branch is its own PDA under `branch`. They are created by explicit admin instructions (`init_tick`, `init_branch`, `init_tick_id_liquidation`) rather than appearing on first write. Each is a `zero_copy` account with `#[repr(C, packed)]`, so the program reads fields straight out of the account buffer without deserialising, which matters when a single liquidation walks a dozen of them.

### The tick bitmap, split across sixteen accounts

Fluid finds the next tick carrying debt through a bitmap. On Solana that bitmap cannot be one account, because the tick range is large and account size is bounded. It is sharded:

```rust
pub const TICK_HAS_DEBT_ARRAY_SIZE: usize = 8;
pub const TICK_HAS_DEBT_CHILDREN_SIZE: usize = 32; // 32 bytes = 256 bits
pub const TICK_HAS_DEBT_CHILDREN_SIZE_IN_BITS: usize = TICK_HAS_DEBT_CHILDREN_SIZE * BIT_PER_BYTE;
pub const TICKS_PER_TICK_HAS_DEBT: usize =
    TICK_HAS_DEBT_ARRAY_SIZE * TICK_HAS_DEBT_CHILDREN_SIZE_IN_BITS; // 8 * 256 = 2048

// Total range: -16383 to 16383 = 32767 ticks
// Each index covers 2048 ticks, so we need 16 indices to cover all ticks
pub const TOTAL_INDICES_NEEDED: usize = 16;
```

Sixteen `TickHasDebtArray` accounts, each holding eight 256-bit maps, cover $$2048 \times 16 = 32768$$ tick slots, enough for the 32767 ticks in the range $$[-16383, 16383]$$. Searching downward for the next tick with debt walks the maps inside one account, and when it runs out it returns a flag saying the search must continue in the previous account, which the caller must have supplied. That is the structural cost of the port: a search that was a loop over storage slots becomes a loop over accounts the transaction had to predict.

### Passing the accounts

Because the set of ticks and branches a liquidation will touch is not known until it runs, `operate` and `liquidate` take their working accounts through Anchor's `remaining_accounts`, plus a small vector telling the program how the flat list is partitioned:

```rust
pub fn liquidate<'info>(
    ctx: Context<'_, '_, 'info, 'info, Liquidate<'info>>,
    debt_amt: u64,
    col_per_unit_debt: u128,
    absorb: bool,
    transfer_type: Option<TransferType>,
    remaining_accounts_indices: Vec<u8>, // sources, branches, ticks, tick_has_debt
) -> Result<(u128, u128)>
```

The program then validates ownership itself. `get_ticks_from_remaining_accounts` rejects any account not owned by the vault program, and rejects any tick whose stored `vault_id` does not match the vault being operated on. The account list is caller-supplied, so those two checks are what stands between the protocol and a forged tick.

`operate` uses a three-element vector (oracle sources, branches, tick bitmaps) and rejects any other length; `liquidate` uses four, adding the tick accounts. Getting the partition wrong is not a silent misread, because each segment is type-checked as it is loaded.

### Address lookup tables

A vault operation names the position, the vault config and state, two token reserves, two liquidity positions, two token vaults, two mints, the oracle and its sources, the current tick, the branches, and the bitmap shards. That does not fit in a legacy transaction. Each vault therefore carries a lookup table address on a dedicated `VaultMetadata` account, set by `update_lookup_table`, and the SDK builds every vault instruction as a versioned transaction against it. The common accounts (config, state, reserves, the first eleven branches, the oracle) live in the table; only the position-specific accounts are passed inline.

## Rates, exchange prices and limits

This layer is a near-literal port, down to the constants.

### Utilization and the rate curve

Exchange prices carry `1e12` precision (`EXCHANGE_PRICES_PRECISION`), rates carry `1e2` precision so that `10_000` means 100%. Utilization is computed on scaled values so that the interest-free and interest-bearing halves of the book stay comparable:

$$
\begin{aligned}
U = \frac{B_r \cdot P_b + B_f \cdot 10^{12}}{S_r \cdot P_s + S_f \cdot 10^{12}}
\end{aligned}
$$

where $$S_r, B_r$$ are the raw interest-bearing totals, $$S_f, B_f$$ the interest-free totals, and $$P_s, P_b$$ the supply and borrow exchange prices. When total supply is zero the function returns zero rather than dividing.

Two rate curves are available per token. `RateDataV1Params` has a single kink; `RateDataV2Params` has two, letting governance keep the rate flat through normal utilization and steep only past the second kink. A borrow that would push utilization above the reserve's `max_utilization` fails with `MaxUtilizationReached`, which is the cap that keeps a reserve from being drained to the point where lenders cannot exit.

### Dynamic withdrawal and debt limits

Each protocol holding a position on the liquidity layer has its own ceilings, and they move with time rather than being fixed. For withdrawals, the limit decays toward a floor as time passes since the last operation:

$$
\begin{aligned}
L_{\text{new}} = \max\left( L_{\text{prev}} - S \cdot p \cdot \frac{\Delta t}{D},\; S \cdot (1 - p) \right)
\end{aligned}
$$

Here $$S$$ is the protocol's supply, $$p$$ the configured `expand_percent`, $$D$$ the `expand_duration`, and $$\Delta t$$ the elapsed seconds. The floor term says that at most a fraction $$p$$ of the position can ever be withdrawn in one expansion window. Below `base_withdrawal_limit` the limit is set to zero and the whole position is withdrawable at once. Borrow limits work symmetrically, expanding from `base_debt_ceiling` toward `max_debt_ceiling`, and `max_debt_ceiling` is a hard cap that expansion never crosses.

The practical effect is that a bug in one protocol built on the liquidity layer cannot drain the shared pool faster than that protocol's own expansion schedule allows.

## The vault protocol

### Ticks encode the health factor

A vault position stores no debt figure. It stores a tick, and the debt follows from it:

$$
\begin{aligned}
\text{ratio}(t) = 1.0015^{t} \cdot 2^{48}
\end{aligned}
$$

with $$t \in [-16383, 16383]$$, giving ratios from `6093` to `13002088133096036565414295`. The ratio is debt over collateral, so a tick is a health factor and every position sitting at the same tick has the same one. Reading a position's debt is a multiplication:

$$
\begin{aligned}
D = \left\lfloor \frac{\text{ratio}(t) \cdot (C + 1)}{2^{48}} \right\rfloor + 1
\end{aligned}
$$

The `+1` on both the collateral and the result rounds debt up, in the protocol's favour. `get_ratio_at_tick` is the familiar binary-decomposition routine, fourteen precomputed factors of $$2^{64}/1.0015^{2^k}$$ multiplied together according to the bits of the tick, then reciprocated for positive ticks. The Solidity version works in 256-bit arithmetic; this one is rewritten for `u128` with an explicit `u256` helper for the products that would overflow.

Grouping positions by tick keeps liquidation cheap: a liquidator does not iterate positions, it walks ticks from the top down, and every position in a liquidated tick is liquidated by the same proportion.

### Branches and the debt factor

When a liquidation stops partway through a tick, the vault opens a branch. A `Branch` account records the tick where liquidation stopped (`minima_tick`), the sub-tick position within it (`minima_tick_partials`, out of `X30`), the debt still attached to it, and a `debt_factor`.

The debt factor is a big-number representation, 35 bits of coefficient and 15 bits of exponent, initialised to `(X35 << 15) | (1 << 14)`. Each liquidation multiplies it by the fraction of debt that survived:

$$
\begin{aligned}
f_{\text{new}} = f_{\text{old}} \cdot \frac{\text{liquidatable} - \text{liquidated}}{\text{liquidatable}}
\end{aligned}
$$

A position discovers it was liquidated lazily, on its next `operate`, by comparing its stored `tick_id` against the tick's `total_ids`, and it recovers its remaining collateral by walking the branch chain and applying the accumulated factors. Branches merge when a later liquidation absorbs an earlier one, at which point the merged branch keeps a connection factor instead of its own debt.

Above `liquidation_max_limit`, a position is not liquidated but absorbed: its collateral and debt move to the vault's `absorbed_col_amount` and `absorbed_debt_amount`, and a liquidator can take them without touching the tick machinery. The cap is on the pair rather than on the penalty alone: `update_core_settings` rejects any configuration where `liquidation_max_limit + liquidation_penalty` exceeds `MAX_LIQUIDATION_PENALTY`, that is 99.7%.

### Decimal normalisation

The EVM version works in each token's native decimals. The Solana version normalises everything to nine decimals before touching the tick math:

```rust
fn get_scale(decimals: u8) -> Result<u128> {
    if decimals <= MAX_TOKEN_DECIMALS {          // 9
        Ok(10u128.pow((MAX_TOKEN_DECIMALS - decimals).cast()?))
    } else {
        return Err(error!(ErrorCodes::VaultInvalidDecimals));
    }
}
```

Amounts are scaled up on the way into `operate` and unscaled on the way out, with `unscale_amounts_up` used wherever rounding must favour the protocol. A consequence worth noting is that the vault program refuses any mint with more than nine decimals outright, and the liquidity program independently refuses anything outside two to nine.

The minimum-size constants are expressed in normalised units, so their real value depends on the token. `MIN_DEBT` is `1e3` at nine decimals, which becomes `1e6` raw units for a six-decimal token such as USDC. Tokens below four decimals get a separate, much smaller set of constants.

### Position ownership is an SPL NFT

Fluid represents a position as an [ERC-721](https://eips.ethereum.org/EIPS/eip-721) token. Here `init_position` mints exactly one unit of a fresh mint and then removes the mint authority, producing a real non-fungible token with Metaplex metadata. Authority is checked against the token account rather than a stored owner field:

```rust
match position_token_account.delegate {
    COption::Some(ref delegate) if position_authority.key == delegate => {
        validate_owner(delegate, &position_authority.to_account_info())?;
        if position_token_account.delegated_amount != 1 { ... }
    }
    _ => validate_owner(&position_token_account.owner, ...)?,
};
```

So both the holder and an approved delegate holding exactly one unit can act on the position. The check runs only when the operation reduces safety (`new_col < 0 || new_debt > 0`), which means anyone may add collateral or repay debt on a position they do not own, exactly as on the EVM side.

One asymmetry at the analysed revision: `module::user::close_position` exists and is complete, but it is not exported as an instruction in `programs/vaults/src/lib.rs`. Positions cannot be closed and their rent reclaimed through the deployed program.

## The oracle program

The oracle composes a chain of hops at fifteen decimals (`RATE_OUTPUT_DECIMALS`), each of which can be inverted. Seven source types are supported: `Pyth`, `Chainlink`, `Redstone`, `StakePool`, `MsolPool`, `SinglePool` and `JupLend`.

`MAX_SOURCES` caps the `sources` vector at four entries, which is not the same as four hops. A `SinglePool` source occupies three consecutive entries and a `JupLend` source occupies four, and `init_oracle_config` validates that those runs are consecutive and internally consistent. A configuration built on `JupLend` therefore has room for exactly one hop, while one built on Pyth feeds alone can chain four.

The freshness rules differ by operation. `get_both_exchange_rate` returns two numbers from the same accounts, one for liquidation and one for user operations, under different thresholds:

| Parameter | Operate | Liquidate |
|-----------|---------|-----------|
| Maximum age of a timestamped feed | 600 s (10 min) | 7200 s (2 h) |
| Rejected when the confidence interval exceeds | 1/50 of the price (2%) | 1/25 of the price (4%) |

The direction of that asymmetry is deliberate. Liquidation accepts an older price, and a wider confidence interval around it, than a user operation, which is the safer of the two failure modes: if a Pyth publisher stalls during a market move, tightening liquidation would freeze the mechanism that protects the protocol from bad debt, while a stale price merely delays a user's borrow. Governance can tune the sources but not these thresholds, which are compile-time constants.

## Flash loans without a callback

An EVM flash loan hands control back to the borrower and checks the balance when control returns. Solana forbids the equivalent: a program cannot invoke a caller-supplied program and expect to regain control safely, and reentering the flash loan program is explicitly blocked.

Instead, `flashloan_borrow` reads the instruction sysvar and proves that repayment is already scheduled in the same transaction before it releases anything.

![flashloan_borrow checks the amount, rejects a stack height above one, scans later instructions for exactly one matching payback, and only then invokes operate]({{site.url_complet}}/assets/article/blockchain/defi/fluid/fluid-solana-flashloan-introspection-workflow.png)

The scan is strict on five counts at once. A candidate instruction must belong to the flash loan program, carry exactly sixteen data bytes, open with the hardcoded `flashloan_payback` discriminator, encode the same amount, and name an account list identical to the borrow's, position by position:

```rust
pub const FLASHLOAN_PAYBACK_DISCRIMINATOR: &[u8] = &[213, 47, 153, 137, 84, 243, 94, 232];
```

Any later instruction that belongs to the program but fails the match raises `FlashloanInvalidInstruction` rather than being skipped, so a borrower cannot bury a decoy call after the real payback. Finding two matches raises `FlashloanMultiplePaybacksFound`. Finding none raises `FlashloanPaybackNotFound`.

`get_stack_height() > FLASHLOAN_STACK_HEIGHT` rejects both instructions when invoked through a CPI, since the introspection only proves anything about top-level instructions. The fee is capped at `FLASHLOAN_FEE_MAX = 50`, half a percent, and the payback path re-runs the whole `pre_operate` handshake before transferring the principal plus fee.

## The lending program

The lending program is the fToken, and it is recognisably [ERC-4626](https://eips.ethereum.org/EIPS/eip-4626) reshaped for SPL. Shares are an SPL mint whose supply the program reads directly, so `total_assets()` is the mint supply times a token exchange price rather than a separately tracked balance.

The four entry points come in pairs, one plain and one slippage-bounded:

- **`deposit` / `deposit_with_min_amount_out`.** Assets in, shares out, with an optional floor on the shares minted.
- **`mint` / `mint_with_max_assets`.** Shares out, assets in, with an optional ceiling on the assets pulled.
- **`withdraw` / `withdraw_with_max_shares_burn`.** Assets out, shares burned, with an optional ceiling on the burn.
- **`redeem` / `redeem_with_min_amount_out`.** Shares in, assets out, with an optional floor on the assets returned.

Passing `u64::MAX` means the whole balance, in the direction that makes sense for each. The doc comments carry the EVM advice unchanged, recommending `deposit` over `mint` and `withdraw` over `redeem` on efficiency grounds, which reads slightly oddly on a chain that prices compute units rather than storage writes.

`calculate_new_token_exchange_price` folds the liquidity layer's supply exchange price together with the reward schedule from the reward rate model program, and refuses to run if the liquidity exchange price has moved backwards:

```rust
if new_liquidity_exchange_price < old_liquidity_exchange_price {
    return Err(ErrorCodes::FTokenLiquidityExchangePriceUnexpected.into());
}
```

`rebalance`, callable by a designated rebalancer, reconciles the program's own accounting with its actual position on the liquidity layer and folds accrued rewards into the orderbook.

## Governance and licensing

Three authorities separate what can be done from what can be initialised.

| Authority | Address | Scope |
|-----------|---------|-------|
| Upgrade | `4MsgBB5VPoTrUSp5XnfbViV386C1UnsTdifLBw33ZMSJ` | Program upgrades, behind a 12-hour timelock multisig |
| Program | `HqPrpa4ESBDnRHRWaiYtjv4xe93wvCS9NNZtDwR89cVa` | Rate curves, LTV, limits, delegation |
| Init | `3H8C6yYTXUcN9RRRDmcLDt3e4aZLYRRX4x2HbEjTqQAA` | Creating reserves, markets and vaults only |

The first two are jointly controlled by Jupiter and Fluid signers; the init authority sits with the Fluid team and can create new state but not reconfigure existing state. Both the program authority and the init authority are compiled into the programs as constants (`GOVERNANCE_MS`, `PROTOCOL_INIT_AUTH`), and `update_authority` refuses to set anything other than `GOVERNANCE_MS`, so rotating them requires an upgrade rather than a transaction. The source comment describes the init authority as a "temporary hardcoded solution ... to be improved later".

Beyond the three authorities, every program except the flash loan one keeps an on-chain auth list capped at ten entries (`MAX_AUTH_COUNT`), and the liquidity program adds a separate guardian list. A guardian can pause a protocol's supply or borrow side per mint without touching configuration, enforced by an account constraint rather than a runtime check.

The code is not open source. It ships under the [Business Source License 1.1](https://mariadb.com/bsl11/) with a change date of 2029-07-24, after which it converts to the open source licence named in the file. Two sets of math helpers are carved out as Apache 2.0 because they derive from other projects: the casting and safe-arithmetic files from Drift, and the `u256` routines from Orca's Whirlpools. The `NOTICE` also credits the SPL token-lending program as modified source, without naming specific files.

## Conclusion

The port keeps Fluid's economic design intact and rebuilds its plumbing. The shared reserve, the tick-based liquidation with branches and debt factors, the dual rate curves and the per-protocol expanding limits all carry over with the same constants. What changed is everything that depended on EVM execution semantics: the pull-based deposit became a snapshot-and-compare handshake, the reentrant flash loan callback became instruction introspection, the storage mapping became a set of PDAs the caller must name in advance, and the unconditional token transfer gained a claim fallback for the case where a destination account will not accept it.

For a reviewer, the parts that carry the most new risk are the ones with no EVM ancestor: the `interacting_*` handshake, whose safety rests on two equality checks and a reset; the caller-supplied account lists, whose safety rests on per-account owner and `vault_id` validation; and the flash loan introspection, whose safety rests on a byte-exact match against a hardcoded discriminator.

- **Risks.** All six programs are upgradeable by one Squads 4-of-6 multisig behind a 12-hour timelock, the shared reserve spreads any vault's unrecovered bad debt to every supplier of that mint with no insurance buffer, and liquidation runs on prices up to two hours old, with LSTs valued at their pool redemption rate rather than at market.

![Mindmap of Fluid on Solana covering deployment and governance, the liquidity layer, the SVM adaptations, the vault tick machinery, the oracle, flash loans and lending]({{site.url_complet}}/assets/article/blockchain/defi/fluid/2026-08-26-fluid-solana-jupiter-lend-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Liquidity layer** | The single program that custodies every token in the protocol; other programs hold accounting positions on it and reach it only by cross-program invocation. |
| **`operate`** | The one entry point handling supply, withdraw, borrow and payback through two signed amounts, positive for in, negative for out. |
| **`pre_operate`** | The instruction that snapshots the token vault balance and stamps the caller and timestamp, authorising exactly one subsequent `operate`. |
| **Exchange price** | A `1e12`-precision accumulator converting between raw (interest-bearing) amounts and actual token amounts, one for supply and one for borrow. |
| **Tick** | An integer $$t$$ in $$[-16383, 16383]$$ encoding a debt-to-collateral ratio of $$1.0015^{t} \cdot 2^{48}$$; all positions at one tick share a health factor. |
| **Branch** | An account recording where a partial liquidation stopped, carrying a debt factor that later lets an affected position compute what it has left. |
| **Debt factor** | A 35-bit coefficient with a 15-bit exponent, multiplied down by each liquidation to record the surviving fraction of a branch's debt. |
| **Absorb** | The path taken for a position past `liquidation_max_limit`: its collateral and debt move to vault-level totals instead of being liquidated tick by tick. |
| **Claim account** | A `UserClaim` PDA crediting tokens that stay in the vault because a direct transfer was not attempted, senior to the free vault balance. |
| **`remaining_accounts_indices`** | A small vector partitioning Anchor's flat `remaining_accounts` list into oracle sources, branches, ticks and bitmap shards. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| One `pre_operate` authorises at most one deposit-carrying `operate`. | `interacting_protocol` and `interacting_timestamp` equality checks, plus `reset_interacting_state()` at the end of `operate`. | The reset is skipped, or the timestamp check is relaxed to a range. |
| A protocol never credits itself more than it transferred in. | `net_amount_in < operate_amount_in` rejects with `TransferAmountOutOfBounds`. | The lower bound is loosened, or the snapshot is taken after the transfer. |
| Tokens earmarked to claim accounts cannot be paid out to anyone else. | Every transfer compares against `balance - total_claim_amount`. | `total_claim_amount` drifts from the sum of live `UserClaim` balances. |
| A tick or branch account supplied by the caller belongs to this vault and this program. | Owner check against `crate::ID` and `vault_id` equality when loading from `remaining_accounts`. | A loader is added that skips either check. |
| A borrow cannot push a reserve past its configured utilization cap. | `utilization > token_reserve.max_utilization` check in `operate`. | The check fires only when `borrow_amount > 0`, so utilization can still rise past the cap through a withdrawal; only the withdrawal limits bound that path. |
| A protocol cannot withdraw more than its expansion schedule allows. | `calc_withdrawal_limit_before_operate` and the `WithdrawalLimitReached` check. | `expand_percent` is set to 100%, collapsing the floor to zero. |
| A flash loan is released only when a matching payback is already in the transaction. | Forward scan of the instruction sysvar for exactly one byte-exact payback. | The discriminator or account-list comparison is weakened, or the scan tolerates unmatched program instructions. |
| Vault math never sees a token with more than nine decimals. | `get_scale` returns `VaultInvalidDecimals` above `MAX_TOKEN_DECIMALS`. | The cap is raised without widening the scaled arithmetic. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| The liquidity program is not callable by end users. | Integrate against Lending, Vaults or Flashloan; a direct `operate` from an unregistered signer has no position account and fails. |
| A deposit is three steps, not one. | Build `pre_operate`, transfer, `operate` in that order and in one transaction; the timestamp check makes splitting them across transactions fail. |
| Sending more than 1% above the declared amount fails. | Compute the exact amount including any transfer fee, rather than padding the transfer. |
| Withdrawals may be credited to a claim account instead of transferred. | Handle `TransferType::CLAIM` by calling `claim` afterwards; do not assume a balance change in the same transaction. |
| Vault instructions do not fit in a legacy transaction. | Read the vault's lookup table from its `VaultMetadata` account and send a versioned transaction. |
| The caller supplies tick, branch and bitmap accounts. | Simulate the operation to discover which accounts are needed, and re-derive them when a liquidation has moved the topmost tick. |
| Amounts passed to the vault are in native token decimals, not normalised. | Pass raw token amounts; `scale_amounts` and `unscale_amounts` are applied inside the program. |
| Liquidation reads a price that may be up to two hours old. | Do not assume the liquidation price matches a live market quote; size liquidations against the returned `col_per_unit_debt`. |
| Positions cannot be closed at the analysed revision. | Budget for the rent of every position account created; it is not currently reclaimable. |
| `close_claim_account` has an empty body. | Rent recovery comes from Anchor's `close = user` constraint, and the account context also requires the claim balance to be zero. |

### Risks

The protocol's own disclosure is short. The repository README has a "Security" section that points to the audit reports in [Jupiter's documentation repository](https://github.com/jup-ag/docs/tree/main/static/files/audits), gives two disclosure addresses (security@fluid.io and security@jup.ag), and describes the three authorities covered in the governance section above. No dedicated risk page turned up in the sources read for this article. What follows adds what the code and the mainnet deployment show. The on-chain facts come from read-only JSON-RPC calls to the public mainnet endpoint on 22 October 2026, between slots 460053497 and 460054186.

#### Smart contracts and transparency

- **The source is readable, but it is not open source and is not tied to the deployed binary.** The code is public under the BSL 1.1 described above. The ProgramData accounts show that five of the six programs were redeployed after the commit this article analyses (dated 26 August 2026): liquidity, lending and the reward rate model at slots 453953579, 453954884 and 453954509 (6 October 2026, 41 days later), vaults and oracle at slots 449989995 and 449989861 (24 September 2026, 29 days later). Only the flash loan program (slot 430476301, 3 July 2026) predates it. Whether the deployed bytecode matches any public commit was not checked.
- **Audits exist; their scope against the deployed code is unknown.** Jupiter's audit folder holds fifteen files whose names start with `lend-`: OtterSec (two), Offside (liquidity, oracle and flash loan, vault), MixBytes (vault), Zenith, Code4rena, two Certora formal-verification reports, and five whose names contain `amm`, which may concern another component. They were not read for this article, so which commit each one covers is open.
- **Every program is upgradeable, and one authority upgrades all six.** Each program account is owned by `BPFLoaderUpgradeab1e11111111111111111111111`, and each ProgramData account names `4MsgBB5VPoTrUSp5XnfbViV386C1UnsTdifLBw33ZMSJ` as upgrade authority; none has been made immutable. The upside is that a bug can be patched without migrating positions, which the redeployments above show is used. The other side is that whoever controls that authority can replace the logic of the program that holds every deposited token, and a single approval can rewrite all six programs at once.
- **The upgrade authority is a [Squads](https://squads.so/) v4 vault behind a 4-of-6 multisig with a 12-hour timelock.** `4MsgBB5…` is off the ed25519 curve (a PDA, with no private key) and is a data-less System account. The liquidity upgrade at slot 453953579 was executed by the Squads v4 program (`SQDS4ep65T869zMMBKyuUq6aD6EgTu8psMjkvj52pCf`, instruction `VaultTransactionExecute`) on behalf of multisig `J3mJ3wz6xkVUk3T8qHnuAYNxsRH3ixHsryYNZAU2vG8P`. Decoding that account at slot 460054156 gives a threshold of 4, six members all holding every permission, a `time_lock` of 43200 seconds (12 hours, matching the README), and the default config authority, so membership changes go through the same 4-of-6 vote and delay.
- **Two authorities are compiled in.** `GOVERNANCE_MS` and `PROTOCOL_INIT_AUTH` are constants, so replacing either key after a compromise needs an upgrade and its 12-hour wait.
- **The new mechanisms carry the most implementation risk.** The `interacting_*` handshake, the caller-supplied `remaining_accounts`, the instruction introspection of flash loans and the tick, branch and debt-factor bookkeeping are each small checks guarding large balances (*derived*). `close_position` is not exported, so position rent is locked at the analysed revision.

#### External dependencies

- **Oracles.** The oracle program accepts seven source types. Pyth, Chainlink and Redstone are timestamped feeds; user operations reject a price older than 600 seconds or a confidence interval wider than 2%, liquidation accepts 7200 seconds and 4%. Liquidation can therefore act on a price twelve times older than the one a borrow would accept, the trade-off discussed in [Pricing a Lending Position During an Incident]({{site.url_complet}}/2026/10/11/oracle-kinds-pricing-lending-position-incident/), and the Pyth integration pitfalls are covered in [Integrating Pyth Network Price Feeds]({{site.url_complet}}/2026/03/13/pyth-integration-security/). Which sources each live vault uses was not read.
- **Exchange-rate sources.** `StakePool`, `MsolPool` and `SinglePool` read the stake pool account itself; `StakePool` returns `total_lamports / pool_token_supply`, fails with `StakePoolNotRefreshed` when the pool has not been updated for the current epoch within its first hour, and rejects a pool whose fees exceed a ceiling. `JupLend` prices a jlToken from Jupiter Lend's own exchange price. These sources depend on the stake pool programs and on the lending program rather than on a market.
- **Jupiter.** The application at jup.ag, the SDK that builds the versioned transactions, and the lookup tables set by `update_lookup_table` are the usual path to the programs. If the front end or the lookup tables become unavailable, the programs still run, but a user has to build vault transactions by hand (*derived*).
- **Solana itself.** Every liquidation is a large versioned transaction that competes for block space and compute units, so under congestion it depends on priority fees and leader inclusion (*derived*). Solana mainnet has also halted block production several times since 2020; during a halt no price is updated and no position can be liquidated or withdrawn, and positions are repriced in one step when blocks resume (*derived*).
- **Token programs.** A mint's freeze authority or a Token-2022 transfer hook can block a transfer; the `CLAIM` path protects the user's side, but a freeze on the liquidity program's own token vault would lock that reserve for every protocol using it (*derived*).
- **Bridged assets and LSTs.** A bridged token is worth what its bridge redeems, and an LST what its stake pool holds; the listed reserves and their issuers were not checked for this article.

#### Depeg

- **LSTs are priced at redemption value, not at market.** Because `StakePool` returns the pool's lamports per token, a secondary-market discount on an LST does not move the oracle price. Borrowers looping an LST against SOL are not liquidated by a temporary discount, which avoids a cascade; the cost is that a liquidator who needs to sell the seized LST at once gets the market price, so the penalty has to cover the gap or liquidation stalls (*derived*). A real loss in the pool (slashing, a pool exploit) lowers `total_lamports` and is passed through.
- **jlTokens follow the reserve's exchange price.** The lending program refuses to run if the liquidity exchange price moves backwards, so a jlToken's price never falls; a shortfall in the reserve shows up as missing liquidity, not as a lower share price (*derived*).
- **Stablecoins.** Whether each stablecoin market prices the token through its own USD feed or treats it as equal to another asset was not read; in the second case a depeg would not show in the oracle price.

#### Collateral and market risk

- **The shared reserve spreads one vault's loss.** Every vault and the lending program draw on one reserve per mint. A vault whose bad debt is never repaid still owes its borrow position on the liquidity program, so the missing tokens are missing for every supplier of that mint, including jlToken holders who never used that vault (*derived*). The per-protocol `max_debt_ceiling` caps how much one vault can owe, which bounds this exposure.
- **Reflexive loops.** Looping an asset against itself or a near copy (an LST against SOL, a jlToken as collateral for the same underlying) multiplies exposure to one rate. For Pyth-priced volatile collateral, liquidators selling seized collateral on Solana venues push the market prices those feeds aggregate (*derived*).
- **Liquidation on a stale price.** With a two-hour tolerance a liquidation can run on a price far from the market. Liquidators act only when it pays, so a stale price that overstates collateral delays liquidation while the shortfall grows (*derived*).
- **Absorption limit.** `update_core_settings` keeps `liquidation_max_limit + liquidation_penalty` at or below 99.7%; positions beyond `liquidation_max_limit` are absorbed into vault-level totals instead of being liquidated tick by tick.

#### Liquidity

- **Utilization.** Suppliers cannot withdraw what is lent out. `max_utilization` stops a borrow, but not a withdrawal, from pushing utilization past the cap, and at full utilization exits wait for repayments or liquidations while the rate curve rises.
- **Withdrawal limits are per protocol, not per user.** The expanding withdrawal limit applies to the lending program's position as a whole, so all jlToken holders share one schedule; a large holder who withdraws first uses the window and the rest wait for it to expand (*derived*). The same mechanism is what bounds a drain by a buggy protocol.
- **Pauses.** A guardian can pause supply or borrow per mint for class 0 protocols (class 1, "established protocols", cannot be paused by guardians). An auth can set the liquidity program's status to locked with `change_status`, and the `ProtocolLockdown` constraint sits on the `PreOperate`, `Operate` and `Claim` contexts, so a lockdown stops withdrawals and claims as well as deposits.
- **Exit during an upgrade window.** The 12-hour timelock gives depositors time to leave before a malicious upgrade lands, but only within what utilization and withdrawal limits allow during those 12 hours (*derived*).

#### Centralisation and governance

The three authorities were read on chain. Each is a System-owned, data-less, off-curve address, and the multisig behind it was found from a `VaultTransactionExecute` it signed.

| Authority | Address | Squads v4 multisig | Threshold | Members (full permissions) | Timelock | Read at slot |
|-----------|---------|--------------------|-----------|----------------------------|----------|--------------|
| Upgrade | `4MsgBB5VPoTrUSp5XnfbViV386C1UnsTdifLBw33ZMSJ` | `J3mJ3wz6xkVUk3T8qHnuAYNxsRH3ixHsryYNZAU2vG8P` | 4 | 6 (6) | 43200 s (12 h) | 460054156 |
| Program (`GOVERNANCE_MS`) | `HqPrpa4ESBDnRHRWaiYtjv4xe93wvCS9NNZtDwR89cVa` | `5Y93cxqp8rGtjDhxGkehewfhFdxLkrCfPDWookCGeASF` | 4 | 9 (7) | 21600 s (6 h) | 460054171 |
| Init (`PROTOCOL_INIT_AUTH`) | `3H8C6yYTXUcN9RRRDmcLDt3e4aZLYRRX4x2HbEjTqQAA` | `B9fGPEBP1M4SvQgtG7egVrdL5N9zBxrFpdtZevTkhQ6o` | 3 | 7 (5) | none | 460054186 |

- **The program authority changes the economics on a six-hour delay.** It sets rate curves, LTV, limits and per-vault oracles (`update_oracle`), and was seen at slot 460047004 executing an `UpdateRateDataV1` on the liquidity program. Two of its nine members, and two of the init multisig's seven, hold only permission value 1, which in Squads v4 is the right to propose, not to vote.
- **The same keys sit on both sides.** Five of the six upgrade members are also full members of the program multisig (*derived* from the addresses). The README says Jupiter and Fluid signers share control; which key belongs to which team cannot be read on chain.
- **The init authority acts without delay.** A 3-of-7 vote with no timelock can create reserves, markets and vaults, though not reconfigure them.
- **Guardians and auths.** Guardian pauses and `change_status` go through auth and guardian lists that were not read; their members and any delay are open.
- **Off-chain parts.** The designated rebalancer of the lending program, the liquidator set, Jupiter's front end and SDK, and the lookup tables are operated off chain.

#### Loss sharing

- **No first-loss buffer found.** A search of the programs for an insurance fund or a bad-debt reserve found none. Debt above `liquidation_max_limit` moves into `absorbed_debt_amount` with its collateral; if that collateral is worth less than the debt, nothing in the code covers the difference.
- **Suppliers absorb it, in order of exit.** Since exchange prices never fall, an unrecovered shortfall is not shared pro rata through the price; the reserve simply holds fewer tokens than it owes, and the last suppliers to withdraw are the ones left short (*derived*). Revenue collected with `collect_revenue` could be used to refill a reserve, but that would be a governance decision, not a mechanism.

#### Regulatory

- **None found in the code.** The programs have no KYC or allow-list for end users. Admin control by identifiable teams bears on whether a service counts as fully decentralised under the EU framework described in [MiCA explained]({{site.url_complet}}/2026/09/17/mica-explained-scope-token-categories-timeline/), a question this article does not settle (*derived*).

#### Summary

| Risk | Where it comes from | What the design does about it | What remains |
|------|---------------------|-------------------------------|--------------|
| Malicious or faulty upgrade | All six programs share one upgrade authority | Squads v4 4-of-6 multisig, 12-hour timelock | Signers' identities unknown; exits limited during the window |
| Deployed code differs from reviewed code | Five programs redeployed after the analysed commit | Public source and fifteen audit files | No verified-build match checked |
| Stale or wrong price | Pyth, Chainlink, Redstone and pool-rate sources | Age and confidence checks, stricter for user operations | Liquidation accepts a two-hour-old price |
| LST market depeg | Pool redemption rate used as price | No liquidation cascade on a market discount | Liquidators sell at market; penalty must cover the gap |
| Bad debt in one vault | Shared reserve per mint | Per-protocol debt ceilings, absorb path | No insurance; last suppliers out take the loss |
| Locked withdrawals | High utilization, per-protocol withdrawal limits, pauses | Rate curve, expansion schedule, claim accounts | Lockdown blocks withdrawals and claims |
| Governance changes | Program authority sets rates, limits, oracles | 4-of-9 multisig, 6-hour timelock | Guardian and auth lists not read |
| Chain halt or congestion | Solana block production and fees | None in the programs | Positions repriced in one step after a halt |

## Frequently Asked Questions

**Q: Why can the Solana liquidity layer not use the same callback-based deposit as the EVM version?**

Two chain features the EVM design depends on are absent. First, there is no ERC-20 allowance, so the pool has no standing permission to move a caller's tokens; SPL transfers are always pushed by a signer. Second, a Solana cross-program invocation cannot re-enter the program that issued it, so the pool cannot call back into the protocol mid-execution to pull the deposit.

The replacement inverts the direction: the caller pushes tokens first, and the pool reconciles by comparing the token vault balance before and after against the amounts declared in `operate`.

**Q: What stops one protocol from crediting itself with a deposit that another protocol made?**

Three things acting together. `pre_operate` writes the caller's public key into `interacting_protocol` and the current Unix second into `interacting_timestamp`. `operate` refuses to proceed unless both match the current caller and the current second, so a snapshot cannot be reused by a different program or carried into a later transaction. `operate` then clears both fields, so a single `pre_operate` authorises exactly one deposit-carrying call.

**Q: Why does the balance check accept up to 1% more than the declared amount, and where does the excess go?**

The lower bound is what protects the protocol, and it is strict: crediting more than was actually received is impossible. The upper bound exists so that a rounding difference or a small transfer-hook surcharge does not abort an otherwise valid deposit. Anything received above the declared amount simply stays in the token vault and accrues to the protocol as revenue, so the tolerance costs the depositor rather than the pool.

**Q: What is a tick, and why does the vault store one instead of a debt figure?**

A tick is an integer $$t$$ that encodes a debt-to-collateral ratio as $$1.0015^{t} \cdot 2^{48}$$, over the range $$[-16383, 16383]$$. Because the ratio is the health factor, every position sitting at the same tick is equally healthy, and a position's debt is recovered by multiplying its collateral by the tick's ratio.

Storing the tick rather than the debt is what makes liquidation cheap. A liquidator walks ticks downward from the topmost one carrying debt and liquidates each tick as a unit, so the cost scales with the price range crossed rather than with the number of positions affected.

**Q: How does a flash loan guarantee repayment without a callback?**

Before releasing anything, `flashloan_borrow` reads the instruction sysvar and scans every instruction scheduled after it in the same transaction, looking for a `flashloan_payback` that matches on four counts: the program, a sixteen-byte payload opening with the hardcoded payback discriminator, the same amount, and an account list identical to the borrow's, position by position. Exactly one match is required; zero and two or more are both errors, and an instruction belonging to the program that fails the match is itself an error rather than being ignored.

Both instructions also require `get_stack_height() == 1`, because the introspection only proves anything about top-level instructions; running either through a CPI would let a caller schedule a payback that never executes.

**Q: The oracle accepts an older, less confident price for liquidation than for a user operation. Why is that the safe direction?**

Because the two operations fail differently. If prices go stale during a volatile period and the protocol refuses to liquidate, undercollateralised positions stay open and the shortfall becomes bad debt borne by lenders. If it refuses to let a user borrow, the user waits.

The thresholds encode that asymmetry directly. `operate` rejects a price older than 600 seconds or whose Pyth confidence interval exceeds 2% of the price; `liquidate` allows 7200 seconds and 4%. Both are compile-time constants rather than governance parameters, so changing the trade-off requires a program upgrade behind the 12-hour timelock.

**Q: A vault operation needs tick, branch and bitmap accounts that the caller has to name in advance. What keeps a caller from supplying forged ones?**

The program validates every account it loads out of `remaining_accounts` rather than trusting the partition vector. Each tick account must be owned by the vault program itself, checked against `crate::ID`, and each must carry a `vault_id` equal to the vault being operated on; the same holds for branch accounts. A forged account fails the owner check, and a genuine account from a different vault fails the id check.

What the caller does control is completeness. Supplying too few bitmap shards makes the downward search return a flag saying it cannot continue, which surfaces as a failed transaction rather than a wrong result.

## Gaps

The risk analysis above depends on these points, which the sources read did not settle.

| Gap | Why it matters | What to read or verify |
|-----|----------------|------------------------|
| Deployed bytecode against the analysed commit | Five programs were redeployed 29 to 41 days after commit `626b177`, so the code read may not be the code running. | Run a verifiable build of the repository and compare its hash with the ProgramData of each program. |
| Audit scope and commits | The fifteen `lend-` audit files were not read, so their findings and the commits they cover are unknown. | Read the reports in jup-ag/docs `static/files/audits` and note each audited commit. |
| Signer identities | The README says Jupiter and Fluid share control, but no on-chain read ties a key to a team. | Ask the teams or check published signer lists for multisigs `J3mJ3wz…`, `5Y93cxq…` and `B9fGPEB…`. |
| Guardian and auth lists | Who can pause a mint or lock the liquidity program, and how fast, was not read. | Read the `auth_list` PDA of the liquidity program and of each other program. |
| Oracle configuration per vault | Which feeds, hops and source types each live vault uses decides its staleness and depeg exposure. | Read each vault's `vault_config.oracle` and the matching oracle account's `sources`. |
| Listed assets | Bridged tokens, LSTs and stablecoins listed, and their issuers, were not checked. | List the liquidity program's `TokenReserve` accounts and their mints. |
| Bad-debt handling | No insurance or reserve was found in code; whether governance has covered shortfalls is undocumented. | Check Jupiter Lend and Fluid documentation and governance posts for a bad-debt policy. |
| Squads v4 permission values | The reading of permission value 1 as "propose only" comes from general knowledge of Squads v4, not from a source cited here. | Confirm the `Permissions` bitmask in the Squads v4 program source. |
| Solana halts | The statement that Solana mainnet has halted several times since 2020 is general knowledge. | Cite the Solana status page or incident reports for each halt. |

## References

### Analyzed source

- [Instadapp/fluid-solana-programs](https://github.com/Instadapp/fluid-solana-programs) — analyzed at commit [`626b177f235224bc5d074d39439cd2558f542886`](https://github.com/Instadapp/fluid-solana-programs/tree/626b177f235224bc5d074d39439cd2558f542886) on branch `main`, no tag on that commit, 2026-08-26

### Specifications and licences

- [ERC-4626: Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-4626)
- [Business Source License 1.1](https://mariadb.com/bsl11/)
- [Anchor framework documentation](https://www.anchor-lang.com/docs)
- [Solana instructions sysvar](https://docs.rs/solana-program/latest/solana_program/sysvar/instructions/index.html)
- [Address lookup tables](https://solana.com/developers/guides/advanced/lookup-tables)

### Protocol documentation

- [Fluid documentation](https://docs.fluid.instadapp.io/)
- [Jupiter Lend](https://jup.ag/lend)
- [Jupiter audit reports](https://github.com/jup-ag/docs/tree/main/static/files/audits)

### Ecosystem analysis and reporting

- [Fluid — Dripping onto Solana, Messari](https://messari.io/report/fluid-dripping-onto-solana)
- [Understanding Fluid — A Comprehensive Overview, Messari](https://messari.io/report/understanding-fluid-a-comprehensive-overview)
- [Solana DEX aggregator Jupiter unveils a new lending protocol, The Block](https://www.theblock.co/post/355466/liquidity-begets-liquidity-solana-dex-aggregator-jupiter-unveils-a-new-lending-protocol)
- [Jupiter Lend — An Emerging Pillar in Solana's DeFi Superapp, Kairos Research](https://www.kairosresear.ch/p/jupiter-lend-an-emerging-pillar-in)

### Derivative work credited in the repository

- [Drift Protocol math functions](https://github.com/drift-labs/protocol-v2/blob/master/programs/drift/src/math/)
- [Orca Whirlpools u256 math](https://github.com/orca-so/whirlpools/blob/810f504e323f814c7b9fc3f59af53428b9cc92b1/programs/whirlpool/src/math/u256_math.rs)
- [SPL token-lending program](https://github.com/solana-labs/solana-program-library/tree/master/token-lending)

### Related articles

- [Introduction to Solana Anchor — Core Concepts and Testing]({{site.url_complet}}/2026/03/13/solana-anchor-introduction/)
- [Solana Core Concept]({{site.url_complet}}/2024/09/19/solana-core-concept/)
- [Integrating Pyth Network Price Feeds — A Security-Focused Guide]({{site.url_complet}}/2026/03/13/pyth-integration-security/)
