#!/usr/bin/env python3
"""
Render documentation screenshots for every theme in themes/.

Each screenshot is a mock pi session drawn with the theme's actual tokens
(the vars are resolved from the JSON, so the images can never drift from
the theme). The braille ink of the harness footer is drawn as real dot
matrices — the way the terminal renders it.

Run:  npm run render:screenshots   (or python3 scripts/render-screenshots.py)
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEMES_DIR = os.path.join(ROOT, "themes", "pi")
OUT_DIR = os.path.join(ROOT, "assets", "phosphor")
FRAMES = os.path.join(ROOT, "scripts", "footer-frames.json")

SCALE = 2  # 2x so the captures stay crisp on retina
W, H = 1280, 800

FONT_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Supplemental/Monaco.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]


def font(size_pt: int) -> ImageFont.FreeTypeFont:
    """Monospace font at 2x, first face that loads."""
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size_pt * SCALE)
            except Exception:
                continue
    return ImageFont.load_default()


F_TITLE = font(13)
F_SMALL = font(13)
F_BODY = font(15)
F_CODE = font(14)
F_FOOT = font(14)


def ink() -> dict:
    """
    The harness footer's animation frames, as a committed snapshot.

    The footer itself lives in the reckoner package, written in TypeScript that
    Python cannot read; while the themes were a subdirectory of that package the
    renderer shelled out to `scripts/dump-ink-frames.ts` for the frames every
    time. A standalone theme project cannot depend on the agent it decorates, so
    the seam is now a file.

    Refresh it from reckoner when the footer vocabulary changes:

        npx tsx scripts/dump-ink-frames.ts > .../scripts/footer-frames.json

    A snapshot can go stale where a live call could not. That is the price of
    standing alone, and it is recorded in AGENTS.md rather than left implicit.
    """
    if not os.path.exists(FRAMES):
        sys.exit(f"no footer frames at {FRAMES}; see the docstring in this function")
    with open(FRAMES, encoding="utf-8") as fh:
        return json.load(fh)


class Theme:
    def __init__(self, path: str):
        data = json.load(open(path))
        self.name = data["name"]
        self.vars = data.get("vars", {})
        self.colors = data["colors"]

    def c(self, key: str) -> str:
        """Resolve a color key (may be a var reference or hex)."""
        v = self.colors[key]
        return self.vars.get(v, v)

    def v(self, key: str) -> str:
        """Resolve a var directly (backgrounds live in vars)."""
        return self.vars.get(key, key)


def braille(pattern: int):
    """Dots (col, row) for a braille pattern, per the Unicode standard."""
    dots = []
    for n in range(8):
        if pattern >> n & 1:
            if n < 6:
                dots.append((n // 3, n % 3))
            else:
                dots.append((n - 6, 3))
    return dots


def draw_braille(d: ImageDraw.ImageDraw, x: float, y: float, em: float,
                 ch: str, color: str) -> None:
    """
    Draw one braille cell as dots. x/y = top-left of the cell.

    The dots are nudged down by a fifth of an em: text drawn from its top-left
    carries the font's ascender as empty space, and ink that ignores that floats
    above the words it sits beside, which is a thing the terminal never does.
    """
    pattern = ord(ch) - 0x2800
    r = em * 0.135
    y += em * 0.20
    for col, row in braille(pattern):
        cx = x + col * em * 0.30
        cy = y + row * em * 0.27
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def text_width(d: ImageDraw.ImageDraw, s: str, f) -> float:
    return d.textlength(s, font=f)


def draw_cells(d: ImageDraw.ImageDraw, x: float, y: float, em: float,
               glyphs: str, color: str, advance: float = None) -> float:
    """Draw a run of braille cells on the character grid. Spaces advance."""
    if advance is None:
        advance = em * 0.62
    for ch in glyphs:
        if ch != " ":
            draw_braille(d, x, y, em, ch, color)
        x += advance
    return x


def draw_footer(d: ImageDraw.ImageDraw, theme: Theme, data: dict,
                x0: float, y: float, right_edge: float, em: float,
                kind: str = "answering", frame: int = 4, well: int = 1,
                plan: bool = True) -> None:
    """
    The footer, drawn the way it is actually laid out: a fixed activity zone,
    groups separated by a raised fleck, and the account side flush right.

    Braille advances by one character cell, not by its own metrics — in a
    terminal the ink sits on the same grid as the words, and a picture that
    forgets that flatters a layout the eye never sees.
    """
    c = theme.c
    grid = text_width(d, "M", F_FOOT)
    ty = y + 2 * SCALE
    act = next(a for a in data["activities"] if a["kind"] == kind)
    well_state = data["well"][well]
    ink = c(well_state["inks"][0]) if well_state["inks"][0] != "dim" else c("muted")

    def sep(x: float) -> float:
        """Two spaces. The fleck was a mark where a gap already says it."""
        return x + grid * 2

    # Left: the activity zone, then place, then what is wrong or in flight.
    x = draw_cells(d, x0, y, em, act["frames"][frame % len(act["frames"])], c("text"), grid)
    x += grid
    x = draw_segments(d, x, ty, [(act["verb"].ljust(9), c("dim"))], F_FOOT)
    x = sep(x)
    x = draw_segments(d, x, ty, [("~/Code/projects/agent-workbench/packages/reckoner", c("muted"))], F_FOOT)
    x = sep(x)
    x = draw_segments(d, x, ty, [("main +2", c("muted"))], F_FOOT)
    if plan:
        x = sep(x)
        x = draw_segments(d, x, ty, [("plan", c("accent"))], F_FOOT)
    x = sep(x)
    x = draw_segments(d, x, ty, [("STEPS ", c("dim"))], F_FOOT)
    trail = data["trail"]["glyphs"]
    for i, ch in enumerate(trail):
        draw_braille(d, x, y, em, ch, c("muted") if ch == "⣿" else c("dim"))
        x += grid

    left_end = x

    # Right: provider, model, well — measured backwards so it sits flush.
    right_text = [("anthropic", c("dim")), ("claude-opus-5", c("dim"))]
    rw = sum(text_width(d, s, F_FOOT) for s, _ in right_text)
    rw += 2 * grid * len(right_text)  # one two-space gap after each
    rw += text_width(d, "CONTEXT ", F_FOOT) + grid * len(well_state["glyphs"])
    x = right_edge - rw

    for s, colour in right_text:
        x = draw_segments(d, x, ty, [(s, colour)], F_FOOT)
        x = sep(x)
    x = draw_segments(d, x, ty, [("CONTEXT ", c("dim"))], F_FOOT)
    for ch, level in zip(well_state["glyphs"], well_state["inks"]):
        draw_braille(d, x, y, em, ch, c("dim") if level == "dim" else ink)
        x += grid


def draw_segments(d: ImageDraw.ImageDraw, x: float, y: float,
                  segments, f) -> float:
    """Draw colored text segments left to right; returns end x."""
    for text, color in segments:
        if text == "":
            continue
        d.text((x, y), text, font=f, fill=color)
        x += text_width(d, text, f)
    return x


def render_theme(theme: Theme, data: dict, path: str) -> None:
    img = Image.new("RGB", (W * SCALE, H * SCALE), theme.v("bg0"))
    d = ImageDraw.Draw(img)
    c = theme.c
    cx = 48 * SCALE

    # ── window chrome ──
    bar_h = 56 * SCALE
    d.rounded_rectangle([0, 0, W * SCALE, bar_h], radius=0, fill=theme.v("bg2"))
    for color, dx in ((c("error"), 20), (c("warning"), 44), (c("success"), 68)):
        d.ellipse([dx * SCALE, 20 * SCALE, (dx + 10) * SCALE, 30 * SCALE], fill=color)
    d.text((92 * SCALE, 19 * SCALE), f"pi — {theme.name}", font=F_TITLE, fill=c("muted"))

    y = bar_h + 28 * SCALE

    # ── status line ──
    draw_segments(d, cx, y, [
        ("plan", c("accent")),
        ("   ", None), ("~/C/p/a-w/p/reckoner  main +2", c("muted")),
        ("   ", None), ("claude-fable-5", c("dim")),
        ("   ", None), ("anthropic", c("dim")),
    ], F_SMALL)
    y += 34 * SCALE

    # ── user message ──
    bubble_w = 700 * SCALE
    bubble_h = 74 * SCALE
    d.rounded_rectangle([cx, y, cx + bubble_w, y + bubble_h], radius=12 * SCALE,
                        fill=c("userMessageBg"), outline=c("borderMuted"))
    d.text((cx + 18 * SCALE, y + 12 * SCALE), "you", font=F_SMALL, fill=c("accent"))
    d.text((cx + 18 * SCALE, y + 38 * SCALE), "make the footer move only when something is actually happening",
           font=F_BODY, fill=c("userMessageText"))
    y += bubble_h + 26 * SCALE

    # ── assistant message ──
    d.text((cx, y), "Every animation is bound to an event now. The tape advances one frame",
           font=F_BODY, fill=c("text"))
    y += 30 * SCALE
    d.text((cx, y), "per token chunk, each tool brings its own motion, and the loop is torn",
           font=F_BODY, fill=c("text"))
    y += 30 * SCALE
    d.text((cx, y), "down when the harness goes quiet — an idle footer costs nothing.",
           font=F_BODY, fill=c("text"))
    y += 42 * SCALE

    # ── code block ──
    code_w = 860 * SCALE
    code_h = 116 * SCALE
    d.rounded_rectangle([cx, y, cx + code_w, y + code_h], radius=10 * SCALE,
                        fill=c("toolPendingBg"), outline=c("borderMuted"))
    code_x = cx + 22 * SCALE
    code_y = y + 18 * SCALE
    draw_segments(d, code_x, code_y, [
        ("const ", c("syntaxKeyword")), ("{ kind, phase }", c("syntaxVariable")),
        (" = ", c("syntaxPunctuation")), ("currentPhase", c("syntaxFunction")),
        ("()", c("syntaxPunctuation")),
    ], F_CODE)
    code_y += 32 * SCALE
    draw_segments(d, code_x, code_y, [
        ("return ", c("syntaxKeyword")), ("fieldCells", c("syntaxFunction")),
        ("(", c("syntaxPunctuation")), ("kind", c("syntaxVariable")),
        (", ", c("syntaxPunctuation")), ("phase", c("syntaxVariable")),
        (", ", c("syntaxPunctuation")),
        ("chunks", c("syntaxVariable")), (")", c("syntaxPunctuation")),
        ("  // one frame per chunk", c("syntaxComment")),
    ], F_CODE)
    y += code_h + 26 * SCALE

    # ── verify line ──
    draw_segments(d, cx, y, [
        ("verify:self", c("success")),
        # No counts: a number in a picture rots the first time a test is added.
        ("  clean · typecheck · tests · themes 7/7", c("dim")),
    ], F_SMALL)

    # ── footer (pinned to the bottom) ──
    foot_h = 58 * SCALE
    foot_y = H * SCALE - foot_h
    d.rectangle([0, foot_y, W * SCALE, foot_y + 2 * SCALE], fill=c("borderMuted"))
    draw_footer(d, theme, data, cx, foot_y + 20 * SCALE, W * SCALE - 48 * SCALE, 14 * SCALE)

    img.save(path)
    print(f"wrote {path}")


def render_footer_states(theme: Theme, data: dict, path: str) -> None:
    """The CONTEXT well at four levels: calm, calm, amber, red."""
    img = Image.new("RGB", (W * SCALE, 592 * SCALE), theme.v("bg0"))
    d = ImageDraw.Draw(img)
    c = theme.c
    em = 14 * SCALE
    captions = {"muted": "calm — the surface moves", "warning": "amber — still", "error": "red — still",
                "dim": "no reading — after a compaction, until the next response"}

    d.text((90 * SCALE, 74 * SCALE), "CONTEXT", font=F_TITLE, fill=c("mdHeading"))
    d.text((90 * SCALE, 98 * SCALE),
           "remaining context as ink — stillness is severity, nothing blinks",
           font=F_SMALL, fill=c("dim"))

    y = 150 * SCALE
    for state in data["well"]:
        level = state["inks"][0]
        ink = c(level) if level in ("muted", "warning", "error", "dim") else c("muted")
        x = 90 * SCALE
        # The activity zone, exactly as the footer reserves it.
        grid = text_width(d, "M", F_FOOT)
        # Read the frame rather than typing one: this whole file exists so that
        # a picture cannot show an animation the footer does not play.
        answering = next(a for a in data["activities"] if a["kind"] == "answering")
        x = draw_cells(d, x, y, em, answering["frames"][6], c("text"), grid) + grid
        x = draw_segments(d, x, y + 2 * SCALE, [("answering".ljust(11), c("dim"))], F_FOOT)
        x = draw_segments(d, x, y + 2 * SCALE, [("~/C/p/a-w/p/reckoner  main +2", c("muted"))], F_FOOT)
        x = draw_cells(d, x, y, em, " ⠄ ", c("dim"), grid)
        x = draw_segments(d, x, y + 2 * SCALE, [("CONTEXT ", c("dim"))], F_FOOT)
        for glyph, level_i in zip(state["glyphs"], state["inks"]):
            draw_braille(d, x, y, em, glyph, c("dim") if level_i == "dim" else ink)
            x += grid
        x += 26 * SCALE
        left = "  —  " if state["remaining"] is None else f"{state['remaining']}% left"
        x = draw_segments(d, x, y + 2 * SCALE, [(left.ljust(9), c("muted"))], F_FOOT)
        x = draw_segments(d, x, y + 2 * SCALE, [("  —  ", c("dim"))], F_FOOT)
        draw_segments(d, x, y + 2 * SCALE, [(captions[level], c("dim"))], F_FOOT)
        y += 76 * SCALE
    d.text((90 * SCALE, y + 10 * SCALE),
           "the surface moves only while tokens are landing, and stops when it matters",
           font=F_SMALL, fill=c("dim"))
    img.save(path)
    print(f"wrote {path}")


def render_activities(theme: Theme, data: dict, path: str) -> None:
    """The whole vocabulary as filmstrips: one row per kind of work."""
    rows = data["activities"]
    row_h, note_x = 54, 760
    height = 180 + len(rows) * row_h + 56
    # Narrower than the session shots: this one is a table, not a screen.
    width = 1180
    img = Image.new("RGB", (width * SCALE, height * SCALE), theme.v("bg0"))
    d = ImageDraw.Draw(img)
    c = theme.c
    em = 13 * SCALE

    d.text((90 * SCALE, 74 * SCALE), "THE INK VOCABULARY", font=F_TITLE, fill=c("mdHeading"))
    d.text((90 * SCALE, 100 * SCALE),
           "one animation per kind of work, three cells wide, played left to right",
           font=F_SMALL, fill=c("dim"))
    d.text((90 * SCALE, 122 * SCALE),
           "the tape advances per token chunk; everything else runs on its own clock; idle does not run at all",
           font=F_SMALL, fill=c("dim"))

    y = 176 * SCALE
    top = y - 14 * SCALE
    for row in rows:
        d.text((90 * SCALE, y + 2 * SCALE), row["verb"], font=F_FOOT, fill=c("text"))
        x = 200 * SCALE
        for frame in row["frames"]:
            # Idle is drawn dim because idle is the one state that never moves.
            colour = c("dim") if row["kind"] == "idle" else c("muted")
            x = draw_cells(d, x, y, em, frame, colour, advance=em * 0.58)
            x += 13 * SCALE
        d.text((note_x * SCALE, y + 2 * SCALE), row["note"], font=F_SMALL, fill=c("dim"))
        y += row_h * SCALE

    # A rule between the motion and the words about it.
    d.line([((note_x - 26) * SCALE, top), ((note_x - 26) * SCALE, y - 20 * SCALE)],
           fill=c("borderMuted"), width=SCALE)

    img.save(path)
    print(f"wrote {path}")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    data = ink()
    files = sorted(f for f in os.listdir(THEMES_DIR) if f.startswith("reckoner-") and f.endswith(".json"))
    for f in files:
        theme = Theme(os.path.join(THEMES_DIR, f))
        render_theme(theme, data, os.path.join(OUT_DIR, f.replace(".json", ".png")))
    exect = Theme(os.path.join(THEMES_DIR, "reckoner-exect.json"))
    render_footer_states(exect, data, os.path.join(OUT_DIR, "footer-states.png"))
    render_activities(exect, data, os.path.join(OUT_DIR, "footer-activities.png"))


if __name__ == "__main__":
    sys.exit(main())
