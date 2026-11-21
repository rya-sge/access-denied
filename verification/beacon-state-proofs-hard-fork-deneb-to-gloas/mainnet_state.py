#!/usr/bin/env python3
"""Re-run the article's mainnet method on a fresh finalized Fulu state.

Standard library only. The state is a different one from the article's (slot
15,580,064 is no longer served by checkpoint sync), so the values differ; the
method and the gindices are the same.

Online (downloads about 350 MB of SSZ into DATA_DIR, which should be outside the
repository; nothing downloaded is committed):

    python3 -I mainnet_state.py --data-dir DATA_DIR

    1. finalized state SSZ from a public checkpoint sync server, and the block header
       at the state's slot from a public beacon API;
    2. hash_tree_root(state) == header.state_root;
    3. 53-sibling branch for validators[1_000_000].withdrawal_credentials, gindex
       12,578,413,029,757,441, verified against the block root;
    4. eth_call to the EIP-4788 contract at the child block's timestamp (only works while
       the root is in the 8191-slot ring buffer, about 27 hours);
    5. the Deneb gindices of the article's stale table (34, 43, 44, 52, 54, 59) on this
       Fulu state, each with a 5-sibling branch at depth 5;
    6. snapshot.json: header, leaf, branches, stale values and the 4788 result (no state bytes).

Offline, from snapshot.json only:

    python3 -I mainnet_state.py --snapshot [snapshot.json]

Not audited; a reading aid for the article.
"""

import argparse
import json
import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I drops the script dir

import beacon_net as net  # noqa: E402
from ssz_state import (  # noqa: E402
    BeaconBlockHeader, BeaconStateFulu, BelowLeaf, Validator, ZERO_HASHES, block_tree,
    concat_gindices, header_bytes, is_valid_merkle_branch, sha256, verify_gindex)

HERE = os.path.dirname(os.path.abspath(__file__))
GENESIS_TIME = 1606824023
BEACON_ROOTS = "0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02"
VALIDATOR_INDEX = 1_000_000
G_WC_FULU = 12_578_413_029_757_441          # concat(11, 75, 2, 2**40 + 1e6, 9)
G_WC_DENEB = 6_385_963_542_123_009          # concat(11, 43, 2, 2**40 + 1e6, 9)
G_BAL_FULU = 393_625_162_993_808            # concat(11, 76, 2, 2**38 + 250000)
G_BAL_DENEB = 200_111_116_505_232           # concat(11, 44, 2, 2**38 + 250000)
STALE_DENEB = [("slot", 34), ("validators", 43), ("balances", 44),
               ("finalized_checkpoint", 52), ("current_sync_committee", 54),
               ("historical_summaries", 59)]

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (" (%s)" % detail if detail else ""))
    return bool(cond)


def h(b):
    return "0x" + b.hex()


def unh(s):
    return bytes.fromhex(s[2:] if s.startswith("0x") else s)


def u64(b):
    return struct.unpack("<Q", b[:8])[0]


# ------------------------------------------------------------------ download

def fetch_state(data_dir):
    path = os.path.join(data_dir, "state.ssz")
    meta_path = os.path.join(data_dir, "state_meta.json")
    if os.path.exists(path) and os.path.exists(meta_path):
        print("reusing", path)
        with open(meta_path) as f:
            return path, json.load(f)
    attempts = []
    for name, base in net.CHECKPOINT_SYNC:
        url = base + "/eth/v2/debug/beacon/states/finalized"
        print("downloading finalized state from", name, "...", flush=True)
        try:
            n, headers, secs = net.download(url, path + ".part")
            os.replace(path + ".part", path)
            meta = {"endpoint": name, "url": url, "bytes": n, "seconds": round(secs),
                    "consensus_version": headers.get("Eth-Consensus-Version") or headers.get("eth-consensus-version"),
                    "downloaded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "failed_attempts": attempts}
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=1)
            return path, meta
        except Exception as e:  # noqa: BLE001 - record and try the next endpoint
            attempts.append({"endpoint": name, "error": "%s: %s" % (type(e).__name__, e)})
            print("  failed:", attempts[-1]["error"])
    raise SystemExit("no checkpoint sync endpoint delivered the state: %r" % attempts)


# ------------------------------------------------------------------ online run

def run_online(data_dir, out_path):
    log = []
    path, meta = fetch_state(data_dir)
    with open(path, "rb") as f:
        data = f.read()
    slot = u64(data[40:48])
    print("state slot", slot, "size", len(data), "version", meta.get("consensus_version"))
    check("state is fulu", meta.get("consensus_version") == "fulu", meta.get("consensus_version"))

    # Header at the state's slot.
    ep, hdr = net.beacon_get("/eth/v1/beacon/headers/%d" % slot, log=log)
    if ep is None:
        raise SystemExit("no beacon API served header %d: %r" % (slot, hdr))
    msg = hdr["data"]["header"]["message"]
    header = {"slot": int(msg["slot"]), "proposer_index": int(msg["proposer_index"]),
              "parent_root": msg["parent_root"], "state_root": msg["state_root"],
              "body_root": msg["body_root"]}
    api_root = hdr["data"]["root"]
    hdata = header_bytes(header["slot"], header["proposer_index"], unh(header["parent_root"]),
                         unh(header["state_root"]), unh(header["body_root"]))
    block_root = BeaconBlockHeader.root(hdata)
    check("header root recomputed == API root", h(block_root) == api_root, api_root)
    check("header slot == state slot", header["slot"] == slot)

    t0 = time.time()
    state = BeaconStateFulu.tree(data)
    secs = time.time() - t0
    state_root = state.root()
    print("hash_tree_root(state) = %s (%.0f s)" % (h(state_root), secs))
    check("hash_tree_root(state) == header.state_root", h(state_root) == header["state_root"])

    parts = BeaconStateFulu.split(data)
    names = [n for n, _ in BeaconStateFulu.fields]
    vals = parts[names.index("validators")]
    nval = len(vals) // 121
    bt = block_tree(hdata, state)

    # Validator 1,000,000.
    g = concat_gindices(11, 75, 2, 2 ** 40 + VALIDATOR_INDEX, 9)
    check("gindex == 12,578,413,029,757,441", g == G_WC_FULU)
    vbytes = vals[121 * VALIDATOR_INDEX:121 * (VALIDATOR_INDEX + 1)]
    vparts = Validator.split(vbytes)
    leaf = vparts[1]
    branch = bt.get_branch(g)
    check("branch has 53 siblings", len(branch) == 53)
    check("53-sibling branch verifies against the block root (is_valid_merkle_branch)",
          verify_gindex(leaf, branch, g, block_root))
    check("52-sibling truncation rejected", not verify_gindex(leaf, branch[:-1], g, block_root)
          and not is_valid_merkle_branch(leaf, branch[:-1], 53, g - 2 ** 53, block_root))
    fields = {"pubkey": h(vparts[0]), "withdrawal_credentials": h(leaf),
              "effective_balance": u64(vparts[2]), "slashed": vparts[3][0],
              "activation_eligibility_epoch": u64(vparts[4]), "activation_epoch": u64(vparts[5]),
              "exit_epoch": u64(vparts[6]), "withdrawable_epoch": u64(vparts[7])}
    bal_chunk = bt.node(G_BAL_FULU)
    bal_branch = bt.get_branch(G_BAL_FULU)
    check("balance chunk branch (48 siblings) verifies", len(bal_branch) == 48
          and verify_gindex(bal_chunk, bal_branch, G_BAL_FULU, block_root))
    balance = u64(bal_chunk[0:8])
    check("balance lane 0 == balances[1_000_000] in the SSZ",
          balance == u64(parts[names.index("balances")][8 * VALIDATOR_INDEX:]))
    walk = {k: h(bt.node(g >> k)) for k in (0, 3, 43, 44, 50, 53)}
    check("walk node 50 == state root, node 53 == block root",
          walk[50] == h(state_root) and walk[53] == h(block_root))
    check("sibling 44 is the length %d as uint256 LE" % nval, branch[43] == nval.to_bytes(32, "little"))
    zero_sibs = sum(1 for lvl in range(40) if branch[3 + lvl] == ZERO_HASHES[lvl])
    data_depth_used = (nval - 1).bit_length()
    check("empty-subtree siblings in the list data = 40 - %d" % data_depth_used,
          zero_sibs == 40 - data_depth_used, "%d" % zero_sibs)
    slot_branch = bt.get_branch(8)
    check("header slot proof at gindex 8 (3 siblings) verifies",
          verify_gindex(slot.to_bytes(32, "little"), slot_branch, 8, block_root))

    # Stale Deneb gindices evaluated at depth 5 on the Fulu (depth 6) state.
    stale = []
    for fname, gd in STALE_DENEB:
        node = state.node(gd)
        br = state.get_branch(gd)
        ok = len(br) == 5 and is_valid_merkle_branch(node, br, 5, gd - 32, state_root)
        covers = [names[c - 64] if c - 64 < len(names) else "padding" for c in (2 * gd, 2 * gd + 1)]
        true_g = 64 + names.index(fname)
        entry = {"field": fname, "deneb_gindex": gd, "fulu_node_covers": covers, "leaf": h(node),
                 "branch": [h(x) for x in br], "valid_depth5": ok,
                 "true_fulu_gindex": true_g, "true_value": h(state.node(true_g))}
        if fname == "slot":
            entry["leaf_as_uint64"] = u64(node)
        stale.append(entry)
        check("stale Deneb gindex %d (%s) verifies at depth 5" % (gd, fname), ok, h(node)[:10] + "...")
    check("gindices 52, 54, 59 give the zero hash of depth 1",
          all(e["leaf"] == h(ZERO_HASHES[1]) for e in stale[3:]))
    deep = {}
    sc = parts[names.index("current_sync_committee")]
    eph = parts[names.index("latest_execution_payload_header")]
    expected_leaf = {"deneb_withdrawal_credentials": (sc[0:32], "first chunk of current_sync_committee.pubkeys[0]"),
                     "deneb_balance": (eph[0:32], "latest_execution_payload_header.parent_hash")}
    for label, gdeep in (("deneb_withdrawal_credentials", G_WC_DENEB), ("deneb_balance", G_BAL_DENEB)):
        total = gdeep.bit_length() - 1
        try:
            bt.node(gdeep)
            deep[label] = {"result": "node exists (unexpected)"}
            check("stale %s path ends below a leaf (no valid branch)" % label, False)
            continue
        except BelowLeaf:
            pass
        d = total
        while True:  # deepest ancestor of the path that exists in the Fulu tree
            try:
                node = bt.node(gdeep >> (total - d))
                break
            except BelowLeaf:
                d -= 1
        want, what = expected_leaf[label]
        deep[label] = {"gindex": gdeep, "proof_length": total, "stops_at_depth": d,
                       "levels_missing": total - d, "leaf": h(node), "leaf_is": what}
        check("stale %s path (%d levels) stops at a leaf at depth %d, %d levels missing: %s"
              % (label, total, d, total - d, what), node == want)
    fin105 = state.node(105)
    check("gindex 105 (pre-Electra FINALIZED_ROOT_GINDEX) is a zero leaf with a valid 6-sibling branch",
          fin105 == ZERO_HASHES[0] and is_valid_merkle_branch(fin105, state.get_branch(105), 6, 105 - 64, state_root))
    fin_root = parts[names.index("finalized_checkpoint")][8:40]
    check("gindex 169 == finalized_checkpoint.root", state.node(169) == fin_root)
    fork_leaf = state.node(concat_gindices(67, 5))
    check("gindex 2,829 from the block root is fork.current_version 0x06000000",
          concat_gindices(11, 67, 5) == 2829 and bt.node(2829) == fork_leaf
          and fork_leaf[:4] == bytes.fromhex("06000000") and len(bt.get_branch(2829)) == 11)
    empty_slot = u64(block_root)
    one_sib = u64(bt.node(2))
    check("empty proof with leaf == root verifies in is_valid_merkle_branch(depth 0)",
          is_valid_merkle_branch(block_root, [], 0, 0, block_root))

    # The child block carries this root through EIP-4788.
    ep2, kids = net.beacon_get("/eth/v1/beacon/headers?parent_root=%s" % h(block_root), log=log)
    r4788 = {"attempted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        child = [d for d in kids["data"] if d["canonical"]][0]
        cslot = int(child["header"]["message"]["slot"])
        _, blk = net.beacon_get("/eth/v2/beacon/blocks/%s" % child["root"], log=log)
        payload = blk["data"]["message"]["body"]["execution_payload"]
        ts = int(payload["timestamp"])
        bn = int(payload["block_number"])
        check("child timestamp == genesis + 12 * child slot", ts == GENESIS_TIME + 12 * cslot)
        _, eb = net.rpc("eth_getBlockByNumber", [hex(bn), False], log=log)
        pbr = eb["result"]["parentBeaconBlockRoot"]
        check("execution block %d parentBeaconBlockRoot == block root" % bn, pbr == h(block_root))
        _, head = net.rpc("eth_blockNumber", [], log=log)
        name, res = net.rpc("eth_call", [{"to": BEACON_ROOTS, "data": "0x" + ts.to_bytes(32, "big").hex()},
                                         "latest"], log=log)
        _, res_bad = net.rpc("eth_call", [{"to": BEACON_ROOTS, "data": "0x" + (ts + 1).to_bytes(32, "big").hex()},
                                          "latest"], log=log)
        r4788.update({"child_slot": cslot, "execution_block": bn, "timestamp": ts,
                      "parentBeaconBlockRoot": pbr, "eth_call_endpoint": name,
                      "eth_call_at_block": int(head["result"], 16), "eth_call_result": res,
                      "eth_call_timestamp_plus_1": res_bad,
                      "ring_index": ts % 8191, "root_storage_slot": ts % 8191 + 8191})
        check("EIP-4788 eth_call returns the block root", res.get("result") == h(block_root),
              str(res)[:80])
        check("EIP-4788 eth_call with timestamp + 1 reverts", "error" in res_bad)
    except Exception as e:  # noqa: BLE001 - recorded, part B continues
        r4788["error"] = "%s: %s" % (type(e).__name__, e)
        check("EIP-4788 read", False, r4788["error"])

    snap = {
        "note": "Fresh finalized Fulu state, not the article's slot 15,580,064. Values differ from the article.",
        "collected_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "state": {"endpoint": meta["endpoint"], "url": meta["url"], "bytes": len(data),
                  "consensus_version": meta.get("consensus_version"), "slot": slot,
                  "validators": nval, "hash_tree_root": h(state_root), "hash_seconds": round(secs),
                  "failed_download_attempts": meta.get("failed_attempts", [])},
        "header": header, "header_endpoint": ep, "block_root": h(block_root),
        "proof": {"validator_index": VALIDATOR_INDEX, "field": "withdrawal_credentials",
                  "gindex": str(g), "leaf": h(leaf), "branch": [h(x) for x in branch]},
        "validator_fields": fields,
        "balance_proof": {"gindex": str(G_BAL_FULU), "chunk": h(bal_chunk), "balance_lane0": balance,
                          "branch": [h(x) for x in bal_branch]},
        "slot_proof": {"gindex": 8, "leaf": h(slot.to_bytes(32, "little")), "branch": [h(x) for x in slot_branch]},
        "walk": {str(k): v for k, v in walk.items()},
        "state_gindex_2": h(state.node(2)), "state_gindex_3": h(state.node(3)),
        "validators_root_gindex_75": h(state.node(75)),
        "stale_deneb": stale, "stale_deep_paths": deep,
        "gindex_105_leaf": h(fin105), "gindex_169_leaf": h(state.node(169)),
        "gindex_2829_leaf": h(fork_leaf),
        "header_shallow_slots": {"empty_proof_uint64": empty_slot, "one_sibling_uint64": one_sib,
                                 "two_sibling_uint64": u64(bt.node(4))},
        "eip4788": r4788,
        "requests": log,
    }
    with open(out_path, "w") as f:
        json.dump(snap, f, indent=1)
        f.write("\n")
    print("wrote", out_path)


# ------------------------------------------------------------------ offline

def run_snapshot(path):
    with open(path) as f:
        s = json.load(f)
    hd = s["header"]
    hdata = header_bytes(hd["slot"], hd["proposer_index"], unh(hd["parent_root"]),
                         unh(hd["state_root"]), unh(hd["body_root"]))
    root = BeaconBlockHeader.root(hdata)
    check("header root recomputed == recorded block root", h(root) == s["block_root"], s["block_root"])
    check("recorded state hash_tree_root == header.state_root", s["state"]["hash_tree_root"] == hd["state_root"])
    p = s["proof"]
    g = int(p["gindex"])
    check("gindex == concat(11, 75, 2, 2**40 + 1e6, 9)",
          g == concat_gindices(11, 75, 2, 2 ** 40 + p["validator_index"], 9) == G_WC_FULU)
    br = [unh(x) for x in p["branch"]]
    leaf = unh(p["leaf"])
    check("53-sibling branch verifies", len(br) == 53 and verify_gindex(leaf, br, g, root))
    check("52-sibling truncation rejected", not verify_gindex(leaf, br[:-1], g, root))
    check("node after 50 siblings == state_root",
          s["walk"]["50"] == hd["state_root"] and s["walk"]["53"] == s["block_root"])
    bp = s["balance_proof"]
    check("balance branch (48) verifies", verify_gindex(unh(bp["chunk"]), [unh(x) for x in bp["branch"]],
                                                       int(bp["gindex"]), root))
    sp = s["slot_proof"]
    check("slot branch (3) verifies", verify_gindex(unh(sp["leaf"]), [unh(x) for x in sp["branch"]], 8, root))
    sr = unh(hd["state_root"])
    for e in s["stale_deneb"]:
        check("stale gindex %d (%s) verifies at depth 5" % (e["deneb_gindex"], e["field"]),
              is_valid_merkle_branch(unh(e["leaf"]), [unh(x) for x in e["branch"]], 5,
                                     e["deneb_gindex"] - 32, sr))
    r = s["eip4788"]
    if "eth_call_result" in r:
        check("recorded EIP-4788 result == block root", r["eth_call_result"].get("result") == s["block_root"])
    else:
        print("INFO EIP-4788 read was not recorded:", r.get("error"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", help="directory for the downloaded state (outside the repository)")
    ap.add_argument("--snapshot", nargs="?", const=os.path.join(HERE, "snapshot.json"),
                    help="re-verify offline from snapshot.json")
    ap.add_argument("--out", default=os.path.join(HERE, "snapshot.json"))
    a = ap.parse_args()
    if a.snapshot:
        run_snapshot(a.snapshot)
    elif a.data_dir:
        os.makedirs(a.data_dir, exist_ok=True)
        run_online(a.data_dir, a.out)
    else:
        ap.error("give --data-dir (online) or --snapshot (offline)")
    fails = [n for n, ok in RESULTS if not ok]
    print("%d PASS, %d FAIL" % (len(RESULTS) - len(fails), len(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
