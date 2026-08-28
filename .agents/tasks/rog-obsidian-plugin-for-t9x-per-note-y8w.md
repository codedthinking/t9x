---
id: rog
type: task
status: open
created: 2026-08-28
related: [y8w, 2is, grr, bcm, ru1, d0z, nu9]
blocked_by: []
---
# Obsidian plugin for t9x (per note y8w)
Thin desktop-only Obsidian plugin in `integrations/obsidian/`, installed
via the 2is plugin-install machinery, with an `_agents -> .agents` symlink
so Obsidian can index the workspace. All logic shells out to the `t9x`
CLI. Commands: pick-up-task-at-cursor (paren-match to locate the
`@(word ...)` marker enclosing the cursor, then delegate it to the
default headless agent, which extracts per the manuscript-tasks skill and
executes), new task, close/reopen, promote/demote note, delegate task,
ready list. Review UI is a bundled Bases file, not a custom view.
Delegation is a data table of headless invocations for claude, opencode,
pi, omp, hermes — no harness, no parser in the plugin beyond marker
boundaries. Full design in note y8w.
