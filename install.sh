#!/usr/bin/env bash
set -euo pipefail

# Symlink config packages into $HOME with GNU Stow.
# Usage: ./install.sh [--packages] [package...]   (no args = all packages)

cd "$(dirname "$0")"

if [ "${1:-}" = "--packages" ]; then
    shift
    sed 's/#.*//; s/[[:space:]]*$//' packages.txt | grep -v '^$' | sudo pacman -S --needed -
    if ! command -v paru >/dev/null 2>&1; then
        tmp=$(mktemp -d)
        git clone --depth 1 https://aur.archlinux.org/paru-bin.git "$tmp/paru-bin"
        (cd "$tmp/paru-bin" && makepkg -si)
        rm -rf "$tmp"
    fi
    sed 's/#.*//; s/[[:space:]]*$//' packages-aur.txt | grep -v '^$' | paru -S --needed -
fi

if ! command -v stow >/dev/null 2>&1; then
    echo "error: GNU Stow is not installed (Arch: sudo pacman -S stow)" >&2
    exit 1
fi

# Create target dirs first so stow links files, not whole directories.
# Without this, runtime files (fish state, Claude credentials) would land
# inside the repo on a fresh machine.
mkdir -p "$HOME/.claude/skills" "$HOME/.local/bin" \
         "$HOME/.config/fish" "$HOME/.config/wezterm" "$HOME/.config/git" \
         "$HOME/.config/zed/themes" "$HOME/.config/btop/themes" \
         "$HOME/.config/neofetch"

# Repo-local git hooks (pre-commit secret scan)
git config core.hooksPath .githooks

packages=("$@")
if [ ${#packages[@]} -eq 0 ]; then
    for dir in */; do
        # system/ holds root-owned files (grub theme), installed manually
        [ "$dir" = "system/" ] && continue
        packages+=("${dir%/}")
    done
fi

stow --restow --target="$HOME" --verbose "${packages[@]}"

# Install fish plugins listed in fish_plugins
if command -v fish >/dev/null 2>&1; then
    fish -c 'type -q fisher; and fisher update' || true
fi
