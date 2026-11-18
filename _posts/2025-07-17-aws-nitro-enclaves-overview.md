---
layout: post
title: "AWS Nitro Enclaves: Secure and Isolated Compute for Sensitive Data"
date: 2025-07-17
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: security
tags: amazon enclave nitro secure-environement
description: "AWS Nitro Enclaves, an Amazon EC2 feature that creates isolated virtual machines for sensitive data: architecture, attestation, KMS and supported instances."
image: /assets/article/virtualization/amazon/nitro_enclaves_eks.png
isMath: false
---

Cloud workloads are routinely encrypted at rest and in transit, but data being processed sits in the clear in the memory of the instance handling it. 

**AWS Nitro Enclaves**, a feature of Amazon EC2,  aims to offer highly isolated and secure execution environments. These enclaves provide a trusted runtime for workloads such as cryptographic operations, personally identifiable information (PII) processing, and sensitive machine learning inference.

[TOC]

## What you need to know first

The overview below assumes a few virtualization and cloud-security concepts that it uses without explaining.

- **Virtual machines and hypervisors**: a hypervisor divides a physical host's CPUs and memory between virtual machines and keeps each one from reading the others' memory. A Nitro Enclave is such a virtual machine, carved out of the vCPUs and memory of its parent EC2 instance.
- **Trusted execution environments**: a trusted execution environment (TEE) runs code in an area that the rest of the system, including its administrators, cannot inspect or modify. Nitro Enclaves are AWS's VM-based form of a TEE, and the site's article on the [Zama KMS]({{site.url_complet}}/2026/09/18/zama-kms-threshold-key-management-architecture-and-operation/) shows one deployed in production.
- **Measurements**: a measurement is a cryptographic hash of a piece of code or configuration taken before it runs. An enclave's PCRs hold such hashes, so a verifier can compare them with the values it expects; PCR0, for instance, is the hash of the enclave image file.
- **Remote attestation**: in remote attestation, a component outside the TEE receives a document signed by the platform that lists the measurements, checks the signature up to a trusted root, and only then trusts the code. An enclave can also place a public key in its attestation document so that the reply is encrypted to the enclave alone.
- **AWS KMS key policies**: AWS Key Management Service keeps keys inside the service and decides who may use them through key policies and IAM permissions. Those policies can carry conditions on attestation values, which is how a key is released only to an enclave whose measurements match.
- **Kubernetes device plugins and EKS nodes**: a device plugin advertises a node's special hardware to the kubelet so that pods can request it as a resource. On Amazon EKS, the nodes are EC2 instances started from a launch template, which is where enclave support has to be switched on.

------

## What Are AWS Nitro Enclaves?

**Nitro Enclaves** are isolated, hardened virtual machines created from a **parent EC2 instance**. These environments are completely cut off from the network and inaccessible via SSH or other external interfaces. They have:

- **No persistent storage**
- **No external network connectivity**
- **No interactive access (not even for root users)**

The purpose of Nitro Enclaves is to **protect data in use**, the third state alongside data at rest and data in transit. By running applications in a trusted and isolated environment, Nitro Enclaves reduce the attack surface and guard against both external threats and insider risks.

Reference: [AWS - What is Nitro Enclaves?](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html)

------

## Key Architectural Components

Nitro Enclaves are built on the **AWS Nitro System**, the combination of dedicated hardware (Nitro Cards, Nitro Security Chip) and the lightweight Nitro Hypervisor on which modern EC2 instances run. An enclave uses the same Nitro Hypervisor that isolates EC2 instances from one another to isolate its vCPUs and memory from the parent instance. Here's how the architecture works:

### Parent Instance

A Nitro-based EC2 instance that hosts the enclave. It allocates dedicated vCPUs and memory for the enclave and is the only entity allowed to communicate with it—via a secure local channel called **vsock**.

Reference: [Nitro Enclaves concepts - Parent instance](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave-concepts.html#term-parent)

### Enclave

The enclave is a separate VM with its own kernel, vCPUs, and memory. It is launched using an **Enclave Image File (.eif)**, which contains the OS, libraries, and enclave application. Once created, the enclave is isolated from both the parent instance and the external world.

### Vsock (Virtual Socket)

Since there’s no network access, **vsock** serves as the only communication channel between the parent instance and its enclaves. It allows local inter-process communication in a secure and controlled way.

### Nitro CLI & SDK

- **Nitro CLI**: Command-line interface used to create, manage, and terminate enclaves.
- **Nitro Enclaves SDK**: A developer toolkit to write enclave-aware applications and interact with services like **AWS KMS** using **attestation**.

------

## Security Features

### Cryptographic Attestation

A core security capability of Nitro Enclaves is **cryptographic attestation**, which allows an enclave to prove its identity and integrity. This is achieved via:

- **Attestation Document**: Generated by the Nitro Hypervisor, containing measurements like Platform Configuration Registers (PCRs) and other metadata.
- **PCRs**: Cryptographic hashes that verify the enclave’s code and environment haven’t changed.

This attestation process is trusted by services like **AWS Key Management Service (KMS)**, enabling key access only when the enclave matches an approved configuration.

See [Cryptographic attestation](https://docs.aws.amazon.com/enclaves/latest/user/set-up-attestation.html).

###  KMS Integration (KMS proxy)

Nitro Enclaves integrate natively with **AWS KMS** to perform cryptographic operations (like key decryption or generation) **only** if the enclave passes attestation. 

The **KMS proxy**, running on the parent instance, securely proxies requests from the enclave to KMS.

See [KMS proxy - Nitro Enclaves concepts](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave-concepts.html#term-proxy)

------

## Supported EC2 Instance Types

Nitro Enclaves are **processor-agnostic** and work on most **Intel, AMD, and AWS Graviton-based EC2 instances** built on the Nitro System.

### Requirements

- **Intel/AMD**: At least **4 vCPUs**
- **Graviton**: At least **2 vCPUs**
- **Linux-only** enclaves, although the parent instance can run Linux or Windows

Only the instance families listed in the AWS user guide are supported, without the smallest size and most `.metal` sizes of each family. Burstable types such as `t3`, some accelerated types such as `g5g` and the High Memory `u-*` instances are not supported at all. Also, Nitro Enclaves are not supported on **Outposts**, **Local Zones**, or **Wavelength Zones**.

------

## Properties

Here is the propreties of Nitro Enclaves

| Limitation                  | Description                                                  |
| --------------------------- | ------------------------------------------------------------ |
| No persistent storage       | Enclaves are ephemeral and lose all state after termination. |
| No network access           | They can’t access AWS services directly; all communication must go through the parent instance. |
| No debugging/SSH            | Users cannot SSH into an enclave, and the data and applications inside the enclave cannot be accessed by the processes |
| Numbers of enclaves by host | Up to **four enclaves per instance**, and enclaves cannot talk to each other—even on the same host. |
| Parent instance dependency  | Enclave lifecycle is tied to the parent instance. If it stops, the enclave terminates. |
| Enclave OS restriction      | Enclaves support **Linux only**.                             |



------

## Use Cases

AWS Nitro Enclaves are ideal for workloads requiring **confidential computing** or **privacy-preserving operations**, including:

- **Processing and anonymizing PII and PHI**
- **Securing machine learning model inference**
- **Digital rights management**
- **Cryptographic signing and key management**
- **Regulated financial or healthcare applications**

------

## Related AWS Services

Nitro Enclaves integrate with several AWS services:

- **AWS Key Management Service (KMS)** – for secure cryptographic operations tied to attestation.
- **AWS Certificate Manager (ACM)** – for SSL/TLS certificate provisioning and management for applications running inside enclaves.

## Using Nitro enclaves with Amazon EKS

Amazon EKS can be used to **deploy, scale, and orchestrate Nitro Enclaves** from Kubernetes pods. By installing the **Nitro Enclaves Kubernetes device plugin** on EC2 instances (EKS nodes), pods on that node gain the ability to **create and manage enclaves** using the Nitro Enclaves CLI.

### Key Components:

- **Launch Template**: Must be enclave-enabled and include specific user data to configure enclave support. Used to create the enclave-enabled EKS nodes.
- **Kubernetes Device Plugin**: Enables pods to interact with enclaves. Compatible with both EKS-managed and self-managed Kubernetes nodes.

> **Note**: All pods on the same enclave-enabled node can communicate with the enclave on that node.

This setup allows Kubernetes users to integrate Nitro Enclaves into containerized workloads, enhancing data security for sensitive operations.

![nitro_enclaves_eks]({{site.url_complet}}/assets/article/virtualization/amazon/nitro_enclaves_eks.png)

Image reference: [docs.aws.amazon.com - kubernetes.html](https://docs.aws.amazon.com/enclaves/latest/user/kubernetes.html)



Reference: [docs.aws.amazon.com - Using Nitro Enclaves with Amazon EKS](https://docs.aws.amazon.com/enclaves/latest/user/kubernetes.html)



------

## Pricing

There is **no additional cost** to use Nitro Enclaves. You only pay for the **EC2 instance** and any other AWS services you use, such as KMS.

See [What is Nitro Enclaves? - pricing](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html#nitro-enclave-pricing)

------

## Conclusion

**AWS Nitro Enclaves** offer a hardware-based solution for isolating and processing sensitive data, designed to meet security and compliance requirements in cloud environments. Through features such as **enclave isolation**, **cryptographic attestation**, and **integration with AWS services like KMS**, Nitro Enclaves enable the development of applications that require secure data handling.

For workloads that involve confidential data and demand strong security boundaries, Nitro Enclaves can be a suitable option within an overall cloud security strategy.

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Data in use** | Data being processed in memory, the third state alongside data at rest and data in transit, which Nitro Enclaves aim to protect. |
| **AWS Nitro System** | The AWS virtualization platform that EC2 runs on and on which Nitro Enclaves are built, providing hardware-level isolation. |
| **Nitro Enclave** | An isolated, hardened virtual machine with its own kernel, vCPUs and memory, created from a parent EC2 instance and with no persistent storage, network access or interactive access. |
| **Parent instance** | The Nitro-based EC2 instance that allocates vCPUs and memory to an enclave, is the only entity that can talk to it, and whose lifecycle the enclave follows. |
| **Enclave Image File (EIF)** | The `.eif` file from which an enclave is launched, containing its operating system, libraries and application. |
| **vsock** | The local virtual socket that is the only communication channel between the parent instance and its enclaves. |
| **Nitro CLI** | The command-line tool used to create, manage and terminate enclaves. |
| **Nitro Enclaves SDK** | The developer toolkit for writing enclave-aware applications and calling services such as AWS KMS with attestation. |
| **Cryptographic attestation** | The process by which an enclave proves its identity and integrity to another party, such as KMS, using an attestation document. |
| **Attestation document** | A document generated by the Nitro Hypervisor that contains the enclave's measurements, including its PCRs, and other metadata. |
| **Platform Configuration Register (PCR)** | A cryptographic hash in the attestation document that lets a verifier check that the enclave's code and environment have not changed. |
| **AWS Key Management Service (KMS)** | The AWS service that performs key operations such as decryption or key generation for an enclave only when its attestation matches an approved configuration. |
| **KMS proxy** | A component on the parent instance that forwards the enclave's requests to KMS, since the enclave has no network access of its own. |
| **Nitro Enclaves Kubernetes device plugin** | The plugin installed on enclave-enabled EKS nodes that lets pods on that node create and manage enclaves. |
| **Confidential computing** | Processing sensitive data in an isolated, attested environment so that it stays protected while in use, the class of workloads Nitro Enclaves target. |

## Reference

- [docs.aws.amazon.com - What is Nitro Enclaves?](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html)
- [aws.amazon.com - AWS Nitro System](https://aws.amazon.com/ec2/nitro/)
- ChatGPT to summarize the documentation

### Related articles

- [Zama FHEVM Architecture — Components, Data Flow and What Has to Be Trusted]({{site.url_complet}}/2026/09/18/zama-fhevm-architecture-components-trust-model/)
- [Inside the Zama KMS — Threshold Key Management for FHE, From MPC Protocol to Enclave Deployment]({{site.url_complet}}/2026/09/18/zama-kms-threshold-key-management-architecture-and-operation/)
