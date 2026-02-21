#!/usr/bin/env bash
set -euo pipefail

# Symlink config packages into $HOME with GNU Stow.
# Usage: ./install.sh [package...]   (no args = all packages)

cd "$(dirname "$0")"

if ! command -v stow >/dev/null 2>&1; then
    echo "error: GNU Stow is not installed (Arch: sudo pacman -S stow)" >&2
    exit 1
fi

packages=("$@")
if [ ${#packages[@]} -eq 0 ]; then
    for dir in */; do
        packages+=("${dir%/}")
    done
fi

stow --restow --target="$HOME" --verbose "${packages[@]}"
