"""Fee of the EIP-7002 / EIP-7251 request contracts (create-plot skill).

Left: fake_exponential(1, excess, 17) as implemented in sys-asm src/common/fake_expo.eas.
Right: decay of that fee after a spike, with no new requests, for both contracts.
Run: python3 -I <this file>
"""
import os
import sys

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps  # noqa: E402

GWEI = 10 ** 9
ETHER = 10 ** 18


def fake_exponential(factor, numerator, denominator):
    i, output, accum = 1, 0, factor * denominator
    while accum > 0:
        output += accum
        accum = (accum * numerator) // (denominator * i)
        i += 1
    return output // denominator


def fee(excess):
    return fake_exponential(1, excess, 17)


ps.apply()
fig, (ax1, ax2) = ps.figure(ncols=2, width_ratios=(1.1, 1))

# Left panel: fee against excess
xs = list(range(0, 801, 5))
c, ls, m = ps.style(0)
ax1.plot(xs, [fee(x) for x in xs], color=c, linestyle=ls)
ax1.set(yscale="log", xlim=(0, 800), ylim=(0.5, 3e20), xlabel="excess requests",
        ylabel="fee in wei (log scale)", title="Fee as a function of excess")
ax1.axhline(GWEI, color="#777777", linewidth=0.8, linestyle=":")
ax1.axhline(ETHER, color="#777777", linewidth=0.8, linestyle=":")
ax1.text(8, GWEI * 1.8, "1 gwei", color="#444444", fontsize=10)
ax1.text(8, ETHER * 1.8, "1 ETH", color="#444444", fontsize=10)
for x, label, dx, ha in [(100, "100: 357 wei", 8, "left"),
                         (353, "353: above 1 gwei", 8, "left"),
                         (705, "705: above 1 ETH", -8, "right")]:
    y = fee(x)
    ax1.plot([x], [y], marker="o", color=c, markersize=5)
    ax1.annotate(label, (x, y), xytext=(dx, -12), textcoords="offset points", ha=ha, fontsize=10, color="#222222")

# Right panel: decay from excess 705 with no new requests
blocks = list(range(0, 721, 5))
for i, (name, target, x_end, y_end, ha, dx, dy) in enumerate([
        ("EIP-7002\n(−2 per block)", 2, 110, None, "left", -42, -135),
        ("EIP-7251 (−1 per block)", 1, 300, None, "left", 10, 8)]):
    c2, ls2, _ = ps.style(i + 1)
    ax2.plot(blocks, [fee(max(705 - target * b, 0)) for b in blocks], color=c2, linestyle=ls2)
    ax2.annotate(name, (x_end, fee(max(705 - target * x_end, 0))), xytext=(dx, dy),
                 textcoords="offset points", ha=ha, fontsize=10, color=c2)
ax2.set(yscale="log", xlim=(0, 720), ylim=(0.5, 3e20), xlabel="blocks after the spike",
        ylabel="fee in wei (log scale)", title="Decay from excess 705, no new requests")
ax2.axhline(1, color="#777777", linewidth=0.8, linestyle=":")

ps.caption(fig, "Computed with the integer algorithm of sys-asm (MIN_FEE = 1, FEE_UPDATE_FRACTION = 17). Excess 705 is an illustration, not an observed value.")
ps.save(fig, __file__)
