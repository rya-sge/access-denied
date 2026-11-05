"""Encoded size and calldata cost of the same data in both encodings, on one real block."""
import statistics as st
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import beacon_types as B  # noqa: E402
import eip6404  # noqa: E402
import rlp_codec as R  # noqa: E402
from mainnet import el_header, load, rlp_receipt, rlp_withdrawal  # noqa: E402
from mpt import trie_proof  # noqa: E402
from ssz_codec import List, ProgressiveList  # noqa: E402


def cd(b):
    """Standard calldata gas (EIP-2028) and EIP-7623 tokens."""
    z = b.count(0)
    nz = len(b) - z
    return 4 * z + 16 * nz, z + 4 * nz


def row(name, r, s):
    gr, tr = cd(r)
    gs, ts = cd(s)
    zr, zs = len(zlib.compress(r, 6)), len(zlib.compress(s, 6))
    print(f"{name:34} rlp {len(r):7} ssz {len(s):7} ratio {len(s)/len(r):6.3f} | "
          f"calldata gas rlp {gr:8} ssz {gs:8} | zlib rlp {zr:7} ssz {zs:7}")


raw, sb, el, rc, hdr = load()
pl = sb["message"]["body"]["execution_payload"]
wds = pl["withdrawals"]
print("Same data, two encodings")
row("one withdrawal", R.encode(rlp_withdrawal(wds[0])), B.Withdrawal.ser(wds[0]))
wl = List(B.Withdrawal, 16)
row("16 withdrawals as a list", R.encode([rlp_withdrawal(w) for w in wds]), wl.ser(wds))
txs = pl["transactions"]
conv = [eip6404.convert(t) for t in txs]
ssz_txs = [eip6404.Transaction.ser(c) for c in conv]
row("260 transactions, concatenated", b"".join(txs), b"".join(ssz_txs))
tl = ProgressiveList(eip6404.Transaction)
row("260 transactions, as a list", R.encode([t if t[0] < 0xC0 else R.decode(t) for t in txs]), tl.ser(conv))
print()
print("Per type, signed form against EIP-6404 Transaction")
by = {}
for t, s in zip(txs, ssz_txs):
    k = 0 if t[0] >= 0xC0 else t[0]
    by.setdefault(k, []).append((len(t), len(s)))
for k in sorted(by):
    a = by[k]
    print(f"type {k}: n={len(a):3} median rlp {st.median(x for x,_ in a):8} median ssz {st.median(y for _,y in a):8} "
          f"median extra {st.median(y-x for x,y in a):7} total rlp {sum(x for x,_ in a):8} total ssz {sum(y for _,y in a):8}")
extra = [len(s) - len(t) for t, s in zip(txs, ssz_txs)]
print(f"all: min extra {min(extra)} median {st.median(extra)} max {max(extra)}, smaller in SSZ: {sum(e<0 for e in extra)} of {len(extra)}")
print()
print("Whole objects, not field-for-field equal")
h = R.encode(el_header(el))
ph = dict(pl)
ph["transactions_root"] = B.ExecutionPayload.fields[13][1].htr(pl["transactions"])
ph["withdrawals_root"] = B.ExecutionPayload.fields[14][1].htr(pl["withdrawals"])
print("rlp(execution header)", len(h), "ExecutionPayloadHeader ssz", len(B.ExecutionPayloadHeader.ser(ph)))
print("rlp(execution block)", int(el["size"], 16), "SignedBeaconBlock ssz", len(raw))
pls = B.ExecutionPayload.ser(pl)
print("ExecutionPayload ssz", len(pls), "of which opaque transactions", sum(len(t) for t in txs))
print("receipts rlp total", sum(len(rlp_receipt(r)) for r in rc), "for", len(rc), "receipts")
print()
print("Inclusion proofs on this block")
tx_trie = {R.encode(i): t for i, t in enumerate(txs)}
wd_trie = {R.encode(i): R.encode(rlp_withdrawal(w)) for i, w in enumerate(wds)}
sizes = [sum(map(len, trie_proof(tx_trie, R.encode(i)))) for i in range(len(txs))]
print(f"tx MPT proof bytes without the transaction: min {min(sizes)} median {st.median(sizes)} max {max(sizes)}")
wp = [sum(map(len, trie_proof(wd_trie, R.encode(i)))) for i in range(len(wds))]
print(f"withdrawal MPT proof bytes: min {min(wp)} median {st.median(wp)} max {max(wp)}")
print("note: the last MPT node holds the leaf value, so the sizes above include one full copy of it")
print("SSZ branch for one element of Transactions (limit 2^20):", 21 * 32, "bytes, 21 siblings")
print("SSZ branch for one element of Withdrawals (limit 16):", 5 * 32, "bytes, 5 siblings")
