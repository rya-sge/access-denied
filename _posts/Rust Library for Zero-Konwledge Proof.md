# Rust Library for Zero-Konwledge Proof

This article presents a collection of Rust Library to work with Kero-Knowledge Proof



##  Zero-Knowledge Proofs

| Library                                                      | Maintener                                                   | Description                                                  | Public audit                                                 | Post-Quantum Secure                    |
| ------------------------------------------------------------ | ----------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | -------------------------------------- |
| **arkworks**                                                 |                                                             | Ecosystem for building and using zkSNARKs, supports modular and efficient cryptographic components. | ❌ No                                                         | ❌ No (uses pairing-based SNARKs)       |
| [Bellman](https://github.com/zkcrypto/bellman)**bellman**    |                                                             | zkSNARK circuit construction library, used in Zcash (Groth16-based). | ✅ Yes (via Zcash)<br <br />[Kuderlski - 2019](https://research.kudelskisecurity.com/wp-content/uploads/2018/08/zcash-audit.pdf/), | ❌ No                                   |
| **bellman-ce**                                               |                                                             | Fork of Bellman with Ethereum’s BN256 support.               | ❌ No                                                         | ❌ No                                   |
| **bellperson**                                               |                                                             | GPU-accelerated fork of Bellman for zkSNARKs (Groth16) used in Filecoin. | ✅ Yes (used in Filecoin)                                     | ❌ No                                   |
| [bulletproofs](https://github.com/dalek-cryptography/bulletproofs) |                                                             | Pure Rust implementation of Bulletproofs using Ristretto.    | yes<br />[Security Audit of dalek libraries](https://blog.quarkslab.com/security-audit-of-dalek-libraries.html)[quarkslab - 2019](https://blog.quarkslab.com/security-audit-of-dalek-libraries.html)https://blog.quarkslab.com/security-audit-of-dalek-libraries.html | ❌ No (depends on ECC)                  |
| [bulletproof](https://github.com/KZen-networks/bulletproofs) | ZenGO                                                       | Implementation of Bulletproofs+ and aggregated range proofs. | ❌ No                                                         | ❌ No                                   |
| [Dusk-Zerocaf](https://github.com/dusk-network/dusk-zerocaf) |                                                             | Ristretto-embedded curve operations for ZK applications.     | ❌ No<br />(Archive/WIP Repo)                                 | ❌ No                                   |
| [merlin](https://github.com/dalek-cryptography/merlin)       | [dalek-cryptography](https://github.com/dalek-cryptography) | Transcript framework for non-interactive zero-knowledge protocols (e.g. Fiat-Shamir). | no                                                           | ✅ Yes* (depends on usage)              |
| [OpenZKP](https://github.com/0xProject/OpenZKP)              | [0xProject](https://github.com/0xProject)                   | Collection of ZKP systems in Rust.                           | ❌ No<br />("*no* comprehensive security audit,")             | ❌ No (legacy SNARKs)                   |
| [SnarkVM](https://github.com/ProvableHQ/snarkVM)             | Navigation MenuProvableHq                                   | Implementation of Zexe model for decentralized private computation with zkSNARKs. | ❌ No                                                         | ❌ No                                   |
| [**Spartan**](https://github.com/microsoft/Spartan)          | Microsoft                                                   | High-speed zkSNARKs with no trusted setup, based on multilinear polynomial commitments. | No<br />("Note that this library has *not* received a security review or audit.") | ❌ No                                   |
| [winterfell](https://github.com/novifinancial/winterfell/)   | Facebook / Meta                                             | Distributed STARK prover for scalable ZK systems.            | ❌ No<br />("This is a research project. It has not been audited and may contain bugs and security flaws. This implementation is NOT ready for production use.") | ✅ Yes (STARKs are post-quantum secure) |
| [ZoKrates](https://github.com/Zokrates/ZoKrates)             | ZoKrate                                                     | Toolbox for generating and verifying zkSNARKs on Ethereum.   | ❌ No<br />("*This is a proof-of-concept implementation. It has not been tested for production.*") | ❌ No                                   |
| [zkp](https://github.com/dalek-cryptography/zkp)             | Dalek-Cryptography                                          | Macro-based ZKP compiler for Schnorr-style proofs  instantiated using the ristretto255 group. | ❌ No                                                         | ❌ No (depends on ECC)                  |

**Notes:**

- ✅ Yes (PQS) = **STARKs** (like Winterfell) are widely regarded as post-quantum secure due to reliance on hashes, not elliptic curves.
- ✅ Yes* = Tools like **Merlin** are protocol-agnostic and may be part of PQ-secure systems if used with post-quantum primitives.
- Most zkSNARKs are **not** post-quantum secure due to their use of pairing-based cryptography or elliptic curves.

