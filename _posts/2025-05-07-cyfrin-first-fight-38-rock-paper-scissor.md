---
layout: post
title: "Cyfrin First Fight 38 - Rock Paper Scissors"
date: 2025-05-07
lang: en
locale: en-GB
categories: solidity blockchain
tags: ctf cyfrin first-fight
description: First Fight 38 - Rock Paper Scissors DApp is a fully decentralized implementation of the classic Rock Paper Scissors game on Ethereum.
image: 
isMath: false
---

Rock Paper Scissors DApp is a fully decentralized implementation of the classic Rock Paper Scissors game on Ethereum. The protocol allows players to compete in a fair and transparent manner with bets placed in ETH or using special Winner Tokens.

This article describes the [First Fight 38](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors) from Cyfrin.

The code is available on [GitHub](https://github.com/CodeHawks-Contests/2025-04-rock-paper-scissors).

[TOC]



## Description

Key features:

- Commit-reveal mechanism ensures fair play (no cheating)
- Support for both ETH and token-based games
- Multiple-turn matches with best-of-N scoring
- Automatic prize distribution and winner token rewards
- Timeout protection against non-responsive players

The smart contract system utilizes a commit-reveal pattern to prevent frontrunning and ensure players cannot see their opponent's move before committing their own.

## All submissions

**High Risk Findings**

H-01. PlayerB Address Can Be Overwritten in joinGameWithEth and joinGameWithToken Functions [Selected submission](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors/s/cm9pvdedb0005la044w93hs7m) by [vito](https://profiles.cyfrin.io/u/vito)

H-02. Players can join games for free[Selected submission](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors/s/cm9lwnrjc0003l204pdhs0j6h) by [5am](https://profiles.cyfrin.io/u/5am)

H-03. [H-1] Denial of Service via ETH Transfer Revert[Selected submission](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors/s/cm9lyebbx0003in046t2i9zo8) by [proofofexploit](https://profiles.cyfrin.io/u/proofofexploit)

H-04. [M-2] Invalid TimeoutReveal When Only One Commit Exists[Selected submission](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors/s/cm9m03owg000dkv04sme11vtm) by [proofofexploit](https://profiles.cyfrin.io/u/proofofexploit)

H-05. RevealMove before Another Player CommitMove Makes Hacker Win All the Multi-Turns Games[Selected submission](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors/s/cm9nw7jay0003lb049th363zm) by [whistleh1995](https://profiles.cyfrin.io/u/whistleh1995)

**Medium Risk Findings**

M-01. Funds received thru receive() are locked🔒[Selected submission](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors/s/cm9v7z09f000hk004kjgzcrta) by [dappscout](https://profiles.cyfrin.io/u/dappscout)

M-02. If a player has won the majority of turns, the losing player can prevent the winning player from receiving rewards[Selected submission](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors/s/cm9pfwle6000hlh042hdxz8hf) by [37h3rn17y2](https://profiles.cyfrin.io/u/37h3rn17y2)

M-03. Lack of Player Address Binding in Move Commitments Allows Replay and Cheating in RockPaperScissors Contract[Selected submission](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors/s/cm9na3tm40003kv041yie1axz) by [bukhara2002](https://profiles.cyfrin.io/u/bukhara2002)

**Low Risk Findings**

L-01. WinningToken Accumulation in the RockPaperScissors Due to Incorrect transferFrom Usage [Selected submission](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors/s/cm9soccpp0005lh04cecnuvrh) by [0x_martonyx](https://profiles.cyfrin.io/u/0x_martonyx)

L-02. [H-01] ETH Rounding Error in RockPaperScissors::_handleTie()[Selected submission](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors/s/cm9po7q4x0003le047xkedsh6) by [0xshaedyw](https://profiles.cyfrin.io/u/0xshaedyw)

L-03. we can cancel the game even before the revealDeadline[Selected submission](https://codehawks.cyfrin.io/c/2025-04-rock-paper-scissors/s/cm9pwe9ct0005jr04yk6poku2) by [lucky2892000](https://profiles.cyfrin.io/u/lucky2892000)

## My submissions

### Height - Function `joinGameWithEth`allows to join a game created with a token as bet

It is possible to join a game where the bet is with a token (`createGameWithToken`without betting the token by calling the function `joinGameWithEth`.

Judge name: Game Staking Inconsistency

#### Summary

It is possible to join a game where the bet is with a token (`createGameWithToken`without betting the token by calling the function `joinGameWithEth`.

#### Vulnerability Details

Concerned function: `joinGameWithEth`

For a game created with `createGameWithToken`, it is possible to join without betting the token by calling the function `joinGameWithEth`.

The check `msg.value == game.bet`will not prevent the attacker to join because since `game.bet`will be set at zero

#### Impact

If the attacker loses the game, no bet token will be transfered to the game creator

##  

#### Tools Used 

Manual analysis / Foundry

PoC

```solidity
function testJoinGameWithTokenThroughETH() public {
        uint256 initialBalance = token.balanceOf(playerB);
        // First create a game with token
        vm.startPrank(playerA);
        token.approve(address(game), 1);
        gameId = game.createGameWithToken(TOTAL_TURNS, TIMEOUT);
        vm.stopPrank();

        vm.startPrank(playerB);
        // Join game though joinGameWithEth
        vm.expectEmit(true, true, false, true);
        emit PlayerJoined(gameId, playerB);

        //game.joinGameWithToken(gameId);
        game.joinGameWithEth(gameId);
        vm.stopPrank();

        // Verify token transfer
        assertEq(token.balanceOf(playerB), initialBalance);
        assertEq(token.balanceOf(address(game)), 1);

        // Verify game state
        (address storedPlayerA, address storedPlayerB,,,,,,,,,,,,,, RockPaperScissors.GameState state) =
            game.games(gameId);

        assertEq(storedPlayerA, playerA);
        assertEq(storedPlayerB, playerB);
        assertEq(uint256(state), uint256(RockPaperScissors.GameState.Created));
    }
```

#### Recommendations

a) use an enum GAME_BET_TYPE to indicate if the bet is with a token or in ether.
Advantage: can be easily extends to add new type of payment

b) Add a second require inside the function `joinGameWithEth` which check the `game.bet`is equal to zero

```solidity
require(game.bet != 0 , "This game requires Token bet");
```



### Low-Two winning tokens are locked in the game smart contract for each token game

Better name from the result: `Minting Instead of Transferring Staked Tokens` or `WinningToken Accumulation in the RockPaperScissors Due to Incorrect transferFrom Usage`

#### Summary

For each token game, there are two winnings/bet tokens locked inside the game smart contract.

#### Vulnerability Details

When a game token is created with the function `createGameWithToken`, the winning token is transfered to the game smart contract.

```solidity
 // Transfer token to contract
 winningToken.transferFrom(msg.sender, address(this), 1);
```

This is also the case when a player B wants to join the game by calling the function `joinGameWithToken`

```solidity
 // Transfer token to contract
winningToken.transferFrom(msg.sender, address(this), 1);
```

But when the winner is chosen, instead of transferred the tokens inside the contract to the winner, the game mints new tokens in the function `_finishTokens`.

```solidity
        // Handle token prizes - winner gets both tokens
        if (game.bet == 0) {
            // Mint a winning token
            winningToken.mint(_winner, 2);
        } else {
            // Mint a winning token for ETH games too
            winningToken.mint(_winner, 1);
        }
```

There is the same problem in the function `_cancelGame`

```solidity
        if (game.bet == 0) {
            if (game.playerA != address(0)) {
                winningToken.mint(game.playerA, 1);
            }
            if (game.playerB != address(0)) {
                winningToken.mint(game.playerB, 1);
            }
        }
```

#### Impact

This design generates several problems:

- The two Winning tokens transferred are locked inside the game contract
- The total supply of the token is "artificially" increased
- The game smart contract must have the minter role on the token, which is not necessary for this use case. It reduces also the possibility in the futur to use another ERC-20 token (e.g USDC) as a winning token for a token game.

```solidity
    function testCompleteTokenGame() public {
        assertEq(token.balanceOf(address(game)), 0);
        gameId = createAndJoinTokenGame();

        // First turn: A=Paper, B=Rock (A wins)
        playTurn(gameId, RockPaperScissors.Move.Paper, RockPaperScissors.Move.Rock);

        // Second turn: A=Rock, B=Scissors (A wins)
        playTurn(gameId, RockPaperScissors.Move.Rock, RockPaperScissors.Move.Scissors);

        // Third turn: A=Paper, B=Scissors (B wins, but A still has more points)
        uint256 tokenBalanceABefore = token.balanceOf(playerA);

        playTurn(gameId, RockPaperScissors.Move.Paper, RockPaperScissors.Move.Scissors);

        // Verify game state
        (,,,,,,,,,,,,, uint8 scoreA, uint8 scoreB, RockPaperScissors.GameState state) = game.games(gameId);

        assertEq(scoreA, 2);
        assertEq(scoreB, 1);
        assertEq(uint256(state), uint256(RockPaperScissors.GameState.Finished));

        // Verify winner received 2 tokens (both players' stakes)
        assertEq(token.balanceOf(playerA) - tokenBalanceABefore, 2);

        // token are locked in the contract
        assertEq(token.balanceOf(address(game)), 2);
    }
```

#### Tools Used 

Foundry

#### Recommendations

Use safeTransferFrom from OpenZeppelin to transfer the token from the game smart contract to the winner instead of minting new tokens.

## Invalid submissions

### RockPaperScissors contract implements custom ownership/admin system instead of using the ownable library from OpenZeppelin

Reason:Non-acceptable severity

#### Summary

RockPaperScissors contract implements custom ownership/admin system instead of using the ownable (or AccessControl) library from OpenZeppelin.

#### Vulnerability Details

While it seems there are no direct vulnerabilities in the implementation, there is no advantage to implement its custom ownership management inside the game contract instead of using the ownable library from OpenZeppelin.
See [https://docs.openzeppelin.com/contracts/5.x/api/access#Ownable](https://docs.openzeppelin.com/contracts/5.x/api/access#Ownable)

Using this library brings several advantage:

- Battle tested and audited contract
- Implements [ERC-173](https://eips.ethereum.org/EIPS/eip-173):
  - Standardized functions to manage ownership
  - Standardized functions emitted when there is a transferred of ownership.
    For example, the custom function `setAdmin`does not emit an event while the OpenZeppelin implementation will emit the event: `emit OwnershipTransferred(oldOwner, newOwner);`
- Reduce the cost of an audit since there is no need to include the OpenZeppelin library in the scope of the contract (save precious money)

#### Impact

- Add unnecessary complexity to the contract
- Does not implement ERC-173 which could make easier to monitor admin/owner change

Additionnaly, the implementation does not respect the following specification:
"**Admin**: The protocol administrator who can update timeout parameters and withdraw accumulated fees
**Contract Owner**: Initially the deployer of the contract, capable of setting a new admin"

Here we can see that there are two different roles: the contract owner and the admin, but only the admin is set at deployment.
This is also why I have increases my initial severity from Low to medium

#### Tools Used

Manual analysis

#### Recommendations

Use the library ownable from OpenZeppelin
OR AccessControl if the author want several separate roles

----

## What I have missed

I missed a lot of vulnerabilities in this contest.

### Summary tab

| Severity | Title                                                        | Summary                                                      | During the contest                                     | Next contest                                          |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------ | ----------------------------------------------------- |
| Hight    | H-01. [H-1] Denial of Service via ETH Transfer Revert        | The contract `RockPaperScissors.sol` attempts to transfer ETH to the winner of a game using a low-level call. If the _winner is a contract that reverts on receiving ETH (e.g., using a receive() function that reverts), the transaction fails and the logic reverts entirely: | -                                                      | Be more attentive to DoS attack                       |
|          | H-02. RevealMove before Another Player CommitMove Makes Hacker Win All the Multi-Turns Games | A critical vulnerability exists in the Rock Paper Scissors game contract where a malicious player can manipulate the game flow to prevent the other player from committing their move. By revealing their move and immediately committing and revealing the next turn's move, the attacker can force the game into a state where the victim cannot commit their move, allowing the attacker to win through timeout. | -                                                      | See H-02                                              |
|          | H-04. [M-2] Invalid TimeoutReveal When Only One Commit Exists | The timeoutReveal() function is intended to allow a game to be canceled when a player fails to reveal their move during the reveal phase. However, the contract allows calling timeoutReveal() even when only one player has committed, which violates the intended flow of the commit-reveal mechanism. |                                                        | See H-02                                              |
|          | H-05. RevealMove before Another Player CommitMove Makes Hacker Win All the Multi-Turns Games | A critical vulnerability exists in the Rock Paper Scissors game contract where a malicious player can manipulate the game flow to prevent the other player from committing their move. By revealing their move and immediately committing and revealing the next turn's move, the attacker can force the game into a state where the victim cannot commit their move, allowing the attacker to win through timeout. |                                                        | See H-02                                              |
| Medium   |                                                              |                                                              |                                                        |                                                       |
|          | M-01. Funds received thru receive() are locked               | The Rock Paper Scissors contract includes a `receive()` function that allows it to accept ETH directly, but provides no mechanism to withdraw this ETH. This creates a permanent ETH lock situation where funds sent directly to the contract become irretrievable. |                                                        | Create a summary about managing ETH inside a contract |
|          | M-02. If a player has won the majority of turns, the losing player can prevent the winning player from receiving rewards | Game does not finish even after a player has won the majority of turns. Since the opponent has essentially lost, the opponent has no incentive to continue playing. The opponent can refuse to play (commit) the remaining turns. This causes the game to be unable to reach `Finished` state, hence preventing the distribution of rewards to the winning player. In this game state, there are several resolution cases, all of which harms the winning player (detailed below) and results in the winning player not able to receive their rightful rewards, with 1 case even benefitting the losing player. This severely disrupts the fairness of the game. |                                                        | See H-02                                              |
|          | M-03. Lack of Player Address Binding in Move Commitments Allows Replay and Cheating in RockPaperScissors Contract | The `RockPaperScissors` smart contract fails to bind player addresses to their committed moves, allowing malicious actors to reuse or intercept another player's commitment. This vulnerability undermines the fairness of the game and opens the door for replay attacks or unauthorized move revelations. | I found salt weak but couldn't make it a vulnerability | Dig more                                              |
| Low      |                                                              |                                                              |                                                        |                                                       |
|          | L-02. [H-01] ETH Rounding Error in RockPaperScissors::_handleTie() | The `_handleTie() function` contains an integer division rounding error that causes permanent loss of ETH during tie resolution. This occurs when refunding players after deducting protocol fees from the total pot. | Found the vulnerability but failed to do a valid POC   | Dig more + submit vulnerability even without PoC      |
|          | L-03. we can cancel the game even before the revealDeadline  | playerA creates the game and sent the gameId to playerB to participate. As there is flaw in this `RockPaperScissors::timeoutReveal` playerB can be able to cancel the game even before the deadline time and playerA who created the game itself cant participate in the game |                                                        | See H-02                                              |



### H-03. [H-1] Denial of Service via ETH Transfer Revert

#### Description:

The contract `RockPaperScissors.sol` attempts to transfer ETH to the winner of a game using a low-level call. If the _winner is a contract that reverts on receiving ETH (e.g., using a receive() function that reverts), the transaction fails and the logic reverts entirely:

```solidity
(bool success,) = _winner.call{value: prize}("");
require(success, "Transfer failed");

```

This allows a malicious player to win a game and then block its resolution entirely by refusing the payout, causing the game to be stuck in a pending state indefinitely. This constitutes a Denial of Service (DoS) vector

**So**

If the _winner is an attacking contract, its receive() can do this:

```solidity
receive() external payable {

​    revert("I don't want your ETH");

}
```

This results in:

- call{value:} fails
- success == false
- require(success, ...) rolls back all execution
- The game is not marked as over
- Funds are stuck
- No one can advance

#### Impact:

- The game cannot be marked as finished.
- No prize can be withdrawn.
- Funds remain locked in the contract.
- The DoS is fully reproducible and prevents normal game flow.
- Admin has no override mechanism.
- Critical game logic is tightly coupled with external code execution

#### Proof of Concept:

- A test contract called RPS_DoS.t.sol has been created for the proof of concept.
- To run the test, simply execute:

#### Recommended mitigation

```solidity
mapping(address => uint256) public pendingWithdrawals;

// Instead of sending ETH directly:
pendingWithdrawals[_winner] += prize;

function withdraw() external {
    uint256 amount = pendingWithdrawals[msg.sender];
    require(amount > 0, "Nothing to withdraw");
    pendingWithdrawals[msg.sender] = 0;
    (bool success,) = msg.sender.call{value: amount}("");
    require(success, "Withdraw failed");
}

```



----

### M-01. Funds received throw receive() are locked

#### Summary

The Rock Paper Scissors contract includes a `receive()` function that allows it to accept ETH directly, but provides no mechanism to withdraw this ETH. This creates a permanent ETH lock situation where funds sent directly to the contract become irretrievable.

#### Vulnerability Details

The contract includes a `receive()` function that accepts ETH without any restrictions:

```
/**
 * @dev Fallback function to accept ETH
 */
receive() external payable {
    // Allow contract to receive ETH
}
```

However, the only ETH withdrawal mechanism in the contract is the `withdrawFees()` function, which only allows the admin to withdraw from the `accumulatedFees` variable:

```
function withdrawFees(uint256 _amount) external {
    require(msg.sender == adminAddress, "Only admin can withdraw fees");

    uint256 amountToWithdraw = _amount == 0 ? accumulatedFees : _amount;
    require(amountToWithdraw <= accumulatedFees, "Insufficient fee balance");

    accumulatedFees -= amountToWithdraw;

    (bool success,) = adminAddress.call{value: amountToWithdraw}("");
    require(success, "Fee withdrawal failed");

    emit FeeWithdrawn(adminAddress, amountToWithdraw);
}
```

The problem is that ETH sent through the `receive()` function:

1. Is added to the contract's general balance
2. Is not tracked in the `accumulatedFees` variable
3. Cannot be withdrawn through the `withdrawFees()` function
4. Has no other withdrawal mechanism

#### Impact

This vulnerability has medium impact because:

1. Any ETH sent directly to the contract (not through game functions) is permanently locked
2. Users or admins who accidentally send ETH to the contract address will lose those funds
3. There is no recovery mechanism for these locked funds

This issue is compounded because having a `receive()` function explicitly signals that the contract is designed to accept ETH, yet that ETH becomes trapped.

#### Recommendations

There are two possible approaches to fix this vulnerability:

**Option 1: Remove the receive function**

```
// Remove this function entirely
// receive() external payable {
//     // Allow contract to receive ETH
// }
```

This prevents ETH from being sent directly to the contract, making the contract behavior clearer.

**Option 2: Add a withdrawal mechanism for all contract balance**

Either approach would prevent ETH from being permanently locked in the contract.
