#!/usr/bin/env bash
# Notification hook: surface Claude Code prompts as desktop notifications.

msg=$(python3 -c \
    'import json,sys;print(json.load(sys.stdin).get("message","Claude Code needs attention"))' \
    2>/dev/null || echo "Claude Code needs attention")

command -v notify-send >/dev/null 2>&1 && notify-send -a "Claude Code" "Claude Code" "$msg"
exit 0
