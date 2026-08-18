# Content Audit — 10 most recent articles

**Date:** 2026-07-31
**Scope:** the 10 newest posts in `_posts/` (2026-07-24 → 2026-07-31), checked against the
`create-article` skill's rules. Three findings outside that window are recorded in §4 because
they are visible on the published site.

Every item below was verified against the repository and, where the failure is visual, against
the rendered PNG. Nothing here is inferred from source alone.

**Articles audited**

| # | Article | `isMath` |
|---|---------|:---:|
| 1 | `2026-07-24-zero-knowledge-proofs-zama-protocol.md` | true |
| 2 | `2026-07-28-conditional-tokens-eli10.md` | true |
| 3 | `2026-07-28-gnosis-conditional-tokens-framework.md` | true |
| 4 | `2026-07-28-medusa-smart-contract-fuzzer.md` | false |
| 5 | `2026-07-28-zk-proof-systems-15-concepts-15-formulas.md` | true |
| 6 | `2026-07-30-alchemy-smart-wallet-account-abstraction.md` | false |
| 7 | `2026-07-30-rundler-alchemy-erc4337-bundler.md` | false |
| 8 | `2026-07-31-coldcard-firmware-security.md` | false |
| 9 | `2026-07-31-cross-chain-bridge-hacks.md` | false |
| 10 | `2026-07-31-cross-chain-bridge-threat-model.md` | false |

---

## 0. Summary

| Check | Result |
|-------|--------|
| Images referenced vs. present on disk | ✅ 10/10, 55 refs, 0 missing |
| Required sections (TOC, FAQ ≥ 5 Q, References, frontmatter `image:`) | ✅ 10/10 |
| PlantUML source leaked into an article | ✅ none |
| MathJax hazards inside `$$…$$` | ✅ clean after §1.2 |
| Unbalanced `$` under `isMath: true` | ✅ clean |
| Table glued to a heading | ✅ none |
| Invented / guessed URLs | ✅ none |
| Local filesystem paths as link targets | ✅ none |
| `tree.txt` registration | ⚠️ 1 gap — fixed in §1.1 |
| Category keys | ✅ valid (see §3.1 — the skill's list was stale, not the article) |
| Mid-sentence em dash budget | ❌ 2 articles far over — §2.1, **open** |

**The 10 articles are in good shape.** Two defects were found and fixed; one style issue is
left open because it needs a decision. The most consequential findings in this audit are
actually in §4 (published diagrams carrying a visible error banner) and §3 (tooling that was
producing wrong answers).

---

## 1. Fixed

### 1.1 `cross-chain-bridge-hacks` was missing from `tree.txt`

**Status:** ✅ fixed.

`_posts/2026-07-31-cross-chain-bridge-hacks.md` had no entry in the PlantUML registry, while its
sibling `-threat-model.md` did. All four `.puml` sources existed on disk and were correctly
rendered; only the registry line was absent.

That is precisely the failure `tree.txt` exists to prevent: whoever next edits a diagram in that
article would have had no pointer to the source and would have had to reverse-engineer it from
the PNG. Entry added:

```
_posts/2026-07-31-cross-chain-bridge-hacks.md
  assets/article/blockchain/2026-07-31-cross-chain-bridge-hacks-mindmap.puml                (mindmap)
  assets/article/blockchain/2026-07-31-cross-chain-bridge-lock-unlock-concept.puml          (concept, in-section)
  assets/article/blockchain/2026-07-31-ronin-2024-uninitialized-weight-workflow.puml        (workflow, in-section)
  assets/article/blockchain/2026-07-31-kelp-dao-rpc-poisoning-workflow.puml                 (workflow, in-section)
```

**Worth a sweep — but not a naive one.** A first attempt simply checked every post for a `tree.txt`
line and reported 170+ "unregistered" articles, which is noise: most older posts have no PlantUML
diagram at all, so they correctly have no entry. The useful test is narrower — an article that
**embeds a PNG which has a sibling `.puml` on disk** but has no registry line:

```bash
cd ~/Downloads/me/access-denied
python3 -c "
import re,glob,os
reg=open('tree.txt',errors='ignore').read()
for fn in sorted(glob.glob('_posts/*.md')):
    src=open(fn,errors='ignore').read()
    pngs=set(re.findall(r'(assets/article/[A-Za-z0-9/._-]+\.png)', src))
    pumls=[p for p in pngs if os.path.isfile(p[:-4]+'.puml')]
    if pumls and ('_posts/'+os.path.basename(fn)) not in reg:
        print('%-70s %d puml' % (os.path.basename(fn), len(pumls)))"
```

That reports **46 articles**, all with a single diagram each, spanning 2021 → 2026-01. See §4.3:
they are a legacy backlog, not new breakage.

### 1.2 Raw `>` inside a `$$` block (Gnosis CTF article)

**Status:** ✅ fixed. **Severity:** low (conformance, not a live break).

`_posts/2026-07-28-gnosis-conditional-tokens-framework.md` line ~74:

```
d = \sum_{j=0}^{k-1} n_j, \qquad d > 0     ->   d \gt 0
```

The `create-article` skill lists raw `<` / `>` in math as a hazard and mandates `\lt` / `\gt`.
In this specific case it renders correctly today, because kramdown escapes the `>` to `&gt;` and
MathJax reads `textContent`, which decodes it back. It was corrected anyway: the article carries
`isMath: true`, the fix is one character, and relying on that escape-then-decode round trip is
not worth the ambiguity.

---

## 2. Open — needs a decision

### 2.1 Mid-sentence em dash budget exceeded on two articles

**Status:** ❌ open. **Severity:** style, systematic.

The skill allows **one** mid-sentence em dash (` — `) per article body, with headings, table
cells and reference-list labels exempt. Two articles are far past it:

| Article | Genuine prose ` — ` occurrences |
|---------|:---:|
| `2026-07-30-alchemy-smart-wallet-account-abstraction.md` | ~36 |
| `2026-07-30-rundler-alchemy-erc4337-bundler.md` | ~43 |

Counted after excluding frontmatter, the credit note, headings, table rows, reference bullets and
definition-style bullets (`` - `nonce` — the user-operation nonce… ``). Representative cases:

> The fallback supports exactly what `SingleSignerValidationModule` supports — secp256k1 ECDSA for an EOA owner…

> Initializer functions on the other variants are not access-controlled — they rely on the proxy pattern's one-shot initialization for safety.

Both are the parenthetical use the rule targets, and both rewrite cleanly to a comma, parentheses
or a subordinate clause.

**Why it is still open:** roughly 79 individual prose rewrites across two long articles. That is a
large unrequested edit to published text, and the articles read well as they stand. Options:

- **(a)** Bring both to the budget of one — faithful to the rule, ~79 edits, some risk of flattening rhythm.
- **(b)** Reduce to a handful of the strongest cases and leave the rest.
- **(c)** Leave as-is and treat the budget as advisory for long reference articles.

A useful diagnostic to re-run after any decision:

```bash
python3 -c "
import re,sys
for fn in sys.argv[1:]:
    L=open(fn).read().split(chr(10)); ic=False; hits=[]
    for i,l in enumerate(L,1):
        if l.startswith('\`\`\`'): ic=not ic; continue
        if ic or i<14: continue
        if l.startswith('#') or l.startswith('|') or l.startswith('>'): continue
        if re.match(r'^\s*-\s*\[', l): continue
        s=re.sub(r'^\s*-\s+\**\`?[A-Za-z0-9_.\`]+\`?\**\s+—\s+','',l)
        if ' — ' in s: hits.append(i)
    print('%s: %d  %s' % (fn.split('/')[-1], len(hits), hits[:15]))" _posts/<article>.md
```

---

## 3. Tooling defects this audit exposed

Three checks reported problems that were not problems. Each was a defect in the check, and each
is now fixed in `~/.claude/skills/create-article/SKILL.md`. Recording them here because a check
that cries wolf gets ignored, and because two of them would have caused a *correct* article to be
"fixed" into a broken one.

### 3.1 The canonical category list was stale — `eli10` is legitimate

`2026-07-28-conditional-tokens-eli10.md` uses `categories: blockchain defi eli10`, which the
skill's canonical key list rejected. The article is right and the list was wrong: `_pages/category/eli10`
exists and 8 posts use the key.

Keys genuinely in use but absent from the skill's list: **`eli10`** (8 posts), **`rfc`** (3),
**`finance`** (2), **`oracle`** (1).

Fixed in the skill by adding the four keys, noting that `eli10` is **additive** (an ELI10 article
carries its topic categories *and* `eli10`), and replacing blind trust in the list with a command
that derives the live set:

```bash
grep -h '^categories:' _posts/*.md | sed 's/^categories:[[:space:]]*//' | tr ' ' '\n' | sort | uniq -c | sort -rn
ls _pages/category/
```

### 3.2 The link scanner did not strip code

The "no local filesystem paths" scanner added earlier flagged
`new uint[](outcomeSlotCount)` — Solidity inside a fenced block, matched because `](` looks like
a Markdown link. Inline code spans such as `` `arr[i](x)` `` fail the same way. The skill's
scanner now strips fenced blocks and inline code spans before matching, and says why.

### 3.3 A line-based `$` counter cannot see code spans

The unbalanced-`$` check flagged the Gnosis article twice on `` `$:(B|C)` `` — Gnosis CTF position
notation, where `$` denotes collateral, inside a code span. MathJax's default `skipHtmlTags`
includes `code`, so these are inert.

**The rule that resolves most `$` questions:** `isMath` decides. `2026-07-31-cross-chain-bridge-hacks.md`
carries 14 bare amounts (`~$540M`, `~$34B`, `$433M`) and is completely fine, because it sets
`isMath: false` and `_layouts/default.html:44` only loads MathJax when `page.isMath` is truthy.
The `$540$M escaping convention is **only** required when `isMath: true`.

---

## 4. Outside the 10 — but live on the site

### 4.1 Three published diagrams carry a PlantUML deprecation banner

**Severity:** high-visibility, low-effort. **Status:** open.

13 lines across 3 `.puml` files still use the deprecated `#RRGGBB:label;` colour prefix. On
PlantUML 1.2026 this does two bad things at once: it **silently drops the colour**, and it
**stamps a yellow warning banner into the PNG**, which is then published. Verified by opening the
committed PNGs — the banner is there now, and the "Access granted" / "Access denied" boxes render
plain white instead of green / red.

| `.puml` file | Bad lines | Article |
|--------------|:---:|---------|
| `assets/article/securite/linux-base-security/posix-permission-resolution-workflow.puml` | 6 | `2026-06-29-linux-base-security-primitives.md` |
| `assets/article/securite/linux-advanced-security/seccomp-bpf-filter-workflow.puml` | 4 | `2026-06-29-linux-advanced-security-seccomp-lsm.md` |
| `assets/article/blockchain/stellar/sep41-path-decision.puml` | 3 | `2026-07-09-stellar-fungible-token-openzeppelin-sep41.md` |

Banner text currently shipping to readers:

```
This syntax is deprecated, you must add <<#90ee90>> at the end of the line, after the ';'
This syntax is deprecated, you must add <<#ff9999>> at the end of the line, after the ';'
```

Fix: move the colour after the closing `;`, then re-render and **look at the PNG** (`plantuml`
exits 0 on this warning, so the exit code proves nothing).

```
#90ee90:Access granted;          <-- deprecated: colour dropped + banner
:Access granted;<<#90ee90>>      <-- correct
```

Repo-wide detector (anchored to line start, so a valid mid-line colour such as
`note over A, B #F3EEFB: text` is not a false positive):

```bash
python3 -c "
import glob,re
for f in sorted(glob.glob('assets/**/*.puml',recursive=True)):
    for i,l in enumerate(open(f,errors='ignore'),1):
        if re.match(r'\s*#[0-9A-Fa-f]{6}\s*:', l): print(f,i,l.rstrip())"
```

### 4.2 Two posts have an empty `categories:` field

**Severity:** low. **Status:** open.

They appear in **no** category listing and are reachable only from the index. Silent breakage:
nothing errors, and the build looks clean.

| Post | Suggested keys |
|------|----------------|
| `2025-05-30-credit-default-swap-overview.md` | `finance` |
| `2025-09-01-ai-bot-crawler.md` | `ai web` |

`2024-03-28-ethereum-stacking.md` is also empty but carries `exclude: yes`, so it is deliberate
and needs no change.

The skill now carries an explicit "never leave `categories:` empty" rule. Detector:

```bash
python3 -c "
import re,glob
for fn in sorted(glob.glob('_posts/*.md')):
    src=open(fn,errors='ignore').read()
    m=re.search(r'^categories:[ \t]*([^\n]*)$', src, re.M)
    if m and not m.group(1).split() and 'exclude: yes' not in src:
        print('EMPTY:', fn)"
```

### 4.3 46 legacy articles have a diagram but no `tree.txt` entry

**Severity:** low, maintenance debt. **Status:** open.

Running the narrowed detector from §1.1 across the repo returns 46 articles that embed a
`.puml`-backed PNG without a registry line, each with exactly one diagram, dated 2021 through
2026-01. Examples: `2024-10-23-ecdsa-overview.md`, `2024-11-4-TLS1.3-overview.md`,
`2025-09-27-seal-overview.md`, `2026-01-13-claude-code-security.md`.

**This is a different problem from §1.1.** Those 46 predate the registry convention; the
`.puml` files sit next to their PNGs under a predictable name, so the source is findable even
without an entry. `cross-chain-bridge-hacks` was a *new* article written under the convention
that was simply missed, which is the case worth preventing.

Backfilling is mechanical (each entry is one line, `(mindmap)`, derived from the sibling `.puml`
path) and could be scripted in one pass. Low urgency; the value is uniformity, so that a future
"is it registered?" check gives a clean signal instead of 46 known exceptions.

---

## 5. Recommended order

1. **§4.1 — deprecation banners.** Highest reader-visible impact for the least work: 13 lines, 3 files, re-render, eyeball the PNGs.
2. **§4.2 — empty categories.** Two one-line frontmatter edits.
3. **§2.1 — em dash budget.** Needs a decision between (a), (b) and (c) before any editing.
4. **§4.3 — backfill the 46 legacy registry entries.** Scriptable, low urgency, do it when convenient.

§1.1, §1.2 and all of §3 are already done.
