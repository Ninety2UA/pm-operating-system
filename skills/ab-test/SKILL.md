---
name: ab-test
description: >
  Analyzes A/B test results with statistical rigor — calculates significance,
  confidence intervals, sample size adequacy, and provides clear recommendations.
  Use when evaluating experiment results, "analyze this test", "is this result
  significant", "A/B test analysis", "experiment results", or when reviewing
  test data from campaigns or product experiments.
allowed-tools: Read Write Edit Glob
argument-hint: "<description or file path>"
---

# A/B Test Analysis

Evaluate A/B test results with statistical rigor — significance testing, confidence intervals, sample size checks, and actionable recommendations.

## Quick Start

User: `/ab-test Control: 1000 visitors, 45 conversions. Variant: 1000 visitors, 62 conversions.`
Result: Calculates conversion rates, statistical significance, confidence intervals, lift, and recommendation.

User: `/ab-test Knowledge/experiment-results.md`
Result: Reads test data from file, performs full analysis.

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

```markdown
## A/B Test Analysis

### Test Summary
- **What was tested:** [Description]
- **Duration:** [N days]
- **Confidence level:** [95%]

### Results

| Metric | Control | Variant | Difference |
|--------|---------|---------|------------|
| Sample size | [N] | [N] | |
| Conversions | [N] | [N] | |
| Rate | [X.XX%] | [X.XX%] | [+/-X.XX pp] |
| **Relative lift** | | | **[+/-X.X%]** |

### Statistical Analysis

| Check | Result | Status |
|-------|--------|--------|
| Sample Ratio Mismatch | [ratio] | [Pass/Fail] |
| Minimum sample size | [adequate/insufficient] | [Pass/Warn] |
| Test duration | [N days] | [Pass/Warn] |
| Z-score | [X.XX] | |
| p-value | [0.XXXX] | |
| **Statistically significant?** | | **[Yes/No]** |
| 95% Confidence Interval | [[lower%, upper%]] | |
| Statistical power | [X%] | [Adequate/Low] |

### Interpretation

[Plain-English interpretation of the results. What does this mean practically?]

**If significant:** "The variant [outperformed/underperformed] the control by [X%] (95% CI: [lower] to [upper]). This result would occur by chance less than [p-value × 100]% of the time."

**If not significant:** "The difference between control and variant is not statistically significant (p = [X.XX]). We cannot conclude that the variant performs differently from the control. You would need approximately [N] more samples per group to detect a [X%] difference with 80% power."

### Recommendation

**[Ship / Don't Ship / Keep Running / Redesign]**

- **Ship:** Result is significant AND practically meaningful (lift > minimum detectable effect you care about)
- **Don't Ship:** Result is significant but variant is worse, OR result is not significant and test has adequate power
- **Keep Running:** Result is trending but test is underpowered — need [N] more days/samples
- **Redesign:** SRM detected or fundamental test design issue

### Next Steps
1. [Specific action based on recommendation]
2. [Follow-up test suggestion if applicable]
3. [What to monitor post-launch if shipping]
```

### Step 5: Offer Follow-ups

- "Want to test with different confidence levels (90%, 99%)?"
- "Want to calculate the required sample size for a future test?"
- "Want me to save this analysis to Knowledge/?"

## Notes

- **No external calls:** Pure mathematical analysis from provided data.
- **Limitations:** This performs frequentist hypothesis testing. For Bayesian analysis or more complex designs (multi-variate, sequential testing), recommend dedicated tools.
- **Practical significance vs. statistical significance:** Always flag when a result is statistically significant but the lift is too small to matter practically (e.g., 0.1% lift on a 10% conversion rate).
- **Common mistakes flagged:** Peeking (checking results too early), stopping early on significance, ignoring SRM, not accounting for seasonality.
