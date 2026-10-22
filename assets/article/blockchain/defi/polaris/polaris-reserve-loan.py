"""Generate polaris-reserve-loan.svg (no third-party dependency).

Uses the Reserve Loans example from the Polaris documentation: 1 fpETH deposited with a floor
of 1 ETH, 1 ETH borrowed (0.9995 received after the 0.05% opening fee), the floor later at 1.2 ETH,
and a utilization-based fee share of 1% of the 0.2 ETH floor growth.

Run: python3 polaris-reserve-loan.py  (writes the SVG next to this file)
"""
import os

W, H = 980, 470
SKY, ORANGE, BLUE, GREEN, VERM = "#56B4E9", "#E69F00", "#0072B2", "#009E73", "#D55E00"
INK, GRID, MUTED = "#222222", "#DDDDDD", "#555555"
out = []


def text(x, y, s, size=13, anchor="start", weight="normal", fill=INK):
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
               f'font-weight="{weight}" fill="{fill}">{s}</text>')


def axes(x0, y0, w, h, ymin, ymax, yticks, ylabel, title):
    sy = lambda v: y0 + h - (v - ymin) / (ymax - ymin) * h
    for t in yticks:
        out.append(f'<line x1="{x0}" y1="{sy(t):.1f}" x2="{x0 + w}" y2="{sy(t):.1f}" stroke="{GRID}"/>')
        text(x0 - 8, sy(t) + 4, f"{t:g}", 11, "end")
    out.append(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}"/>')
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{INK}"/>')
    out.append(f'<text transform="translate({x0 - 44},{y0 + h / 2}) rotate(-90)" font-size="12" '
               f'text-anchor="middle" fill="{INK}">{ylabel}</text>')
    text(x0 + w / 2, y0 - 14, title, 14, "middle", "bold")
    return sy


out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="DejaVu Sans, Helvetica, Arial, sans-serif">')
out.append(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')

# Left panel: floor value of the collateral versus the loan debt, over time
x0, y0, w, h = 90, 50, 500, 330
sy = axes(x0, y0, w, h, 0.9, 1.3, [0.9, 1.0, 1.1, 1.2, 1.3], "value in ETH",
          "Collateral floor value and debt, both in ETH")
sx = lambda t: x0 + t / 10 * w
# The floor rises in steps, each time the Fee Router burns revenue at the floor
steps = [(0, 1.00), (1.2, 1.02), (2.3, 1.05), (3.1, 1.07), (4.4, 1.10), (5.6, 1.12), (6.5, 1.15),
         (7.7, 1.17), (8.8, 1.20), (10, 1.20)]
d = f"M{sx(0):.1f},{sy(1.0):.1f}"
for (t, v), (t2, _) in zip(steps, steps[1:]):
    d += f" L{sx(t):.1f},{sy(v):.1f} L{sx(t2):.1f},{sy(v):.1f}"
area = d + f" L{sx(10):.1f},{sy(1.0):.1f} L{sx(0):.1f},{sy(1.0):.1f} Z"
out.append(f'<path d="{area}" fill="{GREEN}" fill-opacity="0.25"/>')
out.append(f'<path d="{d}" fill="none" stroke="{GREEN}" stroke-width="2.5"/>')
out.append(f'<line x1="{sx(0):.1f}" y1="{sy(1.0):.1f}" x2="{sx(10):.1f}" y2="{sy(1.0):.1f}" '
           f'stroke="{BLUE}" stroke-width="2.5" stroke-dasharray="8,5"/>')
text(sx(9.9), sy(1.2) - 10, "fpETH floor value (only rises)", 12, "end", "bold", GREEN)
text(sx(9.9), sy(1.0) + 20, "loan debt: 1 ETH (received 0.9995 after the 0.05% fee)", 12, "end", "bold", BLUE)
text(sx(7.0), sy(1.05), "floor growth while the loan is open", 12, "middle")
text(sx(7.0), sy(1.033), "(the fee is a share of this area)", 11, "middle", fill=MUTED)
for t, label in ((0, "open"), (10, "later")):
    text(sx(t), y0 + h + 19, label, 11, "middle")
text(x0 + w / 2, y0 + h + 40, "time", 12, "middle")
text(x0 + 6, y0 + 16, "The ETH/USD price appears nowhere: the debt can never exceed the collateral.", 11,
     "start", fill=MUTED)

# Right panel: composition of the collateral's floor value at opening and later
x1, w1 = 720, 220
sy2 = axes(x1, y0, w1, h, 0, 1.3, [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2], "value in ETH",
           "Where the floor value goes")
bw = 62
for cx, segs, label in ((x1 + 55, [(0, 1.0, BLUE, "debt 1.0")], "open"),
                        (x1 + 160, [(0, 1.0, BLUE, "debt 1.0"), (1.0, 1.198, GREEN, "0.198"), (1.198, 1.2, VERM, "")],
                         "later")):
    for a, b, colour, seg_label in segs:
        out.append(f'<rect x="{cx - bw / 2:.1f}" y="{sy2(b):.1f}" width="{bw}" height="{sy2(a) - sy2(b):.1f}" '
                   f'fill="{colour}" fill-opacity="0.8" stroke="#FFFFFF"/>')
        if seg_label:
            text(cx, (sy2(a) + sy2(b)) / 2 + 4, seg_label, 12, "middle", "bold", "#FFFFFF")
    text(cx, y0 + h + 19, label, 11, "middle")
    text(cx, sy2(segs[-1][1]) - 8, f"floor {segs[-1][1]:g}", 11, "middle", "bold")
text(x1 + 160, sy2(1.0) - 6, "borrower", 10, "middle", "bold", "#FFFFFF")
text(x1 + 160, sy2(1.2) - 22, "0.002 fee (1%)", 11, "middle", "bold", VERM)

text(W / 2, H - 12, "Numbers from the Polaris documentation's example; the floor's step pattern is illustrative.",
     11, "middle", fill=MUTED)
out.append("</svg>")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "polaris-reserve-loan.svg"), "w") as fh:
    fh.write("\n".join(out))
