#!/bin/sh
# Interim installer until `t9x plugin install obsidian` exists (task 2is).
# Usage: ./install.sh /path/to/vault
set -e
cd "$(dirname "$0")"
VAULT="${1:?usage: install.sh /path/to/vault}"
[ -d "$VAULT" ] || { echo "no such vault: $VAULT" >&2; exit 1; }
[ -f main.js ] || { npm install --no-fund --no-audit; npm run build; }
mkdir -p "$VAULT/.obsidian/plugins/t9x"
cp manifest.json main.js "$VAULT/.obsidian/plugins/t9x/"
echo "Installed. Enable 't9x' under Settings > Community plugins."
echo "On first load the plugin creates the _agents symlink and t9x-tasks.base."
