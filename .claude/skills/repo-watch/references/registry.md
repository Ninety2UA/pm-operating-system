# Live registry schema — knowledge/currency/repo-registry.json

Hand-editable JSON, validated at every run start
(`currency.validate_registry`); malformed → named errors, never a crash.
Gitignored: adopter-added repo names never enter git history.

```json
{
  "schema_version": 1,
  "repos": {
    "owner/name": {
      "cursor_sha": "<40-char sha — last fully-processed upstream commit>",
      "cursor_date": "YYYY-MM-DD",
      "watch": true,
      "retired_at_sha": "<sha at retire time — tombstone; only when watch is false>",
      "notes": "free text; file pointers only into knowledge/currency/"
    }
  }
}
```

Rules:

- `schema_version` must be `1`.
- Slugs are `owner/name` (GitHub form).
- `cursor_sha` / `retired_at_sha`: full 40-char lowercase SHAs.
- `watch: false` + `retired_at_sha` = retired with tombstone; re-adding
  resumes from the tombstone even if the entry's cursor was deleted.
- Repos present in the seed but absent here are watched from their
  resolved-HEAD first-run cursor (seed SHA as provenance fallback).
- Precedence on disagreement: **ledger > seed > this file** — this file is
  rebuildable state, reconciled against the ledger, never the reverse.
