---
id: 5n0
type: task
status: done
created: 2026-09-15
related: [oma]
blocked_by: []
---
# Implement agent setup and safe note transfers

## Goal

Make `t9x init` install opt-in integrations for Codex, Claude Code, OpenCode, OMP, Pi, and Hermes. Add safe note movement in both directions and make permission failures concise and non-destructive.

## Plan

1. Add tests for interactive, non-interactive, idempotent, and conflicting agent setup.
2. Bundle the `using-t9x` skill and install only the files owned by each selected integration.
3. Add `t9x note import`, then make import and promotion preserve their sources on failure.
4. Add atomic single-file and transactional multi-object writes with rollback.
5. Update the specification, README, and installed skill, then run the full suite and CLI smoke tests.

## Todo

- [x] Add agent-aware `t9x init`.
- [x] Add two-way safe note movement.
- [x] Add atomic writes and permission diagnostics.
- [x] Update documentation and bundled skill.
- [x] Verify the installed package and full test suite.
