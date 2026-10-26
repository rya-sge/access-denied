"""In-section figure for the MIT 6.0002 Lecture 6 article (Monte Carlo simulation).

Running mean return per spin of a single-number bet on a European wheel (37 pockets,
payout 35:1), three seeded runs of one million spins, against the exact expected
return -1/37 and the band -1/37 +/- 1.96 sigma/sqrt(n), with sigma = 216/37.
Run: python3 -I monte-carlo-roulette-convergence.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps  # noqa: E402

MU = -1 / 37            # exact expected return per spin (European wheel)
SIGMA = 216 / 37        # exact standard deviation of one spin's return
N = 1_000_000

ps.apply()
fig, ax = ps.figure(height_px=480)

n = np.arange(1, N + 1)
idx = np.unique(np.geomspace(1, N, 3000).astype(int)) - 1   # thin the path: 3,000 log-spaced points
ns = n[idx]
band = 1.96 * SIGMA / np.sqrt(ns)
ax.fill_between(ns, 100 * (MU - band), 100 * (MU + band), color=ps.color("sky"), alpha=0.35, lw=0)
ax.axhline(100 * MU, color=ps.color("black"), lw=1.4)

for i, seed in enumerate((1, 2, 3)):
    rng = np.random.default_rng(seed)
    win = rng.integers(0, 37, size=N) == 0          # the bet pocket comes up
    ret = np.where(win, 35.0, -1.0)
    running = 100 * np.cumsum(ret) / n
    c, ls, _ = ps.style(i)
    ax.plot(ns, running[idx], color=c, linestyle=ls, lw=1.6)
    ps.label_end(ax, N, running[-1], f"run {i + 1}", c, dx=6, dy=(-12, 0, 12)[i])

ax.set(xscale="log", xlim=(100, N), ylim=(-100, 100),
       xlabel="number of spins $n$ (log scale)",
       ylabel="mean return per spin (%)",
       title="European roulette, single-number bet: the running mean settles near −2.70 %")
from matplotlib.ticker import FuncFormatter
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.annotate("exact expected return −1/37 ≈ −2.70 %", (200000, 100 * MU), xytext=(-40, -70),
            textcoords="offset points", fontsize=10, color=ps.color("black"), ha="right",
            arrowprops=dict(arrowstyle="->", color=ps.color("black"), lw=1))
ax.annotate("95 % band  −1/37 ± 1.96 σ/√n,  σ = 216/37 ≈ 5.84", (3000, 100 * (MU + 1.96 * SIGMA / np.sqrt(3000))),
            xytext=(0, 40), textcoords="offset points", fontsize=10, color=ps.color("blue"))
ps.caption(fig, "Simulated with numpy.random.default_rng, seeds 1, 2 and 3; one bet of one unit per spin. The band is pointwise: it holds at each n, not for a whole path.")
ps.save(fig, __file__)
