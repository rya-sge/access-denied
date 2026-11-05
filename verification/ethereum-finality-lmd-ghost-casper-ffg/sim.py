#!/usr/bin/env python3
"""Scenarios behind the worked examples of the article.  Run: python3 -I sim.py"""
import pathlib
import sys

HERE = pathlib.Path(sys.argv[0]).resolve().parent
model = {"__name__": "model", "__file__": str(HERE / "model.py")}
sys.modules["model"] = type(sys)("model")
sys.modules["model"].__dict__.update(model)
exec(compile((HERE / "model.py").read_text(), "model.py", "exec"), sys.modules["model"].__dict__)
from model import (AttesterSlashing, IndexedAttestation, Net, build_spec, eth,  # noqa: E402
                   BeaconState, Checkpoint, Root, h)


def bits(state):
    return "".join("1" if b else "0" for b in state.justification_bits)


def share_of(state, ns, field):
    """Target share in percent, read from the last block before the epoch boundary."""
    flags = getattr(state, field)
    with_target = sum(1 for f in flags if ns["has_flag"](f, ns["TIMELY_TARGET_FLAG_INDEX"]))
    return 100 * with_target / len(flags)


def run_chain(ns, epochs, policy, net=None, stop_slot=None, on_slot=None):
    """Drive one honest chain: a block every slot, attestations at the deadline.

    policy(slot, committee) returns (attesters, include_slot).  Attestations reach the
    fork choice on the wire in the next slot, and a block at include_slot.
    """
    net = net or Net(ns)
    pool, wire = {}, []
    spe = ns["SLOTS_PER_EPOCH"]
    head = net.genesis_root
    rows = []
    last = stop_slot or epochs * spe + 1
    for slot in range(1, last + 1):
        net.tick(slot)
        for attestation in wire:
            ns["on_attestation"](net.store, attestation)
        wire = []
        parent = net.head()
        signed, root = net.make_block(slot, parent, pool.pop(slot, []))
        net.receive(signed)
        if slot % spe == 0:
            # the first block of an epoch carries the state after the boundary
            state = net.store.block_states[root]
            epoch_ended = slot // spe - 1
            prev = state.previous_justified_checkpoint
            before = net.store.block_states[net.store.blocks[root].parent_root]
            rows.append(dict(epoch=epoch_ended, bits=bits(state),
                             prev_share=share_of(before, ns, "previous_epoch_participation"),
                             cur_share=share_of(before, ns, "current_epoch_participation"),
                             current=state.current_justified_checkpoint.epoch,
                             previous=prev.epoch, finalized=state.finalized_checkpoint.epoch))
        net.tick(slot, ns["get_attestation_due_ms"]())
        head = net.head()
        attesters, include = policy(slot, net.committee(slot))
        if attesters:
            attestation = net.attestation_for(head, slot, attesters)
            wire.append(attestation)
            pool.setdefault(include, []).append(attestation)
        if on_slot:
            on_slot(net, slot, root)
    net.pending_wire = wire
    return net, rows


def rule_fired(prev, row):
    """Which finalization rule produced row, from the bit pattern and old checkpoints."""
    if row["finalized"] == prev["finalized"]:
        return "-"
    e = row["epoch"]
    b = row["bits"]
    if all(c == "1" for c in b[0:2]) and prev["current"] + 1 == e:
        return "12"
    if all(c == "1" for c in b[0:3]) and prev["current"] + 2 == e:
        return "123"
    if all(c == "1" for c in b[1:3]) and prev["previous"] + 2 == e:
        return "23"
    if all(c == "1" for c in b[1:4]) and prev["previous"] + 3 == e:
        return "234"
    return "?"


def print_rows(rows):
    print("epoch-end | prev target % | cur target % | bits[0..3] | previous_just | "
          "current_just | finalized | rule")
    prev = dict(current=0, previous=0, finalized=0)
    for row in rows:
        print(f"{row['epoch']:9d} | {row['prev_share']:13.2f} | {row['cur_share']:12.2f} | "
              f"{row['bits']:10s} | {row['previous']:13d} | "
              f"{row['current']:12d} | {row['finalized']:9d} | {rule_fired(prev, row)}")
        prev = row


def scenario_happy(ns):
    print("\n## A. Full participation, 8 slots per epoch, 64 validators of 32 ETH")
    spe = ns["SLOTS_PER_EPOCH"]
    _, rows = run_chain(ns, 6, lambda slot, c: (c, slot + 1))
    print_rows(rows)
    print("note: the last committee of an epoch is included in the next epoch's first block,")
    print("so the current-epoch target share at the boundary is 7/8 =", 7 / 8 * 100, "%")


def scenario_rules(ns):
    print("\n## B. Late inclusion: every finalization rule fires")
    spe = ns["SLOTS_PER_EPOCH"]
    late_epochs = {5, 7, 8, 9, 10, 11}
    missed = {13, 14}

    def policy(slot, committee):
        epoch = slot // spe
        position = slot % spe
        if epoch in missed and position >= 5:
            return [], 0
        if epoch in late_epochs and position >= 3:
            # the votes exist and reach the fork choice, but no block carries them this epoch
            return committee, (epoch + 1) * spe + 1
        return committee, slot + 1

    net, rows = run_chain(ns, 18, policy)
    print("late inclusion in epochs", sorted(late_epochs), "(committees 3..7 included in the next")
    print("epoch, so 3/8 on time); committees 5..7 absent in epochs", sorted(missed))
    print_rows(rows)
    return rows


def scenario_unrealized(ns):
    print("\n## C. Unrealized justification and the pull-up (full participation)")
    spe = ns["SLOTS_PER_EPOCH"]
    log = []

    def observe(net, slot, root):
        store = net.store
        state = store.block_states[root]
        epoch = slot // spe
        if 3 * spe <= slot <= 4 * spe + 1:
            log.append((slot, epoch, slot % spe, state.current_justified_checkpoint.epoch,
                        store.justified_checkpoint.epoch,
                        store.unrealized_justified_checkpoint.epoch,
                        store.finalized_checkpoint.epoch,
                        store.unrealized_finalized_checkpoint.epoch))

    run_chain(ns, 5, lambda slot, c: (c, slot + 1), on_slot=observe)
    print("slot | epoch | pos | block-state just | store.just | store.unreal_just | store.fin | "
          "store.unreal_fin")
    for row in log:
        print("{:4d} | {:5d} | {:3d} | {:16d} | {:10d} | {:17d} | {:9d} | {:d}".format(*row))


def scenario_fork_choice(ns):
    print("\n## D. Fork choice: weights, late block, proposer boost, get_proposer_head, equivocation")
    net = Net(ns)
    store = net.store
    # Slot 1: block A. Its committee votes for A.
    net.tick(1)
    signed, a = net.make_block(1, net.genesis_root, name="A")
    net.receive(signed)
    net.tick(1, ns["get_attestation_due_ms"]())
    vote_a1 = net.attestation_for(a, 1, net.committee(1))
    # Slot 2: block B arrives after the deadline; seven attesters saw an empty slot and vote
    # A, one saw B.
    net.tick(2)
    ns["on_attestation"](store, vote_a1)
    net.tick(2, ns["get_attestation_due_ms"]())
    committee = net.committee(2)
    vote_a2 = net.attestation_for(a, 2, committee[1:])
    signed, b = net.make_block(2, a, [vote_a1], name="B")
    late_ms = 5000
    net.tick(2, late_ms)
    net.receive(signed)
    vote_b2 = net.attestation_for(b, 2, committee[:1])
    print(f"block B received {late_ms} ms into slot 2, deadline "
          f"{ns['get_attestation_due_ms']()} ms, timely = {store.block_timeliness[b]}")
    # Slot 3
    net.tick(3)
    ns["on_attestation"](store, vote_a2)
    ns["on_attestation"](store, vote_b2)
    print("start of slot 3, before any block:")
    print(f"  weight A = {eth(net.weight(a))} ETH, weight B = {eth(net.weight(b))} ETH, "
          f"head = {net.label(net.head())}")
    node = ns["ForkChoiceNode"](root=b)
    proposer_head = ns["get_proposer_head"](store, node, 3)
    print(f"  get_proposer_head at slot 3 = {net.label(proposer_head.root)} "
          f"(is_head_late={ns['is_head_late'](store, b)}, "
          f"is_head_weak={ns['is_head_weak'](store, b)}, "
          f"is_parent_strong={ns['is_parent_strong'](store, b)})")
    state = store.checkpoint_states[store.justified_checkpoint]
    print(f"  committee weight = {eth(ns['get_total_active_balance'](state) // ns['SLOTS_PER_EPOCH'])}"
          f" ETH, boost = {eth(ns['get_proposer_score'](store))} ETH, reorg head threshold = "
          f"{eth(ns['calculate_committee_fraction'](state, ns['REORG_HEAD_WEIGHT_THRESHOLD']))} ETH, "
          f"parent threshold = "
          f"{eth(ns['calculate_committee_fraction'](state, ns['REORG_PARENT_WEIGHT_THRESHOLD']))} ETH")
    signed, c = net.make_block(3, proposer_head.root, [vote_a2], name="C")
    net.receive(signed)
    print(f"timely block C on {net.label(proposer_head.root)}, boost root = "
          f"{net.label(store.proposer_boost_root)}")
    for name, root in (("A", a), ("B", b), ("C", c)):
        print(f"  weight {name} = {eth(net.weight(root))} ETH")
    print(f"  head with boost = {net.label(net.head())}")
    saved = store.proposer_boost_root
    store.proposer_boost_root = Root()
    print(f"  head if the boost were zero: weight C = {eth(net.weight(c))} ETH, "
          f"head = {net.label(net.head())}")
    store.proposer_boost_root = saved
    # Slot 3 committee votes for the head, C
    net.tick(3, ns["get_attestation_due_ms"]())
    vote_c3 = net.attestation_for(net.head(), 3, net.committee(3))
    net.tick(4)
    ns["on_attestation"](store, vote_c3)
    print("start of slot 4 (boost reset by on_tick), slot 3 committee counted:")
    print(f"  boost root empty = {store.proposer_boost_root == Root()}; weight B = "
          f"{eth(net.weight(b))} ETH, weight C = {eth(net.weight(c))} ETH, "
          f"head = {net.label(net.head())}")
    # Equivocation: five of the C voters are shown to have signed a conflicting vote.
    offenders = net.committee(3)[:5]
    conflicting = net.attestation_for(b, 3, offenders)
    slashing = AttesterSlashing(
        IndexedAttestation(vote_c3.data, tuple(offenders)),
        IndexedAttestation(conflicting.data, tuple(offenders)))
    ns["on_attester_slashing"](store, slashing)
    print(f"on_attester_slashing for {len(offenders)} of the C voters:")
    print(f"  equivocating_indices = {sorted(store.equivocating_indices)}")
    print(f"  weight B = {eth(net.weight(b))} ETH, weight C = {eth(net.weight(c))} ETH, "
          f"head = {net.label(net.head())}")
    before = store.latest_messages[offenders[0]]
    net.tick(4, ns["get_attestation_due_ms"]())
    net.tick(5)
    later = net.attestation_for(c, 4, offenders)
    ns["on_attestation"](store, later)
    print(f"  later vote by an offender ignored: "
          f"{store.latest_messages[offenders[0]] == before}")


def old_correct_justified(store, root):
    """The pre-Capella test, quoted in the book (Part 3, Unrealised justification)."""
    head_state = store.block_states[root]
    return (store.justified_checkpoint.epoch == 0
            or head_state.current_justified_checkpoint == store.justified_checkpoint)


def scenario_filter(ns):
    print("\n## E. filter_node_tree against the unrealized justification reorg")
    spe = ns["SLOTS_PER_EPOCH"]
    keep = {}

    def observe(net, slot, root):
        keep[slot] = root

    # Run to the last slot of epoch 3; blocks W(slot 30), X(31) exist with votes.
    net, _ = run_chain(ns, 4, lambda slot, c: (c, slot + 1), stop_slot=4 * spe - 1, on_slot=observe)
    store = net.store
    x, w = keep[4 * spe - 1], keep[4 * spe - 2]
    net.names[x], net.names[w] = "X", "W"
    print(f"last block X at slot {store.blocks[x].slot}, its parent W at slot {store.blocks[w].slot}")
    print(f"unrealized justified epoch of W = {store.unrealized_justifications[w].epoch}, "
          f"of X = {store.unrealized_justifications[x].epoch}")
    print(f"block-state justified epoch of X = "
          f"{store.block_states[x].current_justified_checkpoint.epoch}")
    # First slot of epoch 4: an adversarial proposer builds Z on W, skipping X.
    net.tick(4 * spe)
    for attestation in net.pending_wire:
        ns["on_attestation"](store, attestation)
    signed, z = net.make_block(4 * spe, w, name="Z")
    print(f"at slot {4 * spe}: store.justified = {store.justified_checkpoint.epoch} (pulled up by "
          f"on_tick_per_slot)")
    net.receive(signed)
    print(f"Z built on W, timely, boost root = {net.label(store.proposer_boost_root)}; "
          f"block-state justified of Z = "
          f"{store.block_states[z].current_justified_checkpoint.epoch}")
    for name, root in (("X", x), ("Z", z)):
        source = ns["get_voting_source"](store, root)
        print(f"  {name}: get_voting_source.epoch = {source.epoch}, viable now = "
              f"{ns['ForkChoiceNode'](root=root) in ns['get_filtered_node_tree'](store)}, "
              f"pre-Capella correct_justified = {old_correct_justified(store, root)}, "
              f"weight = {eth(net.weight(root))} ETH")
    print(f"  head under the current filter = {net.label(net.head())}")
    # Under the old test only Z would survive.
    survivors = [name for name, root in (("X", x), ("Z", z))
                 if old_correct_justified(store, root)]
    print(f"  leaves surviving the pre-Capella test = {survivors}")


def scenario_conflict(ns):
    print("\n## F. Conflicting finalization needs at least 1/3 slashable (network partition)")
    spe = ns["SLOTS_PER_EPOCH"]
    both = {i for i in range(64) if i % 3 == 0}
    only = {"left": {i for i in range(64) if i % 3 == 1},
            "right": {i for i in range(64) if i % 3 == 2}}
    print(f"double signers {len(both)}, left only {len(only['left'])}, "
          f"right only {len(only['right'])}")
    results, votes = {}, {}
    for side in ("left", "right"):
        votes[side] = {}

        def policy(slot, committee, side=side):
            return [i for i in committee if i in both or i in only[side]], slot + 1

        net = Net(ns, genesis=None)
        # Split at the first block: the two sides see different graffiti.
        pool, wire = {}, []
        for slot in range(1, 9 * spe + 1):
            net.tick(slot)
            for attestation in wire:
                ns["on_attestation"](net.store, attestation)
            wire = []
            signed, root = net.make_block(slot, net.head(), pool.pop(slot, []),
                                          graffiti=side.encode())
            net.receive(signed)
            net.tick(slot, ns["get_attestation_due_ms"]())
            attesters, include = policy(slot, net.committee(slot))
            if attesters:
                attestation = net.attestation_for(net.head(), slot, attesters)
                wire.append(attestation)
                pool.setdefault(include, []).append(attestation)
                for i in attesters:
                    votes[side][i] = attestation.data if i in both else None
        state = net.store.block_states[net.head()]
        results[side] = (net, state)
        print(f"{side}: finalized {state.finalized_checkpoint.epoch} "
              f"root {state.finalized_checkpoint.root.hex()[:10]}, justified "
              f"{state.current_justified_checkpoint.epoch}")
    left_cp = results["left"][1].finalized_checkpoint
    right_cp = results["right"][1].finalized_checkpoint
    print("conflicting finalized checkpoints:", left_cp.root != right_cp.root)
    slashable = [i for i in sorted(both)
                 if ns["is_slashable_attestation_data"](votes["left"][i], votes["right"][i])]
    total = 64 * 32
    print(f"slashable validators from the last votes: {len(slashable)} = "
          f"{len(slashable) * 32} ETH of {total} ETH = {100 * len(slashable) / 64:.3f} %")


def scenario_slashing_predicate(ns):
    print("\n## G. is_slashable_attestation_data")
    from model import AttestationData as D
    c = lambda e, r=b"a": Checkpoint(e, Root(r))
    cases = [
        ("same vote twice", D(16, 0, Root(b"x"), c(2), c(3)), D(16, 0, Root(b"x"), c(2), c(3))),
        ("same target epoch, different target root", D(24, 0, Root(b"x"), c(2), c(3, b"p")),
         D(24, 0, Root(b"y"), c(2), c(3, b"q"))),
        ("same FFG vote, different head", D(24, 0, Root(b"x"), c(2), c(3)),
         D(24, 0, Root(b"y"), c(2), c(3))),
        ("surround: 2->5 around 3->4", D(40, 0, Root(b"x"), c(2), c(5)),
         D(32, 0, Root(b"y"), c(3), c(4))),
        ("reversed argument order: 3->4 then 2->5", D(32, 0, Root(b"y"), c(3), c(4)),
         D(40, 0, Root(b"x"), c(2), c(5))),
        ("adjacent links 2->3, 3->4", D(24, 0, Root(b"x"), c(2), c(3)),
         D(32, 0, Root(b"y"), c(3), c(4))),
        ("shared source 2->4, 2->5", D(32, 0, Root(b"x"), c(2), c(4)),
         D(40, 0, Root(b"y"), c(2), c(5))),
    ]
    for name, one, two in cases:
        print(f"  {name}: {ns['is_slashable_attestation_data'](one, two)}")


def leak_run(n, offline, attestation_penalties=True, cap=6000):
    ns = build_spec(slots_per_epoch=8, hist=64, name=f"leak_{n}_{offline}_{attestation_penalties}")
    state = BeaconState(ns, n, 32 * 10**9)
    spe = ns["SLOTS_PER_EPOCH"]
    # The spec recomputes these per validator; caching within an epoch changes nothing and
    # makes a long run possible.
    participating = ns["get_unslashed_participating_indices"]
    total_active = ns["get_total_active_balance"]
    cache = {}

    def cached_participating(state, flag, epoch):
        return cache.setdefault(("p", flag, epoch), participating(state, flag, epoch))

    def cached_total(state):
        return cache.setdefault("t", total_active(state))

    ns["get_unslashed_participating_indices"] = cached_participating
    ns["get_total_active_balance"] = cached_total
    if not attestation_penalties:
        ns["get_flag_index_deltas"] = lambda state, flag: ([0] * n, [0] * n)
    online_flags = 0b111
    start_offline = 8   # stable, finalizing chain first
    log = {}
    for epoch in range(cap):
        cache.clear()
        last_slot = (epoch + 1) * spe - 1
        for slot in range(state.slot, last_slot):
            state.block_roots[slot % ns["SLOTS_PER_HISTORICAL_ROOT"]] = h("root", slot)
        state.slot = last_slot
        share = range(n - offline if epoch >= start_offline else n)
        for i in share:
            state.current_epoch_participation[i] = online_flags
        before = state.finalized_checkpoint.epoch
        leak_before = ns["is_in_inactivity_leak"](state)
        ns["process_epoch"](state)
        state.slot += 1
        if "leak" not in log and epoch >= start_offline and ns["is_in_inactivity_leak"](state):
            log["leak"] = epoch
        if epoch >= start_offline:
            if "justified" not in log and state.current_justified_checkpoint.epoch > log.get(
                    "stalled_just", -1) and state.current_justified_checkpoint.epoch > start_offline:
                log["justified"] = (epoch, state.current_justified_checkpoint.epoch)
            if state.finalized_checkpoint.epoch > start_offline - 2 and "finalized" not in log \
                    and state.finalized_checkpoint.epoch != before:
                log["finalized"] = (epoch, state.finalized_checkpoint.epoch)
                log["balance"] = state.balances[n - 1]
                log["effective"] = state.validators[n - 1].effective_balance
                log["score"] = state.inactivity_scores[n - 1]
                log["online_balance"] = state.balances[0]
                log["share"] = (100 * (n - offline) * state.validators[0].effective_balance
                                / sum(v.effective_balance for v in state.validators))
                break
    log["start"] = start_offline
    return log


def scenario_leak():
    print("\n## H. Inactivity leak, verbatim epoch processing, state only")
    for n, offline, penalties in ((300, 102, False), (300, 102, True), (30, 15, False)):
        log = leak_run(n, offline, penalties)
        just = log.get("justified")
        final = log.get("finalized")
        print(f"N={n}, offline={offline} ({100 * offline / n:.1f} %), attestation penalties="
              f"{penalties}: offline from epoch {log['start']}")
        print(f"  leak first true after epoch {log.get('leak')}; next justification at end of "
              f"epoch {just[0] if just else None}; finality back at end of epoch "
              f"{final[0] if final else None} (finalized {final[1] if final else None})")
        if final:
            print(f"  {final[0] - log['start']} epochs after the failure; offline validator: "
                  f"balance {log['balance'] / 10**9:.4f} ETH, effective "
                  f"{log['effective'] / 10**9:g} ETH, score {log['score']}; online share of "
                  f"effective balance {log['share']:.2f} %")


def book_ejection():
    GWEI = 10**9
    EJECTION_BALANCE = 16 * GWEI
    MAX_EFFECTIVE_BALANCE = 32 * GWEI
    HYSTERESIS_QUOTIENT = 4
    INACTIVITY_SCORE_BIAS = 4
    INACTIVITY_PENALTY_QUOTIENT = 2**24

    def calc(balance):
        return min(MAX_EFFECTIVE_BALANCE, (balance + GWEI // HYSTERESIS_QUOTIENT) // GWEI * GWEI)

    epoch, score = 0, 0
    balance = 32 * GWEI
    effective = calc(balance)
    while effective > EJECTION_BALANCE:
        balance -= effective * score // (INACTIVITY_SCORE_BIAS * INACTIVITY_PENALTY_QUOTIENT)
        effective = calc(balance)
        score += INACTIVITY_SCORE_BIAS
        epoch += 1
    print(f"\nbook's ejection snippet (Part 2, Inactivity leak): {epoch} epochs, "
          f"balance {balance / GWEI:.4f} ETH")


def main():
    ns = build_spec()
    print(f"SLOTS_PER_EPOCH={ns['SLOTS_PER_EPOCH']}, attestation due "
          f"{ns['get_attestation_due_ms']()} ms, reorg cutoff {ns['get_proposer_reorg_cutoff_ms']()} ms")
    scenario_happy(ns)
    scenario_rules(ns)
    scenario_unrealized(ns)
    scenario_fork_choice(ns)
    scenario_filter(ns)
    scenario_conflict(ns)
    scenario_slashing_predicate(ns)
    scenario_leak()
    book_ejection()


main()
