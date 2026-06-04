# Good vs. bad — write the "good" column

The `/prd` skill reads this before drafting. For each section, the difference between a PRD that aligns a team and one nobody trusts is specificity. Match the **Good** column: concrete, numeric, falsifiable. Vague is the default failure mode — fight it.

## Hypothesis

- **Bad:** "Improve onboarding to increase engagement."
- **Good:** "We believe replacing the 7-step signup wizard with a single-screen setup for mid-market teams will lift 7-day activation from 23% to 35%, because 67% of drop-offs happen at step 4."

Why: the good version names the user, the change, a baseline → target, and the reason — so it can be proven wrong.

## Problem / Evidence

- **Bad:** "Users find the current experience confusing."
- **Good:** "67% of surveyed users rely on an external spreadsheet to track this; support tickets on it are up 23% quarter-over-quarter; exit interviews cite it as the #3 reason for churn."

Why: counts, trends, and sources turn an opinion into a problem worth solving. If you have no data, say so with the explicit evidence-gap flag — don't dress up a guess.

## Success metrics

- **Bad:** "Engagement: improve. Satisfaction: increase."
- **Good:** "Calendar adoption: 40% of weekly actives within 90 days (baseline 0); support tickets 89 → 65/month; guardrail: p95 page load stays < 2s."

Why: every metric needs a baseline, a target, a cadence, and — where a change could regress something — a guardrail threshold.

## Scope / Non-Goals

- **Bad:** "Build a great calendar experience."
- **Good:** "V1 = read-only event list synced hourly. NOT building: two-way sync (permanent — out of scope for this product), multi-calendar merge (Phase 2), notifications (Phase 2)."

Why: an opinionated "won't build" list — with permanent vs. deferred marked — is what keeps an MVP shippable.

## Workarounds are proof of pain

The cheapest evidence you already have is what users do *instead*. A spreadsheet, a manual 2x-daily check, a hacked-together script — each is a user spending effort to solve the problem without you. Capture it in the §4 *Current Workaround* column, then promote the strongest one into §8 Evidence. "They built a workaround" beats "they said it's a problem."
