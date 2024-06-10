---
layout: post
title:  Code4Arena Contest - Renzo Oracle
date:   2024-05-30
lang: en
locale: en-GB
categories: blockchain ethereum
tags: ethereum solidity security code4Arena
description: This article presents the oracle implementation from Renzo made during the code4Arena contest
image: /assets/article/blockchain/audit/renzoOracle-uml.png
isMath: false
---

This article presents the oracle implementation from `Renzo`. This analyze has been done for the [Code4Arena](https://github.com/code-423n4/2024-04-renzo) contest..

Since I have a limited time, I found that it could be interesting to focus only in one part in the [oracle implementation](https://github.com/code-423n4/2024-04-renzo/tree/main/contracts/Oracle) instead of the whole code.

**Description**

- Renzo is a Liquid Restaking Token (LRT) and Strategy Manager for  EigenLayer allowing user to restake their eth or LST.

For every LST or ETH deposited on Renzo, it mints an equivalent amount of $ezETH.

- ezETH is the liquid restaking token representing a user’s restaked  position at Renzo. 

Reference: [docs.renzoprotocol.com/docs/renzo/ezeth](https://docs.renzoprotocol.com/docs/renzo/ezeth)

**Links**

- Previous Audits - [Halborn](https://github.com/Renzo-Protocol/contracts-public/blob/master/Audit/Renzo_Protocol_EVM_Contracts_Smart_Contract_Security_Assessment.pdf).

- [Renzo Website](https://www.renzoprotocol.com/)

- [Documentation](https://docs.renzoprotocol.com/docs)
- [oracle implementation](https://github.com/code-423n4/2024-04-renzo/tree/main/contracts/Oracle)
- [Analyser report](https://github.com/code-423n4/2024-04-renzo/blob/main/4naly3er-report.md)

[TOC]

## Past accident

On April 24th, there was a momentary depeg involving Renzo’s ezETH/WETH pair on multiple DEXs set off a chain reaction of liquidations across different protocols. 

The most likely cause suggests that several individuals, with  substantial positions, that were leverage farming opted to close their positions following the Renzo announcement of  token allocation.

That provoqued a cascading series of liquidations on both Morpho and Gearbox protocols.

Reference: [Daedalus - Renzo](https://x.com/daedalus_angels/status/1787797086219419687?s=52&t=txFAbiSPTdLLDlAYj9X_AA)



## Chainlink Integration

Renzo uses the oracle from chainlink, version [AggregatorV3Interface](https://docs.chain.link/data-feeds/api-reference#aggregatorv3interface)

More information [here](https://docs.chain.link/data-feeds/api-reference)

### Reminder

The function `latestRoundData()`from Chainlink oracle allows to get the data from the latest round.

```solidity
function latestRoundData() external view
    returns (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    )
```

The returned values requiresto be validated by the smart contract, notably

- price >= 0

- `updatedAt` != 0 and is not too old

- answeredInRound is now deprecated and I don't think it needs to be checked

Reference: [Tigran Piliposyan](https://x.com/tpiliposian/status/1732706349492936997?t=d0cqvXaPJx6I7OqLQmsQ3w&s=35)

### Schema

Smart contracts UML

![renzoOracle-uml]({{site.url_complet}}/assets/article/blockchain/audit/renzoOracle-uml.png)



## Functions

The interface [IRenzoOracle](https://github.com/code-423n4/2024-04-renzo/blob/main/contracts/Oracle/IRenzoOracle.sol) defines four functions

- lookupTokenValue
- lookupTokenAmountFromValue
- lookupTokenValues
- calculateMintAmount
- calculateRedeemAmount

### setOracleAddress

**Description**

Sets addresses for oracle lookup.  Permission gated to the oracle admin only.

The sender can put the address 0 for `AggregatorV3Interface`to disable lookups for the token.

**Code**

```solidity
function setOracleAddress(
IERC20 _token,
AggregatorV3Interface _oracleAddress
) external nonReentrant onlyOracleAdmin {
if (address(_token) == address(0x0)) revert InvalidZeroInput();

// Verify that the pricing of the oracle is 18 decimals - pricing calculations will be off otherwise
if (_oracleAddress.decimals() != 18)
revert InvalidTokenDecimals(18, _oracleAddress.decimals());

tokenOracleLookup[_token] = _oracleAddress;
emit OracleAddressUpdated(_token, _oracleAddress);
}
```

**Analyze**

| Function                                 |                                         |
| ---------------------------------------- | --------------------------------------- |
| Access control                           | Yes with the modifier `onlyOracleAdmin` |
| Token can not be a zero address          | yes, revert with `InvalidZeroInput`     |
| Oracle address can not be a zero address | No,  reason indicated in the comment    |
| Check token decimals                     | yes, decimals have to be 18             |

**INFO**

- Why using the `nonReentrant`modifier ? The function is protected by access control and can not be reentrant.
- Use a constant instead a magic value (18) as indicated by the [analyzer report](https://github.com/code-423n4/2024-04-renzo/blob/main/4naly3er-report.md#nc-30-constants-should-be-defined-rather-than-using-magic-numbers)

### Check oracle value

**Description**

The functions `lookupTokenValue` and `lookupTokenAmountFromValue`calls both the function `latestRoundData` from chainlink, AggregatorV3Interface.

- lookupTokenAmountFromValue

Given a single token and value, return amount of tokens needed to represent that value

-  lookupTokenValues:

Given list of tokens and balances, return total value (assumes all lookups are denomintated in same underlying currency)

**Code**

```solidity
/// @dev The maxmimum staleness allowed for a price feed from chainlink
uint256 constant MAX_TIME_WINDOW = 86400 + 60; // 24 hours + 60 seconds
(, int256 price, , uint256 timestamp, ) = oracle.latestRoundData();
        if (timestamp < block.timestamp - MAX_TIME_WINDOW) revert OraclePriceExpired();
        if (price <= 0) revert InvalidOraclePrice();
```

**INFO**

An unique function `checkOracle(uint256 price, uint256 timestamp) `could be implemented instead of having the same check implemented twice.

#### lookupTokenValues

**Description**

Batch version of `lookupTokenValue`

Given list of tokens and balances, return total value (assumes all lookups are denomintated in same underlying currency).

The value returned will be denominated in the decimal precision of the lookup oracle
    (e.g. a value of 100 would return as 100 * 10^18)

**Code**

```solidity

    function lookupTokenValues(
        IERC20[] memory _tokens,
        uint256[] memory _balances
    ) external view returns (uint256) {
        if (_tokens.length != _balances.length) revert MismatchedArrayLengths();

        uint256 totalValue = 0;
        uint256 tokenLength = _tokens.length;
        for (uint256 i = 0; i < tokenLength; ) {
            totalValue += lookupTokenValue(_tokens[i], _balances[i]);
            unchecked {
                ++i;
            }
        }

        return totalValue;
    }
```

**Analyze**

| Description                                | Result                                          |
| ------------------------------------------ | ----------------------------------------------- |
| Check input size (_tokens) _balance equals | yes                                             |
| Check input size different of 0            | No, but return 0 in this case                   |
| For loop optimized                         | yes(local variable for tokenLenght, unchecked,) |



#### calculateMintAmount

Given amount of current protocol value, new value being added, and supply of ezETH, determine amount to mint.

Values should be denominated in the same underlying currency with the same decimal precision.

```solidity
uint256 constant SCALE_FACTOR = 10 ** 18;  
    function calculateMintAmount(
        uint256 _currentValueInProtocol,
        uint256 _newValueAdded,
        uint256 _existingEzETHSupply
    ) external pure returns (uint256) {
        // For first mint, just return the new value added.
        // Checking both current value and existing supply to guard against gaming the initial mint
        if (_currentValueInProtocol == 0 || _existingEzETHSupply == 0) {
            return _newValueAdded; // value is priced in base units, so divide by scale factor
        }

        // Calculate the percentage of value after the deposit
        uint256 inflationPercentaage = (SCALE_FACTOR * _newValueAdded) /
            (_currentValueInProtocol + _newValueAdded);

        // Calculate the new supply
        uint256 newEzETHSupply = (_existingEzETHSupply * SCALE_FACTOR) /
            (SCALE_FACTOR - inflationPercentaage);

        // Subtract the old supply from the new supply to get the amount to mint
        uint256 mintAmount = newEzETHSupply - _existingEzETHSupply;

        // Sanity check
        if (mintAmount == 0) revert InvalidTokenAmount();

        return mintAmount;
    }
```



**Analyze**

Calculate the percentage of value after the deposit

```solidity
        uint256 inflationPercentaage = (SCALE_FACTOR * _newValueAdded) /
            (_currentValueInProtocol + _newValueAdded);
```

Calculate the new supply

```solidity
 uint256 newEzETHSupply = (_existingEzETHSupply * SCALE_FACTOR) /
            (SCALE_FACTOR - inflationPercentaage);
```

**Analyze**

It seems OK

#### calculateRedeemAmount

**Description**

Given the amount of ezETH to burn, the supply of ezETH, and the total value in the protocol, determine amount of value to return to user

**Code**

```solidity

    function calculateRedeemAmount(
        uint256 _ezETHBeingBurned,
        uint256 _existingEzETHSupply,
        uint256 _currentValueInProtocol
    ) external pure returns (uint256) {
        // This is just returning the percentage of TVL that matches the percentage of ezETH being burned
        uint256 redeemAmount = (_currentValueInProtocol * _ezETHBeingBurned) / _existingEzETHSupply;

        // Sanity check
        if (redeemAmount == 0) revert InvalidTokenAmount();

        return redeemAmount;
    }
```

**Analyze**

It seems OK

## Others

### Access control

A modifier is defined to restrict the configuration of the contract to only the oracle admin.

```solidity
/// @dev Allows only a whitelisted address to configure the contract
modifier onlyOracleAdmin() {
if (!roleManager.isOracleAdmin(msg.sender)) revert NotOracleAdmin();
_;
}
```

### Proxy implementation

- The implementation is correctly locked  with `_disableInitializers` inside the constructor


```solidity
    /// @dev Prevents implementation contract from being initialized.
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }
```

- The public function `initialize`contains the modifier `initializer` to allow the function to be called only once.


```solidity
function initialize(IRoleManager _roleManager) public initializer
```

- Conclusion

The proxy seems correctly implemented.



## Analyzer report

The automatic analyzer report by Code4Arena has mainly made "informal" remark to improve the code quality.

### Medium

### [[M-7]](https://github.com/code-423n4/2024-04-renzo/blob/main/4naly3er-report.md#nc-27-contract-does-not-follow-the-solidity-style-guides-suggested-layout-ordering) Missing checks for whether the L2 Sequencer is active

Chainlink recommends that users using price oracles, check whether the Arbitrum Sequencer is [active](https://docs.chain.link/data-feeds/l2-sequencer-feeds#arbitrum). If the sequencer goes down, the Chainlink oracles will have stale  prices from before the downtime, until a new L2 OCR transaction goes  through. 

Users who submit their transactions via the [L1 Dealyed Inbox](https://developer.arbitrum.io/tx-lifecycle#1b--or-from-l1-via-the-delayed-inbox) will be able to take advantage of these stale prices. 

=> Use a [Chainlink oracle](https://blog.chain.link/how-to-use-chainlink-price-feeds-on-arbitrum/#almost_done!_meet_the_l2_sequencer_health_flag) to determine whether the sequencer is offline or not, and don't allow operations to take place while the sequencer is offline.

```solidity
File: contracts/Bridge/L2/Oracle/RenzoOracleL2.sol

51:         (, int256 price, , uint256 timestamp, ) = oracle.latestRoundData();
            if (timestamp < block.timestamp - MAX_TIME_WINDOW) revert OraclePriceExpired();
```

### Informal

- [[NC-26]](https://github.com/code-423n4/2024-04-renzo/blob/main/4naly3er-report.md#nc-26-use-scientific-notation-eg-1e18-rather-than-exponentiation-eg-1018) 

Use scientific notation (e.g. `1e18`) rather than exponentiation (e.g. `10**18`)

While this won't save gas in the recent solidity versions, this is  shorter and more readable (this is especially true in calculations).

- [[NC-27]](https://github.com/code-423n4/2024-04-renzo/blob/main/4naly3er-report.md#nc-27-contract-does-not-follow-the-solidity-style-guides-suggested-layout-ordering) Contract does not follow the Solidity style guide's suggested layout ordering

The [style guide](https://docs.soliditylang.org/en/v0.8.16/style-guide.html#order-of-layout) says that, within a contract, the ordering should be:

The right order is:

1. Type declarations
2. State variables
3. Events
4. Modifiers
5. Functions

- [NC-28](https://github.com/code-423n4/2024-04-renzo/blob/main/4naly3er-report.md#nc-28-use-underscores-for-number-literals-add-an-underscore-every-3-digits)

File: contracts/Oracle/RenzoOracle.sol

Use Underscores for Number Literals (add an underscore every 3 digits)

```solidity
uint256 public constant MAX_TIME_WINDOW = 86400 + 60;
```

Can be updated for

```solidity
uint256 public constant MAX_TIME_WINDOW = 86_400 + 60;
```

- [[NC-29]](https://github.com/code-423n4/2024-04-renzo/blob/main/4naly3er-report.md#nc-29-event-is-missing-indexed-fields) 

File: contracts/Bridge/L2/Oracle/RenzoOracleL2.sol

Event is missing `indexed` fields

```solidity
event OracleAddressUpdated(address newOracle, address oldOracle);
```

File: contracts/Oracle/RenzoOracle.sol

```solidity
event OracleAddressUpdated(IERC20 token, AggregatorV3Interface oracleAddress);
```

- [[M-6]](https://github.com/code-423n4/2024-04-renzo/blob/main/4naly3er-report.md#m-6-chainlinks-latestrounddata-might-return-stale-or-incorrect-results) Chainlink's `latestRoundData` might return stale or incorrect results

Report:`latestRoundData()` is used to fetch the asset price from a  Chainlink aggregator, but it's missing additional validations to ensure  that the round is complete. 

My comment: This is not necessary any more

## References

- [Renzo doc - How do LRTs work ?](https://docs.renzoprotocol.com/docs/renzo/how-do-lrts-work)
- [Analyser report](https://github.com/code-423n4/2024-04-renzo/blob/main/4naly3er-report.md)
- [Chainlink doc](https://docs.chain.link/data-feeds/api-reference#aggregatorv3interface)