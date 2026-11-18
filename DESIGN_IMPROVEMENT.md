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
| Mobile article header | Below 900px, article pages (`body.is-post`) show the sidebar as a 48px bar (avatar and name); the article title starts 78px from the top instead of a screen down. Listing pages keep the full author block. | `_layouts/default.html`, `_sass/5-components/_sidebar.scss` |
| Sidebar width | `clamp(220px, 20vw, 300px)` instead of a fixed 300px; at 1024px the card grew from 665px to 745px and the text from 62 to 78 characters a line. | `_sass/5-components/_sidebar.scss`, `_content.scss` |
| Card thumbnails | A post may set `cover:` (root-relative path) to show a picture on its home and category card instead of the mindmap; posts without it are unchanged. | `_includes/post-card.html`, `_includes/categories.html` |
| Sticky TOC | When the space right of the card is at least 220px, a copy of the TOC is fixed there and the section being read is highlighted. | `js/main.js`, `_sass/5-components/_reading.scss` |
| Reading progress | 3px bar at the top of article pages. | `js/main.js`, `_sass/5-components/_reading.scss` |
| Heading anchors | `#` link after each h2/h3, shown on hover or focus. | `js/main.js`, `_data/i18n.yml`, `_includes/javascripts.html` |
| Series navigation | "Previous / Next in this series" cards at the end of articles in an ordered series (`rel=prev/next`). | `_includes/series-next.html`, `_layouts/post.html`, `_sass/5-components/_series.scss`, `_data/i18n.yml` |
| Date line | Sentence case instead of capitals. | `_sass/5-components/_article-page.scss` |
| Claude Code note | Restyled as a small muted line (matched on its link, posts unchanged). | `_sass/5-components/_reading.scss` |
| Dark mode | Follows the visitor's system setting when no choice is stored; a toggle click stores a choice that wins. | `_includes/head.html`, `js/main.js`, comments in `_theme.scss` and `default.html` |
| Print | Only the article prints: sidebar, buttons, footer, related posts and comments hidden, external link targets written out, code wraps. | `_sass/5-components/_print.scss` |
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

### 4. Device check

All checks so far used Chrome with off-screen and on-page iframes. A check on a real phone (iOS Safari, Android Chrome) would cover touch scrolling of tables and the sticky elements.

### 5. Lighthouse and contrast

Not measured yet: Lighthouse accessibility and performance scores, colour contrast of the muted greys (`--text-muted`, `$gray`), Core Web Vitals. See the Gaps of the `website-design-check` skill.
