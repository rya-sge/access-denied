---
layout: post
title: "Zero-Knowledge Proofs in the Zama Protocol — What They Prove and Where They Are Verified"
date:   2026-07-24
last_modified_at: 2026-07-28
lang: en
locale: en-GB
categories: blockchain cryptography ZKP
tags: zama fhe fhevm zero-knowledge zkpok mpc confidential-smart-contract
description: How the Zama Confidential Blockchain Protocol uses zero-knowledge proofs of knowledge on encrypted inputs, which proof system TFHE-rs relies on, where the proof is verified, and why the calldata inputProof holds signatures rather than the proof.
image: /assets/article/cryptographie/zero-knowledge-proof/zama/zero-knowledge-proofs-zama-protocol.png
isMath: true
---

The Zama Confidential Blockchain Protocol is built on Fully Homomorphic Encryption, yet it also carries zero-knowledge proofs and multi-party computation. Each of the three covers a distinct boundary, and the zero-knowledge part is deliberately confined to one of them: the moment a user hands an encrypted value to the network. This article looks at what that proof asserts, which construction produces it, who verifies it, what it costs, and which parts of the protocol people often mistake for zero-knowledge machinery when they are in fact signature checks.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## The division of labour between FHE, MPC and ZK

The [protocol litepaper](https://docs.zama.org/protocol/zama-protocol-litepaper) states the split in three lines. FHE performs the computation on encrypted data and keeps it publicly verifiable, since anyone can recompute an operation and compare. MPC decentralises the global decryption key, so no single operator can read a ciphertext. Zero-knowledge covers the remaining hole: it "ensures the encrypted inputs provided by users were actually encrypted correctly".

The litepaper adds a sentence about that choice which is worth reading twice: "Using ZK only for this specific purpose makes the ZK proofs lightweight and cheap to generate in a browser or mobile app." Scope was traded against cost. A protocol that proves entire state transitions in zero knowledge pushes heavy proving work onto whoever produces a transaction. Here the statement being proved is small and local, so a phone can produce it.

![Division of cryptographic labour in the Zama Protocol]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/zama/zama-zk-trust-boundaries-concept.png)

## Why an encrypted input needs a proof at all

A confidential contract receives a ciphertext from an address it does not trust. Two failure modes follow, and neither is caught by the encryption itself.

The first is a malformed ciphertext. The FHE schemes behind the protocol come from the learning-with-errors family, where a ciphertext is a pair carrying a small noise term. Writing the LWE form of a ciphertext under a secret key $$s$$:

$$
\begin{aligned}
b = \langle a, s \rangle + \Delta m + e \bmod q
\end{aligned}
$$

the value $$e$$ is the noise, $$\Delta$$ the scaling factor that separates the message $$m$$ from it, and correctness holds only while the noise stays inside its budget. Nothing about the byte string tells a verifier that the noise was drawn honestly or that the encoded message sits in the declared range. A submitter free to fabricate ciphertexts controls a parameter the rest of the protocol assumes is well behaved, and the network eventually decrypts derived results through the KMS. Requiring a proof of correct encryption at the entry point is the standard answer to that exposure.

The second failure mode needs no cryptography to explain. Ciphertexts travel in public calldata. Without a binding between the proof and the party submitting it, anyone could lift another user's encrypted amount out of a past transaction and replay it as their own input. The documentation on [encrypted inputs](https://docs.zama.org/protocol/solidity-guides/smart-contract/inputs) lists exactly this as one of the two purposes of the proof: it verifies "that the user knows the plaintext value of the ciphertext, preventing replay attacks or misuse".

## What the ZKPoK asserts, and what it says nothing about

The object attached to an encrypted input is a Zero-Knowledge Proof of Knowledge, abbreviated ZKPoK across the Zama documentation. Three claims travel with it:

- **Knowledge.** The submitter knows the plaintext behind the ciphertext. A ciphertext copied from someone else fails, because the copier cannot exhibit the witness.
- **Well-formedness.** The ciphertext is a correct encryption under the global FHE public key, with parameters inside the ranges the protocol expects.
- **Binding.** The proof ties the input to the address that submits it and to the contract that will consume it, which is what makes replay into another contract or by another caller useless. The next section shows the exact bytes that carry this binding.

What the proof does not do matters just as much. It states nothing about the user's balance, their entitlement to transfer, or any rule the application cares about. A confidential token still cannot learn whether the sender holds enough funds; that comparison happens homomorphically inside the contract, and in the OpenZeppelin confidential token implementation an amount above the balance results in a transfer of zero rather than a revert, precisely because reverting would leak the comparison. Readers arriving from the world of shielded pools tend to assume the proof carries solvency. It does not.

## One packed proof per transaction

A call may take several encrypted arguments. The SDK does not build one proof per argument. All inputs of a transaction are packed into a single ciphertext in a user-defined order, which the documentation describes as "optimizing the size and generation of the zero-knowledge proof". The Solidity side then receives index-typed handles plus one proof blob:

```solidity
function exampleFunction(
  externalEbool param1,
  externalEuint64 param2,
  externalEuint8 param3,
  bytes calldata inputProof
) public {
  // Function logic here
}
```

`param1`, `param2` and `param3` are handles into the packed proof. Argument order in Solidity is free and need not match the order used client-side when the inputs were assembled. The `inputProof` parameter is not the zero-knowledge proof itself, a point developed two sections below.

## Which proof system is actually used

The proving happens in TFHE-rs, whose [zero-knowledge proof documentation](https://docs.zama.org/tfhe-rs/fhe-computation/advanced-features/zk-pok) names its source: the construction is derived from Benoît Libert's [Vector Commitments With Proofs of Smallness](https://eprint.iacr.org/2023/800). The library ships two variants. ZKV1 follows the paper closely, while ZKV2, selected by default with the standard parameters, departs from it and performs better on both the proving and the verification side.

That lineage matters for a reason that comes back later in this article. Libert's construction builds short range proofs out of vector commitments, counted in a handful of group elements, and its security rests on assumptions in a group rather than on lattices.

Three parameters of the API shape what a client can do with it:

- **The CRS.** Proving and verification both take a `CompactPkeCrs`, a Common Reference String generated in advance and shared between clients and servers. It is reusable across encryptions that share the same parameters. In the Zama Protocol, the KMS is the party that produces it.
- **Where the work lands.** `ZkComputeLoad::Proof` makes proving slower and verification faster; `ZkComputeLoad::Verify` does the opposite. The Relayer SDK calls `build_with_proof_packed` with the `Verify` variant, which keeps proof generation light in a browser and pushes the heavier side onto the coprocessors that verify it.
- **The auxiliary data.** The proof accepts a metadata byte string that ties it to arbitrary external context. This is where the binding comes from, and the SDK fills it with a fixed 92-byte layout: the target contract address, the user address, the ACL contract address, then the chain id.

```javascript
const metaData = new Uint8Array(20 + 20 + 20 + 32);
metaData.set(contractAddressBytes20, 0);
metaData.set(userAddressBytes20, 20);
metaData.set(aclContractAddressBytes20, 40);
metaData.set(chainIdBytes32, metaData.length - 32);

const encrypted = builder.build_with_proof_packed(crs, metaData, ZkComputeLoad.Verify);
```

Packing has a hard ceiling: the SDK rejects a list whose encrypted values exceed 2048 bits in total. A call needing more encrypted material than that has to be split across several proofs, and therefore across several billable verifications.

## The verification path

Verification is layered, and the layer that runs the actual zero-knowledge check is not the host chain.

![Lifecycle of an encrypted input and its ZKPoK]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/zama/zama-encrypted-input-zkpok-workflow.png)

Client-side, the Relayer SDK encrypts under the global FHE public key and produces the proof against a Common Reference String. That CRS is not chosen by the client: the KMS generates it through its MPC protocols, alongside key generation and threshold decryption.

The ciphertext and its proof then reach the Gateway, a dedicated Arbitrum rollup that orchestrates the protocol. Coprocessors verify the ZKPoK, store the ciphertext and return signed handles; the Gateway runs a majority consensus over their answers. Users normally do not talk to the Gateway themselves, since the Relayer forwards the request and pays the Gateway-chain fee on their behalf.

On the host chain, the contract calls `FHE.fromExternal`, which turns an `externalEuintXX` into a usable `euintXX`:

```solidity
euint64 amount = FHE.fromExternal(encryptedAmount, inputProof);
FHE.allowThis(amount);
```

The name of that second argument is misleading, and the `InputVerifier` contract shipped in `@fhevm/host-contracts` says so in its own comments. What the client sends off-chain is a bundle, `compressedPackedCT + ZKPOK`, and the handle is derived from it by hashing. What travels in calldata is a different object: a byte string holding a handle count, a signer count, the list of handles, and the coprocessors' signatures.

The host chain therefore verifies ECDSA signatures against a registered signer set and a threshold, over an EIP-712 structure that carries the binding forward:

```solidity
struct CiphertextVerification {
    bytes32[] ctHandles;
    address userAddress;
    address contractAddress;
    uint256 contractChainId;
    bytes extraData;
}
```

The same triple of user, contract and chain that went into the proof metadata reappears here as signed typed data. A caller who is not `userAddress`, or a contract that is not `contractAddress`, cannot make the attestation check out. There is no partial acceptance: deserialisation failures, an unknown signer, or too few signatures each revert before any FHE operation is scheduled.

Client-side the whole construction sits behind a few calls, here with the Hardhat plugin, the Relayer SDK exposing the same shape. Both the contract address and the user address go in, because the proof is bound to that pair:

```typescript
const encInput = await fhevm
  .createEncryptedInput(contractAddress, userAddress)
  .add64(1000n)
  .encrypt();

await contract['confidentialTransfer(address,bytes32,bytes)'](
  recipient,
  encInput.handles[0],
  encInput.inputProof,
);
```

## What is not a zero-knowledge proof here

Several artefacts in the protocol are called proofs without being zero-knowledge arguments, and conflating them leads to wrong security reasoning.

- **The decryption proof.** After `FHE.makePubliclyDecryptable`, an off-chain client calls `publicDecrypt` and receives the cleartext together with a "decryption proof". That blob holds KMS signatures and metadata. The contract validates it with `FHE.checkSignatures`, which reverts when the signatures do not match the handle and cleartext pair. It is a threshold-signature attestation, not a ZK argument, and it is bound to the exact order of the handles passed in.
- **The `inputProof` argument.** Despite its name, the bytes passed to `FHE.fromExternal` hold handles and coprocessor ECDSA signatures, checked against a threshold in `InputVerifier`. The zero-knowledge proof stays off-chain, inside the bundle the client sent to the Gateway, and the host chain never sees it.
- **The correctness of FHE computation.** No proof accompanies an FHE operation today. Verifiability comes from public recomputation: anyone can replay the operation on the stored ciphertexts and check the result, with a majority consensus across coprocessors deciding what gets committed.

## The price of a proof

Proof verification is one of the three metered operations in the fee model, together with decryption and cross-chain bridging. Homomorphic computation itself is not billed by the protocol. The published range for a ZKPoK verification runs from $0.5$ down to $0.005$, the spread reflecting the difference between pay-as-you-go and a monthly subscription. In the litepaper's worked example of a confidential token transfer, one verification covers the encrypted amount while three decryptions cover the two balances and the transferred value, for a total between $0.008$ and $0.8$ per transfer.

Fees are quoted in USD and settled in the ZAMA token, and the bill can fall on the user, the frontend, or a relayer, so an application can absorb them and keep its users away from token management.

Two engineering consequences follow. Packing every input of a call into a single proof is not only a size optimisation, it also collapses what would otherwise be several billable verifications into one. And a design that pushes users through many small confidential calls pays the verification cost each time, which favours batching at the application level.

## The post-quantum gap sits exactly here

Zama's FHE and MPC components are already resistant to quantum adversaries. The proof system is not. The litepaper is explicit: "Zama's FHE and MPC technologies are already resistant to quantum computers. However, the ZKPoK is not (similar to most ZK-SNARKs). We are working on replacing it with a lattice-based ZK scheme that is post-quantum."

The reason is structural rather than incidental. The FHE and MPC layers stand on lattice problems, whereas the proof system inherits its security from the vector-commitment construction described earlier, whose hardness assumptions live in a group. Swapping it for a lattice-based argument is therefore a change of proof system, not a parameter bump, which is why it appears in the roadmap rather than in a release note.

The gap also has a bounded blast radius. An adversary with a quantum computer could forge a proof of knowledge for a ciphertext they did not create, which breaks the anti-replay property at the input boundary. Confidentiality of the data itself rests on the FHE layer and does not fall with the proof system.

## Where zero-knowledge could expand

The roadmap in the litepaper adds two further uses, both aimed at removing trust assumptions rather than at privacy.

**ZK-MPC.** Every MPC protocol in production assumes an honest majority among the nodes running it. Today the protocol backs that assumption with AWS Nitro Enclaves, which makes verifiability depend on hardware. Adding proofs to the MPC protocols would let anyone check that each KMS node contributed correctly, without the enclave assumption.

**ZK-FHE.** Proving that an FHE computation was performed correctly would replace coprocessor consensus with open competition: anyone could execute operations, provided they publish a proof of the result. The litepaper describes the overhead of ZK on top of FHE as impractical for now, with work in progress.

Neither changes what users prove about their own inputs. Both would shift the protocol's verifiability from consensus and hardware towards cryptography.

## Comparison with zero-knowledge-first designs

Putting the approaches side by side clarifies why the proof is so small here.

| Design | What a proof asserts | Who computes on private data | Composability |
|--------|---------------------|------------------------------|---------------|
| ZK-rollup or shielded pool | Validity of a state transition, including balance and authorisation | The user, locally, before proving | Limited across applications |
| Zama Protocol | Correct encryption and knowledge of the submitted input | Coprocessors, homomorphically, on ciphertexts they cannot read | Encrypted state shared between contracts |

In a shielded-pool design, the user is the one who knows the state and proves that their transition respects the rules. In the Zama Protocol nobody holds the plaintext state, so there is nothing for the user to prove about it; the contract itself computes on ciphertexts, and the access control list decides who may later obtain a cleartext. The proof therefore shrinks to a statement about the input alone.

## Conclusion

Zero-knowledge occupies one boundary in the Zama Protocol: the handover of an encrypted value from a client to the network. The proof asserts knowledge of the plaintext, correct encryption under the global public key, and binding to the caller and target contract. It is verified off-chain by coprocessors, settled by Gateway consensus, and surfaced on the host chain as a set of EIP-712 signatures that `InputVerifier` checks before any ciphertext enters a computation. Everything past that point relies on other primitives: homomorphic evaluation for computation, threshold MPC for decryption, and signatures to carry cleartexts back on-chain.

The construction behind it is a compact public-key-encryption proof from TFHE-rs, derived from Libert's vector commitments with proofs of smallness, run over a packed list of at most 2048 bits and tied to a metadata string holding the contract, the user, the ACL address and the chain id. That choice explains both the cost profile, a proof cheap enough for a browser and priced per input verification, and the current post-quantum gap, since group-based assumptions are the one place where the protocol still departs from lattices. The announced work on lattice-based proofs, ZK-MPC and ZK-FHE would widen the role of zero-knowledge without moving it back to the centre of the design.

![Zero-knowledge proofs in the Zama Protocol]({{site.url_complet}}/assets/article/cryptographie/zero-knowledge-proof/zama/zero-knowledge-proofs-zama-protocol.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **ZKPoK** | Zero-Knowledge Proof of Knowledge attached to an encrypted input, showing the submitter knows the plaintext and encrypted it correctly, without revealing it. |
| **Encrypted input** | A value submitted in ciphertext form by a user, accompanied by a ZKPoK and converted on-chain with `FHE.fromExternal`. |
| **Handle** | A 32-byte pointer to a ciphertext held by the coprocessors; host-chain contracts manipulate handles rather than ciphertext bytes. |
| **CRS** | Common Reference String taken by both the prover and the verifier, reusable across encryptions with identical parameters, generated in the protocol by the KMS through its MPC protocols. |
| **ZKV1 / ZKV2** | The two proof variants in TFHE-rs: ZKV1 follows Libert's paper closely, ZKV2 is the default and improves both proving and verification. |
| **Coprocessor** | Off-chain node that verifies ZKPoKs, performs FHE computations with the evaluation key, stores ciphertexts, and relays ACL events. |
| **Gateway** | Dedicated Arbitrum rollup that orchestrates input verification, decryption requests and cross-chain bridging, and runs consensus over coprocessor answers. |
| **KMS** | Key Management Service, a set of MPC nodes performing key generation, CRS generation and threshold decryption without ever reconstructing the secret key. |
| **Access Control List** | Host-chain contract recording which address may use or decrypt which handle; the authority the KMS consults before decrypting. |
| **Decryption proof** | Byte array of KMS signatures and metadata returned by `publicDecrypt` and checked on-chain by `FHE.checkSignatures`; a threshold-signature attestation rather than a ZK argument. |
| **inputProof** | The calldata argument passed with an external handle: handle count, signer count, handles and coprocessor signatures, and not the zero-knowledge proof itself. |

### Security Implementation Checklist

The items below are the properties an integration has to meet for the input and decryption paths to hold up. They are written as statements an implementation either satisfies or fails.

#### Encrypted inputs and proofs

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Every externally supplied handle is converted with `FHE.fromExternal` before use, never trusted as an already-valid ciphertext. | An unverified handle enters a computation without any proof that its sender knew the plaintext. |
| ☐ | Encrypted inputs are built client-side against the target contract address and the submitting user address. | A proof bound to another pair fails verification, or, if binding is skipped, a captured ciphertext can be replayed by a third party. |
| ☐ | Input proofs are treated as single-use material for one transaction, never cached and resubmitted. | Reused proof material either reverts or, in a permissive integration, admits an input the caller does not own. |
| ☐ | All encrypted arguments of a call are packed into one proof rather than proved separately. | Several verification fees are paid where one would do, and proof size and generation time grow. |
| ☐ | The encrypted values of a single call stay within the packed-list capacity, 2048 bits in the SDK. | Input construction throws client-side, or the call has to be split into several proofs and several paid verifications. |
| ☐ | Contract logic does not infer authorisation from the presence of a valid proof. | The proof says nothing about balances or entitlement; treating it as authorisation grants transfers no rule ever checked. |

#### Access control and disclosure

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | `FHE.allow` grants are given only to parties trusted with the plaintext and with the right to reveal it. | ACL access carries no read-only mode: whoever may decrypt may also re-grant or publicly disclose the value, irreversibly. |
| ☐ | ACL grants are re-issued on the new handle after every operation that rewrites an encrypted value. | Observers silently lose access, or a contract can no longer use its own ciphertext in a later transaction. |
| ☐ | `FHE.makePubliclyDecryptable` is called only on values the application accepts to publish forever. | The grant cannot be undone for that handle, and any ACL holder can trigger it. |
| ☐ | Repeated disclosure of a running aggregate is assessed for leakage before being exposed. | Successive published totals reveal each individual delta by subtraction, even though every operation stayed encrypted. |

#### Decryption results

| Check | Security requirement | Failure mode if violated |
|:---:|------------|------------|
| ☐ | Cleartexts returned from `publicDecrypt` are verified on-chain with `FHE.checkSignatures` before any business logic runs. | A caller submits an arbitrary value claiming it is the decryption of a handle, and the contract acts on it. |
| ☐ | The handle list passed to verification keeps the exact order used when the decryption proof was produced. | Verification fails on a correct decryption, or a mismatched pairing of handle and value is accepted as valid. |
| ☐ | Decryption callbacks implement replay protection. | An old, validly signed result is resubmitted later to re-trigger a state change. |
| ☐ | Contract logic never assumes an FHE operation reverted on an invalid amount. | Arithmetic that saturates or transfers zero instead of reverting leaves the caller believing a failed operation succeeded. |

## Frequently Asked Questions

**Q: What exactly does the ZKPoK attached to an encrypted input prove?**

Three things at once: that the submitter knows the plaintext behind the ciphertext, that the ciphertext is a correct encryption under the global FHE public key, and that the input belongs to a specific pair of user address and contract address. It carries no statement about the application's own rules, so a confidential token learns nothing about the sender's balance from it.

**Q: Why does the Zama Protocol not use zero-knowledge proofs for the computation itself?**

Because FHE computation is already publicly verifiable by recomputation: anyone can replay an operation on the stored ciphertexts and compare results, and coprocessors commit their answers under a majority consensus. Proving FHE execution in zero knowledge is on the roadmap under the name ZK-FHE, with the stated goal of letting anyone compete to execute operations, but the litepaper describes the combined overhead of ZK on top of FHE as impractical today.

**Q: Which proof system produces the ZKPoK?**

The proving code lives in TFHE-rs and is derived from Benoît Libert's *Vector Commitments With Proofs of Smallness* (eprint 2023/800), a vector-commitment construction yielding very short range proofs. Two variants ship: ZKV1, close to the paper, and ZKV2, the default, which trades fidelity to the paper for better performance on both sides. The client builds one packed proof over a list of encrypted values with `build_with_proof_packed`, against a CRS and a metadata string; verification uses `verify_and_expand` with the same CRS and metadata.

**Q: Where is the proof verified, on the host chain or off-chain?**

Off-chain, by the coprocessors, whose answers the Gateway settles under majority consensus. What the host chain sees when `FHE.fromExternal` runs is the resulting attestation, checked through the `InputVerifier` contract. This split keeps the expensive verification away from the L1 while the host chain retains the last word on whether an input may be converted into a usable encrypted value.

**Q: The protocol is described as post-quantum, yet the proofs are not. How do those statements fit together?**

The FHE and MPC layers rest on lattice assumptions and are considered quantum-resistant, whereas the current ZKPoK is not, which the litepaper states plainly while announcing a lattice-based replacement. The two claims cover different properties. Confidentiality of ciphertexts and of the decryption key comes from FHE and MPC and does not depend on the proof system; what a quantum adversary would break is the input-boundary guarantee that the submitter knows the plaintext.

**Q: A decryption returns a "proof". Is that another zero-knowledge argument?**

No. `publicDecrypt` returns the cleartext, its ABI encoding, and a byte array of KMS signatures with metadata. The contract passes it to `FHE.checkSignatures`, which reverts when the signatures do not match the handle and cleartext pair. The guarantee comes from threshold signatures produced by the KMS nodes, not from a zero-knowledge argument, and it is bound to the exact ordering of the handles submitted.

**Q: If the proof says nothing about balances, what stops a user from sending more than they own in a confidential token?**

The check happens homomorphically inside the contract, on ciphertexts, and its outcome stays encrypted. Implementations built on ERC-7984 compute the transferable amount under encryption and move zero when the balance is insufficient, rather than reverting, since a revert would disclose the result of a comparison on private data. Combining this with the previous answers: the ZKPoK guards who may submit an input, the ACL guards who may read a result, and the encrypted arithmetic guards the rule itself.

## References

### Protocol documentation

- [Zama Protocol documentation](https://docs.zama.org/protocol)
- [Zama Confidential Blockchain Protocol Litepaper](https://docs.zama.org/protocol/zama-protocol-litepaper)
- [Encrypted inputs](https://docs.zama.org/protocol/solidity-guides/smart-contract/inputs)
- [Access Control List](https://docs.zama.org/protocol/solidity-guides/smart-contract/acl)
- [Decryption](https://docs.zama.org/protocol/solidity-guides/smart-contract/oracle)
- [Relayer SDK guides](https://docs.zama.org/protocol/relayer-sdk-guides)

### Proof system

- [Zero-knowledge proofs in TFHE-rs](https://docs.zama.org/tfhe-rs/fhe-computation/advanced-features/zk-pok)
- [Benoît Libert — Vector Commitments With Proofs of Smallness: Short Range Proofs and More](https://eprint.iacr.org/2023/800)
- [fhevm host contracts, including InputVerifier](https://github.com/zama-ai/fhevm)

### Libraries and standards

- [TFHE-rs](https://docs.zama.ai/tfhe-rs)
- [OpenZeppelin Confidential Contracts](https://docs.openzeppelin.com/confidential-contracts/erc7984)
- [EIP-1153 — Transient storage opcodes](https://eips.ethereum.org/EIPS/eip-1153)

### Tools

- [Claude Code](https://claude.com/product/claude-code)

### Related articles

- [Overview, security and applications of Multi-Party Computation (MPC)]({{site.url_complet}}/2024/10/21/mpc-protocol-overview/)
- [Technical Analysis of the OpenZeppelin ERC-7984 Implementation]({{site.url_complet}}/2026/02/24/erc7984-openzeppelin-analysis/)
- [Canton Network — Architecture, Privacy Model, and Comparison with Ethereum, Railgun, Zcash, Zama fhEVM, and Besu]({{site.url_complet}}/2026/05/12/canton-network-architecture/)
