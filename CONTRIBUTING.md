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

Quote the actual output of the three gates in the PR description. "Should
pass" is not evidence.

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
