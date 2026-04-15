# `slides.json` Schema

The content spec that drives both renderers (`render.js` → HTML/PNG, `build-native.js` → native Google Slides text boxes).

## File location

`<OUT_DIR>/slides.json` — sibling of the `NN-<id>.html` slide files and the `slides/` PNG directory.

## Top-level shape

```json
{
  "deck": { ... deck-level metadata ... },
  "slides": [ ... one entry per slide, in order ... ]
}
```

## `deck` object

| Field | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `title` | string | yes | — | Deck title. Used for Google Slides presentation name and the `<title>` in HTML pages. |
| `audience` | string | no | `""` | Who the deck is for. Used in title-slide subtitle scaffolding and meta.json. |
| `date` | string (ISO YYYY-MM-DD) | yes | today | Deck creation date. Appears in title subtitle. |
| `theme` | string | no | `"dark"` | `"dark"` or `"light"`. Drives CSS variable defaults. |
| `accent` | string (hex) | no | `"#3b82f6"` | Single accent color. ≤30% of slide area per design-rules.md. |
| `font_override` | string or null | no | `null` | Override the Open Sans fallback in editable mode (e.g., `"Roboto"`, `"Lato"`). Must be a Google Slides built-in font. Null = use Open Sans. |

## `slides[]` entries

Each slide is an object:

| Field | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `id` | string (kebab-case) | yes | — | Unique slide ID — the content slug ONLY. Do NOT prepend the order number. Forms filename: `NN-<id>.html` where `NN` is the zero-padded array position (1-based). Must match `^[a-z0-9-]+$`. Good: `tldr`, `pipeline-growth`, `asks`. Bad: `01-tldr` (the `01-` is added automatically). |
| `layout` | enum | yes | — | One of `hero`, `title-body`, `split`, `headline-chart`, `big-number`. |
| `render` | enum | no | `"auto"` | `"auto"`, `"image"`, or `"editable"`. Only consulted in `--google-slides=mixed` mode; ignored otherwise. `"auto"` in mixed mode defaults to `"editable"` unless the layout can't be native (headline-chart always falls back to `"image"` for the chart region). |
| `accent` | string (hex) or null | no | `null` (inherit) | Per-slide accent override. Null = use `deck.accent`. |
| `content` | object | yes | — | Layout-specific content fields (see below). |
| `notes` | string | no | `""` | Speaker notes. Written to Google Slides speaker-note field in editable mode. Ignored in image mode. |

## Layout-specific `content` fields

### `hero`

```json
{ "hero": "Headline statement", "subtitle": "Optional second line" }
```

| Field | Required | Notes |
|---|---|---|
| `hero` | yes | The main statement. Max ~60 chars for good typography at 110pt. |
| `subtitle` | no | Secondary line. Max ~80 chars. |

### `title-body`

```json
{
  "title": "Slide title",
  "body": ["Bullet 1", "Bullet 2", "Bullet 3"],
  "source": "Optional data source / attribution footer"
}
```

| Field | Required | Notes |
|---|---|---|
| `title` | yes | Max ~90 chars for 72pt to fit one line. Two-line titles OK. |
| `body` | yes | Array of 1-3 bullet strings. ≤3 enforced by design-rules.md. Each ≤2 lines. |
| `source` | no | Dataset / methodology caption. Small text at bottom. |

### `split`

```json
{
  "left":  { "subtitle": "Before", "body": "Text for left column" },
  "right": { "subtitle": "After",  "body": "Text for right column" }
}
```

| Field | Required | Notes |
|---|---|---|
| `left.subtitle` | yes | Column label. |
| `left.body` | yes | Column content. String OR array of up to 3 items. |
| `right.subtitle` | yes | Column label. |
| `right.body` | yes | Column content. |

### `headline-chart`

```json
{
  "title": "Finding-as-headline",
  "chart_image_path": "charts/conversion.png",
  "source": "GA4, Mar 1-28, n=12,481"
}
```

| Field | Required | Notes |
|---|---|---|
| `title` | yes | State the FINDING, not the dataset (per design-rules.md). |
| `chart_image_path` | yes | Relative path from `OUT_DIR` to a PNG/SVG chart. For editable mode, chart is still embedded as image (Slides API doesn't support native SVG). |
| `source` | yes | Required for data slides. Dataset + date range + sample size. |

### `big-number`

```json
{
  "number": "287%",
  "caption": "YoY pipeline growth",
  "source": "Internal CRM, Q1 2026 vs. Q1 2025"
}
```

| Field | Required | Notes |
|---|---|---|
| `number` | yes | Short — fits in one rendered line at 200pt. Max ~5 chars for best visual. |
| `caption` | yes | One-line context. |
| `source` | yes | Attribution. |

## Validation rules

Enforced by both renderers on load:

- `deck.title`, `deck.date` required
- Each `slide.id` unique within the deck
- `slide.id` matches `^[a-z0-9-]+$`
- `slide.layout` in the allowed enum
- `slide.content` has all required fields for its layout (error with path, e.g., `slides[2].content.title required`)
- `slide.render` in `{"auto", "image", "editable"}` if present
- Warn (don't error) on unknown keys — forward-compatible for future fields

## Example: complete 5-slide deck

```json
{
  "deck": {
    "title": "Q1 2026 Portfolio Review",
    "audience": "Exec Team",
    "date": "2026-04-14",
    "theme": "dark",
    "accent": "#3b82f6",
    "font_override": null
  },
  "slides": [
    {
      "id": "title",
      "layout": "hero",
      "content": {
        "hero": "Q1 2026 Portfolio Review",
        "subtitle": "Exec Team · April 14, 2026"
      }
    },
    {
      "id": "tldr",
      "layout": "title-body",
      "content": {
        "title": "The three things",
        "body": [
          "Pipeline up 287% YoY — on track for Q2 hiring",
          "CPI $45 vs. $52 industry benchmark",
          "Need 2 PM hires by June to unblock roadmap"
        ]
      },
      "notes": "Lead with the pipeline number. If they push on CPI, show slide 4."
    },
    {
      "id": "pipeline-growth",
      "layout": "big-number",
      "content": {
        "number": "287%",
        "caption": "YoY pipeline growth",
        "source": "Internal CRM, Q1 2026 vs. Q1 2025"
      }
    },
    {
      "id": "conversion-drop",
      "layout": "headline-chart",
      "render": "image",
      "content": {
        "title": "Conversion dropped 18% after Friday push",
        "chart_image_path": "charts/conversion.png",
        "source": "GA4, Mar 1-28, n=12,481"
      }
    },
    {
      "id": "asks",
      "layout": "title-body",
      "content": {
        "title": "What we need from you",
        "body": [
          "Approve 2 PM headcount by April 28",
          "Intro to Acme CRO for renewal expansion",
          "Reallocate $50k from Q3 paid search to organic"
        ],
        "source": "Follow-up owner: Alex · ETA: April 18"
      }
    }
  ]
}
```

## Notes on forward compatibility

- New layouts added later need a schema entry here and positioning in `layout-map.md`
- New `deck` fields → add with sensible default, update validator to warn-on-unknown only for `slides[]` entries
- `render: "auto"` is the escape hatch — future renderers can pick per-slide without changing the spec shape
