"""夏日海岛 (Hawaiian-style summer getaway), shore part: art only, not in the game.
Two connected 342x118 screens at the house scale (1px ≈ 6cm, Buddy 20x28),
light from the top left, the same walking lane height as the other outdoor
places (feet y=103):

    lodge   旅舍     a small plantation-style cottage (the hostel) on lava-rock
                     piers: tin hip roof, lanai with rattan chairs, surfboards,
                     palms, hibiscus and plumeria, a volcanic ridge behind
    cabana  更衣室   a thatched changing hut with two curtained doors (bikini /
                     wetsuit), gear rack, outdoor shower, outrigger canoe; the
                     sand runs down into the water and a pier leads out: walking
                     off the right edge goes to the dive map (summer_sea.py)

Plus the lodge inside (compact: living room, kitchen, bath, bedroom) and live
layers (palm sway frames). Owner decisions and hand-off: docs/SUMMER_SEA.md.
"""
from __future__ import annotations

import math
import random

import numpy as np

from pixelkit import P, Sprite

import house as HS
import friend_houses as FH

W, H = 342, 118
PREVIEW_SCALE = 4
HORIZON = 54
LANE = (94, 107)          # sand path rows; feet at 103
FEET = 103
LODGE = (96, 232)         # cottage x0, x1
LODGE_DOOR = 164
CABANA = (70, 168)
CABANA_DOORS = {"bikini": 96, "wetsuit": 142}
PIER = (228, 342)

S = P.sand
WOOD = P.ash
LEAF = P.green
LEAF2 = P.grass


# ------------------------------------------------------------- sky, sea, ridge

def sky(s):
    R = P.sky_day
    for y in range(HORIZON):
        t = y / HORIZON
        c = R[1] if t < 0.3 else R[2] if t < 0.65 else R[3]
        s.hline(0, W - 1, y, c)
    for y0, a, b in ((int(HORIZON * 0.3), R[1], R[2]), (int(HORIZON * 0.65), R[2], R[3])):
        s.dither(0, y0 - 1, W, 2, a, b, "checker")


def clouds(s, seed):
    rnd = random.Random(seed)
    for _ in range(3):
        x, y = rnd.randint(10, W - 50), rnd.randint(6, 26)
        for dx, r in ((0, 5), (7, 8), (17, 7), (25, 4)):
            s.ellipse(x + dx, y, r, r * 0.6, P.porcelain[3])
        s.hline(x - 4, x + 28, y + 3, P.sky_day[3]).hline(x + 2, x + 24, y + 4, P.porcelain[2])


def ridge(s, x0, x1, peak, seed):
    """A lush volcanic ridge (pali): steep, deeply fluted green slopes,
    hazy with distance, a cloud cap on the summit."""
    rnd = random.Random(seed)
    top = []
    for x in range(W):
        if x0 <= x <= x1:
            u = (x - x0) / (x1 - x0)
            h = peak * math.sin(math.pi * u) ** 0.8
            h += 2.5 * math.sin(x * 0.11) + 1.2 * math.sin(x * 0.27 + 1)
            top.append(int(HORIZON - 2 - h))
        else:
            top.append(HORIZON)
    for x in range(W):
        if top[x] >= HORIZON:
            continue
        for y in range(top[x], HORIZON):
            fl = math.sin(x * 0.55 + (y - top[x]) * 0.08)        # vertical flutes
            c = P.mint[2] if fl > 0.3 else P.mint[1] if fl < -0.4 else P.teal[3]
            if y - top[x] < 2:
                c = P.mint[3]
            s.set(x, y, c)
    for _ in range(18):                                            # a few tree crowns on the lower slopes
        x = rnd.randint(max(0, x0 + 10), min(W - 1, x1 - 10))
        y = HORIZON - rnd.randint(2, 8)
        if top[x] < y:
            s.ellipse(x, y, 2.5, 1.6, P.green[2]).set(x - 1, y - 1, P.green[3])
    cx = min(W - 30, (x0 + x1) // 2)
    for dx, r in ((-10, 6), (0, 9), (11, 6)):                      # cloud cap
        s.ellipse(cx + dx, HORIZON - 2 - peak + 2, r, r * 0.45, P.porcelain[3])


def sea(s, x0=0, x1=W, y0=HORIZON, y1=72):
    R = P.sea
    rnd = random.Random(5)
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        c = R[2] if t < 0.25 else R[3] if t < 0.7 else P.teal[4]
        s.hline(x0, x1 - 1, y, c)
    s.hline(x0, x1 - 1, y0, R[1])
    for _ in range((x1 - x0) // 3):
        x, y = rnd.randint(x0, x1 - 6), rnd.randint(y0 + 2, y1 - 2)
        s.hline(x, x + rnd.randint(1, 4), y, R[4] if rnd.random() < 0.6 else R[3])


def beach(s, top=72):
    """Golden sand from the waterline to the lane, a foam line, shells."""
    rnd = random.Random(7)
    s.rect(0, top, W, LANE[0] - top, S[3])
    for y in range(top, top + 3):
        for x in range(W):
            if (x + y * 3) % 7 < 4:
                s.set(x, y, P.porcelain[3] if y == top else S[4])   # foam lace
    s.hline(0, W - 1, top + 3, S[2])                                # wet sand edge
    for _ in range(400):
        x, y = rnd.randrange(W), rnd.randint(top + 4, LANE[0] - 1)
        s.set(x, y, S[rnd.choice((2, 4, 4))])
    for _ in range(14):
        x, y = rnd.randrange(W - 2), rnd.randint(top + 6, LANE[0] - 2)
        C = rnd.choice((P.coral, P.blossom, P.porcelain + [P.porcelain[3]]))
        s.set(x, y, C[3]).set(x + 1, y, C[2])


def lane(s):
    """The walking lane: packed sand with footprints, edged by a line of
    lava stones at the back."""
    y0, y1 = LANE
    rnd = random.Random(9)
    s.rect(0, y0, W, y1 - y0, S[2])
    for _ in range(500):
        s.set(rnd.randrange(W), rnd.randint(y0, y1 - 1), S[rnd.choice((1, 3, 3))])
    for x in range(4, W, 11):                                       # footprints
        y = y0 + 4 + (x // 11) % 2 * 4
        s.set(x, y, S[1]).set(x + 1, y, S[1]).set(x, y + 1, S[1])
    for x in range(0, W, 5):                                        # lava stones along the back
        r = 2 + (x * 7) % 3 * 0.5
        s.ellipse(x + 2, y0, r, 1.5, P.slate[1]).set(x + 1, y0 - 1, P.slate[3])
    s.hline(0, W - 1, y1 - 1, S[1])


# ------------------------------------------------------------- plants

def palm(s, x, base, h, lean=1, frame=0, seed=0):
    """A coconut palm: a curving ringed trunk and arching fronds, lit from
    the top left; frame 1 lets the frond tips sway a pixel."""
    rnd = random.Random(seed)
    pts = []
    for i in range(h):
        t = i / h
        px = x + lean * (t ** 2) * h * 0.35
        pts.append((px, base - i))
    for i, (px, py) in enumerate(pts):                              # trunk, 4px, rings every 3
        w = 4 if i < h * 0.7 else 3
        for k in range(w):
            c = WOOD[3] if k == 0 else WOOD[1] if k == w - 1 else WOOD[2]
            if i % 3 == 0:
                c = WOOD[1] if k else WOOD[2]
            s.set(int(px) - w // 2 + k, int(py), c)
    tx, ty = pts[-1]
    tx, ty = int(tx), int(ty)
    for k in range(3):                                              # coconuts
        s.ellipse(tx - 2 + k * 2, ty + 3, 1.6, 1.6, P.walnut[2]).set(tx - 2 + k * 2, ty + 2, P.walnut[3])
    sway = 1 if frame else 0
    for a, L in ((-2.9, 20), (-2.4, 22), (-1.9, 17), (-0.3, 20), (-0.75, 22), (-1.25, 17), (-1.57, 12), (-3.3, 15), (0.15, 15)):
        a += rnd.uniform(-0.08, 0.08)
        for j in range(L):
            t = j / L
            ang = a + 0.9 * t * (1 if math.cos(a) > 0 else -1) * (0.6 if abs(math.cos(a)) > 0.3 else 0.2)
            fx = tx + math.cos(a) * j
            fy = ty + math.sin(a) * j + (t ** 2) * L * 0.55
            if t > 0.7:
                fx += sway
            light = 3 if math.sin(a) < -0.5 else 2
            s.set(int(fx), int(fy), LEAF[light])
            if j % 2 == 0 and j > 2:                                # leaflets hanging off the rib
                for d in range(1, 3 + int(2 * (1 - abs(t - 0.4)))):
                    s.set(int(fx) + (1 if math.cos(a) > 0 else -1) * (d // 2), int(fy) + d, LEAF[light - (d > 2)])
    s.ellipse(tx, ty, 2.5, 2, LEAF[3])


def hibiscus(s, cx, base, hw=10, ht=9, F=P.coral):
    rnd = random.Random(cx)
    for _ in range(int(hw * 2.4)):
        u = rnd.uniform(-1, 1)
        v = rnd.uniform(0, 1) * math.sqrt(max(0, 1 - u * u))
        x, y = cx + u * (hw - 2), base - v * (ht - 2)
        light = -u * 0.5 + v * 0.9
        t = 1 if light < 0.1 else 2 if light < 0.5 else 3 if light < 0.85 else 4
        s.ellipse(x, y, 2.6, 2.2, LEAF[t])
    for _ in range(hw // 2):                                        # big flowers: five petals, yellow stamen
        u, v = rnd.uniform(-0.8, 0.8), rnd.uniform(0.2, 0.9)
        x, y = int(cx + u * (hw - 3)), int(base - v * (ht - 3))
        s.rect(x - 1, y - 1, 3, 3, F[2]).set(x, y - 2, F[3]).set(x - 2, y, F[3]).set(x + 2, y, F[1]).set(x, y + 2, F[1])
        s.set(x, y, P.mustard[4]).set(x - 1, y - 1, F[4])


def plumeria(s, x, base, h=26):
    """A small frangipani tree: forked grey branches, leaf rosettes, white and
    yellow flowers."""
    s.vline(x, base - h, base, P.ash[1]).vline(x + 1, base - h, base, P.ash[2])
    for dx, dy in ((-7, -h - 4), (6, -h - 2), (-2, -h - 8)):
        s.line(x, base - h + 4, x + dx, base + dy + 2, P.ash[2])
        cx, cy = x + dx, base + dy
        for k in range(6):
            a = k * math.pi / 3
            s.line(cx, cy, int(cx + math.cos(a) * 4), int(cy + math.sin(a) * 2.5), LEAF[2 + (k % 2)])
        for fx, fy in ((cx - 1, cy - 2), (cx + 2, cy - 1)):
            s.set(fx, fy, P.porcelain[3]).set(fx + 1, fy, P.porcelain[3]).set(fx, fy + 1, P.porcelain[3]).set(fx + 1, fy + 1, P.mustard[4])


def ti_plants(s, x, base):
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.35
        for j in range(9):
            s.set(int(x + math.cos(a) * j), int(base + math.sin(a) * j), (P.green[2], P.coral[1], P.green[3])[k % 3])


def tropical_border(s, seed):
    """Below the lane: ferns, ti leaves and small hibiscus, close to us."""
    rnd = random.Random(seed)
    s.rect(0, LANE[1], W, H - LANE[1], S[1])
    x = -4
    while x < W + 4:
        kind = rnd.random()
        if kind < 0.45:                                             # fern fronds
            for k in range(5):
                a = -math.pi / 2 + (k - 2) * 0.5
                for j in range(8):
                    px, py = int(x + math.cos(a) * j), int(H + 1 + math.sin(a) * j)
                    s.set(px, py, LEAF[2 + (j % 2)])
                    if j % 2:
                        s.set(px + 1, py + 1, LEAF[1])
        elif kind < 0.75:
            ti_plants(s, x, H + 1)
        else:
            hibiscus(s, x, H + 2, 8, 9, rnd.choice((P.coral, P.blossom, P.mustard)))
        x += rnd.randint(7, 12)


# ------------------------------------------------------------- lodge (the hostel)

def lodge(s):
    """A plantation-style cottage on lava-rock piers: pale green board-and-
    batten walls, white trim, a red corrugated tin hip roof, a lanai with
    white posts and railing, louvred windows, a screen door, rattan chairs,
    surfboards and a ukulele, a lei on the post, a koa sign board."""
    x0, x1 = LODGE
    floor = LANE[0] - 8
    wall_top = floor - 30
    R = P.clay
    # roof: hip roof with corrugations, overhanging the lanai
    for k in range(18):
        a, b = x0 - 8 + k, x1 + 8 - k
        y = wall_top - 2 - k
        s.hline(a, b, y, R[2] if k % 2 else R[3])
        for x in range(a, b, 3):
            s.set(x, y, R[1])
        s.set(a, y, R[1]).set(b, y, R[0])
    s.hline(x0 - 9, x1 + 9, wall_top - 1, R[1]).hline(x0 - 9, x1 + 9, wall_top, P.porcelain[3])
    s.rect((x0 + x1) // 2 - 6, wall_top - 26, 13, 7, P.mint[3]).hline((x0 + x1) // 2 - 6, (x0 + x1) // 2 + 6, wall_top - 26, R[3])   # little vent dormer
    for xx in range((x0 + x1) // 2 - 4, (x0 + x1) // 2 + 5, 2):
        s.vline(xx, wall_top - 25, wall_top - 21, P.mint[1])
    # walls
    Wl = P.mint
    s.rect(x0, wall_top + 1, x1 - x0, floor - wall_top - 1, Wl[3])
    for x in range(x0 + 2, x1, 4):
        s.vline(x, wall_top + 1, floor - 1, Wl[2])
    s.vline(x0, wall_top + 1, floor - 1, P.porcelain[3]).vline(x1 - 1, wall_top + 1, floor - 1, P.porcelain[2])
    s.hline(x0, x1 - 1, wall_top + 1, Wl[1])                        # shade under the eave
    for wx in (x0 + 12, x0 + 38, x1 - 54, x1 - 28):                 # louvred windows with white trim
        if abs(wx + 7 - LODGE_DOOR) < 14:
            continue
        s.rect(wx - 1, wall_top + 7, 16, 15, P.porcelain[3])
        s.rect(wx + 1, wall_top + 9, 12, 11, P.glass[1])
        for y in range(wall_top + 9, wall_top + 20, 2):
            s.hline(wx + 1, wx + 12, y, P.glass[3] if y % 4 == 1 else P.glass[2])
        s.vline(wx + 7, wall_top + 9, wall_top + 19, P.porcelain[2])
        s.rect(wx - 2, wall_top + 22, 18, 2, P.porcelain[3]).hline(wx - 2, wx + 15, wall_top + 23, P.porcelain[1])
        hb = wall_top + 24                                          # window box with orchids
        s.rect(wx - 1, hb, 16, 3, WOOD[2]).hline(wx - 1, wx + 14, hb, WOOD[3])
        for k in range(0, 16, 2):
            s.set(wx - 1 + k, hb - 1, LEAF[2]).set(wx + k, hb - 2, (P.lilac, P.blossom, P.porcelain + [P.porcelain[3]])[k % 3][3])
    dx = LODGE_DOOR - 7                                             # screen door
    s.rect(dx - 1, wall_top + 5, 16, floor - wall_top - 5, P.porcelain[3])
    s.rect(dx + 1, wall_top + 7, 12, floor - wall_top - 7, P.teal[2])
    s.rect(dx + 2, wall_top + 8, 10, 12, P.slate[1]).hline(dx + 2, dx + 11, wall_top + 8, P.slate[2])
    s.hline(dx + 1, dx + 12, wall_top + 21, P.porcelain[3]).set(dx + 11, wall_top + 24, P.mustard[3])
    # sign board over the door: a koa plank with a carved hibiscus
    s.rect(dx - 6, wall_top + 1, 26, 4, P.walnut[2]).hline(dx - 6, dx + 19, wall_top + 1, P.walnut[3])
    s.rect(dx + 5, wall_top + 2, 3, 2, P.coral[3]).set(dx + 6, wall_top + 2, P.mustard[4])
    # lanai: deck, posts, railing, steps
    s.rect(x0 - 6, floor, x1 - x0 + 12, 3, WOOD[3]).hline(x0 - 6, x1 + 5, floor, WOOD[4]).hline(x0 - 6, x1 + 5, floor + 2, WOOD[1])
    for px in range(x0 - 5, x1 + 6, 22):
        s.rect(px, wall_top + 1, 3, floor - wall_top - 1, P.porcelain[3]).vline(px + 2, wall_top + 1, floor - 1, P.porcelain[1])
    for x in range(x0 - 5, x1 + 6):
        if abs(x - LODGE_DOOR) < 9:
            continue
        s.set(x, floor - 10, P.porcelain[3]).set(x, floor - 9, P.porcelain[1])
        if x % 3 == 0:
            s.vline(x, floor - 8, floor - 1, P.porcelain[2])
    for k in range(3):
        s.rect(dx - 2 + k, floor + 3 + k * 2, 18 - 2 * k, 2, WOOD[3]).hline(dx - 2 + k, dx + 15 - k, floor + 3 + k * 2, WOOD[4])
    # lava-rock piers and lattice skirt
    for px in range(x0 - 4, x1 + 4, 18):
        s.rect(px, floor + 3, 6, LANE[0] - floor - 3, P.slate[1]).set(px + 1, floor + 4, P.slate[3]).set(px + 3, floor + 6, P.slate[2])
    for x in range(x0, x1):
        for y in range(floor + 3, LANE[0] - 1):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                if not any(px <= x < px + 6 for px in range(x0 - 4, x1 + 4, 18)):
                    s.set(x, y, WOOD[2])
    # rattan chairs, a little table with a pineapple, surfboards, ukulele, lei
    for cx in (x0 + 6, x1 - 22):
        s.rect(cx, floor - 9, 14, 3, P.oak[3]).hline(cx, cx + 13, floor - 9, P.oak[4])
        for k in range(10):
            s.set(cx + k // 2, floor - 12 - k, P.oak[2])
        s.ellipse(cx + 3, floor - 15, 4, 6, P.oak[3])
        s.rect(cx + 4, floor - 11, 8, 2, P.coral[2]).set(cx + 6, floor - 11, P.mustard[4])   # cushion with a flower print
        s.vline(cx + 1, floor - 6, floor - 1, P.oak[1]).vline(cx + 12, floor - 6, floor - 1, P.oak[1])
    tx = x0 + 24
    s.rect(tx, floor - 8, 8, 2, WOOD[3]).vline(tx + 3, floor - 6, floor - 1, WOOD[1])
    s.ellipse(tx + 4, floor - 11, 2, 2.5, P.mustard[3]).set(tx + 3, floor - 12, P.mustard[4])
    for k in range(3):
        s.set(tx + 3 + k, floor - 14 - (k % 2), LEAF[3])
    for k, (bx, C) in enumerate(((x1 + 10, P.coral), (x1 + 16, P.hydrangea), (x1 + 22, P.mustard))):   # surfboards
        for y in range(floor - 34 + k * 3, LANE[0] - 1):
            t = (y - (floor - 34 + k * 3)) / 38
            hw = int(2.6 * math.sin(math.pi * min(1, t * 1.05)) + 0.5)
            s.hline(bx - hw, bx + hw, y, C[2])
            s.set(bx - hw, y, C[3]).set(bx + hw, y, C[1])
        s.vline(bx, floor - 30 + k * 3, LANE[0] - 3, P.porcelain[3])
    ux = dx + 19
    s.ellipse(ux, floor - 14, 2.5, 3, P.walnut[3]).vline(ux, floor - 24, floor - 16, P.walnut[1]).set(ux, floor - 14, P.walnut[0])
    for k in range(9):                                              # lei draped on a post
        a = math.pi * k / 8
        s.set(x0 - 4 + int(4 * math.cos(a)), wall_top + 10 + int(4 * math.sin(a)), (P.coral, P.mustard, P.blossom)[k % 3][3])


def tiki_torch(s, x, base):
    s.vline(x, base - 20, base, P.walnut[2]).vline(x + 1, base - 20, base, P.walnut[1])
    for y in range(base - 20, base, 4):
        s.hline(x, x + 1, y, P.oat[2])
    s.rect(x - 1, base - 24, 4, 4, P.oak[3]).hline(x - 1, x + 2, base - 24, P.oak[4])


def mailbox_sign(s, x, base):
    """A surfboard-shaped direction sign: 旅舍 ← · → 潜水 (icons only)."""
    s.vline(x + 5, base - 18, base, WOOD[2])
    for k, (dy, C, d) in enumerate(((-18, P.coral, -1), (-12, P.sea, 1))):
        y = base + dy
        s.rect(x, y, 12, 4, C[3]).hline(x, x + 11, y, C[4]).set(x - 1 if d < 0 else x + 12, y + 1, C[3]).set(x - 1 if d < 0 else x + 12, y + 2, C[3])


# ------------------------------------------------------------- cabana (changing hut) and pier

def thatch(s, x0, x1, top, eave):
    """A pili-grass thatched roof: long straw strokes, a ragged eave."""
    T = P.mustard
    rnd = random.Random(x0)
    for y in range(top, eave + 1):
        t = (y - top) / max(1, eave - top)
        a, b = int((x0 + x1) / 2 - (x1 - x0) / 2 * (0.25 + 0.75 * t)), int((x0 + x1) / 2 + (x1 - x0) / 2 * (0.25 + 0.75 * t))
        for x in range(a, b + 1):
            c = T[2] if (x + y // 2) % 3 else T[1]
            if y - top < 2 or (x - a) < 2:
                c = T[3]
            s.set(x, y, c)
    for x in range(x0, x1 + 1):
        for k in range(rnd.randint(1, 3)):
            s.set(x, eave + 1 + k, T[1 + (k == 0)])
    s.rect((x0 + x1) // 2 - 6, top - 2, 12, 3, P.walnut[2])


def cabana(s):
    """The changing hut: bamboo walls under a thatch roof, two curtained
    doorways with signs (a bikini top / a mask-and-snorkel), a gear rack with
    wetsuits and fins, an outdoor shower, towels drying."""
    x0, x1 = CABANA
    base = LANE[0] - 1
    top = base - 34
    B = P.oak
    s.rect(x0, top, x1 - x0, base - top, B[2])
    for x in range(x0, x1, 3):                                      # bamboo poles with nodes
        s.vline(x, top, base - 1, B[3]).vline(x + 2, top, base - 1, B[1])
        for y in range(top + (x % 5), base, 7):
            s.hline(x, x + 2, y, B[1])
    thatch(s, x0 - 10, x1 + 10, top - 22, top + 2)
    for key, cx in CABANA_DOORS.items():
        C = P.coral if key == "bikini" else P.hydrangea
        s.rect(cx - 9, base - 26, 18, 26, P.walnut[0])
        for x in range(cx - 8, cx + 9):                             # curtain with folds
            c = C[3] if (x - cx) % 4 in (0, 1) else C[2]
            s.vline(x, base - 25, base - 2, c)
        for x in range(cx - 8, cx + 9, 2):
            s.set(x, base - 2, C[1])
        s.hline(cx - 9, cx + 9, base - 26, P.walnut[2])
        sy = base - 33                                              # the sign: a round koa plaque
        s.ellipse(cx, sy, 5, 4, P.walnut[3]).ellipse(cx, sy, 4, 3, P.oat[3])
        if key == "bikini":
            s.rect(cx - 3, sy - 1, 2, 2, C[2]).rect(cx + 1, sy - 1, 2, 2, C[2]).hline(cx - 1, cx, sy - 1, C[1]).set(cx - 4, sy - 2, C[1]).set(cx + 3, sy - 2, C[1])
        else:
            s.rect(cx - 3, sy - 1, 6, 2, P.slate[2]).set(cx - 2, sy - 1, P.glass[3]).set(cx + 1, sy - 1, P.glass[3]).vline(cx + 3, sy - 4, sy, P.mustard[3])
    rx = x1 + 6                                                     # gear rack
    s.vline(rx, base - 30, base, P.walnut[2]).vline(rx + 22, base - 30, base, P.walnut[2]).hline(rx, rx + 22, base - 29, P.walnut[3])
    for k, C in enumerate((P.slate, P.hydrangea, P.slate)):
        wx = rx + 3 + k * 7
        s.rect(wx, base - 28, 5, 9, C[1]).rect(wx + 1, base - 19, 1, 8, C[1]).rect(wx + 3, base - 19, 1, 8, C[1])
        s.vline(wx, base - 28, base - 20, C[2]).set(wx + 2, base - 27, P.mustard[3])
    for k, C in enumerate((P.mustard, P.coral)):                     # fins standing in the sand
        fx = rx + 3 + k * 9
        s.rect(fx, base - 9, 4, 9, C[2]).hline(fx, fx + 3, base - 9, C[3]).set(fx + 1, base - 5, C[1])
    shx = x0 - 22                                                   # outdoor shower
    s.vline(shx, base - 34, base, P.steel[2]).vline(shx + 1, base - 34, base, P.steel[3])
    s.hline(shx, shx + 7, base - 34, P.steel[2]).rect(shx + 6, base - 34, 4, 2, P.steel[3])
    for k in range(4):
        s.set(shx + 6 + k, base - 30 + k * 3, P.glass[3])
    s.rect(shx - 6, base - 2, 18, 2, WOOD[3])                       # slatted mat
    for x in range(x0 + 4, x1 - 4, 30):                             # towels on the line
        pass


def canoe(s, x, base):
    """An outrigger canoe pulled up on the sand."""
    L = 46
    for i in range(L):
        t = i / L
        d = int(3 * math.sin(math.pi * t) + 1)
        s.vline(x + i, base - d - 1, base - 1, P.walnut[2])
        s.set(x + i, base - d - 1, P.walnut[3])
    s.hline(x, x + L - 1, base - 1, P.walnut[1])
    s.set(x - 1, base - 3, P.walnut[3]).set(x + L, base - 3, P.walnut[3])
    for k in (12, 32):                                              # booms out to the float
        s.line(x + k, base - 4, x + k + 4, base - 9, WOOD[2])
    s.rect(x + 10, base - 10, 28, 2, WOOD[3]).hline(x + 10, x + 37, base - 10, WOOD[4])
    s.rect(x + 20, base - 3, 2, 2, P.coral[2])


def pier(s):
    """A plank pier running out over the water from the lane, with a ladder
    and a dive flag (red with a white diagonal) on the last post."""
    x0, x1 = PIER
    y = LANE[0] - 2
    for x in range(x0, x1):
        s.vline(x, y, y + 3, WOOD[3] if (x // 5) % 2 else WOOD[2])
        if x % 5 == 0:
            s.vline(x, y, y + 3, WOOD[1])
    s.hline(x0, x1 - 1, y, WOOD[4]).hline(x0, x1 - 1, y + 4, WOOD[0])
    for px in range(x0 + 4, x1, 20):
        s.rect(px, y + 4, 3, 16, WOOD[1]).vline(px, y + 4, y + 19, WOOD[2])
        s.rect(px, y - 8, 3, 8, WOOD[2]).vline(px, y - 8, y - 1, WOOD[3]).set(px + 1, y - 9, WOOD[4])
    s.hline(x0 + 4, x1 - 1, y - 7, WOOD[3]).hline(x0 + 4, x1 - 1, y - 6, WOOD[1])   # rope rail
    fx = x1 - 14
    s.vline(fx, y - 28, y - 1, P.steel[2])
    s.rect(fx + 1, y - 28, 12, 8, P.coral[2])
    s.line(fx + 1, y - 21, fx + 12, y - 28, P.porcelain[3]).line(fx + 2, y - 21, fx + 12, y - 27, P.porcelain[3])
    s.ellipse(fx - 8, y - 10, 3, 3, P.coral[2]).ellipse(fx - 8, y - 10, 1.5, 1.5, None) if False else None
    rx, ry = fx - 10, y - 12                                        # a life ring on the rail post
    for a in range(0, 360, 20):
        r = math.radians(a)
        s.set(int(rx + 3.5 * math.cos(r)), int(ry + 3.5 * math.sin(r)), P.coral[2] if (a // 45) % 2 else P.porcelain[3])


def shallows(s, x0):
    """Right part of the cabana screen: the beach curves down into clear
    water: a foam lace, pale turquoise over the sand, deeper blue further out,
    sun glints."""
    rnd = random.Random(31)
    for y in range(HORIZON, H):
        edge = x0 + int((y - HORIZON) * 0.75 + 6 * math.sin(y * 0.15))
        for x in range(edge, W):
            d = (x - edge) / max(1, W - edge) + (HORIZON + 40 - y) / 160
            c = P.teal[4] if d < 0.18 else P.sea[4] if d < 0.32 else P.sea[3] if d < 0.6 else P.sea[2]
            if 0.16 < d < 0.2 or 0.3 < d < 0.34:
                c = P.teal[4] if (x + y) % 2 else P.sea[4]
            s.set(x, y, c)
        for k in range(3):                                          # foam lace and wet sand
            xx = edge - 1 - k
            s.set(xx, y, P.porcelain[3] if k == 0 else (S[4] if (y + k) % 2 else S[2]))
        if (y // 3) % 4 == 0:
            s.hline(edge, edge + 2 + (y % 3), y, P.porcelain[3])
    for _ in range(90):
        y = rnd.randint(HORIZON + 2, H - 1)
        x = rnd.randint(x0 + int((y - HORIZON) * 0.75) + 8, W - 3)
        s.hline(x, x + rnd.randint(1, 3), y, P.porcelain[3] if rnd.random() < 0.3 else P.sea[4])


# ------------------------------------------------------------- scenes

ZONES = [
    {"id": "lodge", "name": "旅舍"},
    {"id": "cabana", "name": "更衣室"},
]
PALMS = {"lodge": [(30, 96, 60, 1, 1), (262, 95, 52, -1, 2), (318, 96, 66, -1, 3)],
         "cabana": [(26, 95, 58, 1, 4), (200, 95, 62, 1, 5)]}


def background(zone):
    s = Sprite(W, H)
    sky(s)
    clouds(s, zone["id"])
    if zone["id"] == "lodge":
        sea(s)
        ridge(s, -40, 230, 30, 1)
        beach(s)
        lane(s)
        for x in (60, 248):
            hibiscus(s, x, LANE[0] - 1, 11, 10, P.coral if x < 100 else P.blossom)
        plumeria(s, 76, LANE[0] - 1)
        lodge(s)
        for x in (88, 242):
            tiki_torch(s, x, LANE[0] - 1)
        mailbox_sign(s, 296, LANE[0] - 1)
    else:
        sea(s)
        ridge(s, 160, 420, 22, 2)
        beach(s)
        shallows(s, 236)
        lane(s)
        s.rect(PIER[0], LANE[0], W - PIER[0], LANE[1] - LANE[0], 0) if False else None
        canoe(s, 8, 80)
        cabana(s)
        hibiscus(s, 186, LANE[0] - 1, 9, 9, P.mustard)
        pier(s)
    border = Sprite(W, H)
    tropical_border(border, zone["id"])
    s.blit(border, 0, 0)
    return s


def trees(zone, frame):
    s = Sprite(W, H)
    for x, base, h, lean, seed in PALMS[zone["id"]]:
        palm(s, x, base, h, lean, frame, seed)
    return s


# ------------------------------------------------------------- lodge inside

IN_W, IN_H = 262, 62
INSIDE_DATA = {"rooms": {"living": (50, 92), "kitchen": (146, 50), "bath": (200, 26), "bedroom": (6, 40)}}


def lodge_inside():
    """One storey, compact: bedroom | living room (front door) | kitchen | bath.
    Built on the friend-house planner shell, then furnished by hand: rattan,
    koa wood, a quilt with a Hawaiian appliqué, a monstera, a surfboard on the
    wall, louvred windows."""
    plan = ("lodge", "海岛旅舍", IN_W, "", "garden", [[("laundry", 6, 72), ("laundry", 82, 82), ("laundry", 168, 50), ("laundry", 222, 34)]])
    data, bg, front = FH.draw_plan(plan)
    s = bg.copy()
    top, fl = 5, 50
    K = P.walnut

    def room(x, w, floor="wood", wall=P.plaster_kitchen):
        HS.back_wall(s, x, w, top, fl, wall)
        HS.floor_band(s, x, w, fl, floor)

    def louvre(x, y, w=16, h=12):
        s.rect(x - 1, y - 1, w + 2, h + 2, P.porcelain[3]).rect(x, y, w, h, P.sky_day[2])
        for yy in range(y, y + h, 2):
            s.hline(x, x + w - 1, yy, P.glass[2])

    room(6, 72, wall=P.plaster_bed)
    room(82, 82)
    room(168, 50, floor="tile")
    room(222, 34, floor="tile", wall=P.plaster_bath)
    # bedroom: koa bed with a quilt (red appliqué), a rattan lamp, a window
    louvre(14, top + 10)
    s.rect(10, fl - 9, 46, 3, K[2]).hline(10, 55, fl - 9, K[3])
    s.rect(10, fl - 20, 3, 20, K[2]).rect(53, fl - 14, 3, 14, K[2])
    s.rect(13, fl - 12, 40, 4, P.porcelain[3]).ellipse(17, fl - 13, 4, 2, P.porcelain[3])
    s.rect(22, fl - 13, 31, 5, P.coral[2]).hline(22, 52, fl - 13, P.coral[3])
    for k in range(24, 52, 7):                                      # appliqué motif
        s.set(k, fl - 11, P.porcelain[3]).set(k + 1, fl - 12, P.porcelain[3]).set(k + 2, fl - 11, P.porcelain[3]).set(k + 1, fl - 10, P.porcelain[3])
    s.vline(10, fl - 6, fl, K[1]).vline(55, fl - 6, fl, K[1])
    s.rect(60, fl - 8, 10, 8, P.oak[2]).hline(60, 69, fl - 8, P.oak[4])   # rattan nightstand + lamp
    s.ellipse(65, fl - 13, 4, 4, P.oak[3]).vline(65, fl - 10, fl - 9, P.oak[1])
    # living room: rattan sofa (seats 3), coffee table, monstera, surfboard on the wall
    louvre(110, top + 8, 20, 12)
    s.rect(90, fl - 10, 44, 3, P.oak[3]).hline(90, 133, fl - 10, P.oak[4])
    s.rect(90, fl - 20, 44, 10, P.oak[2])
    for x in range(91, 133, 2):
        s.vline(x, fl - 19, fl - 11, P.oak[1 + (x % 4 == 1)])
    for k in range(3):
        s.rect(92 + k * 14, fl - 13, 12, 3, P.teal[3]).hline(92 + k * 14, 103 + k * 14, fl - 13, P.teal[4])
        s.set(96 + k * 14, fl - 12, P.porcelain[3]).set(99 + k * 14, fl - 12, P.coral[3])
    s.vline(91, fl - 7, fl, P.oak[1]).vline(132, fl - 7, fl, P.oak[1])
    s.rect(100, fl - 4, 22, 2, K[3]).vline(102, fl - 2, fl, K[1]).vline(119, fl - 2, fl, K[1])
    s.ellipse(111, fl - 6, 2, 2, P.mustard[3])                     # a pineapple on the table
    for k in range(3):
        s.set(110 + k, fl - 9 + (k % 2), P.green[3])
    mx = 146                                                        # monstera in a pot
    s.rect(mx - 3, fl - 7, 7, 7, P.terracotta[2]).hline(mx - 3, mx + 3, fl - 7, P.terracotta[3])
    for a, L in ((-2.4, 9), (-1.6, 12), (-0.8, 9), (-1.2, 7), (-2.0, 7)):
        ex, ey = int(mx + math.cos(a) * L), int(fl - 8 + math.sin(a) * L)
        s.line(mx, fl - 8, ex, ey, P.green[2])
        s.ellipse(ex, ey, 3, 2.2, P.green[2]).set(ex - 1, ey - 1, P.green[3]).set(ex + 1, ey, P.green[1])
    for y in range(top + 6, top + 30):                              # surfboard on the wall
        t = (y - top - 6) / 24
        hw = int(2.5 * math.sin(math.pi * t) + 0.4)
        s.hline(89 - hw, 89 + hw, y, P.hydrangea[3])
    s.vline(89, top + 8, top + 28, P.porcelain[3])
    # kitchen: koa counter, two burners, open shelf with bowls and a bunch of bananas
    s.rect(170, fl - 14, 46, 14, K[2]).hline(170, 215, fl - 14, P.porcelain[3]).hline(170, 215, fl - 13, P.porcelain[2])
    for x in (180, 196):
        s.rect(x, fl - 10, 10, 8, K[1]).set(x + 8, fl - 6, P.mustard[3])
    s.rect(200, fl - 16, 10, 2, P.slate[1])                         # burners
    s.rect(172, fl - 18, 9, 4, P.steel[3]).hline(172, 180, fl - 18, P.steel[4])   # kettle-ish pot
    s.rect(172, top + 12, 40, 2, K[3])
    for k, C in enumerate((P.porcelain, P.teal, P.coral, P.porcelain)):
        s.rect(174 + k * 9, top + 8, 6, 4, C[2]).hline(174 + k * 9, 179 + k * 9, top + 8, C[3])
    for k in range(4):
        s.ellipse(206 + k, top + 18 + k, 1.5, 3, P.mustard[3])
    louvre(186, top + 18, 12, 8)
    # bath: walk-in shower with a bamboo screen, toilet, basin and mirror
    s.rect(224, top + 12, 12, fl - top - 12, P.glass[3]).vline(236, top + 12, fl - 1, P.steel[3])
    s.vline(229, top + 8, top + 12, P.steel[2]).rect(227, top + 12, 5, 2, P.steel[3])
    import _furniture as F
    HS.on_floor(s, F.toilet(), 240, 1, 1)
    s.rect(244, top + 16, 8, 8, P.glass[2]).rect(243, top + 15, 10, 1, P.oak[3])
    s.blit(front, 0, 0)
    return s, INSIDE_DATA


def preview(zone, frame=0):
    s = background(zone)
    s.blit(trees(zone, frame), 0, 0)
    return s


def build():
    out = {}
    pano = Sprite(W * len(ZONES), H)
    for i, z in enumerate(ZONES):
        out[f"summer_{z['id']}"] = background(z)
        for f in (0, 1):
            out[f"summer_{z['id']}_palms_{f}"] = trees(z, f)
        pv = preview(z)
        out[f"summer_{z['id']}_preview"] = pv
        pano.blit(pv, i * W, 0)
    out["summer_shore_panorama"] = pano
    out["summer_lodge_inside"], _ = lodge_inside()
    return out
