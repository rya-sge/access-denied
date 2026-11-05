#!/usr/bin/env python3
"""Measure each lock with real transactions on anvil (Cancun) and print receipts.

Run from the project directory after `forge build`. Uses anvil's unlocked accounts,
so no key is involved. Gas figures are `gasUsed` from receipts: after refunds, with
the EIP-3529 cap applied, including the 21,000 intrinsic cost.
"""
import json, re, socket, subprocess, sys, time

LOCKS = ["LockTransientYul", "LockTransientUint", "LockTransientBool", "LockOZTransient", "LockOZStorage", "LockStorageBool"]

def sh(*a):
    return subprocess.run(a, check=True, capture_output=True, text=True).stdout.strip()

def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

P = port(); RPC = f"http://127.0.0.1:{P}"
anvil = subprocess.Popen(["anvil", "--port", str(P), "--hardfork", "cancun", "--silent"])
time.sleep(1.5)
try:
    FROM = json.loads(sh("cast", "rpc", "eth_accounts", "--rpc-url", RPC))[0]

    def send(to, sig=None, *args, create=None):
        cmd = ["cast", "send", "--rpc-url", RPC, "--unlocked", "--from", FROM, "--gas-limit", "3000000", "--json"]
        cmd += ["--create", create] if create else [to, sig, *args]
        r = json.loads(sh(*cmd))
        assert r["status"] == "0x1", r
        return r

    def deploy(name):
        art = json.load(open(f"out/default/{sourcefile(name)}/{name}.json"))
        return send(None, create=art["bytecode"]["object"])["contractAddress"]

    def sourcefile(name):
        return "Locks.sol"

    def gas(r):
        return int(r["gasUsed"], 16)

    batcher = deploy("Batcher")
    rows = {}
    key = 1000
    for name in LOCKS:
        addr = deploy(name)
        # One warm-up transaction, so every measured call starts from the same state.
        send(addr, "guarded()")
        row = {}
        row["guarded"] = gas(send(addr, "guarded()"))
        row["unguarded"] = gas(send(addr, "unguarded()"))
        row["work"] = gas(send(addr, "guardedWork(uint256)", str(key)))
        row["unwork"] = gas(send(addr, "unguardedWork(uint256)", str(key + 100)))
        row["batch1"] = gas(send(batcher, "run(address,uint256)", addr, "1"))
        row["batch2"] = gas(send(batcher, "run(address,uint256)", addr, "2"))
        row["batch10"] = gas(send(batcher, "run(address,uint256)", addr, "10"))
        rows[name] = row
    base = rows["LockTransientYul"]
    cols = ["guarded", "unguarded", "work", "unwork", "batch1", "batch2", "batch10"]
    print("| lock | " + " | ".join(cols) + " |")
    for n, r in rows.items():
        print(f"| {n} | " + " | ".join(str(r[c]) for c in cols) + " |")
    print()
    print("overhead = guarded - unguarded, work = guardedWork - unguardedWork")
    for n, r in rows.items():
        print(f"{n}: lock-only overhead {r['guarded'] - r['unguarded']}, with work {r['work'] - r['unwork']}")

    # Transaction boundary on a real chain: a value set in one transaction is gone in the next.
    art = json.load(open("out/default/Semantics.sol/Raw.json"))
    raw = send(None, create=art["bytecode"]["object"])["contractAddress"]
    send(raw, "tset(uint256,uint256)", "0", "42")
    print("tget(0) in the next transaction:", int(sh("cast", "call", raw, "tget(uint256)(uint256)", "0", "--rpc-url", RPC).split()[0]))
finally:
    anvil.terminate()
