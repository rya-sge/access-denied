---
layout: post
title: Solidity ABI Encoding – Overview
date: 2025-07-29
lang: en
locale: en-GB
categories: solidity ethereum blockchain
tags: abiencode encodePacked encodeWithSignature ABI
description: This article presents the differences between abi.encode, abi.encodePacked, and abi.encodeWithSignature in Solidity. Use cases, examples, and security tips.
image: 
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
| `abi.encode(...)`              | Standard ABI   | Larger      | <br />Hashing, Calldata, cross-contract calls | Data integrity is crucial, with variable-length arguments | Safe and precise              |
| `abi.encodePacked(...)`        | Tightly Packed | Smaller     | Hashing, gas efficiency                       | Gas optimization, fixed-length arguments                  | ⚠️ Risk of hash collisions     |
| `abi.encodeWithSignature(...)` | ABI + selector | Normal      | Low-level contract calls                      |                                                           | Safe if signature is accurate |

[TOC]



## `abi.encode(...)`

### What It Does:

`abi.encode(...)` encodes data according to the Ethereum ABI (Application Binary Interface). This format is used when calling functions, returning data, or interacting with contracts in a standard way.

Each argument gets padded to a fixed 32-byte size, reducing the risk of ambiguity between arguments.

### Characteristics:

- **Returns**: Dynamic `bytes` array
- **Includes**: Padding (each parameter is 32 bytes), data type info
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

`abi.encodePacked(...)` creates a **tightly packed** version of the encoded data. It strips out padding and data type info, resulting in a smaller byte array.

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
4. **`mapping`** (conceptually dynamic, but cannot be directly encoded)
5. **`structs` containing any of the above dynamic types**

*(Note: `bytes1`…`bytes32` and fixed-size arrays are **static types** and do not pose this specific risk.)*

#### Example:

Another example from [aderyn](https://github.com/Cyfrin/aderyn/blob/aderyn-v0.5.8/aderyn_core/src/detect/high/abi_encode_packed_hash_collision.rs): 

```
`abi.encodePacked(0x123,0x456)` => `0x123456` => 
`abi.encodePacked(0x1,0x23456)`, 

but `abi.encode(0x123,0x456)` => `0x0...1230...456`). \
```



abi.encodePacked("a", "bc") == abi.encodePacked("ab", "c")

This becomes dangerous if you're using such hashes as **unique identifiers**, **nonces**, or **keys in mappings**.

#### Remediation

 When passing the result to a hash function such as `keccak256()` with dynamic types as input, use `abi.encode()`  instead

`abi.encode()`  will pad items to 32 bytes, preventing hash collisions: 

#### Known exploit

```solidity
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
- **Does not check if the target contract actually has that function**. You’re sending raw bytes to a low-level `call`.

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

## Reference 

-  [Nethermind - Understanding Hash Collisions: abi.encodePacked in Solidity](https://www.nethermind.io/blog/understanding-hash-collisions-abi-encodepacked-in-solidity)
- [Cyfrin - ABI Encode (Solidity Code Example)](https://www.cyfrin.io/glossary/abi-encode-solidity-code-example)
- [0xScourgedev - Deep Dive into abi.encode: Types, Padding, and Disassembly](https://medium.com/@scourgedev/deep-dive-into-abi-encode-types-padding-and-disassembly-84472f1b4543)
- [RareSkills - Understanding ABI encoding for function calls](https://rareskills.io/post/abi-encoding)