if status is-interactive

    # ─────────────────────────────────────────────────────
    #  Starship prompt
    # ─────────────────────────────────────────────────────
    starship init fish | source

    # ─────────────────────────────────────────────────────
    #  Environment
    # ─────────────────────────────────────────────────────
    set -gx EDITOR nvim
    set -gx VISUAL nvim

    # ─────────────────────────────────────────────────────
    #  Abbreviations  (like aliases, but they expand inline
    #  so you can see/edit the real command before running)
    # ─────────────────────────────────────────────────────

    # Navigation
    abbr --add .. 'cd ..'
    abbr --add ... 'cd ../..'
    abbr --add .... 'cd ../../..'

    # Listing (requires eza — install with: sudo pacman -S eza)
    abbr --add ls  'eza --icons --group-directories-first'
    abbr --add la  'eza --icons --group-directories-first -a'
    abbr --add ll  'eza --icons --group-directories-first -lh'
    abbr --add lla 'eza --icons --group-directories-first -lha'
    abbr --add lt  'eza --icons --tree --level=2'

    # Pacman shortcuts
    abbr --add pac    'sudo pacman -S'
    abbr --add pacu   'sudo pacman -Syu'
    abbr --add pacr   'sudo pacman -Rns'
    abbr --add pacs   'pacman -Ss'
    abbr --add pacq   'pacman -Qi'

    # Git
    abbr --add g    'git'
    abbr --add gs   'git status'
    abbr --add ga   'git add'
    abbr --add gc   'git commit -m'
    abbr --add gp   'git push'
    abbr --add gl   'git log --oneline --graph --decorate'
    abbr --add gd   'git diff'
    abbr --add gco  'git checkout'
    abbr --add gb   'git branch'

    # Misc
    abbr --add v    'nvim'
    abbr --add c    'clear'
    abbr --add cat  'bat'      # requires: sudo pacman -S bat
    abbr --add grep 'grep --color=auto'
    abbr --add df   'df -h'
    abbr --add du   'du -sh'
    abbr --add ports 'ss -tulpn'

    # ─────────────────────────────────────────────────────
    #  Better history search with up/down arrows
    #  (fish does this by default, but let's be explicit)
    # ─────────────────────────────────────────────────────
    bind \e\[A history-prefix-search-backward
    bind \e\[B history-prefix-search-forward

    # ─────────────────────────────────────────────────────
    #  Suppress the default fish greeting
    # ─────────────────────────────────────────────────────
    set fish_greeting

end
