# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- **Flavor ANSI ramps rebuilt to the phosphor standard (0.1.1 → 0.2.0, all four
  flavors).** The generated 16-color ramps had flattened every slot into the
  accent family with no luminance structure — aerodynamic's red slot was
  emerald, voyager's dark teal, amnesiac's indigo, veridis's dark mint, and
  aerodynamic duplicated `bright.red`/`bright.blue` (#00ffb2 in both). Each
  flavor now follows the phosphor-tube pattern the repo standardizes on: one
  identity hue in luminance steps (deep / base / hero / soft / pale), plus the
  shared warm signal pair — LED red-orange `#ff7a5c` and phosphor amber
  `#e8c878` — for red and yellow slots. aerodynamic reads as green phosphor,
  veridis as P1 handheld, amnesiac as blue-white CRT, voyager as cyan CRT on
  warm black. UI accent families and thinking ramps are untouched: this fixes
  terminal semantics, not palette identity.

### Added

- Pi package contract: `themes/pi/THEMES.md`, `validate_themes.py`,
  `render_preview.py`. Distilled from reckoner-exect. Enforced by
  `python3 themes/pi/validate_themes.py --strict`.
- `pi_skeleton()` in `scripts/generate.py` — every generated pi theme now emits
  the contract ladder (`bg0`–`bg3`, `line`, `muted0/1`, `text0/1`, `paDim`)
  derived from the flavor's own ramp, calibrated against reckoner-exect.
- Prime Agent support: `themes/theme-schema.json`, the union of pi's and Prime's
  contracts, and `bash scripts/install.sh prime`. One file set serves both agents
- Agent surfaces in every pi theme — `toolPanelBg`, `toolDiffAddedBg`,
  `toolDiffRemovedBg`, `toolDiffText`, and dedicated tool, selection and message
  beds — derived in `pi_surfaces()` for the flavors and hand-held for the rest
- **OpenCode and Zed editor themes for all ten themes** — the four flavors
  (palette-driven via new `gen_opencode`/`gen_zed` in `scripts/generate.py`) and
  the six phosphor tubes (via `scripts/generate_phosphor.py`). `themes/opencode/`
  and `themes/zed/` are now generated, not curated. Diff backgrounds added to each
  palette (`diffAddBg`/`diffRemBg`); phosphor diff rows are tinted toward each
  tube's own add/remove signals.
- Generated README visuals: `assets/flavors.svg` and `assets/palette-strips.svg`
- Visual renderer: `scripts/render_repo_visuals.py`
- `make visuals` target for regenerating repo presentation assets

### Changed

- Pi family consolidated to nine keepers. Seven hue-duplicates / broken themes
  archived to `archive/themes/pi/`: amnesiac, anochecer, atardecer, madrugada,
  ocaso, veridis, voyager. `themes/pi/index.txt` lists the nine.
- README rebuilt around the nine: cinta GIFs for validate and install, keeper
  cards in `assets/pi/`, dead day-cycle / sixteen-theme claims removed.
- `scripts/get.sh` pi target no longer suggests the archived `mediodia/anochecer` pair.
- amanecer and mediodia brought up to the contract (canonical skeleton, five
  empty color values wired, `paDim` added). reckoner-factory `border0/1` renamed
  to `bg3`/`line`. reckoner-dusk gained `paDim`.
- `scripts/validate_theme.py` no longer treats empty-string color values as valid.
- `toolPendingBg`, `toolSuccessBg` and `toolErrorBg` no longer all resolve to the
  background, so a tool call now shows its state; diff rows read green and red
  even where the palette names no red
- **Ghostty exports carry their own split chrome.** `themes/ghostty/*.conf` now
  ship `split-divider-color` and `unfocused-split-fill`, both set to the theme's
  background. They used to be written into the user's main config (by hand or by
  `install.sh` awk-ing them out of the export), and Ghostty's main config always
  overrides theme files — so a divider hardcoded there followed no theme but the
  one it was written for. Each export now also emits `cursor-text` with single
  spaces around the `=`.
- **Renamed the flagship flavor** `random-access-theme` → `aerodynamic` (Daft Punk,
  *Aerodynamic*, Discovery 2001) so the theme sits beside `veridis`, `voyager`, and
  `amnesiac` as a single-word album/song name, and stops colliding with the bundle
  name. Palette file is now `palette/aerodynamic-theme.yaml`; all generated exports,
  tokens, and docs updated.
- **Renamed the bundle** to Random Access Themes (`random-access-themes`), matching
  the GitHub repo; Python package name follows.
>>>>>>> 5c2773d (Regenerate theme system: flagship rename, phosphor-standard flavor ANSI)
- README refreshed with a stronger visual hierarchy, hero gallery, and palette overview
- Release packaging now includes README SVG assets used by the repo landing page
- Contributing guide updated to document generated visuals and palette-driven workflow

## [0.1.0] - 2026-03-23

### Added

- Canonical palette definitions for 4 flavors:
  - `palette/random-access-theme.yaml` (flagship — Daft Punk, *Random Access Memories*)
  - `palette/veridis-theme.yaml` (Daft Punk, *Veridis Quo*)
  - `palette/voyager-theme.yaml` (Daft Punk, *Voyager*)
  - `palette/amnesiac-theme.yaml` (Radiohead, *Amnesiac*)
- Generator: `scripts/generate.py` — produces all terminal exports from palette
- WCAG contrast matrix: `scripts/contrast_matrix.py`
- Structural validator: `scripts/validate_theme.py`
- Release packager: `scripts/build_release.sh`
- Install script: `scripts/install.sh` (Ghostty, iTerm2, Pi)
- CI: `.github/workflows/validate.yml` (generate + validate + contrast check)
- Design document: `docs/design.md`
- MIT license

### Terminal themes (all generated from palette YAML)

- Ghostty, WezTerm, iTerm2, Alacritty, kitty, Windows Terminal, Pi
- All 4 flavors supported across all 7 terminals (28 theme files)

### Editor themes

- VS Code: Veridis color theme
- Sublime Text: Veridis color scheme + settings
- Zed: Veridis theme
- Neovim: Veridis colorscheme (Lua)

### Integrations

- tmux status bar config
- fzf color export
- bat syntax theme config
- delta (git diff) colors
- Starship prompt config
- eza color export

### Removed

- Third-party `.terminal` profile bundle (not original work)
- Standalone root `random-access-theme.json` (superseded by `themes/pi/`)
