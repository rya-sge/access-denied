# Anchor - Unchecked type

https://www.anchor-lang.com/docs/the-accounts-struct

Two of the Anchor account types, [AccountInfo](https://docs.rs/anchor-lang/latest/anchor_lang/accounts/account_info/index.html) and [UncheckedAccount](https://docs.rs/anchor-lang/latest/anchor_lang/accounts/unchecked_account/index.html) do not implement any checks on the account being passed. 

Anchor implements safety checks that encourage additional documentation describing why additional checks are not necessary.



## Safety checks

Attempting to build a program containing the following excerpt with `anchor build`:

```rust
#[derive(Accounts)]
pub struct Initialize<'info> {
    pub potentially_dangerous: UncheckedAccount<'info>
}
```

will result in an error similar to the following:

```shell
Error:
        /anchor/tests/unchecked/programs/unchecked/src/lib.rs:15:8
        Struct field "potentially_dangerous" is unsafe, but is not documented.
        Please add a `/// CHECK:` doc comment explaining why no checks through types are necessary.
        See https://book.anchor-lang.com/anchor_in_depth/the_accounts_struct.html#safety-checks for more information.
```

To fix this, write a doc comment describing the potential security implications, e.g.:

```rust
#[derive(Accounts)]
pub struct Initialize<'info> {
    /// CHECK: This is not dangerous because we don't read or write from this account
    pub potentially_dangerous: UncheckedAccount<'info>
}
```



Note

The doc comment needs to be a [line or block doc comment](https://doc.rust-lang.org/reference/comments.html#doc-comments) (/// or /**) to be interpreted as doc attribute by Rust. Double slash comments (//) are not interpreted as such.