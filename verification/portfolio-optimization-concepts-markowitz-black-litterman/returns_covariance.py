"""Returns, annualisation, CAPM, EMA, and covariance estimation concepts.

- simple vs log returns on a 100 -> 150 -> 100 path; arithmetic vs geometric mean
- annualisation of a daily mean and volatility (252, sqrt(252)); volatility drag
- PyPortfolioOpt mean_historical_return (CAGR) vs compounding=False on the same toy path
- CAPM expected return with a beta computed as cov / var
- sample covariance with T < n is singular; eigenvalue spread when n/T = 0.5 (true Sigma = I)
- Ledoit-Wolf shrinkage (scikit-learn): intensity and Frobenius error vs the sample matrix
- zero-filling missing returns shrinks a variance by the observed share
- semicovariance on a toy series

Run:  pfodock py -n -r returns_covariance.py
"""

import warnings

import numpy as np
import pandas as pd
from sklearn.covariance import ledoit_wolf

from pypfopt import expected_returns, risk_models

warnings.filterwarnings("ignore")
rng = np.random.default_rng(42)

# ---------- returns ----------
p = np.array([100.0, 150.0, 100.0])
simple = p[1:] / p[:-1] - 1
logr = np.log(p[1:] / p[:-1])
print("simple returns:", simple, "arithmetic mean:", simple.mean())
print("geometric mean:", (np.prod(1 + simple)) ** (1 / len(simple)) - 1)
print("log returns:", logr, "sum:", logr.sum())

prices = pd.DataFrame({"X": p}, index=pd.date_range("2020-01-01", periods=3))
print("pypfopt mean_historical_return (CAGR, frequency=2):",
      float(expected_returns.mean_historical_return(prices, frequency=2).iloc[0]))
print("pypfopt mean_historical_return compounding=False (frequency=2):",
      float(expected_returns.mean_historical_return(prices, compounding=False, frequency=2).iloc[0]))

mu_d, s_d = 0.0004, 0.01
print(f"annualised mean {mu_d * 252:.4f}, annualised vol {s_d * np.sqrt(252):.4f}")
print(f"compounded daily mean (1+mu_d)^252-1 = {(1 + mu_d) ** 252 - 1:.4f}")

# volatility drag on simulated log-normal returns: geometric ~ arithmetic - sigma^2/2
a_mean, a_vol = 0.08, 0.20
print(f"approx geometric for arithmetic {a_mean}, vol {a_vol}: {a_mean - a_vol ** 2 / 2:.4f}")

# ---------- CAPM ----------
T = 2520
mkt = rng.normal(0.0003, 0.01, T)
asset = 0.0001 + 1.2 * mkt + rng.normal(0, 0.008, T)
beta = np.cov(asset, mkt)[0, 1] / np.var(mkt, ddof=1)
print(f"estimated beta {beta:.4f} (true 1.2)")
rf, mrp = 0.03, 0.05
print(f"CAPM with beta 1.2, rf 3%, premium 5%: {rf + 1.2 * mrp:.4f}")
dfp = pd.DataFrame({"ASSET": 100 * np.cumprod(1 + asset)}, index=pd.bdate_range("2010-01-01", periods=T))
mk = pd.DataFrame({"MKT": 100 * np.cumprod(1 + mkt)}, index=dfp.index)
mkt_cagr = float(np.prod(1 + mkt) ** (252 / T) - 1)
print(f"realised market CAGR in this sample {mkt_cagr:.4f} (drift 0.0003/day would suggest ~{(1.0003 ** 252 - 1):.4f})")
print("pypfopt capm_return (rf 3%, market given, compounding):",
      round(float(expected_returns.capm_return(dfp, market_prices=mk, risk_free_rate=0.03).iloc[0]), 4))

# ---------- EMA ----------
r = pd.Series(np.r_[np.full(500, 0.0002), np.full(250, 0.0010)])
print(f"plain mean x252 {r.mean() * 252:.4f}; EMA(span=500) x252 {r.ewm(span=500).mean().iloc[-1] * 252:.4f}; "
      f"last-year mean x252 {r.iloc[-250:].mean() * 252:.4f}")

# ---------- covariance: T < n ----------
n, T = 50, 40
X = rng.normal(size=(T, n))
Ssmp = np.cov(X, rowvar=False)
print(f"n={n}, T={T}: rank of sample cov = {np.linalg.matrix_rank(Ssmp)}, "
      f"smallest eigenvalue {np.linalg.eigvalsh(Ssmp).min():.2e}")

# eigenvalue spread, true Sigma = I, n/T = 0.5
n, T = 100, 200
q = n / T
eig = []
for _ in range(50):
    X = rng.normal(size=(T, n))
    eig.append(np.linalg.eigvalsh(np.cov(X, rowvar=False)))
eig = np.array(eig)
print(f"n={n}, T={T}: mean min eigenvalue {eig[:, 0].mean():.3f}, mean max {eig[:, -1].mean():.3f} (true: all 1)")
print(f"Marchenko-Pastur edges (1-sqrt q)^2={(1 - np.sqrt(q)) ** 2:.3f}, (1+sqrt q)^2={(1 + np.sqrt(q)) ** 2:.3f}")
print(f"condition number of sample cov ~ {eig[:, -1].mean() / eig[:, 0].mean():.1f} (true 1)")

# ---------- Ledoit-Wolf vs sample: Frobenius error, structured true matrix ----------
n = 30
true_sig = np.linspace(0.10, 0.40, n) / np.sqrt(252)
true_rho = 0.3 * np.ones((n, n)) + 0.7 * np.eye(n)
true_S = true_rho * np.outer(true_sig, true_sig)
L = np.linalg.cholesky(true_S)
for T in (60, 250, 1000):
    e_s, e_lw, ds = [], [], []
    for _ in range(200):
        X = rng.normal(size=(T, n)) @ L.T
        Ss = np.cov(X, rowvar=False)
        Slw, d = ledoit_wolf(X)
        e_s.append(np.linalg.norm(Ss - true_S, "fro"))
        e_lw.append(np.linalg.norm(Slw - true_S, "fro"))
        ds.append(d)
    print(f"n={n}, T={T}: mean LW delta {np.mean(ds):.3f}; Frobenius error LW / sample = "
          f"{np.mean(e_lw) / np.mean(e_s):.3f}")

# ---------- minimum-variance portfolio from each estimator, judged with the true matrix ----------
from pypfopt import CovarianceShrinkage

ones = np.ones(n)
def gmv(M):
    x = np.linalg.solve(M, ones)
    return x / x.sum()
true_gmv_vol = np.sqrt(1 / (ones @ np.linalg.solve(true_S, ones))) * np.sqrt(252)
for T in (60, 250):
    v = {"sample": [], "LW identity": [], "LW const-corr": []}
    for _ in range(200):
        X = rng.normal(size=(T, n)) @ L.T
        df = pd.DataFrame(X)
        cs = CovarianceShrinkage(df, returns_data=True, frequency=1)
        mats = {"sample": np.cov(X, rowvar=False),
                "LW identity": cs.ledoit_wolf().values,
                "LW const-corr": cs.ledoit_wolf("constant_correlation").values}
        for k_, M in mats.items():
            w_ = gmv(M)
            v[k_].append(np.sqrt(w_ @ true_S @ w_) * np.sqrt(252))
    print(f"T={T}: true vol of estimated GMV: " + ", ".join(f"{k_} {np.mean(x_):.4f}" for k_, x_ in v.items())
          + f"; true optimum {true_gmv_vol:.4f}")

# ---------- zero-filled missing data ----------
T = 2000
x = rng.normal(0, 0.02, T)
x_missing = x.copy()
x_missing[: int(0.75 * T)] = np.nan  # listed for the last 25 % of the window
filled = np.nan_to_num(x_missing)
print(f"vol observed only {np.nanstd(x_missing, ddof=1) * np.sqrt(252):.4f}; zero-filled "
      f"{filled.std(ddof=1) * np.sqrt(252):.4f}; ratio {filled.std(ddof=1) / np.nanstd(x_missing, ddof=1):.3f} "
      f"(sqrt(0.25) = 0.5)")

# ---------- semicovariance ----------
rets = pd.DataFrame({"U": [0.02, -0.01, 0.03, -0.02, 0.01], "V": [-0.01, -0.02, 0.02, 0.01, 0.00]})
sc = risk_models.semicovariance(rets, returns_data=True, benchmark=0.0, frequency=1)
drops = np.minimum(rets.values, 0)
print("semicovariance pypfopt:\n", sc.values.round(6))
print("by hand drops' drops / T:\n", (drops.T @ drops / len(rets)).round(6))
