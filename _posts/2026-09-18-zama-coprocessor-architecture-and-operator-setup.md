---
layout: post
title: "Running a Zama Coprocessor — Architecture, Services and Operator Setup"
date:   2026-09-18
lang: en
locale: en-GB
categories: blockchain cryptography security zama
tags: zama fhe fhevm privacy security cloud confidential-smart-contract
description: "What a Zama coprocessor node is made of, how its six services move work through PostgreSQL and S3, and how an operator deploys one on EKS with the coprocessor-operator charts."
image: /assets/article/blockchain/zamafhe/2026-09-18-zama-coprocessor-mindmap.png
isMath: false
---

[Zama](https://www.zama.ai/) runs confidential smart contracts on ordinary EVM chains with Fully Homomorphic Encryption (FHE). The chain never computes on ciphertexts itself: a contract records *which* operation to perform on *which* encrypted handles, and a set of off-chain operators, the **coprocessors**, do the arithmetic, verify users' encrypted inputs and commit their results to a coordination rollup called the Gateway. The protocol's security argument depends on several of them running the same work independently and a majority agreeing; the [architecture article]({{site.url_complet}}/2026/09/18/zama-fhevm-architecture-components-trust-model/) covers that argument.

This article is about one coprocessor, seen from the inside and from the operator's chair. It reads two repositories: `zama-ai/fhevm`, whose `coprocessor/fhevm-engine` directory holds the Rust services a node is made of, and `zama-ai/coprocessor-operator`, the repository Zama gives partner operators to deploy those services on an EKS cluster. The first tells what a coprocessor does; the second tells what it takes to run one in production, down to the CPU counts, the secrets, the PostgreSQL roles and the signing key.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What a coprocessor is responsible for

A coprocessor has four jobs in the protocol, and they map onto four distinct data flows through the node:

- **Compute.** Every FHE operation a contract performs symbolically on a host chain is an event from the `FHEVMExecutor` contract. The coprocessor turns those events into a queue of computations, evaluates them with TFHE-rs using the evaluation key, and stores the resulting ciphertext under the handle the chain already derived.
- **Verify inputs.** When a user registers an encrypted input on the Gateway, the `InputVerification` contract emits a request. The coprocessor checks the zero-knowledge proof, unpacks the ciphertexts, and attests the resulting handles with an [EIP-712](https://eips.ethereum.org/EIPS/eip-712) signature bound to the user, the contract and the chain. That signature is what a contract later checks in `FHE.fromExternal`.
- **Commit.** For every handle the host chain's `ACL` contract allows, the coprocessor prepares the ciphertext for decryption with a *switch-and-squash* step, uploads both forms to its public S3 bucket, and posts their digests to the Gateway's `CiphertextCommits` contract. A handle becomes decryptable once a majority of coprocessors have committed to the same digests.
- **Serve ciphertexts.** The KMS downloads the prepared ciphertexts from the operators' buckets when it decrypts. The bucket URL is part of the coprocessor's on-chain registration: the Gateway's `Coprocessor` struct holds a `txSenderAddress`, a `signerAddress` and an `s3BucketUrl`.

Everything else in the node exists to make those four flows reliable across chain reorganisations, restarts and upgrades.

## The six services

The node is not one binary. `fhevm-engine` is a Cargo workspace of services that share a PostgreSQL database and talk to each other through it, using `LISTEN`/`NOTIFY` channels as a work queue. The operator repository deploys six of them, each as its own Kubernetes workload.

![The six coprocessor services around PostgreSQL: host-listener and gw-listener write work, tfhe-worker, zkproof-worker and sns-worker consume it, and tx-sender posts signed results to the Gateway; ciphertexts go to S3]({{site.url_complet}}/assets/article/blockchain/zamafhe/zama-coprocessor-services-concept.png)

| Service | Listens to | Writes | Notifies | What it does |
|---|---|---|---|---|
| **host-listener** | Host chain WebSocket: `FHEVMExecutor`, `ACL`, `KMSGeneration` events | `computations`, `allowed_handles`, `dependence_chain`, block tables | tfhe-worker | Converts the symbolic execution trace into a computation DAG, tracks block finality and reorgs |
| **host-listener-poller** | Host chain HTTP, at a finality lag | Same tables | tfhe-worker | Catch-up path that re-reads finalised blocks by polling, independent of the subscription |
| **gw-listener** | Gateway: `InputVerification` events | `verify_proofs` | zkproof-worker (`event_zkpok_new_work`) | Turns input-verification requests into proof-checking work |
| **tfhe-worker** | `computations` (polling, dependence chains) | `ciphertexts`, `pbs_computations` | sns-worker (`event_ciphertext_computed`) | The FHE engine: evaluates operations with TFHE-rs on CPU or GPU |
| **zkproof-worker** | `event_zkpok_new_work` | `verify_proofs` (verified, handles) | tx-sender (`event_zkpok_computed`) | Verifies the ZKPoK, unpacks and stores the input ciphertexts, derives their handles |
| **sns-worker** | `event_pbs_computations`, `event_ciphertext_computed` | `ciphertexts128`, `ciphertext_digest`; S3 | tx-sender (`event_ciphertexts_uploaded`) | Switch-and-squash, S3 upload, digest computation |
| **tx-sender** | `event_zkpok_computed`, `event_ciphertexts_uploaded` | `transactions` | Gateway | Signs the EIP-712 attestation over verified handles, then sends `InputVerification` responses and `CiphertextCommits.addCiphertextMaterial` transactions with the operator's key |

A seventh workload, **db-migration**, is a one-shot job that applies the schema migrations before any service starts. Two more, `consensus-detector` and `upgrade-controller`, exist in the workspace for the blue-green upgrade mechanism described later and are not part of the v0.13 operator deployment.

### host-listener: from events to a computation graph

The listener subscribes to the host chain node over WebSocket and reads every event of the three protocol contracts. Each FHE operation event becomes a row in `computations`: the output handle, the operation code, the input handles (the second of which may be a scalar), the result type, and completion flags. Each `Allowed` or `AllowedForDecryption` event becomes a row in `allowed_handles`, which is what later triggers preparation for decryption.

Ordering is the difficult part. Operations depend on each other through their handles, and the worker must not evaluate `add(h1, h2)` before `h1` exists. The listener groups operations into **dependence chains** (a *DCID* in the code), connected components of the dependency graph that may extend across blocks when `--dependence-cross-block` is set, as it is on mainnet. A chain is the unit the worker locks and processes; independent chains run in parallel. A cap on the number of dependent operations per chain (`--dependent-ops-max-per-chain`, disabled with `0` on mainnet) can demote very long chains to a slow lane so that one contract's deep computation does not starve the others.

Reorganisations are handled by finality tracking rather than by rolling back: `--reorg-maximum-duration-in-blocks` (50 on Ethereum, 120 on Polygon) bounds how far back a reorg is expected, `--catchup-finalization-in-blocks` says how long to wait before a block is considered final, and a separate **poller** deployment re-reads blocks over HTTP at a `--finality-lag` of 15 blocks on Ethereum and 120 on Polygon, so that a dropped subscription cannot lose an event. The poller keeps its cursor in `host_listener_poller_state`, seeded once with `--seed-start-block`; the repository ships a job to patch that cursor when a poller has to be moved, with a comment explaining the block it was moved to and why.

### gw-listener and zkproof-worker: input verification

The Gateway listener watches `InputVerification` over the Gateway's WebSocket and inserts each request into `verify_proofs`, then notifies on `event_zkpok_new_work`. A zkproof-worker picks it up, verifies the proof against the CRS, unpacks the packed ciphertext list, stores each ciphertext with its derived handle, and writes back `verified` and the handle list. Its notification on `event_zkpok_computed` wakes the transaction sender, which computes the EIP-712 `CiphertextVerification` hash over the handles, the user, the contract and the chain id, signs it, and posts the response.

The listener's README states a deliberate limitation: it uses `eth_subscribe`, and if the connection drops, the subscription resumes from the head and may skip events. This is accepted because input verification is a synchronous request from the client's point of view; a lost request is retried by the user, and nothing on the Gateway is left inconsistent.

### tfhe-worker: the FHE engine

The worker polls `computations` for chains whose inputs are all available, takes a distributed lock on the chain, and evaluates the operations in order with TFHE-rs. The lock is a lease with a TTL and a time slice, so that a crashed worker's chain is picked up by another. Two thread pools matter: the tokio pool for asynchronous I/O and the FHE pool for the arithmetic itself. On mainnet the values file gives the worker 64 FHE threads, 16 tokio threads, a batch of 16 work items and 100 dependence chains per batch, on a node with 88 CPUs and 128 GiB of memory.

Results go to `ciphertexts` under the output handle; operations that need a programmable bootstrapping also record a row in `pbs_computations`, which the sns-worker consumes. A computation that fails is retried rather than abandoned; the code comments are explicit that a row whose retries are exhausted is demoted to the slow lane and re-armed on a long cadence, so that the failure is visible in metrics instead of silently terminal.

GPU builds exist for the three services that do FHE work (`tfhe-worker`, `sns-worker`, `zkproof-worker`). The repository documents that a GPU image is built for exactly one compute capability, tagged with it (`v0.15.0-cuda12.2-sm90` for H100), and refuses to start on a device of another capability, because the CUDA architectures compiled into TFHE-rs differ and an L40 build would silently lack the Hopper bootstrapping paths. The v0.13 operator values run the CPU images.

### sns-worker: preparing ciphertexts for the KMS

*Switch-and-squash* converts a TFHE ciphertext into a form with a much larger gap between message bits and noise, which the KMS needs for a safe threshold decryption. The worker listens for computed ciphertexts and pending bootstrappings, performs the conversion with the `sns_pk` key stored in the database, stores the 128-bit form in `ciphertexts128`, uploads both the regular and the squashed ciphertext to the S3 bucket, and writes their digests to `ciphertext_digest`. Its notification on `event_ciphertexts_uploaded` tells the transaction sender that a commitment can be posted. The mainnet configuration allows 100 concurrent uploads with up to 100 retries each and rechecks S3 every two seconds for objects still missing.

### tx-sender: the node's voice on the Gateway

The transaction sender is the only service that holds a key, and that key does two things: it signs the EIP-712 attestations over verified input handles, and it signs the Gateway transactions. The sender reads verified proofs and uploaded digests from the database and sends two kinds of transactions:

- **Input-verification responses**, in batches of up to 128, with six retries at most; after that a response is dropped, because the user will have retried the registration.
- **`addCiphertextMaterial` calls**, in batches of 10, retried without limit, because a missing commitment blocks decryption for everyone.

Gas is over-provisioned by 300 percent. On mainnet the signer is an AWS KMS key rather than a private key in a file: the values set `wallet.awsKms.enabled: true`, and the check chart's `kms-check` prints the Ethereum address of that key with `cast wallet address --aws`.

## The data path, end to end

![Sequence of a computation through the coprocessor: executor event, host-listener insert, tfhe-worker evaluation, ACL event, sns-worker switch-and-squash and S3 upload, tx-sender commitment on the Gateway, majority consensus, KMS download]({{site.url_complet}}/assets/article/blockchain/zamafhe/zama-coprocessor-computation-sequence.png)

Following one `FHE.add` from a contract to a decryptable ciphertext:

1. The host chain mines a transaction in which `FHEVMExecutor.fheAdd` derives a handle and emits an event; the contract then calls `FHE.allow` on it and the `ACL` emits `Allowed`.
2. The host-listener sees both events, inserts a `computations` row with the two input handles and the output handle, attaches it to a dependence chain, and inserts an `allowed_handles` row.
3. A tfhe-worker acquires the chain once both inputs are present in `ciphertexts`, evaluates the addition, and stores the result under the output handle.
4. The sns-worker, notified of the new ciphertext and of the allow, computes the squashed form, uploads both objects to S3, and records the two digests.
5. The tx-sender posts `addCiphertextMaterial(handle, keyId, digest, snsDigest)` to `CiphertextCommits`, signed by the operator's key.
6. The Gateway counts commitments per digest; when the coprocessor majority threshold is reached, the material is marked added and the handle can be decrypted.
7. On a decryption request, each KMS party downloads the prepared ciphertext from an operator's bucket, checks its digest against the consensus, and runs the threshold protocol.

Every step between 2 and 5 is idempotent and retried, and every step is visible in the database, which is why the operator tooling spends so much effort on the database.

## Deploying a node with coprocessor-operator

The `coprocessor-operator` repository is small, 296 kB, and is the operator's checklist. It assumes an EKS cluster provisioned with Zama's Terraform modules and supplies what Terraform does not: secrets, database roles, pre-flight checks, and the Helm values for every service on testnet and mainnet.

![Layout of a coprocessor deployment on EKS: namespaces per chain, RDS PostgreSQL, S3 behind a Cloudflare hostname, AWS KMS for the tx-sender key, Karpenter node pools for FHE workers and light services, Grafana Cloud for telemetry]({{site.url_complet}}/assets/article/blockchain/zamafhe/zama-coprocessor-deployment-concept.png)

### Infrastructure the node expects

| Resource | Role | Where it is referenced |
|---|---|---|
| **EKS cluster** with two Karpenter node pools | `coprocessor-pool` for the three FHE workers (88 CPU / 128 GiB for tfhe-worker, 48 CPU / 128 GiB each for zkproof-worker and sns-worker); `zws-pool` for listeners, tx-sender and jobs (1 to 8 CPU) | `affinity` and `tolerations` in every values file |
| **Namespaces** | `coproc` (workers), `coproc-admin` (jobs and checks), `gw-blockchain` (gw-listener, tx-sender), one `<chain>-blockchain` per host chain (`eth-blockchain`, `polygon-blockchain`), `monitoring` | `k8s-check`, `secrets-bootstrap.sh` |
| **RDS PostgreSQL** | The shared database, reached through an `ExternalName` service `coprocessor-database` in `coproc`; `sslmode=require` | `commonConfig.databaseUrl` |
| **S3 bucket** behind a **Cloudflare custom hostname** | Public ciphertext storage; `aws-check` requires an HTTPS `ListBucketResult` from the hostname | `S3_BUCKET_NAME` in `coprocessor-config`, `checks.aws.storageHostname` |
| **AWS KMS key** (`ECC_SECG_P256K1`, sign/verify) | The tx-sender's Ethereum signing key; never in a file | `coprocessor-tx-sender` ConfigMap, `AWS_KEY_ID` |
| **AWS Secrets Manager** | Holds the RDS master credentials, fetched by jobs through an IRSA-bound `db-admin` service account into a memory-backed volume | `db-admin-config[RDS_ADMIN_SECRET_ID]` |
| **Private registry** `hub.zama.org` | All images: service images under `zama-protocol/zama-ai/fhevm/coprocessor/`, utility images for `postgres`, `aws-cli`, `kubectl`, `eth-foundry`, `s5cmd` | `registry-credentials` in every namespace |
| **Grafana Cloud** | Prometheus, Loki and OTLP endpoints, fed by an in-cluster Alloy receiver | `grafana-cloud-credentials`, `tracing.endpoint` |
| **RPC endpoints** | HTTPS and WSS for each host chain, and for the Gateway (a Conduit-hosted Arbitrum Orbit rollup) | `rpc-credentials`, `conduit-credentials` |

### Step 1: secrets

`scripts/secrets-bootstrap.sh` is run once against the cluster. It detects the environment from the kubeconfig context, refuses to continue if a namespace is missing, then creates, idempotently, six groups of secrets:

- **RDS user passwords** for `coprocessor_user`, `postgres_exporter` and `sql_exporter`, generated with `openssl rand` and stored only in Kubernetes Secrets; the coprocessor password is fanned out to every namespace that runs a service, and re-read from an existing secret so that a partial run does not desynchronise them.
- **Registry credentials** for `hub.zama.org`, in every namespace including `kube-system` and `karpenter`.
- **Grafana Cloud credentials**, provided by Zama.
- **RPC credentials** for Ethereum, for Polygon, and for the Gateway.

The RPC URLs are validated for their scheme, and on a mainnet cluster any URL containing `sepolia`, `amoy` or `testnet` requires an explicit confirmation. A second script, `new-blockchain-bootstrap.sh`, copies the database and registry secrets into a new `<chain>-blockchain` namespace when a host chain is added later, precisely because regenerating the password would break the one already set in RDS.

### Step 2: database roles

The `coprocessor-rds-postgres-jobs` chart renders one Kubernetes Job per values file. `helm-values/utils/rds-user-creation.yaml` is the first one to run: an init container fetches the RDS master credentials from Secrets Manager into a `medium: Memory` volume, and the main container runs `psql` as the master user to create or update three roles. `coprocessor_user` gets `CONNECT`, `CREATE` and ownership of the `public` schema; `postgres_exporter` gets `pg_monitor`; `sql_exporter` gets read-only access to every current and future table, the latter through `ALTER DEFAULT PRIVILEGES FOR ROLE coprocessor_user`, which requires the master user to be granted membership of `coprocessor_user` first.

Other values files under `utils/` reuse the same chart for a database dump, a reset, and a bulk copy of the ciphertext corpus from a Zama-owned bucket into the partner's bucket with `s5cmd sync --size-only`, run as a non-root pod with a read-only root filesystem.

### Step 3: pre-flight checks

The `coprocessor-operator-check` chart installs a single Job as a `pre-install,pre-upgrade` Helm hook. Its init containers run in sequence and any failure blocks the release:

1. `k8s-check` lists every namespace, secret, ConfigMap key and `ExternalName` service the stack needs and prints a tick or a cross for each.
2. `aws-check` fetches `https://<storage hostname>` and requires a 200 with a `ListBucketResult` body.
3. `kms-check` resolves the tx-sender's AWS KMS key to an Ethereum address with Foundry's `cast`.
4. `fetch-rds-secret` pulls the master credentials into memory, and `db-check` lists roles, memberships, schema ownership and default privileges.

The RBAC the job needs is a ClusterRole limited to `get` and `list` on namespaces, secrets, services and ConfigMaps, deleted once the hook succeeds; every container drops all Linux capabilities.

### Step 4: the Helm releases

The coprocessor Helm chart itself lives in the `fhevm` repository (`charts/coprocessor`, at version 0.13.20 at the revision read). The operator repository supplies one values file per release, and the pattern is that each release enables exactly one part of the chart and disables the rest:

| Release (mainnet) | Enabled | Namespace | Notes |
|---|---|---|---|
| `values-coproc-infra-db-mig-mainnet.yaml` | `dbMigration` | `coproc` | One-shot; declares both host chains with their ACL addresses |
| `values-eth-coproc-listener-mainnet.yaml` | `hostListener`, `hostListenerPoller` for Ethereum | `eth-blockchain` | Block time 12 s, reorg window 50, finality lag 15 |
| `values-polygon-coproc-listener-mainnet.yaml` | Same for Polygon | `polygon-blockchain` | Block time 2 s, reorg window 120, finality lag 120, `--start-at-block` pinned to the deployment block of the v0.13 contracts |
| `values-gw-coprocessor-mainnet.yaml` | `gwListener`, `txSender` | `gw-blockchain` | Gateway WSS and HTTPS from `conduit-credentials`; tx-sender signs with AWS KMS |
| `values-coproc-workers-mainnet.yaml` | `tfheWorker`, `zkProofWorker`, `snsWorker` | `coproc` | The heavy pool; S3 bucket name from `coprocessor-config` |

Contract addresses are not typed into values: the chart renders ConfigMaps (`eth-sc-addresses`, `polygon-sc-addresses`, `gw-sc-addresses`) from a `network: mainnet` selector, and every service reads `acl.address`, `fhevm_executor.address`, `kms_generation.address` or the Gateway contract addresses from them. Adding a host chain therefore means a new namespace, a new listener release, a new entry in the `chains` list of the migration and worker releases, and a run of `new-blockchain-bootstrap.sh`.

All workloads use a `RollingUpdate` strategy with `maxUnavailable: 0` and a single replica, and expose a metrics port scraped by a `ServiceMonitor`; the tx-sender and gw-listener also expose `/liveness` and `/healthz` probes. Tracing goes to the in-cluster Alloy receiver over OTLP and from there to Grafana Cloud.

### Step 5: the signing key

The tx-sender's key is the operator's identity on the Gateway: `GatewayConfig` registers it as `txSenderAddress`, and a transaction from any other address is refused. The repository's third script, `import-eth-key-to-kms-cross-account.sh`, handles the case where the key was generated elsewhere: it reads a hex private key from Secrets Manager in a source AWS account, converts it to PKCS#8 DER, imports it as external key material into a `PendingImport` KMS key in the operator's account, and prints the resulting public key. After that the private key exists only inside KMS, and the tx-sender signs through the AWS API with the credentials of its IRSA-bound service account.

## Operating the node

Three mechanisms in the code are what an operator will meet once the node runs.

**Cursors and replay.** Both the listener and the poller keep their position in the database. The listener's `--start-at-block` overrides its position on every start, which is why the Polygon values carry a comment to remove it after the first deployment; the poller's `--seed-start-block` is read only when no row exists. Moving a poller backward is a SQL `UPDATE` on `host_listener_poller_state`, done with the poller scaled to zero, and the repository keeps the patch job that did exactly that on Amoy, with the block chosen a thousand blocks before the first observed protocol event.

**Slow lane and retries.** Nothing in the worker is abandoned for running out of attempts. A chain that exceeds the dependent-operations cap, or a row that has exhausted its retries, is marked slow and picked up after all ordinary work; the metric to alert on is `host_listener_slow_lane_marked_chains_total`, and the host-listener README carries a runbook for the case where the slow lane itself is the cause of a stall.

**Blue-green upgrades.** Newer than the v0.13 operator values, the workspace contains an `upgrade-controller` and a `consensus-detector`. An upgrade is proposed on-chain through `ProtocolConfig.proposeCoprocessorUpgrade` with a version and a block window per host chain; the current stack (the *blue* side) keeps serving, a candidate stack with a higher consensus protocol version (the *green* side) computes the same blocks in dry-run into its own database schema, each operator publishes a per-block state hash to S3, and the consensus detector polls every operator's bucket for unanimous agreement on those hashes before the switch. It is the operational form of the protocol's "anyone can recompute and compare" claim, applied to the operators themselves before they change software.

## Conclusion

A Zama coprocessor is a pipeline of six single-purpose Rust services around one PostgreSQL database and one S3 bucket, and running one is mostly a matter of getting that database, that bucket and one signing key right.

- **Two listeners write work**: the host-listener turns executor and ACL events into a computation graph organised in dependence chains; the gw-listener turns input-verification requests into proof-checking rows.
- **Three workers consume it**: tfhe-worker evaluates operations with TFHE-rs, zkproof-worker verifies and signs inputs, sns-worker prepares ciphertexts for the KMS and uploads them.
- **One sender speaks for the node**, posting input attestations and ciphertext commitments to the Gateway with a key held in AWS KMS.
- **The operator repository supplies what Terraform does not**: a secrets bootstrap, database role jobs, a pre-flight check hook, and one values file per release for testnet and mainnet, with the CPU and memory figures of the production pools.
- **Reliability comes from the database**: idempotent inserts, leased locks on dependence chains, finality-lagged pollers, unlimited retries on commitments, and cursors an operator can move with SQL.
- **Upgrades are being made verifiable**: a blue-green mechanism with per-block state hashes compared across operators before a switch.

![Mindmap of the coprocessor: its four responsibilities, the six services and their channels, the end-to-end data path, the infrastructure and deployment steps, and the operating mechanisms]({{site.url_complet}}/assets/article/blockchain/zamafhe/2026-09-18-zama-coprocessor-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Symbolic execution** | The on-chain model where `FHEVMExecutor` derives result handles and emits events instead of computing; the coprocessor consumes those events. |
| **Dependence chain (DCID)** | A connected component of the operation dependency graph, possibly spanning blocks, that a tfhe-worker locks and evaluates as a unit. |
| **Switch-and-squash** | The conversion of a TFHE ciphertext into a larger-domain form the KMS requires for threshold decryption, performed by the sns-worker. |
| **Ciphertext commitment** | The pair of digests (regular and squashed) a coprocessor posts to `CiphertextCommits`; decryption waits for a majority of identical commitments. |
| **Input attestation** | The EIP-712 signature a zkproof-worker produces over verified input handles, the user, the contract and the chain id; checked on-chain by `InputVerifier`. |
| **Host-listener poller** | The catch-up listener that re-reads finalised blocks over HTTP at a fixed lag, guarding against events lost by the WebSocket subscription. |
| **Slow lane** | A scheduling priority for dependence chains that are too long or have failed repeatedly; processed only when ordinary work is exhausted. |
| **`ExternalName` service** | The Kubernetes service `coprocessor-database` in `coproc` that resolves to the RDS endpoint, so every namespace reaches the database by one name. |
| **IRSA** | IAM Roles for Service Accounts; how the `db-admin`, `sns-worker` and `tx-sender` service accounts obtain AWS permissions without static credentials. |
| **Blue-green upgrade** | The mechanism in which a candidate stack computes the same blocks in dry-run and operators compare per-block state hashes before switching. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| An operation is evaluated only after every input ciphertext it depends on exists. | Dependence-chain formation in the host-listener and the worker's acquisition query on `computations`. | A chain is split incorrectly across blocks, or a worker bypasses the lock. |
| One dependence chain is processed by one worker at a time. | Leased locks in `dependence_chain` with a TTL and time slice; stale leases are reclaimed. | The lock TTL is shorter than the evaluation time and two workers evaluate the same chain. |
| A commitment posted to the Gateway matches the object in the operator's bucket. | The sns-worker computes the digest from the uploaded bytes and rechecks S3 before notifying the tx-sender. | The bucket is overwritten or the Cloudflare hostname serves a different bucket. |
| Every Gateway transaction from the node comes from the registered `txSenderAddress`. | The tx-sender signs with the AWS KMS key whose address is in `GatewayConfig`. | The KMS key is rotated without re-registering the operator. |
| A finalised host-chain event is ingested exactly once. | Unique keys on `computations` and `allowed_handles`; poller cursor in `host_listener_poller_state`. | The poller cursor is moved past events, or the reorg window is shorter than a real reorg. |
| Input-verification responses are never replayed against another chain or contract. | The EIP-712 signature covers user, contract and chain id; `InputVerifier` checks the chain id encoded in the handle. | The tx-sender signs with a key not registered as `signerAddress`. |

### Integration Notes

| Behaviour | What an operator should do |
|-----------|------------------------------|
| `--start-at-block` on the listener overrides the saved position on every restart. | Remove it from the values after the first deployment; use the poller's `--seed-start-block` or a SQL cursor patch to move a position. |
| The gw-listener resumes from the head after a dropped subscription and may skip input-verification requests. | Accept it; clients retry input registration. Keep `provider-max-retries` high so the reconnect itself is reliable. |
| Input-verification responses stop retrying after six attempts; ciphertext commitments never stop. | Alert on the commitment retry gauge; a stuck commitment blocks decryption for every user of that handle. |
| The three RDS passwords exist only in Kubernetes Secrets. | Back up the Secrets, and never re-run the RDS step of `secrets-bootstrap.sh` with the secrets deleted. |
| A GPU image runs only on the compute capability in its tag. | Match the tag (`sm90` for H100/H200, `sm89` for L40) to the node pool; there is no floating `:gpu` tag. |
| The check hook blocks a Helm release on any missing resource. | Run Terraform, then `secrets-bootstrap.sh`, then the DB user job, before the first `helm upgrade --install`. |
| Adding a host chain does not populate its namespace's secrets. | Run `new-blockchain-bootstrap.sh <ns>` and add the chain to the `chains` list of the migration and worker releases. |

## Frequently Asked Questions

**Q: Why do the services communicate through PostgreSQL instead of a message queue?**

Because the database is also the system of record: computations, ciphertexts, allowed handles, proofs and transactions all live there, and every service's progress is a row it can be restarted from. `LISTEN`/`NOTIFY` channels such as `event_zkpok_new_work` and `event_ciphertexts_uploaded` give the queue behaviour without a second stateful component, and polling intervals on every worker cover a missed notification.

The cost is that the database is the scaling and availability bottleneck, which is why it is a managed RDS instance with its own exporters and why the operator tooling is mostly about it.

**Q: Which of the six services needs the operator's Ethereum key, and where is it?**

Only the tx-sender. On mainnet the key is an AWS KMS key of type `ECC_SECG_P256K1`; the service signs through the AWS API under an IRSA-bound service account and never sees the private scalar. The same signer object signs the EIP-712 input attestations and the transactions, so in this deployment the `signerAddress` and `txSenderAddress` registered on the Gateway are backed by the same key. The `import-eth-key-to-kms-cross-account.sh` script exists for operators whose key was generated before the KMS key was created.

**Q: A host chain reorganises. What happens to computations already evaluated?**

The listener does not roll back. It tracks block validity and finality (`blocks_valid`, `host_chain_consumer_blocks`), waits `--catchup-finalization-in-blocks` before treating a block as final, and expects reorgs no deeper than `--reorg-maximum-duration-in-blocks`. Work ingested from an orphaned block is superseded when the canonical block is ingested, and the poller, running at a finality lag behind the head, re-reads the canonical history. A reorg deeper than the configured window is an operational incident, not something the code handles.

**Q: How does the KMS find a ciphertext when it has to decrypt it?**

From the handle. The Gateway's `CiphertextCommits` holds the digests a majority of coprocessors agreed on, and `GatewayConfig` holds each coprocessor's `s3BucketUrl`. A KMS party downloads the squashed ciphertext from any operator's bucket, checks that its digest matches the consensus, and only then engages the threshold protocol. This is why the `aws-check` insists that the bucket be publicly listable through the custom hostname: a bucket the KMS cannot read is a coprocessor whose commitments are useless.

**Q: Combine the scheduling and the trust model: what does a coprocessor that is slow, and one that is wrong, each cost the protocol?**

A **slow** coprocessor delays its own commitments. As long as a majority of the others have committed, the handle is already decryptable and the slow node catches up; a commitment it never posts is retried forever and visible in its metrics.

A **wrong** coprocessor posts a digest that disagrees with the majority. The Gateway does not count it toward consensus, the KMS never downloads that ciphertext, and the divergent commitment is a signed on-chain record that governance can act on.

Neither can corrupt a result that the majority computed correctly, which is the assumption the whitepaper states and the commitment flow implements.

**Q: What is the minimum hardware for a mainnet node, according to the values files?**

Two node pools and three managed services:

- **FHE pool**: tfhe-worker on 88 CPUs and 128 GiB; zkproof-worker and sns-worker on 48 CPUs and 128 GiB each; one replica of each.
- **Light pool**: the host listeners and pollers, the gw-listener on 8 CPUs and 16 GiB, and the tx-sender, on 1 to 8 CPUs each.
- **Managed services**: a PostgreSQL instance, an S3 bucket, and a KMS key.

GPU images exist for the three heavy workers, but the v0.13 mainnet values use the CPU builds.

## References

### Analyzed source

- [zama-ai/coprocessor-operator](https://github.com/zama-ai/coprocessor-operator) — analyzed at commit [`6dcf7f726bcd76f676a8199a3bc632d94d889950`](https://github.com/zama-ai/coprocessor-operator/tree/6dcf7f726bcd76f676a8199a3bc632d94d889950) (release [v0.4.9](https://github.com/zama-ai/coprocessor-operator/releases/tag/v0.4.9)), 2026-09-18
- [zama-ai/fhevm](https://github.com/zama-ai/fhevm) — `coprocessor/fhevm-engine`, `charts/coprocessor` and `gateway-contracts`, analyzed at commit [`ac6ff45ebb27c1300cc44669235751c657b3ce14`](https://github.com/zama-ai/fhevm/tree/ac6ff45ebb27c1300cc44669235751c657b3ce14) (50 commits after tag [`v0.14.1`](https://github.com/zama-ai/fhevm/releases/tag/v0.14.1)), 2026-09-18

### Protocol documentation

- [Coprocessor](https://docs.zama.org/protocol/protocol/overview/coprocessor)
- [Gateway](https://docs.zama.org/protocol/protocol/overview/gateway)
- [Zama Confidential Blockchain Protocol Litepaper](https://docs.zama.org/protocol/zama-protocol-litepaper)
- [Zama Coprocessor Terraform Modules](https://github.com/zama-ai/terraform-coprocessor-modules)
- [TFHE-rs](https://github.com/zama-ai/tfhe-rs)

### Standards and tools

- [EIP-712 — Typed structured data hashing and signing](https://eips.ethereum.org/EIPS/eip-712)
- [Helm chart-testing](https://github.com/helm/chart-testing)
- [Karpenter](https://karpenter.sh/)
- [AWS KMS asymmetric keys](https://docs.aws.amazon.com/kms/latest/developerguide/symmetric-asymmetric.html)
- [IAM roles for service accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)

### Related articles

- [Inside the Zama KMS — Threshold Key Management for FHE, From MPC Protocol to Enclave Deployment]({{site.url_complet}}/2026/09/18/zama-kms-threshold-key-management-architecture-and-operation/)
- [Zama FHEVM Architecture — Components, Data Flow and What Has to Be Trusted]({{site.url_complet}}/2026/09/18/zama-fhevm-architecture-components-trust-model/)
- [The Zama FHEVM Whitepaper — What It Specifies, and What the Code Does Differently]({{site.url_complet}}/2026/09/18/zama-fhevm-whitepaper-vs-implementation/)
- [Zero-Knowledge Proofs in the Zama Protocol — What They Prove and Where They Are Verified]({{site.url_complet}}/2026/07/24/zero-knowledge-proofs-zama-protocol/)

### Tooling

- [Claude Code](https://claude.com/product/claude-code)
