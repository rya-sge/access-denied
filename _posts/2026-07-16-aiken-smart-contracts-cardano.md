---
layout: post
title: "Writing Cardano Smart Contracts with Aiken"
date:   2026-07-16
lang: en
locale: en-GB
categories: blockchain
tags: cardano aiken smart-contracts plutus eutxo validator uplc
description: A technical guide to Aiken, the smart-contract language for Cardano. Covers the eUTXO validator model, the single-binary toolchain, Plutus V3 validator handlers, parameterized minting policies, the built-in test runner, and the CIP-57 blueprint deployment flow.
image: /assets/article/blockchain/cardano/aiken-smart-contracts-cardano.png
isMath: false
---

Aiken is a programming language and toolchain for writing smart contracts on Cardano. It targets the same on-chain bytecode as every other Cardano contract language, but it was designed from scratch for that single job, and it ships the compiler, formatter, test runner, and language server in one binary. This article explains how Aiken fits into Cardano's execution model, how a validator is structured, how the toolchain takes source code to a deployable artifact, and where the common mistakes are. Code paths were checked against Aiken `v1.1.23` and the `hello_world` and `gift_card` examples in the [aiken-lang/aiken](https://github.com/aiken-lang/aiken) repository.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The execution model Aiken targets

Before any syntax, one fact governs everything: Cardano is not account-based. It uses the Extended UTXO (eUTXO) model, and a smart contract there is a **validator**, not an autonomous actor.

A validator cannot send funds, call another contract imperatively, read external state, generate randomness, or loop without bound. It is a pure function that receives a proposed transaction and answers one question: *may this transaction proceed?* Its signature is conceptually

```text
validator(datum, redeemer, context) -> Bool
```

- **Datum**: state data attached to the UTXO being unlocked.
- **Redeemer**: an argument the spender supplies to select an action or provide a witness.
- **Context**: the entire transaction under evaluation, including its inputs, outputs, minted value, signatories, and validity interval.

Because the validator sees the whole transaction and produces no side effects, its outcome is deterministic. The wallet or backend can evaluate a script off-chain, learn the exact execution cost, and know whether the node will accept the transaction before it is submitted. The developer-portal guide phrases the split as the off-chain code being the lawyer who drafts an agreement and the on-chain validator being the judge who only checks compliance. The creative work of assembling a valid transaction happens off-chain; the validator rejects anything that violates its rules.

The diagram below traces a spend from transaction construction to the node's phase-2 script evaluation.

![Sequence diagram of validator evaluation when spending a UTXO locked at a script address]({{site.url_complet}}/assets/article/blockchain/cardano/aiken-validator-evaluation-sequence.png)

This model is the reason Aiken exists in the form it does. The language does not need imperative I/O, concurrency primitives, or unbounded recursion, and leaving them out keeps compiled scripts small and their costs predictable.

## Everything compiles to UPLC

Every Cardano smart-contract language compiles to a single target: **UPLC** (Untyped Plutus Lambda Calculus), the bytecode the node's Plutus evaluator executes. The on-chain semantics are fixed by UPLC and the ledger rules, so the choice of source language is a question of ergonomics, not capability.

| Language | Suited to | Notes |
|----------|-----------|-------|
| **Aiken** | Most new projects | Purpose-built, small and fast output, built-in tests, emits a CIP-57 blueprint on build. |
| **Plinth / Plutus Tx** (Haskell) | Haskell teams | The original framework; full Haskell type system and on/off-chain code sharing, at the cost of a steep learning curve and larger scripts. |
| **Plutarch** | Maximum performance | Fine-grained control close to hand-written UPLC; hardest to use. |
| **OpShin** (Python) | Python teams | A typed subset of Python; pairs with PyCardano off-chain. |
| **Scalus** (Scala 3) | JVM teams | On-chain and off-chain in Scala. |
| **Marlowe** | Financial contracts | A domain-specific language, deliberately not Turing-complete, so termination is guaranteed. |

Aiken took syntax cues from Rust, Elm, and Gleam. It is on-chain only by design: off-chain code stays in whatever language the application already uses, which keeps the two halves of a contract cleanly separated. For a team with no prior commitment to the Haskell ecosystem, it is the shortest path to a correct, small validator.

![Component diagram showing multiple source languages compiling to UPLC and then to a CIP-57 blueprint executed by the Cardano node]({{site.url_complet}}/assets/article/blockchain/cardano/aiken-compilation-pipeline-concept.png)

## The toolchain

Aiken is distributed as a single executable that bundles the compiler, formatter, test runner, documentation generator, package manager, and language server. The recommended way to install it is `aikup`, the official version manager:

```bash
npm install -g @aiken-lang/aikup   # or: brew install aiken-lang/tap/aikup
aikup                              # installs the latest release
aiken --version                    # verify
```

Alternatives are `cargo install aiken`, the Nix flake in the repository, or the browser playground at `play.aiken-lang.org` for experiments that need no local setup.

The command surface, taken from the CLI source (`crates/aiken/src/cmd/mod.rs`):

| Command | Purpose |
|---------|---------|
| `aiken new <owner/repo>` | Scaffold a project. The name must use the `owner/repo` form. |
| `aiken build` (alias `b`) | Type-check and compile every validator to `plutus.json`. |
| `aiken check` (alias `c`) | Type-check and run tests. `-m <pattern>` filters by test name. |
| `aiken fmt` | Format source files. |
| `aiken add <owner/repo>` | Add a dependency. |
| `aiken docs` | Generate HTML API documentation from doc comments. |
| `aiken bench` | Run benchmarks. |
| `aiken blueprint <sub>` | Operate on `plutus.json`: `apply`, `address`, `policy`, `hash`, `convert`. |
| `aiken packages <sub>` | `add`, `upgrade`, `clear-cache`. |
| `aiken tx simulate` | Evaluate a transaction's scripts and report execution units. |
| `aiken uplc <sub>` | Low-level UPLC tooling: `eval`, `encode`, `decode`, `fmt`, `shrink`. |

`aiken new` produces a fixed layout:

```text
my-project/
├── aiken.toml                 # manifest: name, version, plutusVersion, dependencies
├── env/                       # per-network environment modules (selected with -e)
├── lib/                       # reusable non-validator modules
└── validators/                # validator modules, one entry each in plutus.json
    └── placeholder.ak
```

The manifest declares the Plutus version and dependencies. New projects should target Plutus V3:

```toml
name = "aiken-lang/hello_world"
version = "1.0.0"
plutusVersion = "v3"
description = "Aiken contracts for project 'aiken-lang/hello_world'"

[[dependencies]]
name = "aiken-lang/stdlib"
version = "v2"
source = "github"
```

## Anatomy of a validator

A file in `validators/` defines one or more **handlers**, one per script purpose. Under Plutus V3 the purposes are `spend`, `mint`, `withdraw`, `publish`, `vote`, and `propose`, plus an `else` fallback that catches any purpose the validator does not handle explicitly. This set is fixed by the compiler (`crates/aiken-lang/src/ast.rs`).

The `hello_world` example is a complete spend validator:

```gleam
use aiken/collection/list
use aiken/crypto.{VerificationKeyHash}
use cardano/transaction.{OutputReference, Transaction}

pub type Datum {
  owner: VerificationKeyHash,
}

pub type Redeemer {
  msg: ByteArray,
}

validator hello_world {
  spend(
    datum: Option<Datum>,
    redeemer: Redeemer,
    _own_ref: OutputReference,
    self: Transaction,
  ) {
    let must_say_hello = redeemer.msg == "Hello, World!"
    expect Some(Datum { owner }) = datum
    let must_be_signed = list.has(self.extra_signatories, owner)
    must_say_hello && must_be_signed
  }

  else(_) {
    fail
  }
}
```

Three properties of this handler generalise to every validator:

1. **It returns a `Bool`.** `True` approves the transaction; `False`, an `expect` that does not match, or `fail` rejects it.
2. **It never acts; it constrains.** Every rule is a predicate over `self`, the transaction. Here it reads `self.extra_signatories`. Other validators inspect `self.mint`, the inputs and outputs, or `self.validity_range`.
3. **The datum is optional.** In Plutus V3 an output at a script address may carry no datum, so `datum` has type `Option<...>` and the `None` case must be handled. The `expect Some(...) = datum` line rejects the spend if the datum is absent or malformed.

### Parameterized validators and minting policies

A validator can take **compile-time parameters**, written after its name. Applying different parameters yields a different compiled script, and therefore a different script address or minting policy ID. This is how one source file produces many independent on-chain instances.

The `gift_card` example uses parameters to build a one-shot minting policy: a token that can be minted exactly once. It is parameterized on a token name and a specific UTXO reference, and the `mint` handler only approves minting when that exact UTXO is spent in the same transaction. Since a UTXO can be spent only once, the mint can happen only once.

```gleam
validator gift_card(token_name: ByteArray, utxo_ref: OutputReference) {
  mint(rdmr: Action, policy_id: PolicyId, self: Transaction) {
    let Transaction { inputs, mint, .. } = self
    expect [Pair(asset_name, amount)] =
      mint |> assets.tokens(policy_id) |> dict.to_pairs()
    when rdmr is {
      Mint -> {
        expect Some(_) =
          list.find(inputs, fn(i) { i.output_reference == utxo_ref })
        amount == 1 && asset_name == token_name
      }
      Burn -> amount == -1 && asset_name == token_name
    }
  }
  else(_) { fail }
}
```

Two checks in the `Mint` branch matter for correctness and are easy to get wrong: the handler pins both the exact `asset_name` and the exact `amount`. Verifying quantity without pinning the asset name is a documented eUTXO pitfall (the *other-token-name* class), since a policy that checks only quantity can be satisfied by minting a different name under the same policy.

Parameters are supplied at deployment time with `aiken blueprint apply`, which rewrites the generic blueprint into a concrete, applied script.

## The standard library

`aiken-lang/stdlib` provides the types and functions a validator reaches for. It is added with `aiken add aiken-lang/stdlib` and the current major line is `v2`. The modules seen most often:

- `aiken/collection/list`, `aiken/collection/dict`, `aiken/collection/pairs` for collections.
- `aiken/crypto` for `VerificationKeyHash`, hashes, and `blake2b_256`.
- `aiken/primitive/bytearray`, `aiken/primitive/int`, `aiken/primitive/string`.
- `cardano/transaction` for `Transaction`, `OutputReference`, `Input`, and `Output`.
- `cardano/assets` for `Value`, `PolicyId`, and helpers such as `tokens` and `quantity_of`.
- `cardano/address` for `Address` and `Credential`.
- `cardano/certificate` and `cardano/governance` for the `publish`, `vote`, and `propose` handlers.

## Testing without an external framework

Aiken has a test runner built into the compiler, so a project needs no separate test dependency. A test is a function marked with the `test` keyword that returns a `Bool`:

```gleam
test or_else_2() {
  or_else(Some(42), 14) == 42
}
```

`aiken check` runs every test and reports the CPU and memory **execution units** each one consumed, so tests double as cost measurements against the same budget the ledger enforces. `aiken check -m or_else` runs only tests whose name matches the pattern.

The runner supports three further modes:

- **Property-based tests.** A `test` that takes an argument becomes a property test. Aiken generates sampled inputs through a `Fuzzer`, and on failure it shrinks the input toward a minimal counterexample.
- **Failure expectations.** `test foo() fail { ... }` asserts that the body errors, which is how you check that a validator rejects an invalid transaction.
- **Benchmarks.** Functions measured by `aiken bench` track cost across sampled inputs.

To exercise a full validator, a test constructs a mock `Transaction`, calls the handler directly, and asserts on the returned `Bool`. Because there is no network and no node in the loop, these tests are fast and deterministic.

## From source to a deployable script

`aiken build` produces `plutus.json`, a **CIP-57 Plutus blueprint**. The blueprint is the contract's interface description, analogous to an ABI: it lists every validator, the schemas of its datum, redeemer, and parameters, and the compiled UPLC. Off-chain code consumes the blueprint rather than the Aiken source, and tooling generates TypeScript, Python, or Rust types from it.

The deployment flow reads and rewrites that blueprint:

```bash
aiken build                              # -> plutus.json
aiken blueprint apply -v <name> <PARAM>  # bake in a compile-time parameter
aiken blueprint policy  -v <name>        # minting policy id (for a mint validator)
aiken blueprint address -v <name>        # bech32 script address (for a spend validator)
aiken blueprint hash    -v <name>        # script hash
```

![Activity diagram of the Aiken build and deployment flow from validators to the off-chain application]({{site.url_complet}}/assets/article/blockchain/cardano/aiken-blueprint-deploy-activity.png)

From there the off-chain application takes over: it reads `plutus.json`, derives the addresses and policy IDs, and builds transactions the validator will approve. The `hello_world` example does this in plain TypeScript (`lock.ts` and `unlock.ts`); the `gift_card` example wires the same blueprint into a full SvelteKit application. Common off-chain libraries are Lucid Evolution, Mesh, cardano-serialization-lib, Blaze, and PyCardano, with any CIP-30 browser wallet on the front end.

## Security considerations specific to eUTXO

Aiken removes whole classes of bugs by construction (no reentrancy, no unbounded loops, deterministic costs), but eUTXO has its own catalogue of mistakes that the compiler cannot catch. A validator only enforces what it explicitly checks, and forgetting a check is the usual failure mode. The recurring classes:

- **Double satisfaction**: one output is counted as satisfying two independent validators in the same transaction.
- **Arbitrary or unbounded datum**: trusting an attacker-supplied datum, or one large enough to make the output expensive to spend.
- **Missing UTXO authentication**: trusting that a UTXO holds particular state without an identifying token to prove it.
- **Other token name**: a minting policy that checks the minted quantity but not the exact asset name.
- **Insufficient staking control**: validating the payment part of an address while ignoring the staking part.

These are cross-language properties of the model, not of Aiken specifically. A validator should be reviewed against them regardless of the source language, and the review belongs before any mainnet deployment.

## Conclusion

Aiken is a focused tool: an on-chain language plus a single-binary toolchain for Cardano validators. It compiles to the same UPLC as every other Cardano language, so it changes the developer experience rather than the on-chain semantics, and its output is compact with predictable costs. A validator is a pure predicate over a transaction, structured as one handler per Plutus V3 purpose, and compile-time parameters turn one source file into many independent on-chain instances such as one-shot minting policies. The build produces a CIP-57 blueprint that off-chain code consumes directly.

Two limits are worth restating. The compiler removes reentrancy, unbounded loops, and non-determinism by construction, but it cannot supply a check the author forgot, so an eUTXO security review remains a separate step. And the language is on-chain only by design; transaction construction stays in the off-chain library of your choice. The mindmap below summarizes the pieces covered here.

![Mindmap summarizing Aiken on Cardano: eUTXO model, language and UPLC target, toolchain, validator handlers, parameters, testing, and deployment artifact]({{site.url_complet}}/assets/article/blockchain/cardano/aiken-smart-contracts-cardano.png)

## Annex — Key Terms

| Term | Definition |
|------|------------|
| **Aiken** | a purpose-built, on-chain-only language and single-binary toolchain for writing Cardano validators, with syntax drawn from Rust, Elm, and Gleam. |
| **Validator** | a pure on-chain function that receives a proposed transaction and returns `True` (approve) or `False` (reject); it constrains transactions rather than performing actions. |
| **eUTXO (Extended UTXO)** | Cardano's ledger model, in which value is held in immutable unspent outputs and a contract is a validator guarding a UTXO, rather than an account with a mutable balance. |
| **UPLC (Untyped Plutus Lambda Calculus)** | the single on-chain bytecode every Cardano node executes; every source language compiles to it, so language choice is about ergonomics, not capability. |
| **Datum** | state data attached to a UTXO. In Plutus V3 a spend handler receives it as an `Option`, since an output at a script address need not carry a datum. |
| **Redeemer** | the typed argument the spender supplies when unlocking a script-controlled UTXO, used by the validator to select an action or provide a witness. |
| **Script context** | the view of the entire transaction (inputs, outputs, mint, signatories, validity range) that the ledger passes to the validator. |
| **Validator handler** | one entry point per script purpose. Under Plutus V3 the purposes are `spend`, `mint`, `withdraw`, `publish`, `vote`, and `propose`, plus an `else` fallback. |
| **CIP-57 blueprint (`plutus.json`)** | the machine-readable interface description Aiken emits on build, listing each validator, its datum/redeemer/parameter schemas, and the compiled code; off-chain code consumes it in place of the source. |
| **Execution units (ex-units)** | the CPU and memory budget a script consumes, bounded per transaction by the ledger; `aiken check` reports ex-units so tests double as cost measurements. |

## Frequently Asked Questions

**Q: Why is a Cardano smart contract described as a validator rather than a program that executes actions?**

Because in the eUTXO model the ledger, not the contract, moves value. A contract is a pure predicate that receives a fully-formed transaction and returns `True` or `False`. It cannot initiate a transfer, call another contract imperatively, or read outside state. Everything it can influence, it influences by rejecting transactions that fail its checks. This is what makes execution deterministic: the same transaction always produces the same verdict and the same cost, which can be computed off-chain before submission.

**Q: If every language compiles to UPLC, what does choosing Aiken actually change?**

Nothing about on-chain semantics, since UPLC and the ledger rules fix those. The choice affects developer ergonomics and the properties of the compiled output. Aiken was built only for writing validators, so it has a small learning curve, produces compact and efficient scripts, ships a built-in test runner, and generates a CIP-57 blueprint automatically. A language such as Plinth gives the full Haskell type system and shared on/off-chain types instead, at the cost of larger scripts and a steeper ramp. The tradeoff is tooling and output size, not capability.

**Q: What are the arguments a `spend` handler receives, and why is the datum wrapped in `Option`?**

A `spend` handler receives the datum attached to the UTXO being unlocked, the redeemer supplied by the spender, a reference to the specific input being validated (`OutputReference`), and the whole transaction as context. The datum is an `Option` because, under Plutus V3, an output at a script address is not required to carry a datum. The handler must therefore account for its absence, typically with `expect Some(...) = datum`, which rejects the spend when no valid datum is present instead of assuming one exists.

**Q: How does a one-shot minting policy guarantee that a token is minted only once?**

By parameterizing the validator on a specific UTXO reference and requiring, in the `Mint` branch, that this exact UTXO be spent in the same transaction. A UTXO can be consumed only once across the entire ledger, so once it is spent the minting condition can never be satisfied again. The `gift_card` example pairs this with checks that pin the exact asset name and a minted amount of `1`, so the policy authorizes precisely one token of one name and nothing else.

**Q: How do Aiken's tests relate to the execution cost a contract pays on-chain?**

The test runner evaluates each `test` against the same execution-budget model the ledger uses and reports the CPU and memory units consumed. A test is therefore also a cost measurement: a change that pushes a validator's units up shows immediately in `aiken check` output. This matters because Cardano bounds script execution units per transaction, so a validator that grows too expensive will fail on-chain even if it is logically correct. Property tests extend this by sampling many inputs and shrinking any failure to a minimal counterexample.

**Q: A validator passed all its unit tests. Why is a separate eUTXO security review still necessary?**

Unit tests confirm the checks a validator does perform behave as intended. They cannot reveal a check the author never wrote. Most eUTXO vulnerabilities are omissions: a minting policy that verifies quantity but forgets the asset name, a spend that trusts a UTXO's state without an authenticating token, or an output double-counted across two validators. These follow from the model rather than from Aiken, and the compiler cannot flag them. A review against the known eUTXO vulnerability classes checks for the constraints that should exist and do not, which testing of existing logic will not surface.

## References

### Aiken language and toolchain

- [Aiken language site and documentation](https://aiken-lang.org)
- [aiken-lang/aiken compiler repository](https://github.com/aiken-lang/aiken)
- [aiken-lang/stdlib API documentation](https://aiken-lang.github.io/stdlib)
- [Aiken installation instructions](https://aiken-lang.org/installation-instructions)
- [Aiken online playground](https://play.aiken-lang.org/)
- [Awesome Aiken](https://github.com/aiken-lang/awesome-aiken)

### Cardano model and standards

- [Cardano developer portal — smart contracts](https://developers.cardano.org/docs/smart-contracts/)
- [CIP-57 — Plutus Contract Blueprint](https://cips.cardano.org/cip/CIP-57)
- [CIP-30 — Cardano dApp-Wallet Web Bridge](https://cips.cardano.org/cip/CIP-30)
- [UPLC-CAPE — cross-compiler UPLC benchmarks](https://github.com/IntersectMBO/UPLC-CAPE)

### Tooling used

- [Claude Code](https://claude.com/product/claude-code)
