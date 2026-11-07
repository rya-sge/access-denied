#!/usr/bin/env python3
"""Success probability of Grover search against the iteration count, N = 1024."""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps

N = 1024
ps.apply()
fig, ax = ps.figure()

j = np.arange(0, 91)
for i, M in enumerate((1, 4)):
    theta = math.asin(math.sqrt(M / N))
    p = np.sin((2 * j + 1) * theta) ** 2
    c, ls, marker = ps.style(i)
    ax.plot(j, p, color=c, linestyle=ls)
    print(f"M={M}: P(25)={np.sin(51 * theta) ** 2:.4f}")

opt = int(math.pi / 4 / math.asin(1 / math.sqrt(N)))
ax.axvline(opt, color="0.35", linestyle=":", linewidth=1.2)
ax.annotate(f"{opt} iterations\nP = 0.9995 for M = 1\nP = 0.0023 for M = 4",
            xy=(opt, 0.0023), xytext=(opt + 2, 0.44), fontsize=11,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="0.6"))

c0, _, _ = ps.style(0)
c1, _, _ = ps.style(1)
ax.text(75, 1.04, "M = 1", color=c0, fontsize=12, ha="center")
ax.text(12, 1.04, "M = 4", color=c1, fontsize=12, ha="center")

ax.set_xlabel("Grover iterations j")
ax.set_ylabel("Probability of measuring a solution")
ax.set_xlim(0, 90)
ax.set_ylim(0, 1.13)
ps.caption(fig, "sin²((2j+1)θ) with sin²θ = M/N, N = 1024; values match a state-vector simulation.")
ps.save(fig, __file__)
