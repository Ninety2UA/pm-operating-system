# Layout → EMU Positioning Map

Per-layout positioning for native-mode Google Slides rendering (`build-native.js`). Each element is placed via `createShape` + `elementProperties` with explicit EMU positions.

## Page geometry

Google Slides default 16:9 page: **9,144,000 × 5,143,500 EMU** (10" × 5.625" at 914,400 EMU/inch).

Our HTML canvas is 1920 × 1080 px.

**Scale factor:** 9,144,000 ÷ 1920 = **4,762.5 EMU/px** (x-axis)
 5,143,500 ÷ 1080 = **4,762.5 EMU/px** (y-axis) — same both axes, aspect preserved.

**Outer margin:** 96px = **457,200 EMU = 0.5"** (clean Slides-native half-inch margin matches the typical Slides default).

**Content area inside margins:**
- Width: 9,144,000 − 2 × 457,200 = **8,229,600 EMU**
- Height: 5,143,500 − 2 × 457,200 = **4,229,100 EMU**

## Positioning conventions

- All positions below are the TOP-LEFT corner of each element in EMU
- All sizes (w, h) in EMU
- Alignment (`center` / `left`) applied via `updateParagraphStyle.alignment` = `"CENTER"` or `"START"`
- Font sizes in **PT** (not EMU): `{"magnitude": <N>, "unit": "PT"}`
- Font family: `"Open Sans"` unless `deck.font_override` is set
- Colors as hex via `updateTextStyle.foregroundColor.opaqueColor.rgbColor = {red, green, blue}` (each 0.0–1.0 float)

## Layout: `hero`

Centered statement + optional subtitle. Uses the ENTIRE content area centered.

| Element | x | y | w | h | Font | Size | Weight | Align | Color |
|---|---|---|---|---|---|---|---|---|---|
| hero | 457,200 | 1,714,500 | 8,229,600 | 1,714,500 | Open Sans | 110pt | 800 | center | primary |
| subtitle | 457,200 | 3,429,000 | 8,229,600 | 400,000 | Open Sans | 52pt | 600 | center | secondary |

Rationale:
- Hero starts at y = page_height / 3 ≈ 1,714,500 EMU to visually center a large statement in the upper-middle band
- Subtitle placed below the hero (y = 1,714,500 + 1,714,500 = 3,429,000) — directly butted, no gap, lets the typography ladder do the spacing visually

## Layout: `title-body`

Top-left title, bulleted body below, optional source footer.

| Element | x | y | w | h | Font | Size | Weight | Align | Color |
|---|---|---|---|---|---|---|---|---|---|
| title | 457,200 | 457,200 | 8,229,600 | 685,800 | Open Sans | 72pt | 700 | left | primary |
| body | 457,200 | 1,371,600 | 8,229,600 | 3,200,000 | Open Sans | 40pt | 400 | left | primary |
| source | 457,200 | 4,800,000 | 8,229,600 | 200,000 | Open Sans | 24pt | 400 | left | secondary |

Bullets via `createParagraphBullets` with preset `BULLET_DISC_CIRCLE_SQUARE` (closest native to our CSS accent-tick — accept fidelity drop). Paragraph spacing:
- `lineSpacing`: 140 (= 1.4×, matches CSS `line-height: 1.4`)
- `spaceBelow`: 24pt (matches CSS `gap: 24px`)

Title y = 457,200 (0.5" margin). Body y = 1,371,600 = 1.5" = title baseline + 1" gap. Source y = 4,800,000 leaves 0.5" bottom margin.

## Layout: `split`

Two columns 50/50 with 80px (381,000 EMU) gap. Each column has a subtitle + body stacked.

Column width = (8,229,600 − 381,000) / 2 = **3,924,300 EMU** (≈823px equivalent)

| Element | x | y | w | h | Font | Size | Weight | Align | Color |
|---|---|---|---|---|---|---|---|---|---|
| left subtitle | 457,200 | 1,371,600 | 3,924,300 | 400,000 | Open Sans | 52pt | 600 | left | secondary |
| left body | 457,200 | 1,848,000 | 3,924,300 | 2,800,000 | Open Sans | 40pt | 400 | left | primary |
| right subtitle | 4,762,500 | 1,371,600 | 3,924,300 | 400,000 | Open Sans | 52pt | 600 | left | secondary |
| right body | 4,762,500 | 1,848,000 | 3,924,300 | 2,800,000 | Open Sans | 40pt | 400 | left | primary |

Left column x = 457,200 (margin). Right column x = 457,200 + 3,924,300 + 381,000 = 4,762,500.

If `left.body` / `right.body` is an array of items, emit them as separate paragraphs with bullets; if a single string, emit as a single paragraph without bullets.

## Layout: `headline-chart`

Title up top, chart fills lower 2/3, source footer.

| Element | x | y | w | h | Font | Size | Weight | Align | Color |
|---|---|---|---|---|---|---|---|---|---|
| title | 457,200 | 457,200 | 8,229,600 | 685,800 | Open Sans | 72pt | 700 | left | primary |
| chart | 457,200 | 1,371,600 | 8,229,600 | 3,200,000 | — | — | — | — | — |
| source | 457,200 | 4,800,000 | 8,229,600 | 200,000 | Open Sans | 24pt | 400 | left | secondary |

**Chart region is ALWAYS an image** (even in editable mode). `chart_image_path` from spec is uploaded to Drive (public read) and inserted via `createImage` with the elementProperties above. The title + source remain native text boxes, so the user can still edit the finding headline in Slides.

## Layout: `big-number`

Hero number centered, caption below, source footer.

| Element | x | y | w | h | Font | Size | Weight | Align | Color |
|---|---|---|---|---|---|---|---|---|---|
| number | 457,200 | 1,500,000 | 8,229,600 | 1,500,000 | Open Sans | 200pt | 800 | center | accent |
| caption | 457,200 | 3,100,000 | 8,229,600 | 500,000 | Open Sans | 44pt | 500 | center | secondary |
| source | 457,200 | 4,800,000 | 8,229,600 | 200,000 | Open Sans | 24pt | 400 | center | secondary |

Note: caption weight 500 maps to Open Sans 600 per `font-map.md`.

## Color token resolution

Native mode resolves tokens to explicit RGB:

| Token | Dark theme | Light theme |
|---|---|---|
| primary | `#f8fafc` | `#0f172a` |
| secondary | `#94a3b8` | `#475569` |
| accent | from `deck.accent` (or per-slide override) | same |
| bg | `#0f172a` | `#ffffff` |

Hex → Slides RGB conversion: split into `rr`, `gg`, `bb` pairs, divide each by 255.0. E.g., `#3b82f6` → `{red: 0.231, green: 0.510, blue: 0.965}`.

## Bullet fidelity

CSS uses a custom accent-colored 24px × 4px dash as the bullet marker. Native Slides bullets are preset glyphs from `BulletGlyphPreset` enum:

| Preset | Appearance |
|---|---|
| `BULLET_DISC_CIRCLE_SQUARE` | • ∘ ▪ (by nesting level) |
| `BULLET_DIAMONDX_ARROW3D_SQUARE` | ◆ ➢ ▪ |
| `BULLET_CHECKBOX` | ☐ |
| `BULLET_ARROW_DIAMOND_DISC` | ➢ ◆ • |

**Default choice:** `BULLET_DISC_CIRCLE_SQUARE` — cleanest visual match for our CSS aesthetic. Document the fidelity drop (CSS accent dash → disc bullet) in skill output warnings.

## Unsupported CSS features in native mode

Emit a warning per slide that uses these, fall back as noted:

| CSS feature | Native fallback | Warning text |
|---|---|---|
| `.underline-accent` gradient | Solid accent color on the affected text run | `slide N: 'underline-accent' not supported in editable mode — using solid accent color` |
| Custom 24px accent-dash bullets | `BULLET_DISC_CIRCLE_SQUARE` | (silent — global fallback, not per-slide) |
| CSS `gap` between columns in split | Hardcoded 381,000 EMU gap | (silent — matches CSS default) |
| Drop shadows on text | Not supported in Slides API | `slide N: text drop-shadow not supported in editable mode — dropped` |
