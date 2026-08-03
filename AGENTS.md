# AGENTS.md

## Purpose

Design/theme system generating terminal and editor themes. Two families: six
phosphor tubes, one colour each, whose pi themes are hand-authored and canonical;
and four OLED-black flavors generated from palette YAML. The canonical pipeline/architecture map is `docs/manifest.md` —
read it before changing anything structural; do not restate it here.

**Done and frozen 2026-08-02** (`~/Code/PLAN.md` Phase 5.2): maintenance only — keeping
the existing six tubes and four flavors generating correctly. No new families, no new
flavors, no new output targets.

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
- **There are two pipelines and they run in opposite directions.** The flavors
  generate everything from `palette/*.yaml`. The phosphor family generates its
  terminal exports **from** `themes/pi/reckoner-*.json`, which is hand-authored
  and canonical — `scripts/generate_phosphor.py`, `make phosphor-exports`, and pi
  is deliberately excluded from its output set. Never run the palette pipeline
  over a phosphor theme: it would overwrite the source with a worse derivation.
  Full reasoning in `docs/manifest.md`.
- **The phosphor family sets the standards here and the flavors follow them.**
  The derived thinking ramp and the validator enforcing it both came from those
  six themes. Where the two families disagree, the phosphors are the reference.
- **The thinking ramp is derived, not assigned.** `thinking_ramp()` in
  `scripts/generate.py` interpolates in HSL from the palette's `dimText` to its
  `mint`, holding the accent's hue. Do not go back to naming palette slots: that
  is what produced ramps which fell twice and finished at 89% lightness across
  208° of hue. `validate_thinking_ramps()` rejects it now.
- **`themes/.checksum` holds one line per palette.** It used to hold only the
  palette most recently generated, so building any flavor other than the default
  left `make validate` reporting the default as stale.
- **pi resolves a theme by the `name` inside the JSON, not the filename, and
  fails to `dark` silently.** `initTheme` catches any resolution error and swaps
  in the built-in dark theme with no warning, so an unresolvable name looks
  exactly like a working install of a dark theme. This family has hit it twice:
  `/tone random` asks for `random-access`, which is registered as
  `random-access-theme` (`PLAN.md` task 0), and a `settings.json` holding
  `tokyo-night/reckoner-scope` — a package-qualified form pi does not support —
  which kept every phosphor theme invisible outside one repo. After any install,
  confirm the active name appears in `ls ~/.pi/agent/themes/`. `install.sh` warns
  when a file's name and stem disagree, but nothing can warn about the fallback.
- **`scripts/install.sh` writes to this machine and backs up what it replaces**
  (`~/.config/ghostty/backups/`, `settings.json.bak-<stamp>`). It takes
  `--theme <name>`, links every pi theme rather than one, and reads Ghostty
  colours from `themes/ghostty/<theme>.conf` — never hand-write colours into it
  again; that heredoc was a silent second copy of the flagship palette. Always
  offer `--dry-run` output before running it against someone's config.
- **`make phosphor` uses the system interpreter**, not `.venv`: it needs Pillow
  and nothing else in the pipeline draws raster images. Its footer animation
  frames come from `scripts/footer-frames.json`, a committed snapshot from the
  reckoner package — refresh with `npx tsx scripts/dump-ink-frames.ts` there.
- There is no pytest suite and no linter/formatter configured — correctness
  is enforced by `scripts/validate_theme.py` and `scripts/contrast_matrix.py`.
- Definition of done: `make check` passes (generate + validate + WCAG
  contrast + tokens) — it IS the test suite.
