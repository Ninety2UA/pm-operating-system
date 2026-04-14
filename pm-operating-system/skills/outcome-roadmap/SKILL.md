---
name: outcome-roadmap
description: >
  Generates an outcome-focused roadmap from active projects and goals,
  reframing work from "what to build" to "what outcomes to achieve." Use this
  skill whenever the user questions what they're working toward, has many
  projects without clear alignment, feels scattered or overwhelmed by the
  backlog, says "show my roadmap", "what outcomes am I working toward",
  "outcome roadmap", "reframe my projects", or during quarterly planning —
  even if they don't say "roadmap."
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

Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/outcome-roadmap/references/outcome-roadmap-template.md` and fill each section from the projects, goals, and outcomes gathered in Steps 2-3.

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
