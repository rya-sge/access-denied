---
layout: post
title: Winternitz One-Time Signature(OTS)
date:   2024-05-30
lang: en
locale: en-GB
categories: cryptography blockchain
tags: hash signature winternitz sha-256
description: Presentation of Winternitz One-Time Signature (W-OST), a post quantum algorithm which relies on hash function (e.g  SHA-256)
image: /assets/article/cryptographie/signature/winternitz-cover.png
isMath: true
---

Faced with the threat of quantum computers (not yet current), there are many supposedly quantum-resistant cryptographic algorithms.

One of them is the algorithm Winternitz One-Time Signature (W-OST)

Winternitz is considered quantum safe since its security is not based on a difficult problem like the logarithm discrete, but relies on hash function (e.g  SHA-256). In short, it consists of computing each element in a chain by hashing the previous element. 

W-OTS iteratively applies a function on a secret input, the private key, whereas the number of iterations depends on the message to be signed.

Unlike traditional signature schemes that use a single private key for multiple signatures, Winternitz OTS generates a new private key for each signature. Therefore, a private key can only be used one time reason why they are called One-Time signature. 

- I am not totally sure about the source, but it seems It was introduced by [Robert Winternitz](https://www.iacr.org/cryptodb/data/author.php?authorkey=1665) in 1982.
- It is an extension of the Lamport one-time-signature scheme which offers the possibility to decide how many bits will be signed together.
- In short, W-OTS iteratively applies a function on a secret input, the private key, whereas the number of iterations depends on the message to be signed.

Reference:  [1. eprint.iacr.org/2011/191.pdf](https://eprint.iacr.org/2011/191.pdf), [6. sphere10.com](https://sphere10.com/articles/cryptography/pqc/wots), [github.com/ - Winternitz one time signature](https://github.com/sea212/winternitz-one-time-signature)

## Introduction

### General description

- Winternitz are One-time Signatures, meaning that a privite key can only be used to create one signature
- The parameter W, called, defined the number of
- They are slower than Lamport signature, but it uses smaller keys.
- Winternitz works on element of 256 bits, for example a 256-bit hash of a message
  - For example, the 256-bit hash can be produced with SHA-256.
- Winternitz does not sign bit by bit, but sign bytes
- Private key is a set of 32 seeds (sk0).
- Public key is a set of 32 values (pk). This is also the last value computed with the different hash operation.
- Signatures are (32 + checksum) elements.

- Storing all lists makes too large keys → compute them on
  the fly using the hash function.
- Add a checksum since the final secret list is the public key.




### Hash chain

Winternitz is based on the concept of hash chain 

- It consists of computing each element in a chain by hashing the previous element. 

$$
\begin{aligned}
X_i = HASH(X_i−1)
\end{aligned}
$$



- Only need to know starting value–can compute all other
- You can’t go backward in chain because of preimage resistance, a propriety of the hash function used.




## Schema

Reference: [asecuritysite.com/hashsig/wint](https://asecuritysite.com/hashsig/wint ) 

![schema]({{site.url_complet}}/assets/article/cryptographie/signature/winternitz-schema.png)

## Operation

The algorithm generates a pair of private/public keys.

### Private key generation

It generates 32x256-bit random private keys.

We then hash these keys several times, and is defined by a parameter (w)

### Public keys

If we use w=8, we hash the private keys by (2^w). 

This creates 32x256 bits public keys.

The value 8 for w seems to be a "constant"

### Signature

The signature is then created by taking eight bits at a time,

A) The message is hashed using SHA-256. This produces 32x 8-bit values (N0, N1 ... N31)

B) The 8-bit binary int (N) is subtracted from 256 

C) The private key is then hashed 256-N times. 

- Example for the first byte

$$
\begin{aligned}[b]
s[0] =H(sk[0])^{256-N0}
\end{aligned}
$$

D) The signature is composed of 32 hashes derived from our random private key.

To verify the signature:

a) The recipient parses the hash of the signature using 1 byte / 8 bits at a time, and extracting the 8-bit int, N. It the same principle as for step A.

b) Each byte is then hashed, defined by the number of times defined by the message hash value, N. Contrary to B, you take directly N instead of 256-N.

- Example for the first byte


$$
\begin{aligned}[b]
s[0] =H(sk[0])^{256-N0}
\end{aligned}
$$

If N = 4, you have 252
$$
\begin{aligned}[b]
s[0] =H(sk[0])^{252}
\end{aligned}
$$
By applying N on the signature, you get the same number of rounds that are used to generate the public key.

- Example for the first byte

$$
\begin{aligned}[b]
H(H(sk[0])^{252})^{4} = H^{256}(sk[0]) = pk[0]
\end{aligned}
$$
c) Since the public key is the last value computed, the final value get in step b must be the public key. If it is not the case, the signature is invalid.

Reference: [asecuritysite.com/hashsig/wint](https://asecuritysite.com/hashsig/wint ) 



But in this construction, it misses a last very important point: the **checksum**.

## Checksum

The Winternitz signature uses a checksum to protect against signature forgeries.

The checksum ensures that an attacker:

- can not increment any byte of  the message proper without invalidating the checksum
- they can not destroy/modify the checksum in a way that would help them.

The construction of the checksum is very similar to the approach used in Merkle’s scheme.

The checksum is the *sum of the differences* between the 255 (the maximum value of a message byte) and each actual message byte being signed. 

The resulting sum is encoded as a base-256 integer and added to the message. 

Both the message and checksum are signed.

For an ![\ell](https://s0.wp.com/latex.php?latex=%5Cell&bg=ffffff&fg=000000&s=0&c=20201002)-byte message, the checksum formula is:
$$
\sum_{l}^{i=1}255 - Mi
$$



### Details

Since the hash function is publicly known, an attacker can decide to take a message which its byte values are lower than the first message signed to forge a signature for a message m'.

If you take the example of the previous section where N0 = 4. If N0' = 3, the attacker can just perform a supplementary hash operation on the first signature to create a valid signature s\`  for its message m`

Signature for m'
$$
s'[0] =H(sk[0])^{256-N0'} = H(sk[0])^{253}
$$

If we use our first signature **s** in our equation,  where 
$$
s[0] =H(sk[0])^{252}
$$
we have now


$$
s'[0] =H(s)^{1} = H(sk[0])^{253}
$$
Indeed, to pass from 252 (s) hash operation to 253 (s`) , we only have to perform one supplementary hash operation.

The verification process works as usual on our message m\` and the signature s`.


$$
H(H(sk[0])^{253})^{3}) = H^{256}(sk[0]) = pk[0]
$$

Reference: 

- [3. blog.cryptographyengineering.com/winternitz-checksum/](https://blog.cryptographyengineering.com/winternitz-checksum/)
- [4. csrc.nist.gov/csrc/media/Presentations/2022/crclub-2022-10-19a/20221020-crypto-club-kelsey-slides-MD-hash-sigs.pdf](https://csrc.nist.gov/csrc/media/Presentations/2022/crclub-2022-10-19a/20221020-crypto-club-kelsey-slides-MD-hash-sigs.pdf)



## Use

Winternitz was used by the "crypto" project [iota,](https://www.iota.org) a distributed ledger technology using a DAG data structure instead of a blockchain.

Using Winternitz for a crypto project is an audacious choice since each private key can only be used one time to sign one transaction.

Therefore, it requires to generate a new private key for each transaction which is not convenient.

Moreover, in case of an error, for example if a private key is used twice, the security of the account is totally compromised.

They have finally switched in 2021 for ECDSA, which is not quantum safe but offers a better adaptability to the crypto world.

Reference: [lekkertech.net - IOTA IOTAs Multisig Problem](http://blog.lekkertech.net/blog/2018/03/07/iota-signatures/), [domschiener - Private Keys and Addresses](https://domschiener.gitbooks.io/iota-guide/content/chapter1/seeds-private-keys-and-addresses.html), [iota - introduction](https://wiki.iota.org/learn/protocols/introduction/)

## Security

- The seed/private key must be generated in a random way. Otherwise, the algorithm is broken. The donjon CTF has a challenge if you want [an example](https://blog.cryptohack.org/multisignatures-donjon-ctf-writeup).
- A private key generated to make a Winternitz signature  should be only used one time.

If it is not the case, it is possible to forge a new valid signature under the following condition:

You need to have two messages m1 and m2 such that each byte of the h1 of m1 are less than each byte of the hash of m2, we can forge a new signature by computing:
$$
256−n1< 256−n2
$$
$$
\tilde{s_i} = H^{\tilde{n_i}-n_i}(s_i)
$$

The cidectf has a nice challenge on that and you can find a writeup [here](https://sylvainpelissier.gitlab.io/posts/2024-02-04-dicectf-winter/).





## WOTS+

According to [this document](csrc.nist.gov/csrc/media/Presentations/2022/crclub-2022-10-19a/20221020-crypto-club-kelsey-slides-MD-hash-sigs.pdf), WOTS+  is specific variant of Winternitz used in SPHINCS+ for one-time signature.

# Reference

[1. On the Security of the Winternitz One-Time Signature Scheme
Full version - eprint.iacr.org/2011/191.pdf](https://eprint.iacr.org/2011/191.pdf)

[2. asecuritysite.com/hashsig/wint](https://asecuritysite.com/hashsig/wint)

[3. Winternitz Checksum](https://blog.cryptographyengineering.com/winternitz-checksum/)

[4. csrc.nist.gov/csrc/media/Presentations/2022/crclub-2022-10-19a/20221020-crypto-club-kelsey-slides-MD-hash-sigs.pdf](https://csrc.nist.gov/csrc/media/Presentations/2022/crclub-2022-10-19a/20221020-crypto-club-kelsey-slides-MD-hash-sigs.pdf)

[5. linkedin.com/posts/billatnapier_the-search-is-on-for-signatures-that-can-activity-7110695731845312512-ozGd/](https://www.linkedin.com/posts/billatnapier_the-search-is-on-for-signatures-that-can-activity-7110695731845312512-ozGd/)

[6. sphere10.com](https://sphere10.com/articles/cryptography/pqc/wots)

[7.Hash-based Signatures: An illustrated Primer](blog.cryptographyengineering.com/2018/04/07/hash-based-signatures-an-illustrated-primer/)

8.Cryptography course

