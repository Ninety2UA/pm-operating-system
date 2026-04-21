# PRD anti-patterns — avoid when drafting, flag when found

The `/prd` skill checks these after saving and prints violations. Violations do **not** block the save — they print as soft flags so you decide whether to fix.

1. **Empty sections** — any section containing only "TBD" or "[placeholder]". Either fill, or consciously skip per the Step 6 stage rubric.
2. **Delegated thinking** — "we'll decide in user-stories" or "figure out later" on MVP-critical calls. PRD must commit to MVP boundaries.
3. **Zero-evidence hypothesis** — Section 8 Evidence has no quote/signal/data **and** no explicit "No evidence yet — validate via X" flag.
4. **Fabricated metrics** — baseline or target numbers without a source. "N/A" is allowed; made-up percentages are not.
5. **Hidden decisions** — P0 requirements that don't trace to a user story **and** a success metric. Orphan FRs signal hidden decisions.
6. **Metric without cadence** — any Section 7 row missing a Frequency column. A target with no frequency is an aspiration, not a metric.
7. **Scope creep into adjacent skills** — no TAM/market-size analysis (that's `/validate-project`), no channel/pricing plan (`/gtm-plan`), no revenue model (`/lean-canvas`), no risk matrix (`/pre-mortem`).
8. **Low-confidence inferences shipped unrefined** — PRD contains 3+ `[INFERRED — low confidence]` flags from the non-interactive default path and was never rerun with `--ask`. Consider `/prd <name> --ask` before starting implementation.
9. **Vibes-based metrics** — a §7 row states a direction without a threshold ("improve engagement", "reduce churn", "better accuracy"). Fix: add a numeric target + cadence, e.g. `≥ 15% reduction, weekly`.
10. **Missing baseline** — a target exists in §7 but no current-state number with N and window. Fix: add `baseline: 8% (N = 186k, 30-day window). Target: ≤ 6.8%.` Without a baseline, "improved" is unprovable.
11. **Fantasy rollout** — §6 MVP / Phase plan says "start small then ramp" with no specifics. Fix: specify exposure %, duration, at least one numeric ramp gate (e.g. "expand 10% → 50% when primary metric ≥ X AND guardrails hold"), and an explicit kill criterion.
12. **No goal alignment** — §2 does not cite `GOALS.md › Objective › KR#`. Fix: link to the specific KR this project advances, or flag `GOALS.md › [refresh needed]` if no current objective fits and the user should run `/refresh-goals`.
