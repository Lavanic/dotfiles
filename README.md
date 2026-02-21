# dotfiles

Configs for my Linux machines, managed with [GNU Stow](https://www.gnu.org/software/stow/).

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

## New machine

```sh
sudo pacman -S stow fish starship wezterm eza ttf-lilex-nerd   # Arch
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
