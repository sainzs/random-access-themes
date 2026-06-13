# Random Access Themes

[![CI](https://github.com/sainzs/random-access-themes/actions/workflows/validate.yml/badge.svg)](https://github.com/sainzs/random-access-themes/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-00ffb2.svg)](LICENSE)
[![Release](https://img.shields.io/badge/release-v0.1.2-00ffb2.svg)](https://github.com/sainzs/random-access-themes/releases)

> OLED-black dark themes for terminals and editors — four flavors, zero warm syntax hues.

![Random Access Themes flavor gallery](assets/flavors.svg)

**At a glance**
- 4 flavors: **Random Access**, **Veridis**, **Voyager**, **Amnesiac**
- 7 terminal ports per flavor: Ghostty, WezTerm, iTerm2, Alacritty, kitty, Windows Terminal, Pi
- Editor ports today: VS Code, Sublime Text, Zed, Neovim (**Veridis**)
- Palette-first workflow: edit YAML, regenerate themes, validate contrast

![Random Access Themes palette strips](assets/palette-strips.svg)

See the [demo preview](docs/demo.md) for the flagship terminal render and
rebuild commands.

---

## Flavors

Four variants, one philosophy: dark surfaces, restrained UI chrome, and a cool-spectrum accent family.

| Flavor | Named after | Accent | Background | Description |
|--------|-------------|--------|------------|-------------|
| **Random Access** | Daft Punk — *Random Access Memories* | `#00ffb2` mint | `#000000` pure OLED black | Flagship. Mint-forward, green-family syntax, zero warm hues |
| **Veridis** | Daft Punk — *Veridis Quo* | `#00ffb2` mint | `#0f0e0d` warm black | Warm-dark base with crisp cream text and electric mint |
| **Voyager** | Daft Punk — *Voyager* | `#2ccfc0` teal | `#0f0e0d` warm black | Warm-dark base with a brighter teal-led accent family |
| **Amnesiac** | Radiohead — *Amnesiac* | `#7b93ff` indigo | `#0f0e0d` warm black | Warm-dark base with cool indigo contrast and sharper separation |

---

## Why it looks different

Most dark themes spread warm accents across the screen. Random Access Themes deliberately compress the visual range:
- **dark surfaces stay dark**
- **syntax lives in a tight accent family**
- **text stays high-contrast and calm**
- **WCAG contrast is treated as a hard requirement, not a nice-to-have**

The flagship Random Access palette reaches **17.44:1** text/background contrast and every foreground color clears **WCAG AA** against the base background.

See the full rationale in [docs/design.md](docs/design.md).

---

## Supported Ports

### Terminals

| Terminal | Random Access | Veridis | Voyager | Amnesiac |
|----------|:---:|:---:|:---:|:---:|
| Ghostty | [conf](themes/ghostty/random-access-theme.conf) | [conf](themes/ghostty/veridis.conf) | [conf](themes/ghostty/voyager.conf) | [conf](themes/ghostty/amnesiac.conf) |
| WezTerm | [toml](themes/wezterm/random-access-theme.toml) | [toml](themes/wezterm/veridis.toml) | [toml](themes/wezterm/voyager.toml) | [toml](themes/wezterm/amnesiac.toml) |
| iTerm2 | [itermcolors](themes/iterm2/random-access-theme.itermcolors) | [itermcolors](themes/iterm2/veridis.itermcolors) | [itermcolors](themes/iterm2/voyager.itermcolors) | [itermcolors](themes/iterm2/amnesiac.itermcolors) |
| Alacritty | [toml](themes/alacritty/random-access-theme.toml) | [toml](themes/alacritty/veridis.toml) | [toml](themes/alacritty/voyager.toml) | [toml](themes/alacritty/amnesiac.toml) |
| kitty | [conf](themes/kitty/random-access-theme.conf) | [conf](themes/kitty/veridis.conf) | [conf](themes/kitty/voyager.conf) | [conf](themes/kitty/amnesiac.conf) |
| Windows Terminal | [json](themes/windows-terminal/random-access-theme.json) | [json](themes/windows-terminal/veridis.json) | [json](themes/windows-terminal/voyager.json) | [json](themes/windows-terminal/amnesiac.json) |
| Pi | [json](themes/pi/random-access-theme.json) | [json](themes/pi/veridis.json) | [json](themes/pi/voyager.json) | [json](themes/pi/amnesiac.json) |

### Editors

| Editor | Flavor |
|--------|--------|
| VS Code | [Veridis](themes/vscode/veridis-color-theme.json) |
| Sublime Text | [Veridis](themes/sublime/veridis.sublime-color-scheme) |
| Zed | [Veridis](themes/zed/veridis.json) |
| Neovim | [Veridis](themes/neovim/veridis.lua) |

---

## Install

### One-line install (no clone)

Fetch a generated theme straight to its standard location — no clone, no Python, no build step:

```bash
curl -fsSL https://raw.githubusercontent.com/sainzs/random-access-themes/main/scripts/get.sh | bash -s -- ghostty
```

Targets: `alacritty` · `wezterm` · `ghostty` · `kitty` · `iterm2` · `windows-terminal` · `pi` · `all`. Add `--dry-run` to preview, or pin a release with `RAT_REF=v0.1.2`. Existing files are backed up before they are overwritten. See [`scripts/get.sh`](scripts/get.sh).

### From a clone

### Ghostty

```bash
bash scripts/install.sh ghostty
```

Writes the full config to `~/.config/ghostty/config` and stubs the macOS Library config to prevent duplicate entries.

### WezTerm

```bash
cp themes/wezterm/random-access-theme.toml ~/.config/wezterm/colors/
```

Then in `wezterm.lua`:

```lua
config.color_scheme = "Random Access Theme"
```

### iTerm2

```bash
bash scripts/install.sh iterm2
```

Then: **Profiles > Colors > Color Presets > Import** and select the `.itermcolors` file.

### Alacritty

```toml
# In alacritty.toml
[import]
paths = ["/path/to/themes/alacritty/random-access-theme.toml"]
```

### kitty

```bash
echo "include /path/to/themes/kitty/random-access-theme.conf" >> ~/.config/kitty/kitty.conf
```

### Windows Terminal

Add the scheme from `themes/windows-terminal/random-access-theme.json` into the `"schemes"` array in your settings JSON.

### Pi

```bash
cp themes/pi/random-access-theme.json ~/.pi/agent/themes/
```

Then: `/settings` > select `random-access-theme` > `/reload`

---

## Integrations

Bonus configs for tools that inherit ANSI colors or benefit from explicit theming:

| Tool | File | What it does |
|------|------|-------------|
| tmux | [`integrations/tmux.conf`](integrations/tmux.conf) | Status bar and pane border colors |
| fzf | [`integrations/fzf-export.sh`](integrations/fzf-export.sh) | `FZF_DEFAULT_OPTS` color env vars |
| bat | [`integrations/bat-config`](integrations/bat-config) | Syntax highlighting theme |
| delta | [`integrations/gitconfig-delta`](integrations/gitconfig-delta) | Git diff colors |
| Starship | [`integrations/starship.toml`](integrations/starship.toml) | Prompt styling |
| eza | [`integrations/eza-export.sh`](integrations/eza-export.sh) | `EZA_COLORS` env vars |

---

## Palette

Flagship Random Access palette — all colors stay in a green-family range, including ANSI remaps.

| Role | Hex | Purpose |
|------|-----|---------|
| bg | `#000000` | Pure OLED black |
| text | `#d8efe9` | Primary text — green-tinted near-white |
| subtle | `#9cb7af` | Secondary text, labels |
| dimText | `#6f8d86` | Comments, disabled |
| mint | `#00ffb2` | Hero accent, cursor |
| green | `#4ade80` | Functions, success |
| teal | `#35d5c5` | Quotes, borders |
| jade | `#66e3c4` | Keywords |
| aqua | `#8bf5dd` | Numbers, highlights |
| emerald | `#26c994` | Errors (no warm red) |
| lime | `#a2e5b8` | Strings, warnings |

All foreground colors pass **WCAG AA** against `#000000`. Most reach **AAA**.

---

## Development

**Requirements:** Python 3.9+, `pyyaml`

```bash
pip install pyyaml
```

| Command | What it does |
|---------|-------------|
| `make generate` | Regenerate terminal themes from palette YAML |
| `make visuals` | Regenerate README SVG visuals from palette YAML |
| `make validate` | Structural + freshness + drift checks |
| `make contrast` | Full WCAG contrast report |
| `make check` | Generate + validate + contrast |
| `make release` | Build release artifacts to `dist/` |

The source-of-truth map lives in [docs/manifest.md](docs/manifest.md), and the
public preview flow is documented in [docs/demo.md](docs/demo.md).

Each flavor has its own palette file in `palette/`. Edit the YAML, then regenerate the assets you changed.

README visuals in `assets/*.svg` are generated by [`scripts/render_repo_visuals.py`](scripts/render_repo_visuals.py).

---

## Design Tokens

The canonical palette is also exported as reusable design tokens for web and UI projects:

| Artifact | Path | Use case |
| --- | --- | --- |
| W3C-style tokens | `tokens/design-tokens.json` | All four flavors in one importable file |
| CSS variables | `tokens/random-access-theme.css` | Web projects using the flagship palette |
| Tailwind config | `tokens/tailwind.js` | Tailwind `extend colors` snippet |

Run `make tokens` to regenerate them after editing a palette.

## Portfolio

random-access-themes is the **design system** of the Random Access agent toolchain — four small packages that compose into one maintainer surface:

| Package | Layer | What it does |
| --- | --- | --- |
| [santiagosainz-skills](https://github.com/sainzs/santiagosainz-skills) | Workflow | Portable maintainer skills: review, planning, debug, verify, handoff |
| [reckoner](https://github.com/sainzs/reckoner) | Memory | Agent memory, auto-verification, and guardrails |
| [registro](https://github.com/sainzs/registro) | Reporting | Agent work report CLI and dashboard |
| **random-access-themes** | Design system | OLED-black themes and tokens shared across the toolchain |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The only files that should be edited manually are the palette YAML files in `palette/` plus repo docs / scripts. Theme files in `themes/` and README SVGs in `assets/` are generated.

## License

[MIT](LICENSE)
