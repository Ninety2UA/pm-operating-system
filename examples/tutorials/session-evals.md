# Session Reviews

Learn from your AI sessions by generating structured reviews.

---

## Use Case

**Important:** Generate your first session review in 60 seconds.

1. After completing a significant task with your AI assistant, run:
   ```
   /session-review
   ```

2. Claude reflects on the session and captures:
   - Your prompts (verbatim)
   - What was accomplished
   - Tools and workflow chains used
   - What worked and what didn't
   - Missing capabilities that could become new commands/skills

3. Reviews are saved to `Knowledge/session-reviews/YYYY/MM/DD_summary.md`

**Weekly payoff:** Run `/weekly` at end of week. It reads all session reviews, finds recurring prompts, and suggests new commands/skills to create.

---

## How It Works

Session reviews use a Claude-native approach: Claude writes the review from its own conversation context while the session is still active. No external scripts or trace parsing needed.

```
Session in progress
    |
    v
/session-review (or AGENTS.md nudges at session end)
    |
    v
Claude reflects on the full conversation
    |
    v
Review saved to Knowledge/session-reviews/YYYY/MM/DD_summary.md
    |
    v
/weekly reads reviews --> finds patterns --> suggests commands/skills
```

### Why This Works

- **Claude already has the context** — no need to parse trace files after the fact
- **Captures nuance** — Claude can assess "user preferred the simpler approach" not just "user said no"
- **Zero dependencies** — just a skill file, no Python scripts to maintain
- **Feeds the learning loop** — weekly pattern analysis turns reviews into system improvements

---

## Review Structure

Each review captures:

| Section | Purpose |
|---------|---------|
| **User Prompts (Verbatim)** | Exact requests — feeds weekly pattern detection |
| **What Was Accomplished** | Concrete outcomes |
| **Workflow Chains** | Sequences of commands/skills used together |
| **What Worked** | Approaches to keep |
| **What Didn't Work** | Friction to fix |
| **Patterns Noticed** | Recurring behaviors or bottlenecks |
| **Missing Capabilities** | Candidates for new commands/skills |

---

## The Learning Loop

```
Daily:    /morning saves journal --> work --> /session-review captures learnings
Weekly:   /weekly reads journals + reviews --> suggests commands/skills/AGENTS.md changes
Quarterly: /quarterly reads weekly summaries --> system-level audit and refresh
```

Over time, the commands and skills you use are literally proposed by the system based on your actual usage patterns.

---

## Tips

**When to review:**
- After backlog processing, sprint planning, or project evaluation sessions
- When something went unexpectedly well or poorly
- When you notice yourself doing the same thing repeatedly

**What makes a good review:**
- Thorough verbatim prompts (the highest-value section)
- Specific friction points ("had to manually edit 12 files" not "could be better")
- Concrete missing capability suggestions ("need a /batch-archive command")

---

Back to: [Tutorials Home](README.md)
