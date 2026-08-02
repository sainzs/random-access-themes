# AGENTS.md

## Purpose

Design/theme system generating terminal and editor themes from palette
sources. The canonical pipeline/architecture map is `docs/manifest.md` —
read it before changing anything structural; do not restate it here.

## Commands

Requirements: Python 3.9+, `pyyaml`. Uses project `.venv/bin/python3` if
present, else system `python3` (see Makefile).

```bash
make generate    # Regenerate terminal theme exports from palette YAML
make visuals     # Regenerate README SVG visuals
make tokens      # Regenerate design tokens in tokens/
make validate    # Structural + freshness + drift validation
make contrast    # Full WCAG contrast report
make check       # generate + validate + contrast + tokens — run before committing
make release     # Build release artifacts into dist/
make install     # Install Pi theme locally
make clean       # rm -rf dist/
make             # default: generate + validate
```

Scripts can be invoked directly, e.g.
`python3 scripts/generate.py --palette palette/random-access-theme.yaml --dry-run`.

## Gotchas

- **Palette-first:** hand-edit only `palette/*.yaml`. Generated outputs
  (`themes/{alacritty,ghostty,iterm2,kitty,pi,wezterm,windows-terminal}/`,
  `tokens/`, `assets/` visuals) are produced by the pipeline — change them
  by regenerating, never by hand.
- Curated hand-authored exceptions: `integrations/`,
  `themes/{vscode,sublime,zed,neovim,opencode}/`.
- There is no pytest suite and no linter/formatter configured — correctness
  is enforced by `scripts/validate_theme.py` and `scripts/contrast_matrix.py`.
- Definition of done: `make check` passes (generate + validate + WCAG
  contrast + tokens) — it IS the test suite.
