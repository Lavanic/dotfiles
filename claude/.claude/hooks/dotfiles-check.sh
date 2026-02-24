#!/usr/bin/env bash
# SessionStart/Stop hook: nudge a dotfiles sync when ~/dotfiles is dirty.
# Usage: dotfiles-check.sh session|stop   (hook JSON arrives on stdin)

REPO="$HOME/dotfiles"
mode="${1:-session}"
input=$(cat)

[ -d "$REPO/.git" ] || exit 0

# Don't loop: if this Stop was already continued by this hook, stay quiet.
if [ "$mode" = stop ]; then
    active=$(printf '%s' "$input" | python3 -c \
        'import json,sys;print(json.load(sys.stdin).get("stop_hook_active",False))' \
        2>/dev/null || echo False)
    [ "$active" = "True" ] && exit 0
fi

status=$(git -C "$REPO" status --porcelain 2>/dev/null) || exit 0
[ -z "$status" ] && exit 0

files=$(printf '%s\n' "$status" | head -20 | cut -c4- | tr '\n' ' ')
msg="~/dotfiles has uncommitted changes: ${files}- Use the dotfiles-sync skill: stage explicit paths, one conventional commit per logical change, push to origin main. If the changes are intentionally unfinished, say so to the user and stop."

if [ "$mode" = stop ]; then
    python3 -c 'import json,sys;print(json.dumps({"decision":"block","reason":sys.argv[1]}))' "$msg"
else
    python3 -c 'import json,sys;print(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":sys.argv[1]}}))' "$msg"
fi
exit 0
