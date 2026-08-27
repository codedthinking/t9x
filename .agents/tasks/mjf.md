---
id: mjf
type: task
status: open
created: 2026-08-27
related: []
blocked_by: []
---
# Automate project migration sweep (see migrate-to-t9x skill)
The procedure lives in `.agents/skills/migrate-to-t9x/`. Tooling could take
over the mechanical parts: dump GitHub issues to task files with
`github: {issue: N}` metadata, scan for TODO/FIXME markers and emit an
inventory draft, wire `blocked_by`/`related` from issue cross-references.
The gentle parts — classification, sign-off, cleanup — stay human-gated.
