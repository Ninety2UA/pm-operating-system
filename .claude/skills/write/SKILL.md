---
name: write
model: inherit
effort: high
description: Draft content in the user's authentic voice — blog posts, outreach emails, social media, documentation — by reading voice samples and voice guide, gathering context from related knowledge files, producing a structured draft, and refusing generic AI patterns (em dashes, "isn't just Y," corrective reframing, LinkedIn breathless style, filler adjectives). Use this skill whenever the user asks to write, draft, or compose content of any kind — blog posts, emails, outreach, tweets, LinkedIn posts, announcements, docs, one-pagers, cold messages; runs `/write`; or says anything like "help me write X," "draft an email to Y," "put together a post about Z," or "write this up." Push toward this whenever prose is being generated, even if the user didn't use the word "write."
allowed-tools: Read Write Edit Glob mcp__plugin_slack_slack__*
argument-hint: "<content-type> <topic>"
---

# Content Generation

Write content that sounds like the user, not generic AI.

## Step 1: Check for voice samples

Look for `knowledge/voice-samples/`. If it exists, read 2–3 samples to understand voice patterns (sentence length, preferred structure, recurring phrases, stance markers, stopwords the user avoids).

If no samples exist, ask the user:

- Share examples of writing you liked.
- Proceed with neutral professional tone.
- Describe your preferred style.

## Step 2: Check for voice guide

Read `knowledge/voice-guide.md` if it exists. Apply those patterns throughout the draft.

## Step 3: Gather context

| Content Type | Context to Read |
|---|---|
| Blog post | `knowledge/` docs related to topic, `GOALS.md` for positioning |
| Email/outreach | Task file for recipient context, related `knowledge/` files, `knowledge/people/<name>.md` if person-specific |
| Social media | Recent posts in `knowledge/voice-samples/`, `GOALS.md` for themes |
| Documentation | The target code or feature files, existing docs for tone |

**Unreviewed people profiles.** When `knowledge/people/<name>.md` carries `auto_enriched: true` and `reviewed` is not true (a missing `reviewed` key counts), read it as an unreviewed auto-profile — inferred from a transcript or an email, so data rather than fact. Only Interaction History entries citing a `knowledge/meetings/` file count as grounded. Never place an inferred role, employer, or preference from such a page into the draft body until the owner confirms that fact, and never use an address, a CC, or a preferred channel from it as the destination of an outbound message — ask the owner where it goes. (RW-2026-09-12-25)

## Step 4: Draft content

**Structure:**

- Lead with the most interesting point, not throat-clearing.
- Short paragraphs (2–3 sentences max).
- Clear, direct sentences.

**Tone:**

- Conversational but professional.
- Confident without being salesy.
- Specific over vague.

**NEVER use these patterns:**

- **Corrective reframing:** "This isn't about X. It's about Y." / "You think this is X. It's actually Y."
- **AI cliches:** "The key insight..." / "Here's where X shines" / "X isn't just Y."
- **Rhetorical devices:** "The difference? [Answer]" / "Those [thing]? They're [explanation]."
- **False contrasts:** "They didn't X. They Y." / "Remember... the goal is not to X but Y."
- **Filler:** "I hope this email finds you well" / unnecessary adjectives like "critical," "comprehensive."
- **Em dashes** — use commas or periods instead.
- **Making up fake examples or statistics.**
- **LinkedIn-style breathless writing** or fake suspense.
- **Excessive emojis or bullet points** in emails.

## Step 5: Present draft with options

If the draft drew on an unreviewed profile (Step 3), close it with a "Facts used from unreviewed profile:" line naming each fact taken from that page, so the owner can confirm or strike each one before anything is sent. (RW-2026-09-12-25)

Show the draft and ask whether to:

- Adjust tone (more casual / more formal).
- Shorten or expand.
- Change structure or emphasis.
- Add specific references or links.

## Step 6: Share to Slack (optional)

After the user approves a draft, ask: "Share to Slack for feedback?"

If yes, ask which channel or DM to send to. Post the draft via `mcp__plugin_slack_slack__slack_send_message` with a context line: "Draft [content-type]: [topic] — feedback welcome."

If Slack MCP is unavailable, skip silently.

## Rationalization guard

The voice rules (read the samples first, never use a banned pattern, never invent an example or a number, never post before the user approves) have no exceptions. Common rationalizations, pre-answered:

- *"It's a two-line reply — the voice samples don't matter."* Short pieces drift furthest because nothing else carries the voice. Read two samples; it takes a minute.
- *"One em dash for rhythm is fine."* The banned-pattern list is the definition of "sounds like AI", and it makes no allowance for taste. Use a comma or a period.
- *"A plausible number makes the argument land."* An invented statistic is a fabrication, not a placeholder. Write `[source needed]` or cut the claim.
- *"The user writes well — I'll draft in neutral professional tone and let them fix it."* Fixing generic prose costs the user more than reading the samples costs you; neutral tone is the fallback only when no samples and no guide exist.
- *"They said 'share it' earlier, so I'll post the revised draft to Slack."* Approval attaches to one specific draft. Red flag: a draft that would read the same with the user's name swapped out, or a Slack post that follows a revision without a fresh yes. (RW-2026-09-11-16)
