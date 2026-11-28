"""Twelve-pixel repair icons, lit from the upper left with material outlines."""
from pixelkit import P, Sprite

PREVIEW_SCALE = 8

DRAWINGS = {
    "coil": ("...oooooo...", "..ohhhmmmo..", ".ohhmmmmdoo.", ".ohmmddmmdo.", ".ommd..mmdo.", ".ommd..mmdo.", ".ommd..mmdo.", ".ommd..mmdo.", "..oddooodo..", "...ooo.o....", "..ohho.ohho.", "..oooo.oooo."),
    "guard": ("............", "...oooooo...", "..ohhhhhho..", ".ohmmmmmmdo.", ".ohmhmmmddo.", ".ohmmmmdddo.", ".ommmdddddo.", "..omdddddo..", "...oddddo...", "....oddo....", ".....oo.....", "............"),
    "fault": ("............", ".....oo.....", "..oo.mm.oo..", "...omhhmo...", "..ohhmmddo..", ".ommomomddo.", ".ommmmmdddo.", "..omdddddo..", "..oooooooo..", "...o....o...", "............", "............"),
    "flag": ("............", "...oooooo...", "...ohhhmo...", "...ommmdo...", "...oddoo....", "...oo.......", "...oo.......", "...oo.......", "..oooo......", ".ohmmdo.....", ".oooooo.....", "............"),
    "mine": ("............", ".....do.....", "...o.do.o...", "...oooooo...", "..ohhmmmdo..", ".oommmmmdoo.", ".oommddddoo.", "..omdddddo..", "...oooooo...", "...o.oo.o...", "............", "............"),
    "light": ("............", "....oooo....", "...ohhhmo...", "..ohhmmmdo..", "..ohmmmmdo..", "..omdddddo..", "...oddddo...", "....oooo....", "............", "............", "............", "............"),
    "dark": ("............", "....oooo....", "...ohhhmo...", "..ohhmmmdo..", "..ohmmmmdo..", "..omdddddo..", "...oddddo...", "....oooo....", "............", "............", "............", "............"),
    "spark": ("............", "............", ".....oo.....", ".....ho.....", "....hmdo....", "..ohhhmdoo..", "...oddmdo...", "....odoo....", ".....oo.....", "............", "............", "............"),
    "bolt": ("............", ".....ooo....", "....ohho....", "...ohmo.....", "..ohmo......", "..ommdoooo..", "...oodmdo...", ".....odo....", "....odo.....", "...odo......", "...oo.......", "............"),
    "seal": ("............", "....oooo....", "...ohhhdo...", "..ohmmmddo..", "..ohmhmddo..", "..ommhdddo..", "...oddddo...", "...oddddo...", "..odoododo..", "..oo..oooo..", "............", "............"),
}

def build():
    ramps = [P.teal, P.steel, P.clay, P.clay, P.slate, P.linen, P.walnut, P.mustard, P.mustard, P.oak]
    return {
        f"liwei_repair_icon_{key}": Sprite.from_grid("\n".join(grid), dict(zip("odmh", (ramp[i] for i in (0,1,2,-1)))))
        for (key, grid), ramp in zip(DRAWINGS.items(), ramps, strict=True)
    }
