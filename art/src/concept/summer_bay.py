"""夏 · 海湾 (summer bay): ONE seamless side-view map, beach -> sea.

Owner sketch (2026-10-31): a cross-section. On the left the land is cut open
(sand on top, a tan layer, then dark earth), palms and a grey mountain behind;
the land slopes down to the right and its slope goes on under the water as
the seabed. Buddy walks off the sand straight into the water, swims at the
surface, and dives when the player clicks below it.
Style reference: a gouache beach painting (flat colour blocks, cumulus with
pale-blue shadow facets, boulders in dark teal + rust facets, white foam curls).

Layout: LAND (342px, one screen) of beach, then the existing dive map
(summer_sea, 1026px) to its right, both under one sky. Waterline WL.
Art only: nothing is wired into the game.
"""
import math
import random

import numpy as np

import summer_isle as SI
import summer_sea as SS
from pixelkit import P, Sprite

PREVIEW_SCALE = 1
LAND = 342
SKY = 96                         # extra sky above the dive map
GW, GH = LAND + SS.OW, SKY + SS.OH
WL = SKY + SS.SURF               # waterline (global)
C = SS.C


def ground_y(x):
    """Top of the sand on the land screen; meets the dive map's seabed at x=LAND."""
    if x < 236:
        return WL - 10 + int(1.2 * math.sin(x * 0.05))
    t = (x - 236) / (LAND - 236)
    return int(WL - 10 + 6 * t * t * (3 - 2 * t))


GROUND = [ground_y(x) for x in range(LAND)] + [SS.FLOOR[x] + SKY for x in range(SS.OW)]


# ------------------------------------------------------------- sky

def sky(s):
    bands = [(0, P.sky_day[1]), (40, P.sky_day[2]), (WL - 34, P.sky_day[3])]
    s.px[:] = SS.gradient_rows(bands, GH, GW)


def cloud(s, cx, base, w, seed):
    """A gouache cumulus: stacked round puffs, flat white tops, pale-blue
    shadow facets on the lower and right parts, a flat bottom."""
    rnd = random.Random(seed)
    puffs = [(cx + rnd.uniform(-w / 2, w / 2), base - rnd.uniform(4, w * 0.25), rnd.uniform(w * 0.12, w * 0.24))
             for _ in range(int(w / 6))]
    puffs.append((cx, base - w * 0.32, w * 0.26))
    yy, xx = np.mgrid[0:GH, 0:GW]
    x0, x1 = int(cx - w), int(cx + w)
    y0 = int(base - w * 0.7)
    sub = (slice(max(0, y0), base), slice(max(0, x0), min(GW, x1)))
    m = np.zeros((GH, GW), bool)
    shade = np.zeros((GH, GW), bool)
    for px, py, r in puffs:
        d = ((xx[sub] - px) ** 2 + (yy[sub] - py) ** 2)
        inside = d <= r * r
        m[sub] |= inside
        # lower-right crescent of each puff is in shadow
        sh = inside & (((xx[sub] - px + r * 0.35) ** 2 + (yy[sub] - py + r * 0.4) ** 2) > (r * 0.95) ** 2)
        shade[sub] |= sh
    lit = m & ~shade
    s.px[shade] = C(P.sky_soft[2])
    s.px[lit] = C(P.porcelain[3])
    # outline the bottom edge softly
    edge = m & ~np.roll(m, -1, 0)
    s.px[edge & (yy > base - w * 0.25)] = C(P.sky_soft[1])


def mountain(s):
    """A grey volcanic ridge far behind the land (owner sketch: grey, left),
    two flat tones: lit west faces, shaded east faces, a pale rim."""
    for x in range(0, 330):
        h = 58 * math.exp(-((x - 60) / 70) ** 2) + 26 * math.exp(-((x - 190) / 45) ** 2) + 2 * math.sin(x * 0.23)
        top = int(WL - 10 - h)
        if top >= WL - 10:
            continue
        slope = (58 * math.exp(-((x + 1 - 60) / 70) ** 2) + 26 * math.exp(-((x + 1 - 190) / 45) ** 2)) - (h - 2 * math.sin(x * 0.23))
        for y in range(top, WL - 8):
            s.set(x, y, P.sea_grey[3] if slope > 0 else P.sea_grey[2])
        s.set(x, top, P.sea_grey[4] if slope > 0 else P.sea_grey[3])


def sailboat(s, x, y):
    s.rect(x - 7, y - 2, 15, 2, P.slate[0]).hline(x - 5, x + 5, y, P.slate[0])
    for k in range(13):
        s.hline(x - 1 - k // 2, x - 1, y - 4 - (12 - k), P.porcelain[3])
        s.hline(x + 1, x + 1 + k // 3, y - 4 - (12 - k), P.porcelain[2])
    s.vline(x, y - 18, y - 2, P.slate[0])


# ------------------------------------------------------------- land

STRATA = [(0, P.sand[4]), (1, P.sand[3]), (5, P.sand[2]), (9, P.clay[3]), (17, P.clay[2]),
          (24, P.walnut[2]), (40, P.walnut[1]), (70, P.walnut[0])]


def strata(s):
    """The cut-open land: wavy bands that follow the ground and dip under the
    sea along the slope; fades into the dive map's own seabed."""
    rnd = random.Random(7)
    for x in range(LAND + 360):
        g = GROUND[x]
        wob = 2 * math.sin(x * 0.045) + 1.5 * math.sin(x * 0.13 + 1)
        for y in range(g, GH):
            d = y - g
            k = 0
            for i, (dd, _) in enumerate(STRATA):
                if d >= dd + (wob if i > 2 else 0):
                    k = i
            col = STRATA[k][1]
            if x >= LAND:                                            # under the sea the earth ends along a slanted
                edge = 40 + 0.9 * (y - WL) + (1 if SS.BAYER[y % 4, x % 4] > 0.5 else 0)
                if x - LAND > edge:                                  # line, like a fault: the reef rock goes on
                    continue
                if y > WL and k < 3:                                 # wet sand one shade darker
                    col = P.sand[max(0, P.sand.index(col) - 1)]
            s.set(x, y, col)
        if x >= LAND:
            continue
        for _ in range(2):                                           # pebbles and roots in the earth
            y = g + rnd.randint(26, GH - g - 1)
            s.set(x, y, P.walnut[0] if y - g < 60 else P.walnut[1])


def boulder(s, cx, base, w, h, seed=0):
    """A gouache boulder (like the reference): a rounded lump in dark teal, a
    big rust facet on the sunlit top-left, a sandy chip on top, a slate
    shadow underneath, outlined in teal."""
    rnd = random.Random(seed)
    top = base - h
    cut = rnd.uniform(-0.15, 0.25)
    pts = []
    for y in range(top, base + 1):
        t = (y - top) / h
        hw = w / 2 * math.sqrt(max(0.0, 1 - (1 - t) ** 2))
        hw = max(1, int(hw))
        for x in range(cx - hw, cx + hw + 1):
            u = (x - cx) / hw
            col = P.teal[1]
            if u * 0.8 + t < 0.75 + cut:
                col = P.clay[2]
            if u * 0.8 + t < 0.35 + cut:
                col = P.clay[3]
            if u + t * 2 < -0.1 and t < 0.35:
                col = P.sand[3]
            if t > 0.78 or (u > 0.55 and t > 0.4):
                col = P.teal[0]
            s.set(x, y, col)
            if x in (cx - hw, cx + hw) or y == top:
                pts.append((x, y))
    for x, y in pts:
        s.set(x, y, P.teal[0])


def foam(s, x0, x1, y):
    """White foam curls along the waterline."""
    for x in range(x0, x1):
        w = int(1.2 * math.sin(x * 0.4) + math.sin(x * 0.11))
        s.set(x, y + w, P.porcelain[3])
        if (x // 5) % 3 == 0:
            s.set(x, y + w + 1, P.porcelain[3])
        if (x // 3) % 4 == 1:
            s.set(x, y + w - 1, P.sky_soft[3])


def footprints(s, x0, x1):
    for i, x in enumerate(range(x0, x1, 7)):
        y = GROUND[x] + 2 + (i % 2) * 2
        s.set(x, y, P.sand[1]).set(x + 1, y, P.sand[1])


def land(s, frame=0):
    mountain(s)
    tmp = Sprite(GW, GH)                                             # front_yard trees are drawn on a 342px canvas:
    SI.jungle(tmp, 0, 150, WL - 10, seed=31, rmin=8, rmax=14)        # their outline wraps to x=341, clear it
    tmp.px[:, 300:] = 0
    s.blit(tmp, 0, 0)
    strata(s)
    # headland rocks on the far left, a scatter by the water like the reference
    for cx, w, h, sd in ((18, 34, 26, 1), (44, 30, 18, 2), (6, 22, 14, 3), (68, 22, 12, 4), (88, 14, 8, 5)):
        boulder(s, cx, GROUND[max(0, cx)] + 3, w, h, sd)
    for cx, w, h, sd in ((LAND - 10, 16, 8, 6), (LAND + 18, 20, 11, 7), (LAND + 2, 9, 5, 8)):
        boulder(s, cx, GROUND[cx] + 2, w, h, sd)
    SI.palm2(s, 112, GROUND[112], 70, lean=1, frame=frame, seed=2)
    SI.palm2(s, 140, GROUND[140], 52, lean=1, frame=frame, seed=5)
    SI.palm2(s, 74, GROUND[74] - 4, 44, lean=-1, frame=frame, seed=8)
    SI.umbrella(s, 196, GROUND[196], R=P.coral)
    SI.lounger(s, 184, GROUND[190])
    SI.lounger(s, 214, GROUND[218], C=P.mustard)
    footprints(s, 230, 312)
    # shoreline foam where the slope enters the water
    xs = [x for x in range(LAND - 40, LAND + 60) if GROUND[x] >= WL - 1]
    if xs:
        foam(s, xs[0] - 4, xs[0] + 70, WL)
    foam(s, LAND - 22, LAND + 40, WL - 1)


# ------------------------------------------------------------- compose

def sea_layer():
    """The dive map composite with its own little sky removed."""
    full = SS.compose3()
    wat = SS.water()
    sky_px = np.all(full.px[:SS.SURF] == wat.px[:SS.SURF], axis=2)
    full.px[:SS.SURF][sky_px] = 0
    for x in range(48):                                              # the beach end of the dive map is land now
        full.px[:SS.SURF, x] = 0
    return full


def bay(frame=0):
    s = Sprite(GW, GH)
    sky(s)
    for cx, base, w, sd in ((120, 60, 70, 1), (300, 44, 56, 2), (560, 70, 90, 3), (860, 50, 64, 4), (1180, 66, 80, 5)):
        cloud(s, cx, base, w, sd)
    s.blit(sea_layer(), LAND, SKY)
    # water in the land screen's right part (the beach slope goes under it)
    for x in range(LAND - 60, LAND):
        if GROUND[x] > WL:
            for y in range(WL, GROUND[x]):
                s.set(x, y, P.sea[4] if y - WL < 2 else P.sea[3])
    sailboat(s, LAND + 300, WL)
    land(s, frame)
    return s


def view(full, cx, cy, size=SS.VIEW):
    vw, vh = size
    x0 = max(0, min(GW - vw, cx - vw // 2))
    y0 = max(0, min(GH - vh, cy - vh // 2))
    return full.crop(x0, y0, vw, vh)


def build():
    full = bay()
    return {
        "bay_preview": full,
        "bay_view_beach": view(full, 200, WL - 40, (342, 118)),
        "bay_view_shore": view(full, LAND, WL + 30),
        "bay_view_dive": view(full, LAND + 200, WL + 90),
    }
