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



#### Implementation Process

EIP 7702’s workflow begins with an authorization process:

- **Authorization Details**: Users sign an authorization specifying a target code address, chain ID, and nonce for replay protection.
- **Bundler Assistance**: If the user lacks Ether to pay transaction fees, a bundler relays the signed authorization onto the blockchain.
- **Account Initialization**: Once the delegation designator is set, users initialize their smart contract wallet, defining ownership rules and other configurations.

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

The traditional flow of crypto onboarding experience can feel cumbersome: Users have to setup a wallet, back up their mnemonic phrase and make sure to keep it safe. What if there was a simpler and more secure way to manage private keys? Passkeys have already solved this problem by allowing users to authenticate using methods like Touch ID while keeping passwords safe. These keys are generated within secure hardware modules, such as Apple's Secure Enclave or a Trusted Platform Module (TPM), which are isolated from the operating system to protect them from being exposed.

EIP-7212 introduces a precompile for the **secp256r1** elliptic curve, a curve that is widely used in protocols like [Apple Secure Enclave](https://support.apple.com/en-au/guide/security/sec59b0b31ff/web) and [WebAuthn](https://webauthn.io/). 

This example demonstrates how the upcoming EIP's EIP-7702 and EIP-7212 (already live in Odyssey's Chapter 1), will enable you to use a passkey to sign an onchain message, improving the onboarding experience for crypto novices using your Dapp.

https://github.com/ithacaxyz/odyssey-examples/tree/main/chapter1/delegate-p256

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