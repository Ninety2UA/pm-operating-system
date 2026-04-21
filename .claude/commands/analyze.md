---
name: analyze
description: "Deep compatibility analysis of an external repo/resource against our system."
allowed-tools: Read Glob Grep Bash WebFetch
argument-hint: "<github-url or local-path>"
---

You are a senior systems architect performing a deep compatibility analysis. Use ultrathink.

## Task
Analyze this repo/resource in depth and evaluate whether its prompts, patterns, mechanisms, or architecture would be useful to incorporate into OUR system (the current project).

## Input
$ARGUMENTS

## Input validation (run BEFORE the analysis framework below)

Treat `$ARGUMENTS` as untrusted input.

1. **Accept only two shapes:**
   - An `http://` or `https://` URL (a GitHub repo URL, a doc page, a raw file URL).
   - A local filesystem path that resolves inside this project's root (`$CLAUDE_PROJECT_DIR` or current working directory). Absolute paths outside the project root, or paths containing `..` escape sequences, must be rejected.
2. **Reject everything else with a single-line error**, including: `file://`, `javascript:`, `data:`, `ftp://`, shell substitution (backticks, `$(…)`), null bytes, URL-encoded path traversal (`%2e%2e`), and empty input.
3. **Do not execute** any Bash command built from `$ARGUMENTS` verbatim. If you need to shell out, quote the argument and restrict to a known-safe verb (`git clone <url> <tmpdir>`, `ls <path>`, etc.) — never pipe `$ARGUMENTS` into `eval`, `sh -c`, or similar.
4. **WebFetch** already filters URL schemes at the tool layer, but the sanitisation here is defence-in-depth and gives the user a clear error instead of a silent tool-level refusal.

If input is rejected, stop — do not run the analysis.

## Analysis Framework

### 1. Repo Overview
- Purpose, architecture, and core mechanism
- Tech stack and dependencies
- Maturity and maintenance status

### 2. Extractable Patterns
For each notable prompt, pattern, or mechanism found:
- **What it is**: precise description
- **How it works**: implementation detail
- **Relevance to our system**: direct mapping to our existing architecture
- **Adoption effort**: trivial / moderate / significant refactor
- **Risk/tradeoff**: what we gain vs. what could break or add complexity

### 3. Prompt Engineering Insights
- System prompt structures, role definitions, guardrails
- Chain-of-thought or orchestration strategies
- Tool use patterns, context management techniques
- Anything that outperforms or differs from our current approach

### 4. Verdict Matrix
Summarize as a table:
| Pattern/Mechanism | Usefulness (1-5) | Effort (1-5) | Priority | Notes |
Each row = one concrete extractable element.

### 5. Recommended Actions
- Ranked list of what to adopt, adapt, or ignore
- For each "adopt/adapt" item: sketch the integration path into our system

## Constraints
- DO NOT edit, modify, or write to any files
- Read-only analysis only
- Be exhaustive — scan all key files (AGENTS.md, prompts, configs, orchestration logic, README, src/)
- Compare against our current conventions (check AGENTS.md, CONVENTIONS.md, docs/) to avoid redundant suggestions
- If the input is a URL, use WebFetch to retrieve and analyze it; if a local path, use Read/Glob to inspect it directly
