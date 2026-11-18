"""Evaluation concepts by Monte Carlo, with a known true model.

1. In-sample optimism: 10 assets with known mu and Sigma, 60 monthly observations.
   Estimate mu and Sigma, solve long-only max Sharpe (rf = 0), and compare the Sharpe ratio
   the optimiser reports (estimated inputs) with the true Sharpe ratio of the same weights,
   the true optimum, equal weights and the estimated minimum-variance portfolio.
2. Backtest selection: the best in-sample Sharpe among N strategies whose true Sharpe is 0.

Run:  pfodock py -n -r evaluation_mc.py
"""

import warnings

import numpy as np
import pandas as pd

from pypfopt import EfficientFrontier

warnings.filterwarnings("ignore")
rng = np.random.default_rng(7)

n, T, R = 10, 60, 500
mu = np.linspace(0.05, 0.10, n)
vol = np.linspace(0.15, 0.30, n)
rho = 0.4 * np.ones((n, n)) + 0.6 * np.eye(n)
S = rho * np.outer(vol, vol)
mu_m, S_m = mu / 12, S / 12
L = np.linalg.cholesky(S_m)
tick = [f"S{i}" for i in range(n)]


def sharpe(w, m, C):
    return (w @ m) / np.sqrt(w @ C @ w)


def max_sharpe(m, C):
    ef = EfficientFrontier(pd.Series(m, index=tick), pd.DataFrame(C, index=tick, columns=tick))
    return np.array(list(ef.max_sharpe(risk_free_rate=0.0).values()))


def min_vol(m, C):
    ef = EfficientFrontier(pd.Series(m, index=tick), pd.DataFrame(C, index=tick, columns=tick))
    return np.array(list(ef.min_volatility().values()))


w_true = max_sharpe(mu, S)
print(f"true optimum (long-only) Sharpe {sharpe(w_true, mu, S):.4f}")
w_eq = np.ones(n) / n
print(f"equal weight true Sharpe {sharpe(w_eq, mu, S):.4f}")
print(f"true GMV (long-only) true Sharpe {sharpe(min_vol(mu, S), mu, S):.4f}")

ins, outs, gmv_out, fails, maxw = [], [], [], 0, []
for _ in range(R):
    X = rng.normal(size=(T, n)) @ L.T + mu_m
    m_hat = X.mean(axis=0) * 12
    S_hat = np.cov(X, rowvar=False) * 12
    if (m_hat <= 0).all():
        fails += 1
        continue
    try:
        w = max_sharpe(m_hat, S_hat)
    except Exception:
        fails += 1
        continue
    ins.append(sharpe(w, m_hat, S_hat))
    outs.append(sharpe(w, mu, S))
    maxw.append(w.max())
    gmv_out.append(sharpe(min_vol(m_hat, S_hat), mu, S))
ins, outs, gmv_out = map(np.array, (ins, outs, gmv_out))
print(f"replications {len(ins)} (skipped {fails})")
print(f"estimated max-Sharpe: in-sample Sharpe mean {ins.mean():.4f}, true Sharpe of same weights "
      f"mean {outs.mean():.4f} (5th pct {np.percentile(outs, 5):.4f}), mean largest weight {np.mean(maxw):.4f}")
print(f"estimated min-vol: true Sharpe mean {gmv_out.mean():.4f}")
print(f"share of runs where estimated max-Sharpe beats equal weight (true Sharpe): "
      f"{(outs > sharpe(w_eq, mu, S)).mean():.3f}")

# --- best of N zero-Sharpe strategies, 5 years of monthly data ---
for N in (1, 10, 100):
    best = []
    for _ in range(2000):
        x = rng.normal(0, 0.05, size=(N, T))
        s = x.mean(axis=1) / x.std(axis=1, ddof=1) * np.sqrt(12)
        best.append(s.max())
    print(f"N={N}: mean best in-sample annual Sharpe {np.mean(best):.3f} (true Sharpe 0)")
print(f"SE of an annual Sharpe estimate over 5 years ~ 1/sqrt(5) = {1 / np.sqrt(5):.3f}")
