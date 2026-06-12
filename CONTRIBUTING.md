# Contributing

Thanks for helping improve Random Access Themes.

## Sources of truth

- **Palettes:** edit `palette/*.yaml`
- **Repo visuals:** generated from palette data by `scripts/render_repo_visuals.py`
- **Theme outputs:** generated into `themes/`

Do not hand-edit generated files in `themes/` or generated README visuals in `assets/*.svg` unless you are also updating the generator.

## Local workflow

```bash
# 1. Edit one or more palettes
$EDITOR palette/random-access-theme.yaml

# 2. Regenerate theme outputs
python3 scripts/generate.py

# 3. Regenerate README visuals
python3 scripts/render_repo_visuals.py

# 4. Validate structure and freshness
python3 scripts/validate_theme.py

# 5. Check contrast
python3 scripts/contrast_matrix.py
```

## Requirements

- Python 3.9+
- `pyyaml`: `pip install pyyaml`

## Style rules

- All colors must be lowercase hex (`#rrggbb`)
- All foreground colors must pass WCAG AA (≥ 4.5:1) vs `bg`
- ANSI black (position 0) is exempt — it is a background color, not text
- Palette hue families should remain intentional and coherent per flavor

## Pull request checklist

- [ ] Only palette YAML, docs, or generator scripts were edited manually
- [ ] Generated files were refreshed where needed
- [ ] `python3 scripts/validate_theme.py` passes
- [ ] `CHANGELOG.md` updated if needed
- [ ] `README.md` updated if behavior or visuals changed
