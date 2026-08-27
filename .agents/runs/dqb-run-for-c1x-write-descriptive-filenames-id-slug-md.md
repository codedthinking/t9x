---
id: dqb
type: run
created: 2026-08-27T13:41:54+02:00
related: [c1x]
outcome: success
finished: 2026-08-27T13:43:59+02:00
---
# Run for c1x: Write descriptive filenames: <id>-<slug>.md
## What was done
- Moved `slugify` from `notes.py` to `workspace.py` (shared, with a 60-char
  cap) and used it in `tasks.new` and `runs.new`: new files are now
  `<id>-<slug>.md`.
- Notes keep their `<date>-<slug>.md` pattern — already human-readable, and
  the spec's date-prefix rationale still holds. The id-uniqueness means the
  note collision counter could go too, but that is a separate cleanup.
- Updated `docs/spec.md` (filename rationale, task filename example,
  directory-structure example) and the path assertion in `tests/test_cli.py`.
- Renamed all existing task and run files with
  `.agents/scripts/rename_to_slugs.py` (git mv, driven by t9x's own scan
  and slugify).
## Result
13/13 tests pass; `t9x ready` and `t9x show` resolve ids as before, since
resolution reads front matter, not filenames.
