---
name: website-design-check
description: "Check the reader experience of the access-denied Jekyll site: static source checks (heading nesting, Key Terms placement, image alt, deprecated PlantUML syntax), a local Docker preview, and in-browser measurements at phone, tablet and desktop widths (line length, tables, code, images, TOC) with Claude in Chrome. Use when asked to review the site design, after changing anything in _sass/, _layouts/, _includes/ or js/, or when a reader reports that something renders strangely."
disable-model-invocation: false
---

# Website design check

Checks how an article of this site reads on a phone, a tablet and a desktop, and whether the
sources contain patterns known to render badly. It was built on 2026-11-18 from the review that
produced `DESIGN_IMPROVEMENT.md` (repository root) and the fixes in
`_sass/5-components/_reading.scss`. Read that file first: it lists what was already fixed and the
open items, so a check does not report a known item as new.

Walk the **Completion checklist** at the end before reporting.

## 1. Static checks (no build)

```bash
python3 .claude/skills/website-design-check/scripts/check_static.py            # whole site
python3 .claude/skills/website-design-check/scripts/check_static.py _posts/<file>.md   # one post
```

Run from the repository root. `FAIL` lines must be fixed before a design review is called clean;
`WARN` lines are reported.

| Check | Level | What it catches | Fix |
|---|---|---|---|
| `heading-nesting` | FAIL | a `###` right after `## What you need to know first`, so the article's sections become sub-sections of the prerequisites | add a `##` parent heading after the prerequisites |
| `key-terms` | FAIL | `### Key Terms` not directly under `## Annex` | move it, see `create-article` |
| `img-alt` | FAIL | `![](...)` | write an alt text that says what the figure shows |
| `table-blank` | FAIL | table with no blank line before it (kramdown prints it as text) | add the blank line |
| `puml-deprecated` | FAIL | activity line `#color:text;`; PlantUML then prints a yellow "This syntax is deprecated" box **inside the PNG** | write `:text; <<#color>>` and re-render with `plantuml -tpng <file>.puml` |
| `bare-toc` | WARN | `[TOC]` not alone on its line (`_layouts/post.html` replaces only `<p>[TOC]</p>`) | put it on its own line |
| `puml-png` | WARN | `.puml` with no `.png`, or a `.png` older than its source | re-render, or confirm the PNG has another name |

## 2. Local preview in Docker

Use the `docker-ruby-app` skill; nothing is installed on the host. From the repository root:

```bash
export RUBYDOCK_SCRATCH=<session scratchpad>
~/.claude/skills/docker-ruby-app/scripts/rubydock -p 4000 -c "$PWD" \
  sh -c 'bundle install --quiet && bundle exec jekyll serve --host 0.0.0.0 --port 4000 --baseurl /access-denied'
```

- Run it in the background and wait for `Server running` in its output (first build about 1 to 3.5 minutes).
- `-c` serves a **copy** taken at start: after editing a Sass, layout or post file, stop the
  container (`docker ps --filter publish=4000 --format '{{.Names}}' | xargs -r docker stop`) and
  start it again. A container that answers 404 lost its copy; stop it and restart.
- The server can be killed when memory runs low; restart it only when the user asks.
- A post that is not published yet (404 on `https://rya-sge.github.io/access-denied/...`) can only
  be checked locally.

## 3. Measure in the browser

Load the Chrome tools in one call (see the `anthropic-skills:chrome-browser` skill), call
`tabs_context_mcp`, open a new tab on the article (local `http://127.0.0.1:4000/access-denied/...`
or the live site), then pass the whole of `scripts/measure_layout.js` to `javascript_tool`.

The script loads the page in off-screen iframes at 360, 390, 768, 1024, 1280, 1440 and 1920 px and
returns one object per width. It works when Chrome refuses `resize_window`, which happened on
2026-11-18: the window stays at its tiled size.

### What to measure

| Field | Expected | Why |
|---|---|---|
| `pageHorizontalScroll` | `false` at every width | a sideways-scrolling page on a phone is the worst reading defect |
| `charsPerLine` | 60-85 from 768px up; 30-45 on phones | above about 90 the eye loses the next line; the live site measured 134 before the 2026-11-18 fix |
| `fontSize` | `17px` from 481px, `16px` below | set in `_reading.scss` |
| `tablesOutsideCard` | `0` | a table must scroll inside its box, never past the card |
| `tablesNotAlignedWithText` | `0` | tables start at the text column's left edge |
| `tablesWithEmptyBorderArea` | `0` | the bordered box is wider than the rows; this was the Jenkins Severity table bug |
| `tablesScrolling` | `0` from 768px; on phones, only tables with 4 or more columns | report the count per width |
| `codeBlocksScrolling` | any on phones; `0` from 1280px except deliberately long lines | code scrolls instead of wrapping, by design |
| `imagesWiderThanCard` | `0` | |
| `tocColumns` | `"2"` from 1100px, `"auto"` below | the inline TOC; from 1280px it is hidden (`body.has-toc-rail`) because the sticky TOC shows in the right column |

### Site frame (since 2026-11-18)

The left sidebar was replaced by a sticky top bar (`_includes/topbar.html`, `_sass/5-components/_topbar.scss`). Check on each sampled page:

- the bar spans the window and its inner row lines up with the main column (both 1200px max);
- below 900px: name, theme switch and menu button only; the menu opens and closes (`aria-expanded`), Escape closes it;
- the bar hides on scroll down and returns on scroll up. Test with real wheel scrolling (`computer` → `scroll`) on the page itself: inside an iframe Chrome throttles scroll events and the check gives false failures;
- from 1280px on articles, `body` has `has-toc-rail` and the TOC sits right of a 900px card;
- exactly one `#js-search-input` per page, and a search returns results.

### What to look at

Numbers miss what looks wrong. Take screenshots at a phone width and at desktop:

- For a phone view when the window cannot be resized, insert a visible 390 × 800 iframe of the same
  URL at the top left (`position: fixed; z-index: 99999`), scroll *inside* it to the section, and
  use `computer` → `zoom` on the region `[0, 0, 394, 804]`. Remove the iframe afterwards.
- Look at: the article header and the first screen on a phone (how much of the article is
  visible); one table of each kind (narrow numeric, wide Key Terms); a code block; a PlantUML
  diagram (read a label: yellow warning box? labels legible after a click-to-zoom?); dark mode
  (`document.documentElement.setAttribute('data-theme','dark')`).
- Check the console with `read_console_messages` and a pattern; errors from browser extensions
  (MetaMask, wallets) are not site errors.

### Pages to sample

At least: one long technical article with tables and code (for example
`2026/11/17/jenkins-security/`), one with diagrams and a series box
(`2026/06/29/linux-advanced-security-seccomp-lsm/`), one older post from 2024, and the home page.

## 4. Report and fix

- Report per page and width: the measured values that miss the table above, with a screenshot of
  each visual defect.
- Fix in the Sass partial that owns the rule (`_sass/5-components/_reading.scss` for the article
  body, `_toc.scss`, `3-elements/_pre.scss`, `_code.scss`, `_blockquote.scss`), keep the change
  scoped to `.c-wrap-content` when it concerns articles only, and explain the reason in a comment,
  as the existing partials do.
- Jekyll 3.10 compiles Sass with libsass: wrap CSS `max()`, `min()` and `clamp()` that mix units in
  `unquote("...")`, or the build may fail.
- Restart the preview, re-run `measure_layout.js` and the static checks, and record the fix in the
  "Done" table of `DESIGN_IMPROVEMENT.md`; add anything left open to its "To do" list.
- Propose a one-line commit message (see `CLAUDE.md`). Do not commit unless asked.

## Completion checklist

Tick an item only with its evidence; mark an item that does not apply N/A with the reason, and tell
the user what was not done.

**Static**
- [ ] `scripts/check_static.py` run on the scope of the review; FAIL count reported, every FAIL fixed or listed as open.

**Preview**
- [ ] Local server answered 200 on the sampled pages after the last change (or N/A: only the live site was reviewed).

**Measurements**
- [ ] `scripts/measure_layout.js` run on every sampled page; values outside the "What to measure" table reported per width.
- [ ] Phone and desktop screenshots taken for each sampled page; dark mode checked on at least one.
- [ ] Console checked; site errors separated from extension errors.

**Fixes and wrap-up**
- [ ] Each fix re-measured after a server restart, with the before and after values.
- [ ] `DESIGN_IMPROVEMENT.md` updated (Done and To do).
- [ ] Browser tabs opened for the check closed; preview server left running only if the user wants it.
- [ ] Commit message proposed.

## Related skills

- `docker-ruby-app`: runs the Jekyll preview (step 2).
- `anthropic-skills:chrome-browser`: how to drive Chrome; read it before step 3.
- `create-article`: the source of the section rules that `check_static.py` enforces (prerequisites, Key Terms, alt text).
- `create-plantuml-diagram`: when a diagram must be redrawn rather than only re-rendered.
- `check-article-ai`: for the wording of articles; this skill covers layout only.

## Gaps

| Gap | Why it matters | What to read or verify |
|---|---|---|
| The thresholds (60-85 characters, 17px) are common typography guidance, not measured on this site's readers. | A review may enforce a value the author does not want. | Confirm with the author; `DESIGN_IMPROVEMENT.md` records the choices made on 2026-11-18. |
| `puml-png` compares file times, which a `git checkout` resets. | It can warn about PNGs that are up to date. | Re-render and compare the image, or `git log -1 --format=%cs` on both files. |
| `measure_layout.js` reads the text column's left edge from the first `h2`; a post with no `h2` gets `null` for the alignment check. | That check is skipped on short posts. | Look at the screenshot instead. |
| The iframe method measures layout, not touch behaviour or real device fonts. | iOS and Android render fonts and scrollbars differently. | Open the local server from a phone on the same network if a device check is needed (bind is 127.0.0.1 today). |
| Lighthouse, contrast ratios and Core Web Vitals are not checked. | Accessibility and loading speed are part of reader experience. | Add a Lighthouse run (Chrome DevTools or `npx lighthouse` in Docker) in a later update. |

## References

- `DESIGN_IMPROVEMENT.md` (repository root), 2026-11-18: review findings, fixes done, open items.
- `_sass/5-components/_reading.scss`, `_sass/5-components/_toc.scss`, `_sass/3-elements/_pre.scss`, `_code.scss`, `_blockquote.scss`: the rules the measurements check.
- `_layouts/post.html`: `[TOC]` substitution, reading time, image lazy loading.
- `~/.claude/skills/docker-ruby-app/SKILL.md`: `rubydock` usage, tested 2026-11-18 with `ruby:3.3`, github-pages 232, Jekyll 3.10.0.
- PlantUML activity diagram colour syntax, plantuml.com/activity-diagram-beta (date unknown); the deprecation message was observed with PlantUML 1.2026.2.
