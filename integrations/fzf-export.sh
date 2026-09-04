# fzf — Random Access Themes
# Colour only, on ANSI slots so it works for every flavor and tube: `blue` = the
# terminal's accent, 8 = muted, 0 = the theme's raised/selection surface, -1 = the
# terminal default (keeps the picker translucent on glass). Source from your profile.
export FZF_DEFAULT_OPTS="
  --height=40% --layout=reverse --border=rounded --padding=0,1
  --color=bg:-1,bg+:0,fg:-1,fg+:blue,hl:blue,hl+:bright-blue
  --color=info:8,prompt:blue,pointer:blue,marker:green,header:8,border:8,label:8,spinner:yellow,gutter:-1"
# Previews and key bindings live in integrations/shell-extras.sh (optional).
