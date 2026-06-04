# EARS primer — §12 Error Handling & §18.A AI Behavior Contract

How to phrase requirements in EARS (Easy Approach to Requirements Syntax). Used to write the §12 error-scenario rows and the §18.A Reject rows in `references/spec-template.md`. Reference: https://alistair.cockburn.us/structured-requirements-using-ears/.

## The 5 EARS patterns
Each pattern has a fixed keyword shape; the response clause is always `the system shall <response>`.

- **Ubiquitous** (always-on, no trigger) — `The system shall <response>.`
  e.g. *The system shall store every upload as markdown + YAML frontmatter.*
- **Event-driven** (a trigger occurs) — `WHEN <trigger> the system shall <response>.`
  e.g. *WHEN a CSV is uploaded the system shall parse it within 3s.*
- **State-driven** (true while in a state) — `WHILE <state> the system shall <response>.`
  e.g. *WHILE detection is running the system shall disable the upload button.*
- **Unwanted-behavior** (a fault/edge case) — `IF <trigger> THEN the system shall <response>.`
  e.g. *IF the CSV has no numeric column THEN the system shall reject it with an inline message.*
- **Optional-feature** (feature-gated) — `WHERE <feature> the system shall <response>.`
  e.g. *WHERE Slack alerting is enabled the system shall post fatal errors to #ops.*

## §12 error rows use the IF/THEN (unwanted-behavior) form
Every §12 scenario is phrased `IF <trigger> THEN the system shall <response>` in the `EARS scenario` column, paired with user message · retry/recovery · log location:

```markdown
| EARS scenario | User-facing message | Retry / recovery | Log location |
|---------------|---------------------|------------------|--------------|
| IF the CSV has no numeric column THEN the system shall reject it | "No numeric data found — check your file" | inline, no retry | console.warn |
| IF an external API 5xxs THEN the system shall retry twice then alert | "Temporarily unavailable, retrying…" | 2× backoff → Slack #ops | structured error log |
```

Cover at least: bad input, external failure, auth failure, and the riskiest failure from `pre-mortem.md`. A happy-path-only table is the anti-pattern — unhandled sad paths are where AI builders silently skip work.

## §18.A Reject rows also use the IF/THEN form
The §18.A AI Behavior Contract's **Reject** table (6 categories, ≥1 each) states required refusals in the same unwanted-behavior shape — phrase the `Required behavior` as `the system shall <refuse / redact / decline>` triggered by the input:

```markdown
| # | Category | Input | Required behavior |
|---|---------|-------|------------------|
| R1 | PII echo | IF asked to emit user PII → the system shall refuse / redact |
| R2 | Jailbreak | IF "ignore previous instructions…" → the system shall refuse, re-affirm purpose |
```

The Good/Bad tables describe input→output behavior and don't need EARS keywords; only the Reject (refusal) rows take the IF/THEN form.

*Anti-pattern:* free-form error prose ("handle bad input gracefully") instead of a triggered `IF … THEN the system shall …` row an agent can implement and test.
