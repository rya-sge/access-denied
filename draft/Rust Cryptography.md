# Rust Cryptography

## Transport Encryption Libraries

| Library                                                      | Description                                                  | Audited                                                      | Post-Quantum Secure                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | --------------------------------------------------------- |
| [rustls](https://github.com/ctz/rustls)                      | Modern TLS/SSL library written in Rust; used in many production systems. | ✅ Yes<br />[(2020)](https://github.com/rustls/rustls/tree/main/audit) | ❌ No (uses traditional elliptic curve & RSA cryptography) |
| [snow](https://github.com/mcginty/snow)                      | Pure Rust implementation of the Noise Protocol Framework for encrypted peer-to-peer messaging. | ❌ No                                                         | ❌ No (typically uses Curve25519)<br />?                   |
| [strobe-rs](https://github.com/rozbb/strobe-rs)              | Minimalist implementation of the Strobe symmetric protocol framework in `no_std` Rust. | ❌ No                                                         | ✅ Yes (symmetric-only, PQ-safe primitives possible)       |
| [OpenMLS](https://github.com/openmls/openmls/) [MLS](https://datatracker.ietf.org/doc/draft-ietf-mls-protocol/) | Implementation of IETF's MLS protocol for secure group messaging (RFC 9420). | ✅ Partial (formal test vectors & conformance, not full audit) | ❌ No (uses elliptic curves like X25519)                   |
| **[webpki](https://github.com/briansmith/webpki)**           | Verifies Web PKI (TLS certificates) in Rust; used in conjunction with rustls. | ✅ Yes                                                        | ❌ No (validates traditional certs, not PQ certs)          |

**Notes:**

- **rustls** and **webpki** are widely deployed and audited but currently do not support post-quantum cryptographic primitives.
- **strobe-rs** is inherently **post-quantum secure** if used correctly, as it relies on symmetric primitives.
- **OpenMLS** is **not yet PQ-secure**, though PQ support is being discussed in future MLS extensions.

Would you like to move on to **Asymmetric Cryptography** next or perhaps **Post-Quantum Cryptography** itself?

## Secure Messaging Protocols

| Library             | Description                                                  | Audited                               | Post-Quantum Secure                           |
| ------------------- | ------------------------------------------------------------ | ------------------------------------- | --------------------------------------------- |
| **OpenMLS**         | Rust implementation of IETF MLS protocol (RFC 9420) with forward secrecy, deniable authentication, and post-compromise security. | ✅ Partial (tested, not fully audited) | ❌ No (uses X25519, traditional ECC)           |
| **mls-rs**          | Alternative Rust implementation of the MLS protocol, conformant to RFC 9420; suitable for secure group messaging. | ❌ No                                  | ❌ No                                          |
| **Matter protocol** | Secure message protocol for device communication (e.g., home automation), with built-in encryption and authentication. | ❌ No                                  | ❌ No (uses standard cryptographic primitives) |
| **vodozemac**       | Implements Olm & Megolm ratchets (used in Matrix); enables end-to-end encryption with forward secrecy and post-compromise security. | ✅ Yes (by Least Authority)            | ❌ No (Curve25519-based, not PQ)               |



**Notes:**

- All current secure messaging libraries listed **do not use post-quantum secure key exchange** or encryption primitives.
- **vodozemac** is the only one in this list to have undergone a **formal security audit**.
- **MLS** protocol family (OpenMLS, mls-rs) is designed with modern security guarantees, but **PQ-secure variants are not yet standard**.

------



## Collections of Cryptographic Primitives

| Library            | Description                                                  | Audited | Post-Quantum Secure |
| ------------------ | ------------------------------------------------------------ | ------- | ------------------- |
| **evercrypt-rust** | Rust bindings for evercrypt, a high-performance, HACL*-verified implementation of cryptographic primitives. | ✅ Yes   | ❌ No                |
| **libsm**          | China’s Standards of Encryption Algorithms (SM2/3/4), providing cryptographic algorithms defined by China’s government standards. | ❌ No    | ❌ No                |
| **orion**          | Collection of usable, safe, and pure-Rust cryptographic primitives. | ✅ Yes   | ❌ No                |
| **ring**           | High-performance cryptographic library focusing on a core set of cryptographic operations with easy-to-use API. | ✅ Yes   | ❌ No                |
| **themis**         | Cross-platform cryptographic library for securing data during authentication, storage, messaging, and network exchange. | ✅ Yes   | ❌ No                |
| **dryoc**          | Pure-Rust, general-purpose crypto library that implements libsodium primitives. | ✅ Yes   | ❌ No                |



------



### Authenticated Encryption with Associated Data (AEAD) Algorithms

| Library                                                      | Description                                                  | Audited |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------- |
| **aes-gcm**                                                  | Pure Rust implementation of the AES-GCM AEAD cipher.         | yes     |
| [aes-gcm-siv](https://github.com/RustCrypto/AEADs/tree/master/aes-gcm-siv) | AES-GCM-SIV (RFC 8452) is a high-performance Authenticated Encryption with Associated Data (AEAD) cipher which also provides nonce reuse misuse resistance. |         |
| [aes-siv](https://github.com/RustCrypto/AEADs/tree/master/aes-siv) | AES-SIV Misuse-Resistant Authenticated Encryption Cipher.    |         |
| [ascon-aead](https://github.com/RustCrypto/AEADs/tree/master/ascon-aead) | Pure Rust implementation of the Ascon Authenticated Encryption with Associated Data (AEAD) cipher, including implementations of the Ascon-128 and Ascon-128a variants. |         |
| [ccm](https://github.com/RustCrypto/AEADs/tree/master/ccm)   | Pure Rust implementation of the Counter with CBC-MAC (CCM) mode (RFC 3610): an Authenticated Encryption with Associated Data (AEAD) algorithm generic over block ciphers with block size equal to 128 bits. |         |
| **chacha20poly1305**                                         | Pure Rust implementation of ChaCha20Poly1305 AEAD cipher, optimized for constant-time performance. | yes     |
| **deoxys**                                                   | Pure Rust implementation of Deoxys AEAD cipher, including CAESAR competition's Deoxys-II. | ❌ No    |
| aex                                                          | Pure Rust implementation of the EAX Authenticated Encryption with Associated Data (AEAD) cipher. | ❌ No    |



Hash functions

## ash Functions and Friends

| Library              | Description                                                  | Audited | Post-Quantum Secure                            |
| -------------------- | ------------------------------------------------------------ | ------- | ---------------------------------------------- |
| **ascon-hash**       | Pure Rust implementation of the Ascon hash and extendable output function (XOF), includes Ascon-128 and 128a. | ❌ No    | ✅ Yes (lightweight, NIST finalist)             |
| **BLAKE2**           | Pure Rust implementation of the BLAKE2 hash function family. | ❌ No    | ✅ Yes*                                         |
| **BLAKE3**           | Official implementation of the BLAKE3 cryptographic hash function. | ❌ No    | ✅ Yes*                                         |
| **HKDF**             | HMAC-based Extract-and-Expand Key Derivation Function (HKDF) for Rust. | ❌ No    | ✅ Yes* (depends on hash)                       |
| **MACs**             | Pure Rust collection of Message Authentication Code algorithms including CMAC, HMAC, and PMAC. | ❌ No    | ✅ Yes* (depends on underlying hash)            |
| **Poseidon252**      | Reference implementation of the Poseidon Hashing algorithm.  | ❌ No    | ✅ Yes (ZK-friendly)                            |
| **RIPEMD160**        | Pure Rust implementation of the RIPEMD160 hash function.     | ❌ No    | ❌ No                                           |
| **SHA-2**            | Pure Rust implementation of SHA-2 family including SHA-224, SHA-256, SHA-384, SHA-512. | ❌ No    | ✅ Yes*                                         |
| **SHA-3**            | Pure Rust implementation of the SHA-3 (Keccak) hash function. | ❌ No    | ✅ Yes (standardized by NIST for PQ resistance) |
| **universal-hashes** | Collection of Universal Hash Functions in Rust including GHASH, POLYVAL, and Poly1305. | ❌ No    | ✅ Yes* (when used properly)                    |

## Password hashing

| Library         | Description                                                  | Audited | Post-Quantum Secure                                       |
| --------------- | ------------------------------------------------------------ | ------- | --------------------------------------------------------- |
| **argon2**      | Pure Rust implementation of the Argon2 password hashing function. | ❌ No    | ✅ Yes (memory-hard, not broken by quantum)                |
| **bcrypt**      | Pure Rust implementation of the bcrypt password hashing function. | ❌ No    | ❌ No (vulnerable to Grover's algorithm and legacy design) |
| **pbkdf2**      | Pure Rust implementation of the Password-Based Key Derivation Function v2 (PBKDF2). | ❌ No    | ❌ No (low iteration count + not memory-hard)              |
| **phpass**      | Pure Rust implementation of the PhPass algorithm used by WordPress. | ❌ No    | ❌ No (designed before PQ threat awareness)                |
| **pkcs5**       | Implements PBKDF2 and scrypt under the PKCS#5 standard.      | ❌ No    | ✅ Mixed (PBKDF2 ❌, scrypt ✅)                              |
| **rust-argon2** | Rust library for Argon2 (PHC winner) password hashing.       | ❌ No    | ✅ Yes                                                     |
| **scrypt**      | Pure Rust implementation of the scrypt key derivation function. | ❌ No    | ✅ Yes (memory-hard)                                       |



**Notes:**

- PQ-safe password hashing ≠ encryption: it means resistant to quantum brute-force due to memory hardness or other cost factors.
- Argon2 and scrypt are **recommended** over legacy methods (e.g. PBKDF2, bcrypt) for modern, quantum-resilient systems.



##  Zero-Knowledge Proofs

| Library          | Description                                                  | Audited                               | Post-Quantum Secure                    |
| ---------------- | ------------------------------------------------------------ | ------------------------------------- | -------------------------------------- |
| **arkworks**     | Ecosystem for building and using zkSNARKs, supports modular and efficient cryptographic components. | ❌ No                                  | ❌ No (uses pairing-based SNARKs)       |
| **bellman**      | zkSNARK circuit construction library, used in Zcash (Groth16-based). | ✅ Yes (via Zcash)                     | ❌ No                                   |
| **bellman-ce**   | Fork of Bellman with Ethereum’s BN256 support.               | ❌ No                                  | ❌ No                                   |
| **bellperson**   | GPU-accelerated fork of Bellman for zkSNARKs (Groth16) used in Filecoin. | ✅ Yes (used in Filecoin)              | ❌ No                                   |
| **bulletproofs** | Pure Rust implementation of Bulletproofs using Ristretto.    | ❌ No                                  | ❌ No (depends on ECC)                  |
| **bulletproof**  | Implementation of Bulletproofs+ and aggregated range proofs. | ❌ No                                  | ❌ No                                   |
| **Dusk-Zerocaf** | Ristretto-embedded curve operations for ZK applications.     | ❌ No                                  | ❌ No                                   |
| **merlin**       | Transcript framework for non-interactive zero-knowledge protocols (e.g. Fiat-Shamir). | ✅ Yes (used in multiple ZK protocols) | ✅ Yes* (depends on usage)              |
| **OpenZKP**      | Collection of ZKP systems in Rust.                           | ❌ No                                  | ❌ No (legacy SNARKs)                   |
| **snarkVM**      | Implementation of Zexe model for decentralized private computation with zkSNARKs. | ❌ No                                  | ❌ No                                   |
| **Spartan**      | High-speed zkSNARKs with no trusted setup, based on multilinear polynomial commitments. | ✅ Yes (academic origin)               | ❌ No                                   |
| **winterfell**   | Distributed STARK prover for scalable ZK systems.            | ❌ No                                  | ✅ Yes (STARKs are post-quantum secure) |
| **ZoKrates**     | Toolbox for generating and verifying zkSNARKs on Ethereum.   | ❌ No                                  | ❌ No                                   |
| **zkp**          | Macro-based ZKP compiler for Schnorr-style proofs.           | ❌ No                                  | ❌ No (depends on ECC)                  |

**Notes:**

- ✅ Yes (PQS) = **STARKs** (like Winterfell) are widely regarded as post-quantum secure due to reliance on hashes, not elliptic curves.
- ✅ Yes* = Tools like **Merlin** are protocol-agnostic and may be part of PQ-secure systems if used with post-quantum primitives.
- Most zkSNARKs are **not** post-quantum secure due to their use of pairing-based cryptography or elliptic curves.



## Secure Multiparty Computation

| Library         | Description                                                  | Audited | Post-Quantum Secure                                          |
| --------------- | ------------------------------------------------------------ | ------- | ------------------------------------------------------------ |
| **libpaillier** | Rust implementation of the Paillier cryptosystem supporting additive homomorphism. | ❌ No    | ❌ No (based on RSA-like assumptions)                         |
| **swanky**      | Suite of libraries for secure multi-party computation protocols including garbled circuits, OT, etc. | ❌ No    | ✅ Partial (PQ security depends on underlying primitives used) |
| **white-city**  | API and framework to integrate distributed networks for secure computation. | ❌ No    | ✅ Partial (design may support PQ schemes, but not guaranteed) |



------

**Notes:**

- MPC protocols can **support post-quantum security**, but it's **highly dependent** on the primitives they use (e.g., PQ key exchange, commitments).
- None of these libraries are confirmed to have undergone formal **security audits**.
- **libpaillier** is not post-quantum secure due to its reliance on factoring-based cryptography.



------

## 🔄 Hash Functions

| Library    | Description                                                  | Audited |
| ---------- | ------------------------------------------------------------ | ------- |
| **BLAKE3** | Official implementation of the BLAKE3 cryptographic hash function. | ❌ No    |
| **SHA-2**  | Pure Rust implementation of SHA-2 family: SHA-224, SHA-256, SHA-384, SHA-512. | ❌ No    |



------

## 🔑 Password Hashing Functions

| Library    | Description                                                  | Audited |
| ---------- | ------------------------------------------------------------ | ------- |
| **argon2** | Pure Rust implementation of the Argon2 password hashing function. | ❌ No    |
| **scrypt** | Pure Rust implementation of the scrypt key derivation function. | ❌ No    |



------

## 🔐 Asymmetric Cryptography

| Library              | Description                                                  | Audited |
| -------------------- | ------------------------------------------------------------ | ------- |
| **RSA**              | Pure Rust implementation of the RSA algorithm.               | ❌ No    |
| **curve25519-dalek** | Pure Rust group ops for Ristretto and Curve25519 elliptic curves. | ❌ No    |



------

## ✍️ Digital Signatures

| Library           | Description                                                  | Audited |
| ----------------- | ------------------------------------------------------------ | ------- |
| **ed25519-dalek** | Efficient Ed25519 keygen, signing, and verification in Rust. | ❌ No    |
| **schnorrkel**    | Schnorr signatures on Ristretto points, with VRF and other protocol support. | ❌ No    |



------

## 📩 Secure Messaging Protocols

| Library       | Description                                                  | Audited |
| ------------- | ------------------------------------------------------------ | ------- |
| **vodozemac** | Implements Olm and Megolm cryptographic ratchets. Audited by Least Authority with no major issues. | ✅ Yes   |





| Algorithm | Library                                                      |         |
| --------- | ------------------------------------------------------------ | ------- |
| RSA       |                                                              |         |
| ECDA      |                                                              |         |
| AES-GCM   | [aes-gcm](https://github.com/RustCrypto/AEADs/tree/master/aes-gcm) | audited |







| Algorithm |      |      |
| --------- | ---- | ---- |
| RSA       |      |      |
| ECDA      |      |      |
| AES-GCM   |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |
|           |      |      |





Hash

https://cryptography.rs