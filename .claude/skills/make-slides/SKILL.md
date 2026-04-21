---
name: make-slides
description: >
  Build polished presentation slides as HTML/CSS at 1920x1080 with a Playwright
  measure → screenshot → iterate loop, then optionally push to Google Slides via
  the gws CLI in any of four modes: image (pixel-perfect, not editable),
  editable (native text boxes), mixed (per-slide choice), or both (two separate
  decks from one run). Use this skill whenever the user says "make slides",
  "build a deck", "create a presentation", "slide deck for", "QBR slides",
  "exec presentation", "demo deck", "pitch slides", "investor deck", "portfolio
  review slides", or needs a visual presentation rather than prose. Push toward
  this whenever the user describes a meeting/talk/review where a deck would be
  the natural artifact.
allowed-tools: Read Write Edit Glob Bash
argument-hint: "<deck-slug> [--google-slides[=image|editable|mixed|both]] [--out <path>]"
---

# Make Slides — HTML/CSS Slide Builder with Playwright + Google Slides Export

Build pixel-perfect 1920×1080 HTML slides, verify with Playwright (overflow check + screenshot), and optionally push to Google Slides in one of four output modes.

## Quick Start

- `/make-slides q1-review` — build locally (HTML + PNG only, no Google Slides)
- `/make-slides q1-review --google-slides` — build + push to Google Slides in **both** modes (two decks: one image-based, one editable) — this is the DEFAULT when `--google-slides` is bare
- `/make-slides q1-review --google-slides=image` — one pixel-perfect image-based deck
- `/make-slides q1-review --google-slides=editable` — one deck with native text boxes (editable in browser, Open Sans fallback)
- `/make-slides q1-review --google-slides=mixed` — one deck, per-slide choice (spec controls via `render` field — charts stay as images, text stays editable)
- `/make-slides q1-review --out ./decks/` — override output directory

## The Four Google Slides Output Modes

| Mode | What you get | Editable? | Fidelity | Best for |
|---|---|---|---|---|
| `image` | One deck, every slide a full-bleed PNG | No | 💯 Perfect | Exec presentations where design matters more than editability |
| `editable` | One deck, every slide native text boxes | Yes | 📉 Limited — Open Sans instead of Inter, no CSS tricks | Collaborator needs to tweak text in the browser |
| `mixed` | One deck, per-slide choice via spec | Per slide | 🎯 Perfect where it matters | Real-world — charts beautiful, titles editable |
| `both` | Two decks from one run (one image, one editable) | One is | 💯 + 📉 | Send pretty one to exec, editable one to collaborator |

**`both` is the default** when `--google-slides` is passed with no value.

If the flag is absent entirely, no Google Slides push happens — you just get HTML/PNG locally.

## Required Inputs

Before starting, confirm:

1. **Deck slug** (kebab-case, used for directory name)
2. **Content** — outline, notes, prose draft, transcript, or topic. Ask if missing.
3. **Audience** — who's this for? (Exec, customer, investor, internal team) — shapes tone/depth
4. **Slide count target** (optional) — let content dictate by default
5. **Style direction** (optional) — dark/light, brand colors, mood. Default: dark, clean type, single accent.

## Prerequisites

Run `command -v npm >/dev/null || { echo "npm not installed — run: brew install node"; exit 1; }` at the start. `/make-slides` depends on Node/Playwright for the render loop; a missing `npm` surfaces a cryptic error deep inside `render.js` otherwise. If `npm` is available but `node_modules/playwright` is missing, run `npm install` at the repo root (the `postinstall` script handles `playwright install chromium`).

## Dimensions

All slides are **1920×1080px** (16:9 standard). Non-negotiable.

## Design Rules

Read `.claude/skills/make-slides/references/design-rules.md` before building. It covers typography ladder, color discipline, layout patterns, chart guidance, and what NOT to do. The rules are opinionated — follow them unless the user overrides explicitly.

## Content Spec: `slides.json`

The skill uses a JSON spec (`OUT_DIR/slides.json`) as the single source of truth for slide content. Two renderers consume it:

- **`render.js`** → generates HTML, runs Playwright, screenshots to PNG
- **`build-native.js`** → builds native Google Slides text boxes via the gws API

Full schema at `.claude/skills/make-slides/references/slides-spec.schema.md`. Five supported layouts: `hero`, `title-body`, `split`, `headline-chart`, `big-number`.

## Workflow

### Step 1: Setup + Flag Parse

Compute `OUT_DIR`:
- Default: `knowledge/decks/<deck-slug>/`
- Override: `<--out path>/<deck-slug>/`

Create `OUT_DIR` and `OUT_DIR/slides/`. Reject any `<deck-slug>` containing `..`, `/`, or characters besides letters, numbers, hyphens.

**Parse `--google-slides` flag:**

```bash
GS_MODE=""                             # empty = skip Google Slides
for arg in "$@"; do
  case "$arg" in
    --google-slides)            GS_MODE="both" ;;    # bare → both (default)
    --google-slides=image)      GS_MODE="image" ;;
    --google-slides=editable)   GS_MODE="editable" ;;
    --google-slides=mixed)      GS_MODE="mixed" ;;
    --google-slides=both)       GS_MODE="both" ;;
    --google-slides=*)          echo "Error: unknown --google-slides mode: $arg"; exit 1 ;;
  esac
done
```

**Check Playwright availability:**

Playwright is declared as a dependency in `package.json` at the personal-os repo root. The preferred install path is `npm install` at the repo root (also offered during `./setup.sh`). The `postinstall` script runs `npx playwright install chromium` automatically.

```bash
# Preferred — install all node deps from the repo root (picks up package.json)
cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || cd .
if ! node -e "require.resolve('playwright')" 2>/dev/null; then
  if [ -f package.json ] && grep -q '"playwright"' package.json; then
    echo "Installing Node deps (playwright + Chromium, one-time)..."
    npm install --no-audit --no-fund
  else
    # Fallback for non-personal-os workspaces: install playwright standalone
    echo "Installing playwright standalone..."
    npm install playwright
    npx playwright install chromium
  fi
fi
```

If first-time setup, tell the user: "Installing Playwright + Chromium (one-time, Chromium is ~150MB but skipped if already cached at ~/Library/Caches/ms-playwright/)."

### Step 2: Plan the Deck → Produce `slides.json`

From the content, draft a structured spec. Present to the user as a layout-level outline (just `layout + title` per slide). Get approval before writing `slides.json`.

Example outline presentation:

```
Planned 5 slides for "Q1 Portfolio Review":
  1. hero           → title slide
  2. title-body     → "The three things" (TL;DR bullets)
  3. big-number     → "287% YoY pipeline growth"
  4. headline-chart → "Conversion dropped 18% after Friday push"
  5. title-body     → "What we need from you" (asks)
```

For **exec/QBR/investor** decks, use BLUF (Bottom Line Up Front):
- Slide 1: `hero` title
- Slide 2: `title-body` TL;DR (the answer / recommendation / ask in 3 bullets)
- Middle slides: evidence
- Final slide: `title-body` with asks / next steps

For **demo** decks:
- Slide 1: `hero` title
- Slide 2: `title-body` problem
- Slide 3: `hero` solution headline
- Middle slides: `headline-chart` demo screenshots
- Final: `title-body` CTA + contact

After user approval, write `OUT_DIR/slides.json` following the schema in `slides-spec.schema.md`. Include deck-level metadata (`title`, `audience`, `date`, `theme`, `accent`). Each slide entry gets `id`, `layout`, `content`.

### Step 3: Generate HTML from Spec

Run the render script — it reads `slides.json`, generates HTML per slide from the template, then runs Playwright:

```bash
node .claude/skills/make-slides/references/render.js "$OUT_DIR"
```

The script:
1. Loads `OUT_DIR/slides.json` (validates; errors on schema violations with useful paths)
2. For each slide entry without a matching `NN-<id>.html` file, generates the HTML from `slide-template.html` + layout-specific markup. **Existing `NN-<id>.html` files are preserved** — user hand-edits win over spec.
3. Spins up a local file server on an OS-assigned ephemeral port (no conflict with other services)
4. For each HTML file: navigates, waits for fonts + network idle, measures `scrollHeight - offsetHeight` on `.slide`, screenshots to `OUT_DIR/slides/NN-<id>.png` at 2× DPR
5. Reports any slide with overflow and writes `.render-report.json`

### Step 4: Iterate on Overflow

If any slide reports overflow:
- **Vertical overflow:** content too tall → edit `slides.json` to reduce text, split into 2 slides, or shrink chart
- **Horizontal overflow:** content too wide → wrap text, use shorter labels
- For structural changes, edit `slides.json` and re-run render (old HTML files will be regenerated only if deleted — so delete the offending file and re-run)
- For quick visual tweaks, edit the generated `NN-<id>.html` directly — those edits persist (spec won't overwrite them)
- Iterate up to 5 rounds per slide

### Step 5: Visual Review

Show the user the PNG screenshots in order. For each, check:

- [ ] No overflow / clipping
- [ ] Text readable at presentation scale
- [ ] Visual hierarchy clear (title > key point > supporting)
- [ ] Accent color used intentionally, not everywhere
- [ ] Whitespace generous, not cramped
- [ ] Chart labels legible
- [ ] No spelling/grammar errors in headlines

Get user approval. Iterate on any flagged slides.

### Step 6: Generate Combined Viewer (Optional)

Create `OUT_DIR/index.html` that embeds all slides in a vertical scroll for fast review:

```html
<!DOCTYPE html>
<html><head><title>[Deck Title]</title>
<style>body { background: #1e1e1e; margin: 0; }
img { display: block; width: 100%; max-width: 1920px; margin: 24px auto; }</style>
</head><body>
<img src="slides/01-title.png">
<img src="slides/02-hook.png">
...
</body></html>
```

Useful for sharing the deck as a single URL or PDF-print preview.

### Step 7: Push to Google Slides (Dispatcher)

Skip entirely if `$GS_MODE` is empty (no `--google-slides` flag).

**Check for prior deck:** if `OUT_DIR/meta.json` exists and contains a `google_slides` block, warn the user:

```
⚠ This deck was previously pushed to Google Slides:
  Image:    https://docs.google.com/presentation/d/[prior-id]
  Editable: https://docs.google.com/presentation/d/[prior-id]

Pushing again will create NEW presentations (old URLs remain valid, but edits you
made in the browser there won't carry over). Continue? [y/N]
```

Read `.claude/skills/make-slides/references/push-to-google.md` for the full API reference.

**Dispatcher:**

```bash
case "$GS_MODE" in
  image)
    PRES_IMAGE=$(push_image_deck "$OUT_DIR")
    echo "Image deck: https://docs.google.com/presentation/d/$PRES_IMAGE"
    ;;
  editable)
    PRES_EDIT=$(push_editable_deck "$OUT_DIR")
    echo "Editable deck: https://docs.google.com/presentation/d/$PRES_EDIT"
    ;;
  mixed)
    PRES_MIX=$(push_mixed_deck "$OUT_DIR")
    echo "Mixed deck: https://docs.google.com/presentation/d/$PRES_MIX"
    ;;
  both)
    PRES_IMAGE=$(push_image_deck "$OUT_DIR")
    PRES_EDIT=$(push_editable_deck "$OUT_DIR")
    echo "Image deck:    https://docs.google.com/presentation/d/$PRES_IMAGE"
    echo "Editable deck: https://docs.google.com/presentation/d/$PRES_EDIT"
    ;;
esac
```

**Function implementations:** see `push-to-google.md`. Summary:

- `push_image_deck`: existing flow. Upload each PNG from `OUT_DIR/slides/` to Drive (public read), create presentation, `batchUpdate` inserts each PNG full-bleed on its own slide.
- `push_editable_deck`: new flow. Invoke `node build-native.js "$OUT_DIR" "$PRES_ID"`. Script reads `slides.json`, builds a `batchUpdate` with `createSlide` + `createShape TEXT_BOX` + `insertText` + `updateTextStyle` + `updateParagraphStyle` per element per slide (per `layout-map.md` positions). For `headline-chart` slides, the chart region is still inserted as an image (Slides API doesn't support native SVG/chart shapes matching our CSS).
- `push_mixed_deck`: new flow. Iterate `slides.json`; per slide, branch on `slide.render` — `"image"` → upload PNG + createImage; `"editable"` or `"auto"` → build native shapes. Combine all requests into ONE batchUpdate (one deck).
- `push_both` (implicit in the `both` case): runs `push_image_deck` then `push_editable_deck` sequentially. Two decks, two URLs.

**Fidelity warnings:** `build-native.js` emits warnings per slide when layout features don't translate (e.g., `underline-accent` gradient). Surface these to the user.

### Step 8: Save Deck Metadata

Write `OUT_DIR/meta.json`:

```json
{
  "deck_slug": "<slug>",
  "title": "<title>",
  "audience": "<audience>",
  "created": "YYYY-MM-DD",
  "slide_count": N,
  "source_content": "<one-line description>",
  "google_slides": {
    "mode": "<image|editable|mixed|both or null>",
    "image_url": "<url or null>",
    "image_presentation_id": "<id or null>",
    "editable_url": "<url or null>",
    "editable_presentation_id": "<id or null>",
    "mixed_url": "<url or null>",
    "mixed_presentation_id": "<id or null>"
  }
}
```

Fields that don't apply for the chosen mode stay null.

### Step 9: Cross-link

If the deck supports a specific project, append a one-line entry to that project's `idea.md` Progress Log:

```
- YYYY-MM-DD: Created deck `[deck-slug]` for [audience] (mode: [GS_MODE]). Path: `knowledge/decks/[deck-slug]/`.
```

If the deck supports a specific meeting (e.g., a customer QBR), link from the meeting note:

```
**Deck:** knowledge/decks/[deck-slug]/index.html
**Google Slides (image):** [url]
**Google Slides (editable):** [url]
```

### Step 10: Cleanup

The local file server shuts down automatically when `render.js` exits normally (`server.close()` in the finally path). No manual cleanup needed unless `render.js` was killed mid-run:

```bash
pkill -f "node.*render.js" 2>/dev/null
```

## Quality Standards

- Every deck must have a TL;DR slide (slide 2) for exec/QBR/investor audiences
- Every data slide must show the source/methodology in a small caption
- Every chart must have labels readable at presentation distance (≥24px)
- Total deck length: 8–15 slides for most use cases. >20 slides = restructure or split.
- Title slide includes audience + date so it's clear when re-discovered later
- Closing slide has a specific next step / ask / CTA — never end on "Thank you" alone

## Notes

- `slides.json` is the source of truth. HTML/PNG/Slides are all regeneratable from it.
- To preserve a version snapshot, copy `OUT_DIR/` to `OUT_DIR-vN/` before editing.
- Hand-edited HTML files (at `OUT_DIR/NN-<id>.html`) are preserved across re-runs — the spec won't overwrite them. Delete a file to regenerate it from spec.
- The Playwright install is one-time per workspace. For new personal-os users, `./setup.sh` offers to install it during onboarding; subsequent runs of this skill detect it via `node_modules/` at the repo root.
- If `gws` auth is expired, push steps fail with an auth error. User re-auths (`gws auth login` or equivalent) and re-runs.
- For editable mode, Open Sans replaces Inter — minor visual drift at 200pt+ (see `font-map.md`). Use `deck.font_override` in spec to pick a different Slides-native font.
- Editable mode can't reproduce CSS tricks (accent-underline gradients, custom bullets). Warnings are emitted per slide. Design-heavy slides should be `render: "image"` in mixed mode.
- `both` mode creates TWO presentations in the user's Drive. Each is independent — edits to one don't sync to the other.
