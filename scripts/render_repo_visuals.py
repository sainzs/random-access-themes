#!/usr/bin/env python3
"""Render README visuals from the canonical palette YAML files.

Outputs:
- assets/flavors.svg
- assets/palette-strips.svg
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

import yaml

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PALETTES = [
    ROOT / "palette" / "random-access-theme.yaml",
    ROOT / "palette" / "veridis-theme.yaml",
    ROOT / "palette" / "voyager-theme.yaml",
    ROOT / "palette" / "amnesiac-theme.yaml",
]

SAMPLE_LINES = [
    [("# OLED-black themes / generated ports", "dimText")],
    [("flavor", "jade"), (" = ", "text"), ("\"{display_name}\"", "lime")],
    [("accent", "jade"), (" = ", "text"), ("\"{mint}\"", "aqua"), ("  # hero accent", "dimText")],
    [("ports", "jade"), (" = ", "text"), ("[", "subtle"), ("\"ghostty\"", "lime"), (", ", "subtle"), ("\"wezterm\"", "lime"), (", ", "subtle"), ("\"kitty\"", "lime"), ("]", "subtle")],
    [("contrast", "jade"), (" = ", "text"), ("17.4", "aqua"), ("  # flagship text/bg", "dimText")],
    [("status", "jade"), (" = ", "text"), ("{{", "subtle"), ("\"wcag\"", "lime"), (": ", "subtle"), ("\"AA+\"", "green"), (", ", "subtle"), ("\"release\"", "lime"), (": ", "subtle"), ("True", "mint"), ("}}", "subtle")],
]

SWATCH_ORDER = [
    ("bg", "bg"),
    ("text", "text"),
    ("mint", "mint"),
    ("green", "green"),
    ("teal", "teal"),
    ("jade", "jade"),
    ("aqua", "aqua"),
    ("emerald", "emerald"),
    ("lime", "lime"),
]


def load_palettes() -> list[dict]:
    out = []
    for path in PALETTES:
        data = yaml.safe_load(path.read_text())
        data["path"] = path
        out.append(data)
    return out


def svg_header(width: int, height: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none">\n'
    )


def text(x: float, y: float, value: str, *, size: int = 16, weight: int = 400,
         fill: str = "#ffffff", family: str = "ui-monospace, SFMono-Regular, Menlo, monospace") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}">{escape(value)}</text>\n'
    )


def rect(x: float, y: float, w: float, h: float, *, fill: str, stroke: str | None = None,
         stroke_width: int = 1, rx: int = 0) -> str:
    attrs = [
        f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"', f'fill="{fill}"'
    ]
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{stroke_width}"')
    if rx:
        attrs.append(f'rx="{rx}"')
    return f"<rect {' '.join(attrs)} />\n"


def circle(cx: float, cy: float, r: float, *, fill: str) -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" />\n'


def render_code_line(x: float, y: float, palette: dict, display_name: str, mint: str, segments: list[tuple[str, str]]) -> str:
    char_w = 10.2
    out = []
    cursor = x
    for raw, role in segments:
        rendered = raw.format(display_name=display_name, mint=mint)
        color = palette.get(role, palette["text"])
        out.append(text(cursor, y, rendered, size=21, fill=color))
        cursor += len(rendered) * char_w
    return "".join(out)


def render_flavors_svg(palettes: list[dict]) -> str:
    width, height = 1600, 1100
    out = [svg_header(width, height)]
    out.append(rect(0, 0, width, height, fill="#050607"))
    out.append(rect(36, 36, width - 72, height - 72, fill="#06080a", stroke="#101214", stroke_width=2, rx=28))

    out.append(text(88, 118, "Random Access Themes", size=42, weight=700, fill="#f2efec", family="system-ui, -apple-system, Segoe UI, sans-serif"))
    out.append(text(88, 158, "OLED-black terminals and editors / four flavors / YAML-driven generation", size=20, fill="#9cb7af", family="system-ui, -apple-system, Segoe UI, sans-serif"))

    chip_y = 198
    chips = [
        ("4 flavors", "#00ffb2"),
        ("7 terminal ports", "#35d5c5"),
        ("WCAG AA+", "#8bf5dd"),
        ("MIT", "#a2e5b8"),
    ]
    chip_x = 88
    for label, color in chips:
        chip_w = 24 + len(label) * 11
        out.append(rect(chip_x, chip_y, chip_w, 34, fill="#0b0c0e", stroke="#1a1c20", rx=17))
        out.append(circle(chip_x + 16, chip_y + 17, 5, fill=color))
        out.append(text(chip_x + 30, chip_y + 22, label, size=15, fill="#d8efe9", family="system-ui, -apple-system, Segoe UI, sans-serif"))
        chip_x += chip_w + 12

    card_w, card_h = 676, 324
    start_x, start_y = 88, 272
    gap_x, gap_y = 48, 48

    for i, data in enumerate(palettes):
        meta = data["meta"]
        p = data["palette"]
        row, col = divmod(i, 2)
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)

        out.append(rect(x, y, card_w, card_h, fill=p["surface"], stroke=p["bg2"], stroke_width=2, rx=24))
        out.append(rect(x + 1, y + 1, card_w - 2, 62, fill=p["bg1"], rx=24))
        out.append(rect(x + 1, y + 40, card_w - 2, 22, fill=p["bg1"]))

        out.append(circle(x + 24, y + 24, 6, fill="#ff5f57"))
        out.append(circle(x + 44, y + 24, 6, fill="#febc2e"))
        out.append(circle(x + 64, y + 24, 6, fill="#28c840"))
        out.append(text(x + 92, y + 29, meta["display_name"], size=18, weight=700, fill=p["text"], family="system-ui, -apple-system, Segoe UI, sans-serif"))

        out.append(text(x + 24, y + 90, meta["description"], size=15, fill=p["subtle"], family="system-ui, -apple-system, Segoe UI, sans-serif"))

        swatch_x = x + 24
        for key in ["bg", "text", "mint", "green", "teal", "aqua"]:
            out.append(rect(swatch_x, y + 112, 54, 16, fill=p[key], rx=8))
            swatch_x += 62

        preview_x, preview_y = x + 24, y + 148
        out.append(rect(preview_x, preview_y, card_w - 48, 148, fill=p["bg"], stroke=p["overlay"], rx=16))
        out.append(text(preview_x + 18, preview_y + 28, "$ palette preview.py", size=18, fill=p["dimText"]))

        line_y = preview_y + 58
        for segments in SAMPLE_LINES:
            out.append(render_code_line(preview_x + 18, line_y, p, meta["display_name"], p["mint"], segments))
            line_y += 22

    out.append(text(88, 1036, "Generated from palette/*.yaml / visual identity matches the actual source of truth", size=18, fill="#6f8d86", family="system-ui, -apple-system, Segoe UI, sans-serif"))
    out.append("</svg>\n")
    return "".join(out)


def render_palette_svg(palettes: list[dict]) -> str:
    width, height = 1600, 820
    out = [svg_header(width, height)]
    out.append(rect(0, 0, width, height, fill="#050607"))
    out.append(rect(36, 36, width - 72, height - 72, fill="#06080a", stroke="#101214", stroke_width=2, rx=28))
    out.append(text(88, 118, "Flavor palette strips", size=38, weight=700, fill="#f2efec", family="system-ui, -apple-system, Segoe UI, sans-serif"))
    out.append(text(88, 156, "A quick visual read of the four flavors: neutral base, text color, and core accent family.", size=20, fill="#9cb7af", family="system-ui, -apple-system, Segoe UI, sans-serif"))

    y = 214
    row_h = 134
    for data in palettes:
        meta = data["meta"]
        p = data["palette"]
        out.append(rect(88, y, 1424, 104, fill=p["surface"], stroke=p["bg2"], stroke_width=2, rx=20))
        out.append(text(116, y + 39, meta["display_name"], size=28, weight=700, fill=p["text"], family="system-ui, -apple-system, Segoe UI, sans-serif"))
        out.append(text(116, y + 68, meta["description"], size=15, fill=p["subtle"], family="system-ui, -apple-system, Segoe UI, sans-serif"))

        sw_x = 520
        sw_y = y + 26
        label_y = y + 88
        sw_w = 92
        gap = 12
        for label, key in SWATCH_ORDER:
            out.append(rect(sw_x, sw_y, sw_w, 30, fill=p[key], rx=10))
            out.append(text(sw_x + 4, label_y, label, size=13, fill="#b1a8a2", family="system-ui, -apple-system, Segoe UI, sans-serif"))
            sw_x += sw_w + gap
        y += row_h

    out.append(text(88, 744, "Tip: lead with the hero gallery in the README, then use these strips to explain how the flavors differ at a glance.", size=18, fill="#6f8d86", family="system-ui, -apple-system, Segoe UI, sans-serif"))
    out.append("</svg>\n")
    return "".join(out)


def main() -> None:
    palettes = load_palettes()
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "flavors.svg").write_text(render_flavors_svg(palettes))
    (ASSETS / "palette-strips.svg").write_text(render_palette_svg(palettes))
    print("[OK] assets/flavors.svg")
    print("[OK] assets/palette-strips.svg")


if __name__ == "__main__":
    main()
