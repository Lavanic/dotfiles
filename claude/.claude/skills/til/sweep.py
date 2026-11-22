#!/usr/bin/env python3
"""Print what was said in Claude Code sessions since the last sweep.

  sweep.py REPO          conversation text since the last mark (or midnight)
  sweep.py REPO --mark   record now as the last sweep

The mark lives in REPO/.git so it never shows up as a change.
"""

import datetime as dt
import glob
import json
import os
import re
import sys

BUDGET = 80_000
MAX_AGE = dt.timedelta(days=3)
NOISE = re.compile(
    r"<(system-reminder|local-command-caveat|local-command-stdout|command-name|"
    r"command-message|command-args)>.*?</\1>", re.S)


def mark_path(repo):
    return os.path.join(repo, ".git", "til-last-sweep")


def since(repo):
    now = dt.datetime.now(dt.timezone.utc)
    midnight = dt.datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        with open(mark_path(repo)) as f:
            last = dt.datetime.fromisoformat(f.read().strip())
        return max(last, now - MAX_AGE)
    except (OSError, ValueError):
        return midnight


def text_of(entry):
    content = entry.get("message", {}).get("content")
    if isinstance(content, str):
        parts = [content]
    elif isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    else:
        parts = []
    return NOISE.sub("", "\n".join(parts)).strip()


def collect(start):
    sessions = []
    for path in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
        if os.path.getmtime(path) < start.timestamp():
            continue
        turns, cwd = [], ""
        with open(path, errors="replace") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("type") not in ("user", "assistant") or e.get("isSidechain") or e.get("isMeta"):
                    continue
                try:
                    ts = dt.datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
                except (KeyError, ValueError):
                    continue
                if ts < start:
                    continue
                text = text_of(e)
                if text:
                    cwd = e.get("cwd") or cwd
                    turns.append((ts, e["type"], text))
        if turns:
            sessions.append((turns[0][0], cwd, turns))
    return sorted(sessions, key=lambda s: s[0])


def render(sessions, cap):
    out = []
    for _, cwd, turns in sessions:
        out.append(f"\n## session in {cwd}")
        for ts, role, text in turns:
            if len(text) > cap:
                text = text[:cap] + " [...]"
            who = "USER" if role == "user" else "CLAUDE"
            out.append(f"[{ts.astimezone():%H:%M}] {who}: {text}")
    return "\n".join(out)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    repo = sys.argv[1]
    if "--mark" in sys.argv[2:]:
        with open(mark_path(repo), "w") as f:
            f.write(dt.datetime.now(dt.timezone.utc).isoformat())
        return
    start = since(repo)
    sessions = collect(start)
    print(f"# sessions since {start.astimezone():%a %b %d %H:%M}: {len(sessions)}")
    for cap in (2000, 1000, 500, 250):
        body = render(sessions, cap)
        if len(body) <= BUDGET:
            break
    print(body[:BUDGET])


if __name__ == "__main__":
    main()
