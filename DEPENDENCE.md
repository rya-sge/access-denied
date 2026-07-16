# Dependencies

This document lists all dependencies used by the **access-denied** Jekyll blog:
Ruby gems, Jekyll plugins, vendored front-end libraries, and third-party
remote/CDN services loaded at runtime.

> Last reviewed: 2026-07-03

---

## 1. Ruby gems (`Gemfile`)

| Gem              | Purpose                                                            | Notes |
|------------------|-------------------------------------------------------------------|-------|
| `bundler`        | Dependency manager for the Ruby gems                              | |
| `jekyll`         | Static-site generator (core of the project)                      | Version unpinned |
| `jekyll-paginate`| Pagination of the article list                                   | Also declared in `_config.yml` plugins |
| `faraday-retry`  | Retry middleware required by GitHub metadata tooling             | Silences the Faraday v2 warning |
| `tzinfo-data`    | Timezone data for Windows (`:mingw, :mswin, :x64_mingw, :jruby`) | Platform-scoped |
| ~~`jekyll-katex`~~ | *(commented out)* alternative math renderer                    | Not active |

## 2. Jekyll plugins (`_config.yml` → `plugins:`)

| Plugin            | Purpose                                        | In Gemfile? |
|-------------------|------------------------------------------------|-------------|
| `jekyll-paginate` | Pagination                                     | ✅ yes |
| `jekyll-feed`     | Generates the Atom/RSS feed                    | ⚠️ **not in Gemfile** |
| `jekyll-seo-tag`  | Injects SEO `<meta>` / Open Graph tags         | ⚠️ **not in Gemfile** |
| `jekyll-sitemap`  | Generates `sitemap.xml`                         | ⚠️ **not in Gemfile** |

> ⚠️ `jekyll-feed`, `jekyll-seo-tag`, and `jekyll-sitemap` are enabled as
> plugins but are **not declared in the `Gemfile`**. They currently work only
> if provided by the environment (e.g. the `github-pages` gem or a system
> install). Consider adding them explicitly to the `Gemfile` for reproducible
> builds.

## 3. Vendored front-end libraries (`js/`)

Bundled locally in the repository (no CDN, no package manager):

| File                          | Library                | Version | Purpose |
|-------------------------------|------------------------|---------|---------|
| `jquery-3.3.1.min.js`         | jQuery                 | 3.3.1   | DOM/JS helper (older release) |
| `evil-icons.min.js`           | Evil Icons             | —       | SVG icon set |
| `jquery.fitvids.js`           | FitVids.js             | —       | Responsive video embeds |
| `simple-jekyll-search.min.js` | Simple-Jekyll-Search   | —       | Client-side article search |
| `main.js`                     | *(project code)*       | —       | Site-specific scripts |
| `mathjaxv4/tex-svg.js`        | MathJax (SVG output)   | 4.1.2   | Self-hosted math rendering |

> ℹ️ jQuery 3.3.1 (2018) is outdated; upgrading to the latest 3.x is advisable
> for security/bugfixes.

## 4. Remote / CDN runtime dependencies

Loaded by the browser when a page is viewed (declared in `_includes/`):

| Service            | Resource                                                        | Used for | Declared in |
|--------------------|-----------------------------------------------------------------|----------|-------------|
| **Google Fonts**   | `fonts.googleapis.com` — *Open Sans*, *Volkhov*                 | Web typography | `_includes/head.html` |
| **Disqus**         | `disqus.com`                                                    | Article comments | `_includes/disqus-comments.html` |
| **Formspree**      | `formspree.io`                                                  | Contact / newsletter form | `_includes/form.html` |

### Legacy / commented-out (not active)

| Resource                                          | Status |
|---------------------------------------------------|--------|
| `cdn.mathjax.org/.../MathJax.js` (MathJax 2)      | Commented out in `_includes/javascripts.html` |
| ~~`polyfill.io/v3/polyfill.min.js`~~              | **Removed** — compromised supply-chain CDN (see security note below) |

## 5. Fonts (local)

| File                                          | Font (family) |
|-----------------------------------------------|---------------|
| `fonts/file/SlGQmQieoJcKemNecTUEhQ.woff2`     | Volkhov (self-hosted `.woff2`) |
| `fonts/file/SlGVmQieoJcKemNeeY4hkHNSbQ.woff2` | Volkhov (self-hosted `.woff2`) |

---

## Security notes

- 🛑 **`polyfill.io` removed (2026-07-03):** the `polyfill.io/v3/polyfill.min.js`
  script that was loaded site-wide via `_includes/mathJax.html` was removed. The
  `polyfill.io` domain was sold in 2024 and began serving malware; it must not be
  used. MathJax 3 does not require it.
- ✅ **MathJax is now self-hosted** (`js/mathjaxv4/tex-svg.js`, v4.1.2) — no
  longer loaded from a CDN, removing that third-party runtime dependency.
- ⚠️ Remaining third-party remote resources (Google Fonts, Disqus, Formspree)
  run with full privileges on every page. For hardening, consider
  **Subresource Integrity (SRI)** hashes and/or self-hosting these assets too.
- ⚠️ jQuery 3.3.1 is outdated — plan an upgrade to the latest 3.x.
