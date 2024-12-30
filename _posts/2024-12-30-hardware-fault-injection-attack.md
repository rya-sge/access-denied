---
layout: post
title: Hardware Security: Understanding Fault Injection Attack
date:   2024-12-30
lang: en
locale: en-GB
categories: security cryptography fault-injection side-channel hardware crypto-wallet
tags: tls mtls cloud
description: Fault injection attack (FIA) is a technique that targets the hardware itself to create unexpected behaviors in systems, often with catastrophic consequences.
image: 
isMath: false
---

Fault injection attack (FIA) is a technique that targets the hardware itself to create unexpected behaviors in systems, often with catastrophic consequences. 

This article delves into fault injection attacks, their mechanisms, targets, and the defenses against them.

> Warning: this article is still in draft state and its content is still mainly taken from several different sources and ChatGPT with a few modifications of my part. Its content should become more personal later.

[TOC]

## Introduction

Fault attacks have been introduced by Boneh, DeMillo and Lipton at Eurocrypt’97.

- The goal consists in perturbing the computation of
  cryptographic operations and to observe the erroneous result.
- Perturbation can occur in many different ways  !

Unlike traditional attacks that rely on exploiting software bugs or network vulnerabilities, fault injection seeks to compromise a system by inducing errors, thereby opening the door for malicious activities. 

### What is a Fault Injection Attack?

A fault injection attack is a deliberate attempt to disrupt the normal operation of a system by injecting errors into its hardware components. 

These errors can be induced by applying stress, such as:

- sudden voltage spikes, 
- clock glitches,
- temperature variations, 
- or even physical manipulation (like laser or electromagnetic interference). 

The idea is to introduce faults into the system, causing it to behave in unintended ways, such as bypassing security checks or revealing sensitive information.

In simpler terms, fault injection can be thought of as corrupting the normal functioning of hardware to expose hidden weaknesses in its behavior. 

For example, an attacker might inject faults into a cryptographic process, causing it to leak cryptographic keys or skip essential authentication steps.

## How Fault Injection Attacks Work

Fault injection attacks are executed by creating a controlled environment where faults are artificially introduced. 

Here are some common techniques used to achieve this:

### Voltage Fault Injection (VFI)

In this method, the attacker manipulates the power supply of the hardware device. By lowering or spiking the voltage at critical times, the hardware's logic may misbehave, leading to errors in operations. This technique is often used to bypass security mechanisms in microcontrollers and secure elements.

### Clock Glitching

Digital systems rely on clock signals to synchronize their operations. By temporarily altering the clock frequency, an attacker can cause timing-related issues, where the system may skip certain instructions or process them incorrectly. This can, for example, allow bypassing authentication or causing a cryptographic algorithm to malfunction.

Requirements:

- Access to internal clock
- Generation and introduction of different clock waveforms

### Electromagnetic Fault Injection (EMFI)

By exposing hardware to a strong electromagnetic pulse, attackers can disrupt the flow of data or corrupt memory cells, forcing the device to behave in an unexpected way. This technique is non-invasive, meaning attackers do not need direct contact with the device, making it highly effective in attacking embedded systems.

Requirement: Electromagnetic pulse shape generation at desired location on chip.

### Laser Fault Injection

Using focused laser beams, attackers can target specific transistors on a chip to alter their behavior. This highly precise method can be used to induce faults in specific regions of a processor, leading to erroneous computations or corrupted data.

Requirement: Chip decapsulation and high precision laser spot generation.

Cost & Difficulty: high

### Targets of Fault Injection Attacks

Fault injection attacks are primarily used against hardware devices, especially those that contain sensitive data or perform critical tasks. Some of the common targets include:

- **Smartcards**: Widely used for financial transactions, smartcards are often a target for attackers trying to extract cryptographic keys or bypass security checks.
- **Embedded Systems**: Found in consumer electronics, industrial control systems, and automotive systems, embedded devices can be vulnerable to fault injections, which could lead to device malfunction or data corruption.
- **Cryptographic Devices**: Fault injection can target hardware security modules (HSMs) or devices performing encryption and decryption operations. By inducing errors, attackers may extract encryption keys, allowing them to decrypt sensitive data.
- **Trusted Execution Environments (TEEs)**: TEEs, such as ARM’s TrustZone, are designed to run secure code isolated from the rest of the system. Fault injection can compromise the isolation, enabling attackers to gain access to protected areas of memory or manipulate sensitive operations.

## Consequences of Fault Injection Attacks

The potential consequences of fault injection attacks can be severe, depending on the system being targeted. Here are a few critical outcomes:

- **Key Extraction**: In cryptographic systems, fault injections can lead to the leakage of cryptographic keys. By analyzing how a cryptographic algorithm responds to faults, attackers can reverse-engineer the key, leading to unauthorized access to encrypted data.
- **Authentication Bypass**: In many systems, fault injection can disable or corrupt authentication mechanisms, allowing attackers to bypass password or PIN verification steps.
- **System Integrity Violation**: In embedded systems or industrial control units, fault injection can cause unpredictable behavior, potentially leading to malfunctions that can disrupt service or even cause physical damage.
- **Tampering with Software**: Fault injection can also lead to the execution of arbitrary code, allowing attackers to modify or tamper with software running on a system. This can lead to a full compromise of the device’s functionality.

## Methods to Prevent Fault Injection Attacks

Given the growing threat of fault injection attacks, researchers and industry leaders have developed several defense mechanisms to protect hardware and systems from such exploits. These include:

### Software approach

Software can also be designed to detect the symptoms of a fault injection. For example, cryptographic algorithms can include fault-resistant implementations that double-check intermediate computations to detect tampering attempts.

#### Randomization

Introducing randomization into the system's operation, such as varying the timing of sensitive operations, can make it harder for attackers to predict when to inject faults, thereby reducing the success rate of attacks.

#### Error Detection / Checksums

Perform checksum on data transfers

#### Execution/temporal Redundancy

It consists to perform the same operation multiple times and verifies that the result is still the same.

By verifying the results of critical operations multiple times, the system can recognize discrepancies caused by a fault injection and take corrective action.

### Hardware approach

#### Fault detector (sensors)

Hardware manufacturers can integrate countermeasures directly into the chip to detect and mitigate the effects of fault injections. For example, secure processors may include voltage sensors, temperature sensors, and clock monitoring circuits that detect irregularities and trigger system resets if faults are suspected.

#### Hardware redundancy

duplicate parts of the hardware to perform computation in parallel. If the attack is successful on one computation, the second will show the right result allowing to detect the attack.

#### Physical Security (special encapsulations)

Strengthening the physical security of devices, such as enclosing critical components in tamper-resistant casings, can make it more difficult for attackers to manipulate hardware directly.

## Cryptography case study

### Perturbing Cryptographic Operations

One can induce faults in semiconductors in many different
ways :

- Electrical glitches ;
- Optical fault induction (laser) ;

- Subtle software or hardware bugs (bug attacks) ;
- etc.

Often, one uses Simple Power Analysis(SPA) or SEMA to properly synchronize the
fault induction time,.

#### Fault Attacks - Verifications

- In a RSA signature verification : signature has to be
  checked.
- The CPU/hardware decides, based on a single bit (OK/NOK),
  whether the signature is valid or not.
- One can fault the instruction enforcing the decision (i.e.,
  transform a JNE in a NOP or in a JE instruction).

#### Rounds

- It is possible to reduce the number of rounds of a cipher.
- We assume that the counter value tracking the remaining
  number of rounds to be computed can be faulted.
- This allows sometimes to recover some bits of the secret key.
- For instance, by reducing the number of rounds to 1.

### Protection Mechanisms

- Add redundancy :
  - When computing an RSA signature, verify the obtained
    result just after.
  - Implement multiple times the same operation and
    compare the results either in a sequential or in a parallel
    way.
- Use arithmetic tricks, such as Shamir’s trick (see exercise)
- Masking.
- Many protection mechanisms are patented !

### Conclusion

Fault injection attacks represent a sophisticated threat against hardware devices used in IoT, finance, and other critical sectors. 

While the techniques for inducing faults have become more refined, defense mechanisms are also evolving, with hardware and software developers working to mitigate the risks posed by such attacks. 

Understanding the mechanics of fault injection, as well as its potential impacts, is crucial for the ongoing development of secure hardware based-systems. 

## References

- [Dekra -Fault Injection Attacks](https://www.dekra.com/en/fault-injection-attacks/)
- Cryptography course (CRY) taught at HEIG-VD in 2023
- ChatGPT with the input "Write me an article about fault injection attack"