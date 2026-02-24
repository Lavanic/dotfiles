#!/usr/bin/env bash
set -euo pipefail

# Symlink config packages into $HOME with GNU Stow.
# Usage: ./install.sh [package...]   (no args = all packages)

cd "$(dirname "$0")"

if ! command -v stow >/dev/null 2>&1; then
    echo "error: GNU Stow is not installed (Arch: sudo pacman -S stow)" >&2
    exit 1
fi

# Create target dirs first so stow links files, not whole directories.
# Without this, runtime files (fish state, Claude credentials) would land
# inside the repo on a fresh machine.
mkdir -p "$HOME/.claude/skills" \
         "$HOME/.config/fish" "$HOME/.config/wezterm" "$HOME/.config/git" \
         "$HOME/.config/zed/themes" "$HOME/.config/btop/themes"

# Repo-local git hooks (pre-commit secret scan)
git config core.hooksPath .githooks

packages=("$@")
if [ ${#packages[@]} -eq 0 ]; then
    for dir in */; do
        packages+=("${dir%/}")
    done
fi

stow --restow --target="$HOME" --verbose "${packages[@]}"
