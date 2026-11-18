"""Markowitz concepts on a 3-asset toy: closed forms, frontier, two-fund theorem,
tangency portfolio, quadratic utility, cross-check with PyPortfolioOpt (cvxpy and CLA),
the DCP rejection of a raw Sharpe objective, and the sensitivity of the tangency
weights to a small change in one expected return ("error maximiser").

Run:  pfodock py -n -r markowitz.py
"""

import warnings

import cvxpy as cp
import numpy as np

from pypfopt import CLA, EfficientFrontier

warnings.filterwarnings("ignore")
np.set_printoptions(precision=4, suppress=True)

TICKERS = ["A", "B", "C"]
mu = np.array([0.08, 0.12, 0.15])
sig = np.array([0.15, 0.20, 0.30])
rho = np.array([[1.0, 0.3, 0.2], [0.3, 1.0, 0.5], [0.2, 0.5, 1.0]])
S = rho * np.outer(sig, sig)
rf = 0.03
one = np.ones(3)
Si = np.linalg.inv(S)


def show(label, w):
    r = w @ mu
    v = np.sqrt(w @ S @ w)
    print(f"{label}: w={w} return={r:.4f} vol={v:.4f} sharpe(rf=3%)={(r - rf) / v:.4f}")
    return r, v


print("Sigma =\n", S)
print("eigenvalues of Sigma:", np.linalg.eigvalsh(S))

# --- frontier constants (Merton 1972) ---
A = one @ Si @ one
B = one @ Si @ mu
C = mu @ Si @ mu
D = A * C - B**2
print(f"A={A:.4f} B={B:.4f} C={C:.4f} D={D:.4f}")

# --- global minimum-variance portfolio ---
w_gmv = Si @ one / A
r_gmv, v_gmv = show("GMV closed form", w_gmv)
print(f"GMV return B/A={B / A:.4f}, variance 1/A={1 / A:.6f}, vol={np.sqrt(1 / A):.4f}")

# --- tangency (max Sharpe) portfolio ---
ex = mu - rf * one
w_tan = Si @ ex / (one @ Si @ ex)
r_tan, v_tan = show("Tangency closed form", w_tan)
print(f"max Sharpe sqrt(ex' Si ex) = {np.sqrt(ex @ Si @ ex):.4f}")

# --- frontier variance formula at a target return ---
m = 0.12
var_m = (A * m**2 - 2 * B * m + C) / D
lam = (C - B * m) / D
gam = (A * m - B) / D
w_m = Si @ (lam * one + gam * mu)
show(f"Frontier portfolio at m={m}", w_m)
print(f"formula vol at m={m}: {np.sqrt(var_m):.4f}")

# --- two-fund theorem: w_m is a combination of GMV and the 'mu' portfolio Si mu / B ---
w_mu = Si @ mu / B
r_mu, _ = show("Second fund Si mu / B", w_mu)
a = (m - r_mu) / (r_gmv - r_mu)
print(f"two-fund weight on GMV a={a:.4f}; max |a*gmv + (1-a)*mu_fund - w_m| = "
      f"{np.max(np.abs(a * w_gmv + (1 - a) * w_mu - w_m)):.2e}")

# --- quadratic utility: max w'mu - delta/2 w'Sw ---
delta = 3.0
w_u_free = Si @ mu / delta  # no budget constraint
print(f"utility delta={delta}, no budget: w={w_u_free}, sum={w_u_free.sum():.4f}")
# with budget 1'w = 1: w = Si(mu - eta 1)/delta, eta chosen so the weights sum to 1
eta = (B - delta) / A
w_u = Si @ (mu - eta * one) / delta
show(f"utility delta={delta}, budget", w_u)

# --- PyPortfolioOpt cross-checks ---
mu_s = dict(zip(TICKERS, mu))
import pandas as pd

mu_p = pd.Series(mu, index=TICKERS)
S_p = pd.DataFrame(S, index=TICKERS, columns=TICKERS)

ef = EfficientFrontier(mu_p, S_p)
w = np.array(list(ef.min_volatility().values()))
show("pypfopt min_volatility", w)
ef = EfficientFrontier(mu_p, S_p)
w = np.array(list(ef.max_sharpe(risk_free_rate=rf).values()))
show("pypfopt max_sharpe(rf=0.03)", w)
ef = EfficientFrontier(mu_p, S_p)
w = np.array(list(ef.efficient_return(m).values()))
show("pypfopt efficient_return(0.12)", w)
ef = EfficientFrontier(mu_p, S_p)
w = np.array(list(ef.max_quadratic_utility(risk_aversion=delta).values()))
show(f"pypfopt max_quadratic_utility({delta})", w)

cla = CLA(mu_p, S_p)
cla.max_sharpe()
show("pypfopt CLA max_sharpe (rf=0)", np.array(list(cla.weights)))
ef = EfficientFrontier(mu_p, S_p)
w = np.array(list(ef.max_sharpe(risk_free_rate=0.0).values()))
show("pypfopt EF max_sharpe(rf=0)", w)
cla = CLA(mu_p, S_p)
cla.min_volatility()
show("pypfopt CLA min_volatility", np.array(list(cla.weights)))

# CLA turning points (corner portfolios), long-only bounds
cla = CLA(mu_p, S_p)
cla._solve()
print("CLA turning points (corner portfolios), long-only:")
for wt in cla.w:
    wt = np.asarray(wt).flatten()
    r = wt @ mu
    v = np.sqrt(wt @ S @ wt)
    print(f"  w={wt} return={r:.4f} vol={v:.4f}")

# --- DCP: a raw Sharpe ratio objective is rejected ---
wv = cp.Variable(3)
try:
    prob = cp.Problem(cp.Maximize((mu - rf) @ wv / cp.sqrt(cp.quad_form(wv, S))),
                      [cp.sum(wv) == 1, wv >= 0])
    prob.solve()
    print("raw Sharpe solved (unexpected)")
except cp.error.DCPError as e:
    print("raw Sharpe objective:", type(e).__name__, str(e).splitlines()[0][:80])

# Variable change: y = k w, (mu - rf)'y = 1, min y'Sy
y = cp.Variable(3)
k = cp.Variable()
prob = cp.Problem(cp.Minimize(cp.quad_form(y, S)),
                  [(mu - rf) @ y == 1, cp.sum(y) == k, k >= 0, y >= 0])
prob.solve()
show("variable-change QP, long-only", y.value / k.value)
print("is DCP:", prob.is_dcp())

# --- error maximiser: change one expected return by 1 point ---
for dB in (+0.01, -0.01):
    mu2 = mu.copy()
    mu2[1] += dB
    ex2 = mu2 - rf
    w2 = Si @ ex2 / (one @ Si @ ex2)
    print(f"mu_B {mu[1]:.2f}->{mu2[1]:.2f}: tangency w={w2}  "
          f"(change in w_B {w2[1] - w_tan[1]:+.4f})")

# standard error of an annual mean estimated from T years
for s_, T in ((0.20, 10), (0.20, 40)):
    print(f"SE of annual mean, sigma={s_}, T={T}y: {s_ / np.sqrt(T):.4f}")
print(f"years for SE of 1 point at sigma 20%: {(0.20 / 0.01) ** 2:.0f}")

# two-fund theorem with the GMV and the tangency portfolio, target 10 %
m2 = 0.10
lam2 = (C - B * m2) / D
gam2 = (A * m2 - B) / D
w_m2 = Si @ (lam2 * one + gam2 * mu)
a2 = (m2 - r_tan) / (r_gmv - r_tan)
print(f"frontier at m=0.10: w={w_m2}; = {a2:.4f} GMV + {1 - a2:.4f} tangency; "
      f"max diff {np.max(np.abs(a2 * w_gmv + (1 - a2) * w_tan - w_m2)):.2e}")

# mu_B moved by one standard error (10 years at 20 % vol), unconstrained and long-only
se = 0.20 / np.sqrt(10)
for sgn in (+1, -1):
    mu2 = mu.copy()
    mu2[1] += sgn * se
    ex2 = mu2 - rf
    w2 = Si @ ex2 / (one @ Si @ ex2)
    ef = EfficientFrontier(pd.Series(mu2, index=TICKERS), S_p)
    w3 = np.array(list(ef.max_sharpe(risk_free_rate=rf).values()))
    print(f"mu_B = {mu2[1]:.4f}: tangency unconstrained {w2}, long-only {np.round(w3, 4)}")

# precise corner portfolios and the interpolation property between adjacent corners
np.set_printoptions(precision=8, suppress=True)
corners = [np.asarray(x).flatten() for x in cla.w]
uniq = [corners[0]] + [c for i, c in enumerate(corners[1:]) if np.max(np.abs(c - corners[i])) > 1e-9]
for c in uniq:
    print("corner:", c, f"return {c @ mu:.6f} vol {np.sqrt(c @ S @ c):.6f}")
for m_ in (0.10, 0.14):
    ef = EfficientFrontier(mu_p, S_p)
    w_ef = np.array(list(ef.efficient_return(m_).values()))
    for c1, c2 in zip(uniq[:-1], uniq[1:]):
        r1, r2 = c1 @ mu, c2 @ mu
        if min(r1, r2) <= m_ <= max(r1, r2):
            t = (m_ - r2) / (r1 - r2)
            w_int = t * c1 + (1 - t) * c2
            print(f"m={m_}: efficient_return {w_ef.round(5)}, corner mix {w_int.round(5)}, "
                  f"max diff {np.max(np.abs(w_ef - w_int)):.1e}")
