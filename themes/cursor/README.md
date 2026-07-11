# Random Access Theme — Cursor

Cursor uses VS Code's theme engine directly, so these files are identical copies of the
`themes/vscode/` color-theme JSONs. No conversion or extra packaging is needed.

## Installation

1. Copy the desired `*-color-theme.json` file into your Cursor extensions or themes folder, or
   reference it from an extension `package.json`.
2. Open **Command Palette** → **Preferences: Color Theme** and select the theme.

## Flavors

| File | Flavor |
|------|--------|
| `random-access-color-theme.json` | Random Access — OLED black, electric mint |
| `veridis-color-theme.json`       | Veridis — warm black, electric mint |
| `voyager-color-theme.json`       | Voyager — warm black, vibrant teal |
| `amnesiac-color-theme.json`      | Amnesiac — warm black, vibrant indigo |

## Source

Colors are derived from the canonical palette YAMLs in `palette/`. The theme JSON files are
generated/maintained alongside the VS Code port in `themes/vscode/` — update them there and
re-copy here.
