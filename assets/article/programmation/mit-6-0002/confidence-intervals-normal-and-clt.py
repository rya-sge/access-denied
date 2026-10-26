"""Figure for the MIT 6.0002 lecture 7 article (create-plot skill).

Left: standard normal PDF with the 1, 1.96 and 3 standard-deviation bands shaded.
Right: central limit theorem with a continuous die on [0, 5): one die versus the mean of 50 dice.
Run: python3 -I confidence-intervals-normal-and-clt.py
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps  # noqa: E402

ps.apply()
fig, (ax1, ax2) = ps.figure(ncols=2, width_ratios=(1, 1))

# Left panel: normal PDF and empirical-rule bands
x = np.linspace(-4, 4, 801)
pdf = np.exp(-x ** 2 / 2) / math.sqrt(2 * math.pi)
bands = [(3, "sky", 0.25), (1.96, "sky", 0.45), (1, "blue", 0.45)]
for k, name, a in bands:
    m = np.abs(x) <= k
    ax1.fill_between(x[m], 0, pdf[m], color=ps.color(name), alpha=a, linewidth=0)
ax1.plot(x, pdf, color="black")
for k, txt, y in [(1, "±1σ: 68.27 %", 0.20), (1.96, "±1.96σ: 95.00 %", 0.115), (3, "±3σ: 99.73 %", 0.035)]:
    ax1.annotate("", xy=(-k, y), xytext=(k, y), arrowprops=dict(arrowstyle="<->", color="black", lw=1))
    ax1.text(0, y + 0.008, txt, ha="center", va="bottom", fontsize=10)
ax1.text(0.15, 0.405, "peak 0.399 (a density, not a probability)", ha="left", fontsize=9, color="dimgray")
ax1.set(xlim=(-4, 4), ylim=(0, 0.45), xlabel="$x$ (standard deviations from the mean)",
        ylabel="density", title="Standard normal PDF, areas = probabilities")

# Right panel: CLT with continuous dice
rng = np.random.default_rng(0)
one = rng.random(1_000_000) * 5
fifty = (rng.random((20_000, 50)) * 5).mean(axis=1)
bins = np.linspace(0, 5, 51)
ax2.hist(one, bins=bins, weights=np.full(one.size, 1 / one.size), color=ps.color(0),
         alpha=0.55, hatch="..", edgecolor="white", linewidth=0.3)
ax2.hist(fifty, bins=bins, weights=np.full(fifty.size, 1 / fifty.size), color=ps.color(1),
         alpha=0.75, hatch="//", edgecolor="white", linewidth=0.3)
ax2.text(4.0, 0.035, "1 die\nmean 2.5, std 1.443", ha="center", fontsize=10, color=ps.color(0))
ax2.text(3.35, 0.15, "mean of 50 dice\nmean 2.5, std 0.204", ha="left", fontsize=10, color=ps.color(1))
ax2.set(xlim=(0, 5), xlabel="value", ylabel="fraction of samples (bin width 0.1)",
        title="Means of 50 uniform draws are close to normal")

ps.caption(fig, "Left: exact areas from the normal CDF. Right: simulated, 10^6 single draws and 20,000 means of 50 draws (seed 0).")
ps.save(fig, __file__)
