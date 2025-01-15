---
layout: post
title:  RareSkills Solidity Interview Answers - Hard
date:   2024-03-04
lang: en
locale: en-GB
categories: blockchain blockchainBestOf ethereum solidity
tags: ethereum solidity interview security gas
description: Solidity Interview questions - Hard, answers from the article - Solidity Interview Questions- by RareSkills.
image: /assets/article/blockchain/ethereum/solidity/solidity_logo.svg
isMath: true
---

This article presents the list of **Hard** questions with their answers related to the article [Solidity Interview Questions](https://www.rareskills.io/post/solidity-interview-questions) by RareSkills.

For the levels medium and advanced, you can see [my first](https://rya-sge.github.io/access-denied/2024/02/14/solidity-interview-question-rareskills/) and [third](https://rya-sge.github.io/access-denied/2024/05/06/solidity-interview-question-rareskills-advanced/) articles.

According to the article, all questions can be answered in three sentences or less.

The answers here are more complete than necessary in order to explain in details the topics.

[TOC]



## Defi

### Compound

> What is the kink parameter in the Compound DeFi formula?

The kink parameter is a point limit for the utilization rate. If this limit is exceedeed, the interest rate increases more rapidly.

In the code, I suppose it is stored in the variable [borrowKink](https://github.com/compound-finance/comet/blob/22cf923b6263177555272dde8b0791703895517d/contracts/Comet.sol#L49).

The corresponding term for *AAVE V3* is “optimal utilization".

For more details on *Compound*, see my article [Compound V2 Overview](https://rya-sge.github.io/access-denied/2024/08/27/compound-protocol-v2/)

Reference: [docs.compound.finance/interest-rates/](https://docs.compound.finance/interest-rates/), [RareSkills - Compound V3 Interest Per Second](https://www.rareskills.io/post/compound-finance-interest-rate-model)

### Uniswap v3

> How does Uniswap V3 determine the boundaries of liquidity intervals?

When a position is created, the liquidity provider must choose the lower and upper tick that will represent their position's borders.

Reference: [docs.uniswap.org/concepts/protocol/concentrated-liquidity#ticks](https://docs.uniswap.org/concepts/protocol/concentrated-liquidity#ticks)

### Risk-free rate

> What is the risk-free rate?

The risk-free rate of return is the interest rate an investor can expect to earn on an investment that carries zero risk

Reference: [CFI - Risk-Free Rate](https://corporatefinanceinstitute.com/resources/valuation/risk-free-rate/#:~:text=The%20risk-free%20rate%20of,investment%20an%20investor%20can%20make).

### Fixed point arithmetic

> How does fixed point arithmetic represent numbers?

Fixed-point represent fractional (non-integer) numbers by using a part of their allocated bits to store the fractional part. The separation between the integer and the fractional part is called a **binary points** and it is similar to the decimal point.

For example, if you take an uint256, you have 256 bits at your disposition. You can decide to store the integer part in the first 128 bits and the decimal part in the other 128 bits.

A notation to indicate where is placed the binary point is the `Q` notation. 

Since Solidity and the EVM does not support nativaly decimal/floating numbers, using fixed point arithmetic can be an interesting solution.

For example, Uniswapv3 uses the `Q` notation with 96 bits inside their library `FixedPoint96`, see [github.com/Uniswap/v3-core - FixedPoint96.sol](https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/FixedPoint96.sol) and [A primer on Uniswap v3 Math](https://blog.uniswap.org/uniswap-v3-math-primer).

It seems that Compound uses also the fixed-point representation since they have a library for storing fixed-precision decimals, see [ExponentialNoError.sol](https://github.com/compound-finance/compound-protocol/blob/a3214f67b73310d547e00fc578e8355911c9d376/contracts/ExponentialNoError.sol).

Reference:

- [Q (number format)](https://en.wikipedia.org/wiki/Q_(number_format))
- [What fixed or float point math libraries are available in Solidity?](https://ethereum.stackexchange.com/questions/83785/what-fixed-or-float-point-math-libraries-are-available-in-solidity)
- [What's the point of `fixed point`?](https://vanhunteradams.com/FixedPoint/FixedPoint.html#What's-the-point-of-fixed-point?)

## Gas

### returndatasize vs push0

> Prior to the Shanghai upgrade, under what circumstances is returndatasize() more efficient than push zero?

Push0 was introduced with the Shanghai upgrade and the [eip-3855](https://eips.ethereum.org/EIPS/eip-3855 ) and I don't manage to find situation where `returndatasize()` could be more efficient.

As a reminder,  `PUSH0` It is an opcode with perform only one job: **to push the constant value ZERO onto the stack**.

Prior to this new opcode, there were several different ways to try to push zero on the stack.

One of the "optimized" alternative was to use `RETURNDATASIZE`.

This operations returns ZERO until your contract has called another contract and the return / revert data was at least 1 byte long at which point it’ll return the length in bytes of that returned data.

It was more optimized that the two traditionals operations used:

-  **PUSH1 00:** using the PUSH1 opcode to push zeroes onto the stack => encoded as two bytes / cost 3 gas

- Using **multiple DUP instructions** to duplicate zeroes and put them on the stack, etc => not an optimized choice since it is increased the contract code size
- Reference
  - [Constant Gas Function Dispatchers in the EVM](https://philogy.github.io/posts/selector-switches/)
  - [PUSH0 opcode: A significant update in the latest solidity version 0.8.20](https://medium.com/coinmonks/push0-opcode-a-significant-update-in-the-latest-solidity-version-0-8-20-ea028668028a#:~:text=PUSH0%20opcode%20is%20actually%20fairly,included%20with%20solidity%20version%200.8)
  - [eip-3855](https://eips.ethereum.org/EIPS/eip-3855 )

### Function name

>  How can the name of a function affect its gas cost, if at all?

The EVM uses a jump table for function calls, and function selectors with lesser hexadecimal order are sorted first over selectors with higher hex order. 

- number of functions <= 4

With a smart contract, which has less or equal four functions, the EVM uses a linear search to find a function. Thus, it is more optimized to put the functions heavily used in first inside the jump table.

- number of functions > 4

If there are more than 4 functions, the EVM will use a binary search to search in the table. A *Binary search* begins by comparing an element in the middle of the array with the target value. In this case, I am not really sure that it is really useful to put the most functions used firstly.

Reference: [rareskills.io/post/gas-optimization#viewer-248d5](https://www.rareskills.io/post/gas-optimization#viewer-248d5)

### Equality comparisons

> Why is strict inequality comparisons more gas efficient than ≤ or ≥? What extra opcode(s) are added?

It is because the EVM  does not have an opcode to represent directly `≤` or `≥`

As a result, the compiler will sometimes change `a ≥ b` for  `!(a < b)` which result in additional opcodes, in this case the opcode [NOT]( https://ethervm.io/#19).

Reference: [rareskills.io/post/gas-optimization#viewer-7b77t](https://www.rareskills.io/post/gas-optimization#viewer-7b77t)

### Gasless transaction

> How can a transaction be executed without a user paying for gas?

You have three main methods to transfer the gas payment to a third party :

1) With meta transaction ( [ERC-2771](https://eips.ethereum.org/EIPS/eip-2771))

This methods implies to implement the interface in your smart contract. OpenZeppelin offers this in their library, see [OpenZeppelin - metatx](https://github.com/OpenZeppelin/openzeppelin-contracts/tree/master/contracts/metatx).

In this situation, another address (=sender) can submit the transaction on-chain on behalf of the original user.

2. With signature, e.g. permit for ERC-20 token

The user signs a message allowing the transaction (e.g. transfer tokens) and send the signature to the third-party. Then the thirds party submits the signature on-chain to the smart contract.

OpenZeppelin offers an implementation to use it with ERC-20, see [OpenZeppelin - Permit](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC20Permit.sol)

3. With Account Abstraction ([ERC-4337](https://eips.ethereum.org/EIPS/eip-4337))

This method is independant from the smart contract since it is managed directly to the wallet level.

###  Vanity addresses

>  Under what circumstances do vanity addresses (leading zero addresses) save gas?

If the address is used as an argument of a function, an address with more zero will cost less gas because there are more zero in the calldata.

Reference: [RareSkills - Use vanity addresses](https://www.rareskills.io/post/gas-optimization#viewer-f970n)

### Access list transaction

> What is an access list transaction?

An Ethereum access list transaction enables saving gas on cross-contract calls by declaring in advance which contract and storage slots will be accessed.  This is defined in the [EIP 2930](https://eips.ethereum.org/EIPS/eip-2930). According to [RareSkills](https://www.rareskills.io/post/eip-2930-optional-access-list-ethereum), up to 100 gas can be saved per accessed storage slot.

You can generate an access list transaction to include in your transaction by calling the JSON-RPC function `eth_createAccessList`.

References: [RareSkills - EIP-2930 - Ethereum access list](https://www.rareskills.io/post/eip-2930-optional-access-list-ethereum), [Infura - Optimizing Ethereum Transactions with eth_createAccessList](https://www.infura.io/blog/post/optimizing-ethereum-transactions-with-eth_createaccesslist)

### Storage slot

> How many storage slots does this use? uint64[] x = [1,2,3,4,5]? Does it differ from memory?

You will have one storage slot to store the length of the array, here `5`.

For the rest, my guess is that the different values are packed together. Since values are `uint64`, you can pack the 4 first values in a slot, and the last value(5) in a second slot.

[Reference](https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html#layout-of-state-variables-in-storage): *"Multiple, contiguous items that need less than 32 bytes are packed into a single storage slot if possible"*

Thus, we will have **3 slots used**.

Remark: since it a dynamic array, the location of the data inside the array are computed with the hash of the slot array declaration where the length is stored:`keccak256(abi.encode(ARRAY_SLOT_DECLARATION))`

References:

- [docs.soliditylang.org - Layout of State Variables in Storage](https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html#layout-of-state-variables-in-storage)
- [Understanding Solidity’s Storage Layout And How To Access State Variables](https://medium.com/@flores.eugenio03/exploring-the-storage-layout-in-solidity-and-how-to-access-state-variables-bf2cbc6f8018#:~:text=Thinking%20of%20storage%20as%20an,fixed%20length%20of%2032%20bytes.&text=State%20variables%20are%20stored%20according,a%20value%20or%20dynamic%20type.)

## Proxy

If you want to build a contract for a proxy architecture, I made a summary of the most important points to think about: [Programming proxy contracts with OpenZeppelin - Summary](https://rya-sge.github.io/access-denied/2022/10/31/proxy-contract-summary/)

### EIP-1967 

> a) How does EIP1967 pick the storage slots, 
>
> b) how many are there, 
>
> c) and what do they represent?

The [EIP-1967](https://eips.ethereum.org/EIPS/eip-1967) defines a consistent location where proxies store the address of the logic contract they delegate to, as well as other proxy-specific information.

**Question A**

Storage slots are computed by hashing with `keccak256`  with a defined string

- They are chosen in such a way so they are guaranteed to not clash with  state variables allocated by the compiler, since they depend on the hash of a string that does not start with a storage index. 
- Furthermore, a `-1` offset is added so the preimage of the hash cannot be known, further reducing the chances of a possible attack. As a result, there is no way a contract can plug something into keccak256 to derive a storage slot that clashes with them.

**Question b**

There are three main storages slots ad one supplementary in the reference implementation (rollback).

**Question C**

They represent several critical variables related to the proxy architecture

- Logic

Storage slot: `0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc`

Obtained: `bytes32(uint256(keccak256('eip1967.proxy.implementation')) - 1))`

- Beacon contract address                

Storage slot: `0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50`

Obtained: `bytes32(uint256(keccak256('eip1967.proxy.beacon')) - 1)`

- Admin address

Storage slot: `0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103`

Obtained: `bytes32(uint256(keccak256('eip1967.proxy.admin')) - 1)`

- rollback

Storage slot: `0x4910fdfa16fed3260ed0e7147f7cc6da11a60208b5b9406d12a635614ffd9143` 

Obtained: `bytes32(uint256(keccak256('eip1967.proxy.rollback')) - 1)`



Reference: [eip-1967](https://eips.ethereum.org/EIPS/eip-1967), [EIP 1967 Storage Slots for Proxies](https://www.rareskills.io/post/erc1967)

> If a proxy calls an implementation, and the implementation self-destructs in the function that gets called, what happens?

Since the context is transmitted to the implementation, the `self destruct` will take effect on the proxy.

The behavior changes with the [Cancun upgrade](https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/cancun.md), see [EIP-6780](https://eips.ethereum.org/EIPS/eip-6780)

- Before Cancun upgrade

The proxy will be destructed and the balance contract(native token, e.g. ether) will be transmitted to the specified address. 

- After Cancun upgrade

Only the balance contract(native token, e.g. ether) will be transmitted to the specified address since `self destruct`can not longer destruct the contract bytecode.

### Beacon

> What is a beacon in the context of proxies?

The beacon keeps the logic/implementation address for multiple proxies in a single location.

It is allow the upgrade of multiple proxies by modifying a single storage slot. 

A beacon contract MUST implement the function `implementation to return the logic address.

```solidity
function implementation() returns (address)
```

Reference: [EIP-1967](https://eips.ethereum.org/EIPS/eip-1967#beacon-contract-address)

### Metaproxy

> What is the metaproxy standard?

This standard, defines in the [ERC-3448](https://eips.ethereum.org/EIPS/eip-3448), describes a minimal bytecode implementation for creating proxy contracts with immutable metadata attached to the bytecode.

References: [ERC-3448](https://eips.ethereum.org/EIPS/eip-3448), [rareskills.io - EIP-3448 MetaProxy Standard: Minimal Proxy with support for immutable metadata](https://www.rareskills.io/post/erc-3448-metaproxy-clone)

Contract example: [https://etherscan.io/address/0xfd7eea107df33d9322c05b8956aed4a5697595b8#code](https://etherscan.io/address/0xfd7eea107df33d9322c05b8956aed4a5697595b8#code)

### Delegatecall

> If a user calls a proxy makes a delegatecall to A, and A makes a regular call to B, 
>
> A. from A's perspective, who is msg.sender? 
>
> B. from B's perspective, who is msg.sender? 
>
> C. From the proxy's perspective, who is msg.sender?

Flow: User => proxy ==> A => B where

`=>` is a regular call and `==>` is a `delegatecall`

**Question A**

From A perspective, `msg.sender` is the original user since A  inherits from the context of the proxy through delegatecall.

See [blainemalone - status](https://twitter.com/blainemalone/status/1586744968546340864)

**Question B**

Since it is a regular call, `msg.sender` is the proxy, not the implementation contract.

If A makes a delegateCall to B, the context is A and it is why it can be dangerous if the contract `self destruct`.

Reference: [openzeppelin.com - Potentially Unsafe Operations](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#potentially-unsafe-operations)

**Question C**

From the proxy's perspective, `msg.sender` is the user

See [blainemalone - status](https://twitter.com/blainemalone/status/1586744968546340864)



> What can delegatecall be used for besides use in a proxy?

`Delegatecall` is also used by libraries in order to allow different contract to use their code and to perform operation on the caller contract bytecode.

Reference: [docs.soliditylang.org - libraries](https://docs.soliditylang.org/en/v0.8.24/contracts.html#libraries), [halborn.com - DELEGATECALL VULNERABILITIES IN SOLIDITY](https://www.halborn.com/blog/post/delegatecall-vulnerabilities-in-solidity)



> When a contract calls another call via call, delegatecall, or staticcall, how is information passed between them?

- With a call, the execution environment is the called's rutime environment. Therefore `msg.sender`is the contract caller and `msg.value`is the value passed in the call.

- `STATICCALL` works pretty similar with a call, but the call can only perform a read operation on the contract called. Thus, it takes only 6 arguments  and the "value" argument is not included and taken to be zero, as defined in [EIP-214](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-214.md)

- With `delgatecall`, the execution environment is the caller’s runtime environment, all the context is transmitted to the contract called, included the value of `msg.sender` and `msg.value`



References:

- [RareSkills - Solidity Staticcall EIP 214](https://www.rareskills.io/post/solidity-staticcall)
- [Intro to Smart Contract Security Audits - Delegatecall (1)](https://slowmist.medium.com/c-delegatecall-i-c55c911ec2d0)
- [Learn Solidity lesson 34. Call, staticcall and delegatecall](https://medium.com/coinmonks/call-staticcall-and-delegatecall-1f0e1853340)
- [In "msg.sender.call.value(msg.value)", where is msg.value taken from?](https://ethereum.stackexchange.com/questions/77957/in-msg-sender-call-valuemsg-value-where-is-msg-value-taken-from)
- [How are delegatecall and staticcall in Solidity different?](https://www.educative.io/answers/how-are-delegatecall-and-staticcall-in-solidity-different)



## Security

### Inflation attack

> What is an inflation attack in ERC4626

An inflation attack in the context of ERC-4626 vault consists to manipulate the exchange rate in order to reduce or dilute the value of other's user deposit.

This is done by typically exploiting the rounding performed during the computation of the user's share during its deposit.

For example, a possible method is  to inflate the denominator used to compute the shares amount just before a user's deposit through a front-running.

With this formula to compute the price
$$
UserSharesAmount = (totalShares * userDepositAmount)  /  asset.balanceOf(address(this))
$$
When a user want to perform a deposit, an attacker can reduce the amount of shares give to this user if he manages to have the following equality where:
$$
userDepositAmount ==  asset.balanceOf(address(this) + 1
$$


Thus, in the equation, since the integers are rounded down (0.5 is rounded to 0), the user will receive 0 share. If we replace by variable name.
$$
x = totalShares * userDepositAmount
$$
We have:
$$
UserSharesAmount = x  /  (x + 1) = 0
$$


References:

[Overview of the Inflation Attack](https://mixbytes.io/blog/overview-of-the-inflation-attack)

### ecrecover

> What is a common vulnerability with ecrecover?

 `ecrecover` is an opcode to recover an address  from an elliptic curve signature or return zero on error. But this opcode suffers from a vulnerability allowing malleable (non-unique) signature.

For every set of parameters `{r, s, v}` used to create a signature, another distinct set `{r', s', v'}` results in an equivalent signature.

This is because the elliptic curve is symmetric, and for each point (x, y) on the curve, there's a corresponding point (x, -y) that maintains the same relationship.

The OpenZeppelin library fixes this issue by adding the following checks on the values `s` and  `v`

>  this function rejects them by requiring the `s` value to be in the lower half order, and the `v` value to be either 27 or 28.

As indicated in the solidity documentation

- `r` = first 32 bytes of signature
- `s` = second 32 bytes of signature
- `v` = final 1 byte of signature

References:

- [github.com/OpenZeppelin - cryptography/ECDSA.sol#L39](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.8.2/contracts/utils/cryptography/ECDSA.sol#L39)
- [docs.soliditylang.org - mathematical-and-cryptographic-functions](https://docs.soliditylang.org/en/latest/units-and-global-variables.html#mathematical-and-cryptographic-functions)
- [scsfg.io#signature-malleability](https://scsfg.io/hackers/signature-attacks/#signature-malleability)
- [github.com/obheda12/#signature-malleability](https://github.com/obheda12/Solidity-Security-Compendium/blob/main/days/day12.md#signature-malleability)

### msg.value - loop

> What is the danger of putting msg.value inside of a loop?

You will take into account the amount transfered n times where n is the number of iteration inside the loop, while the real amount transfered is only once. 

Basically you will have :

Amount accounting = `n * msg.value` 

Amount send in reality = `msg.value`

This vulnerability is often seen with multicalls since these calls enable a user to submit a list of transactions in only one transaction to reduce gas fees. Thus, the same value of `msg.value` is used in all the different calls while looping through the functions to execute, potentially enabling the user to double spend.

This was the root cause of the [Opyn Hack](https://peckshield.medium.com/opyn-hacks-root-cause-analysis-c65f3fe249db) => *However, as we mentioned earlier, the `_exercise()` function could be invoked multiple times in the loop. This leads to the same `msg.value` amount of ETH would be re-used in the second or further `_exercise()` calls in the same transaction. "*

Reference: [RareSkill - Smart Contract Security - msg.value in a loop](https://www.rareskills.io/post/smart-contract-security), [Opyn Hack](https://peckshield.medium.com/opyn-hacks-root-cause-analysis-c65f3fe249db)

### Governance vote

>  Why is it necessary to take a snapshot of balances before conducting a governance vote?

If there is no snapshot of balance, an attacker can vote a first time, then send theses tokens to others addresses in their control and vote again.

Another scenario is a token holder votes, then sell its tokens and the new holder can also vote.

Solution: 

To prevent this attack, [ERC20 Snapshot](https://www.rareskills.io/post/erc20-snapshot) or [ERC20 Votes](https://www.rareskills.io/post/erc20-votes-erc5805-and-erc6372) should be used. By snapshotting a point of time in the past, the current token balances cannot be manipulated to gain illicit voting power.

However, using an ERC20 token with a snapshot or vote capability doesn’t fully solve the problem if someone can take a flashloan to temporarily increase their balance, then take a snapshot of their balance in the same transaction. If that snapshot is used for voting, they will have an unreasonably large amount of votes at their disposal.

Reference: [RareSkill - Smart Contract Security - DoubleVoting](https://www.rareskills.io/post/smart-contract-security#Double%20voting)

### ERC20 approval frontrunning

> What is an ERC20 approval frontrunning attack?

Imagine you have approve a defined amount to a malicious user.

For x reason, you want to increase this amount before it has been spending.

Thus, you call a new time the function approve with the new amount.

In this case, this second transaction can be front-run by the malicious user to spend all approved tokens before the new allowance.

A common solution is to add the functions `increaseAlllowance` and `decreaseAllowance` but it turned out to be rather negative because it has been used for phising attack since these functions are not part of the ERC-20 interface and are not always detected by wallets.

Moreover, an approval front-run attack has never been observed in the nature, see [banteg status](https://twitter.com/bantg/status/1699774038418346108)

It is now **recommended** to put the allowance to zero before setting a new one.

Reference: [RareSkill - Smart Contract Security - Frontrunning](https://www.rareskills.io/post/smart-contract-security), [docs.google.com - ERC20 API: An Attack Vector on the Approve/TransferFrom Methods](https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit?pli=1#heading=h.m9fhqynw2xvt), [github.com/OpenZeppelin/issues/4583](https://github.com/OpenZeppelin/openzeppelin-contracts/issues/4583)

## Solidity Misc

### Event

>  How many arguments can a solidity event have?

Events are treated as functions so they have a limit of **17 arguments**.

In the [solidity GitHub code](https://github.com/ethereum/solidity/blob/85b0cfea9a232b10f88a8eca6cdb132706bac5e5/libsolidity/codegen/ContractCompiler.cpp#L490), you can see there is a stack limit of 17

```solidity
if (stackLayout.size() > 17)
		BOOST_THROW_EXCEPTION(
			CompilerError() <<
			errinfo_sourceLocation(_function.location()) <<
			errinfo_comment("Stack too deep, try removing local variables.")
		);
```

Other references: [reddit.com - Event limitation of arguments](https://www.reddit.com/r/ethdev/comments/8627rz/event_limitation_of_arguments/), [What are limitations of Event arguments?](https://ethereum.stackexchange.com/questions/43459/what-are-limitations-of-event-arguments)

> What is an anonymous Solidity event

In the case of an anonymous event, the first topic no longer refers to the event signature. Then it can be used to declare events with 4 indexed parameters instead of the limit of three.

An anonymous event is declared with the **anonymous** modifier,  which must be placed after the parameter declaration.

**Example**

```solidity
event NotMe(address indexed _to, address indexed _from, address indexed _spender, string indexed _message) anonymous;
```

Reference: [Learn Solidity lesson 27. Events](https://medium.com/coinmonks/learn-solidity-lesson-27-events-f47070b55851)

### Functions

> Under what circumstances can a function receive a mapping as an argument?

Mappings can only have a data location of `storage`. Therefore, it is only possible if the function is declared as `internal and therefore not publicly visible. In this case, you can only pass a storage pointer to a map

References: 

- [docs.soliditylang - mapping-types](https://docs.soliditylang.org/en/v0.8.24/types.html#mapping-types)
- [ethereum.stackexchange - Solidity function that accepts mapping as input](https://ethereum.stackexchange.com/questions/12355/solidity-function-that-accepts-mapping-as-input)
- [ethereum.stackexchange - In Solidity, can you declare a mapping variable inside function?](https://stackoverflow.com/questions/72567551/in-solidity-can-you-declare-a-mapping-variable-inside-function)

> How many arguments can a solidity function have?

Functions have a limit of **17 arguments**. Otherwise, you will have the errors *Stack too deep, try removing local variables* during the compilation.

To bypass this limit, it exists several tricks : use internal functions or struct, block scoping or even parsing msg.data, see [soliditydeveloper - Stack Too Deep -](https://soliditydeveloper.com/stacktoodeep)

In the [Solidity Github](https://github.com/ethereum/solidity/blob/85b0cfea9a232b10f88a8eca6cdb132706bac5e5/libsolidity/codegen/ContractCompiler.cpp#L490), you can see there is a stack limit of 17

```solidity
if (stackLayout.size() > 17)
		BOOST_THROW_EXCEPTION(
			CompilerError() <<
			errinfo_sourceLocation(_function.location()) <<
			errinfo_comment("Stack too deep, try removing local variables.")
		);
```

References: [docs.soliditylang.org#storage-memory-and-the-stack](https://docs.soliditylang.org/en/v0.8.24/introduction-to-smart-contracts.html#storage-memory-and-the-stack)

> In solidity, without assembly, how do you get the function selector of the calldata?

The function selector is obtained by hashing the signature function with `Keccak-256`, then by keeping only the first four bytes of the result.

Here a solidity example

```solidity
function getSelector(string calldata _func) external pure returns (bytes4) {
	return bytes4(keccak256(bytes(_func)));
}
```

References:

- [Solidity by Example - Function Selector](https://solidity-by-example.org/function-selector/)
- [Function Selectors in Solidity: Understanding and Working with Them](https://medium.com/coinmonks/function-selectors-in-solidity-understanding-and-working-with-them-25e07755e976)

### Try catch

> If a try catch makes a call to a contract that does not revert, but a revert happens inside the try block, what happens?

The revert will not be catch by the `try catch`, the transaction will be reverted.

`try / catch` can only catch errors from external function calls and contract creation.

Reference: [docs.soliditylang.org#try-catch](https://docs.soliditylang.org/en/latest/control-structures.html#try-catch), [solidity-by-example.org/try-catch/](https://solidity-by-example.org/try-catch/)

### bytes1[]

> What is the difference between bytes and bytes1[] in memory?

From the [Solidity doc](https://docs.soliditylang.org/en/latest/types.html#fixed-size-byte-arrays)

"The type bytes1[] is an array of bytes, but due to padding rules, it wastes 31 bytes of space for each element (except in storage). It is better to use the bytes type instead. 

Prior to version 0.8. 0, byte used to be an alias for bytes1"

### Sazbo

> How much is one Sazbo of ether?

1 szabo == 1e12 wei == 1e^-6 ether

In the other sens

1 Ether == 1.000.000  == 1e6 Szabo

1 Ether = 1.000.000.000.000.000.000 wei == 1e18 wei

Reference: [bitdegree.org - ether-units](https://www.bitdegree.org/learn/solidity-variables#ether-units)

Warning: 

"The `finney` and `szabo` denominations were removed from Solidity since the version 0.7.0 because they are rarely used and do not make the actual amount readily visible. Instead, explicit values like `1e20` or the very common `gwei` can be used". See [github.com - Solidity v0.7.0 Breaking Changes](https://github.com/ethereum/solidity/blob/breaking/docs/070-breaking-changes.rst#expressions)

## EVM / Assembly

> What opcode accomplishes address(this).balance?

The concerned opcode is `SELFBALANCE` which is cheaper than `BALANCE`.

`	SELFBALANCE`=> 5 gas cost

`BALANCE` => 100 gas cost (if *warm access*) or 2600 (*cold access*)

**Reference:**

- [selfBalance() and address(this).balance gas cost](https://ethereum.stackexchange.com/questions/142547/selfbalance-and-addressthis-balance-gas-cost)

- [ethervm.io/#47 - selfbalance](https://ethervm.io/#47)

- [ethervm.io/#31 - balance](https://ethervm.io/#31)

- [github.com/wolfl - gas.md#a5-balance-extcodesize-extcodehash](https://github.com/wolflo/evm-opcodes/blob/main/gas.md#a5-balance-extcodesize-extcodehash)

> How can you halt an execution with the mload opcode?

I am lost for this question.

You can maybe generate an error by manipulating the stack or memory ?

```solidity
assembly {
    mstore(0x80, add(mload(0x40), 1))
}
```

Reference: [Exploring Assembly Errors in Solidity](https://medium.com/@solidity101/exploring-assembly-errors-in-solidity-8a6e399fdaf1)

> Why does the compiler insert the INVALID op code into Solidity contracts?

a. The INVALID opcode (`0xfe`) is generally present to separate the smart contract code from the metadata, which are appended to the end of the initcode.

b. Another reason is if an invalid opcode is met during the compilation.

There is 16*16=256 combination of different opcodes (00 to FF) but only  part of them are assigned.

As a result, you can have INVALID opcode if an invalid opcode is met during the compilation from Solidity to EVM bytecode. But it is a very rare scenario.

References

- [rareskills.io/post/solidity-metadata#](https://www.rareskills.io/post/solidity-metadata#)

- [Reversing and Debugging EVM Smart contracts : 5 Instructions to end/abort the Execution (Part 4)](https://trustchain.medium.com/reversing-and-debugging-evm-the-end-of-time-part-4-3eafe5b0511a)

### Custom error

> What is the difference between how a custom error and a require with error string is encoded at the EVM level?

Both of them write to memory, then invoke the REVERT opcode pointing to that region in memory, which is the error message. The difference comes from this error message.

=> In the `require` case, the message is a string. 

=> For `revert` with custom error, it is the 4 byte selector, and the abi-encoded args if applicable.

The 4 byte selector of a custom error can be obtained with the `CustomError.selector field`

Gas cost:

"It is sometimes claimed that revert statements are more gas efficient than require statements, but there is nuance to this. The gas savings comes from 4 byte custom error selector being smaller than most strings. But if a custom error takes args, it might write a lot of data".

Reference: [RareSkills_io - Threads](https://twitter.com/RareSkills_io/status/1644716767737180160), [soliditylang.org - Custom Errors in Solidity](https://soliditylang.org/blog/2021/04/21/custom-errors/)

### contract bytecodes 6080604052

> Why do a significant number of contract bytecodes begin with 6080604052? What does that bytecode sequence do?

This sequence stores the value `0x80` to the address `0x40` in memory.

In Solidity, the free memory which can be used to store data begins at address `0x80` and this suit of instruction stores the emplacement where this free memory begins.

**Details:**

 `0x60` is the opcode of `PUSH1`.

The next byte is the argument for this instruction, so `0x80`.

This instruction pushes `0x80` on the stack

Then, we have a second instruction `PUSH1` but with the argument `0x40`.

After this second instruction, the stack looks like:

```
**| 0x40 | 0x80 |**
```

Finally, we have `0x52`, which is the opcode for `MSTORE`.

`MSTORE` takes 2 arguments : `Stack(0)` and `Stack(1`. Since the stack works as a LIFO (Last In, First out), `MSTORE` stores in memory the value of `Stack(0)` in the `Stack(1)` slot.

As a result, the EVM stores **0x80** in the **0x40** address in memory.

In summary, we have the following instructions:

```assembly
PUSH1 0x80
PUSH1 0x40
MSTORE
```

References:

- [A deep-dive into Solidity – contract creation and the init code](https://leftasexercise.com/2021/09/05/a-deep-dive-into-solidity-contract-creation-and-the-init-code/)
- [docs.soliditylang.org - Layout in Memory](https://docs.soliditylang.org/en/v0.8.24/internals/layout_in_memory.html)
- [Reversing and debugging EVM Smart contracts: First steps in assembly (part 1)](https://trustchain.medium.com/reversing-and-debugging-evm-smart-contracts-392fdadef32d)

### Relationship between variable scope and stack depth

> What is the relationship between variable scope and stack depth?

`Stack too depth` concerns variable declared locally and computations.

Thus, you can resolve the *stack too depth* by using `internal function` or the use of block scoping.

Reference: [soliditydeveloper.com - Stack Too Deep](https://soliditydeveloper.com/stacktoodeep)

### Calldata of a function

> Describe the calldata of a function that takes a dynamic length array of uint128 when uint128[1,2,3,4] is passed as an argument

**uint128[1,2,3,4]**

If I use the tool [cast](https://book.getfoundry.sh/reference/cast/cast-calldata) from Foundry to generate calldata from a function `test`

```bash
cast calldata "test(uint128[])" [1,2,3,4]
```

The result is:

```
0xd66cd0db000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004
```

We can then analyze the different values:

| Value      | Description                                                  |
| ---------- | ------------------------------------------------------------ |
| 0xd66cd0db | 4 bytes selector from the function, `test`in my example      |
| <0>2       | Not sure, but my guess is this is the location of the data part ("offset)") since it is a dynamic type |
| <0>4       | Array size                                                   |
| <0>1       | Param 1                                                      |
| <0>2       | Param 2                                                      |
| <0>3       | Param 3                                                      |
| <0>4       | Param 4                                                      |

The numbers inside the array are padded with `0` to fit a 32 bytes / 256 bits numbers



**uint256[]**

We can also try with uint256[]

```bash
cast calldata "test(uint256[])" [1,2,3,4]
```

The result is exactly the same as for the `uint128[]`

```
0xd66cd0db000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004
```

We can then analyze the different values, and we observe that they are the same that for uint128[]

References: [docs.soliditylang - abi-spec.html#examples](https://docs.soliditylang.org/en/v0.8.24/abi-spec.html#examples), [ABI Encoding and EVM Calldata demystified](https://r4bbit.substack.com/p/abi-encoding-and-evm-calldata)

## Blockchain

### Ethereum addres

>  How is an Ethereum address derived?

Ethereum addresses  are derived from public keys or contracts using the one-way hash function `Keccak-256 `and by keeping only the last 20 bytes.

The whole process to obtain an Ethereum address, is described in the excellent book [Mastering Ethereum - Andreas M. Antonopoulos, Gavin Wood](https://github.com/ethereumbook/ethereumbook/blob/develop/04keys-addresses.asciidoc#ethereum-addresses)

a) From a private key K

```
k = f8f8a2f43c8376ccb0871305060d7b27b0554d2cc72bccf41b2705608452f315
```

b) You compute the public key K where
$$
K = k  * G
$$


- G is the generator point specified in the secp256k1 standard
- K is a point on the Elliptic Curve specified by a coordinate (x, y)

```
K = 6e145ccef1033dea239875dd00dfb4fee6e3348b84985c92f103444683bae07b83b5c38e5e...
```

c) On K, you apply ` Keccak-256` to compute the hash

```
Keccak256(K) = 2a5bc342ed616b5ba5732269001d3f1ef827552ae1114027bd3ecf1f086ba0f9
```

d) Then you only keep the last 20 bytes (40 character hexa), which gives the Ethereum address.

```
001d3f1ef827552ae1114027bd3ecf1f086ba0f9
```

Generally, you will append in front the prefix `0x` to indicate the hexa decimal format, which gives a 42-character hexadecimal address 

```
0x001d3f1ef827552ae1114027bd3ecf1f086ba0f9
```

References:

- [github.com/ethereumbook#ethereum-addresses](https://github.com/ethereumbook/ethereumbook/blob/develop/04keys-addresses.asciidoc#ethereum-addresses)
- [github.com/ethereumbook#generating-a-public-key](https://github.com/ethereumbook/ethereumbook/blob/develop/04keys-addresses.asciidoc#generating-a-public-key)
- [etherscan - What is an ethereum address](https://info.etherscan.com/what-is-an-ethereum-address/)

### Optimistic rollup and a zk-rollup

> What is the difference between an optimistic rollup and a zk-rollup?

Optimistic rollups consider all transactions are valid unless proven otherwise. An actor of the network (e.g a validator node) can disput a transactions and if the fraud is confirmed, the malicious actor will be   penalized, generally financially. 

Zero-knowledge rollups (ZK-rollups) employ zero-knowledge proofs (also known as validity proofs) to prove that a transaction is valid, without revealed the content. In general, a proof  takes up less space than the data, which reduces transaction fees. Since claim does need to be disrupted, contrary to optimism rollup, the confirmation/finalization is quicker than with an optimistic rollup.

Reference:

- [My article on Arbitrum](https://rya-sge.github.io/access-denied/2024/01/31/arbitrum-introduction/)

- [Zero-Knowledge vs. Optimistic Rollups Explained: Which One is Better for Blockchain Games?](https://www.immutable.com/blog/zero-knowledge-vs-optimistic-rollups-explained-which-one-is-better-for-blockchain-games).

- [Optimistic vs. Zero-Knowledge Rollups: What’s the Difference?](https://academy.binance.com/en/articles/optimistic-vs-zero-knowledge-rollups-what-s-the-difference)

### Smart contract - Layer2

> Under what circumstances would a smart contract that works on Ethereum not work on Polygon or Optimism? (Assume no dependencies on external contracts)

**Opcode not supported**

A smart contract can not work if one of the opcode present in the contract bytecode is not available in these network. The behavior of some specific opcode can also change between Ethereum and a layer2.

For example, during a short period, the opcode PUSH0 was not available in Optimism and the behavior of PREVRANDAO is not the same on Optimism than on Ethereum,

You have a list of difference for Optimism available on their documentation [docs.optimism - Differences between Ethereum and OP Mainnet](https://docs.optimism.io/chain/differences) and on [rollup.code](https://www.rollup.codes/optimism).

For Polygon PoS, the chain is fully Ethereum equivalent, probably because the excecution layer(Bor) is based on Go Ethereum (Geth). See their [documentation](https://docs.polygon.technology/pos/get-started/building-on-polygon/#smart-contracts)

Regarding Polygon zkEVM, the same issue can appear than for Optimism. As for Optimism, the opcode PUSH0 was not directly available on Polygon zkEVM and has been introduced with the [Dragon Fruit upgrade](https://polygon.technology/blog/polygon-zkevm-dragon-fruit-is-live-on-mainnet).

**Precompiles contract**

Ethereum has nine precompiles contracts, which behave like smart contracts built into the Ethereum protocol.

The behavior of these smart contracts can be different on others EVM compatible chain and layer2. For example, `ecrecover` on `zksync` always return a zero address for the zero digests (see [docs.zksync.io#ecrecover](https://docs.zksync.io/build/developer-reference/differences-with-ethereum.html#ecrecover)).

Reference: [Ethereum precompiled contracts](https://www.rareskills.io/post/solidity-precompiles)

> How can a smart contract change its bytecode without changing its address?

Before the Ethereum's Cancun upgrade (March 2024), it was possible to use the opcode `selfdestruct` to destroy a contract and use `create2` to deploy the contract to the same address. The only requirement is that the contract has to be deployed with `create2` in the first time.

With create2, the address can be pre-computed and it is easier to deploy a bytecode at the same address again.

```
new_address = hash(0xFF, sender, salt, bytecode)
```

Nevertheless, the Ethereum's  [Cancun upgrate](https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/cancun.md) will remove the ability to destruct the smart contract bytecode for SELFDESTRUCT (see [EIP-6780](https://eips.ethereum.org/EIPS/eip-6780)), a part if the opcode is called during the same transaction as the contract creation.

Reference: [OpenZeppelin - Deploying Smart Contracts Using `CREATE2`](https://docs.openzeppelin.com/cli/2.8/deploying-with-create2), [Dark Side of CREATE2 opcode](https://medium.com/coinmonks/dark-side-of-create2-opcode-6b6838a42d71)

## Further reading

You can find different answers to these questions in the following resources

- [github.com/typicalHuman/solidity-interview-questions?tab=readme-ov-file#hard](https://github.com/typicalHuman/solidity-interview-questions?tab=readme-ov-file#hard)

