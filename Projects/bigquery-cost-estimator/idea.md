---
title: BigQuery Cost Estimator
category: technical
priority: P2
project_status: idea
created_date: 2026-03-12
estimated_time: 480
resource_refs:
  - Knowledge/Portfolio_Project_Ideas.md
---

# BigQuery Cost Estimator

## Context
Paste a SQL query and specify table sizes, and the tool estimates the BigQuery on-demand cost — with tips for optimization (partitioning, clustering, column pruning). Built on extensive BigQuery pipeline experience. Supports goal: build & ship products, showcase analytics expertise.

Tech stack: React, SQL parser (basic regex or lightweight parser), cost calculation logic, optimization tips engine.

## Scope
- SQL text input
- Estimated bytes scanned calculator (based on user-provided table sizes)
- Cost estimate at on-demand pricing
- 3-5 optimization suggestions

## Progress Log
- 2026-03-12: Created from Portfolio Project Ideas doc. Build time estimate: 1 day.
