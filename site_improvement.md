# Site Improvements — `access-denied`

**Date:** 2026-07-30
**Scope:** SEO, performance, CSS/JS, build, content hygiene — plus the changes that would make the
future French version (see [`multi-language.md`](./multi-language.md)) much cheaper to add.

Every item below was verified against the repository, not assumed. Items are grouped by theme and each
carries an effort/impact tag. **§9 is the recommended order of execution.**

---

## 1. Bugs — ✅ FIXED (2026-07-30)

These were actual defects with visible consequences. **All of §1 is now implemented** — see the
resolution note under each item.

### 1.1 Ten broken images in published articles ✅ *fixed*

Out of 624 in-article images, **10 render as broken** in production:

| Cause | Count | Files |
|---|---|---|
| **Windows backslashes** in the path | 3 | `2021-06-05-fuzzer-afl.md`, `2022-04-24-galois-counter-mode-gcm.md` |
| **Relative `../assets/…` paths** | 6 | `2024-12-05-virtual-protocol-architecture.md`, `2025-01-14-ethereum-nft-standard.md`, `2026-02-18-solidity-modifier-patterns-gas-bytecode-security.md`, `2026-04-15-soroban-state-archival.md`, `2026-05-11-htlc-garden-finance-bridge.md`, `2026-05-12-canton-network-architecture.md` |

The relative paths break because permalinks are `/:year/:month/:day/:title/` — `../assets/` resolves to
`/:year/:month/:day/assets/`, which doesn't exist. **All 6 target files are present on disk**, so it's
purely a path bug.

```diff
- ![Canton mindmap](../assets/article/blockchain/canton/canton-mindmap.png)
+ ![Canton mindmap]({{site.url_complet}}/assets/article/blockchain/canton/canton-mindmap.png)
```

182 of 255 posts already use `{{site.url_complet}}` correctly — this is drift, not a convention problem.
Worth noting that 4 of the 6 relative-path cases are **mindmap PNGs**, i.e. the article summary image is
the one that's missing.

> **✅ Resolved.** All 10 rewritten to `{{site.url_complet}}/assets/…` with forward slashes. Re-scanned
> all 624 in-article image references across `_posts/`: **0 broken, 0 residual backslash or `../` paths**.
> **Add the CI check (§6.2) so this can't regress.**

### 1.2 The `oracle` category link is a 404 ✅ *fixed*

`_includes/categories.html` auto-generates a link for **every** category in `site.categories`, pointing at
`/category/<slugified-name>/`. There are **20 categories in use but only 19 pages** in `_pages/category/`:
`oracle` (1 post) has no landing page, so its tile on the Categories tab links to a dead URL.

I verified the other 19 all resolve correctly — including `ISO20022` → `/category/iso20022/` and `ZKP` →
`/category/zkp/`. Note the `_pages/category/tryhackeme/` directory name is misspelled, but its
`permalink: /category/tryhackme/` and `site.categories['tryhackme']` query are both correct, so it works —
only the folder name is odd.

This is exactly the class of bug that consolidating the category pages (§5.2) prevents.

> **✅ Resolved.** Added `_pages/category/oracle/index.html` (modelled on the existing pages).
> Re-checked all 20 categories against the 20 permalinks: **every generated link now resolves**.

### 1.3 Duplicate `<title>` on pages without a title ✅ *fixed*

`_includes/head.html:8-10` emits a `<title>` when `page.title` is empty, but `{% seo %}` (line 34) **always**
emits one too. The home page and paginated pages therefore ship two `<title>` tags. Browsers pick the
first; search engines dislike it.

```diff
- {% unless page.title %}
- <title>{{ site.title }}</title>
- {% endunless %}
```

`jekyll-seo-tag` already falls back to `site.title`. Same for the `{% unless page.description %}` block
just below — `jekyll-seo-tag` handles the description too.

> **✅ Resolved.** Removed the duplicate `<title>` and `<meta name="description">` blocks from
> `_includes/head.html`, plus the dead commented-out canonical block, and left a comment explaining why
> nothing should be re-added there. Verified **no layout, include or page emits a literal `<title>`** any
> more — `jekyll-seo-tag` is now the single source.
>
> **Side effect: this also closes §2.2.** The canonical link was commented out; `jekyll-seo-tag` emits
> `rel="canonical"` automatically, so canonicals are now live site-wide.
>
> ⚠️ Note for future edits: Liquid **is** evaluated inside HTML comments, so a literal `{{ "{% seo %}" }}`
> written in a comment would still execute. The replacement comment deliberately refers to the plugin by
> name instead.

### 1.4 Malformed front matter ✅ *fixed*

`_posts/2024-09-09-suisse-crypto-fiscalite.md` had **empty `lang:` and `locale:` values** (my earlier note
said the value "bled into the next key" — that was a misread of the detection script; the fields were
simply blank). The post is French, so it was being served as `<html lang="fr">` only by accident of the
`_layouts/default.html` fallback.

Also **44 posts have an empty `image:`** and 5 have no `image:` key at all — those 49 posts get no
Open Graph preview when shared, are skipped by the "You might also enjoy" widget in
`_layouts/post.html:71` (`{% if post.image %}`), and are skipped as category thumbnails in
`_includes/categories.html`.

> **✅ Partly resolved.** Set `lang: fr` / `locale: fr-FR` on the Swiss-tax post.
>
> **Plus one extra bug found while validating:** `_posts/2021-05-11-virtualbox-augmenter-stockage.md`
> had `last-update: 2021-13-10` — **month 13**. Ruby's YAML parser silently degrades an invalid date to a
> string rather than erroring, so it never broke the build, but the value was meaningless. Corrected to
> `2021-10-13`. (`last-update` is currently read by **no template** — worth either surfacing it as a
> "last updated" line on posts or dropping the field; it appears in 46 posts.)
>
> **Not done — needs your judgement:** the **49 posts with no `image:`** can't be fixed mechanically,
> since each needs a chosen illustration. Until then they have no social-share preview and are invisible
> in the "You might also enjoy" widget.
>
> A full YAML validation pass over all 255 posts now reports **0 invalid front-matter blocks**.
>
> Minor, left alone: that post's filename says `2024-09-09` while its `date:` says `2024-09-18`. Jekyll
> uses the front-matter date, so the live URL is `/2024/09/18/…`. Harmless, but the two disagree.

---

## 2. SEO — ✅ IMPLEMENTED (2026-07-30)

All of §2 is done. **One finding changed during implementation** — see §2.1: the `robots.txt` in this
repository is not the one crawlers actually read, because this is a GitHub Pages *project* site.

### 2.1 `robots.txt` is missing the sitemap ✅ *fixed — but read the caveat*

`jekyll-sitemap` is installed and generates `/sitemap.xml`, but nothing points to it. `jekyll-sitemap`
only auto-creates a `robots.txt` when none exists — and one does, so the `Sitemap:` line was never added.

```
Sitemap: https://rya-sge.github.io/access-denied/sitemap.xml
```

The existing AI-crawler blocks (`GPTBot`, `ClaudeBot`, `Google-Extended`, …) are a deliberate choice and
fine to keep — just note `Google-Extended` only affects AI training, not Search indexing, so rankings
are unaffected.

> **⚠️ Bigger finding, specific to GitHub Pages.** `robots.txt` is only honoured at the **root of a host**
> (RFC 9309). This blog is a GitHub Pages *project* site at `https://rya-sge.github.io/access-denied/`,
> so this file is served at `…/access-denied/robots.txt` — a path crawlers **ignore**. They read
> `https://rya-sge.github.io/robots.txt`, which is served from the separate `rya-sge.github.io`
> user-page repository.
>
> **This means the AI-crawler blocks have most likely never been in effect**, and a `Sitemap:` line here
> would not be read either. Worth checking what that other repo currently serves.
>
> **✅ Done:** added the `Sitemap:` line, an explicit `User-agent: *` / `Disallow:` block, and a header
> comment documenting all of the above so the next reader isn't misled. The rules stay version-controlled
> next to the site and become effective automatically if it ever moves to a custom domain.
>
> **➡️ Action for you (I can't do it from this repo):** copy the AI-crawler rules into the `robots.txt` at
> the root of the `rya-sge.github.io` repository, and submit
> `https://rya-sge.github.io/access-denied/sitemap.xml` in Google Search Console and Bing Webmaster
> Tools. Both are already verified for this site (`googlebed50df54eff8961.html`, `BingSiteAuth.xml`).

### 2.2 Canonical URL is commented out ✅ *fixed as part of §1.3*

`_includes/head.html:17-18` has the canonical link disabled. With pagination (`/page/2/`), category pages
and tag anchors all surfacing the same posts, canonicals matter. `jekyll-seo-tag` emits one automatically
— so the simplest fix is to **delete the commented block and let the plugin do its job**.

> **✅ Resolved** — the dead block was removed in §1.3 and the plugin now supplies the canonical.

### 2.3 `_config.yml` declares the wrong site language ✅ *fixed*

`_config.yml:6` says `lang: "fr_FR"` for a site that is **82% English** (209 EN posts vs 48 FR).
`_layouts/default.html` correctly uses per-page `page.lang`, so this only affects site-level metadata —
but it's the wrong signal to send.

> **✅ Done, with a correction to my original advice.** I recommended `lang: "en"`; that would have been
> wrong. `site.lang` is consumed by **jekyll-seo-tag as the default `og:locale`**, which requires the
> `language_TERRITORY` form. Set to **`en_GB`** instead.
>
> `_layouts/default.html` now derives `<html lang>` from the post's **`locale`** field (`en-GB` / `fr-FR`,
> already present on 214 posts) and falls back to `lang`, then `en`. Both forms are valid BCP 47, and the
> locale form is more precise. This also replaces the old binary `{% if page.lang == "en" %}` test, which
> silently labelled every post lacking a `lang` as **French** — that was mislabelling ~40 English posts.
>
> **Also added for jekyll-seo-tag** (it reads none of the existing `author-name` / `social-*` keys):
> `author`, `logo`, `twitter.username` + `card: summary_large_image`, and a `social.links` block. These
> populate the JSON-LD author/publisher nodes and the Twitter card. Existing template keys left untouched.
>
> **Known remaining nuance:** posts carry `lang: en`, so jekyll-seo-tag emits `og:locale` as `en` rather
> than `en_GB`. Facebook falls back gracefully, so impact is cosmetic. Fixing it properly means rewriting
> `lang:` across 208 posts — which is exactly what §8.1 covers, so it belongs in that batch, not here.

### 2.4 Images are CSS backgrounds, not `<img>` ✅ *fixed*

Post thumbnails in `index.html:20`, `_layouts/category-page.html`, `_layouts/post.html` and the 19
category pages are rendered as `style="background-image: url(…)"`. Consequences:

- **Google Images cannot index them** — a meaningful traffic source for a diagram-heavy technical blog.
- No `alt` text → accessibility failure.
- No `loading="lazy"`, no `width`/`height` → layout shift (CLS) and no lazy loading.

Replacing them with real `<img>` elements plus `object-fit: cover` in CSS fixes all four at once.

> **✅ Done across 24 files** — `index.html`, `_layouts/category-page.html`, `_layouts/post.html` (related
> posts + article hero), `_includes/categories.html`, and all 20 `_pages/category/*/index.html`
> (scripted, since the markup was identical). Verified: **0 background-image thumbnails remain**.
>
> CSS updated in `_index-post.scss`, `_article-page.scss` and `_categories.scss` — each container is now
> `position: relative; overflow: hidden` with an absolutely-positioned `object-fit: cover` image, which
> reproduces the old `background-size: cover` exactly.
>
> Two details worth flagging:
> - The circular category tiles have a `:before` dark overlay. Its `z-index` had to be raised **and** the
>   `figure` made a stacking context (`z-index: 0`), otherwise the overlay would have covered the
>   "View all" label, which is a sibling of the figure rather than a child.
> - Category tile images use `alt=""` **deliberately** — they're decorative, since the category name sits
>   right beside them as text. Post thumbnails use the post title as alt.
>
> **No `width`/`height` attributes were added.** They're normally advised against CLS, but here every
> container already has fixed dimensions (`min-height: 180px`, or an aspect-ratio `:after`), so layout is
> stable without them — and the intrinsic sizes aren't knowable without reading all 209 files.
>
> **Bonus fix:** the article hero block in `_layouts/post.html` built a broken URL
> (`site.baseurl + "/assets/" + page.image`, while `page.image` already starts with `/assets/`, producing
> `/access-denied/assets//assets/…`). It never showed because **no post sets `imagePost`** — it's dead
> code. Repaired but deliberately left gated on `imagePost`, so enabling hero images on 209 posts stays
> your explicit choice rather than a side effect of this change.

### 2.5 In-article images have no lazy loading ✅ *fixed*

619 markdown images across the archive, **zero** with `loading="lazy"`. Kramdown won't add it. Given some
articles carry 20+ screenshots, this is a genuine mobile-performance win.

Alt text is actually in good shape: only 17 of 619 images have an empty `![]`.

> **✅ Done without a plugin** — which matters, because GitHub Pages runs Jekyll in safe mode (§6.1), so
> the `_plugins/` hook I originally floated was never an option. A JS pass would also have been useless:
> by the time JS runs, the browser has already started fetching the images.
>
> The portable fix is a Liquid string replace on the rendered HTML in `_layouts/post.html`:
> ```liquid
> {% assign post_body = page.content | markdownify
>      | replace: '<img src="', '<img loading="lazy" decoding="async" src="' %}
> ```
> This covers all 619 images at once. It relies on kramdown emitting `src` as the first attribute (it
> does, including when a title is present). All in-article images are markdown syntax — **no post uses a
> raw `<img>` tag** — so nothing is missed.
>
> Related posts and every listing thumbnail also got `loading="lazy" decoding="async"` as part of §2.4.

### 2.6 Structured data ✅ *fixed*

`jekyll-seo-tag` emits basic `BlogPosting` JSON-LD. Adding `BreadcrumbList` and filling in
`author`/`publisher` more completely would improve rich-result eligibility.

> **✅ Done.** New `_includes/breadcrumbs.html` emits a `BreadcrumbList` node
> (*AccessDenied → category → article title*), included from `head.html` right after the seo tag. Pure
> Liquid, so it works under Pages' safe mode. It renders **only for posts**, and degrades to a 2-item
> list when a post has no category.
>
> Category slugs are built with `downcase | slugify` — matching `_includes/categories.html` exactly — so
> a breadcrumb URL always points at a real category page (`ISO20022` → `/category/iso20022/`). Both
> branches were validated as parseable JSON.
>
> The `author` / `logo` / `social` config added in §2.3 fills in the publisher side.

---

## 3. Performance — ✅ IMPLEMENTED (2026-07-30), except §3.4

§3.1, §3.2, §3.5 done. §3.3 done **partially and deliberately**: jQuery was kept at the author's
request, and only the version was patched. **§3.4 (image optimisation) was explicitly skipped.**

### 3.1 The entire stylesheet is inlined into every page ✅ *fixed*

`_includes/head.html:35-40`:

```liquid
<style>
  {% capture include_to_scssify %}{% include main.scss %}{% endcapture %}
  {{ include_to_scssify | scssify }}
</style>
```

`_sass/` is 168 KiB across 35 partials, compiled and **embedded in the `<head>` of all ~280 generated
pages**. This means:

- **Zero CSS caching.** Every page navigation re-downloads the full stylesheet as part of the HTML.
- **Larger HTML on every request** — including the paginated `/page/N` fragments that `main.js` fetches
  over AJAX for "Load more", which re-downloads the whole stylesheet each time it's clicked.
- **Slower builds** — SCSS is recompiled once per page instead of once per site.

Fix: make it a real cacheable stylesheet.

```
# assets/css/main.scss  (new file, front matter required)
---
---
@import 'main';
```
```html
<!-- head.html -->
<link rel="stylesheet" href="{{ '/assets/css/main.css' | relative_url }}">
```

`sass: style: compressed` is already set in `_config.yml`, so output stays minified. If you want to keep
first-paint speed, inline only critical CSS and load the rest async — but the plain fix already wins.

> **✅ Done.** `_includes/main.scss` → `_sass/main.scss` (via `git mv`, so history is preserved), new
> `assets/css/main.scss` entry point with empty front matter, and `head.html` now links
> `/assets/css/main.css` via `relative_url`.
>
> **Verified by actually compiling it** with Dart Sass using the same load path Jekyll uses: builds
> clean, and the output contains all the §2.4 `object-fit` rules.
>
> **Measured result — the compiled stylesheet is 25.3 KiB compressed:**
>
> | | Before | After |
> |---|---|---|
> | CSS delivery | inlined into all ~280 pages | one cacheable file |
> | Total CSS bytes across the site | **≈6.9 MiB** duplicated | **25.3 KiB** downloaded once |
> | Cacheable | ❌ never | ✅ yes |
>
> This also shrinks every `/page/N` fragment that the "Load more" button fetches over AJAX — those were
> each re-downloading the full stylesheet.
>
> No cache-busting query string was added: GitHub Pages serves assets with `Cache-Control: max-age=600`
> and an ETag, so a stale stylesheet self-corrects within ten minutes. Add `?v=` only if that ever bites.
>
> Unrelated nit spotted: `_sass/6-trumps/helpers.scss` is missing the `_` prefix every other partial has.
> Sass resolves it either way, so it is cosmetic — worth renaming for consistency.

### 3.2 KaTeX CSS loaded on every page, apparently unused ✅ *fixed*

`_includes/head.html:27-29` loads `fonts/katex.min.css` (22 KiB) on **every page**. But math is rendered
by **MathJax v4 SVG** (`_includes/mathJax.html`), which doesn't use KaTeX stylesheets, and
`jekyll-katex` is commented out in `_config.yml:50`. Only 68 posts even set `isMath: true`.

Worse, the tag carries `integrity="sha384-…" crossorigin="anonymous"` on a **same-origin local file**.
The `crossorigin` attribute forces a CORS check on your own asset, and if the hash doesn't match the
local copy the browser silently blocks the stylesheet. Verify it's genuinely unused, then delete it.

> **✅ Done.** Confirmed unused first: the only remaining mentions of "katex" anywhere in the source are
> the commented-out `#  - jekyll-katex` line in `_config.yml` and a note in `Gemfile`. Math is rendered
> by MathJax v4 in **SVG** mode, which embeds glyph outlines and needs no font CSS at all.
>
> Removed the `<link>` and deleted `fonts/katex.min.css` (22 KiB) — recoverable from git if ever needed.
> Saves 22 KiB **and one render-blocking request on every page**.

### 3.3 jQuery + plugin stack: 180 KiB for very little ⚖️ *version patched; jQuery kept by request*

| File | Size | What it does |
|---|---|---|
| `jquery-3.3.1.min.js` | 135 KiB | Used only by `main.js` |
| `evil-icons.min.js` | 35 KiB | Renders `data-icon` placeholders |
| `simple-jekyll-search.min.js` | 6.6 KiB | Search |
| `jquery.fitvids.js` | 3.3 KiB | Responsive video wrapper — **replaceable by 3 lines of CSS** (`aspect-ratio`) |
| `main.js` | 3.2 KiB | Search init, tab toggle, load-more, smooth scroll |

`main.js` uses jQuery for `$(document).ready`, class toggling, `$.get` and `append` — all trivial in
modern vanilla JS. **jQuery 3.3.1 is from 2018 and has known advisories** (CVE-2019-11358 prototype
pollution, CVE-2020-11022/11023 in `.html()`/`.append()`); `main.js:65-66` uses `$.parseHTML` and
`.append()` on fetched HTML, which is exactly the affected pattern. It's your own same-origin content so
exploitability is low, but it's flagged by every scanner.

**Minimum action:** bump jQuery to 3.7.1. **Better:** drop jQuery and fitVids entirely (~138 KiB saved)
and rewrite `main.js` in vanilla JS.

`evil-icons` is worth reconsidering too: icons are `<div data-icon>` placeholders that are **invisible
until JS runs**, so social links and the search icon are blank on first paint. Inline SVG would render
immediately and cost nothing.

> **⚖️ Decision: jQuery stays.** Per explicit instruction, jQuery was **not** removed and `main.js` was
> **not** rewritten in vanilla JS. fitVids and evil-icons were left untouched as well.
>
> **✅ What was done: the security patch only** — jQuery **3.3.1 → 3.7.1**, which keeps jQuery while
> clearing the three advisories that scanners flag (CVE-2019-11358, CVE-2020-11022, CVE-2020-11023).
>
> Compatibility was checked before swapping, since the riskiest change in that range is the jQuery 3.5
> `htmlPrefilter` fix (self-closing tags for non-void elements are no longer expanded):
> - `jquery.fitvids.js` calls `.wrap('<div class="fluid-width-video-wrapper"></div>')` — **properly
>   closed**, so unaffected.
> - `main.js` calls `$.parseHTML(data)` then `.append($articles)` where `$articles` is a **jQuery object,
>   not an HTML string** — the prefilter is not involved.
>
> The downloaded file was verified against jQuery's **published SRI hash**
> (`sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=`) — exact match, so the artefact is authentic.
> The old `js/jquery-3.3.1.min.js` was deleted. Net size change is a **49 KiB saving** (135 → 85.5 KiB),
> since 3.7.1 dropped IE support.
>
> ⚠️ **Untested at runtime** — no local Jekyll build is possible here (§6.3). Smoke-test search,
> "Load more", the Posts/Categories tabs and video embeds. Revert is one line in
> `_includes/javascripts.html` plus `git checkout` of the old file.

### 3.4 Unoptimised images — 68 MiB of assets ⏭️ *SKIPPED by request — still outstanding*

17 files exceed 500 KiB; the worst offenders:

| Size | File |
|---|---|
| 1.46 MB | `assets/article/blockchain/bitcoin/Bitcoin-address-BIP-39.drawio.png` |
| 1.41 MB | `assets/article/blockchain/oracle/chainlink-push-pull-oracle.png` |
| 1.30 MB | `assets/article/blockchain/wallet/ledger/Ledger-recover.drawio.png` |
| 1.25 MB | `assets/article/blockchain/defi/patrick-baum-hB9vo06o9z8-unsplash.jpg` |

These are mostly **exported draw.io diagrams** — flat-colour vector content stored as PNG, which is the
worst case for that format. Converting diagrams to **SVG** (draw.io exports it natively) would cut them
by 90%+ *and* make them sharp on retina. For photos, WebP at quality 80. A one-off `oxipng`/`cwebp` pass
over the rest is easy and safe.

### 3.5 External font requests ✅ *fixed*

`_includes/head.html:25` still pulls Open Sans from `fonts.googleapis.com` (render-blocking + a
third-party request, and a GDPR talking point in the EU). Volkhov is already self-hosted in `fonts/` —
do the same for Open Sans and add `font-display: swap`.

> **✅ Done.** Open Sans is now self-hosted in `fonts/opensans.css` + `fonts/file/*.woff2`, following the
> exact layout `fonts/volokhov.css` already used. **The site now makes zero third-party requests on page
> load.**
>
> Google served **10 subsets** (cyrillic, greek, hebrew, vietnamese, math, symbols…). Only **latin** and
> **latin-ext** were kept — together they cover English and French, including the `œ` ligature at
> U+0152-0153. That is 4 woff2 files, ~163 KiB total, and browsers fetch only the subsets a page
> actually needs via `unicode-range`.
>
> `font-display: swap` is set on all four faces, so text renders immediately in the fallback instead of
> being invisible while the font loads. Open Sans is Apache-2.0, so self-hosting is permitted; the licence
> is recorded in the CSS header.
>
> The old commented-out Volkhov `googleapis` link was removed at the same time. The only remaining
> mention of `fonts.googleapis.com` in `head.html` is the explanatory comment.

---

## 4. CSS / SCSS

### 4.1 Structure is good 🟢

The ITCSS layering (`0-settings` → `6-trumps`) is clean and the BEM-ish `c-` / `o-` / `u-` naming is
consistent. **Don't restructure this.** The problems are in delivery (§3.1), not organisation.

### 4.2 No dark mode 🟡 *(3–4 h)*

Zero `prefers-color-scheme` rules in `_sass/`. For a technical blog with heavy code blocks, dark mode is
a frequently-expected feature. Since colours are already centralised in `_sass/0-settings/_colors.scss`,
converting them to CSS custom properties and adding one `@media (prefers-color-scheme: dark)` block is
mostly mechanical.

### 4.3 `normalize.scss` is 7.7 KiB of 2012 🟢 *(30 min)*

The largest partial in `_sass/` is a full legacy normalize.css. A modern minimal reset would cut most of
it. Low priority, but it's free bytes on every page.

---

## 5. Templates, accessibility & duplication — ✅ IMPLEMENTED (2026-07-30)

All five items done. The deduplication in §5.1–§5.2 is also the §8.3 multi-language groundwork, so that
item is now largely complete as a side effect.

### 5.1 Search markup is copy-pasted 4× ✅ *fixed*

The identical search box appears in `_includes/header.html`, `_layouts/post.html:8-16`, `tags.html` and
`404.html`. Extract `_includes/search-box.html` and include it. This directly reduces the multi-language
work later (§8.2) — four copies means four places to translate the placeholder.

> **✅ Done.** New `_includes/search-box.html`, taking an optional `class` parameter (three of the four
> call sites need `u-full-width`). Verified: **no file outside the include still contains the raw
> markup**, and all four call sites now include it.
>
> Two small accessibility upgrades came along for free: `type="search"` instead of `type="text"`, and
> `aria-live="polite"` on the results list so screen readers announce results as they appear.

### 5.2 The 19 category pages are near-identical ✅ *fixed (20 pages)*

`_pages/category/*/index.html` are 19 copies of the same ~28-line template differing only in the category
name. They exist because `_plugins/category-generator.rb` **never runs on GitHub Pages** (see §6.1).

Consolidate them to a shared layout so each file is just front matter:

```yaml
---
layout: category-list
title: zkp
category: ZKP
permalink: /category/zkp/
---
```

This is a prerequisite for the French version, where the alternative is maintaining **38** such files.

> **✅ Done.** New `_layouts/category-list.html` holds the markup once; all **20** pages are now front
> matter only — from ~28 lines each down to 6.
>
> A `category:` field was added alongside `title:`, because the two are **not** always the same: the
> ISO 20022 page displays *"ISO 20022"* but must query `site.categories['ISO20022']`. The old
> `_layouts/category-page.html` used `site.categories[page.title]`, which would have silently returned an
> empty list for that page. Verified all 20 categories resolve to a page with the correct key.
>
> `_layouts/category-page.html` (used only by the safe-mode-disabled plugin) now just chains to
> `category-list`, so the plugin path and the checked-in pages can no longer drift apart — which is what
> allowed the missing `oracle` page in §1.2 to go unnoticed.
>
> The post-card markup was **also** duplicated between `index.html` and the category pages, so it moved
> into `_includes/post-card.html` (with an optional `show_words` flag, since only the home page showed
> reading time). `index.html` dropped from 27 lines of card markup to 3.

### 5.3 Accessibility gaps ✅ *fixed (except contrast, see below)*

- Icons are `<div data-icon>` — not focusable, no accessible name, invisible without JS.
- The Posts/Categories switcher (`js/main.js:34`) is `<li>` elements with click handlers — **not
  keyboard-accessible**. Should be `<button>` with `aria-selected`.
- `.c-top` scroll-to-top is a `<div>` with a `title` — should be a `<button>`.
- Thumbnails as CSS backgrounds have no accessible name (§2.4).
- Worth checking contrast ratios in `_sass/0-settings/_colors.scss` against WCAG AA.

`u-screen-reader-text` labels are already used on the search inputs — good, keep that pattern.

> **✅ Done:**
> - **Posts/Categories tabs** are now real `<button>`s inside the `<li>`s, with `role="tab"` and
>   `aria-selected` kept in sync. They were previously unreachable by keyboard entirely. `main.js` now
>   selects by `data-target` rather than `:last-child`, so behaviour no longer depends on markup order.
> - **Scroll-to-top** is a `<button>` with `aria-label="Scroll to top"` instead of a `<div>`.
> - **Social links** — all 9 gained `u-screen-reader-text` names. The screen-reader text is a *sibling*
>   of the icon, not an attribute on it, because evil-icons **replaces** the `data-icon` node at runtime
>   and would discard any `aria-*` put there.
> - **`:focus-visible` outlines** added to both new buttons — making something focusable is pointless if
>   the focus ring is invisible.
> - Thumbnail alt text was already handled in §2.4.
>
> CSS: `<button>` needs its default `background`/`border`/`font` reset to keep the previous look. The
> `:first-child` / `:last-child` border-radius rules had to move to `li:first-child .c-nav__item`,
> because the button is *always* the only child of its `li` and would otherwise have matched both rules
> and got both roundings. **Verified by compiling the SCSS.**
>
> **⚠️ Not done: colour contrast.** Checking `_sass/0-settings/_colors.scss` against WCAG AA needs visual
> verification I can't do here, and fixing it would change the site's palette — a design decision that
> should be yours.

### 5.4 Leftover debug markup ✅ *fixed*

`_layouts/post.html:59` renders a literal `<p>Share button</p>` above the share icons. Delete it.

> **✅ Done** — removed. It was visible on all 255 article pages.

### 5.5 Fragile tags loop ✅ *fixed*

`tags.html:22` iterates `(0..site.tags.size)` with an `{% unless forloop.last %}` guard — an off-by-one
workaround that will silently drop or duplicate a tag if the collection shape changes. `{% for tag in
site.tags %}` is clearer and correct.

> **✅ Done.** Both loops now iterate `site.tags | sort`, which yields `[name, posts]` pairs already
> ordered by name — the `capture`/`split`/index dance and the second range loop are gone. Tag post images
> also gained `loading="lazy"` and escaped alt text.
>
> **Trap hit while doing this**, worth recording: my explanatory comment quoted a Liquid tag, and
> **Liquid parses tags inside `{% comment %}` blocks too** — so the unclosed quoted tag broke the build
> exactly like the markdown docs in §6.4. Caught by the tag-balance check before pushing; the comment was
> reworded to describe the old code in prose instead.

---

## 6. Build & tooling

### 6.1 No CI — and `_plugins/` is dead code in production 🔴 *(1 h, unlocks a lot)*

There is **no `.github/` directory**. The site is built by GitHub Pages' classic pipeline, which runs
Jekyll in **safe mode**, so:

- `_plugins/category-generator.rb` **never executes in production** — hence the 19 hand-written category
  pages (§5.2). Right now the file is misleading dead code.
- No plugin outside the GitHub Pages whitelist can be used — this blocks `jekyll-polyglot`,
  `jekyll-paginate-v2`, image-processing plugins, and more.
- **Nothing validates a build before it goes live.** A Liquid error ships silently.

A ~30-line GitHub Actions workflow (`actions/jekyll-build-pages` + `actions/deploy-pages`) removes all
three limitations at once. This is the **highest-leverage change in this document** — it's a prerequisite
for several items here and for the cheaper multi-language options.

### 6.2 No link/image checking 🟠 *(1 h)*

§1.1 found 10 broken images that have been live for a while. Add `html-proofer` to the CI build:

```yaml
- run: bundle exec htmlproofer ./_site --disable-external --allow-hash-href
```

Catches broken internal links, missing images and malformed HTML on every push. Start with
`--disable-external` (external link checking is flaky), then consider a weekly scheduled run with
externals enabled — a 5-year-old archive of security articles will have accumulated dead outbound links.

### 6.3 Local development is not reproducible 🟠 *(30 min)*

Neither `bundle` nor `jekyll` is installed in this environment, so **the site cannot currently be built
or previewed locally**. `Gemfile.lock` is git-ignored, and the `Gemfile` pins nothing:

```ruby
gem 'jekyll'          # any version
gem 'jekyll-paginate'
```

Meanwhile GitHub Pages runs a **fixed, older** Jekyll (3.9.x via the `github-pages` gem). Local and
production can silently diverge. Fix: use `gem "github-pages", group: :jekyll_plugins` (which pins the
exact production set), **or** move to the Actions build (§6.1) and pin versions yourself. Either way,
**commit `Gemfile.lock`** — it is currently git-ignored, which is the opposite of what you want for a
deployed site.

### 6.4 Repository files are published to the live site ✅ *fixed — and it was breaking the build*

`_config.yml` excludes only `Gemfile`, `Gemfile.lock`, `vendor`, `feedback.md` and `draft`. **Not
excluded**, and therefore copied verbatim into `_site/` and served publicly:

| Path | Size | Notes |
|---|---|---|
| `schema/` | **1.8 MB**, 90 files | `.drawio` / `.excalidraw` diagram sources |
| `article_list.md` | 52 KB | internal index |
| `tree.txt` | 40 KB | directory dump |
| `CLAUDE.md` | 4.2 KB | internal instructions |
| `DEPENDENCE.md`, `polyfills.md` | 9 KB | internal notes |

None have front matter, so they're served as raw files rather than rendered pages. Nothing here is
secret, but it's ~1.9 MB of noise that search engines can index. Extend `exclude:`:

```yaml
exclude:
  - Gemfile
  - Gemfile.lock
  - vendor
  - feedback.md
  - draft
  - schema
  - CLAUDE.md
  - DEPENDENCE.md
  - polyfills.md
  - article_list.md
  - tree.txt
  - multi-language.md
  - site_improvement.md
  - README.md
  - LICENSE.txt
```

Keep `schema/` in the repo (it's the diagram source of truth) — just stop publishing it.

> **🔴 This turned out to be more than cosmetic — it broke the GitHub Pages build.**
>
> GitHub Pages force-enables **`jekyll-optional-front-matter`** (visible in the build log:
> `Requiring: jekyll-optional-front-matter`). That plugin turns **every markdown file without front
> matter into a rendered page**. And Jekyll runs **Liquid before markdown**, so ```` ``` ```` code fences
> do **not** protect Liquid tags — a `{% if %}` quoted inside a fenced block is parsed for real.
>
> Both of the analysis documents I added quote Liquid, so both became pages and both failed to parse:
>
> | File | Problem |
> |---|---|
> | `site_improvement.md` | unbalanced `unless` (3 open / 1 close), `if` (3 / 0), `for` (1 / 0) |
> | `multi-language.md` | unknown tag `{% t %}` (the polyglot translation tag, quoted as an example) |
>
> `feedback.md` has the same defect but was already excluded, which is why the build was green before.
>
> **✅ Fixed** by applying the `exclude:` list above, with a comment in `_config.yml` explaining the trap
> so the next internal note that quotes Liquid gets excluded too. Verified: **0 remaining root files are
> rendered as pages with broken Liquid**, and **2.68 MiB** stops being published.
>
> **Lesson worth keeping:** on GitHub Pages, any internal `.md` at the repo root that quotes Liquid must
> be added to `exclude:` — code fences are not enough.

### 6.5 No analytics 🟠 *(20 min, and it's a blocker for the FR decision)*

`google-analytics:` in `_config.yml` is empty and `_includes/analytics.html` doesn't exist, so the
`{% if site.google-analytics %}` block in `_layouts/default.html:14` never fires.

**There is currently no way to know which articles are read.** That matters well beyond curiosity:
the French-version roadmap in `multi-language.md` §7 has a "check if anyone reads `/fr/`" decision gate,
and it cannot be evaluated without traffic data. A privacy-respecting option (GoatCounter, Plausible,
Umami) fits the blog's stance better than GA and avoids the cookie banner.

---

## 7. Content hygiene

- **`draft/` is excluded from the build but committed** (122 files, 1.3 MB) — fine, just be aware it's
  public on GitHub even though it's not on the site.
- **`_posts/` contains two undated files**: `Blockchain downtime.md` (25 KB) and `permit.md` (5.9 KB).
  Without a `YYYY-MM-DD-` prefix Jekyll won't publish them — they look like drafts sitting in the wrong
  directory. Move them to `draft/` or give them dates.
- **Categories are inconsistently cased**: `ISO20022`, `ZKP`, `blockchainBestOf` vs `ai`, `defi`, `rfc`.
  Slugification currently absorbs this (§1.2), but normalising the taxonomy is easier now than after it's
  duplicated in French. `oracle` (1 post) and `finance` (2) are thin enough to fold into a neighbour
  rather than keep as standalone categories.
- **Two posts use an `Auteur:` front-matter key** that no template reads.
- `disqus-identifier` is commented out — comments are effectively disabled. Deliberate or forgotten?

---

## 8. Adjustments that make the French version cheap later

These are worth doing **now**, independent of whether you ever build the French site. Each one either
reduces future duplication or is strictly harder to retrofit later. Cross-references point to
`multi-language.md`.

### 8.1 Normalise `lang:` on every post — *do this first* 🔴 *(1 h, scripted)*

49 posts have no `lang:` — almost exactly the 48 legacy French ones. 208 have `lang:`, 214 have `locale:`.
Backfill both so every post carries `lang: en|fr`, and fix the malformed line (§1.3).

**Why now:** `_layouts/default.html` already reads `page.lang`, so today those 49 posts are served as
`<html lang="fr">`… while 40+ of the *English* ones would be too if their `lang` were missing. Correct
`lang` attributes matter for screen readers and for search-engine language detection **today**, with no
French site required.

### 8.2 Extract all hardcoded UI strings into `_data/i18n.yml` ✅ *implemented*

Currently English strings are scattered across `index.html`, `_layouts/post.html`,
`_layouts/category-page.html`, `_includes/header.html`, `_includes/categories.html`, `tags.html` and
`404.html`: *"Type to search…"*, *"Load more posts"*, *"You might also enjoy"*, *"minute read"*,
*"View all"*, *"No results found"*, *"Tags in Blog"*, *"Feel free to contact me on"*.

Move them to `_data/i18n.yml` keyed by language and read them via
`{% assign t = site.data.i18n[page.lang] | default: site.data.i18n.en %}`.

**Benefit today:** strings stop being duplicated across 4 files (§5.1), so changing the search
placeholder is one edit instead of four. **Benefit later:** adding French is one YAML block.

> **✅ Done.** `_data/i18n.yml` now holds **23 keys**, with complete `en` and `fr` blocks — verified for
> key parity and no empty values. Ten templates read from it: `search-box`, `header`, `categories`,
> `post-card`, `javascripts`, `post`, `home`, `default`, `index.html`, `tags.html`, `404.html`.
>
> Every consumer resolves its own `t` with
> `{% assign t = site.data.i18n[page.lang] | default: site.data.i18n.en %}`. The `default:` fallback is
> deliberate — a page with a missing or unknown `lang` renders English rather than blank labels.
>
> **A subtlety worth knowing:** each Jekyll layout is rendered in its own pass, so a variable assigned in
> `home.html` is **not** visible in its parent `default.html`. I hit exactly that — the scroll-to-top
> button rendered an empty `aria-label` until `default.html` resolved `t` itself. Any new layout that
> uses `t` must assign it locally; a check for that is in the verification below.
>
> **Two things deliberately not translated:**
> - **Proper nouns** (Twitter, GitHub, LinkedIn, Bluesky…) stay hardcoded — they are names, not UI text.
> - **`404.html`'s front-matter `title:`.** Front matter cannot read `site.data`, so the browser-tab
>   title stays English. The visible `<h1>` *is* translated. A French 404 needs its own page under
>   `/fr/`, which is §8.5 territory.
>
> **Known limitation — dates.** `date_format` is per-language (`%Y, %b %d` vs `%d %b %Y`), so ordering is
> right, but **Jekyll always renders month names in English** whatever the format string. A properly
> localised *"3 février 2026"* needs a month lookup table in `_data/i18n.yml` plus a small Liquid helper.
> Deliberately deferred: it only becomes visible once French pages actually exist.

### 8.3 Deduplicate templates before duplicating them per language ✅ *done via §5.1–§5.2*

§5.1 and §5.2. Nineteen copy-pasted category pages become **38** the day French exists; four copies of
the search box become **eight**. Consolidating first means the French version adds front matter, not
templates. **This is the single change that most reduces future multi-language cost.**

> **✅ Done as part of §5.** What that actually bought, concretely:
>
> | Markup | Before | After | If French is added |
> |---|---|---|---|
> | Category page body | 20 copies × ~28 lines | 1 layout + 20× 6-line front matter | +20 front-matter stubs, **0 new markup** |
> | Search box | 4 copies | 1 include | +0 |
> | Post card | 2 copies | 1 include | +0 |
>
> Combined with §8.2, a French category page is now **six lines with no HTML in it**:
>
> ```yaml
> ---
> layout: category-list
> title: cryptographie
> category: cryptography     # same key — the taxonomy is NOT duplicated
> permalink: /fr/category/cryptographie/
> lang: fr
> ---
> ```
>
> **What is still left to do here.** Deduplication is finished for *listings*, but three templates would
> still need a language-aware pass when French arrives:
>
> 1. **`_layouts/post.html`** — the "You might also enjoy" block uses `site.related_posts`, which is not
>    language-aware and would mix French and English (see §8.5).
> 2. **`index.html`** — one paginated index exists; a second one at `/fr/` is the pagination constraint
>    described in §3.2 of `multi-language.md`.
> 3. **`tags.html`** — a single global tag page across both languages. Either filter it by `page.lang`
>    or accept a shared tag index.
>
> **Recommendation:** keep `categories` and `tags` values identical across languages (English keys),
> translating only the *display* label via `_data/i18n.yml`. Translating the keys themselves would
> fragment the taxonomy and double the number of category pages for no reader benefit.

### 8.4 Add a stable `ref:` translation key 🟡 *(30 min, scripted) — still outstanding*

Add `ref: <slug>` to every post now, derived from the current filename slug and then frozen. It's the
join key that pairs an article with its translation (`multi-language.md` §5.1). Adding it to 255 posts is
a scripted one-liner today; retrofitting it *after* translations exist means reconciling two sets of
files by hand.

**Why a separate key at all** — the obvious alternatives all break:

| Candidate join key | Why it fails |
|---|---|
| Filename | The French file must have a different name, or it collides in `_posts/` |
| `title` | Translated by definition, so it cannot match across languages |
| `permalink` | Differs by design (`/fr/…`), so it cannot match either |
| Date | Not unique — several posts share a date (e.g. seven on 2025-07-11) |

So `ref` has to be its own field, and its one job is to **never change**. It is not a slug, not a title,
and not a URL — renaming an article or fixing its title must leave `ref` untouched, otherwise the pairing
silently breaks and the language switcher stops appearing.

**Proposed shape:**

```yaml
# _posts/2024-11-4-TLS1.3-overview.md
lang: en
ref: tls-1-3-overview

# _posts/fr/2024-11-4-tls1.3-presentation.md
lang: fr
ref: tls-1-3-overview      # identical — this is what pairs them
```

**Implementation notes:**

- Derive the initial value from the filename slug **minus the date prefix**, lowercased and slugified,
  then freeze it. Two posts must never share a `ref` unless they are translations of each other.
- **Watch for near-duplicate slugs** when generating: the seven `cyfrin-first-fight-*` posts and the four
  `2022-04-22-*` cipher-mode posts produce similar stems and need a uniqueness assertion in the script.
- **`2026-07-30-alchemy-smart-wallet-account-abstraction.md`** and the untracked
  `2026-07-30-rundler-alchemy-erc4337-bundler.md` are closely related but are *different articles* — they
  must get different `ref` values.
- Add a build-time guard (§6.2) asserting `ref` is unique per language; a duplicated `ref` would make the
  `where` lookup in the switcher return the wrong article.

**Effort:** ~30 minutes scripted, of which most is eyeballing the generated values. Do it in the same
pass as any future front-matter normalisation to avoid touching all 256 posts twice.

### 8.5 Restructure listings to filter by language 🟡 *(2 h) — still outstanding, and a live bug*

Every listing iterates `site.posts` unconditionally, so **French and English articles are interleaved
everywhere today**. Now that all 256 posts carry an accurate `lang` (§8.1), the fix is mechanical.

**Exact inventory of what needs filtering:**

| Location | Current | Fix | Notes |
|---|---|---|---|
| `index.html:16` | `site.posts limit/offset` | `where: "lang", page.lang` | interacts with pagination — see below |
| `_layouts/category-list.html` | `site.categories[cat]` | `where: "lang", page.lang` | covers all 20 category pages at once |
| `tags.html` | `site.tags` | filter posts per tag | tag *counts* also need recomputing |
| `search.json` | `site.posts` | add a `lang` field, or emit one index per language | pairs with `siteConfig.searchJson` (§8.6) |
| `_layouts/post.html:75` | `site.related_posts` | **replace entirely** | see below |
| `_includes/categories.html` | `site.categories[category] | size` | per-language counts | tile counts are wrong otherwise |

**Three non-obvious complications:**

1. **`site.related_posts` cannot be filtered.** It is computed by Jekyll (most-recent posts, or LSI if
   enabled) and there is no `lang` hook. It must be *replaced* with an explicit Liquid expression, e.g.
   same-language posts sharing a category:
   ```liquid
   {% assign related = site.posts | where: "lang", page.lang %}
   ```
   then exclude `page.url` and take the first 4. Note the existing widget already skips posts with no
   image — now moot, since §"mindmaps" gave every post one.

2. **Pagination.** `index.html` uses `paginator.total_pages` for the "Load more" bound while listing via
   `limit`/`offset`. Filtering by language changes the real post count but **not** `paginator.total_pages`,
   which `jekyll-paginate` computes from the unfiltered `site.posts`. The counter and the list would
   disagree, so the `postCount` / `postsCovered` logic must be recomputed from the filtered array —
   otherwise "Load more" either disappears early or fetches empty pages.

3. **Tag counts.** `tags.html` renders `{{ tag[1] | size }}`. Post-filtering, that must count only
   same-language posts, or a tag can advertise "12" and then list three.

**Do this even if French never happens.** Every item above is a bug on the current site: a visitor on the
home page sees 2021 French posts between 2026 English ones, and category tiles count both languages.
The work is identical whether it is framed as a bug fix or as multi-language groundwork — which is why it
sits in §8 rather than §1.

**Sequencing:** do §8.4 (`ref`) first if you intend to ship French, since the language switcher and the
filtered listings are usually written in the same pass.

### 8.6 Make `js/main.js` path-aware ✅ *implemented*

`main.js:17` hardcodes `/access-denied/search.json` and `main.js:62` hardcodes `/access-denied/page/`.
Both should come from `data-` attributes rendered by Liquid. That kills the hardcoded `baseurl`
duplication now (it breaks any local preview served at `/`), and later lets the same script pick
`search-fr.json` and `/fr/page/N` without a second copy.

> **✅ Done**, via a `window.siteConfig` object emitted by `_includes/javascripts.html` rather than
> `data-` attributes — the script needs several values including nested strings, and one typed object is
> cleaner than scattering attributes across elements:
>
> ```js
> window.siteConfig = {
>   baseurl: …, lang: …,
>   searchJson: …,   // '/search.json'  | relative_url
>   pagePath: …,     // '/page/'        | relative_url
>   i18n: { noResults: …, loading: … }
> };
> ```
>
> `main.js` reads it once at startup with literal fallbacks, so the script still works standalone if the
> config block is ever missing. **Verified: zero occurrences of `access-denied` remain in `js/`, and
> `node --check` passes.**
>
> Two extra wins beyond the original scope:
> - The **`Loading...`** and **`No results found`** strings moved into `_data/i18n.yml` too, so the search
>   UI is fully translatable without touching JavaScript.
> - The five `<script src>` tags now use `relative_url` instead of `{{site.baseurl}}` string
>   concatenation, matching how the stylesheet and fonts are referenced since §3.1.
>
> **This fixes a real bug today:** `jekyll serve` locally has no `/access-denied` prefix, so search and
> "Load more" were silently broken in local preview — both now follow whatever `baseurl` is configured.

---

## 9. Recommended order

**Batch 1 — Quick wins** — ✅ **complete except one item**
~~§1.1 broken images~~ · ~~§1.2 oracle 404~~ · ~~§1.3 duplicate title~~ · ~~§1.4 front matter~~ ·
~~§2.1 sitemap in robots.txt~~ · ~~§2.2 canonical~~ · ~~§2.3 site lang~~ · ~~§6.4 exclude list~~
(promoted here — it was failing the build) — **remaining:** §5.4 debug markup

**All of §2 (SEO) is now done**, including §2.4 real `<img>` tags, §2.5 lazy loading and §2.6 structured
data, which were originally scheduled for Batch 5.

⚠️ **One item needs action outside this repository:** the AI-crawler rules and the sitemap submission
(§2.1) — this repo's `robots.txt` is served from a path crawlers ignore.

**Batch 2 — Foundation** *(~1 day, unlocks everything else)*
§6.1 GitHub Actions build · §6.3 pin dependencies + commit `Gemfile.lock` · §6.2 html-proofer ·
§6.5 analytics

**Batch 3 — Performance** — ✅ **done except §3.4**
~~§3.1 external stylesheet~~ · ~~§3.2 drop KaTeX CSS~~ · ~~§3.5 self-host fonts~~ · ~~§3.3 jQuery
patched to 3.7.1~~ (kept by request) — **remaining:** §3.4 image optimisation (skipped by request)

**Batch 4 — Multi-language groundwork** *(~1 day, pays off twice)*
§8.1 normalise `lang` · §8.3 deduplicate templates · §8.2 `_data/i18n.yml` · §8.5 language-filtered
listings · §8.4 `ref` keys · §8.6 path-aware JS

**Batch 5 — Polish** — mostly done
~~§2.4 real `<img>` tags~~ · ~~§2.5 lazy loading~~ · ~~§5.3 accessibility~~ (except colour contrast) —
**remaining:** §4.2 dark mode · §7 content hygiene · colour contrast

---

## Status summary

| Section | State |
|---|---|
| §1 Bugs | ✅ complete |
| §2 SEO | ✅ complete (§2.1 needs an action in the `rya-sge.github.io` repo) |
| §3 Performance | ✅ except §3.4 image optimisation (skipped by request) |
| §4 CSS | ⬜ §4.2 dark mode and §4.3 normalize outstanding |
| §5 Templates & a11y | ✅ complete except colour contrast |
| §6 Build & tooling | ⬜ §6.1 CI, §6.2 html-proofer, §6.3 pinned deps, §6.5 analytics outstanding — ~~§6.4 done~~ |
| §7 Content hygiene | ⬜ outstanding |
| §8 Multi-language prep | 🟡 §8.1 §8.2 §8.3 §8.6 done — **remaining: §8.4 `ref` keys, §8.5 language-filtered listings** |

**Highest-value remaining work: §6.1** (a GitHub Actions build). Nothing currently validates the site
before it goes live — which is exactly how the §6.4 Liquid failure reached production.

Batches 1 and 2 give the best return per hour. Batch 4 is worth doing **even if the French site never
happens** — every item in it fixes something on the current site (§8.5 in particular fixes a live
mixed-language bug), which is why it's listed as groundwork rather than as speculative work.
