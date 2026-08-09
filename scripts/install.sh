#!/usr/bin/env bash
# Install Random Access Theme to local system locations.
#
# Installs:
#   Pi       → every theme into ~/.pi/agent/themes/, and sets the active one
#   Prime    → every theme into ~/.prime/agent/themes/, and sets the active one.
#              That path is Prime's *global* custom theme directory
#              (getCustomThemesDir() = <agent dir>/themes), so the themes are
#              available in every session rather than one project.
#   Ghostty  → ~/.config/ghostty/config (authoritative)
#              ~/Library/Application Support/com.mitchellh.ghostty/config (stub)
#   iTerm2   → ~/Library/Application Support/iTerm2/<theme>.itermcolors
#
# Usage:
#   bash scripts/install.sh                          # all, theme reckoner-scope
#   bash scripts/install.sh --theme reckoner-wopr    # pick the active theme
#   bash scripts/install.sh --dry-run                # preview without writing
#   bash scripts/install.sh pi                       # Pi only
#   bash scripts/install.sh prime                    # Prime Agent only
#   bash scripts/install.sh ghostty                  # Ghostty only
#   bash scripts/install.sh iterm2                   # iTerm2 only
#   bash scripts/install.sh iterm2 --clean-dynamic   # archive ALL dynamic profiles
#
# The Ghostty colours are read from themes/ghostty/<theme>.conf rather than
# written out here. They used to be a heredoc in this file — a second copy of the
# flagship palette that no generator touched and nothing checked, which is the
# drift this repo exists to prevent.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PALETTE="$ROOT/palette/random-access-theme.yaml"
DRY=0
TARGET="all"
CLEAN_DYNAMIC=0
# The phosphor family is the reference here, and this is the one the harness
# footer was tuned against.
THEME="reckoner-scope"

prev=""
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY=1
  [[ "$arg" == "--clean-dynamic" ]] && CLEAN_DYNAMIC=1
  [[ "$arg" =~ ^(pi|prime|ghostty|iterm2|all)$ ]] && TARGET="$arg"
  [[ "$prev" == "--theme" ]] && THEME="$arg"
  prev="$arg"
done

[[ -f "$ROOT/themes/pi/$THEME.json" ]] || {
  echo "[FAIL] no such theme: $THEME" >&2
  echo "       available:" >&2
  for f in "$ROOT"/themes/pi/*.json; do echo "         $(basename "$f" .json)" >&2; done
  exit 1
}

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
# themes/.checksum carries one line per palette — "<sha>  <file>". It used to
# hold a single hash, and reading it with a bare awk over column one now yields
# four, so this compared four hashes against one and aborted every install.
CHECKSUM_FILE="$ROOT/themes/.checksum"
if [[ -f "$CHECKSUM_FILE" ]]; then
  stale=""
  for pal in "$ROOT"/palette/*.yaml; do
    name="$(basename "$pal")"
    stored=$(awk -v n="$name" '$2 == n {print $1}' "$CHECKSUM_FILE")
    current=$(shasum -a 256 "$pal" | awk '{print $1}')
    [[ "$stored" == "$current" ]] || stale="$stale $name"
  done
  [[ -z "$stale" ]] || fail "palette(s) changed since last generate —$stale — run: make generate"
  ok "themes are up-to-date with all palettes"
fi

# ════════════════════════════════════════════════════════════════════════════
# Pi
# ════════════════════════════════════════════════════════════════════════════
install_pi() {
  section "Pi"
  local settings="$HOME/.pi/agent/settings.json"
  local dir="$HOME/.pi/agent/themes"

  # Every theme, not just the flagship. A theme you cannot switch to is not
  # installed, and /theme lists what is in this directory.
  local count=0
  for src in "$ROOT"/themes/pi/*.json; do
    python3 -c "import json; json.load(open('$src'))" 2>/dev/null \
      || fail "Pi theme is invalid JSON: $src"
    # Symlink rather than copy: a copy is how a fork of this repo's own generated
    # theme ended up six colours adrift in another project.
    if [[ "$DRY" -eq 1 ]]; then
      info "[dry-run] link $(basename "$src") → $dir/"
    else
      mkdir -p "$dir"
      ln -sf "$src" "$dir/$(basename "$src")"
    fi
    count=$((count + 1))
  done
  ok "$count Pi themes linked into $dir"

  # A theme registers under its JSON "name", which is not always its filename.
  local registered
  registered=$(python3 -c "import json;print(json.load(open('$ROOT/themes/pi/$THEME.json'))['name'])")
  if [[ "$registered" != "$THEME" ]]; then
    info "note: $THEME.json registers as \"$registered\" — using that"
  fi

  if [[ -f "$settings" ]] && command -v jq >/dev/null 2>&1; then
    local active
    active=$(jq -r '.theme // ""' "$settings")
    if [[ "$active" != "$registered" ]]; then
      if [[ "$DRY" -eq 0 ]]; then
        cp "$settings" "$settings.bak-$(date +%Y%m%d-%H%M%S)"
        jq --arg t "$registered" '.theme = $t' "$settings" > "${settings}.tmp" \
          && mv "${settings}.tmp" "$settings"
        ok "settings.json theme: \"$active\" → \"$registered\""
      else
        info "[dry-run] settings.json theme: \"$active\" → \"$registered\""
      fi
    else
      ok "settings.json theme already \"$registered\""
    fi
  fi

  echo "  → Run /reload in Pi to activate."
}

# ════════════════════════════════════════════════════════════════════════════
# Prime Agent
# ════════════════════════════════════════════════════════════════════════════
install_prime() {
  section "Prime Agent"
  local settings="$HOME/.prime/agent/settings.json"
  local dir="$HOME/.prime/agent/themes"
  local src_dir="$ROOT/themes/pi"

  # One file set serves both agents. The themes carry all 55 tokens Prime requires;
  # pi ignores the four it does not define (toolPanelBg, toolDiffAddedBg,
  # toolDiffRemovedBg, toolDiffText) because its runtime validator is non-strict.
  # A second themes/prime/ copy existed briefly and differed by exactly one line —
  # the $schema — which is now themes/theme-schema.json, the union of both contracts.
  [[ -d "$src_dir" ]] || fail "themes/pi missing"

  local count=0
  for src in "$src_dir"/*.json; do
    python3 -c "import json; json.load(open('$src'))" 2>/dev/null \
      || fail "Prime theme is invalid JSON: $src"
    if [[ "$DRY" -eq 1 ]]; then
      info "[dry-run] link $(basename "$src") → $dir/"
    else
      mkdir -p "$dir"
      ln -sf "$src" "$dir/$(basename "$src")"
    fi
    count=$((count + 1))
  done
  ok "$count Prime themes linked into $dir (global)"

  local registered
  registered=$(python3 -c "import json;print(json.load(open('$src_dir/$THEME.json'))['name'])")
  if [[ "$registered" != "$THEME" ]]; then
    info "note: $THEME.json registers as \"$registered\" — using that"
  fi

  if [[ -f "$settings" ]] && command -v jq >/dev/null 2>&1; then
    local active
    active=$(jq -r '.theme // ""' "$settings")
    if [[ "$active" != "$registered" ]]; then
      if [[ "$DRY" -eq 0 ]]; then
        cp "$settings" "$settings.bak-$(date +%Y%m%d-%H%M%S)"
        jq --arg t "$registered" '.theme = $t' "$settings" > "${settings}.tmp" \
          && mv "${settings}.tmp" "$settings"
        ok "settings.json theme: \"$active\" → \"$registered\""
      else
        info "[dry-run] settings.json theme: \"$active\" → \"$registered\""
      fi
    else
      ok "settings.json theme already \"$registered\""
    fi
  fi

  echo "  → Restart Prime Agent (or reopen the session) to activate."
}

# ════════════════════════════════════════════════════════════════════════════
# Ghostty
# ════════════════════════════════════════════════════════════════════════════
install_ghostty() {
  section "Ghostty"

  local colours="$ROOT/themes/ghostty/$THEME.conf"
  [[ -f "$colours" ]] || fail "no Ghostty export for $THEME — run: make phosphor-exports"

  # Colours come from the generated export; everything below is personal
  # preference that no palette should own. The two used to be one heredoc here,
  # which meant the installer carried its own copy of the flagship palette.
  local personal
  personal=$(cat << 'GHOSTTY_EOF'

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

  # Two window colours that follow the theme rather than preference: the split
  # divider and the fill behind an unfocused split both read as chrome, so they
  # take the theme's own background.
  local bg
  bg=$(awk '/^background = /{print $3; exit}' "$colours")

  local config
  config="$(cat "$colours")
split-divider-color  = $bg
unfocused-split-fill = $bg
$personal"

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

  local src="$ROOT/themes/iterm2/$THEME.itermcolors"
  local dst="$HOME/Library/Application Support/iTerm2/$THEME.itermcolors"
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
    for f in "$dprofiles"/$THEME.json "$dprofiles"/random-access-theme.json "$dprofiles"/random-access-memories.json; do
      [[ -f "$f" ]] || continue
      mv "$f" "$dprofiles/backups/$(basename "$f").$(date +%Y%m%d-%H%M%S)"
      (( cleared++ )) || true
    done
    [[ "$cleared" -gt 0 ]] && ok "archived $cleared matching dynamic profile(s)" \
                            || ok "no matching dynamic profiles found"
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
  prime)   install_prime ;;
  ghostty) install_ghostty ;;
  iterm2)  install_iterm2 ;;
  all)     install_pi; install_prime; install_ghostty; install_iterm2 ;;
esac

echo ""
echo "Done."
