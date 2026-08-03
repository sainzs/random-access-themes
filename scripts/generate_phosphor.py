#!/usr/bin/env python3
"""
Generate terminal exports for the phosphor family.

The pipeline runs the other way round here, and deliberately.

Everywhere else in this repo a palette YAML is the source of truth and every
export — including the pi theme — is derived from it. The six phosphor themes
arrived already finished: hand-tuned against a real harness, with a thinking ramp
rebuilt in HSL and a brightness ladder that is the whole point of them. Feeding
them through a generator built to spread a cool-spectrum accent family across
four flavors would have produced something worse and called it canonical.

So `themes/pi/reckoner-*.json` **is** the source of truth for these six, and this
script derives the terminal exports from it by reusing the same generator
functions the palettes use. Nothing here can change a pi theme; pi is excluded
from the output set on purpose.

A monochrome tube has no accent family to map, which sounds like a problem and is
actually the philosophy: the eight accent slots collapse onto the theme's own
brightness ladder, because that is how the hardware built hierarchy. The ANSI
sixteen are the same ladder, with the three signal colours — success, warning,
error — kept as themselves so `ls`, `git` and diffs still mean something.

Run:  make phosphor-exports
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from generate import (  # noqa: E402  — same directory, deliberate
    gen_alacritty,
    gen_ghostty,
    gen_iterm2,
    gen_kitty,
    gen_wezterm,
    gen_windows_terminal,
)

ROOT = Path(__file__).parent.parent
PI_DIR = ROOT / "themes" / "pi"
THEMES_DIR = ROOT / "themes"

# pi is absent by design: it is the input, not an output.
OUTPUTS = {
    "ghostty": (gen_ghostty, "ghostty/{name}.conf"),
    "wezterm": (gen_wezterm, "wezterm/{name}.toml"),
    "iterm2": (gen_iterm2, "iterm2/{name}.itermcolors"),
    "alacritty": (gen_alacritty, "alacritty/{name}.toml"),
    "kitty": (gen_kitty, "kitty/{name}.conf"),
    "windows-terminal": (gen_windows_terminal, "windows-terminal/{name}.json"),
}

# What each tube is, for the export headers. The pi themes carry no prose.
#
# The display name is not decoration: WezTerm selects a scheme by this exact
# string and Windows Terminal shows it in a dropdown, both in a namespace shared
# with every other scheme the user has installed. The first version used bare
# words — Scope, Dusk, Factory — which said nothing about where they came from and
# would sit in that list waiting to collide with someone else's Dusk. They carry
# the family now, matching the pi theme ids they are generated from.
#
# The descriptions for dusk and factory used to say what those two are not ("the
# one that is not a tube"). That reads fine in a design note where the contrast is
# the point and badly as the one line a stranger meets at the top of a config
# file.
TUBES = {
    "reckoner-exect": ("Reckoner EXECT", "EXECT-100 / DEC VT520 — amber phosphor on warm near-black."),
    "reckoner-scope": ("Reckoner Scope", "DEC VT640 radar — P1 green on green glass."),
    "reckoner-wopr": ("Reckoner WOPR", "VT100 blue screen — cyan and white-blue, the war room."),
    "reckoner-darkspace": ("Reckoner Darkspace", "dark.spaceAMP — teal wireframe on blackest glass."),
    "reckoner-dusk": ("Reckoner Dusk", "Violet on blue-black — late light, cold screen."),
    "reckoner-factory": ("Reckoner Factory", "Safety orange on true black — machine-shop signage under work lights."),
}


def resolve(theme: dict, key: str) -> str:
    """Follow a colour through `vars` until it is a hex value."""
    value = theme.get("colors", {}).get(key, key)
    for _ in range(5):
        if isinstance(value, str) and value.startswith("#"):
            return value
        variables = theme.get("vars", {})
        value = variables.get(value, theme.get("colors", {}).get(value))
        if value is None:
            break
    raise SystemExit(f"{theme.get('name')}: cannot resolve colour {key!r}")


def as_palette(theme: dict) -> dict:
    """
    Shape a phosphor pi theme like a palette, so the existing generators work.

    The accent slots are not eight colours here, they are eight rungs of one. A
    real tube could not do otherwise, and pretending it could is what would make
    these themes look like everything else.
    """
    dim = resolve(theme, "dim")
    muted = resolve(theme, "muted")
    text = resolve(theme, "text")
    accent = resolve(theme, "accent")
    peak = resolve(theme, "mdHeading")
    variables = theme.get("vars", {})
    background = theme.get("colors", {}).get("background") or variables.get("bg0") or variables.get("bg")
    if not isinstance(background, str) or not background.startswith("#"):
        background = variables.get(background, "#000000")

    return {
        "bg": background,
        "bg1": resolve(theme, "selectedBg"),
        "bg2": resolve(theme, "border"),
        "surface": background,
        "overlay": resolve(theme, "selectedBg"),
        "text": text,
        "subtle": muted,
        "dimText": dim,
        "cursor": accent,
        # The ladder, brightest first where the slot wants brightness.
        "mint": accent,
        "cyan": accent,
        "green": resolve(theme, "success"),
        "teal": muted,
        "jade": resolve(theme, "thinkingXhigh"),
        "aqua": peak,
        "emerald": resolve(theme, "error"),
        "lime": resolve(theme, "warning"),
    }


def as_ansi(theme: dict, palette: dict) -> dict:
    """
    The sixteen, as a brightness ladder with the signals left intact.

    Red, green and yellow keep their meanings — a diff that cannot show a
    deletion is not a saving — and everything else steps up the phosphor.

    Every slot except black lands on a rung that is legible against the
    background. The first version spent `dim` on normal magenta, which put it at
    1.2:1 on all six themes: `dim` is chrome, sized for separators and silkscreen
    labels, and any tool that colours real output magenta would have written it in
    invisible ink. Black stays low on purpose — it is the background's own step,
    and every flavor in this repo does the same.
    """
    return {
        "normal": {
            "black": palette["bg1"],
            "red": palette["emerald"],
            "green": palette["green"],
            "yellow": palette["lime"],
            "blue": palette["subtle"],
            "magenta": palette["text"],
            "cyan": palette["cursor"],
            "white": palette["text"],
        },
        "bright": {
            "black": palette["dimText"],
            "red": palette["emerald"],
            "green": palette["green"],
            "yellow": palette["lime"],
            "blue": palette["cursor"],
            "magenta": palette["aqua"],
            "cyan": palette["aqua"],
            "white": palette["aqua"],
        },
    }


def main() -> None:
    paths = sorted(PI_DIR.glob("reckoner-*.json"))
    if not paths:
        raise SystemExit("no phosphor themes in themes/pi/")

    written = 0
    for path in paths:
        theme = json.loads(path.read_text())
        name = theme["name"]
        display, description = TUBES.get(name, (name, "Phosphor theme."))
        palette = as_palette(theme)
        bundle = {
            "meta": {
                "name": name,
                "display_name": display,
                "description": description,
                "github": "sainzs/random-access-themes",
                # Nothing in the phosphor family blinks. Stillness is severity.
                "cursor_blink": False,
            },
            "palette": palette,
            "ansi": as_ansi(theme, palette),
        }

        for generator, template in OUTPUTS.values():
            out = THEMES_DIR / template.format(name=name)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(generator(bundle))
            written += 1

    print(f"Generated {written} exports for {len(paths)} phosphor themes")
    print(f"  formats: {', '.join(sorted(OUTPUTS))}")
    print("  pi is not among them — it is the source, not an output")


if __name__ == "__main__":
    main()
