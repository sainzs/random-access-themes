#!/usr/bin/env python3
"""Generate Claude Code custom themes from the canonical kitty ports.

Claude Code (2.1.251+) loads custom themes from ~/.claude/themes/*.json with
the schema { "name", "base": "dark"|"light", "overrides": {...} }. Overrides
merge onto a built-in preset, but only for keys it knows — so we map EVERY
key (72 in this build); any key left unset falls back to the stock dark
preset's blue/gray palette and clashes with the theme.

Source:   themes/kitty/<name>.conf   (canonical 16-slot ANSI + specials)
Outputs:  ~/.claude/themes/<name>.json   (override with --dest)

Usage:
    python3 scripts/generate_claude.py
    python3 scripts/generate_claude.py --dry-run
    python3 scripts/generate_claude.py --dest /tmp/claude-themes
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "themes" / "kitty"

# ── color math ────────────────────────────────────────────────────────────────


def _rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    r, g, b = _rgb(hex_color)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def mix(a: str, b: str, t: float) -> str:
    """Blend a toward b by t (0..1) in gamma space."""
    ra, ga, ba = _rgb(a)
    rb, gb, bb = _rgb(b)
    out = (round((ra + (rb - ra) * t) * 255), round((ga + (gb - ga) * t) * 255), round((ba + (bb - ba) * t) * 255))
    return "#{:02x}{:02x}{:02x}".format(*out)


# ── port parsing ──────────────────────────────────────────────────────────────


def parse_kitty(path: Path) -> dict[str, str]:
    colors: dict[str, str] = {}
    for line in path.read_text().splitlines():
        if line.lstrip().startswith("#"):
            continue  # full-line comment (inline hex after 'key  #value' is the value)
        parts = line.split()
        if len(parts) == 2 and all(c in "0123456789abcdefABCDEF" for c in parts[-1].lstrip("#")):
            colors[parts[0]] = parts[-1].lstrip("#").lower()
    return colors


class Port:
    def __init__(self, path: Path):
        raw = parse_kitty(path)
        self.name = path.stem.removesuffix(".conf")
        # Claude's validator only accepts #-prefixed hex — normalize here.
        self.bg = "#" + raw["background"]
        self.fg = "#" + raw["foreground"]
        self.cursor = "#" + raw["cursor"]
        self.selection_bg = "#" + raw["selection_background"]
        self.ansi = ["#" + raw[f"color{i}"] for i in range(16)]
        self.title = next(
            (l.split("—")[0].lstrip("# ").strip() for l in path.read_text().splitlines() if l.startswith("# ") and "—" in l),
            self.name,
        )

    def slot(self, i: int) -> str:
        return self.ansi[i]


# ── the mapping ───────────────────────────────────────────────────────────────


def claude_overrides(p: Port) -> dict[str, str]:
    fg, bg, cursor, sel = p.fg, p.bg, p.cursor, p.selection_bg
    red, green, yellow, blue = (p.slot(i) for i in (1, 2, 3, 4))
    magenta, cyan = p.slot(5), p.slot(6)
    red_b, green_b, yellow_b, blue_b = (p.slot(i) for i in (9, 10, 11, 12))
    magenta_b, cyan_b, white_b = (p.slot(i) for i in (13, 14, 15))

    # The port's "pale peak": brightest of the pale slots, used for shimmer pulses.
    pale = max((cyan_b, magenta_b, yellow_b, white_b), key=luminance)
    if luminance(pale) <= luminance(cursor):
        pale = mix(cursor, "#ffffff", 0.25)

    def lift(c: str) -> str:
        """Shimmer pulse: same hue, pulled toward the pale peak."""
        return mix(c, pale, 0.35)

    def sink(c: str) -> str:
        """Dimmed diff tone: same hue, sunk toward the background."""
        return mix(c, bg, 0.55)

    return {
        # core
        "text": fg,
        "inverseText": bg,
        "background": bg,
        "subtle": mix(fg, bg, 0.48),
        "inactive": mix(fg, bg, 0.32),
        "inactiveShimmer": fg,
        "promptBorder": mix(fg, bg, 0.45),
        "promptBorderShimmer": fg,
        "bashBorder": mix(fg, bg, 0.35),
        # accent family (Claude brand + interactive)
        "claude": cursor,
        "claudeShimmer": pale,
        "claudeBlue_FOR_SYSTEM_SPINNER": blue,
        "claudeBlueShimmer_FOR_SYSTEM_SPINNER": blue_b,
        "permission": blue,
        "permissionShimmer": blue_b,
        "planMode": cyan,
        "ide": blue,
        "skill": magenta,
        "autoAccept": yellow,
        "autoAcceptShimmer": yellow_b,
        "suggestion": cyan_b,
        "remember": cyan_b,
        "merged": green,
        # semantics
        "success": green,
        "error": red,
        "warning": yellow,
        "warningShimmer": yellow_b,
        "diffAdded": green,
        "diffRemoved": red,
        "diffAddedDimmed": sink(green),
        "diffRemovedDimmed": sink(red),
        "diffAddedWord": green_b,
        "diffRemovedWord": red_b,
        # subagent chat markers
        "red_FOR_SUBAGENTS_ONLY": red,
        "blue_FOR_SUBAGENTS_ONLY": blue,
        "green_FOR_SUBAGENTS_ONLY": green,
        "yellow_FOR_SUBAGENTS_ONLY": yellow,
        "purple_FOR_SUBAGENTS_ONLY": magenta,
        "orange_FOR_SUBAGENTS_ONLY": mix(red, yellow, 0.5),
        "pink_FOR_SUBAGENTS_ONLY": mix(red, cyan_b, 0.5),
        "cyan_FOR_SUBAGENTS_ONLY": cyan,
        # fixed brand roles
        "professionalBlue": blue,
        "chromeYellow": yellow,
        "clawd_body": cursor,
        "clawd_background": bg,
        # surfaces (elevated steps from bg toward fg keep the theme's tint)
        "userMessageBackground": mix(bg, fg, 0.10),
        "userMessageBackgroundHover": mix(bg, fg, 0.16),
        "composerSidebarBackground": mix(bg, fg, 0.05),
        "selectionBg": sel,
        "bashMessageBackgroundColor": mix(bg, fg, 0.07),
        "memoryBackgroundColor": mix(bg, blue, 0.12),
        # meters and badges
        "rate_limit_fill": cursor,
        "rate_limit_empty": mix(bg, fg, 0.18),
        "fastMode": red,
        "fastModeShimmer": mix(red, yellow, 0.5),
        "effortUltra": magenta,
        "briefLabelYou": blue,
        "briefLabelClaude": cursor,
        # rainbow (party trick stays in-palette)
        "rainbow_red": red,
        "rainbow_orange": mix(red, yellow, 0.5),
        "rainbow_yellow": yellow,
        "rainbow_green": green,
        "rainbow_blue": blue,
        "rainbow_indigo": magenta,
        "rainbow_violet": mix(magenta, cyan, 0.5),
        "rainbow_red_shimmer": lift(red),
        "rainbow_orange_shimmer": lift(mix(red, yellow, 0.5)),
        "rainbow_yellow_shimmer": lift(yellow),
        "rainbow_green_shimmer": lift(green),
        "rainbow_blue_shimmer": lift(blue),
        "rainbow_indigo_shimmer": lift(magenta),
        "rainbow_violet_shimmer": lift(mix(magenta, cyan, 0.5)),
    }


# ── contrast gate ─────────────────────────────────────────────────────────────


def check(p: Port, o: dict[str, str]) -> list[str]:
    """Return human-readable failures against WCAG targets for terminal UI."""
    bg = o["background"]
    failures = []
    for key, minimum, label in [
        ("text", 7.0, "body text"),
        ("subtle", 3.0, "secondary text"),
        ("error", 3.0, "error"),
        ("warning", 3.0, "warning"),
        ("success", 3.0, "success"),
        ("claude", 3.0, "accent"),
    ]:
        ratio = contrast(o[key], bg)
        if ratio < minimum:
            failures.append(f"  {key} ({o[key]}) on {bg}: {ratio:.2f} < {minimum} — {label}")
    return failures


# ── main ──────────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dest", type=Path, default=Path.home() / ".claude" / "themes")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ports = sorted(SOURCE.glob("*.conf"))
    if not ports:
        print(f"no kitty ports found in {SOURCE}", file=sys.stderr)
        return 1

    failures: list[str] = []
    for path in ports:
        p = Port(path)
        overrides = claude_overrides(p)
        theme = {"name": p.title, "base": "dark", "overrides": overrides}

        bad = check(p, overrides)
        status = "ok " if not bad else "FAIL"
        print(f"[{status}] {p.name:<20} text/bg {contrast(p.fg, p.bg):.1f}:1, "
              f"subtle/bg {contrast(overrides['subtle'], p.bg):.1f}:1, "
              f"error/bg {contrast(overrides['error'], p.bg):.1f}:1, "
              f"warn/bg {contrast(overrides['warning'], p.bg):.1f}:1")
        if bad:
            failures.extend([f"{p.name}: {b}" for b in bad])

        if not args.dry_run:
            args.dest.mkdir(parents=True, exist_ok=True)
            out = args.dest / f"{p.name}.json"
            out.write_text(json.dumps(theme, indent=2) + "\n")

    if failures:
        print("\ncontrast failures:")
        print("\n".join(failures))
        return 2
    print(f"\n{len(ports)} themes -> {args.dest}" + (" (dry run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
