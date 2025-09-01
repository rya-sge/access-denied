# Aave V3 - Market operations

## Aave V3 Market Operations: A Developer’s Guide

### 1. Overview

Aave V3 offers a comprehensive set of **market operations**, enabling developers to integrate core lending features like **supply, borrow, repay, and withdraw into their applications. 

These operations are available via Aave’s React/TypeScript SDKs and GraphQL API, providing composable and secure access to liquidity markets across multiple blockchain networks.

### 2. Permit Functionality (EIP-2612)

Aave supports an optional **permit** workflow, leveraging EIP-2612 signatures to authorize ERC-20 transfers within a single transaction. This streamlines operations by:

- Removing the need for separate approval transactions
- Allowing authorization of specific amounts (not unlimited allowances)
- Enabling time-limited permissions for enhanced security

### 3. Supply Assets

Developers can enable users to:

- **Supply** ERC-20 or native assets to Aave markets
- Receive **aTokens**, which accrue interest over time
- Use options like:
  - **Direct Supply**
  - **On Behalf Of Another**
  - **With Permit** workflows

### 4. Borrow Assets

On supplying assets, users can borrow by leveraging over-collateralized positions. 

Borrowed balances are tracked via **variableDebtTokens**, and risk is managed through:

- **Health Factor** calculations
- **Liquidation thresholds**
- On-chain **oracle** price feeds

### 5. Repay & Withdraw

- **Repay Loans**: Users can pay down their borrowed assets at any time.
- **Withdraw Assets**: Users can redeem underlying assets by burning aTokens, depending on available liquidity and collateralization conditions.

### 6. Advanced Operations: Health Factor Preview

The documentation references advanced operations like **Health Factor Preview**, which enables developers to simulate how a user's health factor might change before executing an action, aiding risk-aware UI flows.

------

### Practical Developer Workflow

Typical flow when integrating a supply (for example):

1. **Identify the reserve** (e.g., WETH)
2. **Prepare the execution plan** (choosing direct or permit-based methods)
3. **Execute** the transaction via the frontend SDK (React/TypeScript) or GraphQL endpoint
4. **Handle post-execution** (e.g., confirm receipt of aTokens)

This flow can be adapted for borrowing, repaying, or withdrawing, following analogous steps—identify target reserves, set up execution plans, and process via SDKs or APIs.[aave.com](https://aave.com/docs/developers/aave-v3/markets/operations?utm_source=chatgpt.com)

------

### Summary Table

| Operation             | Key Actions & Mechanism                                      |
| --------------------- | ------------------------------------------------------------ |
| Permit                | Authorization via EIP-2612 in a single transaction           |
| Supply Assets         | Deposit assets → receive interest-bearing aTokens            |
| Borrow Assets         | Use collateral → borrow → managed by Health Factor & oracles |
| Repay / Withdraw      | Close or reduce positions; withdraw underlying by burning tokens |
| Health Factor Preview | Simulate risk changes before transactions                    |



------