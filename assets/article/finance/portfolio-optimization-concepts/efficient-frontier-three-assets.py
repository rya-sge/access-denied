"""Efficient frontier of the article's 3-asset toy example.

Unconstrained mean-variance frontier (closed form, Merton 1972), long-only frontier (built from the
three CLA corner portfolios, verified in verification/portfolio-optimization-concepts-markowitz-
black-litterman/markowitz.py), capital market line from r_f = 3 %, the minimum-variance and the
tangency portfolios, and the three assets.

Run with the system Python (matplotlib 3.10):  python3 -I efficient-frontier-three-assets.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps  # noqa: E402

mu = np.array([0.08, 0.12, 0.15])
sig = np.array([0.15, 0.20, 0.30])
rho = np.array([[1.0, 0.3, 0.2], [0.3, 1.0, 0.5], [0.2, 0.5, 1.0]])
S = rho * np.outer(sig, sig)
rf = 0.03
one = np.ones(3)
Si = np.linalg.inv(S)
A, B, C = one @ Si @ one, one @ Si @ mu, mu @ Si @ mu
D = A * C - B**2

# unconstrained frontier: sigma^2(m) = (A m^2 - 2 B m + C) / D
m = np.linspace(0.06, 0.17, 300)
vol_u = np.sqrt((A * m**2 - 2 * B * m + C) / D)

# long-only frontier from the corner portfolios (CLA): linear in the weights between corners
corners = [np.array([0.0, 0.0, 1.0]),
           np.array([0.0, 0.57096774, 0.42903226]),
           np.array([0.68656716, 0.26865672, 0.04477612])]
pts = []
for c1, c2 in zip(corners[:-1], corners[1:]):
    for t in np.linspace(0, 1, 100):
        w = (1 - t) * c1 + t * c2
        pts.append((np.sqrt(w @ S @ w), w @ mu))
lo = np.array(pts)

w_gmv = Si @ one / A
ex = mu - rf
w_tan = Si @ ex / (one @ Si @ ex)
g = (np.sqrt(w_gmv @ S @ w_gmv), w_gmv @ mu)
tg = (np.sqrt(w_tan @ S @ w_tan), w_tan @ mu)
sr = (tg[1] - rf) / tg[0]
print(f"GMV vol {g[0]:.4f} ret {g[1]:.4f}; tangency vol {tg[0]:.4f} ret {tg[1]:.4f}; Sharpe {sr:.4f}")

ps.apply()
fig, ax = ps.figure(width_px=980, height_px=520)
c0, ls0, _ = ps.style(0)
c1, ls1, _ = ps.style(1)
c2, ls2, _ = ps.style(2)
ax.plot(vol_u * 100, m * 100, color=c0, linestyle=ls0, lw=2)
ax.plot(lo[:, 0] * 100, lo[:, 1] * 100, color=c1, linestyle=ls1, lw=2.5)
x = np.linspace(0, 0.32, 50)
ax.plot(x * 100, (rf + sr * x) * 100, color=c2, linestyle=ls2, lw=1.6)
ps.label_end(ax, 22, 16.2, "frontier, shorting allowed", c0, dx=0, dy=0, ha="right")
ps.label_end(ax, 26, 14.35, "long-only frontier", c1, dx=6, dy=-22, ha="left")
ps.label_end(ax, 11, (rf + sr * 0.11) * 100, "capital market line (r_f = 3 %)", c2, dx=-6, dy=14, ha="right")
ax.annotate("inefficient half", (vol_u[30] * 100, m[30] * 100), xytext=(8, -4), textcoords="offset points",
            fontsize=10, color=c0)
for (v, r), lab, dx, dy in ((g, "minimum variance", 6, -8), (tg, "tangency (max Sharpe)", 6, -10)):
    ax.plot(v * 100, r * 100, "o", color="black", ms=7)
    ax.annotate(lab, (v * 100, r * 100), xytext=(dx, dy), textcoords="offset points", fontsize=11)
for i, name in enumerate("ABC"):
    ax.plot(sig[i] * 100, mu[i] * 100, "s", color=ps.color(4), ms=7)
    ax.annotate(f"asset {name}", (sig[i] * 100, mu[i] * 100), xytext=(6, 4), textcoords="offset points",
                fontsize=11)
ax.plot(0, rf * 100, "D", color=c2, ms=6)
ax.set_xlim(0, 32)
ax.set_ylim(2, 17)
ax.set_xlabel("volatility (annual standard deviation, %)")
ax.set_ylabel("expected return (annual, %)")
ps.caption(fig, "Illustrative inputs: three assets, mu = 8/12/15 %, sigma = 15/20/30 %, correlations 0.3/0.2/0.5.")
ps.save(fig, __file__)
