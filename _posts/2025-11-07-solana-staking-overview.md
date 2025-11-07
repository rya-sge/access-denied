---
layout: post
title: "Solana Staking - Overview"
date:   2025-11-09
lang: en
locale: en-GB
categories: blockchain solana security
tags: solana staking
description: 
image: 
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
  - Withdraw lamports (SOL) that are not actively staked or during cooldown.
  - Cannot withdraw staked SOL unless deactivated.
- **`Deactivate`**
  - Stop earning rewards and begin cooldown before withdrawal.
  - Stake must go through an **unbonding period** before becoming withdrawable.
- **`Redelegate`**
  - Move activated stake from one validator to another.
  - Creates a new stake account for the redelegated SOL and schedules old stake for deactivation.

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
- **Authority separation:** You can have separate keys for staking (manage delegation) and withdrawal (take out SOL).

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
| **Withdraw**                                     | Withdraw unstaked lamports                                   | `[WRITE]` Stake account, `[WRITE]` Recipient, `[SIGNER]` Withdraw authority | Cannot withdraw staked lamports; lockup may apply            |
| **Deactivate**                                   | Begin cooldown for stake                                     | `[WRITE]` Delegated stake account, `[SIGNER]` Stake authority | Stake stops earning rewards during cooldown                  |
| **Redelegate**                                   | Move activated stake to another validator                    | `[WRITE]` Source stake, `[WRITE]` Destination stake, `[]` Vote account, `[SIGNER]` Stake authority | Old stake scheduled for deactivation; new stake starts activation |
| **DeactivateDelinquent**                         | Deactivate stake from delinquent validator                   | `[WRITE]` Delegated stake, `[]` Delinquent vote, `[]` Reference vote | No signer required; protects network                         |
| **GetMinimumDelegation**                         | Return minimum delegation amount                             | None                                                         | Useful for programs or validation                            |

## Diagram