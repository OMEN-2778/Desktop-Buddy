"""公园: a quiet corner of the park, with a walkable path and a bench behind it. Same canvas and scale as the house (342x118).

    sky | a pale city skyline far off | a hazy line of trees
    lawn with mowing stripes; a pond on the right (reeds, lilies, a duck house)
    big maple on the left, linden on the right, two small trees further back
    a hedge, the lamp post, THE BENCH, a bin, along a gravel path
    a flower border at the front

Seasons change the living things like 家门口 (front_yard.py, whose trees and
shrubs this reuses): spring blossom and tulips, summer deep green and lilies,
autumn red and gold with leaves on the path, winter bare branches, a frozen
pond. Snow and rain are overlays; the lamp and the city windows glow at night.

    build() -> park_<season> (background), park_tree_<season>_<0|1> (sway
    frames), park_snow, park_wet, park_lit, duck frames, previews.
"""

from __future__ import annotations

import math
import random

import numpy as np

from pixelkit import P, Sprite

import front_yard as FY

W, H = 342, 118
SEASONS = FY.SEASONS
HORIZON = 58             # where the lawn meets the far trees
PATH = (94, 107)         # gravel path rows
FEET = 103               # walking lane; benches stand behind it
BENCH = 171              # central bench x, behind the walking lane
LAMP = 130
BIN = 214
POND = (276, 75, 54, 10)  # cx, cy, rx, ry
DUCKS = (POND[1] - 3,)   # the water line ducks swim on (page)
TREES = [("linden", 150, 50, 66, 10, 8), ("cherry", 188, 48, 66, 11, 9), ("maple", 302, 47, 64, 10, 8),
         ("linden", 70, 48, 74, 12, 10), ("cherry", 96, 46, 70, 15, 13), ("maple", 238, 42, 63, 13, 11),
         ("maple", 38, 38, 96, 31, 27), ("linden", 316, 36, 98, 28, 25)]   # kind, x, crown y, foot y, rx, ry (back first)
SHRUBS = [("box", 112, 8, 7, 78), ("hydrangea", 126, 9, 8, 80), ("box", 206, 7, 6, 74), ("box", 228, 8, 7, 90),
          ("hydrangea", 250, 10, 8, 92), ("box", 292, 9, 7, 91), ("hydrangea", 62, 10, 9, 95), ("box", 14, 10, 9, 95),
          ("box", 84, 7, 6, 93), ("hydrangea", 336, 9, 8, 96)]          # kind, cx, half width, height, foot y
HEDGE = (140, 204, 80)   # x0, x1, top

G = {"spring": P.leaf_spring, "summer": P.grass, "autumn": P.grass, "winter": P.sage}
FAR = {"spring": [P.mint, P.leaf_spring], "summer": [P.sage, P.green], "autumn": [P.clay, P.mustard, P.sage],
       "winter": [P.oat, P.ash]}
GRAV, ST, IRON = P.oat, P.pave, P.slate


def sky(s):
    S = P.sky_day
    bands = [(0, 14, S[1]), (14, 30, S[2]), (30, HORIZON, S[3])]
    for y0, y1, c in bands:
        s.rect(0, y0, W, y1 - y0, c)
    for y0, a, b in ((14, S[1], S[2]), (30, S[2], S[3])):            # dithered seams, two rows each
        s.dither(0, y0 - 1, W, 1, a, b, "sparse2")
        s.dither(0, y0, W, 1, a, b, "checker")


def skyline(s):
    """Far-off towers, pale with distance; lit windows are in lit()."""
    C = P.sky_soft
    rnd = random.Random(3)
    x = 104
    while x < 230:
        w, h = rnd.randint(9, 16), rnd.randint(10, 26)
        top = HORIZON - 8 - h
        s.rect(x, top, w, HORIZON - top, C[1])
        s.vline(x, top, HORIZON, C[2])                                 # lit left edge
        for yy in range(top + 3, HORIZON - 8, 3):
            for xx in range(x + 2, x + w - 1, 3):
                if rnd.random() < 0.55:
                    s.set(xx, yy, C[0])
        if rnd.random() < 0.3:                                         # an antenna
            s.vline(x + w // 2, top - 4, top - 1, C[1])
        x += w + rnd.randint(-2, 3)


def treeline(s, season):
    rnd = random.Random(7)
    R = FAR[season]
    m = Sprite(W, H)
    for i in range(70):                                                # overlapping crowns, back row first
        cx = rnd.uniform(-6, W + 6)
        r = rnd.uniform(5, 9)
        cy = HORIZON - 2 - r * rnd.uniform(0.4, 0.9)
        A = R[rnd.randrange(len(R))]
        if season == "winter":                                         # bare: twiggy, see-through
            for k in range(14):
                a = rnd.uniform(0.3, 2.8)
                l = rnd.uniform(r * 0.4, r)
                m.line(int(cx), HORIZON - 1, int(cx + math.cos(a) * l), int(cy - math.sin(a) * l * 0.6 + r * 0.3), A[1 + (k % 2)])
            continue
        m.ellipse(cx, cy, r, r * 0.8, A[2])
        m.ellipse(cx - r * 0.3, cy - r * 0.3, r * 0.55, r * 0.45, A[3])
        for _ in range(4):
            m.set(int(cx + rnd.uniform(-r, r) * 0.7), int(cy + rnd.uniform(0, r * 0.6)), A[1])
    s.blit(m, 0, 0)
    s.hline(0, W - 1, HORIZON - 1, R[0][1])


def lawn(s, season):
    R = G[season]
    rnd = random.Random(11)
    for y in range(HORIZON, PATH[0]):                                  # mowing stripes, slanted, wider near us
        for x in range(W):
            band = ((x + (y - HORIZON) * 1.4) // (14 + (y - HORIZON) * 0.4)) % 2
            s.set(x, y, R[3] if band else R[2])
    s.hline(0, W - 1, HORIZON, R[1])
    for _ in range(900):                                               # blades
        x, y = rnd.randrange(W), rnd.randint(HORIZON + 1, PATH[0] - 1)
        s.set(x, y, R[rnd.choice([1, 2, 4])])
    if season in ("spring", "summer"):                                 # daisies, clover
        for _ in range(60):
            x, y = rnd.randrange(W), rnd.randint(HORIZON + 4, PATH[0] - 2)
            s.set(x, y, P.linen[3] if rnd.random() < 0.7 else P.mustard[4])
    if season == "autumn":
        for _ in range(140):
            x, y = rnd.randrange(W), rnd.randint(HORIZON + 2, PATH[0] - 1)
            s.set(x, y, rnd.choice([P.autumn[2], P.autumn[3], P.mustard[3], P.autumn[4]]))


def pond(s, season):
    cx, cy, rx, ry = POND
    rnd = random.Random(13)
    inside = lambda x, y, k=1.0: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= k * k
    frozen = season == "winter"
    Wt = P.snow if frozen else P.sea
    for y in range(cy - ry - 2, cy + ry + 3):
        for x in range(cx - rx - 3, cx + rx + 4):
            if inside(x, y, 1.12) and not inside(x, y):
                s.set(x, y, ST[2] if y < cy else ST[1])                # stone rim
            elif inside(x, y):
                depth = (y - (cy - ry)) / (2 * ry)
                c = Wt[1] if depth < 0.18 else Wt[2] if depth < 0.7 else Wt[3 if frozen else 2]
                s.set(x, y, c)
    for x in range(cx - rx - 3, cx + rx + 4, 3):                       # rim stones
        for y in range(cy - ry - 2, cy + ry + 3):
            if inside(x, y, 1.12) and not inside(x, y):
                s.set(x, y, ST[0] if y > cy else ST[1])
    if frozen:                                                         # ice: cracks and a shine
        for _ in range(7):
            x, y = rnd.randint(cx - rx + 8, cx + rx - 8), rnd.randint(cy - ry + 3, cy + ry - 3)
            for k in range(rnd.randint(4, 9)):
                if inside(x, y, 0.92):
                    s.set(x, y, Wt[1])
                x += rnd.choice([1, 1, 2]); y += rnd.choice([-1, 0, 0, 1])
        for x0 in (cx - 30, cx + 6):
            s.hline(x0, x0 + 10, cy - 3, Wt[3])
    else:                                                              # reflections of the far trees, glints
        for _ in range(26):
            x, y = rnd.randint(cx - rx + 4, cx + rx - 10), rnd.randint(cy - ry + 3, cy + ry - 2)
            if inside(x + 6, y, 0.9) and inside(x, y, 0.9):
                s.hline(x, x + rnd.randint(2, 6), y, Wt[3] if rnd.random() < 0.7 else Wt[4])
        R = FAR[season][0]
        for x in range(cx - rx + 4, cx + rx - 4):
            if rnd.random() < 0.6:
                s.set(x, cy - ry + 1, R[1])
        if season in ("spring", "summer"):                             # lily pads, a flower or two
            for lx, ly in ((cx - 34, cy + 3), (cx - 26, cy + 6), (cx + 22, cy + 4), (cx + 30, cy + 1), (cx - 8, cy + 7)):
                s.ellipse(lx, ly, 2.5, 1, P.green[3]).set(lx + 1, ly, P.green[1]).set(lx - 1, ly - 1, P.green[4])
            if season == "summer":
                for lx, ly in ((cx - 26, cy + 5), (cx + 30, cy)):
                    s.set(lx, ly, P.blossom[3]).set(lx + 1, ly, P.blossom[4]).set(lx, ly - 1, P.blossom[2])
    reeds = P.mustard if season in ("autumn", "winter") else P.green
    for x0, x1 in ((cx - rx - 4, cx - rx + 7), (cx + rx - 12, cx + rx + 1)):   # reeds and cattails
        for x in range(x0, x1):
            if rnd.random() < 0.55:
                h = rnd.randint(4, 10)
                base = cy + int(ry * 0.5) + rnd.randint(-2, 2)
                s.vline(x, base - h, base, reeds[rnd.choice([1, 2, 3])])
                if rnd.random() < 0.25 and season != "winter":
                    s.vline(x, base - h - 2, base - h, P.walnut[1])
    duck_house(s, cx + 18, cy - 2)


def duck_house(s, x, base):
    """A little wooden duck house on a post in the water."""
    Wd = P.oak
    s.vline(x + 3, base - 4, base + 3, Wd[1])
    s.rect(x, base - 10, 8, 6, Wd[2]).vline(x, base - 10, base - 5, Wd[3]).hline(x, x + 7, base - 5, Wd[1])
    s.rect(x + 3, base - 8, 2, 2, Wd[0])                              # the round hole
    for k in range(5):                                                 # red roof
        s.hline(x - 1 + k, x + 8 - k, base - 11 - k, P.coral[2] if k else P.coral[1])
    s.hline(x + 1, x + 4, base - 13, P.coral[3])
    s.hline(x + 1, x + 6, base - 4, Wd[0])                             # its reflection
    s.dither(x + 1, base + 4, 6, 2, P.sea[1], None, "sparse")


def path(s, season):
    y0, y1 = PATH
    rnd = random.Random(17)
    s.rect(0, y0, W, y1 - y0, GRAV[2])
    s.hline(0, W - 1, y0, ST[3]).hline(0, W - 1, y0 + 1, ST[1])       # kerb stones along the back
    for x in range(0, W, 6):
        s.vline(x, y0, y0 + 1, ST[0])
    for _ in range(700):                                               # gravel
        x, y = rnd.randrange(W), rnd.randint(y0 + 2, y1 - 1)
        s.set(x, y, GRAV[rnd.choice([1, 3, 3, 4])])
    s.hline(0, W - 1, y1 - 1, GRAV[1])
    if season == "autumn":
        for _ in range(60):
            x, y = rnd.randrange(W - 1), rnd.randint(y0 + 2, y1 - 1)
            c = rnd.choice([P.autumn[2], P.autumn[3], P.mustard[3], P.autumn[1]])
            s.set(x, y, c).set(x + 1, y, c if rnd.random() < 0.5 else P.autumn[1])
    if season == "spring":
        for _ in range(26):
            x = int(rnd.gauss(96, 22)); y = rnd.randint(y0 + 2, y1 - 1)
            s.set(x, y, rnd.choice([P.blossom[3], P.blossom[4]]))


def border(s, season):
    """The flower border at the front."""
    y0 = PATH[1]
    R = G[season]
    rnd = random.Random(19)
    s.rect(0, y0, W, H - y0, P.walnut[2]).hline(0, W - 1, y0, R[1])
    for x in range(W):
        for k in range(rnd.randint(1, 3)):
            s.set(x, y0 + k, R[rnd.choice([2, 3, 3, 4])])
    for x in range(0, W, 4):
        for k in range(rnd.randint(4, 8)):
            s.set(x + rnd.randint(0, 2), H - 1 - k + rnd.randint(-1, 0), R[rnd.choice([1, 2, 3])])
    flowers = {"spring": [P.coral, P.mustard, P.blossom, P.lilac],          # tulips
               "summer": [P.hydrangea, P.blossom, P.mustard, P.coral],
               "autumn": [P.autumn, P.mustard, P.clay]}.get(season)        # chrysanthemums
    if not flowers:                                                    # winter: holly and berries
        for x in range(3, W, 7):
            y = H - 4 - rnd.randint(0, 2)
            s.ellipse(x, y, 2, 1.5, P.green[1]).set(x - 1, y - 1, P.green[2]).set(x + 1, y, P.coral[2])
        return
    for x in range(2, W, 5):
        F = flowers[(x // 5 + rnd.randint(0, 1)) % len(flowers)]
        y = H - 6 - rnd.randint(0, 3)
        s.vline(x, y + 1, H - 1, R[1])
        if season == "spring":
            s.rect(x - 1, y - 1, 3, 2, F[2]).set(x, y - 2, F[3]).set(x - 1, y - 2, F[2]).set(x + 1, y - 2, F[2]).set(x - 1, y - 1, F[3])
        elif season == "summer":
            s.ellipse(x, y - 1, 1.6, 1.4, F[2]).set(x - 1, y - 2, F[4]).set(x, y - 1, P.mustard[4])
        else:
            s.ellipse(x, y - 1, 1.8, 1.4, F[3]).set(x, y - 1, F[1]).set(x - 1, y - 2, F[4])
        s.set(x + 1, y + 2, R[3]).set(x - 1, y + 3, R[3])


def shrubs(season):
    s = Sprite(W, H)
    for kind, cx, hw, ht, base in sorted(SHRUBS, key=lambda b: b[4]):
        s.blit(FY.bush(kind, cx, hw, ht, season, base=base), 0, 0)
    return s


def hedge(season):
    x0, x1, top = HEDGE
    s = Sprite(W, H)
    for cx in range(x0 + 7, x1 - 4, 11):
        s.blit(FY.bush("box", cx, 9, PATH[0] - top - (cx % 3), season, base=PATH[0] - 1), 0, 0)
    return s


def lamp(s):
    x, b = LAMP, PATH[0] + 1
    s.rect(x - 2, b - 3, 5, 3, IRON[1]).hline(x - 2, x + 2, b - 3, IRON[3])       # foot
    s.vline(x, b - 42, b - 3, IRON[2]).vline(x + 1, b - 42, b - 3, IRON[1])
    s.hline(x - 1, x + 2, b - 30, IRON[3])                             # a collar
    s.set(x - 1, b - 42, IRON[1]).set(x + 2, b - 42, IRON[1])
    top = b - 52                                                       # lantern
    s.rect(x - 3, top + 2, 8, 7, P.glass[0]).frame(x - 3, top + 2, 8, 7, IRON[1])
    s.vline(x + 0, top + 3, top + 7, IRON[1])
    s.rect(x - 1, top + 3, 1, 4, P.linen[1])
    for k in range(3):                                                 # little cap
        s.hline(x - 4 + k, x + 5 - k, top + 1 - k, IRON[2] if k else IRON[1])
    s.set(x + 1, top - 3, IRON[2])
    s.hline(x - 2, x + 3, top + 9, IRON[1])
    return s


def bench(s, cx=BENCH, base=92):
    """A park bench: oak slats on cast-iron ends, seen front-on."""
    Wd, b = P.oak, base
    x0, x1 = cx - 22, cx + 22
    seat = b - 8
    for lx in (x0 + 2, x1 - 3):                                        # iron ends (legs, armrests)
        s.vline(lx, seat, b - 1, IRON[1]).vline(lx + 1, seat + 1, b - 1, IRON[0])
        s.hline(lx - 1, lx + 2, b - 1, IRON[1])
        s.vline(lx, seat - 7, seat, IRON[2])
        s.hline(lx - 1, lx + 2, seat - 7, IRON[3]).set(lx + 2, seat - 6, IRON[1])
    for k, y in enumerate((b - 26, b - 22, b - 18)):                   # backrest slats
        s.rect(x0 + 1, y, x1 - x0 - 1, 3, Wd[2]).hline(x0 + 1, x1 - 1, y, Wd[3]).hline(x0 + 1, x1 - 1, y + 2, Wd[1])
        s.set(x0 + 1, y + 1, Wd[1]).set(x1 - 1, y + 1, Wd[1])
    for lx in (x0 + 4, x1 - 5):                                        # backrest posts
        s.vline(lx, b - 27, seat, IRON[1])
    s.rect(x0, seat - 1, x1 - x0 + 1, 3, Wd[3]).hline(x0, x1, seat - 1, Wd[4]).hline(x0, x1, seat + 1, Wd[1])   # seat
    s.hline(x0 + 1, x1 - 1, seat + 2, Wd[0])
    s.dither(x0 + 3, b, x1 - x0 - 5, 1, GRAV[1], None, "checker")      # shadow on the gravel


def bin_(s):
    x, b = BIN, FEET - 1
    s.rect(x - 4, b - 13, 9, 13, P.teal[2]).vline(x - 4, b - 13, b - 1, P.teal[3]).vline(x + 4, b - 13, b - 1, P.teal[1])
    for xx in range(x - 3, x + 4, 2):
        s.vline(xx, b - 11, b - 2, P.teal[1])
    s.rect(x - 5, b - 15, 11, 2, P.teal[3]).hline(x - 5, x + 5, b - 15, P.teal[4]).hline(x - 4, x + 4, b - 13, P.teal[0])
    s.dither(x - 3, b, 9, 1, GRAV[1], None, "checker")


def tree_at(i, season, frame):
    kind, x, cy, base, rx, ry = TREES[i]
    return FY.tree(kind, season, frame, at=(x, cy, base, rx, ry))


def background(season):
    s = Sprite(W, H)
    sky(s)
    skyline(s)
    treeline(s, season)
    lawn(s, season)
    pond(s, season)
    path(s, season)
    s.blit(shrubs(season), 0, 0)
    s.blit(hedge(season), 0, 0)
    lamp(s)
    bench(s)
    bin_(s)
    border(s, season)
    return s


def trees(season, frame):
    s = Sprite(W, H)
    for i in range(len(TREES)):
        s.blit(tree_at(i, season, frame), 0, 0)
    return s


def snow_layer():
    S = P.snow
    s = Sprite(W, H)
    rnd = random.Random(23)
    s.rect(0, HORIZON, W, PATH[0] - HORIZON, S[2])                     # the lawn under snow
    for x in range(W):
        if rnd.random() < 0.3:
            s.set(x, rnd.randint(HORIZON + 2, PATH[0] - 1), S[3])
    cx, cy, rx, ry = POND                                              # (the pond ices over by itself)
    for y in range(HORIZON, PATH[0]):
        for x in range(cx - rx - 4, cx + rx + 5):
            if ((x - cx) / (rx + 3)) ** 2 + ((y - cy) / (ry + 2)) ** 2 <= 1:
                s.px[y, x] = 0
    s.hline(0, W - 1, HORIZON, S[3])
    s.rect(0, PATH[0], W, PATH[1] - PATH[0], S[3])                     # the path, a trodden lane
    s.rect(0, FEET - 3, W, 4, S[1]).hline(0, W - 1, FEET - 3, S[0])
    for x in range(3, W, 8):
        s.hline(x, x + 1, FEET - 2 + (x // 8) % 2, S[0])
    s.rect(0, PATH[1], W, H - PATH[1], S[3])                           # the border
    for x in range(0, W, 3):
        s.set(x, PATH[1] + rnd.randint(2, 9), S[2])
    parts = Sprite(W, H)
    parts.blit(shrubs("winter"), 0, 0)
    parts.blit(hedge("winter"), 0, 0)
    lamp(parts)
    bench(parts)
    bin_(parts)
    for i in range(len(TREES)):
        parts.blit(tree_at(i, "winter", 0), 0, 0)
    solid = parts.px[..., 3] == 255
    solid[FEET:FEET + 1] = False                                       # (shadows aren't solid)
    s.px[solid & (np.arange(H)[:, None] >= HORIZON)] = 0               # what stands in the snow stays clear of it
    treeline(parts, "winter")
    m = parts.px[..., 3] > 0
    ys, xs = np.nonzero(tops(m))
    for x, y in zip(xs, ys):
        if y < PATH[0] + 1:
            s.set(x, y - 1, S[3]).set(x, y, S[3] if rnd.random() < 0.7 else S[2])
    return s


def tops(mask):
    up = np.zeros_like(mask)
    up[1:] = mask[:-1]
    return mask & ~up


def wet_layer():
    """Rain: the gravel darkens, puddles mirror the sky."""
    s = Sprite(W, H)
    rnd = random.Random(29)
    y0, y1 = PATH
    for _ in range(900):
        s.set(rnd.randrange(W), rnd.randint(y0 + 2, y1 - 1), GRAV[1])
    for x0, w in ((14, 26), (92, 16), (226, 30), (300, 18)):
        y = rnd.randint(y0 + 4, y1 - 3)
        for xx in range(x0, x0 + w):
            d = abs(xx - (x0 + w / 2)) / (w / 2)
            s.set(xx, y, P.sky_day[1])
            if d < 0.7:
                s.set(xx, y + 1, GRAV[0])
        s.hline(x0 + w // 4, x0 + w // 2, y, P.sky_day[3])
    return s


def lit():
    """Night: the lantern (emissive) and lit windows in the far towers."""
    s = Sprite(W, H)
    x, top = LAMP, PATH[0] + 1 - 52
    s.rect(x - 2, top + 3, 6, 5, P.light[0]).rect(x - 1, top + 4, 4, 3, P.light[1])
    rnd = random.Random(31)
    dark = tuple(int(P.sky_soft[0][i:i + 2], 16) for i in (1, 3, 5))
    refs = [background(se).px for se in SEASONS]                      # windows the trees hide in no season
    for y in range(20, HORIZON - 8):
        for xx in range(104, 232):
            if all(tuple(r[y, xx][:3]) == dark for r in refs) and rnd.random() < 0.45:
                s.set(xx, y, P.light[0])
    return s


def bench_layer():
    """The bench alone: the page draws it over people walking behind it."""
    s = Sprite(W, H)
    bench(s)
    return s


def plane():
    """A far-off airliner, a few pixels long (the page adds the contrail)."""
    s = Sprite(9, 4)
    s.hline(1, 7, 2, P.linen[3]).set(8, 2, P.linen[2]).hline(1, 2, 1, P.linen[2]).set(1, 0, P.linen[2])
    s.hline(3, 5, 3, P.pave[2]).set(4, 1, P.pave[3])
    return s


def duck(frame):
    """A mallard paddling: 0/1 bob, 2 dipping its head."""
    s = Sprite(10, 7)
    body, head = P.oat, P.green
    dy = 1 if frame == 1 else 0
    s.ellipse(4, 4 + dy, 4, 1.8, body[2]).hline(1, 6, 3 + dy, body[3]).set(0, 3 + dy, body[1])
    s.hline(2, 6, 5 + dy, body[1])
    s.set(4, 4 + dy, P.walnut[2]).set(5, 4 + dy, P.walnut[2])                # wing
    if frame == 2:                                                     # head down
        s.rect(7, 4, 2, 2, head[2]).set(9, 5, P.mustard[3])
    else:
        s.rect(7, 1 + dy, 2, 2, head[2]).set(7, 1 + dy, head[3]).set(8, 2 + dy, P.ink[0])
        s.set(9, 2 + dy, P.mustard[3]).set(7, 3 + dy, P.linen[3])
    s.hline(1, 7, 6, P.sea[3])                                         # ripple
    return s


def scene(season="summer", frame=0):
    s = background(season)
    s.blit(trees(season, frame), 0, 0)
    return s


def build():
    out = {}
    for se in SEASONS:
        out[f"park_{se}"] = background(se)
        for f in (0, 1):
            out[f"park_tree_{se}_{f}"] = trees(se, f)
        out[f"park_preview_{se}"] = scene(se)
    out["park_snow"] = snow_layer()
    out["park_wet"] = wet_layer()
    out["park_lit"] = lit()
    snowy = scene("winter")
    snowy.blit(out["park_snow"], 0, 0)
    out["park_preview_snow"] = snowy
    sheet = Sprite(34, 7)
    for i in range(3):
        sheet.blit(duck(i), i * 12, 0)
    out["park_ducks"] = sheet
    return out


PREVIEW_SCALE = 4
