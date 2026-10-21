"""Icons for the trip transition (user: going to the park / dock / mall,
strips sweep over the house and Buddy's head travels along a dotted trail
to an icon of the place; v2 after "not refined enough"). 32x28 stickers:
each part shaded with its own ramp and outlined in its darkest shade, lit
from the top left, then a white sticker edge and a soft drop shadow so they
read on any of the trip colours. Also a little house for the way back.
"""

from __future__ import annotations

import math

from pixelkit import P, Sprite

IW, IH = 32, 28


def part(draw, outline):
    """Draw one part on its own layer and outline it in its darkest shade."""
    s = Sprite(IW, IH)
    draw(s)
    return s.outline(outline, grow=False)


def sticker(layers):
    s = Sprite(IW, IH)
    for l in layers:
        s.blit(l, 0, 0)
    out = s.pad(2, 2, 2, 2).outline(P.linen[3], grow=False)            # white sticker edge
    shadow = Sprite(out.w, out.h)
    a = out.px[..., 3] > 0
    shadow.px[1:, 1:][a[:-1, :-1]] = (34, 24, 42, 70)                   # soft drop shadow, down right
    shadow.blit(out, 0, 0)
    return shadow


def blob(s, cx, cy, rx, ry, R, light=(-0.6, -0.8)):
    """A rounded mass shaded by the light: lit top left, shade bottom right."""
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            u, v = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if u * u + v * v > 1:
                continue
            l = -(u * light[0] + v * light[1])
            s.set(x, y, R[3] if l < -0.45 else R[2] if l < 0.25 else R[1] if l < 0.75 else R[1])
            if u * u + v * v > 0.6 and l < -0.5:
                s.set(x, y, R[4])


# ---------------------------------------------------------------- 公园: a tree, a bench, flowers
def park():
    G, Wd, B, Sl = P.green, P.walnut, P.oak, P.slate

    def ground(s):
        for x in range(1, 31):
            s.set(x, 25, P.grass[2]).set(x, 26, P.grass[1])
            if x % 3 == 0:
                s.set(x, 24, P.grass[3])
        for x, c in ((3, P.blossom), (6, P.mustard), (27, P.blossom), (30, P.lilac)):
            s.set(x, 23, c[3]).set(x, 24, P.grass[2])

    def trunk(s):
        s.rect(8, 12, 3, 13, Wd[2]).vline(8, 12, 24, Wd[3]).vline(10, 12, 24, Wd[1])
        s.line(10, 15, 13, 12, Wd[2]).set(9, 18, Wd[1]).set(9, 21, Wd[1])

    def crown(s):
        for cx, cy, rx, ry in ((9, 9, 8, 6.5), (4.5, 11, 4, 3.5), (14, 11, 4.5, 3.6), (9, 4.5, 5.5, 4)):
            blob(s, cx, cy, rx, ry, G)
        for x, y in ((6, 3), (4, 8), (10, 6), (13, 9), (7, 12)):     # leaf texture
            s.set(x, y, G[4] if y < 8 else G[2])
        for x, y in ((12, 13), (6, 14), (15, 12)):
            s.set(x, y, G[1])
        for x, y in ((11, 4), (5, 10)):                               # two red apples
            s.set(x, y, P.coral[3]).set(x, y + 1, P.coral[2])

    def bench(s):
        for k, y in enumerate((14, 17)):                              # backrest slats
            s.rect(15, y, 15, 2, B[3]).hline(15, 29, y, B[4]).hline(15, 29, y + 1, B[2])
        s.vline(16, 13, 24, Sl[2]).vline(28, 13, 24, Sl[2])           # iron ends
        s.rect(14, 20, 17, 2, B[3]).hline(14, 30, 20, B[4]).hline(14, 30, 21, B[1])   # seat
        s.vline(17, 22, 24, Sl[1]).vline(27, 22, 24, Sl[1])

    def fly(s):
        s.set(23, 6, P.mustard[4]).set(25, 6, P.mustard[4]).set(24, 7, P.walnut[1]).set(23, 7, P.mustard[3]).set(25, 7, P.mustard[3])

    return sticker([part(ground, P.grass[0]), part(trunk, Wd[0]), part(crown, G[0]), part(bench, B[0]), part(fly, P.walnut[0])])


# ---------------------------------------------------------------- 码头: a sailboat on the waves
def dock():
    S, C, L, Wd = P.sea, P.coral, P.linen, P.walnut

    def sea(s):
        for x in range(0, 32):
            top = 21 + int(round(math.sin(x * 0.7) * 1.2))
            s.vline(x, top, 26, S[2])
            s.set(x, top, S[3])
            if x % 6 in (1, 2):
                s.set(x, top - 1, L[3])
            s.set(x, 26, S[1])
        for x in range(3, 30, 7):
            s.hline(x, x + 2, 24, S[3])

    def hull(s):
        for k, y in enumerate(range(16, 22)):
            x0, x1 = 4 + k, 28 - k // 2
            s.hline(x0, x1, y, C[2] if k > 1 else L[3])
            s.set(x0, y, C[3] if k > 1 else L[3])
        s.hline(5, 27, 17, C[3])                                      # the stripe under the rail
        s.hline(7, 26, 21, C[1])
        for x in (11, 17, 23):                                        # portholes
            s.set(x, 19, P.glass[3]).set(x, 20, P.glass[1])

    def mast(s):
        s.vline(15, 1, 16, Wd[2]).vline(16, 2, 16, Wd[1])

    def sails(s):
        for y in range(3, 15):                                        # mainsail, right of the mast
            w = (y - 2) * 10 // 12
            s.hline(17, 17 + w, y, L[3])
            s.set(17 + w, y, L[2])
            if y in (7, 11):
                s.hline(17, 17 + w, y, C[3])                          # two red bands
        for y in range(6, 15):                                        # jib, left
            w = (y - 5) * 7 // 9
            s.hline(14 - w, 14, y, L[2])
            s.set(14 - w, y, L[1])

    def flag(s):
        s.hline(16, 19, 1, C[2]).hline(16, 18, 2, C[3])

    return sticker([part(sea, S[0]), part(hull, C[0]), part(mast, Wd[0]), part(sails, L[0]), part(flag, C[0])])


def loop(s, x0, x1, top, bottom, c, hi=None):
    """A bag handle: an upside-down U with rounded shoulders."""
    s.vline(x0, top + 2, bottom, c).vline(x1, top + 2, bottom, c)
    s.set(x0 + 1, top + 1, c).set(x1 - 1, top + 1, c).hline(x0 + 2, x1 - 2, top, c)
    if hi:
        s.set(x0 + 2, top, hi)


# ---------------------------------------------------------------- 商场: two shopping bags, sparkles
def mall():
    T, B, C, M = P.teal, P.blossom, P.coral, P.mustard

    def back_bag(s):
        s.rect(3, 11, 13, 14, T[2]).vline(3, 11, 24, T[3]).vline(15, 11, 24, T[1])
        s.hline(3, 15, 11, T[3]).hline(4, 14, 13, T[1])
        loop(s, 6, 11, 6, 10, T[1])                                   # handle

    def front_bag(s):
        s.rect(12, 9, 16, 17, B[3]).vline(12, 9, 25, B[4]).vline(27, 9, 25, B[2])
        s.rect(12, 9, 16, 3, B[2]).hline(12, 27, 9, B[4]).hline(12, 27, 11, B[1])   # folded top
        s.hline(13, 27, 25, B[2])

    def handles(s):                                                   # two rope loops
        loop(s, 15, 20, 3, 8, C[1], C[3])
        loop(s, 20, 25, 4, 8, C[1], C[3])

    def heart(s):
        pts = [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."]
        for j, row in enumerate(pts):
            for i, ch in enumerate(row):
                if ch == "#":
                    s.set(16 + i, 14 + j, C[2])
        s.set(17, 15, C[4]).set(18, 15, C[3]).set(17, 16, C[3])

    def sparkles(s):
        for cx, cy, r in ((29, 3, 2), (6, 4, 1)):
            s.set(cx, cy, M[4])
            for k in range(1, r + 1):
                s.set(cx - k, cy, M[3]).set(cx + k, cy, M[3]).set(cx, cy - k, M[3]).set(cx, cy + k, M[3])

    return sticker([part(back_bag, T[0]), part(front_bag, B[0]), part(handles, C[0]), part(heart, C[0]), part(sparkles, M[1])])


# ---------------------------------------------------------------- 家: a little house
def home():
    R, Fw, Te, Gl, Br = P.coral, P.facade_white, P.teal, P.glass, P.brick

    def chimney(s):
        s.rect(21, 3, 4, 6, Br[2]).vline(21, 3, 8, Br[3]).hline(20, 25, 3, Br[3])
        for x, y in ((23, 1), (25, 0)):
            s.set(x, y, P.linen[2])

    def walls(s):
        s.rect(6, 13, 21, 12, Fw[3]).vline(6, 13, 24, Fw[4]).vline(26, 13, 24, Fw[1])
        s.hline(6, 26, 24, Fw[1])

    def roof(s):
        for k in range(10):
            y = 4 + k
            s.hline(16 - k - 2, 16 + k + 2, y, R[2] if (y % 3) else R[1])
            s.set(16 - k - 2, y, R[3])
        s.hline(3, 29, 13, R[1])

    def window(s):
        s.rect(9, 15, 6, 5, Gl[3]).hline(9, 14, 15, Gl[4]).vline(12, 15, 19, Fw[1]).hline(9, 14, 17, Fw[1])

    def door(s):
        s.rect(18, 16, 6, 9, Te[2]).vline(18, 16, 24, Te[3]).set(22, 20, P.mustard[4])

    def bush(s):
        blob(s, 4, 23, 3.5, 2.5, P.green)
        blob(s, 29, 23, 3, 2.5, P.green)

    def step(s):
        s.hline(4, 28, 25, P.oak[2]).hline(4, 28, 26, P.oak[1])

    return sticker([part(chimney, Br[0]), part(walls, Fw[0]), part(roof, R[0]), part(window, Gl[0]),
                    part(door, Te[0]), part(step, P.oak[0]), part(bush, P.green[0])])


def build():
    return {"trip_park": park(), "trip_dock": dock(), "trip_mall": mall(), "trip_home": home()}


PREVIEW_SCALE = 8
