---
id: 2is
type: task
status: open
created: 2026-08-27
related: [w4t, rog]
blocked_by: []
---
# Slash-command plugins for Claude, pi, omp, opencode
Implement per the plan in the related note (w4t): canonical command
markdown in `integrations/commands/`, adapter table in
`src/t9x/plugins.py`, CLI verbs `t9x plugin install [agent ...] [--user]`
and `t9x plugin list`. Ship three commands: /t9x-ready, /t9x-task,
/t9x-review. Verify omp and opencode user-scope directories against
current docs before writing the adapter table.
