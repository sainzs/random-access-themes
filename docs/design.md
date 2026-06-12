# Design

Random Access Theme is a dark terminal palette built around a single constraint:
**no warm hues**. No orange, no yellow, no purple, no red in syntax — only greens.

---

## Philosophy

Most dark themes scatter warm accents (orange strings, yellow keywords, purple types)
across the screen. They're readable, but visually noisy. The eye has to jump across
the color wheel on every glance.

Random Access Theme collapses the syntax palette to a single hue family — green —
differentiated by saturation and brightness rather than hue. The result is a screen
that reads like a single coherent surface instead of a collection of competing signals.

The background is true OLED black (`#060607`). Not "very dark gray." Black.
Every other color is measured against it.

---

## Color Roles

| Token     | Hex       | Role |
|-----------|-----------|------|
| `bg`      | `#060607` | OLED black — base background |
| `bg1`     | `#090a0b` | subtle step up (ANSI black, panel separation) |
| `bg2`     | `#101214` | visible panel borders |
| `surface` | `#0b0c0e` | card / message backgrounds |
| `overlay` | `#1a1c20` | selection, popovers, inactive splits |
| `text`    | `#d8efe9` | primary text — green-tinted near-white |
| `subtle`  | `#9cb7af` | secondary labels, borders |
| `dimText` | `#6f8d86` | muted, comments, disabled |
| `mint`    | `#00ffb2` | **hero accent** — primary brand color |
| `green`   | `#4ade80` | vivid green — success, functions |
| `teal`    | `#35d5c5` | cool teal — operators, borders |
| `jade`    | `#66e3c4` | soft jade — headings, thinking |
| `aqua`    | `#8bf5dd` | bright aqua — numbers, highlights |
| `emerald` | `#26c994` | deep emerald — errors (no warm red) |
| `lime`    | `#a2e5b8` | muted lime — strings, warnings |

---

## Syntax Mapping

| Syntax role    | Color     | Reasoning |
|----------------|-----------|-----------|
| Keywords       | jade      | Prominent but not shouting |
| Functions      | green     | Action — vivid |
| Strings        | lime      | Calm, readable |
| Numbers        | aqua      | Distinct from strings |
| Types          | teal      | Structural — cooler tone |
| Operators      | emerald   | Functional — deeper |
| Comments       | dimText   | Recede naturally |
| Punctuation    | subtle    | Structural, unobtrusive |
| Variables      | text      | Neutral — context carries meaning |

---

## The No-Red Decision

Most palettes use a warm red for errors. This palette uses **emerald** (`#26c994`)
for errors and the ANSI red position. This is an intentional departure.

Reasons:
1. Red on near-black backgrounds requires high saturation to be readable — it fights
   the background rather than sitting on it.
2. In a green-family palette, a warm red reads as a foreign object — jarring rather
   than informative.
3. Emerald provides sufficient semantic differentiation (it's the darkest green,
   lower value than mint/green) without breaking the palette harmony.

If you need warm red in your workflow (e.g., git diffs, build errors), your terminal
emulator's ANSI red slot uses emerald, which is still clearly distinct from success
greens in terminal output.

---

## ANSI 16-Color Palette

The ANSI palette maps all 16 positions to green-family colors. Standard ANSI semantics
are preserved by hue-family brightness, not by hue:

| Slot | Name            | Hex       | Mapped to |
|------|-----------------|-----------|-----------|
| 0    | black           | `#090a0b` | bg1 (near-invisible — intentional) |
| 1    | red             | `#26c994` | emerald |
| 2    | green           | `#4ade80` | green |
| 3    | yellow          | `#a2e5b8` | lime |
| 4    | blue            | `#00ffb2` | mint (hero) |
| 5    | magenta         | `#35d5c5` | teal |
| 6    | cyan            | `#66e3c4` | jade |
| 7    | white           | `#d8efe9` | text |
| 8    | bright black    | `#6f8d86` | dimText |
| 9    | bright red      | `#00ffb2` | mint (hero) |
| 10   | bright green    | `#4ade80` | green |
| 11   | bright yellow   | `#8bf5dd` | aqua |
| 12   | bright blue     | `#00ffb2` | mint |
| 13   | bright magenta  | `#35d5c5` | teal |
| 14   | bright cyan     | `#66e3c4` | jade |
| 15   | bright white    | `#d8efe9` | text |

**Note:** ANSI black (0) at `#090a0b` is intentionally near-invisible vs `bg`.
It is a background-differentiation color, never used as foreground text.

---

## Contrast Targets

All foreground colors meet **WCAG AA** (≥ 4.5:1) against `bg`. Most reach **AAA**
(≥ 7.0:1). Run the full matrix:

```bash
python3 scripts/contrast_matrix.py
```

Selected ratios vs `#060607`:

| Color   | Ratio  | Grade |
|---------|--------|-------|
| text    | 16.82  | AAA   |
| mint    | 15.38  | AAA   |
| aqua    | 15.63  | AAA   |
| green   | 11.62  | AAA   |
| emerald | 9.51   | AAA   |
| subtle  | 9.46   | AAA   |
| dimText | 5.62   | AA    |

---

## Font Recommendation

Designed with **Berkeley Mono Variable** (Retina weight, ~450) on macOS.

- The Retina weight fills strokes without looking heavy on OLED displays.
- The green-tinted foreground (`#d8efe9`) works well with Berkeley Mono's neutral letterforms.
- Fallback: **GeistMono Nerd Font** for icon glyphs.

Any monospace font works. The palette does not depend on a specific font.

---

## Terminal Support

| Terminal        | Format                          | Notes |
|-----------------|---------------------------------|-------|
| Ghostty         | `.conf`                         | Include or paste into config |
| WezTerm         | `.toml` (color scheme file)     | Place in `~/.config/wezterm/colors/` |
| iTerm2          | `.itermcolors`                  | Import via Profiles → Colors → Import |
| Alacritty       | `.toml`                         | Import via `[import]` section |
| kitty           | `.conf`                         | `include` in kitty.conf |
| Windows Terminal | `.json`                        | Paste into `schemes` array in settings |
| Pi (coding agent)| `.json`                        | Copy to `~/.pi/agent/themes/` |
