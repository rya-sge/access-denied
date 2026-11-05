"""Simple Serialize: types, strict decoder and hash_tree_root, standard library only.

Written against ethereum/ssz-specs (see README for the pin). Values are plain Python:
int, bool, bytes, list of bool for bitfields, dict for containers, (selector, value)
for a CompatibleUnion. Each rejection carries a reason code.

sha256 goes through H() so that hashing can be counted.
"""
import hashlib

CHUNK = 32
OFFSET = 4
COUNT = {"h": 0}


class SSZError(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def H(a: bytes, b: bytes) -> bytes:
    COUNT["h"] += 1
    return hashlib.sha256(a + b).digest()


ZERO = [bytes(CHUNK)]
for _ in range(80):
    ZERO.append(hashlib.sha256(ZERO[-1] + ZERO[-1]).digest())


def next_pow2(x: int) -> int:
    return 1 if x <= 1 else 1 << (x - 1).bit_length()


def merkleize(chunks, limit=None) -> bytes:
    n = len(chunks)
    width = next_pow2(n) if limit is None else next_pow2(limit)
    if limit is not None and n > limit:
        raise SSZError("merkleize-over-limit")
    depth = (width - 1).bit_length()
    if n == 0:
        return ZERO[depth]
    if width == 1:
        return chunks[0]
    level = list(chunks)
    for d in range(depth):
        if len(level) % 2:
            level.append(ZERO[d])
        level = [H(level[i], level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]


def merkleize_progressive(chunks, num_leaves=1) -> bytes:
    if not chunks:
        return ZERO[0]
    return H(merkleize(chunks[:num_leaves], num_leaves),
             merkleize_progressive(chunks[num_leaves:], num_leaves * 4))


def pack_bytes(b: bytes):
    b = b + bytes(-len(b) % CHUNK)
    return [b[i:i + CHUNK] for i in range(0, len(b), CHUNK)]


def pack_bits(bits):
    n = bytearray((len(bits) + 7) // 8)
    for i, x in enumerate(bits):
        if x:
            n[i >> 3] |= 1 << (i & 7)
    return pack_bytes(bytes(n))


def mix_length(root, n):
    return H(root, n.to_bytes(CHUNK, "little"))


class T:
    basic = False

    def fixed(self):
        return True

    def size(self):
        raise NotImplementedError


class Uint(T):
    basic = True

    def __init__(self, bits):
        self.n = bits // 8

    def size(self):
        return self.n

    def ser(self, v):
        return int(v).to_bytes(self.n, "little")

    def de(self, d):
        if len(d) != self.n:
            raise SSZError("wrong-size")
        return int.from_bytes(d, "little")

    def htr(self, v):
        return self.ser(v).ljust(CHUNK, b"\0")


class Boolean(T):
    basic = True

    def size(self):
        return 1

    def ser(self, v):
        return b"\x01" if v else b"\x00"

    def de(self, d):
        if len(d) != 1:
            raise SSZError("wrong-size")
        if d[0] > 1:
            raise SSZError("boolean-not-0-or-1")
        return d[0] == 1

    def htr(self, v):
        return self.ser(v).ljust(CHUNK, b"\0")


class ByteVector(T):
    def __init__(self, n):
        self.n = n

    def size(self):
        return self.n

    def ser(self, v):
        if len(v) != self.n:
            raise SSZError("wrong-size")
        return bytes(v)

    def de(self, d):
        return self.ser(d)

    def htr(self, v):
        return merkleize(pack_bytes(bytes(v)), (self.n + 31) // 32)


class ByteList(T):
    def __init__(self, limit=None):
        self.limit = limit

    def fixed(self):
        return False

    def ser(self, v):
        return bytes(v)

    def de(self, d):
        if self.limit is not None and len(d) > self.limit:
            raise SSZError("over-limit")
        return bytes(d)

    def htr(self, v):
        c = pack_bytes(bytes(v))
        r = merkleize_progressive(c) if self.limit is None else merkleize(c, (self.limit + 31) // 32)
        return mix_length(r, len(v))


class BitVector(T):
    def __init__(self, n):
        self.n = n

    def size(self):
        return (self.n + 7) // 8

    def ser(self, v):
        b = bytearray(self.size())
        for i, x in enumerate(v):
            if x:
                b[i >> 3] |= 1 << (i & 7)
        return bytes(b)

    def de(self, d):
        if len(d) != self.size():
            raise SSZError("wrong-size")
        if self.n % 8 and d[-1] >> (self.n % 8):
            raise SSZError("bitvector-padding-nonzero")
        return [bool(d[i >> 3] >> (i & 7) & 1) for i in range(self.n)]

    def htr(self, v):
        return merkleize(pack_bits(v), (self.n + 255) // 256)


class BitList(T):
    def __init__(self, limit=None):
        self.limit = limit

    def fixed(self):
        return False

    def ser(self, v):
        n = len(v)
        b = bytearray(n // 8 + 1)
        for i, x in enumerate(v):
            if x:
                b[i >> 3] |= 1 << (i & 7)
        b[n >> 3] |= 1 << (n & 7)
        return bytes(b)

    def de(self, d):
        if not d:
            raise SSZError("bitlist-empty-encoding")
        if d[-1] == 0:
            raise SSZError("bitlist-no-sentinel")
        n = (len(d) - 1) * 8 + d[-1].bit_length() - 1
        if self.limit is not None and n > self.limit:
            raise SSZError("over-limit")
        return [bool(d[i >> 3] >> (i & 7) & 1) for i in range(n)]

    def htr(self, v):
        c = pack_bits(v)
        r = merkleize_progressive(c) if self.limit is None else merkleize(c, (self.limit + 255) // 256)
        return mix_length(r, len(v))


def _ser_parts(types, vals):
    fixed, var = [], []
    for t, v in zip(types, vals):
        b = t.ser(v)
        if t.fixed():
            fixed.append(b)
            var.append(b"")
        else:
            fixed.append(None)
            var.append(b)
    head = sum(OFFSET if f is None else len(f) for f in fixed)
    off, out = head, []
    for f, b in zip(fixed, var):
        if f is None:
            out.append(off.to_bytes(OFFSET, "little"))
            off += len(b)
        else:
            out.append(f)
    if off >= 1 << 32:
        raise SSZError("offset-overflow")
    return b"".join(out) + b"".join(var)


def _de_parts(types, d):
    """Decode a heterogeneous sequence with the offset rules of a container."""
    head = sum(t.size() if t.fixed() else OFFSET for t in types)
    if all(t.fixed() for t in types):
        if len(d) != head:
            raise SSZError("wrong-size")
    elif len(d) < head:
        raise SSZError("truncated")
    p, offs, out = 0, [], []
    for t in types:
        if t.fixed():
            out.append(t.de(d[p:p + t.size()]))
            p += t.size()
        else:
            offs.append((len(out), int.from_bytes(d[p:p + OFFSET], "little")))
            out.append(None)
            p += OFFSET
    if offs:
        if offs[0][1] != head:
            raise SSZError("first-offset-not-end-of-fixed-part")
        bounds = [o for _, o in offs] + [len(d)]
        for k, (i, o) in enumerate(offs):
            a, b = bounds[k], bounds[k + 1]
            if b < a:
                raise SSZError("offset-past-scope" if k == len(offs) - 1 else "offsets-not-monotonic")
            out[i] = types[i].de(d[a:b])
    return out


class Vector(T):
    def __init__(self, e, n):
        self.e, self.n = e, n

    @property
    def is_packed(self):
        return self.e.basic

    def fixed(self):
        return self.e.fixed()

    def size(self):
        return self.e.size() * self.n

    def ser(self, v):
        if len(v) != self.n:
            raise SSZError("wrong-count")
        return _ser_parts([self.e] * self.n, v)

    def de(self, d):
        return _de_parts([self.e] * self.n, d)

    def htr(self, v):
        if self.e.basic:
            return merkleize(pack_bytes(self.ser(v)), (self.n * self.e.size() + 31) // 32)
        return merkleize([self.e.htr(x) for x in v], self.n)


class List(T):
    def __init__(self, e, limit=None):
        self.e, self.limit = e, limit

    def fixed(self):
        return False

    def ser(self, v):
        return _ser_parts([self.e] * len(v), v)

    def _check(self, n):
        if self.limit is not None and n > self.limit:
            raise SSZError("over-limit")

    def de(self, d):
        if self.e.fixed():
            s = self.e.size()
            if len(d) % s:
                raise SSZError("not-a-multiple-of-element-size")
            self._check(len(d) // s)
            return [self.e.de(d[i:i + s]) for i in range(0, len(d), s)]
        if not d:
            return []
        if len(d) < OFFSET:
            raise SSZError("truncated")
        first = int.from_bytes(d[:OFFSET], "little")
        if first == 0 or first % OFFSET:
            raise SSZError("first-offset-not-end-of-fixed-part")
        if first > len(d):
            raise SSZError("offset-past-scope")
        n = first // OFFSET
        self._check(n)
        return _de_parts([self.e] * n, d)

    def htr(self, v):
        if self.e.basic:
            c = pack_bytes(self.ser(v))
            if self.limit is None:
                r = merkleize_progressive(c)
            else:
                r = merkleize(c, (self.limit * self.e.size() + 31) // 32)
        else:
            c = [self.e.htr(x) for x in v]
            r = merkleize_progressive(c) if self.limit is None else merkleize(c, self.limit)
        return mix_length(r, len(v))


class Container(T):
    def __init__(self, name, fields):
        self.name, self.fields = name, fields
        self.types = [t for _, t in fields]

    def fixed(self):
        return all(t.fixed() for t in self.types)

    def size(self):
        return sum(t.size() for t in self.types)

    def ser(self, v):
        return _ser_parts(self.types, [v[k] for k, _ in self.fields])

    def de(self, d):
        return dict(zip([k for k, _ in self.fields], _de_parts(self.types, d)))

    def htr(self, v):
        return merkleize([t.htr(v[k]) for k, t in self.fields], len(self.fields))

    def field_offset(self, name):
        """Byte offset of a field inside the fixed part."""
        p = 0
        for k, t in self.fields:
            if k == name:
                return p
            p += t.size() if t.fixed() else OFFSET
        raise KeyError(name)


class ProgressiveContainer(Container):
    """Serialises like a Container over its active fields (EIP-7495)."""

    def __init__(self, name, active, fields):
        super().__init__(name, fields)
        if sum(active) != len(fields) or not active or active[-1] != 1:
            raise SSZError("bad-active-fields")
        self.active = active

    def htr(self, v):
        it = iter(self.fields)
        leaves = []
        for bit in self.active:
            if bit:
                k, t = next(it)
                leaves.append(t.htr(v[k]))
            else:
                leaves.append(ZERO[0])
        word = sum(1 << i for i, b in enumerate(self.active) if b).to_bytes(CHUNK, "little")
        return H(merkleize_progressive(leaves), word)


class CompatibleUnion(T):
    """One selector byte, then the option (EIP-8016)."""

    def __init__(self, options):
        self.options = options

    def fixed(self):
        return False

    def ser(self, v):
        s, x = v
        return bytes([s]) + self.options[s].ser(x)

    def de(self, d):
        if not d:
            raise SSZError("union-no-selector")
        if d[0] not in self.options:
            raise SSZError("union-unknown-selector")
        return d[0], self.options[d[0]].de(d[1:])

    def htr(self, v):
        s, x = v
        return H(self.options[s].htr(x), s.to_bytes(CHUNK, "little"))


Uint8, Uint16, Uint32, Uint64, Uint128, Uint256 = (Uint(b) for b in (8, 16, 32, 64, 128, 256))
Bytes20, Bytes32, Bytes48, Bytes96 = (ByteVector(n) for n in (20, 32, 48, 96))


def ProgressiveList(e):
    return List(e, None)


ProgressiveByteList = ByteList(None)
ProgressiveBitList = BitList(None)
