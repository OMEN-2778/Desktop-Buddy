"""Need icons for the status bars, chibi style: chubby drumstick, bubbly Zz,
soap with bubbles, blushing smiley. 10x10, outlined, game palette.
Shown at one icon pixel per house pixel."""

from pixelkit import P, Sprite

PREVIEW_SCALE = 10
SIZE = 10

GRIDS = {
    "hunger": ("""
.oooo.....
oHLSSo....
oLSSSSo...
oSSSSSSo..
oSSSSSDo..
.oSSSDDo..
..ooDDoWo.
....ooWWWo
.....oWWo.
......oo..
""", {"o": P.walnut[1], "H": P.clay[4], "L": P.clay[4], "S": P.clay[3], "D": P.clay[2], "W": P.linen[3]}),
    "energy": ("""
LLLLLL....
SSSSSS....
...SSS....
..SSS.....
.SSS......
SSSSSS....
......LLLL
.......SSS
......SSS.
......SSSS
""", {"S": P.blue[2], "L": P.blue[3]}),
    "hygiene": ("""
......oo..
.....oWHo.
.....oWWo.
..oo..oo..
.oHWo.....
..oo......
.oooooooo.
oHLSSSSSSo
oSSSSSSSDo
.oooooooo.
""", {"o": P.blue[1], "W": P.linen[3], "H": P.linen[3], "L": P.sky_soft[3], "S": P.sky_soft[1], "D": P.sky_soft[0]}),
    "fun": ("""
..oooooo..
.oYYYYYYo.
oYHHYYYYYo
oYYoYYoYYo
oYYoYYoYYo
oBBYYYYBBo
oYYoYYoYYo
.oYYooYYo.
..oooooo..
..........
""", {"o": P.mustard[0], "Y": P.mustard[3], "H": P.mustard[4], "B": P.coral[3]}),
}


def icon(name: str) -> Sprite:
    grid, legend = GRIDS[name]
    rows = [r for r in grid.strip("\n").split("\n")]
    s = Sprite.from_grid("\n".join(r[:SIZE] for r in rows), legend)   # keep every icon SIZE wide
    out = Sprite(SIZE, SIZE)
    out.blit(s, 0, 0)
    return out


def build():
    out = Sprite(SIZE * 4 + 4 * 3, SIZE)
    for i, n in enumerate(GRIDS):
        out.blit(icon(n), i * (SIZE + 4), 0)
    return {"need_icons": out}
