---
id: rog
type: task
status: open
created: 2026-08-28
related: [y8w, 2is, grr]
blocked_by: []
---
# Obsidian plugin for t9x (per note y8w)
Thin desktop-only Obsidian plugin in `integrations/obsidian/`, installed
via the 2is plugin-install machinery, with an `_agents -> .agents` symlink
so Obsidian can index the workspace. All logic shells out to the `t9x`
CLI. Commands: pick-up-task-at-cursor (extract `@(type ...)` marker via
`t9x extract`, then delegate to the default headless agent), new task,
close/reopen, promote/demote note, delegate task, ready list. Review UI
is a bundled Bases file, not a custom view. Delegation is a data table of
headless invocations for claude, opencode, pi, omp, hermes — no harness.
Full design in note y8w. Depends on `t9x extract` (grr) for the cursor
pickup command; skeleton and CRUD commands do not.
