---
id: grr
type: task
status: open
created: 2026-08-27
related: [rog]
blocked_by: []
---
# Manuscript task extraction workflow (@id anchors)
The spec keeps manuscript syntax out of the core. Build the extraction layer
as a workflow on top: find embedded instructions in manuscripts, create tasks
with `origin: {file, line}`, replace the instruction with a short `@id`
anchor. The procedure is drafted as `.agents/skills/manuscript-tasks/`;
tooling to automate it is this task.

Concretized 2026-08-28 (see note y8w): the tooling is a `t9x extract` verb.
Marker syntax `@(type description)`, nestable —
`@(write do this and that @(model verify the proposition))` — where `type`
becomes `capabilities: [type]`. `@(` is the unresolved form of the `@id`
anchor: extraction rewrites the marker to `@<id>` in place, sets
`--origin file:line`, extracts innermost first, and blocks outer on inner.
Interface: `t9x extract <file>` for all markers, `--at <line>` for the one
enclosing that line (prints created ids, outermost last). Tasks land in
`.agents/tasks/` as always. Update the manuscript-tasks skill to document
the marker syntax once the verb exists.
