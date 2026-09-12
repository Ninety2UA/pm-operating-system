# TDD guide — §19 Testing Strategy & Test List (test-first)

How to draft §19: a flat **Test List** authored before any implementation, plus a secondary tooling-lane table. Format follows the §19 shapes in `references/spec-template.md`. The Test List feeds `references/wbs-guide.md` (§20) — every test row becomes a task ordered before its impl. Method is **Canon TDD** (Kent Beck): https://tidyfirst.substack.com/p/canon-tdd.

## Write the test list FIRST
Before choosing implementation modules, derive **one test per P0 acceptance criterion** from `prd.md §5.4` + `user-stories.md`. The list is the executable form of the requirements — you write it, then build to it. If a P0 FR has no pre-named failing test, the design isn't ready.

## Row format (one test per row)
`test-id | SPEC:FR-id | file | given / when / then | fails when | drives impl`

```markdown
| test-id | SPEC:FR | file | given / when / then | fails when | drives impl |
|---------|---------|------|---------------------|------------|-------------|
| T004 | FR-2 | `tests/detect/zscore.test.ts` | given a series w/ one outlier · when detect('zscore') · then 1 Anomaly sev=high | 0 anomalies returned, or severity != high | `src/detect/zscore.ts` |
| T006 | FR-1 | `tests/parse/csv.test.ts` | given a headered CSV · when parse() · then column map inferred | non-zero exit, or the column map is empty | `src/parse/csv.ts` |
```

`SPEC:FR` ties the test back to the §2.1 traceability table. The `drives impl` column is the exact §6 file the paired §20 task implements. `test-id` is the same stable T-ID §20 uses.

## State the failing direction
Every automated row fills `fails when` with an **observable** signal — an exit code, a string that appears in the output, a line that goes missing. (RW-2026-09-12-16) The authoring test is one question: if this command were silently doing nothing, what in its output would tell me? If there is no answer, the command is the problem — fix it rather than invent a signal, because a check that exits 0 on a no-op passes green and silently. Short is complete: `non-zero exit` is a whole answer.

Rejected values: the whole-value placeholders `TBD`, `TODO`, `N/A`, `none`, `unknown`, `?`, `-` in any case, and restatements that carry no information ("the command fails", "the test errors", "it does not pass"). A Manual-lane row carries `manual` instead of a signal and is exempt — that escape is this system's own addition, not a licence to leave an automated row bare. A test the WBS has not written yet states the RED it must show when it first runs.

## The RED → GREEN → REFACTOR cadence
State it literally in the §19 `**Cadence:**` line and live it one behavior at a time:
1. **Write** the failing test (next row on the list).
2. **Confirm RED** — run it, watch it fail for the right reason.
3. **GREEN** — the minimal code to pass; nothing speculative.
4. **REFACTOR** — tidy with the test green; no new behavior.

One behavior per loop. Don't batch five tests then five impls — interleave.

## Each test pairs to a §20 task ordered after it
For every Test List row, §20 carries: a test task (`· write FIRST · confirm RED`) **then** an impl task (`to GREEN T0xx`). The test always precedes the implementation in the dependency graph. See `references/wbs-guide.md`.

## Secondary lane table + "not tested" gate
After the Test List, a 4-lane table (Unit / Integration / E2E / Manual) with scope · tooling · frequency. Then an explicit `**Explicitly not tested:**` line — what the MVP consciously skips (e.g. cross-browser). Naming lanes while enumerating zero tests is the core anti-pattern; "tests later" = no tests.

## Mandatory generated-code-review lane
If §21 or §22 names ANY code generator (v0 / Bolt / Lovable / marketplace skill / AI scaffold), add a non-optional lane:

```markdown
| Generated-code review | every AI-generated file | `/code-review` + semgrep | before merge |
```

This pairs with the §18 SAST + package-existence control. AI code is ~45% vulnerable and hallucinates ~20% of imports — no generated file merges unreviewed.

## Floors
Test List ≥1 row per P0 FR at `active` stage. At `idea`/`evaluating`, render `N/A — populated at ready stage`.

*Anti-pattern:* a §19 that lists lanes but enumerates zero tests; any P0 FR without a pre-named failing test; a named generator with no generated-code-review lane.
