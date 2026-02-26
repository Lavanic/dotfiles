#!/usr/bin/env bash
# Notification hook: quiet desktop ping when Claude needs input.

cat > /dev/null
command -v notify-send >/dev/null 2>&1 && notify-send "ready whenever you are"
exit 0
