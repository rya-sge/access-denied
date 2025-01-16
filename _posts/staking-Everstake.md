# Staking with Everstake

[everstake - ethereum](https://stake.everstake.one/ethereum/)

| Label                        | Value                                                        |
| ---------------------------- | ------------------------------------------------------------ |
| Reward fee                   | 10%                                                          |
| Minimum amount to stake      | 0.1 ETH                                                      |
| Annual percentage rate (APR) | 4-10%<br />                                                  |
| APY                          | Through Trezor: 4.05%                                        |
| Stakers                      | ?                                                            |
| Wallet Integration           | Trezor and Zengo wallet                                      |
| Security                     | Solution audited by [ChainSecurity](https://chainsecurity.com/security-audit/everstake-eth-b2c-staking/) and [Ackee](https://ackeeblockchain.com/blog/everstake-ethereum-staking-protocol-audit-summary/) |

Through Trezor

| Minimum amount to stake | 0.1 ETH    |
| ----------------------- | ---------- |
| APY                     | 4.05%br /> |
| Time to unstake         | 9 days     |
|                         |            |

Reware are automatcally restaked





Minimum amount to stake: 

Integration: partnered with 

See 

- [How to stake ETH via Trezor Suite](https://everstake.one/blog/how-to-stake-eth-via-trezor-suite)
- [How to stake ETH via Zengo Wallet](https://everstake.one/blog/how-to-stake-eth-via-zengo-wallet)

Security

https://x.com/everstake_pool/status/1783101315305894335

https://stake.everstake.one/ethereum/

Solution audited

### 

## How it works

- Everstake 0.1+ ETH staking solution is a protocol enabling one to stake amounts under 32 ETH.
- Once combined users’ deposits exceed 32 ETH, a new validator launches and starts generating rewards.
- The rewards are re-staked automatically, increasing pool shares of respective users and their next rewards.
- You can accelerate your Results by putting assets received from staking back into staking you can amplify the compounding effect and boost your overall results.

## Architecture

![everstake-architecture](/home/ryan/Downloads/me/access-denied/assets/article/blockchain/ethereum/staking/everstake-architecture.png)

## Smart contract architecture

According to the Ackkee Blockchain report, here the main smart contracts:

```solidity
contracts/
├── Accounting.sol
├── AutocompoundAccounting.sol 
├── Governor.sol
├── Pool.sol
├── RewardsTreasury.sol
├── TreasuryBase.sol
├── WithdrawTreasury.sol 
├── Withdrawer.sol
├── common
│      └── Errors.sol
├── interfaces
│  ├── IAccounting.sol
│  ├── IDepositContract.sol
│  ├── IPool.sol
│  ├── IRewardsTreasury.sol
│  └── ITreasuryBase.sol
├── lib
│  ├── UnstructuredRefStorage.sol
│  └── UnstructuredStorage.sol
├── structs 
│  ├── ValidatorList.sol 
│  └── WithdrawRequests.sol
└── utils
      ├── Math.sol
      └── OwnableWithSuperAdmin.sol
```

### Pool

The Pool holds a list of validators that are managed by Everstake and can be used when the pending amount in the Pool reaches 32ETH. 

When it does, a validator is consumed from the list and the beacon deposit contract is called with the validator's public key, signature, and deposit data root along with the address of the rewards treasury encoded in the withdrawal credentials. The Pool contract is the main entry point of the system, it offers the following functions for the users:

#### Stake

The function `stake`is called along with ETH, the `msg.value` must be at least the minimum stake amount. The function will first reinvest any rewards (`Accounting._autocompound`) and deposit the caller's stake, or part of it, either in the withdraw treasury if some amount can be interchanged, in the pending buffer if the total pending amount is not sufficient to launch a new validator, or in one or more yet inactive validators if the sum of the user's value and the pending amount can cover the beacon amount or more. If some of the stake can be interchanged, the associated shares are instantly minted to the new staker. Can only be called when staking is not paused. _

#### unstakePending

A staker whose stake is still pending (not sent to a validator) can use this function to reduce its stake. This function will first update the internal accounting for the rewards treasury (Accounting.update), then reduce the pending stake of the caller and send back the requested value. Can only be called when withdrawals are not paused. 

#### Unstake

a staker who has shares can use this function to initiate a withdrawal of their active stake. The function will first reinvest any rewards (Accounting._autocompound), then if some pending amount is available it will be interchanged as much as possible and the remaining value, if any, will be added to a withdrawal request. The withdrawal request will request the closing of one or more validators if the requested amount exceeds one or more beacon amounts and Everstake will be notified. The remaining amount will be made available for interchange, and the request will be added to a withdrawal request queue. The user can claim the withdrawal as soon as the requested amount is available in the withdraw treasury. If a user initiates the withdrawal of at least 32ETH, a validator will be closed even if it could be that interchange could be covered to avoid closing one or several validators. 

The privileged roles owner, governor, and superAdmin can call the following functions: 

| Function Name           | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| setPendingValidators    | add a new validator in the validators list. Everstake is trusted to regularly add new validators to the list to keep the system running. |
| replacePendingValidator | replace a pending validator in the validators list           |
| markValidatorsAsExited  | marks one or several validators as exited so their slots in the validators list can be reused |
| pauseStaking            | pause/unpause the staking                                    |
| pauseWithdraw           | pause/unpause the withdrawals                                |
| setMinStakeAmount       | set a minimum staking amount                                 |

### Accounting

The Accounting contract holds all the logic related to internal accounting, rewards reinvestment, rounds management, deposits, interchange and withdrawals operations.

#### Exist stake and rewards auto-compounding

The functions responsible for closed validators' stake management and rewards reinvestment are:

- update() / _update(): sends the stake returned by closed validators from the reward treasury to the withdraw treasury and computes the rewards and associated fees if any amount is left, then updates the internal accounting of the cached rewards treasury balance, as well as the fees and rewards balances held by the rewards treasury. 

- autocompound() / _autocompound(): calls _update() first, if the rewards balance of the rewards treasury is above the minimum restake amount, the rewards are accounted for, and interchanged if possible. The rewards are added to the total deposited amount but no shares are minted. If the total pending amount is sufficient to launch one or more validators, the Accounting will trigger a restake which will deposit to new validators.

#### Internal accounting

The internal accounting tracks for each staker the amount they deposited in every current and past active rounds that are not yet activated, as well as the active stake in the form of shares. 

At the end of each active round, a snapshot of the user's part of the deposited beacon amount is taken, so that shares can be minted when the round becomes activated (when the validator they have their stake in is activated in the beacon chain). 

When the validator for a round is activated, Everstake will call `activateValidators`, which will 

1. Take a snapshot of the current total deposited amount and the current supply of shares, 
2. mint the shares related to that round, 
3. and update the total deposited amount, as well as the total supply of shares. 

Users will claim their already minted shares for an activated round whenever they stake again or unstake, this is done within `_autocompoundAccount`. 

Upon withdrawal of the active stake, the associated shares will be burned. 

The exiting amount will first be interchanged as much as possible with the pending stakers and the pending rewards to be restaked, if the pending amount cannot cover the withdrawal amount, the difference will be added in a withdrawal request that can be claimed when enough liquidity has been accrued in the withdraw treasury. 

Note that the accounting functions deposit, withdraw, and withdrawPending are expected to be called for msg.sender by the superAdmin of the Accounting, which is the Pool, but they can also be called by the owner for arbitrary addresses.

## Treasuries

The treasuries are contracts used by the Accounting to store the funds obtained from the validators (rewards or returned stake of closed validators) and the funds to be withdrawn by users. 

Both treasuries have a function `sendEth`, this function sends Eth to some arbitrary address given as a parameter and can only be called by the rewarder of the contract.

### Reward Treasury

In addition to sendEth, the RewardTreasury defines reStake, a function used to call the pool's restake function together with sending some amount of ETH. 

The address of the RewardTreasury is given as part of the withdrawal_credentials parameter to the call to the deposit function of the beacon deposit contract done by the pool. 

This means that rewards and returned stakes from every validator will be sent to the treasury. The balance of the treasury is then used in the following ways by the accounting contract using sendEth and reStake: 

- Funds from a closing validator are sent to the withdraw treasury. 
- Funds from rewards are split in two by the accounting: 
  - Rewards fees stay in the RewardsTreasury, but are accounted for in the Accounting so that the owner of the Accounting contract can claim them. 
  - The rest of the rewards are sent to the pool using restake or to the withdraw treasury depending on if they get interchanged or not during the auto-compounding

### Withdraw Teasury

The withdrawTreasury can receive ETH in the following ways: 

- From the RewardTreasury as mentioned above (either a closing of validator or by interchanging the rewards). 
- From the Pool when a user is staking and part of his stake is interchanged. The funds in the treasury are then used by `_claimWithdrawRequest` to send the ETH to a user claiming a withdrawal request.

### Access Control

Users of the system are generally untrusted and expected to behave unpredictably. The following roles are fully trusted and expected to behave honestly and correctly. •

- The owner, the superAdmin and the governor of the Pool. 
- The owner and the governor of the Accounting. 
- The owner of the RewardTreasury. 
- The owner of the WithdrawTreasury. 

More specifically, the owner of the RewardTreasury and Withdraw are allowed to send ETH from those contracts and are trusted to use this functionality only in case of emergency. 

The owner of Accounting can make calls inside the Accounting contract in the name of arbitrary addresses and is trusted to use this functionality only in case of emergency. 

The superAdmin of the Accounting is assumed to be the address of the Pool. 

The rewarder of both the RewardTreasury and the WithdrawTreasury are assumed to be the address of the Accounting. 

Everstake is trusted in providing and managing the validators correctly by avoiding slashing, claiming the rewards when it is needed and closing the validators when the contract requires it. Everstake is trusted in providing liquidity to facilitate stake and unstake demand.

### Slashing

In case of slashing, Everstake added a feature to stop the update of rewards in case of emergency. See point *7.6 Slashing Is Not Taken Into Account* from ChainSecurity audit report



When it comes to updating the user's balance and refunding the users,



see Trust Model and Users may not be fully refunded in case of slashing.

The exact procedure in case of slashing is not known. Everstake provided us with the following flow in case of slashing: 

1. Wait the closest time until the validator exit 
2. Stop rewards update 
3. Update Pool balances 
4. Activate a new validator 

Some solution thought by Everstake, but not necessary put in place currently

-  Slashing coverage within pool with higher fee rate in collaboration of Insurance services. 
- Pool without slashing coverage with lower fee rate, that will require in case of emergency to deploy changes that could help to update pool balances. 
- In order to mitigate users' loss in case of slashing, Everstake plans to deploy a special emergency treasury fund, where part of the fee can be used to refund the users.
- Even if there is an emergency treasure funds, Everstake does not guarantee all the users to be fully refunded in case of slashing. See point *9.3 Users May Not Be Fully Refunded in Case of Slashing* from ChainSecurity audit report



## Security

- The 0.1+ ETH staking solution has been audited by ChainSecurity, ensuring it meets industry standards for safety and reliability. [Report](https://chainsecurity.com/security-audit/everstake-eth-b2c-staking/)
- The staking platform also passed an audit by Ackee, affirming its security and operational excellence. [VIEW REPORT](https://ackeeblockchain.com/blog/everstake-ethereum-staking-protocol-audit-summary/)