"""Small icons for the game's own UI (not the house): the settings gear.
13x13, metal ramp, lit from the top-left (upper-left half one shade
lighter), eight teeth and a round hole in the middle. Shown at 2
screen pixels per icon pixel inside a round pixel button."""

from pixelkit import P, Sprite

PREVIEW_SCALE = 10
SIZE = 13


GEAR = """
.....###.....
.##..###..##.
.###########.
..#########..
..###...###..
####.....####
####.....####
####.....####
..###...###..
..#########..
.###########.
.##..###..##.
.....###.....
"""


def gear() -> Sprite:
    M = P.metal
    s = Sprite.from_grid(GEAR.strip("\n"), {"#": M[2]})
    for y in range(SIZE):                       # light from the top-left: upper-left half a shade lighter
        for x in range(SIZE):
            if s.px[y, x, 3] and x + y < 12:
                s.set(x, y, M[3])
    for x, y in ((5, 4), (4, 5), (4, 6)):       # the hole's inner rim catches shadow on its lit side
        s.set(x, y, M[1]) if s.px[y, x, 3] else None
    return s


def icon(name: str) -> Sprite:
    return {"gear": gear}[name]()


def build():
    return {"ui_icons": icon("gear")}
