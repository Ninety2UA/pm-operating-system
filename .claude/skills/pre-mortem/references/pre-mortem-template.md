---
title: "Pre-mortem — [Project Title]"
project: <project-name>
created_date: YYYY-MM-DD
risk_count: [total risks identified]
critical_risks: [count of Critical/High risks]
---

# Pre-mortem — [Project Title]

> It is [date + 6 months]. [Project Title] has failed. Here's what went wrong.

## Risk Matrix

| # | Risk | Category | Likelihood | Impact | Severity | Mitigation |
|---|------|----------|-----------|--------|----------|------------|
| 1 | [Specific risk] | Market | High/Med/Low | High/Med/Low | Critical/High/Med/Low | [Action] |
| 2 | [Specific risk] | Execution | High/Med/Low | High/Med/Low | Critical/High/Med/Low | [Action] |
| ... | | | | | | |

**Severity = Likelihood × Impact** (Critical > High > Medium > Low)

## Detailed Analysis

### Critical & High Risks

#### Risk 1: [Risk title]
**Category:** [Market/Competition/Execution/Technical/Business Model/Distribution/Team/Timing]
**Failure story:** "[Narrative: what happened, why it killed the project]"
**Early warning signs:** [What signals to watch for that indicate this risk is materializing]
**Mitigation:**
- [ ] [Concrete action to reduce likelihood or impact]
- [ ] [Concrete action to reduce likelihood or impact]
**Kill condition:** [If [X] happens, seriously consider stopping this project]

#### Risk 2: [Risk title]
...

### Medium & Low Risks

[Same format, briefer treatment]

---

## Top 3 Actions Before Building

The three most important things to do before committing to build:

1. **[Action]** — Validates against Risk [#]. Do this [timeframe].
2. **[Action]** — Validates against Risk [#]. Do this [timeframe].
3. **[Action]** — Validates against Risk [#]. Do this [timeframe].

## Go / No-Go Assessment

**Overall risk level:** [High / Moderate / Low]
**Recommendation:** [Go — risks are manageable / Go with conditions — address top 3 first / No-go — fundamental risks unresolved]
**Key assumption to validate:** [The single most important thing that must be true for this to succeed]

---

**Suggested next step:**
- If Go: Run `/user-stories <project-name>` to decompose into buildable stories.
- If Go with conditions: Address the top 3 actions first, then re-run `/pre-mortem`.
- If No-go: Run `/prioritize` to redirect effort to a stronger project.
