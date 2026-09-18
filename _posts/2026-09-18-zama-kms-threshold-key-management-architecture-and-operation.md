---
layout: post
title: "Inside the Zama KMS — Threshold Key Management for FHE, From MPC Protocol to Enclave Deployment"
date:   2026-09-18
lang: en
locale: en-GB
categories: blockchain cryptography security
tags: zama fhe fhevm mpc threshold-cryptography privacy security enclave
description: "How the Zama KMS holds the FHE decryption key as 13 shares, what its gRPC operations do, how a node is built (core, connector, vaults, backups) and deployed in Nitro Enclaves."
image: /assets/article/blockchain/zamafhe/2026-09-18-zama-kms-mindmap.png
isMath: true
---

[Zama](https://www.zama.ai/) runs confidential smart contracts on ordinary EVM chains with Fully Homomorphic Encryption (FHE): balances and amounts are ciphertexts under one global public key, off-chain coprocessors compute on them, and a smart contract decides who may read a result. The last step, turning a ciphertext back into a number for the party allowed to see it, needs the private key. The property this article depends on is that no machine ever holds that key: it exists only as thirteen shares, spread across thirteen organisations, and decryption is a multi-party computation among them. The component that does this is the **Key Management Service**, the KMS, and it is published as its own repository, `zama-ai/kms`.

Two earlier articles placed the KMS in the protocol: the [architecture article]({{site.url_complet}}/2026/09/18/zama-fhevm-architecture-components-trust-model/) gave its trust assumption, and the [whitepaper reading]({{site.url_complet}}/2026/09/18/zama-fhevm-whitepaper-vs-implementation/) its specification. This one opens the repository. It covers the threshold model and the protocol the KMS runs, the operations it exposes over gRPC and what each one costs, the anatomy of a node (core service, threshold service, connector, vaults, keychains), the enclave and networking design, the backup and recovery machinery, and what a party has to deploy to be one of the thirteen.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What the KMS replaces

A classical key management system is a hardware security module: a box that holds keys and refuses to export them. The repository's introduction lists the reasons Zama did not build on one: HSMs are proprietary, support a fixed set of algorithms, and resist remote attackers rather than physical ones. For an FHE key that every user of every host chain encrypts under, a single box is also a single point of compromise and of failure.

The KMS instead applies threshold cryptography. A group of $$n$$ parties jointly generates a key pair $$(pk, sk)$$ such that each party $$i$$ holds a share $$sk_i$$ and $$sk$$ itself is never assembled anywhere. A parameter $$t \lt n$$ bounds the adversary: with at most $$t$$ corrupted parties, nothing about $$sk$$ leaks, and every protocol still completes with a correct result. The flavour the KMS implements is the strong one, *maliciously secure and robust*: corrupted parties may run arbitrary code, and honest parties still finish (*guaranteed output delivery*). That guarantee requires a strong honest majority, $$t \lt n/3$$, so the smallest cluster with $$t \gt 0$$ has four parties, and the production deployment uses $$n = 13$$, $$t = 4$$.

The protocols come from the paper [Noah's Ark: Efficient Threshold-FHE Using Noise Flooding](https://eprint.iacr.org/2023/815) (WAHC 2023), and their full specification is the cryptographic documentation Zama prepared as a NIST threshold-cryptography submission, shipped in the repository as a PDF. Parameters are chosen for 128-bit computational security and a failure probability of $$2^{-128}$$; the fhevm deployment's parameter set (`BC_PARAMS_SNS`) gives 80 bits of statistical security on top.

The documentation draws three consequences:

- **Decentralisation.** No secret material is stored centrally, so an attacker has to compromise many systems rather than one.
- **Resilience.** The network keeps working with up to $$t$$ parties offline or hostile.
- **Auditability.** Every operation is triggered by a transaction on the Gateway, so the audit log is a blockchain and a corrupt party can be identified and penalised.

## What the KMS does

The gRPC service, `CoreServiceEndpoint`, exposes a small number of operations. Each is a request with a unique 32-byte `RequestId`; long-running ones are started, then polled for their result.

| Operation | RPCs | What happens | Duration (documented) |
|---|---|---|---|
| **Preprocessing** | `KeyGenPreproc`, `KeyGenPreprocResult` | The parties generate correlated randomness consumed once by a later key generation. Threshold mode only; the Gateway drives it, users never see it. | Hours, up to a day, for production parameters |
| **Key generation** | `KeyGen` | Distributed generation of a TFHE key set: public key, server (evaluation) key, and one secret-key share per party. Also key-switching keys between two existing keys. Public material goes to each party's public storage; a signed digest is returned. | A couple of hours |
| **CRS generation** | `CrsGen` | Distributed generation of a powers-of-tau common reference string, used by the zero-knowledge proofs on encrypted inputs. | Minutes |
| **Public decryption** | `PublicDecrypt`, `PublicDecryptSync` | Threshold decryption of a list of ciphertexts; every party and the caller learn the plaintext, and each party signs it. | Seconds |
| **User decryption** | `UserDecrypt`, `UserDecryptSync` | Each party partially decrypts and *signcrypts* its share under the requester's public key; only the designated recipient can reconstruct the plaintext. Authenticated by an [EIP-712](https://eips.ethereum.org/EIPS/eip-712) signature from the user. | Seconds |
| **Epoch and resharing** | `NewMpcEpoch`, `GetEpochResult`, `DestroyMpcEpoch` | Refreshes every party's share of the same key, so that shares stolen before the refresh become worthless; also lets a party that lost its share rejoin, and rotates the party set. | Depends on key count |
| **Contexts** | MPC and custodian context RPCs, `DestroyMpcContext` | Define which parties form the cluster, and which custodians hold backup shares. | — |

Two details of the decryption path matter for anyone verifying results.

**The ciphertext form.** A ciphertext is not decrypted in the form the coprocessor computes. It is first converted by *switch-and-squash* into a larger-domain form with a wide gap between message and noise, which is what makes noise-flooding decryption safe; the coprocessors do this conversion and publish both forms.

**The signature schemes.** Every signed result carries a `signing_schemes` list. An empty list means the historical ECDSA/secp256k1 signature over the EIP-712 hash, which an EVM contract checks with `ecrecover`. A request can also ask for Ed25519, for Solana, or for ML-DSA at three security levels ([FIPS 204](https://csrc.nist.gov/pubs/fips/204/final), post-quantum), and a verifier must reject a response that omits a scheme it asked for.

The decryption mode is configurable. `NoiseFloodSmall` is the default; `NoiseFloodLarge` and two bit-decomposition variants exist. The production values file sets `NoiseFloodSmall`, a decryption capacity of 10,000 and a minimum cache of 6,000 preprocessed items, and 90 preprocessing sessions, which is the material the online decryption consumes.

## Anatomy of a node

![A KMS party: the connector's three services around a database, the core service exposing gRPC on localhost, the threshold service talking mTLS to twelve peers, the private and public vaults in S3, the keychain in AWS KMS or custodian shares, with the kms-server inside a Nitro Enclave]({{site.url_complet}}/assets/article/blockchain/zamafhe/zama-kms-node-anatomy-concept.png)

One party runs one **KMS node**, which the documentation splits into pieces that map onto processes and storage.

### Core service and threshold service

The **core service** (`kms-server`) is the gRPC front. It validates a request, packages the result, signs it, and talks to storage. Behind it, the **threshold service** runs the MPC protocols with the other twelve parties over its own port; it is never called directly. The two live in one binary and one process, and the same binary serves two modes, chosen by the presence of a `[threshold]` section in the TOML configuration: a *centralized* mode, where a single `RealCentralizedKms` holds the whole key, for tests and single-operator setups, and the *threshold* mode.

The Cargo workspace reflects the split. Under `core/`, `threshold-algebra`, `threshold-execution`, `threshold-networking` and `threshold-hashing` are the MPC stack (with `threshold-bgv` as an experimental BGV/BFV variant), and `core/service` is the packaging around it: RPC handlers and state machines under `engine/` (`centralized/` and `threshold/`), the storage abstraction under `vault/`, backup under `backup/`, and the cryptography for signcryption, hybrid ML-KEM, attestation and multi-scheme signing under `cryptography/`. The validation of user-decryption responses is compiled twice, natively and to WASM, so that a browser can verify what the KMS returns.

### The connector

A KMS party does not watch the Gateway itself. The **KMS connector**, which lives in the `fhevm` repository, does: three small Rust services around a database, a `GatewayListener` that stores Gateway events, a `KmsWorker` that turns them into gRPC calls on the local core and stores the answers, and a `TransactionSender` that posts signed responses back to the Gateway. The worker is also where the access-control check happens: it reads each host chain's `ACL` contract over RPC before asking the core to decrypt, since the core itself performs no authorisation.

The documentation states that last point without qualification: the gRPC endpoints allow *indiscriminate* use, and anyone who can call `PublicDecrypt` on more than $$t$$ cores gets a decryption. The deployment pattern follows from it. The connector and the core run on the same machine, the core listens on localhost only, and the gRPC port (50100 by default) "must never be exposed to the internet". Authorisation is entirely the Gateway's job, enforced before an event ever reaches a connector.

### Vaults, keychains and the identity

A node keeps three kinds of storage:

- **Private storage**, the node's own: its FHE key shares, PRSS setup, epoch and context data, and its signing identity. Backends include local files, S3, AWS KMS and the Nitro Enclave path; on mainnet it is an S3 bucket with a `PRIV-p<id>/` prefix.
- **Public storage**, the *Keychain DA*: the public keys, server keys and CRSes the node helped generate, each stored under its own hash digest. Every party hosts its own copy, and the digests are recorded on the Gateway with each party's signature, so a user can fetch a key from any party, hash it and check the signature. On mainnet, an S3 bucket with a `PUB-p<id>/` prefix.
- **A backup vault**, where private material is written as versioned `BackupCiphertext`s wrapped under a key that a **keychain** protects.

The keychain is one of two: `AwsKms`, where the wrapping key is an AWS KMS customer master key (the default and bootstrap path), or `SecretSharing`, where the wrapping key is Shamir-shared across offline *custodians*.

The node's identity is a signing key pair. Since 0.15 a node persists two private objects: an ECDSA/secp256k1 signing key, the authoritative on-chain identity, and an independent `RootSigningSeed` from which every non-ECDSA scheme (Ed25519, ML-DSA) is derived on demand. `kms-gen-keys` is the only program that ever creates the seed. The rule that keeps upgrades safe is that an existing ECDSA key is never re-derived from the seed, so a node upgraded from an older release keeps the address the Gateway already knows.

### Boot-time verification

A node checks its storage before serving a single request, following three rules the architecture notes spell out: private storage is the reference, extra material in public storage is reported but never rejected, and nothing is written or fetched. The checks that stop the boot on failure are:

- every published key set and CRS is present and hashes, over its raw stored bytes, to the digest in the private metadata;
- the EIP-712 signatures in that metadata recover the node's own address;
- a threshold node holds no centralized-only material, and the reverse;
- every key epoch has its `EpochData`, and every epoch its context.

Digests are computed over raw bytes deliberately, so that a TFHE serialisation change cannot make intact material look corrupt.

## Networking between parties

The threshold service talks to its twelve peers over gRPC on port 50001, with mutual TLS. Each party is identified by the Common Name of a self-signed certificate that also serves as its own CA; every peer's certificate is in every other peer's trust store, and the CN must appear in the certificate's SAN list. The identity is checked twice: at the TLS handshake, and on **every** MPC message, whose tag names a sender that must match the certificate.

A session model wraps each computation, whether a decryption, a preprocessing or a key generation, in a `NetworkSession` with its own identifier and round counter. Messages for a session the receiver does not yet know are held briefly in case the request reaches that party late.

In production the transport is not the public internet. The deployment guide has each party expose its service through an AWS PrivateLink endpoint and connect to the other twelve through consumer endpoints, so that inter-party traffic never leaves the AWS network; each peer then appears to a party as an `ExternalName` service such as `party2-external.kms-threshold.svc.cluster.local`.

An insecure, non-TLS mode exists behind a compile-time feature for testing, and the documentation says what it means: without TLS, any connection to the port is trusted to be whoever its message tag claims.

## Enclaves and attestation

The production node runs inside an **AWS Nitro Enclave**, for the reason the whitepaper gave: a share of the decryption key is worth money, and an operator who can read its own share can sell it. In the enclave, the share exists only in memory the parent instance cannot inspect, and the enclave image is measured: its PCR values, covering the kernel, the boot ramdisk and the root filesystem, are signed by the Nitro security module.

The KMS ties this into its TLS. In the `Auto` mode, the certificate a party presents to its peers embeds an attestation document; the custom verifiers (`AttestedServerVerifier`, `AttestedClientVerifier`) check the certificate chain, the attestation, and that the PCR values belong to a list of **trusted releases** in the configuration. A peer running unapproved software cannot join. MPC contexts carry the same list, and a threshold deployment with attestation refuses a context whose PCR allowlist is empty.

The enclave has no network of its own. A small workspace member, `vsocktun`, relays TCP from the enclave to the parent over VSOCK, and the Helm values map the ports the enclave needs: tracing, IMDS, STS, S3, AWS KMS, and the peer port. The production values give the enclave 48 CPUs and 96 GiB out of a `c7a.16xlarge` instance.

## Backup and recovery

The threshold protocols already tolerate $$t$$ parties losing everything: a resharing rebuilds their shares from the others. Two cases remain. A party that loses only its storage should not have to bother twelve others; and more than $$t$$ parties losing their data at once, through a bad update or a coordinated attack, would destroy every ciphertext in the system. The repository answers both with an automatic, encrypted backup of each node's long-term private material to its backup vault, and two ways to protect the key that encrypts it.

With the **AWS KMS keychain**, the wrapping key is a customer master key in the operator's account, and `RestoreFromBackup` rebuilds a node from the vault.

With the **custodian keychain**, the wrapping key is Shamir-shared across $$m$$ custodians with their own quorum, which need not be $$m/3$$. The workflow has three stages:

- **Setup.** Each custodian runs `kms-custodian generate` on an air-gapped machine, writes a BIP39 seed phrase on paper, and hands the operators a public setup message.
- **Context.** The operators install a custodian context with `NewCustodianContext`, which re-encrypts the whole vault under the new key before persisting the recovery material, and rolls back if any step fails.
- **Recovery.** `CustodianRecoveryInit`, then each custodian decrypts its share with the seed phrase and re-encrypts it for the recovering node (`kms-custodian decrypt`), then `CustodianBackupRecovery`.

Custodians cannot recover anything alone, and recovery can target a different, equally sized party set.

The restore order is fixed, contexts and epochs first, key sets and CRS metadata next, the signing key last, so that every intermediate state is bootable and a half-finished restore can be rerun. A node without its signing key stays in recovery mode.

## Becoming one of the thirteen

![The deployment of one KMS party: Terraform for EKS, S3, IAM, KMS and PrivateLink; the kms-core Helm chart as a StatefulSet with the enclave; PRSS initialisation; and the coordination with the twelve other parties and the Gateway]({{site.url_complet}}/assets/article/blockchain/zamafhe/zama-kms-party-deployment-sequence.png)

The production deployment guide is written for one party, deploying into its own AWS account with a party ID assigned by the network coordinator. The steps, with the values the guide gives:

1. **Infrastructure with Terraform.** The `terraform-mpc-modules` repository provisions an EKS cluster with a Nitro-Enclaves-enabled node group of `c7a.16xlarge` instances on a pinned AMI release, with 96 GiB reserved for the enclave and 100 GiB of storage, two S3 buckets for public and private material, IAM roles bound to the service account through IRSA, an AWS KMS root key for the keychain, an optional RDS database for the connector, and the enclave image attestation hash to trust.
2. **PrivateLink.** A provider module exposes the party's peer port as a VPC endpoint service; a consumer module connects to the twelve services the other parties publish. Service names are exchanged out of band.
3. **The Helm release.** The `kms-core` chart (version 1.9.2 for release 0.15.x) deploys a StatefulSet. The values carry the party's ID, the `peersList` with every party's host, port and PEM certificate, the trusted-release PCR list, the threshold parameters, the enclave configuration, both vaults, and the AWS KMS root key. Resources are 8 CPUs and 16 GiB requested, 32 GiB limit, with a gRPC timeout of 360 seconds and a 100 MiB message size, since key material is large.
4. **Signing identity.** `kms-gen-keys` creates the seed and the ECDSA key and, in threshold mode, the party's self-signed certificate. The guide insists the seed reach the backup vault before the node is registered on the Gateway.
5. **PRSS initialisation.** `kms-init`, run once against all parties, sets up the pseudo-random secret sharing the protocols rely on; the material lands in private storage under `PrssSetup`, a restarted node reuses it, and a changed party set requires a new initialisation.
6. **Key generation**, triggered through the Gateway in production; the health-check tool reports key IDs, CRS availability and preprocessing status as it progresses.

Monitoring uses a `ServiceMonitor` on port 9646 and the `kms-health-check` probe. The security page reduces its advice to three ports: 50100 (gRPC) never leaves the host, 50001 (P2P) is open only between KMS nodes, 9646 (metrics) only to monitoring.

## Performance

The benchmarks page reports distributed decryption with 13 parties and the production parameter set, in a LAN setting (one EC2 region). On `c5a.8xlarge` nodes (32 vCPUs), a single `euint64` decryption takes about 96 ms; with 1,024 requests in flight the latency is about 3 s and the throughput about 330 `euint64` per second, or close to 4,800 raw LWE ciphertexts per second for `euint16`. A boolean decrypts in a few milliseconds alone and reaches roughly 700 per second in batches. Key generation and preprocessing are the slow operations, hours rather than seconds, which is why preprocessing runs continuously in the background to keep a cache ahead of demand.

## Conclusion

The Zama KMS is the one component of the protocol whose failure would read every ciphertext, and the repository is organised around making that failure require thirteen independent mistakes.

- **Threshold model**: $$n = 13$$, $$t = 4$$, maliciously secure and robust MPC with guaranteed output delivery; key generation, decryption and CRS generation all run as protocols among the parties, and $$sk$$ never exists.
- **Operations**: preprocessing and key generation take hours and are driven by the Gateway; public and user decryption take seconds; user decryption returns signcrypted shares that only the recipient can open; results are signed under ECDSA by default and optionally Ed25519 or ML-DSA.
- **A node** is a core service on localhost, a threshold service on mTLS, a connector that enforces the ACL and speaks to the Gateway, and three stores: private, public (the Keychain DA) and backup.
- **Authorisation is not the KMS's job**: the gRPC surface decides nothing; the Gateway validates and the connector checks the host chain ACL.
- **Enclaves** keep the share from the operator and let peers refuse unapproved software through attested TLS with a PCR allowlist.
- **Backups** are automatic and encrypted; the wrapping key is an AWS KMS key or a Shamir-shared custodian key with paper seed phrases, and resharing rotates every party's share.
- **Deployment** is one AWS account per party, Terraform plus a Helm StatefulSet, PrivateLink to the other twelve, and a one-time PRSS initialisation.

![Mindmap of the Zama KMS: threshold model, gRPC operations, node anatomy, networking and enclaves, backup and recovery, deployment, performance]({{site.url_complet}}/assets/article/blockchain/zamafhe/2026-09-18-zama-kms-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Threshold cryptography** | A key held as $$n$$ shares such that more than $$t$$ parties must cooperate to use it and at most $$t$$ learn nothing; the KMS requires $$t \lt n/3$$. |
| **Robust MPC** | A multi-party protocol that completes with a correct output even when up to $$t$$ parties are offline or malicious (guaranteed output delivery). |
| **Noise flooding** | The decryption technique of the Noah's Ark paper, in which parties add large noise to their partial decryptions so that the combined result reveals the plaintext and nothing about the key. |
| **Switch-and-squash** | The coprocessor-side conversion of a TFHE ciphertext into a larger-domain form the KMS can decrypt safely with noise flooding. |
| **PRSS** | Pseudo-random secret sharing, the one-time setup material (`kms-init`) from which parties derive correlated randomness without communication. |
| **Preprocessing** | Correlated randomness generated ahead of time and consumed once by a key generation or a decryption. |
| **Signcryption** | Encryption combined with a signature; how each party returns its share of a user decryption so that only the recipient can read it and can verify who sent it. |
| **Keychain DA** | The public storage each party hosts for keys and CRSes, addressed by hash digest and attested by signed digests on the Gateway. |
| **Keychain** | The mechanism protecting the backup wrapping key: an AWS KMS customer master key or a Shamir-shared custodian key. |
| **Attested TLS** | Mutual TLS whose certificates embed a Nitro Enclave attestation document, letting peers check each other's PCR values against a trusted-release list. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| The FHE private key never exists in one place. | Distributed key generation; each party persists only its share; resharing produces new shares of the same key. | More than $$t$$ parties collude, or an enclave breach exposes more than $$t$$ shares. |
| A decryption returns the correct plaintext even with $$t$$ misbehaving parties. | Robust MPC with guaranteed output delivery; the Gateway waits for a threshold of matching signed results. | The corruption threshold $$t \lt n/3$$ is exceeded. |
| Only a Gateway-validated request reaches the core. | Core gRPC bound to localhost; the connector reads Gateway events and checks the host chain ACL. | The gRPC port is exposed, or a connector is modified to skip the ACL read. |
| Only approved software takes part in the MPC. | Attested TLS with a PCR allowlist in the peer configuration and in MPC contexts. | The trusted-release list is emptied on a non-enclave build, or a PCR of a malicious image is added. |
| Published public material is what the parties generated. | Digests in private metadata checked against raw bytes at boot; signed digests on the Gateway; hash-named objects in the Keychain DA. | An operator's private storage is altered together with its public storage. |
| A lost node can be rebuilt without reconstructing the key. | Encrypted backups to the vault, restored in a fixed order; custodian recovery with a quorum of seed phrases. | The wrapping key is lost with no custodian context installed. |
| A node's on-chain identity survives upgrades. | The ECDSA key is stored on its own and never re-derived from the seed. | `kms-gen-keys` is run with `overwrite = true` on a registered node. |

### Integration Notes

| Behaviour | What an integrator or operator should do |
|-----------|------------------------------|
| The core performs no authorisation on gRPC calls. | Never expose port 50100; co-locate the connector; treat the Gateway as the access-control layer. |
| Preprocessing and key generation take hours with production parameters. | Do not schedule them synchronously; keep the preprocessing cache (`minDecCache`) ahead of decryption demand. |
| `kms-init` must run exactly once per party set. | Re-running it fails; a changed party set requires deleting `PrssSetup` and initialising again. |
| An empty `signing_schemes` list yields ECDSA only; naming schemes replaces the default. | Ask for every scheme you intend to verify and reject a response missing one. |
| Only the ECDSA tuple is bound to EIP-712; other schemes sign the serialized payload. | Verifiers for Ed25519 or ML-DSA rebuild the payload, not the typed-data hash. |
| A node configured for the custodian keychain makes no backups until its first context exists. | Install a custodian context immediately after switching keychains; watch the boot warning. |
| Boot fails on foreign or inconsistent storage. | Never point a threshold node at a centralized node's bucket or the reverse; check `EpochData` and `Context` entries before restoring. |
| The trusted-release PCR list gates peers and contexts. | Update the list before rolling out a new enclave image, or peers will reject the upgraded party. |

## Frequently Asked Questions

**Q: What does $$t \lt n/3$$ buy that $$t \lt n/2$$ would not?**

Robustness. With an honest majority ($$t \lt n/2$$) a protocol can be made secure but not guaranteed to finish: malicious parties can force an abort. With a strong honest majority ($$t \lt n/3$$) the KMS's protocols guarantee output delivery, so a decryption or a key generation completes correctly with up to $$t$$ parties offline or hostile. For thirteen parties that means four, and it is why the documentation says the smallest useful cluster has four parties.

**Q: How does a user decryption keep the plaintext from the KMS parties themselves?**

Each party computes only a partial decryption, its share of the plaintext, and signcrypts it under the public key the user supplied in the request. The Gateway collects $$2t + 1$$ such encrypted shares and hands them to the user, who decrypts them locally and reconstructs the value. No party, and not the Gateway or the relayer, ever sees more than one share.

**Q: Where does the access-control decision happen, since the core does not make it?**

In two places, neither of them the core:

- The **Gateway** validates the request and emits an event only for a valid one.
- The **connector's** `KmsWorker`, on each party, reads the relevant host chain's `ACL` contract over RPC and only then calls the local core.

The core's gRPC port is bound to localhost precisely so that these are the only paths in.

**Q: What is the difference between resharing and backup recovery?**

Resharing (`NewMpcEpoch` with a previous epoch) is a protocol among the parties that produces fresh shares of the same key; it makes stolen shares worthless and can rebuild the shares of up to $$t$$ parties from the others.

Backup recovery is local to one node: it restores that node's own private material from its encrypted backup vault, unwrapped by an AWS KMS key or by a quorum of custodians.

Resharing needs the other parties; recovery needs the vault and the keychain.

**Q: Combine enclaves and TLS: what stops a party from running a modified KMS binary?**

Its peers. The enclave image is measured into PCR values signed by the Nitro security module; in `Auto` TLS mode a party's certificate embeds that attestation, and every peer's verifier checks the PCRs against a configured list of trusted releases before completing the handshake.

The same list is attached to MPC contexts, and a context with an empty list is refused on attested deployments. A modified image has different PCRs, is not in the list, and cannot open a session with anyone.

**Q: Why are digests at boot computed over raw stored bytes rather than over the deserialized key?**

Because the check must distinguish corrupted material from a format change. If the node deserialized a key and re-serialized it with a newer TFHE-rs version, the bytes could differ from those hashed at generation time, and intact material would fail verification. Hashing the stored bytes ties the check to what was written, and a mismatch then means the object changed.

## References

### Analyzed source

- [zama-ai/kms](https://github.com/zama-ai/kms) — analyzed at commit [`8badd0959ac2b494371c30930b335bf65844cdd8`](https://github.com/zama-ai/kms/tree/8badd0959ac2b494371c30930b335bf65844cdd8) (6 commits after tag `v0.15.0-0`; Helm chart `kms-core` 1.9.2), 2026-09-18
- [zama-ai/fhevm](https://github.com/zama-ai/fhevm) — `kms-connector`, analyzed at commit [`ac6ff45ebb27c1300cc44669235751c657b3ce14`](https://github.com/zama-ai/fhevm/tree/ac6ff45ebb27c1300cc44669235751c657b3ce14), 2026-09-18

### Papers and specifications

- [Dahl et al. — Noah's Ark: Efficient Threshold-FHE Using Noise Flooding (WAHC 2023)](https://eprint.iacr.org/2023/815)
- [Zama — Threshold FHE cryptographic documentation (NIST threshold submission)](https://github.com/zama-ai/threshold-fhe/blob/main/docs/CryptographicDocumentation.pdf)
- [Fhevm whitepaper, version 3.1](https://github.com/zama-ai/fhevm/blob/main/fhevm-whitepaper.pdf)
- [FIPS 204 — Module-Lattice-Based Digital Signature Standard](https://csrc.nist.gov/pubs/fips/204/final)
- [EIP-712 — Typed structured data hashing and signing](https://eips.ethereum.org/EIPS/eip-712)
- [BIP-39 — Mnemonic code for generating deterministic keys](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)

### Documentation and tooling

- [Zama blog — Introducing the Zama Threshold Key Management System](https://www.zama.ai/post/introducing-zama-threshold-key-management-system-tkms)
- [terraform-mpc-modules](https://github.com/zama-ai/terraform-mpc-modules)
- [TFHE-rs](https://github.com/zama-ai/tfhe-rs)
- [AWS Nitro Enclaves](https://aws.amazon.com/ec2/nitro/nitro-enclaves/)
- [AWS PrivateLink](https://aws.amazon.com/privatelink/)

### Related articles

- [Zama FHEVM Architecture — Components, Data Flow and What Has to Be Trusted]({{site.url_complet}}/2026/09/18/zama-fhevm-architecture-components-trust-model/)
- [The Zama FHEVM Whitepaper — What It Specifies, and What the Code Does Differently]({{site.url_complet}}/2026/09/18/zama-fhevm-whitepaper-vs-implementation/)
- [Running a Zama Coprocessor — Architecture, Services and Operator Setup]({{site.url_complet}}/2026/09/18/zama-coprocessor-architecture-and-operator-setup/)
- [Overview, security and applications of Multi-Party Computation (MPC)]({{site.url_complet}}/2024/10/21/mpc-protocol-overview/)
- [AWS Nitro Enclaves: Secure and Isolated Compute for Sensitive Data]({{site.url_complet}}/2025/07/17/aws-nitro-enclaves-overview/)

### Tooling

- [Claude Code](https://claude.com/product/claude-code)
