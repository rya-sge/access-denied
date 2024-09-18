# Solana Core Concept

This article is an introduction to the core concept around Solana, notably:

- Solana Account Model
- Accounts and programs on Solana
- Transactions and Instructions
- Program Derived Address
- Cross Program Invocation

This is mainly based on video by Anchor Security

Build a strong understanding of the core concepts that make Solana different from other blockchains. Understanding the "Solana programming model" through these core concepts is very important to maximize your success as a Solana blockchain developer.

- [Solana programming model I](https://www.youtube.com/watch?v=Plp4y27LNWs)

[TOC]

## Solana Account Model [#](https://solana.com/docs/core#solana-account-model)

On Solana, all data is stored in what are referred to as "accounts”. The way data is organized on the Solana blockchain resembles a [key-value store](https://en.wikipedia.org/wiki/Key–value_database), where each entry in the database is called an "account". Learn more about [Accounts](https://solana.com/docs/core/accounts) here.

There are three main type of accounts in Solana

- Data Accounts: These are created by Programs and used for storing data.
- Program Accounts: These accounts store executable programs. This is the equivalent of smart contracts on Solana.
- Native Accounts: These refer to native programs on Solana, such as System, Stake, and Vote. They are built-in programs included with the Solana runtime.

### Account info

The data stored on every account on Solana has the following structure known as the [AccountInfo](https://github.com/solana-labs/solana/blob/27eff8408b7223bb3c4ab70523f8a8dca3ca6645/sdk/program/src/account_info.rs#L19).

![account](/home/ryan/Downloads/me/brouillon-article/blockchain/assets/article/blockchain/solana/account.png)

#### Structure

Here the full [structure](https://docs.rs/solana-program/latest/solana_program/account_info/struct.AccountInfo.html)

```rust
pub struct AccountInfo<'a> {
    pub key: &'a Pubkey,
    pub lamports: Rc<RefCell<&'a mut u64>>,
    pub data: Rc<RefCell<&'a mut [u8]>>,
    pub owner: &'a Pubkey,
    pub rent_epoch: Epoch,
    pub is_signer: bool,
    pub is_writable: bool,
    pub executable: bool,
}
```

#### Details

The `AccountInfo` for each account includes the following fields:

- `key`

  - Use to identify an account
  - 256-bit long
  - Usually a public key of `ed25519` keypair

- `data`: A byte array that stores the state of an account. If the account is a program (smart contract), this stores executable program code. This field is often referred to as the "account data".

- `executable`: A boolean flag that indicates if the account is a program.

- `lamports`: 

  - the number of lamports owned by this account, in the smallest unit of SOL (1 SOL = 1 billion lamports).  

  - Only the owner of an account may substract its lamport

  - Runtime assets

    ```bash
    total_lamports_before == total_lamports_after
    ```

- `is_signer`

  - Flag indicating if an account has signed a transaction
  - It is not actually stored in the account
  - It's just runtime metadata

- `data`

  - The raw data byte array stored by this account
  - Up to 10 MB of mutable storage
  - Can only be written by the **owner** account
  - Can not be resized (currently)

- `owner`: 

  - Specifies the public key (program ID) of the program that owns the account.Only the program designated as the owner of an account can
    -  modify the data stored on the account 
    -  deduct the lamport balance. 
  - Only the owner of an account 
    - may assign a new owner
    - write to the data
  - The owner can only be changed if the data is zero

- `executable`

  - Accounts are marked as executable during a successful progroam deployment process
  - Executable accounts are fully immutable once they are marked as final
  - Owned by the bpf loader program

- `rent_epoche`

  - Accounts are helds in validator memory and pay "rent" to stay there
  - Charged every epoch(~2 days) and are determined by account size
  - Accounts with sufficient balance to cover 2 years of rent are exempt from fees

  

Reference: [Solana - accounts](https://solana.com/docs/core/accounts)

### 7 commandments of Solana Accounts

- Each account has an unique address and an owner(some program)
- Owner has fully autonomy over the owned accounts
- Only a data account's owner can modify its data and debit lamports
- Program accounts don't store state
- Account must pay rent to stay alive, otherwise they will be deleted at the end of the transaction
- Anyone is allowed to credit lamports to a data account
- The owner of an account may assign a new owner if the account's data is zeroed out



## Programs on Solana

In the Solana ecosystem, "smart contracts" are called programs. Each [program](https://solana.com/docs/core/accounts#program-account) is an on-chain account that stores executable logic, organized into specific functions referred to as [instructions](https://solana.com/docs/core/transactions#instruction).

In summary: 

- Programs are piece of code that runs by Solana Blockchain
- Programs are stateless. Meaning you can't store any data in them
- Solana uses Accounts to store both program's code and "Data" - We can imagine them as files
- Program can be upgraded on-chain if the authorized authority has not bee revoked. 

See also [Solana Core programs](https://solana.com/docs/core/programs)

### Solana Program Library

The Solana Program Library (SPL) is a collection of on-chain programs targeting the [Sealevel parallel runtime](https://medium.com/solana-labs/sealevel-parallel-processing-thousands-of-smart-contracts-d814b378192). These programs are tested against Solana's implementation of Sealevel, solana-runtime, and deployed to its mainnet. 

There are several different program

- [Stake pool](https://spl.solana.com/stake-pool) to create different staking pool
- [Token-Lending](https://spl.solana.com/token-lending) program to create lending protocol
- [Token Swap Program]( https://spl.solana.com/token-swap): A Uniswap-like exchange for the Token program on the Solana blockchain, implementing multiple automated market maker (AMM) curves.

### Tokens on Solana

Tokens on Solana can be created through the **Token Program**, which defines a common implementation for Fungible and Non Fungible tokens.

There are two others accounts which are crucial:

- A [Mint Account](https://solana.com/docs/core/tokens#mint-account) represents a specific type of token and stores global metadata about the token such as the total supply and mint authority, which is the address authorized to create new units of a token.
- A [Token Account](https://solana.com/docs/core/tokens#token-account) keeps track of individual ownership of how many units of a specific type of token (mint account) are owned by a specific address.

See also my article [Fungible Tokens across blockchains - Solana (SPL token)](https://rya-sge.github.io/access-denied/2024/07/12/fungible-tokens-blockchains/#solana-spl-token)

Reference: [solana.com/docs/core/tokens](https://solana.com/docs/core/tokens)

- Tokens programs: to create different SPL token

| Ethereum / [ERC-20](https://eips.ethereum.org/EIPS/eip-20)   | Solana / SPL token                                           |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Fungible tokens use the ERC-20 standard, a general interface that an ERC-20 token must respect | Integrated program<br />No general interface                 |
| Smart contract template to create a new token                | There is a single token program (spl-token-progran)          |
| To create a new token, you deploy ERC smart contract on-chain | You deploy and interact with SPL program via Solana CLI, see [my article](https://rya-sge.github.io/access-denied/2022/08/06/solana-spl-token/) |

Example

![solana-token-program.drawio](/home/ryan/Downloads/me/brouillon-article/blockchain/solana/solana-token-program.drawio.png)

We have our *Token Program* and our *System Program*

1. The user Alice owns the private key of the *System Account* (wallet)
2. First, we ask our T*oken program* to create our *Mint account*
   1. This mint account is owned by *Token Program*
   2. The `mint_authority` can burn and mint tokens. It can be our user Alice
   3. The *Token Program* contains several different fields related to fungible tokens: supply, decimal
3. Alice with its wallet can ask the Mint account to burn and mint tokens from the Token Account to the Alice wallet

## PDA Hand on Example

Program Derived Addresses (PDAs) provide developers on Solana with two main use cases:

- **Deterministic Account Addresses**: PDAs provide a mechanism to deterministically derive an address using a combination of optional "seeds" (predefined inputs) and a specific program ID.
- **Enable Program Signing**: The Solana runtime enables programs to "sign" for PDAs which are derived from its program ID.

[https://solana.com/docs/core/pda](





## Transactions and Instructions [#](https://solana.com/docs/core#transactions-and-instructions)

On Solana, we send [transactions](https://solana.com/docs/core/transactions#transaction) to interact with the network. Transactions include one or more [instructions](https://solana.com/docs/core/transactions#instruction), each representing a specific operation to be processed. The execution logic for instructions is stored on [programs](https://solana.com/docs/core/programs) deployed to the Solana network, where each program stores its own set of instructions.

Learn more about [Transactions](https://solana.com/docs/core/transactions) and [Instructions](https://solana.com/docs/core/transactions#instruction) here.

## Fees on Solana [#](https://solana.com/docs/core#fees-on-solana)

The Solana blockchain has a few different types of fees and costs that are incurred to use the permissionless network. These can be segmented into a few specific types:

- [Transaction Fees](https://solana.com/docs/core/fees#transaction-fees) - A fee to have validators process transactions/instructions
- [Prioritization Fees](https://solana.com/docs/core/fees#prioritization-fees) - An optional fee to boost transactions processing order
- [Rent](https://solana.com/docs/core/fees#rent) - A withheld balance to keep data stored on-chain

Learn more about [Fees on Solana](https://solana.com/docs/core/fees) here.

## Programs on Solana [#](https://solana.com/docs/core#programs-on-solana)



## Program Derived Address [#](https://solana.com/docs/core#program-derived-address)

Program Derived Addresses (PDAs) provide developers on Solana with two main use cases:

- **Deterministic Account Addresses**: PDAs provide a mechanism to deterministically derive an address using a combination of optional "seeds" (predefined inputs) and a specific program ID.
- **Enable Program Signing**: The Solana runtime enables programs to "sign" for PDAs which are derived from its program ID.

You can think of PDAs as a way to create hashmap-like structures on-chain from a predefined set of inputs (e.g. strings, numbers, and other account addresses).

Learn more about [Program Derived Address](https://solana.com/docs/core/pda) here.

## Cross Program Invocation [#](https://solana.com/docs/core#cross-program-invocation)

A Cross Program Invocation (CPI) refers to when one program invokes the instructions of another program. This mechanism allows for the composability of Solana programs.

You can think of instructions as API endpoints that a program exposes to the network and a CPI as one API internally invoking another API.

Learn more about [Cross Program Invocation](https://solana.com/docs/core/cpi) here.

