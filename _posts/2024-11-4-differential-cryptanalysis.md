---
layout: post
title: Differential Cryptanalysis - Targeting Hash Functions and Cryptographic Algorithms
date:   2024-10-30
lang: en
locale: en-GB
categories: blockchain cryptography
tags: cryptography
description: Differential cryptanalysis is a technic to attack symmetric cryptographic algorithms, such as block ciphers, by analyzing the impact of specific input differences on output differences after several rounds of encryption. 
image:
isMath: true
---

**Differential cryptanalysis** is a technic to attack symmetric cryptographic algorithms, such as block ciphers, by analyzing the impact of specific input differences on output differences after several rounds of encryption. 

This technique, developed in the late 1980s by Eli Biham and Adi Shamir, is especially effective against algorithms that rely on substitution and permutation operations.  Researchers at IBM had already discovered similar techniques in 1974 but not to disclose them publicly.

While initially applied to block ciphers, differential cryptanalysis can also be adapted to attack hash functions, which are essential in ensuring data integrity and digital signatures in modern cryptographic systems.

## Understanding Differential Cryptanalysis

Differential cryptanalysis focuses on how small changes in the input (plaintext) can create predictable changes in the output (ciphertext or hash output). It is especially effective in targeting the "confusion" and "diffusion" mechanisms within block ciphers and hash functions. The attack exploits certain properties within these mechanisms to find specific relationships, known as differential characteristics, that reveal patterns and weaknesses in the algorithm.

### Key Concepts

1. **Plaintext and Ciphertext Differences:** Differential cryptanalysis examines the effect of changing certain bits in the plaintext and how those changes propagate through the encryption process. This difference is often expressed as a binary XOR operation between two inputs.
2. **Differential Characteristics:** These are specific patterns or structures in the cipher that describe how differences in inputs relate to differences in outputs over multiple rounds. They help cryptanalysts track how differences propagate through rounds and layers of encryption or hashing.
3. **Probability of Differences:** A key aspect of differential cryptanalysis is finding differences that occur with a high probability, as these differences are more likely to reveal underlying structures in the cryptographic algorithm.

### Mathematical Foundation

In differential cryptanalysis, let’s denote:

- X and X′ as two different plaintexts,

$$
\Delta X = X \oplus X'
$$



- Y and Y′ as the outputs after encryption,

$$
\Delta Y = Y \oplus Y'
$$





The goal of differential cryptanalysis is to find a differential characteristic (ΔX,ΔY) that has a high probability of occurring.

## Differential Cryptanalysis Against Block Ciphers

Differential cryptanalysis has historically targeted block ciphers by analyzing the substitution-permutation network (SPN) or the Feistel structure in the cipher. 

In block ciphers, input differences can often lead to patterns in the encryption process, which cryptanalysts exploit to reveal parts of the encryption key or the structure of the cipher.

### Differential cryptanalysis against FEAl

FEAL (Fast data Encipherment ALgorithm) is a [block cipher](https://en.wikipedia.org/wiki/Block_cipher) considered at the beginning as an alternative to the [Data Encryption Standard](https://en.wikipedia.org/wiki/Data_Encryption_Standard) (DES) but it is vulnerable to several attacks against it.

- Feal-4 had four rounds. This version was broken by Den Boer using a chosen plaintext attack with 100 to 10000 ciphertexts and another attack by Sean Murphy uses [differential cryptanalysis](https://en.wikipedia.org/wiki/Differential_cryptanalysis) that needs only 20 chosen plaintexts
-  For Feal-8, [Eli Biham](https://en.wikipedia.org/wiki/Eli_Biham) and [Adi Shamir](https://en.wikipedia.org/wiki/Adi_Shamir) described a differential attack on this version in 1989.

#### FEAL-4

FEAL-4 is a 4 round Feistel cipher with a 64 bit block size. This means that the algorithm encrypts/decrypts data in 64 bit chunks. 

- The Feistel structure means that the blocks are actually split in half for processing
- These halves are mixed together via XOR operations throughout the encryption. 
- The non-linear component (the heart of the cipher) is called the **round function**
  -  It is a one-way/trapdoor function that takes a 32 bit input and produces a 32 bit output. 
  - This function is used 4 times during encryption: once for each round. 
  - The strength of FEAL-4 against statistical attacks like differential cryptanalysis is dependent on the behavior of this round function.

#### Comparison with DES

- The structure of FEAL is similar to DES with a modified *F* function, initial and final permutations and key scheduling algorithm. 
- In the *F* function, the *P* permutation and the S boxes of DES are replaced by byte rotations and addition operations

- [theamazingking.com/crypto-feal.php](http://www.theamazingking.com/crypto-feal.php)
- [FEAL-4 Linear Cryptanalysis - Prevention](https://crypto.stackexchange.com/questions/40407/feal-4-linear-cryptanalysis-prevention)
- [Wikipedia - FEAL](https://en.wikipedia.org/wiki/FEAL)

### Differential cryptanalysis against DES

Main idea: 

- This is a chosen plaintext attack, assumes than an attacker knows (plaintext, ciphertext) pairs

- Distribution of may reveal information about the key (certain key bits) 
- After finding several bits, use brute-force for the rest of the bits to find the key.

Surprisingly … DES was resistant to differential cryptanalysis. 

- At the time DES was designed, the authors knew about differential cryptanalysis. 
- S-boxes were designed to resist differential cryptanalysis. 
  - Against 8-round DES, attack requires 238 known plaintext-ciphertext pairs. 
  - Against 16-round DES, attack requires 2 47 chosen plaintexts. 
- Differential cryptanalysis is not effective against DES in practice

Reference:

[Purdue CSS 355 - Introduction to Cryptography](https://www.cs.purdue.edu/homes/ninghui/courses/Fall05/lectures/355_Fall05_lect17.pdf)

#### Example

In this [article](https://medium.com/@jnaman806/breaking-des-using-differential-cryptanalysis-958e8118ff41), the author presents a working attack, but against 6-round DES

## Differential Cryptanalysis against hash function

Differential cryptanalysis also poses a threat to hash functions, which are vital for data integrity and digital signatures. Hash functions map arbitrary-length input data to fixed-size hash outputs. Ideally, even a single bit change in the input should cause a significant change in the output hash (the avalanche effect).

In hash functions, the attacker’s objective is often to find a **collision**—two different inputs that produce the same hash output.

### IOTA Hash Function Curl

Differential cryptanalysis was used by cryptography researchers to find collision on IOTA’s custom hash function Curl-P-27.

OTA Signature Scheme (ISS) is based on Winternitz One-Time Signatures, see [my article](https://rya-sge.github.io/access-denied/2024/05/30/winternitz-signature-scheme/).

In IOTA, users uses winternitz to sign the hash of a message. 

Thus, the security of ISS relies on its cryptographic hash function, which was Curl-P-27.

The vulnerability was used to generate practical collisions and to produce two payments (p1 and p2) in IOTA (they call them “bundles”) which are different, but hash to the same value h, and thus have the same signature s. 
$$
Hash(p1) == hash (p2)
$$


The attack on the IOTA signature scheme function works in a **chosen-message** setting, where an attacker creates two payments—a benign payment and a malicious payment—such that a signature on the benign payment is also a valid signature on the malicious payment.  

- This vulnerability could potentially allow an attacker to destroy users’ funds, or possibly, stolen user funds.
- These attacks apply to both normal and multi-signature IOTA payments.
- Nevertheless, in practice, the attack can be more complicate to produce due the presence of a centralized components (IOTA Coordinator) and the need of a

Spending from a multi-signature address requires one user to produce a payment for another user to sign, which fits exactly in the chosen-message setting of the  attack.

- [Neha - Cryptographic vulnerabilities in IOTA](https://medium.com/@neha/cryptographic-vulnerabilities-in-iota-9a6a9ddc4367)

- [Blackhast - Cryptanalysis of Curl-P and Other Attacks on the IOTA Cryptocurrency](https://i.blackhat.com/us-18/Wed-August-8/us-18-Narula-Heilman-Cryptanalysis-of-Curl-P-wp.pdf)

- [Official IOTA Foundation Response to the Digital Currency Initiative at the MIT Media Lab — Part 4 / 4](https://blog.iota.org/official-iota-foundation-response-to-the-digital-currency-initiative-at-the-mit-media-lab-part-4-11fdccc9eb6d/)

## Countermeasures to Differential Cryptanalysis

Given the effectiveness of differential cryptanalysis, modern cryptographic algorithms often incorporate design features specifically to thwart it:

1.**Randomized Substitution-Permutation Layers:** Many modern ciphers use more complex S-boxes and mixing layers, minimizing the probability of predictable differential characteristics. you need to prove that the Differentials don't go over a certain probability (the lower the better).

2.**Increased Round Count:** By adding rounds, it becomes harder for attackers to track input-output differences, which decreases the effectiveness of differential attacks.

For example, in the case of FEAL, they switched from 4 to 8 rounds and then to N rounds where N is chosen by the user. But similar attack  to differential cryptanalysis was still possible on the 8 round version

3.**Advanced Hash Functions:** Secure hash algorithms like SHA-256 are designed to prevent differential characteristics from propagating through their iterative structures.

4.**Key Schedule Improvements:** Algorithms now use complex key scheduling mechanisms to ensure that keys do not exhibit predictable patterns across rounds.

Reference: [FEAL-4 Linear Cryptanalysis - Prevention](https://crypto.stackexchange.com/questions/40407/feal-4-linear-cryptanalysis-prevention), [FEAL](https://en.wikipedia.org/wiki/FEAL)

## 5. Conclusion

Differential cryptanalysis is a significant technique that has been used to create modern cryptography. While initially effective against early block ciphers like Festel, this attack has also driven the development of more robust encryption standards and secure hashing algorithms that resist such attacks. 

## Reference

- [Wikipedia - Differential cryptanalysis](https://en.wikipedia.org/wiki/Differential_cryptanalysis)
- [Purdue CSS 355 - Introduction to Cryptography](https://www.cs.purdue.edu/homes/ninghui/courses/Fall05/lectures/355_Fall05_lect17.pdf)
- IOTA:
  - [Neha - Cryptographic vulnerabilities in IOTA](https://medium.com/@neha/cryptographic-vulnerabilities-in-iota-9a6a9ddc4367)
  - [Blackhast - Cryptanalysis of Curl-P and Other Attacks on the IOTA Cryptocurrency](https://i.blackhat.com/us-18/Wed-August-8/us-18-Narula-Heilman-Cryptanalysis-of-Curl-P-wp.pdf)
  - [Official IOTA Foundation Response to the Digital Currency Initiative at the MIT Media Lab — Part 4 / 4](https://blog.iota.org/official-iota-foundation-response-to-the-digital-currency-initiative-at-the-mit-media-lab-part-4-11fdccc9eb6d/)
- ChatGPT with the input "Write me an article about the attack DIFFERENTIAL CRYPTANALYSIS targeting hash function and cryptography algorithm. Give examples."