"""Generate polaris-power-law-curve.svg (no third-party dependency).

Left panel: p(s) = 2*sqrt(s) (alpha = 2, beta = 0.5, the prototype's test values),
with the reserve R(100) and the cost of a buy from s = 100 to s = 121 shaded.
Right panel: p(s) = s^beta for beta = 0.15 (testnet value read 2026-10-22), 0.5 and 1.

Run: python3 polaris-power-law-curve.py  (writes the SVG next to this file)
"""
import os

W, H = 980, 470
SKY, ORANGE, BLUE, GREEN, VERM = "#56B4E9", "#E69F00", "#0072B2", "#009E73", "#D55E00"
INK, GRID = "#222222", "#DDDDDD"
out = []


def text(x, y, s, size=13, anchor="start", weight="normal", fill=INK):
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
               f'font-weight="{weight}" fill="{fill}">{s}</text>')


def panel(x0, y0, w, h, xmax, ymax, xticks, yticks, xlabel, ylabel, title):
    sx = lambda v: x0 + v / xmax * w
    sy = lambda v: y0 + h - v / ymax * h
    for t in yticks:
        out.append(f'<line x1="{x0}" y1="{sy(t):.1f}" x2="{x0 + w}" y2="{sy(t):.1f}" stroke="{GRID}"/>')
        text(x0 - 8, sy(t) + 4, f"{t:g}", 11, "end")
    for t in xticks:
        out.append(f'<line x1="{sx(t):.1f}" y1="{y0 + h}" x2="{sx(t):.1f}" y2="{y0 + h + 5}" stroke="{INK}"/>')
        text(sx(t), y0 + h + 19, f"{t:g}", 11, "middle")
    out.append(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{INK}"/>')
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{INK}"/>')
    text(x0 + w / 2, y0 + h + 40, xlabel, 12, "middle")
    out.append(f'<text transform="translate({x0 - 42},{y0 + h / 2}) rotate(-90)" font-size="12" '
               f'text-anchor="middle" fill="{INK}">{ylabel}</text>')
    text(x0 + w / 2, y0 - 14, title, 14, "middle", "bold")
    return sx, sy


def path(f, a, b, sx, sy, n=200):
    pts = [(a + (b - a) * i / n) for i in range(n + 1)]
    return " ".join(f"{'M' if i == 0 else 'L'}{sx(x):.1f},{sy(f(x)):.1f}" for i, x in enumerate(pts))


def area(f, a, b, sx, sy, n=120):
    return f"M{sx(a):.1f},{sy(0):.1f} " + path(f, a, b, sx, sy, n).replace("M", "L", 1) + \
        f" L{sx(b):.1f},{sy(0):.1f} Z"


out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="DejaVu Sans, Helvetica, Arial, sans-serif">')
out.append(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')

# Left panel: the worked example
p = lambda s: 2 * s ** 0.5
sx, sy = panel(80, 50, 470, 330, 160, 28, [0, 20, 40, 60, 80, 100, 121, 140, 160], [0, 5, 10, 15, 20, 25],
               "supply s (pETH)", "marginal price p(s) (ETH per pETH)",
               "p(s) = 2·√s  (α = 2, β = 0.5)")
out.append(f'<path d="{area(p, 0, 100, sx, sy)}" fill="{SKY}" fill-opacity="0.45"/>')
out.append(f'<path d="{area(p, 100, 121, sx, sy)}" fill="{ORANGE}" fill-opacity="0.75"/>')
out.append(f'<path d="{path(p, 0, 160, sx, sy)}" fill="none" stroke="{BLUE}" stroke-width="2.5"/>')
for s0 in (100, 121):
    out.append(f'<line x1="{sx(s0):.1f}" y1="{sy(p(s0)):.1f}" x2="{sx(0):.1f}" y2="{sy(p(s0)):.1f}" '
               f'stroke="{INK}" stroke-dasharray="3,3"/>')
    out.append(f'<circle cx="{sx(s0):.1f}" cy="{sy(p(s0)):.1f}" r="4.5" fill="{VERM}"/>')
text(sx(100) - 6, sy(20) - 10, "p(100) = 20", 12, "end")
text(sx(121) + 9, sy(22) + 17, "p(121) = 22", 12, "start")
text(sx(48), sy(6.5), "reserve R(100)", 13, "middle", "bold")
text(sx(48), sy(5), "= 1,333.33 ETH", 13, "middle")
text(sx(48), sy(3.6), "area under the curve", 11, "middle")
out.append(f'<line x1="{sx(110.5):.1f}" y1="{sy(9):.1f}" x2="{sx(128):.1f}" y2="{sy(13.5):.1f}" stroke="{INK}"/>')
text(sx(129), sy(15.5), "buy 21 pETH:", 12, "start", "bold")
text(sx(129), sy(14), "R(121) − R(100)", 12, "start")
text(sx(129), sy(12.5), "= 441.33 ETH", 12, "start")

# Right panel: effect of beta
sx2, sy2 = panel(680, 50, 270, 330, 10, 10.5, [0, 2, 4, 6, 8, 10], [0, 2, 4, 6, 8, 10],
                 "supply s", "price p(s)", 'p(s) = s<tspan baseline-shift="super" font-size="10">β</tspan>  (α = 1)')
for beta, colour, dash, label, ly in ((1.0, VERM, "", "β = 1 (linear)", 10 ** 1.0),
                                      (0.5, BLUE, "8,5", "β = 0.5 (tests)", 10 ** 0.5),
                                      (0.15, GREEN, "2,4", "β = 0.15 (testnet)", 10 ** 0.15)):
    q = lambda s, b=beta: s ** b
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<path d="{path(q, 0, 10, sx2, sy2)}" fill="none" stroke="{colour}" stroke-width="2.5"{d}/>')
    text(sx2(10) - 4, sy2(ly) - 8, label, 12, "end", "bold", colour)
text(W / 2, H - 12, "Testnet β read on Sepolia on 22 October 2026; the left panel uses the prototype's test parameters.",
     11, "middle", fill="#555555")
out.append("</svg>")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "polaris-power-law-curve.svg"), "w") as fh:
    fh.write("\n".join(out))
