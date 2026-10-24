"""Guest furniture: oak frames, sage/oat upholstery, light from upper left.

The study chair is 18x25, with the seat at y=18 and feet on row 24.
Shared bedding is 42x40: two pillow lanes, the same width as the normal bed,
so the nightstand and wardrobe keep their original clearances.
"""
from pixelkit import P, Sprite


def study_chair():
    s = Sprite(18, 25)
    wood, cloth = P.oak, P.sage
    s.rect(2, 0, 14, 19, wood[0]).rect(3, 1, 12, 16, wood[2])
    s.hline(3, 14, 1, wood[4]).vline(3, 2, 16, wood[3])
    s.rect(4, 3, 10, 12, cloth[0]).rect(5, 4, 8, 10, cloth[2])
    s.hline(5, 12, 4, cloth[3]).vline(12, 5, 13, cloth[1])
    s.rect(2, 20, 3, 5, wood[0]).rect(13, 20, 3, 5, wood[0])
    s.vline(3, 21, 23, wood[2]).vline(14, 21, 23, wood[1])
    s.rect(0, 17, 18, 5, wood[0]).rect(1, 18, 16, 3, cloth[2])
    s.hline(1, 16, 18, cloth[4]).hline(2, 15, 20, cloth[1])
    s.set(2, 0, None).set(15, 0, None).set(0, 17, None).set(17, 17, None)
    return s


def shared_bed():
    s = Sprite(42, 40)
    wood, sheet = P.oak, P.porcelain
    s.rect(0, 0, 5, 38, wood[0]).rect(1, 1, 3, 36, wood[2])
    s.vline(1, 1, 36, wood[4]).set(0, 0, None).set(4, 0, None)
    s.rect(4, 2, 38, 34, sheet[0]).rect(5, 3, 36, 32, sheet[2])
    s.hline(5, 40, 3, sheet[3]).vline(5, 4, 33, sheet[3])
    for y in (3, 21):
        s.rect(5, y, 12, 14, sheet[0]).rect(6, y+1, 10, 12, sheet[3])
        s.vline(15, y+3, y+11, sheet[2])
    s.rect(4, 35, 38, 3, wood[0]).hline(5, 40, 35, wood[3])
    s.rect(6, 38, 2, 2, wood[0]).rect(38, 38, 2, 2, wood[0])
    return s


def shared_cover():
    s = Sprite(42, 40)
    for y, ramp in ((1, P.oat), (19, P.sage)):
        for x in range(18, 42):
            top = y + (0 if x < 30 else (x-30)//3)
            s.vline(x, top, y+17, ramp[0])
            s.vline(x, top+1, y+16, ramp[3] if x<32 else ramp[2])
            s.set(x, top+1, ramp[4]).set(x, y+15, ramp[2])
        s.vline(18, y+2, y+14, P.porcelain[3])
        for x in (26, 33, 39):
            s.vline(x, y+10, y+14, ramp[1])
        s.rect(36, y+7, 4, 10, P.clay[1]).vline(37, y+7, y+15, P.clay[3])
    return s


def sofa_blanket():
    s = Sprite(24, 15)
    r = P.sage
    for x in range(24):
        top = min(5, abs(x-8)//4)
        s.vline(x, top, 13, r[0]).vline(x, top+1, 12, r[2])
        s.set(x, top+1, r[4] if x<13 else r[3])
    s.hline(1, 22, 12, r[1]).vline(3, 3, 11, P.porcelain[2])
    for x in (10, 17, 21):
        s.vline(x, 8, 11, r[1])
    return s


def build():
    return {"guest_chair": study_chair(), "shared_bed": shared_bed(),
            "shared_cover": shared_cover(), "sofa_blanket": sofa_blanket()}
