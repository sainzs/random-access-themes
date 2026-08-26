#!/usr/bin/env python3
"""Render a visual preview card (PNG) for a pi theme JSON.

Usage: python3 render_preview.py [theme-name ...]   # default: all themes
Cards land in previews/<name>.png next to the themes dir.
Broken (empty/unresolvable) colors render as magenta so bugs are visible.
"""
import json, os, sys, glob
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'previews')
FONT_PATH = '/System/Library/Fonts/Menlo.ttc'
W, MARGIN = 1280, 40
BROKEN = '#ff00ff'


def load_fonts():
    try:
        return (ImageFont.truetype(FONT_PATH, 22, index=0),
                ImageFont.truetype(FONT_PATH, 22, index=1),
                ImageFont.truetype(FONT_PATH, 30, index=1),
                ImageFont.truetype(FONT_PATH, 17, index=0))
    except Exception:
        f = ImageFont.load_default()
        return f, f, f, f

F, FB, FTITLE, FS = load_fonts()


def resolver(theme):
    vars_ = theme.get('vars', {})
    def res(v):
        seen = set()
        while isinstance(v, str) and not v.startswith('#') and v not in seen:
            seen.add(v)
            v = vars_.get(v, '')
        return v if isinstance(v, str) and v.startswith('#') else BROKEN
    return res


def text_size(draw, s, font):
    b = draw.textbbox((0, 0), s, font=font)
    return b[2] - b[0], b[3] - b[1]


def chip(draw, x, y, w, h, fill, label, sub=None, border='#444444', label_fg=None):
    draw.rectangle([x, y, x + w, y + h], fill=fill, outline=border, width=1)
    fg = label_fg or ('#000000' if _lum(fill) > 0.5 else '#ffffff')
    if fill == BROKEN:
        fg = '#000000'
    draw.text((x + 12, y + 8), label, font=FS, fill=fg)
    if sub:
        draw.text((x + 12, y + h - 24), sub, font=FS, fill=fg)


def _lum(hexc):
    if not hexc.startswith('#') or len(hexc) < 7:
        return 0.0
    r, g, b = (int(hexc[i:i+2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def render(theme):
    res = resolver(theme)
    c = {k: res(v) for k, v in theme.get('colors', {}).items()}
    v = theme.get('vars', {})
    name = theme.get('name', '?')
    bg = res(v.get('bg0') or v.get('bg') or '#111111')
    muted_lab = c.get('muted', '#888888')

    H = 1900
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)
    x, y = MARGIN, 30

    # header
    d.text((x, y), f'pi theme · {name}', font=FTITLE, fill=c.get('text', '#ffffff'))
    y += 46
    accent = c.get('accent', BROKEN)
    d.rectangle([x, y, x + 60, y + 26], fill=accent)
    d.text((x + 74, y), f'accent {accent}', font=F, fill=muted_lab)
    y += 48

    def section(title):
        nonlocal y
        y += 18
        d.text((x, y), title.upper(), font=FS, fill=muted_lab)
        y += 28

    # neutral ladder
    section('neutral ladder')
    nx = x
    for key in ['bg0', 'bg1', 'bg2', 'bg3', 'line', 'muted0', 'muted1', 'text0', 'text1']:
        raw = v.get(key)
        if raw is None:
            chip(d, nx, y, 124, 72, BROKEN, key, 'MISSING')
        else:
            chip(d, nx, y, 124, 72, res(raw), key, raw)
        nx += 132
    y += 86

    # panel backgrounds
    section('pa* panels')
    pa_keys = ['paToolPendingBg', 'paToolSuccessBg', 'paToolErrorBg', 'paUserMessageBg',
               'paCustomMessageBg', 'paToolPanelBg', 'paSelectedBg', 'paDiffAddedBg',
               'paDiffRemovedBg', 'paDiffText', 'paDim']
    nx, ny = x, y
    for key in pa_keys:
        raw = v.get(key)
        fill = res(raw) if raw else BROKEN
        chip(d, nx, ny, 280, 60, fill, key, raw or 'MISSING')
        nx += 292
        if nx + 280 > W - MARGIN:
            nx, ny = x, ny + 68
    y = ny + 74

    # accents & semantics
    section('accents · semantics · thinking ladder')
    nx = x
    for key in ['accent', 'success', 'error', 'warning', 'bashMode',
                'thinkingOff', 'thinkingMinimal', 'thinkingLow',
                'thinkingMedium', 'thinkingHigh', 'thinkingXhigh']:
        chip(d, nx, y, 132, 64, c.get(key, BROKEN), key.replace('thinking', 'tk'), c.get(key, ''))
        nx += 140
        if nx + 132 > W - MARGIN:
            nx = x
            y += 72
    y += 88

    # mock transcript
    section('mock transcript')
    # user message
    d.rectangle([x, y, W - MARGIN, y + 56], fill=c.get('userMessageBg', BROKEN))
    d.text((x + 14, y + 8), 'userMessage', font=FS, fill=c.get('muted', '#888'))
    d.text((x + 14, y + 28), 'how do we consolidate the theme package?', font=F,
           fill=c.get('userMessageText', BROKEN))
    y += 66
    # tool panel
    d.rectangle([x, y, W - MARGIN, y + 150], fill=c.get('toolPanelBg', BROKEN),
                outline=c.get('border', '#333'), width=1)
    d.text((x + 14, y + 10), '● toolPanel · bash', font=F, fill=c.get('toolTitle', BROKEN))
    d.text((x + 14, y + 40), '$ python3 validate_themes.py --strict', font=F,
           fill=c.get('toolOutput', BROKEN))
    rows = [('toolPendingBg', '  pending…'), ('toolSuccessBg', '✓ 8 themes pass'),
            ('toolErrorBg', '✗ ocaso: empty text')]
    ry = y + 72
    for bgk, line in rows:
        d.rectangle([x + 10, ry, W - MARGIN - 10, ry + 24], fill=c.get(bgk, BROKEN))
        d.text((x + 16, ry + 2), line, font=F,
               fill=c.get('success' if 'Success' in bgk else 'error' if 'Error' in bgk else 'warning', BROKEN))
        ry += 26
    y += 162
    # diff
    d.rectangle([x, y, W - MARGIN, y + 26], fill=c.get('toolDiffAddedBg', BROKEN))
    d.text((x + 14, y + 2), '+ "bg3": "#332412",', font=F, fill=c.get('toolDiffAdded', BROKEN))
    d.rectangle([x, y + 26, W - MARGIN, y + 52], fill=c.get('toolDiffRemovedBg', BROKEN))
    d.text((x + 14, y + 28), '- "text": "",', font=F, fill=c.get('toolDiffRemoved', BROKEN))
    d.text((x + 14, y + 56), '  "line": "#5a3f1a",  // context', font=F,
           fill=c.get('toolDiffContext', BROKEN))
    y += 92
    # markdown + syntax
    d.text((x, y), '# mdHeading', font=FB, fill=c.get('mdHeading', BROKEN))
    y += 34
    d.text((x, y), 'mdLink', font=F, fill=c.get('mdLink', BROKEN))
    tw = text_size(d, 'mdLink', F)[0]
    d.text((x + tw + 10, y), '(mdLinkUrl)', font=F, fill=c.get('mdLinkUrl', BROKEN))
    tw2 = text_size(d, '(mdLinkUrl)', F)[0]
    d.text((x + tw + tw2 + 24, y), '`mdCode`', font=F, fill=c.get('mdCode', BROKEN))
    y += 32
    d.rectangle([x, y, x + 6, y + 30], fill=c.get('mdQuoteBorder', BROKEN))
    d.text((x + 18, y + 4), 'mdQuote — stayed on the gold standard', font=F,
           fill=c.get('mdQuote', BROKEN))
    y += 40
    d.rectangle([x, y, W - MARGIN, y + 34], fill=res(v.get('bg1', '#181818')),
                outline=c.get('mdCodeBlockBorder', BROKEN), width=1)
    d.text((x + 12, y + 6), 'mdCodeBlock', font=F, fill=c.get('mdCodeBlock', BROKEN))
    y += 46
    # syntax line
    sx = x
    for tok, key in [('def ', 'syntaxKeyword'), ('reckon', 'syntaxFunction'),
                     ('(path', 'syntaxPunctuation'), (': str', 'syntaxType'),
                     (') ', 'syntaxPunctuation'), ('= ', 'syntaxOperator'),
                     ('"gold"', 'syntaxString'), (' + ', 'syntaxOperator'),
                     ('42', 'syntaxNumber'), ('  # comment', 'syntaxComment')]:
        fill = c.get(key, BROKEN)
        d.text((sx, y), tok, font=F, fill=fill)
        sx += text_size(d, tok, F)[0]
    d.text((x, y + 30), 'syntaxVariable', font=F, fill=c.get('syntaxVariable', BROKEN))
    y += 70

    # crop to content
    img = img.crop((0, 0, W, min(y + 20, H)))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f'{name}.png')
    img.save(path)
    return path


def main():
    names = sys.argv[1:]
    files = sorted(glob.glob(os.path.join(HERE, '*.json')))
    themes = []
    for f in files:
        t = json.load(open(f))
        if not names or t.get('name') in names:
            themes.append(t)
    for t in themes:
        print(render(t))

if __name__ == '__main__':
    main()
