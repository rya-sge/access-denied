# **Threshold Key Management with Blockchain Coordination**

This document describes a system for decentralized key management that combines **threshold cryptography**, **multi-party computation (MPC)**, and a dedicated **blockchain coordination layer**. The goal is to provide secure, scalable, and verifiable cryptographic services to a wide range of environments, including **Fully Homomorphic EVMs (FH-EVMs)**, standard EVMs, Web2 applications, and enterprise systems.

------

## 1. Introduction

In distributed systems, cryptographic keys are a foundational trust element. A compromise of a single key holder can lead to a complete system breach. **Threshold cryptography** addresses this by splitting a private key into multiple *shares* held by independent servers. Only when a predefined subset of these servers collaborate can the key be used, and at no point is the complete key reconstructed in one place.

In this architecture:

- Keys are never stored or transmitted in full.
- All cryptographic operations are performed using **secure multi-party computation (MPC)**.
- The coordination of MPC servers, payment handling, and policy enforcement is managed by a dedicated blockchain, referred to here as the **Threshold KMS (tKMS) blockchain**.

------

## 2. Architectural Overview

The system consists of four primary components:

1. **tKMS Blockchain** – A dedicated ledger that maintains MPC server state, application configurations, and event logs.
2. **MPC Servers** – Independent nodes, each holding a share of a private key and running inside secure execution environments (e.g., AWS Nitro Enclaves).
3. **Gateways** – Untrusted relays that pass signed, verifiable messages between the tKMS blockchain and external chains or applications.
4. **Application Contracts** – Smart contracts deployed on the tKMS blockchain to manage specific integrations.

### 2.1 Why a Dedicated Blockchain?

Using a blockchain for coordination provides:

- **Immutable auditability** – Every request, server change, and key operation is recorded.
- **Incentive mechanisms** – Payments to MPC servers can be automated via on-chain transactions.
- **Governance** – A DAO or on-chain voting mechanism can adjust parameters such as threshold size, server set, or fees.
- **Multi-chain interoperability** – A single tKMS blockchain can service many independent systems without duplicating infrastructure.

------

## 3. Threshold MPC Operations

In threshold MPC, a secret (such as a private key) is divided into *n* shares, with a threshold *t* such that any *t* or more shares can perform cryptographic operations, but fewer than *t* shares reveal nothing.

In this system:

- **Key generation**: All MPC servers jointly generate shares without any party seeing the full key.
- **Decryption/signing**: Requests are sent to all servers. Each produces a *partial result*, which is combined into the final output.
- **Key refresh**: Shares can be re-randomized without changing the public key, mitigating long-term exposure risk.

------

## 4. Cross-Chain Communication

Many deployments require the tKMS to serve clients on different blockchains or execution environments.

### 4.1 FH-EVM → tKMS Blockchain

- FH-EVM maintains an **access control list (ACL)** as a Merkle tree of ciphertext permissions.
- The Merkle root is stored in FH-EVM block headers.
- The root is communicated to the tKMS blockchain at setup, enabling verification of access requests.

### 4.2 tKMS Blockchain → FH-EVM

- FH-EVM needs to know the MPC server set only once at initialization.
- Subsequent requests are validated by checking MPC signatures.
- Updates to the server set are broadcast via the tKMS blockchain and relayed by Gateways.

------

## 5. Execution Flow

1. An external chain or application sends a cryptographic request through a Gateway.
2. The Gateway submits the request to an **application contract** on the tKMS blockchain.
3. The contract logs the request and triggers the MPC process.
4. Each MPC server processes the request inside its secure enclave and produces a partial result.
5. Partial results are combined and recorded on the tKMS blockchain.
6. The result is relayed back to the requesting system via a Gateway.

This design ensures that:

- No single Gateway is trusted (security is based on signature verification).
- Requests and responses are fully auditable on-chain.
- Cross-chain interactions do not require trust in off-chain actors.

------

## 6. Security Model

The system guarantees:

- **Secrecy** – No single party can reconstruct the full key.
- **Correctness** – Results are verifiable using public cryptographic proofs.
- **Reliability** – The system remains functional unless the threshold of MPC servers or tKMS blockchain validators is compromised.
- **Resilience** – Gateway failure does not compromise security; it only affects availability.

Additional measures:

- **Malformed ciphertext prevention** – Using zero-knowledge proofs to verify ciphertext validity before decryption.
- **Selective failure prevention** – Ensuring an attacker cannot cause repeated decryption errors to leak partial key information.
- **Key refresh protocol** – Mitigates risks from long-term key share exposure.

------

## 7. Performance

The tKMS blockchain uses **CometBFT** consensus, achieving ~1 second finality.
 Two configurations have been benchmarked:

- **T1 (single-server)**: Maximum performance for low-security, centralized use.
- **T4 (threshold with 4 MPC servers)**: Supports 1-corrupt tolerance with minimal additional latency.

Due to the low-latency blockchain layer, thresholding introduces only a small delay compared to centralized processing.

------

## 8. Deployment Models

Three main deployment strategies are supported:

1. **Fully hosted** – Operated as a managed service.
2. **Self-managed** – Organizations run their own MPC servers and blockchain validators.
3. **Open-source** – Community-operated, with publicly verifiable code and protocols.

Each deployment can integrate with existing L1/L2 blockchains, enterprise applications, or hybrid Web2/Web3 systems.

------

## 9. Current Status

**Implemented**:

- Core MPC protocols and cryptographic primitives
- Secure enclave integration
- tKMS blockchain and consensus
- Gateway protocol and cross-chain message verification

**In progress**:

- Horizontal scaling
- S3 integration for temporary storage
- Four-party MPC deployment

**Planned**:

- Refresh protocol integration
- Internal and external audits
- Full open-source release with documentation and white paper

------

## 10. Conclusion

This architecture combines threshold cryptography, MPC, and blockchain-based coordination to deliver a secure, auditable, and scalable key management framework. By separating trust among multiple servers and using an immutable ledger for coordination, it addresses both the **security risks of key centralization** and the **operational complexity of multi-environment integrations**.

The result is a cryptographic service layer that can operate indefinitely, adapt to changing participants, and support diverse applications—from blockchain smart contracts to enterprise encryption services—while maintaining strong guarantees of secrecy, correctness, and reliability.

## Reference

https://www.zama.ai/post/introducing-zama-threshold-key-management-system-tkms

https://docs.zama.ai/protocol/zama-protocol-litepaper