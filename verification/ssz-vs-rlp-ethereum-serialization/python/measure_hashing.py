"""Count hash calls: flat hashing of the serialisation against hash_tree_root."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import beacon_types as B  # noqa: E402
import ssz_codec as S  # noqa: E402
from mainnet import load  # noqa: E402
from ssz_codec import List, Uint64  # noqa: E402


def compressions(n):
    """SHA-256 compression calls for a message of n bytes."""
    return (n + 9 + 63) // 64


raw, sb, el, rc, hdr = load()
m = sb["message"]
ser = B.BeaconBlock.ser(m)
S.COUNT["h"] = 0
B.BeaconBlock.htr(m)
n = S.COUNT["h"]
print(f"real BeaconBlock: {len(ser)} bytes")
print(f"  flat sha256: 1 message, {compressions(len(ser))} compressions")
print(f"  hash_tree_root: {n} two-chunk hashes, {2*n} compressions without precomputed padding")

N = 2_000_000
vals = [(i * 2654435761) % 32_000_000_000 for i in range(N)]
ty = List(Uint64, 2**40)
b = ty.ser(vals)
print(f"List[Uint64, 2**40] with {N} values: {len(b)} bytes, {(len(b)+31)//32} chunks")
print(f"  flat sha256: {compressions(len(b))} compressions, every change repeats all of them")
S.COUNT["h"] = 0
ty.htr(vals)
full = S.COUNT["h"]
print(f"  hash_tree_root, first computation: {full} hashes")

# Update one element by walking one branch of a cached tree.
chunks = S.pack_bytes(b)
levels = [chunks]
while len(levels[-1]) > 1:
    lv = list(levels[-1])
    d = len(levels) - 1
    if len(lv) % 2:
        lv.append(S.ZERO[d])
    levels.append([S.hashlib.sha256(lv[i] + lv[i + 1]).digest() for i in range(0, len(lv), 2)])
root_before = ty.htr(vals)
i = 1234567
vals2 = list(vals)
vals2[i] = 31_999_999_999
c = i // 4
chunk = bytearray(chunks[c])
chunk[(i % 4) * 8:(i % 4) * 8 + 8] = vals2[i].to_bytes(8, "little")
node = bytes(chunk)
S.COUNT["h"] = 0
idx = c
for d in range(len(levels) - 1):
    sib = levels[d][idx ^ 1] if (idx ^ 1) < len(levels[d]) else S.ZERO[d]
    node = S.H(sib, node) if idx & 1 else S.H(node, sib)
    idx >>= 1
for d in range(len(levels) - 1, 38):
    node = S.H(node, S.ZERO[d])
node = S.mix_length(node, N)
inc = S.COUNT["h"]
print(f"  update one value through the cached tree: {inc} hashes, depth 38 + 1 length mix-in")
print("  incremental root equals a full recomputation:", node == ty.htr(vals2), "(and differs from before:", node != root_before, ")")
print(f"  ratio full / incremental: {full/inc:.0f}")
