---
layout: post
title: Gas Sponsorship on Ethereum - A Comparative Analysis of ERC-2612, ERC-2771, ERC-4337, EIP-7702, and Beyond
date: 2026-02-11
lang: en
locale: en-GB
categories: blockchain ethereum solidity
tags: blockchain ethereum gas-sponsorship meta-transactions account-abstraction ERC-4337 EIP-7702 ERC-2771 ERC-2612
description: A technical comparison of Ethereum gas sponsorship standards (ERC-2612, ERC-2771, ERC-4337, EIP-7702, ERC-3009, RIP-7560) analyzing their architecture, trade-offs, and use cases.
image:
isMath: false
---

One of the persistent challenges in the Ethereum ecosystem is the requirement for users to hold ETH to pay for gas fees. This creates a significant barrier to onboarding: a new user who receives ERC-20 tokens cannot use them without first acquiring ETH from a separate source. Over the years, the Ethereum community has developed multiple standards to address this problem, each operating at a different layer of the stack and making different trade-offs between complexity, generality, decentralization, and user custody.

This article provides a technical comparison of the major gas sponsorship standards: ERC-2612, ERC-2771, ERC-4337, EIP-7702, as well as less commonly discussed alternatives such as ERC-3009 and RIP-7560. It examines their architectures, security models, and the scenarios for which each is best suited.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The Gas Problem

In Ethereum's execution model, every transaction requires the sender to pay a gas fee denominated in the chain's native currency (ETH on mainnet). This design creates several practical problems.

First, there is an **onboarding barrier**: new users cannot interact with dApps until they acquire ETH, even if they already hold other tokens. Second, there is a **UX friction**: common workflows such as approving and spending an ERC-20 token require two separate transactions, each incurring gas costs. Third, there is a **custody rigidity**: EOAs (Externally Owned Accounts) have a fixed authentication model based on a single secp256k1 private key, with no built-in support for key rotation, social recovery, or multisig. Gas sponsorship solutions often address several of these issues simultaneously, as the underlying mechanisms for separating the gas payer from the transaction initiator also enable other UX improvements.

## ERC-2612: Permit (Gasless ERC-20 Approvals)

### Overview

[ERC-2612](https://eips.ethereum.org/EIPS/eip-2612) (status: **Final**, created 2020-04-13) extends the ERC-20 token standard with a `permit` function that allows users to modify the `allowance` mapping using a signed [EIP-712](https://eips.ethereum.org/EIPS/eip-712) message rather than an on-chain `approve` transaction. This removes the need for the token holder to submit (and pay gas for) the approval transaction themselves.

### Architecture

ERC-2612 introduces three functions to compliant ERC-20 tokens:

```solidity
function permit(
    address owner,
    address spender,
    uint value,
    uint deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
) external;

function nonces(address owner) external view returns (uint);

function DOMAIN_SEPARATOR() external view returns (bytes32);
```

The signed message follows the EIP-712 typed data format:

```solidity
keccak256(abi.encodePacked(
   hex"1901",
   DOMAIN_SEPARATOR,
   keccak256(abi.encode(
       keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
       owner,
       spender,
       value,
       nonce,
       deadline
   ))
));
```

The `DOMAIN_SEPARATOR` is typically computed from the token's name, version, chain ID, and contract address, providing cross-chain and cross-contract replay protection.

### Gas Sponsorship Model

The gas sponsorship in ERC-2612 is narrowly scoped: a relayer can call `permit` on behalf of the user, paying the gas for the approval step. This is typically combined with a subsequent `transferFrom` in the same transaction. The user signs the permit off-chain (no gas required), and the relayer submits both the permit and the subsequent operation in a single on-chain transaction.

The relayer may be compensated out-of-band, for example by deducting a fee from the transferred amount, or the application operator may subsidize the gas cost entirely.

### Limitations

- **Scope**: ERC-2612 only covers ERC-20 approvals. It does not generalize to arbitrary contract interactions, ETH transfers, or other token standards (ERC-721, ERC-1155).
- **Token dependency**: The ERC-20 token contract itself must implement the `permit` function. Tokens deployed without ERC-2612 support cannot benefit from this mechanism retroactively.
- **Censorship risk**: The relayer can withhold a signed permit. The `deadline` parameter mitigates this by bounding the signature's validity window.
- **Front-running**: Although another party can front-run the permit submission, the end result for the signer is functionally identical (the allowance is set regardless of who submits it).
- **Race condition**: The standard ERC-20 approval race condition ([SWC-114](https://swcregistry.io/docs/SWC-114/)) also applies to permits.

### Adoption

ERC-2612 has been widely adopted. Major ERC-20 tokens (USDC, DAI, UNI, and most tokens deployed via OpenZeppelin v5+) implement the permit extension. It was popularized by Uniswap V2 and has become a de facto standard for new ERC-20 deployments.

## ERC-2771: Meta-Transactions via Trusted Forwarder

### Overview

[ERC-2771](https://eips.ethereum.org/EIPS/eip-2771) (status: **Final**, created 2020-07-01) defines a contract-level protocol for **recipient contracts** to accept meta-transactions through a **Trusted Forwarder**. Unlike ERC-2612, it is a general-purpose mechanism that can be applied to any contract interaction, not just token approvals.

### Architecture

The protocol involves four actors:

1. **Transaction Signer**: The end user who signs a transaction off-chain.
2. **Gas Relay**: An off-chain service that receives the signed request and submits it as an on-chain transaction, paying the gas.
3. **Trusted Forwarder**: An on-chain contract that verifies the user's signature and nonce, then forwards the call to the recipient, appending the original signer's address to the calldata.
4. **Recipient**: The target contract that processes the meta-transaction.

The Trusted Forwarder appends the signer's address (20 bytes) to the end of the calldata:

```solidity
(bool success, bytes memory returnData) = to.call.value(value)(
    abi.encodePacked(data, from)
);
```

The recipient contract overrides its `_msgSender()` function to extract this appended address when the call originates from a trusted forwarder:

```solidity
function _msgSender() internal view returns (address payable signer) {
    signer = msg.sender;
    if (msg.data.length >= 20 && isTrustedForwarder(signer)) {
        assembly {
            signer := shr(96, calldataload(sub(calldatasize(), 20)))
        }
    }
}
```

The recipient must implement a discovery function:

```solidity
function isTrustedForwarder(address forwarder) external view returns (bool);
```

### Gas Sponsorship Model

Gas sponsorship in ERC-2771 is explicit: the gas relay pays for the on-chain transaction. The relay can be operated by the application developer (subsidizing user gas), by a third-party relay network (such as the Gas Station Network / [OpenGSN](https://opengsn.org/)), or by any entity willing to pay gas on behalf of users.

The user retains full custody: every action requires the user's off-chain signature. The gas relay cannot forge or modify the user's intent, provided the Trusted Forwarder correctly verifies signatures.

### Limitations

- **Recipient modification required**: Every contract that wishes to support meta-transactions must inherit `ERC2771Context` (or equivalent), replacing all uses of `msg.sender` with `_msgSender()`. This is a non-trivial integration effort and makes the standard incompatible with already-deployed contracts.
- **Trust in the forwarder**: A malicious or compromised forwarder can forge the `_msgSender()` value, impersonating any address. The security of the entire system depends on the forwarder's correctness. If the forwarder is upgradeable, the trust extends to the upgrade authority.
- **No standardized relay protocol**: ERC-2771 standardizes only the contract-level interface (how the recipient extracts the sender). The off-chain protocol between the user, the gas relay, and the forwarder is not specified by the standard.
- **Limited to `msg.sender` abstraction**: ERC-2771 abstracts only the sender address. It does not abstract gas payment logic, signature validation, or execution flow.

## ERC-4337: Account Abstraction via Alt Mempool

### Overview

[ERC-4337](https://eips.ethereum.org/EIPS/eip-4337) (status: **Review**, created 2021-09-29) introduces a comprehensive account abstraction system without requiring changes to the Ethereum consensus layer. It replaces the concept of EOA-originated transactions with **UserOperations** (pseudo-transactions) that are processed by a network of **Bundlers** through a singleton **EntryPoint** contract.

ERC-4337 is the most architecturally ambitious of the standards discussed in this article. It does not merely abstract gas payments; it abstracts the entire transaction validation and execution model, allowing Smart Contract Accounts to define custom signature verification, nonce management, and gas payment logic.

### Architecture

The system introduces several new actors and contracts:

- **UserOperation**: A data structure describing the user's intended action. It contains fields analogous to a standard transaction (`sender`, `nonce`, `callData`, `maxFeePerGas`, etc.) plus additional fields for gas limits, paymaster data, and factory data.
- **EntryPoint**: A singleton contract deployed at a well-known address that processes bundles of `UserOperations`. It enforces the separation between validation and execution.
- **Bundler**: An off-chain node that collects `UserOperations` from a dedicated P2P mempool, simulates them for validity, and packages them into standard Ethereum transactions that call `EntryPoint.handleOps()`.
- **Smart Contract Account (SCA)**: The user's on-chain account, which must implement `IAccount.validateUserOp()` to verify signatures and pay fees.
- **Paymaster**: An optional contract that agrees to pay gas fees on behalf of the user.
- **Factory**: A contract that deploys new Smart Contract Accounts on-demand via `CREATE2`.

The core entry point interface:

```solidity
function handleOps(
    PackedUserOperation[] calldata ops,
    address payable beneficiary
) external;
```

The Smart Contract Account interface:

```solidity
interface IAccount {
    function validateUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external returns (uint256 validationData);
}
```

The `handleOps` function performs two loops:

1. **Verification loop**: For each `UserOperation`, it creates the sender account if needed (via factory), calls `validateUserOp` on the sender, and optionally calls `validatePaymasterUserOp` on the paymaster.
2. **Execution loop**: For each successfully validated `UserOperation`, it executes the sender's calldata and handles gas refunds.

### Gas Sponsorship Model: Paymasters

The Paymaster mechanism is the primary gas sponsorship feature of ERC-4337. When a `UserOperation` includes a non-empty `paymasterAndData` field, the EntryPoint delegates gas payment to the specified Paymaster contract instead of charging the sender's deposit.

The Paymaster interface:

```solidity
function validatePaymasterUserOp(
    PackedUserOperation calldata userOp,
    bytes32 userOpHash,
    uint256 maxCost
) external returns (bytes memory context, uint256 validationData);

function postOp(
    PostOpMode mode,
    bytes calldata context,
    uint256 actualGasCost,
    uint256 actualUserOpFeePerGas
) external;
```

Paymasters follow a "pre-charge, then refund" model. Common Paymaster implementations include:

- **Verifying Paymaster**: Accepts `UserOperations` signed by an off-chain service, allowing application operators to whitelist sponsored actions.
- **Token Paymaster**: Charges the user in ERC-20 tokens instead of ETH, handling the token-to-ETH conversion internally.
- **Depositor Paymaster**: Draws from a pre-funded deposit in the EntryPoint, allowing dApp developers to sponsor gas for all their users.

### Security Considerations

- **DoS protection**: Bundlers must simulate `UserOperations` before inclusion to prevent DoS attacks. The validation code is sandboxed with strict opcode and storage access rules to prevent griefing.
- **Reputation system**: Paymasters and Factories are "global" entities accessed by multiple `UserOperations`. To prevent abuse, the system uses a reputation/staking mechanism where entities that cause excessive invalidation are throttled or banned.
- **EntryPoint centrality**: The EntryPoint contract is a critical trust point for the entire ecosystem. It must be thoroughly audited and formally verified.
- **Storage collisions**: Smart Contract Accounts that are upgradeable (via proxy or EIP-7702) must ensure no storage layout conflicts between implementations. The recommended approach is [ERC-7201](https://eips.ethereum.org/EIPS/eip-7201) (namespaced storage layout).

### ERC-4337 and EIP-7702 Interoperability

ERC-4337 explicitly supports [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702)-delegated accounts. When the `factory` field in a `UserOperation` is set to the special value `0x7702`, the EntryPoint treats the sender as an EIP-7702 delegated EOA. The bundler wraps the bundle in a type `0x04` (SET_CODE) transaction, including the necessary authorization tuples.

This interoperability means that existing EOAs can opt into the ERC-4337 ecosystem without migrating funds to a new smart contract wallet. They simply delegate their EOA to an ERC-4337-compatible wallet implementation via EIP-7702.

### Limitations

- **Complexity**: ERC-4337 introduces significant architectural complexity. Deploying and operating within the ERC-4337 ecosystem requires understanding `UserOperations`, bundlers, the EntryPoint, paymasters, factories, and the associated simulation rules.
- **Infrastructure dependency**: The system relies on a separate P2P mempool and bundler infrastructure. Although the design is permissionless (anyone can run a bundler), in practice the ecosystem depends on the availability of bundler services.
- **Gas overhead**: The EntryPoint contract adds gas overhead compared to a direct EOA transaction. The verification loop, paymaster interactions, and post-operation processing all consume additional gas.
- **Compatibility**: Pre-ERC-4337 smart contract wallets cannot be used directly, as they lack the `validateUserOp` function. A wrapper contract is needed to bridge legacy wallets.

## EIP-7702: Set Code for EOAs

### Overview

[EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) (status: **Final**, created 2024-05-07) is a protocol-level change introduced with the Pectra upgrade. It adds a new [EIP-2718](https://eips.ethereum.org/EIPS/eip-2718) transaction type (`0x04`) that allows EOAs to delegate their code execution to a smart contract by writing a **delegation indicator** (`0xef0100 || address`) to the EOA's code field.

Unlike the application-layer standards discussed above, EIP-7702 is a core protocol change that modifies the EVM's execution rules. It was designed as a successor to [EIP-3074](https://eips.ethereum.org/EIPS/eip-3074) (AUTH/AUTHCALL), which was ultimately not adopted.

### Architecture

An EIP-7702 transaction includes an `authorization_list` of tuples, each signed by the EOA that wishes to delegate:

```
authorization_list = [[chain_id, address, nonce, y_parity, r, s], ...]
```

For each authorization tuple, the protocol:

1. Recovers the `authority` address from the signature.
2. Verifies the authority's code is empty or already delegated.
3. Verifies the nonce matches.
4. Writes the delegation indicator `0xef0100 || address` to the authority's code field.
5. Increments the authority's nonce.

Once the delegation indicator is set, all code-executing operations (`CALL`, `CALLCODE`, `DELEGATECALL`, `STATICCALL`) on the authority's account load and execute the code at the delegated `address`, in the context of the authority's account (its storage, balance, and address).

The delegation is **persistent**: it survives beyond the transaction that set it. To clear it, the user must submit another EIP-7702 transaction delegating to `address(0)`.

### Gas Sponsorship Model

EIP-7702 enables gas sponsorship through two mechanisms:

1. **Third-party sponsorship**: A sponsor (not the EOA owner) submits the EIP-7702 transaction, paying the gas. The authorization tuple is signed by the EOA owner, but the outer transaction is signed and paid for by the sponsor.
2. **Self-sponsoring**: The EOA owner submits the transaction themselves, delegating to code that implements batching or other UX improvements. The owner pays gas once but can perform multiple operations atomically.

When combined with ERC-4337, EIP-7702 enables the full account abstraction stack: the EOA delegates to an ERC-4337-compatible wallet implementation, gaining access to paymasters, bundlers, and the entire AA ecosystem while retaining its original address.

### Key Features

- **Batching**: Multiple operations can be executed atomically in a single transaction (e.g., approve + swap).
- **Sponsorship**: A third party can pay gas on behalf of the EOA.
- **Privilege de-escalation**: Users can sign sub-keys with restricted permissions (e.g., spend only ERC-20 tokens, not ETH; daily spending limits).
- **Forward compatibility**: EOAs can delegate to ERC-4337 wallet implementations, unifying the EOA and smart contract wallet ecosystems.

### Security Considerations

- **Delegation is powerful**: The delegated code has full access to the EOA's storage, balance, and execution context. A poorly implemented or malicious delegate contract can allow complete account takeover.
- **Front-running initialization**: Since EIP-7702 does not support initcode, storage initialization must be performed in a separate call after delegation. Developers must ensure that initialization calldata is signed by the EOA's key (using ecrecover) to prevent front-running.
- **Storage management**: When changing delegation targets, storage layout collisions can occur. Contracts should use [ERC-7201](https://eips.ethereum.org/EIPS/eip-7201) namespaced storage to avoid conflicts.
- **Broken invariants**: EIP-7702 breaks the invariant that `tx.origin == msg.sender` only holds in the topmost execution frame. Contracts relying on this check for reentrancy protection or flash loan defense may be affected.
- **Transaction propagation**: Once an EOA is delegated, its balance can be modified by external calls (not just transactions it originates), complicating mempool validation. Clients are advised to accept at most one pending transaction per delegated EOA.

## Additional Gas Sponsorship Approaches

### ERC-3009: transferWithAuthorization

[ERC-3009](https://eips.ethereum.org/EIPS/eip-3009) (status: **Stagnant**) extends ERC-20 with a `transferWithAuthorization` function that allows gasless token transfers (not just approvals, as in ERC-2612). The user signs an EIP-712 message authorizing a transfer, and a relayer submits it on-chain.

```solidity
function transferWithAuthorization(
    address from,
    address to,
    uint256 value,
    uint256 validAfter,
    uint256 validBefore,
    bytes32 nonce,
    uint8 v,
    bytes32 r,
    bytes32 s
) external;
```

Compared to ERC-2612, ERC-3009 is more direct (it transfers tokens, not just approvals) and uses a random nonce instead of a sequential one, enabling non-ordered submission. However, it shares the same fundamental limitation: the token contract must implement the standard. It has been adopted by USDC (Circle's reference implementation).

### RIP-7560: Native Account Abstraction

[RIP-7560](https://github.com/ethereum/RIPs/blob/master/RIPS/rip-7560.md) proposes **native account abstraction** at the protocol level, as opposed to ERC-4337's application-layer approach. It introduces a new transaction type that the protocol itself processes with account abstraction semantics, including native support for paymasters, factories, and custom validation logic.

RIP-7560 is designed to complement, and eventually supersede, ERC-4337 by moving its functionality into the consensus layer. This would eliminate the gas overhead of the EntryPoint contract, simplify the bundler architecture, and provide stronger DoS protection guarantees. As a Rollup Improvement Proposal (RIP), it is primarily targeted at L2 rollups rather than Ethereum mainnet, although it could eventually be adopted at L1 as well.

### EIP-3074: AUTH and AUTHCALL (Superseded)

[EIP-3074](https://eips.ethereum.org/EIPS/eip-3074) proposed two new EVM opcodes, `AUTH` and `AUTHCALL`, that would allow a contract (the "invoker") to send transactions on behalf of an EOA. The EOA would sign a message authorizing the invoker, and `AUTHCALL` would execute calls with the EOA's address as `msg.sender`.

EIP-3074 was ultimately superseded by EIP-7702, which provides similar functionality through a different mechanism (code delegation instead of new opcodes). The Ethereum core developers favored EIP-7702 because it avoids introducing opcodes that would become obsolete in a post-EOA world and because it is more naturally compatible with ERC-4337.

### Gas Station Network (GSN / OpenGSN)

The [Gas Station Network](https://opengsn.org/) is not a standard but an infrastructure implementation built on top of ERC-2771. It provides a decentralized network of relayers that forward meta-transactions on behalf of users. GSN includes:

- A relay hub contract that manages relayer registration and staking.
- A paymaster system (separate from ERC-4337 paymasters) that determines who pays for gas.
- A relay selection algorithm that chooses the cheapest available relayer.

GSN was one of the earliest practical gas sponsorship solutions and popularized the ERC-2771 pattern. However, its adoption has been limited compared to ERC-4337, partly due to the requirement for recipient contracts to implement `ERC2771Context`.

## Comparative Analysis

### Summary Table

| Feature | ERC-2612 | ERC-2771 | ERC-4337 | EIP-7702 |
|---|---|---|---|---|
| **Type** | ERC (application layer) | ERC (application layer) | ERC (application layer) | EIP (protocol layer) |
| **Status** | Final | Final | Review | Final |
| **Scope** | ERC-20 approvals only | General-purpose meta-transactions | Full account abstraction | EOA code delegation |
| **Protocol changes** | None | None | None | New transaction type (`0x04`) |
| **User signature** | EIP-712 (off-chain) | Off-chain (verified by forwarder) | UserOperation signature | Authorization tuple signature |
| **Gas payer** | Relayer | Gas relay | Bundler / Paymaster | Transaction sender / sponsor |
| **User custody** | User retains full custody | User retains full custody | User controls SCA via custom validation | User retains EOA key |
| **Contract modification** | Token must implement `permit` | Recipient must implement `ERC2771Context` | Account must implement `IAccount` | None (native EVM support) |
| **Token support** | ERC-20 only | Any (if recipient supports it) | Any | Any |
| **Batching** | No | No (single call per meta-tx) | Yes (via SCA calldata) | Yes (via delegated code) |
| **Custom validation** | No | No | Yes (arbitrary logic) | Yes (via delegated code) |
| **Infrastructure needed** | None (relayer optional) | Forwarder + relay | EntryPoint + bundler network | None |
| **Complexity** | Low | Medium | High | Medium |
| **Gas overhead** | Minimal | Moderate (forwarder call) | High (EntryPoint processing) | Moderate (delegation resolution) |

### Choosing the Right Standard

**Use ERC-2612** when:
- The use case is limited to ERC-20 token interactions.
- Simplicity and minimal integration overhead are priorities.
- The token contract is being deployed (or already supports `permit`).
- A common pattern: approve + action in a single relayed transaction.

**Use ERC-2771** when:
- General-purpose meta-transaction support is needed for a specific set of contracts.
- The application developer controls the recipient contracts and can add `ERC2771Context`.
- A simpler architecture than ERC-4337 is desired.
- The trust model of a single Trusted Forwarder is acceptable.

**Use ERC-4337** when:
- Full account abstraction is required (custom signature validation, key rotation, social recovery, multisig).
- Decentralized, permissionless gas sponsorship is needed.
- The application must support complex gas payment models (ERC-20 payments, cross-chain gas, developer subsidies).
- Forward compatibility with native account abstraction (RIP-7560) is desired.

**Use EIP-7702** when:
- Existing EOAs need smart contract capabilities without migrating funds.
- Batching, sponsorship, or privilege de-escalation is needed at the protocol level.
- The application targets chains that have adopted the Pectra upgrade.
- Combining with ERC-4337 for the full AA experience while preserving the EOA address.

### Composability

These standards are not mutually exclusive. In practice, the most powerful gas sponsorship setups combine multiple approaches:

1. **ERC-2612 + Relayer**: A relayer submits `permit` + `transferFrom` in one transaction, enabling gasless ERC-20 usage for supported tokens.
2. **EIP-7702 + ERC-4337**: An EOA delegates to an ERC-4337 wallet via EIP-7702, gaining access to paymasters, bundlers, and the full AA infrastructure while keeping its original address.
3. **ERC-2771 + GSN**: A recipient contract integrates `ERC2771Context`, and the GSN provides the relay infrastructure with a decentralized network of gas-paying relayers.
4. **ERC-4337 + Token Paymaster**: A Smart Contract Account uses a Token Paymaster to pay gas fees in USDC or another stablecoin, completely eliminating the user's need to hold ETH.

## Conclusion

The evolution of gas sponsorship on Ethereum reflects the broader maturation of the ecosystem. Early solutions like ERC-2612 and ERC-2771 addressed specific pain points with minimal complexity. ERC-4337 introduced a comprehensive account abstraction framework at the application layer, and EIP-7702 brought native protocol support that bridges the gap between EOAs and smart contract wallets.

No single standard is universally optimal. ERC-2612 remains the simplest solution for ERC-20-centric workflows. ERC-2771 provides a lightweight meta-transaction layer for controlled environments. ERC-4337 offers the most complete account abstraction with decentralized gas sponsorship. EIP-7702 enables protocol-level upgrades to existing EOAs. Together, these standards form a layered toolkit that can be combined to meet the specific requirements of any application.

```
@startmindmap
* Gas Sponsorship\non Ethereum
** ERC-2612\n(Permit)
*** ERC-20 approvals only
*** EIP-712 off-chain signatures
*** Minimal complexity
*** Token must implement permit
** ERC-2771\n(Meta-Tx)
*** General-purpose
*** Trusted Forwarder pattern
*** Recipient must be modified
*** GSN relay network
** ERC-4337\n(Account Abstraction)
*** Full account abstraction
*** UserOperation + Bundler + EntryPoint
*** Paymaster for gas sponsorship
*** Custom validation logic
*** Decentralized bundler network
*** EIP-7702 interoperability
** EIP-7702\n(Set Code for EOAs)
*** Protocol-level (tx type 0x04)
*** EOA code delegation
*** Batching + Sponsorship
*** Forward-compatible with ERC-4337
*** Pectra upgrade
** Other Approaches
*** ERC-3009 (transferWithAuthorization)
*** RIP-7560 (Native AA)
*** EIP-3074 (AUTH/AUTHCALL, superseded)
*** GSN (OpenGSN relay network)
@endmindmap
```

## Reference

- [ERC-2612: Permit Extension for EIP-20 Signed Approvals](https://eips.ethereum.org/EIPS/eip-2612)
- [ERC-2771: Secure Protocol for Native Meta Transactions](https://eips.ethereum.org/EIPS/eip-2771)
- [ERC-4337: Account Abstraction Using Alt Mempool](https://eips.ethereum.org/EIPS/eip-4337)
- [EIP-7702: Set Code for EOAs](https://eips.ethereum.org/EIPS/eip-7702)
- [ERC-3009: Transfer With Authorization](https://eips.ethereum.org/EIPS/eip-3009)
- [RIP-7560: Native Account Abstraction](https://github.com/ethereum/RIPs/blob/master/RIPS/rip-7560.md)
- [EIP-3074: AUTH and AUTHCALL](https://eips.ethereum.org/EIPS/eip-3074)
- [OpenGSN - Gas Station Network](https://opengsn.org/)
- [EIP-712: Typed Structured Data Hashing and Signing](https://eips.ethereum.org/EIPS/eip-712)
- [ERC-7201: Namespaced Storage Layout](https://eips.ethereum.org/EIPS/eip-7201)
- [Claude Code](https://claude.com/product/claude-code)
