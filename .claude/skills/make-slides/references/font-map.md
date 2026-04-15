# Font Mapping: Inter → Open Sans

HTML/PNG mode uses **Inter** (via Google Fonts, loaded in `slide-template.html`). Native Google Slides mode cannot use Inter — it's not in the Slides default font set. We map to **Open Sans** as the universal fallback.

## Why Open Sans

Three candidates evaluated:

| Font | Slides native? | Visual similarity to Inter | Weight coverage |
|---|---|---|---|
| **Open Sans** | ✅ Yes | High — same geometric sans, similar x-height, clean | 300, 400, 600, 700, 800 |
| Roboto | ✅ Yes | Medium — rounder, slightly narrower | 100, 300, 400, 500, 700, 900 |
| Lato | ✅ Yes | Lower — humanist touches, more character | 100, 300, 400, 700, 900 |
| Inter | ❌ No (requires user to add to their Slides font picker — inconsistent across Workspace tenants) | — | — |

**Open Sans wins** because it has the closest weight ladder to Inter (400/600/700/800 align exactly) and the cleanest geometric shapes. Roboto's narrower body text reads noticeably different at 40pt.

## Weight mapping table

| CSS Inter weight | Slides Open Sans weight | Notes |
|---|---|---|
| 400 | 400 | Regular — identical intent |
| 500 | 600 | Inter's medium rounds UP to Open Sans semi-bold to preserve emphasis. Rounding DOWN to 400 would erase the distinction. |
| 600 | 600 | Semi-bold — identical |
| 700 | 700 | Bold — identical |
| 800 | 800 | Extra-bold — identical |

Only Inter 500 requires a decision. We chose 600 to keep the subtle emphasis (e.g., "subtitle" text at weight 500 in CSS stays visually heavier than body at 400).

## API call shape

For each text run in `build-native.js`, emit an `updateTextStyle` request:

```json
{
  "updateTextStyle": {
    "objectId": "title_03",
    "textRange": { "type": "ALL" },
    "fields": "fontFamily,weightedFontFamily,fontSize,foregroundColor,bold",
    "style": {
      "fontFamily": "Open Sans",
      "weightedFontFamily": { "fontFamily": "Open Sans", "weight": 700 },
      "fontSize": { "magnitude": 72, "unit": "PT" },
      "foregroundColor": {
        "opaqueColor": { "rgbColor": { "red": 0.973, "green": 0.980, "blue": 0.984 } }
      },
      "bold": true
    }
  }
}
```

Notes:
- `weightedFontFamily.weight` is the numeric weight (400/500/600/700/800)
- `bold: true` is set when weight ≥ 700 (Slides uses this for synthetic-bold fallback if the font file doesn't contain that weight)
- `fontFamily` (plain string) AND `weightedFontFamily` should both be set — Slides uses them together
- Always include all three in the `fields` mask: `"fontFamily,weightedFontFamily,fontSize"` (omit → update is ignored)

## Size mapping

Font sizes are **PT** (points), not EMU. PT ≈ 0.75× CSS pixel at standard DPI, but we preserve CSS px values as PT directly — the downscaling to PT matches Slides conventions well enough in practice.

| CSS px (HTML) | Slides pt (native) |
|---|---|
| 24 | 24pt |
| 28 | 28pt |
| 36 | 36pt |
| 40 | 40pt |
| 44 | 44pt |
| 52 | 52pt |
| 56 | 56pt |
| 64 | 64pt |
| 72 | 72pt |
| 80 | 80pt |
| 96 | 96pt |
| 110 | 110pt |
| 200 | 200pt |

Slight visual difference: Slides may render slightly larger than the HTML preview at the same numeric value. If the user reports this, offer `font_size_scale` in `deck` (future enhancement — not v1).

## Override mechanism

User can set `deck.font_override` in `slides.json`:

```json
{
  "deck": {
    "font_override": "Roboto"
  }
}
```

Valid values: any Google Slides built-in font name (`"Roboto"`, `"Lato"`, `"Montserrat"`, `"Raleway"`, `"Playfair Display"`, `"Source Sans Pro"`, etc.).

Invalid values: the Slides API accepts arbitrary strings; if the font isn't available to the viewer, Slides substitutes at render time. `build-native.js` does NOT validate — if user mis-spells, Slides falls back (typically to Arial).

## Fidelity drift to expect

At 40pt (body text):
- Line width: Open Sans ~2% wider than Inter for typical English text
- Letter shapes: Open Sans has rounder terminals (e.g., `a`, `e`, `o`) — looks softer
- X-height: near-identical, readability preserved

At 72–110pt (titles):
- Visually very close, differences hard to spot without side-by-side
- Open Sans slightly more conventional looking; Inter has tighter letter-spacing

At 200pt (big-number):
- Most visible — Open Sans `287%` looks ~3% wider than Inter `287%`
- Letter shape differences become visible (curves vs more rectangular)
- Consider `font_override: "Montserrat"` for heavier visual weight if this bothers you

## Why we don't just add Inter to Slides

Possible but fragile:
1. User would need to add Inter to their Google account's Slides font picker manually
2. Only visible to viewers who also have Inter available
3. If the deck is shared with someone who hasn't added Inter, Slides falls back silently (often to Arial — jarring)

Open Sans is universally present. Trade one font drift (Inter → Open Sans) for zero viewer-side surprises.
