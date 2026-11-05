"""The EIP-6404 (Draft) SSZ form of a transaction, from its signed RLP bytes.

Read from EIP-6404 at the pinned EIPs commit. No upstream vector exists for this
conversion, so its output is a reading of a Draft, used for sizes and gas only.
"""
from rlp_codec import decode, to_int
from ssz_codec import (Bytes20, Bytes32, CompatibleUnion, Container, ProgressiveByteList,
                       ProgressiveContainer, ProgressiveList, Uint8, Uint64, Uint256)

Basic = ProgressiveContainer("BasicFeesPerGas", [1], [("regular", Uint256)])
Blob = ProgressiveContainer("BlobFeesPerGas", [1, 1], [("regular", Uint256), ("blob", Uint256)])
AccessTuple = Container("AccessTuple", [("address", Bytes20), ("storage_keys", ProgressiveList(Bytes32))])
AccessList = ProgressiveList(AccessTuple)
Sig = ProgressiveByteList

C = [("type_", Uint8), ("chain_id", Uint256), ("nonce", Uint64)]
F = [("max_fees_per_gas", Basic), ("gas", Uint64)]
TO = [("to", Bytes20)]
V = [("value", Uint256), ("input_", ProgressiveByteList)]
A = [("access_list", AccessList)]
P = [("max_priority_fees_per_gas", Basic)]

LegRB = ProgressiveContainer("RlpLegacyReplayableBasic", [1, 0, 1, 1, 1, 1, 1, 1],
                             [("type_", Uint8), ("nonce", Uint64)] + F + TO + V)
LegRC = ProgressiveContainer("RlpLegacyReplayableCreate", [1, 0, 1, 1, 1, 0, 1, 1],
                             [("type_", Uint8), ("nonce", Uint64)] + F + V)
LegB = ProgressiveContainer("RlpLegacyBasic", [1] * 8, C + F + TO + V)
LegC = ProgressiveContainer("RlpLegacyCreate", [1, 1, 1, 1, 1, 0, 1, 1], C + F + V)
AclB = ProgressiveContainer("RlpAccessListBasic", [1] * 9, C + F + TO + V + A)
AclC = ProgressiveContainer("RlpAccessListCreate", [1, 1, 1, 1, 1, 0, 1, 1, 1], C + F + V + A)
FeeB = ProgressiveContainer("RlpBasic", [1] * 10, C + F + TO + V + A + P)
FeeC = ProgressiveContainer("RlpCreate", [1, 1, 1, 1, 1, 0, 1, 1, 1, 1], C + F + V + A + P)
BlobTx = ProgressiveContainer("RlpBlob", [1] * 11,
                              C + [("max_fees_per_gas", Blob), ("gas", Uint64)] + TO + V + A + P +
                              [("blob_versioned_hashes", ProgressiveList(Bytes32))])
AuthR = ProgressiveContainer("RlpReplayableBasicAuthorization", [1, 0, 1, 1],
                             [("magic", Uint8), ("address", Bytes20), ("nonce", Uint64)])
AuthB = ProgressiveContainer("RlpBasicAuthorization", [1, 1, 1, 1],
                             [("magic", Uint8), ("chain_id", Uint256), ("address", Bytes20),
                              ("nonce", Uint64)])
AuthPayload = CompatibleUnion({1: AuthR, 2: AuthB})
Auth = Container("RlpSetCodeAuthorization", [("payload", AuthPayload), ("signature", Sig)])
SetCode = ProgressiveContainer("RlpSetCode", [1] * 10 + [0, 1],
                               C + F + TO + V + A + P + [("authorization_list", ProgressiveList(Auth))])
Payload = CompatibleUnion({1: LegRB, 2: LegRC, 3: LegB, 4: LegC, 5: AclB, 6: AclC,
                           7: FeeB, 8: FeeC, 9: BlobTx, 10: SetCode})
Transaction = Container("Transaction", [("payload", Payload), ("signature", Sig)])


def _sig(yp, r, s):
    return b"\x00" + to_int(r).to_bytes(32, "big") + to_int(s).to_bytes(32, "big") + bytes([yp])


def _al(al):
    return [{"address": a, "storage_keys": list(k)} for a, k in al]


def convert(raw: bytes):
    """Return the Transaction value for signed bytes `raw` (legacy or EIP-2718 typed)."""
    if raw[0] >= 0xC0:
        f = decode(raw)
        nonce, price, gas, to, value, data, v, r, s = f
        v = to_int(v)
        common = {"type_": 0, "nonce": to_int(nonce), "max_fees_per_gas": {"regular": to_int(price)},
                  "gas": to_int(gas), "value": to_int(value), "input_": data}
        if v in (27, 28):
            yp = v - 27
            sel = 1 if to else 2
        else:
            chain = (v - 35) >> 1
            yp = v - 35 - 2 * chain
            common["chain_id"] = chain
            sel = 3 if to else 4
        if to:
            common["to"] = to
        return {"payload": (sel, common), "signature": _sig(yp, r, s)}
    t = raw[0]
    f = decode(raw[1:])
    if t == 1:
        chain, nonce, price, gas, to, value, data, al, yp, r, s = f
        p = {"type_": 1, "chain_id": to_int(chain), "nonce": to_int(nonce),
             "max_fees_per_gas": {"regular": to_int(price)}, "gas": to_int(gas),
             "value": to_int(value), "input_": data, "access_list": _al(al)}
        sel = 5
    elif t == 2:
        chain, nonce, prio, maxfee, gas, to, value, data, al, yp, r, s = f
        p = {"type_": 2, "chain_id": to_int(chain), "nonce": to_int(nonce),
             "max_fees_per_gas": {"regular": to_int(maxfee)}, "gas": to_int(gas),
             "value": to_int(value), "input_": data, "access_list": _al(al),
             "max_priority_fees_per_gas": {"regular": to_int(prio)}}
        sel = 7
    elif t == 3:
        chain, nonce, prio, maxfee, gas, to, value, data, al, maxblob, hashes, yp, r, s = f
        p = {"type_": 3, "chain_id": to_int(chain), "nonce": to_int(nonce),
             "max_fees_per_gas": {"regular": to_int(maxfee), "blob": to_int(maxblob)},
             "gas": to_int(gas), "value": to_int(value), "input_": data, "access_list": _al(al),
             "max_priority_fees_per_gas": {"regular": to_int(prio)},
             "blob_versioned_hashes": list(hashes)}
        sel = 9
    elif t == 4:
        chain, nonce, prio, maxfee, gas, to, value, data, al, auth, yp, r, s = f
        auths = []
        for ac, addr, an, ay, ar, as_ in auth:
            c = to_int(ac)
            if c == 0:
                ap = (1, {"magic": 5, "address": addr, "nonce": to_int(an)})
            else:
                ap = (2, {"magic": 5, "chain_id": c, "address": addr, "nonce": to_int(an)})
            auths.append({"payload": ap, "signature": _sig(to_int(ay), ar, as_)})
        p = {"type_": 4, "chain_id": to_int(chain), "nonce": to_int(nonce),
             "max_fees_per_gas": {"regular": to_int(maxfee)}, "gas": to_int(gas),
             "value": to_int(value), "input_": data, "access_list": _al(al),
             "max_priority_fees_per_gas": {"regular": to_int(prio)},
             "authorization_list": auths}
        sel = 10
    else:
        raise ValueError(t)
    if t in (1, 2):
        if to:
            p["to"] = to
        else:
            sel += 1
    else:
        p["to"] = to
    return {"payload": (sel, p), "signature": _sig(to_int(yp), r, s)}
