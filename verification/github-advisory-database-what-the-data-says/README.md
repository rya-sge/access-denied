# GitHub Advisory Database counts

Reproduces every count quoted in the article `github-advisory-database-what-the-data-says`.

- Input: a checkout of `github/advisory-database` at commit `b6d0ec57e5561f66c3121af72e24871d1d7f2902` (2026-11-04).
- Run: `python3 -I analyse.py <path to the checkout> > results.json`
- Output: `results.json`, as used in the article and in the figure.

A later commit gives different counts, because the database is edited every day.

The "linked to a repository advisory" count is a proxy: it looks for a reference URL of the form `github.com/<owner>/<repo>/security/advisories/GHSA-...`.
