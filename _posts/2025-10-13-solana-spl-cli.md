---
layout: post
title: Solana SPL token - Command
date:   2025-10-13
lang: en
locale: en-GB
categories: blockchain solana
tags: solana spl-token token-2022 token
description: Solana CLI and the spl-token tool allows to create tokens, configure authorities, manage accounts, and use advanced extensions introduced with Token-2022.
image:
isMath: 
---

The Solana blockchain supports the **SPL Token standard**, which defines how fungible and non-fungible tokens are created, transferred, and managed on the network. 

- For developers and issuers, the **command-line interface (CLI)** provides a direct way to interact with the token program. 
- Using the Solana CLI and the `spl-token` tool, it is possible to create tokens, configure authorities, manage accounts, and use advanced extensions introduced with **Token-2022**.

You can find more details and steps in my article: [Introduction to Solana and the spl-token command line](https://rya-sge.github.io/access-denied/2022/08/06/solana-spl-token/) as well as more details about Solana here [Solana Core Concept](https://rya-sge.github.io/access-denied/2024/09/19/solana-core-concept/)

This article contains the list of available command with the Solana CLI.

[TOC]



## Solana concept - Reminder

- Tokens on Soana are digital assets that represent ownership over diverse categories of assets.
- Tokens on Solana are referred to as SPL ([Solana Program Library](https://github.com/solana-program)) Tokens.

### Type of account

- [Token Programs](https://solana.com/docs/tokens#token-program) contain all instruction logic for interacting with tokens on the network (both fungible and non-fungible).
- A [Mint Account](https://solana.com/docs/tokens#mint-account) represents a specific token and stores global metadata about the token such as the total supply and mint authority (address authorized to create new units of a token).
- A [Token Account](https://solana.com/docs/tokens#token-account) tracks individual ownership of tokens for a specific mint account for a specific owner.
- An [Associated Token Account](https://solana.com/docs/tokens#associated-token-account) is a Token Account created with an address derived from the owner and mint account addresses.

#### Mint account

Tokens on Solana are uniquely identified by the address of a [Mint Account](https://github.com/solana-program/token/blob/6d18ff73b1dd30703a30b1ca941cb0f1d18c2b2a/program/src/state.rs#L16-L30) owned by the Token Program. This account acts as a global counter for a specific token and stores data such as:

- **Supply**: Total supply of the token
- **Decimals**: Decimal precision of the token
- **Mint authority**: The account authorized to create new units of the token, increasing the supply
- **Freeze authority**: The account authorized to freeze tokens in a Token Account, preventing them from being transferred or burned

```rust
pub struct Mint {
    /// Optional authority used to mint new tokens. The mint authority may only
    /// be provided during mint creation. If no mint authority is present
    /// then the mint has a fixed supply and no further tokens may be
    /// minted.
    pub mint_authority: COption<Pubkey>,
    /// Total supply of tokens.
    pub supply: u64,
    /// Number of base 10 digits to the right of the decimal place.
    pub decimals: u8,
    /// Is `true` if this structure has been initialized
    pub is_initialized: bool,
    /// Optional authority to freeze token accounts.
    pub freeze_authority: COption<Pubkey>,
}
```



#### Token account

The Token Program creates [Token Accounts](https://github.com/solana-program/token/blob/6d18ff73b1dd30703a30b1ca941cb0f1d18c2b2a/program/src/state.rs#L87-L108) to track individual ownership of each token unit. A Token Account stores data such as:

- **Mint**: The token the Token Account holds units of
- **Owner**: The account authorized to transfer tokens from the Token Account
- **Amount**: Number of the tokens the Token Account currently holds

```rust
pub struct Account {
    /// The mint associated with this account
    pub mint: Pubkey,
    /// The owner of this account.
    pub owner: Pubkey,
    /// The amount of tokens this account holds.
    pub amount: u64,
    /// If `delegate` is `Some` then `delegated_amount` represents
    /// the amount authorized by the delegate
    pub delegate: COption<Pubkey>,
    /// The account's state
    pub state: AccountState,
    /// If is_native.is_some, this is a native token, and the value logs the
    /// rent-exempt reserve. An Account is required to be rent-exempt, so
    /// the value is used by the Processor to ensure that wrapped SOL
    /// accounts do not drop below this threshold.
    pub is_native: COption<u64>,
    /// The amount delegated
    pub delegated_amount: u64,
    /// Optional authority to close the account.
    pub close_authority: COption<Pubkey>,
}
```



## Global command

| Command                                   | Target<br />[Token Account, Token Mint, -] | Description                                                  |
| ----------------------------------------- | ------------------------------------------ | ------------------------------------------------------------ |
| `accounts`                                |                                            | List all token accounts by owner                             |
| `address`                                 |                                            | Get wallet address                                           |
| `apply-pending-balance`                   |                                            | Collect confidential tokens from pending to available balance |
| `approve`                                 | Token account                              | Approve a delegate for a token account                       |
| `authorize`                               | Token mint or  token account               | Authorize a new signing keypair to a token or token account  |
| `balance`                                 | Token account                              | Get token account balance                                    |
| `bench`                                   | -                                          | Token benchmarking facilities                                |
| `burn`                                    | Token account                              | Burn tokens from an account                                  |
| `close`                                   | Token account                              | Close a token account                                        |
| `close-mint`                              | Token mint                                 | Close a token mint                                           |
| `configure-confidential-transfer-account` |                                            | Configure confidential transfers for token account           |
| `create-account`                          | Token mint                                 | Create a new token account                                   |
| `create-multisig`                         | -                                          | Create a new account describing an M:N multisignature        |
| `create-token`                            | -                                          | Create a new token                                           |
| `deposit-confidential-tokens`             |                                            | Deposit amounts for confidential transfers                   |
| `disable-confidential-credits`            |                                            | Disable confidential transfers for token account             |
| `disable-cpi-guard`                       |                                            | Disable CPI Guard for token account                          |
| `disable-non-confidential-credits`        |                                            | Disable non-confidential transfers for token account         |
| `disable-required-transfer-memos`         |                                            | Disable required transfer memos for token account            |
| `display`                                 | Token mint                                 | Query details of an SPL Token mint, account, or multisig by address |
| `enable-confidential-credits`             |                                            | Enable confidential transfers for token account (use `configure...` first) |
| `enable-cpi-guard`                        |                                            | Enable CPI Guard for token account                           |
| `enable-non-confidential-credits`         |                                            | Enable non-confidential transfers for token account          |
| `enable-required-transfer-memos`          |                                            | Enable required transfer memos for token account             |
| `freeze`                                  | Token account                              | Freeze a token account                                       |
| `gc`                                      |                                            | Cleanup unnecessary token accounts                           |
| `help`                                    |                                            | Prints help message for commands                             |
| `initialize-group`                        | Token mint                                 | Initialize group extension on a token mint                   |
| `initialize-member`                       | Token mint                                 | Initialize group member extension on a token mint            |
| `initialize-metadata`                     | Token mint                                 | Initialize metadata extension on a token mint                |
| `mint`                                    | Token mint                                 | Mint new tokens                                              |
| `pause`                                   | Token mint                                 | Pause mint, burn, and transfer                               |
| `resume`                                  | Token mint                                 | Resume mint, burn, and transfer                              |
| `revoke`                                  | Token account                              | Revoke a delegate's authority                                |
| `set-interest-rate`                       | Token mint                                 | Set the interest rate for an interest-bearing token          |
| `set-transfer-fee`                        | Token mint                                 | Set the transfer fee for a token with a configured transfer fee |
| `set-transfer-hook`                       | Token mint                                 | Set the transfer hook program id for a token                 |
| `supply`                                  | Token mint                                 | Get token supply                                             |
| `sync-native`                             |                                            | Sync a native SOL token account to its underlying lamports   |
| `thaw`                                    | Token account                              | Thaw a token account                                         |
| `transfer`                                | Token mint                                 | Transfer tokens between accounts                             |
| `unwrap`                                  |                                            | Unwrap a SOL token account                                   |
| `update-confidential-transfer-settings`   |                                            | Update confidential transfer configuration for a token       |
| `update-default-account-state`            |                                            | Update default account state for the mint (requires extension) |
| `update-group-address`                    | Token mint                                 | Update group pointer address for the mint (requires extension) |
| `update-group-max-size`                   |                                            | Update the maximum number of members for a group             |
| `update-member-address`                   | Token mint                                 | Update group member pointer address for the mint (requires extension) |
| `update-metadata`                         | Token mint                                 | Update metadata on a token mint (with extension)             |
| `update-metadata-address`                 | Token mint                                 | Update metadata pointer address for the mint (requires extension) |
| `withdraw-confidential-tokens`            |                                            | Withdraw amounts for confidential transfers                  |
| `withdraw-excess-lamports`                |                                            | Withdraw lamports from a Token Program owned account         |
| `withdraw-withheld-tokens`                | Token account                              | Withdraw withheld transfer fee tokens from mint and/or accounts |
| `wrap`                                    | -                                          | Wrap native SOL in a SOL token account                       |



### Details

- `authorize`

Authorize a new signing keypair to a token or token account

```
spl-token authorize [OPTIONS] <TOKEN_ADDRESS> <AUTHORITY_TYPE> [--] [AUTHORITY_ADDRESS]
```

- `burn`

Burn tokens from an account

```bash
spl-token burn [OPTIONS] <TOKEN_ACCOUNT_ADDRESS> <TOKEN_AMOUNT>
```

- `close`

Close a token account

```bash
spl-token close [OPTIONS] [--] [TOKEN_MINT_ADDRESS]
```

- `create-account`

Create a new token account

```bash
spl-token create-account [OPTIONS] <TOKEN_MINT_ADDRESS> [ACCOUNT_KEYPAIR]
```

- `create-multisig`

```
spl-token create-multisig [OPTIONS] <MINIMUM_SIGNERS> <MULTISIG_MEMBER_PUBKEY>
```

- `create-token`

```
spl-token create-token [OPTIONS] [--] [TOKEN_KEYPAIR]
```

- `display`

Query details of an SPL Token mint, account, or multisig by address

```
spl-token display [OPTIONS] <TOKEN_ADDRESS>
```

- `enable-cpi-guard`
- `enable-required-transfer-memos`
- `freeze`

Freeze a token account

```
spl-token freeze [OPTIONS] <TOKEN_ACCOUNT_ADDRESS>
```

- `initialize-metadata`

```bash
spl-token initialize-metadata [OPTIONS] <TOKEN_MINT_ADDRESS> <TOKEN_NAME> <TOKEN_SYMBOL> <TOKEN_URI>
```

- `mint`

Mint new tokens

```bash
spl-token mint [OPTIONS] <TOKEN_MINT_ADDRESS> <TOKEN_AMOUNT> [--] [RECIPIENT_TOKEN_ACCOUNT_ADDRESS]
```

- `pause`

Pause mint, burn, and transfer

```
 spl-token pause [OPTIONS] <TOKEN_MINT_ADDRESS>
```

- `resume`

Resume mint, burn, and transfer

```
spl-token resume [OPTIONS] <TOKEN_MINT_ADDRESS>
```

- `revoke`

Revoke a delegate's authority

```
spl-token revoke [OPTIONS] <TOKEN_ACCOUNT_ADDRESS>
```

- `set-interest-rate`

Set the interest rate for an interest-bearing token

```
 spl-token set-interest-rate [OPTIONS] <TOKEN_MINT_ADDRESS> <RATE>
```

- `set-transfer-fee`

Set the transfer fee for a token with a configured transfer fee

```
spl-token set-transfer-fee [OPTIONS] <TOKEN_MINT_ADDRESS> <FEE_IN_BASIS_POINTS> <MAXIMUM_FEE>
```

- `set-transfer-hook`

```
spl-token set-transfer-hook [OPTIONS] <TOKEN_MINT_ADDRESS> [NEW_PROGRAM_ID]
```

- `supply`

Get token supply

```
spl-token supply [OPTIONS] <TOKEN_MINT_ADDRESS>
```

- `thaw`

Thaw a token account

```
spl-token thaw [OPTIONS] <TOKEN_ACCOUNT_ADDRESS>
```

- `transfer`

  Transfer tokens between accounts

```rust
spl-token transfer [OPTIONS] <TOKEN_MINT_ADDRESS> <TOKEN_AMOUNT> <RECIPIENT_WALLET_ADDRESS or RECIPIENT_TOKEN_ACCOUNT_ADDRESS>
```

- `update-default-account-state`

Updates default account state for the mint. Requires the default account state extension.

```
 spl-token update-default-account-state [OPTIONS] <TOKEN_MINT_ADDRESS> <STATE>
```

- `update-group-address`

Updates group pointer address for the mint. Requires the group pointer extension

```bash
spl-token update-group-address [OPTIONS] <TOKEN_MINT_ADDRESS> [--] [GROUP_ADDRESS]
```

- `update-member-address`

Updates group member pointer address for the mint. Requires the group member pointer extension.

```
 spl-token update-member-address [OPTIONS] <TOKEN_MINT_ADDRESS> [--] [MEMBER_ADDRESS]
```

- `update-metadata`

Update metadata on a token mint that has the extension

```
spl-token update-metadata [OPTIONS] <TOKEN_MINT_ADDRESS> <FIELD_NAME> [VALUE_STRING]
```

- `update-metadata-address`

```
spl-token update-metadata-address [OPTIONS] <TOKEN_MINT_ADDRESS> [--] [METADATA_ADDRESS]
```

- `withdraw-withheld-tokens`

```bash
spl-token withdraw-withheld-tokens [OPTIONS] <FEE_RECIPIENT_ADDRESS> <SOURCE_ADDRESS|--include-mint> [--]
```

- `wrap`

Wrap native SOL in a SOL token account

```
spl-token wrap [OPTIONS] <AMOUNT> [KEYPAIR]
```



## Create token

### `spl-token create-token` 

Command Reference

| Section     | Option / Flag                              | Description                                                  |
| ----------- | ------------------------------------------ | ------------------------------------------------------------ |
| **General** | `spl-token create-token`                   | Create a new token                                           |
| **FLAGS**   | `--enable-close`                           | Enable the mint authority to close this mint                 |
|             | `--enable-freeze`                          | Enable the mint authority to freeze token accounts for this mint |
|             | `--enable-group`                           | Enable group configurations in the mint (requires initialization) |
|             | `--enable-member`                          | Enable group member configurations in the mint (requires initialization) |
|             | `--enable-metadata`                        | Enable metadata in the mint (requires initialization)        |
|             | `--enable-non-transferable`                | Permanently force tokens to be non-transferable (they may still be burned) |
|             | `--enable-permanent-delegate`              | Enable the mint authority to act as a permanent delegate     |
|             | `-h, --help`                               | Prints help information                                      |
|             | `-V, --version`                            | Prints version information                                   |
|             | `-v, --verbose`                            | Show additional information                                  |
| **OPTIONS** | `-C, --config <PATH>`                      | Configuration file to use                                    |
|             | `--decimals <DECIMALS>`                    | Number of base 10 digits to the right of the decimal (default: 9) |
|             | `--default-account-state <STATE>`          | Set default account state (`initialized` or `frozen`)        |
|             | `--enable-confidential-transfers <POLICY>` | Enable confidential transfers (`auto` or `manual`)           |
|             | `--fee-payer <KEYPAIR>`                    | Specify fee-payer account (file, ASK keyword, or pubkey + signer) |
|             | `--group-address <ADDRESS>`                | Address for token group configurations                       |
|             | `--interest-rate <RATE_BPS>`               | Set interest rate in basis points (defaults to mint authority) |
|             | `-u, --url <URL_OR_MONIKER>`               | RPC URL or cluster moniker (`mainnet-beta`, `testnet`, `devnet`, `localhost`) |
|             | `--member-address <ADDRESS>`               | Address for token member configurations                      |
|             | `--with-memo <MEMO>`                       | Attach a memo string to the transaction                      |
|             | `--metadata-address <ADDRESS>`             | Address for token metadata                                   |
|             | `--mint-authority <ADDRESS>`               | Mint authority address (defaults to client keypair)          |
|             | `--nonce <PUBKEY>`                         | Nonce account for nonced transaction (for long signing processes) |
|             | `--nonce-authority <KEYPAIR>`              | Keypair for signing a nonced transaction                     |
|             | `--output <FORMAT>`                        | Output format (`json`, `json-compact`)                       |
|             | `-p, --program-id <ADDRESS>`               | SPL Token program id                                         |
|             | `--transfer-fee <FEE_BPS> <MAX_FEE>`       | Add a transfer fee; mint authority can set/withdraw fees     |
|             | `--transfer-hook <PROGRAM_ID>`             | Enable mint authority to set transfer hook program           |
| **ARGS**    | `<TOKEN_KEYPAIR>`                          | Token keypair (file or ASK keyword, defaults to randomly generated) |





## References

- SPL command line - help section