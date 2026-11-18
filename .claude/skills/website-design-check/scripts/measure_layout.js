// Measure an article page at several screen widths.
//
// Usage: open an article (local preview or live site) in Chrome, then pass the
// whole file to mcp__claude-in-chrome__javascript_tool (action javascript_exec).
// It loads the same URL in off-screen iframes of each width, so it works even
// when Chrome refuses to resize the window, and returns one object per width.
//
// Read the result against the thresholds in SKILL.md ("What to measure").
// Edit WIDTHS to add a size; nothing else needs changing.

const WIDTHS = [360, 390, 768, 1024, 1280, 1440, 1920];

// Run right after a navigation, the body may not exist yet.
while (document.readyState !== 'complete') await new Promise(r => setTimeout(r, 200));

const results = {};
for (const w of WIDTHS) {
  const f = document.createElement('iframe');
  f.src = location.href;
  Object.assign(f.style, {
    position: 'absolute', left: '-6000px', top: '0',
    width: w + 'px', height: '900px', border: '0'
  });
  document.body.appendChild(f);
  await new Promise(r => { f.onload = r; });
  await new Promise(r => setTimeout(r, 800));

  const d = f.contentDocument;
  const win = f.contentWindow;
  const card = d.querySelector('.c-wrap-content');
  if (!card) { results[w] = 'no .c-wrap-content: not an article page'; f.remove(); continue; }
  const cardRect = card.getBoundingClientRect();

  // Characters per line, from the first long paragraph of the body.
  const p = [...d.querySelectorAll('.c-wrap-content > p')].find(e => e.innerText.length > 300);
  let charsPerLine = null;
  if (p) {
    const range = d.createRange();
    range.selectNodeContents(p);
    const lines = new Set([...range.getClientRects()].map(r => Math.round(r.top))).size;
    charsPerLine = Math.round(p.innerText.length / lines);
  }

  // Left edge of the text column, read from the first h2 of the body.
  const h2 = d.querySelector('.c-wrap-content > h2');
  const textLeft = h2 ? Math.round(h2.getBoundingClientRect().left) : null;

  const tables = [...card.querySelectorAll('table')];
  const pres = [...card.querySelectorAll('pre')];
  const imgs = [...card.querySelectorAll('img')];

  results[w] = {
    pageHorizontalScroll: d.documentElement.scrollWidth > w,
    cardWidth: Math.round(cardRect.width),
    fontSize: p ? win.getComputedStyle(p).fontSize : null,
    charsPerLine,
    tables: tables.length,
    tablesScrolling: tables.filter(t => t.scrollWidth > t.clientWidth + 1).length,
    tablesOutsideCard: tables.filter(t => t.getBoundingClientRect().right > cardRect.right + 1).length,
    tablesNotAlignedWithText: textLeft === null ? null :
      tables.filter(t => Math.abs(Math.round(t.getBoundingClientRect().left) - textLeft) > 2).length,
    tablesWithEmptyBorderArea: tables.filter(t => {
      const row = t.querySelector('tr');
      return row && t.getBoundingClientRect().width - row.getBoundingClientRect().width > 4;
    }).length,
    codeBlocks: pres.length,
    codeBlocksScrolling: pres.filter(e => e.scrollWidth > e.clientWidth + 1).length,
    imagesWiderThanCard: imgs.filter(i => i.getBoundingClientRect().width > cardRect.width + 1).length,
    tocColumns: (() => {
      const t = d.querySelector('.c-toc__list');
      return t ? win.getComputedStyle(t).columnCount : null;
    })()
  };
  f.remove();
}
results;
