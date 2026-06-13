#!/usr/bin/env python3
"""Export Random Access Theme design tokens for web, CSS, and Tailwind consumers.

Source:   palette/*.yaml
Outputs:  tokens/{random-access-theme,veridis,voyager,amnesiac}.json
          tokens/design-tokens.json      (W3C Design Tokens format)
          tokens/random-access-theme.css (CSS custom properties)
          tokens/tailwind.js             (Tailwind color config snippet)

Usage:
    python3 scripts/export_tokens.py
    python3 scripts/export_tokens.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PALETTE_DIR = ROOT / "palette"
TOKENS_DIR = ROOT / "tokens"

FLAVORS = [
    ("random-access-theme", "random-access-theme"),
    ("veridis", "veridis-theme"),
    ("voyager", "voyager-theme"),
    ("amnesiac", "amnesiac-theme"),
]

# Semantic groups used by every flavor.
TOKEN_GROUPS = {
    "background": ["bg", "bg1", "bg2", "surface", "overlay"],
    "foreground": ["text", "subtle", "dimText"],
    "accent": ["mint", "cyan", "green", "teal", "jade", "aqua", "emerald", "lime"],
    "cursor": ["cursor"],
}


def load_palette(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def palette_tokens(palette: dict) -> dict:
    """Return a W3C Design Tokens $value-style token map for one flavor."""
    meta = palette["meta"]
    tokens: dict = {
        "meta": {
            "name": {"$type": "string", "$value": meta["name"]},
            "displayName": {"$type": "string", "$value": meta["display_name"]},
            "version": {"$type": "string", "$value": meta["version"]},
            "github": {"$type": "string", "$value": meta["github"]},
        }
    }

    for group, keys in TOKEN_GROUPS.items():
        tokens[group] = {}
        for key in keys:
            if key in palette["palette"]:
                tokens[group][key] = {
                    "$type": "color",
                    "$value": palette["palette"][key],
                }

    tokens["ansi"] = {}
    for level in ("normal", "bright"):
        tokens["ansi"][level] = {}
        for name, value in palette["ansi"][level].items():
            tokens["ansi"][level][name] = {
                "$type": "color",
                "$value": value,
            }

    return tokens


def css_variables(flavor: str, tokens: dict) -> str:
    """Generate a CSS custom-properties file for the flagship flavor."""
    lines = [
        f"/* Random Access Theme — {flavor} */",
        f"/* Auto-generated from palette/{flavor}.yaml */",
        ":root {",
    ]
    for group in ("background", "foreground", "accent", "cursor"):
        for key, token in tokens.get(group, {}).items():
            value = token["$value"]
            lines.append(f"  --rat-{key}: {value};")

    for level in ("normal", "bright"):
        for key, token in tokens["ansi"][level].items():
            value = token["$value"]
            lines.append(f"  --rat-ansi-{level}-{key}: {value};")

    lines.append("}")
    return "\n".join(lines) + "\n"


def tailwind_config(tokens: dict) -> str:
    """Generate a Tailwind-compatible JS color config snippet."""
    colors: dict = {}
    for group in ("background", "foreground", "accent", "cursor"):
        for key, token in tokens.get(group, {}).items():
            colors[key] = token["$value"]

    ansi: dict = {}
    for level in ("normal", "bright"):
        ansi[level] = {}
        for key, token in tokens["ansi"][level].items():
            ansi[level][key] = token["$value"]

    config = {
        "colors": {
            "rat": colors,
            "rat-ansi": ansi,
        }
    }

    return (
        "// Tailwind color config snippet for Random Access Theme\n"
        "// Copy into tailwind.config.js / extend colors\n"
        f"module.exports = {json.dumps(config, indent=2)};\n"
    )


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print output instead of writing")
    args = parser.parse_args()

    all_tokens: dict = {
        "$schema": "https://design-tokens.github.io/community-group/format/",
        "name": "Random Access Theme",
        "version": "0.1.1",
        "flavors": {},
    }

    flagship_tokens = None

    for flavor, file_stem in FLAVORS:
        path = PALETTE_DIR / f"{file_stem}.yaml"
        if not path.exists():
            print(f"[FAIL] palette not found: {path}", file=sys.stderr)
            raise SystemExit(1)

        palette = load_palette(path)
        tokens = palette_tokens(palette)
        all_tokens["flavors"][flavor] = tokens

        if flavor == "random-access-theme":
            flagship_tokens = tokens

        out_path = TOKENS_DIR / f"{flavor}.json"
        write_or_print(out_path, json.dumps(tokens, indent=2) + "\n", args.dry_run)

    # W3C-style grouped tokens for all flavors
    write_or_print(
        TOKENS_DIR / "design-tokens.json",
        json.dumps(all_tokens, indent=2) + "\n",
        args.dry_run,
    )

    # CSS and Tailwind are based on the flagship palette
    if flagship_tokens is None:
        print("[FAIL] flagship palette not found", file=sys.stderr)
        raise SystemExit(1)

    write_or_print(
        TOKENS_DIR / "random-access-theme.css",
        css_variables("random-access-theme", flagship_tokens),
        args.dry_run,
    )

    write_or_print(
        TOKENS_DIR / "tailwind.js",
        tailwind_config(flagship_tokens),
        args.dry_run,
    )

    if not args.dry_run:
        print(f"\nExported tokens for {len(FLAVORS)} flavor(s) → tokens/")


if __name__ == "__main__":
    main()
