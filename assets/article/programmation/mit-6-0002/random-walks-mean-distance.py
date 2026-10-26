"""Mean distance from the origin versus number of steps, for the unbiased (UsualDrunk) and the
biased (MasochistDrunk) walks of MIT 6.0002 Lecture 5. Run: python3 -I <this file>

The final position of a lattice walk of n steps only depends on how many of the n steps went
north, south, east and west, so it is drawn exactly from a multinomial(n, 1/4, 1/4, 1/4, 1/4)
distribution instead of simulating each step. 1000 walks per length, seed 0.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps  # noqa: E402

TRIALS = 1000
rng = np.random.default_rng(0)
steps = np.unique(np.round(np.logspace(1, 5, 25)).astype(int))   # 10 .. 100000


def mean_distance(n, north, south):
    """Mean final distance of TRIALS walks of n steps; north/south are the step lengths on y."""
    counts = rng.multinomial(n, [0.25] * 4, size=TRIALS)          # N, S, E, W
    y = north * counts[:, 0] - south * counts[:, 1]
    x = counts[:, 2] - counts[:, 3]
    return np.hypot(x, y).mean()


usual = np.array([mean_distance(n, 1.0, 1.0) for n in steps])
maso = np.array([mean_distance(n, 1.1, 0.9) for n in steps])

ps.apply()
fig, (ax1, ax2) = ps.figure(ncols=2, width_ratios=(1, 1))

series = [
    (usual, "UsualDrunk (simulated)", 0, "o"),
    (maso, "MasochistDrunk (simulated)", 1, "s"),
]
refs = [
    (np.sqrt(steps), "√n", 2),
    (0.05 * steps, "0.05·n", 3),
]

for ax, log in ((ax1, False), (ax2, True)):
    for y, _, i, m in series:
        c, ls, _ = ps.style(i)
        ax.plot(steps, y, color=c, linestyle=ls, marker=m, markersize=4)
    for y, _, i in refs:
        c, ls, _ = ps.style(i)
        ax.plot(steps, y, color=c, linestyle=ls, linewidth=1.4)

ax1.set(xlim=(0, 105000), ylim=(0, 5300), xlabel="number of steps $n$",
        ylabel="mean distance from origin", title="Linear axes (as in the lecture)")
ps.label_end(ax1, steps[-1], maso[-1], "MasochistDrunk", ps.color(1), ha="right", dx=-8, dy=10)
ps.label_end(ax1, 62000, 0.05 * 62000, "0.05·n", ps.color(3), dx=6, dy=-10)
ps.label_end(ax1, steps[-1], usual[-1], "UsualDrunk and √n", ps.color(0), ha="right", dx=-4, dy=14)

ax2.set(xscale="log", yscale="log", xlim=(8, 130000), ylim=(1, 8000),
        xlabel="number of steps $n$ (log scale)", ylabel="mean distance (log scale)",
        title="Log-log axes: slopes 1/2 and 1")
ps.plain_log_ticks(ax2)
ps.label_end(ax2, steps[-1], maso[-1], "MasochistDrunk", ps.color(1), ha="right", dx=-6, dy=12)
ps.label_end(ax2, 60, 0.05 * 60, "0.05·n", ps.color(3), dx=6, dy=-6)
ps.label_end(ax2, 1500, 14, "UsualDrunk", ps.color(0), dx=0, dy=0)
ps.label_end(ax2, 20, np.sqrt(20), "√n", ps.color(2), ha="right", dx=-2, dy=12)

ps.caption(fig, "1000 simulated walks per length, seed 0. The UsualDrunk mean sits slightly below √n "
                "(about 0.886·√n);\nthe MasochistDrunk follows its drift 0.05·n once n is above a few hundred.")
ps.save(fig, __file__)
for n, u, m in zip(steps, usual, maso):
    if n in (10, 100, 1000, 10000, 100000):
        print(n, round(u, 2), round(u / np.sqrt(n), 3), round(m, 1))
