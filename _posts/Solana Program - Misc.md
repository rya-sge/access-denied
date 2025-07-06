# Solana Program - Misc

[TOC]



##  Summary: How Re-Initialization Is Prevented

| Mechanism                 | Purpose                                  |
| ------------------------- | ---------------------------------------- |
| PDA derivation with seeds | Ensures unique pool account per pair     |
| `load_init()`             | Panics if account is already initialized |
| `#[account(init)]`        | Creates account once; fails on re-init   |
| Token order constraint    | Prevents reverse-pair duplication        |

## Reload

Code:

Context: Solana AMM, swap operation

```rust
context.accounts.token_vault_a.reload()?;
context.accounts.token_vault_b.reload()?;
```

### Why Use `reload()`?

Solana CPI calls can modify accounts mid-instruction. If you've **already transferred tokens** in this instruction (like during `initialize_pool` or `swap`), you must `reload()` to get the updated balances before doing calculations.

Failing to do this could lead to:

- Wrong swap outcomes
- Bad LP token minting
- Price desyncs

Failing to do this could lead to:

- Wrong swap outcomes
- Bad LP token minting
- Price desyncs

### In the function swap

After reloading, you **read the actual token balances** from the vaults.

These values represent the **current liquidity reserves** in the AMM:

- `reserve_a` = number of Token A in the pool
- `reserve_b` = number of Token B in the pool

These values are used in **swap math**, like:
$$
amout_{in} = \frac{reserve_a * amount_{out}} {reserve_b - amount_{out}}
$$

#### Alternative

 However, **reserves (amounts)** are **not explicitly stored** in the pool. If you plan to **cache reserves** for performance or accounting, they should be added and updated here, e.g.:

```
rustCopyEditreserve_a: amount_token_a,
reserve_b: amount_token_b,
```

Otherwise, the pool must always rely on `.reload()?.amount` from vaults for real-time reserve state (which is valid, but less efficient if you're calling frequently).

## Load init

> Returns a `RefMut` to the account data structure for reading or writing. Should only be called once, when the account is being initialized.

Context: Solana AMM (Raydium), Pool initialization

Code: [raydium-io/raydium-cp-swap/blob/master/programs/cp-swap/src/instructions/initialize.rs#L222]( https://github.com/raydium-io/raydium-cp-swap/blob/master/programs/cp-swap/src/instructions/initialize.rs#L222)

Documentation: [docs.rs/anchor-lang - struct.AccountLoader.html](https://docs.rs/anchor-lang/latest/anchor_lang/accounts/account_loader/struct.AccountLoader.html), [docs.rs/anchor-lang - struct.AccountLoader.html#method.load_init](https://docs.rs/anchor-lang/latest/anchor_lang/accounts/account_loader/struct.AccountLoader.html#method.load_init)

```rust
let pool_state = &mut pool_state_loader.load_init()?;
```

```rust
let mut observation_state = ctx.accounts.observation_state.load_init()?;
```

Fail if the account was already initialized

Ensuring that a re-execution of initialize() will revert (i.e., return an error)