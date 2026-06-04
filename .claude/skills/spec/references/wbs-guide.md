# WBS guide — §20 Work Breakdown Structure (tasks.md)

How to draft §20: the dependency-ordered task graph an agent runs top-to-bottom. Format follows GitHub Spec Kit `tasks.md`. Read alongside `references/tdd-guide.md` (§19 feeds the test tasks) and `references/spec-template.md` §20 for the exact shapes.

## Decomposition depth — Epic → Task → Sub-task
- **Epic** = a §25 milestone (M1 walking skeleton / M2 MVP / M3 polish). Not a checkbox.
- **Task** = one checkbox `T###`, the unit an agent runs. ≤2h **and** ≤~100 LOC. Names an EXACT file path from §6 + an FR back-ref.
- **Sub-task** = an indented bullet under a Task only when one file needs ≥2 distinct moves; don't manufacture them. Most tasks are leaf checkboxes.

If a task can't fit ≤2h / ≤~100 LOC, split it. A task touching 3 files is 3 tasks.

## The `[P]` parallel marker
Tag `[P]` only when a task touches **different files** AND has **no upstream dependency** in the graph. Two tasks writing the same file are never both `[P]`. A test and its implementation are never `[P]` together (the impl depends on the test existing + RED).

## Test-before-impl ordering
Every implementation task pairs to a §19 test task ordered **before** it. The test row carries `· write FIRST · confirm RED`; the impl row carries `to GREEN T0xx` + `(FR-n, test T0xx)`. Never order an impl task above the test that drives it — that is the headline anti-pattern.

## Phase grouping (fixed order)
`Phase 0 Setup → Phase 1 Foundational (blocking) → Phase 2 M1 → Phase 3 M2 → Phase 4 M3/Polish`. Setup = scaffold tree + pin deps + test runner. Foundational = shared types/contracts everything else imports. Then one phase per milestone.

## Stable T-IDs
`T001`, `T002`, … zero-padded, assigned once, never renumbered. `--deepen` appends new IDs (T013, T014…); it does **not** renumber existing ones. **`/user-stories --tasks` and `/sprint-plan` CONSUME these T-IDs as the decomposition source of truth — they do not re-derive them.** Renumbering breaks every downstream cite.

## Per-milestone Checkpoints + closing dependency graph
End each milestone's phase with a `**Checkpoint M#:**` line = the literal command that proves the slice (mirror §25 Acceptance & Verification). Close §20 with a fenced `### Dependency graph` showing the run order with `→` and `{…}` for parallel fans.

## Worked mini-example

```markdown
### Phase 1 — Foundational (blocking)
- [ ] T003 Define `Anomaly` + `Series` types in `src/types.ts` _(FR-2, FR-3)_
- [ ] T004 [P] Write failing test `tests/detect/zscore.test.ts` — one-outlier series → 1 Anomaly sev=high _(FR-2 · write FIRST · confirm RED)_

### Phase 2 — M1 Walking Skeleton
- [ ] T005 Implement `src/detect/zscore.ts::detect()` to GREEN T004 _(FR-2, test T004)_
- [ ] T006 [P] Write failing test `tests/parse/csv.test.ts` — headered CSV → column map _(FR-1 · write FIRST · confirm RED)_
- [ ] T007 Implement `src/parse/csv.ts` to GREEN T006 _(FR-1, test T006)_
- [ ] T008 Wire `src/pipeline.ts`: parse → detect; depends on T005, T007 _(FR-1, FR-2)_
- **Checkpoint M1:** `pnpm test parse/ detect/ && pnpm build` green; seed CSV → 3 anomalies on chart.

### Dependency graph
\`\`\`
T001→T002→T003→{T004→T005, T006→T007}→T008
\`\`\`
```

T004 (test) precedes T005 (impl); T004 and T006 are `[P]` (different test files, no shared dep); T008 is not `[P]` (depends on T005 + T007).

## Floors
≥12 tasks at `active` stage. At `idea`/`evaluating`, render `N/A — populated at ready stage`.

*Anti-pattern:* tasks without file paths; impl ordered before its test; a flat list ignoring dependencies; renumbered T-IDs that break `/user-stories` + `/sprint-plan` cites.
