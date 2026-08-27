---
id: c1x
type: task
status: done
created: 2026-08-27
related: [dqb]
blocked_by: []
---
# Write descriptive filenames: <id>-<slug>.md
`t9x task new` (and `note new`, `run new`, ...) should write
`<id>-<slug>.md` instead of `<id>.md`, slugifying the title. Rationale:
humans get an overview from plain `ls .agents/tasks/` without the CLI.
The spec already allows this — filenames are free, only `id:` in front
matter is canonical — so this is purely a default-naming change. Also
rename the existing task files to the new pattern.
