---
id: 9aj
type: note
created: 2026-08-27
related: []
---
# Design interpretations in the prototype
Choices the implementation makes where the spec leaves room. Provisional;
revisit if any turns out to be wrong in use.

- `relate` links symmetrically: each id lands in the other object's
  `related`. The spec's examples show backlinks on both sides.
- `run new <task>` backlinks the run id into the task's `related`.
- `run finish` stamps a `finished:` timestamp as an extension field, in
  addition to the optional `outcome`.
- `unblock` clears `blocked_by` entirely as well as setting status open.
- `t9x ready` auto-transitions blocked tasks whose blockers are all
  done/wontdo back to open (the spec explicitly permits this).
- `run new` without a task id is allowed, for untethered exploration.
- YAML comments inside front matter are not preserved byte-for-byte;
  fields, values, and insertion order are.
