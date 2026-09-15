---
id: oma
type: run
created: 2026-09-15T22:58:02+02:00
related: [5n0]
outcome: success
finished: 2026-09-15T23:16:06+02:00
---
# Implement t9x initialization and transfer safety

## Implemented

- Added opt-in setup for Codex, Claude Code, OpenCode, OMP, Pi, and Hermes.
- Added `t9x note import` with copy and rollback-safe move behavior.
- Made object replacement atomic and grouped run backlinks, relationships, and automatic unblocking into rollback-capable transactions.
- Made permission failures concise at the CLI boundary.
- Restricted promotion to regular files so cross-filesystem directory copies cannot leave partial destinations.

## Verification so far

- Initialization tests: 5 passed.
- Transfer tests: 3 passed.
- Permission and transaction tests: 4 passed.

## Final verification

- `uv run pytest`: 24 passed.
- Installed-wheel round trip: initialized all six integrations, imported a note with `--move`, and promoted it back to the human workspace.
- Read-only `.agents/notes`: exited 1 with a concise diagnostic and no traceback.
- Installed-wheel Codex profile: allowed `.agents/notes` writes and denied writes to `.git` and `.codex`.
