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
    gen_opencode,
    gen_wezterm,
    gen_windows_terminal,
    gen_zed,
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
    "opencode": (gen_opencode, "opencode/{name}.json"),
    "zed": (gen_zed, "zed/{name}.json"),
}

# What each tube is, for the export headers. The pi themes carry no prose.
#
# The display name is not decoration: WezTerm selects a scheme by this exact
# string and Windows Terminal shows it in a dropdown, in a namespace shared with
# every other scheme the user has installed. So the name has one job — to be
# picked correctly from a sorted list — and it is written for that.
#
# Colour first, identity second. The colour is what you are choosing by; the
# identity is what the theme is. Two earlier attempts failed the same list test:
#
#   Bare words (Scope, Dusk, Factory) said nothing about where they came from and
#   sat waiting to collide with somebody else's Dusk.
#
#   Prefixing the family (Reckoner Scope, Reckoner Dusk, ...) fixed collisions and
#   created a worse problem: all six began with the same nine characters, so they
#   collapsed into one indistinguishable block in the dropdown and you had to read
#   to the tenth character to tell an amber tube from a violet one. One distinct
#   first word across six themes.
#
# These give six distinct first words that sort into a spread rather than a wall,
# none of which anyone else is shipping, and every identity is the one it always
# had. The tube itself stays in the description, where there is room for it.
TUBES = {
    "reckoner-exect": ("Amber EXECT", "EXECT-100 / DEC VT520 — amber phosphor on warm near-black."),
    "reckoner-scope": ("Green Scope", "DEC VT640 radar — P1 green on green glass."),
    "reckoner-wopr": ("Cyan WOPR", "VT100 blue screen — cyan and white-blue, the war room."),
    "reckoner-darkspace": ("Teal Darkspace", "dark.spaceAMP — teal wireframe on blackest glass."),
    "reckoner-dusk": ("Violet Dusk", "Violet on blue-black — late light, cold screen."),
    "reckoner-factory": ("Orange Factory", "Safety orange on true black — machine-shop signage under work lights."),
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
        # Diff rows tinted toward the tube's own add/remove signals.
        "diffAddBg": _diff_bg(background, resolve(theme, "success")),
        "diffRemBg": _diff_bg(background, resolve(theme, "error")),
    }


def _diff_bg(bg: str, hue_hex: str) -> str:
    """A diff row background: the hue pulled most of the way down to the ground.

    The flavors keep these as fixed palette slots, but a phosphor tube has one
    hue, so a hardcoded green tint would be a foreign colour on an amber or
    violet screen. Blend the signal hue toward the background at 12%: present
    enough to read as a tint, quiet enough to sit under text.
    """
    def rgb(h: str) -> tuple[int, int, int]:
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    br, bg_, bb = rgb(bg)
    hr, hg, hb = rgb(hue_hex)
    t = 0.12
    r = round(br + (hr - br) * t)
    g = round(bg_ + (hg - bg_) * t)
    b = round(bb + (hb - bb) * t)
    return "#%02x%02x%02x" % (r, g, b)


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
