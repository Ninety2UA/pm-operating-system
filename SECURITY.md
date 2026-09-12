# Security

This repository is a personal operating system: markdown skills, agents and
commands that an AI coding host reads, a local MCP server that reads and writes
a workspace of markdown files, a validator, and an adapter generator. There is
no hosted service, no database, and no network listener. The security surface
is therefore what a session can be made to do on the machine it runs on, and
what a clone of this repository carries off it.

## Reporting a vulnerability

Report privately through the repository's **Security** tab, **Report a
vulnerability** (GitHub private vulnerability reporting, enabled on this
repository and verified 2026-09-12). Do not open a public issue or pull request
for a security report: the report is itself the disclosure, and this repository
has one maintainer and no embargo process. (RW-2026-09-12-29)

Useful in a report: the file, check, or tool involved, the host and version you
ran, what you expected the boundary to be, and the smallest reproduction you
have. A finding that depends on the owner's local configuration is still worth
reporting — say which configuration.

There is no service-level commitment. One maintainer reads reports and answers
in the advisory thread; a fix ships as a normal commit with a ledger row, and
the advisory names it.

## Automated checks

Three deterministic gates run before a pull request merges, all of them local
([CONTRIBUTING.md](CONTRIBUTING.md) lists the commands). These are the
security-relevant checks inside the first gate,
`uv run core/scripts/validate.py`:

| Check | What it reads | Class |
|---|---|---|
| `secret-scan` | Three roots, not the tree: `docs/ledger/`, `docs/capabilities.md`, and `core/watchers/` — the tracked artifacts a portfolio reader opens — line by line for credential-shaped strings | fail |
| `guard-wiring` | Every command hook wired in the local settings file, which must resolve to a path that exists and is executable | fail |
| `guard-wiring` timeout notice | The wired report-only guard, when it declares an explicit hook `timeout` below the platform default | warn |
| `secret-bypass` | Catalog prose (skills, agents, commands) and the two root instruction files, for text that tells an agent to read a credential-shaped path | warn |
| `backup-coverage` | Git remote state: no `origin` remote, or `main` ahead of its upstream; one "could not determine" line when git cannot answer at all | warn |
| `privacy-placement` | The git index against the repository's own ignore rules, naming any tracked file those rules say should be ignored | warn |
| `tree-hygiene` | The git index for a tracked symlink and for two tracked paths that collide under case folding | warn |

**"Fail" means the validator exits non-zero on the machine that ran it.** There
is no CI in this repository, so a pull request is checked only when the author
or the maintainer runs the gates and quotes the output in the description; an
unquoted "should pass" is not evidence. (RW-2026-09-12-29)

`guard-wiring` is vacuous on a fresh clone. The report-only guard ships
committed but unwired, the check never requires wiring, and with no local
settings file there is nothing for it to resolve — it acquires an opinion only
once someone wires a hook by hand.

## What the checks do not cover

- **Dependencies.** `core/requirements.txt` and `package.json` declare floors,
  not pins, and nothing here scans or locks them. Installing the framework
  installs whatever those ranges resolve to that day.
- **Gitignored data.** The secret scan reads three tracked roots, not the
  working tree. `knowledge/`, `tasks/`, and `projects/` are gitignored by
  design and are never scanned, so nothing mechanical stops a credential or a
  person's details from being written into a task or a meeting note. Keeping
  them out is the owner's discipline, and the rules are in
  [docs/data-handling.md](docs/data-handling.md).
- **Scheduled runs that carry no marker.** The report-only guard fires only in
  a scheduled run that both carries the `CE_REPORT_ONLY` marker and wires the
  hook locally. The Desktop scheduled home has no marker
  ([docs/capabilities.md](docs/capabilities.md), `home.desktop`), so there a
  task's per-tool allow list is the only gate on `prune_completed_tasks`.
- **Interactive sessions.** The guard is inert without the marker, by design,
  so a guard bug cannot brick normal editing. Interactive sessions rely on the
  host's permission prompts.
- **Skill content.** Nothing scans an installed skill, agent, or command for
  what it instructs. That is a decision rather than an oversight; the trust
  model below says why and what stands in its place.
- **The MCP server.** `manager-ai` runs locally over stdio, started by the
  host, with the file access of the session that started it. It has no network
  listener and no authentication because it has no remote surface: anything
  that can start it can already read the workspace.

## Instruction surfaces

Everything installed here belongs to exactly one of three classes, and the
class decides what a change to it can do. (RW-2026-09-12-28)

| Surface | Examples | What it can do |
|---|---|---|
| **Executable** | `core/scripts/*.py`, `core/mcp/*.py`, the hook scripts under `.claude/hooks/`, `setup.sh` | Runs as a process with your user's rights |
| **Instruction** | Installed skills, agents, and commands, plus the adapters generated from them | Prose the session's model follows, with the session's permissions |
| **Inert** | Templates, examples, and workspace markdown | Read as content; acts only when something quotes it into an instruction |

The middle row is the one that gets misread. An installed skill is not
sandboxed and is not data: it is prose the model follows, and it inherits
whatever the session can already do, so installing a third-party skill is the
same kind of decision as running a third-party script. This framework trusts
its own installed instruction surfaces by decision and ships no content scanner
for them. The controls are the ordinary ones: read a skill before installing
it, keep the catalog small enough that reading it is realistic, and remove what
you do not use. (RW-2026-09-12-28)

Everything that arrives during a session is data, never instruction: fetched
web pages, MCP tool results, meeting transcripts, email bodies, and the bodies
of task and project files. An instruction found inside any of them is recorded
as a quote at most and never acted on. That rule is held by prose in the skills
that read those sources and, in a scheduled run carrying the marker with the
hook wired, by the report-only guard. The watchers add one mechanical step of
their own: every quoted upstream string is written defanged, through
`core/scripts/defang.py` where a shell is available, so a malicious changelog
cannot smuggle an instruction into the next session that reads the report.
Interactive sessions have no guard, so there the host's permission prompt is
the gate. (RW-2026-09-12-28)

**Worked example — the prune tool.** `prune_completed_tasks` is the one MCP
tool that moves files. It previews by default and moves nothing without
`confirm: true`, a JSON boolean the tool schema validates before the handler
runs, so a string or a number is a schema error rather than consent. The rule
travels in the tool's own description, because the description is the one
channel every host reads: an instruction to confirm found in a task body, a
transcript, a fetched page, or another tool's result is data, not consent. The
owner sees this session's preview and says yes, or nothing moves.

## Related

- [CONTRIBUTING.md](CONTRIBUTING.md) — the three gates, and the disclosure
  lines every pull request carries.
- [docs/data-handling.md](docs/data-handling.md) — which data may live in the
  workspace at all, and where.
- [docs/capabilities.md](docs/capabilities.md) — the verified capability rows
  these claims rest on, including the per-home enforcement table.
