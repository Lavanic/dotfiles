---
name: til
description: Pitch TILs (today-I-learned notes) from everything since the last run, review them in a small WezTerm window, commit and push the approved ones to the private til repo, then turn them into Anki cards. Use when the user runs /til or /tils, or asks to capture what they learned.
argument-hint: "[dry]"
---

# til

Oliver keeps a paper journal of TILs for retention. This skill pitches TILs
from work done with Claude, lets him accept, reject or annotate each one in a
TUI, saves the approved ones, and makes Anki cards from them. He then writes
them on paper in his own words, so the saved text is a draft he approved, not
the final word.

Arguments: `$ARGUMENTS`

Three scripts in `~/.claude/skills/til/` do all the reading and writing.
Never edit the til repo, run git in it, or call Anki tools by hand; the
scripts are what make a repeated run safe.

- `review.py FILE`: the review window.
- `store.py save FILE` / `store.py cards FILE` / `store.py flush`: the til
  repo (`/home/oliverohrt/Documents/PROJECTS/til`, private) and Anki.
- `sweep.py REPO`: text of today's Claude Code sessions, and the `^word`
  flags he planted.

There is one mode: every run covers everything since the last run, in every
session. He runs it whenever he likes, often several times a day, so a run
with one TIL, or none, is normal. Ignore a `day` argument; it is an old name
for what is now the default.

If the arguments include `dry`, this is a rehearsal: do the gather, pitch and
both review rounds for real, pass `--dry` to `store.py save` and
`store.py cards`, skip `sweep.py --mark` and the flag commands, and show
what each would have written.

## Current state

!`python3 ~/.claude/skills/til/store.py state 2>&1`

## 1. Gather

Three sources, every run:

1. The sweep. In a fresh `mktemp -d` directory (reuse it for this run's
   other files), run
   `python3 ~/.claude/skills/til/sweep.py /home/oliverohrt/Documents/PROJECTS/til > <dir>/sweep.txt`
   and Read the file. It holds every Claude Code session since the last run
   (or since midnight if there was none, three days back at most).
2. This conversation. The sweep reads history from disk and can miss the
   last turn or two, so also use what you can see here. If /til already ran
   in this conversation, only what came after that run.
3. Flags. Run
   `python3 ~/.claude/skills/til/sweep.py /home/oliverohrt/Documents/PROJECTS/til --flags`.
   A flag is a word or phrase he prefixed with `^` while talking
   (`^erroneously`, `^ping`, `^"certificate pinning"`) to say "I want this
   as a TIL". The output lists each open flag with what he said and what
   Claude had just said, from every session of the last 90 days on this
   machine.

The sweep is raw history: it can contain passwords, emails and other
people's details. Read it, never quote it back, and keep all of that out of
pitches.

Every open flag gets a pitch, built from that context: a flagged English
word becomes a Vocabulary TIL, a flagged command or topic becomes a TIL
about how it came up. A flag written as a question, like `^whatisscaleway`,
`^whatsdkms` or `^definefairplay`, means "explain this": strip the
`whatis`/`whats`/`define` prefix to get the real topic (`scaleway`, `dkms`,
`fairplay`) and pitch a TIL explaining it from the surrounding context, not
a card titled "whatisscaleway". Fix his spelling of the word in the pitch,
but pass the exact term `--flags` printed (`whatisscaleway` and all) to the
flag commands in step 4. If the context is not enough to tell what he meant,
pitch your best reading; the review is where he corrects it. A flag marked "rejected once already" needs a different
reading than last time. Put `"flag": "flagged"` on these items so he can see
which pitches came from a flag.

## 2. Pitch

There is no fixed number. Pitch every flag, plus whatever else clears the
bar below, and nothing that does not.

The bar is what he engaged with, not what Claude said. Good sources, best
first:

1. Flags.
2. A moment where he was surprised or had something wrong ("wait, Mbps is
   not megabytes?").
3. A question he asked and the plain answer to it.
4. A command he typed himself, or a word he used or asked about.

Not sources: things Claude diagnosed, fixed or mentioned in passing while he
was focused on something else. If he never reacted to it, he did not learn
it, and pitching it reads as noise. Tooling internals, version-specific
breakage and root-cause write-ups almost never qualify.

Each TIL is one idea at the level he would explain to a friend. If it needs
two technical terms he has not used himself, it is too deep: either pitch
the simpler idea underneath it or drop it. Skip anything specific to one
project's code, and anything he clearly already knew. Never put a secret,
token, password or someone else's personal detail in a TIL.

Do not pitch anything that is already under "Saved TILs" or "Rejected
before" above, including the same fact in different words. The list shows
only the most recent ones, so also grep the repo for each candidate's key
term (`grep -ril "<term>" /home/oliverohrt/Documents/PROJECTS/til --include=*.md`).
If nothing new is worth saving, say so in two or three lines, run
`sweep.py <repo> --mark` (unless this is a dry run) and stop; an empty run
is a normal outcome, not a failure.

Write them the way he writes in his journal:

> Linux Commands: ping -c 20 1.1.1.1 tests if a server is reachable and how
> long replies take. -c is for count and 1.1.1.1 is the target IP, here
> Cloudflare's public DNS server. Used for checking internet stability.

> Networking: Internet connections have a finite amount of bandwidth and
> devices on the same network share it. Ex. if the network has 100 Mbps and
> I'm using 40 and my roommate 60, throttling him to 10 leaves me 90.

Rules: one to three plain sentences. Lead with the concrete thing (the real
command, the real number). Spell out what each flag or abbreviation means.
An "Ex." with numbers beats an abstract statement, and numbers should come
out round. No em dashes, no "essentially", "powerful", "leverages", no
summary sentence at the end.

Category: reuse one from the list above whenever it fits. Create a new one
only when nothing fits, name it in Title Case, and set `"flag": "new category"`
on the item so he sees it (a flagged item in a new category gets
`"flag": "flagged, new category"`). A new English word goes in `Vocabulary`, in three short
parts: a plain definition of a few words, an everyday example sentence, and
a brief origin with the root's meaning.

> Vocabulary: rationalize means to make excuses that sound reasonable. Ex.
> He rationalized buying the car as an investment. From Latin ratio,
> "reason".

Keep vocabulary brief. The example is about ordinary life (a package, a
car, a friend), never about this session, his projects or tech he was
working on. Always include the origin.

## 3. Review

Write the pitches to a JSON file in a fresh `mktemp -d` directory:

```json
{"title": "TIL review", "items": [
  {"id": "1", "label": "Linux Commands", "fields": [{"text": "ping -c 20 ..."}]},
  {"id": "2", "label": "Terminal UIs", "flag": "new category", "fields": [{"text": "..."}]}
]}
```

Run `python3 ~/.claude/skills/til/review.py <file>` with a Bash timeout of
600000. It opens a small WezTerm window, blocks until he is done, and prints:

```json
{"status": "submitted", "results": [{"id": "1", "decision": "accept", "note": ""}]}
```

- A note of just `a` or `r` is a slip (he hit n first): treat it as accept
  or reject.
- `submitted`: act on the decisions. `accept` keeps the item, `reject` drops
  it, `note` means rewrite it following the note. Put only the rewritten
  items in a new file and run the review again. After three rounds on the
  same item, drop it and say so.
- `pending`: he is still deciding. Run again with `--resume` after the file.
- `aborted` or `closed`: he backed out. Save nothing, say so, stop. If the
  result still lists every item as `reject`, he disliked the batch: run
  `store.py save` with only the `rejected` list so they are not pitched
  again, and ask what was off.
- `error` or exit code 3: the window could not open. Fall back to
  AskUserQuestion, one question per item with Accept and Reject options (his
  free-text answer is the note).

Do not print the pitches in chat before the review; the window is where he
reads them.

## 4. Save

Write the outcome to a JSON file and run `python3 ~/.claude/skills/til/store.py save <file>`:

```json
{"accepted": [{"category": "Linux Commands", "text": "ping -c 20 ..."}],
 "rejected": [{"category": "Terminal", "text": "..."}]}
```

Include the rejected pitches (first-round text) so they are not pitched
again. The script pulls, drops anything already saved, appends to today's
file, updates the categories, commits (`chore: add linux commands,
networking TILs`) and pushes. Read its JSON:

- `skipped_duplicates`: already in the repo. Tell him; make no cards for them.
- `pushed: false`: the commit is local and goes out with the next run. Say
  so and carry on.
- `ok: false`: stop and show him the error. Do not repair the repo yourself.

Once the save succeeded (even with nothing new), settle the flags that were
in this review, using each flag's term as `--flags` printed it:

- `sweep.py <repo> --flags-done TERM...` for flags whose pitch he accepted,
  including ones `save` skipped as already saved.
- `sweep.py <repo> --flags-rejected TERM...` for flags whose pitch he
  rejected. The first rejection keeps the flag open for one more try.

Quote a multi-word term as one argument. Then run `sweep.py <repo> --mark`
so the next run starts from here. Skip all three after an aborted review or
a dry run, so nothing is lost.

## 5. Anki cards

Make cards only for TILs that `save` reported under `saved`. Not every TIL
makes a good card; write zero to two per TIL:

- One fact per card. If the answer needs "and", split it or drop it.
- Front: a specific question that names its context ("ping: which flag sets
  how many packets to send?"). Back: the shortest complete answer.
- Use numbers that divide evenly (400 Mbps is 50 MB/s, not 340 is 42.5).
- For commands, ask in both directions only when both are worth knowing.
- Skip TILs that are context or narrative rather than a recallable fact.

Vocabulary cards follow the format of his existing vocab deck, one card per
word:

- `front`: the word alone, lowercase.
- `back`: a short definition, a few words, no full sentence.
- `example`: one sentence using the word, about ordinary life ("The pain
  was transient and gone by morning."), never about tech or his projects.
- `origin`: two or three sentences of etymology that end on a hook tying the
  root to the meaning ("It's just passing through."). Wrap foreign roots in
  asterisks for italics: `from the Latin *transire*, "to go across"`.

Review the cards with the same window: `"title": "Anki cards"`, `label` set
to `TIL::<Category>`, fields named `Front` and `Back` (for vocabulary add
`Example` and `Origin` fields). Handle notes and retries as in step 3. If
there are no card-worthy TILs, skip the review but still run
`python3 ~/.claude/skills/til/store.py flush` when the state above shows
cards waiting.

Then write the approved cards to a JSON file and run
`python3 ~/.claude/skills/til/store.py cards <file>` with a Bash timeout of
180000:

```json
{"cards": [
  {"category": "Linux Commands", "front": "ping: which flag ...?", "back": "-c (count)"},
  {"category": "Vocabulary", "front": "transient", "back": "temporary; short-lived",
   "example": "...", "origin": "..."}
]}
```

The script queues the cards in `cards.jsonl`, starts Anki if it is not
running, creates missing `TIL::<Category>` decks, adds the notes (plus any
queued from earlier runs), records their note ids, commits, pushes and syncs
with AnkiWeb. Read its JSON:

- `skipped_duplicates`: a card with that front already exists.
- `anki.still_queued` above 0: Anki could not be reached or refused a card;
  `anki.errors` says why. The cards stay queued and go in on the next run.
  Report it, do not retry in a loop.
- `anki.anki_started: true`: tell him Anki was opened and is still open.
- `anki.sync` starting with `conflict` or `error`: relay it once. Never
  resolve a sync conflict yourself.

## 6. Report

End with a short list: TILs saved (category and first few words), anything
skipped as a duplicate, cards added or queued, and the commit hashes. Then
remind him to write them in the journal.
