# Factory Luxury Terminal Setup

This guide documents the settings required to achieve the "Luxury App" terminal aesthetic (no visible chrome, pure OLED blacks, precise margins, and true ANSI inheritance).

## 1. iTerm2 Structural Polish
To break the illusion of a raw terminal and make it feel like a designed page:
* **Margins:** Set `TerminalMargin` to `15` and `TerminalVMargin` to `12` in `com.googlecode.iterm2.plist`. This adds breathing room around the text.
* **Scrollbars:** Hide scrollbars entirely (`Preferences > Advanced > Hide scrollbars`).
* **Cursor:** Set to a vertical bar (`|`), non-blinking.
* **Line Height:** Set vertical spacing to `1.08`.
* **Font:** `BerkeleyMonoVariable-Regular` (No ligatures) with a Nerd Font fallback for non-ASCII.

## 2. FZF "Spotlight" Layout
Instead of drawing from the bottom up, `fzf` is configured to look like a floating command palette:
```bash
# Added to FZF_DEFAULT_OPTS in .zshrc
--layout=reverse --border=rounded --margin=1,2
```

## 3. Toolchain ANSI Inheritance
Instead of relying on hardcoded third-party themes (like "GitHub Dark"), `bat` and `delta` are forced to inherit the exact Factory Mint/Teal/Indigo palette from the terminal emulator.
* **bat:** `--theme=ansi` in `~/.config/bat/config`
* **delta:** `syntax-theme = ansi` in `~/.gitconfig`

## 4. Quiet Chrome
* **Starship:** Icons stripped. Single minimal prompt line showing only path basename, git delta, and `›`.
* **tmux:** Background colors stripped. Status line moved to bottom, showing only session name, path basename, and time in `dimText`.
