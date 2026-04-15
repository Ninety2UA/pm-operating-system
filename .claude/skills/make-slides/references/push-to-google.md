# Push to Google Slides — Four Modes

Workflow reference for pushing a rendered deck to Google Slides via the `gws` CLI. Called from `SKILL.md` Step 7 in one of four dispatcher branches.

## Contract

**HTML and `slides.json` are the source of truth.** Google Slides is a delivery format. Re-running `/make-slides` regenerates Slides presentations from scratch — it does NOT update prior presentations. Edits made in the Google Slides browser UI don't sync back. Users should treat pushed decks as "last delivered snapshot."

## Prerequisites

- `gws` authenticated (`gws auth login` or equivalent if expired)
- `OUT_DIR/slides.json` exists and validates
- `OUT_DIR/slides/NN-<id>.png` files exist (from `render.js`) — needed for image/mixed/both
- For editable/mixed/both: `build-native.js` at `.claude/skills/make-slides/references/build-native.js`

## Mode: `image`

Pixel-perfect, not editable. One deck, every slide a full-bleed PNG.

### Steps

**1. Create the presentation:**

```bash
TITLE=$(jq -r '.deck.title' "$OUT_DIR/slides.json")
PRES_RESPONSE=$(gws slides presentations create --json "$(jq -n --arg t "$TITLE" '{title: $t}')")
PRES_ID=$(echo "$PRES_RESPONSE" | jq -r '.presentationId')
echo "Created image deck: https://docs.google.com/presentation/d/$PRES_ID"
```

**2. Get the default slide objectId** (so we can overwrite slide 1 rather than leaving it blank):

```bash
DEFAULT_SLIDE_ID=$(gws slides presentations get \
  --params "$(jq -n --arg id "$PRES_ID" '{presentationId: $id}')" \
  | jq -r '.slides[0].objectId')
```

**3. Build the request array.** For each slide `NN-<id>.png` in `OUT_DIR/slides/`:

- Upload to Drive with public-read permission:

```bash
UPLOAD=$(gws drive files create \
  --json "$(jq -n --arg n "slide-NN-<id>.png" '{name: $n, mimeType: "image/png"}')" \
  --upload "$OUT_DIR/slides/NN-<id>.png" \
  --upload-content-type "image/png")
FILE_ID=$(echo "$UPLOAD" | jq -r '.id')

gws drive permissions create \
  --params "$(jq -n --arg id "$FILE_ID" '{fileId: $id}')" \
  --json '{"role":"reader","type":"anyone"}'

PNG_URL="https://drive.google.com/uc?export=view&id=$FILE_ID"
```

- Append to request array:
  - If slide 0: `createImage` onto `DEFAULT_SLIDE_ID` (no createSlide needed)
  - Otherwise: `createSlide` with a fresh objectId, then `createImage` onto it

Image is full-bleed: `size = {width: 9144000 EMU, height: 5143500 EMU}`, `transform = {scaleX: 1, scaleY: 1, translateX: 0, translateY: 0}`.

**4. Send the batchUpdate** (argv-based, no shell injection):

```bash
REQUESTS_JSON=$(cat <<'JSON'
{
  "requests": [
    { "createImage": { ... } },
    { "createSlide": { ... } },
    { "createImage": { ... } },
    ...
  ]
}
JSON
)
gws slides presentations batchUpdate \
  --params "$(jq -n --arg id "$PRES_ID" '{presentationId: $id}')" \
  --json "$REQUESTS_JSON"
```

**5. Print the URL and save file IDs** (for optional cleanup later):

```bash
echo "https://docs.google.com/presentation/d/$PRES_ID"
# Save uploaded file IDs to OUT_DIR/.uploaded-drive-files.json for cleanup
```

### When implementing in Claude's skill execution

Rather than constructing the JSON by string manipulation, use `build-image-batch.js` (future enhancement) or build it incrementally in Node. For now, the skill can read `slides.json`, iterate, upload each PNG, accumulate requests, and issue one batchUpdate. Shell script is provided above as a reference — actual execution can use whichever mechanism is cleanest.

## Mode: `editable`

Native text boxes, editable in browser. One deck, no PNG uploads except chart regions (headline-chart layout only).

### Steps

**1. Create the presentation** (same as image mode).

**2. Invoke build-native.js:**

```bash
PRES_ID=$(gws slides presentations create \
  --json "$(jq -n --arg t "$TITLE" '{title: $t}')" \
  | jq -r '.presentationId')

node .claude/skills/make-slides/references/build-native.js "$OUT_DIR" "$PRES_ID" --mode=editable
```

`build-native.js` handles everything: reads `slides.json`, fetches the default slide objectId, uploads chart images for headline-chart slides, builds the full `batchUpdate` request array (createShape TEXT_BOX + insertText + updateTextStyle + updateParagraphStyle + createParagraphBullets per element), and invokes `gws slides presentations batchUpdate`.

Stdout: the presentation ID on success. Stderr: progress + fidelity warnings.

**3. Print URL and surface warnings:**

```bash
echo "https://docs.google.com/presentation/d/$PRES_ID"
```

If `build-native.js` emitted fidelity warnings (e.g., `underline-accent` not supported), surface them to the user verbatim so they know the editable deck has drift.

### Fidelity notes (surface to user)

- Inter → Open Sans (`font-map.md` for mapping)
- CSS accent-underline → solid accent color
- Custom bullets → Slides preset `BULLET_DISC_CIRCLE_SQUARE`
- Drop shadows, gradients → dropped
- Chart regions in `headline-chart` layout → always image (Slides API can't render SVG/native charts matching our design)

## Mode: `mixed`

One deck, per-slide choice between full image and editable text boxes based on `slide.render` field.

### Steps

**1. Create the presentation** (same as image mode).

**2. Invoke build-native.js with `--mode=mixed`:**

```bash
node .claude/skills/make-slides/references/build-native.js "$OUT_DIR" "$PRES_ID" --mode=mixed
```

Internal behavior:
- For each slide in `slides.json`:
  - If `slide.render === "image"` → upload `OUT_DIR/slides/NN-<id>.png`, insert full-bleed image on the slide
  - Else (`"auto"`, `"editable"`, or unset) → build native text boxes
- All requests combined into ONE batchUpdate → ONE presentation

**3. Print URL and surface warnings** (same as editable mode).

### When to use mixed

- Chart slides that benefit from pixel-perfect rendering: set `render: "image"` in `slides.json` for those
- Text-heavy slides that stakeholders should edit: leave `render: "auto"` or unset
- Result: one URL to share, chart fidelity preserved, text editability preserved

## Mode: `both`

Two separate decks from one run. This is the **default** when `--google-slides` is bare.

### Steps

Run **image mode**, then **editable mode**, sequentially. Two separate presentation IDs, two URLs returned.

```bash
# First: image deck
PRES_IMAGE=$(push_image_deck "$OUT_DIR")
echo "Image deck:    https://docs.google.com/presentation/d/$PRES_IMAGE"

# Second: editable deck
TITLE_EDIT=$(jq -r '"\(.deck.title) (editable)"' "$OUT_DIR/slides.json")
PRES_EDIT=$(gws slides presentations create \
  --json "$(jq -n --arg t "$TITLE_EDIT" '{title: $t}')" \
  | jq -r '.presentationId')
node .claude/skills/make-slides/references/build-native.js "$OUT_DIR" "$PRES_EDIT" --mode=editable
echo "Editable deck: https://docs.google.com/presentation/d/$PRES_EDIT"
```

Note the `(editable)` suffix on the editable deck title — helps distinguish the two in Drive.

### Save both to meta.json

```json
{
  ...
  "google_slides": {
    "mode": "both",
    "image_url": "https://docs.google.com/presentation/d/...",
    "image_presentation_id": "...",
    "editable_url": "https://docs.google.com/presentation/d/...",
    "editable_presentation_id": "..."
  }
}
```

## Cleanup Uploaded PNGs (optional, all modes)

After batchUpdate succeeds, Slides has cached the images and no longer needs the Drive originals. For sensitive decks:

```bash
# Read the uploaded file IDs from build-native.js output (and image-mode equivalent)
if [ -f "$OUT_DIR/.uploaded-drive-files.json" ]; then
  for FILE_ID in $(jq -r '.uploaded[]' "$OUT_DIR/.uploaded-drive-files.json"); do
    gws drive files delete --params "$(jq -n --arg id "$FILE_ID" '{fileId: $id}')"
  done
fi
```

**Test before adopting as default:** some Slides deployments may re-fetch the URL on display; if images disappear after deletion, keep the Drive originals.

## Re-run Guard

Before Step 7, check `OUT_DIR/meta.json` for a prior `google_slides` block:

```bash
if [ -f "$OUT_DIR/meta.json" ] && jq -e '.google_slides.image_presentation_id // .google_slides.editable_presentation_id' "$OUT_DIR/meta.json" > /dev/null; then
  echo "⚠ This deck was previously pushed. Re-running creates NEW presentations."
  echo "   Prior image URL:    $(jq -r '.google_slides.image_url // "none"' "$OUT_DIR/meta.json")"
  echo "   Prior editable URL: $(jq -r '.google_slides.editable_url // "none"' "$OUT_DIR/meta.json")"
  echo "   Edits made in the Slides browser UI at those URLs will NOT carry forward."
  # Prompt the user before proceeding (via AskUserQuestion in the skill)
fi
```

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `invalid_grant: reauth related error` | gws auth expired | User runs their gws auth flow, re-runs skill |
| `createImage` returns broken image | Drive file not public-readable | Check `gws drive permissions create` ran successfully; retry with `role=reader,type=anyone` |
| `createShape` returns `Invalid value at shape_type` | gws schema rejected `TEXT_BOX` | Verify in smoke test (task #1); may need different casing or enum value |
| `updateTextStyle` returns `Requested entity not found` | `createShape` in same batchUpdate failed silently upstream | Check request order — shape must be created BEFORE styling |
| batchUpdate response: `This operation is not supported for this document` | Trying to update a read-only template | Don't modify the default presentation shipped by Slides; always create fresh via `presentations create` |
| Presentation has overlapping text boxes | EMU position math wrong in layout-map.md | Double-check: CONTENT_W = PAGE_W − 2×MARGIN = 8229600; right col x = MARGIN + colW + gap |
| Italicized / wrong weight | `fields` mask missing `weightedFontFamily` or `bold` | Verify `fields` string includes all modified properties |
| `jq: parse error: Invalid string` or `JSON.parse` fails on gws output | gws emits literal unescaped newlines inside string values (notably `textRun.content`) when the response includes slide/layout text | Narrow the response via `fields` parameter — e.g. `--params '{"presentationId":"…","fields":"slides(objectId)"}'` — to exclude text content. Alternatively, extract fields via grep/sed instead of a JSON parser. |

## Reference: EMU quick math

- 1 inch = 914400 EMU
- Page = 9,144,000 × 5,143,500 EMU (10" × 5.625", 16:9)
- 1 CSS px (at our 1920×1080 scale) = 4762.5 EMU
- 96px (0.5" margin) = 457200 EMU

Full per-layout map: `layout-map.md`.

## Reference: font styling via API

See `font-map.md` for the complete Inter → Open Sans mapping. Key `updateTextStyle` shape:

```json
{
  "updateTextStyle": {
    "objectId": "title_01",
    "textRange": { "type": "ALL" },
    "fields": "fontFamily,weightedFontFamily,fontSize,foregroundColor,bold,italic",
    "style": {
      "fontFamily": "Open Sans",
      "weightedFontFamily": { "fontFamily": "Open Sans", "weight": 700 },
      "fontSize": { "magnitude": 72, "unit": "PT" },
      "foregroundColor": {
        "opaqueColor": { "rgbColor": { "red": 0.973, "green": 0.980, "blue": 0.984 } }
      },
      "bold": true,
      "italic": false
    }
  }
}
```
