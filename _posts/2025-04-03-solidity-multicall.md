---
layout: post
title: Multicall in Solidity: CALL vs DELEGATECALL Explained
date:   2025-04-03
lang: en
locale: en-GB
categories: blockchain ethereum solidity
tags: blockchain ethereum solidity multicall delegatecall openzeppelin
description: Discover how Multicall enables batch execution of smart contract calls, when to use CALL vs DELEGATECALL, and how contract interactions differ from EOAs.
image: /assets/article/blockchain/ethereum/solidity/multicall/multicall-contract-delegatecall.png
isMath: false
---

Multicall is a smart contract pattern in Ethereum and other EVM-compatible blockchains that allows bundling multiple function calls into a single transaction. Each function call is therefore performed atomically. 

By aggregating several calls in the same transaction, this pattern offers several advantages:

**On-chain perspective:**

- Lower gas costs since the base fee is paid only once
- All transactions are performed in the same block, mitigating frontrunning in certain cases.
- Allowing custom logic in the function call

**Off-chain perspective (Front-end/Backend)**

- Lowering API calls to RPC providers.
- Faster loading of front-end, because multiple information get fetched in one on-chain read call.

[TOC]

## Base concept

### How Multicall Works

1. A user submits multiple function calls to a specific multicall contract or a contract implementing multicall (see OpenZeppelin implementation).
2. The multicall contract sequentially executes these function calls.
3. The results of each call are collected and returned in a single response.
4. If any call fails (depending on implementation), the entire transaction may revert or continue execution.

### Different type of calls

There are two types of accounts in Ethereum: Externally Owned Accounts (EOAs) and Contract Accounts. EOAs are controlled by private keys, and Contract Accounts are controlled by code.

When an EOA calls a contract, the `msg.sender` value during execution of the call provides the address of that EOA. This is also true if the call (`call`) was executed by a contract.

A smart contract can perform several different type of calls

-  [`CALL`](https://www.evm.codes/#f1?fork=cancun) opcode

When a CALL is executed, the *context* changes. New context means storage operations will be performed on the called contract, with a new value (i.e. `msg.value`) and a new caller (i.e. `msg.sender`).

See also [RareSkills - Low Level Call vs High Level Call in Solidity](https://www.rareskills.io/post/low-level-call-solidity)

- `staticcall` opcode

`staticcall` is a variant of `call`, but it does not allow state modifications. If a function tries to modify state, `staticcall` will revert.

See [RareSkills - Staticcall](https://www.rareskills.io/post/solidity-staticcall)

- [`DELEGATECALL`](https://www.evm.codes/#f4) opcode

Contrary to `call`, perform a `delegatecall`won't change the context of the call. This means the contract being delegatecalled will see the same `msg.sender`, the same `msg.value`, and operate on the same storage as the calling contract. This is very powerful, but can also be dangerous.

It's important to note that you cannot directly delegatecall from an EOA—an EOA can only call a contract, not delegatecall it.

### Implementation

There are two main ways to implement and perform a multicall

- The most recent one, by OpenZeppelin, consists to include a function multicall in your contract which allows a sender to perform a multicall on this contract. This present the advantage to keep `msg.sender`as the contract caller
- The first version of `multicall`allows to perform severall `calls` on different contracts. For a write call, it means that the context will change apart if the contract `multicall`is called through a `delegatecall` which is only possible for a smart contract. EOA can then not performed a write call if the value of `msg.sender`or `msg.value`is important.

#### Summary

|                            | OpenZeppelin multicall | External contract multicall |
| -------------------------- | ---------------------- | --------------------------- |
| Opcode used                | `delegateCall`         | `call`                      |
| Write call for EOA         | &#x2611;               | &#x2612;                    |
| Read call for EOA          | &#x2611;               | &#x2611;                    |
| Write call from a contract | &#x2611;               | &#x2611;                    |
| Read call from a contract  | &#x2611;               | &#x2611;                    |
| Work with all contract     | &#x2612;               | &#x2611;                    |



#### OpenZeppelin multicall

> Code: [OpenZeppelin - Multicall.sol](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Multicall.sol)
> [doc v5](https://docs.openzeppelin.com/contracts/5.x/utilities#multicall)

Abstract contract with a utility to allow batching together multiple calls on the same contract in a single transaction. Useful for allowing EOAs to perform multiple operations at once.

Contrary to `multicall3`, it works only on a specific smart contract which extends the library.

Provides a function to batch together multiple calls in a single external call.

 * Consider any assumption about calldata validation performed by the sender may be violated if it's not especially
 * careful about sending transactions invoking {multicall}. For example, a relay address that filters function
 * selectors won't filter calls nested within a {multicall} operation.

NOTE: Since 5.0.1 and 4.9.4, this contract identifies non-canonical contexts (i.e. `msg.sender` is not {Context-_msgSender}).

 * If a non-canonical context is identified, the following self `delegatecall` appends the last bytes of `msg.data`to the subcall. This makes it safe to use with {ERC2771Context}. 
 * Contexts that don't affect the resolution of {Context-_msgSender} are not propagated to subcalls.

Version vulnerable if used with ERC-2771

```solidity
function multicall(bytes[] calldata data) external virtual returns (bytes[] memory results) {
        results = new bytes[](data.length);
        for (uint256 i = 0; i < data.length; i++) {
            results[i] = Address.functionDelegateCall(address(this), data[i]);
        }
        return results;
    }
```

[Version 5.2.0](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/acd4ff74de833399287ed6b31b4debf6b2b35527/contracts/utils/Multicall.sol)

```solidity
abstract contract Multicall is Context {
    /**
     * @dev Receives and executes a batch of function calls on this contract.
     * @custom:oz-upgrades-unsafe-allow-reachable delegatecall
     */
    function multicall(bytes[] calldata data) external virtual returns (bytes[] memory results) {
        bytes memory context = msg.sender == _msgSender()
            ? new bytes(0)
            : msg.data[msg.data.length - _contextSuffixLength():];

        results = new bytes[](data.length);
        for (uint256 i = 0; i < data.length; i++) {
            results[i] = Address.functionDelegateCall(address(this), bytes.concat(data[i], context));
        }
        return results;
    }
}
```

Example from [OpenZeppelin doc:](https://docs.openzeppelin.com/contracts/5.x/utilities#multicall)

```solidity
// contracts/Box.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Multicall} from "@openzeppelin/contracts/utils/Multicall.sol";

contract Box is Multicall {
    function foo() public {
        // ...
    }

    function bar() public {
        // ...
    }
}
```

This is how to call the `multicall` function using Ethers.js, allowing `foo` and `bar` to be called in a single transaction:

```javascript
// scripts/foobar.js

const instance = await ethers.deployContract("Box");

await instance.multicall([
    instance.interface.encodeFunctionData("foo"),
    instance.interface.encodeFunctionData("bar")
]);
```

##### Past vulnerability

Any contract implementing both `Multicall` and ERC-2771 is vulnerable to address spoofing. In the context of the OpenZeppelin contracts library, this can be done with `Multicall` and `ERC2771Context`. An attacker can wrap malicious calldata within a forwarded request and use `Multicall`'s `delegatecall` feature to manipulate the `_msgSender()` resolution in the subcalls.

Schema from OpenZeppelin post-mortem:

![openzeppelin-multicall-erc2771]({{site.url_complet}}/assets/article/blockchain/ethereum/solidity/multicall/openzeppelin-multicall-erc2771.png)

Reference: [Arbitrary Address Spoofing Attack: ERC2771Context Multicall Public Disclosure](https://blog.openzeppelin.com/arbitrary-address-spoofing-vulnerability-erc2771context-multicall-public-disclosure)

#### Multicall3

> Initial project by MakerDAO (archive): [makerdao/multicall](https://github.com/makerdao/multicall)
>
> Multicall3 (and multicall 1 & 2) [mds1/multicall3](mds1/multicall3/tree/main)

Multicall3 is a fork from the library `multicall`, a project initiated by MakerDAO.

Multicall3 has two main use cases:

- Aggregate results from multiple contract reads into a single JSON-RPC request.
- Execute multiple state-changing calls in a single transaction.

##### Deprecated version

[`multicall`](https://github.com/mds1/multicall3/tree/src/Multicall.sol) is the original contract, and [`Multicall2`](https://github.com/mds1/multicall3/tree/src/Multicall2.sol) added support for handling failed calls in a multicall. [`Multicall3`](https://github.com/mds1/multicall3/tree/src/Multicall3.sol) is recommended over these because it's backwards-compatible with both, cheaper to use, adds new methods, and is deployed on more chains

- multicall (original version): this version aggregates results from multiple read-only function calls

- Multicall2 is the same as Multicall, but provides addition functions that allow calls within the batch to fail. 



##### Call multicall from a smart contract VS EOA

Since an EOA cannot perfor a `delegatecall`, this significantly reduces the benefit of calling Multicall3 from an EOA—any calls the Multicall3 executes will have the MultiCall3 address as the `msg.sender`. **This means you should only call Multicall3 from an EOA if the `msg.sender` does not matter.**

If you are using a contract wallet or executing a call to Multicall3 from another contract, you can either CALL or DELEGATECALL. 

- `CALL` will behave the same as described above for the EOA case
- `delegatecalls` will preserve the context. 

This means if you delegatecall to `Multicall3` from a contract, the `msg.sender` of the calls executed by `Multicall3` will be that contract. This can be very useful, and is how the Gnosis Safe [Transaction Builder](https://help.safe.global/en/articles/40841-transaction-builder) works to batch calls from a Safe.

Similarly, because `msg.value` does not change with a delegatecall, you must be careful relying on `msg.value` within a multicall. 

To learn more about this, see [here](https://github.com/runtimeverification/verified-smart-contracts/wiki/List-of-Security-Vulnerabilities#payable-multicall) and [here](https://samczsun.com/two-rights-might-make-a-wrong/).

###### Schema

Made with the help of ChatGPT and [plantUML](https://plantuml.com)

EOA -> multicall

- **Inside `Multicall3`** → `msg.sender = EOA`
- **Inside `TargetContract`** → `msg.sender = Multicall3`

![emulticall-eoa]({{site.url_complet}}/assets/article/blockchain/ethereum/solidity/multicall/emulticall-eoa.png)





Contract -> multicall with `delegatecall`

**Inside `Multicall3` (executing as `ContractA`)** → `msg.sender = EOA`

**Inside `TargetContract`** → `msg.sender = ContractA`

![multicall-contract-delegatecall]({{site.url_complet}}/assets/article/blockchain/ethereum/solidity/multicall/multicall-contract-delegatecall.png)

Contract -> multicall with `call`

- **Inside `Multicall3`** → `msg.sender = ContractA`
- **Inside `TargetContract`** → `msg.sender = Multicall3`

![multicall-contract-call]({{site.url_complet}}/assets/article/blockchain/ethereum/solidity/multicall/multicall-contract-call.png)



#### Uniswap V3 multicall

> Code: [github.com/Uniswap - Multicall.sol](https://github.com/Uniswap/v3-periphery/blob/main/contracts/base/Multicall.sol)
>
> Reference: [docs.uniswap.org/contracts/v3/reference/overview](https://docs.uniswap.org/contracts/v3/reference/overview), [docs.uniswap.org - periphery/base/Multicall](https://docs.uniswap.org/contracts/v3/reference/periphery/base/Multicall)

A `multicall`contract is available as a periphery contract. The periphery is a constellation of smart contracts designed to support domain-specific interactions with the core. As the Uniswap protocol is a permissionless system, the contracts described below have no special privileges and are only a small subset of possible periphery-like contracts.

Enables calling multiple methods in a single call to the contract

Difference with openzeppelin multicall:

- Revert if one call fails
- Store the result of each call in the array `result`
- Code is older than OpenZeppelin and use a very old solidity version (`0.7.6`)

Note

```solidity
// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity =0.7.6;
pragma abicoder v2;
abstract contract Multicall is IMulticall {
    /// @inheritdoc IMulticall
    function multicall(bytes[] calldata data) public payable override returns (bytes[] memory results) {
        results = new bytes[](data.length);
        for (uint256 i = 0; i < data.length; i++) {
            (bool success, bytes memory result) = address(this).delegatecall(data[i]);

            if (!success) {
                // Next 5 lines from https://ethereum.stackexchange.com/a/83577
                if (result.length < 68) revert();
                assembly {
                    result := add(result, 0x04)
                }
                revert(abi.decode(result, (string)));
            }

            results[i] = result;
        }
    }
}
```

Note:

- This code has been written before the introduction of `custom error`(0.8.0). so I am not sure if it sill correct.
- This code must not be combined with ERC-2271 forwarder since it does not patch the vulnerability contrary to OpenZeppelin multicall
- Check result length

```solidity
if (result.length < 68) revert();
```

If `result.length` is less than 68, then the transaction failed silently (without a revert message)

- Slice the signature hash

```solidity
 assembly {
     result := add(result, 0x04)
 }
```

From [ethereum.stackexchange - How can I get the revert reason of a call in Solidity so that I can use it in the same on-chain transaction? (2020)](https://ethereum.stackexchange.com/questions/83528/how-can-i-get-the-revert-reason-of-a-call-in-solidity-so-that-i-can-use-it-in-th)

### ERC-6357: Single-contract Multi-delegatecall

> [ERC specification](https://eips.ethereum.org/EIPS/eip-6357), [Ethereum magicians](https://ethereum-magicians.org/t/eip-6357-single-contract-multi-delegatecall/12621)

This EIP standardizes an interface containing a single function, `multicall`, allowing EOAs to call multiple functions of a smart contract in a single transaction, and revert all calls if any call fails.

```solidity
pragma solidity ^0.8.0;

interface IMulticall {
    /// @notice           Takes an array of abi-encoded call data, delegatecalls itself with each calldata, and returns the abi-encoded result
    /// @dev              Reverts if any delegatecall reverts
    /// @param    data    The abi-encoded data
    /// @returns  results The abi-encoded return values
    function multicall(bytes[] calldata data) external virtual returns (bytes[] memory results);

    /// @notice           OPTIONAL. Takes an array of abi-encoded call data, delegatecalls itself with each calldata, and returns the abi-encoded result
    /// @dev              Reverts if any delegatecall reverts
    /// @param    data    The abi-encoded data
    /// @param    values  The effective msg.values. These must add up to at most msg.value
    /// @returns  results The abi-encoded return values
    function multicallPayable(bytes[] calldata data, uint256[] values) external payable virtual returns (bytes[] memory results);
}
```

####  Rationale

`multicallPayable` is optional because it isn’t always feasible to implement, due to the `msg.value` splitting.

####  Reference Implementation

```solidity
pragma solidity ^0.8.0;
/// Derived from OpenZeppelin's implementation
abstract contract Multicall is IMulticall {
    function multicall(bytes[] calldata data) external virtual returns (bytes[] memory results) {
        results = new bytes[](data.length);
        for (uint256 i = 0; i < data.length; i++) {
            (bool success, bytes memory returndata) = address(this).delegatecall(data);
            require(success);
            results[i] = returndata;
        }
        return results;
    }
}
```





## Reference

- [cyborgDennet - Ethereum Multicall Tutorial](https://blog.blockmagnates.com/ethereum-multicall-tutorial-5893d870f5ef)
- [smart contract tips - Multicall functions in Smart Contracts](https://smartcontract.tips/en/post/multicall-functions-in-smart-contracts)