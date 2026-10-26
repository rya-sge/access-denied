"""Figure for the MIT 6.0002 lecture 8 article (create-plot skill). Run: python3 -I <this file>

Left: the standard error of the mean SE = sigma / sqrt(n) for sigma = 9.44 degrees C (the
population standard deviation of the lecture's daily highs), with the two empirical
standard deviations of 1,000 sample means quoted in the lecture (n = 100 and n = 200).
Right: simulated mean relative error of the sample standard deviation (numpy std, ddof=0)
against n, for three populations of 100,000 points, 400 samples per n, fixed seed.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps  # noqa: E402

ps.apply()
fig, (ax1, ax2) = ps.figure(ncols=2, width_ratios=(1, 1))

# Left panel: SE = sigma / sqrt(n)
SIGMA = 9.44
n = np.linspace(20, 600, 400)
c0, ls0, _ = ps.style(0)
ax1.plot(n, SIGMA / np.sqrt(n), color=c0, linestyle=ls0)
for nn, dx, dy, ha in ((25, 8, 4, "left"), (100, 8, 6, "left"), (600, -4, 10, "right")):
    se = SIGMA / np.sqrt(nn)
    ax1.plot([nn], [se], marker="o", color=c0)
    ps.label_end(ax1, nn, se, f"n = {nn}: {se:.2f}", c0, dx=dx, dy=dy, ha=ha,
                 va="top" if dy < 0 else "bottom")
c1 = ps.color(1)
ax1.plot([100, 200], [0.94, 0.66], linestyle="none", marker="s", markersize=8,
         markerfacecolor="none", markeredgecolor=c1, markeredgewidth=2)
ax1.annotate("lecture: SD of 1,000 sample means\n0.94 at n = 100, 0.66 at n = 200",
             xy=(200, 0.66), xytext=(230, 1.35), color=c1, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=c1))
ax1.set(xlim=(0, 620), ylim=(0, 2.2), xlabel="sample size $n$", ylabel="°C",
        title="SE $= \\sigma/\\sqrt{n}$ with $\\sigma = 9.44$ °C")

# Right panel: relative error of the sample SD, simulated
rng = np.random.default_rng(0)
N = 100_000
pops = [("uniform", rng.random(N)), ("normal", rng.normal(0, 1, N)),
        ("exponential", rng.exponential(2.0, N))]
sizes = np.array([20, 30, 40, 60, 80, 100, 150, 200, 300, 400, 500, 600])
for i, (name, pop) in enumerate(pops):
    sd = pop.std()
    err = []
    for m in sizes:
        d = [abs(sd - pop[rng.choice(N, m, replace=False)].std()) / sd for _ in range(400)]
        err.append(100 * np.mean(d))
    c, ls, mk = ps.style(i)
    ax2.plot(sizes, err, color=c, linestyle=ls, marker=mk, markersize=4)
    lx, dy, va = {"uniform": (450, -8, "top"), "normal": (450, 10, "bottom"),
                  "exponential": (450, 10, "bottom")}[name]
    ly = np.interp(lx, sizes, err)
    ps.label_end(ax2, lx, ly, name, c, dx=0, dy=dy, ha="center", va=va)
ax2.set(xlim=(0, 620), ylim=(0, 26), xlabel="sample size $n$",
        ylabel="mean |s − σ| / σ (%)", title="How far the sample SD is from σ")

ps.caption(fig, "Left: formula, and two values from the lecture. Right: own simulation "
                "(100,000-point populations, 400 samples per size, seed 0).")
ps.save(fig, __file__)
