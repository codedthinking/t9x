---
id: grr
type: task
status: done
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

Resolved 2026-08-28 (see note y8w): no CLI tooling. Extraction is LLM
judgment over an open marker vocabulary — `@(word description)`, nestable,
word recorded verbatim as `capabilities: [word]` — so a deterministic
parser was rejected. The syntax and nesting rules are now documented in
the manuscript-tasks skill itself; any agent extracts by following it.
The Obsidian pickup command (task rog) only locates marker boundaries and
delegates to an agent.
