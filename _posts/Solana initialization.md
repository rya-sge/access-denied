## Solana initialization

```ru
Do you think thse following check avoud to initialize twice a pool ?
pub fn initialize_pool(context: Context<InitializePool>, amount_token_a: u64, amount_token_b: u64) -> Result<()> {
    // Enforce canonical order of mints, to ensure every pair will get initialized only once, inspired by Uniswap
    require!(
        context.accounts.token_mint_a.key() != context.accounts.token_mint_b.key(),
        AmmError::IdenticalTokens 
    );
    require!(
        context.accounts.token_mint_a.key() < context.accounts.token_mint_b.key(),
        AmmError::InvalidTokenOrder 
    );
```

No, **these two checks alone do not fully prevent pool re-initialization**. Let’s break it down:

------

## ✅ What these checks do

### 1. `require!(token_mint_a != token_mint_b)`

- Ensures a pool is not initialized with the same token on both sides (e.g., SOL/SOL).
- ✅ Prevents invalid self-pairs.

### 2. `require!(token_mint_a < token_mint_b)`

- Enforces a **canonical ordering** (e.g., always initialize SOL/USDC as SOL first, USDC second).
- ✅ Ensures **only one ordering is valid**, preventing duplicate pools like USDC/SOL and SOL/USDC.

------

## ❌ What these checks do **not** do

They **do not check if a pool already exists** for the given `(token_a, token_b)` pair.

If your program allows calling `initialize_pool` repeatedly with the same token pair and the same mint addresses, **nothing in these two checks alone prevents it** unless:

- There's **an account constraint or uniqueness enforcement** elsewhere (like a PDA), AND
- The account creation is **fail-fast** (e.g., trying to `init` an account that already exists causes an error).

## Correct

> Description: Creates the account via a CPI to the system program and initializes it (sets its account discriminator).
>
> https://www.anchor-lang.com/docs/references/account-constraints





```rust
 #[account(
        init,
        payer = creator,
        space = ANCHOR_DISCRIMINATOR + LiquidityPool::INIT_SPACE,
        seeds = [b"pool", token_mint_a.key().as_ref(), token_mint_b.key().as_ref()],
        bump
    )]
    pub liquidity_pool: Account<'info, LiquidityPool>,
```

This ensures each unique `(token_mint_a, token_mint_b)` pair results in **exactly one PDA address**.

If someone tries to call `initialize_pool` again with the same two tokens, this PDA will already exist.

Because it's marked with `#[account(init)]`, **Anchor will throw an error if the account already exists**, preventing re-initialization.