"""Generate power-law-linear-vs-loglog.svg (no third-party dependency).

The same power laws y = x^k (k = 2, 1, 0.5, -1) drawn on linear axes (left) and on
logarithmic axes (right), where each becomes a straight line of slope k.

Run: python3 power-law-linear-vs-loglog.py  (writes the SVG next to this file)
"""
import math
import os

W, H = 980, 470
BLUE, ORANGE, GREEN, VERM = "#0072B2", "#E69F00", "#009E73", "#D55E00"
INK, GRID, MUTED = "#222222", "#DDDDDD", "#555555"
CURVES = [(2.0, VERM, "", "k = 2"), (1.0, BLUE, "8,5", "k = 1"), (0.5, GREEN, "2,4", "k = 0.5"),
          (-1.0, ORANGE, "12,4,2,4", "k = −1")]
out = []


def text(x, y, s, size=13, anchor="start", weight="normal", fill=INK):
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
               f'font-weight="{weight}" fill="{fill}">{s}</text>')


def frame(x0, y0, w, h, xlabel, ylabel, title):
    out.append(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}"/>')
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{INK}"/>')
    text(x0 + w / 2, y0 + h + 40, xlabel, 12, "middle")
    out.append(f'<text transform="translate({x0 - 42},{y0 + h / 2}) rotate(-90)" font-size="12" '
               f'text-anchor="middle" fill="{INK}">{ylabel}</text>')
    text(x0 + w / 2, y0 - 14, title, 14, "middle", "bold")


def clip(x0, y0, w, h, cid):
    out.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{w}" height="{h}"/></clipPath>')


out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="DejaVu Sans, Helvetica, Arial, sans-serif">')
out.append(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')

# Left: linear axes, x in [0, 4], y in [0, 6]
x0, y0, w, h = 80, 50, 380, 330
clip(x0, y0, w, h, "c1")
sx = lambda v: x0 + v / 4 * w
sy = lambda v: y0 + h - v / 6 * h
for t in range(0, 7):
    out.append(f'<line x1="{x0}" y1="{sy(t):.1f}" x2="{x0 + w}" y2="{sy(t):.1f}" stroke="{GRID}"/>')
    text(x0 - 8, sy(t) + 4, str(t), 11, "end")
for t in range(0, 5):
    text(sx(t), y0 + h + 19, str(t), 11, "middle")
frame(x0, y0, w, h, "x", "y", 'y = x<tspan baseline-shift="super" font-size="10">k</tspan> on linear axes')
for k, colour, dash, label in CURVES:
    lo = 0.17 if k < 0 else 0.0
    pts = [lo + (4 - lo) * i / 300 for i in range(301)]
    d = " ".join(f"{'M' if i == 0 else 'L'}{sx(x):.1f},{sy(x ** k if x > 0 else 0):.1f}" for i, x in enumerate(pts))
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="2.5"{dd} clip-path="url(#c1)"/>')
text(sx(2.45) + 4, sy(6) + 16, "k = 2", 12, "start", "bold", VERM)
text(sx(4) - 4, sy(4) - 8, "k = 1", 12, "end", "bold", BLUE)
text(sx(4) - 4, sy(2) - 8, "k = 0.5", 12, "end", "bold", GREEN)
text(sx(4) - 4, sy(0.25) - 8, "k = −1", 12, "end", "bold", ORANGE)

# Right: log-log axes, x and y in [0.1, 10]
x1, w1 = 600, 340
clip(x1, y0, w1, h, "c2")
lx = lambda v: x1 + (math.log10(v) + 1) / 2 * w1
ly = lambda v: y0 + h - (math.log10(v) + 1) / 2 * h
for t, lab in ((0.1, "0.1"), (1, "1"), (10, "10")):
    out.append(f'<line x1="{x1}" y1="{ly(t):.1f}" x2="{x1 + w1}" y2="{ly(t):.1f}" stroke="{GRID}"/>')
    out.append(f'<line x1="{lx(t):.1f}" y1="{y0}" x2="{lx(t):.1f}" y2="{y0 + h}" stroke="{GRID}"/>')
    text(x1 - 8, ly(t) + 4, lab, 11, "end")
    text(lx(t), y0 + h + 19, lab, 11, "middle")
frame(x1, y0, w1, h, "x (log scale)", "y (log scale)", "The same curves on log-log axes")
for k, colour, dash, label in CURVES:
    pts = [10 ** (-1 + 2 * i / 200) for i in range(201)]
    d = " ".join(f"{'M' if i == 0 else 'L'}{lx(x):.1f},{ly(x ** k):.1f}" for i, x in enumerate(pts))
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="2.5"{dd} clip-path="url(#c2)"/>')
text(lx(2.0) - 8, ly(4.0), "slope 2", 12, "end", "bold", VERM)
text(lx(5.0) + 8, ly(5.0) + 16, "slope 1", 12, "start", "bold", BLUE)
text(lx(5.0) + 8, ly(2.236) + 18, "slope 0.5", 12, "start", "bold", GREEN)
text(lx(4.0) + 4, ly(0.25) - 14, "slope −1", 12, "start", "bold", ORANGE)

text(W / 2, H - 12, 'A power law y = a·x<tspan baseline-shift="super" font-size="10">k</tspan> is a straight line of slope k once both axes are logarithmic.',
     11, "middle", fill=MUTED)
out.append("</svg>")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "power-law-linear-vs-loglog.svg"), "w") as fh:
    fh.write("\n".join(out))
