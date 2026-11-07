# grover-algorithm-quantum-search

Verification code for the article *Grover's Algorithm: Quantum Search and Its Real Cost for Symmetric Cryptography*
(`_posts/2026-11-06-grover-algorithm-quantum-search.md`).

## What this is

`verify_grover.py` builds the matrices `W`, `R` and `D` of Grover's paper, simulates the algorithm on a state vector and runs the Theorem 2 recurrence.

## What it checks

| Article claim | Check |
|---|---|
| `D = WRW`, `D² = I`, `D = -I + 2P`, inversion about the average | Explicit matrices for `n` = 2 to 5 |
| Theorem 3 gain and the `√(2N)` bound | Recurrence up to `N = 2^20` |
| `P_j = sin²((2j+1)θ)` | State-vector simulation for `N` up to 1024, several `M` |
| The `N = 8` table | Printed amplitudes |
| BBHT figures for `N = 2^20` (804, 596, 706, 9.5%, one in a million) | Closed form |
| BBHT Lemma 2 | Average over the iteration count |
| Toffoli-depth arithmetic of Kudinov and Nick | Exact integers |

It checks the mathematics only. Hardware and gate-cost figures from NIST and other sources are quoted, not recomputed.

## How to run

```bash
python3 verify_grover.py
```

It needs numpy and exits with a non-zero status if a check fails.
