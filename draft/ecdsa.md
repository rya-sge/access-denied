





```solidity
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
        address _signer = ECDSA.recover(hash, signature);
        require(signer_addr == _signer, "New owner should have been authenticated by the signer");
        _transferOwnership(newOwner);
    }
}

```





### 1. **Lack of proper validation on the `hash`**

- The `hash` parameter is passed as an argument, but there’s no validation that ensures it has been created in a proper way or that it actually represents the data (e.g., a message) being signed.
- If the hash is not properly constructed (for example, a different message or transaction), the system could be tricked into accepting invalid signatures. 
- See this warning from OpenZeppelin: [TryRecover](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/acd4ff74de833399287ed6b31b4debf6b2b35527/contracts/utils/cryptography/ECDSA.sol#L46), [ recover](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/acd4ff74de833399287ed6b31b4debf6b2b35527/contracts/utils/cryptography/ECDSA.sol#L85)

**Solution**: You should make sure that the `hash` is created correctly and corresponds to the intended message. It is common to hash the data like `keccak256` of the relevant information (e.g., the contract address and transaction details) before signing.

```solidity
bytes32 messageHash = keccak256(abi.encodePacked(address(this), newOwner));
```

### 2. **Signature Replay Risk**

If the `signature` is used to authenticate a change in the owner, it's essential to ensure that the signature is unique to the transaction (non-replayable). This means the signature should contain a timestamp or a nonce to prevent attackers from reusing valid signatures to trigger the same ownership change again.

**Solution**: Add a mechanism to prevent replay attacks by incorporating a nonce or timestamp in the signature validation. You can include a nonce (a unique identifier for each transaction) to ensure the signature can't be replayed.

```
uint256 nonce;
```

And the hash should be built like:

```
bytes32 messageHash = keccak256(abi.encodePacked(address(this), newOwner, nonce));
```

You should also ensure the nonce value is updated after each change to prevent replay of the same signature.



## 3 ECDA Signature malleability

# ECDSA signature malleability

The `ecrecover` EVM precompile allows for malleable (non-unique) signatures:this function rejects them by requiring the `s` value to be in the lowerhalf order, and the `v` value to be either 27 or 28.

  EIP-2 still allows signature malleability for ecrecover(). Remove this possibility and make the signature
        // unique. Appendix F in the Ethereum Yellow paper (https://ethereum.github.io/yellowpaper/paper.pdf), defines
        // the valid range for s in (301): 0 < s < secp256k1n ÷ 2 + 1, and for v in (302): v ∈ {27, 28}. Most
        // signatures from current libraries generate a unique signature with an s-value in the lower half order.
        //
        // If your library generates malleable signatures, such as s-values in the upper range, calculate a new s-value
        // with 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141 - s1 and flip v from 27 to 28 or
        // vice versa. If your library also generates signatures with 0/1 for v instead 27/28, add 27 to v to accept
        // these malleable signatures as well.

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/acd4ff74de833399287ed6b31b4debf6b2b35527/contracts/utils/cryptography/ECDSA.sol#L143

### OpenZeppelin

The functions `ECDSA.recover` and `ECDSA.tryRecover` are vulnerable to a kind of signature malleability due to accepting EIP-2098 compact signatures in addition to the traditional 65 byte signature format. This is only an issue for the functions that take a single `bytes` argument, and not the functions that take `r, v, s` or `r, vs` as separate arguments.

The potentially affected contracts are those that implement signature reuse or replay protection by marking the signature itself as used rather than the signed message or a nonce included in it. A user may take a signature that has already been submitted, submit it again in a different form, and bypass this protection.

https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-4h98-2769-gh6h

ECDSA in Solidity



1) ECDSA rappel
2) 

To implement signature, the best solution is to use a proof and secure library. The best solution is this one developed by OpenZeppelin which is battle tested.

This library adds some supplementary check  to avoid the malleability of  (non-unique) signature affecting the library ECDA

Moreover, they also add égalment to allow a signature from a smart contract

Important points to think :

1) You need to protect your code against replay attacker. 

   A possibile solution is to store the signature in a hashmap after its use.



**ECRecover**

The EVM offers an opcode to recover an address  from a signature. But this opocpde suffers from a vulnerability allowing malleable (non-unique) signature

The OpenZeppelin library fixes this issue :

>  * this function rejects them by requiring the `s` value to be in the lower
>  * half order, and the `v` value to be either 27 or 28.

Source: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.8.2/contracts/utils/cryptography/ECDSA.sol#L39



According to the OpenZeppelin documentation,

 * IMPORTANT: `hash` _must_ be the result of a hash operation for the
     * verification to be secure: it is possible to craft signatures that recover to arbitrary addresses for non-hashed data. A safe way to ensure this is by receiving a hash of the original message (which may otherwise be too long), and then calling {toEthSignedMessageHash} on it.

Generate the signature :

https://web3js.readthedocs.io/en/v1.3.4/web3-eth-accounts.html#sign[Web3.js]

https://docs.ethers.io/v5/api/signer/#Signer-signMessage[ethers]





## EIP

EIP-2 still allows signature malleability for ecrecover().

https://eips.ethereum.org/EIPS/eip-2098[EIP-2098 short signatures]

Returns an Ethereum Signed Typed Data, created from a
     * `domainSeparator` and a `structHash`. 

### EIP-191 : Ethereum signed message

```
keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash));
```

Any EIP-191 `signed_data` can never be an Ethereum transaction.

```solidity
function signatureBasedExecution(address target, uint256 nonce, bytes memory payload, uint8 v, bytes32 r, bytes32 s) public payable {
        
    // Arguments when calculating hash to validate
    // 1: byte(0x19) - the initial 0x19 byte
    // 2: byte(0) - the version byte
    // 3: address(this) - the validator address
    // 4-6 : Application specific data

    bytes32 hash = keccak256(abi.encodePacked(byte(0x19), byte(0), address(this), msg.value, nonce, payload));

    // recovering the signer from the hash and the signature
    addressRecovered = ecrecover(hash, v, r, s);
   
    // logic of the wallet
    // if (addressRecovered == owner) executeOnTarget(target, payload);
}
```

## EIP-712.

### Description

EIP-712 replace the function `personal_sign`by`eth_signTypedData` (with the latest version being `eth_signTypedData_v4`)

The sign method calculates an Ethereum specific signature with: `sign(keccak256("\x19\x01" ‖ domainSeparator ‖ hashStruct(message)))`, as defined above.

**Note**: the address to sign with must be unlocked.

This EIP puts a warning about the frontrunning and replaces attacks, which are not taken in consideration by the standard

https://medium.com/mycrypto/the-magic-of-digital-signatures-on-ethereum-98fe184dc9c7

https://eips.ethereum.org/EIPS/eip-712[`eth_signTypedData`]

### Improvement 

compared to the standard EIP-191



Other suff

https://kobl.one/blog/create-full-ethereum-keypair-and-address/



https://docs.login.xyz/general-information/siwe-overview/review-of-related-eips

https://hacken.io/insights/ecdsa/
