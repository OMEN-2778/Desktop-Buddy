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
    "wall_sky": ["#6f8299", "#93a8bf", "#b9cede", "#dae8f1"],
    "wall_butter": ["#a8946a", "#cdb98a", "#e8d7a8", "#f5ebcb"],
    # interior (calm scheme: warm neutrals + two muted accents, sage and clay)
    "plaster_bed": ["#cdbfb4", "#dccfc5", "#ece2d9", "#f6efe8"],
    "plaster_bath": ["#bec7c4", "#cfd7d4", "#e2e8e4", "#f0f4f1"],
    "plaster_study": ["#c3c6b3", "#d3d6c3", "#e3e6d5", "#f0f2e6"],
    "plaster_living": ["#d0c3ad", "#dfd3bd", "#eee4d1", "#f8f1e3"],
    "plaster_kitchen": ["#cac3b5", "#dad3c5", "#eae4d8", "#f6f2ea"],
    "plaster_stair": ["#c8bdaf", "#d8cec0", "#e8dfd2", "#f4ede4"],
    "oak": ["#5b4232", "#8a6446", "#b48a62", "#d1ab80", "#e6c9a0"],
    "ash": ["#6a5444", "#9c8064", "#c4a885", "#dcc4a2", "#efe0c4"],
    "walnut": ["#2f2120", "#4a3329", "#6b4a37", "#8c6648", "#a9825e"],
    "oat": ["#7d7266", "#a89a8a", "#cbbfae", "#e2d8c9", "#f3ede3"],
    "sage": ["#3e4a3d", "#5f6f58", "#83957a", "#a8b89c", "#cbd6bf"],
    "clay": ["#5a3229", "#86493a", "#b0674f", "#cc8a6e", "#e3b096"],
    "steel": ["#2e2b30", "#4a464d", "#6e6a70", "#9a9699", "#c9c5c5", "#ecebe8"],
    "porcelain": ["#9f9b98", "#c4c1bc", "#e0ddd8", "#f4f2ee"],
    "tile": ["#aaa59d", "#c8c3ba", "#dcd8cf", "#ebe8e1"],
    "leaf": ["#24352b", "#36513b", "#4f6d4c", "#6f8c5f", "#9db285"],
    "frame": ["#2a2427", "#3d3538", "#52484a", "#6a5f60", "#837677"],
    "sky_soft": ["#86a3c4", "#a3bdd8", "#c4d6e8", "#e5edf4"],
    # outside (家门口): the townhouse row (ours white, left light blue, right brick)
    "facade_white": ["#8e8a93", "#b7b3b5", "#d8d5d2", "#eeebe6", "#faf8f4"],
    "facade_blue": ["#5f7591", "#86a0bd", "#b3cbe0", "#d4e5f2", "#ecf5fb"],
    "brick": ["#4e2c2b", "#7a4136", "#a65a45", "#c4785c", "#dca084"],
    "slate": ["#262a36", "#363c4c", "#4b5366", "#656e82", "#8a92a3"],
    "teal": ["#163a3f", "#22575b", "#337a78", "#4f9f97", "#7fc4b6"],
    "mint": ["#2f5a48", "#4f8a6c", "#7fb79a", "#a9d6bd", "#d2eedd"],
    "pave": ["#5f5c63", "#807c82", "#a3a0a3", "#c2bfbe", "#dcdad6"],
    "grass": ["#22402a", "#335c33", "#4c7d3e", "#6ea24c", "#9cc865"],
    "leaf_spring": ["#2a4a2c", "#3f6d36", "#5f9443", "#86bb57", "#b6dc7c"],
    "autumn": ["#4a1d1c", "#8a2f1f", "#c65022", "#e88a2f", "#f6c45a"],
    "blossom": ["#7a3a55", "#b8668a", "#e095b2", "#f5c3d4", "#fde6ee"],
    "hydrangea": ["#35407a", "#4f63ad", "#7b95d6", "#a9c0ee", "#d6e3fa"],
    "snow": ["#8d9ab3", "#b8c4d8", "#dfe7f2", "#f6f9fd"],
    # sky / light
    "moon": ["#0b1a5c", "#123194", "#1f4bc4", "#5b82e0", "#a9c2f5"],
    "sky_day": ["#5c8dd0", "#80b1e7", "#b4d7f3", "#e3f1fb"],
    "sky_night": ["#141833", "#1f2550", "#333a75", "#5a5f9c"],
    "light": ["#fff1b8", "#fffbe6"],
}

P = SimpleNamespace(**RAMPS)

ALL_COLORS: set[str] = {c.lower() for ramp in RAMPS.values() for c in ramp}


def ramp(name: str) -> list[str]:
    return RAMPS[name]


# ---------------------------------------------------------------- user colors
# Players pick ONE color per part; a full 5-shade ramp is generated from it so
# the pick matches the hand-tuned ramps above (cool shadows, warm highlights).
# The creator page (prototype/creator) mirrors this in JS — keep them in sync.

import colorsys

# per ramp index: (value change, saturation factor, hue shift in degrees)
#   value < 0 darkens (v * (1 + d)); value > 0 lightens toward white
#   hue shift moves toward SHADOW_HUE for darker shades, LIGHT_HUE for lighter
CLOTH_STEPS = [(-0.58, 1.2, 22), (-0.3, 1.1, 10), (0, 1, 0), (0.42, 0.95, 8), (0.72, 0.72, 16)]
SKIN_STEPS = [(-0.55, 1.25, 26), (-0.25, 1.5, 12), (-0.07, 1.3, 5), (0, 1, 0), (0.5, 0.6, 6)]
SHADOW_HUE, LIGHT_HUE, SKIN_SHADOW_HUE = 250.0, 55.0, 350.0


def _toward(h: float, target: float, amount: float) -> float:
    d = (target - h + 180) % 360 - 180
    return (h + max(-amount, min(amount, d))) % 360


def ramp_from(base: str, skin: bool = False) -> list[str]:
    """5-shade ramp around `base` (the color the player picked).

    Cloth/hair: base is index 2. Skin: base is index 3 (the face color)."""
    steps = SKIN_STEPS if skin else CLOTH_STEPS
    shadow_hue = SKIN_SHADOW_HUE if skin else SHADOW_HUE
    r, g, b = (int(base.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h *= 360
    out = []
    for dv, fs, dh in steps:
        if dv < 0:
            hh = _toward(h, shadow_hue, dh)
            ss = min(1.0, s * fs + 0.06)
            vv = v * (1 + dv)
        elif dv > 0:
            hh = _toward(h, LIGHT_HUE, dh)
            ss = s * fs
            vv = min(1.0, v + (1 - v) * dv * (0.4 + 0.6 * v))
        else:
            hh, ss, vv = h, s, v
        rr, gg, bb = colorsys.hsv_to_rgb(hh / 360, ss, vv)
        out.append("#%02x%02x%02x" % (round(rr * 255), round(gg * 255), round(bb * 255)))
    return out


# Swatches shown in the character creator: (label, base color).
# Base = hair/cloth ramp[2], skin ramp[3].
SWATCHES = {
    "hair": [
        ("乌黑", RAMPS["hair_black"][2]), ("深棕", RAMPS["hair_brown"][2]), ("栗色", "#9a5a34"),
        ("奶茶", "#b08f78"), ("金色", RAMPS["mustard"][2]), ("橘红", "#c4562e"),
        ("酒红", "#8a2f45"), ("粉色", RAMPS["hair_pink"][2]), ("薰衣草", "#9a86c8"),
        ("雾蓝", "#5a78b8"), ("薄荷", "#6fb59a"), ("银白", "#c9c6d6"),
    ],
    "skin": [
        ("白皙", "#fbd9c0"), ("自然", RAMPS["skin"][3]), ("暖米", "#ecb98e"),
        ("小麦", RAMPS["skin_tan"][3]), ("棕色", "#b97a55"), ("深色", RAMPS["skin_deep"][3]),
    ],
    "cloth": [
        ("白", "#e8e6ef"), ("浅灰", "#a9a7b5"), ("炭黑", "#4a4658"), ("红", RAMPS["coral"][2]),
        ("珊瑚", "#e07a62"), ("橙", "#e08a3a"), ("芥末黄", RAMPS["mustard"][2]), ("橄榄", "#8a8a3e"),
        ("草绿", RAMPS["green"][2]), ("薄荷", "#5fae96"), ("湖蓝", "#3f8fa6"), ("天蓝", RAMPS["blue"][3]),
        ("藏青", RAMPS["blue"][2]), ("紫", "#7a5aa6"), ("粉", "#e39ab0"), ("咖啡", RAMPS["wood"][2]),
    ],
}
