---
description: "Generate content in your authentic voice — blog posts, emails, social media, documentation"
argument-hint: "<content-type> <topic>"
---

# Content Generation

Write content that sounds like you, not generic AI.

## Instructions

### Step 1: Check for Voice Samples

Look for `Knowledge/voice-samples/`. If it exists, read 2-3 samples to understand voice patterns.

If no samples exist, ask:
- Share examples of writing you liked
- Proceed with neutral professional tone
- Describe your preferred style

### Step 2: Check for Voice Guide

Read `Knowledge/voice-guide.md` if it exists. Apply those patterns throughout.

### Step 3: Gather Context

| Content Type | Context to Read |
|---|---|
| Blog post | `Knowledge/` docs related to topic, `GOALS.md` for positioning |
| Email/outreach | Task file for recipient context, related `Knowledge/` files |
| Social media | Recent posts in `Knowledge/voice-samples/`, `GOALS.md` for themes |

### Step 4: Draft Content

**Structure:**
- Lead with the most interesting point, not throat-clearing
- Short paragraphs (2-3 sentences max)
- Clear, direct sentences

**Tone:**
- Conversational but professional
- Confident without being salesy
- Specific over vague

**NEVER use these patterns:**
- Corrective reframing: "This isn't about X. It's about Y." / "You think this is X. It's actually Y."
- AI cliches: "The key insight..." / "Here's where X shines" / "X isn't just Y"
- Rhetorical devices: "The difference? [Answer]" / "Those [thing]? They're [explanation]"
- False contrasts: "They didn't X. They Y" / "Remember... the goal is not to X but Y"
- Filler: "I hope this email finds you well" / unnecessary adjectives like "critical", "comprehensive"
- Em dashes — use commas or periods instead
- Making up fake examples or statistics
- LinkedIn-style breathless writing or fake suspense
- Excessive emojis or bullet points in emails

### Step 5: Present Draft with Options

Show the draft and ask:
- Adjust tone (more casual / more formal)
- Shorten or expand
- Change structure or emphasis

### Step 6: Share to Slack (Optional)

After the user approves a draft, ask: "Share to Slack for feedback?"

If yes, ask which channel or DM to send to. Post the draft using `mcp__slack__slack_post_message` with a context line: "Draft [content-type]: [topic] — feedback welcome."

If Slack MCP is unavailable, skip silently.
