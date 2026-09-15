# t9x

Local-first, file-first workspace for coding and research agents.

t9x separates the human-curated project workspace from the agent's provisional
working state. Agents get a dedicated `.agents/` directory for tasks, runs,
notes, scripts, and skills — all plain markdown with YAML front matter, all
version controlled with Git. The CLI is convenience only; `cat`, `rg`, and
`$EDITOR` always work.

Full specification: [docs/spec.md](docs/spec.md).

## Install

```sh
uv tool install git+https://github.com/codedthinking/t9x
```

or clone and run in place:

```sh
git clone https://github.com/codedthinking/t9x && cd t9x && uv run t9x --help
```

## Quick start

```sh
cd your-project
t9x init                                 # prompts for agent integrations on a TTY
t9x init --agent codex --agent omp       # repeatable, non-interactive selection
t9x init --no-agent-setup                # create only the .agents/ workspace

t9x task new 'Check variance estimator'  # prints e.g.: qx3  .agents/tasks/qx3.md
t9x ready                                # actionable tasks
t9x show qx3                             # resolve any id anywhere under .agents/

t9x run new qx3                          # record an attempt, linked to the task
t9x run finish f2m --outcome inconclusive

t9x note new 'Variance normalization' --related qx3 f2m
t9x note import docs/memo.md --title 'Memo' --move
t9x relate qx3 k9z                       # symmetric weak link
t9x block qx3 1v2                        # qx3 waits on 1v2
t9x close qx3                            # open|blocked -> done

t9x promote .agents/notes/2026-08-27-variance-normalization.md docs/variance.md
```

Every structured object gets a stable lowercase base36 id (`qx3`). The id is canonical; filenames are presentation. Unknown YAML front matter fields survive every t9x edit, so domain workflows can extend the format freely. Mutating commands use atomic file replacement, and multi-object updates roll back earlier replacements when a later write fails.

## Agent integration

`t9x init` offers Codex, Claude Code, OpenCode, OMP, Pi, and Hermes. The shared `using-t9x` skill is installed at `.agents/skills/using-t9x/SKILL.md`; Claude Code also receives `.claude/skills/using-t9x/SKILL.md`. Existing files with different content cause the complete selected integration set to abort instead of being overwritten.

Codex setup installs a named `t9x-workspace` permission profile in `.codex/config.toml`. Start local Codex with `codex -P t9x-workspace`. Repository configuration cannot force a managed runtime to use that profile; the runtime administrator must allow and select it.

`t9x note import` copies by default. `--move` removes the source only after the new note commits. `t9x promote` applies the same destination-first rule in the other direction. A failed source removal rolls back the destination.

## This repository eats its own dog food

The t9x repo is itself a t9x workspace: its open todos are t9x tasks
(`uv run t9x ready`), design interpretations live in `.agents/notes/`, and
agent-facing skills ship in `.agents/skills/` — start with
[using-t9x](.agents/skills/using-t9x/SKILL.md),
[manuscript-tasks](.agents/skills/manuscript-tasks/SKILL.md), and
[migrate-to-t9x](.agents/skills/migrate-to-t9x/SKILL.md).

## Development

```sh
uv sync
uv run pytest
```
