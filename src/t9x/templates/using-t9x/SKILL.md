---
name: using-t9x
description: >
  Work inside a t9x workspace: record tasks, runs, and notes under .agents/
  instead of scattering provisional material through the project. Use whenever
  a repository contains a .agents/ directory, and whenever you are about to
  write a TODO list, progress log, experiment record, or scratch script.
---

# Using t9x

t9x separates the human-curated project from provisional agent work. Put intentions, attempts, interpretations, and scratch code under `.agents/`. Touch the human workspace only when explicitly asked or through an import or promotion command.

The workspace contains five kinds of material:

| Kind | Question | Location |
| --- | --- | --- |
| Task | What should be done? | `.agents/tasks/` |
| Run | What did we try? | `.agents/runs/` |
| Note | What do we currently think? | `.agents/notes/` |
| Script | What code did the agent write? | `.agents/scripts/` |
| Skill | What reusable method exists? | `.agents/skills/` |

Files are the interface. You may read and edit them with ordinary file tools. IDs such as `qx3` are canonical and unique across `.agents/`; filenames may change.

## Working loop

```sh
t9x ready
t9x show qx3
t9x run new qx3
# Record work in the run file as it happens.
t9x run finish f2m --outcome inconclusive
t9x note new 'What we learned' --related qx3 f2m
t9x close qx3
```

Use one run per attempt or session. A note is for an interpretation that outlives the run. Put scratch code in `.agents/scripts/` and reference it from the run. Record newly discovered work with `t9x task new '...'`.

## State transitions

Never edit `status:` by hand. Use the semantic commands:

```sh
t9x close qx3
t9x wontdo qx3
t9x reopen qx3
t9x block qx3 1v2
t9x unblock qx3
t9x relate qx3 f2m
```

Do not delete completed or rejected tasks. They are project history. Preserve all unknown YAML front matter fields when editing objects directly, and never change an object's `id:`.

## Moving notes across the workspace boundary

Import an existing Markdown document into the agent workspace:

```sh
t9x note import docs/identification.md --title 'Identification' --move
```

Promote accepted agent material into the human workspace:

```sh
t9x promote .agents/notes/2026-08-27-identification.md docs/identification.md
```

Use `--move` or promotion only when the user wants the source removed. Both commands preserve the source if the destination cannot be committed.
