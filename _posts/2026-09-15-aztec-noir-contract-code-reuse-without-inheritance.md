---
layout: post
title: "Code Reuse in Aztec Contracts — Modules, Traits and Library Crates Instead of Inheritance"
date:   2026-09-15
last_modified_at: 2026-09-17
lang: en
locale: en-GB
categories: blockchain ethereum ZKP
tags: aztec zkp noir smart-contracts solidity token
description: "Aztec contracts cannot inherit. What a contract module must own, what a Noir library can hold, and how a trait replaces virtual methods, on a two-variant token."
image: /assets/article/blockchain/aztec/2026-09-15-aztec-code-reuse-mindmap.png
isMath: false
---

[Aztec](https://aztec.network/) is a privacy-focused Layer 2 on Ethereum whose contracts are written in [Noir](https://noir-lang.org/), a Rust-like language that compiles to zero-knowledge circuits. A contract's private functions are proved on the user's device and its public functions run on a sequencer, but from the developer's side both sit in one Noir `contract` block, built with the Aztec.nr framework. The constraints of that language and framework, not of the chain, are the subject here.

A Solidity token that needs a pause switch writes `contract MyToken is ERC20, Pausable` and overrides one hook. An Aztec contract written in Noir cannot do that: the language has no inheritance, and the framework requires every entry point of a contract to be declared inside one `contract` block, in one file. The documentation says it plainly: "you cannot take a token contract and extend it to add minting functionality, or reuse it in a liquidity pool". A team that ships several variants of one token, say a full version and a lighter one without transfer lists, seems condemned to three copies of the same file.

It is not. Noir has crates, modules, generics and traits, and the Aztec framework's own state variables are built with exactly those. This article works through what a contract module must keep for itself, what can move into a library crate, and how a trait does the job that `virtual` and `override` do in Solidity, using a generic restricted token with a pause flag and a freeze list as the running example. It ends with the two things a library still cannot share, and the one dependency trap that catches everyone once.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why there is no inheritance

Two facts, one from the language and one from the framework, decide how every Aztec codebase is laid out.

**Noir has no inheritance.** It is a Rust-like language: structs, `impl` blocks, traits, generics, modules and crates. There is no `is`, no `super`, no virtual dispatch. Code is shared the way Rust shares it, by calling functions and implementing traits, never by extending a type.

**An Aztec contract is one module in one file.** The `#[aztec]` macro is applied to a `pub contract Name { … }` block. It walks the functions in that block and, for each `#[external(...)]` function, generates the wrapper that makes it callable: the code that builds the `PrivateContext` or `PublicContext` from the call inputs, checks initialization, hashes the arguments and returns the kernel inputs. It then computes the function selectors, builds the `Name::at(address)` interface other contracts use, and emits the artifact. It only looks inside the block. The [contract structure documentation](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/contract_structure) states the limitation and its scope: all `#[external]` functions "must be defined directly inside the `contract` block, that is, in the same file", while "it is possible to define `#[internal]` and helper functions in `mod`s in other files".

Together they rule out the Solidity pattern in both of its forms. You cannot inherit a base token because there is no inheritance, and you cannot import a base token's entry points because the macro would not see them. What remains is composition: the contract block declares its entry points, and everything those entry points *do* can live elsewhere.

## What a contract module must own

The line between "must be in the block" and "can be anywhere" is the design constraint, so it is worth stating precisely. Four things belong to the contract module and nothing else:

- **Entry-point declarations and their attributes.** `#[external("private")]`, `#[external("public")]`, `#[external("utility")]`, and the modifiers stacked on them: `#[authorize_once("from", "nonce")]` for authwit checks, `#[only_self]` for functions only the contract may call, `#[view]`, `#[initializer]`. These are what the macro reads.
- **The storage struct.** `#[storage] struct Storage<Context> { … }` declares the state variables, and the macro allocates storage slots to them in declaration order. The slot of a private state variable feeds every note hash and nullifier written under it, so the struct is not only a declaration but a commitment to a layout.
- **Events.** `#[event] struct Transfer { … }` is a contract type. The macro also keeps a global registry of event selectors across the whole crate graph and refuses two events with the same signature — a fact that matters for dependencies, below.
- **Calls that name the contract itself.** `self.enqueue_self.some_public_fn(args)` (queue a public function of this contract from a private one), `self.internal.helper(args)` (an inlined helper), and `self.emit(Event { … })`. The `enqueue_self` and `internal` objects are generated per contract.

Everything else is ordinary Noir: the checks, the arithmetic, the note movements, the reads and writes through state variables. Ordinary Noir can be in a library crate.

![An Aztec contract crate declares its entry points, storage struct, events and self-calls, and calls into a library crate that holds module structs, chain functions and traits; a second contract crate reuses the same library with a different storage struct]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-contract-crate-vs-library-concept.png)

## Library crates and module structs

A Noir crate declared with `type = "lib"` in its `Nargo.toml` can be depended on by any number of contract crates by path or by git tag. The Aztec framework itself is such a crate: `PublicMutable`, `PrivateSet`, `Map`, `DelayedPublicMutable` are structs in the `aztec` library, not language features. The pattern they follow is the one a project's own modules can follow.

A state variable is a struct holding a context and a storage slot, implementing the `StateVariable<N, Context>` trait, where `N` is the number of slots it occupies:

```rust
use aztec::context::{PrivateContext, PublicContext};
use aztec::state_vars::{PublicMutable, StateVariable};

/// A pause switch, as a reusable module: two public flags in two slots.
pub struct Pausable<Context> {
    is_paused: PublicMutable<bool, Context>,
    is_deactivated: PublicMutable<bool, Context>,
}

impl<Context> StateVariable<2, Context> for Pausable<Context> {
    fn new(context: Context, storage_slot: Field) -> Self {
        Self {
            is_paused: PublicMutable::new(context, storage_slot),
            is_deactivated: PublicMutable::new(context, storage_slot + 1),
        }
    }
    fn get_storage_slot(self) -> Field {
        self.is_paused.get_storage_slot()
    }
}

impl Pausable<PublicContext> {
    pub fn is_paused(self) -> bool { self.is_paused.read() }
    pub fn pause(self) { self.is_paused.write(true); }
    pub fn deactivate(self) {
        assert(self.is_paused.read(), "pause first");
        self.is_deactivated.write(true);
    }
}
```

Two properties of this struct carry the whole approach. First, the struct is generic over the context, and the methods are written per context: `impl Pausable<PublicContext>` for what public functions may do, `impl Pausable<&mut PrivateContext>` for what private functions may do. The type system then enforces the private/public split that Aztec imposes: a `PublicMutable` has no `read` in the private `impl`, so a private function that tries to read the pause flag does not compile, which is exactly what the protocol would otherwise refuse at proving time. Second, the struct is a *value*: a context handle and a slot number. It can be copied, passed to a function, returned from one. Nothing about it is tied to the contract that holds it in storage.

A contract uses the module by holding it as a field:

```rust
#[storage]
struct Storage<Context> {
    pausable: Pausable<Context>,                       // 2 slots
    balances: Owned<BalanceSet<Context>, Context>,     // private notes
    total_supply: PublicMutable<u128, Context>,
}
```

and the macro allocates the slots from the `N` of each field. Adding a module to a second contract is adding a line to its storage struct.

## Passing state to library functions

Module structs give reuse of *state*; the same property gives reuse of *logic*. Because a state variable is a value, a library function can take it as an argument and operate on it without the library ever owning storage. The transfer chain of a restricted token — check both parties, spend the sender's notes, create the recipient's note — is a function of the balance set, the freeze list and three arguments:

```rust
use aztec::state_vars::Owned;
use balance_set::BalanceSet;

pub type PrivateBalances = Owned<BalanceSet<&mut PrivateContext>, &mut PrivateContext>;

pub fn transfer_private(
    balances: PrivateBalances,
    freeze: Freezable<&mut PrivateContext>,
    from: AztecAddress,
    to: AztecAddress,
    amount: u128,
) {
    assert(!freeze.is_frozen(from), "Frozen: sender");
    assert(!freeze.is_frozen(to), "Frozen: recipient");
    balances.at(from).sub(amount).deliver(MessageDelivery::onchain_constrained());
    balances.at(to).add(amount).deliver(MessageDelivery::onchain_constrained());
}
```

The contract's entry point becomes a declaration plus one call:

```rust
#[authorize_once("from", "nonce")]
#[external("private")]
fn transfer(from: AztecAddress, to: AztecAddress, amount: u128, nonce: Field) {
    transfer_private(self.storage.balances, self.storage.freeze, from, to, amount);
    self.enqueue_self._assert_not_paused();
}
```

The storage struct, and with it the slot layout, stays in the contract. The library is told which balance set and which freeze list to use, on every call, by value. A second contract with a different storage struct passes its own fields and gets the same chain.

There is one wrinkle worth knowing in advance, because the compiler error is opaque. An `#[internal]` function is an entry point in the macro's eyes, and entry points may not take or return types that contain references. A private state variable holds a `&mut PrivateContext`, so a helper that *returns* a bundle of state variables cannot be `#[internal]`. It can be a `#[contract_library_method]`: a plain function inside the contract block, called directly rather than through `self.internal`, with no entry-point restrictions:

```rust
#[contract_library_method]
fn screening(storage: Storage<&mut PrivateContext>) -> FreezeAndLists {
    FreezeAndLists { freeze: storage.freeze, lists: storage.lists }
}
```

## Traits instead of virtual methods

Solidity variants differ by overriding hooks: OpenZeppelin's `ERC20` calls `_update(from, to, value)` on every balance change, and `ERC20Pausable` overrides it to add `_requireNotPaused()`. The base contract calls a method it does not define; the derived contract supplies it; the call is resolved through the inheritance graph.

Noir expresses the same idea with a trait. The library defines what a variant must be able to decide, and each variant supplies an implementation built from its own storage:

```rust
/// What a variant checks about the parties before any note moves.
pub trait Screening {
    fn transfer(self, from: AztecAddress, to: AztecAddress);
    fn mint(self, to: AztecAddress);
    fn burn(self, account: AztecAddress);
}

/// Full variant: freeze flags plus an allow/deny list.
pub struct FreezeAndLists {
    pub freeze: Freezable<&mut PrivateContext>,
    pub lists: TransferLists<&mut PrivateContext>,
}

/// Light variant: freeze flags only.
pub struct FreezeOnly {
    pub freeze: Freezable<&mut PrivateContext>,
}

impl Screening for FreezeAndLists {
    fn transfer(self, from: AztecAddress, to: AztecAddress) {
        assert(!self.freeze.is_frozen(from), "Frozen: sender");
        assert(!self.freeze.is_frozen(to), "Frozen: recipient");
        self.lists.check(from, to);
    }
    fn mint(self, to: AztecAddress) { /* … */ }
    fn burn(self, account: AztecAddress) { /* … */ }
}

impl Screening for FreezeOnly {
    fn transfer(self, from: AztecAddress, to: AztecAddress) {
        assert(!self.freeze.is_frozen(from), "Frozen: sender");
        assert(!self.freeze.is_frozen(to), "Frozen: recipient");
    }
    fn mint(self, to: AztecAddress) { /* … */ }
    fn burn(self, account: AztecAddress) { /* … */ }
}
```

and the chain is generic over it:

```rust
pub fn transfer_private<S>(balances: PrivateBalances, screening: S, from: AztecAddress, to: AztecAddress, amount: u128)
where
    S: Screening,
{
    screening.transfer(from, to);
    balances.at(from).sub(amount).deliver(MessageDelivery::onchain_constrained());
    balances.at(to).add(amount).deliver(MessageDelivery::onchain_constrained());
}
```

The difference from Solidity's mechanism is not cosmetic. A `virtual` call is resolved at compile time too in the EVM sense, but the pattern is designed around a class hierarchy in which the base does not know its derivations. A Noir trait bound is monomorphised: `transfer_private::<FreezeAndLists>` and `transfer_private::<FreezeOnly>` are two functions, each compiled with the concrete screening inlined. There is no dispatch at runtime, no table, no indirection in the circuit. The generic costs nothing and the light variant's circuit does not contain the list check it never runs.

The trait is also where the design decisions become visible. Reading `Screening` tells a reviewer, in one place, what every variant is required to decide about a transfer, a mint and a burn; reading the two implementations tells them how the variants differ. Three copies of a file tell the same story only to someone who diffs them.

## Two variants from one library

With the state in module structs, the chains in library functions and the variation in a trait, the two token contracts are short. The full variant:

```rust
#[aztec]
pub contract RestrictedToken {
    use restricted_token_lib::{Freezable, FreezeAndLists, Pausable, TransferLists, transfer_private, mint_private};

    #[storage]
    struct Storage<Context> {
        pausable: Pausable<Context>,
        freeze: Freezable<Context>,
        lists: TransferLists<Context>,
        balances: Owned<BalanceSet<Context>, Context>,
        total_supply: PublicMutable<u128, Context>,
    }

    #[event]
    struct Transfer { from: AztecAddress, to: AztecAddress, amount: u128 }

    #[contract_library_method]
    fn screening(storage: Storage<&mut PrivateContext>) -> FreezeAndLists {
        FreezeAndLists { freeze: storage.freeze, lists: storage.lists }
    }

    #[authorize_once("from", "nonce")]
    #[external("private")]
    fn transfer(from: AztecAddress, to: AztecAddress, amount: u128, nonce: Field) {
        transfer_private(self.storage.balances, screening(self.storage), from, to, amount);
        self.enqueue_self._assert_not_paused();
        self.emit(Transfer { from, to, amount }).deliver_to(to, MessageDelivery::onchain_constrained());
    }

    #[external("public")]
    #[only_self]
    fn _assert_not_paused() {
        assert(!self.storage.pausable.is_paused(), "paused");
    }
}
```

The light variant drops `lists` from the storage struct, returns `FreezeOnly` from `screening`, and is otherwise the same text. What remains duplicated between them is the part the macro must see: declarations, attributes, the enqueue, the event. What is not duplicated is every rule.

![A private transfer entry point calls the library chain with the contract's balance set and screening value; the chain screens both parties through the trait, spends and creates notes, and returns; the entry point then enqueues the contract's own public pause check and emits its event]({{site.url_complet}}/assets/article/blockchain/aztec/aztec-library-chain-call-sequence.png)

## Inlining, and what the refactor costs at runtime

A reasonable worry is that moving logic behind function calls and generic bounds changes the circuit. It does not. Noir inlines ordinary function calls into the caller's circuit, the same way the framework's `#[internal]` helpers are "inlined at call sites" in the documentation's words, and a monomorphised generic is just another function. The circuit a private entry point compiles to is the same whether its body was written inline, in an `#[internal]` helper, or in a library function three crates away.

That claim is checkable rather than a matter of trust: `aztec profile gates ./target` reports the gate count of every private function in a workspace. On a three-variant token where the mint, transfer and burn chains were moved from the contracts into a library exactly as above, the profile of all forty-eight private circuits was byte-identical before and after. The refactor is free at runtime, and the profile diff is the acceptance test to run after it.

## Contract crates as dependencies: the interface, not the code

There is a second kind of reuse, and it is easy to mistake for the first. A crate with `type = "contract"` can be a dependency too, and the [calling-contracts documentation](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/calling_contracts) shows why: importing `Token` from the token crate gives `Token::at(address).transfer(to, amount)`, a typed call interface with the right selectors, to be used with `self.call`, `self.enqueue` or `self.view`.

What that dependency does not give is the token's *implementation*. The entry points are inside the token's contract block; the importing contract can call them on a deployed instance, and can do nothing else with them. A "restricted token" that wraps a stock token by forwarding to it is a different contract at a different address, with its own notes, and the wrapped token's notes belong to the wrapper, not to the users — a design that breaks the ownership model the moment a user wants to spend. Contract dependencies are for *calling* contracts, not for extending them.

Two traps come with contract dependencies, and both surface as confusing errors:

- **Event selector collisions.** The `#[event]` macro registers every event signature it sees across the crate graph, and refuses a duplicate. A token that depends on another contract crate which declares the same `Transfer { from, to, amount }` — or the same `RoleGranted` — fails to compile with `Event selector collision detected`. The fix is to depend on an interface-only stub instead: a contract crate whose functions have the right signatures and empty bodies, no events, never deployed. Selectors depend only on names and parameter types, so a call made through the stub is dispatched to the real contract.
- **Nested workspaces.** `nargo` resolves the outermost `[workspace]` above the current directory. A contract checked out as a submodule inside another Nargo workspace cannot be built in place: its packages are "not found" because the tool is looking at the parent's member list. Build it from a copy outside the tree.

## What still cannot be shared

### Events: emitted by the contract, shaped by the library

Events deserve their own paragraph, because they are the one thing a library can neither declare nor emit, and the constraint comes from what the `#[event]` and `#[aztec]` macros generate, not from a style rule. An `#[event] struct Transfer { from, to, amount }` is turned by the macro into a contract type: it gains an `EventInterface` implementation with a selector derived from the struct's signature, and that selector is entered in the crate-graph-wide registry mentioned above. The struct therefore belongs to the contract that declares it, in the same sense that the storage struct does.

Emitting it is a method of the generated `self`, and the two execution contexts differ in what emitting means. In a **public** function, `self.emit(Transfer { … })` writes a public log: plaintext, visible to everyone, the same as a Solidity event, and nothing further to do. In a **private** function, `self.emit(...)` does two things: it pushes a nullifier that is a randomised commitment to the event, so that a third party can later verify the event is authentic without learning its content; and it returns an `EventMessage` that the caller *must* deliver, or the event is lost. Delivery names a recipient and a mode: `deliver_to(to, MessageDelivery::onchain_constrained())` encrypts the event to `to` and proves in the circuit that the ciphertext matches, at a measurable gate cost per delivery; the same message can be delivered again to a second party, such as an auditor.

None of that is available to a library function. It has no `self`, it cannot name the contract's event type, and its `PrivateContext` argument is not the generated object that knows how to emit. What it *can* do is decide the content and return it. The division of labour that follows is the same one as for `enqueue_self`: the library computes, the contract publishes.

```rust
// library: the chain returns what happened, as plain values
pub struct TransferOutcome { pub from: AztecAddress, pub to: AztecAddress, pub amount: u128 }

pub fn transfer_private<S: Screening>(balances: PrivateBalances, screening: S,
                                      from: AztecAddress, to: AztecAddress, amount: u128) -> TransferOutcome {
    screening.transfer(from, to);
    balances.at(from).sub(amount).deliver(MessageDelivery::onchain_constrained());
    balances.at(to).add(amount).deliver(MessageDelivery::onchain_constrained());
    TransferOutcome { from, to, amount }
}

// contract: the entry point owns the event type and the delivery decision
let done = transfer_private(self.storage.balances, screening(self.storage), from, to, amount);
let event = self.emit(Transfer { from: done.from, to: done.to, amount: done.amount });
event.deliver_to(to, MessageDelivery::onchain_constrained());
event.deliver_to(auditor, MessageDelivery::onchain_constrained());
```

Two consequences follow. The *policy* of who receives an event and in which mode is a contract decision that the reader of `main.nr` can see, which is where a privacy reviewer wants it: the recipients of a private event are exactly the parties who learn the transfer happened. And a variant that must not emit something — a light token with no auditor, for instance — simply omits the second `deliver_to`; the library did not decide that for it.

### The residue

After the refactor, each variant still carries, per entry point, the declaration line, its attributes, the `enqueue_self` call and the event emission. On the token above that is roughly forty percent of what the entry points used to be, and all of it is declaration rather than rule. A test that reads each variant's selectors from its compiled interface and asserts the shared set is equal across variants turns "keep the files in step" from a review rule into a check.

Two things could change this. The documentation itself says the single-file restriction is not permanent: "we expect to lift some of these restrictions sometime after the release of Noir 1.0". And Noir's `comptime` metaprogramming, which is how the `#[aztec]` macro generates its wrappers, selectors and interfaces today, could in principle stamp a set of entry points into a contract from a description — the framework already generates `interface()` and `enqueue_self` that way. A project-level macro of that kind is possible now and fragile now, because it would depend on macro internals that have changed with every framework release. Until the language moves, the trait-and-library shape above is the stable one.

## Conclusion

Aztec contracts cannot inherit, and every entry point must sit in one contract block, but that constraint is narrower than "one file per token". The contract module owns four things: entry-point declarations with their attributes, the storage struct that fixes the slot layout, the event types, and the calls that name the contract itself. Everything those entry points do can live in a library crate, because Aztec's state variables are values that a function can take as arguments, and because a Noir trait with a generic bound does at compile time what `virtual` and `override` do in Solidity, monomorphised into the circuit at no cost. A token with two variants becomes one library holding the rules and two short contracts holding declarations plus one trait implementation each — with a gate profile that a diff can prove unchanged.

![Mindmap of code reuse in Aztec contracts covering why there is no inheritance, what the contract module must own, library crates and module structs, traits instead of virtual methods, contract dependencies as interfaces only, and what still cannot be shared]({{site.url_complet}}/assets/article/blockchain/aztec/2026-09-15-aztec-code-reuse-mindmap.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Contract block** | The `pub contract Name { … }` module the `#[aztec]` macro processes; the only place `#[external]` functions, `#[storage]` and `#[event]` types may be declared. |
| **`#[aztec]` macro** | The comptime macro that turns the contract block into an artifact: a callable wrapper per `#[external]` function, the selectors, the `Name::at(address)` interface, storage-slot allocation. |
| **Library crate** | A Noir crate with `type = "lib"`; holds structs, traits and functions that any contract crate can depend on. The `aztec` framework is one. |
| **State variable** | A struct implementing `StateVariable<N, Context>`: a context handle plus a storage slot, occupying `N` slots. `PublicMutable`, `Map`, `PrivateSet` and a project's own modules all are. |
| **Module struct** | A project-defined state variable composing framework ones (a pause switch, a freeze list), held as a field of a contract's storage struct. |
| **Context** | The execution environment a function runs in — `PublicContext` on the sequencer, `&mut PrivateContext` on the user's device — and the type parameter that selects which `impl` block of a state variable applies. |
| **`#[internal]`** | A helper callable only from the same contract, inlined at the call site; still an entry point for the macro, so it cannot take or return types holding references. |
| **`#[contract_library_method]`** | A plain function inside the contract block with no entry-point restrictions, called directly; the place for a helper that returns a bundle of state variables. |
| **Monomorphisation** | Compiling a generic function once per concrete type it is used with, so a trait bound costs nothing at runtime and each variant's circuit contains only its own implementation. |
| **Event selector registry** | The `#[event]` macro's crate-graph-wide table of event signatures; two identical events in one build are refused, which is why a token cannot depend on a contract crate that declares its events. |

### Security Implementation Checklist

#### Storage and layout

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | The `#[storage]` struct stays in each contract and library functions take state variables as arguments; no library-owned composite re-slots an existing private state variable. | Moving a private state variable's slot changes every note hash and nullifier derived from it; existing notes become unspendable. |
| ☐ | New fields are appended after existing ones. | Inserting a field shifts the slots of everything declared after it and orphans public state. |

#### Rules and variants

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every rule that must hold in all variants is in the library chain, not in an entry point. | A rule added to one variant's entry point is silently absent from the others. |
| ☐ | The trait names every decision a variant must make; the light implementation omits checks on purpose and says so. | A variant that "forgets" a check is indistinguishable from one that chose to drop it. |
| ☐ | Each variant's `#[contract_library_method]` builds its screening value from its own storage in one place. | Two entry points passing different screening values apply different rules to the same operation. |

#### Verification

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | `aztec profile gates` is diffed before and after moving logic into the library; every private circuit is identical. | A changed count means the refactor added or dropped a read, a delivery or a check. |
| ☐ | Selectors of the shared entry points are pinned by a test across variants. | A renamed or re-typed entry point in one variant breaks tooling that addresses the set by selector. |
| ☐ | Contract-crate dependencies are interface-only stubs when the depending contract declares the same events. | The build fails on an event selector collision, or a "fix" renames a standard event. |

## Frequently Asked Questions

**Q: Why can a Noir library not simply export a token's `transfer` entry point?**

Because `#[external]` functions are processed by the `#[aztec]` macro, which reads only the contract block it is applied to. A function in a library is invisible to it: no wrapper is generated, so it has no selector and no entry in the artifact. The library can export the *body* as an ordinary function; the contract must declare the entry point that calls it.

**Q: How does a library function get access to the contract's storage?**

It is passed the state variable as an argument. A state variable is a value (a context handle and a slot number), so `transfer_private(self.storage.balances, …)` hands the library exactly the balance set the contract holds, without the library ever declaring storage. The contract keeps the storage struct, and with it the slot layout.

**Q: What does a trait give that a plain function parameter would not?**

A named contract between the library and the variants. `Screening` lists the decisions every variant must be able to make; each variant implements it from its own storage; the chain is generic over it and monomorphised, so the light variant's circuit does not contain the list check it never runs. A plain boolean parameter would carry the same information at runtime but would put a branch in every circuit and would not name the decision.

**Q: Does moving logic into a library change the proving cost?**

No. Noir inlines function calls and monomorphises generics, so the circuit an entry point compiles to is the same whether its body was inline, in an `#[internal]` helper or in a library. It is worth proving rather than assuming: `aztec profile gates` before and after, diffed, is a one-command acceptance test.

**Q: I depend on another contract crate to reuse its code and get "Event selector collision detected". Why?**

A contract dependency gives you a call interface, not code, and it brings that contract's `#[event]` types into the build. The macro keeps a global registry of event signatures and refuses a duplicate, so a token declaring `Transfer { from, to, amount }` cannot depend on a contract crate that declares the same. Depend on an interface-only stub with the same function signatures and no events; selectors depend on names and types only, so a call made through it is dispatched to the real contract.

**Q: A contract holds a pause switch as a module struct. Why does the private transfer not read the flag directly instead of enqueueing a public call?**

Because the module's private `impl` does not offer a read on a `PublicMutable`, and that is deliberate: a private function is proved against a past block and cannot know the current value. The type system enforces in the library what the protocol would refuse at proving time. The private entry point enqueues the contract's own `#[only_self]` public function, which reads the flag in the public phase, one of the four things that must stay in the contract block.

## References

- [Aztec.nr — Contract structure and its "Current Limitations"](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/contract_structure)
- [Aztec.nr — Attributes and macros (`#[external]`, `#[internal]`, `#[only_self]`)](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/functions/attributes)
- [Aztec.nr — State variables and the `StateVariable` trait](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/state_variables)
- [Aztec.nr — Calling other contracts](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/calling_contracts)
- [Aztec.nr — Dependencies](https://docs.aztec.network/developers/docs/aztec-nr/framework-description/dependencies)
- [Noir — Traits](https://noir-lang.org/docs/noir/concepts/traits)
- [Noir — Generics](https://noir-lang.org/docs/noir/concepts/generics)
- [Noir — Comptime metaprogramming](https://noir-lang.org/docs/noir/concepts/comptime)
- [Solidity — Inheritance](https://docs.soliditylang.org/en/latest/contracts.html#inheritance)
- [OpenZeppelin Contracts 5.x — ERC20 and the `_update` hook](https://docs.openzeppelin.com/contracts/5.x/erc20)
- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [How Aztec Works — Private Execution, Notes and Nullifiers, and a Comparison with Zama FHE, Zcash, Canton and Railgun]({{site.url_complet}}/2026/09/08/how-aztec-works-private-execution-model/)
- [Reading Public State from a Private Function on Aztec — Why a Pause Flag Comes with a Delay]({{site.url_complet}}/2026/09/14/aztec-delayed-public-mutable-pause-privacy-delay/)
- [Aztec Contract Standards — AIP-20, AIP-721, ARC-1155, ARC-403, AIP-4626 and the Escrow Standard]({{site.url_complet}}/2026/09/11/aztec-contract-standards-overview/)
- [AIP-20, the Aztec Token Standard, Compared with ERC-20 and ERC-7984]({{site.url_complet}}/2026/09/11/aip-20-aztec-token-standard-vs-erc-20-erc-7984/)
- [ERC-20 Implementation Comparison — OpenZeppelin, Solady, and Solarity Solidity Library]({{site.url_complet}}/2026/02/13/erc20-library-comparison-openzeppelin-solady-solarity/)
- [Packing Small Values into One Field on Aztec — The Packable Trait, Its Cost and Its Traps]({{site.url_complet}}/2026/09/16/aztec-packable-storage-packing/)
