#!/usr/bin/env python3
"""Minimal SSZ hash_tree_root and Merkle proofs for the Fulu BeaconState.

Standard library only. Written for the article "When a Merkle Proof Breaks at a
Hard Fork" to reproduce its mainnet section. Not audited, not a general SSZ
library: it covers the types that appear in the Fulu BeaconState and in
BeaconBlockHeader, read from consensus-specs at commit 065bcd5c6.

Every type works directly on serialized bytes (no decoded object model):

    t.fixed_size()      size in bytes, or None for a variable-size type
    t.root(data)        hash_tree_root of the serialized value
    t.tree(data)        a Tree that can return any node and any branch

A Tree is a fixed-depth binary tree whose leaves may themselves be subtrees
(a container field, a list element, the data half of a list). `Tree.node(g)`
returns the node at generalized index g, descending into subtrees, and
`Tree.get_branch(g)` returns the siblings from the leaf upwards, the order
expected by `is_valid_merkle_branch`.

Self-test (no network): python3 -I ssz_state.py
"""

import hashlib
import struct

# ---------------------------------------------------------------- hashing

def sha256(b):
    return hashlib.sha256(b).digest()


ZERO_CHUNK = b"\x00" * 32
ZERO_HASHES = [ZERO_CHUNK]
for _ in range(64):
    ZERO_HASHES.append(sha256(ZERO_HASHES[-1] * 2))


def next_pow2_depth(n):
    """Depth of a tree with at least n leaves (n <= 1 gives depth 0)."""
    d = 0
    while (1 << d) < n:
        d += 1
    return d


def pack(data):
    """Split bytes into 32-byte chunks, right-padding the last one with zeros."""
    if len(data) % 32:
        data = data + b"\x00" * (32 - len(data) % 32)
    return [data[i:i + 32] for i in range(0, len(data), 32)]


def merkle_layers(chunks, depth):
    """All layers of the tree over `chunks`, virtually padded to 2**depth leaves.

    layers[0] are the leaves actually present, layers[depth] == [root]. Missing
    right nodes at level l are ZERO_HASHES[l]; nothing is stored for them.
    """
    if len(chunks) > (1 << depth):
        raise ValueError("more chunks than the limit allows")
    layers = [list(chunks)]
    cur = layers[0]
    for level in range(depth):
        if not cur:
            nxt = []
        else:
            if len(cur) % 2:
                cur = cur + [ZERO_HASHES[level]]
            nxt = [sha256(cur[i] + cur[i + 1]) for i in range(0, len(cur), 2)]
        layers.append(nxt)
        cur = nxt
    if not layers[depth]:
        layers[depth] = [ZERO_HASHES[depth]]
    return layers


def merkleize(chunks, depth):
    """Root only, without keeping the layers."""
    cur = list(chunks)
    if len(cur) > (1 << depth):
        raise ValueError("more chunks than the limit allows")
    if not cur:
        return ZERO_HASHES[depth]
    for level in range(depth):
        if len(cur) % 2:
            cur.append(ZERO_HASHES[level])
        cur = [sha256(cur[i] + cur[i + 1]) for i in range(0, len(cur), 2)]
    return cur[0]


def mix_in_length(root, length):
    return sha256(root + length.to_bytes(32, "little"))


# ---------------------------------------------------------------- tree

class BelowLeaf(Exception):
    """The requested gindex lies below a leaf chunk: no valid branch exists."""


class Tree:
    """Binary tree of fixed depth. `subs(i)` returns the subtree rooted at leaf i, or None."""

    def __init__(self, layers, depth, subs=None):
        self.layers = layers
        self.depth = depth
        self.subs = subs or (lambda i: None)

    def root(self):
        return self.layers[self.depth][0]

    def node(self, g):
        if g < 1:
            raise ValueError("gindex must be >= 1")
        d = g.bit_length() - 1
        if d <= self.depth:
            level = self.depth - d
            idx = g - (1 << d)
            layer = self.layers[level]
            return layer[idx] if idx < len(layer) else ZERO_HASHES[level]
        leaf = g >> (d - self.depth)
        rest = (1 << (d - self.depth)) | (g & ((1 << (d - self.depth)) - 1))
        sub = self.subs(leaf - (1 << self.depth))
        if sub is None:
            raise BelowLeaf("gindex %d is below a leaf chunk at depth %d" % (g, self.depth))
        return sub.node(rest)

    def get_branch(self, g):
        branch = []
        while g > 1:
            branch.append(self.node(g ^ 1))
            g >>= 1
        return branch


def leaf_tree(chunk):
    return Tree([[chunk]], 0)


def list_tree(data_tree, length):
    """A List/ByteList/Bitlist: data subtree at gindex 2, length chunk at gindex 3."""
    length_chunk = length.to_bytes(32, "little")
    top = [[data_tree.root(), length_chunk], [sha256(data_tree.root() + length_chunk)]]
    return Tree(top, 1, lambda i: data_tree if i == 0 else None)


# ---------------------------------------------------------------- types

class Uint:
    def __init__(self, n):
        self.n = n
        self.basic = True

    def fixed_size(self):
        return self.n

    def root(self, data):
        assert len(data) == self.n
        return data + b"\x00" * (32 - self.n)

    def tree(self, data):
        return leaf_tree(self.root(data))


Uint8, Uint64, Uint256 = Uint(1), Uint(8), Uint(32)
Boolean = Uint(1)


class ByteVector:
    basic = False

    def __init__(self, n):
        self.n = n

    def fixed_size(self):
        return self.n

    def _depth(self):
        return next_pow2_depth((self.n + 31) // 32)

    def root(self, data):
        assert len(data) == self.n
        return merkleize(pack(data), self._depth())

    def tree(self, data):
        return Tree(merkle_layers(pack(data), self._depth()), self._depth())


Bytes4, Bytes20, Bytes32, Bytes48, Bytes96 = (ByteVector(n) for n in (4, 20, 32, 48, 96))


class ByteList:
    basic = False

    def __init__(self, limit):
        self.limit = limit

    def fixed_size(self):
        return None

    def _depth(self):
        return next_pow2_depth((self.limit + 31) // 32)

    def root(self, data):
        return mix_in_length(merkleize(pack(data), self._depth()), len(data))

    def tree(self, data):
        return list_tree(Tree(merkle_layers(pack(data), self._depth()), self._depth()), len(data))


class Bitvector:
    basic = False

    def __init__(self, n):
        self.n = n

    def fixed_size(self):
        return (self.n + 7) // 8

    def _depth(self):
        return next_pow2_depth((self.n + 255) // 256)

    def root(self, data):
        return merkleize(pack(data), self._depth())

    def tree(self, data):
        return Tree(merkle_layers(pack(data), self._depth()), self._depth())


class Bitlist:
    """Not used by the Fulu BeaconState; kept for blocks and attestations."""
    basic = False

    def __init__(self, limit):
        self.limit = limit

    def fixed_size(self):
        return None

    def _split(self, data):
        if not data or data[-1] == 0:
            raise ValueError("bitlist without a delimiter bit")
        nbits = (len(data) - 1) * 8 + data[-1].bit_length() - 1
        b = bytearray(data)
        b[-1] ^= 1 << (data[-1].bit_length() - 1)  # remove the delimiter
        packed = bytes(b[: (nbits + 7) // 8])
        return packed, nbits

    def _depth(self):
        return next_pow2_depth((self.limit + 255) // 256)

    def root(self, data):
        packed, nbits = self._split(data)
        return mix_in_length(merkleize(pack(packed), self._depth()), nbits)

    def tree(self, data):
        packed, nbits = self._split(data)
        return list_tree(Tree(merkle_layers(pack(packed), self._depth()), self._depth()), nbits)


def _split_fixed(elem, data, count):
    size = elem.fixed_size()
    return [data[i * size:(i + 1) * size] for i in range(count)]


def _split_variable(data):
    if not data:
        return []
    first = struct.unpack_from("<I", data, 0)[0]
    if first % 4 or first > len(data):
        raise ValueError("bad first offset")
    offs = [struct.unpack_from("<I", data, 4 * i)[0] for i in range(first // 4)] + [len(data)]
    return [data[offs[i]:offs[i + 1]] for i in range(len(offs) - 1)]


class _Sequence:
    basic = False

    def _elements(self, data):
        size = self.elem.fixed_size()
        if size is None:
            return _split_variable(data)
        if len(data) % size:
            raise ValueError("length not a multiple of the element size")
        return _split_fixed(self.elem, data, len(data) // size)

    def _data_tree(self, data, max_count, keep_layers):
        """Data subtree, its depth computed from the limit (in chunks), not the length."""
        if self.elem.basic:
            depth = next_pow2_depth((max_count * self.elem.fixed_size() + 31) // 32)
            chunks = pack(data)
            if not keep_layers:
                return merkleize(chunks, depth)
            return Tree(merkle_layers(chunks, depth), depth)
        depth = next_pow2_depth(max_count)
        elem = self.elem
        size = elem.fixed_size()
        if size is None:
            elems = self._elements(data)
            roots = [elem.root(e) for e in elems]
            n = len(elems)
            get = elems.__getitem__
        else:
            # Fixed-size elements: slice on demand, so 2.4M validators are not kept as objects.
            if len(data) % size:
                raise ValueError("length not a multiple of the element size")
            n = len(data) // size
            roots = [elem.root(data[i:i + size]) for i in range(0, len(data), size)]

            def get(i):
                return data[i * size:(i + 1) * size]
        if not keep_layers:
            return merkleize(roots, depth)
        return Tree(merkle_layers(roots, depth), depth,
                    lambda i: elem.tree(get(i)) if i < n else None)

    def count(self, data):
        if self.elem.fixed_size() is None:
            return len(_split_variable(data))
        return len(data) // self.elem.fixed_size()


class Vector(_Sequence):
    def __init__(self, elem, n):
        self.elem, self.n = elem, n

    def fixed_size(self):
        s = self.elem.fixed_size()
        return None if s is None else s * self.n

    def root(self, data):
        assert self.count(data) == self.n
        return self._data_tree(data, self.n, False)

    def tree(self, data):
        assert self.count(data) == self.n
        return self._data_tree(data, self.n, True)


class List(_Sequence):
    def __init__(self, elem, limit):
        self.elem, self.limit = elem, limit

    def fixed_size(self):
        return None

    def root(self, data):
        n = self.count(data)
        assert n <= self.limit
        return mix_in_length(self._data_tree(data, self.limit, False), n)

    def tree(self, data):
        n = self.count(data)
        assert n <= self.limit
        return list_tree(self._data_tree(data, self.limit, True), n)


class Container:
    basic = False

    def __init__(self, name, fields):
        self.name = name
        self.fields = fields  # list of (name, type)

    def fixed_size(self):
        total = 0
        for _, t in self.fields:
            s = t.fixed_size()
            if s is None:
                return None
            total += s
        return total

    def split(self, data):
        """Serialized bytes of each field, in order (SSZ offsets for variable fields)."""
        pos, parts, var = 0, [], []
        for i, (_, t) in enumerate(self.fields):
            s = t.fixed_size()
            if s is None:
                var.append((i, struct.unpack_from("<I", data, pos)[0]))
                parts.append(None)
                pos += 4
            else:
                parts.append(data[pos:pos + s])
                pos += s
        if var and var[0][1] != pos:
            raise ValueError("%s: first offset %d != fixed part %d" % (self.name, var[0][1], pos))
        if not var and pos != len(data):
            raise ValueError("%s: size %d != %d" % (self.name, len(data), pos))
        for k, (i, off) in enumerate(var):
            end = var[k + 1][1] if k + 1 < len(var) else len(data)
            if end < off:
                raise ValueError("decreasing offsets")
            parts[i] = data[off:end]
        return parts

    def field(self, data, name):
        for (n, t), part in zip(self.fields, self.split(data)):
            if n == name:
                return t, part
        raise KeyError(name)

    def depth(self):
        return next_pow2_depth(len(self.fields))

    def root(self, data):
        return merkleize([t.root(p) for (_, t), p in zip(self.fields, self.split(data))], self.depth())

    def tree(self, data):
        parts = self.split(data)
        trees = [None if t.basic else t.tree(p) for (_, t), p in zip(self.fields, parts)]
        roots = [t.root(p) if tr is None else tr.root()
                 for ((_, t), p, tr) in zip(self.fields, parts, trees)]
        return Tree(merkle_layers(roots, self.depth()), self.depth(),
                    lambda i: trees[i] if i < len(trees) else None)

    def gindex(self, name):
        for i, (n, _) in enumerate(self.fields):
            if n == name:
                return (1 << self.depth()) + i
        raise KeyError(name)


# ---------------------------------------------------------------- Fulu types (mainnet preset)

SLOTS_PER_EPOCH = 32
SLOTS_PER_HISTORICAL_ROOT = 2 ** 13
HISTORICAL_ROOTS_LIMIT = 2 ** 24
VALIDATOR_REGISTRY_LIMIT = 2 ** 40
EPOCHS_PER_ETH1_VOTING_PERIOD = 2 ** 6
EPOCHS_PER_HISTORICAL_VECTOR = 2 ** 16
EPOCHS_PER_SLASHINGS_VECTOR = 2 ** 13
JUSTIFICATION_BITS_LENGTH = 4
SYNC_COMMITTEE_SIZE = 2 ** 9
BYTES_PER_LOGS_BLOOM = 2 ** 8
MAX_EXTRA_DATA_BYTES = 2 ** 5
PENDING_DEPOSITS_LIMIT = 2 ** 27
PENDING_PARTIAL_WITHDRAWALS_LIMIT = 2 ** 27
PENDING_CONSOLIDATIONS_LIMIT = 2 ** 18
MIN_SEED_LOOKAHEAD = 1

Fork = Container("Fork", [("previous_version", Bytes4), ("current_version", Bytes4), ("epoch", Uint64)])
BeaconBlockHeader = Container("BeaconBlockHeader", [
    ("slot", Uint64), ("proposer_index", Uint64), ("parent_root", Bytes32),
    ("state_root", Bytes32), ("body_root", Bytes32)])
Eth1Data = Container("Eth1Data", [("deposit_root", Bytes32), ("deposit_count", Uint64), ("block_hash", Bytes32)])
Validator = Container("Validator", [
    ("pubkey", Bytes48), ("withdrawal_credentials", Bytes32), ("effective_balance", Uint64),
    ("slashed", Boolean), ("activation_eligibility_epoch", Uint64), ("activation_epoch", Uint64),
    ("exit_epoch", Uint64), ("withdrawable_epoch", Uint64)])
Checkpoint = Container("Checkpoint", [("epoch", Uint64), ("root", Bytes32)])
SyncCommittee = Container("SyncCommittee", [
    ("pubkeys", Vector(Bytes48, SYNC_COMMITTEE_SIZE)), ("aggregate_pubkey", Bytes48)])
ExecutionPayloadHeader = Container("ExecutionPayloadHeader", [  # Deneb layout, unchanged in Electra and Fulu
    ("parent_hash", Bytes32), ("fee_recipient", Bytes20), ("state_root", Bytes32),
    ("receipts_root", Bytes32), ("logs_bloom", ByteVector(BYTES_PER_LOGS_BLOOM)),
    ("prev_randao", Bytes32), ("block_number", Uint64), ("gas_limit", Uint64),
    ("gas_used", Uint64), ("timestamp", Uint64), ("extra_data", ByteList(MAX_EXTRA_DATA_BYTES)),
    ("base_fee_per_gas", Uint256), ("block_hash", Bytes32), ("transactions_root", Bytes32),
    ("withdrawals_root", Bytes32), ("blob_gas_used", Uint64), ("excess_blob_gas", Uint64)])
HistoricalSummary = Container("HistoricalSummary", [("block_summary_root", Bytes32), ("state_summary_root", Bytes32)])
PendingDeposit = Container("PendingDeposit", [
    ("pubkey", Bytes48), ("withdrawal_credentials", Bytes32), ("amount", Uint64),
    ("signature", Bytes96), ("slot", Uint64)])
PendingPartialWithdrawal = Container("PendingPartialWithdrawal", [
    ("validator_index", Uint64), ("amount", Uint64), ("withdrawable_epoch", Uint64)])
PendingConsolidation = Container("PendingConsolidation", [("source_index", Uint64), ("target_index", Uint64)])

BeaconStateFulu = Container("BeaconState", [
    ("genesis_time", Uint64),
    ("genesis_validators_root", Bytes32),
    ("slot", Uint64),
    ("fork", Fork),
    ("latest_block_header", BeaconBlockHeader),
    ("block_roots", Vector(Bytes32, SLOTS_PER_HISTORICAL_ROOT)),
    ("state_roots", Vector(Bytes32, SLOTS_PER_HISTORICAL_ROOT)),
    ("historical_roots", List(Bytes32, HISTORICAL_ROOTS_LIMIT)),
    ("eth1_data", Eth1Data),
    ("eth1_data_votes", List(Eth1Data, EPOCHS_PER_ETH1_VOTING_PERIOD * SLOTS_PER_EPOCH)),
    ("eth1_deposit_index", Uint64),
    ("validators", List(Validator, VALIDATOR_REGISTRY_LIMIT)),
    ("balances", List(Uint64, VALIDATOR_REGISTRY_LIMIT)),
    ("randao_mixes", Vector(Bytes32, EPOCHS_PER_HISTORICAL_VECTOR)),
    ("slashings", Vector(Uint64, EPOCHS_PER_SLASHINGS_VECTOR)),
    ("previous_epoch_participation", List(Uint8, VALIDATOR_REGISTRY_LIMIT)),
    ("current_epoch_participation", List(Uint8, VALIDATOR_REGISTRY_LIMIT)),
    ("justification_bits", Bitvector(JUSTIFICATION_BITS_LENGTH)),
    ("previous_justified_checkpoint", Checkpoint),
    ("current_justified_checkpoint", Checkpoint),
    ("finalized_checkpoint", Checkpoint),
    ("inactivity_scores", List(Uint64, VALIDATOR_REGISTRY_LIMIT)),
    ("current_sync_committee", SyncCommittee),
    ("next_sync_committee", SyncCommittee),
    ("latest_execution_payload_header", ExecutionPayloadHeader),
    ("next_withdrawal_index", Uint64),
    ("next_withdrawal_validator_index", Uint64),
    ("historical_summaries", List(HistoricalSummary, HISTORICAL_ROOTS_LIMIT)),
    ("deposit_requests_start_index", Uint64),
    ("deposit_balance_to_consume", Uint64),
    ("exit_balance_to_consume", Uint64),
    ("earliest_exit_epoch", Uint64),
    ("consolidation_balance_to_consume", Uint64),
    ("earliest_consolidation_epoch", Uint64),
    ("pending_deposits", List(PendingDeposit, PENDING_DEPOSITS_LIMIT)),
    ("pending_partial_withdrawals", List(PendingPartialWithdrawal, PENDING_PARTIAL_WITHDRAWALS_LIMIT)),
    ("pending_consolidations", List(PendingConsolidation, PENDING_CONSOLIDATIONS_LIMIT)),
    ("proposer_lookahead", Vector(Uint64, (MIN_SEED_LOOKAHEAD + 1) * SLOTS_PER_EPOCH)),
])


def header_bytes(slot, proposer_index, parent_root, state_root, body_root):
    return (struct.pack("<QQ", slot, proposer_index) + parent_root + state_root + body_root)


def header_root(slot, proposer_index, parent_root, state_root, body_root):
    return BeaconBlockHeader.root(header_bytes(slot, proposer_index, parent_root, state_root, body_root))


# ---------------------------------------------------------------- proofs

def concat_gindices(*gs):
    """concat_generalized_indices from ssz/merkle-proofs.md."""
    out = 1
    for g in gs:
        d = g.bit_length() - 1
        out = out * (1 << d) + (g - (1 << d))
    return out


def compute_merkle_branch_root(leaf, branch, depth, index):
    """Port of compute_merkle_branch_root (specs/phase0/beacon-chain.md)."""
    value = leaf
    for i in range(depth):
        if index // (2 ** i) % 2:
            value = sha256(branch[i] + value)
        else:
            value = sha256(value + branch[i])
    return value


def is_valid_merkle_branch(leaf, branch, depth, index, root):
    """Port of is_valid_merkle_branch (specs/phase0/beacon-chain.md). `index` is the
    gindex without its leading bit (get_subtree_index)."""
    if depth != len(branch):
        return False
    return compute_merkle_branch_root(leaf, branch, depth, index) == root


def verify_gindex(leaf, branch, gindex, root):
    depth = gindex.bit_length() - 1
    return is_valid_merkle_branch(leaf, branch, depth, gindex - (1 << depth), root)


def block_tree(header_data, state_tree):
    """Header tree whose `state_root` leaf (gindex 11) descends into `state_tree`."""
    parts = BeaconBlockHeader.split(header_data)
    roots = [t.root(p) for (_, t), p in zip(BeaconBlockHeader.fields, parts)]
    if roots[3] != state_tree.root():
        raise ValueError("header state_root != hash_tree_root(state)")
    return Tree(merkle_layers(roots, 3), 3, lambda i: state_tree if i == 3 else None)


# ---------------------------------------------------------------- self-test

def _selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(("PASS " if cond else "FAIL ") + name)

    # Basic merkleization rules.
    check("zero hash of depth 1 = sha256(64 zero bytes) starts f5a5fd42",
          ZERO_HASHES[1].hex().startswith("f5a5fd42"))
    pk = bytes(range(48))
    check("Bytes48 root = sha256(pubkey || 16 zero bytes)", Bytes48.root(pk) == sha256(pk + b"\x00" * 16))
    check("participation list depth 35 (limit 2**40 bytes = 2**35 chunks)",
          List(Uint8, 2 ** 40).root(b"") == mix_in_length(ZERO_HASHES[35], 0))
    check("balances depth 38", List(Uint64, 2 ** 40).root(b"") == mix_in_length(ZERO_HASHES[38], 0))
    check("validators depth 40", List(Validator, 2 ** 40).root(b"") == mix_in_length(ZERO_HASHES[40], 0))
    lk = b"".join(struct.pack("<Q", i) for i in range(64))
    check("proposer_lookahead: 64 values = 16 chunks, depth 4",
          Vector(Uint64, 64).root(lk) == merkleize(pack(lk), 4))
    check("Bitvector[4] 0b1111 -> 0x0f chunk", Bitvector(4).root(b"\x0f") == b"\x0f" + b"\x00" * 31)
    check("Bitlist delimiter removed",
          Bitlist(2048).root(b"\x1f") == mix_in_length(merkleize([b"\x0f" + b"\x00" * 31], 3), 4))
    check("concat(11, 75, 2, 2**40+1000000, 9) = 12,578,413,029,757,441",
          concat_gindices(11, 75, 2, 2 ** 40 + 1_000_000, 9) == 12_578_413_029_757_441)
    check("BeaconState Fulu has 38 fields, depth 6", len(BeaconStateFulu.fields) == 38 and BeaconStateFulu.depth() == 6)

    # Synthetic tree: a small validator list, a branch for every field of every validator.
    vals = b"".join(sha256(bytes([i]))[:48 - 32] + sha256(bytes([i, 1])) + sha256(bytes([i, 2]))
                    + struct.pack("<Q", 32 * 10 ** 9) + b"\x00" + struct.pack("<QQQQ", 1, 2, 3, 4)
                    for i in range(5))
    lt = List(Validator, 2 ** 40)
    tree = lt.tree(vals)
    check("synthetic list tree root == root()", tree.root() == lt.root(vals))
    good = True
    for i in range(5):
        v = vals[121 * i:121 * (i + 1)]
        vt = Validator.tree(v)
        for f in range(8):
            g = concat_gindices(2, 2 ** 40 + i, 8 + f)
            br = tree.get_branch(g)
            good &= len(br) == 44 and verify_gindex(vt.node(8 + f), br, g, tree.root())
            good &= not verify_gindex(vt.node(8 + f), br[:-1], g, tree.root())
    check("synthetic validator field branches verify (44 siblings), truncations fail", good)
    try:
        tree.node(concat_gindices(2, 2 ** 40, 9, 2))
        check("node below a leaf chunk raises BelowLeaf", False)
    except BelowLeaf:
        check("node below a leaf chunk raises BelowLeaf", True)
    print("self-test:", "all PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _selftest() else 1)
