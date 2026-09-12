# Contributing

This repository is public and takes pull requests. Three deterministic gates
decide whether a change is mergeable; a reviewer reads the diff only after they
pass.

## Before you open a PR

1. **Validator.** `uv run core/scripts/validate.py` must end with
   `✓ ALL CHECKS PASS`. Warnings are allowed only in the documented
   non-blocking classes listed in `CLAUDE.md` §Framework Self-Audit.
2. **Adapters.** After editing anything under `.claude/skills`, `.claude/agents`,
   or `.claude/commands`, run `uv run core/scripts/build_adapters.py` and commit
   the regenerated `.agents/`, `.codex/`, `.cursor/` trees and
   `.agents/skills.lock.json` in the same commit as the source.
   `uv run core/scripts/build_adapters.py --check` must exit 0 with no
   `missing`, `orphan`, `stale`, `leftover`, or `manifest` lines. If the build
   refuses a file it did not generate, move the file or pass `--force`; never
   hand-edit generated output.
3. **Tests.** `uv run --with pytest --with pyyaml pytest core/scripts/tests/ -q`
   must pass. A behavior-bearing change ships its test in the same commit, and
   every test must be able to fail (name the production change that would
   break it). Doc-only changes earn no tests and say so.
4. **Disclosure.** Two lines in the PR description, both required, both
   answerable in one sentence:
   - **Security.** Whether the change touches a security-relevant surface —
     the validator's security checks, the report-only guard, `.gitignore`, the
     MCP server's writes, or anything that fetches — and what you checked if
     it does. "No security-relevant change" is a complete answer when true.
     (RW-2026-09-12-30)
   - **Agent.** Whether an AI agent wrote any part of the change, and which
     one, stated as the identity the agent can actually report: the model name
     it was told verbatim when it was told one, the family alone otherwise.
     Never read the identity out of a config file and never invent a version.
     "Written by hand" is the other valid answer. (RW-2026-09-12-30)

Quote the actual output of the three gates in the PR description. "Should
pass" is not evidence.

**PR-side checks.** There is no CI here: the gates run only where you run them,
and a failure means the validator exited non-zero on your machine. Which checks
exist, what each one scans, whether it fails or warns, and what none of them
cover are in [SECURITY.md](SECURITY.md). (RW-2026-09-12-29)

## Changes under `core/`

Read [core/CODING_STANDARDS.md](core/CODING_STANDARDS.md) first. Reviews cite
its headings; a finding that names a rule there is not a matter of taste.

## Changes to the site (`docs/`)

`docs/` is the public GitHub Pages site. A PR that touches it includes:

- **An intent paragraph you wrote yourself.** A few sentences on what was wrong
  and why this fix, in your own words: not AI-generated, not AI-polished. Rough
  is fine. AI help with the change itself is welcome; only this paragraph has
  to be yours.
- **A screenshot** of the rendered page after the change, at the width the
  change targets (for a responsive fix, one per breakpoint you touched). Redact
  anything personal before attaching.

A PR missing either is sent back for them before review starts.

## Ground rules

- Report a vulnerability privately through the repository's Security tab,
  never in a public issue or pull request; the reporting path, the trust model
  behind installed skills, and the limits of the automated checks are in
  [SECURITY.md](SECURITY.md). (RW-2026-09-12-29)
- No personal data in commits. `knowledge/`, `tasks/`, and `projects/` are
  gitignored by design, and the host's memory directory lives outside the
  repo; see [docs/data-handling.md](docs/data-handling.md).
- `git add` explicit paths only, never `-A` or `.`.
- Keep additions generic and configurable. Follow the existing shape of
  skills, agents, and commands, and keep their bodies host-neutral (see
  [docs/portability.md](docs/portability.md)).
- Document a new feature where a user would look for it: `README.md` for
  users, `CLAUDE.md` for the skill and command catalog.
- `setup.sh` must still run after your change; `bash -n setup.sh` is the
  minimum (validator check 15 covers syntax).
