---
layout: post
title:  Solana Programs - Basic Security with Anchor
date:   2024-08-20
lang: en
locale: en-GB
categories: blockchain
tags: blockchain
description: Basic Security tips to write Secure Solana Programs, based on School of Solana Season 5 by Ackee Blockchain Security
image:  /assets/article/blockchain/solana/solanaVerticalLogo.png
isMath: false
---

This article is a summary of the video [Security: Writing Secure Solana Programs](https://www.youtube.com/watch?v=Qkf9QwSfHAM) By Ackee Blockchain Security. This video is the lecture 6 of their cursus *School of Solana Season 5*.

You can also find the written version on [GitHub](https://github.com/Ackee-Blockchain/school-of-solana/tree/master/6.lesson#signer-authorization).

See also [solana.com/developers - security-intro](https://solana.com/developers/courses/program-security/security-intro)

[TOC]

##  Motivation

Over $500 millions were stolen on Solana ecosystem

- [Wormhole: ~$338M](https://www.theverge.com/2022/2/3/22916111/wormhole-hack-github-error-325-million-theft-ethereum-solana)
- [cashio ~$52M](https://www.halborn.com/blog/post/explained-the-cashio-hack-march-2022)
- [Crema Finance ~$8M](https://www.halborn.com/blog/post/explained-the-crema-finance-hack-july-2022)
- [Mango Marget](https://www.halborn.com/blog/post/explained-the-mango-markets-and-attempted-aave-hacks-october-2022)

## Basic Security Tips

- Use [Anchor](https://www.anchor-lang.com) in most cases
  - Saves a lot of boilerplate code
  - Most Solana specific checks within context <> structs
  - Easier for others to review your code
- Tests extensively
  - Focus on unhappy patch scenario. Think like a hacker
- Have your project audited: we all make mistakes

## Common Security exploits

1. Signer check
2. Address check
3. Ownership check
4. Arbitrary CPI
5. Math & logic issues
6. Reintialization and revival attacks
7. Other

###  #1 Signer check

- Verify that the right parties have signed a transaction

- Without a signer check, operations whose execution should be limited to only specific accounts can potentially be performed by any account. 

- Use Anchor's Signer <info> type

**Example**

A user wants to update some data on-chain.

One input account is the user account, and the other is the data account

account is the PDA address based on a seed.

```rust
#[derive(Accounts)]
pub struct UpdateUserDara<'info>{
    // performs signer check
	#[account(mut)]
	user: Signer<'info>,
	
	#[acount(seeds=[b"user-data", user.key().as_ref()],
		bump
	]
	data: Account<'info, UserData>,
}
```

An insecure version of that could be:

```rust
user: AccountInf<'info>,
```

This type is insecure because doesn't check anything. Anyone who know the public key can supply the correct user account and update the data of any users.

Instead of

```rust
user: Signer<'info>,
```

In this case, you can not supply a different user account for a given data account

See also [Signer Authorization](https://solana.com/developers/courses/program-security/signer-auth), [www.rareskills.io/post/anchor-signer - Modifying accounts using different signers](https://www.rareskills.io/post/anchor-signer)

### #2 Address check

>  Verify that an account has the expected address(public key)

As a reminder, with Solana Programming model, each program needs as input all account it will use (read and write).

You have to verify that the accounts supplied are the ones you expect

#### Example

**Insecure version**

```rust
#[account]
pub struct ConfigData {
 	pub admin: Pubkey,
 	pub data: u8
}
```



First account is the admin account who must sign the transaction

In this case, it is insecure because the admin account is not bound to the config Account and to the data itself. You have to check that the admin account is the same as saved on the configData

Here an attacker can supply any kind of account as an admin and sign the transaction, and supply the ConfigData on your programm,

```rust
#[derive(Accounts)]
pub struct UpdateConfig<'info>{
	#[account(mut)]
	admin: Signer<'info>,
	#[account(mut),
		seeds = [b"config"],
		bump
		)]
		config: Account<'info, ConfigData
}
```

**Secure version**

We add here a constraint `has_one`. Here the name `admin`has to match the admin in the data structure. The admin provided must have the same public key that stored in the config.

```rust
#[derive(Accounts)]
pub struct UpdateConfig<'info>{
	#[account(mut)]
	admin: Signer<'info>,
	#[account(mut),
		has_one = admin,
		seeds = [b"config"],
		bump
		)]
		config: Account<'info, ConfigData
}
```

Reminder:

`has_one`is an anchor constraint which checks the `target_account` field on the account matches the key of the `target_account` field in the Account struct

See [Anchor - account-constraints](https://www.anchor-lang.com/docs/account-constraints)

```rust
#[account(
  has_one = <target_account>
)]
```



### #3 Ownership check

>  Verify that an account is owned by the expected program

Anchor program account types implement the `Owner` trait which allows the `Account<'info, T>` wrapper to automatically verify program ownership.

See also [Anchor-lang - account-types](https://www.anchor-lang.com/docs/account-types)

#### Example

**Insecure version**

Here `Config Account` might be owned by another program and any account with the required data structure might be supplied.

```
#[derive(Account)]
pub struct WithdawFees<'info>{
	#[account(mut)]
	admin: Signer<'info>,
	
	// admin.key() == config.admin.key() is check in instruction
	#[account(mut)]
	config: AcccountInfo<'info>,
	
	#[account(mut, seeds = ["treasury"], bump)]
	treasury: AccountInfo<'info'>
}
```

**Secure version**

We replace

```rust
#[account(mut)]
config: AcccountInfo<'info>,
```

`AcccountInfo` does not check the ownership on deserialization.

by

```rust
#[account(mut, has_one = admin)]
config: Acccount<'info, ConfigData>,
```

We use Anchor's Account<'info, T> type that checks automatically the owner.

The owner of this account should be your program to work.

In some casey, if you want that the owner is a different program, you can use the owner constraint.

Full code

```rust
#[derive(Account)]
pub struct WithdawFees<'info>{
	#[account(mut)]
	admin: Signer<'info>,
	
	#[account(mut, has_one = admin)]
	config: Acccount<'info, ConfigData>,
	
	#[account(mut, seeds = ["treasury"], bump)]
	treasury: AccountInfo<'info'>
}
```



### #4 Arbitrary CPI (Cross Program Invocation)

> Verify that the target program you want to invoke has the correct address.

Use Anchor's Program<`info, T>  type that checks the program's address.

Programs that works out of the box are System, Token and AssociatedToken

Others programs must have the CPI modules generated.

Example:

1. Main program invokes an external program to transfer funds from user account to pool account and logs the events
2. External program verifies the correct address of the pool and transfers the funds from users to the pool.
3. If the main program does not verify the address of the external program, an arbitrary malicious program can be supplied

 The Anchor CPI module automatically checks that the  address of the program passed in matches the address of the program  stored in the module.

The best practice while using Anchor is to always use `Program<'info, T>`, which will check that the account is executable and it is the given Program. For example:

```rust
use anchor_spl::token::Token;

#[derive(Accounts)]
pub struct InitializeExchange<'info> {
    // ...
    pub token_program: Program<'info, Token>,
    // ...
}
```

### #5 Math & Logic Issues

- Beware of arithmetics and precision issues
- Validate account data and instruction parameters
- Make sure instructions are executed in correct orders

Example

```rust
require!(voting_state == VotingStage::Started);
```

- Prevent unintended behavior when passing duplicate accounts

Example:

Here we check that user A and user B are not the same account thouth an Anchor constraint.

The security check is kept all the security check within the context

```rust
#[derive(Accounts)]
pub struct Update<'info>{
	#[account(constraint = user_a.key() != user_b.key())]
    user_a: Account<'info, User>,
    user_b: Account<'info, User>,
}
```



### #6 Reintialization and revival attacks

- Don't re-initialize an already initialized account

In Anchor, you can use the `init`constraint on our account.

If already set, then it will not be re-initialized

```rust
#[derive(Accounts)]
pub struct InitVoting<'info'>{
	#[account(init,...)]
	voting: Account<'info, Voting>
}
```

From anchor doc:

```rust
#[account(
  init,
  payer = <target_account>,
  space = <num_bytes>
)]
```

See [anchor-lang.com/docs/account-constraints](https://www.anchor-lang.com/docs/account-constraints)

- Don't re-use an already closed account

In Solana, to close an account, you have to put its lamport balance to zero. The account will be garbage collectrf on runtime

The garbage collection runs only after the transaction is finished. If the account is not closed properly, an attacker can close an account in one instruction and can directly open again the account by sending lamports and therefore the account will not be garbage collected.

```rust
#[derive(Accounts)]
pub struct CloseAccount {
    #[account(
        mut,
     close = receiver)]
    pub data_account: Account<'info, MyData>,
    #[account(mut)]
    pub receiver: SystemAccount<'info>
}
```

Note: newer versions of Anchor do not use closed account discriminator anymore. The account data is clearer and the owner is assigned back to the system program.

From the [Anchor doc](https://www.anchor-lang.com/docs/account-constraints)

```rust
#[account(close = <target_account>)]
```

Closes the account by:

- Sending the lamports to the specified account
- Assigning the owner to the System Program
- Resetting the data of the account

Requires mut to exist on the account.

### #7 Others issues

- Verify account data type to avoid cosplay

An attacker could supply data with different datatype and the programs will deserialize it with the wrong datatype.

In Anchor is very easy, you can only use the account type with the given type. The anchor checks the discriminator at the beginning of your data to match the datatype

In Anchor is very easy, you can only use the account type with the given type. The anchor checks the discriminator at the beginning of your data to match the datatype

```rust
data: Account<'info, DataAccount>,
user: Signer<'info'>
```



- Use canonical bump to avoid multiple valid PDAs

canonical bump means that this is the very first value of your bump when you calculate the PDA address.

with Anchor, you can leave the bump empty, in this case Anchor will calculate the bump for your.

or you can use the bump stored previously during the initialization, here in data

```rust
bump = data.bump
```

- Do not use shared/global PDA authorities. Use account specific PDAs instead

In our example, we can see we have two accounts: data and user accounts

In our example, data account is related to the user account because the seeds are derived from the user public key address.

```rust
seeds=[user.key().as_ref()],
```

Full example:

```rust
#[derive(Accounts)]
pub struct Example<'info> {
    	#[acount(mut,
    	seeds=[user.key().as_ref()],
		bump = data.bump
	)]
	data: Account<'info, DataAccount>,
	user: Signer<'info'>
}
```

