# Example PRD

This is a complete example showing all sections filled in for a real project at the `evaluating` stage.

```markdown
---
title: "PRD: Ad Spend Anomaly Detector"
project: ad-spend-anomaly-detector
date: 2026-03-15
status: draft
author: Your Name
hypothesis: "Solo performance marketers will keep an anomaly detector connected 30+ days if alerts arrive within 1 hour and FPR stays <15%."
stage: evaluating
---

# Ad Spend Anomaly Detector — Product Requirements Document

## 1. Summary

**Hypothesis:** Solo performance marketers will keep an anomaly detector connected 30+ days if alerts arrive within 1 hour and false-positive rate stays below 15%.

A monitoring tool that detects unusual spending patterns in Google Ads campaigns and alerts the user before budget waste compounds. Built for performance marketers who manage multiple campaigns and can't watch dashboards all day.

## 2. Background

- **Context:** Managing 50+ Google Ads campaigns means spending anomalies (sudden cost spikes, CTR drops, budget overruns) often go unnoticed for hours or days, burning budget unnecessarily.
- **Why now:** Google's API now exposes real-time cost data, and LLMs can interpret spending patterns contextually rather than relying on rigid threshold rules.
- **Primary goal/OKR:** GOALS.md › Ship 10 products › portfolio KR (Q2 project)
- **vs. alternatives:** Google Ads automated rules are threshold-only and miss contextual anomalies; Optmyzr offers a partial version at $208/mo; most solo marketers rely on 2x-daily manual dashboard checks.

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

## 5. Solution

### 5.1 Key Features

| Feature | Description | Priority | Effort |
|---------|------------|----------|--------|
| Anomaly detection engine | Analyze spend patterns and flag statistical outliers | P0 | L |
| Alert notifications | Send Slack/email alerts when anomaly detected | P0 | M |
| Campaign dashboard | Visual overview of campaign health and anomaly history | P1 | M |
| Root cause hints | Suggest likely cause of anomaly (audience shift, bid change, etc.) | P2 | M |
| Custom sensitivity | Let users tune alert sensitivity per campaign | P2 | S |

Priority: **P0** = blocks MVP, **P1** = ship in v1 after MVP, **P2** = deferred / nice-to-have.

### 5.2 User Flow

1. User connects their Google Ads account via OAuth
2. System ingests campaign data every 15 minutes
3. Detection engine compares current patterns against historical baselines
4. When anomaly detected, system sends Slack alert with: campaign name, metric affected, magnitude, suggested action
5. User clicks through to dashboard showing anomaly details and history

### 5.3 User Stories

#### US-001: Connect Google Ads Account
**Description:** As a marketer, I want to connect my Google Ads account so the tool can monitor my campaigns.
**Tied to FR:** FR-1, FR-5
**Acceptance Criteria:**
- [ ] OAuth flow completes without errors
- [ ] All active campaigns appear in the dashboard within 5 minutes
- [ ] Connection status shown on settings page

#### US-002: Receive Anomaly Alert
**Description:** As a marketer, I want to be alerted when an anomaly is detected so I can take action quickly.
**Tied to FR:** FR-2, FR-3
**Acceptance Criteria:**
- [ ] Alert arrives within 15 minutes of anomaly detection
- [ ] Alert includes: campaign name, metric, magnitude, suggested action
- [ ] Alert links directly to the affected campaign in the dashboard

#### US-003: View Anomaly Dashboard
**Description:** As a marketer, I want to see a visual overview of all my campaigns' health so I can prioritize my attention.
**Tied to FR:** FR-4
**Acceptance Criteria:**
- [ ] Dashboard loads within 3 seconds
- [ ] Each campaign shows health status (green/yellow/red)
- [ ] Clicking a campaign shows anomaly history for the last 30 days

#### US-004: Suppress Alerts During Known Campaign Launch (edge case)
**Description:** As a marketer, I want to silence alerts for a specific campaign during a planned launch window so I don't get false positives when intentional spend spikes occur.
**Tied to FR:** FR-6 (suppression spec), FR-3 (exception clause)
**Acceptance Criteria:**
- [ ] User can mark a campaign "in launch window" for a time range (e.g., next 48 hours)
- [ ] During that window, the detection engine still flags the anomaly internally but suppresses the Slack alert
- [ ] Suppressed alerts appear on the dashboard with a "suppressed" badge

#### US-005: Recover From OAuth Disconnect (edge case)
**Description:** As a marketer, I want to know if my Google Ads connection breaks so I don't mistakenly assume the system is still watching.
**Tied to FR:** FR-7 (detection + alert), FR-5 (credentials handling)
**Acceptance Criteria:**
- [ ] If OAuth token refresh fails, the system sends a "connection lost" alert within 5 minutes
- [ ] Dashboard shows disconnected campaigns with a red badge
- [ ] One-click "Reconnect" button re-initiates the OAuth flow

### 5.4 Functional Requirements

- FR-1 [P0]: The system must ingest Google Ads cost and performance data every 15 minutes
- FR-2 [P0]: When spend deviates more than 2 standard deviations from the 14-day rolling average, the system must flag it as an anomaly
- FR-3 [P0]: The system must send alerts via Slack within 5 minutes of anomaly detection, except for campaigns the user has marked as in a launch window (see FR-6)
- FR-4 [P1]: The system must support monitoring up to 100 campaigns per account
- FR-5 [P0]: The system must not store raw Google Ads credentials — use OAuth refresh tokens only
- FR-6 [P1]: The system must allow a user to mark a campaign "in launch window" for a user-specified time range; detected anomalies during that window are logged to the dashboard but not sent via Slack
- FR-7 [P1]: The system must detect OAuth refresh failures within 5 minutes and send a "connection lost" alert via Slack with a one-click reconnect link

### 5.5 Technical Considerations

- Google Ads API v17 for data ingestion
- Statistical anomaly detection (Z-score against rolling baseline)
- Slack webhook for alerts (simple, no bot needed for MVP)
- SQLite for local data storage in MVP (Postgres for scale)

### 5.6 Assumptions

- Google Ads API rate limits allow 15-minute polling for 100 campaigns — risk if wrong: may need to batch or extend interval — tested-in-MVP: yes, via week-1 load test against a real account
- Solo marketers check Slack frequently enough for alerts to be actionable — risk if wrong: may need email/SMS fallback — tested-in-MVP: no, validate in Phase 2 via 5-user feedback
- 14-day rolling average provides enough baseline data — risk if wrong: seasonal campaigns may need longer windows — tested-in-MVP: yes, by backfilling historical data and replaying on known anomalies

## 6. Scope & Phases

### MVP (Phase 1) — ~3 weeks after start
- Google Ads OAuth connection
- Basic anomaly detection (Z-score on spend and CPC)
- Slack alerts
- Simple campaign list view
- **Won't build:**
  - Custom sensitivity tuning (Phase 2)
  - Root cause analysis (Phase 2)
  - Email alerts (Phase 2)
  - Auto-optimization (permanent — we alert, user decides)
  - Meta/TikTok support (permanent — Google Ads only)
  - Team/multi-user features (permanent — solo-marketer beachhead)
- **Entry criteria:** OAuth works end-to-end for one account; 14-day baseline backfill succeeds on a real account
- **Exit criteria:** 3 beta users connected; ≥5 real anomalies caught in aggregate; false-positive rate <15% on labeled set
- **Kill criteria:** 0/5 positive beta signals after 21 days → shelve or pivot

### Phase 2+ — ~3 weeks after MVP validation
- Root cause hints (bid changes, audience shifts, etc.)
- Custom sensitivity per campaign
- Anomaly history and trends dashboard
- Email alert fallback
- **Entry criteria:** MVP exit criteria met; 30-day connection retention ≥50%

## 7. Success Criteria

### 7a. Leading indicators (weekly or faster)

| Metric | Baseline | Target | Frequency | Measurement Method |
|--------|----------|--------|-----------|-------------------|
| Alerts delivered per user per week | 0 | 3–10 | Weekly | Slack webhook send log |
| Connection retention at day 7 | N/A | ≥70% | Weekly | Users with active OAuth token |
| Dashboard DAU | 0 | ≥1 per active user | Daily | Dashboard page-view log |

### 7b. Lagging indicators (monthly or slower)

| Metric | Baseline | Target | Frequency | Measurement Method |
|--------|----------|--------|-----------|-------------------|
| Monthly wasted spend saved | $0 | 10% reduction | Monthly | Before/after spend comparison per account |
| False positive rate | N/A | <15% | Monthly | User thumbs up/down on alerts |
| 30-day retention | N/A | ≥50% | Monthly | Users still connected after 30 days |

## 8. Evidence

- **r/PPC thread "wasted overnight spend"** (47 comments, Mar 2026) — multiple solo marketers report missing Google Ads spend anomalies for 24+ hours due to timezone/sleep gaps.
- **Optmyzr charges $208/mo** for a partial version of this tool (threshold-only, no contextual detection) — confirms willingness to pay and unmet need at the solo-PM price point.
- **DM from Sarah M. (Hallam Agency)**, Mar 2026: "I wake up to $500 burned overnight on irrelevant clicks. There has to be a better way."

## 9. Open Questions

- [Owner: self] Should MVP support Google Ads MCC (manager) accounts for agency users? Pushes scope +1 week — needed by MVP start.
- [Owner: user-research] Is Slack the right primary channel, or do most solo marketers prefer email? — needed by Phase 2.
- [Owner: data] What's the right default sensitivity threshold — too sensitive means alert fatigue, too loose means missed anomalies? — needed by MVP start.

## 10. Contacts

| Name | Role | Why them | How to Reach |
|------|------|----------|-------------|
| Sarah M. (Hallam Agency) | Early beta tester | Runs 40+ campaigns, DM'd about the pain on Mar 8 | LinkedIn DM |
| r/PPC thread "wasted overnight spend" | Evidence source | 47 comments validating the pain — revisit when answering open questions | reddit.com/r/PPC/… |
| Google Ads API Slack (#api-support) | Unblocker for FR-4 | Confirm 15-min polling fits free-tier quota before Phase 1 | Slack invite link |
```
