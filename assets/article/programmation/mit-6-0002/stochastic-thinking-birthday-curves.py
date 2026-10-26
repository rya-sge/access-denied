"""Birthday problem curves for the MIT 6.0002 lecture 4 article (create-plot skill).

P(at least k people share a birthday) for a group of N people, computed exactly
(no simulation) with the exponential generating function
    P(no day has k or more people) = N! [x^N] prod_d sum_{j<k} (p_d x)^j / j!
for (a) 366 equally likely dates and (b) the lecture's non-uniform weights.
Run: python3 -I stochastic-thinking-birthday-curves.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps  # noqa: E402

NMAX = 150


def weights_uniform():
    return [1] * 366


def weights_lecture():
    # possibleDates from lecture 4 (slide 23): relative frequency of each day index
    dates = 4 * list(range(0, 57)) + [58] + 4 * list(range(59, 366)) + 4 * list(range(180, 270))
    return [dates.count(d) for d in range(366)]


def p_shared(weights, k, nmax=NMAX):
    """Return [P(some date has >= k people) for N = 0..nmax]."""
    total = sum(weights)
    poly = [1.0] + [0.0] * nmax          # coefficients of the EGF product
    for w in weights:
        if w == 0:
            continue
        p = w / total
        term = [p ** j / math.factorial(j) for j in range(k)]
        new = [0.0] * (nmax + 1)
        for i, c in enumerate(poly):
            if c == 0.0:
                continue
            for j, t in enumerate(term):
                if i + j > nmax:
                    break
                new[i + j] += c * t
        poly = new
    return [1.0 - poly[n] * math.factorial(n) for n in range(nmax + 1)]


N = list(range(NMAX + 1))
curves = [
    (p_shared(weights_uniform(), 2), "two share, uniform"),
    (p_shared(weights_uniform(), 3), "three share, uniform"),
    (p_shared(weights_lecture(), 3), "three share, lecture's non-uniform dates"),
]

ps.apply()
fig, ax = ps.figure()
for i, (y, _) in enumerate(curves):
    c, ls, _m = ps.style(i)
    ax.plot(N, y, color=c, linestyle=ls)
ax.set(xlim=(0, NMAX), ylim=(0, 1.02), xlabel="Number of people $N$",
       ylabel="Probability", title="Probability that at least k people share a birthday")

ps.label_end(ax, 52, curves[0][0][52], "two share, uniform", ps.color(0), dx=8, dy=-6)
ps.label_end(ax, 108, 0.45, "three share, uniform (dashed)", ps.color(1))
ps.label_end(ax, 82, 0.28, "three share, lecture's non-uniform dates (dotted)", ps.color(2))

for n, y, txt, col in [(23, curves[0][0][23], "N = 23: 0.506", 0),
                       (100, curves[1][0][100], "N = 100: 0.644", 1),
                       (100, curves[2][0][100], "N = 100: 0.749", 2)]:
    ax.plot([n], [y], marker="o", color=ps.color(col), markersize=5)
    if col == 2:
        ps.label_end(ax, n, y, txt, ps.color(col), ha="right", dx=-8, dy=10)
    else:
        ps.label_end(ax, n, y, txt, ps.color(col), ha="left" if col == 1 else "right",
                     dx=6 if col == 1 else -8, dy=-12 if col == 1 else 8)

for n in (23, 100):
    print(n, [round(c[0][n], 6) for c in curves])
ps.caption(fig, "Exact values from the generating function, 366 possible dates; no simulation noise.")
ps.save(fig, __file__)
