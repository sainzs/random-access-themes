"""Generate light (-sol) twins for the phosphor/day-cycle themes.

Canon lives in ~/Code/projects/random-access-themes/themes/pi/ (the phosphor
tubes and amanecer are hand-authored sources). Sols are derived from those
sources: every var keeps its hue identity; surfaces move to a paper ladder,
ink darkens, accents take the lightest dark-on-paper value clearing WCAG.
Output lands in the repo's themes/pi/ so install.sh links it like any other
theme and validate_theme.py gates it like any other theme.

Rules taken from the repo (AGENTS.md / docs/manifest.md):
- union token set is kept (schema serves pi AND Prime)
- thinking ramps DESCEND in lightness on paper (escalation = darker/more)
- day-cycle ports (mediodia) are upstream-fidelity: no sol, no tuning
"""

import colorsys
import copy
import glob
import json
import os

REPO_PI = os.path.expanduser(
    "~/Code/projects/random-access-themes/themes/pi")
PORTS = {"mediodia"}          # upstream fidelity: never generate or tune
HAND_SOL = {"amanecer-sol"}   # maintained by hand (upstream Dawn hexes)

PAPER = [0.965, 0.945, 0.915, 0.88]
LINE_L, INK_L, INK1_L, MUTED_L, MUTED0_L = 0.79, 0.15, 0.28, 0.36, 0.43
PANEL_L, SELECTED_L = 0.93, 0.87
WHITE = "#eaeaea"  # worst-case light terminal bg: darker than white or warm paper

GATES = {  # token-class -> min contrast vs worst-case terminal bg
    "syntax": 4.5, "md": 4.5, "toolDiff": 4.5,
}
SOFT = {"syntaxComment", "syntaxOperator", "syntaxPunctuation", "mdQuote"}
THINK_STEPS = [(0.54, 0.22), (0.49, 0.30), (0.44, 0.38),
               (0.39, 0.48), (0.34, 0.60), (0.29, 0.72)]


def hsl(hexs_):
    r, g, b = (int(hexs_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return colorsys.rgb_to_hls(r, g, b)


def hexs(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{round(r * 255):02x}{round(g * 255):02x}{round(b * 255):02x}"


def lum(hexs_):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hexs_[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(fg, bg):
    a, b = sorted((lum(fg), lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def resolve(t, key):
    val = t["colors"].get(key)
    for _ in range(6):
        if isinstance(val, str) and val.startswith("#"):
            return val
        val = t.get("vars", {}).get(val) if isinstance(val, str) else None
    return None


def dark_on_paper(hexv, ratio):
    """Lightest dark-on-paper version of hexv keeping hue, clearing ratio."""
    h, _, s = hsl(hexv)
    for l in [x / 100 for x in range(60, 14, -1)]:
        s_cap = min(max(s, 0.12), 0.9, max(0.15, (0.94 - l) * 2.4))
        if contrast(hexs(h, l, s_cap), WHITE) >= ratio:
            return hexs(h, l, s_cap)
    return hexs(h, 0.25, min(s, 0.8))


def tint(hexv, l, s_cap=0.22):
    h, _, s = hsl(hexv)
    return hexs(h, l, min(s, s_cap))


def thinking_ladder(accent_hex):
    """Six steps, DESCENDING lightness on paper, hue from the theme accent."""
    h, _, _ = hsl(accent_hex)
    return [hexs(h, l, s) for l, s in THINK_STEPS]


def transform(name):
    t = json.load(open(os.path.join(REPO_PI, f"{name}.json")))
    sol = copy.deepcopy(t)
    sol["name"] = f"{name}-sol"
    vars_, out = t["vars"], sol["vars"]

    surfaces = [k for k in vars_ if k.startswith("bg") or k in ("surface", "overlay")]
    ladder = {k: PAPER[min(i, len(PAPER) - 1)]
              for i, k in enumerate(sorted(surfaces, key=lambda k: lum(vars_[k])))}

    for k, v in vars_.items():
        h, l, s = hsl(v)
        if k in ladder:
            out[k] = hexs(h, ladder[k], min(s * 0.35, 0.35))
        elif k == "line":
            out[k] = hexs(h, LINE_L, min(s * 0.5, 0.25))
        elif k == "muted0":
            out[k] = dark_on_paper(v, 3.8)
        elif k in ("muted1", "subtle"):
            out[k] = dark_on_paper(v, 4.5)
        elif k in ("text", "text0", "paDiffText"):
            out[k] = dark_on_paper(v, 7.0)
        elif k in ("text1", "dimText"):
            out[k] = dark_on_paper(v, 4.5)
        elif k == "paDim":
            out[k] = dark_on_paper(v, 3.0)
        elif k == "paSelectedBg":
            out[k] = tint(v, SELECTED_L)
        elif k == "paToolSuccessBg":
            out[k] = tint(v, 0.92)
        elif k == "paToolErrorBg":
            out[k] = tint(v, 0.90)
        elif k in ("paDiffAddedBg", "paDiffRemovedBg"):
            out[k] = tint(v, 0.90)
        elif k.startswith("pa"):
            out[k] = tint(v, PANEL_L)
        else:
            out[k] = dark_on_paper(v, 4.5)

    accent = resolve(t, "accent") or "#333333"
    ramp = dict(zip(["thinkingOff", "thinkingMinimal", "thinkingLow",
                     "thinkingMedium", "thinkingHigh", "thinkingXhigh"],
                    thinking_ladder(accent)))
    for tok in list(sol["colors"]):
        ref = sol["colors"][tok]
        if tok in ramp:
            sol["colors"][tok] = ramp[tok]
            continue
        if tok in SOFT:
            gate = 3.8
        elif any(tok.startswith(p) for p in GATES):
            gate = GATES[next(p for p in GATES if tok.startswith(p))]
        else:
            continue
        src = resolve(t, tok)    # hue source: the ORIGINAL theme's color
        cur = resolve(sol, tok)  # current sol value (post var transform)
        if src and (cur is None or contrast(cur, WHITE) < gate):
            sol["colors"][tok] = dark_on_paper(src, gate)

    ex = sol.get("export")
    if ex:
        ex["pageBg"], ex["cardBg"], ex["infoBg"] = (
            out.get("bg0", ex.get("pageBg")), out.get("bg1", ex.get("cardBg")),
            out.get("bg2", ex.get("infoBg")))
    return sol


def main():
    names = sorted(os.path.basename(p)[:-5]
                   for p in glob.glob(os.path.join(REPO_PI, "*.json")))
    for name in names:
        if name in PORTS or name.endswith("-sol"):
            continue
        if f"{name}-sol" in HAND_SOL:
            print(f"skip {name}-sol (hand-authored)")
            continue
        sol = transform(name)
        path = os.path.join(REPO_PI, f"{name}-sol.json")
        json.dump(sol, open(path, "w"), indent=2, ensure_ascii=False)
        open(path, "a").write("\n")
        print(f"wrote {os.path.basename(path)}")


if __name__ == "__main__":
    main()
