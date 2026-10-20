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


# One-colour glyphs for pill buttons: the page draws them in the button's text
# colour (white on the chosen one), 2 screen pixels per glyph pixel.
GLYPHS = {
    "pause": [            # two bars
        "##..##",
    ] * 9,
    "play": [             # one triangle pointing right
        "#....",
        "##...",
        "###..",
        "####.",
        "#####",
        "####.",
        "###..",
        "##...",
        "#....",
    ],
    "ff": [               # two triangles
        "#....#....",
        "##...##...",
        "###..###..",
        "####.####.",
        "##########",
        "####.####.",
        "###..###..",
        "##...##...",
        "#....#....",
    ],
    "fff": [              # three triangles
        "#....#....#....",
        "##...##...##...",
        "###..###..###..",
        "####.####.####.",
        "###############",
        "####.####.####.",
        "###..###..###..",
        "##...##...##...",
        "#....#....#....",
    ],
}


def glyph(name: str, color=P.ink[1]) -> Sprite:
    return Sprite.from_grid("\n".join(GLYPHS[name]), {"#": color})


def icon(name: str) -> Sprite:
    return {"gear": gear}[name]()


def build():
    out = Sprite(13 + sum(len(GLYPHS[g][0]) + 3 for g in GLYPHS), 13)
    out.blit(icon("gear"), 0, 0)
    x = 16
    for g in GLYPHS:
        out.blit(glyph(g), x, 2)
        x += len(GLYPHS[g][0]) + 3
    return {"ui_icons": out}
