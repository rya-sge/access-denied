#!/usr/bin/env python3
"""Replays scenarios from the spec's own test suite against the verbatim functions.

The pyspec harness needs remerkleable and a build, so the tests themselves are not run.
Each check below restates one test's setup and assertions; the test's name is printed
next to the result.  Run: python3 -I cross_check.py [path-to-consensus-specs]
"""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(sys.argv[0]).resolve().parent
sys.modules["model"] = type(sys)("model")
sys.modules["model"].__dict__.update({"__name__": "model", "__file__": str(HERE / "model.py")})
exec(compile((HERE / "model.py").read_text(), "model.py", "exec"), sys.modules["model"].__dict__)
from model import (AttesterSlashing, BeaconState, Checkpoint, IndexedAttestation,  # noqa: E402
                   Net, Root, build_spec)

ns = build_spec()
SPE = ns["SLOTS_PER_EPOCH"]
results = []


def check(name, condition):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


def checkpoints(epoch):
    return {k: Checkpoint(epoch - k, Root(bytes([0xa0 + k]) * 32)) for k in range(1, 6)
            if epoch >= k}


def mock_state(epoch, cps):
    state = BeaconState(ns, 64, 32 * 10**9)
    state.slot = SPE * epoch - 1
    for c in cps.values():
        state.block_roots[c.epoch * SPE % ns["SLOTS_PER_HISTORICAL_ROOT"]] = c.root
    return state


TOTAL = 64 * 32 * 10**9
GOOD = TOTAL * 2 // 3 + 1 * 10**9
POOR = TOTAL * 2 // 3 - 1 * 10**9


def weigh(state, previous, current):
    ns["weigh_justification_and_finalization"](state, TOTAL, previous, current)


def finalize_on_234(support):
    epoch = 6
    c = checkpoints(epoch)
    state = mock_state(epoch, c)
    old = state.finalized_checkpoint
    state.previous_justified_checkpoint, state.current_justified_checkpoint = c[4], c[3]
    state.justification_bits[1:3] = [True, True]
    return run_case(state, epoch, c, support, c[3], c[2], c[4], old)


def run_case(state, epoch, c, support, previous_after, current_after, finalized_after, old):
    # The test sits at slot SPE * epoch - 1, so current epoch = epoch - 1.  It mocks
    # attestations; here the resulting target balance is passed in directly.
    weigh(state, GOOD if support else POOR, 0)
    if support:
        return (state.previous_justified_checkpoint == previous_after
                and state.current_justified_checkpoint == current_after
                and state.finalized_checkpoint == finalized_after)
    return (state.previous_justified_checkpoint == previous_after
            and state.current_justified_checkpoint == c[3]
            and state.finalized_checkpoint == old)


def finalize_on_23(support):
    epoch = 5
    c = checkpoints(epoch)
    state = mock_state(epoch, c)
    old = state.finalized_checkpoint
    state.previous_justified_checkpoint = c[3]
    state.current_justified_checkpoint = c[3]
    state.justification_bits[1] = True
    return run_case(state, epoch, c, support, c[3], c[2], c[3], old)


def finalize_on_123(support):
    epoch = 7
    c = checkpoints(epoch)
    state = mock_state(epoch, c)
    old = state.finalized_checkpoint
    state.previous_justified_checkpoint, state.current_justified_checkpoint = c[5], c[3]
    state.justification_bits[1] = True
    weigh(state, GOOD if support else POOR, GOOD if support else POOR)
    if support:
        return (state.previous_justified_checkpoint == c[3]
                and state.current_justified_checkpoint == c[1]
                and state.finalized_checkpoint == c[3])
    return (state.previous_justified_checkpoint == c[3]
            and state.current_justified_checkpoint == c[3]
            and state.finalized_checkpoint == old)


def finalize_on_12(support):
    epoch = 4
    c = checkpoints(epoch)
    state = mock_state(epoch, c)
    old = state.finalized_checkpoint
    state.previous_justified_checkpoint = c[2]
    state.current_justified_checkpoint = c[2]
    state.justification_bits[0] = True
    weigh(state, 0, GOOD if support else POOR)
    if support:
        return (state.previous_justified_checkpoint == c[2]
                and state.current_justified_checkpoint == c[1]
                and state.finalized_checkpoint == c[2])
    return (state.previous_justified_checkpoint == c[2]
            and state.current_justified_checkpoint == c[2]
            and state.finalized_checkpoint == old)


print("# test_process_justification_and_finalization.py")
for name, fn in (("234", finalize_on_234), ("23", finalize_on_23),
                 ("123", finalize_on_123), ("12", finalize_on_12)):
    check(f"test_{name}_ok_support", fn(True))
    check(f"test_{name}_poor_support", fn(False))

print("# threshold of weigh_justification_and_finalization")
state = BeaconState(ns, 3, 32 * 10**9)
state.slot = SPE * 4 - 1
state.block_roots[3 * SPE % ns["SLOTS_PER_HISTORICAL_ROOT"]] = Root(b"x" * 32)
ns["weigh_justification_and_finalization"](state, 3, 0, 2)
check("exactly two thirds justifies (>=, not >)", state.current_justified_checkpoint.epoch == 3)


print("# test_get_head.py")
net = Net(ns)
one, root_one = net.make_block(1, net.genesis_root)
two, root_two = net.make_block(1, net.genesis_root, graffiti=b"\x42" * 32)
net.tick(2)
net.receive(one)
net.receive(two)
check("test_split_tie_breaker_no_attestations: higher root wins",
      net.head() == max(root_one, root_two))

net = Net(ns)
parent = net.genesis_root
for slot in (1, 2, 3):
    net.tick(slot)
    signed, parent = net.make_block(slot, parent)
    net.receive(signed)
long_root = parent
short, short_root = net.make_block(1, net.genesis_root, graffiti=b"\x42" * 32)
net.receive(short)
check("test_shorter_chain_but_heavier_weight: long chain while boosted",
      net.head() == long_root)
attestation = net.attestation_for(short_root, 1, net.committee(1))
net.tick(4)
ns["on_attestation"](net.store, attestation)
check("test_shorter_chain_but_heavier_weight: short block after one committee vote",
      net.head() == short_root)

net = Net(ns)
head_1, root_1 = net.make_block(1, net.genesis_root)
head_2, root_2 = net.make_block(1, net.genesis_root, graffiti=b"\x42" * 32)
net.tick(2)
net.receive(head_1)
net.receive(head_2)
low, high = sorted((root_1, root_2))
attestation = net.attestation_for(low, 1, net.committee(1)[:2])
ns["on_attestation"](net.store, attestation)
check("test_discard_equivocations_on_attester_slashing: votes lift the lower root",
      net.head() == low)
conflict = net.attestation_for(high, 1, net.committee(1)[:2])
ns["on_attester_slashing"](net.store, AttesterSlashing(
    IndexedAttestation(attestation.data, attestation.attesting_indices),
    IndexedAttestation(conflict.data, conflict.attesting_indices)))
check("test_discard_equivocations_on_attester_slashing: equivocators removed, tie-break back",
      net.head() == high)

print("# test_ex_ante.py")
net = Net(ns)
net.tick(1)
signed_a, a = net.make_block(1, net.genesis_root)
net.receive(signed_a)
check("test_ex_ante_vanilla: A is head", net.head() == a)
signed_b, b = net.make_block(2, a)
signed_c, c = net.make_block(3, a)
net.tick(3)
net.receive(signed_c)
check("test_ex_ante_vanilla: C is head", net.head() == c)
net.receive(signed_b)
check("test_ex_ante_vanilla: C is head after B", net.head() == c)
vote = net.attestation_for(b, 2, net.committee(2)[:1])
ns["on_attestation"](net.store, vote)
check("test_ex_ante_vanilla: C is head after the single vote", net.head() == c)

print("# is_slashable_attestation_data, both orders of the surround")
from model import AttestationData as D  # noqa: E402
outer, inner = (D(40, 0, Root(b"x"), Checkpoint(2), Checkpoint(5)),
                D(32, 0, Root(b"y"), Checkpoint(3), Checkpoint(4)))
check("outer first is slashable", ns["is_slashable_attestation_data"](outer, inner))
check("inner first is not: callers must try the outer attestation first",
      not ns["is_slashable_attestation_data"](inner, outer))

if len(sys.argv) > 1:
    print("# verbatim check")
    done = subprocess.run([sys.executable, "-I", str(HERE / "extract_spec.py"), sys.argv[1],
                           "--check"], capture_output=True, text=True)
    print(done.stdout.strip())
    check("spec_functions.py equals a fresh extraction", done.returncode == 0)

print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
