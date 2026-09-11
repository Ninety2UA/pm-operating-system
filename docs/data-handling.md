# Data handling

Security asks whether someone else can read what the workspace holds. This note
asks whether the workspace should hold it at all. It covers the three places
personal data lands: `knowledge/people/`, meeting transcripts under
`knowledge/meetings/`, and `knowledge/journals/`. All three are gitignored by
design, and none of this is machine-checked: the validator's secret scan looks
for credentials, not for personal data, so these rules are kept by the owner
and by the skills that write into those directories.

## Tiers

| Tier | What it is | Examples | Handling |
|---|---|---|---|
| **Non-personal** | Nothing that identifies or describes a person | Product decisions, OKR history, framework notes, public company facts | Store, quote, and share freely; may be tracked in git where the workspace shape allows |
| **Personal** | Identifies a person or describes their work with you | Name, role, employer, work email, what they asked for, what you agreed to | Store only for a stated purpose, only in the gitignored directories; never paste into a commit, PR, issue, channel post, or research query; delete when the purpose ends |
| **Sensitive** | Would harm or embarrass the person if it leaked | Health, family, finances, immigration or legal status, performance judgements, opinions about third parties, anything said in confidence | Do not store. Keep the decision or action it led to, not the detail. If a skill captured it, delete the passage itself |

When a passage mixes tiers, the highest tier governs the whole passage.

## Where it lands

### `knowledge/people/`

One file per person, enriched from meetings and email. Personal tier by default.

- Each file states its purpose in one line (for example "meeting prep and
  follow-ups for the analytics vendor evaluation"). Content that does not serve
  that purpose does not go in.
- Record what the person said about the work. Do not record what they said
  about themselves outside work or about other people.
- Review every person file at the quarterly review and delete files whose
  purpose has ended. The tracked template (`_template.md`) carries no personal
  data and must stay that way.

### `knowledge/meetings/`

Transcripts and synced notes from the meeting tool (Granola). Verbatim speech
of people who did not agree to be in a repository.

- Keep the summary, decisions, and action items. Verbatim transcript text is
  sensitive tier by default: quote it only when the exact wording is the
  insight, and never outside this directory.
- Retention limit: 90 days for verbatim transcript sections by default (the
  owner may set another limit here), after which the summary stands alone. The
  date in the path (`YYYY/MM/DD.md`) makes the sweep a directory listing.
- Never send transcript text to an external service (a research query, a
  channel post, a web tool). Skills that read transcripts work on the local
  copy and return summaries.

### `knowledge/journals/`

The owner's own daily plans and actuals, plus weekly and quarterly reviews.
Personal to the owner; mentions of other people follow the tiers above.

- Write about your work, not about other people's lives. A mention of someone
  else is personal tier; a judgement of them is sensitive tier and stays out.
- Session reviews (`knowledge/session-reviews/`) quote the owner's prompts
  verbatim by design; scrub any name or detail about a third party before
  saving.
- No fixed retention: journals are the compounding loop. The quarterly review
  is the point to delete entries that no longer serve it.

## Rules that apply everywhere

- **Minimize.** Collect to a stated purpose. A skill that enriches a person
  file adds only what its purpose needs; "might be useful" is not a purpose.
- **Retain with a limit.** Verbatim transcripts 90 days; person files until
  the purpose ends; everything reviewed at the quarterly review.
- **Delete for real.** Deleting the file is step one. Then check the derived
  artifacts that quoted it (research briefs, decks, updates, session reviews),
  the host's persistent memory directory (memory files may hold facts derived
  from a person file), local backups and any cloud sync of the workspace, and
  the meeting tool's own store, which this workspace does not control.
- **Answer a request.** If someone asks what the workspace holds about them,
  search `knowledge/` for their name and email, export or delete as asked, and
  note the date it was done in the journal.
- **Sharing asks first.** Posting to a channel or sending to an external
  service is an explicit per-message decision (the assistant instructions
  already require confirmation before any post). Personal-tier content needs
  the person's agreement; sensitive-tier content is not shared.

## Gitignored by design

`.gitignore` excludes `knowledge/people/*` (except the template),
`knowledge/meetings/`, `knowledge/journals/`, `knowledge/session-reviews/`,
`knowledge/decisions/`, `knowledge/research/`, `knowledge/updates/`,
`knowledge/decks/`, `knowledge/voice-samples/`, and the currency reports. A
clone of this repository carries none of it. Keep it that way: never negate
these entries, never copy their content into a tracked file, and never link a
tracked document into them (the validator's link check fails on a clone, where
the target does not exist).

Related: [CONTRIBUTING.md](../CONTRIBUTING.md) (no personal data in commits)
and [portability](portability.md) (which hosts read which directories).
