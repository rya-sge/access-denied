"""Generate polaris-adaptive-peg-defense.svg (no third-party dependency).

Left panel: a pAsset's market price around its peg and the arbitrage that applies on each side.
Right panel: the aggregate effect on a market of a 50,000 peg buy and of a 50,000 redemption at peg,
with illustrative numbers and fees ignored. The documentation does not specify how the change is
split between individual positions, so only market totals are drawn.

Run: python3 polaris-adaptive-peg-defense.py  (writes the SVG next to this file)
"""
import math
import os

W, H = 980, 470
SKY, ORANGE, BLUE, GREEN, VERM = "#56B4E9", "#E69F00", "#0072B2", "#009E73", "#D55E00"
INK, GRID, MUTED = "#222222", "#DDDDDD", "#555555"
out = []


def text(x, y, s, size=13, anchor="start", weight="normal", fill=INK):
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
               f'font-weight="{weight}" fill="{fill}">{s}</text>')


def axes(x0, y0, w, h, ymin, ymax, yticks, fmt, ylabel, title):
    sy = lambda v: y0 + h - (v - ymin) / (ymax - ymin) * h
    for t in yticks:
        out.append(f'<line x1="{x0}" y1="{sy(t):.1f}" x2="{x0 + w}" y2="{sy(t):.1f}" stroke="{GRID}"/>')
        text(x0 - 8, sy(t) + 4, fmt(t), 11, "end")
    out.append(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}"/>')
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{INK}"/>')
    out.append(f'<text transform="translate({x0 - 50},{y0 + h / 2}) rotate(-90)" font-size="12" '
               f'text-anchor="middle" fill="{INK}">{ylabel}</text>')
    text(x0 + w / 2, y0 - 14, title, 14, "middle", "bold")
    return sy


out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="DejaVu Sans, Helvetica, Arial, sans-serif">')
out.append(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')
out.append(f'<defs><marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">'
           f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')

# Left panel: price around the peg
x0, y0, w, h = 100, 50, 440, 330
sy = axes(x0, y0, w, h, 0.97, 1.03, [0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03], lambda t: f"{t:.2f}",
          "market price (target = 1.00)", "A pAsset's market price around its peg")
sx = lambda t: x0 + t / 10 * w
out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{sy(1.0) - y0:.1f}" fill="{ORANGE}" fill-opacity="0.18"/>')
out.append(f'<rect x="{x0}" y="{sy(1.0):.1f}" width="{w}" height="{y0 + h - sy(1.0):.1f}" fill="{SKY}" '
           f'fill-opacity="0.22"/>')
out.append(f'<line x1="{x0}" y1="{sy(1.0):.1f}" x2="{x0 + w}" y2="{sy(1.0):.1f}" stroke="{INK}" '
           f'stroke-width="1.5" stroke-dasharray="6,4"/>')
price = lambda t: 1.0 + 0.017 * math.sin(t * 1.25) * math.exp(-0.12 * t)
d = " ".join(f"{'M' if i == 0 else 'L'}{sx(i / 20):.1f},{sy(price(i / 20)):.1f}" for i in range(201))
out.append(f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="2.5"/>')
text(x0 + w - 8, y0 + 20, "Above peg: buy newly minted pAsset at peg", 12, "end", "bold")
text(x0 + w - 8, y0 + 36, "with pETH, sell it; supply expands", 12, "end")
text(x0 + w - 8, y0 + h - 26, "Below peg: buy on the market, redeem", 12, "end", "bold")
text(x0 + w - 8, y0 + h - 10, "at peg for pETH; supply contracts", 12, "end")
out.append(f'<line x1="{sx(1.25):.1f}" y1="{sy(1.0165) - 4:.1f}" x2="{sx(1.25):.1f}" y2="{sy(1.004):.1f}" '
           f'stroke="{INK}" stroke-width="1.5" marker-end="url(#arr)"/>')
out.append(f'<line x1="{sx(3.75):.1f}" y1="{sy(0.9895) + 4:.1f}" x2="{sx(3.75):.1f}" y2="{sy(0.996):.1f}" '
           f'stroke="{INK}" stroke-width="1.5" marker-end="url(#arr)"/>')
text(x0 + w / 2, y0 + h + 22, "time", 12, "middle")

# Right panel: market totals before and after
x1, w1 = 690, 260
sy2 = axes(x1, y0, w1, h, 0, 2.5, [0, 0.5, 1.0, 1.5, 2.0], lambda t: f"{t:g}M",
           "market total, in pAsset units", "Effect on the whole market")
states = [("before", 1.70, 1.00), ("after peg", 1.75, 1.05), ("after", 1.65, 0.95)]
sub = ["", "buy 50k", "redeem 50k"]
bw = 26
for i, (label, coll, debt) in enumerate(states):
    cx = x1 + 45 + i * 85
    for off, v, colour, dash in ((-bw / 2 - 1, coll, GREEN, ""), (bw / 2 + 1, debt, VERM, "")):
        out.append(f'<rect x="{cx + off - bw / 2:.1f}" y="{sy2(v):.1f}" width="{bw}" height="{sy2(0) - sy2(v):.1f}" '
                   f'fill="{colour}" fill-opacity="0.8"/>')
    text(cx, sy2(coll) - 22, f"{coll / debt:.1%}".replace(".0%", "%"), 12, "middle", "bold")
    text(cx, sy2(coll) - 8, "ratio", 10, "middle", fill=MUTED)
    text(cx, y0 + h + 17, label, 11, "middle")
    text(cx, y0 + h + 31, sub[i], 11, "middle")
lx = x1 + 12
out.append(f'<rect x="{lx}" y="{y0 + 8}" width="12" height="12" fill="{GREEN}" fill-opacity="0.8"/>')
text(lx + 18, y0 + 18, "collateral (left bar)", 11)
out.append(f'<rect x="{lx}" y="{y0 + 26}" width="12" height="12" fill="{VERM}" fill-opacity="0.8"/>')
text(lx + 18, y0 + 36, "debt (right bar)", 11)

text(W / 2, H - 12, "Right panel: illustrative numbers, fees ignored. How the change is split between positions "
     "is not specified in the documentation.", 11, "middle", fill=MUTED)
out.append("</svg>")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "polaris-adaptive-peg-defense.svg"), "w") as fh:
    fh.write("\n".join(out))
