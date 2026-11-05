"""GitHub-reviewed advisories per year, by published date and by review date. Run: python3 -I <this file>"""
import json
import os
import sys

sys.path.insert(0, os.path.expanduser("~/.claude/skills/create-plot"))
import plotstyle as ps  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(
    HERE, "../../../../verification/github-advisory-database-what-the-data-says/results.json")))
years = [str(y) for y in range(2017, 2027)]
pub = [data["published_by_year"].get(y, 0) for y in years]
rev = [data["reviewed_by_year"].get(y, 0) for y in years]

ps.apply()
fig, ax = ps.figure()
xs = list(range(len(years)))
c0, _, _ = ps.style(0)
c1, _, _ = ps.style(1)
ax.bar([x - 0.2 for x in xs], pub, 0.4, color=c0, label="By published date")
ax.bar([x + 0.2 for x in xs], rev, 0.4, color=c1, hatch="///", edgecolor="black", linewidth=0.5,
       label="By GitHub review date")
ax.set_xticks(xs, [y if y != "2026" else "2026\n(to 4 Nov)" for y in years])
ax.set(ylabel="Advisories (not withdrawn)", title="GitHub-reviewed advisories per year")
ax.legend(frameon=False, loc="upper left")
ax.annotate("2022: 8,656, of which\n4,968 in May alone", xy=(5 - 0.2, 8656), xytext=(2.6, 9300),
            arrowprops=dict(arrowstyle="-", lw=0.7), fontsize=9)
ax.annotate("11,618", xy=(9 - 0.2, 11618), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
ps.caption(fig, "Snapshot of 2026-11-04. The two series count the same 36,266 advisories.")
ps.save(fig, __file__)
