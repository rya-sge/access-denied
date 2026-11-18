---
layout: post
title: "Cyfrin First Fight 41 - SSSwap"
date: 2025-07-11
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: solidity blockchain
tags: ctf cyfrin first-fight
series: cyfrin-first-fight
description: "Cyfrin First Fight 41, SSSwap: a minimal AMM on Solana built with Anchor, with my submission on vault reloads and the high-severity findings I missed."
image: /assets/article/blockchain/audit/2025-07-11-cyfrin-first-fight-41-ssswap-mindmap.png
isMath: false
---

The protocol is aimed to be a minimalistic AMM on Solana. A template, if you want to call it that way. Users can fork upon the project and integrate additional own logic, that's why I kept it simple. This article describes the [First Fight 41](https://codehawks.cyfrin.io/c/2025-05-ssswap) from Cyfrin.

The code is available on [GitHub](https://github.com/CodeHawks-Contests/2025-05-ssswap).

[TOC]

## What you need to know first

The findings below rely on a few AMM and Solana mechanisms that the submissions use without explaining.

- **Constant-product AMM and LP tokens**: an [automated market maker]({{site.url_complet}}/2025/07/29/automated-market-makers-amm/) holds two token reserves and prices swaps from their ratio. Liquidity providers receive LP tokens for their share; in the Uniswap V2 design, the first deposit mints `sqrt(amountA × amountB)` and later deposits mint in proportion to the existing LP supply, which is the rule H-01 says SSSwap breaks.
- **Solana accounts and SPL token accounts**: on [Solana]({{site.url_complet}}/2024/09/19/solana-core-concept/), programs hold no state of their own; data and balances live in separate accounts passed to each instruction. The pool's `vault_a` and `vault_b` are SPL token accounts, and their `amount` field is the reserve every calculation reads.
- **Anchor account deserialization and `.reload()`**: in [Anchor]({{site.url_complet}}/2026/03/13/solana-anchor-introduction/), an `Account<'info, T>` is deserialized into memory when the instruction starts. If a cross-program invocation later changes the account's data, the in-memory copy keeps the old values until the program calls `.reload()`, which is the subject of the H4 submission.
- **CPIs and PDA signers**: token transfers and LP mints are cross-program invocations (CPIs) to the SPL Token program. When the authority is the pool's program-derived address (PDA), the program signs for it by passing the PDA seeds to `CpiContext::new_with_signer`, as in the H-05 mitigation.
- **Slippage and front-running**: the state of a pool can change between the moment a user signs a transaction and the moment it executes, for instance when an attacker's swap lands first. Swap instructions bound this with `min_out` or `max_in`; H-02 points out that `provide_liquidity` has no such bound on `amount_b`.
- **Checked integer arithmetic in Rust**: amounts are `u64` integers, and `checked_mul` or `checked_div` return `None` on overflow or division by zero instead of producing a wrapped value. The code widens to `u128` before multiplying so that the product of two `u64` amounts fits.
- **Token decimals**: an SPL mint stores a `decimals` field, and every balance is an integer count of the smallest unit. A pool that pairs tokens with very different decimals compares raw integers of very different scales, which H-03 flags.

## Description

- It provides the absolute barebones of AMM functionality:

  - Pool Creation
  - Liquidity Operations
  - Swap Exact In and Exact Out
  - It has Slippage Protection
  - It has LP Fee Collection

  

You will realize that commonly used functions like "preview swap" and "get price" are missing, which is intended for the current state. I might decide to add those at a later point.

The audit is supposed to focus on the code validation of what is written and invariants I believe are important are documented within the natspec of the functions in lib.rs.



## My submissions

### H4-provide_liquidity does not reload vault value

> **Note added after the contest:** the root cause described in this submission does not hold. Anchor deserializes `vault_a` and `vault_b` when the instruction starts, so any transfer made before `provide_liquidity` runs, including one in an earlier instruction of the same transaction, is already reflected in the values read by `calculate_token_b_provision_with_a_given`. `.reload()` is only needed when a cross-program invocation inside the same instruction changes an account after it was deserialized, and here the calculation happens before the transfers. The submission is kept below as it was sent.

#### Root + Impact

#### Description

- In normal behavior, a liquidity provider deposits `amount_a` of token A, and the program computes the corresponding `amount_b` of token B needed to maintain the pool ratio. Then both amounts are transferred to the pool vaults, and the appropriate number of LP tokens is minted to the user.
- However, the function `calculate_token_b_provision_with_a_given` depends on reading accurate vault balances. If the vault accounts are not explicitly reloaded (`.reload()`), the cached state may not reflect recent external token transfers, causing the amount of token B to be miscalculated.

```rust
pub fn provide_liquidity(context: Context<ModifyLiquidity>, 
    amount_a: u64
) -> Result<()> {
    let amount_b = calculate_token_b_provision_with_a_given(
        &mut context.accounts.vault_a,
        &mut context.accounts.vault_b,
        amount_a
    )?;
​
    transfer_tokens(
        &context.accounts.liquidity_provider_token_a, 
        &mut context.accounts.vault_a,
        &amount_a, 
        &context.accounts.token_a_mint, 
        &context.accounts.liquidity_provider, 
        &context.accounts.token_program
    )?;
```



#### Risk

**Likelihood**:

- This will occur when tokens have been transferred into either `vault_a` or `vault_b` before the instruction executes, either as part of a batched transaction or as an external manipulation.
- Programs using cached account state without a fresh `.reload()` are susceptible to using outdated balances, particularly in multi-instruction transactions.

**Impact**:

- The calculated `amount_b` could be incorrect, leading to an imbalance in the pool and unfair liquidity provision.
- LP tokens could be minted at an incorrect ratio, diluting other liquidity providers or benefiting manipulators.

#### Proof of Concept

External actor or same user pre-loads vault_a with extra tokens
`send_tokens_to(vault_a, 10_000);`

Then provides liquidity based on stale vault_a reserve
`provide_liquidity(amount_a = 100_000);`

vault_a balance appears lower than reality during calculation, but includes added tokens during transfer
// This creates misalignment between expected and actual pool state

## Recommended Mitigation

Always reload token accounts before using them in reserve-sensitive calculations to prevent stale state from impacting logi

```rust
 context.accounts.vault_a.reload()?;
```

```rust
context.accounts.vault_b.reload()?;
```



## Missing submissions

### H-01. Incorrect LP Token Calculation in `provide_liquidity` Instruction

```rust
let lp_to_mint: u64 = liquidity_calculation(amount_a, amount_b)?;
```

```rust
fn liquidity_calculation(amount_token_a: u64, amount_token_b: u64) -> Result<u64> {
    // Converts both amounts to u128 to avoid overflow during multiplication.
    let amount_a_u128 = amount_token_a as u128;
    let amount_b_u128 = amount_token_b as u128;
	
    /** Multiplies token A and B amounts.
	* Uses .checked_mul() to safely multiply without overflow.
	* If multiplication fails (i.e., overflow), returns an AmmError::Overflow error.

	* Takes the square root of the product, which is a common formula in AMMs (like Uniswap v2) for initial liquidity:

	* LP tokens to mint = sqrt(amountA × amountB)
*/

    let lp_amount_to_mint_u128 = amount_a_u128
        .checked_mul(amount_b_u128)
        .ok_or(AmmError::Overflow)? 
        .sqrt(); 
	
    let lp_amount_to_mint = lp_amount_to_mint_u128 as u64; // Cast back to u64

    // Check if the result is zero (could happen with very small initial amounts)
    if lp_amount_to_mint == 0 {
        return err!(AmmError::LpAmountCalculation); 
    }

    Ok(lp_amount_to_mint) 
}
```



This calculation is only correct during the **initial pool creation** (when no LP tokens exist yet). For subsequent liquidity additions, the LP token amount must be proportional to the existing LP supply and reserves.

#### Impact

Using the initial pool creation formula to mint LP tokens on additional liquidity deposits will cause:

- **Incorrect LP token minting:** The amount of LP tokens minted will not reflect the depositor’s true share of the pool.
- **Imbalanced LP token distribution:** Liquidity providers may receive too many or too few LP tokens, resulting in unfair shares.
- **Economic exploits:** Malicious actors could exploit this miscalculation to mint more LP tokens than deserved, diluting other liquidity providers’ holdings.
- **Pool state inconsistency:** Pool accounting and invariant assumptions may break, causing downstream issues in swaps or removals.

#### Correct LP Token Calculation for Adding Liquidity

When liquidity already exists, LP tokens to mint must be proportional to the existing LP supply and token reserves. The correct formula is:

```rust
lpA = (amountA * totalSupply) / reserveA;
lpB = (amountB * totalSupply) / reserveB;
lpTokensToMint = min(lpA, lpB);
```

Where:

- `totalSupply` is the current total supply of LP tokens.
- `reserveA` and `reserveB` are the current token balances in the pool vaults.

#### Recommended Fix

Replace the incorrect call to `liquidity_calculation` with a function that:

1. Fetches the current total LP token supply.
2. Fetches the current vault balances (reserves) of tokens A and B.
3. Calculates `lp_to_mint` as the minimum of the proportional LP tokens derived from each token amount relative to reserves and total LP supply.

```rust
fn calculate_lp_tokens_to_mint(
    amount_a: u64,
    amount_b: u64,
    reserve_a: u64,
    reserve_b: u64,
    total_lp_supply: u64,
) -> Result<u64> {
    let lp_a = (amount_a as u128)
        .checked_mul(total_lp_supply as u128)
        .ok_or(AmmError::Overflow)?
        .checked_div(reserve_a as u128)
        .ok_or(AmmError::DivideByZero)?;

    let lp_b = (amount_b as u128)
        .checked_mul(total_lp_supply as u128)
        .ok_or(AmmError::Overflow)?
        .checked_div(reserve_b as u128)
        .ok_or(AmmError::DivideByZero)?;

    let lp_to_mint = lp_a.min(lp_b);

    if lp_to_mint == 0 {
        return err!(AmmError::LpAmountCalculation);
    }

    Ok(lp_to_mint as u64)
}
```

### H-02. Lack of Deposit Slippage Protection in the `liquidity_operations::provide_liquidity` function

**Description**: The AMM doesn't provide slippage protection for liquidity providers, potentially exposing them to front-running attacks. While the swap functions include slippage protection parameters ( `min_out` and `max_in` ), the liquidity provision function doesn't have similar protection. When a user provides liquidity by specifying only `amount_a` , the contract calculates `amount_b` based on the current pool ratio. However, if the pool ratio changes between transaction submission and execution (due to front-running), the user might provide more `amount_b` than expected.

**Impact**:

1. Liquidity providers are vulnerable to front-running attacks
2. Users may provide more tokens than intended if pool ratios change
3. Economic loss for liquidity providers

**Proof of Concept**:

```rust
// User wants to provide liquidity with 100 token A
// Current pool: 1000 A, 500 B
// Expected amount_b = (100 * 500) / 1000 = 50 B

// Attacker front-runs with a large swap that changes the ratio
// New pool: 800 A, 625 B
// Actual amount_b = (100 * 625) / 800 = 78.125 B

// User ends up providing ~28 more token B than expected
```

**Recommended Mitigation**: Add a maximum token B parameter to the liquidity provision function:

```rust
    pub fn provide_liquidity(
        context: Context<ModifyLiquidity>, 
        amount_a: u64,
        max_amount_b: u64  // New parameter
    ) -> Result<()> {
        let amount_b = calculate_token_b_provision_with_a_given(
            &mut context.accounts.vault_a,
            &mut context.accounts.vault_b,
            amount_a
        )?;
        
        // Add slippage protection
        require!(amount_b <= max_amount_b, AmmError::Slippage);
        
        // Rest of the function...
        
        Ok(())
    }
```



### H-03. No Input Validation for Token Decimals in the `liquidity_operations::initialize_pool` function

**Description**: The AMM doesn't validate token decimals, potentially allowing incompatible tokens or tokens with extreme decimal values. The AMM doesn't validate the decimal places of tokens when creating a new pool. This could allow the creation of pools with tokens that have extreme decimal values (e.g., 0 or >18) or incompatible decimal combinations, leading to calculation issues.

**Impact**:

1. Pools with tokens having extreme decimal values could experience calculation errors
2. Incompatible decimal combinations could lead to unfair pricing
3. Potential for precision loss in calculations

**Proof of Concept**: A user could create a pool with a custom token having 0 decimals and another with 30 decimals:

```
// In initialize_pool, no validation of token_mint_a.decimals or token_mint_b.decimals
// This allows creation of pools with any decimal combination
```



**Recommended Mitigation**: Add decimal validation in the `initialize_pool` function:

```rust
    pub fn initialize_pool(context: Context<InitializePool>, amount_token_a: u64, amount_token_b: u64) -> Result<()> {
        // Existing validation...
        
        // Validate token decimals
        let decimals_a = context.accounts.token_mint_a.decimals;
        let decimals_b = context.accounts.token_mint_b.decimals;
        
        // Ensure decimals are within reasonable range
        require!(decimals_a > 0 && decimals_a <= 18, AmmError::InvalidTokenDecimals);
        require!(decimals_b > 0 && decimals_b <= 18, AmmError::InvalidTokenDecimals);
        
        // Optionally, limit decimal difference to prevent extreme imbalances
        let decimal_diff = if decimals_a > decimals_b {
            decimals_a - decimals_b
        } else {
            decimals_b - decimals_a
        };
        require!(decimal_diff <= 12, AmmError::IncompatibleTokenDecimals);
        
        // Rest of the function...
    }
```



### H-05. No Minimum Liquidity Lock in the `liquidity_operations::remove_liquidity` function

H-05. No Minimum Liquidity Lock in the `liquidity_operations::remove_liquidity` function

**Description**: The AMM doesn't permanently lock a minimum amount of liquidity, allowing complete drainage of pools and potential numerical precision issues. The AMM allows liquidity providers to remove 100% of their liquidity from the pool. This creates scenarios where pools can be completely drained, leading to division by zero errors or extremely small reserves that cause precision issues. Most AMM protocols (like Uniswap) permanently lock a small amount of liquidity to prevent these edge cases.

**Impact**:

1. Pools can be completely drained, causing subsequent operations to fail
2. Extremely small reserves can lead to precision issues and unfair pricing
3. Potential for temporary DoS of specific pools

**Proof of Concept**: A user who owns 100% of the LP tokens can remove all liquidity:

```rust
    // User has all LP tokens (total_supply)
    // In remove_liquidity function:
    let amount_a_to_return_u128 = (total_supply as u128)
        .checked_mul(reserve_a as u128)
        .ok_or(AmmError::Overflow)?
        .checked_div(total_supply as u128)
        .ok_or(AmmError::DivisionByZero)?;
    // This returns all of reserve_a

    // Same for reserve_b
    // Result: Pool is completely drained
```



**Recommended Mitigation**: Implement a minimum liquidity lock mechanism in the `initialize_pool` function:

```rust
    pub fn initialize_pool(context: Context<InitializePool>, amount_token_a: u64, amount_token_b: u64) -> Result<()> {
        // Existing code...
        
        // Calculate LP tokens to mint
        let lp_amount_to_mint: u64 = liquidity_calculation(amount_token_a, amount_token_b)?;
        
        // Define minimum liquidity to lock (e.g., 1000)
        const MINIMUM_LIQUIDITY: u64 = 1000;
        
        // Ensure we're minting enough to lock some
        require!(lp_amount_to_mint > MINIMUM_LIQUIDITY, AmmError::InsufficientInitialLiquidity);
        
        // Mint LP tokens to creator
        let creator_lp_amount = lp_amount_to_mint - MINIMUM_LIQUIDITY;
        
        // Mint to creator
        mint_to(cpi_context, creator_lp_amount)?;
        
        // Mint minimum liquidity to a dead address or the protocol itself
        let cpi_accounts_min_liquidity = MintTo {
            mint: context.accounts.lp_mint.to_account_info(),
            to: dead_address_account.to_account_info(), // An account that can never spend
            authority: context.accounts.liquidity_pool.to_account_info(),
        };
        let cpi_context_min_liquidity = CpiContext::new_with_signer(
            context.accounts.token_program.to_account_info(),
            cpi_accounts_min_liquidity,
            signer_seeds,
        );
        mint_to(cpi_context_min_liquidity, MINIMUM_LIQUIDITY)?;
        
        Ok(())
    }
```

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Automated Market Maker (AMM)** | A program that holds two token reserves and lets users swap between them at a price derived from the reserves, with no order book. |
| **Liquidity pool** | The pair of token vaults, together with the pool account, that an AMM trades against and that liquidity providers fund. |
| **Vault** | A token account owned by the pool (here `vault_a` and `vault_b`) whose balance is the reserve used in every pricing and LP calculation. |
| **Liquidity provider (LP)** | A user who deposits both tokens into the pool in the current ratio and receives LP tokens in exchange. |
| **LP token** | A token minted to liquidity providers that represents their share of the pool and is redeemed through `remove_liquidity` for that share of the reserves. |
| **Initial LP mint** | The `sqrt(amountA × amountB)` formula used when no LP tokens exist yet; H-01 shows SSSwap reuses it for every later deposit. |
| **Proportional LP mint** | The rule for later deposits, `min(amountA × totalSupply / reserveA, amountB × totalSupply / reserveB)`, which keeps each provider's share fair. |
| **Slippage protection** | A bound set by the user, such as `min_out`, `max_in` or the proposed `max_amount_b`, that makes the instruction fail if the pool moves too far before execution. |
| **Front-running** | An attacker getting a transaction, such as a large swap, executed before the victim's so that the victim's instruction runs against a changed pool ratio. |
| **Minimum liquidity lock** | A small amount of LP tokens minted to an account that can never spend them, so that the pool can never be fully drained to zero reserves. |
| **Token decimals** | The `decimals` field of an SPL mint, which sets how many smallest units make one token; SSSwap accepts any value when a pool is created. |
| **Cross-program invocation (CPI)** | A call from one Solana program to another, used here to transfer tokens and mint LP tokens through the SPL Token program. |
| **Program-derived address (PDA)** | An address owned by a program rather than a key pair, for which the program signs a CPI by providing the seeds, as the pool does for LP mints. |
| **`.reload()`** | The Anchor method that re-reads an account's data from the runtime, replacing a copy deserialized earlier in the instruction. |
| **Checked arithmetic** | Rust methods such as `checked_mul` and `checked_div` that return an error value on overflow or division by zero, which the code maps to `AmmError` variants. |

## Mindmap

The mindmap below summarizes the article.

![First Fight 41 SSSwap mindmap]({{site.url_complet}}/assets/article/blockchain/audit/2025-07-11-cyfrin-first-fight-41-ssswap-mindmap.png)
