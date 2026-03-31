---
title: Ad Spend Anomaly Detector
category: technical
priority: P2
project_status: idea
created_date: 2026-03-12
estimated_time: 960
resource_refs:
  - Knowledge/Portfolio_Project_Ideas.md
---

# Ad Spend Anomaly Detector

## Context
Upload daily ad spend and performance data, and the tool flags statistical anomalies — spend spikes, sudden CTR drops, conversion rate deviations — with severity scoring and suggested root causes. Built on experience building alerting systems and triaging anomalies daily as part of performance operations at Google. Supports goal: build & ship products, build custom analytical solutions.

Tech stack: React + Recharts, Z-score or IQR-based anomaly detection in JS, Tailwind.

## Scope
- CSV upload
- Time-series chart with anomaly markers (highlighted zones)
- Severity badge per anomaly
- Simple "possible cause" dropdown

## Progress Log
- 2026-03-12: Created from Portfolio Project Ideas doc. Build time estimate: 2 days.
