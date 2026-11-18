---
layout: post
title: Main Security Models - Overview
date: 2025-01-15
last_modified_at: 2026-11-17
lang: en
locale: en-GB
categories: security tryhackme
tags: security threat Bell-LaPadula Clark-Wilson Biba tryhackme
description: "Bell-LaPadula, Biba and Clark-Wilson security models: the confidentiality and integrity rules each one enforces, with examples."
image: /assets/article/securite/security-model/security-models-bell-lapadula-model.drawio.png
isMath: false
---

This article presents three foundational security models: **Bell-LaPadula**, **Biba**, and **Clark-Wilson**.

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

## What you need to know first

The three models are formal access-control policies, and the article describes their rules with a vocabulary from access-control theory that it does not introduce.

- **Subjects and objects**: a subject is an active entity that requests access, such as a user or a process, and an object is a passive resource it accesses, such as a file or a record. Every rule in the article is a condition on whether a given subject may read or write a given object.
- **Security and integrity levels**: each subject and object carries a label taken from an ordered set, for example Unclassified < Confidential < Secret < Top Secret. A subject's label is its clearance and an object's label is its classification, and Bell-LaPadula and Biba decide access by comparing the two.
- **Mandatory and discretionary access control**: under mandatory access control, a system-wide policy decides access and the owner of an object cannot override it. Under discretionary access control, the owner grants permissions as they choose. The no-read-up and no-write-down rules are mandatory, while the discretionary property of Bell-LaPadula adds a discretionary layer on top; see [Advanced GNU/Linux Security - SECCOMP and Linux Security Modules (LSM)]({{site.url_complet}}/2026/06/29/linux-advanced-security-seccomp-lsm/).
- **Information flow**: reading moves information from an object to a subject, and writing moves it from a subject to an object. The models restrict the direction of these flows between levels: Bell-LaPadula stops secrets flowing down, Biba stops untrusted data flowing up.
- **State machine model**: Bell-LaPadula describes the system as a set of states and proves that every allowed transition keeps the system in a secure state. Clark-Wilson's "well-formed transactions" rely on the same idea of moving only from one valid state to another.

------

## The Three Models

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

The first two properties can be summarized as “write up, read down.” Writing up means you can share confidential information with people of higher security clearance, and reading down means you can receive confidential information from people with lower security clearance.

There are certain limitations to the Bell-LaPadula model. For example, it was not designed to handle file-sharing.

References:

[YouTube - Mike Chapple - CertMike Explains The Bell LaPadula Model](https://www.youtube.com/watch?v=G1FWTfJsK6k)

------

### Biba Integrity Model

The Biba model emphasizes **data integrity**, ensuring that information is not improperly modified.

![security-models-biba-integrity-model.drawio]({{site.url_complet}}/assets/article/securite/security-model/security-models-biba-integrity-model.drawio.png)

#### Key Principles:

**Simple Integrity Property (no read-down):**

This principle prohibits subjects from reading information below their own integrity level.

- A subject cannot read data at a lower integrity level.

- This prevents contamination of high-integrity processes with low-integrity data.
- But why ? This information may be incorrect since it came from a lower level

**Integrity \*-Property (no write-up):**

- A subject cannot write data to a higher integrity level.
- This prevents low-integrity processes from corrupting high-integrity data.

#### Variants

Biba also includes the **low-water-mark principle** and **ring policy** for additional flexibility in enforcing integrity.

#### Use Case

Common in military, financial or healthcare systems, where decisions depend on accurate and reliable data.

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

- A subject, such as a user, can only access an object, such as data, through a transformation procedure: an authorized application or process.
- This prevents direct, unrestricted access to data.

4. **Auditability:**

Every action is logged to provide traceability and accountability.

#### Use Case

Often used in commercial systems (e.g., banking) to enforce proper workflows, prevent fraud, and ensure compliance with regulations.

Example:

The main goal is consistency among the various components of the system state

In a bank, the funds at the beginning of the day plus the funds deposited minus the funds withdrawn should equal funds on hand at the end of the day.

Reference: [cs.utexas.edu - lecture24-4up.pdf](https://www.cs.utexas.edu/~byoung/cs361/lecture24-4up.pdf)

See also [YouTube - Security Models Pt 3 Clark-Wilson, Brewer and Nash, Graham-Denning (CISSP Free by Skillset.com)](https://www.youtube.com/watch?v=4esHgEOmTqU)

------

## Summary Comparison

| **Model**     | **Focus**                      | **Key Rules**                                  | **Use Case**                 |
| ------------- | ------------------------------ | ---------------------------------------------- | ---------------------------- |
| Bell-LaPadula | Confidentiality                | No read-up, no write-down                      | Military/Government systems  |
| Biba          | Integrity                      | No read-down, no write-up                      | Financial/Healthcare systems |
| Clark-Wilson  | Integrity + Business Workflows | Well-formed transactions, separation of duties | Business/Commercial systems  |

Each model addresses different security needs and is tailored to specific types of threats and environments.

### Schema

![security-models-summary.drawio]({{site.url_complet}}/assets/article/securite/security-model/security-models-summary.drawio.png)

### Mindmap

![security-models-mindmap]({{site.url_complet}}/assets/article/securite/security-model/security-models-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Subject** | An active entity, such as a user or a process, that requests access to data. |
| **Object** | A passive resource, such as a file or a data item, that a subject reads or writes. |
| **Security level** | The label assigned to subjects and objects, a clearance or a classification, that the models compare to decide whether an access is allowed. |
| **Bell-LaPadula model (BLP)** | A model focused on confidentiality, used in military and government systems, that prevents classified information from leaking to lower levels. |
| **Simple Security Property** | The Bell-LaPadula rule "no read-up": a subject cannot read data at a higher security level than its own. |
| **\*-Security Property** | The Bell-LaPadula rule "no write-down": a subject at a higher level cannot write data to a lower level. |
| **Discretionary Security Property** | The Bell-LaPadula rule that adds an access matrix of allowed read and write operations on top of the two level-based properties. |
| **Access matrix** | A table with one row per subject and one column per object, whose cells list the operations each subject may perform on each object. |
| **Biba integrity model** | A model focused on integrity that prevents data from being improperly modified, summarised as "read up, write down". |
| **Simple Integrity Property** | The Biba rule "no read-down": a subject cannot read data at a lower integrity level, which could be incorrect. |
| **Integrity \*-Property** | The Biba rule "no write-up": a subject cannot write data to a higher integrity level. |
| **Clark-Wilson model** | An integrity model for commercial systems that enforces well-formed transactions, separation of duties and auditability. |
| **Constrained Data Item (CDI)** | In Clark-Wilson, data whose integrity the system must preserve. |
| **Unconstrained Data Item (UDI)** | In Clark-Wilson, any data outside the CDIs, such as user and system input. |
| **Transformation Procedure (TP)** | In Clark-Wilson, a programmed operation that is the only allowed way to modify CDIs and must maintain their integrity. |
| **Integrity Verification Procedure (IVP)** | In Clark-Wilson, a procedure that checks that the CDIs are valid. |
| **Access triple** | The Clark-Wilson rule that a subject reaches an object only through an authorised transformation procedure, written (subject, TP, object). |
| **Separation of duties** | The principle that restricts users to specific roles so that no single individual has unchecked control over sensitive data. |

## References

- ChatGPT with the inputs: *Explain these different models: Bell-LaPadula Model The Biba Integrity Model The Clark-Wilson Model*,  "Create a plantuml mindmap to summarize it"
- [TryHackMe - Security Principles](https://tryhackme.com/r/room/securityprinciples)
- Mike Chapple (YouTube):

  - [CertMike Explains the Biba Integrity Model](https://www.youtube.com/watch?v=nfmwSGtyzV0)
  - [The Bell LaPadula Model](https://www.youtube.com/watch?v=G1FWTfJsK6k)
