# Demo

Random Access Themes is palette-first: the public previews are rendered from the
same YAML palette data that generates terminal exports.

![Random Access Theme terminal preview](../assets/preview.svg)

## What This Proves

- The flagship Random Access palette is rendered without external syntax-theme
  guessing.
- The preview uses the same canonical colors as
  `palette/random-access-theme.yaml`.
- The release visuals are reproducible with the repo scripts.
- The PNG preview in `assets/preview.png` is a portable export of the generated
  SVG for social cards and package listings.

## Rebuild

```bash
make visuals
make check
```

`make visuals` refreshes `assets/flavors.svg`, `assets/palette-strips.svg`, and
`assets/preview.svg`. `make check` regenerates terminal themes, validates the
palette export set, and runs the WCAG contrast report.

## Hosting Notes

This page is intentionally plain Markdown so it works on GitHub today and can
later become the source for a small static docs site on Netlify, Vercel, or
GitHub Pages.
