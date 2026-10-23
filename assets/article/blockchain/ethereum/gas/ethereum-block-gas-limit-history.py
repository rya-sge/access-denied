"""Mainnet block gas limit from 2015 to 2026, read with eth_getBlockByNumber (2026-10-23)."""
import os, sys
from datetime import date
sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

# (block date, gas limit) at sampled mainnet blocks
DATA = [
    (date(2015, 7, 30), 5000),        # genesis
    (date(2015, 8, 7), 21003),        # block 46,147
    (date(2015, 8, 7), 304254),       # block 50,000
    (date(2015, 8, 13), 3141592),     # block 80,000
    (date(2015, 12, 16), 3141592),
    (date(2016, 2, 13), 3141592),
    (date(2016, 3, 14), 4712388),     # Homestead
    (date(2016, 9, 4), 4712384),
    (date(2016, 9, 21), 4704588),
    (date(2016, 10, 11), 1497071),
    (date(2016, 10, 18), 500000),     # Tangerine Whistle
    (date(2016, 10, 24), 1992676),
    (date(2016, 11, 22), 2000000),    # Spurious Dragon
    (date(2017, 4, 8), 4262058),
    (date(2017, 7, 9), 6712392),
    (date(2017, 10, 16), 6705806),    # Byzantium
    (date(2018, 1, 30), 8000029),
    (date(2019, 4, 4), 8023456),
    (date(2019, 6, 21), 8002255),
    (date(2019, 12, 8), 8950633),     # Istanbul
    (date(2020, 5, 4), 9990236),
    (date(2020, 10, 6), 12451188),
    (date(2021, 4, 15), 12457275),    # Berlin
    (date(2021, 5, 24), 14985252),
    (date(2021, 8, 5), 30029122),     # London
    (date(2022, 1, 13), 30058561),
    (date(2022, 9, 15), 30000000),    # Paris (Merge)
    (date(2024, 6, 1), 30000000),
    (date(2024, 12, 28), 30000000),
    (date(2025, 2, 8), 36000000),
    (date(2025, 7, 12), 36140342),
    (date(2025, 9, 5), 45000000),
    (date(2025, 11, 14), 45000000),
    (date(2025, 11, 28), 59940950),
    (date(2026, 1, 9), 59999943),
    (date(2026, 10, 22), 60000000),
]

ps.apply()
fig, ax = ps.figure()
c, ls, marker = ps.style(0)
xs = [d for d, _ in DATA]
ys = [g for _, g in DATA]
ax.plot(xs, ys, color=c, linestyle=ls, marker=marker, markersize=4, linewidth=1.5)
ax.set_yscale("log")
ax.set_ylim(3000, 2.5e8)
ax.yaxis.set_major_formatter(FuncFormatter(
    lambda v, _: f"{v/1e6:g}M" if v >= 1e6 else (f"{v/1e3:g}k" if v >= 1e3 else f"{v:g}")))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.set_ylabel("Block gas limit (log scale)")

# per-transaction cap of EIP-7825 since Fusaka (2025-12-03)
cap_c, cap_ls, _ = ps.style(1)
ax.hlines(2**24, date(2025, 12, 3), date(2026, 10, 22), color=cap_c, linestyle="--")
ax.annotate("per-transaction cap 16.8M\n(Fusaka, EIP-7825)", (date(2025, 12, 3), 2**24),
            xytext=(date(2023, 6, 1), 4.5e6), color=cap_c, fontsize=9,
            arrowprops=dict(arrowstyle="-", color=cap_c, lw=0.8))

notes = [
    (date(2015, 8, 7), 21003, "genesis 5,000; 3,141,592 by mid-August 2015", (date(2016, 1, 1), 12000)),
    (date(2016, 10, 18), 500000, "Oct. 2016 DoS attacks: 500,000", (date(2017, 3, 1), 180000)),
    (date(2021, 8, 5), 30029122, "London: limit 30M, target 15M", (date(2018, 6, 1), 60e6)),
    (date(2025, 11, 28), 59940950, "60M (2025)", (date(2024, 1, 1), 1.2e8)),
]
for x, y, text, xy in notes:
    ax.annotate(text, (x, y), xytext=xy, fontsize=9,
                arrowprops=dict(arrowstyle="-", color="0.4", lw=0.8))

ps.caption(fig, "Gas limit of sampled Ethereum mainnet blocks (dots), read with eth_getBlockByNumber on 2026-10-23; lines join the samples.")
ps.save(fig, __file__)
