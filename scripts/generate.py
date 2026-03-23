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
import hashlib
import json
import sys
import textwrap
from pathlib import Path

import yaml

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
        f"# Random Access Theme — Ghostty",
        f"# {meta['description']}",
        f"# https://github.com/{meta['github']}",
        f"",
        f"background = {strip(c['bg'])}",
        f"foreground = {strip(c['text'])}",
        f"",
        f"cursor-color = {strip(c['cursor'])}",
        f"cursor-text  = {strip(c['bg'])}",
        f"cursor-style       = block",
        f"cursor-style-blink = true",
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
        # Random Access Theme — WezTerm color scheme
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
        "<!-- Random Access Theme — iTerm2 -->",
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
        f"# Random Access Theme — Alacritty",
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
        f"# Random Access Theme — kitty",
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

    theme = {
        "$schema": "https://raw.githubusercontent.com/badlogic/pi-mono/main/packages/coding-agent/src/modes/interactive/theme/theme-schema.json",
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
            "dim":                "dimText",
            "text":               "text",
            "thinkingText":       "jade",
            "selectedBg":         "overlay",
            "userMessageBg":      "surface",
            "userMessageText":    "text",
            "customMessageBg":    "surface",
            "customMessageText":  "text",
            "customMessageLabel": "mint",
            "toolPendingBg":      "bg",
            "toolSuccessBg":      "bg",
            "toolErrorBg":        "bg",
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
            "thinkingOff":        "subtle",
            "thinkingMinimal":    "emerald",
            "thinkingLow":        "teal",
            "thinkingMedium":     "jade",
            "thinkingHigh":       "mint",
            "thinkingXhigh":      "aqua",
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

    palette_path = Path(args.palette)
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
        # Write palette checksum so validate_theme.py can detect stale themes
        checksum = hashlib.sha256(palette_path.read_bytes()).hexdigest()
        checksum_file = THEMES_DIR / ".checksum"
        checksum_file.write_text(f"{checksum}  {palette_path.name}\n")
        print(f"\nGenerated {len(targets)} theme(s) → themes/")


if __name__ == "__main__":
    main()
