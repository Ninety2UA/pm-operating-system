---
title: Campaign Change-Log Forensics Tool
category: technical
priority: P1
project_status: idea
created_date: 2026-03-12
estimated_time: 960
resource_refs:
  - Knowledge/Portfolio_Project_Ideas.md
---

# Campaign Change-Log Forensics Tool

## Context
A tool that ingests a simulated campaign change history (bid changes, budget adjustments, creative swaps, targeting shifts) alongside performance data, and visually correlates changes with performance inflection points. Translates change-history forensics combined with funnel analysis — a skill used daily at Google to diagnose performance swings — into a standalone product. This is the most differentiated portfolio piece: most candidates talk about diagnosing performance issues but can't show how they do it. Recommended as #2 build priority. Supports goal: build & ship products, become recognized expert.

Tech stack: React + D3 (timeline + overlay charts), synthetic data generator.

## Scope
- Timeline view with change events as markers
- Performance line chart overlay
- Click-to-inspect each change event with a "likely impact" annotation
- Use synthetic/generated data

## Progress Log
- 2026-03-12: Created from Portfolio Project Ideas doc. Build time estimate: 2 days. Recommended as #2 build priority for high differentiation.
