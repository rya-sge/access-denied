"""Gas of a transaction against its calldata size, before and after the EIP-7623 floor (Pectra).
Illustrative transaction: 50,000 gas of execution, calldata made only of non-zero bytes."""
import os, sys
sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps
import numpy as np

EXEC = 50_000          # execution gas of the example transaction
n = np.arange(0, 10_001, 50)                    # non-zero calldata bytes
before = 21_000 + 16 * n + EXEC                 # 4 tokens per byte x 4 gas
floor = 21_000 + 40 * n                         # 4 tokens per byte x 10 gas
after = np.maximum(before, floor)
cross = EXEC / 24                               # 40 n = 16 n + EXEC

ps.apply()
fig, ax = ps.figure()
c0, ls0, _ = ps.style(0)
c1, ls1, _ = ps.style(1)
ax.plot(n, before / 1e3, color=c0, linestyle=ls0, label="before Pectra: 21,000 + execution + 16 gas per non-zero byte")
ax.plot(n, after / 1e3, color=c1, linestyle=ls1, label="since Pectra: the larger of that and 21,000 + 40 gas per non-zero byte")
ax.fill_between(n, before / 1e3, after / 1e3, where=n >= cross, color=ps.color("orange"), alpha=0.25)
ax.legend(loc="upper left", fontsize=9, frameon=False)
ax.axvline(cross, color="0.5", linewidth=0.8, linestyle=":")
ax.text(cross + 120, 30, f"floor binds above {cross:,.0f} bytes", fontsize=9, color="0.3")
ax.set_xlabel("Calldata size (non-zero bytes)")
ax.set_ylabel("Gas used (thousands)")
ax.set_xlim(0, 10_000)
ax.set_ylim(0, 450)
ps.caption(fig, "Example transaction with 50,000 gas of execution; values from EIP-7623 (standard 4 gas per token, floor 10 gas per token).")
ps.save(fig, __file__)
