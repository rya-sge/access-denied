---
layout: post
title: Rust for Solana - Basic knowledge
date: 2025-02-10
lang: en
locale: en-GB
categories: solana
tags: solana rust code code4Arena
classification
description: This article explains the basic knowledge of Rust to understand and write Solana Programs
image: /assets/article/blockchain/solana/rust-solana.png
isMath: false
---

If you want to understandard Solana programs, it will be easier if you already know basic concept related to Rust programming.

During a code4Arena context ([Pump Science](https://github.com/code-423n4/2025-01-pump-science)), I have regrouped the main Rust point that I found relevant to understand the codebase. I used ChatGPT and the [rust documentation](https://doc.rust-lang.org/stable/book/title-page.html) to get a definition for each of them.

This article explores the following points, grouped into topics for clarity: `as_ref()`, `Some()` and `is_Some()`, `self` and `&self`, `unwrap`, `Ok(())`, `&mut` and `&`, and the `ctx` parameter.

[TOC]

------

## Ownership and References in Rust

See also [doc.rust-lang.org - Method Syntax](https://doc.rust-lang.org/stable/book/ch05-03-method-syntax.html?highlight=self#wheres-the---operator)

### `self` and `&self`

- `self`: Refers to the instance of the struct being acted upon. It is consumed, which means the caller relinquishes ownership.
- `&self`: A borrowed reference to the instance, enabling non-destructive access.

These keywords are used primarily in method definitions, e.g.,

```rust
impl MyStruct {
    fn consume(self) { /* Ownership taken */ }
    fn borrow(&self) { /* Read-only access */ }
}
```

### `&mut` and `&`

- `&`: Represents an immutable reference to a value. Multiple immutable references can coexist.

Error example:

If you try to modify an immutable reference in your function, you will receive the following error from the compiler

> Cannot borrow `*variable_name` as mutable, as it is behind a `&` reference

- `&mut`: Represents a mutable reference. Only one mutable reference is allowed at a time.

Error example:

If you have more that one mutable reference to a value, you will have the following error:

> cannot borrow `variable_name` as mutable more than once at a time

See also [doc.rust-lang.org _ references and borrowingl](https://doc.rust-lang.org/stable/book/ch04-02-references-and-borrowing.html)

### `as_ref()`

- Used to convert an `Option` or another wrapper type into a reference to its value, if it exists. For instance:

```rust
let opt: Option<String> = Some("Rust".to_string());
let ref_opt: Option<&String> = opt.as_ref();
```

This enables non-destructive access to the contained value.

Another example from [Rust - ch17-03 - design pattern](https://doc.rust-lang.org/stable/book/ch17-03-oo-design-patterns.html?highlight=as_ref#adding-approve-to-change-the-behavior-of-content)

```rust
impl Post {
    // --snip--
    pub fn new() -> Post {
        Post {
            state: Some(Box::new(Draft {})),
            content: String::new(),
        }
    }
    pub fn content(&self) -> &str {
        self.state.as_ref().unwrap().content(self)
    }
    // --snip--
}
```

------



## Option, Result, and Error Handling

### Option and Result Types

#### `Some()` and `is_Some()`

- `Some(value)`: Represents the presence of a value in an `Option`.
- `is_Some()`: A method to check if an `Option` contains a value. Example:

```rust
let opt = Some(10);
if opt.is_Some() {
    println!("Option has a value.");
}
```

#### `unwrap()`

- Extracts the value from `Option` or `Result`.
- Panics if called on `None` or `Err`, so use with caution or in situations where failure is not possible.

```rust
let value = Some(42).unwrap(); // Panics if None
```

------

### Error Handling in Rust

The `Result` enum is defined as having two variants, `Ok` and `Err`, as follows:

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

The `T` and `E` are generic type parameter

- `T` represents the type of the value that will be returned in a success case within the `Ok` variant
- E` represents the type of the error that will be returned in a failure case within the `Err` variant. 

#### `Ok(())`

Represents success in a `Result` type, especially when no additional data is required. Commonly used in functions that return `Result<(), ErrorType>`.

```rust
fn example() -> Result<(), String> {
    Ok(())
}
```

See [doc.rust-lang.org - Recoverable Errors with `Result`](https://doc.rust-lang.org/stable/book/ch09-02-recoverable-errors-with-result.html?highlight=option#recoverable-errors-with-result)

----



### `?` Operator (Error Propagation)

- Used for **propagating errors** in `Result<T, E>` or `Option<T>`.
- If the operation succeeds, it unwraps the value.
- If it fails, it **returns early** with the error.

Example:

```rust
rustCopyEditfn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("Cannot divide by zero".to_string())
    } else {
        Ok(a / b)
    }
}

fn try_divide() -> Result<(), String> {
    let result = divide(10, 2)?; // If error occurs, function exits early.
    println!("Result: {}", result);
    Ok(())
}
```

Example in Solana:

```rust
let locker = &mut ctx
            .accounts
            .into_bonding_curve_locker_ctx(ctx.bumps.bonding_curve);
// If this fails, it returns the error immediately.
locker.revoke_mint_authority()?;
locker.lock_ata()?;
```

See [pump-science-create_bonding_curve.rs#L173](https://github.com/code-423n4/2025-01-pump-science/blob/main/programs/pump-science/src/instructions/curve/create_bonding_curve.rs#L173)

## Implementing Methods and Traits with `impl`

### Using `impl` for Methods

`impl` is used to define methods for structs and enums.

Example:

```rust
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }
}
```

Usage:

```rust
let rect = Rectangle { width: 10, height: 5 };
println!("Area: {}", rect.area());
```

### Implementing a Trait

Rust allows defining behaviors via **traits** and implementing them with `impl`.

Example:

```rust
trait Printable {
    fn print(&self);
}

impl Printable for Rectangle {
    fn print(&self) {
        println!("Rectangle: {} x {}", self.width, self.height);
    }
}
```

Usage:

```rust
let rect = Rectangle { width: 10, height: 5 };
rect.print();
```

### Associated Functions (Static Methods)

Methods that do not require an instance.

Example:

```rust
impl Rectangle {
    fn new(width: u32, height: u32) -> Self {
        Self { width, height }
    }
}
```

Usage:

```rust
let rect = Rectangle::new(10, 5);
```

Example in Solana

```rust
impl<'info> IntoBondingCurveLockerCtx<'info> for CreateBondingCurve<'info> {
    fn into_bonding_curve_locker_ctx(
        &self,
        bonding_curve_bump: u8,
    ) -> BondingCurveLockerCtx<'info> {
        BondingCurveLockerCtx {
            bonding_curve_bump,
            mint: self.mint.clone(),
            bonding_curve: self.bonding_curve.clone(),
            bonding_curve_token_account: self.bonding_curve_token_account.clone(),
            bonding_curve_sol_escrow: self.bonding_curve_sol_escrow.clone(),
            token_program: self.token_program.clone(),
            global: self.global.clone(),
        }
    }
}
```

See [pump science - create_bonding_curve.rs#L86](https://github.com/code-423n4/2025-01-pump-science/blob/main/programs/pump-science/src/instructions/curve/create_bonding_curve.rs#L86)

## Context in Solana Programming

### `ctx`

Commonly seen in Solana programs, `ctx` often refers to a context structure containing accounts and program-specific information. This is part of the [Anchor framework](https://www.anchor-lang.com/), simplifying Solana smart contract development.

```rust
process(ctx: Context<MyAccounts>) -> ProgramResult {
    // Use ctx.accounts for access
    Ok(())
}
```

------

## PlantUML Mindmap

Below is the PlantUML representation summarizing these points.

![rust-solana-mindmap]({{site.url_complet}}/assets/article/blockchain/solana/rust-solana.png)

This breakdown should help you grasp these essential concepts and their use cases. The PlantUML diagram offers a structured way to visualize these topics.