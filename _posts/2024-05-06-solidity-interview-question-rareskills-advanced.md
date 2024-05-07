---
layout: post
title:  RareSkills Solidity Interview Answers - Advanced
date:   2024-05-06
lang: en
locale: en-GB
categories: blockchain ethereum solidity
tags: ethereum solidity interview security gas
description: Solidity Interview Questions - Advanced, answers from the article - Solidity Interview Questions- by RareSkills.
image: /assets/article/blockchain/ethereum/solidity/solidity_logo.png
isMath: false
---

This article presents the list of Advanced questions with their answers related to the article [Solidity Interview Questions](https://www.rareskills.io/post/solidity-interview-questions) by RareSkills.

For the level Medium and Hard, you can see my [my first](https://rya-sge.github.io/access-denied/2024/02/14/solidity-interview-question-rareskills/) and [second article](https://rya-sge.github.io/access-denied/2024/03/04/solidity-interview-question-rareskills-hard/).

According to the article, all questions can be answered in three sentences or less.

The answers here are more complete than necessary in order to explain in details each topic.

## Gas

###  EVM price memory

> How does the EVM price memory usage?

The formula is indicated in the Ethereum [yellow paper](https://ethereum.github.io/yellowpaper/paper.pdf), page 28. The function is polymonial. Thus, the cost is linear up to 724B of memory  used. After this limit, the yellow paper indicates that the cost increases significantly more and my guess is that it then becomes exponential.

![evm-yellow-paper-gas-cost-memory]({{site.url_complet}}/assets/article/blockchain/ethereum/evm/evm-yellow-paper-gas-cost-memory.png)

As also indicated in the page 29:

*Cmem is the memory cost function (the expansion function being the   difference between the cost before  and after). It is a polynomial, with the higher-order coefficient divided and  floored, and thus linear up to 724B of memory  used, after which it costs substantially more.*

See this discussion on ethereum.stackexchange: [How does the cost of EVM memory scale?](https://ethereum.stackexchange.com/questions/29896/how-does-the-cost-of-evm-memory-scale)

### Vanity address

> Under what circumstances do addresses with leading zeros save gas and why?

If the address is used as an argument of a function, an address with more zero will cost less gas because there are more zero in the calldata. It true for smart contract, as well EOA.

Reference: [RareSkills - Use vanity addresses](https://www.rareskills.io/post/gas-optimization#viewer-f970n)



### --via-ir

> How does the --via-ir functionality in the Solidity compiler work?

This option `--via-ir` allows to compile with the IR representation.

Solidity can generate EVM bytecode in two different ways: 

- Directly from Solidity to EVM opcodes (“old codegen”)
- Or through an intermediate representation (“IR”) in Yul (“new codegen” or “IR-based codegen”).

The IR-based code generator was introduced to: 

- To be more transparent and auditable
- To enable more powerful optimization

Reference: [docs.soliditylang.org/en/latest/ir-breaking-changes.html](https://docs.soliditylang.org/en/latest/ir-breaking-changes.html)



### Copy regions of memory

> What is the most efficient way to copy regions of memory?

Initially, the most efficient way was to combine the opcodes MSTORE and MLOAD in *inline assembly*.

But the Dencun upgrade with the [EIP-5656](https://eips.ethereum.org/EIPS/eip-5656) has introduced a new opcode MCOPY, a combination of those two opcodes.

Reference: [Ethereum Evolved: Dencun Upgrade Part 1, EIP-5656 & EIP-6780](https://consensys.io/blog/ethereum-dencun-upgrade-explained-part-1)



### Gas forward

> How much gas can be forwarded in a call to another smart contract?

Only 63/64th of the gas can be forwarded in a message call, which causes a depth limit of a little less than 1000 in practice. This limit has been introduced by [EIP-150](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-150.md) to avoid the *Call Depth Attack* where an attacker manages to cause a *stack too deep error* by calling endless series of contracts calling other contracts, since, prior to the EIP-150, the gas cost of each call was low.

Reference: [docs.soliditylang.org#message-calls](https://docs.soliditylang.org/en/v0.8.25/introduction-to-smart-contracts.html#message-calls), [RareSkills - EIP-150 and the 63/64 Rule for Gas](https://www.rareskills.io/post/eip-150-and-the-63-64-rule-for-gas)

### Negative numbers gas cost

> Why do negative numbers in calldata cost more gas?

 It is due to the two's complement notation  for signed integers.

Numbers with with a lot of zeros cost less gas, but for small negative numbers, the representation will be largely non-zero since the bits are inversed.

For example, -1 is represented as 0xFFFF....FFFF

Reference: [www.rareskills.io/post/gas-optimization#viewer-7umto](https://www.rareskills.io/post/gas-optimization#viewer-7umto)

### String storage slot

> How many storage slots does a string take up?

It depends on the size of the string.

For short values (shorter than 32 bytes) the array elements are stored together with the length in the same slot.

Otherwise, there is a first slot to store the length of the array and a data area that is computed using a `keccak256` hash of that slot’s position.  

Reference: [docs.soliditylang.org/en/latest/internals/layout_in_storage.html#bytes-and-string](https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html#bytes-and-string), [ethereum.stackexchange - Storage and memory layout of strings](https://ethereum.stackexchange.com/questions/107282/storage-and-memory-layout-of-strings)

## Security

### MEV uncle-block attack

> What is the uncle-block attack from an MEV perspective?

In Ethereum occasionally two blocks are mined at roughly the same time, and only one block can be added to the chain. The other gets "uncled" or orphaned

An attacker can see the the block "rejected" and he can decide to manipulate some part of the blocks and.

For example, if a sandwich attack has bee part of

Some blocks, despite being valid, may not be included in the primary  blockchain. These blocks are referred to as Uncle Blocks or Stale  Blocks. Miners who contribute to the network but fall short of having  their blocks added to the main chain are compensated with a reduced  reward for their efforts.

Reference: [www.mev.wiki/attack-examples/uncle-bandit-attack](https://www.mev.wiki/attack-examples/uncle-bandit-attack)

### Signature malleability attack

> How do you conduct a signature malleability attack?

With ECDSA, you can have two different valid signatures generated with the same secret. This complementary signature can be computed without knowing  the private key used to produce the first signature.

If the smart contract implements correctly the signature verification, e.g with OpenZeppelin, this second signature should be rejected.

But if it is not the case, you can perform cool math on a valid signature to compute a second valid signature. To retrieve this first signature, an attacker can get it from transactions or smart contract storage. 

**Current state**

To prevent signature malleability, Ethereum has introduced the [EIP-2](https://eips.ethereum.org/EIPS/eip-2) to consider only lower levels of *s* as valid in a signature. Thus, there is only one valid point at each x coordinate because half points of the curve are no longer considered.

But the precompiled contract `ecrecover` does not include this modification and it still vulnerable to signature malleability. It is the reason why it is safer to use the library [OpenZeppelin ECDSA](https://docs.openzeppelin.com/contracts/5.x/api/utils#ECDSA) which handle appropriately this case. 

**Math part**

The equation for secp256k1 is **y² = x³ + 7** over F(p), which means that a = 0 and b = 7

Elliptic Curve is symmetric on the X-axis, meaning two points can exist with the same X value. We can adjust the signature `s` to produce a valid signature for the same *r* on the other side of the X-axis (`-s mod n`).

This is done by :

- Flipping the s value from `s` to `n - s`,  

- flipping the v value ( 27 -> 28, 28 -> 27)

Reference: [rareskills.io - Smart Contract Securit](https://www.rareskills.io/post/smart-contract-security), [kadenzipfel - Signature Malleability](https://github.com/kadenzipfel/smart-contract-vulnerabilities/blob/master/vulnerabilities/signature-malleability.md), [coders-errands - ECRecover and Signature Verification in Ethereum](https://coders-errand.com/ecrecover-signature-verification-ethereu), [coders - ECDSA Malleability](https://coders-errand.com/malleability-ecdsa-signatures/)



### ECDSA verification

> Why is it important to ECDSA sign a hash rather than an arbitrary bytes32?

Firstly, hash the message is part of the specification and it is never a good idea to not follow a specification.

By hashing the message, we ensure that each message has the same size at the end. If the message was not hashed, there is a risk that the message will be padded or truncated, reducing the security.

Moreover, it is also recommanded to use a hash whose size matches the subgroup. It is the reason why SHA256/Keccak256 is perfect for [secp256r1](https://neuromancer.sk/std/secg/secp256r1) which is defined in a 256-bit prime field.

Reference: 

- [stackoverflow.com - Openssl ECDSA sign input as-is - without digest](https://stackoverflow.com/questions/61775022/openssl-ecdsa-sign-input-as-is-without-digest)
- [crypto.stackexchange - Why the need to hash before signing small data?](https://crypto.stackexchange.com/questions/15295/why-the-need-to-hash-before-signing-small-data), [nvlpubs.nist.gov - FIPS 186-5](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-5.pdf)
- [crypto.stackexchange.com - Is it secure to ECDSA-sign a public key without hashing it first?](https://crypto.stackexchange.com/questions/48716/is-it-secure-to-ecdsa-sign-a-public-key-without-hashing-it-first)

### Read-only reentrancy

> What is read-only reentrancy?

*Read-only* reentrancy attacks target `view` functions that contain reentrancy vulnerabilities. 

In general, reentrancy attack targets state-modifying function in order to exploit the order where the state is updated.

In the case of Read-only reentrancy, the goal is to call a view function which values returned by the function are not yet updated.

An example has been [reported by ChainSecurity](https://chainsecurity.com/curve-lp-oracle-manipulation-post-mortem/) on Curve Finance: 

- An attacker can deposit tokens into one of the pools, then quickly  start a withdrawal. 
- During the transaction, the attacker can exploit the transitional moment where the pool is imbalanced: the tokens are out but  the balance hasn’t been updated 
- By exploiting this vulnerability, the attacker can manipulate the prince and inflate  the value of the pool

Reference: [dragonscVyper, Reentrancy, Curve Finance and the Danger to DeFi](https://blog.dragonscale.ai/vyper-reentrancy-curve-finance-and-the-danger-to-defi/)

Another example is the Sentiment plaform, which allows opening accounts with Balancer pools as assets. In this case, Sentimens called the function `getPrice(token)`from Balancer to know the price of an asset. By using a Read-only reentrancy on this function and a flashloan from Aave, an attacker managed to inflate the price of an asset, because the function `getPrice`does not return the correct price, in a pool and drained the protocol by repeatedly borrow an asset from the platform.

Reference: [Zokyo - Read-only reentrancy attacks: understanding the threat to your smart contracts](https://medium.com/zokyo-io/read-only-reentrancy-attacks-understanding-the-threat-to-your-smart-contracts-99444c0a7334)



Other references:  [Halborn - What Is Read-Only Reentrancy?](https://www.halborn.com/blog/post/what-is-read-only-reentrancy), [SCT Italia - Understanding the Threat of Read- Only Reentrancy Attacks on YourSmart Contracts](https://smartcontract.tips/articoli/understanding-the-threat-of-read-only-reentrancy-attacks-on-yoursmart-contracts/)



###  Symbolic manipulation testing

> Describe how symbolic manipulation testing works.

With symbolic manipulation, the variables in the programs are replaced by expression ("symbolic") instead of using concrete value.

When a program is executed symbolically, the values of the variables are not fixed, but are instead represented as expressions in terms of other symbolic variables.

Symbolic testing can be used as a formal verification method since symbolic testing can check the program for all possible inputs.

You can perform symbolic testing for Solidity smart contracts with [Manticore](https://github.com/trailofbits/manticore), [Mythril](https://github.com/ConsenSys/mythril) or [Halmos](https://github.com/a16z/halmos)

Reference: [Solidity Security Practices Part X: Symbolic Execution](https://medium.com/coinmonks/solidity-security-practices-part-x-symbolic-execution-3af2b82f53aa), [Symbolic testing with Halmos: Leveraging existing tests for formal verification](https://a16zcrypto.com/posts/article/symbolic-testing-with-halmos-leveraging-existing-tests-for-formal-verification/)

> What are the security considerations of reading a (memory) bytes array from an untrusted smart contract call?

According to a [Consensys article](https://consensys.io/blog/ethereum-smart-contract-security-recommendations), external calls may execute malicious code in that contract *or* any other contract that it depends upon.

The smart contract called can also try to perform `re--entrancy`, so the function has to be correctly protected against.

Moreover, the call should not be performed with `Delegatecall` since it hands over all control to the delegatecallee.

Reference: [Consensys - Ethereum Smart Contract Security Recommendations](https://consensys.io/blog/ethereum-smart-contract-security-recommendations), [Consensys - External Calls](https://consensys.github.io/smart-contract-best-practices/development-recommendations/general/external-calls/), [RareSkills - Smart Contract Security](https://www.rareskills.io/post/smart-contract-security)



## Solidity

### Function modifier

> Are function modifiers called from right to left or left to right, or is it non-deterministic?

According to the documentation, they are evaluated in the order presented.  Therefore, I suppose that it is left-to-right.

Reference: [docs.soliditylang.org/function-modifiers](https://docs.soliditylang.org/en/latest/contracts.html#function-modifiers)

### selfdestruct

> When selfdestruct is called, at what point is the Ether transferred? At what point is the smart contract's bytecode erased?

Selfdestruct can no longer destruct/erase the contract bytecode since the Cancun upgrade, more information in [my article](https://rya-sge.github.io/access-denied/2024/03/13/EIP-6780-selfdestruct/).

Before that, my guess is that the contract was only really destroyed at the end of the transaction.

References:

- [docs.soliditylang.org/en/latest/units-and-global-variables.html#contract-related](https://docs.soliditylang.org/en/latest/units-and-global-variables.html#contract-related)

- [hackmd.io/@vbuterin/selfdestruct](https://hackmd.io/@vbuterin/selfdestruct)


### "years" keyword

> Why did Solidity deprecate the "years" keyword?

It was removed because not every year equals 365 days and not even every day has 24 hours-.

This difference come from because of [leap seconds](https://en.wikipedia.org/wiki/Leap_second), a one-[second](https://en.wikipedia.org/wiki/Second) adjustment that is occasionally applied to [Coordinated Universal Time](https://en.wikipedia.org/wiki/Coordinated_Universal_Time) (UTC).

Reference: [docs.soliditylang.org - time-units](https://docs.soliditylang.org/en/latest/units-and-global-variables.html#time-units)

### Signed integer

> What does an int256 variable that stores -1 look like in hex?

We can apply the [Two's complement](https://www.cs.cornell.edu/~tomf/notes/cps104/twoscomp.html).

- Reverse the sign by inverting  the bits (0 goes to 1, and 1 to 0) 

- Add one to the resulting number.

b0.....1 =>(sing inversion) b1......0 => (add one) => b1....1 => (hexa) 0xFFF....FFFF

The answer is **0xFFFF....FFFF**

### Call with value (payable)

> What is the difference between a) payable(msg.sender).call{value: value}(””) and b) msg.sender.call{value: value}(””)?

The keyword payable is only a requirement to send ethers with the function `send` or `transfer` because these functions are not available with a traditional address.

I don't think it is really useful to use payable with`call`.

Reference: [solidity-by-example.org/payable/](https://solidity-by-example.org/payable/), [docs.soliditylang.org/en/v0.8.25/types.html#members-of-addresses](https://docs.soliditylang.org/en/v0.8.25/types.html#members-of-addresses)

## EVM / Assembly

> What addresses to the ethereum precompiles live at?

Ethereum precompiles behave like smart contracts built into the Ethereum protocol. The nine precompiles live in addresses `0x01` to `0x09`.

Precompiles do not execute inside a smart contract, they are part of the Ethereum client specification. You can see a list of them here in the Geth client: [github.com/go-ethereum/.../vm/contracts.go#L73](https://github.com/ethereum/go-ethereum/blob/master/core/vm/contracts.go#L73). Because they are a protocol specification, they are listed in the [Ethereum Yellow Paper](https://ethereum.github.io/yellowpaper/paper.pdf) (in Appendix E).

The list:

| Address | Name                     | Description                                                  |
| ------- | ------------------------ | ------------------------------------------------------------ |
| 0x1     | ecrecover                | Elliptic curve digital signature recovery                    |
| 0x2     | sha256hash               | Hash methods to interact with bitcoin                        |
| 0x3     | ripemd160hash            | Hash methods to interact with bitcoin                        |
| 0x4     | dataCopy (Identity)      | The identity precompile copies one region of memory to another. |
| 0x5     | bigModExp{eip2565: true} | Use for RSA                                                  |
| 0x6     | bn256AddIstanbul         | Used for  zero knowledge proof                               |
| 0x7     | bn256PairingIstanbul     | Used for  zero knowledge proof                               |
| 0x8     | blake2F                  | Hash methods to interact with zcasch                         |

**References**

- [RareSkills - Ethereum precompiled contracts](https://www.rareskills.io/post/solidity-precompiles)

### Function selector

> How does Solidity manage the function selectors when there are more than 4 functions?

If there are more than 4 functions, the EVM will use a binary search to search in the table. A *Binary search* begins by comparing an element in the middle of the array with the target value. 

See my previous article on the hard questions [https://rya-sge.github.io/access-denied/2024/03/04/solidity-interview-question-rareskills-hard/#function-name](https://rya-sge.github.io/access-denied/2024/03/04/solidity-interview-question-rareskills-hard/#function-name).

### delegatecall

> If a delegatecall is made to a contract that makes a delegatecall to another contract, who is msg.sender a)in the proxy, b) the first contract (A), c) and the second contract(B)?

=>` is a regular call and ` ==>` is a `delegatecall

We have:

user => proxy `==>` contract A (implm) `==>` Contract B

a) In the proxy, msg.sender is the user

b) In the first contract A, `msg.sender` is the user since it inherits the context of the proxy

b) In the second contract, `msg.sender` is still the user since it uses the context transmitted by A, which is the proxy's context.

In this case, when A make the deleagtecall to B, it transmis in the call the context of the proxy, so `msg.sender` is the regular user in the proxy

### ABI encoding

> How does ABI encoding vary between calldata and memory, if at all?

There is no difference in my opinion. I haven't seen any information indicating that there are differences in the [solidity documentation](https://docs.soliditylang.org/en/v0.8.25/abi-spec.html)



> If you do a delegatecall to a contract and the opcode CODESIZE executes, which contract size will be returned?

Since the code is executed in the context of the calling contract, I suppose that the size returned is the proxy's size. Moreover, when we use the opcode balance, the returned balance is the proxy's balance according to this [reference](https://blockchain-academy.hs-mittweida.de/courses/solidity-coding-beginners-to-intermediate/lessons/solidity-5-calling-other-contracts-visibility-state-access/topic/delegatecall/).

### uint - Calldata

> What is the difference between how a uint64 and uint256 are abi-encoded in calldata?

No difference if n <= 264 since the uint64 will be padded with zero to 32 bytes/256 bits

See [docs.soliditylang.org/en/v0.8.25/abi-spec.html#examples](https://docs.soliditylang.org/en/v0.8.25/abi-spec.html#examples)

> If you deploy an empty Solidity contract, what bytecode will be present on the blockchain, if any?

By default, the solidity compiler appends some metadata about your contract to the runtime code(more info) [here](https://playground.sourcify.dev/), so you will have non-empty code.

It is possible to deactivate the addition of these metadata in the compiler setting.

Reference: [RareSkills - Ethereum smart contract creation code](https://www.rareskills.io/post/ethereum-contract-creation-code)



### Verbatim (Yul)

>  What does the verbatim keyword do, and where can it be used?

The keyword verbatim allows to create bytecode :

- for opcodes which are not known to the Yul compiler
- which will not be modified by the optimizer.

This keyword does not exist in solidity and can only be used inside a yul file.

Reference: [docs.soliditylang.org/en/latest/yul.html#verbatim]( https://docs.soliditylang.org/en/latest/yul.html#verbatim), [How to use Yul Verbatim with Solidity](https://medium.com/coinmonks/how-to-write-any-function-in-pure-opcodes-and-add-it-to-your-solidity-function-yul-verbatim-c1ce2760f7a5)

### signextend opcode

> What is the use of the signextend opcode?

This opcode allows to extend the sign of a signed integer

Reference: [EVM SIGNEXTEND Opcode explanation](https://ethereum.stackexchange.com/questions/63062/evm-signextend-opcode-explanation)

### Smart contract metadata

> What is stored in the metadata section of a smart contract?

The metadata contains two main information:

- the IPFS hash of the metadata file. 

This file, in the JSON format, is automatically generated by the Solidity compiler. By adding this hash to the runtime bytecode, you can check the authenticity of the file by using the hash.

- The solidity compiler (solc) version

Reference: [docs.soliditylang.org/en/latest/metadata.html,](https://docs.soliditylang.org/en/latest/metadata.html,) [RareSkills - Understanding smart contract metadata](https://www.rareskills.io/post/solidity-metadata)

### Validate on-chain event

> How can you validate on-chain that another smart contract emitted an event, without using an oracle?

This operation seems complicated to do on-chain without an oracle. My first guess is that it is currently not possible to perform this action.

Discussion on this topic [ethereum.stackexchange - Proving the Existence of Logs to the Blockchain](https://ethereum.stackexchange.com/questions/16117/proving-the-existence-of-logs-to-the-blockchain)



### Proxy free pointer

> Under what conditions does the Openzeppelin Proxy.sol overwrite the free memory pointer? Why is it safe to do this?

As indicated in a comment in the [Proxy.sol](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/11dc5e3809ebe07d5405fe524385cbe4f890a08b/contracts/proxy/Proxy.sol#L25) file:

"We take full control of memory in this inline assembly block because it will not return to Solidity code. We overwrite the Solidity scratch pad at memory position 0."

The reason why they do this is because there is no code after the assembly block where the overwrite operation is performed. Thus, there is no risk that another instructions overwrite this part of the memory.

Reference: [Proxy forwarding: `0x40` pointer vs 0 pointer](https://forum.openzeppelin.com/t/proxy-forwarding-0x40-pointer-vs-0-pointer/29826)

## Zero-knowledge

###  zk-friendly hash function

> What is a zk-friendly hash function and how does it differ from a non-zk-friendly hash function?

Contrary to traditional programmation, the efficiency of the circuits in ZK protocols depends on their algebraic structure. Thus, standard hash function like SHA-2 and SHA-3 were not designed with this principle in mind but more with others metrics such as running time.

Zk-friendly hash function will try to be represent as simple expression in a large fields, which is more efficient in terms of prover execution time and proof size.

Example of zk-friendly hash function: [MiMC](https://byt3bit.github.io/primesym/), [Poseidon](https://eprint.iacr.org/2019/458.pdf), and Vision/Rescue

Reference: [zellic.io - ZK-Friendly Hash Functions](https://www.zellic.io/blog/zk-friendly-hash-functions/)

### nullifier

> What is a nullifier in the context of zero knowledge, and what is it used for?

It refers to a private/secret value which, once revealed, can not be used again.

It is similar to a nonce, but unlike this one, the nullifier is destined to be secret.

It is used for example by Tornado cash where each deposit is associated with a unique, secret nullifier. To withdraw funds, users have to reveal this nullifier. Once the nullifier has been revealed, it is not possible to use it again in order to avoid a malicious user to perform the same withdrawal again.

Reference: [2π.com/22/nullifiers/](https://2π.com/22/nullifiers/), [nmohnblatt.github.io/zk-jargon-decoder/definitions/nullifier.html](https://nmohnblatt.github.io/zk-jargon-decoder/definitions/nullifier.html)
