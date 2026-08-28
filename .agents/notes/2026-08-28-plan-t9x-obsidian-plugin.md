---
id: y8w
type: note
created: 2026-08-28
related: [2is, grr, rog]
---
# Plan: t9x Obsidian plugin

## Key observation
Obsidian already does most of the work: tasks and notes are markdown with
YAML frontmatter, which Obsidian parses, renders, and edits natively, and
the core Bases plugin gives a filterable table view over frontmatter for
free. Obsidian desktop runs Electron with full Node access, so the plugin
can spawn the `t9x` CLI and headless agent CLIs directly. The plugin is
therefore a **thin UI shell**: every operation shells out to `t9x`; no
logic is duplicated in TypeScript. No harness of our own — delegation
spawns the agents' existing headless modes.

## The dot-folder problem
Obsidian does not index folders starting with `.`, so `.agents/` is
invisible to a vault rooted at the repo. Fix: `t9x plugin install obsidian`
creates a symlink `_agents -> .agents` in the vault root (gitignored).
Everything under it becomes first-class Obsidian content — editable,
linkable, Bases-queryable — while the canonical path stays `.agents/` for
the CLI and other agents. The plugin translates `_agents/` paths back to
`.agents/` before calling the CLI.
Caveat: verify symlink behavior under Tresorit sync; fallback is rooting a
second vault at `.agents/` itself (loses same-vault access to the human
workspace).

## Components

### 1. `t9x extract` CLI verb (this is task grr's tooling)
In-text task syntax, adopted from ai-learning's extract-tasks /
task-creation skills but retargeted to t9x rules — tasks live in
`.agents/tasks/`, never `TASKS/*.md`:

- Marker: `@(type description)`, nestable:
  `@(write do this and that @(model verify the proposition))`
- `type` ∈ {write, model, literature, empirics, edit, ...} — recorded as
  `capabilities: [type]` in task frontmatter, per the manuscript-tasks
  skill. Open set; unknown types pass through.
- `@(` is the unresolved form of the `@id` anchor: extraction rewrites
  `@(type ...)` to `@<id>` in place, creating the task with
  `--origin file:line`. Same grep story, same resolution rule
  (manuscript-tasks: replace anchor with produced text when done).
- Nesting: extract innermost first; inner id stays referenced in the outer
  task body and outer is blocked by inner (`t9x block outer inner`).
  The document keeps only the outermost anchor.
- Interface: `t9x extract <file>` (all markers) and
  `t9x extract <file> --at <line>` (marker enclosing that line; prints
  created ids, outermost last). Task bodies follow extract-tasks'
  description guidelines: what/why, enough for an unfamiliar agent.

Lives in the CLI, not the plugin, so all five agents and the slash
commands get it too. This narrows grr from "workflow on top" to a concrete
verb; update grr accordingly.

### 2. Obsidian plugin `integrations/obsidian/`
manifest.json + main.ts (esbuild, `isDesktopOnly: true`). Installed by
extending the 2is adapter table: `t9x plugin install obsidian` copies the
built plugin into `.obsidian/plugins/t9x/` and makes the `_agents`
symlink.

Commands (palette entries; user binds hotkeys):
- **Pick up task at cursor** — THE one shortcut. Saves the active file,
  runs `t9x extract <file> --at <line>`, reloads, then delegates the
  outermost new id to the default agent. One keystroke from prose marker
  to running agent. If the cursor is not inside a marker: notice, no-op.
- **New task** — modal for title → `t9x task new`.
- **Close / reopen task** — acts on the active file's `id:` via
  `t9x close` / `t9x reopen`.
- **Promote note** — active file under `_agents/notes/` → path-suggest
  modal → `t9x promote`.
- **Demote to agent space** — reverse direction; plain `Vault.rename`
  into `_agents/notes/` (a move, not an editorial act; no CLI verb
  needed).
- **Delegate task** — task picker + agent picker → spawn headless run.
- **Ready list** — opens the bundled Base.

Review UI: no custom sidebar view. Ship `_agents/t9x.base` — Bases table
over `_agents/tasks/` with status/blocked_by/capabilities columns and
open/blocked/done filters. Click-through to the task file; close it with
the command. Custom ItemView only if Bases proves too limited.

### 3. Delegation adapter table
A dict in the plugin settings mapping agent name → headless invocation,
mirroring the w4t pattern (data table, not classes):

| agent    | invocation (verify at implementation)      |
|----------|--------------------------------------------|
| claude   | `claude -p "<prompt>"`                     |
| opencode | `opencode run "<prompt>"`                  |
| pi       | headless mode per pi-mono docs             |
| omp      | headless mode per omp docs                 |
| hermes   | via its gateway (Telegram/CLI entry point) |

Prompt template (one string, in settings):
"Work on t9x task <id> in <cwd>. Follow .agents/skills/using-t9x: open a
run before working, record findings in the run file, finish the run, close
the task if done." The spawned process is detached; raw stdout/stderr goes
to `.agents/runs/<id>-<agent>.log` for debugging, while the real record is
the run the agent itself opens. A notice reports spawn and exit. No status
polling, no queue, no harness — the run file is the progress report and
`t9x ready` / the Base is the review surface.

## Explicitly skipped
- Custom sidebar/kanban view — Bases covers review; add only if it falls
  short.
- Task-file watching / live sync — Obsidian's metadata cache already
  refreshes on file change; delegation is fire-and-forget.
- Mobile support — spawning CLIs requires desktop.
- A `t9x demote` CLI verb — it is a file move.
- Community-store packaging — install via `t9x plugin install obsidian`;
  submit to the store only if wanted beyond this machine.

## Order of work
1. `t9x extract` verb + tests (closes grr's tooling gap; usable from every
   agent immediately, before any Obsidian code exists).
2. Plugin skeleton + install path via the 2is adapter table + `_agents`
   symlink + Base file.
3. Commands: new/close/promote/demote, then pick-up-at-cursor wired to
   extract + delegate.
4. Delegation table, verifying each agent's headless invocation as added
   (claude and opencode first; pi, omp, hermes after checking docs).
