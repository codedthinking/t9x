---
name: manuscript-tasks
description: >
  Extract embedded work instructions from manuscripts, papers, reports, or
  source files into t9x tasks, leaving a short @id anchor behind. Use when a
  human-authored document contains inline requests for writing, derivation,
  literature search, empirical analysis, or editing — especially explicit
  `@(word ...)` markers.
---

# Manuscript task extraction

Human-authored documents accumulate inline instructions: "cite the 2019
survey here", "derive the variance bound", "redo this figure with the new
sample". These are tasks. Move them into `.agents/tasks/` so they can be
tracked, blocked, and closed, while the manuscript keeps only a short stable
anchor.

## Explicit markers

Authors may mark instructions explicitly as `@(word description)`:

```markdown
@(write add a paragraph on the key mechanism @(model verify the proposition))
```

- `@(` is the unresolved form of the `@id` anchor: extraction replaces the
  whole marker with `@<id>`.
- The first word is an **open vocabulary, not a registry**. Record it
  verbatim as `capabilities: [word]` on the task. Never reject an unknown
  word — interpret it. `write`, `model`, `literature`, `empirics`, `edit`
  are conventions; `@(prove ...)` or `@(hungarian ...)` are equally valid
  and mean what an intelligent reader would take them to mean.
- Markers nest. Extract the innermost first, keep its `@id` referenced in
  the outer task's body, block the outer on the inner
  (`t9x block <outer> <inner>`), and leave only the outermost anchor in
  the document.
- Find markers by searching for `@(`.

Unmarked instructions ("cite the 2019 survey here") are extracted the same
way; the marker only removes the judgment call of spotting them.

## Procedure

1. Find the embedded instruction. Note its file and line.
2. Create the task, recording where it came from:

   ```sh
   t9x task new 'Derive the variance bound for section 4' \
     --origin paper/model.tex:417
   ```

   This prints the new id, e.g. `qx3`.
3. Replace the instruction text in the manuscript with the anchor `@qx3`
   (as a comment if the document format would render it: `% @qx3` in TeX,
   `<!-- @qx3 -->` in markdown).
4. Put the full instruction text into the task body, and add capability
   metadata if the workflow uses it:

   ```yaml
   capabilities: [math, writing]
   ```

5. When the task is done, resolve the anchor: replace `@qx3` with the
   produced text (or delete it), then `t9x close qx3`.

## Rules

- One task per instruction; do not batch unrelated asks into one task.
- `origin.line` is a locator, not an identifier — the anchor in the text is
  what survives editing. Re-find the anchor by searching for `@<id>`.
- The anchor must be the task's real id, never an invented one.
- Do not rewrite surrounding manuscript prose while extracting; extraction
  is mechanical, the work happens later under the task.
