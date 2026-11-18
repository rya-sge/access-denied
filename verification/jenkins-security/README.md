# Jenkins security: advisory statistics

Reproduces the numbers in the section "What nine years of advisories say about plugins" of
`_posts/2026-11-17-jenkins-security.md`.

## What it tests

- The number of advisory files with a structured `issues:` list, and the number of issues.
- Issues per year, per severity, core-only versus plugin.
- Plugin issues for which no listed plugin has a `fixed:` version (announced without a fix).
- A multi-label classification of issue titles by keyword, and a fixed random sample of
  40 titles printed with their labels for a manual accuracy check.

## Input

The `content/security/advisory/` folder of
[jenkins-infra/jenkins.io](https://github.com/jenkins-infra/jenkins.io), commit
`39e4020b363558216017486859a0198b8be59e79` (2026-11-17). Advisories before 2017-11-08 are
free-form AsciiDoc without an `issues:` list and are not counted.

## Run

```bash
git clone https://github.com/jenkins-infra/jenkins.io
git -C jenkins.io checkout 39e4020b363558216017486859a0198b8be59e79
python3 -I advisory_stats.py jenkins.io/content/security/advisory
```

Needs Python 3 and PyYAML.

## Expected output (head)

```text
advisory files with issues: 147 | issues: 1541
first/last: 2017-11-08 2026-10-28
severity: Counter({'Medium': 870, 'High': 453, 'Low': 208, 'Critical': 10})
plugin issues: 1354 | core-only issues: 187
plugin issues with no fixed version at publication: 518
```

## Limits

Titles are matched, not descriptions. One issue can match several classes (205 do) or none
(205 do). In the 40-title sample every assigned label matched the title, and the two titles
without a label belonged to none of the classes; this checks precision on a small sample only,
not recall.
