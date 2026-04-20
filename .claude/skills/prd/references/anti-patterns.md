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
