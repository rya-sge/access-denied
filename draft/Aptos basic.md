# Aptos basic

### 

### Module Structure

Modules define state using structs that can hold resources and capabilities:

```
struct CredCapabilities has key {
    mint_cap: coin::MintCapability<CRED>,
    burn_cap: coin::BurnCapability<CRED>,
}
```

- Resources like `CredCapabilities` store privileged operations (e.g., minting and burning tokens) securely on-chain.





### Initialization module

Modules are initialized with a signer, who sets up the module's resources:

```
 fun init_module(sender: &signer) {
        let (burn_cap, freeze_cap, mint_cap) = coin::initialize<CRED>(
            sender,
            string::utf8(b"Credibility"),
            string::utf8(b"CRED"),
            8,
            false,
        );
        move_to(sender, CredCapabilities { mint_cap, burn_cap });
        coin::destroy_freeze_cap(freeze_cap);
    }
```

### Details

This process creates the core resources and ensures security by removing unnecessary capabilities.

Aptos allows for permissionless publishing of [modules](https://aptos.dev/build/smart-contracts/book/modules-and-scripts) within a [package](https://aptos.dev/build/smart-contracts/book/packages) as well as [upgrading](https://aptos.dev/build/smart-contracts/book/package-upgrades) those that have appropriate compatibility policy set.

A module contains several structs and functions, much like Rust.

During package publishing time, a few constraints are maintained:

- Both Structs and public function signatures are published as immutable.
- The `init_module` function plays a crucial role in module initialization:
  - When a module is published for the first time (i.e., the module does not exist on-chain), the VM will search for and execute the `init_module(account: &signer)` function.
  - When upgrading an existing module that is already on-chain, the `init_module` function will NOT be called.
  - The signer of the account that is publishing the module is passed into the `init_module` function.
  - **This function must be private and not return any value.**
  - The `init_module` function can have at most one parameter, and its type must be `&signer`
  - The `init_module` function should not have generic parameters
  - The `init_module` function is commonly used to initialize module-specific data structures or set initial states.

Reference: [aptos.dev/build/smart-contracts/modules-on-aptos](https://aptos.dev/build/smart-contracts/modules-on-aptos)

### 

### Entry function

```
public entry fun register(account: &signer) {
        coin::register<CRED>(account);
    }
```

These functions allow users or other modules to safely interact with the resources.

## Access control

### Friend functions

```
 public(friend) fun mint(
        module_owner: &signer,
        to: address,
        amount: u64
    ) acquires CredCapabilities {
        let caps = borrow_global<CredCapabilities>(signer::address_of(module_owner));
        let coins = coin::mint<CRED>(amount, &caps.mint_cap);
        if (coin::is_account_registered<CRED>(to)) {
            coin::deposit(to, coins);
        } else {
            coin::destroy_zero(coins);
        };
    }
```

Only authorized modules or addresses can call certain privileged operations.

Controlled using `borrow_global` to access stored resources securely.

```rust
  let caps = borrow_global<CredCapabilities>(signer::address_of(module_owner));
```

## Resource Management

### Coin

- `coin::deposit` / `coin::withdraw` — move coins between accounts safely.
- `coin::merge` — combine multiple coin resources.
- `coin::destroy_zero` — safely discard unused resources.
- Objects can also be transferred and referenced safely, allowing flexible resource handling.

```rust
coin::deposit(defender_addr, pool);

coin::merge(&mut arena.prize_pool, chall_coins);

let first_bet = coin::withdraw<cred_token::CRED>(player, bet_amoun
```



## Global storage - Operators

Move programs can create, delete, and update resources in global storage using the following five instructions:



| Operation                               | Description                                                  | Aborts?                                 |
| --------------------------------------- | ------------------------------------------------------------ | --------------------------------------- |
| `move_to<T>(&signer,T)`                 | Publish `T` under `signer.address`                           | If `signer.address` already holds a `T` |
| `move_from<T>(address): T`              | Remove `T` from `address` and return it                      | If `address` does not hold a `T`        |
| `borrow_global_mut<T>(address): &mut T` | Return a mutable reference to the `T` stored under `address` | If `address` does not hold a `T`        |
| `borrow_global<T>(address): &T`         | Return an immutable reference to the `T` stored under `address` | If `address` does not hold a `T`        |
| `exists<T>(address): bool`              | Return `true` if a `T` is stored under `address`             | Never                                   |



Reference: [https://aptos.dev/build/smart-contracts/book/global-storage-operators](https://aptos.dev/build/smart-contracts/book/global-storage-operators)

### Example: `Counter`

The simple `Counter` module below exercises each of the five global storage operators. The API exposed by this module allows:

- Anyone to publish a `Counter` resource under their account
- Anyone to check if a `Counter` exists under any address
- Anyone to read or increment the value of a `Counter` resource under any address
- An account that stores a `Counter` resource to reset it to zero
- An account that stores a `Counter` resource to remove and delete it

```rust
module 0x42::counter {
  use std::signer;

  /// Resource that wraps an integer counter
  struct Counter has key { i: u64 }

  /// Publish a `Counter` resource with value `i` under the given `account`
  public fun publish(account: &signer, i: u64) {
    // "Pack" (create) a Counter resource. This is a privileged operation that
    // can only be done inside the module that declares the `Counter` resource
    move_to(account, Counter { i })
  }

  /// Read the value in the `Counter` resource stored at `addr`
  public fun get_count(addr: address): u64 acquires Counter {
    borrow_global<Counter>(addr).i
  }

  /// Increment the value of `addr`'s `Counter` resource
  public fun increment(addr: address) acquires Counter {
    let c_ref = &mut borrow_global_mut<Counter>(addr).i;
    *c_ref = *c_ref + 1
  }

  /// Reset the value of `account`'s `Counter` to 0
  public fun reset(account: &signer) acquires Counter {
    let c_ref = &mut borrow_global_mut<Counter>(signer::address_of(account)).i;
    *c_ref = 0
  }

  /// Delete the `Counter` resource under `account` and return its value
  public fun delete(account: &signer): u64 acquires Counter {
    // remove the Counter resource
    let c = move_from<Counter>(signer::address_of(account));
    // "Unpack" the `Counter` resource into its fields. This is a
    // privileged operation that can only be done inside the module
    // that declares the `Counter` resource
    let Counter { i } = c;
    i
  }

  /// Return `true` if `addr` contains a `Counter` resource
  public fun exists_at(addr: address): bool {
    exists<Counter>(addr)
  }
}
```

## Object

### Transfer object

```rust
module my_addr::object_playground {
  use aptos_framework::object::{Self, Object};

  /// Transfer to another address, this can be an object or account
  fun transfer<T: key>(owner: &signer, object: Object<T>, destination: address) {
    object::transfer(owner, object, destination);
  }

  /// Transfer to another object
  fun transfer_to_object<T: key, U: key>(
    owner: &signer,
    object: Object<T>,
    destination: Object<U>
  ) {
    object::transfer_to_object(owner, object, destination);
  }
}
```

https://aptos.dev/build/smart-contracts/object/using-objects#transfer-of-ownership

## Signer

### `signer` Operators

[Section titled “signer Operators”](https://aptos.dev/build/smart-contracts/book/signer#signer-operators)

The `std::signer` standard library module provides two utility functions over `signer` values:

| Function                                    | Description                                                  |
| ------------------------------------------- | ------------------------------------------------------------ |
| `signer::address_of(&signer): address`      | Return the `address` wrapped by this `&signer`.              |
| `signer::borrow_address(&signer): &address` | Return a reference to the `address` wrapped by this `&signer`. |

In addition, the `move_to<T>(&signer, T)` [global storage operator](https://aptos.dev/build/smart-contracts/book/global-storage-operators) requires a `&signer` argument to publish a resource `T` under `signer.address`’s account. This ensures that only an authenticated user can elect to publish a resource under their `address`.

https://aptos.dev/build/smart-contracts/book/signer

### Transferring a coin

[Section titled “Step 4.3.4: Transferring a coin”](https://aptos.dev/build/guides/first-coin#step-434-transferring-a-coin)

Aptos provides several building blocks to support coin transfers:

- `coin::deposit<CoinType>`: Allows any entity to deposit a coin into an account that has already called `coin::register<CoinType>`.
- `coin::withdraw<CoinType>`: Allows any entity to extract a coin amount from their account.
- `aptos_account::transfer_coins<CoinType>`: Transfer coins of specific CoinType to a receiver.

https://aptos.dev/build/guides/first-coin