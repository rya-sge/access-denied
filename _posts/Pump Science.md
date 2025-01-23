# Pump Science

This article presents the liquidation function from the `Dyad Stablecoin`.

This analyse has been done for the [Code4Arena](https://github.com/code-423n4/2025-01-pump-science/) contest..

Since I have a limited time, I found that it could be interesting to focus only in one function in the `VaultManagerV2`, [liquidate](https://github.com/code-423n4/2024-04-dyad/blob/main/src/core/VaultManagerV2.sol#L205) instead of the whole code.

Prior to the contest, the code has also been audited by [Pashow Audit Group](https://github.com/code-423n4/2025-01-pump-science/blob/main/audits/PumpScience%20-%20Pashov%20audit.pdf)

Pump Science Bonding Curve Protocol is a Solana protocol implementing an advanced bonding curve mechanism for fundraising and sustainable project funding. This protocol enables compound submitters to launch their own token ($DRUG) with dynamic fee structures and automated liquidity management.

[TOC]



## Administrative Roles

### Curve Creator

- Can initialize new bonding curves
- Sets initial parameters and optional whitelist
- Configures launch timing and initial purchases

### Admin

- Can modify protocol parameters
- Manages fee settings
- Controls whitelist status

### Fee Recipients

- Protocol Multisig (`3bM4hewuZFZgNXvLWwaktXMa8YHgxsnnhaRfzxJV944P`)
  - Receives trading fees
  - Has authority over locked LP tokens
  - Receives swapped USDC from liquidity migrations

## Create a Bonding Curve

To create a new bonding curve:

1. Initialize curve parameters
2. Optional: Enable whitelist
3. Set launch timing
4. Configure initial purchases

Trading is enabled along the bonding curve until 85 SOL are raised and all 793,100,000 tokens are sold.

### Functions

#### Validate

##### **Function Overview**

The `validate` function is a precondition check for creating a bonding curve. It ensures that input parameters and relevant accounts meet specific criteria before proceeding with the operation.

The key validations performed are:

1. **Start Time Validation**:
   - Ensures the `params.start_slot` is not in the past and is within a defined delay range (`MAX_START_SLOT_DELAY`).
2. **Whitelist Validation**:
   - If whitelisting is enabled (`global.whitelist_enabled`)
     - Ensures a whitelist exists (`self.whitelist.is_some()`).
     - Ensures the `creator` account matches the whitelist's `creator` field.
3. **Global Configuration Validation**:
   - Verifies that the global configuration is not outdated by calling `self.global.is_config_outdated()`.

If all validations pass, the function returns `Ok(())`. Otherwise, it returns an error.

```rust
    pub fn validate(&self, params: &CreateBondingCurveParams) -> Result<()> {
        let clock = Clock::get()?;
        // validate start time
        if let Some(start_slot) = params.start_slot {
            require!(
                start_slot >= clock.slot && start_slot <= clock.slot + MAX_START_SLOT_DELAY,
                ContractError::InvalidStartTime
            )
        }

        // validate whitelist
        if self.global.whitelist_enabled {
            let whitelist = self.whitelist.as_ref();
            require!(whitelist.is_some(), ContractError::NotWhiteList);
            require!(
                whitelist.unwrap().creator == self.creator.key(),
                ContractError::NotWhiteList
            );
        }

        require!(
            !self.global.is_config_outdated()?,
            ContractError::ConfigOutdated
        );

        Ok(())
    }
```

#### Handler

##### **Function Overview**

The `handler` function is responsible for creating and initializing a bonding curve, including minting tokens, setting up metadata, and performing related operations.

------

###### **Main Steps**

1. **Update Bonding Curve from Parameters**:
   - Updates the bonding curve account using the provided parameters, linking the mint, creator, and global accounts.
   - Uses the current Solana clock for time-dependent values and the bump seed for PDA initialization.
2. **Create Token Metadata**:
   - Calls `intialize_meta` to create token metadata on the associated token account using the provided parameters (`name`, `symbol`, `uri`).
3. **Mint Tokens**:
   - Mints the bonding curve's total supply of tokens to its token account using the bonding curve PDA as the mint authority.
4. **Revoke Mint Authority and Lock ATA**:
   - Revokes the mint authority from the bonding curve account to prevent further token minting.
   - Locks the bonding curve token account to ensure secure state management.
5. **Invariant Validation**:
   - Ensures the bonding curve satisfies protocol-specific invariants to maintain correctness and consistency.
6. **Emit Create Event**:
   - Emits an event (`CreateEvent`) with bonding curve details for external tracking and logging.
7. **Log Success**:
   - Logs a success message and returns `Ok(())`.

```rust
 pub fn handler(
        ctx: Context<CreateBondingCurve>,
        params: CreateBondingCurveParams,
    ) -> Result<()> {
        let clock = Clock::get()?;
        ctx.accounts.bonding_curve.update_from_params(
            ctx.accounts.mint.key(),
            ctx.accounts.creator.key(),
            &ctx.accounts.global,
            &params,
            &clock,
            ctx.bumps.bonding_curve,
        );
        msg!("CreateBondingCurve::update_from_params: created bonding_curve");

        let mint_k = ctx.accounts.mint.key();
        let mint_authority_signer = BondingCurve::get_signer(&ctx.bumps.bonding_curve, &mint_k);
        let mint_auth_signer_seeds = &[&mint_authority_signer[..]];
        let mint_authority_info = ctx.accounts.bonding_curve.to_account_info();
        let mint_info = ctx.accounts.mint.to_account_info();

        // Create Token Metadata
        ctx.accounts
            .intialize_meta(mint_auth_signer_seeds, &params)?;

        // Mint Tokens
        mint_to(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                MintTo {
                    authority: mint_authority_info.clone(),
                    to: ctx.accounts.bonding_curve_token_account.to_account_info(),
                    mint: mint_info.clone(),
                },
                mint_auth_signer_seeds,
            ),
            ctx.accounts.bonding_curve.token_total_supply,
        )?;

        let locker = &mut ctx
            .accounts
            .into_bonding_curve_locker_ctx(ctx.bumps.bonding_curve);
        
        // Revoke mint authority
        locker.revoke_mint_authority()?;
        locker.lock_ata()?;

        BondingCurve::invariant(locker)?;
        let bonding_curve = ctx.accounts.bonding_curve.as_mut();
        emit_cpi!(CreateEvent {
            name: params.name,
            symbol: params.symbol,
            uri: params.uri,
            mint: *ctx.accounts.mint.to_account_info().key,
            creator: *ctx.accounts.creator.to_account_info().key,
            virtual_sol_reserves: bonding_curve.virtual_sol_reserves,
            virtual_token_reserves: bonding_curve.virtual_token_reserves,
            token_total_supply: bonding_curve.token_total_supply,
            real_sol_reserves: bonding_curve.real_sol_reserves,
            real_token_reserves: bonding_curve.real_token_reserves,
            start_slot: bonding_curve.start_slot,
        });
        msg!("CreateBondingCurve::handler: success");
        Ok(())
    }
```

#### Initialize meta

##### **Function Overview**

The `initialize_meta` function creates the metadata account for a bonding curve token using the `CreateMetadataAccountsV3` instruction. It integrates metadata details like the token's name, symbol, and URI into the Solana Token Metadata Program.

------

##### **Main Steps**

1. **Prepare Metadata Information**:

   - Constructs a `DataV2`

      object containing the token's metadata:

     - **Name, Symbol, URI**: Defined in `params`.
     - **Seller Fee**: Set to `0`.
     - **Optional Fields**: (`creators`, `collection`, `uses`) are set to `None`.

2. **Create Metadata Context**:

   - Creates a `CpiContext`object to invoke the Token Metadata Program's `CreateMetadataAccountsV3`

      instruction. This includes:

     - Accounts:
       - `payer`: The account paying for the metadata account creation (usually the creator).
       - `mint`: The associated mint account.
       - `metadata`: The metadata account being created.
       - `update_authority` and `mint_authority`: Both set to the bonding curve account.
       - `system_program` and `rent`: Required Solana program accounts for account creation and rent exemption.
     - **Signers**: Uses `mint_auth_signer_seeds` for PDAs.

3. **Invoke Metadata Creation**:

   - Calls `create_metadata_accounts_v3` with the prepared context and metadata.

4. **Log Completion**:

   - Logs a message confirming successful metadata initialization.

### Accounts

```rust
pub struct CreateBondingCurve<'info> {
    #[account(
        init,
        payer = creator,
        mint::decimals = global.mint_decimals,
        mint::authority = bonding_curve,
        mint::freeze_authority = bonding_curve,
    )]
    mint: Box<Account<'info, Mint>>,

    #[account(mut)]
    creator: Signer<'info>,

    #[account(
        init,
        payer = creator,
        seeds = [BondingCurve::SEED_PREFIX.as_bytes(), mint.key().as_ref()],
        bump,
        space = 8 + BondingCurve::INIT_SPACE,
    )]
    bonding_curve: Box<Account<'info, BondingCurve>>,

    #[account(
        init_if_needed,
        payer = creator,
        associated_token::mint = mint,
        associated_token::authority = bonding_curve,
    )]
    bonding_curve_token_account: Box<Account<'info, TokenAccount>>,
    #[account(
        seeds = [BondingCurve::SOL_ESCROW_SEED_PREFIX.as_bytes(), mint.key().as_ref()],
        bump,
    )]
    /// CHECK: PDA to hold SOL for bonding curve
    pub bonding_curve_sol_escrow: AccountInfo<'info>,

    #[account(
        seeds = [Global::SEED_PREFIX.as_bytes()],
        constraint = global.initialized == true @ ContractError::NotInitialized,
        bump,
    )]
    global: Box<Account<'info, Global>>,

    #[account(
        seeds = [Whitelist::SEED_PREFIX.as_bytes(), creator.key().as_ref()],
        bump,
    )]
    whitelist: Option<Account<'info, Whitelist>>,

    #[account(mut)]
    ///CHECK: Using seed to validate metadata account
    metadata: UncheckedAccount<'info>,

    /// CHECK: system program account
    pub system_program: UncheckedAccount<'info>,
    /// CHECK: token program account
    pub token_program: Program<'info, Token>,
    /// CHECK: associated token program account
    pub associated_token_program: UncheckedAccount<'info>,
    /// CHECK: token metadata program account
    pub token_metadata_program: UncheckedAccount<'info>,
    /// CHECK: rent account
    pub rent: UncheckedAccount<'info>,
}

```



Open question: why 8 for the constant seed

### Details

This Solana program struct, `CreateBondingCurve`, defines the accounts and constraints necessary for initializing a bonding curve in a decentralized application. 

Here's a step-by-step explanation of the code's functionality and a review of potential vulnerabilities:

------

### **Main Steps:**

1. **Mint Initialization**:

   - The `mint` account is initialized with specified parameters:
     - **Payer**: The `creator` account funds the initialization.
     - **Authority**: The `bonding_curve` account becomes the authority for minting and freezing tokens.
     - **Decimals**: Defined by `global.mint_decimals`.

2. **Creator as a Signer**:

   - The `creator` account is marked as mutable (`mut`) and must sign the transaction. This ensures that the transaction is authorized by the creator.

3. **Bonding Curve Account Initialization**:

   - The `bonding_curve`

      account is initialized with:

     - **Seeds**: Deterministic account derivation using a seed prefix and the mint's public key.
     - **Space**: Allocates enough space for storing bonding curve data.
     - **Bump**: A bump seed for creating a Program Derived Address (PDA).

4. **Bonding Curve Token Account**:

   - An associated token account for the bonding curve is created if it does not already exist.
   - This account holds tokens associated with the bonding curve.

5. **SOL Escrow PDA**:

   - A PDA (`bonding_curve_sol_escrow`) is derived to hold SOL associated with the bonding curve.
   - The `CHECK` attribute indicates that this account is not validated programmatically but through its seeds.
   - **Global Account**:
     - The `global` account is used to verify the program's global configuration.
     - A constraint ensures it is initialized before proceeding, or an error (`NotInitialized`) is raised.
   - **Optional Whitelist**:
     - The `whitelist` account is conditionally included to add an access control layer, allowing only certain users to interact with the bonding curve.
   - **Unchecked Metadata Account**:
     - The `metadata` account is referenced for validation or additional information, but it is not verified.
   - **Program and System Accounts**:
     - System and token program accounts, including associated token and metadata programs, are passed in. These accounts facilitate interactions with Solana's ecosystem (e.g., creating accounts, minting tokens).

   ### 


## Migration

Code: https://github.com/code-423n4/2025-01-pump-science/tree/main/programs/pump-science/src/instructions/migration

Migration is a critical process that occurs once the bonding curve has completed and the tokens are empty. It involves:

1. Minting the remaining 206,900,000 tokens
2. Sending the experiment fee to the multisig wallet
3. A CPI (Cross-Program Invocation) call to create a Meteora Dynamic AMM (Automated Market Maker). It uses 206,900,000 matched with 85SOL - experiment fee
4. A separate instruction CPI call that locks the liquidity in the AMM and creates an escrow from which the multisig can claim trading fees.