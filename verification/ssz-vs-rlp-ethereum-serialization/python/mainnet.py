"""Load the pinned mainnet block and rebuild its RLP objects from JSON-RPC data."""
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import beacon_types as B  # noqa: E402
import rlp_codec as R  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"


def hx(s):
    s = s[2:]
    return bytes.fromhex(s if len(s) % 2 == 0 else "0" + s)


def qty(s):
    return int(s, 16)


def load():
    raw = gzip.open(DATA / "signed_beacon_block.ssz.gz").read()
    el = json.load(gzip.open(DATA / "el_block.json.gz"))["result"]
    rc = json.load(gzip.open(DATA / "el_receipts.json.gz"))["result"]
    hdr = json.load(open(DATA / "beacon_header.json"))["data"]
    return raw, B.SignedBeaconBlock.de(raw), el, rc, hdr


def el_header(b):
    return [hx(b["parentHash"]), hx(b["sha3Uncles"]), hx(b["miner"]), hx(b["stateRoot"]),
            hx(b["transactionsRoot"]), hx(b["receiptsRoot"]), hx(b["logsBloom"]),
            qty(b["difficulty"]), qty(b["number"]), qty(b["gasLimit"]), qty(b["gasUsed"]),
            qty(b["timestamp"]), hx(b["extraData"]), hx(b["mixHash"]), hx(b["nonce"]),
            qty(b["baseFeePerGas"]), hx(b["withdrawalsRoot"]), qty(b["blobGasUsed"]),
            qty(b["excessBlobGas"]), hx(b["parentBeaconBlockRoot"]), hx(b["requestsHash"])]


def rlp_withdrawal(w):
    return [w["index"], w["validator_index"], w["address"], w["amount"]]


def rlp_receipt(r):
    body = [qty(r["status"]), qty(r["cumulativeGasUsed"]), hx(r["logsBloom"]),
            [[hx(l["address"]), [hx(t) for t in l["topics"]], hx(l["data"])] for l in r["logs"]]]
    t = qty(r["type"])
    e = R.encode(body)
    return e if t == 0 else bytes([t]) + e


def eip2718_body(tx):
    """The form a transaction takes inside the block body list: raw item for legacy,
    byte string for typed."""
    return R.decode(tx) if tx[0] >= 0xC0 else tx
