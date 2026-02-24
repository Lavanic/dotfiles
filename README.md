# dotfiles

Configs for my Linux machines, managed with [GNU Stow](https://www.gnu.org/software/stow/).
Everything is themed with the [otop palette](otop.md).

## What's in here

**fish** (shell)
Starship prompt, nvim as the default editor, and abbreviations: `..`/`...`
for navigation, `pac`/`pacu`/`pacr` for pacman, `g`/`gs`/`ga`/`gc`/`gp` for
git. `ls`, `ll`, `la` and `lt` use eza when it is installed. Also puts
`~/.local/bin` on PATH.

**starship** (prompt)
One line: user@host, directory, git branch and status, language versions
(python, node, rust), duration of slow commands, and a clock on the right.
Colors match the btop default theme.

**wezterm** (terminal)
Lilex Nerd Font, colors matched to the btop default theme, launches fish.
Keybindings for pane splits (ctrl+shift+enter and alt+enter), pane
navigation (ctrl+shift+arrows), pane resizing (alt+arrows), and tabs
(ctrl+t, ctrl+1 through ctrl+9).

**git**
Identity, defaults (main as init branch, auto upstream on push, pruned
fetches, branches sorted by recency), gh as the GitHub credential helper,
and the global ignore file. Machine-specific settings go in the untracked
`~/.gitconfig.local`, which is included last so it wins.

**zed** (editor)
Settings (fonts, One Dark/Light following the system theme, minimap) and a
keymap tweak: alt+g d opens the project diff from anywhere.

**btop** (system monitor)
btop.conf and the otop theme. btop rewrites its conf on exit, so the repo
shows a diff now and then; commit when it is a change worth keeping.

**claude** (Claude Code)
Global CLAUDE.md, settings.json with permissions scoped so Claude can commit
and push this repo on its own, hooks that notice uncommitted dotfiles
changes, a desktop notification hook, and a dotfiles-sync skill. A gitleaks
pre-commit hook guards against committing secrets (sudo pacman -S gitleaks).
Machine-local permission grants stay in untracked settings.local.json.

## New machine

```sh
sudo pacman -S stow fish starship wezterm eza ttf-lilex-nerd git github-cli zed btop   # Arch
git clone https://github.com/Lavanic/dotfiles.git ~/dotfiles
cd ~/dotfiles
./install.sh
```

Each top level directory is a stow package that mirrors `$HOME`, so
`fish/.config/fish/config.fish` gets linked to `~/.config/fish/config.fish`.
Rerun `./install.sh` after pulling, it restows cleanly.

If a config already exists on the machine, stow refuses to overwrite it.
Move the file away, or adopt it into the repo and compare:

```sh
stow --adopt --target="$HOME" fish
git diff
```

## Adding an app

```sh
mkdir -p app/.config/app
mv ~/.config/app/config.toml app/.config/app/
./install.sh app
```
