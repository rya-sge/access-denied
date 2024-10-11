## **Trezor Crypto Wallet Security: An In-Depth Review**

Hardware wallets are physical devices that store private keys offline. 

A **hardware wallet** is one of the most trusted tools for safeguarding cryptocurrencies yourself (self-custodial), providing robust security by keeping your private keys offline and away from online threats, protecting them from hacking and malware.

Among the most popular and trusted hardware wallets for storing digital assets securely is **Trezor**, a product developed by SatoshiLabs. 

Trezor offers several different models, —Trezor One and Trezor Model T for example—each designed to provide users with a high level of protection for their cryptocurrency holdings. 

This article presents the different security features availabe, how your private key are protected, ...

This article explores the key security features of Trezor wallets, the cryptographic algorithms they utilize,

Firstly here a summary of the different option available depending of the models.

| Model                                                        | Seed phrase backup               |  | Device Security       |         | Authentication                             |                              |
| ------------------------------------------------------------ | -------------------------------- | ------------------ | --------------------------- | ------------------------------------------ | ------- | ------- |
|                                                                              | &#x2611; | Multi Share |Pin & passphrase protection|Secure element|Two-factor authentication|FIDO2 Standard|
| [Trezor Model T](https://trezor.io/trezor-model-t)           | &#x2611; | &#x2611;        | &#x2611; |  | &#x2611; | &#x2611; |
| [Trezor Model One](https://trezor.io/trezor-model-one)       | &#x2611; | &#x2612;         | &#x2611; |  | &#x2611;       | &#x2612; |
| [Trezor Safe 3](https://trezor.io/trezor-safe-3-cosmic-black) | &#x2611; | &#x2611;        | &#x2611; |  | &#x2611; | &#x2611; |
| [Trezor Safe 5](https://trezor.io/trezor-safe-5)             | &#x2611; | &#x2611;        | &#x2611; |  | &#x2611; | &#x2611; |



### **Core Security Features of Trezor Wallets**

#### 1. **Offline Private Key Storage**

The cornerstone of Trezor’s security is the **offline storage** of private keys. Since Trezor is a hardware wallet, your private keys never leave the device, ensuring that they are not exposed to the internet. This **air-gapped** design protects against hacking attempts, phishing attacks, and malware, which are common on internet-connected (hot) wallets.

#### 2. **PIN Protection**

Every Trezor wallet requires a **PIN code** to access the device. This PIN is set by the user during initialization and is a critical layer of protection against unauthorized physical access. The PIN entry process is randomized on the Trezor screen, making it resistant to keylogging or screen capture attacks that can occur on compromised computers.

References: [trezor - PIN protection on Trezor devices ](https://trezor.io/learn/a/pin-protection-on-trezor-devices), [Trezor suite protection against keyloggers?](https://forum.trezor.io/t/trezor-suite-protection-against-keyloggers/6386)

#### 3. **Passphrase Support**

In addition to a PIN, Trezor provides the option to add an additional layer of security in the form of a **passphrase**. This passphrase essentially acts as a 25th word added to the standard 24-word recovery seed. 

A passphrase has two main purpose:

- Even if someone gains access to the recovery seed, without knowing the passphrase, they will not be able to recover the wallet. 
- Add your own entropy: even if there is a vulnerability in the random generation by the wallet, it will not possible to recover the wallet without the passphrase.

The wallet obtained by adding a passphrase is called a `hidden wallet`
$$
recovery~seed + passphrase = hidden~ wallet
$$
Reference: [Trezor - Passphrases and hidden wallets](https://trezor.io/learn/a/passphrases-and-hidden-wallets)

#### 4. **Recovery Seed**

When you initialize your Trezor wallet, you are provided with a **recovery seed**, which is a randomly generated 12-24 word phrase. This seed allows you to restore your wallet in case the device is lost or damaged. The seed is generated offline, and the user must write it down in a secure place, as it is the only way to recover the funds. Trezor implements a **BIP-39** mnemonic phrase standard for this recovery seed.

References: [Trezor - How to use a recovery seed](https://trezor.io/learn/a/how-to-use-a-recovery-seed)

#### 5. **Firmware Updates**

Trezor regularly releases **firmware updates** to fix bugs, patch vulnerabilities, and add new features. There are several protection to avoid a malicious updates:

- These updates require user confirmation via the device’s screen, preventing unauthorized or malicious firmware installations. 
- The firmware is also **signed** by SatoshiLabs, ensuring the authenticity of the update before installation.
- Downgrading the firmware, which could be used to install a vulnerable version of Trezor,  erases the memory as a result.

Reference: [Security & safety in Trezor ](https://trezor.io/learn/a/security-safety-in-trezor?srsltid=AfmBOoo-zyONXBVPkTbfQ1r552tSE6H8g2FruZ5JFBbCayxHWeTcCYg8)

# Trezor's encryption Key terms

https://docs.trezor.io/trezor-firmware/storage/index.html#pin-verification-and-decryption-of-protected-entries-in-flash-storage

[PIN verification and decryption of protected entries in flash storage](https://docs.trezor.io/trezor-firmware/storage/index.html#pin-verification-and-decryption-of-protected-entries-in-flash-storage)

![trezor-pin-diagram-activity](/home/ryan/Downloads/me/access-denied/assets/article/cryptographie/wallet/trezor-pin-diagram-activity.png)



Here's an explanation of the key terms used in Trezor's encryption and PIN verification process:

### 1. **KEK (Key Encryption Key)**

- **What it is**: The **KEK** is a 256-bit key derived from the user’s PIN and a salt using the **PBKDF2** algorithm.

KEK || KEIV = *PBKDF2(PRF = HMAC-SHA256, Password = pin, Salt = salt, iterations = 10000, dkLen = 352 bits)*

- **Purpose**: It is used to **decrypt the Encrypted Data Encryption Key (EDEK)**, allowing access to the actual Data Encryption Key (DEK).
- **How it works**: The KEK is part of a layered security approach: instead of encrypting data directly with the PIN, Trezor derives the KEK from the PIN to ensure additional protection. This is notably useful against [fault injection attacks](https://www.dekra.com/en/fault-injection-attacks/).
- This means an attacker would need the KEK, derived from a valid PIN, to access the encrypted key (EDEK).

### 2. **KEIV (Key Encryption Initialization Vector)**

- **What it is**: The **KEIV** is a 96-bit value derived alongside the KEK using the **PBKDF2** algorithm.
- **Purpose**: It is used as an **initialization vector (IV)** for the encryption algorithm **ChaCha20Poly1305**, which helps ensure that even if the same key (KEK) is reused, the output will be different by combining it with the KEIV.
- **How it works**: The KEIV ensures that the encryption process is randomized and secure, so that identical data encrypted with the same key will result in different ciphertexts.

### 3. **DEK (Data Encryption Key)**

- **What it is**: The **DEK** is the actual key used to **encrypt and decrypt protected data** stored in flash storage.
- **Purpose**: The DEK protects sensitive data entries in the device’s flash memory. It is derived by decrypting the **EDEK** with the KEK and KEIV.
- **How it works**: The DEK is used to encrypt and decrypt specific entries (e.g., secrets, settings) in the storage. Without the correct DEK, these entries cannot be read or tampered with.

### 4. **PVC (PIN Verification Code)**

- **What it is**: The **PVC** is a **64-bit code** stored in the flash memory and used to verify if the correct PIN was used during decryption.
- **Purpose**: It serves as a **verification mechanism** to ensure the PIN entered by the user is correct. After the EDEK is decrypted, the PVC is compared with a tag value derived during the decryption process.
- **How it works**: If the PVC matches the computed tag, it confirms that the decryption was performed using the correct PIN. If the PVC doesn’t match, the decryption fails, indicating an incorrect PIN.
- Remark from the trezor documentation: The 64 bit PVC means that there is less than a 1 in 1019 chance that a wrong PIN will happen to have the same PVC as the correct PIN. The existence of false PINs does not pose a security weakness since a false PIN cannot be used to decrypt the protected entries.

### 5. **PBKDF2 (Password-Based Key Derivation Function 2)**

- **What it is**: **PBKDF2** is a key derivation function that uses a password (in this case, the PIN), a salt (a random value), and multiple iterations of a cryptographic hash function to generate a derived key.
- **Purpose**: It is used to transform the user's **PIN** into a **strong cryptographic key** (in this case, the KEK and KEIV). The function also incorporates a salt to prevent precomputed attacks (such as rainbow tables).
- **How it works**: PBKDF2 uses the user's PIN as input and combines it with a salt derived from hardware identifiers (e.g., ProcessorID) and the random salt from flash storage. It runs the hash function (HMAC-SHA256) for 10,000 iterations (or more), producing 352 bits of output: the first 256 bits become the **KEK** and the last 96 bits form the **KEIV**.
- HMAC-SHA256: Hash-based Message Authentication Code)

### 6. **ChaCha20Poly1305**

- **What it is**: **ChaCha20Poly1305** is a **symmetric encryption algorithm** that provides both encryption and authentication in a single operation.

- **Purpose**: It is used to **encrypt and decrypt data securely**, ensuring both confidentiality and integrity of the data. In Trezor, it is used to encrypt the **EDEK** and the protected entries stored in the flash.

- How it works:

  - **ChaCha20** is the encryption part, which transforms plaintext data into ciphertext using a key (e.g., KEK or DEK) and an IV (like the KEIV or entry IV).
  - **Poly1305** is the authentication part, which generates a **tag** (a type of checksum) that ensures the data hasn’t been tampered with. The tag is checked during decryption to verify the data's integrity.
  
- This ensures that even if an attacker modifies the encrypted data or its associated metadata (like the IV), the decryption process will fail due to a tag mismatch.

### Summary of the Workflow:

- **PIN** with salt → **PBKDF2** → Produces **KEK** and **KEIV**.
- **KEK** + **KEIV** → **ChaCha20Poly1305** to decrypt **EDEK** → Produces **DEK**.
- **DEK** is used for encrypting and decrypting sensitive data entries in flash storage.
- **PVC** verifies whether the correct PIN was used for the entire process.



#### 3. **HMAC-SHA512 for Password Stretching**

When encrypting passwords or keys, Trezor uses **HMAC-SHA512** to “stretch” passwords, which makes brute-force attacks more difficult. HMAC  adds an extra layer of security when handling cryptographic keys, making it harder for attackers to recover the seed phrase or private keys from device data.

#### 4. **BIP-32, BIP-39, and BIP-44 Standards**

Trezor follows industry-standard protocols, such as:

- **BIP-32**: Enables the creation of **hierarchical deterministic (HD) wallets**, which allow users to derive multiple private and public keys from a single seed.
- **BIP-39**: Governs the creation of mnemonic seed phrases for easy wallet backups.
- **BIP-44**: Allows for managing multiple cryptocurrency accounts from a single seed phrase, ensuring compatibility across different blockchain networks.

### **Trezor One vs. Trezor Model T: A Security Comparison**

Trezor offers two primary models: **Trezor One** and **Trezor Model T**, both sharing core security features but differing in their user experience and some advanced features.

#### 1. **Trezor One**

- **Security:** Provides robust security through features like PIN protection, recovery seed, and offline storage of private keys.
- **Interface:** Trezor One has a **two-button interface** and a small monochrome screen, making it functional but minimalistic.

- 

### **Additional Security Considerations**

#### 1. **Physical Security**

While Trezor hardware wallets are robust, they are not impervious to **physical attacks** if a device falls into the wrong hands. However, the PIN, and the passphrase i set. The passphrase feature is especially useful because it creates an additional level of obfuscation, meaning even if someone manages to steal your device and get your PIN, they cannot access to your funds without the passphrase.

#### 2. **Supply Chain Attacks**

To address concerns over possible **supply chain attacks** (where the hardware is tampered with before it reaches the user), Trezor implements **tamper-evident packaging**. Users are encouraged to inspect the device for any signs of tampering, such as broken seals. Additionally, users can verify the authenticity of the firmware when initializing the device.

### **Conclusion**

Trezor wallets are designed with a robust set of security features that make them one of the most trusted hardware wallets in the cryptocurrency space.
