---
layout: post
title: "Solana Staking - Overview"
date:   2025-11-09
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: blockchain solana security
tags: solana staking
description: How Solana staking works, from stake accounts and their stake and withdraw authorities to delegation, warm-up, cooldown and the stake program instructions.
image: /assets/article/blockchain/solana/2025-11-07-solana-staking-overview-mindmap.png
isMath: false
---

Staking in Solana is the process of locking SOL tokens in a stake account to participate in network consensus and earn rewards. 

Stakers delegate their SOL to a **validator’s vote account**, helping secure the network. 

Validators then earn rewards for producing blocks, which are shared with stakers.

Key concepts:

- **Stake Account:** A separate account that holds staked SOL. Only SOL in stake accounts can be delegated to validators.
- **Stake Authority:** The key that can manage the stake (delegate, split, deactivate, withdraw).
- **Withdraw Authority:** The key that can withdraw SOL from the stake account.
- **Lockup:** Optional restrictions preventing withdrawals until a certain epoch or date.
- **Delegation:** Assigning staked SOL to a validator’s vote account.
- **Epoch:** A fixed period in Solana (≈2–3 days) after which rewards are calculated and stake changes take effect.



## What you need to know first

The stake instructions below rely on a few parts of Solana's runtime that the article uses without explaining them.

- **Accounts and lamports**: on Solana, state lives in accounts, each holding a balance in lamports and owned by a program that alone can debit it or change its data. One SOL is one billion lamports. A stake account is such an account, owned by the Stake program; see [Solana Core Concept]({{site.url_complet}}/2024/09/19/solana-core-concept/).
- **Rent exemption**: an account must keep a minimum lamport balance, proportional to its data size, to stay on-chain. This reserve is why a stake account delegates its whole balance minus the rent-exempt amount.
- **Instruction accounts and their flags**: every instruction lists the accounts it reads or writes, each marked as writable, signer or neither. The `[WRITE]`, `[SIGNER]` and `[]` notation in the article follows this convention, and a `[SIGNER]` account must have signed the transaction.
- **Sysvars**: special read-only accounts through which programs read cluster state, such as the Rent sysvar, which gives the parameters for the rent-exempt minimum. `Initialize` takes the Rent sysvar as an input account.
- **Validators and vote accounts**: a validator takes part in consensus by submitting votes through its vote account, and stake is delegated to that vote account rather than to the validator's identity key. A validator that stops voting is called delinquent, which is what `DeactivateDelinquent` checks.
- **Seed-derived addresses**: an address can be derived from a base public key, a seed string and an owner program, and the base key's signature then authorizes actions for that address. `AuthorizeWithSeed` and `AuthorizeCheckedWithSeed` use this when the current authority is such a derived address.

## Key Stake Instructions in Solana

### A. Creating/Initializing a Stake Account

- **`Initialize` / `InitializeChecked`**
  - Sets up a new stake account with:
    - **Authorized keys** (stake authority and withdraw authority)
    - Optional **lockup**
  - `InitializeChecked` requires the withdraw authority to sign and no lockup is applied.
- **Accounts Involved:**
  - `[WRITE]` Uninitialized stake account
  - `[]` Rent sysvar
  - `[SIGNER]` Withdraw authority (for InitializeChecked)

**Effect:** Your stake account is ready to receive SOL for staking.

------

### B. Delegating Stake

- **`DelegateStake`**
  - Sends all SOL in a stake account to a **validator’s vote account**.
  - Starts **warm-up period**: the stake gradually becomes active over epochs.
  - You can **re-delegate**, but it will take effect after an epoch.
- **Accounts Involved:**
  - `[WRITE]` Stake account to be delegated
  - `[]` Validator vote account
  - `[SIGNER]` Stake authority

**Effect:** Your SOL begins earning rewards after warm-up.

------

### C. Managing Stake

- **`Authorize` / `AuthorizeChecked` / `AuthorizeWithSeed` / `AuthorizeCheckedWithSeed`**
  - Change the **stake or withdraw authority**.
  - Useful for delegating management to another key.
- **`SetLockup` / `SetLockupChecked`**
  - Apply or update withdrawal restrictions (epoch/date/custodian).

**Effect:** Control over who can manage or withdraw the stake, and enforce lockup rules.

------

### D. Adjusting Stake

- **`Split`**
  - Divide a stake account into two accounts.
  - Useful for managing smaller delegations or moving stake between validators.
- **`Merge`**
  - Combine two stake accounts with identical authorities and lockup.
  - Useful for consolidating multiple small stakes.
- **`Withdraw`**
  - Withdraw lamports (SOL) that are not staked: the balance above the delegated amount, or the stake once its cooldown after `Deactivate` is over.
  - Cannot withdraw staked SOL, including stake that is still in cooldown.
- **`Deactivate`**
  - Stop earning rewards and begin cooldown before withdrawal.
  - Stake must go through an **unbonding period** before becoming withdrawable.
- **`Redelegate`** (deprecated, never enabled)
  - Was designed to move activated stake from one validator to another, creating a new stake account for the redelegated SOL and scheduling the old stake for deactivation.
  - The stake program marks it deprecated since version 2.1.0 with the note "Redelegate will not be enabled". To change validator, use `Deactivate`, wait for the cooldown, then `DelegateStake` again.

------

### E. Special Stake Operations

- **`DeactivateDelinquent`**
  - Automatically deactivates stake delegated to a validator that has been **delinquent** for too long.
  - No signer required — protects network from inactive validators.
- **`GetMinimumDelegation`**
  - Returns the minimum amount of SOL required to delegate stake.

------

## Lifecycle of a Stake Account

Here’s a step-by-step example of how a stake account moves through states:

1. **Initialize** → stake account is created.
2. **DelegateStake** → stake starts warming up (activating).
3. **Fully activated** → stake earns rewards.
4. **Optional actions:**
   - **Split** → create new stake accounts.
   - **Merge** → consolidate stake accounts.
   - **Authorize** → update authority keys.
   - **SetLockup** → add withdrawal restrictions.
5. **Deactivate** → stake begins cooldown.
6. **Withdraw** → SOL is unlocked and can be moved elsewhere.

------

## Key Notes

- **Cooldown/activation:** SOL doesn’t instantly become active or withdrawable. Warm-up/cooldown periods are defined in epochs.
- **Delegation balance:** The entire stake account balance is delegated, minus any lamports reserved for rent exemption.
- **Authority separation:** You can have separate keys for staking, which manages delegation, and for withdrawal, which takes out SOL.

## Instruction

| **Instruction**                                  | **Purpose**                                                  | **Key Accounts / Signers**                                   | **Notes**                                                    |
| ------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Initialize**                                   | Create a new stake account with authorities and optional lockup | `[WRITE]` Uninitialized stake account, `[]` Rent sysvar, `Authorized` keys | Stake ready to receive SOL                                   |
| **InitializeChecked**                            | Same as Initialize, but withdraw authority must sign; no lockup | `[WRITE]` Uninitialized stake account, `[]` Rent sysvar, `[SIGNER]` Withdraw authority | Safe version of Initialize                                   |
| **Authorize / AuthorizeChecked**                 | Change stake or withdraw authority                           | `[WRITE]` Stake account, `[SIGNER]` current authority, `[SIGNER]` new authority (checked) | Checked versions require new authority to sign               |
| **AuthorizeWithSeed / AuthorizeCheckedWithSeed** | Same as above but for derived keys                           | `[WRITE]` Stake account, `[SIGNER]` base authority           | Optional lockup authority if updating withdrawer             |
| **SetLockup / SetLockupChecked**                 | Apply or update withdrawal restrictions                      | `[WRITE]` Stake account, `[SIGNER]` lockup or withdraw authority | Checked requires new lockup authority to sign                |
| **DelegateStake**                                | Delegate stake to validator vote account                     | `[WRITE]` Stake account, `[]` Vote account, `[SIGNER]` Stake authority | Full balance is staked; warm-up period applies               |
| **Split**                                        | Split a stake account into two                               | `[WRITE]` Source stake, `[WRITE]` Uninitialized destination, `[SIGNER]` Stake authority | Destination receives split lamports                          |
| **Merge**                                        | Merge two stake accounts                                     | `[WRITE]` Destination, `[WRITE]` Source, `[SIGNER]` Stake authority | Requires same authorities & lockup; only compatible states can merge |
| **Withdraw**                                     | Withdraw unstaked lamports                                   | `[WRITE]` Stake account, `[WRITE]` Recipient, `[SIGNER]` Withdraw authority | Cannot withdraw staked lamports, including stake still in cooldown; lockup may apply |
| **Deactivate**                                   | Begin cooldown for stake                                     | `[WRITE]` Delegated stake account, `[SIGNER]` Stake authority | Stake stops earning rewards during cooldown                  |
| **Redelegate** (deprecated, never enabled)       | Move activated stake to another validator                    | `[WRITE]` Source stake, `[WRITE]` Destination stake, `[]` Vote account, `[SIGNER]` Stake authority | Deprecated since stake program 2.1.0 ("Redelegate will not be enabled") |
| **DeactivateDelinquent**                         | Deactivate stake from delinquent validator                   | `[WRITE]` Delegated stake, `[]` Delinquent vote, `[]` Reference vote | No signer required; protects network                         |
| **GetMinimumDelegation**                         | Return minimum delegation amount                             | None                                                         | Useful for programs or validation                            |

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Lamport** | The smallest unit of SOL, used for account balances and for the amounts moved by `Split` and `Withdraw`. |
| **Rent exemption** | The minimum lamport balance an account must hold to stay on-chain; a stake account keeps it out of the delegated amount. |
| **Stake account** | An account owned by the Stake program that holds the SOL to be staked; only SOL in a stake account can be delegated. |
| **Stake authority** | The key that manages a stake account: delegating, splitting, merging and deactivating it. |
| **Withdraw authority** | The key that can withdraw SOL from a stake account and must sign `InitializeChecked`. |
| **Lockup** | An optional restriction that prevents withdrawals until a given epoch or date. |
| **Custodian** | The key named in a lockup that can update the lockup's restrictions. |
| **Vote account** | The validator's account that receives delegations and through which the validator votes. |
| **Delegation** | Assigning the SOL in a stake account to a validator's vote account with `DelegateStake`. |
| **Epoch** | A fixed period of about two to three days, at the end of which rewards are calculated and stake changes take effect. |
| **Warm-up** | The period after delegation during which stake becomes active gradually over epochs. |
| **Cooldown** | The period after `Deactivate` during which stake winds down before it can be withdrawn. |
| **Delinquent validator** | A validator that has stopped voting for too long, whose delegated stake anyone can deactivate with `DeactivateDelinquent`. |
| **Split and Merge** | `Split` divides a stake account into two, and `Merge` combines two stake accounts that have the same authorities and lockup. |
| **Minimum delegation** | The smallest amount of SOL that can be delegated, returned by `GetMinimumDelegation`. |

## Mindmap

The mindmap below summarizes the article.

![Solana staking overview mindmap]({{site.url_complet}}/assets/article/blockchain/solana/2025-11-07-solana-staking-overview-mindmap.png)

## Reference

- [github.com/solana-program/stake - instruction.rs](https://github.com/solana-program/stake/blob/main/interface/src/instruction.rs)
