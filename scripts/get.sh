#!/usr/bin/env bash
# get.sh — clone-free installer for Random Access Theme.
#
# Fetches the generated theme file for a terminal from the committed themes/
# directory on GitHub and writes it to the standard location for that terminal.
# No clone, no Python, no build step — just curl.
#
# Run remotely:
#   curl -fsSL https://raw.githubusercontent.com/sainzs/random-access-themes/main/scripts/get.sh | bash -s -- ghostty
#   curl -fsSL https://raw.githubusercontent.com/sainzs/random-access-themes/main/scripts/get.sh | bash -s -- --dry-run wezterm
#
# Or from a clone:
#   bash scripts/get.sh kitty
#
# Targets: alacritty | wezterm | ghostty | kitty | iterm2 | windows-terminal | pi | all
# Override the ref (default: main) with RAT_REF, e.g. RAT_REF=v0.1.1.

set -euo pipefail

REPO="sainzs/random-access-themes"
REF="${RAT_REF:-main}"
BASE="https://raw.githubusercontent.com/${REPO}/${REF}/themes"

DRY=0
TARGETS=()
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    alacritty|wezterm|ghostty|kitty|iterm2|windows-terminal|pi|all) TARGETS+=("$arg") ;;
    *)
      echo "get.sh: unknown argument '$arg'" >&2
      echo "usage: get.sh [--dry-run] <alacritty|wezterm|ghostty|kitty|iterm2|windows-terminal|pi|all>" >&2
      exit 2
      ;;
  esac
done

if [ "${#TARGETS[@]}" -eq 0 ]; then
  TARGETS=("all")
fi

command -v curl >/dev/null 2>&1 || { echo "get.sh: curl is required" >&2; exit 1; }

ok()   { printf "[OK]   %s\n" "$*"; }
info() { printf "[INFO] %s\n" "$*"; }
section() { printf "\n── %s ──\n" "$*"; }

# fetch <url> → stdout (fails the script on HTTP error via curl -f)
fetch() { curl -fsSL "$1"; }

# place <dst> : reads payload from stdin, backs up existing file, writes it
place() {
  local dst="$1"
  local tmp
  tmp="$(mktemp)"
  cat > "$tmp"
  if [ ! -s "$tmp" ]; then
    rm -f "$tmp"
    echo "get.sh: empty payload — aborting (source URL may be wrong)" >&2
    exit 1
  fi
  if [ "$DRY" -eq 1 ]; then
    rm -f "$tmp"
    info "[dry-run] would write → $dst"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  if [ -f "$dst" ]; then
    mkdir -p "$(dirname "$dst")/backups"
    cp "$dst" "$(dirname "$dst")/backups/$(basename "$dst").$(date +%Y%m%d-%H%M%S)"
  fi
  mv "$tmp" "$dst"
  ok "$dst"
}

install_alacritty() {
  section "Alacritty"
  fetch "$BASE/alacritty/random-access-theme.toml" | place "$HOME/.config/alacritty/themes/random-access-theme.toml"
  [ "$DRY" -eq 1 ] && return
  echo "  → Add to alacritty.toml:  import = [\"~/.config/alacritty/themes/random-access-theme.toml\"]"
}

install_wezterm() {
  section "WezTerm"
  fetch "$BASE/wezterm/random-access-theme.toml" | place "$HOME/.config/wezterm/colors/random-access-theme.toml"
  [ "$DRY" -eq 1 ] && return
  echo "  → In wezterm.lua:  config.color_scheme_dirs = { '\$HOME/.config/wezterm/colors' }"
  echo "                     config.color_scheme = 'Random Access Theme'"
}

install_kitty() {
  section "kitty"
  fetch "$BASE/kitty/random-access-theme.conf" | place "$HOME/.config/kitty/theme.conf"
  [ "$DRY" -eq 1 ] && return
  echo "  → Add to kitty.conf:  include theme.conf"
}

install_ghostty() {
  section "Ghostty"
  # Non-destructive: write the color config to a separate file and include it,
  # so an existing ghostty config is never overwritten.
  fetch "$BASE/ghostty/random-access-theme.conf" | place "$HOME/.config/ghostty/random-access-theme"
  [ "$DRY" -eq 1 ] && return
  echo "  → Add to ~/.config/ghostty/config:  config-file = random-access-theme"
}

install_iterm2() {
  section "iTerm2"
  fetch "$BASE/iterm2/random-access-theme.itermcolors" \
    | place "$HOME/Library/Application Support/iTerm2/random-access-theme.itermcolors"
  [ "$DRY" -eq 1 ] && return
  echo "  → iTerm2 → Settings → Profiles → Colors → Color Presets… → Import →"
  echo "    $HOME/Library/Application Support/iTerm2/random-access-theme.itermcolors"
}

install_windows_terminal() {
  section "Windows Terminal"
  # WT has no on-disk theme file; save the scheme JSON for manual paste.
  fetch "$BASE/windows-terminal/random-access-theme.json" \
    | place "$HOME/random-access-theme-windows-terminal.json"
  [ "$DRY" -eq 1 ] && return
  echo "  → Open Windows Terminal → Settings → 'Open JSON file' (Ctrl+Shift+,)"
  echo "    Paste the contents into the \"schemes\" array, then pick it under a profile's appearance."
}

install_pi() {
  section "Pi"
  # This used to fetch one file, which meant installing from a repo of sixteen
  # themes and coming away with one. raw.githubusercontent cannot list a
  # directory, so the family ships a manifest; validate_theme.py fails if it
  # drifts from themes/pi/, so it cannot silently go stale.
  local index
  index="$(fetch "$BASE/pi/index.txt")" || {
    echo "get.sh: could not fetch the theme index — is RAT_REF=$REF valid?" >&2
    exit 1
  }
  local count=0
  while IFS= read -r name; do
    [ -n "$name" ] || continue
    fetch "$BASE/pi/$name.json" | place "$HOME/.pi/agent/themes/$name.json"
    count=$((count + 1))
  done <<EOF
$index
EOF
  [ "$DRY" -eq 1 ] && return
  info "$count themes installed"
  echo "  → Set in ~/.pi/agent/settings.json:  \"theme\": \"mediodia/anochecer\""
  echo "    Any one of them works alone; a single / is a light/dark pair."
  echo "    Then run /reload in Pi."
}

run_target() {
  case "$1" in
    alacritty)        install_alacritty ;;
    wezterm)          install_wezterm ;;
    kitty)            install_kitty ;;
    ghostty)          install_ghostty ;;
    iterm2)           install_iterm2 ;;
    windows-terminal) install_windows_terminal ;;
    pi)               install_pi ;;
    all)
      install_alacritty; install_wezterm; install_kitty; install_ghostty
      install_iterm2; install_windows_terminal; install_pi
      ;;
  esac
}

printf "Random Access Theme — get.sh (%s @ %s)" "$REPO" "$REF"
[ "$DRY" -eq 1 ] && printf " [dry-run]"
printf "\n"

for t in "${TARGETS[@]}"; do
  run_target "$t"
done

printf "\nDone.\n"
