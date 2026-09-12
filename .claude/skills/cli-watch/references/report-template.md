# Platform currency report — template

File: `knowledge/currency/reports/cli/YYYY-MM-DD.md` (final name from the
start; the completion trailer is the LAST line written, so a crashed run
is detectable by its absence — never read a trailerless report as current).

Writing rules: authored prose is yours; every verbatim upstream string is
defanged (backtick-wrapped, `http`→`hxxp`, control characters dropped —
the `core/scripts/defang.py` neutralization). Links you author must be
built from actual data. No conversational filler.

```markdown
# Platform currency report — YYYY-MM-DD

- Mode: report-only | full
- Baseline: <cursor version read> (schema v1) | rescan: <reason> | throttled
- Lock: acquired | reclaimed (<notice>) — released: deleted | marker
- Fetches: <n>/15 | Skipped oversize: <n>
- Model roster: unchanged | new ID(s) classified this run

## Delta since <cursor>

<one line per new version/doc change; nothing new → "No changes since
<cursor>." and skip to Gaps>

## Classified candidates

| ID | Item | Verdict | Rationale (authored) | Provenance (defanged) | Sensitive |
|---|---|---|---|---|---|
| CLI-YYYY-MM-DD-1 | <item> | adopt-candidate / document / not-applicable | <one line> | `vX.Y.Z` — `"<defanged quote ≤150 chars>"` | yes/no |

## Decision lines (owner marks; full mode consumes)

- [ ] adopt CLI-YYYY-MM-DD-1 — <item>   <!-- sensitive lines: heightened
  review required; cannot be adopted from this summary -->

## Egress receipts (self-attested)

| # | defanged URL | purpose | outcome | approx. size |
|---|---|---|---|---|
| 1 | `hxxps://<host>/<path>` | <why fetched> | <200 OK / non-200 / error> | <approx KB> |

<one row per fetch this run made, in fetch order; no fetches → "No
fetches this run." Self-attested: this table is written by the same run
that fetched — the only independent trace is
`knowledge/currency/guard.log`; any reconciliation mismatch, or its
absence, is recorded in Gaps below, not here.>

## Gaps (what this run could not see)

- <e.g. "release dates absent from CHANGELOG; taken from GitHub releases">
- <e.g. "doc anchor X unreachable this run (HTTP nnn)">

## Recovery notices

<anomalies, throttle state, reclaims — or "none">

<!-- report-complete: <UTC ISO timestamp> -->
```

Completeness checklist (a report is complete when):
- [ ] every delta item appears exactly once in Classified candidates
- [ ] every adopt-candidate has a decision line
- [ ] every sensitive row is flagged on its decision line
- [ ] Gaps section present (empty is a claim, not an omission — write "none")
- [ ] Model roster line states `unchanged` or names what the run classified
- [ ] trailer is the final line
