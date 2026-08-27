# Mission log

Prototype of the t9x CLI built from `docs/spec.md`.

## Real

- `t9x init` — scaffold `.agents/{tasks,notes,runs,scripts,skills}`
- `t9x task new/list/show`, `close`, `wontdo`, `reopen`, `block`, `unblock`,
  `relate` — full transition table from the spec, enforced
- `t9x ready` — open tasks; blocked tasks whose blockers are all done/wontdo
  are auto-transitioned back to open (spec allows this)
- `t9x run new [task] / show / finish [--outcome]` — run-task backlinks via
  `related` on both sides
- `t9x note new/list/show` — dated slug filenames, id is canonical
- `t9x skill list/show/add/rm` — SKILL.md convention, recursive discovery
- `t9x show <id>` — resolves any id recursively, including runs stored as
  directories with a README.md
- `t9x promote src dst` — `git mv` when in a repo, plain move otherwise
- Unknown YAML front matter fields survive round trips (tested)
- base36 id generation with namespace-wide collision check and widening

## Interpretation choices (not in the spec, chosen for the prototype)

- `relate` links symmetrically (adds each id to the other's `related`)
- `run finish` stamps a `finished:` timestamp (extension field) in addition
  to the optional `outcome`
- `unblock` clears `blocked_by` as well as setting status open
- `run new` without a task id is allowed (untethered exploration)

## Faked / out of scope

- No manuscript extraction layer (`@qx3` anchors) — spec marks it out of scope
- No harness integration for skill execution — spec marks it out of scope
- YAML comments and exact quoting inside front matter are not preserved
  byte-for-byte; fields, values, and order are

## Next

- `t9x task new --capabilities` passthrough for workflow metadata
- shell completion
