---
layout: post
title:  "Solidity Gas Optimization Cheatsheet"
date:   2023-09-26
last-update: 
categories: blockchain blockchainBestOf ethereum solidity
lang: en
locale: en-GB
tags: blockchain crypto ethereum gas
image: /assets/article/blockchain/ethereum/ethereum-logo-portrait-purple-purple.png
description: This article summarizes the main and easier tricks to save gas with Solidity.
---

This article summarizes the main and easier tricks to save gas when you program smart contracts with **Solidity**.

Smart contract optimization is a key principle on EVM blockchain with Solidity, particularly for a deployment on Ethereum mainet where transactions fees are height. Optimizing gas cost allows to reduce the fees paid by the smart contract users, which is clearly better for their experience.

You will find a more accurate and complete list on [RareSkills](https://www.rareskills.io/post/gas-optimization), which is one of the main references for this article. There is also a very good lesson on [Udemy](https://www.udemy.com/course/advanced-solidity-understanding-and-optimizing-gas-costs/) by Jeffrey Scholz.

To increase your knowledge, you can also see the RareSkills interview questions related to Gas where the answers are available in my articles: [Medium](https://rya-sge.github.io/access-denied/2024/02/14/solidity-interview-question-rareskills/#gas), [Hard](https://rya-sge.github.io/access-denied/2024/03/04/solidity-interview-question-rareskills-hard/#gas), [Advanced](https://rya-sge.github.io/access-denied/2024/05/06/solidity-interview-question-rareskills-advanced/#gas).

The goal of this article is not to aggressively optimize the code and will not present all possible optimizations.

[TOC]



## Key concepts

Before that, here some key concepts

- Gas cost: cost in gas to execute the smart contract.

The transaction gas cost is fixed, it depends on the code of each opcode executed during the transaction and can be precomputed. And if it can be precomputed, it can be optimized...

- Gas price: actual price to pay to a validator (since Proof of Stake) to execute the smart contract and validate the transaction. The gas price is not fixed, it depends on the supply and demand.

Reference: [3. moralis](https://moralis.io/how-to-reduce-solidity-gas-costs-full-guide/), [ethereum.org/en/developers/docs/gas/](https://ethereum.org/en/developers/docs/gas/), [ethereum.stackexchange.com - Why do we still pay gas in proof-of-stake?](https://ethereum.stackexchange.com/questions/141701/why-do-we-still-pay-gas-in-proof-of-stake)



## Cheatsheet
### A. Use the keyword pure and view

Without this keyword, even if you do nothing in your function, you will have gas cost to pay 

This allows you to avoid consuming gas when these functions are called from outside, for example from your client application.

Warning: inside the contract, a call to these functions from another function will continue to consume gas

Reference: [How can I call a constant function without spending any gas inside a transaction function?](https://ethereum.stackexchange.com/questions/13851/how-can-i-call-a-constant-function-without-spending-any-gas-inside-a-transaction)



### B. Cache storage variables: write and read storage variables exactly once

Reading from a storage variable costs at least 100 gas as Solidity does not cache the storage read. Writes are considerably more expensive. 

Therefore, you should manually cache the variable to do exactly one storage read and exactly one storage write.

**For a loop**

When you iterate over a loop, you will have a condition, a limit number, to get out of the loop. This number is generally stored inside a storage variable.

A read operation can be expensive for a loop operation since this operation is performed for each iteration.

The solution is to create a local variable to avoid fetching information on the blockchain.

See point F for an example

Reference: [3. moralis](https://moralis.io/how-to-reduce-solidity-gas-costs-full-guide/), [rareskills.io/post/gas-optimization#viewer-8lubg](https://www.rareskills.io/post/gas-optimization#viewer-8lubg)

### C. Use calldata instead of memory

Use calldata instead of memory to pass as argument, e.g. an array

```solidity
function mintBatch(address[] calldata accounts,uint256[] calldata values) 
```

Inside a constructor, unfortunately it is not possible to use `calldata`, see [ethereum.stackexchange.com](https://ethereum.stackexchange.com/questions/125100/the-reason-why-cant-i-use-calldata-as-a-data-location-for-constructor-parameter) it is the reason why you will see the use of `memory as for this example from OpenZeppelin [ERC20.sol#L50C1-L54C1](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/ERC20.sol#L50C1-L54C1)

```solidity
constructor(string memory name_, string memory symbol_) 
{        _name = name_;        
		_symbol = symbol_;    
}
```



Why?
As indicated in the solidity doc *Calldata is a non-modifiable, non-persistent area where function arguments are stored, and behaves mostly like memory.*

From the [Solidity doc](https://docs.soliditylang.org/en/v0.8.21/types.html#data-location)

*If you can, try to use `calldata` as data location because it will avoid copies and also makes sure that the data cannot be modified*

Reference: [4. Coinmonks/solidity-storage-vs-memory-vs-calldata](https://medium.com/coinmonks/solidity-storage-vs-memory-vs-calldata-8c7e8c38bce), [5. docs.soliditylang.org#data-location](https://docs.soliditylang.org/en/v0.8.21/types.html#data-location)

Some additional lectures: [github.com/ethereum/solidity/issues/5545](https://github.com/ethereum/solidity/issues/5545)

### D.  Use uncheck for arithmetic operation

Since Solidity 0.8.0, all arithmetic operations revert on over- and underflow by default.

This verification adds additional opcode and increase the gas cost of the transaction.

If you are absolutely sure that an underflow/overflow will never happen, you can wrap your operation inside an unchecked block.

Example from the documentation

```solidity
 function f(uint a, uint b) pure public returns (uint) {
        // This subtraction will wrap on underflow.
        unchecked { return a - b; }
 }
```

See point G for an example with a loop

References

- [github.com/ethereum/solidity/issues/10698](https://github.com/ethereum/solidity/issues/10698)
- [docs.soliditylang.org/en/v0.8.16/control-structures.html#checked-or-unchecked-arithmetic](https://docs.soliditylang.org/en/v0.8.16/control-structures.html#checked-or-unchecked-arithmetic)
- [hackmd.io/@totomanov/gas-optimization-loops](https://hackmd.io/@totomanov/gas-optimization-loops)
- [rareskills.io/post/gas-optimization#viewer-5f1pj](https://www.rareskills.io/post/gas-optimization#viewer-5f1pj)




### E. Use ++i instead of i++ to iterate over loop

The reason behind this is in way ++i and i++ are evaluated by the compiler.

- with i++, the variable i (its old value) is returned a first time before incrementing the variable. Therefore, there are 2 values stored on the stack.

- with ++i, the compiler evaluates first the ++ operation on i (i.e it increments i) then returns the variable incremented i. Therefore, there are only one value stored on the stack.

According to cygarr on X

 *the left contract (i++) contains two extra instructions compared to the right contract (++i). These two instructions are DUP (3 gas) and POP (2 gas), which explains the 5 gas difference from earlier.*

Reference: [twitter.com/0xCygaar/status/1607860326271438848](https://twitter.com/0xCygaar/status/1607860326271438848)

### F. Gas-optimal for loop template

By combining  C, D and E, you can obtain this example to create optimize loop.

```solidity
// Store the storage variable inside a local variable
uint256 limit = storageVariableUint256;
for (uint256 i; i <= limit; ) {
    // deactivate check overflow
    unchecked {
    	// ++i instead of i++
        ++i;
    }
}
```

Reference: [rareskills.io/post/gas-optimization#viewer-8rekj](https://www.rareskills.io/post/gas-optimization#viewer-8rekj)

**Exception**

*The solidity version [0.8.22](https://soliditylang.org/blog/2023/10/25/solidity-0.8.22-release-announcement) introduces an overflow check optimization that automatically generates an unchecked arithmetic increment of the counter of for loops.  As a result, it is not useful to use `unchecked` if the loop meets the criteria (see the release doc). 

This native optimization works only for the comparison `<`and not with `<=`

**Example**

```solidity
// Store the storage variable inside a local variable
uint256 limit = storageVariableUint256;
for (uint256 i; i < limit; ++i) {
	// Body
}
```

See [Solidity 0.8.22 Release Announcement](https://soliditylang.org/blog/2023/10/25/solidity-0.8.22-release-announcement)

### G. Most use condition in AND and OR

Inside a condition, you should:

For AND operation, put the most frequent condition (or the condition with the highest probability to fail) first since the second will not be evaluate if the first operation return 0

For OR operation, same scenario, but in the first place it is the condition with the highest probability of success.

Reference: [rareskills.io/post/gas-optimization#viewer-8ieel](https://www.rareskills.io/post/gas-optimization#viewer-8ieel)

### H. Use custom errors instead of require

For custom errors, solidity stores only the first 4 bytes of the hash of the error signature and returns only that.  Therefore, during reverting, only 4 bytes needs to be stored in memory.

In the case of string messages in require statements, Solidity must store(in memory) and revert with at least 64 bytes.

Reference: [blog.openzeppelin.com/defining-industry-standards-for-custom-error-messages-to-improve-the-web3-developer-experience](https://blog.openzeppelin.com/defining-industry-standards-for-custom-error-messages-to-improve-the-web3-developer-experience), [www.rareskills.io/post/gas-optimization#viewer-a0fm0](https://www.rareskills.io/post/gas-optimization#viewer-a0fm0)



### I. Pack your variable inside a struct

The size slot used by the EVM is 32 bytes. You can pack your variable in a slot of 32 bytes to save gas on storage

For example, this struct

```solidity
struct myStruct {
	address account;
	string myString;
	uint8 number;
	bool myBool;
}
```

can by optimized by moving the variable `myString`at the end of the struct because

account => 20 bytes

number => 1 bytes

myBool => 1 bytes

The total is 22 bytes and can be stored in only one slot.

```solidity
struct myStruct {
	address account;
	uint8 number;
	bool myBool;
	string myString;
}
```

Reference: [rareskills.io/post/gas-optimization#viewer-f8m1r](https://www.rareskills.io/post/gas-optimization#viewer-f8m1r)

My thanks to [Marcologonz](https://x.com/Marcologonz) for pointing out an error, now corrected, in this section.

### J. Use the optimizer to compile your contract

The Solidity optimizer tries to simplify complicated expressions, which reduces both code size and execution cost, 

You can activate the optimizer in the configuration inside your development tool (Hardhat or Foundry e.g.).

Parameter

The number of runs specifies roughly how often each opcode of the deployed code will be executed across the life-time of the contract. This means it is a trade-off parameter between code size (deploy cost) and code execution cost (cost after deployment).

- A “runs” parameter of “1” will produce short but expensive code. 

- In contrast, a larger “runs” parameter will produce longer but more gas efficient code.

Example with hardhat

```solidity
module.exports = {  
    solidity: {    
            version: "0.8.19",    
            settings: {      
                optimizer: {        
                enabled: true,        
                runs: 1000,      
                },    
            },  
        }, 
};
```

References:

- [hardhat.org/hardhat-runner/docs/guides/compile-contracts#configuring-the-compiler](https://hardhat.org/hardhat-runner/docs/guides/compile-contracts#configuring-the-compiler)
- [docs.soliditylang.org/en/v0.8.17/internals/optimizer.html](https://docs.soliditylang.org/en/v0.8.17/internals/optimizer.html)
- [rareskills.io/post/gas-optimization#viewer-d3ced](https://www.rareskills.io/post/gas-optimization#viewer-d3ced)

### K. Choose your data structure correctly

Choosing your data structure correctly is crucial.

- Use a map or an array ?

**map**, organized as key-value pairs, is less expensive for direct access since you don't need to iterate over the whole structure, contrary to an array. But a map is not iterable which may be lacking depending on your needs.

Moreover, for **array**, solidity adds bytecode that checks that the index read is valid, otherwise the function is reverted with a panic error. It is however possible to avoid this length checks by using the function *unsafeAccess* function in Openzeppelin’s [Arrays.sol](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Arrays.sol) library, but only if you are 100% sure that your index will always be valid.

See [RareSkills - Using mapping instead of arrays to avoid length checks](https://www.rareskills.io/post/gas-optimization#viewer-87gqn), [RareSkills - Using unsafeAccess on arrays to avoid redundant length checks](https://www.rareskills.io/post/gas-optimization#viewer-do9b4), [Hacken - Gas Optimization In Solidity: Strategies For Cost-Effective Smart Contracts](https://hacken.io/discover/solidity-gas-optimization/)

- If an array, keep the elements sorted or not ?

With an unsorted array, you can easily add a new element because you do not need to care about the order of the array. But, if you want to search for an element, you must iterate through the whole array.

The sorted array is the exact opposite: it is more efficient to perform research because you can use a binary search which is more optimized.

I made an article to compare these two structures: [Access Denied - What to choose between sorted and unsorted array](https://rya-sge.github.io/access-denied/2023/01/06/sorted-unsorted-array/)

## Other tips

- Cheap Contract Deployment Through Clones: [youtube.com/watch?v=3Mw-pMmJ7TA](https://www.youtube.com/watch?v=3Mw-pMmJ7TA)

- Utilizing Bitmaps to dramatically save on Gas: [soliditydeveloper.com/bitmaps](https://soliditydeveloper.com/bitmaps)

## Reference

1. [rareskills.io - The RareSkills Book of Solidity Gas Optimization: 80+ Tips](https://www.rareskills.io/post/gas-optimization)
2. [Udemy - Jeffrey Scholz - Advanced Solidity: Understanding and Optimizing Gas Costs](https://www.udemy.com/course/advanced-solidity-understanding-and-optimizing-gas-costs/?couponCode=ST10MT8624)
3. [0xmacro.com - Solidity Gas Optimizations Cheat Sheet](https://0xmacro.com/blog/solidity-gas-optimizations-cheat-sheet/)
4. [moralis.io - How to Reduce Solidity Gas Costs – Full Guide](https://moralis.io/how-to-reduce-solidity-gas-costs-full-guide/)
5. [coinmonks - Solidity — Storage vs Memory vs Calldata](https://medium.com/coinmonks/solidity-storage-vs-memory-vs-calldata-8c7e8c38bce)
6. [docs.soliditylang.org/en/v0.8.21/types.html#data-location](https://docs.soliditylang.org/en/v0.8.21/types.html#data-location)
7. [coinmonks - Optimizing your Solidity contract’s gas usage](https://medium.com/coinmonks/optimizing-your-solidity-contracts-gas-usage-9d65334db6c7)
8. Estimate gas cost of a transaction: [https://github.com/ethereum/homestead-guide/blob/master/source/contracts-and-transactions/account-types-gas-and-transactions.rst#example-transaction-cost](https://github.com/ethereum/homestead-guide/blob/master/source/contracts-and-transactions/account-types-gas-and-transactions.rst#example-transaction-cost)
9. [Hacken - Gas Optimization In Solidity: Strategies For Cost-Effective Smart Contracts](https://hacken.io/discover/solidity-gas-optimization/)
10. [https://www.linkedin.com/pulse/optimizing-smart-contract-gas-cost-harold-achiando/](https://www.linkedin.com/pulse/optimizing-smart-contract-gas-cost-harold-achiando/)
