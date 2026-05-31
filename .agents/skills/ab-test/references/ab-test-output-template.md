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
