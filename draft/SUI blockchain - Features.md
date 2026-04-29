# SUI blockchain - Features

## DeepBookV3

DeepBookV3 is a next-generation decentralized central limit order book (CLOB) built on Sui. DeepBookV3 leverages Sui's parallel execution and low transaction fees to bring a highly performant, low-latency exchange on chain.

The latest version delivers new features including flash loans, governance, improved account abstraction, and enhancements to the existing matching engine. This version also introduces its own tokenomics with the [DEEP token](https://suiscan.xyz/mainnet/coin/0xdeeb7a4662eec9f2f3def03fb937a663dddaa2e215b8078a284d026b7946c270::deep::DEEP/txs), which you can stake for additional benefits.

DeepBookV3 does not include an end-user interface for token trading. Rather, it offers built-in trading functionality that can support token trades from decentralized exchanges, wallets, or other apps. The available SDK abstracts away a lot of the complexities of interacting with the chain and building programmable transaction blocks, lowering the barrier of entry for active market making.

[docs.sui.io/standards/deepbook](https://docs.sui.io/standards/deepbook)

## Nautilus

Nautilus is a framework for secure and verifiable off-chain computation on Sui. It enables builders to delegate sensitive or resource-intensive tasks to a self-managed [trusted execution environment (TEE)](https://en.wikipedia.org/wiki/Trusted_execution_environment) while preserving trust on chain through smart contract-based verification.

Nautilus supports hybrid decentralized applications (dApps) that require:

- Private data handling
- Complex computations
- Integration with external (Web2) systems

The framework ensures computations are tamper-resistant, isolated, and cryptographically verifiable.

It currently supports self-managed [AWS Nitro Enclave TEEs](https://aws.amazon.com/ec2/nitro/nitro-enclaves/). Developers can verify AWS-signed enclave attestations on chain using Sui smart contracts written in Move. Refer to the [Github repo](https://github.com/MystenLabs/nautilus) for the reproducible build template.

[docs.sui.io/concepts/cryptography/nautilus](https://docs.sui.io/concepts/cryptography/nautilus)

## SUI Kiosk

Kiosk is a decentralized system for commerce applications on Sui. It consists of `Kiosk` objects - shared objects owned by individual parties that store assets and allow listing them for sale as well as utilize custom trading functionality - for example, an auction. While being highly decentralized, Sui Kiosk provides a set of strong guarantees:

- Kiosk owners retain ownership of their assets to the moment of purchase.
- Creators set custom policies - sets of rules applied to every trade (such as pay royalty fee or do some arbitrary action X).
- Marketplaces can index events the `Kiosk` object emits and subscribe to a single feed for on-chain asset trading.

Practically, Kiosk is a part of the Sui framework, and it is native to the system and available to everyone out of the box.

[https://docs.sui.io/standards/kiosk](https://docs.sui.io/standards/kiosk)

## Passkey

Passkey provides a secure and user-friendly alternative for submitting transactions to Sui. Built on the **WebAuthn standard**, passkey lets users authenticate and sign transactions using:

- Hardware security keys, such as YubiKeys
- Mobile devices, such as smartphones and tablets
- Platform-based authenticators, such as Face ID and Touch ID

Passkey simplifies authentication by removing the need to manage seed phrases or private keys manually. Instead, it relies on device-based authentication and cloud synchronization, allowing seamless, phishing-resistant access across multiple devices. You can also use passkey in a [multisig setup](https://docs.sui.io/concepts/cryptography/transaction-auth/multisig), which provides more flexibility to build secure and recoverable wallet experiences.

By supporting the passkey signature scheme, Sui improves security and accessibility, making it easier for users to manage their accounts with hardened security. Passkey-based wallets are tied to the origin, meaning they cannot be phished or used on a different site. This makes passkey a more secure authentication option.

[https://docs.sui.io/concepts/cryptography/passkeys](https://docs.sui.io/concepts/cryptography/passkeys)

## zkLogin

zkLogin is a Sui primitive that lets you send transactions from a Sui address using an OAuth credential, without publicly linking the two.

zkLogin is designed with the following goals:

- **Streamlined onboarding:** zkLogin enables you to transact on Sui using the familiar OAuth login flow, removing the need to handle cryptographic keys or remember mnemonics.
- **Self-custody:** A zkLogin transaction requires user approval via the standard OAuth login process. The OAuth provider cannot transact on the user’s behalf.
- **Security:** zkLogin is a two-factor authentication scheme. Sending a transaction requires both a credential from a recent OAuth login and a salt not managed by the OAuth provider. An attacker who compromises an OAuth account cannot transact from the user’s Sui address unless they also compromise the salt.
- **Privacy:** Zero-knowledge proofs prevent third parties from linking a Sui address with its corresponding OAuth identifier.
- **Optional verified identity:** A user can opt in to verify the OAuth identifier used to derive a particular Sui address. This creates the foundation for a verifiable on-chain identity layer.
- **Accessibility:** zkLogin is one of several native Sui signature schemes thanks to [Sui’s cryptography agility](https://docs.sui.io/concepts/cryptography/transaction-auth/signatures). It integrates with other Sui primitives, such as sponsored transactions and multisig.
- **Rigor:** The code for zkLogin has been independently [audited](https://github.com/sui-foundation/security-audits/blob/main/docs/zksecurity_zklogin-circuits.pdf) by two firms specializing in zero knowledge. The public zkLogin ceremony for creating the common reference string included contributions from more than 100 participants.

[zklogin](https://docs.sui.io/concepts/cryptography/zklogin)