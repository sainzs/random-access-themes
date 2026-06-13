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

# Use project venv if present, otherwise system python3
PYTHON="$(test -x "$ROOT/.venv/bin/python3" && echo "$ROOT/.venv/bin/python3" || echo python3)"

# ── Parse flags ───────────────────────────────────────────────────────────────
SKIP_GENERATE=0
for arg in "$@"; do
  [[ "$arg" == "--no-generate" ]] && SKIP_GENERATE=1
done

# ── Generate ──────────────────────────────────────────────────────────────────
if [[ "$SKIP_GENERATE" -eq 0 ]]; then
  echo "Generating themes from palette..."
  "$PYTHON" "$ROOT/scripts/generate.py"
  echo ""
fi

echo "Exporting design tokens..."
"$PYTHON" "$ROOT/scripts/export_tokens.py"
echo ""

echo "Rendering README visuals..."
"$PYTHON" "$ROOT/scripts/render_repo_visuals.py"
echo ""

# ── Validate ──────────────────────────────────────────────────────────────────
echo "Validating..."
"$PYTHON" "$ROOT/scripts/validate_theme.py" --skip-installed
echo ""

# ── Package ───────────────────────────────────────────────────────────────────
mkdir -p "$DIST/assets" "$DIST/tokens"
rm -f "$DIST"/*.zip "$DIST"/*.md "$DIST/SHA256SUMS"
rm -f "$DIST/assets"/* "$DIST/tokens"/*

# Copy theme files
cp "$ROOT/themes/pi/random-access-theme.json"               "$DIST/"
cp "$ROOT/themes/alacritty/random-access-theme.toml"        "$DIST/"
cp "$ROOT/themes/ghostty/random-access-theme.conf"          "$DIST/"
cp "$ROOT/themes/kitty/random-access-theme.conf"            "$DIST/random-access-theme-kitty.conf"
cp "$ROOT/themes/wezterm/random-access-theme.toml"          "$DIST/random-access-theme-wezterm.toml"
cp "$ROOT/themes/windows-terminal/random-access-theme.json" "$DIST/random-access-theme-windows-terminal.json"
cp "$ROOT/README.md"                                        "$DIST/"
cp "$ROOT/assets/flavors.svg"                               "$DIST/assets/"
cp "$ROOT/assets/palette-strips.svg"                        "$DIST/assets/"
cp "$ROOT/assets/preview.svg"                               "$DIST/assets/"
cp "$ROOT/assets/preview.png"                               "$DIST/assets/"

# iTerm2 — single .itermcolors file
cp "$ROOT/themes/iterm2/random-access-theme.itermcolors"    "$DIST/"

# Design tokens
cp "$ROOT/tokens/design-tokens.json"                        "$DIST/tokens/"
cp "$ROOT/tokens/random-access-theme.css"                   "$DIST/tokens/"
cp "$ROOT/tokens/tailwind.js"                               "$DIST/tokens/"

# Checksums
echo "Building checksums..."
(
  cd "$DIST"
  find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 shasum -a 256 | sed 's# ./##' > SHA256SUMS
)

echo "Done. Release artifacts:"
ls -1 "$DIST"
