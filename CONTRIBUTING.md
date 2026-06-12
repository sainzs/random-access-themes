# Contributing

Thanks for helping improve Random Access Theme.

## One source of truth

**Only edit `palette/random-access-theme.yaml`.**

All files in `themes/` are generated. Do not edit them directly — your changes
will be overwritten the next time the generator runs.

## Local workflow

```bash
# 1. Edit the palette
$EDITOR palette/random-access-theme.yaml

# 2. Regenerate
python3 scripts/generate.py

# 3. Validate
python3 scripts/validate_theme.py

# 4. Check contrast
python3 scripts/contrast_matrix.py
```

## Requirements

- Python 3.9+
- `pyyaml`: `pip install pyyaml`

## Style rules

- All colors must be lowercase hex (`#rrggbb`)
- All foreground colors must pass WCAG AA (≥ 4.5:1) vs `bg`
- ANSI black (position 0) is exempt — it is a background color, not text
- Palette hue must stay in the green family — no orange, purple, or warm red in syntax roles

## Pull request checklist

- [ ] Only `palette/random-access-theme.yaml` is manually edited
- [ ] `python3 scripts/generate.py` was run
- [ ] `python3 scripts/validate_theme.py` passes
- [ ] `CHANGELOG.md` updated
- [ ] README updated if behavior changed
