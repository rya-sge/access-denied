# Transient storage: verification

Code behind the article "Transient Storage in Practice: Reentrancy Locks, Solidity's `transient` and Two Real Failures". Test contracts only: not audited, do not deploy.

Pinned: solc 0.8.38 (bug profiles 0.8.33, 0.8.34, 0.8.38), EVM `cancun`, optimizer on with 200 runs, Foundry 1.5.0. No dependency install: `src/Common.sol` defines a minimal `Vm` interface, and the compilers are read from `~/.svm`.

## How to run

From this directory:

```bash
forge test -vv --offline                             # semantics, locks, stipend, failures, init flag
forge build --offline && python3 scripts/gas.py      # receipts on anvil, Cancun rules
python3 compile/matrix.py                            # accept/reject per solc release
for p in bug-0833-ir bug-0833-ir-noopt bug-0833-legacy bug-0834-ir bug-0838-ir; do
  FOUNDRY_PROFILE=$p forge test -vv --offline
done
solc --evm-version cancun --storage-layout --transient-storage-layout compile/layout.sol
```

`isolate = true` makes each top-level call of a test its own transaction. One transaction is modelled with one call to `Tx.exec` in `src/Common.sol`.

## Which claim depends on what

| Claim | Code |
|---|---|
| Scope, per-contract space, rollback, DELEGATECALL, CALLCODE, static context | `test/Semantics.t.sol` |
| Every lock accepts two calls in a transaction and blocks a nested one | `test/Locks.t.sol` |
| Gas of each lock | `scripts/gas.py` on `src/Locks.sol` |
| Stipend recipient writes transient state, also the payer's through a call back; storage is refused | `test/Stipend.t.sol` |
| Leaky lock, assembly `return`, open flash-loan flag, residue across a bundle | `test/Failures.t.sol` |
| Startale model: drained in the deploying transaction, safe later, stopped by consuming the flag | `test/InitFlag.t.sol` |
| `TransientStorageClearingHelperCollision` in both directions | `bug/`, profiles `bug-*`. On `bug-0833-ir*` four tests fail by design: they assert correct behaviour. `testAssignmentAvoidsTheBug` passes everywhere |
| Version history, unsupported forms, warning 2394 | `compile/matrix.py` |
| Layout | `compile/layout.sol` |

`src/vendor/oz-v5.1.0/` holds three unmodified OpenZeppelin Contracts v5.1.0 files (MIT).

`MiniBundler` is a stand-in for `EntryPoint.handleOps`, and `src/InitFlag.sol` is a reduced model of the Startale contracts. Neither is the real code. The real Startale PoC is in `evm-hack-registry/2026-09-Startale_exp`.

## Results of the last run

Date 2026-11-04. `forge test`: 23 passed, 0 failed.

```text
gas in receive at entry: 2241
gas left after the call back into the payer: 1608
gas consumed by a failed static TSTORE, 50000 forwarded: 52976
```

Receipts (`gasUsed`, after refunds):

```text
| lock | guarded | unguarded | work | unwork | batch1 | batch2 | batch10 |
| LockTransientYul | 24267 | 23983 | 133318 | 133034 | 28031 | 29183 | 38402 |
| LockTransientUint | 24278 | 23983 | 133329 | 133034 | 28042 | 29205 | 38512 |
| LockTransientBool | 24511 | 23983 | 133562 | 133034 | 28275 | 29671 | 40842 |
| LockOZTransient | 24405 | 23983 | 133456 | 133034 | 28169 | 29459 | 39782 |
| LockOZStorage | 26310 | 23983 | 135361 | 133034 | 30074 | 31269 | 55066 |
| LockStorageBool | 37126 | 23983 | 135558 | 133034 | 40128 | 57161 | 193432 |

overhead = guarded - unguarded, work = guardedWork - unguardedWork
LockTransientYul: lock-only overhead 284, with work 284
LockTransientUint: lock-only overhead 295, with work 295
LockTransientBool: lock-only overhead 528, with work 528
LockOZTransient: lock-only overhead 422, with work 422
LockOZStorage: lock-only overhead 2327, with work 2327
LockStorageBool: lock-only overhead 13143, with work 2524
tget(0) in the next transaction: 0
```

Compiler bug, `run()` returns `(s, t)`, correct is `(0, 0)`:

| Profile | `PersistentFirst` | `TransientFirst` | `GuardedVault` owner kept | Second `close` |
|---|---|---|---|---|
| 0.8.33 via-IR, optimizer on and off | `(0, 1)` | `(1, 0)` | no | reverts `locked` |
| 0.8.33 legacy | `(0, 0)` | `(0, 0)` | yes | ok |
| 0.8.34 via-IR | `(0, 0)` | `(0, 0)` | yes | ok |
| 0.8.38 via-IR | `(0, 0)` | `(0, 0)` | yes | ok |
