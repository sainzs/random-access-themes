# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
