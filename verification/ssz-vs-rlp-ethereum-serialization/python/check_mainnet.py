"""Check both codecs against one real mainnet block: nothing here is self-referential,
each comparison is with a value produced by the network."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import beacon_types as B  # noqa: E402
import eip6404  # noqa: E402
import rlp_codec as R  # noqa: E402
from keccak import keccak256  # noqa: E402
from mainnet import eip2718_body, el_header, hx, load, qty, rlp_receipt, rlp_withdrawal  # noqa: E402
from mpt import trie_proof, trie_root, verify_proof  # noqa: E402

fails = 0


def check(label, a, b):
    global fails
    same = a == b
    fails += 0 if same else 1
    print(f"{'ok  ' if same else 'FAIL'} {label}: 0x{a.hex()[:16]}…" if isinstance(a, bytes)
          else f"{'ok  ' if same else 'FAIL'} {label}: {a}")


raw, sb, el, rc, hdr = load()
m = sb["message"]
body = m["body"]
pl = body["execution_payload"]
print("slot", m["slot"], "execution block", pl["block_number"], "transactions", len(pl["transactions"]),
      "withdrawals", len(pl["withdrawals"]), "attestations", len(body["attestations"]),
      "blobs", len(body["blob_kzg_commitments"]))

print("-- SSZ against the beacon chain")
check("re-serialised SignedBeaconBlock equals the downloaded bytes", B.SignedBeaconBlock.ser(sb), raw)
check("hash_tree_root(BeaconBlock) equals the block root", B.BeaconBlock.htr(m), hx(hdr["root"]))
check("hash_tree_root(body) equals header.body_root", B.BeaconBlockBody.htr(body),
      hx(hdr["header"]["message"]["body_root"]))

print("-- RLP against the execution chain")
h = el_header(el)
check("keccak256(rlp(header)) equals the block hash", keccak256(R.encode(h)), hx(el["hash"]))
check("that hash equals ExecutionPayload.block_hash", keccak256(R.encode(h)), pl["block_hash"])
n = 0
for tx, j in zip(pl["transactions"], el["transactions"]):
    n += keccak256(tx) == hx(j["hash"])
check("keccak256 of the opaque SSZ bytes equals each transaction hash", n, len(pl["transactions"]))
tx_trie = {R.encode(i): t for i, t in enumerate(pl["transactions"])}
check("MPT root over the same bytes equals header transactionsRoot", trie_root(tx_trie), hx(el["transactionsRoot"]))
wd_trie = {R.encode(i): R.encode(rlp_withdrawal(w)) for i, w in enumerate(pl["withdrawals"])}
check("MPT root over RLP withdrawals equals header withdrawalsRoot", trie_root(wd_trie), hx(el["withdrawalsRoot"]))
rc_trie = {R.encode(i): rlp_receipt(r) for i, r in enumerate(rc)}
check("MPT root over RLP receipts equals header receiptsRoot", trie_root(rc_trie), hx(el["receiptsRoot"]))
blk = R.encode([h, [eip2718_body(t) for t in pl["transactions"]], [],
                [rlp_withdrawal(w) for w in pl["withdrawals"]]])
check("length of rlp(block) equals the size reported by the node", len(blk), qty(el["size"]))

print("-- one block, two commitments")
print("EL withdrawalsRoot (MPT, keccak, RLP):   0x" + trie_root(wd_trie).hex())
print("CL withdrawals root (SSZ, sha256):       0x" +
      B.ExecutionPayload.fields[14][1].htr(pl["withdrawals"]).hex())
print("EL transactionsRoot (MPT, keccak, RLP):  0x" + trie_root(tx_trie).hex())
print("CL transactions root (SSZ, sha256):      0x" +
      B.ExecutionPayload.fields[13][1].htr(pl["transactions"]).hex())
print("EL parentBeaconBlockRoot field equals beacon parent_root:", hx(el["parentBeaconBlockRoot"]) == m["parent_root"])

print("-- MPT proofs")
i = len(pl["transactions"]) // 2
p = trie_proof(tx_trie, R.encode(i))
check(f"transaction {i}: the proof walks to the transaction", verify_proof(hx(el["transactionsRoot"]), R.encode(i), p),
      pl["transactions"][i])
p = trie_proof(wd_trie, R.encode(7))
check("withdrawal 7: the proof walks to the withdrawal", verify_proof(hx(el["withdrawalsRoot"]), R.encode(7), p),
      wd_trie[R.encode(7)])

print("-- EIP-6404 (Draft) conversion is lossless at field level")
n = 0
for tx in pl["transactions"]:
    v = eip6404.convert(tx)
    b = eip6404.Transaction.ser(v)
    v2 = eip6404.Transaction.de(b)
    n += eip6404.Transaction.ser(v2) == b and eip6404.Transaction.htr(v2) == eip6404.Transaction.htr(v)
check("round trips through the SSZ form", n, len(pl["transactions"]))
print("FAILURES:", fails)
sys.exit(1 if fails else 0)
