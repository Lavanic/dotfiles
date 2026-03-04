if status is-interactive

    starship init fish | source

    if command -q zoxide
        zoxide init fish | source
    end

    if command -q fzf
        set -gx FZF_DEFAULT_OPTS "--height 60% --layout=reverse --border \
--color=fg:#bcbcbc,bg:-1,hl:#f0c050 --color=fg+:#ffffff,bg+:#111111,hl+:#ffe080 \
--color=info:#5f8787,prompt:#50f095,pointer:#f05050 \
--color=marker:#50f095,spinner:#4897d4,header:#4897d4,border:#5f8787"
        set -g fzf_preview_dir_cmd eza --all --color=always --icons
    end

    set -gx EDITOR nvim
    set -gx VISUAL nvim

    # Navigation
    abbr --add ..   'cd ..'
    abbr --add ...  'cd ../..'
    abbr --add .... 'cd ../../..'

    # Listing
    if command -q eza
        alias ls="eza --icons --group-directories-first"
        abbr --add la  'eza --icons --group-directories-first -a'
        abbr --add ll  'eza --icons --group-directories-first -lh'
        abbr --add lla 'eza --icons --group-directories-first -lha'
        abbr --add lt  'eza --icons --tree --level=2'
    end

    # Pacman
    abbr --add pac  'sudo pacman -S'
    abbr --add pacu 'sudo pacman -Syu'
    abbr --add pacr 'sudo pacman -Rns'
    abbr --add pacs 'pacman -Ss'
    abbr --add pacq 'pacman -Qi'

    # Git
    abbr --add g   'git'
    abbr --add gs  'git status'
    abbr --add ga  'git add'
    abbr --add gc  'git commit -m'
    abbr --add gp  'git push'
    abbr --add gl  'git log --oneline --graph --decorate'
    abbr --add gd  'git diff'
    abbr --add gco 'git checkout'
    abbr --add gb  'git branch'

    # Misc
    abbr --add v     'nvim'
    alias code='zeditor'
    abbr --add c     'clear'
    abbr --add grep  'grep --color=auto'
    abbr --add df    'df -h'
    abbr --add du    'du -sh'
    abbr --add ports 'ss -tulpn'

    set fish_greeting

end

fish_add_path --global ~/.local/bin

# machine-local config, untracked (like ~/.gitconfig.local)
if test -f ~/.config/fish/local.fish
    source ~/.config/fish/local.fish
end
