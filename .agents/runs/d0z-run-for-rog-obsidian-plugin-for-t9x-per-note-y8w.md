---
id: d0z
type: run
created: 2026-08-28T22:07:10+02:00
related: [rog]
outcome: success
finished: 2026-08-28T22:07:50+02:00
---
# Run for rog: Obsidian plugin for t9x (per note y8w)

## Bug: "no open tasks" in choo-siow-calvo (2026-08-28)
- First real-vault test (~/Tresorit/Mac/projects/plan/choo-siow-calvo,
  installed via BRAT). Symlink was created, 26 tasks all `status: open`
  with valid ids — data fine.
- Root cause: the delegate picker queried Obsidian's vault index, but
  Obsidian does not index a symlinked folder that appears while it is
  running; `_agents` was created at 22:04 with Obsidian open, so the
  index had no task files.
- Fix (0.1.1): delegate() now lists `.agents/tasks/*.md` via fs and
  regex-reads id/status from frontmatter — delegation no longer depends
  on the index at all. Bootstrap now shows a "restart Obsidian to index
  _agents" notice when it creates the symlink (the review Base and
  in-editor task browsing still need the index).
- 6/6 tests, build clean; released 0.1.1 for BRAT auto-update.
