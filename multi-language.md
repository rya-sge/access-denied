# Multi-language (EN / FR) — Feasibility Analysis

**Date:** 2026-07-30
**Scope:** adding a French version of `access-denied` and translating the English articles.

---

## 1. Verdict

**Yes, this is feasible — and the site is already half-prepared for it.** `_layouts/default.html` already
branches on `page.lang`, and 208 of 255 posts already carry `lang:` / `locale:` front matter. What is
missing is not metadata, it is *language separation*: today every listing on the site (home, categories,
tags, search, related posts) mixes French and English articles indiscriminately.

Two things dominate the decision, and they are very different in nature:

| | Difficulty | Cost |
|---|---|---|
| **Site plumbing** (routing, filtering, SEO, UI strings) | Low–medium, ~1–2 days of work | Bounded and one-off |
| **Translating 209 English articles** | Mechanically easy, editorially expensive | ~409'000 words; the ongoing 2× maintenance burden is the real cost |

The plumbing is not the risk. The risk is committing to maintaining every future article in two languages.

---

## 2. Current state — audit

### 2.1 Content inventory

Measured over `_posts/` (255 files, 3.83 MiB):

| Metric | Value |
|---|---|
| Total posts | 255 |
| Detected **English** posts | **209** (~409'000 words) |
| Detected **French** posts | **48** (~32'000 words) — nearly all from 2021–2022 |
| Posts with `lang:` front matter | 208 (`lang: en` × 207) |
| Posts with `locale:` front matter | 214 (`en-GB` × 207, `fr-FR` × 6) |
| Posts with **no** `lang:` | 49 — these are almost exactly the legacy French posts |
| Average English post | ~1'955 words |
| Median post file | 12.5 KiB (largest: 93 KiB) |
| Categories in use | 20 (`blockchain` 120, `security` 66, `cryptography` 58, `ethereum` 48, …) |
| Static assets | 68 MiB under `assets/` |

Practical reading: the blog **started French (2021–2022) and switched to English**. There is one
front-matter inconsistency to fix (`_posts/2024-09-09-suisse-crypto-fiscalite.md` has a malformed
`lang:` line).

### 2.2 What already works in our favour

- `_layouts/default.html` already emits `<html lang="en">` / `<html lang="fr">` from `page.lang`.
- Front matter is uniform: every post has `title`, `date`, `categories`, `tags`, `description`, `image`.
- `assets/article/**` is **language-agnostic** — screenshots and diagrams are shared, so translating
  costs **zero extra disk** for the 68 MiB of assets.
- The theme is small (4 layouts, ~11 includes, 1 JS file). Surface area to change is genuinely small.

### 2.3 What is broken today (independently of this project)

- `_config.yml` declares `lang: "fr_FR"` for a site that is **82% English**. Wrong signal to search engines.
- **No listing filters by language.** `index.html`, `tags.html`, `_layouts/category-page.html`,
  `_pages/category/*/index.html`, `search.json` and `site.related_posts` all iterate over `site.posts`
  unconditionally. A visitor on the home page currently sees French 2021 posts interleaved with
  English 2026 posts.
- `<link rel="canonical">` in `_includes/head.html` is commented out.
- `js/main.js` hardcodes `/access-denied/search.json` and `/access-denied/page/N`.

**A language split fixes the mixed-listing problem as a side effect.** That is real value even before any
article is translated.

---

## 3. Hard constraints (read this before choosing an approach)

### 3.1 GitHub Pages classic build — no custom plugins

There is **no `.github/` directory** and no CI workflow. The site is built by GitHub Pages' classic
pipeline, which runs Jekyll in **safe mode**. Consequences:

1. **`_plugins/category-generator.rb` never runs in production.** It is dead code on GitHub Pages —
   which is exactly why the 19 hand-written `_pages/category/*/index.html` files exist. Don't rely on it.
2. **`jekyll-polyglot` and `jekyll-multiple-languages-plugin` cannot be used.** They are not on the
   GitHub Pages plugin whitelist. This rules out the two "standard" Jekyll i18n solutions.
3. **`jekyll-paginate-v2` is likewise unavailable.**

The four plugins in `_config.yml` (`jekyll-paginate`, `jekyll-feed`, `jekyll-seo-tag`, `jekyll-sitemap`)
are all whitelisted, so the current setup is fine — but it is a ceiling.

**Escape hatch:** adding a GitHub Actions workflow that runs `bundle exec jekyll build` and publishes
`_site/` removes all three restrictions at once. That is ~30 lines of YAML and would also make the
category generator plugin actually work. **This is a genuinely attractive side-benefit and worth doing
regardless of the language decision.**

### 3.2 Pagination is single-index only

`jekyll-paginate` (v1) paginates one index. A second paginated index at `/fr/` is not supported.
Mitigations: (a) leave the French index unpaginated (fine at 20–50 articles), (b) move to
`jekyll-paginate-v2` via the Actions workflow above. Note that `index.html` already only uses the
paginator for `total_pages` — the actual listing uses `site.posts limit/offset` plus a client-side
"Load more" that fetches `/page/N`. So the coupling is looser than it looks.

### 3.3 URL stability is non-negotiable

The 209 English articles are indexed by search engines at `/:year/:month/:day/:title/`. **They must not
move.** Any scheme that relocates existing English URLs will cost accumulated SEO. The 48 legacy French
posts are also at root URLs — moving those to `/fr/` needs redirects (`jekyll-redirect-from` *is*
whitelisted on GitHub Pages).

---

## 4. Architecture options

### Option A — `lang` front matter + `/fr/` prefix, pure Liquid *(recommended)*

English stays at the root; French lives under `/fr/`. Filtering is done with Liquid `where` filters. No
plugins needed, works on GitHub Pages today.

```
_posts/                       lang: en  →  /2026/07/30/alchemy-smart-wallet/
_posts/fr/                    lang: fr  →  /fr/2026/07/30/alchemy-smart-wallet/
```

- ✅ Works on the current build pipeline, no new dependencies
- ✅ Existing English URLs untouched
- ✅ Incremental — ship the plumbing first, translate at your own pace
- ⚠️ Every listing template must be edited to add a `where: "lang", …` filter
- ⚠️ Legacy French posts need redirects when moved under `/fr/`

### Option B — `jekyll-polyglot` + GitHub Actions

The conventional Jekyll i18n solution: `_i18n/<lang>/` trees, automatic `/fr/` URL generation, automatic
`hreflang`, a `{% t %}` translation tag.

- ✅ Far less hand-written Liquid; handles the tedious parts for you
- ✅ Unlocks `jekyll-paginate-v2` and the category plugin at the same time
- ❌ Requires abandoning the classic GitHub Pages build (new failure mode: builds can now break)
- ❌ Polyglot's site-wide `site.posts` rewriting has surprised people; it is a bigger conceptual change
- ❌ Restructures the whole `_posts/` tree in one go — riskier for a 255-post archive

### Option C — separate French site / repository

- ✅ Zero risk to the existing site
- ❌ Duplicates 68 MiB of assets and the entire theme; two things to maintain forever
- ❌ Cross-linking and `hreflang` become manual
- ❌ Not recommended

**Recommendation: Option A**, with the Actions workflow from §3.1 adopted separately as an independent
improvement. Option A is reversible; Option B is not, and its main benefit (less Liquid) is small
relative to a one-off day of template edits.

---

## 5. Implementation plan (Option A)

### 5.1 Front matter contract

Add two fields to every post:

```yaml
lang: en            # en | fr  — required, no exceptions
ref: alchemy-smart-wallet-account-abstraction   # stable translation key, identical across languages
```

`ref` is what pairs a translation to its original. It must survive title changes, so derive it from the
original English slug and then freeze it.

Backfill script (one-off): set `lang: fr` on the 49 posts that lack it, fix the malformed `lang:` line in
`2024-09-09-suisse-crypto-fiscalite.md`, and set `ref:` to the filename slug everywhere.

### 5.2 `_config.yml`

```yaml
lang: "en"                     # fix: site is 82% English
languages: ["en", "fr"]
default_lang: "en"

defaults:
  - scope: { path: "_posts", type: "posts" }
    values: { lang: "en" }
  - scope: { path: "_posts/fr", type: "posts" }
    values:
      lang: "fr"
      permalink: "/fr/:year/:month/:day/:title/"
```

⚠️ **Verify with a local `bundle exec jekyll build`** that posts in `_posts/fr/` are picked up and that
the subdirectory does not leak into `categories`. If it does, the fallback is a per-file explicit
`permalink:` (mechanical, script-generated).

### 5.3 UI strings → `_data/i18n.yml`

Hardcoded English strings live in `index.html`, `_layouts/post.html`, `_layouts/category-page.html`,
`_includes/header.html`, `_includes/categories.html` and `tags.html`:

`"Type to search..."`, `"Load more posts"`, `"You might also enjoy"`, `"minute read"`, `"View all"`,
`"Posts"`, `"Categories"`, `"Share button"`, `"Feel free to contact me on"`, `"No results found"`,
`"Tags in Blog"`, `"Search for Blog"`.

```yaml
# _data/i18n.yml
en:
  search_placeholder: "Type to search..."
  load_more: "Load more posts"
  related: "You might also enjoy"
  read_time: " minute read"
fr:
  search_placeholder: "Rechercher…"
  load_more: "Voir plus d'articles"
  related: "Vous aimerez aussi"
  read_time: " min de lecture"
```

Usage: `{% assign t = site.data.i18n[page.lang] | default: site.data.i18n.en %}` then `{{ t.load_more }}`.

Also localise dates: `'%Y, %b %d'` renders English month abbreviations. French needs a `_data/i18n.yml`
month table or a `date: '%d/%m/%Y'` numeric format.

### 5.4 Files to modify

| File | Change |
|---|---|
| `_config.yml` | `lang`, `languages`, `defaults` block |
| `index.html` | filter `site.posts | where: "lang", "en"`; use `t.*` strings |
| **`fr/index.html`** *(new)* | French home, `where: "lang", "fr"`, `permalink: /fr/` |
| `_layouts/default.html` | already correct — verify `page.lang` reaches it on all page types |
| `_includes/head.html` | uncomment canonical; add `hreflang` alternates (§5.5); `og:locale` |
| `_includes/header.html` | `t.*` strings; add the language switcher |
| `_includes/categories.html` | filter category counts by `page.lang` |
| `_layouts/category-page.html` | filter by `page.lang` |
| `_layouts/post.html` | `t.*` strings; **replace `site.related_posts`** (not language-aware) with a same-language `where` filter; add "also available in French" link via `ref` |
| `_pages/category/*/index.html` | 19 files — filter by lang; **plus 19 new French counterparts** under `_pages/fr/category/` |
| `tags.html` | filter by lang; add `/fr/tags/` |
| `search.json` | add `"lang"` field, or emit `search-en.json` / `search-fr.json` |
| `js/main.js` | pick the search index and the `/page/N` base from a `data-lang` attribute instead of hardcoding |
| `_includes/toc.html` | check for hardcoded English headings |

The 19 category pages are the bulk of the mechanical work — they are near-identical copies, so generate
them with a script rather than by hand.

### 5.5 Language switcher and `hreflang`

Pairing by `ref`:

```liquid
{% assign other = site.posts | where: "ref", page.ref
                             | where_exp: "p", "p.lang != page.lang" | first %}
{% if other %}
  <a href="{{ other.url | prepend: site.baseurl }}">
    {% if other.lang == 'fr' %}Lire en français{% else %}Read in English{% endif %}
  </a>
  <link rel="alternate" hreflang="{{ other.lang }}"
        href="{{ other.url | prepend: site.baseurl | prepend: site.url }}">
{% endif %}
<link rel="alternate" hreflang="{{ page.lang }}"
      href="{{ page.url | prepend: site.baseurl | prepend: site.url }}">
<link rel="alternate" hreflang="x-default"
      href="{{ site.url }}{{ site.baseurl }}/">
```

`jekyll-seo-tag` does **not** emit `hreflang`, and `jekyll-sitemap` does not emit sitemap alternates —
both must be hand-added in `head.html`. Untranslated articles simply have no alternate, which is correct
and expected by Google.

---

## 6. Translation strategy

### 6.1 Volume

| | Words | Est. tokens (round-trip) |
|---|---|---|
| EN → FR (209 posts) | ~409'000 | ~1.1 M |
| FR → EN (48 legacy posts, optional) | ~32'000 | ~90 K |

French text runs ~15–20% longer than English, so expect the FR archive to be larger on disk.

### 6.2 What must **not** be translated

This is where automated translation of technical articles usually goes wrong:

- **Code blocks** — Solidity/Python/Bash. Identifiers, function names, string literals must stay byte-identical.
  Only `//` comments are candidates, and even then leaving them English is defensible.
- **MathJax** (`$…$`, `$$…$$`) and the `isMath: true` front matter flag.
- **PlantUML `@startmindmap … @endmindmap` blocks** — the *syntax* must be preserved; only node **labels**
  should be translated. And the rendered PNG sitting above each mindmap would then be stale, so either
  re-render it or keep mindmap labels in English.
- **Front matter keys**, `image:` paths, `{{site.url_complet}}` interpolations, `categories`/`tags` values
  (these are index keys — translating them fragments the taxonomy).
- **Standard/protocol names**: ERC-4337, ISO 20022, zk-SNARK, Merkle tree, smart contract.
- **Quoted specification text** — quoting an EIP in translation misrepresents the source.

### 6.3 Terminology

Technical French in this domain is genuinely contested (`smart contract` vs `contrat intelligent`,
`hash` vs `empreinte`, `wallet` vs `portefeuille`). Without a fixed glossary, 209 independently
translated articles will use inconsistent terms and read as machine output.

**Build `_data/glossary-fr.yml` first**, covering the ~100 recurring terms across the top categories
(blockchain 120, security 66, cryptography 58, ethereum 48), and feed it into every translation prompt.
This single artefact is the difference between a credible French blog and an obviously translated one.

The existing 48 French articles are a free corpus for extracting the author's own preferred terminology —
mine them rather than inventing a glossary from scratch.

### 6.4 Workflow

1. Freeze `ref` keys on all English posts.
2. Build the glossary from the 48 existing French posts + a manual pass.
3. Translate in **category batches** (all `cryptography` together) so terminology stays coherent within a topic.
4. Automated post-check per file: code blocks byte-identical to source, `$…$` count matches, image paths
   unchanged, front-matter keys intact, PlantUML block parses.
5. **Human review.** Non-negotiable for security/cryptography content — a mistranslated claim about a
   vulnerability is worse than no French article.

### 6.5 Effort estimate

Machine translation of the whole archive is a few hours of compute. **Human review is the real cost:**
technical post-editing runs ~800–1'500 words/hour, so ~409'000 words ≈ **270–500 hours** for a full
reviewed pass. That is the number that decides this project.

Which is why the recommendation below is *not* "translate everything".

---

## 7. Recommended roadmap

**Phase 0 — Fix what's broken (½ day, valuable on its own)**
Correct `_config.yml`'s `lang`; backfill `lang:` on the 49 posts missing it; fix
`2024-09-09-suisse-crypto-fiscalite.md`; restore the canonical link. *Nothing here commits you to anything.*

**Phase 1 — Language plumbing (1–2 days)**
`ref` keys, `_data/i18n.yml`, `/fr/` routing, filtered listings, language switcher, `hreflang`,
per-language search index. **Ship it with the 48 existing French articles as the entire French site.**
The French version goes live immediately with real content and zero translation work — and the mixed-language
listing bug (§2.3) disappears for everyone.

**Phase 2 — Pilot translation (~15 articles)**
Build the glossary, then translate, review and publish a first batch.

> **Revised 2026-07-30.** This phase originally said "pick the highest-traffic articles, then check
> analytics — that's the decision gate". **The site has no analytics and will not get any** (the author
> has ruled out user tracking; see `site_improvement.md` §6.5), so that gate does not exist and traffic
> data cannot inform the pick.
>
> **Choose editorially instead** — which is arguably better anyway for a technical blog:
> - Articles whose subject has a genuinely French-speaking audience: the Swiss crypto-tax article, the
>   ISO 20022 / finance material, anything regulatory.
> - Articles you are most often asked about or link to yourself.
> - Cornerstone explainers (`eli10`, cryptography fundamentals) that pull readers into the rest of the site.
>
> Deliberately **avoid** starting with the seven Cyfrin First Flight write-ups or other contest notes:
> they are narrow, time-bound, and heavy in untranslatable code.

**Phase 3 — Scale, or don't**
Judge the pilot on effort rather than traffic: did producing 15 reviewed French articles cost what you
expected, and do you want to keep doing it? If yes, continue by category. If no, stop — you have lost two
days of plumbing and gained a properly structured bilingual site, which was worth it anyway.

Qualitative signals are still available without tracking anyone: search-engine referrals visible in
Google Search Console (already verified for this site), inbound links, and reader emails or issues.

**Rule going forward:** new articles are written in English and get French only on demand. Do not commit
to translating every future post; that is the obligation that kills bilingual blogs.

---

## 8. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Translation drift — English updated, French left stale | **High** (the classic failure) | `translated_from_date` in front matter; render "translated from the DD/MM/YYYY version" when the source is newer |
| Inconsistent technical terminology | High | Glossary before translation, category batching |
| Doubling the maintenance burden forever | High | Translate on demand only (Phase 3 rule) |
| Machine translation errors in security content | High | Mandatory human review; do not publish unreviewed |
| Moving legacy FR posts breaks inbound links | Medium | `jekyll-redirect-from` (whitelisted on GH Pages) |
| Thin/duplicate content penalty from bad translations | Medium | Correct `hreflang` + genuine editorial quality |
| `_posts/fr/` subdirectory leaking into `categories` | Medium | Verify with a local build; fallback is explicit per-file `permalink` |
| Two paginated indexes unsupported by `jekyll-paginate` | Low | FR index unpaginated, or the Actions workflow |
| Diagrams in `schema/` with baked-in English text | Low | Leave as-is initially; re-render only where it matters |

---

## 9. Summary

The site is closer to bilingual than it looks — `lang` metadata is largely in place and the theme is
small. Roughly **two days of plumbing** produces a working `/fr/` site, and because 48 genuine French
articles already exist, it launches with real content and no translation debt. The plumbing also fixes
the current mixed-language listings, so it pays for itself.

**Translating all 209 English articles is the expensive part** (~409'000 words, 270–500 hours of technical
review) and should be treated as a separate, evidence-driven decision made *after* the French site is live
and measurable — not bundled into the same commitment.
