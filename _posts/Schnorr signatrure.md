

### Understanding Schnorr Signatures

#### Introduction

Schnorr signatures, named after their inventor Claus-Peter Schnorr, are a type of cryptographic digital signature that is known for its simplicity, efficiency, and strong security properties. They are utilized in various cryptographic protocols and are gaining attention, particularly within the cryptocurrency community, for their potential to enhance security and scalability.

#### How Schnorr Signatures Work

At its core, a Schnorr signature scheme consists of three primary algorithms: key generation, signing, and verification.

1. **Key Generation:**
   - **Private Key (sk):** A random number selected from a large set.
   - **Public Key (pk):** Derived from the private key using a generator point on an elliptic curve or a multiplicative group.
2. **Signing:**
   - To sign a message, a random value (nonce) is generated.
   - This nonce is used to create a commitment.
   - The commitment, public key, and message are hashed together to produce a challenge.
   - The signature is created using the nonce and the private key in combination with the challenge.
3. **Verification:**
   - The verifier checks the validity of the signature by ensuring that the relationship between the commitment, the public key, and the message holds true when recalculated.

#### Detailed Steps

**Key Generation:**

- Choose a large prime number ppp and a generator ggg of a cyclic group of order qqq.
- The private key sksksk is a random integer xxx such that 1≤x≤q−11 \leq x \leq q-11≤x≤q−1.
- The public key pkpkpk is computed as y=gxmod  py = g^x \mod py=gxmodp.

**Signing a Message mmm:**

1. Choose a random nonce kkk such that 1≤k≤q−11 \leq k \leq q-11≤k≤q−1.
2. Compute the commitment R=gkmod  pR = g^k \mod pR=gkmodp.
3. Calculate the challenge e=H(R∣∣m)e = H(R || m)e=H(R∣∣m), where HHH is a cryptographic hash function.
4. Compute the response s=k+e⋅xmod  qs = k + e \cdot x \mod qs=k+e⋅xmodq.
5. The signature is σ=(R,s)\sigma = (R, s)σ=(R,s).

**Verifying a Signature σ=(R,s)\sigma = (R, s)σ=(R,s) for a Message mmm:**

1. Compute the challenge e=H(R∣∣m)e = H(R || m)e=H(R∣∣m).
2. Compute R′=gs⋅y−emod  pR' = g^s \cdot y^{-e} \mod pR′=gs⋅y−emodp.
3. The signature is valid if and only if R′=RR' = RR′=R.

#### Advantages of Schnorr Signatures

1. **Security:**
   - Schnorr signatures are provably secure under the assumption that the discrete logarithm problem is hard.
2. **Efficiency:**
   - The signatures are shorter and the operations required for signing and verification are faster compared to other schemes like ECDSA.
3. **Provable Security:**
   - The security proofs for Schnorr signatures are straightforward, providing a high level of confidence in their security.
4. **Non-malleability:**
   - Unlike ECDSA, Schnorr signatures are inherently non-malleable, meaning it is difficult for an attacker to modify a valid signature to create another valid signature for the same message.
5. **Linear Aggregation:**
   - Multiple Schnorr signatures can be combined into a single aggregate signature, which is very beneficial for applications like blockchain to improve efficiency and reduce storage requirements.

#### Use Cases of Schnorr Signatures

1. **Cryptocurrencies:**
   - **Bitcoin:** Schnorr signatures are proposed to replace ECDSA in Bitcoin to enhance scalability and security. By aggregating multiple signatures into one, they can significantly reduce the size of transactions and blocks.
2. **Digital Identity:**
   - Schnorr signatures can be used in digital identity systems to sign and verify identities securely and efficiently.
3. **Multisignature Schemes:**
   - In applications where multiple parties must sign a document (e.g., joint bank accounts, corporate agreements), Schnorr signatures can simplify the process by allowing for aggregated signatures.
4. **Blockchain and Smart Contracts:**
   - Smart contracts can benefit from the efficiency and security of Schnorr signatures, particularly in scenarios requiring multiple validations or approvals.

#### Conclusion

Schnorr signatures offer a powerful alternative to traditional digital signature schemes with their strong security properties, efficiency, and versatility. As the digital world continues to expand, the adoption of Schnorr signatures is likely to grow, providing robust solutions for secure communications, blockchain technologies, and beyond. Their ability to streamline operations and enhance security makes them a promising tool in the cryptographic arsenal.

## Schnorr signatrure

On Ristretto, a private key is simply a scalar integer value between 0 and ~2256. That’s roughly how many atoms there are in the universe, so we have a big sandbox to play in.

We have a special point on the Ristretto curve called *G*, which acts as the “origin”. A public key is calculated by adding *G* on the curve to itself, �� times. This is the definition of multiplication by a scalar, and is written as:
$$
P_a = k_aG
$$

## Generate signature

1. Generate a secret once-off number (called a *nonce*), 
2. Calculate the public version of the nonce, R from r (where R=r.G).
3. Send the following to Bob, your recipient - your message (m), R, and your public key (P = k.G).
4. The actual signature is created by hashing the combination of all the public information above to create a *challenge*, e:

$$
e = H(R||P||m)
$$



The hashing function is chosen so that *e* has the same range as your private keys. In our case, we want something that returns a 256-bit number, so SHA256 is a good choice.

Now the signature is constructed using your private information:
$$
s = r + ke
$$
Bob can now also calculate e, since he already knows m,R,P. But he doesn’t know your private key, or nonce

## Verify the signature

$$
sG = (r + ke)G
$$


$$
sG = rG +(kG) e
$$
We have R = rg and P = kg , we can therefore subsiste and we have
$$
sG = R + Pe
$$


## Use case in blockchain

### Bitcoin

Schnorr signature is available in Bitcoin

[https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki)

### Chainlink oracle

 There’s a [public implementation](https://github.com/HarryR/solcrypto/blob/master/contracts/Schnorr.sol) which takes about 85k gas, by using the Ethereum [precompiled contracts for the pairing curve AltBN-128](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-196.md).

Schnorr signature is used by Chainlink to aggregate and verify a report sent by an oracle.

As we can see in https://github.com/smartcontractkit/chainlink/blob/62d31d0a6ea724e7ac00d5860d60cc93d88a3f35/core/services/signatures/secp256k1/point.go#L318

https://github.com/smartcontractkit/chainlink/blob/62d31d0a6ea724e7ac00d5860d60cc93d88a3f35/core/services/keystore/keys/vrfkey/proof.go#L38

go.dedis.ch/kyber/v3

https://chain.link/education-hub/schnorr-signature

https://blog.chain.link/threshold-signatures-in-chainlink/#cheaponchainverificationofschnorrsignatures

### Polkadot

Polkadot uses Schnorrkel/Ristretto x25519 ("sr25519") as its key derivation and signing algorithm.

Sr25519 is based on the same underlying [Curve25519](https://en.wikipedia.org/wiki/Curve25519) as its EdDSA counterpart, [Ed25519](https://en.wikipedia.org/wiki/EdDSA#Ed25519). However, it uses Schnorr signatures instead of the EdDSA scheme. Schnorr signatures bring some noticeable benefits over the ECDSA/EdDSA schemes. For one, it is more efficient and still retains the same feature set and security assumptions. They choose to use Schnore signature for the following reasins

- native multisignature through [signature aggregation](https://bitcoincore.org/en/2017/03/23/schnorr-signature-aggregation/).
- A slightly faster signature scheme with far simpler batch verification than [ECDSA batch verification](http://cse.iitkgp.ac.in/~abhij/publications/ECDSA-SP-ACNS2014.pdf)
- More natural threshold and multi-signatures, as well as tricks used by payment channels. 
- The presence of this public key data may improve locality in block verification, possibly openning up larger optimisations.

The names Schnorrkel and Ristretto come from the two Rust libraries that implement this scheme, the [Schnorrkel](https://github.com/w3f/schnorrkel) library for Schnorr signatures and the [Ristretto](https://ristretto.group/ristretto.html) library that makes it possible to use cofactor-8 curves like Curve25519.

References

https://wiki.polkadot.network/docs/learn-cryptography

https://research.web3.foundation/Polkadot/security/keys/accounts-more

https://lib.rs/crates/schnorrkel

## Schnorr signatreu

As for ECdsa, the security of schnorr signature is based on the difficulty to resolve the discrete Log Problem.

https://tlu.tarilabs.com/cryptography/introduction-schnorr-signatures