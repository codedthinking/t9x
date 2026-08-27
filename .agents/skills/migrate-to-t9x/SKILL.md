---
name: migrate-to-t9x
description: >
  Convert an existing project into a t9x workspace: sweep GitHub issues, TODO
  files, inline TODO/FIXME comments, scattered notes, experiment logs, and
  loose scripts into .agents/ as tasks, notes, runs, and scripts. Use when a
  project adopts t9x and its work state lives somewhere else — an issue
  tracker, markdown files, code comments — or nowhere in particular.
---

# Migrating an existing project to t9x

Existing projects keep their work state scattered: an issue tracker, a
`TODO.md`, `FIXME` comments, half-finished notes in `docs/`, scripts in
`scratch/`. Migration sweeps all of it into `.agents/` so that `t9x ready`
becomes the single answer to "what is there to do here?".

You will not know in advance where everything is. That is expected. Work in
three phases — discover, map, execute — and get human sign-off between them.

## The contract

These boundaries hold for the entire migration, whatever it takes:

- **Read anything, write only inside `.agents/`** until the cleanup step.
- **Destroy nothing without sign-off.** Originals (issue text, TODO files,
  comments) stay in place until the human approves the inventory and the
  cleanup plan. Migration copies; cleanup, separately approved, removes.
- **The tracker is closed out only behind the t9x object.** During the sweep,
  do not close, edit, label, or comment on GitHub issues. Once the human
  approves cleanup, each migrated issue is closed as a duplicate of its t9x
  object — never before that object exists, because the closing comment must
  cite the real id.
- **Every migrated object records where it came from** — `origin:` for files
  (`file`, `line`), an extension field for trackers
  (`github: {issue: 42}`).
- **Do not invent.** No status a source doesn't support, no paraphrase where
  the original wording fits, no completion you cannot verify.

## Phase 1 — Discover

Sweep the usual hiding places; the project will have others, so browse, do
not just pattern-match:

- the issue tracker: GitHub issues (open and closed), PR checklists
- work files: `TODO*`, `NOTES*`, `ROADMAP*`, `BACKLOG*`, `CHANGELOG` "next"
  sections, `AGENTS.md`/`CLAUDE.md` task lists
- inline markers: `rg -n 'TODO|FIXME|XXX|HACK' --hidden`
- prose knowledge: `docs/`, `journal/`, lab notebooks, meeting notes,
  long-form comments explaining why something is the way it is
- activity records: experiment logs, benchmark results, tuning diaries
- loose code: `scratch/`, `sandbox/`, `tmp/`, one-off scripts not imported
  by anything

Write the findings into a single inventory note
(`t9x note new 'Migration inventory'`): every candidate item, its source
location, and the kind you propose (task / note / run / script / skip).
Items you cannot classify go in an explicit **Unsorted** section — do not
force them. Show the inventory to the human and stop until they approve.

## Phase 2 — Map

Default rules, adjusted by whatever the human said about the inventory:

| source                              | becomes | details |
|-------------------------------------|---------|---------|
| open issue                          | task, `status: open` | title from issue title; full body dumped into the task body; `github: {issue: N}` |
| closed issue                        | task, `done` (or `wontdo` if rejected) | migrate only when the decision matters as history; otherwise skip — Git and the tracker already remember |
| issue labels                        | `capabilities: [...]` extension field | verbatim, lowercased |
| "blocked by #12" in an issue        | `blocked_by: [<id of #12>]` | second pass, after all issues have ids |
| issue cross-references              | `related:` | second pass |
| TODO/FIXME comment                  | task with `origin: {file, line}` | keep the comment for now; cleanup may replace it with `@id` (see manuscript-tasks) |
| TODO.md / BACKLOG.md line items     | one task each | never one task per file |
| prose knowledge, design rationale   | note | date the filename from `git log --follow --format=%as -- <file> \| tail -1`, not from today |
| experiment/benchmark log            | run, with `outcome:` when the log states one, `finished:` when it is clearly over | |
| loose script still worth having     | copy to `.agents/scripts/` | promotion in reverse; original removed only at cleanup |

Preserve original wording in bodies; add your own reading, if needed, under
a separate heading. When task-vs-note is genuinely unclear, prefer note — a
note can spawn tasks later, but a task wrongly implies someone must act.

## Phase 3 — Execute and clean up

1. Create objects with the CLI (`t9x task new`, `t9x note new`, ...), then
   fill bodies by editing the files. Wire `related:`/`blocked_by:` in the
   second pass.
2. Commit the sweep as one commit: everything added under `.agents/`,
   nothing else touched.
3. Propose cleanup as its own step: which files to delete, which comments to
   replace with `@id` anchors, and the list of migrated issues to close.
   Execute only what the human approves, as a separate commit.

## Closing migrated issues

Only after the t9x object exists and cleanup is approved. For each migrated
issue, in this order:

1. Comment on the issue, citing the object that supersedes it:

   > Migrated to t9x task `qx3` (`.agents/tasks/qx3.md` in this repository).
   > Further discussion and status live there.
   > About the t9x format: T9X_URL

2. Close the issue as **duplicate** (on GitHub: close as "not planned",
   which is how duplicates are closed there; apply the `duplicate` label if
   the repo uses one).

Every such comment carries the same short reference to the t9x format so
readers landing on a closed issue know what `.agents/` is. `T9X_URL` is a
placeholder — the format documentation will live under the t9x repository at
a URL not yet fixed; update this file and reuse the real link once it
exists.

A finished migration means: `t9x ready` lists the real open work, the
inventory note records what was swept and what was deliberately skipped, and
nothing was lost — every original is either still in place or reachable
through Git history.
