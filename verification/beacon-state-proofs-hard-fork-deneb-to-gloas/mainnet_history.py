#!/usr/bin/env python3
"""Exact reproduction of the article's historical mainnet values that public APIs still serve.

Standard library only.

    python3 -I mainnet_history.py              # online: fetch, check, write mainnet_history.json
    python3 -I mainnet_history.py --offline    # re-check mainnet_history.json, no network

Checks:
  1. beacon header at slot 15,580,064 (the article's worked example): state_root starts with
     0x966c88c1 and ends with e72a; hash_tree_root(header), recomputed from its 5 fields, equals
     the API root and is 0xa544aac2...36b3;
  2. execution block 22,431,084 (first Electra block): timestamp 1746612311 (= Electra fork
     timestamp); its parentBeaconBlockRoot is recorded;
  3. beacon header at slot 11,649,023: its recomputed root equals that parentBeaconBlockRoot,
     and its slot is below the Electra fork slot 11,649,024 (364,032 * 32).
  Also: the execution block that carries the slot 15,580,064 root (26,340,577, timestamp
  1793784803), whose parentBeaconBlockRoot must be 0xa544aac2...

The EIP-4788 eth_call of the article (timestamp 1793784803) cannot be repeated: that ring
buffer entry was overwritten about 27 hours after 2026-11-04.

Not audited; a reading aid for the article.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I drops the script dir

import beacon_net as net  # noqa: E402
from ssz_state import BeaconBlockHeader, header_bytes, header_root  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "mainnet_history.json")

ARTICLE_SLOT = 15_580_064
ARTICLE_STATE_ROOT = ("0x966c88c1", "e72a")
ARTICLE_BLOCK_ROOT = ("0xa544aac2", "36b3")
ARTICLE_4788_ROOT = "0xa544aac2197593cc74205def3af75bdb35bdc6e9da212a79bea40eb5919e36b3"
ARTICLE_EXEC_BLOCK = 26_340_577
ARTICLE_EXEC_TS = 1_793_784_803
ELECTRA_EXEC_BLOCK = 22_431_084
ELECTRA_TS = 1_746_612_311
ELECTRA_SLOT = 364_032 * 32
ARTICLE_ELECTRA_PARENT = ("0x947d2274", "552967")
GENESIS_TIME = 1_606_824_023

EXTRA_RPCS = net.EXECUTION_RPCS + [("cloudflare-eth", "https://cloudflare-eth.com"),
                                   ("drpc", "https://eth.drpc.org")]
RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (" (%s)" % detail if detail else ""))


def unh(s):
    return bytes.fromhex(s[2:])


def recompute(hd):
    return "0x" + header_root(hd["slot"], hd["proposer_index"], unh(hd["parent_root"]),
                              unh(hd["state_root"]), unh(hd["body_root"])).hex()


def fetch_header(slot, log):
    name, out = net.beacon_get("/eth/v1/beacon/headers/%d" % slot, log=log)
    if name is None:
        return {"slot_requested": slot, "served": False, "errors": out}
    m = out["data"]["header"]["message"]
    return {"slot_requested": slot, "served": True, "endpoint": name, "api_root": out["data"]["root"],
            "canonical": out["data"].get("canonical"), "finalized": out.get("finalized"),
            "header": {"slot": int(m["slot"]), "proposer_index": int(m["proposer_index"]),
                       "parent_root": m["parent_root"], "state_root": m["state_root"],
                       "body_root": m["body_root"]}}


def fetch_exec_block(number, log):
    for attempt in range(3):
        try:
            name, out = net.rpc("eth_getBlockByNumber", [hex(number), False], rpcs=EXTRA_RPCS, log=log)
            if "result" in out and out["result"]:
                b = out["result"]
                return {"number": number, "served": True, "endpoint": name, "hash": b["hash"],
                        "timestamp": int(b["timestamp"], 16),
                        "parentBeaconBlockRoot": b.get("parentBeaconBlockRoot")}
        except RuntimeError as e:
            err = str(e)
        time.sleep(2)
    return {"number": number, "served": False, "error": locals().get("err", "no result")}


def checks(rec):
    a = rec["article_header"]
    if a["served"]:
        hd = a["header"]
        root = recompute(hd)
        check("slot 15,580,064 header served (%s)" % a["endpoint"], hd["slot"] == ARTICLE_SLOT)
        check("state_root = 0x966c88c1...e72a", hd["state_root"].startswith(ARTICLE_STATE_ROOT[0])
              and hd["state_root"].endswith(ARTICLE_STATE_ROOT[1]), hd["state_root"])
        check("hash_tree_root(header) recomputed == API root", root == a["api_root"], root)
        check("block root = 0xa544aac2...36b3", root.startswith(ARTICLE_BLOCK_ROOT[0])
              and root.endswith(ARTICLE_BLOCK_ROOT[1]))
        check("block root == the full value the article's cast call printed", root == ARTICLE_4788_ROOT)
        # Header-level figures of the article's H-01 discussion.
        r = unh(root)
        check("empty proof 'slot' = first 8 bytes of the root = 14,741,254,758,814,336,165",
              int.from_bytes(r[:8], "little") == 14_741_254_758_814_336_165)
        t = BeaconBlockHeader.tree(header_bytes(hd["slot"], hd["proposer_index"], unh(hd["parent_root"]),
                                                unh(hd["state_root"]), unh(hd["body_root"])))
        one = int.from_bytes(t.node(2)[:8], "little")
        check("one-sibling proof (leaf gindex 2) 'slot' = 11,533,380,310,597,772,962",
              one == 11_533_380_310_597_772_962, str(one))
        check("three siblings (gindex 8) return the true slot 15,580,064",
              int.from_bytes(t.node(8)[:8], "little") == ARTICLE_SLOT)
    else:
        check("slot 15,580,064 header served", False, json.dumps(a.get("errors")))
    c = rec["article_exec_block"]
    if c["served"]:
        check("execution block 26,340,577 timestamp 1793784803 = genesis + 15,580,065 * 12",
              c["timestamp"] == ARTICLE_EXEC_TS == GENESIS_TIME + 12 * (ARTICLE_SLOT + 1))
        check("execution block 26,340,577 parentBeaconBlockRoot == 0xa544aac2...",
              c["parentBeaconBlockRoot"] == ARTICLE_4788_ROOT)
        check("ring index 1793784803 % 8191 = 4949, root slot 13,140",
              ARTICLE_EXEC_TS % 8191 == 4949 and ARTICLE_EXEC_TS % 8191 + 8191 == 13140)
    else:
        check("execution block 26,340,577 served", False, c.get("error"))
    e = rec["electra_exec_block"]
    if e["served"]:
        check("execution block 22,431,084 timestamp == 1746612311", e["timestamp"] == ELECTRA_TS)
        check("Electra timestamp = genesis + 11,649,024 * 12", ELECTRA_TS == GENESIS_TIME + 12 * ELECTRA_SLOT)
        p = e["parentBeaconBlockRoot"]
        check("parentBeaconBlockRoot = 0x947d2274...552967", p.startswith(ARTICLE_ELECTRA_PARENT[0])
              and p.endswith(ARTICLE_ELECTRA_PARENT[1]), p)
    else:
        check("execution block 22,431,084 served", False, e.get("error"))
    d = rec["pre_electra_header"]
    if d["served"] and e["served"]:
        root = recompute(d["header"])
        check("slot 11,649,023 header served (%s)" % d["endpoint"], d["header"]["slot"] == 11_649_023)
        check("hash_tree_root(header 11,649,023) recomputed == API root", root == d["api_root"])
        check("header 11,649,023 root == parentBeaconBlockRoot of block 22,431,084",
              root == e["parentBeaconBlockRoot"])
        check("slot 11,649,023 < Electra fork slot 11,649,024 (Deneb layout, gindex 363)",
              d["header"]["slot"] < ELECTRA_SLOT)
    else:
        check("slot 11,649,023 header served", False, json.dumps(d.get("errors")))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="re-check mainnet_history.json without network")
    ap.add_argument("--json", default=OUT)
    a = ap.parse_args()
    if a.offline:
        with open(a.json) as f:
            rec = json.load(f)
        print("offline re-check of", os.path.basename(a.json), "recorded", rec["collected_utc"])
    else:
        log = []
        rec = {"collected_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        rec["article_header"] = fetch_header(ARTICLE_SLOT, log)
        rec["article_exec_block"] = fetch_exec_block(ARTICLE_EXEC_BLOCK, log)
        rec["electra_exec_block"] = fetch_exec_block(ELECTRA_EXEC_BLOCK, log)
        rec["pre_electra_header"] = fetch_header(ELECTRA_SLOT - 1, log)
        rec["requests"] = log
        with open(a.json, "w") as f:
            json.dump(rec, f, indent=1)
            f.write("\n")
    checks(rec)
    fails = [n for n, ok in RESULTS if not ok]
    print("%d PASS, %d FAIL" % (len(RESULTS) - len(fails), len(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
