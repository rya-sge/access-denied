# Aptos concept

## Vault

### **Module Name**

`secret_vault::vault` – A simple vault module to store a secret string for a specific owner.

------

### **Core Concepts**

1. **Data Structure**

```
struct Vault has key {
    secret: String
}
```

- Represents a vault that stores a single `secret` string.
- Stored under the owner’s account.

------

1. **Error Handling**

```
const NOT_OWNER: u64 = 1;
```

- Prevents non-owners from accessing the vault.

------

1. **Events**

```
#[event]
struct SetNewSecret has drop, store {}
```

- Emitted whenever a new secret is set.

------

1. **Entry Function**

```
public entry fun set_secret(caller: &signer, secret: vector<u8>)
```

- Converts a byte vector to a UTF-8 string and stores it in a `Vault` resource under the caller’s account.
- Emits `SetNewSecret` event.

------

1. **View Function**

```
public fun get_secret(caller: address): String acquires Vault
```

- Retrieves the secret for a given owner address.
- Ensures only the owner can access it (`assert!(caller == @owner, NOT_OWNER)`).

------

1. **Test Function**

```
#[test(owner = @0xcc, user = @0x123)]
fun test_secret_vault(owner: &signer, user: &signer) acquires Vault
```

- Sets up a test environment.
- Tests `set_secret` and ensures the secret is correctly stored and retrievable.
- Prints a debug message on success.

------

### **Summary**

This module is a **basic secret storage vault**:

- Each account can store one secret.
- Only the owner can read their secret.
- Stores secrets in a Move `resource` and uses events for tracking changes.