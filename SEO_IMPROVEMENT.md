# SEO & AI-Answer-Engine Audit — `access-denied`

Audit date: **2026-08-19** · Scope: `_config.yml`, `_layouts/`, `_includes/`, `robots.txt`, the build pipeline, and all **269** files in `_posts/`.

This document does **not** re-propose anything already marked ✅ in `site_improvement.md` (§2 SEO, §3 performance, §5 templates) and does **not** re-propose analytics (§6.5, declined). It covers what is still open, plus a topic that document never addressed: **how this site is consumed by ChatGPT, Perplexity, Claude and Google AI Overviews**, which is a different problem from ranking in the ten blue links.

---

## 0. Summary

| # | Area | Finding | Impact | Effort |
|---|------|---------|--------|--------|
| 1 | Hosting | `robots.txt` is served from a path crawlers never read; no custom domain | 🔴 High | M |
| 2 | Crawler policy | AI **search** bots are allowed only by accident (`User-agent: *`), never by name | 🔴 High | S |
| 3 | Freshness | ~~`last_modified_at` never set~~ — **✅ implemented 2026-08-19**, backfilled from git on 210 posts | 🔴 High | S |
| 4 | Structured data | 98 FAQ sections are bold paragraphs, not headings — no anchors, no outline, no TOC entries (`FAQPage` JSON-LD is **not** the answer, see §3.1) | 🟠 Med | M |
| 5 | Content loss | 3 articles are unpublished (bad filenames), 1 has an invalid filename date. ~~1 duplicate-title stub~~ — **✅ fixed 2026-08-19** | 🟠 Med | S |
| 6 | Extractability | No answer-first summary, no visible author/updated line, no `<time datetime>` | 🟠 Med | M |
| 7 | Internal linking | ~~`site.related_posts` is "4 most recent"~~ — **✅ implemented 2026-08-19**; 28 posts still have zero in-body internal links | 🟠 Med | M |
| 8 | Category pages | ~~20 landing pages with no `<h1>`, no description, no intro text~~ — **✅ implemented 2026-08-19** | 🟠 Med | S |
| 9 | Metadata quality | 126 descriptions exceed the SERP snippet width, 27 are too thin, 2 empty, 3 posts have no category | 🟡 Low | M |
| 10 | Discovery | No IndexNow, no Bing verification file in the repo, no author/about page | 🟡 Low | S |

**What is already good** (do not touch): `jekyll-seo-tag` + `jekyll-sitemap` + `jekyll-feed` are wired correctly, canonical and `og:` tags are emitted once, `BreadcrumbList` JSON-LD is in place, every post has `title`/`date`/`lang`/`locale`/`description`/`image`, all 711 in-article images resolve and are lazy-loaded, fonts are self-hosted, CSS is an external cacheable file, and the Actions build fails on a Liquid error before it can ship. That baseline is better than most Jekyll blogs.

---

## 1. Hosting and crawl control (the structural blocker)

### 1.1 `robots.txt` is not the one crawlers read — still open

The file already documents this honestly. The consequence is worth restating in SEO terms: **every rule in `robots.txt` is currently inert**, including the AI-training opt-outs. Crawlers fetch `https://rya-sge.github.io/robots.txt`, which is generated from the `rya-sge.github.io` user-page repository.

Two ways out, in order of preference:

1. **Custom domain** (e.g. `blog.example.com` or `accessdenied.example`). Beyond fixing `robots.txt`, this is the single highest-leverage SEO change available to this site:
   - `github.io` is on the [Public Suffix List](https://publicsuffix.org/), so `rya-sge.github.io` gets no authority benefit from any other `*.github.io` site — but the blog also gains nothing as a *brand entity*. Google, and more visibly ChatGPT and Perplexity, resolve sources to named entities. "AccessDenied" on its own domain is citable; `rya-sge.github.io/access-denied` reads as a personal scratch space and is frequently rendered as a bare URL rather than a source name.
   - It removes the `/access-denied` path prefix from every URL, which shortens every citation string.
   - It makes `/llms.txt`, `/robots.txt`, IndexNow key files and `/.well-known/` reachable at the host root.
   - Migration cost is real but bounded: set `url`, empty `baseurl`, keep `url_complet` as an alias, add a `CNAME` file, and add `jekyll-redirect-from` (the Actions build runs without safe mode, so any gem is allowed). GitHub serves the old `github.io` URLs with a 301 to the custom domain automatically, so link equity is preserved.

2. **If the domain is not on the table**: copy the AI rules into the `rya-sge.github.io` repo's root `robots.txt` verbatim. Keep this file in place as the source of truth and add a line to the header saying which repo it is mirrored into, so the two cannot drift.

Either way, submit `https://rya-sge.github.io/access-denied/sitemap.xml` manually in **Google Search Console** and **Bing Webmaster Tools** as a URL-prefix property on `https://rya-sge.github.io/access-denied/` — a domain property will mix in every other project site on that host.

> Note: `googlebed50df54eff8961.html` and `BingSiteAuth.xml` are referenced in `robots.txt` as verified, but neither file exists in this repository. If verification currently rests on files living in the user-page repo, they are one unrelated commit away from being deleted. Prefer the meta-tag or DNS verification method, or check the files in here.

### 1.2 Name the AI search crawlers explicitly — highest ROI for ChatGPT/Perplexity

This is the crux of the "indexing in ChatGPT / Perplexity" question, and it hinges on a distinction the current file does not make: **training crawlers and answer/search crawlers are different user-agents**. Blocking the first does not block the second, and allowing the second is what puts the blog into answers with a citation link.

| Engine | Training crawler | Search/answer crawler | User-triggered fetch |
|--------|------------------|------------------------|----------------------|
| OpenAI (ChatGPT) | `GPTBot` | `OAI-SearchBot` | `ChatGPT-User` |
| Perplexity | — (`PerplexityBot` also feeds the index) | `PerplexityBot` | `Perplexity-User` |
| Anthropic (Claude) | `ClaudeBot` | `Claude-SearchBot` | `Claude-User` |
| Google | `Google-Extended` | `Googlebot` | — |
| Apple | `Applebot-Extended` | `Applebot` | — |
| Microsoft (Copilot) | — | `bingbot` | — |

The current policy — block training, allow everything else via `User-agent: *` — is coherent and worth keeping. But it is **implicit**: the answer crawlers are allowed only because they fall through to the wildcard. One future tightening of that wildcard silently removes the site from ChatGPT and Perplexity answers. Make the intent explicit:

```
# --- AI answer engines: indexing and citation ALLOWED -----------------
# These crawlers build the retrieval index that ChatGPT Search, Perplexity
# and Claude cite from. Allowing them is what makes an article appear as a
# named, linked source in an answer. They are distinct from the training
# crawlers blocked below.
User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: bingbot
Allow: /

# --- AI training corpora: BLOCKED ------------------------------------
# (unchanged — GPTBot, ClaudeBot, Google-Extended, Applebot-Extended,
#  Meta-ExternalAgent, Meta-ExternalFetcher, Amazonbot)
```

Two trade-offs to decide consciously, not by default:

- **`Google-Extended`** is currently blocked. Google states it does not affect Search ranking, and AI Overviews are built from `Googlebot` content — that part of the file's comment is accurate. What it *does* cost is grounding in the Gemini apps. If the goal is maximum AI visibility, this is the one block worth reconsidering; if the goal is "no training on my writing", keep it.
- **`GPTBot`** blocked means the content will not be absorbed into model weights, so ChatGPT will not "know" the blog from memory — it will only reach it through `OAI-SearchBot` retrieval, and only when it decides to search. That is exactly the trade the current file makes on purpose. Keeping it is defensible; just know it caps the ceiling.

An `Allow:` directive for a bot that is not otherwise disallowed is a no-op in strict RFC 9309 terms, but every major crawler honours it and it documents intent in the one file everyone reads. Note also that the site already has an article on this exact subject (`2025-09-01-ai-bot-crawler.md`) — the policy here and the claims there should be consistent.

### 1.3 IndexNow for Bing (cheap, and it feeds ChatGPT)

ChatGPT's web search leans heavily on Bing's index; Perplexity blends its own crawler with third-party indices. Getting into Bing quickly therefore has a direct AI-visibility payoff. IndexNow is a single POST per published URL:

```yaml
# .github/workflows/pages.yml — new step after deploy
- name: Ping IndexNow
  if: github.ref == 'refs/heads/master'
  run: |
    curl -sS -X POST https://api.indexnow.org/indexnow \
      -H 'Content-Type: application/json' \
      -d '{"host":"rya-sge.github.io",
           "key":"<32-char-key>",
           "keyLocation":"https://rya-sge.github.io/access-denied/<32-char-key>.txt",
           "urlList":["<new or updated URLs>"]}'
```

The key file may live under the project path as long as `keyLocation` points at it — which is precisely the escape hatch a project site needs. Deriving `urlList` from `git diff --name-only` over `_posts/` on the pushed commit keeps it to changed articles.

---

## 2. Freshness signals — the biggest quick win

### 2.1 `last_modified_at` is never populated — ✅ IMPLEMENTED (2026-08-19)

46 posts carry a `last-update:` key, only **4** of which hold an actual date; the rest are empty. Nothing in the site reads it. Meanwhile:

- `jekyll-seo-tag` reads **`last_modified_at`** to emit `dateModified` in the `BlogPosting` JSON-LD. Absent it, `dateModified` is missing entirely.
- `jekyll-sitemap` reads **`last_modified_at`** for `<lastmod>`. Absent it, it falls back to the file's git-less mtime behaviour and the sitemap tells crawlers nothing useful about what changed.
- Nothing renders an "updated" date to the reader.

This matters disproportionately for this archive because a large share of it is *evergreen but perishable* — a 2021 Mimikatz article, a 2022 Foundry tutorial, an ISO 20022 explainer. Both Google and the answer engines discount undated or stale-looking technical content, and answer engines in particular prefer a source that states when it was last checked.

**What was implemented:**

1. **Backfilled from git history** on all 269 files in `_posts/`. A commit counts as a modification only when it changed the article **body, title or description** — front-matter-only commits (the July 2026 `lang`/`locale` pass, the `oracle` category fix) and commits that only rewrote link/image *targets* (the `\assets\…` → `/assets/…` repair that touched 56 articles without changing a word) are skipped, because stamping `dateModified` on them would advertise a content update that never happened. Where a post already had a real `last-update:` value, the later of the two dates wins. The date is omitted entirely when it is not newer than the publication date, so nothing is ever labelled "updated" on the day it was published.

   Result: **210 posts stamped, 59 left unstamped** (49 never substantively edited after publication, 10 without usable history). Date spread: 2026 → 106, 2025 → 45, 2024 → 35, 2022 → 16, 2021 → 7, 2023 → 1. All 46 legacy `last-update:` keys (42 of them empty) were removed.

2. **Rendered in the article header** (`_layouts/post.html`), replacing the bare `<span>`, which was also missing machine-readable markup:

```liquid
<div class="c-article__date">
  <time datetime="{{ page.date | date_to_xmlschema }}">
    {{ page.date | date: t.date_format }}
  </time>
  {% if page.last_modified_at %}
  <span class="c-article__updated">
    · {{ t.updated_on }}
    <time datetime="{{ page.last_modified_at | date_to_xmlschema }}">
      {{ page.last_modified_at | date: t.date_format }}
    </time>
  </span>
  {% endif %}
</div>
```
`updated_on` was added to both language blocks in `_data/i18n.yml` (`"Updated"` / `"Mis à jour le"`), and `_sass/5-components/_article-page.scss` now styles `time` alongside `span` so the date keeps its appearance.

3. **`update-article` now stamps it.** The skill sets `last_modified_at` to today whenever an edit changes the body, title or description — and explicitly not for mechanical edits. Freshness is now a by-product of normal work rather than a chore.

`jekyll-seo-tag` (`dateModified` in the JSON-LD) and `jekyll-sitemap` (`<lastmod>`) both read `last_modified_at` natively, so no configuration change was needed for either.

> `<time datetime="…">` matters on its own: the listing cards already use it, the article header does not, so the single most important date on the page is the one machines cannot parse reliably.

---

## 3. Structured data

### 3.1 The 98 FAQ sections — markup, not schema — ⚠️ REVISED (2026-08-19)

98 posts end with a `## Frequently Asked Questions` section in a rigidly consistent format (`**Q: …**` followed by answer paragraphs) because the `create-article` skill enforces it. That is a hand-written Q&A corpus, and the obvious move is to emit `FAQPage` JSON-LD for it. **The first version of this document ranked that as the highest-value schema left. That ranking was wrong, and it is corrected here.**

**Google no longer renders FAQ rich results for a site like this one.** In **August 2023** Google restricted the FAQ rich result to well-known government and health sites, which already put the expandable Q&A accordion out of reach for a personal technical blog; the feature was **deprecated outright in May 2026**. Emitting `FAQPage` today buys no SERP feature whatsoever.

It is not *harmful*: `FAQPage` remains a valid schema.org type, and Google's stated position is that structured data it does not use for a feature is ignored rather than penalised. So markup already in place can stay.

**The remaining argument is AI retrieval, and it is weaker than it is usually presented.** There is no published evidence that `OAI-SearchBot` or `PerplexityBot` weight `FAQPage` JSON-LD. Those pipelines fetch and parse *rendered HTML*; where they read schema.org at all, it is mostly for title, date and author. The claim that answer engines "prefer FAQ schema" is widely repeated in SEO commentary and poorly evidenced. Meanwhile the cost is real: a Ruby generator parsing markdown, stripping links, code fences and MathJax out of answer text, with one malformed answer producing invalid JSON-LD across 98 pages at once.

**Revised recommendation: optional, low priority.** Emit it only if the generator stays trivial, and treat it as cheap insurance rather than a win. It is no longer a Tier 1 item.

#### What to do instead — promote the questions to real headings

The thing that demonstrably works is the *HTML*, and this is where the effort belongs.

Today a question renders as `<p><strong>Q: What exactly is forged in a Golden Ticket…</strong></p>`. That gives it:

- no heading element, so it is invisible to the document outline every extractor builds;
- no `id`, so no anchor — a question cannot be linked to, and Google cannot deep-link a passage to it;
- no entry in the article TOC (`_includes/toc.html` only collects headings);
- no clean boundary, so a chunker has to guess where the answer ends.

Promoting each question to an `###` heading fixes all four at once and depends on no vendor honouring any schema type:

```markdown
### What exactly is forged in a Golden Ticket, and what key makes it possible?

A Golden Ticket is a forged Ticket Granting Ticket (TGT). It is possible because…
```

Note that the `Q:` prefix goes away with the bold: as a heading, the question is self-evidently a question. Keep the answer as plain paragraphs — no `A:` prefix.

This is two pieces of work:

1. Change the FAQ convention in `create-article` (and `create-article-eli10` / `create-article-talk`, which inherit it) so new articles use `###` headings.
2. A mechanical pass over the 98 existing FAQ sections. The format is regular enough to script — `^\*\*Q:\s*(.+?)\*\*$` → `### \1` — but the result should be spot-checked, since a handful of answers contain their own bold text.

Worth noting for the TOC: 98 articles gaining 5+ `h3` entries will lengthen it. Check `_includes/toc.html`'s heading-level configuration and cap it at `h2` for the FAQ section if the result is unwieldy.

### 3.2 Upgrade `BlogPosting` → `TechArticle` where it fits

`jekyll-seo-tag` hardcodes `BlogPosting`. For a security/cryptography reference archive, `TechArticle` is the more precise type and carries `dependencies` / `proficiencyLevel`. Because seo-tag's type is not configurable per page, the practical route is a small additional JSON-LD block (schema.org tolerates multiple nodes; use `@id` to tie them together) carrying the fields seo-tag omits and that answer engines actually use:

- `about` / `mentions` — the entities the article covers (Kerberos, ERC-4337, ISO 20022 …). This is what lets an engine match a query to the page by *topic* rather than by string.
- `citation` — the article already averages ~18 external references; exposing them as `citation` nodes is a strong quality signal.
- `articleSection`, `keywords`, `wordCount`, `inLanguage`, `proficiencyLevel: "Expert"`.
- `isPartOf` pointing at the category `CollectionPage`.

A modest version, driven entirely by existing front matter, costs one include and no new front-matter fields:

```liquid
{%- comment -%} _includes/article-schema.html {%- endcomment -%}
{% if page.layout == 'post' %}
{% assign site_root = site.url | append: site.baseurl %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "@id": {{ site_root | append: page.url | append: '#article' | jsonify }},
  "headline": {{ page.title | jsonify }},
  "description": {{ page.description | jsonify }},
  "inLanguage": {{ page.locale | default: page.lang | jsonify }},
  "datePublished": {{ page.date | date_to_xmlschema | jsonify }},
  {% if page.last_modified_at %}"dateModified": {{ page.last_modified_at | date_to_xmlschema | jsonify }},{% endif %}
  "articleSection": {{ page.categories | first | jsonify }},
  "keywords": {{ page.tags | join: ', ' | jsonify }},
  "wordCount": {{ page.content | number_of_words }},
  "proficiencyLevel": "Expert",
  "author": { "@type": "Person", "name": {{ site.author | jsonify }},
              "url": {{ site_root | append: '/about/' | jsonify }} },
  "mainEntityOfPage": {{ site_root | append: page.url | jsonify }}
}
</script>
{% endif %}
```

### 3.3 Category pages have no schema and no words — ✅ IMPLEMENTED (2026-08-19)

The 20 pages under `_pages/category/` were front matter only: `title: zkp`, a `category:` key, a permalink. What rendered was a bare grid of cards. Four problems compounded:

- **No `<h1>` at all.** `_layouts/category-list.html` rendered the search header and went straight to the grid, so the hub pages for the site's best topics had no heading element.
- **No `description`**, so `jekyll-seo-tag` fell back to the site description and all 20 pages shipped the *same* meta snippet.
- **Lowercase display titles** — `zkp`, `iso20022`, `eli10`.
- **No prose**, so a hub with 130 links and zero sentences is thin content to Google and unusable to an answer engine, which cannot summarise a list of titles.

**What was implemented.**

`_layouts/category-list.html` now renders an intro block and structured data:

```liquid
<section class="c-category-intro">
  <h1 class="c-category-intro__title">{{ page.title }}</h1>
  {{ content }}
  <p class="c-category-intro__count">{{ cat_posts | size }} {{ t.category_posts_count | downcase }}</p>
</section>
```

The count comes from `site.categories`, so no page hardcodes a number that would go stale on the next post. Below the grid the layout emits **`CollectionPage` + `ItemList`** JSON-LD naming every post on the page in order, with `numberOfItems` and `itemListOrder`. `jekyll-seo-tag` emits neither — it only knows `WebPage` and `BlogPosting`. Every post is listed rather than a top-N slice, because the grid is not paginated and the markup must describe what is actually on the page.

All 20 pages were rewritten with a proper display title, a 120-160 character `description`, and two paragraphs of intro prose written from the posts each category actually contains:

| Was | Now | Posts |
|-----|-----|-------|
| `ai` | Artificial Intelligence | 14 |
| `blockchain` | Blockchain | 130 |
| `blockchainBestOf` | Blockchain — Best Of | 12 |
| `cryptography` | Cryptography | 60 |
| `defi` | DeFi | 27 |
| `eli10` | Explained for a 10-Year-Old | 8 |
| `ethereum` | Ethereum | 51 |
| `finance` | Finance | 3 |
| `ISO 20022` | ISO 20022 | 25 |
| `linux` | Linux | 8 |
| `network` | Networks and Protocols | 40 |
| `oracle` | Oracles | 1 |
| `programmation` | Programming | 48 |
| `rfc` | RFC | 3 |
| `security` | Security | 75 |
| `solana` | Solana | 9 |
| `solidity` | Solidity | 41 |
| `tryhackme` | TryHackMe | 4 |
| `web` | Web Development and Security | 8 |
| `zkp` | Zero-Knowledge Proofs | 21 |

Every description is now ≤ 160 characters and unique. Titles avoid `&` (written as "and") — a raw ampersand in front matter ends up escaped inconsistently between the `<h1>` and the meta tags.

Styling lives in a new `_sass/5-components/_category-intro.scss`, imported from `_sass/main.scss`.

The `create-website-category` skill was updated to match: it carried the pre-refactor template (the old inline card markup with `background-image` thumbnails, removed in `site_improvement.md` §2.4) and a canonical key list missing `eli10`, `finance`, `oracle` and `rfc`. It now documents the `category-list` front matter, requires `description` and intro prose, and explains why.

**Still open on these pages:** they have no `lang` front matter, so the UI strings resolve to English even on categories whose posts are largely French (`web` is 7 French posts out of 8). That is a translation question rather than an SEO one, and it belongs with the multi-language work in `multi-language.md`.

## 4. Content-level fixes

### 4.1 Articles that are not published at all — 3 lost posts

Jekyll requires `YYYY-MM-DD-slug.md`. These three do not have it and are silently dropped:

- `_posts/Blockchain downtime.md`
- `_posts/permit.md`
- `_posts/The Main Vulnerabilities When Using ECDSA Signatures in Smart Contracts.md`

The last two also have no front matter at all. `feedback.md` §1–2 flagged this; it is still open. Either rename them with a date prefix and add front matter, or move them to `draft/`. Right now they are neither published nor drafts — just invisible.

Also: `_posts/2022-20-12-foundry-tutorial-nft.md` has **month 20** in its filename. It builds only because the `date:` in front matter overrides it, but it is a trap for any tool that parses filenames (including the ones in `_plugins/`). Rename to `2022-12-20-…`. And `_posts/2024-11-4-TLS1.3-overview.md` needs its day zero-padded.

### 4.2 Duplicate title / thin stub — ✅ IMPLEMENTED (2026-08-19)

`_posts/2024-03-28-ethereum-stacking.md` — 34 words, empty description, empty categories, `exclude: yes` — carried **the same `title` as `2024-03-28-ethereum-staking.md`**. `exclude:` only hid it from the home listing; it was still live, still in `sitemap.xml`, still in `search.json`, and still competing with the real article for its own title, while its entire content was a link to the article it competed with. The slug was a typo (`stacking` for `staking`) that had been papered over with a manual pointer page.

**What was implemented.** The stub is deleted, and the real article now declares the old URL:

```yaml
redirect_from:
  - /2024/03/28/ethereum-stacking/
```

`jekyll-redirect-from` was added to `_config.yml`'s `plugins:` list. No `Gemfile` change: it is a dependency of the pinned `github-pages` gem, so listing it separately would fight the pin (per the Gemfile's own note). The stale row was also dropped from `article_list.md`.

#### Verified against GitHub Pages specifically

The plugin is not merely "probably fine" here — four things were checked, because a project site under a `baseurl` is exactly where redirect plugins tend to go wrong:

1. **It is a supported GitHub Pages plugin.** `https://pages.github.com/versions.json` lists `jekyll-redirect-from: 0.16.0` under `github-pages: 232` — the exact version this repo pins. It therefore runs under the **classic safe-mode build** as well as the Actions build, so the redirect keeps working whichever pipeline is live (the Actions source switch in `.github/workflows/pages.yml` is still a manual step).
2. **It is `baseurl`-safe.** `RedirectPage#set_paths` builds the target with Jekyll's own `absolute_url` filter, which prepends `site.url` **and** `site.baseurl`. The emitted target is `https://rya-sge.github.io/access-denied/2024/03/28/ethereum-staking/`, not a root-relative path that would 404 on a project site. The `from` path is a `permalink`, so the page is written to `_site/2024/03/28/ethereum-stacking/index.html` and served under `/access-denied/` like everything else.
3. **It will not re-enter the sitemap.** Generated redirect pages carry `"sitemap" => false` in `RedirectPage::DEFAULT_DATA`, which `jekyll-sitemap` honours. The page also ships `<meta name="robots" content="noindex">` and a `<link rel="canonical">` pointing at the surviving article, so it cannot recreate the duplicate-title problem it was introduced to solve.
4. **No layout collision.** The plugin injects its own `redirect` layout; this repo has no `_layouts/redirect.html` to shadow it.

**The one honest caveat:** GitHub Pages cannot serve a real HTTP 301 for a project site — there is no server configuration to hook. The generated page is a **client-side redirect**: a zero-delay `<meta http-equiv="refresh">`, a `location=` script, and a canonical link. Google treats a zero-delay meta refresh as a redirect and passes signals through it, so this is the correct and standard solution on GitHub Pages, but it is not a 301. A real 301 only becomes available with a custom domain fronted by a CDN (§1.1).

### 4.3 Three posts with no category, two with no description

- No `categories:` → no breadcrumb (`_includes/breadcrumbs.html` degrades to a 2-level crumb), absent from every category hub, orphaned in the internal link graph: `2025-05-30-credit-default-swap-overview.md`, `2025-09-01-ai-bot-crawler.md`, `2024-03-28-ethereum-stacking.md`.
- Empty `description:` → site-wide fallback: `2025-11-07-solana-staking-overview.md`, `2024-03-28-ethereum-stacking.md`.

### 4.4 Meta description lengths

Across 267 posts: average 162 characters, **126 exceed 170** (max 337), **27 are under 80** (min 41). Google renders roughly 150–160 characters on desktop and less on mobile; the tail of a 337-character description is never seen, and the tail is usually where the specifics live. The 27 short ones — mostly 2021-era French posts — waste the slot entirely.

This is not worth a bulk rewrite. Worth doing:
- Trim the ~20 worst offenders (>250 chars) so the front-loaded sentence survives.
- Rewrite the 27 thin ones when those posts are next touched.
- Add a length guard to the `create-article` / `update-article` skills: target 120–160 characters, front-load the specific claim.

### 4.5 Thin content

12 posts are under 400 words. For a technical archive this is the tail that drags average quality down in a site-wide quality assessment, and none of them will ever rank. Options per post: expand (several are genuinely useful notes that deserve 800 words), merge into a related article with a redirect, or leave them — but do not let the count grow.

### 4.6 Duplicate `<h1>` — ✅ IMPLEMENTED (2026-08-19), and the original count was wrong

The first version of this document reported **13 posts** opening with a body-level `# Heading` while `_layouts/post.html` already renders the title as `<h1 class="c-article__title">`. That number came from a regex that did not exclude fenced code blocks, so **9 of the 13 were false positives** — `#` comments inside `bash`, `python` and `yaml` snippets, which are not headings at all:

```bash
# Generate the key      <- counted as an H1 by the naive scan
openssl genpkey ...
```

Re-scanned with fences, indented blocks and front matter excluded, the real figure was **4 published posts**:

| Post | Heading | Fix |
|------|---------|-----|
| `2022-10-29-solidity-version` | `# Reference` | → `## Reference` |
| `2023-06-03-solidity-smart-contracts-doc` | `# Reference` | → `## Reference` |
| `2023-07-20-metamask-secret` | `# Introduction` (line 2) | → `## Introduction` |
| `2025-09-27-seal-overview` | `# Reference` | → `## Reference` |

All four were demoted to `##`, which is the level every other section in those posts already uses — no deeper shift was needed, since none of them had subsections hanging off the stray H1. **No published post now has a second `<h1>`.**

Two files still contain a body H1: `permit.md` and `The Main Vulnerabilities When Using ECDSA Signatures in Smart Contracts.md`. Both are unpublished (no front matter, no date prefix — see §4.1), and in both the H1 is currently the only title the document has, so removing it before they get front matter would lose information. Fix it when they are published, not before.

Noted while in there, not fixed: the archive is split between `## References` (124 posts) and `## Reference` (57). Renaming would change the heading anchors, so it is a deliberate decision rather than a cleanup, and it belongs with a TOC/anchor pass rather than here.

### 4.7 Alt text — ✅ IMPLEMENTED (2026-08-19)

712 in-article images, **17 with empty alt** across 7 posts. All 17 now carry a descriptive sentence.

This matters more here than the raw count suggests: the figures on this blog are architecture diagrams, protocol schemas, terminal output and mindmaps, so the alt text is frequently the only description of the figure that a screen reader, a text-only crawler or an answer engine ever gets. A caption repeat would have been worthless — each was written from what the figure actually shows.

The 17, by article:

| Article | Images | Written from |
|---------|--------|--------------|
| `2022-04-22-cipher-block-chaining-cbc` | 2 | the CBC encryption/decryption schemas — French alt, matching the article |
| `2022-04-22-counter-mode-ctr` | 2 | the CTR keystream construction, French alt |
| `2022-04-22-electronic-codebook-ecb` | 2 | the ECB independent-block schemas, French alt |
| `2023-06-03-solidity-smart-contracts-doc` | 7 | the Surya `graph` / `ftrace` / `describe` / `inheritance` / `parse` outputs, plus the Solgraph and sol2uml examples |
| `2024-02-14-solidity-interview-question-rareskills` | 1 | the TWAP formula, read from the image itself |
| `2025-01-13-chainlink-deco` | 2 | the article's own description of the DECO flow and the proxy/provenance handshake |
| `2025-10-29-aztec-architecture-overview` | 1 | the mindmap PNG, read and described branch by branch |

Where the image could be fetched it was read before being described, rather than guessed from the filename. Two of the Chainlink images return an error page to a non-browser client, so those two were written from the surrounding prose instead.

**Regression guard.** A CI step now fails the build on any `![](…)` in `_posts/`:

```yaml
- name: Check every article image has alt text
  run: |
    if grep -rnE '!\[[[:space:]]*\]\(' _posts/; then
      echo "::error::the article images listed above have no alt text"
      exit 1
    fi
```

Note that `html-proofer` keeps `--ignore-empty-alt`, deliberately. An empty alt is the *correct* markup for a decorative image — the category thumbnails in `_includes/categories.html` sit inside a link that already carries the category name, and repeating it would only add noise for a screen reader. The markdown-level check above catches the case that actually matters without forcing a wrong fix on the decorative one.

`create-article` gained an "Alt text is mandatory" section (with the good/bad examples and a 60–200 character target), and `update-article` now requires alt text on any figure it adds or replaces.

**Still open:** 60 images have an alt shorter than 10 characters (`schema`, `result`, `mindmap`). They pass the check but say almost nothing. Worth improving opportunistically, as those articles are next touched, rather than in one pass.

## 5. Internal linking and site architecture

### 5.1 "You might also enjoy" is not related — it is recent — ✅ IMPLEMENTED (2026-08-19)

`_layouts/post.html` iterates `site.related_posts`. Without the `classifier-reborn` LSI dependency (which is not installed, and which GitHub Pages never allowed), **Jekyll's `related_posts` returns the 10 most recent posts**, not related ones. Every article therefore links to the same four recent posts, and a 2021 Linux article recommends a 2026 Centrifuge article.

That wastes the single best internal-linking surface on the site — 254 pages × 4 links.

**What was implemented.** The block now lives in `_includes/related-posts.html`, called from `_layouts/post.html` as `{% include related-posts.html limit=4 %}`. Candidates are drawn from the post's own categories and ranked in three tiers, most recent first within each:

| Tier | Rule |
|------|------|
| 2 | shares **2 or more tags** with this post |
| 1 | shares **exactly 1 tag** |
| 0 | shares no tag, but sits in one of the same categories |

Measured against the live archive: **171 of 266 posts fill all four slots from tag matches alone**, 164 have a top pick sharing at least two tags, and no post ends up with an empty block. Restricting candidates to same-category posts rather than scanning all 254 costs almost nothing — only **2 posts** have a strong (≥2 tag) match that lives outside their own categories while being under-filled.

Implementation notes, because Liquid makes this less obvious than it looks:

- **No `push` filter exists.** Results accumulate in `",url,url,"` strings — one per tier — which double as the de-duplication set (a post in two of this post's categories appears in the pool twice). They are concatenated best-first and resolved back to documents with `where: 'url'` at render time.
- **`and` / `or` have no precedence in Liquid and bind right to left**, so the tier test is an `elsif` chain of single comparisons. A combined `a == 2 and b >= 2 or a == 1 and b == 1` would silently evaluate as something else entirely.
- **One pass, not three.** Candidates are bucketed in a single loop over the pool (which averages 106 posts), rather than one pass per tier.
- **Tag matching is one `contains` per tag** against a comma-delimited string instead of a nested loop; the commas wrapping both needle and haystack are what stop `eth` from matching `ethereum`.
- **Pure Liquid, deliberately.** A `_plugins/` generator would rank more precisely, but it would render nothing at all if the site ever falls back to the classic GitHub Pages build, which ignores `_plugins/`.

Fixed at the same time: the old loop was wrapped in `{% if post.image %}`, so a related post without an image was computed and then silently dropped, leaving a gap in the row (`feedback.md` #11). The card now renders regardless and only the `<img>` is conditional. The date in each card is also a `<time datetime="…">` element.

### 5.2 28 posts with zero internal links

28 articles link out to external sources but never to another article on this blog. Given how much of the archive is thematically clustered (the SOS Windows/Linux series, the ISO 20022 series, the ZKP series), that is a lot of missed topical reinforcement. Both Google and answer engines use internal link structure to work out which page is the authority on a topic within a site.

Cheapest systematic fix: for each of the top 8 categories, designate one **pillar article**, and make every other article in that category link to it once in the opening section. The recent posts already do this well (the Windows persistence article opens with links to the two preceding articles in the series) — it is the 2021–2023 back catalogue that does not.

### 5.3 Series / cluster metadata — ✅ IMPLEMENTED (2026-08-19)

**What was implemented.** Eight series covering **53 posts**, declared in a new `_data/series.yml` and rendered by `_includes/series-nav.html` as a box under the article title, above the TOC.

| Series | Posts | Ordered | Evidence it is a series |
|--------|-------|---------|--------------------------|
| Windows and Active Directory Security | 3 | yes | the persistence article opens "The two previous articles in this series looked at…" and links both |
| GNU/Linux Security Primitives | 4 | yes | the adversary article opens "The preceding articles built up the twelve base and advanced security primitives…" |
| The ISO 20022 Message Sets | 25 | yes | the overview article *is* a map of the other 24 and links them in a table |
| RareSkills Solidity Interview Answers | 3 | yes | Medium → Hard → Advanced is a stated difficulty progression |
| The Centrifuge V3 Protocol | 4 | no | mutually cross-linked (one article links all three siblings) |
| Hardware Wallet and Firmware Security | 4 | no | mutually cross-linked, three of four link two siblings each |
| Cyfrin First Fight Write-Ups | 7 | no | contest numbering 38–44 |
| Web Application Hacking (WAH) | 3 | no | course numbering WAH10, WAH11, WAH18 |

**Ordered versus unordered is the design decision worth keeping.** Four of the eight groups are articles on one subject with no intended reading order — four independent studies of Centrifuge published the same day, write-ups of seven separate contests. Rendering "Part 1 of 4" over those would tell the reader to start where the author never chose, and would encode a false claim in the `position` field of the structured data. Those render as "4 articles in this series", newest first, with no numbering. `_data/series.yml` carries the flag per series:

```yaml
linux-sos:
  title: "GNU/Linux Security Primitives"
  ordered: true      # members carry series_order: 1..N, box says "Part N of M"

centrifuge:
  title: "The Centrifuge V3 Protocol"
  ordered: false     # no order exists, box says "4 articles in this series"
```

Ordering was taken from the articles themselves, never invented: the two SOS series state their order in prose, and the ISO 20022 order is the one the overview article's own table uses (overview, then the `head` envelope, then the 23 message sets in its listed sequence).

**What it buys.** Every article in a series now links to every sibling, which is the densest topical internal linking on the site — 53 posts × 3 to 25 links each, all within a topic cluster. It also replaces inference with a statement: the include emits a `CreativeWorkSeries` node with a `hasPart` array naming each member (and a `position` for ordered ones), so a crawler no longer has to guess from title prefixes that 25 pages are one work.

Supporting changes: `series_kicker` / `series_part` / `series_of` / `series_articles` added to both language blocks in `_data/i18n.yml`; a `_sass/5-components/_series.scss` component imported from `_sass/main.scss`; the current article renders as plain text rather than a link to itself, with `aria-current="true"`.

`create-article` gained a "Joining an article series" section covering key reuse, the contiguous `1..N` rule for ordered series, the prohibition on `series_order` in unordered ones, and the instruction to default a new series to `ordered: false`.

**Verified:** all 53 posts resolve to a key in `_data/series.yml`, every ordered series has a contiguous `1..N` with no gaps or duplicates, no unordered member carries a stray `series_order`, and no declared series is empty.

**Candidate not implemented:** the four ZKP vulnerability articles of 2026-06-19 (taxonomy, hacks history, cross-chain bridge failures, and the ELI10 version) are clearly one project, but they contain no cross-references and no ordering evidence, so grouping them would have meant inventing the relationship. Worth adding as `ordered: false` if that reading is right — it is a one-line change plus four front-matter keys.

## 6. Optimising for ChatGPT, Perplexity and Google AI Overviews

Answer engines do not rank pages; they retrieve **chunks** and cite the source they lifted them from. The optimisation target is therefore: *is any single passage of this article a complete, quotable, attributable answer to a question someone actually asks?* This archive is unusually well placed — long-form, source-cited, table-heavy, FAQ-terminated — and needs mostly presentation changes rather than content changes.

### 6.1 Answer-first opening (highest impact)

Most articles open with narrative context. Add a short **TL;DR / key-takeaways block** immediately after the `<h1>`, before the TOC: 3–5 bullets, each a self-contained factual claim, no pronouns referring back to the title. This is the passage an engine will quote. It also improves the human experience, which is the test that keeps this from being SEO theatre.

Wire it through front matter so it is structured, not prose:

```yaml
key_takeaways:
  - A Golden Ticket is a TGT forged with the stolen krbtgt key; the KDC accepts it because it keeps no record of issued tickets.
  - Rotating krbtgt twice, 10+ hours apart, is the only reliable remediation.
```

Rendered as a `<ul>` in a bordered box in `_layouts/post.html`. Add it to `create-article` so new articles carry it by default, and backfill the top ~30 articles by traffic.

### 6.2 Question-shaped headings

`##` headings currently read as topic labels ("What persistence means on a Domain Controller" is good; "Golden Ticket" is not). Retrieval matches queries to headings heavily. Where a section answers a question, phrase the heading as that question. The FAQ sections already do this — the body sections mostly do not.

### 6.3 Self-contained sections

A section that opens with "This means the attacker can…" is unusable as a standalone chunk. First sentence of each `##` section should name its subject explicitly. This is a mechanical review pass, well suited to the `update-article` skill.

### 6.4 Make the entity explicit

Answer engines cite *sources*, and a source needs an identity. Currently a post page shows no author byline at all — the author only appears in the sidebar, which is layout chrome that extractors routinely discard. Add:

- A visible byline in `c-article__header`: author name (linked to an about page) + published date + updated date.
- An **`/about/` page** — there is none. It should state who the author is, the credentials behind a security/blockchain blog, and link the social profiles already listed in `_config.yml`. Emit `Person` JSON-LD with `sameAs` pointing at the X / GitHub / LinkedIn / Bluesky profiles. This is the standard mechanism by which an engine decides a source is a *someone* rather than an anonymous page, and it is also plain E-E-A-T for Google.
- Keep `site.author` consistent everywhere (`Ryan S.`); the JSON-LD `author.name` and the visible byline must be the same string.

### 6.5 `llms.txt`

Cheap to add, honest about its status: **no major engine consumes `llms.txt` today** — it is a proposed convention, not a standard, and neither OpenAI nor Perplexity have committed to reading it. It costs 20 minutes to generate from `site.posts` and does no harm; treat it as an option, not a priority, and do not expect measurable effect. It also only really works from a host root, which loops back to §1.1.

### 6.6 Client-side rendering caveats

Two things on the page are invisible to a non-JS crawler: MathJax output (214 posts set `isMath`) and the evil-icons SVG sprites. The math case is benign — the raw `$…$` LaTeX stays in the HTML source and is arguably more extractable than rendered MathML. Worth knowing rather than fixing.

### 6.9 One `## Annex` section instead of sibling annex headings — ✅ IMPLEMENTED (2026-08-19)

Raised by the author: the annexes were all `##` headings (`## Annex — Key Terms`, `## Annex — Invariants`, `## Annex — Integration Notes`), so one closing section produced three or four top-level entries in the table of contents and read as several separate annexes.

**What was implemented.** 59 posts restructured to a single `## Annex` with `###` subsections:

```markdown
## Conclusion
## Annex
### Key Terms
### Invariants
### Integration Notes
## Frequently Asked Questions
## References
```

Checklist annexes carry their own groupings (`### Module 1, Section A — Physical Security` and similar); those were demoted to `####` so they stay one level below the annex they belong to. 21 annex sections were affected, and no annex previously contained an `h4`, so the shift was collision-free.

**The FAQ is not part of the annex** and did not move: it remains its own `##` section after the annex, followed by `## References`. Verified on all 59.

Distribution before the change: 38 posts had a single annex, 21 had two, 1 had three. The grouping was applied uniformly, including to the single-annex posts — a rule with an exception ("group them, unless there is only one") produces an inconsistent TOC and a convention that is harder to state. Reverting that choice for the 38 single-annex posts is a one-line change to the transform if the flatter form reads better there.

Anchors do change (`#annex--key-terms` becomes `#key-terms`). Nothing in the repository links to the old anchors — checked across `_posts`, `_pages`, `_includes` and `_layouts` — and one outlier was left alone: `2026-01-27-cmtat-access-control` uses `### Annex` as a subsection of a deeper structure, which is a different pattern.

`create-article` now opens its annex section with the required structure and states that the FAQ sits outside the annex; every `## Annex — X` reference in that skill (27 of them) was rewritten to the `###` form, and the checklist grouping guidance moved to `####`.

### 6.8 Table of contents placement — ✅ IMPLEMENTED (2026-08-19)

Raised by the author: the TOC rendered between the article title and its first sentence, so the first thing in the body was a list of twenty-odd section links. Moving it below the introduction is the right call, and for a reason that goes past taste — the opening of the body is exactly what Google quotes as a snippet and what an answer engine extracts as a passage. A link list is a poor answer to any question, and it also pushes the actual opening paragraph below the fold.

Investigating it surfaced a **live bug**, and the diagnosis was confirmed against the deployed site rather than inferred from the templates. Fetching `https://rya-sge.github.io/access-denied/2026/08/18/centrifuge-vaults/` shows:

- `<p>[TOC]</p>` present verbatim in the served HTML, between the intro blockquote and the first `<h2>` — so the literal marker text is on the page;
- **no** `<ul id="markdown-toc">`, which is what kramdown's own `{:toc}` emits — so the table of contents is not produced by kramdown or by any plugin, but by `_includes/toc.html`, the Liquid include called from `_layouts/post.html`;
- the TOC `<ul>` at byte 11398 and the article's first paragraph at 14417 — the TOC precedes the introduction.
 195 posts carry a line containing exactly `[TOC]`, placed by the author after the introduction. Kramdown has no such syntax — its own is `{:toc}`, and `[TOC]` is a Python-Markdown convention — and nothing in the templates consumed the marker. So on those 195 pages the literal text `[TOC]` was rendered as a paragraph, while `_layouts/post.html` emitted the real table of contents at the top of the body. Both the misplacement and the stray text had the same cause.

**What was implemented.** The TOC is now captured into a variable and substituted for the rendered marker, which places it exactly where the author already put it:

```liquid
{% capture toc_html %}<nav class="c-toc" aria-label="{{ t.toc_title }}">…</nav>{% endcapture %}
{% if post_body contains '<p>[TOC]</p>' %}
  {% assign post_body = post_body | replace: '<p>[TOC]</p>', toc_html %}
{% elsif post_body contains '[TOC]' %}
  {% assign post_body = post_body | replace: '[TOC]', toc_html %}
{% else %}
  {{ toc_html }}
{% endif %}
```

Measured on the archive: **194 of the 195 markers already have prose before them**, so the authored position is the intended one in essentially every case. The 70 posts with no marker keep the previous behaviour and get the TOC above the body — they are mostly short 2021-era notes where it makes little difference. One post (`2023-06-02-tezos-smartpy-solidity`) had its marker inside a blockquote as `> [TOC]`, which would never have matched; it was corrected in the source.

Heading depth is unchanged: the include is still called without `h_min` / `h_max`, so the same headings appear as before. What is new is the wrapper — a labelled `<nav aria-label="Contents">` with a heading, where the TOC was previously a bare unstyled `<ul>` — plus a `_sass/5-components/_toc.scss` component and a `toc_title` string in both language blocks.

`create-article` now documents the marker and its required position.

### 6.7 Feed

`jekyll-feed` publishes the 10 most recent posts by default. Several aggregators and some AI crawlers use RSS as a discovery channel. Raising it is one line:

```yaml
feed:
  posts_limit: 30
```

---

## 7. Prioritised roadmap

**Tier 1 — do first (high impact, low effort)**

1. Add the explicit AI-search-crawler `Allow` block to `robots.txt` (§1.2) and mirror the file to the host root (§1.1).
2. ~~Migrate `last-update:` → `last_modified_at:`, render published + updated dates with `<time datetime>`~~ — ✅ done 2026-08-19 (§2.1).
3. Fix the 3 unpublished articles and the 2 malformed filenames (§4.1).
4. ~~Delete the `ethereum-stacking` stub, add `jekyll-redirect-from`~~ — ✅ done 2026-08-19 (§4.2).
5. ~~Add `description:` + title-case titles + a 2-sentence intro to the 20 category pages~~ — ✅ done 2026-08-19 (§3.3).
6. Fill in the 3 missing `categories:` and 2 missing `description:` values (§4.3).

**Tier 2 — high impact, medium effort**

7. Promote the 98 FAQ sections' questions from `**Q: …**` to `###` headings, and change the `create-article` convention to match (§3.1). `FAQPage` JSON-LD is explicitly **not** recommended any more.
8. ~~Replace `site.related_posts` with real tag-overlap related posts~~ — ✅ done 2026-08-19 (§5.1).
9. Key-takeaways block in `_layouts/post.html` + `create-article`, backfilled on the top articles (§6.1).
10. `/about/` page with `Person` schema + a visible byline on every article (§6.4).
11. `TechArticle` JSON-LD with `keywords` / `articleSection` / `wordCount` (§3.2).

**Tier 3 — worth doing, larger commitment**

12. Custom domain migration with `jekyll-redirect-from` (§1.1) — unlocks robots.txt, IndexNow at root, and brand identity in citations.
13. IndexNow ping from the deploy workflow (§1.3).
14. Question-shaped headings and self-contained section openers across the archive (§6.2–6.3).
15. Pillar-page internal linking for the 8 largest categories (§5.2). ~~Series metadata~~ — ✅ done 2026-08-19 (§5.3).
16. Description-length pass and thin-content decisions (§4.4–4.5). ~~13 duplicate `<h1>`s~~ — ✅ done 2026-08-19, and there were 4, not 13 (§4.6). ~~17 empty alts~~ — ✅ done 2026-08-19 (§4.7).

**Deliberately not proposed**: analytics (declined, §6.5 of `site_improvement.md`), image optimisation (skipped by request — though the 72 MB `assets/` tree remains the largest Core Web Vitals liability), and a permalink restructure away from `/:year/:month/:day/:title/` (date-based URLs are mildly unhelpful for evergreen content, but the migration risk outweighs the gain now that redirects would be needed for 254 URLs).

---

## 8. How to measure

Without analytics, the available instrumentation is:

- **Google Search Console** — impressions/clicks per query and per page, plus the Rich Results report for the new `FAQPage` and `TechArticle` markup. Also the only place that shows which pages Google has *chosen not to index*, which is the fastest way to spot the thin-content tail.
- **Bing Webmaster Tools** — proxy for ChatGPT's retrieval reach; its IndexNow dashboard confirms pings land.
- **Manual citation checks** — query ChatGPT (with search on) and Perplexity for the head terms of the 10 strongest articles and record whether the blog is cited. Repeat monthly. Crude, but it is the only direct read on AI visibility, and it is the metric the whole of §6 targets.
- **Server-log-free crawl check** — GitHub Pages exposes no logs, which is another argument for a custom domain fronted by a CDN if crawl visibility ever becomes important.

---

## Appendix — audit data

```
_posts/*.md files                       269
  with valid front matter               267   (2 without: permit.md, The Main Vulnerabilities…md)
  correctly named (YYYY-MM-DD-slug)     265   (4 malformed, 1 invalid month)
  language                              219 en / 48 fr / 2 none
  no duplicate slugs across languages   → no translation pairs → hreflang not applicable
front matter coverage (of 267)
  title / date / lang / locale          267
  categories / tags / description       267   (3 empty categories, 2 empty descriptions)
  image                                 267   (0 broken paths)
  isMath                                214
  last_modified_at                      210   (backfilled from git 2026-08-19; 59 posts
                                              have no substantive edit after publication)
content
  median length                         1 713 words   (min 8, max 11 056)
  posts under 400 words                 12
  posts with a FAQ section              98
  posts with [TOC]                      195
  posts with a body-level H1            0     (was 4 real + 9 miscounted code
                                              comments; fixed 2026-08-19)
  posts with tables / code blocks       146 / 144
  in-article images                     712   (0 with empty alt since 2026-08-19;
                                              60 still have an alt under 10 chars)
  external links                        4 876 (avg ~18/post)
  internal links                        avg 2/post; 28 posts with zero
  distinct tags                         748   (553 used exactly once)
descriptions
  average length                        162 chars   (126 over 170, 27 under 80, max 337)
structured data emitted today
  BlogPosting (jekyll-seo-tag)          ✅
  BreadcrumbList (_includes)            ✅
  TechArticle                           ❌
  CollectionPage / ItemList             ✅ (category pages, since 2026-08-19)
  FAQPage                               ❌ (deliberate — no longer recommended, §3.1)
  dateModified                          ✅ (since 2026-08-19)
```
