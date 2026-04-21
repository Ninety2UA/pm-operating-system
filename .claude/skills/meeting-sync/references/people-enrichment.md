After syncing meetings, check `knowledge/people/` for each meeting attendee. Each person gets their own file: `knowledge/people/firstname-lastname.md`.

Read `knowledge/people/_template.md` for the full profile structure.

**For NEW attendees** (no file exists in `knowledge/people/`):

1. Create `knowledge/people/firstname-lastname.md` using the template structure.

2. Analyze the synced meeting notes/transcript to infer and fill:
   - **Quick Facts:** Role, company, background (from how they were introduced)
   - **Communication Preferences:** Were they formal or casual? Did they prefer data or narrative? Did they drive discussion or listen? Async or sync? Mark inferred fields with "(inferred)".
   - **Decision-Making Style:** Did they decide quickly or need time? Ask for data? Want options? Defer to others?
   - **Meeting Guidelines:** What did they lead with? What got their attention? What bored them?
   - **Key Topics & Priorities:** What did they care about most in the meeting?
   - **How to Build Trust / What Damages Trust:** Any cues from the meeting about what they value?
   - **Interaction History:** Add this meeting as the first entry using the **rich format** below.

3. Enrich from email history using the `gws` CLI:
   ```bash
   gws gmail users messages list --params '{"userId": "me", "q": "from:<name> OR to:<name>", "maxResults": 5}' --format json
   ```
   Then fetch the top messages to analyze:
   - Tone and formality level in their emails
   - Response speed patterns (quick responder or slow?)
   - How they structure communication (bullet points? long prose? one-liners?)
   - What topics they email about vs. discuss in meetings
   
   **Error handling (in order):**
   - If `gws` is not installed (exit 127 / command not found): skip enrichment silently.
   - If `gws` returns HTTP 401 / 403 or mentions "invalid_grant" / "expired": stop enrichment and tell the user: `"gws auth expired — run 'gws auth login' to refresh, then re-sync"`. Do NOT repeatedly retry.
   - If no email history exists (empty result set): skip gracefully, note "no email history" in the person's file.
   - Any other error: log the raw error in the person's file under a `## Enrichment errors` section so the user can triage.

4. Set `auto_enriched: true` in the frontmatter.

**For EXISTING attendees** (file already exists):

1. Add a new entry to `## Interaction History` using the **rich format** below
2. Update `last_interaction` in frontmatter
3. If the meeting transcript reveals NEW information about their communication style, decision-making, or preferences — update the relevant sections. Don't overwrite manually-entered content.
4. If the profile is still thin (mostly "(inferred)" or empty sections) and email history is available, run gws enrichment.

**Rich Interaction History format:**

Instead of just "Met on date about topic", write entries that capture what matters for future prep:

```markdown
- YYYY-MM-DD: **[Meeting Title]** — [2-3 line summary of key discussion points]. Decisions: [what was decided]. Committed to: [action items with owner]. Follow-up: [what to revisit next time].
```

Example:
```markdown
- 2026-04-03: **Q2 Roadmap Review** — Discussed prioritization of AI features vs. platform stability. Sarah pushed for stability first, citing 3 customer escalations. Decisions: defer AI assistant to Q3, focus Q2 on reliability. Committed to: I'll draft revised timeline by Friday; Sarah will share escalation data. Follow-up: check if revised timeline works for engineering capacity.
```

This format feeds directly into `/meeting-prep` — richer history means better preparation for next time.

**For GROUP dynamics** (optional):

If the meeting had 3+ attendees who work together regularly, consider creating or updating a group dynamics file (e.g., `knowledge/people/_team-engineering.md`) capturing:
- How team members interact with each other
- Who defers to whom
- Communication patterns within the group
- How to facilitate alignment across the group

This keeps profiles growing richer with each meeting — communication patterns, decision-making style, and relationship context all compound over time.
