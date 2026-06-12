#!/usr/bin/env python3
"""Validate Random Access Theme assets.

Checks:
  1. Canonical palette YAML is well-formed.
  2. Generated themes are fresh (not stale vs palette).
  3. All expected theme files exist in themes/.
  4. Pi theme JSON has all required tokens with valid values.
  5. Text/bg contrast meets WCAG AA.
  6. Installed Pi theme matches generated (drift detection).

Usage:
    python3 scripts/validate_theme.py
    python3 scripts/validate_theme.py --skip-installed   # skip drift check (CI)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PALETTE_FILE  = ROOT / "palette" / "random-access-theme.yaml"
THEMES_DIR    = ROOT / "themes"
CHECKSUM_FILE = THEMES_DIR / ".checksum"
INSTALLED_PI  = Path.home() / ".pi" / "agent" / "themes" / "random-access-theme.json"

RE_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")

EXPECTED_THEMES = [
    "alacritty/random-access-theme.toml",
    "ghostty/random-access-theme.conf",
    "iterm2/random-access-theme.itermcolors",
    "kitty/random-access-theme.conf",
    "pi/random-access-theme.json",
    "wezterm/random-access-theme.toml",
    "windows-terminal/random-access-theme.json",
]

REQUIRED_PI_TOKENS = {
    "accent", "border", "borderAccent", "borderMuted",
    "success", "error", "warning",
    "muted", "dim", "text", "thinkingText",
    "selectedBg",
    "userMessageBg", "userMessageText",
    "customMessageBg", "customMessageText", "customMessageLabel",
    "toolPendingBg", "toolSuccessBg", "toolErrorBg",
    "toolTitle", "toolOutput",
    "mdHeading", "mdLink", "mdLinkUrl",
    "mdCode", "mdCodeBlock", "mdCodeBlockBorder",
    "mdQuote", "mdQuoteBorder", "mdHr", "mdListBullet",
    "toolDiffAdded", "toolDiffRemoved", "toolDiffContext",
    "syntaxComment", "syntaxKeyword", "syntaxFunction",
    "syntaxVariable", "syntaxString", "syntaxNumber",
    "syntaxType", "syntaxOperator", "syntaxPunctuation",
    "thinkingOff", "thinkingMinimal", "thinkingLow",
    "thinkingMedium", "thinkingHigh", "thinkingXhigh",
    "bashMode",
}


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"[OK]   {msg}")


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def contrast(a: str, b: str) -> float:
    def lum(h: str) -> float:
        r, g, b_ = (int(h.lstrip("#")[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b_)
    la, lb = lum(a), lum(b)
    hi, lo = (la, lb) if la >= lb else (lb, la)
    return (hi + 0.05) / (lo + 0.05)


# ── Check 1: Palette ───────────────────────────────────────────────────────────

def validate_palette() -> dict:
    if not PALETTE_FILE.exists():
        fail(f"palette not found: {PALETTE_FILE}")

    try:
        p = yaml.safe_load(PALETTE_FILE.read_text())
    except Exception as e:
        fail(f"invalid YAML: {e}")

    for section in ("meta", "palette", "ansi"):
        if section not in p:
            fail(f"palette missing section: {section}")

    for key in ("name", "display_name", "version"):
        if key not in p["meta"]:
            fail(f"palette.meta missing: {key}")

    for key, val in p["palette"].items():
        if not RE_HEX.match(val):
            fail(f"palette.{key} is not a valid hex color: {val!r}")

    for group in ("normal", "bright"):
        if group not in p["ansi"]:
            fail(f"palette.ansi missing: {group}")
        for name, val in p["ansi"][group].items():
            if not RE_HEX.match(val):
                fail(f"ansi.{group}.{name} is not a valid hex color: {val!r}")

    ok("palette YAML is valid")

    c = p["palette"]
    cr = contrast(c["text"], c["bg"])
    if cr < 4.5:
        fail(f"contrast(text, bg) too low: {cr:.2f} (need ≥ 4.5)")
    ok(f"contrast(text, bg) = {cr:.2f}")

    return p


# ── Check 2: Freshness ─────────────────────────────────────────────────────────

def validate_freshness() -> None:
    if not CHECKSUM_FILE.exists():
        fail(
            "themes/.checksum not found — themes may be stale.\n"
            "       Run: python3 scripts/generate.py"
        )

    stored  = CHECKSUM_FILE.read_text().split()[0]
    current = hashlib.sha256(PALETTE_FILE.read_bytes()).hexdigest()

    if stored != current:
        fail(
            "palette changed since themes were last generated.\n"
            "       Run: python3 scripts/generate.py"
        )
    ok("themes are up-to-date with palette")


# ── Check 3: Generated files ───────────────────────────────────────────────────

def validate_generated_themes() -> None:
    missing = [r for r in EXPECTED_THEMES if not (THEMES_DIR / r).exists()]
    if missing:
        fail(
            "missing generated theme files — run: python3 scripts/generate.py\n"
            + "\n".join(f"  themes/{r}" for r in missing)
        )
    ok(f"all {len(EXPECTED_THEMES)} generated theme files present")


# ── Check 4: Pi theme tokens ───────────────────────────────────────────────────

def validate_pi_theme() -> None:
    pi_path = THEMES_DIR / "pi" / "random-access-theme.json"
    if not pi_path.exists():
        fail(f"Pi theme not found: {pi_path}")

    try:
        theme = json.loads(pi_path.read_text())
    except Exception as e:
        fail(f"Pi theme invalid JSON: {e}")

    if theme.get("name") != "random-access-theme":
        fail(f"Pi theme name must be 'random-access-theme', got: {theme.get('name')!r}")

    colors   = theme.get("colors", {})
    vars_map = theme.get("vars", {})

    missing = sorted(REQUIRED_PI_TOKENS - set(colors.keys()))
    extra   = sorted(set(colors.keys()) - REQUIRED_PI_TOKENS)
    if missing:
        fail(f"Pi theme missing tokens: {', '.join(missing)}")
    if extra:
        fail(f"Pi theme unexpected tokens: {', '.join(extra)}")

    def valid_value(v: object) -> bool:
        if isinstance(v, int):
            return 0 <= v <= 255
        if not isinstance(v, str):
            return False
        return v == "" or RE_HEX.match(v) is not None or v in vars_map

    bad = [k for k, v in colors.items() if not valid_value(v)]
    if bad:
        fail(f"Pi theme invalid values: {', '.join(bad)}")

    ok(f"Pi theme valid ({len(colors)} tokens)")


# ── Check 5: Installed drift ───────────────────────────────────────────────────

def validate_installed(skip: bool) -> None:
    if skip:
        return

    if not INSTALLED_PI.exists():
        warn(
            "Pi theme not installed locally.\n"
            "       Run: bash scripts/install.sh"
        )
        return

    generated = (THEMES_DIR / "pi" / "random-access-theme.json").read_text()
    installed = INSTALLED_PI.read_text()

    if generated != installed:
        warn(
            "Installed Pi theme has drifted from generated source.\n"
            "       Run: bash scripts/install.sh"
        )
        return

    ok("installed Pi theme matches generated (no drift)")


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-installed",
        action="store_true",
        help="Skip installed-theme drift check (use in CI)",
    )
    args = parser.parse_args()

    print("Validating Random Access Theme...\n")
    validate_palette()
    validate_freshness()
    validate_generated_themes()
    validate_pi_theme()
    validate_installed(skip=args.skip_installed)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
