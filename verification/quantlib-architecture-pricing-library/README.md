# QuantLib article: verification

Code behind the numbers of `_posts/2026-11-18-quantlib-architecture-pricing-library.md`.
Every value printed in the article comes from a run of these files; `expected_output.txt` holds the
output of the last run (2026-11-18).

## What is tested

| File | Claims in the article |
|---|---|
| `equity_option.py` | European call 9.41340 (analytic), 9.41375 (finite differences), 9.4044 ± 0.0315 (Monte Carlo, 200,000 paths, seed 42); closed form; Greeks; put-call parity; American put on a CRR tree; spot and vol bumps through `SimpleQuote`; expiry after maturity; up-and-out barrier 1.15537. |
| `moving_reference_date.py` | A curve built with a date keeps that reference date when the evaluation date moves; a curve built with settlement days follows it (9.41340 → 6.40005, closed form with T = 184/365). |
| `rates.py` | Deposit + swap bootstrap reprices its helpers; 5Y fair rate 3.40000 % with matching conventions, 3.39981 % when the curve's 5Y helper uses an `Unadjusted` fixed leg (0.0188 bp); payer swap NPV; fixed-rate bond clean / dirty / accrued / yield / duration / convexity. |
| `main.cpp` | The same European call from C++ against libQuantLib master (1.45-dev): 9.41340, then 12.63876 after a quote change and 11.34848 after relinking the volatility handle. |

## How to run

The scripts need only Docker, through the `docker-quantlib` wrapper (`qldock`). From this directory:

```bash
qldock py -n -r equity_option.py          # QuantLib-Python 1.44 (PyPI wheel)
qldock py -n -r moving_reference_date.py
qldock py -n -r rates.py
qldock cxx -n main.cpp                    # C++, library built from QuantLib master at 1c418a9
```

Without the wrapper: `pip install QuantLib==1.44` and `python3 <file>`; for C++,
`g++ -std=c++17 main.cpp -lQuantLib` against an installed QuantLib.

Evaluation date 15 January 2025 everywhere, so the results do not depend on the day the code runs.
