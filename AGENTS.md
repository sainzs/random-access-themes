# AGENTS.md

## Purpose

Design/theme system generating terminal and editor themes. Three families: six
phosphor tubes, one colour each, whose pi themes are hand-authored and canonical;
four OLED-black flavors generated from palette YAML; and the five-theme day
cycle, hand-held ports of upstream palettes with no exports of their own. The canonical pipeline/architecture map is `docs/manifest.md` —
read it before changing anything structural; do not restate it here.

**Frozen 2026-08-02, reopened once** (`~/Code/PLAN.md` Phase 5.2). The freeze
still holds for the tubes and the flavors: maintenance only, no new flavors, no
new output targets. The day cycle was folded in afterwards on the owner's
instruction, consolidating what had been a second theme repo; that is the one
exception, and it is not a precedent for a fourth family.

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

- **The five day-cycle themes are ports; their colours are not ours to tune.**
  `themes/pi/{madrugada,amanecer,atardecer,ocaso,anochecer}.json` reproduce
  upstream palettes byte for byte. Never run the palette pipeline over them and
  never "fix" a colour to match house contrast — the fidelity is the point. Only
  the six `thinking*` values are ours, rebuilt because pi's ramp is not a concept
  those projects define. `madrugada` is **Apache-2.0** (Tokyo Night), so any
  change to it must be recorded in `NOTICE` under section 4(b); the other three
  are MIT.

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
  `random-access-theme` (`PLAN.md` task 0). A second value, a `settings.json`
  holding `tokyo-night/reckoner-scope`, was recorded here as a package-qualified
  form pi does not support. It is not — verified against pi 0.83.0: a single
  slash is pi's light/dark pair syntax, so that value resolves to `tokyo-night`
  on a light terminal and `reckoner-scope` on a dark one. It never hit the
  fallback. What pi rejects is two or more slashes, which make
  `resolveThemeSetting` return `undefined`; that is the form to avoid. After any install,
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
