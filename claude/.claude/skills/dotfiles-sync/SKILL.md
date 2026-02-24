---
name: dotfiles-sync
description: Commit and push changes in ~/dotfiles, or bring a new tool's config under stow. Use when ~/dotfiles has uncommitted changes (a hook will say so), when a config symlinked into the repo was edited, or when the user asks to add a tool's config to their dotfiles.
---

# dotfiles-sync

The repo at ~/dotfiles is public and owns every config it tracks. Live files
are stow symlinks into it.

## Current state

!`git -C /home/oliverohrt/dotfiles status --short`

## Committing changes

1. Group changed files by stow package (first path segment). One conventional
   commit per logical change, package as scope: `feat(fish): ...`,
   `chore(btop): ...`. Never "update N files".
2. Stage explicit paths only. Never `git add -A` or `git add .`.
3. Commit normally; the pre-commit hook runs a secret scan. If it blocks,
   unstage, remove the secret, and tell the user. Never use --no-verify, and
   never repeat a found secret in output.
4. Push with `git -C /home/oliverohrt/dotfiles push origin main`. Never
   force-push. If the push is rejected, stop and report; don't resolve
   silently.
5. btop rewrites btop.conf on exit. If the only diff is btop runtime noise
   (graph selections and the like), commit it as `chore(btop): config drift`
   or leave it and say so.

## Adding a new tool's config

1. Create the package mirroring $HOME: `<pkg>/.config/<tool>/...` (or
   `<pkg>/.<file>` for home-level dotfiles).
2. Move the real config into the package, then run
   `stow -d /home/oliverohrt/dotfiles -t /home/oliverohrt <pkg>`.
   If stow reports a conflict, the real file still exists: move it aside
   first. Verify with readlink that the live path now points into the repo.
3. Add `!/<pkg>/` to the repo .gitignore allowlist (the root .gitignore
   denies everything by default).
4. Add the package to the README table and the pacman line if it needs a
   package installed.
5. If the tool can be themed, use the otop palette (otop.md at the repo
   root); prefer its terminal/ANSI color mode over hand-theming.
