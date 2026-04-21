---
name: ab-test
description: >
  Analyzes A/B test results with statistical rigor — calculates significance,
  confidence intervals, sample size adequacy, and gives a clear "ship it / keep
  testing / stop" recommendation. Use this skill whenever the user mentions A/B
  tests, experiments, statistical significance, conversion lift, "variant vs
  control", "is this result significant", "analyze this test", or shares test
  data from campaigns or product experiments — even if they don't say "A/B test"
  explicitly.
allowed-tools: Read Write Edit Glob
argument-hint: "<description or file path> [--plan]"
---

# A/B Test Analysis

Evaluate A/B test results with statistical rigor — significance testing, confidence intervals, sample size checks, and actionable recommendations. Also plans experiments up-front via `--plan` mode.

## Quick Start

**Analyze results (default):**

User: `/ab-test Control: 1000 visitors, 45 conversions. Variant: 1000 visitors, 62 conversions.`
Result: Calculates conversion rates, statistical significance, confidence intervals, lift, and recommendation.

User: `/ab-test knowledge/experiment-results.md`
Result: Reads test data from file, performs full analysis.

**Plan an experiment (opt-in):**

User: `/ab-test --plan`
Result: Collects hypothesis, baseline, MDE, α, power, traffic; computes required N per arm and expected duration; drafts a plan doc with Statistical Plan + Rollout Ramp + Kill Criteria + Observability from the template at `.claude/skills/ab-test/references/plan-template.md`. Prints the draft and offers to save to `knowledge/ab-plan-<slug>.md`.

## Plan Mode (`--plan`)

When `--plan` is passed, the skill runs a pre-experiment flow instead of the analysis flow.

### Inputs needed
Ask for (batched via `AskUserQuestion` if Claude Code surface supports it, else inline prompts):

1. **Experiment name** — short slug, e.g. `homepage-cta-copy`
2. **Hypothesis** — one sentence: "We believe [change] will [direction] [metric]…"
3. **Primary metric + baseline** — name, current value, N, window
4. **MDE** — minimum detectable effect (absolute or relative); accept `1pp` / `15%` forms
5. **α / power** — defaults `0.05 / 0.80`; ask only if the user wants to override
6. **Expected daily traffic** — visitors/sessions per day; used to compute duration
7. **Randomization unit** — visitor / session / account

### Compute

Reuse the Step 3 sample-size formula exactly:

```
n = (Z_α/2 + Z_β)² × (p_c(1-p_c) + p_v(1-p_v)) / (p_v - p_c)²
```

Where `p_c` = baseline, `p_v` = `p_c + MDE` (or `p_c × (1 + relative_MDE)` for relative forms). Z values: `Z_α/2 = 1.96` for α = 0.05 two-tailed; `Z_β = 0.84` for power = 0.80.

Duration = `ceil(2n / daily_traffic)` days.

### Write the plan

Read `.claude/skills/ab-test/references/plan-template.md`, fill the 7 sections, and save to `knowledge/ab-plan-<slug>.md` (or return inline if the user declines the save prompt). Flag any unsupplied slot `[INFERRED]` so the doc remains usable.

### Print a concise summary

- N per arm + total + duration
- Top-line gate for S1 → S2 and kill criterion
- Path to saved plan doc
- Next step: "When the test completes, run `/ab-test <path-to-results>` to decide ship / keep-testing / stop."

## Instructions

### Step 1: Parse Input

Check `$ARGUMENTS` for either:
- **Inline data:** Numbers for control/variant (visitors, conversions, revenue, etc.)
- **File path:** Path to a file containing test data

If the input is ambiguous or missing, ask:
1. What are you testing? (conversion rate, revenue, engagement, etc.)
2. Control group: sample size and metric value
3. Variant group: sample size and metric value
4. Test duration (days running)
5. Desired confidence level (default: 95%)

### Step 2: Validate Data

Check for common issues:
- **Sample Ratio Mismatch (SRM):** If control/variant sizes differ by >10%, flag it. SRM invalidates results.
- **Minimum sample size:** For conversion rate tests, warn if either group has < 100 conversions.
- **Test duration:** Warn if test ran < 7 days (day-of-week effects) or < 2 full business cycles.
- **Multiple comparisons:** If testing more than one variant, note that significance thresholds should be adjusted (Bonferroni correction).

### Step 3: Calculate Statistics

Perform these calculations (show your work):

**Conversion Rate Test:**
```
Control rate (p_c) = conversions_c / visitors_c
Variant rate (p_v) = conversions_v / visitors_v

Absolute lift = p_v - p_c
Relative lift = (p_v - p_c) / p_c × 100%

Pooled proportion (p_pool) = (conv_c + conv_v) / (n_c + n_v)
Standard error = sqrt(p_pool × (1 - p_pool) × (1/n_c + 1/n_v))
Z-score = (p_v - p_c) / SE
p-value = 2 × (1 - Φ(|Z|))  [two-tailed]

95% CI for difference = (p_v - p_c) ± 1.96 × SE

Significant? p-value < 0.05 (or user-specified alpha)
```

**Required sample size (if test is underpowered):**
```
n = (Z_α/2 + Z_β)² × (p_c(1-p_c) + p_v(1-p_v)) / (p_v - p_c)²
where Z_α/2 = 1.96 (95% confidence), Z_β = 0.84 (80% power)
```

### Step 4: Present Results

Read the output template at `.claude/skills/ab-test/references/ab-test-output-template.md` and fill each section with the computed statistics from Step 3.

### Step 5: Offer Follow-ups

- "Want to test with different confidence levels (90%, 99%)?"
- "Want to calculate the required sample size for a future test?"
- "Want me to save this analysis to knowledge/?"

## Notes

- **No external calls:** Pure mathematical analysis from provided data.
- **Limitations:** This performs frequentist hypothesis testing. For Bayesian analysis or more complex designs (multi-variate, sequential testing), recommend dedicated tools.
- **Practical significance vs. statistical significance:** Always flag when a result is statistically significant but the lift is too small to matter practically (e.g., 0.1% lift on a 10% conversion rate).
- **Common mistakes flagged:** Peeking (checking results too early), stopping early on significance, ignoring SRM, not accounting for seasonality.
