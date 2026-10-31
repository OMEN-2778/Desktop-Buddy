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


JOIN = LAND + 150                # the beach curve meets the dive map's seabed here


def ground_y(x):
    """Walkable top: flat sand, then ONE smooth beach curve down into the sea
    (gentle at the waterline, steeper further out) until the dive map's floor."""
    if x < 236:
        return WL - 10 + int(1.2 * math.sin(x * 0.05))
    if x < JOIN:
        t = (x - 236) / (JOIN - 236)
        end = SS.FLOOR[JOIN - LAND] + SKY
        return int(WL - 10 + (end - WL + 10) * (t ** 1.8) * (1.6 - 0.6 * t))
    return SS.FLOOR[x - LAND] + SKY


GROUND = [ground_y(x) for x in range(GW)]


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
    for x in range(0, 236):
        h = 58 * math.exp(-((x - 60) / 70) ** 2) + 26 * math.exp(-((x - 190) / 45) ** 2) + 2 * math.sin(x * 0.23)
        top = int(WL - 10 - h)
        if top >= WL - 16:
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


EARTH = np.zeros((GH, GW), bool)    # cut-open earth: stays warm, no water fog


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
            EARTH[y, x] = True
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
    for cx, w, h, sd in ((LAND + 40, 22, 12, 7), (LAND + 26, 10, 6, 8)):
        boulder(s, cx, GROUND[cx] + 2, w, h, sd)
    SI.palm2(s, 112, GROUND[112], 70, lean=1, frame=frame, seed=2)
    SI.palm2(s, 140, GROUND[140], 52, lean=1, frame=frame, seed=5)
    SI.palm2(s, 74, GROUND[74] - 4, 44, lean=-1, frame=frame, seed=8)
    SI.umbrella(s, 196, GROUND[196], R=P.coral)
    SI.lounger(s, 184, GROUND[190])
    SI.lounger(s, 214, GROUND[218], C=P.mustard)
    footprints(s, 230, 312)


# ------------------------------------------------------------- under water (owner: calmer, a real gradient)

def hexrgb(h):
    return np.array(SS.C(h)[:3], float)


WATER_STOPS = [(WL, P.sea[4]), (WL + 70, P.sea[3]), (WL + 170, P.sea[2]), (WL + 270, P.sea[1]), (GH, P.sea[0])]


def water_rgb(y):
    """Smooth vertical gradient (no dither: the page draws it as a canvas gradient)."""
    for (y0, c0), (y1, c1) in zip(WATER_STOPS, WATER_STOPS[1:]):
        if y <= y1:
            t = max(0.0, (y - y0) / (y1 - y0))
            return hexrgb(c0) * (1 - t) + hexrgb(c1) * t
    return hexrgb(WATER_STOPS[-1][1])


WROWS = np.array([water_rgb(y) for y in range(GH)])


def horizon(s):
    """远景 above the water: the far sea as a pale band behind everything, distant
    islands standing on it, a sailboat."""
    s.px[WL - 7:WL, :, :3] = C(P.sea[3])[:3]
    s.px[WL - 7, :, :3] = C(P.sea[4])[:3]
    for cx, w, h in ((420, 90, 16), (520, 50, 9), (980, 120, 22), (1110, 60, 11), (1290, 80, 14)):
        for x in range(cx - w // 2, cx + w // 2):
            u = (x - cx) / (w / 2)
            top = int(WL - 7 - h * max(0.0, 1 - u * u) ** 0.7 - 1.5 * math.sin(x * 0.3))
            for y in range(top, WL - 7):
                s.set(x, y, P.sky_soft[2] if u < -0.1 or y - top < 2 else P.sky_soft[1])
    for x in range(0, GW, 9):                                        # glints on the far water
        if (x * 13) % 7 < 2:
            s.hline(x, x + 2, WL - 4 - (x % 3), P.sea[4])
    sailboat(s, 760, WL - 4)


def rock(s):
    """Seabed beyond the earth: flat gouache tones (lit crust, body, core),
    sand on gentle ground. Depth fog is added afterwards."""
    m = np.zeros((GH, GW), bool)
    sea_mask = SS.terrain().px[..., 3] > 0
    m[SKY:, LAND:] = sea_mask
    for x in range(JOIN):
        m[:, x] = False
        m[GROUND[x]:, x] = True
    under = np.zeros((GH, GW))
    run = np.zeros(GW)
    for y in range(GH):
        run = np.where(m[y], run + 1, 0)
        under[y] = run
    for x in range(LAND, GW):
        slope = abs(GROUND[min(GW - 1, x + 3)] - GROUND[max(0, x - 3)]) / 6
        for y in np.nonzero(m[:, x])[0]:
            if y < WL - 2:
                col = P.sea_grey[3] if under[y, x] < 3 else P.sea_grey[2] if under[y, x] < 12 else P.sea_grey[1]
            else:
                d = under[y, x]
                col = (P.sand[3] if slope < 1 else P.sea_grey[3]) if d < 2 else \
                      (P.sand[2] if slope < 1 else P.sea_grey[2]) if d < 5 else \
                      P.sea_grey[1] if d < 18 else P.slate[0]
            s.set(x, int(y), col)


def calm_decor():
    """Few, grouped pieces (owner: the floor was too busy)."""
    d = Sprite(SS.OW, SS.OH)
    F = [GROUND[x + LAND] - SKY for x in range(SS.OW)]
    kinds = list(SS.CORALS)
    for x0 in (40, 100):                                             # sea grass tufts on the beach slope
        for k in range(4):
            SS.seagrass(d, x0 + k * 4, F[x0 + k * 4] + 1, 4, 10 + k * 2, seed=x0 + k)
    SS.starfish(d, 70, F[70] - 1, P.coral)
    for cx in (200, 290):                                            # two coral heads, a cluster round each
        SS.bommie(d, cx, F[cx] + 2, 1.3, seed=cx)
        for k, dx in enumerate((-22, -14, 16, 24)):
            SS.coral(d, kinds[(cx + k) % len(kinds)], cx + dx, F[cx + dx] + 1, 0.9, seed=cx + k)
    SS.sponge(d, 250, F[250] + 1, P.lilac, 2, seed=1)
    SS.shipwreck(d, 446, F[500] + 2)                                 # the wreck in its kelp
    for x in (420, 432, 560, 574, 588):
        SS.tall_weed(d, x, F[x] + 1, 40 + (x * 7) % 25, P.teal, seed=x)
    SS.anchor(d, 610, F[610] + 1)
    SS.bommie(d, 630, 112, 0.6, seed=630)
    SS.tiki(d, 800, F[800] + 2)
    for x in (680, 700, 850, 870):
        SS.coral(d, kinds[x % len(kinds)], x, F[x] + 1, 1.0, seed=x)
    for y in (60, 100, 150):
        x = next((xx for xx in range(850, SS.OW) if F[xx] <= y), SS.OW - 1)
        SS.coral(d, kinds[y % len(kinds)], x - 1, y + 2, 0.8, seed=y)
    return d


def calm_life():
    s = Sprite(SS.OW, SS.OH)
    put = lambda spr, x, y: s.blit(spr, x, y)
    put(SS.turtle(0), 150, 70)
    put(SS.manta(0), 480, 150)
    put(SS.diver(0, P.hydrangea, P.skin_tan), 330, 60)
    put(SS.diver(1, P.coral, P.skin), 700, 120)
    for k in range(14):                                              # one silver shoal
        put(SS.fish("school", k % 2), 560 + int(22 * math.cos(k * 1.3)), 70 + int(8 * math.sin(k * 1.7)))
    for k, (x, y) in enumerate(((230, 150), (244, 158), (238, 168), (262, 146), (300, 160))):
        put(SS.fish("tang", k % 2), x, y)
    for x, y in ((760, 190), (780, 200), (880, 150)):
        put(SS.fish("butterflyfish", 0), x, y)
    put(SS.jelly(0), 620, 40)
    put(SS.big_fish("eagleray", 0), 900, 110)
    return s


def fog(s):
    """Everything under the surface takes on the water colour with depth, so the
    floor, the earth and the creatures sit IN the water."""
    px = s.px[WL:, :, :3].astype(float)
    f = np.clip(0.08 + (np.arange(WL, GH) - WL) / 420, 0, 0.62)[:, None, None]
    f = np.where(EARTH[WL:, :, None], 0.0, f)
    s.px[WL:, :, :3] = (px * (1 - f) + WROWS[WL:, None, :] * f).astype(np.uint8)


def bay(frame=0):
    s = Sprite(GW, GH)
    sky(s)
    for cx, base, w, sd in ((120, 60, 70, 1), (300, 44, 56, 2), (560, 70, 90, 3), (860, 50, 64, 4), (1180, 66, 80, 5)):
        cloud(s, cx, base, w, sd)
    horizon(s)
    s.px[WL:, :, :3] = WROWS[WL:, None, :].astype(np.uint8)          # the water
    s.px[WL:, :, 3] = 255
    for mask_layer, k in ((SS.far2(), 0.86), (SS.far1(), 0.76)):    # far reef ranges: flat, a shade darker
        m = mask_layer.px[..., 3] > 0
        reg = s.px[SKY:, LAND:, :3]
        reg[m] = (WROWS[SKY:, None, :].repeat(SS.OW, 1)[m] * k).astype(np.uint8)
    for x in range(GW):                                              # surface seen from below
        s.set(x, WL, P.porcelain[3])
        s.set(x, WL + 1, P.sea[4])
    rock(s)
    land(s, frame)
    s.blit(calm_decor(), LAND, SKY)
    s.blit(calm_life(), LAND, SKY)
    rays = SS.rays()
    rays.px[:, :, 3] = np.where(rays.px[..., 3] > 0, 255, 0)
    rp = _pad(rays)
    rp.px[EARTH] = 0
    SS.blend_into(s, rp, 0.10)
    fog(s)
    shore(s)
    return s


def _pad(layer):
    big = Sprite(GW, GH)
    big.blit(layer, LAND, SKY)
    return big


def shore(s):
    """Where the sand enters the water: wet sand, a wash of foam lying on it,
    a thin shallow wedge of pale water."""
    xs = [x for x in range(200, JOIN) if GROUND[x] >= WL]
    x0 = xs[0]
    for x in range(x0 - 14, x0):                                     # wet sand just above the line
        s.set(x, GROUND[x], P.sand[2]).set(x, GROUND[x] + 1, P.sand[2])
    for x in range(x0, x0 + 40):                                     # shallow wedge: lighter water over the sand
        for y in range(WL, GROUND[x]):
            c = s.px[y, x, :3].astype(float)
            s.px[y, x, :3] = (c * 0.6 + hexrgb(P.sea[4]) * 0.4).astype(np.uint8)
    foam(s, x0 - 8, x0 + 46, WL)
    for x in range(x0 - 10, x0 - 2):                                 # the wash front, lying on the sand
        if (x // 2) % 2 == 0:
            s.set(x, GROUND[x] - 1, P.porcelain[3])


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
