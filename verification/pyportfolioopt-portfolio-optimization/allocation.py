"""Discrete allocation checks quoted in the PyPortfolioOpt article.

    pfodock py -n -r allocation.py
"""

import warnings

import numpy as np
import pandas as pd

from pypfopt import EfficientFrontier, HRPOpt, expected_returns, risk_models
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

warnings.filterwarnings("ignore", category=FutureWarning)  # lp_portfolio default-solver notice

BUDGET = 10_000
prices = pd.read_csv("stock_prices.csv", parse_dates=True, index_col="date")
latest = get_latest_prices(prices)
mu = expected_returns.mean_historical_return(prices)
S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
ef = EfficientFrontier(mu, S)
ef.max_sharpe(risk_free_rate=0.02)
w = ef.clean_weights()


def spent(alloc):
    return float(sum(latest[t] * n for t, n in alloc.items()))


def report(label, alloc, leftover):
    print(f"{label}: {len(alloc)} lines, spent {spent(alloc):.2f}, "
          f"leftover reported {leftover:.2f}, budget {BUDGET}")


a, left = DiscreteAllocation(w, latest, total_portfolio_value=BUDGET).greedy_portfolio()
report("greedy (fresh object)", a, left)
a, left = DiscreteAllocation(w, latest, total_portfolio_value=BUDGET).lp_portfolio()
report("lp (fresh object)", a, left)

da = DiscreteAllocation(w, latest, total_portfolio_value=BUDGET)
da.greedy_portfolio()
a, left = da.lp_portfolio()
report("greedy then lp (same object)", a, left)

# HRP: optimize() returns its dict sorted by ticker, clean_weights() keeps column order.
rets = expected_returns.returns_from_prices(prices)
hrp = HRPOpt(rets)
w_sorted = hrp.optimize()
w_cols = hrp.clean_weights()
a, left = DiscreteAllocation(dict(w_cols), latest, total_portfolio_value=BUDGET).lp_portfolio()
report("HRP clean_weights -> lp", a, left)
a, left = DiscreteAllocation(dict(w_sorted), latest, total_portfolio_value=BUDGET).lp_portfolio()
report("HRP optimize() dict -> lp", a, left)
a, left = DiscreteAllocation(dict(w_sorted), latest, total_portfolio_value=BUDGET).greedy_portfolio()
report("HRP optimize() dict -> greedy", a, left)

# Out-of-sample illustration: fit on a common window up to 2016-12-30, measure 2017-01-03..2018-04-11.
pc = prices.loc[prices["BABA"].first_valid_index():].dropna()
train, test = pc.loc[:"2016-12-31"], pc.loc["2017-01-01":]
print(f"\ntrain {train.index.min().date()}..{train.index.max().date()} ({len(train)} rows), "
      f"test {test.index.min().date()}..{test.index.max().date()} ({len(test)} rows)")
mu_t = expected_returns.mean_historical_return(train)
S_t = risk_models.CovarianceShrinkage(train).ledoit_wolf()
test_rets = test.pct_change().dropna()


def realised(weights):
    wv = np.array([weights.get(t, 0.0) for t in test_rets.columns])
    pr = test_rets.values @ wv
    years = len(pr) / 252
    return (np.prod(1 + pr) ** (1 / years) - 1), pr.std(ddof=1) * np.sqrt(252)


def ex_ante(weights):
    wv = np.array([weights.get(t, 0.0) for t in mu_t.index])
    return float(wv @ mu_t.values), float(np.sqrt(wv @ S_t.values @ wv))


rows = {}
e = EfficientFrontier(mu_t, S_t)
e.max_sharpe(risk_free_rate=0.02)
rows["max_sharpe"] = e.clean_weights()
e = EfficientFrontier(mu_t, S_t)
e.min_volatility()
rows["min_volatility"] = e.clean_weights()
h = HRPOpt(train.pct_change().dropna())
h.optimize()
rows["HRP"] = h.clean_weights()
rows["equal_weight"] = {t: 1 / len(pc.columns) for t in pc.columns}
for name, wt in rows.items():
    ra, va = ex_ante(wt)
    rr, vr = realised(wt)
    print(f"{name:15s} ex-ante {100*ra:5.1f}% / {100*va:4.1f}%   realised {100*rr:5.1f}% / {100*vr:4.1f}%")
