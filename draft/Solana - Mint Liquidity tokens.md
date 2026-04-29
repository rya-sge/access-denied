# Solana - Mint Liquidity tokens



## Example 1 - First flight

Calculate and Mint Initial LP Tokens

### Prepare value

```rust

    // Call the calculation function (assuming it returns Result<u64>)
    let lp_amount_to_mint: u64 = liquidity_calculation(amount_token_a, amount_token_b)?;

    // Create the bump slice variable first
    let bump_seed = [context.bumps.liquidity_pool]; // Store the bump in a separate variable
    let token_a_key = context.accounts.token_mint_a.key();
    let token_b_key = context.accounts.token_mint_b.key();

    // Define PDA signer seeds using the variable
    let signer_seeds: &[&[&[u8]]] = &[&[
        b"pool",
        token_a_key.as_ref(),
        token_b_key.as_ref(),
        &bump_seed, // Use the reference to the variable
    ]];
```



### Mint tokens

```rust
    // CPI Context for minting LP tokens
    let cpi_accounts = MintTo {
        mint: context.accounts.lp_mint.to_account_info(),
        to: context.accounts.creator_lp_token_account.to_account_info(),
        authority: context.accounts.liquidity_pool.to_account_info(), // Pool PDA is mint authority
    };
    let cpi_context = CpiContext::new_with_signer(
        context.accounts.token_program.to_account_info(),
        cpi_accounts,
        signer_seeds, // Pass the signer seeds
    );

    // Execute the mint_to CPI
    mint_to(cpi_context, lp_amount_to_mint)?;
```

## Example 2 - token-swap

https://github.com/solana-developers/program-examples/blob/main/tokens/token-swap/anchor/programs/token-swap/src/instructions/deposit_liquidity.rs

Mint the liquidity to user

```rust
    let authority_bump = ctx.bumps.pool_authority;
    let authority_seeds = &[
        &ctx.accounts.pool.amm.to_bytes(),
        &ctx.accounts.mint_a.key().to_bytes(),
        &ctx.accounts.mint_b.key().to_bytes(),
        AUTHORITY_SEED,
        &[authority_bump],
    ];
    let signer_seeds = &[&authority_seeds[..]];
    token::mint_to(
        CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            MintTo {
                mint: ctx.accounts.mint_liquidity.to_account_info(),
                to: ctx.accounts.depositor_account_liquidity.to_account_info(),
                authority: ctx.accounts.pool_authority.to_account_info(),
            },
            signer_seeds,
        ),
        liquidity,
    )?;

    Ok(())
```

