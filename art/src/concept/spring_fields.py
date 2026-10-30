"""春日花溪: a spring-only outing, four connected 342x118 screens in the park's
style (same sky, far tree line, gravel lane at y=94..106, flower border, trees
and bushes from front_yard). Light from the top left.

    brook   溪桥樱堤  a brook winds down from the hills under a stone arch
                      bridge in the lane; cherry trees on both banks
    rape    油菜花田  terraced rapeseed rows run to the hills, white-walled
                      farmhouses, beehives beside the lane
    tulip   风车花圃  tulip stripes in four colours, a windmill behind
    arbor   紫藤花廊  a wooden pergola heavy with wisteria, a bench under it

Art only for now (user decides when it goes into the game).
    build() -> spring_<zone> (background), spring_<zone>_tree_<0|1>,
    spring_<zone>_preview, spring_panorama.
"""
from __future__ import annotations

import math
import random

from pixelkit import P, Sprite

import park as PK
import front_yard as FY
from _park_facilities import poly

W, H = PK.W, PK.H
HZ = PK.HORIZON
PATH = PK.PATH
SEASON = "spring"
PREVIEW_SCALE = 4
G = P.leaf_spring
ST = P.pave

ZONES = [
    {"id": "brook", "name": "溪桥樱堤",
     "trees": [("cherry", 26, 34, 92, 26, 24), ("cherry", 96, 44, 66, 15, 13), ("cherry", 252, 42, 68, 16, 14), ("linden", 140, 47, 62, 10, 9), ("maple", 290, 46, 61, 9, 8),
               ("cherry", 318, 33, 93, 26, 25)]},
    {"id": "rape", "name": "油菜花田",
     "trees": [("linden", 22, 36, 92, 22, 22), ("cherry", 300, 46, 64, 12, 11)]},
    {"id": "tulip", "name": "风车花圃",
     "trees": [("cherry", 330, 34, 93, 22, 22), ("linden", 40, 47, 62, 11, 10)]},
    {"id": "arbor", "name": "紫藤花廊",
     "trees": [("linden", 20, 34, 93, 22, 23), ("cherry", 324, 36, 92, 22, 22)]},
]


# ------------------------------------------------------------- far away

def hills(s, zone):
    """Two hazy ridges behind the tree line, the near one greener."""
    off = {"brook": 0, "rape": 90, "tulip": 170, "arbor": 260}[zone["id"]]
    for k, (base, amp, R) in enumerate(((HZ - 10, 9, P.sky_soft), (HZ - 5, 7, P.mint))):
        for x in range(W):
            u = (x + off * (k + 1)) / W * math.tau
            top = int(base - amp * (0.55 + 0.45 * math.sin(u * 1.3 + k)) - 3 * math.sin(u * 3.1 + 2 * k))
            s.vline(x, top, HZ - 1, R[2])
            s.set(x, top, R[3])
            if k == 0 and x % 2 == 0:
                s.set(x, top + 1, R[3])
        if k == 1:                                         # a few pink and white blooming crowns on the near ridge
            rnd = random.Random(zone["id"] + "ridge")
            for _ in range(14):
                x = rnd.randrange(W)
                c = rnd.choice((P.blossom[3], P.linen[3], P.leaf_spring[3]))
                y = HZ - 4 - rnd.randint(0, 4)
                s.ellipse(x, y, 2.5, 1.6, c).set(x - 1, y - 1, P.blossom[4] if c == P.blossom[3] else c)


def clouds(s, zone):
    rnd = random.Random(zone["id"] + "cl")
    for _ in range(2):
        x, y = rnd.randint(30, W - 60), rnd.randint(8, 22)
        for dx, r in ((0, 6), (8, 8), (18, 6), (25, 4)):
            s.ellipse(x + dx, y, r, r * 0.55, P.linen[3])
        s.hline(x - 5, x + 28, y + 3, P.sky_day[3])


def lawn(s, zone):
    """Soft rolling lawn (no mowing stripes: this is country, not a park)."""
    s.rect(0, HZ, W, PATH[0] - HZ, G[2])
    for cx, cy, rx, ry in ((60, 86, 90, 18), (250, 88, 110, 16)):
        s.ellipse(cx + 4, cy + 3, rx, ry, G[2])
        s.ellipse(cx - 6, cy - 4, rx - 8, ry - 5, G[3])
    s.hline(0, W - 1, HZ, G[1])
    rnd = random.Random(zone["id"] + "lawn")
    for _ in range(420):
        x, y = rnd.randrange(W), rnd.randint(HZ + 1, PATH[0] - 1)
        s.set(x, y, G[rnd.choice((1, 2, 4))])
    for _ in range(70):                                    # daisies, dandelions, violets
        x, y = rnd.randrange(W), rnd.randint(HZ + 3, PATH[0] - 2)
        s.set(x, y, rnd.choice((P.linen[3], P.linen[3], P.mustard[4], P.lilac[3])))


def petals(s, y0, y1, n, seed, x0=0, x1=W):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.randint(x0, x1 - 2), rnd.randint(y0, y1)
        s.set(x, y, rnd.choice((P.blossom[3], P.blossom[4], P.blossom[3])))
        if rnd.random() < 0.3:
            s.set(x + 1, y, P.blossom[2])


# ------------------------------------------------------------- brook

BROOK = [(212, HZ), (204, 66), (186, 74), (170, 82), (166, 90), (168, 96), (170, 118)]   # centre line, far to near


def brook_half(y):
    return 1 + (y - HZ) * 0.42


def brook_center(y):
    for (x0, y0), (x1, y1) in zip(BROOK, BROOK[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / max(1, y1 - y0)
            t = t * t * (3 - 2 * t)
            return x0 + (x1 - x0) * t
    return BROOK[-1][0]


def brook(s):
    rnd = random.Random(31)
    Wt = P.sea
    for y in range(HZ, H):
        cx, hw = brook_center(y), brook_half(y)
        a, b = round(cx - hw), round(cx + hw)
        s.hline(a - 2, b + 2, y, G[1])                     # damp bank edge
        s.hline(a - 1, a, y, ST[2]).hline(b, b + 1, y, ST[1])   # pebbly banks
        depth = (y - HZ) / (H - HZ)
        s.hline(a + 1, b - 1, y, Wt[2] if depth > 0.15 else Wt[3])
        if b - a > 8:
            s.hline(a + 2, a + 2 + int((b - a) * 0.25), y, Wt[3])    # sky in the water, top-left
        s.set(a + 1, y, Wt[1])
    for _ in range(60):                                    # ripples and glints
        y = rnd.randint(HZ + 3, H - 1)
        cx, hw = brook_center(y), brook_half(y)
        if hw < 3:
            continue
        x = int(cx + rnd.uniform(-hw + 2, hw - 4))
        s.hline(x, x + rnd.randint(1, 3), y, Wt[4] if rnd.random() < 0.4 else Wt[3])
    petals(s, HZ + 6, H - 1, 0, 0)
    for _ in range(40):                                    # petals drifting on the water
        y = rnd.randint(HZ + 8, H - 1)
        cx, hw = brook_center(y), brook_half(y)
        x = int(cx + rnd.uniform(-hw + 1, hw - 1))
        s.set(x, y, rnd.choice((P.blossom[3], P.blossom[4])))
    for _ in range(26):                                    # bank stones
        y = rnd.randint(HZ + 10, PATH[0] - 2)
        cx, hw = brook_center(y), brook_half(y)
        x = int(cx + rnd.choice((-1, 1)) * (hw + rnd.uniform(0, 2)))
        s.ellipse(x, y, 2, 1.2, ST[2]).set(x - 1, y - 1, ST[3]).set(x + 1, y, ST[1])
    for side in (-1, 1):                                   # reeds and irises where it meets the lane
        for k in range(10):
            y = PATH[0] - 1 - rnd.randint(0, 6)
            cx, hw = brook_center(y), brook_half(y)
            x = int(cx + side * (hw + 2 + rnd.randint(0, 5)))
            h = rnd.randint(4, 9)
            s.vline(x, y - h, y, P.green[rnd.choice((1, 2, 3))])
            if k % 3 == 0:
                s.rect(x - 1, y - h - 1, 2, 2, P.lilac[2]).set(x, y - h - 2, P.lilac[3]).set(x - 1, y - h, P.mustard[4])


def bridge(s):
    """The lane crosses on a humpless stone slab bridge; its face and arch
    show in front of the lane, low parapets behind and before it."""
    x0, x1 = 138, 202
    y0, y1 = PATH
    s.rect(x0, y0, x1 - x0, y1 - y0, ST[2])
    rnd = random.Random(41)
    for y in range(y0 + 2, y1, 3):                        # flagstones
        off = 0 if (y // 3) % 2 else 4
        for x in range(x0 + off, x1, 8):
            s.vline(x, y, y + 2, ST[1])
        s.hline(x0, x1 - 1, y, ST[1])
    for _ in range(80):
        s.set(rnd.randint(x0, x1 - 1), rnd.randint(y0 + 1, y1 - 1), ST[rnd.choice((1, 3, 3))])
    # back parapet: low railing of stone posts and a capping rail
    for x in range(x0, x1 + 1, 8):
        s.rect(x, y0 - 8, 3, 8, ST[2]).vline(x, y0 - 8, y0 - 1, ST[3]).vline(x + 2, y0 - 8, y0 - 1, ST[1])
        s.rect(x, y0 - 10, 3, 2, ST[3])
    s.hline(x0, x1 + 2, y0 - 6, ST[3]).hline(x0, x1 + 2, y0 - 5, ST[1])
    # front face and the arch over the water
    s.rect(x0 - 2, y1, x1 - x0 + 5, H - y1, ST[2])
    s.hline(x0 - 2, x1 + 2, y1, ST[4]).hline(x0 - 2, x1 + 2, y1 + 1, ST[3])
    cx = 170
    for y in range(y1 + 3, H):
        hw = int(math.sqrt(max(0, 22 ** 2 - (H + 4 - y) ** 2 * 1.6)))
        if hw:
            s.hline(cx - hw, cx + hw, y, P.sea[1])
            s.set(cx - hw - 1, y, ST[0]).set(cx + hw + 1, y, ST[3])
            s.hline(cx - hw + 2, cx - hw + 4, y, P.sea[2])
    for k in range(-5, 6):                                 # voussoir lines round the arch
        a = math.pi / 2 + k * 0.25
        x, y = cx + math.cos(a) * 21, H + 4 - math.sin(a) * 14
        s.set(int(x), int(y) - 1, ST[1])
    for x in range(x0, x1, 7):                             # coursed stone on the face
        s.vline(x, y1 + 2, y1 + 5, ST[1])
    s.hline(x0 - 2, x1 + 2, y1 + 6, ST[1])


# ------------------------------------------------------------- fields

def field(s, vx, top, y_end, far, near, pick, seed):
    """Crop rows converging on (vx, top). The bed is a trapezoid from `far`
    (x0, x1 at the top) to `near` (x0, x1 at y_end) with ragged grassy
    edges; rows blur into haze far off. pick(i, y) gives row i's ramp."""
    rnd = random.Random(seed)
    for y in range(top + 1, y_end):
        d = (y - top) / (y_end - top)
        lo = far[0] + (near[0] - far[0]) * d + rnd.randint(-1, 1)
        hi = far[1] + (near[1] - far[1]) * d + rnd.randint(-1, 1)
        for x in range(int(lo), int(hi)):
            u = (x - vx) / (d * 60 + 0.01)
            i = math.floor(u)
            f = u - i
            R = pick(i, y)
            if d < 0.12:                                   # far off: a soft band of colour
                c = R[3] if (x + y) % 3 else G[3]
            elif f < 0.08 + 0.12 * (1 - d):
                c = G[1] if d > 0.3 else G[2]
            elif f < 0.3:
                c = R[3]
            elif f < 0.78:
                c = R[2] if d < 0.45 else R[3]
            else:
                c = R[1] if d > 0.6 else R[2]
            s.set(x, y, c)
        if d > 0.3:                                        # blooms near us
            for _ in range(int(d * 34)):
                x = rnd.randint(int(lo), int(hi) - 1)
                u = (x - vx) / (d * 60 + 0.01)
                if (u - math.floor(u)) > 0.25:
                    R = pick(math.floor(u), y)
                    s.set(x, y, R[4]).set(x, y - 1, R[3])
        for x in (int(lo) - 1, int(hi)):                   # grass tufts along the edges
            s.set(x, y, G[3]).set(x + rnd.choice((-1, 1)), y, G[2])
    for x in range(near[0] - 2, near[1] + 2):             # a grassy bund at the near edge
        s.set(x, y_end, G[1]).set(x, y_end + 1, G[3] if x % 3 else G[4])


def wildflowers(s, patches, seed):
    """Loose drifts of small flowers in the lawn: (cx, cy, rx, ry, ramp)."""
    rnd = random.Random(seed)
    for cx, cy, rx, ry, R in patches:
        for _ in range(int(rx * ry * 0.9)):
            u, v = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
            if u * u + v * v > 1:
                continue
            x, y = int(cx + u * rx), int(cy + v * ry)
            s.set(x, y + 1, G[1]).set(x, y, R[3] if rnd.random() < 0.6 else R[4])
            if rnd.random() < 0.3:
                s.set(x + 1, y, R[2])


def farmhouse(s, x, base, w=22):
    """A white-walled farmhouse with a dark tiled roof, far off."""
    Wl, Rf = P.linen, P.slate
    s.rect(x, base - 8, w, 8, Wl[3]).vline(x, base - 8, base - 1, Wl[3]).vline(x + w - 1, base - 8, base - 1, Wl[2])
    s.hline(x, x + w - 1, base - 1, Wl[1])
    for wx in range(x + 4, x + w - 3, 7):
        s.rect(wx, base - 6, 2, 2, Rf[1])
    s.rect(x + w // 2 - 1, base - 4, 3, 4, P.walnut[1])
    for k in range(4):
        s.hline(x - 2 + k, x + w + 1 - k, base - 9 - k, Rf[1] if k == 0 else Rf[2])
    s.hline(x + 2, x + w - 3, base - 13, Rf[3])
    s.set(x - 3, base - 10, Rf[2]).set(x + w + 2, base - 10, Rf[2])   # upturned eaves


def beehives(s, x, base):
    for k, dx in enumerate((0, 12)):
        hx = x + dx
        s.rect(hx, base - 9, 9, 9, P.oak[3]).vline(hx, base - 9, base - 1, P.oak[4]).vline(hx + 8, base - 9, base - 1, P.oak[1])
        for yy in (base - 6, base - 3):
            s.hline(hx, hx + 8, yy, P.oak[2])
        s.rect(hx - 1, base - 11, 11, 2, P.linen[3]).hline(hx - 1, hx + 9, base - 10, P.linen[1])
        s.hline(hx + 3, hx + 5, base - 1, P.walnut[0])
        s.hline(hx + 1, hx + 8, base, P.oat[1])
    for bx, by in ((x + 4, base - 15), (x + 20, base - 17), (x + 26, base - 12)):
        s.set(bx, by, P.mustard[3]).set(bx + 1, by, P.walnut[0])


def scarecrow(s, x, base):
    s.vline(x, base - 22, base, P.walnut[2]).hline(x - 8, x + 8, base - 17, P.walnut[2])
    s.rect(x - 4, base - 18, 9, 9, P.coral[2]).vline(x - 4, base - 18, base - 10, P.coral[3]).hline(x - 4, x + 4, base - 10, P.coral[1])
    s.ellipse(x, base - 22, 3, 3, P.linen[3]).set(x - 1, base - 22, P.walnut[0]).set(x + 1, base - 22, P.walnut[0])
    s.hline(x - 6, x + 6, base - 25, P.mustard[2]).rect(x - 3, base - 28, 7, 3, P.mustard[3])
    for k in (-7, -6, 6, 7):
        s.set(x + k, base - 16, P.mustard[4])


def windmill(s, cx, base):
    """A tall white windmill on the horizon: tapering tower, red cap, four
    lattice sails (still; the page can turn a sprite of them)."""
    Wl = P.linen
    top = base - 34
    for y in range(top, base):
        t = (y - top) / (base - top)
        hw = int(5 + 4 * t)
        s.hline(cx - hw, cx + hw, y, Wl[3])
        s.set(cx - hw, y, Wl[3]).set(cx + hw, y, Wl[1]).set(cx + hw - 1, y, Wl[2])
    s.rect(cx - 2, base - 7, 4, 7, P.walnut[1]).hline(cx - 2, cx + 1, base - 8, P.walnut[2])
    s.rect(cx - 1, top + 10, 2, 3, P.sea[1]).rect(cx - 2, top + 20, 2, 3, P.sea[1])
    s.hline(cx - 9, cx + 9, base - 14, P.walnut[2]).hline(cx - 9, cx + 9, base - 13, P.walnut[1])   # gallery
    for x in range(cx - 9, cx + 10, 3):
        s.vline(x, base - 17, base - 14, P.walnut[1])
    for k in range(6):                                     # cap
        s.hline(cx - 6 + k, cx + 6 - k, top - k, P.terracotta[2] if k else P.terracotta[1])
    s.hline(cx - 4, cx, top - 3, P.terracotta[3])
    hub = (cx, top - 1)
    sails(s, *hub)


def sails(s, hx, hy, phase=0.0):
    for k in range(4):
        a = phase + k * math.pi / 2 + 0.35
        for r in range(2, 25):
            x, y = hx + math.cos(a) * r, hy - math.sin(a) * r
            s.set(int(round(x)), int(round(y)), P.walnut[1])
            if r > 6:                                      # the lattice sail beside the stock
                for w in range(1, 5):
                    px, py = x + math.cos(a + math.pi / 2) * w, y - math.sin(a + math.pi / 2) * w
                    c = P.linen[3] if (r + w) % 3 else P.walnut[2]
                    s.set(int(round(px)), int(round(py)), c)
    s.rect(hx - 1, hy - 1, 3, 3, P.walnut[0])


def tulip_pick(i, y):
    return (P.coral, P.mustard, P.blossom, P.lilac, P.hydrangea)[i % 5]


def rape_pick(i, y):
    return P.mustard if i % 4 else G


# ------------------------------------------------------------- arbor

ARBOR = (118, 262, 50)    # x0, x1, beam y


def arbor(s, front=False):
    """Pergola behind the lane: posts, beams and wisteria racemes. The back
    half goes in the background; front=True draws only the hanging flowers
    that overlap the beam (same layer, kept for the page if needed)."""
    x0, x1, by = ARBOR
    Wd = P.oak
    rnd = random.Random(61)
    if not front:
        for x in range(x0, x1 + 1, 24):                    # posts
            s.rect(x, by, 4, PATH[0] - 2 - by, Wd[2]).vline(x, by, PATH[0] - 3, Wd[3]).vline(x + 3, by, PATH[0] - 3, Wd[1])
            s.rect(x - 1, PATH[0] - 4, 6, 3, ST[2]).hline(x - 1, x + 4, PATH[0] - 4, ST[3])
        s.rect(x0 - 8, by - 4, x1 - x0 + 20, 3, Wd[3]).hline(x0 - 8, x1 + 11, by - 4, Wd[4]).hline(x0 - 8, x1 + 11, by - 2, Wd[1])
        for x in range(x0 - 6, x1 + 10, 6):                # rafters ends
            s.rect(x, by - 7, 2, 3, Wd[2]).set(x, by - 7, Wd[3])
        s.rect(x0 - 8, by - 1, x1 - x0 + 20, 2, Wd[1])
    # leafy mass along the top, then racemes hanging down
    for x in range(x0 - 10, x1 + 14, 3):
        y = by - 6 + rnd.randint(-3, 1)
        s.ellipse(x, y, 3.5, 2.6, G[rnd.choice((2, 3))]).set(x - 1, y - 1, G[4]).set(x + 2, y + 1, G[1])
    L = P.lilac
    for x in range(x0 - 8, x1 + 12, 2):
        if rnd.random() < 0.18:
            continue
        top = by - 3 + rnd.randint(-1, 2)
        ln = rnd.randint(6, 16)
        for k in range(ln):
            w = 1 if k < ln - 3 else 0
            c = L[3] if k < ln * 0.35 else L[2] if k < ln * 0.75 else L[1]
            if (x + k) % 5 == 0:
                c = L[4]
            s.hline(x - w + (k % 2), x + (k % 2), top + k, c)
    for _ in range(40):                                    # fallen florets on the stones
        s.set(rnd.randint(x0 - 4, x1 + 6), rnd.randint(PATH[0] + 2, PATH[1] - 2), rnd.choice((L[3], L[4], L[2])))


def stepping(s, x0, x1):
    """Flagstone paving under the pergola, between lawn and lane."""
    for x in range(x0, x1, 9):
        y = 88 + (x // 9) % 2
        s.ellipse(x + 4, y, 4, 1.6, ST[2]).hline(x + 1, x + 6, y - 1, ST[3]).hline(x + 2, x + 6, y + 1, ST[1])


# ------------------------------------------------------------- scenes

def background(zone):
    s = Sprite(W, H)
    PK.sky(s)
    clouds(s, zone)
    hills(s, zone)
    PK.treeline(s, SEASON)
    lawn(s, zone)
    zid = zone["id"]
    patches = {"brook": [(60, 80, 26, 5, P.lilac), (120, 70, 18, 3, P.mustard), (270, 78, 30, 5, P.blossom),
                         (300, 88, 20, 3, P.mustard), (40, 66, 22, 3, P.blossom)],
               "rape": [(20, 72, 18, 4, P.lilac)],
               "tulip": [(28, 70, 20, 4, P.blossom)],
               "arbor": [(50, 76, 34, 6, P.mustard), (300, 74, 24, 5, P.lilac), (200, 66, 60, 3, P.blossom),
                         (90, 88, 20, 3, P.lilac)]}[zid]
    wildflowers(s, patches, zid + "wf")
    if zid == "brook":
        brook(s)
    if zid == "rape":
        farmhouse(s, 168, HZ + 1, 24)
        farmhouse(s, 206, HZ + 2, 16)
        field(s, 190, HZ + 2, PATH[0] - 5, (110, 300), (44, 312), rape_pick, 71)
        scarecrow(s, 262, 84)
    if zid == "tulip":
        windmill(s, 236, HZ + 4)
        field(s, 170, HZ + 3, PATH[0] - 5, (96, 300), (58, 322), tulip_pick, 73)
    if zid == "arbor":
        stepping(s, ARBOR[0] - 6, ARBOR[1] + 10)
    PK.path(s, SEASON)
    petals(s, PATH[0] + 2, PATH[1] - 2, 50 if zid in ("brook", "arbor") else 22, zid + "pp")
    if zid == "brook":
        bridge(s)
        petals(s, PATH[0] + 2, PATH[1] - 2, 18, "br", 138, 202)
    for _, x, _, base, rx, _ in zone["trees"]:            # tree shadows
        s.ellipse(x + 10, base + 3, rx + 2, 3, G[1])
    bushes = {"brook": [("hydrangea", 60, 10, 8, 93), ("box", 290, 9, 7, 93)],
              "rape": [("box", 316, 10, 8, 93)],
              "tulip": [("hydrangea", 22, 12, 9, 93)],
              "arbor": [("hydrangea", 70, 11, 9, 93), ("box", 290, 9, 7, 93)]}[zid]
    for kind, cx, hw, ht, base in bushes:
        s.blit(FY.bush(kind, cx, hw, ht, SEASON, base=base), 0, 0)
    if zid == "rape":
        beehives(s, 92, 93)
    if zid == "arbor":
        arbor(s)
        PK.bench(s, 190, 92)
    border = Sprite(W, H)
    PK.border(border, SEASON)
    if zid == "brook":
        border.px[:, 136:205] = 0
    s.blit(border, 0, 0)
    return s


def trees(zone, frame):
    s = Sprite(W, H)
    for kind, x, cy, base, rx, ry in sorted(zone["trees"], key=lambda t: t[3]):
        s.blit(FY.tree(kind, SEASON, frame, at=(x, cy, base, rx, ry)), 0, 0)
    return s


def preview(zone, frame=0):
    s = background(zone)
    s.blit(trees(zone, frame), 0, 0)
    return s


def build():
    out = {}
    pano = Sprite(W * len(ZONES), H)
    for i, zone in enumerate(ZONES):
        out[f"spring_{zone['id']}"] = background(zone)
        for f in (0, 1):
            out[f"spring_{zone['id']}_tree_{f}"] = trees(zone, f)
        pv = preview(zone)
        out[f"spring_{zone['id']}_preview"] = pv
        pano.blit(pv, i * W, 0)
    out["spring_panorama"] = pano
    return out
