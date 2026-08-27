---
id: w4t
type: note
created: 2026-08-27
related: [2is]
---
# Plan: slash-command plugins for Claude Code, pi, omp, opencode

## Key observation
All four agents already consume the same thing: a markdown prompt file
dropped into a per-agent directory, with the filename becoming the slash
command. There is no runtime to plug into, so "plugin system" reduces to
**one canonical set of command definitions + a per-agent file installer**.
No daemon, no protocol, no per-agent code in the command bodies.

## Per-agent facts (verified 2026-08-27)

| agent       | project dir            | user dir                    | args token   | notes                                    |
|-------------|------------------------|-----------------------------|--------------|------------------------------------------|
| Claude Code | `.claude/commands/`    | `~/.claude/commands/`       | `$ARGUMENTS` | frontmatter: description, argument-hint  |
| pi          | `.pi/prompts/`         | `~/.pi/agent/prompts/`      | `$@`         | badlogic/pi-mono "prompt templates"      |
| omp         | `.omp/commands/`       | `~/.omp/` equivalent        | `$ARGUMENTS` | oh-my-pi; Claude-compatible SKILL format |
| opencode    | `.opencode/command/`   | `~/.config/opencode/command/` | `$ARGUMENTS` | frontmatter: description, agent, model   |

Verify the two "user dir" cells marked uncertain (omp, opencode) against
current docs at implementation time; the table drives a data dict, so a
wrong path is a one-line fix.

## Design

1. **Canonical commands** in the repo: `integrations/commands/<name>.md`.
   Generic frontmatter (`description:`, `args:` hint) and a body written
   agent-agnostically. The only templating is an `{{ARGS}}` placeholder
   substituted per agent. Bodies instruct the agent to call the `t9x` CLI
   (assumed on PATH) — all real logic stays in the CLI, so commands never
   drift from tool behavior.
2. **Adapter table**, not adapter classes: a dict in `src/t9x/plugins.py`
   mapping agent name to {project_dir, user_dir, args_token, frontmatter
   renderer}. Rendering: read canonical file, replace `{{ARGS}}`, emit
   agent-flavored frontmatter, write. Copy, not symlink — the args token
   differs (pi uses `$@`), and install is idempotent regeneration anyway.
3. **CLI verbs**:
   - `t9x plugin install [agent ...] [--user]` — default: all four agents,
     project scope; `--user` targets the home-directory location.
   - `t9x plugin list` — show agents, target paths, and installed state.
   No uninstall verb initially: the files are visible and deletable.

## Initial command set (three, not ten)
- `/t9x-ready` — run `t9x ready`, pick or accept a task id, open a run,
  restate the working loop (open run before experimenting, findings into
  the run file, finish + close).
- `/t9x-task <title>` — create a task from `{{ARGS}}`, ask nothing.
- `/t9x-review` — status overview: ready list, blocked tasks with their
  blockers, recently finished runs; assessment only, no edits.
Everything else (`note new`, `close`, `promote`) is a one-line CLI call
the agent already knows from the using-t9x skill; a slash command adds
nothing.

## Explicitly skipped
- Claude marketplace plugin packaging (`.claude-plugin/plugin.json`) —
  plain commands dir works today; package only if distribution beyond
  this machine is wanted.
- pi/omp TypeScript extensions — markdown prompts suffice; an extension
  would duplicate the CLI.
- Command bodies per agent — one canonical body, token substitution only.

## Sources
- pi prompt templates: github.com/badlogic/pi-mono (coding-agent docs)
- omp slash commands: omp.sh/docs/slash, github.com/can1357/oh-my-pi
