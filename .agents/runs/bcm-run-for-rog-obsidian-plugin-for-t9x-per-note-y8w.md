---
id: bcm
type: run
created: 2026-08-28T21:52:52+02:00
related: [rog]
outcome: success
finished: 2026-08-28T21:55:52+02:00
---
# Run for rog: Obsidian plugin for t9x (per note y8w)

## Environment findings (2026-08-28)
- node v24.18.0, npm 11.16.0 available.
- Headless invocations verified from `--help` on this machine:
  - claude: `claude -p <prompt>` (add `--permission-mode acceptEdits` so
    delegated edits do not hang on approval)
  - pi: `pi -p <prompt>`
  - omp: `omp -p <prompt>`
  - hermes: `hermes -z <prompt>`
  - opencode: NOT INSTALLED here; default kept as `opencode run <prompt>`,
    editable in plugin settings.
- t9x at ~/.local/bin, claude at /opt/homebrew/bin, omp at ~/.bun/bin —
  none on the default GUI-app PATH, so the plugin prepends a configurable
  PATH (default: /opt/homebrew/bin, /usr/local/bin, ~/.local/bin,
  ~/.bun/bin) to spawned-process env.

## Decisions during implementation
- Plugin self-bootstraps on load: creates `_agents -> .agents` symlink and
  a `t9x-tasks.base` Bases file in the vault root if `.agents/` exists.
  Keeps install to "copy manifest.json + main.js".
- Interim install is `integrations/obsidian/install.sh <vault>` until the
  2is `t9x plugin install` machinery exists.
- Marker paren-matching lives in `src/marker.js` (plain JS, pure function)
  with a `node --test` check — the only non-trivial logic in the plugin.
- Agent table, prompts, paths all live in plugin settings as data.
- claude default includes `--permission-mode acceptEdits` so delegated
  work does not hang on edit approval prompts.

## Result
- `integrations/obsidian/`: manifest.json, src/main.ts (~380 lines),
  src/marker.js + marker.test.mjs, esbuild config, install.sh, README.
- `npm test`: 6/6 marker tests pass. `npm run build`: tsc clean, main.js
  16.3kb.
- NOT yet exercised inside a live Obsidian vault — install with
  `integrations/obsidian/install.sh <vault>` and verify: symlink
  creation, Bases table rendering, pickup spawn, Notice on agent exit.
  rog stays open until that runtime check passes.
