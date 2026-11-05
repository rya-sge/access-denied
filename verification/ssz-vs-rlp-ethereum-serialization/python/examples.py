"""Print every byte-level example quoted in the article."""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import beacon_types as B  # noqa: E402
import rlp_codec as R  # noqa: E402
import ssz_codec as S  # noqa: E402
from keccak import keccak256  # noqa: E402
from mainnet import load, rlp_withdrawal  # noqa: E402
from ssz_codec import (BitList, BitVector, Boolean, ByteList, ByteVector, Container, List,  # noqa: E402
                       Uint8, Uint16, Uint32, Uint64, Vector)


def title(s):
    print("\n## " + s)


title("RLP rules")
for label, v in [("empty string", b""), ("integer 0", 0), ("byte 0x00", b"\x00"), ("integer 15", 15),
                 ("byte 0x7f", b"\x7f"), ("byte 0x80", b"\x80"), ("integer 1024", 1024),
                 ('"dog"', b"dog"), ("empty list", []), ('["cat","dog"]', [b"cat", b"dog"]),
                 ("[[],[[]],[[],[[]]]]", [[], [[]], [[], [[]]]])]:
    print(f"{label:24} {R.encode(v).hex()}")
for n in (55, 56, 1024):
    e = R.encode(b"\xaa" * n)
    print(f"string of {n:<5} bytes -> prefix {e[:len(e)-n].hex()}")
e = R.encode([b"\xaa"] * 0 + [b"\xaa" * 54])
print(f"list with 55 byte payload -> prefix {e[:1].hex()}")
e = R.encode([b"\xaa" * 55])
print(f"list with 56 byte payload -> prefix {e[:2].hex()}")

title("RLP carries no type: one encoding, three readings")
b = R.encode(1024)
d = R.decode(b)
print(f"bytes {b.hex()} decode to {d.hex()}: integer {int.from_bytes(d,'big')}, "
      f"bytes 0x{d.hex()}, or text {d!r}")
print("rlp(0) == rlp(b'') == rlp(False):", R.encode(0) == R.encode(b"") == R.encode(False), R.encode(0).hex())

raw, sb, el, rc, hdr = load()
w = sb["message"]["body"]["execution_payload"]["withdrawals"][0]
title("One real withdrawal, block " + str(sb["message"]["body"]["execution_payload"]["block_number"]))
print("index", w["index"], "validator", w["validator_index"], "address 0x" + w["address"].hex(),
      "amount (gwei)", w["amount"])
r = R.encode(rlp_withdrawal(w))
s = B.Withdrawal.ser(w)
print(f"RLP {len(r)} bytes: {r.hex()}")
p = 1 if r[0] < 0xF8 else 1 + r[0] - 0xF7
print(f"  list prefix {r[:p].hex()}")
q = p
for name in ("index", "validator_index", "address", "amount"):
    _, st, en = R._read_header(r, q, len(r))
    print(f"  {name:16} prefix {r[q:st].hex() or '-':4} payload {r[st:en].hex()}")
    q = en
print(f"SSZ {len(s)} bytes: {s.hex()}")
for name, off, n in (("index", 0, 8), ("validator_index", 8, 8), ("address", 16, 20), ("amount", 36, 8)):
    print(f"  offset {off:2} {name:16} {s[off:off+n].hex()}")

title("Variable-size layout")
Foo = Container("Foo", [("a", Uint16), ("b", List(Uint16, 4)), ("c", Uint8), ("d", List(Uint8, 8))])
v = {"a": 0x1234, "b": [1, 2], "c": 0xff, "d": [0xaa, 0xbb, 0xcc]}
e = Foo.ser(v)
print("SSZ", len(e), e.hex())
print("  a", e[0:2].hex(), "| off(b)", e[2:6].hex(), "| c", e[6:7].hex(), "| off(d)", e[7:11].hex(),
      "| b", e[11:15].hex(), "| d", e[15:].hex())
r2 = R.encode([0x1234, [1, 2], 0xff, [0xaa, 0xbb, 0xcc]])
print("RLP same values", len(r2), r2.hex())
print("real block: first 4 bytes of SignedBeaconBlock", raw[:4].hex(), "=", int.from_bytes(raw[:4], "little"),
      "(4 + 96 fixed bytes, the message starts there)")

title("Vectors, lists, fixed and variable")
print("Vector[Uint16,4](1,2,3,4)", Vector(Uint16, 4).ser([1, 2, 3, 4]).hex())
print("Vector[Uint8,8](1,0,2,0,3,0,4,0)", Vector(Uint8, 8).ser([1, 0, 2, 0, 3, 0, 4, 0]).hex())
print("List[Uint16,4](1,2,3,4)", List(Uint16, 4).ser([1, 2, 3, 4]).hex())
print("root Vector[Uint16,4]", Vector(Uint16, 4).htr([1, 2, 3, 4]).hex())
print("root Vector[Uint8,8] ", Vector(Uint8, 8).htr([1, 0, 2, 0, 3, 0, 4, 0]).hex())
print("root List[Uint16,4]  ", List(Uint16, 4).htr([1, 2, 3, 4]).hex())
print("root List[Uint16,8]  ", List(Uint16, 8).htr([1, 2, 3, 4]).hex())
print("root List[Uint16,64] ", List(Uint16, 64).htr([1, 2, 3, 4]).hex())
print("Vector[List[Uint8,3],4]", Vector(List(Uint8, 3), 4).ser([[1, 2], [3, 4, 5], [], [6]]).hex())

title("Bitfields")
print("BitVector[5](1,0,1,0,1)", BitVector(5).ser([1, 0, 1, 0, 1]).hex())
print("Vector[Boolean,5]      ", Vector(Boolean(), 5).ser([1, 0, 1, 0, 1]).hex())
print("BitList[8](1,0,1)      ", BitList(8).ser([True, False, True]).hex())
print("BitList[8](0,0,0)      ", BitList(8).ser([False] * 3).hex())
print("BitList[8](eight 0)    ", BitList(8).ser([False] * 8).hex())
print("BitVector[8](eight 0)  ", BitVector(8).ser([False] * 8).hex())
ab = sb["message"]["body"]["attestations"][0]
abits = B.Attestation.fields[0][1].ser(ab["aggregation_bits"])
print("real attestation 0: aggregation_bits", len(ab["aggregation_bits"]), "bits,", len(abits), "bytes, set",
      sum(ab["aggregation_bits"]), "last byte", abits[-1:].hex(), "committee_bits set", sum(ab["committee_bits"]))
print("real sync aggregate bits set", sum(sb["message"]["body"]["sync_aggregate"]["sync_committee_bits"]), "of 512,",
      "64 bytes")

title("hash_tree_root of the real withdrawal, step by step")
c = [Uint64.htr(w["index"]), Uint64.htr(w["validator_index"]), B.Bytes20.htr(w["address"]), Uint64.htr(w["amount"])]
for name, x in zip(("index", "validator_index", "address", "amount"), c):
    print(f"  chunk {name:16} {x.hex()}")
h01 = hashlib.sha256(c[0] + c[1]).digest()
h23 = hashlib.sha256(c[2] + c[3]).digest()
root = hashlib.sha256(h01 + h23).digest()
print("  h(c0,c1)", h01.hex())
print("  h(c2,c3)", h23.hex())
print("  root    ", root.hex())
print("  codec root equal:", B.Withdrawal.htr(w) == root)
print("  sha256(ssz bytes)   ", hashlib.sha256(s).hexdigest())
print("  keccak256(rlp bytes)", keccak256(r).hex())

title("Summary and expansion, on the real block")
body_root = B.BeaconBlockBody.htr(sb["message"]["body"])
hd = dict(sb["message"])
del hd["body"]
hd["body_root"] = body_root
print("BeaconBlockHeader root equals BeaconBlock root:",
      B.BeaconBlockHeader.htr(hd) == B.BeaconBlock.htr(sb["message"]), B.BeaconBlockHeader.htr(hd).hex())
print("header bytes", len(B.BeaconBlockHeader.ser(hd)), "block bytes", len(B.BeaconBlock.ser(sb["message"])))


def verdict(f):
    try:
        return "accepted: " + repr(f())
    except (R.RLPError, S.SSZError) as e:
        return "refused: " + e.code


title("RLP decoder strictness")
for hx, why in [("8105", "0x05 written with a prefix"), ("b80105", "long form for a short string"),
                ("b8000000", "length byte zero"), ("b90038" + "aa" * 56, "length with a leading zero"),
                ("c26401", "well formed list, shown for contrast"),
                ("c2640102", "one byte after the list ends"), ("83646f", "string shorter than announced"),
                ("c4640102", "list overruns input"), ("f800", "long form for empty list"),
                ("8000", "extra byte after an empty string")]:
    print(f"{hx[:18]:20} {why:38} {verdict(lambda: R.decode(bytes.fromhex(hx)))}")
for hx in ("820400", "820004", "00", "80"):
    print(f"as integer {hx:12} {verdict(lambda: R.to_int(R.decode(bytes.fromhex(hx))))}")

title("SSZ decoder strictness, type {a: Uint16, b: List[Uint8,4]}")
T = Container("T", [("a", Uint16), ("b", List(Uint8, 4))])
good = T.ser({"a": 1, "b": [7, 8]})
print("good", good.hex())
for hx, why in [(good.hex(), "canonical"), ("0100" + "07000000" + "000708", "first offset past end of fixed part"),
                ("0100" + "05000000" + "0708", "first offset inside the fixed part"),
                ("0100" + "0600", "truncated offset"),
                ("0100" + "06000000" + "0102030405", "list above its limit")]:
    print(f"{hx:26} {why:38} {verdict(lambda: T.de(bytes.fromhex(hx)))}")
print(f"{'02':26} {'Boolean byte other than 0 or 1':38} {verdict(lambda: Boolean().de(bytes.fromhex('02')))}")
print(f"{'0500':26} {'BitList with no sentinel':38} {verdict(lambda: BitList(16).de(bytes.fromhex('0500')))}")
print(f"{'e0':26} {'BitVector[5] padding bits set':38} {verdict(lambda: BitVector(5).de(bytes.fromhex('e0')))}")
print(f"{'0100ff':26} {'Uint16 with a spare byte':38} {verdict(lambda: Uint16.de(bytes.fromhex('0100ff')))}")
TT = Container("TT", [("x", List(Uint8, 4)), ("y", List(Uint8, 4))])
print("two-list type {x: List[Uint8,4], y: List[Uint8,4]}, canonical", TT.ser({"x": [0xaa], "y": [0xbb]}).hex())
print(f"{'0800000007000000aabb':26} {'offsets out of order':38} {verdict(lambda: TT.de(bytes.fromhex('0800000007000000aabb')))}")
print(f"{'0800000011000000aabb':26} {'last offset past the end':38} {verdict(lambda: TT.de(bytes.fromhex('0800000011000000aabb')))}")
