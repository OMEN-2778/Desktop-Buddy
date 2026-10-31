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
import _bay_parts as BP
import beach as BE
from pixelkit import P, Sprite

PREVIEW_SCALE = 1
PRE = 684                        # 旅舍 screen (0-342) and 更衣室 screen (342-684) before the beach
LAND = PRE + 342                 # the beach ends / the dive map starts here
SKY = 96                         # extra sky above the dive map
GW, GH = LAND + SS.OW, SKY + SS.OH
WL = SKY + SS.SURF               # waterline (global)
C = SS.C


JOIN = LAND + 250                # the beach profile meets the dive map's seabed here
STACK = (LAND + 900, GW)         # the sea stack that closes the map on the right


def _beach_keys():
    return [(PRE + 236, WL - 10), (PRE + 300, WL - 7), (LAND - 6, WL - 1), (LAND + 40, WL + 7),
            (LAND + 62, WL + 11), (LAND + 80, WL + 9), (LAND + 104, WL + 18), (LAND + 150, WL + 58),
            (LAND + 196, SKY + 150), (LAND + 228, SKY + 170), (JOIN, SS.FLOOR[JOIN - LAND] + SKY)]


def _hermite(keys, x):
    """Smooth curve through the keys (cubic Hermite, tangents from the
    neighbours), so the beach flows: berm, long shallow run, a sandbar, a
    soft drop-off."""
    for i in range(len(keys) - 1):
        (x0, y0), (x1, y1) = keys[i], keys[i + 1]
        if x0 <= x <= x1:
            def tan(j):
                a, b = keys[max(0, j - 1)], keys[min(len(keys) - 1, j + 1)]
                return (b[1] - a[1]) / (b[0] - a[0])
            h = x1 - x0
            t = (x - x0) / h
            m0, m1 = tan(i) * h, tan(i + 1) * h
            return (2 * t ** 3 - 3 * t ** 2 + 1) * y0 + (t ** 3 - 2 * t ** 2 + t) * m0 + \
                   (-2 * t ** 3 + 3 * t ** 2) * y1 + (t ** 3 - t ** 2) * m1
    return keys[-1][1]


def ground_y(x):
    """Walkable top: flat sand, then the beach profile into the sea, then the
    dive map's seabed."""
    if x < PRE + 236:
        return WL - 10 + int(1.2 * math.sin(x * 0.05))
    if x < JOIN:
        return int(round(_hermite(_beach_keys(), x)))
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


PEAKS = [(150, 70, 62), (430, 90, 40), (PRE + 60, 70, 54), (PRE + 190, 45, 24)]   # x, width, height


def mountain(s):
    """Grey volcanic ridges far behind the land (owner sketch: grey), one
    continuous range over all three land screens, ending before the beach
    slope. Two flat tones: lit west faces, shaded east faces, a pale rim."""
    def hgt(x):
        return sum(h * math.exp(-((x - c) / w) ** 2) for c, w, h in PEAKS)
    for x in range(0, PRE + 236):
        h = hgt(x) + 2 * math.sin(x * 0.23) + 6
        top = int(WL - 10 - h)
        if top >= WL - 16:
            continue
        lit = hgt(x + 1) > hgt(x)
        for y in range(top, WL - 8):
            s.set(x, y, P.sea_grey[3] if lit else P.sea_grey[2])
        s.set(x, top, P.sea_grey[4] if lit else P.sea_grey[3])


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
    sea and run on under the whole seabed (owner: no hard line between earth
    and reef). Where the seabed is steep the skin is bare rock, not sand."""
    rnd = random.Random(7)
    for x in range(GW):
        g = GROUND[x]
        steep = abs(GROUND[min(GW - 1, x + 3)] - GROUND[max(0, x - 3)]) / 6
        wob = 2 * math.sin(x * 0.045) + 1.5 * math.sin(x * 0.13 + 1)
        for y in range(g, GH):
            d = y - g
            k = 0
            for i, (dd, _) in enumerate(STRATA):
                if d >= dd + (wob if i > 2 else 0):
                    k = i
            col = STRATA[k][1]
            if d < 3 and x < 470 - 30 * SS.BAYER[y % 4, x % 4]:     # lawn round the lodge, fading into sand
                col = (P.grass[3], P.grass[2], P.grass[1])[d]
            if x >= LAND:
                if y > WL and k < 3:                                 # wet sand one shade darker
                    col = P.sand[max(0, P.sand.index(col) - 1)]
                if steep > 1.2 and d < 7:                            # bare rock skin on steep faces
                    col = (P.sea_grey[3], P.sea_grey[2], P.sea_grey[2], P.sea_grey[1], P.sea_grey[1], P.walnut[1], P.walnut[1])[d]
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


def screen_piece(draw, dy):
    """Draw summer_isle pieces (made for a 342x118 screen, lane at y=94) and
    return them lifted onto our ground line."""
    tmp = Sprite(SI.W, SI.H)
    draw(tmp)
    tmp.px[:, :1] = 0
    tmp.px[:, -1:] = 0
    return tmp


DY = (WL - 10) - (SI.LANE[0] - 1)    # summer_isle's lane top -> our ground


def jungle_strip(s, x0, x1, seed):
    """front_yard trees live on a 342px canvas: draw in 300px pieces."""
    for o in range(x0, x1, 300):
        tmp = Sprite(SI.W, SI.H + 20)
        SI.jungle(tmp, 0, min(300, x1 - o), WL - 10 - DY, seed=seed + o, rmin=8, rmax=14)
        tmp.px[:, 330:] = 0                                          # pieces overlap; only the wrapped column goes
        s.blit(tmp, o, DY)


def lodge_screen(t):
    b = SI.LANE[0] - 1
    for x, h, ln, sd in ((24, 62, 1, 1), (40, 50, -1, 6), (268, 56, -1, 2), (320, 66, -1, 3)):
        SI.palm2(t, x, b + 2, h, lean=ln, seed=sd)
    SI.banana(t, 252, b, 30, 1)
    SI.banana(t, 300, b, 26, 2)
    for x, F in ((62, P.coral), (88, P.blossom), (256, P.mustard), (282, P.coral)):
        SI.hibiscus(t, x, b, 11, 11, F)
    SI.plumeria(t, 74, b, 30)
    SI.lodge(t)
    for x in (86, 244):
        SI.tiki_torch(t, x, b)
        SI.heliconia(t, x + 6, b, P.coral if x < 100 else P.mustard)
    SI.monstera(t, 100, b, 1.2)
    SI.monstera(t, 230, b, 1.1)
    SI.mailbox_sign(t, 316, b)


def cabana_screen(t):
    b = SI.LANE[0] - 1
    for x, h, ln, sd in ((20, 60, 1, 4), (36, 48, -1, 12), (226, 64, 1, 5), (244, 50, -1, 13), (318, 58, 1, 14)):
        SI.palm2(t, x, b + 2, h, lean=ln, seed=sd)
    SI.banana(t, 50, b, 24, 3)
    SI.heliconia(t, 200, b, P.coral)
    SI.hibiscus(t, 264, b, 9, 9, P.mustard)
    SI.canoe(t, 272, b + 2)
    SI.hibiscus(t, 30, b, 9, 9, P.blossom)


def land(s, frame=0):
    BP.mountains(s, 0, PRE + 236, WL - 9, [(170, 60, 74), (440, 80, 56), (PRE + 40, 60, 66), (PRE + 180, 40, 30)], 9)
    gy = lambda x: GROUND[max(0, min(GW - 1, x))]
    BP.jungle(s, 0, PRE + 170, gy, 31)
    BP.understory(s, 0, PRE + 160, gy, 8)
    strata(s)
    for cx, w, h, sd in ((10, 34, 30, 1), (34, 26, 18, 2), (2, 20, 40, 3)):    # rocks close the map on the left
        boulder(s, cx, GROUND[max(0, cx)] + 3, w, h, sd)
    s.blit(screen_piece(lodge_screen, DY), 0, DY)
    s.blit(screen_piece(cabana_screen, DY), 342, DY)
    BP.cabana3d(s, 342 + SI.CABANA[0], 342 + SI.CABANA[1], WL - 9, {k: 342 + v for k, v in SI.CABANA_DOORS.items()})
    BP.understory(s, 342 + 190, 342 + 250, gy, 4)
    for cx, w, h, sd in ((PRE + 30, 20, 12, 4), (PRE + 46, 12, 7, 5), (LAND + 52, 18, 9, 7), (LAND + 40, 9, 5, 8)):
        boulder(s, cx, GROUND[cx] + 2, w, h, sd)
    SI.palm2(s, PRE + 112, GROUND[PRE + 112], 70, lean=1, frame=frame, seed=2)
    SI.palm2(s, PRE + 140, GROUND[PRE + 140], 52, lean=1, frame=frame, seed=5)
    SI.palm2(s, PRE + 74, GROUND[PRE + 74], 44, lean=-1, frame=frame, seed=8)
    SI.umbrella(s, PRE + 196, GROUND[PRE + 196], R=P.coral)
    SI.lounger(s, PRE + 184, GROUND[PRE + 190])
    SI.lounger(s, PRE + 214, GROUND[PRE + 218], C=P.mustard)
    footprints(s, 470, PRE + 300)


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
    for cx, w, h in ((PRE + 420, 90, 16), (PRE + 520, 50, 9), (PRE + 980, 120, 22), (PRE + 1110, 60, 11), (PRE + 1290, 80, 14)):
        for x in range(cx - w // 2, cx + w // 2):
            u = (x - cx) / (w / 2)
            top = int(WL - 7 - h * max(0.0, 1 - u * u) ** 0.7 - 1.5 * math.sin(x * 0.3))
            for y in range(top, WL - 7):
                s.set(x, y, P.sky_soft[2] if u < -0.1 or y - top < 2 else P.sky_soft[1])
    for x in range(0, GW, 9):                                        # glints on the far water
        if (x * 13) % 7 < 2:
            s.hline(x, x + 2, WL - 4 - (x % 3), P.sea[4])
    sailboat(s, PRE + 760, WL - 4)


def rock(s):
    """Seabed beyond the earth: flat gouache tones (lit crust, body, core),
    sand on gentle ground. Depth fog is added afterwards."""
    m = np.zeros((GH, GW), bool)
    sea_mask = SS.terrain().px[..., 3] > 0
    m[SKY:, LAND:] = sea_mask
    for x in range(JOIN):
        m[:, x] = False
        m[GROUND[x]:, x] = True
    m[:WL + 30, STACK[0]:] = False                                   # the sea stack replaces the old surface rocks
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
    top = np.zeros_like(EARTH)                                       # the sand skin of the slope is IN the water
    for x in range(GW):
        top[GROUND[x]:GROUND[x] + 10, x] = True
    f = np.where((EARTH & ~top)[WL:, :, None], 0.0, f)
    s.px[WL:, :, :3] = (px * (1 - f) + WROWS[WL:, None, :] * f).astype(np.uint8)


def bay(frame=0):
    s = Sprite(GW, GH)
    sky(s)
    # owner: use the game's own drifting clouds (beach.cloud, the sprites the page drifts)
    rnd = random.Random(5)
    for x in range(20, GW, 110):
        s.blit(BE.cloud(rnd.randrange(3)), x + rnd.randint(-30, 30), rnd.randint(4, 40))
    BP.mountains(s, 0, PRE + 250, WL - 8, [(80, 80, 70), (300, 60, 52), (560, 90, 64), (PRE + 120, 60, 40)], 5, far=True)
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
    cx, cy = BP.sea_stack(s, STACK[0] + 6, GW + 10, WL, GH, 3)
    SI.palm2(s, cx + 2, cy, 34, lean=-1, seed=21)
    foam(s, STACK[0] - 2, GW, WL)
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
    xs = [x for x in range(PRE, JOIN) if GROUND[x] >= WL]
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
        "bay_view_lodge": view(full, 171, WL - 50, (342, 118)),
        "bay_view_cabana": view(full, 513, WL - 50, (342, 118)),
        "bay_view_beach": view(full, PRE + 171, WL - 50, (342, 118)),
        "bay_view_shore": view(full, LAND, WL + 30),
        "bay_view_dive": view(full, LAND + 200, WL + 90),
    }
