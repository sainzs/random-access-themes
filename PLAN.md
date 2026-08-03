# Plan — theme documentation

`docs/phosphor-themes.md` documents four tubes. There are six, and the other two
are not strays: `dusk` and `factory` belong to the `/tone` family in the reckoner
package, which has its own command. Documenting them as leftovers would be worse
than leaving them out.

Written for another agent to execute. Each task states how to verify it. Two
items need the user's decision — do not settle them by picking whichever reading
makes the task easier.

**Read this first: the plan has been overtaken in part.** It was written while
the themes were a subdirectory of the `reckoner` package. They were extracted to
a standalone project, and then fused into this one. What that fusion already did,
so nobody does it twice:

- The six phosphor themes live in `themes/pi/reckoner-*.json`, documented in
  `docs/phosphor-themes.md`, screenshots in `assets/phosphor/`.
- `reckoner-dusk` was promoted out of `archive/`; the defective copy is deleted.
- The thinking ramp is derived in `scripts/generate.py` and enforced across all
  ten pi themes by `validate_thinking_ramps()` in `scripts/validate_theme.py`.
- `themes/.checksum` covers every palette, not just the last one generated.
- The `random-access.json` fork is gone: the generator now emits exactly what the
  fork had been hand-corrected to.

**Still open, and renumbered below:** tasks 0, 2, 3 and 4. Task 1 (global
symlinks) and task 5 (a screenshot for random-access) are done. Two tasks reach
back into the reckoner package and say so where they do —
`extensions/factory-theme.ts` and `prototypes/lib/stage.ts` live there.

## What is actually there

**Two families, not one list.**

*The tubes* — four phosphor themes, each a real terminal. Documented, screenshot,
in `prototypes/lib/stage.ts`, symlinked globally.

`reckoner-exect` · `reckoner-scope` · `reckoner-wopr` · `reckoner-darkspace`

*The tones* — three themes switched by `/tone`, registered in
`extensions/factory-theme.ts` with `random-access` as the default. Undocumented
in `README.md`; mentioned once, in passing, at `README.md:158`.

`random-access` (default) · `reckoner-dusk` · `reckoner-factory`

This distinction is the plan. `dusk` is violet on blue-black (`#a489d8` on
`#1c1b29`) and `factory` is safety-orange on true black (`#ef6f2e` on `#020202`);
neither is a phosphor and neither should be given an invented CRT model number to
fit a section it does not belong in. `random-access` is mint `#00ffb2` — the
colour of the repo's own licence badge, which is what makes it the house theme
rather than a fourth tone.

| file | registers as | documented | screenshot | in `stage.ts` | symlinked |
|---|---|---|---|---|---|
| `reckoner-exect.json` | `reckoner-exect` | yes | yes | yes | yes |
| `reckoner-scope.json` | `reckoner-scope` | yes | yes | yes | yes |
| `reckoner-wopr.json` | `reckoner-wopr` | yes | yes | yes | yes |
| `reckoner-darkspace.json` | `reckoner-darkspace` | yes | yes | yes | yes |
| `reckoner-dusk.json` | `reckoner-dusk` | no | yes | no | **no** |
| `reckoner-factory.json` | `reckoner-factory` | no | yes | no | **no** |
| `random-access.json` | **`random-access-theme`** | no | **no** | no | **no** |

Facts that will save time:

- **A theme registers under its JSON `name` field, not its filename.**
  `registeredThemes.set(theme.name, theme)` —
  `node_modules/@mariozechner/pi-coding-agent/dist/modes/interactive/theme/theme.js:552`.
  This is the root of the defect in task 0.
- **`scripts/render-screenshots.py` globs `reckoner-*.json`**, which is the only
  reason `random-access` has no screenshot.
- **The doc's role names are not the JSON's keys.** `peak` is `mdHeading`;
  `hot` is `accent`. The mapping is `ROLE_KEY` in `prototypes/lib/stage.ts`.
  Resolving `peak` as a colour key yields four confident false positives — that
  mistake has already been made once while writing this plan.
- **Both existing tables are currently exact**: all 36 token values and all 24
  thinking values match the JSON. A drift check added now starts green.
- Values resolve through `vars` by name, sometimes two hops. `bg` in the token
  table is `colors.background` where present, else `vars.bg0`.

## Task 0 — `/tone random` cannot work, and it is the default

Verify this first; the rest of the plan documents a system that is broken at its
default setting.

`extensions/factory-theme.ts:4` sets `DEFAULT_THEME = "random-access"` and
applies it on every `session_start`. But `themes/random-access.json` has
`"name": "random-access-theme"`, so it registers under that name. The lookup
chain for `"random-access"`:

1. built-in themes — no
2. `registeredThemes` — no, it is under `random-access-theme`
3. `~/.pi/agent/themes/random-access.json` — no such file (there is a stale
   hand-copied `random-access-theme.json` there, which does not match either)

`setTheme` therefore throws, catches, and **falls back to pi's built-in `dark`**,
returning `{ success: false }`, at which point the extension raises a warning
notification. `/tone dusk` and `/tone factory` work, because for them the `name`
field and the string in the extension agree.

Live in any session started from this package, since `package.json` loads
`./extensions` wholesale. Not live in the user's global sessions — their
`settings.json` loads only `harness-footer.ts`.

Two ways to fix, and **this is the user's call**: rename the file to
`reckoner-random-access.json` and set `name` to match, which brings it into the
family and under the screenshot glob; or leave the file name and change `name` to
`random-access`, which is one line and preserves the existing global copy. The
first is tidier and touches the `/tone` aliases, the symlink instructions and the
screenshot set. The second is minimal. Do not choose silently.

Verify: from inside the package, `/tone random` applies the mint theme and raises
no warning. A unit test asserting every string in `factory-theme.ts`'s `THEMES`
resolves to a real registered theme name would stop this recurring — that is the
check that was missing, not the fix.

## Task 1 — the tones are not symlinked globally *(done)*

`README.md`'s install loop covers `exect scope wopr darkspace`, so
`~/.pi/agent/themes/` has four of the six `reckoner-*` themes. `dusk` and
`factory` are absent, and package themes only register in sessions launched from
the package — so `/tone dusk` fails outside this repo for the same reason task 0
fails inside it.

Make the loop glob `themes/reckoner-*.json` rather than list names, so the next
theme does not need this task doing again.

Verify: `ls -l ~/.pi/agent/themes/` shows a symlink per `reckoner-*.json`; the
stale `random-access-theme.json` copy is a separate question that task 0 settles.

## Task 2 — document both families

`README.md`. Add a `## The tones` section beside the existing four, with
the `/tone` command, its aliases (`random`/`rat`, `dusk`, `factory`), and the fact
that the selection is remembered per session branch — it is restored on
`session_start`, `session_switch`, `session_tree` and `session_fork`, which is
worth one sentence because no other theme in the repo behaves that way.

Each tone gets what the tubes get: one italic identity line, one or two sentences,
a screenshot. Frame them as what they are — a tone family for the reckoner
surface — not as tubes.

Retitle what is now false. `README.md` line 3 ("Four phosphor themes"),
line 28 (`## The four`); `README.md` line 66 (`## Themes — four phosphors`), 68,
70, 216. **Leave alone**: `README.md:12` "four brightnesses" and
`README.md:206` "four small packages" — both still true and unrelated.

Verify: every `themes/*.json` has a subsection and every subsection has a file.

## Task 3 — extend the tables to all seven

`## Tokens` and `## Thinking levels`, both hand-maintained, both currently exact.

Seven columns is too wide for GitHub's Markdown rendering. Transposing to themes
as rows is likely better and is a free choice; the thinking table already reads
that way. Keep both oriented the same as each other.

Verify: task 4's checker, written first or alongside.

## Task 4 — put table drift in the gate

The task that stops the other three rotting. Extend
`scripts/validate-themes.mjs`; it already loads and resolves every theme, so it
needs no new dependency and is already in `verify:self`.

Parse each documented value out of `README.md`, compare against the
resolved JSON colour, and report every mismatch rather than the first. Fail when a
theme has no table entry — that is what makes it also catch "a theme was added and
never documented".

Verify **in both directions**: it must pass as written today, and it must fail if
you change one hex digit in the README or add a theme file. A drift checker that
cannot fail is worse than none, because it licenses the belief that the tables are
right.

## Task 5 — `stage.ts` and the screenshot glob

- `THEME_NAMES` in `prototypes/lib/stage.ts` hardcodes the four tubes, so the
  prototype contact sheets cannot show `dusk` or `factory` at all. Add them and
  check the sheets still render at a sensible width with six or seven palettes —
  `npx tsx prototypes/proto-5-reactive.ts`. If the layout will not take it, say
  so rather than quietly narrowing it.
- Give `random-access` a screenshot. The glob is the only obstacle, and task 0's
  outcome may remove it. `python3 scripts/render-screenshots.py` regenerates all.

Verify: `npm run typecheck:prototypes`, then run the prototype and look at it.

## Out of scope

- **Generalising the theme gate to a contrast check** over every role/background
  pair. This repo already has `scripts/contrast_matrix.py` and `make contrast`,
  which is most of the way there — it reports against the palette background
  rather than every role pair. Extending it is the natural next step and is why
  fusing was worth doing.
- **Changing any colour.** The ramps were rebuilt in HSL for a reason and
  `verify:themes` encodes it. If a value looks wrong, report it.
- **The footer.** `## The harness footer` is current as of reckoner's `d1deb7e`.
  The section documents another project's component and is kept here because the
  themes are what make it legible; `scripts/footer-frames.json` is the seam.
- **`render:screenshots --check`.** A real gap — committed PNGs can go stale
  silently, and the hand-drawn mock has drifted three times — but not this plan.

## Definition of done

`npm run verify:self` passes, with the drift check part of it and shown to fail
when the README is wrong. `/tone random` works from inside the package. Every file
in `themes/` appears in the README with a screenshot, or has a stated reason not
to. The word "four" survives only where it is still true.

Read `HANDOFF.md` first — particularly "Measurements that did not measure what
they claimed", which is where task 4 goes wrong if it goes wrong.
