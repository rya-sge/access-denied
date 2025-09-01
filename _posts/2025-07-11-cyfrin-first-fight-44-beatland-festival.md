---
layout: post
title: "Cyfrin First Fight 44 - Beatland Festival"
date: 2025-07-11
lang: en
locale: en-GB
categories: solidity blockchain
tags: ctf cyfrin first-fight
description: Cyfrin First Fight 44 - Beatland Festival.
image: 
isMath: false
---

A festival NFT ecosystem on Ethereum where users purchase tiered passes (ERC1155), attend virtual(or not) performances to earn BEAT tokens (ERC20), and redeem unique memorabilia NFTs (integrated in the same ERC1155 contract) using BEAT tokens.

This article describes the [First Fight 44](https://codehawks.cyfrin.io/c/2025-07-beatland-festival) from Cyfrin.

The code is available on [GitHub](https://github.com/CodeHawks-Contests/2025-07-beatland-festival).

[TOC]

## About the project

A festival NFT ecosystem on Ethereum where users purchase tiered passes (ERC1155), attend virtual(or not) performances to earn BEAT tokens (ERC20), and redeem unique memorabilia NFTs (integrated in the same ERC1155 contract) using BEAT tokens.

### Actors

Owner: The owner and deployer of contracts, sets the Organizer address, collects the festival proceeds.

Organizer: Configures performances and memorabilia.

Attendee: Customer that buys a pass and attends performances. They use rewards received for attending performances to buy memorabilia.

### All submissions

**Heigh**

H-01. Pass Lending Reward Multiplication Enables Unlimited Performance Rewards

[Selected submission](https://codehawks.cyfrin.io/c/2025-07-beatland-festival/s/cmd7kbg9g0005l4048f2fmz85) by [nomadic_bear](https://profiles.cyfrin.io/u/nomadic_bear)

**Medium**

M-01. [H-1] Reseting the current pass supply to 0 in the FestivalPass::configurePass function allows users to bypass the max supply cap of a pass[Selected submission](https://codehawks.cyfrin.io/c/2025-07-beatland-festival/s/cmdabdd930009l404s6pburct) by [demaxl](https://profiles.cyfrin.io/u/demaxl)

M-02. Function `FestivalPass:buyPass` Lacks Defense Against Reentrancy Attacks, Leading to Exceeding the Maximum NFT Pass Supply[Selected submission](https://codehawks.cyfrin.io/c/2025-07-beatland-festival/s/cmd87f5ah0005i9047il0wpig) by [minos](https://profiles.cyfrin.io/u/minos)

M-03. Off-by-One in `redeemMemorabilia` Prevents Last NFT From Being Redeemed

**Low**

L-01. Inactive Collections — Indefinite BEAT Lock-up[Selected submission](https://codehawks.cyfrin.io/c/2025-07-beatland-festival/s/cmdd76y040005l404bykg6lbz) by [rootkit677](https://profiles.cyfrin.io/u/rootkit677)

L-02. FestivalPass.sol - URI Function Returns Metadata for Non-Existent Items[Selected submission](https://codehawks.cyfrin.io/c/2025-07-beatland-festival/s/cmdh9e7ud0005l704nldxie8z) by [0xrektified](https://profiles.cyfrin.io/u/0xrektified)

## Missed submissions

### H-01. Pass Lending Reward Multiplication Enables Unlimited Performance Rewards

[Selected submission](https://codehawks.cyfrin.io/c/2025-07-beatland-festival/s/cmd7kbg9g0005l4048f2fmz85) by [nomadic_bear](https://profiles.cyfrin.io/u/nomadic_bear)



## Description



## Missed submissions

### H-01. Pass Lending Reward Multiplication Enables Unlimited Performance Rewards

#### Root + Impact

#### Description

- The `attendPerformance()` function is designed to reward pass holders for attending performances, with VIP and BACKSTAGE passes receiving multiplied rewards based on their tier. Under normal operation, each pass should generate rewards for a single attendee per performance, maintaining balanced tokenomics where one pass purchase corresponds to one set of performance rewards throughout the festival.
- However, the attendance system tracks attendance per user rather than per pass, while pass ownership validation occurs only at the moment of attendance through `hasPass()`. This allows coordinated users to share a single pass by strategically transferring it between attendees, enabling multiple users to attend the same performance with the same pass and each receive full multiplied rewards, effectively turning one pass purchase into unlimited reward generation.



```
function attendPerformance(uint256 performanceId) external {

​    require(isPerformanceActive(performanceId), "Performance is not active");

@>  require(hasPass(msg.sender), "Must own a pass"); // Only checks current ownership

@>  require(!hasAttended[performanceId][msg.sender], "Already attended this performance"); // Per-user tracking

​    require(block.timestamp >= lastCheckIn[msg.sender] + COOLDOWN, "Cooldown period not met");

​    

@>  hasAttended[performanceId][msg.sender] = true; // Marks user as attended

​    lastCheckIn[msg.sender] = block.timestamp;

​    

​    uint256 multiplier = getMultiplier(msg.sender);

​    BeatToken(beatToken).mint(msg.sender, performances[performanceId].baseReward * multiplier);

}

function hasPass(address user) public view returns (bool) {

@>  return balanceOf(user, GENERAL_PASS) > 0 || 

​           balanceOf(user, VIP_PASS) > 0 || 

​           balanceOf(user, BACKSTAGE_PASS) > 0; // Only checks current balance

}
```

The vulnerability exists in the combination of per-user attendance tracking (`hasAttended[performanceId][msg.sender]`) and point-in-time pass ownership validation (`hasPass(msg.sender)`). The system records that a specific user attended a specific performance, but does not track which pass was used or prevent the same pass from being used by multiple users for the same performance through transfers.

#### Risk

**Likelihood**:

-  The vulnerability requires coordination between multiple users and strategic timing of pass transfers during active performance windows, which demands planning and cooperation rather than simple individual exploitation.  
- The attack becomes immediately executable once multiple users coordinate, as ERC1155 transfers are permissionless and the attendance system provides no restrictions on pass transfers between attendance events.

**Impact**:

- Unlimited reward farming from single pass purchases enables coordinated groups to multiply performance rewards indefinitely (demonstrated: 4x-10x reward multiplication), completely breaking the intended pass-to-reward ratio and causing massive BEAT token inflation.
- Complete bypass of cooldown mechanisms and attendance restrictions through pass lending, allowing rapid reward extraction and undermining all intended rate-limiting protections designed to prevent reward farming abuse.

### 

#### Recommended Mitigation

The fix implements per-pass attendance tracking to ensure each individual pass can only be used once per performance, regardless of how many times it's transferred between users. This preserves the intended 1-pass-1-reward economics while still allowing legitimate pass transfers for other purposes, preventing coordinated reward multiplication while maintaining the flexibility of the ERC1155 standard.

```
contract FestivalPass is ERC1155, Ownable2Step, IFestivalPass {
    // ... existing state variables ...
+   mapping(uint256 => mapping(uint256 => bool)) public passUsedForPerformance; // performanceId => passTokenId => used
    
    function attendPerformance(uint256 performanceId) external {
        require(isPerformanceActive(performanceId), "Performance is not active");
        require(hasPass(msg.sender), "Must own a pass");
        require(!hasAttended[performanceId][msg.sender], "Already attended this performance");
        require(block.timestamp >= lastCheckIn[msg.sender] + COOLDOWN, "Cooldown period not met");
        
+       // Check which pass type the user owns and mark it as used
+       uint256 userPassId = getUserPassId(msg.sender);
+       require(!passUsedForPerformance[performanceId][userPassId], "This pass already used for this performance");
+       passUsedForPerformance[performanceId][userPassId] = true;
        
        hasAttended[performanceId][msg.sender] = true;
        lastCheckIn[msg.sender] = block.timestamp;
        
        uint256 multiplier = getMultiplier(msg.sender);
        BeatToken(beatToken).mint(msg.sender, performances[performanceId].baseReward * multiplier);
        emit Attended(msg.sender, performanceId, performances[performanceId].baseReward * multiplier);
    }
    
+   function getUserPassId(address user) internal view returns (uint256) {
+       if (balanceOf(user, BACKSTAGE_PASS) > 0) return BACKSTAGE_PASS;
+       if (balanceOf(user, VIP_PASS) > 0) return VIP_PASS;
+       if (balanceOf(user, GENERAL_PASS) > 0) return GENERAL_PASS;
+       revert("User has no pass");
+   }
}
```

### Function `FestivalPass:buyPass` Lacks Defense Against Reentrancy Attacks, Leading to Exceeding the Maximum NFT Pass Supply

#### Description

- Under normal circumstances, the system should control the supply of tokens or resources to ensure that it does not exceed a predefined maximum limit. This helps maintain system stability, security, and predictable behavior.
- The function `FestivalPass:buyPass` does not follow the **Checks-Effects-Interactions** pattern. If a user uses a malicious contract as their account and includes reentrancy logic, they can bypass the maximum supply limit.

```solidity
	function buyPass(uint256 collectionId) external payable {
		// Must be valid pass ID (1 or 2 or 3)
		require(collectionId == GENERAL_PASS || collectionId == VIP_PASS || collectionId == BACKSTAGE_PASS, "Invalid pass ID");
		// Check payment and supply
		require(msg.value == passPrice[collectionId], "Incorrect payment amount");
		require(passSupply[collectionId] < passMaxSupply[collectionId], "Max supply reached");
		// Mint 1 pass to buyer
@>		_mint(msg.sender, collectionId, 1, ""); // question: potential reentrancy?
		++passSupply[collectionId];
		// VIP gets 5 BEAT welcome bonus, BACKSTAGE gets 15 BEAT welcome bonus
		uint256 bonus = (collectionId == VIP_PASS) ? 5e18 : (collectionId == BACKSTAGE_PASS) ? 15e18 : 0;
		if (bonus > 0) {
			// Mint BEAT tokens to buyer
			BeatToken(beatToken).mint(msg.sender, bonus);
		}
		emit PassPurchased(msg.sender, collectionId);
	}
```

## Risk

**Likelihood**:

- If a user uses a contract wallet with reentrancy logic, they can trigger multiple malicious calls during the execution of the `_mint` function.

**Impact**:

- Although the attacker still pays for each purchase, the total number of minted NFTs will exceed the intended maximum supply. This can lead to supply inflation and user dissatisfaction.

#### POC

//SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import "@openzeppelin/contracts/token/ERC1155/IERC1155Receiver.sol";
import "../src/FestivalPass.sol";
import "./FestivalPass.t.sol";
import {console} from "forge-std/Test.sol";

contract AttackBuyPass{
	address immutable onlyOnwer;
	FestivalPassTest immutable festivalPassTest;
	FestivalPass immutable festivalPass;
	uint256 immutable collectionId;
	uint256 immutable configPassPrice;
	uint256 immutable configPassMaxSupply;
	

```solidity
uint256 hackMintCount = 0;

constructor(FestivalPassTest _festivalPassTest, FestivalPass _festivalPass, uint256 _collectionId, uint256 _configPassPrice, uint256 _configPassMaxSupply) payable {
	onlyOnwer = msg.sender;
	
	festivalPassTest = _festivalPassTest;
	festivalPass = _festivalPass;
	collectionId = _collectionId;
	configPassPrice = _configPassPrice;
	configPassMaxSupply = _configPassMaxSupply;

	hackMintCount = 1;
}

receive() external payable {}
fallback() external payable {}

function DoAttackBuyPass() public {
	require(msg.sender == onlyOnwer, "AttackBuyPass: msg.sender != onlyOnwer");

	// This attack can only bypass the "maximum supply" restriction.
	festivalPass.buyPass{value: configPassPrice}(collectionId);
}

function onERC1155Received(
	address operator,
	address from,
	uint256 id,
	uint256 value,
	bytes calldata data
) external returns (bytes4){
	if (hackMintCount  festivalPass.passMaxSupply(targetPassId));
}
}
```


#### Recommanded mitigation

- Refactor the function `FestivalPass:buyPass` to follow the **Checks-Effects-Interactions** principle.

```solidity
    function buyPass(uint256 collectionId) external payable {
        // Must be valid pass ID (1 or 2 or 3)
        require(collectionId == GENERAL_PASS || collectionId == VIP_PASS || collectionId == BACKSTAGE_PASS, "Invalid pass ID");
        // Check payment and supply
        require(msg.value == passPrice[collectionId], "Incorrect payment amount");
        require(passSupply[collectionId] < passMaxSupply[collectionId], "Max supply reached");
        // Mint 1 pass to buyer
-        _mint(msg.sender, collectionId, 1, ""); 
        ++passSupply[collectionId];
+        emit PassPurchased(msg.sender, collectionId);        
+        _mint(msg.sender, collectionId, 1, "");        
        // VIP gets 5 BEAT welcome bonus, BACKSTAGE gets 15 BEAT welcome bonus
        uint256 bonus = (collectionId == VIP_PASS) ? 5e18 : (collectionId == BACKSTAGE_PASS) ? 15e18 : 0;
        if (bonus > 0) {
            // Mint BEAT tokens to buyer
            BeatToken(beatToken).mint(msg.sender, bonus);
        }
-        emit PassPurchased(msg.sender, collectionId);
    }
```





L-02. FestivalPass.sol - URI Function Returns Metadata for Non-Existent Items[Selected submission](https://codehawks.cyfrin.io/c/2025-07-beatland-festival/s/cmdh9e7ud0005l704nldxie8z) by [0xrektified](https://profiles.cyfrin.io/u/0xrektified)

### Description

The `uri` function returns metadata URLs for any token ID that belongs to an existing collection, even if the specific item within that collection was never minted. This creates confusion about which tokens actually exist and can cause integration issues with external systems that rely on URI responses to determine token validity.

### Root Cause

The URI function only validates that the collection exists but doesn't verify that the specific item was actually minted:

Copy to clipboard

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

function uri(uint256 tokenId) public view override returns (string memory) {

​    // Handle regular passes (IDs 1-3)

​    if (tokenId <= BACKSTAGE_PASS) {

​        return string(abi.encodePacked("ipfs://beatdrop/", Strings.toString(tokenId)));

​    }

​    

​    // Decode collection and item IDs

​    (uint256 collectionId, uint256 itemId) = decodeTokenId(tokenId);

​    

​    // Check if it's a valid memorabilia token

​    if (collections[collectionId].priceInBeat > 0) {

​        // ❌ Returns URI even for non-existent items!

​        return string(abi.encodePacked(

​            collections[collectionId].baseUri,

​            "/metadata/",

​            Strings.toString(itemId)

​        ));

​    }

​    

​    return super.uri(tokenId);

}

The function should also verify that `itemId` is within the range of actually minted items (`itemId > 0 && itemId < collections[collectionId].currentItemId`).

### Risk

**Likelihood**: Medium - Any external system querying URIs for memorabilia tokens can encounter this issue when checking non-existent item IDs.

**Impact**: Low - No funds are at risk, but metadata integrity is compromised and external integrations may be confused.

### Impact

- External systems receive metadata URLs for tokens that were never minted
- NFT marketplaces might display non-existent items as available
- Inconsistent behavior between `balanceOf()` (returns 0 for non-existent tokens) and `uri()` (returns metadata)
- Confusion about which items in a collection actually exist
- Potential integration failures with systems expecting URI calls to fail for non-existent tokens

### Proof of Concept

This test demonstrates how the URI function returns metadata for items that were never minted:

Copy to clipboard

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

function test_URIReturnsInvalidMetadataForNonExistentItems() public {

​    // Organizer creates a collection with maxSupply = 5

​    vm.prank(organizer);

​    uint256 collectionId = festivalPass.createMemorabiliaCollection(

​        "Test Collection",

​        "ipfs://testbase",

​        50e18,

​        5,  // maxSupply = 5

​        true

​    );

​    

​    // Give user BEAT tokens and let them redeem 2 items

​    vm.prank(address(festivalPass));

​    beatToken.mint(user1, 200e18);

​    

​    // User redeems 2 items (itemIds 1 and 2)

​    vm.startPrank(user1);

​    festivalPass.redeemMemorabilia(collectionId);  // Item 1

​    festivalPass.redeemMemorabilia(collectionId);  // Item 2

​    vm.stopPrank();

​    

​    // Collection now has currentItemId = 3 (next item to be minted)

​    // Only items 1 and 2 actually exist

​    

​    // Encode token IDs for existing and non-existing items

​    uint256 existingItem1 = festivalPass.encodeTokenId(collectionId, 1);

​    uint256 existingItem2 = festivalPass.encodeTokenId(collectionId, 2);

​    uint256 nonExistentItem3 = festivalPass.encodeTokenId(collectionId, 3);

​    uint256 nonExistentItem6 = festivalPass.encodeTokenId(collectionId, 6);

​    

​    // Verify only items 1 and 2 actually exist (user owns them)

​    assertEq(festivalPass.balanceOf(user1, existingItem1), 1);

​    assertEq(festivalPass.balanceOf(user1, existingItem2), 1);

​    assertEq(festivalPass.balanceOf(user1, nonExistentItem3), 0);

​    assertEq(festivalPass.balanceOf(user1, nonExistentItem6), 0);

​    

​    // BUT uri() function returns metadata URLs for ALL items, even non-existent ones!

​    string memory uri1 = festivalPass.uri(existingItem1);

​    string memory uri2 = festivalPass.uri(existingItem2);

​    string memory uri3 = festivalPass.uri(nonExistentItem3);  // Should not exist!

​    string memory uri6 = festivalPass.uri(nonExistentItem6);  // Should not exist!

​    

​    // All URIs are returned even for non-existent items

​    assertEq(uri1, "ipfs://testbase/metadata/1");

​    assertEq(uri2, "ipfs://testbase/metadata/2");

​    assertEq(uri3, "ipfs://testbase/metadata/3"); // ❌ This shouldn't exist

​    assertEq(uri6, "ipfs://testbase/metadata/6"); // ❌ This shouldn't exist

​    

​    // This creates confusion - external systems get metadata URLs for tokens that were never minted

​    console.log("URI for non-existent item 3:", uri3);

​    console.log("URI for non-existent item 6:", uri6);

}

### Recommended Mitigation

Add validation to ensure the requested item actually exists within the collection:

Copy to clipboard

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

function uri(uint256 tokenId) public view override returns (string memory) {

​    // Handle regular passes (IDs 1-3)

​    if (tokenId <= BACKSTAGE_PASS) {

​        return string(abi.encodePacked("ipfs://beatdrop/", Strings.toString(tokenId)));

​    }

​    

​    // Decode collection and item IDs

​    (uint256 collectionId, uint256 itemId) = decodeTokenId(tokenId);

​    

​    // Check if it's a valid memorabilia token

​    if (collections[collectionId].priceInBeat > 0) {

\+       // Validate that the item actually exists

\+       require(itemId > 0 && itemId < collections[collectionId].currentItemId, "Item does not exist");

​        

​        return string(abi.encodePacked(

​            collections[collectionId].baseUri,

​            "/metadata/",

​            Strings.toString(itemId)

​        ));

​    }

​    

​    return super.uri(tokenId);

}

This ensures that URI calls will fail for non-existent items, providing consistent behavior with the rest of the contract and preventing confusion for external integrators.
