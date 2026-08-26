#!/usr/bin/env python3
"""Validate Random Access Theme assets.

Checks:
  1. Canonical palette YAML is well-formed.
  2. Generated themes are fresh (not stale vs palette).
  3. All expected theme files exist in themes/.
  4. Pi theme JSON has all required tokens with valid values.
  5. Preview PNG export is fresh vs preview SVG.
  6. Text/bg contrast meets WCAG AA.
  7. Installed Pi theme matches generated (drift detection).

Usage:
    python3 scripts/validate_theme.py
    python3 scripts/validate_theme.py --skip-installed   # skip drift check (CI)
"""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import re
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PALETTE_FILE  = ROOT / "palette" / "random-access-theme.yaml"
PALETTE_DIR   = ROOT / "palette"
THEMES_DIR    = ROOT / "themes"
CHECKSUM_FILE = THEMES_DIR / ".checksum"
PREVIEW_SVG      = ROOT / "assets" / "preview.svg"
PREVIEW_PNG      = ROOT / "assets" / "preview.png"
PREVIEW_CHECKSUM = ROOT / "assets" / ".preview-checksum"
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
    "toolDiffAddedBg", "toolDiffRemovedBg", "toolPanelBg",
    "toolTitle", "toolOutput",
    "mdHeading", "mdLink", "mdLinkUrl",
    "mdCode", "mdCodeBlock", "mdCodeBlockBorder",
    "mdQuote", "mdQuoteBorder", "mdHr", "mdListBullet",
    "toolDiffAdded", "toolDiffRemoved", "toolDiffText", "toolDiffContext",
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

    stored = {}
    for line in CHECKSUM_FILE.read_text().splitlines():
        if line.strip():
            digest, _, name = line.partition("  ")
            stored[name.strip()] = digest.strip()

    stale = []
    for palette in sorted(PALETTE_DIR.glob("*.yaml")):
        current = hashlib.sha256(palette.read_bytes()).hexdigest()
        if stored.get(palette.name) != current:
            stale.append(palette.name)

    if stale:
        fail(
            "palette changed since themes were last generated: "
            + ", ".join(stale)
            + "\n       Run: python3 scripts/generate.py --palette palette/<name>.yaml"
        )
    ok(f"themes are up-to-date with all {len(stored)} palettes")


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
        return RE_HEX.match(v) is not None or v in vars_map

    bad = [k for k, v in colors.items() if not valid_value(v)]
    if bad:
        fail(f"Pi theme invalid values: {', '.join(bad)}")

    ok(f"Pi theme valid ({len(colors)} tokens)")


# ── Check 5: Preview PNG freshness ─────────────────────────────────────────────

def validate_preview_png() -> None:
    if not PREVIEW_PNG.exists():
        fail(
            "assets/preview.png not found.\n"
            "       Run: python3 scripts/render_repo_visuals.py"
        )
    if not PREVIEW_CHECKSUM.exists():
        fail(
            "assets/.preview-checksum not found — preview.png may be stale.\n"
            "       Run: python3 scripts/render_repo_visuals.py"
        )

    stored  = PREVIEW_CHECKSUM.read_text().split()[0]
    current = hashlib.sha256(PREVIEW_SVG.read_bytes()).hexdigest()

    if stored != current:
        fail(
            "assets/preview.svg changed since preview.png was last exported.\n"
            "       Run: python3 scripts/render_repo_visuals.py\n"
            "       (requires rsvg-convert, inkscape, magick, or cairosvg)"
        )
    ok("preview PNG is up-to-date with preview SVG")


# ── Check 6: Installed drift ───────────────────────────────────────────────────

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

# ── Check 5: Thinking ramps, every pi theme ────────────────────────────────────

PALE = 74.0     # a level above this has stopped being the theme's colour
HUE_SPAN = 40.0 # degrees the escalation may wander before it is a different hue

THINKING = [
    "thinkingOff", "thinkingMinimal", "thinkingLow",
    "thinkingMedium", "thinkingHigh", "thinkingXhigh",
]


def _hsl(hex_colour: str) -> tuple[float, float, float]:
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100, l * 100


def validate_pi_index() -> None:
    """
    `scripts/get.sh` installs the pi family by reading themes/pi/index.txt,
    because raw.githubusercontent.com cannot list a directory. A manifest that
    drifts from the directory it describes is worse than no manifest: the
    installer would silently skip whatever was added and 404 on whatever was
    removed, and the person installing would have no way to tell.
    """
    index = THEMES_DIR / "pi" / "index.txt"
    if not index.exists():
        fail(f"pi theme index missing: {index}")
    listed = [ln.strip() for ln in index.read_text().splitlines() if ln.strip()]
    actual = sorted(p.stem for p in (THEMES_DIR / "pi").glob("*.json"))
    if listed != actual:
        missing = sorted(set(actual) - set(listed))
        extra   = sorted(set(listed) - set(actual))
        detail  = []
        if missing: detail.append(f"not listed: {', '.join(missing)}")
        if extra:   detail.append(f"listed but absent: {', '.join(extra)}")
        if not detail: detail.append("same names, wrong order")
        fail("themes/pi/index.txt is stale — " + "; ".join(detail))
    ok(f"pi theme index lists all {len(actual)} themes")


def validate_thinking_ramps() -> None:
    """
    The six thinking levels say how hard the model is being driven, and the
    escalation must read as more of the theme's own colour — not as more white,
    and not as a different colour.

    This check arrives from the reckoner-themes project, where it was written
    after watching a recording of the footer: at the top thinking level the
    indicator had gone white, and on two themes it had changed hue entirely and
    landed on their error colour, so asking for more reasoning looked like
    something had gone wrong. Three of the four flavors here failed it on the day
    it was added — amnesiac finished at 89% lightness having crossed 208° of hue.

    Applied to every theme in themes/pi/, generated or hand-authored, because
    the previous pi check looked at one file by name and the family has nine.
    """
    paths = sorted((THEMES_DIR / "pi").glob("*.json"))
    if not paths:
        fail("no pi themes found to check")

    for path in paths:
        theme = json.loads(path.read_text())
        colors, vars_map = theme.get("colors", {}), theme.get("vars", {})

        def resolve(key: str) -> str | None:
            val = colors.get(key)
            for _ in range(4):
                if isinstance(val, str) and val.startswith("#"):
                    return val
                val = vars_map.get(val, colors.get(val)) if isinstance(val, str) else None
            return None

        levels = [(name, resolve(name)) for name in THINKING]
        unresolved = [n for n, v in levels if v is None]
        if unresolved:
            fail(f"{path.name}: {', '.join(unresolved)} does not resolve to a colour")

        # Which way "more" points depends on what the theme is painted on. The
        # rule is that escalation reads as more of the theme's own colour, and
        # on ink-on-paper that means getting *darker*: a light theme whose ramp
        # climbed would fade toward its own background exactly when the model is
        # working hardest. `userMessageBg` is a real pi background token, so it
        # says which world we are in without guessing from free-form var names.
        ground = resolve("userMessageBg")
        ground_light = _hsl(ground)[2] if ground else 0.0
        on_paper = ground_light > 50.0
        floor = 100.0 - PALE

        problems, previous = [], None
        hues = []
        for name, hex_colour in levels:
            hue, _sat, light = _hsl(hex_colour)
            hues.append(hue)
            if on_paper:
                if light < floor:
                    problems.append(f"{name} is crushed ({light:.0f}% lightness, floor {floor:.0f}%)")
                if previous is not None and light > previous + 0.01:
                    problems.append(f"{name} is lighter than the level below it; on paper the ramp must descend")
            else:
                if light > PALE:
                    problems.append(f"{name} is washed out ({light:.0f}% lightness, limit {PALE:.0f}%)")
                if previous is not None and light < previous - 0.01:
                    problems.append(f"{name} is darker than the level below it; the ramp must climb")
            previous = light
        span = max(hues) - min(hues)
        if span > HUE_SPAN:
            problems.append(f"the ramp wanders {span:.0f}° of hue (limit {HUE_SPAN:.0f}°)")

        if problems:
            fail(f"{path.name} thinking ramp:\n" + "\n".join(f"       {p}" for p in problems))

    ok(f"thinking ramps hold hue and leave the ground across all {len(paths)} pi themes")


# ── Check 6: Phosphor exports ──────────────────────────────────────────────────

PHOSPHOR_FORMATS = {
    "ghostty": "{name}.conf",
    "wezterm": "{name}.toml",
    "iterm2": "{name}.itermcolors",
    "alacritty": "{name}.toml",
    "kitty": "{name}.conf",
    "windows-terminal": "{name}.json",
}


def validate_phosphor_exports() -> None:
    """
    The phosphor family's terminal exports exist and are legible.

    These run the pipeline backwards — `themes/pi/reckoner-*.json` is the source
    and the terminal files are derived, because those six themes arrived finished
    and a generator built for four cool-spectrum flavors would only have made them
    worse. So the freshness question is different too: not "does this match the
    palette" but "does this match the pi theme it came from".

    The contrast floor is here because a monochrome tube has eight ANSI slots and
    one colour to spend on them. The first mapping put `dim` on normal magenta —
    1.2:1 against the background on all six themes — so any tool colouring real
    output magenta wrote it in invisible ink. Black is exempt: it is the
    background's own step, and every flavor here does the same.
    """
    sources = sorted((THEMES_DIR / "pi").glob("reckoner-*.json"))
    if not sources:
        fail("no phosphor pi themes found")

    missing = []
    for source in sources:
        name = json.loads(source.read_text())["name"]
        for directory, template in PHOSPHOR_FORMATS.items():
            path = THEMES_DIR / directory / template.format(name=name)
            if not path.exists():
                missing.append(f"themes/{directory}/{template.format(name=name)}")
    if missing:
        fail(
            "missing phosphor exports — run: python3 scripts/generate_phosphor.py\n"
            + "\n".join(f"  {m}" for m in missing)
        )

    offenders = []
    for path in sorted((THEMES_DIR / "ghostty").glob("reckoner-*.conf")):
        text = path.read_text()
        background = "#" + re.search(r"background = #?(\w{6})", text).group(1)
        for match in re.finditer(r"palette = (\d+)=#?(\w{6})", text):
            slot, colour = int(match.group(1)), "#" + match.group(2)
            if slot in (0, 8):
                continue
            ratio = contrast(colour, background)
            if ratio < 3.0:
                offenders.append(f"{path.name} slot {slot} ({colour}): {ratio:.2f}:1")
    if offenders:
        fail(
            "phosphor ANSI slots below 3:1 against their own background:\n"
            + "\n".join(f"       {o}" for o in offenders)
        )

    ok(f"phosphor exports present and legible ({len(sources)} themes x {len(PHOSPHOR_FORMATS)} formats)")


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
    validate_pi_index()
    validate_thinking_ramps()
    validate_phosphor_exports()
    validate_preview_png()
    validate_installed(skip=args.skip_installed)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
