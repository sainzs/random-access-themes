#!/usr/bin/env python3
"""Generate Random Access Theme exports from the canonical palette.

Source:   palette/random-access-theme.yaml
Outputs:  themes/{alacritty,ghostty,iterm2,kitty,pi,wezterm,windows-terminal}/

Usage:
    python3 scripts/generate.py
    python3 scripts/generate.py --palette palette/random-access-theme.yaml
    python3 scripts/generate.py --dry-run   # print without writing
"""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import sys
import textwrap
from pathlib import Path

import yaml

# ── Thinking ramp ─────────────────────────────────────────────────────────────

PALE = 74.0  # lightness ceiling; above this a phosphor has stopped being itself


def _hsl(hex_colour: str) -> tuple[float, float, float]:
    r, g, bl = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, bl)
    return h * 360, s * 100, l * 100


def _hex(h: float, s: float, l: float) -> str:
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l / 100, s / 100)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def thinking_ramp(low: str, high: str, steps: int = 6) -> list[str]:
    """
    The six thinking levels, from resting to driven hardest.

    Derived rather than assigned. This used to be six fixed palette slots —
    subtle, emerald, teal, jade, mint, aqua — the same list for every flavor,
    and the result was not a ramp: it fell at minimal, fell again at high, and
    finished on aqua at 75% lightness. Asking the model to think harder made the
    indicator paler until it left the palette entirely and turned white.

    Escalation is **chroma, not lightness**. The whole ramp is drawn in the
    accent's own hue: it starts at the quiet text's saturation and lightness,
    climbs saturation to the accent's, and stops there.

    Holding the hue is not a refinement, it is the point. A first version
    interpolated hue from `dimText` up to the accent, which works only where the
    two already agree — in this palette they sit 4° apart. Where the quiet text
    is a neutral grey the ramp swept the long way through foreign colour:
    amnesiac spanned 208°, so driving the model harder walked its indicator
    across the wheel and out of the theme.
    """
    _, s0, l0 = _hsl(low)
    hue, s1, l1 = _hsl(high)
    ceiling = min(max(l0, l1), PALE)
    out = []
    for i in range(steps):
        t = i / (steps - 1)
        out.append(_hex(hue, s0 + (s1 - s0) * t, l0 + (ceiling - l0) * t))
    return out

ROOT = Path(__file__).resolve().parents[1]
THEMES_DIR = ROOT / "themes"

# ── Helpers ────────────────────────────────────────────────────────────────────

def load_palette(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def hf(hex_color: str) -> tuple[float, float, float]:
    """Hex → (R, G, B) as floats in [0, 1]."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0


def strip(hex_color: str) -> str:
    """Remove leading # from hex color."""
    return hex_color.lstrip("#")


# ── Agent surfaces ─────────────────────────────────────────────────────────────

# Hues for the two states an agent surface has to state outright. They are fixed
# rather than taken from the palette because these beds are semantics before they
# are decoration: "removed" that is not red is not readable as removed, and three
# of the four flavors name a `green` that is really a teal (166°, 175°) or, in
# amnesiac, a blue (231°). A diff drawn in the palette's own "green" therefore
# read as two shades of the same colour. Everything else here — tint, elevation,
# the pending bed — still comes from the flavor's own accent.
SIGNAL_GREEN = 135.0
SIGNAL_RED = 2.0

# The footer's dim keys have to be readable at a glance while staying quiet.
# `dimText` clears WCAG AA on its own in one flavor and misses the mark in the
# other three, which is why the four footers did not look like one family.
DIM_FLOOR = 5.8


def _luminance(hex_colour: str) -> float:
    def channel(v: float) -> float:   # hf() already returns 0..1
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    return sum(k * channel(v) for k, v in zip((0.2126, 0.7152, 0.0722), hf(hex_colour)))


def contrast(fg: str, bg: str) -> float:
    a, b = _luminance(fg), _luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def lift(colour: str, bg: str, floor: float) -> str:
    """Raise `colour`'s lightness, holding hue and saturation, until it clears
    `floor` against `bg`. Returns it unchanged when it already does."""
    h, s, l = _hsl(colour)
    while contrast(_hex(h, s, l), bg) < floor and l < 100:
        l += 0.5
    return _hex(h, s, min(l, 100.0))


def pi_surfaces(c: dict) -> dict:
    """
    The backgrounds pi and Prime Agent draw their own UI on: tool beds, diff
    rows, the panel, the selection, message blocks.

    The palettes do not name them, and the first version simply reused `bg`,
    `surface` and `overlay` for all of them. That made running, done and failed
    the same colour, so a tool call never announced its result, and it left the
    diff rows with no beds at all.

    They are derived here, all of it from three facts about the flavor: the
    accent's hue and chroma, the background's lightness, and the two signal hues
    above. Elevation is lightness — ground +3.5 for a panel, +9.5 for a selection
    — and tint is the accent's, scaled by the accent's own saturation so a vivid
    flavor gets a tinted plate and a muted one gets something closer to grey.
    """
    accent_h, accent_s, _ = _hsl(c["mint"])
    ground_l = _hsl(c["bg"])[2]
    tint = min(36.0, accent_s * 0.36)

    # Where the accent is itself a green, an accent-tinted "pending" collides
    # with "success" by construction — running and done would differ only in
    # lightness. Pending goes neutral there, so finishing is a change of hue.
    hue_gap = abs(((accent_h - SIGNAL_GREEN + 180) % 360) - 180)
    pending_s = 8.0 if hue_gap < 45 else tint * 0.5

    return {
        "paToolPendingBg":   _hex(accent_h,    pending_s,  ground_l + 12.0),
        "paToolSuccessBg":   _hex(SIGNAL_GREEN, 26.0,      ground_l + 10.0),
        "paToolErrorBg":     _hex(SIGNAL_RED,   20.0,      ground_l + 12.0),
        "paUserMessageBg":   _hex(accent_h,    tint,        ground_l + 5.0),
        "paCustomMessageBg": _hex(accent_h,    tint * 0.92, ground_l + 4.0),
        "paToolPanelBg":     _hex(accent_h,    tint * 0.95, ground_l + 8.5),
        "paSelectedBg":      _hex(accent_h,    tint * 0.90, ground_l + 14.5),
        "paDiffAddedBg":     _hex(SIGNAL_GREEN, 30.0,       ground_l + 14.0),
        "paDiffRemovedBg":   _hex(SIGNAL_RED,   26.0,       ground_l + 14.0),
        "paDiffText":        c["text"],
    }


def write_or_print(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        print(f"\n{'─'*60}")
        print(f">> {path}")
        print(f"{'─'*60}")
        print(content)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        print(f"  [OK] {path.relative_to(ROOT)}")


# ── Generators ─────────────────────────────────────────────────────────────────

def gen_ghostty(p: dict) -> str:
    c = p["palette"]
    ansi = p["ansi"]
    meta = p["meta"]
    an = ansi["normal"]
    ab = ansi["bright"]
    order = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

    lines = [
        f"# {meta['display_name']} — Ghostty",
        f"# {meta['description']}",
        f"# https://github.com/{meta['github']}",
        f"",
        f"background = {strip(c['bg'])}",
        f"foreground = {strip(c['text'])}",
        f"",
        f"cursor-color = {strip(c['cursor'])}",
        f"cursor-text  = {strip(c['bg'])}",
        f"cursor-style       = block",
        # A blinking cursor is a decision the theme gets to make. The phosphor
        # family says nothing on the screen ever blinks — stillness is severity —
        # and a generator that hardcodes it overrules the theme it is exporting.
        f"cursor-style-blink = {'true' if meta.get('cursor_blink', True) else 'false'}",
        f"",
        f"selection-background = {strip(c['overlay'])}",
        f"selection-foreground = {strip(c['text'])}",
        f"",
        f"minimum-contrast = 1.2",
        f"",
        f"# ANSI 16-color palette",
    ]
    for i, name in enumerate(order):
        lines.append(f"palette = {i}={an[name]}")
    for i, name in enumerate(order):
        lines.append(f"palette = {i + 8}={ab[name]}")

    return "\n".join(lines) + "\n"


def gen_wezterm(p: dict) -> str:
    c = p["palette"]
    ansi = p["ansi"]
    meta = p["meta"]
    an = ansi["normal"]
    ab = ansi["bright"]
    order = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

    normal_list = ", ".join(f'"{an[n]}"' for n in order)
    bright_list = ", ".join(f'"{ab[n]}"' for n in order)

    return textwrap.dedent(f"""\
        # {meta['display_name']} — WezTerm color scheme
        # {meta['description']}
        # https://github.com/{meta['github']}
        #
        # Place in ~/.config/wezterm/colors/
        # Then set: config.color_scheme = "{meta['display_name']}"

        [colors]
        foreground    = "{c['text']}"
        background    = "{c['bg']}"
        cursor_bg     = "{c['cursor']}"
        cursor_border = "{c['cursor']}"
        cursor_fg     = "{c['bg']}"
        selection_bg  = "{c['overlay']}"
        selection_fg  = "{c['text']}"
        ansi          = [{normal_list}]
        brights       = [{bright_list}]

        [metadata]
        name       = "{meta['display_name']}"
        origin_url = "https://github.com/{meta['github']}"
    """)


def _iterm_color_block(key: str, hex_color: str, indent: int = 1) -> list[str]:
    r, g, b = hf(hex_color)
    t = "\t" * indent
    return [
        f"{t}<key>{key}</key>",
        f"{t}<dict>",
        f"{t}\t<key>Alpha Component</key>",
        f"{t}\t<real>1</real>",
        f"{t}\t<key>Blue Component</key>",
        f"{t}\t<real>{b:.10f}</real>",
        f"{t}\t<key>Color Space</key>",
        f"{t}\t<string>sRGB</string>",
        f"{t}\t<key>Green Component</key>",
        f"{t}\t<real>{g:.10f}</real>",
        f"{t}\t<key>Red Component</key>",
        f"{t}\t<real>{r:.10f}</real>",
        f"{t}</dict>",
    ]


def gen_iterm2(p: dict) -> str:
    c = p["palette"]
    ansi = p["ansi"]
    meta = p["meta"]
    an = ansi["normal"]
    ab = ansi["bright"]
    order = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"',
        '    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
        f"<!-- {meta['display_name']} — iTerm2 -->",
        f"<!-- {meta['description']} -->",
        f"<!-- https://github.com/{meta['github']} -->",
        '<plist version="1.0">',
        "<dict>",
    ]

    for i, name in enumerate(order):
        lines.extend(_iterm_color_block(f"Ansi {i} Color", an[name]))
    for i, name in enumerate(order):
        lines.extend(_iterm_color_block(f"Ansi {i + 8} Color", ab[name]))

    for key, color in [
        ("Background Color",     c["bg"]),
        ("Bold Color",           c["cursor"]),
        ("Cursor Color",         c["cursor"]),
        ("Cursor Text Color",    c["bg"]),
        ("Foreground Color",     c["text"]),
        ("Link Color",           c["cursor"]),
        ("Selected Text Color",  c["text"]),
        ("Selection Color",      c["overlay"]),
    ]:
        lines.extend(_iterm_color_block(key, color))

    lines += ["</dict>", "</plist>"]
    return "\n".join(lines) + "\n"


def gen_alacritty(p: dict) -> str:
    c = p["palette"]
    ansi = p["ansi"]
    meta = p["meta"]
    an = ansi["normal"]
    ab = ansi["bright"]
    order = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

    lines = [
        f"# {meta['display_name']} — Alacritty",
        f"# {meta['description']}",
        f"# https://github.com/{meta['github']}",
        f"",
        f"[colors.primary]",
        f'background = "{c["bg"]}"',
        f'foreground = "{c["text"]}"',
        f"",
        f"[colors.cursor]",
        f'cursor = "{c["cursor"]}"',
        f'text   = "{c["bg"]}"',
        f"",
        f"[colors.selection]",
        f'background = "{c["overlay"]}"',
        f'text       = "{c["text"]}"',
        f"",
        f"[colors.normal]",
    ]
    for name in order:
        lines.append(f"{name:<8} = \"{an[name]}\"")

    lines += ["", "[colors.bright]"]
    for name in order:
        lines.append(f"{name:<8} = \"{ab[name]}\"")

    return "\n".join(lines) + "\n"


def gen_kitty(p: dict) -> str:
    c = p["palette"]
    ansi = p["ansi"]
    meta = p["meta"]
    an = ansi["normal"]
    ab = ansi["bright"]
    order = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

    lines = [
        f"# {meta['display_name']} — kitty",
        f"# {meta['description']}",
        f"# https://github.com/{meta['github']}",
        f"",
        f"background              {c['bg']}",
        f"foreground              {c['text']}",
        f"cursor                  {c['cursor']}",
        f"cursor_text_color       {c['bg']}",
        f"selection_background    {c['overlay']}",
        f"selection_foreground    {c['text']}",
        f"url_color               {c['cursor']}",
        f"",
        f"# ANSI 16-color palette",
    ]
    for i, name in enumerate(order):
        lines.append(f"color{i:<3}                 {an[name]}")
    for i, name in enumerate(order):
        lines.append(f"color{i + 8:<3}                 {ab[name]}")

    return "\n".join(lines) + "\n"


def gen_windows_terminal(p: dict) -> str:
    c = p["palette"]
    ansi = p["ansi"]
    meta = p["meta"]
    an = ansi["normal"]
    ab = ansi["bright"]

    scheme = {
        "name":                meta["display_name"],
        "background":          c["bg"],
        "foreground":          c["text"],
        "cursorColor":         c["cursor"],
        "selectionBackground": c["overlay"],
        "black":               an["black"],
        "red":                 an["red"],
        "green":               an["green"],
        "yellow":              an["yellow"],
        "blue":                an["blue"],
        "purple":              an["magenta"],
        "cyan":                an["cyan"],
        "white":               an["white"],
        "brightBlack":         ab["black"],
        "brightRed":           ab["red"],
        "brightGreen":         ab["green"],
        "brightYellow":        ab["yellow"],
        "brightBlue":          ab["blue"],
        "brightPurple":        ab["magenta"],
        "brightCyan":          ab["cyan"],
        "brightWhite":         ab["white"],
    }
    return json.dumps(scheme, indent=4) + "\n"


def gen_pi(p: dict) -> str:
    c = p["palette"]
    meta = p["meta"]
    ramp = thinking_ramp(c["dimText"], c["mint"])
    surfaces = pi_surfaces(c)
    dim_keys = lift(c["dimText"], c["bg"], DIM_FLOOR)

    theme = {
        # themes/theme-schema.json is the union of pi's and Prime Agent's contracts:
        # Prime's 55 tokens required, pi's scrollbarThumb/thinkingMax optional. One file
        # set serves both runtimes, so there is no second copy to drift.
        "$schema": "../theme-schema.json",
        "name": meta["name"],
        "vars": {
            "bg":      c["bg"],
            "bg1":     c["bg1"],
            "bg2":     c["bg2"],
            "surface": c["surface"],
            "overlay": c["overlay"],
            "text":    c["text"],
            "subtle":  c["subtle"],
            "dimText": c["dimText"],
            "cyan":    c["cyan"],     # alias for mint — keeps original role
            "mint":    c["mint"],
            "green":   c["green"],
            "teal":    c["teal"],
            "jade":    c["jade"],
            "aqua":    c["aqua"],
            "emerald": c["emerald"],
            "lime":    c["lime"],
            **({"paDimKeys": dim_keys} if dim_keys != c["dimText"] else {}),
            **surfaces,
        },
        "colors": {
            "accent":             "mint",
            "border":             "subtle",
            "borderAccent":       "mint",
            "borderMuted":        "subtle",
            "success":            "green",
            "error":              "emerald",
            "warning":            "lime",
            "muted":              "subtle",
            "dim":                "paDimKeys" if dim_keys != c["dimText"] else "dimText",
            "text":               "text",
            "thinkingText":       "jade",
            "selectedBg":         "paSelectedBg",
            "userMessageBg":      "paUserMessageBg",
            "userMessageText":    "text",
            "customMessageBg":    "paCustomMessageBg",
            "customMessageText":  "text",
            "customMessageLabel": "mint",
            "toolPendingBg":      "paToolPendingBg",
            "toolSuccessBg":      "paToolSuccessBg",
            "toolErrorBg":        "paToolErrorBg",
            "toolDiffAddedBg":    "paDiffAddedBg",
            "toolDiffRemovedBg":  "paDiffRemovedBg",
            "toolPanelBg":        "paToolPanelBg",
            "toolTitle":          "mint",
            "toolOutput":         "text",
            "mdHeading":          "mint",
            "mdLink":             "cyan",
            "mdLinkUrl":          "subtle",
            "mdCode":             "cyan",
            "mdCodeBlock":        "text",
            "mdCodeBlockBorder":  "subtle",
            "mdQuote":            "subtle",
            "mdQuoteBorder":      "teal",
            "mdHr":               "subtle",
            "mdListBullet":       "mint",
            "toolDiffAdded":      "green",
            "toolDiffRemoved":    "emerald",
            "toolDiffText":       "paDiffText",
            "toolDiffContext":    "subtle",
            "syntaxComment":      "dimText",
            "syntaxKeyword":      "jade",
            "syntaxFunction":     "green",
            "syntaxVariable":     "text",
            "syntaxString":       "lime",
            "syntaxNumber":       "aqua",
            "syntaxType":         "cyan",
            "syntaxOperator":     "emerald",
            "syntaxPunctuation":  "subtle",
            # Derived, not assigned — see thinking_ramp() for why.
            "thinkingOff":        ramp[0],
            "thinkingMinimal":    ramp[1],
            "thinkingLow":        ramp[2],
            "thinkingMedium":     ramp[3],
            "thinkingHigh":       ramp[4],
            "thinkingXhigh":      ramp[5],
            "bashMode":           "lime",
        },
        "export": {
            "pageBg": c["bg"],
            "cardBg": c["surface"],
            "infoBg": c["bg2"],
        },
    }
    return json.dumps(theme, indent=2) + "\n"


# ── Entry point ────────────────────────────────────────────────────────────────

TARGETS = {
    "ghostty":          (gen_ghostty,          "ghostty/{name}.conf"),
    "wezterm":          (gen_wezterm,           "wezterm/{name}.toml"),
    "iterm2":           (gen_iterm2,            "iterm2/{name}.itermcolors"),
    "alacritty":        (gen_alacritty,         "alacritty/{name}.toml"),
    "kitty":            (gen_kitty,             "kitty/{name}.conf"),
    "windows-terminal": (gen_windows_terminal,  "windows-terminal/{name}.json"),
    "pi":               (gen_pi,                "pi/{name}.json"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--palette", default=str(ROOT / "palette" / "random-access-theme.yaml"))
    parser.add_argument("--dry-run", action="store_true", help="Print output instead of writing")
    parser.add_argument("--target", choices=list(TARGETS), help="Generate a single target only")
    args = parser.parse_args()

    palette_path = Path(args.palette).resolve()
    if not palette_path.exists():
        print(f"[FAIL] palette not found: {palette_path}", file=sys.stderr)
        raise SystemExit(1)

    p = load_palette(palette_path)
    print(f"Generating from: {palette_path.relative_to(ROOT)}\n")

    targets = {args.target: TARGETS[args.target]} if args.target else TARGETS
    theme_name = p["meta"]["name"]

    for name, (generator, rel_path_tpl) in targets.items():
        content = generator(p)
        rel_path = rel_path_tpl.format(name=theme_name)
        out_path = THEMES_DIR / rel_path
        write_or_print(out_path, content, args.dry_run)

    if not args.dry_run:
        # Write a checksum per palette so validate_theme.py can detect stale
        # themes. One line per file, rewritten in place: the previous version
        # stored only the palette it had just built, so generating any flavor
        # other than the default left the gate reporting the default as stale —
        # an order dependency between commands that nothing declared.
        checksum_file = THEMES_DIR / ".checksum"
        sums = {}
        if checksum_file.exists():
            for line in checksum_file.read_text().splitlines():
                if line.strip():
                    digest, _, name = line.partition("  ")
                    sums[name.strip()] = digest.strip()
        sums[palette_path.name] = hashlib.sha256(palette_path.read_bytes()).hexdigest()
        checksum_file.write_text("".join(f"{d}  {n}\n" for n, d in sorted(sums.items())))
        print(f"\nGenerated {len(targets)} theme(s) → themes/")


if __name__ == "__main__":
    main()
