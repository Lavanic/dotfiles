# dotfiles

| | |
| --- | --- |
| **OS** | EndeavourOS (Arch) |
| **DE / compositor** | KDE Plasma / kwin (Wayland) |
| **Shell** | fish |
| **Prompt** | starship |
| **Terminal** | WezTerm |
| **Editor** | Zed |
| **Monitor** | btop |
| **Fetch** | neofetch |
| **Font** | Lilex Nerd Font |

daily setup is fish inside wezterm. wezterm has real splits and tabs built
in so I never ended up needing tmux, and starship handles the prompt and
mostly shuts up unless git has something to say. zoxide is the newest
addition but already the one I'd miss most, `z dot` beats typing paths.
the colors started as me trying to copy btop's default theme into my
terminal, I got them wrong in a brighter direction and liked it better, so
now it's its own palette ([otop](otop.md)) and even btop runs it through a
custom theme. zed is themed to match, same colors same transparency. my
claude code config lives in here too and it has hooks that notice when a
config changes and commit it back, so the repo keeps itself up to date.

everything is a GNU Stow package mirroring `$HOME`.

## Setup

```sh
sudo pacman -S stow fish starship wezterm zed btop eza zoxide git github-cli gitleaks ttf-lilex-nerd
yay -S neofetch
git clone https://github.com/Lavanic/dotfiles.git ~/dotfiles
cd ~/dotfiles && ./install.sh
```

If a real config already exists, stow refuses to overwrite it: move it away
or `stow --adopt --target="$HOME" <pkg>` and diff. Machine-local settings
stay untracked (`~/.gitconfig.local`, `~/.claude/settings.local.json`), and
no ssh, keys, or shell history live here.
