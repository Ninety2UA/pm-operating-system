---
name: prioritize
description: >
  Ranks projects or tasks using structured prioritization frameworks —
  ICE, RICE, Opportunity Score, or Impact-Effort matrix.
  Use when the backlog is overwhelming, "prioritize my projects",
  "rank these ideas", "which project should I work on", "prioritize",
  "stack rank", or when choosing between multiple options.
allowed-tools: Read Write Edit Glob
argument-hint: "[--framework ice|rice|opportunity|impact-effort] [--scope projects|tasks|all]"
---

# Prioritize

Rank projects or tasks using structured prioritization frameworks to cut through decision paralysis.

## Quick Start

User: `/prioritize`
Result: Reads all projects, applies ICE scoring, presents ranked list with recommendations.

User: `/prioritize --framework rice --scope tasks`
Result: Ranks current tasks using RICE framework.

## Instructions

### Step 1: Parse Arguments

Check `$ARGUMENTS` for:
- `--framework` flag: `ice` (default), `rice`, `opportunity`, `impact-effort`
- `--scope` flag: `projects` (default), `tasks`, `all`

### Step 2: Read Items to Prioritize

**If scope = projects:**
- Glob `projects/*/idea.md` and read all frontmatter + Context section
- Filter to status `idea` and `evaluating` (skip `archived` and `paused`)
- If lean canvases exist, read them for business model data

**If scope = tasks:**
- Glob `tasks/*.md` and read all task files
- Filter to status `n` (not started) and `s` (started)

**If scope = all:**
- Read both projects and tasks

Also read `GOALS.md` for alignment scoring.

### Step 3: Score Each Item

Apply the selected framework:

#### ICE (Impact × Confidence × Ease)
| Factor | Scale | Description |
|--------|-------|-------------|
| **Impact** | 1-10 | How much does this move the needle on goals? |
| **Confidence** | 1-10 | How sure are we about the impact estimate? |
| **Ease** | 1-10 | How easy is this to execute? (10 = trivial, 1 = massive) |
| **Score** | | Impact × Confidence × Ease (max 1000) |

#### RICE (Reach × Impact × Confidence / Effort)
| Factor | Scale | Description |
|--------|-------|-------------|
| **Reach** | # people/quarter | How many people will this affect? |
| **Impact** | 0.25-3 | Minimal (0.25), Low (0.5), Medium (1), High (2), Massive (3) |
| **Confidence** | 0-100% | How certain are we? |
| **Effort** | person-hours | How much work is this? |
| **Score** | | (Reach × Impact × Confidence%) / Effort |

#### Opportunity Score (Importance × (1 − Satisfaction))
| Factor | Scale | Description |
|--------|-------|-------------|
| **Importance** | 1-10 | How important is this problem to the target user? |
| **Satisfaction** | 1-10 | How well do current solutions satisfy the need? |
| **Score** | | Importance × (10 − Satisfaction) (max 100) |

#### Impact-Effort Matrix
| Factor | Scale | Description |
|--------|-------|-------------|
| **Impact** | High/Low | Will this meaningfully advance goals? |
| **Effort** | High/Low | How much time/energy does this require? |
| **Quadrant** | | Quick Win (HI/LE), Big Bet (HI/HE), Fill-in (LI/LE), Avoid (LI/HE) |

### Step 4: Present Results

Present a ranked table sorted by score (highest first):

```markdown
## Prioritization Results — [Framework Name]

*Scored [N] [projects/tasks] on YYYY-MM-DD*

### Ranked List

| Rank | Item | [Factor 1] | [Factor 2] | [Factor 3] | Score | Goal Alignment |
|------|------|-----------|-----------|-----------|-------|----------------|
| 1 | [name] | [X] | [X] | [X] | [XXX] | [Which goal] |
| 2 | [name] | [X] | [X] | [X] | [XXX] | [Which goal] |
| ... | | | | | | |

### Tiers

**Tier 1 — Do Now** (top 20% by score):
- [Project/task name]: [One-line why it scored high]
- [Project/task name]: [One-line why it scored high]

**Tier 2 — Do Next** (next 30%):
- [Items]

**Tier 3 — Backlog** (remaining):
- [Items]

**Consider Killing** (bottom 10% with low goal alignment):
- [Items with low scores AND no goal alignment]

### Recommendations

1. **Start with:** [Top-ranked item] — [Why]
2. **Quick win:** [Highest ease/lowest effort item] — [Do this for momentum]
3. **Kill or archive:** [Bottom items] — [Why they're not worth the effort]
```

### Step 5: Offer Actions

After presenting results, suggest:
- "Want me to activate the top project? Run `/lean-canvas [top-project]` to start evaluating."
- "Want to archive the bottom projects? I'll mark them as `archived`."
- "Want to re-score with a different framework? Try `/prioritize --framework rice`."

## Framework Selection Guide

Present this if the user doesn't specify a framework:

| Framework | Best For | Strengths |
|-----------|----------|-----------|
| **ICE** | Quick gut-check on many items | Fast, simple, good for brainstorming |
| **RICE** | Items with known audience reach | Data-driven, accounts for reach |
| **Opportunity** | Product features, user problems | Customer-centric, identifies underserved needs |
| **Impact-Effort** | Fast triage, binary decisions | Visual, quick, good for small batches |

## Notes

- **No external calls:** Works entirely from local files.
- **Scoring honesty:** Score based on evidence, not optimism. A project with no validation data should have low Confidence.
- **Goal alignment bonus:** Items that directly support GOALS.md priorities should get a mental +1 on Impact. Items with no goal alignment should be flagged for potential archiving.
- **Batch size:** Works best with 5-30 items. Over 30, suggest filtering by category first.
- **Re-scoring:** It's fine to re-run with different frameworks. Each framework highlights different aspects. Convergence across frameworks = strong signal.
