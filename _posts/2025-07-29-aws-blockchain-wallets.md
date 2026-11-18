---
layout: post
title: "Blockchain wallets on AWS with Fireblocks and Circle"
date: 2025-07-29
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: security cryptography wallet
tags: amazon enclave nitro secure-environement fireblocks circle wallet
description: Deep dive into blockchain wallets with Circle and Fireblocks and explore how they use AWS services such as AWS Nitro Enclave
image: /assets/article/virtualization/amazon/circle-amazon.png
isMath: false
---

This article explores how to build wallet solutions using AWS procucts.

AWS Nitro Enclaves enables confidential computing for secure key management in blockchain applications. It covers how **Circle** uses AWS for USDC, Programmable Wallets and its financial services, and how **Fireblocks** uses Nitro Enclaves in its multi-party computation (MPC) wallet infrastructure. 

This article is a summary of the following video [AWS re:Invent 2024 - Blockchain wallets on AWS: Secure, smart, and scalable](https://www.youtube.com/watch?v=hKZtadwZgw8) made with [NoteGPT](https://notegpt.io) and with a few annotation by me.

[TOC]

## What you need to know first

The article summarises a talk on wallet infrastructure and relies on a few security and wallet concepts that it names without explaining.

- **Hardware Security Module (HSM)**: a tamper-resistant device that generates and stores cryptographic keys and performs signing inside the hardware, so the private key is not exported in clear. The article uses AWS CloudHSM as the base of a cold wallet; see [PCI PTS HSM v4.0 — How Payment Hardware Security Modules Are Evaluated]({{site.url_complet}}/2026/07/20/pci-pts-hsm-security-requirements-v4/) for how such devices are evaluated.
- **Hot and cold wallets**: a hot wallet keeps its signing key reachable by an online service so it can sign transactions automatically, while a cold wallet keeps the key in an environment with no network access. The article maps the first to Lambda and KMS and the second to CloudHSM; [Crypto Wallets Explained - Types, Risks, and How to select it]({{site.url_complet}}/2024/10/08/crypto-wallet-introduction/) covers the distinction.
- **Confidential computing**: protecting data while it is being processed, not only at rest or in transit, by running the code in an isolated environment that the host operator cannot inspect. Nitro Enclaves are AWS's offer in this category; see [AWS Nitro Enclaves: Secure and Isolated Compute for Sensitive Data]({{site.url_complet}}/2025/07/17/aws-nitro-enclaves-overview/).
- **Attestation**: a signed statement produced by the isolated environment that describes the code it runs, which a remote party checks before trusting it. In the Fireblocks co-signer, KMS releases the decryption key only to an enclave whose attestation matches the expected code.
- **Multi-party computation (MPC) signing**: several parties each hold a share of a key and run a protocol that produces a valid signature without ever reconstructing the full key in one place. Circle and Fireblocks both rely on it; see [Overview, security and applications of Multi-Party Computation (MPC)]({{site.url_complet}}/2024/10/21/mpc-protocol-overview/).
- **Smart contract accounts and ERC-4337**: an account whose rules are code rather than a single private key, with ERC-4337 routing its operations through an `EntryPoint` contract instead of the protocol itself. The ERC-6900 modular wallets mentioned for Circle build on this model; see [ERC-4337: Account Abstraction Using Alt Mempool]({{site.url_complet}}/2025/05/02/erc-4337-overview/).




## Building Blocks of Blockchain Wallets

Developing blockchain wallets demands a secure and scalable architecture. Key components include:

- **Key Management**: Using [AWS Key Management Service (KMS)](https://aws.amazon.com/kms/), [CloudHSM](https://aws.amazon.com/cloudhsm/), or Secrets Manager for secure key handling.
  - `AWS CloudHSM` lets you manage and access your keys on FIPS-validated hardware, protected with customer-owned, single-tenant HSM instances that run in your own Virtual Private Cloud (VPC).
  - `AWS KMS` allows you to create and control keys used to encrypt or digitally sign your data

- **Access Management**: Employing AWS Identity and Access Management (IAM) and CloudTrail for auditing.
- **Compute Layer**: Efficient computation using AWS Lambda, EC2, or Nitro Enclaves.
- **Monitoring and Logging**: Implementing [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) for operational insights.
  - `CloudWatch` is a service that monitors applications, responds to performance changes, optimizes resource use, and provides insights into operational health.

- **Low Latency Access**: Using AWS cluster placement groups for performance-critical use cases.

---

## Amazon product

### AWS Lambda

[Website](https://aws.amazon.com/lambda/)

Run code without thinking about servers or clusters

AWS Lambda is a compute service that runs your code in response to events and automatically manages the compute resources, making it the fastest way to turn an idea into a modern, production, serverless applications.

see also [stackoverflow - Is it possible to keep an AWS Lambda function warm?](https://stackoverflow.com/questions/42877521/is-it-possible-to-keep-an-aws-lambda-function-warm)

### AWS Nitro Enclaves

[Website](https://aws.amazon.com/ec2/nitro/nitro-enclaves/)

Create additional isolation to further protect highly sensitive data within EC2 instances

AWS Nitro Enclaves enables customers to create isolated compute environments to further protect and securely process highly sensitive data such as personally identifiable information (PII), healthcare, financial, and intellectual property data within their Amazon EC2 instances. Nitro Enclaves uses the same Nitro Hypervisor technology that provides CPU and memory isolation for EC2 instances.

Nitro Enclaves helps customers reduce the attack surface area for their most sensitive data processing applications. Enclaves offers an isolated, hardened, and highly constrained environment to host security-critical applications. Nitro Enclaves includes cryptographic attestation for your software, so that you can be sure that only authorized code is running, as well as integration with the AWS Key Management Service, so that only your enclaves can access sensitive material.

There are no additional charges for using AWS Nitro Enclaves other than the use of Amazon EC2 instances and any other AWS services that are used with Nitro Enclaves.

See also my article [AWS Nitro Enclaves: Secure and Isolated Compute for Sensitive Data](https://rya-sge.github.io/access-denied/2025/07/17/aws-nitro-enclaves-overview/)

#### AWS Nitro Enclaves for Blockchain Workloads

AWS Nitro Enclaves enhance security and isolation for blockchain applications. These lightweight, constrained virtual machines operate independently within an EC2 instance, ensuring:

- **Data Protection**: No external networking or administrator access.
- **Isolation**: Enclaves are entirely separate from the parent instance.
- **Ephemeral Storage**: All data exists only in memory and disappears with the enclave.

Nitro Enclaves support cryptographic attestation, allowing enclaves to verify their integrity and state. This integrates with KMS policies, so only trusted applications access sensitive keys.

### Implementing Blockchain Wallets on AWS

1. **Hot Wallets**
   Hot wallets can be implemented with `AWS Lambda` and `KMS` for serverless operation. Transactions are processed via API Gateway, with KMS providing signature services.
2. **Cold Wallets (AWS CloudHSM)**
   Cold wallets utilize `AWS CloudHSM` within a private subnet, which has no route to the internet. The HSM is still online inside the VPC: clients reach it over the network through an elastic network interface, so this design isolates the key on the network rather than keeping it offline (air-gapped). These wallets are highly secure and suited for institutional custody solutions.

---

## Advanced Wallet Solutions by Circle

Circle offers  programmable wallets built on its blockchain infrastructure. Their solutions cater to developers with varying expertise, from crypto-native to Web2 developers unfamiliar with blockchain intricacies. Key offerings include:

- **Developer-Controlled Wallets**: Provide full control over transactions and keys.
- **MPC Wallets**: Employ multi-party computation for secure, customizable user experiences.
- **Modular Wallets**: Allow extensibility with standards like [ERC-6900](https://eips.ethereum.org/EIPS/eip-6900) for tailored functionality.
  - ERC-6900 standardizes smart contract accounts and account modules, which are smart contracts that allow for composable logic within smart contract accounts. A modular account handles two kinds of calls: either from the `EntryPoint` through ERC-4337, or through direct calls from externally owned accounts (EOAs) and other smart contracts. 


Circle’s architecture integrates AWS KMS and MPC servers for robust key management and transaction reconciliation. Developers can also run their MPC nodes, offering flexibility and control.



![circle-amazon]({{site.url_complet}}/assets/article/virtualization/amazon/circle-amazon.png)

## Fireblocks and Nitro Enclaves for Institutional Blockchain Infrastructure

Fireblocks provide blockchain infrastructure and wallet services to institutional clients like Bank of New York Mellon and ANZ. Handling those volumes is where **Nitro Enclaves** and confidential computing are used.

### Details

Fireblocks supports Amazon Web Services (AWS) Nitro Enclaves. Fireblocks customers building products on AWS can utilize Nitro Enclaves to run their Fireblocks API Co-Signer.

Fireblocks employs an API Co-Signer to hold customers’ `MPC signing key shares` and configuration keys. The key shares are used to participate in the MPC signing of a digital asset transaction, while the configuration keys are used to approve modifications to the Fireblocks Workspace.

Fireblocks customers can choose to utilize an `AWS Nitro Enclave` for their API Co-Signer. This requires a customer to follow a deployment process. 

- Fireblocks employs `MPC algorithms` to generate and distribute private key shards, ensuring that a complete and whole private key never exists in any single location. 
  - See also my article [Overview, security and applications of Multi-Party Computation (MPC)](https://rya-sge.github.io/access-denied/2024/10/21/mpc-protocol-overview/)
- The key shards are stored on Fireblocks’ servers, called co-signers, and on the customer’s mobile device or co-signer server, which runs on-premises or in a public cloud. Together they sign transactions in a trustless manner. 
- This ensures that no single party, including Fireblocks, can be a point of failure.

To enhance security, all operations involving these shards are performed within secure environments, such as AWS Nitro Enclaves, ensuring that sensitive data is never exposed nor manipulated, whether in storage or in use.

![FB-AWS-Nitro]({{site.url_complet}}/assets/article/virtualization/amazon/FB-AWS-Nitro.jpg)

Reference: [Fireblocks - Support for AWS Nitro Enclaves on Fireblocks](https://www.fireblocks.com/blog/support-for-aws-nitro-enclaves-on-fireblocks/)

### Transaction Flow and Security Focus

1. **Transaction Initialization**: Transactions are created via a web UI or API and processed by the policy engine, which enforces user-defined rules.
2. **Serialization and Signing**: Protocol-specific serialization converts the transaction into the correct format before signing with private keys.

The policy engine, serialization and signing all run inside confidential computing environments.

### Multiparty Computation (MPC) and Key Security

- MPC ensures no single point of failure by splitting keys into logical shards managed by multiple co-signers.
- Key shards are distributed among Fireblocks’ co-signers and a customer-hosted co-signer, eliminating the risk of key theft from a single location.

### Co-Signer Architecture

1. **Setup**: Customers configure S3 buckets, Nitro-enabled EC2 instances, and AWS KMS keys.
2. **Encrypted Database (KMS keys)**: Key shards stored in S3 are encrypted using KMS keys.
3. **Attestation and Decryption**: The enclave verifies its integrity via KMS attestation before decrypting the database.
4. **Signing Transactions**: The co-signer fetches transactions, participates in MPC communications, and signs securely.



----

### Conclusion

A blockchain wallet holds the keys that move funds, so its implementation is where the security of the whole application concentrates. 

The AWS services covered here, Nitro Enclaves in particular, give a framework for building wallets that keep signing keys isolated even from the operator running them. 

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Hardware Security Module (HSM)** | A tamper-resistant device that stores keys and performs cryptographic operations inside the hardware, the basis of AWS CloudHSM. |
| **AWS KMS** | AWS's managed key service, used to create and control keys that encrypt or sign data, and in the hot-wallet design to provide the signature. |
| **AWS CloudHSM** | Single-tenant, FIPS-validated HSM instances running in the customer's own VPC, used in the article as the base of a cold wallet. |
| **AWS Nitro Enclave** | An isolated, constrained virtual machine inside an EC2 instance, with no external networking, no administrator access and memory-only storage. |
| **Cryptographic attestation** | Proof produced by an enclave about the code it runs, which KMS policies check so that only trusted enclaves can access sensitive keys. |
| **Hot wallet** | A wallet whose key is reachable by an online service, implemented here with Lambda, API Gateway and KMS for serverless signing. |
| **Cold wallet** | A wallet whose key is kept away from internet-facing systems, implemented here with CloudHSM in a private subnet (network isolation, not air-gapped) and suited to institutional custody. |
| **Multi-party computation (MPC)** | A technique where several parties jointly sign with shares of a key, so the complete private key never exists in a single location. |
| **Key share (shard)** | One party's piece of an MPC key, held by Fireblocks' co-signers or by the customer's device or co-signer server. |
| **API Co-Signer** | The Fireblocks component that holds a customer's MPC signing key shares and configuration keys and can run inside a Nitro Enclave. |
| **Policy engine** | The Fireblocks component that enforces user-defined rules on a transaction before it is serialised and signed. |
| **ERC-6900 modular account** | A smart contract account standard with pluggable modules, called either from the ERC-4337 `EntryPoint` or directly by EOAs and other contracts. |

## References

- [AWS CloudHSM cluster architecture](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cluster-architecture.html)

## Related articles

- [Becoming a CASP Under MiCA — Authorisation, Capital and Custody Obligations (Title V)]({{site.url_complet}}/2026/09/17/mica-casp-authorisation-capital-custody/)
- [How Fireblocks Works - MPC Custody, Enclaves, HSMs and Lessons from Real Hacks]({{site.url_complet}}/2026/10/14/how-fireblocks-works-mpc-custody/)
