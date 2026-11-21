# beacon-state-proofs-hard-fork-deneb-to-gloas

Verification code for the article *When a Merkle Proof Breaks at a Hard Fork: Beacon State
Proofs from Deneb to Gloas* (`_posts/2026-11-04-beacon-state-proofs-hard-fork-deneb-to-gloas.md`).

Four parts:

| Part | Files | Network | What it shows |
|---|---|---|---|
| Offline figures | `gindex.py`, `run_output.txt` | no | every gindex, depth, proof length and stale-path outcome printed in the article (133 checks) |
| Historical mainnet values | `mainnet_history.py`, `mainnet_history.json`, `mainnet_history_output.txt` | yes, or `--offline` | the article's headers, roots and first-Electra-block values, **reproduced exactly** (18 checks) |
| The method on a fresh state | `ssz_state.py`, `mainnet_state.py`, `snapshot.json`, `mainnet_state_output.txt`, `mainnet_state_snapshot_output.txt` | yes, or `--snapshot` | the whole hashing and proof method, re-run on the finalized state of slot 15,687,296 (2026-11-19): **same method, different values** (31 checks online, 15 offline) |
| Solidity verifier | `foundry.toml`, `src/`, `test/`, `forge_test_output.txt`, `gas_report.txt`, `forge_fork_output.txt` | no, except the fork test | the article's verifier, copied verbatim, on the real 53-sibling proof of `snapshot.json` (14 tests, plus one fork test) |

`beacon_net.py` holds the HTTP helpers and the list of public endpoints used by the two mainnet
scripts.

## Offline figures: `gindex.py`

`gindex.py` recomputes every **offline** figure of the article from the consensus specs and
checks it against the value the article prints: 133 checks, one `PASS`/`FAIL` line each, exit
code 1 on any `FAIL`.

| Article section | Figures checked |
|---|---|
| Fork table | Fork epochs, first slots and timestamps (also against the dates in the config comments), `BeaconState` field counts (28 / 37 / 38 / 46 / 42), depths, Gloas and Heze as `ProgressiveContainer` |
| SSZ background | `BeaconBlockHeader` field gindices 8 to 12, `Validator` field gindices 8 to 15 |
| Light client check | 105, 169 and 735, each also compared with the `(= …)` value in `specs/{altair,electra,gloas}/light-client/sync-protocol.md` |
| Field gindex table | State gindex and gindex from the block root for the 12 listed fields at Deneb, Electra/Fulu and Gloas; Heze keeps every Gloas gindex; Heze gaps 8, 9, 10, 28; `latest_block_hash` at position 24 |
| Worked example | 11, 75, 715, 1,430, 1,572,301,628,719,680, 12,578,413,029,757,441 and the 53-sibling proof |
| Validator and balance leaves | Proof lengths 52 / 53 / 47 / 48, the six Deneb and Electra gindices, the Gloas gindices with lengths 16, 46, 40, and length 49 for validator 2,398,407 |
| Progressive list ranges | The six rows: index range, `k`, length inside the list data, field proof length, and the 15 siblings outside the list |
| Deneb verifier on Fulu | Which Fulu fields (or padding) each stale Deneb gindex covers; the padding hash `0xf5a5fd42…` = `sha256` of 64 zero bytes |
| Fulu verifier on Gloas | The outcome of the nine fixed-depth paths (reverts below a one-chunk leaf, or verifies a hash of a node), and gindex 169 landing on `fork.current_version` |

Inputs: `ethereum/consensus-specs` at commit `065bcd5c6ad96186cd2c0ac1c435f620a0b25373`
(2026-10-23); the script parses `specs/<fork>/beacon-chain.md`, `specs/*/light-client/sync-protocol.md`
and `configs/mainnet.yaml`. One constant is not in the spec: the mainnet genesis time `1606824023`,
from `/eth/v1/beacon/genesis`, checked indirectly (genesis plus `slot × 12 s` must equal the UTC
date next to each fork epoch in the config).

Rules implemented: `concat_generalized_indices` and `floorlog2` proof lengths from
`ssz/merkle-proofs.md`; EIP-7916 progressive Merkle tree (`merkleize_progressive` = `hash(a, b)`,
`a` the first `num_leaves` chunks, `b` the rest, `num_leaves` = 1, 4, 16, …); EIP-7495 progressive
container (data at gindex 2, `active_fields` at gindex 3). A mutated copy with the two progressive
children swapped fails 8 Gloas checks, including the spec's own `FINALIZED_ROOT_GINDEX_GLOAS`; this
was run once to confirm the checks can fail.

## Historical mainnet values: `mainnet_history.py` (exact reproduction)

Public beacon and execution APIs still serve the headers and blocks the article used, so these
values are reproduced exactly, from the network, on 2026-11-19:

| Article value | Check | Result |
|---|---|---|
| Header at slot 15,580,064, `state_root` `0x966c88c1…e72a` | served by PublicNode, prefix and suffix | PASS |
| Block root `0xa544aac2…36b3`, the full value printed by the article's `cast call` | `hash_tree_root` of the 5 header fields, recomputed locally, equals the API root and the article's value | PASS |
| Execution block 26,340,577, timestamp 1793784803 = genesis + 15,580,065 × 12 | `eth_getBlockByNumber` | PASS |
| Its `parentBeaconBlockRoot` equals `0xa544aac2…`, ring index 4949, root slot 13,140 | same block; arithmetic | PASS |
| Empty-proof "slot" 14,741,254,758,814,336,165 and one-sibling "slot" 11,533,380,310,597,772,962 (H-01 discussion) | first 8 bytes of the root, and of the header node at gindex 2; three siblings give 15,580,064 | PASS |
| First Electra block: execution block 22,431,084, timestamp 1746612311 = Electra fork timestamp | `eth_getBlockByNumber` | PASS |
| Its `parentBeaconBlockRoot` `0x947d2274…552967` is the root of slot 11,649,023, a Deneb block | header 11,649,023 fetched, root recomputed, equal; 11,649,023 < 11,649,024 | PASS |

The execution block's `parentBeaconBlockRoot` is the value the EIP-4788 system call writes into the
ring buffer, so it stands in for the article's `eth_call`, which can no longer be repeated (see
below). The script tries PublicNode first, then other public endpoints (`lodestar-mainnet.chainsafe.io`
for beacon headers; it does serve slot 11,649,023 but not 15,580,064). Each request and the endpoint
that answered are recorded in `mainnet_history.json`.

## The method on a fresh state: `ssz_state.py` and `mainnet_state.py`

Checkpoint sync servers serve only the current finalized state, so the article's state at slot
15,580,064 cannot be downloaded again. `mainnet_state.py` re-runs the whole method on the finalized
state of **2026-11-19**:

- slot **15,687,296**, 340,047,725 bytes of SSZ, version `fulu`, **2,411,196** validators, from the
  Attestant checkpoint sync endpoint (a first attempt stalled at about 41 MB and was restarted);
- `hash_tree_root(state)` = `0xa09951c3…78ad74` = the header's `state_root` (PASS; 69 to 77 s in
  pure Python);
- block root `0xc30d8027…c0aa91`, recomputed from the header and equal to the API root;
- the 53-sibling branch for `withdrawal_credentials` of validator 1,000,000 (gindex
  12,578,413,029,757,441) verifies with the Python port of `is_valid_merkle_branch`; the 52-sibling
  truncation does not;
- EIP-4788: the child block, slot 15,687,297, carries execution block 26,447,488 with timestamp
  1795071587; its `parentBeaconBlockRoot` and an `eth_call` to `0x000F3df6…Beac02` at that timestamp
  (PublicNode, latest block 26,447,618) both return the block root; timestamp + 1 reverts with empty
  data (PASS).

**Values differ from the article's**, because the state differs. Unchanged ones: validator
1,000,000 is still exited (activation 239,886, exit 252,630, withdrawable 252,886, effective balance
0, balance 0), its credentials end in `…60936f`, its `Validator` root is `0x1d90dc6e…5d104c` as in the
article, 18 of the 40 list siblings are empty-subtree roots, gindex 105 is a zero leaf with a valid
6-sibling branch, gindex 2,829 is `fork.current_version` `0x06000000`. New values on this state:

| Article (slot 15,580,064) | This run (slot 15,687,296) |
|---|---|
| state root `0x966c88c1…ece72a`, block root `0xa544aac2…9e36b3` | `0xa09951c3…78ad74`, `0xc30d8027…c0aa91` |
| list data root `0x34af4e59…`, `validators` root `0x40665bcf…` | `0x4ef51813…af3fd843`, `0x84e5e9be…bb9f7c` |
| state gindex 2 `0x8b6c017a…`, gindex 3 `0xa5a2aef7…` | `0x02f6a1df…a07943`, `0xc6172d8f…d2d9c0` |
| stale gindex 34 `0xf6c0cf2d…` (5,674,632,966,883,492,086 as `uint64`) | `0xb6c0179f…` (17,720,692,817,201,184,950) |
| stale gindex 43 `0x3a752dcb…` | `0x49f5361f…` |
| stale gindex 44 `0x88a146c5…` | `0x14b6f6ba…` |
| stale gindices 52, 54, 59 `0xf5a5fd42…` | same (padding) |

Every stale Deneb gindex verifies with a five-sibling branch at depth 5, the covered fields are those
of the article's table, and the deep paths end where the article says: the Deneb validator path
(52 levels) on the first chunk of `current_sync_committee.pubkeys[0]` at depth 20, the balance path
(47 levels) on `latest_execution_payload_header.parent_hash` at depth 14. All of this is in
`snapshot.json` (17 KB, no state bytes), with the branches, so it can be re-verified offline.

`ssz_state.py` is a minimal SSZ implementation for these types only, working on serialized bytes:
`Uint`, `Boolean`, `ByteVector` (a `Bytes48` is two chunks), `ByteList`, `Bitvector`, `Bitlist`,
`Vector`, `List` (depth from the limit in chunks, length mix-in), `Container`, the Fulu
`BeaconState` (38 fields, types from the pinned spec) and `BeaconBlockHeader`. `Tree.node(g)` and
`Tree.get_branch(g)` descend through nested subtrees, and raise `BelowLeaf` for a gindex below a leaf
chunk. `is_valid_merkle_branch` and `compute_merkle_branch_root` are ports of
`specs/phase0/beacon-chain.md`. Its self-test checks the details the article flags (participation
lists at depth 35, `proposer_lookahead` 16 chunks at depth 4, `Bytes48`, bitfields, the zero hashes).

## Solidity verifier: Foundry

`src/BeaconProof.sol` is the article's `BeaconProof` library, copied verbatim (a `diff` against the
article's code block is empty); only a header comment, the SPDX line and the pragma were added.
`src/ProgressiveGindex.sol` holds the article's Gloas `progressiveGindex`, unchanged, but wrapped in a
library: as printed in the article (a top-level function marked `internal`), it does not compile
(`Error (4126): Free functions cannot have visibility`). Both are reference code: not audited, do not
deploy. `test/BeaconProof.t.sol` adds a `Harness` contract with external entry points, so the gas
report can measure them, and a minimal cheatcode interface (no forge-std). Pinned: solc 0.8.28, EVM
`cancun`, optimizer 200 runs, Forge 1.5.0. solc warns that `verify` could be `pure` (warning 2018).

`forge test -vv --offline`: 14 passed, 0 failed (`forge_test_output.txt`):

- the real 53-sibling proof of `snapshot.json` verifies, with the gindex returned by
  `validatorFieldGindex(15_687_296, 1_000_000, 1)`;
- 52-sibling truncation and 54-sibling extension revert `BadProofLength`; an empty proof with
  `leaf == root` reverts `BadProofLength` for the field gindex, for gindex 1 and for gindex 8; a wrong
  leaf reverts `BadProof`;
- the 3-sibling slot proof (gindex 8) and the 48-sibling balance proof (gindex 393,625,162,993,808)
  verify;
- Deneb and Electra gindices of the article's tables (validators 0 and 1,000,000, 52 and 53 levels,
  363 = `concat(11, 43)`, 715 = `concat(11, 75)`), slot 11,649,023 → 363 and 11,649,024 → 715; the
  Deneb gindex with the 53 Fulu siblings reverts `BadProofLength`, with 52 of them `BadProof`;
  `index >= 2**40` and `field >= 8` revert `IndexTooLarge`;
- Gloas arithmetic with `progressiveGindex`: 93,377 (length 16), 100,278,884,853,593 (length 46),
  1,567,394,265,915 (length 40), length 49 for validator 2,398,407. This checks gindices only, not a
  hashed Gloas tree.

Gas (`gas_report.txt`, execution gas of the external call, no intrinsic cost):

| Measure | This run | Article |
|---|---|---|
| `verify`, 53-sibling proof (`--match-test testRealProofVerifies`) | 43,483 | 43,417 |
| `verify`, 48-sibling balance proof | 39,454 | not given |
| Full flow on forked mainnet: 4788 read + slot proof + field proof (`verifyWithdrawalCredentials`) | 56,837 | 55,659 |

The figures are close but not equal: the article's harness was not published, and selector dispatch
and the slot encoding (`le64` here) change the total by a few dozen to about a thousand gas. With EVM
`shanghai` (no `MCOPY`) the same `verify` costs 51,592; `prague` gives 43,483 like `cancun`.

The fork test needs `FORK_URL` and the snapshot root still in the 4788 buffer (about 27 hours after
2026-11-19T07:25Z); without `FORK_URL` it logs that it was skipped and passes. It was run once
against the public PublicNode RPC at block 26,447,637 (`forge_fork_output.txt`): the 4788 read
returned the snapshot block root, timestamp + 1 reverted `NoRoot`, and the full flow verified.

## Run

From this directory. Python: standard library only. Run Python with `-I`; the scripts add their own
directory to `sys.path`.

```bash
python3 -I gindex.py <path to consensus-specs checkout>      # offline, under a second
python3 -I ssz_state.py                                      # SSZ self-test, offline

python3 -I mainnet_history.py                                # online: rewrites mainnet_history.json
python3 -I mainnet_history.py --offline                      # re-checks mainnet_history.json

python3 -I mainnet_state.py --data-dir <dir outside the repo> # online: ~340 MB download, about 10 min,
                                                              # rewrites snapshot.json
python3 -I mainnet_state.py --snapshot                        # offline, from snapshot.json

forge test -vv --offline
forge test --gas-report --offline
FORK_URL=<public RPC URL> forge test --match-test testForkFullFlow -vv --gas-report
```

An online run of `mainnet_state.py` replaces `snapshot.json` with a newer state, so the Foundry
tests then run on that proof; the fork test works only within about 27 hours of that run. The
downloaded state is untrusted input: keep it in its own directory, outside this repository, and do
not commit it.

Endpoints used, all public and without a key: `ethereum-beacon-api.publicnode.com`,
`lodestar-mainnet.chainsafe.io` (fallback), `mainnet-checkpoint-sync.attestant.io`,
`sync-mainnet.beaconcha.in` (fallback), `ethereum-rpc.publicnode.com`. The scripts send a generic
User-Agent and nothing else.

## What is still not reproducible, and why

- **The article's state at slot 15,580,064.** Checkpoint sync serves only the current finalized
  state, and PublicNode's beacon API refuses `/eth/v2/debug/beacon/states` (HTTP 501). Everything
  derived from that state's contents stays unverified: the 339,268,193-byte size, the 2,398,408
  validator count, the recomputation of `0x966c88c1…` from the state bytes (the header value itself
  is verified), the walk nodes `0x34af4e59…` and `0x40665bcf…`, the gindex 2 and 3 nodes, and the
  stale values `0xf6c0cf2d…`, `0x3a752dcb…`, `0x88a146c5…`. An archive beacon node, or a state
  archived on 2026-11-04, would be needed.
- **The article's `eth_call` at timestamp 1793784803.** That ring-buffer entry was overwritten about
  27 hours later; PublicNode refuses historical state for older blocks without a token. The block's
  `parentBeaconBlockRoot` is verified instead.
- **The exact gas figures 43,417 and 55,659.** They depend on the unpublished harness; see the table
  above.
- **The Gloas proofs on 2,398,408 real `Validator` roots inside a synthetic state.** Not rebuilt here:
  only the gindex arithmetic is tested (`gindex.py`, `testGloasProgressiveGindices`).

Not audited; a reading aid for the article, not a library.
