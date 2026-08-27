---
id: grr
type: task
status: open
created: 2026-08-27
related: []
blocked_by: []
---
# Manuscript task extraction workflow (@id anchors)
The spec keeps manuscript syntax out of the core. Build the extraction layer
as a workflow on top: find embedded instructions in manuscripts, create tasks
with `origin: {file, line}`, replace the instruction with a short `@id`
anchor. The procedure is drafted as `.agents/skills/manuscript-tasks/`;
tooling to automate it is this task.
