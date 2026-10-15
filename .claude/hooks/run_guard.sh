#!/bin/sh
# Fail-closed launcher for the guard hook (registered in .claude/settings.json).
# Runs guard_dangerous_commands.py with the first working Python 3.8+ interpreter, passing stdin through.
# Exit code 2 blocks the tool call in Claude Code, whatever the hook's onFailure setting.

# Parameter expansion only, so it works even when PATH has no external tools.
# Handles POSIX paths and the backslash paths Claude Code passes on Windows.
case "$0" in
  */*) hook_dir=${0%/*} ;;
  *\\*) hook_dir=${0%\\*} ;;
  *) hook_dir=. ;;
esac

for interpreter in python3 python py; do
  if command -v "$interpreter" >/dev/null 2>&1 \
    && "$interpreter" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' </dev/null >/dev/null 2>&1; then
    exec "$interpreter" "$hook_dir/guard_dangerous_commands.py"
  fi
done

echo "guard hook: no working Python 3.8+ interpreter found (tried python3, python, py). Command blocked." >&2
exit 2
