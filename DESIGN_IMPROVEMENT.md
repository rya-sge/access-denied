# Design improvements: reader experience

Review of the live site (https://rya-sge.github.io/access-denied/) on 2026-11-18, in Chrome at a 536px window and through a 1440px frame, then checked on a local Docker build (`jekyll serve`, github-pages 232).

## Done (2026-11-18)

| Area | Change | Files |
|---|---|---|
| Line length | Article body is one centred column of about 80 characters (44rem) at 17px, line height 1.7; was about 140 characters at 15px on desktop. Tables, code and image-only paragraphs keep the full card width. | `_sass/5-components/_reading.scss` |
| Code blocks | System monospace instead of Courier, line height 1.55, no wrapping (horizontal scroll), no `break-all`. | `_sass/3-elements/_pre.scss`, `_sass/0-settings/_typography.scss` |
| Inline code | Wraps as a word; only an identifier longer than the line breaks. | `_sass/3-elements/_code.scss` |
| Tables | Light 1px rules, tinted header, zebra rows, horizontal scroll when wider than the card. Each table shrinks to its content (`width: fit-content`; a block-level table otherwise drew an empty bordered area beside narrow tables such as the Jenkins Severity table), starts at the left edge of the text column and may grow to the card's right edge. Right-aligned number cells do not wrap. | `_sass/5-components/_reading.scss` |
| Phone padding | Card padding 20px → 12px below 480px; table cells 6px 8px. On a 360px screen, tables that scroll in the Jenkins security article went from 10 to 6 of 14. | `_sass/5-components/_reading.scss` |
| Blockquotes | Body font instead of the 18px heading serif. | `_sass/3-elements/_blockquote.scss` |
| Table of contents | Two columns from 1100px; a section never splits from its sub-entries. | `_sass/5-components/_toc.scss` |
| Diagrams | Article images open full size in a new tab on click. | `js/main.js` |
| Reading time | "N min read" next to the dates (220 words a minute), English and French. | `_layouts/post.html`, `_data/i18n.yml` |
| PlantUML warning | Three diagrams printed a yellow "This syntax is deprecated" box; converted to `:text; <<#color>>` and re-rendered. | `seccomp-bpf-filter-workflow`, `posix-permission-resolution-workflow`, `sep41-path-decision` (`.puml` and `.png`) |

## To do

Ordered by expected benefit for a reader, highest first.

### 1. Article pages on mobile open with the sidebar, not the article

On a phone, every article starts with the avatar, name, tagline, bio line and social icons, then the title. The first screen shows almost none of the article, and the same block repeats on every page.

- **Change:** below 900px, on `post` pages, collapse the sidebar into a one-line bar (avatar, site name, menu or search icon), or move it below the article.
- **Where:** `_sass/5-components/_sidebar.scss`, `_layouts/default.html` (a `page.layout == 'post'` class on `body`).
- **Check:** the title is visible without scrolling on a 375px-wide screen.

### 2. Diagram text is still small inside the column

Click-to-zoom solves reading a diagram on purpose, but wide PlantUML and Mermaid figures (activity diagrams, mindmaps) are scaled to the column and their labels drop to 6-8px.

- **Change:**
  - Let image-only paragraphs grow past the column, up to the card width. This is done for `p:has(> img:only-child)`, but kramdown output with a caption or a link around the image escapes it; check the common patterns in `_posts/`.
  - In `create-article`, ask for diagrams no wider than about 900px at 1x, or for SVG output (`plantuml -tsvg`), which stays sharp when zoomed.
- **Where:** `_sass/5-components/_reading.scss`; `~/.claude/skills/create-article/SKILL.md` (diagram section).

### 3. Mindmap thumbnails on the home page cards are unreadable

Each home card shows the article's mindmap as its thumbnail. At card size it is a grey tangle that tells the reader nothing, and it is the largest element of the card.

- **Change:**
  - Use a dedicated cover image when the post defines one (a new `cover:` front-matter key), and fall back to the mindmap only otherwise.
  - Or crop the mindmap to its centre with `object-fit: cover` and a fixed height, so the card leads with the title.
- **Where:** `_layouts/home.html` or the card include, `_sass/5-components/_index-post.scss`.

### 4. Fixed 300px left sidebar on desktop

From 900px up the sidebar keeps 300px whatever the screen width. At 1024-1280px it squeezes the card.

- **Change:** `width: clamp(220px, 20vw, 300px)` for the sidebar, with `.c-content { margin-left }` following the same value.
- **Where:** `_sass/5-components/_sidebar.scss`, `_sass/5-components/_content.scss`.

### 5. Sticky table of contents on wide screens

On a 1440px or wider screen, the right side of the card is empty beside the 80-character column. A sticky TOC there would show where the reader is in a 20-minute article.

- **Change:** from about 1400px, place `.c-toc` in a right-hand column with `position: sticky; top: 20px`, and highlight the current section with an `IntersectionObserver` in `js/main.js`. Keep the inline TOC below that width.
- **Where:** `_layouts/post.html` (TOC already captured in `toc_html`), `_sass/5-components/_toc.scss`, `js/main.js`.

### 6. Reading progress bar

A 2-3px bar at the top of article pages, filled as the reader scrolls. Cheap, and useful on 15-20 minute articles.

- **Where:** `_layouts/post.html`, `js/main.js` (scroll listener with `requestAnimationFrame`), `_sass/5-components/_reading.scss`.

### 7. Heading anchors

Readers cannot copy a link to a section. Add a `#` link that appears on hover next to each `h2`/`h3` (the ids already exist from kramdown).

- **Where:** `js/main.js` (insert the anchor), `_sass/5-components/_reading.scss`.

### 8. Previous / next article in a series

The series box lists all parts at the top, but nothing at the end of an article leads to the next part.

- **Change:** add "Next in this series: …" at the end of the article, from `_data/series.yml`.
- **Where:** `_includes/series-nav.html` (or a new `series-next.html`), `_layouts/post.html`.

### 9. Header metadata in capitals

The date line is uppercase ("BY RYAN S. · 2026, JUN 29 · UPDATED 2026, NOV 17 · 20 MIN READ"). Capitals slow reading for a line this long.

- **Change:** sentence case, 13px, muted colour.
- **Where:** `.c-article__date` in `_sass/5-components/_article-page.scss`.

### 10. The "made with Claude Code" note

The same blockquote sits at the top of most recent articles, before the first section. It is now quieter (body font), but it still comes before the content.

- **Change:** move it to the article footer, or render it from a front-matter flag as a small line under the dates.
- **Where:** `_layouts/post.html`; the posts themselves (one line each).

### 11. Dark mode follows the visitor's system setting

Light is forced by design (see the comment in `_sass/0-settings/_theme.scss`). A reader whose system is dark gets a white page at night until they find the toggle.

- **Change, if wanted:** honour `prefers-color-scheme: dark` when no choice is stored, as the comment in `_theme.scss` already describes.

### 12. Print stylesheet

Printing an article also prints the sidebar, the theme toggle and the scroll-to-top button.

- **Change:** an `@media print` block that hides them and removes the card background.
- **Where:** `_sass/6-trumps/helpers.scss` or a new `_sass/5-components/_print.scss`.

## Content issues seen during the review

- `assets/article/securite/linux-advanced-security/seccomp-bpf-filter-workflow.puml` shows 4 seccomp verdicts, while the article text lists 8 since the 2026-11-17 fact check.
