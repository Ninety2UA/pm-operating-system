# Slide Design Rules

Opinionated rules. Follow unless the user overrides explicitly.

## Layout Principles

- **One idea per slide.** If you're cramming, split it. The audience should grasp the slide in 5 seconds.
- **Visual hierarchy matters more than decoration.** Title > key point > supporting detail. Use size, weight, and color to enforce hierarchy — not boxes and lines.
- **Generous whitespace.** Slides project large. Breathing room is a feature, not wasted space. Minimum 80px padding on outer edges.
- **Left-align text by default.** Center alignment only for: single-line titles, hero statements, or full-bleed quotes.
- **Grid your content.** Imagine a 12-column grid. Body text in cols 1–8, supporting visual in 9–12. Or 50/50 split. Avoid floating elements.

## Typography

Use `'Inter'`, `'Outfit'`, or `system-ui, sans-serif` with weights 400/500/600/700/800.

| Element | Size | Weight |
|---|---|---|
| Hero title (slide 1) | 96–120px | 800 |
| Slide title | 64–80px | 700 |
| Subtitle / key point | 44–56px | 600 |
| Body text | 36–44px | 400–500 |
| List item | 36–40px | 400 |
| Caption / source | 24–28px | 400 |
| **Minimum, ever** | **24px** | — |

If body text wants to drop below 24px, the slide has too much content. Cut words, don't shrink type.

## Color

### Dark theme (default)
- Background: `#0f172a` (slate-900)
- Primary text: `#f8fafc` (slate-50)
- Secondary text: `#94a3b8` (slate-400)
- Accent: pick ONE — `#3b82f6` (blue), `#10b981` (emerald), `#f59e0b` (amber), `#ef4444` (red), or `#a855f7` (purple)

### Light theme (alt)
- Background: `#ffffff`
- Primary text: `#0f172a` (slate-900)
- Secondary text: `#475569` (slate-600)
- Accent: same picks as dark theme

### Accent usage
- ≤30% of slide surface area
- Use for: headlines, key numbers, single underline, highlight box behind one keyword
- NEVER use accent for body text — that's what hierarchy is for
- NEVER use multiple accent colors in one deck — pick ONE and commit

### Contrast
Always test contrast at presentation scale. Squint at the slide. If any text becomes hard to read, increase contrast or remove the text.

## Numbers & Data

When the slide is about a number, the number is the slide:

```
        287%
        ────
   YoY pipeline growth
       Q1 2026
```

- Hero number: 200–300px, weight 800, accent color
- Caption underneath: 36–44px, secondary text color
- Source/method: 24–28px, bottom of slide

For comparison numbers (before/after, you/competitor), use side-by-side at 120–180px each.

## Charts

- 3–4 data points max per chart
- Labels ≥24px (use larger if there's room)
- Title above chart describes the FINDING, not the data: "Conversion dropped 18% after Friday push" — not "Daily conversion rate"
- Source caption: dataset, date range, sample size
- One color for primary series, gray for comparison/baseline
- No 3D charts. Ever.
- No pie charts with >4 slices — use a bar chart instead
- Y-axis: start at zero unless the change you're showing is genuinely small relative to the values
- Annotations on the chart > legend below it (when possible)

## Layouts

Pick ONE per slide:

- **Hero statement** — single sentence, centered, large type, lots of space
- **Title + 3 bullets** — title top-left, 3 bullets stacked below (max 3, each ≤2 lines)
- **Title + body + visual** — title top, body 50%, visual 50% (split horizontally or vertically)
- **Headline + chart** — finding-as-headline up top, chart fills lower 2/3
- **Big number** — hero number centered, caption beneath, source bottom
- **Quote** — full-bleed quote in italic, attribution beneath, source caption bottom
- **Comparison** — split slide (50/50 or 33/66), heading on each side
- **List** — numbered list, max 5 items, each ≤2 lines

## What NOT to Do

- ❌ Bullet walls (>3 bullets = restructure)
- ❌ Clip art or stock photos as decoration
- ❌ Multiple accent colors
- ❌ Drop shadows on text (use weight/contrast for emphasis)
- ❌ Logos on every slide (title + closing only)
- ❌ Page numbers (audience doesn't need them)
- ❌ "Agenda" slide for decks <10 slides
- ❌ "Thank you" as the closing slide (always have a next step / ask)
- ❌ Animation / transitions (this is static HTML)
- ❌ Background images behind text (kills readability)
- ❌ All-caps body text (titles only, sparingly)
- ❌ Italics for emphasis (use weight or color instead)

## PM / Data Analyst Specifics

When the user is a PM building exec/QBR/investor decks:

- **BLUF (Bottom Line Up Front)** — slide 2 always carries the recommendation/answer/ask in 3 bullets
- **Lead with the finding, not the data** — chart titles state the conclusion
- **Always include comparison context for KPIs** — "287% YoY" not "287%"; "$45 CPI vs. industry $52" not "$45 CPI"
- **Source every data slide** — dataset, date range, sample size in 24–28px caption
- **Decision asks belong on their own slide** — don't bury "we need to hire 2 PMs" inside a bullet
- **End with explicit next steps** — what happens after this meeting, owned by whom, by when

## App Marketing Specifics

When building decks about app campaigns / marketing data:

- Show **benchmarks** alongside metrics (industry CPI, retention, ROAS) — context > raw numbers
- Use **funnel diagrams** for acquisition flow (impressions → installs → activated → retained)
- For creative analytics: thumbnail of the creative + key metric side-by-side
- For platform comparisons: small platform icons (Meta, Google, TikTok, Apple Search Ads) + metrics side-by-side
- Always disclose which attribution window / model

## Accessibility & Sanity Checks

Before declaring a slide done:

- [ ] Squint test: can you read the headline at 30% zoom?
- [ ] Color test: would this work for a colorblind viewer? (test with grayscale screenshot)
- [ ] Print test: would this make sense if printed in B&W?
- [ ] Cold-open test: would someone joining mid-deck understand this slide alone?
