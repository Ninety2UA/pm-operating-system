---
name: write
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

Show the draft and ask whether to:

- Adjust tone (more casual / more formal).
- Shorten or expand.
- Change structure or emphasis.
- Add specific references or links.

## Step 6: Share to Slack (optional)

After the user approves a draft, ask: "Share to Slack for feedback?"

If yes, ask which channel or DM to send to. Post the draft via `mcp__plugin_slack_slack__slack_send_message` with a context line: "Draft [content-type]: [topic] — feedback welcome."

If Slack MCP is unavailable, skip silently.
