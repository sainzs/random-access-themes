# Optional shell behaviour that pairs with the colour exports. Not colour; opt in.
# Requires: eza, bat, fzf; a Nerd Font for --icons.
alias ls='eza --icons=always --group-directories-first'
alias ll='eza -lh --icons=always --git --group-directories-first'
alias la='eza -lah --icons=always --git --group-directories-first'
alias lt='eza --tree --icons=always --level=2 --group-directories-first'

# fzf: Ctrl-T files → bat preview (eza tree for dirs); Alt-C dirs → eza tree;
# Ctrl-R → full command with ctrl-y to copy (pbcopy: macOS; swap for xclip/wl-copy).
export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=numbers --line-range=:200 {} 2>/dev/null || eza --tree --level=2 --icons=always --color=always {}' --preview-window=right,55%,border-left"
export FZF_ALT_C_OPTS="--preview 'eza --tree --level=2 --icons=always --color=always --group-directories-first {}' --preview-window=right,50%,border-left"
export FZF_CTRL_R_OPTS="--preview 'echo {2..}' --preview-window=down,3,wrap --bind 'ctrl-y:execute-silent(echo -n {2..} | pbcopy)+abort'"

# man pages through bat, on the same ANSI theme.
command -v bat >/dev/null && export MANPAGER="sh -c 'col -bx | bat -l man -p'" MANROFFOPT="-c"
