# Spec anti-patterns — avoid when drafting, flag when found

The `/spec` skill checks these after saving and prints violations. Violations do **not** block the save — they print as soft flags so you decide whether to fix.

1. **Duplicates the PRD verbatim** — spec sections restating FRs, user stories, or background without translating them into components, interfaces, or data flow. Spec is synthesis, not copy-paste. Link back (`see prd.md §5.4`) and add only build-relevant detail.
2. **Placeholders shipped** — any `TBD`, `TK`, `…`, or "to be determined" in the final doc. Either infer with `[INFERRED — low confidence, rerun with --ask]` or consciously defer with a named trigger (`deferred until M1 metrics — see §19`).
3. **Tech choice without justification** — a named library / framework / service with no "why this over what" note. Every P0 stack choice must cite at least one rejected alternative and a one-line reason.
4. **Missing rejected alternatives** — §18 ADR contains fewer than 3 rejected options, or the spec lists only what was picked. Any non-trivial architectural decision deserves a `Rejected: X because Y` line.
5. **Silent integration points** — references external services (`manager-ai`, `Granola`, `Slack`, `Perplexity`, `OpenAI`) without naming the tool / endpoint / auth mode / rate limit / failure behavior. Every external dependency gets a one-row contract in §10.
6. **Over-specifies to line-of-code level** — pseudo-code blocks longer than 15 lines, exhaustive variable-level type declarations, or implementations that belong in code review. Spec shapes, doesn't implement.
7. **No assumptions ledger** — §2 Assumptions Ledger is missing, empty, or all assumptions silently baked in. Each P0 assumption gets a row: what it is, source, risk if wrong, how we'd know.
8. **Scope creep into adjacent skills** — no product-requirement restatement (that's PRD), no risk matrix (pre-mortem), no business model (lean-canvas), no GTM timeline (gtm-plan). Link and summarize in one line max.
9. **Low-confidence inferences shipped unrefined** — spec contains 3+ `[INFERRED — low confidence]` flags from the non-interactive default path and was never rerun with `--ask`. Consider `/spec <name> --ask` before starting build.
10. **No build-order slice** — §19 Milestones describe end-state architecture without a walking-skeleton first milestone, or §20 First-Week Tasks is missing / has fewer than 5 entries. Without a slice, `/sprint-plan` has nothing to pull from.
