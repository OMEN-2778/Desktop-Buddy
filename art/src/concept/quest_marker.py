"""Small quest badges drawn on the world pixel grid, lit from the top left."""

from pixelkit import P, Sprite

PREVIEW_SCALE = 14

PLATE = (
    "..ooooo..",
    ".oHHHHHo.",
    "oHyyyyyso",
    "oHyyyyyso",
    "oHyyyyyso",
    "oHyyyyyso",
    "oHyyyyyso",
    "oHyyyyyso",
    "oHyyyyyso",
    ".ossssso.",
    "..ooooo..",
)

# The exclamation has a rounded shoulder and a tapered stem above its dot.
SIGNS = {
    "!": (".xx.", "xxxx", ".xxx", ".xx.", "..x.", "....", ".xx."),
    "?": (".xxx", "xx.x", "...x", "..x.", ".x..", "....", ".x.."),
}


def build():
    sprites = {}
    for sign, channels in (("!", P.mustard), ("?", P.blue)):
        marker = Sprite.from_grid("\n".join(PLATE), {
            "o": P.ink[0],
            "H": P.wall_cream[-1] if sign == "!" else P.wall_sky[-1],
            "y": channels[-1],
            "s": channels[-2],
        })
        marker.blit(Sprite.from_grid("\n".join(SIGNS[sign]), {"x": P.ink[0]}), 2, 2)
        sprites["quest_marker_offer" if sign == "!" else "quest_marker_followup"] = marker
    return sprites
