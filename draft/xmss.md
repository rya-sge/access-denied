### Understanding the XMSS Algorithm: A Guide to Quantum-Resistant Cryptography

------

### What is XMSS?

XMSS (eXtended Merkle Signature Scheme) is a quantum-resistant, stateful hash-based cryptographic algorithm designed to secure digital signatures. It uses **one-time signatures (OTS)**, **Merkle trees**, and cryptographic hash functions to provide secure and efficient post-quantum digital signatures. Unlike number-theoretic algorithms (e.g., RSA, ECC), XMSS relies purely on the hardness of reversing cryptographic hash functions, making it robust against quantum attacks.



XMSS is described in the RFC [8391](https://datatracker.ietf.org/doc/html/rfc8391)



  The eXtended Merkle Signature Scheme (XMSS) [BDH11] is the latest
   stateful hash-based signature scheme.  It has the smallest signatures
   out of such schemes and comes with a multi-tree variant that solves
   the problem of slow key generation.  

### Security

Moreover, it can be shown that XMSS is secure, making only mild assumptions on the underlying hash function.  In particular, it is not required that the cryptographic hash function is **collision-resistant** for the security of XMSS.

In contrast to traditional signature schemes, the signature schemes described in this document are stateful, meaning the secret key changes over time.  If a secret key state is used twice, no cryptographic security guarantees remain.  In consequence, it becomes



Huelsing, et al.              Informational                     [Page 6]

------

RFC 8391                          XMSS                          May 2018

   feasible to forge a signature on a new message.  This is a new
   property that most developers will not be familiar with and requires
   careful handling of secret keys.  Developers should not use the
   schemes described here except in systems that prevent the reuse of
   secret key states.

From the RRDC

------

### How XMSS Works (with Math Formulas)

XMSS can be broken down into three primary components:

1. **One-Time Signatures (OTS)**: XMSS uses a one-time signature scheme like WOTS+ to sign messages. In WOTS+, private keys consist of n-bit strings x1,x2,…,xw, where `w`is the Winternitz parameter. The public key is derived using a hash function `H`:
   $$
   pk_i = H^{(w)}(x_i)
   $$
   

   where `H(w)` denotes iteratively applying the hash `w` times. For signing, each part of the message hash determines how many times to hash each `xi`.

2. **Merkle Tree**: The Merkle tree organizes the public keys of all OTS into a single tree. Each leaf node represents an OTS public key pki, and parent nodes are derived using:
   $$
   T_i = H(T_{2i} || T_{2i+1})
   $$
   

   The root *T*root serves as the master public key. Verification involves recomputing Troot  from the leaf and provided authentication path.

3. **Signing**: For signing, XMSS selects an unused OTS key to sign the message. The signature includes:

   - The OTS signature.
   - An authentication path: intermediate nodes along the Merkle tree to verify TrootT_{root}Troot.

------

### Differences Between XMSS and Winternitz

While XMSS uses WOTS+ as its underlying one-time signature scheme, the two are distinct. 

Winternitz OTS (WOTS) is a standalone signature scheme optimized for single use, focusing solely on the tradeoff between signature size and speed. 

In contrast, XMSS integrates WOTS+ into a larger structure using Merkle trees to enable multiple signatures while maintaining security. 

XMSS also optimizes WOTS+ for tree-based operations, offering better performance for batch verification and scalability in larger systems.

------

### PlantUML Diagram for XMSS Process

Here is a PlantUML diagram representing the XMSS signing and verification process:

```
plantumlCopyEdit@startuml
start
:Generate OTS keys (WOTS+);
:Build Merkle Tree from OTS public keys;
:Publish Merkle root as master public key;

while (New message to sign?) is (yes)
  :Select unused OTS key;
  :Sign message with OTS;
  :Compute authentication path to Merkle root;
  :Output signature (OTS signature + path);
endwhile (no)

:Verifier computes Merkle root from signature;
:Compare computed root with master public key;

if (roots match?) then (yes)
  :Signature verified;
else (no)
  :Signature invalid;
endif
stop
@enduml
```

------

### Advantages of XMSS

- **Quantum Resistance**: Secures digital signatures against quantum attacks by relying on hash function security.
- **Forward Security**: Uses a unique OTS key per message, ensuring one compromised signature doesn't affect others.
- **Compact Design**: Optimizations like WOTS+ reduce storage and computational overhead.

------

### Challenges of XMSS

- **Stateful Operation**: The signer must track used keys, adding complexity.
- **Finite Usage**: Limited number of signatures due to predefined OTS keys.

This structure ensures that XMSS provides robust, quantum-resistant security in a post-quantum cryptographic landscape.

## Use in blockchain

XMSS is used by the QRL as the main signature scheme