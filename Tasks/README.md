# Tasks

Your personal task files live here. Each task is a markdown file with YAML frontmatter.

> This directory is gitignored—your tasks stay private and local.

---

## Quick Reference

| Field | Values |
|-------|--------|
| **priority** | `P0` (today) · `P1` (this week) · `P2` (scheduled) · `P3` (someday) |
| **status** | `n` (not started) · `s` (started) · `b` (blocked) · `d` (done) |
| **category** | `technical` · `outreach` · `research` · `writing` · `admin` · `personal` · `other` |

---

## Creating Tasks

Tasks are created automatically when you say "process my backlog" to your AI assistant.

You can also create them manually using this template:

```yaml
---
title: [Actionable task name]
category: technical
priority: P1
status: n  # n=not_started, s=started, b=blocked, d=done, r=recurring
created_date: YYYY-MM-DD
estimated_time: 60  # minutes, optional
resource_refs:
  - knowledge/example.md
---

# [Task name]

## Context
Tie to a goal in GOALS.md and reference any supporting material.

## Next Actions
- [ ] Step one
- [ ] Step two

## Progress Log
- YYYY-MM-DD: Notes, blockers, decisions.
```
