# Ecosystem currency report — template

File: `knowledge/currency/reports/repo/YYYY-MM-DD.md` (final name from the
start; completion trailer is the LAST line — a trailerless file is a
crashed run and is never surfaced). Writing rules as in the mining ledger:
authored prose is yours; every verbatim upstream string defanged
(backticks, `http`→`hxxp`, control chars dropped); respectful,
fit-to-this-repo rationales written as if the maintainer will read them.

```markdown
# Ecosystem currency report — YYYY-MM-DD

- Mode: report-only | full
- Registry: <n> watched (<n> seed, <n> adopter-added) | validation: ok | errors
- Lock: acquired | reclaimed (<notice>) — released: deleted | marker
- REST budget used: <n>/6 | Fetches: <n>/25 | Fallbacks used: <which>

## Per-repo deltas

### owner/name — unchanged
Pin: `<head sha7>` (<date>) == cursor.

### owner/name — <k> commits since `<cursor7>`
<one-line delta summary; note truncation if compare hit 250/300 caps>

| ID | Pattern | Verdict | Rationale (authored) | Provenance (defanged) | Reversibility | Sensitive |
|---|---|---|---|---|---|---|
| RW-YYYY-MM-DD-1 | <candidate> | adopt / adapt / skip | <one line> | `<sha7>` `<path>` — `"<defanged quote ≤150>"` | <one line> | yes/no |

<zero-import outcome → "No candidates; cursor pin advanced on next full run.">

## Decision lines (owner marks; full mode consumes)

- [ ] adopt RW-YYYY-MM-DD-1 — <candidate>   <!-- sensitive: heightened review -->

## Anomalies and throttles

<force-push flags, rate-limit fallbacks, per-repo throttle state — or "none">

## Gaps (what this run could not see)

- <compare truncation, unreachable files, skipped oversize docs — or "none">

<!-- report-complete: <UTC ISO timestamp> -->
```

Completeness checklist:
- [ ] every watched repo appears exactly once (unchanged pins included)
- [ ] every adopt/adapt candidate has a decision line; sensitive flagged
- [ ] anomalies + gaps sections present ("none" is a claim)
- [ ] no undefanged upstream string anywhere
- [ ] trailer is the final line
