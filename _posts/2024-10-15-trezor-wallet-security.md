---
layout: post
title: Trezor Crypto Wallet – Cryptography and Security
date:   2024-10-15
lang: en
locale: en-GB
categories: blockchain cryptography security
tags: blockchain wallet trezor hardware
description: This article presents the different types of crypto wallets (hot, warm, cold) and their associated risks
image: /assets/article/blockchain/wallet/trezor/trezor-secure-element.png
isMath: true
---

A **hardware wallet** is one of the most trusted tools for safeguarding cryptocurrencies yourself (self-custodial), providing robust security by keeping your private keys offline and away from online threats,  reducing the risk of hacking and malware.

Among the most popular and trusted hardware wallets for storing digital assets securely is **Trezor**, a product developed by [SatoshiLabs](https://satoshilabs.com), Czech technology holding.

Trezor offers several different models, —Trezor One and Trezor Model T for example—each designed to provide users with several functionalities to protect its assets.

This article explores the key security features of Trezor wallets, the cryptographic algorithms they utilize,  how they protect the seed phrase and the private keys.

Firstly, here is a summary of the different options related to security available depending on the models.

| Model                                                        | Seed phrase backup         |  | Device Security       |        |  |         | Authentication                             |                              |
| ------------------------------------------------------------ | -------------------------------- | ------------------ | --------------------------- | ------------------------------------------ | ------- | ------- | ------- | ------- |
|                                                                              | 12-, 20- & 24-word wallet backup | Multi Share |Pin & passphrase protection|On device entry|MicroSD card support|Secure element protected<br />Certified Chip EAL6+|Two-factor authentication|FIDO2 Standard|
| [Trezor Model One](https://trezor.io/trezor-model-one)       | &#x2611; | &#x2612;         | &#x2611; | &#x2612; | &#x2612; | &#x2612; | &#x2611;       | &#x2612; |
| [Trezor Model T](https://trezor.io/trezor-model-t)           | &#x2611; | &#x2611;        | &#x2611; | &#x2611; | &#x2611; | &#x2612; | &#x2611; | &#x2611; |
| [Trezor Safe 3](https://trezor.io/trezor-safe-3-cosmic-black) | &#x2611; | &#x2611;        | &#x2611; | &#x2611; | &#x2612; | &#x2611; | &#x2611; | &#x2611; |
| [Trezor Safe 5](https://trezor.io/trezor-safe-5)             | &#x2611; | &#x2611;        | &#x2611; | &#x2611; | &#x2611; | &#x2611; | &#x2611; | &#x2611; |

See also [trezor.io/compare](https://trezor.io/compare)

[TOC]

------

## Core Security Features of Trezor Wallets

### 1. Offline Private Key Storage

The cornerstone of Trezor’s security is the **offline storage** of private keys. Since Trezor is a hardware wallet, your private keys never leave the device, ensuring that they are not exposed to the internet. This **air-gapped** design protects against hacking attempts, phishing attacks, and malware, which are common on internet-connected (hot) wallets.

### 2. PIN Protection

Every Trezor wallet requires a **PIN code** to access the device. This PIN is set by the user during initialization and is a critical layer of protection against unauthorized physical access. The PIN entry process is randomized on the Trezor screen, making it resistant to keylogging or screen capture attacks that can occur on compromised computers.

References: [trezor - PIN protection on Trezor devices ](https://trezor.io/learn/a/pin-protection-on-trezor-devices), [Trezor suite protection against keyloggers?](https://forum.trezor.io/t/trezor-suite-protection-against-keyloggers/6386)

### 3. Passphrase Support

In addition to a PIN, Trezor provides the option to add an additional layer of security in the form of a **passphrase**. This passphrase essentially acts as a 25th word added to the standard 24-word recovery seed. 

A passphrase has two main purposes:

- Even if someone gains access to the recovery seed, without knowing the passphrase, they will not be able to recover the wallet. 
- Add your own entropy: even if there is a vulnerability in the random generation by the wallet, it will not possible to recover the wallet without the passphrase.

The wallet obtained by adding a passphrase is called a `hidden wallet`
$$
\begin{aligned}
recovery~seed + passphrase = hidden~ wallet
\end{aligned}
$$
Reference: [Trezor - Passphrases and hidden wallets](https://trezor.io/learn/a/passphrases-and-hidden-wallets)

### 4. Recovery Seed

When you initialize your Trezor wallet, you are provided with a **recovery seed**, which is a randomly generated 12-24 word phrase. This seed allows you to restore your wallet in case the device is lost or damaged. The seed is generated offline, and the user must write it down in a secure place, as it is the only way to recover the funds. Trezor implements a **BIP-39** mnemonic phrase standard for this recovery seed.

References: [Trezor - How to use a recovery seed](https://trezor.io/learn/a/how-to-use-a-recovery-seed)

### 5. Firmware Updates

Trezor regularly releases **firmware updates** to fix bugs, patch vulnerabilities, and add new features.  In case of a compromission of the Trezor architecture, a malicious firmware update could have a disastrous result and compromise your funds.

There are several protections put in place by Trezor to avoid a malicious update:

- These updates require user confirmation via the device’s screen, preventing unauthorized or malicious firmware installations. 
- The firmware is also **signed** by SatoshiLabs, ensuring the authenticity of the update before installation.
- Downgrading the firmware, which could be used to install a vulnerable version of Trezor,  erases the memory as a result.

Reference: [Security & safety in Trezor ](https://trezor.io/learn/a/security-safety-in-trezor?srsltid=AfmBOoo-zyONXBVPkTbfQ1r552tSE6H8g2FruZ5JFBbCayxHWeTcCYg8)

------

## Trezor's encryption Key terms

This section is based on the following resource: [PIN verification and decryption of protected entries in flash storage](https://docs.trezor.io/trezor-firmware/storage/index.html#pin-verification-and-decryption-of-protected-entries-in-flash-storage)

### Schema

#### Data encryption Diagram

What happens when the user choose a new PIN?

![trezor-encryption-pin.drawio]({{site.url_complet}}/assets/article/blockchain/wallet/trezor/trezor-encryption-pin.drawio.png)

#### Activity diagram

What happens when the user enters their PIN?

![trezor-pin-diagram-activity]({{site.url_complet}}/assets/article/blockchain/wallet/trezor/trezor-pin-diagram-activity.png)

### Main Cryptography algorithm

####  PBKDF2 (Password-Based Key Derivation Function 2) with HMAC

**PBKDF2** is a cryptographic key derivation function, which is resistant to [dictionary attacks](https://en.wikipedia.org/wiki/Dictionary_attack) and [rainbow table attacks](https://en.wikipedia.org/wiki/Rainbow_table) by using a salt. 

In summary,it is a key derivation function that uses a password (in this case, the PIN), a salt (a random value), and multiple iterations of a cryptographic hash function (e.g **HMAC**) to generate a derived key.

- It is described in the Internet standard [RFC 2898 (PKCS #5)](http://ietf.org/rfc/rfc2898.txt). 
- **Purpose** in Trezor: It is used to transform the user's **PIN** into a strong cryptographic key (in this case, the KEK and KEIV). The function also incorporates a salt to prevent precomputed attacks (such as rainbow tables).
- **How it works**: PBKDF2 uses the user's PIN as input and combines it with a salt derived from hardware identifiers (e.g., ProcessorID) and the random salt from flash storage. It runs the hash function (HMAC-SHA256) for 10,000 iterations (or more), producing 352 bits of output: the first 256 bits become the **KEK** and the last 96 bits form the **KEIV**.

See [cryptobook.nakov.com - pbkdf2](https://cryptobook.nakov.com/mac-and-key-derivation/pbkdf2)

#### HMAC-SHA256

Here some supplementary defails about HMAC used by PBKDF2.

HMAC stands for Hash-based Message Authentication Code

To derive the Encryption Key (KEK), Trezor uses PBKDf2 with **HMAC-SHA512** to make brute-force attacks more difficult. 

HMAC adds an extra layer of security when handling cryptographic keys, making it harder for attackers to recover the seed phrase or private keys from device data (brute-force attack). 

To obtain that, the HMAC process mixes a secret key, in the case of trezor, the salt, with the message data and hashes the result.

See [datatracker.ietf.org/doc/html/rfc4868#page-3](https://datatracker.ietf.org/doc/html/rfc4868#page-3), [Microsoft - HMACSHA512 Class](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.hmacsha512?view=net-8.0)

#### ChaCha20-Poly1305

**ChaCha20-Poly1305** provides both encryption by using the stream cipher ChaCha20 and authentication with Poly1305 as message authentication code (MAC)  in a single operation. The resulting algorithm is called an Authenticated Encryption with Additional Data cipher (AEAD)

- It is defined in [**RFC 7539**](https://datatracker.ietf.org/doc/html/rfc7539.html) section 2.8.  
- This combination offers strong integrity guarantees.

- **Purpose**: It is used to **encrypt and decrypt data securely**, ensuring both confidentiality and integrity of the data. In Trezor, it is used to encrypt the **EDEK** and the protected entries stored in the flash.
- **How it works:**
  - **ChaCha20** is the encryption part, which transforms plaintext data into ciphertext using a key (e.g., KEK or DEK) and an IV (like the KEIV or entry IV).
  - **Poly1305** is the authentication part, which generates a **tag** (a type of checksum) that ensures the data hasn’t been tampered with. The tag is checked during decryption to verify the data's integrity.
- ChaCha20-Poly1305 ensures that even if an attacker modifies the encrypted data or its associated metadata (like the IV), the decryption process will fail due to a tag mismatch.

See [cryptography - AEAD](https://cryptography.io/en/stable/hazmat/primitives/aead/), [cloudflare - chacha0Poly1305](https://blog.cloudflare.com/it-takes-two-to-chacha-poly/) and [Wikipedia - ChaCha20-Poly1305](https://en.wikipedia.org/wiki/ChaCha20-Poly1305), [Proton - ChaCha20](https://protonvpn.com/blog/chacha20)

### Keys and PVC

Here's an explanation of the different keys used in Trezor's encryption and PIN verification process

#### Trezor Storage

These elements are stored on the Trezor storage.

##### (E)DEK (Data Encryption Key)

The **DEK** is the actual key used to encrypt and decrypt protected data stored in flash storage.

- **Purpose**: The DEK protects sensitive data entries in the device’s flash memory. It is derived by decrypting the **EDEK** with the KEK and KEIV.
- **How it works**: The DEK is used to encrypt and decrypt specific entries (e.g., secrets, settings) in the storage. Without the correct DEK, these entries cannot be read or tampered with.

##### (E)SAK (Storage authentication key)

The storage authentication key (SAK) is used to authenticate the list of (APP, KEY) values for all protected entries that have been set in the storage. This prevents an attacker from erasing or adding entries to the storage.

- The key is encrypted with the key derived from the user's pin

- This key is stored encrypted in the storage.

##### PVC (PIN Verification Code)

The PVC is a **64-bit code** stored in the flash memory and used to verify if the correct PIN was used during decryption.

- **Purpose**: It serves as a **verification mechanism** to ensure the PIN entered by the user is correct. After the EDEK is decrypted, the PVC is compared with a tag value derived during the decryption process.
- **How it works**: If the PVC matches the computed tag, it confirms that the decryption was performed using the correct PIN. If the PVC doesn’t match, the decryption fails, indicating an incorrect PIN.
- Remark from the trezor documentation: The 64-bit PVC means that there is less than a 1 in 1019 chance that a wrong PIN will happen to have the same PVC as the correct PIN. The existence of false PINs does not pose a security weakness since a false PIN cannot be used to decrypt the protected entries.

#### Compute

##### KEK (Key Encryption Key)

The **KEK** is a 256-bit key derived from the user’s PIN and a salt using the **PBKDF2** algorithm.
$$
\begin{aligned}
KEK || KEIV = PBKDF2(PRF = HMAC-SHA256, Password = pin, Salt = salt, iterations = 10000, dkLen = 352 bits)
\end{aligned}
$$

The KEK is used to decrypt the Encrypted Data Encryption Key **(EDEK)**, allowing access to the actual Data Encryption Key (DEK).

- **How it works**: The KEK is part of a layered security approach: instead of encrypting data directly with the PIN, Trezor derives the KEK from the PIN to ensure additional protection. This is notably useful against [fault injection attacks](https://www.dekra.com/en/fault-injection-attacks/).
- This means an attacker would need the KEK, derived from a valid PIN, to access the encrypted key (EDEK).

##### KEIV (Key Encryption Initialization Vector)

The KEIV is a 96-bit value derived alongside the KEK using the **PBKDF2** algorithm.

- **Purpose**: It is used as an **initialization vector (IV)** for the encryption algorithm **ChaCha20Poly1305**, which helps ensure that even if the same key (KEK) is reused, the output will be different by combining it with the KEIV.
- **How it works**: The KEIV ensures that the encryption process is randomized and secure, so that identical data encrypted with the same key will result in different ciphertexts.

### Summary of the Workflow:

- **PIN** with salt → **PBKDF2** → Produces **KEK** and **KEIV**.
- **KEK** + **KEIV** → **ChaCha20Poly1305** to decrypt **EDEK** → Produces **DEK**.
- **DEK** is used for encrypting and decrypting sensitive data entries in flash storage.
- **PVC** verifies whether the correct PIN was used for the entire process.

------

## Backup

### BIP-32, BIP-39, and BIP-44 Standards

To make backup and restoration on a new wallet easier, Trezor implements several known standards. They are also at the origin of some of them (BIP-39 & BIP-44)

- **[BIP-32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)**: Enables the creation of **hierarchical deterministic (HD) wallets**, which allow users to derive multiple private and public keys from a single seed.
- **[BIP-39](https://en.bitcoin.it/wiki/BIP_0039)**: Governs the creation of mnemonic seed phrases for easy wallet backups.
- **[BIP-44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki)**: Allows for managing multiple cryptocurrency accounts from a single seed phrase, ensuring compatibility across different blockchain networks.

The derivation path used in BIP44 follows this structure: 

` m / purpose' / coin_type' / account' / change / address_index`

Thanks to `address_index`, you can have several different addresses for the same account, which is not possible with Ethereum

See [Trezor - What is BIP44?](https://trezor.io/learn/a/what-is-bip44?srsltid=AfmBOopiSIUJDwPISXP5YbzFws1lFEToUwG52ITiM1Y72akbpyvNp8it)

To understand how an address is generated in bitcoin you can read my article: [Bitcoin Keys 101 - From seed phrase to address](https://rya-sge.github.io/access-denied/2024/10/28/bitcoin-keys-101/)

### Multi-share Backup

To perform a multi-share backup, SatoshiLabs has written its own proposal [SLIP39](https://github.com/satoshilabs/slips/blob/master/slip-0039.md) to implement a multi-share backup with **Shamir’s Secret-Sharing**

SLIP39  is a multi-party alternative to Bitcoin Improvement Proposal [BIP39](https://trezor.io/learn/a/what-is-bip39).

This advanced backup method splits your w**allet backup** (recovery seed) into multiple parts, called **shares**, and requires a minimum number of these, the **threshold**, to restore the wallet.

By distributing these shares between different locations and/or trusted individuals, you can significantly reduce the risk of *total* loss or theft. 

=> Even if some shares are lost, your wallet remains secure as long as the threshold number of shares is intact. 

=> Moreover, if some shares fall into the wrong hands, your wallet is still secure as long as less than the threshold number of shares are compromised.

You can fin more information about Shamir's Secret Sharing in my article [MPC - Shamir Secret-Sharing](https://rya-sge.github.io/access-denied/2024/10/21/mpc-protocol-overview/#secret-sharing)

Main reference: [Trezor - Slip39](https://content.trezor.io/slip39)

------

## Model specificity

This section describes the specific features of certain models

### On-Device entry

The [Trezor Model One](https://trezor.io/trezor-model-one) uses a blind matrix for PIN entry -- when required, a matrix of **dots** (instead of numbers) appears on your computer screen

Contrary to the Trezor model One, the PIN for model 3, 5 and T is directly entered by tapping on the touchscreen of your Trezor Model

Here some images from the Trezor website to compare:

- Model One

![trezor-model-one]({{site.url_complet}}/assets/article/blockchain/wallet/trezor/trezor-model-one.png)

- Model T

![trezor-model-t]({{site.url_complet}}/assets/article/blockchain/wallet/trezor/trezor-model-t.png)

Reference: [Trezor - PIN protection on Trezor devices](https://trezor.io/learn/a/pin-protection-on-trezor-devices)



### Chips and Secure Element

The Trezor Safe 5 and Safe 3 reinforce the security by using a Secure Element, certified CC EAL6+. 

#### About the chips

The chips used is the OPTIGA™ Trust M (V3). 

Contrary to the firmware, the code is not open source, but the producer does not restrict Trezor from freely publishing potential vulnerabilities.

#### About the certification

A chips EAL-6 means that the chips has been Semiformally Verified Design and Tested. Additional Security Considerations.

Compared to EAL-5 certification, this certification requires:

- more comprehensive analysis,
-  a structured representation of the implementation, 
- more architectural structure (e.g. layering), 
- more comprehensive independent vulnerability analysis 
- and improved configuration management and development environment controls.

More information on the Trezor website [Secure Element in Trezor Safe Devices](https://trezor.io/learn/a/secure-element-in-trezor-safe-devices)

Reference:[commoncriteriaportal.org, p.22](https://www.commoncriteriaportal.org/files/ccfiles/CC2022PART5R1.pdf), [web archive - CESG.gov.uk ](https://web.archive.org/web/20041012181256/http://www.cesg.gov.uk/site/iacs/index.cfm?menuSelected=1&displayPage=13)

See also [Ledger - What is Security Certification?](https://www.ledger.com/academy/security/the-importance-of-certification)

#### Trezor Safe device authentication check

The Secure Element plays an important role in verifying the authenticity of your device.

1. Trezor Suite generates a random challenge which is then sent to the Trezor.
2. In response, the Trezor uses the Secure Element to sign this random challenge and returns both the signature and the device certificate.
3. To confirm the authenticity of the device, Trezor Suite verifies the signatures of the challenge and the signature on the certificate.

![trezor-secure-element]({{site.url_complet}}/assets/article/blockchain/wallet/trezor/trezor-secure-element.png)

During the manufacturing process of the Trezor Safe hardware wallets, a unique certificate is issued to the new device before it leaves the production line. This certificate is stored in the Secure Element. 

Reference: [Trezor - Trezor Safe device authentication check](https://trezor.io/learn/a/trezor-safe-device-authentication-check)

### Encrypt PIN with MicroSD card

Trezor allows also to encrypt your [PIN](https://trezor.io/learn/a/pin-protection-on-trezor-devices) using a microSD card for the Trezor Model T and Trezor Safe 5. 

This provides extra protection against physical attacks.

When enabled, a randomly-generated secret is stored on the microSD card.

 When checking your PIN or using your PIN to unlock your Trezor, this secret is combined with the PIN to decrypt data stored on the device (note: with which algorithm?). 

As a result, the device gets 'bound' to the microSD card, and cannot be unlocked without it until you intentionally disable the feature or factory-reset your device.

Reference: [Trezor - Encrypt PIN with MicroSD card](https://trezor.io/learn/a/encrypt-pin-with-microsd-card?srsltid=AfmBOorwzwQVVwkOQHzutC5PezE_Ghbq3CRdoBchOu9-PQFVt_0-H-zw)



## Additional Security Considerations

### 1. Physical Security

While Trezor hardware wallets are robust, they are not impervious to **physical attacks** if a device falls into the wrong hands. 

However, a Trezor wallet is protected by the `PIN`, and the `passphrase` if set. 

The passphrase feature is especially useful because it creates an additional level of obfuscation, meaning even if someone manages to steal your device and get your PIN, they cannot access your funds without the passphrase.

Moreover, this passphrase is not stored inside the device, therefore if someone manages to break physically your Trezor Wallet (e.g. with a side-channel attack), they can not access the funds if they don't manage to find the passphrase.

### 2. Supply Chain Attacks

To address concerns over possible **supply chain attacks** (where the hardware is tampered with before it reaches the user), Trezor implements  several measures:

- Seal on the device or the package. Users are encouraged to inspect the device for any signs of tampering, such as broken seals (**Tamper-evident** packaging). 
- A legitimate device will always arrive without firmware installed. The bootloader verifies that the firmware you install has been signed by SatoshiLabs (=secure boot).
  - Thus users can verify the authenticity of the firmware when initializing the device.

- Since 2022, individual chips are now glued onto the board

#### Trezor Safe device authentication check

As indicated in the previous paragraph dedicated to the Secure Element. Trezor Sage 3 and Safe 5 uses it to help to verify the authenticity of the Trezor Safe 3 or Safe 5, and makes it significantly more difficult for it to be tampered with. 

Reference: [Trezor - Trezor Safe device authentication check](https://trezor.io/learn/a/trezor-safe-device-authentication-check)

------

## Past attack and vulnerabilities

### Supply Chain Attack

Fake Trezor sold on the Russia Market through a popular website: Modification performed by the attacker(s):

- They install a malicious firmware in the device
- They removed the bootloader-checks to avoid detection at startup.
- They replace the randomly generated seed phrase with a pre-generated seed phrase saved in the malicious firmware. 
- This is the reason why chips are now glued on the board to make modifications more complicated:

Reference: [Kaspersky.com - Case study: fake hardware cryptowallet](https://www.kaspersky.com/blog/fake-trezor-hardware-crypto-wallet/48155/), [Trezor - Stay safe shopping for hardware wallets](https://blog.trezor.io/stay-safe-shopping-for-hardware-wallets-543f144e3d24)

### Side-channel attack

In the past, several side-channel attacks have been performed on Trezor wallets, notably:

-  [Wallet.fail](https://www.youtube.com/watch?v=Y1OBIGslgGM) (2018)

- [Ledger ](https://www.ledger.com/blog/breaking-trezor-one-with-sca)(2018-2019)

#### Ledger Donjon Team

Ledger identified several side-channel attacks on the Trezor Model One.

One concerned the PIN verification allowing an attacker with a stolen Trezor One to retrieve the correct value of the PIN within a few minutes.

In the first versions of the Trezor Model One, the Pin verification was done like this:

![Trezor code](https://ledger-wp-website-s3-prd.ledger.com/uploads/2024/03/pincode.png)

As indicated by Ledger:

The subtraction operation *storageRom->pin[i] — presented_pin[i]* contains 

- The secret PIN value 
- The user input value

Thus, a side-channel attack is possible to induce differentiability. The Ledger Donjon Team measured the power consumption of the device, then they used Machine Learning to determine the most likely candidate for *storageRom->pin.*

These vulnerabilities have led Satoshi Labs, the company behind the wallet, to propose a more robust version to encrypt the data stored in the device. This new version is the current version shown with the Data encryption Diagram above.

#### Kraken Security Labs

Despite this new architecture, Kraken in 2020, managed to perform a fault injection attack on the device  to extract the entire flash-contents of the microcontroller’s flash memory

- Since Trezor firmware uses encrypted storage, they developed a script to crack the PIN of the dumped device.

- The script was able to brute force any 4-digit pin in under two minutes.
- As a reminder, a PIN brute-force is not directly possible directly on the device, because the storage is automatically wipes after 16 unsuccessful attempts.
- To protect against this, Satoshi Labs answered, also in 2020, in a [article](https://blog.trezor.io/our-response-to-the-read-protection-downgrade-attack-28d23f8949c6) that the best solution is to set a long PIN (against the brute-force attack) and set a passphrase since the passphrase is not set in the device.

Reference:

[Kraken Identifies Critical Flaw in Trezor Hardware Wallets](https://blog.kraken.com/product/security/kraken-identifies-critical-flaw-in-trezor-hardware-wallets), [Trezor - Our Response to the Read Protection Downgrade Attack](https://blog.trezor.io/our-response-to-the-read-protection-downgrade-attack-28d23f8949c6)

![trezor-fault-injection-protection]({{site.url_complet}}/assets/article/blockchain/wallet/trezor/trezor-fault-injection-protection.png)

## Conclusion

Trezor wallets are designed with a robust set of security features with a strong use of cryptography (PBKDF2 with HMAC-SHA256, ChaCha20-Poly1305, ) to protect sensitive information such as the seed phrase against several different attack:

![trezor-Trezor-threat-protection.drawio]({{site.url_complet}}/assets/article/blockchain/wallet/trezor/trezor-Trezor-threat-protection.drawio.png)

The fact that the firmware is open source is also a strong point in their favor.

All these features make them one of the most trusted hardware wallets in the cryptocurrency space.

## References

- Official website [trezor.io](https://trezor.io)
  - [Trezor - Compare](https://trezor.io/compare)
  - [Secure Element in Trezor Safe Devices](https://trezor.io/learn/a/secure-element-in-trezor-safe-devices)
  - [Trezor - How to use a recovery seed](https://trezor.io/learn/a/how-to-use-a-recovery-seed)
  - [Trezor - Trezor Safe device authentication check](https://trezor.io/learn/a/trezor-safe-device-authentication-check)
  - [Security & safety in Trezor ](https://trezor.io/learn/a/security-safety-in-trezor?srsltid=AfmBOoo-zyONXBVPkTbfQ1r552tSE6H8g2FruZ5JFBbCayxHWeTcCYg8)
  - [trezor - PIN protection on Trezor devices ](https://trezor.io/learn/a/pin-protection-on-trezor-devices), [Trezor suite protection against keyloggers?](https://forum.trezor.io/t/trezor-suite-protection-against-keyloggers/6386)
- Supply-chain attack
  - [Kaspersky.com - Case study: fake hardware cryptowallet](https://www.kaspersky.com/blog/fake-trezor-hardware-crypto-wallet/48155/)
  - [Trezor - Stay safe shopping for hardware wallets](https://blog.trezor.io/stay-safe-shopping-for-hardware-wallets-543f144e3d24)
- Side-channel attack:
  - [Wallet.fail](https://www.youtube.com/watch?v=Y1OBIGslgGM) (2018)
  - [BREAKING TREZOR ONE WITH SIDE CHANNEL ATTACKS](https://www.ledger.com/blog/breaking-trezor-one-with-sca)
  - [Kraken Identifies Critical Flaw in Trezor Hardware Wallets](https://blog.kraken.com/product/security/kraken-identifies-critical-flaw-in-trezor-hardware-wallets)
  - [Trezor - Our Response to the Read Protection Downgrade Attack](https://blog.trezor.io/our-response-to-the-read-protection-downgrade-attack-28d23f8949c6)
- ChatGPT
  - 
