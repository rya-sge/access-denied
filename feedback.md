# Website Feedback — AccessDenied Blog

## Critical Issues

### 1. Posts Not Published (Missing Jekyll Filename Convention)
Four posts are missing the required `YYYY-MM-DD-` date prefix in their filename. Jekyll will **not render them** as posts:

- `Blockchain downtime.md`
- `permit.md`
- `The Main Vulnerabilities When Using ECDSA Signatures in Smart Contracts.md`
- `Traditional Futures vs. Perpetual Futures A Technical Comparison.md`

Fix: rename them to follow the `YYYY-MM-DD-slug.md` pattern.

### 2. Missing Frontmatter on Two Posts
`permit.md` and `The Main Vulnerabilities When Using ECDSA Signatures in Smart Contracts.md` have **no YAML frontmatter at all** — no `layout`, `title`, `date`, or `description`. They will not be rendered correctly even after renaming.

### 3. Wrong Description (Copy-Paste Error)
`Traditional Futures vs. Perpetual Futures A Technical Comparison.md` has the description from a different article:
> "This article is an overview of the OpenZeppelin ERC-4337 Account contract..."

This will appear in Google search results with the wrong snippet.

---

## SEO Issues

> **Important context:** `_config.yml` enables the `jekyll-seo-tag` plugin and `_includes/head.html:31` invokes `{% seo %}`. The site is hosted on GitHub Pages (`rya-sge.github.io/access-denied`), where `jekyll-seo-tag`, `jekyll-feed`, and `jekyll-sitemap` are auto-provided even though they are not listed in the `Gemfile`. This plugin auto-generates the canonical and meta-description tags, which changes the assessment of issues #4 and #5 below.

### 4. Canonical URL Tag Commented Out — *observation true, no real impact*
In `_includes/head.html:17`, the hand-written canonical `<link>` is commented out. However, `jekyll-seo-tag` (`{% seo %}` at `_includes/head.html:31`) emits its own `<link rel="canonical">` on every page, so a canonical tag **is** present in the rendered output. The commented-out manual tag is redundant; commenting it out has no SEO effect. **Not an actual problem.**

### 5. Meta Description Not Injected for Posts — *inaccurate; proposed fix would be harmful*
The hand-written logic in `_includes/head.html` is:
```liquid
{% unless page.description %}
  <meta name='description' content="{{ site.description }}">
{% endunless %}
```
It is true that this manual block emits a description only when the page has none. But `jekyll-seo-tag` independently generates `<meta name="description">` from `page.description` (falling back to `page.excerpt`, then `site.description`), so posts with a description **do** get a meta description tag.

⚠️ The previously suggested fix (`{% if page.description %}...{% else %}...{% endif %}`) would emit a **second, duplicate** description tag alongside the plugin's. Do not apply it. If anything, the redundant manual block could be removed and the description left entirely to `jekyll-seo-tag`.

### 6. Non-Zero-Padded Date in Filename — *accurate, low impact*
`2024-11-4-TLS1.3-overview.md` uses a non-padded day (`4` instead of `04`); it is the only such file. Jekyll's filename matcher accepts a 1–2 digit day, so the post renders fine (its permalink is `/2024/11/4/...`). This is a consistency nit rather than a true SEO defect, but renaming to `2024-11-04-...` keeps the corpus uniform.

### 7. Global `lang` Mismatch — *facts correct, impact overstated, root cause is different*
`_config.yml:6` sets `lang: "fr_FR"` while 136 posts declare `lang: en`. However, this is **not** what Google reads for language classification: `_layouts/default.html:2-6` sets `<html lang>` **per post** from `page.lang`, so English posts correctly render `<html lang="en">`. `site.lang` is never used for `<html lang>` (the `{% else %}` branch hardcodes `"fr"`); its only effect is `og:locale` via `jekyll-seo-tag`, a minor signal.

The genuine issue is different: **50 of 187 posts have no `lang` field at all**, so they fall into the `{% else %}` branch and render as `<html lang="fr">` despite English content. Fix by adding `lang: en` to those posts (and optionally aligning `site.lang` to a sensible default such as `en`).

---

## Content Issues

### 8. Typos in `Blockchain downtime.md`
The introductory paragraph contains several typos:

| Found | Should be |
|-------|-----------|
| `particularlly` | `particularly` |
| `collaterteral` | `collateral` |
| `procool` | `protocol` |
| `acumulate` | `accumulate` |
| `serveral` | `several` |
| `prochain` | `blockchain` (French word left in) |
| `pic of transaction` | `spike of transactions` |
| `liquidied` | `liquidated` |

### 9. Typo in 404 Page
`404.html` reads: `"Back to the bLog"` — the capital `L` is unintentional.

---

## Template / Layout Issues

### 10. Hardcoded Placeholder Text in Post Layout
`_layouts/post.html:50` has a literal `<p>Share button</p>` which renders as visible text on every post page. This is clearly a leftover placeholder.

### 11. "You might also enjoy" Silently Skips Posts Without Images
In `_layouts/post.html:71-83`, the related posts section only renders articles that have an `image` field. Posts without images are silently excluded. With 13+ posts having an empty `image:` field, this section will often show fewer than 4 suggestions or appear empty.

### 12. LinkedIn URL Uses Wrong Domain
In `_layouts/home.html:61`, the LinkedIn link points to `https://in.linkedin.com/in/...` (the Indian subdomain). It should be `https://www.linkedin.com/in/...`.

### 13. Bluesky Link is Hardcoded in Template
`_layouts/home.html:64` has the Bluesky profile URL hardcoded directly in the template:
```html
<a href="https://bsky.app/profile/ad403.bsky.social" ...>bsky</a>
```
It should be extracted to `_config.yml` as `social-bluesky` for consistency and maintainability.

### 14. Share Buttons Only Cover Twitter/Facebook
Post share options in `_layouts/post.html` only include Twitter and Facebook, despite the author also having LinkedIn and Bluesky profiles. Consider adding those.

### 15. Twitter References Not Updated to X
Several template files still reference `twitter.com` for the "contact me" link and share button. The platform was rebranded to X. The social icon link in `_layouts/home.html:33` does use `x.com`, but `_layouts/post.html:38` still points to `twitter.com/intent/user`.

---

## Configuration Issues

### 16. `url_complet` Typo in `_config.yml`
`_config.yml:5` has `url_complet` — likely meant to be `url_complete`. Check if this variable is referenced anywhere before renaming.

### 17. Unconfigured Features Left as Placeholders
Several features are set up in the templates but not configured, which silently disables them:
- `google-analytics` — no tracking ID
- `disqus-identifier` — comments disabled
- `mailchimp` — newsletter non-functional
- `author-email` — contact button never shows

These are fine if intentional, but worth documenting so they are not forgotten.

---

## Minor

### 18. `_config.yml` `about-author` is Identical to `description`
Both fields read: `"Blog specialized on Security, Crypto and blockchain."` The `about-author` appears in the sidebar and is a good opportunity for a short personal bio instead of repeating the site tagline.

### 19. No Category Pages in Repo
`_includes/categories.html` links to `/category/<slug>/`, but there are no category page files in `_pages/` or elsewhere in the repo. These links may all 404 unless they are generated by a plugin not listed in the Gemfile.
