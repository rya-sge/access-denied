"""Thin model that runs the verbatim spec functions in spec_functions.py.

This is a model, not a beacon node.  What is stubbed is listed in README.md.
The module is loaded with exec by sim.py and cross_check.py, because `python3 -I`
leaves the script directory off sys.path.
"""
import copy
import dataclasses
import hashlib
import pathlib
import sys
import types
from collections import defaultdict
from dataclasses import dataclass, field

HERE = pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")


class Root(bytes):
    pass


Bytes32 = Root
Uint64 = Uint8 = Slot = Epoch = Gwei = ValidatorIndex = CommitteeIndex = ParticipationFlags = int
Boolean = bool


def h(*parts):
    return Root(hashlib.sha256(repr(parts).encode()).digest())


@dataclass(frozen=True)
class Checkpoint:
    epoch: int = 0
    root: Root = Root()


@dataclass(frozen=True)
class AttestationData:
    slot: int
    index: int
    beacon_block_root: Root
    source: Checkpoint
    target: Checkpoint


@dataclass
class Attestation:
    data: AttestationData
    attesting_indices: tuple


@dataclass
class IndexedAttestation:
    data: AttestationData
    attesting_indices: tuple


@dataclass
class AttesterSlashing:
    attestation_1: IndexedAttestation
    attestation_2: IndexedAttestation


@dataclass
class Validator:
    effective_balance: int
    activation_epoch: int = 0
    exit_epoch: int = 2**64 - 1
    withdrawable_epoch: int = 2**64 - 1
    slashed: bool = False
    withdrawal_credentials: bytes = b"\x01" + bytes(31)


@dataclass
class BeaconBlockHeader:
    slot: int = 0
    proposer_index: int = 0
    parent_root: Root = Root()
    state_root: Root = Root()
    body_root: Root = Root()


@dataclass
class BeaconBlockBody:
    attestations: list = field(default_factory=list)
    graffiti: bytes = b""


@dataclass
class BeaconBlock:
    slot: int = 0
    proposer_index: int = 0
    parent_root: Root = Root()
    state_root: Root = Root()
    body: BeaconBlockBody = field(default_factory=BeaconBlockBody)

    def copy(self):
        return copy.deepcopy(self)


@dataclass
class SignedBeaconBlock:
    message: BeaconBlock


def body_root(body):
    return h("body", [(a.data, a.attesting_indices) for a in body.attestations], body.graffiti)


def hash_tree_root(obj):
    """Stand-in for SSZ: a stable hash of the same field set."""
    if isinstance(obj, (BeaconBlock, BeaconBlockHeader)):
        body = obj.body_root if isinstance(obj, BeaconBlockHeader) else body_root(obj.body)
        return h("block", obj.slot, obj.proposer_index, obj.parent_root, obj.state_root, body)
    if isinstance(obj, BeaconState):
        return h("state", obj.slot, obj.balances, obj.justification_bits,
                 obj.current_justified_checkpoint, obj.previous_justified_checkpoint,
                 obj.finalized_checkpoint, obj.block_roots, obj.latest_block_header,
                 obj.previous_epoch_participation, obj.current_epoch_participation,
                 obj.inactivity_scores, [v.effective_balance for v in obj.validators])
    raise TypeError(type(obj))


class BeaconState:
    def __init__(self, cfg, n, balance):
        hist = cfg["SLOTS_PER_HISTORICAL_ROOT"]
        self.slot = 0
        self.genesis_time = 0
        self.validators = [Validator(effective_balance=balance) for _ in range(n)]
        self.balances = [balance] * n
        self.block_roots = [Root()] * hist
        self.state_roots = [Root()] * hist
        self.latest_block_header = BeaconBlockHeader(body_root=body_root(BeaconBlockBody()))
        self.justification_bits = [False] * 4
        self.previous_justified_checkpoint = Checkpoint()
        self.current_justified_checkpoint = Checkpoint()
        self.finalized_checkpoint = Checkpoint()
        self.previous_epoch_participation = [0] * n
        self.current_epoch_participation = [0] * n
        self.inactivity_scores = [0] * n
        self.slashings = [0] * cfg["EPOCHS_PER_SLASHINGS_VECTOR"]

    def copy(self):
        return copy.deepcopy(self)


MAINNET = dict(
    # phase0 preset and config, mainnet
    SLOTS_PER_EPOCH=32, SLOTS_PER_HISTORICAL_ROOT=8192, SLOT_DURATION_MS=12000,
    MIN_SEED_LOOKAHEAD=1, MIN_ATTESTATION_INCLUSION_DELAY=1,
    MIN_EPOCHS_TO_INACTIVITY_PENALTY=4, JUSTIFICATION_BITS_LENGTH=4,
    EFFECTIVE_BALANCE_INCREMENT=10**9, MAX_EFFECTIVE_BALANCE=32 * 10**9,
    MIN_ACTIVATION_BALANCE=32 * 10**9, MAX_EFFECTIVE_BALANCE_ELECTRA=2048 * 10**9,
    HYSTERESIS_QUOTIENT=4, HYSTERESIS_DOWNWARD_MULTIPLIER=1, HYSTERESIS_UPWARD_MULTIPLIER=5,
    BASE_REWARD_FACTOR=64, EPOCHS_PER_SLASHINGS_VECTOR=8192,
    GENESIS_EPOCH=0, GENESIS_SLOT=0, UINT64_MAX=2**64 - 1, FAR_FUTURE_EPOCH=2**64 - 1,
    BASIS_POINTS=10000, COMPOUNDING_WITHDRAWAL_PREFIX=b"\x02",
    # altair
    TIMELY_SOURCE_FLAG_INDEX=0, TIMELY_TARGET_FLAG_INDEX=1, TIMELY_HEAD_FLAG_INDEX=2,
    TIMELY_SOURCE_WEIGHT=14, TIMELY_TARGET_WEIGHT=26, TIMELY_HEAD_WEIGHT=14,
    PROPOSER_WEIGHT=8, WEIGHT_DENOMINATOR=64, PARTICIPATION_FLAG_WEIGHTS=[14, 26, 14],
    INACTIVITY_SCORE_BIAS=4, INACTIVITY_SCORE_RECOVERY_RATE=16,
    # bellatrix
    INACTIVITY_PENALTY_QUOTIENT_BELLATRIX=2**24, PROPORTIONAL_SLASHING_MULTIPLIER_BELLATRIX=3,
    # fork choice
    PROPOSER_SCORE_BOOST=40, REORG_HEAD_WEIGHT_THRESHOLD=20, REORG_PARENT_WEIGHT_THRESHOLD=160,
    REORG_MAX_EPOCHS_SINCE_FINALIZATION=2, PROPOSER_REORG_CUTOFF_BPS=1667,
    ATTESTATION_DUE_BPS=3333,
)


def build_spec(slots_per_epoch=8, hist=64, name="spec_ns"):
    """Return a namespace holding the verbatim spec with `slots_per_epoch` slots."""
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    ns = mod.__dict__
    ns.update(MAINNET)
    ns.update(SLOTS_PER_EPOCH=slots_per_epoch, SLOTS_PER_HISTORICAL_ROOT=hist)
    ns.update({k: v for k, v in globals().items() if k in {
        "Root", "Bytes32", "Uint64", "Uint8", "Slot", "Epoch", "Gwei", "ValidatorIndex",
        "CommitteeIndex", "ParticipationFlags", "Boolean", "Checkpoint", "AttestationData",
        "Attestation", "IndexedAttestation", "AttesterSlashing", "BeaconBlock", "BeaconState",
        "SignedBeaconBlock", "Validator", "hash_tree_root"}})
    ns["dataclass"] = dataclass
    ns["Sequence"] = list
    ns["EpochParticipation"] = lambda data: list(data)
    source = (HERE / "spec_functions.py").read_text(encoding="utf-8")
    exec(compile("from __future__ import annotations\n" + source, "spec_functions.py", "exec"), ns)

    # ---- stubs: everything below is model code, not spec code -----------------------------
    def get_beacon_proposer_index(state):
        return state.slot % len(state.validators)

    def get_beacon_committee(state, slot, index):
        return [i for i in range(len(state.validators))
                if i % ns["SLOTS_PER_EPOCH"] == slot % ns["SLOTS_PER_EPOCH"]]

    def get_committee_count_per_slot(state, epoch):
        return 1

    def get_indexed_attestation(state, attestation):
        return IndexedAttestation(attestation.data, tuple(attestation.attesting_indices))

    def process_block(state, block):
        assert block.slot == state.slot
        assert block.parent_root == hash_tree_root(state.latest_block_header)
        state.latest_block_header = BeaconBlockHeader(
            block.slot, block.proposer_index, block.parent_root, Root(), body_root(block.body))
        for attestation in block.body.attestations:
            data = attestation.data
            assert data.target.epoch in (ns["get_previous_epoch"](state),
                                         ns["get_current_epoch"](state))
            assert data.target.epoch == ns["compute_epoch_at_slot"](data.slot)
            assert data.slot + ns["MIN_ATTESTATION_INCLUSION_DELAY"] <= state.slot
            flags = ns["get_attestation_participation_flag_indices"](
                state, data, state.slot - data.slot)
            participation = (state.current_epoch_participation
                             if data.target.epoch == ns["get_current_epoch"](state)
                             else state.previous_epoch_participation)
            for index in attestation.attesting_indices:
                for flag in flags:
                    participation[index] = ns["add_flag"](participation[index], flag)

    def process_epoch(state):
        # Subset of process_epoch, in the spec's order.  Registry, slashings and resets are
        # omitted: nothing in the scenarios depends on them.
        ns["process_justification_and_finalization"](state)
        ns["process_inactivity_updates"](state)
        ns["process_rewards_and_penalties"](state)
        ns["process_effective_balance_updates"](state)
        ns["process_participation_flag_updates"](state)

    def state_transition(state, signed_block, validate_result=True):
        block = signed_block.message
        ns["process_slots"](state, block.slot)
        process_block(state, block)
        if validate_result:
            assert block.state_root == hash_tree_root(state)

    ns.update(get_beacon_proposer_index=get_beacon_proposer_index,
              get_beacon_committee=get_beacon_committee,
              get_committee_count_per_slot=get_committee_count_per_slot,
              get_indexed_attestation=get_indexed_attestation,
              is_valid_indexed_attestation=lambda state, indexed: True,
              is_data_available=lambda root: True,
              process_block=process_block, process_epoch=process_epoch,
              state_transition=state_transition)
    return ns


class Net:
    """One node's view: a Store, the wall clock, and block and attestation builders."""

    def __init__(self, ns, n=64, balance=32 * 10**9, genesis=None):
        self.ns = ns
        self.n = n
        if genesis is None:
            state = BeaconState(ns, n, balance)
            block = BeaconBlock(state_root=hash_tree_root(state))
            genesis = (state, block)
        self.genesis_state, self.genesis_block = genesis
        self.store = ns["get_forkchoice_store"](self.genesis_state, self.genesis_block)
        self.genesis_root = hash_tree_root(self.genesis_block)
        self.names = {self.genesis_root: "G"}

    def label(self, root):
        return self.names.get(root, root.hex()[:6])

    def cp(self, c):
        name = self.names.get(c.root)
        return f"{c.epoch}" + (f"/{name}" if name else "")

    def tick(self, slot, ms=0):
        self.ns["on_tick"](self.store, self.store.genesis_time_ms
                           + slot * self.ns["SLOT_DURATION_MS"] + ms)

    def make_block(self, slot, parent, attestations=(), name=None, graffiti=b""):
        ns = self.ns
        state = self.store.block_states[parent].copy()
        ns["process_slots"](state, slot)
        block = BeaconBlock(slot, ns["get_beacon_proposer_index"](state), parent, Root(),
                            BeaconBlockBody(list(attestations), graffiti))
        ns["process_block"](state, block)
        block.state_root = hash_tree_root(state)
        root = hash_tree_root(block)
        if name:
            self.names[root] = name
        return SignedBeaconBlock(block), root

    def receive(self, signed):
        self.ns["on_block"](self.store, signed)
        return hash_tree_root(signed.message)

    def attestation_for(self, head_root, slot, indices):
        """Honest attestation data, from the rules in specs/phase0/validator.md."""
        ns = self.ns
        state = self.store.block_states[head_root].copy()
        if state.slot < slot:
            ns["process_slots"](state, slot)
        epoch = ns["compute_epoch_at_slot"](slot)
        start = ns["compute_start_slot_at_epoch"](epoch)
        boundary = head_root if start == state.slot else ns["get_block_root"](state, epoch)
        data = AttestationData(slot, 0, head_root, state.current_justified_checkpoint,
                               Checkpoint(epoch, boundary))
        return Attestation(data, tuple(sorted(indices)))

    def committee(self, slot):
        return list(self.ns["get_beacon_committee"](self.genesis_state, slot, 0))

    def weight(self, root):
        return self.ns["get_weight"](self.store, self.ns["ForkChoiceNode"](root=root))

    def head(self):
        return self.ns["get_head"](self.store).root


def eth(gwei):
    value = gwei / 10**9
    return f"{value:g}"
