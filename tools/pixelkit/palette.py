"""Project palette: hue-shifted ramps, dark -> light.

Shadows lean cool/purple, highlights lean warm/yellow. Index 0 is the
darkest shade of a ramp; outlines use the ramp's darkest color (or INK),
never pure black.

Add a ramp here before using a new color in an asset; `pixelkit lint`
reports any pixel whose color is not in this file.
"""

from types import SimpleNamespace

RAMPS: dict[str, list[str]] = {
    # outlines / deepest shadow
    "ink": ["#22182a", "#33253b"],
    # people
    "skin": ["#6e3b3f", "#b8664f", "#e39a72", "#f6c39c", "#ffe3c6"],
    "skin_tan": ["#5a2f2e", "#94523d", "#c47a54", "#dea074", "#f0c497"],
    "skin_deep": ["#2e1a1f", "#5a3129", "#80493a", "#a2654b", "#c48a64"],
    "hair_brown": ["#2e1c24", "#51302e", "#7c4734", "#a66a42", "#c98d58"],
    "hair_black": ["#1a1625", "#2b2538", "#433a54", "#5f5472", "#7d7392"],
    "hair_pink": ["#4a1f36", "#8a3a5b", "#c75f81", "#ec8fa6", "#ffc4d0"],
    "blush": ["#e8857a"],
    # cloth
    "blue": ["#1f2242", "#2f3c6d", "#46619e", "#6c90c8", "#a6c5e7"],
    "coral": ["#4a1f2c", "#7e2f3b", "#b94b4b", "#e1725b", "#f6a487"],
    "mustard": ["#5c3b1f", "#9b6a27", "#d29b30", "#efc452", "#fae59c"],
    "green": ["#1c3329", "#2c5237", "#447840", "#6ba14c", "#a7cd6b"],
    "linen": ["#8f8ba2", "#bab7c9", "#dedce7", "#f7f6fb"],
    # materials
    "wood": ["#3a2227", "#5d3831", "#87573e", "#b18051", "#d7ac6f"],
    "birch": ["#6c4b3b", "#9d7453", "#caa273", "#e7c996", "#f7e5ba"],
    "metal": ["#262434", "#3f3c50", "#5e5b71", "#8b8899", "#bebdcc", "#eae9f1"],
    "glass": ["#1d3a4b", "#2f6171", "#4f9ba4", "#90d4d0", "#d5f6ed"],
    "terracotta": ["#3b1d25", "#6c3034", "#9d4539", "#c6644b", "#e18a6b"],
    # architecture
    "cut": ["#2a2431", "#3f3645", "#5b4f5d", "#77697b", "#93849a"],
    "wall_cream": ["#a99789", "#cebdac", "#e5d7c4", "#f2e8d7"],
    "wall_sage": ["#6f7e6b", "#90a18b", "#aec0a6", "#ccdbc1"],
    "wall_blush": ["#9e7b7d", "#c59c9b", "#e1beb8", "#f3d9d1"],
    # sky / light
    "sky_day": ["#5c8dd0", "#80b1e7", "#b4d7f3", "#e3f1fb"],
    "sky_night": ["#141833", "#1f2550", "#333a75", "#5a5f9c"],
    "light": ["#fff1b8", "#fffbe6"],
}

P = SimpleNamespace(**RAMPS)

ALL_COLORS: set[str] = {c.lower() for ramp in RAMPS.values() for c in ramp}


def ramp(name: str) -> list[str]:
    return RAMPS[name]
