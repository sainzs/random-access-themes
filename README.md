# Random Access Themes

[![CI](https://github.com/ssainz/random-access-themes/actions/workflows/validate.yml/badge.svg)](https://github.com/ssainz/random-access-themes/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-00ffb2.svg)](LICENSE)

> OLED-black dark themes for terminals and editors. Named after Daft Punk and Radiohead deep cuts.

![Random Access Themes preview](assets/preview.png)

---

## Flavors

Four variants, one philosophy — every accent lives in the cool spectrum.

| Flavor | Named after | Accent | Background | Description |
|--------|-------------|--------|------------|-------------|
| **Random Access** | Daft Punk — *Random Access Memories* | `#00ffb2` mint | `#000000` cool black | Flagship. Green-family syntax, no warm hues at all |
| **Veridis** | Daft Punk — *Veridis Quo* | `#00ffb2` mint | `#0f0e0d` warm black | Warm-dark base, electric mint accent |
| **Voyager** | Daft Punk — *Voyager* | `#2ccfc0` teal | `#0f0e0d` warm black | Warm-dark base, vibrant electric teal |
| **Amnesiac** | Radiohead — *Amnesiac* | `#7b93ff` indigo | `#0f0e0d` warm black | Warm-dark base, cool indigo accent |

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

Random Access flagship palette — all colors green-family, zero warm hues.

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

All foreground colors pass **WCAG AA** against `#000000`. Most reach **AAA**. See the full design rationale in [docs/design.md](docs/design.md).

---

## Development

**Requirements:** Python 3.9+, `pyyaml`

```bash
pip install pyyaml
```

| Command | What it does |
|---------|-------------|
| `make generate` | Regenerate all themes from palette YAML |
| `make validate` | Structural + freshness + drift checks |
| `make contrast` | Full WCAG contrast report |
| `make check` | All of the above |
| `make release` | Build release artifacts to `dist/` |

Each flavor has its own palette file in `palette/`. Edit the YAML, then `make generate` to propagate.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The only files that should be edited manually are the palette YAML files in `palette/`. Everything in `themes/` is generated.

## License

[MIT](LICENSE)
