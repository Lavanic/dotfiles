#!/usr/bin/env python3
"""Claude Code statusline: dir, git branch, model, context %, session cost."""
import json
import os
import subprocess
import sys


def paint(hexcolor, text):
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (0, 2, 4))
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


def context_pct(path, model_id):
    if not path or not os.path.isfile(path):
        return None
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            f.seek(max(0, size - 2_000_000))
            lines = f.read().decode("utf-8", "ignore").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        usage = (entry.get("message") or {}).get("usage") if isinstance(entry, dict) else None
        if usage and usage.get("input_tokens") is not None:
            used = sum(usage.get(k) or 0 for k in (
                "input_tokens", "cache_read_input_tokens",
                "cache_creation_input_tokens", "output_tokens"))
            window = 1_000_000 if "[1m]" in model_id else 200_000
            return min(100.0, used * 100.0 / window)
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}
    workspace = data.get("workspace") or {}
    cwd = workspace.get("current_dir") or os.getcwd()
    model = data.get("model") or {}
    cost = data.get("cost") or {}

    parts = [paint("f0c050", os.path.basename(cwd.rstrip("/")) or "/")]

    try:
        branch = subprocess.run(
            ["git", "-C", cwd, "branch", "--show-current"],
            capture_output=True, text=True, timeout=2).stdout.strip()
        if branch:
            parts.append(paint("4897d4", f" {branch}"))
    except (OSError, subprocess.SubprocessError):
        pass

    parts.append(paint("5f8787", model.get("display_name") or "?"))

    pct = context_pct(data.get("transcript_path"), model.get("id") or "")
    if pct is not None:
        color = "50f095" if pct < 50 else "f0c050" if pct < 80 else "f05050"
        parts.append(paint(color, f"ctx {pct:.0f}%"))

    usd = cost.get("total_cost_usd")
    duration_ms = cost.get("total_duration_ms") or 0
    if isinstance(usd, (int, float)) and usd > 0:
        label = f"${usd:.2f}"
        if duration_ms > 60_000:
            label += f" (${usd / (duration_ms / 3_600_000):.2f}/h)"
        parts.append(paint("bcbcbc", label))

    sep = " " + paint("555555", "·") + " "
    print(sep.join(parts))


if __name__ == "__main__":
    main()
