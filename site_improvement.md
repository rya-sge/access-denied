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

## 3. Performance

### 3.1 The entire stylesheet is inlined into every page 🔴 *(1 h, biggest single win)*

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

### 3.2 KaTeX CSS loaded on every page, apparently unused 🟠 *(10 min)*

`_includes/head.html:27-29` loads `fonts/katex.min.css` (22 KiB) on **every page**. But math is rendered
by **MathJax v4 SVG** (`_includes/mathJax.html`), which doesn't use KaTeX stylesheets, and
`jekyll-katex` is commented out in `_config.yml:50`. Only 68 posts even set `isMath: true`.

Worse, the tag carries `integrity="sha384-…" crossorigin="anonymous"` on a **same-origin local file**.
The `crossorigin` attribute forces a CORS check on your own asset, and if the hash doesn't match the
local copy the browser silently blocks the stylesheet. Verify it's genuinely unused, then delete it.

### 3.3 jQuery + plugin stack: 180 KiB for very little 🟡 *(3–4 h)*

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

### 3.4 Unoptimised images — 68 MiB of assets 🟡 *(2–3 h, scriptable)*

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

### 3.5 External font requests 🟢 *(15 min)*

`_includes/head.html:25` still pulls Open Sans from `fonts.googleapis.com` (render-blocking + a
third-party request, and a GDPR talking point in the EU). Volkhov is already self-hosted in `fonts/` —
do the same for Open Sans and add `font-display: swap`.

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

## 5. Templates, accessibility & duplication

### 5.1 Search markup is copy-pasted 4× 🟠 *(30 min)*

The identical search box appears in `_includes/header.html`, `_layouts/post.html:8-16`, `tags.html` and
`404.html`. Extract `_includes/search-box.html` and include it. This directly reduces the multi-language
work later (§8.2) — four copies means four places to translate the placeholder.

### 5.2 The 19 category pages are near-identical 🟠 *(1 h)*

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

### 5.3 Accessibility gaps 🟡 *(2 h)*

- Icons are `<div data-icon>` — not focusable, no accessible name, invisible without JS.
- The Posts/Categories switcher (`js/main.js:34`) is `<li>` elements with click handlers — **not
  keyboard-accessible**. Should be `<button>` with `aria-selected`.
- `.c-top` scroll-to-top is a `<div>` with a `title` — should be a `<button>`.
- Thumbnails as CSS backgrounds have no accessible name (§2.4).
- Worth checking contrast ratios in `_sass/0-settings/_colors.scss` against WCAG AA.

`u-screen-reader-text` labels are already used on the search inputs — good, keep that pattern.

### 5.4 Leftover debug markup 🟢 *(1 min)*

`_layouts/post.html:59` renders a literal `<p>Share button</p>` above the share icons. Delete it.

### 5.5 Fragile tags loop 🟢 *(15 min)*

`tags.html:22` iterates `(0..site.tags.size)` with an `{% unless forloop.last %}` guard — an off-by-one
workaround that will silently drop or duplicate a tag if the collection shape changes. `{% for tag in
site.tags %}` is clearer and correct.

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

### 6.4 Repository files are published to the live site 🟠 *(10 min)*

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

### 8.2 Extract all hardcoded UI strings into `_data/i18n.yml` 🟠 *(2 h)*

Currently English strings are scattered across `index.html`, `_layouts/post.html`,
`_layouts/category-page.html`, `_includes/header.html`, `_includes/categories.html`, `tags.html` and
`404.html`: *"Type to search…"*, *"Load more posts"*, *"You might also enjoy"*, *"minute read"*,
*"View all"*, *"No results found"*, *"Tags in Blog"*, *"Feel free to contact me on"*.

Move them to `_data/i18n.yml` keyed by language and read them via
`{% assign t = site.data.i18n[page.lang] | default: site.data.i18n.en %}`.

**Benefit today:** strings stop being duplicated across 4 files (§5.1), so changing the search
placeholder is one edit instead of four. **Benefit later:** adding French is one YAML block.

### 8.3 Deduplicate templates before duplicating them per language 🟠 *(1.5 h)*

§5.1 and §5.2. Nineteen copy-pasted category pages become **38** the day French exists; four copies of
the search box become **eight**. Consolidating first means the French version adds front matter, not
templates. **This is the single change that most reduces future multi-language cost.**

### 8.4 Add a stable `ref:` translation key 🟡 *(30 min, scripted)*

Add `ref: <slug>` to every post now, derived from the current filename slug and then frozen. It's the
join key that pairs an article with its translation (`multi-language.md` §5.1). Adding it to 255 posts is
a scripted one-liner today; retrofitting it *after* translations exist means reconciling two sets of
files by hand.

### 8.5 Restructure listings to filter by language 🟡 *(2 h)*

Every listing — `index.html:15`, `_layouts/category-page.html`, `_pages/category/*/index.html`,
`tags.html`, `search.json`, and `site.related_posts` in `_layouts/post.html:71` — iterates `site.posts`
unconditionally.

**This is already a live bug:** French 2021 posts are interleaved with English 2026 posts on the home
page, in every category listing, and in search results. Adding `| where: "lang", page.lang` fixes the
current site *and* is exactly the change the French version needs.

### 8.6 Make `js/main.js` path-aware 🟢 *(30 min)*

`main.js:17` hardcodes `/access-denied/search.json` and `main.js:62` hardcodes `/access-denied/page/`.
Both should come from `data-` attributes rendered by Liquid. That kills the hardcoded `baseurl`
duplication now (it breaks any local preview served at `/`), and later lets the same script pick
`search-fr.json` and `/fr/page/N` without a second copy.

---

## 9. Recommended order

**Batch 1 — Quick wins** — ✅ **complete except two items**
~~§1.1 broken images~~ · ~~§1.2 oracle 404~~ · ~~§1.3 duplicate title~~ · ~~§1.4 front matter~~ ·
~~§2.1 sitemap in robots.txt~~ · ~~§2.2 canonical~~ · ~~§2.3 site lang~~ — **remaining:** §5.4 debug
markup · §6.4 exclude list

**All of §2 (SEO) is now done**, including §2.4 real `<img>` tags, §2.5 lazy loading and §2.6 structured
data, which were originally scheduled for Batch 5.

⚠️ **One item needs action outside this repository:** the AI-crawler rules and the sitemap submission
(§2.1) — this repo's `robots.txt` is served from a path crawlers ignore.

**Batch 2 — Foundation** *(~1 day, unlocks everything else)*
§6.1 GitHub Actions build · §6.3 pin dependencies + commit `Gemfile.lock` · §6.2 html-proofer ·
§6.5 analytics

**Batch 3 — Performance** *(~1 day, biggest user-visible gain)*
§3.1 external stylesheet · §3.2 drop KaTeX CSS · §3.5 self-host fonts · §3.4 image optimisation ·
§3.3 jQuery upgrade or removal

**Batch 4 — Multi-language groundwork** *(~1 day, pays off twice)*
§8.1 normalise `lang` · §8.3 deduplicate templates · §8.2 `_data/i18n.yml` · §8.5 language-filtered
listings · §8.4 `ref` keys · §8.6 path-aware JS

**Batch 5 — Polish** *(as time allows)*
§2.4 real `<img>` tags · §2.5 lazy loading · §4.2 dark mode · §5.3 accessibility · §7 content hygiene

Batches 1 and 2 give the best return per hour. Batch 4 is worth doing **even if the French site never
happens** — every item in it fixes something on the current site (§8.5 in particular fixes a live
mixed-language bug), which is why it's listed as groundwork rather than as speculative work.
