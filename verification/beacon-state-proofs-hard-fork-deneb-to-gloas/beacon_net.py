"""Small HTTP helpers for the mainnet scripts. Standard library only.

Public, unauthenticated endpoints only. The User-Agent is generic, and no other
identifying data is sent. Responses are untrusted: callers check every value they
use (roots are recomputed locally).
"""

import json
import time
import urllib.error
import urllib.request

USER_AGENT = "beacon-proof-verification/1.0"

# Beacon node APIs (standard /eth/v1 routes), in the order they are tried.
BEACON_APIS = [
    ("publicnode", "https://ethereum-beacon-api.publicnode.com"),
    ("lodestar-chainsafe", "https://lodestar-mainnet.chainsafe.io"),
]

# Checkpoint sync servers (serve /eth/v2/debug/beacon/states/finalized as SSZ).
CHECKPOINT_SYNC = [
    ("attestant", "https://mainnet-checkpoint-sync.attestant.io"),
    ("beaconcha.in", "https://sync-mainnet.beaconcha.in"),
]

# Execution JSON-RPC.
EXECUTION_RPCS = [
    ("publicnode", "https://ethereum-rpc.publicnode.com"),
]


def http_get(url, accept="application/json", timeout=60):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), dict(r.headers)


def get_json(url, timeout=60):
    body, _ = http_get(url, timeout=timeout)
    return json.loads(body)


def beacon_get(path, apis=None, log=None):
    """Try each beacon API in turn. Returns (name, json) or (None, errors)."""
    errors = {}
    for name, base in apis or BEACON_APIS:
        try:
            out = get_json(base + path)
            if log is not None:
                log.append({"path": path, "endpoint": name, "ok": True})
            return name, out
        except (urllib.error.URLError, OSError, ValueError) as e:  # HTTPError is a URLError
            errors[name] = "%s: %s" % (type(e).__name__, e)
            if log is not None:
                log.append({"path": path, "endpoint": name, "ok": False, "error": errors[name]})
            time.sleep(0.5)
    return None, errors


def rpc(method, params, rpcs=None, log=None):
    """JSON-RPC call; returns (name, result) or raises RuntimeError with every error."""
    errors = {}
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for name, url in rpcs or EXECUTION_RPCS:
        try:
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json", "User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as r:
                out = json.loads(r.read())
            if log is not None:
                log.append({"method": method, "endpoint": name, "ok": "error" not in out})
            if "error" in out:
                return name, {"error": out["error"]}
            return name, {"result": out["result"]}
        except (urllib.error.URLError, OSError, ValueError) as e:
            errors[name] = "%s: %s" % (type(e).__name__, e)
    raise RuntimeError("all RPCs failed: %r" % errors)


def download(url, path, accept="application/octet-stream", stall_timeout=90):
    """Stream `url` to `path`. Raises on error or when no byte arrives for `stall_timeout` s."""
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": USER_AGENT})
    n = 0
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=stall_timeout) as r, open(path, "wb") as f:
        headers = dict(r.headers)
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
            n += len(b)
    return n, headers, time.time() - t0
