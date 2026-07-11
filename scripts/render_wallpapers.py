#!/usr/bin/env python3
"""Render desktop wallpapers from the canonical palette YAML files.

Per flavor, generates one minimal geometric wallpaper (a sparse grid, a soft
off-center accent glow, and a thin cursor-accent hairline) using only colors
from that flavor's palette.

Outputs, per flavor `<name>`:
- wallpapers/<name>.svg               (source of truth, tracked in git)
- wallpapers/<name>-1920x1080.png
- wallpapers/<name>-2560x1440.png

Both PNG sizes share the same 16:9 SVG (2560x1440 is an exact 4/3 scale of
1920x1080), so a single composition rasterizes cleanly at both resolutions.

PNG export tries, in order: rsvg-convert, inkscape, magick, cairosvg. If none
of those are installed, it falls back to macOS's built-in `sips -z <h> <w>`,
which can rasterize simple SVGs (flat fills, gradients, no filters) directly
to an arbitrary size. `sips` is macOS-only and is the last resort — install
rsvg-convert (`brew install librsvg`) for a portable, higher-fidelity render.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WALLPAPERS = ROOT / "wallpapers"
PALETTES = [
    ROOT / "palette" / "random-access-theme.yaml",
    ROOT / "palette" / "veridis-theme.yaml",
    ROOT / "palette" / "voyager-theme.yaml",
    ROOT / "palette" / "amnesiac-theme.yaml",
]

CANVAS_W, CANVAS_H = 1920, 1080
PNG_SIZES = [(1920, 1080), (2560, 1440)]


def load_palettes() -> list[dict]:
    out = []
    for path in PALETTES:
        data = yaml.safe_load(path.read_text())
        data["path"] = path
        out.append(data)
    return out


def render_wallpaper_svg(data: dict) -> str:
    p = data["palette"]
    w, h = CANVAS_W, CANVAS_H

    # Off-center glow (rule-of-thirds-ish) and a golden-ratio accent hairline —
    # restrained geometry, no color outside this flavor's own palette.
    glow_cx, glow_cy = 74, 28  # percent
    hairline_y = round(h * 0.618)
    tick_x = round(w * 0.618)

    grid_color = p.get("bg2", p["overlay"])
    cols = [round(w * f) for f in (1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6)]
    rows = [round(h * f) for f in (1 / 4, 2 / 4, 3 / 4)]

    grid_lines = []
    for x in cols:
        grid_lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" />\n')
    for y in rows:
        grid_lines.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" />\n')

    return "".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n',
        "<defs>\n",
        f'<radialGradient id="glow" cx="{glow_cx}%" cy="{glow_cy}%" r="65%">\n',
        f'<stop offset="0%" stop-color="{p["mint"]}" stop-opacity="0.16" />\n',
        f'<stop offset="55%" stop-color="{p["mint"]}" stop-opacity="0.05" />\n',
        f'<stop offset="100%" stop-color="{p["mint"]}" stop-opacity="0" />\n',
        "</radialGradient>\n",
        '<radialGradient id="vignette" cx="50%" cy="50%" r="75%">\n',
        f'<stop offset="0%" stop-color="{p["bg1"]}" stop-opacity="0" />\n',
        f'<stop offset="100%" stop-color="{p["bg"]}" stop-opacity="0.55" />\n',
        "</radialGradient>\n",
        "</defs>\n",
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="{p["bg1"]}" />\n',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="url(#glow)" />\n',
        f'<g stroke="{grid_color}" stroke-width="1" opacity="0.5">\n',
        *grid_lines,
        "</g>\n",
        f'<line x1="0" y1="{hairline_y}" x2="{w}" y2="{hairline_y}" '
        f'stroke="{p["mint"]}" stroke-width="1" opacity="0.4" />\n',
        f'<rect x="{tick_x - 2}" y="{hairline_y - 16}" width="3" height="32" '
        f'fill="{p["mint"]}" opacity="0.85" />\n',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="url(#vignette)" />\n',
        "</svg>\n",
    ])


def export_wallpaper_png(svg: Path, png: Path, width: int, height: int) -> None:
    converters = [
        ("rsvg-convert", ["rsvg-convert", "--width", str(width), "--height", str(height), "-o", str(png), str(svg)]),
        ("inkscape", ["inkscape", str(svg), "--export-type=png", f"--export-filename={png}",
                      f"--export-width={width}", f"--export-height={height}"]),
        ("magick", ["magick", str(svg), "-resize", f"{width}x{height}!", str(png)]),
    ]
    for name, cmd in converters:
        if shutil.which(name) is None:
            continue
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"[OK] {png.relative_to(ROOT)} (via {name})")
        return

    try:
        import cairosvg
    except ImportError:
        pass
    else:
        cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=width, output_height=height)
        print(f"[OK] {png.relative_to(ROOT)} (via cairosvg)")
        return

    if shutil.which("sips") is not None:
        subprocess.run(
            ["sips", "-s", "format", "png", "-z", str(height), str(width), str(svg), "--out", str(png)],
            check=True, capture_output=True,
        )
        print(f"[OK] {png.relative_to(ROOT)} (via sips fallback)")
        return

    print(f"[WARN] no SVG renderer found (rsvg-convert / inkscape / magick / cairosvg / sips)")
    print(f"[WARN] {png.relative_to(ROOT)} not generated")


def main() -> None:
    palettes = load_palettes()
    WALLPAPERS.mkdir(parents=True, exist_ok=True)
    for data in palettes:
        name = data["meta"]["name"]
        svg_path = WALLPAPERS / f"{name}.svg"
        svg_path.write_text(render_wallpaper_svg(data))
        print(f"[OK] {svg_path.relative_to(ROOT)}")
        for width, height in PNG_SIZES:
            png_path = WALLPAPERS / f"{name}-{width}x{height}.png"
            export_wallpaper_png(svg_path, png_path, width, height)


if __name__ == "__main__":
    main()
