# Random Access Themes — richer preview sample
# Useful when generating screenshots with freeze or testing syntax color balance.

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

FlavorName = Literal["random-access-theme", "veridis", "voyager", "amnesiac"]


@dataclass(frozen=True)
class PreviewTheme:
    name: FlavorName
    accent: str
    background: str
    contrast_ratio: float
    terminals: tuple[str, ...]
    editors: tuple[str, ...]

    def summary(self) -> dict[str, object]:
        return {
            "flavor": self.name,
            "accent": self.accent,
            "contrast": round(self.contrast_ratio, 2),
            "ports": len(self.terminals),
            "editors": list(self.editors),
        }


THEMES: list[PreviewTheme] = [
    PreviewTheme(
        name="random-access-theme",
        accent="#00ffb2",
        background="#000000",
        contrast_ratio=17.44,
        terminals=("ghostty", "wezterm", "kitty", "alacritty"),
        editors=("vscode", "zed"),
    ),
    PreviewTheme(
        name="amnesiac",
        accent="#7b93ff",
        background="#0f0e0d",
        contrast_ratio=15.10,
        terminals=("ghostty", "wezterm", "windows-terminal"),
        editors=("neovim",),
    ),
]


def render_status(theme: PreviewTheme) -> str:
    status = "ready" if theme.contrast_ratio >= 7 else "tune"
    target = Path("themes") / "ghostty" / f"{theme.name}.conf"
    return (
        f"{theme.name:<20} accent={theme.accent} "
        f"contrast={theme.contrast_ratio:>5.2f} status={status:<5} "
        f"target={target}"
    )


if __name__ == "__main__":
    print("# visual smoke test")
    for theme in THEMES:
        print(render_status(theme))
        print(theme.summary())
