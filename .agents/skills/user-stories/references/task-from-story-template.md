---
title: "[Story title]"
category: technical
priority: [P0|P1]
status: n
created_date: YYYY-MM-DD
estimated_time: [minutes based on size]
# actual_time: minutes actually spent — optional, same scale as estimated_time. Added only when the task is done: `/weekly` asks for it, `/morning` offers it. Leave this line commented until then.
resource_refs:
  - projects/<project-name>/user-stories.md
  - projects/<project-name>/prd.md
---

# [Story title]

## Context
Part of [Project Title] — [Epic name].
[Goal alignment from idea.md]

## User Story
As a [role], I want [action], so that [benefit].

## Acceptance Criteria
Carried from the story, tags and failure signals intact.
- [ ] `[auto]` [criterion 1] — fails when: [observable signal]
- [ ] `[auto]` [criterion 2] — fails when: [observable signal]
- [ ] `[manual]` [criterion 3] — checked by [who looks, at what]

## Progress Log
- YYYY-MM-DD: Created from user stories decomposition.
