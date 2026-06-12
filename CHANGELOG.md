# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Canonical palette definition: `palette/random-access-theme.yaml`
- Generator: `scripts/generate.py` — produces all terminal exports from palette
- WCAG contrast matrix: `scripts/contrast_matrix.py`
- Structural validator: `scripts/validate_theme.py`
- Release packager: `scripts/build_release.sh`
- CI: `.github/workflows/validate.yml` (generate + validate + contrast check)
- Design document: `docs/design.md`
- MIT license

### Themes (all generated from canonical palette)

- Ghostty: `themes/ghostty/random-access-theme.conf`
- WezTerm: `themes/wezterm/random-access-theme.toml`
- iTerm2: `themes/iterm2/random-access-theme.itermcolors`
- Alacritty: `themes/alacritty/random-access-theme.toml`
- kitty: `themes/kitty/random-access-theme.conf`
- Windows Terminal: `themes/windows-terminal/random-access-theme.json`
- Pi: `themes/pi/random-access-theme.json`

### Removed

- Third-party `.terminal` profile bundle (not original work)
- Standalone root `random-access-theme.json` (superseded by `themes/pi/`)
