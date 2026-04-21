# A/B Test Plan Template

Used by `/ab-test --plan`. Output is a self-contained plan doc the user can save as `knowledge/ab-plan-<slug>.md` or paste into a PRD §7 rollout row.

```markdown
# A/B Test Plan: [Experiment name]

## 1. Hypothesis
We believe [change] will [effect direction] [primary metric] for [segment] because [reasoning]; we'll know if it did when [metric] crosses [threshold] at [significance level] within [duration].

## 2. Baseline
- **Primary metric:** [name] — current value: [X%] (N = [Y], window: [last N days])
- **Secondary / guardrail metrics:** [metric] — acceptable regression: ≤ [Z%]
- **Data source:** [where the baseline came from — dashboard, pull, one-off query]

## 3. Statistical Plan
| Field | Value | Notes |
|-------|-------|-------|
| MDE (minimum detectable effect) | [e.g., 1 percentage point] | smallest lift worth detecting |
| α (significance level) | 0.05 | default two-tailed |
| Power (1 − β) | 0.80 | default |
| N per arm | [computed] | see SKILL.md Step 3 formula |
| Total sample | [2N] | |
| Expected duration | [D] days | at current traffic of [T] visitors/day |
| Randomization unit | [visitor / session / account] | account-level for logged-in flows |

**Sizing note:** [e.g., "MDE set to 1pp because below that the absolute change isn't worth shipping; reducing MDE to 0.5pp would require 4× sample → duration exceeds our patience."]

## 4. Rollout Ramp
Explicit per-stage: exposure %, duration, and the numeric gate to advance. No "start small and ramp" without numbers.

| Stage | Exposure | Duration | Advance gate |
|-------|---------|---------|--------------|
| S1 | 5% | 2 days | No guardrail breach + p50 latency unchanged |
| S2 | 25% | 3 days | Primary metric directionally ≥ baseline + SRM OK |
| S3 | 50% | 4 days | Primary metric lift ≥ [half of MDE] AND guardrails hold |
| S4 | 100% (ship) | n/a | Test reaches N per arm AND p-value < α |

## 5. Kill Criteria
Concrete rollback triggers. If any fires, roll back to control immediately and post-mortem.

- **Guardrail breach:** [metric] degrades by > [Z%] for > [1 hour] at > [5%] exposure
- **Safety signal:** [error rate, crash rate, abuse report] exceeds [threshold]
- **No-detection timeout:** test runs > [1.5× expected duration] without reaching significance → stop and declare inconclusive
- **Sample ratio mismatch (SRM):** control/variant sizes differ by > 10% at any stage

## 6. Observability
- **Primary dashboard:** [link or path]
- **Alerts:** [what pages on which channel] — e.g., `p95 latency > 500ms → Slack #ops`
- **Daily monitoring:** PM checks dashboard daily during S1–S3; eng checks automated alerts

## 7. Decision Point
On test completion, run `/ab-test <results-file>` to compute significance and lift. Output: **ship / keep testing / stop.** Ship only if p-value < α AND practical significance check passes (lift ≥ MDE, guardrails hold).
```

**Fill notes for the skill.** When `/ab-test --plan` drafts this file:
- Compute `N per arm` using the Step 3 formula in `SKILL.md`, plugging in `p_c = baseline rate`, `p_v = baseline + MDE`, `Z_α/2 = 1.96`, `Z_β = 0.84`.
- Compute duration as `(2 × N per arm) / expected_daily_traffic` rounded up to whole days.
- If the user didn't supply traffic, flag `[INFERRED — provide traffic for duration estimate]`.
- Tag any slot without a user-supplied value `[INFERRED]` so the draft is still usable.
