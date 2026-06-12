# Random Access Theme — palette preview
# OLED-black background, mint-forward, green-family syntax

from dataclasses import dataclass
from typing import Optional

@dataclass
class Theme:
    """A terminal color scheme with zero warm hues."""
    name: str
    accent: str = "#00ffb2"  # electric mint
    background: str = "#000000"  # pure OLED black
    version: Optional[int] = None

    def contrast_ratio(self, fg: str, bg: str) -> float:
        """WCAG 2.1 contrast ratio between two hex colors."""
        lum_fg = self._luminance(fg)
        lum_bg = self._luminance(bg)
        hi, lo = max(lum_fg, lum_bg), min(lum_fg, lum_bg)
        return (hi + 0.05) / (lo + 0.05)

    def _luminance(self, hex_color: str) -> float:
        r, g, b = (int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def passes_aa(self, fg: str) -> bool:
        return self.contrast_ratio(fg, self.background) >= 4.5


flavors = ["random-access", "veridis", "voyager", "amnesiac"]
theme = Theme(name="random-access", version=1)

for flavor in flavors:
    ratio = theme.contrast_ratio(theme.accent, theme.background)
    print(f"{flavor}: {ratio:.1f}:1 contrast")
