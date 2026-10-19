"""Need icons for the status bars: drumstick, Zzz, soap + bubbles, smiley.
12x12, outlined, drawn in the game palette."""

from pixelkit import P, Sprite

PREVIEW_SCALE = 10

GRIDS = {
    "hunger": ("""
.....oooo...
...ooLLLLo..
..oLLSSSSSo.
..oLSSSSSSo.
..oSSSSSSDo.
..oSSSSSDDo.
...oSSDDDo..
...oWooooo..
..oWWo......
.oWWo.......
oWWWo.......
.ooo........
""", {"o": P.walnut[1], "L": P.clay[4], "S": P.clay[3], "D": P.clay[2], "W": P.linen[3]}),
    "energy": ("""
SSSSSS......
SSSSSS......
...SS.......
..SS........
.SS.........
SSSSSS......
SSSSSS.SSSS.
.........S..
........S...
.......SSSS.
............
............
""", {"S": P.blue[2]}),
    "hygiene": ("""
.......ooo..
......oWLWo.
......oWWWo.
..oo...ooo..
.oWLo.......
.oWWo.......
..oo........
.oooooooooo.
oLLSSSSSSSSo
oLSSSSSSSSDo
oDDDDDDDDDDo
.oooooooooo.
""", {"o": P.blue[1], "W": P.linen[3], "L": P.sky_soft[3], "S": P.sky_soft[1], "D": P.sky_soft[0]}),
    "fun": ("""
...oooooo...
.ooHHYYYYoo.
.oHYYYYYYYo.
oYYoYYYYoYYo
oYYoYYYYoYYo
oYYYYYYYYYYo
oYoYYYYYYoYo
oYYoYYYYoYYo
.oYYooooYYo.
.ooYYYYYYoo.
...oooooo...
............
""", {"o": P.mustard[0], "Y": P.mustard[3], "H": P.mustard[4]}),
}


def icon(name: str) -> Sprite:
    grid, legend = GRIDS[name]
    return Sprite.from_grid(grid, legend)


def build():
    out = Sprite(12 * 4 + 6 * 3, 12)
    for i, n in enumerate(GRIDS):
        out.blit(icon(n), i * 18, 0)
    return {"need_icons": out}
