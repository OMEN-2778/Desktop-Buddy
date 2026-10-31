"""春日花溪: a spring-only outing, five connected 342x118 screens in the park's
style (same sky, far tree line, gravel lane at y=94..106, flower border, trees
and bushes from front_yard). Light from the top left.

    brook   溪桥樱堤  a brook winds down from the hills under a stone arch
                      bridge in the lane; cherry trees on both banks
    rape    油菜花田  terraced rapeseed rows run to the hills, white-walled
                      farmhouses, beehives beside the lane
    tulip   风车花圃  tulip stripes in four colours, a windmill behind
    farm    小菜园    six raised beds for crops (cabbage, carrot, tomato,
                      strawberry, corn, pumpkin; 4 stages each), a well
    orchard 果园      pear, peach, apple and orange trees (sapling → young
                      → blossom → fruit), an empty pit for a new tree

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
    {"id": "farm", "name": "小菜园",
     "trees": [("linden", 330, 36, 93, 20, 22)]},
    {"id": "orchard", "name": "果园", "trees": []},
]


# ------------------------------------------------------------- far away

def hills(s, zone):
    """Two hazy ridges behind the tree line, the near one greener."""
    off = {"brook": 0, "rape": 90, "tulip": 170, "farm": 260, "orchard": 40}[zone["id"]]
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


# ------------------------------------------------------------- farm

SOIL = P.wood
PLOTS = [(66, 70, 58, 8), (134, 70, 58, 8), (202, 70, 58, 8),          # x, top, w, h: back row
         (58, 81, 66, 10), (134, 81, 66, 10), (210, 81, 66, 10)]       # front row (bigger, nearer)
CROPS = ["cabbage", "carrot", "tomato", "strawberry", "corn", "pumpkin"]


def plot(s, x, y, w, h):
    """A raised bed: plank edging lit on top, tilled soil in furrows."""
    s.rect(x - 1, y - 1, w + 2, h + 3, P.oak[1])
    s.hline(x - 1, x + w, y - 1, P.oak[3]).hline(x - 1, x + w, y + h + 1, P.oak[0])
    s.rect(x, y, w, h, SOIL[2])
    for yy in range(y, y + h, 3):                          # furrows: lit ridge, dark trench
        s.hline(x, x + w - 1, yy, SOIL[3]).hline(x, x + w - 1, yy + 2, SOIL[1])
    rnd = random.Random(x * 7 + y)
    for _ in range(w * h // 8):
        s.set(rnd.randint(x, x + w - 1), rnd.randint(y, y + h - 1), SOIL[rnd.choice((1, 3, 4))])
    for px in range(x - 1, x + w + 1, 12):                 # edging posts
        s.vline(px, y - 2, y + h + 1, P.oak[2]).set(px, y - 2, P.oak[4])


def crop(s, kind, stage, x, base):
    """One plant centred on x standing on `base`; stage 0 seed mound,
    1 sprout, 2 growing, 3 ripe."""
    L = P.green
    if stage == 0:
        s.hline(x - 2, x + 2, base, SOIL[1]).hline(x - 1, x + 1, base - 1, SOIL[3])
        return
    if stage == 1:
        s.vline(x, base - 2, base, L[2]).set(x - 1, base - 3, L[3]).set(x + 1, base - 3, L[3]).set(x - 2, base - 3, L[2])
        return
    big = stage == 3
    if kind == "cabbage":
        r = 4 if big else 2.6
        s.ellipse(x, base - r, r + 1, r, L[2]).ellipse(x - 1, base - r - 1, r * 0.6, r * 0.55, L[3])
        if big:
            s.ellipse(x, base - r, 2, 2, P.leaf_spring[4]).set(x - 1, base - r - 1, P.linen[3])
        s.set(x + 2, base - 1, L[1])
    elif kind == "carrot":
        h = 7 if big else 4
        for dx in (-2, 0, 2):
            s.line(x, base - 1, x + dx, base - h, L[2 + (dx == 0)])
            s.set(x + dx, base - h, L[4])
        if big:
            s.rect(x - 1, base - 1, 3, 2, P.coral[3]).set(x - 1, base - 1, P.coral[4])
    elif kind == "tomato":
        h = 11 if big else 7
        s.vline(x + 2, base - h - 1, base, P.oak[3])         # stake
        s.vline(x, base - h, base, L[1])
        for k in range(2, h, 3):
            s.hline(x - 2, x - 1, base - k, L[2]).hline(x + 1, x + 2, base - k - 1, L[3])
        if big:
            for fx, fy in ((-2, 4), (1, 7), (-1, 9)):
                s.rect(x + fx, base - fy, 2, 2, P.coral[2]).set(x + fx, base - fy, P.coral[4])
    elif kind == "strawberry":
        s.ellipse(x, base - 2, 3, 2, L[2]).set(x - 1, base - 3, L[3]).set(x + 2, base - 1, L[1])
        if big:
            for fx in (-3, 2):
                s.rect(x + fx, base - 1, 2, 2, P.coral[2]).set(x + fx, base - 1, P.coral[4]).set(x + fx + 1, base, P.coral[1])
        else:
            s.set(x - 2, base - 1, P.linen[3])
    elif kind == "corn":
        h = 15 if big else 8
        s.vline(x, base - h, base, L[2]).vline(x + 1, base - h + 2, base, L[1])
        for k in range(3, h, 4):
            s.line(x, base - k, x - 3, base - k + 2, L[3]).line(x + 1, base - k - 1, x + 4, base - k + 1, L[2])
        if big:
            s.rect(x + 2, base - 9, 2, 4, P.mustard[3]).set(x + 2, base - 9, P.mustard[4]).set(x + 3, base - 10, L[3])
            s.hline(x - 1, x + 1, base - h - 1, P.mustard[4])
    elif kind == "pumpkin":
        s.line(x - 4, base - 2, x + 4, base - 3, L[2]).ellipse(x - 3, base - 3, 2, 1.5, L[3]).ellipse(x + 3, base - 3, 2, 1.5, L[2])
        if big:
            s.ellipse(x, base - 3, 4, 3, P.mustard[2]).ellipse(x - 1, base - 4, 2, 1.5, P.mustard[3])
            s.vline(x, base - 5, base - 1, P.mustard[1]).vline(x, base - 7, base - 6, P.walnut[2])


def plot_slots(px, top, w, h):
    """Planting spots in a bed: (x, base) pairs, one per 11 px."""
    n = max(1, w // 11)
    gap = w / n
    return [(round(px + gap * (i + 0.5)), top + h - 1) for i in range(n)]


def well(s, x, base):
    """A stone well with a little roof and a bucket (water for the beds)."""
    s.rect(x - 7, base - 8, 15, 8, ST[2]).hline(x - 7, x + 7, base - 8, ST[4]).hline(x - 7, x + 7, base - 1, ST[1])
    for xx in range(x - 6, x + 7, 4):
        s.vline(xx, base - 7, base - 2, ST[1])
    s.hline(x - 5, x + 5, base - 9, P.sea[1])
    for px in (x - 7, x + 7):
        s.vline(px, base - 22, base - 9, P.walnut[2])
    for k in range(5):
        s.hline(x - 10 + k, x + 10 - k, base - 23 - k, P.terracotta[2] if k else P.terracotta[1])
    s.hline(x - 6, x - 1, base - 26, P.terracotta[3])
    s.hline(x - 6, x + 6, base - 18, P.walnut[1])                # windlass
    s.vline(x, base - 17, base - 13, P.oat[2]).rect(x - 1, base - 13, 3, 3, P.oak[2])


def tool_rack(s, x, base):
    s.vline(x, base - 14, base, P.walnut[2]).vline(x + 12, base - 14, base, P.walnut[2]).hline(x, x + 12, base - 13, P.walnut[3])
    s.vline(x + 3, base - 17, base - 1, P.oak[3]).rect(x + 2, base - 3, 3, 3, P.steel[2])      # spade
    s.vline(x + 8, base - 17, base - 1, P.oak[3]).hline(x + 6, x + 10, base - 17, P.steel[2])  # rake
    for k in range(6, 11, 2):
        s.set(x + k, base - 16, P.steel[1])
    s.rect(x + 15, base - 5, 6, 5, P.sea[2]).hline(x + 15, x + 20, base - 5, P.sea[3])     # watering can
    s.line(x + 21, base - 4, x + 24, base - 7, P.sea[2]).hline(x + 16, x + 19, base - 7, P.sea[1])


def farm(s):
    for x, y, w, h in PLOTS:                               # trodden grass round each bed
        s.ellipse(x + w / 2, y + h / 2 + 1, w / 2 + 6, h / 2 + 3, G[2])
    for x, y, w, h in PLOTS:
        plot(s, x, y, w, h)
    well(s, 300, 80)
    tool_rack(s, 20, 92)


# ------------------------------------------------------------- orchard

WHITE = [P.blossom[0], P.blossom[2], P.blossom[3], P.blossom[4], P.porcelain[3]]   # pale pink-white petals
PEACH = [P.blossom[0], P.coral[2], P.blossom[2], P.blossom[3], P.blossom[4]]
FY.LEAVES.setdefault(("pear", "spring"), [WHITE, WHITE, P.leaf_spring, P.leaf_spring])
FY.LEAVES.setdefault(("apple", "spring"), [WHITE, P.blossom, WHITE, P.leaf_spring])
FY.LEAVES.setdefault(("peach", "spring"), [PEACH, PEACH, P.blossom, P.leaf_spring])
FY.LEAVES.setdefault(("orange", "spring"), [P.green, P.green, P.leaf_spring])
FY.LEAVES.setdefault(("fruit", "spring"), [P.green, P.leaf_spring, P.green])
FRUIT = {"apple": P.coral, "peach": PEACH, "pear": P.mustard, "orange": P.terracotta}
ORCHARD = [("pear", 70, 52, 66, 10, 8), ("peach", 128, 52, 66, 10, 8), ("apple", 186, 52, 66, 10, 8), ("orange", 244, 52, 66, 10, 8),
           ("peach", 300, 52, 66, 10, 8),
           ("apple", 52, 58, 88, 17, 14), ("peach", 124, 58, 88, 17, 14), ("pear", 196, 58, 88, 17, 14),
           ("orange", 268, 58, 88, 17, 14)]
PITS = [(330, 88)]                                         # an empty spot to plant a new tree


def orchard(s):
    for _, x, _, base, rx, _ in ORCHARD:                  # mown circles under the trees
        s.ellipse(x + 2, base + 1, rx * 0.7 + 3, 2.5, G[3])
    rnd = random.Random(81)
    for _, x, _, base, rx, _ in ORCHARD:                  # fallen petals round each trunk
        for _ in range(int(rx * 1.5)):
            s.set(x + rnd.randint(-rx, rx), base + rnd.randint(-1, 3), rnd.choice((P.blossom[3], P.porcelain[3])))
    for x, y in PITS:
        s.ellipse(x, y, 6, 2, SOIL[1]).ellipse(x - 1, y - 1, 4, 1, SOIL[2])
        s.vline(x + 7, y - 9, y, P.oak[3]).rect(x + 5, y - 9, 5, 3, P.oak[4])     # a little sign
    ladder(s, 222, 88)
    for bx in (150, 162):
        s.rect(bx, 85, 9, 6, P.oak[2]).hline(bx, bx + 8, 85, P.oak[4]).hline(bx, bx + 8, 88, P.oak[1])


def ladder(s, x, base):
    s.line(x, base, x + 6, base - 24, P.oak[3]).line(x + 6, base, x + 12, base - 24, P.oak[2])
    for k in range(3, 24, 4):
        s.hline(x + k * 6 // 24, x + 6 + k * 6 // 24, base - k, P.oak[2])


def fruit_tree(kind, frame, at, stage=3):
    """A fruit tree: stage 0 sapling, 1 young, 2 in blossom, 3 bearing fruit."""
    x, cy, base, rx, ry = at
    if stage == 0:
        s = Sprite(W, H)
        s.vline(x, base - 10, base, P.walnut[2]).set(x - 1, base - 10, G[3]).set(x + 1, base - 11, G[3]).set(x, base - 12, G[4])
        s.vline(x + 3, base - 10, base, P.oak[3]).hline(x + 1, x + 3, base - 7, P.oat[2])
        return s
    if stage == 1:
        return FY.tree("linden", SEASON, frame, at=(x, base - 14, base, 6, 5))
    if stage == 2:
        s = FY.tree(kind, SEASON, frame, at=at)
        if kind == "orange":                               # citrus: small white flowers among dark leaves
            rnd = random.Random("orangeflower" + str(x))
            for _ in range(int(rx * ry / 6)):
                u, v = rnd.uniform(-0.85, 0.85), rnd.uniform(-0.8, 0.8)
                if u * u + v * v < 0.75:
                    fx, fy = int(x + u * rx), int(cy + v * ry)
                    s.set(fx, fy, P.porcelain[3]).set(fx + 1, fy, P.linen[2])
        return s
    s = FY.tree("fruit", SEASON, frame, at=at)
    rnd = random.Random(kind + str(x))
    F = FRUIT[kind]
    for _ in range(int(rx * ry / 12)):
        u, v = rnd.uniform(-0.8, 0.8), rnd.uniform(-0.6, 0.8)
        if u * u + v * v < 0.7:
            fx, fy = int(x + u * rx), int(cy + v * ry)
            s.rect(fx, fy, 2, 2, F[2]).set(fx, fy, F[4]).set(fx + 1, fy + 1, F[1])
    return s


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
               "farm": [(30, 72, 20, 4, P.mustard), (300, 64, 20, 2, P.lilac)],
               "orchard": [(100, 74, 30, 3, P.mustard), (240, 76, 30, 3, P.lilac)]}[zid]
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
    if zid == "farm":
        farm(s)
    if zid == "orchard":
        orchard(s)
    PK.path(s, SEASON)
    petals(s, PATH[0] + 2, PATH[1] - 2, 50 if zid in ("brook", "orchard") else 22, zid + "pp")
    if zid == "brook":
        bridge(s)
        petals(s, PATH[0] + 2, PATH[1] - 2, 18, "br", 138, 202)
    for _, x, _, base, rx, _ in zone["trees"]:            # tree shadows
        s.ellipse(x + 10, base + 3, rx + 2, 3, G[1])
    bushes = {"brook": [("hydrangea", 60, 10, 8, 93), ("box", 290, 9, 7, 93)],
              "rape": [("box", 316, 10, 8, 93)],
              "tulip": [("hydrangea", 22, 12, 9, 93)],
              "farm": [("box", 40, 9, 7, 93)],
              "orchard": [("hydrangea", 14, 11, 9, 93)]}[zid]
    for kind, cx, hw, ht, base in bushes:
        s.blit(FY.bush(kind, cx, hw, ht, SEASON, base=base), 0, 0)
    if zid == "rape":
        beehives(s, 92, 93)
    border = Sprite(W, H)
    PK.border(border, SEASON)
    if zid == "brook":
        border.px[:, 136:205] = 0
    s.blit(border, 0, 0)
    return s


def trees(zone, frame):
    s = Sprite(W, H)
    if zone["id"] == "orchard":
        for kind, x, cy, base, rx, ry in sorted(ORCHARD, key=lambda t: t[3]):
            s.blit(fruit_tree(kind, frame, (x, cy, base, rx, ry), stage=2), 0, 0)
    for kind, x, cy, base, rx, ry in sorted(zone["trees"], key=lambda t: t[3]):
        s.blit(FY.tree(kind, SEASON, frame, at=(x, cy, base, rx, ry)), 0, 0)
    return s


def preview(zone, frame=0):
    s = background(zone)
    if zone["id"] == "farm":                               # sample crops at every stage
        for i, (x, y, w, h) in enumerate(PLOTS):
            for j, (cx, base) in enumerate(plot_slots(x, y, w, h)):
                crop(s, CROPS[i], min(3, j), cx, base)
    s.blit(trees(zone, frame), 0, 0)
    return s


def stage_sheet():
    """Every crop and fruit tree at every stage, for review."""
    s = Sprite(240, 180)
    s.rect(0, 0, 240, 180, P.sky_day[3])
    for i, kind in enumerate(CROPS):
        y = 20 + i * 26
        s.rect(2, y + 1, 64, 3, SOIL[2])
        for st in range(4):
            crop(s, kind, st, 9 + st * 16, y)
    for i, kind in enumerate(("apple", "peach", "pear", "orange")):
        for st in range(4):
            cell = fruit_tree(kind, 0, (30, 18, 40, 13, 11), stage=st)
            s.rect(72 + st * 42, 2 + i * 44 + 40, 40, 2, G[2])
            s.blit(cell.crop(8, 2, 44, 42), 70 + st * 42, 2 + i * 44)
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
    out["spring_stages"] = stage_sheet()
    return out
