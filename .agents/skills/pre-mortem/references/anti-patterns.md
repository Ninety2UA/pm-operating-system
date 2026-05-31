# Pre-mortem anti-patterns — avoid when drafting, flag when found

The `/pre-mortem` skill checks these after saving and prints violations. Violations do **not** block the save — they print as soft flags so you decide whether to fix.

1. **Fewer than 5 risks** — a pre-mortem with 4 or fewer failure scenarios is probably optimistic, not rigorous. Fix: generate at least one risk per category named in Step 5 that's relevant to this project; 5–10 risks is the working range.
2. **No likelihood × impact score** — risks listed without a severity ranking (critical / high / med / low, or L×I numeric). Fix: score every risk so the top-3 are unambiguous. Equal-weight risks = nothing actionable.
3. **No mitigation owner or trigger** — mitigations exist but no owner or "fires when" condition. Fix: each mitigation gets `Owner: self | external` and a trigger (`Fires when: <signal>` or `Date: <milestone>`). Without owner + trigger, the mitigation never happens.
4. **Solution-first framing in risk text** — risks written as "we forget to do X" or "we don't build Y." Fix: reframe as failures observable externally — "users distrust alerts after first false positive" beats "we build a weak detector."
5. **Missing kill criteria for top-3 risks** — the top-3 risks lack a "stop working on this" signal. Fix: every critical/high risk gets a kill condition, e.g., `Kill if: <10 paying users after 4 weeks of ramp`. Pre-mortem's whole value is preventing sunk-cost.
6. **No Go/No-Go recommendation** — Summary ends without a Go / No-Go / Conditional-Go call. Fix: make the call and cite the top-2 risks that drove it. A pre-mortem without a verdict is a diary entry.
7. **No goal-alignment risk considered** — no risk contemplates the project succeeding but not advancing any `GOALS.md` objective. Fix: add at least one strategic-fit risk or flag `GOALS.md › [refresh needed]` if no current objective fits.
8. **Stale pre-mortem** — `project_status: active` and `pre-mortem.md` not updated in 30+ days despite new artifacts (spec, user-stories, shipped milestones) landing since. Fix: re-run `/pre-mortem --rebuild` or append a Progress Log entry confirming risks still apply.
