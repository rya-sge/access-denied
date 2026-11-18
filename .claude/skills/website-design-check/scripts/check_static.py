#!/usr/bin/env python3
"""Static design checks on the access-denied sources, no build needed.

Usage:
    python3 .claude/skills/website-design-check/scripts/check_static.py [--root DIR] [FILE.md ...]

With no FILE, checks every post in _posts/ and every .puml under assets/.
Run from the repository root, or pass --root. One PASS/FAIL/WARN line per check,
a summary line, exit code 1 on any FAIL. Read-only: it reports, it never fixes.

Checks
  puml-deprecated  FAIL  activity line `#color:text;` (PlantUML prints a yellow
                         "This syntax is deprecated" box inside the PNG)
  puml-png         WARN  .puml with no .png next to it, or a .png older than its .puml
  heading-nesting  FAIL  a `###` that follows "## What you need to know first" with no
                         `##` in between (the section swallows the article's sections)
  key-terms        FAIL  `### Key Terms` not directly under `## Annex`
  img-alt          FAIL  Markdown image with empty alt text `![](...)`
  bare-toc         WARN  `[TOC]` not alone on its line (the layout only replaces `<p>[TOC]</p>`)
  table-blank      FAIL  a table header row with no blank line before it (kramdown
                         then renders the table as text)
"""
import argparse
import glob
import os
import re
import sys

FENCE = re.compile(r'^(```|~~~)')
PUML_DEPRECATED = re.compile(r'^\s*#[A-Za-z0-9]+:.*;\s*$')
IMG_NO_ALT = re.compile(r'!\[\s*\]\(')


def strip_fences(lines):
    """Yield (lineno, line) outside fenced code blocks."""
    inside = False
    for i, line in enumerate(lines, 1):
        if FENCE.match(line.strip()):
            inside = not inside
            continue
        if not inside:
            yield i, line


def check_post(path):
    fails, warns = [], []
    text = open(path, encoding='utf-8').read()
    lines = text.split('\n')
    # Skip the front matter.
    body_start = 0
    if lines and lines[0].strip() == '---':
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                body_start = i + 1
                break
    body = lines[body_start:]
    numbered = [(n + body_start, l) for n, l in strip_fences(body)]

    # heading-nesting and key-terms
    last_h2 = None
    in_prereq = False
    for n, l in numbered:
        if l.startswith('## '):
            last_h2 = l[3:].strip()
            in_prereq = last_h2 == 'What you need to know first'
        elif l.startswith('### '):
            if in_prereq:
                fails.append(f'heading-nesting  line {n}: "{l.strip()}" sits under "What you need to know first"')
                in_prereq = False  # report once per section
            if l.strip() == '### Key Terms' and last_h2 != 'Annex':
                fails.append(f'key-terms        line {n}: Key Terms is under "## {last_h2}", not "## Annex"')

    # img-alt, bare-toc, table-blank
    prev = ''
    for n, l in numbered:
        if IMG_NO_ALT.search(l):
            fails.append(f'img-alt          line {n}: image without alt text')
        if '[TOC]' in l and l.strip() != '[TOC]':
            warns.append(f'bare-toc         line {n}: [TOC] shares its line with other text')
        if (l.lstrip().startswith('|') and re.match(r'^\s*\|?\s*:?-{3,}', next_line(numbered, n) or '')
                and prev.strip() and not prev.lstrip().startswith('|')):
            fails.append(f'table-blank      line {n}: table header with no blank line before it')
        prev = l
    return fails, warns


def next_line(numbered, n):
    for m, l in numbered:
        if m > n:
            return l
    return None


def check_puml(path):
    fails, warns = [], []
    for n, l in enumerate(open(path, encoding='utf-8').read().split('\n'), 1):
        if PUML_DEPRECATED.match(l):
            fails.append(f'puml-deprecated  line {n}: "{l.strip()}" -> write ":text; <<#color>>"')
    png = path[:-5] + '.png'
    if not os.path.exists(png):
        warns.append('puml-png         no rendered .png next to the source')
    elif os.path.getmtime(png) < os.path.getmtime(path):
        warns.append('puml-png         .png is older than its .puml: re-render it')
    return fails, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('files', nargs='*')
    a = ap.parse_args()
    root = a.root
    if not os.path.isdir(os.path.join(root, '_posts')):
        print(__doc__)
        sys.exit(f'FAIL no _posts/ under {os.path.abspath(root)}: run from the repository root or pass --root')

    if a.files:
        targets = a.files
    else:
        targets = sorted(glob.glob(os.path.join(root, '_posts', '*.md')))
        targets += sorted(glob.glob(os.path.join(root, 'assets', '**', '*.puml'), recursive=True))

    n_fail = n_warn = 0
    for t in targets:
        f, w = check_puml(t) if t.endswith('.puml') else check_post(t)
        rel = os.path.relpath(t, root)
        for m in f:
            print(f'FAIL {rel}: {m}')
        for m in w:
            print(f'WARN {rel}: {m}')
        n_fail += len(f)
        n_warn += len(w)
    print(f'SUMMARY files={len(targets)} fail={n_fail} warn={n_warn}')
    if n_fail == 0:
        print('PASS static design checks')
    sys.exit(1 if n_fail else 0)


if __name__ == '__main__':
    main()
