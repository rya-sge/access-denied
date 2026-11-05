"""Largest exchange hacks, reported loss in USD millions (nominal, upper figure where sources disagree).

Sources: this site's yearly hack articles (2018 to 2024, 2026 year to date), the Bybit article for Bybit,
Binance's statement of 30 October 2026 for Binance (~6.3B USD).
Run with: python3 -I 2026-10-30-bybit-hack-february-2025-cex-comparison.py
"""
import os
import sys

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

# (label, USD millions, signing process subverted rather than keys or credentials stolen)
HACKS = [
    ("Binance (Oct 2026)", 6300, True),
    ("Bybit (Feb 2025)", 1460, True),
    ("Coincheck (Jan 2018)", 534, False),
    ("FTX drain (Nov 2022)", 477, False),
    ("Bitget (Sep 2026)", 387.5, True),
    ("DMM Bitcoin (May 2024)", 305, True),
    ("KuCoin (Sep 2020)", 281, False),
    ("WazirX (Jul 2024)", 235, True),
    ("BitMart (Dec 2021)", 196, False),
    ("Poloniex (Nov 2023)", 130, False),
    ("HTX and HECO (Nov 2023)", 113, False),
    ("Liquid (Aug 2021)", 97, False),
    ("Upbit (Nov 2019)", 49, False),
    ("Binance (May 2019)", 40, False),
]

ps.apply()
fig, ax = ps.figure(width_px=1100, height_px=620)
red, grey = ps.color("vermillion"), "#9E9E9E"
labels = [h[0] for h in HACKS][::-1]
values = [h[1] for h in HACKS][::-1]
signing = [h[2] for h in HACKS][::-1]
for i, (lab, v, s) in enumerate(zip(labels, values, signing)):
    ax.barh(i, v, height=0.62, color=red if s else grey)
    text = f"\\${v / 1000:.2f}B" if v >= 1000 else f"\\${v:.0f}M"
    ax.annotate(text, (v, i), xytext=(5, 0), textcoords="offset points", va="center", fontsize=10,
                fontweight="bold" if lab.startswith("Bybit") else "normal")
ax.set_yticks(range(len(labels)), labels)
ax.set_xlim(0, 7000)
ax.set_xlabel("Reported loss, USD millions (nominal, at the time of each hack)")
ax.grid(axis="y", visible=False)
ax.legend(handles=[Patch(color=red, label="Signing process subverted, keys used as designed"),
                   Patch(color=grey, label="Keys or credentials stolen")], loc="lower right", frameon=False)
ax.set_title("Bybit was 2.7x the largest exchange hack before it, Binance 2026 is 4.3x Bybit", loc="left")
ps.caption(fig, "Upper figure where sources disagree. Sources: access-denied yearly hack articles (2018 to 2026), "
                "Binance statement of 30 Oct 2026 (~\\$6.3B).")
ps.save(fig, __file__, png_dpi=200)
