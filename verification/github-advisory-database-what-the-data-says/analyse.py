#!/usr/bin/env python3
"""Counts quoted in the article. Usage: python3 -I analyse.py <path to github/advisory-database>

Standard library only. Prints JSON. "live" means not withdrawn.
"""
import collections
import glob
import json
import os
import re
import sys

root = sys.argv[1]
REPO_ADV = re.compile(r"github\.com/([^/]+/[^/]+)/security/advisories/GHSA", re.I)


def load(scope):
    for path in glob.iglob(os.path.join(root, "advisories", scope, "**", "*.json"), recursive=True):
        with open(path, encoding="utf-8") as handle:
            yield json.load(handle)


def repo_of(adv):
    for ref in adv.get("references", []):
        match = REPO_ADV.search(ref["url"])
        if match:
            return match.group(1).lower()
    return None


reviewed = list(load("github-reviewed"))
live = [a for a in reviewed if not a.get("withdrawn")]
gone = [a for a in reviewed if a.get("withdrawn")]
out = {"reviewed_files": len(reviewed), "live": len(live), "withdrawn": len(gone)}

published = collections.Counter(a["published"][:4] for a in live)
review_year = collections.Counter(a["database_specific"]["github_reviewed_at"][:4] for a in live)
linked = collections.Counter(a["published"][:4] for a in live if repo_of(a))
out["published_by_year"] = dict(sorted(published.items()))
out["reviewed_by_year"] = dict(sorted(review_year.items()))
out["repo_linked_by_year"] = dict(sorted(linked.items()))

months = collections.Counter(a["published"][:7] for a in live)
out["jan_oct_2025"] = sum(v for k, v in months.items() if "2025-01" <= k <= "2025-10")
out["jan_oct_2026"] = sum(v for k, v in months.items() if "2026-01" <= k <= "2026-10")
out["may_2022"] = months["2022-05"]

for year in ("2025", "2026"):
    cohort = [a for a in live if a["published"].startswith(year)]
    repos = collections.Counter(repo_of(a) for a in cohort if repo_of(a))
    sev = collections.Counter(a["database_specific"]["severity"] for a in cohort)
    cve_year = collections.Counter(
        next((x[4:8] for x in a["aliases"] if x.startswith("CVE-")), "none") for a in cohort)
    out[f"cohort_{year}"] = {
        "advisories": len(cohort), "repositories": len(repos), "top_repositories": repos.most_common(5),
        "severity": dict(sev), "same_year_cve": cve_year[year], "no_cve": cve_year["none"],
        "no_nvd_date": sum(1 for a in cohort if not a["database_specific"]["nvd_published_at"])}

may = [a for a in live if a["published"].startswith("2022-05")]
out["may_2022_cve_before_2022"] = sum(
    1 for a in may if any(x.startswith("CVE-") and x[4:8] < "2022" for x in a["aliases"]))
out["may_2022_reviewed_in_may_2022"] = sum(
    1 for a in may if a["database_specific"]["github_reviewed_at"].startswith("2022-05"))

shapes = collections.Counter()
for adv in live:
    for entry in adv["affected"]:
        ranges = entry.get("ranges", [])
        if not ranges:
            shapes["versions_only"] += 1
        for rng in ranges:
            kinds = {k for event in rng["events"] for k in event}
            shapes["fixed" if "fixed" in kinds else "last_affected" if "last_affected" in kinds
                   else "open_ended"] += 1
        if entry.get("database_specific", {}).get("last_known_affected_version_range"):
            shapes["with_last_known_bound"] += 1
out["range_shapes"] = dict(shapes)
out["advisories_without_fixed_event"] = sum(
    1 for a in live
    if not any("fixed" in e for x in a["affected"] for r in x.get("ranges", []) for e in r["events"]))
out["advisories_multi_package"] = sum(1 for a in live if len(a["affected"]) > 1)
out["advisories_multi_ecosystem"] = sum(
    1 for a in live if len({x["package"]["ecosystem"] for x in a["affected"]}) > 1)
out["max_affected_entries"] = max(len(a["affected"]) for a in live)

types = [{s["type"] for s in a["severity"]} for a in live]
out["cvss"] = {"v3": sum("CVSS_V3" in t for t in types), "v4": sum("CVSS_V4" in t for t in types),
               "both": sum(len(t) == 2 for t in types), "none": sum(not t for t in types)}
out["severity"] = dict(collections.Counter(a["database_specific"]["severity"] for a in live))
out["no_cve_alias"] = sum(1 for a in live if not a["aliases"])
out["no_cwe"] = sum(1 for a in live if not a["database_specific"]["cwe_ids"])
out["top_cwe"] = collections.Counter(
    c for a in live for c in a["database_specific"]["cwe_ids"]).most_common(6)
out["ecosystems"] = collections.Counter(
    e for a in live for e in {x["package"]["ecosystem"] for x in a["affected"]}).most_common()

out["withdrawn_by_year"] = dict(sorted(collections.Counter(a["withdrawn"][:4] for a in gone).items()))
out["withdrawn_titled_duplicate"] = sum(1 for a in gone if a["summary"].startswith("Duplicate Advisory"))
out["withdrawn_with_cve"] = sum(1 for a in gone if a["aliases"])

unreviewed = collections.Counter()
for adv in load("unreviewed"):
    unreviewed["files"] += 1
    unreviewed["with_ecosystem"] += any(x.get("package", {}).get("ecosystem") for x in adv["affected"])
    unreviewed["withdrawn"] += bool(adv.get("withdrawn"))
    unreviewed["no_severity_label"] += adv["database_specific"].get("severity") is None
    unreviewed[adv["published"][:4]] += 1
out["unreviewed"] = dict(sorted(unreviewed.items()))
print(json.dumps(out, indent=1))
