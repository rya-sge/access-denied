---
layout: post
title: Programming contract proxies with OpenZeppelin | Summary
date: 2022-10-31
locale: en-GB
lang: en
last-update: 
categories: blockchain
tags: solidity ethereum smart-contract OpenZeppelin
description: Summary of the most important points to think and check to program proxy contracts on Ethereum, with a focus on the OpenZeppelin library.
isMath: false
image: 
---



## Introduction

This article is a summary of the most important points to think and check to program proxy contracts on Ethereum, with a focus on the OpenZeppelin library. The proxy contracts are complex architectures and need special attention to avoid security risks. For each topics, you can find more information by reading the provided links.

To understand the importance to perform your own security check, we can take the example of the platform Audius, which was hacked for $6 millions due to a vulnerability in their proxy contract [[SharkTeam 2022](https://www.sharkteam.org/report/analysis/20220726001A_en.pdf)], [[Reutov 2022](https://offzone.moscow/getfile/?bmFtZT1BLlJldXRvdl9VcGdyYWRlYWJsZSBzbWFydCBjb250cmFjdHMgc2VjdXJpdHkucGRmJklEPTIzODM=)], [[Toulas 2022](https://www.bleepingcomputer.com/news/security/hackers-steal-6-million-from-blockchain-music-platform-audius/)] or on Wormhole, who offered a bug bounty record of 10 million for a bug affecting their proxy contract [[Immunefi 2022](https://medium.com/immunefi/wormhole-uninitialized-proxy-bugfix-review-90250c41a43a)].


## General points

### Storage collision

In principle, the storage collision is managed by OpenZeppelin. 

Reference: [[OpenZeppelin 2022d](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#unstructured-storage-proxies)]

See: [eip-1967](https://eips.ethereum.org/EIPS/eip-1967 )  [Santiago Palladino 2019]

### Exception & Warning

There are  nevertheless some situations where you must be careful with the storage. 

**New version of your contract**

If you want to write a new version of your contract, you have some limitation.

> You cannot change the order in which the contract state variables are declared, nor their type.

Reference: [[OpenZeppelin 2022h](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#modifying-your-contracts)]

### Constructor / initializer

A constructor is not allowed, except for a few exceptions.

Reference : [[OpenZeppelin 2022c](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#the-constructor-caveat)], [[OpenZeppelin 2022g](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializers)]

* Exception

There exists an exception for immutable variables. With them, you can decide to initialize them only in the constructor. OpenZeppelin, for the upgradeable implementation of ERC2771 by OpenZeppelin, choose to set the forwarder in the constructor

* File: [ERC2771ContextMockUpgradeable.sol ](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/master/contracts/mocks/ERC2771ContextMockUpgradeable.sol) [OpenZeppelin 2022j]

* Issue: [issues/175](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/issues/175 ) , [issues/156](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/issues/156 ), [issues/154](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/issues/154 ) 

### Initializer / OnlyInitializing

- `initializer` is used for public-facing functions ;

- `onlyInitializing` is used for internal functions.

Reference: [[frangio 2022](https://forum.openzeppelin.com/t/whats-the-difference-between-onlyinitializing-and-initialzer/25789)], [[OpenZeppelin 2022g](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializers)]

## To avoid

### Avoiding Initial Values

Use the function `initialize` to initialize variable.

```javascript
contract MyContract is Initializable {
    uint256 public hasInitialValue;

function initialize() public initializer {
    hasInitialValue = 42; // set initial value in initializer
}

}
```

**Exception**  

With OpenZeppelin Upgradeable, it is possible to initialize value with the constant keyword

`uint256 public constant hasInitialValue = 42;`

Reference: [[OpenZeppelin 2022f](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#avoid-initial-values-in-field-declarations)]

### Avoid leaving a contract uninitialized

> An uninitialized contract can be taken over by an attacker. This applies to both a proxy and its implementation contract, which may impact the proxy. To prevent the implementation contract from being used, you should invoke the {_disableInitializers} function in the constructor to automatically lock it when it is deployed

Reference : [[OpenZeppelin 2022n](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/master/contracts/proxy/utils/Initializable.sol)], [[OpenZeppelin 2022o](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializing_the_implementation_contract )]



## Potentially Unsafe Operations

[[OpenZeppelin 2022i](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#potentially-unsafe-operations)]

### Delegatecall

> This is an advanced technique and can put funds at risk of permanent loss.

> If the contract can be made to delegatecall into a malicious contract that contains a selfdestruct, then the calling contract will be destroyed.

Reference: [[OpenZeppelin 2022a](https://docs.openzeppelin.com/upgrades-plugins/1.x/faq#delegatecall-selfdestruct)], [[OpenZeppelin 2022i](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#potentially-unsafe-operations)]

### Modifying Your Contracts

> You cannot change the order in which the contract state variables are declared, nor their type.

Reference: [[OpenZeppelin 2022h](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#modifying-your-contracts)]

### Selfdestruct

> This is an advanced technique and can put funds at risk of permanent loss.
Principle
> If you want implement selfdestruct, it is very important that this functionality can only be triggered through proxies and not on the implementation contract itself.
Details
> If the direct call to the logic contract triggers a selfdestruct operation, then the logic contract will be destroyed, and all your contract instances will end up delegating all calls to an address without any code. This would effectively break all contract instances in your project.

Reference: [[OpenZeppelin 2022a](https://docs.openzeppelin.com/upgrades-plugins/1.x/faq#delegatecall-selfdestruct)], [[OpenZeppelin 2022i](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#potentially-unsafe-operations )]



## Test 

It is important to perform test on your proxy architecture. For this, you can use the Upgrades Plugins. See the documentation here : [[OpenZeppelin 2022m](https://docs.openzeppelin.com/upgrades-plugins/1.x/ )]

Documentation for truffle

- [[OpenZeppelin 2022k](https://docs.openzeppelin.com/upgrades-plugins/1.x/api-truffle-upgrades)]

- [[Truffle Suite 2022](https://trufflesuite.com/blog/a-sweet-upgradeable-contract-experience-with-openzeppelin-and-truffle/)]

Documentation for Hardhat

- [[OpenZeppelin 2022b](https://docs.openzeppelin.com/upgrades-plugins/1.x/api-hardhat-upgrades)]
- [[OpenZeppelin 2022l](https://www.npmjs.com/package/@openzeppelin/hardhat-upgrades)]


## Deployment

> To help ensure secure contract upgrades, it is recommended to deploy using the OpenZeppelin Upgrades plugin (available for Hardhat or Truffle), which validates that the contract adheres to the necessary rules for upgradeability and that the storage layout is correctly preserved.

Reference: [[WEBBER 2022](https://blog.openzeppelin.com/staying-safe-with-smart-contract-upgrades/)]



## Reference

FRANGIO, 2022. What’s the difference between onlyInitializing and initialzer? Online. 9 March 2022. [Accessed 30 October 2022]. Retrieved from: [https://forum.openzeppelin.com/t/whats-the-difference-between-onlyinitializing-and-initialzer/25789/2](https://forum.openzeppelin.com/t/whats-the-difference-between-onlyinitializing-and-initialzer/25789/2)

IMMUNEFI, 2022. Wormhole Uninitialized Proxy Bugfix Review. *Immunefi*. Online. 20 May 2022. [Accessed 31 October 2022]. Retrieved from: [https://medium.com/immunefi/wormhole-uninitialized-proxy-bugfix-review-90250c41a43a](https://medium.com/immunefi/wormhole-uninitialized-proxy-bugfix-review-90250c41a43a)

OPENZEPPELIN, 2022a. FAQ - Can I safely use delegatecall and selfdestruct? *OpenZeppelin \| docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/faq#delegatecall-selfdestruct](https://docs.openzeppelin.com/upgrades-plugins/1.x/faq#delegatecall-selfdestruct)

OPENZEPPELIN, 2022b. OpenZeppelin Hardhat Upgrades API. *OpenZeppelin \| docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/api-hardhat-upgrades](https://docs.openzeppelin.com/upgrades-plugins/1.x/api-hardhat-upgrades)

OPENZEPPELIN, 2022c. Proxy Upgrade Pattern - The Constructor Caveat. *OpenZeppelin | docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#the-constructor-caveat](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#the-constructor-caveat)

OPENZEPPELIN, 2022d. Proxy Upgrade Pattern - Unstructured Storage Proxies. *OpenZeppelin | docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#unstructured-storage-proxies](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#unstructured-storage-proxies)

OPENZEPPELIN, 2022e. Upgrades Plugins - Test usage. *OpenZeppelin | docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/#test-usage](https://docs.openzeppelin.com/upgrades-plugins/1.x/#test-usage)

OPENZEPPELIN, 2022f. Writing Upgradeable Contracts - Avoiding Initial Values in Field Declarations. *OpenZeppelin | docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#avoid-initial-values-in-field-declarations](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#avoid-initial-values-in-field-declarations)

OPENZEPPELIN, 2022g. Writing Upgradeable Contracts - Initializers. *OpenZeppelin | docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializers](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializers)

OPENZEPPELIN, 2022h. Writing Upgradeable Contracts - Modifying Your Contracts. *OpenZeppelin | docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#modifying-your-contracts](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#modifying-your-contracts)

OPENZEPPELIN, 2022i. Writing Upgradeable Contracts - Potentially Unsafe Operations. *OpenZeppelin | docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#potentially-unsafe-operations](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#potentially-unsafe-operations)

OPENZEPPELIN, 2022j. ERC2771ContextMockUpgradeable.sol. *GitHub - OpenZeppelin*. Online. 14 September 2022. [Accessed 29 October 2022]. Retrieved from: [https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/b551d19e6e37deaa15d8c3ca7beec713031d83fd/contracts/mocks/ERC2771ContextMockUpgradeable.sol](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/b551d19e6e37deaa15d8c3ca7beec713031d83fd/contracts/mocks/ERC2771ContextMockUpgradeable.sol)

OPENZEPPELIN, 2022k. OpenZeppelin Truffle Upgrades API. *OpenZeppelin | docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/api-truffle-upgrades](https://docs.openzeppelin.com/upgrades-plugins/1.x/api-truffle-upgrades)

OPENZEPPELIN, 2022l. *@openzeppelin/hardhat-upgrades*. Online. version 1.21.0. September 2022. OpenZeppelin. Retrieved from: [https://www.npmjs.com/package/@openzeppelin/hardhat-upgrades](https://www.npmjs.com/package/@openzeppelin/hardhat-upgrades)

OPENZEPPELIN, 2022m. Upgrades Plugins. *OpenZeppelin | docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/](https://docs.openzeppelin.com/upgrades-plugins/1.x/)

OPENZEPPELIN, 2022n. *Initializable.sol*. Online. version v4.7.3. 14 September 2022. OpenZeppelin. [Accessed 29 October 2022]. Retrieved from: [https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/master/contracts/proxy/utils/Initializable.sol](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/master/contracts/proxy/utils/Initializable.sol)

OPENZEPPELIN, 2022o. Writing Upgradeable Contracts - Initializing the Implementation Contract. *OpenZeppelin | docs*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializing_the_implementation_contract](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializing_the_implementation_contract)

REUTOV, Arseniy, 2022. *Upgradable Contract Vulnerability—Analysis on the Hack of Web3 Music PlatformAudius*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://offzone.moscow/getfile/?bmFtZT1BLlJldXRvdl9VcGdyYWRlYWJsZSBzbWFydCBjb250cmFjdHMgc2VjdXJpdHkucGRmJklEPTIzODM=](https://offzone.moscow/getfile/?bmFtZT1BLlJldXRvdl9VcGdyYWRlYWJsZSBzbWFydCBjb250cmFjdHMgc2VjdXJpdHkucGRmJklEPTIzODM=)

[Santiago Palladino](https://github.com/spalladino), [Francisco Giordano](https://github.com/frangio), [Hadrien Croubois](https://github.com/Amxx), "EIP-1967: Proxy Storage Slots," *Ethereum Improvement Proposals*, no. 1967, April 2019. [Online serial]. Available: [https://eips.ethereum.org/EIPS/eip-1967.](https://eips.ethereum.org/EIPS/eip-1967.)

SHARKTEAM, 2022. *Upgradable Contract Vulnerability—Analysis on the Hack of Web3 Music PlatformAudius*. Online. 26 July 2022. [Accessed 29 October 2022]. Retrieved from: [https://www.sharkteam.org/report/analysis/20220726001A_en.pdf](https://www.sharkteam.org/report/analysis/20220726001A_en.pdf)

TOULAS, Bill, 2022. Hackers steal $6 million from blockchain music platform Audius. *BleepingComputer*. Online. 2022. [Accessed 29 October 2022]. Retrieved from: [https://www.bleepingcomputer.com/news/security/hackers-steal-6-million-from-blockchain-music-platform-audius/](https://www.bleepingcomputer.com/news/security/hackers-steal-6-million-from-blockchain-music-platform-audius/)

TRUFFLE SUITE, 2022. A Sweet Upgradeable Contract Experience with OpenZeppelin and Truffle. *Truffle Suite*. Online. 2022. [Accessed 30 October 2022]. Retrieved from: [https://trufflesuite.com/blog/a-sweet-upgradeable-contract-experience-with-openzeppelin-and-truffle/](https://trufflesuite.com/blog/a-sweet-upgradeable-contract-experience-with-openzeppelin-and-truffle/)

WEBBER, STEPHEN, 2022. Staying Safe with Smart Contract Upgrades. *OpenZeppelin | news & events*. Online. 16 August 2022. [Accessed 30 October 2022]. Retrieved from: [https://blog.openzeppelin.com/staying-safe-with-smart-contract-upgrades/](https://blog.openzeppelin.com/staying-safe-with-smart-contract-upgrades/)