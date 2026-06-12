#!/usr/bin/env python3
"""Render README visuals from the canonical palette YAML files.

Outputs:
- assets/flavors.svg
- assets/palette-strips.svg
- assets/preview.svg
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
    parts = []
    for raw, role in segments:
        rendered = escape(raw.format(display_name=display_name, mint=mint))
        color = palette.get(role, palette["text"])
        parts.append(f'<tspan fill="{color}">{rendered}</tspan>')
    joined = "".join(parts)
    return (
        f'<text x="{x}" y="{y}" xml:space="preserve" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, monospace" '
        f'font-size="21" font-weight="400">{joined}</text>\n'
    )


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


def render_preview_svg(data: dict) -> str:
    p = data["palette"]
    meta = data["meta"]
    width, height = 1680, 1050
    out = [svg_header(width, height)]
    out.append('<defs>\n')
    out.append('<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">\n')
    out.append('<feDropShadow dx="0" dy="24" stdDeviation="28" flood-color="#000000" flood-opacity="0.45" />\n')
    out.append('</filter>\n')
    out.append('</defs>\n')
    out.append(rect(0, 0, width, height, fill="#070809"))
    out.append(rect(80, 72, width - 160, height - 144, fill=p["surface"], stroke=p["bg2"], stroke_width=2, rx=28).replace('/>', ' filter="url(#shadow)" />'))
    out.append(rect(81, 73, width - 162, 64, fill=p["bg1"], rx=28))
    out.append(rect(81, 113, width - 162, 24, fill=p["bg1"]))
    out.append(circle(116, 105, 7, fill="#ff5f57"))
    out.append(circle(140, 105, 7, fill="#febc2e"))
    out.append(circle(164, 105, 7, fill="#28c840"))
    out.append(text(198, 112, f'{meta["display_name"]} — flagship terminal preview', size=22, weight=700, fill=p["text"], family="system-ui, -apple-system, Segoe UI, sans-serif"))
    out.append(text(120, 174, 'Exact colors from palette/random-access-theme.yaml / rendered without external syntax theme guessing', size=17, fill=p["subtle"], family="system-ui, -apple-system, Segoe UI, sans-serif"))

    code_x, code_y = 120, 214
    code_w, code_h = 1440, 528
    out.append(rect(code_x, code_y, code_w, code_h, fill=p["bg"], stroke=p["overlay"], stroke_width=1, rx=18))
    out.append(text(code_x + 24, code_y + 34, '$ cat preview.py', size=18, fill=p["dimText"]))

    preview_lines = [
        [("# Random Access Theme — OLED-black, mint-forward, zero warm hues", "dimText")],
        [],
        [("from", "jade"), (" dataclasses ", "text"), ("import", "jade"), (" dataclass", "text")],
        [("from", "jade"), (" typing ", "text"), ("import", "jade"), (" Literal", "text")],
        [],
        [("Flavor", "mint"), (" = ", "subtle"), ("Literal", "teal"), ("[", "subtle"), ('"random-access"', "lime"), (", ", "subtle"), ('"veridis"', "lime"), (", ", "subtle"), ('"voyager"', "lime"), (", ", "subtle"), ('"amnesiac"', "lime"), ("]", "subtle")],
        [],
        [("@dataclass", "teal"), ("(frozen=", "text"), ("True", "mint"), (")", "text")],
        [("class", "jade"), (" PreviewTheme", "mint"), (":", "subtle")],
        [("    name", "text"), (": ", "subtle"), ("Flavor", "teal")],
        [("    accent", "text"), (": ", "subtle"), ("str", "teal"), (" = ", "subtle"), ('"#00ffb2"', "lime")],
        [("    background", "text"), (": ", "subtle"), ("str", "teal"), (" = ", "subtle"), ('"#000000"', "lime")],
        [("    contrast_ratio", "text"), (": ", "subtle"), ("float", "teal"), (" = ", "subtle"), ("17.44", "aqua")],
        [],
        [("    def", "jade"), (" passes_aa", "mint"), ("(self, ratio", "text"), (": ", "subtle"), ("float", "teal"), (" = ", "subtle"), ("17.44", "aqua"), (") -> ", "subtle"), ("bool", "teal"), (":", "subtle")],
        [("        return", "jade"), (" ratio >= ", "text"), ("4.5", "aqua")],
    ]

    line_y = code_y + 74
    for line in preview_lines:
        if not line:
            line_y += 22
            continue
        out.append(render_code_line(code_x + 24, line_y, p, meta["display_name"], p["mint"], line))
        line_y += 28

    shell_x, shell_y = 120, 774
    shell_w, shell_h = 1440, 152
    out.append(rect(shell_x, shell_y, shell_w, shell_h, fill=p["bg1"], stroke=p["overlay"], stroke_width=1, rx=18))
    out.append(text(shell_x + 24, shell_y + 34, '$ make check', size=18, fill=p["mint"]))

    shell_lines = [
        ("[OK]", p["green"], " palette YAML is valid", p["text"]),
        ("[OK]", p["green"], " contrast(text, bg) = 17.44", p["text"]),
        ("[OK]", p["green"], " all 7 generated theme files present", p["text"]),
        ("[OK]", p["green"], " release assets ready / WCAG AA+ / MIT", p["text"]),
    ]
    sy = shell_y + 68
    for marker, mcolor, tail, tcolor in shell_lines:
        out.append(text(shell_x + 24, sy, marker, size=20, weight=700, fill=mcolor))
        out.append(text(shell_x + 82, sy, tail, size=20, fill=tcolor))
        sy += 28

    out.append(text(120, 973, 'Generated from the canonical palette so the preview matches the actual exported terminal theme.', size=18, fill=p["dimText"], family="system-ui, -apple-system, Segoe UI, sans-serif"))
    out.append("</svg>\n")
    return "".join(out)


def main() -> None:
    palettes = load_palettes()
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "flavors.svg").write_text(render_flavors_svg(palettes))
    (ASSETS / "palette-strips.svg").write_text(render_palette_svg(palettes))
    (ASSETS / "preview.svg").write_text(render_preview_svg(palettes[0]))
    print("[OK] assets/flavors.svg")
    print("[OK] assets/palette-strips.svg")
    print("[OK] assets/preview.svg")


if __name__ == "__main__":
    main()
