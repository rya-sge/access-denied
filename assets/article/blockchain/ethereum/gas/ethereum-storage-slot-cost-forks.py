"""Gas for the first write to a storage slot in a transaction, by fork, split into execution gas and state gas.
Constants from execution-specs forks/frontier, forks/osaka and forks/amsterdam (vm/gas.py, vm/instructions/storage.py)."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps

FORKS = ["Frontier\n(2015)", "Berlin to Fusaka\n(2021–2026)", "Glamsterdam\n(Sepolia 2026)"]
# (execution gas, state gas)
NEW = [(20_000, 0), (22_100, 0), (12_100, 97_920)]       # slot was zero
EXISTING = [(5_000, 0), (5_000, 0), (12_100, 0)]          # slot was non-zero

ps.apply()
fig, (ax1, ax2) = ps.figure(ncols=2, width_ratios=(1.25, 1))
for ax, data, title in ((ax1, NEW, "Slot that was zero (new holder)"), (ax2, EXISTING, "Slot that already held a value")):
    ex = [d[0] for d in data]; st = [d[1] for d in data]
    ax.bar(FORKS, ex, color=ps.color("blue"), label="execution gas")
    ax.bar(FORKS, st, bottom=ex, color=ps.color("orange"), hatch="//", edgecolor="white", label="state gas")
    for i, (e, s) in enumerate(data):
        ax.text(i, e + s + 1500, f"{e + s:,}", ha="center", fontsize=9)
    ax.set_title(title, fontsize=10)
    ax.tick_params(axis="x", labelsize=8)
ax1.set_ylabel("Gas for the first write in a transaction")
ax1.set_ylim(0, 125_000); ax2.set_ylim(0, 125_000)
ax1.yaxis.set_major_formatter(lambda v, _: f"{v/1e3:g}k" if v else "0"); ax2.yaxis.set_major_formatter(lambda v, _: f"{v/1e3:g}k" if v else "0")
ax1.legend(loc="upper left", fontsize=9, frameon=False)
ps.caption(fig, "Cold SSTORE cost from the execution specification; Glamsterdam constants (EIP-8037, EIP-8038) were in Last Call on 2026-10-23.")
ps.save(fig, __file__)
