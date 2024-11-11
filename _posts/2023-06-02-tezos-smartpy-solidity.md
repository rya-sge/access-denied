---
layout: post
title: Solidity (Ethereum) vs SmartPy (Tezos)
date: 2023-06-02
last-update: 
locale: en-GB
lang: en
categories: blockchain ethereum solidity
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
>
> [TOC]
>
> 



## Start

#### Define a contract

*Solidity*

We use the keyword `contract`

```solidity
contract MyEpicGame {}
```

*SmartPy*

Any class inheriting from `sp.Contract` defines a SmartPy *contract*.

```
class A(sp.Contract):
```

Reference: https://smartpy.io/guides/tutorial#summary

#### Class inheritance

*Solidity*

Keyword `is` such as`is ParentContractName`

Example 

```solidity
contract MyEpicGame is ERC721
```

*SmartPy*

The syntax is the following:`class className(parentClassName)`

Example: 

```python
class B(A)
```

>Note that in SmartPy it is required that the superclass's `__init__` function be called explicitly.

Reference: [https://smartpy.io/manual/syntax/overview](https://smartpy.io/manual/syntax/overview)

#### Library / Module

*Solidity*

Solidity allows to define libraries with the keyword `library`

```solidity
library Math {
    function sqrt(uint y) internal pure returns (uint z) {
    // Code
    }
}
```

Reference: [https://solidity-by-example.org/library/](https://solidity-by-example.org/library/)

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

### Constructor

*Solidity*

Use the keyword `constructor`

```solidity
constructor(string[] memory myParam)
```

*SmartPy*

The smart contract constructor is defined with the function  `__init__` , which initialize the storage by assigning to fields of `self.data`. 

Example 1

```python
def __init__(self):
	# Define a value with initial integer 0
    self.init(storage=0)
```

Example 2:

```python
import smartpy as sp

@sp.module
def main():
    class Ducat(sp.Contract):
        def __init__(self, admin):
            self.data.balances = {}
            self.data.admin = admin
```

Here, the init function initialize:

-  `balances` is a [map](https://smartpy.io/manual/syntax/lists-sets-and-maps#maps), which associates a balance to each address. Initially it is empty, indicating that nobody owns any Ducats.

- There is an `admin` address that will special powers, e.g. to mint new Ducat

Reference: [https://smartpy.io/manual/syntax/overview](https://smartpy.io/manual/syntax/overview), [smartpy.io/guides/tutorial#summary](https://smartpy.io/guides/tutorial#summary)

## Variables & Storage

*Solidity*

In solidity, there are 3 types of location for variables: local, state and global. Their location (local, state, global) depends of the place where they are declared or if a specific keyword is used (e.g `memory` and `storage`).

Reference: [https://solidity-by-example.org/variables/](https://solidity-by-example.org/variables/)

*SmartPy*

- Local variable

You can declare a local variable with `sp.local`

```python
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

The type returned is indicated with the keyword `returns`

Example :

```solidity
function tokenURI(uint256 _tokenId) public returns (string memory) 
```

*SmartPy*

`sp.result(value)`

Reference: [https://smartpy.io/reference.html#_return_values](https://smartpy.io/reference.html#_return_values)



### Access control

*Solidity*

You can perform verification with the keywork `require` or with a if and a custom error.

For example, here the contract will generate an error if the transaction sender is not equal to the admin address stored in the contract.

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

### Current timestamp

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

## Key and signatures

*SmartPy*

On Tezos, each tz address is determined by hashing a public key. 

Public keys are of type `sp.key` and can be defined with `sp.key()`. For example, `sp.key("edpkv3w95AcgCWQeoYm5szaEqXX71JkZ261s4wjH1NYRtibX879rDv")`

Reference: [smartpy.io/manual/syntax/keys-and-signatures](https://smartpy.io/manual/syntax/keys-and-signatures)



## Reference

Here a quick list of the main references

- SmartPy Legacy Edition: [https://legacy.smartpy.io/](https://legacy.smartpy.io/)
- SmartPy - First Steps: [https://tezos.b9lab.com/smartpy/intro](https://tezos.b9lab.com/smartpy/intro)
- Write smart contracts on Tezos with SmartPy: [https://tezos.com/developers/smartpy/](https://tezos.com/developers/smartpy/)
- Smart contract development with SmartPy: [https://opentezos.com/smartpy/](https://opentezos.com/smartpy/)
- Smart contract development with SmartPy: [https://opentezos.com/smartpy/write-contract-smartpy/](https://opentezos.com/smartpy/write-contract-smartpy/)
- Tezos Developers' Handbook: [https://tzapac.notion.site/Tezos-Developers-Handbook-ce244ec152504954a311ce1650d4b8c5](https://tzapac.notion.site/Tezos-Developers-Handbook-ce244ec152504954a311ce1650d4b8c5)
- How to Create, Test and Deploy Tezos Smart Contracts?: [https://www.leewayhertz.com/tezos-smart-contracts/](https://www.leewayhertz.com/tezos-smart-contracts/)

