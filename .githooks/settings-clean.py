#!/usr/bin/env python3
"""Git clean filter: drop the "model" key that /model writes into settings.json."""
import json
import sys

raw = sys.stdin.read()
try:
    data = json.loads(raw)
    data.pop("model", None)
    sys.stdout.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
except ValueError:
    sys.stdout.write(raw)
