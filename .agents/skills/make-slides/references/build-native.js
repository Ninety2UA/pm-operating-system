#!/usr/bin/env node
/**
 * build-native.js — build native Google Slides text-box slides from slides.json
 * using the gws CLI. Invoked by /make-slides SKILL.md in editable and mixed modes.
 *
 * Usage:
 *   node build-native.js <out-dir> <presentation-id> [--mode=editable|mixed]
 *
 * Modes:
 *   editable — every slide becomes native text boxes (except chart regions in
 *              headline-chart layout, which stay as embedded images)
 *   mixed    — per-slide: if slide.render === "image", the whole slide becomes
 *              a full-bleed PNG from OUT_DIR/slides/NN-<id>.png. Otherwise
 *              editable (same as above).
 *
 * Prerequisites:
 *   - <presentation-id> refers to an already-created presentation (caller uses
 *     `gws slides presentations create` first)
 *   - For mixed mode with image-marked slides: OUT_DIR/slides/NN-<id>.png must
 *     already exist (caller runs render.js first)
 *   - For any headline-chart slide: chart_image_path in spec must resolve to
 *     a readable PNG/SVG on local disk
 *   - gws CLI authenticated
 *
 * Output:
 *   - Writes combined batchUpdate JSON to <out-dir>/.batchUpdate-native.json
 *   - Invokes `gws slides presentations batchUpdate`
 *   - On success, prints presentation ID to stdout and exits 0
 *   - Warnings about layout-fidelity drops go to stderr
 *
 * Security: uses execFileSync with argv arrays — no shell interpolation.
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

// ---------------------------------------------------------------------------
// CLI args
// ---------------------------------------------------------------------------

const outDir = process.argv[2];
const presId = process.argv[3];
const modeArg = process.argv.slice(4).find((a) => a.startsWith('--mode='));
const MODE = modeArg ? modeArg.split('=')[1] : 'editable';

if (!outDir || !presId) {
  console.error('Usage: node build-native.js <out-dir> <presentation-id> [--mode=editable|mixed]');
  process.exit(1);
}
if (!['editable', 'mixed'].includes(MODE)) {
  console.error(`Invalid --mode: ${MODE} (expected editable or mixed)`);
  process.exit(1);
}
// Guard the presentation ID against unexpected characters before passing to gws.
// Google presentation IDs are alphanumerics with hyphens and underscores.
if (!/^[A-Za-z0-9_-]+$/.test(presId)) {
  console.error(`Invalid presentation ID: ${presId}`);
  process.exit(1);
}

const absOut = path.resolve(outDir);
const specPath = path.join(absOut, 'slides.json');
if (!fs.existsSync(specPath)) {
  console.error(`slides.json not found at ${specPath}`);
  process.exit(1);
}

const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));

// ---------------------------------------------------------------------------
// gws helper — safe argv-based invocation (no shell)
// ---------------------------------------------------------------------------

function runGws(args) {
  // args: array passed directly to execFileSync — no shell interpolation.
  try {
    return execFileSync('gws', args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
  } catch (err) {
    const msg = err.stderr ? err.stderr.toString() : err.message;
    throw new Error(`gws ${args.slice(0, 3).join(' ')} failed: ${msg}`);
  }
}

// ---------------------------------------------------------------------------
// Constants: page geometry, fonts, theme colors
// ---------------------------------------------------------------------------

const PAGE_W = 9144000;  // EMU = 10"
const PAGE_H = 5143500;  // EMU = 5.625" (16:9)
const MARGIN = 457200;   // EMU = 0.5"
const CONTENT_W = PAGE_W - 2 * MARGIN;  // 8229600
// const CONTENT_H = PAGE_H - 2 * MARGIN;  // 4229100 (unused directly)

const FONT_DEFAULT = spec.deck.font_override || 'Open Sans';

function mapWeight(cssWeight) {
  if (cssWeight <= 400) return 400;
  if (cssWeight === 500) return 600; // round up per font-map.md
  return Math.min(cssWeight, 800);
}

const THEME = spec.deck.theme || 'dark';
const DECK_ACCENT = spec.deck.accent || '#3b82f6';

function hexToRgb(hex) {
  const h = hex.replace('#', '');
  const r = parseInt(h.slice(0, 2), 16) / 255;
  const g = parseInt(h.slice(2, 4), 16) / 255;
  const b = parseInt(h.slice(4, 6), 16) / 255;
  return { red: +r.toFixed(4), green: +g.toFixed(4), blue: +b.toFixed(4) };
}

function resolveColor(token, slide) {
  if (typeof token === 'string' && token.startsWith('#')) return hexToRgb(token);
  const accentHex = slide.accent || DECK_ACCENT;
  if (THEME === 'light') {
    const light = { primary: '#0f172a', secondary: '#475569', accent: accentHex, bg: '#ffffff' };
    return hexToRgb(light[token] || '#000000');
  }
  const dark = { primary: '#f8fafc', secondary: '#94a3b8', accent: accentHex, bg: '#0f172a' };
  return hexToRgb(dark[token] || '#ffffff');
}

// ---------------------------------------------------------------------------
// Object ID helpers
// ---------------------------------------------------------------------------

function sid(slideIdx, kind) {
  return `${kind}_${String(slideIdx + 1).padStart(2, '0')}`;
}

function elementProperties(slideObjectId, x, y, w, h) {
  return {
    pageObjectId: slideObjectId,
    size: {
      width: { magnitude: w, unit: 'EMU' },
      height: { magnitude: h, unit: 'EMU' },
    },
    transform: {
      scaleX: 1,
      scaleY: 1,
      translateX: x,
      translateY: y,
      unit: 'EMU',
    },
  };
}

// ---------------------------------------------------------------------------
// Request builders
// ---------------------------------------------------------------------------

function reqCreateSlide(slideObjectId) {
  return {
    createSlide: {
      objectId: slideObjectId,
      slideLayoutReference: { predefinedLayout: 'BLANK' },
    },
  };
}

function reqCreateTextBox(objectId, slideObjectId, x, y, w, h) {
  return {
    createShape: {
      objectId,
      shapeType: 'TEXT_BOX',
      elementProperties: elementProperties(slideObjectId, x, y, w, h),
    },
  };
}

function reqInsertText(objectId, text) {
  return {
    insertText: { objectId, text, insertionIndex: 0 },
  };
}

function reqUpdateTextStyle(objectId, styleOpts) {
  const { fontFamily, fontSizePt, weight, colorRgb, italic = false } = styleOpts;
  const style = {
    fontFamily,
    weightedFontFamily: { fontFamily, weight },
    fontSize: { magnitude: fontSizePt, unit: 'PT' },
    foregroundColor: { opaqueColor: { rgbColor: colorRgb } },
    bold: weight >= 700,
    italic,
  };
  return {
    updateTextStyle: {
      objectId,
      textRange: { type: 'ALL' },
      fields: 'fontFamily,weightedFontFamily,fontSize,foregroundColor,bold,italic',
      style,
    },
  };
}

function reqUpdateParagraphStyle(objectId, alignment, lineSpacing = 140, spaceBelow = 0) {
  const style = { alignment, lineSpacing };
  if (spaceBelow) style.spaceBelow = { magnitude: spaceBelow, unit: 'PT' };
  const fields = spaceBelow ? 'alignment,lineSpacing,spaceBelow' : 'alignment,lineSpacing';
  return {
    updateParagraphStyle: {
      objectId,
      textRange: { type: 'ALL' },
      fields,
      style,
    },
  };
}

function reqCreateBullets(objectId, preset = 'BULLET_DISC_CIRCLE_SQUARE') {
  return {
    createParagraphBullets: {
      objectId,
      textRange: { type: 'ALL' },
      bulletPreset: preset,
    },
  };
}

function reqCreateImage(objectId, slideObjectId, url, x, y, w, h) {
  return {
    createImage: {
      objectId,
      url,
      elementProperties: elementProperties(slideObjectId, x, y, w, h),
    },
  };
}

// ---------------------------------------------------------------------------
// Layout builders — return array of requests per layout
// ---------------------------------------------------------------------------

function styledTextBox(opts) {
  const { objectId, slideObjectId, x, y, w, h, text, font, sizePt, weight, colorRgb, align } = opts;
  if (text === undefined || text === null || text === '') return [];
  return [
    reqCreateTextBox(objectId, slideObjectId, x, y, w, h),
    reqInsertText(objectId, text),
    reqUpdateTextStyle(objectId, { fontFamily: font, fontSizePt: sizePt, weight, colorRgb }),
    reqUpdateParagraphStyle(objectId, align),
  ];
}

function buildHero(slideIdx, slideObjectId, slide) {
  const c = slide.content;
  const reqs = [];
  reqs.push(...styledTextBox({
    objectId: sid(slideIdx, 'hero'),
    slideObjectId,
    x: MARGIN, y: 1714500, w: CONTENT_W, h: 1714500,
    text: c.hero,
    font: FONT_DEFAULT, sizePt: 110, weight: mapWeight(800),
    colorRgb: resolveColor('primary', slide),
    align: 'CENTER',
  }));
  if (c.subtitle) {
    reqs.push(...styledTextBox({
      objectId: sid(slideIdx, 'subtitle'),
      slideObjectId,
      x: MARGIN, y: 3429000, w: CONTENT_W, h: 400000,
      text: c.subtitle,
      font: FONT_DEFAULT, sizePt: 52, weight: mapWeight(600),
      colorRgb: resolveColor('secondary', slide),
      align: 'CENTER',
    }));
  }
  return reqs;
}

function buildTitleBody(slideIdx, slideObjectId, slide) {
  const c = slide.content;
  const reqs = [];
  reqs.push(...styledTextBox({
    objectId: sid(slideIdx, 'title'),
    slideObjectId,
    x: MARGIN, y: MARGIN, w: CONTENT_W, h: 685800,
    text: c.title,
    font: FONT_DEFAULT, sizePt: 72, weight: mapWeight(700),
    colorRgb: resolveColor('primary', slide),
    align: 'START',
  }));

  const bodyText = (c.body || []).join('\n');
  const bodyId = sid(slideIdx, 'body');
  if (bodyText) {
    reqs.push(reqCreateTextBox(bodyId, slideObjectId, MARGIN, 1371600, CONTENT_W, 3200000));
    reqs.push(reqInsertText(bodyId, bodyText));
    reqs.push(reqUpdateTextStyle(bodyId, {
      fontFamily: FONT_DEFAULT,
      fontSizePt: 40,
      weight: mapWeight(400),
      colorRgb: resolveColor('primary', slide),
    }));
    reqs.push(reqUpdateParagraphStyle(bodyId, 'START', 140, 24));
    reqs.push(reqCreateBullets(bodyId, 'BULLET_DISC_CIRCLE_SQUARE'));
  }

  if (c.source) {
    reqs.push(...styledTextBox({
      objectId: sid(slideIdx, 'source'),
      slideObjectId,
      x: MARGIN, y: 4800000, w: CONTENT_W, h: 200000,
      text: c.source,
      font: FONT_DEFAULT, sizePt: 24, weight: mapWeight(400),
      colorRgb: resolveColor('secondary', slide),
      align: 'START',
    }));
  }
  return reqs;
}

function buildSplit(slideIdx, slideObjectId, slide) {
  const c = slide.content;
  const reqs = [];
  const colW = 3924300;
  const rightX = MARGIN + colW + 381000;

  function addColumn(side, x) {
    const col = c[side];
    if (!col) return;
    if (col.subtitle) {
      reqs.push(...styledTextBox({
        objectId: sid(slideIdx, `${side}sub`),
        slideObjectId,
        x, y: 1371600, w: colW, h: 400000,
        text: col.subtitle,
        font: FONT_DEFAULT, sizePt: 52, weight: mapWeight(600),
        colorRgb: resolveColor('secondary', slide),
        align: 'START',
      }));
    }
    const bodyText = Array.isArray(col.body) ? col.body.join('\n') : col.body;
    if (bodyText) {
      const bodyId = sid(slideIdx, `${side}body`);
      reqs.push(reqCreateTextBox(bodyId, slideObjectId, x, 1848000, colW, 2800000));
      reqs.push(reqInsertText(bodyId, bodyText));
      reqs.push(reqUpdateTextStyle(bodyId, {
        fontFamily: FONT_DEFAULT,
        fontSizePt: 40,
        weight: mapWeight(400),
        colorRgb: resolveColor('primary', slide),
      }));
      reqs.push(reqUpdateParagraphStyle(bodyId, 'START', 140, 24));
      if (Array.isArray(col.body)) {
        reqs.push(reqCreateBullets(bodyId, 'BULLET_DISC_CIRCLE_SQUARE'));
      }
    }
  }

  addColumn('left', MARGIN);
  addColumn('right', rightX);
  return reqs;
}

function buildHeadlineChart(slideIdx, slideObjectId, slide, chartPublicUrl) {
  const c = slide.content;
  const reqs = [];
  reqs.push(...styledTextBox({
    objectId: sid(slideIdx, 'title'),
    slideObjectId,
    x: MARGIN, y: MARGIN, w: CONTENT_W, h: 685800,
    text: c.title,
    font: FONT_DEFAULT, sizePt: 72, weight: mapWeight(700),
    colorRgb: resolveColor('primary', slide),
    align: 'START',
  }));

  if (chartPublicUrl) {
    reqs.push(reqCreateImage(
      sid(slideIdx, 'chart'),
      slideObjectId,
      chartPublicUrl,
      MARGIN, 1371600, CONTENT_W, 3200000,
    ));
  } else {
    console.error(`⚠  slide ${slide.id}: chart_image_path not resolved; skipping chart.`);
  }

  reqs.push(...styledTextBox({
    objectId: sid(slideIdx, 'source'),
    slideObjectId,
    x: MARGIN, y: 4800000, w: CONTENT_W, h: 200000,
    text: c.source,
    font: FONT_DEFAULT, sizePt: 24, weight: mapWeight(400),
    colorRgb: resolveColor('secondary', slide),
    align: 'START',
  }));
  return reqs;
}

function buildBigNumber(slideIdx, slideObjectId, slide) {
  const c = slide.content;
  const reqs = [];
  reqs.push(...styledTextBox({
    objectId: sid(slideIdx, 'number'),
    slideObjectId,
    x: MARGIN, y: 1500000, w: CONTENT_W, h: 1500000,
    text: c.number,
    font: FONT_DEFAULT, sizePt: 200, weight: mapWeight(800),
    colorRgb: resolveColor('accent', slide),
    align: 'CENTER',
  }));
  reqs.push(...styledTextBox({
    objectId: sid(slideIdx, 'caption'),
    slideObjectId,
    x: MARGIN, y: 3100000, w: CONTENT_W, h: 500000,
    text: c.caption,
    font: FONT_DEFAULT, sizePt: 44, weight: mapWeight(500),
    colorRgb: resolveColor('secondary', slide),
    align: 'CENTER',
  }));
  reqs.push(...styledTextBox({
    objectId: sid(slideIdx, 'source'),
    slideObjectId,
    x: MARGIN, y: 4800000, w: CONTENT_W, h: 200000,
    text: c.source,
    font: FONT_DEFAULT, sizePt: 24, weight: mapWeight(400),
    colorRgb: resolveColor('secondary', slide),
    align: 'CENTER',
  }));
  return reqs;
}

function buildFullBleedImage(slideIdx, slideObjectId, imageUrl) {
  return [
    reqCreateImage(sid(slideIdx, 'fullimage'), slideObjectId, imageUrl, 0, 0, PAGE_W, PAGE_H),
  ];
}

// ---------------------------------------------------------------------------
// Drive upload — argv-safe
// ---------------------------------------------------------------------------

function uploadToDrive(localPath, displayName) {
  if (!fs.existsSync(localPath)) {
    throw new Error(`File not found: ${localPath}`);
  }
  const mimeType = localPath.toLowerCase().endsWith('.svg') ? 'image/svg+xml' : 'image/png';
  const metadata = JSON.stringify({ name: displayName, mimeType });

  const createOut = runGws([
    'drive', 'files', 'create',
    '--json', metadata,
    '--upload', localPath,
    '--upload-content-type', mimeType,
  ]);
  const fileId = JSON.parse(createOut).id;
  if (!fileId) throw new Error(`Drive upload returned no fileId: ${createOut}`);

  runGws([
    'drive', 'permissions', 'create',
    '--params', JSON.stringify({ fileId }),
    '--json', JSON.stringify({ role: 'reader', type: 'anyone' }),
  ]);

  return { fileId, url: `https://drive.google.com/uc?export=view&id=${fileId}` };
}

function getDefaultSlideObjectId(presentationId) {
  // IMPORTANT: narrow the response via `fields` — the unfiltered presentations.get
  // response includes layouts/masters with text content that may contain literal
  // unescaped newlines (a gws output quirk), breaking JSON.parse.
  const out = runGws([
    'slides', 'presentations', 'get',
    '--params', JSON.stringify({ presentationId, fields: 'slides(objectId)' }),
  ]);
  const pres = JSON.parse(out);
  if (!pres.slides || !pres.slides.length) {
    throw new Error(`Presentation ${presentationId} has no slides`);
  }
  return pres.slides[0].objectId;
}

function sendBatchUpdate(presentationId, requests) {
  return runGws([
    'slides', 'presentations', 'batchUpdate',
    '--params', JSON.stringify({ presentationId }),
    '--json', JSON.stringify({ requests }),
  ]);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  const requests = [];
  const uploadedFileIds = [];
  const warnings = [];

  console.error(`Fetching default slide objectId from presentation ${presId}...`);
  const defaultSlideId = getDefaultSlideObjectId(presId);
  console.error(`Default slide: ${defaultSlideId}`);

  spec.slides.forEach((slide, idx) => {
    let effectiveRender = 'editable';
    if (MODE === 'mixed') {
      if (slide.render === 'image') effectiveRender = 'image';
      else effectiveRender = 'editable'; // "auto", "editable", or unset → editable
    }

    const slideObjectId = idx === 0 ? defaultSlideId : sid(idx, 'slide');

    if (idx > 0) {
      requests.push(reqCreateSlide(slideObjectId));
    }

    if (effectiveRender === 'image') {
      const nn = String(idx + 1).padStart(2, '0');
      const pngPath = path.join(absOut, 'slides', `${nn}-${slide.id}.png`);
      if (!fs.existsSync(pngPath)) {
        warnings.push(`slide ${slide.id}: rendered PNG not found at ${pngPath} — falling back to editable layout.`);
      } else {
        const { fileId, url } = uploadToDrive(pngPath, `slide-${nn}-${slide.id}.png`);
        uploadedFileIds.push(fileId);
        requests.push(...buildFullBleedImage(idx, slideObjectId, url));
        return;
      }
    }

    switch (slide.layout) {
      case 'hero':
        requests.push(...buildHero(idx, slideObjectId, slide));
        break;
      case 'title-body':
        requests.push(...buildTitleBody(idx, slideObjectId, slide));
        break;
      case 'split':
        requests.push(...buildSplit(idx, slideObjectId, slide));
        break;
      case 'headline-chart': {
        const chartAbs = path.isAbsolute(slide.content.chart_image_path)
          ? slide.content.chart_image_path
          : path.join(absOut, slide.content.chart_image_path);
        let chartUrl = null;
        if (fs.existsSync(chartAbs)) {
          const { fileId, url } = uploadToDrive(chartAbs, `chart-${slide.id}.png`);
          uploadedFileIds.push(fileId);
          chartUrl = url;
        } else {
          warnings.push(`slide ${slide.id}: chart_image_path not found at ${chartAbs}`);
        }
        requests.push(...buildHeadlineChart(idx, slideObjectId, slide, chartUrl));
        break;
      }
      case 'big-number':
        requests.push(...buildBigNumber(idx, slideObjectId, slide));
        break;
      default:
        warnings.push(`slide ${slide.id}: unknown layout "${slide.layout}" — skipped`);
    }
  });

  if (requests.length === 0) {
    console.error('No requests generated. Exiting.');
    process.exit(0);
  }

  const CHUNK_SIZE = 450;
  const chunks = [];
  for (let i = 0; i < requests.length; i += CHUNK_SIZE) {
    chunks.push(requests.slice(i, i + CHUNK_SIZE));
  }
  console.error(`Generated ${requests.length} request(s) in ${chunks.length} batch(es).`);

  const batchPath = path.join(absOut, '.batchUpdate-native.json');
  fs.writeFileSync(batchPath, JSON.stringify({ requests }, null, 2));
  console.error(`Wrote full request JSON to ${batchPath}`);

  chunks.forEach((chunk, i) => {
    try {
      sendBatchUpdate(presId, chunk);
      console.error(`Batch ${i + 1}/${chunks.length}: applied ${chunk.length} request(s)`);
    } catch (err) {
      console.error(`Batch ${i + 1}/${chunks.length} FAILED:`);
      console.error(err.message);
      console.error(`Request JSON preserved at ${batchPath} for inspection.`);
      process.exit(2);
    }
  });

  if (warnings.length) {
    console.error('\nFidelity warnings:');
    warnings.forEach((w) => console.error(`  ⚠  ${w}`));
  }
  if (uploadedFileIds.length) {
    const idsPath = path.join(absOut, '.uploaded-drive-files.json');
    // Merge with any prior uploads from image-mode runs
    let prior = [];
    if (fs.existsSync(idsPath)) {
      try { prior = JSON.parse(fs.readFileSync(idsPath, 'utf8')).uploaded || []; } catch (_) {}
    }
    fs.writeFileSync(idsPath, JSON.stringify({ uploaded: [...prior, ...uploadedFileIds] }, null, 2));
    console.error(`\n${uploadedFileIds.length} file(s) uploaded to Drive this run. IDs at ${idsPath}.`);
  }

  console.log(presId);
}

try {
  main();
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
