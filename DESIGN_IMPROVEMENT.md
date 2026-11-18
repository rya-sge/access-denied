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
| Top bar instead of the left sidebar | The fixed sidebar (avatar, name, tagline, social, copyright) is replaced by a 56px sticky top bar: avatar and name (home), Posts, Categories (opens the home categories view through `#categories`), Tags, About, search, social icons and the theme switch. It hides on scroll down and returns on scroll up. Below 900px it shows the name, the theme switch and a menu button that opens the links, search and social. The main column is centred at 1200px; on articles from 1280px the right 280px holds the sticky TOC, and the inline TOC is hidden while that column shows. Superseded the interim compact mobile sidebar and fluid sidebar width. | `_includes/topbar.html`, `_layouts/home.html`, `_layouts/default.html`, `_sass/5-components/_topbar.scss`, `_content.scss`, `_sass/4-objects/_wrapper.scss`, `js/main.js` |
| Author card | Author block moved from the sidebar to a card at the top of the home page (first page) and at the end of each article (replacing the "Feel free to contact me on" line). | `_includes/author-card.html`, `_sass/5-components/_author-card.scss`, `index.html`, `_layouts/post.html` |
| Footer and shared social links | Site footer with social links and copyright; one `social-links.html` include for the bar, the card and the footer. A "Skip to content" link for keyboard users. | `_includes/social-links.html`, `_layouts/home.html`, `_layouts/default.html` |
| One search box | The search lives in the top bar on every page; the hidden duplicates in the article, tags and 404 pages are gone (the results script binds one id). | `_includes/header.html`, `_layouts/post.html`, `tags.html`, `404.html` |
| Card thumbnails | A post may set `cover:` (root-relative path) to show a picture on its home and category card instead of the mindmap; posts without it are unchanged. | `_includes/post-card.html`, `_includes/categories.html` |
| Sticky TOC | When the space right of the card is at least 220px, a copy of the TOC is fixed there and the section being read is highlighted. | `js/main.js`, `_sass/5-components/_reading.scss` |
| Reading progress | 3px bar at the top of article pages. | `js/main.js`, `_sass/5-components/_reading.scss` |
| Heading anchors | `#` link after each h2/h3, shown on hover or focus. | `js/main.js`, `_data/i18n.yml`, `_includes/javascripts.html` |
| Series navigation | "Previous / Next in this series" cards at the end of articles in an ordered series (`rel=prev/next`). | `_includes/series-next.html`, `_layouts/post.html`, `_sass/5-components/_series.scss`, `_data/i18n.yml` |
| Date line | Sentence case instead of capitals. | `_sass/5-components/_article-page.scss` |
| Claude Code note | Restyled as a small muted line (matched on its link, posts unchanged). | `_sass/5-components/_reading.scss` |
| Dark mode | Follows the visitor's system setting when no choice is stored; a toggle click stores a choice that wins. | `_includes/head.html`, `js/main.js`, comments in `_theme.scss` and `default.html` |
| Print | Only the article prints: top bar, author card, buttons, footer, related posts and comments hidden, external link targets written out, code wraps. | `_sass/5-components/_print.scss` |
| Seccomp diagram | Shows the 8 verdicts grouped in 4 outcomes, matching the text; alt text describes the figure. | `seccomp-bpf-filter-workflow.puml` / `.png`, the seccomp post |
| Blockquotes | Body font instead of the 18px heading serif. | `_sass/3-elements/_blockquote.scss` |
| Table of contents | Two columns from 1100px; a section never splits from its sub-entries. | `_sass/5-components/_toc.scss` |
| Diagrams | Article images open full size in a new tab on click. | `js/main.js` |
| Reading time | "N min read" next to the dates (220 words a minute), English and French. | `_layouts/post.html`, `_data/i18n.yml` |
| PlantUML warning | Three diagrams printed a yellow "This syntax is deprecated" box; converted to `:text; <<#color>>` and re-rendered. | `seccomp-bpf-filter-workflow`, `posix-permission-resolution-workflow`, `sep41-path-decision` (`.puml` and `.png`) |

## To do

### 1. Set `cover:` images

The card supports a cover picture now, but no post sets one. Until covers are added, cards still show the mindmap. A simple option: a cropped section of the article's main diagram, or a plain title card in the site colours, at about 800 × 450.

### 2. Diagrams as SVG

Image-only paragraphs already use the full card width and open full size on click. Rendering PlantUML as SVG (`plantuml -tsvg`) would keep labels sharp at any zoom. Changing `create-article` and `create-plantuml-diagram` to produce SVG, and the alt-text and `image:` conventions that assume PNG, is a separate decision.

### 3. Move the Claude Code note

It is now a small muted line, but still sits after the introduction in 250 posts. Moving it to the footer means a front-matter flag (for example `made_with: claude-code`) rendered by `_layouts/post.html`, and removing the blockquote from each post.

### 4. Avatar file size

`assets/1.png`, the avatar shown in the top bar and the author cards, is 1.1 MB for a 32-80px picture. A 160px WebP or JPEG (a few kB) would cut the first load of every page.

### 5. Device check

All checks so far used Chrome with off-screen and on-page iframes. A check on a real phone (iOS Safari, Android Chrome) would cover touch scrolling of tables and the sticky elements.

### 6. Lighthouse and contrast

Not measured yet: Lighthouse accessibility and performance scores, colour contrast of the muted greys (`--text-muted`, `$gray`), Core Web Vitals. See the Gaps of the `website-design-check` skill.
