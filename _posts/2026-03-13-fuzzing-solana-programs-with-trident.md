---
layout: post
title: Fuzzing Solana Programs with Trident
date: 2026-03-13
lang: en
locale: en-GB
categories: solana security blockchain
tags: solana fuzzing trident anchor security testing smart-contract
description: Learn how to use Trident, the Rust-based fuzzing framework for Anchor programs on Solana. Covers fuzzing fundamentals, test structure, instruction construction, invariant checking, and execution.
image: /assets/article/blockchain/solana/solana-fuzzing-trident.png
isMath: false
---

Solana programs are complex stateful systems that handle real economic value. Traditional unit and integration tests verify known scenarios, but they cannot exhaustively explore the vast space of possible inputs and instruction sequences. Fuzzing fills this gap by automatically generating unexpected inputs to discover vulnerabilities, panics, and logic errors that manual testing misses. Trident is an open-source, manually guided fuzzing framework built specifically for Anchor-based Solana programs, offering a structured way to fuzz programs written in Rust.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and the [Trident](https://github.com/Ackee-Blockchain/trident) documentation.

[TOC]

---

## What is Fuzzing?

Fuzzing (or fuzz testing) is a software testing technique that feeds a program with large volumes of randomly generated, malformed, or unexpected data to uncover crashes, assertion failures, memory errors, and unexpected behaviors. Originally popularized in systems programming and binary exploitation, fuzzing has been adapted for smart contract security where the cost of a bug can be catastrophic.

In the context of Solana programs, fuzzing means:

- Generating random instruction data (amounts, flags, arbitrary byte arrays)
- Randomly selecting sequences of instructions to execute
- Comparing observed program state against expected invariants
- Detecting illegal state transitions, panics, or arithmetic overflows

The main challenge specific to Solana is that instructions are stateful and ordered. Calling `withdraw` before `initialize` will always fail — it is not meaningful. A completely random fuzzer would waste most of its cycles on invalid sequences. This is why **guided fuzzing** is essential.

---

## Trident: A Guided Fuzzing Framework for Solana

[Trident](https://github.com/Ackee-Blockchain/trident) is developed by Ackee Blockchain Security and is designed for Anchor-based Solana programs. Its key design principle is that the developer guides the fuzzer by:

1. Specifying **how to construct each instruction** (accounts and data)
2. Defining **flows** — named methods that represent groups of operations the fuzzer can randomly select and execute

This hybrid approach avoids the pitfall of pure black-box fuzzing while still generating randomized inputs and sequences within the developer-defined boundaries.

### Prerequisites and Installation

Before installing Trident, the following tools must be available:

- [Rust](https://www.rust-lang.org/tools/install) (stable, ≥ 1.86)
- [Solana CLI](https://solana.com/docs/intro/installation) (≥ 2.3)
- [Anchor](https://www.anchor-lang.com/docs/installation) (≥ 0.29.0)

Install the Trident CLI via Cargo:

```bash
cargo install trident-cli
```

For code coverage support, also install `cargo-llvm-cov`:

```bash
cargo +stable install cargo-llvm-cov --locked
```

---

## Project Structure

Initializing Trident inside an existing Anchor workspace creates a `trident-tests` directory:

```bash
# Initialize Trident in your Anchor workspace
trident init

# Add additional fuzz test targets later
trident fuzz add
```

The resulting file structure is:

```
project-root/
├── programs/
│   └── my_program/
├── trident-tests/
│   ├── .fuzz-artifacts/        # Metrics, dashboards, coverage reports
│   ├── fuzz_0/
│   │   ├── test_fuzz.rs        # Main fuzz test logic
│   │   ├── fuzz_accounts.rs    # Address storage definitions
│   │   └── types.rs            # Auto-generated IDL types
│   ├── fuzzing/                # Compilation outputs and crash artifacts
│   ├── Cargo.toml
│   └── Trident.toml            # Configuration manifest
└── ...
```

The `types.rs` file is automatically generated from the program IDL and contains all instruction structs, account structs, and data types needed to construct transactions programmatically.

---

## Anatomy of a Fuzz Test

The core of a Trident fuzz test lives in `test_fuzz.rs`. It consists of a struct annotated with `#[derive(FuzzTestMethods)]` and an implementation block annotated with `#[flow_executor]`.

```rust
use trident_fuzz::fuzzing::*;

#[derive(FuzzTestMethods)]
struct FuzzTest {
    /// Fuzzing engine: SVM client, random generation, account management
    trident: Trident,
    /// Reusable address storage for accounts used across flows
    fuzz_accounts: AccountAddresses,
}

#[flow_executor]
impl FuzzTest {
    fn new() -> Self {
        Self {
            trident: Trident::default(),
            fuzz_accounts: AccountAddresses::default(),
        }
    }

    #[init]
    fn start(&mut self) {
        // Runs once at the start of EACH iteration
        // Initialize program state: config, token mints, user accounts
    }

    #[flow]
    fn deposit_flow(&mut self) {
        // Randomly selected during each iteration
        // Construct and execute a deposit instruction
    }

    #[flow]
    fn withdraw_flow(&mut self) {
        // Another candidate flow, selected randomly
    }

    #[end]
    fn end(&mut self) {
        // Runs once at the END of each iteration
        // Perform final assertions or cleanup
    }
}

fn main() {
    FuzzTest::fuzz(1000, 100);
    // 1000 iterations, 100 flows executed per iteration
}
```

### Lifecycle per Iteration

Each iteration follows this deterministic lifecycle:

1. `#[init]` executes — sets up initial on-chain state
2. `#[flow]` methods are randomly selected and executed N times
3. `#[end]` executes — final assertions and cleanup

The randomness lies in which flow methods are selected and in what order. For example, with `deposit_flow` and `withdraw_flow`, a single iteration might execute: `deposit`, `deposit`, `withdraw`, `deposit`, `withdraw`, `withdraw`, ... until the configured number of flows is reached.

---

## Constructing Instructions

All instruction types are generated in `types.rs`. Trident uses a builder pattern to construct instructions:

```rust
use my_program::*;

#[flow]
fn deposit_flow(&mut self) {
    // 1. Obtain or create accounts from address storages
    let user = self.fuzz_accounts.user.insert(&mut self.trident, None);

    let vault = self.fuzz_accounts.vault.insert(
        &mut self.trident,
        Some(PdaSeeds {
            seeds: &[b"vault", user.as_ref()],
            program_id: my_program::program_id(),
        }),
    );

    // 2. Generate random instruction data
    let amount = self.trident.random_from_range(1..1_000_000u64);

    // 3. Build the instruction
    let ix = DepositInstruction::data(DepositInstructionData::new(amount))
        .accounts(DepositInstructionAccounts::new(user, vault))
        .instruction();

    // 4. Execute and handle the result
    let result = self.trident.process_transaction(&[ix], Some("deposit"));

    if result.is_success() {
        // Optionally read and check state
    }
}
```

### Address Storages

Address storages (`fuzz_accounts.*`) are containers that accumulate addresses across multiple flow invocations within a single iteration. They serve two purposes:

- Ensuring that the same accounts are reused realistically across flows (e.g., the same user deposits then withdraws)
- Allowing the fuzzer to sometimes pass incorrect or unexpected addresses (which is what makes it effective at finding authorization bugs)

| Method | Behavior |
|--------|----------|
| `.insert(&mut trident, None)` | Creates a random keypair, adds it to storage, returns its pubkey |
| `.insert(&mut trident, Some(PdaSeeds{...}))` | Derives a PDA from seeds, adds it to storage |
| `.get(&mut trident)` | Returns `Option<Pubkey>` — a random address already in storage, or `None` if empty |

The recommended pattern is to call `insert` in `#[init]` to populate storages, then call `get` in `#[flow]` methods to reuse the created accounts.

---

## Random Data Generation

The `Trident` struct exposes a full suite of random generation utilities:

```rust
// Numeric value in a range (u8, u16, u32, u64, i64, ...)
let amount = self.trident.random_from_range(0..u64::MAX);
let fee_bps = self.trident.random_from_range(0..10_000u16);

// Random public key
let recipient = self.trident.random_pubkey();

// Random keypair (for signers and authority accounts)
let authority = self.trident.random_keypair();

// Random string of given length
let label = self.trident.random_string(32);

// Fill a byte array with random data
let mut seed_data = [0u8; 32];
self.trident.random_bytes(&mut seed_data);

// Random boolean (50/50 probability)
let is_frozen = self.trident.random_bool();
```

These primitives allow constructing instruction data that covers edge cases: zero amounts, maximum values, empty strings, and arbitrary byte sequences.

---

## Account Management

Beyond address storages, Trident provides direct account manipulation capabilities via the embedded SVM client:

```rust
// Fund an account with lamports
self.trident.airdrop(&user_pubkey, 1_000_000_000);

// Read raw account data
let raw_account = self.trident.get_account(&pubkey);

// Read and deserialize typed account data (skip Anchor's 8-byte discriminator)
let state = self.trident
    .get_account_with_type::<VaultState>(&vault_pubkey, 8)
    .expect("vault account not found");

// Derive a PDA (canonical, with automatic bump search)
let (pda, bump) = self.trident.find_program_address(
    &[b"config", authority.as_ref()],
    &my_program::program_id(),
);

// Read sysvars
let clock = self.trident.get_sysvar::<Clock>();
println!("Current slot: {}", clock.slot);

// Get the default transaction fee payer
let payer = self.trident.payer();
```

---

## Handling Transaction Results

`process_transaction` returns a `TransactionResult` that should be inspected to distinguish between expected failures, unexpected failures, and successes:

```rust
let result = self.trident.process_transaction(&[ix], Some("withdraw"));

if result.is_success() {
    // Transaction committed — check invariants
} else if result.is_custom_error_with_code(6001_u32) {
    // InsufficientFunds — expected, skip
} else {
    // Unexpected failure — may indicate a bug
    panic!("Unexpected error:\n{}", result.logs());
}
```

The available inspection methods are:

| Method | Return type | Description |
|--------|-------------|-------------|
| `is_success()` | `bool` | Transaction committed without error |
| `is_error()` | `bool` | Transaction failed |
| `is_custom_error_with_code(u32)` | `bool` | Failed with specific program error code |
| `get_custom_error_code()` | `Option<u32>` | Extract the program error code if present |
| `logs()` | `String` | All program log messages as a single string |
| `get_transaction_timestamp()` | `u64` | Unix timestamp at execution time |

Systematically distinguishing expected from unexpected failures is critical: a fuzzer that panics on every transaction failure provides no signal; one that silently ignores all failures will miss real bugs.

---

## Writing Invariants

Invariants are the core mechanism for detecting logic errors. The standard pattern is to capture program state before and after a transaction, then assert that the state transition is correct:

```rust
#[flow]
fn swap_flow(&mut self) {
    let user = self.fuzz_accounts.user.get(&mut self.trident).expect("Storage empty");
    let pool = self.fuzz_accounts.pool.get(&mut self.trident).expect("Storage empty");
    let amount_in = self.trident.random_from_range(1..10_000u64);

    // Capture state before the transaction
    let pool_before = self.trident
        .get_account_with_type::<PoolState>(&pool, 8)
        .expect("pool not found");

    let ix = SwapInstruction::data(SwapInstructionData::new(amount_in))
        .accounts(SwapInstructionAccounts::new(user, pool))
        .instruction();

    let result = self.trident.process_transaction(&[ix], Some("swap"));

    if result.is_success() {
        // Capture state after the transaction
        let pool_after = self.trident
            .get_account_with_type::<PoolState>(&pool, 8)
            .expect("pool not found");

        // Assert the invariant
        self.swap_invariant(pool_before, pool_after, amount_in);
    }
}

fn swap_invariant(
    &mut self,
    before: PoolState,
    after: PoolState,
    amount_in: u64,
) {
    assert!(
        after.reserve_a + after.reserve_b >= before.reserve_a + before.reserve_b,
        "Total pool reserves must not decrease: {} < {}",
        after.reserve_a + after.reserve_b,
        before.reserve_a + before.reserve_b
    );
}
```

Good invariants for DeFi programs include:

- **Conservation of value**: total tokens in ≥ total tokens out
- **Monotonic counters**: sequence numbers, supply totals never decrease unexpectedly
- **Authorization**: only the expected authority can modify critical accounts
- **Numeric bounds**: balances, rates, and fees stay within valid ranges

---

## Multi-Instruction Transactions

Trident supports passing multiple instructions to a single `process_transaction` call, enabling atomic operation testing:

```rust
#[flow]
fn atomic_flow(&mut self) {
    let ix1 = create_approve_instruction(/* ... */);
    let ix2 = create_transfer_instruction(/* ... */);

    // Both instructions succeed or fail together
    let result = self.trident.process_transaction(
        &[ix1, ix2],
        Some("approve_and_transfer"),
    );

    assert!(result.is_success(), "Atomic flow failed: {}", result.logs());
}
```

This is particularly useful for testing flash-loan patterns, compound DeFi operations, and instruction sequences that must be atomic by protocol design.

---

## Regression Testing

Trident can serialize monitored account states to a JSON file and compare them across different program versions:

```rust
#[init]
fn start(&mut self) {
    let config = self.fuzz_accounts.config.insert(&mut self.trident, None);

    let ix = InitializeInstruction::data(InitializeInstructionData::default())
        .accounts(InitializeInstructionAccounts::new(config))
        .instruction();

    let result = self.trident.process_transaction(&[ix], Some("init"));

    if result.is_success() {
        // Track this account for regression comparison
        self.trident.add_to_regression(&config, "config_account");
    }
}
```

Enable in `Trident.toml`:

```toml
[fuzz.regression]
enabled = true
```

Then compare two regression snapshots after a code change:

```bash
trident compare regression_v1.json regression_v2.json
```

This detects unintended state changes introduced by program updates.

---

## Executing Fuzz Tests

Fuzz tests must be executed from the `trident-tests` directory:

```bash
cd trident-tests

# Basic execution with a random seed
trident fuzz run fuzz_0

# Reproducible run with a fixed seed
trident fuzz run fuzz_0 12345

# Verbose mode: print all transaction logs
TRIDENT_LOG=1 trident fuzz run fuzz_0
```

When the fuzzer discovers a failure, the seed that triggered it is printed. That seed can be reused to reproduce the exact sequence of operations deterministically, which is essential for debugging.

---

## Configuration: `Trident.toml`

The `Trident.toml` manifest controls all runtime options:

```toml
# Metrics and dashboard reporting
[fuzz.metrics]
enabled = true
dashboard = true
json = false

# Regression snapshot generation
[fuzz.regression]
enabled = false

# Code coverage (requires cargo-llvm-cov)
[fuzz.coverage]
enable = true
format = "json"
loopcount = 5          # Generate intermediate report every 5 flows
attach_extension = true # Real-time coverage in the Solana VS Code extension

# Load an external compiled program (e.g., Metaplex)
[[fuzz.programs]]
address = "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"
program = "metaplex-program/metaplex-token-metadata.so"

# Load a dumped mainnet account
[[fuzz.accounts]]
address = "6YG3J7PaxyMnnbU67ifyrgF3BzNzc7cD8hPkqK6ATweE"
filename = "tests/accounts/guardian_set.json"
```

Loading external programs and accounts is critical when the program under test interacts with deployed protocols like the SPL Token program, Metaplex, or any cross-program invocation (CPI) target that must behave realistically.

---

## Practical Example: Fuzzing a DeFi Protocol

Below is a complete skeleton for fuzzing a simplified lending protocol with three operations: initialize, deposit, and withdraw.

```rust
use trident_fuzz::fuzzing::*;
use lending_protocol::*;

#[derive(FuzzTestMethods)]
struct FuzzTest {
    trident: Trident,
    fuzz_accounts: AccountAddresses,
}

#[flow_executor]
impl FuzzTest {
    fn new() -> Self {
        Self {
            trident: Trident::default(),
            fuzz_accounts: AccountAddresses::default(),
        }
    }

    #[init]
    fn start(&mut self) {
        // Create the global config PDA
        let config = self.fuzz_accounts.config.insert(
            &mut self.trident,
            Some(PdaSeeds {
                seeds: &[b"config"],
                program_id: lending_protocol::program_id(),
            }),
        );

        // Create and fund a user account
        let user = self.fuzz_accounts.user.insert(&mut self.trident, None);
        self.trident.airdrop(&user, 10_000_000_000);

        // Initialize protocol
        let ix = InitializeInstruction::data(InitializeInstructionData::default())
            .accounts(InitializeInstructionAccounts::new(config, user))
            .instruction();

        let result = self.trident.process_transaction(&[ix], Some("initialize"));
        assert!(result.is_success(), "Initialization failed: {}", result.logs());
    }

    #[flow]
    fn deposit_flow(&mut self) {
        let user = self.fuzz_accounts.user.get(&mut self.trident).expect("Storage empty");
        let config = self.fuzz_accounts.config.get(&mut self.trident).expect("Storage empty");
        let amount = self.trident.random_from_range(1..1_000_000u64);

        // Read pool state before deposit
        let pool_before = self.trident
            .get_account_with_type::<PoolState>(&config, 8);

        let ix = DepositInstruction::data(DepositInstructionData::new(amount))
            .accounts(DepositInstructionAccounts::new(user, config))
            .instruction();

        let result = self.trident.process_transaction(&[ix], Some("deposit"));

        if result.is_success() {
            let pool_after = self.trident
                .get_account_with_type::<PoolState>(&config, 8)
                .expect("pool not found");

            if let Some(before) = pool_before {
                assert!(
                    pool_after.total_deposits >= before.total_deposits,
                    "Total deposits must not decrease after successful deposit"
                );
            }
        }
    }

    #[flow]
    fn withdraw_flow(&mut self) {
        let user = self.fuzz_accounts.user.get(&mut self.trident).expect("Storage empty");
        let config = self.fuzz_accounts.config.get(&mut self.trident).expect("Storage empty");
        let amount = self.trident.random_from_range(1..500_000u64);

        let ix = WithdrawInstruction::data(WithdrawInstructionData::new(amount))
            .accounts(WithdrawInstructionAccounts::new(user, config))
            .instruction();

        let result = self.trident.process_transaction(&[ix], Some("withdraw"));

        // Only InsufficientFunds (6001) is an acceptable failure
        if result.is_error() && !result.is_custom_error_with_code(6001) {
            panic!("Unexpected withdraw error:\n{}", result.logs());
        }
    }

    #[end]
    fn end(&mut self) {
        // Global invariant: pool should never have negative deposits
        if let Some(config) = self.fuzz_accounts.config.get(&mut self.trident) {
            if let Some(pool) = self.trident.get_account_with_type::<PoolState>(&config, 8) {
                assert!(
                    pool.total_deposits < i64::MAX as u64,
                    "Deposits overflow detected"
                );
            }
        }
    }
}

fn main() {
    FuzzTest::fuzz(2000, 50);
}
```

---

## Summary

![solana-fuzzing-trident]({{site.url_complet}}/assets/article/blockchain/solana/solana-fuzzing-trident.png)



```
@startmindmap
* Trident Fuzzing\nfor Solana
** Core Concepts
*** Guided fuzzing
*** Iteration lifecycle
*** Flow randomization
** Test Structure
*** #[init] setup
*** #[flow] operations
*** #[end] teardown
*** FuzzTest::fuzz(iter, flows)
** Instruction Construction
*** types.rs (auto-generated)
*** data() builder
*** accounts() builder
*** process_transaction()
** Address Storage
*** insert() random keypair
*** insert() PDA with seeds
*** get() reuse existing
** Random Generation
*** random_from_range()
*** random_pubkey()
*** random_keypair()
*** random_bool()
*** random_string()
** Invariants
*** Capture before/after state
*** get_account_with_type()
*** assert state transitions
*** handle expected errors
** Advanced Features
*** Multi-instruction transactions
*** Regression testing
*** Code coverage (llvm-cov)
*** External programs & accounts
** Execution
*** trident fuzz run
*** Seed reproducibility
*** TRIDENT_LOG=1
*** Trident.toml config
@endmindmap
```

---

## Reference

- [Trident GitHub Repository](https://github.com/Ackee-Blockchain/trident)
- [Trident Documentation](https://ackee.xyz/trident/docs/latest/)
- [Anchor Framework](https://www.anchor-lang.com/)
- [Solana Program Security](https://solana.com/developers/guides/advanced/security-intro)
- [Claude Code](https://claude.com/product/claude-code)
