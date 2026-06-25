# CLAUDE.md

Guidance for working in this repository.

## Project

`access-denied` is a **Jekyll** technical blog (security, blockchain, cryptography, DeFi, ZKP, and related topics). Articles are Markdown posts under `_posts/`, with their figures under `assets/article/<category>/`. Posts use MathJax for math and PlantUML mindmaps for summaries.

## Repository Architecture

```
access-denied/
├── CLAUDE.md                  # This file
├── Gemfile                    # Jekyll + jekyll-paginate dependencies
├── .gitignore                 # Ignores _site, Gemfile.lock, .sass-cache, .bundle, ...
├── robots.txt
│
├── _posts/                    # Published articles (YYYY-MM-DD-slug.md), ~187 posts
│
├── draft/                     # Work-in-progress articles (not published)
│   └── article/
│
├── assets/                    # Static assets served by the site
│   └── article/               # Per-article images, organised by category
│       ├── algorithme/        ├── linux/         ├── reseau/
│       ├── blockchain/        ├── mlg/           ├── securite/
│       │   ├── ai/            ├── outil-securite/├── utilitaire/
│       │   ├── canton/        ├── pentest/       ├── virtualBox/
│       │   ├── defi/          ├── programmation/ ├── virtualization/
│       │   ├── ethereum/      ├── cryptographie/ ├── web/
│       │   └── oracle/        ├── docker/        └── windows/
│       ├── finance/           └── jekyll/
│
├── schema/                    # Diagram sources (.drawio, .excalidraw, .txt, mermaid)
│   ├── cryptography/  ├── mlg/  ├── solana/  ├── wallet/  └── save/
│
├── _layouts/                  # Page templates
│   ├── default.html  ├── home.html  ├── post.html  └── category-page.html
│
├── _includes/                 # Reusable HTML fragments
│   ├── head.html      ├── header.html   ├── toc.html      ├── categories.html
│   ├── mathJax.html   ├── newsletter.html├── form.html     ├── disqus-comments.html
│   ├── javascripts.html ├── main.scss   └── newsletter.html
│
├── _pages/                    # Standalone pages
│   └── category/              # Category landing pages
│
├── _plugins/                  # Custom Jekyll plugins (Ruby)
│   └── category-generator.rb
│
├── _sass/                     # Styles, ITCSS structure
│   ├── 0-settings/  ├── 2-generic/   ├── 4-objects/     ├── 6-trumps/
│   ├── 1-tools/     ├── 3-elements/  └── 5-components/
│
├── fonts/                     # Web fonts
└── js/                        # JavaScript
```

> Note: `_site/` (Jekyll build output) and `Gemfile.lock` are git-ignored and do not appear here.

## Working Conventions

- **Posts** live in `_posts/` and must be named `YYYY-MM-DD-slug.md` (the date prefix is required for Jekyll to build the post).
- **Article images** go in `assets/article/<category>/<topic>/`. In the post body, reference them with the `{{site.url_complet}}` prefix (`![alt]({{site.url_complet}}/assets/article/...)`); in the YAML `image:` frontmatter field, use the root-relative path only (`/assets/article/...`).
- **Mindmaps**: keep the `@startmindmap … @endmindmap` source block in the article and embed the rendered PNG above it.

## Commit Messages

**After each batch of modifications performed, provide a suggested GitHub commit message** so the work can be committed in coherent units. Do this for every batch (do not run `git commit` unless explicitly asked; just propose the message).

Guidelines for the message:

- **The commit message must be one line** (a single subject line, no body and no trailer).
- Use the imperative mood (e.g. "Add", "Fix", "Update", "Rename"), capped at ~72 characters.
- One commit per logical batch: keep unrelated changes in separate messages.

Example:

```
Add traditional vs. perpetual futures article with mindmap
```
