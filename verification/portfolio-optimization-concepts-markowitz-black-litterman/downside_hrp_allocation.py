"""Downside risk, HRP and discrete allocation on toy inputs.

- VaR / CVaR of ten daily portfolio returns at beta = 0.8, by sorting and by the
  Rockafellar-Uryasev linear programme (cvxpy)
- drawdown path, maximum drawdown and CDaR (non-compounded, as in PyPortfolioOpt)
- HRP on four assets in two correlated pairs: distances, single linkage, order,
  recursive bisection by hand, compared with HRPOpt; inverse-variance and min-variance for contrast
- discrete allocation of 1,000 over three prices: floor rounding, greedy and integer LP

Run:  pfodock py -n -r downside_hrp_allocation.py
"""

import warnings

import cvxpy as cp
import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import squareform

from pypfopt import HRPOpt
from pypfopt.discrete_allocation import DiscreteAllocation

warnings.filterwarnings("ignore")
np.set_printoptions(precision=4, suppress=True)

# ---------- VaR / CVaR ----------
r = np.array([1.2, -0.5, 0.3, -2.1, 0.8, -1.4, 0.4, -3.0, 0.9, 0.1]) / 100
loss = -r
beta = 0.8
k = int(round((1 - beta) * len(r)))
srt = np.sort(loss)[::-1]
print("losses sorted (worst first, %):", srt * 100)
print(f"VaR_0.8 (lower quantile) {np.quantile(loss, beta, method='inverted_cdf') * 100:.2f}%, "
      f"CVaR_0.8 = mean of {k} worst = {srt[:k].mean() * 100:.2f}%")
a = cp.Variable()
u = cp.Variable(len(r), nonneg=True)
prob = cp.Problem(cp.Minimize(a + cp.sum(u) / ((1 - beta) * len(r))), [u >= loss - a])
prob.solve()
print(f"RU LP: objective (CVaR) {prob.value * 100:.4f}%, alpha {a.value * 100:.4f}%")
for alpha in (0.014, 0.018, 0.021):
    F = alpha + np.maximum(loss - alpha, 0).sum() / ((1 - beta) * len(r))
    print(f"  F(alpha={alpha * 100:.1f}%) = {F * 100:.4f}%")

# ---------- drawdown ----------
cum = np.cumsum(r)
peak = np.maximum.accumulate(np.r_[0.0, cum])[1:]
dd = peak - cum
print("cumulative (%):", (cum * 100).round(2))
print("drawdown (%):", (dd * 100).round(2))
print(f"max drawdown {dd.max() * 100:.2f}%, CDaR_0.8 = mean of {k} worst drawdowns "
      f"{np.sort(dd)[::-1][:k].mean() * 100:.2f}%")

# ---------- HRP ----------
tick = ["A", "B", "C", "D"]
sig = np.array([0.10, 0.15, 0.20, 0.25])
rho = np.array([[1.0, 0.8, 0.1, 0.2],
                [0.8, 1.0, 0.2, 0.1],
                [0.1, 0.2, 1.0, 0.6],
                [0.2, 0.1, 0.6, 1.0]])
S = rho * np.outer(sig, sig)
Sp = pd.DataFrame(S, index=tick, columns=tick)
dist = np.sqrt((1 - rho) / 2)
print("distance matrix:\n", dist)
link = sch.linkage(squareform(dist, checks=False), "single")
print("linkage (i, j, distance, size):\n", link)
order = [tick[i] for i in sch.to_tree(link, rd=False).pre_order()]
print("quasi-diagonal order:", order)


def cvar_(items):
    s = Sp.loc[items, items].values
    iv = 1 / np.diag(s)
    iv /= iv.sum()
    return iv @ s @ iv


w = pd.Series(1.0, index=order)
clusters = [order]
while clusters:
    clusters = [c[j:kk] for c in clusters for j, kk in ((0, len(c) // 2), (len(c) // 2, len(c))) if len(c) > 1]
    for i in range(0, len(clusters), 2):
        c1, c2 = clusters[i], clusters[i + 1]
        v1, v2 = cvar_(c1), cvar_(c2)
        al = 1 - v1 / (v1 + v2)
        print(f"  split {c1} | {c2}: var {v1:.6f} vs {v2:.6f} -> {al:.4f} / {1 - al:.4f}")
        w[c1] *= al
        w[c2] *= 1 - al
w = w[tick]
print("HRP by hand:", w.values)
h = HRPOpt(cov_matrix=Sp)
hw = h.optimize()
print("HRPOpt(cov_matrix):", np.array([hw[t] for t in tick]))
ivp = (1 / sig**2) / (1 / sig**2).sum()
one = np.ones(4)
gmv = np.linalg.solve(S, one)
gmv /= gmv.sum()
for lab, ww in (("HRP", w.values), ("inverse variance", ivp), ("min variance (unconstrained)", gmv)):
    print(f"{lab}: w={ww} vol={np.sqrt(ww @ S @ ww):.4f}")

# ---------- discrete allocation ----------
weights = {"X": 0.5, "Y": 0.3, "Z": 0.2}
prices = pd.Series({"X": 330.0, "Y": 95.0, "Z": 41.0})
V = 1000.0
fl = {t: int(np.floor(weights[t] * V / prices[t])) for t in weights}
spent = sum(fl[t] * prices[t] for t in fl)
print(f"floor shares {fl}, spent {spent:.2f}, left {V - spent:.2f}")
g, gl = DiscreteAllocation(weights, prices, total_portfolio_value=V).greedy_portfolio()
print(f"greedy {g}, left {gl:.2f}, spent {sum(g[t] * prices[t] for t in g):.2f}")
l, ll = DiscreteAllocation(weights, prices, total_portfolio_value=V).lp_portfolio(solver="SCIP" if "SCIP" in cp.installed_solvers() else None)
print(f"LP {l}, left {ll:.2f}, spent {sum(l[t] * prices[t] for t in l):.2f}")
for lab, al_ in (("floor", fl), ("greedy", g), ("LP", l)):
    tot = sum(al_.get(t, 0) * prices[t] for t in weights)
    real = {t: round(al_.get(t, 0) * prices[t] / tot, 4) for t in weights}
    err = sum(abs(weights[t] * V - al_.get(t, 0) * prices[t]) for t in weights)
    print(f"  {lab}: realised weights {real}, sum |w V - x p| = {err:.2f}")
print("installed solvers:", cp.installed_solvers())

# brute force: LP objective sum |w V - x p| + leftover, over all affordable share counts
best, sols = None, []
for x in range(0, 4):
    for y in range(0, 11):
        for z in range(0, 25):
            cost = 330 * x + 95 * y + 41 * z
            if cost > V:
                continue
            obj = abs(500 - 330 * x) + abs(300 - 95 * y) + abs(200 - 41 * z) + (V - cost)
            sols.append((obj, (x, y, z), cost))
mn = min(s[0] for s in sols)
opt = sorted(s for s in sols if abs(s[0] - mn) < 1e-9)
print(f"brute force: minimum objective {mn:.2f}, optimal allocations (X, Y, Z) and spend: "
      + ", ".join(f"{a} {c:.0f}" for _, a, c in opt))
print(f"floor allocation objective {221 + 221:.2f}")
