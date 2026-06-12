#!/usr/bin/env bash
# Install Random Access Theme to local system locations.
#
# Installs:
#   Pi       → ~/.pi/agent/themes/random-access-theme.json
#   Ghostty  → ~/.config/ghostty/config (authoritative)
#              ~/Library/Application Support/com.mitchellh.ghostty/config (stub)
#   iTerm2   → ~/Library/Application Support/iTerm2/random-access-theme.itermcolors
#
# Usage:
#   bash scripts/install.sh                     # install all
#   bash scripts/install.sh --dry-run           # preview without writing
#   bash scripts/install.sh pi                  # install Pi only
#   bash scripts/install.sh ghostty             # install Ghostty only
#   bash scripts/install.sh iterm2              # install iTerm2 only
#   bash scripts/install.sh iterm2 --clean-dynamic  # archive ALL dynamic profiles

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PALETTE="$ROOT/palette/random-access-theme.yaml"
DRY=0
TARGET="all"
CLEAN_DYNAMIC=0

for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY=1
  [[ "$arg" == "--clean-dynamic" ]] && CLEAN_DYNAMIC=1
  [[ "$arg" =~ ^(pi|ghostty|iterm2|all)$ ]] && TARGET="$arg"
done

ok()      { echo "[OK]   $*"; }
info()    { echo "[INFO] $*"; }
fail()    { echo "[FAIL] $*" >&2; exit 1; }
section() { echo ""; echo "── $* ──"; }

install_file() {
  local src="$1" dst="$2"
  local bak_dir
  if [[ "$DRY" -eq 1 ]]; then
    info "[dry-run] $src → $dst"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  if [[ -f "$dst" ]]; then
    bak_dir="$(dirname "$dst")/backups"
    mkdir -p "$bak_dir"
    cp "$dst" "$bak_dir/$(basename "$dst").$(date +%Y%m%d-%H%M%S)"
  fi
  cp "$src" "$dst"
  local src_sum dst_sum
  src_sum=$(shasum -a 256 "$src" | awk '{print $1}')
  dst_sum=$(shasum -a 256 "$dst" | awk '{print $1}')
  [[ "$src_sum" == "$dst_sum" ]] || fail "integrity check failed: $dst"
  ok "$dst"
}

# ── Freshness ────────────────────────────────────────────────────────────────
CHECKSUM_FILE="$ROOT/themes/.checksum"
if [[ -f "$CHECKSUM_FILE" ]]; then
  STORED=$(awk '{print $1}' "$CHECKSUM_FILE")
  CURRENT=$(shasum -a 256 "$PALETTE" | awk '{print $1}')
  [[ "$STORED" == "$CURRENT" ]] || fail "palette changed since last generate — run: python3 scripts/generate.py"
  ok "themes are up-to-date with palette"
fi

# ════════════════════════════════════════════════════════════════════════════
# Pi
# ════════════════════════════════════════════════════════════════════════════
install_pi() {
  section "Pi"
  local src="$ROOT/themes/pi/random-access-theme.json"
  local dst="$HOME/.pi/agent/themes/random-access-theme.json"
  local settings="$HOME/.pi/agent/settings.json"

  python3 -c "import json; json.load(open('$src'))" 2>/dev/null \
    || fail "Pi theme is invalid JSON: $src"
  ok "Pi theme source is valid"

  install_file "$src" "$dst"

  if [[ -f "$settings" ]] && command -v jq >/dev/null 2>&1; then
    local active
    active=$(jq -r '.theme // ""' "$settings")
    if [[ "$active" != "random-access-theme" ]]; then
      if [[ "$DRY" -eq 0 ]]; then
        jq '.theme = "random-access-theme"' "$settings" > "${settings}.tmp" \
          && mv "${settings}.tmp" "$settings"
        ok "settings.json → random-access-theme"
      else
        info "[dry-run] settings.json theme: $active → random-access-theme"
      fi
    else
      ok "settings.json theme already correct"
    fi
  fi

  echo "  → Run /reload in Pi to activate."
}

# ════════════════════════════════════════════════════════════════════════════
# Ghostty
# ════════════════════════════════════════════════════════════════════════════
install_ghostty() {
  section "Ghostty"

  # Complete merged config — colors from palette + personal font/window/UX settings
  local config
  config=$(cat << 'GHOSTTY_EOF'
# Random Access Theme — Ghostty config
# Source: https://github.com/ssainz/random-access-themes

# ── Font ──────────────────────────────────────────────────────────────────────
font-family = Berkeley Mono Variable
font-family = GeistMono Nerd Font Mono
font-family = Symbols Nerd Font
font-size = 15
font-thicken = true
font-style = Retina
font-style-bold = Bold
font-style-italic = Retina Oblique
font-style-bold-italic = Bold Oblique
adjust-cell-height = 18%
bold-is-bright = false
font-feature = liga
font-feature = calt
font-feature = zero

# ── Colors — Random Access Theme ──────────────────────────────────────────────
background = 060607
foreground = d8efe9

cursor-color = 00ffb2
cursor-text  = 060607
cursor-style       = block
cursor-style-blink = true

selection-background = 1a1c20
selection-foreground = d8efe9
split-divider-color  = 101214

minimum-contrast = 1.2

# ANSI 16-color palette
palette = 0=#090a0b
palette = 1=#26c994
palette = 2=#4ade80
palette = 3=#a2e5b8
palette = 4=#00ffb2
palette = 5=#35d5c5
palette = 6=#66e3c4
palette = 7=#d8efe9
palette = 8=#6f8d86
palette = 9=#00ffb2
palette = 10=#4ade80
palette = 11=#8bf5dd
palette = 12=#00ffb2
palette = 13=#35d5c5
palette = 14=#66e3c4
palette = 15=#d8efe9

# ── Window ────────────────────────────────────────────────────────────────────
window-padding-x = 22
window-padding-y = 14,10
window-padding-balance = true
window-decoration = false
window-theme = dark
window-colorspace = display-p3
window-show-tab-bar = never
window-save-state = always
background-opacity = 1.0
background-blur = false
macos-titlebar-style = hidden
macos-titlebar-proxy-icon = hidden
resize-overlay = never
unfocused-split-opacity = 0.92
unfocused-split-fill = 060607
faint-opacity = 0.95

# ── UX ────────────────────────────────────────────────────────────────────────
mouse-hide-while-typing = true
mouse-scroll-multiplier = 3
scrollback-limit = 10000000
copy-on-select = clipboard
confirm-close-surface = false
clipboard-read = allow
clipboard-write = allow
clipboard-trim-trailing-spaces = true
macos-option-as-alt = true

# ── Shell integration ──────────────────────────────────────────────────────────
shell-integration = zsh
shell-integration-features = cursor,sudo,title

# ── Quick Terminal ─────────────────────────────────────────────────────────────
quick-terminal-position = top
quick-terminal-animation-duration = 0.2
quick-terminal-autohide = true
GHOSTTY_EOF
)

  local xdg="$HOME/.config/ghostty/config"
  local lib="$HOME/Library/Application Support/com.mitchellh.ghostty/config"

  if [[ "$DRY" -eq 1 ]]; then
    info "[dry-run] write Ghostty config → $xdg"
    info "[dry-run] stub Library config  → $lib"
  else
    # Write full config to XDG only
    mkdir -p "$(dirname "$xdg")"
    if [[ -f "$xdg" ]]; then
      mkdir -p "$(dirname "$xdg")/backups"
      cp "$xdg" "$(dirname "$xdg")/backups/config.$(date +%Y%m%d-%H%M%S)"
    fi
    echo "$config" > "$xdg"
    ok "$xdg"

    # Stub out Library config so it doesn't override XDG
    mkdir -p "$(dirname "$lib")"
    if [[ -f "$lib" ]]; then
      mkdir -p "$(dirname "$lib")/backups"
      cp "$lib" "$(dirname "$lib")/backups/config.$(date +%Y%m%d-%H%M%S)"
    fi
    printf '# Random Access Theme\n# All config lives in ~/.config/ghostty/config\n' > "$lib"
    ok "$lib (stub)"

    /Applications/Ghostty.app/Contents/MacOS/ghostty +validate-config \
      --config-file="$xdg" >/dev/null 2>&1 \
      && ok "Ghostty config validates" \
      || fail "Ghostty config validation failed"

    local dupe
    dupe=$(/Applications/Ghostty.app/Contents/MacOS/ghostty \
      +show-config --changes-only 2>/dev/null | grep -c "^font-family = Berkeley")
    [[ "$dupe" -eq 1 ]] \
      && ok "no duplicate font entries" \
      || info "font-family appears ${dupe}x — restart Ghostty to verify"
  fi

  echo "  → Quit and relaunch Ghostty to apply."
}

# ════════════════════════════════════════════════════════════════════════════
# iTerm2
# ════════════════════════════════════════════════════════════════════════════
install_iterm2() {
  section "iTerm2"

  local src="$ROOT/themes/iterm2/random-access-theme.itermcolors"
  local dst="$HOME/Library/Application Support/iTerm2/random-access-theme.itermcolors"
  local dprofiles="$HOME/Library/Application Support/iTerm2/DynamicProfiles"

  [[ -f "$src" ]] || fail "iTerm2 theme not found: $src — run: python3 scripts/generate.py"
  if command -v plutil >/dev/null 2>&1; then
    plutil -lint "$src" >/dev/null 2>&1 || fail "invalid .itermcolors plist: $src"
    ok "iTerm2 preset plist validates"
  fi

  if [[ "$DRY" -eq 1 ]]; then
    info "[dry-run] copy .itermcolors → $dst"
    return
  fi

  # Remove only Random Access dynamic profiles by default.
  # Optional: --clean-dynamic archives ALL dynamic profiles.
  local cleared=0
  mkdir -p "$dprofiles/backups"

  if [[ "$CLEAN_DYNAMIC" -eq 1 ]]; then
    for f in "$dprofiles"/*.json; do
      [[ -f "$f" ]] || continue
      mv "$f" "$dprofiles/backups/$(basename "$f").$(date +%Y%m%d-%H%M%S)"
      (( cleared++ )) || true
    done
    [[ "$cleared" -gt 0 ]] && ok "archived $cleared dynamic profile(s)" \
                            || ok "no dynamic profiles found"
  else
    for f in "$dprofiles"/random-access-theme.json "$dprofiles"/random-access-memories.json; do
      [[ -f "$f" ]] || continue
      mv "$f" "$dprofiles/backups/$(basename "$f").$(date +%Y%m%d-%H%M%S)"
      (( cleared++ )) || true
    done
    [[ "$cleared" -gt 0 ]] && ok "archived $cleared Random Access dynamic profile(s)" \
                            || ok "no Random Access dynamic profiles found"
  fi

  # Copy .itermcolors to a stable location for easy re-import
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  ok "copied: $dst"

  echo ""
  echo "  → In iTerm2: Preferences → Profiles → Colors"
  echo "     Color Presets… → Import → select:"
  echo "     $dst"
}

# ════════════════════════════════════════════════════════════════════════════
# Dispatch
# ════════════════════════════════════════════════════════════════════════════
case "$TARGET" in
  pi)      install_pi ;;
  ghostty) install_ghostty ;;
  iterm2)  install_iterm2 ;;
  all)     install_pi; install_ghostty; install_iterm2 ;;
esac

echo ""
echo "Done."
