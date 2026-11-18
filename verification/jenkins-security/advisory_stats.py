"""Count and classify Jenkins security advisory issues.

Usage: python3 -I advisory_stats.py <path to jenkins.io/content/security/advisory>

Reads the YAML front matter of every advisory file, keeps the files that carry a
structured `issues:` list (2017-11-08 onwards), and prints:
  - the number of files and issues, issues per year, severity counts;
  - core-only issues (no `plugins:` list) versus plugin issues;
  - plugin issues where no listed plugin has a `fixed:` version (no fix at publication);
  - a multi-label classification of issue titles by keyword (one issue may match several
    classes, or none);
  - a fixed random sample of 40 titles with their labels, for a manual accuracy check.
"""
import collections, glob, os, random, re, sys
import yaml

D = sys.argv[1]
rows = []
for f in sorted(glob.glob(os.path.join(D, '*.adoc'))):
    src = open(f, encoding='utf-8').read()
    if not src.startswith('---'):
        continue
    d = yaml.safe_load(src.split('---', 2)[1]) or {}
    for i in d.get('issues') or []:
        plugins = [p for p in (i.get('plugins') or []) if isinstance(p, dict)]
        cvss = i.get('cvss') if isinstance(i.get('cvss'), dict) else {}
        rows.append(dict(date=os.path.basename(f)[:10], id=i.get('id'), title=i.get('title') or '',
                         sev=(cvss.get('severity') or 'none').capitalize(),
                         plugins=[p.get('name') for p in plugins],
                         fixed=[p.get('fixed') for p in plugins]))

N = len(rows)
print('advisory files with issues:', len(set(r['date'] for r in rows)), '| issues:', N)
print('first/last:', min(r['date'] for r in rows), max(r['date'] for r in rows))
print('per year:', sorted(collections.Counter(r['date'][:4] for r in rows).items()))
print('severity:', collections.Counter(r['sev'] for r in rows))
plug = [r for r in rows if r['plugins']]
print('plugin issues:', len(plug), '| core-only issues:', N - len(plug))
nofix = [r for r in plug if all(x is None for x in r['fixed'])]
print('plugin issues with no fixed version at publication:', len(nofix))
print('distinct plugins named:', len(set(p for r in plug for p in r['plugins'])))

C = [
    ('XSS', r'\bxss\b|cross-site scripting'),
    ('CSRF', r'\bcsrf\b|cross-site request forgery'),
    ('Missing or incorrect permission check', r'permission check|enumerat\w* credential|improper access control|authorization|missing permission|incorrect permission|lack of permission|without permission|access control'),
    ('Secrets stored or shown in plain text', r'stor\w* .*(credential|password|token|secret|key)|(credential|password|token|secret|key)s? (stored|displayed|transmitted|shown)|plain ?text|unencrypted|mask|redact|sensitive|written to the build log|printed .*log|ineffective credentials encryption|exposure of (credential|secret|password|token|api)'),
    ('XXE', r'\bxxe\b|xml external entit'),
    ('Path traversal / arbitrary file read or write', r'path traversal|arbitrary file|directory traversal|zip slip'),
    ('Sandbox bypass', r'sandbox|classpath approval|script approval'),
    ('SSRF', r'\bssrf\b|server-side request forgery'),
    ('TLS/SSH validation disabled', r'certificate validation|hostname (validation|verification)|host key verification|tls|ssl'),
    ('Agent-to-controller bypass', r'agent-to-controller|agent to controller'),
    ('Unsafe deserialization / RCE', r'deserializ|\brce\b|remote code execution|code execution'),
    ('Session fixation / open redirect / timing', r'session fixation|open redirect|constant time|non-constant'),
]
cnt, sev, multi, none = collections.Counter(), collections.defaultdict(collections.Counter), 0, 0
for r in rows:
    hit = [n for n, p in C if re.search(p, r['title'].lower())]
    multi += len(hit) > 1
    none += not hit
    for h in hit:
        cnt[h] += 1
        sev[h][r['sev']] += 1
for n, _ in C:
    print(f'{cnt[n]:4d}  {n}  {dict(sev[n])}')
print('issues with several labels:', multi, '| with no label:', none)

random.seed(7)
for r in random.sample(rows, 40):
    print('  sample:', [n for n, p in C if re.search(p, r['title'].lower())], '|', r['title'])
