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

### 4. Canonical URL Tag Commented Out
In `_includes/head.html:17`, the canonical `<link>` is commented out. Without it, search engines may index duplicate URLs (e.g. `/page/1/` vs `/`).

### 5. Meta Description Not Injected for Posts
The logic in `_includes/head.html` is:
```liquid
{% unless page.description %}
  <meta name='description' content="{{ site.description }}">
{% endunless %}
```
This outputs the **site description** when there is no page description — but outputs **nothing** when there is one. Posts with a description field get no `<meta name="description">` tag at all.

Fix: change to `{% if page.description %}...{% else %}...{% endif %}`.

### 6. Non-Zero-Padded Date in Filename
`2024-11-4-TLS1.3-overview.md` uses a non-padded day (`4` instead of `04`). While Jekyll may handle this, it's inconsistent and can cause unexpected permalink behavior.

### 7. Global `lang` Mismatch
`_config.yml` sets `lang: "fr_FR"` but the vast majority of posts have `lang: en`. This can affect SEO (Google may classify the site as French) and any locale-specific formatting.

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
