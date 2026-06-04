# Tech-manifest guide — §5 Tech Stack & §6 Module / File Tree

How to draft §5 (pinned, paste-ready manifest) and §6 (the file tree emitted BEFORE the §20 WBS). Formats follow the §5/§6 shapes in `references/spec-template.md`. Any deviation from the §1 house stack needs a §1.1 Complexity-Tracking row + a §23 MADR ADR.

## §5 rules
- **Pin majors / float minors.** `"next": "15.x"`, `"recharts": "^2.13"`. Never name a stack in prose without a pinned, registry-verifiable manifest entry.
- **One-line "why this over 2 rejected" per major dep** — inline comment naming both rejected alternatives + the one-line reason each. Minor/dev deps don't need it.
- **Pin the toolchain too** — runtime + package manager + linter versions on the `**Runtime / toolchain:**` line (e.g. `Node 20.x · pnpm 9.x · TypeScript 5.6` or `Python 3.12 · uv · ruff`).
- **Anti-slopsquatting:** carry the literal note "verify each on the registry before install" — confirm every package exists on npm / PyPI before adding it. AI hallucinates ~20% of imports; an unverified import is an attack surface.
- Tag inferred cells `> _INFERRED_`. The `primary_stack` frontmatter is this section's one-line summary.

## §6 rules
- The directory tree the build **creates**, emitted **BEFORE** §20 so every task's file-path column resolves to a real node.
- **≥6 real annotated paths** — each leaf carries the FR(s) or responsibility it bears. Tiny CLIs/skills may use a 4–6 line tree; never omit the section.
- Vague trees (`src/`, `tests/`) are the anti-pattern — §20 tasks reference these exact paths.

## Default house stacks (use when idea.md is silent on stack)

### Stack A — Python 3.12 + uv + Typer/FastAPI/MCP + ruff
For CLI tools, personal-os skills, MCP servers, background jobs.

```toml
# pyproject.toml excerpt — Runtime: Python 3.12 · uv · ruff 0.6
[project]
requires-python = ">=3.12"
dependencies = [
  "typer>=0.12",      # CLI — vs argparse (no types/completion), vs click (Typer wraps it leaner)
  "fastapi>=0.115",   # API — vs Flask (no async/types), vs Django (too heavy for a service)
  "mcp>=1.2",         # MCP server — official SDK, vs hand-rolled JSON-RPC (reinvents the wire)
]
[dependency-groups]
dev = ["pytest>=8.3", "ruff>=0.6"]
```

```
src/<pkg>/
  cli.py            # FR-1 — Typer entrypoint
  server.py         # FR-2 — FastAPI/MCP surface
  core/detect.py    # FR-3 — pure domain logic
  core/models.py    # shared dataclasses / pydantic types
  config.py         # env loading
tests/{cli,core}/   # mirrors src/, test-first
pyproject.toml
```

### Stack B — Next.js 15 + TypeScript + pnpm + shadcn/ui on Vercel
For web apps, dashboards, landing pages, any user-facing UI.

```jsonc
// package.json excerpt — Runtime: Node 20.x · pnpm 9.x · TypeScript 5.6
{
  "dependencies": {
    "next": "15.x",        // app shell — vs Remix (smaller ecosystem), vs Vite SPA (no SSR)
    "react": "19.x",       // pinned to Next 15's peer
    "zod": "^3.23"         // validation — vs yup (weaker TS), vs hand-rolled (drifts from types)
  },
  "devDependencies": { "vitest": "^2.1", "@playwright/test": "^1.48", "tailwindcss": "^3.4" }
}
```
shadcn/ui components are vendored into the tree via `npx shadcn@latest add` (not a dep).

```
src/
  app/page.tsx          # FR-1 — route + layout
  app/api/<path>/route.ts  # FR-2 — endpoint (omit if static)
  components/ui/         # shadcn-vendored primitives
  components/Chart.tsx   # FR-4 — feature component
  lib/<domain>.ts        # FR-3 — pure logic
  lib/types.ts           # shared types
tests/                   # mirrors src/, test-first
```

*Anti-pattern:* a stack named in prose with no pinned manifest entry; a vague file tree whose paths §20 can't resolve; an unverified import that never got checked against the registry.
