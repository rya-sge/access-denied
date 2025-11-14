# Morpho - Market

## What is a Morpho Market (V1)?

A Morpho Market V1 is a primitive lending pool that pairs one collateral asset with one loan asset. Each market is isolated (meaning risks are contained within each individual market), immutable (cannot be changed after deployment), and will persist as long as the blockchain it deployed on is live. This design ensures predictable behavior and eliminates systematic for lenders and borrowers. Creating a Morpho Market is **permissionless**.

## Key Features

- **Simple Structure**: One collateral asset, one loan asset per market
- **Permanent Parameters**: Once created, rules never change
- **Isolated Risk**: Each market operates independently
- **Permission-less**: New market doesn’t require governance vote to be created - more [here](https://docs.morpho.org/learn/concepts/market#permissionless-market-creation)
- **Transparent Rules**: Clear conditions for lending and borrowing

## Market Identification

Markets follow this naming format:

```
CollateralAsset/LoanAsset (LLTV%, OracleAddress, IRMAddress)
```

For example: `wstETH/WETH (94.5%, ChainlinkOracleV2-wstETHToWETH, AdaptiveCurveIRM)`

## The Five Parameters

1. **Collateral Asset** that should be [ERC20 compliant](https://docs.openzeppelin.com/contracts/4.x/erc20) (except that it can omit return values on `transfer` and `transferFrom`.)
2. **Loan Asset** sharing same properties as collateral asset. However, the Loan asset should not be [ERC4626 compliant](https://docs.openzeppelin.com/contracts/4.x/erc4626).
3. **LLTV (Liquidation Loan-To-Value)**: Maximum borrowing percentage before liquidation risk. E.g: LLTV of 80% means for a collateral value equivalent of $100, the maximum one can borrow in value is $80. If above like $80.0001, the position is liquidatable.
4. **Oracle**: Smart contract address pricing the collateral against the loan asset.
5. **IRM (Interest Rate Model)**: Smart contract address containing the formula for determining interest rate paid by borrowers.

## Governance-Approved LLTV & IRM

### LLTVs

| LLTV (%) | Solidity Values (scaled by 1e18) |
| :------- | :------------------------------- |
| 0        | 0                                |
| 38.5     | 385000000000000000               |
| 62.5     | 625000000000000000               |
| 77.0     | 770000000000000000               |
| 86.0     | 860000000000000000               |
| 91.5     | 915000000000000000               |
| 94.5     | 945000000000000000               |
| 96.5     | 965000000000000000               |
| 98.0     | 980000000000000000               |

### IRM

The only Interest Rate Model (IRM) that has been governance-approved is the [AdaptiveCurveIRM](https://docs.morpho.org/learn/concepts/irm).

## Market ID Generator

Use this tool to generate a unique market ID from your market parameters:

Loan Token Address

Collateral Token Address

Oracle Address

IRM Address

LLTV (in wei, e.g., 915000000000000000 for 91.5%)

Reset

Generated Market ID

`0xbc15a1782163f4be46c23ac61f5da50fed96ad40293f86a5ce0501ce4a246b32`Copy

## Permissionless market creation

A distinctive feature of Morpho is permissionless market creation: the protocol allows users to create isolated markets consisting of the five aforementioned parameters.

This a departure from the existing paradigm and traditional lending platforms which:

1. Require governance approval for asset listing and parameter changes.
2. Pool assets into a single lending pool, sharing risk across the entire protocol.

In Morpho, each parameter is selected at market creation and persists in perpetuity. Or, in other words, are immutable. The LLTV and interest rate model must be chosen from a set of options approved by Morpho Governance.

## Core Interactions

- **Supply**: Lenders deposit loan assets into a specific market to earn interest.
- **Borrow**: Borrowers supply collateral to the same market and borrow loan assets against it, up to the LLTV limit.
- **Withdraw**: Lenders can withdraw their supplied assets and accrued interest, provided there is enough liquidity in the market.
- **Repay**: Borrowers can repay their loan to reclaim their collateral.
- **Liquidate**: If a borrower's position exceeds the LLTV, anyone can liquidate it by repaying a portion of the debt in exchange for a discounted portion of the collateral.