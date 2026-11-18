"""Reproduce every in-sample number quoted in the PyPortfolioOpt article.

Run in the directory that holds stock_prices.csv (see README.md):
    pfodock py -n -r optimise.py
"""

import warnings

import cvxpy
import numpy as np
import pandas as pd
import scipy

import pypfopt
from pypfopt import (
    CLA,
    BlackLittermanModel,
    EfficientCVaR,
    EfficientFrontier,
    HRPOpt,
    black_litterman,
    expected_returns,
    objective_functions,
    risk_models,
)
from pypfopt.base import portfolio_performance

RF = 0.02


def pct(x):
    return f"{100 * x:.1f}%"


def perf(label, r, v, s=None):
    extra = f" / Sharpe {s:.2f}" if s is not None else ""
    print(f"{label}: return {pct(r)} / vol {pct(v)}{extra}")


def top(weights, n=6):
    w = {k: round(v, 4) for k, v in weights.items() if v > 1e-4}
    return dict(sorted(w.items(), key=lambda kv: -kv[1])[:n]), len(w)


print("== versions")
print("pypfopt", pypfopt.__version__, "cvxpy", cvxpy.__version__, "numpy", np.__version__,
      "pandas", pd.__version__, "scipy", scipy.__version__)

prices = pd.read_csv("stock_prices.csv", parse_dates=True, index_col="date")
print("\n== data")
print("shape", prices.shape, "from", prices.index.min().date(), "to", prices.index.max().date())
nan_share = prices.isna().mean().sort_values(ascending=False)
print("NaN share (top 4):", {k: round(v, 3) for k, v in nan_share.head(4).items()})
print("first valid BABA", prices["BABA"].first_valid_index().date(),
      "FB", prices["FB"].first_valid_index().date())

print("\n== estimators")
mu = expected_returns.mean_historical_return(prices)
cs = risk_models.CovarianceShrinkage(prices)
S = cs.ledoit_wolf()
print("Ledoit-Wolf shrinkage delta", round(cs.delta, 4))
print("mu min/max", round(mu.min(), 4), mu.idxmin(), round(mu.max(), 4), mu.idxmax())
S_sample = risk_models.sample_cov(prices)
print("vol BABA sample_cov", pct(np.sqrt(S_sample.loc["BABA", "BABA"])),
      "LW", pct(np.sqrt(S.loc["BABA", "BABA"])))
print("vol FB sample_cov", pct(np.sqrt(S_sample.loc["FB", "FB"])),
      "LW", pct(np.sqrt(S.loc["FB", "FB"])))

print("\n== max_sharpe, rf 2%")
ef = EfficientFrontier(mu, S)
ef.max_sharpe(risk_free_rate=RF)
w_ms = ef.clean_weights()
r, v, s = ef.portfolio_performance(risk_free_rate=RF)
perf("max_sharpe LW", r, v, s)
print("weights", top(w_ms))

print("\n== portfolio_performance with a different rf after max_sharpe(rf=0.02)")
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    r2, v2, s2 = ef.portfolio_performance()  # default 0.0
print("Sharpe reported", round(s2, 2), "warning:", [str(c.message)[:60] for c in caught])
print("standalone portfolio_performance(rf=0) Sharpe",
      round(portfolio_performance(w_ms, mu, S)[2], 2))

print("\n== max_sharpe, default rf (0.0)")
ef0 = EfficientFrontier(mu, S)
ef0.max_sharpe()
perf("max_sharpe LW rf0", *ef0.portfolio_performance())

print("\n== min_volatility")
ef = EfficientFrontier(mu, S)
ef.min_volatility()
w_mv = ef.clean_weights()
perf("min_vol LW", *ef.portfolio_performance(risk_free_rate=RF))
print("weights", top(w_mv))

print("\n== efficient_risk(0.20) and efficient_return(0.20)")
ef = EfficientFrontier(mu, S)
ef.efficient_risk(0.20)
perf("efficient_risk 0.20", *ef.portfolio_performance(risk_free_rate=RF))
ef = EfficientFrontier(mu, S)
ef.efficient_return(0.20)
perf("efficient_return 0.20", *ef.portfolio_performance(risk_free_rate=RF))

print("\n== constraints: max 10% per name, tech <= 30%, L2 gamma 0.1")
sector = {"GOOG": "tech", "AAPL": "tech", "FB": "tech", "BABA": "tech", "AMZN": "tech", "AMD": "tech"}
ef = EfficientFrontier(mu, S, weight_bounds=(0, 0.10))
ef.add_sector_constraints(sector, {}, {"tech": 0.30})
ef.add_objective(objective_functions.L2_reg, gamma=0.1)
ef.min_volatility()
w_c = ef.clean_weights()
tech = sum(w_c[t] for t in sector)
perf("constrained min_vol", *ef.portfolio_performance(risk_free_rate=RF))
print("holdings", top(w_c)[1], "max weight", max(w_c.values()), "tech", round(tech, 4))

print("\n== one problem per object")
ef = EfficientFrontier(mu, S)
ef.min_volatility()
try:
    ef.add_constraint(lambda w: w[0] <= 0.05)
except Exception as e:  # noqa: BLE001
    print(type(e).__name__, str(e)[:70])

print("\n== sample_cov instead of Ledoit-Wolf (README setup), rf 0")
ef = EfficientFrontier(mu, S_sample)
ef.max_sharpe()
perf("max_sharpe sample_cov rf0", *ef.portfolio_performance())

print("\n== common window (from BABA listing)")
pc = prices.loc[prices["BABA"].first_valid_index():].dropna()
print("rows", len(pc), "from", pc.index.min().date())
mu_c = expected_returns.mean_historical_return(pc)
S_c = risk_models.CovarianceShrinkage(pc).ledoit_wolf()
ef = EfficientFrontier(mu_c, S_c)
ef.max_sharpe(risk_free_rate=RF)
perf("max_sharpe common window", *ef.portfolio_performance(risk_free_rate=RF))
print("weights", top(ef.clean_weights()))

print("\n== CLA (rf 0 inside CLA.max_sharpe)")
cla = CLA(mu, S)
cla.max_sharpe()
perf("CLA max_sharpe", *cla.portfolio_performance())
cla.min_volatility()
perf("CLA min_vol", *cla.portfolio_performance())

print("\n== HRP")
rets = expected_returns.returns_from_prices(prices)
hrp = HRPOpt(rets)
w_hrp_returned = hrp.optimize()
w_hrp = hrp.clean_weights()
perf("HRP own performance (arith. mean, sample cov)", *hrp.portfolio_performance(risk_free_rate=RF))
perf("HRP weights under mu/LW", *portfolio_performance(w_hrp, mu, S, risk_free_rate=RF))
print("HRP holdings", top(w_hrp)[1], "max weight", round(max(w_hrp.values()), 4))
print("order of optimize() result", list(w_hrp_returned)[:4], "| clean_weights", list(w_hrp)[:4])

print("\n== EfficientCVaR (beta 0.95)")
ec = EfficientCVaR(mu, rets)
ec.min_cvar()
r_c, cvar = ec.portfolio_performance()
print(f"min_cvar: return {pct(r_c)} / daily CVaR95 {pct(cvar)}")

print("\n== Black-Litterman (illustrative equal market caps, one view)")
mcaps = {t: 1.0 for t in prices.columns}
delta = 2.5
prior = black_litterman.market_implied_prior_returns(mcaps, delta, S)
bl = BlackLittermanModel(S, pi=prior, absolute_views={"AAPL": 0.20},
                         omega="idzorek", view_confidences=[0.5])
post = bl.bl_returns()
print("AAPL prior", pct(prior["AAPL"]), "view 20.0%", "posterior (50% confidence)", pct(post["AAPL"]))
print("unrounded prior", round(prior["AAPL"], 5), "posterior", round(post["AAPL"], 5))
bl_full = BlackLittermanModel(S, pi=prior, absolute_views={"AAPL": 0.20},
                              omega="idzorek", view_confidences=[1.0])
print("AAPL posterior at 100% confidence", pct(bl_full.bl_returns()["AAPL"]))
print("GOOG prior", pct(prior["GOOG"]), "posterior (50%)", pct(post["GOOG"]))
