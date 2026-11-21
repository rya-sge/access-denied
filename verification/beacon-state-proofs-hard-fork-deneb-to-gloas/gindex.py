#!/usr/bin/env python3
"""Recompute the offline figures of the article on beacon state proofs across hard forks.

Usage:
    python3 -I gindex.py <path to ethereum/consensus-specs checkout>

Reads the container definitions from the spec markdown (pinned commit in README.md), computes
field counts, depths, generalized indices (gindices), proof lengths, the progressive-list ranges
and the fate of stale fixed-depth paths, and compares every value with the figure printed in the
article. Prints the tables, then one PASS/FAIL line per checked figure; exits 1 on any FAIL.

Standard library only. No network. Mainnet values (roots, hashes, validator data, gas) are not
covered: see README.md.
"""
import hashlib
import math
import re
import sys
from datetime import datetime, timezone

if len(sys.argv) != 2:
    sys.exit(__doc__)
SPECS = sys.argv[1].rstrip("/") + "/specs/"
CONFIG = sys.argv[1].rstrip("/") + "/configs/mainnet.yaml"

# Mainnet genesis time. Not a spec constant: it is the chain's genesis (beacon API
# /eth/v1/beacon/genesis). It is checked below against the fork dates in the config comments.
MAINNET_GENESIS_TIME = 1606824023

results = []


def check(label, got, want):
    ok = got == want
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got}" + ("" if ok else f" (article: {want})"))


# --- Spec parsing --------------------------------------------------------------------------

def container_fields(fork, name, file="beacon-chain.md"):
    """Field (name, type) list of `class <name>(...)` as defined in specs/<fork>/<file>."""
    text = open(SPECS + fork + "/" + file, encoding="utf-8").read()
    m = re.search(r"class " + name + r"\((\w+)\):\n(.*?)\n```", text, re.S)
    if not m:
        return None, None
    fields = re.findall(r"^    ([a-z0-9_]+): ([A-Za-z0-9_\[\], ]+)$", m.group(2), re.M)
    active = re.search(r"ACTIVE_FIELDS = active_fields\(width=(\d+)(?:, gaps=\(([\d, ]+)\))?\)", m.group(2))
    layout = None
    if active:
        width = int(active.group(1))
        gaps = {int(g) for g in active.group(2).split(",")} if active.group(2) else set()
        positions = [p for p in range(width) if p not in gaps]
        assert len(positions) == len(fields), (fork, name, width, gaps, len(fields))
        layout = dict(zip([f for f, _ in fields], positions))
    return fields, layout


STATE = {}
for fork in ["deneb", "electra", "fulu", "gloas", "heze"]:
    fields, layout = container_fields(fork, "BeaconState")
    STATE[fork] = {"fields": [f for f, _ in fields], "types": dict(fields), "positions": layout}

HEADER, _ = container_fields("phase0", "BeaconBlockHeader")
VALIDATOR, _ = container_fields("phase0", "Validator")
CHECKPOINT, _ = container_fields("phase0", "Checkpoint")
FORK, _ = container_fields("phase0", "Fork")


# --- Gindex arithmetic (consensus-specs ssz/merkle-proofs.md, EIP-7916, EIP-7495) -----------

def concat(*gs):
    """concat_generalized_indices: walk g1, then g2 from the node g1 reached, ..."""
    r = gs[0]
    for g in gs[1:]:
        depth = g.bit_length() - 1
        r = (r << depth) | (g - (1 << depth))
    return r


def proof_length(g):
    return g.bit_length() - 1


def depth_of(n):
    return math.ceil(math.log2(n))


def container_gindex(n_fields, index):
    return (1 << depth_of(n_fields)) + index


def progressive_gindex(i):
    """Gindex of chunk i inside merkleize_progressive (EIP-7916): hash(a, b) with a = the first
    num_leaves chunks (left, 2g) and b = the rest (right, 2g+1); num_leaves = 1, 4, 16, ..."""
    g, start, size = 1, 0, 1
    while i >= start + size:
        g, start, size = 2 * g + 1, start + size, size * 4
    return (2 * g) * size + (i - start)


def state_gindex(fork, field):
    st = STATE[fork]
    if field not in st["fields"]:
        return None
    if st["positions"] is not None:  # ProgressiveContainer: data subtree at gindex 2
        return concat(2, progressive_gindex(st["positions"][field]))
    return container_gindex(len(st["fields"]), st["fields"].index(field))


VALIDATOR_REGISTRY_LIMIT = 2**40
BALANCE_CHUNKS = 2**40 * 8 // 32  # uint64 packed four per chunk
HEADER_STATE_ROOT = container_gindex(len(HEADER), [f for f, _ in HEADER].index("state_root"))
WITHDRAWAL_CREDENTIALS = container_gindex(len(VALIDATOR), [f for f, _ in VALIDATOR].index("withdrawal_credentials"))
CHECKPOINT_ROOT = container_gindex(len(CHECKPOINT), [f for f, _ in CHECKPOINT].index("root"))


def validator_field_gindex(fork, i):
    v = state_gindex(fork, "validators")
    element = progressive_gindex(i) if fork in ("gloas", "heze") else VALIDATOR_REGISTRY_LIMIT + i
    return concat(HEADER_STATE_ROOT, v, 2, element, WITHDRAWAL_CREDENTIALS)


def balance_chunk_gindex(fork, i):
    b = state_gindex(fork, "balances")
    element = progressive_gindex(i // 4) if fork in ("gloas", "heze") else BALANCE_CHUNKS + i // 4
    return concat(HEADER_STATE_ROOT, b, 2, element)


# --- 1. Forks: epochs, slots, timestamps, field counts, depth -----------------------------

print("== Forks (configs/mainnet.yaml, specs/*/beacon-chain.md)")
config = open(CONFIG, encoding="utf-8").read()
SLOT_SECONDS = int(re.search(r"^SLOT_DURATION_MS: (\d+)", config, re.M).group(1)) // 1000
fork_rows = {"deneb": (269568, 8626176, 1710338135, 28, 5),
             "electra": (364032, 11649024, 1746612311, 37, 6),
             "fulu": (411392, 13164544, 1764798551, 38, 6)}
for fork, (w_epoch, w_slot, w_ts, w_n, w_depth) in fork_rows.items():
    m = re.search(rf"^{fork.upper()}_FORK_EPOCH: (\d+)\s*#\s*(.+)$", config, re.M)
    epoch = int(m.group(1))
    slot = epoch * 32
    ts = MAINNET_GENESIS_TIME + slot * SLOT_SECONDS
    comment = datetime.strptime(m.group(2).strip().replace("pm", "PM").replace("am", "AM"),
                                "%B %d, %Y, %I:%M:%S%p UTC")
    comment_ts = int(comment.replace(tzinfo=timezone.utc).timestamp())
    n = len(STATE[fork]["fields"])
    check(f"{fork} epoch", epoch, w_epoch)
    check(f"{fork} first slot", slot, w_slot)
    check(f"{fork} timestamp", ts, w_ts)
    check(f"{fork} timestamp equals the config comment date", ts, comment_ts)
    check(f"{fork} BeaconState fields", n, w_n)
    check(f"{fork} BeaconState depth", depth_of(n), w_depth)
for fork, w_n in (("gloas", 46), ("heze", 42)):
    check(f"{fork} BeaconState fields", len(STATE[fork]["fields"]), w_n)
    check(f"{fork} is a ProgressiveContainer", STATE[fork]["positions"] is not None, True)

# --- 2. Header and Validator field gindices ----------------------------------------------

print("\n== BeaconBlockHeader and Validator field gindices")
for (name, _), want in zip(HEADER, [8, 9, 10, 11, 12]):
    check(f"BeaconBlockHeader.{name}", container_gindex(len(HEADER), [f for f, _ in HEADER].index(name)), want)
for (name, _), want in zip(VALIDATOR, range(8, 16)):
    check(f"Validator.{name}", container_gindex(len(VALIDATOR), [f for f, _ in VALIDATOR].index(name)), want)

# --- 3. Light client constants --------------------------------------------------------------

print("\n== Light client FINALIZED_ROOT_GINDEX (specs/*/light-client/sync-protocol.md)")
for fork, const, want in (("deneb", "FINALIZED_ROOT_GINDEX", 105),
                          ("electra", "FINALIZED_ROOT_GINDEX_ELECTRA", 169),
                          ("gloas", "FINALIZED_ROOT_GINDEX_GLOAS", 735)):
    got = concat(state_gindex(fork, "finalized_checkpoint"), CHECKPOINT_ROOT)
    spec_file = {"deneb": "altair", "electra": "electra", "gloas": "gloas"}[fork]
    text = open(SPECS + spec_file + "/light-client/sync-protocol.md", encoding="utf-8").read()
    spec_value = int(re.search(rf"`{const}`\s*\|.*?\(= (\d+)\)", text).group(1))
    check(f"{const} computed", got, want)
    check(f"{const} equals the spec value", got, spec_value)

# --- 4. State field gindices: state gindex / gindex from the block root -------------------

print("\n== State field gindices (state / from block root)")
article_fields = {
    "slot": ((34, 354), (66, 706), (41, 361)),
    "validators": ((43, 363), (75, 715), (358, 2918)),
    "balances": ((44, 364), (76, 716), (359, 2919)),
    "finalized_checkpoint": ((52, 372), (84, 724), (367, 2927)),
    "current_sync_committee": ((54, 374), (86, 726), (2945, 23425)),
    "latest_execution_payload_header": ((56, 376), (88, 728), None),
    "historical_summaries": ((59, 379), (91, 731), (2950, 23430)),
    "earliest_exit_epoch": (None, (95, 735), (2954, 23434)),
    "pending_deposits": (None, (98, 738), (2957, 23437)),
    "pending_partial_withdrawals": (None, (99, 739), (2958, 23438)),
    "pending_consolidations": (None, (100, 740), (2959, 23439)),
    "proposer_lookahead": (None, None, (2960, 23440)),
}
for field, wants in article_fields.items():
    for fork, want in zip(("deneb", "electra", "gloas"), wants):
        g = state_gindex(fork, field)
        got = None if g is None else (g, concat(HEADER_STATE_ROOT, g))
        check(f"{fork} {field}", got, want)
check("fulu proposer_lookahead (Fulu only)", (state_gindex("fulu", "proposer_lookahead"),
      concat(HEADER_STATE_ROOT, state_gindex("fulu", "proposer_lookahead"))), (101, 741))
check("electra and fulu share every Electra gindex",
      all(state_gindex("electra", f) == state_gindex("fulu", f) for f in STATE["electra"]["fields"]), True)
check("heze keeps every Gloas gindex",
      all(state_gindex("heze", f) == state_gindex("gloas", f) for f in STATE["heze"]["fields"]), True)
check("heze gaps", sorted(set(range(46)) - set(STATE["heze"]["positions"].values())), [8, 9, 10, 28])
check("gloas latest_block_hash position", STATE["gloas"]["positions"]["latest_block_hash"], 24)

# --- 5. Worked example: withdrawal_credentials of validator 1,000,000 at Electra -----------

print("\n== Worked example (Electra, validator 1,000,000)")
steps = [("state_root in the header", HEADER_STATE_ROOT, 11),
         ("validators in a depth-6 state", state_gindex("electra", "validators"), 75),
         ("concat(11, 75)", concat(11, 75), 715),
         ("concat(715, 2)", concat(715, 2), 1430),
         ("concat(1430, 2**40 + 1000000)", concat(1430, 2**40 + 1000000), 1572301628719680),
         ("concat(..., 9)", concat(1430, 2**40 + 1000000, 9), 12578413029757441)]
for label, got, want in steps:
    check(label, got, want)
check("proof length of the worked gindex", proof_length(steps[-1][1]), 53)

# --- 6. Validator and balance leaves ---------------------------------------------------------

print("\n== Validator and balance leaves (gindex, proof length)")
check("deneb validator field proof length", proof_length(validator_field_gindex("deneb", 0)), 52)
check("electra validator field proof length", proof_length(validator_field_gindex("electra", 0)), 53)
check("deneb balance chunk proof length", proof_length(balance_chunk_gindex("deneb", 0)), 47)
check("electra balance chunk proof length", proof_length(balance_chunk_gindex("electra", 0)), 48)
leaves = [("withdrawal_credentials of validator 0", lambda f: validator_field_gindex(f, 0),
           6385963534123009, 12578413021757441, (93377, 16)),
          ("withdrawal_credentials of validator 1,000,000", lambda f: validator_field_gindex(f, 1000000),
           6385963542123009, 12578413029757441, (100278884853593, 46)),
          ("balance chunk of validator 1,000,000", lambda f: balance_chunk_gindex(f, 1000000),
           200111116505232, 393625162993808, (1567394265915, 40))]
for label, fn, w_deneb, w_electra, w_gloas in leaves:
    check(f"deneb {label}", fn("deneb"), w_deneb)
    check(f"electra {label}", fn("electra"), w_electra)
    g = fn("gloas")
    check(f"gloas {label} (gindex, length)", (g, proof_length(g)), w_gloas)
check("gloas validator 2,398,407 field proof length", proof_length(validator_field_gindex("gloas", 2398407)), 49)

# --- 7. Progressive list ranges -------------------------------------------------------------

print("\n== ProgressiveList subtrees: index range, k, length in list data, field proof length")
ranges = {0: (0, 0, 1, 16), 1: (1, 4, 4, 19), 2: (5, 20, 7, 22),
          9: (87381, 349524, 28, 43), 10: (349525, 1398100, 31, 46), 11: (1398101, 5592404, 34, 49)}
extra = proof_length(HEADER_STATE_ROOT) + proof_length(state_gindex("gloas", "validators")) + 1 \
    + proof_length(WITHDRAWAL_CREDENTIALS)
check("siblings around a validator field outside the list data (3 + 8 + 1 + 3)", extra, 15)
for k, want in ranges.items():
    lo, hi = (4**k - 1) // 3, (4**(k + 1) - 1) // 3 - 1
    inside = proof_length(progressive_gindex(lo))
    check(f"k={k}: indices, list-data length, field proof", (lo, hi, inside, inside + extra), want)
    check(f"k={k}: last index has the same length", proof_length(progressive_gindex(hi)), inside)

# --- 8. A Deneb verifier on a Fulu tree -----------------------------------------------------

print("\n== Deneb gindices read in the depth-6 Fulu state")
fulu = STATE["fulu"]["fields"]
PADDING = "0x" + hashlib.sha256(bytes(64)).hexdigest()
check("hash of two zero chunks", PADDING[:10], "0xf5a5fd42")
stale_deneb = {"slot": ("latest_block_header", "block_roots"),
               "validators": ("current_sync_committee", "next_sync_committee"),
               "balances": ("latest_execution_payload_header", "next_withdrawal_index"),
               "finalized_checkpoint": "padding", "current_sync_committee": "padding",
               "historical_summaries": "padding"}
for field, want in stale_deneb.items():
    g = state_gindex("deneb", field)
    first = 2 * (g - 32)  # a depth-5 node covers two depth-6 leaves
    covered = [fulu[j] for j in (first, first + 1) if j < len(fulu)]
    got = tuple(covered) if covered else "padding"
    check(f"deneb {field} (gindex {g}) in the Fulu tree", got, want)

# --- 9. A Fulu verifier on a Gloas tree -----------------------------------------------------

print("\n== Fulu gindices read in the Gloas tree (fixed depth 6)")
ONE_CHUNK = {"Uint64", "Root", "Slot", "Epoch", "Gwei", "Hash32", "ValidatorIndex", "WithdrawalIndex",
             "BuilderIndex", "JustificationBits"}
gloas_types = STATE["gloas"]["types"]
by_position = {p: f for f, p in STATE["gloas"]["positions"].items()}


def gloas_fate(g):
    """Walk the bits of a fixed-depth gindex through the Gloas ProgressiveContainer."""
    bits = bin(g)[3:]
    if bits[0] == "1":
        return "reverts: below the active_fields leaf" if len(bits) > 1 else "active_fields"
    bits = bits[1:]
    start, size = 0, 1  # progressive level: subtree of `size` leaves from position `start`
    while bits:
        b, bits = bits[0], bits[1:]
        if b == "1":  # right: the rest of the chain
            start, size = start + size, size * 4
            continue
        depth = size.bit_length() - 1  # left: the binary subtree
        if len(bits) < depth:
            lo = start + (int(bits, 2) << (depth - len(bits)) if bits else 0)
            hi = lo + (1 << (depth - len(bits))) - 1
            return f"verifies a hash: node over positions {lo} to {hi}"
        pos = start + (int(bits[:depth], 2) if depth else 0)
        rest = bits[depth:]
        field = by_position.get(pos)
        if not rest:
            return f"verifies: leaf {field}"
        if field is None or gloas_types[field] in ONE_CHUNK:
            return f"reverts: below the {field} leaf"
        sub = int("1" + rest, 2)  # gindex inside the field's own tree
        if gloas_types[field] == "Fork" and proof_length(sub) == depth_of(len(FORK)):
            return f"verifies: {field}.{FORK[sub - (1 << depth_of(len(FORK)))][0]}"
        if len(rest) == 1:
            return f"verifies a hash: {'left' if rest == '0' else 'right'} node of {field}"
        return f"verifies a hash: node {sub} inside {field}"
    return "data root"


stale_fulu = {"slot": "reverts: below the genesis_time leaf",
              "validators": "reverts: below the genesis_time leaf",
              "balances": "reverts: below the genesis_time leaf",
              "finalized_checkpoint": "verifies a hash: left node of fork",
              "current_sync_committee": "verifies a hash: left node of latest_block_header",
              "latest_execution_payload_header": "verifies a hash: node over positions 5 to 8",
              "historical_summaries": "verifies a hash: node over positions 17 to 20",
              "pending_deposits": "reverts: below the active_fields leaf",
              "proposer_lookahead": "reverts: below the active_fields leaf"}
for field, want in stale_fulu.items():
    g = state_gindex("fulu", field)
    check(f"fulu {field} (gindex {g}) in the Gloas tree", gloas_fate(g), want)
lc_electra = 169
check("electra FINALIZED_ROOT_GINDEX 169 in the Gloas state", gloas_fate(lc_electra), "verifies: fork.current_version")

# --- Summary ----------------------------------------------------------------------------------

failed = results.count(False)
print(f"\n{len(results)} checks, {len(results) - failed} PASS, {failed} FAIL")
sys.exit(1 if failed else 0)
