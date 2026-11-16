"""PT price toward and after expiry (create-plot skill), for _posts/2026-11-16-pendle-v2-pt-yt-amm.md.

Left: PT price in asset over the last year before expiry, at a constant 10 % implied APY (no trade),
against two linear-discount oracles (d = 10 % and d = 18 %), and the market price if the implied
rate jumps to 20 % six months before expiry. Right: after expiry, 1 PT left unredeemed stays worth
1 asset, while the same PT redeemed into SY at expiry keeps earning the underlying yield (8 %, illustrative).
Run: python3 -I pendle-pt-price-expiry.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps  # noqa: E402

ps.apply()
fig, (ax1, ax2) = ps.figure(ncols=2, width_ratios=(1.35, 1))

# Left panel: days before expiry, from 365 to 0
days = np.linspace(365, 0, 731)
tau = days / 365.0
market = np.exp(-np.log(1.10) * tau)  # constant 10 % implied APY, no trade
lin10 = 1 - 0.10 * tau
lin18 = 1 - 0.18 * tau
shock_days = days[days <= 182.5]
shock = np.exp(-np.log(1.20) * shock_days / 365.0)  # implied rate 20 % from 182.5 days out

c0, ls0, _ = ps.style(0)
c1, ls1, _ = ps.style(1)
c2, ls2, _ = ps.style(2)
c3, ls3, _ = ps.style(4)
ax1.plot(-days, market, color=c0, linestyle=ls0)
ax1.plot(-days, lin10, color=c1, linestyle=ls1)
ax1.plot(-days, lin18, color=c2, linestyle=ls2)
ax1.plot(-shock_days, shock, color=c3, linestyle=ls3)
ax1.plot([-182.5], [np.exp(-np.log(1.10) * 0.5)], "o", color=c0, ms=5)
ax1.plot([-182.5], [0.95], "s", color=c1, ms=5)
ax1.plot([-182.5], [np.exp(-np.log(1.20) * 0.5)], "^", color=c3, ms=6)
ax1.set(xlim=(-365, 0), ylim=(0.80, 1.01), xlabel="days before expiry",
        ylabel="PT price (asset)", title="PT price toward expiry")
ax1.set_xticks([-365, -270, -182.5, -90, 0])
ax1.set_xticklabels(["365", "270", "182.5", "90", "0"])
ps.label_end(ax1, -355, 0.975, "market, 10 % implied", c0)
ps.label_end(ax1, -355, 0.887, "linear, d = 10 %", c1)
ps.label_end(ax1, -265, 0.838, "linear, d = 18 %", c2)
ps.label_end(ax1, -125, 0.855, "market after a\njump to 20 %", c3)
ps.label_end(ax1, -182.5, 0.9535, "0.9535", c0, ha="right", dx=-6, dy=10)
ps.label_end(ax1, -182.5, 0.95, "0.9500", c1, dx=6, dy=-14)
ps.label_end(ax1, -182.5, 0.9129, "0.9129", c3, ha="right", dx=-6, dy=8)

# Right panel: days after expiry, value in asset of what was 1 PT at expiry
after = np.linspace(0, 180, 361)
held = np.ones_like(after)
redeemed = np.exp(0.08 * after / 365.0)  # SY earning 8 % a year (illustrative, continuous)
ax2.plot(after, held, color=c0, linestyle=ls0)
ax2.plot(after, redeemed, color=c2, linestyle=ls2)
ax2.set(xlim=(0, 180), ylim=(0.99, 1.05), xlabel="days after expiry",
        ylabel="value (asset)", title="After expiry: PT held or redeemed")
ps.label_end(ax2, 90, 1.0, "PT left unredeemed: 1 asset", c0, dy=-11, ha="center")
ps.label_end(ax2, 5, 1.036, "redeemed into SY at expiry", c2)

ps.caption(fig, "Illustrative parameters: constant implied APY with no trade; SY yield after expiry 8 % a year. "
                "What an unredeemed PT forgoes goes to Pendle's treasury.")
ps.save(fig, __file__)
