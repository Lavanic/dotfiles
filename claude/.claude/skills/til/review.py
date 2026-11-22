#!/usr/bin/env python3
"""Accept/reject/note review of a short list of items in a small WezTerm window.

  review.py ITEMS.json            open the window, block until done, print result
  review.py ITEMS.json --resume   keep waiting on a window that is still open
  review.py --tui ITEMS.json OUT  the UI itself (runs inside the window)

ITEMS.json: {"title": str, "items": [{"id": str, "label": str, "flag": str?,
             "fields": [{"name": str?, "text": str}]}]}
Result:     {"status": "submitted|aborted|closed|pending|error",
             "results": [{"id": str, "decision": "accept|reject|note", "note": str}]}

Colors are the terminal's ANSI slots, so the UI follows the otop palette.
"""

import curses
import json
import locale
import os
import subprocess
import sys
import textwrap
import time

WAIT_SECONDS = 570
EXIT_NO_WEZTERM = 3

TEAL, GREEN, RED, YELLOW, MAGENTA, GREY, WHITE, TEXT = range(1, 9)
DECISION_COLOR = {"accept": GREEN, "reject": RED, "note": YELLOW, None: GREY}


def write_json(path, data):
    tmp = f"{path}.tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


class Review:
    def __init__(self, scr, spec):
        self.scr = scr
        self.title = spec.get("title", "review")
        self.items = spec["items"]
        self.decisions = [None] * len(self.items)
        self.notes = [""] * len(self.items)
        self.cur = 0
        self.message = ""

    def put(self, y, x, s, attr=0):
        h, w = self.scr.getmaxyx()
        if y < 0 or y >= h or x >= w - 1:
            return
        try:
            self.scr.addstr(y, x, s[: w - 1 - x], attr)
        except curses.error:
            pass

    def color(self, n, extra=0):
        return curses.color_pair(n) | extra

    def undecided(self):
        return sum(d is None for d in self.decisions)

    def draw(self):
        scr = self.scr
        scr.erase()
        h, w = scr.getmaxyx()
        width = max(20, min(w - 2, 80))
        inner = width - 4
        x0 = 1

        self.put(0, x0, self.title, self.color(MAGENTA, curses.A_BOLD))
        count = f"{self.cur + 1}/{len(self.items)}"
        px = x0 + width - len(count) - 2 * len(self.items) - 1
        for i, d in enumerate(self.decisions):
            attr = self.color(DECISION_COLOR[d])
            if i == self.cur:
                attr |= curses.A_BOLD | curses.A_UNDERLINE
            self.put(0, px + 2 * i, "●" if d else "○", attr)
        self.put(0, x0 + width - len(count), count, self.color(GREY))

        item = self.items[self.cur]
        decision = self.decisions[self.cur]
        border = self.color(DECISION_COLOR[decision] if decision else TEAL)

        y = 2
        label = f" {item.get('label', '')} "
        self.put(y, x0, "╭─" + "─" * (width - 3) + "╮", border)
        self.put(y, x0 + 2, label, self.color(YELLOW, curses.A_BOLD))
        flag = item.get("flag")
        if flag:
            self.put(y, x0 + width - len(flag) - 4, f" {flag} ", self.color(MAGENTA))
        y += 1

        lines = []
        for n, field in enumerate(item["fields"]):
            if n:
                lines.append(("", 0))
            if field.get("name"):
                lines.append((field["name"].upper(), self.color(TEAL)))
            for para in str(field["text"]).split("\n"):
                wrapped = textwrap.wrap(para, inner) or [""]
                lines += [(ln, self.color(WHITE)) for ln in wrapped]

        room = max(1, h - y - 7)
        if len(lines) > room:
            lines = lines[: room - 1] + [("…", self.color(GREY))]
        for text, attr in lines:
            self.put(y, x0, "│", border)
            self.put(y, x0 + 2, text, attr)
            self.put(y, x0 + width - 1, "│", border)
            y += 1
        self.put(y, x0, "╰" + "─" * (width - 2) + "╯", border)
        y += 1

        if decision == "accept":
            self.put(y, x0 + 1, "accepted", self.color(GREEN))
        elif decision == "reject":
            self.put(y, x0 + 1, "rejected", self.color(RED))
        elif decision == "note":
            self.put(y, x0 + 1, "retry: ", self.color(YELLOW, curses.A_BOLD))
            self.put(y, x0 + 8, self.notes[self.cur], self.color(YELLOW))
        else:
            self.put(y, x0 + 1, "undecided", self.color(GREY))
        self.note_row = y + 1

        ready = self.undecided() == 0
        keys = [("a", "accept", GREEN), ("r", "reject", RED), ("n", "note", YELLOW),
                ("u", "undo", TEXT), ("←→", "move", TEXT),
                ("⏎", "submit", GREEN if ready else GREY), ("q", "quit", TEXT)]
        rows, x = [[]], 0
        for key in keys:
            size = len(key[0]) + len(key[1]) + 3
            if x + size > w - 3 and rows[-1]:
                rows.append([])
                x = 0
            rows[-1].append(key)
            x += size
        fy = h - 1 - len(rows)
        if self.message:
            self.put(fy - 1, x0 + 1, self.message, self.color(RED))
        for n, row in enumerate(rows):
            x = x0 + 1
            for key, name, col in row:
                dim = col == GREY
                self.put(fy + n, x, key, self.color(GREY if dim else col, curses.A_BOLD))
                x += len(key) + 1
                self.put(fy + n, x, name, self.color(GREY if dim else TEXT))
                x += len(name) + 2
        scr.refresh()

    def advance(self):
        n = len(self.items)
        for step in range(1, n + 1):
            i = (self.cur + step) % n
            if self.decisions[i] is None:
                self.cur = i
                return

    def read_line(self, prompt, initial=""):
        buf = list(initial)
        curses.curs_set(1)
        try:
            while True:
                self.draw()
                h, w = self.scr.getmaxyx()
                y = min(self.note_row, h - 3)
                room = max(1, w - len(prompt) - 5)
                shown = "".join(buf)[-room:]
                self.put(y, 2, " " * (w - 4))
                self.put(y, 2, prompt, self.color(YELLOW, curses.A_BOLD))
                self.put(y, 2 + len(prompt), shown, self.color(WHITE))
                self.scr.refresh()
                try:
                    ch = self.scr.get_wch()
                except curses.error:
                    continue
                if ch in ("\n", "\r") or ch == curses.KEY_ENTER:
                    return "".join(buf).strip()
                if ch == "\x1b":
                    return None
                if ch in ("\x7f", "\b") or ch == curses.KEY_BACKSPACE:
                    if buf:
                        buf.pop()
                elif ch == "\x15":
                    buf.clear()
                elif isinstance(ch, str) and ch.isprintable():
                    buf.append(ch)
        finally:
            curses.curs_set(0)

    def confirm(self, question):
        self.message = f"{question} (y/n)"
        self.draw()
        self.message = ""
        while True:
            try:
                ch = self.scr.get_wch()
            except curses.error:
                continue
            if ch in ("y", "Y"):
                return True
            if ch in ("n", "N", "\x1b", "q"):
                return False

    def result(self, status):
        return {
            "status": status,
            "results": [
                {"id": it["id"], "decision": d, "note": n if d == "note" else ""}
                for it, d, n in zip(self.items, self.decisions, self.notes)
            ],
        }

    def run(self):
        while True:
            self.draw()
            self.message = ""
            try:
                ch = self.scr.get_wch()
            except curses.error:
                continue
            if ch == "a":
                self.decisions[self.cur] = "accept"
                self.advance()
            elif ch == "r":
                self.decisions[self.cur] = "reject"
                self.advance()
            elif ch == "n":
                note = self.read_line("note › ", self.notes[self.cur])
                if note:
                    self.notes[self.cur] = note
                    self.decisions[self.cur] = "note"
                    self.advance()
            elif ch == "u":
                self.decisions[self.cur] = None
            elif ch in ("h", "k") or ch in (curses.KEY_LEFT, curses.KEY_UP):
                self.cur = (self.cur - 1) % len(self.items)
            elif ch in ("l", "j", "\t") or ch in (curses.KEY_RIGHT, curses.KEY_DOWN):
                self.cur = (self.cur + 1) % len(self.items)
            elif ch in ("\n", "\r") or ch == curses.KEY_ENTER:
                left = self.undecided()
                if left == 0:
                    return self.result("submitted")
                self.message = f"{left} undecided"
                self.advance()
            elif ch == "q":
                if all(d is None for d in self.decisions) or self.confirm("quit without submitting?"):
                    return self.result("aborted")


def tui(items_path, out_path):
    locale.setlocale(locale.LC_ALL, "")
    os.environ.setdefault("ESCDELAY", "25")
    with open(items_path) as f:
        spec = json.load(f)

    def main(scr):
        curses.curs_set(0)
        curses.use_default_colors()
        bright = curses.COLORS >= 16
        slots = {TEAL: 6, GREEN: 2, RED: 1, YELLOW: 3, MAGENTA: 5,
                 GREY: 8 if bright else 7, WHITE: 15 if bright else 7, TEXT: 7}
        for pair, slot in slots.items():
            curses.init_pair(pair, slot, -1)
        scr.keypad(True)
        return Review(scr, spec).run()

    sys.stdout.write(f"\033]2;{spec.get('title', 'review')}\007")
    sys.stdout.flush()
    try:
        result = curses.wrapper(main)
    except KeyboardInterrupt:
        result = {"status": "aborted", "results": []}
    except Exception as e:
        result = {"status": "error", "error": repr(e), "results": []}
    write_json(out_path, result)


def panes():
    out = subprocess.run(["wezterm", "cli", "list", "--format", "json"],
                         capture_output=True, text=True, timeout=10).stdout
    return {str(p.get("pane_id")): p for p in json.loads(out)}


def pane_alive(pane_id):
    try:
        return str(pane_id) in panes()
    except Exception:
        return True


def launch(items_path, resume):
    items_path = os.path.abspath(items_path)
    out_path = items_path + ".result"
    pane_file = items_path + ".pane"

    if not resume:
        with open(items_path) as f:
            spec = json.load(f)
        if not spec.get("items"):
            print(json.dumps({"status": "submitted", "results": []}))
            return 0
        if os.path.exists(out_path):
            os.remove(out_path)
        try:
            spawn = subprocess.run(
                ["wezterm", "cli", "spawn", "--new-window", "--cwd", os.path.dirname(items_path),
                 "--", sys.executable, os.path.abspath(__file__), "--tui", items_path, out_path],
                capture_output=True, text=True, timeout=20)
            problem = spawn.stderr.strip() if spawn.returncode else ""
        except (OSError, subprocess.TimeoutExpired) as e:
            problem = str(e)
        if problem:
            print(json.dumps({"status": "error", "error": f"could not open a WezTerm window: {problem}"}))
            return EXIT_NO_WEZTERM
        with open(pane_file, "w") as f:
            f.write(spawn.stdout.strip())

    try:
        with open(pane_file) as f:
            pane_id = f.read().strip()
    except FileNotFoundError:
        print(json.dumps({"status": "error", "error": "no review in progress"}))
        return 1

    deadline = time.monotonic() + WAIT_SECONDS
    while time.monotonic() < deadline:
        if os.path.exists(out_path):
            with open(out_path) as f:
                print(f.read())
            return 0
        if not pane_alive(pane_id):
            time.sleep(0.3)
            if os.path.exists(out_path):
                continue
            print(json.dumps({"status": "closed", "results": []}))
            return 0
        time.sleep(0.4)
    print(json.dumps({"status": "pending", "results": []}))
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "--tui":
        tui(args[1], args[2])
    elif args and args[0] != "--tui":
        sys.exit(launch(args[0], "--resume" in args[1:]))
    else:
        sys.exit(__doc__)
