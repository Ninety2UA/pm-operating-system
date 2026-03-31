---
title: ETL Pipeline Visualizer
category: technical
priority: P2
project_status: idea
created_date: 2026-03-12
estimated_time: 960
resource_refs:
  - Knowledge/Portfolio_Project_Ideas.md
---

# ETL Pipeline Visualizer

## Context
Define a data pipeline (sources -> transforms -> destinations) in a YAML or form interface, and the tool renders a visual flow diagram with data preview at each stage. Built on automated ETL/ELT pipeline experience (Google Ads + YouTube metrics via BigQuery). Supports goal: build & ship products, showcase data engineering skills.

Tech stack: React, react-flow for pipeline diagram, YAML parser, sample data at each node.

## Scope
- 3 source types (API, CSV, Database)
- 4 transform types (filter, join, aggregate, rename)
- 2 destination types (warehouse, dashboard)
- Visual flow + sample data preview

## Progress Log
- 2026-03-12: Created from Portfolio Project Ideas doc. Build time estimate: 2 days.
