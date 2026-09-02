---
layout: post
title: "Rundler — Inside Alchemy's ERC-4337 Bundler"
date:   2026-07-30
lang: en
locale: en-GB
categories: blockchain ethereum programmation
tags: blockchain ethereum erc-4337 erc-7562 erc-7769 account-abstraction bundler rundler rust mempool gas-estimation eip-7702
description: How Rundler implements an ERC-4337 bundler in Rust — the Pool, Builder and RPC tasks, mempool simulation and reputation, the bundle sender state machine, gas estimation, signature aggregation and multi-entry-point support.
image: /assets/article/blockchain/ethereum/erc-4337/2026-07-30-rundler-alchemy-erc4337-bundler.png
isMath: false
---

A bundler occupies an uncomfortable position in [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337). It spends its own ETH to submit a transaction containing other people's user operations, and it is reimbursed only if those operations validate on-chain. Everything between accepting an operation and being paid for it is the bundler's problem: deciding what to admit, predicting what will still be valid several seconds later, and getting a transaction mined at a price that leaves a margin.

Rundler is Alchemy's answer, written in Rust and running in production behind their Bundler API. This article walks through how it is built — the three tasks it splits into, what the mempool actually checks, how bundles are proposed and submitted, and how it estimates the three gas limits that ERC-4337 makes the client's responsibility. The standard itself, and the roles around the bundler, are covered in [ERC-4337: Account Abstraction Using Alt Mempool]({{site.url_complet}}/2025/05/02/erc-4337-overview/).

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The problem a bundler solves

The EntryPoint contract enforces a two-phase discipline: every operation in a batch is validated first, and only then are the calls executed. Reimbursement comes from ETH the account or paymaster has deposited with the EntryPoint. That arrangement makes the bundler's exposure bounded but not zero, because validation is simulated off-chain and executed on-chain, and the two can disagree.

[ERC-7562](https://eips.ethereum.org/EIPS/eip-7562) closes most of that gap by restricting what validation code may do — no banned opcodes, no reads of storage belonging to other accounts, limited gas — so that an off-chain simulation is a reliable prediction. Enforcing those rules is the bundler's job, and it is expensive: it requires a `debug_traceCall` over the validation phase of every incoming operation.

Everything in Rundler's design follows from that: keep the expensive check where it belongs, keep the mempool honest about what is still valid, and never submit a bundle whose failure the bundler will pay for.

## Three tasks

Rundler splits into **Pool**, **Builder** and **RPC**. Each can run in the same process with in-memory message passing, or as separate processes talking over gRPC. The binary exposes one subcommand per arrangement:

| Subcommand | Runs |
|------------|------|
| `node` | Pool, Builder and RPC in a single process |
| `rpc` | the RPC server alone |
| `pool` | the Pool, plus a gRPC endpoint |
| `builder` | the Builder, plus a gRPC endpoint |

![Rundler's three tasks and how they communicate]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/rundler-architecture-concept.png)

The split is what makes horizontal scaling possible. RPC and Builder are stateless; the Pool holds the mempool. A deployment can run many RPC front-ends and many builder workers against one stateful pool, which is how Rundler is deployed in Alchemy's cloud.

Communication is deliberately narrow. RPC pushes operations into the Pool on `eth_sendUserOperation`, and reaches the Builder only through the `debug_` namespace, to set bundling mode and trigger a bundle in tests. The interesting channel is Pool ↔ Builder: the Builder subscribes to the Pool's block stream, asks for the most valuable operations after each new block, re-simulates them, and reports back anything that failed so the Pool can evict it.

The codebase is around 72 000 lines of Rust — a binary crate plus a dozen libraries — with `builder` (~16 600 lines) and `pool` (~15 800) carrying most of the weight.

## Pool

The Pool runs **one mempool per enabled entry point**, driven by shared tracking logic but with entirely separate data structures.

### What happens to an incoming operation

![The path a user operation takes from RPC through the Pool to a mined bundle]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/rundler-userop-lifecycle-workflow.png)

**Prechecks** run first, and they are cheap. They cover the reasons an operation is obviously not minable — fees below what the bundler requires, gas limits above configured caps, the payer lacking funds, and a gas-limit efficiency test. The last one deserves a closer look: `verification_gas_limit_efficiency_reject_threshold` (default `0.5`) rejects operations whose simulated verification `gasUsed / gasLimit` ratio falls below the threshold. An operation that reserves 500 000 gas for verification and uses 50 000 is occupying bundle capacity it does not need, so the Pool refuses it.

Other precheck defaults give a sense of the envelope: `max_verification_gas` 5 000 000, `max_bundle_execution_gas` 10 000 000, `base_fee_accept_percent` 50, and `pre_verification_gas_accept_percent` 100 — the last enforced at 100 % unless the chain has dynamic PVG.

**Simulation** follows, via `debug_traceCall`, with a TypeScript-authored tracer compiled to JavaScript, embedded in the binary and passed to the node as a string parameter. The tracer collects the accesses and opcodes needed to check the ERC-7562 rules. Violations reject the operation.

Two escape hatches exist and both should be understood before they are used. `--unsafe` skips the rule checks and the trace entirely, for chains or nodes where `debug_traceCall` is unavailable. `--enable_unsafe_fallback` does the same, but only when the tracer errors.

**Time bounds** are checked last: an operation is accepted only if `validUntil` is more than 60 seconds away and `validAfter` has already passed. There is no point admitting an operation that will expire before a bundle can carry it.

### Reputation, allowlists, blocklists

The Pool implements ERC-4337 reputation scoring for global entities — factories, paymasters, aggregators — throttling and banning those whose operations repeatedly fail. Two configuration files override it outright: addresses in the **allowlist** are always `Ok` in the reputation manager, addresses in the **blocklist** are always `Banned`. Both accept a local path or an S3 URL, so a fleet can share one list.

Unstaked senders are additionally capped at `same_sender_mempool_count` operations (default `4`), and a replacement must raise the fee by `min_replacement_fee_increase_percentage` (default `10`).

### Chain tracking and reorgs

A chain tracker polls the node (default every 100 ms) and notifies the Pool of new blocks, mined operations and un-mined operations. Mined operations move into a cache rather than being discarded, so a reorg can return them to the mempool.

The cache depth is configurable and it is a real limit, not a formality: **a reorg deeper than the cache loses those operations permanently**. They cannot be restored to the pool, and the sender has to resubmit.

### Sharding and filtering

Two features exist for multi-consumer deployments.

**Sharding** partitions `best_operations` by `sender address mod num_shards`. Each caller passes a `shard_index` and receives a disjoint set. The operational requirement is exactly one caller per shard index — more than one causes bundle invalidations, none at all orphans those operations.

**Filtering** tags operations with a filter ID as they enter the mempool, so a builder configured with the matching `filterId` receives only those. The coupling runs both ways: every defined mempool filter needs a matching builder, or the operations it captures are never bundled.

[Alternative mempools](https://eips.ethereum.org/EIPS/eip-4337#alternative-mempools) are supported through a JSON configuration file, flagged in the documentation as preview-quality with known risks to the bundler.

## Builder

The Builder turns mempool contents into signed transactions and tracks them to a conclusion.

### Workers, signers and the Assigner

Rundler runs `--num_signers` workers. Each worker is paired **1:1 with a signer**, but — and this is the part that differs from a naive design — each worker services **every** configured entry point rather than being pinned to one.

The **Assigner** decides what each worker does per cycle:

- **Entry point selection** is throughput-first: pick the entry point with the most eligible operations. Starvation prevention overrides it — an entry point untouched for `num_signers × starvation_ratio` cycles is force-selected. With four signers and the default ratio of `0.50`, that is two idle cycles.
- **Sender assignment** guarantees no two workers bundle operations from the same sender at once, by tracking sender-to-worker assignments and filtering out operations held by another worker. Assignments release when the bundle completes.
- **Virtual entry points** let one entry point address carry several configurations, keyed by `filter_id`, that workers can build for independently.

### Proposing a bundle

The proposer receives assigned candidates and narrows them down.

**Required fees** are set by the configured priority fee mode, which is where a deployment tunes its own profitability:

- `priority_fee_increase_percent` — the operation's priority fee must exceed the bundle's by N %.
- `base_fee_percent` — the operation's priority fee must be N % of the base fee.

**Gas limit**: the proposer sums each operation's maximum possible gas usage (`preVerificationGas` + `verificationGasLimit` + `callGasLimit`) and stops adding when the bundle would exceed the cap. An operation that overflows the cap is skipped along with everything after it, but stays in the pool. Bundle size is separately capped by `max_bundle_size` (default `128`).

**Second simulation** is the important step. Every candidate is re-simulated and its validation rules re-checked; failures are removed from the bundle *and* from the pool. Then the assembled bundle is validated as a whole through `eth_call`, and any operation that fails is removed — repeatedly, until the entire bundle passes. Only then is a signature aggregated and a transaction built.

### The sender state machine

![The bundle sender's four states and the transitions between them]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/rundler-bundle-sender-state.png)

Three triggers move a worker out of `Building`: a new block (automatic mode), the `bundle_max_send_interval_millis` timer, or a `debug_bundler_sendBundleNow` call in manual mode.

`Pending` waits up to `max_blocks_to_wait_for_mine` blocks (default `2`) before resending at a fee raised by `replacement_fee_percent_increase` (default `10` %).

The cancellation states exist for one specific deadlock. Operations are available that pay more than the estimated gas price, but submitting returns **"replacement underpriced"**; raising the fee to satisfy the node then prices those operations out. The worker is stuck between a transaction it cannot replace and operations it cannot afford. Rundler records the block number the first time it sees this and keeps trying; once the gap exceeds `max_replacement_underpriced_blocks` (default `20`), it moves to `Cancelling`.

The goal there is to clear the blocking transaction for as little as possible. A **hard** cancellation sends a deliberately empty transaction on-chain. A **soft** cancellation is an RPC interaction with no transaction at all — available with senders that support it. `max_cancellation_fee_increases` (default `15`) bounds how hard it tries before giving up and resetting.

### Signing

Four schemes, in configuration precedence order:

1. `--signer.enable_kms_funding` — a KMS-locked master key funding a set of sub-keys.
2. `--signer.private_keys` — raw keys on the command line.
3. `--signer.mnemonic` — BIP-39 derivation.
4. `--signer.aws_kms_key_ids` — KMS-locked keys.

**KMS locking** is the mechanism that makes a shared key pool safe. With `--signer.enable_kms_locking`, keys are leased through Redis before use, so two Rundler instances can be configured with the same key list without both grabbing the same key and colliding on transaction nonces. Redis is not optional here — it is the lock.

**KMS funding** adds a background process that watches sub-key balances and tops any that fall below `fund_below` back up to `fund_to` from the funding key. Sub-keys come from grouped KMS keys, private keys, or a mnemonic, in that order.

### Submitting

| Sender | Path |
|--------|------|
| `raw` | `eth_sendRawTransaction`, or `eth_sendRawTransactionConditional` with `--builder.use_conditional_rpc` |
| `flashbots` | Flashbots Protect — Ethereum mainnet only |
| `polygon_bloxroute` | Bloxroute private transactions — Polygon only |

A builder can also submit through a **proxy** contract instead of calling the EntryPoint directly, configured with `proxy` and `proxyType`. The proxy must expose the same ABI as `IEntryPoint` for `handleOps` and `handleAggregatedOps`. Two proxy types ship: `passthrough` (no logic) and `pbh`, which decodes the World Chain PBH entry point's custom revert reasons during simulation.

## RPC

Four namespaces, each independently enable-able, plus a health check endpoint.

### `eth_`

The methods specified by [ERC-7769](https://eips.ethereum.org/EIPS/eip-7769): `eth_chainId`, `eth_supportedEntryPoints`, `eth_estimateUserOperationGas`, `eth_sendUserOperation`, `eth_getUserOperationByHash`, `eth_getUserOperationReceipt`.

Two lookup methods take a **non-standard second positional parameter** scoping the `eth_getLogs` search for the `UserOperationEvent`. It accepts either a `{ fromBlock, toBlock }` object — hex quantities or block tags, with decimal JSON numbers rejected — or a block hash, which searches that block alone. When a maximum block range is enforced, both bounds become mandatory so the range can be validated, and an over-wide or inverted range is rejected with `-32602`. `eth_getUserOperationReceipt` additionally accepts `"PENDING"`, which on chains with preconfirmations returns a receipt before the operation lands on-chain.

### Per-request permission headers

Rundler accepts per-request policy as HTTP headers, parsed by transport-level middleware, so they apply across methods without changing any JSON-RPC signature. They are honoured **only** when `--rpc.permissions_enabled` is set.

| Header | Field |
|--------|-------|
| `X-Rundler-Trusted` | `trusted` |
| `X-Rundler-Max-Ops-In-Pool-For-Sender` | `maxAllowedInPoolForSender` |
| `X-Rundler-Underpriced-Accept-Pct` | `underpricedAcceptPct` |
| `X-Rundler-Underpriced-Bundle-Pct` | `underpricedBundlePct` |
| `X-Rundler-Eip7702-Disabled` | `eip7702Disabled` |
| `X-Rundler-Sponsorship-Max-Cost` | `bundlerSponsorship.maxCost` |
| `X-Rundler-Sponsorship-Valid-Until` | `bundlerSponsorship.validUntil` |
| `X-Rundler-Max-Block-Range` | (header only — event lookup scope) |

The parsing rules are strict in a way that is worth copying. A malformed value **fails the request closed with `400 Bad Request`** rather than falling back to a default, because a policy header that silently reverts to permissive is a security bug. A duplicated header is ambiguous and rejected. The sponsorship pair is coupled — both or neither.

`X-Rundler-Max-Block-Range` is the odd one out: it is lookup configuration, not a permission, and it never affects `eth_sendUserOperation`. On `eth_sendUserOperation`, headers take precedence over the deprecated positional `permissions` parameter when both are present.

What the permissions actually do:

| Permission | Effect |
|------------|--------|
| `trusted` | skip ERC-7562 simulation entirely, avoiding the `debug_traceCall` |
| `maxAllowedInPoolForSender` | override the per-sender mempool cap |
| `underpricedAcceptPct` | admit an operation paying only X % of estimated fees |
| `underpricedBundlePct` | bundle an operation paying only X % of bundle fees — the bundler eats the difference |
| `bundlerSponsorship` | the bundler pays all gas up to `maxCost` until `validUntil` |
| `eip7702Disabled` | reject [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) senders |

Every one of these removes a protection, which is why the documentation restricts them to trusted internal connections. `bundlerSponsorship` additionally requires the operation to have `maxFeePerGas`, `maxPriorityFeePerGas` and `preVerificationGas` all zero and no paymaster fields, and needs an out-of-band mechanism to refund the bundler.

### `rundler_`

| Method | Purpose |
|--------|---------|
| `rundler_maxPriorityFeePerGas` | suggested priority fee for operations |
| `rundler_getUserOperationGasPrice` | gas price — what Alchemy's `estimateFeesPerGas` SDK helper wraps |
| `rundler_getUserOperationStatus` | one-call status plus receipt |
| `rundler_getMinedUserOperation` | mined operation lookup |
| `rundler_getPendingUserOperationBySenderNonce` | pending operation by `(sender, nonce)` |
| `rundler_dropLocalUserOperation` | drop from the local pool |
| `rundler_sendSponsoredDelegation` | submit a signed EIP-7702 authorization, bundler-paid |
| `rundler_delegationStatus` | poll for that delegation's transaction hash |

`rundler_getUserOperationStatus` is the one worth knowing about as an integrator, because it collapses several round trips. It returns one of `unknown`, `pending`, `pendingBundle`, `mined` or `preconfirmed`, along with the receipt when mined, the operation itself, `addedAtBlock`, the `validUntil` / `validAfter` bounds, and — when the status is `pendingBundle` — the bundle's `txHash`, `sentAtBlock` and `bundlerAddress`. An integrator can distinguish "sitting in the mempool" from "already in a submitted bundle" without guessing.

`rundler_sendSponsoredDelegation` is **disabled by default**, and its documentation states the reason plainly: each submission queues a delegation that must acquire one of the bundler's signers. Unauthenticated access lets an attacker flood it and starve normal bundle sends of signers.

### `debug_` and `admin_`

`debug_` implements the ERC-7769 methods used by the ERC-4337 spec test suite, plus three non-standard additions — `debug_bundler_getStakeStatus`, `debug_bundler_clearMempool` and `debug_bundler_dumpPaymasterBalances`. It should be disabled on production endpoints. `admin_` carries `admin_clearState` and `admin_setTracking`.

## Gas estimation

ERC-4337 makes three gas limits the client's responsibility, and getting them wrong means either a rejected operation or wasted funds. `eth_estimateUserOperationGas` is where Rundler does the most interesting work, and its stated policy is to be as accurate as possible **while always erring toward over-estimation**.

![How Rundler produces preVerificationGas, verificationGasLimit and callGasLimit]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/rundler-gas-estimation-workflow.png)

### preVerificationGas

PVG covers gas the EntryPoint cannot meter during execution. Rundler splits it in two.

The **static** part covers the operation's calldata cost and its share of the EntryPoint's shared per-bundle overhead. It never changes for a given operation.

The **dynamic** part covers data availability on L2s that post to a separate chain. On Arbitrum One, for instance, a transaction is charged extra gas at the start of processing to pay for L1 calldata, and that figure moves with both L1 and L2 gas prices. Rundler queries the chain's precompile for it.

The consequence for integrators is direct: **on chains with dynamic PVG, add a buffer to the estimate**, or an operation priced when the estimate was taken can stop being minable when prices move.

Both calculations assume a **bundle size of 1**, so shared costs are never amortised across a real bundle.

### verificationGasLimit

A binary search, arranged to minimise `eth_call` round trips:

1. Run once at the maximum limit using a gas-measurement helper contract. Failure here means verification will never succeed, and the operation is rejected outright.
2. Seed the search at `gasUsed × 2`, to absorb the EVM's 63/64ths gas-forwarding rule.
3. Search until the lowest successful and highest failing values are within the allowed error (`--verification_gas_allowed_error_pct`, default 15).

A subtlety sits underneath: **verification always moves an asset**. Without a paymaster the sender transfers ETH to the EntryPoint; with an [ERC-20](https://eips.ethereum.org/EIPS/eip-20) paymaster the sender transfers tokens to the paymaster, which transfers ETH to the EntryPoint. The two cases need different treatment.

**Without a paymaster**, verification is estimated at **zero fees**, and the cost of one native transfer is added to the search result. This over-estimates by that transfer's cost when the account already has enough deposited at the EntryPoint to cover the prefund — an over-estimate Rundler accepts, since it does not change the on-chain cost.

**With a paymaster**, the fee fields have to be non-zero or the token transfer never triggers and the estimate misses its gas. The fee must be large enough to trigger a transfer (a USDC fee below `1e-6` rounds to nothing at six decimals) and small enough that a fee-payer holding a modest token balance can still cover the maximum gas. Rundler holds the total fee cost constant by varying `maxFeePerGas` against the current binary-search guess, and exposes the target through `VERIFICATION_ESTIMATION_GAS_FEE`, default 10 000 gwei.

This has a design implication for anyone **writing** an ERC-20 paymaster, and the documentation spells out three ways to handle an account that cannot cover that fee during estimation: absorb the balance error and return the signature-invalid code while still consuming representative gas; require callers to use state overrides to spoof the balance; or publish a hardcoded paymaster gas limit that clients apply on top of a paymaster-free estimate. On EntryPoint v0.7 the third option is cleaner, because `paymasterVerificationGasLimit` is a separate field.

### callGasLimit

Also a binary search, but the bulk of it runs **in Solidity** to avoid network round trips. That requires a spoofed EntryPoint: through `eth_call` state overrides, the real contract is moved aside and a proxy is loaded at its address, carrying the extra estimation logic. Call gas is always estimated at zero fees.

### State overrides

`eth_estimateUserOperationGas` accepts a Geth-format state override set as an optional third positional parameter. The canonical use is the ERC-20 paymaster case above — override the fee-payer's token or ETH balance so estimation can proceed.

### EIP-7623

Pectra's [EIP-7623](https://eips.ethereum.org/EIPS/eip-7623) raised the effective cost of calldata-heavy transactions by introducing a floor on `tx.gasUsed`. The EntryPoint has no visibility into that EVM-level calculation — it charges for the gas the operation uses plus `preVerificationGas` — so a user posting a large calldata payload can undercharge the bundler. Rundler compensates in PVG:

```
let lowest_gas_used =
    old_pvg +
    verification_gas_limit * verification_gas_efficiency_reject_threshold +
    execution_gas_limit * 0.1

if lowest_gas_used < uo_calldata_floor_gas_limit {
    return old_pvg + (uo_calldata_floor_gas_limit — lowest_gas_used)
} else {
    return old_pvg
}
```

The `0.1` is the EntryPoint's minimum 10 % charge on execution gas; the efficiency threshold is the same precheck constant from earlier. `lowest_gas_used` is therefore the least gas the operation can possibly consume on-chain, and the correction only applies when even that minimum falls under the calldata floor.

The trade-off is stated openly: because the bundler must assume minimum gas usage, an operation that triggers the correction *and* then uses more than its minimum is **overcharged**. The documentation's own worked example puts the crossover around 5 682 bytes of calldata, and the advice for anyone regularly posting large payloads is to tune their estimates so on-chain usage sits close to the minimum.

## Supporting four EntryPoint versions

Rundler supports EntryPoint **v0.6.0, v0.7.0, v0.8.0 and v0.9.0** at their canonical addresses:

| Version | Address |
|---------|---------|
| v0.6.0 | `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789` |
| v0.7.0 | `0x0000000071727De22E5E9d8BAf0edAc6f37da032` |
| v0.8.0 | `0x4337084D9E255Ff0702461CF8895CE9E3b5Ff108` |
| v0.9.0 | `0x433709009B8330FDa32311DF1C2AFA402eD8D009` |

Addresses can be overridden through the chain spec, but Rundler expects the contracts themselves to be unmodified — the override exists for chains lacking a deterministic deployment mechanism, not for forks.

Only **two ABIs** are needed: every version from v0.7 onward shares one. The type layer reflects that with a `UserOperation` trait for the common interface, a `UserOperationVariant` container implementing the trait by passthrough, and version-specific `v0_6::UserOperation` / `v0_7::UserOperation` types. The convention is that only genuinely version-specific code touches the concrete types; everything else takes the trait as a generic or handles the variant.

Each task absorbs the multiplicity differently. The Pool runs a **separate mempool per entry point**. The Builder's shared worker pool selects an entry point per cycle. The RPC runs **one server** and routes by the entry point address in the request — and for methods that do not carry one, such as `eth_getUserOperationReceipt`, searches every enabled entry point's logs.

## Signature aggregation

Rundler implements [ERC-7766](https://eips.ethereum.org/EIPS/eip-7766) but requires an **explicit registry** rather than accepting arbitrary aggregators. Three reasons are given, and they compound:

- An aggregator has a lot of power over a bundle, and the bundler must trust it not to cause a denial of service.
- The EntryPoint provides no way to meter an aggregator's gas on-chain, so the bundler has to charge for it through `preVerificationGas` — which requires knowing the aggregator's code.
- Most useful aggregators need an off-chain component to aggregate efficiently anyway.

Each implementation supplies an `AggregatorCosts` with four fields: `execution_fixed_gas` and `sig_fixed_length`, which *may* be amortised across a bundle, and `execution_variable_gas` and `sig_variable_length`, which every operation always pays. The documentation instructs implementers to determine these by simulation and hardcode them.

The aggregator address is passed as an **extra field** on `eth_estimateUserOperationGas` and `eth_sendUserOperation` — a deliberate, documented deviation from both ERC-4337 and ERC-7766. It lets the Pool look up the aggregator and validate the signature without first running `validateUserOp`, improving latency. It is not part of the `PackedUserOperation` and never goes on-chain.

One limitation currently undercuts the whole feature. PVG estimation, precheck fee checks, mempool DA fee checks and the builder's inclusion check all assume **a bundle of size 1**, so every operation is charged the aggregator's full fixed cost. Rundler's own documentation concludes this "renders a large class of aggregators as not useful", and notes that fixing it properly needs research rather than a patch. The two shipped implementations are BLS — described as mostly a proof of concept, not recommended for production — and World Chain's Priority Blockspace for Humans.

A related item on the roadmap is builder ↔ aggregator affinity: routing operations sharing an aggregator to the same builder so more of them can be aggregated together, with a configurable trade-off between time-to-mine and aggregation size.

## Poison user operations

A design document in the repository addresses a failure mode specific to bundling: an operation that consistently fails inside a multi-operation bundle without it being clear which operation is at fault. Left alone, one such operation can block bundle submission indefinitely.

The design pursues three goals at once, and the tension between them is the interesting part:

- **Liveness.** Failures attributable to a single operation remove it immediately. Ambiguous multi-operation failures move the candidates into *suspect isolation*, where each is retried alone. Repeated non-terminal failures are spaced with exponential backoff and eventually remove the operation. Setting `--pool.max_suspect_rpc_failures=0` deliberately disables that eventual removal.
- **Fairness.** Suspects cannot consume normal bundle capacity, because they are submitted alone and isolation is capped at `max(1, num_signers / 2)` while normal work remains. When normal work runs out, the cap expands so idle builders drain the suspect queue. Two-way starvation protection needs at least two builders — with one builder and both classes continuously eligible, no allocation rule can guarantee progress for both.
- **Provider resilience.** When a provider-health event is detected, removal pauses but *analysis continues*. The reasoning is adversarial: gating suspicion during an event would be exploitable, because a herd of poison operations large enough to trip the provider-event signal with its own failures would then be unsuspectable for exactly as long as it sustained the event. Keeping analysis live quarantines the herd even mid-event; the cost is that a genuine outage progressively suspects innocent operations, which is acceptable because suspicion is recoverable — one successful solo attempt clears a false suspect.

That third point is a good example of what separates a bundler design document from a protocol specification. The question is not "what is correct" but "what does an attacker do if we make the intuitive choice".

## Chain specification and running it

Chain-specific parameters come from a layered resolution, highest precedence first: `CHAIN_*` environment variables, then the `--chain_spec` TOML file, then the hardcoded spec named by `--network`, then a `base` spec if one is declared, then defaults. `base` resolution is **one level only** — a base that itself names a base does not resolve further. Hardcoded specs ship in `bin/rundler/chain_specs/`.

Rundler is tested on Ethereum, OP Stack chains (Optimism, Base, Zora, Frax explicitly), Arbitrum Orbit chains (Arbitrum One explicitly) and Polygon PoS, with the general claim that any OP Stack or Orbit chain should work.

The repository runs the ERC-4337 `bundler-spec-tests` for both v0.6 and v0.7 through `make test-spec-integrated`, alongside unit tests. Docker is the recommended way to run it, though no pre-built image is published.

Two licences apply: the library — everything outside `bin/` — is **LGPL-3.0**, and the binaries in `bin/` are **GPL-3.0**. Both are copyleft, which matters before vendoring any of it.

The status banner in the README is not boilerplate and should be read as written: Rundler is under active development, interfaces have breaking changes, and it is offered for production use *at your own risk* — even though Alchemy runs it in their own cloud.

## Conclusion

Most of what Rundler does is defensive. The mempool's prechecks, the efficiency threshold, the 60-second validity floor and the reputation system all exist to keep operations out that would waste bundle capacity. The proposer's second simulation and whole-bundle `eth_call` exist because the mempool's answer goes stale. The cancellation states exist because a stuck transaction is worse than a slow one. The poison-operation isolation exists because a bundler cannot always tell which operation broke a bundle.

The gas estimation section is where the ERC-4337 design pushes the most work onto the bundler, and Rundler's approach there is consistent: search rather than guess, run the search on-chain where round trips dominate, and over-estimate deliberately when the alternative is an operation that fails. The EIP-7623 correction is the clearest instance — a protocol change the EntryPoint cannot see, absorbed by the one component that can measure it, with the resulting over-charge documented rather than hidden.

The parts still marked incomplete are honest about it. Bundle-size-1 estimation makes signature aggregation impractical today, and the documentation says so rather than shipping the feature quietly.

![Mindmap summary of Rundler's architecture, tasks and features]({{site.url_complet}}/assets/article/blockchain/ethereum/erc-4337/2026-07-30-rundler-alchemy-erc4337-bundler.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Bundler** | An off-chain actor that collects user operations, packs them into a single transaction to the EntryPoint, and is reimbursed on-chain from the account's or paymaster's deposit. |
| **Pool** | Rundler's mempool task — one mempool per enabled entry point, responsible for prechecks, simulation, reputation and chain tracking. |
| **Builder** | Rundler's bundling task — a pool of workers that propose, sign, submit and track bundle transactions. |
| **Assigner** | The Builder component that selects which entry point each worker builds for on each cycle and ensures no two workers bundle the same sender concurrently. |
| **Precheck** | The cheap first-pass validation — fees, gas caps, payer funds, gas-limit efficiency — applied before the expensive `debug_traceCall` simulation. |
| **Gas-limit efficiency** | The ratio of an operation's gas limit to its simulated gas used; operations below the configured threshold (default `0.5`) are rejected for reserving bundle capacity they will not use. |
| **preVerificationGas (PVG)** | The gas an operation pays for work the EntryPoint cannot meter — calldata cost, shared bundle overhead, and on some L2s a dynamic data-availability component. |
| **Replacement underpriced** | The node error returned when a replacement transaction's fee is too low; the deadlock it creates with fee-sensitive operations is what Rundler's cancellation states resolve. |
| **KMS key leasing** | Redis-backed locking of AWS KMS signing keys, so multiple Rundler instances sharing a key list never use the same key concurrently and collide on nonces. |
| **Poison user operation** | An operation that repeatedly causes bundle failures without the cause being attributable; Rundler isolates such operations and retries them alone with exponential backoff. |

### Security Implementation Checklist

Derived from the behaviours described above. Aimed at anyone operating a Rundler deployment or integrating against one.

#### RPC exposure

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | `--rpc.permissions_enabled` is off, or the endpoint sits behind a trusted gateway. | `trusted` disables ERC-7562 simulation, reopening the mempool DoS the rules exist to prevent. |
| ☐ | `underpricedBundlePct` and `bundlerSponsorship` are reachable only by authenticated callers. | Both spend the bundler's own funds on operations that do not pay for themselves. |
| ☐ | `rundler_sendSponsoredDelegation` stays disabled, or is placed behind authentication before enabling. | Each call queues a delegation that must acquire a signer; flooding starves normal bundle sends. |
| ☐ | The `debug_` namespace is disabled on production endpoints. | `debug_bundler_clearState` and `debug_bundler_clearMempool` let any caller wipe the mempool. |
| ☐ | The `admin_` namespace is disabled or access-controlled. | `admin_clearState` and `admin_setTracking` alter node behaviour at runtime. |
| ☐ | A malformed policy header is treated as a hard failure, not a fallback to defaults. | A silently ignored policy header applies permissive defaults to a request meant to be constrained. |

#### Simulation integrity

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | `--unsafe` is used only on trusted, non-public deployments. | Skipping the rule checks admits operations whose validation succeeds in simulation and fails on-chain. |
| ☐ | `--enable_unsafe_fallback` is enabled only where a tracer error is a known, tolerated condition. | A node whose tracer is persistently broken silently degrades every operation to unsafe simulation. |
| ☐ | Second simulation and whole-bundle `eth_call` validation are left in place. | The mempool's admission decision is seconds old by bundling time; state may have moved under it. |
| ☐ | The gas-limit efficiency threshold is not lowered without cause. | Operations reserving far more verification gas than they use crowd out bundle capacity. |

#### Signing and funds

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | KMS signing runs with `--signer.enable_kms_locking` and a reachable Redis. | Two instances lease the same key and collide on transaction nonces, stalling both. |
| ☐ | Each configured worker has a distinct, funded signer. | Workers contend for keys, or a bundle is signed by an account that cannot pay. |
| ☐ | `fund_below` / `fund_to` are set so sub-keys cannot be drained mid-bundle. | A worker signs a bundle it cannot afford to submit. |
| ☐ | `max_cancellation_fee_increases` is bounded to a cost the operator accepts. | A cancellation loop escalates fees on an empty transaction against a congested chain. |

#### Operational correctness

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Reorgs deeper than the pool cache are handled out of band. | Un-mined operations cannot re-enter the pool and are lost without notice to the sender. |
| ☐ | Exactly one caller is assigned per mempool shard index. | More than one causes bundle invalidations; none orphans every operation in that shard. |
| ☐ | Every defined mempool filter has a builder with the matching `filterId`. | Operations captured by the filter are admitted to the pool and never bundled. |
| ☐ | A custom aggregator's `AggregatorCosts` are measured by simulation before registration. | The bundler underprices PVG and loses funds, or the aggregator stalls bundle building. |
| ☐ | Integrators on chains with dynamic PVG add a buffer to the estimate. | A price move between estimation and submission leaves the operation unminable. |
| ☐ | A submission proxy's custom revert reasons have a matching `proxyType`. | Bundle simulation misreads reverts and drops valid operations, or keeps invalid ones. |

## Frequently Asked Questions

**Q: Why does Rundler re-simulate operations in the Builder when the Pool already simulated them on admission?**

Because the Pool's answer was correct at admission time and may not be correct now. Chain state moves between the moment an operation enters the mempool and the moment a bundle carrying it is built — balances change, nonces advance, paymaster deposits are drawn down, and a validation that read any of that can flip.

Rundler therefore does it twice, at two granularities. Each candidate is re-simulated individually and its validation rules re-checked, with failures removed from both the bundle and the pool. Then the assembled bundle is validated as a whole through `eth_call`, and the process repeats until the whole bundle passes — because removing one operation can change the outcome for the others.

**Q: What is the "replacement underpriced" deadlock, and how do the cancellation states resolve it?**

It is a state where the bundler has operations paying more than the estimated gas price, but the node rejects its submission because a pending transaction from the same signer is priced too close. Raising the fee to satisfy the node's replacement rule then prices those very operations out — so the worker can neither replace the pending transaction nor build a bundle that pays.

Rundler records the block number when it first sees this and keeps retrying with reset fees. Once the gap exceeds `max_replacement_underpriced_blocks` (default `20`), it moves to `Cancelling`, whose only goal is to clear the blocking transaction as cheaply as possible: a hard cancellation sends a deliberately empty transaction, a soft cancellation is an RPC call with no transaction at all.

**Q: Why must a paymaster be present for Rundler to estimate verification gas with non-zero fees?**

Because an ERC-20 paymaster's gas cost depends on a token transfer that only happens if the fee is large enough to be non-trivial. Estimating at zero fees would skip the transfer entirely and return a limit that is too low for the real operation.

The fee has to sit in a window — large enough to trigger a transfer (a USDC fee below `1e-6` rounds to zero at six decimals) and small enough that a fee-payer with a modest balance can still cover the maximum gas. Rundler keeps the total fee cost constant by varying `maxFeePerGas` against the current binary-search guess, targeting `VERIFICATION_ESTIMATION_GAS_FEE` (default 10 000 gwei).

Without a paymaster none of this applies: verification is estimated at zero fees and the cost of one native transfer is added afterwards.

**Q: Rundler supports ERC-7766 signature aggregation but says most aggregators are not useful. What is the obstacle?**

The bundle-size-1 assumption. An aggregator's costs split into fixed components (`execution_fixed_gas`, `sig_fixed_length`) that *could* be amortised across every operation in a bundle, and variable components that every operation pays regardless.

Rundler currently assumes a bundle of size 1 during PVG estimation, precheck fee checks, mempool DA fee checks and the builder's inclusion check. Every operation is therefore charged the aggregator's full fixed cost as if it were alone — which is exactly the cost aggregation was supposed to share. Since the economics of most aggregators depend on that sharing, the feature works but rarely pays.

**Q: A provider outage is causing bundle failures. Why does Rundler keep marking operations as suspect instead of pausing that analysis?**

Because pausing it would be exploitable. If suspicion were gated on provider health, an attacker could assemble enough poison operations that their own failures trip the provider-event signal — and for exactly as long as they sustained that signal, they would be unsuspectable and would keep riding in normal bundles, blocking them.

Rundler splits the two instead: during a detected event, *removal* pauses — a suspect's counter freezes and makes no progress toward eviction — while *analysis* continues, so a poison herd is still quarantined into isolation. The cost is that a genuine outage progressively suspects innocent operations, which is tolerable because suspicion is recoverable: one successful solo attempt clears a false suspect.

**Q: An operation is accepted into the mempool but never mined, and the sender sees no error. What are the plausible causes?**

Several, and Rundler's own configuration surface names most of them:

- **Its fees stopped being competitive.** The Pool admits on `base_fee_accept_percent` (default 50 %), but the Builder applies the configured priority fee mode at bundling time. An operation can clear admission and never clear the bundle filter.
- **A reorg deeper than the pool cache dropped it.** Mined operations move into a cache for reorg replay; past that depth they cannot be restored, and the sender must resubmit.
- **It matched a mempool filter with no corresponding builder.** Filtered operations are only bundled by a builder configured with the same `filterId`; without one they sit in the pool indefinitely.
- **Sharding is misconfigured.** With no caller assigned to its shard index, an operation is never returned by `best_operations`.
- **Its gas exceeds what the proposer will pack.** An operation whose maximum gas usage overflows the bundle cap is skipped and left in the pool rather than rejected.
- **It has been isolated as a suspect.** Poison-operation handling retries it alone, with exponential backoff, until it either succeeds or reaches the removal threshold.

`rundler_getUserOperationStatus` distinguishes the first case from the rest, since it reports whether the operation is merely `pending` or already in a `pendingBundle`.

**Q: How does one RPC server handle four EntryPoint versions without four code paths?**

Two ABIs cover all four, because every version from v0.7 onward shares one — so only v0.6 needs separate handling. The type layer expresses this with a `UserOperation` trait for the shared interface, a `UserOperationVariant` container that implements the trait by passthrough, and concrete `v0_6::UserOperation` / `v0_7::UserOperation` types reserved for genuinely version-specific code.

Routing happens by the entry point address carried in the request. For methods that do not carry one — `eth_getUserOperationReceipt` being the example — Rundler searches every enabled entry point's logs for the hash.

## References

- [Rundler](https://github.com/alchemyplatform/rundler) — Alchemy, including `docs/architecture/`, `docs/cli.md` and `docs/designs/poison-user-operations.md`
- [Wallet APIs documentation](https://alchemy.com/docs/wallets) — Alchemy
- [ERC-4337 bundler reference implementation](https://github.com/eth-infinitism/bundler) and [bundler-spec-tests](https://github.com/eth-infinitism/bundler-spec-tests) — eth-infinitism
- [ERC-4337 gas estimation](https://www.alchemy.com/blog/erc-4337-gas-estimation) — Alchemy
- [ERC-4337: Account Abstraction Using Alt Mempool](https://eips.ethereum.org/EIPS/eip-4337)
- [ERC-7562: Account Abstraction Validation Scope Rules](https://eips.ethereum.org/EIPS/eip-7562)
- [ERC-7769: JSON-RPC methods for Account Abstraction](https://eips.ethereum.org/EIPS/eip-7769)
- [ERC-7766: Signature Aggregation for ERC-4337](https://eips.ethereum.org/EIPS/eip-7766)
- [EIP-7623: Increase calldata cost](https://eips.ethereum.org/EIPS/eip-7623)
- [EIP-7702: Set EOA account code](https://eips.ethereum.org/EIPS/eip-7702)
- [ERC-20: Token Standard](https://eips.ethereum.org/EIPS/eip-20)
- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [How Alchemy Implements Smart Wallets and Account Abstraction]({{site.url_complet}}/2026/07/30/alchemy-smart-wallet-account-abstraction/)
- [ERC-4337: Account Abstraction Using Alt Mempool]({{site.url_complet}}/2025/05/02/erc-4337-overview/)
- [SenderCreator in ERC-4337 — Deploying Accounts and Reading Counterfactual Addresses]({{site.url_complet}}/2026/07/23/sendercreator-entrypoint-erc4337-counterfactual-address/)
