# Global instructions

## Git
- Conventional commits: feat, fix, chore, docs, refactor.
- Never add co-author or AI attribution lines to commits or PRs.
- Don't push unless I ask. ~/dotfiles is the one exception (see Dotfiles).
- Commit messages read like I typed them: terse, concrete, about the
  change itself. Never meta-commentary like "make it more human" or
  "improve wording"; say what changed ("trim the readme").

## Writing and code style
- No em dashes in prose or docs you write for me.
- No decorative comment banners or box-drawing headers in configs or code.
- Comments only where the code can't say it. No tutorial-voice comments.
- If content (mine or generated) reads like low-effort AI output, flag it
  rather than polishing around it.

## Working
- Don't claim something works until you ran it and saw it pass. Show output.
- Run the repo's check commands and show the output before saying done, and
  say what wasn't tested.
- My machines are Arch-based Linux (KDE, fish, WezTerm, Zed). Use pacman for
  install instructions, paru for AUR, and fish syntax for shell config.
- Hooks and scripts you run use bash.
- Dotfiles live at ~/dotfiles as GNU Stow packages. New tool configs get
  added there as a package, not left loose in ~/.config.

## Dotfiles
- ~/dotfiles (public repo, GNU Stow) owns every config it tracks; live files
  are symlinks into it. Edit the repo file, never a detached copy.
- Standing instruction: when work leaves changes in ~/dotfiles, run the
  dotfiles-sync skill and push to origin main without asking.
- New tool configs become stow packages there (the skill covers how).
- Never bypass the pre-commit secret scan. If it blocks, stop and tell me.
- Theming follows the otop palette (otop.md at the repo root).

## Continuous improvement
- When I correct you the same way a second time, propose a new line for this
  file in your reply.

## TIL flags
- A `^word` or `^"some phrase"` in my messages (like `^erroneously`) flags
  that word or topic for the /til skill. Read the message as if the `^`
  weren't there and don't mention the flag.
