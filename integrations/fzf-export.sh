# fzf — Random Access Themes
# Works with every flavor and tube: colours are ANSI slots (`blue` = the terminal's
# accent, 8 = muted, -1 = terminal default so the picker stays translucent on glass).
# Source this file from your shell profile.
export FZF_DEFAULT_OPTS="
  --height=40% --layout=reverse --border=rounded --border-label-pos=2 --padding=0,1
  --prompt='❯ ' --pointer='▌' --marker='✓'
  --color=bg:-1,bg+:${TERMINAL_SELECTION:-#3a3a3a},fg:-1,fg+:blue,hl:blue,hl+:bright-blue
  --color=info:8,prompt:blue,pointer:blue,marker:green,header:8,border:8,label:8,spinner:yellow,gutter:-1"
# Ctrl-T files → bat preview (eza tree for dirs); Alt-C dirs → eza tree; Ctrl-R → full command, ctrl-y copies.
export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=numbers --line-range=:200 {} 2>/dev/null || eza --tree --level=2 --icons=always --color=always {}' --preview-window=right,55%,border-left"
export FZF_ALT_C_OPTS="--preview 'eza --tree --level=2 --icons=always --color=always --group-directories-first {}' --preview-window=right,50%,border-left"
export FZF_CTRL_R_OPTS="--preview 'echo {2..}' --preview-window=down,3,wrap --bind 'ctrl-y:execute-silent(echo -n {2..} | pbcopy)+abort'"
