# PRD Template

Always use this exact template structure. Fill in each section based on the project context. Adapt depth to the project's pipeline stage — idea-stage PRDs can be lighter on sections 6-8, active-stage PRDs need full detail.

```markdown
---
title: "PRD: [Project Name]"
project: <project-name>
date: YYYY-MM-DD
status: draft
author: [User name from GOALS.md or git config]
---

# [Project Name] — Product Requirements Document

## 1. Summary

2-3 sentences: What is this product/feature? What does it do? Who is it for?

## 2. Background

- **Context:** What is this initiative about? What led to it?
- **Why now:** Has something changed — new technology, market shift, user pain?
- **Connection to goals:** Which goal or OKR from GOALS.md does this advance?

## 3. Objective

What's the objective and why does it matter?

**Key Results** (SMART format):
- KR1: [Measurable outcome with target and timeframe]
- KR2: [Measurable outcome with target and timeframe]
- KR3: [Measurable outcome with target and timeframe]

## 4. Target Users

Who are we building this for? Define by problem/job, not demographics.

| Segment | Problem/Job | Current Workaround | Pain Level |
|---------|------------|-------------------|------------|
| [Segment 1] | [What they need] | [How they cope today] | [High/Med/Low] |
| [Segment 2] | [What they need] | [How they cope today] | [High/Med/Low] |

**Primary segment:** [Which segment to focus on first and why]

## 5. Value Proposition

- What customer jobs/needs does this address?
- What will users gain that they don't have today?
- Which pains will they avoid?
- How is this better than existing alternatives?

## 6. Solution

### 6.1 Key Features

| Feature | Description | Priority | Effort |
|---------|------------|----------|--------|
| [Feature 1] | [What it does] | Must-have | [S/M/L] |
| [Feature 2] | [What it does] | Must-have | [S/M/L] |
| [Feature 3] | [What it does] | Nice-to-have | [S/M/L] |

### 6.2 User Flow

Describe the primary user journey from entry to value:
1. User arrives at [entry point]
2. User does [action]
3. System responds with [result]
4. User achieves [outcome]

### 6.3 User Stories

Initial high-level stories — the `/user-stories` skill later decomposes these into
detailed buildable stories with full acceptance criteria when the project is activated.

#### US-001: [Title]
**Description:** As a [user], I want [feature] so that [benefit].
**Acceptance Criteria:**
- [ ] [Specific, verifiable criterion]
- [ ] [Another criterion]

#### US-002: [Title]
**Description:** As a [user], I want [feature] so that [benefit].
**Acceptance Criteria:**
- [ ] [Specific, verifiable criterion]
- [ ] [Another criterion]

Keep stories small — each should represent a single outcome achievable in one focused session. Acceptance criteria must be verifiable, not vague ("works correctly" is bad; "shows confirmation dialog before deleting" is good).

### 6.4 Functional Requirements

Numbered list of specific system behaviors. Each requirement should be testable.

- FR-1: The system must [specific behavior]
- FR-2: When a user [action], the system must [response]
- FR-3: The system shall [constraint or capability]

Be explicit and unambiguous — these are the contract between the spec and the build.

### 6.5 Technical Considerations

Only if relevant — stack choices, API dependencies, data requirements,
infrastructure needs. Skip if not applicable for this project.

### 6.6 Assumptions

What we believe but haven't proven. Flag these clearly so they can be
validated before or during building.

- [Assumption 1] — risk if wrong: [impact]
- [Assumption 2] — risk if wrong: [impact]

## 7. Scope & Phases

Use relative timeframes ("3 weeks after MVP") rather than calendar dates — PRDs outlive
the original schedule.

### MVP (Phase 1)
What goes in the first shippable version? Be ruthless — the MVP should
deliver the core value proposition with minimum features.

- [Feature/capability included]
- [Feature/capability included]
- **Explicitly excluded:** [Things that feel important but aren't MVP]

### Phase 2+
What comes after the MVP proves the concept?

- [Enhancement 1]
- [Enhancement 2]

### Non-Goals
Things this project intentionally does NOT do:
- [Non-goal 1]
- [Non-goal 2]

## 8. Success Criteria

How will we know this worked? Link back to the Key Results in Section 3.

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| [Metric 1] | [Current state] | [Goal] | [How to measure] |
| [Metric 2] | [Current state] | [Goal] | [How to measure] |

## 9. Open Questions

Remaining questions or areas needing clarification before building:
- [Question 1]
- [Question 2]

## 10. Contacts (Optional)

Even for solo projects, naming domain experts, early users, or advisors creates accountability.

| Name | Role | How to Reach |
|------|------|-------------|
| [Name] | [Domain expert / Early user / Advisor] | [Email / Slack / etc.] |
```
