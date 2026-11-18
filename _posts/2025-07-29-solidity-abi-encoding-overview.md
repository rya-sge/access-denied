---
layout: post
title: Solidity ABI Encoding – Overview
date: 2025-07-29
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: solidity ethereum blockchain
tags: abiencode encodePacked encodeWithSignature ABI
description: This article presents the differences between abi.encode, abi.encodePacked, and abi.encodeWithSignature in Solidity. Use cases, examples, and security tips.
image: /assets/article/blockchain/solidity/2025-07-29-solidity-abi-encoding-overview-mindmap.png
isMath: 
---

In Solidity, **ABI encoding** is crucial when dealing with low-level interactions such as function calls, hashing, or interacting with other contracts. 

Solidity provides three commonly used encoding functions:

- `abi.encode(...)`
- `abi.encodePacked(...)`
- `abi.encodeWithSignature(...)`

Each serves a specific purpose, and choosing the right one is important—not just for functionality, but also for **security**.



## Summary Table

| Function                       | Encodes?       | Output Size | Use For                                       | Use                                                       | Security Notes                |
| ------------------------------ | -------------- | ----------- | --------------------------------------------- | --------------------------------------------------------- | ----------------------------- |
| `abi.encode(...)`              | Standard ABI   | Larger      | <br />Hashing, Calldata, cross-contract calls | Data integrity matters, with variable-length arguments | Safe and precise              |
| `abi.encodePacked(...)`        | Tightly Packed | Smaller     | Hashing, gas efficiency                       | Gas optimization, fixed-length arguments                  | ⚠️ Risk of hash collisions     |
| `abi.encodeWithSignature(...)` | ABI + selector | Normal      | Low-level contract calls                      |                                                           | Safe if signature is accurate |

[TOC]

## What you need to know first

The comparison below assumes a few Solidity and EVM mechanisms that it uses without explaining.

- **Calldata and function selectors**: a call to a contract carries calldata whose first 4 bytes, the function selector, are the first 4 bytes of `keccak256` of the canonical signature such as `"transfer(address,uint256)"`. The ABI-encoded arguments follow, which is exactly what `abi.encodeWithSignature` and `abi.encodeWithSelector` build.
- **Static and dynamic types in the standard ABI**: a static value such as `uint256`, `address` or `bytes32` fills one 32-byte word. A dynamic value such as `bytes`, `string` or `T[]` is replaced in place by an offset, and its length and content are written further on; that length prefix is what `abi.encodePacked` drops.
- **Hashing an encoding**: contracts hash encoded data with `keccak256` to build identifiers, mapping keys and signed messages. A collision in this article does not break `keccak256` itself: two different argument lists produce the same bytes before hashing, so they get the same hash.
- **Signed messages and `ecrecover`**: a contract that checks an [ECDSA]({{site.url_complet}}/2024/10/23/ecdsa-overview/) signature recomputes the hash of the signed fields and recovers the signer from it. If two different sets of fields encode to the same bytes, one signature is accepted for both.
- **EIP-712 typed data**: [EIP-712](https://eips.ethereum.org/EIPS/eip-712) defines how to hash structured data for off-chain signing, combining a domain separator with a struct hash. The struct hash is built with `abi.encode` over the type hash and the fields, with dynamic fields hashed first, which avoids the packed-mode ambiguity.
- **Low-level `call`**: `address.call(data)` sends raw calldata and returns `(bool success, bytes memory returnData)` instead of reverting on failure. A call to an address with no code also returns `success = true`, so the caller has to check the result and, where it matters, that the target is a contract.



## `abi.encode(...)`

### What It Does:

`abi.encode(...)` encodes data according to the Ethereum ABI (Application Binary Interface). This format is used when calling functions, returning data, or interacting with contracts in a standard way.

Each argument gets padded to a fixed 32-byte size, reducing the risk of ambiguity between arguments.

### Characteristics:

- **Returns**: Dynamic `bytes` array
- **Includes**: Padding of each parameter to 32 bytes, plus offsets and lengths for dynamic types. The encoding carries no type information, so the decoder must already know the types
- **Use Case**: When interacting with other contracts or building calldata manually

### Example:

```solidity
bytes memory encodedData = abi.encode(uint256(1), address(0x123...));
```

### Safe To Use?

 Yes. It’s safe and standard. Since it uses padding and follows ABI spec strictly, there's **no ambiguity** in the data.

------

## `abi.encodePacked(...)`

Documentation: [docs.soliditylang.org - Non-standard Packed Mode](https://docs.soliditylang.org/en/develop/abi-spec.html#non-standard-packed-mode)

Through `abi.encodePacked()`, Solidity supports a non-standard packed mode where:

- types shorter than 32 bytes are concatenated directly, without padding or sign extension
- dynamic types are encoded in-place and without the length.
- array elements are padded, but still encoded in-place

Furthermore, structs as well as nested arrays are not supported.

### What It Does:

`abi.encodePacked(...)` creates a **tightly packed** version of the encoded data. It drops most of the padding and the offsets and lengths of dynamic types, resulting in a smaller byte array.

### Characteristics:

- **Returns**: `bytes` array (tightly packed)
- **Use Case**: Primarily for hashing (e.g. in `keccak256(...)`)
- **Gas Efficient**: Yes, due to reduced size

### Example:

```
bytes memory packedData = abi.encodePacked("hello", uint256(123));
```

### Security Risk: Hash Collisions

In general, the encoding is ambiguous as soon as there are two dynamically-sized elements, because of the missing length field.

If you use `keccak256(abi.encodePacked(a, b))` and both `a` and `b` are dynamic types, it is easy to craft collisions in the hash value by moving parts of `a` into `b` and vice-versa. More specifically, `abi.encodePacked("a", "bc") == abi.encodePacked("ab", "c")`. 

If you use `abi.encodePacked` for signatures, authentication or data integrity, make sure to always use the same types and check that **at most one** of them is dynamic. Unless there is a compelling reason, `abi.encode` should be preferred.

See also [Nethermind - Understanding Hash Collisions: abi.encodePacked in Solidity](https://www.nethermind.io/blog/understanding-hash-collisions-abi-encodepacked-in-solidity)

#### Dynamic types in Solidity

Here a list of dynamic types:

1. **`bytes`** (dynamically sized byte array)
2. **`string`** (UTF-8 encoded, dynamically sized)
3. **`T[]` dynamic arrays** (for any type `T`, including nested dynamic arrays like `uint[][]`)
4. **`mapping`** is not an ABI type at all: it can only live in storage and cannot be passed to `abi.encode` or `abi.encodePacked`, so it is listed here only to rule it out
5. **`structs` containing any of the above dynamic types**

*Note: `bytes1`…`bytes32` and fixed-size arrays are **static types** and do not pose this specific risk.*

#### Example:

Another example from [aderyn](https://github.com/Cyfrin/aderyn/blob/aderyn-v0.5.8/aderyn_core/src/detect/high/abi_encode_packed_hash_collision.rs): 

```
`abi.encodePacked(0x123,0x456)` => `0x123456` => 
`abi.encodePacked(0x1,0x23456)`, 

but `abi.encode(0x123,0x456)` => `0x0...1230...456`). \
```



`abi.encodePacked("a", "bc") == abi.encodePacked("ab", "c")`

This becomes dangerous if you're using such hashes as **unique identifiers**, **nonces**, or **keys in mappings**.

#### Remediation

 When passing the result to a hash function such as `keccak256()` with dynamic types as input, use `abi.encode()`  instead

`abi.encode()`  will pad items to 32 bytes, preventing hash collisions: 

#### Known exploit

The snippet below is Rust, not Solidity, and does not call `abi.encodePacked`: it concatenates the fields with `format!` before hashing them, which has the same ambiguity because nothing separates one field from the next.

```rust
fn permit (& mut self, public_key: String, signature: String,
owner: Key, spender: Key, value: U256, deadline: u64,) {
//..
//..
let data : String = format! (
" {}{}{}{}{}{} ",
permit_type_hash, owner, spender, value, nonce, deadline);

let hash : [ u8 ; 32] = keccak256 ( data . as_bytes ());
//..
//..
}
```

See also [Understanding Hash Collisions: abi.encodePacked in Solidity](https://www.nethermind.io/blog/understanding-hash-collisions-abi-encodepacked-in-solidity)

#### Static analyser - Detector

Several static analyzer tools use specific detectors to detect a bad use of `abiEncode` inside a contract

### Slither

[crytic/slither](https://github.com/crytic/slither)

See [Slither - #abi-encodePacked-collision](https://github.com/crytic/slither/wiki/Detector-Documentation#abi-encodePacked-collision) and [Slither - Encode_packed.py](https://github.com/crytic/slither/blob/master/slither/detectors/operations/encode_packed.py)

```python
def _detect_abi_encodePacked_collision(contract: Contract):
    """
    Args:
        contract (Contract)
    Returns:
        list((Function), (list (Node)))
    """
    ret = []
    # pylint: disable=too-many-nested-blocks
    for f in contract.functions_and_modifiers_declared:
        for ir in f.solidity_calls:
            if ir.function == SolidityFunction("abi.encodePacked()"):
                dynamic_type_count = 0
                for arg in ir.arguments:
                    if is_tainted(arg, contract) and _is_dynamic_type(arg):
                        dynamic_type_count += 1
                    elif dynamic_type_count > 1:
                        ret.append((f, ir.node))
                        dynamic_type_count = 0
                    else:
                        dynamic_type_count = 0
                if dynamic_type_count > 1:
                    ret.append((f, ir.node))
    return ret
```



### Aderyn 

[Cyfrin/aderyn](https://github.com/Cyfrin/aderyn)

Aderyn has a detector to check if `encodePacked`is used with a dynamic type such as: `string`, an array `[]` or `bytes`.

See [Cyfrin/aderyn - abi_encode_packed_hash_collision.rs](https://github.com/Cyfrin/aderyn/blob/aderyn-v0.5.8/aderyn_core/src/detect/high/abi_encode_packed_hash_collision.rs)

```rust
 if member_access.member_name == "encodePacked" {
                let mut count = 0;
                let argument_types = member_access.argument_types.as_ref().unwrap();
                for argument_type in argument_types {
                    if argument_type.type_string.as_ref().unwrap().contains("bytes ")
                        || argument_type.type_string.as_ref().unwrap().contains("[]")
                        || argument_type.type_string.as_ref().unwrap().contains("string")
                    {
                        count += 1;
                    }
                }
                if count > 1 {
                    capture!(self, context, member_access);
                }
            }
```



------

## `abi.encodeWithSignature(...)`

### What It Does:

This is a shortcut to encode a function call's signature and arguments.

### Characteristics:

- **Input**: Function signature as a string + parameters
- **Returns**: Calldata (bytes) ready to be sent to another contract

### Example:

```solidity
bytes memory data = abi.encodeWithSignature("transfer(address,uint256)", recipient, amount);
(bool success, ) = tokenAddress.call(data);
```

It’s equivalent to:

```solidity
abi.encodeWithSelector(bytes4(keccak256("transfer(address,uint256)")), recipient, amount);
```

### Safe To Use?

 Yes, **but**:

- You must make sure the function signature string is **correctly spelled and formatted**.
- **Does not check that the target contract has that function**. You’re sending raw bytes to a low-level `call`.

------

## Final Security Recommendations

1. **Avoid hash collisions**: When using `abi.encodePacked` with `keccak256`, don't mix variable-length types (e.g., `string`, `bytes`) in a way that could lead to ambiguity.
2. **Don’t use `abi.encodePacked` to simulate structured data**. If in doubt, use `abi.encode`.
3. **For off-chain signing**: Prefer `abi.encode` with `EIP-712` for typed structured data.
4. **Always validate success of `.call(...)`** when using `abi.encodeWithSignature`.

------

## Conclusion

Solidity's encoding functions are powerful tools for interacting with smart contracts, hashing data, and building secure systems. Understanding their differences—and the subtle risks involved—is essential for safe and effective smart contract development.

If you’re building anything with signature verification, unique identifiers, or low-level contract calls, **choose your encoding method carefully**. The wrong choice could lead to **critical security vulnerabilities**.

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **ABI (Application Binary Interface)** | The standard that defines how function calls, arguments and return values are encoded as bytes when contracts are called or return data. |
| **Calldata** | The byte payload sent with a call to a contract: the function selector followed by the ABI-encoded arguments. |
| **Function signature** | The function name and its argument types without spaces, such as `transfer(address,uint256)`, from which the selector is derived. |
| **Function selector** | The first 4 bytes of `keccak256` of the function signature, which tells the called contract which function to run. |
| **Padding** | Filling each encoded value up to 32 bytes, which `abi.encode` does and `abi.encodePacked` skips for types shorter than 32 bytes. |
| **Static type** | A type with a fixed encoded size, such as `uint256`, `address` or `bytes1` to `bytes32`, which does not create the packed-mode collision risk. |
| **Dynamic type** | A type whose size is known only at run time, such as `bytes`, `string` or `T[]`, whose length the standard ABI writes and packed mode omits. |
| **`abi.encode`** | The Solidity function that encodes its arguments in the standard ABI format, with 32-byte padding, and so gives an unambiguous result. |
| **`abi.encodePacked`** | The Solidity function for the non-standard packed mode, which concatenates values without padding or length fields and does not support structs or nested arrays. |
| **`abi.encodeWithSignature`** | The Solidity function that prepends the selector of a given signature string to the ABI-encoded arguments, producing calldata for a low-level call. |
| **`abi.encodeWithSelector`** | The equivalent of `abi.encodeWithSignature` that takes the 4-byte selector directly instead of the signature string. |
| **Hash collision (packed encoding)** | Two different argument lists that `abi.encodePacked` turns into the same bytes, so `keccak256` returns the same hash, as with `("a", "bc")` and `("ab", "c")`. |
| **EIP-712** | The Ethereum standard for hashing and signing typed structured data, recommended over packed encoding for off-chain signatures. |
| **Low-level call** | A call made with `address.call(data)`, which sends raw calldata, does not check that the target has the function and returns a success flag to validate. |
| **Slither** | A static analyser for Solidity whose `abi-encodePacked-collision` detector flags `abi.encodePacked` calls with more than one dynamic argument. |
| **Aderyn** | A static analyser for Solidity from Cyfrin with a detector for `encodePacked` calls taking more than one `string`, `bytes` or array argument. |

## Reference 

-  [Nethermind - Understanding Hash Collisions: abi.encodePacked in Solidity](https://www.nethermind.io/blog/understanding-hash-collisions-abi-encodepacked-in-solidity)
- [Cyfrin - ABI Encode (Solidity Code Example)](https://www.cyfrin.io/glossary/abi-encode-solidity-code-example)
- [0xScourgedev - Deep Dive into abi.encode: Types, Padding, and Disassembly](https://medium.com/@scourgedev/deep-dive-into-abi-encode-types-padding-and-disassembly-84472f1b4543)
- [RareSkills - Understanding ABI encoding for function calls](https://rareskills.io/post/abi-encoding)

## Mindmap

The mindmap below summarizes the article.

![Solidity ABI encoding mindmap]({{site.url_complet}}/assets/article/blockchain/solidity/2025-07-29-solidity-abi-encoding-overview-mindmap.png)

## Related articles

- [SSZ vs RLP: How Ethereum Serialises Data on Each Layer]({{site.url_complet}}/2026/11/04/ssz-vs-rlp-ethereum-serialization/)
