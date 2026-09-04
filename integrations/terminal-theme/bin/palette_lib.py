"""Shared loader: theme.toml with accents resolved from the pi theme JSONs."""
import colorsys, json, pathlib, tomllib

HERE = pathlib.Path(__file__).resolve().parent.parent
PI_THEMES = HERE.parent.parent / "themes" / "pi"

def _rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def _hex(t): return "#%02x%02x%02x" % t
def hot(h, dl=0.08, ds=0.35):
    """The tubes' "Hot" variant: same hue, lighter AND more saturated. A plain
    white blend greys out toward the sage bright_green and fails the dE gate."""
    r, g, b = (c / 255 for c in _rgb(h)); hh, l, ss = colorsys.rgb_to_hls(r, g, b)
    return _hex(tuple(round(c * 255) for c in colorsys.hls_to_rgb(hh, min(1.0, l + dl), min(1.0, ss + ds))))

def pi_var(ref):
    """'reckoner-scope:text0' -> '#6fe392' (follows var refs)."""
    name, var = ref.split(":", 1)
    theme = json.loads((PI_THEMES / f"{name}.json").read_text())
    v, seen = var, set()
    while not str(v).startswith("#"):
        if v in seen or v not in theme["vars"]: raise KeyError(f"{ref}: unresolved")
        seen.add(v); v = theme["vars"][v]
    return v.lower()

def load():
    T = tomllib.loads((HERE / "theme.toml").read_text())
    for term, spec in T["terminals"].items():
        if "accent_from" in spec: spec["accent"] = pi_var(spec["accent_from"])
        if "accent_bright_from" in spec: spec["accent_bright"] = pi_var(spec["accent_bright_from"])
        spec.setdefault("accent_bright", hot(spec["accent"]))
    return T
