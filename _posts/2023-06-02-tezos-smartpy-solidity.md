---
layout: post
title: Solidity (Ethereum) vs SmartPy (Tezos)
date: 2023-06-02
last-update: 
locale: en-GB
lang: en
categories: blockchain programmation ethereum solidity
tags: solidity tezos smartpy
image:
description: This articles describes a correspondence table between the smart contract languages Solidity (Ethereum) and SmartPy / Python (Tezos).
isMath: false
---

This articles describes a correspondence table between the smart contract language `Solidity` used for Ethereum with `SmartPy / Python` used to develop smart contracts for the blockchain [Tezos](https://tezos.com/)

>- SmartPy is a solution for developing, testing, and deploying smart  contracts on the Tezos blockchain with the Python syntax.
>
>- *Solidity* is an object-oriented, high-level language for implementing smart contracts for Ethereum and EVM blockchain compatible.



> Warning: the SmartPy syntax used in this article may be outdated since it was written for the Legacy version of [SmartPy](https://legacy.smartpy.io/) 

## Overview

#### Define a contract

*Solidity*

We use the keyword `contract`

```
contract MyEpicGame {}
```

*SmartPy*

Any class inheriting from `sp.Contract` defines a SmartPy *contract*.

```
class A(sp.Contract):
```

#### Class inheritance

*Solidity*

Keyword `is` such as`is ParentContractName`

Example 

```solidity
contract MyEpicGame is ERC721
```

*SmartPy*

`class className(parentClassName)`

Example: 

```python
class B(A)
```

>Note that in SmartPy it is required that the superclass's `__init__` function be called explicitly.

Ref: [https://smartpy.io/manual/syntax/overview](https://smartpy.io/manual/syntax/overview)

#### Library / Module

*Solidity*

Solidity allows to define libraries witht he keyword `library`

```solidity
library Math {
    function sqrt(uint y) internal pure returns (uint z) {
    // Code
    }
}
```

Ref: [https://solidity-by-example.org/library/](https://solidity-by-example.org/library/)

*SmartPy*

A module can be defined with`@sp.module`

Example:

```python
@sp.module
def main():
    class Calculator(sp.Contract):
        def __init__(self):
            self.data.result = 0

        @sp.entrypoint
        def multiply(self, x, y):
            self.data.result = x * y
```

## Variables & Storage

*Solidity*

> There are 3 types of variables in Solidity
>
> - local
>   - declared inside a function
>   - not stored on the blockchain
> - state
>   - declared outside a function
>   - stored on the blockchain
> - global (provides information about the blockchain)

Ref: [https://solidity-by-example.org/variables/](https://solidity-by-example.org/variables/)

*SmartPy*

- Local variable

You can declare a local variable with `sp.local`

```
x = sp.local("x", 0)
```

Local variable values can be accessed to and updated with the **.value** field

- Global variable

SmartPy offers us `self.data`, which corresponds to the storage in Michelson.

Example

```python
def repeat(self, params):
    self.data.storage= params
```

## Type

### General overview

*Solidity*

>Solidity is a statically typed language, which means that the type of each variable (state and local) needs to be specified.

Ref: [https://docs.soliditylang.org/en/v0.8.20/types.html](https://docs.soliditylang.org/en/v0.8.20/types.html)

*SmartPy*

>In SmartPy as in Python you don’t need to specify the types of objects. However the contracts that you write in SmartPy will be compiled to Michelson and Michelson requires types. Therefore SmartPy automatically detects the types of expressions (Type Inference).

#### Number

*Solidity*

`int` / `uint`: Signed and unsigned integers of various sizes. 

Keywords `uint8` to `uint256` in steps of `8` (unsigned of 8 up to 256 bits) and `int8` to `int256`. 

*SmartPy*

Integer: `sp.int`

Unsigned integer: `sp.nat`

**Currency Units**

*Solidity*

we can use the keywords `wei` and `ether`

```solidity
uint public oneWei = 1 wei;
```

```solidity
int public oneEther = 1 ether;
```

Ref: [https://betterprogramming.pub/solidity-tutorial-all-about-ether-units-eaebe55dd4dc](https://betterprogramming.pub/solidity-tutorial-all-about-ether-units-eaebe55dd4dc)

*Smartpy*

`a = sp.tez(1`

```
sp.mutez(1000000)
```

Ref: [https://smartpy.io/docs/manual/syntax/integers-and-mutez](https://smartpy.io/docs/manual/syntax/integers-and-mutez)

#### Other types

*SmartPy* allows to use Pairs, Tuples, Option and have a specific type called Record

- Pairs `(a1, a2)` 

- Tuples

 `sp.tuple[sp.int, sp.string, sp.bool]`.

- Records

`sp.record(a=42, b="abc")`

```python
x = sp.record(a=42, b="abc", c=True)
assert x.a == 42
assert x.b == "abc"
assert x.c == True
```

- Options, Variants

And many others available in the references:

- [https://smartpy.io/manual/syntax/tuples-and-records](https://smartpy.io/manual/syntax/tuples-and-records)
- [https://legacy.smartpy.io/docs/types/records#literals](https://legacy.smartpy.io/docs/types/records#literals)
- [https://smartpy.io/docs/manual/syntax/tuples-and-records](https://smartpy.io/docs/manual/syntax/tuples-and-records)
- [https://smartpy.io/manual/syntax/options-and-variants](https://smartpy.io/manual/syntax/options-and-variants)



## Function visibility

Function available from the outside of the contract

*Solidity* 

`external / public`

*SmartPy*

```
@sp.entry_point
```

>An *entry point* is a method of a contract class that can be called from the outside.

Reference: [https://legacy.smartpy.io/docs/introduction/entrypoints](https://legacy.smartpy.io/docs/introduction/entrypoints)



## Other

### Return a value

*Solidity*

keyword `returns`

Example :

```solidity
function tokenURI(uint256 _tokenId) public returns (string memory) 
```

*SmartPy*

`sp.result(value)`

Reference: [https://smartpy.io/reference.html#_return_values](https://smartpy.io/reference.html#_return_values)

### Constructor

*Solidity*

Use the keyword `constructor`

```solidity
constructor(string[] memory myParam)
```

*SmartPy*

>The `__init__` function can be used to initialize the storage by assigning to fields of `self.data`. 

Example

```python
def __init__(self):
	# Define a value with initial integer 0
    self.init(storage=0)
```

Reference: [https://smartpy.io/manual/syntax/overview](https://smartpy.io/manual/syntax/overview)

### Access control

*Solidity*

```solidity
require(msg.sender == admin);
```

Or if a modifier, for example to verify the ownership with `onlyOwner`

```solidity
myFunction(uint256 value) public onlyOwner
```

*SmartPy*

```
sp.verify(sp.sender == self.data.admin);
```

**Current timestamp**

*Solidity*

```solidity
block.timestamp
```

*SmartPy*

```python
sp.now 
```



## Control flow statement 

#### Switch

*Solidity*

Not available, you have to use the statement `if else`

*SmartPy*

**`<expr>.match_cases(v)`**
Similar to a switch case statement, where `expr` is a variant.

```python
variant_type = sp.TVariant(
    action1 = sp.TNat,
    action2 = sp.TString,
)
variant = sp.variant("action1", 10)with variant.match_cases() as arg:
    with arg.match("action1") as a1:
        # Will be executed
        sp.verify(a1 == 10, 'Expected value to be (10).')
```

Reference: [https://legacy.smartpy.io/docs/types/variants#match-cases](https://legacy.smartpy.io/docs/types/variants#match-cases)

#### Loop

*Solidity*

```
for(uint256 i = 0; i < y; ++i)
```

*SmartPy*

```python
sp.range(x, y, step = 1)
```



## Reference

Here a quick list of the main references

- SmartPy Legacy Edition: [https://legacy.smartpy.io/](https://legacy.smartpy.io/)
- SmartPy - First Steps: [https://tezos.b9lab.com/smartpy/intro](https://tezos.b9lab.com/smartpy/intro)
- Write smart contracts on Tezos with SmartPy: [https://tezos.com/developers/smartpy/](https://tezos.com/developers/smartpy/)
- Smart contract development with SmartPy: [https://opentezos.com/smartpy/](https://opentezos.com/smartpy/)
- Smart contract development with SmartPy: [https://opentezos.com/smartpy/write-contract-smartpy/](https://opentezos.com/smartpy/write-contract-smartpy/)
- Tezos Developers' Handbook: [https://tzapac.notion.site/Tezos-Developers-Handbook-ce244ec152504954a311ce1650d4b8c5](https://tzapac.notion.site/Tezos-Developers-Handbook-ce244ec152504954a311ce1650d4b8c5)
- How to Create, Test and Deploy Tezos Smart Contracts?: [https://www.leewayhertz.com/tezos-smart-contracts/](https://www.leewayhertz.com/tezos-smart-contracts/)

