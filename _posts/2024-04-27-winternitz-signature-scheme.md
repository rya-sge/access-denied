## Winternitz One-Time Signature (OTS)

This article is mainly a summary of the main points and information that I found about the cryptographic algorithm Winternitz One-Time Signature (W-OST).

W-OST is used for digital signatures that ensures data integrity, authenticity, and non-repudiation. It was introduced by Herbert Winternitz in 1982. See [sphere10.com](https://sphere10.com/articles/cryptography/pqc/wots).

Unlike traditional signature schemes that use a single private key for multiple signatures, Winternitz OTS generates a new private key for each signature, making it highly secure against attacks such as key reuse and forgery. 

However, a private key can only be used only one time reason why they are called One-Time signature. 

The core idea of W-OTS is to iteratively apply a function on a secret input, whereas the number of iterations depends on the message to be signed, see [1. eprint.iacr.org/2011/191.pdf](https://eprint.iacr.org/2011/191.pdf)

W-OTS is considerate as quantum safe, https://medium.com/asecuritysite-when-bob-met-alice/w-otss-the-problem-sleepwalking-into-a-broken-world-of-trust-7a6e027d1d9f

## Schema

Reference: [asecuritysite.com/hashsig/wint](https://asecuritysite.com/hashsig/wint ) 

![wint](C:\Users\super\Documents\HEIG-git\access-denied\assets\article\cryptographie\winternitz\wint.png)



## Summary

The algorithm generates a pair of private/public keys.

**Private key generation**

It generates 32x256-bit random private keys.

We then hash these a number of times, and is defined by a parameter (w)

**Public keys**

If we use w=8, we hash the private keys by (2^w). 

This creates 32x256 bits public keys.

The value 8 for w seems to be a "constant"

**Signature**

The signature is then created by taking eight bits at a time,

1. The 8-bit binary int (n) is subtracted from 256 
2. The private key is the hashed 256-n times. 
3. The signature is then 32 hashes which are derived from random private keys. 

To verify the signature, the recipient parses the hash of the signature (using 8 bits at a time, and extracting the 8 bit int, n). 

The public key is then derived from the signature.

Reference: [asecuritysite.com/hashsig/wint](https://asecuritysite.com/hashsig/wint ) 

## Checksum

The Winternitz signature uses a checksum that’s very similar to the approach used in Merkle’s scheme.

The checksum is the *sum of the differences* between the 255 (the maximum value of a message byte) and each actual message byte being signed. 

The resulting sum is encoded as a base-256 integer and added to the message. 

Both the message and checksum are signed.

For an ![\ell](https://s0.wp.com/latex.php?latex=%5Cell&bg=ffffff&fg=000000&s=0&c=20201002)-byte message, the checksum formula is:
$$
\sum_{l}^{i=1}255 - Mi
$$


Reference: 

- [3. blog.cryptographyengineering.com/winternitz-checksum/](https://blog.cryptographyengineering.com/winternitz-checksum/)
- [4. csrc.nist.gov/csrc/media/Presentations/2022/crclub-2022-10-19a/20221020-crypto-club-kelsey-slides-MD-hash-sigs.pdf](https://csrc.nist.gov/csrc/media/Presentations/2022/crclub-2022-10-19a/20221020-crypto-club-kelsey-slides-MD-hash-sigs.pdf)

## WOTS+

According to [this document](csrc.nist.gov/csrc/media/Presentations/2022/crclub-2022-10-19a/20221020-crypto-club-kelsey-slides-MD-hash-sigs.pdf), WOTS+  is specific variant of Winternitz used in SPHINCS+ for one-time signature.

# Reference

[1. https://eprint.iacr.org/2011/191.pdf](https://eprint.iacr.org/2011/191.pdf)

[2. asecuritysite.com/hashsig/wint](https://asecuritysite.com/hashsig/wint)

[3. Winternitz Checksum](https://blog.cryptographyengineering.com/winternitz-checksum/)

[4. csrc.nist.gov/csrc/media/Presentations/2022/crclub-2022-10-19a/20221020-crypto-club-kelsey-slides-MD-hash-sigs.pdf](https://csrc.nist.gov/csrc/media/Presentations/2022/crclub-2022-10-19a/20221020-crypto-club-kelsey-slides-MD-hash-sigs.pdf)

[5. linkedin.com/posts/billatnapier_the-search-is-on-for-signatures-that-can-activity-7110695731845312512-ozGd/](https://www.linkedin.com/posts/billatnapier_the-search-is-on-for-signatures-that-can-activity-7110695731845312512-ozGd/)

