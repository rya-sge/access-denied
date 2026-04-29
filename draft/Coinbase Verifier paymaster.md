## Coinbase Verifier paymaster

### Introduction

VerifyingPaymaster is an ERC4337-compatible paymaster contract that accepts a signature for validation and can perform optional prechecks and ERC20 token transfers. It supports the option to restrict sponsorship to certain bundlers.

- This paymaster implementation is designed to work with EntryPoint v0.7 and provides flexibility in handling user operations, including sponsorship and token-based fee payments.
- This contract is used as the Coinbase Developer Platform Paymaster for standard sponsorships.

### Features

- Implements `validatePaymasterUserOp` and `postOp` methods as per the EIP-4337 specification
- Supports allowlisting of bundlers to mitigate certain attack vectors
- Handles ERC20 token payments with prechecks to prevent griefing
- Supports auxiliary fund sources (e.g., Coinbase Magic Spend)
- Implements a two-step ownership transfer process
- Allows for verifying signer rotation with a two-step proce

### Important Notes

- An off-chain signer is responsible for signing UserOps
- Implementers should carefully consider the security implications and potential attack vectors
- The contract supports both native gas sponsorship and ERC20 token payments
- Bundler allowlisting can be enabled/disabled per UserOp

## Contract Details



- The contract inherits from `BasePaymaster` and `Ownable2Step`
- Uses OpenZeppelin's ECDSA for signature verification
- Supports setting validity periods for signatures
- Implements flexible options for token payments, including balance prechecks and prepaymen

https://github.com/coinbase/verifying-paymaster/blob/master/src/VerifyingPaymaster.sol

https://github.com/coinbase/verifying-paymaster/tree/master/docs

