"""Recursive Length Prefix: encoder and strict decoder, standard library only.

The decoder follows ethereum-rlp `decode` and go-ethereum `rlp` on what it rejects.
Each rejection carries a reason code so the strictness table can be printed from a run.
"""


class RLPError(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def int_to_be(n: int) -> bytes:
    if n < 0:
        raise RLPError("negative-integer")
    return b"" if n == 0 else n.to_bytes((n.bit_length() + 7) // 8, "big")


def _length_prefix(n: int, short: int, long_: int) -> bytes:
    if n < 56:
        return bytes([short + n])
    be = int_to_be(n)
    return bytes([long_ + len(be)]) + be


def encode(x) -> bytes:
    if isinstance(x, bool):
        return encode(1 if x else 0)
    if isinstance(x, int):
        return encode(int_to_be(x))
    if isinstance(x, str):
        return encode(x.encode())
    if isinstance(x, (bytes, bytearray)):
        b = bytes(x)
        if len(b) == 1 and b[0] < 0x80:
            return b
        return _length_prefix(len(b), 0x80, 0xB7) + b
    if isinstance(x, (list, tuple)):
        body = b"".join(encode(i) for i in x)
        return _length_prefix(len(body), 0xC0, 0xF7) + body
    raise TypeError(type(x))


def _read_header(d: bytes, i: int, end: int):
    """Return (is_list, payload_start, payload_end) for the item at d[i]."""
    if i >= end:
        raise RLPError("empty-input")
    b0 = d[i]
    if b0 < 0x80:
        return False, i, i + 1
    if b0 <= 0xB7:
        n = b0 - 0x80
        s = i + 1
        if s + n > end:
            raise RLPError("truncated")
        if n == 1 and d[s] < 0x80:
            raise RLPError("single-byte-with-prefix")
        return False, s, s + n
    if b0 <= 0xBF:
        return _long(d, i, end, b0 - 0xB7, False)
    if b0 <= 0xF7:
        n = b0 - 0xC0
        s = i + 1
        if s + n > end:
            raise RLPError("truncated")
        return True, s, s + n
    return _long(d, i, end, b0 - 0xF7, True)


def _long(d, i, end, ll, is_list):
    s = i + 1 + ll
    if s > end:
        raise RLPError("truncated")
    if d[i + 1] == 0:
        raise RLPError("length-leading-zero")
    n = int.from_bytes(d[i + 1:s], "big")
    if n < 56:
        raise RLPError("long-form-for-short-payload")
    if s + n > end:
        raise RLPError("truncated")
    return is_list, s, s + n


def _decode_at(d, i, end):
    is_list, s, e = _read_header(d, i, end)
    if not is_list:
        return d[s:e], e
    items, p = [], s
    while p < e:
        item, p = _decode_at(d, p, e)
        items.append(item)
    return items, e


def decode(d: bytes):
    """Decode exactly one item. Returns bytes or a nested list of bytes."""
    item, e = _decode_at(d, 0, len(d))
    if e != len(d):
        raise RLPError("trailing-bytes")
    return item


def to_int(b) -> int:
    """Typed step: RLP itself has no integers, the schema decides."""
    if not isinstance(b, (bytes, bytearray)):
        raise RLPError("expected-string")
    if len(b) > 0 and b[0] == 0:
        raise RLPError("integer-leading-zero")
    return int.from_bytes(b, "big")
