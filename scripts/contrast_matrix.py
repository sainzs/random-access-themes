#!/usr/bin/env python3
"""WCAG contrast matrix for Random Access Theme.

Computes contrast ratios for all accent/text colors vs background.
Prints a table with WCAG AA (≥4.5) and AAA (≥7.0) pass/fail.

Usage:
    python3 scripts/contrast_matrix.py
    python3 scripts/contrast_matrix.py --palette palette/random-access-theme.yaml
    python3 scripts/contrast_matrix.py --fail-fast   # non-zero exit if any AA fail
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

AA_MIN  = 4.5
AAA_MIN = 7.0


def load_palette(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def _linearize(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)


def contrast(fg: str, bg: str) -> float:
    lf = relative_luminance(fg)
    lb = relative_luminance(bg)
    hi, lo = (lf, lb) if lf >= lb else (lb, lf)
    return (hi + 0.05) / (lo + 0.05)


def grade(ratio: float) -> str:
    if ratio >= AAA_MIN:
        return "AAA"
    if ratio >= AA_MIN:
        return "AA "
    return "FAIL"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--palette", default=str(ROOT / "palette" / "random-access-theme.yaml"))
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    p = load_palette(Path(args.palette))
    c = p["palette"]
    bg = c["bg"]

    # Named palette colors to check against bg
    named = [
        ("text",    c["text"]),
        ("subtle",  c["subtle"]),
        ("dimText", c["dimText"]),
        ("mint",    c["mint"]),
        ("green",   c["green"]),
        ("teal",    c["teal"]),
        ("jade",    c["jade"]),
        ("aqua",    c["aqua"]),
        ("emerald", c["emerald"]),
        ("lime",    c["lime"]),
        ("cursor",  c["cursor"]),
    ]

    # ANSI colors vs bg
    ansi_named = []
    for group, data in p["ansi"].items():
        for name, hex_color in data.items():
            ansi_named.append((f"ansi.{group}.{name}", hex_color))

    all_pairs = named + ansi_named

    header = f"{'Color':<26}  {'Hex':<9}  {'Ratio':>6}  {'WCAG'}"
    separator = "─" * len(header)

    print(f"\nWCAG Contrast Matrix — all colors vs bg ({bg})\n")
    print(header)
    print(separator)

    failures = []
    for label, hex_color in all_pairs:
        if hex_color == bg:
            continue
        ratio = contrast(hex_color, bg)
        g = grade(ratio)
        marker = ""
        if g == "FAIL":
            failures.append((label, hex_color, ratio))
            marker = " ✗"
        print(f"{label:<26}  {hex_color:<9}  {ratio:>6.2f}  {g}{marker}")

    print(separator)
    print(f"\nBackground: {bg}")
    print(f"AA threshold:  {AA_MIN}:1  (normal text)")
    print(f"AAA threshold: {AAA_MIN}:1  (enhanced)")

    if failures:
        print(f"\n[WARN] {len(failures)} color(s) below WCAG AA:")
        for label, hex_color, ratio in failures:
            print(f"  {label} ({hex_color}): {ratio:.2f}")
        if args.fail_fast:
            raise SystemExit(1)
    else:
        print(f"\nAll colors pass WCAG AA against bg.")


if __name__ == "__main__":
    main()
