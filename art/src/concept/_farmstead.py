"""Detailed farm pieces for 春日花溪 (spring_fields.py): the family farmhouse
(outside + a small inside), the barn, livestock, a shrub border for the front
of the lane, and ambient overlays (sun shafts, birds). Light from the top left.
Scale: 1px ≈ 6cm, Buddy is 20x28, so a cow is ~38px long, a sheep ~22px.
"""
from __future__ import annotations

import math
import random

import numpy as np

from pixelkit import P, Sprite

import front_yard as FY
import house as HS
import friend_houses as FH

W, H = 342, 118
LANE = 94                 # top of the gravel lane (park.PATH[0])
G = P.leaf_spring
ST = P.pave
TB = P.walnut


def stones(s, x0, x1, y0, y1, R=ST, seed=1):
    """Coursed fieldstone: rows of stones of varied width, lit top-left,
    dark mortar."""
    rnd = random.Random(seed)
    s.rect(x0, y0, x1 - x0, y1 - y0, R[1])
    y = y0
    while y < y1:
        h = min(rnd.choice((3, 4)), y1 - y)
        x = x0 - rnd.randint(0, 3)
        while x < x1:
            w = rnd.randint(4, 8)
            a, b = max(x, x0), min(x + w - 1, x1 - 1)
            if b > a:
                c = rnd.choice((R[2], R[2], R[3]))
                s.rect(a, y, b - a, h - 1, c)
                s.hline(a, b - 1, y, R[3] if c == R[2] else R[4])
                s.set(b - 1, y + h - 2, R[1])
            x += w
        y += h


def plaster(s, x0, y0, w, h, R, seed):
    """Lime plaster: base tone with sparse warm/cool speckle."""
    s.rect(x0, y0, w, h, R[3])
    rnd = random.Random(seed)
    for _ in range(w * h // 14):
        s.set(rnd.randint(x0, x0 + w - 1), rnd.randint(y0, y0 + h - 1), R[2])


# ------------------------------------------------------------- farmhouse outside

HOUSE = (112, 240)
HOUSE_DOOR = 182


def window(s, x, y, w, h, shutters=True, box=True, curtain=P.blossom):
    s.rect(x - 2, y - 2, w + 4, h + 4, TB[1])                       # frame
    s.hline(x - 2, x + w + 1, y - 2, TB[3])
    s.rect(x, y, w, h, P.glass[1])
    for k in range(w + h):                                          # a diagonal sky reflection
        for d in range(2):
            px, py = x + k - h // 2 + d, y + h - 1 - k
            if x <= px < x + w and y <= py < y + h:
                s.set(px, py, P.glass[3])
    s.rect(x, y, 2, h - 1, curtain[3]).set(x + 1, y + h // 2, curtain[1])   # tied-back curtains
    s.rect(x + w - 2, y, 2, h - 1, curtain[2]).set(x + w - 2, y + h // 2, curtain[1])
    s.hline(x, x + w - 1, y, curtain[3])
    s.vline(x + w // 2, y, y + h - 1, TB[2]).hline(x, x + w - 1, y + h // 2, TB[2])
    s.rect(x - 3, y + h + 1, w + 6, 2, P.porcelain[3]).hline(x - 3, x + w + 2, y + h + 2, P.porcelain[1])  # sill
    if shutters:
        for sx in (x - 7, x + w + 2):
            s.rect(sx, y - 2, 5, h + 4, P.sage[2])
            s.vline(sx, y - 2, y + h + 1, P.sage[3]).vline(sx + 4, y - 2, y + h + 1, P.sage[1])
            s.vline(sx + 2, y - 2, y + h + 1, P.sage[1])
            s.hline(sx, sx + 4, y, P.sage[3]).hline(sx, sx + 4, y + h - 1, P.sage[3])
            s.line(sx, y + h - 1, sx + 4, y, P.sage[3])            # Z brace
    if box:
        by = y + h + 3
        s.rect(x - 2, by, w + 4, 3, P.terracotta[2]).hline(x - 2, x + w + 1, by, P.terracotta[3]).hline(x - 2, x + w + 1, by + 2, P.terracotta[1])
        rnd = random.Random(x * 13 + y)
        for k in range(-1, w + 2):
            s.set(x + k, by - 1, P.green[rnd.choice((2, 3))])
            if rnd.random() < 0.55:
                F = rnd.choice((P.coral, P.blossom, P.mustard, P.linen))
                s.set(x + k, by - 2, F[3]).set(x + k, by - 1, F[2])
        for k in (0, w // 2, w):                                    # trailing ivy
            for d in range(rnd.randint(2, 4)):
                s.set(x + k - 1 + (d % 2), by + 3 + d, P.green[2 + (d == 0)])


def roof(s, x0, x1, top, eave):
    """Steep tiled roof seen from the long side, with a barge board at each
    gable, scalloped tile rows, a little moss and a gutter."""
    Rf = P.terracotta
    rnd = random.Random(7)
    for y in range(top, eave + 1):
        t = (y - top) / (eave - top)
        a, b = int(x0 + 16 - 22 * t), int(x1 - 16 + 22 * t)
        row = (y - top) // 3
        k = (y - top) % 3
        c = (Rf[3], Rf[2], Rf[1])[k]
        s.hline(a, b, y, c)
        if k == 2:                                                  # tile joints, staggered per row
            for x in range(a + (row % 2) * 3, b, 6):
                s.set(x, y, Rf[0]).set(x, y - 1, Rf[1])
        if k == 0:
            for x in range(a, b):
                if rnd.random() < 0.06:
                    s.set(x, y, Rf[4])
                elif rnd.random() < 0.03 and t > 0.5:
                    s.set(x, y, P.sage[2])                         # moss
        s.set(a, y, TB[3]).set(a + 1, y, TB[2]).set(b, y, TB[1]).set(b - 1, y, TB[2])
    s.hline(x0 + 15, x1 - 15, top - 1, Rf[1]).hline(x0 + 15, x1 - 15, top - 2, Rf[3])   # ridge tiles
    for x in range(x0 + 16, x1 - 15, 4):
        s.set(x, top - 2, Rf[4])
    s.rect(x0 - 7, eave + 1, x1 - x0 + 14, 2, P.steel[2]).hline(x0 - 7, x1 + 6, eave + 1, P.steel[4])   # gutter
    s.vline(x1 + 4, eave + 3, LANE - 2, P.steel[2]).vline(x1 + 5, eave + 3, LANE - 2, P.steel[1])       # downpipe
    s.hline(x1 + 3, x1 + 6, LANE - 2, P.steel[1])


def weathervane(s, x, y):
    s.vline(x, y - 10, y, TB[0]).hline(x - 4, x + 4, y - 6, TB[0])
    s.rect(x - 2, y - 13, 5, 3, TB[0]).set(x + 3, y - 14, TB[0]).set(x - 3, y - 12, TB[0]).set(x + 2, y - 14, P.coral[2])


def chimney(s, x, top, base):
    stones(s, x, x + 10, top, base, P.brick, seed=x)
    s.rect(x - 1, top - 2, 12, 2, P.pave[3]).hline(x - 1, x + 10, top - 1, P.pave[1])
    for k, (dx, r) in enumerate(((2, 2), (5, 3), (10, 4), (16, 4.5))):
        cy = top - 6 - k * 6
        s.ellipse(x + 5 + dx, cy, r, r * 0.7, P.porcelain[3 if k < 2 else 2])
        s.ellipse(x + 4 + dx, cy - 1, r * 0.5, r * 0.35, P.porcelain[3])


def climbing_rose(s, x, y0, y1):
    rnd = random.Random(x)
    for y in range(y1, y0, -1):
        xx = x + int(2 * math.sin(y * 0.5))
        s.set(xx, y, P.green[1])
        if rnd.random() < 0.6:
            s.set(xx + rnd.choice((-1, 1)), y, P.green[rnd.choice((2, 3))])
        if rnd.random() < 0.22:
            s.rect(xx - 1 + rnd.randint(-1, 1), y, 2, 2, P.blossom[2]).set(xx, y, P.blossom[4])


def pot(s, x, base, F):
    s.rect(x, base - 4, 6, 4, P.terracotta[2]).hline(x - 1, x + 6, base - 4, P.terracotta[3]).vline(x + 5, base - 3, base - 1, P.terracotta[1])
    s.ellipse(x + 3, base - 7, 3.5, 2.5, P.green[2]).set(x + 1, base - 8, P.green[3])
    for dx in (0, 2, 4, 5):
        s.set(x + dx, base - 8 - (dx % 2), F[3]).set(x + dx, base - 7, F[2])


def bench(s, x, base):
    s.rect(x, base - 7, 18, 2, P.oak[3]).hline(x, x + 17, base - 7, P.oak[4]).hline(x, x + 17, base - 6, P.oak[1])
    s.rect(x, base - 14, 18, 2, P.oak[2]).hline(x, x + 17, base - 14, P.oak[3])
    for lx in (x + 1, x + 16):
        s.vline(lx, base - 14, base - 1, P.oak[1])
    s.rect(x + 3, base - 9, 6, 2, P.blossom[2]).hline(x + 3, x + 8, base - 9, P.blossom[3])   # cushion


def farmhouse(s):
    """Two storeys: fieldstone plinth, lime-white ground floor, half-timbered
    upper floor, steep tiled roof with two dormers, chimney, weathervane,
    porch with bench and pots, a climbing rose."""
    x0, x1 = HOUSE
    base = LANE - 1
    plinth = base - 5
    up = plinth - 25
    eave = up - 19
    top = eave - 27
    chimney(s, x1 - 34, top - 6, eave - 6)
    roof(s, x0, x1, top, eave)
    weathervane(s, x0 + 30, top - 2)
    for wx in (x0 + 38, x1 - 52):                                  # dormers
        plaster(s, wx, eave - 15, 16, 14, P.linen, wx)
        s.vline(wx, eave - 15, eave - 2, P.linen[3]).vline(wx + 15, eave - 15, eave - 2, P.linen[1])
        window(s, wx + 4, eave - 12, 8, 7, shutters=False, box=False, curtain=P.linen)
        for k in range(6):
            s.hline(wx - 3 + k, wx + 18 - k, eave - 16 - k, P.terracotta[3 - (k % 3 == 2)] if k else P.terracotta[1])
        s.set(wx - 3, eave - 16, TB[1]).set(wx + 18, eave - 16, TB[1])
    # upper floor: plaster infill between oak timbers
    plaster(s, x0, eave + 3, x1 - x0, up - eave - 3, P.linen, 11)
    s.hline(x0, x1 - 1, eave + 3, P.linen[1]).hline(x0, x1 - 1, eave + 4, P.linen[2])     # eave shadow
    Tm = P.walnut
    s.rect(x0, up - 1, x1 - x0, 3, Tm[2]).hline(x0, x1 - 1, up - 1, Tm[3]).hline(x0, x1 - 1, up + 1, Tm[1])
    for x in range(x0, x1, 21):
        s.rect(x, eave + 3, 3, up - eave - 3, Tm[2]).vline(x, eave + 3, up - 1, Tm[3])
        if x + 21 < x1:
            for d in range(2):
                s.line(x + 3 + d, up - 2, x + 10 + d, eave + 5, Tm[2 - d])
                s.line(x + 20 - d, up - 2, x + 13 - d, eave + 5, Tm[2 - d])
    s.rect(x1 - 3, eave + 3, 3, up - eave - 3, Tm[1])
    for wx in (x0 + 24, x0 + 66, x1 - 30):
        window(s, wx, eave + 7, 9, 8, shutters=False, curtain=P.linen)
    # ground floor
    plaster(s, x0, up + 2, x1 - x0, plinth - up - 2, P.linen, 13)
    s.hline(x0, x1 - 1, up + 2, P.linen[1])
    s.vline(x1 - 1, up + 2, plinth, P.linen[1]).vline(x1 - 2, up + 2, plinth, P.linen[2])
    for wx in (x0 + 16, x0 + 42, x1 - 40, x1 - 18):
        if abs(wx + 5 - HOUSE_DOOR) > 16:
            window(s, wx, up + 7, 11, 10)
    climbing_rose(s, x0 + 4, eave + 6, plinth)
    # door, porch
    dx = HOUSE_DOOR - 7
    s.rect(dx - 1, plinth - 21, 16, 21, TB[1])
    s.rect(dx, plinth - 20, 14, 20, P.sage[2])
    for px in range(dx + 2, dx + 14, 3):
        s.vline(px, plinth - 20, plinth - 1, P.sage[1])
    s.vline(dx, plinth - 20, plinth - 1, P.sage[3])
    s.rect(dx + 4, plinth - 17, 6, 4, P.glass[2]).hline(dx + 4, dx + 9, plinth - 17, P.glass[3])
    for hy in (plinth - 16, plinth - 5):
        s.hline(dx, dx + 4, hy, P.slate[1])
    s.set(dx + 11, plinth - 9, P.mustard[3]).set(dx + 11, plinth - 10, P.mustard[4])
    s.ellipse(dx + 7, plinth - 23, 3, 2, P.green[2]).set(dx + 5, plinth - 24, P.coral[3]).set(dx + 9, plinth - 23, P.mustard[4])   # wreath
    for px in (dx - 9, dx + 22):
        s.rect(px, plinth - 27, 2, 27 + 4, Tm[3]).vline(px + 1, plinth - 27, base, Tm[1])
    for k in range(5):
        s.hline(dx - 12 + k, dx + 25 - k, plinth - 28 - k, P.terracotta[3 - (k % 2)] if k else P.terracotta[1])
    s.hline(dx - 11, dx + 24, plinth - 27, Tm[1])
    s.rect(dx + 18, plinth - 22, 3, 5, P.slate[1]).rect(dx + 19, plinth - 21, 1, 3, P.light[0])   # lantern
    bench(s, dx - 30, plinth + 4)
    for px, F in ((dx - 7, P.coral), (dx + 17, P.mustard), (x1 - 14, P.blossom), (x0 + 6, P.lilac)):
        pot(s, px, base, F)
    # plinth and steps
    stones(s, x0 - 2, x1 + 2, plinth, base + 1, seed=3)
    s.rect(dx - 4, base - 2, 22, 3, ST[3]).hline(dx - 4, dx + 17, base - 2, ST[4]).hline(dx - 4, dx + 17, base, ST[1])
    s.rect(dx - 2, base - 5, 18, 3, ST[3]).hline(dx - 2, dx + 15, base - 5, ST[4]).hline(dx - 2, dx + 15, base - 3, ST[1])


# ------------------------------------------------------------- farmhouse inside

INSIDE = ("farmhouse", "山谷农舍", 288, "爸妈承包的农舍：楼上小人的卧室、小浴室、爸妈的卧室；楼下客厅连着厨房。", "oak", [
    [("stair", 6, 40), ("bed", 50, 90), ("bath", 144, 40), ("guest_bed", 188, 94)],
    [("entry_stair", 6, 40), ("living", 50, 134), ("kitchen", 188, 94)]])
OPEN_X = 184               # the living/kitchen partition removed: one open room


def farmhouse_inside():
    data, bg, front = FH.draw_plan(INSIDE)
    s = bg.copy()
    w = s.w
    top, fl = 58 + 5, 58 + 50
    HS.back_wall(s, OPEN_X - 4, 12, top, fl, P.plaster_bed)        # open the living room into the kitchen
    HS.floor_band(s, OPEN_X - 4, 12, fl, "wood")
    s.rect(OPEN_X - 1, top - 5, 3, 14, P.walnut[2]).hline(OPEN_X - 1, OPEN_X + 1, top + 8, P.walnut[1])   # a beam over the opening
    for level in range(2):                                         # exposed ceiling joists
        t = level * 58 + 5
        for x in range(8, w - 6, 18):
            s.rect(x, t, 5, 3, P.walnut[1]).hline(x, x + 4, t, P.walnut[3]).set(x + 4, t + 2, P.walnut[0])
    for k, x in enumerate(range(200, 270, 12)):                    # dried herbs and garlic over the kitchen
        s.vline(x, top + 3, top + 6, P.oat[1])
        C = (P.sage, P.mustard, P.linen)[k % 3]
        s.ellipse(x, top + 9, 2, 3, C[2]).set(x - 1, top + 8, C[3])
    for x in range(64, 170, 2):                                    # a rag rug in the living room
        c = (P.clay[2], P.oat[2], P.sage[2], P.mustard[2])[(x // 6) % 4]
        s.set(x, fl + 3, c).set(x + 1, fl + 3, c)
    s.blit(front, 0, 0)
    return s, data


# ------------------------------------------------------------- barn and yard

def barn(s, x, base):
    """Red board-and-batten barn with a gambrel roof, white trim, hayloft
    with hay, sliding doors on a rail, a lantern."""
    w = 86
    R, Wt = P.terracotta, P.porcelain
    wall = base - 34
    s.rect(x, wall, w, 34, R[2])
    for xx in range(x + 1, x + w, 4):
        s.vline(xx, wall, base - 1, R[3]).vline(xx + 2, wall, base - 1, R[1])
    rnd = random.Random(5)
    for _ in range(60):
        s.set(rnd.randint(x, x + w - 1), rnd.randint(wall, base - 1), R[rnd.choice((1, 3))])
    s.vline(x, wall, base - 1, Wt[3]).vline(x + 1, wall, base - 1, Wt[2])
    s.vline(x + w - 1, wall, base - 1, Wt[1]).vline(x + w - 2, wall, base - 1, Wt[2])
    for k in range(22):                                            # gambrel roof
        a, b = (x - 4 + k, x + w + 3 - k) if k < 9 else (x + 5 + (k - 9) * 3, x + w - 6 - (k - 9) * 3)
        if a >= b:
            break
        c = P.slate[3] if k % 3 == 0 else P.slate[2]
        s.hline(a, b, wall - 1 - k, c)
        s.set(a, wall - 1 - k, Wt[3]).set(b, wall - 1 - k, Wt[2])
        for xx in range(a + (k % 2) * 2, b, 5):
            if k % 3 == 2:
                s.set(xx, wall - 1 - k, P.slate[1])
    s.hline(x - 4, x + w + 3, wall, Wt[3]).hline(x - 4, x + w + 3, wall + 1, R[0])
    cx = x + w // 2
    s.rect(cx - 8, wall - 16, 16, 13, Wt[3]).rect(cx - 7, wall - 15, 14, 11, TB[0])   # hayloft
    for k in range(7):
        s.hline(cx - 6, cx + 5, wall - 10 + k // 2, P.mustard[(2, 3, 4)[k % 3]])
    for k in range(-6, 6, 2):
        s.set(cx + k, wall - 11, P.mustard[3])
    s.hline(cx - 9, cx + 8, wall - 17, TB[1]).vline(cx, wall - 22, wall - 17, TB[1]).set(cx, wall - 23, P.steel[3])   # hay hook beam
    d0, d1 = cx - 16, cx + 16                                      # sliding doors
    s.hline(d0 - 6, d1 + 6, base - 27, P.steel[1])
    s.rect(d0, base - 26, 32, 26, R[1])
    for a, b in ((d0, cx), (cx, d1)):
        s.rect(a, base - 26, b - a, 26, R[2])
        for xx in range(a + 2, b, 3):
            s.vline(xx, base - 25, base - 2, R[1])
        s.vline(a, base - 26, base - 1, Wt[3]).vline(b - 1, base - 26, base - 1, Wt[2])
        s.hline(a, b - 1, base - 26, Wt[3]).hline(a, b - 1, base - 13, Wt[3]).hline(a, b - 1, base - 1, Wt[2])
        s.line(a, base - 25, b - 1, base - 14, Wt[3]).line(a, base - 12, b - 1, base - 2, Wt[3])
    for wx in (x + 7, x + w - 17):
        s.rect(wx, base - 22, 10, 9, Wt[3]).rect(wx + 1, base - 21, 8, 7, P.glass[1]).vline(wx + 5, base - 21, base - 15, Wt[3]).hline(wx + 1, wx + 8, base - 18, Wt[3])
        s.rect(wx + 1, base - 21, 3, 2, P.glass[3])
    s.rect(d1 + 3, base - 31, 3, 4, P.slate[1]).set(d1 + 4, base - 30, P.light[0])


def silo(s, x, base):
    h, w = 58, 18
    for y in range(base - h, base):
        s.hline(x, x + w - 1, y, P.porcelain[2])
        s.hline(x, x + 3, y, P.porcelain[3]).hline(x + w - 4, x + w - 1, y, P.porcelain[1]).set(x + w - 1, y, P.porcelain[0])
    for y in range(base - h + 4, base, 6):
        s.hline(x, x + w - 1, y, P.porcelain[1])
        for xx in range(x + 2, x + w - 1, 5):
            s.set(xx, y + 1, P.steel[2])
    s.vline(x + w - 4, base - h + 2, base - 1, P.steel[2])                 # ladder
    for y in range(base - h + 3, base, 3):
        s.set(x + w - 5, y, P.steel[2])
    for k in range(7):
        s.hline(x + k, x + w - 1 - k, base - h - k, P.slate[3 if k < 2 else 2])
    s.set(x + w // 2, base - h - 8, P.steel[3])


def hay(s, x, base):
    """A round stack plus square bales, straw scattered."""
    Y = P.mustard
    s.ellipse(x, base - 7, 13, 8, Y[2])
    s.ellipse(x - 4, base - 10, 8, 5, Y[3]).ellipse(x - 6, base - 12, 4, 2, Y[4])
    for k in range(-11, 12, 2):
        s.line(x + k, base - 1, x + k + 2, base - 10 + abs(k) // 3, Y[1 + (k % 4 == 1)])
    s.hline(x - 12, x + 12, base, Y[0])
    for bx, by in ((x + 16, base), (x + 29, base), (x + 22, base - 7)):
        s.rect(bx, by - 7, 13, 7, Y[2]).hline(bx, bx + 12, by - 7, Y[4]).vline(bx + 12, by - 7, by - 1, Y[1])
        for xx in range(bx + 1, bx + 12, 2):
            s.set(xx, by - 4 + (xx % 3 == 0), Y[3])
        s.vline(bx + 4, by - 7, by - 1, P.oak[1]).vline(bx + 9, by - 7, by - 1, P.oak[1])


def trough(s, x, base):
    s.rect(x, base - 6, 26, 6, P.oak[2]).hline(x, x + 25, base - 6, P.oak[4]).hline(x, x + 25, base - 1, P.oak[1])
    s.hline(x + 1, x + 24, base - 5, P.sea[3]).hline(x + 3, x + 9, base - 5, P.sea[4] if len(P.sea) > 4 else P.sea[3])
    for xx in range(x + 4, x + 24, 7):
        s.vline(xx, base - 4, base - 2, P.oak[1])


def cart(s, x, base):
    s.rect(x, base - 12, 24, 6, P.oak[2]).hline(x, x + 23, base - 12, P.oak[4]).hline(x, x + 23, base - 7, P.oak[1])
    for xx in range(x + 3, x + 23, 5):
        s.vline(xx, base - 11, base - 8, P.oak[1])
    s.line(x + 23, base - 9, x + 34, base - 3, P.oak[1])
    for k in range(-5, 6, 2):
        s.hline(x + 4, x + 18, base - 13 + (k > 2), P.mustard[3])
    cx, cy = x + 8, base - 5
    for a in range(0, 360, 15):
        r = math.radians(a)
        s.set(int(cx + 5 * math.cos(r)), int(cy + 5 * math.sin(r)), TB[1])
    for a in (0, 45, 90, 135):
        r = math.radians(a)
        s.line(int(cx - 4 * math.cos(r)), int(cy - 4 * math.sin(r)), int(cx + 4 * math.cos(r)), int(cy + 4 * math.sin(r)), TB[2])


def rail_fence(s, x0, x1, y, gate=None, R=P.oak):
    """Split-rail paddock fence; posts every 16px, two rails, a gate gap."""
    for x in range(x0, x1):
        if gate and gate[0] <= x < gate[1]:
            continue
        for ry in (y - 8, y - 3):
            s.set(x, ry, R[3]).set(x, ry + 1, R[1])
    for x in range(x0 + 3, x1, 16):
        if gate and gate[0] - 3 <= x < gate[1] + 1:
            continue
        s.rect(x, y - 11, 3, 12, R[2]).vline(x, y - 11, y, R[3]).vline(x + 2, y - 11, y, R[1]).hline(x, x + 2, y - 11, R[4])
        s.set(x - 1, y + 1, G[1]).set(x + 3, y + 1, G[1])
    if gate:
        for gx in gate:
            s.rect(gx - 2, y - 13, 4, 14, R[2]).vline(gx - 2, y - 13, y, R[3]).hline(gx - 2, gx + 1, y - 13, R[4])


# ------------------------------------------------------------- livestock

def cow(frame):
    """Holstein, facing right, 40x26. 0 stand, 1 graze, 2 tail swish, 3 step."""
    s = Sprite(40, 26)
    Wt, Bk, Pk = P.porcelain, P.slate, P.blossom
    body = Sprite(40, 26)
    body.ellipse(17, 11, 13, 6.5, Wt[3])                          # barrel
    body.ellipse(9, 10, 6, 6, Wt[3]).ellipse(26, 10, 6, 6, Wt[3])
    for (cx, cy, rx, ry) in ((12, 8, 4, 3), (22, 12, 4.5, 3), (17, 6, 2.5, 2), (28, 9, 2.5, 3), (7, 12, 2, 2.5)):
        body.ellipse(cx, cy, rx, ry, Bk[1])
        body.set(int(cx - rx * 0.4), int(cy - ry * 0.5), Bk[2])
    px = body.px
    a = px[..., 3] > 0
    for y in range(26):                                           # shade the belly, light the back
        for x in range(40):
            if a[y, x] and tuple(px[y, x, :3]) == tuple(int(Wt[3][i:i + 2], 16) for i in (1, 3, 5)):
                if y >= 14:
                    body.set(x, y, Wt[1])
                elif y >= 13:
                    body.set(x, y, Wt[2])
    s.blit(body.outline(Bk[0], grow=False), 0, 0)
    step = 1 if frame == 3 else 0
    for i, lx in enumerate((6, 10, 23, 27)):                      # legs, hooves
        off = (step if i % 2 == 0 else -step)
        top = 15
        s.rect(lx + off, top, 3, 8, Wt[2] if i in (0, 2) else Wt[1])
        s.vline(lx + off, top, top + 7, Wt[3] if i in (0, 2) else Wt[2])
        s.rect(lx + off, top + 8, 3, 2, Bk[0])
        s.rect(lx + off, top + 2, 3, 2, Bk[1]) if i == 2 else None
    s.ellipse(20, 17, 3, 1.6, Pk[2]).set(19, 18, Pk[3]).set(21, 18, Pk[1])   # udder
    tx = 4
    sw = -2 if frame == 2 else 0                                   # tail
    s.line(tx, 7, tx - 1 + sw, 17, Wt[1]).rect(tx - 2 + sw, 17, 3, 3, Bk[1])
    hy = 3 if frame != 1 else 12                                   # head
    hx = 30
    head = Sprite(40, 26)
    head.rect(hx, hy + 2, 7, 7, Wt[3]).rect(hx + 1, hy + 1, 5, 1, Wt[3])
    head.rect(hx + 4, hy + 6, 5, 4, Pk[3]).set(hx + 6, hy + 7, Pk[1]).set(hx + 8, hy + 7, Pk[1]).hline(hx + 4, hx + 8, hy + 9, Pk[2])
    head.rect(hx, hy + 2, 3, 3, Bk[1])                            # a patch round the ear
    head.set(hx + 4, hy + 4, Bk[0]).set(hx + 5, hy + 3, Wt[3])     # eye
    head.hline(hx - 2, hx, hy + 3, Wt[2]).set(hx - 2, hy + 4, Pk[2])   # ear
    head.set(hx + 1, hy, Wt[2]).set(hx + 1, hy - 1, P.oat[3]).set(hx + 4, hy, P.oat[3])   # horns
    head.set(hx - 1, hy + 5, P.coral[2]).set(hx - 1, hy + 6, P.mustard[3])   # ear tag
    neck = Sprite(40, 26)
    if frame == 1:
        neck.line(28, 9, 32, 13, Wt[3]).line(28, 10, 32, 14, Wt[3]).line(28, 11, 31, 15, Wt[2])
    else:
        neck.rect(28, 6, 4, 6, Wt[3])
    s.blit(neck, 0, 0)
    s.blit(head.outline(Bk[0], grow=False), 0, 0)
    return s


def sheep(frame, lamb=False):
    """Woolly ewe facing left, 24x18 (a lamb is drawn smaller). 0 stand,
    1 graze, 2 look up (ear flick), 3 step."""
    sc = 0.7 if lamb else 1.0
    w, h = (18, 13) if lamb else (24, 18)
    s = Sprite(w, h)
    Wl = P.linen
    wool = Sprite(w, h)
    rnd = random.Random(3 if not lamb else 4)
    cx0, cy0 = (w * 0.56, h * 0.42)
    for _ in range(int(40 * sc)):                                  # curly fleece: overlapping puffs
        u, v = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        if u * u + v * v > 1:
            continue
        x, y = cx0 + u * 8 * sc, cy0 + v * 4.6 * sc
        light = -u * 0.4 - v * 0.9
        c = Wl[3] if light > 0.1 else Wl[2] if light > -0.5 else Wl[1]
        wool.ellipse(x, y, 2.4 * sc + 0.6, 2.0 * sc + 0.5, c)
    for _ in range(int(14 * sc)):
        x, y = int(cx0 + rnd.uniform(-7, 7) * sc), int(cy0 + rnd.uniform(-3, 3) * sc)
        wool.set(x, y, Wl[1]).set(x + 1, y - 1, Wl[3])
    s.blit(wool.outline(P.oat[0], grow=False), 0, 0)
    step = 1 if frame == 3 else 0
    ly = int(cy0 + 4.5 * sc)
    for i, lx in enumerate((cx0 - 5 * sc, cx0 - 2 * sc, cx0 + 3 * sc, cx0 + 6 * sc)):
        off = step if i % 2 else -step
        s.vline(int(lx) + off, ly, h - 2, P.walnut[1]).set(int(lx) + off, h - 1, P.walnut[0])
    hy = int(cy0 - 4 * sc) if frame != 1 else int(cy0 + 2 * sc)
    hx = int(cx0 - 11 * sc)
    face = Sprite(w, h)
    face.rect(hx, hy, int(5 * sc) + 1, int(5 * sc) + 1, P.walnut[1]).rect(hx, hy + int(3 * sc), int(3 * sc), 2, P.walnut[2])
    face.set(hx + 1, hy + 1, P.porcelain[3]).set(hx + 1, hy + 2, P.walnut[0])   # eye with a glint
    face.set(hx, hy + int(4 * sc), P.blossom[1])
    ear = -1 if frame == 2 else 0
    face.hline(hx + int(4 * sc), hx + int(6 * sc), hy + 1 + ear, P.walnut[1]).set(hx + int(6 * sc), hy + 2 + ear, P.blossom[2])
    face.ellipse(hx + int(3 * sc), hy - 1, 2 * sc + 0.5, 1.3, Wl[3])    # topknot
    s.blit(face.outline(P.walnut[0], grow=False), 0, 0)
    return s


def chicken(frame, rooster=False):
    """10x10 hen (or rooster with a tail plume), facing right; 1 pecks."""
    s = Sprite(11, 11)
    C = P.oak if not rooster else P.terracotta
    body = Sprite(11, 11)
    body.ellipse(5, 6, 3.6, 2.8, C[3]).ellipse(4, 7, 2.5, 1.6, C[2])
    body.set(5, 5, C[4]).set(6, 5, C[4]).hline(3, 6, 8, C[1])
    tail = (P.slate[1], P.green[1], P.slate[2]) if rooster else (C[2], C[1], C[2])
    body.line(1, 2, 2, 5, tail[0]).line(2, 2, 3, 5, tail[1]).set(1, 3, tail[2])
    hy = 2 if frame == 0 else 5
    body.rect(7, hy, 3, 3, C[3]).set(8, hy, C[4])
    body.set(8, hy - 1, P.coral[2]).set(7, hy - 1, P.coral[2]).set(8, hy + 3, P.coral[2])
    body.set(10, hy + 1, P.mustard[3]).set(9, hy + 1, P.walnut[0])
    s.blit(body.outline(C[0], grow=False), 0, 0)
    s.set(4, 10, P.mustard[2]).set(6, 10, P.mustard[2])
    return s


# ------------------------------------------------------------- lane edge, ambience

def shrub_border(s, x0=0, x1=W, y0=106, seed=0):
    """Low shrubs below the lane (replaces the park's flower border): two
    staggered rows of rounded box and hydrangea bushes, spring blooms tucked in."""
    rnd = random.Random(seed)
    m = Sprite(W, H)
    m.rect(x0, y0 + 1, x1 - x0, H - y0 - 1, G[1])
    for row, (base, hmin, hmax) in enumerate(((H + 2, 10, 13), (H + 6, 9, 12))):
        x = x0 - 8 + row * 9
        while x < x1 + 8:
            hw = rnd.randint(8, 13)
            kind = "hydrangea" if rnd.random() < 0.3 else "box"
            m.blit(FY.bush(kind, x + hw, hw, rnd.randint(hmin, hmax), "spring", base=base), 0, 0)
            x += hw * 2 - rnd.randint(4, 7)
    for _ in range((x1 - x0) // 8):                                 # azalea and forsythia sprigs
        bx, by = rnd.randint(x0, x1 - 2), rnd.randint(y0 + 4, H - 3)
        F = rnd.choice((P.blossom, P.mustard, P.coral, P.blossom))
        m.set(bx, by, F[3]).set(bx + 1, by, F[2]).set(bx, by - 1, F[4])
    m.px[: y0 - 1] = 0                                             # bush outlines wrap round the canvas
    m.px[:, :x0] = 0
    m.px[:, x1:] = 0
    s.blit(m, 0, 0)


def sun_shafts(w=W):
    """Light shafts slanting from the top left; the page draws this layer with
    low alpha (about 0.15) and breathes it slowly."""
    s = Sprite(w, H)
    for x0, bw in ((10, 14), (52, 8), (96, 18), (150, 7), (196, 12), (262, 16), (330, 9), (400, 14), (470, 10), (540, 16), (610, 9)):
        if x0 > w:
            break
        for y in range(0, 96):
            a = int(x0 + y * 0.55)
            s.hline(a, min(w - 1, a + bw), y, P.light[1])
    return s


def bird(frame):
    """A small bird in flight, 9x5: 0 wings up, 1 level, 2 down."""
    s = Sprite(9, 5)
    C = P.slate[1]
    if frame == 0:
        s.line(0, 0, 3, 3, C).line(8, 0, 5, 3, C)
    elif frame == 1:
        s.hline(0, 3, 2, C).hline(5, 8, 2, C).set(3, 3, C).set(5, 3, C)
    else:
        s.line(0, 4, 3, 2, C).line(8, 4, 5, 2, C)
    s.set(4, 3, C).set(4, 2, C)
    return s


def blend(base, layer, alpha):
    """Preview only: lay `layer` over `base` at `alpha` (the page does this live)."""
    out = base.copy()
    m = layer.px[..., 3] > 0
    out.px[m, :3] = (out.px[m, :3] * (1 - alpha) + layer.px[m, :3] * alpha).astype(np.uint8)
    return out
