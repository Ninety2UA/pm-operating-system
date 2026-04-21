# GTM-Plan anti-patterns — avoid when drafting, flag when found

The `/gtm-plan` skill checks these after saving and prints violations. Violations do **not** block the save — they print as soft flags so you decide whether to fix.

1. **Missing beachhead** — §2 Beachhead is empty, a vague segment ("SMBs"), or copies §1 ICP verbatim. Fix: name one concrete sub-segment you can reach and close on in weeks, not quarters (e.g., "solo performance marketers at B2B SaaS, $5k–$50k/mo ad spend, found via r/PPC").
2. **No numeric channel target** — §4 Channels lists ideas but no target volume, cost, or cadence. Fix: every channel row gets one of `target: N signups/month`, `CAC ≤ $X`, `posts/week`, or similar — otherwise it's an aspiration, not a plan.
3. **No kill criteria on channel bets** — §4 picks channels without specifying when to stop. Fix: add `Kill if: <metric> fails <threshold> after <duration>` per channel. Channels without kill criteria consume all available time.
4. **Pricing without willingness-to-pay evidence** — §5 Pricing names a tier and number, no referenced interview, competitor comp, or lean-canvas input. Fix: cite at least one signal (quote from validation brief, competitor price page, lean-canvas §5) or flag `[INFERRED — price-test in first 10 conversations]`.
5. **Scope creep into PRD territory** — §3 Positioning or §4 Channels restate product functionality instead of market framing. Fix: move feature talk to `prd.md`, keep GTM focused on who / where / how / how-much.
6. **No launch-week ramp plan** — §7 Timeline is monthly milestones only, no week-1 sequence. Fix: add a week-1 day-by-day ramp (e.g., `D1 private beta to 3 peers, D3 Twitter/LinkedIn launch, D5 Product Hunt if early signal, D7 retro + go/no-go on ramp`).
7. **No goal alignment** — plan does not cite `GOALS.md › Objective › KR#`. Fix: link to the specific KR this launch advances, or flag `GOALS.md › [refresh needed]` if no current objective fits.
8. **Stale plan** — `project_status: active` and `gtm-plan.md` not updated in 30+ days. Fix: update with post-launch results or mark plan `paused` / `superseded` with the reason in the Progress Log.
