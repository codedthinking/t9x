# t9x Obsidian plugin

Thin desktop-only UI over the `t9x` CLI (design: `.agents/notes/2026-08-28-plan-t9x-obsidian-plugin.md`).
All logic stays in the CLI and the delegated agents; the plugin locates,
spawns, and displays.

## Install

Via BRAT (recommended — auto-updates): install the BRAT community
plugin, then *Add beta plugin* with repo `codedthinking/t9x`. BRAT reads
`manifest.json`/`main.js` from the GitHub release assets, so the monorepo
layout doesn't matter.

Releasing a new version: bump `version` in `manifest.json`, build, then

```sh
gh release create <version> manifest.json main.js --title <version>
```

The tag must equal the manifest version (bare `x.y.z`, no `v` prefix).
Constraint: BRAT picks the highest-semver release in the repo — if the
t9x CLI ever starts cutting its own GitHub releases, either attach the
plugin assets to those too or move plugin versions to `x.y.z-obsidian.N`
prerelease tags.

Local alternative:

```sh
./install.sh /path/to/vault    # builds if needed, copies manifest.json + main.js
```

Enable **t9x** under Settings → Community plugins. On load, in any vault
whose root contains `.agents/`, the plugin creates:

- `_agents -> .agents` symlink (Obsidian does not index dot-folders;
  the symlink makes the t9x workspace first-class vault content), and
- `t9x-tasks.base` — a Bases table over `_agents/tasks/` for review.

Add `_agents`, `t9x-tasks.base`, and `.obsidian/` to the repo's
`.gitignore`.

## Commands (bind hotkeys in Settings → Hotkeys)

- **Pick up task at cursor** — the one shortcut. Locates the `@(word ...)`
  marker enclosing the cursor (paren-matched, nesting-aware), saves the
  file, and spawns the default agent with instructions to extract it per
  the manuscript-tasks skill and execute the resulting task(s). The agent
  rewrites the marker to `@id` anchors; Obsidian reloads the file.
- **New task** — title modal → `t9x task new`, opens the created file.
- **Close / Reopen task** — uses the active file's `id:` frontmatter.
- **Promote active note** — `t9x promote` into a path you name.
- **Demote active note** — moves the file into `_agents/notes/`.
- **Delegate a task** — pick an open task, pick an agent, spawn headless.
- **Open task review** — opens `t9x-tasks.base`.

Delegated agents run detached with stdout/stderr appended to
`.agents/runs/<task-or-timestamp>-<agent>.log`; the real record is the run
the agent itself opens per using-t9x. A notice fires on spawn and exit.

## Settings

- **t9x binary**, **PATH prepend** — GUI apps don't inherit your shell
  PATH; defaults cover homebrew, `~/.local/bin`, `~/.bun/bin`.
- **Agents** — JSON table of argv templates with `{{PROMPT}}`. Defaults
  verified 2026-08-28: `claude -p --permission-mode acceptEdits`,
  `pi -p`, `omp -p`, `hermes -z`; `opencode run` is unverified (not
  installed on this machine).
- **Pickup / Delegate prompts** — templates with `{{FILE}}`, `{{LINE}}`,
  `{{MARKER}}`, `{{ID}}`.

## Development

```sh
npm install
npm test      # marker-matching unit tests (node --test)
npm run build # tsc --noEmit + esbuild -> main.js
```
