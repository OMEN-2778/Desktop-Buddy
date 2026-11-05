"""草帽湾 lodge: Buddy asleep in the koa bed (owner 2026-11-05: "the quilt must bulge when she sleeps").

An overlay for summer_isle.lodge_inside's bed, in the lodge picture's own coordinates (the game draws it at
the picture's place, after her rotated head on the pillow): the coral Hawaiian quilt pulled up to the chin
over one soft round mound, taller than her head right beside it (skill: sleeping), sloping to the feet,
white breadfruit appliqué on the flat part, the sheet turned down at the neck.
"""
from pixelkit import P, Sprite

W, H = 62, 62           # same size as the lodge picture's left part; only the bed area is painted
BASE = 39               # the row the quilt rests on (the bed's quilt band ends here)


def _profile(x0, x1, peak_x, peak_top, neck_top, flat_top, feet_top):
    out = {}
    for x in range(x0, x1 + 1):
        if x <= peak_x:
            k = (x - x0) / max(1, peak_x - x0)
            t = neck_top + (peak_top - neck_top) * (1 - (1 - k) ** 2)
        else:
            k = (x - peak_x) / max(1, x1 - peak_x)
            t = peak_top + (flat_top - peak_top) * k ** 1.3
            if x1 - 6 <= x <= x1 - 3:
                t = min(t, feet_top)
        out[x] = int(round(t))
    return out


def cover():
    s = Sprite(W, H)
    Q = P.coral
    x0, x1 = 24, 48                                   # chin .. footboard
    top = _profile(x0, x1, x0 + 6, 18, 20, 32, 30)
    xs = sorted(top)
    for x in xs:
        t = top[x]
        for y in range(t, BASE + 1):
            if y == t:
                c = Q[4] if x < x0 + 10 else Q[3]          # lit from the top-left
            elif y >= BASE - 1:
                c = Q[1]
            elif x > x0 + 12 and y > t + 3 and y < BASE - 2:
                c = Q[2]
            else:
                c = Q[2] if y > t + 1 else Q[3]
            s.set(x, y, c)
        # soft shade on the right side of the round form
        if x > x0 + 9:
            s.set(x, BASE - 2, Q[1])
    s.vline(x1, top[x1], BASE, Q[1])                        # the folded edge at the feet
    # breadfruit appliqué where the cover is low enough to show it
    for x in range(x0 + 4, x1 - 2, 7):
        y = max(top[x] + 3, 26)
        if y <= BASE - 3:
            s.set(x, y + 1, P.porcelain[3]).set(x - 1, y, P.porcelain[3]).set(x + 1, y, P.porcelain[3]).set(x, y + 2, P.porcelain[3])
    # the sheet turned down at the neck
    t = top[x0]
    s.vline(x0, t, BASE - 1, P.porcelain[3]).vline(x0 + 1, t, BASE - 2, P.porcelain[2])
    return s


def build():
    return {"summer_lodge_cover": cover()}
