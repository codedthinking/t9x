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

### 1. In-text markers: a skill, not a CLI verb (decided 2026-08-28)
Extraction is LLM work — the `@(word ...)` vocabulary is open by design,
so interpreting a marker takes judgment, not a parser. No `t9x extract`
verb; the syntax lives in the manuscript-tasks skill, which any of the
five agents follows:

- Marker: `@(word description)`, nestable:
  `@(write do this and that @(model verify the proposition))`
- The word is an **open vocabulary, not a registry**: recorded verbatim as
  `capabilities: [word]`, interpreted by the receiving agent, so
  `@(prove ...)` or `@(hungarian ...)` work without any pre-written
  capability. Never validated against a list.
- `@(` is the unresolved form of the `@id` anchor: the agent rewrites the
  marker to `@<id>`, creates the task with `--origin file:line`, extracts
  innermost first, blocks outer on inner, leaves only the outermost
  anchor. Resolution rule as in manuscript-tasks: replace the anchor with
  the produced text when done.

The syntax section is written into `.agents/skills/manuscript-tasks/`
(this closes grr).

Ecosystem fit (korenmiklos/skills @ 8f02a94): extract-tasks is already
t9x-native — `(type ...)` S-expressions in drafts, tasks to
`.agents/tasks/`, `@id` comment anchors (`<!-- @qx3 -->`, `% @qx3`) — and
execution skills (writing, model, literature, empirics, editing) pick
tasks up by capability. The `@(word ...)` marker is the open-vocabulary
superset of that closed five-type pipeline; when the word matches an
execution skill, the delegated agent follows it, otherwise it improvises.
To settle at implementation: extract-tasks uses bare `(type` — collision-
prone in ordinary prose; consider migrating it to `@(` so one grep
pattern covers both — and it says `t9x relate` blocks the outer task,
but the blocking verb is `t9x block`; relate is a symmetric weak link.

### 2. Obsidian plugin `integrations/obsidian/`
manifest.json + main.ts (esbuild, `isDesktopOnly: true`). Installed by
extending the 2is adapter table: `t9x plugin install obsidian` copies the
built plugin into `.obsidian/plugins/t9x/` and makes the `_agents`
symlink.

Commands (palette entries; user binds hotkeys):
- **Pick up task at cursor** — THE one shortcut. The plugin does no
  extraction itself: it paren-matches only to locate the `@(...)` marker
  enclosing the cursor, saves the file, and spawns the default agent with
  "extract the marker at <file>:<line> per the manuscript-tasks skill,
  then execute the resulting task(s)". The agent creates the tasks,
  rewrites the marker to `@id` anchors (Obsidian reloads the saved file
  on external change), and does the work. One keystroke from prose marker
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
the task if done. If the task's capabilities word matches an execution
skill (writing, model, literature, empirics, editing), follow that skill." The spawned process is detached; raw stdout/stderr goes
to `.agents/runs/<id>-<agent>.log` for debugging, while the real record is
the run the agent itself opens. A notice reports spawn and exit. No status
polling, no queue, no harness — the run file is the progress report and
`t9x ready` / the Base is the review surface.

## Explicitly skipped
- A `t9x extract` CLI verb — extraction is judgment over an open
  vocabulary, so it stays LLM work under the manuscript-tasks skill; a
  deterministic parser would either reject novel words or duplicate the
  agent's interpretation. The plugin only locates marker boundaries.
- Custom sidebar/kanban view — Bases covers review; add only if it falls
  short.
- Task-file watching / live sync — Obsidian's metadata cache already
  refreshes on file change; delegation is fire-and-forget.
- Mobile support — spawning CLIs requires desktop.
- A `t9x demote` CLI verb — it is a file move.
- Community-store packaging — install via `t9x plugin install obsidian`;
  submit to the store only if wanted beyond this machine.

## Order of work
1. Marker syntax documented in the manuscript-tasks skill (done
   2026-08-28; closes grr — usable from every agent before any Obsidian
   code exists).
2. Plugin skeleton + install path via the 2is adapter table + `_agents`
   symlink + Base file.
3. Commands: new/close/promote/demote, then pick-up-at-cursor wired to
   marker-locate + delegate.
4. Delegation table, verifying each agent's headless invocation as added
   (claude and opencode first; pi, omp, hermes after checking docs).
