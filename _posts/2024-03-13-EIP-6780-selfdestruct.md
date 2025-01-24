---
layout: post
title:  EIP-6780, selfdestruct, we won't miss you
date:   2024-03-13
lang: en
locale: en-GB
categories: blockchain blockchainBestOf ethereum
tags: ethereum solidity opcode assembly
description: The Ethereum Dencun upgrade introduces the EIP-6780 which updates the opcode selfdestruct to deactivates the destruction of the contract, except if the contract is destructed in the same transaction as created.
image: /assets/article/blockchain/ethereum/solidity/solidity-selfdestruct-meme.png
isMath: false
---



`selfdestruct`is an opcode which, originally, destroyed the contract bytecode from the blockchain and sends the ether balance of the contract to an address passed in parameter.

The `Dencun upgrade` introduces the [EIP-6780](https://eips.ethereum.org/EIPS/eip-6780) ([ethereum-magicians](https://ethereum-magicians.org/t/eip-6780-deactivate-selfdestruct-except-where-it-occurs-in-the-same-transaction-in-which-a-contract-was-created/13539)) which updates the opcode `selfdestruct` to deactivate the destruction of the contract, except if the contract is destructed in the same transaction as created.

[TOC]

## History

During its history, several EIP have already been implemented or discussed regarding the opcode `selfdestruct`.

**Implemented**

- [EIP-6](https://eips.ethereum.org/EIPS/eip-6) 

In the first version, the opcode called `SUICIDE`  and it was changed to `SELFDESTRUCT`.

- [EIP-2929](https://eips.ethereum.org/EIPS/eip-2929#selfdestruct-changes) ([Berlin upgrade](https://github.com/ethereum/execution-specs/blob/119208cf1a13d5002074bcee3b8ea4ef096eeb0d/network-upgrades/mainnet-upgrades/berlin.md))

Gas cost increases for state access opcodes, which concerns also `selfdestruct`

- [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529) ([London upgrade](https://github.com/ethereum/execution-specs/blob/119208cf1a13d5002074bcee3b8ea4ef096eeb0d/network-upgrades/mainnet-upgrades/london.md))

This EIP has removed gas refunds for `SELFDESTRUCT`.

- [EIP-6049](https://eips.ethereum.org/EIPS/eip-6049) ([Shanghai Upgrade](https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/shanghai.md))

Deprecate SELFDESTRUCT without changing its behavior.



**Proposition**

These EIP have never been implemented.

- [Eip-3298](https://eips.ethereum.org/EIPS/eip-3298)

Remove gas refunds for SSTORE and SELFDESTRUCT. It was replaced by [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529).

- [Eip-4758](https://eips.ethereum.org/EIPS/eip-4758) 

Deactivate SELFDESTRUCT by changing it to SENDALL. The [EIP-6780](https://ethereum-magicians.org/t/eip-6780-deactivate-selfdestruct-except-where-it-occurs-in-the-same-transaction-in-which-a-contract-was-created/13539) has been preferred to the solution proposed by this EIP.

-------

## Common vulnerability

This section describes the common vulnerabilities and risks related to the use of `selfdestruct` in a contract.



![selfdestruct.drawio]({{site.url_complet}}/assets/article/blockchain/ethereum/solidity/selfdestruct.drawio.png)

### Impossibility to work (DoS)

If a contract A called a contrat B (or a library) to execute code without verifying that the contract is still in live (not destructed), a self destruct on the contract B can block the contract A for ever. 

#### Parity multisig wallet

A famous example concerns the [Parity multi sig wallet](https://www.parity.io/blog/a-postmortem-on-the-parity-multi-sig-library-self-destruct/). On 2017, a `selfdestruct`has been triggerd by an anonymous user on a library used by the wallet.  As a result, funds in 587 wallets, about 513,774.16 Ether as well as additional tokens, are blocked forever in the contract.

It can also be the case in a proxy architecture, see the paragraph "Proxy implementation not protected" for more details.

- Architecture

![crypto-wallet-parity-wallet-architecture.drawio]({{site.url_complet}}/assets/article/blockchain/wallet/parity-wallet/crypto-wallet-parity-wallet-architecture.drawio.png)

- "Attack" step

![crypto-wallet-parity-wallet-attack.drawio]({{site.url_complet}}/assets/article/blockchain/wallet/parity-wallet/crypto-wallet-parity-wallet-attack.drawio.png)

### Permanently loss of funds by sending ethers

When a smart contract is selfdestructed, all ethers sent to the contract are lost. When a smart contract has no code, following a self-destructed operation, transactions will success with no code executed. Thus, if you send ethers to the contract or call a function previously declared in the smart contract, the value of `msg.value` will be stored and blocked in the contract forever.

You can find a [Code4Arena report](https://github.com/code-423n4/2022-12-escher-findings/issues/296) / [solodit](https://solodit.xyz/issues/h-01-selfdestruct-may-cause-the-funds-to-be-lost-code4rena-escher-escher-contest-git) which gives a concrete example

> After the contract is destroyed, the subsequent execution of the contract's #buy() will always success, the msg.value will be locked in this address

This flaw can also be seen for contracts which perform `call`, `delegatecall` and `staticcall` without checking the existence of the contract. Indeed, the [solidity documentatation](https://docs.soliditylang.org/en/develop/control-structures.html#error-handling-assert-require-revert-and-exceptions) states: "The low-level functions `call`, `delegatecall` and `staticcall` return `true` as their first return value if the account called is non-existent..."

You can find an example in a [Code4Arena report](https://solodit.xyz/issues/m-05-failed-transfer-with-low-level-call-could-be-overlooked-code4rena-trader-joe-trader-joe-contest-git) / [solodit](https://solodit.xyz/issues/m-05-failed-transfer-with-low-level-call-could-be-overlooked-code4rena-trader-joe-trader-joe-contest-git). It also mentioned in the [Uniswap v3 report](https://github.com/Uniswap/v3-core/blob/main/audits/tob/audit.pdf).



### Proxy Implementation not protected

Several architectures with proxy do not correctly protect the `selfdestruct` functions.

In the standard proxy architecture, a function `initialize` replaces the traditional constructor and is defined in the implementation contract. This function is called by the proxy to initialize its own storage.

But this function is public and can also be called directly on the implementation contract if the proper mechanism to avoid this is not put in place. Therefore, an attacker can use this function to take over the contract and if a function contains `selfdestruct` , the attacker can call this function and destroy the implementation contract.

The effect will be different if it is a transparent proxy or an UUPS proxy.

With a transparent proxy, you still have the possibility to upgrade the proxy to a new implementation, but with an UUPS proxy, the logic to upgrade the contract is inside the implementation contract and the proxy can not be upgraded if the implementation contract is destroyed.

You can find an example in a [Consensys diligence report](https://consensys.io/diligence/audits/2020/11/pooltogether-lootbox-and-multiplewinners-strategy/) / [solodit](https://solodit.xyz/issues/lootbox-unprotected-selfdestruct-in-proxy-implementation-consensys-pooltogether-lootbox-and-multiplewinners-strategy-markdown) where this flaw is mentionned.

> The `LootBox` implementation contract is completely unprotected, exposing all its functionality to any actor on the blockchain. The most critical functionality is actually the `LootBox.destroy()` method that calls `selfdestruct()` on the implementation contract.



A bug bounties of $10 million has been also given by Wormhole to a whitehat  through the platform ImmuniFi for a similar bug, see [Wormhole Uninitialized Proxy Bugfix Review](https://medium.com/immunefi/wormhole-uninitialized-proxy-bugfix-review-90250c41a43a).

See also my [checklist](https://rya-sge.github.io/access-denied/2022/10/31/proxy-contract-summary/#avoid-leaving-a-contract-uninitialized) to implement a proxy safely

### DelegateCall

If a contract A performs a `delegatecall` to another contract B, since the call is executed in the context of the contract caller, the contract A can be destructed if the function from the contract B execute the `selfdestruct`opcode.  A `delegatecall`is often used inside the proxy architecture, but it can be used in other contexts.

If the function which performs the delegatecall, e.g. a function `execute`, is not protected enough, an attacker can use this function to perform a delegatecall to a malicous contract and trigger a `selfdestruct` on the contract source.

The behavior is also similar with`callcode`( see [twitter-pashov](https://twitter.com/pashovkrum/status/1753352639465578828?t=PNT2-vS6gEPgTl0yI-6pTA&s=35))

In this example from [Code4Arena](https://code4rena.com/reports/2023-07-tapioca) / [solodit](https://solodit.xyz/issues/h-28-toft-and-usdo-modules-can-be-selfdestructed-code4rena-tapioca-dao-tapioca-dao-git), a public function can be used to manipulate a contract address called to perform a `delegatecall` . An attacker can exploit this to provide a contract with a `selfdestruct` and calls the malicious function through the `delegatecall`.

>All TOFT and USDO modules have public functions that allow an attacker to supply an address `module` that is later used as a destination for a delegatecall. This can point to an attacker-controlled contract that is used to selfdestruct the module.

In this report from [Code4Arena](https://github.com/code-423n4/2022-07-fractional-findings/issues/200/) /[solodit](https://solodit.xyz/issues/h-01-vault-implementation-can-be-destroyed-leading-to-loss-of-all-assets-code4rena-fractional-fractional-v2-contest-git), the vulnerability uses an unprotected `initialize` function inside a proxy implementation to take over the contract and calls the `execute` function to perform a `delegatecall` to an external contract containing the `selfdestruct` opcode.

The code of the `execute` function is available on [GitHub](https://github.com/code-423n4/2022-07-fractional/blob/8f2697ae727c60c93ea47276f8fa128369abfe51/src/Vault.sol#L131)

> The problem is that that implementation vault is not initialized, which means that anybody can initialize the contract to become the owner, and then destroy it by doing a delegate call (via the `execute` function) to a function with the `selfdestruct` opcode. 

The principle is also similar in this report from [Code4Arena](https://github.com/sherlock-audit/2024-01-rio-vesting-escrow-judging) / [solodit](https://solodit.xyz/issues/h-1-vaults-can-be-bricked-by-selfdestructing-implementations-using-forged-immutable-args-sherlock-rio-vesting-escrow-git)

> As was seen in the Astaria beacon proxy [issue](https://x.com/apoorvlathey/status/1671308196743647232?s=20), an attacker is able to forge the calldata that the proxy normally would forward, and can cause the implementation to `selfdestruct()` itself via a `delegatecall()`. The current code has a very similar vulnerability, in that every escrow performs a `delegatecall()` to an address coming from the factory, which is a forgeable immutable argument.

-----

## Motivation to use selfdestruct

This section uses as reference this [research paper](https://soarsmu.github.io/papers/2021/tosem216.pdf) from the [Monash University](https://www.monash.edu/), which provides the reason behind the use of `selfdestruct`. The paper dates from 2021, but it keeps to be very relevant.

### Security Concerns

>use the selfdestruct function to stop the contracts when security vulnerabilities are detected in their contracts. After fixing the vulnerabilities, they can deploy a new contract

- As seen previously, `selfdestruct` adds also new vulnerabilities vectors inside the smart contract.

- You can use alternative like a `pause` function or use a proxy contract to keep the possibility to fix a bug by upgrading to a new implementation.

### End of duty

> when the duty of the contract is finished, they will call the selfdestruct function to remove the contracts from the blockchain, which can clean up the blockchain environment.

It seems a valid concern. When a smart contract is no longer useful, it is indeed good to remove the bytecode from the blockchain (clean up) and also to avoid to have old smart contract to maintain.

For example, in Tokenization and RWA, it is useful to destroy the smart contract if the underlying shares are destroyed. It has been used for example in the [CMTAT](https://github.com/CMTA/CMTAT), a swiss standard to tokenize shares, before being replacing by a  function `deactivateContract`.

But the risk induced by selfdestruct is not enough and you can implement viable alternative, for example:

- By putting the contracts in the pause state forever
- Transmits the contract ownership to the address zero,...

### Quickly Withdraw Ethers

> By using the selfdestruct function, the owner of the contract can remove all the Ethers to a specific address. 

I think it is a better idea to implement a clean `withdraw` function. Moreover, `selfdestruct` sends only the remaining ethers, and don't send the tokens owned by the smart contract.

### Upgrade Contracts

> Adding a selfdestruct function is the easiest method to upgrade their contract.
> This function allows them to remove the old version of the contract and deploy a new version

With proxy, you have now a way to upgrade in live a contract. While it is not an easy task due to several constraints on a proxy, you can decide to put solutions offered in the paragraph *End of Duty* and deploy a new contract.

### Gas Refund

> the gas refund feature of the selfdestruct function allows the transaction sender to get up to half of the gas back. 

This refund has been removed with the [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529).

Before this EIP, `selfdestruct`  has been used by the [GasToken](https://gastoken.io/), a token uses to store gas when the gas price is low and use the gas when it is expensive. Specifically, a user can create a simple contract (GasToken) that contains selfdestruct function when the gas price is low.
Then, the user can destruct the GasToken to save the gas when the gas price is high [Reference: [tosem216.pdf](https://soarsmu.github.io/papers/2021/tosem216.pdf)].

This behavior caused clutter on the blockchain and defeated the original purpose of cleaning it up. This is why the [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529) has been introduced to terminate this use.

Reference: [Fundamentals of Gas Tokens](https://blog.openzeppelin.com/fundamentals-of-gas-tokens), [GasToken](https://gastoken.io/)

### Change the behavior of a contract

> It was not mentionned in the research paper, but a use case to employ `selfdestruct` was to modify the code of a contract deployed.

By combining `selfdestruct` with the opcode `create2`, it was possible to change the contract bytecode, furthermore breaking the code immutability.

With `create2`, the address can be pre-computed and it is easier to deploy a bytecode at the same address again.

The operation consisted to:

- Deploy the contract with `create2`

- Use later the opcode `selfdestruct` to destroy a contract
- use `create2` to deploy the contract to the same address. 

The only requirement is that the contract has to be deployed with `create2` in the first time.



----

## Fun Fact

On April 2022, a hacker after successfully hacked over $1 million in Crypto assets, destructed the smart contract which hold the stolen funds before withdrawing the funds from the smart contract.

Reference: [cointelegraph - Hacker bungles DeFi exploit: Leaves stolen $1M in contract set to self destruct ](https://cointelegraph.com/news/hacker-bungles-defi-exploit-leaves-stolen-1m-in-contract-set-to-self-destruct)

-----

## Breaking control check with selfdestruct

With `selfdestruct`, you have the possibility to break several invariant:

### Contract balance

A check based on the contract balance can be bypassed by forcly sends ether to a contract by using `selfdestruct`.

This invariant can still by bypassed after the upgrade since the transfer of ether is still maintained with the [EIP-6780](https://ethereum-magicians.org/t/eip-6780-deactivate-selfdestruct-except-where-it-occurs-in-the-same-transaction-in-which-a-contract-was-created/13539).

Fortunately,  you will still have the possibility to resolve nice [CTF challenge.](https://blog.solidityscan.com/security-implications-of-selfdestruct-in-solidity-part-2-371b0a0b6ede)

### Contract still living

Contrary to what happened with the [Parity multig sig wallet bug](https://www.parity.io/blog/a-postmortem-on-the-parity-multi-sig-library-self-destruct/), the upgrade will ensure that when a contract/library has been deployed, its code cannot be deleted from the blockchain or its behavior modified by combining `create2 `and `selfdestruct`. After the upgrade, you will no longer have to worry about whether the contract  has been destructed or not.

But the end of `selfdestruct` does not mean that a `behaviour` of a contract can not be changed, e.g. through the call of functions or with the proxy architecture.

-------

## Conclusion

The opcode `selfdestruct` has been initially a good idea. It allowed to reduce the quantity of bytecode stored on the blockchain and provided an interesting tool to developpers to remove unused code and retrieve ethers from a contract.

Unfortunately, the incentives to use `selfdestruct` to clean up the blockchain proved to be counterproductive and has been already removed ([EIP-3529](https://eips.ethereum.org/EIPS/eip-3529)). 

Moreover, its use to change the bytecode of a deployed contract (possible with `create2`) broke the principle of immutability, an important guarantee for users.

Therefore, the security risk posed by this sensible operation makes it better to disable it and find better alternative to fill the different use case where this opcode has been used.

------

## References

- [EIP-6789](https://eips.ethereum.org/EIPS/eip-6780) ([ethereum-magicians](https://ethereum-magicians.org/t/eip-6780-deactivate-selfdestruct-except-where-it-occurs-in-the-same-transaction-in-which-a-contract-was-created/13539))
- [Parity multig sig wallet bug](https://www.parity.io/blog/a-postmortem-on-the-parity-multi-sig-library-self-destruct/)
- [research paper - Why Do Smart Contracts Self-Destruct?](https://soarsmu.github.io/papers/2021/tosem216.pdf)
