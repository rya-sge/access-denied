# The Main Vulnerabilities When Using ECDSA Signatures in Smart Contracts

## Introduction

Elliptic Curve Digital Signature Algorithm (ECDSA) is widely used in blockchain applications, particularly in Ethereum smart contracts, for verifying signatures and authenticating users. However, improper implementation of ECDSA in smart contracts can introduce security vulnerabilities, leading to potential exploits such as signature malleability, replay attacks, and unauthorized access.

In this article, we will explore the key vulnerabilities associated with ECDSA in smart contracts, analyze poor implementations, and showcase best practices for securing signature verification.

[TOC]

## OpenZeppelin

OpenZeppelin provides an ECDSA library which functions can be used to verify that a message was signed by the holder of the private keys of a given address. The documentation of the version 5 is vailable [here](https://docs.openzeppelin.com/contracts/5.x/api/utils#ECDSA-recover-bytes32-bytes-)

There are two main functions which can be used to verify the signature`recover` and `tryRecover`

1. `ECDSA.recover` - This doesn't return an error if something wrong with the signature. It will only return the `address` of the signer. In this case you can see returning `address(0)` when an error occurs.
2. `ECDSA.tryRecover` - This returns the `address`, `error`, and *details related to the error*. There will be no such cases like returning `address(0)`

See also [ethereum.stackexchange - ECDSA.recover versus ECDSA.tryRecover](https://ethereum.stackexchange.com/questions/156467/ecdsa-recover-versus-ecdsa-tryrecover)

### Protection against signature malleability

The `ecrecover` EVM precompile allows for malleable (non-unique) signatures. OpenZeppelin function rejects them by:

- requiring the `s` value to be in the lower half order, 
- requiring the `v` value to be either 27 or 28.

### Important

- `hash` *must* be the result of a hash operation for the verification to be secure: it is possible to craft signatures that recover to arbitrary addresses for non-hashed data. A safe way to ensure this is by receiving a hash of the original message (which may otherwise be too long), and then calling [`MessageHashUtils.toEthSignedMessageHash`](https://docs.openzeppelin.com/contracts/5.x/api/utils#MessageHashUtils-toEthSignedMessageHash-bytes-) on it.
- OpenZeppelin v4 was vulnerable to signature malleability.



## Use

### Checklist

|                           |                                               | Solition                                            |
| ------------------------- | --------------------------------------------- | --------------------------------------------------- |
| Missing pararamer         |                                               | Add the missing parameters                          |
| Replay attack (nonce) ?   | Add a nonce                                   |                                                     |
| Cross-replay attack       | Missing chain id                              | Use EIP712                                          |
| Signature malleability    | eccrecover or OpenzZeppeli vulnerable version | Use OpenZeppelin >=v5.0.0 with recovery/tryRecovery |
|                           |                                               |                                                     |
| Owner is not the signer ? |                                               |                                                     |



### Missing Validation[¶](https://scsfg.io/hackers/signature-attacks/#missing-validation)

One of the most common vulnerabilities is missing validation when `ecrecover` encounters errors and returns an invalid address.

```solidity
function recover(uint8 v, bytes32 r, bytes32 s, bytes32 hash) external 
{    
	address signer = ecrecover(hash, v, r, s);    
//Do more stuff with the hash 
} `
```

A crucial check for `address(0)` is absent in this instance. This omission allows an attacker to submit invalid signatures with arbitrary payloads yet pass as valid. A simple yet effective solution to this issue would be to include a check like the following:

```solidity
`require(signer != address(0), "invalid signature"); `
```

Even better, OpenZeppelin's `ECDSA` library should be used because it automatically reverts when invalid signatures are encountered.

### Replay Attacks[¶](https://scsfg.io/hackers/signature-attacks/#replay-attacks)

Replay attacks occur when a signature and the system consuming it have no deduplication mechanism. A cause for replay attack vulnerabilities is when signatures are not properly invalidated or a nonce is absent from the system. 

The following examples underline the different attack angles on a smart contract signature system and its iterations.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract OwnerAction {
    using ECDSA for bytes32;

    address public owner;

    constructor() payable {
        owner = msg.sender;
    }

    function action(uint256 _param1, bytes32 _param2, bytes memory _sig) external {
        bytes32 hash = keccak256(abi.encodePacked(_param1, _param2));
        bytes32 signedHash = hash.toEthSignedMessageHash();
        address signer = signedHash.recover(_sig);

        require(signer == owner, "Invalid signature");

        // use `param1` and `param2` to perform authorized action
    }
}
```

In this scenario, an attacker possessing the owner's signature can perform the same action multiple times. For instance, if the owner signed a transaction authorizing a transfer of funds, the attacker could replay the signature and drain the contract by transferring funds repeatedly. 



Other example: https://medium.com/cryptronics/signature-replay-vulnerabilities-in-smart-contracts-3b6f7596df57

#### Mitigation

To mitigate this issue, a mapping can invalidate each submitted signature after its first execution. 

However, a nonce must be encoded into the signed payload to allow the owner to sign the same action multiple times. The sole purpose of the nonce value is to change the final signature when the payload data remains the same.

The following code adds the signature invalidation mechanism as well as the nonce-related business logic.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract OwnerAction {
    using ECDSA for bytes32;

    address public owner;
    mapping(bytes32 => bool) public seenSignatures;

    constructor() payable {
        owner = msg.sender;
    }

    function action(uint256 _param1, bytes32 _param2, uint256 _nonce, bytes memory _sig) external {
        bytes32 hash = keccak256(abi.encodePacked(_param1, _param2, _nonce));
        require(!seenSignatures[hash], "Signature has been used");

        bytes32 signedHash = hash.toEthSignedMessageHash();
        address signer = signedHash.recover(_sig);
        require(signer == owner, "Invalid signature");

        seenSignatures[hash] = true;

        // use `param1` and `param2` to perform authorized action
    }
}
```

Even this enhanced contract is not entirely secure. If the system is deployed on multiple chains or if the signer address is used in other contexts on different chains, signature replay attacks are still a potential threat.

#### Mitigation with nonce

- keep track of a [nonce](https://ethereum.stackexchange.com/questions/136224/how-to-use-nonce-to-prevent-signature-replication),
- make the current nonce available to signers,
- validate the signature using the current nonce,
- once a nonce has been used, save this to storage such that the same nonce can't be used again.

https://dacian.me/signature-replay-attacks

https://dacian.me/signature-replay-attacks

#### Cross-chain Replay Attacks[¶](https://scsfg.io/hackers/signature-attacks/#cross-chain-replay-attacks)

Cross-chain replay attacks arise when signatures can be reused across different blockchain systems. Once a signature has been used and invalidated on one chain, an attacker can still copy it, use it on another, and trigger an unwanted state change. This poses a significant threat to smart contract systems deployed across chains with identical code.

Example

Many smart contracts operate on multiple chains from the same contract address and users similarly operate the same address across multiple chains. Biconomy's code4rena contest had the following [code](https://github.com/code-423n4/2023-01-biconomy/blob/main/scw-contracts/contracts/smart-contract-wallet/paymasters/verifying/singleton/VerifyingSingletonPaymaster.sol#L77-L90):

```solidity
function getHash(UserOperation calldata userOp)
public pure returns (bytes32) {
    //can't use userOp.hash(), since it contains also the paymasterAndData itself.
    return keccak256(abi.encode(
            userOp.getSender(),
            userOp.nonce,
            keccak256(userOp.initCode),
            keccak256(userOp.callData),
            userOp.callGasLimit,
            userOp.verificationGasLimit,
            userOp.preVerificationGas,
            userOp.maxFeePerGas,
            userOp.maxPriorityFeePerGas
        ));
}
```

Since a UserOperation is not signed nor verified using the chain_id, a valid signature that was used on one chain could be copied by an attacker and propagated onto another chain, where it would also be valid for the same user & contract address! 

To prevent [cross-chain signature replay attacks](https://code4rena.com/reports/2023-01-biconomy#m-03-cross-chain-signature-replay-attack), smart contracts must validate the signature using the chain_id, and users must [include the chain_id in the message to be signed](https://ethereum.stackexchange.com/questions/116970/how-to-prevent-cross-chain-signed-message-replay). More examples: [[1](https://github.com/sherlock-audit/2022-09-harpie-judging/blob/main/004-M/1-report.md), [2](https://solodit.xyz/issues/unlimitedpricefeed-is-vulnerable-to-crosschain-signature-replay-attacks-halborn-unlimited-network-unlimited-leverage-pdf)]

#### Mitigation

To mitigate this risk, the chain ID should be encoded in the signature payload and validated against the current chain ID where the action is executed.

```solidity
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract OwnerAction {
    using ECDSA for bytes32;

    address public owner;
    mapping(bytes32 => bool) public seenSignatures;

    constructor() payable {
        owner = msg.sender;
    }

    function action(uint256 _param1, bytes32 _param2, uint256 _nonce, uint256 _chainId, bytes memory _sig) external {
        require(_chainId == block.chainid, "Invalid chain ID");

        bytes32 hash = keccak256(abi.encodePacked(_param1, _param2, _nonce, _chainId));
        require(!seenSignatures[hash], "Signature has been used");

        bytes32 signedHash = hash.toEthSignedMessageHash();
        address signer = signedHash.recover(_sig);
        require(signer == owner, "Invalid signature");

        seenSignatures[hash] = true;

        // use `param1` and `param2` to perform authorized action
    }
}
```



It's worth noting that when signatures are used with EIP712 typed data payloads, the domain separator value already includes the chain ID.



### Frontrunning[¶](https://scsfg.io/hackers/signature-attacks/#frontrunning)

Another common issue is frontrunning. Attackers can monitor the mempool for transactions using ECDSA signatures in certain systems, such as those where a reward is paid out for third parties executing a payload. Depending on the information in the signature payload, an attacker can frontrun the original transaction, manipulate specific parameters, and exploit the system.

#### Missing parameter from signature

Regarding the example above, a signature vulnerable to frontrunning attacks would emerge if the valid signature hash were to be calculated as follows:

```solidity
bytes32 hash = keccak256(abi.encodePacked(_param2, _nonce, _chainId));
```

With the `param1` parameter missing, a frontrunning attacker can arbitrarily set the value of `param1` and potentially exploit the system. It is paramount that all parameters participating in the execution of business logic triggered by the signature are included therein.



## Signature Malleability[¶](https://scsfg.io/hackers/signature-attacks/#signature-malleability)

Signature malleability is a characteristic of digital signatures. In Ethereum, an ECDSA signature is represented by two 32-byte sized, `r` and `s` values, and a one-byte recovery value, `v`. 

The signature is in form of a 65-byte long string, however, these bytes are always later split to three components as briefly touched on above:

- last one byte — `v`

`v`: The recovery identifier, which is used to recover the correct public key (address) from the signatu

- first 32 bytes — `r`

`r`: A value derived from the elliptic curve point (x, y) generated during the signing process. The `r` value is the x-coordinate of that point.

- second 32 bytes — `s`

 A value calculated during the signing process using the private key, message hash, and `r`. The `s` value is meant to prove that the signer has knowledge of the private key without revealing it.

This is because the elliptic curve is symmetric, and for each point (x, y) on the curve, there's a corresponding point (x, -y) that maintains the same relationship.The symmetric structure of elliptic curves implies that no signature is unique. A consequence of these "malleable" signatures is that they can be altered without being invalidated.

For every set of parameters `{r, s, v}` used to create a signature, another distinct set `{r', s', v'}` results in an equivalent signature. Therefore, when a smart contract system uses `ecrecover` directly instead of a well-known library like OpenZeppelin's `ECDSA`, detecting and discarding malleable signatures is essential.

OpenZeppelin's ECDSA library contains the following code to prevent forged signatures:

```solidity
if (uint256(s) > 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0) {
    return (address(0), RecoverError.InvalidSignatureS);
}
```

This measure stops signature malleability attacks since most signatures from current libraries yield a unique signature with an s-value in the lower half order. It is vital to the signature validation library that this check is in place.

Example:

The group order used for bitcoin and Ethereum is the following constant 

1) From a valid signature, compute, `s, `r` `v
2) Compute s2 = bytes32(n-s1)
3) 

`0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141`?

    bytes32 constant public groupOrder = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141;



```s
function testMalleable() public {
        // put r,s,v,hash values from `node sign.js` logs
        // first 32 bytes of the signature
        bytes32 r = 0xc1d9e2b5dd63860d27c38a8b276e5a5ab5e19a97452b0cb24094613bcbd517d8;
        // next 32 bytes
        bytes32 s = 0x6dc0d1a7743c3328bfcfe05a2f8691e114f9143776a461ddad6e8b858bb19c1d;
        uint8 v = 28;

        bytes32 hash = 0x3ea2f1d0abf3fc66cf29eebb70cbd4e7fe762ef8a09bcc06c8edf641230afec0;

        //address (signer)
        signer = ecrecover(hash, v, r, s));

        // we change the s value changing the signature
        bytes32 s1 = bytes32(uint256(groupOrder)-uint256(s));
        
        // original signature should use the lower s value
        assertTrue(uint(s1) > uint(s));

        // we changed the signature and show that it signed without knowing the private key
        console.log("Change s, we get a different signer");
        console.log(ecrecover(hash, v, r, s1));

        console.log("Change s and v, we get the same signer");
        uint8 v1 = v==27 ? 28 : 27;
        console.log("original signer with changed signature", ecrecover(hash, v1, r, s1));

    }
```



#### Example

### Ethernaut 9

From: https://stermi.medium.com/ethernautdao-ctf-9-solution-etherwallet-ad460990acfa

```solidity
 bytes32 groupOrder = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141;
bytes memory signature = hex"53e2bbed453425461021f7fa980d928ed1cb0047ad0b0b99551706e426313f293ba5b06947c91fc3738a7e63159b43148ecc8f8070b37869b95e96261fc9657d1c";

// split signature to get back the tuple (uint8 v, bytes32 r, bytes32 s)
(uint8 v, bytes32 r, bytes32 s) = deconstructSignature(signature);

// Now we can calculate what should be the "inverted signature"
  bytes32 invertedS = bytes32(uint256(groupOrder) - uint256(s));
    
  uint8 invertedV = v == 27 ? 28 : 27;

// After calculating which is the inverse `s` and `v` we just need to re-create the signature
  bytes memory invertedSignature = abi.encodePacked(r, invertedS, invertedV);

// Call the function with the signature crafted
  contract.targetFunction(invertedSignature)

// utility function to deconstruct a signature returning (v, r, s)
function deconstructSignature(bytes memory signature)
    public
    pure
    returns (
        uint8,
        bytes32,
        bytes32
    )
{
    bytes32 r;
    bytes32 s;
    uint8 v;
    // ecrecover takes the signature parameters, and the only way to get them
    // currently is to use assembly.
    /// @solidity memory-safe-assembly
    assembly {
        r := mload(add(signature, 0x20))
        s := mload(add(signature, 0x40))
        v := byte(0, mload(add(signature, 0x60)))
    }
    return (v, r, s);

```



https://github.com/0xbok/ecdsa-vuln-poc/tree/master/ch1_malleable

https://github.com/obheda12/Solidity-Security-Compendium/blob/main/days/day12.md

https://swcregistry.io/docs/SWC-117/

https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-4h98-2769-gh6h

### Ethernaut32

https://medium.com/@ynyesto/ethernaut-32-impersonator-825c0ea9d76d

### EIP-2098 Compact Signatures[¶](https://scsfg.io/hackers/signature-attacks/#eip-2098-compact-signatures)

The `ECDSA.recover` and `ECDSA.tryRecover` methods are susceptible to a specific form of signature malleability, owing to their ability to process both EIP-2098 compact signatures and the conventional 65-byte signature format. However, this issue is relevant only to the functions which accept a single byte argument and does not impact the ones that take `{r, v, s}` or `{r, vs}` as separate arguments.

The contracts that could be affected are those that implement strategies of signature reuse or replay protection by marking the signature itself as 'used' instead of the signed message. 

In this case, a user might take an already submitted signature, re-submit it in a different format, such as a compact signature, and circumvent the established protection mechanism.

This issue only affects the OpenZeppelin contracts below and not including version `4.7.3`. The related security advisory can be found [here](https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-4h98-2769-gh6h).

## Example

https://vulners.com/code423n4/CODE423N4:2023-01-BICONOMY-FINDINGS-ISSUES-486

```solidity
// If v is 0 then it is a contract signature
// When handling contract signatures the address of the contract is encoded into r
_signer = address(uint160(uint256(r)));

// Check that signature data pointer (s) is not pointing inside the static part of the signatures bytes
    // This check is not completely accurate, since it is possible that more signatures than the threshold are send.
    // Here we only check that the pointer is not pointing inside the part that is being processed
    require(uint256(s) &gt;= uint256(1) * 65, "BSA021");

    // Check that signature data pointer (s) is in bounds (points to the length of data -&gt; 32 bytes)
    require(uint256(s) + 32 &lt;= signatures.length, "BSA022");

    // Check if the contract signature is in bounds: start of data is s + 32 and end is start + signature length
    uint256 contractSignatureLen;
    // solhint-disable-next-line no-inline-assembly
    assembly {
        contractSignatureLen := mload(add(add(signatures, s), 0x20))
    }
    require(uint256(s) + 32 + contractSignatureLen &lt;= signatures.length, "BSA023");

    // Check signature
    bytes memory contractSignature;
    // solhint-disable-next-line no-inline-assembly
    assembly {
        // The signature data for contract signatures is appended to the concatenated signatures and the offset is stored in s
        contractSignature := add(add(signatures, s), 0x20)
    }
    require(ISignatureValidator(_signer).isValidSignature(data, contractSignature) == EIP1271_MAGIC_VALUE, "BSA024");
```



## 1. Signature Malleability

### **What is Signature Malleability?**

ECDSA signatures consist of three values: `(r, s, v)`. A key issue with ECDSA is that for every valid signature `(r, s)`, there exists another valid signature `(r, -s mod n)`. This means an attacker can alter the signature while keeping it valid, potentially bypassing security checks.

### **Vulnerable Example: Unsafe Signature Verification**

```
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract VulnerableContract {
    address public signer;

    constructor(address _signer) {
        signer = _signer;
    }

    function verifySignature(bytes32 hash, bytes memory signature) public view returns (bool) {
        address recovered = ECDSA.recover(hash, signature);
        return recovered == signer;
    }
}
```

#### **Why is this Vulnerable?**

- The function does not check if `s` is in the lower half of the curve (`s < secp256k1n / 2`).
- An attacker could modify `s` and generate an alternate but still valid signature to bypass signature-based authentication.

### **Secure Example: Preventing Signature Malleability**

A safer approach is to enforce EIP-2 compliance, which requires `s` to be in the lower half of the curve.

```
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract SecureContract {
    address public signer;

    constructor(address _signer) {
        signer = _signer;
    }

    function verifySignature(bytes32 hash, bytes memory signature) public view returns (bool) {
        (address recovered, ECDSA.RecoverError error) = ECDSA.tryRecover(hash, signature);
        require(error == ECDSA.RecoverError.NoError, "Invalid signature");
        return recovered == signer;
    }
}
```

This implementation uses OpenZeppelin’s `tryRecover`, which ensures that only valid, non-malleable signatures are accepted.

## 2. Signature Replay Attacks

### **What is a Replay Attack?**

A replay attack occurs when an attacker reuses a previously valid signature to authorize multiple unintended transactions. This is a common issue when signatures are not bound to a unique identifier such as a nonce.

### **Vulnerable Example: Missing Nonce in Signed Data**

```
contract ReplayVulnerable {
    address public signer;

    function executeTransaction(bytes32 hash, bytes memory signature) public {
        require(ECDSA.recover(hash, signature) == signer, "Invalid signature");
        // Execute transaction
    }
}
```

#### **Why is this Vulnerable?**

- The same `signature` can be reused multiple times since there is no mechanism to track whether it has already been used.
- An attacker could replay the same signed transaction to execute it multiple times.

### **Secure Example: Using a Nonce to Prevent Replays**

```
contract ReplayProtected {
    using ECDSA for bytes32;

    address public signer;
    mapping(bytes32 => bool) public usedSignatures;

    function executeTransaction(bytes32 hash, bytes memory signature) public {
        require(!usedSignatures[hash], "Signature already used");
        require(ECDSA.recover(hash, signature) == signer, "Invalid signature");
        usedSignatures[hash] = true; // Mark as used
    }
}
```

#### **How This Prevents Replay Attacks**

- A mapping stores used signatures, ensuring that they cannot be replayed.
- Before executing the transaction, the contract checks if the signature has been used.

## 3. Unverified Message Hashes

### **Vulnerable Example: Accepting User-Provided Hashes**

```
contract UnverifiedHash {
    function verifySignature(bytes32 hash, bytes memory signature) public view returns (bool) {
        address recovered = ECDSA.recover(hash, signature);
        return recovered != address(0);
    }
}
```

#### **Why is this Vulnerable?**

- The contract does not verify how the `hash` was constructed, allowing attackers to use arbitrary hashes.
- Attackers can sign a different message and still pass the check.

### **Secure Example: Ensuring the Hash is Constructed Properly**

```
contract VerifiedHash {
    function verifySignature(address sender, uint256 amount, bytes memory signature) public view returns (bool) {
        bytes32 messageHash = keccak256(abi.encodePacked(sender, amount));
        bytes32 ethSignedMessageHash = ECDSA.toEthSignedMessageHash(messageHash);
        address recovered = ECDSA.recover(ethSignedMessageHash, signature);
        return recovered != address(0);
    }
}
```

#### **How This Fixes the Issue**

- It ensures that the hash includes key transaction data (`sender` and `amount`).
- It wraps the hash using `toEthSignedMessageHash`, preventing attackers from using arbitrary data.

## Conclusion

When implementing ECDSA signature verification in smart contracts, developers must be cautious to avoid common vulnerabilities. The key takeaways include:

1. **Mitigate Signature Malleability** by ensuring `s` is in the lower half of the curve (EIP-2 compliant).
2. **Prevent Replay Attacks** by including a nonce or marking used signatures.
3. **Verify Message Hashes Properly** to prevent attackers from signing arbitrary data.

By following these best practices and using OpenZeppelin’s well-tested cryptographic libraries, developers can enhance the security of their smart contracts and prevent signature-based exploits.

## Main reference

[dacian - Signature Replay Attacks](https://dacian.me/signature-replay-attacks)

### Others references

[hacken - Key Discovery in ECDSA: Understanding Implementation and Security Risk](https://hacken.io/insights/ecdsa/)

## Other

https://www.alchemy.com/blog/erc-1271-signature-replay-vulnerability

https://stermi.xyz/blog/ethernautdao-ctf-switch-solution

 https://eips.ethereum.org/EIPS/eip-2098[ERC-2098 short signatures]