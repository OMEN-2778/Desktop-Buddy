"""海边: a strip of beach. Same canvas and scale as the house (342x118);
Buddy walks along the sand like on the sidewalk at home.

    sky | a far island | the sea, a wooden pier on the left, a headland with
    a lighthouse and a cottage on the right
    the surf (page: 8 frames, washing in and out)
    sand: a lifeguard tower, a sandcastle, an umbrella and towel, a ball
    a dune with marram grass and a slatted fence at the front

Seasons: summer is the busy one (umbrella, towel, ball, castle); spring and
autumn are quieter (a furled umbrella, the castle half washed away), the
marram grass greens then goes gold; winter is grey sea, empty sand, the
tower shut. Snow, rain and night (lighthouse, cottage window) are overlays.

    build() -> beach_<season>, beach_surf_<season>_<0-7>, beach_snow,
    beach_wet, beach_lit, gull / crab / boat frames, clouds, previews.
"""

from __future__ import annotations

import math
import random

import numpy as np

from pixelkit import P, Sprite

W, H = 342, 118
SEASONS = ["spring", "summer", "autumn", "winter"]
HORIZON = 46
SHORE = 82              # where the still sea meets the sand
FEET = 102              # Buddy's feet
WALK = (10, 332)
DUNE = 108              # dune from here down
TOWER = 126             # lifeguard tower centre x
CASTLE = 64
UMBRELLA = 262
LIGHT = (320, 10)       # lighthouse lamp centre (x, y)
SURF_FRAMES = 8

SD, WOOD, ST = P.sand, P.oak, P.slate
SEA = {"winter": P.sea_grey}


def sea_of(season):
    return SEA.get(season, P.sea)


def sky(s, season):
    S = P.sky_soft if season == "winter" else P.sky_day
    for y0, y1, c in ((0, 12, S[1]), (12, 28, S[2]), (28, HORIZON, S[3])):
        s.rect(0, y0, W, y1 - y0, c)
    for y0, a, b in ((12, S[1], S[2]), (28, S[2], S[3])):
        s.dither(0, y0 - 1, W, 1, a, b, "sparse2")
        s.dither(0, y0, W, 1, a, b, "checker")


def island(s):
    C = P.sky_soft
    for x in range(14, 84):
        t = (x - 14) / 70
        h = int(5 * math.sin(t * math.pi) + 2 * math.sin(t * 9) + (3 if 0.2 < t < 0.45 else 0))
        if h > 0:
            s.vline(x, HORIZON - h, HORIZON - 1, C[1] if x > 40 else C[2])
    s.hline(14, 83, HORIZON - 1, C[0])


def sea(s, season):
    R = sea_of(season)
    rnd = random.Random(3)
    for y in range(HORIZON, SHORE):
        t = (y - HORIZON) / (SHORE - HORIZON)
        c = R[1] if t < 0.22 else R[2] if t < 0.7 else R[3]
        s.hline(0, W - 1, y, c)
    for y0, a, b in ((HORIZON + 8, R[1], R[2]), (HORIZON + 25, R[2], R[3])):
        s.dither(0, y0, W, 1, a, b, "checker")
    s.hline(0, W - 1, HORIZON, R[0])
    for _ in range(140):                                               # swell: light crests, dark troughs
        y = rnd.randint(HORIZON + 2, SHORE - 3)
        t = (y - HORIZON) / (SHORE - HORIZON)
        x, n = rnd.randrange(W), int(2 + t * 7)
        s.hline(x, x + n, y, R[3] if t < 0.5 else R[4])
        s.hline(x + 1, x + n - 1, y + 1, R[1] if t < 0.5 else R[2])
    if season != "winter":                                             # the sun's glitter path
        for _ in range(40):
            y = rnd.randint(HORIZON + 1, HORIZON + 14)
            x = int(rnd.gauss(170, 26))
            s.hline(x, x + rnd.randint(1, 3), y, R[4])


def headland(s, season):
    """Rocks with grass on top, a lighthouse and a little cottage."""
    rnd = random.Random(5)
    G = {"spring": P.leaf_spring, "summer": P.grass, "autumn": P.mustard, "winter": P.sage}[season]
    RK = P.pave
    for x in range(286, W):
        t = (x - 286) / (W - 286)
        top = int(40 - 12 * math.sqrt(min(1, t * 1.6)) + 1.5 * math.sin(x * 0.4))
        foot = SHORE + 1 - int(10 * (1 - t) ** 2)                      # the rocks slope into the sea
        for y in range(top, SHORE + 2):
            depth = y - top
            strata = (y + int(2 * math.sin(x * 0.2))) % 6 == 0
            c = RK[3] if x < 290 + depth * 0.3 else RK[1] if strata else RK[2]
            if depth < 4:
                c = G[3] if depth == 0 else G[2] if depth < 3 else G[1]
            s.set(x, y, c)
        for y in range(max(top, foot - 6), SHORE + 2):                 # boulders at the foot
            if (x // 5 + y // 3) % 3 == 0:
                s.set(x, y, RK[1] if (x + y) % 4 else RK[0])
        if rnd.random() < 0.5:
            s.set(x, top - 1, G[4])
    for _ in range(12):                                                # bushes on the clifftop
        x = rnd.randint(288, W - 4)
        t = (x - 286) / (W - 286)
        y = int(40 - 12 * math.sqrt(min(1, t * 1.6))) - 1
        s.ellipse(x, y, 2.5, 1.8, G[2]).set(x - 1, y - 1, G[4]).set(x + 1, y + 1, G[1])
    for _ in range(30):                                                # cracks in the rock
        x, y = rnd.randint(290, W - 2), rnd.randint(40, SHORE)
        if s.px[y, x, 3]:
            s.set(x, y, RK[0]).set(x + 1, y + 1, RK[1])
    R = sea_of(season)
    for x in range(282, W):                                            # foam where the sea hits the rocks
        if (x * 7) % 5 < 3:
            s.set(x, SHORE - 2 - (x % 3 == 0), R[4])
    # cottage
    Fw = P.facade_white
    cx, cb = 296, 34
    s.rect(cx, cb - 8, 13, 8, Fw[3]).vline(cx + 12, cb - 8, cb - 1, Fw[1]).hline(cx, cx + 12, cb - 1, Fw[1])
    for k in range(5):
        s.hline(cx - 1 + k, cx + 13 - k, cb - 9 - k, P.teal[2] if k else P.teal[1])
    s.rect(cx + 2, cb - 6, 3, 3, P.glass[1]).rect(cx + 8, cb - 5, 3, 5, P.teal[1])
    # lighthouse: white tower, red bands, the lamp room and a dome
    lx, ly = LIGHT
    for y in range(ly + 5, 40):
        hw = 3 + (y - ly - 5) * 0.12
        for x in range(int(lx - hw), int(lx + hw) + 1):
            band = ((y - ly - 5) // 6) % 2 == 1
            R2 = P.coral if band else Fw
            c = R2[3] if x < lx - hw + 2 else R2[1] if x > lx + hw - 2 else R2[2]
            s.set(x, y, c)
    s.rect(lx - 5, ly + 3, 11, 2, ST[1]).hline(lx - 5, lx + 5, ly + 3, ST[2])   # gallery
    s.rect(lx - 3, ly - 2, 7, 5, P.glass[0]).vline(lx, ly - 2, ly + 2, ST[1])    # lamp room (dark by day)
    s.rect(lx - 1, ly - 1, 3, 3, P.mustard[3])                         # the lamp
    for k in range(4):
        s.hline(lx - 3 + k, lx + 3 - k, ly - 3 - k, P.coral[1] if k else P.coral[0])
    s.set(lx, ly - 7, ST[1])


def pier(s):
    """A wooden pier running out to sea on the left, seen side-on."""
    y = 60
    for x in range(0, 50):                                             # deck
        s.set(x, y, WOOD[3]).set(x, y + 1, WOOD[2]).set(x, y + 2, WOOD[1])
    for x in range(1, 50, 8):                                          # piles into the water
        s.vline(x, y + 3, SHORE + 2, WOOD[1]).vline(x + 1, y + 3, SHORE + 2, WOOD[0])
        s.set(x, SHORE - 1, P.sea[4]).set(x + 2, SHORE - 1, P.sea[4])
    for x in range(0, 50, 4):                                          # railing
        s.vline(x, y - 5, y - 1, WOOD[2])
    s.hline(0, 48, y - 5, WOOD[3]).hline(0, 48, y - 3, WOOD[1])
    s.vline(47, y - 12, y - 1, ST[1]).rect(45, y - 14, 5, 3, ST[2])    # a lamp at the end
    s.rect(46, y - 13, 3, 1, P.glass[1])


def sand(s, season):
    rnd = random.Random(7)
    s.rect(0, SHORE, W, H - SHORE, SD[3])
    s.rect(0, SHORE, W, 6, SD[2])                                      # damp sand by the water
    s.dither(0, SHORE + 6, W, 2, SD[2], SD[3], "checker")
    for _ in range(1300):
        x, y = rnd.randrange(W), rnd.randint(SHORE + 2, H - 1)
        s.set(x, y, SD[rnd.choice([2, 2, 4, 4, 1])])
    for y in range(SHORE + 10, DUNE, 4):                               # wind ripples
        for x0 in range(rnd.randint(0, 20), W, rnd.randint(24, 40)):
            n = rnd.randint(6, 14)
            s.hline(x0, x0 + n, y, SD[4]).hline(x0 + 1, x0 + n - 1, y + 1, SD[2])
    for _ in range(14):                                                # shells and pebbles
        x, y = rnd.randint(4, W - 4), rnd.randint(SHORE + 3, DUNE - 2)
        k = rnd.random()
        if k < 0.4:
            s.set(x, y, P.blossom[3]).set(x + 1, y, P.blossom[4]).set(x, y + 1, P.blossom[2])
        elif k < 0.7:
            s.set(x, y, P.linen[3]).set(x + 1, y, P.linen[2])
        else:
            s.set(x, y, P.pave[1]).set(x + 1, y, P.pave[2])
    if season != "winter":                                             # a starfish
        x, y = 196, SHORE + 4
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (-1, 1), (1, 1), (0, 0)):
            s.set(x + dx, y + dy, P.coral[3])
        s.set(x, y, P.coral[4])
    if season == "autumn":                                             # seaweed washed up
        for x0 in (40, 150, 230):
            for k in range(9):
                s.set(x0 + k, SHORE + 3 + (k % 3 == 0), P.green[1] if k % 2 else P.mustard[1])


def tower(s, season):
    """The lifeguard tower: stilts, a ladder, a little hut, a flag."""
    cx, b = TOWER, FEET - 6
    W_ = WOOD
    plat = b - 22
    for lx in (cx - 10, cx + 9):
        s.vline(lx, plat, b, W_[1]).vline(lx + 1, plat, b, W_[0])
    s.line(cx - 9, plat + 2, cx + 9, b - 4, W_[1])                     # a cross brace
    s.line(cx + 9, plat + 2, cx - 9, b - 4, W_[1])
    for y in range(plat + 2, b, 3):                                    # ladder down the front
        s.hline(cx - 3, cx + 2, y, W_[3])
    s.vline(cx - 4, plat, b, W_[2]).vline(cx + 3, plat, b, W_[2])
    s.rect(cx - 13, plat - 2, 27, 3, W_[3]).hline(cx - 13, cx + 13, plat - 2, W_[4]).hline(cx - 13, cx + 13, plat, W_[1])
    hut = P.facade_white
    s.rect(cx - 9, plat - 14, 19, 12, hut[3]).vline(cx + 9, plat - 14, plat - 3, hut[1])
    s.hline(cx - 9, cx + 9, plat - 3, hut[1])
    if season == "winter":                                             # shut for the winter
        s.rect(cx - 6, plat - 11, 13, 6, W_[2])
        for y in range(plat - 11, plat - 5, 2):
            s.hline(cx - 6, cx + 6, y, W_[1])
    else:
        s.rect(cx - 6, plat - 11, 13, 6, P.glass[1]).hline(cx - 6, cx + 6, plat - 11, P.glass[0])
        s.vline(cx, plat - 11, plat - 6, hut[2])
    s.rect(cx - 9, plat - 4, 19, 2, P.coral[2]).hline(cx - 9, cx + 9, plat - 4, P.coral[3])   # red stripe
    for k in range(4):                                                 # roof
        s.hline(cx - 12 + k * 2, cx + 12 - k * 2, plat - 15 - k, P.coral[1] if k == 0 else P.coral[2] if k < 3 else P.coral[3])
    if season != "winter":
        s.vline(cx + 11, plat - 30, plat - 16, ST[2])                  # flagpole + flag
        for k in range(4):
            s.hline(cx + 12, cx + 18 - k, plat - 30 + k, P.coral[3] if k < 2 else P.mustard[3])


def castle(s, season):
    if season == "winter":
        return
    x, b = CASTLE, FEET - 1
    worn = season in ("spring", "autumn")
    S = SD
    s.rect(x - 11, b - 5, 23, 5, S[2]).hline(x - 11, x + 11, b - 5, S[4]).hline(x - 12, x + 12, b, S[1])
    towers = ((x - 8, 8), (x, 12), (x + 8, 8)) if not worn else ((x - 8, 5), (x, 8), (x + 8, 3))
    for tx, h in towers:
        s.frame(tx - 3, b - 6 - h, 7, h + 2, S[1])
    s.frame(x - 12, b - 6, 25, 7, S[1])
    s.rect(x - 11, b - 5, 23, 5, S[2]).hline(x - 11, x + 11, b - 5, S[4])
    for tx, h in towers:
        s.rect(tx - 2, b - 5 - h, 5, h, S[3]).vline(tx + 2, b - 5 - h, b - 6, S[1]).vline(tx - 2, b - 5 - h, b - 6, S[4])
        if not worn:
            s.set(tx - 2, b - 6 - h, S[3]).set(tx, b - 6 - h, S[3]).set(tx + 2, b - 6 - h, S[2])
    if not worn:
        s.rect(x - 1, b - 4, 3, 4, S[1])                               # the gate
        s.vline(x, b - 22, b - 18, P.walnut[1]).hline(x + 1, x + 3, b - 22, P.coral[3]).set(x + 1, b - 21, P.coral[2])
        s.rect(x + 15, b - 5, 5, 5, P.teal[3]).hline(x + 14, x + 20, b - 6, P.teal[4]).hline(x + 15, x + 19, b - 1, P.teal[1])   # bucket
        s.line(x + 22, b - 1, x + 25, b - 8, P.coral[2]).rect(x + 21, b - 2, 3, 2, P.coral[3])   # spade


def umbrella(s, season):
    x, b = UMBRELLA, FEET - 3
    if season == "winter":
        return
    if season != "summer":                                             # furled
        s.vline(x, b - 26, b, P.linen[1])
        for k in range(14):
            w = 1 if k < 3 or k > 11 else 2
            s.hline(x - w + 1, x + w, b - 25 + k, P.coral[2] if k % 4 else P.linen[3])
        return
    s.vline(x, b - 24, b + 1, P.linen[1])                              # open: stripes, a scalloped rim
    for y in range(b - 32, b - 22):
        t = (y - (b - 32)) / 10
        hw = int(18 * math.sqrt(max(0, t * (2 - t))))
        for xx in range(x - hw, x + hw + 1):
            stripe = int((xx - x) / max(1, (y - (b - 34))) * 2.2 + 10) % 2
            R = P.coral if stripe else P.linen
            c = R[3] if xx < x - hw * 0.3 and y < b - 27 else R[2]
            if y == b - 23:
                c = R[1]
            s.set(xx, y, c)
    for xx in range(x - 18, x + 19, 3):
        s.set(xx, b - 22, P.coral[1])
    s.set(x, b - 33, P.linen[1])
    tw = 30                                                            # the towel, then the ball
    for k in range(tw):
        c = (P.teal[3], P.linen[3], P.mustard[3])[(k // 4) % 3]
        s.vline(x - 22 + k, b + 1, b + 4, c)
    s.hline(x - 22, x - 23 + tw, b + 4, P.teal[1])
    bx, by = x + 28, FEET - 3
    s.ellipse(bx, by, 3, 3, P.linen[3])
    s.rect(bx - 3, by - 1, 7, 2, P.coral[2]).rect(bx - 1, by - 3, 2, 7, P.hydrangea[2])
    s.set(bx - 1, by - 2, P.linen[3]).hline(bx - 2, bx + 2, by + 4, SD[1])


def dune(s, season):
    rnd = random.Random(11)
    G = {"spring": P.leaf_spring, "summer": P.green, "autumn": P.mustard, "winter": P.oat}[season]
    for x in range(W):
        top = DUNE + int(2 + 2 * math.sin(x * 0.05) + math.sin(x * 0.17))
        s.vline(x, top, H - 1, SD[4] if x % 9 else SD[3])
        s.set(x, top, SD[4])
    for x in range(0, W, 2):                                           # marram grass tufts
        if rnd.random() < 0.6:
            base = H - 1 - rnd.randint(0, 3)
            for k in range(rnd.randint(2, 4)):
                h = rnd.randint(4, 9)
                lean = rnd.choice([-2, -1, 1, 2])
                s.line(x, base, x + lean, base - h, G[rnd.choice([1, 2, 3])])
    for x in (14, 150, 270):                                           # a slatted fence, here and there
        for k in range(0, 34, 4):
            if x + k < W:
                s.vline(x + k, H - 9, H - 1, WOOD[2]).set(x + k, H - 10, WOOD[3])
        s.hline(x, min(W - 1, x + 33), H - 7, P.ash[1]).hline(x, min(W - 1, x + 33), H - 3, P.ash[1])


def background(season):
    s = Sprite(W, H)
    sky(s, season)
    island(s)
    sea(s, season)
    headland(s, season)
    pier(s)
    sand(s, season)
    tower(s, season)
    castle(s, season)
    umbrella(s, season)
    dune(s, season)
    return s


def head_layer(season):
    """The headland alone: the page draws it over the clouds and the boat."""
    s = Sprite(W, H)
    headland(s, season)
    return s


def surf(season, f):
    """One frame of the shore: the wash runs up the sand and slides back,
    leaving it dark and shining; a new crest rolls in behind it."""
    s = Sprite(W, H)
    R = sea_of(season)
    ph = f / SURF_FRAMES * 2 * math.pi
    reach = 4.5 + 4.5 * math.sin(ph)                                   # how far up the sand the wash is
    rnd = random.Random(f * 3)
    for x in range(W):
        if x > 288:                                                    # (rocks)
            continue
        wob = 1.2 * math.sin(x * 0.11 + ph) + 0.8 * math.sin(x * 0.037 - ph * 0.5)
        edge = SHORE + reach + wob
        hi = SHORE + 9 + wob                                           # where the last wave got to
        for y in range(SHORE - 1, int(hi) + 1):
            if y < edge - 1:
                s.set(x, y, R[3] if (x + y) % 5 else R[4])
            elif y < edge + 0.5:
                s.set(x, y, P.linen[3])                                # foam front
            elif math.cos(ph) < 0 and y <= hi:                         # sliding back: wet sand
                s.set(x, y, SD[2] if (x + y) % 3 else SD[1])
        if rnd.random() < 0.3 and edge > SHORE + 1:
            s.set(x, int(edge) - 1, P.linen[2])                        # bubbles behind the front
    crest = SHORE - 8 + (f % SURF_FRAMES) * 0.9                        # the next wave on its way in
    for x in range(0, 288):
        y = int(crest + 0.8 * math.sin(x * 0.09 + ph))
        if (x // 6 + f) % 3:
            s.set(x, y, R[4]).set(x, y + 1, R[2])
    return s


def snow_layer():
    S = P.snow
    s = Sprite(W, H)
    rnd = random.Random(13)
    s.rect(0, SHORE + 8, W, H - SHORE - 8, S[3])                       # the dry sand
    s.dither(0, SHORE + 8, W, 1, S[2], None, "checker")
    s.rect(0, FEET - 2, W, 4, S[2]).hline(0, W - 1, FEET - 2, S[1])    # a trodden line
    for x in range(3, W, 8):
        s.hline(x, x + 1, FEET - 1 + (x // 8) % 2, S[1])
    for _ in range(300):
        s.set(rnd.randrange(W), rnd.randint(SHORE + 9, H - 1), S[2])
    parts = Sprite(W, H)
    headland(parts, "winter")
    pier(parts)
    tower(parts, "winter")
    solid = Sprite(W, H)
    tower(solid, "winter")
    m = solid.px[..., 3] > 0
    s.px[m] = 0
    for x in range(W):                                                 # rock top, deck, roof, rails
        col = parts.px[:, x, 3] > 0
        for y in range(1, H):
            if col[y] and not col[y - 1] and y < SHORE:
                s.set(x, y - 1, S[3]).set(x, y, S[2] if rnd.random() < 0.5 else S[3])
    for x in range(W):                                                 # the dune and fence
        top = DUNE + int(2 + 2 * math.sin(x * 0.05) + math.sin(x * 0.17))
        s.vline(x, top - 1, H - 1, S[3])
        if x % 7 == 0:
            s.vline(x, H - 9, H - 3, P.oat[1])
    return s


def wet_layer():
    s = Sprite(W, H)
    rnd = random.Random(17)
    for _ in range(1800):
        s.set(rnd.randrange(W), rnd.randint(SHORE + 8, H - 1), SD[2] if rnd.random() < 0.7 else SD[1])
    return s


def lit():
    """Night: the lighthouse lamp, the cottage window, the pier lamp."""
    s = Sprite(W, H)
    lx, ly = LIGHT
    s.rect(lx - 3, ly - 2, 7, 5, P.light[0]).rect(lx - 1, ly - 1, 3, 3, P.light[1])
    s.rect(298, 28, 3, 3, P.light[0])
    s.rect(45, 46, 5, 2, P.light[0]).rect(46, 46, 3, 1, P.light[1])
    return s


def gull(frame):
    """A gull in flight: 0 wings up, 1 level, 2 down; 3 standing."""
    s = Sprite(9, 5)
    Wt, G = P.linen, P.pave
    if frame == 3:
        s.ellipse(4, 2, 2.5, 1.5, Wt[3]).hline(2, 5, 1, G[2]).set(6, 0, Wt[3]).set(7, 1, P.mustard[3])
        s.set(6, 0, Wt[3]).set(5, 0, Wt[2]).vline(3, 3, 4, P.mustard[2]).vline(5, 3, 4, P.mustard[2])
        s.set(6, 1, P.ink[0])
        return s
    s.hline(3, 5, 2, Wt[3]).set(6, 2, Wt[3]).set(7, 2, P.mustard[3])
    if frame == 0:
        s.line(0, 0, 3, 2, G[2]).line(5, 2, 8, 0, G[2])
    elif frame == 1:
        s.hline(0, 3, 2, G[2]).hline(5, 8, 2, G[2])
    else:
        s.line(0, 4, 3, 2, G[2]).line(5, 2, 8, 4, G[2])
    s.set(0, 0 if frame == 0 else 2 if frame == 1 else 4, G[0])
    return s


def crab(frame):
    s = Sprite(7, 4)
    C = P.coral
    s.ellipse(3, 2, 2.5, 1.2, C[2]).hline(2, 4, 1, C[3])
    s.set(2, 0, C[1]).set(4, 0, C[1])
    claws = 0 if frame == 0 else 1
    s.set(0, 1 - claws, C[3]).set(6, 1 - claws, C[3])
    for x in (1, 5) if frame == 0 else (0, 6):
        s.set(x, 3, C[1])
    return s


def boat():
    """A small sailboat for the horizon."""
    s = Sprite(12, 10)
    s.hline(1, 10, 8, P.walnut[2]).hline(2, 9, 9, P.walnut[1])
    s.vline(6, 1, 7, P.walnut[1])
    for k in range(6):
        s.hline(7, 7 + k // 1 if k < 5 else 11, 2 + k, P.linen[3])
    for k in range(5):
        s.hline(5 - k // 2, 5, 3 + k, P.linen[2])
    return s


def cloud(i):
    """Three soft clouds for the page to drift across the sky."""
    rnd = random.Random(i)
    w = (34, 24, 46)[i]
    s = Sprite(w + 4, 12)
    pts = [(rnd.uniform(5, w - 3), rnd.uniform(5, 8), rnd.uniform(3, 5)) for _ in range(w // 4)]
    for x, y, r in pts:
        s.ellipse(x, y, r, r * 0.8, P.linen[2])
    for x, y, r in pts:
        s.ellipse(x - 0.8, y - 1, r * 0.7, r * 0.55, P.linen[3])
    for x in range(s.w):
        col = np.nonzero(s.px[:, x, 3])[0]
        if len(col):
            s.set(x, col.max(), P.linen[1])
    return s


def scene(season="summer", f=0):
    s = background(season)
    s.blit(surf(season, f), 0, 0)
    return s


def build():
    out = {}
    for se in SEASONS:
        out[f"beach_{se}"] = background(se)
        for f in range(SURF_FRAMES):
            out[f"beach_surf_{se}_{f}"] = surf(se, f)
        out[f"beach_preview_{se}"] = scene(se)
    out["beach_snow"] = snow_layer()
    out["beach_wet"] = wet_layer()
    out["beach_lit"] = lit()
    snowy = scene("winter")
    snowy.blit(out["beach_snow"], 0, 0)
    out["beach_preview_snow"] = snowy
    sheet = Sprite(120, 12)
    for i in range(4):
        sheet.blit(gull(i), i * 10, 0)
    for i in range(2):
        sheet.blit(crab(i), 42 + i * 8, 0)
    sheet.blit(boat(), 60, 0)
    for i in range(3):
        sheet.blit(cloud(i), [74, 0, 0][i], 0) if i == 0 else None
    out["beach_critters"] = sheet
    return out


PREVIEW_SCALE = 4
