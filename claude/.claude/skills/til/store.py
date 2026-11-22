#!/usr/bin/env python3
"""Everything /til writes: the til repo and Anki.

  store.py state               what is saved, rejected and queued (for the skill)
  store.py save FILE [--dry]   save approved TILs, remember rejected ones, commit, push
  store.py cards FILE [--dry]  queue approved cards, then flush
  store.py flush               send queued cards to Anki, commit, push, sync

save FILE:  {"accepted": [{"category": str, "text": str}], "rejected": [same]}
cards FILE: {"cards": [{"category": str, "front": str, "back": str,
                        "example": str?, "origin": str?}]}

Every step is safe to repeat: saved TILs and queued cards are checked against
what is already in the repo, and a card only counts as done once its Anki note
id is written to cards.jsonl.
"""

import datetime as dt
import fcntl
import glob
import html
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = os.environ.get("TIL_REPO", "/home/oliverohrt/Documents/PROJECTS/til")
ANKI_URL = os.environ.get("TIL_ANKI_URL", "http://127.0.0.1:3141/")
BRANCH = "main"
VOCAB = "Vocabulary"
VOCAB_MODEL = "Basic Quizlet Extended"


def norm(text):
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def one_line(text):
    return " ".join(str(text).split())


def write_atomic(path, content):
    tmp = f"{path}.tmp"
    with open(tmp, "w") as f:
        f.write(content)
    os.replace(tmp, path)


def git(*args, timeout=30):
    try:
        p = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        return 124, "timed out"


def fail(message):
    print(json.dumps({"ok": False, "error": message}, indent=1))
    sys.exit(1)


def check_repo():
    if not os.path.isdir(os.path.join(REPO, ".git")):
        fail(f"{REPO} is not a git repo")
    code, branch = git("symbolic-ref", "--short", "HEAD")
    if code != 0 or branch != BRANCH:
        fail(f"til repo is on '{branch}', expected '{BRANCH}'")
    for marker in ("rebase-merge", "rebase-apply", "MERGE_HEAD"):
        if os.path.exists(os.path.join(REPO, ".git", marker)):
            fail("til repo has a rebase or merge in progress; finish it first")


def pull():
    """Bring in commits from other machines. Offline is fine; a conflict is not."""
    code, _ = git("fetch", "-q", "origin", timeout=20)
    if code != 0:
        return "offline"
    if git("rev-parse", "-q", "--verify", f"origin/{BRANCH}")[0] != 0:
        return "ok"
    if git("rev-parse", "-q", "--verify", "HEAD")[0] != 0:
        code, out = git("reset", "-q", "--mixed", f"origin/{BRANCH}")
    else:
        code, out = git("rebase", "--autostash", f"origin/{BRANCH}")
    if code != 0:
        git("rebase", "--abort")
        fail(f"could not rebase the til repo onto origin/{BRANCH}: {out[-300:]}")
    return "ok"


def push():
    code, out = git("push", "-u", "origin", BRANCH, timeout=45)
    if code == 0:
        return True, ""
    if "rejected" in out or "fetch first" in out:
        if pull() == "ok":
            code, out = git("push", "-u", "origin", BRANCH, timeout=45)
            if code == 0:
                return True, ""
    lines = [ln for ln in out.splitlines() if ln.startswith(("fatal", "error", " ! "))]
    return False, (lines or out.splitlines() or ["push failed"])[0]


def commit(paths, message):
    git("add", "--", *paths)
    if git("diff", "--cached", "--quiet")[0] == 0:
        return None
    code, out = git("commit", "-q", "-m", message)
    if code != 0:
        git("reset", "-q", "--", *paths)
        fail(f"commit failed: {out[-300:]}")
    return git("rev-parse", "--short", "HEAD")[1]


def unpushed():
    code, out = git("rev-list", "--count", f"origin/{BRANCH}..HEAD")
    return int(out) if code == 0 and out.isdigit() else 0


def saved_tils():
    tils = []
    for path in sorted(glob.glob(os.path.join(REPO, "[0-9]*", "[0-9]*", "*.md"))):
        date = os.path.basename(path)[:-3]
        with open(path) as f:
            for para in f.read().split("\n\n"):
                para = one_line(para)
                if not para or para.startswith("#") or ": " not in para:
                    continue
                category, text = para.split(": ", 1)
                tils.append({"date": date, "category": category, "text": text})
    return tils


def categories():
    try:
        with open(os.path.join(REPO, "categories.md")) as f:
            return [ln[2:].strip() for ln in f if ln.startswith("- ")]
    except OSError:
        return []


def canonical(category, known):
    category = one_line(category).replace(":", " ").strip() or "Misc"
    for k in known:
        if norm(k) == norm(category):
            return k
    return category.title() if category.islower() else category


def rejected_path():
    return os.path.join(REPO, ".git", "til-rejected.jsonl")


def read_jsonl(path):
    rows = []
    try:
        with open(path) as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    except OSError:
        pass
    except ValueError as e:
        fail(f"{path} has a line that is not valid JSON ({e}); fix it by hand first")
    return rows


def dump_jsonl(rows):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def is_duplicate(text, existing):
    n = norm(text)
    for other in existing:
        o = norm(other)
        if n == o:
            return other
    return None


def cmd_state():
    tils = saved_tils()
    print("Categories:", ", ".join(categories()) or "(none yet)")
    print(f"\nSaved TILs: {len(tils)} total. Most recent:")
    for t in tils[-40:]:
        print(f"- {t['date']} {t['category']}: {t['text'][:150]}")
    rejected = read_jsonl(rejected_path())
    if rejected:
        print("\nRejected before (do not pitch again):")
        for r in rejected[-20:]:
            print(f"- {r['category']}: {r['text'][:150]}")
    cards = read_jsonl(os.path.join(REPO, "cards.jsonl"))
    queued = sum(c.get("note_id") is None for c in cards)
    print(f"\nCards: {len(cards)} total, {queued} waiting for Anki")
    if os.path.isdir(os.path.join(REPO, ".git")) and unpushed():
        print(f"Unpushed commits in the til repo: {unpushed()}")


def cmd_save(path, dry):
    spec = load_spec(path, "accepted")
    synced = "skipped" if dry else pull()

    known = categories()
    existing = [t["text"] for t in saved_tils()]
    saved, skipped = [], []
    for item in spec.get("accepted", []):
        text = one_line(item.get("text", ""))
        category = canonical(item.get("category", ""), known)
        if not text:
            continue
        twin = is_duplicate(text, existing)
        if twin:
            skipped.append({"text": text, "already_saved": twin})
            continue
        existing.append(text)
        if category not in known:
            known.append(category)
        saved.append({"category": category, "text": text})

    today = dt.date.today()
    rel = f"{today:%Y/%m/%Y-%m-%d}.md"
    day_path = os.path.join(REPO, rel)
    block = "\n\n".join(f"{s['category']}: {s['text']}" for s in saved)
    names = ", ".join(dict.fromkeys(s["category"].lower() for s in saved))
    message = f"chore: add {names} TILs"
    result = {"ok": True, "dry": dry, "file": rel, "saved": saved, "skipped_duplicates": skipped,
              "commit_message": message if saved else None, "remote": synced}

    if dry or not saved:
        if not dry:
            remember_rejected(spec.get("rejected", []))
        if not saved:
            result["note"] = "nothing new to save"
        print(json.dumps(result, indent=1, ensure_ascii=False))
        return

    os.makedirs(os.path.dirname(day_path), exist_ok=True)
    if os.path.exists(day_path):
        with open(day_path) as f:
            content = f.read().rstrip("\n") + "\n\n" + block + "\n"
    else:
        content = f"# {today:%A, %b} {today.day} {today.year}\n\n{block}\n"
    write_atomic(day_path, content)
    write_atomic(os.path.join(REPO, "categories.md"),
                 "".join(f"- {c}\n" for c in sorted(known, key=str.lower)))
    remember_rejected(spec.get("rejected", []))

    result["commit"] = commit([rel, "categories.md"], message)
    result["pushed"], result["push_error"] = push()
    if not result["pushed"]:
        result["note"] = "committed locally; the next run pushes it"
    print(json.dumps(result, indent=1, ensure_ascii=False))


def remember_rejected(items):
    if not items:
        return
    rows = read_jsonl(rejected_path())
    seen = {norm(r["text"]) for r in rows}
    for item in items:
        text = one_line(item.get("text", ""))
        if text and norm(text) not in seen:
            rows.append({"date": dt.date.today().isoformat(),
                         "category": one_line(item.get("category", "")), "text": text})
    write_atomic(rejected_path(), dump_jsonl(rows[-300:]))


class AnkiDown(Exception):
    pass


def anki_rpc(method, params, timeout=20):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(ANKI_URL, body, {
        "Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
    except (urllib.error.URLError, OSError) as e:
        raise AnkiDown(str(e))
    for line in raw.splitlines():
        if line.startswith("data:"):
            raw = line[5:]
            break
    return json.loads(raw)


def anki(tool, **arguments):
    reply = anki_rpc("tools/call", {"name": tool, "arguments": arguments})
    result = reply.get("result") or {}
    text = (result.get("content") or [{}])[0].get("text", "")
    if "error" in reply or result.get("isError"):
        raise RuntimeError(text or json.dumps(reply.get("error")))
    if result.get("structuredContent") is not None:
        return result["structuredContent"]
    return json.loads(text)


def anki_up():
    try:
        anki_rpc("ping", {}, timeout=3)
        return True
    except AnkiDown:
        return False
    except Exception:
        return True


def ensure_anki():
    """Returns (reachable, process we started or None, problem)."""
    if anki_up():
        return True, None, ""
    running = subprocess.run(["pgrep", "-x", "anki"], capture_output=True).returncode == 0
    proc = None
    if not running:
        if not shutil.which("anki"):
            return False, None, "anki is not installed"
        proc = subprocess.Popen(["anki"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, start_new_session=True)
    deadline = time.monotonic() + (60 if proc else 15)
    while time.monotonic() < deadline:
        if anki_up():
            time.sleep(1.5)
            return True, proc, ""
        if proc and proc.poll() is not None:
            return False, None, "Anki exited right after starting"
        time.sleep(1)
    why = ("Anki did not finish starting (profile picker or a dialog may be open)" if proc
           else "Anki is open but its MCP add-on is not answering on " + ANKI_URL)
    return False, proc, why


def close_anki(proc):
    """Ask an Anki we started to quit the normal way (it saves and syncs on
    exit like a click on the close button). Never touches one he opened."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=90)
        return True
    except (OSError, subprocess.TimeoutExpired):
        return False


def rich(text):
    return html.escape(one_line(text), quote=False)


def italics(text):
    return re.sub(r"\*([^*]+)\*", r"<i>\1</i>", rich(text))


def note_for(card):
    if card["deck"] == f"TIL::{VOCAB}" or card.get("example") or card.get("origin"):
        back = rich(card["back"])
        if card.get("example"):
            back += f"<br><br><i>{rich(card['example'])}</i>"
        if card.get("origin"):
            back += f"<br><br>{italics(card['origin'])}"
        return VOCAB_MODEL, {"FrontText": rich(card["front"]), "BackText": back}
    return "Basic", {"Front": rich(card["front"]), "Back": rich(card["back"])}


def existing_note_ids(deck):
    found, offset = {}, 0
    while True:
        page = anki("find_notes", query=f'"deck:{deck}"', limit=500, offset=offset,
                    include_first_field=True)
        for label in page.get("noteLabels", []):
            plain = html.unescape(re.sub(r"<[^>]+>", "", label.get("firstField", "")))
            found[norm(plain)] = label["noteId"]
        if not page.get("hasMore"):
            return found
        offset += 500


def sync_anki():
    try:
        job = anki("sync")
        deadline = time.monotonic() + 45
        while job.get("status") == "running" and time.monotonic() < deadline:
            time.sleep(1.5)
            job = anki("sync", job_id=job["job_id"])
        status = job.get("status")
        if status == "conflict":
            anki("sync", job_id=job["job_id"], resolve="cancel")
            return "conflict: AnkiWeb wants a full one-way sync; resolve it in Anki"
        if status == "error":
            err = job.get("error") or {}
            return f"error: {err.get('hint') or err.get('message') or err.get('code')}"
        if status == "success":
            return f"ok ({(job.get('result') or {}).get('outcome', 'done')})"
        return str(status)
    except Exception as e:
        return f"error: {e}"


def flush(cards):
    """Send cards without a note id to Anki. Mutates cards; returns a report."""
    pending = [c for c in cards if c.get("note_id") is None]
    report = {"added": 0, "linked_existing": 0, "still_queued": len(pending), "errors": []}
    if not pending:
        return report
    up, proc, why = ensure_anki()
    report["anki_started"] = proc is not None
    if not up:
        report["errors"].append(why)
        if proc:
            report["anki_closed"] = close_anki(proc)
        return report

    by_deck = {}
    for card in pending:
        by_deck.setdefault(card["deck"], []).append(card)
    for deck, group in by_deck.items():
        try:
            anki("create_deck", deck_name=deck)
            known = existing_note_ids(deck)
            fresh = []
            for card in group:
                note_id = known.get(norm(card["front"]))
                if note_id:
                    card["note_id"] = note_id
                    report["linked_existing"] += 1
                else:
                    fresh.append(card)
            by_model = {}
            for card in fresh:
                model, fields = note_for(card)
                by_model.setdefault(model, []).append((card, fields))
            for model, pairs in by_model.items():
                names = anki("model_field_names", model_name=model).get("field_names", [])
                reply = anki("add_notes", deck_name=deck, model_name=model, tags=["til"],
                             notes=[{"fields": {**dict.fromkeys(names, ""), **fields}}
                                    for _, fields in pairs])
                for entry in reply.get("results", []):
                    card = pairs[entry["index"]][0]
                    if entry.get("status") == "created" and entry.get("note_id"):
                        card["note_id"] = entry["note_id"]
                        report["added"] += 1
                    else:
                        reason = entry.get("error") or entry.get("reason") or entry.get("status")
                        report["errors"].append(f"{card['front'][:50]}: {reason}")
        except AnkiDown as e:
            report["errors"].append(f"lost the connection to Anki: {e}")
            break
        except Exception as e:
            report["errors"].append(f"{deck}: {e}")
    report["still_queued"] = sum(c.get("note_id") is None for c in cards)
    if report["added"]:
        report["sync"] = sync_anki()
    if proc:
        report["anki_closed"] = close_anki(proc)
    return report


def cmd_cards(path, dry):
    cards_path = os.path.join(REPO, "cards.jsonl")
    new, skipped = [], []
    if path:
        spec = load_spec(path, "cards")
        if not dry:
            pull()
        cards = read_jsonl(cards_path)
        seen = {(c["deck"], norm(c["front"])) for c in cards}
        known = categories()
        for item in spec.get("cards", []):
            deck = f"TIL::{canonical(item.get('category', ''), known)}"
            front, back = one_line(item.get("front", "")), one_line(item.get("back", ""))
            if not front or not back:
                continue
            if (deck, norm(front)) in seen:
                skipped.append(front)
                continue
            seen.add((deck, norm(front)))
            card = {"date": dt.date.today().isoformat(), "deck": deck, "front": front, "back": back}
            for extra in ("example", "origin"):
                if item.get(extra):
                    card[extra] = one_line(item[extra])
            card["note_id"] = None
            new.append(card)
        cards += new
    else:
        pull()
        cards = read_jsonl(cards_path)

    result = {"ok": True, "dry": dry, "queued": new, "skipped_duplicates": skipped}
    if dry:
        result["would_send_to_anki"] = [c["front"] for c in cards if c.get("note_id") is None]
        print(json.dumps(result, indent=1, ensure_ascii=False))
        return

    before = dump_jsonl(read_jsonl(cards_path))
    if new:
        write_atomic(cards_path, dump_jsonl(cards))
    result["anki"] = flush(cards)
    if dump_jsonl(cards) != before:
        write_atomic(cards_path, dump_jsonl(cards))
        names = ", ".join(dict.fromkeys(c["deck"].split("::", 1)[1].lower() for c in new))
        message = f"chore: add cards for {names}" if new else "chore: record anki note ids"
        result["commit"] = commit(["cards.jsonl"], message)
    if unpushed() or result.get("commit"):
        result["pushed"], result["push_error"] = push()
    print(json.dumps(result, indent=1, ensure_ascii=False))


def load_spec(path, key):
    try:
        with open(path) as f:
            spec = json.load(f)
    except (OSError, ValueError) as e:
        fail(f"cannot read {path}: {e}")
    if not isinstance(spec, dict) or not isinstance(spec.get(key, []), list):
        fail(f'{path} must be an object with a "{key}" list')
    for name in (key, "rejected"):
        for item in spec.get(name, []):
            if not isinstance(item, dict):
                fail(f"{path}: every entry in {name} must be an object")
    return spec


def locked(run):
    """One writer at a time, so two /til runs cannot interleave git or cards.jsonl."""
    check_repo()
    with open(os.path.join(REPO, ".git", "til.lock"), "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fail("another /til run is writing to the til repo; try again in a moment")
        run()


def main():
    args = [a for a in sys.argv[1:] if a != "--dry"]
    dry = "--dry" in sys.argv[1:]
    if args == ["state"]:
        cmd_state()
    elif len(args) == 2 and args[0] == "save":
        locked(lambda: cmd_save(args[1], dry))
    elif len(args) == 2 and args[0] == "cards":
        locked(lambda: cmd_cards(args[1], dry))
    elif args == ["flush"]:
        locked(lambda: cmd_cards(None, False))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
