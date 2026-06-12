#!/usr/bin/env bash
# Build release artifacts for Random Access Theme.
# Outputs to dist/ (gitignored).
#
# Usage:
#   bash scripts/build_release.sh
#   bash scripts/build_release.sh --no-generate   # skip regeneration
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"

# ── Parse flags ───────────────────────────────────────────────────────────────
SKIP_GENERATE=0
for arg in "$@"; do
  [[ "$arg" == "--no-generate" ]] && SKIP_GENERATE=1
done

# ── Generate ──────────────────────────────────────────────────────────────────
if [[ "$SKIP_GENERATE" -eq 0 ]]; then
  echo "Generating themes from palette..."
  python3 "$ROOT/scripts/generate.py"
  echo ""
fi

# ── Validate ──────────────────────────────────────────────────────────────────
echo "Validating..."
python3 "$ROOT/scripts/validate_theme.py" --skip-installed
echo ""

# ── Package ───────────────────────────────────────────────────────────────────
mkdir -p "$DIST"
rm -f "$DIST"/*.zip "$DIST"/*.json "$DIST"/*.md "$DIST/SHA256SUMS"

# Copy theme files
cp "$ROOT/themes/pi/random-access-theme.json"               "$DIST/"
cp "$ROOT/themes/alacritty/random-access-theme.toml"        "$DIST/"
cp "$ROOT/themes/ghostty/random-access-theme.conf"          "$DIST/"
cp "$ROOT/themes/kitty/random-access-theme.conf"            "$DIST/random-access-theme-kitty.conf"
cp "$ROOT/themes/wezterm/random-access-theme.toml"          "$DIST/random-access-theme-wezterm.toml"
cp "$ROOT/themes/windows-terminal/random-access-theme.json" "$DIST/random-access-theme-windows-terminal.json"
cp "$ROOT/README.md"                                        "$DIST/"

# iTerm2 — single .itermcolors file
cp "$ROOT/themes/iterm2/random-access-theme.itermcolors"    "$DIST/"

# Checksums
echo "Building checksums..."
(
  cd "$DIST"
  shasum -a 256 * > SHA256SUMS
)

echo "Done. Release artifacts:"
ls -1 "$DIST"
