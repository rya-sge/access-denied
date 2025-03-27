// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.28;

import "@openzeppelin/access/Ownable.sol";
import "@openzeppelin/utils/cryptography/ECDSA.sol";

contract Revengery is Ownable{
    bool public solved;
    address public immutable signer_addr;

    constructor() Ownable(msg.sender) {
        solved = false;
        // signer_pubkey = 039e1b969068ba94e6c0f80a62c48a2406412dcb7043b9aa360b788097e7e9fd65
        signer_addr = 0x8E2227b11dd10a991b3CB63d37276daC4E4b9417;
    }

    /**
     * Only the owner can solve the challenge ;)
     */
    function solve() external onlyOwner{
        solved = true;
    }

    /**
     * Is the challenge solved ?
     */
    function isSolved() public view returns (bool) {
        return solved;
    }

    /**
     * @dev Change owner
     * @param signature signature of the hash
     * @param hash hash of the message authenticating the new owner
     * @param newOwner address of the new owner
     */
    function changeOwner(bytes memory signature, bytes32 hash, address newOwner) public {
        require(newOwner != address(0), "New owner should not be the zero address");
        require(hash != bytes32(0), "Not this time");
        // Check signature
        address _signer = ECDSA.recover(hash, signature);
        // Check is signer
        require(signer_addr == _signer, "New owner should have been authenticated by the signer");
        // Vulnerable to replay attack
        _transferOwnership(newOwner);
    }
}
