"""夏日海岛 · 海底: the big dive map (art only, not in the game yet).

The dive view is the house width and TWICE its height (342x236, owner: the
picture stretches upward while diving, the UI above moves up with it). The
map is OW x OH, much larger than one view; the camera eases after Buddy, who
swims wherever the player clicks.

No invisible walls: the terrain itself closes the map.
    left   the beach slope rises out of the water (swim up it = back ashore)
    top    the sea surface (she can surface for air)
    right  a volcanic reef wall climbs to the surface, rocks break the waves
    bottom solid seabed everywhere; the trench ends in rock and darkness

Left to right: 浅滩 sandy shallows with seagrass and a turtle cleaning rock |
珊瑚花园 coral garden on a reef plateau | 沉船 a sunken sampan-era wreck on the
sand plain | 深沟 the blue trench | 熔岩拱门 lava arch and pillow lava with a
sunken tiki | 礁墙 the reef wall. Light from the surface: god rays, caustics on
the shallow floor, colour fading to blue with depth.

    build() -> sea_water (depth gradient), sea_far (parallax silhouettes),
    sea_terrain, sea_decor (corals etc., in front of the terrain), sea_front
    (foreground fronds the diver passes behind), sea_rays, creatures,
    sea_preview, sea_map_small. HOTSPOTS and SPAWNS are the interactive spots.
"""
from __future__ import annotations

import math
import random

import numpy as np

from pixelkit import P, Sprite, rgba

PREVIEW_SCALE = 1
OW, OH = 1026, 354         # owner: smaller and fuller (3 x 1.5 dive views)
VIEW = (342, 236)
SURF = 20                  # waterline (sky above it)


def C(hex_):
    return np.array(rgba(hex_), np.uint8)


# ------------------------------------------------------------- seabed profile

KEYS = [(0, SURF - 4), (40, 30), (110, 110), (170, 168), (200, 182), (260, 176), (330, 188),
        (360, 198), (400, 250), (430, 262), (580, 266), (612, 250), (650, 236), (720, 232),
        (820, 238), (860, 222), (900, 150), (940, 70), (980, 26), (1026, 14)]


def floor_y(x):
    for (x0, y0), (x1, y1) in zip(KEYS, KEYS[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            t = t * t * (3 - 2 * t)
            y = y0 + (y1 - y0) * t
            return int(y + 3 * math.sin(x * 0.07) + 2 * math.sin(x * 0.19 + 1))
    return KEYS[-1][1]


FLOOR = [floor_y(x) for x in range(OW)]


def depth_ramp(y):
    """Which shade set to use at depth y: shallow, mid, deep, abyss."""
    return 0 if y < 110 else 1 if y < 220 else 2 if y < 300 else 3


# ------------------------------------------------------------- water

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
WATER = [(SURF, P.sea[4]), (60, P.sea[3]), (140, P.sea[2]), (230, P.sea[1]), (330, P.sea[0])]


def gradient_rows(stops, h, w):
    """Ordered-dither vertical gradient through palette colours (no new colours)."""
    out = np.zeros((h, w, 4), np.uint8)
    xs = np.arange(w)
    for y in range(h):
        for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
            if y0 <= y < y1:
                t = (y - y0) / (y1 - y0)
                pick = BAYER[y % 4][xs % 4] < t
                out[y] = np.where(pick[:, None], C(c1), C(c0))
                break
        else:
            out[y] = C(stops[-1][1] if y >= stops[-1][0] else stops[0][1])
    return out


def water():
    s = Sprite(OW, OH)
    s.px[:] = gradient_rows(WATER, OH, OW)
    s.px[:SURF // 2] = C(P.sky_day[2])
    s.px[SURF // 2:SURF] = C(P.sky_day[3])
    px = s.px
    for x in range(OW):                                            # the surface seen from below: a bright wavy band
        w = int(1.5 * math.sin(x * 0.18) + 1.5 * math.sin(x * 0.05 + 2))
        for k in range(3):
            y = SURF + w + k
            if 0 <= y < OH:
                px[y, x] = C(P.porcelain[3] if k == 0 else P.sea[4] if k == 1 else P.sea[3])
    return s


def far():
    """Parallax: hazy reef silhouettes and a distant drop-off, low contrast,
    drawn with a slower scroll (the page offsets this layer)."""
    s = Sprite(OW, OH)
    rnd = random.Random(2)
    for layer, (base_y, amp, col) in enumerate(((220, 50, P.sea[2]), (270, 30, P.sea[1]))):
        for x in range(OW):
            top = int(base_y - amp * (0.5 + 0.5 * math.sin(x * 0.006 + layer * 2)) - 14 * math.sin(x * 0.021 + layer))
            for y in range(top, OH):
                s.set(x, y, col)
    for _ in range(40):                                            # far coral heads
        x, y = rnd.randrange(OW), rnd.randint(300, 420)
        s.ellipse(x, y, rnd.randint(4, 9), rnd.randint(3, 6), P.sea[2])
    return s


# ------------------------------------------------------------- terrain

def noise(w, h, seed, scale):
    """Cheap value noise in 0..1 (smooth blobs of size ~scale)."""
    rng = np.random.default_rng(seed)
    gw, gh = w // scale + 3, h // scale + 3
    g = rng.random((gh, gw))
    ys, xs = np.mgrid[0:h, 0:w] / scale
    x0, y0 = xs.astype(int), ys.astype(int)
    fx, fy = xs - x0, ys - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = g[y0, x0] * (1 - fx) + g[y0, x0 + 1] * fx
    b = g[y0 + 1, x0] * (1 - fx) + g[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


ROCK_D = [(0, [P.sage[0], P.sage[1], P.sage[2], P.sage[3]]), (110, [P.slate[1], P.slate[2], P.slate[3], P.slate[4]]),
          (220, [P.sea_grey[0], P.sea_grey[1], P.sea_grey[2], P.sea_grey[3]]), (320, [P.blue[0], P.sea_grey[0], P.sea_grey[1], P.sea_grey[2]])]
SAND_D = [(0, [P.sand[1], P.sand[2], P.sand[3], P.sand[4]]), (130, [P.sand[0], P.sand[1], P.sand[2], P.sand[3]]),
          (240, [P.sea_grey[1], P.sea_grey[2], P.sea_grey[3], P.sea_grey[4]]), (340, [P.sea_grey[0], P.sea_grey[1], P.sea_grey[2], P.sea_grey[3]])]


def shade_map(mask, kind_sand, seed):
    """Colour every masked pixel: shade from rock noise + light from above
    (top edges lit, deeper inside darker), ramp from depth with an ordered
    dither between depth bands."""
    h, w = mask.shape
    n1, n2 = noise(w, h, seed, 9), noise(w, h, seed + 1, 3)
    top = np.zeros_like(mask)
    top[1:] = mask[1:] & ~mask[:-1]
    under = np.zeros((h, w))
    run = np.zeros(w)
    for y in range(h):                                             # how far below the surface of the rock
        run = np.where(mask[y], run + 1, 0)
        under[y] = run
    out = np.zeros((h, w, 4), np.uint8)
    ys, xs = np.mgrid[0:h, 0:w]
    bay = BAYER[ys % 4, xs % 4]
    for which, D in ((False, ROCK_D), (True, SAND_D)):
        sel = mask & (kind_sand == which)
        if not sel.any():
            continue
        if which:
            shade = np.where(under <= 1, 3, np.where(n2 > 0.55, 2, 1))
        else:                                                      # lit crust, mottled band, calm dark core
            shade = np.where(under <= 1, 3,
                    np.where(under <= 4, np.where(n2 > 0.7, 3, 2),
                    np.where(under <= 16, np.where(n1 + 0.3 * n2 > 0.75, 2, 1),
                             np.where(n1 > 0.84, 1, 0))))
        band = np.zeros((h, w), int)
        for i, (y0, _) in enumerate(D[1:], 1):
            span = 90
            t = np.clip((ys - (y0 - span / 2)) / span, 0, 1)
            band = np.where(t > bay, i, band)
        for i, (_, R) in enumerate(D):
            for k in range(4):
                m = sel & (band == i) & (shade == k)
                out[m] = C(R[k])
    return out


def terrain():
    """Rock and sand below FLOOR: sand on gentle slopes, algae-green rock in
    the shallows going slate then blue-grey with depth (dithered, no bands),
    pillow lava boulders, the lava arch, rocks breaking the surface at the
    reef wall."""
    s = Sprite(OW, OH)
    mask = np.zeros((OH, OW), bool)
    sand = np.zeros((OH, OW), bool)
    for x in range(OW):
        fy = max(0, FLOOR[x])
        mask[fy:, x] = True
        slope = abs(FLOOR[min(OW - 1, x + 3)] - FLOOR[max(0, x - 3)]) / 6
        if slope < 1.0:
            sand[fy:fy + 5 + (x * 7) % 3, x] = True
    yy, xx = np.mgrid[0:OH, 0:OW]
    for cx, cy, r in ((440, 262, 12), (566, 264, 10), (692, 232, 14), (842, 236, 16), (870, 214, 12),
                      (214, 182, 9), (300, 184, 11), (380, 214, 8)):
        b = ((xx - cx) / r) ** 2 + ((yy - cy) / (r * 0.7)) ** 2 <= 1
        mask |= b
        sand &= ~b
    arch = lava_arch_mask(760, 236)
    mask |= arch
    for y in range(110, 262):                                      # a coral pinnacle rising from the valley
        hw = int(6 + (y - 110) * 0.14 + 2 * math.sin(y * 0.3))
        mask[y, 630 - hw:630 + hw] = True
    for cx, top, r in ((968, 4, 20), (1010, 0, 18), (924, 14, 10)):   # rocks breaking the surface
        for k in range(5):
            ex, ey, er = cx + (k - 2) * r * 0.35, top + 6 + (k % 2) * 4 + abs(k - 2) * 5, r * (0.55 - abs(k - 2) * 0.08)
            mask |= ((xx - ex) / er) ** 2 + ((yy - ey) / (er * 0.9)) ** 2 <= 1
        mask[top + 10:SURF + 40, int(cx - r * 0.7):int(cx + r * 0.7)] = True
    s.px[:] = shade_map(mask, sand, 4)
    rnd = random.Random(4)
    for _ in range(600):                                           # pebbles and shell bits on the sand
        x = rnd.randrange(OW)
        y = FLOOR[x] + rnd.randint(0, 3)
        if 0 <= y < OH and sand[y, x]:
            s.set(x, y, rnd.choice((P.porcelain[3], P.sand[0], P.coral[3] if y < 300 else P.sea_grey[4])))
    for cx in (968, 1010, 924):
        s.hline(cx - 14, cx + 14, SURF, P.porcelain[3]).hline(cx - 10, cx + 10, SURF + 1, P.sea[4])
    return s


def lava_arch_mask(cx, base):
    """A natural lava arch: an elliptical ring cut off below by the floor,
    lumpy edges, wide feet."""
    yy, xx = np.mgrid[0:OH, 0:OW]
    n = noise(OW, OH, 21, 5)
    outer = ((xx - cx) / 50) ** 2 + ((yy - base) / 64) ** 2 <= 1 + 0.25 * (n - 0.5)
    inner = ((xx - cx) / 30) ** 2 + ((yy - base) / 44) ** 2 <= 1 + 0.2 * (n - 0.5)
    return outer & ~inner & (yy <= base + 6)


# ------------------------------------------------------------- reef life (static decor)

CORALS = {
    "branch": P.coral, "brain": P.mustard, "table": P.teal, "fan": P.blossom,
    "finger": P.lilac, "plate": P.hydrangea,
}


def coral(s, kind, x, base, size=1.0, seed=0):
    rnd = random.Random(seed or x * 7 + base)
    R = CORALS[kind]
    if kind == "branch":                                           # antler coral
        def grow(x0, y0, ang, L, d):
            x1, y1 = x0 + math.cos(ang) * L, y0 - math.sin(ang) * L
            s.line(int(x0), int(y0), int(x1), int(y1), R[2])
            s.line(int(x0) - 1, int(y0), int(x1) - 1, int(y1), R[3])
            if d:
                for da in (-0.5, 0.45):
                    grow(x1, y1, ang + da + rnd.uniform(-0.1, 0.1), L * 0.7, d - 1)
            else:
                s.set(int(x1), int(y1), R[4])
        for a in (1.2, 1.57, 1.95):
            grow(x, base, a, 7 * size, 3)
    elif kind == "brain":
        r = 8 * size
        s.ellipse(x, base - r * 0.6, r, r * 0.7, R[2])
        s.ellipse(x - r * 0.3, base - r * 0.8, r * 0.55, r * 0.35, R[3])
        for k in range(-int(r), int(r), 3):                         # meandering grooves
            for t in range(int(r * 0.8)):
                yy = int(base - r * 0.6 + t - r * 0.4 + 1.5 * math.sin((k + t) * 0.8))
                if (k + t) % 4 == 0:
                    s.set(int(x + k * 0.9), yy, R[1])
        s.hline(int(x - r), int(x + r), base, R[1])
    elif kind == "table":
        w = int(14 * size)
        s.vline(x, base - 8, base, R[1]).vline(x + 1, base - 8, base, R[2])
        for k in range(3):
            s.hline(x - w + k * 2, x + w - k * 2, base - 9 - k, R[2 + (k == 0)])
        s.hline(x - w, x + w, base - 8, R[1])
        for xx in range(x - w + 1, x + w, 3):
            s.set(xx, base - 11, R[4])
    elif kind == "fan":                                            # sea fan
        h = int(16 * size)
        for k in range(-h, h + 1, 2):
            s.line(x, base, x + k, base - h + abs(k) // 2, R[2])
        for y in range(base - h, base - 2, 3):
            hw = int((h - (base - y) * 0.5))
            for xx in range(x - hw, x + hw, 2):
                s.set(xx, y, R[3])
        s.vline(x, base - 4, base, R[1])
    elif kind == "finger":
        for k in range(-3, 4):
            h = int((9 - abs(k) * 1.5) * size)
            s.rect(x + k * 2, base - h, 2, h, R[2]).set(x + k * 2, base - h, R[4]).vline(x + k * 2 + 1, base - h + 1, base - 1, R[1])
    elif kind == "plate":
        for k in range(3):
            w = int((10 - k * 2) * size)
            s.ellipse(x + k, base - 3 - k * 4, w, 2, R[2]).hline(x + k - w + 1, x + k + w - 1, base - 4 - k * 4, R[3])


def sponge(s, x, base, R=P.lilac, n=3, seed=0):
    """Tube sponges: a cluster of upright tubes with dark open tops."""
    rnd = random.Random(seed or x)
    for k in range(n):
        h = rnd.randint(6, 12)
        bx = x + k * 3 - n
        s.rect(bx, base - h, 3, h, R[2]).vline(bx, base - h, base - 1, R[3]).vline(bx + 2, base - h, base - 1, R[1])
        s.hline(bx, bx + 2, base - h, R[1]).set(bx + 1, base - h, R[0])


def bommie(s, x, base, size=1.0, seed=0):
    """A coral head (bommie): a rock knoll crowded with corals, sponges and
    an anemone, the most colourful thing in the reef."""
    rnd = random.Random(seed or x)
    r = int(22 * size)
    hgt = int(16 * size)
    d = 0 if base < 300 else 1
    R = [P.sage, P.slate][d]
    for y in range(base - hgt, base + 1):
        t = (y - (base - hgt)) / max(1, hgt)
        hw = int(r * math.sqrt(max(0, t)) * (0.85 + 0.15 * math.sin(y * 0.7)))
        s.hline(x - hw, x + hw, y, R[1])
        s.hline(x - hw, x - hw + max(1, hw // 3), y, R[2])
        s.set(x - hw, y, R[3])
    spots = sorted([rnd.uniform(-0.85, 0.85) for _ in range(int(9 * size) + 3)])
    kinds = ["brain", "branch", "table", "fan", "finger", "plate"]
    for u in spots:                                                 # corals on the knoll's surface
        px = int(x + u * r)
        t = 1 - abs(u)
        py = int(base - hgt * math.sqrt(t) * 0.95) + 2
        k = rnd.choice(kinds)
        coral(s, k, px, py, rnd.uniform(0.55, 0.95) * size, seed=px * 3 + py)
    sponge(s, x + int(r * 0.5), base - 2, rnd.choice((P.lilac, P.coral, P.mustard)), 3, seed=x + 1)
    anemone(s, x - int(r * 0.45), base - 2, rnd.choice((P.blossom, P.coral)))


def limu(s, x, base, R=P.coral):
    """Red limu (seaweed) tufts."""
    for k in range(-3, 4):
        for j in range(5 - abs(k)):
            s.set(x + k + (j % 2), base - j, R[1 + (j > 1)])


def seagrass(s, x, base, n=6, h=14, R=P.green, seed=0):
    rnd = random.Random(seed or x)
    for k in range(n):
        bx = x + k * 2 - n
        hh = rnd.randint(h // 2, h)
        for j in range(hh):
            sx = bx + int(1.5 * math.sin(j * 0.4 + k))
            s.set(sx, base - j, R[2 if j < hh * 0.7 else 3])


def anemone(s, x, base, R=P.blossom):
    s.ellipse(x, base - 2, 5, 2.5, R[1])
    for k in range(-5, 6, 2):
        s.line(x, base - 3, x + k, base - 9 + abs(k) // 2, R[3])
        s.set(x + k, base - 9 + abs(k) // 2, R[4])


def urchin(s, x, base):
    s.ellipse(x, base - 2, 3, 2.5, P.slate[0])
    for a in range(0, 360, 30):
        r = math.radians(a)
        s.set(int(x + 5 * math.cos(r)), int(base - 2 - 4 * math.sin(r)), P.slate[1])


def starfish(s, x, y, R=P.coral):
    s.set(x, y, R[3])
    for a in range(5):
        r = math.radians(a * 72 - 90)
        for k in range(1, 4):
            s.set(int(x + math.cos(r) * k), int(y + math.sin(r) * k * 0.8), R[2 if k > 1 else 3])


def clam(s, x, base):
    """A giant clam with a purple-blue mantle (a hotspot: a pearl inside)."""
    s.ellipse(x, base - 4, 9, 4, P.porcelain[2]).ellipse(x, base - 4, 7, 2, P.lilac[2])
    for k in range(-8, 9, 3):
        s.vline(x + k, base - 7 + abs(k) // 4, base - 1, P.porcelain[1])
    s.hline(x - 6, x + 6, base - 4, P.hydrangea[3]).set(x, base - 5, P.porcelain[3])


def shipwreck(s, x, base):
    """A sunken wooden sampan / small trader on its side in the sand: broken
    hull planks, a fallen mast with a torn sail, a cargo hold with crates and a
    chest (hotspot), limu and corals growing on it."""
    Wd = [P.walnut[0], P.walnut[1], P.walnut[2], P.walnut[3]]
    L = 140
    for i in range(L):
        t = i / L
        top = int(base - 30 * math.sin(math.pi * min(1, t * 1.1)) - 4)
        if 0.38 < t < 0.5:                                         # the broken middle
            top += 14
        for y in range(top, base):
            c = Wd[1] if (y - top) % 4 else Wd[0]
            if (i // 9) % 2 and (y - top) % 4 == 1:
                c = Wd[2]
            s.set(x + i, y, c)
        s.set(x + i, top, Wd[3])
    for k in range(5):                                             # ribs showing where it broke
        rx = x + 56 + k * 4
        s.vline(rx, base - 30, base - 12, Wd[2])
    mx = x + 92
    s.line(mx, base - 30, mx + 70, base - 70, Wd[2]).line(mx + 1, base - 30, mx + 71, base - 70, Wd[1])
    for k in range(18):                                            # torn sail drifting
        s.line(mx + 20 + k * 2, base - 42 - k, mx + 30 + k * 2, base - 34 - k + (k % 3), P.oat[2] if k % 3 else P.oat[1])
    for cx in (x + 30, x + 42):                                    # crates
        s.rect(cx, base - 12, 10, 10, P.oak[1]).hline(cx, cx + 9, base - 12, P.oak[2]).line(cx, base - 3, cx + 9, base - 12, P.oak[0])
    treasure(s, x + 66, base - 2)
    for k in range(6):
        seagrass(s, x + 10 + k * 22, base - 4 - (k % 2) * 8, 3, 10, P.green, seed=k + 9)
    coral(s, "plate", x + 120, base - 18, 0.8)
    coral(s, "fan", x + 16, base - 22, 0.7)


def treasure(s, x, base):
    s.rect(x, base - 8, 14, 8, P.walnut[1]).rect(x, base - 11, 14, 3, P.walnut[2]).hline(x, x + 13, base - 11, P.walnut[3])
    for xx in (x, x + 13):
        s.vline(xx, base - 11, base - 1, P.mustard[2])
    s.hline(x, x + 13, base - 8, P.mustard[2]).rect(x + 6, base - 9, 2, 3, P.mustard[4])
    for k in range(5):                                             # a glint of coins
        s.set(x + 2 + k * 2, base - 12 - (k % 2), P.mustard[4])


def tiki(s, x, base):
    """A sunken carved ki'i statue, mossy, leaning a little."""
    St = [P.sea_grey[0], P.sea_grey[1], P.sea_grey[2], P.sea_grey[3]]
    s.rect(x, base - 30, 14, 30, St[1]).vline(x, base - 30, base - 1, St[2]).vline(x + 13, base - 30, base - 1, St[0])
    s.rect(x - 2, base - 33, 18, 4, St[2])
    s.rect(x + 2, base - 26, 4, 3, St[0]).rect(x + 8, base - 26, 4, 3, St[0])       # eyes
    s.rect(x + 3, base - 18, 8, 5, St[0]).hline(x + 4, x + 9, base - 16, St[3])        # big mouth
    s.rect(x + 1, base - 10, 12, 2, St[2])
    for k in range(6):
        s.set(x + k * 2, base - 31 + (k % 3), P.green[2])
    s.set(x + 7, base - 22, P.green[1])


def anchor(s, x, base):
    s.vline(x, base - 22, base - 2, P.steel[1]).hline(x - 4, x + 4, base - 19, P.steel[1])
    s.ellipse(x, base - 24, 2, 2, P.steel[1])
    for k in range(6):
        s.set(x - k, base - 2 - k // 2, P.steel[1]).set(x + k, base - 2 - k // 2, P.steel[1])
    s.set(x - 6, base - 6, P.steel[2]).set(x + 6, base - 6, P.steel[2])


def tall_weed(s, x, base, h, R=P.teal, seed=0):
    """Tall swaying seaweed ribbons for the wreck valley forest."""
    rnd = random.Random(seed or x)
    for k in range(3):
        bx = x + k * 3
        hh = int(h * rnd.uniform(0.7, 1.0))
        for j in range(hh):
            sx = bx + int(2.5 * math.sin(j * 0.15 + k * 2))
            s.set(sx, base - j, R[2 if (j // 4) % 2 else 3])
            if j % 6 == 3:
                s.set(sx + 1, base - j, R[4]).set(sx + 2, base - j + 1, R[3])


def decor():
    s = Sprite(OW, OH)
    rnd = random.Random(12)
    kinds = list(CORALS)
    # 浅滩: dense seagrass on the beach slope, starfish, limu, small coral heads
    for x in range(36, 180, 4):
        seagrass(s, x, FLOOR[x] + 1, rnd.randint(3, 6), rnd.randint(8, 18), seed=x)
    for x in range(30, 176, 13):
        starfish(s, x, FLOOR[x] - 1, rnd.choice((P.coral, P.mustard, P.blossom)))
        limu(s, x + 6, FLOOR[x + 6] + 1, rnd.choice((P.coral, P.clay)))
    for x in (80, 140):
        bommie(s, x, FLOOR[x] + 2, 0.7, seed=x)
    # 珊瑚花园 on the plateau: big coral heads, corals packed between them
    for x in range(176, 362, 5):
        coral(s, kinds[(x * 7) % len(kinds)], x + rnd.randint(-2, 2), FLOOR[x] + 1, rnd.uniform(0.7, 1.2), seed=x)
    for x, sz in ((196, 1.2), (250, 1.6), (306, 1.3), (350, 1.0)):
        bommie(s, x, FLOOR[x] + 2, sz, seed=x)
    for x in range(180, 360, 17):
        sponge(s, x + 8, FLOOR[x + 8] + 1, rnd.choice((P.lilac, P.coral, P.mustard)), 2, seed=x)
        urchin(s, x + 3, FLOOR[x + 3] + 1)
    clam(s, 280, FLOOR[280] + 1)
    for y in range(200, 255, 9):                                   # the slope down to the valley
        x = next((xx for xx in range(350, 420) if FLOOR[xx] >= y), 400)
        coral(s, "fan", x - 2, y + 2, 0.7, seed=y)
        sponge(s, x - 5, y + 4, P.mustard, 2, seed=y + 3)
    # 沉船谷: a seaweed forest round the wreck
    for x in range(412, 600, 9):
        tall_weed(s, x, FLOOR[x] + 1, rnd.randint(30, 70), rnd.choice((P.teal, P.green, P.sage)), seed=x)
    shipwreck(s, 446, FLOOR[500] + 2)
    anchor(s, 590, FLOOR[590] + 1)
    for x in range(420, 600, 11):
        seagrass(s, x, FLOOR[x] + 1, 3, 10, P.sage, seed=x)
    # the pinnacle: corals stepping up both faces
    for y in range(116, 262, 7):
        hw = int(6 + (y - 110) * 0.14)
        coral(s, kinds[(y // 7) % len(kinds)], 630 - hw - 1, y + 3, 0.6, seed=y)
        coral(s, kinds[(y // 7 + 3) % len(kinds)], 630 + hw + 1, y + 3, 0.6, seed=y + 1)
    bommie(s, 630, 112, 0.6, seed=630)
    # 熔岩拱门: tiki, coral heads on the pillow lava, fans on the arch
    tiki(s, 800, FLOOR[800] + 2)
    for x in range(652, 900, 6):
        if 720 < x < 800:
            continue
        coral(s, kinds[(x * 5) % len(kinds)], x, FLOOR[x] + 1, rnd.uniform(0.7, 1.1), seed=x)
    for x, sz in ((680, 1.1), (850, 1.3)):
        bommie(s, x, FLOOR[x] + 2, sz, seed=x)
    for x in (735, 760, 785):
        coral(s, "fan", x, 176 + abs(x - 760) // 3, 0.6, seed=x)
    # 礁墙: corals and sponges stepping up the wall to the surface
    for y in range(36, 230, 7):
        x = next((xx for xx in range(850, OW) if FLOOR[xx] <= y), OW - 1)
        coral(s, kinds[(y // 7) % len(kinds)], x - 1, y + 2, 0.75, seed=y)
        if y % 21 == 1:
            sponge(s, x + 3, y + 3, P.coral, 2, seed=y)
    return s


def front():
    """Foreground fronds and coral silhouettes the diver passes behind."""
    s = Sprite(OW, OH)
    for x in range(20, OW, 110):
        y = FLOOR[x] + 2
        seagrass(s, x, y + 6, 8, 28, P.teal, seed=x + 1)
    return s


def rays():
    """God rays from the surface: a few long slanted shafts and caustic
    ripples over the shallow floor (the page draws them at low alpha and
    slides them slowly)."""
    s = Sprite(OW, OH)
    for x0, w in ((60, 14), (300, 10), (520, 16), (800, 12)):
        for y in range(SURF, 220):
            a = int(x0 + (y - SURF) * 0.35)
            s.hline(a, a + w - int((y - SURF) / 30), y, P.porcelain[3])
    for x in range(0, 420):                                        # caustics where the floor is shallow
        fy = FLOOR[x]
        if fy < 220:
            for k in range(0, 10, 3):
                if (x * 7 + k * 13) % 9 < 2:
                    s.set(x, fy - 1 - k // 3, P.porcelain[3])
    return s


# ------------------------------------------------------------- creatures (sprites, 2 frames unless noted)

def fish(kind, frame):
    """Small reef fish facing right."""
    if kind == "tang":                                             # yellow tang
        s = Sprite(12, 10)
        s.ellipse(5, 5, 4.5, 4, P.mustard[3]).set(3, 2, P.mustard[4]).set(8, 4, P.walnut[0])
        s.rect(9, 5, 2, 1, P.porcelain[3])
        t = 0 if frame == 0 else 1
        s.vline(0, 3 + t, 7 - t, P.mustard[2]).vline(1, 4, 6, P.mustard[2])
        return s
    if kind == "humu":                                             # humuhumunukunukuāpuaʻa (reef triggerfish)
        s = Sprite(16, 10)
        s.ellipse(8, 5, 6.5, 4, P.oat[2])
        s.line(4, 3, 9, 7, P.slate[1]).line(5, 3, 10, 7, P.mustard[3]).hline(9, 13, 5, P.slate[1])
        s.set(11, 4, P.walnut[0]).set(13, 5, P.coral[3]).set(10, 2, P.hydrangea[3]).set(11, 3, P.hydrangea[3])
        t = frame
        s.vline(1, 3 + t, 7 - t, P.slate[1]).set(2, 5, P.slate[1])
        return s
    if kind == "idol":                                             # Moorish idol
        s = Sprite(12, 14)
        s.ellipse(6, 8, 4, 4.5, P.porcelain[3])
        s.vline(5, 4, 12, P.slate[0]).vline(8, 5, 11, P.mustard[3]).vline(9, 5, 11, P.slate[0])
        s.line(6, 4, 2, 0, P.porcelain[3])
        s.set(9, 7, P.walnut[0]).set(10, 8, P.mustard[3])
        s.vline(1, 7, 9 - frame, P.slate[0])
        return s
    if kind == "parrot":                                           # parrotfish
        s = Sprite(18, 10)
        s.ellipse(9, 5, 7, 4, P.teal[3]).ellipse(7, 4, 4, 2, P.mint[3])
        for k in range(4, 14, 3):
            s.set(k, 6, P.blossom[3])
        s.set(14, 4, P.walnut[0]).rect(15, 5, 2, 2, P.porcelain[3])
        s.vline(1, 2 + frame, 8 - frame, P.blossom[2]).vline(2, 3, 7, P.teal[2])
        return s
    if kind == "butterfly":
        s = Sprite(11, 10)
        s.ellipse(5, 5, 4, 4, P.mustard[4]).vline(7, 2, 8, P.slate[0]).set(4, 4, P.slate[1])
        s.vline(0, 3 + frame, 7 - frame, P.mustard[3])
        return s
    s = Sprite(7, 3)                                               # silver school fish
    s.hline(1, 5, 1, P.porcelain[3]).set(5, 0, P.porcelain[2]).set(6, 1, P.slate[1]).set(0, frame * 2, P.porcelain[2])
    return s


def turtle(frame):
    """Honu, a green sea turtle, swimming right; 2 strokes."""
    s = Sprite(34, 22)
    sh = [P.green[0], P.green[1], P.walnut[2], P.oak[2], P.oak[3]]
    s.ellipse(15, 11, 12, 7, sh[2])
    for cx, cy in ((10, 9), (16, 8), (22, 10), (13, 13), (19, 13)):  # scutes
        s.ellipse(cx, cy, 3, 2, sh[3]).set(cx - 1, cy - 1, sh[4])
    s.ellipse(15, 15, 11, 2, P.oat[2])
    s.ellipse(29, 11, 4, 3, P.sage[2]).set(30, 10, P.walnut[0]).set(28, 9, P.sage[3])
    up = frame == 0
    s.line(19, 9, 26, 2 if up else 18, P.sage[2]).line(20, 10, 27, 3 if up else 19, P.sage[1])
    s.line(8, 14, 3, 19 if up else 16, P.sage[2])
    s.set(2, 11, P.sage[2]).set(1, 12, P.sage[1])
    return s


def manta(frame):
    """A manta ray gliding; frame 1 wingtips down."""
    s = Sprite(50, 22)
    tip = 2 if frame == 0 else 8
    for x in range(50):
        t = abs(x - 25) / 25
        top = int(10 - (1 - t) * 6 + (tip if t > 0.7 else 0) * (t - 0.7) / 0.3)
        bot = int(12 + (1 - t) * 4 - (2 if t > 0.8 else 0))
        s.vline(x, top, bot, P.slate[1])
        s.set(x, top, P.slate[3])
    s.vline(25, 14, 21, P.slate[0])
    s.set(22, 10, P.porcelain[3]).set(28, 10, P.porcelain[3])
    s.set(23, 8, P.slate[0]).set(27, 8, P.slate[0])
    return s


def octopus(frame):
    """Heʻe: a day octopus, tentacles curling; frame 1 changes colour a bit."""
    s = Sprite(18, 16)
    R = P.coral if frame == 0 else P.clay
    s.ellipse(9, 5, 5, 4.5, R[2]).ellipse(7, 3, 2, 1.5, R[3])
    s.set(7, 6, P.porcelain[3]).set(11, 6, P.porcelain[3]).set(7, 7, P.walnut[0]).set(11, 7, P.walnut[0])
    for k in range(6):
        x0 = 4 + k * 2
        for j in range(7):
            s.set(x0 + int(2 * math.sin(j * 0.7 + k + frame)), 9 + j, R[2 if j < 4 else 1])
    return s


def jelly(frame):
    s = Sprite(12, 20)
    s.ellipse(6, 4, 5, 3.5 if frame == 0 else 3, P.lilac[3])
    s.hline(1, 11, 6 if frame == 0 else 5, P.lilac[2])
    for k in range(4):
        x = 2 + k * 3
        for j in range(10):
            s.set(x + int(math.sin(j * 0.6 + k + frame * 2)), 8 + j, P.lilac[4] if j % 2 else P.lilac[3])
    return s


def eel(frame):
    """A moray peeking out of a crevice (head and neck), mouth opening."""
    s = Sprite(16, 12)
    s.rect(0, 4, 9, 6, P.sage[1])
    for k in range(0, 9, 2):
        s.set(k, 6, P.mustard[2])
    s.ellipse(11, 6, 4, 3, P.sage[2]).set(12, 4, P.mustard[4]).set(12, 5, P.walnut[0])
    s.hline(10, 15, 7 + frame, P.walnut[0])
    return s


def crab(frame):
    s = Sprite(12, 9)
    s.ellipse(6, 4, 4, 3, P.porcelain[2]).ellipse(5, 3, 2.5, 1.8, P.porcelain[3])   # the shell it carries
    s.set(9, 6, P.coral[2]).set(10, 5, P.coral[3]).set(10, 7 - frame, P.coral[2])
    for k in (7, 9):
        s.set(k, 8, P.coral[1])
    return s


def seal(frame):
    """A Hawaiian monk seal resting or swimming."""
    s = Sprite(30, 12)
    s.ellipse(14, 6, 12, 4, P.slate[2]).ellipse(12, 5, 9, 2, P.slate[3])
    s.ellipse(26, 5, 4, 3.5, P.slate[2]).set(27, 4, P.walnut[0]).set(29, 6, P.walnut[0])
    s.set(28, 6, P.porcelain[3])
    s.line(1, 4 + frame, 3, 6, P.slate[1]).line(1, 8 - frame, 3, 6, P.slate[1])
    s.set(16, 10, P.slate[1]).set(17, 11, P.slate[1])
    return s


def diver(frame, suit=P.slate, skin=P.skin, fin=P.mustard):
    """An NPC scuba diver swimming right: fins kick, a tank on the back,
    mask, arms forward; a bubble trail is drawn by the page."""
    s = Sprite(32, 12)
    s.rect(9, 4, 14, 5, suit[1]).hline(9, 22, 4, suit[2])          # body
    s.rect(12, 2, 9, 3, P.steel[3]).hline(12, 20, 2, P.steel[4])    # tank
    s.ellipse(25, 6, 3, 2.5, skin[2]).hline(25, 28, 5, P.slate[0]).set(27, 5, P.glass[3])   # head + mask
    s.line(23, 7, 30, 8, suit[2])                                  # arm forward
    k = 2 if frame else -1                                         # legs and fins kick
    s.line(9, 5, 3, 5 + k, suit[1]).line(9, 7, 3, 8 - k, suit[1])
    s.rect(0, 4 + k, 4, 2, fin[2]).rect(0, 7 - k, 4, 2, fin[3])
    return s


def bubble(frame):
    s = Sprite(5, 5)
    r = 1.6 if frame == 0 else 2.2
    s.ellipse(2, 2, r, r, P.porcelain[2]).set(1, 1, P.porcelain[3])
    m = s.px[..., 3] > 0
    s.px[m] = rgba(P.porcelain[2])
    s.px[1:4, 1:4] = 0
    s.set(1, 1, P.porcelain[3])
    return s


CREATURES = {
    "tang": lambda f: fish("tang", f), "humu": lambda f: fish("humu", f), "idol": lambda f: fish("idol", f),
    "parrot": lambda f: fish("parrot", f), "butterflyfish": lambda f: fish("butterfly", f), "school": lambda f: fish("school", f),
    "turtle": turtle, "manta": manta, "octopus": octopus, "jelly": jelly, "eel": eel, "crab": crab, "seal": seal,
    "bubble": bubble, "diver": diver,
}

# Interactive spots (map px): what the page can offer when the diver swims close.
HOTSPOTS = [
    {"id": "turtle_rock", "x": 120, "y": FLOOR[120] - 8, "name": "海龟清洁站", "what": "honu come to rest; swim slowly beside one"},
    {"id": "clam", "x": 280, "y": FLOOR[280] - 4, "name": "巨蚌", "what": "opens now and then: a pearl"},
    {"id": "coral_photo", "x": 250, "y": FLOOR[250] - 24, "name": "珊瑚花园", "what": "photo spot; fish scatter and return"},
    {"id": "octopus_den", "x": 352, "y": FLOOR[352] - 6, "name": "章鱼洞", "what": "an octopus hides, peeks, changes colour"},
    {"id": "wreck_chest", "x": 518, "y": FLOOR[500] - 4, "name": "沉船宝箱", "what": "a chest in the hold: coins, a message in a bottle"},
    {"id": "kelp_forest", "x": 470, "y": 220, "name": "海藻林", "what": "swim through the swaying weed; small fish hide in it"},
    {"id": "pinnacle", "x": 630, "y": 104, "name": "珊瑚尖塔", "what": "circle the tower top: a school of fish wheels round"},
    {"id": "arch", "x": 760, "y": 210, "name": "熔岩拱门", "what": "swim through it (a little achievement)"},
    {"id": "tiki", "x": 806, "y": FLOOR[800] - 18, "name": "沉没的提基像", "what": "make a wish"},
    {"id": "eel_crevice", "x": 890, "y": 170, "name": "海鳗石缝", "what": "a moray peeks out; it is shy"},
    {"id": "seal_rock", "x": 960, "y": SURF + 6, "name": "海豹礁", "what": "a monk seal naps on the rock by the surface"},
]
SPAWNS = {
    "tang": (170, 120, 360, 180), "humu": (180, 140, 360, 185), "idol": (190, 130, 350, 180),
    "parrot": (170, 120, 400, 190), "butterflyfish": (650, 170, 900, 225), "school": (560, 60, 700, 120),
    "turtle": (40, 40, 420, 150), "manta": (400, 140, 620, 230), "octopus": (346, 182, 360, 196),
    "jelly": (420, 30, 900, 110), "eel": (884, 160, 900, 180), "crab": (40, 30, 170, 160),
    "seal": (930, 10, 1020, 40), "diver": (60, 30, 900, 200),
}


# ------------------------------------------------------------- previews

def compose():
    s = water()
    for layer in (far(), terrain(), decor()):
        s.blit(layer, 0, 0)
    r = rays()
    m = r.px[..., 3] > 0
    s.px[m, :3] = (s.px[m, :3] * 0.86 + r.px[m, :3] * 0.14).astype(np.uint8)
    rnd = random.Random(3)
    for kind, (x0, y0, x1, y1) in SPAWNS.items():
        if kind in ("bubble",):
            continue
        n = {"school": 16, "tang": 8, "idol": 5, "butterflyfish": 6, "humu": 3, "parrot": 3, "diver": 4, "jelly": 3, "turtle": 2}.get(kind, 1)
        for k in range(n):
            spr = CREATURES[kind](k % 2) if kind != "diver" else diver(k % 2, (P.slate, P.hydrangea, P.coral, P.teal)[k % 4], (P.skin, P.skin_tan, P.skin_deep)[k % 3])
            for _ in range(20):                                    # only in open water (or on the floor for crabs)
                px_, py_ = rnd.randint(x0, max(x0, x1 - spr.w)), rnd.randint(y0, max(y0, y1 - spr.h))
                if kind == "crab":
                    py_ = FLOOR[px_ + spr.w // 2] - spr.h + 1
                if py_ + spr.h - 1 < FLOOR[min(OW - 1, px_ + spr.w // 2)] or kind == "crab":
                    s.blit(spr, px_, py_)
                    break
    s.blit(front(), 0, 0)
    return s


def creature_sheet():
    keys = [k for k in CREATURES]
    s = Sprite(260, 120)
    s.rect(0, 0, 260, 120, P.sea[2])
    x, y, rowh = 4, 4, 0
    for k in keys:
        for f in (0, 1):
            spr = CREATURES[k](f)
            if x + spr.w > 256:
                x, y, rowh = 4, y + rowh + 4, 0
            s.blit(spr, x, y)
            x += spr.w + 3
            rowh = max(rowh, spr.h)
    return s


def build():
    out = {"sea_water": water(), "sea_far": far(), "sea_terrain": terrain(), "sea_decor": decor(),
           "sea_front": front(), "sea_rays": rays()}
    pv = compose()
    out["sea_preview"] = pv
    for k, fn in CREATURES.items():
        for f in (0, 1):
            out[f"sea_{k}_{f}"] = fn(f)
    out["sea_creatures"] = creature_sheet()
    return out
