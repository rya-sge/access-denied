---
layout: post
title: "Medusa — Architecture and Practical Use of a Coverage-Guided Solidity Fuzzer"
date:   2026-07-28
last_modified_at: 2026-07-30
lang: en
locale: en-GB
categories: blockchain ethereum solidity security
tags: solidity fuzzing medusa invariant-testing property-testing trail-of-bits go-ethereum coverage-guided crytic
description: How Medusa fuzzes Solidity contracts. Architecture, the corpus and coverage feedback loop, assertion, property and optimization tests, and a step-by-step setup on a real project.
image: /assets/article/blockchain/solidity/medusa/2026-07-28-medusa-smart-contract-fuzzer.png
isMath: false
---

[Medusa](https://github.com/crytic/medusa) is a smart contract fuzzer written in Go by [Trail of Bits](https://www.trailofbits.com/). It executes randomised sequences of transactions against a project's contracts and reports the sequences that break a stated property. This article describes what the tool is trying to achieve, how it is built internally, and how to put it to work on a Solidity codebase.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why Smart Contract Fuzzing Uses a Different Model

Classical fuzzing, in the tradition of [AFL](https://lcamtuf.coredump.cx/afl/), feeds random bytes to a binary and watches for crashes. A segmentation fault is an unambiguous oracle: the program was not supposed to do that, and the fuzzer found an input that made it happen.

Smart contracts do not offer that oracle. A contract cannot segfault, and a reverted transaction is not a bug. Reverts are the normal way a contract rejects invalid input, so treating them as failures would flood any campaign with noise. The fuzzer therefore needs an oracle supplied by the developer rather than by the runtime.

That oracle is the **invariant**: a property of the system that must hold no matter what happens to it.

> **Definition.** An invariant is a property that remains unchanged after one or more operations are applied to the system.

Medusa's documentation groups invariants into two families, and the distinction shapes how a harness is written.

- **Function-level invariants** arise from a single function. For a `deposit()` that credits `balances[msg.sender]`, the caller's recorded balance must increase by exactly the deposited amount, and `totalDeposited` must move by the same quantity. These are pre-conditions and post-conditions of one call.
- **System-level invariants** hold across the whole execution regardless of call order. The constant-product relation of an automated market maker, the rule that no single account balance may exceed an ERC-20 total supply, or the rule that a contract's accounted deposits always equal its ether balance, all fall in this family.

The difference matters because a system-level invariant can only break after a particular *sequence* of calls. Testing `deposit` in isolation will never reveal a bug that needs a deposit, then a withdrawal, then a second deposit at a specific block timestamp. This is why Medusa is built around call sequences rather than individual calls.

## Architecture

Medusa is a Go program built on [medusa-geth](https://github.com/crytic/medusa-geth), a fork of [go-ethereum](https://github.com/ethereum/go-ethereum). Building on geth rather than a bespoke interpreter is a deliberate choice, recorded in the project's FAQ: it keeps EVM behaviour equivalent to the reference client, and Go makes the fuzzer usable as a library rather than only as a binary.

![Medusa component architecture]({{site.url_complet}}/assets/article/blockchain/solidity/medusa/medusa-architecture-concept.png)

### Module map

The repository divides into a small number of packages with clear responsibilities.

- **`cmd/`** is the [Cobra](https://github.com/spf13/cobra)-based CLI. It exposes `init`, `fuzz`, `corpus clean` and `completion`.
- **`compilation/`** abstracts the build step behind platform adapters. The default adapter shells out to [`crytic-compile`](https://github.com/crytic/crytic-compile), which understands Foundry, Hardhat and other frameworks; a direct `solc` adapter exists for single-file targets.
- **`chain/`** implements `TestChain`, the in-memory EVM harness. It owns block production, state management, the cheatcode contract, and the tracers.
- **`fuzzing/`** contains the campaign logic: the `Fuzzer` orchestrator, the worker pool, call sequence generation, value generation, the corpus, coverage maps, and the test case providers.
- **`events/`** provides the emitter used for lifecycle notifications, and `logging/` wraps [Zerolog](https://github.com/rs/zerolog).

### The test chain

Each worker owns a private `TestChain` instance. There is no shared EVM state between workers, which is what makes the parallelism sound: two workers exploring different sequences cannot contaminate each other's storage.

The chain is configured for testing rather than for consensus. By default `chainConfig.codeSizeCheckDisabled` is `true`, lifting the 24576-byte contract size limit of [EIP-170](https://eips.ethereum.org/EIPS/eip-170), and `skipAccountChecks` is `true`, disabling nonce validation and the requirement that a transaction origin be an externally owned account. Both defaults exist because a fuzzing harness is frequently a large contract calling itself from synthetic addresses, and enforcing mainnet rules would obstruct that.

The cheatcode contract is deployed at `0x7109709ECfa91a80626fF3989D68f67F5b1DD12D`, the same address Foundry uses, so a Foundry-style `vm.*` interface resolves without modification.

### Workers, resets, and memory

A campaign runs `fuzzing.workers` goroutines, ten by default. Each worker repeatedly generates a sequence, executes it, and rebases the chain to the state captured immediately after deployment.

Geth's state database accumulates data as blocks are produced, so a worker that ran indefinitely would grow without bound. Medusa handles this by destroying and recreating each worker after `fuzzing.workerResetLimit` sequences (50 by default). The trade-off is explicit in the documentation: a high limit means more memory per worker and a slower state database, while a low limit means paying the cost of replaying contract deployments more often.

### Events and hooks

Two extension surfaces make the Go API usable for custom testing methodologies.

`FuzzerEvents` emits `FuzzerStarting`, `FuzzerStopping`, `WorkerCreated` and `WorkerDestroyed`. The built-in test case providers subscribe to these to allocate and tear down their per-worker state.

`FuzzerHooks` exposes four replaceable functions: `NewCallSequenceGeneratorConfigFunc` for the generation strategy, `NewShrinkingValueMutatorFunc` for shrinking heuristics, `ChainSetupFunc` for deployment and initialisation, and a list of `CallSequenceTestFuncs` invoked after every call in a sequence. A new class of test is added by appending to that list, without touching the core loop. The API is documented as still under development and subject to breaking changes.

## The Fuzzing Lifecycle

![Medusa fuzzing lifecycle]({{site.url_complet}}/assets/article/blockchain/solidity/medusa/medusa-fuzzing-lifecycle-workflow.png)

### Deployment and the base state

At startup, Medusa compiles the project and deploys every contract named in `fuzzing.targetContracts`, in array order, from `fuzzing.deployerAddress` (`0x30000` by default). Contracts created during a target's constructor are deployed as a side effect. The resulting chain state is the **initial deployment state**, and every call sequence starts from it.

The array order is load-bearing. Constructor arguments can reference an earlier deployment through the `DeployedContract:<ContractName>` syntax in `fuzzing.constructorArgs`, and reordering the array changes the deployment addresses. The documentation flags this explicitly: changing the order, the deployer address, or the sender addresses can invalidate an entire stored corpus, because the addresses recorded in saved sequences no longer resolve.

### Call sequences

A call sequence is an array of transactions executed against the base state without resetting in between. Its maximum length is `fuzzing.callSequenceLength`, 100 by default. After the sequence completes, the chain rebases and the next sequence begins.

The length is the knob that selects between two testing modes:

- **Stateless fuzzing** uses a length of 1. State is discarded after every transaction. This suits arithmetic libraries and isolated pure functions, and it runs faster.
- **Stateful fuzzing** uses a longer sequence. State carries across calls, so the fuzzer can reach a `withdraw` path only after having produced a balance through `deposit` and `stake`. Nothing forces it to call those functions in that order; the coverage feedback loop is what makes it converge on orderings that reach new code.

### Generation: new versus mutated

For each sequence, the generator draws against `NewSequenceProbability`, which defaults to `0.3`. Roughly three times in ten it builds a fully random sequence. The rest of the time it starts from a corpus entry and applies one of four mutation strategies, chosen by weighted random selection. The defaults in `defaultCallSequenceGeneratorConfigFunc` are:

| Strategy | Unmodified weight | Mutated weight |
|---|---:|---:|
| Corpus head (take a prefix of a stored sequence, append new calls) | 800 | 80 |
| Corpus tail (take a suffix of a stored sequence, prepend new calls) | 100 | 10 |
| Splice at random (head of one stored sequence, tail of another) | 200 | 20 |
| Interleave at random (alternate calls from two stored sequences) | 100 | 10 |

The "unmodified" variants replay the corpus calls verbatim; the "mutated" variants attach a prefetch hook that pushes every ABI input value through the value mutator just before the call is executed. The ten-to-one ratio between the two columns means the fuzzer mostly reuses known-good calls and only occasionally perturbs their arguments, which preserves the state-building prefixes that made those sequences interesting in the first place.

### Coverage and the corpus

Medusa records **edge** coverage rather than instruction coverage. A `CoverageTracer` hooks the EVM, but it does not emit a marker on every instruction. Its opcode callback returns early unless the call frame has just been entered or the previous instruction was a `JUMP` or `JUMPI`, and a separate frame-exit callback records how the frame terminated. The four cases that produce a marker are therefore jumps, contract entrance, returns and reverts.

Each marker is a 64-bit value packing a source in the upper 32 bits and a destination in the lower 32 bits. For a jump, those are the program counters the jump left from and landed on. For a return or a revert, the source is the program counter of the terminating opcode and the destination is a reserved sentinel. For contract entrance, the source is a reserved sentinel and the destination is the first program counter executed in the frame. A `ContractCoverageMap` is a map from marker to hit count, held per code hash and per deployed address inside `CoverageMaps`.

The distinction is worth keeping in mind because the published documentation still describes the older model, a byte array indexed by bytecode position with one entry per executed opcode. Recording transitions rather than positions is what lets the fuzzer distinguish reaching a branch target from a new predecessor, which straight line-coverage would collapse.

When a call increases coverage, the prefix of the sequence up to and including that call is written to the corpus. The corpus is therefore not a log of everything tried, but a curated set of sequences each of which is known to have reached something new.

```
# Simplified execution loop, following the project documentation
sequence = generator.NewCallSequence()

for i < len(sequence) {
    tx = sequence[i]
    result = blockchain.executeTransaction(tx)

    if coverageTracker.updateCoverage() {
        corpus.addCallSequence(sequence[:i+1])
    }

    if tester.checkForInvariantFailures(result) {
        reportFailedTestCase()
    }
}
```

On disk, the corpus lives under `fuzzing.corpusDirectory`, with call sequences in `call_sequences/` and sequences associated with test results in `test_results/`, all as JSON. Leaving `corpusDirectory` empty (the default) means nothing is loaded at startup and nothing is persisted at exit, so every campaign restarts from zero knowledge. Setting it is the single change with the largest effect on repeat runs.

### Pruning

A corpus grows monotonically during a campaign, and entries become redundant as later sequences subsume their coverage. A `CorpusPruner` runs on a ticker every `fuzzing.pruneFrequency` minutes (5 by default, 0 to disable) on its own cloned chain, replays stored sequences, and drops those that no longer contribute coverage. Pruning only applies when `coverageEnabled` is true, and it keeps both memory use and startup replay time bounded over long campaigns.

### Value generation and Slither

Random 256-bit integers almost never satisfy an equality check against a magic constant. Medusa addresses this by seeding its value pool with constants harvested from the target: it runs [Slither](https://github.com/crytic/slither) over the project and extracts interesting literals, falling back to mining constants from each contract's AST if Slither is unavailable. Results are cached in `slither_results.json` so restarts do not pay the analysis cost again; the cache should be disabled while the code under test is still changing.

The mutational generator itself is configured with per-type biases and probabilities. Its defaults give a 0.5 bias toward generating a fresh random integer rather than mutating an existing one, a 0.1 probability of mutating any given integer, address, boolean or bytes argument, and array and string sizes drawn from 0 to 100. Mutation rounds per value range from 0 to 1.

## The Three Test Case Providers

Three providers run concurrently, each registering a `CallSequenceTestFunc` that executes after every call. They are recognised by function signature, and the rules are enforced in `fuzzing/utils/fuzz_method_utils.go`.

### Assertion tests

The assertion provider watches for EVM-level panics raised during any call the fuzzer makes. Which panic codes count as failures is governed by `testing.assertionTesting.panicCodeConfig`. By default only `failOnAssertion` is enabled, so a plain `assert(false)` fails the test and nothing else does.

Every other panic class is opt-in: `failOnArithmeticUnderflow`, `failOnDivideByZero`, `failOnOutOfBoundsArrayAccess`, `failOnPopEmptyArray`, `failOnEnumTypeConversionOutOfBounds`, `failOnIncorrectStorageAccess`, `failOnAllocateTooMuchMemory`, `failOnCallUninitializedVariable`, and the catch-all `failOnCompilerInsertedPanic`. Enabling arithmetic panics on a codebase that uses checked arithmetic as a deliberate guard will produce findings that are not bugs, which is why they default to off.

Any public method that is not a property or optimization test is treated as an assertion test target. Whether `view` and `pure` methods are called at all is controlled by `testing.testViewMethods`, which defaults to `true`.

### Property tests

A property test is a function whose name carries a configured prefix, defaulting to `property_`, that takes **no arguments** and returns a single `bool`. Returning `false` marks the test failed. The prefix list is configurable, and adding `echidna_` lets an existing [Echidna](https://github.com/crytic/echidna) suite be reused without renaming.

The fuzzer does not control a property test's inputs, because it has none. It controls the call sequence, and the property functions observe the resulting state after each transaction. They should be `view` or `pure`: their role is to read state and answer a question, not to change it.

```solidity
// The accounted total must always match the ether actually held
function property_total_deposited_eq_balance() public view returns (bool) {
    return depositContract.totalDeposited() == address(depositContract).balance;
}
```

### Optimization tests

An optimization test carries the `optimize_` prefix, takes no arguments, and returns an `int256`. Rather than passing or failing, the provider tracks the maximum value observed across the campaign and reports the sequence that produced it, then shrinks that sequence toward the minimal path to the same value. The starting point is the minimum representable `int256`.

This is the tool for quantifying a suspected weakness. Where a property test asks whether an accounting error can occur, an optimization test asks how large it can be made.

If a function carries one of these prefixes but has the wrong signature, Medusa does not silently ignore it. `BinTestByType` produces a warning naming the expected signature, which is worth reading in the startup output: a `property_` function that accidentally returns `uint256` would otherwise be quietly demoted to an ordinary assertion target and never checked as a property.

## Shrinking and Failure Reporting

A failing sequence of 100 calls with 256-bit arguments is not a usable bug report. When a provider detects a failure it returns a `ShrinkCallSequenceRequest` carrying a `VerifierFunction`, and the worker enters a shrinking loop bounded by `fuzzing.shrinkLimit` (5000 iterations by default).

![From a failing sequence to a minimal reproduction]({{site.url_complet}}/assets/article/blockchain/solidity/medusa/medusa-failure-shrinking-sequence.png)

The loop applies candidate reductions and keeps only those for which the verifier still reproduces the failure. The reductions include removing calls that reverted (using the execution results already attached to each element, so no replay is needed), removing one call at random, and mutating arguments toward smaller values through a dedicated shrinking mutator whose `ShrinkValueProbability` is 1.

Removing a call transfers its block-number and timestamp delays to the preceding call, so that the timing structure of the sequence survives the reduction. The source notes a known limitation here: reverted calls are dropped without preserving their delays, so a bug that depends on the exact block progression contributed by a reverted call may shrink imperfectly. The final call is always retained, since it is usually the one that triggered the failure.

The reported sequence names each call with its arguments, block number, timestamp, gas, value and sender:

```
[FAILED] Property Test: TestDepositContract.property_total_deposited_eq_balance()
Test for method "TestDepositContract.property_total_deposited_eq_balance()" failed after the following call sequence:
[Call Sequence]
1) TestDepositContract.deposit([55408297438917960862474451975836818265]) (block=1, time=2, gas=12500000, gasprice=1, value=0, sender=0x10000)
2) TestDepositContract.withdraw([19028842074912045090817234023499421958]) (block=3, time=5, gas=12500000, gasprice=1, value=0, sender=0x20000)
3) TestDepositContract.deposit([7702981288038713856009128004564213903]) (block=4, time=8, gas=12500000, gasprice=1, value=0, sender=0x10000)
```

An execution trace accompanies the sequence, at a detail level set by `testing.verbosity` or the `-v`, `-vv`, `-vvv` flags: top-level calls only, nested calls (the default), or a trace attached to every element of the sequence.

## Using Medusa on a Solidity Project

![Introducing a fuzzing campaign into a Solidity project]({{site.url_complet}}/assets/article/blockchain/solidity/medusa/medusa-project-setup-workflow.png)

### Installation

Six routes are documented. `go install github.com/crytic/medusa@latest` requires Go 1.20 or later; `brew install medusa` covers macOS and Linux; `nix build` produces `./result/bin/medusa`; `docker pull ghcr.io/crytic/medusa` avoids a local toolchain; precompiled binaries are attached to the [GitHub releases](https://github.com/crytic/medusa/releases); and a source build is `go build -trimpath` after cloning.

Whichever route is chosen, `crytic-compile` (and therefore a Python environment) is needed for the default compilation platform, and Slither is a recommended optional dependency for value generation.

### Initialising the project

```shell
cd my_project
medusa init
```

This writes `medusa.json` in the working directory. Invoked without a platform argument it configures `crytic-compile`; `medusa init solc` selects the direct compiler path instead. On a Foundry or Hardhat project, the compilation `target` should stay at its default of `.`, which tells `crytic-compile` to build the whole project including remappings and dependencies.

Three settings deserve attention before the first run:

- **`fuzzing.targetContracts`** is required. It names the contracts to deploy and fuzz, typically a single harness contract such as `["TestDepositContract"]`.
- **`fuzzing.testLimit`** caps the campaign at a number of calls. It defaults to `0`, meaning unbounded, which is rarely what you want while iterating. `10_000` or `100_000` gives a usable feedback cycle.
- **`fuzzing.corpusDirectory`** enables persistence. Setting it to `"corpus"` creates that directory beside `medusa.json` and also becomes the destination for coverage and revert reports.

### A function-level harness

A function-level test looks like a unit test whose fixed inputs have been replaced by parameters the fuzzer controls, plus explicit bounding so that the generated values land in a meaningful range.

```solidity
contract TestDepositContract {
    DepositContract depositContract;

    constructor() payable {
        depositContract = new DepositContract();
    }

    function testDeposit(uint256 _amount) public {
        // Bound the fuzzed value to what this contract can actually send
        uint256 amount = clampLte(_amount, address(this).balance);

        uint256 preBalance = depositContract.balances(address(this));

        depositContract.deposit{value: amount}();

        assert(depositContract.balances(address(this)) == preBalance + amount);
    }

    function clampLte(uint256 a, uint256 b) internal pure returns (uint256) {
        if (!(a <= b)) {
            return a % (b + 1);
        }
        return a;
    }
}
```

The clamping is not cosmetic. Without it, almost every generated `_amount` exceeds the contract's balance and the call reverts before reaching the assertion, so the campaign burns its budget on transactions that test nothing.

For this style of test, `fuzzing.callSequenceLength` is set to `1` so that the harness is restored to its full ether balance before each transaction, and `fuzzing.targetContractsBalances` gives the harness the ether it needs to deposit in the first place. That array maps one-to-one onto `targetContracts` and accepts base-10 strings, hexadecimal strings, or scientific notation such as `"1.2e18"`.

### A system-level harness

System-level testing needs three ingredients: wrapper functions that let the fuzzer drive the system with bounded inputs, `property_` functions that observe the result, and a call sequence long enough for interesting states to arise.

```solidity
contract TestDepositContract {
    DepositContract depositContract;

    constructor() payable {
        depositContract = new DepositContract();
    }

    receive() external payable {}

    // Wrappers: bounded entry points the fuzzer can call
    function deposit(uint256 _amount) public {
        uint256 maxAmount = address(this).balance;
        uint256 maxDepositAmount = depositContract.MAX_DEPOSIT_AMOUNT();
        uint256 totalDeposited = depositContract.totalDeposited();

        if (totalDeposited < maxDepositAmount) {
            uint256 remainingCapacity = maxDepositAmount - totalDeposited;
            if (remainingCapacity < maxAmount) {
                maxAmount = remainingCapacity;
            }
        } else {
            maxAmount = 0;
        }

        depositContract.deposit{value: clampLte(_amount, maxAmount)}();
    }

    function withdraw(uint256 _amount) public {
        uint256 amount = clampLte(_amount, depositContract.balances(address(this)));
        depositContract.withdraw(amount);
    }

    // Properties: one invariant each, checked after every transaction
    function property_total_deposited_lte_max() public view returns (bool) {
        return depositContract.totalDeposited() <= depositContract.MAX_DEPOSIT_AMOUNT();
    }

    function property_total_deposited_eq_balance() public view returns (bool) {
        return depositContract.totalDeposited() == address(depositContract).balance;
    }

    function property_user_balance_lte_total() public view returns (bool) {
        return depositContract.balances(address(this)) <= depositContract.totalDeposited();
    }

    function clampLte(uint256 a, uint256 b) internal pure returns (uint256) {
        if (!(a <= b)) {
            return a % (b + 1);
        }
        return a;
    }
}
```

Two design points hide in that listing. First, one invariant per property function: when a campaign fails, the function name identifies the broken rule with no further investigation. Second, the harness above routes every call through itself, so `msg.sender` inside `DepositContract` is always the harness address. If the system under test makes decisions based on caller identity, this collapses the multi-user dimension of the test; the fix is to configure `fuzzing.senderAddresses` and let the fuzzer call the system directly rather than through a single wrapper contract.

The comparison below summarises how the two styles differ.

|  | Function-level (assertion tests) | System-level (property tests) |
|---|---|---|
| Where the invariant lives | In the fuzzed function, via `assert()` | In standalone `property_` functions |
| What the fuzzer controls | The function arguments | The call sequence |
| When it is checked | During execution of the call | After every transaction |
| Typical `callSequenceLength` | `1` | `50` or more |

### Running a campaign

```shell
medusa fuzz --config medusa.json
```

Most configuration fields have a CLI equivalent for one-off runs: `--target-contracts`, `--test-limit`, `--seq-len`, `--workers`, `--timeout`, `--corpus-dir`, `--senders`, `--deployer`, `--fail-fast`, and `--use-slither`. The configuration file remains the recommended route, since flags are not recorded anywhere.

`--explore` changes what the run is for. It sets `stopOnFailedTest` and `stopOnNoTests` to `false` and disables all three testing modes, leaving pure coverage exploration. This is how you build a corpus for a codebase before any properties have been written.

By default `testing.stopOnFailedTest` is `true`, so the campaign halts at the first failure. Setting it to `false` collects every failing property in one run, which is usually preferable once a suite is established.

### Reading the reports

Two report families are produced at the end of a campaign, written to `<corpusDirectory>/coverage/` or to `crytic-export/coverage/` when no corpus directory is configured.

**Coverage reports** are controlled by `fuzzing.coverageFormats`, defaulting to `["lcov", "html"]`. Note that the reporting page of the documentation still shows this key as `coverageReports`, which the configuration parser does not recognise; the field declared in `fuzzing/config` is `coverageFormats`. The HTML report at `corpus/coverage/coverage_report.html` highlights executed source lines and is the fastest way to see whether the fuzzer is actually reaching the logic you care about. The LCOV output feeds standard tooling: `genhtml corpus/coverage/lcov.info --output-dir corpus --rc derive_function_end_line=0`, where the flag is required to stop `genhtml` from crashing on Solidity sources, or the [Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters) extension for in-editor annotation. `fuzzing.coverageExclusions` accepts glob patterns such as `["lib/**"]` to keep dependencies out of the numbers.

**Revert reports** are experimental and disabled by default (`fuzzing.revertReporterEnabled`). They record which functions revert most often and why, in both HTML and JSON. This is a harness debugging tool rather than a security finding: a wrapper that reverts on 99% of calls is a wrapper whose clamping is wrong, and the revert report is what makes that visible.

Read together, low coverage tells you the fuzzer is not reaching the code and the revert report tells you why.

### Maintaining the corpus

A stored corpus references contract addresses, method selectors and sender addresses. Refactoring the contracts or changing the ABI can leave entries that no longer replay. `medusa corpus clean` reads the project configuration, redeploys the targets, replays each stored sequence against a test chain, and deletes those that fail validation. It requires `fuzzing.corpusDirectory` to be set.

### Continuous integration

`medusa fuzz` returns distinct exit codes, defined in `cmd/exitcodes`: `0` on success, `1` for a general error, `6` for an error already logged, and `7` when a test case failed. A CI job can therefore distinguish a broken build from a genuine invariant violation.

```yaml
- name: Run Medusa
  run: medusa fuzz --config medusa.json --test-limit 100000
```

Committing the corpus directory to the repository lets each CI run start from the coverage the previous runs achieved, rather than rediscovering the same paths from scratch on every pull request.

## Advanced Capabilities

**Cheatcodes.** With `chainConfig.cheatCodesEnabled` (default `true`), the standard `vm.*` interface is available: `warp`, `roll`, `fee`, `prevrandao`, `chainId`, `coinbase` for block context; `store`, `load`, `etch`, `deal`, `getNonce`, `setNonce` for state manipulation; `prank`, `startPrank`, `stopPrank`, `prankHere` for caller identity; `snapshot` and `revertTo` for state checkpoints; `sign` and `addr` for key material; and a family of parsing and string conversion helpers. Medusa does not implement the whole Foundry cheatcode surface, so a ported harness may need adjustment. `ffi` is gated behind a separate `enableFFI` flag, disabled by default, because it permits arbitrary command execution on the host.

**Fork mode.** Setting `chainConfig.forkConfig.forkModeEnabled` with an `rpcUrl` and `rpcBlock`, or passing `--rpc-url` and `--rpc-block`, fetches state lazily from a live network. Block tags such as `LATEST` are not yet supported, so a numeric height is required. `poolSize` controls the RPC client pool and is recommended at two to three times the worker count, subject to whatever rate limit the provider imposes.

**Genesis state.** `chainConfig.genesisStateFile` loads a snapshot of EVM state (balances, nonces, bytecode and storage) captured elsewhere, so that deployment pipelines too complex to replicate in a constructor do not have to be. The typical route is a Foundry broadcast script against Anvil followed by `cast rpc anvil_dumpState > state.json`; the compressed Anvil dump, a decompressed wrapper JSON, and a plain account map are all detected automatically. Loaded accounts merge with Medusa's own fuzzer accounts, and the fuzzer accounts win on address conflicts.

Genesis state needs a companion setting. `genesisContractMappings` binds an address in the snapshot to a compiled contract name so that Medusa has an ABI for it. Without a mapping, the bytecode is present but no calls can be generated against it. The mapping controls ABI binding only: dependencies such as tokens and oracles belong there so that internal calls resolve, while only the contracts you actually want driven belong in `targetContracts` as well.

**Predeployed contracts.** `fuzzing.predeployedContracts` places named contracts at fixed addresses, which is useful when the system expects a canonical deployment. Constructor arguments are not supported for these.

**Console logging.** Medusa implements Foundry's and Hardhat's `console.sol`, so `console.log` output appears in execution traces. Format specifier support differs: `%v` is recommended and covers all supported types, `%s` does not accept `bool`, and `%i` and `%e` are unsupported.

## Configuration Choices That Matter

A short list of settings that determine whether a campaign produces anything useful.

- **`callSequenceLength`** selects stateless (`1`) or stateful (`50`+) testing. Getting this wrong is the most common reason a system-level property never fails despite a real bug.
- **`corpusDirectory`** turns each campaign into an increment on the last. Empty means every run starts blind.
- **`workers` with `workerResetLimit`** together determine throughput and memory. The defaults of 10 and 50 are a reasonable starting point on developer hardware.
- **`blockNumberDelayMax`** and **`blockTimestampDelayMax`** default to 60480 blocks and 604800 seconds. They let the fuzzer jump forward to reach time-gated code such as vesting cliffs and cooldowns, and they should be sized against the periods the system actually uses.
- **`senderAddresses`** defaults to `[0x10000, 0x20000, 0x30000]`. Any system where authorisation or per-user accounting matters needs these to be exercised rather than bypassed by a single-caller wrapper.
- **`targetFunctionSignatures`** and **`excludeFunctionSignatures`** narrow the campaign to specific ABI signatures. Property and optimization tests are always called regardless.
- **`panicCodeConfig`** should be tuned to the codebase. Enabling arithmetic panics is informative on unchecked-heavy code and noisy on code that relies on checked arithmetic reverting.

## Conclusion

Medusa applies coverage-guided fuzzing to a domain where the classical crash oracle does not exist, replacing it with invariants supplied by the developer. Its architecture follows from that substitution: a geth-based test chain per worker for EVM fidelity and isolation, a corpus of coverage-increasing call sequences that feeds a weighted mutation strategy, three test case providers that interpret failure differently, and a shrinking loop that turns a hundred-call sequence into a reproduction a developer can read.

The tool is only as good as the harness. Coverage reports and revert reports exist precisely because a harness that clamps too aggressively, or targets the wrong contract, will run to completion and report nothing. Trail of Bits positions Medusa as its exploratory fuzzer alongside the more mature Echidna, and the Go-level API remains explicitly subject to change, so projects adopting it should expect to track releases.

![Medusa mindmap]({{site.url_complet}}/assets/article/blockchain/solidity/medusa/2026-07-28-medusa-smart-contract-fuzzer.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Invariant** | A property of a contract system that must hold after any operation; it supplies the oracle that a smart contract fuzzer lacks by default. |
| **Call sequence** | An ordered array of transactions executed against the initial deployment state without an intervening reset, bounded by `callSequenceLength`. |
| **Corpus** | The persisted collection of call sequences that were observed to increase coverage, reused and mutated to seed later sequences. |
| **Coverage map** | A per-contract map from edge marker to hit count, where a marker packs a source and destination program counter for a jump, return, revert or contract entrance. |
| **Initial deployment state** | The chain state immediately after all target contracts are deployed, to which each worker rebases before starting a new sequence. |
| **Shrinking** | The bounded search that removes calls and reduces arguments while a verifier confirms the failure still reproduces, yielding a minimal repro. |
| **Assertion test** | A test that fails when an EVM panic selected in `panicCodeConfig` is raised; by default only `assert(false)` qualifies. |
| **Property test** | A prefixed function taking no arguments and returning `bool`, evaluated after every transaction to check a system-level invariant. |
| **Optimization test** | A prefixed function taking no arguments and returning `int256`, whose maximum observed value the fuzzer tries to raise rather than falsify. |
| **Stateful fuzzing** | Fuzzing that preserves EVM state across the calls of a sequence, so that later calls can reach code paths unlocked by earlier ones. |

### Security Implementation Checklist

A fuzzing harness fails silently. A campaign that never reaches the code under test, or whose properties can never return `false`, terminates cleanly and reports success. The checklist below covers the harness and configuration properties that separate a campaign providing genuine assurance from one providing only the appearance of it.

#### Harness reachability

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Coverage of the contracts under test is inspected in the HTML report after each campaign. | An unreached function is reported as passing, so absence of findings is mistaken for absence of bugs. |
| ☐ | The revert report is consulted when coverage is low, and wrappers reverting on most calls are corrected. | Over-tight clamping makes the fuzzer spend its whole budget on transactions that revert before reaching any assertion. |
| ☐ | Clamping bounds inputs to the valid range without excluding boundary values such as zero and the exact maximum. | Off-by-one and boundary bugs sit outside the range the fuzzer is ever allowed to generate. |
| ☐ | `targetContracts` names the harness, and the contracts under test are deployed and reachable from it. | Fuzzing the wrong contract produces a green campaign that exercised none of the target logic. |
| ☐ | Startup warnings about test functions with invalid signatures are read and resolved. | A `property_` function with the wrong return type is demoted to an ordinary call target and its invariant is never evaluated. |

#### Property design

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Each `property_` function checks exactly one invariant and is `view` or `pure`. | A property that mutates state can mask the violation it was meant to detect, and a compound property hides which rule broke. |
| ☐ | At least one property is verified to fail against a deliberately injected bug before the suite is trusted. | A property that cannot return `false` under any reachable state passes forever and asserts nothing. |
| ☐ | System-level invariants are tested with `callSequenceLength` well above 1. | Multi-transaction bugs are structurally unreachable when state is discarded after every call. |
| ☐ | `senderAddresses` is configured and used when authorisation or per-user accounting matters. | Routing every call through one wrapper collapses the multi-user dimension, hiding access control and cross-account bugs. |
| ☐ | `panicCodeConfig` is set deliberately for the codebase rather than left at defaults. | Arithmetic overflow, division by zero and out-of-bounds access go unreported when the corresponding flags stay off. |

#### Campaign integrity

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | `corpusDirectory` is set and the corpus is preserved between runs. | Each campaign restarts blind, so deep states reached previously must be rediscovered within the same budget. |
| ☐ | `medusa corpus clean` is run after ABI changes, contract reordering, or a change of deployer and sender addresses. | Stale corpus entries no longer replay, silently reducing the effective corpus to a fraction of its recorded size. |
| ☐ | `testLimit` or `timeout` is large enough that the campaign is not cut short before coverage plateaus. | A short campaign reports success purely because it stopped before reaching the interesting states. |
| ☐ | CI treats exit code `7` as a build failure, distinctly from `1` and `6`. | A genuine invariant violation is swallowed by a pipeline that only checks for a non-zero status it also gets from build errors. |
| ☐ | `enableFFI` remains `false` unless the harness genuinely needs it and the code under test is trusted. | The `ffi` cheatcode permits arbitrary command execution on the machine running the campaign. |
| ☐ | `stopOnFailedTest` is set to `false` for established suites so all violations surface in one run. | Halting at the first failure hides subsequent independent violations behind a single known one. |

## Frequently Asked Questions

**Q: Why can a smart contract fuzzer not simply look for crashes the way AFL does?**

Because the EVM has no equivalent of a crash. A contract cannot dereference a bad pointer or overflow a stack buffer in a way the runtime signals as an error, and the one abnormal-looking outcome that does exist, the revert, is the ordinary mechanism by which a contract rejects invalid input. Treating reverts as failures would report every `require` in the codebase. Medusa therefore relies on an oracle the developer supplies: assertions, `property_` functions, and enabled panic codes.

**Q: What determines whether a call sequence is written to the corpus?**

Coverage. A `CoverageTracer` attached to the EVM emits a marker whenever control flow branches, encoding the source and destination program counters of a jump, return, revert or contract entrance. If executing call *i* of a sequence produces a marker that was not previously recorded for that contract, the prefix `sequence[0..i]` is added to the corpus.

The corpus is thus a set of sequences each known to have reached something new, not a log of everything attempted. Sequences that add no coverage are discarded, and the `CorpusPruner` periodically re-evaluates stored entries and removes those that later sequences have made redundant.

**Q: What is the difference between an assertion test and a property test, and when would you use each?**

An assertion test is any fuzzer-callable method whose execution raises an enabled EVM panic; the invariant is written inline with `assert()` and the fuzzer controls the method's arguments. It is checked while that call executes, and it suits pre-condition and post-condition reasoning about one function.

A property test is a prefixed, argument-free function returning `bool` that is evaluated after *every* transaction in a sequence; the fuzzer controls the call sequence rather than the property's inputs.

Use assertions for function-level reasoning with a short sequence, and properties for global rules that must survive arbitrary orderings, with a long sequence. Both providers run concurrently, so a suite normally contains both.

**Q: A campaign completes without failures. What should be checked before concluding the contracts are sound?**

At minimum, three things:

- Open the HTML coverage report and confirm the fuzzer actually executed the logic of interest; a green campaign over unreached code proves nothing.
- Enable the revert report and check that the wrappers are not rejecting most generated inputs, which indicates clamping bounds that are too tight.
- Confirm that each property can in fact fail, by injecting a bug and observing the campaign catch it. Beyond that, check that `callSequenceLength` matches the kind of invariant being tested and that `testLimit` was large enough for coverage to plateau.

**Q: Why does the documentation warn that reordering `targetContracts` can invalidate an entire corpus?**

Contracts are deployed in array order from a fixed deployer address, and a contract's address is derived from the deployer address and its nonce. Reordering the array changes the nonce at which each contract is created, so every deployment address shifts. A stored corpus entry records concrete target addresses, so after a reorder those calls reference addresses where the intended contract no longer sits.

The same reasoning applies to changing `deployerAddress` or `senderAddresses`. This is what `medusa corpus clean` is for: it replays every stored sequence against a freshly deployed chain and deletes the ones that no longer validate.

**Q: How do coverage guidance and Slither constant mining work together?**

They attack the same problem from opposite ends. Coverage guidance is a feedback loop: it observes which sequences reached new bytecode and biases future generation toward mutating those sequences, with the weight table favouring corpus prefixes ten to one over argument mutation so that state-building work is preserved.

Slither constant mining is a priming step with no feedback: before fuzzing begins, it extracts literals from the target's source so that the value generator can propose them directly.

Coverage guidance alone would rarely satisfy an equality check against a magic constant, since the probability of generating a specific 256-bit value at random is negligible; supplying the constant lets the guard be passed once, after which coverage guidance takes over and retains the sequence that passed it.

If Slither is unavailable, Medusa falls back to mining constants from each contract's AST.

## References

### Project and documentation

- [Medusa on GitHub](https://github.com/crytic/medusa)
- [Medusa documentation summary](https://github.com/crytic/medusa/blob/master/docs/src/SUMMARY.md)
- [Medusa installation guide](https://github.com/crytic/medusa/blob/master/docs/src/getting_started/installation.md)
- [The fuzzing lifecycle](https://github.com/crytic/medusa/blob/master/docs/src/testing/fuzzing_lifecycle.md)
- [Types of invariants](https://github.com/crytic/medusa/blob/master/docs/src/testing/invariants.md)
- [Writing function-level invariants](https://github.com/crytic/medusa/blob/master/docs/src/testing/writing-function-level-invariants.md)
- [Writing system-level invariants](https://github.com/crytic/medusa/blob/master/docs/src/testing/writing-system-level-invariants.md)
- [Fuzzing configuration reference](https://github.com/crytic/medusa/blob/master/docs/src/project_configuration/fuzzing_config.md)
- [Testing configuration reference](https://github.com/crytic/medusa/blob/master/docs/src/project_configuration/testing_config.md)
- [Chain configuration reference](https://github.com/crytic/medusa/blob/master/docs/src/project_configuration/chain_config.md)
- [Cheatcodes overview](https://github.com/crytic/medusa/blob/master/docs/src/cheatcodes/cheatcodes_overview.md)
- [Medusa reports](https://github.com/crytic/medusa/blob/master/docs/src/testing/reporting.md)
- [Medusa FAQ](https://github.com/crytic/medusa/blob/master/docs/src/faq.md)

### Related tooling

- [Echidna](https://github.com/crytic/echidna)
- [Slither](https://github.com/crytic/slither)
- [crytic-compile](https://github.com/crytic/crytic-compile)
- [medusa-geth](https://github.com/crytic/medusa-geth)
- [go-ethereum](https://github.com/ethereum/go-ethereum)
- [Foundry Book](https://book.getfoundry.sh/)
- [Coverage Gutters for VS Code](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters)

### Background

- [AFL (american fuzzy lop)](https://lcamtuf.coredump.cx/afl/)
- [EIP-170 — Contract code size limit](https://eips.ethereum.org/EIPS/eip-170)
- [Trail of Bits](https://www.trailofbits.com/)
- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [Fuzzing Solana Programs with Trident]({{site.url_complet}}/2026/03/13/fuzzing-solana-programs-with-trident/)
