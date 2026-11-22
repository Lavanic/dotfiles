#!/usr/bin/env python3
"""Read Claude Code session history for /til.

  sweep.py REPO                       conversation text since the last mark (or midnight)
  sweep.py REPO --mark                record now as the last sweep
  sweep.py REPO --flags               list open ^word flags
  sweep.py REPO --flags-done TERM...  these flags were pitched and accepted
  sweep.py REPO --flags-rejected TERM...  these were pitched and rejected

A flag is a word or phrase Oliver prefixes with ^ while talking (^erroneously,
^"certificate pinning") to say "make this a TIL later". A flag stays open
until a pitch for it is accepted, or rejected twice. Flagging the same word
again after that reopens it.

State lives in REPO/.git so it never shows up as a change.
"""

import datetime as dt
import glob
import json
import os
import re
import sys

BUDGET = 80_000
MAX_AGE = dt.timedelta(days=3)
FLAG_AGE = dt.timedelta(days=90)
REJECTIONS_TO_CLOSE = 2

NOISE = re.compile(
    r"<(system-reminder|local-command-caveat|local-command-stdout|command-name|"
    r"command-message|command-args)>.*?</\1>", re.S)
NOT_TYPED = re.compile(
    r"<pasted_content.*?</pasted_content[^>]*>|<bash-(input|stdout|stderr)>.*?</bash-\1>|"
    r"```.*?```|`[^`\n]*`", re.S)
FLAG = re.compile(r'''(?<![\w^\\])\^(?:"([^"\n]{2,60})"|([A-Za-z][A-Za-z'-]{1,40}))''')


def transcripts(newer_than):
    for path in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
        try:
            if os.path.getmtime(path) >= newer_than.timestamp():
                yield path
        except OSError:
            continue


def spoken(entry):
    """Text of a real user or assistant turn, or '' for anything synthetic."""
    if entry.get("type") not in ("user", "assistant"):
        return ""
    if entry.get("isSidechain") or entry.get("isMeta") or entry.get("isCompactSummary"):
        return ""
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        parts = [content]
    elif isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    else:
        parts = []
    return NOISE.sub("", "\n".join(parts)).strip()


def timestamp(entry):
    try:
        return dt.datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
    except (KeyError, ValueError, AttributeError):
        return None


def write_atomic(path, content):
    tmp = f"{path}.tmp"
    with open(tmp, "w") as f:
        f.write(content)
    os.replace(tmp, path)


def clean_term(term):
    term = re.sub(r"'s$", "", term.strip()).strip("'-")
    return " ".join(term.split())


def flag_state_path(repo):
    return os.path.join(repo, ".git", "til-flags.json")


def load_flag_state(repo):
    state = {"done": {}, "rejections": {}}
    try:
        with open(flag_state_path(repo)) as f:
            loaded = json.load(f)
        if isinstance(loaded.get("done"), dict) and isinstance(loaded.get("rejections"), dict):
            state = {"done": loaded["done"], "rejections": loaded["rejections"]}
    except (OSError, ValueError, AttributeError):
        pass
    return state


def closed_at(state, term):
    try:
        return dt.datetime.fromisoformat(state["done"][term])
    except (KeyError, ValueError):
        return None


def find_flags(repo):
    """Open flags grouped by term: {term_lower: {"term", "uses": [...], "rejections"}}."""
    state = load_flag_state(repo)
    start = dt.datetime.now(dt.timezone.utc) - FLAG_AGE
    flags = {}
    for path in transcripts(start):
        last_claude = None
        with open(path, errors="replace") as f:
            for line in f:
                is_user = '"type":"user"' in line
                if not is_user and '"type":"assistant"' not in line:
                    continue
                if not is_user:
                    last_claude = line
                    continue
                if "^" not in line:
                    continue
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                typed = NOT_TYPED.sub(" ", spoken(entry))
                when = timestamp(entry)
                if not typed or when is None or when < start:
                    continue
                for m in FLAG.finditer(typed):
                    term = clean_term(m.group(1) or m.group(2))
                    closed = closed_at(state, term.lower())
                    if len(term) < 2 or (closed and when <= closed):
                        continue
                    before = ""
                    if last_claude:
                        try:
                            before = spoken(json.loads(last_claude))
                        except ValueError:
                            pass
                    slot = flags.setdefault(term.lower(), {
                        "term": term, "uses": [],
                        "rejections": state["rejections"].get(term.lower(), 0)})
                    slot["uses"].append({"when": when, "said": " ".join(typed.split())[:400],
                                         "claude_before": " ".join(before.split())[:300]})
    return flags


def cmd_flags(repo):
    flags = find_flags(repo)
    if not flags:
        print("No open flags.")
        return
    for slot in sorted(flags.values(), key=lambda s: s["uses"][0]["when"]):
        again = "  (rejected once already: pitch a different reading)" if slot["rejections"] else ""
        print(f"- ^{slot['term']}{again}")
        for use in sorted(slot["uses"], key=lambda u: u["when"])[-2:]:
            print(f"    {use['when'].astimezone():%b %d %H:%M} he said: {use['said']}")
            if use["claude_before"]:
                print(f"      Claude just before: {use['claude_before']}")


def cmd_close(repo, terms, rejected):
    state = load_flag_state(repo)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    for raw in terms:
        term = clean_term(raw.lstrip("^")).lower()
        if not term:
            continue
        if rejected:
            count = state["rejections"].get(term, 0) + 1
            state["rejections"][term] = count
            if count < REJECTIONS_TO_CLOSE:
                continue
        state["done"][term] = now
        state["rejections"].pop(term, None)
    write_atomic(flag_state_path(repo), json.dumps(state, indent=1))
    print(f"open flags left: {len(find_flags(repo))}")


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


def collect(start):
    sessions = []
    for path in transcripts(start):
        turns, cwd = [], ""
        with open(path, errors="replace") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                text = spoken(entry)
                when = timestamp(entry)
                if not text or when is None or when < start:
                    continue
                cwd = entry.get("cwd") or cwd
                turns.append((when, entry["type"], text))
        if turns:
            sessions.append((turns[0][0], cwd, turns))
    return sorted(sessions, key=lambda s: s[0])


def render(sessions, cap):
    out = []
    for _, cwd, turns in sessions:
        out.append(f"\n## session in {cwd}")
        for when, role, text in turns:
            if len(text) > cap:
                text = text[:cap] + " [...]"
            who = "USER" if role == "user" else "CLAUDE"
            out.append(f"[{when.astimezone():%H:%M}] {who}: {text}")
    return "\n".join(out)


def cmd_sweep(repo):
    start = since(repo)
    sessions = collect(start)
    print(f"# sessions since {start.astimezone():%a %b %d %H:%M}: {len(sessions)}")
    body = ""
    for cap in (2000, 1000, 500, 250):
        body = render(sessions, cap)
        if len(body) <= BUDGET:
            break
    if len(body) > BUDGET:
        print("[older turns dropped to fit]")
        body = body[-BUDGET:]
    print(body)


def main():
    if len(sys.argv) < 2 or not os.path.isdir(os.path.join(sys.argv[1], ".git")):
        sys.exit(__doc__)
    repo, args = sys.argv[1], sys.argv[2:]
    if args[:1] == ["--flags"]:
        cmd_flags(repo)
    elif args[:1] == ["--flags-done"]:
        cmd_close(repo, args[1:], rejected=False)
    elif args[:1] == ["--flags-rejected"]:
        cmd_close(repo, args[1:], rejected=True)
    elif args[:1] == ["--mark"]:
        write_atomic(mark_path(repo), dt.datetime.now(dt.timezone.utc).isoformat())
    elif not args:
        cmd_sweep(repo)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
