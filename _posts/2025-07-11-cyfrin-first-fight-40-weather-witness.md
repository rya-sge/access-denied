---
layout: post
title: "Cyfrin First Fight 40 - Weather Witness"
date: 2025-07-11
lang: en
locale: en-GB
categories: solidity blockchain
tags: ctf cyfrin first-fight
description: First Fight 40 - Weather Witness.
image: 
isMath: false
---

This project provides a dynamic NFT system that changes based on real-world weather conditions for specified locations using Chainlink Functions, Automation, and ERC721 standards. Users can mint their weather NFT and automate the weather updates using Chainlink Automation.

This article describes the [First Fight 40](https://codehawks.cyfrin.io/c/2025-05-weather-witness) from Cyfrin.

The code is available on [GitHub](https://github.com/CodeHawks-Contests/2025-05-weather-witness).

[TOC]



## Description

- Weather NFT enables users to mint NFTs tied to specific geographic locations (identified by pincode and ISO country code). These NFTs automatically update to reflect the current weather conditions of their linked location through Chainlink's decentralized oracle network. The project leverages Chainlink Functions to fetch weather data and Chainlink Automation to keep the NFTs up-to-date.

  The codebase is primarily built around two main contracts:
  
  - `WeatherNft.sol` - Main contract for minting and managing dynamic weather NFTs
  - `WeatherNftStore.sol` - Base contract containing storage variables, events, and data structures
  
  ### WeatherNft
  
  This contract allows users to:
  
  - Mint NFTs linked to specific geographic locations User can mint weather NFT by paying the mint price. The smart contract also allows user to automate the weather updations in order to update the NFT at regular intervals on the basis of heartbeat. The user can specify whether they want to register automation via chainlink automation by passing _registerKeeper as true. They are required to make an initial link deposit which will fund their keeper subscription. A dedicated keeper subcription is made for every NFT having tokenId as the checkData.
  - Weather Query Chainlink functions is utilized to send a request to Open Weather API and fetch the current weather. The WeatherNft takes in user's pincode and isocode to fetch the current weather. The implementation to get the current weather on the basis of pincode and isocode is written in GetWeather.js Related Links for OpenWeather API:
  
  ```
  https://openweathermap.org/api/geocoding-api
  https://openweathermap.org/current
  https://openweathermap.org/weather-conditions
  ```
  
  - Set up automated weather updates using Chainlink Automation The checkupkeep and performupkeep function performs the automation task for weather NFT auto updation with the current temperature. The checkupkeep function is triggered by chainlink keepers with the respective tokenId to check for NFT update if interval has passed depicted by heartbeat. The keepers then call performupkeep function to send a request to chainlink functions to fetch the current weather and update the NFT data.
  - Manual Weather Update A user can also choose to not subscribe to automation and can manually call performupkeep with the tokenId of their NFT and get their NFT updated with the latest data from the chainlink functions request to open weather API.
  
  ### WeatherNftStore
  
  This contract contains:
  
  - Storage variables for the WeatherNft system
  - Event definitions
  - Error declarations
  - Data structure definitions
  
  ### Minting a Weather NFT
  
  A user calls the `requestMintWeatherNFT` function with:
  
  1. Pincode - postal/zip code of the location
  2. ISO country code - country identifier
  3. Optional Keeper registration - to automate weather updates
  4. Heartbeat interval - frequency of weather updates
  5. Initial LINK deposit - for automation services
  
  The minting process involves:
  
  1. Payment of the current mint price (which increases with each mint)
  2. Sending a Chainlink Functions request to fetch weather data
  3. Chainlink function callback populates the state with the response and error containing the weather data.
  4. User calls the fulfillMintRequest function and NFT is minted with the current weather data in response.
  5. If requested, a Chainlink Automation upkeep is registered to keep the NFT updated
  
  ### Automating Weather Updates
  
  For NFTs with registered automation:
  
  1. Chainlink Keepers check if the heartbeat interval has passed
  2. When it's time for an update, the keeper calls `performUpkeep`
  3. A new Chainlink Functions request is sent to fetch the current weather
  4. When the data arrives, the NFT's weather state is updated
  
  ### Weather States
  
  The contract supports the following weather states:
  
  - SUNNY
  - CLOUDY
  - RAINY
  - THUNDERSTORM
  - WINDY
  - SNOW
  
  Each weather state has an associated image URI that represents the current condition. The sample URI can be found in the deployment script (deploy/DeployWeatherNft.js)
  
  ### Roles in the Project:
  
  1. NFT Owner
     - Users who mint and own Weather NFTs
     - Can transfer ownership of their NFTs
  2. Contract Owner
     - Can update Chainlink Functions configuration
     - Can modify gas limits and other system parameters
     - Controls subscription IDs and other administrative settings



## All submissions

## My submissions

### Heigh - PerformUpkeep should only be performed when checkUpkeep return true

#### Root + Impact

PerformUpkeep does not call `checkUpkeep`

As a result, it is possible to update the NFT weather state before the heartbeat.

#### Description

Keeper will call checkUpKeep before perming the call to PerformUpkeep.
But since there is no access control on the function, anybody can call the function even if checkUpKeep return false.

```solidity
// Root cause in the codebase with @> marks to highlight the relevant section
```



#### Risk

**Likelihood**:

Interest in an attacker is probably low

**Impact**:

NFT weather state is updated before the heartbeat



#### Recommended Mitigation

Call checkUpKeep inside performUpkeep

```solidity
\- remove this code

\+ add this code

function performUpkeep(bytes calldata performData) external override {

bool res = checkUpkeep(performData)

require(res, "Invalid update")

}
```

### Heigh - NFT price (ether) is locked in the smart contract (Lack of Withdraw function)

#### Root + Impact

The contract includes a payable function to accept Ether but lacks a corresponding function to withdraw it, which leads to the Ether being locked in the contract.

#### Description

requestMintWeatherNFT is payable where msg.value == `s_currentMintPrice`

The value represents the NFT price and it is locked in the smart contract

```solidity
 function requestMintWeatherNFT(

​        string memory _pincode,

​        string memory _isoCode,

​        bool _registerKeeper,

​        uint256 _heartbeat,

​        uint256 _initLinkDeposit

​    ) external payable returns (bytes32 _reqId) {

​        require(

​            msg.value == s_currentMintPrice,

​            WeatherNft__InvalidAmountSent()

​        );
```



#### Risk

**Likelihood**:

For each NFT minted, the NFT price will be locked in the smart contract

**Impact**:

Ethers payed for each mint is locked inside the smart contract

#### Recommended Mitigation

Implement a public or external function that allows for the withdrawal of Ether from the contract.

```solidity
- remove this code
+ add this code
 function withdraw(uint256 amount) external onlyOwner{
        require(amount > 0, "Nothing to withdraw");
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Withdraw failed");
    }
```

## Invalid submissions

### Low - Conversion - loss of precision for link deposit

#### Reason: incorrect statement

- After discussion with the sponsor, this turns out to be invalid. This is because the Chainlink has a capped maximum supply of 1 billion LINK tokens. This means that the total number of LINK tokens will never exceed 1 billion. The token has 18 decimals, so the max scaled value that is required to represent all LINK tokens is 1e27. The max value of `uint96` is 2**96 - 1, that is around 79e27 and it is sufficient to store all LINK tokens. Therefore, the cast from uint256 to uint96 is safe and there is no possibility of token truncation/loss of tokens.

#### Root + Impact

`initLinkDeposit, a uint256,is converted to an uint96 in FullFillMintRequest.

There is a potentiel of incorrect recording of deposit funds if the user put an amount > 2^96 as a deposit when he creates is NFT



#### Description

When creating the parameters for the keeper, the value of initLinkDeposit which represents the initial link deposit by the user during the mint is converted to a uint96 while the current unit is uint256.

```solidity
 IAutomationRegistrarInterface.RegistrationParams

​                memory _keeperParams = IAutomationRegistrarInterface

​                    .RegistrationParams({

​                        name: string.concat(

​                            "Weather NFT Keeper: ",

​                            Strings.toString(tokenId)

​                        ),

​                        encryptedEmail: "",

​                        upkeepContract: address(this),

​                        gasLimit: s_upkeepGaslimit,

​                        adminAddress: address(this),

​                        triggerType: 0,

​                        checkData: abi.encode(tokenId),

​                        triggerConfig: "",

​                        offchainConfig: "",

​                        // @audit : uint256 - uint96 conversion

​                        amount: uint96(_userMintRequest.initLinkDeposit)

​                    });
```



#### Risk

**Likelihood**:

the user makes an initial deposit > 2^96 (low)

**Impact**:

The check will depend of how this amount is used by the keeper, but it is probably to know the amount deposited by the user.

#### Proof of Concept

Use a deposit > 2^96



#### Recommended Mitigation

Use an uint96 for the function parameter in requestMintWeather NFT and in the corresponding struct UserMintRequest

```solidity
- remove this code
    function requestMintWeatherNFT(
       [...]
        uint256 _initLinkDeposit 
    ) external payable returns (bytes32 _reqId) 
​
​
  struct UserMintRequest {
       [...]
        uint256 initLinkDeposit;
        string pincode;
        string isoCode;
    }
+ add this code
    function requestMintWeatherNFT(
        [...]
        uint96 _initLinkDeposit
    ) external payable returns (bytes32 _reqId) 
​
    struct UserMintRequest {
       [...]
        uint96 initLinkDeposit;
        string pincode;
        string isoCode;
    }
```

