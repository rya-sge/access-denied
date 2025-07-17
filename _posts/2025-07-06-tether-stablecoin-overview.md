---
layout: post
title: "Tether USDT smart contract - Overview"
date: 2025-07-06
lang: en
locale: en-GB
categories: ethereum defi
tags: stablecoin USDT
description: This article analyze the features, architecture, and implications of the Solidity version deployed on Ethereum mainet, especially from a security, centralization, and functional standpoint.
image: /assets/article/blockchain/ethereum/contract-analyse/tether-mainet.svg
isMath: true
---

Tether's USDT is the largest stablecoin in terms of market cap (July 6, 2025). Its Ethereum version has a marketcap of $64b  according to [defilama](https://defillama.com/stablecoins/ethereum).

This article explores the features, structure, and behavior of the USDT smart contract on Ethereum, focusing on security, centralization, and functionality.

USDT operates through a Solidity-based smart contract first deployed on Ethereum in **2017**. While it follows the ERC-20 standard, it includes several extensions to address regulatory and operational needs.

**Key Features of the USDT Smart Contract:**

- **Ownership Controls**: The `Ownable` module allows a designated authority to manage upgrades and token issuance.
- **Blacklist Mechanism**: Specific addresses can be frozen or have funds removed,
- **Pause/Unpause Capability**: Trading and transfers can be paused in critical situations via the `Pausable` feature.
- **Upgradability**: Through the `deprecate()` function, the contract can forward all logic to a newer version
- **Optional Transfer Fees**: A configurable fee structure is implemented, though typically unused.
- **Token Supply Adjustments**: The owner can `issue()` or `redeem()` tokens, allowing the supply to be adjusted in response to off-chain actions.

USDT operates across multiple chains (Ethereum, Tron, Solana, and others), but the original Ethereum contract remains a useful reference for understanding how USDT works.

[TOC]



## Overview

### High-Level Overview

- **Contract Name**: `TetherToken`
- **Deployed**: November 2017
- **Language**: Solidity `^0.4.17`
- **ERC Standard**: Implements ERC20 with custom extensions
- **Design Pattern**: Inherits from multiple base contracts (`Ownable`, `Pausable`, `BlackList`, `StandardToken`)
- **Purpose**: Mintable, burnable stablecoin backed by fiat (off-chain), with owernship controls for upgrades, blacklisting, and pausing.

------

### Key Components and Functionality

#### SafeMath Library

- Prevents integer overflows/underflows.
- Uses `assert()` instead of `require()` (older Solidity style).
- Common best practice for tokens at the time.

------

#### Ownable Contract

- Provides owner-only access control.
- Enables ownership transfer.
- Many sensitive operations gated behind `onlyOwner`.

------

#### ERC20 Implementation

- `Tether` ->`BasicToken` → `StandardToken`
- Custom fee logic added to `transfer` and `transferFrom`
- Implements `allowance`, `approve`, etc.
- Contains **short address attack protection** via `onlyPayloadSize` (now obsolete in modern Solidity).

------

#### Fee Mechanism

- Controlled by:
  - `basisPointsRate`: fee in basis points (1 bp = 0.01%)
  - `maximumFee`: upper cap on fee (hardcoded limits in `setParams`)
- Fees go to the `owner`, not burned.

------

#### Pausable Functionality

- `pause()` and `unpause()` by `owner`
- Disables `transfer`, `transferFrom` when paused.
- Useful for emergency halts.

------

#### Blacklist Mechanism

- `addBlackList`, `removeBlackList`, `destroyBlackFunds`
- Owner can zero out a blacklisted user’s balance and reduce total supply
- **Very powerful**, potentially controversial feature (centralized censorship)

------

#### Upgrade Mechanism

- If `deprecated == true`, calls are forwarded to a new contract at `upgradedAddress`
- At this time, enables seamless transition without forcing users to migrate. Now the proxy architecture is generally preferred.
- `transfer`, `balanceOf`, etc. all redirect to `UpgradedStandardToken`

------

#### Minting & Burning

- `issue(uint amount)` – owner can mint tokens to themselves
- `redeem(uint amount)` – owner can burn their own tokens
- No restrictions on minting other than overflow protections



## Schema

Here an UML with all the contracts and inheritance.

The base contract, which is the final contract deployed on mainet is `TetherToken`

![tether-mainet]({{site.url_complet}}/assets/article/blockchain/ethereum/contract-analyse/tether-mainet.svg)

## List of non-ERC20 functions

Here is the list of external and public functions which are not part of the ERC-20 standard interface.

| Function Signature                               | Description                                      | Emits Event                          | Access Control               | Defined In    |
| ------------------------------------------------ | ------------------------------------------------ | ------------------------------------ | ---------------------------- | ------------- |
| `transferOwnership(address newOwner)`            | Transfers ownership to a new address.            | —                                    | `onlyOwner`                  | `Ownable`     |
| `pause()`                                        | Pauses the contract (disables key functions).    | `Pause()`                            | `onlyOwner`, `whenNotPaused` | `Pausable`    |
| `unpause()`                                      | Unpauses the contract (restores functionality).  | `Unpause()`                          | `onlyOwner`, `whenPaused`    | `Pausable`    |
| `getBlackListStatus(address _maker)`             | Returns whether an address is blacklisted.       | —                                    | None                         | `BlackList`   |
| `getOwner()`                                     | Returns the contract owner.                      | —                                    | None                         | `BlackList`   |
| `addBlackList(address _evilUser)`                | Adds an address to the blacklist.                | `AddedBlackList(address)`            | `onlyOwner`                  | `BlackList`   |
| `removeBlackList(address _clearedUser)`          | Removes an address from the blacklist.           | `RemovedBlackList(address)`          | `onlyOwner`                  | `BlackList`   |
| `destroyBlackFunds(address _blackListedUser)`    | Destroys funds of blacklisted address.           | `DestroyedBlackFunds(address, uint)` | `onlyOwner`                  | `BlackList`   |
| `deprecate(address _upgradedAddress)`            | Marks contract as deprecated & sets new address. | `Deprecate(address)`                 | `onlyOwner`                  | `TetherToken` |
| `issue(uint amount)`                             | Mints new tokens to the owner.                   | `Issue(uint)`                        | `onlyOwner`                  | `TetherToken` |
| `redeem(uint amount)`                            | Burns tokens from owner balance.                 | `Redeem(uint)`                       | `onlyOwner`                  | `TetherToken` |
| `setParams(uint newBasisPoints, uint newMaxFee)` | Updates transfer fee rate and max fee.           | `Params(uint, uint)`                 | `onlyOwner`                  | `TetherToken` |

## Code

USDT is relatively small in term of code size, here a copy of the code:



### Solidity version declaration

```solidity
/**
 *Submitted for verification at Etherscan.io on 2017-11-28
*/

pragma solidity ^0.4.17;

```

### Utility



#### Safemath

- **Purpose**: Prevents overflow/underflow in arithmetic operations (`add`, `sub`, `mul`, `div`).
- **Usage**: Standard Solidity library for safe math; used by other token contracts for arithmetic safety.

```solidity
/**
 * @title SafeMath
 * @dev Math operations with safety checks that throw on error
 */
library SafeMath {
    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
        if (a == 0) {
            return 0;
        }
        uint256 c = a * b;
        assert(c / a == b);
        return c;
    }

    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        // assert(b > 0); // Solidity automatically throws when dividing by 0
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold
        return c;
    }

    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        assert(b <= a);
        return a - b;
    }

    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        assert(c >= a);
        return c;
    }
}
```



#### Ownable

**Purpose**: Adds an `owner` role with `onlyOwner` restrictions.

**Key Functions**: `transferOwnership()` allows changing the contract owner.

**Usage**: Used across all contracts to restrict sensitive actions to the contract owner (admin)

```solidity
/**
 * @title Ownable
 * @dev The Ownable contract has an owner address, and provides basic authorization control
 * functions, this simplifies the implementation of "user permissions".
 */
contract Ownable {
    address public owner;

    /**
      * @dev The Ownable constructor sets the original `owner` of the contract to the sender
      * account.
      */
    function Ownable() public {
        owner = msg.sender;
    }

    /**
      * @dev Throws if called by any account other than the owner.
      */
    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    /**
    * @dev Allows the current owner to transfer control of the contract to a newOwner.
    * @param newOwner The address to transfer ownership to.
    */
    function transferOwnership(address newOwner) public onlyOwner {
        if (newOwner != address(0)) {
            owner = newOwner;
        }
    }

}
```

#### UpgradedStandardToken is StandardToken ("interface")

A contract which defined the main functions to implement an upgradeability system.

**Purpose**: Interface for upgraded token contract.

**Usage**: Allows the original contract to delegate calls to a newer version via upgrade path.

**Functions**: Proxy equivalents of `transfer`, `transferFrom`, `approve` for legacy compatibility.

```solidity
contract UpgradedStandardToken is StandardToken{
    // those methods are called by the legacy contract
    // and they must ensure msg.sender to be the contract address
    function transferByLegacy(address from, address to, uint value) public;
    function transferFromByLegacy(address sender, address from, address spender, uint value) public;
    function approveByLegacy(address from, address spender, uint value) public;
}
```



### Transfer restriction

#### contract Pausable is Ownable

- **Purpose**: Adds emergency stop mechanism (`pause()` / `unpause()`).
- **Usage**: Disables transfers and sensitive functions while paused.
- **Access**: Only `owner` can pause/unpause the contract.

```solidity
/**
 * @title Pausable
 * @dev Base contract which allows children to implement an emergency stop mechanism.
 */
contract Pausable is Ownable {
  event Pause();
  event Unpause();

  bool public paused = false;


  /**
   * @dev Modifier to make a function callable only when the contract is not paused.
   */
  modifier whenNotPaused() {
    require(!paused);
    _;
  }

  /**
   * @dev Modifier to make a function callable only when the contract is paused.
   */
  modifier whenPaused() {
    require(paused);
    _;
  }

  /**
   * @dev called by the owner to pause, triggers stopped state
   */
  function pause() onlyOwner whenNotPaused public {
    paused = true;
    Pause();
  }

  /**
   * @dev called by the owner to unpause, returns to normal state
   */
  function unpause() onlyOwner whenPaused public {
    paused = false;
    Unpause();
  }
}
```



#### contract BlackList is Ownable, BasicToken

- **Purpose**: Allows the `owner` to blacklist addresses and destroy their funds.
- **Key Functions**:
  - `addBlackList()`, `removeBlackList()`
  - `destroyBlackFunds()` reduces `totalSupply` and wipes balance.
- **Criticism**: This function enables *censorship and fund seizure*

```solidity
contract BlackList is Ownable, BasicToken {
/////// Getters to allow the same blacklist to be used also by other contracts (including upgraded Tether) ///////
function getBlackListStatus(address _maker) external constant returns (bool) {
    return isBlackListed[_maker];
}

function getOwner() external constant returns (address) {
    return owner;
}

mapping (address => bool) public isBlackListed;

function addBlackList (address _evilUser) public onlyOwner {
    isBlackListed[_evilUser] = true;
    AddedBlackList(_evilUser);
}

function removeBlackList (address _clearedUser) public onlyOwner {
    isBlackListed[_clearedUser] = false;
    RemovedBlackList(_clearedUser);
}

function destroyBlackFunds (address _blackListedUser) public onlyOwner {
    require(isBlackListed[_blackListedUser]);
    uint dirtyFunds = balanceOf(_blackListedUser);
    balances[_blackListedUser] = 0;
    _totalSupply -= dirtyFunds;
    DestroyedBlackFunds(_blackListedUser, dirtyFunds);
}

event DestroyedBlackFunds(address _blackListedUser, uint _balance);

event AddedBlackList(address _user);

event RemovedBlackList(address _user);
}
```



### ERC-20 part



#### ERC20Basic

- **Purpose**: Simplified ERC-20 interface.
- **Key Methods**: `balanceOf()`, `transfer()`, `totalSupply()`, `Transfer` event.
- **Usage**: Base interface that all token contracts inherit from.

```solidity
/**
 * @title ERC20Basic
 * @dev Simpler version of ERC20 interface
 * @dev see https://github.com/ethereum/EIPs/issues/20
 */
contract ERC20Basic {
    uint public _totalSupply;
    function totalSupply() public constant returns (uint);
    function balanceOf(address who) public constant returns (uint);
    function transfer(address to, uint value) public;
    event Transfer(address indexed from, address indexed to, uint value);
}

```

#### ERC20 is ERC20Basic

- **Purpose**: Full ERC-20 interface, extending `ERC20Basic`.
- **Key Methods**: Adds `approve()`, `transferFrom()`, `allowance()`, and `Approval` event.

```solidity
/**
 * @title ERC20 interface
 * @dev see https://github.com/ethereum/EIPs/issues/20
 */
contract ERC20 is ERC20Basic {
    function allowance(address owner, address spender) public constant returns (uint);
    function transferFrom(address from, address to, uint value) public;
    function approve(address spender, uint value) public;
    event Approval(address indexed owner, address indexed spender, uint value);
}
```



#### BasicToken is Ownable, ERC20Basic

**Purpose**: Implements `ERC20Basic`, provides core token logic: `balances`, `transfer()`.

**Features**:

- Uses `SafeMath` for safe calculations.
- Optional transfer fee via `basisPointsRate` and `maximumFee`.
- Includes protection against short address attack via `onlyPayloadSize` modifier.

```solidity

/**
 * @title Basic token
 * @dev Basic version of StandardToken, with no allowances.
 */
contract BasicToken is Ownable, ERC20Basic {
    using SafeMath for uint;

    mapping(address => uint) public balances;

    // additional variables for use if transaction fees ever became necessary
    uint public basisPointsRate = 0;
    uint public maximumFee = 0;

    /**
    * @dev Fix for the ERC20 short address attack.
    */
    modifier onlyPayloadSize(uint size) {
        require(!(msg.data.length < size + 4));
        _;
    }

    /**
    * @dev transfer token for a specified address
    * @param _to The address to transfer to.
    * @param _value The amount to be transferred.
    */
    function transfer(address _to, uint _value) public onlyPayloadSize(2 * 32) {
        uint fee = (_value.mul(basisPointsRate)).div(10000);
        if (fee > maximumFee) {
            fee = maximumFee;
        }
        uint sendAmount = _value.sub(fee);
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(sendAmount);
        if (fee > 0) {
            balances[owner] = balances[owner].add(fee);
            Transfer(msg.sender, owner, fee);
        }
        Transfer(msg.sender, _to, sendAmount);
    }

    /**
    * @dev Gets the balance of the specified address.
    * @param _owner The address to query the the balance of.
    * @return An uint representing the amount owned by the passed address.
    */
    function balanceOf(address _owner) public constant returns (uint balance) {
        return balances[_owner];
    }

}
```



#### StandardToken is BasicToken, ERC20

- **Purpose**: Adds support for **allowance-based transfers** (`approve`/`transferFrom`), fulfilling full ERC-20 spec.
- **Key Features**:
  - `allowed` mapping tracks delegated spending.
  - Inherits from `BasicToken`.
  - Supports unlimited allowances via `MAX_UINT`.

```solidity
/**
 * @title Standard ERC20 token
 *
 * @dev Implementation of the basic standard token.
 * @dev https://github.com/ethereum/EIPs/issues/20
 * @dev Based oncode by FirstBlood: https://github.com/Firstbloodio/token/blob/master/smart_contract/FirstBloodToken.sol
 */
contract StandardToken is BasicToken, ERC20 {

    mapping (address => mapping (address => uint)) public allowed;

    uint public constant MAX_UINT = 2**256 - 1;

    /**
    * @dev Transfer tokens from one address to another
    * @param _from address The address which you want to send tokens from
    * @param _to address The address which you want to transfer to
    * @param _value uint the amount of tokens to be transferred
    */
    function transferFrom(address _from, address _to, uint _value) public onlyPayloadSize(3 * 32) {
        var _allowance = allowed[_from][msg.sender];

        // Check is not needed because sub(_allowance, _value) will already throw if this condition is not met
        // if (_value > _allowance) throw;

        uint fee = (_value.mul(basisPointsRate)).div(10000);
        if (fee > maximumFee) {
            fee = maximumFee;
        }
        if (_allowance < MAX_UINT) {
            allowed[_from][msg.sender] = _allowance.sub(_value);
        }
        uint sendAmount = _value.sub(fee);
        balances[_from] = balances[_from].sub(_value);
        balances[_to] = balances[_to].add(sendAmount);
        if (fee > 0) {
            balances[owner] = balances[owner].add(fee);
            Transfer(_from, owner, fee);
        }
        Transfer(_from, _to, sendAmount);
    }

    /**
    * @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
    * @param _spender The address which will spend the funds.
    * @param _value The amount of tokens to be spent.
    */
    function approve(address _spender, uint _value) public onlyPayloadSize(2 * 32) {

        // To change the approve amount you first have to reduce the addresses`
        //  allowance to zero by calling `approve(_spender, 0)` if it is not
        //  already 0 to mitigate the race condition described here:
        //  https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
        require(!((_value != 0) && (allowed[msg.sender][_spender] != 0)));

        allowed[msg.sender][_spender] = _value;
        Approval(msg.sender, _spender, _value);
    }

    /**
    * @dev Function to check the amount of tokens than an owner allowed to a spender.
    * @param _owner address The address which owns the funds.
    * @param _spender address The address which will spend the funds.
    * @return A uint specifying the amount of tokens still available for the spender.
    */
    function allowance(address _owner, address _spender) public constant returns (uint remaining) {
        return allowed[_owner][_spender];
    }

}

```



### TetherToken is Pausable, StandardToken, BlackList

- **Purpose**: The actual token implementation — essentially an **upgradeable, pausable, blacklisting, fee-supporting ERC-20 token**.
- **Inherits**:
  - `StandardToken`
  - `Pausable`
  - `BlackList`
- **Key Features**:
  - `issue()` and `redeem()` to mint/burn tokens.
  - `setParams()` to configure transfer fees.
  - `deprecate()` enables upgrade to a new contract.
  - Implements conditional proxying to `upgradedAddress` if deprecated.
  - `owner` can freeze blacklisted addresses or redirect the contract’s logic entirely.

```solidity
contract TetherToken is Pausable, StandardToken, BlackList {

    string public name;
    string public symbol;
    uint public decimals;
    address public upgradedAddress;
    bool public deprecated;

    //  The contract can be initialized with a number of tokens
    //  All the tokens are deposited to the owner address
    //
    // @param _balance Initial supply of the contract
    // @param _name Token Name
    // @param _symbol Token symbol
    // @param _decimals Token decimals
    function TetherToken(uint _initialSupply, string _name, string _symbol, uint _decimals) public {
        _totalSupply = _initialSupply;
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
        balances[owner] = _initialSupply;
        deprecated = false;
    }

    // Forward ERC20 methods to upgraded contract if this one is deprecated
    function transfer(address _to, uint _value) public whenNotPaused {
        require(!isBlackListed[msg.sender]);
        if (deprecated) {
            return UpgradedStandardToken(upgradedAddress).transferByLegacy(msg.sender, _to, _value);
        } else {
            return super.transfer(_to, _value);
        }
    }

    // Forward ERC20 methods to upgraded contract if this one is deprecated
    function transferFrom(address _from, address _to, uint _value) public whenNotPaused {
        require(!isBlackListed[_from]);
        if (deprecated) {
            return UpgradedStandardToken(upgradedAddress).transferFromByLegacy(msg.sender, _from, _to, _value);
        } else {
            return super.transferFrom(_from, _to, _value);
        }
    }

    // Forward ERC20 methods to upgraded contract if this one is deprecated
    function balanceOf(address who) public constant returns (uint) {
        if (deprecated) {
            return UpgradedStandardToken(upgradedAddress).balanceOf(who);
        } else {
            return super.balanceOf(who);
        }
    }

    // Forward ERC20 methods to upgraded contract if this one is deprecated
    function approve(address _spender, uint _value) public onlyPayloadSize(2 * 32) {
        if (deprecated) {
            return UpgradedStandardToken(upgradedAddress).approveByLegacy(msg.sender, _spender, _value);
        } else {
            return super.approve(_spender, _value);
        }
    }

    // Forward ERC20 methods to upgraded contract if this one is deprecated
    function allowance(address _owner, address _spender) public constant returns (uint remaining) {
        if (deprecated) {
            return StandardToken(upgradedAddress).allowance(_owner, _spender);
        } else {
            return super.allowance(_owner, _spender);
        }
    }

    // deprecate current contract in favour of a new one
    function deprecate(address _upgradedAddress) public onlyOwner {
        deprecated = true;
        upgradedAddress = _upgradedAddress;
        Deprecate(_upgradedAddress);
    }

    // deprecate current contract if favour of a new one
    function totalSupply() public constant returns (uint) {
        if (deprecated) {
            return StandardToken(upgradedAddress).totalSupply();
        } else {
            return _totalSupply;
        }
    }

    // Issue a new amount of tokens
    // these tokens are deposited into the owner address
    //
    // @param _amount Number of tokens to be issued
    function issue(uint amount) public onlyOwner {
        require(_totalSupply + amount > _totalSupply);
        require(balances[owner] + amount > balances[owner]);

        balances[owner] += amount;
        _totalSupply += amount;
        Issue(amount);
    }

    // Redeem tokens.
    // These tokens are withdrawn from the owner address
    // if the balance must be enough to cover the redeem
    // or the call will fail.
    // @param _amount Number of tokens to be issued
    function redeem(uint amount) public onlyOwner {
        require(_totalSupply >= amount);
        require(balances[owner] >= amount);

        _totalSupply -= amount;
        balances[owner] -= amount;
        Redeem(amount);
    }

    function setParams(uint newBasisPoints, uint newMaxFee) public onlyOwner {
        // Ensure transparency by hardcoding limit beyond which fees can never be added
        require(newBasisPoints < 20);
        require(newMaxFee < 50);

        basisPointsRate = newBasisPoints;
        maximumFee = newMaxFee.mul(10**decimals);

        Params(basisPointsRate, maximumFee);
    }

    // Called when new token are issued
    event Issue(uint amount);

    // Called when tokens are redeemed
    event Redeem(uint amount);

    // Called when contract is deprecated
    event Deprecate(address newAddress);

    // Called if contract ever adds fees
    event Params(uint feeBasisPoints, uint maxFee);
}
```

------

## Security and Centralization Concerns

### Centralization risk

USDT is a centralized stablecoin as shown in the following table:

| Feature                           | Centralization Risk? | Notes                                         |
| --------------------------------- | -------------------- | --------------------------------------------- |
| `pause()`                         | &#x2611;             | &#x2611;Owner can halt all transfers          |
| `blacklist` & `destroyBlackFunds` | &#x2611;             | &#x2611;Owner can confiscate user funds       |
| `issue()` / `redeem()`            | &#x2611;             | &#x2611;Mint and burn at will by owner        |
| `deprecated` upgrade path         | &#x2611;             | &#x2611;Users can't opt out of upgrade        |
| `fees`                            | &#x2611;             | &#x2611;Can be changed within limits by owner |



### Protection

#### Fix for ERC20 Short Address Attack" — No Longer Needed

##### What was it?

Early Solidity versions (before ~0.5.0) had a problem where malformed transaction payloads (i.e., too short) could be interpreted incorrectly. This was called the **short address attack**, particularly relevant to `transfer(address,uint)` functions.

##### The Fix:

```solidity
onlyPayloadSize(uint size) {
    require(msg.data.length >= size + 4);
    _;
}
```

This ensured the correct number of bytes were passed in.

##### Why it’s no longer needed:

- **Solidity ≥ 0.5.0** introduced **ABI decoding with strict size checks**, automatically reverting if the input data length is incorrect.
- This makes `onlyPayloadSize()` obsolete in modern Solidity versions.
- The compiler also adds checks behind the scenes during external function calls.

------

#### Use of `SafeMath` Library — Optional in Solidity ≥ 0.8.0

##### What was it?

`SafeMath` was used to **prevent integer overflow and underflow** (e.g., `a + b` exceeding `uint256` limits).

##### SafeMath usage:

```solidity
using SafeMath for uint256;
uint256 c = a.add(b);
```

##### Why it’s no longer needed:

- **Solidity 0.8.0 and above** includes **built-in overflow/underflow checks**.
- So operations like `a + b`, `a - b`, and `a * b` automatically revert on overflow/underflow.
- This makes `SafeMath` redundant nowadays

------

### Summary Table

| Old Practice        | Why It Was Needed                            | Why It’s Now Obsolete                            |
| ------------------- | -------------------------------------------- | ------------------------------------------------ |
| `onlyPayloadSize()` | Prevent short address attack in old Solidity | Solidity ≥0.5.0 has built-in input length checks |
| `SafeMath`          | Prevent overflows/underflows                 | Solidity ≥0.8.0 has native overflow protection   |

------

## Main points

- Full-featured ERC20 with:
  - Fee support
  - Emergency pause
  - Upgradeability
  - Mint/burn
- Modular and extensible code
- Built-in blacklist & security controls for issuer

### Propreties

- **Owner has sweeping power** (mint, freeze, confiscate, halt)
- **Security mechanisms** (like short address attack prevention) are outdated
- **Obsolete Solidity version** (v0.4.x lacks modern language features like `revert()` and `safe constructors`)
- **No use of events in critical areas like `transfer` in upgraded contract**
- **Deprecation relies on trust** in `upgradedAddress` implementation



------

## Summary

This is a **classic example of a custodial/centralized stablecoin** with:

- Centralized control over minting, upgrades, and user balances.
  - A practical, but trust-heavy implementation.

- Solidity code presents a reasonable structure for 2017, but not aligned with modern solidity code

## Reference

- USDT mainet contract address: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
- ChatGPT for the analyse
