# ethereum-finality-lmd-ghost-casper-ffg

Verification code for the article *How Ethereum Finalises Blocks: LMD GHOST and Casper FFG*
(`_posts/2026-11-04-ethereum-finality-lmd-ghost-casper-ffg.md`).

## What this is

A small model that **executes the spec's own functions**. `spec_functions.py` holds 92
definitions copied verbatim from `ethereum/consensus-specs` at commit
`065bcd5c6ad96186cd2c0ac1c435f620a0b25373`, each from the newest fork up to Fulu that defines
it. `model.py` supplies the types and stubs they need, and `sim.py` runs the scenarios.

It is a model, not a beacon node, and it is not audited.

## Files

| File | Purpose |
|---|---|
| `extract_spec.py` | Regenerates or checks `spec_functions.py` from a consensus-specs checkout. |
| `spec_functions.py` | Generated, verbatim. Do not edit. |
| `model.py` | State, block and attestation types, the stubs below, `Net` (a node's view). |
| `sim.py` | Scenarios A to H, the source of every number in the article's worked example. |
| `cross_check.py` | Restates cases from the spec's test suite against the verbatim functions. |
| `run_output.txt` | Output of `sim.py`. |
| `cross_check_output.txt` | Output of `cross_check.py`. |

## Run

Standard library only. From this directory:

```bash
python3 -I sim.py                           # about 30 seconds
python3 -I cross_check.py                   # add a consensus-specs path for the verbatim check
python3 -I extract_spec.py <consensus-specs> --check
```

## What is stubbed or absent

- SSZ: `hash_tree_root` is a SHA-256 of the same field set.
- BLS: `is_valid_indexed_attestation` returns true.
- Shuffling: a committee is the validators with one index modulo `SLOTS_PER_EPOCH`, one per slot; the proposer is `slot % n`.
- `process_block` covers the header and attestations. `process_epoch` runs only justification, inactivity updates, rewards and penalties, effective balance updates and participation rotation, in spec order.
- Blobs: `is_data_available` returns true. Deposits, exits, ejection, withdrawals, sync committees and proposer rewards are absent.
- `SLOTS_PER_EPOCH` = 8 and `SLOTS_PER_HISTORICAL_ROOT` = 64, the minimal preset's values. All other constants are mainnet values.
- Scenario H caches `get_total_active_balance` and `get_unslashed_participating_indices` within an epoch, with no change in result, because the spec recomputes them per validator. Its first and third rows replace `get_flag_index_deltas` with zeros, to isolate inactivity penalties.
- Gloas and Heze are not executed: they are not live on mainnet, and the article discusses them in prose.

## Article claims that depend on it

| Scenario | Claim |
|---|---|
| A | Full-participation justification table, 87.5 % current share, first finalisation at the end of epoch 3. |
| B | All four finalisation rules fire: 123, 23, 234, 12. Stall in epochs 13 and 14. |
| C | Unrealised justification crosses at slot 30, realised at slot 32. |
| D | Weights, proposer boost, `get_proposer_head`, equivocation handling. |
| E | `filter_node_tree` keeps X where the pre-Capella test would keep only Z. |
| F | Two partitions finalise conflicting checkpoints with 22 of 64 validators slashable. |
| G | `is_slashable_attestation_data` cases, including asymmetry of the surround test. |
| H | Inactivity leak durations, compared with the book's ejection snippet. |

## Limits

`cross_check.py` restates the tests; it does not run the pyspec harness, which needs
`remerkleable` and a generated spec. Numbers describe rule behaviour on a small model. They
are not mainnet measurements, except where the article scales them explicitly.
