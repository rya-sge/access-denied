---
layout: post
title: "Cyfrin First Fight 41 - SSSwap"
date: 2025-07-11
lang: en
locale: en-GB
categories: solidity blockchain
tags: ctf cyfrin first-fight
description: First Fight 41 - SSSwap is aimed to be a minimalistic AMM on Solana.
image: 
isMath: false
---

The protocol is aimed to be a minimalistic AMM on Solana. A template, if you want to call it that way. Users can fork upon the project and integrate additional own logic, that's why I kept it simple. This article describes the [First Fight 41](https://codehawks.cyfrin.io/c/2025-05-ssswap) from Cyfrin.

The code is available on [GitHub](https://github.com/CodeHawks-Contests/2025-05-ssswap).

[TOC]



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

