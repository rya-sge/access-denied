"""Cross-check the two codecs against upstream vectors.

RLP: ethereum/tests RLPTests (rlptest.json, invalidRLPTest.json) and the table of
go-ethereum rlp/decode_test.go cases transcribed in GETH_CASES.
SSZ: the reference tests of ethereum/ssz-specs v0.1.0, plus examples of the
Upgrading Ethereum book. Every SSZ vector is decoded, re-encoded byte for byte and
rooted. Every rejection vector must be refused.
"""
import json
import random
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python3 -I drops the script directory

import rlp_codec as R
import ssz_codec as S
from keccak import keccak256
from ssz_codec import (BitList, BitVector, ByteList, ByteVector, Boolean, CompatibleUnion, Container,
                       List, ProgressiveBitList, ProgressiveContainer, ProgressiveList, Uint8, Uint16,
                       Uint32, Uint64, Uint128, Uint256, Vector, Bytes32)

ROOT = Path(__file__).resolve().parent.parent
fails = 0


def ok(cond, what):
    global fails
    if not cond:
        fails += 1
        print("FAIL", what)


def rlp_input(v):
    if isinstance(v, str) and v.startswith("#"):
        return int(v[1:])
    if isinstance(v, list):
        return [rlp_input(x) for x in v]
    return v


def check_rlp():
    d = json.load(open(ROOT / "vectors/rlptest.json"))
    n = 0
    for name, t in d.items():
        out = bytes.fromhex(t["out"][2:] if t["out"].startswith("0x") else t["out"])
        ok(R.encode(rlp_input(t["in"])) == out, "rlptest enc " + name)
        ok(R.encode(R.decode(out)) == out, "rlptest roundtrip " + name)
        n += 1
    print(f"RLP rlptest.json: {n} vectors, encode and round trip")
    d = json.load(open(ROOT / "vectors/invalidRLPTest.json"))
    n = 0
    for name, t in d.items():
        h = t["out"]
        h = h[2:] if h.startswith("0x") else h
        try:
            bytes.fromhex(h)
        except ValueError:
            print("  skipped, not hex:", name)
            continue
        raised = False
        try:
            R.decode(bytes.fromhex(h))
        except R.RLPError:
            raised = True
        ok(raised, "invalidRLP accepted " + name)
        n += 1
    print(f"RLP invalidRLPTest.json: {n} vectors, all refused")
    # go-ethereum rlp/decode_test.go: (hex input, kind, expected)
    n = 0
    for hx, kind, exp in GETH_CASES:
        b = bytes.fromhex(hx)
        try:
            v = R.decode(b)
            if kind == "uint":
                v = R.to_int(v)
            ok(exp is not None and v == exp, f"geth {hx} gave {v!r}")
        except R.RLPError as e:
            ok(exp is None, f"geth {hx} refused {e.code}")
        n += 1
    print(f"RLP go-ethereum decode table: {n} cases")


GETH_CASES = [
    ("05", "uint", 5), ("80", "uint", 0), ("820505", "uint", 0x0505),
    ("83050505", "uint", 0x050505), ("8405050505", "uint", 0x05050505),
    ("00", "uint", None), ("8105", "uint", None), ("820004", "uint", None),
    ("B8020004", "uint", None),
    ("C0", "any", []), ("C80102030405060708", "any", [bytes([i]) for i in range(1, 9)]),
    ("F8020102", "any", None), ("C101", "any", [b"\x01"]),
    ("8D6162636465666768696A6B6C6D", "any", b"abcdefghijklm"),
    ("B90006", "any", None), ("B800", "any", None),
    ("8180", "any", b"\x80"), ("C8", "any", None),
]


def t(d, name):
    return d[name]


def registry():
    r = {}
    r.update({"Uint8": Uint8, "Uint16": Uint16, "Uint32": Uint32, "Uint64": Uint64,
              "Uint128": Uint128, "Uint256": Uint256, "Boolean": Boolean(),
              "Bytes4": ByteVector(4), "Bytes32": Bytes32, "Bytes52": ByteVector(52),
              "Bytes64": ByteVector(64), "ByteList512KiB": ByteList(LIMIT_512K),
              "SampleBitVector8": BitVector(8), "SampleBitVector64": BitVector(64),
              "SampleBitList16": BitList(16), "SampleUint16Vector3": Vector(Uint16, 3),
              "SampleUint64Vector4": Vector(Uint64, 4), "SampleUint32List16": List(Uint32, 16),
              "SampleBytes32List8": List(Bytes32, 8), "SmokeBitList8": BitList(8),
              "ProgressiveBitList": ProgressiveBitList,
              "BoundaryBitList256": BitList(256), "BoundaryUint64List32": List(Uint64, 32)})
    for n in (1, 7, 9, 255, 256, 257):
        r[f"BoundaryBitVector{n}"] = BitVector(n)
    u64p = ProgressiveList(Uint64)
    u16p = ProgressiveList(Uint16)
    b32p = ProgressiveList(Bytes32)
    u16l4 = List(Uint16, 4)
    sq = ProgressiveContainer("SampleSquare", [1, 0, 1], [("side", Uint16), ("color", Uint8)])
    ci = ProgressiveContainer("SampleCircle", [0, 1, 1], [("radius", Uint16), ("color", Uint8)])
    sqp = ProgressiveList(sq)
    cip = ProgressiveList(ci)
    shape = CompatibleUnion({1: sq, 2: ci, 127: sq})
    r.update({
        "SampleUint64ProgressiveList": u64p, "SampleBytes32ProgressiveList": b32p,
        "SampleNestedProgressiveList": ProgressiveList(u16p),
        "SampleContainerWithProgressiveList": Container("C", [("a", Uint16), ("b", u64p), ("c", Uint8)]),
        "SampleSquare": sq, "SampleCircle": ci, "SampleSquareProgressiveList": sqp,
        "SampleOneField": ProgressiveContainer("O", [1], [("a", Uint16)]),
        "SampleLeadingGaps": ProgressiveContainer("L", [0, 0, 1], [("c", Uint32)]),
        "SampleMultipleGaps": ProgressiveContainer("M", [1, 0, 0, 1, 0, 1],
                                                   [("a", Uint8), ("b", Uint16), ("c", Uint32)]),
        "SampleWidestLayout": ProgressiveContainer("W", [0] * 255 + [1], [("tail", Uint8)]),
        "SampleLevelBoundary": ProgressiveContainer("B", [1] + [0] * 20 + [1],
                                                    [("first", Uint16), ("last", Uint8)]),
        "SampleBoundedListField": ProgressiveContainer("BL", [1, 0, 1], [("head", Uint64), ("body", u16l4)]),
        "SampleProgressiveFields": ProgressiveContainer(
            "PF", [1, 1, 1], [("head", Uint64), ("numbers", u64p), ("flags", ProgressiveBitList)]),
        "SampleOuterShape": ProgressiveContainer(
            "OS", [1, 0, 1], [("head", Uint8), ("inner", ProgressiveContainer(
                "IS", [1, 0, 1], [("x", Uint16), ("y", Uint8)]))]),
        "SampleShape": shape, "SampleNumbers": CompatibleUnion({1: u16l4, 2: u16l4}),
        "SampleEmptyProne": CompatibleUnion({1: sqp, 2: cip}),
        "SampleNestedShape": CompatibleUnion({1: shape, 2: CompatibleUnion({5: sq})}),
        "SampleShapeContainer": Container("SC", [("tag", Uint64), ("body", shape)]),
        "SampleShapeProgressiveContainer": ProgressiveContainer(
            "SPC", SHAPE_PC_ACTIVE, [("tag", Uint64), ("body", shape)]),
        "SampleShapeProgressiveList": ProgressiveList(shape),
    })
    return r


LIMIT_512K = 512 * 1024
SHAPE_PC_ACTIVE = [1, 0, 1]


def check_ssz():
    reg = registry()
    tar = tarfile.open(ROOT / "vectors/ssz-test-vectors-v0.1.0.tar.gz")
    n_ok = n_rej = 0
    missing = {}
    for m in tar.getmembers():
        if not m.name.endswith(".json"):
            continue
        for tid, v in json.load(tar.extractfile(m)).items():
            name = v["typeName"]
            if name not in reg:
                missing[name] = missing.get(name, 0) + 1
                continue
            ty = reg[name]
            if name == "SampleShapeContainer" and "test_progressive_containers" in tid:
                # the name is defined twice upstream, with a different shape in this file
                ty = Container("SC2", [("a", Uint8), ("square", reg["SampleSquare"])])
            if "rejectionReason" in v:
                raised = False
                try:
                    ty.de(bytes.fromhex(v["rawBytes"][2:]))
                except S.SSZError:
                    raised = True
                ok(raised, "SSZ accepted " + tid)
                n_rej += 1
                continue
            b = bytes.fromhex(v["serialized"][2:])
            try:
                x = ty.de(b)
            except S.SSZError as e:
                ok(False, f"SSZ refused {tid} {name} {e.code} {v['serialized'][:40]}")
                continue
            ok(ty.ser(x) == b, "SSZ reserialise " + tid)
            ok("0x" + ty.htr(x).hex() == v["root"], "SSZ root " + tid)
            n_ok += 1
    print(f"SSZ ssz-specs v0.1.0: {n_ok} valid vectors (decode, re-encode, root), "
          f"{n_rej} rejection vectors, types not mapped: {missing or 'none'}")


def check_book():
    Baz = Container("Baz", [("x", Uint8), ("y", List(Uint8, 10)), ("z", Uint8)])
    ok(Baz.ser({"x": 1, "y": [2, 3], "z": 4}).hex() == "0106000000040203", "book Baz")
    vl = Vector(List(Uint8, 3), 4)
    ok(vl.ser([[1, 2], [3, 4, 5], [], [6]]).hex() ==
       "10000000120000001500000015000000010203040506", "book Vector[List]")
    ok(BitList(100).ser([False] * 3).hex() == "08", "book bitlist")
    ok(BitList(8).ser([False] * 8).hex() == "0001", "book bitlist full byte")
    ok(BitVector(5).ser([1, 0, 1, 0, 1]).hex() == "15", "book bitvector")
    a = b"".join(i.to_bytes(32, "little") for i in (1, 2, 3, 4))
    ch = [a[i:i + 32] for i in range(0, 128, 32)]
    ok(S.merkleize(ch).hex() ==
       "bfe3c665d2e561f13b30606c580cb703b2041287e212ade110f0bfd8563e21bb", "book merkleize 4")
    ok(S.merkleize(ch[:3]).hex() ==
       "66c419026fee8793be7fd0011b9db46b98a79f9c9b640e25317865c358f442db", "book merkleize 3")
    ok(S.merkleize(ch[:1], 4).hex() ==
       "553c8ccfd20bb4db224b1ae47359e9968a5c8098c15d8bf728b19e55749c773b", "book merkleize limit")
    print("SSZ book examples: 8 checked")


def check_keccak():
    ok(keccak256(b"").hex() ==
       "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470", "keccak empty")
    ok(keccak256(R.encode([])).hex() ==
       "1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347", "keccak rlp([])")
    ok(keccak256(R.encode(b"")).hex() ==
       "56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421", "empty trie root")
    print("keccak256: 3 known digests")


def fuzz():
    rng = random.Random(20261104)
    acc = 0
    for _ in range(200000):
        n = rng.randrange(1, 14)
        b = bytes(rng.choice((rng.randrange(256), 0x80, 0xB8, 0xC0, 0xF8, 0, 1, 2))
                  for _ in range(n))
        try:
            v = R.decode(b)
        except R.RLPError:
            continue
        acc += 1
        ok(R.encode(v) == b, "RLP non-injective " + b.hex())
    print(f"RLP fuzz: 200000 inputs, {acc} accepted, all re-encode to the same bytes")
    ty = Container("F", [("a", Uint16), ("b", List(Uint8, 8)), ("c", BitList(16)),
                         ("d", List(List(Uint8, 4), 4)), ("e", Boolean())])
    base = ty.ser({"a": 7, "b": [1, 2], "c": [True, False], "d": [[1], [2, 3]], "e": True})
    acc = 0
    for _ in range(200000):
        b = bytearray(base)
        for _ in range(rng.randrange(1, 4)):
            i = rng.randrange(len(b))
            b[i] = rng.choice((0, 1, 2, 11, 12, 13, 14, 15, 16, 17, 18, 255, rng.randrange(256)))
        b = bytes(b[:rng.randrange(len(b) + 1)] if rng.random() < 0.2 else b)
        try:
            v = ty.de(b)
        except S.SSZError:
            continue
        acc += 1
        ok(ty.ser(v) == b, "SSZ non-injective " + b.hex())
    print(f"SSZ fuzz: 200000 mutated inputs, {acc} accepted, all re-encode to the same bytes")


if __name__ == "__main__":
    check_keccak()
    check_rlp()
    check_ssz()
    check_book()
    fuzz()
    print("FAILURES:", fails)
    sys.exit(1 if fails else 0)
