#!/usr/bin/env python3
"""Validate pi themes against the package contract (see THEMES.md).

Usage:
    python3 validate_themes.py [--strict] [name ...]

Checks (all hard failures unless noted):
  - JSON parses; "name" equals filename
  - vars: canonical skeleton present (bg0-3, line, muted0/1, text0/1)
  - vars: all 11 pa* panel vars present
  - colors: all 55 contract keys present (extras = warning)
  - no empty-string values anywhere
  - every non-hex colors value resolves to a vars entry
  - export block has pageBg/cardBg/infoBg
  - WCAG contrast(text0, bg0) >= 4.5 (3.0-4.5 = warning)
  - luminance ladder monotonicity for skeleton rungs (warning)
Exit 1 if any checked theme fails.
"""
import json, os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))

SKELETON = ['bg0', 'bg1', 'bg2', 'bg3', 'line', 'muted0', 'muted1', 'text0', 'text1']
PA_SET = ['paToolPendingBg', 'paToolSuccessBg', 'paToolErrorBg', 'paUserMessageBg',
          'paCustomMessageBg', 'paToolPanelBg', 'paSelectedBg', 'paDiffAddedBg',
          'paDiffRemovedBg', 'paDiffText', 'paDim']
COLOR_KEYS = ['accent', 'border', 'borderAccent', 'borderMuted', 'success', 'error',
              'warning', 'muted', 'dim', 'text', 'thinkingText', 'selectedBg',
              'userMessageBg', 'userMessageText', 'customMessageBg', 'customMessageText',
              'customMessageLabel', 'toolPendingBg', 'toolSuccessBg', 'toolErrorBg',
              'toolDiffAddedBg', 'toolDiffRemovedBg', 'toolPanelBg', 'toolTitle',
              'toolOutput', 'mdHeading', 'mdLink', 'mdLinkUrl', 'mdCode', 'mdCodeBlock',
              'mdCodeBlockBorder', 'mdQuote', 'mdQuoteBorder', 'mdHr', 'mdListBullet',
              'toolDiffAdded', 'toolDiffRemoved', 'toolDiffText', 'toolDiffContext',
              'syntaxComment', 'syntaxKeyword', 'syntaxFunction', 'syntaxVariable',
              'syntaxString', 'syntaxNumber', 'syntaxType', 'syntaxOperator',
              'syntaxPunctuation', 'thinkingOff', 'thinkingMinimal', 'thinkingLow',
              'thinkingMedium', 'thinkingHigh', 'thinkingXhigh', 'bashMode']
EXPORT_KEYS = ['pageBg', 'cardBg', 'infoBg']


def lum(hexc):
    r, g, b = (int(hexc[i:i+2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _lab(hexc):
    def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    h = hexc.lstrip('#')
    r, g, b = (lin(int(h[i:i + 2], 16) / 255) * 100 for i in (0, 2, 4))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 95.047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 100.0
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 108.883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b):
    """CIE76 ΔE — ~2 just noticeable, 5+ clearly different panels."""
    return sum((p - q) ** 2 for p, q in zip(_lab(a), _lab(b))) ** 0.5


SURFACE = os.environ.get('RECKONER_SURFACE', '#121212')   # terminal background pi draws on
PA_MIN_FROM_SURFACE = 6.0
PA_MIN_PAIRWISE = 5.0


def resolve(vars_, v, depth=0):
    if depth > 8 or not isinstance(v, str):
        return ''
    if v.startswith('#'):
        return v
    return resolve(vars_, vars_.get(v, ''), depth + 1)


def validate(path):
    errs, warns = [], []
    name = os.path.basename(path)[:-5]
    try:
        t = json.load(open(path))
    except Exception as e:
        return [f'JSON parse error: {e}'], warns
    if t.get('name') != name:
        errs.append(f'"name" is {t.get("name")!r}, filename says {name!r}')

    vars_ = t.get('vars', {})
    colors = t.get('colors', {})
    export = t.get('export', {})

    for k in SKELETON:
        if k not in vars_:
            errs.append(f'vars missing skeleton rung "{k}"')
    for k in PA_SET:
        if k not in vars_:
            errs.append(f'vars missing panel var "{k}"')
    for k in COLOR_KEYS:
        if k not in colors:
            errs.append(f'colors missing contract key "{k}"')
    extra = set(colors) - set(COLOR_KEYS)
    if extra:
        warns.append(f'colors has extra keys: {sorted(extra)}')

    for section, obj in (('vars', vars_), ('colors', colors), ('export', export)):
        for k, v in obj.items():
            if isinstance(v, str) and v == '':
                errs.append(f'{section}.{k} is an empty string')

    for k, v in colors.items():
        if isinstance(v, str) and v and not v.startswith('#'):
            if resolve(vars_, v) == '':
                errs.append(f'colors.{k} -> "{v}" does not resolve to a hex value')

    for k in EXPORT_KEYS:
        if k not in export:
            errs.append(f'export missing "{k}"')

    def rv(key):
        return resolve(vars_, vars_.get(key, ''))

    bg0, text0 = rv('bg0'), rv('text0')
    if bg0 and text0:
        c = contrast(text0, bg0)
        if c < 3.0:
            errs.append(f'contrast(text0, bg0) = {c:.2f} < 3.0')
        elif c < 4.5:
            warns.append(f'contrast(text0, bg0) = {c:.2f} < 4.5')

    # bg1 is a *recessed* inset (darker than the page on dark themes, lighter
    # on light ones) — the ascending/descending rule applies to bg0 -> bg2 -> bg3.
    ladder = [rv(k) for k in ['bg0', 'bg2', 'bg3']]
    if all(ladder):
        lums = [lum(h) for h in ladder]
        dark = lum(rv('bg0') or '#000000') < 0.5
        bad = (any(b < a - 1e-9 for a, b in zip(lums, lums[1:])) if dark
               else any(b > a + 1e-9 for a, b in zip(lums, lums[1:])))
        if bad:
            warns.append('bg0->bg2->bg3 ladder moves the wrong way for this polarity')

    # Surface rule (THEMES.md): panels must be visible on the terminal surface
    # and distinguishable from each other. Dark themes only.
    if lum(rv('bg0') or '#000000') < 0.5:
        panels = {k: rv(k) for k in PA_SET if k.endswith('Bg') and rv(k)}
        for k, h in panels.items():
            d = delta_e(h, SURFACE)
            if d < PA_MIN_FROM_SURFACE:
                errs.append(f'{k} {h} ΔE {d:.1f} from surface {SURFACE} (< {PA_MIN_FROM_SURFACE})')
        keys = list(panels)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                d = delta_e(panels[a], panels[b])
                if d < PA_MIN_PAIRWISE:
                    errs.append(f'{a} vs {b} ΔE {d:.1f} (< {PA_MIN_PAIRWISE}) — panels indistinguishable')

    return errs, warns


def main():
    strict = '--strict' in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith('--')]
    files = sorted(glob.glob(os.path.join(HERE, '*.json')))
    failed = 0
    for f in files:
        base = os.path.basename(f)[:-5]
        if names and base not in names:
            continue
        errs, warns = validate(f)
        for w in warns:
            print(f'  warn  {base}: {w}')
        if errs:
            failed += 1
            for e in errs:
                print(f'  FAIL  {base}: {e}')
        else:
            print(f'  ok    {base}')
    if strict and failed:
        print(f'\n{failed} theme(s) failed')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
