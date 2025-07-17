# Understanding the Commit-Reveal Scheme in Solidity (with Example)

When designing decentralized applications (dApps) on Ethereum, developers often face challenges related to fairness and secrecy, especially in games or auctions. A common solution to prevent cheating or front-running in such situations is the **commit-reveal scheme**.

This article walks you through what a commit-reveal scheme is, why it’s useful, and how you can implement a simple version in Solidity.

------

## What is the Commit-Reveal Scheme?

The **commit-reveal scheme** is a two-phase protocol often used in blockchain applications to securely collect inputs (like votes, bids, or random numbers) without revealing them upfront.

### 🔐 Phase 1: Commit

Participants submit a *commitment*, usually a hash of their actual value combined with a secret (a nonce). This hides the real value but proves that the value was chosen ahead of time.

### 🔓 Phase 2: Reveal

Participants reveal their actual value and secret. The contract checks the hash against the commitment to verify authenticity.

------

## Why Use It?

In Ethereum, all transactions are public and visible before being confirmed. If one player submits their move in a game or their bid in an auction, others can see it and potentially gain an unfair advantage. The commit-reveal scheme prevents this by:

- Hiding values until everyone has committed
- Ensuring revealed values match their commitments

------

## Solidity Example

Let’s implement a simple commit-reveal game where two players submit a secret number, and the higher number wins.

```solidity
solidityCopyEdit// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CommitRevealGame {
    struct Player {
        bytes32 commitment;
        uint revealedNumber;
        bool hasCommitted;
        bool hasRevealed;
    }

    address public player1;
    address public player2;
    mapping(address => Player) public players;

    enum Phase { Commit, Reveal, Complete }
    Phase public currentPhase;

    constructor(address _player2) {
        player1 = msg.sender;
        player2 = _player2;
        currentPhase = Phase.Commit;
    }

    function commit(bytes32 _commitment) external {
        require(currentPhase == Phase.Commit, "Not in commit phase");
        require(msg.sender == player1 || msg.sender == player2, "Not a player");
        require(!players[msg.sender].hasCommitted, "Already committed");

        players[msg.sender].commitment = _commitment;
        players[msg.sender].hasCommitted = true;

        if (players[player1].hasCommitted && players[player2].hasCommitted) {
            currentPhase = Phase.Reveal;
        }
    }

    function reveal(uint _number, string memory _secret) external {
        require(currentPhase == Phase.Reveal, "Not in reveal phase");
        require(players[msg.sender].hasCommitted, "Must commit first");
        require(!players[msg.sender].hasRevealed, "Already revealed");

        bytes32 hash = keccak256(abi.encodePacked(_number, _secret));
        require(hash == players[msg.sender].commitment, "Invalid reveal");

        players[msg.sender].revealedNumber = _number;
        players[msg.sender].hasRevealed = true;

        if (players[player1].hasRevealed && players[player2].hasRevealed) {
            currentPhase = Phase.Complete;
        }
    }

    function getWinner() external view returns (address winner) {
        require(currentPhase == Phase.Complete, "Game not finished");

        uint num1 = players[player1].revealedNumber;
        uint num2 = players[player2].revealedNumber;

        if (num1 > num2) return player1;
        if (num2 > num1) return player2;
        return address(0); // Draw
    }
}
```