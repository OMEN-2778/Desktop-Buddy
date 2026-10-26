"""Small icons for the game's own UI: settings gear and the contacts glyph.
The gear is 13x13, metal ramp, lit from the top-left, with eight teeth
and a round hole. Contacts uses a 16x16 two-person silhouette with
slate-blue foreground shading. Both display at an integer 2x scale."""

from pixelkit import P, Sprite
import math

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
    return {"gear": gear, "people": people}[name]()


def people() -> Sprite:
    """Two separate busts at 16x16: a slate-blue foreground and softer rear figure."""
    rows = [
        "................",
        "..........LLL...",
        ".........LMMML..",
        "...OOO...LMMML..",
        "..OHBBO..LMMML..",
        "..OBBBO...MMM...",
        "..OBBBO....M....",
        "...OOO....MMM...",
        "....B....LMMML..",
        "..OOBOO.LMMMMML.",
        ".OHHBBBO.LMMML..",
        "OHBBBBBBO.LMML..",
        "OBBBBBBBO..MM...",
        "OBBBBBBBO.......",
        ".OOOOOOO........",
        "................",
    ]
    out = Sprite.from_grid("\n".join(rows), {
        "O": P.blue[1], "B": P.blue[2], "H": P.blue[3],
        "L": P.metal[2], "M": P.metal[3],
    })
    for x, y in ((5, 5), (5, 6), (6, 11), (7, 11), (6, 12), (7, 12), (6, 13), (7, 13)):
        out.set(x, y, P.blue[1])
    for x, y in ((10, 2), (10, 3), (9, 9)):
        out.set(x, y, P.metal[4])
    out.set(1, 12, P.blue[3])
    return out


def need_stripes() -> Sprite:
    """8px repeating diagonal made of solid stair steps; CSS supplies faint opacity."""
    s = Sprite(8, 8)
    for y in range(8):
        for x in range(8):
            if (x + y) % 8 < 3:
                s.set(x, y, P.linen[3])
    return s


def relief_plate(size=14, radius=6, kind="green") -> Sprite:
    """Palette-only bevel hugging the pixel contour, never rectangular black strips.

    The 14px version has 6px corners for CSS nine-slice scaling at 2x;
    badge versions map 1:1 to desktop/mobile inner discs at the same 2x.
    """
    shadow, face, light = (
        (P.coral[2], P.coral[3], P.coral[4]) if kind == "red"
        else (P.mustard[2],P.mustard[3],P.mustard[4]) if kind == "gold"
        else (P.blue[2],P.blue[3],P.blue[4]) if kind == "blue"
        else (P.green[3], P.green[4], P.sage[4])
    )
    mask = [[False] * size for _ in range(size)]
    for y in range(size):
        row = min(y, size - 1 - y)
        inset = 0 if row >= radius else math.floor(radius - math.sqrt(radius**2 - (radius - row - .5)**2) + .5)
        for x in range(inset, size - inset):
            mask[y][x] = True
    inside = lambda x, y: 0 <= x < size and 0 <= y < size and mask[y][x]
    out = Sprite(size, size)
    for y in range(size):
        for x in range(size):
            if not mask[y][x]:
                continue
            lit = not inside(x - 1, y) or not inside(x, y - 1)
            shaded = not inside(x + 1, y) or not inside(x, y + 1)
            color = light if lit and x + y < size else shadow if shaded else face
            out.set(x, y, color)
    return out


def build():
    out = Sprite(13 + sum(len(GLYPHS[g][0]) + 3 for g in GLYPHS), 13)
    out.blit(icon("gear"), 0, 0)
    x = 16
    for g in GLYPHS:
        out.blit(glyph(g), x, 2)
        x += len(GLYPHS[g][0]) + 3
    return {"ui_icons": out, "ui_people": people(), "ui_need_stripes": need_stripes(),
            "ui_relief_badge": relief_plate(22, 11),
            "ui_relief_badge_small": relief_plate(19, 9),
            "ui_relief_answer": relief_plate(),
            "ui_relief_decline": relief_plate(kind="red")}


def pixel_surface(kind='panel', dark=False):
    """Nine-slice UI surface: square 2px steps and an unbroken 2px outline.

    Light comes from top-left. No CSS radius or antialiased corner is needed.
    Panel slice=12, pill=19, other controls=8; thumb is used at native size.
    """
    w,h,r = (32,32,10) if kind=='panel' else (40,40,18) if kind in ('pill','gold-pill') else (14,24,4) if kind=='thumb' else (24,24,6)
    face,hi,lo=(P.hair_black[1],P.hair_black[2],P.hair_black[0]) if dark else (P.linen[3],P.linen[3],P.linen[1])
    if kind in ('control','thumb'):face,hi,lo=(P.hair_black[2],P.hair_black[3],P.hair_black[1]) if dark else (P.linen[2],P.linen[3],P.linen[1])
    if kind=='positive':face,hi,lo=P.sage[3],P.sage[4],P.sage[1]
    if kind in ('gold','gold-pill'):face,hi,lo=P.birch[3],P.birch[4],P.birch[1]
    if kind=='track':face,hi,lo=(P.hair_black[1],P.hair_black[2],P.hair_black[0]) if dark else (P.linen[2],P.linen[3],P.linen[1])
    mask=set()
    for y in range(h):
        row=min(y,h-1-y)
        inset=0 if row>=r else int(math.ceil((r-math.sqrt(max(0,r*r-(r-row-.5)**2)))/2)*2)
        for x in range(inset,w-inset):mask.add((x,y))
    s=Sprite(w,h)
    for x,y in mask:
        edge=any((x+dx,y+dy) not in mask for dx,dy in ((2,0),(-2,0),(0,2),(0,-2)))
        color=P.ink[0] if edge else hi if (x-3,y) not in mask or (x,y-3) not in mask else lo if (x+3,y) not in mask or (x,y+3) not in mask else face
        s.set(x,y,color)
    return s
