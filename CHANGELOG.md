# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
- Generated README visuals: `assets/flavors.svg` and `assets/palette-strips.svg`
- Visual renderer: `scripts/render_repo_visuals.py`
- `make visuals` target for regenerating repo presentation assets

### Changed

- Pi family consolidated to nine keepers. Seven hue-duplicates / broken themes
  archived to `archive/themes/pi/`: amnesiac, anochecer, atardecer, madrugada,
  ocaso, veridis, voyager. `themes/pi/index.txt` lists the nine.
- amanecer and mediodia brought up to the contract (canonical skeleton, five
  empty color values wired, `paDim` added). reckoner-factory `border0/1` renamed
  to `bg3`/`line`. reckoner-dusk gained `paDim`.
- `scripts/validate_theme.py` no longer treats empty-string color values as valid.
- `toolPendingBg`, `toolSuccessBg` and `toolErrorBg` no longer all resolve to the
  background, so a tool call now shows its state; diff rows read green and red
  even where the palette names no red
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
