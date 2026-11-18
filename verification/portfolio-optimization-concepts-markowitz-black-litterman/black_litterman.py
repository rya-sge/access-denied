"""Black-Litterman concepts on the 3-asset toy of markowitz.py, cross-checked with PyPortfolioOpt.

- reverse optimisation: Pi = delta Sigma w_mkt, and the unconstrained optimiser at delta returns w_mkt
- market-implied risk aversion delta = (E[R_m] - r_f) / sigma_m^2 for a 7 % premium and 16 % vol
- one absolute view with Idzorek confidence c: the posterior closes the fraction c of the gap
- one relative view with the He-Litterman default Omega: tau cancels in the posterior mean
- posterior covariance
- two views: the per-view fraction is no longer exactly c
- re-run of the PyPortfolioOpt article's AAPL example on stock_prices.csv (if present in $PWD)

Run:  pfodock py -n -r black_litterman.py
"""

import os
import warnings

import numpy as np
import pandas as pd

from pypfopt import BlackLittermanModel, black_litterman, risk_models

warnings.filterwarnings("ignore")
np.set_printoptions(precision=5, suppress=True)

T_ = ["A", "B", "C"]
sig = np.array([0.15, 0.20, 0.30])
rho = np.array([[1.0, 0.3, 0.2], [0.3, 1.0, 0.5], [0.2, 0.5, 1.0]])
S = rho * np.outer(sig, sig)
Sp = pd.DataFrame(S, index=T_, columns=T_)
w_mkt = np.array([0.5, 0.3, 0.2])
delta = 2.5

print(f"delta for 7% premium, 16% vol: {0.07 / 0.16 ** 2:.4f}")

Pi = delta * S @ w_mkt
print("Pi = delta Sigma w_mkt:", Pi)
Pi_p = black_litterman.market_implied_prior_returns(dict(zip(T_, w_mkt)), delta, Sp)
print("pypfopt market_implied_prior_returns:", Pi_p.values)
w_back = np.linalg.solve(delta * S, Pi)
print("reverse check (delta Sigma)^-1 Pi:", w_back)


def bl_post(Pi, S, P, Q, Om, tau):
    tSP = tau * S @ P.T
    return Pi + tSP @ np.linalg.solve(P @ tSP + Om, Q - P @ Pi)


tau = 0.05
# --- one absolute view on C: 10 % ---
P = np.array([[0.0, 0.0, 1.0]])
Q = np.array([0.10])
for c in (0.25, 0.5, 1.0):
    alpha = (1 - c) / c
    Om = np.array([[tau * alpha * (P @ S @ P.T).item()]])
    post = bl_post(Pi, S, P, Q, Om, tau)
    bl = BlackLittermanModel(Sp, pi=pd.Series(Pi, index=T_), absolute_views={"C": 0.10},
                             omega="idzorek", view_confidences=[c])
    r = bl.bl_returns().values
    print(f"abs view C=10%, c={c}: by hand {post}, pypfopt {r}, "
          f"fraction of gap closed on C {(post[2] - Pi[2]) / (0.10 - Pi[2]):.4f}")

# --- one relative view: B outperforms A by 3 %, He-Litterman Omega ---
P = np.array([[-1.0, 1.0, 0.0]])
Q = np.array([0.03])
for tau_ in (0.025, 0.05, 0.5):
    Om = np.diag(np.diag(tau_ * P @ S @ P.T))
    post = bl_post(Pi, S, P, Q, Om, tau_)
    print(f"relative view B-A=3%, He-Litterman Omega, tau={tau_}: posterior {post}, "
          f"view portfolio {(P @ post).item():.5f} (prior {(P @ Pi).item():.5f})")
bl = BlackLittermanModel(Sp, pi=pd.Series(Pi, index=T_), P=P, Q=Q)  # default omega
print("pypfopt default omega, relative view:", bl.bl_returns().values)
print("pypfopt posterior covariance:\n", bl.bl_cov().values)
Om = np.diag(np.diag(tau * P @ S @ P.T))
M = np.linalg.inv(np.linalg.inv(tau * S) + P.T @ np.linalg.inv(Om) @ P)
print("by hand Sigma + M:\n", S + M)
print("posterior vol / prior vol:", np.sqrt(np.diag(S + M)) / sig)

# --- two absolute views with Idzorek 50 % each: fraction per view ---
P = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
Q = np.array([0.10, 0.10])
c = np.array([0.5, 0.5])
Om = np.diag([tau * (1 - ci) / ci * (P[i] @ S @ P[i]) for i, ci in enumerate(c)])
post = bl_post(Pi, S, P, Q, Om, tau)
print(f"two views A=10%, C=10% at 50%: posterior {post}; fractions "
      f"A {(post[0] - Pi[0]) / (0.10 - Pi[0]):.4f}, C {(post[2] - Pi[2]) / (0.10 - Pi[2]):.4f}")

# --- re-run of the PyPortfolioOpt article's example ---
if os.path.exists("stock_prices.csv"):
    prices = pd.read_csv("stock_prices.csv", parse_dates=True, index_col="date")
    Slw = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
    prior = black_litterman.market_implied_prior_returns({t: 1.0 for t in prices.columns}, 2.5, Slw)
    bl = BlackLittermanModel(Slw, pi=prior, absolute_views={"AAPL": 0.20},
                             omega="idzorek", view_confidences=[0.5])
    post = bl.bl_returns()["AAPL"]
    print(f"stock_prices.csv AAPL prior {prior['AAPL']:.5f}, posterior at 50% {post:.5f}, "
          f"prior + 0.5 (0.20 - prior) = {prior['AAPL'] + 0.5 * (0.20 - prior['AAPL']):.5f}")
else:
    print("stock_prices.csv not found: AAPL re-run skipped")
