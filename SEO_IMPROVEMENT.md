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
| 4 | Structured data | 98 articles have a FAQ section; none emit `FAQPage` JSON-LD | 🔴 High | M |
| 5 | Content loss | 3 articles are unpublished (bad filenames), 1 is a duplicate-title stub, 1 has an invalid filename date | 🟠 Med | S |
| 6 | Extractability | No answer-first summary, no visible author/updated line, no `<time datetime>` | 🟠 Med | M |
| 7 | Internal linking | ~~`site.related_posts` is "4 most recent"~~ — **✅ implemented 2026-08-19**; 28 posts still have zero in-body internal links | 🟠 Med | M |
| 8 | Category pages | 20 landing pages with no title-case, no description, no intro text | 🟠 Med | S |
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

### 3.1 `FAQPage` on 98 articles — the highest-value schema left

98 posts already end with a `## Frequently Asked Questions` section in a rigidly consistent format (`**Q: …**` followed by answer paragraphs) because the `create-article` skill enforces it. That is a ready-made, hand-written Q&A corpus that is currently invisible as structured data.

Two payoffs: Google can surface the questions directly, and — more importantly here — answer engines strongly favour content that is already chunked into question/answer pairs, because it maps onto how they retrieve.

Since the Actions build runs **without safe mode**, a Ruby plugin is the robust route (a Liquid string-parse of `**Q:` would be fragile against bold text inside answers):

```ruby
# _plugins/faq_jsonld.rb
# Emits FAQPage JSON-LD for any post whose body contains a
# "## Frequently Asked Questions" section in the create-article format:
#   **Q: <question>**
#   <one or more answer paragraphs, until the next Q or the next H2>
#
# Stored in page.data['faq_jsonld'] and rendered by _includes/faq-schema.html,
# so a post with no FAQ emits nothing at all.
module Jekyll
  class FaqJsonLd < Generator
    safe true
    priority :low

    HEADING = /^##\s+(?:Frequently Asked Questions|FAQ)\s*$/
    QUESTION = /^\*\*Q:\s*(.+?)\*\*\s*$/

    def generate(site)
      site.posts.docs.each { |post| build(post) }
    end

    private

    def build(post)
      body = post.content
      start = body =~ HEADING
      return unless start

      section = body[start..]
      section = section.split(/^##\s+(?!Frequently|FAQ)/, 2).first

      pairs = []
      section.split(QUESTION).drop(1).each_slice(2) do |question, answer|
        next if answer.nil?
        text = answer.strip
        next if text.empty?
        pairs << { '@type' => 'Question',
                   'name' => question.strip,
                   'acceptedAnswer' => { '@type' => 'Answer', 'text' => text } }
      end
      return if pairs.empty?

      post.data['faq_jsonld'] = {
        '@context' => 'https://schema.org',
        '@type' => 'FAQPage',
        'mainEntity' => pairs
      }.to_json
    end
  end
end
```

```liquid
{%- comment -%} _includes/faq-schema.html — add after breadcrumbs.html in head {%- endcomment -%}
{% if page.faq_jsonld %}
<script type="application/ld+json">{{ page.faq_jsonld }}</script>
{% endif %}
```

Caveats to respect: the answer text must be **plain text** (strip markdown links, code fences and math before emitting — a stray `$$` or unescaped quote will invalidate the block), and the JSON-LD must match what the reader sees, or it is spam. Validate a sample with the Rich Results Test before rolling it out to all 98.

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

### 3.3 Category pages have no schema and no words

The 20 pages under `_pages/category/` are front matter only: `title: zkp`, a `category:` key, a permalink. What renders is a bare grid of cards. Three problems compound:

- **No `description`** → `jekyll-seo-tag` falls back to the site description, so 20 pages ship the *same* meta description. Duplicate-snippet territory.
- **Lowercase display titles** (`zkp`, `iso20022`, `eli10`) — these are the `<h1>`/`<title>` of hub pages for the site's best topics.
- **No intro prose** → a category hub with 131 links and zero sentences is a thin page to Google and useless to an answer engine, which cannot summarise a list of titles.

Fix (per page, ~4 lines of front matter + 2 sentences):

```yaml
---
layout: category-list
title: Zero-Knowledge Proofs
category: ZKP
permalink: /category/zkp/
description: Articles on zero-knowledge proof systems — SNARKs, STARKs, recursive proofs, and the vulnerability classes that affect ZK circuits in production.
---

Zero-knowledge proofs let one party convince another that a statement is true
without revealing why. These {{ site.categories.ZKP | size }} articles cover the
proof systems themselves (Groth16, PLONK, STARKs), the tooling around them, and
the real-world failures that have hit ZK deployments.
```

`_layouts/category-list.html` needs one line to render `{{ content }}` above the grid, plus an `ItemList`/`CollectionPage` JSON-LD block listing the posts in order. Those hubs are the pages most likely to rank for the broad head terms ("zero knowledge proof explained", "ISO 20022 message types") that individual articles are too specific to win.

---

## 4. Content-level fixes

### 4.1 Articles that are not published at all — 3 lost posts

Jekyll requires `YYYY-MM-DD-slug.md`. These three do not have it and are silently dropped:

- `_posts/Blockchain downtime.md`
- `_posts/permit.md`
- `_posts/The Main Vulnerabilities When Using ECDSA Signatures in Smart Contracts.md`

The last two also have no front matter at all. `feedback.md` §1–2 flagged this; it is still open. Either rename them with a date prefix and add front matter, or move them to `draft/`. Right now they are neither published nor drafts — just invisible.

Also: `_posts/2022-20-12-foundry-tutorial-nft.md` has **month 20** in its filename. It builds only because the `date:` in front matter overrides it, but it is a trap for any tool that parses filenames (including the ones in `_plugins/`). Rename to `2022-12-20-…`. And `_posts/2024-11-4-TLS1.3-overview.md` needs its day zero-padded.

### 4.2 Duplicate title / thin stub

`_posts/2024-03-28-ethereum-stacking.md` — 34 words, empty description, empty categories, `exclude: yes` — carries **the same `title` as `2024-03-28-ethereum-staking.md`**. `exclude:` only hides it from the home listing; it is still live, still in `sitemap.xml`, still in `search.json`, and still competing with the real article for its own title. This is textbook keyword cannibalisation, made worse by the fact that the stub's only content is a link to the article it competes with.

Fix: delete the file and add a redirect instead. Since the Actions build allows gems outside the Pages whitelist, add `jekyll-redirect-from` and put on the real article:

```yaml
redirect_from:
  - /2024/03/28/ethereum-stacking/
```

That is a proper redirect page with a canonical, rather than a competing document.

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

### 4.6 Duplicate `<h1>`

13 posts open with a body-level `# Heading`, while `_layouts/post.html` already renders the title as `<h1 class="c-article__title">`. Two `<h1>`s on a page is not fatal but it muddies the document outline that both Google and every content-extraction library rely on. Demote those 13 to `##`.

### 4.7 Alt text

711 in-article images, **17 with empty alt**. Small number, quick fix — and worth doing because for a blog whose figures are architecture diagrams, the alt text is often the only description of the diagram that a text-only crawler (or an answer engine) ever sees. Prefer a sentence describing what the diagram *shows* over a repeat of the caption. Note that `html-proofer` currently runs with `--ignore-empty-alt`; once the 17 are fixed, drop that flag so a regression is caught.

---

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

### 5.3 Series / cluster metadata

Several groups of posts form explicit series. Adding `series: windows-sos` to their front matter and rendering a "Part N of M" navigation box would create dense, semantically meaningful internal links and give answer engines an unambiguous signal that these pages belong together. It also renders well as a `hasPart` / `isPartOf` schema relation.

---

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
4. Delete the `ethereum-stacking` stub, add `jekyll-redirect-from` (§4.2).
5. Add `description:` + title-case titles + a 2-sentence intro to the 20 category pages (§3.3).
6. Fill in the 3 missing `categories:` and 2 missing `description:` values (§4.3).

**Tier 2 — high impact, medium effort**

7. `FAQPage` JSON-LD plugin for the 98 FAQ articles (§3.1).
8. ~~Replace `site.related_posts` with real tag-overlap related posts~~ — ✅ done 2026-08-19 (§5.1).
9. Key-takeaways block in `_layouts/post.html` + `create-article`, backfilled on the top articles (§6.1).
10. `/about/` page with `Person` schema + a visible byline on every article (§6.4).
11. `TechArticle` JSON-LD with `keywords` / `articleSection` / `wordCount` (§3.2).

**Tier 3 — worth doing, larger commitment**

12. Custom domain migration with `jekyll-redirect-from` (§1.1) — unlocks robots.txt, IndexNow at root, and brand identity in citations.
13. IndexNow ping from the deploy workflow (§1.3).
14. Question-shaped headings and self-contained section openers across the archive (§6.2–6.3).
15. Series metadata and pillar-page internal linking for the 8 largest categories (§5.2–5.3).
16. Description-length pass, thin-content decisions, 13 duplicate `<h1>`s, 17 empty alts (§4.4–4.7).

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
  posts with a body-level H1            13
  posts with tables / code blocks       146 / 144
  in-article images                     711   (17 with empty alt)
  external links                        4 876 (avg ~18/post)
  internal links                        avg 2/post; 28 posts with zero
  distinct tags                         748   (553 used exactly once)
descriptions
  average length                        162 chars   (126 over 170, 27 under 80, max 337)
structured data emitted today
  BlogPosting (jekyll-seo-tag)          ✅
  BreadcrumbList (_includes)            ✅
  FAQPage / TechArticle / ItemList      ❌
  dateModified                          ✅ (since 2026-08-19)
```
