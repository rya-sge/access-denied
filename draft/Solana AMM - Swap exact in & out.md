# Solana AMM - Swap exact in & out



## Swap Exact out

```rust
pub fn swap_exact_out(context: Context<SwapContext>, amount_out: u64, max_in: u64, zero_for_one: bool) -> Result<()> {
    context.accounts.token_vault_a.reload()?;
    context.accounts.token_vault_b.reload()?;
    let reserve_a: u64 = context.accounts.token_vault_a.amount;
    let reserve_b: u64 = context.accounts.token_vault_b.amount;

    require!(reserve_a > 0 && reserve_b > 0, AmmError::PoolIsEmpty);
    require!(amount_out > 0, AmmError::NoZeroAmount);
    
    if zero_for_one {
        require!(amount_out < reserve_b, AmmError::InsufficientLiquidity);

        let numerator: u128 = (reserve_a as u128)
            .checked_mul(amount_out as u128)
            .ok_or(AmmError::Overflow)?;
        let denominator: u128 = (reserve_b as u128)
            .checked_sub(amount_out as u128)
            .ok_or(AmmError::Underflow)?;

        require!(denominator > 0, AmmError::DivisionByZero); 

        let amount_in_no_fee: u64 = numerator.div_floor(&denominator) as u64;

        let fee_numerator_u128 = (amount_in_no_fee as u128)
            .checked_mul(3)
            .ok_or(AmmError::Overflow)?;
        let lp_fees: u64 = fee_numerator_u128.div_floor(&1000) as u64;
        
        let amount_in_final = (amount_in_no_fee as u128)
            .checked_add(lp_fees as u128)
            .ok_or(AmmError::Overflow)? as u64;

        require!(amount_in_final > 0 || (amount_in_final == 0 && amount_out == 0), AmmError::CalculationFailure);
        require!(amount_in_final <= max_in, AmmError::Slippage);

        transfer_tokens(
            &context.accounts.user_token_a,
            &mut context.accounts.token_vault_a,
            &amount_in_final,
            &context.accounts.token_a,
            &context.accounts.user,
            &context.accounts.token_program,
        )?;

        let token_a_key = context.accounts.token_a.key();
        let token_b_key = context.accounts.token_b.key();
        let bump_seed = [context.bumps.liquidity_pool];

        let signer_seeds: &[&[&[u8]]] = &[&[
            b"pool",
            token_a_key.as_ref(),
            token_b_key.as_ref(),
            &bump_seed,
        ]];

        let cpi_accounts_transfer_out = TransferChecked {
            from: context.accounts.token_vault_b.to_account_info(),
            mint: context.accounts.token_b.to_account_info(),
            to: context.accounts.user_token_b.to_account_info(),
            authority: context.accounts.liquidity_pool.to_account_info(),
        };
        let cpi_context_transfer_out = CpiContext::new_with_signer(
            context.accounts.token_program.to_account_info(),
            cpi_accounts_transfer_out,
            signer_seeds,
        );
        transfer_checked(cpi_context_transfer_out, amount_out, context.accounts.token_b.decimals)?
    } else {
        require!(amount_out < reserve_a, AmmError::InsufficientLiquidity);

        let numerator: u128 = (reserve_b as u128)
            .checked_mul(amount_out as u128)
            .ok_or(AmmError::Overflow)?;
        let denominator: u128 = (reserve_a as u128)
            .checked_sub(amount_out as u128)
            .ok_or(AmmError::Underflow)?;

        require!(denominator > 0, AmmError::DivisionByZero);

        let amount_in_no_fee: u64 = numerator.div_floor(&denominator) as u64;

        let fee_numerator_u128 = (amount_in_no_fee as u128)
            .checked_mul(3)
            .ok_or(AmmError::Overflow)?;
        let lp_fees: u64 = fee_numerator_u128.div_floor(&1000) as u64;
        
        let amount_in_final = (amount_in_no_fee as u128)
            .checked_add(lp_fees as u128)
            .ok_or(AmmError::Overflow)? as u64;

        require!(amount_in_final > 0 || (amount_in_final == 0 && amount_out == 0), AmmError::CalculationFailure);
        require!(amount_in_final <= max_in, AmmError::Slippage);

        transfer_tokens(
            &context.accounts.user_token_b,
            &mut context.accounts.token_vault_b,
            &amount_in_final,
            &context.accounts.token_b,
            &context.accounts.user,
            &context.accounts.token_program,
        )?;

        let token_a_key = context.accounts.token_a.key();
        let token_b_key = context.accounts.token_b.key();
        let bump_seed = [context.bumps.liquidity_pool];

        let signer_seeds: &[&[&[u8]]] = &[&[
            b"pool",
            token_a_key.as_ref(),
            token_b_key.as_ref(),
            &bump_seed,
        ]];

        let cpi_accounts_transfer_out = TransferChecked {
            from: context.accounts.token_vault_a.to_account_info(),
            mint: context.accounts.token_a.to_account_info(),
            to: context.accounts.user_token_a.to_account_info(),
            authority: context.accounts.liquidity_pool.to_account_info(),
        };
        let cpi_context_transfer_out = CpiContext::new_with_signer(
            context.accounts.token_program.to_account_info(),
            cpi_accounts_transfer_out,
            signer_seeds,
        );
        transfer_checked(cpi_context_transfer_out, amount_out, context.accounts.token_a.decimals)?
    }
    Ok(())
}
```

### Function signature

```rust
pub fn swap_exact_out(
    context: Context<SwapContext>, 
    amount_out: u64, 
    max_in: u64, 
    zero_for_one: bool
) -> Result<()> 
```

amount_out: the exact amount of token user wants to receive.

max_in: the maximum amount of input tokens user is willing to pay.

zero_for_one: direction of the trade:

true: swap token A → token B

false: swap token B → token A

This is a "swap exact out" model, where you specify the desired output and calculate the necessary input.

### General Flow

1. **Reload vault balances** to get the freshest reserves.

2. **Determine trade direction** using `zero_for_one`.

3. **Calculate input amount required** based on AMM formula:
   $$
   x=rA⋅yrB−yx = \frac{r_A \cdot y}{r_B - y}x=rB−yrA⋅y
   $$
   where:

   - xxx: tokens needed in
   - yyy: desired output (`amount_out`)
   - rAr_ArA, rBr_BrB: reserves of token A and B

4. **Apply 0.3% fee** (3 / 1000)

5. **Check slippage protection**: `amount_in <= max_in`

6. **Do the token transfer**:

   - Transfer `amount_in` from user to vault
   - Transfer `amount_out` from vault to user, using `transfer_checked` with program authority

### Mathematics and Fee Logic

- **Input required without fee**:

  

- **Apply 0.3% fee**:

  

This is equivalent to the Uniswap-style `x * y = k` formula, rearranged to solve for input amount.

### Key Validations

- Pool reserves must be > 0
- `amount_out` must be > 0
- `amount_out` must be less than the corresponding reserve
- Avoid division by zero and overflows
- Slippage protection via `max_in`
- Final amount in must be > 0

### CPI Transfers with Authority Seeds

When sending tokens out from the vault to the user, the program uses a **PDA signer** (derived from the pool address):

```rust
signer_seeds: &[&[&[u8]]] = &[&[
    b"pool",
    token_a_key.as_ref(),
    token_b_key.as_ref(),
    &bump_seed,
]];
```

This is used to authorize the `transfer_checked` CPI call, ensuring the program has permission to move funds from the vault.

###  What This Function Does Not Do

- It doesn't update internal AMM state like fees collected or any event emission (may be done elsewhere).
- It assumes `context` has all necessary accounts validated elsewhere (likely via Anchor's `#[derive(Accounts)]`).
- There's no rounding protection (e.g., refund dust), but rounding is minimized using `div_floor`.

## Swap Exact In

```rust
pub fn swap_exact_in(context: Context<SwapContext>, amount_in: u64, min_out: u64, zero_for_one: bool) -> Result<()> {
    context.accounts.token_vault_a.reload()?;
    context.accounts.token_vault_b.reload()?;
    let reserve_a: u64 = context.accounts.token_vault_a.amount;
    let reserve_b: u64 = context.accounts.token_vault_b.amount;

    if reserve_a == 0 || reserve_b == 0 {
        return err!(AmmError::PoolIsEmpty);
    }
    if amount_in == 0 {
        return err!(AmmError::NoZeroAmount);
    }

    if zero_for_one {
        let numerator: u128 = (reserve_b as u128).checked_mul(amount_in as u128).ok_or(AmmError::Overflow)?;
        let denominator: u128 = (reserve_a as u128).checked_add(amount_in as u128).ok_or(AmmError::Overflow)?;
        if denominator == 0 {
            return err!(AmmError::DivisionByZero);
        }

        let mut amount_out: u64 = numerator.div_floor(&denominator) as u64;

        let lp_fees = (amount_out as u128 * 3).div_floor(&1000) as u64;

        amount_out = amount_out - lp_fees;

        if amount_out == 0 || amount_out < min_out {
            return err!(AmmError::Slippage);
        }

        transfer_tokens(
            &context.accounts.user_token_a,
            &mut context.accounts.token_vault_a,
            &amount_in,
            &context.accounts.token_a,
            &context.accounts.user,
            &context.accounts.token_program,
        )?;

        let token_a_key = context.accounts.token_a.key();
        let token_b_key = context.accounts.token_b.key();
        let bump_seed = [context.bumps.liquidity_pool];

        let signer_seeds: &[&[&[u8]]] = &[&[
            b"pool",
            token_a_key.as_ref(),
            token_b_key.as_ref(),
            &bump_seed,
        ]];

        let cpi_accounts_transfer_out = TransferChecked {
            from: context.accounts.token_vault_b.to_account_info(),
            mint: context.accounts.token_b.to_account_info(),
            to: context.accounts.user_token_b.to_account_info(),
            authority: context.accounts.liquidity_pool.to_account_info(),
        };
        let cpi_context_transfer_out = CpiContext::new_with_signer(
            context.accounts.token_program.to_account_info(),
            cpi_accounts_transfer_out,
            signer_seeds,
        );
        transfer_checked(cpi_context_transfer_out, amount_out, context.accounts.token_b.decimals)?
    } else {
        let numerator: u128 = (reserve_a as u128).checked_mul(amount_in as u128).ok_or(AmmError::Overflow)?;
        let denominator: u128 = (reserve_b as u128).checked_add(amount_in as u128).ok_or(AmmError::Overflow)?;
        if denominator == 0 {
            return err!(AmmError::DivisionByZero);
        }
        let mut amount_out: u64 = numerator.div_floor(&denominator) as u64;

        let lp_fees = (amount_out as u128 * 3).div_floor(&1000) as u64;

        amount_out = amount_out - lp_fees;

        if amount_out == 0 || amount_out < min_out {
            return err!(AmmError::Slippage);
        }

        transfer_tokens(
            &context.accounts.user_token_b,
            &mut context.accounts.token_vault_b,
            &amount_in,
            &context.accounts.token_b,
            &context.accounts.user,
            &context.accounts.token_program,
        )?;

        let token_a_key = context.accounts.token_a.key();
        let token_b_key = context.accounts.token_b.key();
        let bump_seed = [context.bumps.liquidity_pool];

        let signer_seeds: &[&[&[u8]]] = &[&[
            b"pool",
            token_a_key.as_ref(),
            token_b_key.as_ref(),
            &bump_seed,
        ]];

        let cpi_accounts_transfer_out = TransferChecked {
            from: context.accounts.token_vault_a.to_account_info(),
            mint: context.accounts.token_a.to_account_info(),
            to: context.accounts.user_token_a.to_account_info(),
            authority: context.accounts.liquidity_pool.to_account_info(),
        };
        let cpi_context_transfer_out = CpiContext::new_with_signer(
            context.accounts.token_program.to_account_info(),
            cpi_accounts_transfer_out,
            signer_seeds,
        );
        transfer_checked(cpi_context_transfer_out, amount_out, context.accounts.token_a.decimals)?
    }

    Ok(())
}
```

## Function Overview: `swap_exact_in`

```
rustCopyEditpub fn swap_exact_in(
    context: Context<SwapContext>, 
    amount_in: u64, 
    min_out: u64, 
    zero_for_one: bool
) -> Result<()>
```

This function performs a **swap with a fixed input amount** (`amount_in`) and calculates the **output amount** a user receives, ensuring it's not less than `min_out` (slippage protection). This follows the **"exact in"** model used in automated market makers (AMMs).

------

### AMM Logic: Constant Product

This implementation also uses a **Uniswap v2-style constant product** invariant:

x⋅y=kx \cdot y = kx⋅y=k

Where:

- `x`, `y` are the reserves of token A and B
- The swap shifts the reserves such that the product remains constant

------

### Trade Direction via `zero_for_one`

- `true`: swap **Token A → Token B**
- `false`: swap **Token B → Token A**

------

## 🔍 **Step-by-Step Analysis**

### 1. **Sanity Checks**

```
if reserve_a == 0 || reserve_b == 0 {
    return err!(AmmError::PoolIsEmpty);
}
if amount_in == 0 {
    return err!(AmmError::NoZeroAmount);
}
```

- Prevents division-by-zero and meaningless swaps

------

###  2. **Swap Logic (A → B or B → A)**

#### If `zero_for_one` is `true`:

```rust
numerator = reserve_b * amount_in;
let denominator = reserve_a + amount_in;
let amount_out = numerator / denominator;
```

- Formula:

  amount_out=⌊reserveout⋅amountinreservein+amountin⌋amount\_out = \left\lfloor \frac{reserve_{out} \cdot amount_{in}}{reserve_{in} + amount_{in}} \right\rflooramount_out=⌊reservein+amountinreserveout⋅amountin⌋

- Then subtracts 0.3% **fee**:

  lp_fees=⌊amount_out⋅31000⌋lp\_fees = \left\lfloor amount\_out \cdot \frac{3}{1000} \right\rfloorlp_fees=⌊amount_out⋅10003⌋

  amount_out−=lp_feesamount\_out -= lp\_feesamount_out−=lp_fees

- Requires `amount_out ≥ min_out` (slippage protection)

- Transfers:

  - `amount_in` from **user to vault A**
  - `amount_out` from **vault B to user**

------

#### If `zero_for_one` is `false`:

Same process, but swaps **Token B → Token A** with corresponding vaults and reserves swapped.

------

### 🔐 3. **Token Transfers**

Transfers are split into two parts:

- **User → Pool**:
   Using `transfer_tokens` to move `amount_in` from user to the appropriate vault
- **Pool → User**:
   Using `transfer_checked` with a **PDA authority (`liquidity_pool`)** and `signer_seeds` derived from:

```
rustCopyEditsigner_seeds: &[&[&[u8]]] = &[&[
    b"pool",
    token_a_key.as_ref(),
    token_b_key.as_ref(),
    &bump_seed,
]];
```

This ensures the program signs on behalf of the pool account securely.

### Protections and Edge Cases

- ✅ Overflow protection (`checked_mul`, `checked_add`)
- ✅ Division-by-zero checks
- ✅ LP fee logic: always subtracts from output
- ✅ Slippage enforced before any token is moved
- ✅ Uses correct signer seeds for secure program authority
- ✅ Reloads accounts to avoid stale reserve values

------

## Important Differences From `swap_exact_out`

| Feature              | `swap_exact_in`                        | `swap_exact_out`                    |
| -------------------- | -------------------------------------- | ----------------------------------- |
| User specifies       | `amount_in` (input)                    | `amount_out` (output)               |
| User constraint      | `min_out` (minimum acceptable)         | `max_in` (maximum acceptable)       |
| Output is calculated | From input amount, fees are subtracted | Input is calculated, fees are added |
| Slippage protection  | `amount_out >= min_out`                | `amount_in <= max_in`               |
| Fee deduction        | After calculating `amount_out`         | Before finalizing `amount_in`       |