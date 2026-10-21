"""海边: out on a wooden dock by the sea (user: simple, a dock; now and then
a cargo ship or a speedboat goes by far out). Same canvas and scale as the
house (342x118); Buddy walks along the planks like on the sidewalk at home.

    a big sky | the sea to the horizon
    the dock's railing along the back, two lamps, a life ring
    weathered planks (wider towards us), two bollards, a coil of rope

Kept sparse on purpose. Seasons tint the sea and sky (winter grey);
snow, rain and night (the lamps) are overlays. Ships, gulls and clouds
are drawn by the page.

    build() -> beach_<season>, beach_snow, beach_wet, beach_lit, ship,
    speedboat, previews.
"""

from __future__ import annotations

import math
import random

import numpy as np

from pixelkit import P, Sprite

W, H = 342, 118
SEASONS = ["spring", "summer", "autumn", "winter"]
HORIZON = 52
DECK = 88               # the dock's back edge
FEET = 106              # Buddy's feet
WALK = (10, 332)
LAMPS = (118, 236)
POSTS = range(14, W, 38)
BOLLARDS = (62, 282)
RING = 166              # the life ring hangs here

WD, IRON = P.ash, P.slate
SEA = {"winter": P.sea_grey}


def sea_of(season):
    return SEA.get(season, P.sea)


def sky(s, season):
    S = P.sky_soft if season == "winter" else P.sky_day
    for y0, y1, c in ((0, 16, S[1]), (16, 34, S[2]), (34, HORIZON, S[3])):
        s.rect(0, y0, W, y1 - y0, c)
    for y0, a, b in ((16, S[1], S[2]), (34, S[2], S[3])):
        s.dither(0, y0 - 1, W, 1, a, b, "sparse2")
        s.dither(0, y0, W, 1, a, b, "checker")


def sea(s, season):
    R = sea_of(season)
    rnd = random.Random(3)
    for y in range(HORIZON, DECK):
        t = (y - HORIZON) / (DECK - HORIZON)
        s.hline(0, W - 1, y, R[1] if t < 0.25 else R[2] if t < 0.75 else R[3])
    for y0, a, b in ((HORIZON + 9, R[1], R[2]), (HORIZON + 27, R[2], R[3])):
        s.dither(0, y0, W, 1, a, b, "checker")
    s.hline(0, W - 1, HORIZON, R[0])
    for x in range(250, W):                                            # a far shore, faint
        h = int(2 + 1.5 * math.sin(x * 0.08) + (x - 250) * 0.02)
        s.vline(x, HORIZON - h, HORIZON - 1, P.sky_soft[1])
    for _ in range(90):                                                # gentle swell
        y = rnd.randint(HORIZON + 2, DECK - 2)
        t = (y - HORIZON) / (DECK - HORIZON)
        x, n = rnd.randrange(W), int(2 + t * 6)
        s.hline(x, x + n, y, R[3] if t < 0.5 else R[4])


def railing(s):
    top = DECK - 17
    for x in POSTS:                                                    # posts
        s.rect(x, top - 1, 3, DECK - top + 3, WD[2]).vline(x, top - 1, DECK + 1, WD[3]).vline(x + 2, top - 1, DECK + 1, WD[1])
        s.hline(x - 1, x + 3, top - 2, WD[3])
    for y in (top + 1, top + 8):                                       # two rails
        s.hline(0, W - 1, y, WD[3]).hline(0, W - 1, y + 1, WD[1])
    cx, cy = RING, top + 9                                             # the life ring on the rails
    for y in range(cy - 5, cy + 6):
        for x in range(cx - 5, cx + 6):
            d = math.hypot(x - cx, y - cy)
            if 2.2 <= d <= 4.8:
                quarter = (x - cx >= 0) == (y - cy >= 0)
                s.set(x, y, (P.coral[2] if quarter else P.linen[3]) if d > 2.8 else P.coral[1])
    s.set(cx - 3, cy - 3, P.coral[3])


def deck(s):
    rnd = random.Random(7)
    rows = [DECK, DECK + 3, DECK + 7, DECK + 12, DECK + 18, DECK + 24, H]   # planks widen towards us
    for i in range(len(rows) - 1):
        y0, y1 = rows[i], rows[i + 1]
        s.rect(0, y0, W, y1 - y0, WD[2] if i % 2 else WD[3])
        s.hline(0, W - 1, y0, WD[1])
        s.hline(0, W - 1, y0 + 1, WD[4] if i % 2 == 0 else WD[3])
        seam = 60 + i * 23                                             # butt joints, staggered
        for x in range(rnd.randint(0, 40), W, seam):
            s.vline(x, y0 + 1, y1 - 1, WD[1])
            if y1 - y0 > 4:                                            # nail heads
                s.set(x + 2, y0 + 2, IRON[2]).set(x - 2, y0 + 2, IRON[2])
        for _ in range((y1 - y0) * 14):                                # grain
            x, y = rnd.randrange(W - 6), rnd.randint(y0 + 2, y1 - 1)
            s.hline(x, x + rnd.randint(2, 6), y, WD[1] if rnd.random() < 0.5 else WD[4])
    s.hline(0, W - 1, DECK, WD[0])


def lamp(s, x):
    b = DECK + 1
    s.rect(x - 2, b - 3, 5, 3, IRON[1]).hline(x - 2, x + 2, b - 3, IRON[3])
    s.vline(x, b - 40, b - 3, IRON[2]).vline(x + 1, b - 40, b - 3, IRON[1])
    top = b - 48
    s.rect(x - 3, top + 2, 8, 6, P.glass[0]).frame(x - 3, top + 2, 8, 6, IRON[1])
    s.rect(x - 1, top + 3, 1, 3, P.linen[1])
    for k in range(3):
        s.hline(x - 4 + k, x + 5 - k, top + 1 - k, IRON[2] if k else IRON[1])
    s.hline(x - 2, x + 3, top + 8, IRON[1])


def bollard(s, x):
    b = FEET - 4
    s.rect(x - 4, b - 6, 9, 6, IRON[1]).vline(x - 4, b - 6, b - 1, IRON[3]).vline(x + 4, b - 6, b - 1, IRON[0])
    s.rect(x - 5, b - 8, 11, 2, IRON[2]).hline(x - 5, x + 5, b - 8, IRON[3])
    s.hline(x - 3, x + 3, b - 9, IRON[2])
    s.dither(x - 4, b, 10, 1, WD[1], None, "checker")


def rope(s, x):
    """A coil of rope beside the bollard."""
    b = FEET - 3
    for k, (rx, ry) in enumerate(((6, 2.2), (4.5, 1.6), (3, 1.1))):
        s.ellipse(x, b - 2 - k, rx, ry, P.oat[2 + (k % 2)], fill=False)
    s.set(x - 1, b - 4, P.oat[4]).line(x - 6, b - 2, x - 12, b - 6, P.oat[2])


def props(s):
    railing(s)
    for x in LAMPS:
        lamp(s, x)
    for x in BOLLARDS:
        bollard(s, x)
    rope(s, BOLLARDS[0] + 16)


def background(season):
    s = Sprite(W, H)
    sky(s, season)
    sea(s, season)
    deck(s)
    props(s)
    return s


def tops(mask):
    up = np.zeros_like(mask)
    up[1:] = mask[:-1]
    return mask & ~up


def snow_layer():
    S = P.snow
    s = Sprite(W, H)
    rnd = random.Random(13)
    s.rect(0, DECK + 1, W, H - DECK - 1, S[3])
    for _ in range(260):
        s.set(rnd.randrange(W), rnd.randint(DECK + 2, H - 1), S[2])
    s.rect(0, FEET - 2, W, 4, S[2]).hline(0, W - 1, FEET - 2, S[1])   # a trodden line
    for x in range(3, W, 8):
        s.hline(x, x + 1, FEET - 1 + (x // 8) % 2, S[1])
    parts = Sprite(W, H)
    props(parts)
    solid = parts.px[..., 3] > 0
    s.px[solid & (np.arange(H)[:, None] > DECK)] = 0
    ys, xs = np.nonzero(tops(solid))
    for x, y in zip(xs, ys):
        s.set(x, y - 1, S[3]).set(x, y, S[3] if rnd.random() < 0.6 else S[2])
    return s


def wet_layer():
    s = Sprite(W, H)
    rnd = random.Random(17)
    for _ in range(1600):
        s.set(rnd.randrange(W), rnd.randint(DECK + 2, H - 1), WD[1])
    for x0, y, w in ((30, DECK + 14, 26), (150, DECK + 21, 34), (250, DECK + 9, 20)):   # shine where it pools
        s.hline(x0, x0 + w, y, P.sky_day[2]).hline(x0 + w // 4, x0 + w // 2, y, P.sky_day[3])
    return s


def lit():
    s = Sprite(W, H)
    for x in LAMPS:
        top = DECK + 1 - 48
        s.rect(x - 2, top + 3, 6, 4, P.light[0]).rect(x - 1, top + 4, 4, 2, P.light[1])
    return s


def ship():
    """A container ship for the horizon, small with distance (bow right)."""
    s = Sprite(40, 11)
    hull, R = P.slate, P.coral
    for k in range(3):
        s.hline(1 + k, 38 - k * 2, 7 + k, hull[2] if k < 2 else hull[1])
    s.hline(3, 33, 10, R[1])
    cols = (P.coral[2], P.teal[2], P.mustard[3], P.hydrangea[2], P.mint[2], P.clay[2])
    for i, x in enumerate(range(10, 34, 4)):                           # stacked containers
        for j in range(1 + (i % 3 != 2)):
            s.rect(x, 5 - j * 2, 3, 2, cols[(i * 2 + j) % len(cols)])
    s.rect(3, 1, 5, 6, P.linen[3]).hline(3, 7, 3, P.glass[1])          # bridge at the stern
    s.rect(5, 0, 2, 1, P.coral[2])
    return s


def speedboat():
    """A white speedboat (bow right); the page adds its wake."""
    s = Sprite(16, 6)
    s.hline(0, 13, 3, P.linen[3]).hline(1, 14, 4, P.linen[2]).hline(3, 15, 5, P.hydrangea[1])
    s.set(14, 3, P.linen[3])
    s.rect(6, 1, 4, 2, P.glass[1]).hline(5, 9, 0, P.slate[2])
    s.set(3, 2, P.coral[2]).set(4, 2, P.coral[2])
    return s


def gull(frame):
    """A gull in flight: 0 wings up, 1 level, 2 down."""
    s = Sprite(9, 5)
    Wt, G = P.linen, P.pave
    s.hline(3, 5, 2, Wt[3]).set(6, 2, Wt[3]).set(7, 2, P.mustard[3])
    if frame == 0:
        s.line(0, 0, 3, 2, G[2]).line(5, 2, 8, 0, G[2])
    elif frame == 1:
        s.hline(0, 3, 2, G[2]).hline(5, 8, 2, G[2])
    else:
        s.line(0, 4, 3, 2, G[2]).line(5, 2, 8, 4, G[2])
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


def scene(season="summer"):
    s = background(season)
    s.blit(ship(), 200, HORIZON - 9)
    s.blit(speedboat(), 80, HORIZON + 14)
    return s


def build():
    out = {}
    for se in SEASONS:
        out[f"beach_{se}"] = background(se)
        out[f"beach_preview_{se}"] = scene(se)
    out["beach_snow"] = snow_layer()
    out["beach_wet"] = wet_layer()
    out["beach_lit"] = lit()
    snowy = scene("winter")
    snowy.blit(out["beach_snow"], 0, 0)
    out["beach_preview_snow"] = snowy
    out["beach_ship"] = ship()
    out["beach_speedboat"] = speedboat()
    return out


PREVIEW_SCALE = 4
