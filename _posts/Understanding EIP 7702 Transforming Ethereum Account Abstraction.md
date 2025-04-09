### Understanding EIP 7702: Transforming Ethereum Account Abstraction

From: https://www.youtube.com/watch?v=_k5fKlKBWV4

EIP 7702 has taken center stage in discussions about Ethereum's evolution, particularly regarding account abstraction. Introduced during a breakout call on Ethereum’s future, this proposal aims to unify user experiences, facilitate smart contract wallet adoption, and build on the foundation laid by previous efforts such as EIP 3074.



Advantage:

, transaction bundling or granting limited permissions to a sub-key.

## Introduction

### Status of Account Abstraction standard

- ERC-4337
  - Solved most AA use-cased
  - no longer "new" - used by serious projects
- EIP-7702
  - Allow EOAs to role-play as Smart counts
  - Scheduled for inclusion with Pectra
- RIP-7560
  - Enshrines ERC-4337 design - becomes native part of L2 rollups
  - Ready for devnet
- EIP-7702
  - Similar to RIP-7560 but less opinionated
  - Targets Ethereum L1 with EOF (Pectra)

### In summary

- Change the behavior of existing EOAs - allow them to have code
- Fully sovled the "execution" part of Account abstraction
- Does not solve the "security part of Account abstraction
  - ECDSA key can override the contract code
  - EOA needed to create Type-4 transactions
- Works well with ERC-4337

#### The Genesis of EIP 7702

The roots of EIP 7702 trace back to years of collaboration among developers, particularly around EIP 3074. Despite criticism suggesting a rushed approach, this proposal is the culmination of iterative development and refinement. By addressing challenges with the Prague hard fork and community consensus, EIP 7702 emerges as a bridge between traditional Ethereum accounts and the expanding world of smart contract wallets.

#### The Technical Innovation

EIP 7702 introduces a new transaction type: the set code transaction. This innovation allows Ethereum Externally Owned Accounts (EOAs) to adopt the capabilities of smart contract wallets by embedding smart contract code directly into EOAs. Key features include:

1. **Unified Interface for Users**: By merging EOA and smart contract wallet functionalities, developers no longer need to design applications that cater to one or the other, fostering a seamless user experience.
2. **Creation by Template**: Unlike traditional smart contract deployment, EIP 7702 simplifies code integration into accounts, reducing the overhead of call data during deployment. This ensures minimal gas costs and streamlined migration of EOAs to smart contract wallets.
3. **Delegation Designators**: A structured bytecode pointer in the account determines where to load smart contract wallet code. This design ensures flexibility and future compatibility, including revocation and updates.

## Motivation

There is a lot of interest in adding short-term functionality improvements to EOAs, increasing the usability of applications and in some cases allowing improved security. Three particular applications include:

- **Batching**: allowing multiple operations from the same user in one atomic transaction. 
  - One common example is an [ERC-20](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md) approval followed by spending that approval, a common workflow in DEXes that requires two transactions today. 
  - Advanced use cases of batching occasionally involve dependencies: the output of the first operation is part of the input to the second operation.
- **Sponsorship**: account X pays for a transaction on behalf of account Y. Account X could be paid in some other ERC-20 for this service, or it could be an application operator including the transactions of its users for free.
- **Privilege de-escalation**: users can sign sub-keys and give them specific permissions that are much weaker than global access to the account. For example, you could imagine a permission to spend ERC-20 tokens but not ETH, or to spend up to 1% of the total balance per day, or to interact only with a specific application.



##### Delegation Designation

The delegation designation uses the banned opcode `0xef` from [EIP-3541](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-3541.md) to designate the code has a special purpose. 

This designator requires:

- all code executing operations to follow the address pointer to get the account's executable code, and requires all other code reading operations to act only on the delegation designator (`0xef0100 || address`). 
- The following reading instructions are impacted: `EXTCODESIZE`, `EXTCODECOPY`, `EXTCODEHASH`
- The following executing instructions are impacted: `CALL`, `CALLCODE`, `STATICCALL`, `DELEGATECALL`, 
- As well as transactions with `destination` targeting the code with delegation designation.

For example, `EXTCODESIZE` would return `23` (the size of `0xef0100 || address`), `EXTCODEHASH` would return `keccak256(0xef0100 || address)`, and `CALL` would load the code from `address` and execute it in the context of `authority`.

`CODESIZE` and `CODECOPY` instructions operate on executable code, as before. *Note that in a delegated execution `CODESIZE` and `CODECOPY` produce different result comparing to `EXTCODESIZE` and `EXTCODECOPY` of execution target.*

In case a delegation designator points to a precompile address, retrieved code is considered empty and `CALL`, `CALLCODE`, `STATICCALL`, `DELEGATECALL` instructions targeting this account will execute empty code, i.e. succeed with no execution given enough gas.

In case a delegation designator points to another designator, creating a potential chain or loop of designators, clients must retrieve only the first code and then stop following the designator chain.



#### Gas Costs

The intrinsic cost of the new transaction is inherited from [EIP-2930](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-2930.md), specifically `21000 + 16 * non-zero calldata bytes + 4 * zero calldata bytes + 1900 * access list storage key count + 2400 * access list address count`. Additionally, we add a cost of `PER_EMPTY_ACCOUNT_COST * authorization list length`.

The transaction sender will pay for all authorization tuples, regardless of validity or duplication.

If a code reading instruction accesses a cold account during the resolution of delegated code, add an additional [EIP-2929](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-2929.md) `COLD_ACCOUNT_READ_COST` cost of `2600` gas to the normal cost and add the account to `accessed_addresses`. Otherwise, assess a `WARM_STORAGE_READ_COST` cost of `100`.

#### Transaction Origination

Modify the restriction put in place by [EIP-3607](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-3607.md) to allow EOAs whose code is a valid delegation designation, i.e., `0xef0100 || address`, to continue to originate transactions. Accounts with any other code values may not originate transactions.

Additionally, if a transaction's `destination` has a delegation designation, add the target of the delegation to `accessed_addresses`.

#### Implementation Process

EIP 7702’s workflow begins with an authorization process:

- **Authorization Details**: Users sign an authorization specifying a target code address, chain ID, and nonce for replay protection.
- **Bundler Assistance**: If the user lacks Ether to pay transaction fees, a bundler relays the signed authorization onto the blockchain.
- **Account Initialization**: Once the delegation designator is set, users initialize their smart contract wallet, defining ownership rules and other configurations.

## Specification



### Parameters

| Parameter                | Value   |
| ------------------------ | ------- |
| `SET_CODE_TX_TYPE`       | `0x04`  |
| `MAGIC`                  | `0x05`  |
| `PER_AUTH_BASE_COST`     | `12500` |
| `PER_EMPTY_ACCOUNT_COST` | `25000` |

#### Enhancing User Security and Flexibility

By enabling EOAs to transition to smart contract wallets, EIP 7702 addresses critical issues such as:

- **Gas Sponsorship**: Delegated accounts can now batch transactions or allow gas fees to be paid by third parties.
- **Privilege De-escalation**: Users can implement multi-signature wallets or limited permissions, enhancing security models.
- **Reversibility**: Delegations can be cleared, restoring EOAs to their original state, thereby reducing user hesitation in adopting this feature.

#### Challenges and Comparisons

While EIP 7702 resolves many issues, it does not replace other Ethereum Improvement Proposals like EIP 4337. For instance, EIP 4337 defines relayers and other critical functionalities not covered by EIP 7702. Moreover, concerns like post-quantum security or recursive delegations are beyond the scope of 7702.

#### Gas Cost Considerations

EIP 7702 aims to balance functionality with efficiency:

- **Authorization Costs**: Setting code incurs an intrinsic cost of 25,000 gas per authorization, with refunds available for existing accounts.
  - If the account already exists, a refund of 12.5k is issued
  - Refund is subject to global refunds mechanics, i.e 20% of the toal gas used by the tx

- **Convenience Warming**: To optimize performance, the delegation target account is pre-warmed, reducing execution overhead.

#### Conclusion and Future Prospects

EIP 7702 represents a pivotal step in Ethereum’s journey toward account abstraction. By enabling smart contract capabilities within EOAs, it opens doors for innovative applications, streamlined user experiences, and broader adoption of decentralized finance.

As the Ethereum community experiments with this proposal on rolling test networks, collaboration among wallet developers, application creators, and users will shape its final form. Early 2025 marks the anticipated rollout of EIP 7702, bringing Ethereum closer to its vision of a unified, flexible blockchain ecosystem.

### Can we wait for them to add full AA to Ethereum

Full native AA will hit L1:

- After it has been tested in production
- After this roadmap is complexte
- After there is a consensus among core devs

Such things take yeaesar

## Foundry

Foundry already includes several command to craft and sign EIP-7702 transaction

- Get the contract address associated with an EOA address, 0x if no contract associated

```bash
cast code
```

Reference: [book.getfoundry - cast/code](https://book.getfoundry.sh/reference/cli/cast/code)

- sign an EIP-7702  authorization

```bash
cast wallet sign-auth [OPTIONS] <ADDRESS>
```

With private key indicated

```bash
SIGNED_AUTH=$(cast wallet sign-auth <delegate contract address> --private-key <private key)
```



See [book.getfoundry.sh - sign-auth](https://book.getfoundry.sh/reference/cli/cast/wallet/sign-auth)

- Send an EIP-7720 transaction

```bash
cast send <address> "<function signature>" "<function argument>" --private-key <private key> --auth <signed auth>
```

Option:

 --auth <AUTH>          EIP-7702 authorization list.                    Can be either a hex-encoded signed authorization or an address.

Reference: [book.getfoundry.sh - cast/send](https://book.getfoundry.sh/reference/cli/cast/send)

## Example



### Simple delegate contract

This example demonstrates how EIP-7702 allows Alice to authorize a smart contract to execute a transaction on her behalf, with Bob sponsoring the gas fees for a seamless experience. 

Here the smart contract code, which delegates calls from the user and executes on their behalf. 

From: [src - SimpleDelegateContract.sol](https://github.com/ithacaxyz/odyssey-examples/blob/main/chapter1/contracts/src/SimpleDelegateContract.sol)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract SimpleDelegateContract {
    struct Call {
        bytes data;
        address to;
        uint256 value;
    }

    event Executed(address indexed to, uint256 value, bytes data);

    function execute(Call[] memory calls) external payable {
        for (uint256 i = 0; i < calls.length; i++) {
            Call memory call = calls[i];
            (bool success,) = call.to.call{value: call.value}(call.data);
            require(success, "Call failed");
            emit Executed(call.to, call.value, call.data);
        }
    }

    receive() external payable {}
}
```

##### Steps

- Configure the private key for tests

```bash
# using anvil dev accounts 
export ALICE_ADDRESS= <address>
export ALICE_PK= <PK>
export BOB_PK= <PK>
```

- Deploy the contract `SimpleDelegateContract`.

```bash
forge create SimpleDelegateContract --private-key <deployer private key>

export SIMPLE_DELEGATE_ADDRESS="<enter-contract-address>"
```

- Alice (delegator) sign an EIP-7702 authorization using its wallets by specifying Bob address, With Foundry, it is possible with the following command: `

```bash
SIGNED_AUTH=$(cast wallet sign-auth $SIMPLE_DELEGATE_ADDRESS --private-key $ALICE_PK)
```

- Bob can now sign and send the transaction to execute calls on on Alice's behalf.

He will pay the gas price.

```bash
cast send $ALICE_ADDRESS "execute((bytes,address,uint256)[])" "[("0x",$(cast az),0)]" --private-key $BOB_PK --auth $SIGNED_AUTH
```

### Delegate an account to a P256 Key

[EIP-7702](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-7702.md) and [EIP-7212](https://github.com/ethereum/RIPs/blob/master/RIPS/rip-7212.md) allow users to delegate control over an EOA to a P256 key. This has large potential for UX improvement as P256 keys are adopted by commonly used protocols like [Apple Secure Enclave](https://support.apple.com/en-au/guide/security/sec59b0b31ff/web) and [WebAuthn](https://webauthn.io/).

Passkeys allows users to authenticate using methods like Touch ID while keeping passwords safe. These keys are generated within secure hardware modules, such as Apple's Secure Enclave or a Trusted Platform Module (TPM), which are isolated from the operating system to protect them from being exposed.

This example demonstrates how the upcoming EIP's EIP-7702 and EIP-7212 (already live in Odyssey's Chapter 1), will enable you to use a passkey to sign an onchain message

https://github.com/ithacaxyz/odyssey-examples/tree/main/chapter1/delegate-p256

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import {Secp256r1} from "./Secp256r1.sol";

/// @notice Contract designed for being delegated to by EOAs to authorize a secp256r1 key to transact on their behalf.
contract P256Delegation {
    /// @notice The x coordinate of the authorized public key
    uint256 authorizedPublicKeyX;
    /// @notice The y coordinate of the authorized public key
    uint256 authorizedPublicKeyY;

    /// @notice Internal nonce used for replay protection, must be tracked and included into prehashed message.
    uint256 public nonce;

    /// @notice Authorizes provided public key to transact on behalf of this account. Only callable by EOA itself.
    function authorize(uint256 publicKeyX, uint256 publicKeyY) public {
        require(msg.sender == address(this));

        authorizedPublicKeyX = publicKeyX;
        authorizedPublicKeyY = publicKeyY;
    }

    /// @notice Main entrypoint for authorized transactions. Accepts transaction parameters (to, data, value) and a secp256r1 signature.
    function transact(address to, bytes memory data, uint256 value, bytes32 r, bytes32 s) public {
        bytes32 digest = keccak256(abi.encode(nonce++, to, data, value));
        require(Secp256r1.verify(digest, r, s, authorizedPublicKeyX, authorizedPublicKeyY), "Invalid signature");

        (bool success,) = to.call{value: value}(data);
        require(success);
    }
}
```

### Step

- Deploy a [P256Delegation](https://github.com/ithacaxyz/odyssey-examples/blob/main/chapter1/contracts/src/P256Delegation.sol) contract, which we will be delegating to

```solidity
forge create P256Delegation --private-key "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

```

- Send an EIP-7702 transaction, which delegates to our newly deployed contract. This transaction will both authorize the delegation and set it to use our P256 public key that we have generated previously:

```bash
export DELEGATE_ADDRESS=<enter-delegate-contract-address>
export PUBKEY_X=<enter-public-key-x>
export PUBKEY_Y=<enter-public-key-y>
cast send 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 'authorize(uint256,uint256)' $PUBKEY_X $PUBKEY_Y --auth $DELEGATE_ADDRESS --private-key <sender private key>
```

- Verify that new code at our EOA account contains the [delegation designation](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-7702.md#delegation-designation), a special opcode prefix to highlight the code has a special purpose:

```bash
$ cast code 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
0xef0100...
```



- Prepare signature to be able to transact on behalf of the EOA account by using the `transact` function of the delegation contract. Let's generate a signature for sending 1 ether to the zero address by using our P256 private key:

```
python p256.py sign $(cast abi-encode 'f(uint256,address,bytes,uint256)' $(cast call 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 'nonce()(uint256)') '0x0000000000000000000000000000000000000000' '0x' '1000000000000000000')
```

- `python p256.py sign` function signs the message with our previously generated p256 key

  ```bash
  cast abi-encode 'f(uint256,address,bytes,uint256)
  ```

  abi-encodes the payload expected by the `P256Delegation contract` with the following fields

  - nonce: `$(cast call 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 'nonce()(uint256)')` is used to fetch the nonce from the EOA to protect against replay attacks
  - address: `0x0000000000000000000000000000000000000000`
  - bytes: `0x`
  - amount: `1000000000000000000` wei (= 1 ETH)

The command output will respond with the signature r and s values.

-  Send the message including signature via the `transact` function of the delegation contract:

```bash
# use dev account
export SENDER_PK=<sender private key>
export SIG_R=<enter-signature-r>
export SIG_S=<enter-signature-s>
cast send 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 'transact(address to,bytes data,uint256 value,bytes32 r,bytes32 s)' '0x0000000000000000000000000000000000000000' '0x' '1000000000000000000' $SIG_R $SIG_S --private-key $SENDER_PK
```

Note that, similarly to [simple-7702 example](https://github.com/ithacaxyz/odyssey-examples/blob/main/chapter1/simple-7702), there is no restriction on who could submit this transaction.

### Note

This example is not secure because: 

- Anyone could send the transaction to any address on Alice's behalf, since there’s no such restriction in the signed authorization. 
- To address this issue, you would need to add additional setup functions which would be called on user's bytecode once delegation has been applied.



https://book.getfoundry.sh/reference/cli/cast/wallet/sign-auth

1) 

https://github.com/ithacaxyz/odyssey-examples/tree/main/chapter1/simple-7702

## Reference

- [EIP-7702: a technical deep dive by lightclient | Devcon SEA](https://www.youtube.com/watch?v=_k5fKlKBWV4)
- [An introduction to EIP-7702 | Jan Gorzny - Zircuit](https://www.youtube.com/watch?v=WG_0EiHtKlc)
- [Deep Dive into Ethereum 7702 Smart Accounts: security risks, footguns and testing](https://www.youtube.com/watch?v=ZFN2bYt9gNE)
  - [EIP7702 Goat](https://github.com/theredguild/7702-goat)