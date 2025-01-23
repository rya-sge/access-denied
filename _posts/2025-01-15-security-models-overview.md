---
layout: post
title: Main Security Models - Overview
date: 2025-01-15
lang: en
locale: en-GB
categories: security tryhackme
tags: security threat Bell-LaPadula Clark-Wilson Biba tryhackme
description: This article provides a comprehensive overview of three foundational security models: Bell-LaPadula, Biba, and Clark-Wilson.
image: /assets/article/securite/security-model/security-models-bell-lapadula-model.drawio.png
isMath: false
---

This article provides a comprehensive overview of three foundational security models: **Bell-LaPadula**, **Biba**, and **Clark-Wilson**.

 It explains their core principles and applications, focusing on how each model addresses different aspects of security—confidentiality, integrity, and workflow enforcement. 

> Warning: this article is still in draft state and its content is still mainly taken from the documentation. Its content should become more personal later.
>
> This article was made with ChatGPT and the room [Security Principles](https://tryhackme.com/r/room/securityprinciples) by TryHackMe

There are many additional security models if you want to explore more. Examples include:

- Brewer and Nash model
- Goguen-Meseguer model
- Sutherland model
- Graham-Denning model
- Harrison-Ruzzo-Ullman model

[TOC]



------

### Bell-LaPadula Model (Confidentiality)

The Bell-LaPadula (BLP) model focuses on **confidentiality** and controlling access to classified information.

![security-models-bell-lapadula-model.drawio]({{site.url_complet}}/assets/article/securite/security-model/security-models-bell-lapadula-model.drawio.png)

#### Key Principles

1. **Simple Security Property (no read-up, "ss-property"):**

   - A subject (user or process) at a lower security level cannot read data at a higher security level.
   - This prevents unauthorized access to confidential data above the authorized level.

2. ***-Security Property (no write-down):**

   - A subject at a higher security level cannot write data to a lower security level.
   - This ensures sensitive data is not leaked to less secure levels.

3. **Discretionary Security Property:**

   - Access controls can be defined and enforced to limit users' permissions further. 
   - This property uses an access matrix to allow read and write operations. An example access matrix is shown in the table below and used in conjunction with the first two properties.

   | Subjects  | Object A   | Object B  |
   | --------- | ---------- | --------- |
   | Subject 1 | Write      | No access |
   | Subject 2 | Read/Write | Read      |

#### Use Case:

Common in military or government systems where confidentiality and prevention of information leaks are paramount.

#### Conclusion and limitation

The first two properties can be summarized as “write up, read down.” You can share confidential information with people of higher security clearance (write up), and you can receive confidential information from people with lower security clearance (read down).

There are certain limitations to the Bell-LaPadula model. For example, it was not designed to handle file-sharing.

References:

[YouTube - Mike Chapple - CertMike Explains The Bell LaPadula Model](https://www.youtube.com/watch?v=G1FWTfJsK6k)

------

### Biba Integrity Model

The Biba model emphasizes **data integrity**, ensuring that information is not improperly modified.

![security-models-biba-integrity-model.drawio]({{site.url_complet}}/assets/article/securite/security-model/security-models-biba-integrity-model.drawio.png)

#### Key Principles:

**Simple Integrity Property (no read-down):**

This principle prohibits people from reading information below their clearance level.

- A subject cannot read data at a lower integrity level.

- This prevents contamination of high-integrity processes with low-integrity data.
- But why ? This information may be incorrect since it came from a lower level

**Integrity \*-Property (no write-up):**

- A subject cannot write data to a higher integrity level.
- This prevents low-integrity processes from corrupting high-integrity data.

#### Variants

Biba also includes the **low-water-mark principle** and **ring policy** for additional flexibility in enforcing integrity.

#### Use Case

Common in military, financial or healthcare systems where data accuracy and reliability are crucial.

#### Conclusion and limitation

These two properties can be summarized as “read up, write down.” This rule is in contrast with the Bell-LaPadula Model, and this should not be surprising as one is concerned with confidentiality while the other is with integrity.

Biba Model suffers from various limitations. One example is that it does not handle internal threats (insider threat).

#### References

[YouTube - Mike Chapple - CertMike Explains the Biba Integrity Model](https://www.youtube.com/watch?v=nfmwSGtyzV0)

------

### Clark-Wilson Model

The Clark-Wilson model enforces both **data integrity** and **well-formed transactions**, focusing on realistic business environments.

The Clark-Wilson Model also aims to achieve integrity by using the following concepts:

- **Constrained Data Item (CDI)**: This refers to the data type whose integrity we want to preserve.
- **Unconstrained Data Item (UDI)**: This refers to all data types beyond CDI, such as user and system input.
- **Transformation Procedures (TPs)**: These procedures are programmed operations, such as read and write, and should maintain the integrity of CDIs.
- **Integrity Verification Procedures (IVPs)**: These procedures check and ensure the validity of CDIs.

#### Key Principles

1. **Separation of Duties:**

Users are limited to specific roles, ensuring no single individual has unchecked control over sensitive data.

2. **Well-Formed Transactions:**

- Operations must follow specific steps to transition the system from one valid state to another.
- This ensures only authorized changes are made.

3. **Access Triple (Subject, Transformation Procedure, Object):**

- A subject (user) can only access an object (data) through a transformation procedure (authorized application or process).
- This prevents direct, unrestricted access to data.

4. **Auditability:**

Every action is logged to provide traceability and accountability.

#### Use Case

Often used in commercial systems (e.g., banking) to enforce proper workflows, prevent fraud, and ensure compliance with regulations.

------

## Summary Comparison

| **Model**     | **Focus**                      | **Key Rules**                                  | **Use Case**                 |
| ------------- | ------------------------------ | ---------------------------------------------- | ---------------------------- |
| Bell-LaPadula | Confidentiality                | No read-up, no write-down                      | Military/Government systems  |
| Biba          | Integrity                      | No read-down, no write-up                      | Financial/Healthcare systems |
| Clark-Wilson  | Integrity + Business Workflows | Well-formed transactions, separation of duties | Business/Commercial systems  |

Each model addresses different security needs and is tailored to specific types of threats and environments.

### Mindmap

![security-models-mindmap]({{site.url_complet}}/assets/article/securite/security-model/security-models-mindmap.png)

## References

- ChatGPT with the inputs: *Explain these different models: Bell-LaPadula Model The Biba Integrity Model The Clark-Wilson Model*,  "Create a plantuml mindmap to summarize it"
- [TryHackMe - Security Principles](https://tryhackme.com/r/room/securityprinciples)
- Mike Chapple (YouTube):

  - [CertMike Explains the Biba Integrity Model](https://www.youtube.com/watch?v=nfmwSGtyzV0)
  - [The Bell LaPadula Model](https://www.youtube.com/watch?v=G1FWTfJsK6k)

  ### 