"""茵菲谷 seasonal crops (owner 2026-11-02: richer farming). Five new crops in the
spring_fields.crop style (drawn standing on the bed, stage 0 seed, 1 sprout, 2 growing,
3 ripe) plus their 16x16 UI icons in the farm_icons style (outlined in each ramp's
darkest shade, light from the top left), and a heart for animal friendship.
  spring: 土豆 potato   summer: 西瓜 watermelon, 辣椒 pepper   autumn: 萝卜 radish, 茄子 eggplant
"""
from pixelkit import P, Sprite
import spring_fields as F
from farm_icons import g, _round_fruit

PREVIEW_SCALE = 6
L = P.green
NEW = ("potato", "watermelon", "pepper", "radish", "eggplant")


def crop(s, kind, stage, x, base):
    if kind not in NEW or stage < 2:
        return F.crop(s, kind if kind not in NEW else "carrot", stage, x, base)
    big = stage == 3
    if kind == "potato":                                   # a bushy clump; ripe: tubers peeping out
        r = 4 if big else 3
        s.ellipse(x, base - r, r + 1, r, L[2]).ellipse(x - 1, base - r - 1, r - 1, r - 1, L[3]).set(x - 2, base - r - 2, L[4])
        if big:
            s.set(x, base - r - 3, P.linen[3]).set(x + 2, base - r - 2, P.linen[3])
            for fx in (-4, 3):
                s.rect(x + fx, base - 1, 2, 2, P.oat[2]).set(x + fx, base - 1, P.oat[3])
    elif kind == "watermelon":                             # a trailing vine; ripe: a striped melon
        s.line(x - 5, base - 1, x + 5, base - 2, L[2]).ellipse(x - 4, base - 3, 2, 1.5, L[3]).ellipse(x + 4, base - 3, 2, 1.5, L[2])
        if big:
            s.ellipse(x, base - 3, 4, 3, L[1]).ellipse(x - 1, base - 4, 3, 2, L[2])
            for dx in (-2, 0, 2):
                s.vline(x + dx, base - 5, base - 1, L[3])
            s.set(x - 2, base - 5, L[4])
    elif kind == "pepper":                                 # a little bush; ripe: red pods hanging
        h = 9 if big else 6
        s.vline(x, base - h, base, L[1])
        for k in range(2, h, 2):
            s.hline(x - 2, x - 1, base - k, L[2]).hline(x + 1, x + 2, base - k - 1, L[3])
        s.set(x, base - h - 1, L[3])
        if big:
            for fx, fy in ((-2, 3), (2, 5), (-1, 7)):
                s.vline(x + fx, base - fy, base - fy + 2, P.coral[2]).set(x + fx, base - fy, P.coral[4])
    elif kind == "radish":                                 # leafy top; ripe: white shoulder above the soil
        h = 7 if big else 5
        for dx in (-3, -1, 1, 3):
            s.line(x, base - 1, x + dx, base - h + abs(dx) // 2, L[2 + (abs(dx) == 1)])
        if big:
            s.rect(x - 1, base - 2, 3, 3, P.porcelain[3]).set(x - 1, base - 2, P.light[1]).hline(x - 1, x + 1, base, P.porcelain[1])
    elif kind == "eggplant":                               # a staked plant; ripe: glossy purple fruit
        h = 10 if big else 6
        s.vline(x + 2, base - h - 1, base, P.oak[3]).vline(x, base - h, base, L[1])
        for k in range(2, h, 3):
            s.hline(x - 3, x - 1, base - k, L[2]).hline(x + 1, x + 3, base - k - 1, L[3])
        if big:
            for fx, fy in ((-2, 4), (1, 7)):
                s.rect(x + fx, base - fy, 2, 3, P.lilac[1]).set(x + fx, base - fy, P.lilac[2]).set(x + fx, base - fy - 1, L[2])


# ---------------------------------------------------------------- icons (16x16)
def potato():
    rows = ["................", "................", "................", "......oooo......", "....ooCCCCoo....",
            "...oHHCCdCCCo...", "..oHWHCCCCCCDo..", "..oHCCCCCdCCDo..", "..oCCdCCCCCDDo..", "..oCCCCCCCDDo...",
            "...oCCCCCDDo....", "....oooooo......", "................", "................", "................", "................"]
    O = P.oat
    return g(rows, {"o": O[0], "C": O[2], "H": O[3], "W": O[4], "D": O[1], "d": P.walnut[2]})


def watermelon():
    rows = ["................", "................", "........l.......", ".......lL.......", "....oooooooo....",
            "...oHLHLHLHLo...", "..oHWLHLHLHLDo..", "..oLHLHLHLHLDo..", "..oHLHLHLHLDDo..", "..oLHLHLHLHDDo..",
            "...oLHLHLHDDo...", "....oDDDDDDo....", ".....oooooo.....", "................", "................", "................"]
    return g(rows, {"o": L[0], "H": L[3], "L": L[1], "W": P.light[1], "D": L[1], "l": L[2]})


def pepper():
    rows = ["................", ".......ll.......", "......lLLl......", ".....oolloo.....", "....oHWCCCo.....",
            "....oHCCCCDo....", "....oHCCCCDo....", ".....oCCCCDo....", ".....oCCCDo.....", "......oCCDo.....",
            "......oCDo......", ".......oDo......", ".......oo.......", "................", "................", "................"]
    R = P.coral
    return g(rows, {"o": R[0], "C": R[2], "H": R[3], "W": R[4], "D": R[1], "l": L[2], "L": L[3]})


def radish():
    rows = [".....l...l......", "....lLl.lLl.....", ".....lLlLl......", "......lLl.......", ".....oooooo.....",
            "....oHWCCCCo....", "....oHCCCCDo....", "....oCCCCCDo....", ".....oCCCDo.....", ".....oCCCDo.....",
            "......oCDo......", "......oCo.......", ".......o........", "................", "................", "................"]
    W = P.porcelain
    return g(rows, {"o": P.slate[3], "C": W[2], "H": W[3], "W": P.light[1], "D": W[1], "l": L[2], "L": L[3]})


def eggplant():
    rows = ["................", "........l.......", ".......lLl......", "......lLLLl.....", "......oooooo....",
            ".....oHWCCCo....", "....oHHCCCCDo...", "....oHCCCCCDo...", "....oCCCCCCDo...", "....oCCCCCDDo...",
            ".....oCCCDDo....", "......ooooo.....", "................", "................", "................", "................"]
    R = P.lilac
    return g(rows, {"o": R[0], "C": R[1], "H": R[2], "W": R[3], "D": R[0], "l": L[2], "L": L[3]})


def heart():
    rows = ["................", "................", "................", "...ooo...ooo....", "..oHWCo.oCCCo...",
            "..oHCCCoCCCDo...", "..oCCCCCCCCDo...", "...oCCCCCCDo....", "....oCCCCDo.....", ".....oCCDo......",
            "......oDo.......", ".......o........", "................", "................", "................", "................"]
    R = P.coral
    return g(rows, {"o": R[0], "C": R[2], "H": R[3], "W": R[4], "D": R[1]})


ICONS = {"potato": potato, "watermelon": watermelon, "pepper": pepper, "radish": radish, "eggplant": eggplant, "heart": heart}


def stages():
    s = Sprite(100, 26 * len(NEW))
    for i, k in enumerate(NEW):
        s.rect(0, 20 + i * 26, 100, 3, F.SOIL[2])
        for st in range(4):
            crop(s, k, st, 12 + st * 22, 20 + i * 26)
    return s


def build():
    out = {"infei_crop_stages": stages()}
    out.update({f"farm_icon_{k}": f() for k, f in ICONS.items()})
    return out
