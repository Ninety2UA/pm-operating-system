# Example PRD

This is a complete example showing all sections filled in for a real project.

```markdown
---
title: "PRD: Ad Spend Anomaly Detector"
project: ad-spend-anomaly-detector
date: 2026-03-15
status: draft
author: Dominik Benger
---

# Ad Spend Anomaly Detector — Product Requirements Document

## 1. Summary

A monitoring tool that detects unusual spending patterns in Google Ads campaigns and alerts the user before budget waste compounds. Built for performance marketers who manage multiple campaigns and can't watch dashboards all day.

## 2. Background

- **Context:** Managing 50+ Google Ads campaigns means spending anomalies (sudden cost spikes, CTR drops, budget overruns) often go unnoticed for hours or days, burning budget unnecessarily.
- **Why now:** Google's API now exposes real-time cost data, and LLMs can interpret spending patterns contextually rather than relying on rigid threshold rules.
- **Connection to goals:** Advances "Build tools that solve real PM/marketer pain points" goal and "Ship 3 portfolio projects this quarter" OKR.

## 3. Objective

Reduce wasted ad spend by detecting anomalies within 1 hour of occurrence instead of the current 24-48 hour manual review cycle.

**Key Results:**
- KR1: Detect 90% of spending anomalies within 60 minutes (baseline: manual review catches ~50% within 24hrs)
- KR2: False positive rate below 15% (to maintain user trust in alerts)
- KR3: Save users at least 10% of wasted spend per month vs. no monitoring

## 4. Target Users

| Segment | Problem/Job | Current Workaround | Pain Level |
|---------|------------|-------------------|------------|
| Solo performance marketers | Monitor 20-50 campaigns for budget waste | Manual dashboard checks 2x/day, spreadsheet comparisons | High |
| Small agency teams (2-5 people) | Catch anomalies across client accounts | Shared scripts, Google Ads automated rules (limited) | Medium |

**Primary segment:** Solo performance marketers — they have the most pain (no team to share monitoring) and are easiest to reach (communities, LinkedIn).

## 5. Value Proposition

- **Job addressed:** "Alert me when something abnormal happens with my ad spend so I can fix it before the budget is wasted"
- **Gain:** Peace of mind — stop checking dashboards obsessively. Catch issues in minutes, not days.
- **Pain avoided:** No more waking up to find a campaign burned $500 overnight on irrelevant clicks.
- **vs. alternatives:** Google Ads automated rules are rigid (threshold-based only). This tool uses contextual pattern detection — it knows that a 3x cost increase on a brand campaign is abnormal, but on a new prospecting campaign during launch week it's expected.

## 6. Solution

### 6.1 Key Features

| Feature | Description | Priority | Effort |
|---------|------------|----------|--------|
| Anomaly detection engine | Analyze spend patterns and flag statistical outliers | Must-have | L |
| Alert notifications | Send Slack/email alerts when anomaly detected | Must-have | M |
| Campaign dashboard | Visual overview of campaign health and anomaly history | Must-have | M |
| Root cause hints | Suggest likely cause of anomaly (audience shift, bid change, etc.) | Nice-to-have | M |
| Custom sensitivity | Let users tune alert sensitivity per campaign | Nice-to-have | S |

### 6.2 User Flow

1. User connects their Google Ads account via OAuth
2. System ingests campaign data every 15 minutes
3. Detection engine compares current patterns against historical baselines
4. When anomaly detected, system sends Slack alert with: campaign name, metric affected, magnitude, suggested action
5. User clicks through to dashboard showing anomaly details and history

### 6.3 User Stories

#### US-001: Connect Google Ads Account
**Description:** As a marketer, I want to connect my Google Ads account so the tool can monitor my campaigns.
**Acceptance Criteria:**
- [ ] OAuth flow completes without errors
- [ ] All active campaigns appear in the dashboard within 5 minutes
- [ ] Connection status shown on settings page

#### US-002: Receive Anomaly Alert
**Description:** As a marketer, I want to be alerted when an anomaly is detected so I can take action quickly.
**Acceptance Criteria:**
- [ ] Alert arrives within 15 minutes of anomaly detection
- [ ] Alert includes: campaign name, metric, magnitude, suggested action
- [ ] Alert links directly to the affected campaign in the dashboard

#### US-003: View Anomaly Dashboard
**Description:** As a marketer, I want to see a visual overview of all my campaigns' health so I can prioritize my attention.
**Acceptance Criteria:**
- [ ] Dashboard loads within 3 seconds
- [ ] Each campaign shows health status (green/yellow/red)
- [ ] Clicking a campaign shows anomaly history for the last 30 days

### 6.4 Functional Requirements

- FR-1: The system must ingest Google Ads cost and performance data every 15 minutes
- FR-2: When spend deviates more than 2 standard deviations from the 14-day rolling average, the system must flag it as an anomaly
- FR-3: The system must send alerts via Slack within 5 minutes of anomaly detection
- FR-4: The system must support monitoring up to 100 campaigns per account
- FR-5: The system must not store raw Google Ads credentials — use OAuth refresh tokens only

### 6.5 Technical Considerations

- Google Ads API v17 for data ingestion
- Statistical anomaly detection (Z-score against rolling baseline)
- Slack webhook for alerts (simple, no bot needed for MVP)
- SQLite for local data storage in MVP (Postgres for scale)

### 6.6 Assumptions

- Google Ads API rate limits allow 15-minute polling for 100 campaigns — risk if wrong: may need to batch or extend interval
- Solo marketers check Slack frequently enough for alerts to be actionable — risk if wrong: may need email/SMS fallback
- 14-day rolling average provides enough baseline data — risk if wrong: seasonal campaigns may need longer windows

## 7. Scope & Phases

### MVP (Phase 1) — ~3 weeks after start
- Google Ads OAuth connection
- Basic anomaly detection (Z-score on spend and CPC)
- Slack alerts
- Simple campaign list view
- **Explicitly excluded:** Custom sensitivity tuning, root cause analysis, multi-account support, email alerts

### Phase 2 — ~3 weeks after MVP validation
- Root cause hints (bid changes, audience shifts, etc.)
- Custom sensitivity per campaign
- Anomaly history and trends dashboard

### Non-Goals
- Real-time bid management or auto-optimization
- Support for non-Google ad platforms (Meta, TikTok)
- Team collaboration features

## 8. Success Criteria

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| Anomaly detection time | 24 hrs (manual) | < 1 hr | Time from anomaly start to alert |
| False positive rate | N/A | < 15% | User feedback on alerts |
| Monthly wasted spend saved | $0 | 10% reduction | Before/after spend comparison |

## 9. Open Questions

- Should we support Google Ads MCC (manager) accounts for agency users in Phase 1?
- What's the right default sensitivity — too sensitive means alert fatigue, too loose means missed anomalies?
- Is Slack the right primary channel, or do most solo marketers prefer email?

## 10. Contacts

| Name | Role | How to Reach |
|------|------|-------------|
| [Google Ads API community] | Technical reference | developers.google.com |
| [Target user from LinkedIn] | Early beta tester | LinkedIn DM |
```
