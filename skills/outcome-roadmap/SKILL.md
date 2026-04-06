---
name: outcome-roadmap
description: >
  Generates an outcome-focused roadmap from active projects and goals.
  Reframes work from "what to build" to "what outcomes to achieve."
  Use when reviewing the project pipeline, "show my roadmap", "what outcomes
  am I working toward", "outcome roadmap", "reframe my projects",
  or during quarterly planning to align projects with outcomes.
allowed-tools: Read Write Edit Glob
argument-hint: "[--save]"
---

# Outcome Roadmap

Transform your project pipeline from a feature list into an outcome-focused roadmap that ties every project to a measurable result.

## Quick Start

User: `/outcome-roadmap`
Result: Reads all projects, goals, and OKRs, generates an outcome-focused roadmap, presents inline.

User: `/outcome-roadmap --save`
Result: Same, but saves to `knowledge/outcome-roadmap.md`.

## Instructions

### Step 1: Parse Arguments

Check `$ARGUMENTS` for an optional `--save` flag.

### Step 2: Read Context

Read in this order:
1. `GOALS.md` — vision, success criteria, OKRs (if they exist)
2. Use Glob for `projects/*/idea.md` — read all project frontmatter (title, priority, project_status, category)
3. For projects with status `evaluating` or `active`, read the full idea.md
4. Check for lean canvases: Glob `projects/*/lean-canvas.md`
5. Read `tasks/*.md` frontmatter for active work

### Step 3: Group Projects by Outcome

Don't organize by project name or category. Instead, identify 3-5 outcomes the user is working toward (from GOALS.md and OKRs), then map every project to an outcome:

Outcome framing: **"Enable [who] to [achieve what] so that [business impact]"**

Example outcomes:
- "Enable marketing teams to detect ad spend anomalies so that budget waste is caught early"
- "Enable the user to demonstrate AI product expertise so that consulting clients trust their capabilities"
- "Enable solo advertisers to automate campaign analysis so that they save 5+ hours/week"

Projects that don't map to any outcome should be flagged as "unaligned."

### Step 4: Generate the Roadmap

```markdown
---
title: "Outcome Roadmap"
created_date: YYYY-MM-DD
outcomes: [N]
projects_mapped: [N]
unaligned_projects: [N]
---

# Outcome Roadmap

*Generated YYYY-MM-DD from [N] projects across [N] outcomes*

## Roadmap View

### Now (Active & Evaluating)

**Outcome 1: [Enable X to Y so that Z]**
*Supports: [OKR reference or goal]*

| Project | Status | Pipeline Stage | Next Action |
|---------|--------|---------------|-------------|
| [project-name] | active | Building (sprint N) | [Current task] |
| [project-name] | evaluating | Lean canvas done | `/gtm-plan` |

**Outcome 2: [Enable X to Y so that Z]**
*Supports: [OKR reference or goal]*

| Project | Status | Pipeline Stage | Next Action |
|---------|--------|---------------|-------------|
| [project-name] | evaluating | Validated | `/lean-canvas` |

---

### Next (High-Priority Ideas)

**Outcome 3: [Enable X to Y so that Z]**

| Project | Priority | Quick Assessment |
|---------|----------|-----------------|
| [project-name] | P1 | [One-line from idea.md context] |
| [project-name] | P1 | [One-line from idea.md context] |

---

### Later (Backlog Ideas)

| Project | Priority | Outcome Alignment |
|---------|----------|-------------------|
| [project-name] | P2 | Outcome 1 |
| [project-name] | P3 | Outcome 2 |
| ... | | |

---

### Unaligned Projects

These projects don't clearly support any current goal or outcome. Consider archiving or clarifying their purpose.

| Project | Priority | Why Unaligned |
|---------|----------|---------------|
| [project-name] | P3 | [No matching goal in GOALS.md] |

---

## Pipeline Health

| Metric | Count |
|--------|-------|
| Total projects | [N] |
| Active (building) | [N] |
| Evaluating | [N] |
| Ideas (not yet evaluated) | [N] |
| Unaligned (consider archiving) | [N] |
| Projects with lean canvas | [N] |
| Projects with GTM plan | [N] |
| Projects killed this quarter | [N] |

## Recommendations

1. **[Most impactful recommendation]** — e.g., "You have 3 projects supporting Outcome 1 but none are active. Pick one to activate this week."
2. **[Second recommendation]** — e.g., "15 projects are unaligned with current goals. Consider archiving them to reduce cognitive load."
3. **[Third recommendation]** — e.g., "Outcome 2 has no projects in the pipeline. If this goal matters, run `/discover-ideas` focused on [topic]."
```

### Step 5: Save or Present

If `--save` flag: Save to `knowledge/outcome-roadmap.md`.
Otherwise: Present inline (do not save).

### Step 6: Present Summary

Present:
- Number of outcomes identified
- Distribution: how many projects are Now / Next / Later / Unaligned
- Top recommendation
- Suggest: "Run `/prioritize` to rank projects within each outcome, or `/plan-okrs` to align OKRs with these outcomes."

## Notes

- **No external calls:** Works entirely from local files.
- **Refresh cadence:** Re-run monthly or during quarterly planning. The roadmap is a snapshot, not a live document.
- **Unaligned is a signal:** Many unaligned projects means either the goals need updating or the ideas were captured without strategic intent. Both are worth addressing.
- **Outcome ≠ project:** Multiple projects can serve one outcome. One project should not serve multiple outcomes (sign of scope creep).
