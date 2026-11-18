# Portfolio optimisation concepts article: verification

Scripts that produce every number quoted in
`_posts/2026-11-18-portfolio-optimization-concepts-markowitz-black-litterman.md`.
All inputs are small toy examples (two to ten assets, simulated or hand-written returns), except
the Black-Litterman re-run on the PyPortfolioOpt sample prices.

## What is tested

| Script | Article claims |
|---|---|
| `returns_covariance.py` | simple vs log returns on 100 -> 150 -> 100; arithmetic vs geometric mean; annualisation (252, sqrt 252); volatility drag; CAPM (beta estimate, 3 % + 1.2 x 5 % = 9 %) and a CAPM estimate that comes out negative because the simulated market's realised return is negative; EMA vs plain mean; a sample covariance with T < n is singular (rank 39 for n = 50, T = 40); eigenvalue spread for n/T = 0.5 against the Marchenko-Pastur edges; Ledoit-Wolf intensity and error; true volatility of the minimum-variance portfolio built from the sample, Ledoit-Wolf identity-target and constant-correlation matrices; zero-filling 75 % missing returns halves a volatility; semicovariance by hand vs `risk_models.semicovariance`. |
| `markowitz.py` | 3-asset toy: frontier constants A, B, C, D; minimum-variance, tangency and frontier portfolios in closed form; two-fund theorem; quadratic utility with and without budget; the same portfolios from `EfficientFrontier` and `CLA`; CLA corner portfolios and the straight-line mix between them; `cvxpy` rejects a raw Sharpe objective (`DCPError`) and accepts the variable change; sensitivity of the tangency weights to a 1-point and to a one-standard-error change in one expected return. |
| `black_litterman.py` | reverse optimisation Pi = delta Sigma w_mkt and its inverse; delta = 0.07 / 0.16^2; one absolute view with Idzorek confidences 25 / 50 / 100 % (fraction of the gap closed), by hand and with `BlackLittermanModel`; one relative view with the He-Litterman Omega for three values of tau (posterior unchanged); posterior covariance; two views (fractions no longer equal to the confidence); re-run of the PyPortfolioOpt article's AAPL example (0.09791 -> 0.14896) when `stock_prices.csv` is in the directory. |
| `downside_hrp_allocation.py` | VaR and CVaR at 80 % of ten returns by sorting and by the Rockafellar-Uryasev LP; drawdown path, maximum drawdown, CDaR; HRP on four assets (distances, single linkage, order, bisection) by hand vs `HRPOpt`, with inverse-variance and minimum-variance weights; floor, greedy and integer-LP allocation of 1,000 over three prices. |
| `evaluation_mc.py` | 500 Monte Carlo replications, 10 assets, 60 monthly returns: in-sample vs true Sharpe ratio of the estimated max-Sharpe portfolio, estimated minimum-variance portfolio, equal weights; best in-sample Sharpe among 1, 10 and 100 zero-Sharpe strategies. |
| `qalc_checks.qalc` | the hand-computable numbers quoted in the article, one `qalc` expression per line. |

`*.out.txt` are the outputs of the run used for the article (2026-11-18), with the HiGHS solver
banner removed. The efficient-frontier figure is drawn by
`assets/article/finance/portfolio-optimization-concepts/efficient-frontier-three-assets.py` from the
same toy inputs and the corner portfolios printed by `markowitz.py`.

## Environment

PyPortfolioOpt at commit `a6638d2e06dae6f444fd022cfd4b3c528902a85b` (1.6.0 + 8 commits), installed from
source in a `python:3.12-slim` image: cvxpy 1.9.3, numpy 2.5.5, pandas 3.1.1, scipy 1.17.1 (below 1.18,
which breaks `HRPOpt`), scikit-learn 1.9.1, solvers CLARABEL, SCS, SCIPY, HIGHS, OSQP. Runs offline.
Random seeds are fixed in each script.

## How to run

```bash
pip install "pyportfolioopt==1.6.0" "scipy<1.18"   # or install the pinned commit from source
python3 returns_covariance.py
python3 markowitz.py
python3 downside_hrp_allocation.py
python3 evaluation_mc.py
# optional: copy tests/resources/stock_prices.csv from the PyPortfolioOpt repository at the pinned
# commit (SHA-256 1f3bc5da6d4b589a34704be69a1a8cd382f643dbedbefbc73319c3b21d9d9c71) for the AAPL re-run
python3 black_litterman.py
while read -r e; do qalc -t "$e"; done < qalc_checks.qalc
```

The toy inputs are illustrative. Nothing here is a forecast or investment advice.
