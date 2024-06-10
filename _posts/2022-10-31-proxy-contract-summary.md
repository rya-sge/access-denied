---
layout: post
title: Programming contract proxies with OpenZeppelin | Summary
date: 2022-10-31
locale: en-GB
lang: en
last-update: 
categories: blockchain ethereum solidity
tags: solidity ethereum smart-contract OpenZeppelin
description: Summary of the most important points to think and check to program proxy contracts on Ethereum, with a focus on the OpenZeppelin library.
isMath: true
image: /assets/article/blockchain/ethereum/proxy_schema-proxy_base.drawio.png
---

## Introduction

[TOC]

Proxy contracts  are an architecture widely used within the Ethereum ecosystem. Basically, in this architecture, there are two main contracts:

- The proxy contract, which stores the memory and delegate its calls to another contract called logic or implementation contracts
- This second contract contains all the smart contract logic. 

The proxy will delegate the calls from the sender to the implementation.

![proxy]({{site.url_complet}}/assets/article/blockchain/ethereum/proxy_schema-proxy_base.drawio.png)

Proxy contracts can generally be upgraded to a new implementation.

![proxy]({{site.url_complet}}/assets/article/blockchain/ethereum/ethereum-proxy-schema-proxy_upgrade.drawio.png)

For example, the implementation of an ERC-20 proxy will contain all the logic to perform a transfer while the balance of each address is stored in the proxy memory.

To change the behavior of the proxy contract, the proxy admin can deploy a new logic contract and points the proxy to this new one.

But this kind of architecture is not easy to implement, and it is the origin of several bugs:

- The platform Audius, which was hacked in 2022 for $6 million due to a vulnerability in their proxy contract (storage conflict).  Reference: [[SharkTeam 2022](https://www.sharkteam.org/report/analysis/20220726001A_en.pdf)], [[Reutov 2022](https://offzone.moscow/getfile/?bmFtZT1BLlJldXRvdl9VcGdyYWRlYWJsZSBzbWFydCBjb250cmFjdHMgc2VjdXJpdHkucGRmJklEPTIzODM=)], [[Toulas 2022](https://www.bleepingcomputer.com/news/security/hackers-steal-6-million-from-blockchain-music-platform-audius/)].
- Wormhole, who offered a bug bounty record of $10 million for a bug affecting their proxy contract (Uninitialized Proxy), also in 2022. Reference: [[Immunefi 2022](https://medium.com/immunefi/wormhole-uninitialized-proxy-bugfix-review-90250c41a43a)].

The majority of bug related to proxy concerns:

- Storage collision between the proxy and the implementation contract
- Storage collision between an implementation and the new one when performing an upgrade
- Uninitialized implementation but the severity of this has reduced with the EIP-6780 (deactivate selfdestruct) 

[OpenZeppelin](https://www.openzeppelin.com) did a fantastic job of offering proper tools to manage and create proxy contracts.

If you want to use a proxy architecture,  this article is a summary of the most important points to think about and check to build proxy contracts on Ethereum/EVM, with a focus on the OpenZeppelin library. For each topic, you can find more information by reading the provided links.

The [Solidity interviews Questions](https://www.rareskills.io/post/solidity-interview-questions) by RareSkills contains also several questions related to proxy architecture. You can find my answers for them in two article:  [Medium](https://rya-sge.github.io/access-denied/2024/02/14/solidity-interview-question-rareskills/) and [Hard levels](https://rya-sge.github.io/access-denied/2024/03/04/solidity-interview-question-rareskills-hard/#proxy)




## General points

### Storage collision

A storage collision can appear in two situations:

a) **Proxy and the implementation contract**

Storage collision between the proxy and the implementation contract

A storage collision happens when a proxy and its implementation use the same slot to store a value. As a result, when the implementation contract writes to update its variable, it will overwrite in reality the variable used by the proxy.

A solution, used by OpenZeppelin, is to “randomize” slot positions in the proxy’s storage

Reference: [[d. OpenZeppelin - Unstructured Storage Proxies](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#unstructured-storage-proxies)]

b) **Two implementations**

Storage collision between two implementations

This collision happens when a proxy is upgraded to point to a new implementation

In this case, the new implementation overwrites a variable from the previous implementation.

It is very important to keep in mind that you cannot change the order in which the contract state variables are declared, nor their type.

A first solution put in place by OpenZeppelin was to use a state variable named `__gap`. This is empty reserved space allows to freely add new state variables in the future without compromising the storage compatibility with existing deployments. See [OpenZeppelin doc - storage gaps](https://docs.openzeppelin.com/contracts/4.x/upgradeable#storage_gaps).

Since their version v5.0.0, OpenZeppelin proposed and uses the [ERC-7201 -  Namespaced Storage Layout](https://eips.ethereum.org/EIPS/eip-7201). In short, in this case, the storage of each variable is computed with the following formula:
$$
keccak256(id) - 1
$$
Example from the ERC:
$$
keccak256(abi.encode(uint256(keccak256("example.main")) - 1))\;\& ~bytes32(uint256(0xff));
$$


```solidity
bytes32 private constant MAIN_STORAGE_LOCATION =
 0x183a6125c38840424c4a85fa12bab2ab606c4b6d0e7cc73c0c06ba5300eab500;
```



Reference: [[h. OpenZeppelin - Modifying your contracts](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#modifying-your-contracts)], [p. OpenZeppelin - Storage Collisions Between Implementation Versions](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#storage-collisions-between-implementation-versions), [eip-1967](https://eips.ethereum.org/EIPS/eip-1967 ), [Introducing OpenZeppelin Contracts 5.0](https://blog.openzeppelin.com/introducing-openzeppelin-contracts-5.0#Namespaced)



### Constructor / initializer

In principle, you can not have a constructor in your implementation contract

If variables are initialized inside the constructor, the proxy has no way to see these values since :

- The constructor is not stored in the runtime bytecode, but only in the creation bytecode.
- The implementation contract is not deployed in the context of the proxy.

The solution is to use a public `initialize` function to initialize the proxy with the different values for each variable.

One exception to this is for **immutable** variables. Since this value is  stored in the contract bytecode instead of the contract storage, you can use and initialize an immutable inside the constructor of the  implementation contract.

For example, OpenZeppelin, for the upgradeable implementation of ERC2771 by OpenZeppelin, choose to set the forwarder in the constructor

* File: [ERC2771ContextMockUpgradeable.sol ](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/master/contracts/mocks/ERC2771ContextMockUpgradeable.sol) [OpenZeppelin 2022j]

* Issue: [issues/175](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/issues/175 ) , [issues/156](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/issues/156 ), [issues/154](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/issues/154 ) 

Reference : [c. OpenZeppelin - proxies#the constructor caveat](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#the-constructor-caveat), [g. OpenZeppelin - initializers](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializers)

### Initializer / OnlyInitializing

**initializer**

Since proxied contracts do not make use of a constructor, it’s common to move constructor logic to an external initializer function, usually called `initialize`. It then becomes necessary to protect this initializer function so it can only be called once. The [`initializer`](https://docs.openzeppelin.com/contracts/4.x/api/proxy#Initializable-initializer--) modifier provided by this contract will have this effect.

**onlyInitializing**

Modifier to protect an initialization function so that it can only be invoked by functions with the [`initializer`](https://docs.openzeppelin.com/contracts/4.x/api/proxy#Initializable-initializer--) and [`reinitializer`](https://docs.openzeppelin.com/contracts/4.x/api/proxy#Initializable-reinitializer-uint8-) modifiers, directly or indirectly.

**In short**

- `initializer` is used for public-facing functions ;

- `onlyInitializing` is used for internal functions.

Reference: [frangio 2022](https://forum.openzeppelin.com/t/whats-the-difference-between-onlyinitializing-and-initialzer/25789), [g. OpenZeppelin - initializers](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializers)

## To avoid

### Avoiding Initial Values

Variables must be initialized inside the function `initialize`.

```javascript
contract MyContract is Initializable {
    uint256 public hasInitialValue;

function initialize() public initializer {
    hasInitialValue = 42; // set initial value in initializer
}

}
```

**Exception**  

It is possible to initialize value with the constant keyword

`uint256 public constant hasInitialValue = 42;`

Reference: [[f. OpenZeppelin - Avoid initial values in field declarations](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#avoid-initial-values-in-field-declarations)]

### Avoid leaving a contract uninitialized

As seen in the section "Initializer / OnlyInitializing", a proxy contract calls a specific function from the implementation contract to initialize its variables.

But what happens if this function is called on the implementation contract directly by an attacker?

This can be very bad since this function is not protected by default and can be used to take over the implementation contract.

 To prevent the implementation contract from being used, you should invoke the `{_disableInitializers}` function in the constructor to automatically lock it when it is deployed

Reference : [n. OpenZeppelin- Initializable](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/master/contracts/proxy/utils/Initializable.sol), [o. OpenZeppelin - initializing_the_implementation_contract](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializing_the_implementation_contract )

## Potentially Unsafe Operations

The main reference for this section is this article from OpenZeppelin: [[Potentially Unsafe Operations](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#potentially-unsafe-operations)]

### Delegatecall

As indicated in the OpenZeppelin documentation, use a `delegatecall`in your implementation contract is an advanced technique and can put funds at risk of permanent loss.

- For example, before [EIP-6780](https://rya-sge.github.io/access-denied/2024/03/13/EIP-6780-selfdestruct/), if the contract can be made to delegatecall into a malicious contract that contains a selfdestruct, then the calling contract will be destroyed.
- perform a `call`or a `delegatecall`can lead to several vulnerabilities if not properly implemented, as seen for example in the [furucombo](https://cmichel.io/replaying-ethereum-hacks-furucombo/) hack in 2021.

Reference: [[a.OpenZeppelin - delegatecall selfdestruct](https://docs.openzeppelin.com/upgrades-plugins/1.x/faq#delegatecall-selfdestruct)], [[i.OpenZeppelin - potentially unsafe operations](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#potentially-unsafe-operations)]

### Modifying Your Contracts

When you modify your implementation contract to create a new version, you cannot change the order in which the contract state variables are declared, nor their type. 

If you don't respect this, this will lead to a collision between the storage of the previous implementation and the new one.

Reference: [[h.OpenZeppelin - modifying your contracts](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#modifying-your-contracts)]

### Selfdestruct

Since the Dencun Upgrade and the EIP-6780, `selfdestruct`can no longer destruct the contract bytecode.

More information in [my article](https://rya-sge.github.io/access-denied/2024/03/13/EIP-6780-selfdestruct/).

Before this update, if a direct call, without passing through the proxy, to the logic contract triggers a `self destruct`, then the logic contract will be destroyed.

The result is catastrophic since all your contract instances will end up delegating all calls to an address without any code. 

- With a transparent proxy, it was still possible to upgrade to a new implementation
- but with a UUPS proxy, the consequence is much more serious since the logic to upgrade the proxy is coded in the logic contract. Therefore, if the logic contract is destroyed, it is not possible to upgrade the proxy and all the proxy point to the logic contracts are broken forever.

Reference: [[a.OpenZeppelin - delegatecall-selfdestruct](https://docs.openzeppelin.com/upgrades-plugins/1.x/faq#delegatecall-selfdestruct)], [[i.OpenZeppelin - potentially unsafe operations](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#potentially-unsafe-operations )]



## Deployment & Test 

It is important to perform tests on your proxy architecture. For this, you can use the Upgrades Plugins. Plugins are available for [Hardhat](https://docs.openzeppelin.com/upgrades-plugins/1.x/api-hardhat-upgrades), [Foundry](https://docs.openzeppelin.com/upgrades-plugins/1.x/api-foundry-upgrades) and [Truffle](https://docs.openzeppelin.com/upgrades-plugins/1.x/api-truffle-upgrades)

This plugin validates that the contract respects the necessary rules for upgradeability and that the storage layout is correctly preserved.

These plugins are also available to manage deployment and upgrade.

Reference: [[OpenZeppelin - staying safe with smart contract upgrades/](https://blog.openzeppelin.com/staying-safe-with-smart-contract-upgrades/)]

### Standalone

If you want to have the possibility to deploy with a proxy or also in standalone mode (without proxy), you should call the `initialize`function directly in the constructor for the standalone version like this:

```solidity
constructor(<constructor argument>)  {
        initialize(< function argument>);
    }
```

If you do not this, an attacker could front-run you to call the function `initialize` before you.

However, this remains very unlikely.

## Specificity

### UUPS proxy

In a UUPS proxy, the logic to upgrade the proxy is coded in the implementation contract. Thus, it is important that this function is indeed implemented in the implementation and correctly protected by an access control.

With OpenZeppelin, your contract must inherit from the contract `UUPSUpgradeable` and overrides the function `_authorizeUpgrade`.

Here the function is protected by the modifier `onlyOwner`.

```solidity
function _authorizeUpgrade(address) internal onlyOwner {}
```

This function is internal because it is called by the public function [upgradeToAndCall.](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/proxy/utils/UUPSUpgradeable.sol#L86).

### Transparent proxy

In a transparent proxy, since the function to upgrade is in the proxy, not in the implementation, it is better to use a dedicated contract `ProxyAdmin`to manage the proxy. 

- If the admin calls the proxy, it can call the `upgradeToAndCall` function but any other call won’t be forwarded to the implementation. 
- If the admin tries to call a function on the implementation it will fail with an error indicating the proxy admin cannot fallback to the target implementation.

See [Openzeppelin doc - ProxyAdmin](https://docs.openzeppelin.com/contracts/5.x/api/proxy#ProxyAdmin) 





## Checklist

List of main points to check on a proxy contract based on OpenZeppelin architecture:

- constructor

  - call to `_disableInitializers()`to disable the possibility to initialize the implementation

- Storage gap in all base contracts if [ERC-7201](https://eips.ethereum.org/EIPS/eip-7201) is not used

- Public initialize function 

  - Add `initializer`to the signature to prevent its initializer function from being invoked twice.

- Internal `_init` function

  - Add `internal onlyInitializing` to the signature
  - Call all the `init` functions of the contracts parents
  - An `_init` function does not set any variable, it is role of the `unchained init` function

- internal `__init_unchained` function

  - No call to the parent `init` function of the contracts parents, it is role of the `_init` function
  - Set the different variables

- If UUPS proxy, the function to upgrade the proxy is public/external and protected by access control. With OpenZeppelin, the function `_authorizeUpgrade`is correctly overriden.

  

## Reference

### OpenZeppelin 

**Documentation**

a) [FAQ - Can I safely use delegatecall and selfdestruct?](https://docs.openzeppelin.com/upgrades-plugins/1.x/faq#delegatecall-selfdestruct)

b) [OpenZeppelin Hardhat Upgrades AP](https://docs.openzeppelin.com/upgrades-plugins/1.x/api-hardhat-upgrades)

c)[Proxy Upgrade Pattern - The Constructor Caveat](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#the-constructor-caveat)

d) [Proxy Upgrade Pattern - Unstructured Storage Proxies](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#unstructured-storage-proxies)4

e) [Upgrades Plugins - Test usage](https://docs.openzeppelin.com/upgrades-plugins/1.x/#test-usage)

f) [Writing Upgradeable Contracts - Avoiding Initial Values in Field Declarations](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#avoid-initial-values-in-field-declarations)

g) [Writing Upgradeable Contracts - Initializers](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializers)

h) [Writing Upgradeable Contracts - Modifying Your Contracts](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#modifying-your-contracts)

i) [Writing Upgradeable Contracts - Potentially Unsafe Operations](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#potentially-unsafe-operations)

k) [OpenZeppelin Truffle Upgrades API](https://docs.openzeppelin.com/upgrades-plugins/1.x/api-truffle-upgrades)

m) [Upgrades Plugins](https://docs.openzeppelin.com/upgrades-plugins/1.x/)

o) [Writing Upgradeable Contracts - Initializing the Implementation Contract](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializing_the_implementation_contract)

p) [Storage Collisions Between Implementation Versions](https://docs.openzeppelin.com/upgrades-plugins/1.x/proxies#storage-collisions-between-implementation-versions)

q) [blog - OpenZeppelin - staying safe with smart contract upgrades/](https://blog.openzeppelin.com/staying-safe-with-smart-contract-upgrades/)

[Truffle - A Sweet Upgradeable Contract Experience with OpenZeppelin and Truffle](https://trufflesuite.com/blog/a-sweet-upgradeable-contract-experience-with-openzeppelin-and-truffle/)

**Github**

j) [github.com/OpenZeppelin - mocks/ERC2771ContextMockUpgradeable.sol](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/b551d19e6e37deaa15d8c3ca7beec713031d83fd/contracts/mocks/ERC2771ContextMockUpgradeable.sol)

n) [github.com/OpenZeppelin - contracts/proxy/utils/Initializable.sol](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/blob/master/contracts/proxy/utils/Initializable.sol)

r) [npmjs.com - openzeppelin/hardhat-upgrades](https://www.npmjs.com/package/@openzeppelin/hardhat-upgrades)



### Others

- [OpenZeppelin forum - What’s the difference between onlyInitializing and initialzer](https://forum.openzeppelin.com/t/whats-the-difference-between-onlyinitializing-and-initialzer/25789/2)
- [immunefi - Wormhole Uninitialized Proxy Bugfix Review](https://medium.com/immunefi/wormhole-uninitialized-proxy-bugfix-review-90250c41a43a)
- [Certik - Upgradeable Proxy Contract Security Best Practices](https://www.certik.com/resources/blog/FnfYrOCsy3MG9s9gixfbJ-upgradeable-proxy-contract-security-best-practices)
- [EIP-1967: Proxy Storage Slots](https://eips.ethereum.org/EIPS/eip-1967.)
- Audius hack: 
  - [Audius Governance Takeover Post-Mortem 7/23/22](https://blog.audius.co/article/audius-governance-takeover-post-mortem-7-23-22)
  - [sharkteam.org - report/analysis audius hack](https://www.sharkteam.org/report/analysis/20220726001A_en.pdf)
  - [bleepingcomputer.com - Hackers steal $6 million from blockchain music platform Audius](https://www.bleepingcomputer.com/news/security/hackers-steal-6-million-from-blockchain-music-platform-audius/)
  - offzone moscow - Upgradable Contract Vulnerability—Analysis on the Hack of Web3 Music Platform Audius

