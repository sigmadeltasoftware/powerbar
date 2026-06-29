#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude"

if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is required but not found."
    exit 1
fi

mkdir -p "$DEST"
cp "$SCRIPT_DIR/powerbar.py" "$DEST/powerbar.py"
chmod +x "$DEST/powerbar.py"

# pbrun: wrap long builds/verifies to publish live [N/M] progress to the status line.
cp "$SCRIPT_DIR/pbrun.py" "$DEST/pbrun.py"
chmod +x "$DEST/pbrun.py"

python3 -c "
import json, os
path = os.path.expanduser('~/.claude/settings.json')
try:
    with open(path) as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}
config['statusLine'] = {'type': 'command', 'command': 'python3 ~/.claude/powerbar.py'}
with open(path, 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')
"

echo "Installed powerbar.py + pbrun.py to $DEST/"
echo "Updated $DEST/settings.json with statusLine config."
echo "Restart Claude Code to activate."
echo "Tip: wrap long runs to see live progress, e.g.:"
echo "  python3 ~/.claude/pbrun.py --label 'verify' -- synapse verify-proofs --flow X --jobs 6"
