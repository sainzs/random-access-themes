# Consolidation notes — 2026-08-26

Method: every preview card was inspected by pixel-sampling the rendered PNGs
(`render_preview.py` paints empty/unresolvable colors as magenta `#ff00ff`, so
defects are literally visible). Coordinates below refer to the 1280px-wide cards.

## What I saw in the 5 keeper cards

- **reckoner-exect (reference)** — zero magenta anywhere. The page renders true
  `#16100a` amber-black; the `paToolSuccessBg` chip is a deep moss `#1c2913` and
  the transcript's error row an ember `#371b12`, both clearly warm-tinted against
  the page rather than neutral gray. The `bg1` ladder chip (`#100b06`) is visibly
  *darker* than the page — the recessed inset — and `paDim` renders `#796344`, a
  desaturated amber-gray just dimmer than `muted0` (`#8a6224`). Accent chip is
  bright phosphor `#ffd280`.
- **amanecer** — the page falls back to generic `#111111` because no `bg0` var
  existed; Rosé's base `#191724` never appeared. Magenta in six places: the
  header title (empty `colors.text`), all nine neutral-ladder chips stamped
  MISSING, the `paDim` chip, the `userMessageText` transcript line, the
  `mdCodeBlock` label inside a fallback `#181818` rect, and the `syntaxVariable`
  token. The ten existing `pa*` chips did render as proper Rosé tints
  (`#202d21` success, `#36202a` error, `#452939` diff-removed).
- **mediodia** — the light theme was rendering on a near-black `#111111`
  fallback page, so its verified-light panels (`#e8e7ee` user-message,
  `#dceadd` success, `#c9e3cb` diff-added, `#e5c8cf` diff-removed) floated like
  pale islands on darkness — noon daylight nowhere in sight. Same six magenta
  bands as amanecer (header, 9 ladder chips, paDim chip, three text roles).
- **reckoner-factory** — clean `#020202` slate page, orange accent; the *only*
  magenta was exactly two ladder chips: the `bg3` and `line` slots, MISSING
  because those rungs lived under the names `border0`/`border1`. Panels
  (`#241a15` tool panel, `#461417` diff-removed) rendered fine.
- **reckoner-dusk** — lavender page `#1c1b29` fully rendered; the single magenta
  chip on the whole card was `paDim` (MISSING). `paToolSuccessBg` `#223223` and
  user-message panel `#2c2a3b` read as correct dark tints.

## Derivation choices per keeper

### amanecer (Rosé Pine dawn, rose 2°)
- Skeleton taken from the native ramp: `bg0=base #191724`, `bg2=surface #1f1d2e`,
  `bg3=overlay #26233a`, `line=highlightMed #403d52` (kept as-is — its 2.4×
  luminance step over bg3 is proper accent-border duty), `muted0=mutedv #6e6a86`,
  `muted1=subtle #908caa`, `text0=text #e0def4`.
- `bg1 #100e17` derived as a 0.62× deepening of base (mirroring exect's
  bg1-darker-than-bg0 recess `#100b06` vs `#16100a`); Rosé has no native color
  darker than base, so this is a taste derivation in the same indigo hue.
- `text1 #bcb9d3` derived ~0.68 luminance of text0 toward subtle (exect's
  text1/text0 ratio is 0.70) — a dimmer lavender reading tone, not a palette
  foreigner. `paDim #65617a`: desaturated mauve-gray just below muted0, mirroring
  exect's paDim↔muted0 relationship (`#796344` vs `#8a6224`).
- Five empties wired per exect: `text/userMessageText/customMessageText→text0`,
  `mdCodeBlock→text1`, `syntaxVariable→text0`. Neutral color refs rewired to
  canonical names (`subtle→muted1`, `mutedv→muted0`, `highlightMed→line`,
  `overlay→bg3`, `surface→bg2`); identity accents love/gold/rose/pine/foam/iris
  and the rose thinking-ladder untouched. `export` re-pinned to bg0/bg1/bg2.

### mediodia (Catppuccin Latte, the only light theme — everything inverts)
- `bg0=mantle #e6e9ef` (page), `bg1=base #eff1f5` introduced — the true Latte
  base that was missing; on a light theme the recessed inset is *lighter* than
  the page, mirroring exect's darker-bg1 move, so the mdCodeBlock well now
  renders as a clean white card. Then descending: `bg2=crust #dce0e8`,
  `bg3=surface0 #ccd0da`, `line=surface1 #bcc0cc`.
- `muted0=overlay0 #9ca0b0` (dimmer, lower contrast on light), `muted1=overlay1
  #8c8fa1` (more readable), `text0=text #4c4f69` (darkest ink), `text1=subtext
  #5c5f77`.
- `pa*` panels pixel-verified as light tints already (`#dceadd`, `#c9e3cb`,
  `#e5c8cf`, …) — left untouched; `paDim #afb3c1` blended between overlay0 and
  surface0 as the quiet dim tone. Same five empty fixes; `border` stays on the
  old surface1 rung (now `line`), preserving the theme's original border taste.
- `export` re-pinned: pageBg `#e6e9ef`, cardBg `#eff1f5` (light card on a
  hair-darker page), infoBg `#dce0e8`.

### reckoner-factory (orange 20°)
- Pure rename, no re-skin: `border0 #2e2c2b → bg3`, `border1 #3d3a39 → line`,
  done in-place so var order matches exect (bg0…bg3, line, muted0…).
- Five color refs re-pointed: `border→bg3`; `borderMuted`, `mdCodeBlockBorder`,
  `mdQuoteBorder`, `mdHr→line`. `borderAccent` deliberately stays `accent3` —
  the orange ladder (accent/accent2/accent3) is the identity.
- No aliases left behind; `paSyntaxComment` kept (still referenced). Card had no
  other defects — panels and thinking ladder were already reckoner-grade.

### reckoner-dusk (violet 261°)
- One rung only: added `paDim #706985` (the hex `colors.dim` already pointed at
  via `paPhosphorTrace`) immediately after `paDiffText`, and re-pointed
  `colors.dim→paDim`.
- `paPhosphorTrace`/`paPhosphorTrace2` vars untouched — a footer extension reads
  them (`thinkingOff` still references `paPhosphorTrace2`). Nothing else changed.

## Roster verdicts (archive candidates vs. their reckoner hue-mates)

- **amnesiac** — archive: confirmed — blue accent `#7b93ff` duplicates
  reckoner-wopr's 205° blue family (`#6fc4ff`, zero-magenta card); amnesiac's own
  card shows magenta ladder chips and a magenta paDim chip (canonical rungs +
  paDim missing), and it shares the same off-contract var template as veridis.
- **anochecer** — archive: confirmed — violet `#cba6f7` (Catppuccin Mocha mauve)
  duplicates reckoner-dusk's 261° violet; its card is fully broken — magenta
  header title, nine MISSING ladder chips, magenta paDim chip and magenta
  transcript/code-block/syntax text.
- **atardecer** — archive: confirmed — amber `#d8a657` sits ~2° from
  reckoner-exect's 39° amber signature; card fully broken with magenta header and
  all skeleton/paDim chips MISSING.
- **madrugada** — archive: confirmed — blue `#7aa2f7` duplicates reckoner-wopr;
  fully broken card (six magenta bands incl. header), no bg0 var at all.
- **ocaso** — archive: confirmed — amber `#d4a84b` duplicates exect; fully broken
  card with the same empty-text magenta signature the roster notes recorded.
- **random-access-theme** — archive: confirmed — near-identical twin of veridis:
  same var template, same accent `#00ffb2`, same pure-black `#000000` page, same
  magenta ladder+paDim chips (a diff shows only a `dim` ref name and trivial
  thinking-ladder hex drift). Green is owned by the clean reckoner-scope.
- **veridis** — archive: confirmed — green-phosphor `#00ffb2` duplicates
  reckoner-scope (`#a8ffc2`, zero magenta); veridis renders on true `#000000`
  with magenta ladder and paDim chips, and is random-access-theme's twin.
- **voyager** — archive: confirmed — teal `#2ccfc0` duplicates
  reckoner-darkspace's 174° teal (`#7dfff2`, clean card); voyager is the same
  shared off-contract template (bg/bg1/bg2/surface/overlay/dimText…), rendering
  with magenta ladder + paDim chips.

No dissents: every archive candidate is either a hue-duplicate of a healthy
reckoner or structurally broken (or both), as seen on the cards.

## Roster revision — keep the flagship

`random-access-theme` was listed as an archive candidate (hue-adjacent to
reckoner-scope). Reconsidered after reading the repo: it is the package
flagship (the repo is named for it; `scripts/validate_theme.py` and
`scripts/get.sh` pin it as the canonical pi theme). Scope is phosphor green
138° / 34% on a tinted `#0a120c`; random-access is electric mint 162° / 100%
on true OLED `#000000` — 24° and a saturation world apart. Kept as the ninth
keeper and normalized at the source (`pi_skeleton()` in `scripts/generate.py`).
The seven remaining candidates were archived to `archive/themes/pi/`.

## random-access-theme — source-level normalization (round 2)

Round 1 patched installed JSONs by hand; this round moved the fix upstream into
the generator, so the contract is now a property of the source, not of a patch.

**Emitter change** (`scripts/generate.py` in the random-access-themes repo):
`gen_pi` now calls a new `pi_skeleton(c)` deriver and merges its rungs into
every pi JSON it emits — same rules for all four ramp palettes
(amnesiac/veridis/voyager/random-access-theme), palette-relative, nothing
hardcoded per theme:

- `bg0 = palette.bg1` (the practical page), `bg1 = palette.bg` (the pure-black
  void becomes the recessed inset — exect's bg1 is likewise darker than its
  bg0), `bg2 = palette.bg2`, `bg3 = palette.overlay`.
- `line` — accent border: bg3 brightened toward muted0 to **1.68×** its HSL
  lightness (exect measures 13.5 → 22.7, i.e. `#332412` → `#5a3f1a`); hue and
  saturation follow the same fraction of the bg3 → muted0 path.
- `muted0 = palette.dimText`, `muted1 = palette.subtle`, `text0 = palette.text`.
- `text1` — text0 walked toward muted1 until WCAG luminance is **0.70×**
  text0's (exect: 0.705, `#ffb753` → `#e09a3f`).
- `paDim` — muted0 at **0.48×** saturation, lightness solved so luminance lands
  at **0.94×** muted0's (exect: `#8a6224` → `#796344`): the dim tone sits just
  below the quietest text. These three constants reproduce exect's own rungs
  within one RGB unit per channel.
- colors rewired to the canonical rungs: `text/userMessageText/
  customMessageText→text0`, `mdCodeBlock→text1`, `syntaxVariable→text0`,
  `dim→paDim`, `border→bg2`, `borderMuted/mdCodeBlockBorder/mdQuoteBorder/
  mdHr→bg3`. Identity wiring untouched (`accent→mint`, `borderAccent→mint`,
  `bashMode→lime`, …); all legacy ramp vars still emitted. Still exactly the
  55 contract keys.

**Regenerated card** (`previews/random-access-theme.png`, 1280×1326, zero
magenta pixels): page paints bg0 `#090a0b` instead of the old void; the ladder
chips — previously nine magenta MISSING chips — now read bg0 `#090a0b`, bg1
`#000000`, bg2 `#101214`, bg3 `#1a1c20`, line `#2c3136`, muted0 `#6f8d86`,
muted1 `#9cb7af`, text0 `#d8efe9`, text1 `#aecfc5`. The pa* row ends on a real
paDim chip `#788783` (was magenta). Accent chips: mint `#00ffb2`, success
`#4ade80`, error `#26c994`; panels unchanged (`#1c2120`/`#132016`/`#251918`/
`#070e0c`/`#0e1d19`/`#19312a`/`#2d1b1a`…). Borders dropped from `subtle` grey
to the quiet bg2/bg3 rungs, so the transcript blocks sit on tint with only the
accent border still mint-adjacent.

**Validators**: `scripts/validate_theme.py` — all checks green, exit 0 (55
tokens exact, palette freshness, no installed drift — the installed file is a
symlink into the repo). `validate_themes.py random-access-theme` — `ok`,
exit 0. The other three ramp palettes were deliberately not regenerated; their
installed copies stay archived as-is.
