<!-- Every section below is required. CONTRIBUTING.md explains each one. -->

## What this changes

<!-- A few sentences you wrote yourself: what was wrong, and why this fix.
Rough is fine, and not AI-generated or AI-polished. Help from an agent with
the change itself is welcome; only this paragraph has to be yours. -->

## Gate output

Paste the last lines of each gate, run on your machine. There is no CI, so this
block is the only evidence that the gates ran. Rewrite every home path as `~`
before pasting — the validator's memory-directory notice prints an absolute
path under your home — and never paste a username.

```text
$ uv run core/scripts/validate.py
(last lines here)

$ uv run core/scripts/build_adapters.py --check
(last lines here)

$ uv run --with pytest --with pyyaml pytest core/scripts/tests/ -q
(last lines here)
```

- [ ] Warnings appear only in the documented non-blocking classes. Environment
      notices, such as a missing memory directory, describe my install rather
      than the framework.
- [ ] A behavior-bearing change ships its test in the same commit, and I can
      name the production change that would break it. A doc-only change says
      so instead.
- [ ] Anything edited under `.claude/skills`, `.claude/agents`, or
      `.claude/commands` ships its regenerated adapters in the same commit.

## Screenshots

Required when this PR touches the published site under `docs/`: one screenshot
of the rendered page after the change, at the width the change targets, and one
per breakpoint for a responsive fix. Redact anything personal first. Write
"not a `docs/` change" when it does not apply.

## Security disclosure

Does this touch a security-relevant surface — the validator's security checks,
the report-only guard, `.gitignore`, the MCP server's writes, or anything that
fetches? Say which, and what you checked. "No security-relevant change" is a
complete answer when it is true. Never report a vulnerability here; see
[SECURITY.md](../SECURITY.md).

## Agent disclosure

Did an AI agent write any part of this change, and which one? Name the identity
the agent can actually report: the model name it was told verbatim when it was
told one, the family alone otherwise. Never read the identity out of a config
file and never invent a version. "Written by hand" is the other valid answer.
