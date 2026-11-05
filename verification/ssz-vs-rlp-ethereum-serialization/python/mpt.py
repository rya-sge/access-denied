"""Merkle-Patricia trie root and inclusion proof over an in-memory key/value map."""
from keccak import keccak256
from rlp_codec import encode, decode


def _nibbles(k: bytes):
    out = []
    for b in k:
        out += [b >> 4, b & 15]
    return out


def _hp(nib, leaf: bool) -> bytes:
    flag = 2 if leaf else 0
    if len(nib) % 2:
        first = [(flag | 1) << 4 | nib[0]]
        rest = nib[1:]
    else:
        first = [flag << 4]
        rest = nib
    return bytes(first + [rest[i] << 4 | rest[i + 1] for i in range(0, len(rest), 2)])


def _common(a, b):
    n = 0
    while n < len(a) and n < len(b) and a[n] == b[n]:
        n += 1
    return n


def _node(items):
    """items: sorted list of (nibbles, value). Returns the node as a nested RLP object."""
    if len(items) == 1:
        k, v = items[0]
        return [_hp(k, True), v]
    pre = items[0][0]
    for k, _ in items[1:]:
        pre = pre[: _common(pre, k)]
    if pre:
        return [_hp(pre, False), _ref(_node([(k[len(pre):], v) for k, v in items]))]
    br = [b""] * 17
    for n in range(16):
        sub = [(k[1:], v) for k, v in items if k and k[0] == n]
        if sub:
            br[n] = _ref(_node(sub))
    for k, v in items:
        if not k:
            br[16] = v
    return br


def _ref(node):
    """Node reference: the node itself if its RLP is under 32 bytes, else its hash."""
    e = encode(node)
    return node if len(e) < 32 else keccak256(e)


def trie_root(kv: dict) -> bytes:
    if not kv:
        return keccak256(encode(b""))
    return keccak256(encode(_node(sorted((_nibbles(k), v) for k, v in kv.items()))))


def trie_proof(kv: dict, key: bytes):
    """Return the RLP-encoded hashed nodes on the path to key, root first."""
    path = _nibbles(key)
    items = sorted((_nibbles(k), v) for k, v in kv.items())
    proof = []

    def walk(items, path, is_root):
        n = _node(items)
        e = encode(n)
        if is_root or len(e) >= 32:
            proof.append(e)
        if len(items) == 1:
            return
        pre = items[0][0]
        for k, _ in items[1:]:
            pre = pre[: _common(pre, k)]
        if pre:
            items = [(k[len(pre):], v) for k, v in items]
            path = path[len(pre):]
            # the extension's child is a branch: visit it
            walk(items, path, False)
            return
        if path:
            sub = [(k[1:], v) for k, v in items if k and k[0] == path[0]]
            if sub:
                walk(sub, path[1:], False)

    walk(items, path, True)
    return proof


def verify_proof(root: bytes, key: bytes, proof) -> bytes:
    """Independent walker: follows hashes from root to the value. Returns the value."""
    db = {keccak256(p): p for p in proof}
    path = _nibbles(key)
    ref = root
    while True:
        node = decode(db[ref]) if isinstance(ref, (bytes, bytearray)) and len(ref) == 32 else ref
        if len(node) == 17:
            if not path:
                return node[16]
            ref = node[path[0]]
            path = path[1:]
            continue
        hp = node[0]
        flag = hp[0] >> 4
        nib = ([hp[0] & 15] if flag & 1 else []) + _nibbles(hp[1:])
        if path[: len(nib)] != nib:
            raise ValueError("path mismatch")
        path = path[len(nib):]
        if flag & 2:
            if path:
                raise ValueError("leaf mismatch")
            return node[1]
        ref = node[1]
