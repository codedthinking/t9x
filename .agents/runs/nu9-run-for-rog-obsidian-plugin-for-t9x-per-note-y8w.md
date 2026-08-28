---
id: nu9
type: run
created: 2026-08-28T22:28:26+02:00
related: [rog]
outcome: success
finished: 2026-08-28T22:29:38+02:00
---
# Run for rog: Obsidian plugin for t9x (per note y8w)

## Symlink approach dead; pivot to Hidden Folders Access (2026-08-28)
- User confirmed: after a full Obsidian restart, `_agents` still not in
  the explorer. Obsidian resolves symlinks to real paths, so a symlink
  into a dot folder is never indexed. Symlink trick unrecoverable.
- User chose "invert the symlink" from the options, then asked to check
  prior art first. Found dsebastien/obsidian-hidden-folders-access:
  monkey-patches the vault adapter (listRecursiveChild, reconcileFile)
  to inject whitelisted hidden folders into the live index — explorer,
  search, editing, metadata cache, Bases, watchers; disk paths stay
  `.agents/...`; no restart needed. Strictly dominates inversion (no
  repo-layout change, no symlink sync risk), so adopted; inversion is
  the documented fallback if HFA breaks on an Obsidian update.
- Plugin 0.1.2: no more symlink bootstrap (removes stale pre-0.1.2
  symlink), Base targets `.agents/tasks`, all `_agents` path translation
  dropped, bootstrap notices if hidden-folders-access is not enabled.
- 6/6 tests, build clean; released 0.1.2.
