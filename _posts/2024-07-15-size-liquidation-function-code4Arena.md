---
layout: post
title:  Size Code4Arena - Liquidation function
date:   2024-07-15
lang: en
locale: en-GB
categories: blockchain ethereum defi
tags: ethereum solidity security code4Arena
description: Size Protocol is a credit marketplace with unified liquidity across maturities. This article presents the liquidation function. This analyze has been done for the Code4Arena contest.
image: /assets/article/blockchain/defi/money-2180330_640.jpg
isMath: false
---

[Size Protocol](https://www.size.credit/) is a credit marketplace with unified liquidity across maturities.

This article presents the liquidation function from `Size protocol`. This analyze has been done for the [Code4Arena](https://code4rena.com/audits/2024-06-size) contest..

Since I have a limited time, I found that it could be interesting to focus only in one part in the liquidation function instead of the whole code.

[TOC]

## Introduction

### Links

- Previous audits:
  - https://github.com/code-423n4/2024-06-size/blob/main/audits/2024-03-19-LightChaserV3.md
  - https://github.com/code-423n4/2024-06-size/blob/main/audits/2024-03-26-Solidified.pdf
  - https://github.com/code-423n4/2024-06-size/blob/main/audits/2024-05-30-Spearbit-draft.pdf
- **Documentation:** [https://docs.size.cash/](https://docs.size.cash/)
- **Website:** https://size.credit/
- **X/Twitter:** https://x.com/SizeCredit

### Presentation

Loans not paid back by the due date also become eligible for liquidation. However, a smaller penalty is applied, assuming the loan remains well-collateralized.

Mainly from the documentation:

- The system relies on ETH collateral to collateralize borrow positions. 
- Fixed-rate loans use a collateralization ratio (collateral / debt) to measure risk. If the collateralization ratio drops below the liquidation threshold (i.e. 130%), ***all*** fixed-rate positions owned by that borrower become eligible for liquidation. 
- ETH collateral is over-collateralized at 130%.
- Positions are liquidated one at a time, and the liquidation threshold may rise back above the liquidation threshold if the liquidation is not unprofitable, giving the user another chance to supply more collateral.
- insurance reserve: While the system expects to generate a profit via liquidations, there may be times when liquidations are unprofitable. In this case, an insurance reserve, owned by the protocol, may attempt to cover losses to ensure solvency.

### Attack ideas

From Code4Arena description:

Liquidations: In Spearbit's security review, several High and Medium-severity vulnerabilities (5.2.1, 5.3.1, 5.3.3) were identified concerning liquidation and self-liquidation incentives. Consequently, we overhauled our incentives mechanism, moving away from a fixed overdue liquidation reward and a variable liquidation reward based on collateral ratio to a variable liquidation reward based on the loan's future value.

## Details

There are three functions to perform a liquidation: liquidate, selfLiquidate, liquidateWithReplacement

### Workflow

All these functions have the modifier whenNotPaused and perform:

1) Validate params
2) Execute with params
3) Validate the result

#### Liquidate

```solidity
    /// @inheritdoc ISize
    function liquidate(LiquidateParams calldata params)
        external
        payable
        override(ISize)
        whenNotPaused
        returns (uint256 liquidatorProfitCollateralToken)
    {
        state.validateLiquidate(params);
        liquidatorProfitCollateralToken = state.executeLiquidate(params);
        state.validateMinimumCollateralProfit(params, liquidatorProfitCollateralToken);
    }

```

#### validateLiquidate

```solidity
  function validateLiquidate(State storage state, LiquidateParams calldata params) external view {
        DebtPosition storage debtPosition = state.getDebtPosition(params.debtPositionId);

        // validate msg.sender
        // N/A

        // validate debtPositionId
        if (!state.isDebtPositionLiquidatable(params.debtPositionId)) {
            revert Errors.LOAN_NOT_LIQUIDATABLE(
                params.debtPositionId,
                state.collateralRatio(debtPosition.borrower),
                state.getLoanStatus(params.debtPositionId)
            );
        }

        // validate minimumCollateralProfit
        // N/A
    }
```

validateLiquidate: https://github.com/code-423n4/2024-06-size/blob/main/src/libraries/actions/Liquidate.sol#L37

Validates the input parameters for liquidating a debt position.

- Only validate the debt position.

- Don't validate the sender, all addresses can perform liquidation

- Don't validate a miminumCollateralProfit

#### executeLiquidate

executeLiquidate: https://github.com/code-423n4/2024-06-size/blob/main/src/libraries/actions/Liquidate.sol#L75

1) Get loan status
2) Compute the collateral ratio
3) Emit Event
4) Determine Protocol Fee Percentage by Checking if the loan is both underwater and overtue
5) Gets the assigned collateral and converts the debt value to collateral token value.



```solidity

    function executeLiquidate(State storage state, LiquidateParams calldata params)
        external
        returns (uint256 liquidatorProfitCollateralToken)
    {
        DebtPosition storage debtPosition = state.getDebtPosition(params.debtPositionId);
        LoanStatus loanStatus = state.getLoanStatus(params.debtPositionId);
        uint256 collateralRatio = state.collateralRatio(debtPosition.borrower);

        emit Events.Liquidate(params.debtPositionId, params.minimumCollateralProfit, collateralRatio, loanStatus);

        // if the loan is both underwater and overdue, the protocol fee related to underwater liquidations takes precedence
        uint256 collateralProtocolPercent = state.isUserUnderwater(debtPosition.borrower)
            ? state.feeConfig.collateralProtocolPercent
            : state.feeConfig.overdueCollateralProtocolPercent;

        uint256 assignedCollateral = state.getDebtPositionAssignedCollateral(debtPosition);
        uint256 debtInCollateralToken = state.debtTokenAmountToCollateralTokenAmount(debtPosition.futureValue);
        uint256 protocolProfitCollateralToken = 0;

        // profitable liquidation
        if (assignedCollateral > debtInCollateralToken) {
            uint256 liquidatorReward = Math.min(
                assignedCollateral - debtInCollateralToken,
                Math.mulDivUp(debtPosition.futureValue, state.feeConfig.liquidationRewardPercent, PERCENT)
            );
            liquidatorProfitCollateralToken = debtInCollateralToken + liquidatorReward;

            // split the remaining collateral between the protocol and the borrower, capped by the crLiquidation
            uint256 collateralRemainder = assignedCollateral - liquidatorProfitCollateralToken;

            // cap the collateral remainder to the liquidation collateral ratio
            //   otherwise, the split for non-underwater overdue loans could be too much
            uint256 collateralRemainderCap =
                Math.mulDivDown(debtInCollateralToken, state.riskConfig.crLiquidation, PERCENT);

            collateralRemainder = Math.min(collateralRemainder, collateralRemainderCap);

            protocolProfitCollateralToken = Math.mulDivDown(collateralRemainder, collateralProtocolPercent, PERCENT);
        } else {
            // unprofitable liquidation
            liquidatorProfitCollateralToken = assignedCollateral;
        }

        state.data.borrowAToken.transferFrom(msg.sender, address(this), debtPosition.futureValue);
        state.data.collateralToken.transferFrom(debtPosition.borrower, msg.sender, liquidatorProfitCollateralToken);
        state.data.collateralToken.transferFrom(
            debtPosition.borrower, state.feeConfig.feeRecipient, protocolProfitCollateralToken
        );

        debtPosition.liquidityIndexAtRepayment = state.data.borrowAToken.liquidityIndex();
        state.repayDebt(params.debtPositionId, debtPosition.futureValue);
    }
```

## Step

### executeLiquidate

#### Function Declaration

```solidity
function executeLiquidate(State storage state, LiquidateParams calldata params)
    external
    returns (uint256 liquidatorProfitCollateralToken)

```

`State storage state`: Reference to the contract's state.

`LiquidateParams calldata params`: Parameters needed for liquidation.

`external`: Indicates that this function can be called from outside the contract.

`returns (uint256 liquidatorProfitCollateralToken)`: Returns the profit in collateral tokens to the liquidator.



#### Function Body

##### 1. Retrieve Debt Position and Loan Status

```solidity
DebtPosition storage debtPosition = state.getDebtPosition(params.debtPositionId);
LoanStatus loanStatus = state.getLoanStatus(params.debtPositionId);
uint256 collateralRatio = state.collateralRatio(debtPosition.borrower);

```

- Retrieves the debt position and loan status for the given debt position ID.

- Calculates the collateral ratio for the borrower.

##### 2. Emit Liquidate Event

```solidity
Eemit Liquidate Event
```

Emits an event for the liquidation process with relevant details.

##### 3. Determine Protocol Fee Percentage

```solidity
uint256 collateralProtocolPercent = state.isUserUnderwater(debtPosition.borrower)
    ? state.feeConfig.collateralProtocolPercent
    : state.feeConfig.overdueCollateralProtocolPercent;
```

Checks if the user is underwater (collateral value less than debt value) and sets the protocol fee percentage accordingly.

A collateral is underwater if its collateral ratio is less than 1%.

If yes, the percent is `state.feeConfig.collateralProtocolPercent`

If no, it is `overdueCollateralProtocolPercent`

##### 4. Calculate Collateral and Debt Values

```solidity
uint256 assignedCollateral = state.getDebtPositionAssignedCollateral(debtPosition);
uint256 debtInCollateralToken = state.debtTokenAmountToCollateralTokenAmount(debtPosition.futureValue);
uint256 protocolProfitCollateralToken = 0;
```

Gets the assigned collateral and converts the debt value to collateral token value.

##### 5. Profitable Liquidation Handling

```solidity
if (assignedCollateral > debtInCollateralToken) {
    uint256 liquidatorReward = Math.min(
        assignedCollateral - debtInCollateralToken,
        Math.mulDivUp(debtPosition.futureValue, state.feeConfig.liquidationRewardPercent, PERCENT)
    );
    liquidatorProfitCollateralToken = debtInCollateralToken + liquidatorReward;

    uint256 collateralRemainder = assignedCollateral - liquidatorProfitCollateralToken;
    uint256 collateralRemainderCap =
        Math.mulDivDown(debtInCollateralToken, state.riskConfig.crLiquidation, PERCENT);
    collateralRemainder = Math.min(collateralRemainder, collateralRemainderCap);

    protocolProfitCollateralToken = Math.mulDivDown(collateralRemainder, collateralProtocolPercent, PERCENT);
} else {
    liquidatorProfitCollateralToken = assignedCollateral;
}
```

If the collateral is greater than the debt:

- Calculates the liquidator's reward.
- Calculates the profit for the liquidator.
- Determines the remaining collateral and caps it according to the liquidation collateral ratio.
- Calculates the protocol's profit from the remaining collateral.

If not, the liquidator takes all the assigned collateral.

##### Token Transfers

```solidity
state.data.borrowAToken.transferFrom(msg.sender, address(this), debtPosition.futureValue);
state.data.collateralToken.transferFrom(debtPosition.borrower, msg.sender, liquidatorProfitCollateralToken);
state.data.collateralToken.transferFrom(
    debtPosition.borrower, state.feeConfig.feeRecipient, protocolProfitCollateralToken
);
```

- Transfers the debt amount in borrow tokens from the liquidator to the contract.
- Transfers the collateral profit to the liquidator and the protocol’s profit to the fee recipient.



#### Update Debt Position and Repay Debt

```
debtPosition.liquidityIndexAtRepayment = state.data.borrowAToken.liquidityIndex();
state.repayDebt(params.debtPositionId, debtPosition.futureValue);
```

- Updates the liquidity index at repayment.

- Repays the debt associated with the debt position ID.

#### Summary

This function handles the liquidation process by:

- Retrieving the necessary data about the debt position.
- Emitting a liquidation event.
- Calculating the collateral and debt values.
- Determining the liquidator's profit and the protocol's profit.
- Executing token transfers for the liquidated amount and profits.
- Updating the debt position and repaying the debt.

## Reference

- ChatGPT with the input "Explain me this function from a lending protofol (defi). Explains each step". 
- [code4rena.com/audits/2024-06-size](https://code4rena.com/audits/2024-06-size)
- [docs.size.cash/](https://docs.size.cash/)