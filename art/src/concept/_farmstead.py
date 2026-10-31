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


# ============================================================= Chinese style (owner: 中式的氛围)
# Grey tiles (青瓦) in vertical runs with round end tiles, ridges that curl
# up at the ends, white walls on a grey brick base, dark lattice windows,
# red couplets and lanterns, strings of chillies and corn, bamboo fences.

DARK = P.walnut
RED = P.terracotta


def cn_roof(s, x0, x1, top, eave, lift=3, overhang=8):
    """A grey-tiled roof from the long side: vertical tile runs, a row of
    round end tiles at the eave, a heavy ridge whose ends curl upward, and
    eaves that lift a little at the corners."""
    T = P.slate
    a0, b0 = x0 - overhang, x1 + overhang
    for y in range(top, eave + 1):
        t = (y - top) / max(1, eave - top)
        a, b = int(x0 + 10 - (10 + overhang) * t), int(x1 - 10 + (10 + overhang) * t)
        s.hline(a, b, y, T[2])
        for x in range(a + 1, b, 3):                               # tile runs: lit crest, dark trough
            s.set(x, y, T[3]).set(x + 1, y, T[2]).set(x + 2, y, T[1])
        s.set(a, y, T[1]).set(b, y, T[0])
    for x in range(a0, b0 + 1):                                    # lifted eave line
        d = min(x - a0, b0 - x)
        up = max(0, lift - d // 4)
        s.set(x, eave + 1 - up, T[1])
        if (x - a0) % 3 == 1:
            s.set(x, eave + 2 - up, T[3]).set(x, eave + 3 - up, T[1])   # 瓦当
    for k in range(lift + 1):
        s.set(a0 - k // 2, eave - k, T[1]).set(b0 + k // 2, eave - k, T[1])
    s.rect(x0 + 8, top - 3, x1 - x0 - 16, 3, T[1]).hline(x0 + 8, x1 - 9, top - 3, T[3])   # ridge
    for x in range(x0 + 10, x1 - 10, 5):
        s.set(x, top - 2, T[2])
    for ex, d in ((x0 + 8, -1), (x1 - 9, 1)):                      # curled ridge ends
        for k in range(5):
            s.set(ex + d * k, top - 3 - k // 2 - (k == 4), T[1])
            s.set(ex + d * k, top - 2 - k // 2, T[2])
        s.set(ex + d * 5, top - 6, T[3])


def lattice(s, x, y, w, h, frame=DARK, paper=P.linen, pattern="grid"):
    """A dark wooden lattice window over pale paper/glass."""
    s.rect(x - 2, y - 2, w + 4, h + 4, frame[1]).hline(x - 2, x + w + 1, y - 2, frame[3])
    s.rect(x, y, w, h, paper[3]).rect(x, y + h // 2, w, h - h // 2, paper[2])
    if pattern == "grid":
        for xx in range(x + 2, x + w - 1, 3):
            s.vline(xx, y, y + h - 1, frame[2])
        for yy in range(y + 2, y + h - 1, 3):
            s.hline(x, x + w - 1, yy, frame[2])
    else:                                                          # 冰裂纹-ish diagonals
        for k in range(-h, w, 4):
            s.line(x + max(0, k), y + max(0, -k), x + min(w - 1, k + h - 1), y + min(h - 1, h - 1 - k + k), frame[2])
    s.rect(x + w // 2 - 2, y + h // 2 - 2, 4, 4, paper[3]).rect(x + w // 2 - 1, y + h // 2 - 1, 2, 2, RED[3])   # 窗花
    s.hline(x - 3, x + w + 2, y + h + 2, frame[2]).hline(x - 3, x + w + 2, y + h + 3, frame[0])


def lantern(s, x, y):
    s.vline(x + 3, y - 3, y, DARK[0])
    s.ellipse(x + 3, y + 4, 3.5, 3.5, RED[2]).ellipse(x + 2, y + 3, 1.5, 1.5, RED[4])
    s.hline(x + 1, x + 5, y, P.mustard[2]).hline(x + 1, x + 5, y + 8, P.mustard[2])
    for k in range(3):
        s.set(x + 2 + k, y + 9 + (k % 2), P.mustard[3])


def couplets(s, dx, dw, top, bottom):
    for cx in (dx - 5, dx + dw + 2):
        s.rect(cx, top, 3, bottom - top, RED[2]).vline(cx, top, bottom - 1, RED[3])
        for yy in range(top + 2, bottom - 1, 3):
            s.set(cx + 1, yy, P.mustard[3])
    s.rect(dx, top - 4, dw, 3, RED[2]).hline(dx, dx + dw - 1, top - 4, RED[3])
    for xx in range(dx + 2, dx + dw - 1, 3):
        s.set(xx, top - 3, P.mustard[3])


def chili_string(s, x, y, n=7, kind="chili"):
    s.vline(x, y, y + 1, P.oat[1])
    for k in range(n):
        yy = y + 2 + k * 2
        if kind == "chili":
            s.set(x - 1 + (k % 2) * 2, yy, RED[3]).set(x, yy, RED[2]).set(x, yy + 1, RED[1])
        else:
            s.rect(x - 1, yy, 3, 2, P.mustard[3]).set(x - 1, yy, P.mustard[4])


def cn_farmhouse(s):
    """A two-storey Chinese farmhouse: grey brick base, white walls with a
    dark timber band, a wooden balcony upstairs, grey tile roofs with curled
    ridge ends, lattice windows, red double doors with couplets, lanterns,
    chillies and corn hung to dry."""
    x0, x1 = HOUSE
    base = LANE - 1
    plinth = base - 6
    up = plinth - 24
    eave = up - 20
    top = eave - 20
    cn_roof(s, x0, x1, top, eave)
    # upper storey
    plaster(s, x0 + 2, eave + 4, x1 - x0 - 4, up - eave - 4, P.linen, 21)
    s.hline(x0 + 2, x1 - 3, eave + 4, P.linen[1]).hline(x0 + 2, x1 - 3, eave + 5, P.linen[2])
    for wx in (x0 + 18, x0 + 52, x1 - 66, x1 - 32):
        lattice(s, wx, eave + 9, 14, 9)
    s.rect(x0 - 2, up - 7, x1 - x0 + 4, 2, DARK[2]).hline(x0 - 2, x1 + 1, up - 7, DARK[3])   # balcony rail
    for x in range(x0, x1, 4):
        s.vline(x, up - 5, up - 1, DARK[2])
        if (x // 4) % 2:
            s.set(x + 2, up - 3, DARK[1])
    s.rect(x0 - 3, up, x1 - x0 + 6, 3, DARK[2]).hline(x0 - 3, x1 + 2, up, DARK[3]).hline(x0 - 3, x1 + 2, up + 2, DARK[0])
    for bx in range(x0 + 4, x1, 20):                               # brackets under the balcony
        s.line(bx, up + 3, bx + 3, up + 6, DARK[1])
    # ground storey
    plaster(s, x0, up + 3, x1 - x0, plinth - up - 3, P.linen, 23)
    s.hline(x0, x1 - 1, up + 3, P.linen[1])
    s.vline(x1 - 1, up + 3, plinth, P.linen[1])
    for px in (x0, x1 - 3):
        s.rect(px, up + 3, 3, plinth - up - 3, DARK[2]).vline(px, up + 3, plinth - 1, DARK[3])
    for wx in (x0 + 14, x0 + 40, x1 - 54, x1 - 28):
        lattice(s, wx, up + 8, 13, 10, pattern="grid")
    # door
    dw = 18
    dx = HOUSE_DOOR - dw // 2
    s.rect(dx - 2, plinth - 22, dw + 4, 22, DARK[1])
    for k, a in enumerate((dx, dx + dw // 2)):
        s.rect(a, plinth - 21, dw // 2, 21, RED[1]).vline(a, plinth - 21, plinth - 1, RED[2])
        for yy in (plinth - 17, plinth - 9):
            s.rect(a + 2, yy, dw // 2 - 4, 5, RED[2]).hline(a + 2, a + dw // 2 - 3, yy, RED[3])
        s.set(a + (dw // 2 - 2 if k == 0 else 1), plinth - 12, P.mustard[3]).set(a + (dw // 2 - 2 if k == 0 else 1), plinth - 11, P.mustard[2])   # knockers
    s.rect(dx - 1, plinth - 2, dw + 2, 2, ST[2])                   # threshold
    couplets(s, dx, dw, plinth - 21, plinth - 2)
    s.rect(dx + 5, plinth - 30, 8, 4, DARK[0]).rect(dx + 6, plinth - 29, 6, 2, P.mustard[3])   # name plaque
    for lx in (dx - 14, dx + dw + 8):
        lantern(s, lx, eave + 6)
    chili_string(s, x0 + 8, up + 5, 8, "chili")
    chili_string(s, x0 + 11, up + 5, 6, "corn")
    chili_string(s, x1 - 9, up + 5, 8, "chili")
    # grey brick base and steps
    s.rect(x0 - 2, plinth, x1 - x0 + 4, base - plinth + 1, P.slate[2])
    for y in range(plinth, base + 1, 2):
        s.hline(x0 - 2, x1 + 1, y, P.slate[1])
        for x in range(x0 - 2 + (y % 4), x1 + 2, 6):
            s.set(x, y + 1, P.slate[1])
    s.hline(x0 - 2, x1 + 1, plinth, P.slate[3])
    s.rect(dx - 4, base - 2, dw + 8, 3, ST[3]).hline(dx - 4, dx + dw + 3, base - 2, ST[4]).hline(dx - 4, dx + dw + 3, base, ST[1])
    s.rect(dx - 2, base - 5, dw + 4, 3, ST[3]).hline(dx - 2, dx + dw + 1, base - 5, ST[4]).hline(dx - 2, dx + dw + 1, base - 3, ST[1])
    for px, F in ((dx - 12, P.coral), (dx + dw + 6, P.mustard)):    # glazed pots
        s.rect(px, base - 5, 7, 5, P.teal[2]).hline(px - 1, px + 7, base - 5, P.teal[3]).vline(px + 6, base - 4, base - 1, P.teal[1])
        s.ellipse(px + 3, base - 8, 3.5, 2.5, P.green[2]).set(px + 2, base - 10, F[3]).set(px + 4, base - 9, F[2])


def granary(s, x, base):
    """粮仓: rammed-earth walls on a stone footing, timber frame, a grey tile
    roof with curled ridge ends, big plank doors with a red 福 diamond, a
    loft opening spilling straw."""
    w = 90
    E = P.ash
    wall = base - 32
    s.rect(x, wall, w, 32, E[2])
    for y in range(wall + 2, base, 5):                             # rammed-earth layers
        s.hline(x, x + w - 1, y, E[1])
        s.hline(x, x + w - 1, y + 1, E[3])
    rnd = random.Random(8)
    for _ in range(80):
        s.set(rnd.randint(x, x + w - 1), rnd.randint(wall, base - 1), E[rnd.choice((1, 3))])
    for px in (x, x + w - 4, x + w // 2 - 20, x + w // 2 + 17):
        s.rect(px, wall, 4, 32, DARK[2]).vline(px, wall, base - 1, DARK[3])
    s.rect(x, wall, w, 3, DARK[2]).hline(x, x + w - 1, wall, DARK[3])
    cn_roof(s, x, x + w, wall - 20, wall - 1, lift=4, overhang=7)
    cx = x + w // 2
    s.rect(cx - 15, base - 24, 30, 24, DARK[1])                    # plank doors
    for xx in range(cx - 14, cx + 15, 3):
        s.vline(xx, base - 23, base - 1, DARK[2])
    s.vline(cx, base - 24, base - 1, DARK[0])
    for yy in (base - 20, base - 6):
        s.hline(cx - 14, cx + 14, yy, P.steel[1])
    for k in range(5):                                             # 福 diamond
        s.hline(cx - k, cx + k, base - 33 + k, RED[2]).hline(cx - k, cx + k, base - 25 - k, RED[2])
    s.set(cx, base - 29, P.mustard[3]).set(cx - 1, base - 28, P.mustard[3]).set(cx + 1, base - 30, P.mustard[3])
    for lx in (x + 12, x + w - 22):                                # small lattice vents
        lattice(s, lx, base - 24, 9, 7, paper=P.oat)
    s.rect(x - 2, base - 3, w + 4, 3, ST[2]).hline(x - 2, x + w + 1, base - 3, ST[3])
    for k in range(20):
        s.set(cx - 14 + rnd.randint(0, 28), base + rnd.randint(0, 2), P.mustard[rnd.choice((2, 3))])


def grain_bin(s, x, base):
    """囤: a round woven grain bin on a stone pad with a conical thatch hat."""
    w, h = 20, 24
    B = P.oak
    for y in range(base - h, base):
        s.hline(x, x + w - 1, y, B[2])
        s.hline(x, x + 3, y, B[3]).hline(x + w - 4, x + w - 1, y, B[1])
        if (y - base) % 3 == 0:
            for xx in range(x + (y % 2), x + w, 2):
                s.set(xx, y, B[1])
    for y in (base - h + 4, base - 6):
        s.hline(x, x + w - 1, y, DARK[1])
    T = P.mustard
    for k in range(12):
        hw = 2 + k
        s.hline(x + w // 2 - hw, x + w // 2 + hw - 1, base - h - 12 + k, T[3] if k % 3 else T[2])
        s.set(x + w // 2 + hw - 1, base - h - 12 + k, T[1])
    for xx in range(x - 2, x + w + 2, 2):
        s.vline(xx, base - h, base - h + 1, T[2])
    s.rect(x - 2, base - 2, w + 4, 2, ST[2]).hline(x - 2, x + w + 1, base - 2, ST[3])


def bamboo_fence(s, x0, x1, y, gate=None):
    """竹篱笆: crossed bamboo laths with a rail, posts every 18px."""
    B = P.sage
    for x in range(x0, x1):
        if gate and gate[0] <= x < gate[1]:
            continue
        s.set(x, y - 7, B[3]).set(x, y - 6, B[1])
        k = (x - x0) % 8
        s.set(x, y - 1 - k, B[2]) if k < 8 else None
        s.set(x, y - 8 + k, B[2])
    for x in range(x0 + 2, x1, 18):
        if gate and gate[0] - 2 <= x < gate[1] + 1:
            continue
        s.rect(x, y - 11, 2, 12, B[3]).vline(x + 1, y - 11, y, B[1]).set(x, y - 11, B[4])
        s.hline(x, x + 1, y - 4, B[1])
    if gate:
        for gx in gate:
            s.rect(gx - 1, y - 13, 3, 14, P.oak[2]).vline(gx - 1, y - 13, y, P.oak[3])


# ------------------------------------------------------------- Chinese farmhouse inside

CN_W, CN_H = 288, 120
GROUND_TOP, GROUND_FL = 63, 108
LIVING = (50, 282)          # one open room: living | dining | kitchen, one wooden floor
INSIDE_DATA = {
    "rooms": {"buddy_bed": (50, 90), "bath": (144, 40), "parents_bed": (188, 94), "living": LIVING},
    "seats": {"sofa": [(72, GROUND_FL - 3), (86, GROUND_FL - 3), (100, GROUND_FL - 3)],          # up to three people
              "dining": [(164, GROUND_FL - 4), (184, GROUND_FL - 4), (202, GROUND_FL - 4)]},
    "parents_bed_off_limits": True,
}


def settee(w=46):
    """A wooden three-seat settee (长木椅) with cushions, side-on."""
    s = Sprite(w, 18)
    s.rect(0, 0, w, 3, DARK[2]).hline(0, w - 1, 0, DARK[3])        # top rail of the back
    for x in range(2, w - 2, 5):
        s.vline(x, 3, 9, DARK[1])
    s.rect(0, 10, w, 3, DARK[2]).hline(0, w - 1, 10, DARK[3])      # seat
    for k in range(3):
        cx = 2 + k * (w - 4) // 3
        s.rect(cx, 7, (w - 4) // 3 - 1, 3, P.sage[2]).hline(cx, cx + (w - 4) // 3 - 2, 7, P.sage[3])
    for x in (0, w - 3):
        s.rect(x, 0, 3, 18, DARK[1]).vline(x, 0, 17, DARK[2])
    s.rect(3, 13, w - 6, 1, DARK[0])
    return s


def tea_table():
    s = Sprite(26, 8)
    s.rect(0, 0, 26, 2, DARK[2]).hline(0, 25, 0, DARK[4])
    for x in (2, 22):
        s.rect(x, 2, 2, 6, DARK[1])
    s.rect(9, -3 + 3, 0, 0, DARK[1])
    return s


def teaset(s, x, y):
    s.rect(x, y - 3, 5, 3, P.porcelain[3]).set(x + 5, y - 2, P.porcelain[2]).set(x + 2, y - 4, P.teal[2])
    for k in (8, 12):
        s.rect(x + k, y - 2, 2, 2, P.porcelain[3])


def square_table():
    """八仙桌-like square table, side view, 26 wide."""
    s = Sprite(26, 16)
    s.rect(0, 0, 26, 3, DARK[2]).hline(0, 25, 0, DARK[4]).hline(0, 25, 2, DARK[1])
    s.rect(1, 3, 24, 2, DARK[1])
    for x in (1, 23):
        s.rect(x, 3, 2, 13, DARK[2]).vline(x, 3, 15, DARK[3])
    s.line(3, 5, 6, 3, DARK[1]).line(22, 5, 19, 3, DARK[1])
    return s


def stool():
    s = Sprite(8, 10)
    s.rect(0, 0, 8, 2, DARK[3]).hline(0, 7, 0, DARK[4])
    s.vline(1, 2, 9, DARK[1]).vline(6, 2, 9, DARK[1]).hline(1, 6, 6, DARK[1])
    return s


def stove():
    """灶台: a whitewashed brick stove with a wok, a stoke hole and a flue."""
    s = Sprite(40, 40)
    s.rect(0, 22, 40, 18, P.porcelain[3]).hline(0, 39, 22, P.porcelain[2]).vline(39, 22, 39, P.porcelain[1])
    s.rect(0, 24, 40, 3, P.teal[2]).hline(0, 39, 24, P.teal[3])     # tiled band
    s.rect(8, 31, 9, 6, P.slate[0]).ellipse(12, 36, 3, 2, P.coral[2]).set(12, 35, P.mustard[4])   # stoke hole + embers
    s.ellipse(26, 22, 9, 2.5, P.slate[1]).hline(18, 34, 21, P.slate[3])   # the wok in the stove top
    s.line(34, 20, 38, 17, DARK[2])
    s.rect(4, 0, 8, 22, P.porcelain[2]).vline(4, 0, 21, P.porcelain[3]).vline(11, 0, 21, P.porcelain[1])   # flue
    s.rect(3, 0, 10, 2, P.slate[2])
    s.rect(18, 12, 6, 3, RED[2]).set(20, 13, P.mustard[3])         # the kitchen god's red paper
    return s


def water_jar():
    s = Sprite(14, 14)
    s.ellipse(7, 8, 6.5, 6, P.walnut[2]).ellipse(5, 6, 3, 3, P.walnut[3]).hline(1, 12, 2, P.walnut[1])
    s.rect(1, 1, 12, 2, DARK[2]).hline(1, 12, 1, DARK[3])           # wooden lid
    s.rect(9, -0, 4, 1, P.oak[3])
    return s


def scroll(w=12, h=26, kind="mountain"):
    """挂轴: a hanging scroll with a landscape or a big character."""
    s = Sprite(w, h)
    s.rect(0, 0, w, h, P.oat[3]).rect(1, 2, w - 2, h - 5, P.linen[3])
    s.hline(0, w - 1, 0, DARK[1]).hline(0, w - 1, h - 2, DARK[1]).hline(0, w - 1, h - 1, DARK[0])
    if kind == "mountain":
        for k in range(w - 4):
            s.vline(2 + k, h - 6 - abs(k - (w - 4) // 2) * 2, h - 5, P.sage[1 + (k % 2)])
        s.set(w - 3, 5, RED[2])
    else:                                                          # a red 福 square turned on its point
        c, m = w // 2, h // 2 - 1
        for k in range(w // 2 - 1):
            s.hline(c - k, c + k - 1, m - (w // 2 - 2) + k, RED[2]).hline(c - k, c + k - 1, m + (w // 2 - 2) - k, RED[2])
        for dx, dy in ((-1, -2), (0, -2), (-2, 0), (-1, 0), (0, 0), (1, 0), (-1, 2), (0, 2), (0, 1)):
            s.set(c + dx, m + dy, P.mustard[3])
    return s


def moon_window(r=10):
    s = Sprite(r * 2 + 3, r * 2 + 3)
    s.ellipse(r + 1, r + 1, r + 1, r + 1, DARK[1])
    s.ellipse(r + 1, r + 1, r - 0.5, r - 0.5, P.glass[2])
    s.ellipse(r - 2, r - 2, r * 0.5, r * 0.4, P.glass[3])
    for k in range(-r, r + 1, 4):
        s.vline(r + 1 + k, 1, r * 2 + 1, DARK[2]) if abs(k) < r - 1 else None
    s.ellipse(r + 1, r + 1, r - 0.5, r - 0.5, None) if False else None
    m = np.zeros((s.h, s.w), bool)
    yy, xx = np.mgrid[:s.h, :s.w]
    m[((xx - r - 1) ** 2 + (yy - r - 1) ** 2) > (r + 1.2) ** 2] = True
    s.px[m] = 0
    return s


def cn_farmhouse_inside():
    """Upstairs from the friend-house planner (bedrooms, bath, stairs), dressed
    Chinese; downstairs drawn by hand as one open room with one wooden floor:
    a living corner with a three-seat settee and tea table, a square dining
    table for three, and a kitchen with a brick stove."""
    plan = ("farmhouse", "山谷农舍", CN_W, "", "oak", [
        [("stair", 6, 40), ("bed", 50, 90), ("bath", 144, 40), ("guest_bed", 188, 94)],
        [("entry_stair", 6, 40), ("laundry", 50, 232)]])
    data, bg, front = FH.draw_plan(plan)
    s = bg.copy()
    x0, x1 = LIVING
    top, fl = GROUND_TOP, GROUND_FL
    HS.back_wall(s, x0, x1 - x0, top, fl, P.plaster_living)        # wipe the placeholder room
    HS.floor_band(s, x0, x1 - x0, fl, "wood")
    s.rect(x0, fl - 15, x1 - x0, 12, DARK[2])                      # wooden wainscot
    s.hline(x0, x1 - 1, fl - 15, DARK[3]).hline(x0, x1 - 1, fl - 4, DARK[1])
    for x in range(x0 + 6, x1, 12):
        s.rect(x, fl - 13, 9, 8, DARK[1]).hline(x, x + 8, fl - 13, DARK[3])
    for x in range(x0 + 4, x1 - 2, 18):                            # ceiling joists
        s.rect(x, top, 5, 3, DARK[1]).hline(x, x + 4, top, DARK[3])
    # living corner
    HS.place(s, moon_window(10), x0 + 18, top + 9)
    HS.place(s, scroll(12, 26, "fu"), x0 + 52, top + 6)
    HS.on_floor(s, settee(46), x0 + 14, 0, 2)
    tt = tea_table()
    s.blit(tt, x0 + 24, fl + 1 - tt.h + 3)
    teaset(s, x0 + 30, fl - 3)
    pot_x = x0 + 66
    s.rect(pot_x, fl - 7, 8, 8, P.teal[2]).hline(pot_x, pot_x + 7, fl - 7, P.teal[3])   # potted bamboo
    for k in range(4):
        s.vline(pot_x + 1 + k * 2, fl - 26 + k * 3, fl - 8, P.green[2 + (k % 2)])
        s.line(pot_x + 1 + k * 2, fl - 20 + k * 3, pot_x + 4 + k * 2, fl - 22 + k * 3, P.green[3])
    # dining: square table, three stools (left, back, right)
    tx = x0 + 112
    HS.on_floor(s, stool(), tx + 10, 0, 1)                         # the one behind the table
    HS.place(s, scroll(10, 20, "mountain"), tx + 8, top + 8)
    lantern(s, tx + 10, top + 4)
    st = square_table()
    s.blit(st, tx, fl + 2 - st.h)
    for sx in (tx - 9, tx + 27):
        s.blit(stool(), sx, fl + 2 - 10)
    s.rect(tx + 6, fl - 16, 5, 2, P.porcelain[3]).rect(tx + 14, fl - 16, 5, 2, P.porcelain[3]).set(tx + 12, fl - 17, P.coral[3])   # bowls
    # kitchen
    kx = x1 - 82
    HS.on_floor(s, stove(), kx, 0, 1)
    HS.on_floor(s, water_jar(), kx + 44, 0, 1)
    s.rect(kx + 46, top + 14, 30, 3, DARK[2]).hline(kx + 46, kx + 75, top + 14, DARK[3])   # shelf with jars
    for k, C in enumerate((P.porcelain, P.teal, P.clay, P.porcelain)):
        s.rect(kx + 48 + k * 7, top + 8, 5, 6, C[2]).hline(kx + 48 + k * 7, kx + 52 + k * 7, top + 8, C[3])
    for k, x in enumerate(range(kx + 60, kx + 78, 5)):
        chili_string(s, x, top + 18, 6, "chili" if k % 2 == 0 else "corn")
    s.rect(kx + 60, fl - 22, 18, 3, DARK[2]).hline(kx + 60, kx + 77, fl - 22, DARK[3])   # chopping block on a stand
    s.vline(kx + 62, fl - 19, fl, DARK[1]).vline(kx + 75, fl - 19, fl, DARK[1])
    s.rect(kx + 64, fl - 25, 9, 3, P.oak[3]).set(kx + 70, fl - 26, P.steel[3])
    # upstairs: Chinese touches over the planner's rooms (lattice instead of curtained windows)
    for f in data["furniture"]:
        if f.get("kind") == "window":
            lattice(s, f["x"] + 2, f["y"] + 2, f["w"] - 4, f["h"] - 6)
    for x in (60, 196):
        s.blit(scroll(10, 18, "mountain"), x + 50, 5 + 12)
    lantern(s, 160, 8)
    s.blit(front, 0, 0)
    return s, INSIDE_DATA
