erefore allowing transactions with any s value with 0 < s <  n, opens a transaction malleability concern. This is not a serious  security flaw, especially since Ethereum uses addresses and not  transaction hashes as the input to an ether value transfer or other  transaction, but all Ethereum nodes, including Besu, will only allow  signatures where s <= n/2 . This makes sure that only one of the two  possible valid signatures will be accepted. As any ECDSA library, that  is not focused on Blockchains (e.g. libcrypto from OpenSSL), will not  take this constraint into consideration, any created signature has to be normalized after the creation of the signature to fit the above  mentioned criteria.





- The **ECDSA signing** algorithm works by:

1. Calculating the message **hash**, using a cryptographic hash function e.g. SHA-256

```
h = hash(msg)
```

1. Generating securely a **random** number ***k\***
2. Calculating the random point `R = k * G` and take its x-coordinate: `r = R.x`
3. Calculating the signature proof `s` using the formula:

```
s = k^-1 * (h + p * r) mod n
```

where `p` is the signer’s private key, and the order `n`

1. Return the signature (r, s).



You can compute `-s` with

```
s = k^-1 * (h + p * r) mod n
```



1. Calculate a hash (`e`) from the message to sign.
2. Generate a secure random value for `k`.
3. Calculate point `(x₁, y₁)` on the elliptic curve by multiplying `k` with the `G` constant of the elliptic curve.
4. Calculate `r = x₁ mod n`. If `r` equals zero, go back to step 2.
5. Calculate `s = k⁻¹(e + rdₐ) mod n`. If `s` equals zero, go back to step 2.



 

1. Calculating the message **hash**, using a cryptographic hash function e.g. SHA-256

```
h = hash(msg)
```

1. Generating securely a **random** number ***k\***
2. Calculating the random point `R = k * G` and take its x-coordinate: `r = R.x`
3. Calculating the signature proof `s` using the formula:

$$
s = k^-1 * (h + p * r) mod n
$$



the signature verification algorithm, we are given a signature `(r, s)`, a message `m` and a public key `Q`. We compute a point `X = (x1, y1)` and accept the signature if `x1 == r mod n`.

This verification returns also true for `-X = (x1, -y1)` since it has the same x-coordinate.

The point R is compuded as:

`kG`, modulo *n.*



```
X = (eG + rQ) / s mod n. 
```

where

`Q` is the public key

`R` is the random point chosen during signing. 

`e` is the hash of the message

The inverse can be computed as:

```
-R = (eG + rQ) / -s mod n
```



that `r` is the x-coordinate of a random curve point, `kG`, modulo *n.*







Ethereum uses the exact same elliptic curve, called secp256k1

 mod 