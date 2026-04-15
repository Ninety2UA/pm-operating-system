#!/usr/bin/env node
/**
 * Render slides: generate HTML from slides.json (if needed), measure overflow,
 * screenshot to PNG.
 *
 * Usage:
 *   node render.js <out-dir> [<slides-json-path>]
 *
 * Default slides-json-path: <out-dir>/slides.json
 *
 * Behavior:
 *   1. If slides.json exists, for each slide entry without a matching
 *      NN-<id>.html file in <out-dir>, generate the HTML from slide-template.html
 *      + layout-specific markup. Existing NN-<id>.html files are preserved
 *      (user hand-edits win over spec).
 *   2. Discover NN-<slug>.html files in <out-dir>, sorted.
 *   3. For each: launch Playwright, wait for fonts, measure overflow on .slide,
 *      screenshot to <out-dir>/slides/NN-<slug>.png at 2x DPR.
 *   4. Write .render-report.json with per-slide measurements.
 *   5. Exit code 2 if any slide has overflow; 0 otherwise.
 *
 * Backward compatible: if no slides.json is present, behaves exactly as before.
 */

// Playwright is required lazily inside main() — lets spec validation + HTML
// generation run (and report errors) even when Playwright isn't installed yet.
const fs = require('fs');
const path = require('path');
const http = require('http');

const SLIDE_W = 1920;
const SLIDE_H = 1080;
const SCRIPT_DIR = __dirname;
// Port 0 = let OS assign an ephemeral free port (avoids conflicts with other
// services). Actual port is read from server.address().port after listen().

const outDir = process.argv[2];
if (!outDir) {
  console.error('Usage: node render.js <out-dir> [<slides-json-path>]');
  process.exit(1);
}

const absOut = path.resolve(outDir);
const slidesOut = path.join(absOut, 'slides');
if (!fs.existsSync(slidesOut)) fs.mkdirSync(slidesOut, { recursive: true });

const specPath = process.argv[3] || path.join(absOut, 'slides.json');

// ---------------------------------------------------------------------------
// Spec loading + validation
// ---------------------------------------------------------------------------

function loadSpec(p) {
  if (!fs.existsSync(p)) return null;
  const raw = JSON.parse(fs.readFileSync(p, 'utf8'));
  validateSpec(raw, p);
  return raw;
}

function validateSpec(spec, specPath) {
  const errors = [];
  if (!spec.deck || typeof spec.deck !== 'object') errors.push('deck object required');
  else {
    if (!spec.deck.title) errors.push('deck.title required');
    if (!spec.deck.date) errors.push('deck.date required');
  }
  if (!Array.isArray(spec.slides)) errors.push('slides array required');
  else {
    const ids = new Set();
    spec.slides.forEach((s, i) => {
      const at = `slides[${i}]`;
      if (!s.id) errors.push(`${at}.id required`);
      else if (!/^[a-z0-9-]+$/.test(s.id)) errors.push(`${at}.id must match ^[a-z0-9-]+$ (got "${s.id}")`);
      else if (ids.has(s.id)) errors.push(`${at}.id "${s.id}" duplicated`);
      else ids.add(s.id);

      const layouts = ['hero', 'title-body', 'split', 'headline-chart', 'big-number'];
      if (!layouts.includes(s.layout)) errors.push(`${at}.layout must be one of ${layouts.join('|')} (got "${s.layout}")`);

      if (s.render && !['auto', 'image', 'editable'].includes(s.render)) {
        errors.push(`${at}.render must be auto|image|editable if set (got "${s.render}")`);
      }

      if (!s.content || typeof s.content !== 'object') errors.push(`${at}.content required`);
      else {
        const required = {
          'hero': ['hero'],
          'title-body': ['title', 'body'],
          'split': ['left', 'right'],
          'headline-chart': ['title', 'chart_image_path', 'source'],
          'big-number': ['number', 'caption', 'source'],
        };
        for (const key of required[s.layout] || []) {
          if (s.content[key] === undefined || s.content[key] === null || s.content[key] === '') {
            errors.push(`${at}.content.${key} required for layout "${s.layout}"`);
          }
        }
      }
    });
  }
  if (errors.length) {
    console.error(`Spec validation failed (${specPath}):`);
    errors.forEach((e) => console.error(`  - ${e}`));
    process.exit(3);
  }
}

// ---------------------------------------------------------------------------
// HTML generation from spec
// ---------------------------------------------------------------------------

function loadTemplateStyles() {
  const tplPath = path.join(SCRIPT_DIR, 'slide-template.html');
  const tpl = fs.readFileSync(tplPath, 'utf8');
  // Extract <head> block so slides inherit fonts + base CSS
  const headMatch = tpl.match(/<head>([\s\S]*?)<\/head>/);
  return headMatch ? headMatch[1] : '';
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function themeCssVars(deck, slide) {
  const accent = slide.accent || deck.accent || '#3b82f6';
  const theme = deck.theme || 'dark';
  if (theme === 'light') {
    return `--bg:#ffffff;--text-primary:#0f172a;--text-secondary:#475569;--accent:${accent};`;
  }
  return `--bg:#0f172a;--text-primary:#f8fafc;--text-secondary:#94a3b8;--accent:${accent};`;
}

function renderHero(c) {
  const sub = c.subtitle ? `<h2 class="subtitle" style="margin-top:32px;">${escapeHtml(c.subtitle)}</h2>` : '';
  return `<div class="slide layout-hero">
    <h1 class="title-hero">${escapeHtml(c.hero)}</h1>
    ${sub}
  </div>`;
}

function renderTitleBody(c) {
  const bullets = (c.body || []).map((b) => `<li>${escapeHtml(b)}</li>`).join('\n      ');
  const source = c.source ? `<div class="source-footer">${escapeHtml(c.source)}</div>` : '';
  return `<div class="slide layout-title-body">
    <h1 class="title-slide">${escapeHtml(c.title)}</h1>
    <ul class="body">
      ${bullets}
    </ul>
    ${source}
  </div>`;
}

function renderSplit(c) {
  function col(side) {
    const s = c[side];
    const sub = s.subtitle ? `<h2 class="subtitle">${escapeHtml(s.subtitle)}</h2>` : '';
    let body;
    if (Array.isArray(s.body)) {
      body = `<ul class="body">${s.body.map((b) => `<li>${escapeHtml(b)}</li>`).join('')}</ul>`;
    } else {
      body = `<p class="body">${escapeHtml(s.body)}</p>`;
    }
    return `<div class="col">${sub}${body}</div>`;
  }
  return `<div class="slide layout-split">
    ${col('left')}
    ${col('right')}
  </div>`;
}

function renderHeadlineChart(c) {
  const chartSrc = escapeHtml(c.chart_image_path);
  return `<div class="slide layout-headline-chart">
    <h1 class="title-slide">${escapeHtml(c.title)}</h1>
    <div class="chart">
      <img src="${chartSrc}" alt="" style="max-width:100%;max-height:100%;object-fit:contain;">
    </div>
    <div class="source-footer">${escapeHtml(c.source)}</div>
  </div>`;
}

function renderBigNumber(c) {
  return `<div class="slide layout-big-number">
    <div class="hero-number">${escapeHtml(c.number)}</div>
    <div class="caption">${escapeHtml(c.caption)}</div>
    <div class="source">${escapeHtml(c.source)}</div>
  </div>`;
}

const LAYOUT_RENDERERS = {
  'hero': renderHero,
  'title-body': renderTitleBody,
  'split': renderSplit,
  'headline-chart': renderHeadlineChart,
  'big-number': renderBigNumber,
};

function renderSlideHtml(slide, deck, headBlock) {
  const inner = LAYOUT_RENDERERS[slide.layout](slide.content);
  const vars = themeCssVars(deck, slide);
  return `<!DOCTYPE html>
<html lang="en">
<head>
${headBlock.trim()}
<style>.slide{${vars}}</style>
</head>
<body>
  ${inner}
</body>
</html>
`;
}

function filenameFor(slide, index) {
  const nn = String(index + 1).padStart(2, '0');
  return `${nn}-${slide.id}.html`;
}

function generateHtmlFromSpec(spec, outDir) {
  const headBlock = loadTemplateStyles();
  const generated = [];
  const skipped = [];
  spec.slides.forEach((slide, index) => {
    const fname = filenameFor(slide, index);
    const fpath = path.join(outDir, fname);
    if (fs.existsSync(fpath)) {
      skipped.push(fname);
    } else {
      const html = renderSlideHtml(slide, spec.deck, headBlock);
      fs.writeFileSync(fpath, html);
      generated.push(fname);
    }
  });
  if (generated.length) console.log(`Generated ${generated.length} slide HTML file(s) from spec:`);
  generated.forEach((f) => console.log(`  + ${f}`));
  if (skipped.length) console.log(`Preserved ${skipped.length} existing slide HTML file(s) (hand-edited):`);
  skipped.forEach((f) => console.log(`  · ${f}`));
}

// ---------------------------------------------------------------------------
// Static file server (unchanged from v1)
// ---------------------------------------------------------------------------

function startServer(rootDir) {
  const mime = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.json': 'application/json',
  };
  const server = http.createServer((req, res) => {
    let urlPath = decodeURIComponent(req.url.split('?')[0]);
    if (urlPath === '/') urlPath = '/index.html';
    const filePath = path.join(rootDir, urlPath);
    if (!filePath.startsWith(rootDir)) {
      res.writeHead(403);
      return res.end('forbidden');
    }
    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.writeHead(404);
        return res.end('not found');
      }
      const ext = path.extname(filePath).toLowerCase();
      res.writeHead(200, { 'Content-Type': mime[ext] || 'application/octet-stream' });
      res.end(data);
    });
  });
  // listen(0) = OS-assigned ephemeral port; read actual port via server.address().port
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

(async () => {
  // Step 1: Generate HTML from spec if a spec exists
  const spec = loadSpec(specPath);
  if (spec) {
    console.log(`Using spec: ${specPath}`);
    generateHtmlFromSpec(spec, absOut);
  } else {
    console.log(`(no slides.json at ${specPath} — using existing HTML files only)`);
  }

  // Step 2: Discover slide HTML files (NN-slug.html), sorted by NN
  const slideFiles = fs
    .readdirSync(absOut)
    .filter((f) => /^\d+-.*\.html$/.test(f))
    .sort();

  if (slideFiles.length === 0) {
    console.error(`No slide HTML files found in ${absOut} (expected pattern: NN-slug.html)`);
    process.exit(1);
  }

  // Step 3: Render and measure (Playwright required lazily here)
  let chromium;
  try {
    ({ chromium } = require('playwright'));
  } catch (err) {
    console.error('Playwright is not installed. Run: npm install playwright && npx playwright install chromium');
    process.exit(4);
  }

  const server = await startServer(absOut);
  const PORT = server.address().port;
  console.log(`Static server: http://127.0.0.1:${PORT} (root: ${absOut})`);

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: SLIDE_W, height: SLIDE_H },
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();

  const results = [];
  let anyOverflow = false;

  for (const file of slideFiles) {
    const url = `http://127.0.0.1:${PORT}/${file}`;
    await page.goto(url, { waitUntil: 'networkidle' });

    // Wait for fonts to be ready (critical for typography-driven layouts)
    await page.evaluate(() => document.fonts.ready);

    const measurements = await page.evaluate(() => {
      const el = document.querySelector('.slide');
      if (!el) return null;
      return {
        containerW: el.offsetWidth,
        containerH: el.offsetHeight,
        contentW: el.scrollWidth,
        contentH: el.scrollHeight,
        overflowW: el.scrollWidth - el.offsetWidth,
        overflowH: el.scrollHeight - el.offsetHeight,
      };
    });

    if (!measurements) {
      console.error(`  ✖ ${file}: no .slide element found`);
      continue;
    }

    const { overflowW, overflowH } = measurements;
    const status = overflowW === 0 && overflowH === 0 ? '✓' : '✖';
    if (overflowW !== 0 || overflowH !== 0) anyOverflow = true;

    const slideEl = await page.$('.slide');
    const pngName = file.replace(/\.html$/, '.png');
    const pngPath = path.join(slidesOut, pngName);
    await slideEl.screenshot({ path: pngPath });

    const overflowMsg =
      overflowW === 0 && overflowH === 0
        ? 'no overflow'
        : `overflow: ${overflowW}px wide, ${overflowH}px tall`;

    console.log(`  ${status} ${file} → slides/${pngName} (${overflowMsg})`);
    results.push({ file, ...measurements, png: `slides/${pngName}` });
  }

  fs.writeFileSync(
    path.join(absOut, '.render-report.json'),
    JSON.stringify({ rendered_at: new Date().toISOString(), slides: results }, null, 2)
  );

  await browser.close();
  server.close();

  if (anyOverflow) {
    console.error('\n⚠  One or more slides have overflow. Edit the HTML and re-run.');
    process.exit(2);
  }

  console.log('\n✓ All slides rendered with no overflow.');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
