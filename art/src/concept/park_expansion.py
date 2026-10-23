"""Five connected 342x118 park screens, shared seasons and walking lane.

Left to right: lakeside pavilion, lake promenade, original park, picnic
meadow, woodland picnic clearing. Skyline/shore behind, seats at y=92,
clear gravel path y=94..106, low flowers in front. Light from top left.
Sage foliage, slate roofs, oak wood, muted clay picnic cloths, teal lake.
"""
from __future__ import annotations

import random
import numpy as np
from pixelkit import P, Sprite
import park as PK
import front_yard as FY

W, H = PK.W, PK.H
PREVIEW_SCALE = 4
ZONES = [
    {"id": "gazebo", "name": "湖边凉亭", "bench": 101, "lamp": 197,
     "pond": (224, 72, 114, 15),
     "trees": [("linden", 28, 33, 91, 25, 24), ("cherry", 310, 35, 92, 25, 23), ("maple", 259, 43, 64, 12, 10)]},
    {"id": "lakeside", "name": "湖畔步道", "bench": 90, "lamp": 205,
     "pond": (100, 73, 116, 15),
     "trees": [("linden", 22, 32, 93, 25, 27), ("cherry", 299, 36, 92, 31, 25), ("maple", 235, 42, 66, 13, 12)]},
    {"id": "central", "name": "公园中央", "bench": PK.BENCH, "lamp": PK.LAMP,
     "pond": PK.POND, "trees": PK.TREES},
    {"id": "meadow", "name": "野餐草坪", "bench": 270, "lamp": 228, "pond": None,
     "trees": [("cherry", 37, 35, 91, 30, 25), ("linden", 313, 35, 94, 29, 27), ("maple", 184, 43, 67, 16, 13)]},
    {"id": "grove", "name": "林间野餐区", "bench": 282, "lamp": 117, "pond": None,
     "trees": [("maple", 18, 26, 95, 27, 28), ("linden", 64, 31, 71, 27, 26), ("cherry", 150, 25, 65, 24, 24),
               ("linden", 246, 30, 71, 26, 25), ("maple", 326, 26, 94, 27, 29)]},
]


def lake(s, season, geometry):
    cx, cy, rx, ry = geometry
    water = P.snow if season == "winter" else P.sea
    s.ellipse(cx, cy, rx + 3, ry + 2, P.pave[1])
    s.ellipse(cx, cy - 1, rx + 2, ry + 1, P.pave[3])
    s.ellipse(cx, cy, rx, ry, water[2])
    s.ellipse(cx, cy - 4, rx - 3, ry - 4, water[1])
    rnd = random.Random(71)
    for _ in range(68):
        x = rnd.randint(max(1, cx - rx + 5), min(W - 8, cx + rx - 6))
        y = rnd.randint(cy - ry + 4, cy + ry - 3)
        if ((x - cx) / (rx - 6)) ** 2 + ((y - cy) / (ry - 2)) ** 2 < .86:
            s.hline(x, x + rnd.randint(2, 7), y, water[min(len(water) - 1, rnd.choice((2, 3, 3, 4)))])
    if season == "winter":
        for x in range(max(0, cx - rx + 20), min(W - 8, cx + rx), 39):
            s.line(x, cy - 5, x + 4, cy, P.snow[0]).line(x + 4, cy, x + 13, cy + 2, P.snow[1])
    else:
        for x, y in ((cx - 41, cy + 7), (cx + 39, cy + 8), (cx + 58, cy + 2)):
            s.ellipse(x, y, 4, 1, P.green[2]).hline(x - 2, x, y - 1, P.green[3])
            if season in ("spring", "summer"):
                s.set(x + 1, y - 2, P.blossom[3]).hline(x, x + 2, y - 1, P.blossom[4])
    for x in range(max(0, cx - rx + 5), min(W, cx + rx), 23):
        if abs(x - cx) < rx - 12:
            continue
        for k in range(4):
            y = cy + ry - 2
            s.vline(x + k * 2, y - 6 - k % 3, y, P.sage[1] if season == "winter" else P.green[2])
            s.set(x + k * 2 - 1, y - 3, P.mustard[2])


def pavilion(s):
    # Broad octagonal slate roof, layered eaves and curved upward corners.
    x, y = 101, 19
    s.ellipse(x + 3, 88, 62, 5, P.sage[1])
    for k in range(4):
        s.rect(x - 57 - k * 2, 86 + k * 2, 115 + k * 4, 2, P.pave[3 - k % 2])
        s.hline(x - 57 - k * 2, x + 57 + k * 2, 87 + k * 2, P.pave[1])
    # Back rail, open central bay and wood columns with stone feet.
    for a, b in ((x - 43, x - 23), (x + 24, x + 45)):
        s.rect(a, 71, b - a, 3, P.walnut[2]).hline(a, b, 71, P.oak[3])
        s.hline(a, b, 83, P.walnut[0])
        for xx in range(a + 3, b, 6):
            s.rect(xx, 74, 2, 9, P.walnut[1])
    for xx in (x - 47, x - 24, x + 24, x + 47):
        s.rect(xx - 2, 46, 5, 39, P.walnut[1]).vline(xx - 2, 46, 84, P.oak[3])
        s.rect(xx - 4, 84, 9, 3, P.pave[2]).hline(xx - 4, xx + 4, 84, P.pave[4])
        s.rect(xx - 3, 48, 7, 3, P.oak[1])
    for yy in range(y, 46):
        half = int(5 + (yy - y) * 1.9)
        s.hline(x - half, x + half, yy, P.slate[1 if yy % 5 == 0 else 2])
        s.hline(x - half, x - max(1, half // 3), yy, P.slate[3])
    for dx in (-37, -18, 18, 37):
        s.line(x, y + 2, x + dx, 45, P.slate[1])
    s.hline(x - 59, x + 59, 46, P.slate[0]).hline(x - 61, x + 61, 45, P.slate[3])
    s.hline(x - 56, x + 56, 48, P.walnut[0])
    for side in (-1, 1):
        s.line(x + side * 50, 44, x + side * 62, 40, P.slate[2])
        s.line(x + side * 50, 43, x + side * 62, 39, P.slate[4])
    s.vline(x, y - 7, y, P.slate[0]).rect(x - 2, y - 4, 5, 2, P.slate[3])
    # Two little lanterns tucked under the eaves.
    for xx in (x - 35, x + 35):
        s.vline(xx, 48, 53, P.walnut[0])
        s.rect(xx - 3, 54, 7, 8, P.clay[1]).rect(xx - 2, 55, 5, 5, P.mustard[2])
        s.hline(xx - 2, xx + 2, 54, P.oak[0]).hline(xx - 2, xx + 2, 61, P.oak[0])
        s.vline(xx, 62, 65, P.clay[2])


def bridge(s):
    # A little arched bridge on the far lake bank, outside the walk lane.
    for xx in range(190, 287):
        yy = 79 - round(10 * (1 - ((xx - 238) / 49) ** 2))
        s.vline(xx, yy, yy + 4, P.oak[2]).set(xx, yy, P.oak[4]).set(xx, yy + 4, P.walnut[1])
        s.set(xx, yy - 12, P.walnut[1])
        if xx % 9 == 1:
            s.vline(xx, yy - 12, yy - 1, P.oak[1]).set(xx + 1, yy - 11, P.oak[3])
    s.hline(191, 285, 85, P.pave[1])


def cloth(s, x, y, w=57, h=13, color=None):
    c = color or P.clay
    s.ellipse(x + w // 2 + 2, y + h - 1, w // 2 + 3, 3, P.sage[1])
    s.rect(x, y, w, h, P.linen[2])
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if ((xx - x) // 5 + (yy - y) // 3) % 2 == 0:
                s.set(xx, yy, c[2])
    s.hline(x, x + w - 1, y, P.linen[3]).hline(x, x + w - 1, y + h - 1, c[0])
    for xx in range(x + 1, x + w, 3):
        s.set(xx, y + h, P.linen[2])


def basket(s, x, y):
    s.ellipse(x + 6, y - 3, 5, 5, P.oak[1], fill=False)
    s.rect(x, y, 13, 8, P.oak[1]).rect(x + 1, y, 11, 7, P.oak[3])
    for yy in (y + 2, y + 5):
        s.hline(x + 1, x + 11, yy, P.oak[2])
    for xx in (x + 3, x + 7, x + 10):
        s.vline(xx, y + 1, y + 6, P.oak[1])
    s.hline(x, x + 12, y, P.oak[4])
    s.rect(x + 1, y - 2, 8, 2, P.linen[2]).set(x + 2, y - 3, P.linen[3])


def picnic(s, woodland=False):
    if woodland:
        # An oak picnic table, A-frame legs, two separate long seats.
        for xx in (191, 239):
            s.line(xx, 72, xx - 8, 88, P.walnut[1]).line(xx + 1, 72, xx + 9, 88, P.oak[1])
            s.hline(xx - 8, xx + 9, 85, P.oak[2])
        s.rect(180, 66, 72, 5, P.oak[2]).hline(180, 251, 66, P.oak[4]).hline(180, 251, 70, P.walnut[0])
        for xx in range(183, 249, 9):
            s.vline(xx, 67, 69, P.oak[1])
        s.rect(176, 79, 80, 3, P.oak[3]).hline(176, 255, 82, P.walnut[0])
        for xx in (182, 247):
            s.vline(xx, 82, 89, P.walnut[1])
        s.rect(200, 66, 24, 4, P.clay[2]).hline(200, 223, 66, P.linen[3])
        basket(s, 226, 58)
        s.rect(192, 60, 4, 6, P.teal[2]).hline(192, 195, 59, P.metal[3])
        # Hammock between two trunks, behind the walking path.
        s.line(18, 62, 40, 74, P.oak[1]).line(40, 74, 64, 62, P.oak[1])
        for xx in range(23, 60):
            yy = 66 + round(7 * (1 - ((xx - 41) / 19) ** 2))
            s.vline(xx, yy, yy + 3, P.linen[2]).set(xx, yy, P.sage[3])
    else:
        cloth(s, 91, 76, 69, 14)
        basket(s, 103, 69)
        s.ellipse(137, 80, 8, 2, P.porcelain[3]).ellipse(137, 80, 5, 1, P.mustard[3])
        s.rect(146, 69, 4, 8, P.teal[1]).hline(146, 149, 68, P.metal[4])
        s.rect(124, 76, 3, 4, P.linen[3]).set(127, 77, P.linen[1])
        cloth(s, 195, 78, 45, 10, P.sage)
        basket(s, 215, 72)
        # A folded sun umbrella, generously shaded canvas above the blanket.
        s.vline(211, 47, 77, P.oak[2])
        for yy in range(35, 48):
            half = round((yy - 34) * 1.8)
            s.hline(211 - half, 211 + half, yy, P.linen[3])
            s.hline(211, 211 + half // 2, yy, P.sage[2])
            s.hline(211 - half, 211 - half // 2, yy, P.sage[3])
        s.hline(187, 235, 48, P.sage[0]).set(211, 33, P.oak[1])


def props(zone, season):
    s = Sprite(W, H)
    if zone["id"] == "gazebo":
        pavilion(s)
    elif zone["id"] == "lakeside":
        bridge(s)
    elif zone["id"] in ("meadow", "grove"):
        picnic(s, zone["id"] == "grove")
    PK.bench(s, zone["bench"], 92)
    # Move the existing cast-iron lantern without changing its pixel style.
    lantern = Sprite(W, H)
    PK.lamp(lantern)
    s.blit(lantern.crop(PK.LAMP - 5, 38, 12, 60), zone["lamp"] - 5, 38)
    return s


def background(zone, season):
    if zone["id"] == "central":
        return PK.background(season)
    s = Sprite(W, H)
    PK.sky(s)
    PK.treeline(s, season)
    PK.lawn(s, season)
    if zone["pond"]:
        lake(s, season, zone["pond"])
    PK.path(s, season)
    for kind, x, hw, ht, base in (("hydrangea", 15, 13, 8, 92), ("box", 328, 12, 7, 92)):
        s.blit(FY.bush(kind, x, hw, ht, season, base=base), 0, 0)
    s.blit(props(zone, season), 0, 0)
    PK.border(s, season)
    return s


def trees(zone, season, frame):
    if zone["id"] == "central":
        return PK.trees(season, frame)
    s = Sprite(W, H)
    for kind, x, cy, base, rx, ry in sorted(zone["trees"], key=lambda t: t[3]):
        s.blit(FY.tree(kind, season, frame, at=(x, cy, base, rx, ry)), 0, 0)
    return s


def snow(zone):
    if zone["id"] == "central":
        return PK.snow_layer()
    s = Sprite(W, H)
    # Snow masks protect water, furniture, pavilion and trees.
    solid = props(zone, "winter")
    solid.blit(trees(zone, "winter", 0), 0, 0)
    mask = solid.px[..., 3] > 0
    for y in range(PK.HORIZON, H):
        for x in range(W):
            if mask[y, x]:
                continue
            if zone["pond"]:
                cx, cy, rx, ry = zone["pond"]
                if ((x - cx) / (rx + 4)) ** 2 + ((y - cy) / (ry + 2)) ** 2 < 1:
                    continue
            s.set(x, y, P.snow[1] if 100 <= y <= 104 else P.snow[3])
    ys, xs = np.nonzero(PK.tops(mask))
    for y, x in zip(ys, xs):
        if y > 5:
            s.set(x, y - 1, P.snow[3])
    return s


def lit(zone):
    if zone["id"] == "central":
        return PK.lit()
    s = Sprite(W, H)
    x = zone["lamp"]
    s.rect(x - 2, 46, 6, 5, P.light[0]).rect(x - 1, 47, 4, 3, P.light[1])
    if zone["id"] == "gazebo":
        for xx in (66, 136):
            s.rect(xx - 2, 55, 5, 5, P.light[0]).rect(xx - 1, 56, 3, 3, P.light[1])
    return s


def bench_layer(zone):
    s = Sprite(W, H)
    PK.bench(s, zone["bench"], 92)
    return s


def build():
    out = {}
    for zone in ZONES:
        for season in PK.SEASONS:
            bg = background(zone, season)
            out[f'park_{zone["id"]}_{season}'] = bg
            preview = bg.copy()
            preview.blit(trees(zone, season, 0), 0, 0)
            out[f'park_{zone["id"]}_preview_{season}'] = preview
    return out
