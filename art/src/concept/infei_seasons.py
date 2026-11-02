"""茵菲谷 (the spring farm map) in summer, autumn and winter. Owner 2026-11-02: plan C, the
farm lies fallow in winter (snow on the beds), and the map needs its other three seasons.

Same layout, buildings, props and coordinates as spring_fields.py; only what grows and
what lies on the ground changes:
- summer: deep green lawn and trees, the rape field gone to green pods, the flower
  field lavender, fruit on the orchard trees;
- autumn: tawny lawn with fallen leaves, the rape field cut to golden stubble, the
  flower field marigold, orange and red crowns, ripe fruit;
- winter: snow on the ground, the fields and the beds, bare trees, snow caps on every
  roof, fence, cart and branch top (found from each layer's own silhouette).
Builds infei_<season>_<zone>(_trees_<f>)(_front).png and infei_<season>_panorama.png.
"""
import math
import random

import numpy as np

import spring_fields as F
import front_yard as FY
import park as PK
from pixelkit import Sprite, P

SEASONS = ("summer", "autumn", "winter")
PREVIEW_SCALE = 3
W, H = F.W, F.H

GROUND = {   # the lawn ramp (5 shades, dark -> light) per season
    "spring": P.leaf_spring,
    "summer": P.green,
    "autumn": [P.walnut[1], P.grass[1], P.grass[2], P.mustard[2], P.mustard[3]],
    "winter": [P.slate[3], P.porcelain[1], P.snow[1], P.snow[2], P.snow[3]],
}
FIELD = {   # what the two flower fields turn into: (rape rows, tulip rows)
    "summer": ([P.green, P.leaf_spring], [P.lilac, P.green, P.lilac, P.hydrangea]),
    "autumn": ([P.mustard, P.walnut], [P.autumn, P.mustard, P.terracotta, P.autumn]),
    "winter": ([GROUND["winter"]], [GROUND["winter"]]),
}
for kind in ("pear", "apple", "peach", "fruit"):
    FY.LEAVES.setdefault((kind, "summer"), [P.green, P.grass])
    FY.LEAVES.setdefault((kind, "autumn"), [P.autumn, P.mustard, P.green])
FY.LEAVES.setdefault(("orange", "summer"), [P.green, P.green, P.grass])
FY.LEAVES.setdefault(("orange", "autumn"), [P.green, P.green, P.grass])


def _season(season):
    """Point spring_fields at a season: its globals and the few spring-only details."""
    F.SEASON = season
    F.G = GROUND[season]
    snow = season == "winter"
    rape, tulip = FIELD[season]
    F.rape_pick = lambda i, y: rape[i % len(rape)]
    F.tulip_pick = lambda i, y: tulip[i % len(tulip)]

    def lawn(s, zone):
        G = F.G
        width = s.w
        s.rect(0, F.HZ, width, F.PATH[0] - F.HZ, G[2])
        for cx, cy, rx, ry in ((60 * width / W, 86, 90 * width / W, 18), (250 * width / W, 88, 110 * width / W, 16)):
            s.ellipse(cx + 4, cy + 3, rx, ry, G[2])
            s.ellipse(cx - 6, cy - 4, rx - 8, ry - 5, G[3])
        s.hline(0, width - 1, F.HZ, G[1])
        rnd = random.Random(zone["id"] + "lawn")
        for _ in range(round(420 * width / W)):
            x, y = rnd.randrange(width), rnd.randint(F.HZ + 1, F.PATH[0] - 1)
            s.set(x, y, G[rnd.choice((1, 2, 4))])
        dots = {"summer": (P.linen[3], P.mustard[4], P.green[4]), "autumn": (P.autumn[2], P.autumn[3], P.mustard[3], P.autumn[4]),
                "winter": (P.snow[3], P.porcelain[1])}[season]
        for _ in range(round((50 if season == "summer" else 110 if season == "autumn" else 60) * width / W)):
            x, y = rnd.randrange(width), rnd.randint(F.HZ + 3, F.PATH[0] - 2)
            s.set(x, y, rnd.choice(dots))
    F.lawn = lawn

    def petals(s, y0, y1, n, seed, x0=0, x1=W):
        if season != "autumn":
            return
        rnd = random.Random(seed)
        for _ in range(n):                                   # fallen leaves on the lane
            x, y = rnd.randint(x0, x1 - 2), rnd.randint(y0, y1)
            s.set(x, y, rnd.choice((P.autumn[2], P.autumn[3], P.mustard[3])))
            if rnd.random() < 0.4:
                s.set(x + 1, y, P.autumn[1])
    F.petals = petals

    orig_wild = _ORIG["wildflowers"]

    def wildflowers(s, patches, seed):
        if season == "summer":
            orig_wild(s, [(cx, cy, rx, ry, R) for cx, cy, rx, ry, R in patches if R is not P.blossom], seed)
        elif season == "autumn":
            orig_wild(s, [(cx, cy, rx * 0.7, ry, P.autumn) for cx, cy, rx, ry, R in patches], seed)
    F.wildflowers = wildflowers

    def hills(s, zone):
        off = {"brook": 0, "rape": 90, "tulip": 170, "home": 220, "farm": 260, "orchard": 40, "pasture": 40 + W}[zone["id"]]
        near = {"summer": P.sage, "autumn": P.clay, "winter": [P.slate[3], P.porcelain[0], P.porcelain[1], P.snow[2]]}[season]
        for k, (base, amp, R) in enumerate(((F.HZ - 10, 9, P.sky_soft), (F.HZ - 5, 7, near))):
            for x in range(W):
                u = (x + off + 137 * k) / W * math.tau
                top = int(base - amp * (0.55 + 0.45 * math.sin(u * 1.3 + k)) - 3 * math.sin(u * 3.1 + 2 * k))
                s.vline(x, top, F.HZ - 1, R[2])
                s.set(x, top, R[3])
                if (k == 0 or snow) and x % 2 == 0:
                    s.set(x, top + 1, R[3])
    F.hills = hills

    def plot(s, x, y, w, h):
        _ORIG["plot"](s, x, y, w, h)
        if snow:                                             # the beds lie under snow, furrows just showing
            S = P.snow
            s.rect(x, y, w, h, S[2])
            for yy in range(y, y + h, 3):
                s.hline(x, x + w - 1, yy, S[3])
            rnd = random.Random(x * 3 + y)
            for _ in range(w * h // 14):
                s.set(rnd.randint(x, x + w - 1), rnd.randint(y, y + h - 1), F.SOIL[rnd.choice((1, 2))])
    F.plot = plot


_ORIG = {k: getattr(F, k) for k in ("lawn", "petals", "wildflowers", "hills", "plot", "rape_pick", "tulip_pick", "G", "SEASON")}


def _restore():
    for k, v in _ORIG.items():
        setattr(F, k, v)


def caps(m):
    """Top pixels of a silhouette: where snow settles."""
    up = np.zeros_like(m)
    up[1:] = m[:-1]
    return m & ~up


def snowcap(s, mask, rnd, keep_below=None):
    """Snow along the top edge of everything in `mask`: a lit line, a shaded line under it."""
    S = P.snow
    ys, xs = np.nonzero(caps(mask))
    for x, y in zip(xs, ys):
        if keep_below is not None and y > keep_below:
            continue
        if y >= 1:
            s.set(x, y - 1, S[3])
        s.set(x, y, S[3] if rnd.random() < 0.6 else S[2])


def objects(zone, full):
    """What stands on the ground: the scene minus a render with only sky, hills, lawn and lane."""
    keep = {k: getattr(F, k) for k in ("homestead", "pasture", "orchard", "farm", "windmill", "farmhouse", "scarecrow", "beehives", "bridge", "brook", "field")}
    fy_bush, fs_border = FY.bush, F.FS.shrub_border
    try:
        for k in keep:
            setattr(F, k, lambda *a, **kw: None)
        FY.bush = lambda *a, **kw: Sprite(W, H)
        F.FS.shrub_border = lambda *a, **kw: None
        bare = F.background(zone, mill_sails=True, with_clouds=False)
    finally:
        for k, v in keep.items():
            setattr(F, k, v)
        FY.bush, F.FS.shrub_border = fy_bush, fs_border
    a, b = full.px, bare.px
    return np.any(a != b, axis=2) & (a[..., 3] > 0)


def background(zone, season, **kw):
    _season(season)
    try:
        s = F.background(zone, **kw)
        if season == "winter":
            m = objects(zone, F.background(zone, mill_sails=True, with_clouds=False))
            rnd = random.Random(zone["id"] + "snow")
            snowcap(s, m, rnd)
            slate = {tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in P.slate[1:]}
            px = s.px
            for y in range(0, 64):                           # tiled roofs under a blanket, every third tile row showing
                for x in range(W):
                    if m[y, x] and tuple(px[y, x, :3]) in slate and y % 3:
                        s.set(x, y, P.snow[3] if (x + y) % 5 else P.snow[2])
            ys, xs = np.nonzero(m[F.PATH[1] - 2:])              # the shrub strip under the lane: snow lying in the leaves
            for x, y in zip(xs, ys + F.PATH[1] - 2):
                if rnd.random() < 0.45:
                    s.set(x, y, P.snow[rnd.choice((2, 3, 3))])
        return s
    finally:
        _restore()


def trees(zone, season, frame):
    _season(season)
    try:
        if zone["id"] == "orchard":
            s = Sprite(W, H)
            for i, (kind, x, cy, base, rx, ry) in sorted(enumerate(F.ORCHARD), key=lambda t: t[1][3]):
                young = F.YOUNG.get(i)
                if season == "winter":
                    tr = FY.tree("fruit", "winter", frame, at=(x, cy, base, rx, ry)) if young is None else F.fruit_tree(kind, frame, (x, cy, base, rx, ry), stage=0)
                else:
                    tr = F.fruit_tree(kind, frame, (x, cy, base, rx, ry), stage=young if young is not None else 3)
                s.blit(tr, 0, 0)
            rest = F.trees(dict(zone, id="orchard_rest"), frame)
            s.blit(rest, 0, 0)
        else:
            s = F.trees(zone, frame)
        if season == "winter":
            snowcap(s, s.px[..., 3] > 0, random.Random(zone["id"] + "tsnow" + str(frame)))
        return s
    finally:
        _restore()


def front(zone, season):
    s = F.front(zone)
    if season == "winter" and zone["id"] == "pasture":
        snowcap(s, s.px[..., 3] > 0, random.Random("fence"))
    return s


def preview(zone, season, frame=0):
    s = background(zone, season)
    if zone["id"] == "pasture" and season != "winter":
        for kind, x, y, f in sorted(F.HERD, key=lambda h: h[2]):
            a = F.animal(kind, f)
            s.blit(a, x, y - a.h)
    if zone["id"] == "home":
        for x, y, f, r in F.COOP:
            s.blit(F.FS.chicken(f, r), x, y - 11)
    s.blit(front(zone, season), 0, 0)
    s.blit(trees(zone, season, frame), 0, 0)
    return s


def build():
    out = {}
    for season in SEASONS:
        pano = Sprite(W * len(F.ZONES), H)
        for i, zone in enumerate(F.ZONES):
            key = f"infei_{season}_{zone['id']}"
            out[key] = background(zone, season)
            for f in (0, 1):
                out[f"{key}_trees_{f}"] = trees(zone, season, f)
            if zone["id"] == "pasture":
                out[f"{key}_front"] = front(zone, season)
            pano.blit(preview(zone, season), i * W, 0)
        out[f"infei_{season}_panorama"] = pano
    return out
