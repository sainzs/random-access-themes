# terminal-theme — Matte Black HC

Lives at `integrations/terminal-theme/` in the random-access-themes package; the
operator's `~/.config/terminal-theme` is a symlink here (or set `RAT_REPO`).
Accents are read from `themes/pi/*.json` (`accent_from` in theme.toml). Python 3.11+.

One palette for Ghostty, kitty, iTerm2, Warp and the shell layer. Omarchy
Matte Black lineage (charcoal `#121212`; amber upstream, replaced here by the
reckoner greens), contrast lifted so every text role clears WCAG AA on the
glass-composited background.

```
theme.toml            source of truth (palette, glass, fonts, per-terminal accents)
bin/render-theme      theme.toml → native theme files (see list below)
bin/check-contrast    WCAG (solid/grey-glass/white-glass) + ΔE76 separation; exit 1 on failure
bin/theme-check       runs EVERY gate below in one go — run after any edit
bin/winid.swift       CGWindowID helper for `screencapture -l` (build: `swiftc -O bin/winid.swift -o bin/winid`)
backups/<stamp>/      every file a render replaced + rollback.sh (`backups/latest` → newest)
plans/modernize.md    the plan and gate log
```

## Where the accent lives

Each terminal gets its own accent in **ANSI slot 4/12 (blue)** of its theme —
the four greens of the pi *reckoner* theme package: Ghostty scope phosphor
`#6fe392` · kitty aerodynamic mint `#00ffb2` · iTerm2 darkspace teal `#3ce6da`
· Warp exect phosGreen `#9acc63`. Semantic green is a muted sage so success
never impersonates the accent (gated by ΔE ≥ 25). The shell layer
(starship, zsh-syntax-highlighting, fzf, eza, tmux) only ever says `blue`,
so one `~/.config/starship.toml` and one `.zshrc` block serve all four.

## Generated files (do not edit — edit theme.toml, run render-theme)

- `~/.config/ghostty/themes/Matte Black HC`
- `~/.config/kitty/matte-black-hc.conf` (kitty.conf `include`s it)
- `~/Library/Application Support/iTerm2/DynamicProfiles/matte-black-hc.json`
  (inherits keybindings etc. from profile "Default"; set as default profile)
- `~/.warp/themes/matte-black-hc.yaml`
- `~/.config/shell/palette.sh` (`TERMINAL_*` roles, sourced by shell/env.sh)
- `palette.json`

## Glass

| app | setting |
|-----|---------|
| Ghostty | `background-opacity 0.88`, `background-blur macos-glass-regular` (native Liquid Glass, macOS 26) |
| kitty | `background_opacity 0.88`, `background_blur 24`; **Cmd+Shift+G** solid, **Cmd+Shift+Alt+G** glass |
| iTerm2 | Transparency 0.12, Blur radius 24, only default bg is transparent |
| Warp | `override_opacity 88`, `override_blur 24` |

## Motion

- Ghostty: chained shaders `cursor-trail.glsl` (smear in cursor colour on jumps)
  and `focus-glow.glsl` (bloom on focus gain, frost while unfocused), both
  compiled with glslang; `bell-features attention,title,border`; quick-terminal
  slide; resize overlay.
- kitty: `cursor_trail 1` (mint), 80 ms accent bell flash, powerline tabs.
- iTerm2: cursor shadow + boost, blur. Warp: native. (Neither exposes shaders.)

## Fonts

Berkeley Mono Variable (Light / Retina) with BerkeleyMono Nerd Font as symbol
fallback. JetBrainsMono Nerd Font is installed as the Omarchy-faithful
alternate — swap `font-family` / `font_family` / profile font by hand.

## Reload

Ghostty **Cmd+Shift+,** · kitty auto-reloads (or Cmd+Shift+R) · iTerm2 and
Warp: relaunch. New shells pick up `palette.sh` and `starship.toml`.

## Shell extras on the same palette

`bat --theme=ansi`, `delta` ANSI syntax theme with accent file headers, `man`
through bat, fzf Ctrl-T/Alt-C/Ctrl-R previews (bat / eza tree / history), eza
directories-first, zsh completion menu colours. All ANSI-slot based.

## pi (reckoner) themes

pi draws prose on the terminal surface and only paints panels, so every dark
reckoner theme's `pa*` set is now derived against `#121212`
(`themes/pi/derive_panels.py`; rule recorded in THEMES.md). Rerun it
if `base.background` changes here.

## Gates (`bin/theme-check` runs them all)

`bin/check-contrast` (WCAG on solid/grey-glass/white-glass + ΔE76 separation) ·
`ghostty +validate-config` + `+show-config | grep -c custom-shader` (=2, no
double load) · glslang on both shaders · kitty `load_config(accumulate_bad_lines)`
· `jq` on the iTerm2 profile · `yq` on the Warp yaml · `starship print-config` ·
`~/.pi/agent/themes/validate_themes.py --strict`.

## Rollback

`backups/latest/rollback.sh` undoes the most recent render (local, gitignored).
The original 2026-09-03 migration snapshot is `backup-20260903-1723/rollback.sh`.
