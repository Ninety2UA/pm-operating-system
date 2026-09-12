# Coding standards for `core/`

The criteria a review of `core/` cites instead of restating. `AGENTS.md` loads
into every turn and must stay short; this file is read once per review, so its
rules can carry their reasons. A finding cites the heading (for example
"violates *Temp-plus-rename*"), quotes the rule, then states the defect. Files
this document does not cover fall back to `AGENTS.md` §Working Conventions.

Scope: `core/scripts/`, `core/mcp/`, the two hook scripts the validator wires
(`report-only-guard.sh`, `init-workspace.sh`), and `setup.sh`. Skill, agent,
and command bodies are governed by `AGENTS.md` and by the adapter build's
residual net, not by this file.

## Validator checks

- **A check is a pure function over a root path.** Signature
  `check_<name>(root: Path | str) -> list[str]` in `core/scripts/validate_checks.py`.
  No module globals, no reads outside `root`, no network. It returns one message
  per finding and an empty list when clean.
- **Classification lives in the wiring line, not in the check.** `validate.py`
  wires each check with one line that decides `fail(...)` or `warn(...)`.
  Fail-class is reserved for defects that are green today and would break a
  clone. Warn-class covers lints and remote-coverage findings whose data is
  tracked. Anything that reads gitignored data runs only behind the local
  report flag (`--staleness-report`), never in the default run — with one
  carve-out: the hook-wiring checks (`check_guard_wiring`,
  `check_guard_wiring_timeout`) read `.claude/settings.local.json` in the
  default run, because a mis-wired guard is a defect of this install that
  the owner must see on every run, and the check reports only the wiring
  shape, never the file's contents.
- **Every check ships two tests.** A synthetic fixture under `tmp_path` that
  produces the defect and asserts the message, and a `_green_on_real_repo` test
  that runs the check over `REPO_ROOT` (`from conftest import REPO_ROOT`) and
  asserts an empty list. Write the fixture test first and watch it fail before
  the check exists.
- **A message never echoes a secret.** Name the file, the line, and the rule
  that fired, never the matched value. The lint over credential-shaped paths
  reports the path and the instructing sentence's location, not file contents.
- **No user paths.** Check 37 fails the validator if it hardcodes a home
  directory; derive every path from `ROOT`.
- **Bounded subprocesses.** Every synchronous `subprocess` call in
  `core/scripts/*.py` and `core/mcp/*.py` passes an explicit `timeout` above
  zero and no higher than 600 s and catches its own `TimeoutExpired`, so a
  hung binary surfaces as a named failure carrying the binary and the remedy,
  never as a hang or an emptied result that reads as a clean sweep. The spawn
  lint in `core/scripts/tests/test_source_lints.py` parses the tracked sources
  as an AST and fails on a missing timeout and on one that is `None`, zero,
  negative, or over the ceiling; a non-literal value is trusted and `Popen` is
  a documented gap, because there the bound lives on the pipe handling.
  (RW-2026-09-12-8)

## Writes

- **Temp-plus-rename.** A file another run may read (baseline, registry, lock,
  report) is written to a temp file in the *same* directory and moved into
  place with `os.replace`; `write_baseline_atomic` in `core/scripts/currency.py`
  is the pattern. Never truncate-and-rewrite in place.
- **Defang on write.** Fetched text (changelogs, commit messages, diffs, pages)
  passes through `core/scripts/defang.py` at the site that writes it into a
  report or any tracked file, not in a later cleanup pass. Provenance is
  quoted, never executed.
- **Framework code writes only where it says.** Watchers write under
  `knowledge/currency/`; the adapter build writes the three managed bases and
  its manifest; nothing under `core/` writes into `knowledge/people/`,
  `knowledge/meetings/`, or `knowledge/journals/` (see `docs/data-handling.md`).

## The report-only guard

- **No new binaries.** The guard drill runs under a stub `PATH` that contains
  exactly `cat sed base64 date echo printf tr dirname command realpath bash`.
  Calling anything else (`python3`, `timeout`, `sleep`, `jq`) makes the guard
  fail closed in the drill and fail open on a host that lacks the binary.
- **bash 3.2 floor.** macOS ships bash 3.2: no arrays, no `mapfile`, no
  `read -a`, no `declare -A`, no `${var,,}`. Time bounds use builtins
  (`read -t`, `trap`, `kill`), never `sleep` or `timeout`.
- **Fail closed, exit 2.** Every deny is `exit 2`. The EXIT trap that converts
  any other non-zero status into a deny stays in place; a guard that cannot
  decide denies.
- **Inert without the marker.** The guard's first action is `exit 0` when
  `CE_REPORT_ONLY` is unset, so a guard bug can never brick an interactive
  session. The drill never writes to the repo's real `guard.log`.

## Commits and adapters

- **Path-limited commits.** `git add` names explicit paths; never `git add -A`
  or `git add .`. The repo root carries untracked files and gitignored personal
  data that a wide add would sweep in.
- **Adapters regenerate in the same commit as the source.** Any edit under
  `.claude/skills`, `.claude/agents`, or `.claude/commands` is followed by
  `uv run core/scripts/build_adapters.py`, and the regenerated `.agents/`,
  `.codex/`, `.cursor/` trees plus `.agents/skills.lock.json` land in the same
  commit. The build refuses to overwrite a file it did not generate; resolve a
  refusal by moving the file or passing `--force`, never by hand-editing output.
- **Host-neutral bodies.** Generated skill and agent bodies carry no raw model
  IDs, no Claude-only tool names, and no `.claude/` paths; `--check` enforces
  this residual net and validator check 38 runs the same comparison.
- **Count citations move together.** When the validator's check range changes,
  the `validate.py` banner, the `README.md` counts, `docs/index.html`, and the
  `CLAUDE.md` self-audit parenthetical change in the same commit.

## Tests

- **Every test can fail.** Before writing one, name the production change that
  would break it. Derive expected values by hand, never by calling the code
  under test. Never assert by grepping a skill's or script's own text, which
  only proves the source is the source; run the artifact and assert its output
  or side effect.
- **Doc-only changes earn no tests.** The validator is the replacement gate;
  the PR says so.
- **Fixtures under `tmp_path`, tests under `core/scripts/tests/`.** The global
  `.gitignore` drops `test_*.py` everywhere else, so a test elsewhere is
  silently untracked.
- **The suite never touches the live account.** `conftest.py` moves `HOME` and
  `XDG_CONFIG_HOME` into a throwaway directory in `pytest_sessionstart` —
  before collection, because a module can bind `Path.home()` at import time —
  and forwards only the `uv` cache, the `uv` python directory, and the memory
  directory so the run neither re-downloads nor loses validator coverage. A
  function-scoped watch snapshots the four live config files and every file
  under the memory directory by existence, size, and content digest, and fails
  the offending test by name in `~/...` form. A subprocess launched with an
  explicit `env=` dict never sees the sandbox and resolves the real home
  through the password database: pass `{**os.environ, ...}` unless isolation is
  the point. No test ever writes to a watched file to prove the watch — a drill
  injects its own home under `tmp_path` and the watch over the real one stays
  enforcement only. (RW-2026-09-12-11, RW-2026-09-12-12)
- **A test that greps a committed artifact needs an allow-list entry.** The
  source-grep lint in `core/scripts/tests/test_source_lints.py` fails any test
  function that reads a skill, agent, command, hook, or script as text and then
  searches that text; the exemptions are `(file, function, reason)` triples
  whose length must equal a ceiling constant, so adding one is a visible diff
  line and the PR that raises the ceiling states why the test cannot be made
  behavioural. An entry whose function no longer greps is reported stale and is
  removed rather than kept. (RW-2026-09-12-13)
- **Hook events are a closed set.** `VALID_HOOK_EVENTS` in `validate.py` is
  the nine-event set the platform documents; extend it from the hooks
  reference, never from a skill's example.

## How reviews use this file

Cite the heading, quote the rule, then the finding. If a rule here conflicts
with `AGENTS.md`, this file wins for the files it covers and the conflict is a
finding in its own right. New rules are added here with their reason, not to
`AGENTS.md`.
