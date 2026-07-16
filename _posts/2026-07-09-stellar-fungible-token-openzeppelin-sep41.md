---
layout: post
title: "Deploying a SEP-41 Fungible Token on Stellar with OpenZeppelin"
date:   2026-07-09
lang: en
locale: en-GB
categories: blockchain programmation
tags: stellar soroban smart-contracts openzeppelin sep-41 rust token
description: A technical walkthrough of the three ways to issue a fungible token on Stellar, the architecture of the OpenZeppelin stellar-tokens library, and a compile-verified SEP-41 contract from cargo new to a funded testnet deployment.
image: /assets/article/blockchain/stellar/stellar-openzeppelin-sep41.png
isMath: false
---

Issuing a fungible token on Stellar is not a single operation. Depending on whether the asset must trade on the classic order book, carry custom transfer rules, or both, the correct answer is a network primitive, a Soroban smart contract, or a combination of the two. This article maps that decision space, then walks through the [OpenZeppelin Stellar Contracts](https://github.com/OpenZeppelin/stellar-contracts) library (`stellar-tokens` v0.7.1, `soroban-sdk` 26.1.0) to build, test and deploy a SEP-41 token.

Every Rust snippet below was compiled against the library at commit `1e51389`, and the behavioural claims (supply cap enforcement, pause semantics, ownership) are backed by tests that were executed, not asserted.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## What SEP-41 actually specifies

[SEP-41](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0041.md) is the Stellar ecosystem proposal that defines the standard token interface for Soroban contracts. It is deliberately narrow. The interface consists of exactly ten functions:

| Function | Signature |
|---|---|
| `allowance` | `(env: Env, from: Address, spender: Address) -> i128` |
| `approve` | `(env: Env, from: Address, spender: Address, amount: i128, live_until_ledger: u32)` |
| `balance` | `(env: Env, id: Address) -> i128` |
| `transfer` | `(env: Env, from: Address, to: MuxedAddress, amount: i128)` |
| `transfer_from` | `(env: Env, spender: Address, from: Address, to: Address, amount: i128)` |
| `burn` | `(env: Env, from: Address, amount: i128)` |
| `burn_from` | `(env: Env, spender: Address, from: Address, amount: i128)` |
| `decimals` | `(env: Env) -> u32` |
| `name` | `(env: Env) -> String` |
| `symbol` | `(env: Env) -> String` |

Three properties of this interface deserve attention because they shape the implementation.

**Amounts are `i128`, not an unsigned type.** The standard uses a signed 128-bit integer. Negative amounts are therefore representable at the type level and must be rejected at runtime. The OpenZeppelin implementation raises `FungibleTokenError::LessThanZero` (error code 103) for `amount < 0`.

**Allowances expire.** `approve` takes a `live_until_ledger` argument: the ledger sequence number after which the allowance is void. An entry whose `live_until_ledger` is below the current ledger "should be treated as a 0 amount allowance". This has no counterpart in most token standards, and it is the reason allowances live in *temporary* storage (covered below). Passing a ledger in the past is rejected unless the amount is being reset to zero.

**`total_supply` and `mint` are not part of the standard.** The specification omits both to give contracts flexibility over supply mechanics. OpenZeppelin nevertheless provides `total_supply()` on its `FungibleToken` trait because it is near-universally expected, and exposes `Base::mint` as a helper rather than a trait method, since the correct signature depends on the authorization model. Conversely, `burn` *is* mandatory: a contract that does not implement `FungibleBurnable` is not SEP-41 compliant.

## Three ways to ship a fungible token on Stellar

The most consequential decision happens before any Rust is written.

![Decision tree for choosing a fungible-token path on Stellar]({{site.url_complet}}/assets/article/blockchain/stellar/sep41-path-decision.png)

### Path 1: a classic asset and its Stellar Asset Contract

Stellar has issued fungible assets since long before Soroban existed. A classic asset is a `CODE:ISSUER` pair, held in trustlines, tradable on the built-in decentralized exchange, usable in path payments, and supported by every anchor and wallet in the ecosystem. No contract code is involved.

To make such an asset callable from Soroban, the network exposes a [Stellar Asset Contract](https://developers.stellar.org/docs/tokens/stellar-asset-contract) (SAC): a built-in contract, not user-deployed Wasm, that implements the SEP-41 interface over the classic asset. Its address is deterministic, derived as the SHA-256 hash of a `HashIDPreimage::ENVELOPE_TYPE_CONTRACT_ID_FROM_ASSET` preimage, so every classic asset has a reserved contract address whether or not it has been instantiated.

```bash
# Instantiate the SAC for an existing classic asset
stellar contract asset deploy \
  --source-account alice \
  --network testnet \
  --asset USDC:GCYEIQEWOCTTSA72VPZ6LYIZIK4W4KNGJR72UADIXUXG45VDFRVCQTYE

# Its contract id is deterministic and can be computed without deploying
stellar contract id asset \
  --network testnet \
  --asset USDC:GCYEIQEWOCTTSA72VPZ6LYIZIK4W4KNGJR72UADIXUXG45VDFRVCQTYE
```

Beyond the SEP-41 functions, a SAC exposes four privileged operations restricted to the asset admin (initially the issuer G-account): `mint`, `clawback`, `set_admin` and `set_authorized`.

The cost of this path is rigidity. The SAC's semantics are fixed by the protocol. It must honour classic trustline flags such as `AUTHORIZED_FLAG` and `TRUSTLINE_CLAWBACK_ENABLED_FLAG`; transfers to or from the issuer account are implicitly burns and mints; classic account balances remain capped at a signed 64-bit integer while contract balances use 128 bits. You cannot add a supply cap, a transfer hook, or a pause switch.

### Path 2: a custom Soroban token

Writing a Soroban contract that implements SEP-41 gives complete control over the logic: capped supply, allowlists, pausing, voting checkpoints, vault share accounting. This is where `stellar-tokens` applies. The trade-off is the mirror image of path 1: a custom token is not a classic asset, so it does not appear on the classic DEX, cannot be used in path payments, and is not automatically understood by anchors.

### Path 3: a classic asset with an OpenZeppelin SAC admin

The two paths are not mutually exclusive. `set_admin` lets the asset issuer transfer SAC administrative control to an arbitrary contract address. That contract then becomes the only entity able to call `mint`, `clawback` and `set_authorized`, and it can wrap those calls in any authorization logic it likes: role-based access control, rate limits, two-step handovers, timelocks.

The library ships two flavours of this, and the choice between them is a genuine design decision:

- **`sac_admin_wrapper`** defines an explicit entry point per admin function and forwards to the SAC after running custom checks. Modular and easy to reason about, at the cost of splitting the user-facing interface (on the SAC) from the admin interface (on the wrapper).
- **`sac_admin_generic`** implements `__check_auth` so the admin contract itself acts as a custom account. Authorization logic is injected while both interfaces stay unified.

Here is the wrapper approach as it appears in the repository's `examples/sac-admin-wrapper`:

```rust
use soroban_sdk::{contract, contractimpl, symbol_short, Address, Env};
use stellar_access::access_control::{self as access_control, AccessControl};
use stellar_macros::{only_admin, only_role};
use stellar_tokens::fungible::{self as fungible, sac_admin_wrapper::SACAdminWrapper};

#[contract]
pub struct ExampleContract;

#[contractimpl]
impl ExampleContract {
    pub fn __constructor(e: &Env, default_admin: Address, manager: Address, sac: Address) {
        access_control::set_admin(e, &default_admin);
        access_control::grant_role_no_auth(e, &manager, &symbol_short!("manager"), &default_admin);
        fungible::sac_admin_wrapper::set_sac_address(e, &sac);
    }
}

#[contractimpl]
impl SACAdminWrapper for ExampleContract {
    #[only_admin]
    fn set_admin(e: Env, new_admin: Address, _operator: Address) {
        fungible::sac_admin_wrapper::set_admin(&e, &new_admin);
    }

    #[only_role(operator, "manager")]
    fn mint(e: Env, to: Address, amount: i128, operator: Address) {
        fungible::sac_admin_wrapper::mint(&e, &to, amount);
    }

    #[only_role(operator, "manager")]
    fn clawback(e: Env, from: Address, amount: i128, operator: Address) {
        fungible::sac_admin_wrapper::clawback(&e, &from, amount);
    }

    #[only_role(operator, "manager")]
    fn set_authorized(e: Env, id: Address, authorize: bool, operator: Address) {
        fungible::sac_admin_wrapper::set_authorized(&e, &id, authorize);
    }
}

#[contractimpl(contracttrait)]
impl AccessControl for ExampleContract {}
```

### Comparison

| | Classic asset + SAC | Custom Soroban token | Classic asset + OZ SAC admin |
|---|---|---|---|
| Rust code required | none | full contract | admin contract only |
| Classic DEX, path payments, anchors | yes | no | yes |
| Custom transfer logic | no | yes | no (transfers stay on the SAC) |
| Custom admin logic | no | yes | yes |
| Supply cap, pause, allowlist | no | yes | mint-side only |
| Balance width | 64-bit classic / 128-bit contract | 128-bit | 64-bit classic / 128-bit contract |
| Clawback | if enabled on the asset | if implemented | if enabled on the asset |
| Upgradeable logic | no | yes | yes |

The remainder of this article follows path 2.

## Architecture of the OpenZeppelin fungible module

The library is published as a set of crates rather than a monolith. A typical token pulls in four of them: `stellar-tokens` (the token logic), `stellar-access` (ownership and roles), `stellar-contract-utils` (pausable, upgradeable) and `stellar-macros` (the attribute macros that glue the previous three together).

### The trait, the associated type, and the override hook

The central abstraction is a trait with an associated type:

```rust
#[contracttrait]
pub trait FungibleToken {
    type ContractType: ContractOverrides;

    fn transfer(e: &Env, from: Address, to: MuxedAddress, amount: i128) {
        Self::ContractType::transfer(e, &from, &to, amount);
    }

    fn balance(e: &Env, account: Address) -> i128 {
        Self::ContractType::balance(e, &account)
    }
    // ... the remaining SEP-41 methods, each delegating identically
}
```

Every method body forwards to `Self::ContractType::<method>`. `ContractType` is one of a small set of marker types shipped by the library: `Base`, `AllowList`, `BlockList`, `RWA`, `Vault`. Each implements the internal `ContractOverrides` trait, whose default implementation simply calls `Base`. An extension that needs to change transfer semantics overrides only the methods it cares about.

![How a call is routed through the ContractType associated type]({{site.url_complet}}/assets/article/blockchain/stellar/sep41-trait-dispatch.png)

The payoff is that incompatible extensions become a type error rather than a runtime surprise. `FungibleAllowList` is declared as:

```rust
pub trait FungibleAllowList: FungibleToken<ContractType = AllowList> { ... }
```

and `FungibleBlockList` as:

```rust
pub trait FungibleBlockList: FungibleToken<ContractType = BlockList> { ... }
```

Since a contract has exactly one `FungibleToken` implementation and therefore exactly one `ContractType`, implementing both traits cannot type-check. An allowlist token and a blocklist token are structurally different contracts, and the compiler enforces it.

As a contract author you never name `ContractOverrides`. You pick a `ContractType`, leave the method bodies empty, and `#[contractimpl(contracttrait)]` fills them in.

### High-level and low-level functions

The module exposes two layers. High-level functions perform authorization, mutate state and emit events. Low-level `_no_auth` siblings do neither, take a `caller: &Address` purely so the event carries the right actor, and leave verification to you. Mixing the two halves (calling a `_no_auth` function and then separately requiring auth) is how subtle authorization bugs get written, so the library documents each function that intentionally skips a check with a `# Security Warning` block. `Base::mint` is one of them: it has no authorization at all, by design, because only the contract knows who is allowed to mint.

## A minimal SEP-41 token

The smallest compliant contract implements `FungibleToken` and `FungibleBurnable`, and sets metadata in the constructor.

```rust
use soroban_sdk::{contract, contractimpl, Address, Env, MuxedAddress, String};
use stellar_tokens::fungible::{burnable::FungibleBurnable, Base, FungibleToken};

#[contract]
pub struct MinimalToken;

#[contractimpl]
impl MinimalToken {
    pub fn __constructor(
        e: &Env,
        owner: Address,
        name: String,
        symbol: String,
        initial_supply: i128,
    ) {
        Base::set_metadata(e, 7, name, symbol);
        Base::mint(e, &owner, initial_supply);
    }
}

#[contractimpl(contracttrait)]
impl FungibleToken for MinimalToken {
    type ContractType = Base;
}

#[contractimpl(contracttrait)]
impl FungibleBurnable for MinimalToken {}
```

Two details are worth pausing on.

`MuxedAddress` is imported but never written anywhere in the visible source. Removing it does not produce an unused-import warning; it produces a hard compile error:

```text
error[E0425]: cannot find type `MuxedAddress` in this scope
  --> src/minimal.rs:15:1
   |
15 | #[contractimpl(contracttrait)]
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ not found in this scope
   |
   = note: this error originates in the macro
           `soroban_sdk::contractimpl_trait_default_fns_not_overridden`
```

The macro expands the default body of `transfer`, whose signature names `MuxedAddress`, into your module. The type must therefore be nameable at the expansion site even though your code never mentions it. This is a recurring papercut with `#[contractimpl(contracttrait)]` and it is worth knowing before spending time on it.

The second detail is `7` in `set_metadata`. Classic Stellar assets use seven decimals throughout, and matching that convention keeps a custom token consistent with the rest of the ecosystem. Several examples in the repository use `18`, an Ethereum convention that carries no meaning on Stellar.

The `#[contractimpl]` versus `#[contractimpl(contracttrait)]` distinction matters: the bare form goes on the contract's inherent `impl` block (the one holding `__constructor`), and the `(contracttrait)` form goes on `impl <Trait> for Contract` blocks so the macro can supply the default method bodies. Swapping them is a common mistake.

## Adding ownership, pausing and a supply cap

A production token usually needs an owner who can mint, an emergency stop, and a hard supply ceiling. Each is a separate module, and they compose.

```rust
use soroban_sdk::{contract, contractimpl, Address, Env, MuxedAddress, String};
use stellar_access::ownable::{self as ownable, Ownable};
use stellar_contract_utils::pausable::{self as pausable, Pausable};
use stellar_macros::{only_owner, when_not_paused};
use stellar_tokens::fungible::{
    burnable::FungibleBurnable,
    capped::{check_cap, set_cap},
    Base, FungibleToken,
};

#[contract]
pub struct MyToken;

#[contractimpl]
impl MyToken {
    pub fn __constructor(e: &Env, owner: Address, name: String, symbol: String, cap: i128) {
        Base::set_metadata(e, 7, name, symbol);
        set_cap(e, cap);
        ownable::set_owner(e, &owner);
    }

    #[only_owner]
    #[when_not_paused]
    pub fn mint(e: &Env, to: Address, amount: i128) {
        check_cap(e, amount, Base::total_supply(e));
        Base::mint(e, &to, amount);
    }
}

#[contractimpl(contracttrait)]
impl FungibleToken for MyToken {
    type ContractType = Base;

    #[when_not_paused]
    fn transfer(e: &Env, from: Address, to: MuxedAddress, amount: i128) {
        Self::ContractType::transfer(e, &from, &to, amount);
    }

    #[when_not_paused]
    fn transfer_from(e: &Env, spender: Address, from: Address, to: Address, amount: i128) {
        Self::ContractType::transfer_from(e, &spender, &from, &to, amount);
    }
}

#[contractimpl(contracttrait)]
impl FungibleBurnable for MyToken {}

#[contractimpl(contracttrait)]
impl Ownable for MyToken {}

#[contractimpl(contracttrait)]
impl Pausable for MyToken {
    #[only_owner]
    fn pause(e: &Env, _caller: Address) {
        pausable::pause(e);
    }

    #[only_owner]
    fn unpause(e: &Env, _caller: Address) {
        pausable::unpause(e);
    }
}
```

Several things are going on here.

**Partial overrides.** `impl FungibleToken` overrides only `transfer` and `transfer_from` in order to attach `#[when_not_paused]`. The other seven methods are left to the macro. `impl Ownable` and `impl FungibleBurnable` override nothing at all.

**`Pausable` has no default bodies for `pause` and `unpause`.** Unlike `FungibleToken`, the `Pausable` trait declares them without an implementation, precisely because the library refuses to guess who is allowed to pause. You must supply both, and you must add the authorization yourself. The `_caller` parameter is part of the SEP-agnostic trait signature; once `#[only_owner]` is applied it is unused, hence the underscore. This mirrors the pattern used by the RWA token example in the repository.

**`#[only_owner]` injects `require_auth`.** It expands to a lookup of the stored owner followed by `owner.require_auth()`. This is why the library also ships `#[has_role]` and `#[has_any_role]` next to `#[only_role]` and `#[only_any_role]`: Soroban panics if `require_auth()` is called twice on the same address in one invocation, so the `has_*` variants perform the check without injecting the auth call, for use when the delegated `Base::` helper already requires it. Getting this wrong is not a silent bug, but it is an easy one to write.

**`check_cap` precedes the mint.** The capped extension does not expose a trait. It gives you three free functions (`set_cap`, `query_cap`, `check_cap`) and expects `check_cap(e, amount, Base::total_supply(e))` to run before `Base::mint`. Note that `set_cap` deliberately does not require the cap to be greater than the current total supply, which lets an operator freeze minting by setting a cap below the circulating amount.

### Verifying the behaviour

The claims above are testable. Test files in this codebase begin with `extern crate std;`, register the contract, and drive it through the generated client.

```rust
extern crate std;

use soroban_sdk::{testutils::Address as _, Address, Env, String};
use stellar_contract_utils::pausable::PausableClient;

use crate::contract::{MyToken, MyTokenClient};

fn setup<'a>() -> (Env, Address, MyTokenClient<'a>) {
    let e = Env::default();
    e.mock_all_auths();
    let owner = Address::generate(&e);
    let addr = e.register(
        MyToken,
        (
            owner.clone(),
            String::from_str(&e, "My Token"),
            String::from_str(&e, "MTK"),
            1_000_i128,
        ),
    );
    let client = MyTokenClient::new(&e, &addr);
    (e, owner, client)
}

#[test]
#[should_panic(expected = "Error(Contract, #106)")]
fn mint_beyond_cap_panics() {
    let (e, _owner, client) = setup();
    let to = Address::generate(&e);
    client.mint(&to, &1_001);
}

#[test]
#[should_panic(expected = "Error(Contract, #1000)")]
fn transfer_blocked_when_paused() {
    let (e, owner, client) = setup();
    let to = Address::generate(&e);
    client.mint(&owner, &100);

    let pausable = PausableClient::new(&e, &client.address);
    pausable.pause(&owner);
    assert!(pausable.paused());

    client.transfer(&owner, &to, &10);
}
```

Error `106` is `FungibleTokenError::ExceededCap`; `1000` is `PausableError::EnforcedPause`. Panic assertions use the numeric form because contract errors cross the host boundary as codes, not names. Each package occupies its own numeric range (fungible in the 100s, pausable in the 1000s, access-control in the 2000s, ownable in the 2100s), so a code alone identifies the module that rejected the call.

One trap in the client API: `transfer` accepts `impl Into<MuxedAddress>`, so `client.transfer(&owner, &to, &10)` compiles while `client.transfer(&owner, &to.into(), &10)` does not, because the target type of `.into()` is ambiguous.

Running the suite:

```text
$ cargo test --package my-token
running 4 tests
test test::burn_reduces_total_supply ... ok
test test::metadata_and_mint_within_cap ... ok
test test::mint_beyond_cap_panics ... ok
test test::transfer_blocked_when_paused ... ok

test result: ok. 4 passed; 0 failed
```

## Building and deploying

### The manifest

```toml
[package]
name = "my-token"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]
doctest = false

[dependencies]
soroban-sdk = "26.1.0"
# Pin exactly: the library is in active development and iterates quickly.
stellar-tokens = "=0.7.1"
stellar-access = "=0.7.1"
stellar-contract-utils = "=0.7.1"
stellar-macros = "=0.7.1"

[dev-dependencies]
soroban-sdk = { version = "26.1.0", features = ["testutils"] }

[profile.release]
opt-level = "z"
overflow-checks = true
strip = "symbols"
panic = "abort"
codegen-units = 1
lto = true
```

Examples use `crate-type = ["cdylib"]`; library crates that are also consumed as Rust dependencies use `["lib", "cdylib"]`. `overflow-checks = true` in the release profile is not optional for a token: arithmetic that silently wraps in release mode is a supply bug.

### Build with the Stellar CLI, not with cargo

The documented incantation `cargo build --target wasm32v1-none --release` fails against the OpenZeppelin workspace, because it enables the `experimental_spec_shaking_v2` feature on `soroban-sdk`:

```text
error: soroban-sdk feature 'experimental_spec_shaking_v2' requires stellar-cli v25.2.0+

The soroban-sdk 'experimental_spec_shaking_v2' feature requires building
with `stellar contract build` from stellar-cli v25.2.0 or newer.

To fix, either:
  - Build with `stellar contract build` using stellar-cli v25.2.0+
  - Disable the feature by removing 'experimental_spec_shaking_v2' from
    the soroban-sdk import features list in Cargo.toml.
```

Spec shaking prunes unused type definitions from the contract's exported interface, shrinking the Wasm. The build script detects whether the invoking build system supports it and refuses to proceed otherwise. Use `stellar contract build`.

### The lifecycle

![Sequence diagram of building, deploying and invoking a SEP-41 token]({{site.url_complet}}/assets/article/blockchain/stellar/sep41-deploy-sequence.png)

```bash
# 1. An identity, funded by Friendbot on testnet
stellar keys generate alice --network testnet --fund

# 2. Compile to Wasm
stellar contract build
# -> target/wasm32v1-none/release/my_token.wasm

# 3. Deploy. Everything after `--` is passed to __constructor.
stellar contract deploy \
  --wasm target/wasm32v1-none/release/my_token.wasm \
  --source-account alice \
  --network testnet \
  --alias my_token \
  -- \
  --owner "$(stellar keys address alice)" \
  --name "My Token" \
  --symbol MTK \
  --cap 1000000
# -> CACDYF3CYMJEJTIVFESQYZTN67GO2R5D5IUABTCUG3HXQSRXCSOROBAN
```

Constructor arguments are named after the `__constructor` parameters, which is why the parameter names in your Rust source become part of your deployment interface. Renaming `owner` to `admin` is a breaking change to the deploy command.

Invoking follows the same shape, with the function name after the separator:

```bash
CID=CACDYF3CYMJEJTIVFESQYZTN67GO2R5D5IUABTCUG3HXQSRXCSOROBAN

stellar contract invoke --id $CID --source-account alice --network testnet \
  -- mint --to "$(stellar keys address bob)" --amount 1000

stellar contract invoke --id $CID --source-account bob --network testnet \
  -- transfer --from "$(stellar keys address bob)" \
               --to "$(stellar keys address alice)" --amount 250

stellar contract invoke --id $CID --source-account alice --network testnet \
  -- balance --account "$(stellar keys address alice)"
```

Read-only calls such as `balance` are simulated and cost nothing, but the CLI still requires a source account to build the transaction envelope.

## Storage tiers, TTL and state archival

Soroban does not have permanent world state. Every entry carries a Time-To-Live, and an entry whose TTL reaches zero is archived. Developers arriving from EVM-based chains tend to trip over this, and a token contract touches all three storage tiers.

![Storage tiers and the persistent entry lifecycle]({{site.url_complet}}/assets/article/blockchain/stellar/sep41-storage-ttl.png)

| Tier | What the fungible module stores there | Lifetime |
|---|---|---|
| `instance` | `Meta { decimals, name, symbol }`, `TotalSupply`, `Cap` | shares the contract instance's TTL |
| `persistent` | `Balance(Address)` | archived when TTL expires, restorable |
| `temporary` | `Allowance(AllowanceKey { owner, spender })` | deleted when TTL expires, never restorable |

Allowances sit in temporary storage because SEP-41 already gives them an expiry (`live_until_ledger`). The storage tier and the standard agree: an expired allowance is gone, and there is nothing to restore.

### Who extends what

The library follows a rule that is easy to state and easy to get wrong: **library-owned `persistent` and `temporary` reads extend TTL; writes do not.** Reading a balance bumps its TTL; writing a balance does not. The canonical shape appears throughout `storage.rs`:

```rust
if let Some(value) = e.storage().persistent().get::<_, i128>(&key) {
    e.storage().persistent().extend_ttl(&key, BALANCE_TTL_THRESHOLD, BALANCE_EXTEND_AMOUNT);
    value
} else {
    0
}
```

The argument order is always `(&key, TTL_THRESHOLD, EXTEND_AMOUNT)`: extend only if the remaining TTL has fallen below the threshold, and when extending, extend to the amount. The constants come in a fixed trio:

```rust
const DAY_IN_LEDGERS: u32 = 17280;
pub const BALANCE_EXTEND_AMOUNT: u32 = 30 * DAY_IN_LEDGERS;
pub const BALANCE_TTL_THRESHOLD: u32 = BALANCE_EXTEND_AMOUNT - DAY_IN_LEDGERS;
pub const INSTANCE_EXTEND_AMOUNT: u32 = 7 * DAY_IN_LEDGERS;
pub const INSTANCE_TTL_THRESHOLD: u32 = INSTANCE_EXTEND_AMOUNT - DAY_IN_LEDGERS;
```

One consequence follows directly: because writes do not extend TTL, a balance that only ever *receives* transfers and is never read drifts toward archival. In practice `Base::transfer` reads both balances, so ordinary activity keeps them alive, but a dormant holder's balance can be archived. Archival is not loss. A restored persistent entry retains its original value.

`instance` TTL is deliberately not managed by the library. It exposes `INSTANCE_TTL_THRESHOLD` and `INSTANCE_EXTEND_AMOUNT` as sane defaults but never calls `instance().extend_ttl()` itself, because the right cadence depends on the contract's traffic. If the contract instance is archived, the contract stops working until it is restored. This is the contract developer's responsibility.

From the CLI:

```bash
# Extend the contract instance: no key is given
stellar contract extend \
  --id $CID --source-account alice --network testnet \
  --ledgers-to-extend 535679 --durability persistent

# Extend a specific persistent entry.
# --key accepts symbols only, so a structured key such as
# Balance(Address) must be passed as base64-encoded XDR.
stellar contract extend \
  --id $CID --source-account alice --network testnet \
  --key-xdr "$KEY_XDR" \
  --ledgers-to-extend 535679 --durability persistent
```

`535679` ledgers is the CLI's maximum, roughly 30 days at a five-second close time. `--durability` accepts `persistent` or `temporary` and defaults to `persistent`.

The archival model, including the automatic-restoration behaviour introduced in Protocol 23 and how it interacts with default-valued entries, is covered in more depth in [Soroban State Archival — Storage Semantics and Security Implications]({{site.url_complet}}/2026/04/15/soroban-state-archival/).

## Generating a starting point

The [OpenZeppelin Contracts Wizard](https://wizard.openzeppelin.com/stellar) supports Stellar and emits a Rust contract from a checkbox UI (name, symbol, pre-mint amount, mintable, burnable, pausable, access control). It can export a single file, a Rust package, or a [Scaffold Stellar](https://scaffoldstellar.org/) package.

The wizard is a scaffold, not a substitute for reading the output. The library's own contributing guidelines are blunt about generated code: treat it as a first draft, read every line, and run `cargo +nightly fmt`, `cargo clippy` and `cargo test` before shipping.

## Conclusion

Choosing how to issue a fungible token on Stellar is a choice about which ecosystem you want to be native to. A classic asset with its Stellar Asset Contract is native to the classic DEX, anchors and path payments, at the price of fixed semantics. A custom Soroban token built on `stellar-tokens` gives full control over transfer and supply logic, at the price of leaving classic infrastructure behind. Handing SAC administration to an OpenZeppelin admin contract recovers custom authorization on the mint side while keeping the asset classic.

Within path 2, the library's design leans on Rust's type system: a single associated type selects the contract's behaviour and makes incompatible extensions unrepresentable. The extensions themselves are small and composable, and the attribute macros keep authorization declarative. The parts that demand attention are the ones the type system cannot check, namely TTL management for instance storage, the double `require_auth()` hazard, and the low-level `_no_auth` functions that trade safety for control.

The library is explicitly labelled experimental software by its authors. The [audit reports](https://github.com/OpenZeppelin/stellar-contracts/tree/main/audits) in the repository state what has been reviewed and what has not.

![Mindmap summarising SEP-41 fungible tokens on Stellar with OpenZeppelin]({{site.url_complet}}/assets/article/blockchain/stellar/stellar-openzeppelin-sep41.png)

## Frequently Asked Questions

**Q: SEP-41 defines ten functions, yet the OpenZeppelin `FungibleToken` trait exposes nine of them and omits `burn`. Why, and what does a contract have to do to be compliant?**

`burn` and `burn_from` live in a separate trait, `FungibleBurnable`. The split is deliberate: not every fungible-token use case wants burning, and the library prefers composable traits over one large interface with optional methods. SEP-41 does mandate burning, so a compliant contract must implement both `FungibleToken` and `FungibleBurnable`. In practice this costs one line, since `impl FungibleBurnable for MyToken {}` with an empty body is enough; the macro fills in the bodies and routes them through `BurnableOverrides` according to the contract's `ContractType`.

**Q: What prevents a contract from being both an allowlist token and a blocklist token?**

The associated type. `FungibleToken` declares `type ContractType: ContractOverrides`, and a type has exactly one implementation of a given trait, so a contract has exactly one `ContractType`. `FungibleAllowList` is declared with the supertrait bound `FungibleToken<ContractType = AllowList>` and `FungibleBlockList` with `FungibleToken<ContractType = BlockList>`. Implementing both would require `ContractType` to equal `AllowList` and `BlockList` simultaneously, which does not type-check. The exclusion is enforced at compile time, with no runtime check and no gas cost.

**Q: Why does a minimal token that never writes `MuxedAddress` still fail to compile without importing it?**

`#[contractimpl(contracttrait)]` copies the default bodies of any trait methods you did not override into your module. The default body of `FungibleToken::transfer` has the signature `fn transfer(e: &Env, from: Address, to: MuxedAddress, amount: i128)`. When that body is expanded at your call site, the name `MuxedAddress` must resolve in your module's scope. Rust macro hygiene does not automatically bring type paths along, so the import is required even though nothing you wrote refers to it. The error surfaces as `E0425: cannot find type MuxedAddress in this scope`, pointing at the attribute rather than at any line you typed.

**Q: The `Pausable` trait supplies a default body for `paused()` but not for `pause()` and `unpause()`. What is the reasoning?**

`paused()` is a pure read with one correct implementation. `pause()` and `unpause()` change state and must be authorized, and the library has no way to know whether the right gate is an owner, a role, a multisig or a governance vote. Rather than ship an unauthenticated default that a careless integrator might leave in place, the trait declares them without bodies so the compiler forces you to write one. The underlying free functions `pausable::pause(e)` and `pausable::unpause(e)` do exist and carry an explicit `# Security Warning` noting that they perform no authorization. This is the same reasoning behind `Base::mint`, `set_admin` and `set_owner` being auth-free.

**Q: Combine two ideas from the article. A token holder receives tokens once and then never touches the contract for a year. Explain what happens to their balance, and why the outcome would differ if the same data had been stored as an allowance.**

Balances live in `persistent` storage. The library extends a balance's TTL on *reads*, not on writes, so receiving a transfer does not by itself refresh the recipient's entry (though `Base::transfer` happens to read both sides, which does refresh it at transfer time). With no further activity for a year, the entry's TTL lapses and the balance is archived. Archival is recoverable: a restored persistent entry keeps its original value, so the holder's tokens are not destroyed, and Protocol 23's automatic restoration makes this largely transparent. An allowance would behave differently. Allowances live in `temporary` storage, which is deleted rather than archived on expiry, and is never restorable. That is a deliberate match to SEP-41's own semantics, where an allowance past its `live_until_ledger` "should be treated as a 0 amount allowance". Losing an expired allowance is the specified behaviour; losing a balance would be a bug, which is why the two use different tiers.

**Q: You want a token that trades on Stellar's classic DEX but whose minting is controlled by a three-of-five multisig with a daily rate limit. Which path do you take, and what can you still not do?**

Path 3: issue a classic asset, then call `set_admin` on its Stellar Asset Contract to transfer administration to an OpenZeppelin SAC-admin contract that implements the multisig and rate limit. The asset stays classic, so it keeps DEX listing, path payments and anchor support, while `mint`, `clawback`, `set_authorized` and `set_admin` now route through your authorization logic. What you cannot do is change transfer semantics. User-facing `transfer`, `approve` and `balance` remain on the SAC and follow protocol-fixed rules, so a transfer allowlist, a transfer fee, or a pause switch on transfers is out of reach. Those would require path 2 and the loss of classic DEX integration. Within path 3 you would then choose `sac_admin_wrapper` (explicit admin entry points, split interface) or `sac_admin_generic` (custom `__check_auth`, unified interface).

## References

### Specifications and protocol

- [SEP-0041: Token Interface](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0041.md)
- [Stellar Asset Contract](https://developers.stellar.org/docs/tokens/stellar-asset-contract)
- [Stellar Docs: State Archival](https://developers.stellar.org/docs/learn/fundamentals/contract-development/storage/state-archival)

### OpenZeppelin Stellar Contracts

- [OpenZeppelin Stellar Contracts (repository)](https://github.com/OpenZeppelin/stellar-contracts)
- [OpenZeppelin Stellar Contracts (documentation)](https://docs.openzeppelin.com/stellar-contracts)
- [Fungible Token module](https://docs.openzeppelin.com/stellar-contracts/tokens/fungible/fungible)
- [Audit reports](https://github.com/OpenZeppelin/stellar-contracts/tree/main/audits)
- [`stellar-tokens` on crates.io](https://crates.io/crates/stellar-tokens)
- [`examples/sac-admin-wrapper`](https://github.com/OpenZeppelin/stellar-contracts/tree/main/examples/sac-admin-wrapper)
- [`examples/fungible-pausable`](https://github.com/OpenZeppelin/stellar-contracts/tree/main/examples/fungible-pausable)

### Tooling

- [OpenZeppelin Contracts Wizard for Stellar](https://wizard.openzeppelin.com/stellar)
- [Stellar CLI Manual](https://developers.stellar.org/docs/tools/cli/stellar-cli)
- [Deploy to Testnet](https://developers.stellar.org/docs/build/smart-contracts/getting-started/deploy-to-testnet)
- [Deploy the Stellar Asset Contract for a Stellar asset](https://developers.stellar.org/docs/tools/cli/cookbook/deploy-stellar-asset-contract)
- [Extend a deployed contract's storage entry TTL](https://developers.stellar.org/docs/tools/cli/cookbook/extend-contract-storage)
- [Scaffold Stellar](https://scaffoldstellar.org/)
- [Stellar: How to Use the OpenZeppelin Contract Wizard to Create a Fungible Token](https://stellar.org/blog/developers/how-to-use-the-openzeppelin-contract-wizard)

### Related reading

- [Soroban State Archival — Storage Semantics and Security Implications]({{site.url_complet}}/2026/04/15/soroban-state-archival/)
- [Claude Code](https://claude.com/product/claude-code)
