---
id: ru1
type: run
created: 2026-08-28T21:58:54+02:00
related: [rog]
outcome: success
finished: 2026-08-28T21:59:28+02:00
---
# Run for rog: Obsidian plugin for t9x (per note y8w)

## BRAT distribution (2026-08-28)
- Verified from the BRAT developer guide: BRAT fetches manifest.json and
  main.js from GitHub *release assets only* — repo layout (monorepo
  subdir) is irrelevant; release tag, release name, and manifest version
  must all match; private repos work via fine-grained PAT.
- Pushed main (fcd494b..4632e4a) and created release `0.1.0` on
  codedthinking/t9x with manifest.json + main.js attached:
  https://github.com/codedthinking/t9x/releases/tag/0.1.0
- Install path: BRAT "Add beta plugin" -> codedthinking/t9x.
- Known ceiling: BRAT installs the highest-semver release in the repo.
  Fine while the plugin is the only release train; if the CLI starts
  cutting GitHub releases, attach plugin assets to those or switch the
  plugin to x.y.z-obsidian.N prerelease tags. Documented in the README.
- install.sh kept as the local no-GitHub alternative.
