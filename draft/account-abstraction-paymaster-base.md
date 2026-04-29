---
layout: post
title: "Account abstraction - ETH infinitism - Base Paymaster"
date:   2025-12-13
locale: en-GB
lang: en
last-update: 
categories: blockchain solidity
tags: solidity ethereum smart-contract openzeppelin
description: This article is an overview of the OpenZeppelin ERC-4337 Account contract. The content is mainly based on the OpenZeppelin documentation.
isMath: false
image: /assets/article/blockchain/ethereum/erc-4337/erc4337-openzeppelin-account-mindmap.png
---



# 

[https://github.com/eth-infinitism/account-abstraction/tree/1c6b669d0eea734e09a87e095ba15e076151718a](https://github.com/eth-infinitism/account-abstraction/tree/1c6b669d0eea734e09a87e095ba15e076151718a)

This article is an overview of the OpenZeppelin [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337) Account contract. 



ERC-4337 is a standard for account abstraction in Ethereum. It introduces new concepts like EntryPoint contracts, Paymasters, and Bundlers to enable a more flexible and user-friendly transaction experience.

For more information on ERC-4337, please refer to the [official EIP](https://eips.ethereum.org/EIPS/eip-4337).

## Introduction

Helper class for creating a paymaster

### Use

```solidity
import "@account-abstraction/contracts/core/BasePaymaster.sol";

contract MyCustomPaymaster is BasePaymaster {
    /// implement your gas payment logic here
    function _validatePaymasterUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 maxCost
    ) internal virtual override returns (bytes memory context, uint256 validationData) {
        context = “”; // specify “context” if needed in postOp call. 
        validationData = _packValidationData(
            false,
            validUntil,
            validAfter
        );
    }
}
```

Example to use the paymaster

From Example to use the paymaster



This is a simple ERC-4337 account implementation that provides only the minimal logic required to process user operations.

Developers are expected to implement the `AbstractSigner._rawSignatureValidation` function themselves in order to define how the account validates signatures.

The core account does not include any mechanism for executing arbitrary external calls, even though this is an essential feature for most accounts; instead, developers are free to choose and implement their preferred approach, such as [ERC-6900](https://eips.ethereum.org/EIPS/eip-6900), [ERC-7579](https://eips.ethereum.org/EIPS/eip-7579), or [ERC-7821](https://eips.ethereum.org/EIPS/eip-7821).

Implementing signature validation is a security-critical task, as mistakes could allow attackers to bypass the account’s protections, so developers are encouraged to refer to existing implementations like `SignerECDSA`, `SignerP256`, or `SignerRSA` for guidance. The account is designed to be stateless.

```
import "@openzeppelin/contracts/account/Account.sol";
```

For a deep dive into ERC-4437, see my article [ERC-4337: Account Abstraction Using Alt Mempool](https://rya-sge.github.io/access-denied/2025/05/02/erc-4337-overview/)

## Schema

### UML

![basePaymasterUML](/home/ryan/Downloads/me/access-denied/assets/article/blockchain/ethereum/erc-4337/base-paymaster/basePaymasterUML.png)

### Graph

![surya_graph_BasePaymaster.sol.png](file:///home/ryan/Downloads/me/access-denied/assets/article/blockchain/ethereum/erc-4337/base-paymaster/surya_graph_BasePaymaster.sol.png)





## Sūrya's Description Report

### Files Description Table


| File Name                | SHA-1 Hash                               |
| ------------------------ | ---------------------------------------- |
| ./core/BasePaymaster.sol | 11d9b5e0b2214b380b7ecc4ee13072931a97a7c0 |


### Contracts Description Table


|     Contract      |             Type             |         Bases         |                |               |
| :---------------: | :--------------------------: | :-------------------: | :------------: | :-----------: |
|         └         |      **Function Name**       |    **Visibility**     | **Mutability** | **Modifiers** |
|                   |                              |                       |                |               |
| **BasePaymaster** |        Implementation        | IPaymaster, Stakeable |                |               |
|         └         |        <Constructor>         |       Public ❗️        |       🛑        |    Ownable    |
|         └         |          entryPoint          |       Public ❗️        |                |      NO❗️      |
|         └         | _validateEntryPointInterface |      Internal 🔒       |       🛑        |               |
|         └         |   validatePaymasterUserOp    |      External ❗️       |       🛑        |      NO❗️      |
|         └         |   _validatePaymasterUserOp   |      Internal 🔒       |       🛑        |               |
|         └         |            postOp            |      External ❗️       |       🛑        |      NO❗️      |
|         └         |           _postOp            |      Internal 🔒       |       🛑        |               |
|         └         |           deposit            |       Public ❗️        |       💵        |      NO❗️      |
|         └         |          withdrawTo          |       Public ❗️        |       🛑        |   onlyOwner   |
|         └         |          getDeposit          |       Public ❗️        |                |      NO❗️      |
|         └         |    _requireFromEntryPoint    |      Internal 🔒       |       🛑        |               |


### Legend

| Symbol | Meaning                   |
| :----: | ------------------------- |
|   🛑    | Function can modify state |
|   💵    | Function is payable       |















