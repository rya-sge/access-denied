---
layout: post
title: Pedersen Hash Function Overview
date:   2024-05-07
lang: en
locale: en-GB
categories: cryptography blockchain
tags: hash Petersen starkware
description:  Presentation of the hash function Pedersen, which is efficient for zero-knowledge circuits / zk-SNARK
image: /assets/article/cryptographie/pedersen-hash-function.png
isMath: true
---

A hash operation in a zero-knowledge context (e.g zk-SNARK circuit) requires specific construction to be efficient.

For example, the widely used SHA-256 consists mostly of boolean operations which is not efficient to evaluate inside of a ZK circuit. Each invocation of SHA256 currently adds tens of thousands of multiplication gates, which is clearly not optimized.

One of the hash function designed to be used in a zero-knowledge context is the **Pedersen Hash function**. This function is more efficient in a ZK circuit since it relies on [elliptic curve cryptography](https://en.wikipedia.org/wiki/Elliptic-curve_cryptography). 

Its security is based on the **Elliptic Curve Discrete Logarithm Problem** (ECDLP), which makes the function `one-way` since solving the ECDLP  is considered as computationally infeasible.

Hoe does it work ? In short, Pedersen maps a sequence of bits to a compressed point on an elliptic curve and generally returns the x-coordinate of the computed point as a hash.

This function is available on Starkware, ZCash and the protocol Iden3.

Reference: [book.cairo-lang.org/ch11-05-hash.html](https://book.cairo-lang.org/ch11-05-hash.html), [What is the elliptic curve discrete logarithm problem (ECDLP) and why is it difficult to solve?](https://eitca.org/cybersecurity/eitc-is-acc-advanced-classical-cryptography/elliptic-curve-cryptography/introduction-to-elliptic-curves/examination-review-introduction-to-elliptic-curves/what-is-the-elliptic-curve-discrete-logarithm-problem-ecdlp-and-why-is-it-difficult-to-solve/)



## Use case

The **Pedersen hash** is computed as a linear combination of points on an elliptic curve.  Since the computation relies on arithmetic field, they are therefore fairly efficient to compute in zero-knowledge circuits, e.g zk-SNARK proofs  and Merkle Tree.

For example, SHA256 consists mostly of boolean operations, so it is not efficient to evaluate inside of a zk-SNARK circuit, which is an arithmetic circuit over a large prime field. Each invocation of SHA256 currently adds tens of thousands of multiplication gates, making it the primary cost during proving.

Reference: 

- [iden3 - Pedersen Hash](https://github.com/iden3/iden3-docs/blob/master/source/iden3_repos/research/publications/zkproof-standards-workshop-2/pedersen-hash/pedersen.rst)
- [research.nccgroup.com - Breaking Pedersen Hashes in Practice](https://research.nccgroup.com/2023/03/22/breaking-pedersen-hashes-in-practice/)[https://bitzecbzc.github.io/technology/jubjub/index.html](https://bitzecbzc.github.io/technology/jubjub/index.html)

### Pedersen commitment

It important to not confuse the Pederson hash function with the Pedersen commitment.

The pederson commitment adds a  random blinding factor *r*, multiply by a public point on the curve *H*.

Pedersen commitments are cryptographic algorithms that allow a prover to commit to a certain value without revealing it or being able to change it.

The commitment and hash version rely both on the ECDLP hardness assumption.

- [Mina book - Commitments](https://o1-labs.github.io/proof-systems/fundamentals/zkbook_commitment.html)
- [RareSkills - What are Pedersen Commitments and How They Work](https://www.rareskills.io/post/pedersen-commitment)

## Operation

The Pedersen hash is defined as the linear combination of the points with the encoding of the message chunks:
$$
\begin{aligned}[b]
H(M) = H(M1M2 … Mk ) = ⟨M1⟩ ⋅ G1 + ⟨M2⟩ ⋅ G2 + … + ⟨Mk⟩ ⋅ Gk\\
\end{aligned}
$$
**Message**

- M is the message  that we wish to hash, represented as a bit string of *fixed* length **k ⋅ r**
- We split this message *M* into *k* chunks of *r* bits each: *M = M1M2 … Mk*. 

**Generators**

- **G1, G2, …, Gk* are generators of the prime-order subgroup of our chosen elliptic curve group.
- These generators must be sampled uniformly at random, such that no relationship between them is known.

 **Encoding function**

The function ⟨⋅⟩, commonly referred to as the *encoding* function, converts a bit string into a scalar element. This function has to be injective in order to be collision-resistant.

**Output**

The output of the hash function defined above is a point on the curve. 

In practice, the desired output may be a field element, in which case *a single coordinate* (X) of the resulting point is often used as the hash. 



Reference:  [research.nccgroup.com - Breaking Pedersen Hashes in Practice](https://research.nccgroup.com/2023/03/22/breaking-pedersen-hashes-in-practice/)

## Implementation

### Product

#### ZCash (2018)

The Pedersen hash function has been integrated in ZCash's in 2018 through the network upgrade, Sapling.

In their implementation, they use the `Jubjub` elliptic curve utilizing 3-bit lookup tables.

This is a bit different that the traditional implementation of the Pedersen hash function on the Baby-Jubjub elliptic curve which use 4-bit windows.

According to their documentation, this solution with 3-bit has less constraints, thus enhancing computational efficiency.

Reference:

- [linkedin.com/pulse/4-bit-window-pedersen-hash-function-efficient-standard-paul-socarde/](https://www.linkedin.com/pulse/4-bit-window-pedersen-hash-function-efficient-standard-paul-socarde/)
- [github.com/zcash/zcash/issues/2234](https://github.com/zcash/zcash/issues/2234)
- [zips.z.cash/protocol/protocol.pdf](https://zips.z.cash/protocol/protocol.pdf), p.77

#### StarkWare

StarkWare has implemented a version of this function for StarkNet in C++, [released in 2021](https://twitter.com/StarkWareLtd/status/1361295729793372168?lang=en)
$$
\begin{aligned}[b]
H(a,b)=[P0+a_{low}⋅P1+a_{high}⋅P2+b_{low}⋅P3+b_{high}⋅P4]x \\
\end{aligned}
$$
Where:

- a*low*  is the 248 low bits of a.

- a*high* is the 4 high bits of a(and similarly for b).

- [P]x denotes the x-coordinate of an elliptic-curve point P.

- P0,P1,P2,P3,P4 are constant points on the elliptic curve, derived from the decimal digits of π.


The shift point P0 was added for technical reasons to make sure the point at infinity on the elliptic curve does not appear during the computation.

According to the [Cairo documentation](https://book.cairo-lang.org/ch11-05-hash.html), Pedersen was the first hash function used on StarkNet, and is still used to compute the addresses of variables in storage, for example, `LegacyMap` uses Pedersen to hash the keys of a storage mapping on StarkNet.

Reference: [doc](https://docs.starkware.co/starkex/crypto/pedersen-hash-function.html), [pedersen-hash.cc](https://github.com/starkware-libs/crypto-cpp/blob/master/src/starkware/crypto/pedersen_hash.cc)

#### Iden3

The Blockchain-based identity management solution, `iden3`, which uses zkSNARKs, has also made an implementation of this function in `circom` .

Their implementation uses the Baby-Jubjub elliptic curve and 4-bit  windows, which requires less constraints per bit than using 3-bit  windows used by ZCash.

The generators *P*0, …, *P**k* are generated in such a manner that it is difficult to find a connection between any of these points. To obtain that, they decide to take `D = "string\_seed"` followed by a byte `S` holding that smallest number that `H = Keccak256(D || S)` results in a point in the elliptic curve *E*. This method to compute the points is different than Starkware which derived them from the decimal digits of π.

Reference: 

- [github.com/iden3/iden3-docs/blob/master/source/iden3_repos/research/publications/zkproof-standards-workshop-2/pedersen-hash/pedersen.rst](https://github.com/iden3/iden3-docs/blob/master/source/iden3_repos/research/publications/zkproof-standards-workshop-2/pedersen-hash/pedersen.rst)
- [github.com/iden3/circomlib/tree/master/circuits](https://github.com/iden3/circomlib/tree/master/circuits)
- [github.com/iden3/circomlib/blob/master/circuits/pedersen.circom](https://github.com/iden3/circomlib/blob/master/circuits/pedersen.circom)

### Language

#### Cairo

According to the Cairo documentation, the hash function `Poseidon` is cheaper and faster than Pedersen when working with STARK proofs system and it recommends to use Poseidon in Cairo programs.

```rust
fn main() -> (felt252, felt252) {
    let struct_to_hash = StructForHash { first: 0, second: 1, third: (1, 2), last: false };

    // hash1 is the result of hashing a struct with a base state of 0
    let hash1 = PedersenTrait::new(0).update_with(struct_to_hash).finalize();

    let mut serialized_struct: Array<felt252> = ArrayTrait::new();
    Serde::serialize(@struct_to_hash, ref serialized_struct);
    let first_element = serialized_struct.pop_front().unwrap();
    let mut state = PedersenTrait::new(first_element);

    while let Option::Some(value) = serialized_struct.pop_front() {
        state = state.update(value);
    };

    // hash2 is the result of hashing only the fields of the struct
    let hash2 = state.finalize();

    (hash1, hash2)
}
```



Reference: [book.cairo-lang.org/ch11-05-hash.html](https://book.cairo-lang.org/ch11-05-hash.html)

#### Rust

##### starknet-rs

This library offers a complete Starknet library in Rust, which also contains a version for the pedersen hash in rust.

- Curve parameter

This first part defines the different constants (P1, P2, P3, P4).

Reference: [github.com/xJonathanLEI/starknet-rs/blob/master/starknet-curve/src/curve_params.rs](https://github.com/xJonathanLEI/starknet-rs/blob/master/starknet-curve/src/curve_params.rs)

```rust
pub const PEDERSEN_P1: AffinePoint = AffinePoint {
    x: FieldElement::from_mont([
        16491878934996302286,
        12382025591154462459,
        10043949394709899044,
        253000153565733272,
    ]),
    y: FieldElement::from_mont([
        13950428914333633429,
        2545498000137298346,
        5191292837124484988,
        285630633187035523,
    ]),
    infinity: false,
};
pub const PEDERSEN_P2: AffinePoint = AffinePoint {
    x: FieldElement::from_mont([
        1203723169299412240,
        18195981508842736832,
        12916675983929588442,
        338510149841406402,
    ]),
    y: FieldElement::from_mont([
        12352616181161700245,
        11743524503750604092,
        11088962269971685343,
        161068411212710156,
    ]),
    infinity: false,
};
pub const PEDERSEN_P3: AffinePoint = AffinePoint {
    x: FieldElement::from_mont([
        1145636535101238356,
        10664803185694787051,
        299781701614706065,
        425493972656615276,
    ]),
    y: FieldElement::from_mont([
        8187986478389849302,
        4428713245976508844,
        6033691581221864148,
        345457391846365716,
    ]),
    infinity: false,
};
```



- Function

```rust
pub fn pedersen_hash(x: &FieldElement, y: &FieldElement) -> FieldElement {
    let x = x.to_bits_le();
    let y = y.to_bits_le();

    // Preprocessed material is lookup-tables for each chunk of bits
    let table_size = (1 << CURVE_CONSTS_BITS) - 1;
    let add_points = |acc: &mut ProjectivePoint, bits: &[bool], prep: &[AffinePoint]| {
        bits.chunks(CURVE_CONSTS_BITS)
            .enumerate()
            .for_each(|(i, v)| {
                let offset = v
                    .iter()
                    .rev()
                    .fold(0, |acc, &bit| (acc << 1) + bit as usize);

                if offset > 0 {
                    // Table lookup at 'offset-1' in table for chunk 'i'
                    *acc += &prep[i * table_size + offset - 1];
                }
            });
    };

    // Compute hash
    let mut acc = SHIFT_POINT;
    add_points(&mut acc, &x[..248], &CURVE_CONSTS_P0); // Add a_low * P1
    add_points(&mut acc, &x[248..252], &CURVE_CONSTS_P1); // Add a_high * P2
    add_points(&mut acc, &y[..248], &CURVE_CONSTS_P2); // Add b_low * P3
    add_points(&mut acc, &y[248..252], &CURVE_CONSTS_P3); // Add b_high * P4

    // Return x-coordinate
    AffinePoint::from(&acc).x
}
```

Reference: [github.com/xJonathanLEI/starknet-rs/blob/master/starknet-crypto/src/pedersen_hash.rs](https://github.com/xJonathanLEI/starknet-rs/blob/master/starknet-crypto/src/pedersen_hash.rs)

##### Node Pathfinder

This project is a [Starknet](https://www.starknet.io) full node giving to give view into Starknet. A version of pedersen is also available in rust.

In the code, we can see that four constants are used: P1, P2, P3 and P4. Since the coe follows the [Starkware](https://docs.starkware.co/starkex/crypto/pedersen-hash-function.html) implementation,  we can suppose they are the points on the elliptic curve, derived from the decimal digits of *π*.

```rust
pub fn pedersen_hash(a: StarkHash, b: StarkHash) -> StarkHash {
    let mut result = PEDERSEN_P0.clone();
    let a = FieldElement::from(a).into_bits();
    let b = FieldElement::from(b).into_bits();

    // Add a_low * P1
    let tmp = PEDERSEN_P1.multiply(&a[..248]);
    result = result.add(&tmp);

    // Add a_high * P2
    let tmp = PEDERSEN_P2.multiply(&a[248..252]);
    result = result.add(&tmp);

    // Add b_low * P3
    let tmp = PEDERSEN_P3.multiply(&b[..248]);
    result = result.add(&tmp);

    // Add b_high * P4
    let tmp = PEDERSEN_P4.multiply(&b[248..252]);
    result = result.add(&tmp);

    // Return x-coordinate
    StarkHash::from(result.x)
}
```

- Reference: [github.com/eqlabs/pathfinder/blob/b091cb889e624897dbb0cbec3c1df9a9e411eb1e/crates/pedersen/src/lib.rs#L87](https://github.com/eqlabs/pathfinder/blob/b091cb889e624897dbb0cbec3c1df9a9e411eb1e/crates/pedersen/src/lib.rs#L87)



## Elliptic curve choice

**Jubjub elliptic curve (Zcash)**

Jubjub is a twisted Edwards curve of the form
$$
\begin{aligned}[b]
-x^2 + y^2 = 1 + d x^2 y^2
\end{aligned}
$$
It is built over the BLS12-381 scalar field, with:
$$
\begin{aligned}[b]
d = -(10240/10241)
\end{aligned}
$$
Reference: [bitzecbzc.github.io/technology/jubjub/index.html](https://bitzecbzc.github.io/technology/jubjub/index.html)

**Baby-Jubjub elliptic curve (iden3)**

Iden3 uses the baby-jubjub curve, under the Montgomery Form .
$$
E : v
2 = u
3 + 168698u
2 + u.
$$
This is birationally equivalent to the Edwards elliptic curve where d = `9706598848417545097372247223557719406784115219466060233080913168975159366771`.

See [4-bit Window Pedersen Hash On The Baby Jubjub Elliptic Curve](https://iden3-docs.readthedocs.io/en/latest/_downloads/4b929e0f96aef77b75bb5cfc0f832151/Pedersen-Hash.pdf), [Baby Jubjub Elliptic Curve](https://docs.iden3.io/publications/pdfs/Baby-Jubjub.pdf)

## Security

This section came mainly from the article [Breaking Pedersen Hashes in Practice](https://research.nccgroup.com/2023/03/22/breaking-pedersen-hashes-in-practice/) from nccgroup.

### Collision with variable-length inputs

The hash function is not collision-resistant for variable-length inputs. For example, if we allow larger bit strings to be hashed, such that their encoding is larger than the subgroup order, it come possible to compute collisions.

**Reminder:*

- The order of an elliptic curve is defined as the number of distinct points on an elliptic curve *E* including the point at infinity ∞.
- When you perform multiplication (P + P + P....+P), you will finish by get all the points on the curve and you reach the point at infinity ∞ (0). 
- The scalar factor requires to reach this point-at-infinity is the subgroup order and is called *r* in our example. We have the following equation where 0 is the point at infinity.

**Example**
$$
A)~r ⋅ G = 0
$$

As a result, if the take a point G multiply by scalar *a*
$$
B)~ G * a
$$
This operation produces the same result as multiplying *G* by *a + k ⋅ r*, for any value of *k*
$$
C) ~ G * a = G * a + k * r
$$
With the equation A, we have
$$
(a + k ⋅ r) ⋅ G = a ⋅ G + k ⋅ r ⋅ G = a ⋅ G + k ⋅ 0 = a ⋅ G
$$
Thus, multiplying the point *G* by a scalar *a* produces the same result as multiplying *G* by *a + k ⋅ r*, for any value of *k*. This situation happens if the encoding is larger than the subgroup order *r*.

### Weierstrass curve

If the function returns only the x-coordinate, it can lead of collision if a Weierstrass curve is used because we have two points which have the same coordinate x.  An example of this kind of curve is the curve secp256k1 used in Ethereum and Bitcoin, which is symmetric on the X-axis.

 The second point being the inverse:
$$
P = (x, y)\\-P = (x, -y)
$$


But with the twisted Edwards form, the inverse has a different coordinate X.
$$
−P=(−x,y)
$$
Thus, for implementation using *Jubjub*, a twisted Edwards curve, you can return only the X coordinate. 

Reference:

- [Is it possible to get the negative point with −x in that version of the Pedersen hash over the BaybyJubJub curve?](https://crypto.stackexchange.com/questions/107320/is-it-possible-to-get-the-negative-point-with-−x-in-that-version-of-the-pedersen)
- [Twisted Edwards Elliptic Curves for Zero-Knowledge Circuits](https://upcommons.upc.edu/bitstream/handle/2117/361741/mathematics-09-03022.pdf?sequence=1), page 7

###  Pseudorandom function (PRF) 

As with other hash functions, this function can not be used as a pseudorandom function (PRF) since the hash produced is predicable and not random.



### Reference 

- [research.nccgroup - Breaking Pedersen Hashes in Practice](https://research.nccgroup.com/2023/03/22/breaking-pedersen-hashes-in-practice/)
- [pedersen sage](https://github.com/ncc-pbottine/ToyPedersenHash/blob/main/pedersen.sage)
- [crypto.stackexchange - Pedersen  Hash : when truncating the hash to keep only the X coordinate, is it  possible to compute a collision when the Babyjubjub curve is used?](https://crypto.stackexchange.com/questions/107032/pedersen-hash-when-truncating-the-hash-to-keep-only-the-x-coordinate-is-it-po)

## References

This section contains the main references

- [research.nccgroup.com - Breaking Pedersen Hashes in Practice](https://research.nccgroup.com/2023/03/22/breaking-pedersen-hashes-in-practice/)
- [iden3 - Pedersen Hash](https://github.com/iden3/iden3-docs/blob/master/source/iden3_repos/research/publications/zkproof-standards-workshop-2/pedersen-hash/pedersen.rst)
- [zips.z.cash/protocol/protocol.pdf](https://zips.z.cash/protocol/protocol.pdf), p.77
- [StarkWare doc](https://docs.starkware.co/starkex/crypto/pedersen-hash-function.html)

