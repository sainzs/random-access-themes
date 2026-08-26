# The day cycle

Six pi themes named for the hours. Four of them — `madrugada`, `atardecer`,
`ocaso`, `anochecer` — were archived to [`archive/themes/pi/`](../archive/themes/pi/)
in the 2026-08-26 consolidation (hue-duplicates of healthy reckoners, or
structurally broken). Two remain as keepers: `amanecer` (Rosé Pine dawn) and
`mediodia` (Catppuccin Latte, the only light theme).

Five of the six were **ports**: their colours belong to upstream projects and
are reproduced unchanged. Attribution and the statement of changes Apache-2.0
requires are in [`NOTICE`](../NOTICE).

| Theme | Hour | Palette | Upstream | Licence |
|---|---|---|---|---|
| `madrugada` | before dawn | blue-violet night | [Tokyo Night](https://github.com/folke/tokyonight.nvim) | **Apache-2.0** |
| `amanecer` | dawn | rose and gold | [Rosé Pine](https://github.com/rose-pine/neovim) | MIT |
| `mediodia` | noon | Latte, ink on paper | Catppuccin | MIT |
| `atardecer` | late afternoon | burnt ochre, olive | [Gruvbox Material](https://github.com/sainnhe/gruvbox-material) | MIT |
| `ocaso` | sundown | amber on ink | none identified | — |
| `anochecer` | nightfall | mauve | [Catppuccin](https://github.com/catppuccin/catppuccin) | MIT |

`mediodia` closes the cycle and is the repo's **only light theme**. It is
Catppuccin Latte to `anochecer`'s Mocha — the two ends of the day sharing one
palette, which is why noon reads as the same design seen in daylight rather than
as a stranger among the five.

Its ramp **descends**. On paper, escalation is ink: a ramp that climbed would
fade toward its own background exactly when the model is working hardest. That
cost a change to `validate_thinking_ramps`, which until then assumed every theme
was painted on black — see `scripts/validate_theme.py`.

### madrugada

<p align="center"><img src="../assets/day-cycle/madrugada.png" alt="madrugada" width="720"/></p>

### amanecer

<p align="center"><img src="../assets/day-cycle/amanecer.png" alt="amanecer" width="720"/></p>

### atardecer

<p align="center"><img src="../assets/day-cycle/atardecer.png" alt="atardecer" width="720"/></p>

### ocaso

<p align="center"><img src="../assets/day-cycle/ocaso.png" alt="ocaso" width="720"/></p>

### anochecer

<p align="center"><img src="../assets/day-cycle/anochecer.png" alt="anochecer" width="720"/></p>

## Where they sit in the repo

They are **sources**, like the phosphor tubes and unlike the flavors: hand-held
JSON in `themes/pi/`, not generated from `palette/*.yaml`. Never run the palette
pipeline over them — it would overwrite the upstream colours that are the whole
point of a port.

The day cycle also has no exports. The phosphor family generates six terminal
formats from its pi themes; these do not, because the upstream projects already
publish their own terminal builds and a second-hand copy would drift from them.
`ocaso`, the one theme with no identified upstream, keeps the rule anyway.

## What was changed, and why

Only pi's six `thinking*` colours.

pi's thinking ramp says how hard the model is being driven, and none of these
upstream projects define one — it is a pi concept. The values that arrived with
the ports were assembled from whatever accents each palette happened to name, and
all five failed this repo's `validate_thinking_ramps` check on the day they were
tested:

| theme | what was wrong |
|---|---|
| `madrugada` | ramp did not climb; 75% and 79% lightness; wandered 91° of hue |
| `amanecer` | ramp did not climb; 78% and 83%; wandered 265° |
| `atardecer` | ramp did not climb; wandered 147° |
| `ocaso` | 77%; wandered 270° |
| `anochecer` | 76%, 81% and 86%; wandered 146° |

The limit is 40° of hue and 74% lightness. Every one of them also ended on its
palette's **error colour**, so asking for more reasoning looked like something
had broken — the exact defect the check was written to catch after watching a
recording of the footer.

Each ramp is now derived from its own palette's signature hue on the curve
`reckoner-scope` established: lightness 24.7 → 66.3%, saturation 27 → 67.4%, hue
held. The optional `thinkingMax` token was dropped throughout.

Syntax and interface colours are untouched and still match upstream exactly. The
one other role that moved is `bashMode`, repointed within each palette's own
colours so it stops colliding with `success`; `NOTICE` records it. pi/Prime
background roles the upstream palettes do not define — tool, diff, selection and
message surfaces — are authored here.
