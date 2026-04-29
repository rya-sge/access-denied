# Exploring Advanced Locking Scripts in Bitcoin: P2WPKH, P2WSH, and P2TR

Bitcoin’s versatility and security come from its ability to handle different transaction types using its built-in scripting language. 

Over time, Bitcoin has evolved from basic transaction scripts to more sophisticated and efficient mechanisms. 

Among the advanced locking scripts are **P2WPKH (Pay-to-Witness-Public-Key-Hash)**, **P2WSH (Pay-to-Witness-Script-Hash)**, and **P2TR (Pay-to-Taproot)**, which leverage Segregated Witness (SegWit) and Taproot improvements to enhance scalability, security, and privacy. 

This article will delve into these three locking scripts, how they function, and their unique advantages.

------

## Pay-to-Witness-Public-Key-Hash (P2WPKH)

> [BIP 141: Segregated Witness](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki)

### Overview

P2WPKH is the SegWit equivalent of the traditional Pay-to-Public-Key-Hash (P2PKH) script. It locks funds to a hashed public key, requiring the spender to provide the corresponding public key and a valid signature. 

However, unlike P2PKH, P2WPKH gets **unlocked via the [Witness](https://learnmeabitcoin.com/technical/transaction/witness/) field** instead of the [ScriptSig](https://learnmeabitcoin.com/technical/transaction/input/scriptsig/).

The benefit of using P2WPKH over P2PKH is that Witness field data has less [weight](https://learnmeabitcoin.com/technical/transaction/size/#weight) than the ScriptSig field data, so when you come to unlock a P2WPKH you will pay slightly less in transaction [fees](https://learnmeabitcoin.com/technical/transaction/fee/).

### ScriptPubKey Format

#### Lock

The P2WPKH locking script has the following format:

```
OP_0
OP_PUSHBYTES_20  <PubKeyHash>
```

- **OP_0**: Indicates the use of SegWit.
- **<PubKeyHash>**: A 20-byte hash of the recipient’s public key.

#### Unlock

To unlock a P2WPKH, you need to provide a valid signature followed by the original public key in the [witness](https://learnmeabitcoin.com/technical/transaction/witness/) field for the transaction input.

```
<signature><PubKey>
```

**The Witness field is not Script.** It uses [Compact Size](https://learnmeabitcoin.com/technical/general/compact-size/) fields for indicating the number of items, and the size of the signature and public key. This is instead of using data push opcodes (e.g. `OP_PUSHBYTES_33`) as you would do when unlocking a P2PKH.

**Only compressed public keys are accepted in P2WPKH.** So when you create the public key hash for the ScriptPubKey, make sure it's the hash of a *compressed* public key and not an uncompressed public key, otherwise it will be considered non-standard and will not be relayed by nodes (although it's still technically valid and could get [mined](https://learnmeabitcoin.com/technical/mining/) into the [blockchain](https://learnmeabitcoin.com/technical/blockchain/) if you can send it directly to a miner). This is different to P2PKH, where uncompressed public keys *are* allowed.

### How It Works

1. To spend the funds, the unlocking script (witness data) provides:
   - The public key corresponding to the hashed public key in the locking script.
   - A valid ECDSA signature proving ownership of the private key.
2. The witness data is not part of the transaction hash, reducing transaction size and improving malleability resistance.

### Advantages

- **Reduced Transaction Size:** Lower fees and faster processing.
- **Malleability Resistance:** Signature data does not alter the transaction hash.
- **Backward Compatibility:** Works with non-SegWit-aware wallets via wrapped P2SH ???

### References

[learnmebitcoin - P2WPKH](https://learnmeabitcoin.com/technical/script/p2wpkh/)

------

## Pay-to-Witness-Script-Hash (P2WSH)

### Overview

P2WSH is an advanced version of Pay-to-Script-Hash (P2SH) designed for SegWit transactions. It allows users to lock funds with complex conditions encoded in a custom script. The script’s hash is stored in the locking script, and the actual script is revealed only when funds are spent.

### ScriptPubKey Format

The P2WSH locking script has the following format:

```
php


Copy code
OP_0 <ScriptHash>
```

- **OP_0**: Identifies this as a SegWit transaction.
- **<ScriptHash>**: A 32-byte SHA256 hash of the spending script.

### How It Works

1. The locking script contains the hash of a spending script rather than the script itself.
2. To spend the funds, the unlocking script (witness data) must include:
   - The original spending script matching the hash in the locking script.
   - The data required to satisfy the spending script.
3. The node verifies that the provided script matches its hash and evaluates the script to ensure it resolves to `True`.

### Use Cases

- Multi-signature wallets.
- Time-locked contracts.
- Custom conditions requiring complex scripting.

### Advantages

- **Efficient Verification:** The hash is stored instead of the full script, reducing transaction size.
- **Enhanced Privacy:** The spending script is revealed only when funds are spent.
- **Malleability Resistance:** Benefits from SegWit’s improvements.

------

## Pay-to-Taproot (P2TR)

### Overview

P2TR, introduced in Bitcoin’s **Taproot upgrade** (activated in November 2021), represents the most advanced locking script in Bitcoin. It combines SegWit and Schnorr signatures to improve scalability, privacy, and efficiency. P2TR can lock funds either to a single public key or a complex script but allows all spending conditions to appear as a single public key under normal circumstances.

### ScriptPubKey Format

The P2TR locking script has the following format:

```
php


Copy code
OP_1 <TaprootOutputKey>
```

- **OP_1**: Indicates a Taproot transaction.
- **<TaprootOutputKey>**: A 32-byte output key derived from either a single public key or a Merkle root of multiple conditions.

### How It Works

1. Single-Key Spending:
   - Funds are locked to a public key, and spending requires a Schnorr signature.
2. Script-Based Spending:
   - A Merkle tree encodes multiple spending conditions.
   - The Taproot output key commits to the root of this Merkle tree.
   - To spend via a script, the spender reveals only the script path, reducing the amount of data disclosed.

### Use Cases

- Simplified multi-signature wallets.
- Complex contracts with minimal on-chain footprint.
- Privacy-focused transactions.

### Advantages

- **Enhanced Privacy:** All transactions, whether single-key or script-based, appear identical on-chain.
- **Improved Efficiency:** Schnorr signatures allow batch verification, reducing computational overhead.
- **Flexibility:** Supports complex spending conditions without revealing unnecessary details.

------

## Comparing the Locking Scripts

| **Feature**        | **P2WPKH**          | **P2WSH**          | **P2TR**                   |
| ------------------ | ------------------- | ------------------ | -------------------------- |
| **Introduced In**  | SegWit (BIP 141)    | SegWit (BIP 141)   | Taproot (BIP 341/342)      |
| **Privacy**        | Low                 | Moderate           | High                       |
| **Efficiency**     | High                | Moderate           | Very High                  |
| **Use Case**       | Simple transactions | Complex conditions | Flexible, private spending |
| **Signature Type** | ECDSA               | ECDSA              | Schnorr                    |

------

## Conclusion

P2WPKH, P2WSH, and P2TR are three powerful locking scripts that demonstrate Bitcoin’s progression towards greater scalability, flexibility, and privacy. P2WPKH and P2WSH utilize SegWit to reduce transaction size and improve malleability resistance, while P2TR, with its Taproot enhancements, pushes Bitcoin to the forefront of cryptographic innovation. By adopting these advanced mechanisms, Bitcoin users can enjoy lower fees, better privacy, and a more versatile transaction experience, ensuring the network remains robust and future-ready.