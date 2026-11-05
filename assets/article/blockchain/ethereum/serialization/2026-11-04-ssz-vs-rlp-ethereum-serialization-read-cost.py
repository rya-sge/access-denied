"""Net gas to read `amount` from element i of 16 real withdrawals. Data: forge run."""
import os
import re
import sys

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps  # noqa: E402

src = os.path.expanduser(
    "~/Downloads/me/access-denied/verification/ssz-vs-rlp-ethereum-serialization/results/forge.txt")
t = open(src).read()
rlp = [int(x) for x in re.findall(r"net rlpListAmount: (\d+)", t)]
ssz = [int(x) for x in re.findall(r"net sszListAmount: (\d+)", t)]
assert len(rlp) == len(ssz) == 16
ps.apply()
fig, ax = ps.figure()
xs = list(range(16))
c, ls, m = ps.style(0)
ax.plot(xs, rlp, color=c, linestyle=ls, marker=m)
c2, ls2, m2 = ps.style(1)
ax.plot(xs, ssz, color=c2, linestyle=ls2, marker=m2)
ax.text(3.2, 12500, "RLP: walk every earlier item", color=c)
ax.text(6, ssz[6] + 900, "SSZ: fixed offset", color=c2)
ax.set_xlabel("Withdrawal position in the list")
ax.set_ylabel("Net gas")
ax.set_ylim(0, 18000)
ps.save(fig, __file__)
ps.greyscale_preview(__file__.replace(".py", ".png"))
