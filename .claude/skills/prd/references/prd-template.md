# PRD Template

Always use this exact template structure. Fill in each section based on the project context. See SKILL.md Step 6 for the stage-specific depth rubric (80–150 lines for idea, 150–250 for evaluating, 200–300 for active).

```markdown
---
title: "PRD: [Project Name]"
project: <project-name>
date: YYYY-MM-DD
status: draft
author: [User name from GOALS.md or git config]
hypothesis: "[one-sentence testable hypothesis]"
stage: idea  # idea | evaluating | ready | active | paused | archived
---

# [Project Name] — Product Requirements Document

## 1. Summary

**Hypothesis:** We believe [user] will [behavior] because [reason]; we'll know if [metric crosses threshold].

2-3 sentences: What is this product/feature? What does it do? Who is it for?

## 2. Background

- **Context:** What is this initiative about? What led to it?
- **Why now:** Has something changed — new technology, market shift, user pain?
- **Primary goal/OKR:** GOALS.md › [Objective] › [KR#]
- **vs. alternatives:** How is this better than what users do today? (1–2 sentences)

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

## 5. Solution

### 5.1 Key Features

| Feature | Description | Priority | Effort |
|---------|------------|----------|--------|
| [Feature 1] | [What it does] | P0 | [S/M/L] |
| [Feature 2] | [What it does] | P0 | [S/M/L] |
| [Feature 3] | [What it does] | P1 | [S/M/L] |
| [Feature 4] | [What it does] | P2 | [S/M/L] |

Priority: **P0** = blocks MVP, **P1** = ship in v1 after MVP, **P2** = deferred / nice-to-have.

### 5.2 User Flow

Describe the primary user journey from entry to value:
1. User arrives at [entry point]
2. User does [action]
3. System responds with [result]
4. User achieves [outcome]

### 5.3 User Stories

One primary story per P0 feature, plus one edge-case story for each P0 feature. The `/user-stories` skill later decomposes these into full buildable stories when the project is activated.

#### US-001: [Title]
**Description:** As a [user], I want [feature] so that [benefit].
**Tied to FR:** FR-X, FR-Y
**Acceptance Criteria:**
- [ ] [Specific, verifiable criterion]
- [ ] [Another criterion]

#### US-002: [Title]
**Description:** As a [user], I want [feature] so that [benefit].
**Tied to FR:** FR-Z
**Acceptance Criteria:**
- [ ] [Specific, verifiable criterion]
- [ ] [Another criterion]

Keep stories small. Acceptance criteria must be verifiable, not vague ("works correctly" is bad; "shows confirmation dialog before deleting" is good).

### 5.4 Functional Requirements

Numbered list of specific system behaviors. Tag each with P-tier inline. Each requirement should be testable.

- FR-1 [P0]: The system must [specific behavior]
- FR-2 [P0]: When a user [action], the system must [response]
- FR-3 [P1]: The system shall [constraint or capability]
- FR-4 [P2]: The system should [deferred capability]

Be explicit and unambiguous — these are the contract between the spec and the build.

### 5.5 Technical Considerations

Only if relevant — stack choices, API dependencies, data requirements,
infrastructure needs. Skip if not applicable for this project.

### 5.6 Assumptions

What we believe but haven't proven. Flag these clearly so they can be validated before or during building.

- [Assumption 1] — risk if wrong: [impact] — tested-in-MVP: [yes/no + method]
- [Assumption 2] — risk if wrong: [impact] — tested-in-MVP: [yes/no + method]

## 6. Scope & Phases

Use relative timeframes ("3 weeks after MVP") rather than calendar dates — PRDs outlive
the original schedule.

### MVP (Phase 1)
What goes in the first shippable version? Be ruthless — the MVP should
deliver the core value proposition with minimum features.

- [Feature/capability included]
- [Feature/capability included]
- **Won't build:**
  - [Thing deferred to Phase 2]
  - [Thing never to be built] (permanent)
- **Entry criteria:** [Verifiable conditions to start MVP]
- **Exit criteria:** [Verifiable conditions for MVP to be considered done]
- **Kill criteria:** [Evidence under which to shelve the project]

### Phase 2+
What comes after the MVP proves the concept?

- [Enhancement 1]
- [Enhancement 2]
- **Entry criteria:** [What triggers Phase 2 work]

## 7. Success Criteria

How will we know this worked? Link back to the Key Results in Section 3.

### 7a. Leading indicators (weekly or faster)

| Metric | Baseline | Target | Frequency | Measurement Method |
|--------|----------|--------|-----------|-------------------|
| [Metric 1] | [Current state] | [Goal] | [Weekly] | [How to measure] |
| [Metric 2] | [Current state] | [Goal] | [Daily] | [How to measure] |

### 7b. Lagging indicators (monthly or slower)

| Metric | Baseline | Target | Frequency | Measurement Method |
|--------|----------|--------|-----------|-------------------|
| [Metric 1] | [Current state] | [Goal] | [Monthly] | [How to measure] |

## 8. Evidence

Quotes, usage stats, competitor signals, or customer-discovery notes that back the hypothesis. Concrete beats hand-wavy.

- [Quote or signal 1]
- [Quote or signal 2]
- [Quote or signal 3]

If no direct evidence exists yet, use this exact flag in place of the bullets:

> No direct evidence yet — PRD proceeds on hypothesis; validate via [method] before Phase 2.

## 9. Open Questions

Remaining questions or areas needing clarification before building. Tag each with who unblocks it.

- [Owner: eng] [Question text] — needed by [stage]
- [Owner: user-research] [Question text] — needed by [stage]
- [Owner: self] [Question text] — needed by [stage]

## 10. Contacts

Even for solo projects, naming domain experts, early users, or advisors creates accountability.

| Name | Role | Why them | How to Reach |
|------|------|----------|-------------|
| [Name] | [Domain expert / Early user / Advisor] | [Specific reason — ties to an open question, assumption, or story] | [Email / Slack / LinkedIn] |
```
