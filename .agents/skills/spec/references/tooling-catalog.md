# Tooling catalog — §21 Build Toolkit (AI agents · skills · MCPs)

How to draft §21: the concrete toolchain to BUILD this project, mapped to its §7 components and §25 milestones — **in-repo first**, every row traceable. Three tables (build agent · in-repo skills · MCP servers) + a marketplace-gaps line. Format follows the §21 shapes in `references/spec-template.md`.

## In-repo skill → need map (recommend the existing skill FIRST)
Detect the capability from §7, map to the skill already in the repo before reaching outward:

| Need | In-repo skill |
|------|---------------|
| UI build / review | `/ui-ux-pro-max` |
| Diagrams (C4 / runtime) | `/excalidraw` |
| Deploy (Next.js) | `/vercel:deploy` |
| Web scraping / extraction | `firecrawl` |
| Code QA | `/code-review` + `/verify` + `/run` |
| Slides / decks | `/make-slides` |

These recommendations are **deterministic** — they emit on every run regardless of `--ask`, because they need no network.

## MCP discovery
For MCP servers the FRs imply but the house set lacks, source from the **official MCP Registry** at https://registry.modelcontextprotocol.io/. Name tools with **fully-qualified `Server: tool`** identifiers (e.g. `manager-ai: list_projects`) so the host resolves the wire name. Each new server cross-links to a §15 secret row. List already-wired house servers only if this build actually calls them.

## Marketplace discovery (skills.sh)
For genuine gaps with no in-repo skill, emit the literal **skills.sh** verbs — copyable, not run for the user:
- find: `npx skills find "<capability>"`
- add: `npx skills add <owner/repo@skill>` — **project-scoped install, NOT `-g`** (keep the dependency local to the repo).

Reference: https://www.skills.sh/vercel-labs/skills/find-skills.

## Vetting / security rubric (before any `add`)
1. **Leaderboard-first** — prefer skills surfaced on the skills.sh leaderboard.
2. **Accept** a skill only if it has **≥1K installs** OR comes from an **official source** (e.g. `vercel-labs`, `anthropics`, `microsoft`).
3. **Scan before add** — run Socket or Snyk against it before installing. An unvetted marketplace skill is untrusted code in your build path.

## The `--ask` gate (live vs deterministic)
- **In-repo skill + MCP recommendations** → always emit deterministically (no network).
- **LIVE lookups** — hitting the MCP Registry or skills.sh to resolve a row — run **only with `--ask`**. On the default/batch path, emit the literal `npx skills find "<capability>"` query + the `Server: tool` candidate without executing any network call.

*Anti-pattern:* a generic toolchain dump. Any row not traceable to a named §7 component / §20 task / FR — or copyable verbatim into another project — is boilerplate. Renders `N/A — house MCP servers suffice` for the new-MCP group when none are needed.
