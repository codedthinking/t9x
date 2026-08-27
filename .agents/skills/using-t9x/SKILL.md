---
name: using-t9x
description: >
  Work inside a t9x workspace: record tasks, runs, and notes under .agents/
  instead of scattering provisional material through the project. Use whenever
  a repository contains a .agents/ directory, and whenever you are about to
  write a TODO list, progress log, experiment record, or scratch script.
---

# Using t9x

t9x separates the human-curated project from your provisional working state.
Everything you produce while working — intentions, attempts, interpretations,
scratch code — goes under `.agents/` as plain files. The human workspace
(`src/`, `docs/`, `paper/`, ...) is only touched when explicitly asked, or via
promotion.

The five kinds, by the question they answer:

| kind   | question                        | where                      |
|--------|---------------------------------|----------------------------|
| task   | what should be done?            | `.agents/tasks/<id>.md`    |
| run    | what did we try?                | `.agents/runs/`            |
| note   | what do we currently think?     | `.agents/notes/`           |
| script | what code did the agent write?  | `.agents/scripts/`         |
| skill  | what reusable method exists?    | `.agents/skills/<name>/`   |

Files are the interface. You may always read and edit them directly with
normal tools; the CLI is convenience. IDs (`qx3`) are canonical and unique
across all of `.agents/`; filenames may be renamed freely.

## The working loop

```sh
t9x ready                  # what is actionable now
t9x show qx3               # read the task
t9x run new qx3            # open a run record BEFORE experimenting
# ... work; append findings to the run file as you go ...
t9x run finish f2m --outcome inconclusive
t9x note new 'What we learned' --related qx3 f2m   # only if durable
t9x close qx3
```

Rules of thumb:

- One run per attempt or session. Write results into the run file while
  working, not from memory afterwards. `finish` means the record is complete,
  not that it succeeded.
- A note is for interpretations that outlive the run that produced them. If
  it only restates what happened, it belongs in the run.
- Scratch code goes in `.agents/scripts/` with no metadata; reference it from
  runs by path.
- New work you discover mid-task: `t9x task new '...'`, optionally
  `--origin file:line` pointing at where it came from, then keep going.

## State changes go through verbs

Never edit `status:` by hand. Use the semantic verbs so transitions stay
valid:

```sh
t9x close qx3      # open|blocked -> done
t9x wontdo qx3     # open|blocked -> wontdo (deliberate rejection; keep it)
t9x reopen qx3     # done|wontdo -> open
t9x block qx3 1v2  # qx3 waits on 1v2
t9x unblock qx3
t9x relate qx3 f2m # symmetric weak link
```

Do not delete done or wontdo tasks — they are project history. Obsolete
notes, runs, and scripts may simply be deleted; Git is the archive.

## Editing front matter

When you edit an object's file directly, preserve every YAML field you do not
understand (`capabilities:`, `manuscript:`, ...). Extension fields are part
of the format. Keep `id:` untouched, always.

## Crossing into the human workspace

When provisional material is accepted as real project content:

```sh
t9x promote .agents/notes/2026-08-27-identification.md docs/identification.md
```

Promote only when asked or when the human workspace clearly calls for it;
promotion is an editorial act, not a tidy-up.
