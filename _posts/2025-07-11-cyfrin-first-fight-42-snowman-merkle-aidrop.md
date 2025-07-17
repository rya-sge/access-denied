---
layout: post
title: "Cyfrin First Fight 42 - Snowman Merkle Airdrop"
date: 2025-07-11
lang: en
locale: en-GB
categories: solidity blockchain
tags: ctf cyfrin first-fight
description: First Fight 41 - Airdrop protocol on Ethereum.
image: 
isMath: false
---

The protocol integrates three smart contracts—**Snow.sol**, **Snowman.sol**, and **SnowmanAirdrop.sol**—to bridge ERC20 and ERC721 assets. 

- **Snow.sol** is an ERC20 token that can be earned or purchased and staked to claim **Snowman** NFTs.
-  **Snowman.sol** is a fully on-chain ERC721 contract storing metadata via Base64 encoding. 
- The **SnowmanAirdrop** contract uses Merkle trees and signatures for efficient NFT distribution, enabling direct or delegated claims. Together, these contracts enable seamless staking and airdrop mechanics across tokens and NFTs.

This article describes the [First Fight 42](https://codehawks.cyfrin.io/c/2025-06-snowman-merkle-airdrop) from Cyfrin.

The code is available on [GitHub](https://github.com/CodeHawks-Contests/2025-06-snowman-merkle-airdrop).

[TOC]



## Description

- `Snow.sol`:

  The `Snow` contract is an `ERC20` token that automatically makes one eligible to claim a `Snowman NFT`.

  The `Snow` token is staked in the `SnowmanAirdrop` contract, and the staker receives `Snowman` NFTs in the value of how many `Snow` tokens they own.

  The `Snow` token can either be earned for free onece a week, or bought at anytime, up until during the `::FARMING_DURATION` is over.

  The `Snow` token can be bought with either `WETH` or native `ETH`.

- `Snowman.sol`:

  The `Snowman` contract is an `ERC721` contract that utilizes `Base64` encoding to achieve total on-chain storage.

  Stakers of the Snow token receive this NFT.

- `SnowmanAirdrop.sol`:

  The `SnowmanAirdrop` contract utilizes `Merkle` trees implementation for a more efficient airdrop system.

  Recipients can either claim a `Snowman` NFT themselves, or have someone claim on their behalf using the recipient's `v`, `r`, `s` signatures.

  Recipients stake

## Valid submissions

### H1-Anyone can mint Snowman NFT (Lack of access control) / Unrestricted NFT mint function

#### Root + Impact

#### Description

In normal behavior, the `mintSnowman` function is intended to be called by a trusted contract (such as an airdrop distributor) to mint Snowman NFTs to eligible users based on off-chain logic or Merkle proofs. In this project, this contract is S**nowmanAidrop**

However, the function is marked `external` and lacks any form of access control. This allows **any arbitrary external address** to call `mintSnowman`, minting an unlimited number of NFTs to themselves or others without restriction.

```solidity
function mintSnowman(address receiver, uint256 amount) external {
        for (uint256 i = 0; i < amount; i++) {
            _safeMint(receiver, s_TokenCounter);

            emit SnowmanMinted(receiver, s_TokenCounter);

            s_TokenCounter++;
        }
    }
```



#### Risk

**Likelihood**:

- This will occur any time an attacker directly interacts with the contract and invokes `mintSnowman`, since there is no modifier or check preventing public access.
- It does not require any special privileges or prior conditions; a standard external call from a web3 wallet or script is sufficient.

**Impact**:

- Unlimited and unauthorized minting of NFTs, leading to total dilution of supply and value.
- Project credibility may suffer significantly if an attacker exploits this to flood the market

#### Proof of Concept

Add the following test in the test contract TestSnowman

```solidity
function testMintSnowmanAccessControl() public {

        // Alice mint tokens to herself

        vm.prank(alice);

       nft.mintSnowman(alice, 1);

       assert(nft.ownerOf(0) == alice);

   }
```



#### Recommended Mitigation

Restrict access to only an authorized minter, such as the airdrop contract:

```diff
\+ SnowmanAirdrop private immutable i_airdrop;

\+ error Unauthorized();



\+ modifier onlyAirdrop() {

\+     if (msg.sender != address(i_airdrop)) revert Unauthorized();

\+     _;

\+ }



function mintSnowman(address receiver, uint256 amount)

\-     external {

\+     external onlyAirdrop {



    for (uint256 i = 0; i < amount; i++) {

        _safeMint(receiver, s_TokenCounter);

       emit SnowmanMinted(receiver, s_TokenCounter);

        s_TokenCounter++;

    }

}
```

This ensures that only the intended contract (here the airdrop distributor) can mint NFTs, preventing unauthorized access.



### L-02.E IP-712 Typehash has a typo error (Hight)

Note: severity was considered hight by the judges

Other name: Inconsistent MESSAGE_TYPEHASH with standard EIP-712 declaration

#### Root + Impact

#### Description

The `claimSnowman` function relies on an EIP-712 signature to verify that the receiver is authorized to claim their Snowman NFTs. The signature hash is constructed using a `MESSAGE_TYPEHASH` constant intended to represent the typed data struct `SnowmanClaim(address receiver, uint256 amount)`.



However, the declared `MESSAGE_TYPEHASH` uses a malformed type string with a typo (`addres` instead of `address`), causing the resulting signature hash to be invalid if not taking into account and **ensuring that such signed message will ever verify correctly**.

```solidity
// Root cause in the codebase with @> marks to highlight the relevant section

bytes32 private constant MESSAGE_TYPEHASH = keccak256("SnowmanClaim(addres receiver, uint256 amount)");
```



#### Risk

**Likelihood**:


Weak because it is more likely that the receiver will use information from the contracts, e.g. by calling the getMessageHash function

**Impact**:

Invalid signature if the receiver does not take into account the typo in his signature

#### Proof of Concept

No PoC

#### Recommended Mitigation

```solidity
\- bytes32 private constant MESSAGE_TYPEHASH = keccak256("SnowmanClaim(addres receiver, uint256 amount)");

\+ bytes32 private constant MESSAGE_TYPEHASH = keccak256("SnowmanClaim(address receiver, uint256 amount)");


```

### H03-claimSnowman uses live balance, risk of invalid proof (Medium)

Note: severity was considered Medium by the judges.

Other name: Invalid merkle-proof as a result of snow balance change before claim action

#### Root + Impact

#### Description

- The airdrop contract allows eligible users to claim Snowman NFTs by proving their entitlement via an EIP-712 signature and a Merkle proof based on their `Snow` token balance.

- However, the Merkle leaf is constructed dynamically using the user's **current** `Snow` token balance (via `balanceOf`) instead of a fixed amount determined at the time of snapshot, as welle as the signature through `getMessageHash` .

  
  If the balance of the user changes, This results in invalid signature and **proof mismatches** and failed claims.

```solidity
function claimSnowman(address receiver, bytes32[] calldata merkleProof, uint8 v, bytes32 r, bytes32 s)
        external
        nonReentrant
    {
        if (receiver == address(0)) {
            revert SA__ZeroAddress();
        }
      // @audit
        if (i_snow.balanceOf(receiver) == 0) {
            revert SA__ZeroAmount();
        }

        if (!_isValidSignature(receiver, getMessageHash(receiver), v, r, s)) {
            revert SA__InvalidSignature();
        }
      // @audit
        uint256 amount = i_snow.balanceOf(receiver);

        bytes32 leaf = keccak256(bytes.concat(keccak256(abi.encode(receiver, amount))));

        if (!MerkleProof.verify(merkleProof, i_merkleRoot, leaf)) {
            revert SA__InvalidProof();
        }

        i_snow.safeTransferFrom(receiver, address(this), amount); // send tokens to contract... akin to burning

        s_hasClaimedSnowman[receiver] = true;

        emit SnowmanClaimedSuccessfully(receiver, amount);

        i_snowman.mintSnowman(receiver, amount);
    }

function getMessageHash(address receiver) public view returns (bytes32) {
        if (i_snow.balanceOf(receiver) == 0) {
            revert SA__ZeroAmount();
        }
       @audit here
        uint256 amount = i_snow.balanceOf(receiver);

        return _hashTypedDataV4(
            keccak256(abi.encode(MESSAGE_TYPEHASH, SnowmanClaim({receiver: receiver, amount: amount})))
        );
    }
```



#### Risk

**Impact**:

**Likelihood**:

A Merkle tree snapshot is generated using a fixed balance at a specific time, and a user changes their balance **after snapshot** but before claiming.

A signature is made by a specific receiver before a change with its Snow balance.

**Impact**:

- Users are **unable to claim **their Snowman NFTs if their balance changes even if they were eligible at snapshot time.
- Airdrop becomes **inaccessible** to a significant portion of users who moved tokens, breaking the trust and usability of the system.
- An attacker may attempt to transfer small portions of tokens to invalidate the evidence and make it more difficult, or even impossible, to claim the airdrop.

#### Proof of Concept

Add the following test in TestSnowmanAirdrop

Here, Bob, our malicious attacker, transfers token to Alice to make the signature verification and merkle proof invalid

Contract will revert with `SA__InvalidSignature()`

The reason is because the signature is checked with `getMessageHash`which uses the live balance

```solidity
 function testClaimSnowmanFailedProof() public {

        // Alice claim test

        assert(nft.balanceOf(alice) == 0);

        vm.prank(alice);

        snow.approve(address(airdrop), 1);



        // Get alice's digest

        bytes32 alDigest = airdrop.getMessageHash(alice);



        // alice signs a message

        (uint8 alV, bytes32 alR, bytes32 alS) = vm.sign(alKey, alDigest);



        // malicious bob transfers tokens to Alice
        vm.prank(bob);

        snow.transfer(alice, 1);



        // satoshi calls claims on behalf of alice using her signed message

        // Revert because wrong proof

        vm.prank(satoshi);

        airdrop.claimSnowman(alice, AL_PROOF, alV, alR, alS);

    }
```



#### Recommended Mitigation

Verify `amount` via Merkle proof instead of computing it from `balanceOf`.

Change the function getMessageHash too to take the amount in parameter instead of using the live balance

Require also to fix **M01- s_hasClaimedSnowman is not checked in claimSnowman**

```solidity
\-  if (i_snow.balanceOf(receiver) == 0) {

\-        revert SA__ZeroAmount();

\- }

\- uint256 amount = i_snow.balanceOf(receiver);

\+ error AlreadyClaimed();

\+ function claimSnowman(address receiver, uint256 amount, ...) external {

\+  require(!s_hasClaimedSnowman[receiver], AlreadyClaimed());

\+   bytes32 leaf = keccak256(abi.encodePacked(receiver, amount));

​    ...

}

\- function getMessageHash(address receiver)

\+ function getMessageHash(address receiver, uint256 amount)
```

### M01- s_hasClaimedSnowman is not checked in claimSnowman (low)

Note: severity was considered Low by the judges

#### Root + Impact

#### Description

The principle of an airdrop is to authorize the claim for a same user only once
The function `claimSnowman`allows multiple claims as long as the user has tokens.

While, this feature can certainly be desired by the project author, at the end of the function however, a mapping is updated to indicate that the receiver has claimed. So we can assume that the function should only be called once.

```solidity
// Root cause in the codebase with @> marks to highlight the relevant section

​    function claimSnowman(address receiver, bytes32[] calldata merkleProof, uint8 v, bytes32 r, bytes32 s)

​        external

​        nonReentrant

​    {

​        if (receiver == address(0)) {

​            revert SA__ZeroAddress();

​        }

​        if (i_snow.balanceOf(receiver) == 0) {

​            revert SA__ZeroAmount();

​        }



​        if (!_isValidSignature(receiver, getMessageHash(receiver), v, r, s)) {

​            revert SA__InvalidSignature();

​        }



​        uint256 amount = i_snow.balanceOf(receiver);



​        bytes32 leaf = keccak256(bytes.concat(keccak256(abi.encode(receiver, amount))));



​        if (!MerkleProof.verify(merkleProof, i_merkleRoot, leaf)) {

​            revert SA__InvalidProof();

​        }



​        i_snow.safeTransferFrom(receiver, address(this), amount); // send tokens to contract... akin to burning



​       // @audit here

​      s_hasClaimedSnowman[receiver] = true;



​        emit SnowmanClaimedSuccessfully(receiver, amount);



​        i_snowman.mintSnowman(receiver, amount);

​    }
```



#### Risk

**Likelihood**:

- A receiver or someone with the signature calls the function twice or more

**Impact**:

- Behavior not anticipated by the project authors
  - If the receiver has received some new Snow tokens since the first claim, he can claim twice
  - Otherwise, the function will revert (SA__ZeroAmount())

#### Proof of Concept

Here Alice claims again after receing tokens from another token holder, Bob

```solidity
  function testClaimSnowmanTwice() public {

​        // Alice claim test

​        assert(nft.balanceOf(alice) == 0);

​        vm.prank(alice);

​        snow.approve(address(airdrop), 2);



​        // Get alice's digest

​        bytes32 alDigest = airdrop.getMessageHash(alice);



​        // alice signs a message

​        (uint8 alV, bytes32 alR, bytes32 alS) = vm.sign(alKey, alDigest);



​        // satoshi calls claims on behalf of alice using her signed message

​        vm.prank(satoshi);

​        airdrop.claimSnowman(alice, AL_PROOF, alV, alR, alS);



​        assert(nft.balanceOf(alice) == 1);

​        assert(nft.ownerOf(0) == alice);



​        // Transfer of Snow tokens Bob -> Alice

​        vm.prank(bob);

​        snow.transfer(alice, 1);



​        // Alice claims Again

​        airdrop.claimSnowman(alice, AL_PROOF, alV, alR, alS);

​        assert(nft.balanceOf(alice) == 2);

​        assert(nft.ownerOf(1) == alice);

​    }
```



#### Recommended Mitigation

```solidity
\- remove this code

\+ add this code



In the contract:

\+ error AlreadyClaimed();


In the function claimSnowman, at the beginning

\+  require(!s_hasClaimedSnowman[receiver], AlreadyClaimed());
```

## Invalid submissions

### H02-Risk of overpaying fees for the users with buySnow

Reason:Non-acceptable severity

#### Root + Impact

#### Description

The `buySnow` function allows users to purchase `Snow` tokens by either sending ETH directly or paying with WETH. The function attempts to determine the payment method based on whether the `msg.value` exactly matches the required ETH fee (`s_buyFee * amount`). If not, it falls back to attempting a WETH `safeTransferFrom`.

As the result, the function`buySnow` function can **take more fees than intended** due to imprecise ETH value matching and silent fallback to WETH.

The specific issue is that this logic is **ambiguous and unsafe**. Users who mistakenly overpay or underpay by even 1 wei will silently trigger a WETH transfer, which may fail if WETH has not been approved. This causes **unexpected reverts**, poor UX, and the most severe this introduces **financial risk for users** and undermines trust in the token mechanics.

Additionally, there's no way for the user to explicitly choose the payment method, leading to unpredictable behavior.

  

```solidity
    function buySnow(uint256 amount) external payable canFarmSnow {
        if (msg.value == (s_buyFee * amount)) {
            _mint(msg.sender, amount);
        } else {
            i_weth.safeTransferFrom(msg.sender, address(this), (s_buyFee * amount));
            _mint(msg.sender, amount);
        }
​
        s_earnTimer = block.timestamp;
​
        emit SnowBought(msg.sender, amount);
    }
```



#### Risk

**Likelihood**:

- This occurs whenever a user provides an incorrect ETH value (overpaying or underpaying by any amount), which is common due to frontend inconsistencies or slippage buffers.
- This also occurs when a user unknowingly relies on WETH payment without approving the correct allowance beforehand.

**Impact**:

- Users experience failed transactions and wasted gas due to unintuitive fallback behavior.
- **financial risk for users** and undermines trust in the token mechanics.

#### Proof of Concept

Add the following test in TestSnow

Here the contract will take WETH as fees + the value of msg.value (here 1 wei). As a result, it will collects more fees as intended

```solidity
   function testCanBuySnowWithWEthAndContractTakeAlsoMsgValue() public {

​        assert(jerry.balance ==  0);

​        vm.deal(jerry, 1 wei);

​        // In the past, the sender has approved the Snow contract

​        vm.startPrank(jerry);

​        weth.approve(address(snow), FEE);



​        // Now he want to pay with ETH but the amount is too low

​        // As a result the contract takes the weth amount and msg.value

​        snow.buySnow{value: 1 wei}(1);

​        vm.stopPrank();



​        assert(weth.balanceOf(address(snow)) == FEE);

​        assert(snow.balanceOf(jerry) == 1);

​        assert(address(snow).balance == 1 wei);

​        assert(jerry.balance ==  0);

​    }
```



#### Recommended Mitigation

Separate the two different methods of payment in two functions.

Ensures clear and intentional user behavior, removes ambiguity, and prevents unintentional failures or misuse.

```solidity
\- function buySnow(uint256 amount) external payable canFarmSnow {

\-     if (msg.value == (s_buyFee * amount)) {

\-         _mint(msg.sender, amount);

\-     } else {

\-         i_weth.safeTransferFrom(msg.sender, address(this), (s_buyFee * amount));

\-         _mint(msg.sender, amount);

\-     }

\-     s_earnTimer = block.timestamp;

\-     emit SnowBought(msg.sender, amount);

\- }

+error InvalidETHAmount();

\+ function buySnowWithETH(uint256 amount) external payable canFarmSnow {

\+     uint256 cost = s_buyFee * amount;

\+     if (msg.value !!= cost) revert InvalidETHAmount();

\+     _mint(msg.sender, amount);

\+     emit SnowBought(msg.sender, amount);

\+ }



\+ function buySnowWithWETH(uint256 amount) external canFarmSnow {

\+     uint256 cost = s_buyFee * amount;

\+     i_weth.safeTransferFrom(msg.sender, address(this), cost);

\+     _mint(msg.sender, amount);

\+     emit SnowBought(msg.sender, amount);

\+ }
```



## Missing  submissions

### L-02. Global Timer Reset in Snow::buySnow Denies Free Claims for All Users

Only one low has bee missed: L-02. Global Timer Reset in Snow::buySnow Denies Free Claims for All Users
Reason: I see the vulnerability but have forgotten to submit it

The `Snow::buySnow` function contains a critical flaw where it resets a global timer `(s_earnTimer)` to the current block timestamp on every invocation. This timer controls eligibility for free token claims via `Snow::earnSnow()`, which requires 1 week to pass since the last timer reset. As a result:

Any token purchase `(via buySnow)` blocks all free claims for all users for 7 days

Malicious actors can permanently suppress free claims with micro-transactions

Contradicts protocol documentation promising **"free weekly claims per user"**

#### Impact:

- **Complete Denial-of-Service:** Free claim mechanism becomes unusable
- **Broken Protocol Incentives:** Undermines core user acquisition strategy
- **Economic Damage:** Eliminates promised free distribution channel
- **Reputation Harm:** Users perceive protocol as dishonest

```
    function buySnow(uint256 amount) external payable canFarmSnow {
        if (msg.value == (s_buyFee * amount)) {
            _mint(msg.sender, amount);
        } else {
            i_weth.safeTransferFrom(msg.sender, address(this), (s_buyFee * amount));
            _mint(msg.sender, amount);
        }

  @>      s_earnTimer = block.timestamp;

        emit SnowBought(msg.sender, amount);
    }
```

#### Risk

**Likelihood**:

• Triggered by normal protocol usage (any purchase) • Requires only one transaction every 7 days to maintain blockage • Incentivized attack (low-cost disruption)

**Impact**:

• Permanent suppression of core protocol feature • Loss of user trust and adoption • Violates documented tokenomics

#### Proof of Concept

**Attack Scenario:** Permanent Free Claim Suppression

- Attacker calls **buySnow(1)** with minimum payment
- **s_earnTimer** sets to current timestamp (T0)
- All **earnSnow()** calls revert for **next 7 days**
- On day 6, attacker repeats **buySnow(1)**
- New timer reset (T1 = T0+6 days)
- Free claims blocked until **T1+7 days (total 13 days)**
- Repeat step **4 every 6 days → permanent blockage** **Test Case:**

```solidity
// Day 0: Deploy contract
snow = new Snow(...);  // s_earnTimer = 0

// UserA claims successfully
snow.earnSnow(); // Success (first claim always allowed)

// Day 1: UserB buys 1 token
snow.buySnow(1); // Resets global timer to day 1

// Day 2: UserA attempts claim
snow.earnSnow(); // Reverts! Requires day 1+7 = day 8

// Day 7: UserC buys 1 token (day 7 < day 1+7)
snow.buySnow(1); // Resets timer to day 7

// Day 8: UserA retries
snow.earnSnow(); // Still reverts! Now requires day 7+7 = day 14
```

#### Recommended Mitigation

**Step 1:** Remove Global Timer Reset from `buySnow`

```solidity
function buySnow(uint256 amount) external payable canFarmSnow {
     // ... existing payment logic ...
-     s_earnTimer = block.timestamp;
       emit SnowBought(msg.sender, amount);
}
```

**Step 2:** Implement Per-User Timer in `earnSnow`

```solidity
// Add new state variable
mapping(address => uint256) private s_lastClaimTime;

function earnSnow() external canFarmSnow {
    // Check per-user timer instead of global
    if (s_lastClaimTime[msg.sender] != 0 && 
        block.timestamp < s_lastClaimTime[msg.sender] + 1 weeks
    ) {
        revert S__Timer();
    }
    
    _mint(msg.sender, 1);
    s_lastClaimTime[msg.sender] = block.timestamp; // Update user-specific timer
    emit SnowEarned(msg.sender, 1); // Add missing event
}
```

**Step 3:** Initialize First Claim (Constructor)

```solidity
constructor(...) {
    // Initialize with current timestamp to prevent immediate claims
    s_lastClaimTime[address(0)] = block.timestamp;
}
```
