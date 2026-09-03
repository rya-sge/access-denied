---
layout: post
title: "Merkle Patricia Forestry on Cardano — How It Differs From Other Merkle Trees"
date:   2026-08-28
lang: en
locale: en-GB
categories: blockchain
tags: cardano aiken merkle-tree hash eutxo data-structure
description: Merkle Patricia Forestry stores a branch's 16 children as a small Merkle tree, so a Cardano proof carries 4 hashes per level instead of 15.
image: /assets/article/blockchain/cardano/merkle-patricia-forestry-cardano.png
isMath: true
---

A name service on Cardano has to settle one question inside a validator: does this name map to this address? An account-based chain answers it in a single opcode, because the contract reads its own storage. Cardano has no such opcode. A validator is handed the datum attached to the UTXO it is spending, the redeemer the spender supplied, and the script context describing the transaction, and it is handed nothing else. There is no `SLOAD`, and no way to reach state the transaction did not bring with it.

That constraint applies to every application built on a large key/value store, whether it holds a registry of names, a delegator table or an oracled dataset. The store cannot sit anywhere the validator can read it. It has to be compressed into something small enough to travel in a datum, and every claim about it has to be provable from the bytes the spender carried in.

Merkle Patricia Forestry (MPF) is the answer that the Aiken ecosystem settled on. The datum holds a 32-byte root hash. The redeemer holds a proof under a kilobyte. From those two values a validator can verify that a key maps to a value, that a key is absent, or that a given insertion or deletion transforms one root into another. The library ships as a pair: an [Aiken](https://aiken-lang.org) package that only ever verifies, and a Node.js package that actually stores the data and produces the proofs.

The name describes the construction. It is a Patricia trie, in the sense of a radix-16 prefix tree with path compression, and its branch nodes are themselves tiny Merkle trees. That second layer of hashing is what separates MPF from Ethereum's Modified Merkle Patricia Trie it borrows from, and from the binary Merkle trees and sparse Merkle trees it tends to get lumped in with. This article works through the structure as the library actually implements it, and sets it against those three neighbours.

> This article has been made with the help of [Claude Code](https://claude.com/product/claude-code) and several custom skills

[TOC]

## Why the eUTXO model asks for a different structure

On an account-based chain, an authenticated map is usually a convenience. Ethereum contracts do not walk a Merkle Patricia Trie to read storage; the node does that for them, and contracts call `SLOAD`. Trie proofs surface at the boundaries, in light clients and cross-chain bridges verifying against a block header.

On Cardano the situation inverts. The validator sees the transaction and nothing else, so the only way to make a statement about a large dataset is to carry the evidence in the transaction. Three budgets bound how large that evidence can be:

- **Transaction size.** The mainnet maximum transaction size is 16 384 bytes, and everything competes for it: inputs, outputs, datums, redeemers, witnesses. A proof is not the only passenger.
- **Execution units.** A transaction's script budget is capped in both memory and CPU steps. The library's own benchmark table notes that 140K memory units and 100M CPU units are each 1% of the respective maximum, which puts the ceilings at roughly 14M memory units and 10G CPU steps.
- **Script size.** Every byte of compiled UPLC either sits in the transaction or in a reference script. Including MPF as a dependency adds about 2.5 KB of generated UPLC.

Two consequences follow, and the library is built around both. First, the structure never exists on-chain: only a root hash crosses the boundary, and the on-chain package deliberately ships no primitive for constructing a trie, not even for debugging. Second, proof bytes are the resource worth optimising, because CPU and memory turn out to be the slack constraints. That is exactly the trade MPF makes.

## A short taxonomy of the structures it gets compared with

Three structures are routinely called "Merkle trees" and routinely confused with each other. They differ in how an element is addressed, and that single choice determines nearly everything else.

### Binary Merkle tree

The classical construction. Leaves are hashed, adjacent hashes are combined pairwise, and the process repeats to a single root. An element is addressed by **position**, and a proof is the sibling hash at each level: roughly $$\log_2 n$$ hashes, so 20 hashes or 640 bytes for a million leaves.

What it cannot do is the problem. There is no key, only an index, so there is no lookup by key and no way to prove that something is absent: absence would require showing every leaf. Inserting in the middle renumbers everything after it. This is the right structure for a fixed committed list, an airdrop allowlist or a transaction set inside a block, and the wrong one for a mutable registry.

### Sparse Merkle tree

The [sparse Merkle tree](https://eprint.iacr.org/2016/683.pdf) fixes the addressing problem by fixing the shape. Conceptually it is a complete binary tree of depth 256, where the leaf at position $$H(k)$$ holds the value for key $$k$$ and every other leaf holds a default. Addressing is by key, non-membership is proved exactly like membership by showing the default value at that leaf, and updates are local.

The cost is depth. A naive proof is 256 sibling hashes, 8 KB. In practice implementations compress the empty subtrees, because the hash of a subtree containing only defaults is itself a default that can be precomputed per level; a compressed proof then carries only the $$\log_2 n$$ or so siblings that are not default, plus a bitmap saying which levels were elided. That brings a million-element proof back to roughly 640 bytes of hashes. It works, but the traversal is 256 levels deep in the general case and the compression is an extra protocol that both sides must implement identically.

### Ethereum's Modified Merkle Patricia Trie

[Ethereum's MPT](https://ethereum.org/en/developers/docs/data-structures-and-encoding/patricia-merkle-trie/) is a radix-16 trie: each level consumes one hex digit (a nibble) of the path, so a branch node has 16 slots. The lineage is the [PATRICIA trie](https://dl.acm.org/doi/10.1145/321479.321481) of 1968, with path compression so that runs of single-child nodes collapse. It uses three node kinds, branch, extension and leaf, all RLP-encoded, and the state trie addresses accounts by `keccak256(address)` rather than by the raw address.

The radix-16 branching factor is a real gain: depth drops to about $$\log_{16} n$$, five levels for a million entries instead of twenty. The problem is what a proof has to carry at each of those levels. A branch node's hash commits to its RLP encoding, which contains all 16 child references. To recompute the node hash, the verifier needs the whole node, which means the 15 sibling hashes it did not take. That is roughly 480 bytes of hashes plus RLP framing per level, so a five-level proof lands around 2.5 KB. The trie got shallower and each level got 15 times more expensive.

## What a Merkle Patricia Forestry is

MPF starts from the Ethereum design and attacks precisely that per-level cost.

### Keys become paths

Every key is hashed before it is used for navigation. The off-chain helper is a one-liner:

```js
export function intoPath(key) {
  return digest(key = typeof key === 'string'
    ? Buffer.from(key)
    : key
  ).toString('hex');
}
```

`digest` is [BLAKE2b](https://datatracker.ietf.org/doc/html/rfc7693) with a 32-byte output, so a path is always 64 nibbles regardless of the key's own length or structure. Two properties follow. Paths are uniformly distributed, so the expected depth is

$$
\begin{aligned}
d \approx \log_{16} n = \frac{\log_2 n}{4}
\end{aligned}
$$

which is five levels at a million entries and seven at a hundred million. And no adversary can choose keys that deepen the trie, because doing so would require finding BLAKE2b preimages sharing a long prefix. The on-chain side hashes identically, in `including`:

```aiken
fn including(key: ByteArray, value: ByteArray, proof: Proof) -> ByteArray {
  do_including(blake2b_256(key), blake2b_256(value), 0, proof)
}
```

Note that the value is hashed too. A proof commits to a 32-byte digest of the value, not to the value itself, which keeps proof steps a fixed size whatever the payload.

### Two node kinds, and how they are hashed

Where Ethereum has three node kinds, MPF has two. There is no separate extension node, because the compressed prefix is carried inside the branch and leaf nodes themselves.

Write $$h$$ for BLAKE2b-256 and define the pairing function the library calls `combine`:

$$
\begin{aligned}
c(x, y) = h(x \mathbin\| y)
\end{aligned}
$$

A **branch** node with prefix $$p$$ and children $$c_0, \ldots, c_{15}$$ hashes as

$$
\begin{aligned}
H_B = h\big(\text{nib}(p) \mathbin\| \mathcal M(c_0, \ldots, c_{15})\big)
\end{aligned}
$$

where $$\text{nib}(p)$$ writes the prefix one nibble per byte and $$\mathcal M$$ is the Merkle root discussed in the next section. A branch always has at least two non-empty children; a node with a single child is a leaf by construction, which is what gives the trie its path compression.

A **leaf** node holds the remaining suffix of the path and the value:

$$
\begin{aligned}
H_L = h\big(\text{head} \mathbin\| \text{tail} \mathbin\| h(v)\big)
\end{aligned}
$$

The `head` and `tail` split is a parity tag. When the remaining suffix has an even number of nibbles it packs cleanly two per byte, and `head` is the single byte `0xFF`. When it is odd, `head` is `0x00` followed by a byte holding the orphan first nibble, and `tail` packs the rest. The on-chain `suffix` helper produces the same bytes by prepending onto the path:

```aiken
pub fn suffix(path, cursor) {
  if cursor % 2 == 0 {
    bytearray.drop(path, cursor / 2)
      |> bytearray.push(0xff)
  } else {
    bytearray.drop(path, ( cursor + 1 ) / 2)
      |> bytearray.push(nibble(path, cursor))
      |> bytearray.push(0)
  }
}
```

The tag matters for soundness. Without it, a suffix of `0a` and a suffix of `a` followed by a different framing could produce the same preimage, and two distinct trie states would share a root. Note the asymmetry with branches: leaf suffixes run up to 64 nibbles so packing them is worth a parity tag, while branch prefixes are short and are left unpacked.

### The forestry: a Merkle tree inside every branch

Rather than committing to a flat list of 16 children, a branch commits to the **Merkle root of a complete binary tree of depth 4 over those 16 slots**, with absent children represented by the null hash of 32 zero bytes:

```js
export function merkleRoot(children, size = 16) {
  let nodes = children.map(x => x?.hash ?? x ?? NULL_HASH);
  let n = nodes.length;
  // ...
  do {
    for (let i = 0; 2 * i < n; i += 1) {
      nodes.push(digest(Buffer.concat(nodes.splice(0, 2))));
    }
    n = nodes.length;
  } while (n > 1);
  return nodes[0];
}
```

Proving one child now takes the four siblings along that inner tree instead of the fifteen other children:

$$
\begin{aligned}
4 \times 32 = 128 \text{ bytes per level, against } 15 \times 32 = 480
\end{aligned}
$$

![Reduction from a branch node hash down to one child slot, showing the four sibling hashes n8, n4, n2 and n1 that a Branch proof step carries, with the sub-trie root rebuilt from the remaining steps]({{site.url_complet}}/assets/article/blockchain/cardano/mpf-branch-forestry-concept.png)

On-chain, that reduction is a hard-coded four-step fold rather than a loop, which is why it is cheap in execution units:

```aiken
pub fn merkle_16(
  branch: Int,
  root: ByteArray,
  neighbor_8: ByteArray,
  neighbor_4: ByteArray,
  neighbor_2: ByteArray,
  neighbor_1: ByteArray,
) -> ByteArray {
  if branch <= 7 {
    combine(
      merkle_8(branch, root, neighbor_4, neighbor_2, neighbor_1),
      neighbor_8,
    )
  } else {
    combine(
      neighbor_8,
      merkle_8(branch - 8, root, neighbor_4, neighbor_2, neighbor_1),
    )
  }
}
```

A second optimisation sits beside it. The hashes of subtrees made entirely of null hashes are constants, so the library precomputes them once:

```aiken
pub const null_hash =
  #"0000000000000000000000000000000000000000000000000000000000000000"

pub const null_hash_2 = combine(null_hash, null_hash)
pub const null_hash_4 = combine(null_hash_2, null_hash_2)
pub const null_hash_8 = combine(null_hash_4, null_hash_4)
```

These let the `sparse_merkle_16` family short-circuit the common case where a branch has exactly two occupied slots, which is what a freshly created fork looks like. The empty trie inherits the same convention: its root is `null_hash`, so `is_empty` is a comparison against 32 zero bytes.

### What this buys, in bytes

Putting the per-level cost against the depth gives the two proof sizes:

$$
\begin{aligned}
\lvert \pi_{\text{MPF}} \rvert \approx 128\,d + \varepsilon, \qquad \lvert \pi_{\text{MPT}} \rvert \approx 480\,d + \varepsilon
\end{aligned}
$$

with $$d \approx \log_{16} n$$ and $$\varepsilon$$ the encoding overhead. The library's measured figures track that closely: about 760 bytes at $$10^6$$ entries, about 1180 bytes at $$10^9$$. Growth is logarithmic and shallow, roughly 140 bytes per additional decimal order of magnitude.

Against the alternatives, MPF does not win on every axis:

| Structure | Addressing | Proof at 10⁶ items | Non-membership | Node kinds |
|-----------|-----------|--------------------|----------------|------------|
| Binary Merkle tree | position | ~640 B (20 levels) | not expressible | 1 |
| Sparse Merkle tree | key, 256-bit path | ~640 B compressed | native | 1 + default |
| Ethereum MPT | hashed key, radix 16 | ~2.5 KB | supported | 3 (RLP) |
| Merkle Patricia Forestry | hashed key, radix 16 | ~760 B | native (`miss`) | 2 |

Against a well-compressed sparse Merkle tree, MPF is in the same order of magnitude in bytes, and what it gains is structure rather than size: five proof steps to decode instead of twenty, five node reads per off-chain lookup instead of twenty, and no separate empty-subtree compression scheme that both implementations must agree on. Against Ethereum's MPT, which is the structure it is actually derived from, the gain is direct and is roughly a factor of four.

## The proof format

A proof is a list of steps, one per trie level, processed from left to right. Each step names the neighbour information at that level and a `skip` count giving the length of the common prefix consumed there.

```aiken
pub type Proof =
  List<ProofStep>

pub type ProofStep {
  Branch { skip: Int, neighbors: ByteArray }
  Fork { skip: Int, neighbor: Neighbor }
  Leaf { skip: Int, key: ByteArray, value: ByteArray }
}

pub type Neighbor {
  nibble: Int,
  prefix: ByteArray,
  root: ByteArray,
}
```

The three kinds correspond to three shapes a level can have:

- **`Branch`.** The ordinary case: a node with several occupied slots. `neighbors` is exactly 128 bytes, the four sibling hashes of the inner Merkle tree, sliced apart on-chain at offsets 0, 32, 64 and 96.
- **`Fork`.** The sparse case: exactly two occupied slots, ours and one neighbour. Rather than pad to a full 128 bytes, the step names the neighbour directly by its nibble, its own prefix and its root, and the verifier rebuilds a two-slot sparse Merkle root via `sparse_merkle_16`.
- **`Leaf`.** A fork whose neighbour happens to be a leaf. Because a leaf's hash depends on its remaining suffix, the step carries the neighbour's full key and value digest so the verifier can reconstruct that suffix itself, at whatever cursor position the fork occurs.

Verification is a recursion that descends the list and rebuilds hashes on the way back up, so the root is computed from the deepest step outwards:

```aiken
fn do_including(
  path: ByteArray,
  value: ByteArray,
  cursor: Int,
  proof: Proof,
) -> ByteArray {
  when proof is {
    [] -> combine(suffix(path, cursor), value)

    [Branch { skip, neighbors }, ..steps] -> {
      let next_cursor = cursor + skip
      let root = do_including(path, value, next_cursor + 1, steps)
      do_branch(path, cursor, next_cursor, root, neighbors)
    }
    // Fork and Leaf follow the same shape
  }
}
```

The `cursor` is the position in the 64-nibble path, advanced by `skip` for the shared prefix and then by one more for the nibble that selects the branch. Note that the path is never transmitted: the verifier recomputes it from the key, so a proof cannot claim a path that the key does not produce.

## One proof, two roots

The feature that distinguishes MPF's API from a conventional membership proof is that the same proof yields two different roots.

- `including(key, value, proof)` rebuilds the root of the trie **with** the element present.
- `excluding(key, proof)` walks the same steps but stops one short, rebuilding the root of the trie **without** it.

Every public operation is a pair of comparisons over those two functions:

```aiken
pub fn insert(
  self: MerklePatriciaForestry,
  key: ByteArray,
  value: ByteArray,
  proof: Proof,
) -> MerklePatriciaForestry {
  expect excluding(key, proof) == self.root
  MerklePatriciaForestry { root: including(key, value, proof) }
}
```

An insert asserts that the current root is the one without the element, then returns the root with it. A delete is the mirror image. `has` and `miss` compare one side against the stored root and return a boolean rather than failing. And `update` exploits the pair to save work:

```aiken
pub fn update(
  self: MerklePatriciaForestry,
  key: ByteArray,
  proof: Proof,
  old_value: ByteArray,
  new_value: ByteArray,
) -> MerklePatriciaForestry {
  expect including(key, old_value, proof) == self.root
  MerklePatriciaForestry { root: including(key, new_value, proof) }
}
```

A delete followed by an insert would evaluate `excluding` in between; because the key and its position are unchanged, `update` skips it and runs `including` twice instead. That is the difference between the update and insert rows in the benchmark table.

![Off-chain trie, transaction builder, Aiken validator and the on-chain MPF library exchanging a proof, showing insert, delete and update each reducing to a comparison between including and excluding]({{site.url_complet}}/assets/article/blockchain/cardano/mpf-onchain-verification-sequence.png)

## Where the boundary between the two packages sits

The split is strict and worth stating plainly, because it is the part integrators most often get wrong.

The **off-chain package** owns the data. It stores nodes in a [LevelDB](https://leveljs.org/)-backed store, keeps only the topmost node in memory and holds children as references, and exposes `insert`, `delete`, `get` and `prove`. Proofs serialise to JSON, to [CBOR](https://datatracker.ietf.org/doc/html/rfc8949) for use as a redeemer, to Aiken source for tests, and to textual UPLC for `aiken uplc eval`. Its `console.log` output is a pretty-printed trie, which is the fastest way to see the structure:

```
╔═══════════════════════════════════════════════════════════════════╗
║ #ee54d685370064b61cd8921f8476e54819990a67f6ebca402d1280ba1b03c75f ║
╚═══════════════════════════════════════════════════════════════════╝
 ┌─ 09ad7..[55 digits]..19d9 #33af5a3bbf8f { apple → 🍎 }
 ├─ 1 #a38f7e65ebf6
 │  ├─ b021f..[54 digits]..2290 #e5f9beffc856 { tomato → 🍅 }
 │  └─ e7b4b..[54 digits]..0675 #b5e92076b81f { cherries → 🍒 }
 ├─ 39cd4..[55 digits]..9e65 #ac9d183ca637 { blueberry → 🫐 }
 └─ 9 #75eba4e4dae1
    ├─ 702e3..[54 digits]..3a28 #c8b244fad188 { grapes → 🍇 }
    └─ b19ae..[54 digits]..962c #830b96edc35b { tangerine → 🍊 }
```

Six fruits, and the trie is already two levels deep with three branches at the root that are single leaves. That is path compression at work: `apple` and `blueberry` occupy one node each because no other key shares their first nibble.

The **on-chain package** owns nothing. `MerklePatriciaForestry` is an opaque type wrapping 32 bytes, `from_root` refuses anything that is not 32 bytes long, and there is no constructor that takes elements. The README states the restriction outright: the Aiken library contains no primitives for building tries on-chain, even for debugging. Every proof in the on-chain test suite was generated by the JavaScript package and pasted in.

## What the trade actually costs

Reading the library's benchmark table against the mainnet ceilings makes the trade-off concrete. Taking an insert into a trie of $$10^6$$ elements:

| Resource | Cost | Share of the transaction budget |
|----------|------|---------------------------------|
| Proof size | ~760 bytes | ~4.6% of the 16 384-byte transaction |
| Memory units | 444.5K | ~3.2% of ~14M |
| CPU units | 126.3M | ~1.3% of ~10G |
| Script size | ~2.5 KB of UPLC | fixed, once per script |

The forestry spends four extra BLAKE2b invocations per level to avoid transmitting eleven hashes per level. At roughly 3% of the memory budget and 1% of the CPU budget for a single operation, neither execution resource is the binding constraint; transaction size is, and it is the one the design optimises. The picture only changes when a transaction batches many operations, at which point the linear growth in proof bytes is what runs out first.

## Sharp edges

Several behaviours will surprise a reader who arrives expecting a hashmap.

**A false `has` is not a proof of absence.** The library documents this in a caution block, and it is the easiest mistake to make. `has(trie, key, value, proof)` compares `including(key, value, proof)` against the stored root, so it answers "is this key present *with this value*". A wrong value, a stale proof and a genuinely absent key all return `False`. Proving absence requires `miss`, which the on-chain changelog dates to version 2.1.0. Its own doc comment claims 1.2.0, a version that package never released, so read the changelog rather than the annotation.

**A proof is bound to one exact root.** Proofs commit to the neighbouring hashes at every level, so any write anywhere in the trie invalidates every outstanding proof, not just those near the modified key. Under eUTXO this compounds the usual contention on a single UTXO: two spenders racing to update the same registry will both hold proofs against the same old root, and the loser must rebuild against the new one. Designs that need throughput shard the registry across several UTXOs.

**Terminal forks with a non-empty common prefix were wrong twice.** When a proof's last step is a `Fork` or a `Leaf`, `excluding` has to reconstruct what the neighbour node looked like *before* the fork existed, which means splicing the shared prefix back onto it. The source carries a worked ASCII example of the reconstruction, and the fix arrived in two stages: version 2.0.1 corrected leaf forks with a non-zero common prefix, and version 2.1.0 corrected terminal forks with non-empty prefixes. Both are the same class of bug, in the one code path where the verifier must invent a node rather than recompute one.

```aiken
[Fork { skip, neighbor }] -> {
  let neighbor_prefix = bytearray.push(neighbor.prefix, neighbor.nibble)
  let prefix =
    if skip == 0 {
      neighbor_prefix
    } else {
      bytearray.concat(
        nibbles(path, cursor, cursor + skip),
        neighbor_prefix,
      )
    }
  combine(prefix, neighbor.root)
}
```

**Values are digests off-chain.** `Leaf.computeHash` asserts that the value it receives is exactly 32 bytes, because the caller has already hashed it. Passing a raw payload where a digest is expected fails loudly rather than producing a divergent root, which is the right failure but not an obvious one from the public API.

**Insert and delete are assertive.** `insert` fails if the key already exists, `delete` fails if it does not, and the off-chain package raises on a repeated insert too. There is no upsert; use `update`.

## Conclusion

Merkle Patricia Forestry is a radix-16 Patricia trie in the Ethereum lineage, with one substitution: a branch node commits to the Merkle root of a depth-4 binary tree over its 16 slots rather than to the slots themselves. That substitution moves the per-level proof cost from fifteen sibling hashes to four, which is what makes a million-entry authenticated map usable inside a 16 KB Cardano transaction.

The rest of the design follows from the eUTXO constraint. Keys are hashed into fixed 64-nibble paths, so depth is logarithmic and no adversary can deepen one branch at will. Node kinds are reduced from three to two by folding the compressed prefix into branches and leaves. The on-chain package holds no data and cannot build a trie; it verifies proofs against a 32-byte root and produces a new one. And because `including` and `excluding` walk the same proof to two different roots, insertion, deletion and update are all expressible as a comparison between them.

Compared with a compressed sparse Merkle tree the byte counts are similar, and the argument for MPF is fewer proof steps and shallower traversal rather than smaller proofs. Compared with the Ethereum MPT it is derived from, the proof is about four times smaller for the same dataset. What it does not remove is the contention that comes with any single-root structure under eUTXO, where every write invalidates every outstanding proof.

![Mindmap of Merkle Patricia Forestry covering the radix-16 trie structure, the forestry optimisation that merkleises 16 children into a depth-4 tree, the Branch/Fork/Leaf proof format, the including and excluding root pair, and the comparison with binary, sparse and Ethereum Merkle structures]({{site.url_complet}}/assets/article/blockchain/cardano/merkle-patricia-forestry-cardano.png)

## Annex

### Key Terms

| Term | Definition |
|------|------------|
| **Merkle Patricia Forestry (MPF)** | A radix-16 Patricia trie whose branch nodes commit to a depth-4 Merkle tree over their 16 children, giving 128-byte proof steps. |
| **Nibble** | A single hexadecimal digit, four bits. A path is 64 nibbles, one consumed per trie level. |
| **Path** | `blake2b_256(key)` rendered as 64 nibbles. Navigation uses the path, never the raw key. |
| **Null hash** | 32 zero bytes, the conventional hash of an empty trie or an absent child slot. |
| **`combine`** | The pairing function `blake2b_256(left ++ right)`, used for every internal hash in the structure. |
| **Skip** | The number of nibbles of common prefix consumed at one proof step, before the nibble that selects a branch. |
| **Fork** | A proof step for a level with exactly two occupied slots, naming the single neighbour instead of four sibling hashes. |
| **`including` / `excluding`** | The two root reconstructions from one proof, with and without the element, from which every public operation is built. |
| **Proof of exclusion** | Evidence that a key is absent, verified by `miss`. Distinct from `has` returning `False`, which is not a proof of anything. |
| **Opaque root** | The on-chain `MerklePatriciaForestry` type, a wrapper around exactly 32 bytes with no constructor that accepts elements. |

### Invariants

| Invariant | Enforced by | Breaks if |
|-----------|-------------|-----------|
| A root is always exactly 32 bytes. | `expect bytearray.length(root) == 32` in `from_root`, and the opaque type having no other public constructor. | A constructor taking an arbitrary byte array is exposed. |
| The empty trie's root is 32 zero bytes. | `empty` is defined as `null_hash`, and absent child slots use the same constant. | The null-hash convention changes without also changing the precomputed `null_hash_2`, `null_hash_4` and `null_hash_8`. |
| A branch node has at least two non-empty children. | An assertion in `Branch.from`; a node with one child is represented as a leaf. | Single-child branches are permitted, which would give two distinct encodings of the same map and so two distinct roots. |
| A path is the hash of the key, never the key. | Both `including` and `excluding` call `blake2b_256(key)` before walking; the path is never transmitted in a proof. | The path is taken from the proof instead of recomputed, letting a prover claim a position its key does not reach. |
| Two distinct leaf suffixes never share a preimage. | The parity tag in `suffix`, `0xFF` for even-length suffixes and `0x00` plus the orphan nibble for odd ones. | The tag is dropped, letting an odd-length and an even-length suffix collide into one root. |
| A branch and its neighbours reconstruct to the same root only if the four supplied hashes are the real siblings. | `merkle_16` folding the four neighbours in fixed positional order into the branch's inner Merkle root. | Neighbour ordering is treated as free rather than positional. |
| An insert only succeeds from the root that excludes the key. | `expect excluding(key, proof) == self.root` before computing the new root. | The pre-state check is dropped, allowing an insert over an existing key and a silent overwrite. |

### Integration Notes

| Behaviour | What an integrator should do |
|-----------|------------------------------|
| `has` returning `False` does not prove the key is absent. | Use `miss` with a proof of exclusion when absence is the claim being made; treat `has` strictly as "present with this exact value". |
| Any write invalidates every outstanding proof, not only proofs near the modified key. | Regenerate proofs against the current root immediately before building a transaction, and shard the registry across UTXOs if concurrent writers are expected. |
| The on-chain package cannot build a trie, by design. | Keep an off-chain trie as the source of truth, and replay every accepted on-chain operation against it so the two roots stay equal. |
| Off-chain, a leaf's value must already be a 32-byte digest. | Hash payloads before storing them; do not pass raw values into the low-level node constructors. |
| `insert` fails on an existing key and `delete` fails on a missing one. | Use `update` for a change in place; there is no upsert primitive on either side. |
| Proofs must be serialised for the target consumer. | `toCBOR` for a redeemer, `toAiken` for test fixtures, `toUPLC` for `aiken uplc eval`. Reconstruct with `Proof.fromJSON`, which needs the original key and value. |
| The dependency adds roughly 2.5 KB of UPLC to a validator. | Budget for it in script size, and consider a reference script when several validators share the library. |
| Terminal-fork verification changed in 2.0.1 and again in 2.1.0. | Pin at least version 2.1.0 on-chain, and pair it with an off-chain package that generates proofs for the same format. |

## Frequently Asked Questions

**Q: What does the word "forestry" actually refer to?**

It refers to the small Merkle trees hidden inside the branch nodes. A branch has 16 child slots, and instead of committing to them as a flat list, MPF builds a complete binary Merkle tree of depth 4 over those slots and commits to its root. Every branch node is therefore a tiny tree of its own, and the whole structure is a trie of trees.

The consequence is the point: proving one child requires the four siblings along that inner tree rather than the fifteen other children, which is 128 bytes per level instead of 480.

**Q: Why are keys hashed before use rather than used directly as trie paths?**

For two reasons:

- **Uniform depth.** A BLAKE2b-256 digest is 64 nibbles regardless of the key, and its digits are uniformly distributed, so the expected trie depth is about $$\log_{16} n$$ and the structure stays balanced whatever the keys look like.
- **Resistance to adversarial key choice.** With raw keys, an adversary can choose keys sharing long prefixes and deepen one branch of the trie arbitrarily, inflating proofs and execution costs along that path. Doing the same against hashed paths would require finding BLAKE2b preimages with a chosen prefix.

Ethereum's state trie hashes keys for the same reason.

**Q: How can one proof support both membership and insertion?**

Because the verifier can stop at two different points while rebuilding the root. `including` walks the proof steps and terminates by hashing the element's own leaf into the reconstruction, producing the root of the trie that contains it. `excluding` walks the identical steps but terminates without that leaf, producing the root of the trie that does not.

An insert is then just an assertion that the stored root equals the second value, followed by returning the first. A delete asserts the reverse. Nothing about the proof itself distinguishes the two operations.

**Q: If a compressed sparse Merkle tree has proofs of roughly the same size, why choose MPF?**

The gain is in the proof's structure rather than its byte count:

- **Fewer steps to decode.** Five proof steps at a million entries instead of about twenty, and decoding a list of constructors in UPLC has a real per-item cost.
- **Shallower traversal off-chain.** Five node reads per lookup instead of twenty, which matters when nodes live on disk.
- **No separate compression protocol.** Sparse Merkle tree proofs of practical size depend on an empty-subtree elision scheme with a bitmap, which both implementations must agree on exactly. MPF's path compression is part of the node encoding itself.

Where MPF clearly wins is against the Ethereum MPT it derives from, which is roughly four times larger for the same dataset.

**Q: Why does the leaf hash need a parity tag on its prefix?**

Because the remaining suffix is packed two nibbles per byte, and an odd-length suffix does not pack evenly. Without a tag, the byte string fed to the hash would be ambiguous: different suffixes could produce the same preimage, so two distinct trie states would share a root and a proof for one would verify against the other.

The tag resolves it by making the two framings unmistakable. An even-length suffix is prefixed with `0xFF`; an odd-length one is prefixed with `0x00` followed by a byte holding the single orphan nibble. Branch prefixes need no such treatment because they are stored unpacked, one nibble per byte.

**Q: A validator verifies an insert and the transaction succeeds. What still has to happen, and what has just broken?**

Two things, in order:

- **The off-chain trie must replay the same insert.** The on-chain side holds only a root; it cannot reconstruct the store. If the off-chain trie is not updated, its root diverges from the datum and every subsequent proof it generates will fail verification.
- **Every proof issued against the previous root is now stale.** Proofs commit to neighbouring hashes at each level, so a write anywhere invalidates all of them, including proofs for keys far from the one that changed.

The second point is what makes concurrent writers hard under eUTXO. Two parties holding proofs against the same old root will race for the UTXO, and only one can win; the other must fetch the new root, regenerate its proof and rebuild the transaction.

## References

### Structures and background

- [Ethereum Merkle Patricia Trie](https://ethereum.org/en/developers/docs/data-structures-and-encoding/patricia-merkle-trie/) — the radix-16 trie MPF derives from, with its three RLP-encoded node kinds
- [Efficient Sparse Merkle Trees — Caching Strategies and Secure (Non-)Membership Proofs](https://eprint.iacr.org/2016/683.pdf), Dahlberg, Pulls and Peeters, IACR ePrint 2016/683
- [PATRICIA — Practical Algorithm To Retrieve Information Coded in Alphanumeric](https://dl.acm.org/doi/10.1145/321479.321481), D. R. Morrison, Journal of the ACM, 1968
- [RFC 7693 — The BLAKE2 Cryptographic Hash and Message Authentication Code](https://datatracker.ietf.org/doc/html/rfc7693)
- [RFC 8949 — Concise Binary Object Representation (CBOR)](https://datatracker.ietf.org/doc/html/rfc8949)

### Library documentation

- [Merkle Patricia Forestry — Technical analysis](https://github.com/aiken-lang/merkle-patricia-forestry/wiki/Technical-analysis) — the project wiki's account of the forestry optimisation
- [Merkle Patricia Forestry — Proof format](https://github.com/aiken-lang/merkle-patricia-forestry/wiki/Proof-format)
- [On-chain API reference](https://aiken-lang.github.io/merkle-patricia-forestry/aiken/merkle_patricia_forestry.html) — generated from `aiken docs`
- [@aiken-lang/merkle-patricia-forestry on npm](https://www.npmjs.com/package/@aiken-lang/merkle-patricia-forestry) — the off-chain package
- [level.js](https://leveljs.org/) — the on-disk store backing the off-chain trie

### Cardano platform

- [Aiken](https://aiken-lang.org) — the language and toolchain the on-chain package targets
- [Cardano developer portal — smart contracts](https://developers.cardano.org/docs/smart-contracts/) — eUTXO validators, datums and redeemers

### Analyzed source

- [aiken-lang/merkle-patricia-forestry](https://github.com/aiken-lang/merkle-patricia-forestry) — analyzed at commit [`540dfdbf61f8697c548db460dee1beff78cadb19`](https://github.com/aiken-lang/merkle-patricia-forestry/tree/540dfdbf61f8697c548db460dee1beff78cadb19), 2026-08-28. The commit carries no tag; it is after on-chain `v2.1.0` (2025-07-12) and off-chain `v1.3.1` (2025-07-12), the versions whose behaviour this article describes.

### Related articles

- [Writing Cardano Smart Contracts with Aiken]({{site.url_complet}}/2026/07/16/aiken-smart-contracts-cardano/)
- [The Extended UTXO Model, and How It Differs from Bitcoin]({{site.url_complet}}/2026/07/16/eutxo-vs-bitcoin-utxo/)
- [Merkle DAGs(IPFS, GIT) - Overview]({{site.url_complet}}/2025/04/09/merkle-dag/)
