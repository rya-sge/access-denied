# PyPortfolioOpt article: verification

Scripts that produce every number quoted in
`_posts/2026-11-18-pyportfolioopt-portfolio-optimization.md`.

## What is tested

| Script | Article claims |
|---|---|
| `optimise.py` | data shape and NaN shares; Ledoit-Wolf shrinkage constant; BABA and FB volatility under `sample_cov` and under `CovarianceShrinkage.ledoit_wolf()` (zero-filled NaNs); max Sharpe (rf 2 % and 0 %), min volatility, `efficient_risk(0.20)`, `efficient_return(0.20)`; sector, bound and L2 constraints; `InstantiationError` on a reused object; the README `sample_cov` result (29.9 % / 21.8 % / 1.38); the common-window result; CLA; HRP (own estimators and under mu/LW); the order of the dict returned by `HRPOpt.optimize()`; min CVaR; the Black-Litterman single-view example (equal market caps, illustrative only). |
| `allocation.py` | greedy and LP allocations on fresh objects; greedy then LP on the same object (overspend); HRP `optimize()` dict passed to `lp_portfolio()` (overspend); one train/test split (fit 2014-09-19..2016-12-30, measure 2017-01-03..2018-04-11). |
| `black_litterman_prior.py` | "What you need to know first": the Black-Litterman posterior formula reproduces `bl_returns()` (toy 3-asset example, one view), and with no views an unconstrained optimiser at the same risk aversion returns the market weights 0.5 / 0.3 / 0.2. |
| `hrp_scipy118.py` | `HRPOpt.optimize()` raises `AttributeError` on SciPy 1.18.1 (`_LINKAGE_METHODS` removed). Needs network once for `pip install`. |
| `dump_for_check.py` | writes `w.json`, `alloc.json` and `alloc_bad.json` for the PyPortfolioOpt skill's `check_portfolio.py`. |

`optimise.out.txt` and `allocation.out.txt` are the outputs of the run used for the article
(2026-11-18), with solver banners and library warnings removed.

## Environment

PyPortfolioOpt at commit `a6638d2e06dae6f444fd022cfd4b3c528902a85b` (1.6.0 + 8 commits), installed from
source in a `python:3.12-slim` image: cvxpy 1.9.3, numpy 2.5.5, pandas 3.1.1, scipy 1.17.1 (pinned
below 1.18, see the article's HRP pitfall). Runs offline.

## How to run

The sample data is the library's own `tests/resources/stock_prices.csv` (20 US stocks, 1989-12-29 to
2018-04-11, SHA-256 `1f3bc5da6d4b589a34704be69a1a8cd382f643dbedbefbc73319c3b21d9d9c71`). It is not
copied here; take it from the repository at the pinned commit.

```bash
cp <PyPortfolioOpt>/tests/resources/stock_prices.csv .
pip install "pyportfolioopt==1.6.0" "scipy<1.18"   # or install the pinned commit from source
python3 optimise.py
python3 allocation.py
python3 black_litterman_prior.py
```

Numbers are in-sample estimates on historical data. They are not forecasts and not investment advice.
